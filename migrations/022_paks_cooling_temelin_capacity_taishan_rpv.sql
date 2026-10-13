-- 022_paks_cooling_temelin_capacity_taishan_rpv.sql
-- Date: 2026-10-13
-- Description: Three sourced fixes found by the Nucleopedia spot check
--   (review/2026-10-13-nucleopedia-spotcheck.html), each confirmed on a primary source.
--   (1) Paks 1-5 cooling: natural-draft tower -> once-through river (Danube). The
--       per-plant cooling assignment never covered Hungary (July audit was US-only).
--       Sources: Periodica Polytechnica (BME) 1991 cooling-system paper, pp.bme.hu/ci/article/download/3869/2974/7627
--       ("fresh-water cooled ... returned to the Danube"); Paks II EIA clarification, paks2.hu
--       ("will be cooled by the water of the Danube, as is the case with the existing plant").
--   (2) Temelin 1/2 capacity: net 1086 was the gross figure (net > gross 1080 in the DB).
--       Source: IAEA PRIS API (pris-stats.iaea.org/reactor/reactor-by-id/74 and /75, fetched
--       2026-10-13): gross 1086 / net 1027 (unit 1), gross 1086 / net 1029 (unit 2), RUP basis Net.
--   (3) Taishan 1/2 RPV maker: July audit wrongly marked MHI as WRONG -> "Framatome" (designer
--       vs fabricator confusion). Source: World Nuclear News, "Construction milestone at Taishan 2
--       EPR" ("the pressure vessel from Mitsubishi Heavy Industries (MHI) of Japan" / "the
--       pressure vessel by Dongfang Electric Co (DEC)"); corroborated by Power Technology and
--       Nucleopedia. Whitelisted in verification_2026-07/final_verdicts.psv in the same change.
-- Affected tables: reactor_details (5 cooling_type + 2 pressure_vessel_manufacturer), reactors (2 rows)
-- Backup: nuclear_reactors.db.bak-pre022-20261013

BEGIN TRANSACTION;

UPDATE reactor_details SET cooling_type = 'Once-through (river)'
 WHERE reactor_id IN (SELECT id FROM reactors WHERE plant_name = 'Paks' AND unit_number IN ('1','2','3','4','5'));

UPDATE reactors SET gross_capacity_mw = 1086, net_capacity_mw = 1027, reference_power_mw = 1027,
       updated_at = CURRENT_TIMESTAMP
 WHERE plant_name = 'Temelin' AND unit_number = '1';
UPDATE reactors SET gross_capacity_mw = 1086, net_capacity_mw = 1029, reference_power_mw = 1029,
       updated_at = CURRENT_TIMESTAMP
 WHERE plant_name = 'Temelin' AND unit_number = '2';

UPDATE reactor_details SET pressure_vessel_manufacturer = 'Mitsubishi Heavy Industries'
 WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Taishan' AND unit_number = '1');
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Dongfang Electric'
 WHERE reactor_id = (SELECT id FROM reactors WHERE plant_name = 'Taishan' AND unit_number = '2');

COMMIT;
