#!/usr/bin/env python3
"""
Fix Chinese reactor data based on WNA + Wikipedia cross-verification.

Sources:
- WNA Reactor Database (world-nuclear.org/nuclear-reactor-database)
- Wikipedia infobox coordinates
- World Nuclear News articles

Run modes:
  --preview   Show what would change (default)
  --apply     Actually apply the changes
"""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DB_PATH = Path(__file__).parent / "nuclear_reactors.db"


# ── COORDINATE FIXES (from Wikipedia) ──────────────────────────────────────
COORD_FIXES = [
    # (plant_name, new_lat, new_lon, source_note)
    ("Bailong", 21.54528, 108.29389, "Wikipedia: Guangxi Bailong Nuclear Power Project"),
    ("Lianjiang", 21.55417, 109.80694, "Wikipedia: Lianjiang NPP"),
    ("Linglong", 19.46075, 108.89992, "Wikipedia: Changjiang site (SMR co-located)"),
    ("Lufeng", 22.75000, 115.80000, "Wikipedia: Lufeng NPP"),
    ("Sanao", 27.20200, 120.51300, "Wikipedia: San'ao NPP"),
    ("Xudabao", 40.35139, 120.54583, "Wikipedia: Xudabao NPP"),
    ("Yangjiang", 21.70833, 112.26111, "Wikipedia: Yangjiang NPS — 29km fix"),
    ("Jinqimen", 29.05640, 121.94480, "Wikipedia: Jinqimen NPP — 550km fix!"),
    ("Hongyanhe", 39.79583, 121.48056, "Wikipedia: Hongyanhe NPP"),
]

# Zhangzhou: all 4 units should share same coordinates
ZHANGZHOU_COORDS = (23.82917, 117.49167)  # Wikipedia

# Ningde: all units should share site coordinates
NINGDE_COORDS = (27.04444, 120.28333)  # Wikipedia


# ── SHIDAOWAN FIXES ────────────────────────────────────────────────────────
# Our current Shidaowan-1 (id=714) and Shidaowan-2 (id=730) have wrong data.
# They were created with HPR1000 construction dates but CAP1400 design.
# Real CAP1400 data from WNA:
SHIDAOWAN_FIXES = {
    "cap1400_unit1": {  # id=714
        "gross_capacity_mw": 1500.0,
        "net_capacity_mw": 1400.0,
        "thermal_capacity_mw": 4040.0,
        "construction_start": "2019-06-19",
        "grid_connection": "2024-10-31",
        "status": "Operational",
    },
    "cap1400_unit2": {  # id=730
        "gross_capacity_mw": 1500.0,
        "net_capacity_mw": 1400.0,
        "thermal_capacity_mw": 4040.0,
        "construction_start": "2020-04-21",
    },
}

# Missing HPR1000 units at Shidaowan (to add)
SHIDAOWAN_NEW_UNITS = [
    {
        "plant_name": "Shidaowan",
        "unit_number": "3",
        "design_series": "HPR1000",
        "gross_capacity_mw": 1200.0,
        "net_capacity_mw": 1116.0,
        "construction_start": "2024-07-28",
        "status": "Under Construction",
    },
    {
        "plant_name": "Shidaowan",
        "unit_number": "4",
        "design_series": "HPR1000",
        "gross_capacity_mw": 1200.0,
        "net_capacity_mw": 1116.0,
        "construction_start": "2025-05-08",
        "status": "Under Construction",
    },
]


