"""Invariant scan: internal-consistency checks that need no outside source (audit Phase 1b).

Purpose: flag rows that cannot all be true at once (net > gross, dates out of order, one value
  copied across units built a decade apart, ...). Candidates only: each still needs a source.
Inputs:  nuclear_reactors.db (read-only).
Outputs: audit/invariants.tsv (check, reactor/plant, detail) + counts on stdout.
Usage:   python scripts/invariant_scan.py
last_run: 2026-10-13
"""
import csv
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
TODAY = date.today().isoformat()


def main():
    db = sqlite3.connect(f"file:{ROOT / 'nuclear_reactors.db'}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    rs = [dict(r) for r in db.execute("""
        SELECT r.*, m.name AS model, t.code AS tech, d.cooling_type, d.constructor, d.architect_engineer,
               d.turbine_supplier, d.pressure_vessel_manufacturer
        FROM reactors r LEFT JOIN models m ON m.id = r.model_id LEFT JOIN technologies t ON t.id = r.technology_id
        LEFT JOIN reactor_details d ON d.reactor_id = r.id""")]
    out = []

    def flag(check, who, detail):
        out.append([check, who, detail])

    for r in rs:
        who = f"{r['plant_name']} {r['unit_number']} [{r['status']}]"
        g, n, t = r["gross_capacity_mw"], r["net_capacity_mw"], r["thermal_capacity_mw"]
        if g and n and n > g:
            flag("net > gross", who, f"net {n} > gross {g}")
        if g and t and r["tech"] in ("PWR", "BWR", "PHWR") and not (0.27 <= g / t <= 0.40):
            flag("gross/thermal ratio implausible (LWR/PHWR)", who, f"gross {g} / thermal {t} = {g / t:.3f}")
        seq = [(k, str(r[k])[:10]) for k in ("construction_start", "first_criticality", "grid_connection",
                                               "commercial_operation", "permanent_shutdown") if r[k]]
        for (k1, v1), (k2, v2) in zip(seq, seq[1:]):
            if len(v1) == 10 and len(v2) == 10 and v2 < v1:
                flag("dates out of order", who, f"{k2} {v2} < {k1} {v1}")
        if r["status"] == "Operational":
            for k in ("planned_retirement", "licensed_until"):
                v = str(r[k]) if r[k] is not None else ""
                if v and v[:4].isdigit() and v[:10] < TODAY[: len(v[:10])]:
                    flag(f"{k} in the past (operating reactor)", who, v)
        for k in ("construction_start", "grid_connection", "commercial_operation", "permanent_shutdown"):
            v = str(r[k]) if r[k] else ""
            if v.endswith("-01-01"):
                flag("1 January date (often a year-only placeholder)", who, f"{k} {v}")

    # One value on every unit of a plant whose units were built far apart (class 1: per-plant copy)
    plants = defaultdict(list)
    for r in rs:
        plants[(r["plant_name"], r["country_id"])].append(r)
    for (plant, _), us in plants.items():
        yrs = [int(str(u["construction_start"])[:4]) for u in us if u["construction_start"]]
        if len(us) < 2 or not yrs or max(yrs) - min(yrs) < 8:
            continue
        for k in ("cooling_type", "model", "design_series", "containment_type", "constructor",
                  "architect_engineer", "turbine_supplier", "pressure_vessel_manufacturer"):
            vals = {u[k] for u in us}
            if len(vals) == 1 and None not in vals:
                flag("same value on units built 8+ years apart", f"{plant} ({len(us)} units, {min(yrs)}-{max(yrs)})",
                     f"{k} = {next(iter(vals))}")

    gen_before = db.execute("""SELECT r.plant_name || ' ' || r.unit_number, COUNT(*), MIN(g.year), substr(r.grid_connection,1,4)
        FROM generation_annual g JOIN reactors r ON r.id = g.reactor_id
        WHERE r.grid_connection IS NOT NULL AND g.year < CAST(substr(r.grid_connection,1,4) AS INT)
        GROUP BY r.id""").fetchall()
    for name, cnt, y0, gy in gen_before:
        flag("generation before grid connection", name, f"{cnt} rows from {y0}; grid {gy}")

    with open(ROOT / "audit" / "invariants.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["check", "who", "detail"])
        w.writerows(out)
    for k, v in Counter(o[0] for o in out).most_common():
        print(f"  {v:4}  {k}")


if __name__ == "__main__":
    main()
