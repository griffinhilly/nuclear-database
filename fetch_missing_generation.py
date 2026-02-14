#!/usr/bin/env python3
"""
Fetch missing generation data from IAEA PRIS and insert directly into SQLite.

This script:
1. Maps KNOWN_PRIS_IDS to reactors.id by matching plant_name + unit_number
2. Fetches ALL available years from each PRIS reactor page (1960-2030)
3. Inserts any years missing from the DB with INSERT OR IGNORE
4. Updates reactors.pris_id for matched reactors
"""

import sqlite3
import time
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Reuse KNOWN_PRIS_IDS from the existing fetch script
from fetch_pris_generation import KNOWN_PRIS_IDS, PRIS_BASE

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "nuclear_reactors.db"

MIN_YEAR = 1960
MAX_YEAR = 2030

# Manual mapping from PRIS key names to (plant_name, unit_number) in the database.
# Only entries that can't be matched automatically need to be listed here.
# Format: 'PRIS_KEY': ('db_plant_name', 'db_unit_number')
PRIS_TO_DB_OVERRIDES = {
    # USA - names differ between PRIS keys and DB
    'ANO-1': ('Arkansas Nuclear One', '1'),
    'ANO-2': ('Arkansas Nuclear One', '2'),
    'COOK-1': ('Cook (Donald C. Cook)', '1'),
    'COOK-2': ('Cook (Donald C. Cook)', '2'),
    'DAVIS-BESSE-1': ('Davis Besse', '1'),
    'FITZPATRICK': ('Fitzpatrick (James A. Fitzpatrick)', '1'),
    'GINNA': ('Ginna (R. E. Ginna)', '1'),
    'FARLEY-1': ('Farley (Joseph M. Farley)', '1'),
    'FARLEY-2': ('Farley (Joseph M. Farley)', '2'),
    'HATCH-1': ('Hatch (Edwin I. Hatch)', '1'),
    'HATCH-2': ('Hatch (Edwin I. Hatch)', '2'),
    'ROBINSON-2': ('Robinson (H B Robinson)', '2'),
    'ST. LUCIE-1': ('St Lucie', '1'),
    'ST. LUCIE-2': ('St Lucie', '2'),
    'SOUTH TEXAS-1': ('South Texas Project', '1'),
    'SOUTH TEXAS-2': ('South Texas Project', '2'),
    'COLUMBIA': ('Columbia', '1'),
    'COOPER': ('Cooper', '1'),
    'MONTICELLO': ('Monticello', '1'),
    'POINT LEPREAU': ('Point Lepreau', '1'),
    'SIZEWELL B': ('Sizewell B', '1'),
    'GRAND GULF-1': ('Grand Gulf', '1'),

    # France - Flamanville 3 is separate EPR unit
    'FLAMANVILLE-3': ('Flamanville', '3'),

    # Russia - DB uses "Kursk 1" / "Leningrad 1" / "Novovoronezh 1" style
    'KURSK-1': ('Kursk 1', '1'),
    'KURSK-2': ('Kursk 1', '2'),
    'KURSK-3': ('Kursk 1', '3'),
    'KURSK-4': ('Kursk 1', '4'),
    'LENINGRAD-1': ('Leningrad 1', '1'),
    'LENINGRAD-2': ('Leningrad 1', '2'),
    'LENINGRAD-3': ('Leningrad 1', '3'),
    'LENINGRAD-4': ('Leningrad 1', '4'),
    'LENINGRAD II-1': ('Leningrad 2', '1'),
    'LENINGRAD II-2': ('Leningrad 2', '2'),
    'NOVOVORONEZH-3': ('Novovoronezh 1', '3'),
    'NOVOVORONEZH-4': ('Novovoronezh 1', '4'),
    'NOVOVORONEZH-5': ('Novovoronezh 1', '5'),
    'NOVOVORONEZH II-1': ('Novovoronezh 2', '1'),
    'NOVOVORONEZH II-2': ('Novovoronezh 2', '2'),

    # South Korea - DB has parenthetical former names
    'HANBIT-1': ('Hanbit (Yonggwang)', '1'),
    'HANBIT-2': ('Hanbit (Yonggwang)', '2'),
    'HANBIT-3': ('Hanbit (Yonggwang)', '3'),
    'HANBIT-4': ('Hanbit (Yonggwang)', '4'),
    'HANBIT-5': ('Hanbit (Yonggwang)', '5'),
    'HANBIT-6': ('Hanbit (Yonggwang)', '6'),
    'HANUL-1': ('Hanul (Ulchin)', '1'),
    'HANUL-2': ('Hanul (Ulchin)', '2'),
    'HANUL-3': ('Hanul (Ulchin)', '3'),
    'HANUL-4': ('Hanul (Ulchin)', '4'),
    'HANUL-5': ('Hanul (Ulchin)', '5'),
    'HANUL-6': ('Hanul (Ulchin)', '6'),
    'SHIN-HANUL-1': ('Shin-Hanul (Shin-Ulchin)', '1'),
    'SHIN-HANUL-2': ('Shin-Hanul (Shin-Ulchin)', '2'),

    # UK - DB uses "Dungeness B", "Heysham A", etc. directly
    'DUNGENESS B-1': ('Dungeness B', '1'),
    'DUNGENESS B-2': ('Dungeness B', '2'),
    'HEYSHAM A-1': ('Heysham A', '1'),
    'HEYSHAM A-2': ('Heysham A', '2'),
    'HEYSHAM B-1': ('Heysham B', '1'),
    'HEYSHAM B-2': ('Heysham B', '2'),
    'HINKLEY POINT B-1': ('Hinkley Point B', '1'),
    'HINKLEY POINT B-2': ('Hinkley Point B', '2'),
    'HUNTERSTON B-1': ('Hunterston B', '1'),
    'HUNTERSTON B-2': ('Hunterston B', '2'),
    'HARTLEPOOL-1': ('Hartlepool', '1'),
    'HARTLEPOOL-2': ('Hartlepool', '2'),
    'TORNESS-1': ('Torness', '1'),
    'TORNESS-2': ('Torness', '2'),

    # France
    'SAINT-ALBAN-1': ('St. Alban', '1'),
    'SAINT-ALBAN-2': ('St. Alban', '2'),

    # China
    'LING AO-1': ('Ling Ao', '1'),
    'LING AO-2': ('Ling Ao', '2'),
    'QINSHAN-1': ('Qinshan 1', '1'),
    'QINSHAN-2': ('Qinshan 2', '1'),
    'QINSHAN-3': ('Qinshan 3', '1'),
}


