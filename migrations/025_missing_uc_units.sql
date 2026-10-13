-- 025_missing_uc_units.sql
-- Date: 2026-10-13
-- Description: Audit batch D. Five units IAEA PRIS lists as Under Construction that the DB lacked
--   (Jinqimen 2, Xuwei 1, Zhaoyuan 1) or still held as planned (Taipingling 4, Shin-Hanul 4).
--   Xuwei 1 and Zhaoyuan 1 were dropped from planned in March 2026 as "already under construction"
--   but never added to reactors. Bushehr 3 is NOT here: PRIS says UC since 2024-04-25, which
--   conflicts with the May 2026 decision (WNA: no first concrete) -> audit batch C research.
-- Sources: IAEA PRIS API (pris-stats.iaea.org/reactor/reactors-by-code/CN, /KR; pulled 2026-10-13):
--   ids, construction dates, capacities, PRIS turbine supplier. Wikipedia GeoData (MediaWiki API
--   prop=coordinates) for the two new sites: Xuwei 34.625076, 119.508261; Zhaoyuan 37.4871, 120.3453.
--   Zhaoyuan owner + cooling (Bohai Sea, no towers): Wikipedia infobox. Existing-site units take the
--   site's coordinates, model, series and containment from their sibling units (same design, same phase).
-- Data notes: Xuwei 1 net left NULL — PRIS net 729 vs gross 1208 fails the net/gross guard (possibly a
--   cogeneration rating; unverified). Taipingling 4 PRIS net = gross (1209) -> net taken as NULL too.
--   Xuwei cooling NULL (no source). Owners in house short form where the site already has one.
-- Affected: reactors INSERT 5; reactor_details INSERT 5; planned_reactors DELETE 2 (Taipingling 4,
--   Shin Hanul 4); turbine suppliers whitelisted in final_verdicts.psv in the same change.
-- Backup: nuclear_reactors.db.bak-pre025-20261013

BEGIN TRANSACTION;

INSERT INTO reactors (plant_name, unit_number, reactor_id, pris_id, country_id, latitude, longitude, technology_id,
    model_id, design_series, containment_type, supplier_id, owner, operator, status, construction_start,
    thermal_capacity_mw, gross_capacity_mw, net_capacity_mw, reference_power_mw, notes, created_at, updated_at)
VALUES
 ('Jinqimen', '2', 'Jinqimen_2_China', 2208, 9, 29.0564, 121.9448, 2, 30, 'HPR1000', 'Large Dry (Double)', 13,
  'CNNC', 'CNNC (Xiangshan) Nuclear Energy Co., Ltd.', 'Under Construction', '2026-04-04', 3190, 1230, 1145, 1145,
  'Added 2026-10 audit from IAEA PRIS (id 2208).', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
 ('Taipingling', '4', 'Taipingling_4_China', 2143, 9, 22.69444444, 114.98333333, 2, 30, 'HPR1000', 'Large Dry (Double)', NULL,
  'CGN', 'CGN Huizhou Second Nuclear Power Co., Ltd', 'Under Construction', '2026-05-10', 3180, 1209, NULL, NULL,
  'Added 2026-10 audit from IAEA PRIS (id 2143); moved from planned. PRIS net = gross (1209), net left NULL.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
 ('Xuwei', '1', 'Xuwei_1_China', 2170, 9, 34.625076, 119.508261, 2, 30, 'HPR1000', 'Large Dry (Double)', 13,
  'CNNC', 'CNNC SuNeng Nuclear Power Co., Ltd.', 'Under Construction', '2026-01-16', 3190, 1208, NULL, NULL,
  'Added 2026-10 audit from IAEA PRIS (id 2170). PRIS net 729 vs gross 1208 unverified (cogeneration?); net left NULL.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
 ('Zhaoyuan', '1', 'Zhaoyuan_1_China', 2171, 9, 37.4871, 120.3453, 2, 30, 'HPR1000', 'Large Dry (Double)', NULL,
  'Shandong Zhaoyuan NPC', NULL, 'Under Construction', '2025-11-18', 3190, 1214, 1117, 1117,
  'Added 2026-10 audit from IAEA PRIS (id 2171); owner from Wikipedia infobox.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
 ('Shin-Hanul (Shin-Ulchin)', '4', 'Shin-Hanul (Shin-Ulchin)_4_South Korea', 2207, 29, 37.09277778, 129.38361111, 2, 105, 'APR1400', 'Large Dry', 30,
  'Korea Hydro and Nuclear Power Co', 'Korea Hydro and Nuclear Power Co.', 'Under Construction', '2026-05-29', 3983, 1400, 1340, 1340,
  'Added 2026-10 audit from IAEA PRIS (id 2207); moved from planned.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO reactor_details (reactor_id, cooling_type, turbine_supplier)
SELECT id,
       CASE WHEN plant_name = 'Xuwei' THEN NULL ELSE 'Once-through (seawater)' END,
       CASE plant_name WHEN 'Jinqimen' THEN 'Dongfang Electric'
                       WHEN 'Shin-Hanul (Shin-Ulchin)' THEN 'Doosan Heavy Industries / General Electric'
                       ELSE 'Harbin Electric' END
FROM reactors WHERE pris_id IN (2208, 2143, 2170, 2171, 2207);

DELETE FROM planned_reactors WHERE project_name = 'Taipingling' AND unit_number = '4';
DELETE FROM planned_reactors WHERE project_name = 'Shin Hanul' AND unit_number = '4';

COMMIT;
