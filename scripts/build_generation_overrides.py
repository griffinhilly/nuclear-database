"""Build audit/pris_generation/overrides_eia.psv: reactor-years where a national source corrects IAEA PRIS.

Purpose: PRIS December 2021 is a copy of November for 90 US units + Bruce 1 (and a few other years);
  US EIA-923/906/759 unit data and Ontario IESO unit output give the true figures. Migration 031's
  builder applies this file last (source column names the national source).
Inputs:  audit/pris_generation/monthly_raw.json, nuclear_reactors.db (read-only), EIA-923/906/759 and
         IESO files downloaded to the session scratchpad on 2026-10-14 (paths below; re-download to rebuild).
Outputs: audit/pris_generation/overrides_eia.psv
Detector for the defect: scripts/pris_copied_month_check.py
last_run: 2026-10-14
"""
import json, csv, sqlite3, glob, os, sys
from collections import defaultdict
ROOT = r'C:\Users\griff\Projects\reg\nuclear-database'
OUT = ROOT + r'\audit\pris_generation\overrides_eia.psv'
d = json.load(open(ROOT + r'\audit\pris_generation\monthly_raw.json'))['rows']
pm = {(r[0], r[1], r[2]): r[3] for r in d}
c = sqlite3.connect(f'file:{ROOT}/nuclear_reactors.db?mode=ro'.replace('\\', '/'), uri=True)
db = {r[0]: r[1:] for r in c.execute('select pris_id,id,plant_name,unit_number from reactors where pris_id is not null')}

# our plant_name -> EIA Plant Id ; unit overrides
PLANT = {'Nine Mile Point': '2589', 'Dresden': '869', 'Ginna (R. E. Ginna)': '6122', 'Turkey Point': '621',
         'Quad Cities': '880', 'Palisades': '1715', 'Browns Ferry': '46', 'Robinson (H B Robinson)': '3251',
         'Monticello': '1922', 'Point Beach': '4046', 'Oconee': '3265', 'Salem': '2410', 'Diablo Canyon': '6099',
         'Peach Bottom': '3166', 'Surry': '3806', 'Prairie Island': '1925', 'Cooper': '8036',
         'Arkansas Nuclear One': '8055', 'Cook (Donald C. Cook)': '6000', 'Calvert Cliffs': '6011',
         'Hatch (Edwin I. Hatch)': '6051', 'Brunswick': '6014', 'Sequoyah': '6152',
         'Fitzpatrick (James A. Fitzpatrick)': '6110', 'Beaver Valley': '6040', 'St Lucie': '6045',
         'Millstone': '566', 'North Anna': '6168', 'Fermi': '1729', 'Davis Besse': '6149',
         'Farley (Joseph M. Farley)': '6001', 'Limerick': '6105', 'Hope Creek': '6118', 'McGuire': '6038',
         'LaSalle': '6026', 'Susquehanna': '6103', 'Watts Bar': '7722', 'Summer (V C Summer)': '6127',
         'Columbia': '371', 'Harris (Shearon Harris)': '6015', 'Catawba': '6036', 'Grand Gulf': '6072',
         'Vogtle': '649', 'Perry': '6020', 'Seabrook': '6115', 'Comanche Peak': '6145', 'Byron': '6023',
         'Braidwood': '6022', 'River Bend': '6462', 'Clinton': '204', 'Wolf Creek': '210', 'Callaway': '6153',
         'South Texas Project': '6251', 'Palo Verde': '6008', 'Pilgrim': '1590'}
UNIT = {('371', '1'): '2'}  # Columbia Generating Station reports as unit 2 (WNP-2)

def load923(y):
    e = list(csv.reader(open(f'../eia/nuc_{y}.psv', encoding='utf-8'), delimiter='|'))
    h = e[0]
    out = {}
    for r in e[1:]:
        x = dict(zip(h, r))
        out[(x["Plant Id"], x["Nuclear Unit Id"])] = (float(x['Net Generation (Megawatthours)']), r[0], x['Plant Name'])
    return out

