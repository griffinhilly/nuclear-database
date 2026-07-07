# PLAN.md Current State — archive (swept 2026-07-06 wrapup, newest first)

Bullets swept from `PLAN.md ## Current State` per prune-on-wrap. Nothing here is needed
to resume work; it is preserved for provenance.

## Jul 6, 2026 (session 2) — backlog sweep detail (headline retained in PLAN.md)

- **011**: Novovoronezh-5 = prototype VVER-1000 (V-187), series renamed VVER-440/187→VVER-1000/187, predecessor chain rewired, specs + model description corrected (committed `96a421d`).
- **012 (cooling audit)**: 40 per-unit fixes across the US fleet + Scope-C fills; Fermi 2/Perry/Davis-Besse now show their natural-draft towers; Braidwood/Clinton/South Texas/Wolf Creek/Comanche Peak → cooling pond; Catawba → mechanical draft; Tarapur tower hypothesis REFUTED (stays seawater). Ledger: `cooling_audit_2026-07.md`. Validator checks 9–11 added.
- **013 (2025 PRIS backfill)**: 2025 coverage 93.3% of operational fleet; 2024 gaps filled. **Spec-blind review caught a blocker**: 13 reactors carried duplicate (wrong) pris_ids → pair-partner's output written onto them (238% CFs on shutdown reactors, ~100 TWh double-counted).
- **015 (pris_id repair)**: full PRIS id-space scan (1–1150) → 24 pris_id fixes (13 dup losers, 5 wrong-unique, 6 NULL fills), contaminated generation repaired from true PRIS pages (incl. pre-existing Shin-Kori 3/4 contamination back to 2006). Ledger: `pris_id_repair_2026-07.md`; ground truth: `pris_id_map_2026-07.json`. Validator checks 12–14 added. Post-repair: validator = 54 baseline exactly, public CF-anomaly endpoint = 0.
- **014 (descriptions)**: all 16 missing model + 4 missing plant descriptions written (individually researched); V-187 spec control-elements filled (109). Zero missing descriptions remain.
- **World-electricity rebase (commit 5d4bb64)**: old hardcoded denominator claimed EI sourcing but ran 7–15% low (latent-space artifact, same class as the pris_ids). Replaced with real EI series via OWID, 1985–2025; pre-1985 stub dropped rather than spliced. Share chart now 8.8% for 2024 (was 10.3%). Sources page citation updated.
- Bonus: `/api/data/validation` had returned HTTP 500 in production since March (query vs nonexistent `owners` table) — fixed (6be0cc6). Origin of wrong pris_ids established by git archaeology and recorded in the ledger (b99c8bf).

## Jul 6, 2026 (session 1) — /start reconciliation

Migration 010 CONFIRMED SHIPPED: committed `b1ae92f` Jun 4 11:29, merged to `main`, pushed, deployed — live-verified via API (Tianwan 5 = ACPR-1000). The stale "NOT yet committed / deployed" note arose because the Jun 4 COMP-update commit (1e7ea2d, 11:10) froze that language before the data commit landed at 11:29.

## Jun 4, 2026

**Noah override reversals applied (migration 010).** All 3 May-28 overrides reversed after Noah supplied sources and held his ground; every Noah correction is now accepted. Validator clean.

## May 28-29, 2026 — Noah review

**Noah review SHIPPED.** Committed (058a304), pushed, deployed to Fly.io (3 machines, health-checked). Live site verified: 738 reactors / 223 Shutdown / 76 UC / 417 operational. Confirmed merged to `main` Jun 4.

- ~45 external corrections from Noah, verified by 6 parallel research agents (PRIS/WNA), applied via migrations 002-008, a code-side "Permanent Shutdown"->"Shutdown" rename (app.py/database.py/12 templates), and 3 new `validate_db.py` checks. Ledger: `noah_review.md`. Validator: all hard-FAIL checks pass; 54 remaining = pre-existing WARN backlog (capacity-rounding + net/coord nulls).
- Committed in 058a304 (May 29): 8 migration files, app.py + database.py + 12 templates, validate_db.py, scripts/rename_status_shutdown.py, noah_review.md, COMP updates. DB backed up to `nuclear_reactors.db.bak-noah-20260528`.
- **Migration 009** (spec-blind review fixes): Khmelnytskyi notes de-contradicted; Darlington SMR construction_start -> first-concrete (2026-05); VVER-1200/510 year fixed; orphan artifact models W?/V-120 dropped; entity_descriptions synced (renamed Sellafield->Calder Hall, Shidaowan->Shidaowan Guohe One, MONTS-D'ARREE->EL-4, W?->WH 2-loop, CANDU casing; deleted artifacts).
- **Never-operated audit COMPLETE (D2)**: only 3 such reactors in the DB (Lungmen 1/2, Baltic-1), all moved to planned/Cancelled. Zwentendorf/Bataan/Kalkar/WNP/Bellefonte are not in this DB's reactor set. Audit done, not deferred.
- Follow-ups all since resolved: Noah suffix sources (Jun 4, migration 010); manual descriptions (Jul 6, migration 014); Novovoronezh-1 U5 series (Jul 6, migration 011); cooling audit + 2025 backfill (Jul 6, migrations 012/013/015).
