"""Diff the DB against the PRIS API pull, field by field (deterministic; no AI).

Purpose: Phase 1a of the 2026-10 audit (docs/audit-plan-2026-10.md). Matches every PRIS reactor
  to a DB reactor (pris_id first, then normalized name within country, then reviewed aliases),
  then compares status, milestone dates, capacities, owner/operator, model and suppliers.
Inputs:  audit/pris_api/all_reactors.json (scripts/pris_api_pull.py), nuclear_reactors.db (read-only).
Outputs: audit/pris_match.tsv (one row per pairing, with method), audit/pris_diff.tsv (one row per
  compared field), audit/pris_unmatched.txt; summary on stdout.
Usage:   python scripts/pris_api_diff.py
last_run: 2026-10-13
"""
import csv
import difflib
import json
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
AUD = ROOT / "audit"

CC = {  # PRIS countryCode -> DB countries.name (Taiwan is filed under CN in PRIS)
    "AE": "UAE", "AM": "Armenia", "AR": "Argentina", "BD": "Bangladesh", "BE": "Belgium", "BG": "Bulgaria",
    "BR": "Brazil", "BY": "Belarus", "CA": "Canada", "CH": "Switzerland", "CN": "China", "CZ": "Czech Republic",
    "DE": "Germany", "EG": "Egypt", "ES": "Spain", "FI": "Finland", "FR": "France", "GB": "UK", "HU": "Hungary",
    "IN": "India", "IR": "Iran", "IT": "Italy", "JP": "Japan", "KR": "South Korea", "KZ": "Kazakhstan",
    "LT": "Lithuania", "MX": "Mexico", "NL": "Netherlands", "PK": "Pakistan", "RO": "Romania", "RU": "Russia",
    "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "TR": "Turkey", "UA": "Ukraine", "US": "USA",
    "ZA": "South Africa",
}
STATUS = {"Operational": "Operational", "Permanent Shutdown": "Shutdown", "Decommissioning Completed": "Shutdown",
          "Under Construction": "Under Construction", "Suspended Operation": "Suspended"}


GERMAN = str.maketrans({"Ü": "UE", "Ö": "OE", "Ä": "AE", "ü": "ue", "ö": "oe", "ä": "ae", "ß": "ss"})
# Reviewed aliases: normalized PRIS name -> normalized DB plant+unit (MEMORY.md "PRIS renames reactors")
ALIAS = {"XUDAPU1": "XUDABAO1", "XUDAPU2": "XUDABAO2", "XUDAPU3": "XUDABAO3", "XUDAPU4": "XUDABAO4",
         "CHASNUPP5": "CHASHMA5", "KANUPP1": "KARACHI1", "SAEUL3": "SHINKORI5", "SAEUL4": "SHINKORI6",
         "EL4": "BRENNILIS1", "G2": "G22", "G3": "G33", "WINFRITHSGHWR": "WINFRITH1", "HADDAMNECK": "HADDAMNECK1",
         "BRESTOD300": "BREST1", "APS1OBNINSK": "APS1OBNINSK1", "CAREM25": "CAREM251",
         "BR3": "BR31", "XIAPU1": "CFR1", "XIAPU2": "CFR2"}  # Xiapu = CFR-600 site


def norm(s, strip_paren=True):
    s = (s or "").translate(GERMAN)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    if strip_paren:
        s = re.sub(r"\([^)]*\)", "", s)
    return re.sub(r"[^A-Z0-9]", "", s)


def pris_keys(p):
    """Candidate normalized keys for a PRIS unit name (alias, then single-unit plants get a '1')."""
    k = norm(p["unitName"])
    keys = [ALIAS.get(k, k)]
    if not re.search(r"\d$", k) or k in ("THTR300", "BRESTOD300", "CAREM25", "APS1OBNINSK"):
        keys.append(ALIAS.get(k, k) + "1")
    return keys


def d10(v):
    return str(v)[:10] if v else None


