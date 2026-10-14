"""Score the Phase 2 pilot: calibration accuracy per tier, plus the ledger of proposed changes.

Purpose: go/no-go gate for the fleet-wide agent audit (docs/audit-plan-2026-10.md success criterion 1:
  >=95% precision on WRONG calls, >=80% recall of known errors, on the calibration set).
Inputs:  audit/phase2/pilot_results.json (workflow return value), audit/phase2/pilot_items.psv,
         audit/calibration.psv
Outputs: audit/phase2/pilot_ledger.psv (every item: final verdict, tier, value, source, quote) — feed
         to scripts/quote_check.py; audit/phase2/score.md (calibration metrics, clean vs contaminated).
Usage:   python scripts/phase2_score.py
Note:    a calibration item is "contaminated" when the same reactor+field also appeared as a pilot
         (Track A) item, or a sibling calibration item for the same reactor sat in the same batch;
         headline metrics use clean items only.
last_run: 2026-10-14
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P2 = ROOT / "audit" / "phase2"
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main():
    res = json.load(open(P2 / "pilot_results.json", encoding="utf-8"))
    items = {r["item_id"]: r for r in csv.DictReader(open(P2 / "pilot_items.psv", encoding="utf-8"), delimiter="|")}
    cal = {r["cal_id"]: {**r, "label": r.get("label") or r.get("label(WRONG/CORRECT/TRAP)")}
           for r in csv.DictReader(open(ROOT / "audit" / "calibration.psv", encoding="utf-8"), delimiter="|")}

    final = {}
    for b in res:
        for v in b["accepted"]:
            final[v["item_id"]] = v
        for v in b["adjudicated"]:
            final[v["item_id"]] = v
        for iid, claims in b["disputes"].items():
            if iid not in final:
                final[iid] = {"item_id": iid, "verdict": "BLOCKED", "tier": "unadjudicated", "note": "adjudicator returned nothing"}
    haiku_first = {}
    for b in res:
        for iid, claims in b["disputes"].items():
            votes = Counter(c["verdict"] for c in claims)
            haiku_first[iid] = votes.most_common(1)[0][0]
        for v in b["accepted"]:
            haiku_first[v["item_id"]] = v["verdict"]

    # contamination
    a_keys = {(i["reactor_db_id"], i["field"]) for i in items.values() if i["origin"] == "A"}
    cal_batch = defaultdict(list)
    for i in items.values():
        if i["origin"] == "CAL":
            cal_batch[(i["batch"], i["reactor_db_id"])].append(i["item_id"])

    with open(P2 / "pilot_ledger.psv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|")
        w.writerow(["item_id", "origin", "cal_id", "reactor_db_id", "reactor", "field", "shown", "verdict", "tier",
                    "proposed_value", "source_url", "quote", "note"])
        for iid, it in sorted(items.items()):
            v = final.get(iid, {"verdict": "MISSING", "tier": "none"})
            w.writerow([iid, it["origin"], it["cal_id"], it["reactor_db_id"], it["reactor"], it["field"], it["shown"],
                        v.get("verdict"), v.get("tier"), v.get("proposed_value") or "", v.get("source_url") or "",
                        (v.get("quote") or "").replace("|", "/").replace("\n", " "), (v.get("note") or "").replace("|", "/").replace("\n", " ")])

    def score(pick, clean_only):
        tp = fp = fn = tn = blocked = trap_ok = trap_n = val_ok = 0
        rows = []
        for iid, it in items.items():
            if it["origin"] != "CAL":
                continue
            c = cal[it["cal_id"]]
            contaminated = (it["reactor_db_id"], it["field"]) in a_keys or len(cal_batch[(it["batch"], it["reactor_db_id"])]) > 1
            if clean_only and contaminated:
                continue
            exp = c["trap_note"].split(".")[0].replace("expected=", "").strip()
            got = pick(iid)
            said_wrong = got in ("WRONG", "FILL")
            if got == "BLOCKED":
                blocked += 1
            if c["label"].startswith("TRAP"):
                trap_n += 1
                ok = (exp.startswith("WRONG") and (said_wrong or ("BLOCKED" in exp and got == "BLOCKED"))) or \
                     (exp == "CORRECT" and got == "CORRECT")
                trap_ok += ok
            if exp.startswith("WRONG"):
                if said_wrong:
                    tp += 1
                    pv = final.get(iid, {}).get("proposed_value")
                    val_ok += bool(pv) and (norm(c["truth_value"])[:12] in norm(pv) or norm(pv)[:12] in norm(c["truth_value"]))
                elif got != "BLOCKED":
                    fn += 1
            else:
                if said_wrong:
                    fp += 1
                elif got == "CORRECT":
                    tn += 1
            rows.append((iid, it["cal_id"], c["label"], exp, got, contaminated))
        n_wrong = sum(1 for r in rows if r[3].startswith("WRONG"))
        prec = tp / (tp + fp) if tp + fp else None
        rec = tp / n_wrong if n_wrong else None
        return dict(n=len(rows), tp=tp, fp=fp, fn=fn, tn=tn, blocked=blocked, precision=prec, recall=rec,
                    traps=f"{trap_ok}/{trap_n}", proposed_value_matches_truth=f"{val_ok}/{tp}"), rows

    out = ["# Phase 2 pilot — calibration score", ""]
    for label, pick in (("Final (Haiku unanimous or Sonnet adjudication)", lambda i: final.get(i, {}).get("verdict")),
                        ("Haiku alone (majority of 3)", lambda i: haiku_first.get(i))):
        for clean in (True, False):
            m, rows = score(pick, clean)
            out.append(f"## {label} — {'clean items only' if clean else 'all calibration items'}")
            out.append("")
            for k, v in m.items():
                out.append(f"- {k}: {round(v, 3) if isinstance(v, float) else v}")
            out.append("")
    m, rows = score(lambda i: final.get(i, {}).get("verdict"), False)
    out.append("## Per-item (final)")
    out.append("")
    out.append("| item | cal | label | expected | got | contaminated |")
    out.append("|---|---|---|---|---|---|")
    for r in sorted(rows):
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    out.append("")
    tiers = Counter(v.get("tier") for v in final.values())
    verdicts = Counter((items[i]["origin"], v.get("verdict")) for i, v in final.items() if i in items)
    out.append(f"Tiers: {dict(tiers)}")
    out.append(f"Verdicts by origin: {dict(verdicts)}")
    (P2 / "score.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out[:40]))


if __name__ == "__main__":
    main()
