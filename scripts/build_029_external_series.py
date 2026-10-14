"""Build migration 029: external benchmark series + IAEA suspension dates.

Purpose: homepage world totals (generation, share of electricity) must come from a published series,
  not from scaling up incomplete per-reactor rows; the fleet count must drop idle (suspended) reactors
  from the year they went idle. Both facts get a DB home so every chart reads one source.
Inputs:  audit/owid/nuclear-energy-generation.csv, audit/owid/electricity-generation.csv
           (Our World in Data grapher CSVs, downloaded 2026-10-14; citation: "Ember (2026); Energy Institute -
           Statistical Review of World Energy (2026) - with major processing by Our World in Data")
         audit/pris_api/all_reactors.json (IAEA PRIS API pull 2026-10-13; latestSuspendedOperationsDate)
         nuclear_reactors.db (read-only, to match pris_id)
Outputs: migrations/029_external_series_and_suspension.sql
Usage:   python scripts/build_029_external_series.py
last_run: 2026-10-14
"""
import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CITE = "Ember (2026); Energy Institute - Statistical Review of World Energy (2026); via Our World in Data"
RETRIEVED = "2026-10-14"


def rows(fname, col, series):
    out = []
    with open(ROOT / "audit" / "owid" / fname, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if not r["code"] or not r[col] or int(r["year"]) < 1965:
                continue
            code = "WLD" if r["code"] == "OWID_WRL" else r["code"]
            if len(code) != 3:
                continue
            out.append((series, code, r["entity"], int(r["year"]), float(r[col])))
    return out


def q(s):
    return "'" + s.replace("'", "''") + "'"


def main():
    data = rows("nuclear-energy-generation.csv", "nuclear_generation__twh", "nuclear_generation_twh") + \
        rows("electricity-generation.csv", "total_generation__twh", "electricity_generation_twh")
    pris = {r["id"]: r for r in json.load(open(ROOT / "audit/pris_api/all_reactors.json", encoding="utf-8"))}
    db = sqlite3.connect(f"file:{ROOT / 'nuclear_reactors.db'}?mode=ro", uri=True)
    susp = []
    for rid, pid, name, unit in db.execute(
            "SELECT id, pris_id, plant_name, unit_number FROM reactors WHERE status = 'Suspended'"):
        d = (pris.get(pid) or {}).get("latestSuspendedOperationsDate")
        if d:
            susp.append((rid, d[:10], name, unit))

    lines = [
        "-- 029_external_series_and_suspension.sql",
        f"-- Date: {RETRIEVED}",
        "-- Description: (1) external_series: published nuclear generation and total electricity generation",
        "--   (TWh) by country and World (code WLD), 1965-2025. Homepage world totals read this instead of",
        "--   scaling up incomplete generation_annual rows (that method put 2025 at ~2,967 TWh vs 2,812 published).",
        f"--   Source: {CITE}; retrieved {RETRIEVED}. OWID nuclear-energy-generation + electricity-generation CSVs.",
        "-- (2) reactors.suspended_since: date operation was suspended, for reactors with status Suspended,",
        "--   from IAEA PRIS latestSuspendedOperationsDate (pris-stats.iaea.org API pull 2026-10-13).",
        "--   History charts drop a suspended reactor from the year it went idle.",
        f"-- Affected: CREATE TABLE external_series + {len(data)} INSERTs; ALTER reactors ADD suspended_since;",
        f"--   UPDATE {len(susp)} reactors.",
        "-- Built by scripts/build_029_external_series.py. Backup: nuclear_reactors.db.bak-pre029-20261014",
        "",
        "BEGIN TRANSACTION;",
        "CREATE TABLE IF NOT EXISTS external_series (",
        "    series TEXT NOT NULL, country_code TEXT NOT NULL, entity TEXT, year INTEGER NOT NULL,",
        "    value REAL NOT NULL, source TEXT NOT NULL, retrieved TEXT NOT NULL,",
        "    PRIMARY KEY (series, country_code, year));",
        "ALTER TABLE reactors ADD COLUMN suspended_since TEXT;",
    ]
    for s, code, ent, y, v in data:
        lines.append(f"INSERT INTO external_series VALUES ({q(s)},{q(code)},{q(ent)},{y},{v},{q(CITE)},{q(RETRIEVED)});")
    for rid, d, name, unit in susp:
        lines.append(f"UPDATE reactors SET suspended_since = {q(d)} WHERE id = {rid}; -- {name} {unit}")
    lines.append("COMMIT;")
    out = ROOT / "migrations" / "029_external_series_and_suspension.sql"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out, len(data), "series rows,", len(susp), "suspension dates")


if __name__ == "__main__":
    main()
