"""Build migration 033 (DRAFT): Phase 2 pilot changes that survived Opus refutation review.

Purpose: turn the three-tier pilot ledger into a guarded migration. Tier 1: 3 Haiku researchers per batch;
  tier 2: Sonnet adjudicator on disagreements and every proposed change; tier 3: Opus reviewers trying to
  refute each proposed change with an independent second source. Only UPHELD / UPHELD_WITH_EDIT outcomes
  are written; values are mapped to the house vocabulary (deterministic map below); ambiguous role values
  are skipped and listed.
Inputs:  audit/phase2/proposals.json, audit/phase2/refute_results.json, nuclear_reactors.db (read-only)
Outputs: migrations/033_phase2_pilot.sql, audit/phase2/033_changes.psv (one row per write, with sources),
         audit/whitelist_033.psv (vendor values to append to verification_2026-07/final_verdicts.psv)
Usage:   python scripts/build_033_phase2_pilot.py
last_run: 2026-10-14
"""
import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P2 = ROOT / "audit" / "phase2"
DETAILS = {"cooling_type", "constructor", "architect_engineer", "turbine_supplier", "pressure_vessel_manufacturer"}
VENDOR = {"constructor", "architect_engineer", "turbine_supplier", "pressure_vessel_manufacturer"}
# House vocabulary (values already used in the DB for the same thing).
VOCAB = {
    "containment_type": {
        "double": "Large Dry (Double)",
        "bubbler condenser": "Pressure Suppression", "pressure suppression": "Pressure Suppression",
        "large dry": "Large Dry", "full-pressure prestressed concrete with steel liner": "Large Dry",
    },
    "pressure_vessel_manufacturer": {"skoda": "Skoda Works"},
    "architect_engineer": {"energoprojekt praha": "Energoprojekt Praha", "bechtel": "Bechtel"},
}
# Ambiguous role answers: reviewers named two firms for one field; leave the field unchanged.
SKIP_IF_CONTAINS = (";",)


def house(field, v):
    if v is None or v == "":
        return None
    low = v.lower()
    for key, name in VOCAB.get(field, {}).items():
        if key in low or (key == "skoda" and "škoda" in low):
            return name
    return v


def q(v):
    return "NULL" if v is None else "'" + str(v).replace("'", "''") + "'"


def main():
    props = {p["item_id"]: p for p in json.load(open(P2 / "proposals.json", encoding="utf-8"))}
    ref = {r["item_id"]: r for r in json.load(open(P2 / "refute_results.json", encoding="utf-8"))}
    db = sqlite3.connect(f"file:{ROOT / 'nuclear_reactors.db'}?mode=ro", uri=True)
    writes, skipped = [], []
    for iid, p in props.items():
        r = ref.get(iid)
        if not r or r["outcome"] not in ("UPHELD", "UPHELD_WITH_EDIT"):
            skipped.append((iid, p, r["outcome"] if r else "MISSING", r["reason"] if r else ""))
            continue
        val = r["final_value"] if r["outcome"] == "UPHELD_WITH_EDIT" else (p["proposed_value"] if r["final_value"] in (None,) else r["final_value"])
        if r["outcome"] == "UPHELD" and r["final_value"] == "":
            val = None
        if p["field"] == "architect_engineer" and isinstance(val, str) and ";" in val:
            val = val.split(";")[0].split(" (")[0].strip()  # e.g. "Energoprojekt Praha (detailed design); LOTEP ..."
        if isinstance(val, str) and any(s in val for s in SKIP_IF_CONTAINS):
            skipped.append((iid, p, "AMBIGUOUS_ROLE", val))
            continue
        val = house(p["field"], val) if val not in (None, "") else None
        if p["field"] in ("licensed_until", "planned_retirement") and isinstance(val, str) and val.lower().startswith("indefinite"):
            skipped.append((iid, p, "NOT_A_DATE", val))
            continue
        shown = p["shown"] if p["shown"] not in ("", "None") else None
        if (val or None) == (shown or None):
            continue
        writes.append((iid, p, r, val, shown))

    L = ["-- 033_phase2_pilot.sql",
         "-- Date: 2026-10-14",
         "-- Description: Phase 2 audit pilot (Hungary, Czech Republic, Taiwan + passed licence/retirement dates).",
         "--   Three tiers: 3 Haiku researchers per batch -> Sonnet adjudication -> Opus refutation review with an",
         "--   independent second source. Only changes the Opus tier UPHELD are written; values mapped to house",
         "--   vocabulary. Per-change sources and quotes: audit/phase2/033_changes.psv (local).",
         f"-- Writes: {len(writes)}. Skipped: {len(skipped)} (refuted, unsure, ambiguous role, not a date).",
         "-- Vendor values are appended to the whitelist (verification_2026-07/final_verdicts.psv) in the same change.",
         "-- Backup: nuclear_reactors.db.bak-pre033-20261014", "", "BEGIN TRANSACTION;"]
    with open(P2 / "033_changes.psv", "w", encoding="utf-8", newline="") as fh, \
            open(ROOT / "audit" / "whitelist_033.psv", "w", encoding="utf-8", newline="") as wl:
        w = csv.writer(fh, delimiter="|")
        w.writerow(["item_id", "reactor_db_id", "reactor", "field", "old", "new", "outcome", "source_url", "quote",
                    "second_source_url", "reason"])
        ww = csv.writer(wl, delimiter="|")
        for iid, p, r, val, shown in writes:
            rid, f = int(p["reactor_db_id"]), p["field"]
            tbl, key = ("reactor_details", "reactor_id") if f in DETAILS else ("reactors", "id")
            guard = f"{f} IS NULL" if shown is None else f"{f} = {q(shown)}"
            L.append(f"UPDATE {tbl} SET {f} = {q(val)} WHERE {key} = {rid} AND ({guard});  -- {p['reactor']}")
            w.writerow([iid, rid, p["reactor"], f, shown, val, r["outcome"], r["source_url"], (r["quote"] or "").replace("|", "/"),
                        r["second_source_url"], r["reason"].replace("|", "/").replace("\n", " ")])
            if f in VENDOR and val:
                name = db.execute("SELECT plant_name, unit_number FROM reactors WHERE id = ?", (rid,)).fetchone()
                ww.writerow([rid, name[0], name[1], f, "CONFIRMED", "HIGH", "yes", val,
                             f"{r['source_url']} ; {r['second_source_url'] or ''} (Phase 2 pilot, Opus-upheld 2026-10-14)"])
    L += ["COMMIT;", ""]
    (ROOT / "migrations" / "033_phase2_pilot.sql").write_text("\n".join(L), encoding="utf-8")
    with open(P2 / "033_skipped.psv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|")
        w.writerow(["item_id", "reactor", "field", "shown", "proposed", "why", "detail"])
        for iid, p, why, det in skipped:
            w.writerow([iid, p["reactor"], p["field"], p["shown"], p["proposed_value"], why, (det or "").replace("|", "/")[:400]])
    print(f"{len(writes)} writes, {len(skipped)} skipped")


if __name__ == "__main__":
    main()
