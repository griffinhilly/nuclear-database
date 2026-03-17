"""
Add capacity_changes table and fix CF > 110% entries.

Tracks historical capacity changes (uprates, derates) for reactors.
Also cleans up bad generation data discovered during analysis:
- Bruce 1 & 2: generation entries during confirmed layup periods
- Wolsong 1: impossible spike entries (CF > 110% even at max capacity)

Sources: IAEA PRIS, WNA, Wikipedia, CEA/GIF publications.
"""
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = 'C:/Users/griff/nuclear-database/nuclear_reactors.db'


def create_capacity_changes_table(cur):
    """Create the capacity_changes table."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS capacity_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reactor_id INTEGER NOT NULL,
            effective_date DATE NOT NULL,
            gross_capacity_mw REAL NOT NULL,
            net_capacity_mw REAL,
            change_type TEXT NOT NULL,
            source TEXT,
            notes TEXT,
            FOREIGN KEY (reactor_id) REFERENCES reactors(id),
            UNIQUE(reactor_id, effective_date)
        )
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_capacity_changes_reactor_date
        ON capacity_changes(reactor_id, effective_date)
    """)
    print("Created capacity_changes table")


# =============================================================================
# CAPACITY CHANGE DATA
# =============================================================================

CAPACITY_CHANGES = [
    # Phenix (id=186) — French FBR
    # Original 264 MWe gross / 233 MWe net. Shut down 1993 for refurbishment.
    # Restarted 2003 at 2/3 power (2 of 3 steam generators): 142 MWe gross / 130 MWe net.
    # Sources: PRIS, Wikipedia, CEA/GIF Webinar
    (186, '1974-07-14', 264, 233, 'initial', 'PRIS/Wikipedia',
     'Original full-power rating (3 steam generators)'),
    (186, '2003-06-01', 142, 130, 'derate', 'PRIS/ASN',
     'Restart at ~2/3 power after 10-year refurbishment; 2 of 3 steam generators'),

    # Bruce 1 (id=28) — Canadian CANDU 791
    # Original ~805 MWe gross / 740 MWe net. Uprated to 868/848 by ~1987.
    # Laid up Oct 1997 — Sept 2012. Restarted at 868 gross / 772 net.
    # Sources: PRIS, WNA, Bruce Power
    (28, '1977-09-01', 805, 740, 'initial', 'PRIS/WNA',
     'Original CANDU 791 rating'),
    (28, '1987-01-01', 868, 848, 'uprate', 'PRIS',
     'Reference power increase to 848 MWe net'),
    (28, '2012-09-19', 868, 772, 'restart', 'PRIS/Bruce Power',
     'Restart after 15-year layup; lower net due to refurbishment constraints'),

    # Bruce 2 (id=29) — Canadian CANDU 791
    # Original ~805 MWe gross / 740 MWe net. Uprated to 836/848 by ~1988.
    # Laid up Oct 1995 — Oct 2012 (lead contamination). Restarted at 836 gross / 734 net.
    # Sources: PRIS, WNA, Bruce Power
    (29, '1977-09-01', 805, 740, 'initial', 'PRIS/WNA',
     'Original CANDU 791 rating'),
    (29, '1988-01-01', 836, 848, 'uprate', 'PRIS',
     'Reference power increase to 848 MWe net'),
    (29, '2012-10-16', 836, 734, 'restart', 'PRIS/Bruce Power',
     'Restart after 17-year layup; lower net, gradually increasing'),

    # Rajasthan 1 (id=255) — Indian PHWR (CANDU derivative)
    # Original ~220 MWe gross / 207 MWe net. Progressively derated due to
    # end-shield cracking. Settled at 100 MWe gross / 90 MWe net by late 1980s.
    # Suspended 2004.
    # Sources: PRIS, Stanford/Jayaraman, World Nuclear Report
    (255, '1973-12-16', 220, 207, 'initial', 'PRIS/DAE',
     'Original CANDU-derivative design rating'),
    (255, '1982-01-01', 100, 90, 'derate', 'PRIS',
     'Derated due to end-shield cracking and structural issues'),

    # Wolsong 1 (id=439) — South Korean CANDU 6
    # Original 683 MWe gross / 629 MWe net. Derated ~2004 to 622/578.
    # Refurbished Apr 2009 — Jul 2011. Restored to 691/657 post-refurb.
    # Sources: PRIS, WNA, WNN
    (439, '1983-04-22', 683, 629, 'initial', 'PRIS/WNA',
     'Original CANDU 6 rating'),
    (439, '2004-01-01', 622, 578, 'derate', 'PRIS',
     'Derated before refurbishment'),
    (439, '2011-07-01', 691, 657, 'uprate', 'PRIS/WNN',
     'Capacity restored after full retube refurbishment'),
]


