#!/usr/bin/env python3
"""
Migration: Create entity_descriptions table and populate with containment type + status descriptions.

Usage:
    python add_descriptions.py          # Dry run (shows what would happen)
    python add_descriptions.py --apply  # Actually create table and insert data
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

# =============================================================================
# DESCRIPTION DATA
# =============================================================================

CONTAINMENT_DESCRIPTIONS = {
    "Large Dry": (
        "The most common containment design worldwide, consisting of a large reinforced concrete "
        "or prestressed concrete structure with a steel liner. Large dry containments maintain "
        "atmospheric pressure under normal operation and are designed to withstand the full pressure "
        "and temperature transients of a design-basis loss-of-coolant accident (LOCA) without "
        "requiring active pressure suppression systems. Typical internal free volumes range from "
        "50,000 to 90,000 cubic meters, providing substantial margin for steam absorption."
    ),
    "Large Dry (Double)": (
        "A reinforced variant of the large dry containment featuring two concentric containment "
        "structures: an inner prestressed concrete shell with a steel liner and an outer reinforced "
        "concrete shield building. The annular space between the two shells is maintained at "
        "sub-atmospheric pressure to capture any leakage from the inner containment, providing an "
        "additional barrier against radioactive release. This design is standard for French PWRs "
        "and has been widely adopted in countries licensing Framatome/EDF reactor designs."
    ),
    "Mark I": (
        "The earliest GE boiling water reactor containment design, featuring a distinctive inverted "
        "lightbulb-shaped drywell connected to a torus-shaped wetwell (suppression pool) at its "
        "base. During a LOCA, steam from the drywell is directed through downcomers into the "
        "suppression pool, where it condenses, limiting containment pressure. Deployed on BWR/1 "
        "through BWR/4 designs from the 1960s-70s, the Mark I is the containment type involved in "
        "the 2011 Fukushima Daiichi accident, which prompted global reviews of its hydrogen venting "
        "capabilities."
    ),
    "Mark II": (
        "The second-generation GE BWR containment design, replacing the Mark I's torus-shaped "
        "suppression pool with a cylindrical suppression chamber located directly beneath the "
        "drywell. This over-under arrangement simplifies construction and reduces the building "
        "footprint while maintaining the pressure suppression principle. Deployed primarily on "
        "BWR/5 reactors in the late 1970s and 1980s."
    ),
    "Spherical Double": (
        "A containment design using a spherical steel primary containment vessel surrounded by a "
        "reinforced concrete secondary structure. The spherical geometry provides optimal resistance "
        "to internal pressure loads, allowing thinner walls for a given design pressure. This design "
        "is characteristic of German Konvoi-type and pre-Konvoi PWRs built by KWU (Kraftwerk Union), "
        "and is also used in some Spanish and Argentine reactors derived from German designs."
    ),
    "Pressure Suppression": (
        "A containment concept that uses a large pool of water to condense steam released during a "
        "loss-of-coolant accident, thereby limiting the peak containment pressure. Unlike the GE "
        "Mark series, this general category covers non-GE pressure suppression designs including "
        "those used in VVER and RBMK reactor buildings, where steam is routed through bubbler "
        "condenser trays or suppression pools to reduce post-accident pressure."
    ),
    "Ice Condenser": (
        "A pressure suppression containment variant that uses large baskets of ice (borated water "
        "frozen into ice beds) to absorb heat and condense steam during an accident, rather than a "
        "water suppression pool. The ice condenser design allows a significantly smaller containment "
        "volume compared to large dry designs while achieving comparable pressure ratings. Used in "
        "several Westinghouse PWR plants in the United States and the Loviisa VVER plant in Finland."
    ),
    "Mark III": (
        "The third-generation GE BWR containment design, used with BWR/6 reactors. The Mark III "
        "features a free-standing steel containment vessel surrounded by a reinforced concrete "
        "shield building, with a suppression pool in an annular configuration around the drywell. "
        "It incorporates a horizontal vent system connecting the drywell to the suppression pool, "
        "providing improved steam condensation performance over earlier Mark designs."
    ),
    "Subatmospheric": (
        "A variant of the large dry containment design that maintains the containment atmosphere "
        "at below-atmospheric pressure (typically around 10 psia) during normal operation. This "
        "negative pressure differential ensures that any leakage path would draw air inward rather "
        "than releasing radioactive material outward. Used at several Westinghouse PWR plants in "
        "the United States, including Surry and North Anna."
    ),
}

STATUS_DESCRIPTIONS = {
    "Operational": (
        "The reactor has been connected to the electrical grid and is available for electricity "
        "generation. This is the IAEA PRIS standard definition, beginning from the date of first "
        "grid connection through the commercial operation lifetime of the unit."
    ),
    "Under Construction": (
        "Construction of the reactor has formally begun, defined by the IAEA as the date of first "
        "concrete pour for the reactor building basemat. This milestone marks the transition from "
        "site preparation to nuclear-grade construction."
    ),
    "Permanent Shutdown": (
        "The reactor has been permanently removed from service with no intention to restart. The "
        "shutdown may result from end-of-license-life, economic decisions, policy changes, or "
        "post-accident decommissioning. Once declared permanently shut down, the unit enters the "
        "decommissioning process."
    ),
    "Suspended": (
        "The reactor's construction or operation has been suspended indefinitely. For units under "
        "construction, this typically reflects political or financial decisions to halt building. "
        "For operating units, it indicates the IAEA status 'Suspended Operation' — the reactor is "
        "not generating but has not been declared permanently shut down."
    ),
}


def run_migration(apply=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if table already exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entity_descriptions'")
    exists = cur.fetchone() is not None

    if exists:
        cur.execute("SELECT COUNT(*) FROM entity_descriptions")
        count = cur.fetchone()[0]
        print(f"Table 'entity_descriptions' already exists with {count} rows.")
        if not apply:
            print("Use --apply to drop and recreate.")
            conn.close()
            return
        print("Dropping and recreating...")
        cur.execute("DROP TABLE entity_descriptions")

    # Create table
    print("\nCreating entity_descriptions table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entity_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            description TEXT NOT NULL,
            source TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(entity_type, entity_name)
        )
    """)

    # Insert containment descriptions
    print(f"\nInserting {len(CONTAINMENT_DESCRIPTIONS)} containment type descriptions...")
    for name, desc in CONTAINMENT_DESCRIPTIONS.items():
        if apply:
            cur.execute(
                "INSERT OR REPLACE INTO entity_descriptions (entity_type, entity_name, description, source) VALUES (?, ?, ?, ?)",
                ("containment", name, desc, "AI-generated from engineering references")
            )
        print(f"  + {name}")

    # Insert status descriptions
    print(f"\nInserting {len(STATUS_DESCRIPTIONS)} status descriptions...")
    for name, desc in STATUS_DESCRIPTIONS.items():
        if apply:
            cur.execute(
                "INSERT OR REPLACE INTO entity_descriptions (entity_type, entity_name, description, source) VALUES (?, ?, ?, ?)",
                ("status", name, desc, "IAEA PRIS definitions")
            )
        print(f"  + {name}")

    if apply:
        conn.commit()
        # Verify
        cur.execute("SELECT entity_type, COUNT(*) FROM entity_descriptions GROUP BY entity_type")
        print("\n=== Verification ===")
        total = 0
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} descriptions")
            total += row[1]
        print(f"  Total: {total} descriptions")
    else:
        print("\n[DRY RUN] No changes made. Use --apply to execute.")

    conn.close()


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    run_migration(apply=apply)
