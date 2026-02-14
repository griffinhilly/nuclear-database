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

### 7. Generation Data Gaps
- Generation data post-2020 is incomplete (~114/436 reactors reporting for 2022-2024, ~26% coverage). The decade chart and home page stats use coverage adjustment to estimate full-fleet output.
- `KNOWN_PRIS_IDS` dictionary in `fetch_pris_generation.py` only covers 267 reactors (explicitly incomplete for China, Japan, France). 178 operational reactors have no PRIS ID mapped.
- `pris_scraper.py` has untapped country-level discovery that could expand PRIS ID coverage.
- Alternative data sources (US EIA, ENTSO-E, WNA, national regulators) have not been explored.
- Automated validation endpoint exists at `/api/data/validation`. `fetch_missing_generation.py` partially addresses 2021.
