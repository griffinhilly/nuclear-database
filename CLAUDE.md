# Nuclear Reactor Database

## Overview

Flask web app serving a global nuclear reactor database with 733 reactors across 39 countries, plus 122 planned reactors. Backed by SQLite (`nuclear_reactors.db`) with reactor specs, generation history (1954-2024), and geographic coordinates. All reactor data verified against IAEA PRIS (March 2026).

## Architecture

- **`app.py`** — Main Flask app. All routes, API endpoints, validation logic. Runs on port 5001 locally, 8080 on Fly.io.
- **`templates/`** — 10 Jinja2 templates (dashboard, 8 detail pages, sources page). Client-side JS with Chart.js and Leaflet.
- **`nuclear_reactors.db`** — SQLite database. Key tables: `reactors`, `generation_annual`, `countries`, `technologies`, `planned_reactors`, `design_lineages`, `design_series_info`.
- **`start.sh`** — Entrypoint for Fly.io. Copies DB from image to persistent volume on every deploy.

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

## Data Coverage

Generation data post-2020 is incomplete — only ~112 of ~430 operational reactors report data for 2022-2024. Endpoints use **coverage adjustment**: scale each year's raw sum by `(operational_reactors / reporting_reactors)` to estimate full-fleet output. See `/sources` page for full methodology.

## Key Decisions

- **Generation chart**: Annual nuclear share of global electricity (%) 1970-2024. Nuclear TWh from PRIS (coverage-adjusted), global TWh from EI Statistical Review.
- **Map**: Groups multi-unit plants by coordinate proximity (4 decimal places). Status filter toggles (All/Operational/UC/Suspended/Shutdown). Marker color = best status at plant.
- **Reactor statuses**: Operational, Under Construction, Suspended (IAEA "Suspended Operation"), Permanent Shutdown. "Under Construction" = IAEA first concrete pour definition.
- **Capacity factor**: Computed at query time from `electricity_gwh / (gross_capacity_mw / 1000 * 8760)`.
- **Reactor age**: Computed live via `JULIANDAY('now') - JULIANDAY(commercial_operation)`.
- **Sources**: All data attributed via coded references [PRIS], [WNA], [EI-SR]. Methodology documented at `/sources`.
- **Design lineages**: 24 lineage families (e.g., "GE BWR", "Framatome PWR", "VVER") in `design_lineages` table. Each of 123 unique `design_series` values mapped to a lineage with generation order, predecessor links, and Gen I/II/III/III+/IV labels in `design_series_info` table. Predecessor chains form tree structures (no cycles). All 733 reactors have `design_series` (100% coverage).
- **Coordinates**: All 733 reactors verified against Wikipedia article coordinates (GeoData/External Maps). Wikipedia is the gold standard — always use article coordinates, never dismiss small discrepancies. ~15 plants unmatched by automated tools need manual Wikipedia lookup. Multi-site complexes (Kursk, Leningrad, Novovoronezh, Hanul) have per-site coords.

## Git / Deployment

- Remote: `git@github.com:griffinhilly/nuclear-database.git` (SSH)
- **Primary deployment: Fly.io** (`fly.toml`, app name: `nuclear-database`, region: `ord`)
- Fly.io uses a persistent volume mounted at `/data` for the SQLite database.

### Deploy Process

After pushing to main, deploy to Fly.io:

```bash
git push origin main
fly deploy
```

The `start.sh` script automatically copies the DB from the image to the persistent volume on every deploy, so no SSH step is needed. The `fly` CLI is at `~/.fly/bin/fly.exe`. Note: `fly ssh` does not work from Git Bash on Windows (handle error) — use PowerShell or cmd if SSH is ever needed.

**Always deploy after pushing changes that affect the live site.**
