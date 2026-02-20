#!/usr/bin/env python3
"""
Nuclear Reactor Status Audit & Correction Script
=================================================
Reviews reactor statuses in the database and applies corrections
based on known operational changes through February 2026.

RUN IN TWO MODES:
  python status_audit.py --review    Show proposed changes (default)
  python status_audit.py --apply     Apply changes to database

Always run --review first and check the output before applying.
"""

import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

# =============================================================================
# PROPOSED STATUS CORRECTIONS
# Each entry: (plant_name, unit_number, old_status, new_status,
#              commercial_operation_date_correction, notes)
# =============================================================================

CORRECTIONS = [
    # --- Under Construction → Operational (confirmed commercial operation) ---

    # USA
    ("Vogtle", "3", "Under Construction", "Operational",
     "2023-07-31", "Entered commercial operation July 31, 2023"),
    ("Vogtle", "4", "Under Construction", "Operational",
     "2024-04-29", "Entered commercial operation April 29, 2024"),

    # Russia
    ("Novovoronezh 2", "2", "Under Construction", "Operational",
     "2019-10-31", "Commercial operation Oct 31, 2019 (date in DB was correct)"),
    ("Leningrad 2", "2", "Under Construction", "Operational",
     "2021-03-22", "Commercial operation March 22, 2021"),

    # China
    ("Fuqing", "5", "Under Construction", "Operational",
     "2021-01-30", "Commercial operation Jan 30, 2021"),
    ("Fuqing", "6", "Under Construction", "Operational",
     "2022-03-25", "Commercial operation March 25, 2022"),
    ("Tianwan", "6", "Under Construction", "Operational",
     "2021-06-03", "Commercial operation June 3, 2021"),
    ("Hongyanhe", "5", "Under Construction", "Operational",
     "2021-07-31", "Commercial operation July 31, 2021"),
    ("Hongyanhe", "6", "Under Construction", "Operational",
     "2022-06-23", "Commercial operation June 23, 2022"),
    ("Fangchenggang", "3", "Under Construction", "Operational",
     "2023-03-25", "Commercial operation March 25, 2023"),
    ("Fangchenggang", "4", "Under Construction", "Operational",
     "2024-05-25", "Commercial operation May 25, 2024"),
    ("Zhangzhou", "1", "Under Construction", "Operational",
     "2025-01-01", "Commercial operation January 1, 2025"),
    ("Zhangzhou", "2", "Under Construction", "Operational",
     "2026-01-01", "Commercial operation January 1, 2026"),

    # UAE
    ("Barakah", "2", "Under Construction", "Operational",
     "2022-03-24", "Commercial operation March 2022"),
    ("Barakah", "3", "Under Construction", "Operational",
     "2023-02-24", "Commercial operation February 2023"),
    ("Barakah", "4", "Under Construction", "Operational",
     "2024-09-22", "Commercial operation September 2024"),

    # Belarus
    ("Belarusian", "1", "Under Construction", "Operational",
     "2021-06-10", "Commercial operation June 2021"),
    ("Belarusian", "2", "Under Construction", "Operational",
     "2023-11-01", "Commercial operation November 1, 2023"),

    # Finland
    ("Olkiluoto", "3", "Under Construction", "Operational",
     "2023-04-16", "Commercial operation April 16, 2023"),

    # Slovakia
    ("Mochovce", "3", "Under Construction", "Operational",
     "2023-10-01", "Commercial operation October 2023"),

    # South Korea
    ("Shin-Hanul (Shin-Ulchin)", "1", "Under Construction", "Operational",
     "2022-12-07", "Commercial operation December 7, 2022"),
    ("Shin-Hanul (Shin-Ulchin)", "2", "Under Construction", "Operational",
     "2024-04-05", "Commercial operation April 5, 2024"),

    # India
    ("Kakrapar", "3", "Under Construction", "Operational",
     "2023-06-30", "Commercial operation June 30, 2023"),
    ("Kakrapar", "4", "Under Construction", "Operational",
     "2024-03-31", "Commercial operation March 31, 2024"),

    # --- Unknown → Operational ---

    ("Bushehr", "1", "Unknown", "Operational",
     "2013-09-01", "Operational since 2011, commercial operation ~2013"),

    # --- Operational → Permanent Shutdown (recent closures) ---

    # Taiwan
    ("Kuosheng (Second)", "2", "Operational", "Permanent Shutdown",
     None, "Permanently shut down July 2023 (license expired)"),
    ("Maanshan (Third)", "1", "Operational", "Permanent Shutdown",
     None, "Permanently shut down July 2024"),
    ("Maanshan (Third)", "2", "Operational", "Permanent Shutdown",
     None, "Permanently shut down May 17, 2025 — Taiwan's last reactor"),

    # --- Date corrections only (status already correct but date was wrong) ---

    ("Flamanville", "3", "Under Construction", "Under Construction",
     None, "Still in commissioning as of Feb 2026. Clearing incorrect "
           "commercial_operation date of 2023-03-01. Grid connected Dec 2024, "
           "100% power Dec 2025, commercial operation expected Q1 2026."),
]