# ── REACTOR DATA FIXES (from WNA) ─────────────────────────────────────────
# (reactor_id, field_updates_dict, source_note)
REACTOR_FIXES = [
    # Zhangzhou-1: wrong capacity
    (114, {"gross_capacity_mw": 1212.0, "grid_connection": "2024-11-28"},
     "WNA: Zhangzhou-1 gross 1212, grid connection Nov 2024"),

    # Zhangzhou-3: more precise construction date
    (709, {"construction_start": "2024-02-22"},
     "WNA: Zhangzhou-3 CS Feb 22 not Feb 1"),

    # Zhangzhou-4: more precise construction date
    (710, {"construction_start": "2024-09-27"},
     "WNA: Zhangzhou-4 CS Sep 27 not Sep 1"),

    # Bailong-1: wrong reactor type and dates
    (716, {"design_series": "CAP1000", "gross_capacity_mw": 1250.0,
           "construction_start": "2025-12-25"},
     "WNA: Bailong-1 is CAP1000, not HPR1000. CS Dec 25 2025"),

    # Taipingling-1: now operational per WNA
    (98, {"status": "Operational", "grid_connection": "2026-02-13"},
     "WNA: Taipingling-1 grid connected Feb 13, 2026"),

    # Taipingling-3: wrong construction date
    (717, {"construction_start": "2025-06-10", "gross_capacity_mw": 1202.0},
     "WNA: Taipingling-3 CS Jun 10, 2025 (not Jan 2024). Gross 1202"),

    # Fangchenggang 3-4: capacity
    (62, {"gross_capacity_mw": 1188.0}, "WNA: Fangchenggang-3 gross 1188"),
    (63, {"gross_capacity_mw": 1188.0}, "WNA: Fangchenggang-4 gross 1188"),

    # Lianjiang: capacity
    (711, {"gross_capacity_mw": 1250.0, "construction_start": "2023-09-27"},
     "WNA: Lianjiang-1 gross 1250, CS Sep 27"),
    (712, {"gross_capacity_mw": 1250.0},
     "WNA: Lianjiang-2 gross 1250"),

    # Lufeng: capacity swap
    (699, {"gross_capacity_mw": 1200.0},
     "WNA: Lufeng-1 gross 1200 (was 1250 — swapped with unit 2)"),
    (700, {"gross_capacity_mw": 1250.0, "construction_start": "2025-12-22"},
     "WNA: Lufeng-2 gross 1250 (was 1200). CS Dec 22"),

    # Ningde-1: capacity
    (84, {"gross_capacity_mw": 1089.0}, "WNA: Ningde-1 gross 1089"),
    (85, {"gross_capacity_mw": 1089.0}, "WNA: Ningde-2 gross 1089"),
    (86, {"gross_capacity_mw": 1089.0}, "WNA: Ningde-3 gross 1089"),
    (87, {"gross_capacity_mw": 1089.0}, "WNA: Ningde-4 gross 1089"),

    # Sanao-3: capacity + date
    (694, {"gross_capacity_mw": 1210.0, "construction_start": "2025-11-19"},
     "WNA: Sanao-3 gross 1210, CS Nov 19"),

    # Xudabao 3-4: more precise construction dates
    (705, {"construction_start": "2021-07-28"},
     "WNA: Xudabao-3 CS Jul 28 (not Jul 1)"),
    (706, {"construction_start": "2022-05-19"},
     "WNA: Xudabao-4 CS May 19 (not May 1)"),
    (703, {"construction_start": "2023-11-03"},
     "WNA: Xudabao-1 CS Nov 3 (not Nov 1)"),
    (704, {"construction_start": "2024-07-17"},
     "WNA: Xudabao-2 CS Jul 17 (not Jul 1)"),
]

# Missing reactor: Ningde-6
NINGDE_6 = {
    "plant_name": "Ningde",
    "unit_number": "6",
    "design_series": "HPR1000",
    "gross_capacity_mw": 1210.0,
    "net_capacity_mw": 1116.0,
    "construction_start": "2025-12-16",
    "status": "Under Construction",
}


def get_model_id(conn, design_series):
    """Look up model_id for a design series."""
    row = conn.execute(
        "SELECT model_id FROM reactors WHERE design_series = ? AND model_id IS NOT NULL LIMIT 1",
        (design_series,)
    ).fetchone()
    return row[0] if row else None


def get_technology_id(conn, design_series):
    """Look up technology_id for a design series."""
    row = conn.execute(
        "SELECT technology_id FROM reactors WHERE design_series = ? AND technology_id IS NOT NULL LIMIT 1",
        (design_series,)
    ).fetchone()
    return row[0] if row else None


