#!/usr/bin/env python3
"""
Insert country descriptions into entity_descriptions table.
39 countries, each with 2-3 paragraph nuclear program histories.

Usage:
    python insert_country_descriptions.py          # Dry run
    python insert_country_descriptions.py --apply  # Insert into DB
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

COUNTRY_DESCRIPTIONS = {
    "Argentina": (
        "Argentina was the first country in Latin America to develop nuclear energy, commissioning "
        "its first power reactor, Atucha-1, in 1974. The country's nuclear program has been shaped "
        "by a commitment to heavy water reactor technology, primarily using pressurized heavy water "
        "reactors (PHWRs) of both German (Siemens/KWU) and Canadian (CANDU) origin. Argentina also "
        "developed indigenous fuel cycle capabilities, including uranium enrichment and heavy water "
        "production facilities.\n\n"
        "The program expanded with Embalse (a CANDU-6, 1984) and Atucha-2 (completed in 2014 after "
        "a long construction hiatus). Argentina's nuclear sector is managed by Nucleoeléctrica "
        "Argentina S.A. (NA-SA), with the National Atomic Energy Commission (CNEA) overseeing "
        "research and development. The country has pursued the development of the CAREM small "
        "modular reactor, an indigenous pressurized water reactor design currently under construction, "
        "which would make Argentina one of the first countries to deploy an SMR."
    ),
    "Armenia": (
        "Armenia operates a single nuclear power plant at Metsamor, located about 30 km west of "
        "Yerevan. The plant originally housed two VVER-440/V270 reactors built with Soviet-era "
        "technology. Unit 1 was permanently shut down in 1989 following the devastating Spitak "
        "earthquake, and Unit 2 was also shut down but restarted in 1995 due to severe energy "
        "shortages caused by the collapse of the Soviet Union and a blockade by neighboring countries.\n\n"
        "Nuclear power provides roughly one-third of Armenia's electricity, making it critical to "
        "the country's energy security. The continued operation of Metsamor-2, which lacks a full "
        "containment structure, has been a source of concern for the EU and neighboring Turkey and "
        "Georgia. Armenia has explored options for a replacement reactor, with Russian assistance "
        "for a new VVER unit discussed but not yet committed."
    ),
    "Bangladesh": (
        "Bangladesh entered the nuclear power sector with the Rooppur Nuclear Power Plant, the "
        "country's first nuclear facility, located on the bank of the Padma River in Ishwardi. "
        "The project, built with Russian technology and financing under an intergovernmental "
        "agreement signed in 2011, consists of two VVER-1200/V523 units — Russia's Generation III+ "
        "pressurized water reactor design.\n\n"
        "Construction began in 2017 (Unit 1) and 2018 (Unit 2), with commissioning expected in "
        "the mid-2020s. The plant represents a major infrastructure investment for Bangladesh, "
        "which faces growing electricity demand driven by rapid industrialization and population "
        "growth. Rosatom is providing the reactors under a build-own-operate model with fuel "
        "supply guarantees, making Bangladesh the latest in a series of countries adopting Russian "
        "nuclear technology as newcomers to nuclear power."
    ),
    "Belarus": (
        "Belarus became a nuclear power nation in 2020 with the commissioning of the Belarusian "
        "Nuclear Power Plant (Ostrovets) near the Lithuanian border. The plant features two "
        "VVER-1200/V491 reactors, Russia's Generation III+ design, built by Rosatom under an "
        "intergovernmental agreement. Unit 1 began commercial operation in 2021, and Unit 2 "
        "followed in 2023.\n\n"
        "The project has been controversial, particularly with neighboring Lithuania, which has "
        "raised safety concerns about the site's proximity to its capital Vilnius (approximately "
        "50 km away) and has refused to purchase electricity from the plant. Despite this, the "
        "plant provides a significant share of Belarus's electricity and reduces the country's "
        "near-total dependence on Russian natural gas imports. Belarus historically experienced "
        "severe contamination from the 1986 Chernobyl disaster, with large areas of southern "
        "Belarus heavily affected by fallout."
    ),
    "Belgium": (
        "Belgium has operated nuclear power plants since 1962, when the BR-3 experimental PWR "
        "at Mol achieved criticality — making it one of the earliest nuclear power countries in "
        "Europe. The country's commercial nuclear fleet was concentrated at two sites: Doel (near "
        "Antwerp) and Tihange (near Liège), with seven reactors built between 1975 and 1985, all "
        "pressurized water reactors designed by Framatome/Westinghouse.\n\n"
        "Belgium committed to a nuclear phase-out in 2003, originally targeting closure of all "
        "reactors by 2025. However, the 2022 energy crisis prompted a reversal: the government "
        "agreed to extend the operation of Doel-4 and Tihange-3 by ten years to 2035, while the "
        "remaining five commercial reactors were shut down between 2022 and 2025. At its peak, "
        "nuclear power provided over half of Belgium's electricity. The Belgian Nuclear Research "
        "Centre (SCK CEN) at Mol remains a globally significant nuclear research institution, "
        "hosting the MYRRHA accelerator-driven research reactor project."
    ),
    "Brazil": (
        "Brazil's nuclear power program is centered at the Angra dos Reis site in Rio de Janeiro "
        "state, where the country operates two pressurized water reactors: Angra-1 (Westinghouse, "
        "626 MW, operational since 1985) and Angra-2 (Siemens/KWU, 1,350 MW, operational since "
        "2001). A third unit, Angra-3, also a Siemens/KWU design, has been under construction "
        "with significant interruptions since 1984, with completion currently targeted for the "
        "late 2020s.\n\n"
        "Nuclear power provides a small but stable share of Brazil's electricity, complementing "
        "the country's hydropower-dominated grid. Brazil possesses the world's sixth-largest "
        "uranium reserves and operates all stages of the nuclear fuel cycle domestically, including "
        "uranium enrichment using indigenously developed centrifuge technology. The country also "
        "operates a nuclear-powered submarine program, making it one of few nations to have "
        "developed naval nuclear propulsion capabilities."
    ),
    "Bulgaria": (
        "Bulgaria has operated nuclear power since 1974, when the first unit at the Kozloduy "
        "Nuclear Power Plant on the Danube River was connected to the grid. The site eventually "
        "housed six reactors: four older VVER-440/V230 units and two newer VVER-1000/V320 units. "
        "The four VVER-440 units were closed between 2002 and 2006 as a condition of Bulgaria's "
        "accession to the European Union, which considered them non-upgradable to Western safety "
        "standards.\n\n"
        "The two remaining VVER-1000 units at Kozloduy continue to operate and provide roughly "
        "one-third of Bulgaria's electricity. Bulgaria has pursued construction of a new nuclear "
        "plant at Belene using VVER-1000 equipment originally ordered from Russia, though the "
        "project has been repeatedly started and stopped due to political and financing disputes. "
        "More recently, Bulgaria has evaluated deploying the equipment at Kozloduy as Units 7-8, "
        "potentially with Westinghouse AP1000 technology instead."
    ),
    "Canada": (
        "Canada developed an independent nuclear reactor technology — the CANDU (CANada Deuterium "
        "Uranium) pressurized heavy water reactor — which uses natural uranium fuel and heavy water "
        "as both moderator and coolant, eliminating the need for uranium enrichment. The first CANDU "
        "prototype, NPD, achieved criticality in 1962, and the design was commercialized with the "
        "Douglas Point and Pickering stations in the late 1960s and early 1970s. CANDU reactors "
        "have been exported to India, South Korea, Romania, Argentina, Pakistan, and China.\n\n"
        "Canada's nuclear fleet is concentrated in Ontario, where Ontario Power Generation (OPG) "
        "and Bruce Power operate 17 CANDU reactors at the Bruce, Darlington, and Pickering sites, "
        "providing roughly 60% of Ontario's electricity. Several reactors at Bruce and Darlington "
        "have undergone or are undergoing major refurbishment programs extending their operational "
        "lives. Atomic Energy of Canada Limited (AECL) developed the CANDU technology, with the "
        "commercial reactor business now owned by SNC-Lavalin (Candu Energy). Canada is also a "
        "major global uranium producer, with mines in Saskatchewan's Athabasca Basin region."
    ),
    "China": (
        "China has the world's most ambitious nuclear construction program, with more reactors "
        "under construction than any other country. The program began modestly with the Qinshan-1 "
        "CNP-300 prototype (1991) and the Daya Bay plant built with French technology (1994). "
        "After 2005, China launched a massive expansion, importing Westinghouse AP1000, Framatome "
        "EPR, and Russian VVER-1000 designs while simultaneously developing indigenous reactor "
        "technology. This effort produced the Hualong One (HPR1000), China's flagship Generation "
        "III pressurized water reactor, which achieved its first grid connection at Fuqing-5 in "
        "2021.\n\n"
        "China's nuclear fleet has grown to become the world's second-largest by installed capacity "
        "(after the United States) and the third-largest by number of reactors (after the US and "
        "France). The country typically approves 6-10 new reactor starts per year and aims for "
        "nuclear to play a significant role in its carbon neutrality targets. China is also "
        "pursuing advanced reactor designs including high-temperature gas-cooled reactors (the "
        "Shidaowan HTR-PM demonstration plant), fast breeder reactors (CEFR, CFR-600), and small "
        "modular reactors (ACP100/Linglong One). The China National Nuclear Corporation (CNNC) and "
        "China General Nuclear Power Group (CGN) are the primary operators."
    ),
    "Czech Republic": (
        "The Czech Republic operates six nuclear reactors at two sites: four VVER-440/V213 units "
        "at Dukovany (operational since 1985-1987) and two VVER-1000/V320 units at Temelín "
        "(operational since 2002-2003). Together, these provide roughly one-third of the country's "
        "electricity, making nuclear power a cornerstone of Czech energy policy.\n\n"
        "The Czech Republic has been planning to expand its nuclear capacity, with a new unit at "
        "Dukovany selected as the priority project. In 2024, the government selected South Korea's "
        "KHNP with its APR1000 design as the preferred bidder, marking a significant departure "
        "from the country's historical reliance on Russian reactor technology. The existing Dukovany "
        "units are undergoing life extension programs, and additional new builds at Temelín are "
        "under consideration. ČEZ, the majority state-owned utility, operates all Czech nuclear plants."
    ),
    "Egypt": (
        "Egypt's nuclear ambitions date back to the 1950s, but the country did not begin "
        "construction of its first nuclear power plant until 2022. The El Dabaa Nuclear Power "
        "Plant, located on the Mediterranean coast west of Alexandria, will house four "
        "VVER-1200/V529 reactors built by Russia's Rosatom under a 2017 intergovernmental "
        "agreement that includes Russian financing, fuel supply, and operational support.\n\n"
        "When completed, El Dabaa will be the first nuclear power plant in Africa outside of "
        "South Africa and will significantly diversify Egypt's electricity generation, which is "
        "currently dominated by natural gas. The project represents one of the largest "
        "infrastructure investments in Egypt's history. Egypt's Nuclear Power Plants Authority "
        "(NPPA) will operate the facility, with extensive technology transfer provisions included "
        "in the contract."
    ),
    "Finland": (
        "Finland has been a nuclear power nation since 1977, when the Loviisa-1 VVER-440 reactor "
        "— a Soviet-designed unit uniquely fitted with a Westinghouse-designed ice condenser "
        "containment — began operation. The country's nuclear fleet grew to four reactors across "
        "two sites: two VVER-440 units at Loviisa (operated by Fortum) and two BWR units at "
        "Olkiluoto (operated by TVO).\n\n"
        "Finland's most notable recent nuclear milestone was the completion of Olkiluoto-3, a "
        "1,600 MW EPR reactor that began commercial operation in 2023 after years of construction "
        "delays and cost overruns — it was the first EPR to operate in Europe. Olkiluoto-3 is now "
        "the most powerful reactor in Europe and single-handedly provides roughly 15% of Finland's "
        "electricity. Nuclear power supplies approximately 35-40% of Finland's electricity, making "
        "it one of the most nuclear-dependent countries per capita. Finland is also notable for "
        "being the first country to begin construction of a deep geological repository for spent "
        "nuclear fuel (Onkalo, at the Olkiluoto site), operated by Posiva."
    ),
    "France": (
        "France operates the largest nuclear fleet in Europe and the second-largest in the world, "
        "with nuclear power providing approximately 65-70% of the country's electricity — the "
        "highest nuclear share of any major economy. The French nuclear program was launched in "
        "earnest after the 1973 oil crisis under the 'Messmer Plan,' which committed to a rapid, "
        "standardized buildout of pressurized water reactors based on a Westinghouse license. "
        "Framatome (now part of EDF group) developed the technology into a series of increasingly "
        "powerful designs: the 900 MW CP0/CP1/CP2 series, the 1,300 MW P4/P'4 series, and the "
        "1,450 MW N4 series.\n\n"
        "Électricité de France (EDF) operates all French nuclear plants. The standardized fleet "
        "approach — building many nearly identical reactors — reduced costs and simplified "
        "maintenance and regulatory oversight. France reprocesses its spent fuel at the La Hague "
        "facility and fabricates MOX (mixed oxide) fuel, giving it one of the world's most "
        "complete nuclear fuel cycles. More recently, France has launched the EPR2 program, a "
        "simplified evolution of the EPR design, with plans for six to fourteen new reactors "
        "to replace aging units and expand capacity. The first EPR built in France, Flamanville-3, "
        "experienced major construction delays but reached criticality in 2024."
    ),
    "Germany": (
        "Germany was once one of the world's leading nuclear power nations, with a peak fleet of "
        "19 power reactors providing roughly 30% of the country's electricity. German reactor "
        "designs, particularly the Konvoi series built by Siemens/KWU, were regarded as among the "
        "most advanced in the world, featuring distinctive spherical double containments and "
        "high thermal efficiency.\n\n"
        "Following the 2011 Fukushima accident, Chancellor Angela Merkel's government reversed a "
        "previous decision to extend reactor lifetimes and accelerated a full nuclear phase-out. "
        "Eight older reactors were immediately shut down, and the remaining nine were scheduled for "
        "closure by 2022. The last three German reactors — Emsland, Isar-2, and Neckarwestheim-2 "
        "— received a brief extension through April 2023 due to the energy crisis triggered by "
        "the Russia-Ukraine conflict, but were then permanently shut down, ending over 60 years "
        "of German nuclear power generation. The decision remains politically divisive, with "
        "critics arguing it increased German dependence on fossil fuels and raised electricity "
        "prices, while supporters cite safety concerns and the availability of renewable alternatives."
    ),
    "Hungary": (
        "Hungary's nuclear power comes from the Paks Nuclear Power Plant, located on the Danube "
        "in central Hungary, which houses four VVER-440/V213 reactors that have been operational "
        "since the 1980s. These four units supply approximately half of Hungary's electricity, "
        "making Paks one of the most important energy facilities in the country.\n\n"
        "Hungary is expanding its nuclear capacity with the Paks II project, which will add two "
        "VVER-1200 reactors built by Russia's Rosatom under a 2014 intergovernmental agreement "
        "financed primarily by a Russian state loan. The project has faced delays and EU scrutiny "
        "over state aid and procurement rules, but construction is proceeding. The existing Paks "
        "units have undergone power uprates and received 20-year life extensions, allowing them "
        "to operate into the 2030s. MVM Paks Nuclear Power Plant Ltd., a state-owned company, "
        "operates the facility."
    ),
    "India": (
        "India has developed a largely indigenous nuclear power program shaped by its unique "
        "geopolitical position outside the Nuclear Non-Proliferation Treaty (NPT). Following its "
        "1974 nuclear test, India was excluded from international nuclear commerce for decades, "
        "which drove the development of domestic reactor technology based on the CANDU-derivative "
        "pressurized heavy water reactor (PHWR) design. India's first commercial reactor, Tarapur-1 "
        "(a US-supplied BWR), began operation in 1969, but the bulk of India's fleet consists of "
        "indigenously built PHWRs at sites across the country.\n\n"
        "The 2008 India-US Civil Nuclear Agreement ended India's nuclear isolation, enabling imports "
        "of foreign reactor technology. India is now building Russian VVER-1000 units at Kudankulam "
        "and has agreements for French EPRs at Jaitapur and American AP1000s at Kovvada, though "
        "these projects have progressed slowly. India's three-stage nuclear program envisions a "
        "long-term transition from PHWRs to fast breeder reactors (the PFBR at Kalpakkam) and "
        "eventually thorium-fueled reactors, leveraging India's vast thorium reserves. The Nuclear "
        "Power Corporation of India Limited (NPCIL) operates all commercial nuclear plants."
    ),
    "Iran": (
        "Iran's nuclear power program has been one of the most geopolitically significant in the "
        "world, intertwined with decades of international tensions over the country's uranium "
        "enrichment activities. The Bushehr Nuclear Power Plant, Iran's only nuclear power station, "
        "was originally started by the German firm Kraftwerk Union in 1975 under Shah Mohammad Reza "
        "Pahlavi's government. Construction was abandoned after the 1979 Islamic Revolution and "
        "damage during the Iran-Iraq War, before being completed by Russia's Rosatom.\n\n"
        "Bushehr Unit 1, a VVER-1000/V446 reactor, finally achieved criticality in 2011 and began "
        "commercial operation in 2013, making it the first nuclear power reactor in the Middle East. "
        "A second unit at Bushehr is currently under construction, also with Russian technology. "
        "Iran's broader nuclear activities — including uranium enrichment at Natanz and Fordow — "
        "have been the subject of the Joint Comprehensive Plan of Action (JCPOA) and ongoing "
        "International Atomic Energy Agency monitoring."
    ),
    "Italy": (
        "Italy was an early pioneer of nuclear power, with its first reactor (Latina, a British "
        "Magnox GCR design) achieving criticality in 1963. The country operated four nuclear power "
        "plants through the 1980s, including the Caorso BWR and the Trino Vercellese PWR. However, "
        "following the 1986 Chernobyl disaster, a 1987 national referendum led to the phase-out of "
        "all Italian nuclear power plants, with the last reactor (Caorso) shutting down in 1990.\n\n"
        "Italy has periodically reconsidered nuclear power — a 2008 government initiative to resume "
        "construction was overturned by another referendum in 2011, shortly after the Fukushima "
        "accident. As a result, Italy remains one of the few major industrialized nations without "
        "nuclear power, relying heavily on natural gas and importing significant amounts of "
        "electricity from France's nuclear fleet. Italian companies, particularly Ansaldo Nucleare "
        "(now part of the Ansaldo Energia group), remain active in nuclear engineering and "
        "decommissioning services internationally."
    ),
    "Japan": (
        "Japan built the world's third-largest nuclear fleet, with 54 operational reactors at its "
        "peak providing roughly 30% of the country's electricity. The program expanded rapidly from "
        "the 1970s through the 2000s, using primarily boiling water reactors from GE/Hitachi/Toshiba "
        "and pressurized water reactors from Mitsubishi/Westinghouse. Japan's nuclear infrastructure "
        "includes fuel fabrication, reprocessing (the Rokkasho facility), and advanced reactor R&D.\n\n"
        "The March 2011 Fukushima Daiichi accident — triggered by a magnitude 9.0 earthquake and "
        "subsequent tsunami — was the worst nuclear disaster since Chernobyl and fundamentally "
        "transformed Japan's nuclear sector. All reactors were shut down for safety reviews, and the "
        "Nuclear Regulation Authority (NRA) was established with stricter post-Fukushima safety "
        "standards. Reactor restarts have been slow: as of 2026, only about 15 of the 33 operable "
        "reactors have received NRA approval and returned to service, while many older units have "
        "been permanently decommissioned. Japan's energy policy now positions nuclear as an important "
        "part of its carbon-neutral 2050 strategy, alongside renewables."
    ),
    "Kazakhstan": (
        "Kazakhstan's sole experience with nuclear power generation came from the BN-350 fast "
        "breeder reactor at Aktau (formerly Shevchenko) on the Caspian Sea coast, which operated "
        "from 1973 to 1999. This Soviet-designed sodium-cooled fast reactor was unique in that it "
        "served a dual purpose: generating electricity and desalinating seawater for the city. "
        "The reactor was permanently shut down in 1999 and is currently undergoing decommissioning.\n\n"
        "Despite having no operating power reactors, Kazakhstan is the world's largest uranium "
        "producer, accounting for over 40% of global uranium output through its state-owned company "
        "Kazatomprom. The country has periodically discussed building new nuclear power plants, with "
        "a proposed site near Lake Balkhash and consideration of Russian, Chinese, South Korean, "
        "and French reactor designs."
    ),
    "Lithuania": (
        "Lithuania operated the Ignalina Nuclear Power Plant, which housed two RBMK-1500 reactors "
        "— the most powerful individual reactor units ever built and of the same fundamental design "
        "as the Chernobyl reactors. The plant provided the majority of Lithuania's electricity "
        "during its operation, at times exporting power to neighboring countries.\n\n"
        "Closure of Ignalina was a condition of Lithuania's accession to the European Union, which "
        "considered the RBMK design non-upgradable to EU safety standards. Unit 1 was shut down in "
        "2004 and Unit 2 in 2009. The closures significantly impacted Lithuania's energy "
        "independence, transforming it from a net electricity exporter to an importer. A proposal "
        "to build a replacement reactor (the Visaginas project) was rejected in a 2012 advisory "
        "referendum, leaving Lithuania without nuclear power. The Ignalina site is now undergoing "
        "one of the largest decommissioning projects in the world, with EU financial support."
    ),
    "Mexico": (
        "Mexico operates two nuclear reactors at the Laguna Verde Nuclear Power Plant on the Gulf "
        "of Mexico coast in Veracruz state. Both units are General Electric BWR-5 boiling water "
        "reactors with Mark II containments, commissioned in 1990 (Unit 1) and 1995 (Unit 2). The "
        "plant provides approximately 4-5% of Mexico's electricity.\n\n"
        "Laguna Verde is operated by the Comisión Federal de Electricidad (CFE), Mexico's state "
        "utility. The plant has operated with a generally good safety and performance record and "
        "has undergone power uprates to increase output. Mexico has periodically discussed expanding "
        "its nuclear capacity but has not committed to new construction. The country's energy policy "
        "has focused primarily on natural gas, oil, and more recently renewable energy sources."
    ),
    "Netherlands": (
        "The Netherlands has had a limited nuclear power program, with only two commercial reactors "
        "ever built. The Dodewaard BWR (55 MW) operated from 1969 to 1997 and has been "
        "decommissioned, while the Borssele PWR (485 MW), a Siemens/KWU design, has been "
        "operational since 1973 and is the country's sole remaining nuclear power plant.\n\n"
        "Nuclear power provides a small share of Dutch electricity (about 3%), with the country's "
        "generation dominated by natural gas and growing wind capacity. In 2021, the Dutch "
        "government signaled a policy shift toward new nuclear construction, announcing plans "
        "for two new large reactors to help meet climate targets. The Netherlands also hosts "
        "significant nuclear research and fuel cycle infrastructure, including the URENCO "
        "enrichment facility at Almelo, the Petten High Flux Reactor (a major medical isotope "
        "producer), and the NRG nuclear research center."
    ),
    "Pakistan": (
        "Pakistan's nuclear power program began with the Karachi Nuclear Power Plant (KANUPP), "
        "a Canadian-supplied CANDU-type PHWR that has been operational since 1972. Following "
        "Pakistan's nuclear weapons test in 1998 and exclusion from mainstream nuclear commerce, "
        "the country's civilian nuclear expansion has relied primarily on Chinese technology and "
        "financing.\n\n"
        "China has supplied multiple reactors to Pakistan: two CNP-300 units at Chashma (operational "
        "since 2000 and 2011), two ACP-1000/CNP-1000 units at Chashma (operational since 2016 and "
        "2017), and the Karachi-2 and Karachi-3 units featuring the Hualong One (HPR1000) design, "
        "making Pakistan the first export customer for China's flagship reactor. The Pakistan Atomic "
        "Energy Commission (PAEC) operates all nuclear plants. Nuclear power provides a small but "
        "growing share of Pakistan's electricity, and additional Chinese-supplied reactors are "
        "under discussion."
    ),
    "Romania": (
        "Romania operates two CANDU-6 pressurized heavy water reactors at the Cernavodă Nuclear "
        "Power Plant on the Danube River, with Unit 1 operational since 1996 and Unit 2 since 2007. "
        "The CANDU technology was selected during the Ceaușescu era as an alternative to Soviet "
        "reactor designs, giving Romania fuel independence since CANDUs use natural uranium.\n\n"
        "Nuclear power provides approximately 20% of Romania's electricity. Plans for Units 3 and 4 "
        "at Cernavodă have been discussed for decades; a 2020 agreement with the United States "
        "committed to completing these units with American financing and project management support. "
        "Romania's nuclear program is operated by Societatea Națională Nuclearelectrica (SNN), "
        "a majority state-owned company listed on the Bucharest Stock Exchange."
    ),
    "Russia": (
        "Russia (and the former Soviet Union) has been at the forefront of nuclear technology "
        "since the world's first nuclear power plant, the 5 MW Obninsk AM-1, began generating "
        "electricity in 1954. The Soviet Union developed several reactor lineages including the "
        "VVER (pressurized water reactor), RBMK (graphite-moderated boiling water reactor), and "
        "BN (sodium-cooled fast breeder reactor). Today, Russia operates a diverse fleet spanning "
        "VVER-440, VVER-1000, VVER-1200, RBMK-1000, BN-600, and BN-800 designs.\n\n"
        "Russia's state nuclear corporation, Rosatom, is the world's leading nuclear technology "
        "exporter, with reactor construction projects in Bangladesh, Belarus, China, Egypt, Hungary, "
        "India, Iran, Turkey, and several other countries. Domestically, Russia is replacing aging "
        "Soviet-era reactors with new VVER-1200 units and pursuing advanced technologies including "
        "the BREST-OD-300 lead-cooled fast reactor and floating nuclear power plants (the Akademik "
        "Lomonosov, deployed in Pevek in 2020). Russia also operates the world's only fleet of "
        "nuclear-powered icebreakers and maintains extensive nuclear fuel cycle facilities, "
        "including enrichment and reprocessing."
    ),
    "Slovakia": (
        "Slovakia has been a nuclear power nation since the 1970s, when the first Soviet-designed "
        "VVER-440 reactors at Jaslovské Bohunice began operation. The country's nuclear fleet "
        "has evolved significantly: the two older V230-type units at Bohunice were shut down in "
        "2006 and 2008 as a condition of EU accession (similar to Bulgaria's and Lithuania's "
        "closures), while two newer V213 units at the same site continue to operate.\n\n"
        "Two additional VVER-440/V213 units operate at the Mochovce site, and two more Mochovce "
        "units (3 and 4) have been under construction — Mochovce-3 was completed and connected "
        "to the grid in 2023 after decades of construction delays, making it the newest reactor in "
        "the EU. Nuclear power provides over 50% of Slovakia's electricity, one of the highest "
        "shares in the world. Slovenské Elektrárne, majority-owned by the Italian utility Enel, "
        "operates all Slovak nuclear plants."
    ),
    "Slovenia": (
        "Slovenia operates a single nuclear reactor — the Krško Nuclear Power Plant, a Westinghouse "
        "two-loop PWR located on the Sava River. The plant has been operational since 1983 and is "
        "jointly owned by Slovenia and Croatia under an intergovernmental agreement dating from the "
        "former Yugoslavia. Nuclear power provides approximately 35-40% of Slovenia's electricity.\n\n"
        "Krško has undergone significant safety upgrades, including post-Fukushima enhancements, "
        "and received a 20-year life extension to 2043. Slovenia has been exploring the construction "
        "of a second unit at the Krško site (JEK2), with the government approving the project in "
        "principle and evaluating reactor technology options."
    ),
    "South Africa": (
        "South Africa is the only country in Africa with operating nuclear power reactors. The "
        "Koeberg Nuclear Power Plant, located near Cape Town on the Atlantic coast, houses two "
        "Framatome-designed 900 MW PWR units that have been operational since 1984-1985. Nuclear "
        "power provides approximately 5% of South Africa's electricity, complementing the country's "
        "coal-dominated generation fleet.\n\n"
        "Koeberg is operated by Eskom, South Africa's state utility. The plant has undergone "
        "steam generator replacements and is pursuing a 20-year life extension. South Africa's "
        "nuclear history also includes a now-dismantled nuclear weapons program (the only country "
        "to have voluntarily denuclearized) and the Pebble Bed Modular Reactor (PBMR) project, "
        "an advanced high-temperature gas reactor that was cancelled in 2010 after significant "
        "investment. New nuclear capacity has been discussed but faces funding constraints."
    ),
    "South Korea": (
        "South Korea operates one of the world's most successful nuclear power programs, with a "
        "fleet of predominantly pressurized water reactors that provide roughly 30% of the country's "
        "electricity. The program began with Kori-1 (a Westinghouse PWR, 1978) and evolved through "
        "technology transfer into a fully indigenous design capability. The Korean Standard Nuclear "
        "Plant (KSNP/OPR-1000) and its successor, the APR1400, were developed domestically by Korea "
        "Hydro & Nuclear Power (KHNP) and the Korea Atomic Energy Research Institute (KAERI).\n\n"
        "The APR1400 has been a major export success: four units were built at Barakah in the UAE "
        "(South Korea's first nuclear export), and the design was selected for new builds in the "
        "Czech Republic. Domestically, South Korea continues to build new APR1400 units at the "
        "Shin-Hanul site. The country's nuclear policy has fluctuated between pro- and anti-nuclear "
        "administrations, but the current direction favors continued operation and new construction "
        "as part of carbon reduction goals. South Korea's nuclear industry is also advancing the "
        "APR+ and i-SMR designs for future deployment."
    ),
    "Spain": (
        "Spain operates seven nuclear reactors at five sites, providing approximately 20-22% of "
        "the country's electricity. The fleet includes both BWR and PWR designs from American "
        "vendors (GE, Westinghouse), commissioned between 1971 and 1988. Spain's nuclear program "
        "expanded rapidly in the 1970s and 1980s before a 1983 moratorium halted new construction "
        "and cancelled several planned reactors.\n\n"
        "Spain's current energy policy schedules the progressive closure of all nuclear plants "
        "between 2027 and 2035, as operating licenses expire and are not renewed. However, the "
        "phase-out timeline has been debated as Spain faces decarbonization targets and concerns "
        "about electricity price impacts. The country's nuclear fleet is operated by several "
        "utilities, including Iberdrola, Endesa, and Naturgy, often in joint-ownership arrangements. "
        "The José Cabrera (Zorita) and Santa María de Garoña plants have already been permanently "
        "shut down and are in various stages of decommissioning."
    ),
    "Sweden": (
        "Sweden developed a substantial nuclear power program beginning in the 1970s, ultimately "
        "operating 12 commercial reactors across four sites (Barsebäck, Forsmark, Oskarshamn, and "
        "Ringhals). At its peak, nuclear power provided approximately 50% of Sweden's electricity, "
        "with hydropower supplying most of the remainder — giving Sweden one of the lowest-carbon "
        "electricity grids in the world.\n\n"
        "A 1980 referendum called for phasing out nuclear power, and the two Barsebäck reactors "
        "were closed in 1999 and 2005. Additional older units at Oskarshamn and Ringhals were "
        "retired between 2015 and 2020 for economic rather than political reasons. However, Swedish "
        "nuclear policy has shifted: the current government has reversed the phase-out commitment "
        "and supports both life extensions for existing reactors and new construction. Six reactors "
        "remain in operation, providing roughly 30% of national electricity. Sweden is also "
        "developing a deep geological repository for spent fuel at Forsmark, with construction "
        "approved in 2022."
    ),
    "Switzerland": (
        "Switzerland operates four nuclear reactors at three sites: Beznau (two units, operational "
        "since 1969 and 1971 — among the oldest operating reactors in the world), Gösgen "
        "(operational since 1979), and Leibstadt (operational since 1984). Nuclear power provides "
        "roughly one-third of Switzerland's electricity, complementing the country's extensive "
        "hydropower resources.\n\n"
        "Following the 2011 Fukushima accident, Switzerland decided not to build new nuclear plants "
        "but allowed existing reactors to operate for their remaining technical lifetimes without "
        "a fixed shutdown date. The Mühleberg BWR was voluntarily shut down by its operator BKW in "
        "2019 for economic reasons. The remaining four reactors continue to operate under the Swiss "
        "Federal Nuclear Safety Inspectorate (ENSI) oversight, with no mandated closure dates, "
        "creating an open-ended phase-out that depends on the technical and economic viability of "
        "each plant."
    ),
    "Taiwan": (
        "Taiwan operated nuclear power plants from 1978 to 2025, with six reactors at three sites "
        "(Chinshan, Kuosheng, and Maanshan) providing up to 20% of the island's electricity at "
        "their peak. The reactors were a mix of GE BWR and Westinghouse PWR designs. Taiwan's "
        "nuclear program was managed by the state-owned Taiwan Power Company (Taipower).\n\n"
        "Taiwan committed to a nuclear phase-out under the Democratic Progressive Party (DPP) "
        "government, with all six commercial reactors progressively shut down as their 40-year "
        "licenses expired. A fourth nuclear plant (Lungmen) with two advanced BWR units was "
        "partially built but mothballed in 2014 after years of public opposition and safety "
        "debates. A 2018 referendum voted to abolish the legal deadline for the phase-out, but "
        "the government continued with the closure schedule. The nuclear phase-out has intensified "
        "concerns about Taiwan's electricity supply reliability and carbon emissions, given the "
        "island's heavy dependence on imported liquefied natural gas."
    ),
    "Turkey": (
        "Turkey is building its first nuclear power plant at Akkuyu on the Mediterranean coast, "
        "a project that will make Turkey one of the newest members of the nuclear power community. "
        "The Akkuyu plant features four VVER-1200 reactors being built by Russia's Rosatom under "
        "a build-own-operate (BOO) model — the first such arrangement in the nuclear industry, "
        "where Rosatom retains ownership while Turkey purchases the electricity.\n\n"
        "Turkey has sought nuclear power for decades, with various proposals dating back to the "
        "1970s that repeatedly failed to materialize. Beyond Akkuyu, Turkey has signed agreements "
        "for a second nuclear plant at Sinop (originally planned with a Franco-Japanese consortium "
        "but currently being reassessed) and has discussed a third plant with Chinese technology. "
        "The nuclear program is a key component of Turkey's strategy to reduce dependence on "
        "imported natural gas and diversify its rapidly growing electricity supply."
    ),
    "UAE": (
        "The United Arab Emirates became the first new nuclear power nation in the Arab world when "
        "the Barakah Nuclear Energy Plant began commercial operation in 2021. Located in the Al "
        "Dhafra region of Abu Dhabi, the plant houses four South Korean APR1400 pressurized water "
        "reactors built by the Korea Electric Power Corporation (KEPCO) consortium. All four units "
        "were completed and connected to the grid between 2020 and 2024.\n\n"
        "The UAE's nuclear program is notable for its rapid and systematic execution: the country "
        "established the Emirates Nuclear Energy Corporation (ENEC) in 2009, selected the Korean "
        "bid in 2009, began construction in 2012, and had all four units operational within about "
        "twelve years. The program followed IAEA guidelines for newcomer countries and established "
        "an independent nuclear regulator (FANR). At full capacity, Barakah provides approximately "
        "25% of Abu Dhabi's electricity and is a cornerstone of the UAE's strategy to diversify "
        "away from fossil fuels."
    ),
    "UK": (
        "The United Kingdom was a pioneer of nuclear power, opening the world's first commercial "
        "nuclear power station at Calder Hall in 1956. The UK's first-generation program built a "
        "fleet of Magnox gas-cooled reactors (26 units across 11 sites), followed by the "
        "second-generation Advanced Gas-Cooled Reactors (AGRs, 14 units across 6 sites). These "
        "indigenous gas-cooled reactor designs were unique to the UK and gave the country decades "
        "of nuclear generation, though the AGRs suffered from construction delays and cost overruns.\n\n"
        "The UK's nuclear landscape has shifted dramatically in the 21st century. All Magnox "
        "stations have been permanently shut down, and the AGR fleet is being progressively retired "
        "by EDF Energy, with the last stations closing by the mid-2020s. New nuclear construction "
        "is underway at Hinkley Point C, where two EPR reactors are being built by EDF — the first "
        "new nuclear construction in the UK in over two decades. A second EPR project at Sizewell C "
        "has received government backing. The UK also has one of the world's most active SMR "
        "programs, with Rolls-Royce SMR and other designs under regulatory review. The Sellafield "
        "site in Cumbria remains one of the world's largest and most complex nuclear facilities, "
        "housing fuel reprocessing and decommissioning operations."
    ),
    "USA": (
        "The United States operates the world's largest fleet of nuclear power reactors, with "
        "approximately 94 operating units providing about 18-20% of the nation's electricity and "
        "nearly half of its carbon-free generation. The US pioneered commercial nuclear power, with "
        "the Shippingport reactor (1957) and subsequent rapid expansion through the 1960s and 1970s. "
        "American reactor designs — Westinghouse's pressurized water reactor and GE's boiling water "
        "reactor — became the global standard, licensed and built in dozens of countries worldwide.\n\n"
        "The US nuclear industry experienced a long pause in new construction following the 1979 "
        "Three Mile Island accident and increased regulatory requirements, with no new reactor "
        "orders for over 30 years. This ended with the Vogtle Expansion project in Georgia, where "
        "two Westinghouse AP1000 units (the first new US reactors in a generation) began commercial "
        "operation in 2023-2024 after significant delays and cost overruns. The US nuclear landscape "
        "is now experiencing renewed interest driven by decarbonization goals, data center electricity "
        "demand, and bipartisan policy support. Several utilities are pursuing license renewals to "
        "80 years, the Palisades plant is being restarted from decommissioning (a first), and "
        "multiple SMR and advanced reactor designs are under NRC review."
    ),
    "Ukraine": (
        "Ukraine operates one of Europe's largest nuclear fleets, with 15 reactors at four nuclear "
        "power plant sites providing over half of the country's electricity — the second-highest "
        "nuclear share in Europe after France. All Ukrainian power reactors are Russian-designed "
        "VVER types: 13 VVER-1000 units and 2 VVER-440 units, operated by Energoatom, the "
        "state-owned nuclear utility.\n\n"
        "Ukraine is inextricably linked to nuclear history through the 1986 Chernobyl disaster, "
        "the worst nuclear accident in history, which occurred at the RBMK-equipped Chernobyl "
        "plant (now within the Exclusion Zone). The last Chernobyl unit was shut down in 2000, "
        "and a New Safe Confinement was completed over the destroyed Unit 4 in 2016. Since "
        "Russia's 2022 invasion, Ukraine's nuclear plants have faced unprecedented wartime risks, "
        "with the Zaporizhzhia plant (Europe's largest, with six VVER-1000 units) occupied by "
        "Russian forces and repeatedly caught in crossfire. Ukraine has been diversifying its "
        "nuclear fuel supply away from Russia, contracting with Westinghouse for fuel assemblies "
        "compatible with its VVER reactors."
    ),
}


def run(apply=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print(f"{'Inserting' if apply else 'Would insert'} {len(COUNTRY_DESCRIPTIONS)} country descriptions\n")

    for name, desc in COUNTRY_DESCRIPTIONS.items():
        if apply:
            cur.execute(
                "INSERT OR REPLACE INTO entity_descriptions (entity_type, entity_name, description, source) VALUES (?, ?, ?, ?)",
                ("country", name, desc, "Wikipedia, WNA, IAEA — AI-reviewed")
            )
        print(f"  {'+'if apply else '~'} {name} ({len(desc)} chars)")

    if apply:
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM entity_descriptions WHERE entity_type = 'country'")
        print(f"\nVerification: {cur.fetchone()[0]} country descriptions in DB")
        cur.execute("SELECT COUNT(*) FROM entity_descriptions")
        print(f"Total descriptions in DB: {cur.fetchone()[0]}")
    else:
        print("\n[DRY RUN] Use --apply to insert.")

    conn.close()


if __name__ == "__main__":
    run("--apply" in sys.argv)
