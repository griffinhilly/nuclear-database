"""
WNA Audit Script — Compare World Nuclear Association reactor data against our database.

Scrapes WNA country summary pages for all non-Chinese reactors, then compares:
- Reactor existence (missing from either side)
- Status (Operational/UC/Shutdown)
- Net capacity (MWe)
- Model/design series
- Reactor type (PWR/BWR/etc.)
- Key dates (grid connection, construction start, permanent shutdown)

Outputs: wna_audit_report.txt (human-readable) + wna_scraped_data.json (raw data)
"""

import json
import os
import re
import sqlite3
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import ssl
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = "nuclear_reactors.db"
BASE_URL = "https://world-nuclear.org/nuclear-reactor-database/summary/"

# Map our DB country names to WNA URL slugs
COUNTRY_URL_MAP = {
    "Argentina": "Argentina",
    "Armenia": "Armenia",
    "Bangladesh": "Bangladesh",
    "Belarus": "Belarus",
    "Belgium": "Belgium",
    "Brazil": "Brazil",
    "Bulgaria": "Bulgaria",
    "Canada": "Canada",
    "Czech Republic": "Czech Republic",
    "Egypt": "Egypt",
    "Finland": "Finland",
    "France": "France",
    "Germany": "Germany",
    "Hungary": "Hungary",
    "India": "India",
    "Iran": "Iran",
    "Italy": "Italy",
    "Japan": "Japan",
    "Kazakhstan": "Kazakhstan",
    "Lithuania": "Lithuania",
    "Mexico": "Mexico",
    "Netherlands": "Netherlands",
    "Pakistan": "Pakistan",
    "Romania": "Romania",
    "Russia": "Russia",
    "Slovakia": "Slovakia",
    "Slovenia": "Slovenia",
    "South Africa": "South Africa",
    "South Korea": "South Korea",
    "Spain": "Spain",
    "Sweden": "Sweden",
    "Switzerland": "Switzerland",
    "Taiwan": "Taiwan",
    "Turkey": "Turkey",
    "UAE": "United Arab Emirates",
    "UK": "United Kingdom",
    "USA": "United States Of America",
    "Ukraine": "Ukraine",
}

