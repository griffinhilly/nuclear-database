"""
WNA Audit Phase 1 Updates
- Add 6 missing UC reactors
- Update statuses (Kursk)
- Fill in missing dates (14 reactors)
- Flag items for manual review
"""

import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = "nuclear_reactors.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    changes = []

    # ========================================================================
    # 1. CREATE RITM-200S MODEL (for Cape Nagloynyn floating reactors)
    # ========================================================================
    cur.execute("SELECT id FROM models WHERE name = 'RITM-200S'")
    if not cur.fetchone():
        cur.execute("INSERT INTO models (name) VALUES ('RITM-200S')")
        ritm_model_id = cur.lastrowid
        changes.append(f"Created model RITM-200S (id={ritm_model_id})")
    else:
        cur.execute("SELECT id FROM models WHERE name = 'RITM-200S'")
        ritm_model_id = cur.fetchone()[0]
        changes.append(f"Model RITM-200S already exists (id={ritm_model_id})")

    # ========================================================================
    # 2. ADD 6 MISSING UC REACTORS
    # ========================================================================
    new_reactors = [
        {
            "plant_name": "Kaiga", "unit_number": "5",
            "country_id": 15,  # India
            "technology_id": 1,  # PHWR
            "model_id": 64,  # PHWR-700
            "supplier_id": 21,  # NPCIL
            "status": "Under Construction",
            "net_capacity_mw": 630, "gross_capacity_mw": 700, "thermal_capacity_mw": 2166,
            "construction_start": "2026-03-01",
            "design_series": "PHWR-700",
            "owner": "NPCIL",
            "site_location": "Kaiga", "state_province": "Karnataka",
            "latitude": 14.86532222, "longitude": 74.43964167,
        },
        {
            "plant_name": "Kaiga", "unit_number": "6",
            "country_id": 15,
            "technology_id": 1, "model_id": 64, "supplier_id": 21,
            "status": "Under Construction",
            "net_capacity_mw": 630, "gross_capacity_mw": 700, "thermal_capacity_mw": 2166,
            "construction_start": "2026-03-01",
            "design_series": "PHWR-700",
            "owner": "NPCIL",
            "site_location": "Kaiga", "state_province": "Karnataka",
            "latitude": 14.86532222, "longitude": 74.43964167,
        },
        {
            "plant_name": "Cape Nagloynyn", "unit_number": "1",
            "country_id": 25,  # Russia
            "technology_id": 2,  # PWR
            "model_id": ritm_model_id,  # RITM-200S
            "supplier_id": 29,  # Rosatom
            "status": "Under Construction",
            "net_capacity_mw": 50, "gross_capacity_mw": 57, "thermal_capacity_mw": 165,
            "construction_start": "2022-08-31",
            "design_series": "RITM-200S",
            "owner": "Rosatom",
            "site_location": "Cape Nagloynyn", "state_province": "Chukotka",
            "latitude": None, "longitude": None,  # Floating plant, deployment TBD
            "notes": "Floating NPP (FNPP-2) for Baimskaya mining operation. Barge built at Wison shipyard in China.",
        },
        {
            "plant_name": "Cape Nagloynyn", "unit_number": "2",
            "country_id": 25,
            "technology_id": 2, "model_id": ritm_model_id, "supplier_id": 29,
            "status": "Under Construction",
            "net_capacity_mw": 50, "gross_capacity_mw": 57, "thermal_capacity_mw": 165,
            "construction_start": "2022-08-31",
            "design_series": "RITM-200S",
            "owner": "Rosatom",
            "site_location": "Cape Nagloynyn", "state_province": "Chukotka",
            "latitude": None, "longitude": None,
            "notes": "Floating NPP (FNPP-2) for Baimskaya mining operation. Barge built at Wison shipyard in China.",
        },
        {
            "plant_name": "Leningrad 2", "unit_number": "4",
            "country_id": 25,
            "technology_id": 2,  # PWR
            "model_id": 150,  # VVER-1200
            "supplier_id": 29,  # Rosatom
            "status": "Under Construction",
            "net_capacity_mw": 1101, "gross_capacity_mw": 1188, "thermal_capacity_mw": 3200,
            "construction_start": "2025-03-20",
            "design_series": "VVER-1200",
            "owner": "Rosenergoatom",
            "site_location": "Sosnovyy Bor", "state_province": None,
            "latitude": 59.831111, "longitude": 29.059722,
        },
        {
            "plant_name": "Shin-Hanul (Shin-Ulchin)", "unit_number": "3",
            "country_id": 29,  # South Korea
            "technology_id": 2,  # PWR
            "model_id": 105,  # APR1400
            "supplier_id": 30,  # KEPCO
            "status": "Under Construction",
            "net_capacity_mw": 1340, "gross_capacity_mw": 1400, "thermal_capacity_mw": 3983,
            "construction_start": "2025-05-20",
            "design_series": "APR1400",
            "containment_type": "Large Dry",
            "owner": "Korea Hydro and Nuclear Power Co",
            "site_location": "Ulchin-gun", "state_province": "North Gyeongsang",
            "latitude": 37.09277778, "longitude": 129.38361111,
        },
    ]

    for r in new_reactors:
        # Check if already exists
        cur.execute(
            "SELECT id FROM reactors WHERE plant_name=? AND unit_number=?",
            (r["plant_name"], r["unit_number"])
        )
        if cur.fetchone():
            changes.append(f"SKIP: {r['plant_name']} {r['unit_number']} already exists")
            continue

        cols = [k for k in r.keys()]
        vals = [r[k] for k in cols]
        placeholders = ", ".join(["?" for _ in cols])
        col_names = ", ".join(cols)
        cur.execute(f"INSERT INTO reactors ({col_names}) VALUES ({placeholders})", vals)
        new_id = cur.lastrowid
        changes.append(f"ADD: {r['plant_name']} {r['unit_number']} (id={new_id}) — {r['status']}, {r['net_capacity_mw']} MWe")

    # ========================================================================
    # 3. STATUS UPDATES
    # ========================================================================

    # Kursk 1 unit 2 (id=376): Operational -> Permanent Shutdown (shut down 2024-01-31)
    cur.execute("SELECT status FROM reactors WHERE id=376")
    old = cur.fetchone()[0]
    if old != "Permanent Shutdown":
        cur.execute(
            "UPDATE reactors SET status='Permanent Shutdown', permanent_shutdown='2024-01-31' WHERE id=376"
        )
        changes.append(f"STATUS: Kursk 1-2 (id=376): {old} -> Permanent Shutdown (shutdown 2024-01-31)")

    # Kursk 2 unit 1 (id=379): Under Construction -> Operational (grid connection 2025-12-31)
    cur.execute("SELECT status FROM reactors WHERE id=379")
    old = cur.fetchone()[0]
    if old != "Operational":
        cur.execute(
            "UPDATE reactors SET status='Operational', grid_connection='2025-12-31' WHERE id=379"
        )
        changes.append(f"STATUS: Kursk 2-1 (id=379): {old} -> Operational (grid 2025-12-31)")

    # ========================================================================
    # 4. FILL MISSING DATES
    # ========================================================================

    date_updates = [
        # (id, field, value, description)
        (484, "grid_connection", "2022-10-08", "Barakah 3"),
        (485, "grid_connection", "2024-03-23", "Barakah 4"),
        (245, "grid_connection", "2024-02-20", "Kakrapar 4"),
        (348, "grid_connection", "2022-03-04", "Karachi 3"),
        (408, "grid_connection", "2023-01-31", "Mochovce 3"),
        (126, "grid_connection", "2022-03-12", "Olkiluoto 3"),
        (10,  "grid_connection", "2023-05-13", "Belarusian 2 (Ostrovets 2)"),
        (255, "permanent_shutdown", "2004-10-09", "Rajasthan 1"),
        (429, "grid_connection", "2022-06-09", "Shin Hanul 1"),
        (430, "grid_connection", "2023-12-21", "Shin Hanul 2"),
        (680, "grid_connection", "2023-03-31", "Vogtle 3"),
        (681, "grid_connection", "2024-03-06", "Vogtle 4"),
        (632, "permanent_shutdown", "2022-05-20", "Palisades"),
    ]

    for reactor_id, field, value, desc in date_updates:
        cur.execute(f"SELECT {field} FROM reactors WHERE id=?", (reactor_id,))
        old_val = cur.fetchone()[0]
        if old_val is None:
            cur.execute(f"UPDATE reactors SET {field}=? WHERE id=?", (value, reactor_id))
            changes.append(f"DATE: {desc} (id={reactor_id}): {field} = {value}")
        else:
            changes.append(f"SKIP DATE: {desc} (id={reactor_id}): {field} already set to {old_val}")

    # ========================================================================
    # 5. BELGIUM SHUTDOWN DATE UPDATES (life extensions)
    # ========================================================================

    belgium_updates = [
        (12, "permanent_shutdown", "2025-02-14", "Doel 1", "2022-10-01"),
        (13, "permanent_shutdown", "2025-11-30", "Doel 2", "2022-12-01"),
        (16, "permanent_shutdown", "2025-09-30", "Tihange 1", "2022-10-01"),
    ]

    for reactor_id, field, new_val, desc, old_expected in belgium_updates:
        cur.execute(f"SELECT {field} FROM reactors WHERE id=?", (reactor_id,))
        old_val = cur.fetchone()[0]
        cur.execute(f"UPDATE reactors SET {field}=? WHERE id=?", (new_val, reactor_id))
        changes.append(f"DATE: {desc} (id={reactor_id}): {field} {old_val} -> {new_val} (life extension)")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 70)
    print("WNA PHASE 1 UPDATES")
    print("=" * 70)
    for c in changes:
        print(f"  {c}")
    print(f"\nTotal changes: {len(changes)}")

    # Items flagged for manual review
    print("\n" + "=" * 70)
    print("FLAGGED FOR REVIEW (not changed)")
    print("=" * 70)
    print("  Khmelnytskyi 3 (id=539): WNA=UC, DB=Permanent Shutdown — war-related, ambiguous")
    print("  Khmelnytskyi 4 (id=540): WNA=UC, DB=Permanent Shutdown — war-related, ambiguous")
    print("  Tsuruga 2 (id=334): WNA=Operable, DB=PS (2024-11-13) — NRA rejected safety review, our date seems correct")

    conn.commit()
    conn.close()
    print("\nAll changes committed.")


if __name__ == "__main__":
    main()
