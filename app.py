#!/usr/bin/env python3
"""
Nuclear Reactor Database - Production App
Main entry point for deployment.
"""

import os
import sys
import sqlite3
from flask import Flask, jsonify, request, render_template
from functools import wraps
from pathlib import Path

# =============================================================================
# APP CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent
DB_PATH = Path(os.environ.get('DATABASE_PATH', BASE_DIR / "nuclear_reactors.db"))

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_SORT_KEYS'] = False

# API Keys (in production, use environment variables)
VALID_API_KEYS = {
    os.environ.get('API_KEY_PAID', 'demo-key-12345'): {'tier': 'paid', 'name': 'Demo User'},
    os.environ.get('API_KEY_FREE', 'free-tier-key'): {'tier': 'free', 'name': 'Free User'},
}

# =============================================================================
# DATABASE HELPER
# =============================================================================

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(sql, params=None):
    """Execute query and return results as list of dicts."""
    conn = get_db()
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

# =============================================================================
# AUTHENTICATION
# =============================================================================

def require_api_key(tier='free'):
    """Decorator to require API key authentication."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')

            if not api_key:
                if tier == 'free':
                    return f(*args, **kwargs)
                return jsonify({'error': 'API key required', 'code': 401}), 401

            if api_key not in VALID_API_KEYS:
                return jsonify({'error': 'Invalid API key', 'code': 401}), 401

            user = VALID_API_KEYS[api_key]
            if tier == 'paid' and user['tier'] != 'paid':
                return jsonify({'error': 'Paid subscription required', 'code': 403}), 403

            request.user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =============================================================================
# FRONTEND ROUTES
# =============================================================================

@app.route('/')
def home():
    """Redirect to dashboard."""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the main dashboard."""
    return render_template('index.html')

# =============================================================================
# FREE TIER API ENDPOINTS
# =============================================================================

@app.route('/api/stats')
@require_api_key('free')
def global_stats():
    """Global nuclear statistics."""
    stats = query_db("""
        SELECT
            COUNT(*) as total_reactors,
            SUM(CASE WHEN status = 'Operational' THEN 1 ELSE 0 END) as operational,
            SUM(CASE WHEN status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
            SUM(CASE WHEN status = 'Permanent Shutdown' THEN 1 ELSE 0 END) as shutdown,
            ROUND(SUM(CASE WHEN status = 'Operational' THEN gross_capacity_mw ELSE 0 END) / 1000, 1) as operational_gw,
            ROUND(AVG(CASE WHEN status = 'Operational' THEN age_years END), 1) as avg_age
        FROM reactors
    """)[0]

    # Get the most recent year with generation data and compute coverage-adjusted estimate
    gen_latest = query_db("""
        SELECT
            g.year,
            SUM(g.electricity_gwh) as raw_total,
            COUNT(DISTINCT g.reactor_id) as reporting
        FROM generation_annual g
        WHERE g.year = (SELECT MAX(year) FROM generation_annual)
        GROUP BY g.year
    """)

    generation_info = {}
    if gen_latest and gen_latest[0]['raw_total']:
        year = gen_latest[0]['year']
        raw_twh = gen_latest[0]['raw_total'] / 1000
        reporting = gen_latest[0]['reporting']

        # Count reactors operational during that year
        operational_that_year = query_db("""
            SELECT COUNT(*) as count FROM reactors
            WHERE commercial_operation IS NOT NULL
              AND commercial_operation <= ?
              AND (permanent_shutdown IS NULL OR permanent_shutdown >= ?)
        """, (f'{year}-12-31', f'{year}-01-01'))[0]['count']

        coverage_pct = round(reporting / operational_that_year * 100, 1) if operational_that_year else 0
        adjustment = operational_that_year / reporting if reporting < operational_that_year else 1.0
        adjusted_twh = round(raw_twh * adjustment, 1)

        generation_info = {
            'year': year,
            'adjusted_twh': adjusted_twh,
            'raw_twh': round(raw_twh, 1),
            'reporting_reactors': reporting,
            'operational_reactors': operational_that_year,
            'coverage_pct': coverage_pct,
            'is_estimated': coverage_pct < 90
        }

    return jsonify({
        'global_statistics': {
            'total_reactors': stats['total_reactors'],
            'operational': {
                'count': stats['operational'],
                'capacity_gw': stats['operational_gw']
            },
            'under_construction': stats['under_construction'],
            'permanently_shutdown': stats['shutdown'],
            'average_fleet_age_years': stats['avg_age'],
            'generation': generation_info
        },
        'data_coverage': {
            'countries': query_db("""
                SELECT COUNT(DISTINCT c.id) as cnt FROM countries c
                JOIN reactors r ON c.id = r.country_id
                WHERE r.status IN ('Operational', 'Under Construction')
            """)[0]['cnt'],
            'generation_years': '1954-2024',
            'last_updated': '2024-12'
        }
    })

@app.route('/api/countries')
@require_api_key('free')
def list_countries():
    """List all countries with reactors."""
    countries = query_db("""
        SELECT
            c.name,
            c.code as iso_code,
            COUNT(CASE WHEN r.status = 'Operational' THEN 1 END) as operational,
            COUNT(CASE WHEN r.status = 'Under Construction' THEN 1 END) as under_construction,
            ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw
        FROM countries c
        LEFT JOIN reactors r ON c.id = r.country_id
        GROUP BY c.name, c.code
        HAVING operational > 0 OR under_construction > 0
        ORDER BY operational DESC
    """)
    return jsonify({'countries': countries, 'count': len(countries)})

@app.route('/api/countries/<country>/summary')
@require_api_key('free')
def country_summary(country):
    """Country summary statistics."""
    stats = query_db("""
        SELECT
            c.name as country,
            COUNT(*) as total_reactors,
            SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
            SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
            ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000, 1) as capacity_gw,
            ROUND(AVG(CASE WHEN r.status = 'Operational' THEN r.age_years END), 1) as avg_age
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        WHERE LOWER(c.name) = LOWER(?)
        GROUP BY c.name
    """, (country,))

    if not stats:
        return jsonify({'error': f'Country not found: {country}'}), 404
    return jsonify(stats[0])

