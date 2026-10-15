"""Process one finished Phase 2 fleet wave: ledger, calibration score, draft migration (deterministic; no AI).

Purpose: after the fleet workflow returns (3 Haiku -> Sonnet adjudication -> Opus refutation per batch), turn
  its return value into (1) a ledger of every item's final verdict, (2) the calibration score for the wave's
  hidden answer-key items, (3) a guarded DRAFT migration of the changes the Opus tier upheld, plus the vendor
  whitelist rows and a skipped list. Nothing touches the DB; applying the migration needs Griffin's OK.
Inputs:  --output <workflow task .output JSON> (key "result"), audit/phase2/wave<N>_items.psv,
         audit/calibration.psv, nuclear_reactors.db (read-only)
Outputs: audit/phase2/wave<N>_results.json, wave<N>_ledger.psv, wave<N>_score.md, wave<N>_changes.psv,
         wave<N>_skipped.psv, migrations/<NNN>_phase2_wave<N>.sql, audit/whitelist_<NNN>.psv
Usage:   python scripts/phase2_wave_process.py --wave 1 --migration 034 --output <path>
last_run: 2026-10-14
"""
import argparse
import csv
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P2 = ROOT / "audit" / "phase2"
DETAILS = {"cooling_type", "constructor", "architect_engineer", "turbine_supplier", "pressure_vessel_manufacturer"}
VENDOR = {"constructor", "architect_engineer", "turbine_supplier", "pressure_vessel_manufacturer"}
CONTAINMENT = ["Large Dry (Double)", "Large Dry", "Mark III", "Mark II", "Mark I", "Pre-Mark I", "Ice Condenser",
               "Subatmospheric", "Spherical Double", "Pressure Suppression"]
CONT_MAP = {"double": "Large Dry (Double)", "bubbler": "Pressure Suppression", "dry, ambient": "Large Dry",
            "dry ambient": "Large Dry", "dry, sub-atmospheric": "Subatmospheric", "subatmospheric": "Subatmospheric",
            "ice condenser": "Ice Condenser", "large dry": "Large Dry"}
COOLING = ["Once-through (seawater)", "Once-through (river)", "Once-through (lake)", "Cooling pond",
           "Cooling tower (natural draft)", "Cooling tower (mechanical draft)"]
# Company spellings: legal suffixes dropped, then the short name the DB already uses for the same firm.
SUFFIX = re.compile(r",?\s+(Inc\.?|Incorporated|Corporation|Corp\.?|Co\.?|Company|S\.?A\.?|Ltd\.?)$", re.I)
ALIAS = {"bechtelpower": "Bechtel", "bechtelconstruction": "Bechtel", "stonewebsterengineering": "Stone & Webster",
         "burnsandroe": "Burns & Roe", "tennesseevalleyauthority": "TVA", "westinghouseelectric": "Westinghouse",
         "ebascoservices": "Ebasco", "americanelectricpowerservice": "American Electric Power",
         "bwxtechnologiesincbwxt": "BWX Technologies", "imp": "IMPSA", "nucleoelectricaargentina": "Nucleoeléctrica Argentina (NA-SA)",
         "nucleoelctricaargentina": "Nucleoeléctrica Argentina (NA-SA)", "comisionfederaldeelectricidad": "Comision Federal de Electricidad",
         "pacificgaselectric": "Pacific Gas & Electric"}
# Hand decisions on single items (item_id -> value, why), shown on the review page.
OVERRIDES = {"W1B017-10": ("Indian Point 1", "one-off B&W design (not W 4-Loop); design_series is required, and one-off "
                                             "units are named after the unit, as CVTR and Saxton are")}
# Upheld changes held back by hand (item_id -> why), listed as skipped on the review page.
HOLD = {"W2B074-17": "granularity, not an error: Grohnde is a KWU 4-loop PWR, and the house labels every KWU 4-loop unit "
                     "(incl. the other Vor-Konvoi plants Brokdorf, Grafenrheinfeld, Philippsburg 2) 'Siemens 4-Loop'; "
                     "relabel the series fleet-wide or not at all"}
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
clean = lambda s: (s or "").replace("|", "/").replace("\n", " ").strip()


