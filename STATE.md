# Nuclear Database — State

**Phase**: Post-core development. WNA audit complete.

**Last worked on (Mar 16)**:
- WNA audit: scraped all 38 non-Chinese countries, matched 640/640 WNA reactors
- Added 6 missing UC reactors: Kaiga 5/6, Cape Nagloynyn 1/2, Leningrad 2-4, Shin-Hanul 3 (739 total)
- Updated 156 operational/UC reactor net capacities from WNA (>20 MWe threshold)
- Filled 13 missing dates (grid_connection + permanent_shutdown)
- Fixed Belgium shutdown dates (Doel 1/2, Tihange 1 life extensions)
- Fixed Wylfa 2 shutdown (2015 -> 2012), Kuosheng 2 shutdown (Jul -> Mar 2023)
- Status fixes: Kursk 1-2 (PS), Kursk 2-1 (Operational), Khmelnytskyi 3/4 (Suspended)
- Created RITM-200S model for floating NPP reactors

**Uncommitted**: All prior uncommitted work + WNA audit scripts + DB changes.

**Known issues**:
- 11 CF entries at 100-102% — confirmed plausible, no action needed
- Flamanville 3 + Taipingling 1 missing commercial_operation (still commissioning)
- 15 Ukrainian reactors no data after 2021 (war-related, not fixable)
- `fetch_missing_generation.py` imports deleted module — use `fix_generation_data.py`
- 121 shutdown reactor capacity diffs vs WNA — left as-is (PRIS authoritative for shutdown reactors)
- ~11 shutdown date diffs >30 days (historical reactors) — need PRIS spot-check, saved as TODO

**Next**:
- Commit + deploy to Fly.io (significant changes accumulated)
- Re-run generation backfill when 2025 PRIS data becomes available