@app.route('/api/countries/<country>/detail')
@require_api_key('free')
def country_detail(country):
    """Detailed country page data: fleet info, generation history, reactor list, tech mix."""
    # Country summary stats
    stats = query_db("""
        SELECT
            c.name as country,
            COUNT(*) as total_reactors,
            SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
            SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
            SUM(CASE WHEN r.status = 'Permanent Shutdown' THEN 1 ELSE 0 END) as shutdown,
            SUM(CASE WHEN r.status = 'Long-term Shutdown' THEN 1 ELSE 0 END) as long_term_shutdown,
            ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw,
            ROUND(AVG(CASE WHEN r.status = 'Operational' THEN r.age_years END), 1) as avg_age
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        WHERE LOWER(c.name) = LOWER(?)
        GROUP BY c.name
    """, (country,))

    if not stats:
        return jsonify({'error': f'Country not found: {country}'}), 404

    # Generation history: sum by year across all reactors in this country
    generation_history = query_db("""
        SELECT
            g.year,
            ROUND(SUM(g.electricity_gwh) / 1000.0, 2) as total_twh,
            COUNT(DISTINCT g.reactor_id) as reactor_count
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        JOIN countries c ON r.country_id = c.id
        WHERE LOWER(c.name) = LOWER(?)
        GROUP BY g.year
        ORDER BY g.year
    """, (country,))

    # All reactors for this country
    reactors = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, t.code as technology,
               r.gross_capacity_mw, r.status, r.commercial_operation,
               r.latitude, r.longitude
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE LOWER(c.name) = LOWER(?)
        ORDER BY
            CASE r.status
                WHEN 'Operational' THEN 1
                WHEN 'Under Construction' THEN 2
                WHEN 'Permanent Shutdown' THEN 3
                ELSE 4
            END,
            r.plant_name, r.unit_number
    """, (country,))

    # Technology mix (all statuses)
    technology_mix = query_db("""
        SELECT t.code as technology, COUNT(*) as count,
               ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE LOWER(c.name) = LOWER(?)
        GROUP BY t.code
        ORDER BY count DESC
    """, (country,))

    return jsonify({
        'country': stats[0],
        'generation_history': generation_history,
        'reactors': reactors,
        'technology_mix': technology_mix
    })

@app.route('/api/technologies')
@require_api_key('free')
def list_technologies():
    """List reactor technologies."""
    techs = query_db("""
        SELECT
            t.code,
            t.name as full_name,
            COUNT(CASE WHEN r.status = 'Operational' THEN 1 END) as operational,
            COUNT(*) as total,
            ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000, 1) as capacity_gw
        FROM technologies t
        LEFT JOIN reactors r ON t.id = r.technology_id
        GROUP BY t.code, t.name
        ORDER BY capacity_gw DESC
    """)
    return jsonify({'technologies': techs, 'count': len(techs)})

@app.route('/api/reactors/age-distribution')
@require_api_key('free')
def age_distribution():
    """Operational reactor count by age bracket."""
    brackets = query_db("""
        SELECT
            CASE
                WHEN age_years < 10 THEN '0-9'
                WHEN age_years < 20 THEN '10-19'
                WHEN age_years < 30 THEN '20-29'
                WHEN age_years < 40 THEN '30-39'
                WHEN age_years < 50 THEN '40-49'
                ELSE '50+'
            END as bracket,
            COUNT(*) as count,
            ROUND(SUM(gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors
        WHERE status = 'Operational' AND age_years IS NOT NULL
        GROUP BY bracket
        ORDER BY MIN(age_years)
    """)
    return jsonify({'brackets': brackets})


@app.route('/api/construction-map')
@require_api_key('free')
def construction_map():
    """Under-construction reactor sites for mapping."""
    reactors = query_db("""
        SELECT r.plant_name, r.unit_number, c.name as country,
               t.code as technology, r.gross_capacity_mw,
               r.latitude, r.longitude
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE r.status = 'Under Construction'
          AND r.latitude IS NOT NULL AND r.longitude IS NOT NULL
        ORDER BY r.plant_name, r.unit_number
    """)

    # Group by site (plant_name)
    sites = {}
    for r in reactors:
        key = r['plant_name']
        if key not in sites:
            sites[key] = {
                'site_name': key,
                'country': r['country'],
                'latitude': r['latitude'],
                'longitude': r['longitude'],
                'reactors': [],
                'total_capacity_mw': 0
            }
        sites[key]['reactors'].append({
            'name': f"{r['plant_name']}-{r['unit_number']}",
            'technology': r['technology'],
            'capacity_mw': r['gross_capacity_mw']
        })
        sites[key]['total_capacity_mw'] += r['gross_capacity_mw'] or 0

    return jsonify({'sites': list(sites.values()), 'count': len(sites)})


@app.route('/api/reactors/count')
@require_api_key('free')
def reactor_counts():
    """Reactor counts by status."""
    counts = query_db("""
        SELECT status, COUNT(*) as count,
               ROUND(SUM(gross_capacity_mw) / 1000, 1) as capacity_gw
        FROM reactors GROUP BY status ORDER BY count DESC
    """)
    return jsonify({'by_status': counts, 'total': sum(c['count'] for c in counts)})

# =============================================================================
# PAID TIER API ENDPOINTS
# =============================================================================

@app.route('/api/reactors')
@require_api_key('paid')
def list_reactors():
    """List reactors with pagination and filters."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 500)  # Increased limit to 500
    status = request.args.get('status')
    technology = request.args.get('technology')
    country = request.args.get('country')

    offset = (page - 1) * per_page

    where_clauses = []
    params = []

    if status:
        where_clauses.append("r.status = ?")
        params.append(status)
    if technology:
        where_clauses.append("t.code = ?")
        params.append(technology)
    if country:
        where_clauses.append("c.name = ?")
        params.append(country)

    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    count_sql = f"""
        SELECT COUNT(*) as total FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        {where_sql}
    """
    total = query_db(count_sql, params if params else None)[0]['total']

    sql = f"""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology, r.gross_capacity_mw, r.status,
               r.commercial_operation, r.permanent_shutdown, r.latitude, r.longitude
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        {where_sql}
        ORDER BY c.name COLLATE NOCASE, r.plant_name, r.unit_number
        LIMIT ? OFFSET ?
    """
    params.extend([per_page, offset])
    reactors = query_db(sql, params)

    return jsonify({
        'reactors': reactors,
        'pagination': {'page': page, 'per_page': per_page, 'total': total, 'pages': (total + per_page - 1) // per_page}
    })

@app.route('/api/reactors/<int:reactor_id>')
@require_api_key('paid')
def get_reactor(reactor_id):
    """Get detailed information for a single reactor."""
    reactor = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology, t.name as technology_name,
               r.thermal_capacity_mw, r.gross_capacity_mw, r.net_capacity_mw,
               r.status, r.commercial_operation, r.permanent_shutdown,
               ROUND((JULIANDAY(COALESCE(r.permanent_shutdown, 'now')) - JULIANDAY(r.commercial_operation)) / 365.25, 2) as age_years,
               r.latitude, r.longitude
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE r.id = ?
    """, (reactor_id,))

    if not reactor:
        return jsonify({'error': 'Reactor not found'}), 404

    r = reactor[0]

    # Get generation history (calculate capacity factor from generation and capacity)
    generation = query_db("""
        SELECT g.year, g.electricity_gwh,
               ROUND(g.electricity_gwh / (r.gross_capacity_mw / 1000.0 * 8760) * 100, 1) as capacity_factor
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE g.reactor_id = ?
          AND r.gross_capacity_mw > 0
        ORDER BY g.year DESC
    """, (reactor_id,))

    # Get lifetime stats (calculate avg capacity factor from generation and capacity)
    lifetime_stats = query_db("""
        SELECT
            SUM(g.electricity_gwh) as total_gwh,
            AVG(g.electricity_gwh) as avg_annual_gwh,
            ROUND(AVG(g.electricity_gwh / (r.gross_capacity_mw / 1000.0 * 8760) * 100), 1) as avg_capacity_factor,
            MIN(g.year) as first_year,
            MAX(g.year) as last_year,
            COUNT(*) as years_operating
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE g.reactor_id = ?
          AND r.gross_capacity_mw > 0
    """, (reactor_id,))[0]

    return jsonify({
        'reactor': r,
        'generation_history': generation,
        'lifetime_stats': {
            'total_generation_twh': round(lifetime_stats['total_gwh'] / 1000, 2) if lifetime_stats['total_gwh'] else None,
            'avg_annual_gwh': round(lifetime_stats['avg_annual_gwh'], 1) if lifetime_stats['avg_annual_gwh'] else None,
            'avg_capacity_factor': round(lifetime_stats['avg_capacity_factor'], 1) if lifetime_stats['avg_capacity_factor'] else None,
            'years_operating': lifetime_stats['years_operating'],
            'first_year': lifetime_stats['first_year'],
            'last_year': lifetime_stats['last_year']
        }
    })

@app.route('/reactor/<int:reactor_id>')
def reactor_detail_page(reactor_id):
    """Serve the reactor detail page."""
    return render_template('reactor_detail.html', reactor_id=reactor_id)

@app.route('/plant/<plant_name>')
def plant_detail_page(plant_name):
    """Serve the plant detail page."""
    return render_template('plant_detail.html', plant_name=plant_name)

@app.route('/api/plants/<plant_name>')
@require_api_key('free')
def plant_detail(plant_name):
    """Plant-level detail: all reactors at a plant, aggregate stats, combined generation."""
    # All reactors at this plant
    reactors = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology, t.name as technology_name,
               r.thermal_capacity_mw, r.gross_capacity_mw, r.net_capacity_mw,
               r.status, r.commercial_operation, r.permanent_shutdown,
               ROUND((JULIANDAY(COALESCE(r.permanent_shutdown, 'now')) - JULIANDAY(r.commercial_operation)) / 365.25, 2) as age_years,
               r.latitude, r.longitude, r.owner, r.operator,
               m.name as model, s.name as supplier
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        LEFT JOIN models m ON r.model_id = m.id
        LEFT JOIN suppliers s ON r.supplier_id = s.id
        WHERE r.plant_name = ?
        ORDER BY CAST(r.unit_number AS INTEGER), r.unit_number
    """, (plant_name,))

    if not reactors:
        return jsonify({'error': f'Plant not found: {plant_name}'}), 404

    # Aggregate stats
    operational = [r for r in reactors if r['status'] == 'Operational']
    total_capacity = sum(r['gross_capacity_mw'] or 0 for r in operational)

    # Per-reactor lifetime stats (generation totals per unit)
    reactor_ids = [r['id'] for r in reactors]
    placeholders = ','.join('?' * len(reactor_ids))
    unit_stats = query_db(f"""
        SELECT g.reactor_id,
               ROUND(SUM(g.electricity_gwh) / 1000.0, 2) as total_twh,
               ROUND(AVG(g.electricity_gwh), 1) as avg_annual_gwh,
               ROUND(AVG(g.electricity_gwh / (r.gross_capacity_mw / 1000.0 * 8760) * 100), 1) as avg_capacity_factor,
               MIN(g.year) as first_year, MAX(g.year) as last_year,
               COUNT(*) as years_operating
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE g.reactor_id IN ({placeholders})
          AND r.gross_capacity_mw > 0
        GROUP BY g.reactor_id
    """, reactor_ids)
    unit_stats_map = {s['reactor_id']: s for s in unit_stats}

    # Combined generation history (sum across all units by year)
    generation_history = query_db(f"""
        SELECT g.year,
               ROUND(SUM(g.electricity_gwh), 2) as total_gwh,
               COUNT(DISTINCT g.reactor_id) as units_reporting
        FROM generation_annual g
        WHERE g.reactor_id IN ({placeholders})
        GROUP BY g.year
        ORDER BY g.year
    """, reactor_ids)

    # Plant-level aggregate lifetime stats
    plant_total_gwh = sum(s.get('total_twh', 0) or 0 for s in unit_stats) * 1000
    plant_years = set()
    for h in generation_history:
        plant_years.add(h['year'])

    return jsonify({
        'plant': {
            'name': plant_name,
            'country': reactors[0]['country'],
            'total_units': len(reactors),
            'operational_units': len(operational),
            'total_capacity_mw': total_capacity,
            'latitude': reactors[0]['latitude'],
            'longitude': reactors[0]['longitude'],
        },
        'reactors': [{
            **r,
            'lifetime_stats': unit_stats_map.get(r['id'], {})
        } for r in reactors],
        'generation_history': generation_history,
        'plant_stats': {
            'total_generation_twh': round(plant_total_gwh / 1000, 2) if plant_total_gwh else None,
            'years_with_data': len(plant_years),
            'first_year': min(plant_years) if plant_years else None,
            'last_year': max(plant_years) if plant_years else None,
        }
    })

@app.route('/model/<model_name>')
def model_detail_page(model_name):
    """Serve the model detail page."""
    return render_template('model_detail.html', model_name=model_name)

@app.route('/api/models/<model_name>/detail')
@require_api_key('free')
def model_detail(model_name):
    """Detailed model page data: summary stats, generation history, reactor list, country breakdown."""
    # Model summary stats
    stats = query_db("""
        SELECT
            m.name,
            t.code as technology_code,
            COUNT(*) as total,
            SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
            SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
            SUM(CASE WHEN r.status = 'Permanent Shutdown' THEN 1 ELSE 0 END) as shutdown,
            ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw,
            ROUND(AVG(CASE WHEN r.status = 'Operational' THEN r.age_years END), 1) as avg_age
        FROM models m
        LEFT JOIN reactors r ON m.id = r.model_id
        LEFT JOIN technologies t ON m.technology_id = t.id
        WHERE LOWER(m.name) = LOWER(?)
        GROUP BY m.name, t.code
    """, (model_name,))

    if not stats:
        return jsonify({'error': f'Model not found: {model_name}'}), 404

    # Generation history: sum by year across all reactors with this model
    generation_history = query_db("""
        SELECT
            g.year,
            ROUND(SUM(g.electricity_gwh) / 1000.0, 2) as total_twh,
            COUNT(DISTINCT g.reactor_id) as reactor_count
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        JOIN models m ON r.model_id = m.id
        WHERE LOWER(m.name) = LOWER(?)
        GROUP BY g.year
        ORDER BY g.year
    """, (model_name,))

    # All reactors with this model
    reactors = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology,
               r.gross_capacity_mw, r.status, r.commercial_operation,
               r.permanent_shutdown, r.latitude, r.longitude
        FROM reactors r
        JOIN models m ON r.model_id = m.id
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE LOWER(m.name) = LOWER(?)
        ORDER BY
            CASE r.status
                WHEN 'Operational' THEN 1
                WHEN 'Under Construction' THEN 2
                WHEN 'Long-term Shutdown' THEN 3
                WHEN 'Permanent Shutdown' THEN 4
                ELSE 5
            END,
            c.name COLLATE NOCASE, r.plant_name, r.unit_number
    """, (model_name,))

    # Country breakdown
    country_breakdown = query_db("""
        SELECT c.name as country, COUNT(*) as count,
               ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors r
        JOIN models m ON r.model_id = m.id
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE LOWER(m.name) = LOWER(?)
        GROUP BY c.name
        ORDER BY count DESC
    """, (model_name,))

    return jsonify({
        'model': stats[0],
        'generation_history': generation_history,
        'reactors': reactors,
        'country_breakdown': country_breakdown
    })

@app.route('/country/<country>')
def country_detail_page(country):
    """Serve the country detail page."""
    return render_template('country_detail.html', country_name=country)

@app.route('/technology/<tech_code>')
def technology_detail_page(tech_code):
    """Serve the technology detail page."""
    return render_template('technology_detail.html', tech_code=tech_code)

@app.route('/api/technologies/<tech_code>/detail')
@require_api_key('free')
def technology_detail(tech_code):
    """Detailed technology page data: fleet info, generation history, reactor list, country breakdown."""
    # Technology summary stats
    stats = query_db("""
        SELECT
            t.code,
            t.name as full_name,
            t.description,
            COUNT(*) as total,
            SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
            SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
            SUM(CASE WHEN r.status = 'Permanent Shutdown' THEN 1 ELSE 0 END) as shutdown,
            ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw,
            ROUND(AVG(CASE WHEN r.status = 'Operational' THEN r.age_years END), 1) as avg_age
        FROM technologies t
        LEFT JOIN reactors r ON t.id = r.technology_id
        WHERE UPPER(t.code) = UPPER(?)
        GROUP BY t.code, t.name, t.description
    """, (tech_code,))

    if not stats:
        return jsonify({'error': f'Technology not found: {tech_code}'}), 404

    # Generation history: sum by year across all reactors with this technology
    generation_history = query_db("""
        SELECT
            g.year,
            ROUND(SUM(g.electricity_gwh) / 1000.0, 2) as total_twh,
            COUNT(DISTINCT g.reactor_id) as reactor_count
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        JOIN technologies t ON r.technology_id = t.id
        WHERE UPPER(t.code) = UPPER(?)
        GROUP BY g.year
        ORDER BY g.year
    """, (tech_code,))

    # All reactors with this technology
    reactors = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               r.gross_capacity_mw, r.status, r.commercial_operation,
               r.permanent_shutdown, r.latitude, r.longitude
        FROM reactors r
        JOIN technologies t ON r.technology_id = t.id
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE UPPER(t.code) = UPPER(?)
        ORDER BY
            CASE r.status
                WHEN 'Operational' THEN 1
                WHEN 'Under Construction' THEN 2
                WHEN 'Long-term Shutdown' THEN 3
                WHEN 'Permanent Shutdown' THEN 4
                ELSE 5
            END,
            c.name COLLATE NOCASE, r.plant_name, r.unit_number
    """, (tech_code,))

    # Country breakdown (all statuses)
    country_breakdown = query_db("""
        SELECT c.name as country, COUNT(*) as count,
               ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors r
        JOIN technologies t ON r.technology_id = t.id
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE UPPER(t.code) = UPPER(?)
        GROUP BY c.name
        ORDER BY count DESC
    """, (tech_code,))

    return jsonify({
        'technology': stats[0],
        'generation_history': generation_history,
        'reactors': reactors,
        'country_breakdown': country_breakdown
    })

@app.route('/owner/<owner_name>')
def owner_detail_page(owner_name):
    """Serve the owner detail page."""
    return render_template('owner_detail.html', owner_name=owner_name)

@app.route('/api/owners/<owner_name>/detail')
@require_api_key('free')
def owner_detail(owner_name):
    """Detailed owner page data: summary stats, generation history, reactor list, country/technology breakdowns."""
    # Owner summary stats
    stats = query_db("""
        SELECT
            r.owner as name,
            COUNT(*) as total,
            SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
            SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
            SUM(CASE WHEN r.status = 'Permanent Shutdown' THEN 1 ELSE 0 END) as shutdown,
            ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw,
            ROUND(AVG(CASE WHEN r.status = 'Operational' THEN r.age_years END), 1) as avg_age,
            COUNT(DISTINCT r.country_id) as countries
        FROM reactors r
        WHERE r.owner COLLATE NOCASE = ?
        GROUP BY r.owner
    """, (owner_name,))

    if not stats:
        return jsonify({'error': f'Owner not found: {owner_name}'}), 404

    # Generation history: sum by year across all reactors owned by this owner
    generation_history = query_db("""
        SELECT
            g.year,
            ROUND(SUM(g.electricity_gwh) / 1000.0, 2) as total_twh,
            COUNT(DISTINCT g.reactor_id) as reactor_count
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE r.owner COLLATE NOCASE = ?
        GROUP BY g.year
        ORDER BY g.year
    """, (owner_name,))

    # All reactors owned by this owner
    reactors = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology, m.name as model_name,
               r.gross_capacity_mw, r.status, r.commercial_operation,
               r.permanent_shutdown, r.latitude, r.longitude
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        LEFT JOIN models m ON r.model_id = m.id
        WHERE r.owner COLLATE NOCASE = ?
        ORDER BY
            CASE r.status
                WHEN 'Operational' THEN 1
                WHEN 'Under Construction' THEN 2
                WHEN 'Long-term Shutdown' THEN 3
                WHEN 'Permanent Shutdown' THEN 4
                ELSE 5
            END,
            c.name COLLATE NOCASE, r.plant_name, r.unit_number
    """, (owner_name,))

    # Country breakdown
    country_breakdown = query_db("""
        SELECT c.name as country, COUNT(*) as count,
               ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE r.owner COLLATE NOCASE = ?
        GROUP BY c.name
        ORDER BY count DESC
    """, (owner_name,))

    # Technology breakdown
    technology_breakdown = query_db("""
        SELECT t.code as technology, COUNT(*) as count
        FROM reactors r
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE r.owner COLLATE NOCASE = ?
        GROUP BY t.code
        ORDER BY count DESC
    """, (owner_name,))

    return jsonify({
        'owner': stats[0],
        'generation_history': generation_history,
        'reactors': reactors,
        'country_breakdown': country_breakdown,
        'technology_breakdown': technology_breakdown
    })

@app.route('/status/<status>')
def status_detail_page(status):
    """Serve the status detail page."""
    return render_template('status_detail.html', status_name=status)

@app.route('/api/statuses/<status>/detail')
@require_api_key('free')
def status_detail(status):
    """Detailed status page data: summary stats, generation history, reactor list, country/technology breakdowns."""
    # Status summary stats
    stats = query_db("""
        SELECT
            r.status,
            COUNT(*) as total_count,
            ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw,
            ROUND(AVG(r.age_years), 1) as avg_age,
            COUNT(DISTINCT r.country_id) as countries
        FROM reactors r
        WHERE r.status = ?
        GROUP BY r.status
    """, (status,))

    if not stats:
        return jsonify({'error': f'Status not found: {status}'}), 404

    # Generation history: sum by year across all reactors with this status
    generation_history = query_db("""
        SELECT
            g.year,
            ROUND(SUM(g.electricity_gwh) / 1000.0, 2) as total_twh,
            COUNT(DISTINCT g.reactor_id) as reactor_count
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE r.status = ?
        GROUP BY g.year
        ORDER BY g.year
    """, (status,))

    # All reactors with this status
    reactors = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology, r.gross_capacity_mw, r.status,
               r.commercial_operation, r.permanent_shutdown,
               r.latitude, r.longitude
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE r.status = ?
        ORDER BY c.name COLLATE NOCASE, r.plant_name, r.unit_number
    """, (status,))

    # Country breakdown
    country_breakdown = query_db("""
        SELECT c.name as country, COUNT(*) as count,
               ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE r.status = ?
        GROUP BY c.name
        ORDER BY count DESC
    """, (status,))

    # Technology mix
    technology_mix = query_db("""
        SELECT t.code as technology, COUNT(*) as count,
               ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors r
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE r.status = ?
        GROUP BY t.code
        ORDER BY count DESC
    """, (status,))

    return jsonify({
        'status': stats[0],
        'generation_history': generation_history,
        'reactors': reactors,
        'country_breakdown': country_breakdown,
        'technology_mix': technology_mix
    })

