"""Build DRAFT migration 031: refresh generation_annual from IAEA PRIS monthly-table sums.

Purpose: turn the PRIS diff (scripts/pris_generation_diff.py) into a reviewable SQL migration. Never
  touches the DB itself (reads it read-only). Rules, applied per reactor-year:
  REPLACE  ours and PRIS both present, PRIS > 0, and the PRIS figure is "eligible": 12 months present,
           OR a partial operating year (grid or shutdown year, by our dates or PRIS dates), OR fewer
           months in a full year but the PRIS annual table agrees with the monthly sum within 1%.
           Also requires CF <= 105% vs historical gross (validator check 14 basis); else HOLD.
           Every replaced row gets source = SOURCE (also rows whose value does not change).
  DELETE_PRE_GRID   our row dated before our grid-connection year and PRIS has no positive row.
           No -1 year tolerance: PRIS has 0 positive rows before a grid year (its own or ours) across
           all 20k reactor-years, and its grid-year months start at the grid month (3 exceptions,
           all inside the grid year). Our pre-grid rows are multi-year runs (e.g. Tianwan 1 1971-88,
           Bugey 4 and 5 byte-identical) -- copied-identity damage, not test generation.
  DELETE_POST_SHUTDOWN  our row after our shutdown year and PRIS has no row (0 cases today).
  DELETE_PRIS_ZERO  ours positive but PRIS reports <= 0 GWh for an eligible year: the DB stores idle
           years by absence (migration 013 convention). Our values there are mostly capacity figures
           written as GWh (Darlington 2 878, Mihama 3 780, Ohi 3/4 1127 for idle years).
  INSERT   PRIS-only, PRIS > 0, eligible, year inside our [grid year, shutdown year], CF guard.
  KEEP_OURS_ONLY  everything else we hold that PRIS lacks (listed, unchanged).
  HOLD     PRIS disagrees but is not eligible (or fails a guard) -- listed for a human.
Inputs:  nuclear_reactors.db (read-only), audit/pris_generation/{reactor_year.csv,reactors_dim.json}
Outputs: migrations/031_pris_generation_refresh.sql (DRAFT, not applied),
         audit/pris_generation/031_actions.tsv (one row per reactor-year acted on or held),
         audit/pris_generation/031_lifetime.tsv (touched reactors: lifetime_generation_gwh vs row sums)
Usage:   python scripts/build_031_pris_generation.py [--db nuclear_reactors.db]
last_run: 2026-10-14
"""
import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pris_generation_diff import PG, ROOT, classify, load  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SOURCE = "IAEA PRIS data browser (pris-stats.iaea.org), pulled 2026-10-14"
BACKUP = "nuclear_reactors.db.bak-pre031-20261014"
OUT_SQL = ROOT / "migrations" / "031_pris_generation_refresh.sql"
CF_MAX = 1.05


def eligible(r):
    """Is the PRIS figure a complete statement of the year? Returns reason or None."""
    if r["basis"] != "monthly":
        return None
    if r["months"] == 12:
        return "12_months"
    if r["partial_year"]:
        return "partial_operating_year"
    a = r["pris_annual"]
    if a is not None and abs(a - r["pris"]) <= max(0.01 * abs(r["pris"]), 0.05):
        return "annual_table_agrees"
    return None


