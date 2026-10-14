"""Diff generation_annual against IAEA PRIS per-reactor generation (monthly-table sums).

Purpose: classify every reactor-year as match (<=1%) / differ / ours_only / pris_only, flag rows
  outside each reactor's operating window, partial-month PRIS years, and the incomplete latest year;
  compare country x year totals (ours vs PRIS vs published Ember/EI series). Feeds the migration-031
  builder (scripts/build_031_pris_generation.py imports load() and classify() from here).
Inputs:  nuclear_reactors.db (--db, opened read-only), audit/pris_generation/reactor_year.csv +
         reactors_dim.json (scripts/pris_generation_pull.py), published series table external_series
         (--series-db; it lives only in the scratch DB until migration 029 is applied),
         optional --after-db (a copy with 031 applied) and --consistency-log (site_consistency output).
Outputs: audit/pris_generation/diff.tsv, audit/pris_generation/summary.md
Usage:   python scripts/pris_generation_diff.py --series-db <test.db> [--after-db <test031.db>]
             [--consistency-log <file>]
last_run: 2026-10-14
"""
import argparse
import csv
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
PG = ROOT / "audit" / "pris_generation"
YEARS = range(2015, 2026)
LATEST_PRIS_YEAR = 2025


def ro(path):
    return sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True)


def yr(d):
    return int(d[:4]) if d else None


def load(db_path):
    """Return (reactors by our id, ours {(rid, year): gwh}, pris {(pris_id, year): row}, dim by pris_id)."""
    db = ro(db_path)
    reactors = {}
    for rid, pid, name, cc, status, grid, shut, gross in db.execute(
            "SELECT r.id, r.pris_id, r.plant_name || ' ' || COALESCE(r.unit_number, ''), co.code, r.status, "
            "r.grid_connection, r.permanent_shutdown, r.gross_capacity_mw "
            "FROM reactors r LEFT JOIN countries co ON co.id = r.country_id"):
        reactors[rid] = {"id": rid, "pris_id": pid, "name": name.strip(), "cc": cc, "status": status,
                         "grid": grid, "shut": shut, "gross": gross}
    ours = {(r, y): g for r, y, g in db.execute("SELECT reactor_id, year, electricity_gwh FROM generation_annual")}
    caps = defaultdict(list)
    for r, d, g in db.execute("SELECT reactor_id, effective_date, gross_capacity_mw FROM capacity_changes "
                              "WHERE gross_capacity_mw IS NOT NULL ORDER BY effective_date"):
        caps[r].append((d, g))
    for r in reactors.values():
        r["caps"] = caps.get(r["id"], [])
    dim = {d["id"]: d for d in json.loads((PG / "reactors_dim.json").read_text(encoding="utf-8"))["rows"]}
    pris = {}
    for row in csv.DictReader(open(PG / "reactor_year.csv", encoding="utf-8")):
        m = row["gwh_net_from_monthly"]
        a = row["gwh_net_annual_table"]
        if m == "" and a == "":
            continue  # PRIS row with no energy value at all (4 cases): treat as no PRIS data
        pris[(int(row["pris_reactor_id"]), int(row["year"]))] = {
            "gwh": float(m) if m != "" else float(a), "basis": "monthly" if m != "" else "annual_only",
            "months": int(row["months_present"]), "annual": float(a) if a != "" else None,
            "lf": float(row["load_factor"]) if row["load_factor"] != "" else None}
    return reactors, ours, pris, dim


def eff_gross(r, year):
    """Historical gross MW in force at year end (capacity_changes, else current) -- validator check 14 basis."""
    g = r["gross"]
    for d, cap in r["caps"]:
        if d <= f"{year}-12-31":
            g = cap
    return g


def window_hours(r, year):
    """Hours in `year` between our grid connection and our shutdown (whole year if dates are absent)."""
    from datetime import datetime
    start, end = datetime(year, 1, 1), datetime(year + 1, 1, 1)
    if r["grid"] and r["grid"][:4] == str(year):
        start = datetime.fromisoformat(r["grid"][:10])
    if r["shut"] and r["shut"][:4] == str(year):
        end = datetime.fromisoformat(r["shut"][:10])
    return max((end - start).total_seconds() / 3600, 24.0)


