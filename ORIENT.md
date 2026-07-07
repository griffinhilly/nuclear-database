# Nuclear Database — Orientation

A Flask web app tracking the world's nuclear reactor fleet: 738 reactors across 39 countries with specs, generation history (1954-2025), geographic coordinates, design lineages, and 123 planned projects. All data verified against IAEA PRIS and cross-checked with WNA. Live at [nuclear-database.fly.dev](https://nuclear-database.fly.dev/).

## Codebase Shape

- **`app.py`** — Monolith Flask app. All routes, API endpoints, validation logic.
- **`nuclear_reactors.db`** — SQLite database. Core tables: `reactors`, `generation_annual`, `capacity_changes`, `planned_reactors`, `design_lineages`, `design_series_info`, `entity_descriptions`.
- **`templates/`** — 13 Jinja2 templates (dashboard, 9 detail pages, lineages, sources). Client-side JS with Chart.js and Leaflet.
- **`*.py` scripts** — ~30 one-shot data scripts (backfills, audits, coordinate verification, description insertion). Most are run-once artifacts, not part of the running app.
- **`guides/`** — Feature decisions, data quality notes, session log.
- **Audit ledgers** (repo root) — `noah_review.md`, `cooling_audit_2026-07.md`, `pris_id_repair_2026-07.md`; `pris_id_map_2026-07.json` is the ground-truth PRIS id→name map (validate any pris_id against it before keying a backfill on it).

## Common Operations

```bash
pip install -r requirements.txt
python app.py                # Local server on port 5001
python app.py --validate     # Data validation report

git push origin main         # Push to griffinhilly/nuclear-database
~/.fly/bin/fly.exe deploy    # Deploy to Fly.io
```

## Known Weirdness

- `fly ssh` does not work from Git Bash — use PowerShell or cmd.
- `fly.exe` lives at `~/.fly/bin/fly.exe` (not on PATH in bash).
- PRIS blocks Python `requests` via TLS fingerprinting — data scripts use `curl` subprocess.
- Ghost process can linger on port 5001 after restarts — use 5002 or `taskkill`.
- Global electricity data (for nuclear share chart) is a hardcoded dict in `app.py`, not from the DB.

## Key Links

- **Live site:** https://nuclear-database.fly.dev/
- **Repo:** github.com/griffinhilly/nuclear-database
- **Data sources:** IAEA PRIS, World Nuclear Association, Energy Institute Statistical Review
- **Brand:** REG color palette (teal/yellow/emerald/orange) — see `~/Projects/reg/STYLE/style-guide.md`