def decide(r):
    """Return (action, reason)."""
    f = r["flags"]
    p, o = r["pris"], r["ours"]
    if o is not None and "before_our_grid_year" in f and (p is None or p <= 0):
        return "DELETE_PRE_GRID", "before our grid year; PRIS has no positive row"
    if o is not None and "after_our_shutdown_year" in f and p is None:
        return "DELETE_POST_SHUTDOWN", "after our shutdown year; PRIS has no row"
    if p is None:
        return ("KEEP_OURS_ONLY", "PRIS has no row") if o is not None else (None, None)
    el = eligible(r)
    if o is None:
        if p <= 0:
            return None, None  # PRIS idle year; DB stores idle by absence -> already consistent
        if not el:
            return "HOLD", f"pris_only but not eligible ({r['months']} months, full year)"
        if "before_our_grid_year" in f or "after_our_shutdown_year" in f:
            return "HOLD", "pris_only outside our operating window (date conflict)"
        if r["cf_pris"] is not None and r["cf_pris"] > CF_MAX:
            return "HOLD", f"pris_only fails CF guard ({r['cf_pris']:.0%} vs gross {r['eff_gross']})"
        return "INSERT", el
    # both present
    if p <= 0:
        if el:
            return "DELETE_PRIS_ZERO", f"PRIS {p:g} GWh ({el}); idle years are stored by absence"
        return "HOLD", f"PRIS {p:g} GWh but not eligible ({r['months']} months)"
    if not el:
        return ("HOLD" if r["cls"] == "differ" else "KEEP_MATCH_INELIGIBLE"), \
            f"PRIS {r['months']} months in a full year; annual table {r['pris_annual']}"
    if r["cf_pris"] is not None and r["cf_pris"] > CF_MAX:
        return "HOLD", f"CF guard: PRIS value is {r['cf_pris']:.0%} of historical gross {r['eff_gross']} MW"
    return "REPLACE", el


