#!/usr/bin/env python3
"""
Insert plant-level descriptions into entity_descriptions table.
315 plants: ~50 hand-written for historically significant sites,
remainder auto-generated from DB data.

Usage:
    python insert_plant_descriptions.py          # Dry run
    python insert_plant_descriptions.py --apply  # Insert into DB
"""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

# ---------------------------------------------------------------------------
# Manual descriptions for historically significant plants
# ---------------------------------------------------------------------------
MANUAL_DESCRIPTIONS = {
    # === Landmarks / Firsts ===
    "Shippingport": (
        "Shippingport Atomic Power Station in Pennsylvania was the first full-scale commercial "
        "pressurized water reactor in the United States, achieving criticality in December 1957 and "
        "beginning commercial operation in May 1958. Built as a joint project between the U.S. Atomic "
        "Energy Commission and the Duquesne Light Company, it was designed by the Naval Reactors Branch "
        "under Admiral Hyman Rickover, adapting submarine reactor technology for civilian power. The "
        "plant operated through three core configurations over its lifetime, including a pioneering "
        "light-water breeder reactor core in its final years. Shippingport was permanently shut down in "
        "1982 and fully decommissioned by 1989, becoming a landmark demonstration that a commercial "
        "nuclear plant could be safely decommissioned."
    ),
    "Dresden": (
        "Dresden Nuclear Power Station in Illinois was the first privately financed nuclear power plant "
        "in the United States. Unit 1, a 210 MW boiling water reactor built by General Electric, began "
        "commercial operation in 1960 and operated until 1978. Units 2 and 3, both BWR-3 designs, "
        "followed in 1970 and 1971, bringing the site's total capacity to over 2,000 MW. The station "
        "played a significant role in demonstrating the commercial viability of nuclear power for private "
        "utilities and pioneered the BWR containment designs that would become industry standards."
    ),
    "Indian Point": (
        "Indian Point Energy Center, located on the Hudson River just 40 km north of New York City, was "
        "one of the most controversial nuclear plants in the United States due to its proximity to the "
        "nation's largest metropolitan area. The site housed three pressurized water reactors: Unit 1 "
        "(1962-1974), Unit 2 (1974-2020), and Unit 3 (1976-2021). Decades of public opposition centered "
        "on evacuation feasibility, spent fuel storage, and environmental impacts on the Hudson River "
        "ecosystem. Indian Point provided roughly 25% of New York City's electricity before its final "
        "closure in April 2021, making its shutdown one of the most significant nuclear retirements in "
        "U.S. history."
    ),

    # === Major Accidents / Incidents ===
    "Chernobyl": (
        "Chernobyl Nuclear Power Plant in northern Ukraine was the site of the worst nuclear disaster "
        "in history on April 26, 1986, when a flawed reactor design and operator error during a safety "
        "test caused a steam explosion and graphite fire in RBMK-1000 Unit 4. The accident released "
        "massive amounts of radioactive material across Europe, caused dozens of immediate deaths and "
        "thousands of long-term health effects, and led to the permanent evacuation of a 30 km Exclusion "
        "Zone. The remaining three units continued operating until 2000, when the last reactor was shut "
        "down under international pressure. A New Safe Confinement structure was completed over the "
        "destroyed Unit 4 in 2016 to contain radioactive debris for at least 100 years."
    ),
    "Three Mile Island": (
        "Three Mile Island in Pennsylvania was the site of the most serious accident in U.S. commercial "
        "nuclear power history when Unit 2 suffered a partial core meltdown on March 28, 1979. A "
        "combination of equipment failure, design deficiencies, and operator confusion led to a loss of "
        "coolant that damaged approximately half the reactor core. While the containment structure "
        "prevented significant radiation release, the accident profoundly changed U.S. nuclear "
        "regulation, operator training, and public perception of nuclear safety. Unit 1, undamaged by "
        "the accident, continued operating until 2019. The cleanup of Unit 2 took over a decade and cost "
        "approximately $1 billion."
    ),
    "Fukushima-Daiichi": (
        "Fukushima Daiichi Nuclear Power Plant on Japan's northeast coast was the site of the world's "
        "most severe nuclear accident since Chernobyl when the Tohoku earthquake and tsunami struck on "
        "March 11, 2011. The tsunami overwhelmed the plant's sea wall, knocked out backup diesel "
        "generators, and caused station blackout in Units 1-4, leading to three reactor core meltdowns, "
        "hydrogen explosions, and major radioactive contamination. Over 150,000 residents were evacuated "
        "from the surrounding area. The disaster triggered a global reassessment of nuclear safety, led "
        "Japan to shut down its entire reactor fleet for safety reviews, and prompted Germany's decision "
        "to phase out nuclear power. Decommissioning of the six-unit plant is expected to take 30-40 years."
    ),

    # === Largest / Most Powerful ===
    "Zaporizhzhia": (
        "Zaporizhzhia Nuclear Power Plant in southeastern Ukraine is the largest nuclear power station "
        "in Europe, with six VVER-1000 reactors producing a combined gross capacity of 6,000 MW. Built "
        "between 1980 and 1996, the plant typically generated roughly half of Ukraine's nuclear "
        "electricity and about one-fifth of the country's total power supply. In March 2022, Russian "
        "forces seized the plant during the invasion of Ukraine, making it the first operating nuclear "
        "power station to be occupied in a war zone. The situation drew intense international concern "
        "and repeated IAEA monitoring missions as shelling near the site raised fears of a radiological "
        "incident."
    ),
    "Kashiwazaki Kariwa": (
        "Kashiwazaki-Kariwa Nuclear Power Plant in Niigata Prefecture is the world's largest nuclear "
        "power station by total installed capacity, with seven reactors (five BWR-5 and two ABWR units) "
        "totaling 8,212 MW gross. Operated by TEPCO, the same utility that operated Fukushima Daiichi, "
        "the plant was shut down after the 2007 Chuetsu offshore earthquake damaged several units and "
        "raised concerns about seismic safety. All reactors have remained offline since 2012 following "
        "post-Fukushima safety reviews, making it one of the largest idle power assets in the world. "
        "Restart has been repeatedly delayed by regulatory requirements and local government consent."
    ),
    "Bruce": (
        "Bruce Nuclear Generating Station on the shore of Lake Huron in Ontario is the largest "
        "operating nuclear power plant in North America and one of the largest in the world, with eight "
        "CANDU pressurized heavy water reactors producing a combined gross capacity of 6,797 MW. Built "
        "in two phases (Bruce A, 1977-1979, and Bruce B, 1984-1987), the station is operated by Bruce "
        "Power under a long-term lease from Ontario Power Generation. Bruce A underwent a major "
        "refurbishment program that returned its four units to service after being laid up in the late "
        "1990s, and a life-extension program is underway to keep the station operating into the 2060s."
    ),
    "Gravelines": (
        "Gravelines Nuclear Power Station on the coast of northern France near Dunkirk is the largest "
        "nuclear power plant in Western Europe, with six 950 MW CP1-series pressurized water reactors "
        "producing a combined gross capacity of 5,706 MW. Built between 1975 and 1985, the plant is "
        "part of EDF's standardized French nuclear fleet and uses seawater cooling from the English "
        "Channel. Gravelines has been one of France's most productive nuclear sites, consistently "
        "generating a significant share of the country's electricity. Its six units are undergoing "
        "periodic safety reviews as part of France's program to extend reactor lifetimes beyond 40 years."
    ),
    "Palo Verde": (
        "Palo Verde Nuclear Generating Station in Arizona is the largest nuclear power plant in the "
        "Western Hemisphere and the only large-scale nuclear plant not situated adjacent to a body of "
        "water, using treated municipal wastewater from Phoenix for cooling. Its three Combustion "
        "Engineering System 80 pressurized water reactors, with a combined gross capacity of 4,242 MW, "
        "began commercial operation between 1986 and 1988. Palo Verde consistently ranks as one of the "
        "top electricity-producing plants in the United States, generating enough power for roughly "
        "four million people. The plant is jointly owned by several southwestern utilities and operated "
        "by Arizona Public Service."
    ),
    "Kori": (
        "Kori Nuclear Power Plant on the southeastern coast of South Korea was the site of the "
        "country's first commercial nuclear reactor, Kori Unit 1, a Westinghouse PWR that began "
        "operation in 1978. The site eventually housed four pressurized water reactors with a combined "
        "capacity of 3,367 MW. Kori Unit 1 was permanently shut down in 2017 after nearly 40 years of "
        "service, becoming the first commercial reactor decommissioned in South Korea. The Kori site "
        "is adjacent to the newer Shin-Kori complex, and together they form one of the world's largest "
        "concentrations of nuclear generating capacity."
    ),
    "Barakah": (
        "Barakah Nuclear Energy Plant in Abu Dhabi is the first nuclear power station in the Arab "
        "world, featuring four Korean-designed APR1400 pressurized water reactors with a combined gross "
        "capacity of 5,600 MW. Built by a consortium led by the Korea Electric Power Corporation "
        "(KEPCO), construction began in 2012 and the units were progressively commissioned between 2021 "
        "and 2024. Barakah represents the UAE's flagship effort to diversify its energy mix away from "
        "hydrocarbons and is the largest single nuclear new-build project completed in recent years. "
        "At full operation, the plant is expected to supply approximately 25% of the UAE's electricity."
    ),

    # === Politically Significant ===
    "Hinkley Point C": (
        "Hinkley Point C in Somerset is the first new nuclear power station to be built in the United "
        "Kingdom in over two decades, featuring two EPR (European Pressurized Reactor) units with a "
        "planned combined capacity of 3,440 MW. The project, developed by EDF Energy with Chinese "
        "investment from CGN, was approved in 2016 after years of negotiation over a guaranteed strike "
        "price for its electricity. Construction has experienced significant delays and cost overruns, "
        "with the project budget more than doubling from initial estimates. The Hinkley Point site has "
        "a long nuclear history, with the adjacent Hinkley Point A (Magnox, 1965-2000) and Hinkley "
        "Point B (AGR, 1976-2022) stations having operated for decades."
    ),
    "Vogtle": (
        "Vogtle Electric Generating Plant in Georgia is one of the most significant nuclear sites in "
        "the United States, home to both legacy and next-generation reactor technology. Units 1 and 2, "
        "Westinghouse 4-loop PWRs commissioned in 1987-1989, have been reliable baseload generators for "
        "decades. Units 3 and 4, AP1000 reactors that achieved commercial operation in 2023 and 2024 "
        "respectively, represent the first new nuclear reactors built in the United States in over 30 "
        "years. The AP1000 expansion became a cautionary tale for new nuclear construction, with costs "
        "escalating from $14 billion to over $35 billion and construction delays exceeding seven years."
    ),
    "Flamanville": (
        "Flamanville Nuclear Power Plant on the Normandy coast of France houses two operational 1,300 MW "
        "P4-series PWRs (commissioned 1986-1987) and the troubled Flamanville-3 EPR unit. The EPR, "
        "originally expected to begin operation in 2012 at a cost of 3.3 billion euros, became a symbol "
        "of the difficulties facing new nuclear construction in Europe, with its schedule slipping over "
        "a decade and costs escalating to more than 13 billion euros. Problems included welding defects "
        "in the reactor vessel lid, quality control issues in safety-critical components, and workforce "
        "skill shortages. The unit finally received its operating license in 2024."
    ),
    "Olkiluoto": (
        "Olkiluoto Nuclear Power Plant on Finland's west coast houses three reactors: two ABB-built BWR "
        "units (commissioned 1979 and 1982) and the Olkiluoto 3 EPR, which became the first European "
        "Pressurized Reactor to achieve commercial operation in April 2023. The EPR project, originally "
        "contracted in 2003 with a target completion of 2009, became notorious as the most delayed "
        "nuclear construction project in Western history, running 14 years behind schedule with costs "
        "roughly tripling. Construction problems included concrete quality issues, welding deficiencies, "
        "and the instrumentation and control system design. Despite its troubled construction, the 1,600 MW "
        "unit now provides roughly 15% of Finland's electricity."
    ),
    "Bushehr": (
        "Bushehr Nuclear Power Plant on Iran's Persian Gulf coast is one of the most geopolitically "
        "significant nuclear facilities in the world. Originally contracted to the German firm "
        "Kraftwerk Union in 1975 under the Shah, construction was abandoned after the 1979 Islamic "
        "Revolution and the plant was damaged during the Iran-Iraq War. Russia's Atomstroyexport "
        "eventually completed Unit 1 with a VVER-1000 reactor, which began commercial operation in "
        "2013 after decades of delays and international controversy over Iran's nuclear intentions. "
        "Unit 2, also a VVER design, is under construction. Bushehr has been central to diplomatic "
        "tensions surrounding Iran's nuclear program, though it operates under IAEA safeguards with "
        "Russian-supplied fuel."
    ),
    "Akkuyu": (
        "Akkuyu Nuclear Power Plant on Turkey's Mediterranean coast is the country's first nuclear "
        "power station, featuring four VVER-1200 reactors with a planned combined capacity of 4,780 MW. "
        "The project is built and will be operated by Rosatom under a build-own-operate (BOO) model, "
        "the first of its kind for a nuclear power plant, meaning Russia will own and operate the plant "
        "on Turkish soil. Construction began in 2018 under an intergovernmental agreement signed in "
        "2010. The project has attracted both domestic and international attention for its unique "
        "ownership structure and its location in a seismically active region."
    ),

    # === Notable for Other Reasons ===
    "Sellafield": (
        "Sellafield, originally known as Windscale, is one of the most historically significant nuclear "
        "sites in the world. Located in Cumbria, England, it housed the Calder Hall reactors -- the "
        "world's first commercial-scale nuclear power station, which began generating electricity to the "
        "national grid in 1956 using Magnox gas-cooled reactor technology. Beyond power generation, "
        "Sellafield became the United Kingdom's primary nuclear fuel reprocessing and waste management "
        "complex. The site was also the location of the 1957 Windscale fire, one of the worst nuclear "
        "accidents in British history. All five power-generating reactors (four Magnox and one AGR "
        "prototype) have been permanently shut down, but the broader Sellafield complex remains "
        "operational for decommissioning and waste processing."
    ),
    "Dounreay PFR": (
        "Dounreay Prototype Fast Reactor (PFR) in Caithness, Scotland, was a 250 MW sodium-cooled fast "
        "breeder reactor that operated from 1976 to 1994. It was the larger successor to the Dounreay "
        "Fast Reactor (DFR) on the same site and represented the United Kingdom's most ambitious effort "
        "to develop commercial fast breeder technology. The PFR demonstrated the feasibility of a fast "
        "reactor fuel cycle but was ultimately closed as the economics of breeder reactors became "
        "unfavorable with low uranium prices. The Dounreay site is now undergoing one of Europe's most "
        "complex nuclear decommissioning programs."
    ),
    "Dounreay DFR": (
        "Dounreay Fast Reactor (DFR) in Caithness, Scotland, was a pioneering experimental fast breeder "
        "reactor that operated from 1959 to 1977. Built on the remote north coast of Scotland, the "
        "15 MW sodium-potassium cooled reactor was one of the world's first fast reactors to generate "
        "electricity and served as a testbed for fast neutron reactor physics and liquid metal cooling "
        "technology. DFR's successful operation led to the construction of the larger Prototype Fast "
        "Reactor (PFR) at the same site. The facility is now being decommissioned as part of the "
        "broader Dounreay site cleanup."
    ),
    "Koeberg": (
        "Koeberg Nuclear Power Station near Cape Town is the only nuclear power plant on the African "
        "continent. Its two Framatome-designed CP1 pressurized water reactors, with a combined gross "
        "capacity of 1,940 MW, have been operational since 1984 and 1985 respectively. Koeberg provides "
        "a significant share of the Western Cape's electricity and has been critical to South Africa's "
        "energy security, particularly during the country's recurring power shortages. The plant has "
        "undergone steam generator replacements and life-extension work to continue operating beyond "
        "its original design life. It was the subject of a sabotage attempt before commissioning in 1982."
    ),
    "Armenian": (
        "Armenian Nuclear Power Plant (also known as Metsamor) near the city of Metsamor in western "
        "Armenia is one of the world's most controversial operating reactors. Its two VVER-440 units, "
        "built without full containment structures, began operation in 1977 and 1980. Both units were "
        "shut down after the devastating 1988 Spitak earthquake, but Unit 2 was restarted in 1995 "
        "due to severe energy shortages following the collapse of the Soviet Union and economic blockades "
        "by neighboring countries. The plant's continued operation in a seismically active region "
        "without Western-standard containment has drawn persistent concern from the European Union and "
        "neighboring Turkey."
    ),
    "Ignalina": (
        "Ignalina Nuclear Power Plant in northeastern Lithuania housed two RBMK-1500 reactors, the most "
        "powerful single-unit reactors ever built, each producing 1,300 MW net. The RBMK design, the "
        "same type involved in the Chernobyl disaster, made Ignalina's closure a condition of "
        "Lithuania's accession to the European Union. Unit 1 was shut down in 2004 and Unit 2 in 2009, "
        "despite nuclear power having provided approximately 70% of Lithuania's electricity. The closure "
        "represented a major energy security sacrifice for EU membership and the plant is now undergoing "
        "a lengthy decommissioning process."
    ),
    "Bilibino": (
        "Bilibino Nuclear Power Plant is one of the most remote nuclear power stations in the world, "
        "located in the Chukotka Autonomous Okrug in Russia's far northeast Arctic region. Its four "
        "small EGP-6 light water graphite reactors, with a combined capacity of just 48 MW, were built "
        "between 1974 and 1977 to provide electricity and district heating to the isolated gold-mining "
        "town of Bilibino. The plant operated for nearly 50 years in extreme Arctic conditions, with "
        "all four units permanently shut down by 2023 as the floating Akademik Lomonosov took over its "
        "role in the region."
    ),
    "Akademik Lomonosov": (
        "Akademik Lomonosov is the world's first floating nuclear power plant, a barge-mounted station "
        "housing two KLT-40S pressurized water reactors derived from Russian nuclear icebreaker "
        "technology. With a combined capacity of 76 MW, it was towed to the remote port of Pevek in "
        "Russia's Chukotka region and began commercial operation in May 2020, replacing the aging "
        "Bilibino plant and a local coal-fired station. The vessel demonstrates Russia's concept for "
        "deployable nuclear power to serve remote Arctic and coastal communities. It is operated by "
        "Rosenergoatom and represents a novel approach to nuclear power delivery that several countries "
        "have expressed interest in replicating."
    ),
    "Angra": (
        "Angra Nuclear Power Plant (Central Nuclear Almirante Alvaro Alberto) on the coast of Rio de "
        "Janeiro state is Brazil's only nuclear power station and the sole nuclear facility in Latin "
        "America with pressurized water reactor technology. Unit 1, a 640 MW Westinghouse PWR, has "
        "operated since 1985, while Unit 2, a 1,350 MW Siemens/KWU pre-Konvoi design, was completed "
        "in 2001 after a prolonged construction hiatus. Unit 3, also a pre-Konvoi design, is under "
        "construction after being suspended for years. The site reflects Brazil's complex nuclear "
        "history, including its indigenous enrichment program and its decision to pursue both German and "
        "American reactor technology."
    ),
    "Darlington": (
        "Darlington Nuclear Generating Station on the shore of Lake Ontario in Ontario is one of "
        "Canada's largest nuclear plants, with four CANDU 850 pressurized heavy water reactors "
        "producing a combined gross capacity of 3,736 MW. Commissioned between 1990 and 1993, the "
        "plant is operated by Ontario Power Generation and is currently undergoing a major mid-life "
        "refurbishment program to replace pressure tubes and other key components, extending the "
        "station's operating life to approximately 2055. Darlington has also been selected as the "
        "site for Canada's first small modular reactor, a GE Hitachi BWRX-300."
    ),
    "Pickering": (
        "Pickering Nuclear Generating Station, located just east of Toronto on the shore of Lake "
        "Ontario, is one of the world's largest nuclear plants by number of units, with eight CANDU "
        "pressurized heavy water reactors and a combined gross capacity of 4,328 MW. Units 1-4 (the "
        "Pickering A station, commissioned 1971-1973) were among the earliest CANDU commercial reactors, "
        "while Units 5-8 (Pickering B, 1983-1986) featured an improved design. Pickering A Units 2 and "
        "3 were laid up in 1997 and never restarted. The station's proximity to Canada's largest city "
        "has made its continued operation and eventual decommissioning subjects of public debate."
    ),
    "Daya Bay": (
        "Daya Bay Nuclear Power Plant in Guangdong province was China's first large-scale commercial "
        "nuclear power station using imported technology, with two Framatome-designed M310 pressurized "
        "water reactors that began operation in 1994. The project, a joint venture between China and "
        "Hong Kong interests, was built with French technical assistance and marked a turning point in "
        "China's nuclear development by establishing the foundation for subsequent domestic reactor "
        "programs. Most of Daya Bay's output is exported to Hong Kong under a long-term agreement. The "
        "plant's successful operation demonstrated China's ability to operate Western-designed reactors "
        "and paved the way for the adjacent Ling Ao station."
    ),
    "Qinshan 1": (
        "Qinshan Nuclear Power Plant Phase 1 in Zhejiang province holds the distinction of being "
        "China's first domestically designed and built nuclear reactor. The 310 MW CNP-300 pressurized "
        "water reactor achieved commercial operation in 1994, making it a milestone in China's nuclear "
        "self-reliance program. Although modest in capacity compared to later Chinese reactors, Qinshan "
        "1 proved that China could independently design, construct, and operate a nuclear power plant. "
        "The broader Qinshan site later expanded to include Phase 2 (CNP-600 units) and Phase 3 "
        "(CANDU-6 units), becoming one of China's most diverse nuclear complexes."
    ),
    "Taishan": (
        "Taishan Nuclear Power Plant in Guangdong province is home to the world's first two operational "
        "EPR (European Pressurized Reactor) units, beating the long-delayed Olkiluoto 3 and Flamanville "
        "3 projects to commissioning. Both 1,750 MW units began commercial operation in 2018, built by "
        "a joint venture between CGN and EDF. While Taishan benefited from more favorable construction "
        "conditions and labor costs than its European counterparts, Unit 1 experienced a fuel rod "
        "cladding issue in 2021 that required an extended shutdown. The plant demonstrated that the EPR "
        "design could be successfully built and operated, providing important lessons for the European "
        "EPR projects."
    ),
    "Fuqing": (
        "Fuqing Nuclear Power Plant in Fujian province is one of China's most significant nuclear "
        "sites, housing six reactors including the world's first Hualong One (HPR1000) unit. Units 1-4 "
        "are CNP-1000 pressurized water reactors commissioned between 2014 and 2017, while Units 5 and "
        "6 are the demonstration Hualong One units that achieved commercial operation in 2021 and 2022 "
        "respectively. The Hualong One is China's flagship indigenous Generation III reactor design, "
        "combining elements from prior Chinese and French PWR technology, and its successful operation "
        "at Fuqing has been central to China's nuclear export ambitions."
    ),
    "Kudankulam": (
        "Kudankulam Nuclear Power Plant on the southern tip of India's Tamil Nadu coast is India's "
        "first facility with Russian VVER pressurized water reactor technology. Units 1 and 2, VVER-1000 "
        "reactors built by Atomstroyexport, began commercial operation in 2014 and 2017 after years of "
        "construction delays and significant local protests over safety and environmental concerns. The "
        "site is planned for six units total, with Units 3-6 under construction, making it India's "
        "largest nuclear power station when completed. Kudankulam represents a cornerstone of "
        "Indo-Russian nuclear cooperation and India's broader program to expand nuclear capacity."
    ),
    "Tarapur": (
        "Tarapur Atomic Power Station in Maharashtra is India's oldest nuclear power plant, with its "
        "first two units (BWR boiling water reactors supplied by General Electric) achieving commercial "
        "operation in 1969. These 210 MW units were built under a bilateral agreement with the United "
        "States, but fuel supply was disrupted after India's 1974 nuclear test and the subsequent U.S. "
        "Nuclear Non-Proliferation Act. Units 3 and 4, Indian-designed 540 MW pressurized heavy water "
        "reactors, were added in 2006 and represent a significant step up in India's indigenous reactor "
        "capacity. Tarapur's history encapsulates India's complex relationship with the global nuclear "
        "non-proliferation regime."
    ),
    "Madras": (
        "Madras Atomic Power Station (MAPS) at Kalpakkam in Tamil Nadu was India's first domestically "
        "built nuclear power plant, with two 220 MW CANDU-derivative pressurized heavy water reactors "
        "that began operation in 1984 and 1986. The Kalpakkam site is also home to India's Prototype "
        "Fast Breeder Reactor (PFBR), a 500 MW sodium-cooled fast reactor that has been under "
        "construction since 2004 and represents India's ambition to close the nuclear fuel cycle using "
        "its abundant thorium reserves. The site serves as a critical hub for India's three-stage "
        "nuclear power program, which envisions a transition from natural uranium PHWRs through fast "
        "breeders to thorium-fueled reactors."
    ),
    "Rooppur": (
        "Rooppur Nuclear Power Plant on the bank of the Padma River in Ishwardi is Bangladesh's first "
        "nuclear power station, featuring two Russian-designed VVER-1200 (V-523) pressurized water "
        "reactors with a combined capacity of 2,400 MW. Built by Atomstroyexport under an "
        "intergovernmental agreement with Russia, construction began in 2017. The project represents a "
        "major infrastructure investment for Bangladesh, which faces rapidly growing electricity demand "
        "driven by industrialization. Rooppur makes Bangladesh the third South Asian country to operate "
        "nuclear power, after India and Pakistan."
    ),
    "El Dabaa": (
        "El Dabaa Nuclear Power Plant on Egypt's Mediterranean coast is the country's first nuclear "
        "power station, featuring four Russian-designed VVER-1200 reactors with a planned combined "
        "capacity of 4,800 MW. Construction began in 2022 under an intergovernmental agreement with "
        "Russia, fulfilling a decades-old Egyptian ambition to develop nuclear energy. The project is "
        "financed primarily through a Russian state loan. When completed, El Dabaa will make Egypt the "
        "second African nation with nuclear power after South Africa and is expected to provide a "
        "significant share of the country's baseload electricity."
    ),
    "Novovoronezh 1": (
        "Novovoronezh Nuclear Power Plant in Voronezh Oblast is the birthplace of the VVER reactor "
        "series, the Soviet-designed pressurized water reactor family that became one of the world's "
        "most widely deployed reactor types. Unit 1, a prototype VVER-210, began operation in 1964, "
        "followed by progressively larger and more refined designs through Unit 5 (VVER-1000). The "
        "station served as the development platform for each successive VVER generation, from the early "
        "V-120 and V-179 models through the standardized V-187 design. Units 1-4 have been permanently "
        "shut down, while Unit 5 continues to operate. The adjacent Novovoronezh-2 site hosts the "
        "latest VVER-1200 design."
    ),
    "Novovoronezh 2": (
        "Novovoronezh-2 Nuclear Power Plant is the reference site for Russia's latest-generation "
        "VVER-1200 (V-392M) pressurized water reactor, with two units that began commercial operation "
        "in 2017 and 2019. Located adjacent to the original Novovoronezh station, the plant serves as "
        "the domestic showcase for the AES-2006 design that Russia is actively exporting worldwide to "
        "countries including Egypt, Bangladesh, Turkey, and Hungary. The VVER-1200 incorporates passive "
        "safety systems and a core catcher, representing Russia's Generation III+ technology."
    ),
    "Beloyarsk": (
        "Beloyarsk Nuclear Power Plant in Sverdlovsk Oblast has been Russia's primary fast reactor "
        "development site since the 1960s. Units 1 and 2 were experimental graphite-moderated "
        "light-water-cooled reactors (AMB-100 and AMB-200) that operated from 1964 to 1989. Unit 3, "
        "a BN-600 sodium-cooled fast breeder reactor commissioned in 1981, was the world's largest "
        "operating fast reactor for decades. Unit 4, a BN-800 commissioned in 2016, is the world's "
        "most powerful fast neutron reactor and serves as a testbed for MOX fuel and closed fuel cycle "
        "technologies. Beloyarsk is central to Russia's long-term strategy of transitioning to a fast "
        "reactor fuel cycle."
    ),
    "Kursk 1": (
        "Kursk Nuclear Power Plant in Kursk Oblast houses four RBMK-1000 graphite-moderated light water "
        "reactors, the same design type involved in the Chernobyl disaster, with a combined gross "
        "capacity of 4,000 MW. Built between 1977 and 1986, the station has been one of Russia's major "
        "baseload electricity providers. Units 1 and 2 were permanently shut down in 2021 and 2024 "
        "respectively, while the remaining units continue operating with post-Chernobyl safety upgrades. "
        "The Kursk 1 plant is being progressively replaced by the adjacent Kursk-2 station, which "
        "features modern VVER-1200 reactors."
    ),
    "Kursk 2": (
        "Kursk-2 Nuclear Power Plant is a new-build replacement station being constructed adjacent to "
        "the original Kursk RBMK plant, featuring VVER-1200/V-491 pressurized water reactors. The "
        "project represents Russia's strategy of replacing its aging RBMK fleet with modern Generation "
        "III+ technology at existing nuclear sites. Two units are under construction, with the station "
        "planned to eventually match or exceed the capacity of the original Kursk plant. Kursk-2 is "
        "part of a broader program that includes similar replacement builds at the Leningrad and "
        "Smolensk RBMK sites."
    ),
    "Leningrad 1": (
        "Leningrad Nuclear Power Plant near Sosnovy Bor on the Gulf of Finland houses four RBMK-1000 "
        "reactors with a combined gross capacity of 4,000 MW. Unit 1, which began operation in 1974, "
        "was the first RBMK reactor to be built outside the Chernobyl prototype site. The station's "
        "older units are being progressively shut down and replaced by the adjacent Leningrad-2 plant. "
        "Units 1 and 2 have been permanently shut down, while Units 3 and 4 continue operating with "
        "post-Chernobyl safety modifications. The plant has been one of the major electricity suppliers "
        "for the St. Petersburg region."
    ),
    "Leningrad 2": (
        "Leningrad-2 Nuclear Power Plant is a modern replacement station being built adjacent to the "
        "original Leningrad RBMK plant, featuring VVER-1200 pressurized water reactors. Units 1 and 2 "
        "began commercial operation in 2018 and 2021, with additional units planned. The station uses "
        "the AES-2006 design, the same Generation III+ platform deployed at Novovoronezh-2 and being "
        "exported internationally. Leningrad-2 demonstrates Russia's commitment to replacing its RBMK "
        "fleet with modern pressurized water reactors while maintaining nuclear generating capacity in "
        "the northwestern region."
    ),
    "Belarusian": (
        "Belarusian Nuclear Power Plant (Ostrovets) near the Lithuanian border is Belarus's first "
        "nuclear power station, featuring two Russian-designed VVER-1200/V-491 pressurized water "
        "reactors with a combined capacity of 2,388 MW. Built by Atomstroyexport, Units 1 and 2 began "
        "commercial operation in 2021 and 2023 respectively. The plant has been controversial since its "
        "inception, drawing strong opposition from neighboring Lithuania, which raised concerns about "
        "the site's proximity to Vilnius (only 50 km away) and questioned the adequacy of safety "
        "assessments. The project was built under a Russian state credit and has made nuclear power a "
        "major component of Belarus's electricity supply."
    ),
    "Paks": (
        "Paks Nuclear Power Plant in central Hungary is the country's sole nuclear power station, "
        "providing roughly half of Hungary's electricity from four VVER-440/V-213 pressurized water "
        "reactors commissioned between 1983 and 1987. The plant has been one of the most reliable "
        "VVER-440 installations in the world, consistently achieving high capacity factors. Hungary "
        "has approved the construction of two new VVER-1200 units (Paks II) at the site under a "
        "controversial intergovernmental agreement with Russia, which has drawn scrutiny from the "
        "European Union over procurement and state aid concerns. The existing units have received "
        "life extensions to operate beyond their original 30-year design life."
    ),
    "Cernavodă": (
        "Cernavodă Nuclear Power Plant is Romania's only nuclear power station and the only CANDU "
        "pressurized heavy water reactor plant in Europe. Unit 1 began operation in 1996 and Unit 2 in "
        "2007, together providing roughly 20% of Romania's electricity. The plant was originally planned "
        "for five units under a Canadian-Romanian agreement signed in the 1970s, but only two were "
        "completed due to funding difficulties following the fall of the Ceaușescu regime. Romania has "
        "explored completing Units 3 and 4 with various international partners, and the CANDU design's "
        "ability to use natural uranium fuel has been a strategic advantage for the country."
    ),
    "Krško": (
        "Krško Nuclear Power Plant in southeastern Slovenia is unique in being jointly owned and "
        "operated by two countries, Slovenia and Croatia, under an agreement that predates both nations' "
        "independence from Yugoslavia. The single Westinghouse 2-loop pressurized water reactor, with a "
        "gross capacity of 727 MW, began commercial operation in 1983 and provides roughly 20% of "
        "Slovenia's and 15% of Croatia's electricity. The plant's continued operation and potential "
        "replacement have been subjects of bilateral negotiation, and Slovenia has explored building a "
        "second unit at the site."
    ),
    "Fessenheim": (
        "Fessenheim Nuclear Power Plant in Alsace was France's oldest operating nuclear power station "
        "before its closure, with two 920 MW CP0-series pressurized water reactors that had operated "
        "since 1977 and 1978. The plant became a symbol of the French nuclear phase-down debate and "
        "faced decades of opposition from both French and German environmental groups due to its "
        "location near the Rhine, the German border, and a seismic zone. Its closure in 2020, a "
        "campaign promise of President Hollande later carried out under President Macron, was the first "
        "permanent shutdown of a French nuclear power plant driven by political rather than technical "
        "reasons."
    ),
    "Wylfa": (
        "Wylfa Nuclear Power Station on the island of Anglesey in Wales housed the last two Magnox "
        "gas-cooled reactors to operate in the United Kingdom, with a combined gross capacity of "
        "1,070 MW. The Magnox reactors, which began operation in 1971, were the final representatives "
        "of the UK's first-generation nuclear technology and operated for over four decades. The final "
        "reactor was shut down in 2015, marking the end of the Magnox era in British nuclear history. "
        "The Wylfa site was proposed for a new Hitachi ABWR plant (Wylfa Newydd), but that project was "
        "cancelled in 2020 after the developer withdrew."
    ),
    "Sizewell B": (
        "Sizewell B in Suffolk is the United Kingdom's only operating pressurized water reactor, a "
        "1,250 MW unit based on the Westinghouse SNUPPS design that began commercial operation in 1995. "
        "It was the last nuclear power station completed in the UK before the decades-long hiatus in new "
        "nuclear construction that is only now being broken by Hinkley Point C. The plant represented a "
        "deliberate British shift from gas-cooled reactor technology to the PWR standard dominant "
        "worldwide. The adjacent Sizewell site has been approved for Sizewell C, a two-unit EPR station "
        "that would replicate the Hinkley Point C design."
    ),
    "Sizewell A": (
        "Sizewell A Nuclear Power Station in Suffolk housed two Magnox gas-cooled reactors that "
        "operated from 1966 until 2006, when they became the last Magnox reactors to close on the "
        "English east coast. The 490 MW station was part of the UK's first-generation nuclear program "
        "and operated alongside the later Sizewell B PWR on the same coastal site. The plant is now "
        "being decommissioned by the Nuclear Decommissioning Authority."
    ),
    "San Onofre": (
        "San Onofre Nuclear Generating Station on the southern California coast between Los Angeles and "
        "San Diego housed three pressurized water reactors. Unit 1 (Westinghouse, 1968-1992) was one of "
        "the earliest large commercial PWRs in the western United States. Units 2 and 3 (Combustion "
        "Engineering, 1983-1984) were prematurely retired in 2013 after replacement steam generators "
        "manufactured by Mitsubishi Heavy Industries developed unexpected tube degradation, leading to "
        "a radioactive leak. The premature closure became a major case study in nuclear component "
        "manufacturing quality and led to lengthy regulatory and legal proceedings."
    ),
    "Diablo Canyon": (
        "Diablo Canyon Power Plant on California's central coast is the state's last operating nuclear "
        "power station, with two Westinghouse 4-loop pressurized water reactors producing a combined "
        "2,394 MW. The plant has been at the center of decades of seismic safety debate, particularly "
        "after the discovery of the nearby Hosgri fault during construction and the Shoreline fault "
        "in 2008. Originally slated for closure by 2025 under state policy, the decision was reversed "
        "in 2022-2023 as California faced electricity reliability concerns, and the plant received a "
        "federal license extension to continue operating. Diablo Canyon provides roughly 9% of "
        "California's electricity."
    ),
    "Browns Ferry": (
        "Browns Ferry Nuclear Plant in Alabama is one of the largest nuclear stations in the United "
        "States, with three General Electric BWR-4 boiling water reactors producing a combined gross "
        "capacity of 3,465 MW. The plant is notable for the March 22, 1975 fire, caused by a worker "
        "using a candle to check for air leaks in cable penetrations, which disabled critical safety "
        "systems in Units 1 and 2. The fire led to major changes in U.S. nuclear fire protection "
        "regulations and cable separation requirements. Unit 1 was shut down for over 20 years for "
        "repairs and upgrades before returning to service in 2007. The plant is operated by the "
        "Tennessee Valley Authority."
    ),
    "Watts Bar": (
        "Watts Bar Nuclear Plant in Tennessee is notable for housing the last nuclear reactor to achieve "
        "commercial operation in the United States in the 20th century (Unit 1, 1996) and the first new "
        "U.S. reactor of the 21st century (Unit 2, 2016). The two Westinghouse 4-loop ice condenser "
        "PWRs, with a combined gross capacity of 2,428 MW, are operated by the Tennessee Valley "
        "Authority. Unit 2's construction was suspended in 1985 and not resumed until 2007, making its "
        "total construction period one of the longest in U.S. nuclear history. Together, the two units "
        "span the gap in American nuclear construction that lasted over three decades."
    ),

    # === Hinkley Point A & B (part of HPC narrative but distinct entries) ===
    "Hinkley Point A": (
        "Hinkley Point A Nuclear Power Station in Somerset was one of the United Kingdom's first-"
        "generation Magnox gas-cooled reactor stations, with two reactors that began commercial "
        "operation in 1965. The 534 MW station was part of the UK's post-war nuclear program and "
        "operated for over 30 years before closing in 2000. The Hinkley Point site has housed three "
        "generations of nuclear technology, with Hinkley Point B (AGR) and Hinkley Point C (EPR) "
        "following on adjacent land."
    ),
    "Hinkley Point B": (
        "Hinkley Point B Nuclear Power Station in Somerset was an Advanced Gas-cooled Reactor (AGR) "
        "station with two units that operated from 1976 until 2022. With a combined gross capacity of "
        "1,310 MW, the station was one of the UK's most reliable AGR plants and generated electricity "
        "for over 45 years. Its closure in 2022 was part of the planned retirement of the UK's AGR "
        "fleet, with the adjacent Hinkley Point C EPR project under construction as its successor."
    ),

    # === Additional manually requested plants ===
    "Shin-Kori": (
        "Shin-Kori Nuclear Power Plant on South Korea's southeastern coast is one of the country's "
        "newest and most powerful nuclear stations, housing a mix of OPR1000 and APR1400 reactors. "
        "Units 1 and 2 are OPR1000 designs commissioned in 2011 and 2012, while Units 3 and 4 are "
        "APR1400 reactors — the same Korean Generation III design exported to the UAE's Barakah plant. "
        "The site is adjacent to the original Kori station, and together they represent the evolution of "
        "South Korea's nuclear technology from imported Westinghouse designs to fully indigenous systems."
    ),
}


