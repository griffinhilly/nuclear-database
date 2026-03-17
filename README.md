# Global Nuclear Database

A comprehensive web application tracking the world's nuclear reactor fleet — 739 reactors across 39 countries with specifications, generation history, geographic data, and planned projects. All reactor coordinates verified against Wikipedia. Capacity and status cross-checked with WNA.

**Live site:** [nuclear-database.fly.dev](https://nuclear-database.fly.dev/)

## Features

- **Dashboard** — Global statistics, fleet analytics charts, interactive map, reactor data tables
- **Interactive Map** — All reactor locations with status filter toggles. Click any plant to see all its reactors.
- **Detail Pages** — Drill into any reactor, plant, country, technology, model, owner, supplier, or status group
- **Design Lineages** — 24 reactor design families tracing evolutionary trees from Gen I prototypes to Gen III+ designs, with predecessor links and generation labels
- **Generation History** — Annual electricity generation data from 1954-2024 with coverage-adjusted estimates
- **Nuclear Share Chart** — Nuclear's percentage of global electricity from 1970-2024
- **Planned Reactors** — 122 planned projects worldwide with likelihood ratings and sources
- **Sources & Methodology** — Full data attribution and calculation methods at `/sources`
- **REST API** — Free and paid tiers for programmatic access

## Data Sources

| Code | Source | Covers |
|------|--------|--------|
| [PRIS] | IAEA Power Reactor Information System | Reactor specs, status, generation data |
| [WNA] | World Nuclear Association | Planned reactors, country profiles, capacity cross-check |
| [EI-SR] | Energy Institute Statistical Review | Global electricity totals |

All reactor statuses verified against IAEA PRIS as of March 2026.

## Running Locally

```bash
pip install -r requirements.txt
python app.py                # Starts on http://localhost:5001
```

## Deployment

Deployed on Fly.io. After pushing changes:

```bash
git push origin main
fly deploy
```

## Tech Stack

- **Backend:** Python / Flask / SQLite
- **Frontend:** Vanilla JS, Chart.js, Leaflet.js
- **Hosting:** Fly.io (3 VMs, ord region, persistent volume for DB)
