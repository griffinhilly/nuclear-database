# Migration 019 Review — Design-Spec Completion Pass (2026-07-22)

Ground truth: `spec_final_verdicts.psv` (1,987 verdicts from 10 re-run batches, all
retrieval-sourced; taint gate in `merge_specs.py` passed). Re-run backlog:
`spec_rerun_manifest.psv` (367 BLOCKED rows, quota-starved, values untouched).

## Verdict totals
| Verdict | Count | Action |
|---|---|---|
| CONFIRMED (HIGH/MED) | 724 | keep visible |
| WRONG | 72 | tiered below |
| UNVERIFIABLE + CONFIRMED/LOW | 824 | NULL (zero-doubt) |
| BLOCKED | 367 | no change; re-run next quota window |

## Tier R — REJECT, do not apply (7 rows)
- **ATR × 6** (thermal 250, moderator light-water/Be, pressure 26.9, enrichment ~93% HEU,
  40 assemblies, outlet 71°C): entity collision. Sources describe the **US Advanced Test
  Reactor (Idaho test reactor)**; our `ATR` series is **Fugen** (Japan Advanced Thermal
  Reactor, Tsuruga — see migration 017 comment). DB values match Fugen. No change.
- **MHI 2-Loop thermal 1570→1650**: agent's own flag — the series spans Mihama-1,
  Tomari-1, Genkai-1/2, Ikata-1/2 with genuinely different ratings. Neither 1570 nor
  1650 is honest for the series. **Proposed instead: NULL (mixed-within-series)**, same
  treatment migration 017 gave CANDU turbine speed.

## Tier A — HIGH-confidence corrections, apply (19 rows)
Primary/authoritative sources (NRC USAR, IAEA PRIS pages, MDEP report, Paks plant docs,
PNNL profile). Includes two reversals of the Jul 20 sweep:
- **SNUPPS turbine 3000→1800** (Wolf Creek USAR; 017 misfiled SNUPPS in the Soviet list)
- **VVER-1000/320 turbine 3000→1500 + LP sections 4→3** (MDEP TR-VVERWG-06 App.1: V-320
  fleet uses the half-speed K-1000-60/1500 turbine)
Rest: OPR-1000 thermal 2825 + LP 3, CNP-1000 thermal 2905, VVER-440 family primary-circuit
set (123 bar / 297 / 266 / 37 rods for V-213 & V-230), PHWR-700 37-element bundle,
KS 150 natural-metal fuel, OCR organic-terphenyl moderator, SGHWR 318 MWt, Saxton 23.5 MWt.

## Tier B — MED-confidence corrections, apply per plan (46 rows)
Secondary sources (Wikipedia spec tables, fr.wikipedia paliers, NS Energy/Modern Power,
GEM). Zero-doubt logic: a sourced correction beats a value that was never verified at
all. Notable: P4 core height 3.66→4.27 m (900 MWe value on the 1300 MWe series), CP2
control elements 48→57, VVER-210/365 prototype fixes, BREST-OD-300 MNUP fuel,
KLT-40S enrichment 14.1, ACP100 385 MWt. Sub-1% rounding-class deltas (CNP-300 999,
PLWBR 236, live-steam decimals) included — small but sourced.
- Watch-item within tier: **EL-4 enrichment → "Natural"** conflicts with some accounts
  of slightly-enriched EL-4 fuel; MED source (GEM/Wikipedia). Applied per rule, listed
  for Noah/Dirk round-2 glance.

## NULL pass (824 rows + 1 mixed-series)
UNVERIFIABLE after real search (mostly granular thermal-hydraulic/turbine fields and
thinly-documented prototypes/internal aggregation series: Siemens loops, BWR/G1-G3,
Pre-Konvoi). ~41% of the checked values. Originals remain recoverable from git history
and `spec_final_verdicts.psv` retains every verdict + source.

## Deferred
- 367 BLOCKED rows re-run (manifest ready) → then drift-guard check 15 extension to
  design_series_specs (guard must wait until the table's whitelist is complete).
- BWR/G1-G3 + Siemens-loop + Pre-Konvoi series names: DB-internal taxonomy confirmed
  found in no external source — flag to Griffin whether to keep/rename (display issue,
  not a data error).
