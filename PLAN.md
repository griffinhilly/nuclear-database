# Nuclear Database — Plan

## Current State

May 28 — **Noah review applied & validated locally; NOT yet committed/deployed** (awaiting Griffin approval for git push + fly deploy).

- **Last worked**: May 28 — ~45 external corrections from Noah. Verified by 6 parallel research agents (PRIS/WNA), applied via migrations 002-008, a code-side "Permanent Shutdown"->"Shutdown" rename (app.py/database.py/12 templates), and 3 new `validate_db.py` checks. Ledger: `noah_review.md`. Validator: all hard-FAIL checks pass; 54 remaining are the pre-existing WARN backlog (capacity-rounding + net/coord nulls), identical to the pre-Noah backup. App smoke-tested on :5002 (stats, status page, renamed plants, planned-with-Cancelled all OK).
- **Uncommitted**: 8 new migration files, app.py + database.py + 12 templates, validate_db.py, scripts/rename_status_shutdown.py, noah_review.md, COMP updates. DB backed up to `nuclear_reactors.db.bak-noah-20260528`.
- **Migration 009** (spec-blind review fixes): Khmelnytskyi notes de-contradicted; Darlington SMR construction_start -> first-concrete (2026-05); VVER-1200/510 year fixed; orphan artifact models W?/V-120 dropped; entity_descriptions synced (renamed Sellafield->Calder Hall, Shidaowan->Shidaowan Guohe One, MONTS-D'ARREE->EL-4, W?->WH 2-loop, CANDU casing; deleted artifacts).
- **Open follow-ups**:
  1. **Ask Noah** for sources on undocumented suffixes V-491S / V-491T / V-412T (applied base codes only). Also tell him the 3 overrides (Ling'ao=M310, Lianjiang=CAP1000, Kudankulam=V-412).
  2. **Manual descriptions needed** (per project's manual-description standard): plants Windscale AGR, Shidaowan (HPR1000 units), Darlington SMR; and new models (V-510K, V-527/528/529, V-213+, M310+, CPR-1000+, BWRX-300, VBWR, WH 2-loop, VVER-210/365). App shows blank gracefully meanwhile.
  3. Spotted adjacent (out of Noah scope): Novovoronezh-1 U5 series is "VVER-440/187" but should be "VVER-1000/187" (it's the prototype VVER-1000).
  4. Reviewer-flagged (deferred, working): `expected_online='Cancelled'` is text in an INTEGER column (Griffin's D2 choice) — safe only because each cancelled project is homogeneous; do NOT mix int years + 'Cancelled' in one project. A few orphan model rows remain (CNP-1000, VVER-1200, VVER-TOI, V-392B, MONTS-D'ARREE) — cosmetic, mostly real designs.
  5. Optional cosmetic: rename `/api/stats` JSON key `permanently_shutdown` -> `shutdown` (+ frontend); remove dead `'Long-term Shutdown'` CASE branch in app.py.
- **Known issue**: Ghost process can linger on port 5001 — use 5002 or `taskkill`
- **Next (pre-existing backlog)**: Follow-up cooling audit (Fermi 2, Tarapur 3/4, US mechanical-vs-natural-draft). 2025 PRIS data backfill when available.

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
- [ ] Data freshness: re-run backfill scripts when 2025 PRIS data becomes available
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

### 8. Cooling System Audit Follow-up
- [ ] Fermi 2 (USA): likely wrong — has 475 ft natural-draft tower but marked "Once-through (lake)"
- [ ] Tarapur 3/4 (India): NPCIL literature suggests PHWR units use induced-draft cooling towers despite coastal location. Satellite was inconclusive — induced-draft towers are low-profile. Needs primary source verification.
- [ ] US mechanical vs natural draft: Byron, Braidwood, Comanche Peak may be mechanical draft. Audit full US cooling_tower set.
- [ ] China section fragile: fallthrough returns "seawater" for any unrecognized plant. Will break when inland sites enter construction.
- [ ] Add cooling data checks to `validate_db.py` (null check, enum check, flag all-same-per-plant as review candidate)
