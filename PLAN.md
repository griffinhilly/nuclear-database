# Nuclear Database — Plan

## Completed
- Core Flask app with SQLite backend (688 reactors, 38 countries)
- Dashboard with stat cards, charts, Leaflet map, data tables
- Detail pages: reactor, plant, country, technology, status, model, supplier, owner
- All links flow through plant pages (map markers -> plant -> reactor)
- Generation data backfill (94% coverage for 2024)
- Visual design refresh (light theme, modern cards/typography)
- Countries choropleth map
- Fly.io deployment (3 VMs, ord region, persistent volumes)

## Remaining

### Uprates / Capacity Additions
- Track historical capacity changes (uprates, derates) for reactors over time
- Data source TBD (IAEA PRIS, WNA, or manual research)
- Schema: new table linking reactor_id to capacity changes with dates
- Display on reactor and plant detail pages (timeline or table)
- Aggregate into country/technology/global capacity history charts

### Ongoing
- Generation data gap monitoring (41 reactors without PRIS ID, mostly idle Japanese units)
- Data freshness: re-run backfill scripts when 2025 PRIS data becomes available
