"""Build audit/calibration.psv: known-answer items for the multi-agent data audit (Phase 0).

Purpose: ~80 (value shown, truth) pairs with a locally recorded URL + quote for every truth.
Inputs (all read-only): nuclear_reactors.db, .bak-pre022/.bak-pre023/.bak-pre028/.bak-noah-20260528,
  reactor_details_unverified_archive, audit/batch_c/triage.json, audit/pris_api/<CC>.json,
  review/nucleopedia/export/*.xml, migrations/022, migrations/025, verification_2026-07/final_verdicts.psv,
  verification_2026-07/noah_dirk_consult_2026-07.md, verification_2026-07/spec_final_verdicts.psv.
Outputs: audit/calibration.psv
Every shown value is re-read from its database / ledger, and every quote is re-found in its local
file; any mismatch aborts the build.
last_run: 2026-10-14
"""
import html, json, re, sqlite3, sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\griff\Projects\reg\nuclear-database")


def ro(name):
    return sqlite3.connect(f"file:{ROOT / name}?mode=ro", uri=True)


DB = {"current": ro("nuclear_reactors.db"), "bak22": ro("nuclear_reactors.db.bak-pre022-20261013"),
      "bak23": ro("nuclear_reactors.db.bak-pre023-20261013"), "bak28": ro("nuclear_reactors.db.bak-pre028-20261013"),
      "baknoah": ro("nuclear_reactors.db.bak-noah-20260528")}
DETAIL = {"cooling_type", "constructor", "architect_engineer", "turbine_supplier", "pressure_vessel_manufacturer"}
TRIAGE = json.load(open(ROOT / "audit/batch_c/triage.json", encoding="utf-8"))
FV = (ROOT / "verification_2026-07/final_verdicts.psv").read_text(encoding="utf-8")
NOAH = (ROOT / "verification_2026-07/noah_dirk_consult_2026-07.md").read_text(encoding="utf-8")
SPEC = (ROOT / "verification_2026-07/spec_final_verdicts.psv").read_text(encoding="utf-8")
MIG = {n: (ROOT / "migrations" / n).read_text(encoding="utf-8") for n in
       ["022_paks_cooling_temelin_capacity_taishan_rpv.sql", "025_missing_uc_units.sql"]}
NPX = html.unescape((ROOT / "review/nucleopedia/export/Nucleopedia-20261013172215.xml").read_text(encoding="utf-8"))
NP = {}  # Reaktorbox NAME -> (page title, {key: raw line})
for title, body in re.findall(r"<title>(.*?)</title>(.*?)</page>", NPX, flags=re.S):
    for z in re.findall(r"\{\{Reaktorbox/Zelle(.*?)\n\}\}", body, flags=re.S):
        lines = {}
        for ln in z.split("\n"):
            m = re.match(r"\|([^=]+?)\s*=", ln)
            if m:
                lines[m.group(1).strip()] = ln.strip()
        name = re.sub(r"<ref.*", "", lines.get("NAME", "").split("=", 1)[-1]).strip()
        NP[name] = (title, lines)
PRIS = {}


def db_value(src, rid, field):
    con = DB[src]
    if field in DETAIL:
        r = con.execute(f"SELECT {field} FROM reactor_details WHERE reactor_id=?", (rid,)).fetchone()
    else:
        r = con.execute(f"SELECT {field} FROM reactors WHERE id=?", (rid,)).fetchone()
    return None if r is None else r[0]


