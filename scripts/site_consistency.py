"""Site consistency gate: every published number must agree with every other surface that shows it.

Purpose: catch the bug class where two charts compute the "same" quantity with different rules
  (2026-10-14: header said 420 operating reactors, history chart said 436; generation card ~2,967 TWh
  vs 2,812 published; age chart silently dropped 34 reactors). Also answers "what does this change
  touch?": given a migration, list every site surface that reads the tables/columns it writes.
  Checks C5-C9 (audit/site_dependencies_findings.md section C) cover per-entity pages, the
  choropleth, model tables, reactor-page rendering, hardcoded text claims, and chart titles.
Inputs:  nuclear_reactors.db (or --db PATH), app.py (via Flask test client, no server needed),
         templates/*.html (static claims, chart fields), audit/pris_api/all_reactors.json (optional,
         local-only IAEA benchmark), Chrome (optional, for the rendered-page check).
Outputs: report on stdout; exit 1 if any FAIL.
Usage:   python scripts/site_consistency.py                 # all checks on nuclear_reactors.db
         python scripts/site_consistency.py --db test.db    # check a migrated copy before applying
         python scripts/site_consistency.py --no-browser    # skip the headless-Chrome page check
         python scripts/site_consistency.py --all-reactor-pages   # render every reactor page (slow)
         python scripts/site_consistency.py --migration migrations/029_x.sql   # list affected surfaces
Run:     before AND after every migration, and before every deploy (CLAUDE.md Data Change Protocol).
         The browser check starts app.py on --port (default 5021) and stops that PID when done.
last_run: 2026-10-14
"""
import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Which surfaces read which table.columns. "*" = any column of the table. Keep in step with app.py;
# a surface missing here is a surface no migration will flag.
DEPENDENCIES = {
    "Homepage card: Operational reactors": ["reactors.status"],
    "Homepage card: Capacity (GW, gross)": ["reactors.status", "reactors.gross_capacity_mw"],
    "Homepage card: Under construction": ["reactors.status"],
    "Homepage card: Generation (TWh)": ["external_series.*"],
    "Homepage card: Countries operating": ["reactors.status", "reactors.country_id"],
    "Homepage card: Average age": ["reactors.status", "reactors.grid_connection", "reactors.commercial_operation",
                                   "reactors.permanent_shutdown"],
    "Homepage card history charts (/api/stats/history)": [
        "reactors.commercial_operation", "reactors.grid_connection", "reactors.permanent_shutdown",
        "reactors.suspended_since", "reactors.construction_start", "reactors.gross_capacity_mw",
        "reactors.country_id", "capacity_changes.*", "external_series.*"],
    "Homepage chart: Global installed capacity (/api/capacity/history)": [
        "reactors.commercial_operation", "reactors.grid_connection", "reactors.permanent_shutdown",
        "reactors.suspended_since", "reactors.gross_capacity_mw", "capacity_changes.*"],
    "Homepage chart: Nuclear share of electricity (/api/generation/annual)": ["external_series.*"],
    "Homepage chart: Capacity by technology (/api/technologies)": [
        "reactors.status", "reactors.technology_id", "reactors.gross_capacity_mw", "technologies.*"],
    "Homepage chart: Top 10 countries (/api/countries)": [
        "reactors.status", "reactors.country_id", "reactors.gross_capacity_mw", "countries.*"],
    "Homepage chart: Status distribution (/api/reactors/count)": ["reactors.status", "reactors.gross_capacity_mw"],
    "Homepage chart: Age distribution (/api/reactors/age-distribution)": [
        "reactors.status", "reactors.grid_connection", "reactors.commercial_operation", "reactors.gross_capacity_mw"],
    "Homepage map + construction map": ["reactors.latitude", "reactors.longitude", "reactors.status",
                                        "reactors.plant_name", "reactors.gross_capacity_mw"],
    "Homepage construction modal note (units without coordinates)": [
        "reactors.status", "reactors.latitude", "reactors.longitude"],
    "Homepage countries choropleth (/api/countries: operating ramp + building-first style)": [
        "reactors.status", "reactors.country_id", "reactors.gross_capacity_mw", "countries.*"],
    "Homepage lineage callout text (families / series counts)": [
        "design_lineages.*", "design_series_info.*", "reactors.design_series"],
    "Homepage table + search": ["reactors.*", "planned_reactors.*"],
    "Planned capacity, net else gross (homepage Planned tab + planned pages)": [
        "planned_reactors.net_capacity_mw", "planned_reactors.gross_capacity_mw"],
    "Footer: Last updated (latest _migrations.applied_at)": ["_migrations.*"],
    "Sources page text (dates, coverage claims)": ["external_series.*", "_migrations.*"],
    "Country / reactor / plant / owner / supplier / model / technology pages": [
        "reactors.*", "reactor_details.*", "generation_annual.*", "capacity_changes.*", "countries.*",
        "technologies.*", "entity_descriptions.*"],
    "Fleet rows incl. Suspended (country / technology / owner / supplier / model pages)": [
        "reactors.status", "reactors.country_id", "reactors.technology_id", "reactors.owner",
        "reactors.supplier_id", "reactors.model_id", "reactors.design_series"],
    "Country / technology capacity history charts (/api/capacity/history?country= / technology=)": [
        "reactors.commercial_operation", "reactors.grid_connection", "reactors.permanent_shutdown",
        "reactors.suspended_since", "reactors.gross_capacity_mw", "reactors.country_id",
        "reactors.technology_id", "capacity_changes.*"],
    "Technology / status / supplier country-breakdown charts": [
        "reactors.status", "reactors.gross_capacity_mw", "reactors.country_id", "reactors.technology_id",
        "reactors.supplier_id"],
    "Supplier page capacity (operating only; chart = all statuses)": [
        "reactors.status", "reactors.gross_capacity_mw", "reactors.supplier_id"],
    "Status page generation chart (current-status history)": ["generation_annual.*", "reactors.status"],
    "Model / series pages: Total = table rows": ["reactors.model_id", "reactors.design_series", "models.*"],
    "Reactor page cards (design specs, reactor details, capacity history)": [
        "design_series_specs.*", "reactor_details.*", "capacity_changes.*", "reactors.design_series"],
    "Design lineage pages": ["design_lineages.*", "design_series_info.*", "reactors.design_series",
                             "reactors.model_id"],
    "Lineages page totals + Unclassified card": ["design_series_info.*", "reactors.design_series",
                                                 "reactors.status", "reactors.gross_capacity_mw"],
    "Containment page (type count text, type colours)": ["reactors.containment_type", "entity_descriptions.*"],
    "Planned reactor pages": ["planned_reactors.*"],
}

