#!/usr/bin/env python3
"""Fix incorrect generation data by re-fetching from IAEA PRIS.

The original PRIS scraper (fetch_missing_generation.py) had a fragile HTML
parser that grabbed the first numeric value from any table on the page.
This script re-fetches correct unit-level annual electricity generation
from PRIS and fixes discrepancies.

Two fix modes:
  - Replace: When PRIS has correct unit-level data (CF <= 105%), update DB
  - Delete: When PRIS also has station-level data (CF > 105%), delete the
    bad DB entries that were inserted by the scraper

Uses curl for HTTP (PRIS blocks Python requests via TLS fingerprinting).

Usage:
    python fix_generation_data.py                  # Dry run: show what would change
    python fix_generation_data.py --apply          # Apply fixes to DB
"""

import sqlite3
import subprocess
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"
PRIS_URL = "https://pris.iaea.org/pris/CountryStatistics/ReactorDetails.aspx?current={pris_id}"
REQUEST_DELAY = 2.0
MAX_REASONABLE_CF = 1.05  # 105% — above this, PRIS data is likely station-level


def fetch_pris_html(pris_id):
    """Fetch PRIS reactor page HTML using curl."""
    url = PRIS_URL.format(pris_id=pris_id)
    try:
        result = subprocess.run(
            ['curl', '-s', '-f', '--max-time', '30', url],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except Exception as e:
        print(f"  curl error: {e}")
        return None


def parse_pris_generation(html):
    """Parse annual electricity generation from PRIS reactor page HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    generation = {}

    tables = soup.find_all('table')
    target_table = None
    elec_col_idx = None

    for table in tables:
        headers = table.find_all('th')
        header_texts = [h.get_text(strip=True) for h in headers]
        for i, text in enumerate(header_texts):
            if 'Electricity' in text and 'GW' in text:
                target_table = table
                elec_col_idx = i
                break
        if target_table:
            break

    if target_table is None:
        return {}

    for row in target_table.find_all('tr'):
        cells = row.find_all(['td', 'th'])
        if len(cells) < 2:
            continue
        first_cell = cells[0].get_text(strip=True)
        if not first_cell.isdigit():
            continue
        year = int(first_cell)
        if year < 1960 or year > 2030:
            continue
        if elec_col_idx < len(cells):
            cell_text = cells[elec_col_idx].get_text(strip=True)
            cell_text = cell_text.replace(',', '').replace('\xa0', '').strip()
            try:
                if cell_text and cell_text not in ('NC', 'N/A', '-', ''):
                    val = float(cell_text)
                    if 0 < val < 20000:
                        generation[year] = val
            except ValueError:
                pass

    return generation


def main():
    apply = '--apply' in sys.argv

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get all reactors with CF > 110% and a pris_id
    cur.execute("""
        SELECT DISTINCT r.id, r.plant_name, r.unit_number, r.pris_id,
               COALESCE(r.reference_power_mw, r.net_capacity_mw) as cap
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE r.pris_id IS NOT NULL
        AND g.electricity_gwh * 1000
            / (COALESCE(r.reference_power_mw, r.net_capacity_mw) * 8760) > 1.10
        ORDER BY r.plant_name, r.unit_number
    """)
    reactors = cur.fetchall()

    print(f"{'FIX' if apply else 'DRY RUN'}: Checking {len(reactors)} reactors with CF > 110%")
    print("=" * 70)

    total_replaced = 0
    total_deleted = 0
    total_added = 0
    reactors_fixed = 0
    fetch_failures = 0

    for i, (db_id, plant, unit, pris_id, cap) in enumerate(reactors, 1):
        print(f"\n[{i}/{len(reactors)}] {plant}-{unit} (PRIS {pris_id}, {cap}MW)")

        # Get current DB data
        cur.execute(
            "SELECT year, electricity_gwh FROM generation_annual "
            "WHERE reactor_id = ? ORDER BY year",
            (db_id,)
        )
        db_data = {row[0]: row[1] for row in cur.fetchall()}

        # Fetch from PRIS
        html = fetch_pris_html(pris_id)
        if not html:
            print("  PRIS fetch failed — skipping")
            fetch_failures += 1
            time.sleep(REQUEST_DELAY)
            continue

        pris_data = parse_pris_generation(html)
        if not pris_data:
            print("  No generation data on PRIS page — skipping")
            fetch_failures += 1
            time.sleep(REQUEST_DELAY)
            continue

        # Check if PRIS has unit-level data by looking at median CF
        pris_cfs = []
        for year, gwh in pris_data.items():
            cf = gwh * 1000 / (cap * 8760)
            pris_cfs.append(cf)
        pris_cfs.sort()
        median_pris_cf = pris_cfs[len(pris_cfs) // 2] if pris_cfs else 0

        pris_is_unit_level = median_pris_cf <= MAX_REASONABLE_CF

        if pris_is_unit_level:
            print(f"  PRIS data is unit-level (median CF={median_pris_cf*100:.0f}%)")
        else:
            print(f"  PRIS data is STATION-LEVEL (median CF={median_pris_cf*100:.0f}%) — will delete bad DB entries only")

        changed = False
        for year in sorted(set(db_data.keys()) | set(pris_data.keys())):
            db_val = db_data.get(year)
            pris_val = pris_data.get(year)

            if db_val is not None and pris_val is not None:
                if abs(db_val - pris_val) <= 0.1:
                    continue  # Match

                cf_db = db_val * 1000 / (cap * 8760)
                cf_pris = pris_val * 1000 / (cap * 8760)

                if pris_is_unit_level:
                    # Replace DB with PRIS value
                    print(f"  {year}: REPLACE DB={db_val:.1f} ({cf_db*100:.0f}%)"
                          f" -> PRIS={pris_val:.1f} ({cf_pris*100:.0f}%)"
                          f"{'  !!!' if cf_db > 1.1 else ''}")
                    if apply:
                        cur.execute(
                            "UPDATE generation_annual SET electricity_gwh = ? "
                            "WHERE reactor_id = ? AND year = ?",
                            (pris_val, db_id, year)
                        )
                    total_replaced += 1
                    changed = True
                else:
                    # PRIS is station-level too. If DB value is bad (>110% CF), delete it
                    if cf_db > 1.10:
                        print(f"  {year}: DELETE DB={db_val:.1f} ({cf_db*100:.0f}%)"
                              f" [PRIS also bad: {pris_val:.1f} ({cf_pris*100:.0f}%)]")
                        if apply:
                            cur.execute(
                                "DELETE FROM generation_annual "
                                "WHERE reactor_id = ? AND year = ?",
                                (db_id, year)
                            )
                        total_deleted += 1
                        changed = True

            elif db_val is None and pris_val is not None and pris_is_unit_level:
                cf_pris = pris_val * 1000 / (cap * 8760)
                if cf_pris <= MAX_REASONABLE_CF:
                    print(f"  {year}: ADD PRIS={pris_val:.1f} ({cf_pris*100:.0f}%)")
                    if apply:
                        cur.execute(
                            "INSERT OR IGNORE INTO generation_annual "
                            "(reactor_id, year, electricity_gwh) VALUES (?, ?, ?)",
                            (db_id, year, pris_val)
                        )
                    total_added += 1
                    changed = True

        if changed:
            reactors_fixed += 1
        elif not changed and pris_is_unit_level:
            print("  OK — all data matches PRIS")

        time.sleep(REQUEST_DELAY)

    if apply:
        conn.commit()

    print("\n" + "=" * 70)
    print(f"{'Applied' if apply else 'Would apply'}:")
    print(f"  Reactors fixed: {reactors_fixed}/{len(reactors)}")
    print(f"  Values replaced with PRIS: {total_replaced}")
    print(f"  Bad values deleted: {total_deleted}")
    print(f"  Missing values added: {total_added}")
    if fetch_failures:
        print(f"  Fetch failures: {fetch_failures}")

    conn.close()


if __name__ == '__main__':
    main()
