# Nuclear Database — Plan

## Current State

Oct 15, 2026 — refreshed (Oct 13 text below still current unless superseded). Jul 22 design-spec pass and Jul 21-23 embed-map redesign shipped (bullets below). Jul 6 sweep detail + May 28 deferred items: `PLAN_current_state_archive_2026-07.md`.

- **Oct 14-15 release — SHIPPED (commit 328d13c, deployed + pushed Oct 15)**: migrations 034-039. 034-038 = Phase 2 fleet audit waves 1-5 (supply chain, licence, containment, cooling; three-tier verified; whitelists `audit/whitelist_03x.psv` appended to `final_verdicts.psv`). 039 = projection inputs: new columns `planned_retirement_basis/source`, `commissioning_milestone/_date/_source`; 24 sourced closures, 12 refuted dates cleared, 76 milestones; Guohe One 2 → Operational (032 had set CONNECTED without the status flip). Live: 424 operating / 410.6 GW gross. Validator 19-issue baseline; site_consistency 0 FAIL / 4 WARN (all explained).
- **Homepage projection = range to 2030 (Griffin, Oct 15)**: top = every UC unit on schedule, only SAFETY_CONDITION closures (UK AGRs close 2030 in both lines — Griffin: fine for now, to discuss with Madi); bottom = every LAW_POLICY/OWNER_DECISION/SAFETY closure, only units past hot tests (HOT_TESTS/FUEL_LOAD/CRITICALITY/GRID) added. Licence-end dates are not closures. View A (full history; band is a sliver by design). 2030: top 471 / 463.9 GW, bottom 417 / 406.1 GW. Method: app.py `fleet_projection` comments. Keep current: re-run research for closures/milestones (`audit/projection/*.psv`, builder `scripts/build_039_projection_inputs.py`) and the monthly freshness check.
- **Change history (Oct 15)**: `scripts/db_change_history.py` + `scripts/change_history_report.py` → `review/2026-10-15-change-history.html` (every DB value change since Jan, by audit; 10 failure modes). Griffin read it: "not as bad as I feared".
- **Later (Griffin)**: median forecast line (non-China dates shifted by vendor slip record, `audit/projection/slip_track_record_*`); what to do with Noah/Dirk data; other data sources (survey `audit/data_sources/`); Explore page → Madi (`review/2026-10-15-explore-for-madi.html`).
- **Open data issues from Oct 15**: Saeul 3 (Shin-Kori 5) → Operational once a sourced grid date exists · Kursk II-3 and Darlington SMR construction-start conflicts · WNA lists 4 Chinese UC units we lack (Xin'an HTR-PM600 1/2, Bailong 2, Zhaoyuan 2) · Koeberg licensed_until blank · Linglong 1 expected 2026 stale · Pickering 5-8 refurbishment outage (held) · Palisades 1 / Rajasthan 1 Suspended with a shutdown date.
- **Oct 10-13 (Madi session)**: Noah asked how data has been entered, for himself and Dirk; both will add data. Write-up `docs/data-entry-process.md` + reply page `review/2026-10-10-data-entry-reply.html` — **local only** (repo is PUBLIC; `docs/`, `review/`, `*.db.bak*` are in `.git/info/exclude`). Open decision for Madi/Griffin: Route A (they send a correction sheet, we apply) vs Route B (they edit the DB). `_migrations` was missing 016-021 (applied but unlogged → a bare `migrations/run.py` would re-run them); rows added Oct 13 after backup `nuclear_reactors.db.bak-premiglog-20261013`, now 21/21.
- **Dirk = outside industry expert, same standing as Noah** (his attestations count as gospel). His site de.nucleopedia.org is behind a Cloudflare bot challenge — decided NOT to scrape; **Madi is asking Dirk for an export** (MediaWiki XML / DB / allow-list). When it arrives: parse infoboxes with a script (not an LLM swarm), per-value page URL as source, deterministic diff vs DB.
- **Viz direction (Oct 13)**: emulate usenergydata.org (IFP; hand-built D3 v7, OWID-style) — chart card (title+units subtitle, Map/Line/Bar/Table tabs, source line, download, standalone/embeddable URL), choropleth + year slider, question-led topic pages. Prototype started: world choropleth of nuclear generation by country with year slider (local only until Madi reviews). Also open: template-by-template ideation (what fleet facts we don't communicate yet) and a fresh factual audit with current models.

- **Data state**: validator at 54-warning baseline with 14 checks (9–14 new: cooling enum/NULLs/uniformity, duplicate pris_ids, post-shutdown generation, CF>105% public-endpoint mirror). Generation through 2025 (93.3% operational coverage). Zero missing descriptions. pris_id ground truth: `pris_id_map_2026-07.json`.
- **Backlog** (unranked): label the current-year share point provisional on the dashboard chart (2025 = 9.3% rides on 88.6% coverage estimate) · capacity-history gaps (Wolsong 3/4 net values, Hunterston B 1990s derate, Hinkley Point B2 1994, Bruce 2 MCR uprate) · general NULL-pris_id sweep from the id map · Shidaowan Guohe One generation needs a non-PRIS source · 1970–84 world-electricity stub (UN yearbook transcription) if the share chart should extend back · China cooling fallthrough fragility in populate_reactor_details.py · 3 reactors have no reactor_details row at all (741 reactors vs 738 verified — identify + backfill attested values only).
- **Embed map (Jul 16–20)**: `/embed/map` — iframe-able teaser map for the REG website (tint #FFBF00 per designers, UC dots #996a00 "yellow map" per Madi/designers, CTA removed, fit-to-fleet framing). Deployed Jul 20.
- **Constants audit (Jul 20)**: hardcoded-constants backlog item DONE — ledger `constants_audit_2026-07.md`. design_series_specs: systematic turbine-speed error class fixed fleet-wide (migrations 016+017, 80 row-changes: Soviet/UK full-speed 3000, Japan 60Hz-zone 1800, HTGR 3600, mixed-grid→NULL) + 9 wrong thermal/fuel/pressure values fixed + Magnox/UNGG unrepresentable values nulled. planned_reactors: Duwayhin fabrication stripped, 3 more corrected. reactor_details constructor/AE/turbine/RPV fields HIDDEN from API+UI (heuristic-assigned, ~15-20% sample error rate) re-verified per-reactor Jul 20 (24 batches + 2 gap-fills, 2940 verdicts): only CONFIRMED HIGH/MED values shown (migration 018, 2043 NULLed, archive table kept); 593 sourced corrections + 22 weak confirmations await Noah/Dirk in verification_2026-07/noah_dirk_consult_2026-07.md.
- **Design-spec completion pass — SHIPPED Jul 22 (migrations 019-021)**: 1,987 retrieval-sourced verdicts (`verification_2026-07/spec_final_verdicts.psv`, review `migration_019_review.md`): 65 corrections + 12 more from an Opus re-attestation pass, 804 UNVERIFIABLE values NULLed, entity-collision gate added to `merge_specs.py` (ATR=Fugen, SNUPPS=Sizewell B), validator check 16 (text strays in numeric spec columns). **Residue**: 367 BLOCKED rows (`spec_rerun_manifest.psv`) + 281 pass-3 rows (`pass3_residue.psv`) still unverified, values untouched — re-run with search-capable agents.
- **Embed map redesign (Jul 21-23)**: Figma duotone vector choropleth, country hover tooltips with live counts, Forma DJR Micro brand font, cooperative zoom (commits e8dc357, 4815367).
- **Drift guard (Jul 21)**: validate_db.py check 15 — any non-NULL reactor_details vendor value not whitelisted in `final_verdicts.psv` fails validation. Tested (plant-and-revert). Noah/Dirk attestations must be appended to final_verdicts.psv (visible=yes) in the same change that writes them to the DB.
- **Data leads found Oct 13 (not fixed)**: 2021-24 national generation totals look low vs published national figures (France ~25% low, KR/RU ~10-15%, US ~5%; 2025 looks right) — re-pull from PRIS per reactor before trusting the share chart · 48 reactors / 637 generation rows dated before own grid connection (pris_id-class contamination?) · `operator` NULL for all 738 · `lifetime_generation_gwh` holds TWh · 40/76 UC units lack net capacity · stale planned_retirement/licensed_until. Full list: `review/2026-10-13-site-ideas.html` part 5 (local). SQL trap: DATE-affinity columns — compare to `'2010-01-01'`, never `'2010'`.
- **Nucleopedia spot-check (Oct 13, via search-engine snippets — site itself is behind Cloudflare)**: 7 capacity values matched exactly. Vendor fields: corroborates July corrections for Zaporizhzhia turbines (Turboatom) and Temelín RPVs (Škoda); supplies Biblis RPV maker (GHH Oberhausen; July said "not RDM, unknown"); supports original Izhora for Novovoronezh II RPVs. **July audit error found: Taishan RPVs** — `final_verdicts.psv` marks MHI WRONG→"Framatome" (HIGH), but WNN + Power Technology say Taishan 1 = MHI, Taishan 2 = Dongfang Electric. Fields are hidden (NULL) so nothing wrong is live, but `noah_dirk_consult_2026-07.md` lines 92/94 propose the wrong value → July "WRONG" verdicts include false positives (NSSS-vendor-vs-fabricator confusion); re-check before sending. Nucleopedia has content we lack: INES-rated incident histories, cost history, ownership shares, turbine/generator model designations, cooling-tower specs, licence-extension events, cancelled-project pages, capacity-change history (e.g. Mühleberg 372→390).
- **Nucleopedia export comparison (Oct 13, Griffin exported 10 pages via Special:Export from his browser → `review/nucleopedia/`)**: 38 per-reactor entries, 297 values agree, 50 differ, 169 they have and we lack. **Live errors flagged**: Paks 1-5 cooling = natural draft in DB but Paks is once-through Danube cooling; Temelín 1/2 net 1086 > gross 1080 (net looks like gross; WNA 1027 net). Taishan 2 turbine Alstom vs Dongfang. Their Biblis-B row copies Biblis-A capacities (tell Dirk). Page: `review/2026-10-13-nucleopedia-spotcheck.html`. Their per-reactor table (Vorlage:Reaktorbox/Zelle) has 57 fields incl. contract year, sub-suppliers, cycle length, generator voltage, planned/cancelled units.
- **Reader corrections form (Oct 13 prototype, uncommitted)**: "Suggest a correction" button in `_reg_footer.html` (every page) → `POST /api/corrections` → separate `submissions.db` (gitignored; never the reactor DB) → `scripts/review_submissions.py list|accept|decline` → public `/contributions` ("Improved by our readers", accepted only, name only if opted in). Honeypot + per-IP rate limit. **Blocker for production**: fly.toml runs 3 machines with per-machine volumes, so a file store would split — needs a shared store decision (Google Sheet in REG Drive vs single machine vs email).
- **Deploy (Oct 13)**: `~/.fly/bin/fly.exe` is a 0-byte symlink Windows refuses to launch — call `~/.fly/bin/flyctl.exe` (v0.4.19, works) directly. Auth token expired: Griffin must run `flyctl.exe auth login` once (browser).
- **PRIS moved (Oct 13)**: pris.iaea.org pages 302 → `pris-stats.iaea.org` (Angular app); all old PRIS scrapers are broken. New JSON API: `/reactor/reactors-by-code/<CC>` (whole country incl. shutdown: status, dates, thermal/gross/net/design-net, model, owner, operator, turbine+reactor supplier), `/reactor/reactor-by-id/<id>`, `/country/countries/` (38 codes). Annual-history endpoint not yet found. Backbone of the audit: `docs/audit-plan-2026-10.md` (local).
- **Nucleopedia runs Cargo** (`Spezial:CargoTables` / `Spezial:CargoQuery`) — a whole-table structured export may exist; bulk export needs Dirk's OK.
- **Audit Phase 1 done (Oct 13, deterministic)**: `scripts/pris_api_pull.py` (739 PRIS reactors cached in `audit/pris_api/`), `scripts/pris_api_diff.py` (733/738 matched; alias + transliteration table inside), `scripts/invariant_scan.py`. Results + proposed fix batches A–G: `review/2026-10-13-audit-phase1.html` (local). Headlines: placeholder round numbers (China 1000 MW net, VVER 3000/3200 MWt, Barakah 3200 MWt vs 3983), gross-stored-as-net on 15 reactors, Russian date drift, 6 status conflicts, 6 missing UC units (Jinqimen 2, Xuwei 1, Zhaoyuan 1 absent; Taipingling 4, Bushehr 3, Shin-Hanul 4 still "planned"), operator blank on all 738. Awaiting Griffin's go on batches A–E.
- **Audit batches A-E + statuses (Oct 13) — APPLIED (migrations 023-028)**: migrations 023 (PRIS fills, 2,314 blanks incl. operator/first criticality/pris_id), 024 (PRIS capacities + dates, guarded: net/gross, gross/thermal, past-CF<=105%, no US capacity, no capacity_changes reactors), 025 (5 missing UC units; deletes 2 planned rows), 026 (475 PRIS turbine suppliers, whitelisted), 027 (25 batch-C research verdicts with re-found quotes). Builder: `scripts/audit_build_batches.py`; quote checker: `scripts/quote_check.py`. Whitelist rows for 025/026/027 already appended to final_verdicts.psv (uncommitted). Rehearsal: validator 17 issues, 0 FAIL. Pages: `review/2026-10-13-audit-batches-ABDE.html`, `review/2026-10-13-audit-batch-c.html`. Status decisions applied as recommended (028): Sanao 1, Tarapur 1/2 -> Operational; Tsuruga 2 -> Suspended; KK-6, Palisades, Bushehr 3 unchanged. NOT YET DEPLOYED (needs `flyctl.exe auth login`). 27 batch-C items held (mostly Soviet-era Russian dates → Nucleopedia ask). Wolsong 3/4 derate needs capacity_changes rows. Taipingling 1/2 province wrong (Guangxi → Guangdong).
- **Migration 022 (Oct 13) APPLIED + committed ee17b17**: Paks 1-5 cooling → once-through river; Temelín 1/2 → gross 1086 / net 1027, 1029 (PRIS API); Taishan RPVs → MHI / Dongfang (WNN), whitelisted in final_verdicts.psv. Backup `nuclear_reactors.db.bak-pre022-20261013` taken. Taishan lines in the Noah/Dirk consult list withdrawn.
- **Next up** (unranked): viz prototype (`/charts/nuclear-by-country`, uncommitted) → Madi review · ideas catalogue A–K in `review/2026-10-13-site-ideas.html` · Route A/B decision + send the vendor consult package (`verification_2026-07/noah_dirk_consult_2026-07.md`, 593 corrections; not yet sent as of Jul 21 — confirm) · Nucleopedia export when Dirk sends it · factual re-audit with current models (incl. the 648 spec residue rows) · backlog / external triggers (2026 PRIS data ~mid-2027).

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