# Charts whose title names a quantity: the dataset (and sort key, if any) must be that quantity.
# (template, title text, start marker of the chart's code, end marker, required regexes)
CHART_FIELD_CLAIMS = [
    ("index.html", "Top 10 Countries by Capacity", "async function loadCountryChart", "async function",
     [r"\.sort\(\(a, b\) => b\.capacity_gw - a\.capacity_gw\)", r"data: top10\.map\(c => c\.capacity_gw\)"]),
    ("index.html", "Capacity by Technology", "async function loadTechChart", "async function",
     [r"\.sort\(\(a, b\) => b\.capacity_gw - a\.capacity_gw\)", r"data: chartData\.map\(t => t\.capacity_gw\)"]),
    ("index.html", "Global Installed Capacity", "async function loadCapacityChart", "async function",
     [r"withProjection\(history, data\.projection, 'capacity_gw'\)", r"data: series\.past"]),
    ("index.html", "Nuclear Share of Global Electricity", "async function loadGenerationChart", "async function",
     [r"data: annual\.map\(d => d\.share_pct\)"]),
    ("index.html", "Reactor Status Distribution", "async function loadStatusChart", "async function",
     [r"data: data\.by_status\.map\(s => s\.count\)"]),
    # Sort for these two is server-side; checked against the endpoints in check_chart_fields.
    ("technology_detail.html", "Top 15 by Operating Capacity", "// Country breakdown chart", "// Generation chart",
     [r"data: top15\.map\(c => c\.capacity_gw\)"]),
    ("status_detail.html", "Top 15 by ", "// Country breakdown chart", "// Technology mix",
     [r"data: top15\.map\(c => c\.capacity_gw\)"]),
]

# Hardcoded numbers that must not come back (each was stale once). Pattern -> why.
FORBIDDEN_LITERALS = [
    ("index.html", r"Explore \d+ design families", "lineage family count must come from the DB"),
    ("index.html", r"\d+ reactor series", "series count must come from the DB"),
    ("lineages.html", r"\d+ design families spanning", "family count must come from the DB"),
    ("containment_detail.html", r"The \d+ containment types", "containment type count must come from the DB"),
    ("_reg_footer.html", r"Last updated [A-Z][a-z]+ \d{4}", "footer date must come from _migrations"),
]


def affected_surfaces(sql_text):
    """Tables/columns a migration writes -> surfaces that read them."""
    writes = set()
    for m in re.finditer(r"UPDATE\s+(\w+)\s+SET\s+(.*?)(?:\s+WHERE|;)", sql_text, re.I | re.S):
        for col in re.findall(r"(\w+)\s*=", m.group(2)):
            writes.add(f"{m.group(1)}.{col}")
    for m in re.finditer(r"(?:INSERT\s+(?:OR\s+\w+\s+)?INTO|DELETE\s+FROM|CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?)\s+(\w+)",
                         sql_text, re.I):
        writes.add(f"{m.group(1)}.*")
    for m in re.finditer(r"ALTER\s+TABLE\s+(\w+)\s+ADD\s+COLUMN\s+(\w+)", sql_text, re.I):
        writes.add(f"{m.group(1)}.{m.group(2)}")
    hits = {}
    for surface, deps in DEPENDENCIES.items():
        for w in writes:
            t, c = w.split(".")
            for d in deps:
                dt, dc = d.split(".")
                if dt == t and (dc == "*" or c == "*" or dc == c):
                    hits.setdefault(surface, set()).add(w)
    return writes, hits


# Conflicts researched on 2026-10-14 where no source settles the value (audit/capacity_conflicts_2026-10-14.psv).
# They stay visible as WARN until resolved; remove a name once its values are sourced and fixed.
KNOWN_CAPACITY_CONFLICTS = {"Bruce 1", "Bruce 2", "Turkey Point 3", "Turkey Point 4", "Quad Cities 2"}
# Research-scale units that IAEA PRIS itself reports with net = gross.
NET_EQUALS_GROSS_AS_REPORTED = {"GE Vallecitos 1", "Saxton 1"}


class Report:
    def __init__(self):
        self.rows = []

    def check(self, name, ok, detail, warn_only=False):
        status = "PASS" if ok else ("WARN" if warn_only else "FAIL")
        self.rows.append((status, name, detail))

    def print(self):
        for status, name, detail in self.rows:
            print(f"[{status}] {name}: {detail}")
        n_fail = sum(1 for r in self.rows if r[0] == "FAIL")
        n_warn = sum(1 for r in self.rows if r[0] == "WARN")
        n_pass = sum(1 for r in self.rows if r[0] == "PASS")
        print(f"\n{len(self.rows)} checks: {n_pass} PASS, {n_fail} FAIL, {n_warn} WARN")
        return n_fail