# Shutdown dates for reactors changing to Permanent Shutdown
SHUTDOWN_DATES = {
    ("Kuosheng (Second)", "2"): "2023-07-01",
    ("Maanshan (Third)", "1"): "2024-07-27",
    ("Maanshan (Third)", "2"): "2025-05-17",
}


def review_corrections():
    """Show all proposed corrections without applying them."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print("NUCLEAR REACTOR STATUS AUDIT — PROPOSED CORRECTIONS")
    print(f"Database: {DB_PATH}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 80)

    status_changes = 0
    date_fixes = 0
    not_found = 0

    for plant, unit, old_status, new_status, new_date, notes in CORRECTIONS:
        cursor.execute(
            "SELECT r.id, r.plant_name, r.unit_number, r.status, "
            "r.commercial_operation, c.name as country "
            "FROM reactors r JOIN countries c ON r.country_id = c.id "
            "WHERE r.plant_name = ? AND r.unit_number = ?",
            (plant, unit)
        )
        row = cursor.fetchone()

        if not row:
            print(f"\n  [NOT FOUND] {plant}-{unit}")
            not_found += 1
            continue

        current_status = row['status']
        current_date = row['commercial_operation']
        country = row['country']

        # Check if status change is needed
        needs_status_change = (old_status != new_status) and (current_status == old_status)
        needs_date_fix = (new_date is not None and current_date != new_date) or \
                         (new_date is None and plant == "Flamanville" and current_date is not None)

        if needs_status_change or needs_date_fix:
            print(f"\n  [{country}] {plant}-{unit}")
            if needs_status_change:
                print(f"    Status: {current_status} → {new_status}")
                status_changes += 1
            if needs_date_fix:
                if new_date:
                    print(f"    Commercial operation: {current_date} → {new_date}")
                else:
                    print(f"    Commercial operation: {current_date} → NULL (clearing incorrect date)")
                date_fixes += 1
            print(f"    Notes: {notes}")
        else:
            if current_status != old_status:
                print(f"\n  [SKIP] {plant}-{unit} ({country}) — "
                      f"expected status '{old_status}' but found '{current_status}'")
            else:
                print(f"\n  [ALREADY CORRECT] {plant}-{unit} ({country})")

    # Show shutdown dates
    for (plant, unit), shutdown_date in SHUTDOWN_DATES.items():
        cursor.execute(
            "SELECT r.permanent_shutdown FROM reactors r "
            "WHERE r.plant_name = ? AND r.unit_number = ?",
            (plant, unit)
        )
        row = cursor.fetchone()
        if row and not row['permanent_shutdown']:
            print(f"\n  [SHUTDOWN DATE] {plant}-{unit}: will set permanent_shutdown = {shutdown_date}")

    conn.close()

    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {status_changes} status changes, {date_fixes} date corrections, "
          f"{not_found} not found")
    print(f"{'=' * 80}")
    print(f"\nTo apply these corrections, run:")
    print(f"  python status_audit.py --apply")


def apply_corrections():
    """Apply all corrections to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("APPLYING REACTOR STATUS CORRECTIONS")
    print("=" * 80)

    applied = 0
    skipped = 0

    for plant, unit, old_status, new_status, new_date, notes in CORRECTIONS:
        cursor.execute(
            "SELECT id, status, commercial_operation FROM reactors "
            "WHERE plant_name = ? AND unit_number = ?",
            (plant, unit)
        )
        row = cursor.fetchone()

        if not row:
            print(f"  [NOT FOUND] {plant}-{unit} — skipping")
            skipped += 1
            continue

        reactor_id, current_status, current_date = row

        if current_status != old_status:
            print(f"  [SKIP] {plant}-{unit} — status is '{current_status}', "
                  f"expected '{old_status}'")
            skipped += 1
            continue

        updates = []
        params = []

        # Status change
        if old_status != new_status:
            updates.append("status = ?")
            params.append(new_status)

        # Commercial operation date
        if new_date is not None:
            updates.append("commercial_operation = ?")
            params.append(new_date)
        elif plant == "Flamanville" and unit == "3":
            updates.append("commercial_operation = NULL")

        # Shutdown date
        if (plant, unit) in SHUTDOWN_DATES:
            updates.append("permanent_shutdown = ?")
            params.append(SHUTDOWN_DATES[(plant, unit)])

        if updates:
            sql = f"UPDATE reactors SET {', '.join(updates)} WHERE id = ?"
            params.append(reactor_id)
            cursor.execute(sql, params)
            print(f"  [UPDATED] {plant}-{unit}: {old_status} → {new_status} "
                  f"{'(+ date fix)' if new_date or plant == 'Flamanville' else ''}")
            applied += 1
        else:
            print(f"  [NO CHANGE] {plant}-{unit}")

    conn.commit()
    conn.close()

    print(f"\n{'=' * 80}")
    print(f"DONE: {applied} reactors updated, {skipped} skipped")
    print(f"{'=' * 80}")


def main():
    parser = argparse.ArgumentParser(description="Nuclear reactor status audit")
    parser.add_argument("--review", action="store_true", default=True,
                        help="Review proposed changes (default)")
    parser.add_argument("--apply", action="store_true",
                        help="Apply corrections to database")
    args = parser.parse_args()

    if args.apply:
        apply_corrections()
    else:
        review_corrections()


if __name__ == "__main__":
    main()
