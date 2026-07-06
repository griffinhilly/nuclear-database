# PRIS id repair — July 2026 (migration 015)

**One-line purpose:** 24 reactors had wrong or missing `reactors.pris_id` values; 13 of them
duplicated another reactor's id, which made pris_id-keyed generation backfills (incl.
migration 013) write the id-owner's output onto them. Migration 015 fixes every id and
repairs the contaminated generation rows.

**How it was found:** a spec-blind reviewer of migration 013 spotted 2025 generation on
permanently-shutdown reactors at up to 238% capacity factor. Root cause was NOT the backfill
logic itself but pre-existing duplicate pris_ids. A full PRIS id-space scan (ids 1–1150,
name read from each page's `lblReactorName`) then exposed the wider class, including
wrong-but-unclaimed ids that corrupt nothing today but silently mis-fetch forever.

**Ground truth artifact:** `pris_id_map_2026-07.json` (id → PRIS reactor name for ids 1–1150,
721 named). Use it to validate any future pris_id assignment. Validator check 12 makes
duplicate ids a hard failure; checks 13 (generation after shutdown) and 14 (CF >105% vs
historical gross — mirrors the public `/api/data/validation` anomaly query) trip on the
damage this class causes.

## Id corrections (migration 015)

| Reactor | Old pris_id | Old id actually was | New pris_id (PRIS name) |
|---|---|---|---|
| Pickering 1 | 75 | TEMELIN-2 | 49 (PICKERING-1) |
| Wolsong 1 | 487 | SMOLENSK-2 | 407 (WOLSONG-1) |
| Kursk 1-1 | 495 | KALININ-3 | 476 (KURSK-1) |
| Kursk 1-2 | 496 | KALININ-4 | 485 (KURSK-2) |
| Dungeness B 1 | 690 | MCGUIRE-1 | 248 (DUNGENESS B-1) |
| Dungeness B 2 | 691 | MCGUIRE-2 | 249 (DUNGENESS B-2) |
| Hinkley Point B 1 | 698 | ST. LUCIE-2 | 244 (HINKLEY POINT B-1) |
| Hinkley Point B 2 | 699 | WATTS BAR-1 | 245 (HINKLEY POINT B-2) |
| Hunterston B 1 | 700 | WATTS BAR-2 | 246 (HUNTERSTON B-1) |
| Hunterston B 2 | 701 | SUMMER-1 | 247 (HUNTERSTON B-2) |
| Shin-Kori 3 | 838 | TIANWAN-1 | 885 (SAEUL-1 — PRIS renamed) |
| Shin-Kori 4 | 839 | TIANWAN-2 | 886 (SAEUL-2 — PRIS renamed) |
| Shidaowan Guohe One 1 | 957 | SHIDAO BAY-1 | NULL (no PRIS page exists) |
| Kori 1 | 471 | (dead id) | 394 (KORI-1) |
| Leningrad 1-1 | 499 | NOVOVORONEZH-1 | 474 (LENINGRAD-1) |
| Leningrad 1-2 | 500 | (dead id) | 475 (LENINGRAD-2) |
| Pickering 4 | 76 | (dead id) | 52 (PICKERING-4) |
| Novovoronezh 1-3 | 509 | (dead id) | 519 (NOVOVORONEZH-3) |
| Novovoronezh 1-1 | NULL | — | 499 (NOVOVORONEZH-1) |
| Novovoronezh 1-2 | NULL | — | 513 (NOVOVORONEZH-2) |
| Pickering 2 | NULL | — | 50 (PICKERING-2) |
| Pickering 3 | NULL | — | 51 (PICKERING-3) |
| Leningrad 2-3 | NULL | — | 902 (LENINGRAD 2-3) |
| Leningrad 2-4 | NULL | — | 970 (LENINGRAD 2-4) |

## Generation repairs

Contaminated rows = loser's row with a value byte-identical to the id-owner's row in the same
year (2-decimal GWh coincidence is impossible; identity ⇒ copy). Each was corrected from the
reactor's TRUE PRIS page, or deleted where PRIS carries no positive value for that year
(pre-operation years, post-shutdown years, outage years). The 2024/2025 backfill was then
re-applied correctly. Post-repair samples verified equal to live PRIS values (Pickering 1
2024 = 3333.23; Kursk 1-1 2021 = 5656.38; Shin-Kori 3 2025 = 10358.26; Shin-Kori 4
2024 = 10557.79).

- Deleted: 10 bogus 2025 rows + 9 bogus 2024 rows (shutdown reactors + Shidaowan Guohe One),
  plus older contamination: Shin-Kori 3 pre-2016 rows (10, were Tianwan 1's), Shin-Kori 4
  pre-2019 rows (12, were Tianwan 2's), Dungeness B 1 1981–83 (McGuire 1's), Wolsong 1
  2013/2019 (Smolensk 2's — Wolsong 1 was offline both years), Pickering 1 2002 (Temelin 2's;
  Pickering 1 was laid up 1997–2003).
- Corrected in place: Kursk 1-1 2021; Pickering 1 2024; Shin-Kori 3 2022–2025; Shin-Kori 4
  2022–2025 (all now true PRIS values).
- Leningrad 1-1 (held NOVOVORONEZH-1's id): history verified UNCONTAMINATED — its rows are
  RBMK-scale and start exactly at its own 1973 grid connection. Id fixed; no rows touched.
- Fleet totals after repair: 2025 = 2622.8 TWh (389 rows), 2024 = 2426.2 TWh (396 rows).
  Public `/api/data/validation` CF-anomaly count: 0 (was 16 mid-corruption).

## All-mapping audit (432 mapped reactors)

50 flags from the loose name-match: the 13 duplicates and 5 wrong-unique ids above (fixed),
plus 32 benign name-noise cases (transliteration/aliases: GOESGEN, KRSKO, ZAPORIZHZHYA,
CHASNUPP=Chashma, KANUPP=Karachi, ANO=Arkansas Nuclear One, plant-vs-unit "1" suffixes).
Full list: `pris_mapping_audit.txt` alongside the map JSON.

## Left for the backlog (pre-existing, surfaced by the new checks during development)

1. **Capacity-history gaps** (flagged when check 14 briefly ran against historical NET):
   Wolsong 3/4 (many years at 110–122% vs 569/595 MW net — CANDU-6 net is ~650–680; their
   `capacity_changes`/net values look wrong), Hunterston B 1 1990s (~610 MW era before the
   ~490 MW boiler derate — derate history missing), Hinkley Point B 2 1994, Bruce 2 2024
   (missing MCR uprate record). Capacity-side debt, not generation corruption.
2. **General NULL pris_id sweep**: only the affected families were filled; other reactors
   with NULL pris_id (mostly UC/prototypes) could be mapped from `pris_id_map_2026-07.json`.
3. **Shidaowan Guohe One 1** has no PRIS page; its generation (if/when reported) needs a
   non-PRIS source (WNA/CNNC).
4. **Dungeness B 1/2 2020–21**: PRIS shows small NEGATIVE values (house-load during
   defueling); DB keeps its older positive rows (not contamination — left as-is; convention
   stores no ≤0 rows).
5. **Newly-mapped shutdown reactors** (Kori 1, Pickering 1–4, Leningrad 1-1/1-2,
   Novovoronezh 1-1/1-2/1-3): their PRIS pages carry full histories that could enrich/verify
   DB rows in a future alignment pass.
