"""Flag PRIS reactor-months whose value equals the previous month (copied-month defect).

Purpose: catch the PRIS defect found 2026-10-14 (Dec-2021 = Nov-2021 for 90 US units + 1 CAN unit).
Inputs:  audit/pris_generation/monthly_raw.json (as written by scripts/pris_generation_pull.py;
         key "rows" = [ReactorId, Year, Month, Energy_GWh_net, row_count]).
Outputs: stdout report grouped by year; exit code 1 if any hit, 0 if none.
Usage:   python scripts/pris_copied_month_check.py [path/to/monthly_raw.json]
last_run: 2026-10-14
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'audit' / 'pris_generation' / 'monthly_raw.json'
rows = json.loads(path.read_text(encoding='utf-8'))['rows']
val = {(int(r[0]), int(r[1]), int(r[2])): r[3] for r in rows if r[3] is not None}

hits = defaultdict(list)  # year -> [(reactor, month, value)]
for (rid, y, m), v in val.items():
    prev = (rid, y, m - 1) if m > 1 else (rid, y - 1, 12)
    if prev in val and round(v, 3) != 0 and round(v, 3) == round(val[prev], 3):
        hits[y].append((rid, m, v))

total = sum(len(h) for h in hits.values())
print(f'{path}: {len(val)} reactor-months; {total} equal to previous month (non-zero, 3 dp)')
for y in sorted(hits):
    by_month = defaultdict(list)
    for rid, m, v in sorted(hits[y]):
        by_month[m].append(rid)
    parts = ', '.join(f'm{m:02d}: {len(r)}' for m, r in sorted(by_month.items()))
    print(f'{y}: {len(hits[y])} hits ({parts})')
    for rid, m, v in sorted(hits[y]):
        print(f'    reactor {rid} {y}-{m:02d} = {v:.3f} GWh')
sys.exit(1 if total else 0)
