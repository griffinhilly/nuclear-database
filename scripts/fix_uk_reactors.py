#!/usr/bin/env python3
"""Fix architect_engineer and constructor for UK nuclear reactors.

Research sources:
- World Nuclear Association: Nuclear Development in the United Kingdom
- Wikipedia articles for individual UK nuclear stations
- Graces Guide entries for UK nuclear consortia
- NIA article: "Delivering Sizewell B"

UK nuclear construction history:
  The UK's Magnox stations were built under turnkey contracts by industrial
  consortia, which served as both constructor and architect-engineer:
    - AEI-John Thompson Nuclear Energy Co. (Berkeley, 1956-57)
    - Nuclear Power Plant Co. (NPPC) (Bradwell, 1956-57)
    - GEC/Simon Carves (Hunterston A, 1956-57)
    - English Electric/Babcock & Wilcox/Taylor Woodrow (Hinkley Point A, 1957)
    - Atomic Power Constructions (APC) (Trawsfynydd, 1959)
  In 1960, AEI-JT + NPPC merged -> The Nuclear Power Group (TNPG)
  In 1965, English Electric consortium -> Nuclear Design & Construction (NDC)
  In 1968, NDC + GEC -> British Nuclear Design & Construction (BNDC)
  In 1973, TNPG + BNDC merged -> National Nuclear Corporation (NNC)

  AGR stations were ordered 1965-1980:
    - Dungeness B: APC (1965), then BNDC after APC collapsed (1969)
    - Hinkley Point B, Hunterston B: TNPG (1967)
    - Hartlepool, Heysham A: BNDC (1967-1970)
    - Heysham B, Torness: NNC (1979-1980)
    - Windscale AGR (Sellafield 5): UKAEA prototype (1958-1962)

  UKAEA stations (Calder Hall, Chapelcross, Dounreay, Winfrith, Windscale AGR)
  were designed and built by the UKAEA directly.

  Sizewell B: CEGB was architect-engineer, Nuclear Electric (successor to CEGB)
  was the constructor/project manager.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nuclear_reactors.db")


def fix_uk_reactors():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all UK reactors
    cur.execute(
        """
        SELECT r.id, r.plant_name, r.unit_number, r.design_series,
               rd.constructor, rd.architect_engineer
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        LEFT JOIN reactor_details rd ON r.id = rd.reactor_id
        WHERE c.name = 'UK'
        ORDER BY r.plant_name, r.unit_number
    """
    )
    reactors = cur.fetchall()

    updates = []

    for rx in reactors:
        rid = rx["id"]
        plant = rx["plant_name"]
        unit = rx["unit_number"]
        design = rx["design_series"]
        old_constructor = rx["constructor"]
        old_ae = rx["architect_engineer"]

        new_constructor = old_constructor  # default: keep existing
        new_ae = None

        # ── UKAEA-built stations ──────────────────────────────────────
        # Calder Hall (Sellafield 1-4), Chapelcross, Dounreay DFR/PFR,
        # Winfrith SGHWR: all designed and built by UKAEA
        if plant == "Sellafield" and str(unit) in ("1", "2", "3", "4"):
            new_constructor = "UKAEA"
            new_ae = "UKAEA"

        elif plant == "Chapelcross":
            new_constructor = "UKAEA"
            new_ae = "UKAEA"

        elif plant == "Dounreay DFR":
            new_constructor = "UKAEA"
            new_ae = "UKAEA"

        elif plant == "Dounreay PFR":
            new_constructor = "UKAEA"
            new_ae = "UKAEA"

        elif plant == "Winfrith":
            new_constructor = "UKAEA"
            new_ae = "UKAEA"

        # Windscale AGR prototype (Sellafield unit 5)
        # Built by UKAEA with Mitchell Construction as civil contractor
        elif plant == "Sellafield" and str(unit) == "5":
            new_constructor = "UKAEA"
            new_ae = "UKAEA"

        # ── Magnox consortia stations ─────────────────────────────────
        # Berkeley: AEI-John Thompson Nuclear Energy Co. (pre-TNPG)
        elif plant == "Berkeley":
            new_constructor = "AEI-John Thompson Nuclear Energy Co."
            new_ae = "AEI-John Thompson Nuclear Energy Co."

        # Bradwell: Nuclear Power Plant Co. (NPPC) (pre-TNPG)
        elif plant == "Bradwell":
            new_constructor = "Nuclear Power Plant Co. (NPPC)"
            new_ae = "Nuclear Power Plant Co. (NPPC)"

        # Hunterston A: GEC/Simon Carves consortium
        elif plant == "Hunterston A":
            new_constructor = "GEC"
            new_ae = "GEC"

        # Hinkley Point A: English Electric/Babcock & Wilcox/Taylor Woodrow
        # DB had APC which is wrong
        elif plant == "Hinkley Point A":
            new_constructor = "English Electric"
            new_ae = "English Electric"

        # Trawsfynydd: Atomic Power Constructions (APC)
        elif plant == "Trawsfynydd":
            new_constructor = "APC"
            new_ae = "APC"

        # Dungeness A: TNPG
        elif plant == "Dungeness A":
            new_constructor = "TNPG"
            new_ae = "TNPG"

        # Sizewell A: BNDC (English Electric/Babcock & Wilcox/Taylor Woodrow)
        # Contract awarded Nov 1960 to BNDC (then still called NDC)
        # DB had TNPG which is wrong
        elif plant == "Sizewell A":
            new_constructor = "BNDC"
            new_ae = "BNDC"

        # Oldbury: TNPG
        elif plant == "Oldbury":
            new_constructor = "TNPG"
            new_ae = "TNPG"

        # Wylfa: BNDC (English Electric consortium, by then reorganized as BNDC)
        # Construction began 1963 under BNDC
        elif plant == "Wylfa":
            new_constructor = "BNDC"
            new_ae = "BNDC"

        # ── AGR stations ──────────────────────────────────────────────
        # Dungeness B: Originally APC (1965), APC collapsed 1969,
        # BNDC took over as main contractor
        elif plant == "Dungeness B":
            new_constructor = "APC/BNDC"
            new_ae = "APC/BNDC"

        # Hinkley Point B: TNPG (ordered 1967)
        elif plant == "Hinkley Point B":
            new_constructor = "TNPG"
            new_ae = "TNPG"

        # Hunterston B: TNPG (ordered 1967)
        elif plant == "Hunterston B":
            new_constructor = "TNPG"
            new_ae = "TNPG"

        # Hartlepool: BNDC (ordered 1967 as NDC, became BNDC 1968)
        elif plant == "Hartlepool":
            new_constructor = "BNDC"
            new_ae = "BNDC"

        # Heysham A: BNDC (ordered 1970)
        elif plant == "Heysham A":
            new_constructor = "BNDC"
            new_ae = "BNDC"

        # Heysham B: NNC (ordered 1979)
        elif plant == "Heysham B":
            new_constructor = "NNC"
            new_ae = "NNC"

        # Torness: NNC (ordered 1980)
        elif plant == "Torness":
            new_constructor = "NNC"
            new_ae = "NNC"

        # ── PWR ───────────────────────────────────────────────────────
        # Sizewell B: Nuclear Electric was constructor/project manager,
        # CEGB (later Nuclear Electric) served as architect-engineer
        elif plant == "Sizewell B":
            new_constructor = "Nuclear Electric"
            new_ae = "Nuclear Electric"

        # ── EPR (Hinkley Point C) ─────────────────────────────────────
        # Already has correct data, skip
        elif plant == "Hinkley Point C":
            continue

        else:
            print(f"  WARNING: No mapping for {plant} unit {unit} (id={rid})")
            continue

        # Track changes
        constructor_changed = new_constructor != old_constructor
        ae_changed = new_ae != old_ae

        if constructor_changed or ae_changed:
            updates.append(
                {
                    "id": rid,
                    "plant": plant,
                    "unit": unit,
                    "old_constructor": old_constructor,
                    "new_constructor": new_constructor,
                    "old_ae": old_ae,
                    "new_ae": new_ae,
                    "constructor_changed": constructor_changed,
                    "ae_changed": ae_changed,
                }
            )

    # Print summary
    print(f"\nTotal UK reactors: {len(reactors)}")
    print(f"Updates to apply: {len(updates)}")

    constructor_fixes = [u for u in updates if u["constructor_changed"]]
    ae_additions = [u for u in updates if u["ae_changed"]]

    if constructor_fixes:
        print(f"\n{'='*80}")
        print("CONSTRUCTOR CORRECTIONS:")
        print(f"{'='*80}")
        for u in constructor_fixes:
            print(
                f"  {u['plant']} {u['unit']}: "
                f"'{u['old_constructor']}' -> '{u['new_constructor']}'"
            )

    if ae_additions:
        print(f"\n{'='*80}")
        print("ARCHITECT-ENGINEER UPDATES:")
        print(f"{'='*80}")
        for u in ae_additions:
            print(
                f"  {u['plant']} {u['unit']}: "
                f"'{u['old_ae']}' -> '{u['new_ae']}'"
            )

    # Apply updates
    print(f"\nApplying {len(updates)} updates...")
    for u in updates:
        cur.execute(
            """
            UPDATE reactor_details
            SET constructor = ?, architect_engineer = ?
            WHERE reactor_id = ?
        """,
            (u["new_constructor"], u["new_ae"], u["id"]),
        )

    conn.commit()
    print("Done.")

    # Verify
    print(f"\n{'='*80}")
    print("VERIFICATION - All UK reactors after update:")
    print(f"{'='*80}")
    cur.execute(
        """
        SELECT r.id, r.plant_name, r.unit_number, r.design_series,
               rd.constructor, rd.architect_engineer
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        LEFT JOIN reactor_details rd ON r.id = rd.reactor_id
        WHERE c.name = 'UK'
        ORDER BY r.design_series, r.plant_name, r.unit_number
    """
    )
    rows = cur.fetchall()
    null_ae_count = 0
    for r in rows:
        ae = r["architect_engineer"] or "MISSING"
        if ae == "MISSING":
            null_ae_count += 1
        print(
            f"  {r['id']:<5} {r['plant_name']:<25} {r['unit_number'] or '':<5} "
            f"{r['design_series'] or '':<12} "
            f"constructor={r['constructor'] or 'NULL':<40} "
            f"ae={ae:<40}"
        )

    if null_ae_count:
        print(f"\n  WARNING: {null_ae_count} reactors still missing architect_engineer!")
    else:
        print(f"\n  All {len(rows)} UK reactors have architect_engineer populated.")

    conn.close()


if __name__ == "__main__":
    fix_uk_reactors()