# Explicit name overrides: (country, WNA name) -> (DB plant_name, DB unit_number)
# For reactors where automatic matching cannot work due to fundamentally different names
NAME_OVERRIDES = {
    # Belarus — WNA uses site name, we use project name
    ("Belarus", "Ostrovets 1"): ("Belarusian", "1"),
    ("Belarus", "Ostrovets 2"): ("Belarusian", "2"),
    # France — various historical naming differences
    ("France", "Chinon A 1"): ("Chinon A (EDF1)", "1"),
    ("France", "Chinon A 2"): ("Chinon A (EDF2)", "2"),
    ("France", "Chinon A 3"): ("Chinon A (EDF3)", "3"),
    ("France", "Chooz A (Ardennes)"): ("Chooz-A", "1"),
    ("France", "El 4 (Monts D\u2019Arree)"): ("Brennilis", "1"),  # curly apostrophe
    ("France", "El 4 (Monts D'Arree)"): ("Brennilis", "1"),  # straight apostrophe
    ("France", "G 2 (Marcoule)"): ("G2", "2"),
    ("France", "G 3 (Marcoule)"): ("G3", "3"),
    # Germany — WNA uses A/B/C for units, we use 1/2/3
    ("Germany", "Biblis A"): ("Biblis", "1"),
    ("Germany", "Biblis B"): ("Biblis", "2"),
    ("Germany", "Gundremmingen A"): ("Gundremmingen", "1"),
    ("Germany", "Gundremmingen B"): ("Gundremmingen", "2"),
    ("Germany", "Gundremmingen C"): ("Gundremmingen", "3"),
    # Hungary — WNA uses "Paks II-1", we use "Paks 5"
    ("Hungary", "Paks II-1"): ("Paks", "5"),
    # Russia — multi-site naming (old RBMK units)
    ("Russia", "Kursk 1"): ("Kursk 1", "1"),
    ("Russia", "Kursk 2"): ("Kursk 1", "2"),
    ("Russia", "Kursk 3"): ("Kursk 1", "3"),
    ("Russia", "Kursk 4"): ("Kursk 1", "4"),
    ("Russia", "Kursk 2-1"): ("Kursk 2", "1"),
    ("Russia", "Kursk 2-2"): ("Kursk 2", "2"),
    ("Russia", "Leningrad 1"): ("Leningrad 1", "1"),
    ("Russia", "Leningrad 2"): ("Leningrad 1", "2"),
    ("Russia", "Leningrad 3"): ("Leningrad 1", "3"),
    ("Russia", "Leningrad 4"): ("Leningrad 1", "4"),
    ("Russia", "Leningrad 2 1"): ("Leningrad 2", "1"),
    ("Russia", "Leningrad 2 2"): ("Leningrad 2", "2"),
    ("Russia", "Leningrad 2-3"): ("Leningrad 2", "3"),
    ("Russia", "Leningrad 2-4"): ("Leningrad 2", "4"),
    ("Russia", "Novovoronezh 1"): ("Novovoronezh 1", "1"),
    ("Russia", "Novovoronezh 2"): ("Novovoronezh 1", "2"),
    ("Russia", "Novovoronezh 3"): ("Novovoronezh 1", "3"),
    ("Russia", "Novovoronezh 4"): ("Novovoronezh 1", "4"),
    ("Russia", "Novovoronezh 5"): ("Novovoronezh 1", "5"),
    ("Russia", "Novovoronezh 2 1"): ("Novovoronezh 2", "1"),
    ("Russia", "Novovoronezh 2 2"): ("Novovoronezh 2", "2"),
    ("Russia", "Seversk BREST-OD-300"): ("BREST", "1"),
    ("Russia", "APS 1 Obninsk"): ("APS1 Obninsk", "1"),
    # South Korea — Saeul is renamed Shin-Kori 3-6
    ("South Korea", "Saeul 1"): ("Shin-Kori", "3"),
    ("South Korea", "Saeul 2"): ("Shin-Kori", "4"),
    ("South Korea", "Saeul 3"): ("Shin-Kori", "5"),
    ("South Korea", "Saeul 4"): ("Shin-Kori", "6"),
    # UK — Calder Hall reactors are "Sellafield" in our DB
    ("UK", "Calder Hall 1"): ("Sellafield", "1"),
    ("UK", "Calder Hall 2"): ("Sellafield", "2"),
    ("UK", "Calder Hall 3"): ("Sellafield", "3"),
    ("UK", "Calder Hall 4"): ("Sellafield", "4"),
    ("UK", "Windscale AGR"): ("Sellafield", "5"),
    # Ukraine — transliteration difference
    ("Ukraine", "Khmelnitski 1"): ("Khmelnytskyi", "1"),
    ("Ukraine", "Khmelnitski 2"): ("Khmelnytskyi", "2"),
    ("Ukraine", "Khmelnitski 3"): ("Khmelnytskyi", "3"),
    ("Ukraine", "Khmelnitski 4"): ("Khmelnytskyi", "4"),
    # France — El 4 / Brennilis (HTML entities in apostrophe)
    ("France", "El 4 (Monts D'Arree)"): ("Brennilis", "1"),
    # Germany — ß/ss difference
    ("Germany", "HDR Grosswelzheim"): ("HDR Großwelzheim", "1"),
    # Japan — JPDR full name
    ("Japan", "Japan Power Demonstration Reactor (JPDR)"): ("JPDR", "1"),
    # Russia — Leningrad 2-4 (new VVER UC unit)
    ("Russia", "Leningrad 2-4"): ("Leningrad 2", "4"),  # may not exist in DB yet
    # UK — Winfrith SGHWR
    ("UK", "Winfrith SGHWR"): ("Winfrith", "1"),
    # USA — formal names vs our abbreviated names
    ("USA", "Enrico Fermi 1"): ("Fermi", "1"),
    ("USA", "Enrico Fermi 2"): ("Fermi", "2"),
    ("USA", "Carolinas\u2013Virginia Tube Reactor (CVTR)"): ("CVTR", "1"),
    ("USA", "Carolinas\uFFFDVirginia Tube Reactor (CVTR)"): ("CVTR", "1"),
    ("USA", "Vallecitos"): ("GE Vallecitos", "1"),
    ("USA", "Virgil C. Summer 1"): ("Summer (V C Summer)", "1"),
}


