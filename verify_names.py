#!/usr/bin/env python3
"""
Verify reactor plant names against Wikidata and IAEA PRIS naming conventions.

Strategy:
1. Use Wikidata matches from coordinate verification to compare names
2. Query Wikidata for official/alternative names (aliases)
3. Flag name discrepancies, especially for German plants
4. Cross-reference with PRIS naming where pris_id exists
"""

import sqlite3
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"
WD_RESULTS = Path(__file__).parent / "wikidata_verification.json"


def get_db_plants_with_details():
    """Get all plants with their details from DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT r.plant_name, c.name as country, r.pris_id,
               COUNT(*) as unit_count,
               GROUP_CONCAT(DISTINCT r.unit_number) as units,
               GROUP_CONCAT(DISTINCT r.id) as reactor_ids
        FROM reactors r
        LEFT JOIN countries c ON r.country_id = c.id
        GROUP BY r.plant_name
        ORDER BY c.name, r.plant_name
    """).fetchall()
    plants = [dict(r) for r in rows]
    conn.close()
    return plants


def fetch_wikidata_names(qids):
    """Fetch labels and aliases for a batch of Wikidata QIDs."""
    # Wikidata API supports up to 50 entities per call
    all_names = {}
    batch_size = 50
    qid_list = list(qids)

    for i in range(0, len(qid_list), batch_size):
        batch = qid_list[i:i + batch_size]
        ids = "|".join(batch)
        url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={ids}&props=labels|aliases&languages=en&format=json"

        req = urllib.request.Request(url)
        req.add_header("User-Agent", "NuclearDatabaseVerify/1.0")

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        for qid, entity in data.get("entities", {}).items():
            label = entity.get("labels", {}).get("en", {}).get("value", "")
            aliases = [a["value"] for a in entity.get("aliases", {}).get("en", [])]
            all_names[qid] = {
                "label": label,
                "aliases": aliases,
            }

    return all_names


def normalize_name(name):
    """Normalize a plant name for comparison."""
    n = name.lower().strip()
    # Remove common suffixes
    for suffix in ["nuclear power plant", "nuclear power station",
                   "nuclear station", "nuclear plant", "power station",
                   "power plant", "npp", "nps", "atomic power station",
                   "atomic energy station", "nuclear generating station",
                   "kernkraftwerk", "atomkraftwerk", "akw", "kkw"]:
        n = n.replace(suffix, "").strip()
    # Remove parenthetical
    if "(" in n:
        n = n[:n.index("(")].strip()
    return n


def compare_names(db_name, wd_label, wd_aliases):
    """Compare DB name against Wikidata label and aliases. Return best match info."""
    db_norm = normalize_name(db_name)

    # Check exact match with label
    wd_norm = normalize_name(wd_label)
    if db_norm == wd_norm:
        return {"match": "exact", "score": 1.0, "best_wd_name": wd_label}

    # Check aliases
    for alias in wd_aliases:
        alias_norm = normalize_name(alias)
        if db_norm == alias_norm:
            return {"match": "alias_exact", "score": 1.0, "best_wd_name": alias}

    # Fuzzy match with label
    label_score = SequenceMatcher(None, db_norm, wd_norm).ratio()

    # Fuzzy match with aliases
    best_alias = ""
    best_alias_score = 0
    for alias in wd_aliases:
        alias_norm = normalize_name(alias)
        s = SequenceMatcher(None, db_norm, alias_norm).ratio()
        if s > best_alias_score:
            best_alias_score = s
            best_alias = alias

    if label_score >= best_alias_score:
        return {"match": "fuzzy", "score": label_score, "best_wd_name": wd_label}
    else:
        return {"match": "fuzzy_alias", "score": best_alias_score, "best_wd_name": best_alias}


