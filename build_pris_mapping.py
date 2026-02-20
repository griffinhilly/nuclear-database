#!/usr/bin/env python3
"""
Build Complete PRIS ID Mapping
==============================
Uses pris_scraper.py's get_country_reactors() to fetch full reactor lists
from PRIS for all nuclear countries, then matches against the database
by plant name + unit number to build a complete PRIS ID mapping.

Output: Updates KNOWN_PRIS_IDS in fetch_pris_generation.py
"""

import sqlite3
import json
import time
import re
from pathlib import Path
from pris_scraper import PRISScraper, COUNTRIES

DATA_DIR = Path(__file__).parent
DB_PATH = DATA_DIR / "nuclear_reactors.db"
OUTPUT_FILE = DATA_DIR / "pris_id_mapping.json"


def get_db_reactors():
    """Get all reactors from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, r.plant_name, r.unit_number, r.status, c.name as country,
               r.pris_id
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        WHERE r.status IN ('Operational', 'Under Construction')
        ORDER BY c.name, r.plant_name, r.unit_number
    """)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def normalize_name(name):
    """Normalize reactor name for matching."""
    name = name.upper().strip()
    # Remove common suffixes/prefixes
    name = re.sub(r'\s*\(.*?\)\s*', '', name)  # Remove parenthetical
    name = re.sub(r'\s+', ' ', name)  # Normalize spaces
    name = name.replace('-', ' ').replace('_', ' ')
    return name


def match_pris_to_db(pris_reactors, db_reactors):
    """Match PRIS reactor entries to database entries."""
    mapping = {}  # key format: "PLANT_NAME-UNIT" → pris_id

    # Build lookup from DB
    db_lookup = {}
    for r in db_reactors:
        key = f"{r['plant_name'].upper()}-{r['unit_number']}"
        db_lookup[key] = r
        # Also create normalized version
        norm_key = f"{normalize_name(r['plant_name'])}-{r['unit_number']}"
        db_lookup[norm_key] = r

    for pris_r in pris_reactors:
        pris_name = pris_r.get('name', '').strip()
        pris_id = pris_r.get('pris_id')
        if not pris_name or not pris_id:
            continue

        # Try to parse unit number from PRIS name (e.g., "VOGTLE-3" or "BRUCE 3")
        match = re.match(r'^(.+?)[\s-]+(\d+)$', pris_name)
        if match:
            plant = match.group(1).strip()
            unit = match.group(2)
        else:
            plant = pris_name
            unit = "1"  # Single-unit plants

        # Try exact match
        key = f"{plant.upper()}-{unit}"
        if key in db_lookup:
            mapping[key] = int(pris_id)
            continue

        # Try normalized match
        norm_key = f"{normalize_name(plant)}-{unit}"
        if norm_key in db_lookup:
            mapping[key] = int(pris_id)
            continue

        # Try without unit suffix for single-unit plants
        for db_key, db_r in db_lookup.items():
            if normalize_name(plant) == normalize_name(db_r['plant_name']):
                full_key = f"{db_r['plant_name'].upper()}-{db_r['unit_number']}"
                if full_key not in mapping:
                    mapping[full_key] = int(pris_id)
                    break

    return mapping


def main():
    print("=" * 60)
    print("Building Complete PRIS ID Mapping")
    print("=" * 60)

    scraper = PRISScraper()
    db_reactors = get_db_reactors()
    print(f"Database has {len(db_reactors)} operational/construction reactors")

    all_pris_reactors = []

    for country, code in sorted(COUNTRIES.items()):
        print(f"  Fetching {country} ({code})...", end='')
        reactors = scraper.get_country_reactors(code)
        for r in reactors:
            r['country'] = country
        all_pris_reactors.extend(reactors)
        print(f" {len(reactors)} reactors")
        time.sleep(0.5)

    print(f"\nTotal PRIS reactors found: {len(all_pris_reactors)}")

    # Match
    mapping = match_pris_to_db(all_pris_reactors, db_reactors)
    print(f"Matched {len(mapping)} reactors to PRIS IDs")

    # Save mapping
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(mapping, f, indent=2, sort_keys=True)
    print(f"Saved mapping to {OUTPUT_FILE}")

    # Show what we'd add to fetch_pris_generation.py
    from fetch_pris_generation import KNOWN_PRIS_IDS
    new_ids = {k: v for k, v in mapping.items() if k not in KNOWN_PRIS_IDS}
    print(f"\nNew PRIS IDs not in KNOWN_PRIS_IDS: {len(new_ids)}")
    for name, pid in sorted(new_ids.items()):
        print(f"  '{name}': {pid},")

    return mapping


if __name__ == "__main__":
    main()