def populate_capacity_changes(cur):
    """Insert capacity change records."""
    for reactor_id, date, gross, net, change_type, source, notes in CAPACITY_CHANGES:
        cur.execute("""
            INSERT OR REPLACE INTO capacity_changes
                (reactor_id, effective_date, gross_capacity_mw, net_capacity_mw,
                 change_type, source, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (reactor_id, date, gross, net, change_type, source, notes))
    print(f"Inserted {len(CAPACITY_CHANGES)} capacity change records")


# =============================================================================
# BAD GENERATION DATA CLEANUP
# =============================================================================

def cleanup_bad_generation_data(cur):
    """Remove generation entries that are known to be incorrect."""
    total_deleted = 0

    # Bruce 1 (id=28): laid up Oct 1997 — Sept 2012
    # Generation data for 1998-2011 is impossible (unit was completely shut down)
    cur.execute("""
        DELETE FROM generation_annual
        WHERE reactor_id = 28 AND year >= 1998 AND year <= 2011
    """)
    deleted = cur.rowcount
    total_deleted += deleted
    print(f"  Bruce 1: deleted {deleted} generation entries (1998-2011 layup period)")

    # Bruce 2 (id=29): laid up Oct 1995 — Oct 2012
    # Generation data for 1996-2011 is impossible
    cur.execute("""
        DELETE FROM generation_annual
        WHERE reactor_id = 29 AND year >= 1996 AND year <= 2011
    """)
    deleted = cur.rowcount
    total_deleted += deleted
    print(f"  Bruce 2: deleted {deleted} generation entries (1996-2011 layup period)")

    # Wolsong 1 (id=439): 3 impossible spikes
    # 2010: 6651 GWh at 683 MW = 111% CF (during refurbishment)
    # 2014: 7821 GWh at 691 MW = 129% CF (physically impossible)
    # 2018: 7353 GWh at 691 MW = 122% CF (physically impossible)
    cur.execute("""
        DELETE FROM generation_annual
        WHERE reactor_id = 439 AND year IN (2010, 2014, 2018)
    """)
    deleted = cur.rowcount
    total_deleted += deleted
    print(f"  Wolsong 1: deleted {deleted} impossible spike entries (2010, 2014, 2018)")

    print(f"  Total: deleted {total_deleted} bad generation entries")
    return total_deleted


# =============================================================================
# REACTOR TABLE CORRECTIONS
# =============================================================================

def fix_reactor_capacities(cur):
    """Fix gross/net capacity values to match current PRIS data."""
    fixes = [
        # Phenix: DB has gross=142, net=233 — net is actually original design net.
        # Current PRIS: gross=142, net=130 (derated). Design net=233.
        # Fix net to match current operating value.
        (186, 142, 130, 'Phenix: net was original design (233), corrected to derated (130)'),

        # Rajasthan 1: DB has gross=100, net=207 — net is original design net.
        # Current PRIS: gross=100, net=90 (derated). Design net=207.
        (255, 100, 90, 'Rajasthan 1: net was original design (207), corrected to derated (90)'),

        # Bruce 1: DB has gross=830, PRIS says 868
        (28, 868, 816, 'Bruce 1: updated to current PRIS values'),

        # Bruce 2: DB has gross=800, PRIS says 836
        (29, 836, 817, 'Bruce 2: updated to current PRIS values'),
    ]

    for reactor_id, gross, net, reason in fixes:
        cur.execute("""
            UPDATE reactors
            SET gross_capacity_mw = ?, net_capacity_mw = ?
            WHERE id = ?
        """, (gross, net, reactor_id))
        print(f"  {reason}")


# =============================================================================
# VERIFICATION
# =============================================================================

def verify_no_impossible_cf(cur):
    """Check that no CF > 110% entries remain."""
    # Use the new capacity_changes-aware calculation
    cur.execute("""
        SELECT r.id, r.plant_name, r.unit_number, g.year, g.electricity_gwh,
               COALESCE(
                   (SELECT cc.gross_capacity_mw
                    FROM capacity_changes cc
                    WHERE cc.reactor_id = r.id
                      AND cc.effective_date <= (g.year || '-12-31')
                    ORDER BY cc.effective_date DESC
                    LIMIT 1),
                   r.gross_capacity_mw
               ) as effective_gross,
               ROUND(g.electricity_gwh / (
                   COALESCE(
                       (SELECT cc.gross_capacity_mw
                        FROM capacity_changes cc
                        WHERE cc.reactor_id = r.id
                          AND cc.effective_date <= (g.year || '-12-31')
                        ORDER BY cc.effective_date DESC
                        LIMIT 1),
                       r.gross_capacity_mw
                   ) / 1000.0 * 8760
               ) * 100, 1) as capacity_factor
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE r.gross_capacity_mw > 0
          AND g.electricity_gwh / (
                   COALESCE(
                       (SELECT cc2.gross_capacity_mw
                        FROM capacity_changes cc2
                        WHERE cc2.reactor_id = r.id
                          AND cc2.effective_date <= (g.year || '-12-31')
                        ORDER BY cc2.effective_date DESC
                        LIMIT 1),
                       r.gross_capacity_mw
                   ) / 1000.0 * 8760
               ) * 100 > 110
        ORDER BY capacity_factor DESC
    """)
    rows = cur.fetchall()
    if rows:
        print(f"\n  WARNING: {len(rows)} entries still have CF > 110%:")
        for row in rows:
            print(f"    {row[1]} {row[2]} | {row[3]} | {row[4]:.1f} GWh | "
                  f"eff_gross={row[5]:.0f} MW | CF={row[6]}%")
        return False
    else:
        print("\n  SUCCESS: Zero entries with CF > 110%")
        return True


def verify_cf_above_100(cur):
    """Show entries with CF > 100% for awareness (not necessarily errors)."""
    cur.execute("""
        SELECT r.plant_name, r.unit_number, g.year,
               ROUND(g.electricity_gwh / (
                   COALESCE(
                       (SELECT cc.gross_capacity_mw
                        FROM capacity_changes cc
                        WHERE cc.reactor_id = r.id
                          AND cc.effective_date <= (g.year || '-12-31')
                        ORDER BY cc.effective_date DESC
                        LIMIT 1),
                       r.gross_capacity_mw
                   ) / 1000.0 * 8760
               ) * 100, 1) as capacity_factor
        FROM generation_annual g
        JOIN reactors r ON g.reactor_id = r.id
        WHERE r.gross_capacity_mw > 0
          AND g.electricity_gwh / (
                   COALESCE(
                       (SELECT cc2.gross_capacity_mw
                        FROM capacity_changes cc2
                        WHERE cc2.reactor_id = r.id
                          AND cc2.effective_date <= (g.year || '-12-31')
                        ORDER BY cc2.effective_date DESC
                        LIMIT 1),
                       r.gross_capacity_mw
                   ) / 1000.0 * 8760
               ) * 100 > 100
        ORDER BY capacity_factor DESC
        LIMIT 20
    """)
    rows = cur.fetchall()
    if rows:
        print(f"\n  INFO: {len(rows)} entries with CF 100-110% (may be normal):")
        for row in rows:
            print(f"    {row[0]} {row[1]} | {row[2]} | CF={row[3]}%")


def show_generation_count(cur):
    """Show current generation entry count."""
    cur.execute("SELECT COUNT(*) FROM generation_annual")
    count = cur.fetchone()[0]
    print(f"\n  Generation entries: {count}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    print("=" * 60)
    print("Nuclear Database — Capacity Changes Migration")
    print("=" * 60)

    # Step 1: Create table
    print("\n[1] Creating capacity_changes table...")
    create_capacity_changes_table(cur)

    # Step 2: Populate capacity changes
    print("\n[2] Populating capacity change records...")
    populate_capacity_changes(cur)

    # Step 3: Clean up bad generation data
    print("\n[3] Cleaning up bad generation data...")
    cleanup_bad_generation_data(cur)

    # Step 4: Fix reactor capacity values
    print("\n[4] Fixing reactor table capacity values...")
    fix_reactor_capacities(cur)

    # Step 5: Verify
    print("\n[5] Verification...")
    show_generation_count(cur)
    success = verify_no_impossible_cf(cur)
    verify_cf_above_100(cur)

    if success:
        conn.commit()
        print("\n" + "=" * 60)
        print("Migration complete — all changes committed.")
        print("=" * 60)
    else:
        print("\n  Rolling back — fix remaining issues before committing.")
        conn.rollback()

    conn.close()


if __name__ == '__main__':
    main()
