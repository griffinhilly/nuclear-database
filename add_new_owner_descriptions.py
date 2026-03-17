#!/usr/bin/env python3
"""Add entity descriptions for newly assigned owners."""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

DESCRIPTIONS = {
    "State Power Investment Corporation": (
        "State Power Investment Corporation (SPIC) is one of China's five major state-owned power "
        "generation groups, formed from the 2015 merger of China Power Investment Corporation and "
        "the State Nuclear Power Technology Corporation. SPIC operates nuclear plants including "
        "Haiyang (AP1000) and Shidaowan (CAP1400), and holds the intellectual property rights for "
        "China's indigenous CAP1400 reactor design."
    ),
    "Energiewerke Nord": (
        "Energiewerke Nord (EWN) is the German federal government company responsible for "
        "decommissioning the former East German nuclear facilities, primarily the five "
        "VVER-440 reactors at Greifswald and the Rheinsberg reactor. These Soviet-designed "
        "plants were shut down after German reunification in 1990."
    ),
    "MVM Paks Nuclear Power Plant Ltd": (
        "MVM Paks Nuclear Power Plant Ltd, a subsidiary of the Hungarian state energy company MVM, "
        "operates Hungary's only nuclear station at Paks. The four VVER-440 units provide "
        "approximately half of Hungary's electricity. A fifth unit (VVER-1200) is under "
        "construction as part of the Paks II project with Russian financing."
    ),
    "Nuclear Power Plants Authority": (
        "The Nuclear Power Plants Authority (NPPA) is the Egyptian government body responsible "
        "for developing and operating Egypt's nuclear power program. It is overseeing the "
        "construction of the El Dabaa station \u2014 four Russian VVER-1200 units that will make "
        "Egypt the first country in Africa and the Arab world with a large-scale nuclear fleet."
    ),
    "ENEL": (
        "ENEL (Ente Nazionale per l'Energia Elettrica) is Italy's largest energy company. "
        "It operated all four of Italy's nuclear power plants before the country's 1987 "
        "referendum ended nuclear power following Chernobyl. Decommissioning responsibilities "
        "were later transferred to Sogin."
    ),
    "KBG": (
        "Kernkraftwerk-Betriebsgesellschaft mbH (KBG) operated German experimental nuclear "
        "facilities including the MZFR heavy water reactor at Karlsruhe and the KNK-II "
        "sodium-cooled fast reactor, both now permanently shut down and decommissioned."
    ),
    "Ignalina NPP": (
        "Ignalina Nuclear Power Plant was the Lithuanian state enterprise operating the two "
        "RBMK-1500 reactors at Ignalina \u2014 the most powerful reactor units ever built. Both "
        "were shut down (2004 and 2009) as a condition of Lithuania's EU accession, despite "
        "strong domestic opposition to the closures."
    ),
    "Axpo": (
        "Axpo is Switzerland's largest energy company, headquartered in Baden. It operates the "
        "Beznau nuclear station, home to the world's oldest operating commercial nuclear reactor "
        "(Beznau-1, commissioned 1969). Axpo is also a major shareholder in the Leibstadt plant."
    ),
    "China Huaneng Group": (
        "China Huaneng Group is one of China's five major state-owned power generation companies. "
        "Its nuclear involvement centers on the Shidao Bay HTR-PM \u2014 the world's first commercial "
        "high-temperature gas-cooled pebble-bed reactor, which began operation in 2023."
    ),
    "Kernkraftwerk G\u00f6sgen-D\u00e4niken AG": (
        "Kernkraftwerk G\u00f6sgen-D\u00e4niken AG operates the G\u00f6sgen nuclear plant in the canton of "
        "Solothurn, Switzerland. The single-unit 1,010 MW PWR is majority-owned by Alpiq and "
        "is one of Switzerland's four remaining nuclear stations."
    ),
    "Kernkraftwerk Leibstadt AG": (
        "Kernkraftwerk Leibstadt AG operates Switzerland's newest and largest nuclear plant, "
        "the Leibstadt BWR on the Rhine near the German border. The plant is jointly owned by "
        "several Swiss utilities including Axpo, Alpiq, and BKW."
    ),
    "BKW": (
        "BKW (formerly Bernische Kraftwerke) is a Swiss energy company based in Bern. It "
        "operated the M\u00fchleberg nuclear plant, a GE BWR that was permanently shut down in "
        "December 2019 \u2014 the first Swiss reactor to close, now under decommissioning."
    ),
    "HKG": (
        "Hochtemperatur-Kernkraftwerk GmbH (HKG) operated the THTR-300 high-temperature "
        "gas-cooled pebble-bed reactor in Hamm-Uentrop, Germany. The experimental reactor "
        "operated only briefly (1985-1989) before being shut down due to technical problems "
        "and political opposition."
    ),
    "SNA": (
        "Soci\u00e9t\u00e9 Nationale pour l'Encouragement de la Technique Atomique Industrielle (SNA) "
        "operated the experimental Lucens reactor in Switzerland, a CO2-cooled heavy water "
        "reactor that suffered a partial meltdown in 1969 \u2014 Switzerland's worst nuclear incident."
    ),
    "AVR GmbH": (
        "Arbeitsgemeinschaft Versuchsreaktor GmbH (AVR) operated the AVR experimental "
        "pebble-bed reactor in J\u00fclich, Germany (1967-1988). This prototype high-temperature "
        "gas-cooled reactor provided key experience for pebble-bed technology later adopted "
        "by China's HTR-PM."
    ),
    "AEG": (
        "AEG (Allgemeine Elektricit\u00e4ts-Gesellschaft) was a major German industrial conglomerate "
        "that built the HDR Gro\u00dfwelzheim experimental reactor, a superheated steam BWR prototype. "
        "AEG was also a major nuclear equipment supplier before its acquisition by Daimler-Benz."
    ),
    "KKN GmbH": (
        "Kernkraftwerk Niederaichbach GmbH operated the experimental Niederaichbach "
        "heavy-water-moderated, gas-cooled pressure tube reactor in Bavaria, Germany. "
        "The reactor operated only briefly (1972-1974) and was fully decommissioned by 1995 \u2014 "
        "the first German nuclear plant to complete decommissioning."
    ),
    "Connecticut Yankee Atomic Power Co": (
        "Connecticut Yankee Atomic Power Company operated the Haddam Neck nuclear plant in "
        "Connecticut from 1968 to 1996. The plant was one of the early Yankee consortium reactors "
        "and was fully decommissioned by 2007."
    ),
    "Maine Yankee Atomic Power Co": (
        "Maine Yankee Atomic Power Company operated the Maine Yankee nuclear plant from 1972 to "
        "1997. The plant was shut down after a cost analysis determined that the expense of "
        "required safety upgrades exceeded the value of continued operation."
    ),
    "Consumers Public Power District": (
        "Consumers Public Power District operated the Hallam Nuclear Power Facility in Nebraska, "
        "an experimental sodium-cooled graphite-moderated reactor that operated from 1962 to 1964 "
        "before being entombed in place."
    ),
}


