# Nuclear Reactor Database

## Overview

Flask web app serving a global nuclear reactor database with 743 reactors across 39 countries, plus 121 planned reactors. Backed by SQLite (`nuclear_reactors.db`) with reactor specs, generation history (1954-2025), and geographic coordinates. Structured fields aligned to the IAEA PRIS JSON API (pris-stats.iaea.org) in the Oct 2026 audit (migrations 023-028); PRIS pulls/diffs: `scripts/pris_api_pull.py`, `scripts/pris_api_diff.py`.

## Architecture

- **`app.py`** — Main Flask app. All routes, API endpoints, validation logic. Runs on port 5001 locally, 8080 on Fly.io.
- **`templates/`** — 10 Jinja2 templates (dashboard, 8 detail pages, sources page). Client-side JS with Chart.js and Leaflet.
- **`nuclear_reactors.db`** — SQLite database. Key tables: `reactors`, `generation_annual`, `capacity_changes`, `countries`, `technologies`, `planned_reactors`, `design_lineages`, `design_series_info`.
- **`start.sh`** — Entrypoint for Fly.io. Copies DB from image to persistent volume on every deploy.

## API Tiers

- **The whole API is free (Griffin, 2026-10-16).** The paid tier is switched off, not deleted (`PAID_TIER_ENABLED` in app.py), because it may return. Endpoints marked `@require_api_key('paid')` (`/api/reactors`, `/api/reactors/<id>`, `/api/reactors/search`, `/api/query`, `/api/planned`, `/api/map`) need a key only when `PAID_TIER_ENABLED=1`; keys come only from Fly secrets (`API_KEY_PAID`, `API_KEY_FREE`). The old development key was printed in this public repo and no longer exists in code. Never hardcode a key again. If the paid tier returns, the homepage and reactor pages call those endpoints from the browser and need server-side data first.

## Launch plumbing (2026-10-16)

- **Page meta**: `page_meta()` + `inject_page_meta()` in app.py give every page its own `<title>`, description, canonical link and Open Graph / Twitter tags (`templates/_meta.html`, included after `<title>` in every public template). Detail pages render in the browser, so this is all link previews and search engines see. Preview image: `static/og-card.png`, rebuilt by `python scripts/build_og_card.py`.
- **`SITE_URL`** (env) sets the public address for canonical links, previews and the sitemap. Set it as a Fly secret/env when the site moves to its REG address.
- **`/robots.txt`, `/sitemap.xml`** (every reactor, plant, country, technology, status, owner, supplier, model, lineage and planned page). `/embed/map` is noindex. Branded 404/500 page: `templates/error.html`; `/api/*` errors stay JSON.
- **Reader corrections**: "Suggest a correction" in `_reg_footer.html` → `POST /api/corrections` → `/data/submissions.db` on whichever Fly machine took the request (3 machines, one volume each). Review with `python scripts/review_submissions.py list|accept|decline` — it reads every machine through `/admin/api/submissions` (header `fly-force-instance-id`), authorized by the `ADMIN_TOKEN` Fly secret; the local copy of that credential lives in `~/.config/nuclear-database/admin_token`, never in the repo. Accepting writes a public line to `data/contributions.json`; commit + deploy publishes it on `/contributions`. The data change itself still goes through a migration.

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
~/.fly/bin/flyctl.exe deploy --remote-only   # NOT fly.exe: that symlink is 0 bytes and Windows blocks it
```
- **Smart App Control blocks the current `flyctl.exe` (Oct 15)**; the March build still runs: `~/.fly/bin/flyctl.exe.old deploy ../ndb-deploy --remote-only` (pass the worktree path; don't cd the session into it).
- **Deploy what's committed, not the working tree**: the Docker build copies files from disk, so uncommitted prototypes ship too. To deploy only HEAD: `git worktree add ../ndb-deploy HEAD`, deploy from there, then `git worktree remove`.
- **Line endings**: `start.sh` must be LF. `.gitattributes` forces `*.sh eol=lf`; a CRLF `start.sh` crash-loops every machine ("./start.sh: No such file or directory", outage 2026-10-14). After any deploy, check `https://nuclear-database.fly.dev/api/stats`.

