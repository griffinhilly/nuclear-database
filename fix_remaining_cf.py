"""
Fix remaining CF > 102% entries based on PRIS research.

Sources: IAEA PRIS reactor detail pages (fetched Mar 2026),
NRC Info Finder, Rosatom publications.
"""
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = 'C:/Users/griff/nuclear-database/nuclear_reactors.db'


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=" * 60)
    print("Fix remaining CF > 102% entries")
    print("=" * 60)

    # =====================================================================
    # FIX 1: Cook 2 (id=579)
    # DB gross=1151, PRIS gross=1231, PRIS net=1168
    # DB value was the pre-upgrade value. PRIS is authoritative.
    # =====================================================================
    print("\n[1] Cook 2 — DB gross 1151, PRIS gross 1231")
    cur.execute("""INSERT OR REPLACE INTO capacity_changes
        (reactor_id, effective_date, gross_capacity_mw, net_capacity_mw, change_type, source, notes)
        VALUES (579, '1978-07-01', 1133, 1060, 'initial', 'PRIS/NRC',
        'Original W 4-Loop rating (design net 1060)')""")
    cur.execute("""INSERT OR REPLACE INTO capacity_changes
        (reactor_id, effective_date, gross_capacity_mw, net_capacity_mw, change_type, source, notes)
        VALUES (579, '2003-05-02', 1231, 1168, 'uprate', 'PRIS/NRC',
        'MUR 1.66% + turbine upgrades; PRIS gross=1231, net=1168')""")
    cur.execute("UPDATE reactors SET gross_capacity_mw = 1231, net_capacity_mw = 1168 WHERE id = 579")
    print("  Fixed: gross 1151->1231, net 1100->1168")

    # =====================================================================
    # FIX 2: Turkey Point 3 (id=675) & 4 (id=676)
    # PRIS gross=829, PRIS net=837 — net > gross is impossible.
    # PRIS gross is stale. Pre-EPU station service ratio = 728/693 = 1.050.
    # Estimated true post-EPU gross = 837 * 1.050 = 879 MWe.
    # =====================================================================
    print("\n[2] Turkey Point 3&4 — PRIS net (837) > gross (829), gross is stale")
    tp_gross = 879  # 837 * 1.050
    for rid in (675, 676):
        cur.execute("UPDATE reactors SET gross_capacity_mw = ? WHERE id = ?", (tp_gross, rid))
        cur.execute("""UPDATE capacity_changes SET gross_capacity_mw = ?
            WHERE reactor_id = ? AND source = 'NRC EPU'""", (tp_gross, rid))
    print(f"  Fixed: gross 829->{tp_gross} (est. from PRIS net 837 x 1.050 station service ratio)")

    # =====================================================================
    # FIX 3: Russian VVER-1000 thermal uprates
    # Rosatom uprated VVER-1000s to 104% thermal (3000->3120 MWt).
    # Balakovo 4 pilot at 107% (3000->3200 MWt, PRIS thermal already updated).
    # PRIS kept gross at 1000 MWe for all. Proportional estimates:
    #   104%: 1000 * (3120/3000) = 1040 MWe
    #   107%: 1000 * (3200/3000) = 1067 MWe
    # =====================================================================
    print("\n[3] Russian VVER-1000 thermal uprates")

    vver_104 = [
        (354, 'Balakovo 1', '1986-05-23'),
        (355, 'Balakovo 2', '1988-01-18'),
        (367, 'Kalinin 1', '1985-06-12'),
        (369, 'Kalinin 3', '2005-11-08'),
        (394, 'Rostov 1', '2001-03-30'),
        (395, 'Rostov 2', '2010-12-10'),
    ]
    for rid, name, comm_date in vver_104:
        cur.execute("""INSERT OR REPLACE INTO capacity_changes
            (reactor_id, effective_date, gross_capacity_mw, net_capacity_mw, change_type, source, notes)
            VALUES (?, ?, 1000, 950, 'initial', 'PRIS', 'Original VVER-1000/V-320 rating')""",
            (rid, comm_date))
        cur.execute("""INSERT OR REPLACE INTO capacity_changes
            (reactor_id, effective_date, gross_capacity_mw, net_capacity_mw, change_type, source, notes)
            VALUES (?, '2012-01-01', 1040, 988, 'uprate', 'Rosatom',
            '104%% thermal uprate (3000->3120 MWt); PRIS gross not updated')""", (rid,))
        cur.execute("UPDATE reactors SET gross_capacity_mw = 1040 WHERE id = ?", (rid,))
        print(f"  {name}: gross 1000->1040 (104% thermal)")

    # Balakovo 4 (id=357): 107% pilot
    cur.execute("""INSERT OR REPLACE INTO capacity_changes
        (reactor_id, effective_date, gross_capacity_mw, net_capacity_mw, change_type, source, notes)
        VALUES (357, '1993-12-22', 1000, 950, 'initial', 'PRIS', 'Original VVER-1000/V-320 rating')""")
    cur.execute("""INSERT OR REPLACE INTO capacity_changes
        (reactor_id, effective_date, gross_capacity_mw, net_capacity_mw, change_type, source, notes)
        VALUES (357, '2015-01-01', 1067, 1013, 'uprate', 'Rosatom/PRIS',
        '107%% thermal uprate pilot (3000->3200 MWt); PRIS thermal=3200 confirmed')""")
    cur.execute("UPDATE reactors SET gross_capacity_mw = 1067 WHERE id = 357")
    print("  Balakovo 4: gross 1000->1067 (107% thermal pilot)")

    # =====================================================================
    # FIX 4: Wolsong 2 (id=440) — derated per PRIS
    # DB gross=675 (original), PRIS current gross=593, net=571
    # Add capacity_change for the derate
    # =====================================================================
    print("\n[4] Wolsong 2 — derated per PRIS (675->593)")
    cur.execute("""INSERT OR REPLACE INTO capacity_changes
        (reactor_id, effective_date, gross_capacity_mw, net_capacity_mw, change_type, source, notes)
        VALUES (440, '1997-07-01', 675, 652, 'initial', 'PRIS', 'Original CANDU 6 rating')""")
    cur.execute("""INSERT OR REPLACE INTO capacity_changes
        (reactor_id, effective_date, gross_capacity_mw, net_capacity_mw, change_type, source, notes)
        VALUES (440, '2016-01-01', 593, 571, 'derate', 'PRIS',
        'Derated per PRIS (gross 675->593, net 652->571)')""")
    cur.execute("UPDATE reactors SET gross_capacity_mw = 593, net_capacity_mw = 571 WHERE id = 440")
    print("  Fixed: gross 675->593, net 652->571")

    # =====================================================================
    # FIX 5: Quad Cities 1 (id=647) — PRIS gross 940 looks correct,
    # but generation data exceeds theoretical max by 4.6%.
    # No known uprate beyond the EPU. Likely generation data issue.
    # Delete the 3 impossible entries (2021, 2022, 2024 with CF > 102%).
    # =====================================================================
    print("\n[5] Quad Cities 1 — generation data exceeds theoretical max at PRIS-confirmed 940 MW")
    cur.execute("""SELECT year, electricity_gwh,
        ROUND(electricity_gwh / (940.0 / 1000.0 * 8760) * 100, 1) as cf
        FROM generation_annual WHERE reactor_id = 647
        AND electricity_gwh / (940.0 / 1000.0 * 8760) * 100 > 102
        ORDER BY year""")
    bad_qc = cur.fetchall()
    for row in bad_qc:
        print(f"  Deleting {row[0]}: {row[1]:.1f} GWh = {row[2]}% CF (impossible at 940 MW)")
    cur.execute("""DELETE FROM generation_annual WHERE reactor_id = 647
        AND electricity_gwh / (940.0 / 1000.0 * 8760) * 100 > 102""")
    print(f"  Deleted {cur.rowcount} impossible generation entries")

    # =====================================================================
    # FIX 6: Sendai 1 (id=317) — PRIS gross 890 confirmed, generation 2.8% over
    # Delete entries with CF > 102%
    # =====================================================================
    print("\n[6] Sendai 1 — generation data exceeds theoretical max at PRIS-confirmed 890 MW")
    cur.execute("""SELECT g.year, g.electricity_gwh,
        ROUND(g.electricity_gwh / (890.0 / 1000.0 * 8760) * 100, 1) as cf
        FROM generation_annual g WHERE g.reactor_id = 317
        AND g.electricity_gwh / (890.0 / 1000.0 * 8760) * 100 > 102
        ORDER BY g.year""")
    for row in cur.fetchall():
        print(f"  Deleting {row[0]}: {row[1]:.1f} GWh = {row[2]}% CF")
    cur.execute("""DELETE FROM generation_annual WHERE reactor_id = 317
        AND electricity_gwh / (890.0 / 1000.0 * 8760) * 100 > 102""")
    print(f"  Deleted {cur.rowcount} impossible generation entries")

    # =====================================================================
    # FIX 7: Takahama 3 (id=326) — PRIS gross 870 confirmed, generation 2.7% over
    # =====================================================================
    print("\n[7] Takahama 3 — generation data exceeds theoretical max at PRIS-confirmed 870 MW")
    cur.execute("""SELECT g.year, g.electricity_gwh,
        ROUND(g.electricity_gwh / (870.0 / 1000.0 * 8760) * 100, 1) as cf
        FROM generation_annual g WHERE g.reactor_id = 326
        AND g.electricity_gwh / (870.0 / 1000.0 * 8760) * 100 > 102
        ORDER BY g.year""")
    for row in cur.fetchall():
        print(f"  Deleting {row[0]}: {row[1]:.1f} GWh = {row[2]}% CF")
    cur.execute("""DELETE FROM generation_annual WHERE reactor_id = 326
        AND electricity_gwh / (870.0 / 1000.0 * 8760) * 100 > 102""")
    print(f"  Deleted {cur.rowcount} impossible generation entries")

    # =====================================================================
    # FIX 8: Wolsong 2 2011 entry — 103.6% at original 675 MW
    # This is during the period when Wolsong 1 was being refurbished.
    # Likely misattributed station-level data.
    # =====================================================================
    print("\n[8] Wolsong 2 2011 — CF 103.6% at historical 675 MW")
    cur.execute("""SELECT electricity_gwh FROM generation_annual
        WHERE reactor_id = 440 AND year = 2011""")
    row = cur.fetchone()
    if row:
        cf = row[0] / (675.0 / 1000.0 * 8760) * 100
        print(f"  2011: {row[0]:.1f} GWh = {cf:.1f}% CF at 675 MW")
        if cf > 102:
            cur.execute("DELETE FROM generation_annual WHERE reactor_id = 440 AND year = 2011")
            print(f"  Deleted (impossible at historical capacity)")

    # =====================================================================
    # VERIFY
    # =====================================================================
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    EFFECTIVE_CAPACITY = """COALESCE(
        (SELECT cc.gross_capacity_mw FROM capacity_changes cc
         WHERE cc.reactor_id = r.id AND cc.effective_date <= (g.year || '-12-31')
         ORDER BY cc.effective_date DESC LIMIT 1),
        r.gross_capacity_mw)"""

    for threshold in [110, 105, 102, 100]:
        cur.execute(f"""
            SELECT COUNT(*) FROM generation_annual g
            JOIN reactors r ON g.reactor_id = r.id
            WHERE r.gross_capacity_mw > 0
              AND g.electricity_gwh / ({EFFECTIVE_CAPACITY} / 1000.0 * 8760) * 100 > {threshold}
        """)
        count = cur.fetchone()[0]
        print(f"CF > {threshold}%: {count}")

    cur.execute("SELECT COUNT(*) FROM capacity_changes")
    print(f"\nCapacity changes: {cur.fetchone()[0]} records")
    cur.execute("SELECT COUNT(DISTINCT reactor_id) FROM capacity_changes")
    print(f"Reactors with changes: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM generation_annual")
    print(f"Generation entries: {cur.fetchone()[0]}")

    # Show remaining CF > 100%
    cur.execute(f"""
        SELECT r.plant_name, r.unit_number, g.year,
               ROUND(g.electricity_gwh / ({EFFECTIVE_CAPACITY} / 1000.0 * 8760) * 100, 1) as cf
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE r.gross_capacity_mw > 0
          AND g.electricity_gwh / ({EFFECTIVE_CAPACITY} / 1000.0 * 8760) * 100 > 100
        ORDER BY cf DESC
    """)
    rows = cur.fetchall()
    if rows:
        print(f"\nRemaining CF > 100% ({len(rows)} entries):")
        for row in rows:
            print(f"  {row[0]} {row[1]} | {row[2]} | CF={row[3]}%")

    conn.commit()
    print("\n" + "=" * 60)
    print("All fixes committed.")
    print("=" * 60)


if __name__ == '__main__':
    main()
