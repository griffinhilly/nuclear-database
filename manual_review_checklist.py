#!/usr/bin/env python3
"""
Generate a manual review checklist for plants that need human verification.
Outputs a formatted checklist with Wikipedia links for easy spot-checking.
"""

import sqlite3
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"
WD_RESULTS = Path(__file__).parent / "wikidata_verification.json"


def main():
    with open(WD_RESULTS, encoding="utf-8") as f:
        data = json.load(f)

    # Get manual review + medium-confidence items
    manual_review = [c for c in data["corrections"] if c["verdict"] == "MANUAL_REVIEW"]
    likely_wrong = [c for c in data["corrections"]
                    if c["verdict"] in ("LIKELY_WRONG",)
                    and not c.get("osm_agrees", False)]

    # Sort by distance (biggest first = most likely wrong)
    all_review = manual_review + likely_wrong
    all_review.sort(key=lambda x: -x["wd_dist_m"])

    # Also get unmatched plants
    unmatched = data.get("unmatched", [])

    # Generate checklist
    checklist = []
    for i, c in enumerate(all_review, 1):
        plant = c["plant"]
        country = c["country"]
        db_lat = c["db_lat"]
        db_lon = c["db_lon"]
        wd_lat = c["wd_lat"]
        wd_lon = c["wd_lon"]
        dist = c["wd_dist_m"]

        # Build Google Maps comparison links
        gm_db = f"https://www.google.com/maps/@{db_lat},{db_lon},15z"
        gm_wd = f"https://www.google.com/maps/@{wd_lat},{wd_lon},15z"
        wiki_url = c.get("wd_wiki_url", "")

        osm_info = ""
        if "osm_lat" in c:
            osm_info = f"OSM: ({c['osm_lat']:.4f}, {c['osm_lon']:.4f}) — {c['osm_dist_m']:.0f}m from DB"

        checklist.append({
            "num": i,
            "plant": plant,
            "country": country,
            "verdict": c["verdict"],
            "db_coords": f"({db_lat:.4f}, {db_lon:.4f})",
            "wd_coords": f"({wd_lat:.4f}, {wd_lon:.4f})",
            "distance": dist,
            "gm_db_link": gm_db,
            "gm_wd_link": gm_wd,
            "wiki_url": wiki_url,
            "osm_info": osm_info,
            "reactor_ids": c["db_reactor_ids"],
        })

    # Print formatted checklist
    print("=" * 80)
    print(f"MANUAL REVIEW CHECKLIST — {len(checklist)} plants to verify")
    print("=" * 80)
    print()
    print("Instructions:")
    print("  1. Open the Wikipedia link to find the correct coordinates")
    print("  2. Open the Google Maps DB link to see where our pin currently is")
    print("  3. If wrong, note the correct lat/lon from Wikipedia or Google Maps")
    print("  4. Mark as CORRECT, FIX (with new coords), or SKIP")
    print()

    for item in checklist:
        dist_str = f"{item['distance']:.0f}m" if item["distance"] < 1000 else f"{item['distance']/1000:.1f}km"
        print(f"--- [{item['num']}/{len(checklist)}] {item['plant']} ({item['country']}) — {dist_str} off ---")
        print(f"  Verdict:   {item['verdict']}")
        print(f"  DB coords: {item['db_coords']}")
        print(f"  WD coords: {item['wd_coords']}")
        if item["osm_info"]:
            print(f"  {item['osm_info']}")
        print(f"  Reactor IDs: {item['reactor_ids']}")
        if item["wiki_url"]:
            print(f"  Wikipedia: {item['wiki_url']}")
        print(f"  GM (our pin):  {item['gm_db_link']}")
        print(f"  GM (wikidata): {item['gm_wd_link']}")
        print(f"  Status: [ ] CORRECT  [ ] FIX: ___.____  ___.____  [ ] SKIP")
        print()

    if unmatched:
        print(f"\n{'=' * 80}")
        print(f"UNMATCHED PLANTS — {len(unmatched)} (no Wikidata match)")
        print("=" * 80)
        print("These plants had no Wikidata match. Check coordinates manually.")
        print()
        for i, u in enumerate(unmatched, 1):
            lat = u["lat"]
            lon = u["lon"]
            gm = f"https://www.google.com/maps/@{lat},{lon},15z"
            print(f"  [{i}] {u['plant_name']} ({u['country']}) — ({lat:.4f}, {lon:.4f})")
            print(f"      GM: {gm}")
            print()

    # Write as JSON too for programmatic use
    out = {
        "review_items": checklist,
        "unmatched": unmatched,
    }
    out_path = Path(__file__).parent / "manual_review_checklist.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nJSON checklist written to: {out_path}")


if __name__ == "__main__":
    main()
