#!/usr/bin/env python3
"""
Fill missing turbine_supplier, architect_engineer, and pressure_vessel_manufacturer
for 14 Japanese reactors in the reactor_details table.

Sources:
- NS Energy: Fukushima Daiichi construction details (Ebasco/Kajima/GE/Toshiba/Hitachi)
- Wikipedia: Fukushima Daiichi, Tokai, Shimane, Monju, Fugen, JPDR articles
- World Nuclear Association reactor database
- JAIF reactor data
- MHI corporate site (Monju FBR involvement)
- Hitachi-GE Nuclear Energy corporate site (BWR construction history)

Rationale:
  Japanese reactor vendors are vertically integrated. The NSSS constructor also
  served as architect-engineer and turbine supplier. This matches the existing
  pattern in the database for all other Japanese reactors (Fukushima Daini,
  Kashiwazaki Kariwa, Genkai, Ikata, Ohi, etc.).

  Pressure vessels: almost all Japanese RPVs were forged by Japan Steel Works (JSW).
  Monju and Tokai-1 are exceptions due to their non-LWR designs.

Run modes:
  --preview   Show what would change (default)
  --apply     Actually apply the changes
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "nuclear_reactors.db"

# ── UPDATES ──────────────────────────────────────────────────────────────────
# Each entry: (reactor_id, {field: value, ...}, source_note)
#
# Convention follows the existing database pattern:
#   - architect_engineer = NSSS constructor (vertically integrated in Japan)
#   - turbine_supplier   = NSSS constructor
#   - pressure_vessel_manufacturer = JSW for almost all LWRs

UPDATES = [
    # ── Fukushima Daiichi ────────────────────────────────────────────────
    # Constructor already populated. A/E and turbine supplier = constructor.
    # Unit 1 (id=274): GE turnkey, BWR/3
    (274, {
        "architect_engineer": "GE",
        "turbine_supplier": "GE",
    }, "GE turnkey BWR/3; NS Energy confirms GE supplied Unit 1"),

    # Unit 2 (id=275): Toshiba-built BWR/4
    (275, {
        "architect_engineer": "Toshiba",
        "turbine_supplier": "Toshiba",
    }, "Toshiba constructor; follows JP vertical integration pattern"),

    # Unit 3 (id=276): Toshiba-built BWR/4
    (276, {
        "architect_engineer": "Toshiba",
        "turbine_supplier": "Toshiba",
    }, "Toshiba constructor; follows JP vertical integration pattern"),

    # Unit 4 (id=277): Hitachi-built BWR/4
    (277, {
        "architect_engineer": "Hitachi",
        "turbine_supplier": "Hitachi",
    }, "Hitachi constructor; follows JP vertical integration pattern"),

    # Unit 5 (id=278): Toshiba-built BWR/4
    (278, {
        "architect_engineer": "Toshiba",
        "turbine_supplier": "Toshiba",
    }, "Toshiba constructor; follows JP vertical integration pattern"),

    # Unit 6 (id=279): Hitachi-built BWR/5 (GE design)
    (279, {
        "architect_engineer": "Hitachi",
        "turbine_supplier": "Hitachi",
    }, "Hitachi constructor for BWR/5; follows JP vertical integration pattern"),

    # ── Hamaoka 1 & 2 ───────────────────────────────────────────────────
    # Both BWR/4, constructor = Toshiba (already in DB)
    # Hamaoka 3/4/5 all have Toshiba as A/E and turbine supplier
    (288, {
        "architect_engineer": "Toshiba",
        "turbine_supplier": "Toshiba",
    }, "Toshiba constructor; consistent with Hamaoka 3/4/5 pattern"),

    (289, {
        "architect_engineer": "Toshiba",
        "turbine_supplier": "Toshiba",
    }, "Toshiba constructor; consistent with Hamaoka 3/4/5 pattern"),

    # ── Shimane 1 ────────────────────────────────────────────────────────
    # BWR/3, constructor = Hitachi (already in DB)
    # Shimane 2 has Hitachi for all three fields; Shimane 3 has Hitachi-GE
    # Hitachi corporate site confirms Shimane 1 was first domestically-built BWR
    (321, {
        "architect_engineer": "Hitachi",
        "turbine_supplier": "Hitachi",
    }, "Hitachi built Japan's first domestic BWR; Hitachi-GE corporate site"),

    # ── Tsuruga 1 ──────────────────────────────────────────────────────
    # BWR/2, constructor = GE (already in DB)
    # Early GE-supplied unit. GE was the NSSS vendor.
    # Tokai-2 (id=329, same operator JAPC) has GE/GE/GE in the DB.
    (333, {
        "architect_engineer": "GE",
        "turbine_supplier": "GE",
    }, "GE BWR/2; same operator (JAPC) as Tokai-2 which has GE for all fields"),

    # ── JPDR ─────────────────────────────────────────────────────────────
    # BWR/1, no constructor in DB. GE manufactured JPDR-1 (confirmed by WNA/JAERI).
    # 12.5 MWe experimental reactor at Tokai-mura.
    (297, {
        "constructor": "GE",
        "architect_engineer": "GE",
        "turbine_supplier": "GE",
    }, "GE manufactured JPDR-1; WNA, JAERI confirm GE as supplier"),

    # ── Tokai 1 ──────────────────────────────────────────────────────────
    # Magnox (GCR), constructor = GEC (already in DB)
    # UK Magnox design imported. GEC was the prime contractor.
    # Pressure vessel: fabricated by Fuji Electric (welding documented in
    # 1965 Fuji Electric Review article). RPV was a 18m spherical steel vessel.
    # Turbine: GEC supplied the complete plant as prime contractor.
    (328, {
        "architect_engineer": "GEC",
        "turbine_supplier": "GEC",
        "pressure_vessel_manufacturer": "Fuji Electric",
    }, "GEC prime contractor for UK Magnox export; PV welded by Fuji Electric (1965 paper)"),

    # ── Fugen ATR ────────────────────────────────────────────────────────
    # ATR (Advanced Thermal Reactor), constructor = Fuji Electric (already in DB)
    # Unique PNC/JAEA design. Joint construction by Hitachi, Toshiba, MHI, Fuji, Sumitomo.
    # Fuji Electric was the lead constructor. A/E was PNC (Power Reactor and Nuclear
    # Fuel Development Corporation), the government entity that designed the ATR.
    # Turbine: Fuji Electric (constructor supplied BOP including turbine for this
    # BWR-like steam cycle).
    (273, {
        "architect_engineer": "Fuji Electric",
        "turbine_supplier": "Fuji Electric",
    }, "Fuji Electric lead constructor; PNC designed, Fuji built BOP/turbine"),

    # ── Monju ────────────────────────────────────────────────────────────
    # Fast breeder reactor (FBR), constructor = MHI (already in DB)
    # MHI was the prime NSSS contractor. MHI manufactured reactor vessel at Kobe.
    # Turbine: MHI (follows PWR/FBR pattern where MHI supplies complete NSSS+BOP)
    # Pressure vessel: MHI (manufactured at Kobe shipyard per MHI Spectra article)
    (308, {
        "architect_engineer": "Mitsubishi Heavy Industries",
        "turbine_supplier": "Mitsubishi Heavy Industries",
        "pressure_vessel_manufacturer": "Mitsubishi Heavy Industries",
    }, "MHI prime contractor; reactor vessel made at MHI Kobe (MHI Spectra)"),
]


def preview(conn):
    """Show what would change without modifying the database."""
    print("=" * 80)
    print("PREVIEW: Japanese reactor detail updates")
    print("=" * 80)

    for reactor_id, fields, source in UPDATES:
        row = conn.execute(
            "SELECT r.plant_name, r.unit_number, rd.constructor, "
            "rd.architect_engineer, rd.turbine_supplier, rd.pressure_vessel_manufacturer "
            "FROM reactors r LEFT JOIN reactor_details rd ON r.id = rd.reactor_id "
            "WHERE r.id = ?", (reactor_id,)
        ).fetchone()

        if not row:
            print(f"  WARNING: reactor_id={reactor_id} not found!")
            continue

        plant, unit, constructor, ae, ts, pvm = row
        name = f"{plant}-{unit}" if unit else plant
        print(f"\n  {name} (id={reactor_id})")
        print(f"    Source: {source}")
        print(f"    Current:  constructor={constructor}, A/E={ae}, "
              f"turbine={ts}, PV={pvm}")
        changes = []
        for field, value in fields.items():
            label = {
                "constructor": "constructor",
                "architect_engineer": "A/E",
                "turbine_supplier": "turbine",
                "pressure_vessel_manufacturer": "PV",
            }.get(field, field)
            changes.append(f"{label}: {value}")
        print(f"    Setting:  {', '.join(changes)}")

    print(f"\n  Total: {len(UPDATES)} reactors to update")
    print("=" * 80)
    print("Run with --apply to execute these changes.")


def apply_updates(conn):
    """Apply the updates to the database."""
    updated = 0
    skipped = 0

    for reactor_id, fields, source in UPDATES:
        # Verify reactor exists
        row = conn.execute(
            "SELECT r.plant_name, r.unit_number "
            "FROM reactors r WHERE r.id = ?", (reactor_id,)
        ).fetchone()
        if not row:
            print(f"  SKIP: reactor_id={reactor_id} not found")
            skipped += 1
            continue

        plant, unit = row
        name = f"{plant}-{unit}" if unit else plant

        # Ensure reactor_details row exists
        existing = conn.execute(
            "SELECT reactor_id FROM reactor_details WHERE reactor_id = ?",
            (reactor_id,)
        ).fetchone()

        if not existing:
            conn.execute(
                "INSERT INTO reactor_details (reactor_id) VALUES (?)",
                (reactor_id,)
            )

        # Build SET clause
        set_parts = []
        values = []
        for field, value in fields.items():
            set_parts.append(f"{field} = ?")
            values.append(value)
        values.append(reactor_id)

        sql = f"UPDATE reactor_details SET {', '.join(set_parts)} WHERE reactor_id = ?"
        conn.execute(sql, values)
        updated += 1
        print(f"  OK: {name} (id={reactor_id}) — {', '.join(f'{k}={v}' for k, v in fields.items())}")

    conn.commit()
    print(f"\nDone: {updated} updated, {skipped} skipped")


def verify(conn):
    """Show final state of all updated reactors."""
    print("\n" + "=" * 80)
    print("VERIFICATION: Final state of updated reactors")
    print("=" * 80)

    ids = [u[0] for u in UPDATES]
    placeholders = ",".join("?" * len(ids))
    rows = conn.execute(f"""
        SELECT r.id, r.plant_name, r.unit_number, r.design_series,
               rd.constructor, rd.architect_engineer, rd.turbine_supplier,
               rd.pressure_vessel_manufacturer
        FROM reactors r
        LEFT JOIN reactor_details rd ON r.id = rd.reactor_id
        WHERE r.id IN ({placeholders})
        ORDER BY r.plant_name, r.unit_number
    """, ids).fetchall()

    for row in rows:
        rid, plant, unit, design, constructor, ae, ts, pvm = row
        name = f"{plant}-{unit}" if unit else plant
        print(f"  {name:25s} ({design:8s})  "
              f"constructor={constructor or '?':25s}  A/E={ae or '?':25s}  "
              f"turbine={ts or '?':25s}  PV={pvm or '?'}")

    # Check remaining gaps
    print("\n  Remaining Japan gaps:")
    gaps = conn.execute("""
        SELECT r.id, r.plant_name, r.unit_number, r.design_series,
               rd.constructor, rd.architect_engineer, rd.turbine_supplier,
               rd.pressure_vessel_manufacturer
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        LEFT JOIN reactor_details rd ON r.id = rd.reactor_id
        WHERE c.name = 'Japan'
          AND (rd.turbine_supplier IS NULL OR rd.architect_engineer IS NULL
               OR rd.pressure_vessel_manufacturer IS NULL)
        ORDER BY r.plant_name, r.unit_number
    """).fetchall()

    if gaps:
        for row in gaps:
            rid, plant, unit, design, constructor, ae, ts, pvm = row
            name = f"{plant}-{unit}" if unit else plant
            missing = []
            if not ae:
                missing.append("A/E")
            if not ts:
                missing.append("turbine")
            if not pvm:
                missing.append("PV")
            print(f"    {name:25s} missing: {', '.join(missing)}")
    else:
        print("    None! All Japanese reactors now have complete details.")


def main():
    mode = "preview"
    if "--apply" in sys.argv:
        mode = "apply"

    conn = sqlite3.connect(DB_PATH)

    if mode == "preview":
        preview(conn)
    else:
        print("Applying Japanese reactor detail updates...")
        apply_updates(conn)
        verify(conn)

    conn.close()


if __name__ == "__main__":
    main()
