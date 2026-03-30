# Nuclear Database — Memory

## Current State (Mar 2026)
- **739 reactors**: 417 Operational, 72 Under Construction, 24 Suspended, 226 Permanent Shutdown
- **119 planned reactors** with likelihood ratings (High/Medium/Low)
- **39 countries**, all verified against IAEA PRIS
- **All reactors have coordinates** — verified against Wikipedia GeoData (gold standard)
- **All reactors have owners** — 154 distinct owners, all with descriptions
- **Design lineages**: 24 families, 123 series, 100% coverage
- **Entity descriptions**: 708 total across 7 entity types. **All manual** — 0 template plant descriptions, 0 template owner descriptions remaining
- **Generation data**: 19,818 entries, 0 CF > 102%, 11 entries at 100-102% (plausible per industry contacts)
- **Capacity changes**: 106 records for 47 reactors (Belgium SG+uprate, Germany thermal stretch+MUR, US EPU/MUR, Korean rerating, etc.)
- **Capacity alignment**: COMPLETE — 229/229 reactors aligned. `net_capacity_mw` = `reference_power_mw` = current PRIS RUP (or NRC/WNA where PRIS stale)
- Live at https://nuclear-database.fly.dev/

Session history: see `guides/session-log.md`

## Gotchas
- `fly ssh` doesn't work from Git Bash on Windows (handle error). Use PowerShell or cmd if needed.
- `fly.exe` is at `~/.fly/bin/fly.exe` (not on PATH in bash)
- Global electricity data in app.py is hardcoded dict (1970-2024) from EI Statistical Review
- Reactor `name` column doesn't exist — use `plant_name` + `unit_number`
- Python print with Unicode chars fails on Windows cp1252 — add `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
- Chinese plant naming is complex: same site can have different `plant_name` entries for different phases (Shidao Bay vs Shidaowan, Qinshan 1/2/3)
- PRIS blocks Python `requests` via TLS fingerprinting — must use `curl` via subprocess
- `fetch_missing_generation.py` imports from deleted `fetch_pris_generation.py` — cannot run as-is. Use `fix_generation_data.py` for PRIS data fixes.
- Chapelcross/Sellafield generation data is station-level divided across units (identical values per unit) — all entries are approximations
- WNA "Gross Capacity" field sometimes reports net/reference power, not true gross (discovered for Browns Ferry: WNA=1256, actual gross=1310; Cook 2: WNA=1151, PRIS=1231)
- PRIS itself can have stale values — both gross and RUP. Browns Ferry EPU completed 2019, PRIS still showed pre-EPU 1200 MWe in 2026 (actual: 1256). For US reactors, verify against NRC/WNA before trusting PRIS.
- **Capacity source priority**: NRC (US only) > WNA > PRIS for operational reactors. PRIS is authoritative for shutdown reactors (usually). Always cross-reference when gaps are large.
- Bad generation data deleted: Bruce 1&2 layup (30), Wolsong 1 spikes (3), Bruce 6 MCR (2), Quad Cities 1 impossible (2), Sendai 1 (2), Takahama 3 (1), Wolsong 2 (1) = 41 total
- 11 CF 100-102% entries remain — all plausible per industry contacts (Mark confirms ~101% possible for US units over a full year)

Data quality notes: see `guides/data-quality.md`

## Decisions
- IAEA "first concrete pour" = under construction. Anything less = planned.
- Suspended status used for: post-Fukushima Japan (14 reactors), India Tarapur 1/2, India Rajasthan 1, China CEFR, USA Palisades, Ukraine Khmelnytskyi 3/4 (war-related)
- Fly.io as primary deployment over Render (persistent volumes, better control)
- `start.sh` always copies DB on deploy (no conditional check) — simpler, ensures fresh data
- Plant names use proper diacritics/Unicode (Krümmel not Kruemmel, Zaporizhzhia not Zaporozhye)
- Wikipedia GeoData coordinates are the gold standard — never dismiss small (<1km) discrepancies
- Multi-site complexes (Kursk, Leningrad, Novovoronezh, Hanul/Shin-Hanul) have per-site coordinates. **Decision (Madi, Mar 16): treat as separate plants.** Old and new generations are physically separate construction sites 1-2 km apart.
- WNA audit capacity strategy (Mar 16): updated operational/UC reactor net capacities from WNA (>20 MWe threshold), left shutdown reactors at PRIS values. Superseded by Mar 26-29 capacity alignment audit which set all reactors to net = ref = PRIS RUP (or NRC/WNA where PRIS stale).
- Korean "Saeul" renaming (Shin-Kori 3-6 → Saeul 1-4) not applied — keeping PRIS naming for DB consistency. WNA audit script has name overrides for matching.
- **`net_capacity_mw` = PRIS Reference Unit Power** (current/final operating capacity), not Design Net Capacity. Original design values preserved in `capacity_changes` initial records. Decision made Mar 26 after discovering systematic design-vs-operating discrepancy across 229 reactors.
- **Model detail page uses design_series grouping** when a model name is a subset of a broader series (e.g., "W (2-loop)" promotes to "W 2-Loop" showing all 19 reactors). Guard prevents promotion when a model spans multiple design_series.
