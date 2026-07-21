#!/usr/bin/env python3
# Purpose: merge batch verification verdicts into final per-reactor-field decisions,
#          generate migration 018 + the Noah/Dirk consult package.
# Inputs:  results/batch_*.psv (verdict rows), ../nuclear_reactors.db (reactor ids)
# Outputs: final_verdicts.psv, ../migrations/018_vendor_field_verification.sql,
#          noah_dirk_consult_2026-07.md, merge_report.txt (stdout)
# last_run: 2026-07-20
import glob, os, sqlite3, sys, collections

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "nuclear_reactors.db")
FIELDS = {"constructor", "architect_engineer", "turbine_supplier", "rpv_manufacturer"}
DBCOL = {"rpv_manufacturer": "pressure_vessel_manufacturer"}

# --- load verdicts; gap-fill files (batch_NNb) supersede their primary batch ---
verdicts = {}  # (plant, unit, field) -> dict
def load(path, supersede):
    for ln in open(path, encoding="utf-8", errors="replace"):
        ln = ln.strip()
        if not ln or ln.startswith("#") or ln.startswith("plant|"):
            continue
        p = [x.strip() for x in ln.split("|")]
        if len(p) < 4 or p[2] not in FIELDS:
            continue
        verdict = p[3].upper()
        if verdict not in ("CONFIRMED", "WRONG", "UNVERIFIABLE"):
            continue
        p += [""] * (7 - len(p))
        conf = p[5].upper() or "LOW"
        if conf == "MED-HIGH":
            conf = "HIGH"
        key = (p[0], p[1], p[2])
        if key in verdicts and not supersede:
            continue
        verdicts[key] = {"verdict": verdict, "corrected": p[4], "conf": conf, "src": p[6]}

primaries = sorted(f for f in glob.glob(os.path.join(HERE, "results", "batch_*.psv"))
                   if not f.endswith("b.psv"))
gapfills = sorted(f for f in glob.glob(os.path.join(HERE, "results", "batch_*b.psv")))
for f in primaries:
    load(f, supersede=False)
for f in gapfills:
    load(f, supersede=True)

# --- match to reactor ids ---
con = sqlite3.connect(DB)
rid = {}
for r in con.execute("SELECT id, plant_name, unit_number FROM reactors"):
    rid[(r[1].lower(), str(r[2]).lower())] = r[0]
matched, unmatched = {}, []
for (plant, unit, field), v in verdicts.items():
    k = (plant.lower(), unit.lower())
    if k in rid:
        matched[(rid[k], field)] = (plant, unit, v)
    else:
        unmatched.append((plant, unit, field, v["verdict"]))

# --- classify ---
visible, consult_wrong, consult_lowconf, nulled = [], [], [], []
for (reactor_id, field), (plant, unit, v) in sorted(matched.items()):
    if v["verdict"] == "CONFIRMED" and v["conf"] in ("HIGH", "MED"):
        visible.append((reactor_id, field))
    else:
        nulled.append((reactor_id, field))
        if v["verdict"] == "WRONG":
            consult_wrong.append((plant, unit, field, v))
        elif v["verdict"] == "CONFIRMED":  # LOW confidence
            consult_lowconf.append((plant, unit, field, v))

# any db field value not covered by a verdict (3 reactors lacked detail rows,
# name mismatches, agent omissions) is unattested -> NULL as well
covered = set(matched.keys())
extra_null = []
for r in con.execute("""SELECT d.reactor_id, r.plant_name, r.unit_number,
                               d.constructor, d.architect_engineer,
                               d.turbine_supplier, d.pressure_vessel_manufacturer
                        FROM reactor_details d JOIN reactors r ON r.id = d.reactor_id"""):
    for i, field in enumerate(["constructor", "architect_engineer",
                               "turbine_supplier", "rpv_manufacturer"]):
        if r[3 + i] is not None and (r[0], field) not in covered:
            extra_null.append((r[0], field))