def copied(y, m=12):
    return sorted(rid for (rid, yy, mm), v in pm.items() if yy == y and mm == m and (rid, y, m - 1) in pm
                  and round(v, 3) != 0 and round(v, 3) == round(pm[(rid, y, m - 1)], 3))

def pris_year(rid, y):
    return sum(pm.get((rid, y, m), 0) or 0 for m in range(1, 13))

FILES = {2021: 'EIA923_Schedules_2_3_4_5_M_12_2021_Final_Revision.xlsx', 2019: 'EIA923_Schedules_2_3_4_5_M_12_2019_Final_Revision.xlsx',
         2007: 'f906920_2007.xls'}
rows, skipped = [], []

def add_us(rid, y, eia, reason):
    rec = db[rid]
    pid = PLANT[rec[1]]
    unit = UNIT.get((pid, rec[2]), rec[2])
    if (pid, unit) not in eia:
        skipped.append((rid, y, rec, 'no EIA row')); return
    v, xrow, pname = eia[(pid, unit)]
    rows.append([rec[0], rid, f'{rec[1]} {rec[2]}', y, round(v / 1000, 3),
                 f'US EIA-923 {y}, Page 1 Generation and Fuel Data, plant {pid} unit {unit}' if y >= 2008 else
                 f'US EIA-906/920 {y}, Page 1 Generation and Fuel Data, plant {pid} unit {unit}',
                 f"{FILES[y]} excel row {xrow} ('{pname}'), col Net Generation (MWh) = {v:.0f}",
                 reason + f'; PRIS year sum {pris_year(rid, y):.3f}'])

e21 = load923(2021)
for rid in copied(2021):
    if rid == 53:
        continue  # Bruce 1, Canada: IESO below
    add_us(rid, 2021, e21, 'PRIS Dec-2021 = Nov-2021 (copied month)')
e19 = load923(2019)
add_us(639, 2019, e19, 'PRIS Apr-May 2019 = 0 while EIA shows 477+302 GWh')
if os.path.exists('../eia/nuc_2007.psv'):
    e07 = load923(2007)
    for rid in (764, 765):
        add_us(rid, 2007, e07, 'PRIS Dec-2007 = Nov-2007 (copied month)')
# Bruce 1 2021 from IESO
if len(sys.argv) > 1:
    rows.append([db[53][0], 53, 'Bruce 1', 2021, float(sys.argv[1]),
                 'CA IESO Generator Output and Capability 2021, generator BRUCEA-G1',
                 'PUB_GenOutputCapabilityMonth_202101..202112.csv, Measurement Output, sum Hour 1-24 (MW) all days /1000',
                 f'PRIS Dec-2021 = Nov-2021 (copied month); PRIS year sum {pris_year(53, 2021):.3f}'])
# Humboldt Bay 3 (PRIS 599) 1972 from EIA-759 utility file (GEN01..GEN12 in kWh)
rows.append([db[599][0], 599, f'{db[599][1]} {db[599][2]}', 1972, 363.133,
             'US EIA-759 1972 (utility file f7591972u.xls), PG&E plant HUMBOLDT BY, FUELNM NUCLEAR (single nuclear unit)',
             'f7591972u.xls sheet 1 excel row 5847: PLTCODE 334, CAPACITY 60000 kW, sum GEN01..GEN12 = 363,133,000 kWh',
             f'PRIS Dec-1972 = Nov-1972 (copied month); PRIS year sum {pris_year(599, 1972):.3f}'])
with open(OUT, 'w', encoding='utf-8', newline='') as f:
    f.write('reactor_id|pris_id|name|year|gwh_net|source|locator|reason\n')
    for r in rows:
        f.write('|'.join(str(x) for x in r) + '\n')
adj = sum(r[4] - pris_year(r[1], r[3]) for r in rows)
print('rows', len(rows), 'adjustment vs PRIS GWh', round(adj, 3), 'skipped', skipped)
big = sorted(rows, key=lambda r: -abs(r[4] - pris_year(r[1], r[3])))[:8]
for r in big: print(r[2], r[3], r[4], round(pris_year(r[1], r[3]), 3))
