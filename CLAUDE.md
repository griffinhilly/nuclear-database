# Nuclear Reactor Database

## Overview

Flask web app serving a global nuclear reactor database with 688 reactors across 38 countries. Backed by a SQLite database (`nuclear_reactors.db`) with reactor specs, generation history (1954-2024), and geographic coordinates. Data sourced from IAEA PRIS.

## Architecture

- **`app.py`** — Main Flask app. All routes, API endpoints, and validation logic. Runs on port 5001.
- **`templates/index.html`** — Dashboard with stat cards, Chart.js charts, Leaflet map, and data tables.
- **`templates/reactor_detail.html`** — Individual reactor page with generation history chart and specs.
- **`templates/country_detail.html`** — Country detail page with fleet overview, generation history chart, reactor list, and map.
- **`nuclear_reactors.db`** — SQLite database. Key tables: `reactors`, `generation_annual`, `countries`, `technologies`, `planned_reactors`.

## API Tiers

- **Free (no key)**: `/api/stats`, `/api/countries`, `/api/countries/<country>/summary`, `/api/countries/<country>/detail`, `/api/technologies`, `/api/reactors/count`, `/api/generation/decades`, `/api/data/validation`
- **Paid (requires `X-API-Key` header or `?api_key=`)**: `/api/reactors`, `/api/reactors/<id>`, `/api/reactors/search`, `/api/query`, `/api/planned`, `/api/map`
- Demo key for development: `demo-key-12345`

## Running

```bash
python3 app.py              # Starts on port 5001
python3 app.py --validate   # Prints data validation report
```

Dependencies: `flask`, `gunicorn` (see `requirements.txt`). Uses Python 3.8+ with sqlite3.

## Data Coverage Issue

Generation data post-2020 is incomplete — only ~112 of ~430 operational reactors report data for 2022-2024. The `/api/generation/decades` endpoint handles this with coverage adjustment: it scales each year's raw sum by `(operational_reactors / reporting_reactors)` to estimate full-fleet output, then averages across years in the decade.

## Key Decisions

- **Generation chart shows avg annual TWh/yr per decade** (not total decade sums) to make decades with different year counts comparable. The 2020s uses a dashed line and diamond marker to indicate it's a projection.
- **Map groups multi-unit plant markers** by rounding coordinates to 4 decimal places. Popup lists all units with links.
- **Capacity factor is computed at query time** from `electricity_gwh / (gross_capacity_mw / 1000 * 8760)` rather than relying on stored values.
- **Reactor age is computed live** via `JULIANDAY('now') - JULIANDAY(commercial_operation)`.

## Planned Work

See `PLANNED_ADDITIONS.md` for the backlog. Items 1-4 and 6 have been addressed. Remaining:
- #5: Erroneous generation data for Braidwood-2 (2025/2030 entries need removal)
- #7: Generation data gaps (2021 partially addressed via `fetch_missing_generation.py`, automated validation endpoint exists at `/api/data/validation`)

## Git / Deployment

- Remote: `git@github.com:griffinhilly/nuclear-database.git` (SSH)
- Deployment config: `render.yaml` (Render)
