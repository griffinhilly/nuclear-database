-- 037_phase2_wave4.sql
-- Date: 2026-10-14 (approved by Griffin 2026-10-15; applied 2026-10-15)
-- Description: Phase 2 fleet audit, wave 4. Three tiers per batch: 3 Haiku researchers -> Sonnet
--   adjudication -> Opus refutation with an independent second source. Only Opus-UPHELD changes are written;
--   values mapped to existing house spellings. Each UPDATE is guarded on the old value.
--   Per-change sources and quotes: audit/phase2/wave4_changes.psv (local).
-- Writes: 131. Skipped: 29 (see audit/phase2/wave4_skipped.psv).
-- Vendor values are appended to the whitelist (verification_2026-07/final_verdicts.psv) in the same change.
-- Backup: nuclear_reactors.db.bak-pre037-<date>

BEGIN TRANSACTION;
UPDATE reactor_details SET constructor = 'Titan-2' WHERE reactor_id = 385 AND (constructor = 'Atomstroyexport');  -- Leningrad 2 1
UPDATE reactor_details SET architect_engineer = 'Atomproekt' WHERE reactor_id = 385 AND (architect_engineer IS NULL);  -- Leningrad 2 1
UPDATE reactor_details SET constructor = 'Titan-2' WHERE reactor_id = 386 AND (constructor = 'Atomstroyexport');  -- Leningrad 2 2
UPDATE reactor_details SET architect_engineer = 'Atomproekt' WHERE reactor_id = 386 AND (architect_engineer IS NULL);  -- Leningrad 2 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Izhora Plants' WHERE reactor_id = 386 AND (pressure_vessel_manufacturer IS NULL);  -- Leningrad 2 2
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 726 AND (containment_type IS NULL);  -- Leningrad 2 3
UPDATE reactor_details SET constructor = 'Titan-2' WHERE reactor_id = 726 AND (constructor = 'Atomstroyexport');  -- Leningrad 2 3
UPDATE reactor_details SET architect_engineer = 'Atomproekt' WHERE reactor_id = 726 AND (architect_engineer IS NULL);  -- Leningrad 2 3
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 738 AND (containment_type IS NULL);  -- Leningrad 2 4
UPDATE reactor_details SET constructor = 'Titan-2' WHERE reactor_id = 738 AND (constructor = 'Atomstroyexport');  -- Leningrad 2 4
UPDATE reactor_details SET architect_engineer = 'Atomproekt' WHERE reactor_id = 738 AND (architect_engineer IS NULL);  -- Leningrad 2 4
UPDATE reactor_details SET architect_engineer = 'Atomenergoproekt' WHERE reactor_id = 268 AND (architect_engineer IS NULL);  -- Bushehr 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 534 AND (turbine_supplier IS NULL);  -- Chernobyl 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 535 AND (turbine_supplier IS NULL);  -- Chernobyl 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 536 AND (turbine_supplier IS NULL);  -- Chernobyl 4
UPDATE reactors SET licensed_until = '2033' WHERE id = 371 AND (licensed_until IS NULL);  -- Kola 1
UPDATE reactors SET planned_retirement = '2033' WHERE id = 371 AND (planned_retirement = '2032');  -- Kola 1
UPDATE reactors SET licensed_until = '2034' WHERE id = 372 AND (licensed_until IS NULL);  -- Kola 2
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 373 AND (containment_type IS NULL);  -- Kola 3
UPDATE reactors SET licensed_until = '2030' WHERE id = 383 AND (licensed_until IS NULL);  -- Leningrad 1 3
UPDATE reactors SET licensed_until = '2030' WHERE id = 384 AND (licensed_until IS NULL);  -- Leningrad 1 4
UPDATE reactors SET planned_retirement = NULL WHERE id = 384 AND (planned_retirement = '2026');  -- Leningrad 1 4
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 406 AND (containment_type IS NULL);  -- Mochovce 1
UPDATE reactor_details SET architect_engineer = 'Energoprojekt Praha' WHERE reactor_id = 406 AND (architect_engineer = 'Atomenergoproekt');  -- Mochovce 1
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 407 AND (containment_type IS NULL);  -- Mochovce 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Skoda Works' WHERE reactor_id = 408 AND (pressure_vessel_manufacturer IS NULL);  -- Mochovce 3
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 409 AND (containment_type IS NULL);  -- Mochovce 4
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Skoda Works' WHERE reactor_id = 409 AND (pressure_vessel_manufacturer IS NULL);  -- Mochovce 4
UPDATE reactors SET licensed_until = '2040' WHERE id = 361 AND (licensed_until IS NULL);  -- Beloyarsk 3
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 362 AND (turbine_supplier IS NULL);  -- Beloyarsk 4
UPDATE reactor_details SET pressure_vessel_manufacturer = 'ZiO-Podolsk' WHERE reactor_id = 362 AND (pressure_vessel_manufacturer IS NULL);  -- Beloyarsk 4
UPDATE reactors SET licensed_until = '2033' WHERE id = 545 AND (licensed_until IS NULL);  -- South Ukraine 1
UPDATE reactors SET licensed_until = '2035' WHERE id = 546 AND (licensed_until IS NULL);  -- South Ukraine 2
UPDATE reactors SET licensed_until = '2030' WHERE id = 547 AND (licensed_until IS NULL);  -- South Ukraine 3
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 379 AND (containment_type IS NULL);  -- Kursk 2 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 379 AND (pressure_vessel_manufacturer IS NULL);  -- Kursk 2 1
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 380 AND (containment_type IS NULL);  -- Kursk 2 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 380 AND (pressure_vessel_manufacturer IS NULL);  -- Kursk 2 2
UPDATE reactors SET licensed_until = '2028' WHERE id = 537 AND (licensed_until IS NULL);  -- Khmelnytskyi 1
UPDATE reactors SET licensed_until = '2035' WHERE id = 538 AND (licensed_until IS NULL);  -- Khmelnytskyi 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 539 AND (turbine_supplier = 'Skoda');  -- Khmelnytskyi 3
UPDATE reactor_details SET turbine_supplier = 'Kaluga Turbine Plant' WHERE reactor_id = 351 AND (turbine_supplier IS NULL);  -- Akademik Lomonosov 1
UPDATE reactors SET licensed_until = '2029' WHERE id = 351 AND (licensed_until IS NULL);  -- Akademik Lomonosov 1
UPDATE reactor_details SET turbine_supplier = 'Kaluga Turbine Plant' WHERE reactor_id = 352 AND (turbine_supplier IS NULL);  -- Akademik Lomonosov 2
UPDATE reactors SET licensed_until = '2029' WHERE id = 352 AND (licensed_until IS NULL);  -- Akademik Lomonosov 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 395 AND (turbine_supplier IS NULL);  -- Rostov 2
UPDATE reactor_details SET constructor = 'NIAEP' WHERE reactor_id = 396 AND (constructor IS NULL);  -- Rostov 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 396 AND (turbine_supplier IS NULL);  -- Rostov 3
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Izhora Plants' WHERE reactor_id = 396 AND (pressure_vessel_manufacturer IS NULL);  -- Rostov 3
UPDATE reactor_details SET constructor = 'NIAEP' WHERE reactor_id = 397 AND (constructor IS NULL);  -- Rostov 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 397 AND (turbine_supplier IS NULL);  -- Rostov 4
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Izhora Plants' WHERE reactor_id = 397 AND (pressure_vessel_manufacturer IS NULL);  -- Rostov 4
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 336 AND (containment_type IS NULL);  -- Ignalina 1
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 337 AND (containment_type IS NULL);  -- Ignalina 2
UPDATE reactor_details SET constructor = 'Magadanenergostroy' WHERE reactor_id = 363 AND (constructor IS NULL);  -- Bilibino 1
UPDATE reactor_details SET turbine_supplier = 'Brno Machine-Building Plant' WHERE reactor_id = 363 AND (turbine_supplier IS NULL);  -- Bilibino 1
UPDATE reactor_details SET constructor = 'Magadanenergostroy' WHERE reactor_id = 364 AND (constructor IS NULL);  -- Bilibino 2
UPDATE reactor_details SET turbine_supplier = 'Brno Machine-Building Plant' WHERE reactor_id = 364 AND (turbine_supplier IS NULL);  -- Bilibino 2
UPDATE reactor_details SET constructor = 'Magadanenergostroy' WHERE reactor_id = 365 AND (constructor IS NULL);  -- Bilibino 3
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 7 AND (cooling_type = 'Once-through (river)');  -- Rooppur 1
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 7 AND (containment_type IS NULL);  -- Rooppur 1
UPDATE reactor_details SET architect_engineer = 'Rosatom Engineering Division' WHERE reactor_id = 7 AND (architect_engineer IS NULL);  -- Rooppur 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 7 AND (pressure_vessel_manufacturer IS NULL);  -- Rooppur 1
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 8 AND (cooling_type = 'Once-through (river)');  -- Rooppur 2
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 8 AND (containment_type IS NULL);  -- Rooppur 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 8 AND (pressure_vessel_manufacturer IS NULL);  -- Rooppur 2
UPDATE reactors SET licensed_until = '2030' WHERE id = 399 AND (licensed_until IS NULL);  -- Smolensk 2
UPDATE reactors SET licensed_until = '2034' WHERE id = 400 AND (licensed_until IS NULL);  -- Smolensk 3
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 718 AND (containment_type IS NULL);  -- El Dabaa 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Izhora Plants' WHERE reactor_id = 718 AND (pressure_vessel_manufacturer IS NULL);  -- El Dabaa 1
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 719 AND (containment_type IS NULL);  -- El Dabaa 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 719 AND (pressure_vessel_manufacturer IS NULL);  -- El Dabaa 2
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 720 AND (containment_type IS NULL);  -- El Dabaa 3
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 721 AND (containment_type IS NULL);  -- El Dabaa 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 6 AND (turbine_supplier IS NULL);  -- Armenian 2
UPDATE reactor_details SET constructor = 'Kursk NPP Construction Directorate' WHERE reactor_id = 375 AND (constructor IS NULL);  -- Kursk 1 1
UPDATE reactor_details SET constructor = 'Kursk NPP Construction Directorate' WHERE reactor_id = 376 AND (constructor IS NULL);  -- Kursk 1 2
UPDATE reactors SET planned_retirement = '2033' WHERE id = 377 AND (planned_retirement = '2029');  -- Kursk 1 3
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 541 AND (containment_type IS NULL);  -- Rivne 1
UPDATE reactors SET licensed_until = '2030' WHERE id = 541 AND (licensed_until IS NULL);  -- Rivne 1
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 542 AND (containment_type IS NULL);  -- Rivne 2
UPDATE reactors SET licensed_until = '2037' WHERE id = 543 AND (licensed_until IS NULL);  -- Rivne 3
UPDATE reactors SET licensed_until = '2044' WHERE id = 411 AND (licensed_until IS NULL);  -- Koeberg 1
UPDATE reactors SET licensed_until = '2045' WHERE id = 412 AND (licensed_until IS NULL);  -- Koeberg 2
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = 354 AND (cooling_type = 'Cooling tower (natural draft)');  -- Balakovo 1
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = 355 AND (cooling_type = 'Cooling tower (natural draft)');  -- Balakovo 2
UPDATE reactors SET licensed_until = '2043' WHERE id = 355 AND (licensed_until IS NULL);  -- Balakovo 2
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = 356 AND (cooling_type = 'Cooling tower (natural draft)');  -- Balakovo 3
UPDATE reactors SET licensed_until = '2048' WHERE id = 356 AND (licensed_until IS NULL);  -- Balakovo 3
UPDATE reactor_details SET cooling_type = 'Cooling pond' WHERE reactor_id = 357 AND (cooling_type = 'Cooling tower (natural draft)');  -- Balakovo 4
UPDATE reactors SET licensed_until = '2051' WHERE id = 357 AND (licensed_until IS NULL);  -- Balakovo 4
UPDATE reactors SET licensed_until = '2044' WHERE id = 367 AND (licensed_until IS NULL);  -- Kalinin 1
UPDATE reactors SET licensed_until = '2038' WHERE id = 368 AND (licensed_until IS NULL);  -- Kalinin 2
UPDATE reactor_details SET constructor = 'AECL-Ansaldo Consortium' WHERE reactor_id = 349 AND (constructor = 'AECL');  -- Cernavodă 1
UPDATE reactor_details SET architect_engineer = 'CITON' WHERE reactor_id = 349 AND (architect_engineer IS NULL);  -- Cernavodă 1
UPDATE reactor_details SET constructor = 'AECL-Ansaldo Consortium' WHERE reactor_id = 350 AND (constructor = 'AECL');  -- Cernavodă 2
UPDATE reactor_details SET architect_engineer = 'CITON' WHERE reactor_id = 350 AND (architect_engineer IS NULL);  -- Cernavodă 2
UPDATE reactor_details SET constructor = 'Titan-2' WHERE reactor_id = 727 AND (constructor IS NULL);  -- BREST 1
UPDATE reactor_details SET constructor = 'Atomstroyexport' WHERE reactor_id = 9 AND (constructor IS NULL);  -- Belarusian 1
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 9 AND (turbine_supplier IS NULL);  -- Belarusian 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 9 AND (pressure_vessel_manufacturer IS NULL);  -- Belarusian 1
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 10 AND (containment_type IS NULL);  -- Belarusian 2
UPDATE reactor_details SET constructor = 'Atomstroyexport' WHERE reactor_id = 10 AND (constructor IS NULL);  -- Belarusian 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 10 AND (pressure_vessel_manufacturer IS NULL);  -- Belarusian 2
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 389 AND (cooling_type = 'Cooling pond');  -- Novovoronezh 1 3
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 390 AND (cooling_type = 'Cooling pond');  -- Novovoronezh 1 4
UPDATE reactors SET licensed_until = '2032' WHERE id = 390 AND (licensed_until IS NULL);  -- Novovoronezh 1 4
UPDATE reactors SET licensed_until = '2036' WHERE id = 391 AND (licensed_until IS NULL);  -- Novovoronezh 1 5
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 480 AND (containment_type IS NULL);  -- Akkuyu 1
UPDATE reactor_details SET architect_engineer = 'Atomenergoproekt' WHERE reactor_id = 480 AND (architect_engineer IS NULL);  -- Akkuyu 1
UPDATE reactor_details SET turbine_supplier = 'GE Steam Power' WHERE reactor_id = 480 AND (turbine_supplier IS NULL);  -- Akkuyu 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 480 AND (pressure_vessel_manufacturer = 'Izhora Plants');  -- Akkuyu 1
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 481 AND (containment_type IS NULL);  -- Akkuyu 2
UPDATE reactor_details SET architect_engineer = 'Atomenergoproekt' WHERE reactor_id = 481 AND (architect_engineer IS NULL);  -- Akkuyu 2
UPDATE reactor_details SET turbine_supplier = 'GE Steam Power' WHERE reactor_id = 481 AND (turbine_supplier IS NULL);  -- Akkuyu 2
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 722 AND (containment_type IS NULL);  -- Akkuyu 3
UPDATE reactor_details SET architect_engineer = 'Atomenergoproekt' WHERE reactor_id = 722 AND (architect_engineer IS NULL);  -- Akkuyu 3
UPDATE reactor_details SET turbine_supplier = 'GE Steam Power' WHERE reactor_id = 722 AND (turbine_supplier IS NULL);  -- Akkuyu 3
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 722 AND (pressure_vessel_manufacturer = 'Izhora Plants');  -- Akkuyu 3
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 723 AND (containment_type IS NULL);  -- Akkuyu 4
UPDATE reactor_details SET architect_engineer = 'Atomenergoproekt' WHERE reactor_id = 723 AND (architect_engineer IS NULL);  -- Akkuyu 4
UPDATE reactor_details SET turbine_supplier = 'GE Steam Power' WHERE reactor_id = 723 AND (turbine_supplier IS NULL);  -- Akkuyu 4
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 723 AND (pressure_vessel_manufacturer = 'Izhora Plants');  -- Akkuyu 4
UPDATE reactor_details SET architect_engineer = 'Atomenergoproekt' WHERE reactor_id = 392 AND (architect_engineer IS NULL);  -- Novovoronezh 2 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Izhora Plants' WHERE reactor_id = 392 AND (pressure_vessel_manufacturer IS NULL);  -- Novovoronezh 2 1
UPDATE reactor_details SET architect_engineer = 'Atomenergoproekt' WHERE reactor_id = 393 AND (architect_engineer IS NULL);  -- Novovoronezh 2 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Izhora Plants' WHERE reactor_id = 393 AND (pressure_vessel_manufacturer IS NULL);  -- Novovoronezh 2 2
UPDATE reactors SET licensed_until = '2028' WHERE id = 551 AND (licensed_until IS NULL);  -- Zaporizhzhia 4
UPDATE reactors SET licensed_until = '2030' WHERE id = 552 AND (licensed_until IS NULL);  -- Zaporizhzhia 5
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 403 AND (containment_type IS NULL);  -- Bohunice 3
UPDATE reactors SET containment_type = 'Pressure Suppression' WHERE id = 404 AND (containment_type IS NULL);  -- Bohunice 4
COMMIT;
