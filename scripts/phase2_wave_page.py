"""Build the local review page for one Phase 2 fleet wave (deterministic; reads the processed wave files).

Purpose: one self-contained HTML page per wave for Griffin: what ran, calibration score, every proposed DB
  write with sources and quotes, what was skipped and why, and the decisions he needs to make.
Inputs:  audit/phase2/wave<N>_ledger.psv, wave<N>_changes.psv, wave<N>_skipped.psv, wave<N>_score.md,
         audit/phase2/qc_w<N>/quote_check_final.tsv (optional), --notes <json file with region/agents/minutes/decisions>
Outputs: review/2026-10-14-audit-wave<N>.html (local only; never published)
Usage:   python scripts/phase2_wave_page.py --wave 1 --migration 034 --notes audit/phase2/wave1_notes.json
last_run: 2026-10-14
"""
import argparse
import csv
import html
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P2 = ROOT / "audit" / "phase2"
esc = html.escape
LABEL = {"licensed_until": "licence end", "planned_retirement": "planned retirement", "constructor": "constructor",
         "architect_engineer": "architect-engineer", "pressure_vessel_manufacturer": "pressure-vessel maker",
         "turbine_supplier": "turbine maker", "containment_type": "containment", "design_series": "design series",
         "cooling_type": "cooling"}


def rd(name):
    return list(csv.DictReader(open(P2 / name, encoding="utf-8"), delimiter="|"))


def host(u):
    m = re.match(r"https?://(?:www\.)?([^/]+)", u or "")
    return m.group(1) if m else (u or "")


def link(u):
    return f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(host(u))}</a>' if u else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int, required=True)
    ap.add_argument("--migration", required=True)
    ap.add_argument("--notes", required=True)
    a = ap.parse_args()
    W, M = a.wave, a.migration
    notes = json.load(open(a.notes, encoding="utf-8"))
    led, ch, sk = rd(f"wave{W}_ledger.psv"), rd(f"wave{W}_changes.psv"), rd(f"wave{W}_skipped.psv")
    qc = {}
    qcp = P2 / f"qc_w{W}" / "quote_check_final.tsv"  # after quote_check.py + quote_check_browser.py
    if qcp.exists():
        qc = {r["item_id"]: r["final"] for r in csv.DictReader(open(qcp, encoding="utf-8"), delimiter="	")}
    fleet = [r for r in led if r["origin"] == "F"]

    def final(r):
        if r["verdict"] in ("WRONG", "FILL"):
            return "change" if r["refute"].startswith("UPHELD") else "blocked"
        return {"CORRECT": "confirmed", "BLOCKED": "blocked"}.get(r["verdict"], "blocked")
    oc = Counter(final(r) for r in fleet)
    byf = Counter(r["field"] for r in ch)
    blk_f = Counter(r["field"] for r in fleet if final(r) == "blocked")
    qcc = Counter(qc.get(r["item_id"], "not checked") for r in ch)
    score = (P2 / f"wave{W}_score.md").read_text(encoding="utf-8")
    cal_rows = [l for l in score.splitlines() if l.startswith("| W")]

    def cal_tr(l):
        c = [x.strip() for x in l.strip("|").split("|")]
        verdict = {"WRONG": "change", "FILL": "change", "CORRECT": "confirmed"}.get(c[6], "can't verify")
        good = (c[5].startswith("WRONG") and verdict == "change") or (c[5] == "CORRECT" and verdict == "confirmed")
        bad = (c[5].startswith("WRONG") and verdict == "confirmed") or (c[5] == "CORRECT" and verdict == "change")
        cls = "ok" if good else ("bad" if bad else "mut")
        return (f"<tr><td>{esc(c[2])}</td><td>{esc(LABEL.get(c[3], c[3].replace('_', ' ')))}</td>"
                f"<td>{'known error' if c[5].startswith('WRONG') else 'known correct'}</td>"
                f"<td class='{cls}'>{verdict}</td><td>{esc(c[8])}</td></tr>")

    def ch_tr(r):
        s = qc.get(r["item_id"], "")
        badge = {"FOUND": "ok", "PARTIAL": "ok"}.get(s, "mut")
        return (f"<tr><td>{esc(r['reactor'])}</td><td>{esc(r['old'] or '(empty)')}</td><td><b>{esc(r['new'] or '(clear)')}</b></td>"
                f"<td>{link(r['source_url'])}<br>{link(r['second_source_url'])}</td>"
                f"<td class='q'>“{esc(r['quote'][:200])}”<br><span class='{badge}'>quote check: {esc(s.lower() or 'n/a')}</span></td></tr>")

    sections = ""
    for f in sorted(byf, key=lambda f: -byf[f]):
        rows = sorted((r for r in ch if r["field"] == f), key=lambda r: r["reactor"])
        sections += (f"<details{' open' if byf[f] < 8 else ''}><summary><b>{esc(LABEL.get(f, f))}</b> — {byf[f]} change(s)</summary>"
                     f"<div class='scroll'><table><tr><th>Reactor</th><th>Before</th><th>After</th><th>Sources</th><th>Quote</th></tr>"
                     + "".join(ch_tr(r) for r in rows) + "</table></div></details>")
    sk_tr = "".join(f"<tr><td>{esc(r['reactor'])}</td><td>{esc(LABEL.get(r['field'], r['field']))}</td><td>{esc(r['shown'] or '(empty)')}</td>"
                    f"<td>{esc(r['proposed'] or '(clear)')}</td><td>{esc(r['why'])}</td><td class='q'>{esc(r['detail'][:260])}</td></tr>" for r in sk)
    dec = "".join(f"<div class='ask'><b>Decide {i}: {esc(d['title'])}</b><br>{d['html']}</div>" for i, d in enumerate(notes["decisions"], 1))
    notable = "".join(f"<li>{n}</li>" for n in notes.get("notable", []))

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Audit Wave {W} Review</title><style>
:root{{--bg:#fbfaf7;--fg:#1d2420;--mut:#5d6660;--card:#fff;--line:#e3e1da;--b:#3F55C3;--ok:#2f6b45;--bad:#b3261e}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141816;--fg:#e8ebe8;--mut:#9aa39d;--card:#1c211e;--line:#2c332f;--b:#8c9cf0;--ok:#6fbf8a;--bad:#f2867e}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;margin:0;padding:0 16px}}
main{{max-width:960px;margin:0 auto;padding:24px 0 60px}}h1{{font-size:1.6rem;line-height:1.25}}h2{{font-size:1.2rem;margin:2em 0 .4em;border-top:1px solid var(--line);padding-top:1.2em}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}}.ask{{border-left:4px solid var(--b);padding:10px 14px;background:var(--card);margin:12px 0}}
table{{border-collapse:collapse;width:100%;font-size:.85rem}}td,th{{text-align:left;padding:6px;border-bottom:1px solid var(--line);vertical-align:top}}.q{{color:var(--mut);font-size:.8rem}}
.scroll{{overflow-x:auto}}.mut{{color:var(--mut)}}.big{{font-size:1.5rem;font-weight:700}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}}
.ok{{color:var(--ok)}}.bad{{color:var(--bad);font-weight:600}}details{{margin:10px 0}}summary{{cursor:pointer;padding:6px 0}}a{{color:var(--b)}}</style></head><body><main>
<p class="mut">Nuclear reactor database · fleet audit wave {W} ({esc(notes['region'])}) · 14 Oct 2026 · local page, not published</p>
<h1>Wave {W}: {len(ch)} sourced changes ready for your OK</h1>
<div class="card"><b>Short version.</b> {notes['short']}</div>

