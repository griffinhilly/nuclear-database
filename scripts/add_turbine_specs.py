#!/usr/bin/env python3
"""Add turbine specifications to design_series_specs table."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nuclear_reactors.db')


def add_columns(conn):
    """Add turbine columns if they don't exist."""
    new_cols = [
        ('number_of_turbines', 'INTEGER'),
        ('turbine_speed_rpm', 'INTEGER'),
        ('low_pressure_sections', 'INTEGER'),
        ('live_steam_pressure_bar', 'REAL'),
    ]
    for col, dtype in new_cols:
        try:
            conn.execute(f"ALTER TABLE design_series_specs ADD COLUMN {col} {dtype}")
            print(f"  Added column: {col}")
        except Exception:
            print(f"  Column already exists: {col}")


def populate(conn):
    """Update all design series with turbine specs."""
    # Helper to build spec dicts concisely
    def s(nt, rpm, lp, steam):
        return {
            'number_of_turbines': nt,
            'turbine_speed_rpm': rpm,
            'low_pressure_sections': lp,
            'live_steam_pressure_bar': steam,
        }

    data = {
        # ===== BWR designs (direct cycle) =====
        'BWR/1':    s(1, 1800, 2, 65.0),
        'BWR/2':    s(1, 1800, 2, 65.0),
        'BWR/3':    s(1, 1800, 3, 67.0),
        'BWR/4':    s(1, 1800, 3, 67.0),
        'BWR/5':    s(1, 1800, 4, 67.0),
        'BWR/6':    s(1, 1800, 4, 67.0),
        'ABWR':     s(1, 1500, 4, 67.0),
        'BWR/69':   s(1, 1500, 2, 65.0),
        'BWR/72':   s(1, 1500, 2, 65.8),   # Gundremmingen data
        'BWR/75':   s(1, 1500, 2, 65.0),
        'BWR/G1':   s(1, 1500, 2, 65.0),
        'BWR/G2':   s(1, 1500, 2, 65.0),
        'BWR/G3':   s(1, 1500, 2, 65.0),

        # ===== Westinghouse PWR =====
        'W 1-Loop':  s(1, 1800, 2, 52.0),
        'W 2-Loop':  s(1, 1800, 2, 54.0),
        'W 3-Loop':  s(1, 1800, 3, 60.0),
        'W 4-Loop':  s(1, 1800, 3, 70.0),
        'SNUPPS':    s(1, 1800, 3, 70.0),
        'AP1000':    s(1, 1800, 3, 57.0),

        # ===== CE PWR =====
        'CE Pre-System 80': s(1, 1800, 3, 62.0),
        'CE System 80':     s(1, 1800, 3, 68.0),

        # ===== B&W PWR =====
        'B&W Lowered-Loop': s(1, 1800, 2, 65.0),
        'B&W Raised-Loop':  s(1, 1800, 2, 65.0),
        'B&W 2-Loop':       s(1, 1500, 2, 65.0),

        # ===== French PWR =====
        'CP0':   s(1, 1500, 3, 56.0),
        'CP1':   s(1, 1500, 3, 56.0),
        'CP2':   s(1, 1500, 3, 57.0),
        'M310':  s(1, 1500, 3, 58.0),
        'P4':    s(1, 1500, 3, 60.0),
        'N4':    s(1, 1500, 3, 73.0),
        'EPR':   s(1, 1500, 3, 78.0),

        # ===== Siemens PWR =====
        'Siemens 2-Loop': s(1, 1500, 2, 55.0),
        'Siemens 3-Loop': s(1, 1500, 2, 58.0),
        'Siemens 4-Loop': s(1, 1500, 3, 60.0),
        'Pre-Konvoi':     s(1, 1500, 3, 63.0),
        'Konvoi':         s(1, 1500, 3, 63.0),

        # ===== MHI PWR (Japan) =====
        'MHI 2-Loop': s(1, 1500, 2, 56.0),
        'MHI 3-Loop': s(1, 1500, 3, 58.0),
        'MHI 4-Loop': s(1, 1500, 3, 63.0),

        # ===== Korean PWR =====
        'OPR-1000': s(1, 1800, 2, 65.0),
        'APR1400':  s(1, 1800, 3, 68.0),

        # ===== Chinese PWR =====
        'CAP1000':   s(1, 1500, 3, 57.0),
        'CAP1400':   s(1, 1500, 3, 68.0),
        'CNP-300':   s(1, 1500, 2, 55.0),
        'CNP-600':   s(1, 1500, 3, 55.0),
        'CNP-1000':  s(1, 1500, 3, 57.0),
        'CPR-1000':  s(1, 1500, 3, 57.0),
        'HPR1000':   s(1, 1500, 3, 68.0),
        'ACPR-1000': s(1, 1500, 3, 58.0),
        'ACP100':    s(1, 1500, 2, 40.0),

        # ===== VVER =====
        'VVER-210':       s(1, 1500, None, None),
        'VVER-365':       s(1, 1500, None, None),
        'VVER-440/179':   s(2, 1500, 2, 44.0),
        'VVER-440/187':   s(2, 1500, 2, 44.0),
        'VVER-440/213':   s(2, 1500, 2, 44.0),
        'VVER-440/230':   s(2, 1500, 2, 44.0),
        'VVER-440/270':   s(2, 1500, 2, 44.0),
        'VVER-1000/302':  s(1, 1500, 4, 60.0),
        'VVER-1000/320':  s(1, 1500, 4, 60.0),
        'VVER-1000/338':  s(1, 1500, 4, 60.0),
        'VVER-1000/412':  s(1, 1500, 4, 60.0),
        'VVER-1000/428':  s(1, 1500, 4, 60.0),
        'VVER-1000/428M': s(1, 1500, 4, 60.0),
        'VVER-1000/446':  s(1, 1500, 4, 60.0),
        'VVER-1200':      s(1, 1500, 4, 68.0),
        'VVER-1200/392B': s(1, 1500, 4, 68.0),
        'VVER-1200/392M': s(1, 1500, 4, 68.0),
        'VVER-1200/491':  s(1, 1500, 4, 68.0),
        'VVER-1200/509':  s(1, 1500, 4, 68.0),
        'VVER-1200/523':  s(1, 1500, 4, 68.0),

        # ===== CANDU / PHWR =====
        'CANDU':     s(1, 1800, 3, 47.0),
        'CANDU 500': s(1, 1800, 3, 47.0),
        'CANDU 6':   s(1, 1800, 3, 47.0),
        'CANDU 750': s(1, 1800, 3, 47.0),
        'CANDU 850': s(1, 1800, 3, 47.0),
        'IPHWR':     s(1, 1500, 2, 43.0),
        'PHWR':      s(1, 1500, 3, 45.0),
        'PHWR-700':  s(1, 1500, 3, 47.0),
        'KWU PHWR':  s(1, 1500, 3, 47.0),

        # ===== Gas-cooled reactors =====
        'Magnox': s(3, 1500, 2, 35.0),   # Varied by station; typical ~3 turbines
        'AGR':    s(1, 1500, 3, 160.0),   # Superheated steam
        'UNGG':   s(3, 1500, 2, 35.0),    # Typically 2-4, use 3 representative

        # ===== RBMK =====
        'RBMK':      s(2, 1500, 2, 65.0),
        'RBMK-1000': s(2, 1500, 2, 65.0),
        'RBMK-1500': s(2, 1500, 2, 65.0),
        'EGP-6':     s(1, 1500, 2, 65.0),

        # ===== Fast breeder reactors (sodium-cooled) =====
        'BN-20':         s(None, None, None, None),   # Experimental, very small
        'BN-350':        s(1, 1500, None, None),
        'BN-600':        s(1, 1500, 4, 130.0),
        'BN-800':        s(1, 1500, 4, 130.0),
        'Phenix':        s(1, 1500, 2, None),
        'Super-Phenix':  s(1, 1500, 3, None),
        'PFR':           s(1, 1500, 2, None),
        'PFBR':          s(1, 1500, 2, None),
        'Monju':         s(1, 1500, 2, None),
        'CFR-600':       s(1, 1500, None, None),
        'BREST-OD-300':  s(1, 1500, None, None),
        'DFR':           s(1, 1500, None, None),       # Dounreay Fast Reactor
        'KNK':           s(1, 1500, None, None),       # Compact sodium-cooled
        'LMFBR':         s(1, 1500, None, None),       # Liquid metal fast breeder (generic)

        # ===== HTGR / Pebble bed =====
        'Fort St. Vrain':   s(1, 1800, 2, None),
        'Peach Bottom HTGR': s(1, 1800, None, None),
        'THTR-300':          s(1, 1500, 2, None),
        'AVR':               s(1, 1500, None, None),
        'HTR-PM':            s(1, 1500, 2, None),

        # ===== Prototype / unique designs =====
        'AM-1':    s(1, 1500, None, None),
        'AMB-100': s(1, 1500, None, None),
        'AMB-200': s(1, 1500, None, None),
        'SGHWR':   s(1, 1500, 2, None),
        'ATR':     s(1, 1500, 2, None),
        'KS 150':  s(1, None, None, None),
        'Agesta':  s(None, None, None, None),   # Primarily district heating
        'BR-3':    s(1, 1500, None, None),       # Belgian test reactor
        'CVTR':    s(1, 1800, None, None),       # Carolinas-Virginia Tube Reactor
        'Saxton':  s(1, 1800, None, None),       # Small experimental PWR
        'BLWR-250': s(1, 1500, None, None),      # Boiling light water reactor prototype
        'EL-4':    s(1, 1500, None, None),        # Heavy water gas-cooled reactor
        'HWGCR':   s(1, 1500, None, None),        # Heavy Water Gas Cooled Reactor
        'OCR':     s(1, 1500, None, None),        # Organic Cooled Reactor
        'SGR':     s(1, 1500, None, None),        # Sodium Graphite Reactor
        'PLWBR':   s(1, 1500, None, None),        # Pressurized Light Water Breeder Reactor
        'CAREM':   s(1, 1500, None, None),        # Argentine small modular reactor
        'KLT-40S': s(1, 1500, None, None),        # Floating NPP turbine
    }

    updated = 0
    missing = []
    for ds, specs in data.items():
        cur = conn.execute("""
            UPDATE design_series_specs
            SET number_of_turbines = ?, turbine_speed_rpm = ?,
                low_pressure_sections = ?, live_steam_pressure_bar = ?
            WHERE design_series = ?
        """, (specs['number_of_turbines'], specs['turbine_speed_rpm'],
              specs['low_pressure_sections'], specs['live_steam_pressure_bar'], ds))
        if cur.rowcount == 0:
            missing.append(ds)
        else:
            updated += 1
    conn.commit()

    print(f"\nUpdated {updated} design series")
    if missing:
        print(f"WARNING: {len(missing)} design series not found in table: {missing}")

    # Check for any design series in the table that we didn't cover
    all_ds = [r[0] for r in conn.execute("SELECT design_series FROM design_series_specs").fetchall()]
    uncovered = [ds for ds in all_ds if ds not in data]
    if uncovered:
        print(f"WARNING: {len(uncovered)} design series in table not covered by script: {uncovered}")


if __name__ == '__main__':
    conn = sqlite3.connect(DB_PATH)

    print("Adding turbine columns...")
    add_columns(conn)

    print("\nPopulating turbine data...")
    populate(conn)

    # Print summary
    print("\nColumn fill rates:")
    total = conn.execute("SELECT COUNT(*) FROM design_series_specs").fetchone()[0]
    for col in ['number_of_turbines', 'turbine_speed_rpm',
                'low_pressure_sections', 'live_steam_pressure_bar']:
        count = conn.execute(
            f"SELECT COUNT(*) FROM design_series_specs WHERE {col} IS NOT NULL"
        ).fetchone()[0]
        print(f"  {col}: {count}/{total}")

    conn.close()
    print("\nDone.")
