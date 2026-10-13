"""Build audit batches A/B/E (migrations) and C (research list) from the PRIS diff.

Purpose: turn audit/pris_diff.tsv into reviewed, guarded SQL migrations (2026-10 audit, see
  docs/audit-plan-2026-10.md). Deterministic: every rule below is code, every value is PRIS.
  A = fill blanks (pris_id, first criticality, operator, blank capacities/dates)
  B = adopt PRIS where we differ: non-US capacities (net/reference, gross, thermal) on reactors
      without a capacity_changes history; dates within 31 days or replacing a 1-January placeholder
  E = turbine supplier from PRIS where ours is blank, manufacturers only, mapped to house names;
      also writes the whitelist rows validator check 15 needs
  C = everything that needs research: guard failures, larger date conflicts, statuses,
      capacity conflicts on reactors with documented uprate histories, PRIS-vs-July conflicts
Inputs:  audit/pris_diff.tsv, audit/pris_api/all_reactors.json, nuclear_reactors.db (read-only),
         verification_2026-07/final_verdicts.psv
Outputs: migrations/023_pris_fills.sql, migrations/024_pris_capacity_dates.sql,
         migrations/026_pris_turbine_suppliers.sql, audit/whitelist_026.psv, audit/batch_c_items.tsv
Usage:   python scripts/audit_build_batches.py
last_run: 2026-10-13
"""
import csv
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
AUD = ROOT / "audit"
TODAY = "2026-10-13"
SRC = "IAEA PRIS API (pris-stats.iaea.org), pulled 2026-10-13"

