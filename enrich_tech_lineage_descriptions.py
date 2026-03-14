#!/usr/bin/env python3
"""
Enrich existing technology and design lineage descriptions in-place.
Technologies: 1-2 sentences -> 1-2 paragraphs
Lineages: 2-4 sentences -> 2-3 paragraphs

Usage:
    python enrich_tech_lineage_descriptions.py          # Dry run
    python enrich_tech_lineage_descriptions.py --apply   # Update DB
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

TECHNOLOGY_DESCRIPTIONS = {
    "BWR": (
        "The Boiling Water Reactor (BWR) is the second most common commercial reactor type "
        "worldwide, developed by General Electric in the United States in the 1950s. In a BWR, "
        "ordinary (light) water serves as both coolant and moderator, boiling directly in the "
        "reactor core at approximately 285°C to produce steam that drives the turbine-generator "
        "without an intermediate steam generator. This direct-cycle design simplifies the plant "
        "layout and eliminates the large steam generators found in PWRs, but means the steam "
        "turbine and associated piping must be shielded against radioactive contamination from "
        "short-lived isotopes in the steam.\n\n"
        "BWRs operate at lower pressures (~7 MPa) than PWRs (~15.5 MPa), allowing thinner reactor "
        "vessels, and use control rods inserted from below the core. The technology evolved through "
        "several generations: GE's BWR/1 through BWR/6, ABB-Atom's Swedish variants, and the "
        "advanced ABWR and ESBWR designs. BWRs constitute a significant fraction of the world's "
        "nuclear fleet, particularly in the United States, Japan, Sweden, and Germany."
    ),
    "PWR": (
        "The Pressurized Water Reactor (PWR) is the most widely deployed commercial reactor type "
        "in the world, accounting for roughly two-thirds of all operating nuclear power reactors. "
        "Developed from the US Navy's submarine reactor program by Westinghouse in the 1950s, the "
        "PWR uses ordinary (light) water under high pressure (~15.5 MPa) as both coolant and "
        "neutron moderator. The pressurized primary coolant absorbs heat from the reactor core "
        "at approximately 315°C and transfers it through steam generators to a separate secondary "
        "loop, where lower-pressure water boils to produce steam for the turbine. This two-loop "
        "design keeps radioactive water contained within the primary circuit.\n\n"
        "PWR technology has been developed by numerous vendors worldwide: Westinghouse (USA), "
        "Framatome (France), Siemens/KWU (Germany), Mitsubishi Heavy Industries (Japan), "
        "Combustion Engineering (USA), Babcock & Wilcox (USA), and the Soviet/Russian VVER "
        "lineage. Modern Generation III/III+ PWR designs include the Westinghouse AP1000, "
        "the Framatome EPR, the Korean APR1400, the Chinese Hualong One, and the Russian "
        "VVER-1200, which feature passive safety systems, enhanced containments, and longer "
        "design lifetimes."
    ),
    "PHWR": (
        "The Pressurized Heavy Water Reactor (PHWR) uses heavy water (deuterium oxide, D₂O) as "
        "both moderator and coolant, enabling the use of natural (unenriched) uranium fuel. This "
        "eliminates the need for uranium enrichment facilities, making PHWRs attractive to "
        "countries seeking energy independence without enrichment technology. The moderating "
        "efficiency of heavy water is superior to light water, allowing a self-sustaining chain "
        "reaction with natural uranium's low fissile content (0.7% U-235).\n\n"
        "The dominant PHWR design is Canada's CANDU (CANada Deuterium Uranium), which uses a "
        "distinctive horizontal pressure tube configuration rather than a single large pressure "
        "vessel. This allows on-power refueling — fuel bundles can be inserted and removed while "
        "the reactor operates — resulting in very high capacity factors. India developed its own "
        "PHWR variant, derived from early CANDU technology, with reactors ranging from 220 MW to "
        "700 MW. PHWRs are operated in Canada, India, South Korea, Romania, Argentina, Pakistan, "
        "and China."
    ),
    "GCR": (
        "Gas-Cooled Reactors (GCRs) use graphite as the neutron moderator and carbon dioxide "
        "(CO₂) gas as the coolant. This combination was the basis for the earliest commercial "
        "nuclear power programs in the United Kingdom and France. The British Magnox reactors "
        "(named after the magnesium alloy fuel cladding) were the first generation, operating "
        "from 1956, followed by the more advanced AGR (Advanced Gas-Cooled Reactor) series that "
        "used enriched uranium oxide fuel in stainless steel cladding and operated at higher "
        "temperatures for improved thermal efficiency.\n\n"
        "France developed its own GCR variant, the UNGG (Uranium Naturel Graphite Gaz), using "
        "natural uranium fuel. Gas-cooled reactors can achieve higher coolant outlet temperatures "
        "than water-cooled designs, and the use of an inert gas coolant eliminates the possibility "
        "of coolant boiling. However, the low heat capacity of gas requires large core volumes and "
        "high gas flow rates. While first-generation GCRs have largely been retired, the concept "
        "lives on in the High Temperature Gas Reactor (HTGR) designs."
    ),
    "LWGR": (
        "The Light Water Graphite Reactor (LWGR) uses graphite as the neutron moderator and "
        "ordinary (light) water as the coolant, a combination developed exclusively in the Soviet "
        "Union. The most prominent LWGR design is the RBMK (Reaktor Bolshoy Moshchnosti Kanalnyy, "
        "meaning 'High-Power Channel Reactor'), which uses a massive graphite stack with vertical "
        "pressure tubes containing the fuel assemblies and boiling water coolant.\n\n"
        "The RBMK design was capable of being built in very large sizes (1,000 MW and 1,500 MW) "
        "and allowed on-power refueling, but it suffered from a dangerous positive void coefficient "
        "of reactivity — meaning that loss of coolant could increase reactor power rather than "
        "decrease it. This characteristic contributed to the 1986 Chernobyl disaster. Following "
        "Chernobyl, significant safety modifications were made to remaining RBMK units. All RBMK "
        "reactors outside Russia have been shut down; Russia continues to operate several modified "
        "RBMK-1000 units."
    ),
    "FBR": (
        "Fast Breeder Reactors (FBRs) use fast (unmoderated) neutrons to sustain the fission "
        "chain reaction, unlike thermal reactors which slow neutrons with a moderator. The fast "
        "neutron spectrum allows FBRs to convert fertile uranium-238 (which constitutes 99.3% of "
        "natural uranium) into fissile plutonium-239 in a 'blanket' surrounding the core, "
        "potentially producing more fissile material than they consume — hence 'breeder.' This "
        "technology could theoretically extend the world's uranium fuel supply by a factor of 60 "
        "or more.\n\n"
        "FBRs typically use liquid sodium as the coolant due to its excellent heat transfer "
        "properties and minimal neutron moderation. Major fast reactor programs have existed in "
        "Russia (BN-350, BN-600, BN-800), France (Phénix, Superphénix), Japan (Monju), the UK "
        "(PFR), the US (EBR-I, EBR-II, Fermi-1), and India (PFBR). While the technology has "
        "proven technically feasible, economic competitiveness and sodium safety challenges have "
        "limited commercial deployment. Russia's BN-800 (operational since 2016) is currently the "
        "world's most powerful operating fast reactor."
    ),
    "HTGR": (
        "The High Temperature Gas Reactor (HTGR) represents an advanced evolution of gas-cooled "
        "reactor technology, using helium gas as the coolant and graphite as both moderator and "
        "structural material. The key innovation is the use of TRISO (TRi-structural ISOtropic) "
        "fuel particles — tiny spheres of uranium encased in multiple layers of ceramic and carbon "
        "coatings that can withstand extremely high temperatures (up to ~1,600°C) without releasing "
        "fission products. This provides an inherent safety feature: the fuel itself serves as a "
        "primary containment barrier.\n\n"
        "HTGRs can achieve coolant outlet temperatures of 700-950°C, far higher than water-cooled "
        "reactors (~300°C), enabling higher thermal efficiency and potential applications in "
        "industrial process heat and hydrogen production. Two main fuel configurations exist: "
        "prismatic block (used in Japan's HTTR and the US Fort St. Vrain) and pebble bed (used "
        "in Germany's AVR/THTR and China's HTR-PM). China's Shidaowan HTR-PM, which achieved "
        "commercial operation in 2023, is the world's first commercial pebble bed HTGR and "
        "demonstrates the technology's viability for deployment."
    ),
    "HWGCR": (
        "The Heavy Water Gas-Cooled Reactor (HWGCR) is a rare reactor type that combines heavy "
        "water (D₂O) moderation with carbon dioxide gas cooling. This hybrid approach was explored "
        "experimentally in the 1960s, seeking to combine the neutron economy advantages of heavy "
        "water with the high-temperature potential of gas cooling. Only a small number were ever "
        "built, most notably the Czechoslovak KS 150 (A-1) reactor at Jaslovské Bohunice and "
        "France's EL-4 (Brennilis) prototype.\n\n"
        "The concept offered theoretical advantages — natural uranium fuel capability (from heavy "
        "water moderation) plus higher thermal efficiency (from gas cooling) — but proved "
        "impractical in competition with simpler, more proven designs. The type was largely "
        "abandoned by the 1970s in favor of light water reactors and standard PHWR designs."
    ),
    "HWLWR": (
        "The Heavy Water Light Water Reactor (HWLWR) is a hybrid design using heavy water (D₂O) "
        "as the neutron moderator and ordinary light water as the coolant. This configuration "
        "retains the neutron economy benefits of heavy water moderation (allowing use of slightly "
        "enriched or natural uranium fuel) while using cheaper and more readily available light "
        "water for heat removal. The concept was explored primarily in the Soviet Union and Japan.\n\n"
        "The most notable HWLWR was the Soviet Prototype advanced heavy water reactor at Dimitrovgrad "
        "and the Japanese Fugen (Advanced Thermal Reactor), which operated from 1979 to 2003. "
        "The ATR concept was part of Japan's long-term nuclear strategy but was ultimately not "
        "pursued commercially in favor of conventional LWR technology. The type remains a "
        "historical curiosity with no current operating examples."
    ),
    "LMGMR": (
        "The Liquid Metal Graphite Moderated Reactor (LMGMR) is a rare Soviet-era design that "
        "combines liquid metal (bismuth or sodium) cooling with graphite moderation. This unusual "
        "combination was used in only one power reactor: the AM-1 (Atom Mirny) at Obninsk, which "
        "in 1954 became the world's first nuclear power plant to generate electricity for a grid. "
        "The AM-1 operated at just 5 MW of electrical output and served primarily as a prototype "
        "and research facility.\n\n"
        "While the AM-1 holds enormous historical significance as the birthplace of civilian "
        "nuclear power, the LMGMR concept was not pursued for commercial deployment. Subsequent "
        "Soviet reactor development branched into the VVER (water-cooled) and RBMK "
        "(graphite-moderated, water-cooled) lineages for large-scale power generation, and "
        "sodium-cooled fast reactors (BN series) for fast breeder applications."
    ),
    "OCM": (
        "The Organic Cooled and Moderated Reactor (OCM) is an experimental reactor concept that "
        "uses organic liquids (typically polyphenyls such as terphenyl mixtures) as both the "
        "coolant and neutron moderator. Organic coolants can operate at high temperatures without "
        "requiring high pressure, do not become highly radioactive, and do not corrode common "
        "metals — advantages that promised simpler, cheaper plant designs.\n\n"
        "Only one OCM was built for power generation: the Gentilly-1 (CANDU-OCR) in Quebec, "
        "Canada, which was an experimental organic-cooled variant of the CANDU design. The "
        "concept was ultimately abandoned due to problems with organic coolant decomposition under "
        "radiation (requiring continuous purification and replacement) and the superior economics "
        "of conventional water-cooled designs."
    ),
    "SGHWR": (
        "The Steam Generating Heavy Water Reactor (SGHWR) is a British-designed reactor type that "
        "uses heavy water (D₂O) as the neutron moderator and light water as the coolant, with "
        "steam generation occurring within vertical pressure tubes in the reactor core — similar "
        "in some respects to a boiling water reactor but with heavy water moderation. The design "
        "was developed by the UK Atomic Energy Authority at Winfrith.\n\n"
        "The only SGHWR built was the 100 MW prototype at Winfrith in Dorset, which operated "
        "from 1968 to 1990. The SGHWR was briefly selected as the UK's next-generation reactor "
        "design in 1974 before the decision was reversed in favor of the AGR and later the PWR "
        "(Sizewell B). The concept demonstrated technical feasibility but was never commercialized."
    ),
}

LINEAGE_DESCRIPTIONS = {
    "ge-bwr": (
        "General Electric's boiling water reactor lineage is one of the foundational reactor "
        "families in commercial nuclear power, spanning from the earliest experimental units of "
        "the late 1950s through seven generations of increasingly refined designs. The BWR concept "
        "— where water boils directly in the reactor core, producing steam that drives the turbine "
        "without intermediate heat exchangers — was pioneered by GE and the Argonne National "
        "Laboratory. The direct-cycle approach simplifies the plant design compared to PWRs by "
        "eliminating steam generators, though it requires radiation shielding of the turbine "
        "building.\n\n"
        "The lineage progressed through clearly defined generations: the prototype BWR/1 (Dresden-1, "
        "1960), the first commercial designs BWR/2 and BWR/3 with internal jet pump recirculation, "
        "the widely deployed BWR/4 (including all six Fukushima Daiichi units), the BWR/5 with "
        "improved emergency core cooling, and the BWR/6 with redesigned fuel and control systems. "
        "Containment designs evolved in parallel: the distinctive Mark I (inverted lightbulb drywell "
        "with torus wetwell), Mark II (cylindrical over-under), and Mark III (free-standing steel "
        "with horizontal vents). The GE BWR lineage has been deployed extensively in the United "
        "States, Japan, Mexico, Spain, Sweden, and several other countries."
    ),
    "abb-bwr": (
        "The ABB-Atom (originally ASEA-Atom) BWR lineage represents Sweden's independent "
        "development of boiling water reactor technology, producing designs with several distinctive "
        "features that differentiate them from GE's BWR family. Most notably, ABB-Atom BWRs use "
        "internal recirculation pumps mounted inside the reactor vessel rather than external "
        "recirculation loops, eliminating large-bore piping penetrations below the core and reducing "
        "the risk of large-break loss-of-coolant accidents.\n\n"
        "The lineage evolved from the Ågesta prototype (which also produced district heating) "
        "through the Oskarshamn and Barsebäck stations to the advanced Forsmark-3 design. Swedish "
        "BWRs also feature prestressed concrete containments with condensation pools rather than "
        "the steel containments and torus/suppression pool designs used by GE. ABB-Atom exported "
        "its technology to Finland (Olkiluoto 1-2) and contributed to the development of the "
        "ABWR. The Swedish BWR designs were generally regarded as among the safest of the "
        "Generation II reactor types."
    ),
    "abwr": (
        "The Advanced Boiling Water Reactor (ABWR) is a Generation III reactor design developed "
        "jointly by GE, Hitachi, and Toshiba, incorporating lessons learned from decades of BWR "
        "operation worldwide. The ABWR was the first Generation III reactor design to receive "
        "regulatory approval and the first to be built, with Kashiwazaki-Kariwa Units 6 and 7 in "
        "Japan achieving commercial operation in 1996-1997 — making them landmarks in nuclear "
        "technology evolution.\n\n"
        "Key innovations include reactor-internal recirculation pumps (adopted from the Swedish "
        "BWR tradition, eliminating external recirculation piping), a reinforced concrete "
        "containment vessel (RCCV), digital instrumentation and control systems, and a standardized "
        "modular construction approach designed to reduce build times. The ABWR produces "
        "approximately 1,350 MW of electrical output. Four ABWRs operate in Japan (two at "
        "Kashiwazaki-Kariwa and two at Hamaoka), with additional units built or planned in Japan "
        "and Taiwan. The design served as a stepping stone to GE-Hitachi's more advanced ESBWR "
        "passive-safety concept."
    ),
    "westinghouse-pwr": (
        "The Westinghouse PWR lineage is the foundational family of pressurized water reactors, "
        "tracing its origins to the US Navy's nuclear submarine program. Captain Hyman Rickover's "
        "team at Westinghouse developed the submarine thermal reactor (STR) for the USS Nautilus, "
        "and this technology was adapted for the Shippingport Atomic Power Station (1957), the "
        "world's first full-scale commercial PWR. The design uses pressurized light water as both "
        "coolant and moderator, with heat transferred from the reactor core through steam "
        "generators to produce steam in a secondary loop.\n\n"
        "Westinghouse developed progressively larger designs organized by the number of primary "
        "coolant loops: 1-loop (early prototypes), 2-loop (up to ~600 MW), 3-loop (~900 MW), and "
        "4-loop (~1,100-1,200 MW). The technology was licensed globally, forming the basis for "
        "French (Framatome), German (Siemens/KWU), Japanese (MHI), Korean (KHNP), and other "
        "national PWR programs. The Westinghouse AP1000, a Generation III+ evolution with passive "
        "safety systems, represents the latest in this lineage. No reactor family has been more "
        "influential in shaping the global nuclear industry — the majority of the world's "
        "operating reactors trace their design DNA to Westinghouse's original PWR concept."
    ),
    "framatome-pwr": (
        "The Framatome PWR lineage is the product of France's extraordinary commitment to nuclear "
        "standardization — the 'Messmer Plan' of 1974 that led to the world's most systematic "
        "nuclear buildout. Framatome (now part of the EDF group) began with a Westinghouse license "
        "for the 3-loop PWR design and progressively developed it into a fully French technology. "
        "The standardized fleet approach built nearly identical reactors in large batches, "
        "dramatically reducing costs and simplifying operations.\n\n"
        "The lineage evolved through well-defined series: the 900 MW CP0/CP1/CP2 variants "
        "(34 units), the 1,300 MW P4 and P'4 series (20 units), and the 1,450 MW N4 "
        "(4 units). Each generation incorporated incremental improvements while maintaining "
        "maximum commonality with predecessors. The culmination of this lineage is the EPR "
        "(European Pressurized Reactor), a 1,600+ MW Generation III+ design featuring four "
        "independent safety trains, a core catcher, and double containment. EPRs have been built "
        "at Olkiluoto (Finland), Taishan (China), Flamanville (France), and Hinkley Point C (UK). "
        "The simplified EPR2 is now planned for the next generation of French reactors."
    ),
    "ce-pwr": (
        "The Combustion Engineering (CE) PWR lineage developed several distinctive design features "
        "that set it apart from Westinghouse's approach. CE PWRs used a 2×4 loop arrangement — "
        "two hot legs and four cold legs — with larger-diameter reactor vessels and fewer but "
        "larger steam generators. This configuration provided high power density with a simpler "
        "primary circuit layout. CE also developed its own digital reactor protection system "
        "(NUPLEX 80+) and the System 80 standardized plant design.\n\n"
        "The CE PWR lineage was commercially significant, with units deployed at several US plants "
        "including Palo Verde (the largest nuclear generating station in the Western Hemisphere, "
        "with three System 80 units), Millstone, Calvert Cliffs, Waterford, and others. The "
        "technology was also exported to South Korea, where it formed the foundation for Korea's "
        "indigenous reactor program — the OPR-1000 (Korean Standard Nuclear Plant) and the "
        "highly successful APR1400 are direct descendants of CE's System 80 design. CE was "
        "acquired by ABB in 1990 and subsequently by Westinghouse, but its design DNA lives on "
        "prominently in the Korean nuclear program."
    ),
    "bw-pwr": (
        "Babcock & Wilcox (B&W) developed a distinctive PWR lineage characterized by its "
        "once-through steam generators (OTSGs) — a design fundamentally different from the "
        "U-tube and inverted-U steam generators used by Westinghouse, Framatome, and CE. In B&W's "
        "OTSGs, feedwater enters at the top and flows downward around the tubes while primary "
        "coolant flows upward inside them, producing superheated steam. B&W also used a unique "
        "lowered-loop arrangement where the steam generators and reactor coolant pumps are "
        "positioned below the reactor vessel.\n\n"
        "B&W supplied reactors to several US plants, including Three Mile Island, Oconee, Crystal "
        "River, and Davis-Besse. The Three Mile Island Unit 2 accident in 1979 — the most serious "
        "commercial nuclear accident in US history prior to Fukushima — occurred at a B&W-designed "
        "reactor, though the accident resulted from a combination of equipment malfunction and "
        "operator error rather than an inherent design flaw. Despite this association, B&W's "
        "remaining units have compiled strong operating records. B&W's nuclear division evolved "
        "into BWXT, which continues to manufacture naval nuclear reactors for the US Navy."
    ),
    "siemens-pwr": (
        "The Siemens/KWU (Kraftwerk Union) PWR lineage produced some of the most technically "
        "advanced and distinctive pressurized water reactors ever built. The designs are "
        "immediately recognizable by their signature spherical steel primary containment vessels — "
        "a design choice that provides optimal resistance to internal pressure while minimizing "
        "material requirements. KWU PWRs also feature four independent safety trains and a "
        "comprehensive set of engineered safety features.\n\n"
        "The lineage evolved from early pre-Konvoi designs (Obrigheim, Stade, Biblis) through "
        "the standardized Konvoi series (Isar-2, Emsland, Neckarwestheim-2, and Grohnde), which "
        "were considered among the world's most advanced Generation II reactors. Konvoi units "
        "consistently achieved world-leading capacity factors and thermal efficiency. The "
        "technology was exported to Brazil (Angra), Spain (Trillo), Argentina (Atucha), and the "
        "Netherlands (Borssele). Siemens merged its nuclear division with Framatome in 2001 to "
        "form AREVA NP (now Framatome), and the KWU PWR design heritage influenced the development "
        "of the EPR."
    ),
    "siemens-bwr": (
        "Siemens/KWU developed its own BWR lineage for the German market, distinct from both GE's "
        "American designs and ABB-Atom's Swedish variants. The KWU BWRs, designated as BWR/69 and "
        "its successor the SWR/72 (Siedewasserreaktor), introduced internal recirculation pumps "
        "— eliminating external recirculation piping — independently of the Swedish approach. "
        "These designs also featured fine-motion control rod drives and digital instrumentation.\n\n"
        "The lineage includes reactors at Würgassen, Brunsbüttel, Philippsburg-1, Isar-1, and "
        "Krümmel. While fewer in number than the Siemens PWR fleet, the KWU BWR designs were "
        "technically advanced for their era. All German BWRs were shut down during the country's "
        "nuclear phase-out, with the last units closing between 2011 and 2023. The Siemens BWR "
        "technology was never exported outside Germany."
    ),
    "mhi-pwr": (
        "Mitsubishi Heavy Industries (MHI) developed Japan's PWR lineage under a technology "
        "agreement with Westinghouse, adapting and refining the 2-loop, 3-loop, and 4-loop PWR "
        "designs for Japanese conditions. MHI PWRs power Japan's western electric grid (operated "
        "by utilities including Kansai Electric, Shikoku Electric, and Kyushu Electric) and have "
        "been built at sites including Takahama, Ōi, Genkai, Sendai, and Ikata.\n\n"
        "MHI progressively incorporated domestic improvements while maintaining Westinghouse "
        "compatibility, developing the larger 4-loop APWR (Advanced PWR) for new construction. "
        "Japanese PWRs have generally fared better in the post-Fukushima restart process than "
        "BWRs, with several MHI-designed units among the first to receive Nuclear Regulation "
        "Authority (NRA) approval and return to service. MHI's nuclear division also contributes "
        "to Japan's fast reactor and fusion research programs."
    ),
    "korean-pwr": (
        "South Korea's indigenous PWR program is one of the great technology-transfer success "
        "stories in nuclear energy. Beginning with turnkey imports (Kori-1, a Westinghouse PWR), "
        "Korea systematically absorbed reactor design and construction capabilities over three "
        "decades, transitioning from buyer to designer to exporter. The Korean Standard Nuclear "
        "Plant (KSNP/OPR-1000), derived from Combustion Engineering's System 80 design, marked "
        "Korea's emergence as an independent reactor designer in the 1990s.\n\n"
        "The lineage culminated in the APR1400, a 1,400 MW Generation III design developed by "
        "KHNP and KEPCO that won the landmark UAE Barakah contract in 2009 — Korea's first "
        "nuclear export and one of the largest in nuclear industry history. Four APR1400 units "
        "were built at Barakah on schedule and on budget, establishing Korea's credentials as a "
        "competitive nuclear exporter. The APR1400 was subsequently selected for the Czech "
        "Republic's Dukovany expansion. Domestically, APR1400s continue to be built at Shin-Hanul "
        "and Shin-Kori. KHNP is developing next-generation designs including the APR+ and the "
        "i-SMR (innovative Small Modular Reactor)."
    ),
    "vver": (
        "The VVER (Vodo-Vodyanoi Energeticheskiy Reaktor, or Water-Water Power Reactor) is the "
        "Soviet/Russian pressurized water reactor family and the second most widely deployed "
        "reactor design lineage in the world after the Westinghouse PWR family. Developed by OKB "
        "Gidropress and the Kurchatov Institute from the 1950s, VVERs share the fundamental PWR "
        "principle of pressurized water cooling and moderation but feature distinctive design "
        "elements including hexagonal fuel assemblies, horizontal steam generators, and (in earlier "
        "models) reduced-height containments.\n\n"
        "The lineage evolved through several major variants: the compact VVER-440 (Models V179, "
        "V230, V213) deployed widely across the Soviet bloc; the VVER-1000 (V302, V320, V338, "
        "V392) that became the standard Soviet large reactor; and the modern VVER-1200 (V392M, "
        "V491, V523, V529), a Generation III+ design with passive safety features, double "
        "containment, and core catcher. The VVER-1200, marketed internationally by Rosatom as the "
        "AES-2006, is the most commercially successful reactor design on the current export "
        "market, with units built or under construction in Russia, Belarus, Bangladesh, Egypt, "
        "Finland, Hungary, India, Iran, Turkey, and China. Rosatom is now developing the "
        "VVER-1300 (VVER-TOI) as the next standardized design."
    ),
    "candu": (
        "The CANDU (CANada Deuterium Uranium) is one of the most distinctive reactor families in "
        "commercial nuclear power, developed by Atomic Energy of Canada Limited (AECL). Its "
        "defining features are the use of heavy water (D₂O) as both moderator and coolant, natural "
        "uranium fuel (eliminating the need for enrichment), and a horizontal pressure tube design "
        "where individual fuel channels pass through a large unpressurized calandria tank filled "
        "with heavy water moderator. This architecture enables on-power refueling using automated "
        "fueling machines — fuel bundles are inserted and removed while the reactor operates.\n\n"
        "The lineage progressed from the NPD prototype (1962) through the 500 MW CANDU-6 "
        "(the primary export model, deployed in Argentina, Romania, South Korea, Pakistan, and "
        "China) to the 900 MW CANDU-9 and Bruce/Darlington units. The CANDU design achieves "
        "exceptional neutron economy and very high capacity factors. Canada's nuclear fleet is "
        "concentrated in Ontario, where 17 CANDU reactors at Bruce, Darlington, and Pickering "
        "provide roughly 60% of provincial electricity. AECL's commercial reactor division was "
        "acquired by SNC-Lavalin (now AtkinsRéalis) as Candu Energy, and the advanced EC6 "
        "(Enhanced CANDU 6) is offered for new construction."
    ),
    "indian-phwr": (
        "India's indigenous PHWR program represents one of the most remarkable examples of "
        "self-reliant nuclear technology development. After Canada suspended nuclear cooperation "
        "following India's 1974 nuclear test, India was cut off from international nuclear "
        "commerce, forcing the Nuclear Power Corporation of India Limited (NPCIL) and the Bhabha "
        "Atomic Research Centre (BARC) to develop reactor technology independently. Using the "
        "CANDU concept as a starting point, India designed and built its own pressurized heavy "
        "water reactors with progressively increasing capability.\n\n"
        "The Indian PHWR lineage evolved from the 100 MW and 220 MW designs (deployed at "
        "Rajasthan, Madras/Kalpakkam, Narora, Kakrapar, and Kaiga) to the larger 540 MW units "
        "at Tarapur and the 700 MW PHWRs at Kakrapar and Rajasthan — the most advanced Indian "
        "PHWR design. While sharing the fundamental PHWR principle of heavy water moderation and "
        "pressure tube architecture, Indian designs diverge from CANDU in several details including "
        "containment design, safety systems, and seismic qualification. The Indian PHWR fleet "
        "forms the backbone of the first stage of India's three-stage nuclear power program, "
        "which envisions eventual transition to fast breeders and thorium-based reactors."
    ),
    "chinese-pwr": (
        "China's PWR program draws from multiple international technology streams, synthesized "
        "into a rapidly evolving indigenous capability. The program began with the CNP-300, a "
        "small PWR derived from China's naval reactor program, deployed at Qinshan and exported "
        "to Pakistan. China then imported and absorbed technology from three major Western/Russian "
        "sources: French M310 designs (Daya Bay, Ling Ao), Canadian CANDU technology (Qinshan III), "
        "and later Westinghouse AP1000 and Russian VVER-1000 designs.\n\n"
        "This multi-stream approach enabled China to develop the Hualong One (HPR1000), its "
        "flagship Generation III pressurized water reactor combining elements from French, "
        "Westinghouse, and indigenous designs. The Hualong One features a 177-fuel-assembly core, "
        "three safety trains, double containment, and a 60-year design life. First deployed at "
        "Fuqing-5 (2021), it has become China's standard for new domestic construction and nuclear "
        "exports, with units built in Pakistan (Karachi) and proposed for multiple international "
        "markets. China's PWR development is split between CNNC (Hualong One) and CGN (which "
        "developed the parallel ACPR1000 before the designs were merged). The CAP1000/1400, "
        "derived from Westinghouse AP1000 technology, represents a separate Chinese PWR stream."
    ),
    "uk-gcr": (
        "Britain's gas-cooled reactor program represents one of the longest and most distinctive "
        "nuclear technology lineages, spanning two generations of reactor design unique to the "
        "United Kingdom. The first generation — the Magnox reactors, named after the magnesium "
        "alloy cladding of their natural uranium metal fuel — began with Calder Hall in 1956 "
        "(the world's first commercial nuclear power station) and continued through 26 units at "
        "11 sites. Magnox reactors used CO₂ gas coolant and graphite moderation, producing "
        "electricity at modest thermal efficiency.\n\n"
        "The second generation — the Advanced Gas-Cooled Reactor (AGR) — addressed Magnox "
        "limitations by using enriched uranium oxide fuel in stainless steel cladding, achieving "
        "significantly higher coolant temperatures (~650°C) and thermal efficiency (~40%). "
        "Fourteen AGR units were built at six twin-reactor stations, commissioned between 1976 "
        "and 1989. While technically sophisticated, the AGR program suffered from construction "
        "delays, cost overruns, and limited operational flexibility. All Magnox stations have been "
        "permanently shut down, and the AGR fleet is being progressively retired by EDF Energy, "
        "with the last stations closing in the mid-2020s after extended service lives."
    ),
    "french-gcr": (
        "France's UNGG (Uranium Naturel Graphite Gaz) reactor program was the country's "
        "first-generation nuclear technology, developed independently of the British Magnox "
        "program but sharing the same fundamental concept: graphite moderation, CO₂ gas cooling, "
        "and natural uranium fuel. Nine UNGG reactors were built in France between 1956 and 1971 "
        "at sites including Marcoule, Chinon, St-Laurent-des-Eaux, and Bugey.\n\n"
        "The UNGG design used natural metallic uranium fuel with magnesium alloy cladding, similar "
        "to Magnox but with some design differences. France ultimately abandoned the GCR lineage "
        "in favor of American PWR technology after the Messmer Plan of 1974, concluding that "
        "light water reactors offered better economics and scalability. All UNGG reactors were "
        "shut down by 1994, and France went on to build the world's most standardized PWR fleet "
        "under Framatome. The UNGG program's legacy lies primarily in establishing France's "
        "nuclear industrial base and demonstrating the country's commitment to energy independence."
    ),
    "rbmk-lwgr": (
        "The RBMK (Reaktor Bolshoy Moshchnosti Kanalnyy, or High-Power Channel Reactor) is the "
        "Soviet Union's graphite-moderated, water-cooled reactor design, developed alongside the "
        "VVER as part of the USSR's dual-track reactor program. The RBMK design uses a massive "
        "graphite block as neutron moderator with vertical pressure tubes containing fuel "
        "assemblies and boiling water coolant — combining features of graphite-moderated and "
        "boiling water reactor concepts. The design allowed very large unit sizes (1,000 MW and "
        "1,500 MW) and on-power refueling.\n\n"
        "The RBMK is permanently associated with the 1986 Chernobyl disaster, when Reactor No. 4 "
        "at the Chernobyl Nuclear Power Plant in Ukraine suffered an uncontrolled power excursion "
        "during a safety test, leading to steam explosions, an open graphite fire, and the "
        "worst nuclear accident in history. A key contributing factor was the RBMK's positive "
        "void coefficient — when coolant is lost, reactivity increases rather than decreases, "
        "creating an inherent instability at low power. Following Chernobyl, extensive "
        "modifications were made to remaining RBMK units, including modifications to the control "
        "rod design and operating procedures. Lithuania's two RBMK-1500 units (the most powerful "
        "ever built) were closed as an EU accession condition. Russia continues to operate "
        "modified RBMK-1000 units at three sites."
    ),
    "sodium-fast": (
        "Sodium-cooled fast reactors represent the most mature fast breeder technology, with "
        "development programs spanning seven decades across multiple countries. Liquid sodium is "
        "used as the coolant because it transfers heat exceptionally well, does not significantly "
        "moderate (slow) neutrons (preserving the fast neutron spectrum needed for breeding), and "
        "has a high boiling point (883°C) allowing unpressurized operation. However, sodium reacts "
        "vigorously with water and burns in air, requiring careful engineering of secondary systems "
        "and leak management.\n\n"
        "Major programs include the USSR/Russian BN series (BN-350 at Aktau, BN-600 and BN-800 at "
        "Beloyarsk — the world's largest operating fast reactors), France's Phénix and Superphénix "
        "(the latter the world's largest fast reactor at 1,200 MW, shut down in 1997), Japan's "
        "Monju (plagued by a sodium leak in 1995 and permanently closed in 2017), the UK's "
        "Dounreay PFR, and the US's EBR-I, EBR-II, and Fermi-1. India's Prototype Fast Breeder "
        "Reactor (PFBR) at Kalpakkam aims to be the next operational unit. Russia's BN-800 "
        "(operational 2016) is the current state of the art, and Russia is now building the "
        "BN-1200M as the next-generation commercial fast reactor."
    ),
    "lead-cooled-fast": (
        "Lead-cooled fast reactors use liquid lead or lead-bismuth eutectic (LBE) as the primary "
        "coolant, offering several advantages over sodium: lead does not react with water or air, "
        "provides excellent radiation shielding, and has an even higher boiling point (1,749°C). "
        "The Soviet Union developed LBE-cooled reactors for nuclear submarine propulsion (the "
        "Alfa-class), gaining unique operational experience with this technology.\n\n"
        "Russia's BREST-OD-300 reactor at Seversk, currently under construction, is the world's "
        "first lead-cooled fast reactor designed for commercial power generation. The BREST concept "
        "is part of Russia's Proryv ('Breakthrough') closed fuel cycle program, designed to operate "
        "with a co-located fuel fabrication and reprocessing facility. The lead-cooled fast reactor "
        "is also being pursued internationally through the European ALFRED demonstrator project "
        "and various Generation IV research initiatives. The technology promises inherent safety "
        "advantages due to the chemical inertness of lead coolant and the natural circulation "
        "capability of heavy liquid metals."
    ),
    "htgr": (
        "The High Temperature Gas Reactor lineage uses helium coolant, graphite moderation, and "
        "TRISO (TRi-structural ISOtropic) coated particle fuel — ceramic-encapsulated microspheres "
        "that retain fission products at temperatures up to ~1,600°C, providing an inherent safety "
        "barrier. The technology promises higher thermal efficiency (40-50% vs. ~33% for LWRs) "
        "and the potential for industrial process heat and hydrogen production applications.\n\n"
        "Two main fuel configurations have been developed: prismatic block fuel (used in the US "
        "Peach Bottom and Fort St. Vrain reactors, and Japan's HTTR test reactor) and pebble bed "
        "fuel (used in Germany's AVR and THTR-300, and China's HTR series). Germany pioneered "
        "both concepts but abandoned nuclear power before commercializing them. China has taken "
        "the lead with the Shidaowan HTR-PM, a twin-module pebble bed reactor driving a single "
        "steam turbine, which achieved commercial operation in 2023 — the world's first commercial "
        "HTGR. China is now planning a scaled-up HTR-PM600 with six reactor modules. South Africa's "
        "PBMR (Pebble Bed Modular Reactor) project was cancelled in 2010 after significant "
        "investment. The HTGR concept remains actively pursued in several Generation IV programs."
    ),
    "hwgcr": (
        "The Heavy Water Gas-Cooled Reactor lineage represents a historical experiment in combining "
        "the superior neutron economy of heavy water moderation with the high-temperature "
        "potential of gas cooling. Only two power-producing examples were built: France's EL-4 "
        "(Brennilis) prototype, which operated from 1967 to 1985, and Czechoslovakia's KS 150 "
        "(A-1) at Jaslovské Bohunice, which suffered a serious fuel damage accident in 1977 and "
        "was permanently shut down.\n\n"
        "The concept offered theoretical advantages — natural uranium capability from heavy water "
        "moderation combined with higher thermal efficiency from gas cooling — but proved "
        "uncompetitive with simpler, more proven alternatives. Both France and Czechoslovakia "
        "subsequently adopted PWR technology (Framatome and VVER respectively). The HWGCR lineage "
        "is now entirely historical with no prospect of revival."
    ),
    "smr": (
        "Small Modular Reactors (SMRs) represent a diverse category of reactor designs generally "
        "defined as producing under 300 MW of electrical output, with an emphasis on factory "
        "fabrication, modular construction, and simplified safety systems. The SMR concept aims "
        "to address the economic challenges of large nuclear plants (multi-billion-dollar upfront "
        "costs, long construction times) by enabling standardized manufacturing, shorter "
        "construction schedules, and incremental capacity additions.\n\n"
        "The SMR landscape includes water-cooled designs (NuScale VOYGR, Rolls-Royce SMR, "
        "Argentina's CAREM, China's ACP100/Linglong One, Russia's KLT-40S floating reactor), "
        "high-temperature gas-cooled designs (X-energy Xe-100), sodium-cooled fast reactors "
        "(TerraPower Natrium), and molten salt concepts (Kairos Power). Russia deployed the "
        "world's first floating nuclear power plant, the Akademik Lomonosov, in 2020 at Pevek "
        "in the Arctic, using two KLT-40S reactors derived from icebreaker technology. Argentina's "
        "CAREM-25 is among the most advanced land-based SMR construction projects. The SMR market "
        "is still nascent, with most designs in licensing or early construction phases."
    ),
    "other-prototypes": (
        "This category encompasses one-of-a-kind prototype and demonstration reactors that do not "
        "belong to any major design lineage. These pioneering facilities represent the experimental "
        "diversity of early nuclear power development, when multiple reactor concepts were explored "
        "before the industry converged on a few dominant designs — primarily the PWR, BWR, and "
        "PHWR.\n\n"
        "Notable prototypes include the Shippingport reactor (the first US commercial PWR, later "
        "used to demonstrate the light water breeder concept), the Fermi-1 sodium-cooled fast "
        "breeder, the Piqua organic-cooled reactor, and various early experimental units that "
        "tested concepts subsequently abandoned or absorbed into major lineages. These reactors "
        "played a crucial role in establishing the technological foundations of commercial nuclear "
        "power, even though their specific designs were not replicated."
    ),
}


def run(apply=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Update technologies
    print(f"{'Updating' if apply else 'Would update'} {len(TECHNOLOGY_DESCRIPTIONS)} technology descriptions\n")
    for code, desc in TECHNOLOGY_DESCRIPTIONS.items():
        cur.execute("SELECT description FROM technologies WHERE code = ?", (code,))
        old = cur.fetchone()
        old_len = len(old[0]) if old and old[0] else 0
        if apply:
            cur.execute("UPDATE technologies SET description = ? WHERE code = ?", (desc, code))
        print(f"  {'+'if apply else '~'} {code}: {old_len} -> {len(desc)} chars")

    # Update lineages
    print(f"\n{'Updating' if apply else 'Would update'} {len(LINEAGE_DESCRIPTIONS)} lineage descriptions\n")
    for slug, desc in LINEAGE_DESCRIPTIONS.items():
        cur.execute("SELECT description FROM design_lineages WHERE slug = ?", (slug,))
        old = cur.fetchone()
        old_len = len(old[0]) if old and old[0] else 0
        if apply:
            cur.execute("UPDATE design_lineages SET description = ? WHERE slug = ?", (desc, slug))
        print(f"  {'+'if apply else '~'} {slug}: {old_len} -> {len(desc)} chars")

    if apply:
        conn.commit()
        cur.execute("SELECT code, LENGTH(description) FROM technologies ORDER BY code")
        print("\n=== Technology description lengths ===")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} chars")
        cur.execute("SELECT slug, LENGTH(description) FROM design_lineages ORDER BY slug")
        print("\n=== Lineage description lengths ===")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} chars")
    else:
        print("\n[DRY RUN] Use --apply to update.")

    conn.close()


if __name__ == "__main__":
    run("--apply" in sys.argv)