def strip_diacritics(text):
    """Remove diacritics/accents from text (ü->u, ö->o, å->a, etc.)."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def german_umlaut_to_ascii(text):
    """Convert German umlaut spellings: ue->ü, oe->ö, ae->ä (for matching WNA->DB)."""
    # This converts WNA's ASCII umlauts to the Unicode we use in our DB
    # Only apply to known German patterns to avoid false positives
    text = text.replace("ue", "ü").replace("oe", "ö").replace("ae", "ä")
    text = text.replace("Ue", "Ü").replace("Oe", "Ö").replace("Ae", "Ä")
    return text


def fetch_page(country_wna_name):
    """Fetch a WNA country summary page and return HTML."""
    encoded = urllib.parse.quote(country_wna_name)
    url = f"{BASE_URL}{encoded}"
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=30)
        return resp.read().decode("utf-8")
    except Exception as e:
        print(f"  ERROR fetching {country_wna_name}: {e}")
        return None


def parse_tables(html):
    """Parse reactor tables from WNA country summary page HTML."""
    reactors = []
    table_pattern = re.compile(r'<table\s+class="table\s+(table\d+)\s*">(.*?)</table>', re.DOTALL)

    for match in table_pattern.finditer(html):
        table_class = match.group(1)
        table_html = match.group(2)

        if table_class == "table1":
            table_type = "operable"
        elif table_class == "table2":
            table_type = "uc"
        elif table_class == "table3":
            table_type = "shutdown"
        else:
            continue

        header_match = re.search(r'<thead.*?>(.*?)</thead>', table_html, re.DOTALL)
        if not header_match:
            continue

        tbody_match = re.search(r'<tbody>(.*?)</tbody>', table_html, re.DOTALL)
        if not tbody_match:
            continue

        rows = re.findall(r'<tr>(.*?)</tr>', tbody_match.group(1), re.DOTALL)
        for row_html in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            if len(cells) < 4:
                continue

            name_match = re.search(r'href="/nuclear-reactor-database/details/([^"]+)"[^>]*>([^<]+)</a>', cells[0])
            if name_match:
                slug = name_match.group(1)
                name = name_match.group(2).strip()
            else:
                name = re.sub(r'<[^>]+>', '', cells[0]).strip()
                slug = ""

            # Decode HTML entities in name
            import html as html_mod
            name = html_mod.unescape(name)

            model = re.sub(r'<[^>]+>', '', cells[1]).strip()
            process = re.sub(r'<[^>]+>', '', cells[2]).strip()

            cap_str = re.sub(r'<[^>]+>', '', cells[3]).strip().replace(',', '')
            try:
                capacity = float(cap_str) if cap_str else None
            except ValueError:
                capacity = None

            date_str = ""
            date_type = ""
            if len(cells) >= 5:
                date_str = re.sub(r'<[^>]+>', '', cells[4]).strip()
                if table_type == "operable":
                    date_type = "grid_connection"
                elif table_type == "uc":
                    date_type = "construction_start"
                elif table_type == "shutdown":
                    date_type = "permanent_shutdown"

            reactors.append({
                "name": name,
                "slug": slug,
                "model": model,
                "process": process,
                "capacity_mwe": capacity,
                "date_value": date_str,
                "date_type": date_type,
                "table_type": table_type,
            })

    return reactors


def parse_wna_date(date_str):
    """Parse WNA date format (DD/MM/YYYY) to ISO format (YYYY-MM-DD)."""
    date_str = date_str.strip()
    if not date_str or date_str == "—":
        return None
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def normalize_name(name):
    """Normalize a reactor name for fuzzy matching.

    Strips diacritics, removes parenthetical parts, normalizes whitespace/hyphens.
    """
    n = name.strip()
    # Remove parenthetical parts
    n = re.sub(r'\s*\([^)]+\)', '', n)
    # Strip diacritics and handle ß
    n = n.replace("ß", "ss")
    n = strip_diacritics(n)
    # Lowercase
    n = n.lower()
    # Replace hyphens and dots with spaces
    n = n.replace('-', ' ').replace('.', ' ')
    # Collapse whitespace
    n = re.sub(r'\s+', ' ', n).strip()
    return n


def normalize_status(status):
    """Normalize status strings for comparison."""
    s = status.lower().strip()
    if s in ("operable", "operational"):
        return "Operational"
    elif s in ("uc", "under construction"):
        return "Under Construction"
    elif s in ("shutdown", "permanent shutdown", "permanently shutdown"):
        return "Permanent Shutdown"
    elif s in ("suspended",):
        return "Suspended"
    return status


def map_wna_status(table_type):
    """Map WNA table type to our status."""
    if table_type == "operable":
        return "Operational"
    elif table_type == "uc":
        return "Under Construction"
    elif table_type == "shutdown":
        return "Permanent Shutdown"
    return "Unknown"


def normalize_process(process):
    """Normalize WNA process/type to our technology names."""
    mapping = {
        "PWR": "Pressurized Water Reactor",
        "BWR": "Boiling Water Reactor",
        "PHWR": "Pressurized Heavy Water Reactor",
        "GCR": "Gas-Cooled Reactor",
        "LWGR": "Light Water Graphite Reactor",
        "FBR": "Fast Breeder Reactor",
        "HWGCR": "Heavy Water Gas-Cooled Reactor",
        "SGHWR": "Steam Generating Heavy Water Reactor",
        "HWLWR": "Heavy Water Light Water Reactor",
        "HTGR": "High Temperature Gas-Cooled Reactor",
    }
    return mapping.get(process.upper(), process)


def load_db_reactors():
    """Load all non-Chinese reactors from our database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT r.id, r.plant_name, r.unit_number, r.status,
               r.net_capacity_mw, r.gross_capacity_mw, r.thermal_capacity_mw,
               r.construction_start, r.first_criticality, r.grid_connection,
               r.commercial_operation, r.permanent_shutdown,
               r.design_series, r.containment_type, r.owner, r.operator,
               c.name as country, t.name as tech_type,
               m.name as model_name
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        LEFT JOIN models m ON r.model_id = m.id
        WHERE c.name != 'China'
        ORDER BY c.name, r.plant_name, r.unit_number
    """)

    reactors = [dict(row) for row in cur.fetchall()]
    conn.close()
    return reactors


def build_db_lookup(db_reactors):
    """Build multiple lookup dicts for matching WNA reactors to DB reactors."""
    lookup = {}

    for r in db_reactors:
        country = r["country"]
        plant = r["plant_name"]
        unit = r["unit_number"] or ""

        # Full name: "Plant Unit"
        full_name = f"{plant} {unit}".strip()
        key = (country, normalize_name(full_name))
        lookup[key] = r

        # Plant name only (for single-unit matching)
        key_plant = (country, normalize_name(plant))
        # Only set if not already set (avoid overwriting multi-unit plants)
        if key_plant not in lookup:
            lookup[key_plant] = r

        # Also index by parenthetical content (for US plants)
        # "Cook (Donald C. Cook)" -> also match "Donald C. Cook"
        paren_match = re.search(r'\(([^)]+)\)', plant)
        if paren_match:
            alt_name = paren_match.group(1)
            if unit:
                alt_full = f"{alt_name} {unit}"
            else:
                alt_full = alt_name
            key_alt = (country, normalize_name(alt_full))
            lookup[key_alt] = r

    return lookup


def match_reactor(wna_reactor, country, db_lookup, db_reactors):
    """Try to match a WNA reactor to a DB reactor. Returns db_reactor or None."""
    wna_name = wna_reactor["name"]

    # 1. Check explicit overrides first
    override_key = (country, wna_name)
    if override_key in NAME_OVERRIDES:
        plant, unit = NAME_OVERRIDES[override_key]
        country_reactors = [r for r in db_reactors if r["country"] == country]
        for r in country_reactors:
            if r["plant_name"] == plant and r["unit_number"] == unit:
                return r
        # Override target not found in DB — genuinely missing
        return None

    # 2. Normalize WNA name and try direct lookup
    norm = normalize_name(wna_name)
    key = (country, norm)
    if key in db_lookup:
        return db_lookup[key]

    # 3. Parse WNA name into plant + unit, try lookup
    plant, unit = _parse_wna_name(wna_name)
    if unit:
        full = f"{plant} {unit}"
        key2 = (country, normalize_name(full))
        if key2 in db_lookup:
            return db_lookup[key2]

    # 4. If WNA has no unit number, try with unit "1"
    if not unit:
        full_with_1 = f"{wna_name} 1"
        key3 = (country, normalize_name(full_with_1))
        if key3 in db_lookup:
            return db_lookup[key3]

    # 5. Try German umlaut conversion (WNA uses ASCII, we use Unicode)
    if country == "Germany" or country == "Switzerland" or country == "Sweden":
        umlaut_name = german_umlaut_to_ascii(wna_name)
        if umlaut_name != wna_name:
            norm_u = normalize_name(umlaut_name)
            key_u = (country, norm_u)
            if key_u in db_lookup:
                return db_lookup[key_u]
            # Also try with unit "1"
            key_u1 = (country, normalize_name(umlaut_name + " 1"))
            if key_u1 in db_lookup:
                return db_lookup[key_u1]

    # 6. Try matching against DB names with diacritics stripped
    country_reactors = [r for r in db_reactors if r["country"] == country]
    for r in country_reactors:
        db_full = r["plant_name"]
        if r["unit_number"]:
            db_full += " " + r["unit_number"]

        if normalize_name(db_full) == norm:
            return r

        # Match ignoring all spaces
        if normalize_name(db_full).replace(" ", "") == norm.replace(" ", ""):
            return r

    # 7. Try matching WNA name against parenthetical content in DB plant names
    for r in country_reactors:
        paren_match = re.search(r'\(([^)]+)\)', r["plant_name"])
        if paren_match:
            alt_name = paren_match.group(1)
            db_alt_full = alt_name
            if r["unit_number"]:
                db_alt_full += " " + r["unit_number"]
            if normalize_name(db_alt_full) == norm:
                return r

    # 8. Try matching WNA plant part against DB plant_name with unit
    if unit:
        for r in country_reactors:
            if normalize_name(r["plant_name"]) == normalize_name(plant) and r["unit_number"] == unit:
                return r

    # 9. UK: WNA uses "X A 1" for AGR plants, we use "X 1"
    if country == "UK":
        # Strip " A " from WNA names (Hartlepool A 1 -> Hartlepool 1)
        stripped = re.sub(r'\s+A\s+(\d+)$', r' \1', wna_name)
        if stripped != wna_name:
            key_uk = (country, normalize_name(stripped))
            if key_uk in db_lookup:
                return db_lookup[key_uk]

    # 10. Pakistan: WNA uses full name "Chashma Nuclear Power Plant 1", we use "Chashma 1"
    if "Nuclear Power Plant" in wna_name:
        short = re.sub(r'\s*Nuclear Power Plant\s*', ' ', wna_name).strip()
        short = re.sub(r'\s+', ' ', short)
        key_short = (country, normalize_name(short))
        if key_short in db_lookup:
            return db_lookup[key_short]

    # 11. USA: WNA uses full formal names, try matching against DB abbreviated names
    if country == "USA":
        # "Susquehanna Steam Electric Station 1" -> try "Susquehanna 1"
        # Try progressively shorter prefixes
        words = wna_name.split()
        for i in range(len(words) - 1, 0, -1):
            partial = " ".join(words[:i])
            # Check if the last word(s) are a number
            remainder = " ".join(words[i:])
            if re.match(r'^\d+$', remainder):
                key_partial = (country, normalize_name(f"{partial} {remainder}"))
                if key_partial in db_lookup:
                    return db_lookup[key_partial]
                # Also try without the number and with unit "1"
            # Or just try the first word + last number
        # Try first word + last number
        match_num = re.search(r'(\d+)\s*$', wna_name)
        if match_num:
            first_word = words[0]
            num = match_num.group(1)
            key_fw = (country, normalize_name(f"{first_word} {num}"))
            if key_fw in db_lookup:
                return db_lookup[key_fw]

    return None


def _parse_wna_name(wna_name):
    """Parse WNA reactor name into (plant_name, unit_number)."""
    # Remove parenthetical suffixes
    clean = re.sub(r'\s*\([^)]+\)\s*$', '', wna_name).strip()

    # Try to split at last space before a number
    match = re.match(r'^(.+?)\s+(\d+)$', clean)
    if match:
        return match.group(1).strip(), match.group(2)

    return clean, ""


def compare_dates(wna_date_str, db_date_str, tolerance_days=1):
    """Compare two date strings. Returns (match, wna_parsed, db_parsed)."""
    wna_parsed = parse_wna_date(wna_date_str)
    db_parsed = db_date_str

    if not wna_parsed and not db_parsed:
        return True, None, None
    if not wna_parsed or not db_parsed:
        return False, wna_parsed, db_parsed

    try:
        wna_dt = datetime.strptime(wna_parsed, "%Y-%m-%d")
        db_dt = datetime.strptime(db_parsed, "%Y-%m-%d")
        diff = abs((wna_dt - db_dt).days)
        return diff <= tolerance_days, wna_parsed, db_parsed
    except ValueError:
        return wna_parsed == db_parsed, wna_parsed, db_parsed


def main():
    print("=" * 70)
    print("WNA AUDIT — Comparing WNA reactor data against our database")
    print("=" * 70)

    # Load our DB
    print("\nLoading database...")
    db_reactors = load_db_reactors()
    db_lookup = build_db_lookup(db_reactors)
    print(f"  Loaded {len(db_reactors)} non-Chinese reactors from {len(set(r['country'] for r in db_reactors))} countries")

    # Check for cached scraped data
    all_wna_reactors = []
    scrape_errors = []

    if os.path.exists("wna_scraped_data.json"):
        import html as html_mod
        print("\nUsing cached WNA data from wna_scraped_data.json...")
        with open("wna_scraped_data.json", "r", encoding="utf-8") as f:
            all_wna_reactors = json.load(f)
        # Decode any HTML entities in cached names
        for r in all_wna_reactors:
            r["name"] = html_mod.unescape(r["name"])
        print(f"  Loaded {len(all_wna_reactors)} scraped reactors")
    else:
        print(f"\nScraping {len(COUNTRY_URL_MAP)} countries from WNA...")
        for i, (our_country, wna_country) in enumerate(sorted(COUNTRY_URL_MAP.items())):
            print(f"  [{i+1}/{len(COUNTRY_URL_MAP)}] {our_country}...", end=" ", flush=True)
            html = fetch_page(wna_country)
            if not html:
                scrape_errors.append(our_country)
                print("FAILED")
                continue
            reactors = parse_tables(html)
            print(f"{len(reactors)} reactors")
            for r in reactors:
                r["country"] = our_country
            all_wna_reactors.extend(reactors)
            if i < len(COUNTRY_URL_MAP) - 1:
                time.sleep(0.5)

        print(f"\nTotal WNA reactors scraped: {len(all_wna_reactors)}")
        with open("wna_scraped_data.json", "w", encoding="utf-8") as f:
            json.dump(all_wna_reactors, f, indent=2, ensure_ascii=False)
        print("Saved raw data to wna_scraped_data.json")

    # Match and compare
    print("\nMatching and comparing...")

    discrepancies = []
    wna_only = []
    matched_db_ids = set()

    for wna_r in all_wna_reactors:
        country = wna_r["country"]
        db_r = match_reactor(wna_r, country, db_lookup, db_reactors)

        if not db_r:
            wna_only.append(wna_r)
            continue

        matched_db_ids.add(db_r["id"])
        reactor_discs = []
        reactor_label = f"{wna_r['name']} ({country})"

        # Compare status
        wna_status = map_wna_status(wna_r["table_type"])
        db_status = normalize_status(db_r["status"])
        if wna_status != db_status:
            if db_status == "Suspended" and wna_status in ("Operational", "Permanent Shutdown"):
                reactor_discs.append(("STATUS", wna_status, db_status, "Our 'Suspended' vs WNA"))
            else:
                reactor_discs.append(("STATUS", wna_status, db_status, ""))

        # Compare capacity
        if wna_r["capacity_mwe"] is not None and db_r["net_capacity_mw"] is not None:
            diff = abs(wna_r["capacity_mwe"] - db_r["net_capacity_mw"])
            if diff > 1:
                reactor_discs.append((
                    "NET_CAPACITY",
                    f"{wna_r['capacity_mwe']:.0f} MWe",
                    f"{db_r['net_capacity_mw']:.0f} MWe",
                    f"diff: {diff:.0f} MWe"
                ))

        # Compare reactor type
        wna_type_full = normalize_process(wna_r["process"])
        if db_r["tech_type"] and wna_type_full != db_r["tech_type"]:
            reactor_discs.append(("TYPE", wna_r["process"], db_r["tech_type"], ""))

        # Compare date
        if wna_r["date_value"] and wna_r["date_type"]:
            db_date = db_r.get(wna_r["date_type"])
            match, wna_parsed, db_parsed = compare_dates(wna_r["date_value"], db_date)
            if not match:
                reactor_discs.append((
                    wna_r["date_type"].upper(),
                    wna_parsed or "(none)",
                    db_parsed or "(none)",
                    ""
                ))

        # Compare model/design_series (informational)
        if wna_r["model"] and db_r["design_series"]:
            wna_model_norm = normalize_name(wna_r["model"])
            db_series_norm = normalize_name(db_r["design_series"])
            if wna_model_norm != db_series_norm:
                reactor_discs.append((
                    "MODEL",
                    wna_r["model"],
                    db_r["design_series"],
                    "info"
                ))

        if reactor_discs:
            discrepancies.append((reactor_label, db_r["id"], reactor_discs))

    # Find DB reactors not in WNA
    db_unmatched = [r for r in db_reactors if r["id"] not in matched_db_ids]
    db_only_countries = {}
    for r in db_unmatched:
        country = r["country"]
        if country not in db_only_countries:
            db_only_countries[country] = []
        full_name = r["plant_name"]
        if r["unit_number"]:
            full_name += " " + r["unit_number"]
        db_only_countries[country].append((full_name, r["status"]))

    # Generate report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("WNA AUDIT REPORT")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report_lines.append("=" * 80)
    report_lines.append("")
    report_lines.append(f"WNA reactors scraped: {len(all_wna_reactors)}")
    report_lines.append(f"DB reactors (non-Chinese): {len(db_reactors)}")
    report_lines.append(f"Matched: {len(matched_db_ids)}")
    report_lines.append(f"WNA-only (not in our DB): {len(wna_only)}")
    report_lines.append(f"DB-only (not in WNA): {len(db_unmatched)}")
    report_lines.append(f"Reactors with discrepancies: {len(discrepancies)}")
    if scrape_errors:
        report_lines.append(f"Scrape failures: {scrape_errors}")

    # Discrepancies by type
    disc_by_type = {}
    for label, db_id, discs in discrepancies:
        for disc in discs:
            disc_type = disc[0]
            disc_by_type[disc_type] = disc_by_type.get(disc_type, 0) + 1

    report_lines.append("")
    report_lines.append("--- DISCREPANCY SUMMARY ---")
    for dtype, count in sorted(disc_by_type.items()):
        report_lines.append(f"  {dtype}: {count}")

    # Actionable discrepancies (non-MODEL)
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("ACTIONABLE DISCREPANCIES (Status, Capacity, Type, Dates)")
    report_lines.append("=" * 80)

    for label, db_id, discs in sorted(discrepancies):
        actionable = [d for d in discs if d[0] != "MODEL"]
        if actionable:
            report_lines.append(f"\n  {label} [DB id={db_id}]")
            for field, wna_val, db_val, note in actionable:
                note_str = f"  ({note})" if note else ""
                report_lines.append(f"    {field}: WNA={wna_val}  |  DB={db_val}{note_str}")

    # Model differences (informational)
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("MODEL/DESIGN SERIES DIFFERENCES (Informational)")
    report_lines.append("=" * 80)

    for label, db_id, discs in sorted(discrepancies):
        model_discs = [d for d in discs if d[0] == "MODEL"]
        if model_discs:
            for field, wna_val, db_val, note in model_discs:
                report_lines.append(f"  {label}: WNA={wna_val}  |  DB={db_val}")

    # WNA-only reactors
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("WNA-ONLY REACTORS (in WNA but not matched in our DB)")
    report_lines.append("=" * 80)

    if wna_only:
        for r in sorted(wna_only, key=lambda x: (x["country"], x["name"])):
            status = map_wna_status(r["table_type"])
            cap = f"{r['capacity_mwe']:.0f} MWe" if r["capacity_mwe"] else "?"
            report_lines.append(f"  {r['name']} ({r['country']}) — {status}, {cap}, {r['process']}")
    else:
        report_lines.append("  (none)")

    # DB-only reactors
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("DB-ONLY REACTORS (in our DB but not matched in WNA)")
    report_lines.append("=" * 80)

    if db_only_countries:
        for country in sorted(db_only_countries):
            report_lines.append(f"\n  {country}:")
            for name, status in sorted(db_only_countries[country]):
                report_lines.append(f"    {name} — {status}")
    else:
        report_lines.append("  (none)")

    report_lines.append("")

    report_text = "\n".join(report_lines)
    with open("wna_audit_report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)

    print(report_text)
    print(f"\nReport saved to wna_audit_report.txt")


if __name__ == "__main__":
    main()
