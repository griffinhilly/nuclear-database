#!/usr/bin/env python3
"""
Verify reactor coordinates against Wikidata.

Strategy:
1. Query Wikidata SPARQL for all nuclear power plants/stations with coordinates
2. Match to our DB plants by name similarity + country
3. Compare distances — flag anything >50m
4. Cross-reference with OSM results for consensus
5. Produce a prioritized correction list
"""

import sqlite3
import json
import math
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"
OSM_RESULTS = Path(__file__).parent / "coordinate_verification.json"


def haversine_m(lat1, lon1, lat2, lon2):
    """Distance in meters between two lat/lon points."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def fetch_wikidata_plants():
    """Fetch all nuclear power stations from Wikidata SPARQL."""
    # Query for nuclear power plants (Q134447) and their subclasses
    query = """
    SELECT ?item ?itemLabel ?coord ?countryLabel ?article WHERE {
      {
        ?item wdt:P31/wdt:P279* wd:Q134447 .
      } UNION {
        ?item wdt:P31/wdt:P279* wd:Q11963 .
      }
      ?item wdt:P625 ?coord .
      OPTIONAL { ?item wdt:P17 ?country . }
      OPTIONAL {
        ?article schema:about ?item ;
                 schema:isPartOf <https://en.wikipedia.org/> .
      }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fr,de,es,ja,ko,zh,ru" . }
    }
    """

    url = "https://query.wikidata.org/sparql"
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    full_url = f"{url}?{params}"

    print("Fetching nuclear plants from Wikidata SPARQL...")
    req = urllib.request.Request(full_url)
    req.add_header("User-Agent", "NuclearDatabaseVerify/1.0 (coordinate verification)")
    req.add_header("Accept", "application/sparql-results+json")

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    plants = []
    seen = set()  # Deduplicate by QID
    for binding in result.get("results", {}).get("bindings", []):
        qid = binding["item"]["value"].split("/")[-1]
        if qid in seen:
            continue
        seen.add(qid)

        coord = binding.get("coord", {}).get("value", "")
        if not coord:
            continue
        # Parse "Point(lon lat)" format
        try:
            inner = coord.replace("Point(", "").replace(")", "")
            lon_str, lat_str = inner.split()
            lat = float(lat_str)
            lon = float(lon_str)
        except (ValueError, IndexError):
            continue

        name = binding.get("itemLabel", {}).get("value", "")
        country = binding.get("countryLabel", {}).get("value", "")
        wiki_url = binding.get("article", {}).get("value", "")

        plants.append({
            "qid": qid,
            "name": name,
            "country": country,
            "lat": lat,
            "lon": lon,
            "wiki_url": wiki_url,
        })

    print(f"  Found {len(plants)} Wikidata nuclear plant entries")
    return plants


def get_db_plants():
    """Get all unique plant locations from our database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT r.plant_name, c.name as country,
               r.latitude, r.longitude,
               COUNT(*) as unit_count,
               GROUP_CONCAT(r.unit_number, ',') as units,
               GROUP_CONCAT(r.status, ',') as statuses,
               GROUP_CONCAT(r.id, ',') as reactor_ids
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        WHERE r.latitude IS NOT NULL AND r.longitude IS NOT NULL
        GROUP BY r.plant_name, ROUND(r.latitude, 2), ROUND(r.longitude, 2)
        ORDER BY c.name, r.plant_name
    """).fetchall()
    plants = [dict(r) for r in rows]
    conn.close()
    print(f"  {len(plants)} unique plant sites in our DB")
    return plants


def name_similarity(a, b):
    """Fuzzy name similarity score (0-1)."""
    a = a.lower().strip()
    b = b.lower().strip()
    # Strip common suffixes for better matching
    for suffix in ["nuclear power plant", "nuclear power station",
                   "nuclear station", "nuclear plant", "power station",
                   "power plant", "npp", "nps", "atomic power station",
                   "atomic energy station", "nuclear generating station"]:
        a = a.replace(suffix, "").strip()
        b = b.replace(suffix, "").strip()
    # Also strip parenthetical content
    if "(" in a:
        a = a[:a.index("(")].strip()
    if "(" in b:
        b = b[:b.index("(")].strip()
    return SequenceMatcher(None, a, b).ratio()


def match_plants(db_plants, wd_plants):
    """Match DB plants to Wikidata plants by name + proximity."""
    matches = []
    unmatched_db = []

    for db in db_plants:
        best_match = None
        best_score = -1

        for wd in wd_plants:
            dist = haversine_m(db["latitude"], db["longitude"],
                               wd["lat"], wd["lon"])

            # Two matching strategies:
            # 1. Very close proximity (<50km) + decent name match
            # 2. Good name match + same country + reasonable distance
            name_sim = name_similarity(db["plant_name"], wd["name"])

            score = 0
            if dist < 50000:  # Within 50km
                # Proximity-weighted score
                proximity_bonus = max(0, 1 - dist / 50000)
                score = name_sim * 0.6 + proximity_bonus * 0.4

                # Bonus for country match
                if db["country"] and wd["country"]:
                    if db["country"].lower() == wd["country"].lower():
                        score += 0.1

            if score > best_score:
                best_score = score
                best_match = wd
                best_dist = dist

        if best_score > 0.3 and best_match:
            matches.append({
                "db_plant": db["plant_name"],
                "db_country": db["country"],
                "db_lat": db["latitude"],
                "db_lon": db["longitude"],
                "db_units": db["units"],
                "db_reactor_ids": db["reactor_ids"],
                "wd_name": best_match["name"],
                "wd_country": best_match["country"],
                "wd_lat": best_match["lat"],
                "wd_lon": best_match["lon"],
                "wd_qid": best_match["qid"],
                "wd_wiki_url": best_match["wiki_url"],
                "distance_m": round(best_dist, 1),
                "match_score": round(best_score, 3),
            })
        else:
            unmatched_db.append({
                "plant_name": db["plant_name"],
                "country": db["country"],
                "lat": db["latitude"],
                "lon": db["longitude"],
                "units": db["units"],
            })

    return matches, unmatched_db


def load_osm_results():
    """Load previous OSM verification results for cross-reference."""
    if not OSM_RESULTS.exists():
        return {}
    with open(OSM_RESULTS, encoding="utf-8") as f:
        data = json.load(f)
    # Index OSM matches by plant name for quick lookup
    osm_by_plant = {}
    for m in data.get("all_matches", []):
        osm_by_plant[m["db_plant"]] = m
    return osm_by_plant


def cross_reference(wd_matches, osm_by_plant):
    """Cross-reference Wikidata and OSM results to build consensus."""
    corrections = []

    for m in wd_matches:
        plant = m["db_plant"]
        osm = osm_by_plant.get(plant)

        db_lat, db_lon = m["db_lat"], m["db_lon"]
        wd_lat, wd_lon = m["wd_lat"], m["wd_lon"]
        wd_dist = m["distance_m"]

        entry = {
            "plant": plant,
            "country": m["db_country"],
            "db_lat": db_lat,
            "db_lon": db_lon,
            "db_reactor_ids": m["db_reactor_ids"],
            "wd_lat": wd_lat,
            "wd_lon": wd_lon,
            "wd_dist_m": wd_dist,
            "wd_qid": m["wd_qid"],
            "wd_wiki_url": m["wd_wiki_url"],
        }

        if osm:
            osm_lat, osm_lon = osm["osm_lat"], osm["osm_lon"]
            osm_dist = osm["distance_m"]
            # Distance between OSM and Wikidata
            osm_wd_dist = haversine_m(osm_lat, osm_lon, wd_lat, wd_lon)

            entry["osm_lat"] = osm_lat
            entry["osm_lon"] = osm_lon
            entry["osm_dist_m"] = osm_dist
            entry["osm_wd_dist_m"] = round(osm_wd_dist, 1)

            # Consensus logic
            if wd_dist <= 50 and osm_dist <= 50:
                entry["verdict"] = "PASS"
                entry["confidence"] = "high"
            elif wd_dist <= 50:
                # DB close to Wikidata but not OSM — trust Wikidata
                entry["verdict"] = "PASS"
                entry["confidence"] = "medium"
            elif osm_wd_dist < 500:
                # OSM and Wikidata agree with each other but not DB
                entry["verdict"] = "CORRECT_TO_WD"
                entry["confidence"] = "high"
                entry["suggested_lat"] = wd_lat
                entry["suggested_lon"] = wd_lon
            elif osm_dist <= 50:
                # DB close to OSM but not Wikidata — probably DB is right
                entry["verdict"] = "PASS"
                entry["confidence"] = "medium"
            else:
                # All three disagree — needs manual review
                entry["verdict"] = "MANUAL_REVIEW"
                entry["confidence"] = "low"
        else:
            # No OSM data — rely on Wikidata alone
            if wd_dist <= 50:
                entry["verdict"] = "PASS"
                entry["confidence"] = "medium"
            elif wd_dist > 1000:
                entry["verdict"] = "LIKELY_WRONG"
                entry["confidence"] = "medium"
                entry["suggested_lat"] = wd_lat
                entry["suggested_lon"] = wd_lon
            else:
                entry["verdict"] = "MANUAL_REVIEW"
                entry["confidence"] = "low"

        corrections.append(entry)

    return corrections


def main():
    print("=" * 70)
    print("WIKIDATA COORDINATE VERIFICATION")
    print("=" * 70)

    # Step 1: Get data
    print("\n--- Loading data ---")
    db_plants = get_db_plants()
    wd_plants = fetch_wikidata_plants()

    # Step 2: Match
    print("\n--- Matching plants ---")
    matches, unmatched = match_plants(db_plants, wd_plants)
    print(f"  Matched: {len(matches)}")
    print(f"  Unmatched: {len(unmatched)}")

    # Step 3: Cross-reference with OSM
    print("\n--- Cross-referencing with OSM data ---")
    osm_by_plant = load_osm_results()
    print(f"  OSM data available for {len(osm_by_plant)} plants")
    corrections = cross_reference(matches, osm_by_plant)

    # Step 4: Summarize
    verdicts = {}
    for c in corrections:
        v = c["verdict"]
        verdicts[v] = verdicts.get(v, 0) + 1

    print(f"\n{'=' * 70}")
    print("RESULTS")
    print(f"{'=' * 70}")
    for v, count in sorted(verdicts.items()):
        print(f"  {v}: {count}")
    print(f"  Unmatched in Wikidata: {len(unmatched)}")

    # Step 5: Show high-confidence corrections
    auto_fix = [c for c in corrections
                if c["verdict"] in ("CORRECT_TO_WD", "LIKELY_WRONG")
                and c.get("confidence") in ("high", "medium")]
    auto_fix.sort(key=lambda x: -x["wd_dist_m"])

    if auto_fix:
        print(f"\n--- HIGH-CONFIDENCE CORRECTIONS ({len(auto_fix)} plants) ---")
        print(f"{'Plant':<30} {'Country':<15} {'DB→WD dist':>12} {'OSM agrees?':>12} {'Verdict':<15}")
        print("-" * 90)
        for c in auto_fix:
            dist_str = f"{c['wd_dist_m']:.0f}m" if c["wd_dist_m"] < 1000 else f"{c['wd_dist_m']/1000:.1f}km"
            osm_agrees = "yes" if c.get("osm_wd_dist_m", 99999) < 500 else "no OSM" if "osm_lat" not in c else "no"
            print(f"{c['plant']:<30} {c['country']:<15} {dist_str:>12} {osm_agrees:>12} {c['verdict']:<15}")

    # Step 6: Show manual review items
    manual = [c for c in corrections if c["verdict"] == "MANUAL_REVIEW"]
    manual.sort(key=lambda x: -x["wd_dist_m"])

    if manual:
        print(f"\n--- NEEDS MANUAL REVIEW ({len(manual)} plants) ---")
        print(f"{'Plant':<30} {'Country':<15} {'DB→WD':>10} {'DB→OSM':>10} {'OSM→WD':>10}")
        print("-" * 80)
        for c in manual[:30]:  # Show first 30
            wd_str = f"{c['wd_dist_m']:.0f}m" if c["wd_dist_m"] < 1000 else f"{c['wd_dist_m']/1000:.1f}km"
            osm_str = f"{c.get('osm_dist_m', 0):.0f}m" if c.get("osm_dist_m", 0) < 1000 else f"{c.get('osm_dist_m', 0)/1000:.1f}km" if "osm_dist_m" in c else "N/A"
            owd_str = f"{c.get('osm_wd_dist_m', 0):.0f}m" if c.get("osm_wd_dist_m", 0) < 1000 else f"{c.get('osm_wd_dist_m', 0)/1000:.1f}km" if "osm_wd_dist_m" in c else "N/A"
            print(f"{c['plant']:<30} {c['country']:<15} {wd_str:>10} {osm_str:>10} {owd_str:>10}")

    # Step 7: Show unmatched plants
    if unmatched:
        print(f"\n--- UNMATCHED IN WIKIDATA ({len(unmatched)} plants) ---")
        for u in unmatched[:20]:
            print(f"  {u['plant_name']:<30} {u['country']:<15} ({u['lat']:.4f}, {u['lon']:.4f})")
        if len(unmatched) > 20:
            print(f"  ... and {len(unmatched) - 20} more")

    # Step 8: Write full results
    results = {
        "summary": {
            "db_plants": len(db_plants),
            "wikidata_plants": len(wd_plants),
            "matched": len(matches),
            "unmatched": len(unmatched),
            "verdicts": verdicts,
        },
        "corrections": corrections,
        "auto_fix": auto_fix,
        "manual_review": manual,
        "unmatched": unmatched,
    }

    out_path = Path(__file__).parent / "wikidata_verification.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nFull results written to: {out_path}")


if __name__ == "__main__":
    main()
