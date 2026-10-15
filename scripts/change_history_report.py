"""Build the change-history review page from the cell-level ledger.

Purpose: one page listing every audit/fix since January, newest first, with failure modes, biggest changes and
         change counts grouped by size.
Inputs:  audit/change_history/cells.tsv, versions.tsv (scripts/db_change_history.py),
         audit/change_history/groups.json (version -> audit grouping), audit/change_history/narrative.json
         (failure modes + per-audit write-up, hand-written from migration headers, MEMORY.md, session log),
         audit/change_history/_tmp/<version>.db (for headline counts per version).
Outputs: review/<date>-change-history.html (local review page; review/ is git-excluded).
last_run: 2026-10-15
"""
import csv
import html
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CH = ROOT / "audit" / "change_history"
csv.field_size_limit(10 ** 8)

IDENT = {"pris_id", "model_id", "reactor_id", "technology_id", "supplier_id", "country_id"}
TIERS = ["Very large", "Large", "Medium", "Small", "Category swap", "Rename / respell", "Filled blank",
         "Hidden (cleared)", "Identifier", "Row added", "Row removed"]
TIER_NOTE = {
    "Very large": "number off by more than 20%, or a date off by more than 5 years",
    "Large": "number off 5-20%, date off 1-5 years, or a location off by more than 10 km",
    "Medium": "number off 1-5%, date off 1-12 months, location off 1-10 km",
    "Small": "number off under 1%, date off under a month, location off under 1 km",
    "Category swap": "a different status, firm, cooling type, design or owner",
    "Rename / respell": "a plant name, unit number or spelling corrected",
    "Filled blank": "a value added where the field was empty",
    "Hidden (cleared)": "a value removed because it was wrong or could not be sourced",
    "Identifier": "a link to an outside record (IAEA id, model id) set or corrected",
    "Row added": "a whole reactor (or details row) added",
    "Row removed": "a whole reactor (or details row) removed",
}
TIER_COLOR = {"Very large": "#b3261e", "Large": "#e07a1f", "Medium": "#d9b100", "Small": "#7fb069",
              "Category swap": "#6a4c93", "Rename / respell": "#9c89b8", "Filled blank": "#1f7a8c",
              "Hidden (cleared)": "#8d99ae", "Identifier": "#bfc0c0", "Row added": "#2b59c3", "Row removed": "#14213d"}
HEADLINE_FIELDS = {"status", "gross_capacity_mw", "net_capacity_mw", "grid_connection", "commercial_operation",
                   "permanent_shutdown", "suspended_since", "construction_start"}


def tier(r):
    k, b, f = r["kind"], r["bucket"], r["field"]
    if k == "INSERT":
        return "Row added"
    if k == "DELETE":
        return "Row removed"
    if f in IDENT:
        return "Identifier"
    if k == "FILL":
        return "Filled blank"
    if k == "CLEAR":
        return "Hidden (cleared)"
    if k == "RESPELL" or f in ("plant_name", "unit_number"):
        return "Rename / respell"
    if b in ("status", "text replace"):
        return "Category swap"
    if b in ("number >20%", "date >5 years"):
        return "Very large"
    if b in ("number 5-20%", "date 1-5 years", "coord >10 km"):
        return "Large"
    if b in ("number 1-5%", "date 1-12 months", "coord 1-10 km"):
        return "Medium"
    return "Small"


def headline(dbpath):
    try:
        c = sqlite3.connect(dbpath)
        st = dict(c.execute("SELECT status, COUNT(*) FROM reactors GROUP BY status").fetchall())
        gw = c.execute("SELECT ROUND(SUM(gross_capacity_mw)/1000.0,1) FROM reactors WHERE status='Operational'").fetchone()[0]
        c.close()
        return {"operating": st.get("Operational", 0), "uc": st.get("Under Construction", 0), "gw": gw,
                "total": sum(st.values())}
    except sqlite3.Error:
        return None


def e(s):
    return html.escape(str(s))


