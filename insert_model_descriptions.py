#!/usr/bin/env python3
"""
Insert model descriptions into entity_descriptions table.
154 models with 1-2 paragraph descriptions for major models,
2-4 sentences for minor/prototype models.

Usage:
    python insert_model_descriptions.py          # Dry run
    python insert_model_descriptions.py --apply  # Insert into DB
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

MODEL_DESCRIPTIONS = {
    # =====================================================================
    # MAJOR GCR MODELS
    # =====================================================================
    "Magnox": (
        "The Magnox reactor is Britain's first-generation gas-cooled reactor design, named after "
        "the magnesium-aluminium alloy (Magnox) used to clad its natural uranium metal fuel rods. "
        "Twenty-eight Magnox units were built across 11 sites in the UK between 1956 and 1971, "
        "making it one of the earliest mass-deployed commercial reactor designs. The reactors use "
        "carbon dioxide gas as coolant and graphite as moderator, with relatively low power "
        "density and thermal efficiency compared to later designs.\n\n"
        "Magnox reactors could use natural uranium fuel, avoiding the need for enrichment, which "
        "was a strategic advantage in the early nuclear era. However, the metallic fuel limited "
        "operating temperatures and burnup. The design also served dual purposes — several early "
        "Magnox reactors (particularly Calder Hall and Chapelcross) produced weapons-grade "
        "plutonium alongside electricity. All Magnox reactors have been permanently shut down, "
        "with the last (Wylfa-1) closing in 2015, and their sites are in various stages of "
        "decommissioning."
    ),
    "AGR": (
        "The Advanced Gas-Cooled Reactor (AGR) is Britain's second-generation gas-cooled reactor "
        "design, developed to address the limitations of the earlier Magnox design. AGRs use "
        "enriched uranium oxide fuel in stainless steel cladding, enabling significantly higher "
        "operating temperatures (coolant outlet ~650°C) and thermal efficiency (~40%) compared "
        "to Magnox reactors. The design retains the CO₂ gas coolant and graphite moderator "
        "combination but operates at higher pressure.\n\n"
        "Fifteen AGR units were built at seven twin-reactor stations in the UK, commissioned "
        "between 1976 and 1989. While technically sophisticated, the AGR program was plagued by "
        "construction delays and cost overruns, and the design was never exported. AGRs have been "
        "a reliable workhorse of UK electricity generation, though graphite core degradation has "
        "become a life-limiting factor. EDF Energy operates the remaining fleet, which is being "
        "progressively retired in the mid-2020s."
    ),
    "UNGG": (
        "The UNGG (Uranium Naturel Graphite Gaz) is France's first-generation gas-cooled reactor "
        "design, analogous to Britain's Magnox program. UNGG reactors use natural uranium metal "
        "fuel, CO₂ gas cooling, and graphite moderation. Six units were built at Chinon, "
        "Saint-Laurent-des-Eaux, and Bugey between 1963 and 1972. France abandoned the UNGG "
        "concept in favor of American PWR technology after the 1974 Messmer Plan, and all UNGG "
        "reactors were shut down by 1994."
    ),

    # =====================================================================
    # MAJOR PWR MODELS - FRENCH
    # =====================================================================
    "CP0": (
        "The CP0 (Contrat Programme 0) is the first standardized French PWR series, comprising "
        "six 900 MW three-loop units at Fessenheim and Bugey, commissioned between 1977 and 1979. "
        "Based on the Westinghouse three-loop design under license, the CP0 series established "
        "France's approach to standardized nuclear construction. The CP0 units are the oldest in "
        "France's PWR fleet; Fessenheim 1 and 2 were permanently shut down in 2020."
    ),
    "CP1": (
        "The CP1 (Contrat Programme 1) series is the second batch of France's standardized 900 MW "
        "three-loop PWR program, comprising 18 units at Gravelines, Dampierre, Le Blayais, and "
        "Tricastin. Commissioned between 1980 and 1981, the CP1 series incorporated lessons "
        "learned from the CP0 units, including improvements to auxiliary systems and containment "
        "design. The CP1 represents the core of France's 900 MW fleet and has been operated "
        "successfully by EDF for over four decades, with ongoing life extension programs."
    ),
    "CP2": (
        "The CP2 (Contrat Programme 2) series is the third and final batch of France's 900 MW "
        "PWR program, comprising 10 units at Chinon-B, Cruas, and Saint-Laurent-B. Commissioned "
        "between 1983 and 1988, the CP2 units feature improvements over the CP1 design including "
        "upgraded control room ergonomics and auxiliary systems. Together with CP0 and CP1, the "
        "34 units of the 900 MW program form the backbone of France's nuclear fleet."
    ),
    "P4 REP 1300": (
        "The P4 REP 1300 is the first generation of France's 1,300 MW four-loop PWR series, "
        "comprising 20 units at Paluel, Saint-Alban, Flamanville, Cattenom, Belleville, Nogent, "
        "Penly, and Golfech. Commissioned between 1984 and 1993, the P4 design scaled up from "
        "the 900 MW series to a four-loop configuration with larger steam generators and a "
        "prestressed concrete containment with a steel liner. The P4 series demonstrated France's "
        "ability to standardize at larger power levels, with each unit producing roughly 1,300 MW."
    ),
    "N4 REP 1450": (
        "The N4 REP 1450 is France's most powerful domestically designed PWR series, comprising "
        "four 1,450 MW units at Chooz-B and Civaux. Commissioned between 1996 and 2002, the N4 "
        "represents the final evolution of the French standardized PWR program before the "
        "transition to the EPR design. The N4 units feature digital instrumentation and control "
        "systems, larger-diameter reactor vessels, and improved steam generators. The N4 was the "
        "last fully French-designed reactor series before the Framatome-Siemens merger produced "
        "the European EPR."
    ),
    "France CPI": (
        "The France CPI designation refers to French PWR units in the Paluel/Saint-Alban P'4 "
        "variant of the 1,300 MW series, featuring incremental design improvements over the base "
        "P4 configuration. These units incorporated enhanced automation, improved containment "
        "ventilation, and other refinements based on operating experience from the earlier P4 "
        "units."
    ),
    "EPR": (
        "The EPR (European Pressurized Reactor, later Evolutionary Power Reactor) is a "
        "Generation III+ pressurized water reactor designed jointly by Framatome and Siemens, "
        "producing approximately 1,650 MW of electrical output — making it the most powerful "
        "reactor design in operation. The EPR features four independent safety trains (compared "
        "to two or three in earlier designs), a core catcher to contain molten fuel in a severe "
        "accident, double containment, and a design life of 60 years.\n\n"
        "Six EPR units have been built: Olkiluoto-3 in Finland (2023, after major delays), "
        "Taishan 1-2 in China (2018-2019, the first to operate), Flamanville-3 in France (loaded "
        "fuel 2024), and Hinkley Point C Units 1-2 in the UK (under construction). The early EPR "
        "projects suffered severe construction delays and cost overruns, partly attributed to the "
        "design's complexity and first-of-a-kind construction challenges. The simplified EPR2 "
        "design addresses these issues for France's next-generation reactor program."
    ),
    "M310": (
        "The M310 is a Framatome 900 MW three-loop PWR design exported to China, where four "
        "units were built at the Daya Bay and Ling Ao power stations near Hong Kong in Guangdong "
        "province. Based on the French CP1/CP2 design, the M310 was a key technology transfer "
        "vehicle that helped establish China's nuclear industry in the 1990s. All four M310 units "
        "remain in operation with strong capacity factors. The design served as the foundation "
        "for China's subsequent CPR-1000 indigenous development."
    ),
    "Framatome 3 loop": (
        "A generic designation for Framatome three-loop PWR exports that do not fall under the "
        "standard French CP-series naming. These units share the fundamental Framatome 900 MW "
        "three-loop configuration with pressurized water primary circuit, three steam generators, "
        "and a prestressed concrete containment."
    ),
    "CHOOZ-A": (
        "Chooz-A (also known as SENA — Société d'Énergie Nucléaire Franco-Belge des Ardennes) "
        "was a Franco-Belgian prototype PWR built inside a rock cavern at the Chooz site in the "
        "French Ardennes. Operational from 1967 to 1991, this 305 MW Westinghouse-designed reactor "
        "was one of the earliest PWRs in continental Europe and served as a technology pathfinder "
        "for the French nuclear program that followed."
    ),

    # =====================================================================
    # MAJOR PWR MODELS - WESTINGHOUSE
    # =====================================================================
    "W (4-loop) DRYAMB": (
        "The Westinghouse four-loop PWR with large dry ambient-pressure containment is one of "
        "the most widely deployed reactor configurations in the United States. This design features "
        "four primary coolant loops, each with a steam generator and reactor coolant pump, driving "
        "a turbine-generator producing approximately 1,100-1,200 MW of electrical output. The "
        "large dry containment — a massive reinforced or prestressed concrete structure with a "
        "steel liner — provides passive pressure suppression capability for design-basis accidents.\n\n"
        "This configuration is used at major US nuclear stations including Braidwood, Byron, "
        "Comanche Peak, Seabrook, South Texas Project, and Vogtle (original units). The "
        "four-loop Westinghouse PWR with dry ambient containment has proven to be among the "
        "most reliable and highest-performing reactor configurations in the US fleet."
    ),
    "W (4-loop)": (
        "The Westinghouse four-loop PWR is the largest standard configuration in the Westinghouse "
        "PWR family, featuring four primary coolant loops with steam generators producing "
        "approximately 1,100-1,200 MW of electrical output. This general designation covers "
        "four-loop units with various containment types that are not further specified. The "
        "four-loop design evolved from Westinghouse's earlier one-, two-, and three-loop "
        "configurations, achieving the highest power output in the Westinghouse domestic lineup."
    ),
    "W (4-loop) ICECDN": (
        "The Westinghouse four-loop PWR with ice condenser containment uses baskets of borated "
        "ice to absorb heat and condense steam during an accident, allowing a significantly "
        "smaller containment building than the large dry design while maintaining equivalent "
        "pressure ratings. This configuration is used at the Catawba, McGuire, Sequoyah, and "
        "Watts Bar plants in the southeastern United States. The ice condenser concept requires "
        "periodic ice basket maintenance but offers construction cost savings through reduced "
        "containment volume."
    ),
    "W (4-loop) DRYSUB": (
        "The Westinghouse four-loop PWR with subatmospheric containment maintains the containment "
        "atmosphere at below-atmospheric pressure during normal operation, ensuring that any "
        "leakage path draws air inward rather than releasing radioactive material outward. This "
        "variant is used at the Surry and North Anna plants in Virginia, operated by Dominion "
        "Energy. The subatmospheric design provides an inherent safety advantage for leak "
        "management."
    ),
    "W (3-loop)": (
        "The Westinghouse three-loop PWR is a widely deployed configuration producing "
        "approximately 900-1,000 MW of electrical output, featuring three primary coolant loops "
        "with steam generators. This design was the basis for the French nuclear program — "
        "Framatome licensed the three-loop configuration for the 900 MW CP series. Domestically, "
        "three-loop units operate at several US plants including Farley, North Anna (early units), "
        "and H.B. Robinson. The three-loop design also formed the basis for numerous international "
        "exports."
    ),
    "W (3-loop) DRYAMB": (
        "The Westinghouse three-loop PWR with large dry ambient-pressure containment combines the "
        "900-1,000 MW three-loop reactor design with a large reinforced concrete containment "
        "building. This configuration is deployed at several US plants including Farley, Shearon "
        "Harris, and V.C. Summer (original unit). The large dry containment provides substantial "
        "volume for steam absorption during design-basis events."
    ),
    "W (3-loop) DRYSUB": (
        "The Westinghouse three-loop PWR with subatmospheric containment is a variant used at a "
        "small number of US plants. The subatmospheric containment maintains negative pressure "
        "during normal operation, providing enhanced leak-tightness. This configuration produces "
        "approximately 900-1,000 MW of electrical output."
    ),
    "W (3-loops)": (
        "An alternate designation for Westinghouse three-loop PWR units, equivalent to the "
        "W (3-loop) configuration. These reactors feature three primary coolant loops and produce "
        "approximately 900-1,000 MW of electrical output."
    ),
    "W (2-loop)": (
        "The Westinghouse two-loop PWR is a smaller configuration producing approximately "
        "500-600 MW of electrical output, featuring two primary coolant loops with steam "
        "generators. This design was used for several early commercial PWRs in the US and for "
        "international exports, including early plants in Belgium, South Korea, and Slovenia. "
        "The Krško plant in Slovenia is a notable example of this configuration. Two-loop "
        "Westinghouse units represent some of the earliest commercial PWRs still in operation."
    ),
    "W (2-loop) DRYAMB": (
        "The Westinghouse two-loop PWR with large dry ambient-pressure containment combines the "
        "smaller two-loop reactor configuration with a reinforced concrete containment. This "
        "variant is used at several US plants including Prairie Island and Kewaunee (now shut "
        "down). The two-loop design produces approximately 500-600 MW of electrical output."
    ),
    "W (1-loop)": (
        "The Westinghouse one-loop PWR is the smallest and earliest Westinghouse configuration, "
        "used only for prototype and demonstration reactors. The single-loop design features one "
        "steam generator and one primary coolant pump. Shippingport, the world's first "
        "full-scale commercial PWR (1957), used this configuration at approximately 60 MW."
    ),
    "AP1000": (
        "The Westinghouse AP1000 (Advanced Passive 1000) is a Generation III+ pressurized water "
        "reactor that pioneered the use of passive safety systems in a large commercial reactor "
        "design. The AP1000 relies on natural forces — gravity, natural circulation, compressed "
        "gas, and evaporation — rather than active pumps and diesel generators for emergency core "
        "cooling, significantly simplifying the plant design and reducing the number of safety-"
        "related components, valves, and piping.\n\n"
        "The AP1000 produces approximately 1,117 MW of electrical output from a two-loop "
        "configuration with larger-than-traditional steam generators. Six AP1000 units are "
        "in operation: Sanmen 1-2 and Haiyang 1-2 in China (2018-2019, the first to operate), "
        "and Vogtle 3-4 in the United States (2023-2024). The US Vogtle project experienced "
        "significant cost overruns and schedule delays as a first-of-a-kind construction effort, "
        "but the completed units represent the first new US reactors in a generation."
    ),
    "WH F": (
        "The WH F designation refers to Westinghouse-designed PWR units built in South Korea "
        "during the country's early nuclear program. These include the Kori and Yonggwang "
        "(Hanbit) units that were built as turnkey imports in the 1970s-1980s, providing the "
        "technology base from which South Korea developed its indigenous OPR-1000 and APR1400 "
        "designs."
    ),
    "WE 312": (
        "The WE 312 designation refers to early Westinghouse PWR units, specifically the "
        "312 MW configuration used for some of the earliest commercial reactors. These units "
        "represent the transitional period from prototype to commercial-scale PWR deployment."
    ),
    "W?": (
        "An unspecified Westinghouse PWR variant where the exact loop configuration or "
        "containment type is not documented in available records."
    ),
    "SNUPPS": (
        "The Standardized Nuclear Unit Power Plant System (SNUPPS) is a standardized Westinghouse "
        "four-loop PWR design developed in the 1970s as a joint project among several US utilities "
        "to reduce costs through design replication. The concept aimed to build identical plants at "
        "multiple sites using a single NRC design certification. The Callaway plant in Missouri "
        "and the Wolf Creek plant in Kansas were built to the SNUPPS design, producing "
        "approximately 1,200 MW each."
    ),
    "PLWBR": (
        "The Pressurized Light Water Breeder Reactor (PLWBR) was a unique demonstration project "
        "at the Shippingport Atomic Power Station, where the original PWR core was replaced with "
        "a thorium-uranium-233 breeder core in 1977. The PLWBR successfully demonstrated that "
        "breeding (producing more fissile material than consumed) was achievable in a light water "
        "reactor using the thorium fuel cycle. The experiment ran until 1982 and confirmed a "
        "breeding ratio slightly greater than 1.0."
    ),
    "PWR": (
        "A generic PWR designation used for reactors where the specific vendor model or loop "
        "configuration is not further specified in IAEA records. These are typically early or "
        "prototype pressurized water reactors that predate the standardized model naming "
        "conventions of later programs."
    ),
    "PWR 3 loops": (
        "A generic designation for a three-loop pressurized water reactor where the specific "
        "vendor or detailed model variant is not specified. The three-loop configuration "
        "typically produces approximately 900-1,000 MW of electrical output."
    ),
    "PWR 3 loop": (
        "A generic designation for a three-loop pressurized water reactor, equivalent to "
        "'PWR 3 loops.' The three-loop configuration is one of the most common PWR arrangements "
        "worldwide."
    ),
    "2-loop WE": (
        "A two-loop Westinghouse PWR, an alternate naming for the W (2-loop) configuration "
        "producing approximately 500-600 MW of electrical output."
    ),

    # =====================================================================
    # MAJOR PWR MODELS - CE
    # =====================================================================
    "CE (2-loop) DRYAMB": (
        "The Combustion Engineering two-loop PWR with large dry ambient-pressure containment is "
        "a distinctive design featuring CE's characteristic 2×4 loop arrangement — two hot legs "
        "and four cold legs — with two large steam generators. This configuration produces "
        "approximately 800-900 MW of electrical output. CE two-loop units are deployed at Calvert "
        "Cliffs, Millstone, St. Lucie, and Waterford in the United States."
    ),
    "CE DRYAMB": (
        "A Combustion Engineering PWR with large dry ambient-pressure containment, where the "
        "specific loop variant is not further specified. CE PWRs are distinguished by their 2×4 "
        "primary loop arrangement and larger-diameter reactor vessels compared to Westinghouse "
        "designs."
    ),
    "CE80 DRYAMB": (
        "The Combustion Engineering System 80 PWR with large dry ambient-pressure containment "
        "represents CE's most advanced domestic design, featuring an optimized core design and "
        "enhanced safety systems. The System 80 units at Palo Verde in Arizona — the largest "
        "nuclear generating station in the Western Hemisphere with three units — are the "
        "flagship deployment. The System 80 served as the basis for South Korea's OPR-1000 "
        "and ultimately the APR1400."
    ),
    "CE (2-loop) ": (
        "A Combustion Engineering two-loop PWR where the containment type is not further "
        "specified. CE's two-loop design uses the distinctive 2×4 loop arrangement with two "
        "large steam generators."
    ),
    "CE (2-loop)": (
        "A Combustion Engineering two-loop PWR, equivalent to other CE 2-loop designations. "
        "The CE two-loop configuration produces approximately 800-1,300 MW of electrical output "
        "depending on the specific design generation."
    ),
    "CE 3-loop": (
        "A rare Combustion Engineering three-loop PWR variant. Most CE designs used a two-loop "
        "arrangement, making three-loop CE units uncommon in the commercial fleet."
    ),

    # =====================================================================
    # MAJOR PWR MODELS - B&W
    # =====================================================================
    "B&W (L-loop)": (
        "The Babcock & Wilcox lowered-loop PWR is B&W's standard configuration, characterized "
        "by once-through steam generators (OTSGs) positioned below the reactor vessel — a unique "
        "arrangement among PWR vendors. In the lowered-loop design, the steam generators and "
        "reactor coolant pumps are at a lower elevation than the reactor vessel, and the OTSGs "
        "produce slightly superheated steam. This configuration produces approximately 800-900 MW "
        "of electrical output and is deployed at Oconee, Three Mile Island, Crystal River, and "
        "Davis-Besse."
    ),
    "B&W (L-loop) DRYAMB": (
        "A Babcock & Wilcox lowered-loop PWR with large dry ambient-pressure containment. This "
        "variant combines B&W's distinctive once-through steam generators in a lowered-loop "
        "configuration with a standard large dry reinforced concrete containment building."
    ),
    "B&W (R-loop)": (
        "The Babcock & Wilcox raised-loop PWR is a less common variant where the steam generators "
        "are positioned at a higher elevation relative to the reactor vessel. The raised-loop "
        "arrangement was used at a limited number of B&W-supplied plants."
    ),
    "B&W": (
        "A generic Babcock & Wilcox PWR designation where the specific loop configuration "
        "(raised or lowered) is not specified. B&W PWRs are distinguished by their once-through "
        "steam generators, which produce slightly superheated steam unlike the saturated steam "
        "of U-tube generators used by other vendors."
    ),

    # =====================================================================
    # MAJOR PWR MODELS - SIEMENS/KWU
    # =====================================================================
    "Konvoi": (
        "The Konvoi is the final and most advanced standardized PWR series built by Siemens/KWU "
        "for the German market. Three Konvoi units were built — Isar-2 (1988), Emsland (1988), "
        "and Neckarwestheim-2 (1989) — and were widely regarded as among the best-performing "
        "reactors in the world, consistently achieving capacity factors above 90% and world-"
        "record annual electricity generation. The Konvoi features Siemens' signature spherical "
        "steel primary containment surrounded by a reinforced concrete shield building, four "
        "independent safety trains, and advanced digital instrumentation. All three units were "
        "shut down in April 2023 as part of Germany's nuclear phase-out."
    ),
    "PRE KONVOI": (
        "The Pre-Konvoi designation covers the generation of Siemens/KWU PWRs built immediately "
        "before the standardized Konvoi series, including units at Grohnde, Philippsburg-2, and "
        "Brokdorf. These reactors share the characteristic KWU spherical double containment and "
        "four-loop design but with some variation between units. The Pre-Konvoi plants also "
        "achieved excellent operating performance."
    ),
    "KWU (PHWR)": (
        "This designation refers to the Siemens/KWU-designed pressurized heavy water reactors "
        "built at Atucha in Argentina. The Atucha design is unique: it uses heavy water as "
        "moderator and coolant in a pressure vessel configuration (unlike the horizontal pressure "
        "tubes of CANDU reactors), making it one of the very few vertical pressure vessel PHWRs "
        "ever built. Atucha-1 (1974) and Atucha-2 (2014) are operated by NA-SA."
    ),
    "KWU 2-loops": (
        "A two-loop Siemens/KWU PWR design, used for smaller-output units. The KWU two-loop "
        "configuration retains the distinctive Siemens design features including high-quality "
        "materials and advanced safety systems, but in a smaller package producing approximately "
        "450-500 MW of electrical output."
    ),

    # =====================================================================
    # MAJOR PWR MODELS - MHI
    # =====================================================================
    "M (3-loop)": (
        "The Mitsubishi Heavy Industries three-loop PWR is the most common MHI configuration, "
        "producing approximately 850-900 MW of electrical output. Built under Westinghouse "
        "license and adapted for Japanese conditions, MHI three-loop units operate at Takahama, "
        "Ōi, and Genkai in western Japan. Several of these units were among the first to receive "
        "post-Fukushima restart approval from Japan's Nuclear Regulation Authority."
    ),
    "M (4-loop)": (
        "The Mitsubishi Heavy Industries four-loop PWR is the largest standard MHI configuration, "
        "producing approximately 1,100-1,200 MW of electrical output. The four-loop design "
        "represents MHI's adaptation of the Westinghouse four-loop concept for the Japanese "
        "market. These units operate at sites including Ōi and Takahama in western Japan."
    ),
    "M (2-loop)": (
        "The Mitsubishi Heavy Industries two-loop PWR is the smallest standard MHI configuration, "
        "producing approximately 500-600 MW of electrical output. MHI two-loop units were among "
        "the earlier reactors built in Japan, including units at Ikata and Genkai. The Ikata "
        "units were notable for pioneering MOX fuel use in Japanese PWRs."
    ),

    # =====================================================================
    # MAJOR PWR MODELS - VVER
    # =====================================================================
    "VVER V-320": (
        "The VVER V-320 is the standard Soviet VVER-1000 reactor model, producing approximately "
        "1,000 MW of electrical output. The V-320 is the most widely deployed VVER variant, with "
        "25 units operating across Russia and Ukraine. The design features four primary coolant "
        "loops with horizontal steam generators (a distinctive VVER characteristic), hexagonal "
        "fuel assemblies, and a prestressed concrete containment. The V-320 design was "
        "standardized in the early 1980s and represents the backbone of both the Russian and "
        "Ukrainian nuclear fleets."
    ),
    "VVER V-213": (
        "The VVER V-213 is the improved variant of the VVER-440 reactor, developed with enhanced "
        "safety features including a bubble condenser containment system that provides pressure "
        "suppression capability — a significant upgrade over the earlier V-230 model. The V-213 "
        "produces approximately 440 MW of electrical output and has been deployed in Russia, "
        "Czech Republic, Slovakia, Hungary, and Finland (Loviisa, with Western safety upgrades). "
        "The V-213 is the most commonly operating VVER-440 variant."
    ),
    "VVER V-230": (
        "The VVER V-230 is the original VVER-440 reactor model, built in the 1960s-1970s without "
        "a full containment structure — a feature that became a significant safety concern after "
        "Western standards were applied following the end of the Cold War. The V-230 uses a "
        "confinement building rather than a pressure-rated containment, limiting its ability to "
        "prevent radioactive release during severe accidents. EU accession requirements led to the "
        "closure of V-230 units in Bulgaria, Lithuania, and Slovakia, though some continue to "
        "operate in Russia and Armenia (with the Armenian unit lacking even basic containment)."
    ),
    "VVER-1200": (
        "The VVER-1200 is Russia's Generation III+ pressurized water reactor, the centerpiece of "
        "Rosatom's domestic and export reactor program. Producing approximately 1,200 MW of "
        "electrical output, the VVER-1200 features passive safety systems, a core catcher for "
        "severe accident mitigation, double containment, and a 60-year design life. It is "
        "marketed internationally as the AES-2006 power plant. Multiple VVER-1200 variants exist "
        "(V-392M, V-491, V-523, V-529) with differences in safety system configurations for "
        "different regulatory frameworks."
    ),
    "VVER V-491": (
        "The VVER V-491 is a variant of the VVER-1200 reactor designed for export, featuring "
        "active and passive safety systems, a double containment structure, and a core catcher. "
        "The V-491 is being deployed at the Belarus Ostrovets plant and at the Akkuyu plant in "
        "Turkey. It produces approximately 1,200 MW of electrical output and represents Rosatom's "
        "primary export product for countries new to nuclear power."
    ),
    "VVER V-412": (
        "The VVER V-412 is a variant of the VVER-1000 reactor with enhanced safety features "
        "developed for construction at the Kudankulam site in India. The design incorporates "
        "passive hydrogen recombiners and other post-Chernobyl safety improvements. Four V-412 "
        "units are planned for Kudankulam, with Units 1-2 operational and Units 3-4 under "
        "construction."
    ),
    "VVER V-428": (
        "The VVER V-428 is a variant of the VVER-1000 reactor designed for the Chinese market, "
        "deployed at the Tianwan Nuclear Power Plant in Jiangsu province. The V-428 incorporates "
        "enhanced safety features including a full-pressure double containment and passive "
        "hydrogen recombiners. The first two Tianwan units (V-428) were among the first Russian "
        "reactor exports to China."
    ),
    "VVER V-428M": (
        "The VVER V-428M is an upgraded variant of the V-428 design, also deployed at the Tianwan "
        "Nuclear Power Plant in China. The 'M' designation indicates modernization improvements "
        "to the original V-428 design, including enhanced instrumentation and control systems."
    ),
    "VVER V-338": (
        "The VVER V-338 is a VVER-1000 variant deployed at the Rivne (Rovno) Nuclear Power Plant "
        "in Ukraine. The V-338 features some design differences from the standard V-320, "
        "reflecting the evolutionary development of the VVER-1000 design through the late Soviet "
        "period."
    ),
    "VVER V-302": (
        "The VVER V-302 is an early VVER-1000 variant, one of the first 1,000 MW class VVER "
        "designs. The V-302 was deployed at the Novovoronezh Nuclear Power Plant (Unit 5) as the "
        "lead unit for the VVER-1000 program, serving as a prototype and reference plant for the "
        "subsequent standardized V-320 series."
    ),
    "VVER V-270": (
        "The VVER V-270 is an early VVER-440 variant used at the Metsamor (Armenian) Nuclear "
        "Power Plant. Like the V-230, the V-270 lacks a Western-standard containment structure. "
        "Unit 1 was shut down after the 1988 Spitak earthquake, while Unit 2 was restarted in "
        "1995 due to Armenia's energy crisis and continues to operate despite international "
        "concerns about its safety margins."
    ),
    "VVER V-179": (
        "The VVER V-179 is one of the earliest VVER-440 variants, deployed at the Novovoronezh "
        "Nuclear Power Plant (Units 3-4) in Russia. The V-179 represents an early stage of "
        "VVER-440 development, predating the more widely deployed V-213 and V-230 models."
    ),
    "VVER V-120": (
        "The VVER V-120 is an early prototype VVER-210 variant, among the first pressurized "
        "water reactors designed in the Soviet Union. These small-output units were deployed at "
        "Novovoronezh as the initial demonstration of Soviet PWR technology."
    ),
    "VVER V-70": (
        "The VVER V-70 is the very first VVER prototype, a 210 MW unit deployed at the "
        "Novovoronezh Nuclear Power Plant (Unit 1) in 1964. As the first Soviet pressurized "
        "water reactor, the V-70 established the VVER design concept that would evolve into one "
        "of the world's most widely deployed reactor families."
    ),
    "VVER V-187": (
        "The VVER V-187 is a VVER-440 variant deployed at the Kola Nuclear Power Plant in "
        "Russia's Murmansk Oblast, one of the northernmost nuclear power plants in the world. "
        "The V-187 is an intermediate variant between the early V-179 and the later V-213 models."
    ),
    "VVER V-446": (
        "The VVER V-446 is the VVER-1000 variant deployed at the Bushehr Nuclear Power Plant in "
        "Iran. Originally based on a German KWU design abandoned after the 1979 Islamic Revolution, "
        "the Bushehr containment was completed by Rosatom using VVER-1000 reactor technology fitted "
        "into the existing German-designed building — a unique hybrid in nuclear construction."
    ),
    "VVER V-392M": (
        "The VVER V-392M is a variant of the VVER-1200 reactor designed for domestic Russian "
        "deployment, first built at the Novovoronezh-II Nuclear Power Plant. The V-392M features "
        "combined active and passive safety systems, a full-pressure containment, and a core "
        "catcher. It is the reference design for Russia's latest domestic nuclear construction."
    ),
    "VVER V-392B": (
        "The VVER V-392B is a VVER-1200 variant with design modifications compared to the V-392M, "
        "deployed at the Leningrad-II Nuclear Power Plant. It is part of Russia's fleet renewal "
        "program, replacing aging RBMK-1000 units with modern Generation III+ VVER technology."
    ),
    "VVER V-509": (
        "The VVER V-509 is a VVER-1200 variant designed for deployment in Egypt at the El Dabaa "
        "Nuclear Power Plant. The V-509 incorporates design adaptations for the Egyptian site "
        "conditions, including seismic qualification and cooling water arrangements for the "
        "Mediterranean coastal location."
    ),
    "VVER V-523": (
        "The VVER V-523 is a VVER-1200 variant designed for the Rooppur Nuclear Power Plant in "
        "Bangladesh. This variant incorporates Rosatom's latest Generation III+ safety features "
        "and is adapted for the site conditions in Bangladesh."
    ),
    "VVER V-529": (
        "The VVER V-529 is a VVER-1200 variant designated for specific export projects, "
        "incorporating adaptations to meet the regulatory requirements and site conditions of "
        "the customer country."
    ),
    "VVER-TOI": (
        "The VVER-TOI (Typical Optimized and Informatized) is Russia's latest VVER variant, "
        "a VVER-1300 design producing approximately 1,300 MW of electrical output. The VVER-TOI "
        "incorporates standardization improvements, optimized construction methods, and fully "
        "digital instrumentation and control systems. The first VVER-TOI unit is under "
        "construction at the Kursk-II Nuclear Power Plant, replacing the aging RBMK units at "
        "the original Kursk site."
    ),
    "KLT-40S": (
        "The KLT-40S is a compact pressurized water reactor derived from Russian nuclear "
        "icebreaker technology, designed for the Akademik Lomonosov floating nuclear power plant. "
        "Two KLT-40S units are installed on the barge-mounted plant stationed at Pevek in "
        "Russia's Chukotka region, making it the world's first floating nuclear power plant. "
        "Each reactor produces approximately 35 MW of electrical output. The KLT-40S demonstrates "
        "the viability of transportable nuclear power for remote Arctic communities."
    ),

    # =====================================================================
    # MAJOR PWR MODELS - KOREAN
    # =====================================================================
    "OPR-1000": (
        "The OPR-1000 (Optimized Power Reactor 1000, originally the Korean Standard Nuclear Plant "
        "or KSNP) is South Korea's first indigenously designed commercial reactor, derived from "
        "Combustion Engineering's System 80 technology through a systematic technology transfer "
        "program. Producing approximately 1,000 MW of electrical output, twelve OPR-1000 units "
        "were built at Hanbit (Yonggwang) and Hanul (Ulchin), with all units maintaining excellent "
        "operating performance. The OPR-1000 established South Korea as an independent reactor "
        "designer and served as the foundation for the larger APR1400."
    ),
    "APR1400": (
        "The APR1400 (Advanced Power Reactor 1400) is South Korea's flagship Generation III "
        "reactor design, developed by KHNP and KEPCO as an evolution of the OPR-1000 with "
        "enhanced safety features, increased power output (1,400 MW), and a 60-year design life. "
        "The APR1400 features four independent safety injection systems, an in-containment "
        "refueling water storage tank, and seismic isolation capabilities.\n\n"
        "The APR1400 achieved a major international success when it won the UAE Barakah Nuclear "
        "Power Plant contract in 2009, where four units were built largely on schedule — a "
        "significant achievement in an era of widespread nuclear construction delays. Domestically, "
        "APR1400 units operate at Shin-Kori and Shin-Hanul. The design was also selected for the "
        "Czech Republic's new-build program. The APR1400 is one of the most commercially "
        "competitive Generation III reactor designs on the current global market."
    ),

    # =====================================================================
    # MAJOR PWR MODELS - CHINESE
    # =====================================================================
    "CPR-1000": (
        "The CPR-1000 (Chinese Pressurized Reactor 1000) is China's first indigenously mass-"
        "produced commercial reactor design, derived from the French M310 three-loop PWR through "
        "technology transfer at Daya Bay and Ling Ao. Producing approximately 1,000 MW of "
        "electrical output, twenty CPR-1000 units were built at multiple sites during China's "
        "rapid nuclear expansion in the 2010s. The CPR-1000 is operated primarily by China General "
        "Nuclear Power Group (CGN). While highly successful in domestic deployment, the CPR-1000 "
        "is classified as a Generation II+ design and has been superseded by the Generation III "
        "Hualong One for new construction."
    ),
    "HPR1000": (
        "The HPR1000 (Hualong One) is China's flagship Generation III pressurized water reactor, "
        "jointly developed by CNNC and CGN by merging their respective ACP1000 and ACPR1000+ "
        "designs. Producing approximately 1,170 MW of electrical output, the HPR1000 features "
        "a 177-fuel-assembly core, three independent safety trains, active and passive safety "
        "systems, double containment, and a 60-year design life.\n\n"
        "The first HPR1000, Fuqing-5, achieved commercial operation in 2021. The design has "
        "become China's standard for both domestic new construction and international export, "
        "with units built in Pakistan (Karachi 2-3, the first HPR1000 export) and proposed for "
        "several other countries. The HPR1000 is one of the most actively built reactor designs "
        "in the world, with dozens of units operational, under construction, or planned across "
        "Chinese nuclear sites."
    ),
    "CNP-600": (
        "The CNP-600 is an indigenous Chinese two-loop PWR design producing approximately 600 MW "
        "of electrical output. Developed by CNNC, it represents a scaled-up evolution of the "
        "earlier CNP-300. Six CNP-600 units were built at Qinshan Phase II, demonstrating China's "
        "capability to design and construct commercial reactors domestically. The CNP-600 served "
        "as an important stepping stone in China's progression toward larger indigenous designs."
    ),
    "CNP-300": (
        "The CNP-300 is China's earliest indigenous PWR design, a compact 300 MW reactor derived "
        "from the country's nuclear submarine propulsion program. The prototype was built at "
        "Qinshan (Unit 1, operational 1991) — China's first domestically designed nuclear power "
        "plant. The CNP-300 was exported to Pakistan, where four units were built at the Chashma "
        "Nuclear Power Plant under bilateral agreements outside the NSG framework."
    ),
    "CNP-1000": (
        "The CNP-1000 (also designated ACP-1000) is a Chinese three-loop PWR producing "
        "approximately 1,000 MW of electrical output. Developed by CNNC, it represents a step "
        "up from the CNP-600 toward larger-scale indigenous reactor designs. Four CNP-1000 units "
        "were built at the Chashma site in Pakistan. The design evolved into the larger ACP1000 "
        "that was eventually merged into the Hualong One program."
    ),
    "ACPR-1000": (
        "The ACPR-1000 (Advanced CPR-1000) is CGN's improved variant of the CPR-1000, incorporating "
        "enhanced safety features to meet Generation III requirements. Four ACPR-1000 units were "
        "built at the Yangjiang Nuclear Power Plant. The ACPR-1000 was eventually merged with "
        "CNNC's ACP1000 design to create the unified Hualong One (HPR1000) program, ending the "
        "parallel development tracks of China's two nuclear corporations."
    ),
    "CAP1000": (
        "The CAP1000 is a Chinese adaptation of the Westinghouse AP1000 design, produced through "
        "technology transfer from the AP1000 units built at Sanmen and Haiyang. The CAP1000 "
        "represents China's localized version of the AP1000 with increasing domestic content, "
        "intended for subsequent domestic deployment beyond the initial AP1000 reference plants. "
        "Ten CAP1000 units have been ordered for Chinese sites."
    ),
    "CAP1400": (
        "The CAP1400 (also known as Guohe One) is a scaled-up Chinese development of the AP1000 "
        "passive safety concept, producing approximately 1,500 MW of electrical output. Developed "
        "by the State Nuclear Power Technology Corporation (SNPTC, now SPIC), the CAP1400 uses "
        "passive safety systems derived from the AP1000 but with a larger core and higher power "
        "output. The demonstration unit at Shidaowan (Rongcheng) is under construction."
    ),
    "ACP100": (
        "The ACP100 (Linglong One) is China's small modular reactor design, developed by CNNC. "
        "Producing approximately 125 MW of electrical output, it is a compact pressurized water "
        "reactor designed for deployment in remote areas, islands, and industrial heat applications. "
        "The demonstration unit at Changjiang in Hainan province is under construction and "
        "represents one of the world's most advanced land-based SMR construction projects."
    ),

    # =====================================================================
    # MAJOR BWR MODELS
    # =====================================================================
    "BWR-5": (
        "The BWR-5 is General Electric's fifth-generation boiling water reactor design, featuring "
        "improved emergency core cooling systems (ECCS) with high-pressure core spray and "
        "low-pressure core injection capabilities. Producing approximately 800-1,100 MW of "
        "electrical output, twenty BWR-5 units were built primarily in the United States and "
        "Japan. The BWR-5 was typically paired with Mark II containment (cylindrical suppression "
        "chamber beneath the drywell), though some units used other containment types."
    ),
    "BWR-5 (Mark 2)": (
        "The BWR-5 with Mark II containment combines GE's fifth-generation BWR with the second-"
        "generation containment design featuring a cylindrical suppression chamber directly "
        "beneath the drywell in an over-under arrangement. This configuration was deployed at "
        "several US and Japanese plants."
    ),
    "BWR-4 (Mark 1)": (
        "The BWR-4 with Mark I containment is the most widely deployed GE BWR configuration, "
        "featuring the distinctive inverted lightbulb-shaped drywell connected to a torus-shaped "
        "wetwell (suppression pool). Producing approximately 750-1,100 MW, this combination "
        "includes all six Fukushima Daiichi units. The Mark I containment's hydrogen management "
        "capability was a focus of post-Fukushima safety reviews worldwide. Despite this, many "
        "BWR-4/Mark I units continue to operate with post-Fukushima safety enhancements."
    ),
    "BWR-4 (Mark 2)": (
        "The BWR-4 with Mark II containment pairs the fourth-generation GE BWR with the improved "
        "cylindrical over-under suppression chamber design. This variant addressed some of the "
        "Mark I's design constraints with a simpler geometry and improved structural margins."
    ),
    "BWR-4": (
        "A generic designation for GE's fourth-generation boiling water reactor where the "
        "containment type is not further specified. The BWR-4 was GE's most widely deployed "
        "generation, with improvements to fuel design, control systems, and recirculation flow "
        "control over the earlier BWR-3."
    ),
    "BWR-6": (
        "The BWR-6 is General Electric's sixth and final generation of the classic BWR series, "
        "featuring a redesigned fuel bundle, improved control rod drives, and optimized core "
        "design. Producing approximately 1,100-1,400 MW, the BWR-6 was typically paired with "
        "the Mark III containment design and was deployed at a limited number of US plants "
        "including Clinton and Grand Gulf."
    ),
    "BWR-6 (Mark 3)": (
        "The BWR-6 with Mark III containment represents the most advanced configuration in GE's "
        "classic BWR series. The Mark III features a free-standing steel containment vessel "
        "surrounded by a concrete shield building, with a horizontal vent system for improved "
        "steam condensation. This configuration operates at Grand Gulf, Perry, Clinton, and "
        "River Bend in the United States."
    ),
    "BWR-3 (Mark 1)": (
        "The BWR-3 with Mark I containment is an early GE BWR configuration that introduced "
        "jet pump recirculation, eliminating the need for external recirculation piping and "
        "reducing the risk of large-break loss-of-coolant accidents. The BWR-3 was deployed at "
        "several US and Japanese plants, including early units at the Dresden and Fukushima "
        "Daiichi sites."
    ),
    "BWR-3": (
        "A generic designation for GE's third-generation BWR where the containment type is not "
        "further specified. The BWR-3 introduced internal jet pump recirculation — a major "
        "design advancement that became standard in all subsequent GE BWR generations."
    ),
    "BWR-2 (Mark 1)": (
        "The BWR-2 with Mark I containment is an early GE BWR configuration, preceding the "
        "introduction of jet pump recirculation in the BWR-3. BWR-2 units use external "
        "recirculation loops and represent some of the earliest commercial BWR deployments."
    ),
    "BWR-2": (
        "A generic designation for GE's second-generation BWR. The BWR-2 was an early "
        "commercial design that preceded the major recirculation system redesign introduced "
        "in the BWR-3."
    ),
    "BWR-1 (Mark 2)": (
        "The BWR-1 with Mark II containment designation covers first-generation GE BWR units "
        "with the cylindrical over-under suppression containment. BWR-1 units were among the "
        "very first commercial boiling water reactors, including the Big Rock Point and Humboldt "
        "Bay prototypes."
    ),
    "BWR-1": (
        "A generic designation for GE's first-generation commercial BWR. The BWR-1 was the "
        "earliest commercial boiling water reactor design, deployed at prototype and early "
        "commercial plants in the 1960s. Notable BWR-1 units include the Vallecitos experimental "
        "reactor and Dresden-1."
    ),
    "BWR": (
        "A generic BWR designation used for boiling water reactors where the specific GE "
        "generation number is not further specified in available records."
    ),
    "GE design": (
        "A generic designation for a GE-designed boiling water reactor where the specific model "
        "generation is not documented."
    ),
    "BWR with fossil fuel-fired superheater": (
        "The Indian Point-1 reactor, a unique GE BWR that used an oil-fired superheater to boost "
        "steam temperature and improve thermal efficiency. This hybrid nuclear-fossil design was "
        "a one-of-a-kind experiment that was not replicated. Indian Point-1 operated from 1962 to "
        "1974 before being permanently shut down."
    ),
    "Superheated steam reactor": (
        "The BONUS (BOiling NUclear Superheater) reactor in Puerto Rico was an experimental BWR "
        "that used an integral nuclear superheater zone within the reactor core to produce "
        "superheated steam, improving thermal efficiency without a separate fossil-fired "
        "superheater. The 16 MW unit operated from 1964 to 1968 as a technology demonstration."
    ),
    "Superheater": (
        "A designation for a reactor incorporating nuclear superheating — producing steam at "
        "temperatures above the saturation point within the reactor core or an auxiliary nuclear "
        "superheater zone. This concept was explored in several experimental reactors in the 1960s."
    ),
    "ABWR": (
        "The Advanced Boiling Water Reactor (ABWR) is a Generation III design jointly developed "
        "by GE, Hitachi, and Toshiba, producing approximately 1,350 MW of electrical output. "
        "The ABWR introduced reactor-internal recirculation pumps (eliminating external "
        "recirculation piping), a reinforced concrete containment vessel, and digital "
        "instrumentation. Kashiwazaki-Kariwa Units 6-7 (1996-1997) were the world's first "
        "Generation III reactors to achieve commercial operation. Eight ABWR units have been "
        "built in Japan, and the design was selected for units in Taiwan (construction suspended)."
    ),

    # =====================================================================
    # MAJOR BWR MODELS - ABB-ATOM / SWEDISH
    # =====================================================================
    "ABB-III, BWR-2500": (
        "The ABB-III BWR-2500 is the most advanced variant of ABB-Atom's Swedish BWR lineage, "
        "producing approximately 1,100 MW of electrical output and approximately 2,500 MW of "
        "thermal output. This design features internal recirculation pumps, fine-motion control "
        "rod drives, and a prestressed concrete containment with a condensation pool. The "
        "ABB-III BWR-2500 is deployed at Forsmark-3 and Oskarshamn-3 in Sweden."
    ),
    "ABB-III, BWR-3000": (
        "The ABB-III BWR-3000 is the largest ABB-Atom BWR variant, producing approximately "
        "1,170 MW of electrical output from approximately 3,000 MW thermal. This design is "
        "deployed at the Olkiluoto 1-2 units in Finland, ABB-Atom's primary export market."
    ),
    "ABB-II": (
        "The ABB-II designation covers the second generation of ABB-Atom's Swedish BWR designs, "
        "deployed at the Barsebäck and Ringhals sites in Sweden. These units feature internal "
        "recirculation pumps and ABB-Atom's characteristic prestressed concrete containment "
        "design."
    ),
    "ABB-I": (
        "The ABB-I designation covers the first generation of ASEA-Atom's commercial BWR designs, "
        "deployed at the Oskarshamn-1 and Ringhals-1 plants in Sweden. These early units "
        "established the Swedish BWR tradition of internal recirculation pumps and simplified "
        "reactor systems."
    ),

    # =====================================================================
    # MAJOR BWR MODELS - SIEMENS
    # =====================================================================
    "BWR-69": (
        "The BWR-69 is Siemens/KWU's boiling water reactor design for the German market, "
        "introducing internal recirculation pumps independently of the Swedish ABB-Atom approach. "
        "The BWR-69 designation refers to the 69-series design featuring fine-motion control rod "
        "drives and German-standard safety systems. Four units were built at Würgassen, "
        "Brunsbüttel, Philippsburg-1, and Isar-1 — all now permanently shut down as part of "
        "Germany's nuclear phase-out."
    ),
    "BWR-72": (
        "The BWR-72 is an upgraded Siemens/KWU BWR design (72-series), incorporating improvements "
        "over the BWR-69 including enhanced fuel management and safety systems. The BWR-72 was "
        "deployed at the Krümmel and Gundremmingen plants in Germany, both now permanently shut "
        "down."
    ),

    # =====================================================================
    # PHWR / CANDU MODELS
    # =====================================================================
    "CANDU 6": (
        "The CANDU 6 is the primary export model of Canada's pressurized heavy water reactor "
        "family, producing approximately 600-700 MW of electrical output. The CANDU 6 is a "
        "standardized single-unit design that has been deployed in Argentina (Embalse), Romania "
        "(Cernavodă), South Korea (Wolsong), Pakistan (KANUPP-2), and China (Qinshan III). The "
        "design features on-power refueling, natural uranium fuel capability, and a robust "
        "safety record. The Enhanced CANDU 6 (EC6) is offered for new construction with improved "
        "safety features."
    ),
    "CANDU": (
        "A generic CANDU designation for Canadian pressurized heavy water reactors where the "
        "specific model variant is not further specified."
    ),
    "CANDU 850": (
        "The CANDU 850 is a larger-output CANDU variant producing approximately 850 MW of "
        "electrical output, deployed at the Darlington Nuclear Generating Station in Ontario. "
        "The four Darlington units are among the most advanced CANDU reactors, with all four "
        "undergoing major refurbishment programs to extend their operational lives."
    ),
    "CANDU 750b": (
        "The CANDU 750b is a CANDU variant producing approximately 750 MW of electrical output, "
        "deployed at the Bruce Nuclear Generating Station in Ontario. The 'b' designation "
        "indicates the Bruce-B variant of this output class."
    ),
    "CANDU 750a": (
        "The CANDU 750a is a CANDU variant producing approximately 750 MW of electrical output, "
        "deployed at the Bruce Nuclear Generating Station. The 'a' designation indicates the "
        "Bruce-A variant."
    ),
    "CANDU 791": (
        "The CANDU 791 is a CANDU variant producing approximately 791 MW of electrical output, "
        "a specific sub-variant deployed at the Pickering or Bruce sites in Ontario."
    ),
    "CANDU 500b": (
        "The CANDU 500b is a CANDU variant producing approximately 500 MW of electrical output. "
        "The 'b' designation distinguishes this from the 500a variant, reflecting design "
        "differences between earlier and later 500 MW units."
    ),
    "CANDU 500a": (
        "The CANDU 500a is a CANDU variant producing approximately 500 MW of electrical output, "
        "deployed at the Pickering Nuclear Generating Station in Ontario."
    ),
    "CANDU 500A": (
        "An alternate designation for the CANDU 500a variant at the Pickering site, producing "
        "approximately 500 MW of electrical output."
    ),
    "CANDU 200": (
        "The CANDU 200 is the Douglas Point reactor, an early CANDU prototype producing "
        "approximately 200 MW of electrical output. As the first CANDU to generate electricity "
        "for the grid (1967), Douglas Point demonstrated the commercial viability of the "
        "pressurized heavy water reactor concept. The unit was shut down in 1984."
    ),
    "CANDU 137": (
        "The CANDU 137 designation refers to the Nuclear Power Demonstration (NPD) reactor at "
        "Rolphton, Ontario — the first CANDU prototype, producing approximately 22 MW of "
        "electrical output. Operational from 1962 to 1987, NPD proved the CANDU concept of "
        "horizontal pressure tubes with on-power refueling."
    ),
    "Horizontal pressure tube type": (
        "A generic designation for Indian pressurized heavy water reactors using the horizontal "
        "pressure tube configuration derived from CANDU technology. This designation covers "
        "India's 220 MW PHWR fleet at Rajasthan, Madras/Kalpakkam, Narora, Kakrapar, and "
        "Kaiga sites. India's PHWRs are indigenously designed and built by NPCIL, sharing "
        "the CANDU principle but with Indian-specific safety and containment designs."
    ),
    "PHWR-700": (
        "The PHWR-700 is India's most advanced indigenous pressurized heavy water reactor design, "
        "producing approximately 700 MW of electrical output. The PHWR-700 represents a "
        "significant scale-up from India's earlier 220 MW and 540 MW PHWR designs, with "
        "improved safety features and higher burnup fuel. Units have been built at Kakrapar "
        "and Rajasthan."
    ),
    "PHWR": (
        "A generic pressurized heavy water reactor designation where the specific model or "
        "output class is not further specified."
    ),

    # =====================================================================
    # LWGR / RBMK MODELS
    # =====================================================================
    "RBMK-1000": (
        "The RBMK-1000 is the standard Soviet graphite-moderated, water-cooled channel reactor, "
        "producing approximately 1,000 MW of electrical output. Eleven RBMK-1000 units were built "
        "at four sites in Russia and Ukraine (plus the four Chernobyl units). The RBMK-1000 at "
        "Chernobyl Unit 4 was the reactor involved in the 1986 disaster. Following extensive "
        "safety modifications — including changes to the control rod design to eliminate the "
        "positive scram effect and restrictions on low-power operation — Russia continues to "
        "operate modified RBMK-1000 units at Kursk, Leningrad, and Smolensk."
    ),
    "RBMK-1500": (
        "The RBMK-1500 is a scaled-up variant of the RBMK-1000, producing approximately 1,500 MW "
        "of electrical output — the most powerful individual reactor units ever built. Two "
        "RBMK-1500 units were built at the Ignalina Nuclear Power Plant in Lithuania. Both were "
        "shut down as a condition of Lithuania's EU accession (Unit 1 in 2004, Unit 2 in 2009), "
        "as the RBMK design was deemed non-upgradable to EU safety standards."
    ),
    "EGP-6": (
        "The EGP-6 is a small graphite-moderated, water-cooled reactor producing approximately "
        "12 MW of electrical output, designed for remote Arctic communities. Four EGP-6 units "
        "operated at the Bilibino Nuclear Power Plant in Chukotka, Russia's far northeast — one "
        "of the most remote nuclear power plants in the world. The EGP-6 provided both "
        "electricity and district heating to the town of Bilibino. The units have been "
        "progressively shut down as the floating Akademik Lomonosov replaced them."
    ),
    "AM-1": (
        "The AM-1 (Atom Mirny, 'Peaceful Atom') at Obninsk was the world's first nuclear power "
        "plant to generate electricity for a grid, achieving criticality on June 26, 1954 and "
        "producing 5 MW of electrical output. The AM-1 used a graphite moderator with liquid "
        "metal (bismuth) and water cooling — a unique design that was not replicated for "
        "commercial power. It operated until 2002 and is now a museum and historical landmark."
    ),
    "AMB-100": (
        "The AMB-100 (Atom Mirny Bolshoy, 'Large Peaceful Atom') was a Soviet graphite-moderated, "
        "water-cooled reactor producing approximately 100 MW of electrical output at the Beloyarsk "
        "Nuclear Power Plant. Operational from 1964 to 1981, it was an early Soviet power reactor "
        "that served as a technology demonstrator for the RBMK concept."
    ),
    "AMB-200": (
        "The AMB-200 was a scaled-up version of the AMB-100 at Beloyarsk, producing approximately "
        "200 MW of electrical output. Operational from 1967 to 1989, the AMB-200 was part of the "
        "Soviet program to develop large graphite-moderated reactors that eventually led to the "
        "RBMK series."
    ),
    "SGR": (
        "The SGR (Steam Generating Reactor) designation refers to the AM-1 reactor at Obninsk, "
        "also known as the Soviet Graphite Reactor. This was the world's first nuclear power "
        "plant, using a unique combination of graphite moderation and liquid metal cooling that "
        "was classified under the LMGMR (Liquid Metal Graphite Moderated Reactor) technology type."
    ),

    # =====================================================================
    # FBR MODELS
    # =====================================================================
    "BN-600": (
        "The BN-600 is a Soviet/Russian sodium-cooled fast breeder reactor producing approximately "
        "600 MW of electrical output at the Beloyarsk Nuclear Power Plant. Operational since 1980, "
        "the BN-600 is one of the longest-running fast reactors in the world and has compiled an "
        "excellent operating record. It uses a pool-type primary circuit with the reactor core, "
        "primary pumps, and intermediate heat exchangers all contained within a single vessel."
    ),
    "BN-800": (
        "The BN-800 is Russia's most advanced operating fast breeder reactor, producing "
        "approximately 880 MW of electrical output at Beloyarsk. Operational since 2016, the "
        "BN-800 is the world's most powerful fast neutron reactor and serves as a technology "
        "demonstrator for MOX fuel and minor actinide transmutation. It is the reference design "
        "for the planned BN-1200M commercial fast reactor."
    ),
    "BN-350": (
        "The BN-350 was a Soviet sodium-cooled fast breeder reactor at Aktau (Shevchenko), "
        "Kazakhstan, that uniquely served dual purposes: producing approximately 150 MW of "
        "electrical output and desalinating seawater for the city. Operational from 1973 to 1999, "
        "the BN-350 was one of the world's first fast reactors to operate at commercial scale "
        "and provided decades of operating experience with sodium-cooled technology."
    ),
    "BN-20": (
        "The BN-20 designation refers to the early experimental Soviet fast reactor BR-5/BR-10 "
        "at Obninsk, which produced approximately 5-10 MW of thermal output. This small research "
        "reactor provided fundamental experience with sodium-cooled fast reactor technology that "
        "informed the design of the larger BN-350, BN-600, and BN-800."
    ),
    "CFR-600": (
        "The CFR-600 (China Fast Reactor 600) is China's demonstration sodium-cooled fast reactor "
        "currently under construction at the Xiapu Nuclear Power Plant in Fujian province. "
        "Producing approximately 600 MW of electrical output, the CFR-600 is designed to "
        "demonstrate commercial-scale fast breeder technology and advance China's closed nuclear "
        "fuel cycle strategy. Two units are under construction."
    ),
    "Prototype (FBR)": (
        "A generic designation for prototype and demonstration fast breeder reactors worldwide. "
        "This category covers early fast reactor experiments including France's Rapsodie and "
        "Phénix, the UK's Dounreay Fast Reactor (DFR) and Prototype Fast Reactor (PFR), the "
        "US's Experimental Breeder Reactors (EBR-I, EBR-II), and other national fast reactor "
        "programs. These prototypes were essential in proving the viability of fast neutron "
        "reactor technology."
    ),
    "DFR": (
        "The Dounreay Fast Reactor (DFR) was the UK's first fast reactor, located at the "
        "Dounreay site in Caithness, Scotland. Using a sodium-potassium (NaK) alloy as coolant, "
        "the DFR operated from 1959 to 1977 as a research and demonstration facility, producing "
        "approximately 15 MW of electrical output. It was followed by the larger Prototype Fast "
        "Reactor (PFR)."
    ),
    "PFR": (
        "The Prototype Fast Reactor (PFR) at Dounreay, Scotland, was the UK's second and larger "
        "fast reactor, producing approximately 250 MW of electrical output using liquid sodium "
        "coolant. Operational from 1975 to 1994, the PFR demonstrated the pool-type fast reactor "
        "concept and provided extensive experience with sodium-cooled technology. The PFR program "
        "was cancelled as part of the UK's decision not to pursue commercial fast reactors."
    ),
    "Na-1200": (
        "The Na-1200 designation refers to France's Superphénix, a 1,200 MW sodium-cooled fast "
        "breeder reactor at Creys-Malville — the world's largest fast reactor ever built. "
        "Operational from 1986 to 1997, Superphénix suffered from sodium leaks, political "
        "opposition, and technical problems. Its closure marked the end of France's fast breeder "
        "program, though the operating experience informed subsequent international fast reactor "
        "designs."
    ),
    "PH-250": (
        "The PH-250 designation refers to France's Phénix fast reactor at Marcoule, producing "
        "approximately 250 MW of electrical output. Operational from 1973 to 2009, Phénix was "
        "one of the longest-operating fast reactors in the world and served as the prototype for "
        "Superphénix. In its later years, Phénix was used for transmutation experiments, "
        "demonstrating the potential to reduce the volume and toxicity of nuclear waste."
    ),
    "Monju": (
        "Monju was Japan's prototype sodium-cooled fast breeder reactor, producing approximately "
        "280 MW of electrical output at Tsuruga in Fukui Prefecture. Named after the Buddhist "
        "deity of wisdom, Monju achieved criticality in 1994 but suffered a major sodium leak and "
        "fire in 1995, just four months after reaching initial power. The reactor remained shut "
        "down for most of its life and was permanently decommissioned in 2017, ending Japan's "
        "fast breeder program."
    ),
    "Liquid Metal FBR": (
        "A generic designation for a liquid metal-cooled fast breeder reactor where the specific "
        "model is not further specified. This typically refers to early prototype fast reactors "
        "using sodium or sodium-potassium coolant."
    ),

    # =====================================================================
    # HTGR MODELS
    # =====================================================================
    "HTR-PM": (
        "The HTR-PM (High Temperature Reactor - Pebble bed Module) at the Shidaowan Nuclear "
        "Power Plant in Shandong province is the world's first commercial high-temperature "
        "gas-cooled reactor, achieving commercial operation in 2023. The plant uses a twin-module "
        "design where two 250 MW thermal pebble bed reactor modules drive a single 210 MW steam "
        "turbine-generator. Each reactor module contains approximately 400,000 spherical fuel "
        "pebbles with TRISO-coated uranium particles, using helium gas as the coolant.\n\n"
        "The HTR-PM demonstrates the commercial viability of pebble bed HTGR technology and is "
        "the culmination of decades of development tracing back to Germany's AVR and THTR-300 "
        "experimental reactors. China plans to scale up the concept with the HTR-PM600, using "
        "six reactor modules driving a single large turbine."
    ),
    "Pebble bed prototype": (
        "A designation for pebble bed HTGR prototypes, including Germany's AVR (Arbeitsgemeinschaft "
        "Versuchsreaktor) at Jülich, which operated from 1967 to 1988 at 15 MW electrical output. "
        "The AVR pioneered the pebble bed fuel concept where spherical fuel elements circulate "
        "continuously through the reactor core. The AVR's operating experience and the subsequent "
        "THTR-300 demonstration plant provided the technological foundation for China's HTR-PM."
    ),
    "Pebble bed reactor": (
        "A generic designation for pebble bed high-temperature gas-cooled reactors using TRISO-"
        "coated fuel particles encased in graphite spheres (pebbles) that flow through the "
        "reactor core. The pebble bed concept allows continuous refueling and inherent safety "
        "through the fuel's ability to retain fission products at very high temperatures."
    ),

    # =====================================================================
    # HWGCR MODELS
    # =====================================================================
    "MONTS-D'ARREE": (
        "The Monts d'Arrée reactor (EL-4, later renamed Brennilis) was a French heavy water "
        "gas-cooled reactor prototype at Brennilis in Brittany, producing approximately 70 MW "
        "of electrical output. Operational from 1967 to 1985, it used heavy water as moderator "
        "and CO₂ gas as coolant. The reactor demonstrated the HWGCR concept but France "
        "subsequently adopted PWR technology exclusively."
    ),
    "KS 150": (
        "The KS 150 (also designated A-1) was a Czechoslovak heavy water gas-cooled reactor at "
        "Jaslovské Bohunice, producing approximately 143 MW of electrical output. The reactor "
        "suffered a serious fuel damage accident in 1977 and was permanently shut down. The "
        "incident led Czechoslovakia to abandon the HWGCR concept in favor of Soviet VVER "
        "technology."
    ),
    "Pressure tube reactor": (
        "A generic designation for a heavy water gas-cooled reactor using a pressure tube "
        "configuration. This type combines heavy water moderation with gas cooling in individual "
        "pressure tubes rather than a pressure vessel."
    ),
    "HWGCR: 2-loops": (
        "A two-loop heavy water gas-cooled reactor variant. The two-loop configuration was used "
        "in experimental HWGCR designs, with separate primary coolant circuits for redundancy."
    ),

    # =====================================================================
    # HWLWR MODELS
    # =====================================================================
    "HW BLWR 250": (
        "A heavy water boiling light water reactor producing approximately 250 MW of thermal "
        "output. This designation typically refers to early experimental designs that combined "
        "heavy water moderation with boiling light water coolant, exploring hybrid concepts "
        "before the industry standardized on conventional reactor types."
    ),
    "ATR": (
        "The Advanced Thermal Reactor (ATR) was Japan's Fugen prototype, a heavy water moderated, "
        "light water cooled reactor at Tsuruga in Fukui Prefecture. Producing approximately "
        "165 MW of electrical output, Fugen operated from 1979 to 2003 and was designed to use "
        "plutonium-bearing MOX fuel in a thermal reactor. Japan abandoned the ATR concept in "
        "favor of conventional LWR technology for MOX fuel utilization."
    ),

    # =====================================================================
    # SMR / SPECIAL MODELS
    # =====================================================================
    "CAREM Prototype": (
        "CAREM (Central Argentina de Elementos Modulares) is Argentina's indigenous small modular "
        "reactor, a 32 MW electrical output integral PWR currently under construction at the "
        "Atucha site. CAREM features an integrated primary circuit with the steam generators "
        "located inside the reactor pressure vessel, natural circulation for primary cooling, "
        "and passive safety systems. When completed, CAREM will be one of the first SMR "
        "prototypes to achieve operation."
    ),
    "\"25\"": (
        "A designation for reactors with approximately 25 MW of electrical output, typically "
        "referring to small prototype or demonstration units from the early era of nuclear "
        "power development."
    ),
}


def run(apply=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get existing models from DB
    cur.execute("SELECT name FROM models ORDER BY name")
    db_models = {row[0] for row in cur.fetchall()}

    # Check coverage
    described = set(MODEL_DESCRIPTIONS.keys())
    missing = db_models - described
    extra = described - db_models

    print(f"DB models: {len(db_models)}")
    print(f"Descriptions written: {len(described)}")
    print(f"Missing descriptions: {len(missing)}")
    if missing:
        for m in sorted(missing):
            print(f"  ! {m}")
    if extra:
        print(f"Extra (not in DB): {len(extra)}")
        for m in sorted(extra):
            print(f"  ? {m}")

    print(f"\n{'Inserting' if apply else 'Would insert'} {len(described & db_models)} model descriptions\n")

    count = 0
    for name, desc in sorted(MODEL_DESCRIPTIONS.items()):
        if name not in db_models:
            continue
        if apply:
            cur.execute(
                "INSERT OR REPLACE INTO entity_descriptions (entity_type, entity_name, description, source) VALUES (?, ?, ?, ?)",
                ("model", name, desc, "Wikipedia, WNA, IAEA — AI-reviewed")
            )
        count += 1

    if apply:
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM entity_descriptions WHERE entity_type = 'model'")
        print(f"Verification: {cur.fetchone()[0]} model descriptions in DB")
        cur.execute("SELECT COUNT(*) FROM entity_descriptions")
        print(f"Total descriptions in DB: {cur.fetchone()[0]}")

    print(f"\nProcessed {count} models")
    conn.close()


if __name__ == "__main__":
    run("--apply" in sys.argv)