@app.route('/supplier/<supplier_name>')
def supplier_detail_page(supplier_name):
    """Serve the supplier detail page."""
    return render_template('supplier_detail.html', supplier_name=supplier_name)

@app.route('/api/suppliers/<supplier_name>/detail')
@require_api_key('free')
def supplier_detail(supplier_name):
    """Detailed supplier page data: summary, generation history, reactor list, country/technology breakdowns."""
    # Supplier summary stats
    stats = query_db("""
        SELECT
            s.name,
            COUNT(*) as total,
            SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
            SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
            SUM(CASE WHEN r.status = 'Permanent Shutdown' THEN 1 ELSE 0 END) as shutdown,
            ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw,
            ROUND(AVG(CASE WHEN r.status = 'Operational' THEN r.age_years END), 1) as avg_age
        FROM suppliers s
        LEFT JOIN reactors r ON s.id = r.supplier_id
        WHERE LOWER(s.name) = LOWER(?)
        GROUP BY s.name
    """, (supplier_name,))

    if not stats:
        return jsonify({'error': f'Supplier not found: {supplier_name}'}), 404

    # Generation history: sum by year across all reactors built by this supplier
    generation_history = query_db("""
        SELECT
            g.year,
            ROUND(SUM(g.electricity_gwh) / 1000.0, 2) as total_twh,
            COUNT(DISTINCT g.reactor_id) as reactor_count
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        JOIN suppliers s ON r.supplier_id = s.id
        WHERE LOWER(s.name) = LOWER(?)
        GROUP BY g.year
        ORDER BY g.year
    """, (supplier_name,))

    # All reactors by this supplier
    reactors = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology, m.name as model_name,
               r.gross_capacity_mw, r.status, r.commercial_operation,
               r.permanent_shutdown, r.latitude, r.longitude
        FROM reactors r
        JOIN suppliers s ON r.supplier_id = s.id
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        LEFT JOIN models m ON r.model_id = m.id
        WHERE LOWER(s.name) = LOWER(?)
        ORDER BY
            CASE r.status
                WHEN 'Operational' THEN 1
                WHEN 'Under Construction' THEN 2
                WHEN 'Long-term Shutdown' THEN 3
                WHEN 'Permanent Shutdown' THEN 4
                ELSE 5
            END,
            c.name COLLATE NOCASE, r.plant_name, r.unit_number
    """, (supplier_name,))

    # Country breakdown
    country_breakdown = query_db("""
        SELECT c.name as country, COUNT(*) as count,
               ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors r
        JOIN suppliers s ON r.supplier_id = s.id
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE LOWER(s.name) = LOWER(?)
        GROUP BY c.name
        ORDER BY count DESC
    """, (supplier_name,))

    # Technology breakdown
    technology_breakdown = query_db("""
        SELECT t.code as technology, COUNT(*) as count
        FROM reactors r
        JOIN suppliers s ON r.supplier_id = s.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE LOWER(s.name) = LOWER(?)
        GROUP BY t.code
        ORDER BY count DESC
    """, (supplier_name,))

    return jsonify({
        'supplier': stats[0],
        'generation_history': generation_history,
        'reactors': reactors,
        'country_breakdown': country_breakdown,
        'technology_breakdown': technology_breakdown
    })

@app.route('/api/reactors/search')
@require_api_key('paid')
def search_reactors():
    """Search reactors by name."""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({'error': 'Query must be at least 2 characters'}), 400

    results = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology, r.gross_capacity_mw, r.status,
               r.commercial_operation, r.latitude, r.longitude
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE r.plant_name LIKE ?
        ORDER BY r.plant_name
    """, (f'%{query}%',))

    return jsonify({'query': query, 'results': results, 'count': len(results)})

