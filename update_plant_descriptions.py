#!/usr/bin/env python3
"""Replace template-generated plant descriptions with manually written ones.

Targets the most significant plants by capacity, historical importance,
and public interest. Each description covers the plant's role in nuclear
history, technical configuration context, and notable events.

Usage:
    python update_plant_descriptions.py              # Dry run
    python update_plant_descriptions.py --apply      # Apply to DB
"""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

DESCRIPTIONS = {
    # === CHINA ===
    "Hongyanhe": (
        "Hongyanhe is the largest operating nuclear power station in northeast China, "
        "located on the Liaodong Peninsula in Liaoning province. Its six units were built "
        "in two phases: units 1-4 are CPR-1000 reactors (commissioned 2013-2016) and "
        "units 5-6 are the improved ACPR-1000 design (commissioned 2021-2022). With over "
        "6 GW of capacity, it is one of the largest nuclear stations in the world. The "
        "site is operated by a joint venture between CGN and State Power Investment Corporation."
    ),
    "Yangjiang": (
        "Yangjiang is a six-unit nuclear station on the coast of Guangdong province in "
        "southern China, one of CGN's flagship sites. Units 1-4 are CPR-1000 reactors "
        "while units 5-6 are the improved ACPR-1000 design, making it a bridge between "
        "China's second and third generation PWR technology. Commissioned between 2014 and "
        "2019, the station's rapid construction demonstrated China's maturing nuclear "
        "supply chain. Yangjiang is part of the dense cluster of nuclear plants along the "
        "Pearl River Delta coast that also includes Daya Bay, Ling Ao, and Taishan."
    ),
    "Tianwan": (
        "Tianwan in Jiangsu province is the centerpiece of Sino-Russian nuclear cooperation, "
        "featuring a mix of Russian and Chinese reactor designs across eight units. Units 1-2 "
        "are VVER-1000 reactors supplied by Atomstroyexport, commissioned in 2007 — Russia's "
        "first nuclear export to China. Units 3-4 are an upgraded VVER-1000 variant (428M), "
        "while units 5-6 switched to China's indigenous CNP-600/CPR-1000 design. Units 7-8, "
        "currently under construction, use the Russian VVER-1200. This diversity makes Tianwan "
        "a unique showcase of both Russian export reactor evolution and China's domestic "
        "nuclear capabilities."
    ),
    "Ningde": (
        "Ningde is a CGN nuclear station in Fujian province on China's southeast coast. "
        "Its first four units are CPR-1000 reactors commissioned between 2013 and 2016, "
        "while two additional HPR1000 (Hualong One) units are under construction. The site "
        "was developed as part of China's rapid nuclear expansion along its eastern seaboard "
        "during the 2010s, providing baseload power to Fujian's growing industrial economy."
    ),
    "Shidaowan": (
        "Shidaowan in Shandong province is home to China's demonstration CAP1400 (Guohe One) "
        "reactor — one of the world's most powerful reactor designs at 1400 MW per unit. The "
        "CAP1400 is China's scaled-up derivative of the Westinghouse AP1000, developed with "
        "fully indigenous intellectual property. The site also hosts two HPR1000 units under "
        "construction. Nearby, the separate Shidao Bay HTR-PM — the world's first commercial "
        "high-temperature gas-cooled pebble-bed reactor — began operation in 2023, making the "
        "Shidaowan area a showcase for China's advanced reactor ambitions."
    ),
    "Fangchenggang": (
        "Fangchenggang is a four-unit nuclear station in Guangxi province, notable as one of "
        "the first sites to deploy China's indigenous HPR1000 (Hualong One) reactor. Units 1-2 "
        "are CPR-1000 reactors (commissioned 2016), while unit 3 — commissioned in 2024 — is "
        "among the first Hualong One units to enter service, alongside Fuqing-5/6. Unit 4 is "
        "expected to follow shortly. The station provides baseload power to western Guangdong "
        "and Guangxi."
    ),
    "Ling Ao": (
        "Ling Ao sits immediately adjacent to the Daya Bay nuclear station in Guangdong "
        "province, sharing the same coastal site near Shenzhen. Units 1-2 are Framatome "
        "M310 reactors (commissioned 2002-2003), essentially identical to the Daya Bay units "
        "and among the last French-designed reactors built in China before the transition to "
        "indigenous designs. Units 3-4 (sometimes called Ling Dong) are CPR-1000 reactors "
        "representing China's first fully localized PWR design, commissioned in 2010-2011. "
        "Together with Daya Bay, the site forms one of the world's largest nuclear complexes."
    ),
    "Haiyang": (
        "Haiyang in Shandong province is one of two demonstration sites for the Westinghouse "
        "AP1000 in China, alongside Sanmen. Units 1-2 were commissioned in 2018-2019 after "
        "significant construction delays shared across the global AP1000 program. Despite the "
        "difficult construction phase, both units have achieved strong operating performance. "
        "Two additional CAP1000 units — China's localized derivative of the AP1000 — are under "
        "construction at the site."
    ),
    "Sanmen": (
        "Sanmen in Zhejiang province is the world's first AP1000 nuclear power plant, with "
        "unit 1 achieving criticality in June 2018 — making it the lead unit for Westinghouse's "
        "Generation III+ passive safety design after years of delays. Unit 2 followed shortly "
        "after. The AP1000 uses passive safety systems that rely on natural forces like gravity "
        "and convection rather than active components, a major post-Chernobyl design philosophy. "
        "Two CAP1000 units are under construction to expand the site."
    ),

    # === JAPAN ===
    "Hamaoka": (
        "Hamaoka in Shizuoka prefecture is Japan's most controversial nuclear plant due to its "
        "location directly above the subduction zone where a major Tokai earthquake is anticipated. "
        "The site has five units spanning three BWR generations, with units 1-2 permanently shut "
        "down and units 3-5 suspended since 2011. In May 2011, Prime Minister Kan personally "
        "requested the shutdown of Hamaoka, the only plant singled out by name after Fukushima. "
        "Chubu Electric has since built a 22-meter sea wall and invested billions in safety "
        "upgrades, but restart remains politically contentious."
    ),
    "Ohi": (
        "Ohi (sometimes spelled Oi) on the coast of Fukui prefecture was the first nuclear plant "
        "to restart after Japan's post-Fukushima nationwide shutdown. Units 3-4, both 1,180 MW "
        "four-loop PWRs, were temporarily restarted in July 2012 to prevent summer power shortages "
        "in the Kansai region, before being shut down again pending new regulatory standards. They "
        "permanently restarted under NRA approval in 2018. Units 1-2, older Westinghouse designs, "
        "were permanently shut down in 2018 rather than undergo costly upgrades."
    ),
    "Fukushima-Daini": (
        "Fukushima Daini (Fukushima II) sits approximately 12 kilometers south of the destroyed "
        "Fukushima Daiichi plant. During the March 2011 tsunami, Daini also lost cooling systems "
        "on three of four units and came close to its own meltdown, but operators managed cold "
        "shutdown within days — a story largely overshadowed by the Daiichi disaster. All four "
        "BWR-5 units were permanently shut down in 2020. TEPCO announced decommissioning plans "
        "that will span decades, though the process is far simpler than the Daiichi cleanup."
    ),
    "Takahama": (
        "Takahama in Fukui prefecture is operated by Kansai Electric and features four PWR units "
        "spanning two generations. Units 3-4 (MHI three-loop, 870 MW each) restarted in 2016-2017, "
        "while unit 1 — commissioned in 1974 — became the oldest operating reactor in Japan when it "
        "restarted in 2023 under a 60-year life extension, making it a test case for Japan's revised "
        "policy on reactor lifespan beyond the original 40-year limit."
    ),
    "Mihama": (
        "Mihama in Fukui prefecture holds a special place in Japanese nuclear history as the site "
        "of Japan's first commercial PWR. Unit 1 (1970) and unit 2 (1972) were early Westinghouse "
        "two-loop designs and have been permanently shut down. Unit 3, a larger MHI three-loop "
        "reactor, was the site of a fatal steam pipe rupture in 2004 that killed five workers — "
        "the deadliest accident in Japanese nuclear history. After extensive safety upgrades, unit 3 "
        "restarted in 2021 under a life extension beyond 40 years."
    ),
    "Tokai": (
        "Tokai in Ibaraki prefecture is the birthplace of nuclear power in Japan. Tokai-1, a "
        "British-designed Magnox gas-cooled reactor, began operation in 1966 as Japan's first "
        "commercial nuclear plant and operated until 1998. Tokai-2, a GE BWR-5, has been "
        "suspended since the 2011 Fukushima disaster and faces local opposition to restart "
        "due to the difficulty of evacuating the surrounding densely populated area."
    ),
    "Genkai": (
        "Genkai in Saga prefecture on the island of Kyushu is Kyushu Electric's primary nuclear "
        "site. Units 1-2, early MHI two-loop PWRs, have been permanently shut down, while "
        "units 3-4 (four-loop, 1,180 MW each) restarted in 2018. Genkai-3 was notable as the "
        "first Japanese reactor to use MOX (mixed oxide plutonium-uranium) fuel in 2009, part "
        "of Japan's plutonium recycling program."
    ),
    "Sendai": (
        "Sendai (officially Satsumasendai) in Kagoshima prefecture made history on August 11, 2015, "
        "when unit 1 became the first reactor in Japan to restart under the post-Fukushima regulatory "
        "framework established by the Nuclear Regulation Authority (NRA). Unit 2 followed in October "
        "2015. Both are MHI three-loop PWRs operated by Kyushu Electric, and their restart was "
        "considered a bellwether for Japan's broader nuclear policy after the nationwide shutdown."
    ),

    # === SOUTH KOREA ===
    "Hanbit (Yonggwang)": (
        "Hanbit (formerly Yonggwang) on the southwest coast of South Korea is one of the country's "
        "largest nuclear stations with six operational units. Units 1-2 are Westinghouse two-loop "
        "PWRs commissioned in 1986-1987, while units 3-6 are Korean-designed OPR-1000 reactors "
        "that marked South Korea's transition from imported to indigenous nuclear technology. The "
        "station was renamed from Yonggwang to Hanbit in 2013 to avoid confusion with the nearby city."
    ),
    "Hanul (Ulchin)": (
        "Hanul (formerly Ulchin) on South Korea's east coast is a six-unit station operated by "
        "KHNP. Units 1-2 are French-designed CP1 reactors supplied by Framatome — the only French "
        "PWR exports to South Korea — while units 3-6 are Korean OPR-1000 designs. Renamed from "
        "Ulchin to Hanul in 2013, the site is adjacent to the Shin-Hanul station where newer "
        "APR1400 units are being deployed."
    ),
    "Shin-Hanul (Shin-Ulchin)": (
        "Shin-Hanul (formerly Shin-Ulchin) is a new nuclear station adjacent to the existing "
        "Hanul site on South Korea's east coast. Its two APR1400 units — South Korea's most "
        "advanced domestic reactor design — were commissioned in 2022-2024. The APR1400 is the "
        "same design exported to the UAE's Barakah plant, and Shin-Hanul represents the latest "
        "generation of South Korea's nuclear fleet."
    ),
    "Wolsong": (
        "Wolsong in Gyeongju is South Korea's only CANDU heavy-water reactor site, distinct from "
        "the country's predominantly PWR fleet. Unit 1, a Canadian-supplied CANDU 6 commissioned "
        "in 1983, was permanently shut down in 2019 amid controversy over whether the closure was "
        "politically motivated. Units 2-4 continue to operate. The plant is located near the "
        "historic city of Gyeongju, a UNESCO World Heritage area, which has added sensitivity "
        "to expansion proposals."
    ),

    # === FRANCE ===
    "Paluel": (
        "Paluel on the Normandy coast was the lead site for France's P4 series — the 1,300 MW "
        "class that followed the initial 900 MW CP0/CP1/CP2 standardized fleet. Its four units, "
        "commissioned in 1985-1986, were among the first to use Framatome's four-loop design that "
        "would be deployed across eight French sites. Paluel is one of EDF's largest nuclear "
        "stations and a significant contributor to Normandy's electricity exports."
    ),
    "Cattenom": (
        "Cattenom in the Moselle department near the Luxembourg border is one of France's most "
        "powerful nuclear stations with four 1,300 MW P4 units commissioned between 1987 and 1992. "
        "Its proximity to Luxembourg, Germany, and Belgium has made it a recurring focus of "
        "cross-border nuclear safety debates, with Luxembourg in particular repeatedly calling "
        "for its closure. Despite this, Cattenom remains a major source of electricity for "
        "northeast France."
    ),
    "Bugey": (
        "Bugey in the Ain department near Lyon is one of France's oldest nuclear sites. Unit 1, "
        "a UNGG (natural uranium graphite gas) reactor commissioned in 1972, represents France's "
        "indigenous first-generation reactor technology before the pivot to American-licensed PWRs. "
        "Units 2-5 are 900 MW CP0 pressurized water reactors commissioned in 1979-1980, among the "
        "first of France's standardized PWR fleet. The mix of reactor types at Bugey reflects the "
        "technological transition that defined France's nuclear program in the 1970s."
    ),
    "Tricastin": (
        "Tricastin in the Rhône Valley is notable not just for its four CP1 PWR units (commissioned "
        "1980-1981) but for the adjacent Georges Besse uranium enrichment plant — one of the largest "
        "in the world. The nuclear station was originally built in part to supply electricity to the "
        "energy-intensive gaseous diffusion enrichment process, which has since been replaced by more "
        "efficient centrifuge technology (Georges Besse II). The site remains a major hub of France's "
        "nuclear fuel cycle."
    ),
    "Chinon B": (
        "Chinon on the Loire River is a historic site in French nuclear history. The original Chinon A "
        "reactors (1963-1966) were UNGG gas-graphite designs and among France's first nuclear power "
        "plants — Chinon A1 is now a museum. The current Chinon B station comprises four CP2 PWR "
        "units (900 MW class) commissioned between 1984 and 1988. The site's location in the Loire "
        "Valley wine region has required careful management of thermal discharge into the river."
    ),

    # === RUSSIA ===
    "Rostov": (
        "Rostov (also known as Volgodonsk) in Rostov Oblast is one of Russia's newer nuclear stations, "
        "with four VVER-1000 units commissioned between 2001 and 2018. Construction of unit 1 began "
        "in 1981 but was delayed for nearly two decades by the Soviet collapse and economic turmoil "
        "of the 1990s. The station's completion across the 2000s and 2010s reflected the revival of "
        "Russia's domestic nuclear construction program under Rosatom."
    ),
    "Balakovo": (
        "Balakovo in Saratov Oblast on the Volga River is one of Russia's largest nuclear stations "
        "with four VVER-1000 units. Commissioned between 1986 and 1993, it was part of the major "
        "Soviet nuclear expansion program that continued even after Chernobyl. The station has "
        "consistently been one of Rosenergoatom's top performers, achieving high capacity factors "
        "and serving as a benchmark for VVER-1000 operations."
    ),
    "Kalinin": (
        "Kalinin (now in Tver Oblast) features four VVER-1000 units spanning three decades of "
        "construction — units 1-2 commissioned in 1985-1987, unit 3 in 2004, and unit 4 in 2012. "
        "This timeline reflects the interruption of Soviet nuclear construction during the economic "
        "upheaval of the 1990s and its subsequent restart. Unit 4 features the upgraded VVER-1000/338 "
        "design with enhanced safety systems."
    ),

    # === UKRAINE ===
    "Khmelnytskyi": (
        "Khmelnytskyi in western Ukraine is one of four nuclear stations operated by Energoatom. "
        "Units 1-2 are Soviet-era VVER-1000 reactors (commissioned 1988-2005, with unit 2's "
        "construction spanning the Soviet collapse). Units 3-4, under construction using the "
        "Russian-designed VVER-1200, became a focus of geopolitical tension after Russia's 2022 "
        "invasion — Ukraine announced plans to complete them with Westinghouse fuel and Western "
        "instrumentation rather than Russian components, an unprecedented technical adaptation."
    ),

    # === EUROPE (OTHER) ===
    "Kozloduy": (
        "Kozloduy on the Danube in northwest Bulgaria has been central to the country's nuclear "
        "politics for decades. Units 1-4, Soviet VVER-440/230 reactors without full containment "
        "structures, were shut down in 2002-2006 as a condition of Bulgaria's EU accession — a "
        "decision that remains controversial domestically. Units 5-6, larger VVER-1000 reactors "
        "with modern safety systems, continue to operate and provide roughly a third of Bulgaria's "
        "electricity. A new AP1000 unit is planned for the site."
    ),
    "Ringhals": (
        "Ringhals on Sweden's west coast is the largest nuclear station in Scandinavia. Its four "
        "units represent a unique mix: unit 1 is an ASEA-Atom BWR while units 2-4 are Westinghouse "
        "three-loop PWRs — the only PWRs in Sweden's otherwise all-BWR fleet. Units 1-2 were "
        "permanently shut down in 2019-2020 as part of Vattenfall's economic optimization, though "
        "political interest in reversing those closures has grown alongside Sweden's shift toward "
        "a more pro-nuclear energy policy."
    ),
    "Forsmark": (
        "Forsmark, located on the Baltic coast north of Stockholm, gained international attention "
        "on April 28, 1986, when radiation monitors at the plant detected elevated readings — the "
        "first alert outside the Soviet Union that something had gone wrong at Chernobyl. The "
        "station's three ASEA-Atom BWR units (commissioned 1980-1985) continue to operate and are "
        "among Sweden's most productive nuclear plants. The site also hosts Sweden's repository for "
        "short-lived radioactive waste (SFR) and has been selected for the country's deep geological "
        "repository for spent nuclear fuel."
    ),
    "Doel": (
        "Doel near Antwerp is one of Belgium's two nuclear stations and a focal point of the "
        "country's nuclear phase-out debate. Units 1-2 (Westinghouse two-loop) were shut down "
        "in 2022-2023, while units 3-4 continue to operate under a ten-year life extension "
        "negotiated in 2023 after Belgium reversed course on its planned complete nuclear exit. "
        "The station's location near Belgium's largest port and second-largest city has made "
        "evacuation planning a persistent concern in safety debates."
    ),
    "Tihange": (
        "Tihange on the Meuse River near Liège is Belgium's other nuclear station, operated by "
        "Electrabel (Engie). Unit 1, a French CP0-derived design, was permanently shut down in "
        "2022 as part of Belgium's partial phase-out. Units 2-3, larger Westinghouse three-loop "
        "PWRs, attracted international scrutiny when hydrogen-induced flaking was discovered in "
        "their reactor pressure vessels in 2012, leading to extended shutdowns and safety "
        "investigations. Both units received life extensions to continue operating through the 2030s."
    ),
    "Loviisa": (
        "Loviisa in southern Finland is unique as the only VVER reactor plant in a Western country "
        "operating under Western safety standards. Its two VVER-440/213 units, supplied by the "
        "Soviet Union and commissioned in 1977-1981, were extensively modified with Western "
        "instrumentation, containment upgrades, and safety systems by Finnish engineers — "
        "creating a hybrid design that became a model for VVER safety upgrades across Eastern "
        "Europe after the Cold War. Operated by Fortum, the units have achieved excellent "
        "operating performance."
    ),
    "Dukovany": (
        "Dukovany in the Vysočina Region is the Czech Republic's first nuclear station, with four "
        "VVER-440/213 units commissioned between 1985 and 1987. The station provides approximately "
        "20% of the country's electricity and has undergone extensive modernization to extend its "
        "operating life. A new large reactor unit is planned for the site, with Dukovany selected "
        "as the preferred location for the Czech Republic's nuclear expansion."
    ),
    "Mochovce": (
        "Mochovce in southern Slovakia features four VVER-440/213 units. Units 1-2 were "
        "commissioned in 1998-2000 after post-Soviet completion with Western safety upgrades. "
        "Units 3-4 became one of Europe's most protracted nuclear construction projects — begun "
        "in 1987, suspended after the Soviet collapse, restarted in 2009, and completed decades "
        "behind schedule. Unit 3 finally began commercial operation in 2023 after years of "
        "regulatory review and cost overruns. Mochovce helps Slovakia maintain one of the "
        "highest nuclear shares of electricity generation in the world."
    ),
    # French 900 MW sites
    "Blayais": (
        "Blayais on the Gironde estuary in southwest France features four CP1 PWR units "
        "(commissioned 1981-1983). The station experienced a significant flooding event during "
        "Storm Martin in December 1999, when the Gironde estuary surged and partially flooded "
        "the site, leading to a Level 2 INES incident. This event prompted major flood protection "
        "upgrades and influenced nuclear safety thinking about extreme weather events years before "
        "the Fukushima disaster raised similar concerns globally."
    ),
    "Dampierre": (
        "Dampierre on the Loire River in central France is a four-unit CP1 station commissioned "
        "in 1980-1981. As one of the earliest sites in France's standardized 900 MW PWR fleet, "
        "it was built during the massive nuclear expansion triggered by the 1973 oil crisis — the "
        "Messmer Plan that would make France the world's most nuclear-dependent major economy."
    ),
    "Cruas": (
        "Cruas in the Ardèche department of southern France is a four-unit CP2 station commissioned "
        "in 1984-1985. The site is notable for its distinctive cooling towers decorated with a large "
        "fresco by artist Jean-Marie Pierret, making it one of the most visually recognizable nuclear "
        "plants in France. The CP2 series introduced incremental improvements over the CP1 design "
        "in France's standardized 900 MW reactor fleet."
    ),
}


def run(apply=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    updated = 0
    not_found = 0
    for name, desc in sorted(DESCRIPTIONS.items()):
        cur.execute(
            "SELECT description FROM entity_descriptions "
            "WHERE entity_type = 'plant' AND entity_name = ?",
            (name,)
        )
        row = cur.fetchone()
        if not row:
            print(f"  SKIP {name}: not found in entity_descriptions")
            not_found += 1
            continue

        old_len = len(row[0])
        new_len = len(desc)
        if apply:
            cur.execute(
                "UPDATE entity_descriptions SET description = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE entity_type = 'plant' AND entity_name = ?",
                (desc, name)
            )
            print(f"  Updated {name}: {old_len} -> {new_len} chars")
        else:
            print(f"  Would update {name}: {old_len} -> {new_len} chars")
        updated += 1

    if apply:
        conn.commit()

    print(f"\n{'Updated' if apply else 'Would update'} {updated} plant descriptions")
    if not_found:
        print(f"Not found: {not_found}")
    conn.close()


if __name__ == "__main__":
    run("--apply" in sys.argv)