def classify(reactors, ours, pris, dim):
    """One record per reactor-year in ours U PRIS (matched reactors only; PRIS-only reactors listed separately)."""
    by_pid = {r["pris_id"]: r for r in reactors.values() if r["pris_id"]}
    out = []
    keys = {(rid, y) for rid, y in ours}
    for (pid, y) in pris:
        if pid in by_pid:
            keys.add((by_pid[pid]["id"], y))
    for rid, y in sorted(keys):
        r = reactors[rid]
        p = pris.get((r["pris_id"], y)) if r["pris_id"] else None
        o = ours.get((rid, y))
        d = dim.get(r["pris_id"], {})
        pg, ps = yr(d.get("grid_date")), yr(d.get("shutdown_date"))
        og, osd = yr(r["grid"]), yr(r["shut"])
        if o is not None and p is not None:
            diff = o - p["gwh"]
            pct = diff / abs(p["gwh"]) * 100 if p["gwh"] else None
            cls = "match" if abs(diff) <= 0.01 * abs(p["gwh"]) or abs(diff) < 0.05 else "differ"
        elif o is not None:
            diff = pct = None
            cls = "ours_only"
        else:
            diff = pct = None
            cls = "pris_only"
        flags = []
        if og is not None and y < og:
            flags.append("before_our_grid_year")
        if osd is not None and y > osd:
            flags.append("after_our_shutdown_year")
        if pg is not None and y < pg:
            flags.append("before_pris_grid_year")
        if ps is not None and y > ps:
            flags.append("after_pris_shutdown_year")
        partial_year = y in {og, osd, pg, ps}
        if partial_year:
            flags.append("partial_operating_year")
        full_year = (og is not None and og < y and (osd is None or y < osd))
        if p is not None and p["basis"] == "monthly" and p["months"] < 12 and full_year:
            flags.append("months_lt_12_in_full_year")
        if p is not None and p["basis"] == "annual_only":
            flags.append("pris_annual_table_only")
        if p is not None and p["gwh"] <= 0:
            flags.append("pris_nonpositive")
        if p is not None and p["annual"] is not None and p["basis"] == "monthly" and \
                abs(p["annual"] - p["gwh"]) > max(0.01 * abs(p["gwh"]), 0.05):
            flags.append("pris_monthly_ne_annual")
        if y == LATEST_PRIS_YEAR:
            flags.append("latest_pris_year")
        if og != pg and r["pris_id"]:
            flags.append("grid_year_ours_ne_pris")
        g = eff_gross(r, y)
        cf_pris = p["gwh"] * 1000 / (g * 8760) if (p and g) else None
        hrs = window_hours(r, y)
        cfw_ours = o * 1000 / (g * hrs) if (o is not None and g) else None
        cfw_pris = p["gwh"] * 1000 / (g * hrs) if (p and g) else None
        if (cfw_ours or 0) > 1.05:
            flags.append("ours_exceeds_gross_x_hours_in_window")
        if (cfw_pris or 0) > 1.05:
            flags.append("pris_exceeds_gross_x_hours_in_window")
        out.append({"reactor_id": rid, "pris_id": r["pris_id"], "name": r["name"], "pris_name": d.get("unit_name", ""),
                    "cc": r["cc"], "status": r["status"], "grid": r["grid"], "shut": r["shut"],
                    "pris_grid": d.get("grid_date"), "pris_shut": d.get("shutdown_date"), "year": y,
                    "ours": o, "pris": p["gwh"] if p else None, "basis": p["basis"] if p else "",
                    "months": p["months"] if p else "", "pris_annual": p["annual"] if p else None,
                    "lf": p["lf"] if p else None, "diff": diff, "pct": pct, "cls": cls, "flags": flags,
                    "partial_year": partial_year, "full_year": full_year, "eff_gross": g, "cf_pris": cf_pris,
                    "cfw_ours": cfw_ours, "cfw_pris": cfw_pris})
    return out