def enc(name):
    return urllib.parse.quote(str(name), safe="")


def short(items, n=8):
    items = list(items)
    return f"{items[:n]}{' ...' if len(items) > n else ''}"


def run_checks(db_path, browser=True, all_reactor_pages=False, port=5021):
    os.environ["DATABASE_PATH"] = str(db_path)
    sys.path.insert(0, str(ROOT))
    import app as site  # noqa: E402  (reads DATABASE_PATH at import)
    c = site.app.test_client()
    get = lambda u: c.get(u).get_json()
    R = Report()
    year = date.today().year

    stats = get("/api/stats")["global_statistics"]
    hist = {r["year"]: r for r in get("/api/stats/history")["years"]}
    caph = {r["year"]: r for r in get("/api/capacity/history")["history"]}
    counts = {r["status"]: r for r in get("/api/reactors/count")["by_status"]}
    countries = get("/api/countries")["countries"]
    techs = get("/api/technologies")["technologies"]
    ages = get("/api/reactors/age-distribution")["brackets"]
    annual = get("/api/generation/annual")["annual"]
    op, cap = stats["operational"]["count"], stats["operational"]["capacity_gw"]
    now = hist.get(year, {})

    # --- Cross-surface agreement: the same quantity must show the same value everywhere ---
    R.check("operating count: card = history chart (this year)", now.get("operational") == op,
            f"card {op}, history {now.get('operational')}")
    R.check("operating count: card = capacity chart (this year)", caph.get(year, {}).get("reactor_count") == op,
            f"card {op}, capacity chart {caph.get(year, {}).get('reactor_count')}")
    R.check("operating count: card = status pie", counts.get("Operational", {}).get("count") == op,
            f"card {op}, pie {counts.get('Operational', {}).get('count')}")
    R.check("operating count: card = sum of country bars", sum(x["operational"] for x in countries) == op,
            f"card {op}, countries {sum(x['operational'] for x in countries)}")
    R.check("operating count: card = sum of technology slices", sum(x["operational"] for x in techs) == op,
            f"card {op}, technologies {sum(x['operational'] for x in techs)}")
    R.check("operating count: card = sum of age brackets", sum(x["count"] for x in ages) == op,
            f"card {op}, age chart {sum(x['count'] for x in ages)}")
    # Tolerance: each displayed part is rounded to 0.1 GW, so a sum of n parts may drift by n * 0.05.
    for label, val, parts in [("history chart", now.get("capacity_gw"), 1),
                              ("capacity chart", caph.get(year, {}).get("capacity_gw"), 1),
                              ("status pie", counts.get("Operational", {}).get("capacity_gw"), 1),
                              ("country bars", round(sum(x["capacity_gw"] for x in countries), 1), len(countries)),
                              ("technology slices", round(sum(x["capacity_gw"] for x in techs), 1), len(techs)),
                              ("age brackets", round(sum(x["capacity_gw"] for x in ages), 1), len(ages))]:
        tol = 0.05 * parts + 0.001
        R.check(f"capacity GW: card = {label}", val is not None and abs(val - cap) <= tol,
                f"card {cap}, {label} {val}")
    R.check("under construction: card = history chart", now.get("under_construction") == stats["under_construction"],
            f"card {stats['under_construction']}, history {now.get('under_construction')}")
    R.check("countries: card = history chart", now.get("countries") == stats["operating_countries"],
            f"card {stats['operating_countries']}, history {now.get('countries')}")
    R.check("average age: card ~ history chart", abs((now.get("avg_age") or 0) - stats["average_fleet_age_years"]) <= 0.6,
            f"card {stats['average_fleet_age_years']} (today), history {now.get('avg_age')} (year end)")
    g = stats.get("generation") or {}
    last = annual[-1] if annual else {}
    R.check("generation: card = share chart (latest year)", g.get("twh") == last.get("nuclear_twh") and g.get("year") == last.get("year"),
            f"card {g.get('year')} {g.get('twh')}, share chart {last.get('year')} {last.get('nuclear_twh')}")
    R.check("generation: card = history chart", hist.get(g.get("year"), {}).get("generation_twh") == g.get("twh"),
            f"card {g.get('twh')}, history {hist.get(g.get('year'), {}).get('generation_twh')}")
    both = sorted(set(hist) & set(caph))
    off = [(y, hist[y]["operational"], caph[y]["reactor_count"]) for y in both
           if hist[y]["operational"] != caph[y]["reactor_count"]]
    R.check("operating count: history chart = capacity chart in EVERY year", not off, f"{len(off)} years differ: {off[:5]}")
    offc = [(y, hist[y]["capacity_gw"], caph[y]["capacity_gw"]) for y in both
            if abs((hist[y]["capacity_gw"] or 0) - (caph[y]["capacity_gw"] or 0)) > 0.05]
    R.check("capacity GW: history chart = capacity chart in EVERY year", not offc, f"{len(offc)} years differ: {offc[:5]}")
    R.check("history charts stop at the current year", max(hist) == year and max(caph) == year,
            f"stats history ends {max(hist)}, capacity history ends {max(caph)}")

    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    q = lambda s, p=(): db.execute(s, p).fetchall()

    check_entity_pages(R, c, get, q, year)
    check_choropleth(R, stats, countries)
    check_model_pages(R, c, q)
    reactor_sample = check_reactor_payloads(R, c, q)
    check_static_claims(R, c, get, q, stats)
    check_chart_fields(R, get, q)
    check_planned(R, get, q)

    # --- Data invariants the charts rely on ---
    bad = q("""SELECT r.plant_name || ' ' || r.unit_number, r.gross_capacity_mw, cc.gross_capacity_mw
               FROM reactors r JOIN capacity_changes cc ON cc.id = (
                   SELECT id FROM capacity_changes WHERE reactor_id = r.id AND gross_capacity_mw IS NOT NULL
                   ORDER BY effective_date DESC LIMIT 1)
               WHERE cc.gross_capacity_mw != r.gross_capacity_mw""")
    known = [b for b in bad if b[0] in KNOWN_CAPACITY_CONFLICTS]
    bad = [b for b in bad if b[0] not in KNOWN_CAPACITY_CONFLICTS]
    R.check("latest capacity_changes gross = reactors.gross_capacity_mw", not bad, f"{len(bad)} mismatched: {bad[:6]}")
    R.check("known capacity conflicts still open (research blocked; see KNOWN_CAPACITY_CONFLICTS)", not known,
            f"{known}", warn_only=True)
    bad = q("""SELECT r.plant_name || ' ' || r.unit_number, r.net_capacity_mw, cc.net_capacity_mw
               FROM reactors r JOIN capacity_changes cc ON cc.id = (
                   SELECT id FROM capacity_changes WHERE reactor_id = r.id AND net_capacity_mw IS NOT NULL
                   ORDER BY effective_date DESC LIMIT 1)
               WHERE cc.net_capacity_mw != r.net_capacity_mw""")
    known = [b for b in bad if b[0] in KNOWN_CAPACITY_CONFLICTS]
    bad = [b for b in bad if b[0] not in KNOWN_CAPACITY_CONFLICTS]
    R.check("latest capacity_changes net = reactors.net_capacity_mw", not bad, f"{len(bad)} mismatched: {bad[:6]}")
    R.check("known net-capacity conflicts still open", not known, f"{known}", warn_only=True)
    bad = q("SELECT plant_name || ' ' || unit_number FROM reactors WHERE status = 'Suspended' "
            "AND suspended_since IS NULL AND permanent_shutdown IS NULL")
    R.check("every Suspended reactor has suspended_since (or a shutdown date)", not bad, f"{bad}")
    bad = q("SELECT plant_name || ' ' || unit_number FROM reactors WHERE status = 'Operational' "
            "AND grid_connection IS NULL")
    R.check("every Operational reactor has a grid connection date", not bad, f"{bad}")
    bad = q("SELECT plant_name || ' ' || unit_number FROM reactors WHERE status = 'Under Construction' "
            "AND construction_start IS NULL")
    R.check("every Under Construction reactor has a construction start", not bad, f"{bad}")
    bad = q("SELECT plant_name || ' ' || unit_number FROM reactors WHERE status = 'Operational' "
            "AND permanent_shutdown IS NOT NULL")
    R.check("no Operational reactor has a permanent shutdown date", not bad, f"{bad}")
    bad = q("SELECT plant_name || ' ' || unit_number, net_capacity_mw, gross_capacity_mw FROM reactors "
            "WHERE net_capacity_mw >= gross_capacity_mw")
    bad = [b for b in bad if b[0] not in NET_EQUALS_GROSS_AS_REPORTED]
    R.check("net capacity < gross capacity", not bad, f"{bad}")
    # Origin 2026-10-15: migration 032 recorded Guohe One 2 as CONNECTED but left it Under Construction.
    bad = q("SELECT plant_name || ' ' || unit_number, expected_operation FROM reactors "
            "WHERE status = 'Under Construction' AND (expected_status = 'CONNECTED' OR grid_connection IS NOT NULL)")
    R.check("no Under Construction reactor is recorded as connected to the grid", not bad, f"{bad}")
    bad = q("SELECT plant_name || ' ' || unit_number, planned_retirement FROM reactors "
            "WHERE status = 'Operational' AND planned_retirement IS NOT NULL "
            "AND CAST(substr(planned_retirement, 1, 4) AS INTEGER) < CAST(strftime('%Y', 'now') AS INTEGER)")
    R.check("no Operational reactor has a planned retirement year in the past", not bad, f"{len(bad)}: {bad[:8]}",
            warn_only=True)
    bad = q("SELECT plant_name || ' ' || unit_number, commercial_operation FROM reactors "
            "WHERE status = 'Under Construction' AND commercial_operation IS NOT NULL")
    R.check("Under Construction reactors hold no (expected) commercial-operation date", not bad,
            f"{len(bad)} hold a future date in an actual-date column: {bad}", warn_only=True)
    try:
        latest = q("SELECT MAX(year), MAX(retrieved) FROM external_series WHERE series = 'nuclear_generation_twh'")[0]
        R.check("external generation series is fresh (covers last year)", latest[0] is not None and latest[0] >= year - 1,
                f"latest year {latest[0]}, retrieved {latest[1]}")
    except sqlite3.OperationalError as e:
        R.check("external_series table present", False, str(e))

    # --- External benchmark: IAEA PRIS (local pull) ---
    pris_file = ROOT / "audit" / "pris_api" / "all_reactors.json"
    if pris_file.exists():
        pris = json.load(open(pris_file, encoding="utf-8"))
        p_op = [r for r in pris if r["statusName"] == "Operational"]
        p_net = sum(r["netElectricalCapacity"] or 0 for r in p_op) / 1000
        our_net = q("SELECT SUM(net_capacity_mw) / 1000.0 FROM reactors WHERE status = 'Operational'")[0][0]
        R.check("operating count within 5 of IAEA PRIS", abs(len(p_op) - op) <= 5, f"ours {op}, PRIS {len(p_op)}",
                warn_only=True)
        R.check("operating net GW within 2% of IAEA PRIS", abs(our_net - p_net) / p_net <= 0.02,
                f"ours {our_net:.1f}, PRIS {p_net:.1f}", warn_only=True)

    # --- C8 (rendered): pages render in a real browser, error panel hidden ---
    if browser:
        if all_reactor_pages:
            reactor_sample = [r[0] for r in q("SELECT id FROM reactors ORDER BY id")]
        check_browser(R, db_path, q, reactor_sample, port)
    else:
        R.check("rendered pages (headless Chrome)", True, "skipped (--no-browser)", warn_only=True)
    return R


