# Nuclear Database — Session Log

## Jul 16, 2026 — /embed/map teaser for REG website rebuild (deployed)
- **Context**: REG website being rebuilt (Figma design features the database prominently; homepage has a yellow-tinted world-map teaser panel). Designer asked for "the code" to embed the reactor map.
- **Built**: public `/embed/map` route (app.py, after `/sources`) + `templates/embed_map.html`. Inlines coordinates server-side — no API key exposure; `/api/map` stays paid-tier. Leaflet map with dashboard's site grouping/status colors/capacity sizing, REG-yellow teaser tint (`?tint=0` disables), "Explore the Database →" CTA (`target=_top`, relative link so it follows the serving domain).
- **Integration handoff**: designer embeds via iframe pointing at `https://nuclear-database.fly.dev/embed/map`; URL swaps when `database.radiantenergygroup.com` subdomain is set up (pending DNS access — Madi asked).
- **Deployed**: commit `36956a1`, fly deploy verified live via headless-Chrome screenshot.

## Apr 3-4, 2026 — Cooling System Audit (9 plants fixed)
- **Root cause**: `populate_reactor_details.py` assigned cooling type per plant, not per unit
- **Fixed**: Doel 3/4 (natural draft), Nine Mile Point 2 (natural draft), Hope Creek (natural draft), Leningrad 2 (natural draft), Kursk 2 (natural draft), Novovoronezh 2 (natural draft), St. Laurent B (natural draft), Dampierre (natural draft), Chinon B (mechanical draft)
- **Verified correct**: Blayais, Tricastin, Bugey 2/3 vs 4/5, Tihange, Tarapur (satellite), Kakrapar, all French plants audited
- **Deferred**: Fermi 2 (likely wrong), Tarapur 3/4 (needs NPCIL source), US mech-vs-natural-draft audit, China inland fragility, validation checks
- **Triggered by**: Belgium report review spotted Doel 3/4 error

## Mar 14, 2026 — Entity Descriptions (ALL 6 PHASES COMPLETE)
- **688 total descriptions** across 7 entity types in `entity_descriptions` table
- **Phase 1**: Infrastructure — created `entity_descriptions` table, `get_entity_description()` helper, updated all 7 API endpoints and templates
- **Phase 2**: 39 country descriptions (2-3 paragraphs each, nuclear program history)
- **Phase 3**: Enriched 12 technology descriptions (1-2 sentences → 1-2 paragraphs) and 24 lineage descriptions (2-4 sentences → 2-3 paragraphs) in their native tables
- **Phase 4**: 154 model descriptions (1-2 paragraphs each)
- **Phase 5**: 315 plant descriptions (61 manual + 254 template-generated) and 33 supplier descriptions
- **Phase 6**: 134 owner descriptions (35 manual + 99 template-generated)
- Entity descriptions by type: plant (315), model (154), owner (134), country (39), supplier (33), containment (9), status (4)
- Migration scripts: `add_descriptions.py`, `insert_country_descriptions.py`, `enrich_tech_lineage_descriptions.py`, `insert_model_descriptions.py`, `insert_supplier_descriptions.py`, `insert_plant_descriptions.py`, `insert_owner_descriptions.py`

## Mar 12, 2026 — Coordinate & Name Verification + Chinese Data Overhaul
- **Name corrections** (19 changes, 46 reactors): German umlauts (Krümmel, Gösgen, Mühleberg), Ukrainian transliterations (Zaporizhzhia, Rivne, Khmelnytskyi), misspellings (Fukushima-Daiichi, Niederaichbach), official names (Chasnupp→Chashma, Kanupp→Karachi, Xudapu→Xudabao), diacritics (Krško, Cernavodă, Barsebäck, Ågesta)
- **Coordinate verification pipeline**: Multi-phase verification across entire fleet:
  1. 3-source cross-validation (Wikidata SPARQL + OSM Overpass + DB): 137 high-confidence auto-fixes
  2. 34 plants manually verified via Wikipedia: 28 fixed (62 reactors), incl. multi-site Russian complexes
  3. 8 "likely fine" plants all confirmed wrong by user (Stade was in a river): all fixed to Wikipedia coords
  4. 10 Wikidata-unmatched plants: all had Wikipedia pages, 5 were 41-404km off (BREST, Baltic, CEFR, CVTR, BONUS)
  5. 74 plants bulk-adopted Wikidata coords (>50m discrepancies)
  6. 100 plants updated to Wikipedia GeoData coords via MediaWiki API scrape
  7. EL-4 renamed to Brennilis (broken plant page)
- **Chinese data overhaul**: Root cause analysis revealed Chinese UC data was systematically unreliable (approximate coords, conflated reactor types, missing units). Fixed via WNA reactor database cross-reference:
  - Shidaowan rebuilt: corrected CAP1400 data (capacity, dates, status), added 2 missing HPR1000 units
  - Coordinate fixes for 37 Chinese reactors across 11 plants (Jinqimen was 550km off!)
  - Data fixes: Bailong reactor type (HPR1000→CAP1000), Taipingling-1 now operational, capacity/date corrections for 21 reactors
  - Added Ningde-6 (missing UC reactor)
- **Verification scripts**: `verify_wikidata.py`, `verify_names.py`, `verify_coordinates.py`, `apply_corrections.py`, `fix_chinese_data.py`, `fix_final_coords.py`, `fix_remaining_coords.py`, `fix_unmatched_coords.py`, `adopt_wikidata_coords.py`, `scrape_wikipedia_coords.py`, `manual_review_checklist.py`
- **Design lineage pages**: D3.js family tree visualization, Leaflet maps, Chart.js country breakdown. Added navigation links across all templates. Esri Light Gray Canvas tiles for English labels.

## Mar 10-11, 2026 — Design Series + Lineages Data Layer
- Filled all `design_series` gaps: **100% coverage**
- Created `design_lineages` (24 families) and `design_series_info` (123 series) tables
- Predecessor chains form valid tree structures (75 edges, no cycles)

## Mar 8-9, 2026 — Major Data Audit & Feature Push
- Fixed status errors across 10 countries, added 41 missing UC reactors
- Added "Suspended" status, map filter toggles, annual generation chart
- Created Sources & Methodology page
- Added coordinates for 131 reactors, moved deployment to Fly.io
