"""Replay all capacity alignment fixes from Mar 26 session onto remote DB."""
import sqlite3, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
conn = sqlite3.connect("nuclear_reactors.db")

def insert_cc(records):
    conn.executemany("""
        INSERT INTO capacity_changes (reactor_id, effective_date, gross_capacity_mw, net_capacity_mw, change_type, source, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, records)

# --- BELGIUM ---
# Doel 1/2
conn.execute("UPDATE reactors SET net_capacity_mw = 445, reference_power_mw = 445 WHERE id = 12")
conn.execute("UPDATE reactors SET net_capacity_mw = 445, reference_power_mw = 445 WHERE id = 13")
insert_cc([
    (12, "1975-02-15", 454.0, 392.0, "initial", "PRIS", "Original W 2-loop design rating"),
    (12, "2010-01-01", 454.0, 433.0, "uprate", "PRIS/INIS", "Steam generator replacement (MHI, Aug 2009); ~10% power uprate"),
    (12, "2019-01-01", 454.0, 445.0, "uprate", "PRIS/WNA", "Turbine replacement program; final uprated capacity"),
    (13, "1975-12-01", 454.0, 392.0, "initial", "PRIS", "Original W 2-loop design rating"),
    (13, "2005-01-01", 454.0, 433.0, "uprate", "PRIS/INIS", "Steam generator replacement (2004 campaign); ~10% power uprate"),
    (13, "2020-01-01", 454.0, 445.0, "uprate", "PRIS/WNA", "Turbine replacement program; final uprated capacity"),
])

# Doel 3
conn.execute("UPDATE reactors SET net_capacity_mw = 1006, reference_power_mw = 1006 WHERE id = 14")
insert_cc([
    (14, "1982-10-01", 1056.0, 890.0, "initial", "PRIS", "Original Framatome 3-loop design rating"),
    (14, "1993-09-22", 1056.0, 1006.0, "uprate", "PRIS/INIS", "SG replacement (44 days) + 10% power uprate; thermal 2785->3054 MWt"),
])

# Doel 4 (no uprate)
conn.execute("UPDATE reactors SET net_capacity_mw = 1026, reference_power_mw = 1026 WHERE id = 15")

# Tihange 1
conn.execute("UPDATE reactors SET net_capacity_mw = 962, reference_power_mw = 962 WHERE id = 16")
insert_cc([
    (16, "1975-10-01", 1009.0, 870.0, "initial", "PRIS", "Original Framatome 3-loop design rating; two 481 MW turbines"),
    (16, "1995-01-01", 1009.0, 931.0, "uprate", "PRIS/INIS", "SG replacement (MHI) + first phase uprate ~7%"),
    (16, "1997-01-01", 1009.0, 962.0, "uprate", "PRIS/INIS", "Second phase 8% uprate complete; thermal to 2873 MWt"),
])

# Tihange 2
conn.execute("UPDATE reactors SET net_capacity_mw = 1008, reference_power_mw = 1008 WHERE id = 17")
insert_cc([
    (17, "1983-06-01", 1055.0, 900.0, "initial", "PRIS", "Original W 3-loop design rating; thermal 2775 MWt"),
    (17, "1995-01-01", 1055.0, 950.0, "uprate", "PRIS/INIS", "4.5% core power uprate (no SG replacement); thermal 2775->2905 MWt; fuel cycle 12->15 months"),
    (17, "2001-08-11", 1055.0, 1008.0, "uprate", "PRIS/INIS/OSTI", "SG replacement (MHI, 17.5 days) + further 5.5% uprate; total 10%; thermal 2905->3064 MWt"),
])

# Tihange 3 (no uprate)
conn.execute("UPDATE reactors SET net_capacity_mw = 1038, reference_power_mw = 1038 WHERE id = 18")

# --- CHINESE AP1000s ---
conn.execute("UPDATE reactors SET net_capacity_mw = 1170 WHERE id = 72")
conn.execute("UPDATE reactors SET net_capacity_mw = 1170 WHERE id = 73")
conn.execute("UPDATE reactors SET net_capacity_mw = 1157 WHERE id = 95")
conn.execute("UPDATE reactors SET net_capacity_mw = 1157 WHERE id = 96")

# --- GERMAN PWRs ---
german = {
    205: (1402, [
        ("1985-04-18", 1468.0, 1268.0, "initial", "PRIS", "Original Siemens/KWU 4-loop design rating"),
        ("1993-01-01", 1468.0, 1324.0, "uprate", "PRIS", "Thermal stretch uprate; +56 MWe"),
        ("2000-01-01", 1468.0, 1392.0, "uprate", "PRIS", "Further thermal uprate + MUR; +68 MWe"),
        ("2010-01-01", 1468.0, 1402.0, "uprate", "PRIS", "Final MUR refinement; +10 MWe"),
    ]),
    200: (1410, [
        ("1988-04-09", 1485.0, 1285.0, "initial", "PRIS", "Original Konvoi design rating"),
        ("1988-01-01", 1485.0, 1310.0, "uprate", "PRIS", "Early stretch uprate; +25 MWe"),
        ("1993-01-01", 1485.0, 1330.0, "uprate", "PRIS", "Thermal optimization; +20 MWe"),
        ("1999-01-01", 1485.0, 1380.0, "uprate", "PRIS", "Major thermal uprate; +50 MWe"),
        ("2009-01-01", 1485.0, 1410.0, "uprate", "PRIS", "Final uprate + MUR (VDI 2048); +30 MWe"),
    ]),
    214: (1345, [
        ("1979-09-06", 1410.0, 1230.0, "initial", "PRIS", "Original Siemens/KWU 4-loop design rating"),
        ("1991-01-01", 1410.0, 1243.0, "uprate", "PRIS", "First stretch uprate; +13 MWe"),
        ("1993-01-01", 1410.0, 1255.0, "uprate", "PRIS", "Continued thermal optimization; +12 MWe"),
        ("1996-01-01", 1410.0, 1285.0, "uprate", "PRIS", "Further thermal uprate; +30 MWe"),
        ("2000-01-01", 1410.0, 1345.0, "uprate", "PRIS", "Final uprate + MUR; +60 MWe"),
    ]),
    202: (1410, [
        ("1986-12-22", 1480.0, 1307.0, "initial", "PRIS", "Original Siemens/KWU 4-loop design rating"),
        ("1999-01-01", 1480.0, 1370.0, "uprate", "PRIS", "Thermal stretch uprate; +63 MWe"),
        ("2008-01-01", 1480.0, 1410.0, "uprate", "PRIS", "Final uprate + MUR; +40 MWe"),
    ]),
    199: (1335, [
        ("1988-06-20", 1406.0, 1242.0, "initial", "PRIS", "Original Konvoi design rating"),
        ("2000-01-01", 1406.0, 1329.0, "uprate", "PRIS", "Major thermal uprate; +87 MWe"),
        ("2014-01-01", 1406.0, 1335.0, "uprate", "PRIS", "Final MUR refinement; +6 MWe"),
    ]),
    201: (1310, [
        ("1989-04-15", 1400.0, 1225.0, "initial", "PRIS", "Original Konvoi design rating"),
        ("1992-01-01", 1400.0, 1269.0, "uprate", "PRIS", "Thermal stretch uprate; +44 MWe"),
        ("2005-01-01", 1400.0, 1310.0, "uprate", "PRIS", "Final uprate + MUR; +41 MWe"),
    ]),
    203: (1360, [
        ("1985-02-01", 1430.0, 1289.0, "initial", "PRIS", "Original Siemens/KWU 4-loop design rating"),
        ("1990-01-01", 1430.0, 1325.0, "uprate", "PRIS", "Thermal stretch uprate; +36 MWe"),
        ("1995-01-01", 1430.0, 1360.0, "uprate", "PRIS", "Final uprate; +35 MWe"),
    ]),
    208: (1240, [
        ("1977-01-31", 1300.0, 1178.0, "initial", "PRIS", "Original Siemens/KWU 4-loop design rating"),
        ("1995-01-01", 1300.0, 1240.0, "uprate", "PRIS", "Thermal stretch uprate + MUR; +62 MWe"),
    ]),
    215: (340, [
        ("1969-03-31", 357.0, 283.0, "initial", "PRIS", "Original Siemens 2-loop design rating"),
        ("1970-01-01", 357.0, 340.0, "uprate", "PRIS", "Early operational stabilization; net settled at 340 MWe"),
    ]),
    206: (1275, [
        ("1982-06-17", 1345.0, 1225.0, "initial", "PRIS", "Original Siemens/KWU 4-loop design rating"),
        ("1994-01-01", 1345.0, 1275.0, "uprate", "PRIS", "Thermal stretch uprate; +50 MWe"),
    ]),
    207: (1167, [
        ("1975-02-26", 1225.0, 1146.0, "initial", "PRIS", "Original Siemens/KWU 4-loop design rating"),
        ("1995-01-01", 1225.0, 1167.0, "uprate", "PRIS", "Thermal stretch uprate; +21 MWe"),
    ]),
    216: (640, [
        ("1972-05-19", 672.0, 630.0, "initial", "PRIS", "Original Siemens/KWU 4-loop design rating"),
        ("1985-01-01", 672.0, 640.0, "uprate", "PRIS", "Thermal stretch uprate; +10 MWe"),
    ]),
}

for rid, (ref, changes) in german.items():
    conn.execute("UPDATE reactors SET net_capacity_mw = ?, reference_power_mw = ? WHERE id = ?", (ref, ref, rid))
    insert_cc([(rid, *c) for c in changes])

conn.commit()

# VERIFY
cc = conn.execute("SELECT COUNT(*) FROM capacity_changes").fetchone()[0]
d1 = conn.execute("SELECT net_capacity_mw FROM reactors WHERE id = 12").fetchone()
isar = conn.execute("SELECT net_capacity_mw FROM reactors WHERE id = 200").fetchone()
haiyang = conn.execute("SELECT net_capacity_mw FROM reactors WHERE id = 72").fetchone()
print(f"capacity_changes: {cc} (expected 105)")
print(f"Doel 1 net: {d1[0]} (expected 445)")
print(f"Isar 2 net: {isar[0]} (expected 1410)")
print(f"Haiyang 1 net: {haiyang[0]} (expected 1170)")
conn.close()
print("All capacity fixes replayed successfully.")
