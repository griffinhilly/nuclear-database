# Nuclear Database — Memory

## Current State (Jul 2026)
- **Generation data through 2025** (backfilled Jul 6: 93.3% of operational fleet for 2025; 2024 raw total 2426.2 TWh, 2025 raw total 2622.8 TWh). Cooling audit complete (per-unit, US fleet). All entity descriptions complete (0 missing). pris_id integrity repaired + guarded (validator checks 12-14); ground-truth map `pris_id_map_2026-07.json`.
- **Constants audit + vendor verification (Jul 20-21, migrations 016-018)**: design-spec fixes (turbine-speed class + 9 values), planned_reactors fixes (Duwayhin fabrication), and the **zero-doubt policy** (Griffin): reactor_details vendor fields show ONLY per-reactor-verified values (902 visible, 2,043 NULLed, originals in `reactor_details_unverified_archive`). 593 sourced corrections await Noah/Dirk (`verification_2026-07/noah_dirk_consult_2026-07.md` — their attestations are gospel; append to `final_verdicts.psv` visible=yes in the same change that writes the DB, or validator check 15 fails). Ledger: `constants_audit_2026-07.md`. Design-spec completion pass (migration 019) staged+paused — resume protocol in PLAN.md.

## Prior State (May 2026)
- **738 reactors**: 417 Operational, 76 Under Construction, 22 Suspended, 223 Shutdown
  - (Mar 2026 was 739 / 72 / 24 / 226 "Permanent Shutdown". May 28 Noah review: status "Permanent Shutdown" renamed to "Shutdown"; +Kursk 2-3 & Darlington SMR-1 as UC; Khmelnytskyi 3/4 Suspended->UC; Madras-1 ->Suspended; CEFR ->Operational; Lungmen 1/2 + Baltic-1 moved reactors->planned as cancelled-construction.)
- **123 planned reactors** with likelihood ratings (High/Medium/Low)
- **39 countries**, all verified against IAEA PRIS
- **All reactors have coordinates** — verified against Wikipedia GeoData (gold standard)
- **All reactors have owners** — 154 distinct owners, all with descriptions
- **Design lineages**: 24 families, 123 series, 100% coverage
- **Entity descriptions**: 708 total across 7 entity types. **All manual** — 0 template plant descriptions, 0 template owner descriptions remaining
- **Generation data**: 20,181 entries through 2025; public CF-anomaly endpoint = 0 (validator check 14 mirrors it); 11 entries at 100-102% vs net (plausible per industry contacts)
- **Capacity changes**: 106 records for 47 reactors (Belgium SG+uprate, Germany thermal stretch+MUR, US EPU/MUR, Korean rerating, etc.)
- **Capacity alignment**: COMPLETE — 229/229 reactors aligned. `net_capacity_mw` = `reference_power_mw` = current PRIS RUP (or NRC/WNA where PRIS stale)
- Live at https://nuclear-database.fly.dev/

- **Cooling audit (Apr 3-4)**: 9 plants fixed (Doel 3/4, NMP 2, Hope Creek, Leningrad 2, Kursk 2, Novovoronezh 2, St. Laurent B, Dampierre, Chinon B). Root cause: script assigned per-plant not per-unit. Follow-up needed: Fermi 2, Tarapur 3/4, US mech-vs-natural-draft, China inland fragility.

