#!/usr/bin/env python3
"""
Nuclear Reactor Database - Production App
Main entry point for deployment.
"""

import os
import sys
import sqlite3
from flask import Flask, jsonify, request, render_template, redirect
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

# SQL subquery: effective gross capacity for a (reactor, year) pair.
# Uses capacity_changes table when available, falls back to reactors.gross_capacity_mw.
# Requires 'r' aliased to reactors and 'g' aliased to generation_annual.
EFFECTIVE_CAPACITY = """
    COALESCE(
        (SELECT cc.gross_capacity_mw
         FROM capacity_changes cc
         WHERE cc.reactor_id = r.id
           AND cc.effective_date <= (g.year || '-12-31')
         ORDER BY cc.effective_date DESC
         LIMIT 1),
        r.gross_capacity_mw
    )"""

def get_entity_description(entity_type, entity_name):
    """Look up description from entity_descriptions table."""
    result = query_db(
        "SELECT description FROM entity_descriptions WHERE entity_type = ? AND LOWER(entity_name) = LOWER(?)",
        (entity_type, entity_name)
    )
    return result[0]['description'] if result else None

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

@app.route('/sources')
def sources():
    """Data sources and methodology page."""
    return render_template('sources.html')

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
            SUM(CASE WHEN status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
            SUM(CASE WHEN status = 'Suspended' THEN 1 ELSE 0 END) as suspended,
            SUM(CASE WHEN status = 'Long-term Shutdown' THEN 1 ELSE 0 END) as long_term_shutdown,
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
            'generation_years': '1954-2025',
            'last_updated': '2025-12'
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
            SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
            SUM(CASE WHEN r.status = 'Suspended' THEN 1 ELSE 0 END) as suspended,
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
                WHEN 'Suspended' THEN 3
                WHEN 'Long-term Shutdown' THEN 4
                WHEN 'Shutdown' THEN 5
                ELSE 6
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

    description = get_entity_description('country', country)

    return jsonify({
        'country': stats[0],
        'description': description,
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
               r.latitude, r.longitude,
               r.design_series, r.containment_type,
               m.name as model, s.name as supplier,
               r.owner, r.operator,
               r.construction_start, r.first_criticality, r.grid_connection,
               dl.slug as lineage_slug, dl.name as lineage_name
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        LEFT JOIN models m ON r.model_id = m.id
        LEFT JOIN suppliers s ON r.supplier_id = s.id
        LEFT JOIN design_series_info dsi ON r.design_series = dsi.design_series
        LEFT JOIN design_lineages dl ON dsi.lineage_id = dl.id
        WHERE r.id = ?
    """, (reactor_id,))

    if not reactor:
        return jsonify({'error': 'Reactor not found'}), 404

    r = reactor[0]

    # Get generation history (calculate capacity factor using historical capacity)
    generation = query_db(f"""
        SELECT g.year, g.electricity_gwh,
               ROUND(g.electricity_gwh / ({EFFECTIVE_CAPACITY} / 1000.0 * 8760) * 100, 1) as capacity_factor,
               ROUND({EFFECTIVE_CAPACITY}, 0) as effective_capacity_mw
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE g.reactor_id = ?
          AND r.gross_capacity_mw > 0
        ORDER BY g.year DESC
    """, (reactor_id,))

    # Get lifetime stats (calculate avg capacity factor using historical capacity)
    lifetime_stats = query_db(f"""
        SELECT
            SUM(g.electricity_gwh) as total_gwh,
            AVG(g.electricity_gwh) as avg_annual_gwh,
            ROUND(AVG(g.electricity_gwh / ({EFFECTIVE_CAPACITY} / 1000.0 * 8760) * 100), 1) as avg_capacity_factor,
            MIN(g.year) as first_year,
            MAX(g.year) as last_year,
            COUNT(*) as years_operating
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE g.reactor_id = ?
          AND r.gross_capacity_mw > 0
    """, (reactor_id,))[0]

    # Get capacity changes (uprates/derates) if any
    capacity_changes = query_db("""
        SELECT effective_date, gross_capacity_mw, net_capacity_mw,
               change_type, source, notes
        FROM capacity_changes
        WHERE reactor_id = ?
        ORDER BY effective_date
    """, (reactor_id,))

    # Get design series technical specs (table may not exist yet)
    design_specs = None
    if r.get('design_series'):
        try:
            specs = query_db("""
                SELECT * FROM design_series_specs WHERE design_series = ?
            """, (r['design_series'],))
            if specs:
                design_specs = specs[0]
        except Exception:
            pass

    # Get reactor-specific details (cooling type, vendors)
    reactor_details = None
    try:
        details = query_db("""
            SELECT cooling_type, constructor, architect_engineer,
                   turbine_supplier, pressure_vessel_manufacturer
            FROM reactor_details WHERE reactor_id = ?
        """, (reactor_id,))
        if details:
            reactor_details = details[0]
    except Exception:
        pass

    response = {
        'reactor': r,
        'generation_history': generation,
        'lifetime_stats': {
            'total_generation_twh': round(lifetime_stats['total_gwh'] / 1000, 2) if lifetime_stats['total_gwh'] else None,
            'avg_annual_gwh': round(lifetime_stats['avg_annual_gwh'], 1) if lifetime_stats['avg_annual_gwh'] else None,
            'avg_capacity_factor': round(lifetime_stats['avg_capacity_factor'], 1) if lifetime_stats['avg_capacity_factor'] else None,
            'years_operating': lifetime_stats['years_operating'],
            'first_year': lifetime_stats['first_year'],
            'last_year': lifetime_stats['last_year']
        },
        'capacity_changes': capacity_changes
    }
    if design_specs:
        response['design_specs'] = design_specs
    if reactor_details:
        response['reactor_details'] = reactor_details

    return jsonify(response)

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
               ROUND(AVG(g.electricity_gwh / ({EFFECTIVE_CAPACITY} / 1000.0 * 8760) * 100), 1) as avg_capacity_factor,
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

    description = get_entity_description('plant', plant_name)

    # Get capacity changes for all reactors at this plant
    capacity_changes = query_db(f"""
        SELECT cc.reactor_id, r.unit_number, cc.effective_date,
               cc.gross_capacity_mw, cc.net_capacity_mw,
               cc.change_type, cc.notes
        FROM capacity_changes cc
        JOIN reactors r ON cc.reactor_id = r.id
        WHERE cc.reactor_id IN ({placeholders})
        ORDER BY r.unit_number, cc.effective_date
    """, reactor_ids)

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
        'description': description,
        'reactors': [{
            **r,
            'lifetime_stats': unit_stats_map.get(r['id'], {})
        } for r in reactors],
        'generation_history': generation_history,
        'capacity_changes': capacity_changes,
        'plant_stats': {
            'total_generation_twh': round(plant_total_gwh / 1000, 2) if plant_total_gwh else None,
            'years_with_data': len(plant_years),
            'first_year': min(plant_years) if plant_years else None,
            'last_year': max(plant_years) if plant_years else None,
        }
    })

@app.route('/model/<path:model_name>')
def model_detail_page(model_name):
    """Serve the model detail page."""
    return render_template('model_detail.html', model_name=model_name)

@app.route('/api/models/<path:model_name>/detail')
@require_api_key('free')
def model_detail(model_name):
    """Detailed model page data: summary stats, generation history, reactor list, country breakdown.
    Falls back to design_series lookup if no exact model name match (for lineage tree links)."""
    # Try exact model name first
    stats = query_db("""
        SELECT
            m.name,
            t.code as technology_code,
            COUNT(*) as total,
            SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
            SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
            SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
            ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw,
            ROUND(AVG(CASE WHEN r.status = 'Operational' THEN r.age_years END), 1) as avg_age
        FROM models m
        LEFT JOIN reactors r ON m.id = r.model_id
        LEFT JOIN technologies t ON m.technology_id = t.id
        WHERE LOWER(m.name) = LOWER(?)
        GROUP BY m.name, t.code
    """, (model_name,))

    # If model name matched, check if there's a broader design_series that includes
    # additional model variants (e.g., "W (2-loop)" + "W (2-loop) DRYAMB" both belong to "W 2-Loop")
    is_design_series = False
    if stats:
        ds_check = query_db("""
            SELECT r.design_series
            FROM reactors r
            JOIN models m ON r.model_id = m.id
            WHERE LOWER(m.name) = LOWER(?) AND r.design_series IS NOT NULL
            GROUP BY r.design_series
        """, (model_name,))
        if len(ds_check) == 1:
            design_series_name = ds_check[0]['design_series']
            ds_total = query_db("SELECT COUNT(*) as cnt FROM reactors WHERE LOWER(design_series) = LOWER(?)", (design_series_name,))
            if ds_total and ds_total[0]['cnt'] > stats[0]['total']:
                is_design_series = True
                model_name = design_series_name
                stats = query_db("""
                    SELECT
                        ? as name,
                        t.code as technology_code,
                        COUNT(*) as total,
                        SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
                        SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
                        SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
                        ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw,
                        ROUND(AVG(CASE WHEN r.status = 'Operational' THEN r.age_years END), 1) as avg_age
                    FROM reactors r
                    LEFT JOIN technologies t ON r.technology_id = t.id
                    WHERE LOWER(r.design_series) = LOWER(?)
                    GROUP BY t.code
                """, (design_series_name, design_series_name))

    # If no model match, try design_series lookup (aggregates all model variants)
    if not is_design_series and not stats:
        ds_check = query_db("SELECT 1 FROM reactors WHERE LOWER(design_series) = LOWER(?) LIMIT 1", (model_name,))
        if not ds_check:
            return jsonify({'error': f'Model not found: {model_name}'}), 404
        is_design_series = True
        stats = query_db("""
            SELECT
                ? as name,
                t.code as technology_code,
                COUNT(*) as total,
                SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
                SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
                SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
                ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw,
                ROUND(AVG(CASE WHEN r.status = 'Operational' THEN r.age_years END), 1) as avg_age
            FROM reactors r
            LEFT JOIN technologies t ON r.technology_id = t.id
            WHERE LOWER(r.design_series) = LOWER(?)
            GROUP BY t.code
        """, (model_name, model_name))

    if not stats:
        return jsonify({'error': f'Model not found: {model_name}'}), 404

    # Build WHERE clause based on lookup type
    if is_design_series:
        where_clause = "LOWER(r.design_series) = LOWER(?)"
        where_param = model_name
    else:
        where_clause = "LOWER(m.name) = LOWER(?)"
        where_param = model_name

    # Generation history
    gen_join = "JOIN models m ON r.model_id = m.id" if not is_design_series else ""
    generation_history = query_db(f"""
        SELECT
            g.year,
            ROUND(SUM(g.electricity_gwh) / 1000.0, 2) as total_twh,
            COUNT(DISTINCT g.reactor_id) as reactor_count
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        {gen_join}
        WHERE {where_clause}
        GROUP BY g.year
        ORDER BY g.year
    """, (where_param,))

    # All reactors
    reactors = query_db(f"""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology, m.name as model,
               r.gross_capacity_mw, r.status, r.commercial_operation,
               r.permanent_shutdown, r.latitude, r.longitude
        FROM reactors r
        JOIN models m ON r.model_id = m.id
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE {where_clause}
        ORDER BY
            CASE r.status
                WHEN 'Operational' THEN 1
                WHEN 'Under Construction' THEN 2
                WHEN 'Suspended' THEN 3
                WHEN 'Long-term Shutdown' THEN 4
                WHEN 'Shutdown' THEN 5
                ELSE 6
            END,
            c.name COLLATE NOCASE, r.plant_name, r.unit_number
    """, (where_param,))

    # Country breakdown
    country_breakdown = query_db(f"""
        SELECT c.name as country, COUNT(*) as count,
               ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors r
        {"JOIN models m ON r.model_id = m.id" if not is_design_series else ""}
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE {where_clause}
        GROUP BY c.name
        ORDER BY count DESC
    """, (where_param,))

    # Lineage info — join through models for exact match, direct for design_series
    if is_design_series:
        lineage_info = query_db("""
            SELECT dl.slug as lineage_slug, dl.name as lineage_name
            FROM reactors r
            JOIN design_series_info dsi ON r.design_series = dsi.design_series
            JOIN design_lineages dl ON dsi.lineage_id = dl.id
            WHERE LOWER(r.design_series) = LOWER(?)
            LIMIT 1
        """, (model_name,))
    else:
        lineage_info = query_db("""
            SELECT dl.slug as lineage_slug, dl.name as lineage_name
            FROM reactors r
            JOIN models m ON r.model_id = m.id
            JOIN design_series_info dsi ON r.design_series = dsi.design_series
            JOIN design_lineages dl ON dsi.lineage_id = dl.id
            WHERE LOWER(m.name) = LOWER(?)
            LIMIT 1
        """, (model_name,))

    result = {
        'model': stats[0],
        'generation_history': generation_history,
        'reactors': reactors,
        'country_breakdown': country_breakdown
    }
    if lineage_info:
        result['lineage_slug'] = lineage_info[0]['lineage_slug']
        result['lineage_name'] = lineage_info[0]['lineage_name']

    # Design series
    if is_design_series:
        result['design_series'] = model_name
        # Use design_series_info description as fallback
        dsi_desc = query_db("SELECT description FROM design_series_info WHERE LOWER(design_series) = LOWER(?)", (model_name,))
        result['description'] = dsi_desc[0]['description'] if dsi_desc and dsi_desc[0]['description'] else None
        # List model variants under this series
        variants = query_db("""
            SELECT DISTINCT m.name FROM reactors r
            JOIN models m ON r.model_id = m.id
            WHERE LOWER(r.design_series) = LOWER(?)
            ORDER BY m.name
        """, (model_name,))
        result['model_variants'] = [v['name'] for v in variants]
    else:
        ds_info = query_db("""
            SELECT r.design_series
            FROM reactors r
            JOIN models m ON r.model_id = m.id
            WHERE LOWER(m.name) = LOWER(?) AND r.design_series IS NOT NULL
            LIMIT 1
        """, (model_name,))
        if ds_info:
            result['design_series'] = ds_info[0]['design_series']
        result['description'] = get_entity_description('model', model_name)

    return jsonify(result)

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
            SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
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
                WHEN 'Suspended' THEN 3
                WHEN 'Long-term Shutdown' THEN 4
                WHEN 'Shutdown' THEN 5
                ELSE 6
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
            SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
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
                WHEN 'Suspended' THEN 3
                WHEN 'Long-term Shutdown' THEN 4
                WHEN 'Shutdown' THEN 5
                ELSE 6
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

    description = get_entity_description('owner', owner_name)

    return jsonify({
        'owner': stats[0],
        'description': description,
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

    description = get_entity_description('status', status)

    return jsonify({
        'status': stats[0],
        'description': description,
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
            SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
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
                WHEN 'Suspended' THEN 3
                WHEN 'Long-term Shutdown' THEN 4
                WHEN 'Shutdown' THEN 5
                ELSE 6
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

    description = get_entity_description('supplier', supplier_name)

    return jsonify({
        'supplier': stats[0],
        'description': description,
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

@app.route('/planned/<project_name>')
def planned_detail_page(project_name):
    """Serve the planned plant detail page."""
    return render_template('planned_detail.html', project_name=project_name)

@app.route('/api/planned/<project_name>')
@require_api_key('free')
def planned_detail(project_name):
    """Planned plant detail: all planned units at a project, milestones, nearby plants."""
    units = query_db("""
        SELECT p.id, p.project_name, p.unit_number, c.name as country,
               t.code as technology, p.model, p.gross_capacity_mw, p.net_capacity_mw,
               p.thermal_capacity_mw, p.vendor, p.vendor_country, p.is_export,
               p.expected_construction_start, p.expected_online,
               p.likelihood, p.likelihood_rating, p.status, p.notes,
               p.latitude, p.longitude, p.developer, p.cost_estimate, p.description,
               p.site_location
        FROM planned_reactors p
        LEFT JOIN countries c ON p.country_id = c.id
        LEFT JOIN technologies t ON p.technology_id = t.id
        WHERE p.project_name = ?
        ORDER BY CAST(p.unit_number AS INTEGER), p.unit_number
    """, (project_name,))

    if not units:
        return jsonify({'error': f'Planned plant not found: {project_name}'}), 404

    first = units[0]

    # Parse milestones from notes field (split by sentence, match keywords)
    milestones = []
    notes_text = first['notes'] or ''
    sentences = [s.strip() for s in notes_text.replace('. ', '.\n').split('\n') if s.strip()]
    milestone_keywords = [
        ('Development Consent Order', 'DCO'),
        ('Site preparation', 'Construction prep'),
        ('Final Investment Decision', 'FID'),
        ('first concrete', 'FCP'),
        ('grid connection', 'Grid connection'),
    ]
    for keyword, label in milestone_keywords:
        for sentence in sentences:
            if keyword.lower() in sentence.lower():
                milestones.append({'date': label, 'description': sentence.rstrip('.'), 'future': False})
                break

    # Add future milestones from data
    if first['expected_construction_start']:
        milestones.append({
            'date': f"~{first['expected_construction_start']}",
            'description': 'Expected construction start (first nuclear concrete)',
            'future': True
        })
    if first['expected_online']:
        online_years = sorted(set(u['expected_online'] for u in units if u['expected_online']))
        for yr in online_years:
            matching = [u for u in units if u['expected_online'] == yr]
            unit_labels = ', '.join(f"Unit {u['unit_number']}" for u in matching)
            milestones.append({
                'date': f"~{yr}",
                'description': f'{unit_labels} expected online',
                'future': True
            })

    # Find nearby existing plants (same coordinates or similar name)
    nearby = []
    if first['latitude'] and first['longitude']:
        nearby = query_db("""
            SELECT DISTINCT r.plant_name as name,
                   CASE
                       WHEN SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) > 0 THEN 'Operational'
                       WHEN SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) > 0 THEN 'Under Construction'
                       WHEN SUM(CASE WHEN r.status = 'Suspended' THEN 1 ELSE 0 END) > 0 THEN 'Suspended'
                       ELSE 'Shutdown'
                   END as status
            FROM reactors r
            WHERE ABS(r.latitude - ?) < 0.05 AND ABS(r.longitude - ?) < 0.05
            GROUP BY r.plant_name
            ORDER BY r.plant_name
        """, (first['latitude'], first['longitude']))

    return jsonify({
        'plant': {
            'project_name': first['project_name'],
            'country': first['country'],
            'site_location': first['site_location'],
            'technology': first['technology'],
            'latitude': first['latitude'],
            'longitude': first['longitude'],
            'developer': first['developer'],
            'cost_estimate': first['cost_estimate'],
            'description': first['description'],
            'thermal_capacity_mw': first['thermal_capacity_mw'],
            'likelihood': first['likelihood'],
            'status': first['status'],
            'expected_online': min(u['expected_online'] for u in units if u['expected_online']) if any(u['expected_online'] for u in units) else None,
        },
        'units': [{
            'unit_number': u['unit_number'],
            'model': u['model'],
            'gross_capacity_mw': u['gross_capacity_mw'],
            'net_capacity_mw': u['net_capacity_mw'],
            'vendor': u['vendor'],
            'vendor_country': u['vendor_country'],
            'expected_online': u['expected_online'],
            'likelihood': u['likelihood'],
            'notes': u['notes'],
        } for u in units],
        'milestones': milestones,
        'nearby_plants': nearby,
    })

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
        ('2020s', 2020, 2025),
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
            'is_partial': end >= 2025,
            'yearly_detail': yearly_adjusted
        })

    conn.close()

    return jsonify({
        'decades': result,
        'note': 'Adjusted for reporting coverage. 2020s based on available years projected at annual rate.'
    })


@app.route('/api/generation/annual')
@require_api_key('free')
def generation_annual_share():
    """Annual nuclear generation and share of global electricity."""
    conn = get_db()
    cursor = conn.cursor()

    # Global electricity generation by year (TWh) - IEA/EI Statistical Review data
    global_electricity_twh = {
        1970: 5249, 1971: 5529, 1972: 5876, 1973: 6242, 1974: 6370,
        1975: 6504, 1976: 6945, 1977: 7281, 1978: 7611, 1979: 7897,
        1980: 8043, 1981: 8129, 1982: 8161, 1983: 8476, 1984: 8917,
        1985: 9259, 1986: 9544, 1987: 9958, 1988: 10368, 1989: 10717,
        1990: 11020, 1991: 11195, 1992: 11380, 1993: 11596, 1994: 11890,
        1995: 12264, 1996: 12658, 1997: 12998, 1998: 13235, 1999: 13547,
        2000: 14013, 2001: 14303, 2002: 14821, 2003: 15365, 2004: 16057,
        2005: 16595, 2006: 17242, 2007: 17880, 2008: 18200, 2009: 17930,
        2010: 19050, 2011: 19700, 2012: 20200, 2013: 20800, 2014: 21300,
        2015: 21700, 2016: 22200, 2017: 22800, 2018: 23400, 2019: 23700,
        2020: 23500, 2021: 24800, 2022: 25200, 2023: 25600, 2024: 26100,
    }

    result = []
    for year in range(1970, 2025):
        cursor.execute("""
            SELECT COALESCE(SUM(electricity_gwh), 0) as raw_gwh,
                   COUNT(DISTINCT reactor_id) as reporting
            FROM generation_annual WHERE year = ?
        """, (year,))
        row = cursor.fetchone()
        raw_gwh, reporting = row[0], row[1]
        if reporting == 0:
            continue

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

        adjustment = operational / reporting if reporting < operational else 1.0
        nuclear_twh = round((raw_gwh / 1000.0) * adjustment, 1)
        global_twh = global_electricity_twh.get(year)
        share_pct = round(nuclear_twh / global_twh * 100, 1) if global_twh else None

        result.append({
            'year': year,
            'nuclear_twh': nuclear_twh,
            'global_twh': global_twh,
            'share_pct': share_pct,
            'reporting_reactors': reporting,
            'operational_reactors': operational
        })

    conn.close()
    return jsonify({
        'annual': result,
        'source': 'Nuclear: IAEA PRIS (coverage-adjusted). Global electricity: IEA/EI Statistical Review.'
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
            'plant_name': r['plant_name'],
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

    # 5. Capacity factor anomalies (CF > 100% using historical capacity)
    cf_anomalies = query_db(f"""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               g.year, g.electricity_gwh,
               ROUND({EFFECTIVE_CAPACITY}, 0) as effective_capacity_mw,
               ROUND(g.electricity_gwh / ({EFFECTIVE_CAPACITY} / 1000.0 * 8760) * 100, 1) as capacity_factor
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        JOIN countries c ON r.country_id = c.id
        WHERE r.gross_capacity_mw > 0
          AND g.electricity_gwh / ({EFFECTIVE_CAPACITY} / 1000.0 * 8760) * 100 > 105
        ORDER BY g.electricity_gwh / ({EFFECTIVE_CAPACITY} / 1000.0 * 8760) * 100 DESC
    """)
    results['cf_anomalies'] = cf_anomalies

    # 6. Whitespace issues in key text columns
    whitespace_issues = query_db("""
        SELECT 'models.name' as location, m.id, m.name as value
        FROM models m WHERE m.name != TRIM(m.name)
        UNION ALL
        SELECT 'reactors.plant_name', r.id, r.plant_name
        FROM reactors r WHERE r.plant_name != TRIM(r.plant_name)
        UNION ALL
        SELECT 'reactors.design_series', r.id, r.design_series
        FROM reactors r WHERE r.design_series IS NOT NULL AND r.design_series != TRIM(r.design_series)
        UNION ALL
        SELECT 'suppliers.name', s.id, s.name
        FROM suppliers s WHERE s.name != TRIM(s.name)
        UNION ALL
        SELECT 'reactors.owner', r.id, r.owner
        FROM reactors r WHERE r.owner IS NOT NULL AND r.owner != TRIM(r.owner)
    """)
    results['whitespace_issues'] = whitespace_issues

    return results


@app.route('/api/capacity/history')
@require_api_key('free')
def capacity_history():
    """Installed nuclear capacity by year, optionally filtered by country or technology."""
    country = request.args.get('country')
    technology = request.args.get('technology')

    conn = get_db()
    cursor = conn.cursor()

    # Build filter clauses
    joins = ""
    where_extra = ""
    filter_params = []
    if country:
        joins += " JOIN countries c ON r.country_id = c.id"
        where_extra += " AND LOWER(c.name) = LOWER(?)"
        filter_params.append(country)
    if technology:
        joins += " JOIN technologies t ON r.technology_id = t.id"
        where_extra += " AND UPPER(t.code) = UPPER(?)"
        filter_params.append(technology)

    result = []
    for year in range(1954, 2027):
        year_end = f'{year}-12-31'
        year_start = f'{year}-01-01'

        sql = f"""
            SELECT COUNT(*) as reactor_count,
                   ROUND(SUM(
                       COALESCE(
                           (SELECT cc.gross_capacity_mw
                            FROM capacity_changes cc
                            WHERE cc.reactor_id = r.id
                              AND cc.effective_date <= ?
                            ORDER BY cc.effective_date DESC
                            LIMIT 1),
                           r.gross_capacity_mw
                       )
                   ) / 1000.0, 1) as capacity_gw
            FROM reactors r
            {joins}
            WHERE r.commercial_operation IS NOT NULL
              AND r.commercial_operation <= ?
              AND (r.permanent_shutdown IS NULL OR r.permanent_shutdown >= ?)
              {where_extra}
        """
        params = [year_end, year_end, year_start] + filter_params
        cursor.execute(sql, params)
        row = cursor.fetchone()
        if row['reactor_count'] > 0:
            result.append({
                'year': year,
                'reactor_count': row['reactor_count'],
                'capacity_gw': row['capacity_gw']
            })

    conn.close()
    return jsonify({'history': result})


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

    # CF anomalies
    anomalies = results.get('cf_anomalies', [])
    print(f"\n--- Capacity Factor Anomalies (CF > 105%) ---")
    print(f"Count: {len(anomalies)}")
    if anomalies:
        for a in anomalies[:20]:
            name = f"{a['plant_name']}-{a['unit_number']}"
            print(f"  {name:<35} {a['country']:<15} {a['year']}  CF={a['capacity_factor']}%  ({a['effective_capacity_mw']:.0f} MW)")
        if len(anomalies) > 20:
            print(f"  ... and {len(anomalies) - 20} more")
    else:
        print("  No anomalies found.")

    print("\n" + "=" * 70)


# =============================================================================
# LINEAGE ROUTES & API
# =============================================================================

@app.route('/lineages')
def lineages_page():
    """Serve the lineage listing page."""
    return render_template('lineages.html')

@app.route('/lineage/<slug>')
def lineage_detail_page(slug):
    """Serve the lineage detail page."""
    return render_template('lineage_detail.html', lineage_slug=slug)

@app.route('/api/lineages')
@require_api_key('free')
def lineages_list():
    """All design lineages with reactor counts and status breakdown."""
    lineages = query_db("""
        SELECT dl.id, dl.name, dl.slug, dl.description, dl.origin_country,
               dl.original_designer, dl.technology_type,
               COUNT(r.id) as reactor_count,
               SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
               SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
               SUM(CASE WHEN r.status = 'Suspended' THEN 1 ELSE 0 END) as suspended,
               SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
               ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw,
               COUNT(DISTINCT dsi.id) as series_count
        FROM design_lineages dl
        JOIN design_series_info dsi ON dsi.lineage_id = dl.id
        JOIN reactors r ON r.design_series = dsi.design_series
        GROUP BY dl.id
        ORDER BY COUNT(r.id) DESC
    """)
    return jsonify({'lineages': lineages})

@app.route('/api/lineages/<slug>/detail')
@require_api_key('free')
def lineage_detail(slug):
    """Full lineage detail: info, series tree, and reactor list."""
    lineage = query_db("SELECT * FROM design_lineages WHERE slug = ?", (slug,))
    if not lineage:
        return jsonify({'error': 'Lineage not found'}), 404
    lineage = lineage[0]

    # Series in this lineage with reactor counts
    series = query_db("""
        SELECT dsi.design_series, dsi.generation_order, dsi.generation_label,
               dsi.typical_capacity_mwe, dsi.first_commercial_year, dsi.predecessor,
               dsi.description,
               COUNT(r.id) as reactor_count,
               SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
               SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
               SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
               SUM(CASE WHEN r.status = 'Suspended' THEN 1 ELSE 0 END) as suspended
        FROM design_series_info dsi
        LEFT JOIN reactors r ON r.design_series = dsi.design_series
        WHERE dsi.lineage_id = ?
        GROUP BY dsi.id
        ORDER BY dsi.generation_order
    """, (lineage['id'],))

    # All reactors in this lineage
    reactors = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country, r.status,
               r.gross_capacity_mw, r.commercial_operation, r.permanent_shutdown,
               r.design_series, r.latitude, r.longitude
        FROM reactors r
        JOIN design_series_info dsi ON r.design_series = dsi.design_series
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE dsi.lineage_id = ?
        ORDER BY r.design_series, c.name, r.plant_name, r.unit_number
    """, (lineage['id'],))

    # Aggregate stats
    stats = query_db("""
        SELECT
            COUNT(r.id) as total,
            SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
            SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
            SUM(CASE WHEN r.status = 'Suspended' THEN 1 ELSE 0 END) as suspended,
            SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
            ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw,
            COUNT(DISTINCT c.name) as countries
        FROM reactors r
        JOIN design_series_info dsi ON r.design_series = dsi.design_series
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE dsi.lineage_id = ?
    """, (lineage['id'],))[0]

    # Country breakdown
    country_breakdown = query_db("""
        SELECT c.name as country,
               COUNT(r.id) as count,
               ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors r
        JOIN design_series_info dsi ON r.design_series = dsi.design_series
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE dsi.lineage_id = ? AND r.status = 'Operational'
        GROUP BY c.name
        ORDER BY SUM(r.gross_capacity_mw) DESC
    """, (lineage['id'],))

    return jsonify({
        'lineage': lineage,
        'series': series,
        'reactors': reactors,
        'stats': stats,
        'country_breakdown': country_breakdown
    })