def get_supplier_id(conn, design_series):
    """Look up supplier_id for a design series."""
    row = conn.execute(
        "SELECT supplier_id FROM reactors WHERE design_series = ? AND supplier_id IS NOT NULL LIMIT 1",
        (design_series,)
    ).fetchone()
    return row[0] if row else None


def preview_all(conn):
    """Show all planned changes."""

    print(f"\n{'=' * 80}")
    print("1. COORDINATE FIXES")
    print(f"{'=' * 80}")

    coord_count = 0
    for plant, new_lat, new_lon, note in COORD_FIXES:
        rows = conn.execute(
            "SELECT id, latitude, longitude FROM reactors WHERE plant_name = ?",
            (plant,)).fetchall()
        if rows:
            old_lat, old_lon = rows[0][1], rows[0][2]
            print(f"\n  {plant} ({len(rows)} reactors): ({old_lat}, {old_lon}) -> ({new_lat}, {new_lon})")
            print(f"    {note}")
            coord_count += len(rows)
        else:
            print(f"\n  {plant}: NOT FOUND")

    # Zhangzhou
    rows = conn.execute(
        "SELECT id, latitude, longitude FROM reactors WHERE plant_name = 'Zhangzhou'").fetchall()
    if rows:
        print(f"\n  Zhangzhou ({len(rows)} reactors): all -> ({ZHANGZHOU_COORDS[0]}, {ZHANGZHOU_COORDS[1]})")
        print(f"    Wikipedia: all units at same site")
        coord_count += len(rows)

    # Ningde
    rows = conn.execute(
        "SELECT id, latitude, longitude FROM reactors WHERE plant_name = 'Ningde'").fetchall()
    if rows:
        print(f"\n  Ningde ({len(rows)} reactors): all -> ({NINGDE_COORDS[0]}, {NINGDE_COORDS[1]})")
        print(f"    Wikipedia: all units at same site")
        coord_count += len(rows)

    print(f"\n  Total coordinate fixes: {coord_count} reactors")

    print(f"\n{'=' * 80}")
    print("2. SHIDAOWAN FIXES")
    print(f"{'=' * 80}")

    r714 = conn.execute("SELECT * FROM reactors WHERE id = 714").fetchone()
    print(f"\n  Shidaowan-1 (id=714): CAP1400")
    print(f"    capacity: {r714[9]}MW -> 1500MW")
    print(f"    construction_start: {r714[20]} -> 2019-06-19")
    print(f"    grid_connection: {r714[22]} -> 2024-10-31")
    print(f"    status: {r714[19]} -> Operational")

    r730 = conn.execute("SELECT * FROM reactors WHERE id = 730").fetchone()
    print(f"\n  Shidaowan-2 (id=730): CAP1400")
    print(f"    capacity: {r730[9]}MW -> 1500MW")
    print(f"    construction_start: {r730[20]} -> 2020-04-21")

    print(f"\n  ADD: Shidaowan-3 (HPR1000, 1200MW, UC, CS 2024-07-28)")
    print(f"  ADD: Shidaowan-4 (HPR1000, 1200MW, UC, CS 2025-05-08)")

    print(f"\n{'=' * 80}")
    print("3. REACTOR DATA FIXES (from WNA)")
    print(f"{'=' * 80}")

    for rid, updates, note in REACTOR_FIXES:
        row = conn.execute("SELECT plant_name, unit_number FROM reactors WHERE id = ?", (rid,)).fetchone()
        if row:
            changes = ", ".join(f"{k}: {v}" for k, v in updates.items())
            print(f"\n  #{rid} {row[0]}-{row[1]}: {changes}")
            print(f"    {note}")

    print(f"\n  ADD: Ningde-6 (HPR1000, 1210MW, UC, CS 2025-12-16)")

    print(f"\n{'=' * 80}")
    print("4. PLANNED_REACTORS CLEANUP")
    print(f"{'=' * 80}")

    # Check for duplicates
    for name in ["Shidaowan", "Xudabao", "San'ao", "Sanao"]:
        planned = conn.execute(
            "SELECT id, project_name, unit_number, model FROM planned_reactors WHERE project_name LIKE ?",
            (f"%{name}%",)).fetchall()
        if planned:
            for p in planned:
                print(f"  planned_reactors #{p[0]}: {p[1]}-{p[2]} ({p[3]})")

    # Shidaowan 3-4 in planned should become HPR1000 Phase II (units 5-6)
    print(f"\n  Shidaowan 3-4 in planned_reactors are labeled CAP1400 but the real")
    print(f"  CAP1400 units are now in reactors table. These planned entries likely")
    print(f"  represent the HPR1000 Phase II (units 5-6). Update or remove.")