## Data Change Protocol

1. **Bulk updates (>5 rows)**: Create a numbered SQL migration in `migrations/` before applying.
2. **Sampling protocol**: For pattern-based fixes touching 50+ records without individual research, spot-check 10-15 records against an authoritative source before and after. Document the sample.
3. **Post-update validation**: Run `python scripts/validate_db.py` after any bulk change. Zero issues required before deploy.
4. **Capacity source priority**: NRC (US only) > WNA > PRIS for operational reactors. PRIS can be stale for recently-uprated reactors.
5. **Binary DB merge conflicts**: Take remote DB (preserves new schema), replay SQL migrations, validate.
6. **Invariant scan BEFORE spot-sampling on bulk writes**: check join-key integrity (pris_id uniqueness + agreement with `pris_id_map_2026-07.json`), post-shutdown activity, and CF range FIRST; only then sample values. Sampling verifies values and is structurally blind to identity/key violations (2026-07-06: a 12/12 value sample passed while 13 duplicate pris_ids double-counted ~100 TWh).
7. **Provenance rule — model recall is never a source**: any script that bulk-writes factual values must record a per-row source naming where each value was *retrieved*; a source column written by the same process that wrote the values is self-attestation and counts as unverified. Verification agents must report BLOCKED rather than confirm from memory when search is unavailable (2026-07-21: search-dead agent hallucinated a "correction" to Konvoi's real 18x18 lattice).
8. **Vendor-field whitelist (zero-doubt policy, 2026-07-20)**: reactor_details supply-chain fields may only hold values listed visible=yes in `verification_2026-07/final_verdicts.psv` — validator check 15 enforces this. New attestations (e.g. from Noah/Dirk, whose word is gospel) are appended to the whitelist in the same change that writes the DB.
9. **Agent-facing verification extracts must carry all sibling columns** needed to judge a mismatch (gross AND net capacity, etc.) — an incomplete extract caused 2 false-positive corrections on 2026-07-20.
10. **Consistency gate before every deploy (2026-10-14)**: `python scripts/site_consistency.py` must show 0 FAIL. It checks that every quantity shown in two places agrees (cards vs charts vs drill-downs, every year), charts plot what their titles say, and 27 pages render in headless Chrome. Before a migration, `--migration migrations/0xx.sql` lists the pages/charts that read what it writes; re-check those. Origin: the homepage said 420 operating reactors while its chart said 436, the 2025 generation card was ~5% high, and the age chart dropped 34 reactors — each surface had its own rule.
11. **One rule per quantity**: history charts and cards use `OPERATING_IN_YEAR_SQL`, `UNDER_CONSTRUCTION_IN_YEAR_SQL`, `CAPACITY_AT_YEAR_END_SQL`, `AGE_SQL` in app.py. Never write a new counting rule inline.
12. **Releases get a before/after review**: `python scripts/compare_site_versions.py --old-app <deployed app.py> --old-db <live copy> --new-db <candidate>` lists every changed served value; review the largest with fresh-context agents before deploying.
13. **Freshness**: run `python scripts/pris_api_pull.py --force && python scripts/freshness_check.py` monthly (status drift vs PRIS, unrecorded grid connections/shutdowns, passed licence/expected dates, generation coverage). After any PRIS generation pull, run `scripts/pris_copied_month_check.py` (PRIS Dec 2021 = Nov for 90 US units).
14. **Generation sources**: per-reactor rows from the PRIS data browser (`scripts/pris_generation_pull.py`); US unit-years where EIA-923 differs >2% take EIA (`audit/pris_generation/overrides_eia.psv`). World/country headline totals come from `external_series` (Ember/EI via OWID), never from summing reactor rows. Every generation row carries `source`.

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
