# Nuclear Database — Plan

## Completed

### Core App
- Flask app with SQLite backend (733 reactors, 39 countries)
- Dashboard with stat cards, charts, Leaflet map, data tables
- 8 detail pages: reactor, plant, country, technology, status, model, supplier, owner
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

### Design Lineages — Data Layer (Mar 11, 2026)
- All 729 reactors have `design_series` (100% coverage)
- `design_lineages` table: 24 families with slug, description, origin country, designer, technology type
- `design_series_info` table: 123 series with lineage FK, generation order/label, capacity, year, predecessor, description
- Script: `add_lineages.py`

## Remaining

### Design Lineages — Visualization (next session)
- Lineage listing page (`/lineages`) — overview of all 24 families with reactor counts, status breakdown
- Lineage detail page (`/lineage/<slug>`) — interactive family tree diagram (inspired by PDF Ch.2 diagrams: timeline-based trees with branching, order dates, commercial operation, capacity, containment)
- Link from reactor detail page Design & Safety card to lineage page
- Consider D3.js or similar for the tree visualization
- Expose lineage data via API endpoints

### Uprates / Capacity Additions (#6)
- Track historical capacity changes (uprates, derates) for reactors over time
- Data source TBD (IAEA PRIS, WNA, or manual research)
- Schema: new table linking reactor_id to capacity changes with dates
- Display on reactor and plant detail pages (timeline or table)
- Aggregate into country/technology/global capacity history charts

### Coordinate Remaining
- ~15 plants unmatched by automated Wikipedia scraper (bad name matches) — most already verified manually
- Multi-site consolidation decision (Madi): treat Kursk 1/2, Leningrad 1/2, Novovoronezh 1/2, Hanul/Shin-Hanul as single plants?
- Duplicate planned_reactors entries to clean up: Xudabao 3-4 (ids 187,188) and San'ao 3 (id 176)

### Data Quality
- #5 from PLANNED_ADDITIONS: Erroneous generation data for Braidwood-2 (2025/2030 entries need removal)
- Generation data gap monitoring (41 reactors without PRIS ID, mostly idle Japanese units)
- Data freshness: re-run backfill scripts when 2025 PRIS data becomes available
- Non-Chinese countries haven't been WNA-audited for reactor specs (capacity, dates, status)

### Ownership Audit (#4, #5 from revisions)
- Verify ownership for all reactors (Exelon->Constellation, decommissioning transfers)
- Cross-reference NRC, Wikipedia, company websites