# PRIS turbineSupplierName -> house name. None = not a turbine manufacturer (export agency, utility,
# design institute, placeholder): never written, to avoid the designer-vs-maker error class.
TURBINE = {
    "GENERAL ELECTRIC CO.": "General Electric", "General Electric": "General Electric",
    "GENERAL ELECTRIC CO. / GENERAL ELECTRIC TECHNICAL SERVICES CO.": "General Electric",
    "WESTINGHOUSE ELECTRIC CORPORATION": "Westinghouse",
    "Dongfang Electric Corporation": "Dongfang Electric", "Dongfang Turbine Co., Ltd": "Dongfang Electric",
    "Kharkiv Turbine Factory": "Turboatom", 'Kharkiv Turbine Plant "Turboatom"': "Turboatom",
    "TURBOATOM Kharkiv Turbine Manufacture Plant": "Turboatom",
    "MITSUBISHI HEAVY INDUSTRIES, LTD.": "Mitsubishi Heavy Industries",
    "ALSTOM": "Alstom", "TURBINE: ALSTOM; ALTERNATOR: ACEC": "Alstom", "Arabelle Solutions": "Arabelle Solutions",
    "ALSTHOM ATLANTIQUE": "Alsthom",
    "KRAFTWERK UNION, AG": "KWU", "SIEMENS/KRAFTWERK UNION, AG.": "KWU", "Siemens AG, Power Generation": "Siemens",
    "C.A.PARSONS": "C. A. Parsons", "NEI PARSONS": "NEI Parsons", "NEI-PARSONS": "NEI Parsons",
    "HITACHI, LTD.": "Hitachi", "Japan Hitachi Company.": "Hitachi", "TOSHIBA CORPORATION": "Toshiba",
    "Bharat Heavy Electricals Ltd (BHEL)\nwww.bhel.com": "BHEL", "ALSTOM-BHEL": "Alstom-BHEL",
    "Shanghai Electric Group": "Shanghai Electric", "SHANGHAI ELECTRIC": "Shanghai Electric",
    "Shanghai Turbine Co.": "Shanghai Electric", "Shanghai Turbine Works": "Shanghai Electric",
    "GENERAL ELECTRIC COMPANY (UK)": "GEC", "GEC TURBINE GENERATORS, LTD.": "GEC",
    "Associated Electric Industry (UK)": "AEI", "THE ENGLISH ELECTRIC CO., LTD.": "English Electric",
    "Richardsons Westgarth": "Richardsons Westgarth",
    "STAL-LAVAL": "Stal-Laval", "ASEA-ATOM / STAL-LAVAL": "Stal-Laval",
    "BROWN BOVERI ET CIE": "Brown Boveri (BBC)", "BROWN BOVERI & CIE": "Brown Boveri (BBC)",
    "HARBIN TURBINE COMPANY LIMITED": "Harbin Electric", "HARBIN ELECTRIC CORPORATION": "Harbin Electric",
    "Harbin Electric Co., Ltd.": "Harbin Electric",
    'JOINT-STOCK COMPANY "LENINGRADSKIY METALLICHESKIY ZAVOD"': "Power Machines (LMZ)",
    "PJSC Power Machines": "Power Machines (LMZ)",
    "ŠKODA CONCERN NUCLEAR POWER PLANT WORKS": "Skoda",
    "CANADIAN GENERAL ELECTRIC": "GE Canada", "ALLIS CHALMERS": "Allis-Chalmers",
    "ALLGEMEINE ELEKTRICITAETS-GESELLSCHAFT": "AEG",
    "Doosan Heavy Industries & Construction  and General Electric": "Doosan Heavy Industries / General Electric",
    "GENERAL ELECTRIC CO. / TOSHIBA CORPORATION": "General Electric / Toshiba",
    "GENERAL ELECTRIC CO./ HITACHI, LTD.": "General Electric / Hitachi",
    "TURBINE: COCKERILL-TOSI ; ALTERNATOR: ACEC": "Cockerill-Tosi",
    "Alstom - General Electric (France)\n48, rue Albert Dhalenne \n93400 Saint-Ouen, FRANCE": "Alstom",
    "ANSALDO, SPA.": "Ansaldo", "Franco Tosi meccanica - Legnano(Milano)": "Franco Tosi", "RATEAU": "Rateau",
    "SOCIETE ALSACIENNE DE CONSTRUCTIONS MECANIQUES": "SACM",
    "Turbine was made bij Stork in Hengelo NL\nGenerator was made by HOLEC in Ridderkerk / Slikkeveer NL": "Stork",
    "Bergmann Borsig Berlin": "Bergmann-Borsig",
    '"Electrotiazhmash" Kharkiv': None,  # generator maker, not turbine
}
DATE_COLS = ("construction_start", "first_criticality", "grid_connection", "commercial_operation", "permanent_shutdown")
LOW_EFF = {"GCR", "LWGR", "FBR", "HTGR", "HWGCR", "SGHWR", "OCM", "LMGMR"}


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    db = sqlite3.connect(f"file:{ROOT / 'nuclear_reactors.db'}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    R = {r["id"]: dict(r) for r in db.execute(
        "SELECT r.*, t.code AS tech, c.name AS country FROM reactors r LEFT JOIN technologies t ON t.id = r.technology_id "
        "JOIN countries c ON c.id = r.country_id")}
    has_cc = {r[0] for r in db.execute("SELECT DISTINCT reactor_id FROM capacity_changes")}
    max_gen = {r[0]: r[1] for r in db.execute("SELECT reactor_id, MAX(electricity_gwh) FROM generation_annual GROUP BY reactor_id")}
    used_ids = {r["pris_id"] for r in R.values() if r["pris_id"] is not None}
    pris = {p["id"]: p for p in json.loads((AUD / "pris_api" / "all_reactors.json").read_text(encoding="utf-8"))}
    july = {}
    for row in csv.DictReader(open(ROOT / "verification_2026-07" / "final_verdicts.psv", encoding="utf-8"), delimiter="|"):
        july[(int(row["reactor_id"]), row["field"])] = row
    diffs = defaultdict(dict)
    for r in csv.DictReader(open(AUD / "pris_diff.tsv", encoding="utf-8"), delimiter="\t"):
        diffs[int(r["reactor_id"])][r["field"]] = r

    A, B, E, C, wl = [], [], [], [], []

    def research(rid, field, ours, theirs, why):
        r = R[rid]
        C.append([rid, f"{r['plant_name']} {r['unit_number']}", r["country"], r["status"], field, ours, theirs, why])

    for rid, fields in diffs.items():
        r = R[rid]
        pid = int(next(iter(fields.values()))["pris_id"])
        p = pris[pid]
        set_a, set_b = {}, {}
        # ---- pris_id ----
        if "pris_id" in fields and fields["pris_id"]["class"] == "fill":
            if pid in used_ids:
                research(rid, "pris_id", None, pid, "PRIS id already used by another DB reactor")
            else:
                set_a["pris_id"] = pid
        # ---- first criticality / operator / blank dates ----
        for col in DATE_COLS:
            d = fields.get(col)
            if d and d["class"] == "fill":
                set_a[col] = d["pris_value"]
        if r["operator"] is None and (p["operatorName"] or "").strip():
            set_a["operator"] = " ".join(p["operatorName"].split())
        # ---- capacities ----
        pg, pn, pt = p["grossElectricalCapacity"] or None, p["netElectricalCapacity"] or None, p["thermalPower"] or None
        tech = r["tech"] or ""
        lo = 0.70 if tech in LOW_EFF else 0.85

        def net_ok(net, gross):
            return gross is None or (net <= gross and net >= lo * gross)

        def gross_ok(gross, thermal):
            return thermal is None or tech in LOW_EFF or 0.27 <= gross / thermal <= 0.40

        new_gross = r["gross_capacity_mw"]
        # gross
        d = fields.get("gross_capacity_mw")
        if d and pg and d["class"] != "match":
            if r["country"] == "USA" or rid in has_cc:
                if d["class"].startswith("DIFF"):
                    research(rid, "gross_capacity_mw", r["gross_capacity_mw"], pg,
                             "US capacity rule" if r["country"] == "USA" else "has capacity_changes history")
            elif not gross_ok(pg, pt or r["thermal_capacity_mw"]):
                research(rid, "gross_capacity_mw", r["gross_capacity_mw"], pg, "PRIS gross fails gross/thermal guard")
            elif max_gen.get(rid) and max_gen[rid] / (pg * 8.76) > 1.05:
                research(rid, "gross_capacity_mw", r["gross_capacity_mw"], pg,
                         f"likely derate: PRIS gross would put past output at {max_gen[rid] / (pg * 8.76):.0%} CF; needs capacity_changes history")
            else:
                set_b["gross_capacity_mw"] = pg
                new_gross = pg
        # thermal
        d = fields.get("thermal_capacity_mw")
        if d and pt and d["class"] != "match":
            target = set_a if d["class"] == "fill" else set_b
            if d["class"] != "fill" and (r["country"] == "USA" or rid in has_cc):
                if d["class"].startswith("DIFF"):
                    research(rid, "thermal_capacity_mw", r["thermal_capacity_mw"], pt,
                             "US (NRC licensed power)" if r["country"] == "USA" else "has capacity_changes history")
            elif new_gross and not gross_ok(new_gross, pt):
                research(rid, "thermal_capacity_mw", r["thermal_capacity_mw"], pt, "PRIS thermal fails gross/thermal guard")
            else:
                target["thermal_capacity_mw"] = pt
        # net = reference (house rule outside the US)
        d = fields.get("net_capacity_mw")
        if d and pn and not d["class"].startswith("match"):
            cls = d["class"]
            if cls == "fill" or r["net_capacity_mw"] is None:
                if net_ok(pn, new_gross or pg):
                    set_a["net_capacity_mw"] = pn
                    set_a["reference_power_mw"] = pn
                else:
                    research(rid, "net_capacity_mw", None, pn, f"PRIS net fails net/gross guard (gross {new_gross or pg})")
            elif r["country"] == "USA":
                pass  # NRC > WNA > PRIS for US operating reactors: not adopted, not researched here
            elif rid in has_cc:
                if cls.startswith("DIFF"):
                    research(rid, "net_capacity_mw", r["net_capacity_mw"], pn, "has capacity_changes history")
            elif not net_ok(pn, new_gross):
                research(rid, "net_capacity_mw", r["net_capacity_mw"], pn, f"PRIS net fails net/gross guard (gross {new_gross})")
            else:
                set_b["net_capacity_mw"] = pn
                set_b["reference_power_mw"] = pn
        elif r["reference_power_mw"] is None and r["net_capacity_mw"] is not None and r["country"] != "USA":
            set_a["reference_power_mw"] = r["net_capacity_mw"]
        # ---- dates (all countries) ----
        merged = {c: (str(r[c])[:10] if r[c] else None) for c in DATE_COLS}
        merged.update({k: v for k, v in set_a.items() if k in DATE_COLS})
        for col in ("construction_start", "grid_connection", "commercial_operation", "permanent_shutdown"):
            d = fields.get(col)
            if not d or d["class"] in ("match", "match-year", "fill", "pris-blank"):
                continue
            ours, theirs = d["db_value"], d["pris_value"]
            placeholder = ours.endswith("-01-01") and ours[:4] == theirs[:4]
            if d["class"].startswith("near") or placeholder:
                set_b[col] = theirs
                merged[col] = theirs
            else:
                research(rid, col, ours, theirs, f"date conflict ({d['class']})")
        seq = [merged[c] for c in DATE_COLS if merged.get(c)]
        if any(len(x) == 10 and len(y) == 10 and y < x for x, y in zip(seq, seq[1:])):
            for col in DATE_COLS:
                set_b.pop(col, None)
                set_a.pop(col, None) if col != "first_criticality" else None
            research(rid, "date order", ", ".join(f"{c}={merged[c]}" for c in DATE_COLS if merged.get(c)), "",
                     "dates out of order after applying PRIS")
        # ---- status ----
        d = fields.get("status")
        if d and d["class"] == "DIFF":
            research(rid, "status", d["db_value"], d["pris_value"], "status conflict")
        # ---- turbine supplier (E) ----
        d = fields.get("turbine_supplier")
        if d and d["class"] == "fill":
            raw = p["turbineSupplierName"].strip()
            house = TURBINE.get(raw)
            jv = july.get((rid, "turbine_supplier"))
            if house is None:
                pass  # agency / utility / placeholder: not a manufacturer
            elif jv and jv["verdict"] == "WRONG" and jv["confidence"] == "HIGH" and jv["corrected_value"] \
                    and house.split()[0].lower() not in jv["corrected_value"].lower():
                research(rid, "turbine_supplier", f"July HIGH correction: {jv['corrected_value'][:60]}", house,
                         "PRIS conflicts with a July HIGH-confidence correction")
            else:
                E.append((rid, house, raw))
                wl.append(f"{rid}|{r['plant_name']}|{r['unit_number']}|turbine_supplier|CONFIRMED|HIGH|yes||"
                          f"{SRC}: turbineSupplierName=\"{' '.join(raw.split())}\"; migration 026")
        if set_a:
            A.append((rid, set_a))
        if set_b:
            B.append((rid, set_b))

    def write_mig(name, title, desc, items, backup):
        lines = [f"-- {name}", f"-- Date: {TODAY}", f"-- Description: {title}", *[f"--   {l}" for l in desc],
                 f"-- Source: {SRC}. Built by scripts/audit_build_batches.py from audit/pris_diff.tsv.",
                 f"-- Rows: {len(items)} reactors. Backup: {backup}", "", "BEGIN TRANSACTION;"]
        for rid, sets in items:
            r = R[rid]
            sql = ", ".join(f"{k} = {q(v)}" for k, v in sets.items())
            lines.append(f"UPDATE reactors SET {sql}, updated_at = CURRENT_TIMESTAMP WHERE id = {rid};  "
                         f"-- {r['plant_name']} {r['unit_number']}")
        lines += ["COMMIT;", ""]
        (ROOT / "migrations" / name).write_text("\n".join(lines), encoding="utf-8")

    write_mig("023_pris_fills.sql", "Audit batch A: fill blank fields from PRIS (no existing value overwritten).",
              ["pris_id (new ids checked unique), first_criticality, operator, blank capacities and dates.",
               "Net blanks filled only when PRIS net passes the net/gross guard; reference = net (house rule)."],
              A, "nuclear_reactors.db.bak-pre023-20261013")
    write_mig("024_pris_capacity_dates.sql", "Audit batch B: adopt PRIS where we differ (guarded).",
              ["Non-US gross/thermal/net(=reference) on reactors WITHOUT capacity_changes history, each passing",
               "net/gross (>=0.85, >=0.70 gas/graphite/fast) and gross/thermal (0.27-0.40 LWR/PHWR) guards.",
               "Dates: PRIS adopted when within 31 days or replacing a 1-January placeholder; all countries.",
               "Everything else went to the research list (audit/batch_c_items.tsv)."],
              B, "nuclear_reactors.db.bak-pre024-20261013")
    lines = ["-- 026_pris_turbine_suppliers.sql", f"-- Date: {TODAY}",
             "-- Description: Audit batch E: turbine supplier from PRIS where ours is blank (mostly values hidden",
             "--   since July for lack of a source). Manufacturers only, mapped to house names; export agencies,",
             "--   utilities and design institutes skipped. Whitelisted in verification_2026-07/final_verdicts.psv",
             "--   (rows from audit/whitelist_026.psv) in the same change, per validator check 15.",
             f"-- Source: {SRC}. Rows: {len(E)}.", "", "BEGIN TRANSACTION;"]
    for rid, house, raw in E:
        lines.append(f"UPDATE reactor_details SET turbine_supplier = {q(house)} WHERE reactor_id = {rid};  "
                     f"-- {R[rid]['plant_name']} {R[rid]['unit_number']}")
    lines += ["COMMIT;", ""]
    (ROOT / "migrations" / "026_pris_turbine_suppliers.sql").write_text("\n".join(lines), encoding="utf-8")
    (AUD / "whitelist_026.psv").write_text("\n".join(wl) + "\n", encoding="utf-8")
    with open(AUD / "batch_c_items.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["reactor_id", "reactor", "country", "status", "field", "ours", "pris", "why"])
        w.writerows(C)

    print(f"A: {len(A)} reactors, {sum(len(s) for _, s in A)} values  {Counter(k for _, s in A for k in s)}")
    print(f"B: {len(B)} reactors, {sum(len(s) for _, s in B)} values  {Counter(k for _, s in B for k in s)}")
    print(f"E: {len(E)} turbine values; skipped non-manufacturer names: "
          f"{sum(1 for f in diffs.values() if f.get('turbine_supplier', {}).get('class') == 'fill') - len(E)}")
    print(f"C: {len(C)} research items  {Counter(c[7].split(' (')[0] for c in C)}")


if __name__ == "__main__":
    main()
