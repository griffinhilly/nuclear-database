"""Build the Phase 2 audit pilot work list (deterministic; no AI).

Purpose: the tiered agent audit (docs/audit-plan-2026-10.md, Phase 2 pilot). Produces batches of
  (reactor, field, value shown) items for research agents, mixing in the calibration set blind, so
  the tiers can be scored on known answers before a fleet-wide run.
  Track A: every hard-to-source field for the pilot countries (Hungary, Czech Republic, Taiwan),
           blanks included (agents may propose a sourced fill).
  Track B: operating reactors whose recorded licence end or planned retirement year has passed
           (from scripts/freshness_check.py logic).
  Calibration: audit/calibration.psv (83 items; truth columns NOT passed to agents).
Inputs:  nuclear_reactors.db (read-only), audit/calibration.psv
Outputs: audit/phase2/pilot_batches.json (batches for the workflow), audit/phase2/pilot_items.psv
         (every item with its origin; calibration truth stays only in audit/calibration.psv)
Usage:   python scripts/phase2_build_pilot.py
last_run: 2026-10-14
"""
import csv
import json
import sqlite3
import zlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "audit" / "phase2"
PILOT_COUNTRIES = ("Hungary", "Czech Republic", "Taiwan")
FIELDS = {  # field -> (table, column, what it means for the researcher)
    "cooling_type": ("reactor_details", "cooling_type", "condenser cooling method for THIS unit (e.g. once-through river/sea, natural- or mechanical-draft cooling tower)"),
    "containment_type": ("reactors", "containment_type", "containment design type (e.g. large dry, ice condenser, Mark I/II/III, bubbler-condenser for VVER-440/213)"),
    "constructor": ("reactor_details", "constructor", "main construction contractor (company that built the plant)"),
    "architect_engineer": ("reactor_details", "architect_engineer", "architect-engineer (plant design/engineering firm), NOT the reactor vendor"),
    "turbine_supplier": ("reactor_details", "turbine_supplier", "turbine-generator manufacturer for THIS unit"),
    "pressure_vessel_manufacturer": ("reactor_details", "pressure_vessel_manufacturer", "company that FABRICATED the reactor pressure vessel (not the designer)"),
    "design_series": ("reactors", "design_series", "reactor design series (e.g. VVER-440/V-213, Westinghouse 4-loop, GE BWR/6)"),
    "licensed_until": ("reactors", "licensed_until", "current operating licence end (year or date); renewals count"),
    "planned_retirement": ("reactors", "planned_retirement", "currently announced retirement/closure year, if any"),
}
SIBLINGS = ["status", "gross_capacity_mw", "net_capacity_mw", "thermal_capacity_mw", "construction_start",
            "grid_connection", "commercial_operation", "permanent_shutdown", "owner", "operator"]
BATCH = 18


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(f"file:{ROOT / 'nuclear_reactors.db'}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    rows = {r["id"]: dict(r) for r in db.execute(f"""
        SELECT r.id, r.plant_name, r.unit_number, c.name AS country, r.design_series, r.containment_type,
               r.licensed_until, r.planned_retirement, m.name AS model, {', '.join('r.' + s for s in SIBLINGS)},
               d.cooling_type, d.constructor, d.architect_engineer, d.turbine_supplier, d.pressure_vessel_manufacturer
        FROM reactors r JOIN countries c ON c.id = r.country_id LEFT JOIN models m ON m.id = r.model_id
        LEFT JOIN reactor_details d ON d.reactor_id = r.id""")}

    def ctx(r, field):
        # The item's own field is never shown in context: for calibration items the current DB value
        # is often the truth, and showing it would leak the answer.
        return {k: r.get(k) for k in ["plant_name", "unit_number", "country", "model", "design_series"] + SIBLINGS
                if k != field}

    items = []
    for r in rows.values():
        if r["country"] in PILOT_COUNTRIES:
            for f in FIELDS:
                items.append({"origin": "A", "reactor_db_id": r["id"], "field": f, "shown": r.get(f)})
    for r in rows.values():
        if r["status"] != "Operational":
            continue
        for f in ("licensed_until", "planned_retirement"):
            v = r.get(f)
            if v is not None and int(str(v)[:4]) < 2026 and not any(
                    i["reactor_db_id"] == r["id"] and i["field"] == f for i in items):
                items.append({"origin": "B", "reactor_db_id": r["id"], "field": f, "shown": v})
    cal_map = {"containment": "containment_type", "rpv_manufacturer": "pressure_vessel_manufacturer"}
    for c in csv.DictReader(open(ROOT / "audit" / "calibration.psv", encoding="utf-8"), delimiter="|"):
        f = cal_map.get(c["field"], c["field"])
        items.append({"origin": "CAL", "cal_id": c["cal_id"], "reactor_db_id": int(c["reactor_db_id"]),
                      "field": f, "shown": c["value_shown_to_agent"] or None})

    # Group by plant so one researcher covers one site's sources; order is shuffled deterministically
    # by plant name so calibration items sit among real ones.
    by_plant = defaultdict(list)
    for i in items:
        by_plant[(rows[i["reactor_db_id"]]["country"], rows[i["reactor_db_id"]]["plant_name"])].append(i)
    batches, cur = [], []
    for key in sorted(by_plant, key=lambda k: (zlib.crc32(k[1].encode()) % 997, k)):
        for i in by_plant[key]:
            cur.append(i)
            if len(cur) >= BATCH:
                batches.append(cur)
                cur = []
    if cur:
        batches.append(cur)

    out_batches = []
    with open(OUT / "pilot_items.psv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|")
        w.writerow(["item_id", "batch", "origin", "cal_id", "reactor_db_id", "reactor", "field", "shown"])
        for bi, b in enumerate(batches, 1):
            ob = []
            for k, i in enumerate(b, 1):
                iid = f"B{bi:02d}-{k:02d}"
                r = rows[i["reactor_db_id"]]
                w.writerow([iid, bi, i["origin"], i.get("cal_id", ""), r["id"], f"{r['plant_name']} {r['unit_number']}",
                            i["field"], i["shown"]])
                ob.append({"item_id": iid, "reactor": f"{r['plant_name']} {r['unit_number']}", "context": ctx(r, i["field"]),
                           "field": i["field"], "field_meaning": FIELDS.get(i["field"], ("", "", i["field"]))[2],
                           "value_on_site": i["shown"]})
            out_batches.append({"batch": bi, "items": ob})
    (OUT / "pilot_batches.json").write_text(json.dumps(out_batches, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    from collections import Counter
    print(len(items), "items in", len(batches), "batches;", Counter(i["origin"] for i in items))


if __name__ == "__main__":
    main()
