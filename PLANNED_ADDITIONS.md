# Planned Additions

## Completed

- ~~**1. Reactor Links in Home Page Table**~~ — Done. Table rows link to reactor detail pages.
- ~~**2. Operating Life Display Format**~~ — Done. Shows "X Years, Y Days" format.
- ~~**3. Map Marker Selection for Multi-Unit Plants**~~ — Done. Multi-unit plants grouped into single markers with popup listing all units.
- ~~**4. Average Capacity Factor Not Populated**~~ — Done. Computed at query time from generation and capacity data.
- ~~**6. Display Max Capacity**~~ — Done. Thermal, gross, and net capacity shown on detail page.

## Remaining

### 5. Erroneous Generation Data (Braidwood-2)
- There are 4 GWh of generation listed for both 2025 and 2030. These erroneous values should be removed and the data re-pulled from the source.

### 7. Generation Data Gaps
- Generation data post-2020 is incomplete (~112/430 reactors reporting for 2022-2024). The decade chart uses coverage adjustment, but underlying data should be improved.
- Automated validation endpoint exists at `/api/data/validation`. `fetch_missing_generation.py` partially addresses 2021.

### 8. Country Detail Pages
Create detail pages for individual countries (similar to reactor detail pages). Should include:
- Country overview stats (operational reactors, total capacity, avg fleet age)
- Generation history chart for the country
- List of all reactors in the country with links to reactor detail pages
- Map zoomed to the country's reactor locations

### 9. Show 2024 Generation Data on Home Page
Update the home page stats cards to display 2024 generation data instead of 2023. The "2023 Generation (TWh)" card should pull the most recent year with sufficient data coverage, or show coverage-adjusted 2024 figures.