@app.route('/api/query')
@require_api_key('paid')
def custom_query():
    """Custom analysis query."""
    technology = request.args.get('technology')
    country = request.args.get('country')
    start_year = request.args.get('start', type=int)
    end_year = request.args.get('end', type=int)

    if not all([technology, country, start_year, end_year]):
        return jsonify({'error': 'Required: technology, country, start, end'}), 400

    result = query_db("""
        SELECT
            AVG(g.electricity_gwh) as avg_annual_gwh,
            SUM(g.electricity_gwh) as total_gwh,
            COUNT(*) as data_points,
            COUNT(DISTINCT g.reactor_id) as reactor_count,
            MIN(g.year) as first_year,
            MAX(g.year) as last_year
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        JOIN technologies t ON r.technology_id = t.id
        JOIN countries c ON r.country_id = c.id
        WHERE t.code = ? AND c.name = ? AND g.year >= ? AND g.year <= ?
    """, (technology, country, start_year, end_year))

    if not result or not result[0]['avg_annual_gwh']:
        return jsonify({'error': 'No data found'}), 404

    r = result[0]
    return jsonify({
        'query': {'technology': technology, 'country': country, 'period': f'{start_year}-{end_year}'},
        'result': {
            'avg_annual_generation_gwh': round(r['avg_annual_gwh'], 2),
            'total_generation_twh': round(r['total_gwh'] / 1000, 2),
            'reactor_count': r['reactor_count'],
            'data_points': r['data_points']
        }
    })

