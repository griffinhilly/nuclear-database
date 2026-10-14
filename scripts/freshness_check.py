"""Freshness check: find facts that time has made stale (time-based detector; deterministic, no AI).

Purpose: the database drifts even when nobody edits it. Reactors connect to the grid, close, restart;
  licences and planned dates pass; a new year of generation data is published. This lists every fact
  whose real-world state has probably changed since we recorded it, so a refresh happens on schedule
  instead of when a reader notices. Companion to scripts/site_consistency.py (agreement between surfaces).
Inputs:  nuclear_reactors.db (or --db PATH, read-only); audit/pris_api/all_reactors.json (IAEA PRIS pull,
         refresh first with: python scripts/pris_api_pull.py --force).
Outputs: report on stdout; with --out, also writes it to that file. Exit 1 if any ACTION item.
Usage:   python scripts/pris_api_pull.py --force && python scripts/freshness_check.py --out audit/freshness/<date>.txt
Schedule: monthly (PRIS updates continuously; generation series update yearly, around mid-year).
last_run: 2026-10-14
"""
import argparse
import json
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PRIS_STATUS = {"Operational": "Operational", "Under Construction": "Under Construction",
               "Suspended Operation": "Suspended", "Permanent Shutdown": "Shutdown",
               "Decommissioning Completed": "Shutdown"}
# Deliberate disagreements with PRIS, each decided with a source in migration 028 (re-check when PRIS moves):
# Sanao 1, Tarapur 1/2, KK-6 are running (PRIS lags); Palisades is restarting, not permanently closed;
# Bushehr 3 has no first concrete reported, so it stays a planned project. Changjiang 3, Taipingling 2 and
# Tianwan 7 connected to the grid in Jul-Oct 2026 (migration 032); PRIS still lists them under construction.
STATUS_EXCEPTIONS = {"Sanao 1", "Tarapur 1", "Tarapur 2", "Kashiwazaki Kariwa 6", "Palisades 1",
                     "Changjiang 3", "Taipingling 2", "Tianwan 7"}