def main():
    cells = list(csv.DictReader(open(CH / "cells.tsv", encoding="utf-8"), delimiter="\t"))
    versions = list(csv.DictReader(open(CH / "versions.tsv", encoding="utf-8"), delimiter="\t"))
    groups = json.load(open(CH / "groups.json", encoding="utf-8"))
    narr = json.load(open(CH / "narrative.json", encoding="utf-8"))
    vinfo = {v["version"]: v for v in versions}
    by_ver = defaultdict(list)
    for r in cells:
        by_ver[r["version"]].append(r)

    # per group stats
    stats = []
    for g in groups:
        rs = [r for v in g["versions"] for r in by_ver.get(v, [])]
        reactor = [r for r in rs if r["table"] in ("reactors", "reactor_details")]
        other = Counter(r["table"] for r in rs if r["table"] not in ("reactors", "reactor_details"))
        gen = [r for r in rs if r["table"] == "generation_annual"]
        gen_rows = Counter(r["kind"] for r in gen if r["kind"] in ("INSERT", "DELETE"))
        gen_changed = len({r["key"] for r in gen if r["field"] == "electricity_gwh" and r["kind"] not in ("INSERT", "DELETE")})
        tiers = Counter(tier(r) for r in reactor)
        units = len({r["reactor_id"] for r in reactor if r["reactor_id"]})
        headline_cells = sum(1 for r in reactor if r["field"] in HEADLINE_FIELDS or r["kind"] in ("INSERT", "DELETE"))
        dates = [vinfo[v]["date"] for v in g["versions"] if v in vinfo]
        stats.append({"g": g, "reactor": len(reactor), "units": units, "tiers": tiers, "other": other,
                      "gen_added": gen_rows.get("INSERT", 0), "gen_removed": gen_rows.get("DELETE", 0),
                      "gen_changed": gen_changed, "headline_cells": headline_cells,
                      "fields": Counter(r["field"] for r in reactor if r["kind"] not in ("INSERT", "DELETE")),
                      "start": min(dates) if dates else "", "end": max(dates) if dates else ""})

    # headline evolution per version
    evo = []
    for v in versions:
        p = CH / "_tmp" / f"{v['version']}.db"
        if v["version"] == "working":
            p = ROOT / "nuclear_reactors.db"
        if v["version"] == "pending":
            p = CH / "_tmp" / "pending.db"
        h = headline(p) if p.exists() else None
        if h:
            evo.append({"v": v["version"], "d": v["date"], **h})

    total_reactor = sum(s["reactor"] for s in stats if s["g"]["id"] != "phase2_pending")
    total_all_tiers = Counter()
    for s in stats:
        if s["g"]["id"] != "phase2_pending":
            total_all_tiers.update(s["tiers"])

    out = []
    w = out.append
    w("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>")
    w("<title>Database Change History</title><style>")
    w(""":root{--bg:#f6f6f4;--card:#fff;--ink:#1d1d1b;--ink2:#55554f;--line:#deddd6;--accent:#1f4e79;--warn:#b3261e;--chip:#eef1f5}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#141413;--card:#1f1f1d;--ink:#ecebe6;--ink2:#a9a8a0;--line:#3a3a36;--accent:#8fb8de;--warn:#ff8a80;--chip:#2a2d33}}
:root[data-theme=dark]{--bg:#141413;--card:#1f1f1d;--ink:#ecebe6;--ink2:#a9a8a0;--line:#3a3a36;--accent:#8fb8de;--warn:#ff8a80;--chip:#2a2d33}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
main{max-width:1060px;margin:0 auto;padding:24px 16px 80px}h1{font-size:26px;margin:0 0 6px}h2{font-size:20px;margin:36px 0 10px;border-bottom:2px solid var(--line);padding-bottom:6px}
h3{font-size:17px;margin:0 0 4px}.sub{color:var(--ink2)}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:12px 0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.kpi b{display:block;font-size:24px}.kpi span{color:var(--ink2);font-size:13px}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{border-bottom:1px solid var(--line);padding:5px 6px;text-align:right;white-space:nowrap}th:first-child,td:first-child{text-align:left;white-space:normal;min-width:210px}th{font-size:12px;white-space:normal;vertical-align:bottom}
.scroll{overflow-x:auto}.bar{display:flex;height:16px;border-radius:4px;overflow:hidden;background:var(--chip);min-width:40px}.bar i{display:block;height:100%}
.legend{display:flex;flex-wrap:wrap;gap:8px 14px;font-size:12px;color:var(--ink2);margin:8px 0}.legend i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:4px;vertical-align:-1px}
.chip{display:inline-block;background:var(--chip);border-radius:999px;padding:1px 9px;font-size:12px;margin:2px 4px 2px 0}.pending{border-left:4px solid var(--warn)}
.fm{display:grid;grid-template-columns:1fr;gap:10px}@media(min-width:760px){.fm{grid-template-columns:1fr 1fr}}
ul{margin:6px 0 6px 20px;padding:0}li{margin:3px 0}.row{display:grid;grid-template-columns:200px 1fr 60px;gap:8px;align-items:center;font-size:13px;margin:4px 0}
@media(max-width:600px){.row{grid-template-columns:110px 1fr 46px}}.muted{color:var(--ink2);font-size:13px}svg text{fill:var(--ink2);font-size:11px}
""")
    w("</style></head><body><main>")
    w(f"<h1>Database change history</h1><p class='sub'>Every change to the reactor data since the first version on 15 January 2026, "
      f"grouped into {len(groups)} audits, newest first. Built {date.today().isoformat()} from the {len(versions) - 1} saved versions "
      f"of the database in git, plus the three audit drafts not yet applied.</p>")

    pend = next(s for s in stats if s["g"]["id"] == "phase2_pending")
    w("<div class='kpis'>")
    for val, lab in [(f"{total_reactor:,}", "reactor-level values changed (applied)"),
                     (f"{len({r['reactor_id'] for r in cells if r['table'] in ('reactors','reactor_details') and r['version']!='pending' and r['reactor_id']}):,}", "reactors touched at least once"),
                     (f"{len(groups) - 1}", "audits and fix rounds applied"),
                     (f"{pend['reactor']}", "changes waiting in drafts 036-038"),
                     (f"{evo[-1]['operating'] if evo else ''}", "operating reactors now (after drafts)")]:
        w(f"<div class='kpi'><b>{val}</b><span>{e(lab)}</span></div>")
    w("</div>")

    # what you're deciding
    w("<div class='card'><b>What this page is for.</b> " + narr["purpose"] + "</div>")

    # failure modes
    w("<h2>1. The main failure modes</h2><p class='muted'>" + narr["failure_intro"] + "</p><div class='fm'>")
    for fm in narr["failure_modes"]:
        w(f"<div class='card'><h3>{e(fm['title'])}</h3><p>{fm['what']}</p><ul>")
        for x in fm["examples"]:
            w(f"<li>{x}</li>")
        w(f"</ul><p class='muted'><b>Found in:</b> {e(fm['found_in'])}. <b>Guard now:</b> {fm['guard']}</p></div>")
    w("</div>")

    # quantified
    w("<h2>2. How big the fixes were</h2><p class='muted'>" + narr["size_intro"] + "</p><div class='legend'>")
    for t in TIERS:
        w(f"<span><i style='background:{TIER_COLOR[t]}'></i>{e(t)}</span>")
    w("</div><div class='card'>")
    mx = max(s["reactor"] for s in stats) or 1
    for s in reversed(stats):
        segs = "".join(f"<i style='width:{100 * s['tiers'].get(t, 0) / s['reactor']:.2f}%;background:{TIER_COLOR[t]}' title='{e(t)}: {s['tiers'].get(t, 0)}'></i>"
                       for t in TIERS if s["tiers"].get(t)) if s["reactor"] else ""
        width = max(4, 100 * s["reactor"] / mx)
        w(f"<div class='row'><span>{e(s['g']['title'])}</span><div><div class='bar' style='width:{width:.1f}%'>{segs}</div></div><span>{s['reactor']:,}</span></div>")
    w("</div><div class='card scroll'><table><thead><tr><th>Audit (newest first)</th>")
    for t in TIERS:
        w(f"<th title='{e(TIER_NOTE[t])}'>{e(t)}</th>")
    w("<th>Total</th><th>Feeds a headline</th></tr></thead><tbody>")
    for s in reversed(stats):
        cls = " class='pending'" if s["g"]["id"] == "phase2_pending" else ""
        w(f"<tr{cls}><td>{e(s['g']['title'])}<br><span class='muted'>{e(s['start'])}{(' to ' + e(s['end'])) if s['end'] != s['start'] else ''}</span></td>")
        for t in TIERS:
            n = s["tiers"].get(t, 0)
            w(f"<td>{n if n else ''}</td>")
        w(f"<td><b>{s['reactor']:,}</b></td><td>{s['headline_cells']:,}</td></tr>")
    w("<tr><td><b>All applied audits</b></td>")
    for t in TIERS:
        w(f"<td><b>{total_all_tiers.get(t, 0):,}</b></td>")
    w(f"<td><b>{total_reactor:,}</b></td><td></td></tr></tbody></table>")
    w("<p class='muted'>Size classes: " + "; ".join(f"<b>{e(t)}</b>: {e(TIER_NOTE[t])}" for t in TIERS) +
      ". \"Feeds a headline\" counts changes to status, capacity and the key dates that drive the homepage numbers, plus added or removed reactors.</p></div>")

    # other tables
    w("<div class='card scroll'><b>Changes outside the per-reactor facts</b><table><thead><tr><th>Audit</th><th>Generation rows added</th><th>Generation rows corrected</th><th>Generation rows removed</th><th>Other tables (rows or cells)</th></tr></thead><tbody>")
    for s in reversed(stats):
        oth = ", ".join(f"{k} {v:,}" for k, v in s["other"].most_common() if k != "generation_annual")
        if s["gen_added"] or s["gen_changed"] or s["gen_removed"] or oth:
            w(f"<tr><td>{e(s['g']['title'])}</td><td>{s['gen_added']:,}</td><td>{s['gen_changed']:,}</td><td>{s['gen_removed']:,}</td><td style='white-space:normal;text-align:left'>{e(oth)}</td></tr>")
    w("</tbody></table></div>")

    # headline evolution chart (svg)
    if evo:
        W, H, P = 1000, 220, 36
        from datetime import date as _d
        dn = [_d.fromisoformat(x["d"]).toordinal() for x in evo]
        d0, d1 = min(dn), max(dn)
        xs = lambda i: P + (dn[i] - d0) * (W - 2 * P) / max(1, d1 - d0)
        lo = min(min(x["operating"] for x in evo), 0); hi = max(x["operating"] for x in evo) * 1.08
        ys = lambda v: H - P - (v - lo) * (H - 2 * P) / (hi - lo)
        op = " ".join(f"{xs(i):.1f},{ys(x['operating']):.1f}" for i, x in enumerate(evo))
        uc = " ".join(f"{xs(i):.1f},{ys(x['uc']):.1f}" for i, x in enumerate(evo))
        w("<h2>3. What the headline counts looked like at each version</h2><div class='card scroll'>")
        w(f"<svg viewBox='0 0 {W} {H}' width='100%' role='img' aria-label='Operating and under-construction counts by version'>")
        for tick in range(0, int(hi) + 1, 100):
            w(f"<line x1='{P}' x2='{W - P}' y1='{ys(tick):.1f}' y2='{ys(tick):.1f}' stroke='var(--line)'/><text x='4' y='{ys(tick) + 4:.1f}'>{tick}</text>")
        w(f"<polyline points='{op}' fill='none' stroke='#1f7a8c' stroke-width='2.5'/><polyline points='{uc}' fill='none' stroke='#e07a1f' stroke-width='2.5'/>")
        y0, m0 = divmod(_d.fromordinal(d0).year * 12 + _d.fromordinal(d0).month - 1, 12)
        for k in range(0, 13):
            yy, mm = divmod(y0 * 12 + m0 + k, 12)
            od = _d(yy, mm + 1, 1).toordinal()
            if d0 <= od <= d1:
                xx = P + (od - d0) * (W - 2 * P) / max(1, d1 - d0)
                w(f"<line x1='{xx:.1f}' x2='{xx:.1f}' y1='{P}' y2='{H - P}' stroke='var(--line)' stroke-dasharray='2 3'/>"
                  f"<text x='{xx:.1f}' y='{H - 8}' text-anchor='middle'>{_d(yy, mm + 1, 1).strftime('%b')}</text>")
        w("</svg><div class='legend'><span><i style='background:#1f7a8c'></i>Operating reactors</span><span><i style='background:#e07a1f'></i>Under construction</span></div>")
        w("<table><thead><tr><th>Version</th><th>Date</th><th>Operating</th><th>Under construction</th><th>Operating GW (gross)</th><th>All reactors</th></tr></thead><tbody>")
        prev = None
        for x in evo:
            if prev and (x["operating"], x["uc"], x["total"]) == (prev["operating"], prev["uc"], prev["total"]) and x["v"] not in ("pending",):
                prev = x
                continue
            sub = e(vinfo[x["v"]]["subject"][:70])
            w(f"<tr><td>{sub}</td><td>{e(x['d'])}</td><td>{x['operating']}</td><td>{x['uc']}</td><td>{x['gw']}</td><td>{x['total']}</td></tr>")
            prev = x
        w("</tbody></table><p class='muted'>" + narr["evo_note"] + "</p></div>")

    # per-audit
    w("<h2>4. Audit by audit, newest first</h2>")
    na = narr["audits"]
    for s in reversed(stats):
        g = s["g"]; n = na.get(g["id"], {})
        cls = "card pending" if g["id"] == "phase2_pending" else "card"
        w(f"<div class='{cls}'><h3>{e(g['title'])}</h3><p class='muted'>{e(s['start'])}{(' to ' + e(s['end'])) if s['end'] != s['start'] else ''}"
          f" &middot; {s['reactor']:,} reactor-level changes on {s['units']} reactors"
          f"{(' &middot; ' + format(s['gen_added'] + s['gen_changed'] + s['gen_removed'], ',') + ' generation rows') if (s['gen_added'] + s['gen_changed'] + s['gen_removed']) else ''}</p>")
        if n.get("trigger"):
            w(f"<p><b>Why it ran:</b> {n['trigger']}</p>")
        if n.get("biggest"):
            w("<p><b>Biggest changes:</b></p><ul>" + "".join(f"<li>{x}</li>" for x in n["biggest"]) + "</ul>")
        if n.get("failure_modes"):
            w("<p>" + "".join(f"<span class='chip'>{e(x)}</span>" for x in n["failure_modes"]) + "</p>")
        top = ", ".join(f"{k} {v}" for k, v in s["fields"].most_common(6))
        if top:
            w(f"<p class='muted'><b>Most-changed fields:</b> {e(top)}</p>")
        if s["reactor"]:
            segs = "".join(f"<i style='width:{100 * s['tiers'].get(t, 0) / s['reactor']:.2f}%;background:{TIER_COLOR[t]}' title='{e(t)}: {s['tiers'].get(t, 0)}'></i>" for t in TIERS if s["tiers"].get(t))
            w(f"<div class='bar'>{segs}</div><p class='muted'>" + " &middot; ".join(f"{e(t)} {s['tiers'][t]}" for t in TIERS if s['tiers'].get(t)) + "</p>")
        w("</div>")

    w("<h2>5. How this page was made</h2><div class='card'>" + narr["method"] + "</div>")
    w("</main></body></html>")
    path = ROOT / "review" / f"{date.today().isoformat()}-change-history.html"
    path.write_text("\n".join(out), encoding="utf-8")
    print(path, sum(len(x) for x in out) // 1024, "KB", file=sys.stderr)


if __name__ == "__main__":
    main()
