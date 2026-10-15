"""Export the unit lists the projection research works from.

Purpose: snapshot of Under Construction units and operating/suspended units for the projection-range research.
Inputs:  nuclear_reactors.db
Outputs: audit/projection/uc_units_<date>.tsv, audit/projection/operating_units_<date>.tsv
last_run: 2026-10-15
"""
import csv
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "audit" / "projection"
OUT.mkdir(parents=True, exist_ok=True)
stamp = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()

c = sqlite3.connect(ROOT / "nuclear_reactors.db")
c.row_factory = sqlite3.Row
QUERIES = {
    "uc_units": """SELECT r.id, c.name AS country, r.plant_name, r.unit_number, r.status, r.construction_start,
                          r.first_criticality, r.grid_connection, r.expected_operation, r.expected_status,
                          r.expected_source, r.gross_capacity_mw
                   FROM reactors r JOIN countries c ON c.id = r.country_id
                   WHERE r.status = 'Under Construction' ORDER BY c.name, r.plant_name, r.unit_number""",
    "operating_units": """SELECT r.id, c.name AS country, r.plant_name, r.unit_number, r.status, r.grid_connection,
                                 r.gross_capacity_mw, r.planned_retirement, r.licensed_until
                          FROM reactors r JOIN countries c ON c.id = r.country_id
                          WHERE r.status IN ('Operational', 'Suspended') ORDER BY c.name, r.plant_name, r.unit_number""",
}
for name, q in QUERIES.items():
    rows = c.execute(q).fetchall()
    path = OUT / f"{name}_{stamp}.tsv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(rows[0].keys())
        w.writerows(tuple(r) for r in rows)
    print(path.name, len(rows))
