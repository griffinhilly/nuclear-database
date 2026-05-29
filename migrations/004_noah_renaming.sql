-- 004_noah_renaming.sql
-- Date: 2026-05-28
-- Description: Unit/plant renaming from the Noah review. Root cause R1 — the build
--   auto-numbered units even where real plants use letters (Biblis A/B,
--   Gundremmingen A/B/C) or where the operating plant != site name (Calder Hall &
--   Windscale are on the Sellafield site). Plus Shidaowan naming per Griffin Q1.
-- Affected tables: reactors (UPDATE plant_name / unit_number / reactor_id)
-- Source: Noah review 2026-05-28 (noah_review.md).

-- Biblis 1/2 -> Biblis A / B (German letter convention)
UPDATE reactors SET unit_number='A', reactor_id='Biblis_A_Germany' WHERE plant_name='Biblis' AND unit_number='1';
UPDATE reactors SET unit_number='B', reactor_id='Biblis_B_Germany' WHERE plant_name='Biblis' AND unit_number='2';

-- Gundremmingen 1/2/3 -> A / B / C
UPDATE reactors SET unit_number='A', reactor_id='Gundremmingen_A_Germany' WHERE plant_name='Gundremmingen' AND unit_number='1';
UPDATE reactors SET unit_number='B', reactor_id='Gundremmingen_B_Germany' WHERE plant_name='Gundremmingen' AND unit_number='2';
UPDATE reactors SET unit_number='C', reactor_id='Gundremmingen_C_Germany' WHERE plant_name='Gundremmingen' AND unit_number='3';

-- Sellafield 1-4 -> Calder Hall 1-4 (the operating Magnox plant on the Sellafield site)
UPDATE reactors
   SET plant_name='Calder Hall',
       reactor_id='Calder Hall_'||unit_number||'_UK'
 WHERE plant_name='Sellafield' AND unit_number IN ('1','2','3','4');

-- Sellafield-5 -> Windscale AGR (WAGR prototype, distinct single-unit plant)
UPDATE reactors
   SET plant_name='Windscale AGR', unit_number='1', reactor_id='Windscale AGR_1_UK'
 WHERE plant_name='Sellafield' AND unit_number='5';

-- ── Shidaowan (Q1: Guohe One official; order-sensitive) ─────────────────────
-- Step 1: CAP1400 units (currently Shidaowan U1/U2) -> plant "Shidaowan Guohe One"
UPDATE reactors
   SET plant_name='Shidaowan Guohe One',
       reactor_id='Shidaowan Guohe One_'||unit_number||'_China'
 WHERE plant_name='Shidaowan' AND design_series='CAP1400';

-- Step 2: HPR1000 Phase-I units (now the only 'Shidaowan' rows) renumber U3/U4 -> U1/U2
--   (matches IAEA PRIS "Shidaowan-1/2"; planned Phase-II rows stay U3/U4 and become consistent)
UPDATE reactors SET unit_number='1', reactor_id='Shidaowan_1_China'
 WHERE plant_name='Shidaowan' AND design_series='HPR1000' AND unit_number='3';
UPDATE reactors SET unit_number='2', reactor_id='Shidaowan_2_China'
 WHERE plant_name='Shidaowan' AND design_series='HPR1000' AND unit_number='4';
