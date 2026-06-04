-- 010_noah_override_reversals.sql
-- Date: 2026-06-04
-- Description: Reverse the three May-28 "OVERRIDE NOAH" decisions after Noah supplied
--   authoritative sources, apply the previously-deferred VVER suffix variants (Q2,
--   source now provided), and fix a related model error Noah's rebuttal surfaced.
--   All three overrides now resolve in Noah's favour (see noah_review.md, OVERRIDE section).
-- Affected tables:
--   models            INSERT OR IGNORE x4 (new VVER suffix models)
--   design_series_info INSERT OR IGNORE x4 + UPDATE x1 (M310+ description de-contradiction)
--   reactors          UPDATE: Ling'ao 1/2, Kudankulam 3/4 & 5/6, Tianwan 7/8, Xudabao 3/4, Tianwan 5/6 (10 rows)
--   planned_reactors  UPDATE: Lianjiang 3/4 (2 rows)
-- Sources (verified 2026-06-04):
--   * Lianjiang 3/4 -> CAP1400 (Guohe One), 1534 gross / 1400 net: China MEE EIA public
--     notice (Jan 2026, per Noah), corroborated by WNA, World Nuclear News, Wikipedia,
--     Global Energy Monitor. Refutes the May-28 "Shidaowan conflation" override reason
--     (it is SPIC/State Nuclear, not Shidaowan). Lianjiang 1/2 stay CAP1000 (Phase I).
--   * Tianwan 5/6 -> ACPR-1000 (was CPR-1000): WNA / World Nuclear News / Wikipedia.
--     Surfaced by Noah's M310+ explanation; independent of the taxonomy debate.
--   * VVER suffix variants V-412M/T (Kudankulam 3/4, 5/6) and V-491S/T (Xudabao 3/4,
--     Tianwan 7/8): OKB Gidropress 75-year anniversary book (2021), per Noah. PRIS/WNA
--     carry the base V-412 / V-491 codes; the suffixes are the designer's own designations.
--   * Ling'ao 1/2 -> M310+ (CGN improved/localized M310): Noah; taxonomy decision,
--     Griffin-approved 2026-06-04. Daya Bay 1/2 stay M310 (original Framatome M310).
-- Note: app renders blank descriptions gracefully; entity_descriptions for the 4 new
--   models are a tracked manual-content follow-up.

-- 1. New models (technology_id 2 = PWR)
INSERT OR IGNORE INTO models (name, technology_id) VALUES
  ('VVER V-412M', 2),   -- Kudankulam 3/4
  ('VVER V-412T', 2),   -- Kudankulam 5/6
  ('VVER V-491S', 2),   -- Xudabao (Xudapu) 3/4
  ('VVER V-491T', 2);   -- Tianwan 7/8

-- 2. New design_series lineage entries (lineage_id 13 = VVER). Suffix variants modeled on
--    the existing VVER-1000/428 -> VVER-1000/428M precedent: same generation as the base
--    series, predecessor = base series (parallel site variants, not a generational chain).
INSERT OR IGNORE INTO design_series_info
  (design_series, lineage_id, generation_order, generation_label, typical_capacity_mwe, first_commercial_year, predecessor, description) VALUES
  ('VVER-1000/412M', 13, 8, 'Gen III', '1000-1050', NULL, 'VVER-1000/412',
     'Site-specific V-412 variant for Kudankulam 3/4 (India). Designation per OKB Gidropress (2021); PRIS/WNA carry the base V-412 code.'),
  ('VVER-1000/412T', 13, 8, 'Gen III', '1000-1050', NULL, 'VVER-1000/412',
     'Site-specific V-412 variant for Kudankulam 5/6 (India). Designation per OKB Gidropress (2021); PRIS/WNA carry the base V-412 code.'),
  ('VVER-1200/491S', 13, 9, 'Gen III+', '1170-1200', NULL, 'VVER-1200/491',
     'Site-specific V-491 variant for Xudabao/Xudapu 3/4 (China). Designation per OKB Gidropress (2021); PRIS/WNA carry the base V-491 code.'),
  ('VVER-1200/491T', 13, 9, 'Gen III+', '1170-1200', NULL, 'VVER-1200/491',
     'Site-specific V-491 variant for Tianwan 7/8 (China). Designation per OKB Gidropress (2021); PRIS/WNA carry the base V-491 code.');

-- 3a. Override reversal #1 -- Ling'ao 1/2 -> M310+ (Daya Bay 1/2 deliberately untouched).
UPDATE reactors
  SET model_id=(SELECT id FROM models WHERE name='M310+'), design_series='M310+'
  WHERE plant_name='Ling Ao' AND unit_number IN ('1','2');

-- 3b. Override reversal #2 -- Lianjiang 3/4 (planned) -> CAP1400 / Guohe One.
UPDATE planned_reactors
  SET model='CAP1400', gross_capacity_mw=1534, net_capacity_mw=1400
  WHERE project_name='Lianjiang' AND unit_number IN ('3','4');

-- 3c. Override reversal #3 + Q2 suffix -- Kudankulam 3/4 -> V-412M, 5/6 -> V-412T.
UPDATE reactors
  SET model_id=(SELECT id FROM models WHERE name='VVER V-412M'), design_series='VVER-1000/412M'
  WHERE plant_name='Kudankulam' AND unit_number IN ('3','4');
UPDATE reactors
  SET model_id=(SELECT id FROM models WHERE name='VVER V-412T'), design_series='VVER-1000/412T'
  WHERE plant_name='Kudankulam' AND unit_number IN ('5','6');

-- 3d. Q2 suffixes -- Tianwan 7/8 -> V-491T, Xudabao 3/4 -> V-491S.
UPDATE reactors
  SET model_id=(SELECT id FROM models WHERE name='VVER V-491T'), design_series='VVER-1200/491T'
  WHERE plant_name='Tianwan' AND unit_number IN ('7','8');
UPDATE reactors
  SET model_id=(SELECT id FROM models WHERE name='VVER V-491S'), design_series='VVER-1200/491S'
  WHERE plant_name='Xudabao' AND unit_number IN ('3','4');

-- 4. Related fix surfaced by Noah's M310+ rebuttal -- Tianwan 5/6 are ACPR-1000, not CPR-1000.
--    ACPR-1000 model (id 33) and design_series already exist (also used by Yangjiang 5/6).
UPDATE reactors
  SET model_id=(SELECT id FROM models WHERE name='ACPR-1000'), design_series='ACPR-1000'
  WHERE plant_name='Tianwan' AND unit_number IN ('5','6');

-- 5. De-contradict the M310+ lineage description. It still named Fangjiashan 1-2 (CPR-1000)
--    and Tianwan 5-6 (now ACPR-1000) as M310+. Actual M310+ units after this migration:
--    Ling'ao 1-2 (CGN) + Fuqing 1-4 (CNNC).
UPDATE design_series_info
  SET description='Improved, more-localized M310 (higher domestic content than the original Framatome M310 at Daya Bay). Units: Ling''ao 1-2 (CGN) and Fuqing 1-4 (CNNC).'
  WHERE design_series='M310+';
