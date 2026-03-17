# Nuclear Database — Data Quality Lessons

## Coordinate Verification

- **Wikipedia is the coordinate gold standard**: Every manual spot-check confirmed Wikipedia infobox coords are accurate (pointing to the actual reactor building). Discrepancies under 1km were NOT "different reference points" — they were genuine errors (Stade was in a river). OSM was wrong for Berkeley. Google Maps was wrong for Shidao Bay. WNA is best for reactor specs but doesn't have coordinates.
- **Coordinate precision is a quality signal**: Operational plants have 4+ decimal places (PRIS-verified). Round coordinates (≤2 decimals) = approximated, needs verification.
- **Coordinate verification complete**: Wikipedia GeoData coordinates adopted as gold standard for all plants. Final sweep via MediaWiki API `prop=coordinates` updated 100 more plants. ~15 plants unmatched by automated tools (bad name matches); coords already verified manually or via earlier batches.
- **Multi-site complexes** (Kursk 1/2, Leningrad 1/2, Novovoronezh 1/2, Hanul/Shin-Hanul) have per-site coordinates — user may consolidate these as single plants (Madi to decide — unresolved as of Mar 14).

## Chinese Data Caveats

- **Chinese UC data is highest-risk**: PRIS has delays, coordinates are often city-center approximations (≤2 decimal places), multi-phase naming creates confusion. WNA reactor database is more reliable for Chinese plants.
- Chinese plant naming is complex: same site can have different `plant_name` entries for different reactor phases (Shidao Bay vs Shidaowan, Qinshan 1/2/3).
- A full overhaul was done Mar 12 — see `guides/session-log.md` for details.

## General Data Notes

- Global electricity data in `app.py` is a hardcoded dict (1970-2024) from EI Statistical Review.
- Reactor `name` column doesn't exist — use `plant_name` + `unit_number`.
- Generation data post-2020 is incomplete: only ~112 of ~430 operational reactors report for 2022-2024. Coverage adjustment: scale raw sum by `(operational_reactors / reporting_reactors)`.
