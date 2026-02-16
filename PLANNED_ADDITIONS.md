# Planned Additions

## Completed

- ~~**1. Reactor Links in Home Page Table**~~ — Done. Table rows link to reactor detail pages.
- ~~**2. Operating Life Display Format**~~ — Done. Shows "X Years, Y Days" format.
- ~~**3. Map Marker Selection for Multi-Unit Plants**~~ — Done. Multi-unit plants grouped into single markers with popup listing all units.
- ~~**4. Average Capacity Factor Not Populated**~~ — Done. Computed at query time from generation and capacity data.
- ~~**5. Erroneous Generation Data (Braidwood-2)**~~ — Done. Erroneous 2025/2030 entries already removed from database.
- ~~**6. Display Max Capacity**~~ — Done. Thermal, gross, and net capacity shown on detail page.
- ~~**8. Country Detail Pages**~~ — Done. Fleet overview, generation chart, reactor list with links, and map zoomed to country.
- ~~**9. Show 2024 Generation Data on Home Page**~~ — Done. Stats card dynamically shows most recent year with coverage-adjusted estimate and reporting percentage.

## Remaining

### 7. Generation Data Gaps — Largely Resolved
- **PRIS ID coverage**: 389/430 operational reactors (90.5%), up from 252 (58.6%). `backfill_pris_coverage.py` discovers IDs via ASP.NET postbacks from all 38 PRIS countries.
- **2024 generation coverage**: 404/430 reactors (94.0%), up from 108 (25.1%). 1,133 new generation records inserted.
- **Year coverage (2020+)**: 2020: 98.8%, 2021: 96.0%, 2022: 90.5%, 2023: 92.1%, 2024: 94.0%.
- **Remaining gaps**: 41 reactors without PRIS ID are mostly Japanese units idle since Fukushima (listed as Operational but not generating), 3 German reactors shut down in 2023, and Taiwan units PRIS lists as non-operational. 29 reactors have no post-2020 data for the same reasons.
- Alternative data sources (US EIA, ENTSO-E, WNA, national regulators) have not been explored but are less critical now.

### 10. Visual Design Refresh
- Update the website's visual design to look less drab — modernize colors, typography, card styles, and overall aesthetic.

### 11. Hosting Migration
- Move off Render to a hosting provider with better uptime that doesn't require cold-start reboots after periods of inactivity. Evaluate options like Fly.io, Railway, or a VPS.

### 12. Global Nuclear Countries Map
- Add a choropleth or highlighted world map to the countries overview showing which countries have nuclear power programs. Color-code by operational reactor count or capacity, similar to the existing reactor location map but at the country level.
