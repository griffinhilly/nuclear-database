-- 036_phase2_wave3.sql
-- Date: 2026-10-14 (approved by Griffin 2026-10-15; applied 2026-10-15)
-- Description: Phase 2 fleet audit, wave 3. Three tiers per batch: 3 Haiku researchers -> Sonnet
--   adjudication -> Opus refutation with an independent second source. Only Opus-UPHELD changes are written;
--   values mapped to existing house spellings. Each UPDATE is guarded on the old value.
--   Per-change sources and quotes: audit/phase2/wave3_changes.psv (local).
-- Writes: 122. Skipped: 64 (see audit/phase2/wave3_skipped.psv).
-- Vendor values are appended to the whitelist (verification_2026-07/final_verdicts.psv) in the same change.
-- Backup: nuclear_reactors.db.bak-pre036-<date>

BEGIN TRANSACTION;
UPDATE reactors SET planned_retirement = NULL WHERE id = 440 AND (planned_retirement = '2026');  -- Wolsong 2
UPDATE reactor_details SET constructor = 'Daewoo E&C' WHERE reactor_id = 441 AND (constructor IS NULL);  -- Wolsong 3
UPDATE reactor_details SET constructor = 'Daewoo E&C' WHERE reactor_id = 442 AND (constructor IS NULL);  -- Wolsong 4
UPDATE reactor_details SET architect_engineer = 'Ebasco' WHERE reactor_id = 274 AND (architect_engineer IS NULL);  -- Fukushima-Daiichi 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'IHI' WHERE reactor_id = 274 AND (pressure_vessel_manufacturer IS NULL);  -- Fukushima-Daiichi 1
UPDATE reactor_details SET architect_engineer = 'Ebasco' WHERE reactor_id = 275 AND (architect_engineer IS NULL);  -- Fukushima-Daiichi 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'IHI' WHERE reactor_id = 276 AND (pressure_vessel_manufacturer IS NULL);  -- Fukushima-Daiichi 3
UPDATE reactor_details SET architect_engineer = 'Ebasco' WHERE reactor_id = 279 AND (architect_engineer IS NULL);  -- Fukushima-Daiichi 6
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 102 AND (containment_type IS NULL);  -- Tianwan 1
UPDATE reactor_details SET architect_engineer = 'Atomproekt' WHERE reactor_id = 102 AND (architect_engineer IS NULL);  -- Tianwan 1
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 103 AND (containment_type IS NULL);  -- Tianwan 2
UPDATE reactor_details SET architect_engineer = 'Atomproekt' WHERE reactor_id = 103 AND (architect_engineer IS NULL);  -- Tianwan 2
UPDATE reactors SET licensed_until = '2060' WHERE id = 106 AND (licensed_until IS NULL);  -- Tianwan 5
UPDATE reactors SET licensed_until = '2061' WHERE id = 107 AND (licensed_until IS NULL);  -- Tianwan 6
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 707 AND (containment_type IS NULL);  -- Tianwan 7
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 707 AND (pressure_vessel_manufacturer IS NULL);  -- Tianwan 7
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 708 AND (containment_type IS NULL);  -- Tianwan 8
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 708 AND (pressure_vessel_manufacturer IS NULL);  -- Tianwan 8
UPDATE reactors SET licensed_until = '2030' WHERE id = 342 AND (licensed_until IS NULL);  -- Chashma 1
UPDATE reactor_details SET constructor = 'China Zhongyuan Engineering' WHERE reactor_id = 343 AND (constructor IS NULL);  -- Chashma 2
UPDATE reactors SET licensed_until = '2031' WHERE id = 343 AND (licensed_until IS NULL);  -- Chashma 2
UPDATE reactor_details SET constructor = 'China Zhongyuan Engineering' WHERE reactor_id = 344 AND (constructor IS NULL);  -- Chashma 3
UPDATE reactor_details SET constructor = 'China Zhongyuan Engineering' WHERE reactor_id = 345 AND (constructor IS NULL);  -- Chashma 4
UPDATE reactor_details SET constructor = 'China Zhongyuan Engineering' WHERE reactor_id = 728 AND (constructor IS NULL);  -- Chashma 5
UPDATE reactors SET licensed_until = '2054' WHERE id = 66 AND (licensed_until IS NULL);  -- Fuqing 1
UPDATE reactors SET licensed_until = '2055' WHERE id = 67 AND (licensed_until IS NULL);  -- Fuqing 2
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 431 AND (constructor IS NULL);  -- Shin-Kori 1
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 432 AND (constructor IS NULL);  -- Shin-Kori 2
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 433 AND (constructor IS NULL);  -- Shin-Kori 3
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 434 AND (constructor IS NULL);  -- Shin-Kori 4
UPDATE reactor_details SET constructor = 'Samsung C&T / Doosan Enerbility / Hanwha E&C' WHERE reactor_id = 435 AND (constructor IS NULL);  -- Shin-Kori 5
UPDATE reactor_details SET constructor = 'Samsung C&T / Doosan Enerbility / Hanwha E&C' WHERE reactor_id = 436 AND (constructor IS NULL);  -- Shin-Kori 6
UPDATE reactor_details SET turbine_supplier = 'BHEL' WHERE reactor_id = 238 AND (turbine_supplier IS NULL);  -- Kaiga 1
UPDATE reactors SET licensed_until = '2053' WHERE id = 108 AND (licensed_until IS NULL);  -- Yangjiang 1
UPDATE reactor_details SET turbine_supplier = 'BHEL' WHERE reactor_id = 254 AND (turbine_supplier IS NULL);  -- PFBR 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Larsen & Toubro' WHERE reactor_id = 254 AND (pressure_vessel_manufacturer IS NULL);  -- PFBR 1
UPDATE reactor_details SET turbine_supplier = 'Alstom-BHEL' WHERE reactor_id = 261 AND (turbine_supplier IS NULL);  -- Rajasthan 7
UPDATE reactor_details SET turbine_supplier = 'Alstom-BHEL' WHERE reactor_id = 262 AND (turbine_supplier IS NULL);  -- Rajasthan 8
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Shanghai Electric' WHERE reactor_id = 56 AND (pressure_vessel_manufacturer IS NULL);  -- Changjiang 1
UPDATE reactor_details SET architect_engineer = 'CGN Engineering Design' WHERE reactor_id = 75 AND (architect_engineer IS NULL);  -- Hongyanhe 2
UPDATE reactors SET licensed_until = '2053' WHERE id = 75 AND (licensed_until IS NULL);  -- Hongyanhe 2
UPDATE reactor_details SET architect_engineer = 'CGN Engineering Design' WHERE reactor_id = 76 AND (architect_engineer IS NULL);  -- Hongyanhe 3
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 78 AND (containment_type IS NULL);  -- Hongyanhe 5
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 79 AND (containment_type IS NULL);  -- Hongyanhe 6
UPDATE reactor_details SET pressure_vessel_manufacturer = 'China First Heavy Industries' WHERE reactor_id = 114 AND (pressure_vessel_manufacturer IS NULL);  -- Zhangzhou 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'China First Heavy Industries' WHERE reactor_id = 115 AND (pressure_vessel_manufacturer IS NULL);  -- Zhangzhou 2
UPDATE reactor_details SET turbine_supplier = 'Alstom / Dongfang Electric' WHERE reactor_id = 82 AND (turbine_supplier = 'Dongfang Electric');  -- Ling Ao 3
UPDATE reactor_details SET turbine_supplier = 'Alstom / Dongfang Electric' WHERE reactor_id = 83 AND (turbine_supplier = 'Dongfang Electric');  -- Ling Ao 4
UPDATE reactor_details SET turbine_supplier = 'Alstom-BHEL' WHERE reactor_id = 244 AND (turbine_supplier IS NULL);  -- Kakrapar 3
UPDATE reactor_details SET turbine_supplier = 'Alstom-BHEL' WHERE reactor_id = 245 AND (turbine_supplier IS NULL);  -- Kakrapar 4
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 247 AND (containment_type IS NULL);  -- Kudankulam 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Izhora Plants' WHERE reactor_id = 248 AND (pressure_vessel_manufacturer IS NULL);  -- Kudankulam 3
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 249 AND (containment_type IS NULL);  -- Kudankulam 4
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 724 AND (containment_type IS NULL);  -- Kudankulam 5
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 724 AND (pressure_vessel_manufacturer IS NULL);  -- Kudankulam 5
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 725 AND (containment_type IS NULL);  -- Kudankulam 6
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 725 AND (pressure_vessel_manufacturer IS NULL);  -- Kudankulam 6
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 317 AND (turbine_supplier = 'Siemens');  -- Sendai 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 318 AND (turbine_supplier = 'Siemens');  -- Sendai 2
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 331 AND (containment_type = 'Large Dry');  -- Tomari 2
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 332 AND (containment_type = 'Large Dry');  -- Tomari 3
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 745 AND (cooling_type = 'Once-through (seawater)');  -- Zhaoyuan 1
UPDATE reactors SET containment_type = 'Mark I' WHERE id = 315 AND (containment_type = 'Mark II');  -- Onagawa 2
UPDATE reactors SET containment_type = 'Mark I' WHERE id = 316 AND (containment_type = 'Mark II');  -- Onagawa 3
UPDATE reactor_details SET constructor = 'Toshiba / Hitachi' WHERE reactor_id = 316 AND (constructor = 'Toshiba');  -- Onagawa 3
UPDATE reactors SET containment_type = 'Large Dry (Double)' WHERE id = 731 AND (containment_type IS NULL);  -- Shidaowan 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'China First Heavy Industries' WHERE reactor_id = 87 AND (pressure_vessel_manufacturer IS NULL);  -- Ningde 4
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 739 AND (constructor IS NULL);  -- Shin-Hanul (Shin-Ulchin) 3
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 746 AND (constructor IS NULL);  -- Shin-Hanul (Shin-Ulchin) 4
UPDATE reactor_details SET architect_engineer = 'KEPCO E&C' WHERE reactor_id = 746 AND (architect_engineer IS NULL);  -- Shin-Hanul (Shin-Ulchin) 4
UPDATE reactor_details SET turbine_supplier = 'Doosan Heavy Industries' WHERE reactor_id = 746 AND (turbine_supplier = 'Doosan Heavy Industries / General Electric');  -- Shin-Hanul (Shin-Ulchin) 4
UPDATE reactors SET licensed_until = '2055' WHERE id = 60 AND (licensed_until IS NULL);  -- Fangchenggang 1
UPDATE reactors SET licensed_until = '2056' WHERE id = 61 AND (licensed_until IS NULL);  -- Fangchenggang 2
UPDATE reactor_details SET architect_engineer = 'Hitachi' WHERE reactor_id = 301 AND (architect_engineer IS NULL);  -- Kashiwazaki Kariwa 4
UPDATE reactor_details SET architect_engineer = 'Hitachi' WHERE reactor_id = 302 AND (architect_engineer IS NULL);  -- Kashiwazaki Kariwa 5
UPDATE reactor_details SET architect_engineer = 'Kansai Electric / Gilbert Associates' WHERE reactor_id = 324 AND (architect_engineer IS NULL);  -- Takahama 1
UPDATE reactor_details SET architect_engineer = 'Kansai Electric / Mitsubishi Atomic Power Industries' WHERE reactor_id = 325 AND (architect_engineer = 'Mitsubishi Heavy Industries');  -- Takahama 2
UPDATE reactors SET licensed_until = '2035' WHERE id = 325 AND (licensed_until IS NULL);  -- Takahama 2
UPDATE reactors SET licensed_until = '2045' WHERE id = 326 AND (licensed_until IS NULL);  -- Takahama 3
UPDATE reactors SET licensed_until = '2033' WHERE id = 426 AND (licensed_until IS NULL);  -- Kori 2
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 427 AND (constructor IS NULL);  -- Kori 3
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 428 AND (constructor IS NULL);  -- Kori 4
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 428 AND (architect_engineer IS NULL);  -- Kori 4
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Shanghai Electric' WHERE reactor_id = 73 AND (pressure_vessel_manufacturer IS NULL);  -- Haiyang 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'China First Heavy Industries' WHERE reactor_id = 695 AND (pressure_vessel_manufacturer IS NULL);  -- Haiyang 3
UPDATE reactor_details SET pressure_vessel_manufacturer = 'China First Heavy Industries' WHERE reactor_id = 96 AND (pressure_vessel_manufacturer IS NULL);  -- Sanmen 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 705 AND (pressure_vessel_manufacturer IS NULL);  -- Xudabao 3
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Atommash' WHERE reactor_id = 706 AND (pressure_vessel_manufacturer IS NULL);  -- Xudabao 4
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 413 AND (constructor IS NULL);  -- Hanbit (Yonggwang) 1
UPDATE reactors SET design_series = 'W 3-Loop' WHERE id = 413 AND (design_series = 'W 2-Loop');  -- Hanbit (Yonggwang) 1
UPDATE reactors SET licensed_until = '2025' WHERE id = 413 AND (licensed_until IS NULL);  -- Hanbit (Yonggwang) 1
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 414 AND (constructor IS NULL);  -- Hanbit (Yonggwang) 2
UPDATE reactors SET design_series = 'W 3-Loop' WHERE id = 414 AND (design_series = 'W 2-Loop');  -- Hanbit (Yonggwang) 2
UPDATE reactors SET licensed_until = '2026' WHERE id = 414 AND (licensed_until IS NULL);  -- Hanbit (Yonggwang) 2
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 415 AND (constructor IS NULL);  -- Hanbit (Yonggwang) 3
UPDATE reactor_details SET constructor = 'Hyundai E&C' WHERE reactor_id = 416 AND (constructor IS NULL);  -- Hanbit (Yonggwang) 4
UPDATE reactor_details SET constructor = 'Hyundai E&C / Daelim' WHERE reactor_id = 417 AND (constructor IS NULL);  -- Hanbit (Yonggwang) 5
UPDATE reactor_details SET constructor = 'Hyundai E&C / Daelim' WHERE reactor_id = 418 AND (constructor IS NULL);  -- Hanbit (Yonggwang) 6
UPDATE reactors SET containment_type = 'Mark I' WHERE id = 319 AND (containment_type = 'Mark II');  -- Shika 1
UPDATE reactor_details SET turbine_supplier = 'BHEL' WHERE reactor_id = 265 AND (turbine_supplier IS NULL);  -- Tarapur 3
UPDATE reactor_details SET turbine_supplier = 'BHEL' WHERE reactor_id = 266 AND (turbine_supplier IS NULL);  -- Tarapur 4
UPDATE reactor_details SET constructor = 'Toshiba' WHERE reactor_id = 288 AND (constructor IS NULL);  -- Hamaoka 1
UPDATE reactors SET containment_type = 'Mark I' WHERE id = 290 AND (containment_type = 'Mark II');  -- Hamaoka 3
UPDATE reactor_details SET architect_engineer = 'Hitachi' WHERE reactor_id = 321 AND (architect_engineer IS NULL);  -- Shimane 1
UPDATE reactors SET containment_type = 'Mark I' WHERE id = 322 AND (containment_type = 'Mark II');  -- Shimane 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Babcock-Hitachi' WHERE reactor_id = 323 AND (pressure_vessel_manufacturer IS NULL);  -- Shimane 3
UPDATE reactors SET containment_type = 'Ice Condenser' WHERE id = 309 AND (containment_type IS NULL);  -- Ohi 1
UPDATE reactors SET containment_type = 'Ice Condenser' WHERE id = 310 AND (containment_type IS NULL);  -- Ohi 2
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 311 AND (containment_type IS NULL);  -- Ohi 3
UPDATE reactors SET licensed_until = '2031' WHERE id = 311 AND (licensed_until IS NULL);  -- Ohi 3
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 312 AND (containment_type IS NULL);  -- Ohi 4
UPDATE reactors SET licensed_until = '2033' WHERE id = 312 AND (licensed_until IS NULL);  -- Ohi 4
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 711 AND (cooling_type = 'Once-through (seawater)');  -- Lianjiang 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Shanghai Electric' WHERE reactor_id = 711 AND (pressure_vessel_manufacturer IS NULL);  -- Lianjiang 1
UPDATE reactor_details SET cooling_type = 'Cooling tower (natural draft)' WHERE reactor_id = 712 AND (cooling_type = 'Once-through (seawater)');  -- Lianjiang 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'China First Heavy Industries' WHERE reactor_id = 691 AND (pressure_vessel_manufacturer IS NULL);  -- Linglong 1
UPDATE reactor_details SET constructor = 'Dong-Ah Construction' WHERE reactor_id = 421 AND (constructor IS NULL);  -- Hanul (Ulchin) 3
UPDATE reactor_details SET constructor = 'Dong-Ah Construction' WHERE reactor_id = 422 AND (constructor IS NULL);  -- Hanul (Ulchin) 4
UPDATE reactor_details SET constructor = 'Mitsubishi Heavy Industries' WHERE reactor_id = 296 AND (constructor IS NULL);  -- Ikata 3
UPDATE reactors SET licensed_until = '2041' WHERE id = 88 AND (licensed_until IS NULL);  -- Qinshan 1 1
UPDATE reactor_details SET constructor = 'Westinghouse / Mitsubishi Atomic Power Industries' WHERE reactor_id = 305 AND (constructor IS NULL);  -- Mihama 1
UPDATE reactor_details SET constructor = 'Mitsubishi Atomic Power Industries' WHERE reactor_id = 306 AND (constructor IS NULL);  -- Mihama 2
COMMIT;