def house(field, v, existing):
    """Map a value onto a spelling already used in the DB (case/punctuation-insensitive), else keep it."""
    if v in (None, ""):
        return None, "clear"
    if field == "containment_type":
        for c in CONTAINMENT:
            if norm(c) == norm(v):
                return c, "exact"
        low = v.lower()
        for k, c in CONT_MAP.items():
            if k in low:
                return c, "mapped"
        return v, "NEW_CONTAINMENT"  # not in house vocabulary: skipped by caller
    if field == "cooling_type":
        hit = next((c for c in COOLING if norm(c) == norm(v)), None)
        return (hit, "exact") if hit else (v, "NEW_COOLING")  # no house category (e.g. estuary): skipped
    if field in ("licensed_until", "planned_retirement"):
        return v[:4], "year"  # house format is the year
    if field in VENDOR:
        while SUFFIX.search(v):
            v = SUFFIX.sub("", v).strip()
        v = ALIAS.get(norm(v), v)
    hit = existing.get(field, {}).get(norm(v)) or existing.get("_vendor", {}).get(norm(v))
    return (hit, "house") if hit else (v, "new")


def q(v):
    return "NULL" if v is None else "'" + str(v).replace("'", "''") + "'"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int, required=True)
    ap.add_argument("--migration", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    W, M = a.wave, a.migration
    res = json.load(open(a.output, encoding="utf-8"))["result"]
    if isinstance(res, str):
        res = json.loads(res)
    (P2 / f"wave{W}_results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    items = {r["item_id"]: r for r in csv.DictReader(open(P2 / f"wave{W}_items.psv", encoding="utf-8"), delimiter="|")}
    cal = {r["cal_id"]: {**r, "label": r.get("label(WRONG/CORRECT/TRAP)")}
           for r in csv.DictReader(open(ROOT / "audit" / "calibration.psv", encoding="utf-8"), delimiter="|")}

    db = sqlite3.connect(f"file:{ROOT / 'nuclear_reactors.db'}?mode=ro", uri=True)
    existing = {}
    for f in VENDOR | {"cooling_type", "design_series"}:
        tbl = "reactor_details" if f in DETAILS else "reactors"
        existing[f] = {norm(v): v for (v,) in db.execute(f"SELECT DISTINCT {f} FROM {tbl} WHERE {f} IS NOT NULL")}
    existing["_vendor"] = {k: v for f in VENDOR for k, v in existing[f].items()}

    final, refuted = {}, {}
    for b in res:
        for v in b["accepted"] + b["adjudicated"]:
            final[v["item_id"]] = v
        for iid in b["disputes"]:
            final.setdefault(iid, {"item_id": iid, "verdict": "BLOCKED", "tier": "unadjudicated",
                                   "note": "adjudicator returned nothing"})
        for r in b.get("refuted", []):
            refuted[r["item_id"]] = r
    missing = [i for i in items if i not in final]

    # Final pipeline outcome per item: a proposed change counts only if Opus upheld it.
    def outcome(iid):
        v = final.get(iid)
        if not v:
            return "MISSING"
        if v["verdict"] in ("WRONG", "FILL"):
            r = refuted.get(iid)
            if not r or not r["outcome"].startswith("UPHELD") or ";" in (r.get("final_value") or v.get("proposed_value") or ""):
                return "BLOCKED"
            return v["verdict"]
        return v["verdict"]

    with open(P2 / f"wave{W}_ledger.psv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|")
        w.writerow(["item_id", "origin", "cal_id", "reactor_db_id", "reactor", "field", "shown", "verdict", "tier",
                    "refute", "proposed_value", "final_value", "source_url", "quote", "second_source_url", "note"])
        for iid, it in items.items():
            v = final.get(iid, {"verdict": "MISSING", "tier": "none"})
            r = refuted.get(iid, {})
            w.writerow([iid, it["origin"], it["cal_id"], it["reactor_db_id"], it["reactor"], it["field"], it["shown"],
                        v.get("verdict"), v.get("tier"), r.get("outcome", ""), clean(v.get("proposed_value")),
                        clean(r.get("final_value")), clean(r.get("source_url") or v.get("source_url")),
                        clean(r.get("quote") or v.get("quote")), clean(r.get("second_source_url")),
                        clean(r.get("reason") or v.get("note"))])

    # Calibration score (all wave calibration items are clean: placed away from same-plant items).
    tp = fp = fn = tn = blk = val_ok = 0
    rows = []
    for iid, it in items.items():
        if it["origin"] != "CAL":
            continue
        c = cal[it["cal_id"]]
        exp = c["trap_note"].split(".")[0].replace("expected=", "").strip()
        got = outcome(iid)
        said_wrong = got in ("WRONG", "FILL")
        blk += got in ("BLOCKED", "MISSING")
        ok = ""
        if exp.startswith("WRONG"):
            if said_wrong:
                tp += 1
                r = refuted.get(iid, {})
                pv = r.get("final_value") if r.get("outcome") == "UPHELD_WITH_EDIT" else final[iid].get("proposed_value")
                ok = bool(pv) and (norm(c["truth_value"])[:12] in norm(pv) or norm(pv)[:12] in norm(c["truth_value"]))
                val_ok += ok
            elif got not in ("BLOCKED", "MISSING"):
                fn += 1
        else:
            fp += said_wrong
            tn += got == "CORRECT"
        rows.append((iid, c["cal_id"], c["reactor"], c["field"], c["label"], exp, got, ok, c["truth_value"]))
    n_wrong = sum(r[5].startswith("WRONG") for r in rows)
    out = [f"# Phase 2 wave {W} — calibration score", "",
           f"- calibration items: {len(rows)} (known errors: {n_wrong})",
           f"- precision of changes: {tp}/{tp + fp}" + (f" = {tp / (tp + fp):.3f}" if tp + fp else ""),
           f"- recall of known errors: {tp}/{n_wrong}" + (f" = {tp / n_wrong:.3f}" if n_wrong else ""),
           f"- known errors confidently called CORRECT (bad miss): {fn}",
           f"- blocked (can't verify): {blk}", f"- proposed value matched truth: {val_ok}/{tp}", "",
           "| item | cal | reactor | field | label | expected | got | value ok | truth |", "|---|---|---|---|---|---|---|---|---|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    out += ["", f"Final outcomes (fleet items): {dict(Counter(outcome(i) for i, it in items.items() if it['origin'] == 'F'))}",
            f"Tiers: {dict(Counter(v.get('tier') for v in final.values()))}",
            f"Refute outcomes: {dict(Counter(r['outcome'] for r in refuted.values()))}",
            f"Items with no verdict: {len(missing)} {missing[:20]}"]
    (P2 / f"wave{W}_score.md").write_text("\n".join(out), encoding="utf-8")

    # Draft migration: fleet items whose change Opus upheld.
    writes, skipped = [], []
    for iid, it in items.items():
        v = final.get(iid)
        if it["origin"] != "F" or not v or v["verdict"] not in ("WRONG", "FILL"):
            continue
        r = refuted.get(iid)
        if not r or not r["outcome"].startswith("UPHELD"):
            skipped.append((iid, it, v, r["outcome"] if r else "NOT_REVIEWED", (r or {}).get("reason", "")))
            continue
        if iid in HOLD:
            skipped.append((iid, it, v, "HELD_BY_HAND", HOLD[iid])); continue
        val = r["final_value"] if r["outcome"] == "UPHELD_WITH_EDIT" else (r["final_value"] or v.get("proposed_value"))
        f = it["field"]
        if isinstance(val, str) and ";" in val:
            skipped.append((iid, it, v, "AMBIGUOUS_ROLE", val)); continue
        if f in ("licensed_until", "planned_retirement") and isinstance(val, str) and not re.match(r"^\d{4}(-\d\d(-\d\d)?)?$", val.strip()):
            skipped.append((iid, it, v, "NOT_A_DATE", val)); continue
        val, how = house(f, val.strip() if isinstance(val, str) else val, existing)
        if iid in OVERRIDES:
            val, how = OVERRIDES[iid][0], "override"
        if how in ("NEW_CONTAINMENT", "NEW_COOLING"):
            skipped.append((iid, it, v, "NOT_HOUSE_VOCAB", val)); continue
        if not r.get("second_source_url") and val is not None:
            skipped.append((iid, it, v, "NO_SECOND_SOURCE", r.get("reason", ""))); continue
        shown = it["shown"] if it["shown"] not in ("", "None") else None
        if norm(val) == norm(shown):
            continue
        writes.append((iid, it, r, val, shown, how))

    L = [f"-- {M}_phase2_wave{W}.sql", "-- Date: 2026-10-14 (DRAFT — apply only after Griffin approves)",
         f"-- Description: Phase 2 fleet audit, wave {W}. Three tiers per batch: 3 Haiku researchers -> Sonnet",
         "--   adjudication -> Opus refutation with an independent second source. Only Opus-UPHELD changes are written;",
         "--   values mapped to existing house spellings. Each UPDATE is guarded on the old value.",
         f"--   Per-change sources and quotes: audit/phase2/wave{W}_changes.psv (local).",
         f"-- Writes: {len(writes)}. Skipped: {len(skipped)} (see audit/phase2/wave{W}_skipped.psv).",
         "-- Vendor values are appended to the whitelist (verification_2026-07/final_verdicts.psv) in the same change.",
         f"-- Backup: nuclear_reactors.db.bak-pre{M}-<date>", "", "BEGIN TRANSACTION;"]
    with open(P2 / f"wave{W}_changes.psv", "w", encoding="utf-8", newline="") as fh, \
            open(ROOT / "audit" / f"whitelist_{M}.psv", "w", encoding="utf-8", newline="") as wl:
        w = csv.writer(fh, delimiter="|")
        w.writerow(["item_id", "reactor_db_id", "reactor", "field", "old", "new", "spelling", "outcome", "verdict",
                    "source_url", "quote", "second_source_url", "reason"])
        ww = csv.writer(wl, delimiter="|")
        for iid, it, r, val, shown, how in writes:
            rid, f = int(it["reactor_db_id"]), it["field"]
            tbl, key = ("reactor_details", "reactor_id") if f in DETAILS else ("reactors", "id")
            guard = f"{f} IS NULL" if shown is None else f"{f} = {q(shown)}"
            L.append(f"UPDATE {tbl} SET {f} = {q(val)} WHERE {key} = {rid} AND ({guard});  -- {it['reactor']}")
            w.writerow([iid, rid, it["reactor"], f, shown, val, how, r["outcome"], final[iid]["verdict"],
                        clean(r["source_url"]), clean(r["quote"]), clean(r["second_source_url"]), clean(r["reason"])])
            if f in VENDOR and val:
                pl, un = db.execute("SELECT plant_name, unit_number FROM reactors WHERE id = ?", (rid,)).fetchone()
                ww.writerow([rid, pl, un, "rpv_manufacturer" if f == "pressure_vessel_manufacturer" else f, "CONFIRMED", "HIGH", "yes", val,
                             f"{r['source_url']} ; {r['second_source_url'] or ''} (Phase 2 wave {W}, Opus-upheld 2026-10-14)"])
    L += ["COMMIT;", ""]
    (ROOT / "migrations" / f"{M}_phase2_wave{W}.sql").write_text("\n".join(L), encoding="utf-8")
    with open(P2 / f"wave{W}_skipped.psv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|")
        w.writerow(["item_id", "reactor", "field", "shown", "proposed", "why", "detail"])
        for iid, it, v, why, det in skipped:
            w.writerow([iid, it["reactor"], it["field"], it["shown"], clean(v.get("proposed_value")), why, clean(det)[:400]])
    print("\n".join(out[:8]))
    print(out[-4:])
    print(f"{len(writes)} writes, {len(skipped)} skipped; spelling: {dict(Counter(x[5] for x in writes))}")
    print(f"skips: {dict(Counter(x[3] for x in skipped))}")


if __name__ == "__main__":
    main()