# --- write final verdicts file ---
with open(os.path.join(HERE, "final_verdicts.psv"), "w", encoding="utf-8") as f:
    f.write("reactor_id|plant|unit|field|verdict|confidence|visible|corrected_value|source\n")
    for (reactor_id, field), (plant, unit, v) in sorted(matched.items()):
        vis = "yes" if (reactor_id, field) in set(visible) else "no"
        f.write(f"{reactor_id}|{plant}|{unit}|{field}|{v['verdict']}|{v['conf']}|{vis}|{v['corrected']}|{v['src']}\n")

# --- migration 018 ---
keep = set(visible)
mig = [
    "-- Migration 018: vendor-field verification outcome (constants audit, Option 4)",
    "-- Policy (Griffin 2026-07-20): only CONFIRMED (HIGH/MED confidence) values remain",
    "-- visible. WRONG and UNVERIFIABLE values -> NULL; sourced corrections are NOT",
    "-- applied to public data, they await Noah/Dirk review (noah_dirk_consult_2026-07.md).",
    "-- Full pre-audit values preserved in reactor_details_unverified_archive.",
    "",
    "CREATE TABLE IF NOT EXISTS reactor_details_unverified_archive AS",
    "  SELECT * FROM reactor_details;",
    "",
]
by_field = collections.defaultdict(list)
for reactor_id, field in nulled + extra_null:
    by_field[field].append(reactor_id)
for field, ids in sorted(by_field.items()):
    col = DBCOL.get(field, field)
    ids = sorted(set(ids))
    for i in range(0, len(ids), 200):
        chunk = ",".join(map(str, ids[i:i + 200]))
        mig.append(f"UPDATE reactor_details SET {col} = NULL WHERE reactor_id IN ({chunk});")
with open(os.path.join(HERE, "..", "migrations", "018_vendor_field_verification.sql"),
          "w", encoding="utf-8") as f:
    f.write("\n".join(mig) + "\n")

# --- Noah/Dirk consult package ---
with open(os.path.join(HERE, "noah_dirk_consult_2026-07.md"), "w", encoding="utf-8") as f:
    f.write("# Vendor-field review for Noah & Dirk — 2026-07\n\n")
    f.write("We verified the four supply-chain fields (constructor, architect-engineer,\n"
            "turbine supplier, RPV manufacturer) for all 738 reactors against public\n"
            "sources. Only values we confirmed are shown on the site. Below: (A) values\n"
            "our sources say are WRONG, with the proposed correction — please confirm or\n"
            "refute; (B) values we confirmed only from a weak source. Anything you attest\n"
            "goes back on the site as verified.\n\n")
    f.write(f"## A. Proposed corrections ({len(consult_wrong)})\n\n")
    f.write("| Plant | Unit | Field | Proposed correction | Confidence | Source |\n|---|---|---|---|---|---|\n")
    for plant, unit, field, v in consult_wrong:
        f.write(f"| {plant} | {unit} | {field} | {v['corrected'] or '(unknown — old value wrong)'} | {v['conf']} | {v['src']} |\n")
    f.write(f"\n## B. Weakly-sourced confirmations ({len(consult_lowconf)})\n\n")
    f.write("| Plant | Unit | Field | Value we found | Source |\n|---|---|---|---|---|\n")
    for plant, unit, field, v in consult_lowconf:
        f.write(f"| {plant} | {unit} | {field} | (current db value) | {v['src']} |\n")

print(f"verdict rows merged: {len(verdicts)} (gap-fills superseded primaries where present)")
print(f"matched to reactors: {len(matched)}; unmatched: {len(unmatched)}")
for u in unmatched[:12]:
    print("  UNMATCHED:", u)
print(f"visible (CONFIRMED HIGH/MED): {len(visible)}")
print(f"nulled (WRONG/UNVERIFIABLE/LOW): {len(nulled)}; uncovered non-null values also nulled: {len(extra_null)}")
print(f"consult: {len(consult_wrong)} proposed corrections, {len(consult_lowconf)} weak confirmations")
