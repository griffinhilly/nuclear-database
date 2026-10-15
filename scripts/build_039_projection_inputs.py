"""Build migration 039: closure dates with their basis, commissioning milestones, and status fixes.

Purpose: data behind the projection range (app.py fleet_projection), from the 2026-10-15 research.
Inputs:  audit/projection/closures_*.psv, audit/projection/uc_milestones_*.psv (research, one row per unit,
           verbatim quote + URL), audit/projection/qc_*.tsv (scripts/quote_check.py results for those files),
         a DB with 036-038 applied (default audit/change_history/_tmp/pending.db) for guards and current values.
Outputs: migrations/039_projection_inputs.sql, audit/projection/039_rows.psv (every decision, for the review page).
Rules:
  Closures (planned_retirement + planned_retirement_basis + planned_retirement_source):
    LAW_POLICY / OWNER_DECISION / SAFETY_CONDITION with a FOUND/PARTIAL quote -> written.
    LICENCE_END -> basis LICENCE_RENEWAL_PENDING when the row says a renewal/extension is being sought
      (not a scheduled closure; neither scenario closes it), else LICENCE_END.
    REFUTED -> planned_retirement cleared if we hold one (unless a later draft already set the new value).
    UNCONFIRMED / unverified quote -> no write; listed on the review page.
  Milestones (commissioning_milestone/_date/_source) for Under Construction units with a FOUND/PARTIAL quote.
  GRID milestone with a full date -> status Operational + grid_connection (the 032 miss, e.g. Guohe One 2).
  HOLD (below) overrides any row by hand, with a reason.
last_run: 2026-10-15
"""
import csv
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "audit" / "projection"
DB = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "audit" / "change_history" / "_tmp" / "pending.db"
WRITE_BASES = ("LAW_POLICY", "OWNER_DECISION", "SAFETY_CONDITION")
MILESTONES = ("GRID", "CRITICALITY", "FUEL_LOAD", "HOT_TESTS", "COLD_TESTS", "MAJOR_EQUIPMENT", "CIVIL", "PAUSED")
RENEWAL = re.compile(r"renew|extension|extend|apply|applied|request|seek|approved|pursu|EIA|permit", re.I)
W = "closures_world_2026-10-15"
HOLD = {    # (file stem, db_id) -> reason; row is listed, nothing written
    (W, 47): "refurbishment outage from Sept 2026, not a closure (units return after refurbishment)",
    (W, 48): "refurbishment outage from Sept 2026, not a closure (units return after refurbishment)",
    (W, 49): "refurbishment outage from Sept 2026, not a closure (units return after refurbishment)",
    (W, 50): "refurbishment outage from Sept 2026, not a closure (units return after refurbishment)",
    ("uc_milestones_china_2026-10-15", 54): "CFR 1 criticality rests on one unofficial 2023 report (IPFM); CNNC has "
                                            "announced nothing, so it is not high-confidence enough for the conservative line",
}
# Licence ends are not scheduled closures (renewal is sought or routine), except where the owner has said the
# unit retires at licence end: Rosatom retires each old RBMK as its replacement unit enters service.
BASIS_OVERRIDE = {
    (W, 378): ("OWNER_DECISION", "Kursk 4: old Kursk units scheduled to shut by 2031 as Kursk II replaces them"),
    (W, 383): ("OWNER_DECISION", "Leningrad 3: licence to 2030; replaced by Leningrad II unit 7"),
}
# On the grid but the source date is approximate: day-level date needed by the age and history rules.
GRID_DATE_OVERRIDE = {
    730: ("2025-09-01", "WNA reactor database first grid connection (WNA marks it approximate); China NEA "
                        "'China Nuclear Power Development Report 2026' lists Guohe One unit 2 grid-connected in 2025"),
}


def load(pattern):
    rows = []
    for f in sorted(P.glob(pattern)):
        qc = {}
        qf = P / f"qc_{f.stem.split('_2026')[0]}.tsv"
        if qf.exists():
            for r in csv.DictReader(open(qf, encoding="utf-8"), delimiter="\t"):
                qc[int(r["row"])] = r["status"]
        qb = P / f"qcb_{f.stem.split('_2026')[0]}.tsv"   # browser second pass (scripts/quote_check_browser.py)
        if qb.exists():
            for r in csv.DictReader(open(qb, encoding="utf-8"), delimiter="\t"):
                qc[int(r["item_id"])] = r["final"]
        for n, r in enumerate(csv.DictReader(open(f, encoding="utf-8"), delimiter="|"), start=1):
            r["_file"], r["_row"], r["_qc"] = f.stem, n, qc.get(n, "UNCHECKED")
            rows.append(r)
    return rows