def check_entity_pages(R, c, get, q, year):
    """C5 + finding 14/16: per-country and per-technology cards agree with their capacity charts,
    and the fleet rows (Operational / UC / Suspended / Shutdown) add up to Total on every entity page."""
    for kind, names, detail_url, hist_param, key, total_key in [
        ("country", [r[0] for r in q("SELECT name FROM countries ORDER BY name")],
         "/api/countries/{}/detail", "country", "country", "total_reactors"),
        ("technology", [r[0] for r in q("SELECT code FROM technologies ORDER BY code")],
         "/api/technologies/{}/detail", "technology", "technology", "total"),
    ]:
        count_bad, gw_bad, end_bad, sum_bad, checked = [], [], [], [], 0
        for name in names:
            r = c.get(detail_url.format(enc(name)))
            if r.status_code != 200:
                continue  # countries/technologies with no reactors have no page
            checked += 1
            card = r.get_json()[key]
            h = get(f"/api/capacity/history?{hist_param}={enc(name)}")["history"]
            last = h[-1] if h else {"year": year, "reactor_count": 0, "capacity_gw": 0.0}
            if h and last["year"] != year:
                end_bad.append((name, last["year"]))
            if last["reactor_count"] != card["operational"]:
                count_bad.append((name, card["operational"], last["reactor_count"]))
            if abs((last["capacity_gw"] or 0) - (card["capacity_gw"] or 0)) > 0.051:
                gw_bad.append((name, card["capacity_gw"], last["capacity_gw"]))
            parts = sum(card.get(s) or 0 for s in ("operational", "under_construction", "suspended", "shutdown",
                                                    "long_term_shutdown"))
            if "suspended" not in card or parts != card[total_key]:
                sum_bad.append((name, card[total_key], parts))
        R.check(f"C5 every {kind}: capacity chart runs to {year}", not end_bad, f"{checked} checked; ends early: {short(end_bad)}")
        R.check(f"C5 every {kind}: card operating count = capacity chart last point", not count_bad,
                f"{checked} checked; (name, card, chart) mismatches: {short(count_bad)}")
        R.check(f"C5 every {kind}: card GW = capacity chart last point (0.05 GW)", not gw_bad,
                f"{checked} checked; (name, card, chart) mismatches: {short(gw_bad)}")
        R.check(f"fleet rows sum to Total on every {kind} page (incl. Suspended)", not sum_bad,
                f"{checked} checked; (name, total, sum of rows): {short(sum_bad)}")

    # Owner and supplier pages: fleet rows sum to Total
    for kind, names, url, key in [
        ("owner", [r[0] for r in q("SELECT DISTINCT owner FROM reactors WHERE owner IS NOT NULL AND owner != ''")],
         "/api/owners/{}/detail", "owner"),
        ("supplier", [r[0] for r in q("SELECT name FROM suppliers")], "/api/suppliers/{}/detail", "supplier"),
    ]:
        sum_bad, checked = [], 0
        for name in names:
            r = c.get(url.format(enc(name)))
            if r.status_code != 200:
                sum_bad.append((name, f"HTTP {r.status_code}"))
                continue
            checked += 1
            card = r.get_json()[key]
            parts = sum(card.get(s) or 0 for s in ("operational", "under_construction", "suspended", "shutdown"))
            if "suspended" not in card or parts != card["total"]:
                sum_bad.append((name, card["total"], parts))
        R.check(f"fleet rows sum to Total on every {kind} page (incl. Suspended)", not sum_bad,
                f"{checked} checked; problems: {short(sum_bad)}")
    # Supplier capacity is operating-only (finding 8): the supplier GW cards sum to the operating total
    sup_gw = sum((get(f"/api/suppliers/{enc(n)}/detail").get("supplier") or {}).get("capacity_gw") or 0
                 for (n,) in q("SELECT name FROM suppliers"))
    op_gw_with_supplier = q("SELECT COALESCE(SUM(gross_capacity_mw), 0) / 1000.0 FROM reactors "
                            "WHERE status = 'Operational' AND supplier_id IS NOT NULL")[0][0]
    n_sup = q("SELECT COUNT(*) FROM suppliers")[0][0]
    R.check("supplier pages: capacity = operating units only", abs(sup_gw - op_gw_with_supplier) <= 0.05 * n_sup + 0.001,
            f"sum of supplier cards {sup_gw:.1f} GW, operating reactors with a supplier {op_gw_with_supplier:.1f} GW")


