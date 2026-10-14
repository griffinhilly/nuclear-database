-- 033_phase2_pilot.sql
-- Date: 2026-10-14
-- Description: Phase 2 audit pilot (Hungary, Czech Republic, Taiwan + passed licence/retirement dates).
--   Three tiers: 3 Haiku researchers per batch -> Sonnet adjudication -> Opus refutation review with an
--   independent second source. Only changes the Opus tier UPHELD are written; values mapped to house
--   vocabulary. Per-change sources and quotes: audit/phase2/033_changes.psv (local).
-- Writes: 62. Skipped: 8 (refuted, unsure, ambiguous role, not a date).
-- Vendor values are appended to the whitelist (verification_2026-07/final_verdicts.psv) in the same change.
-- Backup: nuclear_reactors.db.bak-pre033-20261014

BEGIN TRANSACTION;
UPDATE reactors SET planned_retirement = NULL WHERE id = 556 AND (planned_retirement = '2021');  -- Beaver Valley 1
UPDATE reactors SET licensed_until = '2030-06' WHERE id = 443 AND (licensed_until = '2020');  -- Almaraz 1
UPDATE reactors SET licensed_until = '2030-06' WHERE id = 444 AND (licensed_until = '2020');  -- Almaraz 2
UPDATE reactors SET planned_retirement = NULL WHERE id = 383 AND (planned_retirement = '2025');  -- Leningrad 1 3
UPDATE reactors SET planned_retirement = NULL WHERE id = 361 AND (planned_retirement = '2025');  -- Beloyarsk 3
UPDATE reactors SET planned_retirement = '2030' WHERE id = 504 AND (planned_retirement = '2024');  -- Hartlepool 1
UPDATE reactors SET planned_retirement = '2030' WHERE id = 505 AND (planned_retirement = '2024');  -- Hartlepool 2
UPDATE reactors SET licensed_until = '2044-11-02' WHERE id = 584 AND (licensed_until = '2024');  -- Diablo Canyon 1
UPDATE reactors SET licensed_until = '2045-08-26' WHERE id = 585 AND (licensed_until = '2025');  -- Diablo Canyon 2
UPDATE reactors SET planned_retirement = '2030' WHERE id = 585 AND (planned_retirement = '2025');  -- Diablo Canyon 2
UPDATE reactors SET planned_retirement = '2030' WHERE id = 508 AND (planned_retirement = '2024');  -- Heysham B 1
UPDATE reactors SET planned_retirement = '2035' WHERE id = 18 AND (planned_retirement = '2025-02-15');  -- Tihange 3
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 116 AND (containment_type IS NULL);  -- Dukovany 1
UPDATE reactor_details SET architect_engineer = 'Energoprojekt Praha' WHERE reactor_id = 116 AND (architect_engineer = 'Atomenergoproekt');  -- Dukovany 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Skoda Works' WHERE reactor_id = 116 AND (pressure_vessel_manufacturer IS NULL);  -- Dukovany 1
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 117 AND (containment_type IS NULL);  -- Dukovany 2
UPDATE reactor_details SET architect_engineer = 'Energoprojekt Praha' WHERE reactor_id = 117 AND (architect_engineer = 'Atomenergoproekt');  -- Dukovany 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Skoda Works' WHERE reactor_id = 117 AND (pressure_vessel_manufacturer IS NULL);  -- Dukovany 2
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 118 AND (containment_type IS NULL);  -- Dukovany 3
UPDATE reactor_details SET architect_engineer = 'Energoprojekt Praha' WHERE reactor_id = 118 AND (architect_engineer = 'Atomenergoproekt');  -- Dukovany 3
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Skoda Works' WHERE reactor_id = 118 AND (pressure_vessel_manufacturer IS NULL);  -- Dukovany 3
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 119 AND (containment_type IS NULL);  -- Dukovany 4
UPDATE reactor_details SET architect_engineer = 'Energoprojekt Praha' WHERE reactor_id = 119 AND (architect_engineer = 'Atomenergoproekt');  -- Dukovany 4
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Skoda Works' WHERE reactor_id = 119 AND (pressure_vessel_manufacturer IS NULL);  -- Dukovany 4
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 474 AND (turbine_supplier = 'General Electric');  -- Kuosheng (Second) 1
UPDATE reactors SET licensed_until = '2021-12-27' WHERE id = 474 AND (licensed_until IS NULL);  -- Kuosheng (Second) 1
UPDATE reactors SET licensed_until = '2023-03-14' WHERE id = 475 AND (licensed_until IS NULL);  -- Kuosheng (Second) 2
UPDATE reactor_details SET architect_engineer = 'Ebasco' WHERE reactor_id = 472 AND (architect_engineer IS NULL);  -- Chinshan (First) 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 472 AND (turbine_supplier = 'General Electric');  -- Chinshan (First) 1
UPDATE reactors SET licensed_until = '2018-12-05' WHERE id = 472 AND (licensed_until IS NULL);  -- Chinshan (First) 1
UPDATE reactors SET planned_retirement = '2018-12-06' WHERE id = 472 AND (planned_retirement = '2018-12-01');  -- Chinshan (First) 1
UPDATE reactors SET licensed_until = '2019-07-15' WHERE id = 473 AND (licensed_until IS NULL);  -- Chinshan (First) 2
UPDATE reactors SET planned_retirement = '2019-07-16' WHERE id = 473 AND (planned_retirement = '2019-07-01');  -- Chinshan (First) 2
UPDATE reactors SET planned_retirement = NULL WHERE id = 47 AND (planned_retirement = '2024');  -- Pickering 5
UPDATE reactors SET planned_retirement = NULL WHERE id = 48 AND (planned_retirement = '2024');  -- Pickering 6
UPDATE reactors SET planned_retirement = NULL WHERE id = 49 AND (planned_retirement = '2024');  -- Pickering 7
UPDATE reactors SET planned_retirement = NULL WHERE id = 50 AND (planned_retirement = '2024');  -- Pickering 8
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 234 AND (containment_type IS NULL);  -- Paks 1
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 235 AND (containment_type IS NULL);  -- Paks 2
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 236 AND (containment_type IS NULL);  -- Paks 3
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 237 AND (containment_type IS NULL);  -- Paks 4
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Skoda Works' WHERE reactor_id = 237 AND (pressure_vessel_manufacturer IS NULL);  -- Paks 4
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 729 AND (containment_type IS NULL);  -- Paks 5
UPDATE reactors SET planned_retirement = NULL WHERE id = 426 AND (planned_retirement = '2023');  -- Kori 2
UPDATE reactors SET planned_retirement = NULL WHERE id = 427 AND (planned_retirement = '2025');  -- Kori 3
UPDATE reactors SET planned_retirement = NULL WHERE id = 587 AND (planned_retirement = '2021');  -- Dresden 2
UPDATE reactors SET planned_retirement = NULL WHERE id = 588 AND (planned_retirement = '2021');  -- Dresden 3
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 478 AND (containment_type IS NULL);  -- Maanshan (Third) 1
UPDATE reactors SET licensed_until = '2024' WHERE id = 478 AND (licensed_until IS NULL);  -- Maanshan (Third) 1
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 479 AND (containment_type IS NULL);  -- Maanshan (Third) 2
UPDATE reactors SET licensed_until = '2025' WHERE id = 479 AND (licensed_until IS NULL);  -- Maanshan (Third) 2
UPDATE reactors SET licensed_until = '2034' WHERE id = 450 AND (licensed_until = '2024');  -- Trillo 1
UPDATE reactors SET planned_retirement = '2035' WHERE id = 15 AND (planned_retirement = '2025-09-01');  -- Doel 4
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 120 AND (containment_type IS NULL);  -- Temelin 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Skoda Works' WHERE reactor_id = 120 AND (pressure_vessel_manufacturer IS NULL);  -- Temelin 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Skoda Works' WHERE reactor_id = 121 AND (pressure_vessel_manufacturer IS NULL);  -- Temelin 2
UPDATE reactors SET licensed_until = '2030' WHERE id = 445 AND (licensed_until = '2021');  -- Asco 1
UPDATE reactors SET licensed_until = '2031' WHERE id = 446 AND (licensed_until = '2021');  -- Asco 2
UPDATE reactors SET planned_retirement = '2030' WHERE id = 506 AND (planned_retirement = '2024');  -- Heysham A 1
UPDATE reactors SET planned_retirement = '2030' WHERE id = 507 AND (planned_retirement = '2024');  -- Heysham A 2
UPDATE reactors SET licensed_until = '2030' WHERE id = 452 AND (licensed_until = '2020');  -- Vandellos 2
UPDATE reactors SET licensed_until = '2030' WHERE id = 447 AND (licensed_until = '2021');  -- Cofrentes 1
COMMIT;
