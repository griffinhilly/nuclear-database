"""
Insert 2-4 sentence descriptions for all 134 nuclear power plant owners
into the entity_descriptions table.

Usage:
    python insert_owner_descriptions.py          # dry-run (preview)
    python insert_owner_descriptions.py --apply   # write to DB
"""

import sys
import sqlite3
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

# ---------------------------------------------------------------------------
# Manual descriptions for ~35 major operators
# ---------------------------------------------------------------------------
MANUAL_DESCRIPTIONS = {
    "EDF": (
        "Electricite de France (EDF) is the world's largest nuclear power operator, "
        "running 67 reactors across France with a combined capacity exceeding 71 GW. "
        "EDF's fleet is predominantly pressurized water reactors (PWRs) and forms the backbone "
        "of France's electricity system, which derives roughly 70% of its power from nuclear energy. "
        "The company also operated early gas-cooled and fast breeder reactor designs."
    ),
    "Rosenergoatom": (
        "Rosenergoatom is the sole operator of all civilian nuclear power plants in Russia, "
        "managing a fleet of 45 reactors with a combined capacity of about 36.7 GW. "
        "Its portfolio includes VVER pressurized water reactors, RBMK light-water graphite reactors, "
        "and the BN-600/BN-800 sodium-cooled fast breeder reactors. "
        "As a subsidiary of Rosatom, it plays a central role in Russia's domestic energy strategy."
    ),
    "Korea Hydro and Nuclear Power Co": (
        "Korea Hydro and Nuclear Power Co (KHNP) is a subsidiary of Korea Electric Power Corporation (KEPCO) "
        "and operates all 30 nuclear reactors in South Korea, with 26 currently operational. "
        "KHNP's fleet of PWRs and PHWRs provides approximately 31.3 GW of capacity, "
        "making South Korea one of the world's most nuclear-dependent nations. "
        "KHNP has also become a major nuclear exporter through the APR1400 reactor design."
    ),
    "NPCIL": (
        "Nuclear Power Corporation of India Limited (NPCIL) is India's state-owned nuclear utility, "
        "operating 28 reactors with 21 currently in service across multiple sites. "
        "Its fleet includes indigenous pressurized heavy water reactors (PHWRs) as well as imported "
        "BWRs and PWRs, with a total capacity of about 11.6 GW. "
        "NPCIL is central to India's ambitious nuclear expansion program."
    ),
    "NDA": (
        "The Nuclear Decommissioning Authority (NDA) is a UK government body responsible for "
        "the cleanup and decommissioning of the country's legacy nuclear fleet of 26 gas-cooled reactors. "
        "None of the NDA's assigned reactors remain operational, as the UK's first-generation Magnox "
        "stations have all been permanently shut down. "
        "The NDA manages one of the world's largest nuclear decommissioning programs."
    ),
    "Constellation Energy Generation, LLC": (
        "Constellation Energy Generation is the largest nuclear operator in the United States, "
        "running 24 reactors across multiple states with 21 currently operational. "
        "Its fleet spans PWRs, BWRs, and the retired Peach Bottom HTGR, "
        "providing roughly 23.8 GW of carbon-free generating capacity. "
        "Constellation was formed from the Exelon Generation nuclear fleet spin-off in 2022."
    ),
    "Energoatom": (
        "Energoatom (NAEK Energoatom) operates all 21 nuclear reactors in Ukraine, "
        "including Europe's largest nuclear power station at Zaporizhzhia. "
        "With 15 operational units providing about 19.6 GW of capacity, nuclear power "
        "supplies roughly half of Ukraine's electricity. "
        "Since Russia's 2022 invasion, Energoatom has operated under extraordinary wartime conditions, "
        "with the Zaporizhzhia plant occupied by Russian forces."
    ),
    "Tokyo EPCO": (
        "Tokyo Electric Power Company (TEPCO) is one of Japan's largest utilities, "
        "responsible for 17 nuclear reactors with a combined capacity of about 17.3 GW. "
        "Only one unit is currently operational, as most remain shut down following the "
        "2011 Fukushima Daiichi disaster, which occurred at TEPCO's Fukushima site. "
        "TEPCO continues to manage the decades-long Fukushima decommissioning effort."
    ),
    "EDF Energy": (
        "EDF Energy is the UK subsidiary of Electricite de France, operating 17 reactors "
        "including the country's fleet of Advanced Gas-Cooled Reactors (AGRs) and the new Hinkley Point C PWR under construction. "
        "Nine of its units remain operational with a combined capacity of about 13.8 GW. "
        "EDF Energy is the primary nuclear generator in the UK's current electricity market."
    ),
    "OPG": (
        "Ontario Power Generation (OPG) is a Crown corporation of the Province of Ontario, Canada, "
        "operating 12 CANDU pressurized heavy water reactors at the Darlington and Pickering stations. "
        "Eight units are currently operational, providing about 8.1 GW of capacity. "
        "OPG's nuclear fleet supplies roughly half of Ontario's electricity."
    ),
    "Kansai EPCO": (
        "Kansai Electric Power Company (KEPCO) is the largest PWR operator in Japan, "
        "with 11 reactors and a combined capacity of about 9.8 GW. "
        "Seven of its units have restarted under Japan's post-Fukushima regulatory regime, "
        "more than any other Japanese utility. "
        "Kansai EPCO operates the Mihama, Takahama, and Ohi nuclear stations."
    ),
    "China Guangdong Nuclear Power Group": (
        "China Guangdong Nuclear Power Group (CGNPG) was the predecessor organization to CGN "
        "(China General Nuclear Power Group), one of China's two major nuclear operators. "
        "It operates 10 PWR units with all reactors in service, providing about 10.9 GW of capacity. "
        "The group pioneered commercial nuclear power in China with the Daya Bay and Ling Ao stations near Hong Kong."
    ),
    "Bruce Power": (
        "Bruce Power operates the Bruce Nuclear Generating Station in Ontario, Canada, "
        "which is the world's largest operating nuclear power facility by number of units. "
        "All eight CANDU PHWR units are operational, providing about 6.8 GW of capacity. "
        "Bruce Power is a private partnership that leases the station from Ontario Power Generation."
    ),
    "Tennessee Valley Authority": (
        "The Tennessee Valley Authority (TVA) is a US federal utility operating seven nuclear reactors "
        "across three sites in Tennessee and Alabama, all currently operational. "
        "Its fleet includes both BWR and PWR designs with a combined capacity of about 8.3 GW. "
        "TVA is one of the largest public power providers in the United States."
    ),
    "Pakistan Atomic Energy Commission": (
        "The Pakistan Atomic Energy Commission (PAEC) operates all seven of Pakistan's nuclear power reactors, "
        "with six currently in service. "
        "Its fleet includes Chinese-supplied PWRs and a Canadian-origin PHWR at Karachi and Chashma, "
        "providing roughly 3.6 GW of capacity. "
        "PAEC is also responsible for Pakistan's nuclear research and fuel cycle activities."
    ),
    "Electrabel": (
        "Electrabel, now operating as ENGIE Electrabel, managed Belgium's entire fleet of seven PWR reactors "
        "at the Doel and Tihange nuclear power stations with a combined capacity of about 6.2 GW. "
        "Belgium began phasing out nuclear power, and only two units remain operational as of recent years. "
        "Electrabel has been a subsidiary of the French energy group ENGIE (formerly GDF Suez)."
    ),
    "CNNC": (
        "China National Nuclear Corporation (CNNC) is one of China's two major state-owned nuclear enterprises, "
        "operating seven reactors including both PWRs and the CFR-600 fast breeder reactor. "
        "Four of its units are currently operational with a combined capacity of about 4.7 GW. "
        "CNNC also oversees China's nuclear fuel cycle, weapons complex, and reactor export programs."
    ),
    "Taiwan Power Co.": (
        "Taiwan Power Company (Taipower) is the state-owned utility that operated all eight of Taiwan's "
        "nuclear reactors at three power stations, using both BWR and PWR designs. "
        "None are currently operational following Taiwan's nuclear phase-out policy, "
        "though the fleet had a combined capacity of about 7.9 GW. "
        "Debate over reversing the phase-out has continued in Taiwanese politics."
    ),
    "Qinshan Nuclear Power Company": (
        "Qinshan Nuclear Power Company operates seven reactors at the Qinshan Nuclear Power Plant "
        "in Zhejiang Province, China, all currently operational. "
        "The site includes China's first domestically designed PWR (Qinshan-1, operational since 1991) "
        "as well as PHWR units built with Canadian CANDU technology. "
        "The complex has a combined capacity of about 4.4 GW."
    ),
    "NextEra Energy": (
        "NextEra Energy is one of the largest electric utilities in the United States, "
        "operating six PWR reactors across Florida and Wisconsin, all currently in service. "
        "Its nuclear fleet provides about 5.0 GW of capacity and operates alongside "
        "NextEra's massive renewable energy portfolio. "
        "The company's nuclear plants include the Turkey Point and St. Lucie stations in Florida."
    ),
    "Duke Energy Carolinas, LLC": (
        "Duke Energy Carolinas operates five PWR reactors at the Catawba, McGuire, and Oconee "
        "nuclear stations in North and South Carolina, all currently operational. "
        "With a combined capacity of about 5.1 GW, these plants are a major source of "
        "baseload power for the Carolinas region. "
        "Duke Energy is one of the largest electric utilities in the United States."
    ),
    "Southern Company": (
        "Southern Company operates four nuclear reactors through its subsidiaries, "
        "including the Hatch BWR and Farley PWR stations, all currently operational. "
        "The company's nuclear capacity totals about 3.7 GW. "
        "Southern Company's subsidiary Georgia Power brought the Vogtle 3 and 4 AP1000 units online, "
        "the first new nuclear builds in the US in a generation."
    ),
    "ENEC": (
        "The Emirates Nuclear Energy Corporation (ENEC) operates four APR1400 pressurized water reactors "
        "at the Barakah Nuclear Energy Plant in the UAE, all operational. "
        "With a combined capacity of about 5.6 GW, Barakah makes the UAE the first Arab nation "
        "to generate nuclear electricity. "
        "The plant was built in partnership with Korea Electric Power Corporation (KEPCO)."
    ),
    "TVO": (
        "Teollisuuden Voima (TVO) operates three nuclear reactors at the Olkiluoto site in Finland, "
        "including two BWRs and the EPR (Olkiluoto 3), all currently operational. "
        "With a combined capacity of about 3.5 GW, Olkiluoto is Finland's largest power plant. "
        "The Olkiluoto 3 EPR, which began commercial operation in 2023 after years of delays, "
        "is the largest nuclear reactor in Europe."
    ),
    "Fortum Power and Heat": (
        "Fortum Power and Heat operates two VVER-440 pressurized water reactors "
        "at the Loviisa Nuclear Power Plant in Finland, both currently operational. "
        "The plant has a combined capacity of about 1.0 GW and is notable as one of the few "
        "Western-operated plants using Soviet-designed reactor technology. "
        "Fortum is a Finnish state-majority-owned energy company."
    ),
    "ESKOM": (
        "Eskom operates the Koeberg Nuclear Power Station near Cape Town, South Africa, "
        "the only nuclear power plant on the African continent. "
        "Its two PWR units are both operational with a combined capacity of about 1.9 GW. "
        "Koeberg provides critical baseload electricity to South Africa's Western Cape region."
    ),
    "Comision Federal de Electricidad": (
        "The Comision Federal de Electricidad (CFE) is Mexico's state-owned electric utility, "
        "operating the country's only nuclear power station at Laguna Verde in Veracruz. "
        "Its two BWR units are both operational with a combined capacity of about 1.6 GW. "
        "Laguna Verde is the sole nuclear power plant in Latin America outside of Argentina and Brazil."
    ),
    "MECA": (
        "MECA (Societatea Nationala Nuclearelectrica) operates the Cernavoda Nuclear Power Plant, "
        "Romania's only nuclear facility, with two CANDU PHWR units both currently operational. "
        "The plant provides about 1.4 GW of capacity, supplying roughly 20% of Romania's electricity. "
        "Two additional units at Cernavoda have been planned for decades but remain unbuilt."
    ),
    "NEK": (
        "Nuklearna elektrarna Krsko (NEK) operates Slovenia's sole nuclear reactor, "
        "a Westinghouse PWR at the Krsko Nuclear Power Plant. "
        "The 700 MW unit is co-owned by Slovenia and Croatia and has been operational since 1983. "
        "Krsko provides approximately one-third of Slovenia's electricity."
    ),
    "BelNPP": (
        "BelNPP operates Belarus's only nuclear power facility, the Belarusian Nuclear Power Plant "
        "near Ostrovets, featuring two Russian-designed VVER-1200 (AES-2006) pressurized water reactors. "
        "Both units are operational with a combined capacity of about 2.4 GW. "
        "The plant, which began generation in 2020, made Belarus the newest country to adopt nuclear power in Europe."
    ),
    "BAEC": (
        "The Bangladesh Atomic Energy Commission (BAEC) oversees the Rooppur Nuclear Power Plant, "
        "Bangladesh's first nuclear power facility currently under construction with two Russian-designed VVER-1200 reactors. "
        "The two units will have a combined capacity of about 2.4 GW when completed. "
        "The project represents Bangladesh's entry into nuclear power generation."
    ),
    "ANPPCJSC": (
        "ANPPCJSC (Armenian Nuclear Power Plant Closed Joint Stock Company) operates the Metsamor Nuclear Power Plant, "
        "Armenia's sole nuclear facility near the Turkish border. "
        "One VVER-440 unit remains operational (the other was permanently shut down), providing about 0.4 GW "
        "and generating roughly one-third of Armenia's electricity. "
        "The plant has operated well beyond its original design life."
    ),
    "Georgia Power Co": (
        "Georgia Power Company, a subsidiary of Southern Company, operates four PWR reactors "
        "at the Hatch and Vogtle nuclear stations in Georgia, all currently operational. "
        "Its fleet includes the Vogtle Units 3 and 4 AP1000 reactors, the first new nuclear units "
        "built in the United States in over 30 years. "
        "Georgia Power's nuclear capacity totals about 5.0 GW."
    ),
    "Dominion Energy Virginia": (
        "Dominion Energy Virginia operates four PWR reactors at the North Anna and Surry nuclear stations "
        "in Virginia, all currently operational with a combined capacity of about 3.8 GW. "
        "These stations are among the oldest operating nuclear plants in the US, "
        "with Surry having begun commercial operation in 1972. "
        "Dominion is one of the largest energy companies in the eastern United States."
    ),
    "COGEMA": (
        "COGEMA (Compagnie Generale des Matieres Nucleaires) was a French state-owned company "
        "focused on the nuclear fuel cycle, including uranium mining, enrichment, and reprocessing. "
        "It operated two small gas-cooled reactors with a combined capacity of about 0.1 GW, "
        "both now permanently shut down. "
        "COGEMA was reorganized into Orano (formerly Areva NC) in 2018."
    ),
}