def main():
    print("=" * 70)
    print("PLANT NAME VERIFICATION")
    print("=" * 70)

    # Load Wikidata verification results for QID mapping
    if not WD_RESULTS.exists():
        print("ERROR: Run verify_wikidata.py first to generate wikidata_verification.json")
        sys.exit(1)

    with open(WD_RESULTS, encoding="utf-8") as f:
        wd_data = json.load(f)

    # Build plant→QID mapping from corrections
    plant_qids = {}
    for c in wd_data["corrections"]:
        plant_qids[c["plant"]] = c["wd_qid"]

    print(f"\n--- Loading data ---")
    db_plants = get_db_plants_with_details()
    print(f"  {len(db_plants)} plants in DB")
    print(f"  {len(plant_qids)} have Wikidata QID matches")

    # Fetch detailed names from Wikidata
    print(f"\n--- Fetching Wikidata names and aliases ---")
    unique_qids = set(plant_qids.values())
    wd_names = fetch_wikidata_names(unique_qids)
    print(f"  Got names for {len(wd_names)} entities")

    # Compare names
    print(f"\n--- Comparing names ---")
    discrepancies = []
    good_matches = []

    for plant in db_plants:
        pname = plant["plant_name"]
        qid = plant_qids.get(pname)
        if not qid or qid not in wd_names:
            continue

        wd = wd_names[qid]
        result = compare_names(pname, wd["label"], wd["aliases"])

        entry = {
            "db_name": pname,
            "country": plant["country"],
            "reactor_ids": plant["reactor_ids"],
            "unit_count": plant["unit_count"],
            "wd_qid": qid,
            "wd_label": wd["label"],
            "wd_aliases": wd["aliases"],
            "match_type": result["match"],
            "match_score": result["score"],
            "best_wd_name": result["best_wd_name"],
        }

        if result["score"] < 0.85:
            discrepancies.append(entry)
        else:
            good_matches.append(entry)

    discrepancies.sort(key=lambda x: x["match_score"])

    print(f"\n{'=' * 70}")
    print("RESULTS")
    print(f"{'=' * 70}")
    print(f"  Good matches (score >= 0.85): {len(good_matches)}")
    print(f"  Discrepancies (score < 0.85): {len(discrepancies)}")

    # Show all discrepancies
    if discrepancies:
        print(f"\n--- NAME DISCREPANCIES ({len(discrepancies)}) ---")
        print(f"{'Our Name':<35} {'Country':<15} {'Score':>6} {'Wikidata Name':<40}")
        print("-" * 100)
        for d in discrepancies:
            print(f"{d['db_name']:<35} {d['country']:<15} {d['match_score']:>5.0%} {d['wd_label']:<40}")
            if d["wd_aliases"]:
                aliases_str = ", ".join(d["wd_aliases"][:5])
                print(f"{'':>35} {'':>15} {'':>6} aliases: {aliases_str}")

    # Show German plants specifically
    german = [d for d in discrepancies if d["country"] == "Germany"]
    if german:
        print(f"\n--- GERMAN PLANT DISCREPANCIES ({len(german)}) ---")
        for d in german:
            print(f"  DB: {d['db_name']}")
            print(f"  WD: {d['wd_label']}")
            if d["wd_aliases"]:
                print(f"  Aliases: {', '.join(d['wd_aliases'][:5])}")
            print()

    # Also show close-but-not-exact matches that might be misspellings
    near_misses = [g for g in good_matches if g["match_type"] == "fuzzy" and g["match_score"] < 0.95]
    near_misses.sort(key=lambda x: x["match_score"])
    if near_misses:
        print(f"\n--- NEAR MISSES (0.85-0.95 score, possible misspellings) ({len(near_misses)}) ---")
        print(f"{'Our Name':<35} {'Country':<15} {'Score':>6} {'Wikidata Name':<40}")
        print("-" * 100)
        for d in near_misses:
            print(f"{d['db_name']:<35} {d['country']:<15} {d['match_score']:>5.0%} {d['wd_label']:<40}")

    # Write results
    results = {
        "summary": {
            "total_compared": len(good_matches) + len(discrepancies),
            "good_matches": len(good_matches),
            "discrepancies": len(discrepancies),
            "near_misses": len(near_misses),
        },
        "discrepancies": discrepancies,
        "near_misses": near_misses,
        "good_matches": good_matches,
    }

    out_path = Path(__file__).parent / "name_verification.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nFull results written to: {out_path}")


if __name__ == "__main__":
    main()
