#!/usr/bin/env python3
"""
Nuclear Reactor SQLite Database
Builds and manages the nuclear reactor database for querying.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent
DB_FILE = DATA_DIR / "nuclear_reactors.db"
EXCEL_FILE = DATA_DIR / "nuclear_database_updated.xlsx"


def create_database():
    """Create the SQLite database with optimized schema."""

    # Remove existing database
    if DB_FILE.exists():
        DB_FILE.unlink()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # =========================================================================
    # CORE TABLES
    # =========================================================================

    # Countries table
    cursor.execute("""
        CREATE TABLE countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            code TEXT,
            region TEXT
        )
    """)

    # Reactor types/technologies
    cursor.execute("""
        CREATE TABLE technologies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT,
            description TEXT
        )
    """)

    # Reactor models
    cursor.execute("""
        CREATE TABLE models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            technology_id INTEGER,
            FOREIGN KEY (technology_id) REFERENCES technologies(id)
        )
    """)

    # Suppliers/Vendors
    cursor.execute("""
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            country_id INTEGER,
            FOREIGN KEY (country_id) REFERENCES countries(id)
        )
    """)

    # =========================================================================
    # MAIN REACTORS TABLE
    # =========================================================================

    cursor.execute("""
        CREATE TABLE reactors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Identification
            plant_name TEXT NOT NULL,
            unit_number TEXT,
            reactor_id TEXT UNIQUE,
            pris_id INTEGER,

            -- Location
            country_id INTEGER,
            state_province TEXT,
            site_location TEXT,
            latitude REAL,
            longitude REAL,

            -- Technical specs
            technology_id INTEGER,
            model_id INTEGER,
            thermal_capacity_mw REAL,
            gross_capacity_mw REAL,
            net_capacity_mw REAL,
            reference_power_mw REAL,

            -- Ownership & Supply
            owner TEXT,
            operator TEXT,
            supplier_id INTEGER,

            -- Status & Dates
            status TEXT NOT NULL,
            construction_start DATE,
            first_criticality DATE,
            grid_connection DATE,
            commercial_operation DATE,
            permanent_shutdown DATE,
            planned_retirement DATE,
            licensed_until DATE,

            -- Performance metrics
            construction_time_years REAL,
            age_years REAL,
            lifetime_generation_gwh REAL,
            lifetime_energy_factor REAL,
            lifetime_load_factor REAL,

            -- Metadata
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (country_id) REFERENCES countries(id),
            FOREIGN KEY (technology_id) REFERENCES technologies(id),
            FOREIGN KEY (model_id) REFERENCES models(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
    """)

    # =========================================================================
    # GENERATION DATA (Time Series)
    # =========================================================================

    cursor.execute("""
        CREATE TABLE generation_annual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reactor_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            electricity_gwh REAL,
            capacity_factor REAL,
            availability_factor REAL,

            FOREIGN KEY (reactor_id) REFERENCES reactors(id),
            UNIQUE(reactor_id, year)
        )
    """)

    # =========================================================================
    # PLANNED REACTORS
    # =========================================================================

    cursor.execute("""
        CREATE TABLE planned_reactors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Identification
            project_name TEXT NOT NULL,
            unit_number TEXT,

            -- Location
            country_id INTEGER,
            site_location TEXT,

            -- Technical specs
            technology_id INTEGER,
            model TEXT,
            gross_capacity_mw REAL,
            net_capacity_mw REAL,

            -- Vendor info
            vendor TEXT,
            vendor_country TEXT,
            is_export INTEGER,

            -- Timeline
            expected_construction_start INTEGER,
            expected_online INTEGER,

            -- Status
            likelihood TEXT,
            likelihood_rating INTEGER,
            status TEXT,
            notes TEXT,

            FOREIGN KEY (country_id) REFERENCES countries(id),
            FOREIGN KEY (technology_id) REFERENCES technologies(id)
        )
    """)

    # =========================================================================
    # INDEXES for fast querying
    # =========================================================================

    cursor.execute("CREATE INDEX idx_reactors_country ON reactors(country_id)")
    cursor.execute("CREATE INDEX idx_reactors_technology ON reactors(technology_id)")
    cursor.execute("CREATE INDEX idx_reactors_status ON reactors(status)")
    cursor.execute("CREATE INDEX idx_reactors_coords ON reactors(latitude, longitude)")
    cursor.execute("CREATE INDEX idx_generation_reactor ON generation_annual(reactor_id)")
    cursor.execute("CREATE INDEX idx_generation_year ON generation_annual(year)")
    cursor.execute("CREATE INDEX idx_generation_reactor_year ON generation_annual(reactor_id, year)")
    cursor.execute("CREATE INDEX idx_planned_country ON planned_reactors(country_id)")

    # =========================================================================
    # VIEWS for common queries
    # =========================================================================

    # View: Reactor summary with country and technology names
    cursor.execute("""
        CREATE VIEW reactor_summary AS
        SELECT
            r.id,
            r.plant_name,
            r.unit_number,
            r.reactor_id,
            c.name as country,
            r.state_province,
            r.site_location,
            t.code as technology,
            t.name as technology_name,
            m.name as model,
            r.gross_capacity_mw,
            r.net_capacity_mw,
            r.status,
            r.commercial_operation,
            r.permanent_shutdown,
            r.age_years,
            r.latitude,
            r.longitude,
            r.owner,
            s.name as supplier
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        LEFT JOIN models m ON r.model_id = m.id
        LEFT JOIN suppliers s ON r.supplier_id = s.id
    """)

    # View: Annual generation with reactor details
    cursor.execute("""
        CREATE VIEW generation_details AS
        SELECT
            g.year,
            g.electricity_gwh,
            r.plant_name,
            r.unit_number,
            c.name as country,
            t.code as technology,
            r.gross_capacity_mw,
            r.status
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        LEFT JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
    """)

    # View: Country statistics
    cursor.execute("""
        CREATE VIEW country_stats AS
        SELECT
            c.name as country,
            COUNT(CASE WHEN r.status = 'Operational' THEN 1 END) as operational_reactors,
            COUNT(CASE WHEN r.status = 'Under Construction' THEN 1 END) as under_construction,
            COUNT(CASE WHEN r.status = 'Permanent Shutdown' THEN 1 END) as shutdown,
            SUM(CASE WHEN r.status = 'Operational' THEN r.gross_capacity_mw ELSE 0 END) as operational_capacity_mw,
            AVG(CASE WHEN r.status = 'Operational' THEN r.age_years END) as avg_fleet_age
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        GROUP BY c.name
        ORDER BY operational_capacity_mw DESC
    """)

    conn.commit()
    conn.close()

    print(f"Created database schema: {DB_FILE}")


def populate_database():
    """Populate the database from Excel data."""

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Load Excel data
    print("Loading Excel data...")
    df = pd.read_excel(EXCEL_FILE, sheet_name='All Reactors')
    df_planned = pd.read_excel(EXCEL_FILE, sheet_name='Planned Reactors')

    # =========================================================================
    # Populate lookup tables
    # =========================================================================

    print("Populating lookup tables...")

    # Countries
    countries = df['Country'].dropna().unique()
    country_map = {}
    for country in countries:
        cursor.execute("INSERT OR IGNORE INTO countries (name) VALUES (?)", (country,))
        cursor.execute("SELECT id FROM countries WHERE name = ?", (country,))
        country_map[country] = cursor.fetchone()[0]

    # Add planned reactor countries
    for country in df_planned['Country'].dropna().unique():
        if country not in country_map:
            cursor.execute("INSERT OR IGNORE INTO countries (name) VALUES (?)", (country,))
            cursor.execute("SELECT id FROM countries WHERE name = ?", (country,))
            country_map[country] = cursor.fetchone()[0]

    print(f"  Countries: {len(country_map)}")

    # Technologies
    tech_names = {
        'PWR': 'Pressurized Water Reactor',
        'BWR': 'Boiling Water Reactor',
        'PHWR': 'Pressurized Heavy Water Reactor',
        'GCR': 'Gas Cooled Reactor',
        'LWGR': 'Light Water Graphite Reactor',
        'FBR': 'Fast Breeder Reactor',
        'HTGR': 'High Temperature Gas Reactor',
        'HWGCR': 'Heavy Water Gas Cooled Reactor',
        'HWLWR': 'Heavy Water Light Water Reactor',
        'LMGMR': 'Liquid Metal Graphite Moderated Reactor',
        'SGHWR': 'Steam Generating Heavy Water Reactor',
        'OCM': 'Organic Cooled and Moderated Reactor',
    }

    technologies = df['Technology'].dropna().unique()
    tech_map = {}
    for tech in technologies:
        name = tech_names.get(tech, tech)
        cursor.execute(
            "INSERT OR IGNORE INTO technologies (code, name) VALUES (?, ?)",
            (tech, name)
        )
        cursor.execute("SELECT id FROM technologies WHERE code = ?", (tech,))
        tech_map[tech] = cursor.fetchone()[0]

    print(f"  Technologies: {len(tech_map)}")

    # Models
    models = df['Model'].dropna().unique()
    model_map = {}
    for model in models:
        cursor.execute("INSERT OR IGNORE INTO models (name) VALUES (?)", (str(model),))
        cursor.execute("SELECT id FROM models WHERE name = ?", (str(model),))
        model_map[model] = cursor.fetchone()[0]

    print(f"  Models: {len(model_map)}")

    # Suppliers
    suppliers = df['Supplier'].dropna().unique()
    supplier_map = {}
    for supplier in suppliers:
        cursor.execute("INSERT OR IGNORE INTO suppliers (name) VALUES (?)", (str(supplier),))
        cursor.execute("SELECT id FROM suppliers WHERE name = ?", (str(supplier),))
        supplier_map[supplier] = cursor.fetchone()[0]

    print(f"  Suppliers: {len(supplier_map)}")

    # =========================================================================
    # Populate reactors
    # =========================================================================

    print("Populating reactors...")

    # Identify year columns
    year_cols = [c for c in df.columns if isinstance(c, int) and 1954 <= c <= 2030]

    reactor_count = 0
    generation_count = 0

    for idx, row in df.iterrows():
        # Get foreign key IDs
        country_id = country_map.get(row.get('Country'))
        tech_id = tech_map.get(row.get('Technology'))
        model_id = model_map.get(row.get('Model'))
        supplier_id = supplier_map.get(row.get('Supplier'))

        # Parse dates safely
        def parse_date(val):
            if pd.isna(val):
                return None
            if isinstance(val, datetime):
                return val.strftime('%Y-%m-%d')
            return str(val)[:10] if val else None

        # Insert reactor
        cursor.execute("""
            INSERT INTO reactors (
                plant_name, unit_number, reactor_id,
                country_id, state_province, site_location,
                latitude, longitude,
                technology_id, model_id,
                thermal_capacity_mw, gross_capacity_mw, net_capacity_mw, reference_power_mw,
                owner, supplier_id,
                status,
                construction_start, grid_connection, commercial_operation,
                permanent_shutdown, planned_retirement, licensed_until,
                construction_time_years, age_years,
                lifetime_generation_gwh, lifetime_energy_factor, lifetime_load_factor,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get('Plant Name'),
            str(row.get('#')) if pd.notna(row.get('#')) else None,
            row.get('Reactor_ID'),
            country_id,
            row.get('State') if pd.notna(row.get('State')) else None,
            row.get('Location') if pd.notna(row.get('Location')) else None,
            float(row.get('Latitude')) if pd.notna(row.get('Latitude')) else None,
            float(row.get('Longitude')) if pd.notna(row.get('Longitude')) else None,
            tech_id,
            model_id,
            float(row.get('Thermal Capacity')) if pd.notna(row.get('Thermal Capacity')) else None,
            float(row.get('Gross Capacity')) if pd.notna(row.get('Gross Capacity')) else None,
            float(row.get('Design Net Capacity')) if pd.notna(row.get('Design Net Capacity')) else None,
            float(row.get('Reference Unit Power (MW)')) if pd.notna(row.get('Reference Unit Power (MW)')) else None,
            row.get('Owner') if pd.notna(row.get('Owner')) else None,
            supplier_id,
            str(row.get('Status')) if pd.notna(row.get('Status')) else 'Unknown',
            parse_date(row.get('Construction Start')),
            parse_date(row.get('Grid Connection')),
            parse_date(row.get('Commercial Operation')),
            parse_date(row.get('Permanent Shutdown Date')),
            parse_date(row.get('Planned Retirement Date')),
            parse_date(row.get('Licensed Until')),
            float(row.get('Construction Time')) if pd.notna(row.get('Construction Time')) else None,
            float(row.get('Age')) if pd.notna(row.get('Age')) else None,
            float(row.get('Lifetime Electricity Production')) if pd.notna(row.get('Lifetime Electricity Production')) else None,
            float(row.get('Lifetime Energy Avail. Factor')) if pd.notna(row.get('Lifetime Energy Avail. Factor')) else None,
            float(row.get('Lifetime Load Factor')) if pd.notna(row.get('Lifetime Load Factor')) else None,
            row.get('Notes') if pd.notna(row.get('Notes')) else None,
        ))

        reactor_db_id = cursor.lastrowid
        reactor_count += 1

        # Insert generation data
        for year in year_cols:
            val = row.get(year)
            if pd.notna(val):
                try:
                    gwh = float(val)
                    if gwh > 0:
                        cursor.execute("""
                            INSERT INTO generation_annual (reactor_id, year, electricity_gwh)
                            VALUES (?, ?, ?)
                        """, (reactor_db_id, year, gwh))
                        generation_count += 1
                except (ValueError, TypeError):
                    pass

    print(f"  Reactors: {reactor_count}")
    print(f"  Generation records: {generation_count}")

    # =========================================================================
    # Populate planned reactors
    # =========================================================================

    print("Populating planned reactors...")

    planned_count = 0
    for idx, row in df_planned.iterrows():
        country_id = country_map.get(row.get('Country'))
        tech_id = tech_map.get(row.get('Technology'))

        cursor.execute("""
            INSERT INTO planned_reactors (
                project_name, unit_number,
                country_id, site_location,
                technology_id, model,
                gross_capacity_mw, net_capacity_mw,
                vendor, vendor_country, is_export,
                expected_construction_start, expected_online,
                likelihood, likelihood_rating, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get('Plant Name'),
            str(row.get('#')) if pd.notna(row.get('#')) else None,
            country_id,
            None,
            tech_id,
            row.get('Model') if pd.notna(row.get('Model')) else None,
            float(row.get('Gross Capacity')) if pd.notna(row.get('Gross Capacity')) else None,
            float(row.get('Design Net Capacity')) if pd.notna(row.get('Design Net Capacity')) else None,
            row.get('Vendor') if pd.notna(row.get('Vendor')) else None,
            row.get('Vending Country') if pd.notna(row.get('Vending Country')) else None,
            1 if row.get('Exported reactor?') == 'Yes' else 0,
            int(row.get('Expected Start')) if pd.notna(row.get('Expected Start')) else None,
            int(row.get('Expected Online')) if pd.notna(row.get('Expected Online')) else None,
            row.get('Online by 2030 Likelihood') if pd.notna(row.get('Online by 2030 Likelihood')) else None,
            int(row.get('Number rating')) if pd.notna(row.get('Number rating')) else None,
            row.get('Status') if pd.notna(row.get('Status')) else None,
            row.get('Notes') if pd.notna(row.get('Notes')) else None,
        ))
        planned_count += 1

    print(f"  Planned reactors: {planned_count}")

    conn.commit()
    conn.close()

    print(f"\nDatabase populated: {DB_FILE}")
    print(f"Database size: {DB_FILE.stat().st_size / 1024:.1f} KB")


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


class NuclearDB:
    """High-level interface for querying the nuclear reactor database."""

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_FILE

    def _query(self, sql, params=None):
        """Execute a query and return results as list of dicts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def _query_df(self, sql, params=None):
        """Execute a query and return results as DataFrame."""
        conn = sqlite3.connect(self.db_path)
        if params:
            df = pd.read_sql_query(sql, conn, params=params)
        else:
            df = pd.read_sql_query(sql, conn)
        conn.close()
        return df

    # =========================================================================
    # REACTOR QUERIES
    # =========================================================================

    def get_reactor(self, plant_name, unit=None):
        """Get a specific reactor by name and optional unit number."""
        sql = "SELECT * FROM reactor_summary WHERE plant_name = ?"
        params = [plant_name]
        if unit:
            sql += " AND unit_number = ?"
            params.append(str(unit))
        return self._query(sql, params)

    def get_reactors_by_country(self, country, status=None):
        """Get all reactors in a country."""
        sql = "SELECT * FROM reactor_summary WHERE country = ?"
        params = [country]
        if status:
            sql += " AND status = ?"
            params.append(status)
        return self._query(sql, params)

    def get_reactors_by_technology(self, technology, status=None):
        """Get all reactors of a specific technology."""
        sql = "SELECT * FROM reactor_summary WHERE technology = ?"
        params = [technology]
        if status:
            sql += " AND status = ?"
            params.append(status)
        return self._query(sql, params)

    def get_operational_fleet(self):
        """Get all operational reactors."""
        return self._query("SELECT * FROM reactor_summary WHERE status = 'Operational'")

    def search_reactors(self, query):
        """Search reactors by name (partial match)."""
        sql = """
            SELECT * FROM reactor_summary
            WHERE plant_name LIKE ? OR site_location LIKE ?
        """
        pattern = f"%{query}%"
        return self._query(sql, (pattern, pattern))

    # =========================================================================
    # GENERATION QUERIES
    # =========================================================================

    def get_reactor_generation(self, plant_name, unit=None, start_year=None, end_year=None):
        """Get generation history for a reactor."""
        sql = """
            SELECT g.year, g.electricity_gwh, r.plant_name, r.unit_number
            FROM generation_annual g
            JOIN reactors r ON g.reactor_id = r.id
            WHERE r.plant_name = ?
        """
        params = [plant_name]

        if unit:
            sql += " AND r.unit_number = ?"
            params.append(str(unit))
        if start_year:
            sql += " AND g.year >= ?"
            params.append(start_year)
        if end_year:
            sql += " AND g.year <= ?"
            params.append(end_year)

        sql += " ORDER BY g.year"
        return self._query(sql, params)

    def get_country_generation(self, country, start_year=None, end_year=None):
        """Get total generation by year for a country."""
        sql = """
            SELECT
                g.year,
                SUM(g.electricity_gwh) as total_gwh,
                COUNT(DISTINCT g.reactor_id) as reactor_count
            FROM generation_annual g
            JOIN reactors r ON g.reactor_id = r.id
            JOIN countries c ON r.country_id = c.id
            WHERE c.name = ?
        """
        params = [country]

        if start_year:
            sql += " AND g.year >= ?"
            params.append(start_year)
        if end_year:
            sql += " AND g.year <= ?"
            params.append(end_year)

        sql += " GROUP BY g.year ORDER BY g.year"
        return self._query(sql, params)

    def get_technology_generation(self, technology, country=None, start_year=None, end_year=None):
        """Get generation by year for a technology type."""
        sql = """
            SELECT
                g.year,
                SUM(g.electricity_gwh) as total_gwh,
                AVG(g.electricity_gwh) as avg_gwh,
                COUNT(DISTINCT g.reactor_id) as reactor_count
            FROM generation_annual g
            JOIN reactors r ON g.reactor_id = r.id
            JOIN technologies t ON r.technology_id = t.id
        """
        params = []
        conditions = ["t.code = ?"]
        params.append(technology)

        if country:
            sql += " JOIN countries c ON r.country_id = c.id"
            conditions.append("c.name = ?")
            params.append(country)

        if start_year:
            conditions.append("g.year >= ?")
            params.append(start_year)
        if end_year:
            conditions.append("g.year <= ?")
            params.append(end_year)

        sql += " WHERE " + " AND ".join(conditions)
        sql += " GROUP BY g.year ORDER BY g.year"

        return self._query(sql, params)

    def avg_generation_by_technology_country_decade(self, technology, country, start_year, end_year):
        """
        Calculate average annual generation for a technology in a country over a period.
        Example: "Average annual generation for PWRs in the United States in the 2000s"
        """
        sql = """
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
            WHERE t.code = ?
              AND c.name = ?
              AND g.year >= ?
              AND g.year <= ?
        """
        return self._query(sql, (technology, country, start_year, end_year))

    # =========================================================================
    # STATISTICS QUERIES
    # =========================================================================

    def get_country_stats(self):
        """Get statistics by country."""
        return self._query("SELECT * FROM country_stats")

    def get_global_stats(self):
        """Get global nuclear statistics."""
        sql = """
            SELECT
                COUNT(*) as total_reactors,
                SUM(CASE WHEN status = 'Operational' THEN 1 ELSE 0 END) as operational,
                SUM(CASE WHEN status = 'Under Construction' THEN 1 ELSE 0 END) as under_construction,
                SUM(CASE WHEN status = 'Permanent Shutdown' THEN 1 ELSE 0 END) as shutdown,
                SUM(CASE WHEN status = 'Operational' THEN gross_capacity_mw ELSE 0 END) / 1000 as operational_gw,
                AVG(CASE WHEN status = 'Operational' THEN age_years END) as avg_age
            FROM reactors
        """
        return self._query(sql)[0]

    def get_generation_by_year(self, year):
        """Get total global generation for a specific year."""
        sql = """
            SELECT
                SUM(electricity_gwh) as total_gwh,
                COUNT(DISTINCT reactor_id) as reactor_count
            FROM generation_annual
            WHERE year = ?
        """
        return self._query(sql, (year,))[0]

    # =========================================================================
    # GEOGRAPHIC QUERIES
    # =========================================================================

    def get_reactors_with_coords(self):
        """Get all reactors with coordinates for mapping."""
        return self._query("""
            SELECT
                plant_name, unit_number, country, technology,
                gross_capacity_mw, status, latitude, longitude
            FROM reactor_summary
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)

    def get_reactors_in_region(self, min_lat, max_lat, min_lon, max_lon):
        """Get reactors within a geographic bounding box."""
        sql = """
            SELECT * FROM reactor_summary
            WHERE latitude BETWEEN ? AND ?
              AND longitude BETWEEN ? AND ?
        """
        return self._query(sql, (min_lat, max_lat, min_lon, max_lon))

    # =========================================================================
    # PLANNED REACTORS
    # =========================================================================

    def get_planned_reactors(self, country=None, likelihood=None):
        """Get planned reactors with optional filters."""
        sql = """
            SELECT
                p.project_name, p.unit_number, c.name as country,
                t.code as technology, p.model,
                p.gross_capacity_mw, p.vendor, p.vendor_country,
                p.expected_online, p.likelihood, p.status
            FROM planned_reactors p
            LEFT JOIN countries c ON p.country_id = c.id
            LEFT JOIN technologies t ON p.technology_id = t.id
            WHERE 1=1
        """
        params = []

        if country:
            sql += " AND c.name = ?"
            params.append(country)
        if likelihood:
            sql += " AND p.likelihood = ?"
            params.append(likelihood)

        sql += " ORDER BY p.expected_online"
        return self._query(sql, params if params else None)


def main():
    """Build the database."""
    print("=" * 60)
    print("Building Nuclear Reactor SQLite Database")
    print("=" * 60)

    create_database()
    populate_database()

    # Run some test queries
    print("\n" + "=" * 60)
    print("Testing Database Queries")
    print("=" * 60)

    db = NuclearDB()

    # Test 1: Global stats
    print("\n--- Global Statistics ---")
    stats = db.get_global_stats()
    print(f"Total reactors: {stats['total_reactors']}")
    print(f"Operational: {stats['operational']} ({stats['operational_gw']:.1f} GW)")
    print(f"Under construction: {stats['under_construction']}")
    print(f"Shutdown: {stats['shutdown']}")
    print(f"Average age: {stats['avg_age']:.1f} years")

    # Test 2: The user's example query
    print("\n--- Example Query: Average PWR generation in USA, 2000-2009 ---")
    result = db.avg_generation_by_technology_country_decade('PWR', 'USA', 2000, 2009)
    if result and result[0]['avg_annual_gwh']:
        r = result[0]
        print(f"Average annual generation per reactor: {r['avg_annual_gwh']:.2f} GWh")
        print(f"Total generation (decade): {r['total_gwh']:.2f} GWh")
        print(f"Data points: {r['data_points']}")
        print(f"Reactors included: {r['reactor_count']}")

    # Test 3: Country stats
    print("\n--- Top 10 Countries by Operational Capacity ---")
    country_stats = db.get_country_stats()
    for cs in country_stats[:10]:
        print(f"  {cs['country']}: {cs['operational_reactors']} reactors, "
              f"{cs['operational_capacity_mw']/1000:.1f} GW")

    # Test 4: Reactor search
    print("\n--- Search: 'Vogtle' ---")
    vogtle = db.search_reactors('Vogtle')
    for r in vogtle:
        print(f"  {r['plant_name']}-{r['unit_number']}: {r['status']}, "
              f"{r['gross_capacity_mw']} MW")

    # Test 5: Generation history
    print("\n--- Vogtle-1 Generation (2020-2024) ---")
    gen = db.get_reactor_generation('Vogtle', '1', 2020, 2024)
    for g in gen:
        print(f"  {g['year']}: {g['electricity_gwh']:.2f} GWh")

    print("\n" + "=" * 60)
    print("Database ready for queries!")
    print(f"Location: {DB_FILE}")
    print("=" * 60)


if __name__ == '__main__':
    main()