MISSING_EXCEPTIONS = {"BUSHEHR-3"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "nuclear_reactors.db"))
    ap.add_argument("--out")
    a = ap.parse_args()
    db = sqlite3.connect(f"file:{Path(a.db).resolve()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    q = lambda s, *p: [dict(r) for r in db.execute(s, p)]
    today = date.today()
    lines, n_action = [], 0

    def item(level, name, rows, detail=""):
        nonlocal n_action
        if not rows:
            lines.append(f"[OK] {name}")
            return
        if level == "ACTION":
            n_action += 1
        lines.append(f"[{level}] {name}: {len(rows)} {detail}")
        for r in rows[:15]:
            lines.append(f"      - {r}")
        if len(rows) > 15:
            lines.append(f"      ... {len(rows) - 15} more")

    # 1. Source freshness
    pris_file = ROOT / "audit" / "pris_api" / "all_reactors.json"
    if pris_file.exists():
        age = (datetime.now() - datetime.fromtimestamp(pris_file.stat().st_mtime)).days
        item("ACTION" if age > 35 else "OK", "IAEA PRIS pull is recent",
             [f"pulled {age} days ago; run scripts/pris_api_pull.py --force"] if age > 35 else [])
    else:
        item("ACTION", "IAEA PRIS pull present", ["missing; run scripts/pris_api_pull.py"])
    try:
        latest = q("SELECT MAX(year) AS y, MAX(retrieved) AS r FROM external_series WHERE series = 'nuclear_generation_twh'")[0]
        due = today.year - 1 if today.month >= 7 else today.year - 2
        item("ACTION", "Published generation series has last year's data",
             [f"latest {latest['y']} (retrieved {latest['r']}); {due} expected — re-download OWID and rebuild migration 029's data"]
             if (latest["y"] or 0) < due else [])
    except sqlite3.OperationalError:
        item("ACTION", "external_series table present", ["missing (migration 029 not applied)"])
    gen_latest = q("SELECT MAX(year) AS y FROM generation_annual")[0]["y"]
    item("ACTION", "Reactor-level generation has last year's data",
         [f"latest year {gen_latest}; run scripts/pris_generation_pull.py"]
         if (gen_latest or 0) < (today.year - 1 if today.month >= 4 else today.year - 2) else [])

    # 2. Status and milestones vs IAEA PRIS
    if pris_file.exists():
        pris = {r["id"]: r for r in json.load(open(pris_file, encoding="utf-8"))}
        rows = q("SELECT id, plant_name || ' ' || unit_number AS name, pris_id, status, grid_connection, "
                 "permanent_shutdown FROM reactors")
        drift, new_grid, new_close = [], [], []
        for r in rows:
            p = pris.get(r["pris_id"])
            if not p:
                continue
            ps = PRIS_STATUS.get(p["statusName"], p["statusName"])
            if ps != r["status"] and r["name"] not in STATUS_EXCEPTIONS:
                drift.append(f"{r['name']}: ours {r['status']}, PRIS {p['statusName']}")
            if p.get("gridDate") and p["gridDate"][:10] <= today.isoformat() and not r["grid_connection"]:
                new_grid.append(f"{r['name']}: PRIS grid connection {p['gridDate'][:10]}")
            if p.get("shutdownDate") and not r["permanent_shutdown"]:
                new_close.append(f"{r['name']}: PRIS shutdown {p['shutdownDate'][:10]}")
        item("ACTION", "Status agrees with IAEA PRIS", drift)
        item("ACTION", "Grid connections recorded", new_grid)
        item("ACTION", "Shutdowns recorded", new_close)
        ours = {r["pris_id"] for r in rows if r["pris_id"]}
        missing = [f"{p['unitName']} ({p['countryName']}, {p['statusName']})" for p in pris.values()
                   if p["id"] not in ours and p["unitName"] not in MISSING_EXCEPTIONS and p["statusName"] in ("Operational", "Under Construction", "Suspended Operation")]
        item("ACTION", "Every PRIS operating / under-construction unit is in the DB", missing)

    # 3. Dates that time has passed (some columns hold bare years as integers: compare years, not strings)
    item("ACTION", "Under-construction reactors with an expected date already passed",
         [f"{r['n']}: {r['d']}" for r in q(
             "SELECT plant_name || ' ' || unit_number AS n, COALESCE(grid_connection, commercial_operation) AS d "
             "FROM reactors WHERE status = 'Under Construction' AND COALESCE(grid_connection, commercial_operation) <= date('now')")])
    item("WARN", "Under-construction reactors started more than 12 years ago (stalled or stale?)",
         [f"{r['n']}: started {r['s']}" for r in q(
             "SELECT plant_name || ' ' || unit_number AS n, construction_start AS s FROM reactors "
             "WHERE status = 'Under Construction' AND construction_start < date('now', '-12 years')")])
    item("ACTION", "Operating reactors whose recorded licence end has passed",
         [f"{r['n']}: {r['d']}" for r in q(
             "SELECT plant_name || ' ' || unit_number AS n, licensed_until AS d FROM reactors "
             "WHERE status = 'Operational' AND licensed_until IS NOT NULL "
             "AND CAST(substr(CAST(licensed_until AS TEXT), 1, 4) AS INTEGER) < CAST(strftime('%Y', 'now') AS INTEGER) "
             "ORDER BY licensed_until")],
         "(licence renewed, or reactor closed?)")
    item("ACTION", "Operating reactors whose recorded planned retirement has passed",
         [f"{r['n']}: {r['d']}" for r in q(
             "SELECT plant_name || ' ' || unit_number AS n, planned_retirement AS d FROM reactors "
             "WHERE status = 'Operational' AND planned_retirement IS NOT NULL "
             "AND CAST(substr(CAST(planned_retirement AS TEXT), 1, 4) AS INTEGER) < CAST(strftime('%Y', 'now') AS INTEGER) "
             "ORDER BY planned_retirement")])
    item("ACTION", "Planned projects whose expected construction start has passed",
         [f"{r['n']}: {r['d']}" for r in q(
             "SELECT project_name || ' ' || COALESCE(unit_number, '') AS n, expected_construction_start AS d "
             "FROM planned_reactors WHERE CAST(expected_construction_start AS TEXT) < strftime('%Y', 'now')")],
         "(did construction start? move to reactors)")
    item("ACTION", "Suspended reactors: check for restarts",
         [r["n"] for r in q("SELECT plant_name || ' ' || unit_number AS n FROM reactors WHERE status = 'Suspended'")]
         if today.month in (1, 4, 7, 10) else [], "(quarterly reminder)")

    # 4. Generation coverage for the latest complete year
    y = today.year - 1 if today.month >= 7 else today.year - 2
    try:
        rows = q("""SELECT c.name AS country, c.code, COALESCE(SUM(g.electricity_gwh), 0) / 1000.0 AS ours,
                           (SELECT value FROM external_series e WHERE e.series = 'nuclear_generation_twh'
                              AND e.country_code = c.code AND e.year = ?) AS published
                    FROM countries c JOIN reactors r ON r.country_id = c.id
                    LEFT JOIN generation_annual g ON g.reactor_id = r.id AND g.year = ?
                    GROUP BY c.id HAVING published > 1""", y, y)
        # Ours is net (PRIS), published is gross: about 0.93-0.98 is normal.
        bad = [f"{r['country']}: ours {r['ours']:.1f} TWh vs published {r['published']:.1f} ({r['ours'] / r['published']:.2f})"
               for r in rows if not 0.88 <= r["ours"] / r["published"] <= 1.02]
        item("ACTION", f"Country generation {y} within 0.88-1.02 of published (net vs gross)", bad)
    except sqlite3.OperationalError:
        pass
    silent = q("""SELECT r.plant_name || ' ' || r.unit_number AS n FROM reactors r
                  WHERE r.status = 'Operational' AND r.grid_connection < ?
                    AND NOT EXISTS (SELECT 1 FROM generation_annual g WHERE g.reactor_id = r.id AND g.year = ?)""",
               f"{y}-01-01", y)
    item("WARN", f"Operating reactors with no generation row for {y}", [r["n"] for r in silent],
         "(idle all year, or data missing?)")

    lines.append(f"\n{n_action} ACTION items")
    text = "\n".join(lines)
    print(text)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text + "\n", encoding="utf-8")
    sys.exit(1 if n_action else 0)


if __name__ == "__main__":
    main()