def parse_pris_key(pris_key):
    """Parse a PRIS key like 'BRAIDWOOD-2' into (plant_name, unit_number).

    Returns title-cased plant name and unit number string.
    Handles keys with no unit suffix (e.g., 'COLUMBIA').
    """
    # Try splitting on last hyphen to get unit number
    parts = pris_key.rsplit('-', 1)
    if len(parts) == 2 and parts[1].isdigit():
        name = parts[0].title()
        unit = parts[1]
    else:
        # No unit number suffix (e.g., COLUMBIA, COOPER)
        name = pris_key.title()
        unit = '1'
    return name, unit


def build_reactor_lookup(conn):
    """Build a lookup dict from (UPPER(plant_name), unit_number) -> reactor_id."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, plant_name, unit_number FROM reactors")
    lookup = {}
    for row in cursor.fetchall():
        reactor_id, plant_name, unit_number = row
        key = (plant_name.upper(), str(unit_number or '').strip())
        lookup[key] = (reactor_id, plant_name)
    return lookup


def map_pris_to_db(conn):
    """Map KNOWN_PRIS_IDS entries to database reactor IDs.

    Returns list of (pris_key, pris_id, reactor_db_id, db_plant_name) tuples.
    """
    lookup = build_reactor_lookup(conn)
    matched = []
    unmatched = []

    for pris_key, pris_id in KNOWN_PRIS_IDS.items():
        # First check manual overrides
        if pris_key in PRIS_TO_DB_OVERRIDES:
            db_name, db_unit = PRIS_TO_DB_OVERRIDES[pris_key]
            db_key = (db_name.upper(), db_unit)
            if db_key in lookup:
                reactor_db_id, actual_name = lookup[db_key]
                matched.append((pris_key, pris_id, reactor_db_id, actual_name))
                continue

        # Auto-match: parse the PRIS key and look up
        name, unit = parse_pris_key(pris_key)
        db_key = (name.upper(), unit)
        if db_key in lookup:
            reactor_db_id, actual_name = lookup[db_key]
            matched.append((pris_key, pris_id, reactor_db_id, actual_name))
        else:
            unmatched.append(pris_key)

    return matched, unmatched


def get_existing_years(conn, reactor_db_id):
    """Return the set of years already in generation_annual for this reactor."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT year FROM generation_annual WHERE reactor_id = ?",
        (reactor_db_id,)
    )
    return {row[0] for row in cursor.fetchall()}


