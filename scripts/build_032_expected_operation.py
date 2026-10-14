"""Build migration 032: expected start of operation for reactors under construction + date fixes.

Purpose: expected dates were stored in actual-date columns (grid_connection / commercial_operation) for 6
  under-construction units, and 74 others had none, so the homepage projection piled overdue units into
  next year. This adds sourced expected dates in their own columns, clears future dates from actual-date
  columns, moves units already on the grid to Operational, and fixes dates found wrong in review.
Inputs:  audit/uc_expected_dates_2026-10-14.psv (one row per UC reactor: expected_grid, expected_commercial,
         status note, source URL + quote, researched 2026-10-14), audit/date_status_checks_2026-10-14.psv,
         nuclear_reactors.db (read-only, for guards).
Outputs: migrations/032_expected_operation_and_dates.sql
Usage:   python scripts/build_032_expected_operation.py
last_run: 2026-10-14
"""
import csv
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "audit" / "uc_expected_dates_2026-10-14.psv"
TODAY = date.today().isoformat()
# Already on the grid per WNA China page (updated 2026-10-08) / CGTN-sourced report; exact grid dates.
CONNECTED = {689: "2026-08-01", 99: "2026-07-04", 707: "2026-10-08"}  # Changjiang 3, Taipingling 2, Tianwan 7


def q(s):
    return "NULL" if s is None else "'" + str(s).replace("'", "''") + "'"


def first_date(text):
    """Earliest date-like token: YYYY, YYYY-MM or YYYY-MM-DD (ranges take their first year)."""
    m = re.search(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", text or "")
    if not m:
        return None
    return "-".join(p for p in m.groups() if p)


def main():
    rows = list(csv.DictReader(open(LEDGER, encoding="utf-8"), delimiter="|"))
    status_col = [k for k in rows[0] if k.startswith("status_note")][0]
    L = [
        "-- 032_expected_operation_and_dates.sql",
        "-- Date: 2026-10-14",
        "-- Description: expected start of operation for reactors under construction, in new columns",
        "--   (expected_operation = earliest announced grid connection, else commercial operation; YYYY[-MM[-DD]];",
        "--   expected_status = ON_TRACK / DELAYED / NO_DATE / PAUSED / CONNECTED; expected_source = URL).",
        "--   Ledger with verbatim quotes: audit/uc_expected_dates_2026-10-14.psv (researched 2026-10-14).",
        "-- Also: (1) future dates removed from actual-date columns (they were PRIS expectations, now in",
        "--   expected_operation); (2) Changjiang 3, Taipingling 2, Tianwan 7 are on the grid -> Operational",
        "--   (WNA China profile updated 2026-10-08; Tianwan 7 also bastillepost.com report of grid connection);",
        "--   (3) commercial_operation set NULL where wrong: Shidaowan Guohe One 1 (held Shidao Bay 1's date,",
        "--   true date 'end of 2024', day unknown, WNA), Monju and Saxton (never in commercial operation; PRIS",
        "--   commercialDate null); (4) Fangjiashan 1 2014 generation 1000.0 GWh deleted: round unsourced figure.",
        "--   Ledger: audit/date_status_checks_2026-10-14.psv.",
        "-- Built by scripts/build_032_expected_operation.py. Backup: nuclear_reactors.db.bak-pre032-20261014",
        "",
        "BEGIN TRANSACTION;",
        "ALTER TABLE reactors ADD COLUMN expected_operation TEXT;",
        "ALTER TABLE reactors ADD COLUMN expected_status TEXT;",
        "ALTER TABLE reactors ADD COLUMN expected_source TEXT;",
        "",
    ]
    n_exp = 0
    for r in rows:
        rid = int(r["reactor_id"])
        st = r[status_col].strip()
        if rid in CONNECTED:
            continue
        exp = None if st == "PAUSED" else (first_date(r["expected_grid"]) or first_date(r["expected_commercial"]))
        n_exp += exp is not None
        L.append(f"UPDATE reactors SET expected_operation = {q(exp)}, expected_status = {q(st)}, "
                 f"expected_source = {q(r['source_url'].split(' ; ')[0])}, updated_at = CURRENT_TIMESTAMP "
                 f"WHERE id = {rid} AND status = 'Under Construction';  -- {r['reactor']}")
    L += ["",
          "-- Future dates out of actual-date columns (the expectation is now in expected_operation)",
          f"UPDATE reactors SET grid_connection = NULL WHERE status = 'Under Construction' AND grid_connection > '{TODAY}';",
          f"UPDATE reactors SET commercial_operation = NULL WHERE status = 'Under Construction' AND commercial_operation > '{TODAY}';",
          f"UPDATE reactors SET first_criticality = NULL WHERE status = 'Under Construction' AND first_criticality > '{TODAY}';",
          "",
          "-- Units already connected to the grid"]
    for rid, d in CONNECTED.items():
        L.append(f"UPDATE reactors SET status = 'Operational', grid_connection = '{d}', expected_operation = NULL, "
                 f"expected_status = NULL, expected_source = NULL, updated_at = CURRENT_TIMESTAMP "
                 f"WHERE id = {rid} AND status = 'Under Construction';")
    L += ["",
          "-- Wrong commercial-operation dates",
          "UPDATE reactors SET commercial_operation = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = 714 AND commercial_operation = '2023-12-06';",
          "UPDATE reactors SET commercial_operation = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = 308 AND commercial_operation = '1995-08-01';",
          "UPDATE reactors SET commercial_operation = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = 657 AND commercial_operation = '1967-01-01';",
          "",
          "-- Unsourced placeholder generation",
          "DELETE FROM generation_annual WHERE reactor_id = 64 AND year = 2014 AND electricity_gwh = 1000.0;",
          "",
          "COMMIT;", ""]
    out = ROOT / "migrations" / "032_expected_operation_and_dates.sql"
    out.write_text("\n".join(L), encoding="utf-8")
    print(out, f"{len(rows)} ledger rows, {n_exp} with an expected date, {len(CONNECTED)} moved to Operational")


if __name__ == "__main__":
    main()
