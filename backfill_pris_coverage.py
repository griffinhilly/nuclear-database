#!/usr/bin/env python3
"""
Backfill PRIS Coverage: Discover PRIS IDs for all countries, match to DB
reactors, update pris_id column, and fetch generation data.

The PRIS website no longer exposes reactor IDs in direct links — it uses
ASP.NET postbacks.  This script simulates those postbacks (one per reactor)
to discover the current PRIS IDs, then matches them to the local SQLite DB
and optionally fetches generation history.

Usage:
    python3 backfill_pris_coverage.py --dry-run              # Discover + match, report only
    python3 backfill_pris_coverage.py --discover-only         # Discover + match + update pris_id, skip fetch
    python3 backfill_pris_coverage.py --fetch-mode all        # Full run
    python3 backfill_pris_coverage.py --fetch-mode new-only   # Fetch only for newly-matched reactors
"""

import argparse
import re
import sqlite3
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Import from existing scripts (read-only)
from pris_scraper import COUNTRIES
from fetch_missing_generation import (
    PRIS_TO_DB_OVERRIDES,
    parse_pris_key,
    build_reactor_lookup,
    fetch_reactor_generation,
    DB_PATH,
)

PRIS_COUNTRY_URL = (
    "https://pris.iaea.org/pris/CountryStatistics/"
    "CountryDetails.aspx?current={code}"
)