- **Noah review (May 28)**: ~45 external corrections from Noah, verified by 6 parallel research agents vs IAEA PRIS/WNA (asymmetric bar: default Noah unless overwhelming evidence). Applied via migrations 002-008 + a code-side status rename + 3 new validate_db.py checks. See `noah_review.md` for the full ledger. Net: many real model-code/naming errors fixed (Kola 3/4 V-213, Kursk II V-510K, Novovoronezh 1/2, Khmelnytskyi 3/4 model+status, Vandellos UNGG, Fuqing M310+, etc.). 3 OVERRIDES were initially logged (Ling'ao M310, Lianjiang CAP1000, Kudankulam V-412), **all REVERSED 2026-06-04** — see next bullet.

- **Override reversal (Jun 4, migration 010)**: Noah replied with sources and held his ground; all three overrides resolve in his favour. **Ling'ao 1/2 → M310+** (Griffin-approved taxonomy; Daya Bay 1/2 stay M310 — original Framatome M310 vs CGN improved/localized). **Lianjiang 3/4 → CAP1400/Guohe One, 1534 gross/1400 net** (China MEE EIA notice + WNA/WNN/Wikipedia/GEM confirm SPIC State-Nuclear, NOT a Shidaowan conflation; Lianjiang 1/2 stay CAP1000 Phase I). **Kudankulam 3/4 → V-412M, 5/6 → V-412T**; **Tianwan 7/8 → V-491T, Xudabao 3/4 → V-491S** (Q2 suffixes, now sourced to OKB Gidropress 2021 book — the designer's own designations; PRIS/WNA carry generic codes). **Bonus fix:** Tianwan 5/6 were wrongly CPR-1000 → **ACPR-1000** (CNNC; WNA/WNN/Wikipedia), surfaced by Noah's M310+ explanation; M310+ lineage description de-contradicted. Validator clean (54 pre-existing WARN unchanged). With this, **every Noah correction is accepted.** Remaining: manual entity_descriptions for the 4 new VVER models.

- **Jul 6 session (migrations 011-015)**: Novovoronezh-5 V-187 series fix; US cooling audit (40 per-unit fixes; ledger `cooling_audit_2026-07.md`); 2025 PRIS backfill; **pris_id corruption found by spec-blind review + repaired** (ledger `pris_id_repair_2026-07.md`). World-electricity denominator rebase = OPEN decision (dict ~15% low vs EI; share chart overstates nuclear).

Session history: see `guides/session-log.md`