def get_owner_data(conn):
    """Query all unique owners with their reactor counts and metadata."""
    cur = conn.cursor()
    cur.execute("""
        SELECT r.owner, COUNT(*) as total,
               SUM(CASE WHEN r.status = 'Operational' THEN 1 ELSE 0 END) as oper,
               GROUP_CONCAT(DISTINCT c.name) as countries,
               GROUP_CONCAT(DISTINCT t.code) as techs,
               ROUND(SUM(r.gross_capacity_mw) / 1000.0, 1) as capacity_gw
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        WHERE r.owner IS NOT NULL
        GROUP BY r.owner
        ORDER BY total DESC
    """)
    return cur.fetchall()


def format_countries(countries_str):
    """Format country list for natural language."""
    if not countries_str:
        return "unknown countries"
    countries = countries_str.split(",")
    if len(countries) == 1:
        return countries[0]
    if len(countries) == 2:
        return f"{countries[0]} and {countries[1]}"
    return ", ".join(countries[:-1]) + f", and {countries[-1]}"


def format_tech_summary(techs_str, capacity_gw):
    """Build a brief technology/capacity sentence fragment."""
    if not techs_str and not capacity_gw:
        return ""
    parts = []
    if techs_str:
        codes = techs_str.split(",")
        tech_map = {
            "PWR": "pressurized water reactor",
            "BWR": "boiling water reactor",
            "PHWR": "pressurized heavy water reactor",
            "GCR": "gas-cooled reactor",
            "LWGR": "light-water graphite reactor",
            "FBR": "fast breeder reactor",
            "HTGR": "high-temperature gas-cooled reactor",
            "HWGCR": "heavy-water gas-cooled reactor",
            "HWLWR": "heavy-water light-water reactor",
            "SGHWR": "steam-generating heavy water reactor",
            "OCM": "organic-cooled/moderated reactor",
        }
        if len(codes) == 1:
            name = tech_map.get(codes[0], codes[0])
            parts.append(f"{name} ({codes[0]}) technology")
        else:
            parts.append(f"{', '.join(codes)} technology")
    if capacity_gw and capacity_gw > 0:
        parts.append(f"with a combined capacity of about {capacity_gw} GW")
    return " ".join(parts)


