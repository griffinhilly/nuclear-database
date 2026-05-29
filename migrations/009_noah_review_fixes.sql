-- 009_noah_review_fixes.sql
-- Date: 2026-05-28
-- Description: Fixes from the spec-blind review of migrations 002-008.
--   (1) Khmelnytskyi 3/4 contradictory notes (002-008 appended to a stale note).
--   (2) Darlington SMR-1 construction_start -> first-concrete convention (was authorization date).
--   (3) VVER-1200/510 first_commercial_year corrected (Kursk II-1 already operational).
--   (4) Drop orphan artifact models (W?, VVER V-120).
--   (5) Sync entity_descriptions to the renamed/replaced plants & models: RENAME to preserve
--       manual description content under the new keys (plant/model detail pages look these up
--       by name); DELETE descriptions of pure artifacts.
-- Affected tables: reactors (UPDATE 2), design_series_info (UPDATE 1), models (DELETE 2),
--   entity_descriptions (UPDATE ~7, DELETE ~6).

-- (1) Khmelnytskyi 3/4: replace the contradictory notes with a single coherent statement
UPDATE reactors
   SET notes='Units 3/4 are VVER-1000 (original design V-320). Construction long suspended; status returned to Under Construction amid 2024-25 completion plans. Completion equipment source unresolved — candidates are the VVER-1000 components bought from Bulgaria''s cancelled Belene project, or a pivot to Westinghouse AP1000 (units 5/6 are separately planned as AP1000). [2026-05 Noah review: status->UC; model corrected from erroneous V-392B.]'
 WHERE plant_name='Khmelnytskyi' AND unit_number IN ('3','4');

-- (2) Darlington SMR-1: use first-concrete-equivalent (basemat, May 2026) per the DB's
--     first-concrete=UC convention, not the May-2025 construction-authorization date.
UPDATE reactors SET construction_start='2026-05-01'
 WHERE plant_name='Darlington SMR' AND unit_number='1';

-- (3) VVER-1200/510 lineage: Kursk II-1 is already operational; 2026 first_commercial_year was wrong
UPDATE design_series_info SET first_commercial_year=NULL WHERE design_series='VVER-1200/510';

-- (4) Drop orphan artifact models (0 reactors, not in planned text)
DELETE FROM models WHERE name IN ('W?', 'VVER V-120')
   AND id NOT IN (SELECT DISTINCT model_id FROM reactors WHERE model_id IS NOT NULL);

-- (5a) entity_descriptions — RENAME to preserve manual content under new keys
--      Plants:
UPDATE entity_descriptions SET entity_name='Calder Hall', updated_at=CURRENT_TIMESTAMP
 WHERE entity_type='plant' AND entity_name='Sellafield';
UPDATE entity_descriptions SET entity_name='Shidaowan Guohe One', updated_at=CURRENT_TIMESTAMP
 WHERE entity_type='plant' AND entity_name='Shidaowan';   -- existing text describes the CAP1400/Guohe One units
--      Models:
UPDATE entity_descriptions SET entity_name='EL-4', updated_at=CURRENT_TIMESTAMP
 WHERE entity_type='model' AND entity_name='MONTS-D''ARREE';
UPDATE entity_descriptions SET entity_name='WH 2-loop', updated_at=CURRENT_TIMESTAMP
 WHERE entity_type='model' AND entity_name='W?';
UPDATE entity_descriptions SET entity_name='CANDU 500B', updated_at=CURRENT_TIMESTAMP
 WHERE entity_type='model' AND entity_name='CANDU 500b';
UPDATE entity_descriptions SET entity_name='CANDU 750A', updated_at=CURRENT_TIMESTAMP
 WHERE entity_type='model' AND entity_name='CANDU 750a';
UPDATE entity_descriptions SET entity_name='CANDU 750B', updated_at=CURRENT_TIMESTAMP
 WHERE entity_type='model' AND entity_name='CANDU 750b';

-- (5b) entity_descriptions — DELETE descriptions of pure artifacts / now-removed entities
DELETE FROM entity_descriptions WHERE entity_type='model'
   AND entity_name IN ('"25"', 'VVER V-120', 'VVER V-392B', 'CANDU 500a');
DELETE FROM entity_descriptions WHERE entity_type='plant'
   AND entity_name IN ('Lungmen (Fourth)', 'Baltic');  -- moved to planned (cancelled); planned has its own notes