# =============================================================================
# CONTAINMENT TYPES
# =============================================================================

@app.route('/containment')
def containment_page():
    """Serve the containment types overview page."""
    return render_template('containment_detail.html')

@app.route('/containment/<containment_type>')
def containment_detail_page(containment_type):
    """Redirect old per-type URLs to overview page with filter."""
    return redirect(f'/containment?type={containment_type}')

@app.route('/api/containment/overview')
@require_api_key('free')
def containment_overview():
    """All containment types with stats, descriptions, and reactor list."""
    types = query_db("""
        SELECT r.containment_type,
            COUNT(*) as total,
            SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as operational,
            SUM(CASE WHEN r.status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
            SUM(CASE WHEN r.status = 'Shutdown' THEN 1 ELSE 0 END) as shutdown,
            SUM(CASE WHEN r.status = 'Suspended' THEN 1 ELSE 0 END) as suspended,
            ROUND(SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) / 1000.0, 1) as capacity_gw
        FROM reactors r
        WHERE r.containment_type IS NOT NULL AND r.containment_type != ''
        GROUP BY r.containment_type
        ORDER BY COUNT(*) DESC
    """)

    # Attach descriptions
    type_list = []
    for t in types:
        desc = get_entity_description('containment', t['containment_type'])
        type_list.append({
            'name': t['containment_type'],
            'description': desc,
            'total': t['total'],
            'operational': t['operational'],
            'under_construction': t['under_construction'],
            'shutdown': t['shutdown'],
            'suspended': t['suspended'],
            'capacity_gw': t['capacity_gw']
        })

    reactors = query_db("""
        SELECT r.id, r.plant_name, r.unit_number, c.name as country,
               t.code as technology, m.name as model,
               r.containment_type, r.gross_capacity_mw, r.status,
               r.commercial_operation, r.permanent_shutdown,
               r.latitude, r.longitude
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        LEFT JOIN models m ON r.model_id = m.id
        WHERE r.containment_type IS NOT NULL AND r.containment_type != ''
        ORDER BY
            CASE r.status
                WHEN 'Operational' THEN 1
                WHEN 'Under Construction' THEN 2
                WHEN 'Suspended' THEN 3
                WHEN 'Long-term Shutdown' THEN 4
                WHEN 'Shutdown' THEN 5
                ELSE 6
            END,
            c.name COLLATE NOCASE, r.plant_name, r.unit_number
    """)

    return jsonify({
        'types': type_list,
        'reactors': reactors
    })

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