def run():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    count = 0
    for name, desc in sorted(DESCRIPTIONS.items()):
        cur.execute(
            "SELECT id FROM entity_descriptions WHERE entity_type = 'owner' AND entity_name = ?",
            (name,)
        )
        if cur.fetchone():
            cur.execute(
                "UPDATE entity_descriptions SET description = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE entity_type = 'owner' AND entity_name = ?",
                (desc, name)
            )
            print(f"  Updated: {name}")
        else:
            cur.execute(
                "INSERT INTO entity_descriptions (entity_type, entity_name, description) "
                "VALUES ('owner', ?, ?)",
                (name, desc)
            )
            print(f"  Inserted: {name}")
        count += 1

    conn.commit()
    print(f"\nTotal: {count} owner descriptions added/updated")

    # Verify
    cur.execute("""
        SELECT DISTINCT r.owner FROM reactors r
        LEFT JOIN entity_descriptions ed ON ed.entity_type = 'owner' AND ed.entity_name = r.owner
        WHERE r.owner IS NOT NULL AND ed.id IS NULL
    """)
    remaining = cur.fetchall()
    print(f"Owners still without descriptions: {len(remaining)}")
    for r in remaining:
        print(f"  {r[0]}")

    conn.close()


if __name__ == "__main__":
    run()