# ---------------------------------------------------------------------------
# Supplemental overrides for reactors in countries not previously covered.
# Format: 'PRIS_NAME': ('db_plant_name', 'db_unit_number')
# ---------------------------------------------------------------------------
SUPPLEMENTAL_OVERRIDES = {
    # India - PRIS uses abbreviated station names (KAPS, MAPS, NAPS, RAPS, TAPS)
    'KAPS-1': ('Kakrapar', '1'),
    'KAPS-2': ('Kakrapar', '2'),
    'MAPS-1': ('Madras', '1'),
    'MAPS-2': ('Madras', '2'),
    'NAPS-1': ('Narora', '1'),
    'NAPS-2': ('Narora', '2'),
    'RAPS-1': ('Rajasthan', '1'),
    'RAPS-2': ('Rajasthan', '2'),
    'RAPS-3': ('Rajasthan', '3'),
    'RAPS-4': ('Rajasthan', '4'),
    'RAPS-5': ('Rajasthan', '5'),
    'RAPS-6': ('Rajasthan', '6'),
    'TAPS-1': ('Tarapur', '1'),
    'TAPS-2': ('Tarapur', '2'),
    'TAPS-3': ('Tarapur', '3'),
    'TAPS-4': ('Tarapur', '4'),

    # Ukraine - PRIS uses different transliterations
    'RIVNE-1': ('Rovno', '1'),
    'RIVNE-2': ('Rovno', '2'),
    'RIVNE-3': ('Rovno', '3'),
    'RIVNE-4': ('Rovno', '4'),
    'KHMELNITSKI-1': ('Khmelnitski', '1'),
    'KHMELNITSKI-2': ('Khmelnitski', '2'),
    'KHMELNYTSKA-1': ('Khmelnitski', '1'),
    'KHMELNYTSKA-2': ('Khmelnitski', '2'),
    'KHMELNYTSKYY-1': ('Khmelnitski', '1'),
    'KHMELNYTSKYY-2': ('Khmelnitski', '2'),
    'ZAPORIZHZHE-1': ('Zaporozhye', '1'),
    'ZAPORIZHZHE-2': ('Zaporozhye', '2'),
    'ZAPORIZHZHE-3': ('Zaporozhye', '3'),
    'ZAPORIZHZHE-4': ('Zaporozhye', '4'),
    'ZAPORIZHZHE-5': ('Zaporozhye', '5'),
    'ZAPORIZHZHE-6': ('Zaporozhye', '6'),
    'ZAPORIZHZHYA-1': ('Zaporozhye', '1'),
    'ZAPORIZHZHYA-2': ('Zaporozhye', '2'),
    'ZAPORIZHZHYA-3': ('Zaporozhye', '3'),
    'ZAPORIZHZHYA-4': ('Zaporozhye', '4'),
    'ZAPORIZHZHYA-5': ('Zaporozhye', '5'),
    'ZAPORIZHZHYA-6': ('Zaporozhye', '6'),
    'SOUTH UKRAINE-1': ('South Ukraine', '1'),
    'SOUTH UKRAINE-2': ('South Ukraine', '2'),
    'SOUTH UKRAINE-3': ('South Ukraine', '3'),

    # France - reactors missing from original overrides
    'CHINON B-1': ('Chinon B', '1'),
    'CHINON B-2': ('Chinon B', '2'),
    'CHINON B-3': ('Chinon B', '3'),
    'CHINON B-4': ('Chinon B', '4'),
    'CHOOZ B-1': ('Chooz B', '1'),
    'CHOOZ B-2': ('Chooz B', '2'),
    'ST. LAURENT B-1': ('St. Laurent B', '1'),
    'ST. LAURENT B-2': ('St. Laurent B', '2'),
    'SAINT LAURENT B-1': ('St. Laurent B', '1'),
    'SAINT LAURENT B-2': ('St. Laurent B', '2'),

    # UK - PRIS uses "HARTLEPOOL A" instead of "HARTLEPOOL"
    'HARTLEPOOL A-1': ('Hartlepool', '1'),
    'HARTLEPOOL A-2': ('Hartlepool', '2'),

    # Russia - units not in original overrides
    'AKADEMIK LOMONOSOV-1': ('Akademik Lomonosov', '1'),
    'AKADEMIK LOMONOSOV-2': ('Akademik Lomonosov', '2'),
    'BILIBINO-2': ('Bilibino', '2'),
    'BILIBINO-3': ('Bilibino', '3'),
    'BILIBINO-4': ('Bilibino', '4'),

    # China - compound plant names (Qinshan 2, Qinshan 3, Ling Ao extra units)
    'QINSHAN 2-2': ('Qinshan 2', '2'),
    'QINSHAN 2-3': ('Qinshan 2', '3'),
    'QINSHAN 2-4': ('Qinshan 2', '4'),
    'QINSHAN 3-2': ('Qinshan 3', '2'),
    'LING AO-3': ('Ling Ao', '3'),
    'LING AO-4': ('Ling Ao', '4'),

    # Taiwan - DB has parenthetical names
    'KUOSHENG-2': ('Kuosheng (Second)', '2'),
    'MAANSHAN-1': ('Maanshan (Third)', '1'),
    'MAANSHAN-2': ('Maanshan (Third)', '2'),

    # USA - reactors with parenthetical names not in original overrides
    'HARRIS-1': ('Harris (Shearon Harris)', '1'),
    'SUMMER-1': ('Summer (V C Summer)', '1'),
    'PALISADES': ('Palisades', '1'),

    # Japan - potential space/no-space variations
    'HIGASHIDORI-1': ('Higashi Dori', '1'),
    'KASHIWAZAKI KARIWA-1': ('Kashiwazaki Kariwa', '1'),
    'KASHIWAZAKI KARIWA-2': ('Kashiwazaki Kariwa', '2'),
    'KASHIWAZAKI KARIWA-3': ('Kashiwazaki Kariwa', '3'),
    'KASHIWAZAKI KARIWA-4': ('Kashiwazaki Kariwa', '4'),
    'KASHIWAZAKI KARIWA-5': ('Kashiwazaki Kariwa', '5'),
    'KASHIWAZAKI KARIWA-6': ('Kashiwazaki Kariwa', '6'),
    'KASHIWAZAKI KARIWA-7': ('Kashiwazaki Kariwa', '7'),

    # Slovakia - Bohunice V2 naming
    'BOHUNICE V2-3': ('Bohunice', '3'),
    'BOHUNICE V2-4': ('Bohunice', '4'),

    # Pakistan - potential abbreviated names
    'CHASNUPP-1': ('Chasnupp', '1'),
    'CHASNUPP-2': ('Chasnupp', '2'),
    'CHASNUPP-3': ('Chasnupp', '3'),
    'CHASNUPP-4': ('Chasnupp', '4'),
    'KANUPP': ('Kanupp', '1'),
    'C-1': ('Chasnupp', '1'),
    'C-2': ('Chasnupp', '2'),
    'C-3': ('Chasnupp', '3'),
    'C-4': ('Chasnupp', '4'),
    'K-1': ('Kanupp', '1'),

    # Germany (may still be listed in PRIS even if recently shut down)
    'EMSLAND': ('Emsland', '1'),
    'ISAR-2': ('Isar', '2'),
    'NECKARWESTHEIM-2': ('Neckarwestheim', '2'),
}