def sq(v):
    return "NULL" if v is None else "'" + str(v).replace("'", "''") + "'"


def main():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    db = {r["id"]: dict(r) for r in c.execute("SELECT * FROM reactors")}
    name = lambda i: f"{db[i]['plant_name']} {db[i]['unit_number']}" if i in db else "?"
    sql, log = [], []

    def note(kind, r, action, detail=""):
        log.append([kind, r.get("db_id"), r.get("unit"), r.get("_file"), r.get("_qc"), action, detail])

    for r in load("closures_*.psv"):
        try:
            i = int(r["db_id"])
        except ValueError:
            note("closure", r, "SKIP", "no db id"); continue
        if i not in db:
            note("closure", r, "SKIP", "db id not found"); continue
        if (r["_file"], i) in HOLD:
            note("closure", r, "HOLD", HOLD[(r["_file"], i)]); continue
        ok = r["_qc"] in ("FOUND", "PARTIAL")
        basis, d, cur = r["basis"].strip(), r["closure_date"].strip(), db[i]["planned_retirement"]
        if (r["_file"], i) in BASIS_OVERRIDE:
            basis = BASIS_OVERRIDE[(r["_file"], i)][0]
        elif basis == "LICENCE_END":
            basis = "LICENCE_RENEWAL_PENDING" if RENEWAL.search(r.get("extension_status") or "") else "LICENCE_END_ONLY"
        if not ok:
            note("closure", r, "NO WRITE", f"quote {r['_qc']}"); continue
        if basis in WRITE_BASES:
            if not re.match(r"^\d{4}(-\d{2}){0,2}$", d):
                note("closure", r, "SKIP", f"bad date {d}"); continue
            sql.append(f"UPDATE reactors SET planned_retirement = {sq(d)}, planned_retirement_basis = {sq(basis)}, "
                       f"planned_retirement_source = {sq(r['source_url'])}, updated_at = CURRENT_TIMESTAMP "
                       f"WHERE id = {i} AND planned_retirement IS {sq(cur)};  -- {name(i)}")
            note("closure", r, "WRITE", f"{cur} -> {d} ({basis})")
        elif basis in ("LICENCE_RENEWAL_PENDING", "LICENCE_END_ONLY"):
            why = "renewal sought" if basis == "LICENCE_RENEWAL_PENDING" else "no renewal found yet"
            note("closure", r, "INFO", f"licence end {d} ({why}): not a scheduled closure; no write")
        elif basis == "REFUTED":
            if cur is None:
                note("closure", r, "NONE", "already blank")
            elif d and re.match(r"^\d{4}", d) and str(cur)[:4] == d[:4]:
                note("closure", r, "NONE", f"draft already holds the new value {cur}")
            else:
                sql.append(f"UPDATE reactors SET planned_retirement = NULL, planned_retirement_basis = NULL, "
                           f"planned_retirement_source = {sq(r['source_url'])}, updated_at = CURRENT_TIMESTAMP "
                           f"WHERE id = {i} AND planned_retirement IS {sq(cur)};  -- {name(i)} (refuted)")
                note("closure", r, "CLEAR", f"{cur} -> blank")
        else:
            note("closure", r, "NO WRITE", basis)

    for r in load("uc_milestones_*.psv"):
        try:
            i = int(r["db_id"])
        except ValueError:
            note("milestone", r, "SKIP", "no db id (e.g. NEW)"); continue
        if i not in db or db[i]["status"] != "Under Construction":
            note("milestone", r, "SKIP", f"not UC in db ({db.get(i, {}).get('status')})"); continue
        if (r["_file"], i) in HOLD:
            note("milestone", r, "HOLD", HOLD[(r["_file"], i)]); continue
        m = r["milestone"].strip()
        dm = re.search(r"\d{4}(-\d{2}){0,2}", r["milestone_date"] or "")
        md = (("<" if r["milestone_date"].strip().startswith("<") else "") + dm.group(0)) if dm else ""
        if m not in MILESTONES or r["_qc"] not in ("FOUND", "PARTIAL"):
            note("milestone", r, "NO WRITE", f"{m} quote {r['_qc']}"); continue
        sql.append(f"UPDATE reactors SET commissioning_milestone = {sq(m)}, commissioning_milestone_date = {sq(md or None)}, "
                   f"commissioning_source = {sq(r['source_url'])} WHERE id = {i};  -- {name(i)}")
        note("milestone", r, "WRITE", f"{m} {md}")
        if m == "GRID":
            if i in GRID_DATE_OVERRIDE:
                md = GRID_DATE_OVERRIDE[i][0]
                note("status", r, "NOTE", GRID_DATE_OVERRIDE[i][1])
            if re.match(r"^\d{4}-\d{2}-\d{2}$", md):
                sql.append(f"UPDATE reactors SET status = 'Operational', grid_connection = {sq(md)}, updated_at = CURRENT_TIMESTAMP "
                           f"WHERE id = {i} AND status = 'Under Construction' AND grid_connection IS NULL;  -- {name(i)} on the grid")
                note("status", r, "WRITE", f"Under Construction -> Operational, grid {md}")
            else:
                note("status", r, "HOLD", f"on the grid but date not to the day ({md})")

    # Malformed expected dates found by the research (value '2027-20'; the year part is the announced year).
    for i in [k for k, v in db.items() if v.get("expected_operation") and not re.match(r"^\d{4}(-(0[1-9]|1[0-2])(-(0[1-9]|[12]\d|3[01]))?)?$", v["expected_operation"])]:
        fixed = db[i]["expected_operation"][:4]
        sql.append(f"UPDATE reactors SET expected_operation = {sq(fixed)} WHERE id = {i} "
                   f"AND expected_operation = {sq(db[i]['expected_operation'])};  -- {name(i)} (malformed date)")
        log.append(["cleanup", i, name(i), "", "", "WRITE", f"expected_operation {db[i]['expected_operation']} -> {fixed}"])

    head = f"""-- 039_projection_inputs.sql
-- Date: 2026-10-15 (DRAFT, not approved)
-- Description: data behind the projection range. (1) New columns: planned_retirement_basis
--   (LAW_POLICY / OWNER_DECISION / SAFETY_CONDITION), planned_retirement_source,
--   commissioning_milestone (GRID / CRITICALITY / FUEL_LOAD / HOT_TESTS / COLD_TESTS / MAJOR_EQUIPMENT / CIVIL / PAUSED),
--   commissioning_milestone_date, commissioning_source. (2) Sourced closure dates with their basis; refuted
--   dates cleared. (3) Commissioning milestones for reactors under construction. (4) Reactors found on the
--   grid -> Operational (incl. Shidaowan Guohe One 2, recorded CONNECTED by 032 but never flipped).
--   (5) Malformed expected_operation values (2027-20) cut to the year.
-- Research + verbatim quotes: audit/projection/closures_*.psv, uc_milestones_*.psv; quote re-check by
--   scripts/quote_check.py (qc_*.tsv); decisions: audit/projection/039_rows.psv. Applies after 036-038.
-- Built by scripts/build_039_projection_inputs.py. Backup first: nuclear_reactors.db.bak-pre039-<date>
"""
    body = ["BEGIN TRANSACTION;"] + [f"ALTER TABLE reactors ADD COLUMN {col} TEXT;" for col in (
        "planned_retirement_basis", "planned_retirement_source", "commissioning_milestone",
        "commissioning_milestone_date", "commissioning_source")] + sql + ["COMMIT;"]
    (ROOT / "migrations" / "039_projection_inputs.sql").write_text(head + "\n" + "\n".join(body) + "\n", encoding="utf-8")
    with open(P / "039_rows.psv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="|")
        w.writerow(["kind", "db_id", "unit", "file", "quote_check", "action", "detail"])
        w.writerows(log)
    from collections import Counter
    print("statements", len(sql), Counter((k, a) for k, _, _, _, _, a, _ in log))


if __name__ == "__main__":
    main()
