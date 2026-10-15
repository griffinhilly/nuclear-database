-- 038_phase2_wave5.sql
-- Date: 2026-10-14 (approved by Griffin 2026-10-15; applied 2026-10-15)
-- Description: Phase 2 fleet audit, wave 5. Three tiers per batch: 3 Haiku researchers -> Sonnet
--   adjudication -> Opus refutation with an independent second source. Only Opus-UPHELD changes are written;
--   values mapped to existing house spellings. Each UPDATE is guarded on the old value.
--   Per-change sources and quotes: audit/phase2/wave5_changes.psv (local).
-- Writes: 50. Skipped: 27 (see audit/phase2/wave5_skipped.psv).
-- Vendor values are appended to the whitelist (verification_2026-07/final_verdicts.psv) in the same change.
-- Backup: nuclear_reactors.db.bak-pre038-<date>

BEGIN TRANSACTION;
UPDATE reactors SET containment_type = 'Ice Condenser' WHERE id = 122 AND (containment_type IS NULL);  -- Loviisa 1
UPDATE reactors SET containment_type = 'Ice Condenser' WHERE id = 123 AND (containment_type IS NULL);  -- Loviisa 2
UPDATE reactor_details SET architect_engineer = 'Motor-Columbus' WHERE reactor_id = 468 AND (architect_engineer IS NULL);  -- Gösgen 1
UPDATE reactor_details SET constructor = 'Taylor Woodrow' WHERE reactor_id = 490 AND (constructor IS NULL);  -- Calder Hall 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Whessoe' WHERE reactor_id = 491 AND (pressure_vessel_manufacturer IS NULL);  -- Calder Hall 2
UPDATE reactor_details SET cooling_type = 'Once-through (river)' WHERE reactor_id = 168 AND (cooling_type = 'Cooling tower (natural draft)');  -- St. Alban 2
UPDATE reactor_details SET architect_engineer = 'Empresarios Agrupados' WHERE reactor_id = 444 AND (architect_engineer IS NULL);  -- Almaraz 2
UPDATE reactor_details SET constructor = 'Siemens' WHERE reactor_id = 215 AND (constructor IS NULL);  -- Obrigheim 1
UPDATE reactor_details SET architect_engineer = 'EDF' WHERE reactor_id = 185 AND (architect_engineer IS NULL);  -- Golfech 1
UPDATE reactor_details SET architect_engineer = 'EDF' WHERE reactor_id = 191 AND (architect_engineer IS NULL);  -- Golfech 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Degerfors Järnverk' WHERE reactor_id = 453 AND (pressure_vessel_manufacturer IS NULL);  -- Ågesta 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Framatome' WHERE reactor_id = 141 AND (pressure_vessel_manufacturer IS NULL);  -- Gravelines 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Framatome' WHERE reactor_id = 142 AND (pressure_vessel_manufacturer IS NULL);  -- Gravelines 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Rotterdam Dockyard (RDM)' WHERE reactor_id = 463 AND (pressure_vessel_manufacturer IS NULL);  -- Ringhals 2
UPDATE reactors SET planned_retirement = NULL WHERE id = 140 AND (planned_retirement = '2026');  -- Dampierre 1
UPDATE reactors SET planned_retirement = NULL WHERE id = 143 AND (planned_retirement = '2026');  -- Dampierre 2
UPDATE reactor_details SET constructor = 'BBC / General Electric' WHERE reactor_id = 469 AND (constructor IS NULL);  -- Leibstadt 1
UPDATE reactor_details SET constructor = 'Bylor' WHERE reactor_id = 514 AND (constructor IS NULL);  -- Hinkley Point C 1
UPDATE reactor_details SET turbine_supplier = 'Arabelle Solutions' WHERE reactor_id = 514 AND (turbine_supplier IS NULL);  -- Hinkley Point C 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Framatome' WHERE reactor_id = 514 AND (pressure_vessel_manufacturer IS NULL);  -- Hinkley Point C 1
UPDATE reactor_details SET constructor = 'Bylor' WHERE reactor_id = 515 AND (constructor IS NULL);  -- Hinkley Point C 2
UPDATE reactor_details SET turbine_supplier = 'Arabelle Solutions' WHERE reactor_id = 515 AND (turbine_supplier IS NULL);  -- Hinkley Point C 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Framatome' WHERE reactor_id = 515 AND (pressure_vessel_manufacturer IS NULL);  -- Hinkley Point C 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'John Thompson' WHERE reactor_id = 498 AND (pressure_vessel_manufacturer IS NULL);  -- Dounreay DFR 1
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 466 AND (containment_type IS NULL);  -- Beznau 1
UPDATE reactors SET planned_retirement = '2033' WHERE id = 466 AND (planned_retirement IS NULL);  -- Beznau 1
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 467 AND (containment_type IS NULL);  -- Beznau 2
UPDATE reactors SET planned_retirement = '2035' WHERE id = 450 AND (planned_retirement IS NULL);  -- Trillo 1
UPDATE reactor_details SET architect_engineer = 'EDF' WHERE reactor_id = 173 AND (architect_engineer IS NULL);  -- Flamanville 1
UPDATE reactor_details SET architect_engineer = 'EDF' WHERE reactor_id = 176 AND (architect_engineer IS NULL);  -- Flamanville 2
UPDATE reactor_details SET architect_engineer = 'EDF' WHERE reactor_id = 197 AND (architect_engineer IS NULL);  -- Flamanville 3
UPDATE reactor_details SET constructor = 'VEB BMK Kohle und Energie' WHERE reactor_id = 221 AND (constructor = 'Atomenergoexport');  -- Greifswald 3
UPDATE reactor_details SET constructor = 'VEB BMK Kohle und Energie' WHERE reactor_id = 222 AND (constructor = 'Atomenergoexport');  -- Greifswald 1
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 224 AND (containment_type IS NULL);  -- Greifswald 5
UPDATE reactors SET licensed_until = '2038' WHERE id = 126 AND (licensed_until IS NULL);  -- Olkiluoto 3
UPDATE reactor_details SET constructor = 'Kraftwerk Union (KWU)' WHERE reactor_id = 340 AND (constructor IS NULL);  -- Borssele 1
UPDATE reactors SET licensed_until = '2033' WHERE id = 340 AND (licensed_until IS NULL);  -- Borssele 1
UPDATE reactor_details SET architect_engineer = 'EDF' WHERE reactor_id = 182 AND (architect_engineer IS NULL);  -- Nogent 2
UPDATE reactor_details SET cooling_type = 'Once-through (river)' WHERE reactor_id = 269 AND (cooling_type = 'Cooling tower (natural draft)');  -- Caorso 1
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 495 AND (cooling_type = 'Once-through (seawater)');  -- Chapelcross 2
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 496 AND (cooling_type = 'Once-through (seawater)');  -- Chapelcross 3
UPDATE reactor_details SET constructor = 'Mitchell Construction' WHERE reactor_id = 496 AND (constructor IS NULL);  -- Chapelcross 3
UPDATE reactors SET planned_retirement = NULL WHERE id = 456 AND (planned_retirement = '2040-12-01');  -- Forsmark 1
UPDATE reactors SET planned_retirement = NULL WHERE id = 457 AND (planned_retirement = '2041-07-01');  -- Forsmark 2
UPDATE reactors SET planned_retirement = '2032' WHERE id = 446 AND (planned_retirement IS NULL);  -- Asco 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Rotterdam Dockyard (RDM)' WHERE reactor_id = 447 AND (pressure_vessel_manufacturer IS NULL);  -- Cofrentes 1
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 524 AND (containment_type = 'Large Dry');  -- Sizewell B 1
UPDATE reactor_details SET turbine_supplier = 'GEC-Alsthom' WHERE reactor_id = 524 AND (turbine_supplier = 'GEC');  -- Sizewell B 1
UPDATE reactors SET planned_retirement = '2055' WHERE id = 524 AND (planned_retirement = '2035');  -- Sizewell B 1
UPDATE reactor_details SET architect_engineer = 'EDF' WHERE reactor_id = 184 AND (architect_engineer IS NULL);  -- Penly 1
COMMIT;