def main():
    pris = json.loads((AUD / "pris_api" / "all_reactors.json").read_text(encoding="utf-8"))
    db = sqlite3.connect(f"file:{ROOT / 'nuclear_reactors.db'}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    ours = [dict(r) for r in db.execute("""
        SELECT r.*, c.name AS country, m.name AS model, s.name AS supplier,
               d.turbine_supplier, d.pressure_vessel_manufacturer
        FROM reactors r JOIN countries c ON c.id = r.country_id
        LEFT JOIN models m ON m.id = r.model_id LEFT JOIN suppliers s ON s.id = r.supplier_id
        LEFT JOIN reactor_details d ON d.reactor_id = r.id""")]

    # ---- matching ----
    by_id = {p["id"]: p for p in pris}
    pairs, used_p, used_o = [], set(), set()
    for o in ours:                                   # 1. existing pris_id
        p = by_id.get(o["pris_id"])
        if p:
            pairs.append((o, p, "pris_id")); used_p.add(p["id"]); used_o.add(o["id"])

    def country_of(p):
        return "Taiwan" if "TAIWAN" in p["unitName"].upper() else CC.get(p["countryCode"])

    pkey = defaultdict(list)
    for p in pris:
        if p["id"] not in used_p:
            for k in pris_keys(p):
                pkey[(country_of(p), k)].append(p)
    for o in ours:                                   # 2. normalized name within country
        if o["id"] in used_o:
            continue
        cands = pkey.get((o["country"], norm(o["plant_name"]) + norm(o["unit_number"])), [])
        cands = [p for p in cands if p["id"] not in used_p]
        if len(cands) == 1:
            pairs.append((o, cands[0], "name")); used_p.add(cands[0]["id"]); used_o.add(o["id"])
    # 3. fuzzy within country, same trailing unit token; marked for review
    rest_p = defaultdict(list)
    for p in pris:
        if p["id"] not in used_p:
            rest_p[country_of(p)].append(p)
    for o in ours:
        if o["id"] in used_o:
            continue
        unit = norm(o["unit_number"])
        target = norm(o["plant_name"]) + unit
        scored = []
        for p in rest_p.get(o["country"], []):
            pn = norm(p["unitName"])
            if not pn.endswith(unit):
                continue
            scored.append((difflib.SequenceMatcher(None, target, pn).ratio(), p))
        scored.sort(key=lambda x: -x[0])
        if scored and scored[0][0] >= 0.72 and (len(scored) == 1 or scored[0][0] - scored[1][0] >= 0.08):
            p = scored[0][1]
            pairs.append((o, p, f"fuzzy {scored[0][0]:.2f}")); used_p.add(p["id"]); used_o.add(o["id"])
            rest_p[o["country"]].remove(p)

    with open(AUD / "pris_match.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["reactor_id", "db_name", "country", "db_pris_id", "pris_id", "pris_name", "method"])
        for o, p, m in sorted(pairs, key=lambda x: x[2]):
            w.writerow([o["id"], f"{o['plant_name']} {o['unit_number']}", o["country"], o["pris_id"], p["id"], p["unitName"], m])
    un_o = [o for o in ours if o["id"] not in used_o]
    un_p = [p for p in pris if p["id"] not in used_p]
    with open(AUD / "pris_unmatched.txt", "w", encoding="utf-8") as f:
        f.write(f"DB reactors with no PRIS match ({len(un_o)}):\n")
        for o in sorted(un_o, key=lambda o: (o["country"], o["plant_name"])):
            f.write(f"  {o['country']:14} {o['plant_name']} {o['unit_number']}  [{o['status']}] pris_id={o['pris_id']}\n")
        f.write(f"\nPRIS reactors with no DB match ({len(un_p)}):\n")
        for p in sorted(un_p, key=lambda p: (p["countryCode"], p["unitName"])):
            f.write(f"  {p['countryCode']} {p['id']:>5} {p['unitName']}  [{p['statusName']}] net={p['netElectricalCapacity']}\n")

    # ---- field diffs ----
    rows = []

    def add(o, p, field, ov, pv, cls):
        rows.append([o["id"], f"{o['plant_name']} {o['unit_number']}", o["country"], o["status"], p["id"], field,
                     "" if ov is None else ov, "" if pv is None else pv, cls])

    for o, p, _ in pairs:
        if o["pris_id"] != p["id"]:
            add(o, p, "pris_id", o["pris_id"], p["id"], "fill" if o["pris_id"] is None else "DIFF")
        ps = STATUS.get(p["statusName"], p["statusName"])
        add(o, p, "status", o["status"], ps, "match" if ps == o["status"] else "DIFF")
        for col, key in (("construction_start", "constructionDate"), ("first_criticality", "criticalityDate"),
                         ("grid_connection", "gridDate"), ("commercial_operation", "commercialDate"),
                         ("permanent_shutdown", "shutdownDate")):
            ov, pv = d10(o[col]), d10(p[key])
            if not ov and not pv:
                continue
            if not pv:
                cls = "pris-blank"
            elif not ov:
                cls = "fill"
            elif ov == pv:
                cls = "match"
            elif len(ov) == 4 and pv.startswith(ov):
                cls = "match-year"
            else:
                try:
                    from datetime import date
                    gap = abs((date.fromisoformat(ov) - date.fromisoformat(pv)).days)
                except ValueError:
                    gap = 9999
                cls = "near (<=31d)" if gap <= 31 else ("DIFF-year" if ov[:4] != pv[:4] else "DIFF")
            add(o, p, col, ov, pv, cls)
        for col, key in (("thermal_capacity_mw", "thermalPower"), ("gross_capacity_mw", "grossElectricalCapacity"),
                         ("net_capacity_mw", "netElectricalCapacity"), ("reference_power_mw", "netElectricalCapacity")):
            ov, pv = o[col], p[key]
            if ov is None and not pv:
                continue
            if not pv:
                cls = "pris-blank"
            elif ov is None:
                cls = "fill"
            else:
                gap = abs(ov - pv)
                cls = "match" if gap <= 1 else ("near (<=2%)" if gap <= max(10, 0.02 * pv) else "DIFF")
                if cls != "match" and o["country"] == "USA" and col in ("net_capacity_mw", "reference_power_mw"):
                    cls += " [US: NRC>WNA>PRIS rule]"
            add(o, p, col, ov, pv, cls)
        for col, key in (("owner", "ownerName"), ("operator", "operatorName"), ("model", "model"),
                         ("supplier", "reactorSupplierName"), ("turbine_supplier", "turbineSupplierName")):
            ov, pv = o[col], (p[key] or "").strip() or None
            if not ov and not pv:
                continue
            cls = "pris-blank" if not pv else ("fill" if not ov else ("match" if norm(ov) == norm(pv) else "text-differs"))
            add(o, p, col, ov, pv, cls)

    with open(AUD / "pris_diff.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["reactor_id", "db_name", "country", "db_status", "pris_id", "field", "db_value", "pris_value", "class"])
        w.writerows(rows)

    print(f"PRIS {len(pris)} | DB {len(ours)} | matched {len(pairs)} "
          f"({Counter(m.split()[0] for _, _, m in pairs)}) | unmatched DB {len(un_o)}, PRIS {len(un_p)}")
    summary = defaultdict(Counter)
    for r in rows:
        summary[r[5]][r[8]] += 1
    for field, c in summary.items():
        print(f"  {field:22} " + ", ".join(f"{k}={v}" for k, v in c.most_common()))


if __name__ == "__main__":
    main()
