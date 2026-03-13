#!/usr/bin/env python3
"""
Adopt Wikidata coordinates for all plants where we don't already have
manually-verified Wikipedia coordinates. Based on finding that Wikipedia/
Wikidata coordinates consistently point to the actual reactor building,
while our DB coords were sometimes offset.
"""

import sqlite3
import json
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DB_PATH = Path(__file__).parent / "nuclear_reactors.db"
WD_RESULTS = Path(__file__).parent / "wikidata_verification.json"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p = math.pi / 180
    a = (0.5 - math.cos((lat2 - lat1) * p) / 2 +
         math.cos(lat1 * p) * math.cos(lat2 * p) *
         (1 - math.cos((lon2 - lon1) * p)) / 2)
    return 2 * R * math.asin(math.sqrt(a))


# Plants already manually fixed to Wikipedia coordinates — DO NOT override
SKIP_PLANTS = {
    # fix_final_coords.py (Wikipedia-verified)
    "Lucens", "Niederaichbach", "Hallam", "Rolphton NPD", "Jose Cabrera",
    "Lacrosse", "Gösgen", "Kozloduy", "Pathfinder", "Chashma", "Würgassen",
    "El Dabaa", "AVR Jülich", "Chapelcross", "Saxton", "GE Vallecitos",
    "Gentilly", "Super-Phenix", "Fugen ATR", "Embalse", "Rooppur",
    "Fuqing", "Berkeley",
    # Multi-site fixes (Wikipedia-verified, separate sites)
    "Kursk 2", "Leningrad 1", "Leningrad 2",
    "Novovoronezh 1", "Novovoronezh 2",
    # fix_remaining_coords.py (user-verified Wikipedia)
    "Lungmen (Fourth)", "Piqua", "Elk River", "Brennilis",
    "Vak Kahl", "HDR Großwelzheim", "Lingen", "Stade",
    # fix_chinese_data.py (Wikipedia/WNA-verified)
    "Haiyang", "Shidao Bay", "Shidaowan", "Zhangzhou", "Jinqimen",
    "Taipingling", "Lianjiang", "San'ao", "Bailong",
}


def main():
    mode = "preview"
    if "--apply" in sys.argv:
        mode = "apply"

    with open(WD_RESULTS, encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)

    # Build corrections list
    updates = []
    skipped = []

    seen = set()
    for c in data["corrections"]:
        plant = c["plant"]
        if plant in seen:
            continue
        seen.add(plant)
        wd_lat = c["wd_lat"]
        wd_lon = c["wd_lon"]

        if plant in SKIP_PLANTS:
            row = conn.execute(
                "SELECT latitude, longitude FROM reactors WHERE plant_name = ? LIMIT 1",
                (plant,)).fetchone()
            if row:
                dist = haversine(row[0], row[1], wd_lat, wd_lon)
                if dist > 50:
                    skipped.append((plant, dist))
            continue

        row = conn.execute(
            "SELECT latitude, longitude FROM reactors WHERE plant_name = ? LIMIT 1",
            (plant,)).fetchone()
        if not row:
            continue

        db_lat, db_lon = row
        dist = haversine(db_lat, db_lon, wd_lat, wd_lon)
        if dist <= 50:
            continue

        count = conn.execute(
            "SELECT COUNT(*) FROM reactors WHERE plant_name = ?",
            (plant,)).fetchone()[0]
        updates.append({
            "plant": plant,
            "dist": dist,
            "db_lat": db_lat, "db_lon": db_lon,
            "wd_lat": wd_lat, "wd_lon": wd_lon,
            "count": count,
        })

    updates.sort(key=lambda x: -x["dist"])
    total_reactors = sum(u["count"] for u in updates)

    print("=" * 80)
    print("ADOPT WIKIDATA COORDINATES")
    print("=" * 80)
    print(f"\nUpdating {len(updates)} plants ({total_reactors} reactors)")
    print(f"Skipping {len(skipped)} plants (already have Wikipedia coords)\n")

    for u in updates:
        d = f"{u['dist']:.0f}m" if u["dist"] < 1000 else f"{u['dist']/1000:.1f}km"
        print(f"  {u['plant']} ({u['count']}): "
              f"({u['db_lat']}, {u['db_lon']}) -> ({u['wd_lat']}, {u['wd_lon']})  [{d}]")

    if skipped:
        print(f"\n--- Skipped (keeping Wikipedia fixes) ---")
        for plant, dist in sorted(skipped, key=lambda x: -x[1]):
            d = f"{dist:.0f}m" if dist < 1000 else f"{dist/1000:.1f}km"
            print(f"  {plant}: {d} from WD")

    if mode == "apply":
        for u in updates:
            conn.execute(
                "UPDATE reactors SET latitude = ?, longitude = ? WHERE plant_name = ?",
                (u["wd_lat"], u["wd_lon"], u["plant"]))
        conn.commit()
        print(f"\n{'=' * 80}")
        print(f"APPLIED: {len(updates)} plants, {total_reactors} reactors updated")
        print(f"{'=' * 80}")
    else:
        print(f"\n{'=' * 80}")
        print(f"DRY RUN: {total_reactors} reactors would be updated. Use --apply to execute.")
        print(f"{'=' * 80}")

    conn.close()


if __name__ == "__main__":
    main()
