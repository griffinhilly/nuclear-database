#!/usr/bin/env python3
"""
Fix remaining 7 'likely wrong' plants + Stade (in river).
All coordinates sourced from Wikipedia by manual verification.
Also renames EL-4 (Monts D'Arree) to Brennilis per user.
"""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

COORD_FIXES = [
    ("Lungmen (Fourth)", 25.038611, 121.924167,
     "Wikipedia: Lungmen Nuclear Power Plant"),
    ("Piqua", 40.1323056, -84.2373527,
     "Wikipedia: Piqua Nuclear Generating Station"),
    ("Elk River", 45.2890066, -93.5817684,
     "Wikipedia: Elk River Station"),
    ("EL-4 (Monts D'Arree)", 48.3524663, -3.8726512,
     "Wikipedia: Brennilis Nuclear Power Plant — 1.4km fix"),
    ("Vak Kahl", 50.0591194, 8.9872778,
     "Wikipedia: Kahl Nuclear Power Plant"),
    ("HDR Großwelzheim", 50.0591194, 8.9872778,
     "Wikipedia: same site as Kahl"),
    ("Lingen", 52.4774511, 7.3082937,
     "Wikipedia: Lingen Nuclear Power Plant"),
    ("Stade", 53.6267023, 9.5293137,
     "Wikipedia: Stade Nuclear Power Plant — was in middle of river"),
]

NAME_FIX = ("EL-4 (Monts D'Arree)", "Brennilis",
            "Wikipedia: officially Brennilis Nuclear Power Plant; EL-4 page is broken")


def main():
    mode = "preview"
    if "--apply" in sys.argv:
        mode = "apply"

    conn = sqlite3.connect(DB_PATH)

    print("=" * 80)
    print("REMAINING COORDINATE + NAME FIXES")
    print("=" * 80)

    total = 0
    for plant, lat, lon, note in COORD_FIXES:
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

    # Name fix
    old_name, new_name, reason = NAME_FIX
    rows = conn.execute(
        "SELECT id FROM reactors WHERE plant_name = ?", (old_name,)).fetchall()
    if rows:
        print(f"\n  RENAME: {old_name} -> {new_name} ({len(rows)} reactors)")
        print(f"    {reason}")
        if mode == "apply":
            conn.execute(
                "UPDATE reactors SET plant_name = ? WHERE plant_name = ?",
                (new_name, old_name))
    else:
        # Maybe already renamed by coord fix order
        print(f"\n  RENAME: {old_name} -> (NOT FOUND, may need coord fix first)")

    if mode == "apply":
        conn.commit()
        print(f"\n{'=' * 80}")
        print(f"APPLIED: {total} reactor coordinate updates + 1 rename")
        print(f"{'=' * 80}")
    else:
        print(f"\n{'=' * 80}")
        print(f"DRY RUN: {total} reactors would be updated. Use --apply to execute.")
        print(f"{'=' * 80}")

    conn.close()


if __name__ == "__main__":
    main()
