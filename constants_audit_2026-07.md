# Hardcoded-Constants Audit — 2026-07-20

Purpose: repo-wide audit of hardcoded constants claiming a source, per the reviewer
suggestion after two fabricated-constant bugs on 2026-07-06 (world-electricity dict
~15% low despite claiming "EI Statistical Review"; model-guessed KNOWN_PRIS_IDS
corrupting 24 pris_ids). Method: inventory → blast-radius triage → sampled
verification by 8 parallel research agents against primary sources.

## Inventory & Triage

| Constant / surface | Where | Feeds | Risk triage |
|---|---|---|---|
| `global_electricity_twh` | app.py ~L1667 | live share chart | **CLEAN** — Jul 6 rebase, provenance comment, EI-via-OWID retrieved 2026-07-06 |
| Design specs dicts | scripts/populate_design_specs.py + scripts/add_turbine_specs.py | `design_series_specs` (123 rows × ~20 fields, per-row `source` labels), served on reactor/model API + pages | **HIGH — sampled (agents A1–A5)**: 31 series covering ~85% of installed units, 6 checkable fields each |
| Heuristic supply-chain fields | scripts/populate_reactor_details.py (`determine_constructor/architect_engineer/turbine_supplier/rpv_manufacturer`) | `reactor_details` (741 rows), served on reactor API | **HIGH — sampled (agents B1–B2)**: 27 reactors stratified over 18 countries. These were never sourced at all — assigned by country/design pattern rules. Cooling field previously audited (Apr + Jul 6); the other 4 fields never were |
| Planned-reactor entries | update_planned_reactors.py + mar2026 patch | `planned_reactors` (123 rows) | **MEDIUM — sampled (agent C)**: 12 entries vs WNA/news |
| `SUPPLEMENTAL_OVERRIDES` | backfill_pris_coverage.py | PRIS-name→DB-name mapping | benign — identity aliases, no fabricated numbers; keys covered by pris_id_map_2026-07.json ground truth |
| CAPACITY_CHANGES | add_uprates.py | `capacity_changes` | lower — superseded/verified by Mar 26–29 net-capacity alignment audit (229/229) + PRIS/NRC/WNA cross-checks |
| SHUTDOWN_DATES, CORRECTIONS | status_audit.py | reactors status/dates | lower — re-verified by WNA audit (Mar 16) + Noah review (May 28) |
| Generation-fix dicts | fix_generation_data.py, fix_remaining_cf.py | `generation_annual` | lower — domain re-verified by validator checks 13–14 + 2025 PRIS backfill |
| Coordinate fix lists | fix_*_coords.py, fix_chinese_data.py | reactors lat/lng | lower — superseded by Wikipedia-GeoData gold-standard verification passes |
| Description dicts | insert_*/update_*_descriptions.py | entity_descriptions | out of scope — prose, different audit shape (factual-claims-in-prose audit would be its own task) |
| Templates | templates/*.html | UI | clean — labels only, no data constants |

## Sampled Verification (agents dispatched 2026-07-20)

- A1 VVER/RBMK · A2 US PWR · A3 EU/Asia PWR · A4 BWR · A5 GCR/HWR/China — `design_series_specs`, 6 fields/series
- B1/B2 — `reactor_details` constructor/AE/turbine/RPV, 27 reactors
- C — `planned_reactors`, 12 entries

All 8 reported DONE 2026-07-20. Orchestrator spot-checked the load-bearing WRONG
verdicts against own domain knowledge before accepting (CP1 palier 2785, UK/Soviet
full-speed turbines, LaSalle 3323, Isar-1 592 FA, Akkuyu Arabelle, Ringhals
Stal-Laval — all consistent).

## Findings

### F1 — design_series_specs: systematic turbine-speed error class (CONFIRMED)
`turbine_speed_rpm = 1500` written for families whose real machines are full-speed
3000 rpm. Confirmed WRONG with sources: VVER-1000/320 (K-1000-60/3000),
VVER-440/213, VVER-440/230, VVER-1200/491 (K-1200-6.8/50 domestic fleet),
RBMK-1000 (K-500-65/3000), Magnox (Calder Hall 3000 rpm), AGR (Sizewell-B-vs-AGR
comparison sources). Mechanism: script treated "1500 rpm" as the generic 50 Hz
nuclear default — true for French/German/wet-steam PWR half-speed machines, false
for Soviet and UK gas-cooled full-speed designs. US 1800 rpm values all confirmed
correct. UNGG unverified, same risk class. ABWR "1500" is region-specific
(50 Hz Japan) not universal — caveat, not error.

### F2 — design_series_specs: scattered wrong values + copy-paste rows (CONFIRMED)
- CP1 thermal 2660 → **2785** MWth (2660 is the CP0 figure; PRIS unit pages + palier docs). CP2 (same CPY palier, also shows 2660) implicated — verify at repair.
- Siemens 4-Loop thermal 3690 → **3765** (Konvoi design; no source matches 3690).
- IPHWR(-220) thermal 693 → **754.5** (IAEA ARIS SR-74); operating pressure 95 → ~85 bar (contested, 87 kg/cm²g).
- HPR1000 thermal 3150 vs official design paper **3050** (contested).
- BWR/5 row byte-identical to BWR/4; real BWR/5 (LaSalle) = **3323** MWth.
- BWR-69 franken-row: Isar-1 thermal (2575) + Krümmel fuel count (840; Isar-1 has 592). No real plant has both.
- BWR/3 thermal 2381 matches no actual BWR/3 unit (Dresden 2527, Millstone 2011, Monticello 1775).
- AGR thermal 1623 contested (Heysham 2 sources say ~1500).
- Magnox: single series values (1180 MWth, 3800 elements, 20 bar) may be unrepresentable — stations ranged ~200–1875 MWth.
- Everything else sampled (loops, SGs, FA counts, pressures, US/FR/KR/CN structure) CONFIRMED genuine — incl. all 36 US PWR values, EPR, APR1400, CANDU 6, AGR steam cycle (41/160 bar), RBMK, VVER structure.

### F3 — reactor_details: heuristic fields ~15–20% wrong where checkable (CONFIRMED)
~10 confirmed errors in ~108 field-checks across 27 reactors; many more UNVERIFIABLE.
Systematic sub-bugs:
- **RDM-default**: "Rotterdam Dockyard" assigned as RPV maker to every KWU-design plant. Isar 2 + Angra 2 actually Gutehoffnungshütte (GHH); Ringhals 3 actually Uddcomb (Stal-Laval turbine, not Westinghouse).
- **Licensor-as-constructor**: AECL listed as Bruce constructor (actually Ontario Hydro); CNNC listed for Lufeng (a CGN site).
- **Vendor-as-turbine/RPV**: Vogtle 3 turbine "Westinghouse" (actually Toshiba); Akkuyu turbine "Skoda" (actually GE Arabelle via AAEM); Browns Ferry 1 / STP 1 RPV "Combustion Engineering" (agent cites GE Power / Westinghouse via power-technology.com — MEDIUM confidence, that source blurs vendor-vs-forge; re-verify at repair).
- Stale corporate names: "Creusot-Loire" for 1990s+ French builds (Framatome/Creusot Forge).
RPV manufacturer is the least trustworthy field; constructor/AE mostly right.

### F4 — planned_reactors: 4 wrong + 2 stale of 12 sampled (CONFIRMED)
- **Duwayhin (Saudi)**: fabricated — claims APR1400 / construction Q1 2026 / High; WNA says no vendor selected, no construction date. Worst case in sample.
- Taishan 4: 1200 MWe (WNN), not 1150. Doicesti: 462 MW total (6×77), not 420. Novocherkassk: "VVER-optimum" (WNN), not VVER-TOI.
- Stale: Almaty (CNNC reported awarded; res. dated Jan 26 2026), Kalpakkam FBR-600 (overstated certainty).
- Confirmed current: Wylfa RR-SMR, Doicesti FID timing, Taishan approval, Metsamor direction.

### F5 — clean surfaces
app.py electricity dict (Jul 6 rebase), templates, SUPPLEMENTAL_OVERRIDES aliases,
capacity/status/generation/coordinate constants (all superseded by dedicated audits).

## Repairs

(pending Griffin's scope decision — options in session discussion 2026-07-20)
