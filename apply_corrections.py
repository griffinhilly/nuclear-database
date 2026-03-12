#!/usr/bin/env python3
"""
Apply verified coordinate and name corrections to the nuclear database.

Run modes:
  --preview   Show what would change (default)
  --apply     Actually apply the changes
"""

import sqlite3
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"
WD_RESULTS = Path(__file__).parent / "wikidata_verification.json"

# ── NAME CORRECTIONS ────────────────────────────────────────────────────────
# Each entry: (old_name, new_name, reason)
NAME_CORRECTIONS = [
    # User-requested
    ("Chasnupp", "Chashma", "Official IAEA name; user-requested"),

    # Misspelling
    ("Neideraichbach", "Niederaichbach", "Misspelling — transposed 'ei'→'ie'"),
    ("Fukushima-Daichi", "Fukushima-Daiichi", "Misspelling — missing 'i'"),

    # German umlauts (ASCII approximation → proper Unicode)
    ("AVR Juelich", "AVR Jülich", "German umlaut correction"),
    ("HDR Grosswelzheim", "HDR Großwelzheim", "German umlaut/eszett correction"),
    ("Kruemmel", "Krümmel", "German umlaut correction"),
    ("Muelheim-Kaerlich", "Mülheim-Kärlich", "German umlaut correction"),

    # Swiss German umlauts
    ("Goesgen", "Gösgen", "German umlaut correction"),
    ("Muehleberg", "Mühleberg", "German umlaut correction"),

    # Ukrainian transliteration (Russian→Ukrainian, IAEA standard post-2022)
    ("Zaporozhye", "Zaporizhzhia", "Ukrainian transliteration per IAEA"),
    ("Rovno", "Rivne", "Ukrainian transliteration per IAEA"),
    ("Khmelnitski", "Khmelnytskyi", "Ukrainian transliteration per IAEA"),

    # Official names
    ("Kanupp", "Karachi", "Official IAEA name: Karachi Nuclear Power Plant"),

    # Romanization fixes
    ("Xudapu", "Xudabao", "Correct Chinese romanization per Wikidata/IAEA"),

    # Diacritics
    ("Krsko", "Krško", "Slovenian diacritics"),
    ("Cernavoda", "Cernavodă", "Romanian diacritics"),
    ("Barseback", "Barsebäck", "Swedish diacritics"),
    ("Santa Maria de Garona", "Santa María de Garoña", "Spanish diacritics"),
    ("Agesta", "Ågesta", "Swedish diacritics"),
]


def get_coordinate_corrections():
    """Load high-confidence coordinate corrections from Wikidata verification."""
    if not WD_RESULTS.exists():
        print("WARNING: wikidata_verification.json not found, skipping coordinate corrections")
        return []

    with open(WD_RESULTS, encoding="utf-8") as f:
        data = json.load(f)

    corrections = []
    for c in data.get("auto_fix", []):
        if "suggested_lat" not in c:
            continue
        corrections.append({
            "plant": c["plant"],
            "country": c["country"],
            "reactor_ids": c["db_reactor_ids"],
            "old_lat": c["db_lat"],
            "old_lon": c["db_lon"],
            "new_lat": c["suggested_lat"],
            "new_lon": c["suggested_lon"],
            "distance_m": c["wd_dist_m"],
            "confidence": c["confidence"],
            "verdict": c["verdict"],
            "osm_agrees": c.get("osm_wd_dist_m", 99999) < 500,
        })

    return corrections


def preview_name_corrections(conn):
    """Show what name changes would be applied."""
    print(f"\n{'=' * 70}")
    print("NAME CORRECTIONS PREVIEW")
    print(f"{'=' * 70}")

    total_reactors = 0
    applicable = []

    for old_name, new_name, reason in NAME_CORRECTIONS:
        rows = conn.execute(
            "SELECT id, plant_name, unit_number FROM reactors WHERE plant_name = ?",
            (old_name,)
        ).fetchall()

        if rows:
            applicable.append((old_name, new_name, reason, len(rows)))
            total_reactors += len(rows)
            print(f"\n  {old_name} → {new_name}")
            print(f"    Reason: {reason}")
            print(f"    Affects {len(rows)} reactor(s): {', '.join(f'#{r[0]}' for r in rows)}")
        else:
            print(f"\n  {old_name} → (NOT FOUND in DB, skipping)")

    print(f"\n  TOTAL: {len(applicable)} name changes affecting {total_reactors} reactor records")
    return applicable