def q(s):
    return "'" + s.replace("'", "''") + "'"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "nuclear_reactors.db"))
    a = ap.parse_args()
    reactors, ours, pris, dim = load(a.db)
    recs = classify(reactors, ours, pris, dim)

    acts = []
    for r in recs:
        act, why = decide(r)
        if act is None:
            continue
        sub = act
        if act == "REPLACE":
            new = round(r["pris"], 3)
            d = abs(new - r["ours"])
            sub = "REPLACE_differ" if r["cls"] == "differ" else ("REPLACE_refine" if d >= 0.0005 else "REPLACE_source_only")
        acts.append((sub, why, r))
    cnt = Counter(s for s, _, _ in acts)
    for k in sorted(cnt):
        print(f"  {k}: {cnt[k]}")

    # Lifetime check for touched reactors (rows changed, inserted or deleted -- not source_only).
    changed = {"REPLACE_differ", "REPLACE_refine", "INSERT", "DELETE_PRE_GRID", "DELETE_POST_SHUTDOWN",
               "DELETE_PRIS_ZERO"}
    touched = {r["reactor_id"] for s, _, r in acts if s in changed}
    before, after = defaultdict(float), defaultdict(float)
    for (rid, y), g in ours.items():
        before[rid] += g or 0
    after.update(before)
    for s, _, r in acts:
        rid = r["reactor_id"]
        if s in ("REPLACE_differ", "REPLACE_refine"):
            after[rid] += round(r["pris"], 3) - r["ours"]
        elif s == "INSERT":
            after[rid] += round(r["pris"], 3)
        elif s.startswith("DELETE"):
            after[rid] -= r["ours"]
    import sqlite3
    db = sqlite3.connect(f"file:{Path(a.db).as_posix()}?mode=ro", uri=True)
    life = dict(db.execute("SELECT id, lifetime_generation_gwh FROM reactors"))
    pris_life = defaultdict(float)
    for (pid, y), p in pris.items():
        pris_life[pid] += max(p["gwh"], 0)
    lrows = []
    for rid in sorted(touched):
        # lifetime_generation_gwh holds TWh-scale values (max 367; Atucha 1 = 94.1 vs 108 TWh of rows)
        # despite its name, and no app.py/template reads it. Compare on a TWh basis (x1000).
        lt = life.get(rid) * 1000 if life.get(rid) is not None else None
        b, af = before[rid], after[rid]
        dis = lambda x: lt is not None and lt > 0 and abs(x - lt) / lt > 0.01
        lrows.append([rid, reactors[rid]["name"], reactors[rid]["pris_id"], "" if lt is None else round(lt / 1000, 3),
                      round(b, 1), round(af, 1), round(pris_life.get(reactors[rid]["pris_id"], 0), 1),
                      "yes" if dis(b) else ("n/a" if lt is None else "no"),
                      "yes" if dis(af) else ("n/a" if lt is None else "no")])
    with open(PG / "031_lifetime.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["reactor_id", "name", "pris_id", "lifetime_generation_gwh_raw_value_TWh_scale", "sum_rows_before_031_gwh",
                    "sum_rows_after_031_gwh", "pris_sum_all_years_gwh", "disagrees_before_gt1pct", "disagrees_after_gt1pct"])
        w.writerows(lrows)
    newly = [x for x in lrows if x[7] == "no" and x[8] == "yes"]
    still = [x for x in lrows if x[7] == "yes" and x[8] == "yes"]
    fixed = [x for x in lrows if x[7] == "yes" and x[8] == "no"]
    print(f"  touched reactors {len(touched)}: lifetime newly disagrees {len(newly)}, still disagrees {len(still)}, "
          f"now agrees {len(fixed)}, no lifetime value {sum(1 for x in lrows if x[8] == 'n/a')}")

    with open(PG / "031_actions.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["action", "reason", "reactor_id", "name", "country", "year", "ours_gwh", "pris_gwh",
                    "pris_months", "pris_annual_gwh", "class", "flags"])
        for s, why, r in acts:
            if s == "REPLACE_source_only":
                continue  # 19k identical-value rows; counted in the SQL header, not listed
            w.writerow([s, why, r["reactor_id"], r["name"], r["cc"], r["year"], r["ours"], r["pris"], r["months"],
                        r["pris_annual"], r["cls"], ",".join(r["flags"])])

    # ---------- SQL ----------
    upd = [(s, r) for s, _, r in acts if s.startswith("REPLACE")]
    ins = [r for s, _, r in acts if s == "INSERT"]
    dels = [(s, r) for s, _, r in acts if s.startswith("DELETE")]
    L = [
        "-- 031_pris_generation_refresh.sql",
        "-- Date: 2026-10-14",
        "-- Description: refresh generation_annual from IAEA PRIS per-reactor monthly production",
        "--   (Fact_ReactorMonthlyProduction summed to calendar years; electricity supplied, GWh net),",
        f"--   source: {SOURCE}; Power BI route in audit/pris_generation_route_2026-10-14.md;",
        "--   pull scripts/pris_generation_pull.py -> audit/pris_generation/reactor_year.csv; diff",
        "--   scripts/pris_generation_diff.py -> audit/pris_generation/diff.tsv + summary.md.",
        "--   Adds generation_annual.source (per-row provenance; NULL = pre-031 row of unrecorded origin).",
        "--   Keyed on reactors.pris_id (738 reactors, unique, all present in PRIS Dim_Reactor; ids agree with",
        "--   pris_id_map_2026-07.json except 17 new UC ids with no generation).",
        "-- Rules: see scripts/build_031_pris_generation.py docstring. Row counts by action:",
    ]
    for k in sorted(cnt):
        L.append(f"--   {k:<22} {cnt[k]:>6}")
    L += [
        "--   (REPLACE_* = UPDATE value+source; REPLACE_source_only = value unchanged, source set;",
        "--    KEEP_* and HOLD = no SQL, listed in audit/pris_generation/031_actions.tsv.)",
        f"-- Statements: {len(upd)} UPDATE, {len(ins)} INSERT, {len(dels)} DELETE, 1 ALTER.",
        "-- Each UPDATE/DELETE is guarded on the current value (abs diff < 0.0005), so a row changed since",
        "--   the draft was built is skipped rather than overwritten; re-run the builder if counts drift.",
        "-- Affected: generation_annual (values, rows, new column source). reactors.lifetime_generation_gwh",
        "--   is NOT changed; reactors whose lifetime figure would disagree with their rows: 031_lifetime.tsv.",
        f"-- Backup before applying: {BACKUP}",
        "-- After applying: python scripts/validate_db.py ; python scripts/site_consistency.py",
        "",
        "BEGIN TRANSACTION;",
        "ALTER TABLE generation_annual ADD COLUMN source TEXT;",
        "",
    ]
    S = q(SOURCE)
    for label, items in (("REPLACE_differ", [r for s, r in upd if s == "REPLACE_differ"]),
                         ("REPLACE_refine", [r for s, r in upd if s == "REPLACE_refine"]),
                         ("REPLACE_source_only", [r for s, r in upd if s == "REPLACE_source_only"])):
        L.append(f"-- {label}: {len(items)}")
        for r in items:
            L.append(f"UPDATE generation_annual SET electricity_gwh = {round(r['pris'], 3)!r}, source = {S} "
                     f"WHERE reactor_id = {r['reactor_id']} AND year = {r['year']} "
                     f"AND abs(electricity_gwh - {r['ours']!r}) < 0.0005;")
        L.append("")
    for label in ("DELETE_PRE_GRID", "DELETE_POST_SHUTDOWN", "DELETE_PRIS_ZERO"):
        items = [r for s, r in dels if s == label]
        L.append(f"-- {label}: {len(items)}")
        for r in items:
            L.append(f"DELETE FROM generation_annual WHERE reactor_id = {r['reactor_id']} AND year = {r['year']} "
                     f"AND abs(electricity_gwh - {r['ours']!r}) < 0.0005;  -- {r['name']}")
        L.append("")
    L.append(f"-- INSERT (PRIS-only reactor-years): {len(ins)}")
    for r in ins:
        L.append(f"INSERT INTO generation_annual (reactor_id, year, electricity_gwh, source) VALUES "
                 f"({r['reactor_id']}, {r['year']}, {round(r['pris'], 3)!r}, {S});  -- {r['name']}")
    # Independent-source overrides, applied last (audit/pris_generation/overrides_eia.psv): reactor-years
    # where a national source shows PRIS wrong (e.g. PRIS December 2021 = copy of November for 90 US
    # units; EIA-923 unit data gives the true month). Upsert: update the row, or insert if absent.
    ov_file = PG / "overrides_eia.psv"
    if ov_file.exists():
        ov = list(csv.DictReader(open(ov_file, encoding="utf-8"), delimiter="|"))
        L.append("")
        L.append(f"-- OVERRIDE (independent national source beats PRIS): {len(ov)}  [{ov_file.name}]")
        for o in ov:
            src, rid, yr, val = q(o["source"]), int(o["reactor_id"]), int(o["year"]), round(float(o["gwh_net"]), 3)
            L.append(f"UPDATE generation_annual SET electricity_gwh = {val!r}, source = {src} "
                     f"WHERE reactor_id = {rid} AND year = {yr};  -- {o['name']}: {o['reason']}")
            L.append(f"INSERT INTO generation_annual (reactor_id, year, electricity_gwh, source) "
                     f"SELECT {rid}, {yr}, {val!r}, {src} WHERE NOT EXISTS "
                     f"(SELECT 1 FROM generation_annual WHERE reactor_id = {rid} AND year = {yr});")
    # Rows that are physically impossible (more energy than the gross rating allows between grid
    # connection and year end) and absent from PRIS: audit/pris_generation/impossible_rows.psv.
    imp_file = PG / "impossible_rows.psv"
    if imp_file.exists():
        imp = list(csv.DictReader(open(imp_file, encoding="utf-8"), delimiter="|"))
        L.append("")
        L.append(f"-- DELETE_IMPOSSIBLE (exceeds gross rating x hours since grid connection; not in PRIS): {len(imp)}")
        for o in imp:
            L.append(f"DELETE FROM generation_annual WHERE reactor_id = {int(o['reactor_id'])} AND year = {int(o['year'])} "
                     f"AND abs(electricity_gwh - {float(o['gwh'])!r}) < 0.0005;  -- {o['name']}: {o['reason']}")
    L += ["", "COMMIT;", ""]
    OUT_SQL.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT_SQL} ({len(L)} lines); {PG / '031_actions.tsv'}; {PG / '031_lifetime.tsv'}")


if __name__ == "__main__":
    main()
