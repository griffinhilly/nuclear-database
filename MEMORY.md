# Nuclear Database — Memory

## Current State (Mar 2026)
- **733 reactors**: 416 Operational, 66 Under Construction, 22 Suspended, 229 Permanent Shutdown
- **122 planned reactors** with likelihood ratings (High/Medium/Low)
- **39 countries**, all verified against IAEA PRIS
- **All reactors have coordinates** — verified against Wikipedia GeoData (gold standard)
- **Design lineages**: 24 families, 123 series, 100% coverage
- Live at https://nuclear-database.fly.dev/

## Recent Sessions

### Mar 12, 2026 — Coordinate & Name Verification + Chinese Data Overhaul
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

### Mar 10-11, 2026 — Design Series + Lineages Data Layer
- Filled all `design_series` gaps: **100% coverage**
- Created `design_lineages` (24 families) and `design_series_info` (123 series) tables
- Predecessor chains form valid tree structures (75 edges, no cycles)

### Mar 8-9, 2026 — Major Data Audit & Feature Push
- Fixed status errors across 10 countries, added 41 missing UC reactors
- Added "Suspended" status, map filter toggles, annual generation chart
- Created Sources & Methodology page
- Added coordinates for 131 reactors, moved deployment to Fly.io

## Data Quality Lessons
- **Chinese UC data is highest-risk**: PRIS has delays, coordinates are often city-center approximations (≤2 decimal places), multi-phase naming creates confusion. WNA reactor database is more reliable for Chinese plants.
- **Coordinate precision is a quality signal**: Operational plants have 4+ decimal places (PRIS-verified). Round coordinates (≤2 decimals) = approximated, needs verification.
- **Wikipedia is the coordinate gold standard**: Every manual spot-check confirmed Wikipedia infobox coords are accurate (pointing to the actual reactor building). Discrepancies under 1km were NOT "different reference points" — they were genuine errors (Stade was in a river). OSM was wrong for Berkeley. Google Maps was wrong for Shidao Bay. WNA is best for reactor specs but doesn't have coordinates.
- **Coordinate verification complete**: Wikipedia GeoData coordinates adopted as gold standard for all plants. Final sweep via MediaWiki API `prop=coordinates` updated 100 more plants. ~15 plants unmatched by automated tools (bad name matches); coords already verified manually or via earlier batches. Multi-site complexes (Kursk 1/2, Leningrad 1/2, Novovoronezh 1/2, Hanul/Shin-Hanul) have per-site coordinates — user may consolidate these as single plants (Madi to decide).

## Gotchas
- `fly ssh` doesn't work from Git Bash on Windows (handle error). Use PowerShell or cmd if needed.
- `fly.exe` is at `~/.fly/bin/fly.exe` (not on PATH in bash)
- Global electricity data in app.py is hardcoded dict (1970-2024) from EI Statistical Review
- Reactor `name` column doesn't exist — use `plant_name` + `unit_number`
- Python print with Unicode chars fails on Windows cp1252 — add `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
- Chinese plant naming is complex: same site can have different plant_name entries for different reactor phases (Shidao Bay vs Shidaowan, Qinshan 1/2/3)

## Decisions
- IAEA "first concrete pour" = under construction. Anything less = planned.
- Suspended status used for: post-Fukushima Japan (14 reactors with NRA restart applications), India Tarapur 1/2, India Rajasthan 1, China CEFR, USA Palisades
- Fly.io as primary deployment over Render (persistent volumes, better control)
- start.sh always copies DB on deploy (no conditional check) — simpler, ensures fresh data
- Plant names use proper diacritics/Unicode (Krümmel not Kruemmel, Zaporizhzhia not Zaporozhye)
- Wikipedia GeoData coordinates are the gold standard for all plants. Use MediaWiki API `prop=coordinates` or click "External maps" on the article. Never dismiss small (<1km) discrepancies — they're real errors, not reference-point differences.
- Multi-site complexes (Kursk, Leningrad, Novovoronezh, Hanul/Shin-Hanul) need per-site coordinates that differ from the main Wikipedia article. Pending Madi's decision on whether to consolidate.
