#!/usr/bin/env python3
"""
Final coordinate fixes based on Wikipedia/WNA manual verification.
Two batches: "likely wrong" (WD-only) and "truly concerning" (all disagree).
"""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

# (plant_name, new_lat, new_lon, note)
FIXES = [
    # === BATCH 1: "Likely Wrong" — Wikidata confirmed by Wikipedia ===
    ("Lucens", 46.6928, 6.8269,
     "Wikipedia 'Lucens reactor' — WD had matched wrong entity (Muhleberg)"),
    ("Niederaichbach", 48.6047, 12.3039,
     "Wikipedia: Niederaichbach NPP — 43km fix"),
    ("Hallam", 40.5583, -96.7847,
     "Wikipedia: Hallam Nuclear Power Facility — 35km fix"),
    ("Rolphton NPD", 46.1867, -77.6578,
     "Wikipedia: Nuclear Power Demonstration — 17.8km fix"),
    ("Jose Cabrera", 40.3492, -2.8844,
     "Wikipedia: Jose Cabrera Nuclear Power Station — 15.9km fix"),
    ("Lacrosse", 43.5601, -91.2315,
     "Wikipedia: La Crosse BWR — 14.2km fix"),
    ("Gösgen", 47.3661, 7.9667,
     "Wikipedia: Gosgen NPP — 13km fix"),
    ("Kozloduy", 43.7461, 23.7706,
     "Wikipedia: Kozloduy NPP — 11.2km fix"),
    ("Pathfinder", 43.6036, -96.6375,
     "Wikipedia: Pathfinder Nuclear Generating Station — 10.2km fix"),
    ("Chashma", 32.3903, 71.4625,
     "Wikipedia: Chashma Nuclear Power Complex — 7.8km fix"),
    ("Würgassen", 51.6392, 9.3914,
     "German Wikipedia: KKW Wurgassen — 4.9km fix"),
    ("El Dabaa", 31.0442, 28.4978,
     "Wikipedia: El Dabaa NPP — 4.6km fix"),
    ("AVR Jülich", 50.9031, 6.4211,
     "Wikipedia: AVR reactor — 4.1km fix"),
    ("Chapelcross", 55.0157, -3.2261,
     "Wikipedia: Chapelcross NPS — 3.6km fix"),
    ("Saxton", 40.2269, -78.2419,
     "Wikipedia: Saxton Nuclear Generating Station — 3.0km fix"),
    ("GE Vallecitos", 37.6133, -121.8402,
     "Wikipedia: Vallecitos Nuclear Center — 2.9km fix"),
    ("Gentilly", 46.3958, -72.3569,
     "Wikipedia: Gentilly Nuclear Generating Station — 2.5km fix"),

    # === BATCH 2: "Truly Concerning" — all sources disagreed ===
    ("Super-Phenix", 45.758333, 5.472222,
     "Wikipedia: Superphenix — DB had wrong longitude (15.6km fix)"),
    ("Fugen ATR", 35.754444, 136.016389,
     "Wikipedia: Fugen Nuclear Power Plant — 4.0km fix"),
    ("Embalse", -32.232, -64.443,
     "Wikipedia: Embalse Nuclear Power Station — 3.1km fix"),
    ("Rooppur", 24.066667, 89.047222,
     "Wikipedia: Rooppur NPP — 1.2km fix, WD+OSM agree"),
    ("Fuqing", 25.445833, 119.447222,
     "Wikipedia: Fuqing NPP — 811m fix"),
    ("Berkeley", 51.6925, -2.4936,
     "Wikipedia: Berkeley NPS — 449m fix"),
]

# Multi-site fixes: different coordinates per sub-plant
MULTISITE_FIXES = [
    # Kursk: Kursk 1 (RBMK) vs Kursk 2 (VVER-TOI, separate site ~2.6km away)
    {"plant": "Kursk 2", "lat": 51.688333, "lon": 35.573333,
     "note": "Wikipedia: Kursk II (VVER-TOI) — separate site from Kursk I"},

    # Leningrad: Leningrad 1 (RBMK) vs Leningrad 2 (VVER-1200, ~2.5km apart)
    {"plant": "Leningrad 1", "lat": 59.852500, "lon": 29.048611,
     "note": "Wikipedia: Leningrad I (RBMK)"},
    {"plant": "Leningrad 2", "lat": 59.831111, "lon": 29.059722,
     "note": "Wikipedia: Leningrad II (VVER-1200) — separate site ~2.5km south"},

    # Novovoronezh: Nov I vs Nov II (~1.4km apart)
    {"plant": "Novovoronezh 1", "lat": 51.275000, "lon": 39.200000,
     "note": "Wikipedia: Novovoronezh I"},
    {"plant": "Novovoronezh 2", "lat": 51.264990, "lon": 39.211450,
     "note": "Wikipedia: Novovoronezh II — separate site ~1.4km south"},
]


def main():
    mode = "preview"
    if "--apply" in sys.argv:
        mode = "apply"

    conn = sqlite3.connect(DB_PATH)

    print("=" * 80)
    print("FINAL COORDINATE FIXES")
    print("=" * 80)

    total_reactors = 0

    # Standard fixes
    for plant, lat, lon, note in FIXES:
        rows = conn.execute(
            "SELECT id, latitude, longitude FROM reactors WHERE plant_name = ?",
            (plant,)).fetchall()
        if rows:
            old = f"({rows[0][1]}, {rows[0][2]})"
            print(f"\n  {plant} ({len(rows)} reactors): {old} -> ({lat}, {lon})")
            print(f"    {note}")
            total_reactors += len(rows)
            if mode == "apply":
                conn.execute(
                    "UPDATE reactors SET latitude = ?, longitude = ? WHERE plant_name = ?",
                    (lat, lon, plant))
        else:
            print(f"\n  {plant}: NOT FOUND")

    # Multi-site fixes
    print(f"\n{'=' * 80}")
    print("MULTI-SITE FIXES")
    print(f"{'=' * 80}")

    for fix in MULTISITE_FIXES:
        rows = conn.execute(
            "SELECT id, latitude, longitude FROM reactors WHERE plant_name = ?",
            (fix["plant"],)).fetchall()
        if rows:
            old = f"({rows[0][1]}, {rows[0][2]})"
            print(f"\n  {fix['plant']} ({len(rows)} reactors): {old} -> ({fix['lat']}, {fix['lon']})")
            print(f"    {fix['note']}")
            total_reactors += len(rows)
            if mode == "apply":
                conn.execute(
                    "UPDATE reactors SET latitude = ?, longitude = ? WHERE plant_name = ?",
                    (fix["lat"], fix["lon"], fix["plant"]))
        else:
            print(f"\n  {fix['plant']}: NOT FOUND")

    if mode == "apply":
        conn.commit()
        print(f"\n{'=' * 80}")
        print(f"APPLIED: {total_reactors} reactor records updated")
        print(f"{'=' * 80}")
    else:
        print(f"\n{'=' * 80}")
        print(f"DRY RUN: {total_reactors} reactors would be updated. Use --apply to execute.")
        print(f"{'=' * 80}")

    conn.close()


if __name__ == "__main__":
    main()
