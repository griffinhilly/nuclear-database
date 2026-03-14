# Nuclear Database — File Index

## Core Application
| File | Description |
|------|-------------|
| `app.py` | Main Flask app — all routes, API endpoints, validation logic |
| `nuclear_reactors.db` | SQLite database (733 reactors, generation data, planned reactors) |
| `requirements.txt` | Python dependencies (flask, gunicorn) |
| `database.py` | Database schema creation and initial data loading script |

## Templates
| File | Description |
|------|-------------|
| `templates/index.html` | Dashboard — stats, charts, map, data tables |
| `templates/reactor_detail.html` | Individual reactor page |
| `templates/plant_detail.html` | Plant page (groups all reactors at a site) |
| `templates/country_detail.html` | Country detail — fleet overview, generation, reactor list, map |
| `templates/technology_detail.html` | Technology type detail page |
| `templates/model_detail.html` | Reactor model detail page |
| `templates/status_detail.html` | Status group detail page |
| `templates/owner_detail.html` | Owner/operator detail page |
| `templates/supplier_detail.html` | Supplier/vendor detail page |
| `templates/containment_detail.html` | Containment type detail page |
| `templates/lineages.html` | Design lineages overview page |
| `templates/lineage_detail.html` | Individual design lineage detail page |
| `templates/sources.html` | Data Sources & Methodology page |

## Deployment
| File | Description |
|------|-------------|
| `fly.toml` | Fly.io deployment config (app name, region, volumes, health checks) |
| `Dockerfile` | Docker build for Fly.io (python:3.11-slim) |
| `start.sh` | Entrypoint — copies DB to persistent volume, starts gunicorn |
| `render.yaml` | Render deployment config (legacy, not primary) |
| `.dockerignore` | Docker build exclusions |

## Data Scripts
| File | Description |
|------|-------------|
| `backfill_pris_coverage.py` | Backfill generation data from IAEA PRIS |
| `build_pris_mapping.py` | Map reactor IDs to PRIS IDs |
| `fetch_missing_generation.py` | Fetch generation data for reactors with gaps |
| `status_audit.py` | Audit reactor statuses against external sources |
| `update_planned_reactors.py` | Rebuild planned_reactors table (Mar 2026 research) |
| `update_planned_mar2026_patch.py` | Patch script for planned reactor cleanup |
| `add_design_fields.py` | Populate design_series and containment_type from model names |
| `add_lineages.py` | Create design_lineages + design_series_info tables, fill design_series gaps |
| `add_descriptions.py` | Create entity_descriptions table, insert containment/status descriptions |
| `insert_country_descriptions.py` | Insert 39 country descriptions into entity_descriptions |
| `enrich_tech_lineage_descriptions.py` | Enrich technology (12) and lineage (24) descriptions in-place |
| `insert_model_descriptions.py` | Insert 154 model descriptions into entity_descriptions |
| `insert_supplier_descriptions.py` | Insert 33 supplier descriptions into entity_descriptions |
| `insert_plant_descriptions.py` | Insert 315 plant descriptions (61 manual + 254 template) |
| `insert_owner_descriptions.py` | Insert 134 owner descriptions (35 manual + 99 template) |

## Coordinate Verification Scripts
| File | Description |
|------|-------------|
| `verify_coordinates.py` | OSM Overpass API coordinate cross-validation |
| `verify_wikidata.py` | Wikidata SPARQL coordinate verification (3-source consensus) |
| `verify_names.py` | Wikidata label/alias name comparison |
| `apply_corrections.py` | Apply name + high-confidence coordinate corrections |
| `fix_chinese_data.py` | Chinese reactor data overhaul (WNA-verified coords, types, capacities) |
| `fix_final_coords.py` | Wikipedia-verified fixes for 28 plants (manual review batch) |
| `fix_remaining_coords.py` | Wikipedia-verified fixes for 8 plants dismissed as "<1km" |
| `fix_unmatched_coords.py` | Wikipedia fixes for 10 Wikidata-unmatched plants |
| `adopt_wikidata_coords.py` | Bulk adopt Wikidata coords for 74 plants >50m off |
| `scrape_wikipedia_coords.py` | Scrape Wikipedia GeoData coords via MediaWiki API for all plants |
| `manual_review_checklist.py` | Generate formatted checklist with Google Maps/Wikipedia links |

## Verification Data (generated, not committed)
| File | Description |
|------|-------------|
| `coordinate_verification.json` | OSM verification results |
| `wikidata_verification.json` | Wikidata verification results (307 matched plants) |
| `name_verification.json` | Name comparison results |
| `wikipedia_coords.json` | Wikipedia GeoData coordinate scrape results |
| `manual_review_checklist.json` | Plant review checklist with links |
| `nuclear_reactors.db.bak` | Database backup before corrections |

## Documentation
| File | Description |
|------|-------------|
| `CLAUDE.md` | AI assistant instructions and project conventions |
| `README.md` | Human-readable project overview |
| `INDEX.md` | This file — complete file listing |
| `MEMORY.md` | Working notes across sessions |
| `PLAN.md` | Project roadmap and next steps |
| `PLANNED_ADDITIONS.md` | Original backlog of planned features |
| `Nuclear_DB_Revisions.md` | User's 13-item revision list (untracked) |

## Other
| File | Description |
|------|-------------|
| `templates/SafetyFeaturesOfOperatingLightWaterReactors.pdf` | Reference PDF (summary) |
| `templates/SafetyFeaturesOfOperatingLightWaterReactors_Full.pdf` | Full 312-page reference (Gavrilas et al.) — Ch.2 has family tree diagrams per country |
| `templates/SAFETY_FEATURES_REFERENCE.md` | Notes on the reference PDF |
| `.gitignore` | Git exclusions |