def preview_coordinate_corrections(corrections):
    """Show what coordinate changes would be applied."""
    print(f"\n{'=' * 70}")
    print("COORDINATE CORRECTIONS PREVIEW")
    print(f"{'=' * 70}")

    # Split by confidence
    high = [c for c in corrections if c["osm_agrees"]]
    medium = [c for c in corrections if not c["osm_agrees"]]

    if high:
        print(f"\n--- HIGH CONFIDENCE (OSM + Wikidata agree): {len(high)} plants ---")
        print(f"{'Plant':<30} {'Country':<15} {'Dist':>8} {'Old Lat':>10} {'Old Lon':>10} → {'New Lat':>10} {'New Lon':>10}")
        print("-" * 105)
        for c in sorted(high, key=lambda x: -x["distance_m"]):
            dist_str = f"{c['distance_m']:.0f}m" if c["distance_m"] < 1000 else f"{c['distance_m']/1000:.1f}km"
            print(f"{c['plant']:<30} {c['country']:<15} {dist_str:>8} {c['old_lat']:>10.4f} {c['old_lon']:>10.4f} → {c['new_lat']:>10.4f} {c['new_lon']:>10.4f}")

    if medium:
        print(f"\n--- MEDIUM CONFIDENCE (Wikidata only, no OSM): {len(medium)} plants ---")
        print(f"{'Plant':<30} {'Country':<15} {'Dist':>8} {'Old Lat':>10} {'Old Lon':>10} → {'New Lat':>10} {'New Lon':>10}")
        print("-" * 105)
        for c in sorted(medium, key=lambda x: -x["distance_m"]):
            dist_str = f"{c['distance_m']:.0f}m" if c["distance_m"] < 1000 else f"{c['distance_m']/1000:.1f}km"
            print(f"{c['plant']:<30} {c['country']:<15} {dist_str:>8} {c['old_lat']:>10.4f} {c['old_lon']:>10.4f} → {c['new_lat']:>10.4f} {c['new_lon']:>10.4f}")

    total = len(high) + len(medium)
    total_reactors = sum(len(c["reactor_ids"].split(",")) for c in corrections)
    print(f"\n  TOTAL: {total} coordinate corrections affecting {total_reactors} reactor records")
    return corrections


def apply_name_corrections(conn, applicable):
    """Apply name corrections."""
    total = 0
    for old_name, new_name, reason, count in applicable:
        conn.execute(
            "UPDATE reactors SET plant_name = ? WHERE plant_name = ?",
            (new_name, old_name)
        )
        total += count
        print(f"  ✓ {old_name} → {new_name} ({count} reactors)")
    return total


def apply_coordinate_corrections(conn, corrections):
    """Apply coordinate corrections."""
    total = 0
    for c in corrections:
        reactor_ids = [int(x) for x in c["reactor_ids"].split(",")]
        for rid in reactor_ids:
            conn.execute(
                "UPDATE reactors SET latitude = ?, longitude = ? WHERE id = ?",
                (c["new_lat"], c["new_lon"], rid)
            )
            total += 1
        tag = "HIGH" if c["osm_agrees"] else "MED"
        dist_str = f"{c['distance_m']:.0f}m" if c["distance_m"] < 1000 else f"{c['distance_m']/1000:.1f}km"
        print(f"  ✓ [{tag}] {c['plant']} ({c['country']}) — moved {dist_str} ({len(reactor_ids)} reactors)")
    return total


def main():
    mode = "preview"
    if "--apply" in sys.argv:
        mode = "apply"

    high_only = "--high-only" in sys.argv

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Preview both
    name_applicable = preview_name_corrections(conn)
    coord_corrections = get_coordinate_corrections()
    if high_only:
        coord_corrections = [c for c in coord_corrections if c["osm_agrees"]]
        print(f"\n  (--high-only: filtered to {len(coord_corrections)} high-confidence corrections)")
    preview_coordinate_corrections(coord_corrections)

    if mode == "preview":
        print(f"\n{'=' * 70}")
        print("DRY RUN — no changes applied. Run with --apply to execute.")
        print(f"{'=' * 70}")
    elif mode == "apply":
        print(f"\n{'=' * 70}")
        print("APPLYING CORRECTIONS...")
        print(f"{'=' * 70}")

        print("\n--- Applying name corrections ---")
        name_count = apply_name_corrections(conn, name_applicable)

        print("\n--- Applying coordinate corrections ---")
        coord_count = apply_coordinate_corrections(conn, coord_corrections)

        conn.commit()
        print(f"\n{'=' * 70}")
        print(f"DONE: {name_count} name updates + {coord_count} coordinate updates applied")
        print(f"{'=' * 70}")

    conn.close()


if __name__ == "__main__":
    main()
