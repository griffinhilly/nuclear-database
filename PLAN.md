# Nuclear Database — Plan

## Current State

Jul 6 (session 2) — **BACKLOG SWEEP COMPLETE: migrations 011–015 applied + validated, NOT yet pushed/deployed.** All four open backlog items done in one session (orchestrator-agent pattern + spec-blind review):
- **011**: Novovoronezh-5 = prototype VVER-1000 (V-187), series renamed VVER-440/187→VVER-1000/187, predecessor chain rewired, specs + model description corrected (committed `96a421d`).
- **012 (cooling audit)**: 40 per-unit fixes across the US fleet + Scope-C fills; Fermi 2/Perry/Davis-Besse now show their natural-draft towers; Braidwood/Clinton/South Texas/Wolf Creek/Comanche Peak → cooling pond; Catawba → mechanical draft; Tarapur tower hypothesis REFUTED (stays seawater). Ledger: `cooling_audit_2026-07.md`. Validator checks 9–11 added.
- **013 (2025 PRIS backfill)**: 2025 coverage 93.3% of operational fleet; 2024 gaps filled. **Spec-blind review caught a blocker**: 13 reactors carried duplicate (wrong) pris_ids → pair-partner's output written onto them (238% CFs on shutdown reactors, ~100 TWh double-counted).
- **015 (pris_id repair)**: full PRIS id-space scan (1–1150) → 24 pris_id fixes (13 dup losers, 5 wrong-unique, 6 NULL fills), contaminated generation repaired from true PRIS pages (incl. pre-existing Shin-Kori 3/4 contamination back to 2006). Ledger: `pris_id_repair_2026-07.md`; ground truth: `pris_id_map_2026-07.json`. Validator checks 12–14 added (dup ids, post-shutdown generation, CF>105% vs historical gross = public endpoint mirror). **Post-repair: validator = 54 baseline exactly, public CF-anomaly endpoint = 0, totals 2025 = 2622.8 TWh / 2024 = 2426.2 TWh.**
- **014 (descriptions)**: all 16 missing model + 4 missing plant descriptions written (individually researched); V-187 spec control-elements filled (109). Zero missing descriptions remain.
- **World-electricity rebase DONE (Griffin-approved Option 1, commit 5d4bb64)**: the old hardcoded denominator claimed EI sourcing but ran 7–15% low (latent-space artifact, same class as the pris_ids). Replaced wholesale with the real EI series via OWID, 1985–2025 (EI starts 1985; unverifiable pre-1985 stub dropped rather than spliced). Share chart now reads 8.8% for 2024 (was 10.3%), 1996 peak 16.7% (net-vs-gross convention explains gap to published ~17.5%). Sources page citation updated.
- **NEXT**: push (6 commits ahead) + `fly deploy` (fly CLI needs `fly auth login`); new backlog items in `pris_id_repair_2026-07.md` §backlog (capacity-history gaps: Wolsong 3/4, Hunterston B 1990s, Bruce 2 MCR; general NULL-pris_id sweep; Shidaowan Guohe One non-PRIS generation source).

Jul 6 (session 1) — **Migration 010 CONFIRMED SHIPPED** (session-start audit): committed `b1ae92f` Jun 4 11:29, merged to `main`, pushed to GitHub, and deployed to Fly.io — live-verified via API (Tianwan 5 = ACPR-1000, a change that exists only in 010). The "NOT yet committed / deployed" note below was stale: the Jun 4 COMP-update commit (1e7ea2d, 11:10) froze that language before the data commit landed at 11:29.

Jun 4 — **Noah override reversals applied (migration 010).** All 3 May-28 overrides reversed after Noah supplied sources and held his ground; every Noah correction is now accepted. Validator clean.

May 28-29 — **Noah review SHIPPED.** Committed (058a304), pushed to GitHub, deployed to Fly.io (3 machines, health-checked). Live site verified: 738 reactors / 223 Shutdown / 76 UC / 417 operational. **Confirmed merged to `main`** Jun 4 (the earlier "not merged" note was stale; main history contains 058a304 + docs).

