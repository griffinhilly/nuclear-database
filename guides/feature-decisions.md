# Nuclear Database — Feature Decisions

## Chart Design

- **Generation chart**: Annual nuclear share of world electricity (%) 1985-2025. Numerator and denominator both from the published series in `external_series` (Ember + Energy Institute via Our World in Data, gross). The old coverage adjustment (scaling the PRIS sum by operating/reporting reactors) was dropped on 2026-10-14: it overstated 2025 by ~5%.
- **World totals come from published series; drill-downs from reactor rows.** Homepage world generation reads `external_series`; reactor/plant/country pages sum `generation_annual` (IAEA PRIS, net).
- **One rule per quantity** (2026-10-14): every history chart uses `OPERATING_IN_YEAR_SQL` / `UNDER_CONSTRUCTION_IN_YEAR_SQL` / `CAPACITY_AT_YEAR_END_SQL` / `AGE_SQL` in app.py, so the current-year point equals the stat card. `scripts/site_consistency.py` enforces the agreement; run it before every deploy.
- **History + projection style** (Griffin, 2026-10-14): the past is a solid line ending in a **solid dot at today's value**; the projection continues from the dot as a **dashed line** in the same colour. No vertical "today" rule. Applies to every forward-looking chart. Projection = reactors under construction at announced dates or country median build time since 2010; closures not included until we hold sourced closure dates; units building >12 years without an announced date are left out. Method text shown under the chart.

## Map Design

- **Grouping**: Multi-unit plants grouped by coordinate proximity (4 decimal places).
- **Status filter**: Toggles — All / Operational / Under Construction / Suspended / Shutdown. Marker color = best status at plant.
- **Reactor statuses**: Operational, Under Construction, Suspended (IAEA "Suspended Operation"), Permanent Shutdown. "Under Construction" = IAEA first concrete pour definition.

## Computed Fields

- **Capacity factor**: Computed at query time using historical capacity: `electricity_gwh / (effective_gross / 1000 * 8760)`. The `effective_gross` comes from the `capacity_changes` table (most recent entry where `effective_date <= year-end`), falling back to `reactors.gross_capacity_mw` for reactors without capacity change records. This ensures uprated/derated reactors use period-correct capacity.
- **Reactor age**: Computed live from first grid connection (IAEA PRIS convention), falling back to commercial operation: `AGE_SQL` in app.py. The stored `reactors.age_years` column is stale and must not be read.
- **Installed capacity history**: `/api/capacity/history` endpoint, filtered by `?country=` or `?technology=`. For each year 1954 to the current year, sums effective gross capacity of reactors operating under `OPERATING_IN_YEAR_SQL` (started by year-end via commercial operation or grid connection, not shut or suspended before year-start); the current year uses each reactor's current rating. Green area chart (#16a34a) on dashboard, country, and technology pages. Tooltip shows GW + reactor count.

## Design Lineage Structure

- 24 lineage families (e.g., "GE BWR", "Framatome PWR", "VVER") in `design_lineages` table.
- Each of 123 unique `design_series` values mapped to a lineage with generation order, predecessor links, and Gen I/II/III/III+/IV labels in `design_series_info` table.
- Predecessor chains form tree structures (no cycles). All 733 reactors have `design_series` (100% coverage).
- Lineage pages: D3.js family tree visualization, Leaflet maps, Chart.js country breakdown.

## Sources & Attribution

- All data attributed via coded references: [PRIS], [WNA], [EI-SR].
- Methodology documented at `/sources`.
- IAEA "first concrete pour" = under construction. Anything less = planned.

## Status Decisions

- **Suspended** status used for: post-Fukushima Japan (14 reactors with NRA restart applications), India Tarapur 1/2, India Rajasthan 1, China CEFR, USA Palisades.
- Plant names use proper diacritics/Unicode (Krümmel not Kruemmel, Zaporizhzhia not Zaporozhye).