# ---------------------------------------------------------------------------
# PRIS ID discovery via ASP.NET postbacks
# ---------------------------------------------------------------------------

def _get_country_page(session, country_code):
    """GET a PRIS country page; return (soup, url) or (None, url)."""
    url = PRIS_COUNTRY_URL.format(code=country_code)
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser'), url
    except Exception as e:
        print(f" error: {e}")
        return None, url


def _extract_reactor_rows(soup):
    """Extract reactor name, status, and postback target from a country page.

    Returns list of dicts: {'name', 'status', 'postback_target'}
    """
    rows = []
    links = soup.find_all(
        'a', href=re.compile(r'rptCountryReactors.*hypReactorName')
    )
    for link in links:
        name = link.text.strip()
        # Extract postback target from href
        m = re.search(r"__doPostBack\('([^']+)'", link['href'])
        target = m.group(1) if m else None

        # Get status from sibling cells
        tr = link.find_parent('tr')
        status = ''
        if tr:
            cells = tr.find_all('td')
            if len(cells) >= 3:
                status = cells[2].text.strip()

        rows.append({'name': name, 'status': status, 'postback_target': target})
    return rows


def _extract_form_fields(soup):
    """Extract ASP.NET hidden form fields needed for postback."""
    fields = {}
    for name in ('__VIEWSTATE', '__EVENTVALIDATION', '__VIEWSTATEGENERATOR'):
        tag = soup.find('input', {'name': name})
        if tag:
            fields[name] = tag['value']
    return fields


def _resolve_pris_id(session, page_url, form_fields, postback_target):
    """POST a simulated postback and read the PRIS ID from the redirect."""
    data = {
        **form_fields,
        '__EVENTTARGET': postback_target,
        '__EVENTARGUMENT': '',
    }
    try:
        resp = session.post(page_url, data=data, timeout=30,
                            allow_redirects=False)
        loc = resp.headers.get('Location', '')
        m = re.search(r'current=(\d+)', loc)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def discover_all_pris_ids(session, delay_country=1.0, delay_reactor=0.3,
                          operational_only=True):
    """Discover PRIS IDs for all reactors across all PRIS countries.

    Uses ASP.NET postbacks: one GET per country page, then one lightweight
    POST per reactor to resolve its PRIS ID from the 302 redirect.

    Returns dict: {PRIS_NAME_UPPER: {'pris_id': int, 'name': str,
                    'status': str, 'country': str}}
    """
    all_reactors = {}
    countries_sorted = sorted(COUNTRIES.items())

    for ci, (country_name, country_code) in enumerate(countries_sorted, 1):
        print(f"  [{ci}/{len(countries_sorted)}] {country_name} ({country_code})...",
              end='', flush=True)

        soup, page_url = _get_country_page(session, country_code)
        if soup is None:
            print(" page fetch failed")
            continue

        rows = _extract_reactor_rows(soup)
        form_fields = _extract_form_fields(soup)

        if not rows:
            print(" 0 reactors on page")
            time.sleep(delay_country)
            continue

        # Filter to operational only to reduce request count
        if operational_only:
            targets = [r for r in rows if r['status'] == 'Operational']
        else:
            targets = rows

        resolved = 0
        for r in targets:
            if r['postback_target'] is None:
                continue
            pris_id = _resolve_pris_id(session, page_url, form_fields,
                                       r['postback_target'])
            if pris_id is not None:
                key = r['name'].strip().upper()
                all_reactors[key] = {
                    'pris_id': pris_id,
                    'name': r['name'].strip(),
                    'status': r['status'],
                    'country': country_name,
                }
                resolved += 1
            time.sleep(delay_reactor)

        print(f" {len(rows)} listed, {len(targets)} operational, {resolved} resolved")
        time.sleep(delay_country)

    return all_reactors


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def get_coverage_stats(conn):
    """Get current generation data coverage stats."""
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM reactors WHERE status = 'Operational'"
    )
    total_operational = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM reactors WHERE status = 'Operational' "
        "AND pris_id IS NOT NULL"
    )
    with_pris = cursor.fetchone()[0]

    cursor.execute("""
        SELECT ga.year, COUNT(DISTINCT ga.reactor_id)
        FROM generation_annual ga
        JOIN reactors r ON ga.reactor_id = r.id
        WHERE r.status = 'Operational' AND ga.year >= 2020
        GROUP BY ga.year ORDER BY ga.year
    """)
    year_coverage = cursor.fetchall()

    return total_operational, with_pris, year_coverage