- **Last worked**: May 28 — ~45 external corrections from Noah. Verified by 6 parallel research agents (PRIS/WNA), applied via migrations 002-008, a code-side "Permanent Shutdown"->"Shutdown" rename (app.py/database.py/12 templates), and 3 new `validate_db.py` checks. Ledger: `noah_review.md`. Validator: all hard-FAIL checks pass; 54 remaining are the pre-existing WARN backlog (capacity-rounding + net/coord nulls), identical to the pre-Noah backup. App smoke-tested on :5002 (stats, status page, renamed plants, planned-with-Cancelled all OK).
- **Committed in 058a304** (May 29): 8 new migration files, app.py + database.py + 12 templates, validate_db.py, scripts/rename_status_shutdown.py, noah_review.md, COMP updates. DB backed up to `nuclear_reactors.db.bak-noah-20260528`.
- **Migration 009** (spec-blind review fixes): Khmelnytskyi notes de-contradicted; Darlington SMR construction_start -> first-concrete (2026-05); VVER-1200/510 year fixed; orphan artifact models W?/V-120 dropped; entity_descriptions synced (renamed Sellafield->Calder Hall, Shidaowan->Shidaowan Guohe One, MONTS-D'ARREE->EL-4, W?->WH 2-loop, CANDU casing; deleted artifacts).
- **Never-operated audit COMPLETE (D2)**: queried all `status='Shutdown'` reactors with no grid_connection AND no commercial_operation → only **3** in the DB (Lungmen 1/2, Baltic-1), all moved to planned/Cancelled. The other famous never-built plants (Zwentendorf, Bataan, Kalkar/SNR-300, WNP, Bellefonte) are NOT in this DB's reactor set, so nothing further to move. Audit done, not deferred.
- **Open follow-ups (intended TODO)**:
  1. ~~Ask Noah for suffix sources / tell him the 3 overrides~~ **RESOLVED Jun 4** — Noah supplied sources (Gidropress 2021 book; MEE EIA notice), all 3 overrides reversed in migration 010. Suffixes V-491S/T, V-412M/T applied; Tianwan 5/6 CPR-1000→ACPR-1000 bonus fix. Nothing left to ask Noah on these.
  2. ~~Manual descriptions needed~~ **DONE Jul 6** (migration 014 — all 16 models + 4 plants, incl. Cape Nagloynyn which this list had missed).
  3. ~~Novovoronezh-1 U5 series fix~~ **DONE Jul 6** (migration 011).
- **Deliberately deferred (Griffin accepted, not forgotten)**:
  4. `expected_online='Cancelled'` text-in-INTEGER column — Griffin said "fine for now" (May 28). Safe only because each cancelled project is homogeneous; do NOT mix int years + 'Cancelled' in one project (app.py `min()/sorted()` at L1404/1445 would TypeError). Cheap future hardening: guard those calls or `WHERE expected_online != 'Cancelled'`. A few orphan model rows remain (CNP-1000, VVER-1200, VVER-TOI, V-392B, MONTS-D'ARREE) — cosmetic, mostly real designs.
  5. Optional cosmetic: rename `/api/stats` JSON key `permanently_shutdown` -> `shutdown` (+ frontend); remove dead `'Long-term Shutdown'` CASE branch in app.py.
- **Known issue**: Ghost process can linger on port 5001 — use 5002 or `taskkill`
- ~~Follow-up cooling audit~~ **DONE Jul 6** (migration 012). ~~2025 PRIS backfill~~ **DONE Jul 6** (migrations 013+015).

## Completed

### Core App
- Flask app with SQLite backend (739 reactors, 39 countries)
- Dashboard with stat cards, charts, Leaflet map, data tables
- 9 detail pages: reactor, plant, country, technology, status, model, supplier, owner, containment
- Sources & Methodology page (`/sources`) with coded references
- All links flow through plant pages (map markers -> plant -> reactor)
- Generation data backfill (94% coverage for 2024)
- Visual design refresh (light theme, modern cards/typography)

### Data Audit (Mar 2026)
- Country-by-country IAEA PRIS alignment — all 31 nuclear countries verified
- Added "Suspended" status (22 reactors, mostly post-Fukushima Japan)
- Added 41 missing under-construction reactors (28 -> 66)
- Cleaned planned_reactors table (removed UC duplicates, 122 entries)
- Added coordinates for all 733 reactors (zero missing)
- Fixed Germany, Belgium, Japan, Russia, Canada, USA, France, Pakistan, India, China status errors

### Coordinate & Name Verification (Mar 12, 2026)
- 19 plant name corrections (46 reactors): umlauts, transliterations, misspellings, official names, diacritics
- Chinese data overhaul: Shidaowan rebuilt, 37 reactors fixed, 4 new reactors added (733 total)
- Multi-phase coordinate verification: 137 auto-fixes + 28 manual + 8 user-verified + 10 unmatched + 74 Wikidata-adopted + 100 Wikipedia GeoData scraped
- Wikipedia GeoData established as gold standard for all coordinates
- EL-4 renamed to Brennilis

### Map & Charts
- Map status filter toggles (All/Operational/UC/Suspended/Shutdown)
- Map shows plant names with all reactors per plant in popup
- Marker color reflects best status at plant
- Generation chart: annual nuclear share of global electricity (1970-2024)
- Source annotations on all charts

### Deployment
- Fly.io deployment (3 VMs, ord region, persistent volumes)
- Auto DB sync on deploy via start.sh
- GitHub remote at griffinhilly/nuclear-database

### Design Lineages (Mar 11-12, 2026)
- All 739 reactors have `design_series` (100% coverage)
- `design_lineages` table: 24 families with slug, description, origin country, designer, technology type
- `design_series_info` table: 123 series with lineage FK, generation order/label, capacity, year, predecessor, description
- Lineage listing page (`/lineages`) — overview of all 24 families with filter tabs
- Lineage detail page (`/lineage/<slug>`) — D3.js family tree, Leaflet map, Chart.js country breakdown
- Lineage tree embedded in model detail pages with highlighted current series
- Model pages resolve both exact model names and design_series names (for lineage tree navigation)

### Entity Descriptions (Mar 14-16, 2026)
- 708 descriptions across 7 entity types in `entity_descriptions` table
- Enriched 12 technology and 24 lineage descriptions in their native tables
- Entity types: plant (315), model (154), owner (154), country (39), supplier (33), containment (9), status (4)
- **All 315 plant descriptions are manual** (0 templates) — completed Mar 16
- **All 154 owner descriptions are manual** (0 templates) — completed Mar 16
- Models, countries, suppliers, containment, status: 100% manual

### Containment Consolidation (Mar 14, 2026)
- Replaced 9 per-type containment pages with single `/containment` overview page
- Type cards, filterable map (color-coded by type), filterable reactor table
- Old `/containment/<type>` URLs redirect to `/containment?type=<type>`
- De-emphasized containment in 29 model descriptions (now a data field, not a bio topic)

### Data Quality Cleanup (Mar 14, 2026)
- Fixed 169+ generation entries with impossible capacity factors from broken PRIS scraper
- Updated 11 reference_power_mw values from PRIS (uprated reactors + UK AGR corrections)
- Deleted 124 bad generation entries (post-shutdown, pre-operation, station-level duplicates, impossible data)
- Replaced 104 generation values with correct PRIS unit-level data
- Fixed Rajasthan-7 status (UC → Operational)
- 19 remaining CF > 110% entries are known limitations (historical ref power changes) — Uprates task will fix

### Cooling System Audit (Apr 3-4, 2026)
- Root cause: `populate_reactor_details.py` assigned cooling type per plant name, not per unit
- Fixed 9 plants where newer/larger units have cooling towers but older units don't:
  - Doel 3/4 (Belgium): once-through → natural draft tower
  - Nine Mile Point 2 (USA): once-through lake → natural draft tower
  - Hope Creek (USA): once-through seawater → natural draft tower
  - Leningrad 2 (Russia): once-through seawater → natural draft tower
  - Kursk 2 (Russia): cooling pond → natural draft tower
  - Novovoronezh 2 (Russia): cooling pond → natural draft tower
  - St. Laurent B (France): once-through river → natural draft tower
  - Dampierre (France): once-through river → natural draft tower
  - Chinon B (France): once-through river → mechanical draft tower (UNESCO landscape)
- Verified correct: Blayais, Tricastin, Bugey 2/3 vs 4/5, Tihange, Tarapur, Kakrapar, all coastal plants

## Remaining

### 1. Coordinate & Planned Reactor Cleanup
- [x] Multi-site consolidation: **keep as separate plants** (Madi decision, Mar 16). No changes needed — coordinates already distinct per generation.
- ~15 plants unmatched by Wikipedia scraper — most already verified manually

### 2. Data Quality (Mar 15, 2026)
- [x] Fixed: 4 operational reactors got PRIS IDs (Taipingling 1084, Shidaowan 957, KK-6 383, Madras 304)
- [x] Fixed: Taishan 2 commercial_operation = 2019-09-07, Shidaowan 1 = 2023-12-06
- [x] Noted: Flamanville 3 + Taipingling 1 still in commissioning (commercial_operation TBD)
- [x] Noted: 15 Ukrainian reactors no data after 2021 (war-related, not fixable)
- [x] Data freshness: 2025 PRIS backfill DONE Jul 6 (migrations 013+015; 93.3% operational-fleet coverage)
- [x] WNA audit for non-Chinese reactor specs (capacity, dates, status) — DONE Mar 16

### 6. WNA Audit (Mar 16, 2026) — MOSTLY COMPLETE
- [x] Scraped 640 reactors from 38 countries, matched 640/640
- [x] Added 6 missing UC reactors (Kaiga 5/6, Cape Nagloynyn 1/2, Leningrad 2-4, Shin-Hanul 3)
- [x] Updated 156 operational/UC net capacities from WNA (>20 MWe threshold)
- [x] Filled 13 missing dates (grid_connection, permanent_shutdown)
- [x] Fixed Belgium life extensions (Doel 1/2, Tihange 1)
- [x] Fixed Wylfa 2 + Kuosheng 2 shutdown dates
- [x] Status fixes: Kursk 1-2 (PS), Kursk 2-1 (Operational), Khmelnytskyi 3/4 (Suspended)
- [ ] ~11 shutdown date diffs >30 days need PRIS spot-check (Greifswald 1/4, Onagawa 1, Hunterston B 1/2, Shoreham, HDR Großwelzheim, Hamaoka 4 grid, Hinkley Point B 1, CAREM25 construction start)
- [ ] 121 shutdown reactor capacity diffs left as-is (PRIS authoritative for shutdown reactors)
- Note: Korean "Saeul" renaming (Shin-Kori 3-6) not applied — keeping PRIS naming for consistency

### 3. Template Description Improvements (Mar 15, 2026) — COMPLETE
- [x] 315/315 plant descriptions are now manual (0 templates remaining)
- [x] 154/154 owner descriptions are now manual (0 templates remaining)
- Written in batches: 91 directly + 121 from agents + 25 name-fix pass = all 213 former templates replaced

### 4. Ownership Audit (Mar 15, 2026) — COMPLETE
- [x] Researched all US transfers since 2020 via NRC records
- [x] Palisades: Holtec → Palisades Energy, LLC (restart entity)
- [x] Susquehanna: Talen Energy → Susquehanna Nuclear, LLC
- [x] Confirmed correct: Vistra (Beaver Valley, Davis-Besse, Perry), Holtec (Indian Point), ADP (Crystal River), EnergySolutions (Kewaunee)
- Remaining cosmetic: some parent-vs-subsidiary naming (Duke Energy vs Duke Energy Carolinas, etc.) — low priority

### 5. Uprates / Capacity Additions
- [x] Schema: `capacity_changes` table with reactor_id, effective_date, gross/net capacity, change_type, source, notes
- [x] 105 capacity change records for 46 reactors (original 23 + Belgium 7 + Germany 12 + AP1000 corrections)
- [x] CF calculation in app.py uses historical capacity via COALESCE subquery (3 locations updated)
- [x] CF > 102%: 0 (was 15 at >110%). 41 bad generation entries deleted. Gross capacity corrected for 23 reactors.
- [x] Display: Capacity History card on reactor + plant detail pages, Reference Capacity column in generation table
- [x] Validation report includes CF anomaly check. Sources page updated with effective capacity methodology.
- [x] PRIS-verified: Cook 2 (1231), Turkey Point 3&4 (879 est.), Russian VVERs (1040/1067), Wolsong 2 derate (593)
- [x] Phase 3: Aggregate capacity history charts — `/api/capacity/history` endpoint + charts on dashboard, country, and technology pages
- [ ] 11 entries at CF 100-102% remain — confirmed plausible by industry contact

### 7. Net Capacity Alignment Audit (Mar 26-29, 2026) — COMPLETE
Convention: `net_capacity_mw` = `reference_power_mw` = PRIS Reference Unit Power (current/final operating capacity).
Original design values preserved in `capacity_changes` initial records. 229/229 discrepancies resolved.

- [x] Belgium (7): Doel 1-4, Tihange 1-3. SG replacement + uprate history documented.
- [x] Chinese AP1000 (4): Haiyang 1/2, Sanmen 1/2. Corrected from 1000 MWe placeholder.
- [x] German PWR (12): Multi-step thermal stretch + MUR (VDI 2048) uprate timelines from PRIS.
- [x] UK GCR+PWR (36): Magnox degradation + AGR degradation. Both net AND ref corrected from PRIS-verified values.
- [x] South Korea (24): APR1400 mixed-source fixes. PWR + Wolsong CANDU aligned.
- [x] USA (50): Three-pattern fix (shutdown uprates, WNA-updated operational, NRC-verified). Browns Ferry 1/2/3 set to NRC-confirmed 1256 MWe (PRIS was stale). Indian Point 2/3 set to WNA-confirmed 998/1030 MWe. Harris missing 2018 uprate record added (928→964 MWe). Turkey Point 3 corrected to 802 MWe.
- [x] Remaining 30 countries (96): Mechanical alignment of shutdown + operational reactors.
- [x] Model detail page: design_series promotion fix (app.py)
- [x] Whitespace validation added to `run_validation()`. "CE (2-loop) " orphan model merged.
- [x] 106 capacity_changes records (was 55)

**Key lesson**: PRIS Reference Unit Power can be stale for recently-uprated US reactors (Browns Ferry EPU completed 2019, PRIS still showed pre-EPU values in 2026). NRC and WNA are more current for US operational reactors. For future capacity verification, check NRC first for US reactors, WNA for international.

### 8. Cooling System Audit Follow-up — COMPLETE (Jul 6, migration 012)
- [x] Fermi 2 → natural draft (also caught unsuspected: Perry, Davis-Besse, ANO-2, Duane Arnold, Farley)
- [x] Tarapur 3/4: tower hypothesis REFUTED by 3 primary sources — stays Once-through (seawater)
- [x] Full US fleet audited per-unit (40 changes, ~95 units confirmed); Byron was genuinely natural draft; Braidwood/Clinton/South Texas/Wolf Creek/Comanche Peak → cooling pond; Catawba → mechanical
- [x] validate_db.py checks 9-11 added (NULL advisory, enum hard check, uniform-cooling advisory)
- [ ] China fallthrough fragility in populate_reactor_details.py — noted, unfixed (one-shot script; revisit if inland UC sites appear)