## Gotchas
- **Fields with no internal-consistency check are the highest fabrication risk** — a wrong constructor/vendor name offends no validator and contradicts no other table, so it never earns an audit. Audit such fields *because* nothing can catch them. (Jul 20: 4 systematic bug classes found in never-audited heuristic fields — NSSS-vendor-as-constructor, RDM-RPV default for KWU plants, licensor-as-constructor, blanket LMZ/Izhora with pre-1998 Atomstroyexport anachronisms. Ledger: constants_audit_2026-07.md.)
- **Agent-facing data extracts must include every column needed to judge a mismatch** — a Jul 20 sample extract omitted gross_capacity, so agents compared sources' gross MWe against DB net and produced 2 false-positive WRONGs. Include gross+net (or all sibling columns) in any verification extract.
- **Verification fan-outs: if WebSearch dies, agents silently degrade to memory-only verdicts** — one Jul 21 agent "corrected" Konvoi's real 18x18 lattice from priors. Every verification-agent prompt must require BLOCKED when search is unavailable; quarantine (never merge) results from search-dead agents. Batch confirm-rates also vary wildly between agents (6%-74%) — treat cross-batch rates as uncalibrated; Noah/Dirk review is the calibration backstop for WRONG proposals.
- Ghost Flask process lingers on ports 5001+ — kill by port/PID (`netstat -ano | grep :PORT` then `taskkill //F //PID N`), NEVER `taskkill //IM python.exe` (kills unrelated sessions).
- **pris_id is load-bearing and was silently wrong for 24 reactors** (13 duplicates + 5 dead/foreign ids + 6 NULLs, fixed Jul 6 in migration 015). Origin (git archaeology): the Feb 14 backfill session wrote hand/model-guessed ids from `KNOWN_PRIS_IDS` (in the never-committed `fetch_pris_generation.py`), then the postback scraper corrected only PRIS-**Operational** reactors — the guesses survived on exactly the shutdown/renamed/unlisted units the scraper couldn't see. Full story: `pris_id_repair_2026-07.md`. Any backfill keyed on pris_id propagates identity errors into generation data. Before trusting a pris_id, check it against `pris_id_map_2026-07.json`; validator check 12 hard-fails duplicates. Symptom of past damage: byte-identical generation values on two reactors in the same year.
- **PRIS renames reactors**: Shin-Kori 3/4 are now SAEUL-1/2 in PRIS (DB keeps Shin-Kori naming; pris_ids 885/886). Name-matching PRIS pages needs alias awareness (GOESGEN, KRSKO, ZAPORIZHZHYA, CHASNUPP=Chashma, KANUPP=Karachi, ANO=Arkansas Nuclear One).
- **Shidaowan Guohe One 1 has NO PRIS page** (pris_id NULL since migration 015) — its generation needs a non-PRIS source (WNA/CNNC). Do not "find" it an id; the CAP1400 demo is absent from PRIS as of Jul 2026.
- **Subagent CF-flag rationalization (process)**: the Jul 6 orchestrator saw 21 CF>102% flags incl. 200%+ values on shutdown reactors and wrote them off as "gross-vs-net artifacts". A 216% CF cannot be a basis artifact (~5-8% max). Treat any CF>110% flag as corruption-until-proven-otherwise; the flag that looks explainable is the one that isn't.
- **Dungeness B 1/2 2020-21**: PRIS shows small NEGATIVE electricity (house-load during defueling); DB convention stores no <=0 rows, so DB's older positive rows for those years stand (known, accepted).
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
- `populate_reactor_details.py` assigns cooling per plant name — any multi-generation site with mixed cooling needs unit-level logic. Check new plants against this pattern.
- Induced-draft cooling towers are low-profile (~30m) and hard to spot on satellite vs. natural-draft hyperbolic towers (~150-170m). Don't rely solely on satellite for cooling type verification.
- Chinon B uses mechanical-draft towers (not natural draft) — unique in the French fleet, driven by UNESCO Loire Valley landscape constraints.
- Bad generation data deleted: Bruce 1&2 layup (30), Wolsong 1 spikes (3), Bruce 6 MCR (2), Quad Cities 1 impossible (2), Sendai 1 (2), Takahama 3 (1), Wolsong 2 (1) = 41 total
- 11 CF 100-102% entries remain — all plausible per industry contacts (Mark confirms ~101% possible for US units over a full year)
- **PRIS reactor-type codes can leak into the `models.name` field** — found a model literally named `"25"` (WITH quote chars) used by US prototypes (Vallecitos, Saxton). The quotes meant a naive `WHERE name='25'` missed it. `validate_db.py` check 7 now flags numeric-only model names.
- **Auto-numbered units (R1)**: the build synthesized integer unit_numbers even where real plants use letters (Biblis A/B, Gundremmingen A/B/C) or where site≠plant (Calder Hall/Windscale on the Sellafield site). Noah's general note. Fixed those; no clean automated check (reactor_id transliteration mismatches like Khmelnitski≠Khmelnytskyi make it un-automatable) — watch for it when adding plants.
- **Noah's VVER suffix convention** (V-491S/T, V-412M/T) is NOT in IAEA PRIS/WNA (they show plain V-491/V-412). Some suffixes ARE documented (V-510K, V-213+). Treat undocumented suffixes as Noah-internal until sourced.
- **`reactors.status` canonical set is now {Operational, Under Construction, Suspended, Shutdown}** (no more "Permanent Shutdown"). `validate_db.py` check 6 enforces this. Note `app.py` still has a dead `'Long-term Shutdown'` CASE branch (0 rows). The `/api/stats` JSON key is still literally `permanently_shutdown` (value is correct) — cosmetic, left untouched to avoid frontend breakage.

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
- **Status "Permanent Shutdown" -> "Shutdown" (May 28, Noah + REG editorial)**: REG argues some German/Belgian units should be refurbished and restarted, so "Permanent" contradicts the firm's own position. "Suspended" stays the shorter-term-offline category. DB value + all code references renamed together.
- **Shidaowan naming (May 28, Q1)**: CAP1400 units -> "Shidaowan Guohe One" (国和一号, the official CAP1400 brand); HPR1000 Phase-I units -> "Shidaowan 1/2" (PRIS). Rejected Noah's "SN-1/SN-2" (zero source support). The site has 3 programs: Shidao Bay (HTR-PM), Shidaowan Guohe One (CAP1400), Shidaowan (HPR1000).
- **Cancelled-construction class (May 28, D2)**: units that began construction but never operated (Lungmen 1/2, Baltic-1) live in `planned_reactors` with `expected_online='Cancelled'` (text in the integer-year column; app handles it because each such project is homogeneously 'Cancelled' — do NOT mix int years and 'Cancelled' in one project or `min()/sorted()` in app.py will TypeError).