def check_choropleth(R, stats, countries):
    """C6: the Countries card equals the number of countries the choropleth shades as operating."""
    html = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    rule = re.search(r"const isOperating = c => c\.operational > 0;", html)
    R.check("C6 choropleth uses the card's operating rule (operational > 0)", bool(rule),
            "found isOperating rule in index.html" if rule else "isOperating rule missing or changed in index.html")
    a3 = set(re.findall(r"'([A-Z]{3})':'\d{3}'", html))
    unmapped = [x["name"] for x in countries if x["iso_code"] not in a3]
    R.check("C6 every /api/countries entry has a choropleth shape (alpha3ToNumeric)", not unmapped,
            f"{len(countries)} countries; not shaded: {unmapped}")
    shaded_operating = sum(1 for x in countries if x["operational"] > 0 and x["iso_code"] in a3)
    R.check("C6 Countries card = choropleth countries shaded as operating", shaded_operating == stats["operating_countries"],
            f"card {stats['operating_countries']}, choropleth {shaded_operating}")
    building = [x["name"] for x in countries if x["operational"] == 0 and x["under_construction"] > 0]
    R.check("C6 choropleth non-operating countries are all 'building' (styled separately)",
            len(countries) - shaded_operating == len(building),
            f"{len(building)} building, none operating: {building}")


