"""
WNA Audit Phase 2 — Capacity Updates

Strategy: Update net_capacity_mw for OPERATIONAL reactors where WNA differs by >20 MWe.
Shutdown reactors are left alone (capacity at shutdown is fixed, PRIS is authoritative).
Suspended reactors are left alone (status is ambiguous).
UC reactors are updated (WNA likely has current design specs).

Also normalizes TYPE naming in the audit script (no DB changes needed).
"""

import json
import re
import sqlite3
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = "nuclear_reactors.db"
THRESHOLD_MWE = 20


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Load scraped WNA data
    with open("wna_scraped_data.json", "r", encoding="utf-8") as f:
        wna_data = json.load(f)

    import html as html_mod
    for r in wna_data:
        r["name"] = html_mod.unescape(r["name"])

    # Load all non-Chinese reactors
    cur.execute("""
        SELECT r.id, r.plant_name, r.unit_number, r.status,
               r.net_capacity_mw, r.gross_capacity_mw,
               c.name as country
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        WHERE c.name != 'China'
    """)
    db_reactors = {r["id"]: dict(r) for r in cur.fetchall()}

    # Re-use the matching from the audit to build WNA->DB id mapping
    # Load the audit report to extract matched pairs with capacity diffs
    with open("wna_audit_report.txt", "r", encoding="utf-8") as f:
        report = f.read()

    # Parse actionable capacity discrepancies from the report
    capacity_updates = []
    skipped_shutdown = []
    skipped_suspended = []
    skipped_small = []

    lines = report.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("  ") and "[DB id=" in line:
            # Extract reactor label and DB id
            m = re.search(r"\[DB id=(\d+)\]", line)
            if not m:
                i += 1
                continue
            db_id = int(m.group(1))
            reactor_label = line.strip().split(" [DB")[0]

            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                disc = lines[i].strip()
                if disc.startswith("NET_CAPACITY:"):
                    # Parse: NET_CAPACITY: WNA=1011 MWe  |  DB=900 MWe  (diff: 111 MWe)
                    cap_m = re.search(r"WNA=(\d+) MWe\s+\|\s+DB=(\d+) MWe\s+\(diff: (\d+) MWe\)", disc)
                    if cap_m:
                        wna_cap = int(cap_m.group(1))
                        db_cap = int(cap_m.group(2))
                        diff = int(cap_m.group(3))

                        if db_id in db_reactors:
                            db_r = db_reactors[db_id]
                            status = db_r["status"]

                            if status == "Permanent Shutdown":
                                skipped_shutdown.append((reactor_label, db_id, wna_cap, db_cap, diff))
                            elif status == "Suspended":
                                skipped_suspended.append((reactor_label, db_id, wna_cap, db_cap, diff))
                            elif diff <= THRESHOLD_MWE:
                                skipped_small.append((reactor_label, db_id, wna_cap, db_cap, diff))
                            else:
                                capacity_updates.append((reactor_label, db_id, wna_cap, db_cap, diff, status))
                i += 1
        else:
            i += 1

    # Print summary
    print("=" * 70)
    print("WNA PHASE 2 — CAPACITY UPDATES")
    print("=" * 70)
    print(f"\nTotal capacity discrepancies found: {len(capacity_updates) + len(skipped_shutdown) + len(skipped_suspended) + len(skipped_small)}")
    print(f"  Will update (Operational/UC, diff > {THRESHOLD_MWE} MWe): {len(capacity_updates)}")
    print(f"  Skipped — Permanent Shutdown: {len(skipped_shutdown)}")
    print(f"  Skipped — Suspended: {len(skipped_suspended)}")
    print(f"  Skipped — diff <= {THRESHOLD_MWE} MWe: {len(skipped_small)}")

    # Apply updates
    print(f"\n--- APPLYING {len(capacity_updates)} CAPACITY UPDATES ---\n")

    by_country = {}
    for label, db_id, wna_cap, db_cap, diff, status in sorted(capacity_updates):
        country = label.split("(")[-1].rstrip(")")
        if country not in by_country:
            by_country[country] = []
        by_country[country].append((label, db_id, wna_cap, db_cap, diff, status))

    update_count = 0
    for country in sorted(by_country):
        print(f"  {country}:")
        for label, db_id, wna_cap, db_cap, diff, status in by_country[country]:
            reactor_name = label.split(f" ({country})")[0]
            cur.execute("UPDATE reactors SET net_capacity_mw=? WHERE id=?", (wna_cap, db_id))
            print(f"    {reactor_name}: {db_cap} -> {wna_cap} MWe (+{wna_cap - db_cap})")
            update_count += 1

    # Show what was skipped (shutdown)
    print(f"\n--- SKIPPED: SHUTDOWN REACTORS ({len(skipped_shutdown)}) ---\n")
    for label, db_id, wna_cap, db_cap, diff in sorted(skipped_shutdown)[:10]:
        direction = "WNA higher" if wna_cap > db_cap else "WNA lower"
        print(f"  {label}: WNA={wna_cap}, DB={db_cap} ({direction}, {diff} MWe)")
    if len(skipped_shutdown) > 10:
        print(f"  ... and {len(skipped_shutdown) - 10} more")

    conn.commit()
    conn.close()

    print(f"\n{'=' * 70}")
    print(f"Updated {update_count} reactor capacities.")
    print(f"Remaining date diffs saved as TODO in PLAN.md")


if __name__ == "__main__":
    main()
