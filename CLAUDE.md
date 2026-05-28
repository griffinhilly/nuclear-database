# Nuclear Reactor Database

## Overview

Flask web app serving a global nuclear reactor database with 739 reactors across 39 countries, plus 122 planned reactors. Backed by SQLite (`nuclear_reactors.db`) with reactor specs, generation history (1954-2024), and geographic coordinates. Reactor data verified against IAEA PRIS and cross-checked with WNA (March 2026).

## Architecture

- **`app.py`** — Main Flask app. All routes, API endpoints, validation logic. Runs on port 5001 locally, 8080 on Fly.io.
- **`templates/`** — 10 Jinja2 templates (dashboard, 8 detail pages, sources page). Client-side JS with Chart.js and Leaflet.
- **`nuclear_reactors.db`** — SQLite database. Key tables: `reactors`, `generation_annual`, `capacity_changes`, `countries`, `technologies`, `planned_reactors`, `design_lineages`, `design_series_info`.
- **`start.sh`** — Entrypoint for Fly.io. Copies DB from image to persistent volume on every deploy.

## API Tiers

- **Free (no key)**: `/api/stats`, `/api/countries`, `/api/countries/<country>/summary`, `/api/countries/<country>/detail`, `/api/technologies`, `/api/reactors/count`, `/api/generation/decades`, `/api/capacity/history`, `/api/data/validation`
- **Paid (requires `X-API-Key` header or `?api_key=`)**: `/api/reactors`, `/api/reactors/<id>`, `/api/reactors/search`, `/api/query`, `/api/planned`, `/api/map`
- Demo key for development: `demo-key-12345`

## Running

```bash
python3 app.py              # Starts on port 5001
python3 app.py --validate   # Prints data validation report
```

Dependencies: `flask`, `gunicorn` (see `requirements.txt`). Uses Python 3.8+ with sqlite3.

## Git / Deployment

- Remote: `git@github.com:griffinhilly/nuclear-database.git` (SSH)
- **Primary deployment: Fly.io** (`fly.toml`, app name: `nuclear-database`, region: `ord`)
- Fly.io uses a persistent volume mounted at `/data` for the SQLite database.
- The `fly` CLI is at `~/.fly/bin/fly.exe`. Note: `fly ssh` does not work from Git Bash on Windows — use PowerShell or cmd if SSH is ever needed.

```bash
git push origin main
fly deploy
```

## Data Change Protocol

1. **Bulk updates (>5 rows)**: Create a numbered SQL migration in `migrations/` before applying.
2. **Sampling protocol**: For pattern-based fixes touching 50+ records without individual research, spot-check 10-15 records against an authoritative source before and after. Document the sample.
3. **Post-update validation**: Run `python scripts/validate_db.py` after any bulk change. Zero issues required before deploy.
4. **Capacity source priority**: NRC (US only) > WNA > PRIS for operational reactors. PRIS can be stale for recently-uprated reactors.
5. **Binary DB merge conflicts**: Take remote DB (preserves new schema), replay SQL migrations, validate.

## Key Decisions

- **Coordinates**: Wikipedia GeoData is the gold standard — always use article coordinates, never dismiss small discrepancies. See `guides/data-quality.md` for full notes.
- **Capacity**: `net_capacity_mw` = `reference_power_mw` = PRIS Reference Unit Power (current/final). Original design values in `capacity_changes` initial records. **Always query `capacity_changes` for historical/time-series questions, not just the static `reactors` table — plants change capacity over time (uprates, derates).**
- Other feature decisions (chart design, map grouping, capacity factor formula, design lineage structure): see `guides/feature-decisions.md`

## Situational Guides

- When modifying map, charts, capacity factor, or design lineage pages → read `guides/feature-decisions.md`
- When adding or verifying reactor data → read `guides/data-quality.md`
- When doing bulk data updates → read `migrations/README.md` and follow the Data Change Protocol above
- When re-running or extending the WNA audit → read `wna_audit.py` header comments and `MEMORY.md` decisions
- When debugging issues that may trace to prior work → read `guides/session-log.md`