def check_model_pages(R, c, q):
    """C7: on every model and design-series page, Total Reactors = rows in the reactor table."""
    names = [r[0] for r in q("SELECT name FROM models")] + \
            [r[0] for r in q("SELECT DISTINCT design_series FROM reactors WHERE design_series IS NOT NULL")]
    bad, http_bad, checked = [], [], 0
    for name in sorted(set(names)):
        r = c.get(f"/api/models/{urllib.parse.quote(name, safe='/')}/detail")
        if r.status_code != 200:
            http_bad.append((name, r.status_code))
            continue
        checked += 1
        j = r.get_json()
        m = j["model"]
        parts = sum(m.get(s) or 0 for s in ("operational", "under_construction", "suspended", "shutdown"))
        if m["total"] != len(j["reactors"]) or parts != m["total"]:
            bad.append((name, m["total"], len(j["reactors"]), parts))
    R.check("C7 every model / series page: Total = table rows = sum of fleet rows", not bad,
            f"{checked} pages; (name, total, rows, fleet-row sum): {short(bad)}")
    R.check("C7 every model / series name resolves to a page", not http_bad, f"failures: {short(http_bad)}")


def check_reactor_payloads(R, c, q):
    """C8: every reactor's detail payload has what reactor_detail.html needs; returns a page sample."""
    ids = [r[0] for r in q("SELECT id FROM reactors ORDER BY id")]
    bad, no_specs = [], []
    for rid in ids:
        r = c.get(f"/api/reactors/{rid}?api_key=demo-key-12345")
        if r.status_code != 200:
            bad.append((rid, f"HTTP {r.status_code}"))
            continue
        j = r.get_json()
        re_ = j.get("reactor") or {}
        missing = [k for k in ("plant_name", "unit_number", "status", "country") if re_.get(k) in (None, "")]
        if not isinstance(j.get("lifetime_stats"), dict):
            missing.append("lifetime_stats")
        if not isinstance(j.get("generation_history"), list):
            missing.append("generation_history")
        # the capacity-history table calls cc.gross_capacity_mw.toLocaleString() with no null guard
        if any(cc.get("gross_capacity_mw") is None for cc in j.get("capacity_changes") or []):
            missing.append("capacity_changes.gross_capacity_mw is null")
        if missing:
            bad.append((rid, missing))
        if "reactor_details" in j and "design_specs" not in j:
            no_specs.append(rid)
    R.check("C8 every reactor detail payload has the fields the page renders", not bad,
            f"{len(ids)} reactors; problems: {short(bad)}")
    # The details card and the specs card share specRow(): it must be defined at script top level,
    # not inside the design-specs block (finding 1: 28 pages showed "Reactor not found").
    html = (TEMPLATES / "reactor_detail.html").read_text(encoding="utf-8")
    fa = re.search(r"^( *)function formatAge\(", html, re.M)
    sr = re.search(r"^( *)function specRow\(", html, re.M)
    R.check("C8 reactor page: specRow() is defined at script top level", bool(fa and sr and fa.group(1) == sr.group(1)),
            f"{len(no_specs)} reactors have details but no design_series_specs row (they need the shared helper)")
    sample = [66, 741, 1] + no_specs[:5]
    for status in ("Operational", "Under Construction", "Suspended", "Shutdown"):
        row = q("SELECT MIN(id) FROM reactors WHERE status = ?", (status,))
        if row and row[0][0]:
            sample.append(row[0][0])
    row = q("SELECT MIN(reactor_id) FROM capacity_changes WHERE change_type = 'uprate'")
    if row and row[0][0]:
        sample.append(row[0][0])
    row = q("SELECT MIN(id) FROM reactors WHERE id NOT IN (SELECT reactor_id FROM generation_annual)")
    if row and row[0][0]:
        sample.append(row[0][0])
    seen = set()
    return [x for x in sample if x in set(ids) and not (x in seen or seen.add(x))]


