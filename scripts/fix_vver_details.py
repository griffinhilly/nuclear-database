#!/usr/bin/env python3
"""Fill missing constructor, architect_engineer, turbine_supplier, and
pressure_vessel_manufacturer for Eastern European VVER/RBMK reactors.

Sources:
  - Czech plants (Dukovany, Temelin): CEZ corporate pages, Skoda JS references,
    World Nuclear Association Czech Republic profile
  - Loviisa: Fortum history, WNA Finland profile, STUK
  - Paks: WNA Hungary profile, MVM Paks corporate, Turboatom history
  - Bohunice / Mochovce: WNA Slovakia profile, Skoda JS references
  - Ignalina: WNA Lithuania profile, NIKIET/RBMK Wikipedia, Turboatom history
  - Bohunice A1: KS 150 Wikipedia, Skoda Works/Plzen references
  - VVER-440 turbines: K-220-44 manufactured by Turboatom (Kharkov) and Skoda Plzen
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nuclear_reactors.db')


def update_reactor(conn, reactor_id, **fields):
    """Update non-NULL fields in reactor_details for a given reactor_id."""
    set_clauses = []
    values = []
    for col, val in fields.items():
        if val is not None:
            set_clauses.append(f"{col} = ?")
            values.append(val)
    if not set_clauses:
        return
    values.append(reactor_id)
    sql = f"UPDATE reactor_details SET {', '.join(set_clauses)} WHERE reactor_id = ?"
    conn.execute(sql, values)


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # -----------------------------------------------------------------------
    # 1. Czech Republic — Dukovany 1-4 (IDs 116-119) — VVER-440/213
    #    Constructor: Skoda Praha (general technology contractor)
    #    A/E and turbine supplier already populated
    # -----------------------------------------------------------------------
    for rid in (116, 117, 118, 119):
        update_reactor(conn, rid, constructor="Skoda Praha")
    print("Updated Dukovany 1-4: constructor = Skoda Praha")

    # -----------------------------------------------------------------------
    # 2. Czech Republic — Temelin 1-2 (IDs 120-121) — VVER-1000/320
    #    Constructor: Skoda Praha (general supplier of power section)
    # -----------------------------------------------------------------------
    for rid in (120, 121):
        update_reactor(conn, rid, constructor="Skoda Praha")
    print("Updated Temelin 1-2: constructor = Skoda Praha")

    # -----------------------------------------------------------------------
    # 3. Finland — Loviisa 1-2 (IDs 122-123) — VVER-440/213
    #    Constructor: Atomenergoexport (Soviet NSSS supplier per IVO contract)
    # -----------------------------------------------------------------------
    for rid in (122, 123):
        update_reactor(conn, rid, constructor="Atomenergoexport")
    print("Updated Loviisa 1-2: constructor = Atomenergoexport")

    # -----------------------------------------------------------------------
    # 4. Hungary — Paks 1-4 (IDs 234-237) — VVER-440/213
    #    Constructor: Atomenergoexport (contracted 1971, construction from 1974)
    # -----------------------------------------------------------------------
    for rid in (234, 235, 236, 237):
        update_reactor(conn, rid, constructor="Atomenergoexport")
    print("Updated Paks 1-4: constructor = Atomenergoexport")

    # -----------------------------------------------------------------------
    # 5. Slovakia — Bohunice V1 units 1-2 (IDs 401-402) — VVER-440/230
    #    Constructor: Atomenergoexport (supplied reactors, with Skoda equipment)
    # -----------------------------------------------------------------------
    for rid in (401, 402):
        update_reactor(conn, rid, constructor="Atomenergoexport")
    print("Updated Bohunice V1 (1-2): constructor = Atomenergoexport")

    # -----------------------------------------------------------------------
    # 6. Slovakia — Bohunice V2 units 3-4 (IDs 403-404) — VVER-440/213
    #    Constructor: Skoda Praha (built by Skoda per WNA Slovakia profile)
    # -----------------------------------------------------------------------
    for rid in (403, 404):
        update_reactor(conn, rid, constructor="Skoda Praha")
    print("Updated Bohunice V2 (3-4): constructor = Skoda Praha")

    # -----------------------------------------------------------------------
    # 7. Slovakia — Mochovce 1-4 (IDs 406-409) — VVER-440/213
    #    Constructor: Skoda Praha (main contractor since 1987; units 3-4
    #    completed by consortium led by Skoda JS)
    # -----------------------------------------------------------------------
    for rid in (406, 407, 408, 409):
        update_reactor(conn, rid, constructor="Skoda Praha")
    print("Updated Mochovce 1-4: constructor = Skoda Praha")

    # -----------------------------------------------------------------------
    # 8. Lithuania — Ignalina 1-2 (IDs 336-337) — RBMK-1500
    #    Constructor: Minsredmash (Soviet Ministry of Medium Machine Building,
    #      consistent with all other RBMK plants in database)
    #    Architect-Engineer: NIKIET (chief designer of RBMK reactors)
    #    Turbine Supplier: Turboatom (Kharkov K-750-65/3000 turbines)
    #    Pressure Vessel: N/A for RBMK (channel-type reactor, no traditional RPV)
    # -----------------------------------------------------------------------
    for rid in (336, 337):
        update_reactor(conn, rid,
                       constructor="Minsredmash",
                       architect_engineer="NIKIET",
                       turbine_supplier="Turboatom")
    print("Updated Ignalina 1-2: constructor = Minsredmash, A/E = NIKIET, "
          "turbine = Turboatom")

    # -----------------------------------------------------------------------
    # 9. Slovakia — Bohunice A-1 (ID 405) — KS 150 (HWGCR)
    #    Constructor: Skoda Works (built entirely in Czechoslovakia)
    #    Architect-Engineer: Energoprojekt Praha (with Soviet design cooperation)
    #    Turbine Supplier: Skoda (manufactured at Plzen)
    #    Pressure Vessel: Skoda Works (reactor vessel manufactured by Skoda Plzen)
    # -----------------------------------------------------------------------
    update_reactor(conn, 405,
                   constructor="Skoda Works",
                   architect_engineer="Energoprojekt Praha",
                   turbine_supplier="Skoda",
                   pressure_vessel_manufacturer="Skoda Works")
    print("Updated Bohunice A-1: constructor = Skoda Works, A/E = Energoprojekt Praha, "
          "turbine = Skoda, PV = Skoda Works")

    conn.commit()

    # -----------------------------------------------------------------------
    # Verification: show all updated rows
    # -----------------------------------------------------------------------
    print("\n--- Verification ---")
    rows = cursor.execute("""
        SELECT r.id, r.plant_name, r.unit_number, r.design_series, c.name as country,
               rd.constructor, rd.architect_engineer, rd.turbine_supplier,
               rd.pressure_vessel_manufacturer
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        JOIN reactor_details rd ON r.id = rd.reactor_id
        WHERE r.id IN (116,117,118,119,120,121,122,123,
                       234,235,236,237,336,337,
                       401,402,403,404,405,406,407,408,409)
        ORDER BY c.name, r.plant_name, r.unit_number
    """).fetchall()

    fmt = "{:<4} {:<12} {:<4} {:<15} {:<16} {:<20} {:<20} {:<18} {:<16}"
    print(fmt.format("ID", "Plant", "Unit", "Design", "Country",
                     "Constructor", "Architect/Eng", "Turbine", "PV Mfr"))
    print("-" * 145)
    for r in rows:
        print(fmt.format(
            r['id'], r['plant_name'], r['unit_number'], r['design_series'],
            r['country'],
            r['constructor'] or '—',
            r['architect_engineer'] or '—',
            r['turbine_supplier'] or '—',
            r['pressure_vessel_manufacturer'] or '—'
        ))

    # Check for remaining NULLs
    remaining = cursor.execute("""
        SELECT COUNT(*) FROM reactor_details rd
        JOIN reactors r ON r.id = rd.reactor_id
        JOIN countries c ON r.country_id = c.id
        WHERE r.id IN (116,117,118,119,120,121,122,123,
                       234,235,236,237,336,337,
                       401,402,403,404,405,406,407,408,409)
          AND (rd.constructor IS NULL OR rd.architect_engineer IS NULL
               OR rd.turbine_supplier IS NULL)
    """).fetchone()[0]

    if remaining:
        print(f"\nWarning: {remaining} reactor(s) still have NULL fields.")
    else:
        print("\nAll target reactors now have constructor, A/E, and turbine supplier populated.")

    conn.close()


if __name__ == '__main__':
    main()