def build_normalized_lookup(lookup):
    """Build a secondary lookup that strips parentheticals and normalizes Saint/St."""
    normalized = {}
    for (name_upper, unit), value in lookup.items():
        clean = re.sub(r'\s*\([^)]*\)', '', name_upper).strip()
        clean = re.sub(r'\bSAINT\b', 'ST', clean)
        clean = re.sub(r'\bST\.\b', 'ST', clean)
        norm_key = (clean, unit)
        if norm_key not in normalized:
            normalized[norm_key] = value
    return normalized


def match_discovered_to_db(discovered_reactors, conn):
    """Match discovered PRIS reactors to DB entries using 3-tier matching.

    Returns:
        matched: list of (pris_name, pris_id, reactor_db_id, db_plant_name)
        unmatched: list of (pris_name, pris_id, country)
    """
    lookup = build_reactor_lookup(conn)
    all_overrides = {**PRIS_TO_DB_OVERRIDES, **SUPPLEMENTAL_OVERRIDES}
    normalized_lookup = build_normalized_lookup(lookup)

    matched = []
    unmatched = []

    for pris_key, reactor_info in sorted(discovered_reactors.items()):
        pris_id = int(reactor_info['pris_id'])
        country = reactor_info.get('country', '?')

        # Tier 1: Check combined overrides dict
        if pris_key in all_overrides:
            db_name, db_unit = all_overrides[pris_key]
            db_lookup_key = (db_name.upper(), db_unit)
            if db_lookup_key in lookup:
                reactor_db_id, actual_name = lookup[db_lookup_key]
                matched.append((pris_key, pris_id, reactor_db_id, actual_name))
                continue

        # Tier 2: Auto-parse (split on last hyphen, title-case, look up)
        name, unit = parse_pris_key(pris_key)
        db_lookup_key = (name.upper(), unit)
        if db_lookup_key in lookup:
            reactor_db_id, actual_name = lookup[db_lookup_key]
            matched.append((pris_key, pris_id, reactor_db_id, actual_name))
            continue

        # Tier 3: Normalized match (strip parentheticals, normalize Saint/St)
        clean_name = re.sub(r'\s*\([^)]*\)', '', name.upper()).strip()
        clean_name = re.sub(r'\bSAINT\b', 'ST', clean_name)
        clean_name = re.sub(r'\bST\.\b', 'ST', clean_name)
        norm_key = (clean_name, unit)
        if norm_key in normalized_lookup:
            reactor_db_id, actual_name = normalized_lookup[norm_key]
            matched.append((pris_key, pris_id, reactor_db_id, actual_name))
            continue

        unmatched.append((pris_key, pris_id, country))

    return matched, unmatched