def check_static_claims(R, c, get, q, stats):
    """C9: text claims on pages (counts, dates) match live counts; no stale literals come back."""
    for tpl, pat, why in FORBIDDEN_LITERALS:
        text = (TEMPLATES / tpl).read_text(encoding="utf-8")
        hit = re.search(pat, text)
        R.check(f"C9 no hardcoded literal in {tpl}: {why}", not hit, f"found '{hit.group(0)}'" if hit else "none")

    lin = get("/api/lineages")
    unc = lin.get("unclassified") or {"reactor_count": 0, "series": []}
    families = len(lin["lineages"])
    series = sum(l["series_count"] for l in lin["lineages"]) + len(unc["series"])
    reactors_total = sum(l["reactor_count"] for l in lin["lineages"]) + unc["reactor_count"]
    R.check("C9 /lineages Total Reactors (incl. Unclassified) = database total", reactors_total == stats["total_reactors"],
            f"lineages {reactors_total}, DB {stats['total_reactors']}; unclassified {unc['reactor_count']} "
            f"({', '.join(unc['series'])})")
    home = c.get("/").data.decode("utf-8")
    m = re.search(r"Explore (\d+) design families and (\d+) reactor series", home)
    R.check("C9 homepage lineage callout = /lineages counts", bool(m) and (int(m.group(1)), int(m.group(2))) == (families, series),
            f"homepage {m.groups() if m else 'text not found'}, /lineages ({families}, {series})")
    page = c.get("/lineages").data.decode("utf-8")
    m = re.search(r"(\d+) design families spanning (\d+) years", page)
    first = q("""SELECT MIN(dsi.first_commercial_year) FROM design_series_info dsi
                 JOIN reactors r ON r.design_series = dsi.design_series""")[0][0]
    R.check("C9 /lineages subtitle = live family count and span", bool(m) and int(m.group(1)) == families
            and int(m.group(2)) == date.today().year - first,
            f"subtitle {m.groups() if m else 'text not found'}, live ({families}, {date.today().year - first})")

    types = get("/api/containment/overview")["types"]
    page = c.get("/containment").data.decode("utf-8")
    m = re.search(r"The (\d+) containment types", page)
    R.check("C9 containment intro count = types listed", bool(m) and int(m.group(1)) == len(types),
            f"text {m.group(1) if m else 'not found'}, API {len(types)}")
    html = (TEMPLATES / "containment_detail.html").read_text(encoding="utf-8")
    colours = set(re.findall(r"'([^']+)': '#[0-9A-Fa-f]{6}'", html.split("const typeColors")[1].split("};")[0]))
    uncoloured = [t["name"] for t in types if t["name"] not in colours]
    R.check("C9 containment: every type has a colour or the page has a fallback colour",
            "FALLBACK_TYPE_COLOR" in html or not uncoloured, f"types without their own colour: {uncoloured}")

    try:
        latest = q("SELECT MAX(applied_at) FROM _migrations")[0][0]
        expect = datetime.strptime(latest[:10], "%Y-%m-%d").strftime("%B %Y") if latest else None
    except sqlite3.OperationalError:
        latest, expect = None, None
    m = re.search(r"Last updated ([A-Z][a-z]+ \d{4})", home)
    R.check("C9 footer 'Last updated' = month of the latest applied migration",
            bool(m) and (expect is None or m.group(1) == expect),
            f"footer {m.group(1) if m else 'not found'}, latest migration applied {latest}")
    applied = {r[0] for r in q("SELECT filename FROM _migrations")} if latest else set()
    pending = sorted(p.name for p in (ROOT / "migrations").glob("[0-9][0-9][0-9]_*.sql") if p.name not in applied)
    R.check("migrations on disk are all recorded in _migrations", not pending,
            f"not recorded in this DB (footer date ignores them): {pending}", warn_only=True)


def check_chart_fields(R, get, q):
    """Each chart whose title names a quantity plots (and sorts by) that quantity."""
    for tpl, title, start, end, patterns in CHART_FIELD_CLAIMS:
        html = (TEMPLATES / tpl).read_text(encoding="utf-8")
        if title not in html:
            R.check(f"chart field: {tpl} '{title}'", False, "title not found; update CHART_FIELD_CLAIMS")
            continue
        i = html.find(start)
        j = html.find(end, i + len(start)) if i >= 0 else -1
        block = html[i:j if j > 0 else None] if i >= 0 else ""
        missing = [p for p in patterns if not re.search(p, block)]
        R.check(f"chart field: {tpl} '{title}' plots/sorts the titled quantity", bool(block) and not missing,
                f"missing in chart code: {missing}" if missing else "dataset and sort key match the title")
    # Server-side sorts for the "Top 15 by ... Capacity" charts
    unsorted = []
    for (code,) in q("SELECT code FROM technologies"):
        cb = get(f"/api/technologies/{enc(code)}/detail").get("country_breakdown") or []
        gw = [x["capacity_gw"] or 0 for x in cb]
        if gw != sorted(gw, reverse=True):
            unsorted.append(("technology", code))
        op_gw = q("SELECT COALESCE(SUM(r.gross_capacity_mw), 0) / 1000.0 FROM reactors r JOIN technologies t "
                  "ON r.technology_id = t.id WHERE t.code = ? AND r.status = 'Operational'", (code,))[0][0]
        if abs(sum(gw) - op_gw) > 0.05 * len(gw) + 0.001:
            unsorted.append(("technology GW not operating-only", code, round(sum(gw), 1), round(op_gw, 1)))
    for (status,) in q("SELECT DISTINCT status FROM reactors"):
        cb = get(f"/api/statuses/{enc(status)}/detail").get("country_breakdown") or []
        gw = [x["capacity_gw"] or 0 for x in cb]
        if gw != sorted(gw, reverse=True):
            unsorted.append(("status", status))
    R.check("chart field: technology / status 'Top 15 by Capacity' endpoints sort by capacity (tech: operating only)",
            not unsorted, f"problems: {unsorted}")


def check_planned(R, get, q):
    """Finding 13: the homepage Planned tab and the planned pages use one capacity basis."""
    rows = get("/api/planned?api_key=demo-key-12345")["planned_reactors"]
    tab_total = sum(r.get("capacity_mw") or 0 for r in rows)
    page_total = 0
    for (name,) in q("SELECT DISTINCT project_name FROM planned_reactors"):
        j = get(f"/api/planned/{enc(name)}")
        page_total += sum(u.get("capacity_mw") or 0 for u in j.get("units") or [])
    db_total = q("SELECT COALESCE(SUM(COALESCE(net_capacity_mw, gross_capacity_mw)), 0) FROM planned_reactors")[0][0]
    R.check("planned capacity: homepage tab = planned pages = net-else-gross total",
            abs(tab_total - page_total) < 0.5 and abs(tab_total - db_total) < 0.5,
            f"tab {tab_total:,.0f} MW, pages {page_total:,.0f} MW, DB {db_total:,.0f} MW")


