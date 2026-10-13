-- 023_pris_fills.sql
-- Date: 2026-10-13
-- Description: Audit batch A: fill blank fields from PRIS (no existing value overwritten).
--   pris_id (new ids checked unique), first_criticality, operator, blank capacities and dates.
--   Net blanks filled only when PRIS net passes the net/gross guard; reference = net (house rule).
-- Source: IAEA PRIS API (pris-stats.iaea.org), pulled 2026-10-13. Built by scripts/audit_build_batches.py from audit/pris_diff.tsv.
-- Rows: 733 reactors. Backup: nuclear_reactors.db.bak-pre023-20261013

BEGIN TRANSACTION;
UPDATE reactors SET first_criticality = '1974-01-13', operator = 'NUCLEOELECTRICA ARGENTINA S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 1;  -- Atucha 1
UPDATE reactors SET first_criticality = '2014-05-30', operator = 'NUCLEOELECTRICA ARGENTINA S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 2;  -- Atucha 2
UPDATE reactors SET first_criticality = '1983-03-13', operator = 'NUCLEOELECTRICA ARGENTINA S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 4;  -- Embalse 1
UPDATE reactors SET first_criticality = '1980-01-01', operator = 'Closed Joint Stock Company Armenian NPP', updated_at = CURRENT_TIMESTAMP WHERE id = 6;  -- Armenian 2
UPDATE reactors SET first_criticality = '2020-10-11', operator = 'Republican Unitary Enterprise "Belarusian Nuclear Power Plant"', updated_at = CURRENT_TIMESTAMP WHERE id = 9;  -- Belarusian 1
UPDATE reactors SET first_criticality = '2023-03-25', operator = 'Republican Unitary Enterprise "Belarusian Nuclear Power Plant"', updated_at = CURRENT_TIMESTAMP WHERE id = 10;  -- Belarusian 2
UPDATE reactors SET first_criticality = '1985-03-31', operator = 'ENGIE ELECTRABEL + EDF BELGIUM + EDF LUMINUS', updated_at = CURRENT_TIMESTAMP WHERE id = 15;  -- Doel 4
UPDATE reactors SET first_criticality = '1985-06-05', operator = 'ENGIE ELECTRABEL', updated_at = CURRENT_TIMESTAMP WHERE id = 18;  -- Tihange 3
UPDATE reactors SET first_criticality = '1982-03-13', operator = 'ELETRONUCLEAR S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 19;  -- Angra 1
UPDATE reactors SET first_criticality = '2000-07-14', operator = 'ELETRONUCLEAR S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 20;  -- Angra 2
UPDATE reactors SET first_criticality = '1987-11-05', operator = 'Kozloduy Npp ,lc', updated_at = CURRENT_TIMESTAMP WHERE id = 26;  -- Kozloduy 5
UPDATE reactors SET first_criticality = '1991-05-29', operator = 'Kozloduy Npp ,lc', updated_at = CURRENT_TIMESTAMP WHERE id = 27;  -- Kozloduy 6
UPDATE reactors SET first_criticality = '1976-12-17', operator = 'Bruce Power', updated_at = CURRENT_TIMESTAMP WHERE id = 28;  -- Bruce 1
UPDATE reactors SET first_criticality = '1976-07-27', operator = 'Bruce Power', updated_at = CURRENT_TIMESTAMP WHERE id = 29;  -- Bruce 2
UPDATE reactors SET first_criticality = '1977-11-28', operator = 'Bruce Power', updated_at = CURRENT_TIMESTAMP WHERE id = 30;  -- Bruce 3
UPDATE reactors SET first_criticality = '1978-12-10', operator = 'Bruce Power', updated_at = CURRENT_TIMESTAMP WHERE id = 31;  -- Bruce 4
UPDATE reactors SET first_criticality = '1984-11-14', operator = 'Bruce Power', updated_at = CURRENT_TIMESTAMP WHERE id = 32;  -- Bruce 5
UPDATE reactors SET first_criticality = '1984-05-29', operator = 'Bruce Power', updated_at = CURRENT_TIMESTAMP WHERE id = 33;  -- Bruce 6
UPDATE reactors SET first_criticality = '1986-01-07', operator = 'Bruce Power', updated_at = CURRENT_TIMESTAMP WHERE id = 34;  -- Bruce 7
UPDATE reactors SET first_criticality = '1987-02-13', operator = 'Bruce Power', updated_at = CURRENT_TIMESTAMP WHERE id = 35;  -- Bruce 8
UPDATE reactors SET first_criticality = '1990-10-29', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 36;  -- Darlington 1
UPDATE reactors SET first_criticality = '1989-11-05', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 37;  -- Darlington 2
UPDATE reactors SET first_criticality = '1992-11-09', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 38;  -- Darlington 3
UPDATE reactors SET first_criticality = '1993-03-13', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 39;  -- Darlington 4
UPDATE reactors SET first_criticality = '1971-02-25', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 43;  -- Pickering 1
UPDATE reactors SET first_criticality = '1971-09-15', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 44;  -- Pickering 2
UPDATE reactors SET first_criticality = '1972-04-24', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 45;  -- Pickering 3
UPDATE reactors SET first_criticality = '1973-05-16', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 46;  -- Pickering 4
UPDATE reactors SET first_criticality = '1982-10-23', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 47;  -- Pickering 5
UPDATE reactors SET first_criticality = '1983-10-15', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 48;  -- Pickering 6
UPDATE reactors SET first_criticality = '1984-10-22', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 49;  -- Pickering 7
UPDATE reactors SET first_criticality = '1985-12-17', operator = 'Ontario Power Generation', updated_at = CURRENT_TIMESTAMP WHERE id = 50;  -- Pickering 8
UPDATE reactors SET first_criticality = '1982-07-25', operator = 'NEW BRUNSWICK ELECTRIC POWER COMMISSION', updated_at = CURRENT_TIMESTAMP WHERE id = 51;  -- Point Lepreau 1
UPDATE reactors SET first_criticality = '2015-10-12', operator = 'Hainan Nuclear Power Company', updated_at = CURRENT_TIMESTAMP WHERE id = 56;  -- Changjiang 1
UPDATE reactors SET first_criticality = '2016-06-09', operator = 'Hainan Nuclear Power Company', updated_at = CURRENT_TIMESTAMP WHERE id = 57;  -- Changjiang 2
UPDATE reactors SET first_criticality = '1993-07-28', operator = 'Daya Bay Nuclear Power Operations and Management Co, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 58;  -- Daya Bay 1
UPDATE reactors SET first_criticality = '1994-01-21', operator = 'Daya Bay Nuclear Power Operations and Management Co, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 59;  -- Daya Bay 2
UPDATE reactors SET first_criticality = '2015-10-13', operator = 'Guangxi Fangchenggang Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 60;  -- Fangchenggang 1
UPDATE reactors SET first_criticality = '2016-06-29', operator = 'Guangxi Fangchenggang Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 61;  -- Fangchenggang 2
UPDATE reactors SET first_criticality = '2022-12-27', grid_connection = '2023-01-10', operator = 'Guangxi Fangchenggang Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 62;  -- Fangchenggang 3
UPDATE reactors SET first_criticality = '2024-04-03', grid_connection = '2024-04-09', operator = 'Guangxi Fangchenggang Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 63;  -- Fangchenggang 4
UPDATE reactors SET first_criticality = '2014-10-21', operator = 'CNNC Nuclear Operation Management Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 64;  -- Fangjiashan 1
UPDATE reactors SET first_criticality = '2014-12-25', operator = 'CNNC Nuclear Operation Management Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 65;  -- Fangjiashan 2
UPDATE reactors SET first_criticality = '2014-07-24', operator = 'CNNC Fujian Fuqing Nuclear Power Co., LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 66;  -- Fuqing 1
UPDATE reactors SET first_criticality = '2015-07-22', operator = 'CNNC Fujian Fuqing Nuclear Power Co., LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 67;  -- Fuqing 2
UPDATE reactors SET first_criticality = '2016-07-03', operator = 'CNNC Fujian Fuqing Nuclear Power Co., LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 68;  -- Fuqing 3
UPDATE reactors SET first_criticality = '2017-07-16', operator = 'CNNC Fujian Fuqing Nuclear Power Co., LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 69;  -- Fuqing 4
UPDATE reactors SET first_criticality = '2020-10-21', operator = 'CNNC Fujian Fuqing Nuclear Power Co., LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 70;  -- Fuqing 5
UPDATE reactors SET first_criticality = '2021-12-11', grid_connection = '2022-01-01', operator = 'CNNC Fujian Fuqing Nuclear Power Co., LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 71;  -- Fuqing 6
UPDATE reactors SET first_criticality = '2018-08-08', operator = 'Shandong Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 72;  -- Haiyang 1
UPDATE reactors SET first_criticality = '2018-09-29', operator = 'Shandong Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 73;  -- Haiyang 2
UPDATE reactors SET first_criticality = '2013-01-16', operator = 'Liaoning Hongyanhe Nuclear Power Co. Ltd. (LHNPC)', updated_at = CURRENT_TIMESTAMP WHERE id = 74;  -- Hongyanhe 1
UPDATE reactors SET first_criticality = '2013-10-24', operator = 'Liaoning Hongyanhe Nuclear Power Co. Ltd. (LHNPC)', updated_at = CURRENT_TIMESTAMP WHERE id = 75;  -- Hongyanhe 2
UPDATE reactors SET first_criticality = '2014-10-27', operator = 'Liaoning Hongyanhe Nuclear Power Co. Ltd. (LHNPC)', updated_at = CURRENT_TIMESTAMP WHERE id = 76;  -- Hongyanhe 3
UPDATE reactors SET first_criticality = '2016-03-05', operator = 'Liaoning Hongyanhe Nuclear Power Co. Ltd. (LHNPC)', updated_at = CURRENT_TIMESTAMP WHERE id = 77;  -- Hongyanhe 4
UPDATE reactors SET first_criticality = '2021-06-13', grid_connection = '2021-06-25', operator = 'Liaoning Hongyanhe Nuclear Power Co. Ltd. (LHNPC)', updated_at = CURRENT_TIMESTAMP WHERE id = 78;  -- Hongyanhe 5
UPDATE reactors SET first_criticality = '2022-04-21', grid_connection = '2022-05-02', operator = 'Liaoning Hongyanhe Nuclear Power Co. Ltd. (LHNPC)', updated_at = CURRENT_TIMESTAMP WHERE id = 79;  -- Hongyanhe 6
UPDATE reactors SET first_criticality = '2002-02-04', operator = 'Daya Bay Nuclear Power Operations and Management Co, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 80;  -- Ling Ao 1
UPDATE reactors SET first_criticality = '2002-08-27', operator = 'Daya Bay Nuclear Power Operations and Management Co, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 81;  -- Ling Ao 2
UPDATE reactors SET first_criticality = '2010-06-09', operator = 'Daya Bay Nuclear Power Operations and Management Co, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 82;  -- Ling Ao 3
UPDATE reactors SET first_criticality = '2011-02-25', operator = 'Daya Bay Nuclear Power Operations and Management Co, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 83;  -- Ling Ao 4
UPDATE reactors SET first_criticality = '2012-11-24', operator = 'Fujian Ningde Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 84;  -- Ningde 1
UPDATE reactors SET first_criticality = '2013-12-20', operator = 'Fujian Ningde Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 85;  -- Ningde 2
UPDATE reactors SET first_criticality = '2015-03-08', operator = 'Fujian Ningde Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 86;  -- Ningde 3
UPDATE reactors SET first_criticality = '2016-03-16', operator = 'Fujian Ningde Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 87;  -- Ningde 4
UPDATE reactors SET first_criticality = '1991-10-31', operator = 'CNNC Nuclear Operation Management Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 88;  -- Qinshan 1 1
UPDATE reactors SET first_criticality = '2001-11-15', operator = 'CNNC Nuclear Operation Management Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 89;  -- Qinshan 2 1
UPDATE reactors SET first_criticality = '2004-02-25', operator = 'CNNC Nuclear Operation Management Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 90;  -- Qinshan 2 2
UPDATE reactors SET first_criticality = '2010-07-13', operator = 'CNNC Nuclear Operation Management Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 91;  -- Qinshan 2 3
UPDATE reactors SET first_criticality = '2011-11-17', operator = 'CNNC Nuclear Operation Management Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 92;  -- Qinshan 2 4
UPDATE reactors SET first_criticality = '2002-09-21', operator = 'CNNC Nuclear Operation Management Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 93;  -- Qinshan 3 1
UPDATE reactors SET first_criticality = '2003-01-18', operator = 'CNNC Nuclear Operation Management Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 94;  -- Qinshan 3 2
UPDATE reactors SET first_criticality = '2018-06-21', operator = 'SANMEN NUCLEAR POWER CO., LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 95;  -- Sanmen 1
UPDATE reactors SET first_criticality = '2018-08-17', operator = 'SANMEN NUCLEAR POWER CO., LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 96;  -- Sanmen 2
UPDATE reactors SET first_criticality = '2021-09-12', grid_connection = '2021-12-14', operator = 'Huaneng Shandong Shidao Bay Nuclear Power Company, Ltd.', updated_at = CURRENT_TIMESTAMP WHERE id = 97;  -- Shidao Bay 1
UPDATE reactors SET first_criticality = '2026-02-03', commercial_operation = '2026-04-19', operator = 'CGN Huizhou Nuclear Power Co.,Ltd,', updated_at = CURRENT_TIMESTAMP WHERE id = 98;  -- Taipingling 1
UPDATE reactors SET first_criticality = '2018-06-06', operator = 'Taishan Nuclear Power Joint Venture Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 100;  -- Taishan 1
UPDATE reactors SET first_criticality = '2019-05-28', operator = 'Taishan Nuclear Power Joint Venture Company Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 101;  -- Taishan 2
UPDATE reactors SET first_criticality = '2005-12-20', operator = 'Jiangsu Nuclear Power Corporation', updated_at = CURRENT_TIMESTAMP WHERE id = 102;  -- Tianwan 1
UPDATE reactors SET first_criticality = '2007-05-01', operator = 'Jiangsu Nuclear Power Corporation', updated_at = CURRENT_TIMESTAMP WHERE id = 103;  -- Tianwan 2
UPDATE reactors SET first_criticality = '2017-09-29', operator = 'Jiangsu Nuclear Power Corporation', updated_at = CURRENT_TIMESTAMP WHERE id = 104;  -- Tianwan 3
UPDATE reactors SET first_criticality = '2018-09-30', operator = 'Jiangsu Nuclear Power Corporation', updated_at = CURRENT_TIMESTAMP WHERE id = 105;  -- Tianwan 4
UPDATE reactors SET first_criticality = '2020-07-27', operator = 'Jiangsu Nuclear Power Corporation', updated_at = CURRENT_TIMESTAMP WHERE id = 106;  -- Tianwan 5
UPDATE reactors SET first_criticality = '2021-05-04', operator = 'Jiangsu Nuclear Power Corporation', updated_at = CURRENT_TIMESTAMP WHERE id = 107;  -- Tianwan 6
UPDATE reactors SET first_criticality = '2013-12-23', operator = 'Yangjiang Nuclear Power Company', updated_at = CURRENT_TIMESTAMP WHERE id = 108;  -- Yangjiang 1
UPDATE reactors SET first_criticality = '2015-03-02', operator = 'Yangjiang Nuclear Power Company', updated_at = CURRENT_TIMESTAMP WHERE id = 109;  -- Yangjiang 2
UPDATE reactors SET first_criticality = '2015-10-11', operator = 'Yangjiang Nuclear Power Company', updated_at = CURRENT_TIMESTAMP WHERE id = 110;  -- Yangjiang 3
UPDATE reactors SET first_criticality = '2016-12-30', operator = 'Yangjiang Nuclear Power Company', updated_at = CURRENT_TIMESTAMP WHERE id = 111;  -- Yangjiang 4
UPDATE reactors SET first_criticality = '2018-05-16', operator = 'Yangjiang Nuclear Power Company', updated_at = CURRENT_TIMESTAMP WHERE id = 112;  -- Yangjiang 5
UPDATE reactors SET first_criticality = '2019-06-22', operator = 'Yangjiang Nuclear Power Company', updated_at = CURRENT_TIMESTAMP WHERE id = 113;  -- Yangjiang 6
UPDATE reactors SET first_criticality = '2024-11-07', operator = 'CNNP Guodian Zhangzhou Energy Co.,Ltd', updated_at = CURRENT_TIMESTAMP WHERE id = 114;  -- Zhangzhou 1
UPDATE reactors SET first_criticality = '2025-11-03', grid_connection = '2025-11-22', operator = 'CNNP Guodian Zhangzhou Energy Co.,Ltd', updated_at = CURRENT_TIMESTAMP WHERE id = 115;  -- Zhangzhou 2
UPDATE reactors SET first_criticality = '1985-02-12', operator = 'CZECH POWER Co., ČEZ a.s.', updated_at = CURRENT_TIMESTAMP WHERE id = 116;  -- Dukovany 1
UPDATE reactors SET first_criticality = '1986-01-23', operator = 'CZECH POWER Co., ČEZ a.s.', updated_at = CURRENT_TIMESTAMP WHERE id = 117;  -- Dukovany 2
UPDATE reactors SET first_criticality = '1986-10-28', operator = 'CZECH POWER Co., ČEZ a.s.', updated_at = CURRENT_TIMESTAMP WHERE id = 118;  -- Dukovany 3
UPDATE reactors SET first_criticality = '1987-06-01', operator = 'CZECH POWER Co., ČEZ a.s.', updated_at = CURRENT_TIMESTAMP WHERE id = 119;  -- Dukovany 4
UPDATE reactors SET first_criticality = '2000-10-11', operator = 'CZECH POWER Co., ČEZ a.s.', updated_at = CURRENT_TIMESTAMP WHERE id = 120;  -- Temelin 1
UPDATE reactors SET first_criticality = '2002-05-31', operator = 'CZECH POWER Co., ČEZ a.s.', updated_at = CURRENT_TIMESTAMP WHERE id = 121;  -- Temelin 2
UPDATE reactors SET first_criticality = '1977-01-21', operator = 'FORTUM POWER AND HEAT OY (former IVO)', updated_at = CURRENT_TIMESTAMP WHERE id = 122;  -- Loviisa 1
UPDATE reactors SET first_criticality = '1980-10-17', operator = 'FORTUM POWER AND HEAT OY (former IVO)', updated_at = CURRENT_TIMESTAMP WHERE id = 123;  -- Loviisa 2
UPDATE reactors SET first_criticality = '1978-07-21', operator = 'TEOLLISUUDEN VOIMA OYJ', updated_at = CURRENT_TIMESTAMP WHERE id = 124;  -- Olkiluoto 1
UPDATE reactors SET first_criticality = '1979-10-13', operator = 'TEOLLISUUDEN VOIMA OYJ', updated_at = CURRENT_TIMESTAMP WHERE id = 125;  -- Olkiluoto 2
UPDATE reactors SET first_criticality = '2021-12-21', operator = 'TEOLLISUUDEN VOIMA OYJ', updated_at = CURRENT_TIMESTAMP WHERE id = 126;  -- Olkiluoto 3
UPDATE reactors SET first_criticality = '1978-04-20', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 134;  -- Bugey 2
UPDATE reactors SET first_criticality = '1978-08-31', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 135;  -- Bugey 3
UPDATE reactors SET first_criticality = '1979-02-17', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 136;  -- Bugey 4
UPDATE reactors SET first_criticality = '1979-07-15', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 137;  -- Bugey 5
UPDATE reactors SET first_criticality = '1980-03-15', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 140;  -- Dampierre 1
UPDATE reactors SET first_criticality = '1980-02-21', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 141;  -- Gravelines 1
UPDATE reactors SET first_criticality = '1980-08-02', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 142;  -- Gravelines 2
UPDATE reactors SET first_criticality = '1980-12-05', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 143;  -- Dampierre 2
UPDATE reactors SET first_criticality = '1980-11-29', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 144;  -- Tricastin 3
UPDATE reactors SET first_criticality = '1981-05-31', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 145;  -- Tricastin 4
UPDATE reactors SET first_criticality = '1981-01-25', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 146;  -- Dampierre 3
UPDATE reactors SET first_criticality = '1981-08-05', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 147;  -- Dampierre 4
UPDATE reactors SET first_criticality = '1980-11-30', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 148;  -- Gravelines 3
UPDATE reactors SET first_criticality = '1981-05-31', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 149;  -- Gravelines 4
UPDATE reactors SET first_criticality = '1981-01-04', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 150;  -- St. Laurent B 1
UPDATE reactors SET first_criticality = '1981-05-12', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 151;  -- St. Laurent B 2
UPDATE reactors SET first_criticality = '1981-05-20', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 153;  -- Blayais 1
UPDATE reactors SET first_criticality = '1982-06-28', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 154;  -- Blayais 2
UPDATE reactors SET first_criticality = '1982-10-28', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 155;  -- Chinon B 1
UPDATE reactors SET first_criticality = '1983-09-23', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 156;  -- Chinon B 2
UPDATE reactors SET first_criticality = '1984-05-13', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 157;  -- Paluel 1
UPDATE reactors SET first_criticality = '1984-08-11', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 158;  -- Paluel 2
UPDATE reactors SET first_criticality = '1983-07-29', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 159;  -- Blayais 3
UPDATE reactors SET first_criticality = '1983-05-01', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 160;  -- Blayais 4
UPDATE reactors SET first_criticality = '1983-04-02', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 161;  -- Cruas 1
UPDATE reactors SET first_criticality = '1984-08-01', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 162;  -- Cruas 2
UPDATE reactors SET first_criticality = '1985-08-04', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 165;  -- St. Alban 1
UPDATE reactors SET first_criticality = '1985-08-07', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 166;  -- Paluel 3
UPDATE reactors SET first_criticality = '1984-04-09', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 167;  -- Cruas 3
UPDATE reactors SET first_criticality = '1986-06-07', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 168;  -- St. Alban 2
UPDATE reactors SET first_criticality = '1984-10-01', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 169;  -- Cruas 4
UPDATE reactors SET first_criticality = '1984-08-05', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 170;  -- Gravelines 5
UPDATE reactors SET first_criticality = '1985-07-21', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 171;  -- Gravelines 6
UPDATE reactors SET first_criticality = '1986-10-24', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 172;  -- Cattenom 1
UPDATE reactors SET first_criticality = '1985-09-29', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 173;  -- Flamanville 1
UPDATE reactors SET first_criticality = '1986-03-29', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 174;  -- Paluel 4
UPDATE reactors SET first_criticality = '1987-09-09', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 175;  -- Belleville 1
UPDATE reactors SET first_criticality = '1986-06-12', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 176;  -- Flamanville 2
UPDATE reactors SET first_criticality = '1987-08-07', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 177;  -- Cattenom 2
UPDATE reactors SET first_criticality = '1988-05-25', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 178;  -- Belleville 2
UPDATE reactors SET first_criticality = '1986-09-18', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 179;  -- Chinon B 3
UPDATE reactors SET first_criticality = '1987-10-13', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 180;  -- Chinon B 4
UPDATE reactors SET first_criticality = '1987-09-12', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 181;  -- Nogent 1
UPDATE reactors SET first_criticality = '1988-10-04', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 182;  -- Nogent 2
UPDATE reactors SET first_criticality = '1990-02-16', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 183;  -- Cattenom 3
UPDATE reactors SET first_criticality = '1990-04-01', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 184;  -- Penly 1
UPDATE reactors SET first_criticality = '1990-04-24', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 185;  -- Golfech 1
UPDATE reactors SET first_criticality = '1991-05-04', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 187;  -- Cattenom 4
UPDATE reactors SET first_criticality = '1996-07-25', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 188;  -- Chooz B 1
UPDATE reactors SET first_criticality = '1992-01-10', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 189;  -- Penly 2
UPDATE reactors SET first_criticality = '1993-05-21', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 191;  -- Golfech 2
UPDATE reactors SET first_criticality = '1997-03-10', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 192;  -- Chooz B 2
UPDATE reactors SET first_criticality = '1997-11-29', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 193;  -- Civaux 1
UPDATE reactors SET first_criticality = '1980-02-21', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 194;  -- Tricastin 1
UPDATE reactors SET first_criticality = '1980-07-22', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 195;  -- Tricastin 2
UPDATE reactors SET first_criticality = '1999-11-27', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 196;  -- Civaux 2
UPDATE reactors SET operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 197;  -- Flamanville 3
UPDATE reactors SET first_criticality = '1982-12-14', operator = 'PAKS NUCLEAR POWER PLANT, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 234;  -- Paks 1
UPDATE reactors SET first_criticality = '1984-08-26', operator = 'PAKS NUCLEAR POWER PLANT, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 235;  -- Paks 2
UPDATE reactors SET first_criticality = '1986-09-15', operator = 'PAKS NUCLEAR POWER PLANT, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 236;  -- Paks 3
UPDATE reactors SET first_criticality = '1987-08-09', operator = 'PAKS NUCLEAR POWER PLANT, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 237;  -- Paks 4
UPDATE reactors SET first_criticality = '2000-09-26', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 238;  -- Kaiga 1
UPDATE reactors SET first_criticality = '1999-09-24', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 239;  -- Kaiga 2
UPDATE reactors SET first_criticality = '2007-02-26', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 240;  -- Kaiga 3
UPDATE reactors SET first_criticality = '2010-11-27', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 241;  -- Kaiga 4
UPDATE reactors SET first_criticality = '1992-09-03', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 242;  -- Kakrapar 1
UPDATE reactors SET first_criticality = '1995-01-08', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 243;  -- Kakrapar 2
UPDATE reactors SET first_criticality = '2020-07-22', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 244;  -- Kakrapar 3
UPDATE reactors SET first_criticality = '2023-12-17', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 245;  -- Kakrapar 4
UPDATE reactors SET first_criticality = '2013-07-13', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 246;  -- Kudankulam 1
UPDATE reactors SET first_criticality = '2016-07-10', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 247;  -- Kudankulam 2
UPDATE reactors SET first_criticality = '1983-07-02', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 250;  -- Madras 1
UPDATE reactors SET first_criticality = '1985-08-12', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 251;  -- Madras 2
UPDATE reactors SET first_criticality = '1989-03-12', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 252;  -- Narora 1
UPDATE reactors SET first_criticality = '1991-10-24', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 253;  -- Narora 2
UPDATE reactors SET first_criticality = '1980-10-08', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 256;  -- Rajasthan 2
UPDATE reactors SET first_criticality = '1999-12-24', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 257;  -- Rajasthan 3
UPDATE reactors SET first_criticality = '2000-11-03', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 258;  -- Rajasthan 4
UPDATE reactors SET first_criticality = '2009-11-24', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 259;  -- Rajasthan 5
UPDATE reactors SET first_criticality = '2010-01-23', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 260;  -- Rajasthan 6
UPDATE reactors SET first_criticality = '2024-09-19', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 261;  -- Rajasthan 7
UPDATE reactors SET first_criticality = '2006-05-21', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 265;  -- Tarapur 3
UPDATE reactors SET first_criticality = '2005-03-06', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 266;  -- Tarapur 4
UPDATE reactors SET first_criticality = '2011-05-08', operator = 'Nuclear Power Production and Development Co. of Iran', updated_at = CURRENT_TIMESTAMP WHERE id = 267;  -- Bushehr 1
UPDATE reactors SET first_criticality = '1993-05-28', operator = 'Kyushu Electric Power Co., Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 286;  -- Genkai 3
UPDATE reactors SET first_criticality = '1996-10-23', operator = 'Kyushu Electric Power Co., Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 287;  -- Genkai 4
UPDATE reactors SET first_criticality = '1994-02-23', operator = 'SHIKOKU ELECTRIC POWER CO., INC', updated_at = CURRENT_TIMESTAMP WHERE id = 296;  -- Ikata 3
UPDATE reactors SET first_criticality = '1995-12-18', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 303;  -- Kashiwazaki Kariwa 6
UPDATE reactors SET first_criticality = '1976-01-28', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 307;  -- Mihama 3
UPDATE reactors SET first_criticality = '1991-05-17', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 311;  -- Ohi 3
UPDATE reactors SET first_criticality = '1992-05-28', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 312;  -- Ohi 4
UPDATE reactors SET first_criticality = '1994-11-02', operator = 'Tohoku Electric Power Co., Inc', updated_at = CURRENT_TIMESTAMP WHERE id = 315;  -- Onagawa 2
UPDATE reactors SET first_criticality = '1983-08-25', operator = 'Kyushu Electric Power Co., Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 317;  -- Sendai 1
UPDATE reactors SET first_criticality = '1985-03-18', operator = 'Kyushu Electric Power Co., Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 318;  -- Sendai 2
UPDATE reactors SET first_criticality = '1988-05-25', operator = 'THE CHUGOKU ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 322;  -- Shimane 2
UPDATE reactors SET first_criticality = '1974-03-14', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 324;  -- Takahama 1
UPDATE reactors SET first_criticality = '1974-12-20', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 325;  -- Takahama 2
UPDATE reactors SET first_criticality = '1984-04-17', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 326;  -- Takahama 3
UPDATE reactors SET first_criticality = '1984-10-11', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 327;  -- Takahama 4
UPDATE reactors SET first_criticality = '1988-11-04', operator = 'COMISION FEDERAL DE ELECTRICIDAD', updated_at = CURRENT_TIMESTAMP WHERE id = 338;  -- Laguna Verde 1
UPDATE reactors SET first_criticality = '1994-09-05', operator = 'COMISION FEDERAL DE ELECTRICIDAD', updated_at = CURRENT_TIMESTAMP WHERE id = 339;  -- Laguna Verde 2
UPDATE reactors SET first_criticality = '1973-06-20', operator = 'N.V. ELEKTRICITEITS-PRODUKTIEMAATSCHAPPIJ ZUID-NEDERLAND', updated_at = CURRENT_TIMESTAMP WHERE id = 340;  -- Borssele 1
UPDATE reactors SET first_criticality = '2000-05-03', operator = 'PAKISTAN ATOMIC ENERGY COMMISSION', updated_at = CURRENT_TIMESTAMP WHERE id = 342;  -- Chashma 1
UPDATE reactors SET first_criticality = '2011-02-22', operator = 'PAKISTAN ATOMIC ENERGY COMMISSION', updated_at = CURRENT_TIMESTAMP WHERE id = 343;  -- Chashma 2
UPDATE reactors SET first_criticality = '2016-08-01', operator = 'PAKISTAN ATOMIC ENERGY COMMISSION', updated_at = CURRENT_TIMESTAMP WHERE id = 344;  -- Chashma 3
UPDATE reactors SET first_criticality = '2017-03-15', operator = 'PAKISTAN ATOMIC ENERGY COMMISSION', updated_at = CURRENT_TIMESTAMP WHERE id = 345;  -- Chashma 4
UPDATE reactors SET first_criticality = '2021-02-28', operator = 'PAKISTAN ATOMIC ENERGY COMMISSION', updated_at = CURRENT_TIMESTAMP WHERE id = 347;  -- Karachi 2
UPDATE reactors SET first_criticality = '2022-02-21', operator = 'PAKISTAN ATOMIC ENERGY COMMISSION', updated_at = CURRENT_TIMESTAMP WHERE id = 348;  -- Karachi 3
UPDATE reactors SET first_criticality = '1996-04-16', operator = 'SOCIETATEA NATIONALA NUCLEARELECTRICA, S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 349;  -- Cernavodă 1
UPDATE reactors SET first_criticality = '2007-05-06', operator = 'SOCIETATEA NATIONALA NUCLEARELECTRICA, S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 350;  -- Cernavodă 2
UPDATE reactors SET first_criticality = '2018-11-02', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 351;  -- Akademik Lomonosov 1
UPDATE reactors SET first_criticality = '2018-11-08', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 352;  -- Akademik Lomonosov 2
UPDATE reactors SET first_criticality = '1985-12-12', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 354;  -- Balakovo 1
UPDATE reactors SET first_criticality = '1987-10-02', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 355;  -- Balakovo 2
UPDATE reactors SET first_criticality = '1988-12-16', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 356;  -- Balakovo 3
UPDATE reactors SET first_criticality = '1993-03-24', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 357;  -- Balakovo 4
UPDATE reactors SET first_criticality = '1980-02-26', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 361;  -- Beloyarsk 3
UPDATE reactors SET first_criticality = '2014-06-27', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 362;  -- Beloyarsk 4
UPDATE reactors SET first_criticality = '1984-04-10', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 367;  -- Kalinin 1
UPDATE reactors SET first_criticality = '1986-11-25', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 368;  -- Kalinin 2
UPDATE reactors SET first_criticality = '2004-11-26', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 369;  -- Kalinin 3
UPDATE reactors SET first_criticality = '2011-11-08', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 370;  -- Kalinin 4
UPDATE reactors SET first_criticality = '1973-06-25', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 371;  -- Kola 1
UPDATE reactors SET first_criticality = '1974-11-30', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 372;  -- Kola 2
UPDATE reactors SET first_criticality = '1981-02-07', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 373;  -- Kola 3
UPDATE reactors SET first_criticality = '1984-10-07', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 374;  -- Kola 4
UPDATE reactors SET first_criticality = '1976-10-25', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 375;  -- Kursk 1 1
UPDATE reactors SET first_criticality = '1978-12-16', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 376;  -- Kursk 1 2
UPDATE reactors SET first_criticality = '1983-08-09', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 377;  -- Kursk 1 3
UPDATE reactors SET first_criticality = '1985-10-31', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 378;  -- Kursk 1 4
UPDATE reactors SET first_criticality = '2025-05-22', commercial_operation = '2026-04-27', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 379;  -- Kursk 2 1
UPDATE reactors SET first_criticality = '1973-09-12', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 381;  -- Leningrad 1 1
UPDATE reactors SET first_criticality = '1975-05-06', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 382;  -- Leningrad 1 2
UPDATE reactors SET first_criticality = '1979-09-17', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 383;  -- Leningrad 1 3
UPDATE reactors SET first_criticality = '1980-12-29', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 384;  -- Leningrad 1 4
UPDATE reactors SET first_criticality = '2018-02-06', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 385;  -- Leningrad 2 1
UPDATE reactors SET first_criticality = '2020-08-29', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 386;  -- Leningrad 2 2
UPDATE reactors SET first_criticality = '1963-12-17', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 387;  -- Novovoronezh 1 1
UPDATE reactors SET first_criticality = '1969-12-23', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 388;  -- Novovoronezh 1 2
UPDATE reactors SET first_criticality = '1971-12-22', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 389;  -- Novovoronezh 1 3
UPDATE reactors SET first_criticality = '1972-12-25', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 390;  -- Novovoronezh 1 4
UPDATE reactors SET first_criticality = '1980-04-30', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 391;  -- Novovoronezh 1 5
UPDATE reactors SET first_criticality = '2016-05-20', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 392;  -- Novovoronezh 2 1
UPDATE reactors SET first_criticality = '2019-03-22', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 393;  -- Novovoronezh 2 2
UPDATE reactors SET first_criticality = '2001-02-23', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 394;  -- Rostov 1
UPDATE reactors SET first_criticality = '2010-01-22', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 395;  -- Rostov 2
UPDATE reactors SET first_criticality = '2014-12-07', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 396;  -- Rostov 3
UPDATE reactors SET first_criticality = '2017-12-29', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 397;  -- Rostov 4
UPDATE reactors SET first_criticality = '1982-09-10', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 398;  -- Smolensk 1
UPDATE reactors SET first_criticality = '1985-04-08', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 399;  -- Smolensk 2
UPDATE reactors SET first_criticality = '1989-11-29', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 400;  -- Smolensk 3
UPDATE reactors SET first_criticality = '1984-08-07', operator = 'SLOVENSKÉ ELEKTRÁRNE, A.S.', updated_at = CURRENT_TIMESTAMP WHERE id = 403;  -- Bohunice 3
UPDATE reactors SET first_criticality = '1985-08-02', operator = 'SLOVENSKÉ ELEKTRÁRNE, A.S.', updated_at = CURRENT_TIMESTAMP WHERE id = 404;  -- Bohunice 4
UPDATE reactors SET first_criticality = '1998-06-09', operator = 'SLOVENSKÉ ELEKTRÁRNE, A.S.', updated_at = CURRENT_TIMESTAMP WHERE id = 406;  -- Mochovce 1
UPDATE reactors SET first_criticality = '1999-12-01', operator = 'SLOVENSKÉ ELEKTRÁRNE, A.S.', updated_at = CURRENT_TIMESTAMP WHERE id = 407;  -- Mochovce 2
UPDATE reactors SET first_criticality = '2022-10-22', operator = 'SLOVENSKÉ ELEKTRÁRNE, A.S.', updated_at = CURRENT_TIMESTAMP WHERE id = 408;  -- Mochovce 3
UPDATE reactors SET first_criticality = '1981-09-11', operator = 'Nuklearna elektrarna Krško', updated_at = CURRENT_TIMESTAMP WHERE id = 410;  -- Krško 1
UPDATE reactors SET first_criticality = '1984-03-14', operator = 'ESKOM', updated_at = CURRENT_TIMESTAMP WHERE id = 411;  -- Koeberg 1
UPDATE reactors SET first_criticality = '1985-07-07', operator = 'ESKOM', updated_at = CURRENT_TIMESTAMP WHERE id = 412;  -- Koeberg 2
UPDATE reactors SET first_criticality = '1986-01-31', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 413;  -- Hanbit (Yonggwang) 1
UPDATE reactors SET first_criticality = '1986-10-15', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 414;  -- Hanbit (Yonggwang) 2
UPDATE reactors SET first_criticality = '1994-10-13', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 415;  -- Hanbit (Yonggwang) 3
UPDATE reactors SET first_criticality = '1995-07-07', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 416;  -- Hanbit (Yonggwang) 4
UPDATE reactors SET first_criticality = '2001-11-24', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 417;  -- Hanbit (Yonggwang) 5
UPDATE reactors SET first_criticality = '2002-09-01', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 418;  -- Hanbit (Yonggwang) 6
UPDATE reactors SET first_criticality = '1988-02-25', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 419;  -- Hanul (Ulchin) 1
UPDATE reactors SET first_criticality = '1989-02-25', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 420;  -- Hanul (Ulchin) 2
UPDATE reactors SET first_criticality = '1997-12-21', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 421;  -- Hanul (Ulchin) 3
UPDATE reactors SET first_criticality = '1998-12-14', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 422;  -- Hanul (Ulchin) 4
UPDATE reactors SET first_criticality = '2003-11-28', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 423;  -- Hanul (Ulchin) 5
UPDATE reactors SET first_criticality = '2004-12-16', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 424;  -- Hanul (Ulchin) 6
UPDATE reactors SET first_criticality = '1977-06-19', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 425;  -- Kori 1
UPDATE reactors SET first_criticality = '1983-04-09', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 426;  -- Kori 2
UPDATE reactors SET first_criticality = '1985-01-01', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 427;  -- Kori 3
UPDATE reactors SET first_criticality = '1985-10-26', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 428;  -- Kori 4
UPDATE reactors SET first_criticality = '2022-05-22', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 429;  -- Shin-Hanul (Shin-Ulchin) 1
UPDATE reactors SET first_criticality = '2023-12-06', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 430;  -- Shin-Hanul (Shin-Ulchin) 2
UPDATE reactors SET first_criticality = '2010-07-15', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 431;  -- Shin-Kori 1
UPDATE reactors SET first_criticality = '2011-12-27', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 432;  -- Shin-Kori 2
UPDATE reactors SET first_criticality = '2015-12-29', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 433;  -- Shin-Kori 3
UPDATE reactors SET first_criticality = '2019-04-08', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 434;  -- Shin-Kori 4
UPDATE reactors SET first_criticality = '2012-01-06', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 437;  -- Shin-Wolsong 1
UPDATE reactors SET first_criticality = '2015-02-08', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 438;  -- Shin-Wolsong 2
UPDATE reactors SET first_criticality = '1982-11-21', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 439;  -- Wolsong 1
UPDATE reactors SET first_criticality = '1997-01-29', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 440;  -- Wolsong 2
UPDATE reactors SET first_criticality = '1998-02-19', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 441;  -- Wolsong 3
UPDATE reactors SET first_criticality = '1999-04-10', operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 442;  -- Wolsong 4
UPDATE reactors SET first_criticality = '1981-04-05', operator = 'CENTRALES NUCLEARES ALMARAZ-TRILLO (ID/UFG/ENDESA/HC/NUCLENOR)', updated_at = CURRENT_TIMESTAMP WHERE id = 443;  -- Almaraz 1
UPDATE reactors SET first_criticality = '1983-09-19', operator = 'CENTRALES NUCLEARES ALMARAZ-TRILLO (ID/UFG/ENDESA/HC/NUCLENOR)', updated_at = CURRENT_TIMESTAMP WHERE id = 444;  -- Almaraz 2
UPDATE reactors SET first_criticality = '1983-06-16', operator = 'ASOCIACIÓN NUCLEAR ASCÓ-VANDELLÓS A.I.E. (ENDESA/ID)', updated_at = CURRENT_TIMESTAMP WHERE id = 445;  -- Asco 1
UPDATE reactors SET first_criticality = '1985-09-11', operator = 'ASOCIACIÓN NUCLEAR ASCÓ-VANDELLÓS A.I.E. (ENDESA/ID)', updated_at = CURRENT_TIMESTAMP WHERE id = 446;  -- Asco 2
UPDATE reactors SET first_criticality = '1984-08-23', operator = 'IBERDROLA, S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 447;  -- Cofrentes 1
UPDATE reactors SET first_criticality = '1988-05-14', operator = 'CENTRALES NUCLEARES ALMARAZ-TRILLO (ID/UFG/ENDESA/HC/NUCLENOR)', updated_at = CURRENT_TIMESTAMP WHERE id = 450;  -- Trillo 1
UPDATE reactors SET first_criticality = '1987-11-14', operator = 'ASOCIACIÓN NUCLEAR ASCÓ-VANDELLÓS A.I.E. (ENDESA/ID)', updated_at = CURRENT_TIMESTAMP WHERE id = 452;  -- Vandellos 2
UPDATE reactors SET first_criticality = '1980-04-23', operator = 'FORSMARK KRAFTGRUPP AB', updated_at = CURRENT_TIMESTAMP WHERE id = 456;  -- Forsmark 1
UPDATE reactors SET first_criticality = '1980-11-16', operator = 'FORSMARK KRAFTGRUPP AB', updated_at = CURRENT_TIMESTAMP WHERE id = 457;  -- Forsmark 2
UPDATE reactors SET first_criticality = '1984-10-28', operator = 'FORSMARK KRAFTGRUPP AB', updated_at = CURRENT_TIMESTAMP WHERE id = 458;  -- Forsmark 3
UPDATE reactors SET first_criticality = '1984-12-29', operator = 'OKG AKTIEBOLAG', updated_at = CURRENT_TIMESTAMP WHERE id = 461;  -- Oskarshamn 3
UPDATE reactors SET first_criticality = '1980-07-29', operator = 'Ringhals AB', updated_at = CURRENT_TIMESTAMP WHERE id = 464;  -- Ringhals 3
UPDATE reactors SET first_criticality = '1982-05-19', operator = 'Ringhals AB', updated_at = CURRENT_TIMESTAMP WHERE id = 465;  -- Ringhals 4
UPDATE reactors SET first_criticality = '1969-06-30', operator = 'Kernkraftwerk Beznau CH-5312 Döttingen', updated_at = CURRENT_TIMESTAMP WHERE id = 466;  -- Beznau 1
UPDATE reactors SET first_criticality = '1971-10-16', operator = 'Kernkraftwerk Beznau CH-5312 Döttingen', updated_at = CURRENT_TIMESTAMP WHERE id = 467;  -- Beznau 2
UPDATE reactors SET first_criticality = '1979-01-20', operator = 'KERNKRAFTWERK GÖSGEN-DÄNIKEN AG', updated_at = CURRENT_TIMESTAMP WHERE id = 468;  -- Gösgen 1
UPDATE reactors SET first_criticality = '1984-03-09', operator = 'KERNKRAFTWERK LEIBSTADT', updated_at = CURRENT_TIMESTAMP WHERE id = 469;  -- Leibstadt 1
UPDATE reactors SET first_criticality = '2020-07-31', operator = 'Nawah Energy Company', updated_at = CURRENT_TIMESTAMP WHERE id = 482;  -- Barakah 1
UPDATE reactors SET first_criticality = '2021-08-27', operator = 'Nawah Energy Company', updated_at = CURRENT_TIMESTAMP WHERE id = 483;  -- Barakah 2
UPDATE reactors SET first_criticality = '2022-09-22', operator = 'Nawah Energy Company', updated_at = CURRENT_TIMESTAMP WHERE id = 484;  -- Barakah 3
UPDATE reactors SET first_criticality = '2024-03-01', operator = 'Nawah Energy Company', updated_at = CURRENT_TIMESTAMP WHERE id = 485;  -- Barakah 4
UPDATE reactors SET first_criticality = '1982-12-23', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 502;  -- Dungeness B 1
UPDATE reactors SET first_criticality = '1985-12-04', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 503;  -- Dungeness B 2
UPDATE reactors SET first_criticality = '1983-06-24', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 504;  -- Hartlepool 1
UPDATE reactors SET first_criticality = '1984-09-09', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 505;  -- Hartlepool 2
UPDATE reactors SET first_criticality = '1983-04-06', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 506;  -- Heysham A 1
UPDATE reactors SET first_criticality = '1984-06-03', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 507;  -- Heysham A 2
UPDATE reactors SET first_criticality = '1988-06-23', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 508;  -- Heysham B 1
UPDATE reactors SET first_criticality = '1988-11-01', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 509;  -- Heysham B 2
UPDATE reactors SET first_criticality = '1976-09-24', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 512;  -- Hinkley Point B 1
UPDATE reactors SET first_criticality = '1976-02-01', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 513;  -- Hinkley Point B 2
UPDATE reactors SET first_criticality = '1976-01-31', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 518;  -- Hunterston B 1
UPDATE reactors SET first_criticality = '1977-03-27', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 519;  -- Hunterston B 2
UPDATE reactors SET first_criticality = '1995-01-31', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 524;  -- Sizewell B 1
UPDATE reactors SET first_criticality = '1988-03-25', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 525;  -- Torness 1
UPDATE reactors SET first_criticality = '1988-12-23', operator = 'EDF Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 526;  -- Torness 2
UPDATE reactors SET first_criticality = '1987-12-10', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 537;  -- Khmelnytskyi 1
UPDATE reactors SET first_criticality = '2004-08-01', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 538;  -- Khmelnytskyi 2
UPDATE reactors SET first_criticality = '1980-12-17', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 541;  -- Rivne 1
UPDATE reactors SET first_criticality = '1981-12-19', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 542;  -- Rivne 2
UPDATE reactors SET first_criticality = '1986-11-11', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 543;  -- Rivne 3
UPDATE reactors SET first_criticality = '2004-09-26', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 544;  -- Rivne 4
UPDATE reactors SET first_criticality = '1982-12-09', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 545;  -- South Ukraine 1
UPDATE reactors SET first_criticality = '1984-12-30', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 546;  -- South Ukraine 2
UPDATE reactors SET first_criticality = '1989-09-02', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 547;  -- South Ukraine 3
UPDATE reactors SET first_criticality = '1984-12-07', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 548;  -- Zaporizhzhia 1
UPDATE reactors SET first_criticality = '1985-06-28', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 549;  -- Zaporizhzhia 2
UPDATE reactors SET first_criticality = '1986-12-04', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 550;  -- Zaporizhzhia 3
UPDATE reactors SET first_criticality = '1987-12-15', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 551;  -- Zaporizhzhia 4
UPDATE reactors SET first_criticality = '1989-07-20', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 552;  -- Zaporizhzhia 5
UPDATE reactors SET first_criticality = '1995-10-06', operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 553;  -- Zaporizhzhia 6
UPDATE reactors SET first_criticality = '1974-08-06', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 554;  -- Arkansas Nuclear One 1
UPDATE reactors SET first_criticality = '1978-12-05', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 555;  -- Arkansas Nuclear One 2
UPDATE reactors SET first_criticality = '1976-05-10', operator = 'FIRST ENERGY NUCLEAR OPERATING CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 556;  -- Beaver Valley 1
UPDATE reactors SET first_criticality = '1987-08-04', operator = 'FIRST ENERGY NUCLEAR OPERATING CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 557;  -- Beaver Valley 2
UPDATE reactors SET first_criticality = '1987-05-29', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 560;  -- Braidwood 1
UPDATE reactors SET first_criticality = '1988-03-08', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 561;  -- Braidwood 2
UPDATE reactors SET first_criticality = '1973-08-17', operator = 'Tennessee Valley Authority', updated_at = CURRENT_TIMESTAMP WHERE id = 562;  -- Browns Ferry 1
UPDATE reactors SET first_criticality = '1974-07-20', operator = 'Tennessee Valley Authority', updated_at = CURRENT_TIMESTAMP WHERE id = 563;  -- Browns Ferry 2
UPDATE reactors SET first_criticality = '1976-08-08', operator = 'Tennessee Valley Authority', updated_at = CURRENT_TIMESTAMP WHERE id = 564;  -- Browns Ferry 3
UPDATE reactors SET first_criticality = '1976-10-08', operator = 'Progress Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 565;  -- Brunswick 1
UPDATE reactors SET first_criticality = '1975-03-20', operator = 'Progress Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 566;  -- Brunswick 2
UPDATE reactors SET first_criticality = '1985-02-02', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 567;  -- Byron 1
UPDATE reactors SET first_criticality = '1987-01-09', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 568;  -- Byron 2
UPDATE reactors SET first_criticality = '1984-10-02', operator = 'AMEREN UE, Union Electric Company', updated_at = CURRENT_TIMESTAMP WHERE id = 569;  -- Callaway 1
UPDATE reactors SET first_criticality = '1974-10-07', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 570;  -- Calvert Cliffs 1
UPDATE reactors SET first_criticality = '1976-11-30', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 571;  -- Calvert Cliffs 2
UPDATE reactors SET first_criticality = '1985-01-07', operator = 'Duke Energy Corp.', updated_at = CURRENT_TIMESTAMP WHERE id = 572;  -- Catawba 1
UPDATE reactors SET first_criticality = '1986-05-08', operator = 'Duke Energy Corp.', updated_at = CURRENT_TIMESTAMP WHERE id = 573;  -- Catawba 2
UPDATE reactors SET first_criticality = '1987-02-27', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 574;  -- Clinton 1
UPDATE reactors SET first_criticality = '1984-01-19', operator = 'Energy Northwest', updated_at = CURRENT_TIMESTAMP WHERE id = 575;  -- Columbia 1
UPDATE reactors SET first_criticality = '1990-04-03', operator = 'Luminant Generation Company, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 576;  -- Comanche Peak 1
UPDATE reactors SET first_criticality = '1993-03-24', operator = 'Luminant Generation Company, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 577;  -- Comanche Peak 2
UPDATE reactors SET first_criticality = '1975-01-18', operator = 'American Electric Power Company, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 578;  -- Cook (Donald C. Cook) 1
UPDATE reactors SET first_criticality = '1978-03-10', operator = 'American Electric Power Company, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 579;  -- Cook (Donald C. Cook) 2
UPDATE reactors SET first_criticality = '1974-02-21', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 580;  -- Cooper 1
UPDATE reactors SET first_criticality = '1977-08-12', operator = 'FIRST ENERGY NUCLEAR OPERATING CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 583;  -- Davis Besse 1
UPDATE reactors SET first_criticality = '1984-04-29', operator = 'Pacific Gas and Electric Company', updated_at = CURRENT_TIMESTAMP WHERE id = 584;  -- Diablo Canyon 1
UPDATE reactors SET first_criticality = '1985-08-19', operator = 'Pacific Gas and Electric Company', updated_at = CURRENT_TIMESTAMP WHERE id = 585;  -- Diablo Canyon 2
UPDATE reactors SET first_criticality = '1970-01-07', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 587;  -- Dresden 2
UPDATE reactors SET first_criticality = '1971-01-12', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 588;  -- Dresden 3
UPDATE reactors SET first_criticality = '1977-08-09', operator = 'Southern Nuclear Operating Company, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 591;  -- Farley (Joseph M. Farley) 1
UPDATE reactors SET first_criticality = '1981-05-05', operator = 'Southern Nuclear Operating Company, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 592;  -- Farley (Joseph M. Farley) 2
UPDATE reactors SET first_criticality = '1985-06-21', operator = 'DETROIT EDISON CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 594;  -- Fermi 2
UPDATE reactors SET first_criticality = '1974-11-17', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 595;  -- Fitzpatrick (James A. Fitzpatrick) 1
UPDATE reactors SET first_criticality = '1969-11-08', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 599;  -- Ginna (R. E. Ginna) 1
UPDATE reactors SET first_criticality = '1982-08-18', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 600;  -- Grand Gulf 1
UPDATE reactors SET first_criticality = '1987-01-03', operator = 'Progress Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 603;  -- Harris (Shearon Harris) 1
UPDATE reactors SET first_criticality = '1974-09-12', operator = 'Southern Nuclear Operating Company, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 604;  -- Hatch (Edwin I. Hatch) 1
UPDATE reactors SET first_criticality = '1978-07-04', operator = 'Southern Nuclear Operating Company, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 605;  -- Hatch (Edwin I. Hatch) 2
UPDATE reactors SET first_criticality = '1986-06-28', operator = 'PSEG Nuclear, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 606;  -- Hope Creek 1
UPDATE reactors SET first_criticality = '1982-06-21', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 613;  -- LaSalle 1
UPDATE reactors SET first_criticality = '1984-03-10', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 614;  -- LaSalle 2
UPDATE reactors SET first_criticality = '1984-12-22', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 615;  -- Limerick 1
UPDATE reactors SET first_criticality = '1989-08-12', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 616;  -- Limerick 2
UPDATE reactors SET first_criticality = '1981-08-08', operator = 'Duke Energy Corp.', updated_at = CURRENT_TIMESTAMP WHERE id = 618;  -- McGuire 1
UPDATE reactors SET first_criticality = '1983-05-08', operator = 'Duke Energy Corp.', updated_at = CURRENT_TIMESTAMP WHERE id = 619;  -- McGuire 2
UPDATE reactors SET first_criticality = '1975-10-17', operator = 'Dominion Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 621;  -- Millstone 2
UPDATE reactors SET first_criticality = '1986-01-23', operator = 'Dominion Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 622;  -- Millstone 3
UPDATE reactors SET first_criticality = '1970-12-10', operator = 'Northern States Power Co. (subsidiary of Xcel Energy)', updated_at = CURRENT_TIMESTAMP WHERE id = 623;  -- Monticello 1
UPDATE reactors SET first_criticality = '1969-09-05', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 624;  -- Nine Mile Point 1
UPDATE reactors SET first_criticality = '1987-05-23', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 625;  -- Nine Mile Point 2
UPDATE reactors SET first_criticality = '1978-04-05', operator = 'Dominion Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 626;  -- North Anna 1
UPDATE reactors SET first_criticality = '1980-06-12', operator = 'Dominion Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 627;  -- North Anna 2
UPDATE reactors SET first_criticality = '1973-04-19', operator = 'Duke Energy Corp.', updated_at = CURRENT_TIMESTAMP WHERE id = 628;  -- Oconee 1
UPDATE reactors SET first_criticality = '1973-11-11', operator = 'Duke Energy Corp.', updated_at = CURRENT_TIMESTAMP WHERE id = 629;  -- Oconee 2
UPDATE reactors SET first_criticality = '1974-09-05', operator = 'Duke Energy Corp.', updated_at = CURRENT_TIMESTAMP WHERE id = 630;  -- Oconee 3
UPDATE reactors SET first_criticality = '1985-05-25', operator = 'ARIZONA PUBLIC SERVICE CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 633;  -- Palo Verde 1
UPDATE reactors SET first_criticality = '1986-04-18', operator = 'ARIZONA PUBLIC SERVICE CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 634;  -- Palo Verde 2
UPDATE reactors SET first_criticality = '1987-10-25', operator = 'ARIZONA PUBLIC SERVICE CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 635;  -- Palo Verde 3
UPDATE reactors SET first_criticality = '1973-09-16', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 638;  -- Peach Bottom 2
UPDATE reactors SET first_criticality = '1974-08-07', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 639;  -- Peach Bottom 3
UPDATE reactors SET first_criticality = '1986-06-06', operator = 'FIRST ENERGY NUCLEAR OPERATING CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 640;  -- Perry 1
UPDATE reactors SET first_criticality = '1970-11-02', operator = 'NextEra Energy Resources, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 643;  -- Point Beach 1
UPDATE reactors SET first_criticality = '1972-05-30', operator = 'NextEra Energy Resources, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 644;  -- Point Beach 2
UPDATE reactors SET first_criticality = '1973-12-01', operator = 'Northern States Power Co. (subsidiary of Xcel Energy)', updated_at = CURRENT_TIMESTAMP WHERE id = 645;  -- Prairie Island 1
UPDATE reactors SET first_criticality = '1974-12-17', operator = 'Northern States Power Co. (subsidiary of Xcel Energy)', updated_at = CURRENT_TIMESTAMP WHERE id = 646;  -- Prairie Island 2
UPDATE reactors SET first_criticality = '1971-10-18', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 647;  -- Quad Cities 1
UPDATE reactors SET first_criticality = '1972-04-26', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 648;  -- Quad Cities 2
UPDATE reactors SET first_criticality = '1985-10-31', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 650;  -- River Bend 1
UPDATE reactors SET first_criticality = '1970-09-20', operator = 'Progress Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 651;  -- Robinson (H B Robinson) 2
UPDATE reactors SET first_criticality = '1976-12-11', operator = 'PSEG Nuclear, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 652;  -- Salem 1
UPDATE reactors SET first_criticality = '1980-08-08', operator = 'PSEG Nuclear, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 653;  -- Salem 2
UPDATE reactors SET first_criticality = '1989-06-13', operator = 'NextEra Energy Resources, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 658;  -- Seabrook 1
UPDATE reactors SET first_criticality = '1980-07-05', operator = 'Tennessee Valley Authority', updated_at = CURRENT_TIMESTAMP WHERE id = 659;  -- Sequoyah 1
UPDATE reactors SET first_criticality = '1981-11-05', operator = 'Tennessee Valley Authority', updated_at = CURRENT_TIMESTAMP WHERE id = 660;  -- Sequoyah 2
UPDATE reactors SET first_criticality = '1988-03-08', operator = 'STP Nuclear Operating Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 663;  -- South Texas Project 1
UPDATE reactors SET first_criticality = '1989-03-12', operator = 'STP Nuclear Operating Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 664;  -- South Texas Project 2
UPDATE reactors SET first_criticality = '1976-04-22', operator = 'Florida Power & Light Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 665;  -- St Lucie 1
UPDATE reactors SET first_criticality = '1983-06-02', operator = 'Florida Power & Light Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 666;  -- St Lucie 2
UPDATE reactors SET first_criticality = '1982-10-22', operator = 'SOUTH CAROLINA ELECTRIC & GAS CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 667;  -- Summer (V C Summer) 1
UPDATE reactors SET first_criticality = '1972-07-01', operator = 'Dominion Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 668;  -- Surry 1
UPDATE reactors SET first_criticality = '1973-03-07', operator = 'Dominion Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 669;  -- Surry 2
UPDATE reactors SET first_criticality = '1982-09-10', operator = 'PPL Susquehanna, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 670;  -- Susquehanna 1
UPDATE reactors SET first_criticality = '1984-05-08', operator = 'PPL Susquehanna, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 671;  -- Susquehanna 2
UPDATE reactors SET first_criticality = '1972-10-20', operator = 'Florida Power & Light Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 675;  -- Turkey Point 3
UPDATE reactors SET first_criticality = '1973-06-11', operator = 'Florida Power & Light Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 676;  -- Turkey Point 4
UPDATE reactors SET first_criticality = '1987-03-09', operator = 'Southern Nuclear Operating Company, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 678;  -- Vogtle 1
UPDATE reactors SET first_criticality = '1989-03-28', operator = 'Southern Nuclear Operating Company, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 679;  -- Vogtle 2
UPDATE reactors SET first_criticality = '2023-03-01', operator = 'Southern Nuclear Operating Company, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 680;  -- Vogtle 3
UPDATE reactors SET first_criticality = '2024-02-14', operator = 'Southern Nuclear Operating Company, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 681;  -- Vogtle 4
UPDATE reactors SET first_criticality = '1985-03-04', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 682;  -- Waterford 3
UPDATE reactors SET first_criticality = '1996-01-01', operator = 'Tennessee Valley Authority', updated_at = CURRENT_TIMESTAMP WHERE id = 683;  -- Watts Bar 1
UPDATE reactors SET first_criticality = '2016-05-23', operator = 'Tennessee Valley Authority', updated_at = CURRENT_TIMESTAMP WHERE id = 684;  -- Watts Bar 2
UPDATE reactors SET first_criticality = '1985-05-22', operator = 'WOLF CREEK NUCLEAR OPERATING CORP.', updated_at = CURRENT_TIMESTAMP WHERE id = 685;  -- Wolf Creek 1
UPDATE reactors SET first_criticality = '2029-12-11', grid_connection = '2030-03-06', commercial_operation = '2030-10-20', operator = 'Joint Stock Company ''Concern Rosenergoatom''', thermal_capacity_mw = 3200, net_capacity_mw = 1064, reference_power_mw = 1064, updated_at = CURRENT_TIMESTAMP WHERE id = 726;  -- Leningrad 2 3
UPDATE reactors SET first_criticality = '2031-12-13', grid_connection = '2032-03-06', commercial_operation = '2032-10-20', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 738;  -- Leningrad 2 4
UPDATE reactors SET pris_id = 1055, operator = 'COMISION NACIONAL DE ENERGIA ATOMICA', updated_at = CURRENT_TIMESTAMP WHERE id = 3;  -- Carem25 1
UPDATE reactors SET pris_id = 1, first_criticality = '1976-12-15', operator = 'Closed Joint Stock Company Armenian NPP', updated_at = CURRENT_TIMESTAMP WHERE id = 5;  -- Armenian 1
UPDATE reactors SET pris_id = 1078, operator = 'Nuclear Power Plant Company Bangladesh Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 7;  -- Rooppur 1
UPDATE reactors SET pris_id = 1079, operator = 'Nuclear Power Plant Company Bangladesh Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 8;  -- Rooppur 2
UPDATE reactors SET pris_id = 8, first_criticality = '1962-08-29', operator = 'CENTRE D''ETUDE DE L''ENERGIE NUCLEAIRE / STUDIECENTRUM VOOR KERNENERGIE', updated_at = CURRENT_TIMESTAMP WHERE id = 11;  -- BR-3 1
UPDATE reactors SET pris_id = 9, first_criticality = '1974-07-18', operator = 'ENGIE ELECTRABEL + EDF BELGIUM + EDF LUMINUS', updated_at = CURRENT_TIMESTAMP WHERE id = 12;  -- Doel 1
UPDATE reactors SET pris_id = 11, first_criticality = '1975-08-04', operator = 'ENGIE ELECTRABEL + EDF BELGIUM + EDF LUMINUS', updated_at = CURRENT_TIMESTAMP WHERE id = 13;  -- Doel 2
UPDATE reactors SET pris_id = 12, first_criticality = '1982-06-14', operator = 'ENGIE ELECTRABEL + EDF BELGIUM + EDF LUMINUS', updated_at = CURRENT_TIMESTAMP WHERE id = 14;  -- Doel 3
UPDATE reactors SET pris_id = 10, first_criticality = '1975-02-21', operator = 'ENGIE ELECTRABEL', updated_at = CURRENT_TIMESTAMP WHERE id = 16;  -- Tihange 1
UPDATE reactors SET pris_id = 13, first_criticality = '1982-10-05', operator = 'ENGIE ELECTRABEL', updated_at = CURRENT_TIMESTAMP WHERE id = 17;  -- Tihange 2
UPDATE reactors SET pris_id = 26, first_criticality = '2033-07-04', grid_connection = '2033-07-14', commercial_operation = '2033-11-01', operator = 'ELETRONUCLEAR S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 21;  -- Angra 3
UPDATE reactors SET pris_id = 16, first_criticality = '1974-06-30', operator = 'Kozloduy Npp ,lc', updated_at = CURRENT_TIMESTAMP WHERE id = 22;  -- Kozloduy 1
UPDATE reactors SET pris_id = 17, first_criticality = '1975-08-22', operator = 'Kozloduy Npp ,lc', updated_at = CURRENT_TIMESTAMP WHERE id = 23;  -- Kozloduy 2
UPDATE reactors SET pris_id = 18, first_criticality = '1980-12-04', operator = 'Kozloduy Npp ,lc', updated_at = CURRENT_TIMESTAMP WHERE id = 24;  -- Kozloduy 3
UPDATE reactors SET pris_id = 19, first_criticality = '1982-04-25', operator = 'Kozloduy Npp ,lc', updated_at = CURRENT_TIMESTAMP WHERE id = 25;  -- Kozloduy 4
UPDATE reactors SET pris_id = 40, first_criticality = '1966-11-15', operator = 'ONTARIO HYDRO', updated_at = CURRENT_TIMESTAMP WHERE id = 40;  -- Douglas Point 1
UPDATE reactors SET pris_id = 47, first_criticality = '1970-11-12', operator = 'HYDRO QUEBEC', updated_at = CURRENT_TIMESTAMP WHERE id = 41;  -- Gentilly 1
UPDATE reactors SET pris_id = 32, first_criticality = '1982-09-11', operator = 'HYDRO QUEBEC', updated_at = CURRENT_TIMESTAMP WHERE id = 42;  -- Gentilly 2
UPDATE reactors SET pris_id = 29, first_criticality = '1962-04-11', operator = 'ONTARIO HYDRO', updated_at = CURRENT_TIMESTAMP WHERE id = 52;  -- Rolphton NPD 1
UPDATE reactors SET pris_id = 1101, operator = 'CHINA NATIONAL NUCLEAR CORPORATION', updated_at = CURRENT_TIMESTAMP WHERE id = 54;  -- CFR 1
UPDATE reactors SET pris_id = 2121, construction_start = '2020-12-27', operator = 'CHINA NATIONAL NUCLEAR CORPORATION', updated_at = CURRENT_TIMESTAMP WHERE id = 55;  -- CFR 2
UPDATE reactors SET pris_id = 1091, first_criticality = '2026-06-25', operator = 'CGN Huizhou Nuclear Power Co.,Ltd,', updated_at = CURRENT_TIMESTAMP WHERE id = 99;  -- Taipingling 2
UPDATE reactors SET pris_id = 172, first_criticality = '1958-07-21', operator = 'COMPAGNIE GENERALE DES MATIERES NUCLEAIRES', net_capacity_mw = 39, reference_power_mw = 39, updated_at = CURRENT_TIMESTAMP WHERE id = 127;  -- G2 2
UPDATE reactors SET pris_id = 161, first_criticality = '1959-06-11', operator = 'COMPAGNIE GENERALE DES MATIERES NUCLEAIRES', updated_at = CURRENT_TIMESTAMP WHERE id = 128;  -- G3 3
UPDATE reactors SET pris_id = 173, first_criticality = '1962-09-16', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 129;  -- Chinon A (EDF1) 1
UPDATE reactors SET pris_id = 184, first_criticality = '1964-08-17', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 130;  -- Chinon A (EDF2) 2
UPDATE reactors SET pris_id = 195, first_criticality = '1966-03-01', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 131;  -- Chinon A (EDF3) 3
UPDATE reactors SET pris_id = 206, first_criticality = '1966-10-18', operator = 'SOCIETE D''ENERGIE NUCLEAIRE FRANCO-BELGE DES ARDENNES', updated_at = CURRENT_TIMESTAMP WHERE id = 132;  -- Chooz-A 1
UPDATE reactors SET pris_id = 217, first_criticality = '1966-12-23', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 133;  -- Brennilis 1
UPDATE reactors SET pris_id = 225, first_criticality = '1969-01-07', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 138;  -- St. Laurent A 1
UPDATE reactors SET pris_id = 230, first_criticality = '1972-03-21', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 139;  -- Bugey 1
UPDATE reactors SET pris_id = 178, first_criticality = '1985-09-07', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 152;  -- Super-Phenix 1
UPDATE reactors SET pris_id = 163, first_criticality = '1977-03-07', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 163;  -- Fessenheim 1
UPDATE reactors SET pris_id = 164, first_criticality = '1977-06-27', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 164;  -- Fessenheim 2
UPDATE reactors SET pris_id = 162, first_criticality = '1973-08-31', operator = 'Commissariat à l''Energie Atomique (80%) Electricité de France (20%)', updated_at = CURRENT_TIMESTAMP WHERE id = 186;  -- Phenix 1
UPDATE reactors SET pris_id = 229, first_criticality = '1971-07-04', operator = 'ÉLECTRICITÉ DE FRANCE', updated_at = CURRENT_TIMESTAMP WHERE id = 190;  -- St. Laurent A 2
UPDATE reactors SET pris_id = 100, first_criticality = '1984-03-09', operator = 'RWE Nuclear GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 198;  -- Gundremmingen B
UPDATE reactors SET pris_id = 108, first_criticality = '1988-04-14', operator = 'Kernkraftwerke Lippe-Ems GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 199;  -- Emsland 1
UPDATE reactors SET pris_id = 106, first_criticality = '1988-01-15', operator = 'PreussenElektra GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 200;  -- Isar 2
UPDATE reactors SET pris_id = 119, first_criticality = '1988-12-29', operator = 'EnBW Kernkraft GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 201;  -- Neckarwestheim 2
UPDATE reactors SET pris_id = 107, first_criticality = '1986-10-08', operator = 'PreussenElektra GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 202;  -- Brokdorf 1
UPDATE reactors SET pris_id = 101, first_criticality = '1984-09-01', operator = 'PreussenElektra GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 203;  -- Grohnde 1
UPDATE reactors SET pris_id = 102, first_criticality = '1984-10-26', operator = 'RWE Nuclear GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 204;  -- Gundremmingen C
UPDATE reactors SET pris_id = 98, first_criticality = '1984-12-13', operator = 'EnBW Kernkraft GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 205;  -- Philippsburg 2
UPDATE reactors SET pris_id = 97, first_criticality = '1981-12-09', operator = 'PreussenElektra GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 206;  -- Grafenrheinfeld 1
UPDATE reactors SET pris_id = 85, first_criticality = '1974-07-16', operator = 'RWE Power AG', updated_at = CURRENT_TIMESTAMP WHERE id = 207;  -- Biblis A
UPDATE reactors SET pris_id = 91, first_criticality = '1976-03-25', operator = 'RWE Power AG', updated_at = CURRENT_TIMESTAMP WHERE id = 208;  -- Biblis B
UPDATE reactors SET pris_id = 86, first_criticality = '1976-06-23', operator = 'Kernkraftwerk Brunsbüttel GmbH & Co. oHG', updated_at = CURRENT_TIMESTAMP WHERE id = 209;  -- Brunsbüttel 1
UPDATE reactors SET pris_id = 89, first_criticality = '1977-11-20', operator = 'PreussenElektra GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 210;  -- Isar 1
UPDATE reactors SET pris_id = 94, first_criticality = '1983-09-14', operator = 'Kernkraftwerk Krümmel GmbH & Co. oHG', updated_at = CURRENT_TIMESTAMP WHERE id = 211;  -- Krümmel 1
UPDATE reactors SET pris_id = 88, first_criticality = '1976-05-26', operator = 'EnBW Kernkraft GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 212;  -- Neckarwestheim 1
UPDATE reactors SET pris_id = 87, first_criticality = '1979-03-09', operator = 'EnBW Kernkraft GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 213;  -- Philippsburg 1
UPDATE reactors SET pris_id = 90, first_criticality = '1978-09-16', operator = 'PreussenElektra GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 214;  -- Unterweser 1
UPDATE reactors SET pris_id = 121, first_criticality = '1968-09-22', operator = 'EnBW Kraftwerke AG', updated_at = CURRENT_TIMESTAMP WHERE id = 215;  -- Obrigheim 1
UPDATE reactors SET pris_id = 83, first_criticality = '1972-01-08', operator = 'PreussenElektra GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 216;  -- Stade 1
UPDATE reactors SET pris_id = 136, first_criticality = '1971-10-20', operator = 'PreussenElektra GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 217;  -- Würgassen 1
UPDATE reactors SET pris_id = 135, first_criticality = '1977-10-10', operator = 'KERNKRAFTWERK-BETRIEBSGESELLSCHAFT MBH', updated_at = CURRENT_TIMESTAMP WHERE id = 218;  -- KNK II 1
UPDATE reactors SET pris_id = 126, first_criticality = '1979-07-22', operator = 'ENERGIEWERKE Nord GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 219;  -- Greifswald 4
UPDATE reactors SET pris_id = 122, first_criticality = '1966-03-01', operator = 'ENERGIEWERKE Nord GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 220;  -- Rheinsberg 1
UPDATE reactors SET pris_id = 125, first_criticality = '1977-10-16', operator = 'ENERGIEWERKE Nord GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 221;  -- Greifswald 3
UPDATE reactors SET pris_id = 123, first_criticality = '1973-12-15', operator = 'ENERGIEWERKE Nord GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 222;  -- Greifswald 1
UPDATE reactors SET pris_id = 124, first_criticality = '1974-12-03', operator = 'ENERGIEWERKE Nord GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 223;  -- Greifswald 2
UPDATE reactors SET pris_id = 127, first_criticality = '1989-03-26', operator = 'ENERGIEWERKE Nord GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 224;  -- Greifswald 5
UPDATE reactors SET pris_id = 114, first_criticality = '1966-08-16', operator = 'ARBEITSGEMEINSCHAFT VERSUCHSREAKTOR GMBH', updated_at = CURRENT_TIMESTAMP WHERE id = 225;  -- AVR Jülich 1
UPDATE reactors SET pris_id = 92, first_criticality = '1983-09-13', operator = 'HOCHTEMPERATUR-KERNKRAFTWERK GMBH', updated_at = CURRENT_TIMESTAMP WHERE id = 226;  -- THTR-300 1
UPDATE reactors SET pris_id = 96, first_criticality = '1986-03-01', operator = 'RWE Nuclear GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 227;  -- Mülheim-Kärlich 1
UPDATE reactors SET pris_id = 82, first_criticality = '1960-11-13', operator = 'VERSUCHSATOMKRAFTWERK KAHL GMBH', updated_at = CURRENT_TIMESTAMP WHERE id = 228;  -- Vak Kahl 1
UPDATE reactors SET pris_id = 93, first_criticality = '1965-09-29', operator = 'KERNKRAFTWERK-BETRIEBSGESELLSCHAFT MBH', updated_at = CURRENT_TIMESTAMP WHERE id = 229;  -- MZFR 1
UPDATE reactors SET pris_id = 104, first_criticality = '1966-08-14', operator = 'RWE Nuclear GmbH', updated_at = CURRENT_TIMESTAMP WHERE id = 230;  -- Gundremmingen A
UPDATE reactors SET pris_id = 133, first_criticality = '1968-01-31', operator = 'Kernkraftwerk Lingen GmbH (RWE Nuclear GmbH)', updated_at = CURRENT_TIMESTAMP WHERE id = 231;  -- Lingen 1
UPDATE reactors SET pris_id = 84, first_criticality = '1972-12-17', operator = 'KERNKRAFTWERK NIEDERAICHBACH GMBH', updated_at = CURRENT_TIMESTAMP WHERE id = 232;  -- Niederaichbach 1
UPDATE reactors SET pris_id = 134, first_criticality = '1969-10-14', operator = 'HEISSDAMPFREAKTOR-BETRIEBSGESELLSCHAFT MBH.', updated_at = CURRENT_TIMESTAMP WHERE id = 233;  -- HDR Großwelzheim 1
UPDATE reactors SET pris_id = 1059, operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 248;  -- Kudankulam 3
UPDATE reactors SET pris_id = 1060, operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 249;  -- Kudankulam 4
UPDATE reactors SET pris_id = 859, operator = 'Bharatiya Nabhikiya Vidyut Nigam Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 254;  -- PFBR 1
UPDATE reactors SET pris_id = 302, first_criticality = '1972-08-11', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 255;  -- Rajasthan 1
UPDATE reactors SET pris_id = 299, operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 262;  -- Rajasthan 8
UPDATE reactors SET pris_id = 285, first_criticality = '1969-02-01', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 263;  -- Tarapur 1
UPDATE reactors SET pris_id = 296, first_criticality = '1969-02-28', operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 264;  -- Tarapur 2
UPDATE reactors SET pris_id = 311, operator = 'Nuclear Power Production and Development Co. of Iran', thermal_capacity_mw = 3012, updated_at = CURRENT_TIMESTAMP WHERE id = 268;  -- Bushehr 2
UPDATE reactors SET pris_id = 327, first_criticality = '1977-12-31', operator = 'Societa Gestione Impanti Nucleari S.p.a.', updated_at = CURRENT_TIMESTAMP WHERE id = 269;  -- Caorso 1
UPDATE reactors SET pris_id = 326, first_criticality = '1964-06-21', operator = 'Societa Gestione Impanti Nucleari S.p.a.', updated_at = CURRENT_TIMESTAMP WHERE id = 270;  -- Enrico Fermi 1
UPDATE reactors SET pris_id = 325, first_criticality = '1963-06-05', operator = 'Societa Gestione Impanti Nucleari S.p.a.', updated_at = CURRENT_TIMESTAMP WHERE id = 271;  -- Garigliano 1
UPDATE reactors SET pris_id = 318, first_criticality = '1962-12-27', operator = 'Societa Gestione Impanti Nucleari S.p.a.', updated_at = CURRENT_TIMESTAMP WHERE id = 272;  -- Latina 1
UPDATE reactors SET pris_id = 345, first_criticality = '1978-03-20', operator = 'JAPAN ATOMIC ENERGY AGENCY', updated_at = CURRENT_TIMESTAMP WHERE id = 273;  -- Fugen ATR 1
UPDATE reactors SET pris_id = 377, first_criticality = '1970-10-10', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 274;  -- Fukushima-Daiichi 1
UPDATE reactors SET pris_id = 389, first_criticality = '1973-05-10', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 275;  -- Fukushima-Daiichi 2
UPDATE reactors SET pris_id = 334, first_criticality = '1974-09-06', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 276;  -- Fukushima-Daiichi 3
UPDATE reactors SET pris_id = 340, first_criticality = '1978-01-28', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 277;  -- Fukushima-Daiichi 4
UPDATE reactors SET pris_id = 341, first_criticality = '1977-08-26', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 278;  -- Fukushima-Daiichi 5
UPDATE reactors SET pris_id = 342, first_criticality = '1979-03-09', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 279;  -- Fukushima-Daiichi 6
UPDATE reactors SET pris_id = 350, first_criticality = '1981-06-17', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 280;  -- Fukushima-Daini 1
UPDATE reactors SET pris_id = 351, first_criticality = '1983-04-26', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 281;  -- Fukushima-Daini 2
UPDATE reactors SET pris_id = 361, first_criticality = '1984-10-18', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 282;  -- Fukushima-Daini 3
UPDATE reactors SET pris_id = 364, first_criticality = '1986-10-24', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 283;  -- Fukushima-Daini 4
UPDATE reactors SET pris_id = 336, first_criticality = '1975-01-28', operator = 'Kyushu Electric Power Co., Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 284;  -- Genkai 1
UPDATE reactors SET pris_id = 352, first_criticality = '1980-05-21', operator = 'Kyushu Electric Power Co., Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 285;  -- Genkai 2
UPDATE reactors SET pris_id = 335, first_criticality = '1974-06-20', operator = 'CHUBU ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 288;  -- Hamaoka 1
UPDATE reactors SET pris_id = 349, first_criticality = '1978-03-28', operator = 'CHUBU ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 289;  -- Hamaoka 2
UPDATE reactors SET pris_id = 362, first_criticality = '1986-11-21', operator = 'CHUBU ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 290;  -- Hamaoka 3
UPDATE reactors SET pris_id = 376, first_criticality = '1992-12-02', operator = 'CHUBU ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 291;  -- Hamaoka 4
UPDATE reactors SET pris_id = 843, first_criticality = '2004-03-23', operator = 'CHUBU ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 292;  -- Hamaoka 5
UPDATE reactors SET pris_id = 841, first_criticality = '2005-01-24', operator = 'Tohoku Electric Power Co., Inc', updated_at = CURRENT_TIMESTAMP WHERE id = 293;  -- Higashi Dori 1
UPDATE reactors SET pris_id = 348, first_criticality = '1977-01-29', operator = 'SHIKOKU ELECTRIC POWER CO., INC', updated_at = CURRENT_TIMESTAMP WHERE id = 294;  -- Ikata 1
UPDATE reactors SET pris_id = 358, first_criticality = '1981-07-31', operator = 'SHIKOKU ELECTRIC POWER CO., INC', updated_at = CURRENT_TIMESTAMP WHERE id = 295;  -- Ikata 2
UPDATE reactors SET pris_id = 333, first_criticality = '1963-08-22', operator = 'JAPAN ATOMIC ENERGY AGENCY', updated_at = CURRENT_TIMESTAMP WHERE id = 297;  -- JPDR 1
UPDATE reactors SET pris_id = 359, first_criticality = '1984-12-12', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 298;  -- Kashiwazaki Kariwa 1
UPDATE reactors SET pris_id = 365, first_criticality = '1989-11-30', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 299;  -- Kashiwazaki Kariwa 2
UPDATE reactors SET pris_id = 380, first_criticality = '1992-10-19', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 300;  -- Kashiwazaki Kariwa 3
UPDATE reactors SET pris_id = 381, first_criticality = '1993-11-01', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 301;  -- Kashiwazaki Kariwa 4
UPDATE reactors SET pris_id = 367, first_criticality = '1989-07-20', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 302;  -- Kashiwazaki Kariwa 5
UPDATE reactors SET pris_id = 384, first_criticality = '1996-11-01', operator = 'Tokyo Electric Power Company Holdings, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 304;  -- Kashiwazaki Kariwa 7
UPDATE reactors SET pris_id = 366, first_criticality = '1970-07-29', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 305;  -- Mihama 1
UPDATE reactors SET pris_id = 386, first_criticality = '1972-04-10', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 306;  -- Mihama 2
UPDATE reactors SET pris_id = 357, first_criticality = '1994-04-05', operator = 'JAPAN ATOMIC ENERGY AGENCY', updated_at = CURRENT_TIMESTAMP WHERE id = 308;  -- Monju 1
UPDATE reactors SET pris_id = 339, first_criticality = '1977-12-02', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 309;  -- Ohi 1
UPDATE reactors SET pris_id = 343, first_criticality = '1978-09-14', operator = 'Kansai Electric Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 310;  -- Ohi 2
UPDATE reactors SET pris_id = 867, operator = 'ELECTRIC POWER DEVELOPMENT CO., LTD.', updated_at = CURRENT_TIMESTAMP WHERE id = 313;  -- Ohma 1
UPDATE reactors SET pris_id = 347, first_criticality = '1983-10-18', operator = 'Tohoku Electric Power Co., Inc', updated_at = CURRENT_TIMESTAMP WHERE id = 314;  -- Onagawa 1
UPDATE reactors SET pris_id = 385, first_criticality = '2001-04-26', operator = 'Tohoku Electric Power Co., Inc', updated_at = CURRENT_TIMESTAMP WHERE id = 316;  -- Onagawa 3
UPDATE reactors SET pris_id = 375, first_criticality = '1992-11-20', operator = 'HOKURIKU ELECTRIC POWER CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 319;  -- Shika 1
UPDATE reactors SET pris_id = 842, first_criticality = '2005-05-26', operator = 'HOKURIKU ELECTRIC POWER CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 320;  -- Shika 2
UPDATE reactors SET pris_id = 387, first_criticality = '1973-06-01', operator = 'THE CHUGOKU ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 321;  -- Shimane 1
UPDATE reactors SET pris_id = 862, operator = 'THE CHUGOKU ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 323;  -- Shimane 3
UPDATE reactors SET pris_id = 344, first_criticality = '1965-05-04', operator = 'JAPAN ATOMIC POWER CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 328;  -- Tokai 1
UPDATE reactors SET pris_id = 346, first_criticality = '1978-01-18', operator = 'JAPAN ATOMIC POWER CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 329;  -- Tokai 2
UPDATE reactors SET pris_id = 370, first_criticality = '1988-11-16', operator = 'HOKKAIDO ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 330;  -- Tomari 1
UPDATE reactors SET pris_id = 371, first_criticality = '1990-07-25', operator = 'HOKKAIDO ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 331;  -- Tomari 2
UPDATE reactors SET pris_id = 856, first_criticality = '2009-03-03', operator = 'HOKKAIDO ELECTRIC POWER CO., INC.', updated_at = CURRENT_TIMESTAMP WHERE id = 332;  -- Tomari 3
UPDATE reactors SET pris_id = 355, first_criticality = '1969-10-03', operator = 'JAPAN ATOMIC POWER CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 333;  -- Tsuruga 1
UPDATE reactors SET pris_id = 360, first_criticality = '1986-05-28', operator = 'JAPAN ATOMIC POWER CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 334;  -- Tsuruga 2
UPDATE reactors SET pris_id = 414, first_criticality = '1972-11-01', operator = 'Limited liability partnership «Mangistau atomic energy complex-Kazatomprom»', updated_at = CURRENT_TIMESTAMP WHERE id = 335;  -- Aktau 1
UPDATE reactors SET pris_id = 415, first_criticality = '1983-10-04', operator = 'IGNALINA NUCLEAR POWER PLANT', updated_at = CURRENT_TIMESTAMP WHERE id = 336;  -- Ignalina 1
UPDATE reactors SET pris_id = 416, first_criticality = '1986-12-01', operator = 'IGNALINA NUCLEAR POWER PLANT', updated_at = CURRENT_TIMESTAMP WHERE id = 337;  -- Ignalina 2
UPDATE reactors SET pris_id = 422, first_criticality = '1968-06-24', operator = 'BV GEMEENSCHAPPELIJKE KERNENERGIECENTRALE NEDERLAND (BV GKN)', updated_at = CURRENT_TIMESTAMP WHERE id = 341;  -- Dodewaard 1
UPDATE reactors SET pris_id = 427, first_criticality = '1971-08-01', operator = 'PAKISTAN ATOMIC ENERGY COMMISSION', updated_at = CURRENT_TIMESTAMP WHERE id = 346;  -- Karachi 1
UPDATE reactors SET pris_id = 447, first_criticality = '1954-05-06', operator = 'MINISTRY OF MEDIUM MACHINE BUILDING OF THE USSR (MINSREDMASH)', updated_at = CURRENT_TIMESTAMP WHERE id = 353;  -- APS1 Obninsk 1
UPDATE reactors SET pris_id = 488, first_criticality = '1963-09-01', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 359;  -- Beloyarsk 1
UPDATE reactors SET pris_id = 503, first_criticality = '1967-10-10', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 360;  -- Beloyarsk 2
UPDATE reactors SET pris_id = 467, first_criticality = '1973-12-11', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 363;  -- Bilibino 1
UPDATE reactors SET pris_id = 468, first_criticality = '1974-12-07', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 364;  -- Bilibino 2
UPDATE reactors SET pris_id = 469, first_criticality = '1975-12-06', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 365;  -- Bilibino 3
UPDATE reactors SET pris_id = 470, first_criticality = '1976-12-12', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 366;  -- Bilibino 4
UPDATE reactors SET pris_id = 1008, first_criticality = '2028-03-10', grid_connection = '2028-04-21', commercial_operation = '2028-09-10', operator = 'Joint Stock Company ''Concern Rosenergoatom''', updated_at = CURRENT_TIMESTAMP WHERE id = 380;  -- Kursk 2 2
UPDATE reactors SET pris_id = 548, first_criticality = '1978-11-27', operator = 'JADROVA A VYRADOVACIA SPOLOCNOST /NUCLEAR AND DECOMMISSIONING COMPANY, plc./', updated_at = CURRENT_TIMESTAMP WHERE id = 401;  -- Bohunice 1
UPDATE reactors SET pris_id = 549, first_criticality = '1980-03-15', operator = 'JADROVA A VYRADOVACIA SPOLOCNOST /NUCLEAR AND DECOMMISSIONING COMPANY, plc./', updated_at = CURRENT_TIMESTAMP WHERE id = 402;  -- Bohunice 2
UPDATE reactors SET pris_id = 543, first_criticality = '1972-10-24', operator = 'JADROVA A VYRADOVACIA SPOLOCNOST /NUCLEAR AND DECOMMISSIONING COMPANY, plc./', updated_at = CURRENT_TIMESTAMP WHERE id = 405;  -- Bohunice A 1
UPDATE reactors SET pris_id = 545, operator = 'SLOVENSKÉ ELEKTRÁRNE, A.S.', updated_at = CURRENT_TIMESTAMP WHERE id = 409;  -- Mochovce 4
UPDATE reactors SET pris_id = 1074, operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 435;  -- Shin-Kori 5
UPDATE reactors SET pris_id = 1075, operator = 'Korea Hydro and Nuclear Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 436;  -- Shin-Kori 6
UPDATE reactors SET pris_id = 139, first_criticality = '1968-06-30', operator = 'UNION FENOSA GENERATION, S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 448;  -- Jose Cabrera 1
UPDATE reactors SET pris_id = 149, first_criticality = '1970-11-05', operator = 'NUCLENOR, S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 449;  -- Santa María de Garoña 1
UPDATE reactors SET pris_id = 150, first_criticality = '1972-02-11', operator = 'HISPANO-FRANCESA DE ENERGIA NUCLEAR, S.A.', updated_at = CURRENT_TIMESTAMP WHERE id = 451;  -- Vandellos 1
UPDATE reactors SET pris_id = 528, first_criticality = '1963-07-17', operator = 'AB SVAFO', updated_at = CURRENT_TIMESTAMP WHERE id = 453;  -- Ågesta 1
UPDATE reactors SET pris_id = 534, first_criticality = '1970-12-12', operator = 'OKG AKTIEBOLAG', updated_at = CURRENT_TIMESTAMP WHERE id = 459;  -- Oskarshamn 1
UPDATE reactors SET pris_id = 535, first_criticality = '1974-03-06', operator = 'OKG AKTIEBOLAG', updated_at = CURRENT_TIMESTAMP WHERE id = 460;  -- Oskarshamn 2
UPDATE reactors SET pris_id = 536, first_criticality = '1973-08-20', operator = 'Ringhals AB', updated_at = CURRENT_TIMESTAMP WHERE id = 462;  -- Ringhals 1
UPDATE reactors SET pris_id = 537, first_criticality = '1974-06-19', operator = 'Ringhals AB', updated_at = CURRENT_TIMESTAMP WHERE id = 463;  -- Ringhals 2
UPDATE reactors SET pris_id = 966, first_criticality = '1966-12-29', operator = 'Energie de l''Ouest Suisse', updated_at = CURRENT_TIMESTAMP WHERE id = 470;  -- Lucens 1
UPDATE reactors SET pris_id = 56, first_criticality = '1971-03-08', operator = 'BKW ENERGIE AG', updated_at = CURRENT_TIMESTAMP WHERE id = 471;  -- Mühleberg 1
UPDATE reactors SET pris_id = 554, first_criticality = '1977-10-16', operator = 'Taiwan Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 472;  -- Chinshan (First) 1
UPDATE reactors SET pris_id = 555, first_criticality = '1978-11-09', operator = 'Taiwan Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 473;  -- Chinshan (First) 2
UPDATE reactors SET pris_id = 556, first_criticality = '1981-02-01', operator = 'Taiwan Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 474;  -- Kuosheng (Second) 1
UPDATE reactors SET pris_id = 557, first_criticality = '1982-03-26', operator = 'Taiwan Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 475;  -- Kuosheng (Second) 2
UPDATE reactors SET pris_id = 558, first_criticality = '1984-03-30', operator = 'Taiwan Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 478;  -- Maanshan (Third) 1
UPDATE reactors SET pris_id = 559, first_criticality = '1985-02-01', operator = 'Taiwan Power Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 479;  -- Maanshan (Third) 2
UPDATE reactors SET pris_id = 553, operator = 'Akkuyu Nuclear Joint Stock Company (JSC)', updated_at = CURRENT_TIMESTAMP WHERE id = 480;  -- Akkuyu 1
UPDATE reactors SET pris_id = 1080, operator = 'Akkuyu Nuclear Joint Stock Company (JSC)', updated_at = CURRENT_TIMESTAMP WHERE id = 481;  -- Akkuyu 2
UPDATE reactors SET pris_id = 264, first_criticality = '1961-08-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 486;  -- Berkeley 1
UPDATE reactors SET pris_id = 265, first_criticality = '1962-03-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 487;  -- Berkeley 2
UPDATE reactors SET pris_id = 266, first_criticality = '1961-08-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 488;  -- Bradwell 1
UPDATE reactors SET pris_id = 267, first_criticality = '1962-04-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 489;  -- Bradwell 2
UPDATE reactors SET pris_id = 231, first_criticality = '1956-05-01', operator = 'Sellafield Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 490;  -- Calder Hall 1
UPDATE reactors SET pris_id = 232, first_criticality = '1956-12-01', operator = 'Sellafield Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 491;  -- Calder Hall 2
UPDATE reactors SET pris_id = 233, first_criticality = '1958-01-01', operator = 'Sellafield Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 492;  -- Calder Hall 3
UPDATE reactors SET pris_id = 234, first_criticality = '1958-12-01', operator = 'Sellafield Limited', updated_at = CURRENT_TIMESTAMP WHERE id = 493;  -- Calder Hall 4
UPDATE reactors SET pris_id = 252, first_criticality = '1958-11-09', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 494;  -- Chapelcross 1
UPDATE reactors SET pris_id = 253, first_criticality = '1959-05-30', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 495;  -- Chapelcross 2
UPDATE reactors SET pris_id = 254, first_criticality = '1959-08-31', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 496;  -- Chapelcross 3
UPDATE reactors SET pris_id = 255, first_criticality = '1959-12-22', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 497;  -- Chapelcross 4
UPDATE reactors SET pris_id = 242, first_criticality = '1959-11-14', operator = 'UNITED KINGDOM ATOMIC ENERGY AUTHORITY', updated_at = CURRENT_TIMESTAMP WHERE id = 498;  -- Dounreay DFR 1
UPDATE reactors SET pris_id = 243, first_criticality = '1974-03-01', operator = 'UNITED KINGDOM ATOMIC ENERGY AUTHORITY', updated_at = CURRENT_TIMESTAMP WHERE id = 499;  -- Dounreay PFR 1
UPDATE reactors SET pris_id = 275, first_criticality = '1965-06-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 500;  -- Dungeness A 1
UPDATE reactors SET pris_id = 276, first_criticality = '1965-09-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 501;  -- Dungeness A 2
UPDATE reactors SET pris_id = 271, first_criticality = '1964-05-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 510;  -- Hinkley Point A 1
UPDATE reactors SET pris_id = 272, first_criticality = '1964-10-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 511;  -- Hinkley Point A 2
UPDATE reactors SET pris_id = 1072, operator = 'EDF Energy - China General Nuclear joint venture', updated_at = CURRENT_TIMESTAMP WHERE id = 514;  -- Hinkley Point C 1
UPDATE reactors SET pris_id = 1073, operator = 'EDF Energy - China General Nuclear joint venture', updated_at = CURRENT_TIMESTAMP WHERE id = 515;  -- Hinkley Point C 2
UPDATE reactors SET pris_id = 269, first_criticality = '1963-08-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 516;  -- Hunterston A 1
UPDATE reactors SET pris_id = 270, first_criticality = '1964-03-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 517;  -- Hunterston A 2
UPDATE reactors SET pris_id = 235, first_criticality = '1965-06-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 522;  -- Sizewell A 1
UPDATE reactors SET pris_id = 236, first_criticality = '1965-12-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 523;  -- Sizewell A 2
UPDATE reactors SET pris_id = 273, first_criticality = '1964-09-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 527;  -- Trawsfynydd 1
UPDATE reactors SET pris_id = 274, first_criticality = '1964-12-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 528;  -- Trawsfynydd 2
UPDATE reactors SET pris_id = 268, first_criticality = '1962-08-09', operator = 'UNITED KINGDOM ATOMIC ENERGY AUTHORITY', updated_at = CURRENT_TIMESTAMP WHERE id = 529;  -- Windscale AGR 1
UPDATE reactors SET pris_id = 239, first_criticality = '1967-09-01', operator = 'UNITED KINGDOM ATOMIC ENERGY AUTHORITY', updated_at = CURRENT_TIMESTAMP WHERE id = 530;  -- Winfrith 1
UPDATE reactors SET pris_id = 240, first_criticality = '1969-11-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 531;  -- Wylfa 1
UPDATE reactors SET pris_id = 241, first_criticality = '1970-09-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 532;  -- Wylfa 2
UPDATE reactors SET pris_id = 581, operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 539;  -- Khmelnytskyi 3
UPDATE reactors SET pris_id = 582, operator = 'State Enterprise “National Nuclear Energy Generating Company ‘Energoatom”', updated_at = CURRENT_TIMESTAMP WHERE id = 540;  -- Khmelnytskyi 4
UPDATE reactors SET pris_id = 601, first_criticality = '1962-09-27', operator = 'CONSUMERS POWER CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 558;  -- Big Rock Point 1
UPDATE reactors SET pris_id = 703, first_criticality = '1964-04-13', operator = 'DOE & PUERTO RICO WATER RESOURCES', updated_at = CURRENT_TIMESTAMP WHERE id = 559;  -- Bonus 1
UPDATE reactors SET pris_id = 645, first_criticality = '1977-01-14', operator = 'Progress Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 581;  -- Crystal River 3
UPDATE reactors SET pris_id = 600, first_criticality = '1963-03-01', operator = 'CAROLINAS-VIRGINIA NUCLEAR POWER ASSOC.', updated_at = CURRENT_TIMESTAMP WHERE id = 582;  -- CVTR 1
UPDATE reactors SET pris_id = 597, first_criticality = '1959-10-15', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 586;  -- Dresden 1
UPDATE reactors SET pris_id = 667, first_criticality = '1974-03-23', operator = 'NextEra Energy Resources, LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 589;  -- Duane Arnold 1
UPDATE reactors SET pris_id = 596, first_criticality = '1962-11-01', operator = 'RURAL COOPERATIVE POWER ASSOC.', updated_at = CURRENT_TIMESTAMP WHERE id = 590;  -- Elk River 1
UPDATE reactors SET pris_id = 602, first_criticality = '1963-08-23', operator = 'DETROIT EDISON CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 593;  -- Fermi 1
UPDATE reactors SET pris_id = 634, first_criticality = '1973-08-06', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 596;  -- Fort Calhoun 1
UPDATE reactors SET pris_id = 623, first_criticality = '1974-01-31', operator = 'PUBLIC SERVICE CO. OF COLORADO', updated_at = CURRENT_TIMESTAMP WHERE id = 597;  -- Fort St. Vrain 1
UPDATE reactors SET pris_id = 893, first_criticality = '1957-08-03', operator = 'General Electric', updated_at = CURRENT_TIMESTAMP WHERE id = 598;  -- GE Vallecitos 1
UPDATE reactors SET pris_id = 605, first_criticality = '1967-07-24', operator = 'CONNECTICUT YANKEE ATOMIC POWER CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 601;  -- Haddam Neck (Connecticut Yankee) 1
UPDATE reactors SET pris_id = 891, first_criticality = '1963-01-01', operator = 'Atomic Energy Commission and Nebraska Public Power District', updated_at = CURRENT_TIMESTAMP WHERE id = 602;  -- Hallam 1
UPDATE reactors SET pris_id = 599, first_criticality = '1963-02-16', operator = 'Pacific Gas and Electric Company', updated_at = CURRENT_TIMESTAMP WHERE id = 607;  -- Humboldt Bay 1
UPDATE reactors SET pris_id = 643, first_criticality = '1962-08-02', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 608;  -- Indian Point 1
UPDATE reactors SET pris_id = 611, first_criticality = '1973-05-22', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 609;  -- Indian Point 2
UPDATE reactors SET pris_id = 635, first_criticality = '1976-04-04', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 610;  -- Indian Point 3
UPDATE reactors SET pris_id = 647, first_criticality = '1974-03-07', operator = 'Dominion Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 611;  -- Kewaunee 1
UPDATE reactors SET pris_id = 710, first_criticality = '1967-07-11', operator = 'DAIRYLAND POWER COOPERATIVE', updated_at = CURRENT_TIMESTAMP WHERE id = 612;  -- Lacrosse 1
UPDATE reactors SET pris_id = 649, first_criticality = '1972-10-23', operator = 'MAINE YANKEE ATOMIC POWER CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 617;  -- Maine Yankee 1
UPDATE reactors SET pris_id = 610, first_criticality = '1970-10-26', operator = 'Dominion Energy', updated_at = CURRENT_TIMESTAMP WHERE id = 620;  -- Millstone 1
UPDATE reactors SET pris_id = 606, first_criticality = '1969-05-03', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 631;  -- Oyster Creek 1
UPDATE reactors SET pris_id = 616, first_criticality = '1971-05-22', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 632;  -- Palisades 1
UPDATE reactors SET pris_id = 598, first_criticality = '1964-01-01', operator = 'NUCLEAR MANAGEMENT CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 636;  -- Pathfinder 1
UPDATE reactors SET pris_id = 603, first_criticality = '1966-03-03', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 637;  -- Peach Bottom 1
UPDATE reactors SET pris_id = 639, first_criticality = '1972-06-16', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 641;  -- Pilgrim 1
UPDATE reactors SET pris_id = 894, first_criticality = '1961-01-01', operator = 'City of Piqua Government', updated_at = CURRENT_TIMESTAMP WHERE id = 642;  -- Piqua 1
UPDATE reactors SET pris_id = 651, first_criticality = '1974-09-16', operator = 'SACRAMENTO MUNICIPAL UTILITY DISTRICT', updated_at = CURRENT_TIMESTAMP WHERE id = 649;  -- Rancho Seco 1
UPDATE reactors SET pris_id = 604, first_criticality = '1967-06-14', operator = 'SOUTHERN CALIFORNIA EDISON Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 654;  -- San Onofre 1
UPDATE reactors SET pris_id = 683, first_criticality = '1982-07-26', operator = 'SOUTHERN CALIFORNIA EDISON Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 655;  -- San Onofre 2
UPDATE reactors SET pris_id = 684, first_criticality = '1983-08-29', operator = 'SOUTHERN CALIFORNIA EDISON Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 656;  -- San Onofre 3
UPDATE reactors SET pris_id = 892, first_criticality = '1967-01-01', operator = 'Saxton Nuclear Experimental Reactor Corporation', updated_at = CURRENT_TIMESTAMP WHERE id = 657;  -- Saxton 1
UPDATE reactors SET pris_id = 890, first_criticality = '1957-01-01', operator = 'Department of Energy and Duquesne Light Co.', updated_at = CURRENT_TIMESTAMP WHERE id = 661;  -- Shippingport 1
UPDATE reactors SET pris_id = 659, first_criticality = '1985-02-15', operator = 'Long Island Power Authority', updated_at = CURRENT_TIMESTAMP WHERE id = 662;  -- Shoreham 1
UPDATE reactors SET pris_id = 637, first_criticality = '1974-06-05', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 672;  -- Three Mile Island 1
UPDATE reactors SET pris_id = 657, first_criticality = '1978-03-27', operator = 'GENERAL PUBLIC UTILITIES (owned by FirstEnergy Corp.)', updated_at = CURRENT_TIMESTAMP WHERE id = 673;  -- Three Mile Island 2
UPDATE reactors SET pris_id = 675, first_criticality = '1975-12-15', operator = 'PORTLAND GENERAL ELECTRIC CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 674;  -- Trojan 1
UPDATE reactors SET pris_id = 626, first_criticality = '1972-03-24', operator = 'Entergy Nuclear Operations, Inc.', updated_at = CURRENT_TIMESTAMP WHERE id = 677;  -- Vermont Yankee 1
UPDATE reactors SET pris_id = 638, first_criticality = '1960-08-19', operator = 'YANKEE ATOMIC ELECTRIC CO.', updated_at = CURRENT_TIMESTAMP WHERE id = 686;  -- Yankee NPS 1
UPDATE reactors SET pris_id = 640, first_criticality = '1973-06-19', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 687;  -- Zion 1
UPDATE reactors SET pris_id = 646, first_criticality = '1973-12-24', operator = 'Exelon Generation Co., LLC', updated_at = CURRENT_TIMESTAMP WHERE id = 688;  -- Zion 2
UPDATE reactors SET pris_id = 941, operator = 'China Huaneng Group', thermal_capacity_mw = 3190, updated_at = CURRENT_TIMESTAMP WHERE id = 689;  -- Changjiang 3
UPDATE reactors SET pris_id = 942, operator = 'China Huaneng Group', thermal_capacity_mw = 3190, updated_at = CURRENT_TIMESTAMP WHERE id = 690;  -- Changjiang 4
UPDATE reactors SET pris_id = 1111, operator = 'Hainan Nuclear Power Company', thermal_capacity_mw = 385, updated_at = CURRENT_TIMESTAMP WHERE id = 691;  -- Linglong 1
UPDATE reactors SET pris_id = 1094, first_criticality = '2026-02-14', grid_connection = '2026-03-12', operator = 'CGN Cangnan Nuclear Power Co., Ltd.', thermal_capacity_mw = 3180, net_capacity_mw = 1117, reference_power_mw = 1117, updated_at = CURRENT_TIMESTAMP WHERE id = 692;  -- Sanao 1
UPDATE reactors SET pris_id = 1107, operator = 'CGN Cangnan Nuclear Power Co., Ltd.', thermal_capacity_mw = 3180, net_capacity_mw = 1117, reference_power_mw = 1117, updated_at = CURRENT_TIMESTAMP WHERE id = 693;  -- Sanao 2
UPDATE reactors SET pris_id = 2168, operator = 'CGN Cangnan Second Nuclear Power Company, Ltd.', thermal_capacity_mw = 3180, net_capacity_mw = 1208, reference_power_mw = 1208, updated_at = CURRENT_TIMESTAMP WHERE id = 694;  -- Sanao 3
UPDATE reactors SET pris_id = 993, operator = 'Shandong Nuclear Power Company, Ltd.', thermal_capacity_mw = 3400, net_capacity_mw = 1161, reference_power_mw = 1161, updated_at = CURRENT_TIMESTAMP WHERE id = 695;  -- Haiyang 3
UPDATE reactors SET pris_id = 994, operator = 'Shandong Nuclear Power Company, Ltd.', thermal_capacity_mw = 3400, net_capacity_mw = 1161, reference_power_mw = 1161, updated_at = CURRENT_TIMESTAMP WHERE id = 696;  -- Haiyang 4
UPDATE reactors SET pris_id = 995, operator = 'SANMEN NUCLEAR POWER CO., LTD.', thermal_capacity_mw = 3400, net_capacity_mw = 1163, reference_power_mw = 1163, updated_at = CURRENT_TIMESTAMP WHERE id = 697;  -- Sanmen 3
UPDATE reactors SET pris_id = 996, operator = 'SANMEN NUCLEAR POWER CO., LTD.', thermal_capacity_mw = 3400, net_capacity_mw = 1163, reference_power_mw = 1163, updated_at = CURRENT_TIMESTAMP WHERE id = 698;  -- Sanmen 4
UPDATE reactors SET pris_id = 1064, operator = 'CGN Lufeng Nuclear Power Co., Ltd', thermal_capacity_mw = 3400, net_capacity_mw = 1250, reference_power_mw = 1250, updated_at = CURRENT_TIMESTAMP WHERE id = 699;  -- Lufeng 1
UPDATE reactors SET pris_id = 1065, operator = 'CGN Lufeng Nuclear Power Co., Ltd', thermal_capacity_mw = 3400, updated_at = CURRENT_TIMESTAMP WHERE id = 700;  -- Lufeng 2
UPDATE reactors SET pris_id = 1113, operator = 'CGN Lufeng Nuclear Power Co., Ltd', thermal_capacity_mw = 3180, net_capacity_mw = 1116, reference_power_mw = 1116, updated_at = CURRENT_TIMESTAMP WHERE id = 701;  -- Lufeng 5
UPDATE reactors SET pris_id = 1114, operator = 'CGN Lufeng Nuclear Power Co., Ltd', thermal_capacity_mw = 3180, net_capacity_mw = 1116, reference_power_mw = 1116, updated_at = CURRENT_TIMESTAMP WHERE id = 702;  -- Lufeng 6
UPDATE reactors SET pris_id = 999, operator = 'LIAONING NUCLEAR POWER COMPANY, LMT.', updated_at = CURRENT_TIMESTAMP WHERE id = 703;  -- Xudabao 1
UPDATE reactors SET pris_id = 1000, operator = 'LIAONING NUCLEAR POWER COMPANY, LMT.', updated_at = CURRENT_TIMESTAMP WHERE id = 704;  -- Xudabao 2
UPDATE reactors SET pris_id = 1104, operator = 'LIAONING NUCLEAR POWER COMPANY, LMT.', thermal_capacity_mw = 3200, net_capacity_mw = 1200, reference_power_mw = 1200, updated_at = CURRENT_TIMESTAMP WHERE id = 705;  -- Xudabao 3
UPDATE reactors SET pris_id = 1112, operator = 'LIAONING NUCLEAR POWER COMPANY, LMT.', thermal_capacity_mw = 3200, net_capacity_mw = 1200, reference_power_mw = 1200, updated_at = CURRENT_TIMESTAMP WHERE id = 706;  -- Xudabao 4
UPDATE reactors SET pris_id = 1105, operator = 'Jiangsu Nuclear Power Corporation', thermal_capacity_mw = 3200, net_capacity_mw = 1171, reference_power_mw = 1171, updated_at = CURRENT_TIMESTAMP WHERE id = 707;  -- Tianwan 7
UPDATE reactors SET pris_id = 1110, operator = 'Jiangsu Nuclear Power Corporation', thermal_capacity_mw = 3200, net_capacity_mw = 1171, reference_power_mw = 1171, updated_at = CURRENT_TIMESTAMP WHERE id = 708;  -- Tianwan 8
UPDATE reactors SET pris_id = 1121, operator = 'CNNP Guodian Zhangzhou Energy Co.,Ltd', thermal_capacity_mw = 3180, net_capacity_mw = 1129, reference_power_mw = 1129, updated_at = CURRENT_TIMESTAMP WHERE id = 709;  -- Zhangzhou 3
UPDATE reactors SET pris_id = 1122, operator = 'CNNP Guodian Zhangzhou Energy Co.,Ltd', thermal_capacity_mw = 3180, net_capacity_mw = 1129, reference_power_mw = 1129, updated_at = CURRENT_TIMESTAMP WHERE id = 710;  -- Zhangzhou 4
UPDATE reactors SET pris_id = 1123, operator = 'Zhanjiang Nuclear Power Company, Ltd.', thermal_capacity_mw = 3400, net_capacity_mw = 1224, reference_power_mw = 1224, updated_at = CURRENT_TIMESTAMP WHERE id = 711;  -- Lianjiang 1
UPDATE reactors SET pris_id = 1124, operator = 'Zhanjiang Nuclear Power Company, Ltd.', thermal_capacity_mw = 3400, net_capacity_mw = 1224, reference_power_mw = 1224, updated_at = CURRENT_TIMESTAMP WHERE id = 712;  -- Lianjiang 2
UPDATE reactors SET pris_id = 2136, operator = 'Fujian Ningde Nuclear Power Company, Ltd.', thermal_capacity_mw = 3180, net_capacity_mw = 1200, reference_power_mw = 1200, updated_at = CURRENT_TIMESTAMP WHERE id = 713;  -- Ningde 5
UPDATE reactors SET pris_id = 2167, operator = 'CHINA NATIONAL NUCLEAR CORPORATION', thermal_capacity_mw = 3190, net_capacity_mw = 1145, reference_power_mw = 1145, updated_at = CURRENT_TIMESTAMP WHERE id = 715;  -- Jinqimen 1
UPDATE reactors SET pris_id = 2169, operator = 'China Power Investment Guangxi Nuclear Power Co., Ltd.', thermal_capacity_mw = 3400, net_capacity_mw = 1160, reference_power_mw = 1160, updated_at = CURRENT_TIMESTAMP WHERE id = 716;  -- Bailong 1
UPDATE reactors SET pris_id = 2142, operator = 'CGN Huizhou Second Nuclear Power Co., Ltd', thermal_capacity_mw = 3180, net_capacity_mw = 1209, reference_power_mw = 1209, updated_at = CURRENT_TIMESTAMP WHERE id = 717;  -- Taipingling 3
UPDATE reactors SET pris_id = 137, operator = 'Nuclear Power Plants Authority', thermal_capacity_mw = 3200, net_capacity_mw = 1100, reference_power_mw = 1100, updated_at = CURRENT_TIMESTAMP WHERE id = 718;  -- El Dabaa 1
UPDATE reactors SET pris_id = 138, operator = 'Nuclear Power Plants Authority', thermal_capacity_mw = 3200, net_capacity_mw = 1100, reference_power_mw = 1100, updated_at = CURRENT_TIMESTAMP WHERE id = 719;  -- El Dabaa 2
UPDATE reactors SET pris_id = 1120, operator = 'Nuclear Power Plants Authority', thermal_capacity_mw = 3200, net_capacity_mw = 1100, reference_power_mw = 1100, updated_at = CURRENT_TIMESTAMP WHERE id = 720;  -- El Dabaa 3
UPDATE reactors SET pris_id = 2127, operator = 'Nuclear Power Plants Authority', thermal_capacity_mw = 3200, net_capacity_mw = 1100, reference_power_mw = 1100, updated_at = CURRENT_TIMESTAMP WHERE id = 721;  -- El Dabaa 4
UPDATE reactors SET pris_id = 1081, operator = 'Akkuyu Nuclear Joint Stock Company (JSC)', thermal_capacity_mw = 3200, net_capacity_mw = 1114, reference_power_mw = 1114, updated_at = CURRENT_TIMESTAMP WHERE id = 722;  -- Akkuyu 3
UPDATE reactors SET pris_id = 1082, operator = 'Akkuyu Nuclear Joint Stock Company (JSC)', thermal_capacity_mw = 3200, net_capacity_mw = 1114, reference_power_mw = 1114, updated_at = CURRENT_TIMESTAMP WHERE id = 723;  -- Akkuyu 4
UPDATE reactors SET pris_id = 1108, operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', thermal_capacity_mw = 3000, net_capacity_mw = 917, reference_power_mw = 917, updated_at = CURRENT_TIMESTAMP WHERE id = 724;  -- Kudankulam 5
UPDATE reactors SET pris_id = 1109, operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', thermal_capacity_mw = 3000, net_capacity_mw = 917, reference_power_mw = 917, updated_at = CURRENT_TIMESTAMP WHERE id = 725;  -- Kudankulam 6
UPDATE reactors SET pris_id = 1106, commercial_operation = '2028-12-31', operator = 'Siberian Chemical Plant JSC', thermal_capacity_mw = 700, net_capacity_mw = 281, reference_power_mw = 281, updated_at = CURRENT_TIMESTAMP WHERE id = 727;  -- BREST 1
UPDATE reactors SET pris_id = 1115, operator = 'PAKISTAN ATOMIC ENERGY COMMISSION', thermal_capacity_mw = 3180, net_capacity_mw = 1117, reference_power_mw = 1117, updated_at = CURRENT_TIMESTAMP WHERE id = 728;  -- Chashma 5
UPDATE reactors SET pris_id = 1076, operator = 'Paks II. Nuclear Power Plant Private Company Limited by Shares', thermal_capacity_mw = 3200, net_capacity_mw = 1185, reference_power_mw = 1185, updated_at = CURRENT_TIMESTAMP WHERE id = 729;  -- Paks 5
UPDATE reactors SET pris_id = 2138, operator = 'Huaneng Shandong Shidao Bay Nuclear Power Company, Ltd.', thermal_capacity_mw = 3180, updated_at = CURRENT_TIMESTAMP WHERE id = 731;  -- Shidaowan 1
UPDATE reactors SET pris_id = 2139, operator = 'Huaneng Shandong Shidao Bay Nuclear Power Company, Ltd.', thermal_capacity_mw = 3180, updated_at = CURRENT_TIMESTAMP WHERE id = 732;  -- Shidaowan 2
UPDATE reactors SET pris_id = 2137, operator = 'Fujian Ningde Nuclear Power Company, Ltd.', thermal_capacity_mw = 3190, reference_power_mw = 1116.0, updated_at = CURRENT_TIMESTAMP WHERE id = 733;  -- Ningde 6
UPDATE reactors SET pris_id = 293, operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', reference_power_mw = 630.0, updated_at = CURRENT_TIMESTAMP WHERE id = 734;  -- Kaiga 5
UPDATE reactors SET pris_id = 294, operator = 'NUCLEAR POWER CORPORATION OF INDIA, LTD.', reference_power_mw = 630.0, updated_at = CURRENT_TIMESTAMP WHERE id = 735;  -- Kaiga 6
UPDATE reactors SET pris_id = 2206, operator = 'Korea Hydro and Nuclear Power Co.', reference_power_mw = 1340.0, updated_at = CURRENT_TIMESTAMP WHERE id = 739;  -- Shin-Hanul (Shin-Ulchin) 3
UPDATE reactors SET pris_id = 1009, first_criticality = '2031-01-21', grid_connection = '2031-05-08', commercial_operation = '2031-12-01', operator = 'Joint Stock Company ''Concern Rosenergoatom''', thermal_capacity_mw = 3300, updated_at = CURRENT_TIMESTAMP WHERE id = 740;  -- Kursk 2 3
UPDATE reactors SET pris_id = 2193, operator = 'Ontario Power Generation', thermal_capacity_mw = 870, updated_at = CURRENT_TIMESTAMP WHERE id = 741;  -- Darlington SMR 1
UPDATE reactors SET pris_id = 538, first_criticality = '1975-01-18', operator = 'Barsebäck Kraft AB', updated_at = CURRENT_TIMESTAMP WHERE id = 454;  -- Barsebäck 1
UPDATE reactors SET pris_id = 540, first_criticality = '1977-02-20', operator = 'Barsebäck Kraft AB', updated_at = CURRENT_TIMESTAMP WHERE id = 455;  -- Barsebäck 2
UPDATE reactors SET pris_id = 237, first_criticality = '1967-08-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 520;  -- Oldbury 1
UPDATE reactors SET pris_id = 238, first_criticality = '1967-12-01', operator = 'MAGNOX, LTD', updated_at = CURRENT_TIMESTAMP WHERE id = 521;  -- Oldbury 2
UPDATE reactors SET pris_id = 568, first_criticality = '1977-08-02', operator = 'MINTOPENERGO OF UKRAINE - MINISTRY OF FUEL AND ENERGY OF UKRAINE', updated_at = CURRENT_TIMESTAMP WHERE id = 533;  -- Chernobyl 1
UPDATE reactors SET pris_id = 569, first_criticality = '1978-11-17', operator = 'MINTOPENERGO OF UKRAINE - MINISTRY OF FUEL AND ENERGY OF UKRAINE', updated_at = CURRENT_TIMESTAMP WHERE id = 534;  -- Chernobyl 2
UPDATE reactors SET pris_id = 575, first_criticality = '1981-06-02', operator = 'MINTOPENERGO OF UKRAINE - MINISTRY OF FUEL AND ENERGY OF UKRAINE', updated_at = CURRENT_TIMESTAMP WHERE id = 535;  -- Chernobyl 3
UPDATE reactors SET pris_id = 576, first_criticality = '1983-11-26', operator = 'MINTOPENERGO OF UKRAINE - MINISTRY OF FUEL AND ENERGY OF UKRAINE', updated_at = CURRENT_TIMESTAMP WHERE id = 536;  -- Chernobyl 4
COMMIT;
