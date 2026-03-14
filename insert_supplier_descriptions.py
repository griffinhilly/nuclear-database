#!/usr/bin/env python3
"""Insert supplier descriptions into entity_descriptions table."""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

SUPPLIER_DESCRIPTIONS = {
    "Westinghouse": (
        "Westinghouse Electric Company is the originator of the pressurized water reactor and the "
        "most influential nuclear reactor vendor in history. Founded by George Westinghouse, the "
        "company's nuclear division grew from the US Navy's submarine reactor program under Admiral "
        "Hyman Rickover. Westinghouse developed the 1-loop through 4-loop PWR series that became "
        "the global standard, with technology licensed to Framatome (France), Siemens (Germany), "
        "MHI (Japan), and KHNP (South Korea). Now a subsidiary of Cameco Corporation, Westinghouse "
        "continues to supply fuel, services, and the Generation III+ AP1000 reactor design."
    ),
    "Framatome": (
        "Framatome (formerly AREVA NP, originally Framatome S.A.) is France's nuclear reactor "
        "designer and fuel manufacturer, responsible for building France's entire standardized PWR "
        "fleet under EDF's nuclear program. Starting with a Westinghouse license, Framatome "
        "developed increasingly independent designs culminating in the 900 MW CP series, 1,300 MW "
        "P4 series, 1,450 MW N4, and the Generation III+ EPR. Framatome is now majority-owned by "
        "EDF and remains one of the world's leading nuclear engineering companies, providing "
        "reactor components, fuel assemblies, and instrumentation globally."
    ),
    "GE": (
        "General Electric developed the boiling water reactor (BWR) technology that became the "
        "second most widely deployed reactor type worldwide. GE's BWR lineage evolved through "
        "six generations (BWR/1 through BWR/6) from the 1950s to the 1980s. GE's nuclear division "
        "later partnered with Hitachi to form GE-Hitachi Nuclear Energy, which developed the ABWR "
        "and ESBWR advanced designs. GE-Hitachi now markets the BWRX-300 small modular reactor."
    ),
    "Rosatom": (
        "Rosatom State Atomic Energy Corporation is Russia's state nuclear enterprise and the "
        "world's leading nuclear technology exporter. Rosatom encompasses the entire nuclear fuel "
        "cycle: uranium mining, enrichment, fuel fabrication, reactor design and construction "
        "(through subsidiary ASE/Atomstroyexport), plant operation, and spent fuel management. "
        "Rosatom markets the VVER-1200 reactor internationally and has active construction "
        "projects in Bangladesh, Belarus, China, Egypt, Hungary, India, Iran, and Turkey."
    ),
    "CNNC": (
        "China National Nuclear Corporation (CNNC) is one of China's two major state-owned nuclear "
        "enterprises, responsible for the indigenous development of the CNP-300, CNP-600, and "
        "CNP-1000 reactor series. CNNC co-developed the Hualong One (HPR1000), China's flagship "
        "Generation III reactor, now being deployed domestically and exported. CNNC also manages "
        "China's nuclear fuel cycle, weapons program, and advanced reactor research."
    ),
    "AECL": (
        "Atomic Energy of Canada Limited (AECL) developed the CANDU pressurized heavy water "
        "reactor, one of the most distinctive reactor families in commercial nuclear power. AECL "
        "supplied CANDU reactors to Canada, India, South Korea, Romania, Argentina, Pakistan, and "
        "China. The commercial reactor division was sold to SNC-Lavalin (now AtkinsRéalis) as "
        "Candu Energy in 2011, while AECL continues to manage Canada's nuclear laboratories."
    ),
    "KEPCO": (
        "Korea Electric Power Corporation (KEPCO) is South Korea's national electric utility and "
        "the parent company of Korea Hydro & Nuclear Power (KHNP). Through its subsidiaries, KEPCO "
        "developed the OPR-1000 and APR1400 reactor designs, building South Korea's nuclear fleet "
        "and winning the landmark UAE Barakah export contract. KEPCO is now one of the world's "
        "most competitive nuclear vendors."
    ),
    "Mitsubishi": (
        "Mitsubishi Heavy Industries (MHI) is Japan's primary PWR manufacturer, building reactors "
        "under Westinghouse license for Japan's western-grid utilities. MHI developed the 2-loop, "
        "3-loop, and 4-loop PWR configurations adapted for Japanese conditions and is developing "
        "the APWR (Advanced PWR) for next-generation deployment. MHI also manufactures reactor "
        "components for international customers."
    ),
    "CE": (
        "Combustion Engineering (CE) was an American nuclear reactor vendor that developed a "
        "distinctive PWR lineage featuring 2×4 loop arrangements and large-diameter reactor "
        "vessels. CE supplied reactors to major US plants including Palo Verde, Millstone, and "
        "Calvert Cliffs. CE's System 80 design was the foundation for South Korea's nuclear "
        "program. CE was acquired by ABB in 1990 and later by Westinghouse."
    ),
    "Atomstroyexport": (
        "Atomstroyexport (ASE) is Rosatom's nuclear plant construction subsidiary, responsible "
        "for building VVER reactors both domestically and internationally. ASE has constructed "
        "VVER-1000 and VVER-1200 units in China (Tianwan), India (Kudankulam), Iran (Bushehr), "
        "Belarus (Ostrovets), and other countries. ASE is now integrated into Rosatom's engineering "
        "division."
    ),
    "KWU": (
        "Kraftwerk Union (KWU) was Siemens' nuclear power subsidiary, created in 1969 from the "
        "merger of Siemens and AEG nuclear activities. KWU developed distinctive PWR and BWR "
        "designs for Germany characterized by spherical containments, high engineering standards, "
        "and excellent operating performance. KWU also exported reactors to Brazil, Argentina, "
        "Spain, and the Netherlands. KWU merged with Framatome in 2001 to form AREVA NP."
    ),
    "Toshiba": (
        "Toshiba Corporation's nuclear division built boiling water reactors for the Japanese "
        "market under GE license, including units at Fukushima, Kashiwazaki-Kariwa, and other "
        "sites. Toshiba acquired Westinghouse Electric in 2006 but later divested the stake "
        "following severe financial losses from the AP1000 construction projects at Vogtle and "
        "V.C. Summer in the United States."
    ),
    "Hitachi": (
        "Hitachi Ltd.'s nuclear division manufactured BWRs for the Japanese market under GE "
        "license and partnered with GE to form GE-Hitachi Nuclear Energy in 2007. Hitachi-built "
        "BWRs operate at several Japanese sites. The GE-Hitachi partnership now markets the "
        "ABWR and BWRX-300 small modular reactor designs."
    ),
    "B&W": (
        "Babcock & Wilcox (B&W) was an American nuclear reactor vendor that developed a distinctive "
        "PWR design featuring once-through steam generators (OTSGs) and a lowered-loop primary "
        "circuit layout. B&W supplied reactors to Oconee, Three Mile Island, Crystal River, and "
        "Davis-Besse. B&W's nuclear division evolved into BWXT (BWX Technologies), which continues "
        "to manufacture naval reactors for the US Navy."
    ),
    "NPCIL": (
        "Nuclear Power Corporation of India Limited (NPCIL) is India's state-owned nuclear "
        "utility, responsible for designing, building, and operating all Indian nuclear power "
        "plants. NPCIL developed India's indigenous PHWR program (220 MW through 700 MW units) "
        "and operates foreign-supplied reactors at Tarapur (BWR) and Kudankulam (VVER)."
    ),
    "ABB": (
        "ABB (ASEA Brown Boveri) formed from the 1988 merger of Sweden's ASEA and Switzerland's "
        "Brown Boveri. ABB's nuclear division inherited ASEA-Atom's Swedish BWR technology and "
        "Combustion Engineering's PWR line (acquired 1990). ABB supplied BWRs to Finland "
        "(Olkiluoto 1-2) and Sweden (Forsmark, Oskarshamn). ABB exited the nuclear business in "
        "2000, with its reactor activities transferred to Westinghouse and BNFL."
    ),
    "Atomenergoexport": (
        "Atomenergoexport was the Soviet Union's nuclear technology export organization, "
        "responsible for constructing VVER reactors in Warsaw Pact countries and allied nations. "
        "It supplied VVER-440 units to Czechoslovakia, Hungary, Bulgaria, Finland, and East "
        "Germany. After the Soviet dissolution, its functions were absorbed into Atomstroyexport "
        "and eventually Rosatom."
    ),
    "Minsredmash": (
        "Minsredmash (Ministry of Medium Machine Building) was the Soviet ministry responsible "
        "for the entire Soviet nuclear complex, including both weapons and civilian power reactor "
        "construction. Minsredmash oversaw the construction of RBMK and early VVER reactors "
        "within the Soviet Union. After 1992, its functions were transferred to Minatom and "
        "eventually Rosatom."
    ),
    "Siemens": (
        "Siemens AG supplied nuclear reactors through its nuclear division before the creation of "
        "the KWU subsidiary. Early Siemens-supplied reactors include units built before the formal "
        "establishment of Kraftwerk Union. Siemens exited the nuclear new-build business entirely "
        "after the Framatome merger in 2001, though Siemens continues to supply conventional "
        "turbine-generator equipment to nuclear plants."
    ),
    "ACECOWEN": (
        "ACECOWEN (Actinides and Concepts for Energy Withdrawal) is a consortium designation "
        "associated with certain reactor construction projects. The consortium supplied equipment "
        "and engineering services for nuclear plant construction in partnership with larger vendors."
    ),
    "Areva": (
        "Areva S.A. was the French nuclear conglomerate formed from the merger of Framatome, "
        "Cogema, and Technicatome in 2001. Areva was responsible for the EPR reactor design and "
        "construction projects at Olkiluoto (Finland), Flamanville (France), and Taishan (China). "
        "Financial difficulties from EPR cost overruns led to Areva's restructuring in 2018, with "
        "the reactor division becoming Framatome (majority EDF-owned)."
    ),
    "ASEA-Atom": (
        "ASEA-Atom was Sweden's nuclear reactor division, developing the distinctive Swedish BWR "
        "lineage with internal recirculation pumps and prestressed concrete containments. ASEA-Atom "
        "built reactors for Sweden's Oskarshamn, Barsebäck, Forsmark, and Ringhals sites. The "
        "company became ABB-Atom after the 1988 ASEA-Brown Boveri merger."
    ),
    "FAEA": (
        "FAEA (Federal Atomic Energy Agency) was a Russian government agency that managed civilian "
        "nuclear activities during the transitional period between the Soviet-era Minsredmash and "
        "the establishment of Rosatom in 2007."
    ),
    "FramACEC": (
        "FramACEC was a Franco-Belgian consortium between Framatome and ACEC (Ateliers de "
        "Constructions Électriques de Charleroi) that supplied nuclear reactors to Belgium's "
        "nuclear power program. The consortium built PWR units at the Doel and Tihange sites."
    ),
    "SACM": (
        "SACM (Société Alsacienne de Constructions Mécaniques) was a French industrial company "
        "involved in the construction of France's early UNGG gas-cooled reactors. SACM supplied "
        "reactor components for the first-generation French nuclear program before the country's "
        "transition to PWR technology."
    ),
    "CNEA": (
        "CNEA (Comisión Nacional de Energía Atómica) is Argentina's National Atomic Energy "
        "Commission, responsible for nuclear research, development, and regulatory oversight. "
        "CNEA has managed the development of the CAREM small modular reactor and Argentina's "
        "nuclear fuel cycle capabilities."
    ),
    "ACLF": (
        "ACLF (Ateliers et Chantiers de la Loire et du Forez) was a French industrial company "
        "that participated in nuclear reactor construction during the early French nuclear program."
    ),
    "CGE": (
        "CGE (Canadian General Electric) was the Canadian subsidiary of General Electric that "
        "supplied BWR components and engineering for early Canadian nuclear projects, including "
        "the Douglas Point CANDU reactor's conventional island equipment."
    ),
    "ASPALDO": (
        "Aspaldo is an industrial supplier that provided equipment for an early Italian nuclear "
        "reactor project. Italy's brief nuclear power program in the 1960s-80s involved multiple "
        "international suppliers before the post-Chernobyl phase-out."
    ),
    "CNCLNEY": (
        "A consortium designation associated with the construction of a specific nuclear power "
        "plant unit, likely involving multiple French industrial partners."
    ),
    "Hitatchi-GE": (
        "Hitachi-GE Nuclear Energy is the joint venture between Hitachi and GE for nuclear "
        "reactor design and construction, primarily serving the Japanese market. The partnership "
        "markets the ABWR in Japan and the BWRX-300 small modular reactor internationally. "
        "(Note: alternate spelling of Hitachi-GE.)"
    ),
    "MAEC-Kaz": (
        "MAEC-Kaz (Mangistau Atomic Energy Complex - Kazakhstan) was the Soviet/Kazakh operator "
        "of the BN-350 fast breeder reactor at Aktau (formerly Shevchenko) on the Caspian Sea. "
        "MAEC managed the reactor's dual-purpose operation for electricity generation and seawater "
        "desalination until its shutdown in 1999."
    ),
    "Montreal Energy": (
        "Montreal Engineering Company was a Canadian engineering firm involved in the construction "
        "of CANDU reactor projects. The company provided project management and engineering "
        "services for CANDU exports."
    ),
}


def run(apply=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT name FROM suppliers ORDER BY name")
    db_suppliers = {row[0] for row in cur.fetchall()}

    described = set(SUPPLIER_DESCRIPTIONS.keys())
    missing = db_suppliers - described

    print(f"DB suppliers: {len(db_suppliers)}, Descriptions: {len(described)}")
    if missing:
        print(f"Missing: {sorted(missing)}")

    count = 0
    for name, desc in sorted(SUPPLIER_DESCRIPTIONS.items()):
        if name not in db_suppliers:
            continue
        if apply:
            cur.execute(
                "INSERT OR REPLACE INTO entity_descriptions (entity_type, entity_name, description, source) VALUES (?, ?, ?, ?)",
                ("supplier", name, desc, "Wikipedia, WNA — AI-reviewed")
            )
        count += 1
        if apply:
            print(f"  + {name}: {len(desc)} chars")

    if apply:
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM entity_descriptions WHERE entity_type = 'supplier'")
        print(f"\nSupplier descriptions: {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM entity_descriptions")
        print(f"Total descriptions: {cur.fetchone()[0]}")

    print(f"Processed {count} suppliers")
    conn.close()


if __name__ == "__main__":
    run("--apply" in sys.argv)