@app.route('/api/planned')
@require_api_key('paid')
def planned_reactors():
    """Get planned reactors."""
    reactors = query_db("""
        SELECT p.project_name, p.unit_number, c.name as country,
               t.code as technology, p.model, p.gross_capacity_mw,
               p.vendor, p.expected_online, p.likelihood
        FROM planned_reactors p
        LEFT JOIN countries c ON p.country_id = c.id
        LEFT JOIN technologies t ON p.technology_id = t.id
        ORDER BY p.expected_online
    """)
    return jsonify({'planned_reactors': reactors, 'count': len(reactors)})

@app.route('/api/stats/history')
@require_api_key('free')
def stats_history():
    """Year-by-year historical stats for dashboard stat cards."""
    conn = get_db()
    cursor = conn.cursor()

    # Get year range from commercial_operation dates
    cursor.execute("""
        SELECT MIN(CAST(substr(commercial_operation, 1, 4) AS INTEGER)),
               MAX(CAST(substr(commercial_operation, 1, 4) AS INTEGER))
        FROM reactors WHERE commercial_operation IS NOT NULL
    """)
    min_year, max_year = cursor.fetchone()
    if not min_year:
        conn.close()
        return jsonify({'years': []})

    years = []
    for year in range(min_year, max_year + 1):
        year_end = f'{year}-12-31'
        year_start = f'{year}-01-01'

        # Operational reactors and capacity at end of year
        cursor.execute("""
            SELECT COUNT(*) as count,
                   ROUND(COALESCE(SUM(gross_capacity_mw), 0) / 1000.0, 1) as capacity_gw,
                   COUNT(DISTINCT country_id) as countries
            FROM reactors
            WHERE commercial_operation IS NOT NULL
              AND commercial_operation <= ?
              AND (permanent_shutdown IS NULL OR permanent_shutdown >= ?)
        """, (year_end, year_start))
        row = dict(cursor.fetchone())

        # Under construction at end of year (reactors that had not yet started operating)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM reactors
            WHERE commercial_operation IS NOT NULL
              AND commercial_operation > ?
              AND (permanent_shutdown IS NULL OR permanent_shutdown >= ?)
        """, (year_end, year_start))
        uc = cursor.fetchone()[0]

        # Generation for this year
        cursor.execute("""
            SELECT ROUND(COALESCE(SUM(electricity_gwh), 0) / 1000.0, 1) as twh,
                   COUNT(DISTINCT reactor_id) as reporting
            FROM generation_annual
            WHERE year = ?
        """, (year,))
        gen_row = cursor.fetchone()
        gen_twh = gen_row[0] if gen_row else 0
        gen_reporting = gen_row[1] if gen_row else 0

        # Coverage-adjust generation if needed
        operational_count = row['count']
        if gen_reporting > 0 and gen_reporting < operational_count:
            gen_twh = round(gen_twh * (operational_count / gen_reporting), 1)

        years.append({
            'year': year,
            'operational': row['count'],
            'capacity_gw': row['capacity_gw'],
            'countries': row['countries'],
            'under_construction': uc,
            'generation_twh': gen_twh
        })

    conn.close()

    # Compute average age per year
    for entry in years:
        y = entry['year']
        ages = query_db("""
            SELECT ROUND(AVG(
                (JULIANDAY(? || '-12-31') - JULIANDAY(commercial_operation)) / 365.25
            ), 1) as avg_age
            FROM reactors
            WHERE commercial_operation IS NOT NULL
              AND commercial_operation <= ?
              AND (permanent_shutdown IS NULL OR permanent_shutdown >= ?)
        """, (str(y), f'{y}-12-31', f'{y}-01-01'))
        entry['avg_age'] = ages[0]['avg_age'] if ages and ages[0]['avg_age'] else 0

    return jsonify({'years': years})


@app.route('/api/generation/decades')
@require_api_key('free')
def generation_decades():
    """Coverage-adjusted average annual nuclear generation by decade."""
    conn = get_db()
    cursor = conn.cursor()

    # Define decades: label, start year, end year
    decades = [
        ('1970s', 1970, 1979),
        ('1980s', 1980, 1989),
        ('1990s', 1990, 1999),
        ('2000s', 2000, 2009),
        ('2010s', 2010, 2019),
        ('2020s', 2020, 2024),
    ]

    result = []

    for label, start, end in decades:
        yearly_adjusted = []

        for year in range(start, end + 1):
            # Raw generation sum and count of reactors with data this year
            cursor.execute("""
                SELECT COALESCE(SUM(electricity_gwh), 0) as raw_gwh,
                       COUNT(DISTINCT reactor_id) as reporting
                FROM generation_annual
                WHERE year = ?
            """, (year,))
            row = cursor.fetchone()
            raw_gwh = row[0]
            reporting = row[1]

            if reporting == 0:
                continue

            # Count reactors that were operational during this year:
            # commercial_operation <= end of year AND
            # (no permanent_shutdown OR permanent_shutdown > start of year)
            year_start = f'{year}-01-01'
            year_end = f'{year}-12-31'
            cursor.execute("""
                SELECT COUNT(*) FROM reactors
                WHERE commercial_operation IS NOT NULL
                  AND commercial_operation <= ?
                  AND (permanent_shutdown IS NULL OR permanent_shutdown >= ?)
            """, (year_end, year_start))
            operational = cursor.fetchone()[0]

            if operational == 0:
                continue

            # Scale up: if only 112 of 430 reactors report, estimate full fleet
            adjustment = operational / reporting if reporting < operational else 1.0
            adjusted_twh = (raw_gwh / 1000.0) * adjustment
            yearly_adjusted.append({
                'year': year,
                'raw_twh': round(raw_gwh / 1000.0, 1),
                'reporting': reporting,
                'operational': operational,
                'adjusted_twh': round(adjusted_twh, 1)
            })

        if not yearly_adjusted:
            continue

        avg_annual = sum(y['adjusted_twh'] for y in yearly_adjusted) / len(yearly_adjusted)
        years_covered = len(yearly_adjusted)
        total_years = end - start + 1

        result.append({
            'decade': label,
            'avg_annual_twh': round(avg_annual, 1),
            'years_with_data': years_covered,
            'total_years': total_years,
            'is_partial': end >= 2024,
            'yearly_detail': yearly_adjusted
        })

    conn.close()

    return jsonify({
        'decades': result,
        'note': 'Adjusted for reporting coverage. 2020s based on available years projected at annual rate.'
    })


@app.route('/api/map')
@require_api_key('paid')
def map_data():
    """Get reactor coordinates for mapping."""
    status = request.args.get('status')

    sql = """
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology, r.gross_capacity_mw, r.status,
               r.latitude, r.longitude
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE r.latitude IS NOT NULL AND r.longitude IS NOT NULL
    """
    params = []
    if status:
        sql += " AND r.status = ?"
        params.append(status)

    reactors = query_db(sql, params if params else None)

    features = [{
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [r['longitude'], r['latitude']]},
        'properties': {
            'id': r['id'],
            'name': f"{r['plant_name']}-{r['unit_number']}",
            'country': r['country'],
            'technology': r['technology'],
            'capacity_mw': r['gross_capacity_mw'],
            'status': r['status']
        }
    } for r in reactors]

    return jsonify({'type': 'FeatureCollection', 'features': features, 'count': len(features)})

# =============================================================================
# DATA VALIDATION
# =============================================================================

def run_validation():
    """Run data validation checks and return results as a dict."""
    results = {}

    # 1. Per-year coverage: how many reactors have data for each year
    year_coverage = query_db("""
        SELECT g.year, COUNT(DISTINCT g.reactor_id) as reactor_count
        FROM generation_annual g
        WHERE g.year >= 2015
        GROUP BY g.year
        ORDER BY g.year
    """)
    results['year_coverage'] = year_coverage

    # Total operational reactors for context
    operational_count = query_db(
        "SELECT COUNT(*) as count FROM reactors WHERE status = 'Operational'"
    )[0]['count']
    results['operational_reactors'] = operational_count

    # 2. Missing year gaps: reactors that have data before AND after a year but not for that year
    gap_reactors = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               MIN(g.year) as first_year, MAX(g.year) as last_year,
               COUNT(g.year) as years_with_data
        FROM reactors r
        JOIN generation_annual g ON r.id = g.reactor_id
        JOIN countries c ON r.country_id = c.id
        WHERE r.status = 'Operational'
        GROUP BY r.id
        HAVING MAX(g.year) - MIN(g.year) + 1 > COUNT(g.year)
        ORDER BY (MAX(g.year) - MIN(g.year) + 1 - COUNT(g.year)) DESC
        LIMIT 50
    """)

    # For each reactor with gaps, find the specific missing years
    gaps_detail = []
    for reactor in gap_reactors:
        existing_years = query_db(
            "SELECT year FROM generation_annual WHERE reactor_id = ? ORDER BY year",
            (reactor['id'],)
        )
        existing_set = {r['year'] for r in existing_years}
        all_years = set(range(reactor['first_year'], reactor['last_year'] + 1))
        missing = sorted(all_years - existing_set)
        # Only report gaps in recent years (2015+)
        recent_missing = [y for y in missing if y >= 2015]
        if recent_missing:
            gaps_detail.append({
                'reactor_id': reactor['id'],
                'plant_name': reactor['plant_name'],
                'unit_number': reactor['unit_number'],
                'country': reactor['country'],
                'data_range': f"{reactor['first_year']}-{reactor['last_year']}",
                'missing_years': recent_missing
            })
    results['year_gaps'] = gaps_detail

    # 3. Operational reactors with no recent data (no data after 2020)
    no_recent = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               MAX(g.year) as last_data_year
        FROM reactors r
        LEFT JOIN generation_annual g ON r.id = g.reactor_id
        JOIN countries c ON r.country_id = c.id
        WHERE r.status = 'Operational'
        GROUP BY r.id
        HAVING MAX(g.year) < 2021 OR MAX(g.year) IS NULL
        ORDER BY c.name, r.plant_name
    """)
    results['no_recent_data'] = no_recent

    # 4. pris_id coverage
    pris_coverage = query_db("""
        SELECT
            COUNT(*) as total_operational,
            SUM(CASE WHEN pris_id IS NOT NULL THEN 1 ELSE 0 END) as with_pris_id
        FROM reactors
        WHERE status = 'Operational'
    """)[0]
    results['pris_coverage'] = pris_coverage

    return results


@app.route('/api/data/validation')
@require_api_key('free')
def data_validation():
    """Data quality validation report."""
    results = run_validation()
    return jsonify({
        'validation_report': {
            'operational_reactors': results['operational_reactors'],
            'year_coverage': results['year_coverage'],
            'year_gaps': results['year_gaps'],
            'no_recent_data': {
                'count': len(results['no_recent_data']),
                'reactors': results['no_recent_data']
            },
            'pris_id_coverage': results['pris_coverage']
        }
    })


def print_validation_report():
    """Print a text-formatted validation report to stdout."""
    results = run_validation()

    print("=" * 70)
    print("NUCLEAR DATABASE VALIDATION REPORT")
    print("=" * 70)

    print(f"\nOperational reactors: {results['operational_reactors']}")

    # Year coverage
    print(f"\n--- Year Coverage (2015+) ---")
    print(f"{'Year':<8} {'Reactors with data':<25} {'Coverage'}")
    for row in results['year_coverage']:
        pct = round(row['reactor_count'] / results['operational_reactors'] * 100, 1)
        bar = '#' * int(pct / 2)
        print(f"{row['year']:<8} {row['reactor_count']:<25} {pct:>5.1f}%  {bar}")

    # PRIS ID coverage
    pc = results['pris_coverage']
    print(f"\n--- PRIS ID Coverage ---")
    print(f"Operational reactors with pris_id: {pc['with_pris_id']}/{pc['total_operational']}")

    # Year gaps
    print(f"\n--- Year Gaps (recent, top {len(results['year_gaps'])}) ---")
    if results['year_gaps']:
        for g in results['year_gaps'][:20]:
            name = f"{g['plant_name']}-{g['unit_number']}"
            print(f"  {name:<35} {g['country']:<15} missing: {g['missing_years']}")
        if len(results['year_gaps']) > 20:
            print(f"  ... and {len(results['year_gaps']) - 20} more")
    else:
        print("  No gaps found.")

    # No recent data
    print(f"\n--- Operational Reactors Without Recent Data (post-2020) ---")
    print(f"Count: {len(results['no_recent_data'])}")
    if results['no_recent_data']:
        for r in results['no_recent_data'][:20]:
            name = f"{r['plant_name']}-{r['unit_number']}"
            last = r['last_data_year'] or 'never'
            print(f"  {name:<35} {r['country']:<15} last data: {last}")
        if len(results['no_recent_data']) > 20:
            print(f"  ... and {len(results['no_recent_data']) - 20} more")

    print("\n" + "=" * 70)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    if '--validate' in sys.argv:
        print_validation_report()
    else:
        port = int(os.environ.get('PORT', 5001))
        debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
        app.run(host='0.0.0.0', port=port, debug=debug)