<h2>1. What ran</h2>
<p>{len(fleet):,} items: every hard-to-source field for the reactors in {esc(notes['region'])}. Each batch of about 18 items went through three
independent Haiku researchers, a Sonnet adjudicator for any disagreement or proposed change, and an Opus reviewer that tried to disprove each
change with a second, independent source. {notes['agents']} agents, about {notes['minutes']} minutes. {len(cal_rows)} answer-key items were mixed in without labels.</p>
<div class="grid">
<div class="card"><div class="big">{oc['confirmed']:,}</div>values confirmed by a fetched source</div>
<div class="card"><div class="big">{oc['change']:,}</div>changes upheld by all three tiers</div>
<div class="card"><div class="big">{oc['blocked']:,}</div>can't verify (left as is)</div>
<div class="card"><div class="big">{len(ch)}</div>writes in draft migration {M}</div>
</div>
<p class="mut">"Can't verify" is the safe outcome: nothing is written. By field: {', '.join(f'{LABEL.get(f, f)} {n}' for f, n in blk_f.most_common())}.</p>

<h2>2. Answer-key check</h2>
<p>{notes['cal_summary']}</p>
<div class="scroll"><table><tr><th>Reactor</th><th>Field</th><th>Answer key</th><th>Pipeline said</th><th>True value</th></tr>{''.join(cal_tr(l) for l in cal_rows)}</table></div>

<h2>3. Quote check</h2>
<p>A script re-fetched every cited page (plain download, then real Chrome for sites that block scripts, with PDF text extraction) and searched for the quote.
Results for the {len(ch)} changes: {', '.join(f'{k.lower()} {v}' for k, v in qcc.most_common())}. "Found" means the exact words are on the page; "partial" means at least 70% of them are, including a 4-word run. {notes.get('qc_note', '')}</p>

<h2>4. Decisions</h2>
{dec}

<h2>5. The {len(ch)} changes, by field</h2>
<p class="mut">Each passed all three tiers with two independent sources. Company names use the spelling the database already uses ("Bechtel", not "Bechtel Power Corporation"). Licence ends are stored as the year, like the rest of the column.</p>
<ul>{notable}</ul>
{sections}

<h2>6. Not written ({len(sk)})</h2>
<div class="scroll"><table><tr><th>Reactor</th><th>Field</th><th>Now</th><th>Proposed</th><th>Why not</th><th>Detail</th></tr>{sk_tr}</table></div>
</main></body></html>"""
    out = ROOT / "review" / f"2026-10-14-audit-wave{W}.html"
    out.write_text(page, encoding="utf-8")
    print(out, len(ch), len(sk), dict(qcc))


if __name__ == "__main__":
    main()