def norm(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


# ---------- truth-source helpers (each returns url, quote and asserts the quote is in the local file) ----------
def pris(cc, unit, keys):
    if cc not in PRIS:
        PRIS[cc] = ((ROOT / f"audit/pris_api/{cc}.json").read_text(encoding="utf-8"))
    raw = PRIS[cc]
    rec = next(r for r in json.loads(raw) if r["unitName"] == unit)
    parts = [f'"unitName": {json.dumps(unit, ensure_ascii=False)}'] + \
            [f'"{k}": {json.dumps(rec[k], ensure_ascii=False)}' for k in keys]
    for p in parts:
        assert p in raw, (cc, p)
    return (f"https://pris-stats.iaea.org/reactor/reactors-by-code/{cc}",
            "; ".join(parts) + f" [IAEA PRIS API record id {rec['id']}, pulled 2026-10-13, audit/pris_api/{cc}.json]")


def nucleo(name, keys):
    title, lines = NP[name]
    q = [lines[k] for k in keys]
    for s in q:
        assert s in NPX, s
    # drop the leading wikitext pipe, alignment padding, and any trailing {{Konvert|...}} template (pressure)
    q = [re.sub(r"\s{2,}", " ", s).lstrip("|").split("{{")[0].rstrip(" ,") for s in q]
    return (f"https://de.nucleopedia.org/wiki/{title.replace(' ', '_')}",
            f"Reaktorbox {name}: " + " ; ".join(q) + " [Nucleopedia export 2026-10-13, review/nucleopedia/export/]")


def triage(i, rid, field_hint):
    x = TRIAGE[i]
    assert x["qstatus"] == "FOUND", (i, x["qstatus"])
    assert str(x["reactor_id"]) == str(rid), (i, x["reactor_id"], rid)
    assert x["field"] == field_hint, (i, x["field"], field_hint)
    return x["source_url"], x["quote"] + " [audit/batch_c quote_check FOUND]"


def ledger(text, url, quote, label):
    assert quote in text, (label, quote)
    return url, f"{quote} [{label}]"


def mig(name, url, quote):
    return ledger(MIG[name], url, quote, f"migrations/{name} header")


def fv(url, quote):
    return ledger(FV, url, quote, "verification_2026-07/final_verdicts.psv, CONFIRMED/HIGH visible=yes")


T = lambda i, rid, f: triage(i, rid, f)
WNN_TAISHAN = "https://world-nuclear-news.org/articles/construction-milestone-at-taishan-2-epr"
BME = "https://pp.bme.hu/ci/article/download/3869/2974/7627"

# ---------- items ----------
# (reactor_db_id, field, shown_from, shown_value, truth_value, label, source(url,quote), trap_note)
# shown_from: current | bak22 | bak23 | bak28 | baknoah | archive | batchc-ours | planned(pre-025) | pris | ledger
I = []
add = lambda *a: I.append(a)

# ===== WRONG: planted old values with the corrected truth =====
add(234, "cooling_type", "bak22", "Cooling tower (natural draft)", "Once-through (river)", "WRONG",
    mig("022_paks_cooling_temelin_capacity_taishan_rpv.sql", BME, "fresh-water cooled ... returned to the Danube"),
    "Per-plant value copied onto every unit; Danube once-through (Paks II EIA corroborates).")
add(236, "cooling_type", "bak22", "Cooling tower (natural draft)", "Once-through (river)", "WRONG",
    nucleo("Paks-3", ["KÜHLUNG"]), "Same Paks error as unit 1; second source.")
add(120, "net_capacity_mw", "bak22", "1086", "1027", "WRONG",
    pris("CZ", "TEMELIN-1", ["grossElectricalCapacity", "netElectricalCapacity"]), "Gross stored as net (net > gross 1080 in DB).")
add(121, "net_capacity_mw", "bak22", "1086", "1029", "WRONG",
    pris("CZ", "TEMELIN-2", ["grossElectricalCapacity", "netElectricalCapacity"]), "Gross stored as net.")
add(116, "net_capacity_mw", "bak23", "510", "479", "WRONG",
    pris("CZ", "DUKOVANY-1", ["grossElectricalCapacity", "netElectricalCapacity"]), "Old net 510 exceeded old gross 500 (net > gross).")
add(101, "pressure_vessel_manufacturer", "archive", "Mitsubishi Heavy Industries", "Dongfang Electric", "WRONG",
    ledger(FV, WNN_TAISHAN, '"the pressure vessel by Dongfang Electric Co (DEC)"', "verification_2026-07/final_verdicts.psv CORRECTED (migration 022)"),
    "Unit 1 vessel (MHI) copied onto unit 2.")
add(120, "pressure_vessel_manufacturer", "archive", "Izhora Plants", "Škoda JS (Škoda Plzeň)", "WRONG",
    nucleo("Temelín-1", ["REAKTORDRUCKBEHÄLTER"]), "July HIGH correction (Czech Wikipedia: vessel made by Škoda Plzeň) agrees; currently hidden.")
add(548, "turbine_supplier", "archive", "Power Machines (LMZ)", "Turboatom", "WRONG",
    nucleo("Saporischschja-1", ["TURBOSATZ"]), "July correction to Turboatom backed by Nucleopedia.")
add(678, "turbine_supplier", "archive", "Westinghouse", "General Electric", "WRONG",
    pris("US", "VOGTLE-1", ["turbineSupplierName"]), "Reactor vendor copied into turbine field; Nucleopedia also GE.")
add(126, "turbine_supplier", "archive", "Alstom", "Siemens", "WRONG",
    pris("FI", "OLKILUOTO-3", ["turbineSupplierName"]), "Alstom Arabelle is Flamanville 3, not OL3; Nucleopedia also Siemens.")
add(207, "pressure_vessel_manufacturer", "archive", "Rotterdam Dockyard (RDM)", "GHH Oberhausen", "WRONG",
    nucleo("Biblis-A", ["REAKTORDRUCKBEHÄLTER"]), "July: Biblis absent from RDM's own build list.")
add(230, "turbine_supplier", "archive", "KWU", "AEG", "WRONG",
    nucleo("Gundremmingen A", ["TURBOSATZ"]), "Anachronism: KWU founded 1969, unit on grid 1966.")
add(230, "constructor", "archive", "Kraftwerk Union (KWU)", "AEG, General Electric, Hochtief", "WRONG",
    nucleo("Gundremmingen A", ["AUFTRAGNEHMER"]), "Anachronism: KWU founded 1969.")
add(373, "design_series", "baknoah", "VVER-440/230", "VVER-440/213", "WRONG",
    pris("RU", "KOLA-3", ["model"]), "Units 1-2 series homogenized onto units 3-4 (Noah review, migration 003).")
add(29, "thermal_capacity_mw", "bak23", "2456", "2620", "WRONG", T(2, 29, "thermal_capacity_mw"), "")
add(291, "commercial_operation", "bak23", "1993-01-27", "1993-09-03", "WRONG", T(23, 291, "commercial_operation"),
    "Old value is the grid-connection date.")
add(351, "gross_capacity_mw", "bak23", "38", "35", "WRONG", T(29, 351, "gross_capacity_mw"), "")
add(360, "permanent_shutdown", "bak23", "1990-01-01", "1989-09-25", "WRONG", T(39, 360, "permanent_shutdown"),
    "1-January placeholder; source confirms year 1989, exact day from PRIS.")
add(389, "construction_start", "bak23", "1971-12-27", "1967-07-01", "WRONG", T(65, 389, "construction_start"),
    "Old value equals the grid date (date-order violation).")
add(395, "thermal_capacity_mw", "bak23", "3200", "3120", "WRONG", T(69, 395, "thermal_capacity_mw"), "")
add(405, "net_capacity_mw", "bak23", "110", "93", "WRONG", T(70, 405, "net_capacity_mw"), "")
add(531, "commercial_operation", "bak23", "1971-01-24", "1971-11-01", "WRONG", T(86, 531, "commercial_operation"),
    "Old value is the grid-connection date.")
add(675, "gross_capacity_mw", "bak23", "879", "829", "WRONG", T(98, 675, "gross_capacity_mw"), "WNA mirrors PRIS here (one effective source).")
add(692, "status", "bak28", "Under Construction", "Operational", "WRONG", T(8, 692, "status"), "Grid-connected 2026-03-12; stale status.")
add(263, "status", "bak28", "Suspended", "Operational", "WRONG", T(19, 263, "status"), "Back on grid 2026 after refurbishment.")
add(743, "status", "planned(pre-025)", "Planned", "Under Construction", "WRONG",
    pris("CN", "TAIPINGLING-4", ["statusName", "constructionDate"]), "Held as planned_reactors row id 186 before migration 025.")
add(746, "status", "planned(pre-025)", "Planned", "Under Construction", "WRONG",
    pris("KR", "SHIN-HANUL-4", ["statusName", "constructionDate"]), "Held as planned_reactors row id 269 before migration 025.")
add(482, "thermal_capacity_mw", "bak23", "3200", "3983", "WRONG",
    pris("AE", "BARAKAH-1", ["thermalPower"]), "APR-1400 thermal; 3200 is far off.")
add(490, "construction_start", "bak23", "1953-01-01", "1953-08-01", "WRONG",
    pris("GB", "CALDER HALL-1", ["constructionDate"]), "1-January placeholder.")
add(470, "grid_connection", "bak23", "1968-01-01", "1968-01-29", "WRONG",
    pris("CH", "LUCENS", ["gridDate"]), "1-January placeholder.")
add(721, "construction_start", "bak23", "2024-01-01", "2024-01-23", "WRONG",
    pris("EG", "EL DABAA-4", ["constructionDate"]), "1-January placeholder.")
add(26, "thermal_capacity_mw", "bak23", "3000", "3120", "WRONG",
    pris("BG", "KOZLODUY-5", ["thermalPower"]), "Pre-uprate (104%) rating; stale.")

# ===== CORRECT: current (or ledger) values confirmed by a found quote or a structured source =====
add(355, "commercial_operation", "current", None, "1988-01-18", "CORRECT", T(35, 355, "commercial_operation"), "PRIS says 1987-10-22 (unsupported).")
add(361, "commercial_operation", "current", None, "1981-11-01", "CORRECT", T(40, 361, "commercial_operation"), "PRIS says 1980-11-01.")
add(740, "construction_start", "current", None, "2026-01-31", "CORRECT", T(60, 740, "construction_start"), "PRIS API says 2025-12-24 (planned date).")
add(388, "permanent_shutdown", "current", None, "1990-08-29", "CORRECT", T(64, 388, "permanent_shutdown"), "PRIS says 1990-01-23.")
add(562, "commercial_operation", "current", None, "1974-08-01", "CORRECT", T(90, 562, "commercial_operation"), "PRIS says 1974-12-20.")
add(443, "grid_connection", "current", None, "1981-05-01", "CORRECT", pris("ES", "ALMARAZ-1", ["gridDate"]), "")
add(12, "commercial_operation", "current", None, "1975-02-15", "CORRECT", pris("BE", "DOEL-1", ["commercialDate"]), "")
add(120, "gross_capacity_mw", "current", None, "1086", "CORRECT",
    pris("CZ", "TEMELIN-1", ["grossElectricalCapacity", "netElectricalCapacity"]), "Fixed by migration 022; 1086 is gross, not net.")
add(410, "net_capacity_mw", "current", None, "696", "CORRECT", pris("SI", "KRSKO", ["netElectricalCapacity"]), "")
add(426, "net_capacity_mw", "current", None, "640", "CORRECT", pris("KR", "KORI-2", ["netElectricalCapacity"]), "")
add(342, "gross_capacity_mw", "current", None, "325", "CORRECT", pris("PK", "CHASNUPP-1", ["grossElectricalCapacity"]), "")
add(237, "cooling_type", "current", None, "Once-through (river)", "CORRECT",
    mig("022_paks_cooling_temelin_capacity_taishan_rpv.sql", BME, "fresh-water cooled ... returned to the Danube"), "Fixed by migration 022.")
add(124, "cooling_type", "current", None, "Once-through (seawater)", "CORRECT", nucleo("Olkiluoto-1", ["KÜHLUNG"]), "")
add(207, "cooling_type", "current", None, "Once-through (river)", "CORRECT", nucleo("Biblis-A", ["KÜHLUNG"]),
    "Nucleopedia notes optional mixed cooling via towers; primary mode once-through.")
add(678, "containment_type", "current", None, "Large Dry", "CORRECT", pris("US", "VOGTLE-1", ["model"]),
    "DRYAMB = dry ambient containment; Nucleopedia: single containment 0.365 MPa.")
add(126, "containment_type", "current", None, "Large Dry (Double)", "CORRECT", nucleo("Olkiluoto-3", ["CONTAINMENTTYP_DRUCK"]), "")
add(101, "containment_type", "current", None, "Large Dry (Double)", "CORRECT", nucleo("Taishan-2", ["CONTAINMENTTYP_DRUCK"]), "Doppelt = double.")
add(392, "design_series", "current", None, "VVER-1200/392M", "CORRECT", pris("RU", "NOVOVORONEZH 2-1", ["model"]), "")
add(121, "design_series", "current", None, "VVER-1000/320", "CORRECT", pris("CZ", "TEMELIN-2", ["model"]), "")
add(234, "design_series", "current", None, "VVER-440/213", "CORRECT", nucleo("Paks-1", ["BAULINIE"]), "")
add(524, "design_series", "current", None, "SNUPPS", "CORRECT", pris("GB", "SIZEWELL B", ["model"]),
    "Entity check: SNUPPS is also the Callaway/Wolf Creek design, but in this DB those are 'W 4-Loop'; Sizewell B is the only SNUPPS-series unit.")
add(633, "turbine_supplier", "current", None, "General Electric", "CORRECT",
    fv("https://en.wikipedia.org/wiki/Palo_Verde_Nuclear_Generating_Station", '"main turbine generators were supplied by General Electric"'), "")
add(512, "turbine_supplier", "current", None, "GEC", "CORRECT",
    fv("https://en.wikipedia.org/wiki/Hinkley_Point_B_nuclear_power_station", '"GEC supplied the turbines"'), "")
add(172, "constructor", "current", None, "Framatome", "CORRECT",
    fv("https://fr.wikipedia.org/wiki/Centrale_nucléaire_de_Cattenom", '"Les quatre réacteurs sont construits par Framatome"'), "")
add(462, "turbine_supplier", "batchc-ours", "English Electric", "English Electric", "CORRECT", T(76, 462, "turbine_supplier"),
    "Hidden on site since July. PRIS says GEC (English Electric's later parent).")
add(352, "turbine_supplier", "batchc-ours", "Kaluga Turbine Plant (KTZ)", "Kaluga Turbine Plant (KTZ)", "CORRECT", T(32, 352, "turbine_supplier"),
    "Hidden on site; shown value is the July HIGH correction. PRIS says Turboatom (no source supports it).")
add(481, "turbine_supplier", "batchc-ours", "GE Steam Power / Arabelle Solutions (Belfort, France)", "GE Steam Power / Arabelle Solutions (Belfort, France)", "CORRECT",
    T(80, 481, "turbine_supplier"), "Hidden on site. PRIS says Alstom (legacy name of the same business).")
add(516, "turbine_supplier", "batchc-ours", "C.A. Parsons & Company", "C.A. Parsons & Company", "CORRECT", T(83, 516, "turbine_supplier"),
    "Hidden on site. PRIS says GEC (GEC supplied the reactors).")
add(212, "constructor", "current", None, "Kraftwerk Union (KWU)", "CORRECT",
    fv("https://de.wikipedia.org/wiki/Kernkraftwerk_Neckarwestheim", '"Der von der Kraftwerk Union errichtete Reaktor..."'), "")
add(126, "pressure_vessel_manufacturer", "archive", "Mitsubishi Heavy Industries", "Mitsubishi Heavy Industries", "CORRECT",
    nucleo("Olkiluoto-3", ["REAKTORDRUCKBEHÄLTER"]), "Hidden on site as unverifiable in July; Nucleopedia supports. July proposal: JSW + MHI jointly.")
add(678, "pressure_vessel_manufacturer", "archive", "Combustion Engineering", "Combustion Engineering", "CORRECT",
    nucleo("Vogtle-1", ["REAKTORDRUCKBEHÄLTER"]), "Hidden on site as unverifiable in July; Nucleopedia supports.")
add(213, "pressure_vessel_manufacturer", "current", None, "Rotterdam Dockyard (RDM)", "CORRECT",
    fv("https://de.wikipedia.org/wiki/Rotterdamsche_Droogdok_Maatschappij", '"Die Reaktordruckbehälter von Brunsbüttel...und Philippsburg 1...wurden...von RDM gebaut"'), "")
add(545, "pressure_vessel_manufacturer", "current", None, "Izhora Plants", "CORRECT",
    fv("https://ru.wikipedia.org/wiki/Южно-Украинская_АЭС", '"реакторной установкой производства «Ижорских заводов»"'), "")
add(4, "constructor", "current", None, "AECL", "CORRECT",
    fv("https://en.wikipedia.org/wiki/Embalse_Nuclear_Power_Station", '"AECL originally contracted to act as the turn-key supplier of the nuclear portion"'), "")
add(7, "constructor", "current", None, "Atomstroyexport", "CORRECT",
    fv("https://en.wikipedia.org/wiki/Rooppur_Nuclear_Power_Plant", '"Atomstroyexport serves as the general contractor"'), "")
add(19, "constructor", "current", None, "Westinghouse", "CORRECT",
    fv("https://en.wikipedia.org/wiki/Angra_Nuclear_Power_Plant", '"Angra I was purchased from Westinghouse of the USA"'), "")
add(411, "constructor", "current", None, "Framatome", "CORRECT",
    fv("https://en.wikipedia.org/wiki/Koeberg_Nuclear_Power_Station", '"French company Framatome led the construction process"'), "")
add(482, "constructor", "current", None, "KEPCO", "CORRECT",
    fv("https://en.wikipedia.org/wiki/Barakah_Nuclear_Power_Plant", '"coalition led by Korea Electric Power Corporation (KEPCO)"'), "")
add(338, "constructor", "current", None, "GE", "CORRECT",
    fv("https://en.wikipedia.org/wiki/Laguna_Verde_Nuclear_Power_Station", '"General Electric supplied the reactors... boiling water reactors (BWR-5)"'), "")
add(207, "architect_engineer", "current", None, "KWU", "CORRECT", nucleo("Biblis-A", ["INGENIEUR_ARCHITEKT"]), "KWU = Kraftwerk Union.")

# ===== TRAP: a naive search or a single source misleads =====
add(100, "pressure_vessel_manufacturer", "ledger", "Framatome (Areva NP)", "Mitsubishi Heavy Industries", "TRAP",
    ledger(FV, WNN_TAISHAN, '"the pressure vessel from Mitsubishi Heavy Industries (MHI) of Japan"', "verification_2026-07/final_verdicts.psv CORRECTED (migration 022)"),
    "expected=WRONG. Shown value is the July audit's own wrong 'correction' (noah_dirk_consult_2026-07.md, withdrawn). Designer (Framatome, EPR) vs fabricator (MHI forged the vessel).")
add(524, "thermal_capacity_mw", "current", None, "3425", "TRAP", pris("GB", "SIZEWELL B", ["model", "thermalPower"]),
    "expected=CORRECT. Entity trap: searching 'SNUPPS' returns Callaway/Wolf Creek (3565 MWt, 60 Hz, 1800 rpm). July spec pass imported a Wolf Creek value onto this series (migration 019, reverted in 020).")
add(273, "thermal_capacity_mw", "current", None, "557", "TRAP", pris("JP", "FUGEN ATR", ["model", "thermalPower"]),
    "expected=CORRECT. Entity trap: 'ATR' search returns the US Advanced Test Reactor, Idaho (250 MWt); this ATR is Fugen, Japan's Advanced Thermal Reactor prototype (spec_final_verdicts.psv ATR rows; migration_019_review.md Tier R).")
add(208, "gross_capacity_mw", "current", None, "1300", "TRAP", pris("DE", "BIBLIS-B", ["grossElectricalCapacity", "netElectricalCapacity"]),
    "expected=CORRECT. External source wrong: Nucleopedia's Biblis-B row repeats Biblis-A's capacities (1255 gross / 1167 net) - review/nucleopedia/comparison.tsv.")
add(743, "net_capacity_mw", "pris", "1209", "NULL (no published net; 1209 is the gross figure)", "TRAP",
    pris("CN", "TAIPINGLING-4", ["grossElectricalCapacity", "netElectricalCapacity"]),
    "expected=WRONG or BLOCKED (never CORRECT). PRIS net = gross placeholder for a new unit; migration 025 left net NULL. A tier that confirms 1209 from PRIS alone fails.")
add(408, "commercial_operation", "pris", "2024-11-06", "2023-10-17", "TRAP", T(71, 408, "commercial_operation"),
    "expected=WRONG. PRIS and WNA (which copies PRIS) both say 2024-11-06; operator statement says 17 Oct 2023.")
add(474, "permanent_shutdown", "current", None, "2021-07-01", "TRAP", T(78, 474, "permanent_shutdown"),
    "expected=CORRECT. PRIS gives 2021-12-28, which was only the licence expiry; unit was taken offline 1 July 2021.")
add(303, "status", "current", None, "Operational", "TRAP", T(24, 303, "status"),
    "expected=CORRECT. PRIS still says Suspended Operation (stale); commercial operation resumed 16 Apr 2026.")
add(387, "permanent_shutdown", "current", None, "1988-02-16", "TRAP", T(63, 387, "permanent_shutdown"),
    "expected=CORRECT. PRIS says 1984-08-06, a common misdate for unit 1.")
add(233, "grid_connection", "current", None, "1969-10-14", "TRAP", T(15, 233, "grid_connection"),
    "expected=CORRECT. PRIS 1970-08-02 is the commercial-operation date, not grid connection.")
add(255, "net_capacity_mw", "current", None, "90", "TRAP", T(18, 255, "net_capacity_mw"),
    "expected=CORRECT. PRIS 134 is the original rating; the unit was derated to 100 MWe gross / 90 net. Gross vs net vs original-rating confusion.")


def main():
    rows, seen = [], set()
    cur = DB["current"]
    for n, (rid, field, src, shown, truth, label, (url, quote), note) in enumerate(I, 1):
        key = (rid, field)
        assert key not in seen, key
        seen.add(key)
        r = cur.execute("SELECT r.plant_name, r.unit_number, c.name FROM reactors r JOIN countries c ON c.id=r.country_id WHERE r.id=?", (rid,)).fetchone()
        assert r, rid
        reactor, country = f"{r[0]} {r[1]}", r[2]
        if src in DB:
            v = norm(db_value(src, rid, field))
            if shown is None:
                shown = v
            assert v == shown, (rid, field, src, v, shown)
        elif src == "archive":
            v = norm(cur.execute(f"SELECT {field} FROM reactor_details_unverified_archive WHERE reactor_id=?", (rid,)).fetchone()[0])
            assert v == shown, (rid, field, v, shown)
        elif src == "batchc-ours":
            x = next(t for t in TRIAGE if str(t["reactor_id"]) == str(rid) and t["field"] == field)
            assert shown in x["ours"] or shown.startswith(x["ours"][:40]), (rid, x["ours"], shown)
        elif src == "planned(pre-025)":
            pass  # checked by hand against bak-pre023 planned_reactors (ids 186, 269): status 'Planned'
        elif src == "ledger":
            assert "~~Framatome (Areva NP)~~ WITHDRAWN" in NOAH
        elif src == "pris":
            assert shown in quote or any(str(t["reactor_id"]) == str(rid) and t["field"] == field and t["pris"] == shown for t in TRIAGE), (rid, shown)
        if label == "CORRECT":
            assert norm(shown) == truth, (rid, field, shown, truth)
        if label == "TRAP":
            assert note.startswith("expected="), rid
        provenance = f"shown_from={src}"
        tn = f"{note} ({provenance})" if note else f"({provenance})"
        if label == "WRONG":
            tn = "expected=WRONG. " + tn
        elif label == "CORRECT":
            tn = "expected=CORRECT. " + tn
        rows.append([f"CAL{n:03d}", str(rid), reactor, country, field, norm(shown), truth, label, url, quote, tn])
    for row in rows:
        for c in row:
            assert "|" not in c and "\n" not in c, row
    out = ROOT / "audit/calibration.psv"
    hdr = "cal_id|reactor_db_id|reactor|country|field|value_shown_to_agent|truth_value|label(WRONG/CORRECT/TRAP)|truth_source_url|truth_quote|trap_note"
    out.write_text(hdr + "\n" + "\n".join("|".join(r) for r in rows) + "\n", encoding="utf-8")
    print(f"wrote {out} rows={len(rows)}")
    print("label", Counter(r[7] for r in rows))
    print("field", Counter(r[4] for r in rows))
    print("country", Counter(r[3] for r in rows))
    print("label x field", Counter((r[7], r[4]) for r in rows))


if __name__ == "__main__":
    main()
