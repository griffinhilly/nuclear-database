#!/usr/bin/env python3
"""De-emphasize containment in model descriptions.

Containment type is now a data field in reactor/model detail tables,
so descriptions should focus on reactor design characteristics instead.
"""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

UPDATED_DESCRIPTIONS = {
    "B&W (L-loop) DRYAMB": (
        "A Babcock & Wilcox lowered-loop PWR featuring B&W's distinctive once-through "
        "steam generators (OTSGs), which produce superheated steam for higher thermodynamic "
        "efficiency. The lowered-loop configuration places the steam generators below the "
        "reactor vessel, using gravity-assisted natural circulation for emergency cooling."
    ),
    "BWR-1 (Mark 2)": (
        "First-generation GE boiling water reactor units, among the very first commercial "
        "BWRs including Big Rock Point and Humboldt Bay. These early prototypes established "
        "the fundamental BWR concept of generating steam directly in the reactor vessel, "
        "eliminating the need for separate steam generators."
    ),
    "BWR-2 (Mark 1)": (
        "An early GE BWR configuration preceding the introduction of jet pump recirculation "
        "in the BWR-3. BWR-2 units use external recirculation loops and represent some of "
        "the earliest commercial BWR deployments."
    ),
    "BWR-3": (
        "GE's third-generation boiling water reactor, which introduced internal jet pump "
        "recirculation — a major design advancement that became standard in all subsequent "
        "GE BWR generations. Jet pumps eliminated large external recirculation piping, "
        "reducing the risk of large-break loss-of-coolant accidents."
    ),
    "BWR-3 (Mark 1)": (
        "A GE third-generation BWR that introduced jet pump recirculation, eliminating "
        "the need for external recirculation piping and reducing the risk of large-break "
        "loss-of-coolant accidents. The BWR-3 was deployed at several US and Japanese "
        "plants, including early units at the Dresden and Fukushima Daiichi sites."
    ),
    "BWR-4": (
        "GE's fourth-generation boiling water reactor and its most widely deployed "
        "generation, with improvements to fuel design, control systems, and recirculation "
        "flow control over the earlier BWR-3. BWR-4 units typically produce 750-1,100 MW "
        "of electrical output."
    ),
    "BWR-4 (Mark 1)": (
        "The most widely deployed GE BWR configuration, producing approximately 750-1,100 MW. "
        "This combination includes all six Fukushima Daiichi units. Post-Fukushima safety "
        "reviews focused on hydrogen management and severe accident mitigation for this "
        "configuration. Despite this, many BWR-4 units continue to operate with enhanced "
        "safety modifications."
    ),
    "BWR-4 (Mark 2)": (
        "A fourth-generation GE BWR variant deployed at several US and Japanese plants. "
        "The BWR-4 improved fuel design and recirculation flow control over the earlier "
        "BWR-3 generation."
    ),
    "BWR-5": (
        "General Electric's fifth-generation boiling water reactor, featuring improved "
        "emergency core cooling systems (ECCS) with high-pressure core spray and low-pressure "
        "core injection capabilities. Producing approximately 800-1,100 MW of electrical "
        "output, twenty BWR-5 units were built primarily in the United States and Japan."
    ),
    "BWR-5 (Mark 2)": (
        "A GE fifth-generation BWR with improved emergency core cooling systems including "
        "high-pressure core spray and low-pressure core injection. This configuration was "
        "deployed at several US and Japanese plants."
    ),
    "BWR-6": (
        "General Electric's sixth and final generation of the classic BWR series, featuring "
        "a redesigned fuel bundle, improved control rod drives, and optimized core design. "
        "Producing approximately 1,100-1,400 MW, the BWR-6 was deployed at a limited number "
        "of US plants including Clinton and Grand Gulf."
    ),
    "BWR-6 (Mark 3)": (
        "The most advanced configuration in GE's classic BWR series, featuring a redesigned "
        "fuel bundle, improved control rod drives, and optimized core design producing "
        "approximately 1,100-1,400 MW. This configuration operates at Grand Gulf, Perry, "
        "Clinton, and River Bend in the United States."
    ),
    "CE (2-loop)": (
        "A Combustion Engineering two-loop PWR featuring CE's characteristic 2x4 loop "
        "arrangement — two hot legs and four cold legs — with two large steam generators. "
        "CE two-loop units produce approximately 800-1,300 MW of electrical output "
        "depending on the specific design generation."
    ),
    "CE (2-loop) DRYAMB": (
        "A Combustion Engineering two-loop PWR featuring CE's characteristic 2x4 loop "
        "arrangement — two hot legs and four cold legs — with two large steam generators. "
        "This configuration produces approximately 800-900 MW of electrical output. "
        "CE two-loop units are deployed at Calvert Cliffs, Millstone, St. Lucie, and "
        "Waterford in the United States."
    ),
    "CE DRYAMB": (
        "A Combustion Engineering PWR distinguished by its 2x4 primary loop arrangement "
        "and larger-diameter reactor vessels compared to Westinghouse designs. CE PWRs "
        "were deployed at major US plants and served as the technological foundation for "
        "South Korea's nuclear program."
    ),
    "CE80 DRYAMB": (
        "Combustion Engineering's most advanced domestic PWR design, featuring an optimized "
        "core design and enhanced safety systems. The System 80 units at Palo Verde in "
        "Arizona — the largest nuclear generating station in the Western Hemisphere with "
        "three units — are the flagship deployment. The System 80 served as the basis for "
        "South Korea's OPR-1000 and ultimately the APR1400."
    ),
    "PRE KONVOI": (
        "The Pre-Konvoi designation covers the generation of Siemens/KWU four-loop PWRs "
        "built immediately before the standardized Konvoi series, including units at Grohnde, "
        "Philippsburg-2, and Brokdorf. These reactors share the characteristic KWU design "
        "philosophy with some variation between units, and achieved excellent operating "
        "performance."
    ),
    # V-213: keep bubble condenser mention but reframe as safety upgrade, not containment focus
    "VVER V-213": (
        "The VVER V-213 is the improved variant of the VVER-440 reactor, developed with "
        "enhanced safety features including a bubble condenser pressure suppression system "
        "— a significant upgrade over the earlier V-230 model. The V-213 produces "
        "approximately 440 MW of electrical output and has been deployed in Russia, "
        "Czech Republic, Slovakia, Hungary, and Finland (Loviisa, with Western safety "
        "upgrades). The V-213 is the most commonly operating VVER-440 variant."
    ),
    # V-230: containment absence IS the story — keep but slightly reframe
    "VVER V-230": (
        "The VVER V-230 is the original VVER-440 reactor model, built in the 1960s-1970s "
        "without a full pressure-rated safety enclosure — a feature that became a significant "
        "safety concern after Western standards were applied following the end of the Cold War. "
        "EU accession requirements led to the closure of V-230 units in Bulgaria, Lithuania, "
        "and Slovakia, though some continue to operate in Russia and Armenia."
    ),
}


def run(apply=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    count = 0
    for name, desc in sorted(UPDATED_DESCRIPTIONS.items()):
        cur.execute(
            "SELECT description FROM entity_descriptions WHERE entity_type = 'model' AND entity_name = ?",
            (name,)
        )
        row = cur.fetchone()
        if not row:
            print(f"  SKIP {name}: not found in DB")
            continue

        old_len = len(row[0])
        new_len = len(desc)
        if apply:
            cur.execute(
                "UPDATE entity_descriptions SET description = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE entity_type = 'model' AND entity_name = ?",
                (desc, name)
            )
            print(f"  Updated {name}: {old_len} -> {new_len} chars")
        else:
            print(f"  Would update {name}: {old_len} -> {new_len} chars")
        count += 1

    if apply:
        conn.commit()

    print(f"\n{'Updated' if apply else 'Would update'} {count} model descriptions")
    conn.close()


if __name__ == "__main__":
    run("--apply" in sys.argv)