def fmt(v, nd=1):
    return "" if v is None else f"{v:,.{nd}f}"


def published(series_db):
    db = ro(series_db)
    return {(cc, y): v for cc, y, v in db.execute(
        "SELECT country_code, year, value FROM external_series WHERE series = 'nuclear_generation_twh'")}


def country_year(db_path):
    db = ro(db_path)
    t = defaultdict(float)
    for cc, y, g in db.execute("SELECT co.code, g.year, SUM(g.electricity_gwh) FROM generation_annual g "
                               "JOIN reactors r ON r.id = g.reactor_id JOIN countries co ON co.id = r.country_id "
                               "GROUP BY co.code, g.year"):
        t[(cc, y)] += g / 1000
    return t


def ratio_table(lines, ours_t, pub, ccs, title):
    lines += [f"### {title}", "",
              "Cells: ours / published (TWh ratio). Blank = no published value or no generation. "
              "Published = Ember/EI via OWID (mostly gross basis; PRIS and our rows are net, so ~0.93-0.97 is "
              "the expected 'agreement' band).", "",
              "| Country | " + " | ".join(str(y) for y in YEARS) + " |", "|---|" + "---|" * len(YEARS)]
    cells = []
    for cc in ccs:
        row = []
        for y in YEARS:
            o, p = ours_t.get((cc, y), 0), pub.get((cc, y))
            if p and p > 0:
                row.append(f"{o / p:.2f}")
                cells.append((cc, y, o, p))
            else:
                row.append("")
        lines.append(f"| {cc} | " + " | ".join(row) + " |")
    o = [sum(ours_t.get((c, y), 0) for c in ccs) for y in YEARS]
    lines.append("| **All (ours) / WLD** | " + " | ".join(
        f"{a / pub[('WLD', y)]:.2f}" if pub.get(("WLD", y)) else "" for a, y in zip(o, YEARS)) + " |")
    lines.append("")
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "nuclear_reactors.db"))
    ap.add_argument("--series-db", required=True)
    ap.add_argument("--after-db")
    ap.add_argument("--consistency-log")
    a = ap.parse_args()
    reactors, ours, pris, dim = load(a.db)
    recs = classify(reactors, ours, pris, dim)

    cols = ["reactor_id", "pris_id", "name", "pris_name", "cc", "status", "grid", "shut", "pris_grid", "pris_shut",
            "year", "ours", "pris", "basis", "months", "pris_annual", "lf", "diff", "pct", "cls", "flags"]
    with open(PG / "diff.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["reactor_id", "pris_id", "name", "pris_unit_name", "country", "status", "our_grid_connection",
                    "our_permanent_shutdown", "pris_grid_date", "pris_shutdown_date", "year", "ours_gwh",
                    "pris_gwh_monthly_sum", "pris_basis", "pris_months_present", "pris_gwh_annual_table",
                    "pris_load_factor", "ours_minus_pris_gwh", "pct_diff", "class", "flags"])
        for r in recs:
            w.writerow([("" if r[c] is None else round(r[c], 3) if isinstance(r[c], float) else
                         ",".join(r[c]) if isinstance(r[c], list) else r[c]) for c in cols])
    cnt = defaultdict(int)
    for r in recs:
        cnt[r["cls"]] += 1
    print("classes:", dict(cnt))

    # ---------- summary.md ----------
    by_pid = {r["pris_id"] for r in reactors.values() if r["pris_id"]}
    gen_reactors = {rid for rid, _ in ours}
    unmatched_ours = [r for r in reactors.values() if not r["pris_id"]]
    pris_gen_ids = {pid for pid, _ in pris}
    unmatched_pris = sorted(pid for pid in pris_gen_ids if pid not in by_pid)
    pmap = json.loads((ROOT / "pris_id_map_2026-07.json").read_text(encoding="utf-8"))
    not_in_map = [r for r in reactors.values() if r["pris_id"] and str(r["pris_id"]) not in pmap]
    map_name_bad = [(r["name"], r["pris_id"], pmap[str(r["pris_id"])], dim.get(r["pris_id"], {}).get("unit_name"))
                    for r in reactors.values() if r["pris_id"] and pmap.get(str(r["pris_id"])) and
                    dim.get(r["pris_id"]) and pmap[str(r["pris_id"])].replace("&#39;", "'") != dim[r["pris_id"]]["unit_name"]]
    pub = published(a.series_db)
    ours_t = country_year(a.db)
    pris_t = defaultdict(float)
    for r in recs:
        if r["pris"] is not None and r["pris"] > 0:
            pris_t[(r["cc"], r["year"])] += r["pris"] / 1000
    ccs = sorted({cc for (cc, y) in ours_t if y in YEARS} | {cc for (cc, y) in pris_t if y in YEARS})

    L = ["# PRIS generation diff (2026-10-14)", "",
         "Built by `scripts/pris_generation_diff.py` from `audit/pris_generation/reactor_year.csv` "
         "(IAEA PRIS data browser, pris-stats.iaea.org, Power BI monthly table summed to years; pulled 2026-10-14 by "
         "`scripts/pris_generation_pull.py`) against `nuclear_reactors.db` (read-only). Row-level detail: "
         "`audit/pris_generation/diff.tsv`. PRIS energy = electricity supplied, GWh net.", "",
         "## Matching", "",
         f"- Our reactors: {len(reactors)}; with pris_id: {len(reactors) - len(unmatched_ours)}; pris_id duplicates: "
         f"{len(by_pid) != len(reactors) - len(unmatched_ours)}.",
         f"- Our reactors without pris_id (all generation rows for them are ours_only): " +
         "; ".join(f"{r['name']} ({r['status']}, {sum(1 for k in ours if k[0] == r['id'])} gen rows)"
                   for r in unmatched_ours) + ".",
         f"- PRIS reactors with generation that match none of ours: {len(unmatched_pris)}" +
         (": " + ", ".join(f"{p} {dim.get(p, {}).get('unit_name')}" for p in unmatched_pris) if unmatched_pris else "") + ".",
         f"- Our pris_ids absent from `pris_id_map_2026-07.json`: {len(not_in_map)} (all Under Construction, ids > 2100 "
         f"added in Oct 2026; none has generation): {', '.join(r['name'] for r in not_in_map)}.",
         f"- Our pris_ids whose map name differs from the current PRIS Dim_Reactor name: {len(map_name_bad)}"
         + (": " + "; ".join(f"{n} ({p}: map {m} / PRIS {d})" for n, p, m, d in map_name_bad) if map_name_bad else "") + ".",
         f"- Reactors with our generation rows: {len(gen_reactors)}; PRIS reactors with generation: {len(pris_gen_ids)}.",
         "", "## Classes (all reactor-years)", "",
         "| Class | Rows | Ours GWh | PRIS GWh |", "|---|---|---|---|"]
    for c in ("match", "differ", "ours_only", "pris_only"):
        rs = [r for r in recs if r["cls"] == c]
        L.append(f"| {c} | {len(rs):,} | {fmt(sum(r['ours'] or 0 for r in rs), 0)} | "
                 f"{fmt(sum(r['pris'] or 0 for r in rs), 0)} |")
    po = [r for r in recs if r["cls"] == "pris_only"]
    L += ["", f"pris_only splits into {sum(1 for r in po if r['pris'] > 0)} positive rows and "
              f"{sum(1 for r in po if r['pris'] <= 0)} rows where PRIS reports <= 0 GWh (the DB stores idle years by absence, "
              "so those are consistent, not gaps).", ""]
    dif = [r for r in recs if r["cls"] == "differ"]
    nz = [r for r in dif if r["pris"] <= 0]
    L += [f"differ: {len(dif)} rows, of which {len(nz)} have PRIS <= 0 GWh while ours is positive "
          f"(ours sum {fmt(sum(r['ours'] for r in nz), 0)} GWh).", ""]
    bands = [(1, 2), (2, 5), (5, 10), (10, 25), (25, 50), (50, 1e9)]
    L += ["| abs % diff (PRIS > 0) | rows |", "|---|---|"]
    for lo, hi in bands:
        L.append(f"| {lo}-{hi if hi < 1e9 else 'inf'}% | "
                 f"{sum(1 for r in dif if r['pris'] > 0 and lo < abs(r['pct']) <= hi)} |")
    L.append("")

    # Country x year
    L += ["## Country x year, 2015-2025 (TWh): ours / PRIS / published", "",
          "Each cell: ours / PRIS (monthly sums, matched reactors) / published (Ember/EI via OWID; "
          "`external_series`, read from the scratch DB). Published is mostly gross-basis, so it runs ~3-7% above net.", "",
          "| Country | " + " | ".join(str(y) for y in YEARS) + " |", "|---|" + "---|" * len(YEARS)]
    for cc in ccs:
        L.append(f"| {cc} | " + " | ".join(
            f"{ours_t.get((cc, y), 0):.1f} / {pris_t.get((cc, y), 0):.1f} / "
            f"{pub[(cc, y)]:.1f}" if (cc, y) in pub else
            f"{ours_t.get((cc, y), 0):.1f} / {pris_t.get((cc, y), 0):.1f} / -" for y in YEARS) + " |")
    L.append("| **World** | " + " | ".join(
        f"{sum(ours_t.get((c, y), 0) for c in ccs):.0f} / {sum(pris_t.get((c, y), 0) for c in ccs):.0f} / "
        f"{pub.get(('WLD', y), 0):.0f}" for y in YEARS) + " |")
    L.append("")
    before_cells = ratio_table(L, ours_t, pub, ccs, "Ratio before refresh (ours today / published)")

    # Operating-window lists
    def lst(title, rows, extra=None):
        L.extend([f"### {title} ({len(rows)})", ""])
        if not rows:
            L.extend(["(none)", ""])
            return
        L.extend(["| Reactor | Year | Our grid / shutdown | PRIS grid / shutdown | Ours GWh | PRIS GWh | Months | Note |",
                  "|---|---|---|---|---|---|---|---|"])
        for r in rows:
            L.append(f"| {r['name']} | {r['year']} | {r['grid'] or '-'} / {r['shut'] or '-'} | "
                     f"{r['pris_grid'] or '-'} / {r['pris_shut'] or '-'} | {fmt(r['ours'])} | {fmt(r['pris'])} | "
                     f"{r['months']} | {extra(r) if extra else ''} |")
        L.append("")

    L += ["## Rows outside the operating window", ""]
    pre = [r for r in recs if r["ours"] is not None and "before_our_grid_year" in r["flags"]]
    post = [r for r in recs if r["ours"] is not None and "after_our_shutdown_year" in r["flags"]]
    runs = defaultdict(list)
    for r in pre:
        runs[r["reactor_id"]].append(r)
    L += [f"### Our rows dated before our grid-connection year ({len(pre)} rows, {len(runs)} reactors)", "",
          "PRIS has a positive row for none of them (PRIS has 0 positive rows before any grid year, its own or ours). "
          "They are multi-year runs, often byte-identical across sister units (Bugey 4 = Bugey 5): copied-identity "
          "damage. Row-level detail: diff.tsv, flag before_our_grid_year.", "",
          "| Reactor | Our grid connection | PRIS grid date | Years | Rows | Ours GWh | PRIS rows (<=0) |",
          "|---|---|---|---|---|---|---|"]
    for rid, rs in sorted(runs.items(), key=lambda kv: kv[1][0]["name"]):
        L.append(f"| {rs[0]['name']} | {rs[0]['grid']} | {rs[0]['pris_grid']} | {rs[0]['year']}-{rs[-1]['year']} | "
                 f"{len(rs)} | {fmt(sum(r['ours'] for r in rs), 0)} | {sum(1 for r in rs if r['pris'] is not None)} |")
    L.append("")
    lst("Our rows dated after our shutdown year", post,
        lambda r: "PRIS has it" if r["pris"] is not None else "PRIS has no row")
    ppre = [r for r in recs if r["pris"] is not None and r["pris"] > 0 and
            ("before_pris_grid_year" in r["flags"] or "before_our_grid_year" in r["flags"])]
    ppost = [r for r in recs if r["pris"] is not None and r["pris"] > 0 and
             ("after_pris_shutdown_year" in r["flags"] or "after_our_shutdown_year" in r["flags"])]
    lst("PRIS rows (positive) dated before a grid-connection year (ours or PRIS)", ppre)
    lst("PRIS rows (positive) dated after a shutdown year (ours or PRIS)", ppost)

    m12 = [r for r in recs if "months_lt_12_in_full_year" in r["flags"]]
    L += [f"## PRIS months_present < 12 in a full operating year ({len(m12)})", "",
          "Full operating year = strictly between our grid year and our shutdown year. Missing months can mean "
          "an outage month with no row (PRIS omits some idle months) or a reporting gap. `annual` = annual-table value.", "",
          "| Reactor | Year | Months | PRIS monthly sum | PRIS annual | Ours | Class |", "|---|---|---|---|---|---|---|"]
    for r in m12:
        L.append(f"| {r['name']} | {r['year']} | {r['months']} | {fmt(r['pris'])} | {fmt(r['pris_annual'])} | "
                 f"{fmt(r['ours'])} | {r['cls']} |")
    L.append("")

    # Incomplete latest year
    op = [x for x in reactors.values() if x["grid"] and yr(x["grid"]) <= LATEST_PRIS_YEAR and
          (not x["shut"] or yr(x["shut"]) >= LATEST_PRIS_YEAR)]
    have_p = {r["reactor_id"] for r in recs if r["year"] == LATEST_PRIS_YEAR and r["pris"] is not None}
    have_o = {r["reactor_id"] for r in recs if r["year"] == LATEST_PRIS_YEAR and r["ours"] is not None}
    nopris = [x for x in op if x["id"] not in have_p]
    L += [f"## Incomplete latest year ({LATEST_PRIS_YEAR})", "",
          f"PRIS has no data after {LATEST_PRIS_YEAR}; our DB has no rows after "
          f"{max(y for _, y in ours)} either, so 2026 is simply not covered yet.",
          f"Reactors in operation during {LATEST_PRIS_YEAR} (grid by then, not shut before it): {len(op)}. "
          f"PRIS rows: {len(have_p & {x['id'] for x in op})}; our rows: {len(have_o & {x['id'] for x in op})}.",
          f"In operation but no PRIS {LATEST_PRIS_YEAR} row ({len(nopris)}): " +
          ", ".join(f"{x['name']}{' (ours has it)' if x['id'] in have_o else ''}" for x in
                    sorted(nopris, key=lambda x: (x['cc'] or '', x['name']))) + ".", ""]
    p25 = [r for r in recs if r["year"] == LATEST_PRIS_YEAR and r["basis"] == "monthly" and r["months"] < 12
           and not r["partial_year"]]
    L += [f"PRIS {LATEST_PRIS_YEAR} rows with < 12 months and no grid/shutdown that year ({len(p25)}): " +
          ", ".join(f"{r['name']} ({r['months']} mo)" for r in p25) + ".", ""]

    if a.after_db:
        acts = list(csv.DictReader(open(PG / "031_actions.tsv", encoding="utf-8"), delimiter="\t"))
        sql_lines = (ROOT / "migrations" / "031_pris_generation_refresh.sql").read_text(encoding="utf-8").splitlines()[:40]
        counts = [ln[3:].split() for ln in sql_lines
                  if ln.startswith("--   ") and len(ln[3:].split()) == 2 and ln[3:].split()[1].isdigit()]
        L += ["## Draft migration 031 (NOT applied to nuclear_reactors.db)", "",
              "`migrations/031_pris_generation_refresh.sql`, built by `scripts/build_031_pris_generation.py` "
              "(rules in its docstring). Per-row actions: `audit/pris_generation/031_actions.tsv` (all but the "
              "unchanged-value REPLACE_source_only rows). Every written row gets source = "
              "'IAEA PRIS data browser (pris-stats.iaea.org), pulled 2026-10-14' in a new generation_annual.source column.", "",
              "| Action | Rows |", "|---|---|"]
        for k, v in counts:
            L.append(f"| {k} | {v} |")
        L.append("")
        hold = [x for x in acts if x["action"] == "HOLD"]
        L += [f"### HOLD - PRIS value not written ({len(hold)})", "",
              "| Reactor | Year | Ours | PRIS | Reason |", "|---|---|---|---|---|"]
        L += [f"| {x['name']} | {x['year']} | {x['ours_gwh']} | {x['pris_gwh']} | {x['reason']} |" for x in hold]
        keep = [x for x in acts if x["action"] == "KEEP_OURS_ONLY"]
        L += ["", f"### KEEP_OURS_ONLY - our rows PRIS lacks, left unchanged ({len(keep)})", "",
              "`implausible` = exceeds 105% of gross capacity x the hours between our grid date and year end.", "",
              "| Reactor | Country | Year | Ours GWh | Flags |", "|---|---|---|---|---|"]
        L += [f"| {x['name']} | {x['country']} | {x['year']} | {x['ours_gwh']} | "
              f"{'**implausible**, ' if 'ours_exceeds_gross_x_hours_in_window' in x['flags'] else ''}"
              f"{x['flags']} |" for x in keep]
        zero = [x for x in acts if x["action"] == "DELETE_PRIS_ZERO"]
        byc = sorted(((c, sum(1 for x in zero if x["country"] == c)) for c in {x["country"] for x in zero}),
                     key=lambda t: -t[1])
        L += ["", f"### DELETE_PRIS_ZERO ({len(zero)} rows, {fmt(sum(float(x['ours_gwh']) for x in zero) / 1000)} TWh)", "",
              "Ours positive, PRIS 0 GWh for a complete year. Most of our values are capacity figures written as GWh "
              "(Darlington 2 878, Mihama 3 780, Ohi 3/4 1127, Kakrapar 202 in refurbishment or idle years). By country: " +
              ", ".join(f"{c} {n}" for c, n in byc) + ".", ""]
        life = list(csv.DictReader(open(PG / "031_lifetime.tsv", encoding="utf-8"), delimiter="\t"))
        newly = [x for x in life if x["disagrees_before_gt1pct"] == "no" and x["disagrees_after_gt1pct"] == "yes"]
        n_before = sum(1 for x in life if x["disagrees_before_gt1pct"] == "yes")
        n_still = sum(1 for x in life if x["disagrees_before_gt1pct"] == "yes" and x["disagrees_after_gt1pct"] == "yes")
        n_fixed = sum(1 for x in life if x["disagrees_before_gt1pct"] == "yes" and x["disagrees_after_gt1pct"] == "no")
        n_na = sum(1 for x in life if x["disagrees_after_gt1pct"] == "n/a")
        L += ["### reactors.lifetime_generation_gwh (not changed by 031)", "",
              f"Touched reactors (a value changed, or a row inserted/deleted): {len(life)}. The column holds TWh-scale "
              "values despite its name (max 367; no app.py route or template reads it), so it is compared x1000. "
              f"It already disagrees (>1%) with the row sums for {n_before} of them before 031 (median ratio "
              f"rows/lifetime ~1.18: a stale snapshot). After 031: still disagree {n_still}, newly disagree "
              f"{len(newly)}, newly agree {n_fixed}, no value {n_na}. Full list: `031_lifetime.tsv`.", ""]
        if newly:
            L += ["| Reactor | lifetime (TWh) | rows before (GWh) | rows after (GWh) |", "|---|---|---|---|"]
            L += [f"| {x['name']} | {x['lifetime_generation_gwh_raw_value_TWh_scale']} | {x['sum_rows_before_031_gwh']} | "
                  f"{x['sum_rows_after_031_gwh']} |" for x in newly]
            L.append("")
        rd = sorted((x for x in acts if x["action"] == "REPLACE_differ"), key=lambda x: (x["country"], int(x["year"])))
        step = max(len(rd) // 12, 1)
        samp = rd[::step][:12]
        gross = {r["reactor_id"]: r for r in recs}
        L += ["### Invariant scan and sample (Data Change Protocol 5-6)", "",
              "- Join key: pris_id unique (738 reactors); every id with generation exists in PRIS Dim_Reactor; ids agree "
              "with pris_id_map_2026-07.json (name differences are PRIS spelling/Taiwan suffix only, listed above).",
              "- Post-shutdown rows: 0 before, 0 after (validator check 13 OK on test031.db).",
              "- CF range: validator check 14 (CF > 105% of historical gross) OK on test031.db; builder holds any PRIS "
              "value above that (5 G3 3 rows).",
              "- Independent anchor (recipe): EIA-923 2024 Byron-2 10,204,282 MWh = PRIS 10,204.3 GWh; world 2024 PRIS "
              "monthly sum 2,617.5 TWh = IAEA published 2,617 TWh.",
              f"- Sample: every {step}th REPLACE_differ row by country/year (12 rows). Check is PRIS-internal (monthly sum "
              "vs annual table) plus implied net load factor; it is not an independent source.", "",
              "| Reactor | Year | Ours | PRIS monthly | PRIS annual | Months | PRIS LF % | Reason |",
              "|---|---|---|---|---|---|---|---|"]
        for x in samp:
            L.append(f"| {x['name']} | {x['year']} | {x['ours_gwh']} | {x['pris_gwh']} | {x['pris_annual_gwh']} | "
                     f"{x['pris_months']} | {next((fmt(r['lf']) for r in recs if r['reactor_id'] == int(x['reactor_id']) and r['year'] == int(x['year'])), '')} | {x['reason']} |")
        L.append("")
        L += ["## After migration 031 (applied to a scratch copy only)", ""]
        after_t = country_year(a.after_db)
        after_cells = ratio_table(L, after_t, pub, ccs, "Ratio after refresh (ours after 031 / published)")
        med = {}
        for cc in ccs:
            v = sorted(o / p for c, y, o, p in after_cells if c == cc and o > 0)
            med[cc] = v[len(v) // 2] if v else None
        scored = [(abs(o / p / med[cc] - 1) if med[cc] else 1.0, cc, y, o, p) for cc, y, o, p in after_cells
                  if o > 0 or p >= 0.5]
        worst = sorted(scored, reverse=True)[:10]
        L += ["Worst 10 cells after refresh. Published is gross for some countries and net for others (USA, PAK, ARG "
              "sit at ~1.00; most at ~0.95), so each cell is scored by its distance from that country's own median "
              "ratio over 2015-2025:", "",
              "| Country | Year | Ours after (TWh) | Published (TWh) | Ratio after | Country median | Ratio before |",
              "|---|---|---|---|---|---|---|"]
        for _, cc, y, o, p in worst:
            L.append(f"| {cc} | {y} | {o:.2f} | {p:.2f} | {o / p:.2f} | {med[cc]:.2f} | {ours_t.get((cc, y), 0) / p:.2f} |")
        L.append("")
        L += ["World totals (TWh): year: before -> after (PRIS world monthly sum; published WLD)", ""]
        for y in YEARS:
            L.append(f"- {y}: {sum(ours_t.get((c, y), 0) for c in ccs):.1f} -> {sum(after_t.get((c, y), 0) for c in ccs):.1f} "
                     f"(PRIS matched {sum(pris_t.get((c, y), 0) for c in ccs):.1f}; published {pub.get(('WLD', y), 0):.1f})")
        L.append("")
        print("worst after:", [(cc, y, round(o / p, 2), med[cc]) for _, cc, y, o, p in worst])
    if a.consistency_log:
        txt = Path(a.consistency_log).read_text(encoding="utf-8", errors="replace").strip().splitlines()
        L += ["### site_consistency.py --db test031.db", "", "```"] + txt + ["```", ""]
    (PG / "summary.md").write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {PG / 'diff.tsv'} ({len(recs)} rows) and {PG / 'summary.md'}")


if __name__ == "__main__":
    main()