def check_browser(R, db_path, q, reactor_ids, port):
    """C8 (rendered) + smoke test: real pages in headless Chrome; the error panel stays hidden."""
    if not CHROME.exists():
        R.check("rendered pages (headless Chrome)", True, f"skipped: {CHROME} not found", warn_only=True)
        return
    first = lambda sql: (q(sql) or [[None]])[0][0]
    pages = ["/", "/sources", "/lineages", "/containment",
             f"/country/{enc('France')}", f"/country/{enc('Japan')}",
             f"/plant/{enc(first('SELECT plant_name FROM reactors ORDER BY id'))}",
             f"/technology/{enc('PWR')}", f"/status/{enc('Operational')}", f"/status/{enc('Shutdown')}",
             f"/supplier/{enc(first('SELECT s.name FROM suppliers s JOIN reactors r ON r.supplier_id = s.id ORDER BY r.id'))}",
             f"/owner/{enc(first('SELECT owner FROM reactors WHERE owner IS NOT NULL ORDER BY id'))}",
             f"/model/{enc(first('SELECT m.name FROM models m JOIN reactors r ON r.model_id = m.id ORDER BY r.id'))}",
             f"/lineage/{first('SELECT slug FROM design_lineages ORDER BY id')}",
             f"/containment/{enc(first('SELECT containment_type FROM reactors WHERE containment_type IS NOT NULL ORDER BY id'))}",
             f"/planned/{enc(first('SELECT project_name FROM planned_reactors ORDER BY id'))}"]
    pages += [f"/reactor/{rid}" for rid in reactor_ids]

    try:  # never test (or stop) someone else's server: the port must be free
        urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2)
        R.check("rendered pages (headless Chrome)", False, f"port {port} is already in use; choose another with --port")
        return
    except OSError:
        pass
    env = dict(os.environ, DATABASE_PATH=str(db_path), PORT=str(port), FLASK_DEBUG="false")
    server = subprocess.Popen([sys.executable, str(ROOT / "app.py")], cwd=str(ROOT), env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(base + "/api/stats", timeout=2)
                break
            except OSError:
                time.sleep(0.5)
        else:
            R.check("rendered pages (headless Chrome)", False, f"server did not start on port {port}")
            return

        def render(path):
            try:
                status = urllib.request.urlopen(base + path, timeout=30).status
            except urllib.error.HTTPError as e:
                return path, e.code, ""
            prof = tempfile.mkdtemp(prefix="ndb-chrome-")
            try:
                out = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-first-run",
                                      f"--user-data-dir={prof}", "--virtual-time-budget=15000", "--dump-dom",
                                      base + path], capture_output=True, timeout=120)
                return path, status, out.stdout.decode("utf-8", "replace")
            except subprocess.TimeoutExpired:
                return path, status, ""
            finally:
                shutil.rmtree(prof, ignore_errors=True)

        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(render, pages))
    finally:
        server.terminate()  # by PID: the server this function started
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()

    failures = []
    for path, status, dom in results:
        dom = re.sub(r"<script\b.*?</script>", "", dom, flags=re.S | re.I)  # page text only, not JS source
        problems = []
        if status != 200:
            problems.append(f"HTTP {status}")
        if not dom:
            problems.append("no DOM (Chrome timed out)")
        err = re.search(r'<div[^>]*\bid="error"[^>]*>', dom)
        if err and "display: none" not in err.group(0):
            problems.append("error panel shown")
        content = re.search(r'<div[^>]*\bid="content"[^>]*>', dom)
        if content and "display: none" in content.group(0):
            problems.append("content still hidden")
        if "Failed to load data" in dom:
            problems.append("'Failed to load data' shown")
        if path == "/" and dom and re.search(r'id="stat-operational">--<', dom):
            problems.append("homepage stat cards not filled")
        # Page titles filled by JS (status-name, reactor-name, ...): blank = wrong field read (finding 9)
        for tid, text in re.findall(r'<[a-z0-9]+[^>]*\bid="([a-z]+-name)"[^>]*>(.*?)</', dom, re.S):
            if re.sub(r"<[^>]+>", "", text).strip() in ("", "Loading..."):
                problems.append(f"#{tid} is empty")
        if problems:
            failures.append((path, problems))
    n_reactor = sum(1 for p in pages if p.startswith("/reactor/"))
    R.check("rendered pages (headless Chrome): 200, content shown, error panel hidden", not failures,
            f"{len(pages)} pages incl. {n_reactor} reactor pages {reactor_ids[:12]}; failures: {failures}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "nuclear_reactors.db"))
    ap.add_argument("--migration")
    ap.add_argument("--no-browser", action="store_true", help="skip the headless-Chrome page check")
    ap.add_argument("--all-reactor-pages", action="store_true", help="render every reactor page in Chrome")
    ap.add_argument("--port", type=int, default=5021, help="port for the temporary server (browser check)")
    a = ap.parse_args()
    if a.migration:
        writes, hits = affected_surfaces(Path(a.migration).read_text(encoding="utf-8"))
        print("Writes:", ", ".join(sorted(writes)))
        print("Surfaces to re-check after applying:")
        for s, w in hits.items():
            print(f"  - {s}  <- {', '.join(sorted(w))}")
        if not hits:
            print("  (none declared; add the surface to DEPENDENCIES if this is wrong)")
        return
    R = run_checks(Path(a.db).resolve(), browser=not a.no_browser, all_reactor_pages=a.all_reactor_pages,
                   port=a.port)
    sys.exit(1 if R.print() else 0)


if __name__ == "__main__":
    main()