def generate_template_description(owner, total, oper, countries_str, techs_str, capacity_gw):
    """Generate a template description from database data."""
    reactor_word = "reactor" if total == 1 else "reactors"
    country_text = format_countries(countries_str)

    # First sentence: owner, count, country
    sentence1 = f"{owner} operates {total} nuclear {reactor_word} in {country_text}"

    # Operational status clause
    if oper == total:
        sentence1 += ", all currently operational."
    elif oper == 0:
        sentence1 += ", none of which are currently operational."
    else:
        sentence1 += f", {oper} of which {'is' if oper == 1 else 'are'} currently operational."

    # Second sentence: tech and capacity
    tech_info = format_tech_summary(techs_str, capacity_gw)
    if tech_info:
        sentence2 = f"Its fleet employs {tech_info}."
    else:
        sentence2 = ""

    return f"{sentence1} {sentence2}".strip()


def main():
    apply = "--apply" in sys.argv

    conn = sqlite3.connect(str(DB_PATH))
    owners = get_owner_data(conn)

    print(f"Found {len(owners)} unique owners in database")
    print(f"Manual descriptions: {len(MANUAL_DESCRIPTIONS)}")
    print(f"Auto-generated: {len(owners) - len(MANUAL_DESCRIPTIONS)}")
    print()

    descriptions = []
    manual_used = set()

    for owner, total, oper, countries, techs, capacity_gw in owners:
        if owner in MANUAL_DESCRIPTIONS:
            desc = MANUAL_DESCRIPTIONS[owner]
            manual_used.add(owner)
            source = "Manual description with AI assistance"
        else:
            desc = generate_template_description(owner, total, oper, countries, techs, capacity_gw)
            source = "Auto-generated from database metadata"
        descriptions.append((owner, desc, source))

    # Check for manual descriptions that didn't match any owner
    unmatched = set(MANUAL_DESCRIPTIONS.keys()) - manual_used
    if unmatched:
        print(f"WARNING: {len(unmatched)} manual descriptions did not match any owner:")
        for name in sorted(unmatched):
            print(f"  - {name}")
        print()

    # Preview
    for owner, desc, source in descriptions:
        tag = "[MANUAL]" if source.startswith("Manual") else "[AUTO]  "
        print(f"{tag} {owner}")
        print(f"         {desc[:120]}{'...' if len(desc) > 120 else ''}")
        print()

    if apply:
        cur = conn.cursor()
        cur.executemany(
            """INSERT OR REPLACE INTO entity_descriptions
               (entity_type, entity_name, description, source)
               VALUES ('owner', ?, ?, ?)""",
            [(owner, desc, source) for owner, desc, source in descriptions],
        )
        conn.commit()
        print(f"Inserted/updated {len(descriptions)} owner descriptions.")
    else:
        print("Dry run complete. Use --apply to write to database.")

    conn.close()


if __name__ == "__main__":
    main()