def fetch_reactor_generation(pris_id, session):
    """Fetch ALL available generation data for a reactor from PRIS.

    Parses any year between MIN_YEAR and MAX_YEAR from the page tables.
    """
    url = f"{PRIS_BASE}{pris_id}"

    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        generation = {}
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    first_cell = cells[0].text.strip()
                    if first_cell.isdigit() and MIN_YEAR <= int(first_cell) <= MAX_YEAR:
                        year = int(first_cell)
                        for cell in cells[1:]:
                            cell_text = cell.text.strip().replace(',', '').replace(' ', '')
                            try:
                                if cell_text and cell_text not in ['NC', 'N/A', '-', '']:
                                    val = float(cell_text)
                                    if 0 < val < 20000:
                                        generation[year] = val
                                        break
                            except ValueError:
                                continue

        return generation

    except Exception as e:
        print(f"  Error fetching PRIS ID {pris_id}: {e}")
        return {}


def main():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    print("=" * 60)
    print("Fetch Missing Generation Data (all years from PRIS)")
    print("=" * 60)

    # Step 1: Map PRIS IDs to database reactor IDs
    print("\n[1/4] Mapping PRIS IDs to database reactors...")
    matched, unmatched = map_pris_to_db(conn)
    print(f"  Matched: {len(matched)} reactors")
    if unmatched:
        print(f"  Unmatched: {len(unmatched)} PRIS keys: {', '.join(unmatched[:10])}")
        if len(unmatched) > 10:
            print(f"    ... and {len(unmatched) - 10} more")

    # Step 2: Fetch from PRIS and insert missing years
    print(f"\n[2/4] Fetching all available data from PRIS ({len(matched)} reactors)...")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Nuclear Research Database Bot)'
    })

    fetched_count = 0
    inserted_count = 0
    errors = 0
    cursor = conn.cursor()

    for i, (pris_key, pris_id, reactor_db_id, db_name) in enumerate(matched, 1):
        existing = get_existing_years(conn, reactor_db_id)
        print(f"  [{i}/{len(matched)}] {db_name} (PRIS {pris_id})...", end='')

        generation = fetch_reactor_generation(pris_id, session)

        if generation:
            fetched_count += 1
            # Find years PRIS has that our DB doesn't
            new_years = {y: v for y, v in generation.items() if y not in existing}

            if new_years:
                years_inserted = []
                for year in sorted(new_years):
                    try:
                        cursor.execute(
                            "INSERT OR IGNORE INTO generation_annual (reactor_id, year, electricity_gwh) VALUES (?, ?, ?)",
                            (reactor_db_id, year, new_years[year])
                        )
                        if cursor.rowcount > 0:
                            inserted_count += 1
                            years_inserted.append(str(year))
                    except sqlite3.Error as e:
                        print(f" DB error: {e}", end='')
                        errors += 1

                if years_inserted:
                    print(f" inserted {', '.join(years_inserted)}")
                else:
                    print(" no new data (already in DB)")
            else:
                pris_range = f"{min(generation)}-{max(generation)}" if generation else "none"
                print(f" no new data (PRIS has {pris_range}, all in DB)")
        else:
            print(" fetch failed")
            errors += 1

        # Rate limiting: 0.5s between requests
        time.sleep(0.5)

    conn.commit()

    # Step 3: Update pris_id column
    print(f"\n[3/4] Updating reactors.pris_id for {len(matched)} matched reactors...")
    updated_pris = 0
    for pris_key, pris_id, reactor_db_id, db_name in matched:
        cursor.execute(
            "UPDATE reactors SET pris_id = ? WHERE id = ? AND (pris_id IS NULL OR pris_id != ?)",
            (pris_id, reactor_db_id, pris_id)
        )
        if cursor.rowcount > 0:
            updated_pris += 1

    conn.commit()
    print(f"  Updated pris_id for {updated_pris} reactors")

    # Step 4: Summary
    print(f"\n[4/4] Summary")
    print("=" * 60)
    print(f"  PRIS keys mapped to DB: {len(matched)}/{len(KNOWN_PRIS_IDS)}")
    print(f"  Successfully fetched:   {fetched_count}")
    print(f"  Data points inserted:   {inserted_count}")
    print(f"  Fetch/DB errors:        {errors}")
    print(f"  pris_id column updated: {updated_pris}")

    # Post-fetch coverage
    print("\n  Post-fetch coverage (recent years):")
    cursor.execute(
        "SELECT year, COUNT(*) FROM generation_annual WHERE year >= 2010 GROUP BY year ORDER BY year"
    )
    for year, count in cursor.fetchall():
        print(f"    {year}: {count} reactors")

    # Total records
    cursor.execute("SELECT COUNT(*) FROM generation_annual")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT MIN(year), MAX(year) FROM generation_annual")
    min_yr, max_yr = cursor.fetchone()
    print(f"\n  Total generation records: {total} ({min_yr}-{max_yr})")

    conn.close()
    print("\nDone.")


if __name__ == '__main__':
    main()