# ---------------------------------------------------------------------------
# Template generation from DB data
# ---------------------------------------------------------------------------
def _build_template(plant_name, country, tech_name, models, unit_count,
                    statuses, first_commercial, total_capacity):
    """Build a template description paragraph from aggregated DB data."""
    parts = []

    # Opening sentence
    unit_word = "unit" if unit_count == 1 else "units"
    # Strip trailing " Reactor" from tech_name to avoid "Reactor reactor unit"
    tech_label = tech_name
    if tech_label and tech_label.endswith(" Reactor"):
        tech_label = tech_label[:-len(" Reactor")]
    if models and models != "None":
        # Clean up model list for readability
        model_list = [m.strip() for m in models.split(",")]
        if len(model_list) == 1:
            model_info = f" ({model_list[0]})"
        elif len(model_list) == 2:
            model_info = f" ({model_list[0]} and {model_list[1]})"
        else:
            joined = ", ".join(model_list[:-1]) + ", and " + model_list[-1]
            model_info = f" ({joined})"
        parts.append(
            f"{plant_name} is a nuclear power station in {country} featuring "
            f"{unit_count} {tech_label} reactor {unit_word}{model_info} "
            f"with a combined capacity of {int(total_capacity):,} MW."
        )
    else:
        parts.append(
            f"{plant_name} is a nuclear power station in {country} featuring "
            f"{unit_count} {tech_label} reactor {unit_word} "
            f"with a combined capacity of {int(total_capacity):,} MW."
        )

    # Commercial operation date
    if first_commercial:
        year = first_commercial[:4]
        if unit_count == 1:
            parts.append(f"The reactor achieved commercial operation in {year}.")
        else:
            parts.append(f"The first unit achieved commercial operation in {year}.")

    # Status info
    status_list = [s.strip() for s in statuses.split(",")]
    if len(status_list) == 1:
        status = status_list[0]
        if status == "Permanent Shutdown":
            parts.append("All units have been permanently shut down.")
        elif status == "Under Construction":
            parts.append(
                "All units are currently under construction."
                if unit_count > 1
                else "The unit is currently under construction."
            )
        elif status == "Suspended":
            parts.append(
                "Operations are currently suspended."
                if unit_count > 1
                else "The reactor is currently suspended from operation."
            )
        # Operational — no extra note needed
    else:
        if "Under Construction" in status_list and "Operational" in status_list:
            parts.append("The site includes both operational units and units under construction.")
        elif "Permanent Shutdown" in status_list and "Operational" in status_list:
            parts.append("The site includes both operational and permanently shut down units.")
        elif "Permanent Shutdown" in status_list and "Under Construction" in status_list:
            parts.append("Older units have been permanently shut down while new units are under construction.")

    return " ".join(parts)


