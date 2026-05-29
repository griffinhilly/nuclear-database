-- 003_noah_corrections.sql
-- Date: 2026-05-28
-- Description: In-place reactor corrections from the Noah review — reactor model,
--   design_series, technology, containment, and status. Each block targets a plant
--   + unit_number. Depends on 002 (new models/series must exist first).
-- Affected tables: reactors (UPDATE, ~45 rows)
-- Source: Noah review 2026-05-28, verified vs IAEA PRIS / WNA (see noah_review.md).
-- Notes on OVERRIDES (Noah's value NOT applied, per overwhelming evidence):
--   Ling'ao 1/2 stay M310 (not M310+); Lianjiang 3/4 stay CAP1000 (planned);
--   Kudankulam 3/4 stay V-412 (no "M"); undocumented suffixes S/T/M dropped per Griffin Q2.

-- ── Russian / export VVER model codes ──────────────────────────────────────
-- Kola 3/4: were homogenized as V-230; units 3/4 are the later V-213 generation
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-213'),
       design_series='VVER-440/213'
 WHERE plant_name='Kola' AND unit_number IN ('3','4');

-- Kursk 2 (Kursk II) 1/2: VVER-TOI = V-510K, not V-491 (that's Leningrad II)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-510K'),
       design_series='VVER-1200/510'
 WHERE plant_name='Kursk 2' AND unit_number IN ('1','2');

-- Leningrad II 3/4: align to V-491 (units 1/2 already V-491)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-491'),
       design_series='VVER-1200/491'
 WHERE plant_name='Leningrad 2' AND unit_number IN ('3','4');

-- Akkuyu 3/4: align to V-509 (units 1/2 already V-509)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-509'),
       design_series='VVER-1200/509'
 WHERE plant_name='Akkuyu' AND unit_number IN ('3','4');

-- Paks 5/6: V-527 (Paks II)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-527'),
       design_series='VVER-1200/527'
 WHERE plant_name='Paks' AND unit_number IN ('5','6');

-- El Dabaa 1-4: V-529
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-529'),
       design_series='VVER-1200/529'
 WHERE plant_name='El Dabaa';

-- Bushehr 2: V-528 (Phase II; unit 1 stays V-446, unit 3 is in planned)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-528'),
       design_series='VVER-1000/528'
 WHERE plant_name='Bushehr' AND unit_number='2';

-- Xudabao 3/4: base code V-491 (Noah's "V-491S" suffix unverified -> dropped, Q2)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-491'),
       design_series='VVER-1200/491'
 WHERE plant_name='Xudabao' AND unit_number IN ('3','4');

-- Tianwan 7/8: base code V-491 (Noah's "V-491T" suffix unverified -> dropped, Q2)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-491'),
       design_series='VVER-1200/491'
 WHERE plant_name='Tianwan' AND unit_number IN ('7','8');

-- Mochovce 3/4: V-213+ (upgraded V-213); series stays VVER-440/213
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-213+')
 WHERE plant_name='Mochovce' AND unit_number IN ('3','4');

-- Novovoronezh-1 U1: first VVER ever — VVER-210 (project V-1), not V-120/VVER-365
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER-210 (V-1)'),
       design_series='VVER-210'
 WHERE plant_name='Novovoronezh 1' AND unit_number='1';

-- Novovoronezh-1 U2: VVER-365 (project V-3M), not V-120
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER-365 (V-3M)'),
       design_series='VVER-365'
 WHERE plant_name='Novovoronezh 1' AND unit_number='2';

-- Kudankulam 5/6: fill base code V-412 (was NULL model; Noah's "V-412T" suffix dropped, Q2)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VVER V-412'),
       design_series='VVER-1000/412'
 WHERE plant_name='Kudankulam' AND unit_number IN ('5','6');

-- ── Other model / type corrections ─────────────────────────────────────────
-- Kori-1: kill "W?" artifact -> WH 2-loop
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='WH 2-loop')
 WHERE plant_name='Kori' AND unit_number='1';

-- Vandellos-1: French UNGG, not British Magnox
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='UNGG'),
       design_series='UNGG'
 WHERE plant_name='Vandellos' AND unit_number='1';

-- Brennilis: design = EL-4 (kill "MONTS-D'ARREE" model)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='EL-4')
 WHERE plant_name='Brennilis';

-- Millstone-1: BWR-3 model + Mark I containment (both were NULL)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='BWR-3'),
       containment_type='Mark I'
 WHERE plant_name='Millstone' AND unit_number='1';

-- Fuqing 1-4: M310+ (CNNC M310 family), not CNP-1000
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='M310+'),
       design_series='M310+'
 WHERE plant_name='Fuqing' AND unit_number IN ('1','2','3','4');

-- Yangjiang 3/4: CPR-1000+ (units 1/2 = CPR-1000, 5/6 = ACPR-1000)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='CPR-1000+'),
       design_series='CPR-1000+'
 WHERE plant_name='Yangjiang' AND unit_number IN ('3','4');

-- Bailong-1: CAP1000 (fix model/series mismatch — was model HPR1000 / series CAP1000)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='CAP1000')
 WHERE plant_name='Bailong' AND unit_number='1';

-- Tarapur 1/2: containment was wrongly "Mark II"; correct = Pre-Mark I (early BWR-1)
UPDATE reactors SET containment_type='Pre-Mark I'
 WHERE plant_name='Tarapur' AND unit_number IN ('1','2');

-- ── Khmelnytskyi 3/4: status + model + series all corrected ─────────────────
-- Status -> Under Construction; model V-392B was wrong (that's Novovoronezh-II) ->
-- VVER-1000 (orig. V-320 design). Belene/AP1000 equipment path uncertain (Apr 2025).
UPDATE reactors SET status='Under Construction',
       model_id=(SELECT id FROM models WHERE name='VVER V-320'),
       design_series='VVER-1000/320',
       notes=COALESCE(notes,'')||' [2026-05 Noah review: status->UC; model corrected from erroneous V-392B to VVER-1000/V-320; completion equipment source (Belene VVER-1000 vs Westinghouse) unresolved.]'
 WHERE plant_name='Khmelnytskyi' AND unit_number IN ('3','4');

-- ── Status-only corrections ────────────────────────────────────────────────
-- Madras-1: PRIS "Suspended Operation" since 2018-01-30 (EMCCR refurbishment)
UPDATE reactors SET status='Suspended'
 WHERE plant_name='Madras' AND unit_number='1';

-- CEFR: operational experimental fast reactor (not commercial), not Suspended
UPDATE reactors SET status='Operational'
 WHERE plant_name='CEFR';
