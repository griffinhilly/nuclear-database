-- 024_pris_capacity_dates.sql
-- Date: 2026-10-13
-- Description: Audit batch B: adopt PRIS where we differ (guarded).
--   Non-US gross/thermal/net(=reference) on reactors WITHOUT capacity_changes history, each passing
--   net/gross (>=0.85, >=0.70 gas/graphite/fast) and gross/thermal (0.27-0.40 LWR/PHWR) guards.
--   Dates: PRIS adopted when within 31 days or replacing a 1-January placeholder; all countries.
--   Everything else went to the research list (audit/batch_c_items.tsv).
-- Source: IAEA PRIS API (pris-stats.iaea.org), pulled 2026-10-13. Built by scripts/audit_build_batches.py from audit/pris_diff.tsv.
-- Rows: 230 reactors. Backup: nuclear_reactors.db.bak-pre024-20261013

BEGIN TRANSACTION;
UPDATE reactors SET net_capacity_mw = 335, reference_power_mw = 335, construction_start = '1968-05-31', updated_at = CURRENT_TIMESTAMP WHERE id = 1;  -- Atucha 1
UPDATE reactors SET gross_capacity_mw = 740, net_capacity_mw = 688, reference_power_mw = 688, construction_start = '1981-07-09', grid_connection = '2014-06-23', commercial_operation = '2016-05-22', updated_at = CURRENT_TIMESTAMP WHERE id = 2;  -- Atucha 2
UPDATE reactors SET gross_capacity_mw = 656, thermal_capacity_mw = 2064, net_capacity_mw = 608, reference_power_mw = 608, construction_start = '1974-03-31', updated_at = CURRENT_TIMESTAMP WHERE id = 4;  -- Embalse 1
UPDATE reactors SET gross_capacity_mw = 448, updated_at = CURRENT_TIMESTAMP WHERE id = 6;  -- Armenian 2
UPDATE reactors SET net_capacity_mw = 1030, reference_power_mw = 1030, updated_at = CURRENT_TIMESTAMP WHERE id = 18;  -- Tihange 3
UPDATE reactors SET net_capacity_mw = 609, reference_power_mw = 609, updated_at = CURRENT_TIMESTAMP WHERE id = 19;  -- Angra 1
UPDATE reactors SET gross_capacity_mw = 1040, thermal_capacity_mw = 3120, updated_at = CURRENT_TIMESTAMP WHERE id = 26;  -- Kozloduy 5
UPDATE reactors SET gross_capacity_mw = 1040, thermal_capacity_mw = 3120, updated_at = CURRENT_TIMESTAMP WHERE id = 27;  -- Kozloduy 6
UPDATE reactors SET gross_capacity_mw = 865, thermal_capacity_mw = 2550, net_capacity_mw = 770, reference_power_mw = 770, updated_at = CURRENT_TIMESTAMP WHERE id = 30;  -- Bruce 3
UPDATE reactors SET gross_capacity_mw = 865, thermal_capacity_mw = 2550, updated_at = CURRENT_TIMESTAMP WHERE id = 31;  -- Bruce 4
UPDATE reactors SET net_capacity_mw = 817, reference_power_mw = 817, construction_start = '1978-05-31', grid_connection = '1984-12-01', commercial_operation = '1985-02-28', updated_at = CURRENT_TIMESTAMP WHERE id = 32;  -- Bruce 5
UPDATE reactors SET net_capacity_mw = 817, reference_power_mw = 817, updated_at = CURRENT_TIMESTAMP WHERE id = 34;  -- Bruce 7
UPDATE reactors SET construction_start = '1979-07-30', grid_connection = '1987-03-07', commercial_operation = '1987-05-20', updated_at = CURRENT_TIMESTAMP WHERE id = 35;  -- Bruce 8
UPDATE reactors SET net_capacity_mw = 878, reference_power_mw = 878, updated_at = CURRENT_TIMESTAMP WHERE id = 36;  -- Darlington 1
UPDATE reactors SET net_capacity_mw = 878, reference_power_mw = 878, updated_at = CURRENT_TIMESTAMP WHERE id = 37;  -- Darlington 2
UPDATE reactors SET net_capacity_mw = 878, reference_power_mw = 878, updated_at = CURRENT_TIMESTAMP WHERE id = 38;  -- Darlington 3
UPDATE reactors SET net_capacity_mw = 878, reference_power_mw = 878, updated_at = CURRENT_TIMESTAMP WHERE id = 39;  -- Darlington 4
UPDATE reactors SET permanent_shutdown = '2024-10-01', updated_at = CURRENT_TIMESTAMP WHERE id = 43;  -- Pickering 1
UPDATE reactors SET net_capacity_mw = 601, reference_power_mw = 601, updated_at = CURRENT_TIMESTAMP WHERE id = 56;  -- Changjiang 1
UPDATE reactors SET net_capacity_mw = 601, reference_power_mw = 601, updated_at = CURRENT_TIMESTAMP WHERE id = 57;  -- Changjiang 2
UPDATE reactors SET gross_capacity_mw = 1026, net_capacity_mw = 986, reference_power_mw = 986, updated_at = CURRENT_TIMESTAMP WHERE id = 58;  -- Daya Bay 1
UPDATE reactors SET gross_capacity_mw = 1026, net_capacity_mw = 986, reference_power_mw = 986, updated_at = CURRENT_TIMESTAMP WHERE id = 59;  -- Daya Bay 2
UPDATE reactors SET gross_capacity_mw = 1086, updated_at = CURRENT_TIMESTAMP WHERE id = 60;  -- Fangchenggang 1
UPDATE reactors SET gross_capacity_mw = 1086, updated_at = CURRENT_TIMESTAMP WHERE id = 61;  -- Fangchenggang 2
UPDATE reactors SET gross_capacity_mw = 1180, construction_start = '2015-12-24', updated_at = CURRENT_TIMESTAMP WHERE id = 62;  -- Fangchenggang 3
UPDATE reactors SET gross_capacity_mw = 1180, construction_start = '2016-12-23', updated_at = CURRENT_TIMESTAMP WHERE id = 63;  -- Fangchenggang 4
UPDATE reactors SET gross_capacity_mw = 1089, updated_at = CURRENT_TIMESTAMP WHERE id = 64;  -- Fangjiashan 1
UPDATE reactors SET gross_capacity_mw = 1089, updated_at = CURRENT_TIMESTAMP WHERE id = 65;  -- Fangjiashan 2
UPDATE reactors SET gross_capacity_mw = 1089, updated_at = CURRENT_TIMESTAMP WHERE id = 66;  -- Fuqing 1
UPDATE reactors SET gross_capacity_mw = 1089, updated_at = CURRENT_TIMESTAMP WHERE id = 67;  -- Fuqing 2
UPDATE reactors SET gross_capacity_mw = 1089, updated_at = CURRENT_TIMESTAMP WHERE id = 68;  -- Fuqing 3
UPDATE reactors SET gross_capacity_mw = 1089, updated_at = CURRENT_TIMESTAMP WHERE id = 69;  -- Fuqing 4
UPDATE reactors SET gross_capacity_mw = 1161, thermal_capacity_mw = 3050, net_capacity_mw = 1075, reference_power_mw = 1075, updated_at = CURRENT_TIMESTAMP WHERE id = 70;  -- Fuqing 5
UPDATE reactors SET gross_capacity_mw = 1150, thermal_capacity_mw = 3060, net_capacity_mw = 1075, reference_power_mw = 1075, updated_at = CURRENT_TIMESTAMP WHERE id = 71;  -- Fuqing 6
UPDATE reactors SET gross_capacity_mw = 1119, net_capacity_mw = 1061, reference_power_mw = 1061, updated_at = CURRENT_TIMESTAMP WHERE id = 77;  -- Hongyanhe 4
UPDATE reactors SET gross_capacity_mw = 1119, net_capacity_mw = 1061, reference_power_mw = 1061, updated_at = CURRENT_TIMESTAMP WHERE id = 78;  -- Hongyanhe 5
UPDATE reactors SET gross_capacity_mw = 1119, net_capacity_mw = 1061, reference_power_mw = 1061, updated_at = CURRENT_TIMESTAMP WHERE id = 79;  -- Hongyanhe 6
UPDATE reactors SET gross_capacity_mw = 1086, updated_at = CURRENT_TIMESTAMP WHERE id = 82;  -- Ling Ao 3
UPDATE reactors SET gross_capacity_mw = 1086, updated_at = CURRENT_TIMESTAMP WHERE id = 83;  -- Ling Ao 4
UPDATE reactors SET gross_capacity_mw = 330, net_capacity_mw = 326, reference_power_mw = 326, updated_at = CURRENT_TIMESTAMP WHERE id = 88;  -- Qinshan 1 1
UPDATE reactors SET gross_capacity_mw = 670, net_capacity_mw = 623, reference_power_mw = 623, updated_at = CURRENT_TIMESTAMP WHERE id = 89;  -- Qinshan 2 1
UPDATE reactors SET gross_capacity_mw = 708, net_capacity_mw = 623, reference_power_mw = 623, updated_at = CURRENT_TIMESTAMP WHERE id = 90;  -- Qinshan 2 2
UPDATE reactors SET gross_capacity_mw = 670, net_capacity_mw = 623, reference_power_mw = 623, updated_at = CURRENT_TIMESTAMP WHERE id = 91;  -- Qinshan 2 3
UPDATE reactors SET gross_capacity_mw = 670, net_capacity_mw = 623, reference_power_mw = 623, updated_at = CURRENT_TIMESTAMP WHERE id = 92;  -- Qinshan 2 4
UPDATE reactors SET net_capacity_mw = 150, reference_power_mw = 150, updated_at = CURRENT_TIMESTAMP WHERE id = 97;  -- Shidao Bay 1
UPDATE reactors SET thermal_capacity_mw = 3190, updated_at = CURRENT_TIMESTAMP WHERE id = 98;  -- Taipingling 1
UPDATE reactors SET net_capacity_mw = 1000, reference_power_mw = 1000, updated_at = CURRENT_TIMESTAMP WHERE id = 102;  -- Tianwan 1
UPDATE reactors SET net_capacity_mw = 1000, reference_power_mw = 1000, updated_at = CURRENT_TIMESTAMP WHERE id = 103;  -- Tianwan 2
UPDATE reactors SET gross_capacity_mw = 1126, net_capacity_mw = 1060, reference_power_mw = 1060, updated_at = CURRENT_TIMESTAMP WHERE id = 104;  -- Tianwan 3
UPDATE reactors SET gross_capacity_mw = 1126, net_capacity_mw = 1060, reference_power_mw = 1060, updated_at = CURRENT_TIMESTAMP WHERE id = 105;  -- Tianwan 4
UPDATE reactors SET net_capacity_mw = 1060, reference_power_mw = 1060, updated_at = CURRENT_TIMESTAMP WHERE id = 106;  -- Tianwan 5
UPDATE reactors SET net_capacity_mw = 1060, reference_power_mw = 1060, commercial_operation = '2021-06-02', updated_at = CURRENT_TIMESTAMP WHERE id = 107;  -- Tianwan 6
UPDATE reactors SET net_capacity_mw = 1000, reference_power_mw = 1000, updated_at = CURRENT_TIMESTAMP WHERE id = 108;  -- Yangjiang 1
UPDATE reactors SET gross_capacity_mw = 1086, updated_at = CURRENT_TIMESTAMP WHERE id = 109;  -- Yangjiang 2
UPDATE reactors SET gross_capacity_mw = 1086, updated_at = CURRENT_TIMESTAMP WHERE id = 110;  -- Yangjiang 3
UPDATE reactors SET gross_capacity_mw = 1086, updated_at = CURRENT_TIMESTAMP WHERE id = 111;  -- Yangjiang 4
UPDATE reactors SET thermal_capacity_mw = 3190, net_capacity_mw = 1126, reference_power_mw = 1126, updated_at = CURRENT_TIMESTAMP WHERE id = 114;  -- Zhangzhou 1
UPDATE reactors SET gross_capacity_mw = 511, net_capacity_mw = 479, reference_power_mw = 479, updated_at = CURRENT_TIMESTAMP WHERE id = 116;  -- Dukovany 1
UPDATE reactors SET gross_capacity_mw = 511, net_capacity_mw = 479, reference_power_mw = 479, updated_at = CURRENT_TIMESTAMP WHERE id = 117;  -- Dukovany 2
UPDATE reactors SET gross_capacity_mw = 511, net_capacity_mw = 479, reference_power_mw = 479, updated_at = CURRENT_TIMESTAMP WHERE id = 118;  -- Dukovany 3
UPDATE reactors SET gross_capacity_mw = 511, net_capacity_mw = 479, reference_power_mw = 479, updated_at = CURRENT_TIMESTAMP WHERE id = 119;  -- Dukovany 4
UPDATE reactors SET gross_capacity_mw = 531, construction_start = '1971-05-01', updated_at = CURRENT_TIMESTAMP WHERE id = 122;  -- Loviisa 1
UPDATE reactors SET gross_capacity_mw = 531, updated_at = CURRENT_TIMESTAMP WHERE id = 123;  -- Loviisa 2
UPDATE reactors SET gross_capacity_mw = 920, updated_at = CURRENT_TIMESTAMP WHERE id = 124;  -- Olkiluoto 1
UPDATE reactors SET gross_capacity_mw = 920, updated_at = CURRENT_TIMESTAMP WHERE id = 125;  -- Olkiluoto 2
UPDATE reactors SET gross_capacity_mw = 1660, net_capacity_mw = 1575, reference_power_mw = 1575, commercial_operation = '2023-05-01', updated_at = CURRENT_TIMESTAMP WHERE id = 126;  -- Olkiluoto 3
UPDATE reactors SET net_capacity_mw = 910, reference_power_mw = 910, updated_at = CURRENT_TIMESTAMP WHERE id = 134;  -- Bugey 2
UPDATE reactors SET net_capacity_mw = 910, reference_power_mw = 910, updated_at = CURRENT_TIMESTAMP WHERE id = 135;  -- Bugey 3
UPDATE reactors SET net_capacity_mw = 880, reference_power_mw = 880, commercial_operation = '1979-07-01', updated_at = CURRENT_TIMESTAMP WHERE id = 136;  -- Bugey 4
UPDATE reactors SET net_capacity_mw = 880, reference_power_mw = 880, updated_at = CURRENT_TIMESTAMP WHERE id = 137;  -- Bugey 5
UPDATE reactors SET gross_capacity_mw = 509, updated_at = CURRENT_TIMESTAMP WHERE id = 234;  -- Paks 1
UPDATE reactors SET gross_capacity_mw = 506, updated_at = CURRENT_TIMESTAMP WHERE id = 235;  -- Paks 2
UPDATE reactors SET gross_capacity_mw = 506, updated_at = CURRENT_TIMESTAMP WHERE id = 236;  -- Paks 3
UPDATE reactors SET gross_capacity_mw = 506, updated_at = CURRENT_TIMESTAMP WHERE id = 237;  -- Paks 4
UPDATE reactors SET net_capacity_mw = 932, reference_power_mw = 932, updated_at = CURRENT_TIMESTAMP WHERE id = 246;  -- Kudankulam 1
UPDATE reactors SET net_capacity_mw = 932, reference_power_mw = 932, updated_at = CURRENT_TIMESTAMP WHERE id = 247;  -- Kudankulam 2
UPDATE reactors SET net_capacity_mw = 205, reference_power_mw = 205, updated_at = CURRENT_TIMESTAMP WHERE id = 250;  -- Madras 1
UPDATE reactors SET net_capacity_mw = 205, reference_power_mw = 205, updated_at = CURRENT_TIMESTAMP WHERE id = 251;  -- Madras 2
UPDATE reactors SET net_capacity_mw = 187, reference_power_mw = 187, updated_at = CURRENT_TIMESTAMP WHERE id = 256;  -- Rajasthan 2
UPDATE reactors SET construction_start = '2003-01-20', grid_connection = '2010-03-28', commercial_operation = '2010-03-31', updated_at = CURRENT_TIMESTAMP WHERE id = 260;  -- Rajasthan 6
UPDATE reactors SET grid_connection = '2025-03-17', commercial_operation = '2025-04-15', updated_at = CURRENT_TIMESTAMP WHERE id = 261;  -- Rajasthan 7
UPDATE reactors SET net_capacity_mw = 482, reference_power_mw = 482, updated_at = CURRENT_TIMESTAMP WHERE id = 265;  -- Tarapur 3
UPDATE reactors SET commercial_operation = '2013-09-23', updated_at = CURRENT_TIMESTAMP WHERE id = 267;  -- Bushehr 1
UPDATE reactors SET net_capacity_mw = 777, reference_power_mw = 777, construction_start = '1976-09-27', grid_connection = '1989-04-09', commercial_operation = '1990-07-25', updated_at = CURRENT_TIMESTAMP WHERE id = 338;  -- Laguna Verde 1
UPDATE reactors SET gross_capacity_mw = 803, net_capacity_mw = 775, reference_power_mw = 775, construction_start = '1977-05-31', grid_connection = '1994-11-10', commercial_operation = '1995-04-09', updated_at = CURRENT_TIMESTAMP WHERE id = 339;  -- Laguna Verde 2
UPDATE reactors SET net_capacity_mw = 482, reference_power_mw = 482, updated_at = CURRENT_TIMESTAMP WHERE id = 340;  -- Borssele 1
UPDATE reactors SET net_capacity_mw = 313, reference_power_mw = 313, updated_at = CURRENT_TIMESTAMP WHERE id = 345;  -- Chashma 4
UPDATE reactors SET net_capacity_mw = 1017, reference_power_mw = 1017, commercial_operation = '2021-05-21', updated_at = CURRENT_TIMESTAMP WHERE id = 347;  -- Karachi 2
UPDATE reactors SET net_capacity_mw = 1017, reference_power_mw = 1017, commercial_operation = '2022-04-18', updated_at = CURRENT_TIMESTAMP WHERE id = 348;  -- Karachi 3
UPDATE reactors SET commercial_operation = '2007-11-01', updated_at = CURRENT_TIMESTAMP WHERE id = 350;  -- Cernavodă 2
UPDATE reactors SET construction_start = '1980-12-02', grid_connection = '1985-12-24', updated_at = CURRENT_TIMESTAMP WHERE id = 354;  -- Balakovo 1
UPDATE reactors SET grid_connection = '1988-12-24', updated_at = CURRENT_TIMESTAMP WHERE id = 356;  -- Balakovo 3
UPDATE reactors SET gross_capacity_mw = 885, updated_at = CURRENT_TIMESTAMP WHERE id = 362;  -- Beloyarsk 4
UPDATE reactors SET thermal_capacity_mw = 3120, grid_connection = '1986-12-11', updated_at = CURRENT_TIMESTAMP WHERE id = 368;  -- Kalinin 2
UPDATE reactors SET thermal_capacity_mw = 3120, updated_at = CURRENT_TIMESTAMP WHERE id = 370;  -- Kalinin 4
UPDATE reactors SET grid_connection = '1974-12-08', updated_at = CURRENT_TIMESTAMP WHERE id = 372;  -- Kola 2
UPDATE reactors SET commercial_operation = '1984-12-07', updated_at = CURRENT_TIMESTAMP WHERE id = 374;  -- Kola 4
UPDATE reactors SET permanent_shutdown = '2021-12-19', updated_at = CURRENT_TIMESTAMP WHERE id = 375;  -- Kursk 1 1
UPDATE reactors SET gross_capacity_mw = 1253, net_capacity_mw = 1200, reference_power_mw = 1200, construction_start = '2018-04-28', updated_at = CURRENT_TIMESTAMP WHERE id = 379;  -- Kursk 2 1
UPDATE reactors SET permanent_shutdown = '2018-12-21', updated_at = CURRENT_TIMESTAMP WHERE id = 381;  -- Leningrad 1 1
UPDATE reactors SET gross_capacity_mw = 1188, net_capacity_mw = 1101, reference_power_mw = 1101, commercial_operation = '2018-10-24', updated_at = CURRENT_TIMESTAMP WHERE id = 385;  -- Leningrad 2 1
UPDATE reactors SET gross_capacity_mw = 1188, net_capacity_mw = 1101, reference_power_mw = 1101, commercial_operation = '2021-03-18', updated_at = CURRENT_TIMESTAMP WHERE id = 386;  -- Leningrad 2 2
UPDATE reactors SET commercial_operation = '1964-12-29', updated_at = CURRENT_TIMESTAMP WHERE id = 387;  -- Novovoronezh 1 1
UPDATE reactors SET gross_capacity_mw = 1180, net_capacity_mw = 1100, reference_power_mw = 1100, updated_at = CURRENT_TIMESTAMP WHERE id = 392;  -- Novovoronezh 2 1
UPDATE reactors SET gross_capacity_mw = 1181, net_capacity_mw = 1101, reference_power_mw = 1101, updated_at = CURRENT_TIMESTAMP WHERE id = 393;  -- Novovoronezh 2 2
UPDATE reactors SET thermal_capacity_mw = 3120, updated_at = CURRENT_TIMESTAMP WHERE id = 396;  -- Rostov 3
UPDATE reactors SET gross_capacity_mw = 1030, thermal_capacity_mw = 3120, net_capacity_mw = 979, reference_power_mw = 979, updated_at = CURRENT_TIMESTAMP WHERE id = 397;  -- Rostov 4
UPDATE reactors SET grid_connection = '1985-05-04', commercial_operation = '1985-07-03', updated_at = CURRENT_TIMESTAMP WHERE id = 399;  -- Smolensk 2
UPDATE reactors SET gross_capacity_mw = 500, updated_at = CURRENT_TIMESTAMP WHERE id = 403;  -- Bohunice 3
UPDATE reactors SET gross_capacity_mw = 500, updated_at = CURRENT_TIMESTAMP WHERE id = 404;  -- Bohunice 4
UPDATE reactors SET gross_capacity_mw = 500, updated_at = CURRENT_TIMESTAMP WHERE id = 406;  -- Mochovce 1
UPDATE reactors SET gross_capacity_mw = 500, updated_at = CURRENT_TIMESTAMP WHERE id = 407;  -- Mochovce 2
UPDATE reactors SET net_capacity_mw = 438, reference_power_mw = 438, updated_at = CURRENT_TIMESTAMP WHERE id = 408;  -- Mochovce 3
UPDATE reactors SET gross_capacity_mw = 736, updated_at = CURRENT_TIMESTAMP WHERE id = 410;  -- Krško 1
UPDATE reactors SET gross_capacity_mw = 964, net_capacity_mw = 924, reference_power_mw = 924, updated_at = CURRENT_TIMESTAMP WHERE id = 411;  -- Koeberg 1
UPDATE reactors SET gross_capacity_mw = 1025, updated_at = CURRENT_TIMESTAMP WHERE id = 413;  -- Hanbit (Yonggwang) 1
UPDATE reactors SET gross_capacity_mw = 1024, updated_at = CURRENT_TIMESTAMP WHERE id = 414;  -- Hanbit (Yonggwang) 2
UPDATE reactors SET gross_capacity_mw = 1041, updated_at = CURRENT_TIMESTAMP WHERE id = 415;  -- Hanbit (Yonggwang) 3
UPDATE reactors SET gross_capacity_mw = 1041, net_capacity_mw = 961, reference_power_mw = 961, updated_at = CURRENT_TIMESTAMP WHERE id = 416;  -- Hanbit (Yonggwang) 4
UPDATE reactors SET gross_capacity_mw = 1051, updated_at = CURRENT_TIMESTAMP WHERE id = 417;  -- Hanbit (Yonggwang) 5
UPDATE reactors SET gross_capacity_mw = 1014, thermal_capacity_mw = 2775, updated_at = CURRENT_TIMESTAMP WHERE id = 419;  -- Hanul (Ulchin) 1
UPDATE reactors SET gross_capacity_mw = 1011, updated_at = CURRENT_TIMESTAMP WHERE id = 420;  -- Hanul (Ulchin) 2
UPDATE reactors SET gross_capacity_mw = 1049, thermal_capacity_mw = 2825, updated_at = CURRENT_TIMESTAMP WHERE id = 423;  -- Hanul (Ulchin) 5
UPDATE reactors SET gross_capacity_mw = 1049, updated_at = CURRENT_TIMESTAMP WHERE id = 424;  -- Hanul (Ulchin) 6
UPDATE reactors SET net_capacity_mw = 576, reference_power_mw = 576, updated_at = CURRENT_TIMESTAMP WHERE id = 425;  -- Kori 1
UPDATE reactors SET gross_capacity_mw = 681, updated_at = CURRENT_TIMESTAMP WHERE id = 426;  -- Kori 2
UPDATE reactors SET gross_capacity_mw = 1046, net_capacity_mw = 996, reference_power_mw = 996, updated_at = CURRENT_TIMESTAMP WHERE id = 427;  -- Kori 3
UPDATE reactors SET gross_capacity_mw = 1046, updated_at = CURRENT_TIMESTAMP WHERE id = 428;  -- Kori 4
UPDATE reactors SET gross_capacity_mw = 1455, thermal_capacity_mw = 3983, updated_at = CURRENT_TIMESTAMP WHERE id = 429;  -- Shin-Hanul (Shin-Ulchin) 1
UPDATE reactors SET gross_capacity_mw = 1455, thermal_capacity_mw = 3983, updated_at = CURRENT_TIMESTAMP WHERE id = 430;  -- Shin-Hanul (Shin-Ulchin) 2
UPDATE reactors SET gross_capacity_mw = 1038, net_capacity_mw = 986, reference_power_mw = 986, updated_at = CURRENT_TIMESTAMP WHERE id = 431;  -- Shin-Kori 1
UPDATE reactors SET gross_capacity_mw = 1036, net_capacity_mw = 982, reference_power_mw = 982, updated_at = CURRENT_TIMESTAMP WHERE id = 432;  -- Shin-Kori 2
UPDATE reactors SET gross_capacity_mw = 1488, updated_at = CURRENT_TIMESTAMP WHERE id = 433;  -- Shin-Kori 3
UPDATE reactors SET gross_capacity_mw = 1491, thermal_capacity_mw = 3983, updated_at = CURRENT_TIMESTAMP WHERE id = 434;  -- Shin-Kori 4
UPDATE reactors SET gross_capacity_mw = 1048, updated_at = CURRENT_TIMESTAMP WHERE id = 437;  -- Shin-Wolsong 1
UPDATE reactors SET gross_capacity_mw = 1048, updated_at = CURRENT_TIMESTAMP WHERE id = 438;  -- Shin-Wolsong 2
UPDATE reactors SET thermal_capacity_mw = 2941, updated_at = CURRENT_TIMESTAMP WHERE id = 445;  -- Asco 1
UPDATE reactors SET gross_capacity_mw = 1027, updated_at = CURRENT_TIMESTAMP WHERE id = 446;  -- Asco 2
UPDATE reactors SET gross_capacity_mw = 1142, thermal_capacity_mw = 3234, updated_at = CURRENT_TIMESTAMP WHERE id = 456;  -- Forsmark 1
UPDATE reactors SET gross_capacity_mw = 1160, updated_at = CURRENT_TIMESTAMP WHERE id = 457;  -- Forsmark 2
UPDATE reactors SET gross_capacity_mw = 1208, updated_at = CURRENT_TIMESTAMP WHERE id = 458;  -- Forsmark 3
UPDATE reactors SET gross_capacity_mw = 1141, net_capacity_mw = 1084, reference_power_mw = 1084, updated_at = CURRENT_TIMESTAMP WHERE id = 464;  -- Ringhals 3
UPDATE reactors SET gross_capacity_mw = 1190, thermal_capacity_mw = 3292, net_capacity_mw = 1134, reference_power_mw = 1134, updated_at = CURRENT_TIMESTAMP WHERE id = 465;  -- Ringhals 4
UPDATE reactors SET gross_capacity_mw = 1285, updated_at = CURRENT_TIMESTAMP WHERE id = 469;  -- Leibstadt 1
UPDATE reactors SET gross_capacity_mw = 1417, thermal_capacity_mw = 3983, net_capacity_mw = 1337, reference_power_mw = 1337, updated_at = CURRENT_TIMESTAMP WHERE id = 482;  -- Barakah 1
UPDATE reactors SET gross_capacity_mw = 1417, thermal_capacity_mw = 3983, net_capacity_mw = 1337, reference_power_mw = 1337, construction_start = '2013-04-15', updated_at = CURRENT_TIMESTAMP WHERE id = 483;  -- Barakah 2
UPDATE reactors SET gross_capacity_mw = 1417, thermal_capacity_mw = 3983, net_capacity_mw = 1337, reference_power_mw = 1337, updated_at = CURRENT_TIMESTAMP WHERE id = 484;  -- Barakah 3
UPDATE reactors SET gross_capacity_mw = 1417, thermal_capacity_mw = 3983, net_capacity_mw = 1337, reference_power_mw = 1337, commercial_operation = '2024-09-07', updated_at = CURRENT_TIMESTAMP WHERE id = 485;  -- Barakah 4
UPDATE reactors SET commercial_operation = '1976-02-07', updated_at = CURRENT_TIMESTAMP WHERE id = 518;  -- Hunterston B 1
UPDATE reactors SET commercial_operation = '1977-04-01', updated_at = CURRENT_TIMESTAMP WHERE id = 519;  -- Hunterston B 2
UPDATE reactors SET commercial_operation = '1989-02-04', updated_at = CURRENT_TIMESTAMP WHERE id = 526;  -- Torness 2
UPDATE reactors SET net_capacity_mw = 376, reference_power_mw = 376, updated_at = CURRENT_TIMESTAMP WHERE id = 542;  -- Rivne 2
UPDATE reactors SET grid_connection = '1987-07-12', updated_at = CURRENT_TIMESTAMP WHERE id = 560;  -- Braidwood 1
UPDATE reactors SET construction_start = '1970-12-09', grid_connection = '1985-10-20', commercial_operation = '1986-03-13', updated_at = CURRENT_TIMESTAMP WHERE id = 585;  -- Diablo Canyon 2
UPDATE reactors SET commercial_operation = '1986-09-19', updated_at = CURRENT_TIMESTAMP WHERE id = 634;  -- Palo Verde 2
UPDATE reactors SET construction_start = '2013-03-02', updated_at = CURRENT_TIMESTAMP WHERE id = 680;  -- Vogtle 3
UPDATE reactors SET gross_capacity_mw = 1150, construction_start = '2024-03-14', updated_at = CURRENT_TIMESTAMP WHERE id = 726;  -- Leningrad 2 3
UPDATE reactors SET gross_capacity_mw = 1150, net_capacity_mw = 1064, reference_power_mw = 1064, updated_at = CURRENT_TIMESTAMP WHERE id = 738;  -- Leningrad 2 4
UPDATE reactors SET grid_connection = '1962-10-10', updated_at = CURRENT_TIMESTAMP WHERE id = 11;  -- BR-3 1
UPDATE reactors SET permanent_shutdown = '2025-10-01', updated_at = CURRENT_TIMESTAMP WHERE id = 16;  -- Tihange 1
UPDATE reactors SET gross_capacity_mw = 1405, thermal_capacity_mw = 3900, construction_start = '2010-05-30', updated_at = CURRENT_TIMESTAMP WHERE id = 21;  -- Angra 3
UPDATE reactors SET net_capacity_mw = 206, reference_power_mw = 206, updated_at = CURRENT_TIMESTAMP WHERE id = 40;  -- Douglas Point 1
UPDATE reactors SET net_capacity_mw = 22, reference_power_mw = 22, grid_connection = '1962-06-04', updated_at = CURRENT_TIMESTAMP WHERE id = 52;  -- Rolphton NPD 1
UPDATE reactors SET gross_capacity_mw = 682, thermal_capacity_mw = 1882, net_capacity_mw = 642, reference_power_mw = 642, construction_start = '2017-12-29', updated_at = CURRENT_TIMESTAMP WHERE id = 54;  -- CFR 1
UPDATE reactors SET gross_capacity_mw = 682, thermal_capacity_mw = 1882, net_capacity_mw = 642, reference_power_mw = 642, updated_at = CURRENT_TIMESTAMP WHERE id = 55;  -- CFR 2
UPDATE reactors SET commercial_operation = '1959-04-23', updated_at = CURRENT_TIMESTAMP WHERE id = 127;  -- G2 2
UPDATE reactors SET net_capacity_mw = 40, reference_power_mw = 40, commercial_operation = '1960-04-05', updated_at = CURRENT_TIMESTAMP WHERE id = 128;  -- G3 3
UPDATE reactors SET net_capacity_mw = 70, reference_power_mw = 70, updated_at = CURRENT_TIMESTAMP WHERE id = 129;  -- Chinon A (EDF1) 1
UPDATE reactors SET permanent_shutdown = '1985-06-14', updated_at = CURRENT_TIMESTAMP WHERE id = 130;  -- Chinon A (EDF2) 2
UPDATE reactors SET grid_connection = '1966-08-04', updated_at = CURRENT_TIMESTAMP WHERE id = 131;  -- Chinon A (EDF3) 3
UPDATE reactors SET grid_connection = '1977-10-07', updated_at = CURRENT_TIMESTAMP WHERE id = 164;  -- Fessenheim 2
UPDATE reactors SET net_capacity_mw = 52, reference_power_mw = 52, updated_at = CURRENT_TIMESTAMP WHERE id = 229;  -- MZFR 1
UPDATE reactors SET commercial_operation = '1973-01-02', updated_at = CURRENT_TIMESTAMP WHERE id = 232;  -- Niederaichbach 1
UPDATE reactors SET net_capacity_mw = 25, reference_power_mw = 25, updated_at = CURRENT_TIMESTAMP WHERE id = 233;  -- HDR Großwelzheim 1
UPDATE reactors SET net_capacity_mw = 150, reference_power_mw = 150, updated_at = CURRENT_TIMESTAMP WHERE id = 263;  -- Tarapur 1
UPDATE reactors SET net_capacity_mw = 150, reference_power_mw = 150, updated_at = CURRENT_TIMESTAMP WHERE id = 264;  -- Tarapur 2
UPDATE reactors SET gross_capacity_mw = 1057, updated_at = CURRENT_TIMESTAMP WHERE id = 268;  -- Bushehr 2
UPDATE reactors SET grid_connection = '1964-10-22', updated_at = CURRENT_TIMESTAMP WHERE id = 270;  -- Enrico Fermi 1
UPDATE reactors SET grid_connection = '1963-05-12', updated_at = CURRENT_TIMESTAMP WHERE id = 272;  -- Latina 1
UPDATE reactors SET net_capacity_mw = 12, reference_power_mw = 12, updated_at = CURRENT_TIMESTAMP WHERE id = 297;  -- JPDR 1
UPDATE reactors SET net_capacity_mw = 1328, reference_power_mw = 1328, updated_at = CURRENT_TIMESTAMP WHERE id = 313;  -- Ohma 1
UPDATE reactors SET net_capacity_mw = 498, reference_power_mw = 498, updated_at = CURRENT_TIMESTAMP WHERE id = 314;  -- Onagawa 1
UPDATE reactors SET net_capacity_mw = 1108, reference_power_mw = 1108, updated_at = CURRENT_TIMESTAMP WHERE id = 320;  -- Shika 2
UPDATE reactors SET net_capacity_mw = 1060, reference_power_mw = 1060, updated_at = CURRENT_TIMESTAMP WHERE id = 329;  -- Tokai 2
UPDATE reactors SET grid_connection = '1954-06-26', updated_at = CURRENT_TIMESTAMP WHERE id = 353;  -- APS1 Obninsk 1
UPDATE reactors SET commercial_operation = '1964-04-27', updated_at = CURRENT_TIMESTAMP WHERE id = 359;  -- Beloyarsk 1
UPDATE reactors SET permanent_shutdown = '2025-12-19', updated_at = CURRENT_TIMESTAMP WHERE id = 365;  -- Bilibino 3
UPDATE reactors SET gross_capacity_mw = 1200, net_capacity_mw = 1123, reference_power_mw = 1123, updated_at = CURRENT_TIMESTAMP WHERE id = 380;  -- Kursk 2 2
UPDATE reactors SET gross_capacity_mw = 1400, thermal_capacity_mw = 3983, updated_at = CURRENT_TIMESTAMP WHERE id = 435;  -- Shin-Kori 5
UPDATE reactors SET gross_capacity_mw = 1400, thermal_capacity_mw = 3983, updated_at = CURRENT_TIMESTAMP WHERE id = 436;  -- Shin-Kori 6
UPDATE reactors SET commercial_operation = '1964-05-02', updated_at = CURRENT_TIMESTAMP WHERE id = 453;  -- Ågesta 1
UPDATE reactors SET gross_capacity_mw = 963, thermal_capacity_mw = 2652, net_capacity_mw = 852, reference_power_mw = 852, updated_at = CURRENT_TIMESTAMP WHERE id = 463;  -- Ringhals 2
UPDATE reactors SET grid_connection = '1968-01-29', updated_at = CURRENT_TIMESTAMP WHERE id = 470;  -- Lucens 1
UPDATE reactors SET gross_capacity_mw = 985, updated_at = CURRENT_TIMESTAMP WHERE id = 474;  -- Kuosheng (Second) 1
UPDATE reactors SET gross_capacity_mw = 985, updated_at = CURRENT_TIMESTAMP WHERE id = 475;  -- Kuosheng (Second) 2
UPDATE reactors SET permanent_shutdown = '2024-07-28', updated_at = CURRENT_TIMESTAMP WHERE id = 478;  -- Maanshan (Third) 1
UPDATE reactors SET permanent_shutdown = '2025-05-18', updated_at = CURRENT_TIMESTAMP WHERE id = 479;  -- Maanshan (Third) 2
UPDATE reactors SET gross_capacity_mw = 1200, updated_at = CURRENT_TIMESTAMP WHERE id = 480;  -- Akkuyu 1
UPDATE reactors SET construction_start = '1953-08-01', updated_at = CURRENT_TIMESTAMP WHERE id = 490;  -- Calder Hall 1
UPDATE reactors SET net_capacity_mw = 11, reference_power_mw = 11, commercial_operation = '1962-10-02', updated_at = CURRENT_TIMESTAMP WHERE id = 498;  -- Dounreay DFR 1
UPDATE reactors SET gross_capacity_mw = 230, updated_at = CURRENT_TIMESTAMP WHERE id = 500;  -- Dungeness A 1
UPDATE reactors SET gross_capacity_mw = 230, updated_at = CURRENT_TIMESTAMP WHERE id = 501;  -- Dungeness A 2
UPDATE reactors SET gross_capacity_mw = 1089, thermal_capacity_mw = 3132, net_capacity_mw = 1035, reference_power_mw = 1035, updated_at = CURRENT_TIMESTAMP WHERE id = 539;  -- Khmelnytskyi 3
UPDATE reactors SET gross_capacity_mw = 1089, thermal_capacity_mw = 3132, net_capacity_mw = 1035, reference_power_mw = 1035, updated_at = CURRENT_TIMESTAMP WHERE id = 540;  -- Khmelnytskyi 4
UPDATE reactors SET construction_start = '1968-10-30', grid_connection = '1976-04-25', commercial_operation = '1976-08-28', permanent_shutdown = '2021-04-28', updated_at = CURRENT_TIMESTAMP WHERE id = 610;  -- Indian Point 3
UPDATE reactors SET construction_start = '1967-03-12', grid_connection = '1971-12-29', updated_at = CURRENT_TIMESTAMP WHERE id = 632;  -- Palisades 1
UPDATE reactors SET commercial_operation = '1966-08-01', updated_at = CURRENT_TIMESTAMP WHERE id = 636;  -- Pathfinder 1
UPDATE reactors SET gross_capacity_mw = 1215, updated_at = CURRENT_TIMESTAMP WHERE id = 692;  -- Sanao 1
UPDATE reactors SET gross_capacity_mw = 1215, updated_at = CURRENT_TIMESTAMP WHERE id = 694;  -- Sanao 3
UPDATE reactors SET construction_start = '2023-04-22', updated_at = CURRENT_TIMESTAMP WHERE id = 696;  -- Haiyang 4
UPDATE reactors SET construction_start = '2023-03-22', updated_at = CURRENT_TIMESTAMP WHERE id = 698;  -- Sanmen 4
UPDATE reactors SET gross_capacity_mw = 1250, updated_at = CURRENT_TIMESTAMP WHERE id = 699;  -- Lufeng 1
UPDATE reactors SET gross_capacity_mw = 1200, updated_at = CURRENT_TIMESTAMP WHERE id = 700;  -- Lufeng 2
UPDATE reactors SET construction_start = '2022-02-25', updated_at = CURRENT_TIMESTAMP WHERE id = 708;  -- Tianwan 8
UPDATE reactors SET gross_capacity_mw = 1224, updated_at = CURRENT_TIMESTAMP WHERE id = 711;  -- Lianjiang 1
UPDATE reactors SET gross_capacity_mw = 1224, updated_at = CURRENT_TIMESTAMP WHERE id = 712;  -- Lianjiang 2
UPDATE reactors SET gross_capacity_mw = 1254, construction_start = '2025-12-22', updated_at = CURRENT_TIMESTAMP WHERE id = 716;  -- Bailong 1
UPDATE reactors SET gross_capacity_mw = 1209, updated_at = CURRENT_TIMESTAMP WHERE id = 717;  -- Taipingling 3
UPDATE reactors SET construction_start = '2022-07-20', updated_at = CURRENT_TIMESTAMP WHERE id = 718;  -- El Dabaa 1
UPDATE reactors SET construction_start = '2022-11-19', updated_at = CURRENT_TIMESTAMP WHERE id = 719;  -- El Dabaa 2
UPDATE reactors SET construction_start = '2023-05-03', updated_at = CURRENT_TIMESTAMP WHERE id = 720;  -- El Dabaa 3
UPDATE reactors SET construction_start = '2024-01-23', updated_at = CURRENT_TIMESTAMP WHERE id = 721;  -- El Dabaa 4
UPDATE reactors SET construction_start = '2021-03-10', updated_at = CURRENT_TIMESTAMP WHERE id = 722;  -- Akkuyu 3
UPDATE reactors SET construction_start = '2022-07-21', updated_at = CURRENT_TIMESTAMP WHERE id = 723;  -- Akkuyu 4
UPDATE reactors SET construction_start = '2021-06-08', updated_at = CURRENT_TIMESTAMP WHERE id = 727;  -- BREST 1
UPDATE reactors SET gross_capacity_mw = 1225, net_capacity_mw = 1134, reference_power_mw = 1134, updated_at = CURRENT_TIMESTAMP WHERE id = 731;  -- Shidaowan 1
UPDATE reactors SET gross_capacity_mw = 1225, net_capacity_mw = 1134, reference_power_mw = 1134, construction_start = '2025-05-07', updated_at = CURRENT_TIMESTAMP WHERE id = 732;  -- Shidaowan 2
UPDATE reactors SET gross_capacity_mw = 1221, updated_at = CURRENT_TIMESTAMP WHERE id = 733;  -- Ningde 6
UPDATE reactors SET gross_capacity_mw = 1200, net_capacity_mw = 1123, reference_power_mw = 1123, updated_at = CURRENT_TIMESTAMP WHERE id = 740;  -- Kursk 2 3
UPDATE reactors SET net_capacity_mw = 300, reference_power_mw = 300, construction_start = '2026-04-22', updated_at = CURRENT_TIMESTAMP WHERE id = 741;  -- Darlington SMR 1
COMMIT;
