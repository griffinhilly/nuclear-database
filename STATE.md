# Nuclear Database — State

**Phase**: Post-core development. All major audits complete. Deployed.

**Last worked on (Mar 16)**:
- WNA audit: scraped 38 countries, matched 640/640 reactors, added 6 UC, updated 156 capacities, filled 13 dates, fixed statuses
- Committed and deployed to Fly.io (723163f)

**Uncommitted**: Wylfa 2 + Kuosheng 2 date fixes, Khmelnytskyi 3/4 -> Suspended (applied after commit).

**Known issues**:
- 11 CF entries at 100-102% — confirmed plausible, no action needed
- Flamanville 3 + Taipingling 1 missing commercial_operation (still commissioning)
- 15 Ukrainian reactors no data after 2021 (war-related, not fixable)
- `fetch_missing_generation.py` imports deleted module — use `fix_generation_data.py`
- 121 shutdown reactor capacity diffs vs WNA — left as-is (PRIS authoritative)
- ~11 shutdown date diffs >30 days — need PRIS spot-check (TODO in PLAN.md)

**Next**:
- Commit remaining post-deploy fixes (Wylfa 2, Kuosheng 2, Khmelnytskyi 3/4)
- Re-run generation backfill when 2025 PRIS data becomes available