def apply_all(conn):
    """Apply all fixes."""

    # 1. Coordinate fixes
    print("\n--- Applying coordinate fixes ---")
    for plant, new_lat, new_lon, note in COORD_FIXES:
        result = conn.execute(
            "UPDATE reactors SET latitude = ?, longitude = ? WHERE plant_name = ?",
            (new_lat, new_lon, plant))
        print(f"  {plant}: {result.rowcount} reactors updated")

    # Zhangzhou
    result = conn.execute(
        "UPDATE reactors SET latitude = ?, longitude = ? WHERE plant_name = 'Zhangzhou'",
        ZHANGZHOU_COORDS)
    print(f"  Zhangzhou: {result.rowcount} reactors updated")

    # Ningde
    result = conn.execute(
        "UPDATE reactors SET latitude = ?, longitude = ? WHERE plant_name = 'Ningde'",
        NINGDE_COORDS)
    print(f"  Ningde: {result.rowcount} reactors updated")

    # 2. Shidaowan fixes
    print("\n--- Applying Shidaowan fixes ---")
    for field, value in SHIDAOWAN_FIXES["cap1400_unit1"].items():
        conn.execute(f"UPDATE reactors SET {field} = ? WHERE id = 714", (value,))
    print("  Shidaowan-1 (id=714): CAP1400 data corrected, status->Operational")

    for field, value in SHIDAOWAN_FIXES["cap1400_unit2"].items():
        conn.execute(f"UPDATE reactors SET {field} = ? WHERE id = 730", (value,))
    print("  Shidaowan-2 (id=730): CAP1400 data corrected")

    # Add HPR1000 units
    shidao_lat = 36.972222222
    shidao_lon = 122.528888888
    country_id = 9  # China
    tech_id = get_technology_id(conn, "HPR1000")
    model_id = get_model_id(conn, "HPR1000")
    supplier_id = get_supplier_id(conn, "HPR1000")

    for unit in SHIDAOWAN_NEW_UNITS:
        conn.execute("""
            INSERT INTO reactors (
                plant_name, unit_number, country_id, technology_id, model_id,
                supplier_id, gross_capacity_mw, net_capacity_mw, status,
                construction_start, latitude, longitude, design_series
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (unit["plant_name"], unit["unit_number"], country_id, tech_id,
              model_id, supplier_id, unit["gross_capacity_mw"],
              unit["net_capacity_mw"], unit["status"],
              unit["construction_start"], shidao_lat, shidao_lon,
              unit["design_series"]))
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        print(f"  Added Shidaowan-{unit['unit_number']} (HPR1000): reactor #{new_id}")

    # 3. Reactor data fixes
    print("\n--- Applying WNA data fixes ---")
    for rid, updates, note in REACTOR_FIXES:
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [rid]
        conn.execute(f"UPDATE reactors SET {set_clause} WHERE id = ?", values)
        row = conn.execute("SELECT plant_name, unit_number FROM reactors WHERE id = ?", (rid,)).fetchone()
        print(f"  #{rid} {row[0]}-{row[1]}: {', '.join(f'{k}={v}' for k,v in updates.items())}")

    # Add Ningde-6
    ningde_tech = get_technology_id(conn, "HPR1000")
    ningde_model = get_model_id(conn, "HPR1000")
    ningde_supplier = get_supplier_id(conn, "HPR1000")
    conn.execute("""
        INSERT INTO reactors (
            plant_name, unit_number, country_id, technology_id, model_id,
            supplier_id, gross_capacity_mw, net_capacity_mw, status,
            construction_start, latitude, longitude, design_series
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (NINGDE_6["plant_name"], NINGDE_6["unit_number"], country_id,
          ningde_tech, ningde_model, ningde_supplier,
          NINGDE_6["gross_capacity_mw"], NINGDE_6["net_capacity_mw"],
          NINGDE_6["status"], NINGDE_6["construction_start"],
          NINGDE_COORDS[0], NINGDE_COORDS[1], NINGDE_6["design_series"]))
    new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    print(f"  Added Ningde-6 (HPR1000): reactor #{new_id}")

    # 4. Update planned_reactors for Shidaowan
    # The planned Shidaowan 3-4 CAP1400 entries should be updated to HPR1000
    # since the real CAP1400 units are now in the reactors table and the
    # next planned units are HPR1000 Phase II
    conn.execute("""
        UPDATE planned_reactors
        SET model = 'HPR1000 (Hualong One)',
            gross_capacity_mw = 1200.0,
            net_capacity_mw = 1116.0,
            notes = 'HPR1000 Phase II. Phase I units (3-4) now under construction in reactors table.'
        WHERE project_name = 'Shidaowan' AND unit_number IN ('3', '4')
    """)
    print("  Updated planned_reactors: Shidaowan 3-4 -> HPR1000 Phase II (units 5-6)")

    conn.commit()


def verify(conn):
    """Print verification summary."""
    print(f"\n{'=' * 80}")
    print("VERIFICATION")
    print(f"{'=' * 80}")

    total = conn.execute("SELECT COUNT(*) FROM reactors WHERE country_id = 9").fetchone()[0]
    uc = conn.execute("SELECT COUNT(*) FROM reactors WHERE country_id = 9 AND status = 'Under Construction'").fetchone()[0]
    op = conn.execute("SELECT COUNT(*) FROM reactors WHERE country_id = 9 AND status = 'Operational'").fetchone()[0]
    print(f"\n  Chinese reactors total: {total}")
    print(f"  Operational: {op}")
    print(f"  Under Construction: {uc}")

    print(f"\n  Shidaowan complex:")
    for row in conn.execute("""
        SELECT id, plant_name, unit_number, design_series, gross_capacity_mw,
               status, construction_start
        FROM reactors WHERE plant_name IN ('Shidao Bay', 'Shidaowan')
        ORDER BY plant_name, unit_number
    """):
        print(f"    #{row[0]} {row[1]}-{row[2]}  {row[3]:<10} {row[4]:>6.0f}MW  {row[5]:<20} CS:{row[6]}")

    # Check for remaining round coordinates
    print(f"\n  Remaining round-coordinate reactors:")
    for row in conn.execute("""
        SELECT id, plant_name, unit_number, latitude, longitude
        FROM reactors WHERE country_id = 9
        AND LENGTH(CAST(latitude AS TEXT)) - LENGTH(REPLACE(CAST(latitude AS TEXT), '.', '')) <= 3
        AND (CAST(latitude AS TEXT) LIKE '%.0' OR CAST(latitude AS TEXT) LIKE '%.00'
             OR CAST(latitude AS TEXT) NOT LIKE '%.____%')
    """):
        lat_str = str(row[3])
        lon_str = str(row[4])
        lat_dec = len(lat_str.split('.')[-1]) if '.' in lat_str else 0
        lon_dec = len(lon_str.split('.')[-1]) if '.' in lon_str else 0
        if lat_dec <= 2 and lon_dec <= 2:
            print(f"    #{row[0]} {row[1]}-{row[2]}  ({row[3]}, {row[4]})")


def main():
    mode = "preview"
    if "--apply" in sys.argv:
        mode = "apply"

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    preview_all(conn)

    if mode == "preview":
        print(f"\n{'=' * 80}")
        print("DRY RUN — no changes applied. Run with --apply to execute.")
        print(f"{'=' * 80}")
    elif mode == "apply":
        print(f"\n{'=' * 80}")
        print("APPLYING ALL FIXES...")
        print(f"{'=' * 80}")
        apply_all(conn)
        verify(conn)

    conn.close()


if __name__ == "__main__":
    main()
