-- 035_phase2_wave2.sql
-- Date: 2026-10-14 (approved by Griffin 2026-10-14)
-- Description: Phase 2 fleet audit, wave 2. Three tiers per batch: 3 Haiku researchers -> Sonnet
--   adjudication -> Opus refutation with an independent second source. Only Opus-UPHELD changes are written;
--   values mapped to existing house spellings. Each UPDATE is guarded on the old value.
--   Per-change sources and quotes: audit/phase2/wave2_changes.psv (local).
-- Writes: 28. Skipped: 10 (see audit/phase2/wave2_skipped.psv).
-- Vendor values are appended to the whitelist (verification_2026-07/final_verdicts.psv) in the same change.
-- Backup: nuclear_reactors.db.bak-pre035-20261014

BEGIN TRANSACTION;
UPDATE reactors SET licensed_until = '2050' WHERE id = 122 AND (licensed_until IS NULL);  -- Loviisa 1
UPDATE reactors SET licensed_until = '2050' WHERE id = 123 AND (licensed_until IS NULL);  -- Loviisa 2
UPDATE reactor_details SET cooling_type = NULL WHERE reactor_id = 490 AND (cooling_type = 'Once-through (seawater)');  -- Calder Hall 1
UPDATE reactor_details SET cooling_type = NULL WHERE reactor_id = 491 AND (cooling_type = 'Once-through (seawater)');  -- Calder Hall 2
UPDATE reactor_details SET cooling_type = NULL WHERE reactor_id = 492 AND (cooling_type = 'Once-through (seawater)');  -- Calder Hall 3
UPDATE reactor_details SET cooling_type = NULL WHERE reactor_id = 493 AND (cooling_type = 'Once-through (seawater)');  -- Calder Hall 4
UPDATE reactor_details SET cooling_type = 'Once-through (river)' WHERE reactor_id = 165 AND (cooling_type = 'Cooling tower (natural draft)');  -- St. Alban 1
UPDATE reactor_details SET architect_engineer = 'Empresarios Agrupados' WHERE reactor_id = 443 AND (architect_engineer IS NULL);  -- Almaraz 1
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = 444 AND (cooling_type = 'Cooling tower (natural draft)');  -- Almaraz 2
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 200 AND (cooling_type = 'Once-through (river)');  -- Isar 2
UPDATE reactor_details SET cooling_type = 'Cooling tower (mechanical draft)' WHERE reactor_id = 201 AND (cooling_type = 'Cooling tower (natural draft)');  -- Neckarwestheim 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Société des Forges et Ateliers du Creusot' WHERE reactor_id = 132 AND (pressure_vessel_manufacturer IS NULL);  -- Chooz-A 1
UPDATE reactors SET planned_retirement = '2032' WHERE id = 467 AND (planned_retirement IS NULL);  -- Beznau 2
UPDATE reactor_details SET constructor = 'VEB BMK Kohle und Energie' WHERE reactor_id = 223 AND (constructor = 'Atomenergoexport');  -- Greifswald 2
UPDATE reactors SET design_series = 'VVER-440/213' WHERE id = 224 AND (design_series = 'VVER-440/230');  -- Greifswald 5
UPDATE reactors SET licensed_until = '2038' WHERE id = 124 AND (licensed_until IS NULL);  -- Olkiluoto 1
UPDATE reactors SET licensed_until = '2038' WHERE id = 125 AND (licensed_until IS NULL);  -- Olkiluoto 2
UPDATE reactors SET containment_type = 'Spherical Double' WHERE id = 12 AND (containment_type IS NULL);  -- Doel 1
UPDATE reactors SET containment_type = 'Spherical Double' WHERE id = 13 AND (containment_type IS NULL);  -- Doel 2
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 14 AND (containment_type IS NULL);  -- Doel 3
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 15 AND (containment_type IS NULL);  -- Doel 4
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 494 AND (cooling_type = 'Once-through (seawater)');  -- Chapelcross 1
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 497 AND (cooling_type = 'Once-through (seawater)');  -- Chapelcross 4
UPDATE reactor_details SET constructor = 'Mitchell Construction' WHERE reactor_id = 497 AND (constructor IS NULL);  -- Chapelcross 4
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 203 AND (cooling_type = 'Once-through (river)');  -- Grohnde 1
UPDATE reactors SET planned_retirement = NULL WHERE id = 194 AND (planned_retirement = '2028');  -- Tricastin 1
UPDATE reactors SET planned_retirement = NULL WHERE id = 195 AND (planned_retirement = '2028');  -- Tricastin 2
UPDATE reactors SET planned_retirement = NULL WHERE id = 458 AND (planned_retirement = '2045-08-01');  -- Forsmark 3
COMMIT;
