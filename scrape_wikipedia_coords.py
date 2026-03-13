#!/usr/bin/env python3
"""
Fetch actual Wikipedia article coordinates for all nuclear plants.

Strategy:
1. Query Wikidata SPARQL for nuclear plants with Wikipedia sitelinks + P625 coords
2. Match to our DB plant names using label matching + proximity
3. Fetch coordinates from Wikipedia articles via MediaWiki API (prop=coordinates)
4. Compare Wikipedia article coords to DB, report/fix discrepancies

Wikipedia article coords (from GeoData) are the gold standard — they power
the "External maps" link on each article and consistently point to the
actual reactor building.
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
OUT_PATH = Path(__file__).parent / "wikipedia_coords.json"

UA = "NuclearDatabaseBot/1.0 (coordinate verification)"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p = math.pi / 180
    a = (0.5 - math.cos((lat2 - lat1) * p) / 2 +
         math.cos(lat1 * p) * math.cos(lat2 * p) *
         (1 - math.cos((lon2 - lon1) * p)) / 2)
    return 2 * R * math.asin(math.sqrt(a))


def fetch_json(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                wait = 5 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise


def sparql_query(query):
    url = "https://query.wikidata.org/sparql"
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    return fetch_json(f"{url}?{params}")


def get_wikidata_with_wikipedia():
    """Get nuclear plants from Wikidata with Wikipedia titles AND WD coordinates."""
    query = """
    SELECT ?item ?itemLabel ?article ?coord WHERE {
      {?item wdt:P31/wdt:P279* wd:Q134447.}
      UNION
      {?item wdt:P31/wdt:P279* wd:Q11963.}
      ?item wdt:P625 ?coord .
      ?article schema:about ?item ;
               schema:isPartOf <https://en.wikipedia.org/> .
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """
    data = sparql_query(query)
    results = []
    seen = set()
    for row in data["results"]["bindings"]:
        qid = row["item"]["value"].split("/")[-1]
        if qid in seen:
            continue
        seen.add(qid)

        article_url = row["article"]["value"]
        title = urllib.parse.unquote(
            article_url.replace("https://en.wikipedia.org/wiki/", ""))

        # Parse WD coordinate
        coord_str = row["coord"]["value"]  # "Point(lon lat)"
        parts = coord_str.replace("Point(", "").replace(")", "").split()
        wd_lon, wd_lat = float(parts[0]), float(parts[1])

        results.append({
            "qid": qid,
            "label": row["itemLabel"]["value"],
            "wiki_title": title,
            "wd_lat": wd_lat,
            "wd_lon": wd_lon,
        })
    return results


def get_wiki_coords(titles):
    """Fetch coordinates from Wikipedia articles, one small batch at a time."""
    coords = {}
    batch_size = 10  # Small batches to avoid URL length issues

    for i in range(0, len(titles), batch_size):
        batch = titles[i:i + batch_size]
        titles_str = "|".join(t.replace(" ", "_") for t in batch)
        params = urllib.parse.urlencode({
            "action": "query",
            "titles": titles_str,
            "prop": "coordinates",
            "colimit": "max",
            "redirects": "1",
            "format": "json",
        })
        url = f"https://en.wikipedia.org/w/api.php?{params}"

        try:
            data = fetch_json(url)
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                title = page.get("title", "")
                if "coordinates" in page and page["coordinates"]:
                    c = page["coordinates"][0]
                    coords[title] = (c["lat"], c["lon"])
        except Exception as e:
            print(f"  Error fetching batch {i}: {e}")

        if (i + batch_size) % 50 == 0 or i + batch_size >= len(titles):
            print(f"  Fetched {min(i + batch_size, len(titles))}/{len(titles)} "
                  f"({len(coords)} with coords so far)")
        time.sleep(2)

    return coords


def normalize(name):
    """Normalize plant name for matching."""
    import re
    name = name.lower().strip()
    for suffix in ["nuclear power plant", "nuclear power station",
                   "nuclear generating station", "nuclear station",
                   "power station", "power plant", "npp", "nps",
                   "atomic power station", "atomic energy station"]:
        name = name.replace(suffix, "")
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"[^a-z0-9]", " ", name)
    return re.sub(r"\s+", " ", name).strip()


def match_plants(db_plants, wd_articles):
    """Match DB plants to Wikidata articles using name + proximity."""
    matches = {}
    unmatched = []

    # Index by normalized label and title
    by_norm = {}
    for art in wd_articles:
        for field in [art["label"], art["wiki_title"].replace("_", " ")]:
            norm = normalize(field)
            if norm not in by_norm:
                by_norm[norm] = []
            by_norm[norm].append(art)

    for plant_name, info in db_plants.items():
        db_norm = normalize(plant_name)
        db_lat, db_lon = info["lat"], info["lon"]

        # Exact normalized match
        if db_norm in by_norm:
            # If multiple, pick closest
            candidates = by_norm[db_norm]
            best = min(candidates,
                       key=lambda a: haversine(db_lat, db_lon, a["wd_lat"], a["wd_lon"]))
            matches[plant_name] = best
            continue

        # Fuzzy match with proximity tiebreaker
        best_score = 0
        best_art = None
        for art in wd_articles:
            for field in [art["label"], art["wiki_title"].replace("_", " ")]:
                score = SequenceMatcher(None, db_norm, normalize(field)).ratio()
                if score > best_score:
                    best_score = score
                    best_art = art

        if best_art and best_score >= 0.65:
            # Sanity check: reject if >200km away (bad match)
            dist = haversine(db_lat, db_lon, best_art["wd_lat"], best_art["wd_lon"])
            if dist < 200000:
                matches[plant_name] = best_art
                continue

        unmatched.append(plant_name)

    return matches, unmatched


def search_wikipedia(plant_name):
    """Search Wikipedia for a plant and return the first result's coords."""
    search_terms = [
        f"{plant_name} nuclear power plant",
        f"{plant_name} nuclear",
        plant_name,
    ]
    for term in search_terms:
        params = urllib.parse.urlencode({
            "action": "query",
            "list": "search",
            "srsearch": term,
            "srlimit": "3",
            "format": "json",
        })
        url = f"https://en.wikipedia.org/w/api.php?{params}"
        try:
            data = fetch_json(url)
            results = data.get("query", {}).get("search", [])
            if results:
                titles = [r["title"] for r in results]
                coords = get_wiki_coords(titles)
                if coords:
                    title = list(coords.keys())[0]
                    return title, coords[title]
        except Exception:
            pass
        time.sleep(2)
    return None, None


def main():
    mode = "preview"
    if "--apply" in sys.argv:
        mode = "apply"

    conn = sqlite3.connect(DB_PATH)

    # Get all distinct plant names
    db_plants = {}
    rows = conn.execute("""
        SELECT plant_name, latitude, longitude, COUNT(*) as units
        FROM reactors GROUP BY plant_name
    """).fetchall()
    for r in rows:
        db_plants[r[0]] = {"lat": r[1], "lon": r[2], "units": r[3]}

    print(f"DB has {len(db_plants)} distinct plant names\n")

    # Step 1: Wikidata SPARQL
    print("Fetching Wikidata articles with Wikipedia sitelinks + coords...")
    wd_articles = get_wikidata_with_wikipedia()
    print(f"  Found {len(wd_articles)} articles\n")

    # Step 2: Match
    print("Matching to DB plant names...")
    matches, unmatched = match_plants(db_plants, wd_articles)
    print(f"  Matched: {len(matches)}")
    print(f"  Unmatched: {len(unmatched)}")

    # Step 3: Search Wikipedia for unmatched plants
    if unmatched:
        print(f"\nSearching Wikipedia for {len(unmatched)} unmatched plants...")
        still_unmatched = []
        search_matches = {}
        for plant in sorted(unmatched):
            title, coord = search_wikipedia(plant)
            if coord:
                db = db_plants[plant]
                dist = haversine(db["lat"], db["lon"], coord[0], coord[1])
                if dist < 200000:  # Sanity: within 200km
                    search_matches[plant] = {
                        "wiki_title": title,
                        "wiki_lat": coord[0],
                        "wiki_lon": coord[1],
                    }
                    print(f"  Found: {plant} -> {title}")
                else:
                    still_unmatched.append(plant)
                    print(f"  Bad match: {plant} -> {title} ({dist/1000:.0f}km away)")
            else:
                still_unmatched.append(plant)
                print(f"  Not found: {plant}")
        unmatched = still_unmatched
    else:
        search_matches = {}

    # Step 4: Fetch Wikipedia article coordinates for all matched plants
    all_titles = list(set(m["wiki_title"] for m in matches.values()))
    print(f"\nFetching Wikipedia coordinates for {len(all_titles)} articles...")
    wiki_coords = get_wiki_coords(all_titles)
    print(f"  Got coords for {len(wiki_coords)} / {len(all_titles)} articles")

    no_coords_titles = [t for t in all_titles if t not in wiki_coords]
    if no_coords_titles:
        print(f"  {len(no_coords_titles)} articles have no GeoData coordinates")

    # Step 5: Compare
    print(f"\n{'=' * 80}")
    print("COMPARISON: DB vs Wikipedia article coordinates")
    print(f"{'=' * 80}")

    updates = []
    correct = 0
    no_wiki = 0
    plants_with_wiki_coords = {}

    for plant_name, art in matches.items():
        wiki_title = art["wiki_title"]
        # Try both with and without underscores
        coord = wiki_coords.get(wiki_title) or wiki_coords.get(
            wiki_title.replace("_", " "))

        if not coord:
            no_wiki += 1
            continue

        db = db_plants[plant_name]
        dist = haversine(db["lat"], db["lon"], coord[0], coord[1])
        plants_with_wiki_coords[plant_name] = {
            "wiki_title": wiki_title,
            "wiki_lat": coord[0], "wiki_lon": coord[1],
            "db_lat": db["lat"], "db_lon": db["lon"],
            "dist": dist,
        }

        if dist <= 50:
            correct += 1
        else:
            updates.append({
                "plant": plant_name,
                "units": db["units"],
                "db_lat": db["lat"], "db_lon": db["lon"],
                "wiki_lat": coord[0], "wiki_lon": coord[1],
                "wiki_title": wiki_title,
                "dist": dist,
            })

    # Add search matches
    for plant_name, sm in search_matches.items():
        db = db_plants[plant_name]
        dist = haversine(db["lat"], db["lon"], sm["wiki_lat"], sm["wiki_lon"])
        plants_with_wiki_coords[plant_name] = {
            "wiki_title": sm["wiki_title"],
            "wiki_lat": sm["wiki_lat"], "wiki_lon": sm["wiki_lon"],
            "db_lat": db["lat"], "db_lon": db["lon"],
            "dist": dist,
        }
        if dist > 50:
            updates.append({
                "plant": plant_name,
                "units": db["units"],
                "db_lat": db["lat"], "db_lon": db["lon"],
                "wiki_lat": sm["wiki_lat"], "wiki_lon": sm["wiki_lon"],
                "wiki_title": sm["wiki_title"],
                "dist": dist,
            })
        else:
            correct += 1

    updates.sort(key=lambda x: -x["dist"])

    print(f"\n  Already correct (<50m):      {correct}")
    print(f"  Need updating (>50m):        {len(updates)}")
    print(f"  No Wikipedia GeoData coords: {no_wiki}")
    print(f"  Not matched at all:          {len(unmatched)}")
    print(f"  Total with Wiki coords:      {len(plants_with_wiki_coords)}")

    if updates:
        total_reactors = sum(u["units"] for u in updates)
        print(f"\n  Updates: {len(updates)} plants ({total_reactors} reactors)")
        print(f"\n  {'Plant':<35} {'Units':>5} {'Dist':>8}  Wiki article")
        print("  " + "-" * 90)
        for u in updates:
            d = f"{u['dist']:.0f}m" if u["dist"] < 1000 else f"{u['dist']/1000:.1f}km"
            title_short = u["wiki_title"][:45]
            print(f"  {u['plant']:<35} {u['units']:>5} {d:>8}  {title_short}")

    if unmatched:
        print(f"\n  Unmatched plants ({len(unmatched)}):")
        for p in sorted(unmatched):
            db = db_plants[p]
            print(f"    {p} ({db['units']} units) @ ({db['lat']}, {db['lon']})")

    # Save results
    result = {
        "summary": {
            "total_plants": len(db_plants),
            "matched_with_coords": len(plants_with_wiki_coords),
            "already_correct": correct,
            "need_updating": len(updates),
            "no_wiki_coords": no_wiki,
            "unmatched": len(unmatched),
        },
        "updates": updates,
        "unmatched": unmatched,
        "plants_with_coords": {k: v for k, v in
                               sorted(plants_with_wiki_coords.items())},
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {OUT_PATH}")

    # Apply
    if mode == "apply" and updates:
        print(f"\n{'=' * 80}")
        print("APPLYING WIKIPEDIA COORDINATES")
        print(f"{'=' * 80}")
        total = 0
        for u in updates:
            conn.execute(
                "UPDATE reactors SET latitude = ?, longitude = ? "
                "WHERE plant_name = ?",
                (u["wiki_lat"], u["wiki_lon"], u["plant"]))
            total += u["units"]
            d = f"{u['dist']:.0f}m" if u["dist"] < 1000 else f"{u['dist']/1000:.1f}km"
            print(f"  {u['plant']} ({u['units']}): [{d}] {u['wiki_title']}")
        conn.commit()
        print(f"\nAPPLIED: {len(updates)} plants, {total} reactors")

    conn.close()


if __name__ == "__main__":
    main()