def run(apply=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Query aggregated data for all plants
    cur.execute("""
        SELECT r.plant_name, c.name AS country, t.name AS tech_name,
               GROUP_CONCAT(DISTINCT m.name) AS models,
               COUNT(*) AS unit_count,
               GROUP_CONCAT(DISTINCT r.status) AS statuses,
               MIN(r.commercial_operation) AS first_commercial,
               SUM(r.gross_capacity_mw) AS total_capacity
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        LEFT JOIN technologies t ON r.technology_id = t.id
        LEFT JOIN models m ON r.model_id = m.id
        GROUP BY r.plant_name
        ORDER BY r.plant_name
    """)
    plants = cur.fetchall()

    manual_count = 0
    template_count = 0
    total = len(plants)

    print(f"{'Inserting' if apply else 'Would insert'} descriptions for {total} plants\n")

    for row in plants:
        plant_name, country, tech_name, models, unit_count, statuses, first_comm, total_cap = row

        if plant_name in MANUAL_DESCRIPTIONS:
            desc = MANUAL_DESCRIPTIONS[plant_name]
            source = "Wikipedia, WNA, IAEA — AI-reviewed"
            tag = "manual"
            manual_count += 1
        else:
            desc = _build_template(plant_name, country, tech_name, models,
                                   unit_count, statuses, first_comm, total_cap)
            source = "Generated from IAEA PRIS data"
            tag = "template"
            template_count += 1

        if apply:
            cur.execute(
                "INSERT OR REPLACE INTO entity_descriptions "
                "(entity_type, entity_name, description, source) "
                "VALUES (?, ?, ?, ?)",
                ("plant", plant_name, desc, source),
            )

        marker = "+" if apply else "~"
        print(f"  {marker} [{tag:8s}] {plant_name} ({len(desc)} chars)")

    if apply:
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM entity_descriptions WHERE entity_type = 'plant'")
        plant_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM entity_descriptions")
        total_desc = cur.fetchone()[0]
        print(f"\nVerification: {plant_count} plant descriptions in DB")
        print(f"Total descriptions in DB: {total_desc}")
    else:
        print("\n[DRY RUN] Use --apply to insert.")

    print(f"\nSummary: {manual_count} manual + {template_count} template = {manual_count + template_count} total")
    conn.close()


if __name__ == "__main__":
    run("--apply" in sys.argv)
