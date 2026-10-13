-- 027_batch_c_verified.sql
-- Date: 2026-10-13
-- Description: Audit batch C — research verdicts that changed a value. Kept only verdicts PRIS/OTHER with
--   confidence HIGH/MED whose verbatim quote scripts/quote_check.py re-found on the cited page (FOUND/PARTIAL).
--   Ledger with every source URL + quote: audit/batch_c/results_*.psv, audit/batch_c/triage.json (local).
--   Net capacity also sets reference_power_mw (house rule outside the US).
-- Rows: 25. Backup: nuclear_reactors.db.bak-pre023-20261013 (taken before 023-027)

BEGIN TRANSACTION;
UPDATE reactors SET thermal_capacity_mw = 2620.0, updated_at = CURRENT_TIMESTAMP WHERE id = 29;  -- Bruce 2 (https://world-nuclear.org/nuclear-reactor-database/details/B)
UPDATE reactors SET net_capacity_mw = 1100.0, reference_power_mw = 1100.0, updated_at = CURRENT_TIMESTAMP WHERE id = 689;  -- Changjiang 3 (https://world-nuclear.org/reactor/default.aspx/changjiang-3)
UPDATE reactors SET net_capacity_mw = 1100.0, reference_power_mw = 1100.0, updated_at = CURRENT_TIMESTAMP WHERE id = 690;  -- Changjiang 4 (https://world-nuclear.org/reactor/default.aspx/changjiang-4)
UPDATE reactors SET net_capacity_mw = 100.0, reference_power_mw = 100.0, updated_at = CURRENT_TIMESTAMP WHERE id = 691;  -- Linglong 1 (http://world-nuclear.org/nuclear-reactor-database/details/ch)
UPDATE reactors SET net_capacity_mw = 1161.0, reference_power_mw = 1161.0, updated_at = CURRENT_TIMESTAMP WHERE id = 700;  -- Lufeng 2 (https://world-nuclear.org/nuclear-reactor-database/details/L)
UPDATE reactor_details SET turbine_supplier = 'Siemens' WHERE reactor_id = 215;  -- Obrigheim 1
UPDATE reactors SET commercial_operation = '1993-09-03', updated_at = CURRENT_TIMESTAMP WHERE id = 291;  -- Hamaoka 4 (https://world-nuclear.org/nuclear-reactor-database/details/H)
UPDATE reactors SET construction_start = '1966-04-22', updated_at = CURRENT_TIMESTAMP WHERE id = 333;  -- Tsuruga 1 (https://world-nuclear.org/nuclear-reactor-database/details/T)
UPDATE reactors SET gross_capacity_mw = 35.0, updated_at = CURRENT_TIMESTAMP WHERE id = 351;  -- Akademik Lomonosov 1 (https://en.wikipedia.org/wiki/Akademik_Lomonosov)
UPDATE reactors SET gross_capacity_mw = 35.0, updated_at = CURRENT_TIMESTAMP WHERE id = 352;  -- Akademik Lomonosov 2 (https://en.wikipedia.org/wiki/Akademik_Lomonosov)
UPDATE reactors SET permanent_shutdown = '1981-06-18', updated_at = CURRENT_TIMESTAMP WHERE id = 359;  -- Beloyarsk 1 (https://world-nuclear-news.org/articles/dismantling-of-beloy)
UPDATE reactors SET permanent_shutdown = '1989-09-25', updated_at = CURRENT_TIMESTAMP WHERE id = 360;  -- Beloyarsk 2 (https://world-nuclear-news.org/articles/dismantling-of-beloy)
UPDATE reactors SET commercial_operation = '2012-09-25', updated_at = CURRENT_TIMESTAMP WHERE id = 370;  -- Kalinin 4 (https://world-nuclear-news.org/articles/kalinin-4-accepted-f)
UPDATE reactors SET construction_start = '1967-07-01', updated_at = CURRENT_TIMESTAMP WHERE id = 389;  -- Novovoronezh 1 3 (https://world-nuclear.org/nuclear-reactor-database/details/N)
UPDATE reactors SET construction_start = '1974-03-01', updated_at = CURRENT_TIMESTAMP WHERE id = 391;  -- Novovoronezh 1 5 (https://world-nuclear.org/nuclear-reactor-database/details/N)
UPDATE reactors SET thermal_capacity_mw = 3120.0, updated_at = CURRENT_TIMESTAMP WHERE id = 395;  -- Rostov 2 (https://world-nuclear.org/nuclear-reactor-database/details/R)
UPDATE reactors SET net_capacity_mw = 93.0, reference_power_mw = 93.0, updated_at = CURRENT_TIMESTAMP WHERE id = 405;  -- Bohunice A 1 (https://world-nuclear.org/nuclear-reactor-database/details/B)
UPDATE reactors SET commercial_operation = '2023-10-17', updated_at = CURRENT_TIMESTAMP WHERE id = 408;  -- Mochovce 3 (https://oenergetice.cz/jaderne-elektrarny/novy-slovensky-jad)
UPDATE reactors SET construction_start = '1972-08-01', updated_at = CURRENT_TIMESTAMP WHERE id = 425;  -- Kori 1 (https://world-nuclear.org/nuclear-reactor-database/details/K)
UPDATE reactors SET construction_start = '1963-09-01', updated_at = CURRENT_TIMESTAMP WHERE id = 531;  -- Wylfa 1 (https://world-nuclear.org/nuclear-reactor-database/details/W)
UPDATE reactors SET commercial_operation = '1971-11-01', updated_at = CURRENT_TIMESTAMP WHERE id = 531;  -- Wylfa 1 (https://world-nuclear.org/nuclear-reactor-database/details/W)
UPDATE reactors SET construction_start = '1963-09-01', updated_at = CURRENT_TIMESTAMP WHERE id = 532;  -- Wylfa 2 (https://world-nuclear.org/nuclear-reactor-database/details/W)
UPDATE reactors SET commercial_operation = '1972-01-03', updated_at = CURRENT_TIMESTAMP WHERE id = 532;  -- Wylfa 2 (https://world-nuclear.org/nuclear-reactor-database/details/W)
UPDATE reactors SET gross_capacity_mw = 829.0, updated_at = CURRENT_TIMESTAMP WHERE id = 675;  -- Turkey Point 3 (https://world-nuclear.org/nuclear-reactor-database/details/T)
UPDATE reactors SET gross_capacity_mw = 829.0, updated_at = CURRENT_TIMESTAMP WHERE id = 676;  -- Turkey Point 4 (https://world-nuclear.org/nuclear-reactor-database/details/T)
COMMIT;
