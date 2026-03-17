# Nuclear Database — Feature Decisions

## Chart Design

- **Generation chart**: Annual nuclear share of global electricity (%) 1970-2024. Nuclear TWh from PRIS (coverage-adjusted), global TWh from EI Statistical Review.
- **Coverage adjustment**: Scale each year's raw PRIS sum by `(operational_reactors / reporting_reactors)` to estimate full-fleet output. See `/sources` page for full methodology.

## Map Design

- **Grouping**: Multi-unit plants grouped by coordinate proximity (4 decimal places).
- **Status filter**: Toggles — All / Operational / Under Construction / Suspended / Shutdown. Marker color = best status at plant.
- **Reactor statuses**: Operational, Under Construction, Suspended (IAEA "Suspended Operation"), Permanent Shutdown. "Under Construction" = IAEA first concrete pour definition.

## Computed Fields

- **Capacity factor**: Computed at query time using historical capacity: `electricity_gwh / (effective_gross / 1000 * 8760)`. The `effective_gross` comes from the `capacity_changes` table (most recent entry where `effective_date <= year-end`), falling back to `reactors.gross_capacity_mw` for reactors without capacity change records. This ensures uprated/derated reactors use period-correct capacity.
- **Reactor age**: Computed live via `JULIANDAY('now') - JULIANDAY(commercial_operation)`.
- **Installed capacity history**: `/api/capacity/history` endpoint, filtered by `?country=` or `?technology=`. For each year 1954-2026, sums effective gross capacity of all reactors with `commercial_operation <= year-end` and no `permanent_shutdown` before year-start. Green area chart (#16a34a) on dashboard, country, and technology pages. Tooltip shows GW + reactor count.

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
