-- 006_noah_uc_cancelled_planned.sql
-- Date: 2026-05-28
-- Description: Cross-table moves + planned fixes from the Noah review.
--   (a) Add Kursk 2-3 and Darlington SMR-1 to reactors as Under Construction
--       (construction-start verified vs IAEA PRIS / CNSC); remove Kursk II-3 from planned.
--   (b) Move cancelled-but-never-operated units (Lungmen 1/2, Baltic-1) reactors->planned,
--       marked via expected_online='Cancelled' (Griffin D2).
--   (c) Planned-table fixes: Bushehr-3 model, Xiasu->Xiapu, Palisades SMR->Pioneer,
--       Ukraine AP1000 aggregate row rename+annotate (Griffin Q4 = minimal).
-- Affected tables: reactors (INSERT x2, DELETE x3), planned_reactors (INSERT x3, DELETE x1, UPDATE)
-- Bushehr-3 stays planned: no first concrete yet (WNA Feb 2026) -> project rule keeps it planned.

-- model needed for Darlington SMR-1
INSERT OR IGNORE INTO models (name, technology_id) VALUES ('BWRX-300', 6);

-- ── (a) Missing UC units ───────────────────────────────────────────────────
-- Kursk 2-3: IAEA PRIS Under Construction, first concrete 2026-01-31 (VVER-TOI / V-510K)
INSERT INTO reactors
  (plant_name, unit_number, reactor_id, country_id, state_province, site_location,
   latitude, longitude, technology_id, model_id, gross_capacity_mw, net_capacity_mw,
   design_series, status, construction_start, created_at, updated_at)
SELECT 'Kursk 2','3','Kursk 2_3_Russia', country_id, state_province, site_location,
   latitude, longitude, technology_id,
   (SELECT id FROM models WHERE name='VVER V-510K'), 1255, 1175,
   'VVER-1200/510', 'Under Construction', '2026-01-31', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM reactors WHERE plant_name='Kursk 2' AND unit_number='1';
-- remove the now-duplicated planned Kursk II-3 row
DELETE FROM planned_reactors WHERE project_name='Kursk II' AND unit_number='3';

-- Darlington SMR-1: CNSC-licensed (Apr 2025), construction authorised May 2025, basemat May 2026.
-- First G7 SMR under construction. Copy site/country/coords from Darlington U1.
INSERT INTO reactors
  (plant_name, unit_number, reactor_id, country_id, state_province, site_location,
   latitude, longitude, technology_id, model_id, gross_capacity_mw, net_capacity_mw,
   design_series, status, construction_start, created_at, updated_at)
SELECT 'Darlington SMR','1','Darlington SMR_1_Canada', country_id, state_province, site_location,
   latitude, longitude,
   (SELECT id FROM technologies WHERE code='BWR'),
   (SELECT id FROM models WHERE name='BWRX-300'), 300, 284,
   'BWRX-300', 'Under Construction', '2025-05-08', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM reactors WHERE plant_name='Darlington' AND unit_number='1';

-- ── (b) Cancelled-construction class -> planned (never operated) ────────────
INSERT INTO planned_reactors
  (project_name, unit_number, country_id, site_location, technology_id, model,
   gross_capacity_mw, net_capacity_mw, latitude, longitude, expected_online, status, likelihood, notes)
SELECT plant_name, unit_number, country_id, site_location, technology_id, 'ABWR',
   gross_capacity_mw, net_capacity_mw, latitude, longitude, 'Cancelled', 'Planned', 'Low',
   'Construction cancelled — never operated. ABWR project mothballed; abandoned after the 2021 referendum. Moved from reactors 2026-05 (Noah review).'
FROM reactors WHERE plant_name='Lungmen (Fourth)' AND unit_number IN ('1','2');
DELETE FROM reactors WHERE plant_name='Lungmen (Fourth)';

INSERT INTO planned_reactors
  (project_name, unit_number, country_id, site_location, technology_id, model,
   gross_capacity_mw, net_capacity_mw, latitude, longitude, expected_online, status, likelihood, notes)
SELECT plant_name, unit_number, country_id, site_location, technology_id, 'VVER-1200',
   gross_capacity_mw, net_capacity_mw, latitude, longitude, 'Cancelled', 'Planned', 'Low',
   'Construction suspended 2013 / cancelled — never operated. Moved from reactors 2026-05 (Noah review).'
FROM reactors WHERE plant_name='Baltic';
DELETE FROM reactors WHERE plant_name='Baltic';

-- ── (c) Planned-table fixes ────────────────────────────────────────────────
-- Bushehr-3 model -> V-528 (stays planned; no first concrete yet)
UPDATE planned_reactors SET model='VVER-1000/V-528'
 WHERE project_name='Bushehr' AND unit_number='3';

-- Xiasu -> Xiapu (romanization typo; Hualong One project, Fujian)
UPDATE planned_reactors SET project_name='Xiapu' WHERE project_name='Xiasu';

-- Palisades SMR -> Palisades Pioneer (Holtec official "Palisades Pioneer 1 & 2", SMR-300)
UPDATE planned_reactors SET project_name='Palisades Pioneer' WHERE project_name='Palisades SMR';

-- Ukraine AP1000 aggregate row: rename + annotate (minimal cleanup, do not explode)
UPDATE planned_reactors
   SET project_name='Ukraine AP1000 Program (remaining units)',
       notes='Aggregate placeholder: up to 7 AP1000 units beyond Khmelnytskyi 5/6 from the 9-unit Westinghouse–Energoatom agreement. Sites not yet allocated (candidates: Rivne, South Ukraine, Zaporizhzhia, new greenfield). Highly speculative; not individually sited.'
 WHERE project_name='Ukraine AP1000 Program' AND unit_number='7-13';
