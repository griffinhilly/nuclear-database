#!/usr/bin/env python3
"""
Nuclear Reactor Database - Production App
Main entry point for deployment.
"""

import os
import sqlite3
from flask import Flask, jsonify, request, render_template
from functools import wraps
from pathlib import Path

# =============================================================================
# APP CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "nuclear_reactors.db"

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

    gen_2023 = query_db("SELECT SUM(electricity_gwh) as total FROM generation_annual WHERE year = 2023")

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
            'generation_2023_twh': round(gen_2023[0]['total'] / 1000, 1) if gen_2023[0]['total'] else None
        },
        'data_coverage': {
            'countries': 38,
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
            COUNT(CASE WHEN r.status = 'Operational' THEN 1 END) as operational,
            COUNT(CASE WHEN r.status = 'Under Construction' THEN 1 END) as under_construction
        FROM countries c
        LEFT JOIN reactors r ON c.id = r.country_id
        GROUP BY c.name
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
               r.commercial_operation, r.latitude, r.longitude
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        {where_sql}
        ORDER BY c.name, r.plant_name, r.unit_number
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
               r.gross_capacity_mw, r.status, r.commercial_operation,
               r.age_years, r.latitude, r.longitude
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE r.id = ?
    """, (reactor_id,))

    if not reactor:
        return jsonify({'error': 'Reactor not found'}), 404

    r = reactor[0]

    # Get generation history
    generation = query_db("""
        SELECT year, electricity_gwh, capacity_factor
        FROM generation_annual
        WHERE reactor_id = ?
        ORDER BY year DESC
        LIMIT 10
    """, (reactor_id,))

    # Get lifetime stats
    lifetime_stats = query_db("""
        SELECT
            SUM(electricity_gwh) as total_gwh,
            AVG(electricity_gwh) as avg_annual_gwh,
            AVG(capacity_factor) as avg_capacity_factor,
            MIN(year) as first_year,
            MAX(year) as last_year,
            COUNT(*) as years_operating
        FROM generation_annual
        WHERE reactor_id = ?
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
# MAIN
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
