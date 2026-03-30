# Nuclear Database — Plan

## Current State

Post-core development. Capacity alignment audit nearly complete.

- **Last worked**: Mar 26-29 — Capacity alignment audit: 223/229 reactors fixed across all countries. Model page design_series promotion fix. Whitespace validation added. All deployed.
- **Known issue**: Ghost process can linger on port 5001 — use 5002 or `taskkill`
- **Next**: US Phase 2 (6 reactors needing NRC verification). Then 2025 PRIS data backfill when available.

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

### 7. Net Capacity Alignment Audit (Mar 26, 2026) — IN PROGRESS
Convention: `net_capacity_mw` = PRIS Reference Unit Power (current/final operating capacity).
Original design values preserved in `capacity_changes` initial records.

**Completed (23 reactors):**
- [x] Belgium (7): Doel 1-4, Tihange 1-3. SG replacement + uprate history documented for Doel 1-3, Tihange 1-2.
- [x] Chinese AP1000 (4): Haiyang 1/2, Sanmen 1/2. Data correction — 1000 MWe was placeholder from model name.
- [x] German PWR (12): All shutdown. Multi-step thermal stretch + MUR (VDI 2048) uprate timelines from PRIS.
- [x] Model detail page: design_series promotion fix (app.py)

**Completed Wave 2 (52 more reactors, Mar 26):**
- [x] UK GCR (35): Magnox degradation (CO2 corrosion) + AGR degradation (graphite cracking). Both net AND ref corrected from PRIS-verified values. Sizewell B PWR also aligned.
- [x] South Korea (24): APR1400 mixed-source fixes. PWR ref aligned to 2024 PRIS RUP. Wolsong CANDU ref aligned to derated values.

**Remaining (156 reactors with >5 MWe gap):**
- [ ] USA (50) — see US Capacity Alignment Plan below
- [ ] Sweden BWR (6) + PWR (3) — known significant uprates
- [ ] Czech Republic PWR (6), France PWR/GCR (10), Russia PWR/FBR (6), China (8), Germany BWR (8)
- [ ] Canada (7), Finland (5), India (5), Hungary (4), Japan (4), Switzerland (4)
- [ ] ~15 other countries with 1-3 reactor discrepancies each

### US Capacity Alignment Plan

The US fleet (50 reactors) is the most complex group due to three overlapping data issues:

**Root cause**: Three data layers accumulated:
1. Original scrape: `net_capacity_mw` = PRIS Design Net Capacity
2. WNA audit (Mar 16): Updated net for operational reactors from WNA (>20 MWe threshold)
3. `reference_power_mw` = PRIS RUP snapshot (one-time, now stale for many reactors)

**Three sub-patterns identified by research:**

**Pattern A — Shutdown, ref > net (15 reactors)**: Standard design-vs-uprated gap. Net has original design capacity, ref has final operating RUP. Some ref values also stale (Indian Point 2/3 revised downward by PRIS post-shutdown).
- **Action**: Set net = ref, except for IP2/3 where PRIS has revised down (IP2: 1020→998, IP3: 1040→1030). Spot-check a few others.
- **Confidence**: High for most, medium for Indian Point.

**Pattern B — Operational, ref > net (15 reactors)**: PRIS revised RUP downward since our scrape. WNA audit correctly updated net to current value. Ref is now stale (higher than actual).
- **Action**: Set ref = net (net from WNA is more current). Verified for Ginna, Monticello, Grand Gulf.
- **Confidence**: High — agent verified the pattern with representative examples.

**Pattern C — Operational, net > ref (20 reactors)**: WNA audit set net higher than old PRIS RUP snapshot. Two sub-groups:
- **C1 — Large gaps (5 reactors)**: Browns Ferry 2/3, Cook 2, Harris, Turkey Point 3. Known EPU/MUR uprates. PRIS itself is stale for Browns Ferry (shows 1200, actual post-EPU ~1256). Our capacity_changes records may be most accurate.
  - **Action**: Use capacity_changes final value where available. For Browns Ferry, use NRC-confirmed ~1256. Cross-check Harris and Turkey Point against NRC uprate database.
  - **Confidence**: Medium — need NRC verification for exact values.
- **C2 — Small gaps (15 reactors)**: Normal drift where WNA is slightly more current than old PRIS snapshot.
  - **Action**: Set ref = net (WNA values are more current). Exception: Cooper (net=778 is actually old design net, not WNA; WNA says 769).
  - **Confidence**: High for most. Spot-check Cooper and any others where net looks like a round design number.

**Proposed execution (2 phases):**
1. **Phase 1 — Mechanical fixes**: Pattern B (set ref = net, 15 reactors) + Pattern C2 (set ref = net, ~13 reactors) + Pattern A majority (set net = ref, ~12 reactors). ~40 reactors, high confidence.
2. **Phase 2 — Research-dependent**: Indian Point 2/3 (get current PRIS values), Browns Ferry 1/2/3 (NRC EPU values), Harris/Turkey Point 3 (NRC verification), Cooper (WNA value), Watts Bar 1 (recent uprate). ~10 reactors needing targeted verification.
