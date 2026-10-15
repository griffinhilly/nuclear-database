"""Build one wave of the Phase 2 fleet audit (deterministic; no AI).

Purpose: fleet-wide run of the three-tier agent audit validated by the pilot (docs/audit-plan-2026-10.md).
  Items: every hard-to-source field for the wave's reactors (blanks included); licence end and planned
  retirement only for Operational / Suspended units; items already decided in the pilot are skipped.
  Calibration: the wave's share of audit/calibration.psv (~1/4 each), placed in batches that contain no
  other item from the same plant, so siblings cannot give the answer away. DISPUTED items are left out.
Inputs:  nuclear_reactors.db (read-only), audit/calibration.psv, audit/phase2/pilot_items.psv
Outputs: audit/phase2/wave<N>_batches.json, audit/phase2/wave<N>_items.psv
Usage:   python scripts/phase2_build_wave.py --wave 1
last_run: 2026-10-14
"""
import argparse
import csv
import json
import sqlite3
import zlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "audit" / "phase2"
WAVES = {
    1: ["USA", "Canada", "Mexico", "Brazil", "Argentina"],
    2: ["France", "UK", "Germany", "Sweden", "Spain", "Belgium", "Switzerland", "Finland", "Italy", "Netherlands"],
    3: ["China", "Japan", "India", "South Korea", "Pakistan"],
    4: ["Russia", "Ukraine", "Slovakia", "Bulgaria", "Armenia", "Belarus", "Lithuania", "Kazakhstan", "Romania",
        "Slovenia", "Egypt", "Turkey", "UAE", "Iran", "Bangladesh", "South Africa"],
}
FIELDS = {
    "cooling_type": "condenser cooling method for THIS unit (e.g. once-through river/sea, natural- or mechanical-draft cooling tower)",
    "containment_type": "containment design type; house vocabulary: Large Dry, Large Dry (Double), Mark I, Mark II, Mark III, Ice Condenser, Subatmospheric, Spherical Double, Pressure Suppression (incl. VVER-440/213 bubbler condenser), Pre-Mark I",
    "constructor": "main construction contractor (company that built the plant) - NOT the reactor (NSSS) vendor unless it was also the builder",
    "architect_engineer": "architect-engineer (plant design/engineering firm), NOT the reactor vendor",
    "turbine_supplier": "turbine-generator manufacturer for THIS unit",
    "pressure_vessel_manufacturer": "company that FABRICATED the reactor pressure vessel (not the designer)",
    "design_series": "reactor design series (e.g. VVER-440/V-213, Westinghouse 4-loop, GE BWR/6)",
    "licensed_until": "current operating licence end (year or date); renewals count; 'indefinite' licences: answer BLOCKED and explain",
    "planned_retirement": "currently ANNOUNCED closure year; if a closure plan was withdrawn and none is announced, the right value is empty",
}
SIBLINGS = ["status", "gross_capacity_mw", "net_capacity_mw", "thermal_capacity_mw", "construction_start",
            "grid_connection", "commercial_operation", "permanent_shutdown", "owner", "operator"]
BATCH = 18


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int, required=True)
    w = ap.parse_args().wave
    db = sqlite3.connect(f"file:{ROOT / 'nuclear_reactors.db'}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    rows = {r["id"]: dict(r) for r in db.execute(f"""
        SELECT r.id, r.plant_name, r.unit_number, c.name AS country, r.design_series, r.containment_type,
               r.licensed_until, r.planned_retirement, m.name AS model, {', '.join('r.' + s for s in SIBLINGS)},
               d.cooling_type, d.constructor, d.architect_engineer, d.turbine_supplier, d.pressure_vessel_manufacturer
        FROM reactors r JOIN countries c ON c.id = r.country_id LEFT JOIN models m ON m.id = r.model_id
        LEFT JOIN reactor_details d ON d.reactor_id = r.id""")}
    done = {(int(i["reactor_db_id"]), i["field"]) for i in csv.DictReader(open(OUT / "pilot_items.psv", encoding="utf-8"), delimiter="|")
            if i["origin"] in ("A", "B")}

    items = []
    for r in rows.values():
        if r["country"] not in WAVES[w]:
            continue
        for f in FIELDS:
            if f in ("licensed_until", "planned_retirement") and r["status"] not in ("Operational", "Suspended"):
                continue
            if (r["id"], f) in done:
                continue
            items.append({"origin": "F", "reactor_db_id": r["id"], "field": f, "shown": r.get(f)})

    by_plant = defaultdict(list)
    for i in items:
        r = rows[i["reactor_db_id"]]
        by_plant[(r["country"], r["plant_name"])].append(i)
    batches, cur = [], []
    for key in sorted(by_plant, key=lambda k: (zlib.crc32(k[1].encode()) % 997, k)):
        for i in by_plant[key]:
            cur.append(i)
            if len(cur) >= BATCH:
                batches.append(cur)
                cur = []
    if cur:
        batches.append(cur)

    # Calibration share for this wave: every 4th item offset by wave; DISPUTED excluded.
    cal_map = {"containment": "containment_type", "rpv_manufacturer": "pressure_vessel_manufacturer"}
    cal = [c for c in csv.DictReader(open(ROOT / "audit" / "calibration.psv", encoding="utf-8"), delimiter="|")
           if "expected=DISPUTED" not in c["trap_note"]]
    mine = [c for k, c in enumerate(cal) if k % 4 == w - 1]
    placed = 0
    for k, c in enumerate(mine):
        rid = int(c["reactor_db_id"])
        plant = rows[rid]["plant_name"]
        for j in range(len(batches)):
            b = batches[(k * 7 + j) % len(batches)]
            if all(rows[i["reactor_db_id"]]["plant_name"] != plant for i in b):
                b.append({"origin": "CAL", "cal_id": c["cal_id"], "reactor_db_id": rid,
                          "field": cal_map.get(c["field"], c["field"]), "shown": c["value_shown_to_agent"] or None})
                placed += 1
                break

    out_batches = []
    with open(OUT / f"wave{w}_items.psv", "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh, delimiter="|")
        wr.writerow(["item_id", "batch", "origin", "cal_id", "reactor_db_id", "reactor", "field", "shown"])
        for bi, b in enumerate(batches, 1):
            ob = []
            for k, i in enumerate(b, 1):
                iid = f"W{w}B{bi:03d}-{k:02d}"
                r = rows[i["reactor_db_id"]]
                wr.writerow([iid, bi, i["origin"], i.get("cal_id", ""), r["id"], f"{r['plant_name']} {r['unit_number']}",
                             i["field"], i["shown"]])
                ctx = {k2: r.get(k2) for k2 in ["plant_name", "unit_number", "country", "model", "design_series"] + SIBLINGS
                       if k2 != i["field"] and r.get(k2) is not None}
                ob.append({"item_id": iid, "reactor": f"{r['plant_name']} {r['unit_number']}", "context": ctx,
                           "field": i["field"], "field_meaning": FIELDS.get(i["field"], i["field"]),
                           "value_on_site": i["shown"]})
            out_batches.append({"batch": bi, "items": ob})
    (OUT / f"wave{w}_batches.json").write_text(json.dumps(out_batches, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"wave {w}: {len(items)} fleet items + {placed}/{len(mine)} calibration in {len(batches)} batches")


if __name__ == "__main__":
    main()
