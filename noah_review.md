# Noah Review — Data Corrections (2026-05-28)

Source: Noah's edit list. Default posture (Griffin): **assume Noah correct unless overwhelming contra-evidence.**
Workflow: verify → fix via migration → root-cause → operationalize.

Confidence key: **HIGH** = DB internal evidence or well-known fact confirms; **VERIFY** = default Noah, want one external source; **DECISION** = taxonomy/modeling choice for Griffin.

Tech/model storage: `reactors.technology_id`→`technologies.code`, `reactors.model_id`→`models.name`, `reactors.design_series` (text), `reactors.containment_type` (text). Planned units in `planned_reactors`.

---

## A. Model-code corrections — HIGH confidence (internal evidence supports)

| # | Entity | Current | Noah → | Evidence |
|---|--------|---------|--------|----------|
| A1 | Kola 3/4 | all 4 = VVER V-230 / VVER-440/230 | 3/4 = **V-213** (VVER-440/213) | Kola 1/2 = V-230, 3/4 = later V-213 generation. DB wrongly homogenized. |
| A2 | Novovoronezh-1 (U1) | VVER V-120 / VVER-365 | **VVER-210 / V-1** | First VVER ever; DB has U1&U2 both V-120/VVER-365 — historically wrong. |
| A3 | Novovoronezh-2 (U2) | VVER V-120 / VVER-365 | **VVER-365 / V-3M** | Per-unit lineage: U1=210, U2=365, U3/4=440, U5=1000. |
| A4 | Kursk 2-1, 2-2 | VVER V-491 / VVER-1200/491 | **V-510K** | Kursk II = lead VVER-TOI (V-510K), NOT V-491 (that's Leningrad II). Clear mislabel. |
| A5 | Leningrad II-3/4 | generic VVER-1200 | **V-491** | Units 1/2 already V-491; 3/4 just generic. Consistency. |
| A6 | Akkuyu 3/4 | generic VVER-1200 | **V-509** | Units 1/2 already V-509; 3/4 generic. Consistency. |
| A7 | Kori-1 | model = `W?` (literal artifact) | **WH 2-loop** | `W?` is a data artifact; series already "W 2-Loop". |
| A8 | Vandellos-1 | GCR / Magnox / model=None | **UNGG** | French UNGG (gas-graphite) built in Spain — NOT Magnox (British). |
| A9 | "25" model artifact | GE Vallecitos & Saxton: model = `25` | real types (BWR/PWR prototype) | PRIS numeric type-code leaked as model name. See root-cause R2. |
| A10 | Canadian CANDU caps | `CANDU 500A` vs `500a/500b`, `750a/750b` | unify casing | Mixed case in `models`/`design_series`. |
| A11 | BREST | series only "BREST-OD-300", reactor name "BREST" | name **BREST-OD-300** | Full designation. |

## A-ext. VVER export codes — HIGH-ish (well-documented, light verify)

| # | Entity | Current | Noah → |
|---|--------|---------|--------|
| A12 | Paks 5/6 | generic VVER-1200 | **V-527** |
| A13 | El Dabaa 1-4 | generic VVER-1200 | **V-529** |
| A14 | Bushehr 2/3 | VVER V-446 | **V-528** (+ unit 3 missing → see D1) |
| A15 | Xudabao 3/4 | generic VVER-1200 | **V-491S** |

---

## B. Naming-convention fixes (root-cause R1: auto-numbering)

| # | Entity | Current | Noah → | Note |
|---|--------|---------|--------|------|
| B1 | Biblis 1/2 | Biblis U1, U2 | **Biblis A, Biblis B** | German fleet uses letters. |
| B2 | Gundremmingen 1/2/3 | U1, U2, U3 | **Gundremmingen A, B, C** | |
| B3 | Sellafield 1-4 | Sellafield U1-4 | **Calder Hall 1-4** | Plant=Calder Hall, site=Sellafield. |
| B4 | Sellafield-5 | Sellafield U5 (AGR) | **Windscale AGR** (WAGR) | Prototype AGR, distinct plant. |
| B5 | Brennilis-1 | model = MONTS-D'ARREE | model/type **EL-4** | Plant renamed to Brennilis (Mar 2026); reactor design = EL-4. |
| B6 | Xiasu 1-4 (planned) | "Xiasu" | **Xiapu** | Romanization typo (Xiapu County, Fujian). |

---

## C. Need external verification (default Noah; want 1 authoritative source)

| # | Entity | Current | Noah → | Why flagged |
|---|--------|---------|--------|-------------|
| C1 | Madras-1 | Operational | **Suspended** | Mild contra — want to confirm extended-outage/suspended status. |
| C2 | CEFR | Suspended | **Operational** (experimental, not commercial) | Status + note that it's experimental. |
| C3 | Khmelnytskyi 3/4 | Suspended | **Under Construction** | Confirm construction resumed; model (V-392B?) may also need review. |
| C4 | Ling'ao 1/2 | M310 | **M310+** | |
| C5 | Fuqing 1-4 | CNP-1000 | **M310+** (same as Ling'ao 1/2) | Contra: often cited CNP-1000. Taxonomy fuzz. |
| C6 | Yangjiang 3/4 | CPR-1000 | **CPR-1000+** | Contra: 1-4 usually all CPR-1000. |
| C7 | Tianwan 7/8 | generic VVER-1200 | **V-491T** | |
| C8 | Kudankulam 3/4 | VVER V-412 | **V-412M** | |
| C9 | Kudankulam 5/6 | model=None / VVER-1000/412 | **V-412T** | |
| C10 | Mochovce 3/4 | VVER V-213 | **V-213+** | |
| C11 | Millstone-1 | model=None / BWR/3 | **BWR-3 + Mark I containment** | |
| C12 | Tarapur 1/2 | containment = Mark II | **Mark I** | Early BWR-1; plausible. |
| C13 | Bailong-1 | model=HPR1000 / series=CAP1000 (mismatch) | **CAP1000** | Identify what "Bailong" site is. |
| C14 | Lianjiang 3/4 (planned) | CAP1000, 1250/1170 | **CAP1400, 1530 MW** | |

---

## D. Genuine decisions (Griffin) — DECIDED 2026-05-28

| # | Item | Decision |
|---|------|----------|
| D1 | Missing units now under construction | Bushehr-3 (planned, V-528), Kursk 2-3 (planned, VVER-TOI), Darlington SMR-1 (planned has only U2-4). **Verify construction-start, then move planned→reactors as Under Construction** (project rule: first concrete = UC). |
| D2 | Lungmen (Fourth) 1/2 + cancelled-construction class | **DECIDED:** group cancelled-but-never-operated units under **Planned**, mark cancellation via online-date field = text `"Cancelled"` (not a year). Move Lungmen 1/2 from `reactors`→`planned_reactors`. **Audit fleet for other never-operated units mislabeled "(Permanent) Shutdown"** (Zwentendorf, Bataan, Kalkar/SNR-300, WNP, Bellefonte, etc.). |
| D3 | Shidaowan naming | **DECIDED (lean Noah):** CAP1400 units → **SN-1/SN-2** (State Nuclear). Research the HPR1000 units (U3/4 → "Shidaowan 1-1/1-2") + the separate "Shidao Bay" HTR-PM row, then confirm. |
| D4 | Palisades SMR → Pioneer | Research Holtec branding; default **Pioneer-1, Pioneer-2**. |
| D5 | Ukraine AP1000 Program U7-13 | Research the actual project; **offer remodel options** (one aggregate row → individual units? drop? annotate?). |
| D6 | Planned-units modeling | Research/audit `planned_reactors` structure; **offer cleanup options**. |
| **D7** | **Status rename: "Permanent Shutdown" → "Shutdown"** | **DECIDED (NEW, Noah + REG editorial):** rename fleet-wide. Rationale: REG argues German/Belgian units should be refurbished & restarted — "Permanent" contradicts that position. Scope: 226 `reactors.status` rows + `app.py` (filters, labels, status page, map color logic) + templates + `validate_db.py` enum + status `entity_descriptions`. "Suspended" stays as the shorter-term-offline category. |

---

## E. Root causes → operationalize

- **R1 — Auto-numbering units.** Build/populate scripts assigned numeric `unit_number` universally, even where real plants use letters (Biblis A/B, Gundremmingen A/B/C) or where site≠plant (Calder Hall units on the Sellafield site). Noah's general note: "Adding automatic numbers makes no sense, since many units use no numbers at all."
  - Fix: preserve source (PRIS/WNA) unit designations; don't synthesize numbers.
  - Operationalize: `validate_db.py` check flagging plants whose unit labels don't match source convention; audit full fleet for other auto-numbered letter-plants.
- **R2 — PRIS type-code leak ("25").** Scraper mapped PRIS reactor-type numeric code into `models.name` for prototypes (Vallecitos, Saxton). Noah: "for some small US-prototypes, the reactor type is described as '25', which is the number of PRIS to define prototypes."
  - Fix: PRIS type-code → human-readable mapping; correct the 2 affected.
  - Operationalize: `validate_db.py` check flagging numeric-only / suspiciously-short model names.
- **R3 — VVER V-code granularity.** Many edits collapse to: DB stored generic series (VVER-1200) or a wrong V-code, instead of the precise per-unit V-xxx. Bulk model assignment by series, not per-unit design.
  - Operationalize: per-unit VVER V-code reference; validate_db check that VVER reactors carry a specific V-code, not just series.

---

---

# VERDICTS — research complete (2026-05-28, 6 parallel research agents vs PRIS/WNA/Wikipedia)

## ✅ READY TO APPLY — Noah confirmed or clear improvement (asymmetric bar satisfied)

**Status:**
- Madras-1 → **Suspended** (PRIS: "Suspended Operation" since 2018-01-30, zero generation since). CONFIRM.
- CEFR → **Operational** (experimental, not commercial; reached full power 2014, tests through 2021). CONFIRM.
- Khmelnytskyi 3/4 → **Under Construction** (WNA classification; Rada legislation Feb 2025). CONFIRM. **+ BONUS model fix:** current "VVER-1200/V-392B" is WRONG (V-392B = Novovoronezh-II/Leningrad-II). Correct = **VVER-1000** (orig. V-320). → set model VVER-1000, series VVER-1000/320, note Belene/AP1000 uncertainty.

**VVER model codes — documented, apply:**
- Kola 3/4 → **V-213** (1/2 stay V-230). Kursk 2-1/2 → **V-510K** (VVER-TOI; PRIS shows V-510). Leningrad-II 3/4 → **V-491**. Akkuyu 3/4 → **V-509**. Paks 5/6 → **V-527** (WNA explicit). El Dabaa 1-4 → **V-529**. Bushehr 2/3 → **V-528** (PRIS direct). Mochovce 3/4 → **V-213+** (Wikipedia VVER table). Novovoronezh-1 (U1) → **VVER-210/V-1**; Novovoronezh-2 (U2) → **VVER-365/V-3M** (PRIS).

**Other model/type:**
- Kori-1 → **WH 2-loop** (kill `W?` artifact). Vandellos-1 → **UNGG** (not Magnox). Brennilis model → **EL-4** (kill MONTS-D'ARREE). Millstone-1 → model **BWR-3** + containment **Mark I**. "25" artifact (Vallecitos, Saxton) → real types (R2). Canadian CANDU casing → unify (500a/b→500A/B etc.). BREST → **BREST-OD-300**.
- Fuqing 1-4 → **M310+** (WNA: CNNC M310+ family; not CNP-1000). CONFIRM. Yangjiang 3/4 → **CPR-1000+** (1/2=CPR-1000, 5/6=ACPR-1000). CONFIRM. Bailong-1 → **CAP1000** (new Guangxi site, first concrete Dec 2025; kills HPR1000/CAP1000 mismatch). CONFIRM.

**Naming (root cause R1):**
- Biblis 1/2 → **Biblis A / Biblis B**. Gundremmingen 1/2/3 → **A / B / C**. Sellafield 1-4 → **Calder Hall 1-4**. Sellafield-5 → **Windscale AGR**. Xiasu → **Xiapu** (CONFIRM). Palisades SMR → **Pioneer 1 / Pioneer 2** (Holtec official "Palisades Pioneer 1 & 2"; CONFIRM).

**Containment:**
- Tarapur 1/2: current "Mark II" is WRONG. Noah's "Mark I" is closer; most-precise term = **"Pre-Mark I"** (NPCIL/AERB: BWR-1 suppression-pool design predating formal Mark nomenclature). → DECISION Q3.

**Missing UC units (construction-date verified):**
- **Kursk 2-3** → MOVE planned→reactors as **Under Construction** (PRIS: UC, start 2026-01-31, ID 1009). Model V-510K/VVER-TOI.
- **Darlington SMR-1** → ADD as **Under Construction** (CNSC licence Apr 2025, basemat May 2026; first G7 SMR). Model BWRX-300. *(Not in planned table at all — fully missing, Noah right.)*
- **Bushehr-3** → STAYS planned. First concrete NOT yet poured (pre-construction per WNA Feb 2026). Per project rule (first-concrete=UC) it remains planned. Fix model → V-528. *(So "unit 3 missing" = it's in planned, not absent.)*

**Cancelled-construction class (D2):**
- Lungmen (Fourth) 1/2 + **Baltic-1** → move `reactors`→`planned`, status grouped as Planned, `expected_online`="Cancelled". All three never operated. CONFIRM.

**Status rename (D7):** "Permanent Shutdown" → **"Shutdown"** fleet-wide (226 rows + app.py + templates + validator + status description).

## ⛔ OVERRIDE NOAH — overwhelming authoritative evidence to the contrary

- **Ling'ao 1/2: keep M310** (NOT M310+). IAEA PRIS lists both as M310; M310+ is the CNNC label for Fuqing/Fangjiashan/Tianwan-5/6, not the CGN Ling'ao units. *(Noah's Fuqing→M310+ is right; his premise that Ling'ao 1/2 are also M310+ is inverted.)*
- **Lianjiang 3/4: keep CAP1000 (~1160 MW)** (NOT CAP1400/1530 MW). All sources: all 6 Lianjiang units are CAP1000. Noah appears to have conflated with Shidaowan (CAP1400).
- **Kudankulam 3/4: keep V-412** (NOT V-412M). PRIS/WNA list all 6 KK units identically as V-412. *(DB already V-412 → no change.)*

## ✔️ DECISIONS RESOLVED (Griffin, 2026-05-28)
- **Q1 Shidaowan → Guohe One (official).** CAP1400 units (DB "Shidaowan U1/U2") → **"Shidaowan Guohe One" U1/U2**; HPR1000 units (DB "Shidaowan U3/U4") → **"Shidaowan" U1/U2** (PRIS). NOT SN-1/SN-2.
- **Q2 VVER suffixes → base code + ask Noah.** Apply **V-491** (Xudabao 3/4, Tianwan 7/8) and **V-412** (Kudankulam 5/6, currently NULL); do NOT add S/T/M suffixes. **TODO: ask Noah for his source on V-491S / V-491T / V-412T.**
- **Q3 Tarapur containment → "Pre-Mark I".**
- **Q4 Planned remodel → Minimal.** Rename+annotate the Ukraine "U7-13" row; leave Doicesti/Wloclawek aggregates as-is.

## ❓ (resolved — see above)

- **Q1 — Shidaowan naming.** Noah: CAP1400 units→SN-1/SN-2, HPR1000 units→"Shidaowan 1-1/1-2". Research: **ZERO source support for SN-1/SN-2**; official CAP1400 brand = **"Guohe One" (国和一号)** → WNA "Shidaowan Guohe One 1/2". HPR1000 units are PRIS **"Shidaowan 1/2"** (Noah's "1-1/1-2" would collide with the HTR-PM module numbering). *Contradicts Griffin's stated lean toward SN-1/SN-2 → bring back.*
- **Q2 — Undocumented VVER suffixes.** Xudabao 3/4 **V-491S**, Tianwan 7/8 **V-491T**, Kudankulam 5/6 **V-412T** — base code is a clear improvement (currently generic VVER-1200 / NULL), but the suffix letters appear in NO authoritative source (PRIS/WNA show plain V-491 / V-412). Adopt Noah's suffix convention, or apply base code + ask Noah for his source?
- **Q3 — Tarapur containment:** "Mark I" (Noah) vs "Pre-Mark I" (most precise per NPCIL/AERB)?
- **Q4 — Planned-table remodel scope.** Ukraine "AP1000 Program U7-13" = 1 row for 7 unsited units (9-unit Westinghouse deal minus K5/6). Recommend: **rename + annotate, don't explode** (no confirmed sites; exploding fabricates specificity). Wloclawek U1-4 & Doicesti U1-6 are defensible aggregates (Doicesti VOYGR-6 = one 6-module plant). Minimal cleanup vs full per-unit explosion?

## Execution plan (post-decisions)
1. Migrations (numbered SQL in `migrations/`): (a) model codes, (b) statuses + Khmelnytskyi model, (c) naming/unit-labels, (d) missing-UC moves, (e) cancelled-construction moves, (f) "Permanent Shutdown"→"Shutdown" global, (g) "25" + Canadian-caps cleanup.
2. Root-cause script fixes R1/R2/R3 + three `validate_db.py` checks.
3. `python scripts/validate_db.py` → zero issues.
4. COMP update, commit, `fly deploy`.

## Status log
- 2026-05-28: Triage created. 6 research agents verified all items. Q1-Q4 resolved by Griffin.
- 2026-05-28: **APPLIED** via migrations 002-008 + code rename (007) + validate_db.py checks 6/7/8.
  - 002 new models/series; 003 corrections; 004 renaming; 005 "25"+Canada; 006 UC/cancelled/planned; 007 status rename; 008 drop orphan `"25"` (005 missed it — name had literal quote chars).
  - DB verified row-by-row; app smoke-tested (:5002) — stats, status page, renamed plants, planned/Cancelled all OK.
  - Validator: hard-FAIL checks all pass; 54 remaining = pre-existing WARN backlog (identical to pre-Noah backup).
  - Spec-blind review pass → migration 009 (Khmelnytskyi notes, Darlington date, entity_descriptions sync, orphan-model cleanup).
- 2026-05-29: **SHIPPED.** Branch `noah-review-2026-05` (058a304) pushed; `fly deploy` succeeded (3 machines health-checked); live site verified (738/223/76/417). Branch not merged to main (PR available).
  - TODO ask Noah: sources for V-491S / V-491T / V-412T suffixes; inform him of the 3 overrides (Ling'ao M310, Lianjiang CAP1000, Kudankulam V-412).
  - TODO (manual content): plant descriptions for Windscale AGR, Shidaowan (HPR1000), Darlington SMR; descriptions for new models.
