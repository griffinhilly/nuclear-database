#!/usr/bin/env python3
"""
Fix coordinates for the 10 plants that had no Wikidata match.
All coordinates sourced from Wikipedia articles.
"""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

FIXES = [
    # Massively wrong (>1km)
    ("BREST", 56.6583, 84.9482,
     "Seversk NPP — DB had wrong longitude (78.33 vs 84.95), 404km fix"),
    ("Baltic", 54.9389, 22.1611,
     "Wikipedia: Kaliningrad Nuclear Power Plant — 90km fix"),
    ("CEFR", 39.7408, 116.0303,
     "Wikipedia: China Experimental Fast Reactor — DB longitude off by ~0.9 deg, 78km fix"),
    ("CVTR", 34.2625, -81.3292,
     "Wikipedia: Carolinas-Virginia Tube Reactor — 71km fix"),
    ("Bonus", 18.3664, -67.2686,
     "Wikipedia: BONUS reactor (Rincon, PR) — 41km fix"),

    # Close but improvable (<1km)
    ("BR-3", 51.2185, 5.0932,
     "Wikipedia: SCK CEN research center (BR-3 located there) — 720m fix"),
    ("Fort St. Vrain", 40.2439, -104.8754,
     "Wikipedia: Fort Saint Vrain NPP — user-verified on satellite, 510m fix"),
    ("Dounreay DFR", 58.5801, -3.7437,
     "Wikipedia: Dounreay — 360m fix"),
    ("Dounreay PFR", 58.5801, -3.7437,
     "Wikipedia: Dounreay — 360m fix"),
    ("Aktau", 43.607, 51.283,
     "Wikipedia: BN-350 reactor — 70m fix"),
]


def main():
    mode = "preview"
    if "--apply" in sys.argv:
        mode = "apply"

    conn = sqlite3.connect(DB_PATH)

    print("=" * 80)
    print("UNMATCHED PLANT COORDINATE FIXES (Wikipedia-sourced)")
    print("=" * 80)

    total = 0
    for plant, lat, lon, note in FIXES:
        rows = conn.execute(
            "SELECT id, latitude, longitude FROM reactors WHERE plant_name = ?",
            (plant,)).fetchall()
        if rows:
            old = f"({rows[0][1]}, {rows[0][2]})"
            print(f"\n  {plant} ({len(rows)} reactors): {old} -> ({lat}, {lon})")
            print(f"    {note}")
            total += len(rows)
            if mode == "apply":
                conn.execute(
                    "UPDATE reactors SET latitude = ?, longitude = ? WHERE plant_name = ?",
                    (lat, lon, plant))
        else:
            print(f"\n  {plant}: NOT FOUND")

    if mode == "apply":
        conn.commit()
        print(f"\n{'=' * 80}")
        print(f"APPLIED: {total} reactor records updated")
        print(f"{'=' * 80}")
    else:
        print(f"\n{'=' * 80}")
        print(f"DRY RUN: {total} reactors would be updated. Use --apply to execute.")
        print(f"{'=' * 80}")

    conn.close()


if __name__ == "__main__":
    main()