def update_pris_ids(conn, matched):
    """Update reactors.pris_id for all matched reactors.

    Returns count of rows actually changed.
    """
    cursor = conn.cursor()
    updated = 0
    for _pris_name, pris_id, reactor_db_id, _db_name in matched:
        cursor.execute(
            "UPDATE reactors SET pris_id = ? "
            "WHERE id = ? AND (pris_id IS NULL OR pris_id != ?)",
            (pris_id, reactor_db_id, pris_id)
        )
        if cursor.rowcount > 0:
            updated += 1
    conn.commit()
    return updated


def fetch_and_insert_generation(conn, reactors_to_fetch, session, delay=0.5):
    """Fetch generation data from PRIS and insert into DB.

    Returns (fetched_count, inserted_count, error_count).
    """
    cursor = conn.cursor()
    fetched_count = 0
    inserted_count = 0
    error_count = 0

    for i, (pris_name, pris_id, reactor_db_id, db_name) in enumerate(
            reactors_to_fetch, 1):
        cursor.execute(
            "SELECT year FROM generation_annual WHERE reactor_id = ?",
            (reactor_db_id,)
        )
        existing_years = {row[0] for row in cursor.fetchall()}

        print(f"  [{i}/{len(reactors_to_fetch)}] {db_name} (PRIS {pris_id})...",
              end='', flush=True)

        generation = fetch_reactor_generation(pris_id, session)

        if generation:
            fetched_count += 1
            new_years = {y: v for y, v in generation.items()
                         if y not in existing_years}

            if new_years:
                years_inserted = []
                for year in sorted(new_years):
                    try:
                        cursor.execute(
                            "INSERT OR IGNORE INTO generation_annual "
                            "(reactor_id, year, electricity_gwh) VALUES (?, ?, ?)",
                            (reactor_db_id, year, new_years[year])
                        )
                        if cursor.rowcount > 0:
                            inserted_count += 1
                            years_inserted.append(str(year))
                    except sqlite3.Error as e:
                        print(f" DB error: {e}", end='')
                        error_count += 1

                if years_inserted:
                    print(f" +{len(years_inserted)} years"
                          f" ({years_inserted[0]}-{years_inserted[-1]})")
                else:
                    print(" all years already in DB")
            else:
                print(" no new data")
        else:
            print(" fetch failed")
            error_count += 1

        time.sleep(delay)

    conn.commit()
    return fetched_count, inserted_count, error_count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Backfill PRIS coverage: discover IDs, match, and '
                    'fetch generation data.'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Discover and match only, do not write to database'
    )
    parser.add_argument(
        '--discover-only', action='store_true',
        help='Discover, match, and update pris_id, but skip generation fetch'
    )
    parser.add_argument(
        '--fetch-mode', choices=['all', 'new-only'], default=None,
        help='all = every matched reactor; new-only = only newly-matched'
    )
    parser.add_argument(
        '--delay', type=float, default=1.0,
        help='Delay between country page requests (default: 1.0s)'
    )
    args = parser.parse_args()

    if not args.dry_run and not args.discover_only and args.fetch_mode is None:
        args.fetch_mode = 'all'

    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    print("=" * 65)
    print("Backfill PRIS Coverage")
    print("=" * 65)

    # Pre-run stats
    total_op, pre_pris, pre_year_cov = get_coverage_stats(conn)
    print(f"\nPre-run: {pre_pris}/{total_op} operational reactors have pris_id")
    if pre_year_cov:
        print("  Recent year coverage:")
        for year, count in pre_year_cov:
            print(f"    {year}: {count} reactors")

    # Shared HTTP session for all requests
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'Nuclear Research Database Bot'
    })

    # ------------------------------------------------------------------
    # Step 1: Discover PRIS IDs from all countries via postbacks
    # ------------------------------------------------------------------
    print(f"\n[1/5] Discovering PRIS IDs from {len(COUNTRIES)} countries "
          "(via ASP.NET postbacks)...")
    discovered = discover_all_pris_ids(
        session, delay_country=args.delay, delay_reactor=0.3,
        operational_only=True
    )
    print(f"  Total discovered: {len(discovered)} operational reactors")

    # ------------------------------------------------------------------
    # Step 2: Match discovered reactors to DB entries
    # ------------------------------------------------------------------
    print(f"\n[2/5] Matching PRIS reactors to database...")
    matched, unmatched = match_discovered_to_db(discovered, conn)
    print(f"  Matched: {len(matched)}")
    print(f"  Unmatched: {len(unmatched)}")

    if unmatched:
        print("\n  Unmatched reactors (for manual review):")
        by_country = {}
        for name, pris_id, country in unmatched:
            by_country.setdefault(country, []).append((name, pris_id))
        for country in sorted(by_country):
            reactors = by_country[country]
            print(f"    {country} ({len(reactors)}):")
            for name, pris_id in reactors:
                print(f"      '{name}': {pris_id},")

    if args.dry_run:
        print("\n[DRY RUN] No database changes made.")
        conn.close()
        return

    # ------------------------------------------------------------------
    # Step 3: Update pris_id in database
    # ------------------------------------------------------------------
    print(f"\n[3/5] Updating reactors.pris_id for {len(matched)} "
          "matched reactors...")
    # Identify which reactors will actually change
    cursor = conn.cursor()
    newly_updated_ids = set()
    for _pris_name, pris_id, reactor_db_id, _db_name in matched:
        cursor.execute(
            "SELECT pris_id FROM reactors WHERE id = ?", (reactor_db_id,)
        )
        old_pris = cursor.fetchone()[0]
        if old_pris is None or old_pris != pris_id:
            newly_updated_ids.add(reactor_db_id)

    updated_count = update_pris_ids(conn, matched)
    print(f"  Updated: {updated_count} reactors "
          "(previously had no/different pris_id)")

    if args.discover_only:
        print("\n[DISCOVER-ONLY] Skipping generation fetch.")
        _, post_pris, _ = get_coverage_stats(conn)
        print(f"\nPost-run: {post_pris}/{total_op} operational reactors "
              "have pris_id")
        conn.close()
        return

    # ------------------------------------------------------------------
    # Step 4: Fetch generation data
    # ------------------------------------------------------------------
    if args.fetch_mode == 'new-only':
        reactors_to_fetch = [
            (n, pid, rid, dn) for n, pid, rid, dn in matched
            if rid in newly_updated_ids
        ]
        print(f"\n[4/5] Fetching generation for {len(reactors_to_fetch)} "
              "newly-matched reactors...")
    else:
        reactors_to_fetch = matched
        print(f"\n[4/5] Fetching generation for all "
              f"{len(reactors_to_fetch)} matched reactors...")

    if reactors_to_fetch:
        fetched, inserted, errors = fetch_and_insert_generation(
            conn, reactors_to_fetch, session, delay=0.5
        )
    else:
        fetched, inserted, errors = 0, 0, 0
        print("  Nothing to fetch.")

    # ------------------------------------------------------------------
    # Step 5: Report results
    # ------------------------------------------------------------------
    print(f"\n[5/5] Summary")
    print("=" * 65)

    _, post_pris, post_year_cov = get_coverage_stats(conn)

    print(f"  PRIS IDs:         {pre_pris} -> {post_pris} / "
          f"{total_op} operational reactors")
    print(f"  Newly updated:    {updated_count}")
    print(f"  Reactors fetched: {fetched}")
    print(f"  Records inserted: {inserted}")
    print(f"  Fetch errors:     {errors}")
    print(f"  Unmatched:        {len(unmatched)}")

    if post_year_cov:
        print("\n  Post-run year coverage (2020+):")
        pre_cov_dict = dict(pre_year_cov)
        for year, count in post_year_cov:
            pre_count = pre_cov_dict.get(year, 0)
            marker = f"  (+{count - pre_count})" if count > pre_count else ""
            print(f"    {year}: {count} reactors{marker}")

    conn.close()
    print("\nDone.")


if __name__ == '__main__':
    main()
