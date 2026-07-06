-- 012_cooling_system_audit.sql
-- Date: 2026-07-06
-- Description: Per-unit cooling_type audit of the entire US fleet (75 plants) plus
--   Scope C NULL-fills for well-sourced non-US/prototype reactors. The original
--   cooling_type was populated per-PLANT (not per-unit), producing systemic errors
--   in both directions. Each value below was individually researched (>=2 independent
--   documentary sources per change) and independently re-verified by the orchestrator
--   against Wikipedia article text / NRC environmental reports. See cooling_audit_2026-07.md.
-- Affected tables: reactor_details (30 US updates incl. 1 -> NULL; 8 Scope C updates;
--   2 Scope C inserts) = 40 rows; reactors.notes (5 hybrid annotations).
-- Tarapur 3/4 investigated (induced-draft-tower hypothesis) -> UNCHANGED (evidence
--   supports once-through seawater). 11 Scope C items left NULL (unresolved).

-- === Scope A: US fleet per-unit cooling corrections ===
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Arkansas Nuclear One' AND unit_number = '2');  -- Arkansas Nuclear One 2: was 'Once-through (lake)'
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Braidwood' AND unit_number = '1');  -- Braidwood 1: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Braidwood' AND unit_number = '2');  -- Braidwood 2: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Catawba' AND unit_number = '1');  -- Catawba 1: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Catawba' AND unit_number = '2');  -- Catawba 2: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Clinton' AND unit_number = '1');  -- Clinton 1: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Comanche Peak' AND unit_number = '1');  -- Comanche Peak 1: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Comanche Peak' AND unit_number = '2');  -- Comanche Peak 2: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Davis Besse' AND unit_number = '1');  -- Davis Besse 1: was 'Once-through (lake)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Duane Arnold' AND unit_number = '1');  -- Duane Arnold 1: was 'Once-through (river)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Farley (Joseph M. Farley)' AND unit_number = '1');  -- Farley (Joseph M. Farley) 1: was 'Once-through (river)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Farley (Joseph M. Farley)' AND unit_number = '2');  -- Farley (Joseph M. Farley) 2: was 'Once-through (river)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Fermi' AND unit_number = '2');  -- Fermi 2: was 'Once-through (lake)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Hatch (Edwin I. Hatch)' AND unit_number = '1');  -- Hatch (Edwin I. Hatch) 1: was 'Once-through (river)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Hatch (Edwin I. Hatch)' AND unit_number = '2');  -- Hatch (Edwin I. Hatch) 2: was 'Once-through (river)'
UPDATE reactor_details SET cooling_type = 'Once-through (lake)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'McGuire' AND unit_number = '1');  -- McGuire 1: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Once-through (lake)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'McGuire' AND unit_number = '2');  -- McGuire 2: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Palisades' AND unit_number = '1');  -- Palisades 1: was 'Once-through (lake)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Perry' AND unit_number = '1');  -- Perry 1: was 'Once-through (lake)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Prairie Island' AND unit_number = '1');  -- Prairie Island 1: was 'Once-through (river)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Prairie Island' AND unit_number = '2');  -- Prairie Island 2: was 'Once-through (river)'
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'River Bend' AND unit_number = '1');  -- River Bend 1: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Once-through (lake)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Robinson (H B Robinson)' AND unit_number = '2');  -- Robinson (H B Robinson) 2: was 'Once-through (river)'
UPDATE reactor_details SET cooling_type = 'Once-through (river)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Sequoyah' AND unit_number = '1');  -- Sequoyah 1: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Once-through (river)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Sequoyah' AND unit_number = '2');  -- Sequoyah 2: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'South Texas Project' AND unit_number = '1');  -- South Texas Project 1: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'South Texas Project' AND unit_number = '2');  -- South Texas Project 2: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Once-through (lake)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Summer (V C Summer)' AND unit_number = '1');  -- Summer (V C Summer) 1: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Wolf Creek' AND unit_number = '1');  -- Wolf Creek 1: was 'Cooling tower (natural draft)'
UPDATE reactor_details SET cooling_type = NULL WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'GE Vallecitos' AND unit_number = '1');  -- GE Vallecitos 1: was 'Once-through (seawater)'

-- === Scope C: NULL fills (>=2 sources); UPDATE existing reactor_details rows ===
UPDATE reactor_details SET cooling_type = 'Once-through (lake)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Brennilis' AND unit_number = '1');  -- Brennilis 1: was None
UPDATE reactor_details SET cooling_type = 'Once-through (river)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'APS1 Obninsk' AND unit_number = '1');  -- APS1 Obninsk 1: was None
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'BREST' AND unit_number = '1');  -- BREST 1: was None
UPDATE reactor_details SET cooling_type = 'Once-through (seawater)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Dounreay DFR' AND unit_number = '1');  -- Dounreay DFR 1: was None
UPDATE reactor_details SET cooling_type = 'Once-through (seawater)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Dounreay PFR' AND unit_number = '1');  -- Dounreay PFR 1: was None
UPDATE reactor_details SET cooling_type = 'Once-through (seawater)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Bonus' AND unit_number = '1');  -- Bonus 1: was None
UPDATE reactor_details SET cooling_type = 'Once-through (river)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Saxton' AND unit_number = '1');  -- Saxton 1: was None
UPDATE reactor_details SET cooling_type = 'Once-through (river)' WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Shippingport' AND unit_number = '1');  -- Shippingport 1: was None

-- === Scope C: NULL fills; INSERT (these reactors had no reactor_details row) ===
INSERT INTO reactor_details (reactor_id, cooling_type) SELECT id, 'Once-through (lake)' FROM reactors WHERE plant_name = 'Darlington SMR' AND unit_number = '1';  -- Darlington SMR 1: new row (had no reactor_details)
INSERT INTO reactor_details (reactor_id, cooling_type) SELECT id, 'Cooling tower (natural draft)' FROM reactors WHERE plant_name = 'Kursk 2' AND unit_number = '3';  -- Kursk 2 3: new row (had no reactor_details)

-- === Material hybrid annotations (once-through units with significant cooling towers) ===
UPDATE reactors SET notes = TRIM(COALESCE(notes,'') || ' Cooling: once-through from the Tennessee River (Wheeler Lake); supplemented by mechanical-draft helper cooling towers.') WHERE plant_name = 'Browns Ferry' AND unit_number = '1';
UPDATE reactors SET notes = TRIM(COALESCE(notes,'') || ' Cooling: once-through from the Tennessee River (Wheeler Lake); supplemented by mechanical-draft helper cooling towers.') WHERE plant_name = 'Browns Ferry' AND unit_number = '2';
UPDATE reactors SET notes = TRIM(COALESCE(notes,'') || ' Cooling: once-through from the Tennessee River (Wheeler Lake); supplemented by mechanical-draft helper cooling towers.') WHERE plant_name = 'Browns Ferry' AND unit_number = '3';
UPDATE reactors SET notes = TRIM(COALESCE(notes,'') || ' Cooling: primarily once-through from Chickamauga Lake (Tennessee River); two natural-draft cooling towers used in supplemental/helper mode during low-flow/high-temperature conditions.') WHERE plant_name = 'Sequoyah' AND unit_number = '1';
UPDATE reactors SET notes = TRIM(COALESCE(notes,'') || ' Cooling: primarily once-through from Chickamauga Lake (Tennessee River); two natural-draft cooling towers used in supplemental/helper mode during low-flow/high-temperature conditions.') WHERE plant_name = 'Sequoyah' AND unit_number = '2';
