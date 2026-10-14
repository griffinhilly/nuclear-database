-- 030_capacity_conflicts_and_dates.sql
-- Date: 2026-10-14
-- Description: Resolve current-rating conflicts found by scripts/site_consistency.py (reactors vs latest
--   capacity_changes row) and revert dates that migration 024 took from IAEA PRIS where PRIS is wrong.
--   Research ledgers (local): audit/capacity_conflicts_2026-10-14.psv, audit/024_single_digit_dates_verdicts.psv.
--
-- Capacity (reactors current rating, and the capacity_changes rows that must agree with it):
--   Balakovo 1/2/4, Kalinin 1/3, Rostov 2 -> gross 1000 / net 950. The Rosatom 104% programme raised THERMAL
--     power; the published electrical rating stayed 1000/950 (IAEA PRIS reactor-by-id; WNA Russia reactor table;
--     ru.wikipedia Balakovo/Rostov). The 2012 rows held derived values (1040/988, i.e. 1.04 x rating, no source):
--     they become 'thermal_uprate' events at the published rating, re-dated where a source dates them
--     (Balakovo 2 Sept 2008 "Опытная эксплуатация на 104 % мощности с сентября 2008 года"; Kalinin 1 2013
--     "Kalinin 1 was undergoing tests at 104% in 2013" (WNA); Rostov 2 Oct 2012 "С октября 2012 года ...").
--   Rostov 1 -> gross 1042 / net 989 (PRIS); its uprate row re-dated to 2009 ("С 2009 года энергоблок № 1
--     работает на уровне тепловой мощности 104 % (3200 МВт)", ru.wikipedia Rostov NPP).
--   Wolsong 1 -> gross 691 / net 661: "the refurbishment restored it to the design level of 691 MWe gross"
--     (WNA South Korea page); net 661 (PRIS). Refurbishment ended July 2011.
-- NOT changed (research blocked; listed as known exceptions in scripts/site_consistency.py):
--   Bruce 1/2 (PRIS gross 880 but no uprate date; 2012 restart values unsourced), Turkey Point 3/4 (post-uprate
--   gross not found; current gross 829 is below the NRC net 837), Quad Cities 2 (2001 row net 908 unsourced).
--
-- Dates (migration 024 had replaced correct values with PRIS values):
--   Vogtle 3 construction_start 2013-03-02 -> 2013-03-12: "The pour for the basemat at Vogtle started at about
--     21.00 local time on 12 March" (nucnet.org/news/new-milestone-in-us-as-first-concrete-is-poured-at-vogtle-3).
--   Maanshan 1 permanent_shutdown 2024-07-28 -> 2024-07-27: "shut down on 27 July and officially entered its
--     decommissioning period on 28 July" (world-nuclear-news.org/articles/taiwanese-reactor-shut-down-for-decommissioning).
--   Maanshan 2 permanent_shutdown 2025-05-18 -> 2025-05-17: taken off the grid at about 22:00 on 17 May
--     (world-nuclear-news.org/articles/reactor-closure-marks-taiwans-nuclear-exit).
--   Cernavoda 2 commercial_operation 2007-11-01 -> 2007-09-28: operator timeline (nuclearelectrica.ro/cne/en/about-us/about-us/).
--   Palisades 1 construction_start 1967-03-12 -> 1967-03-04: "The first concrete was poured on March 4, 1967"
--     (powermag.com, Palisades closes after 50 years). Single source.
-- Net capacity placeholders (net = gross, impossible for a power reactor):
--   Under construction Lufeng 1, Lianjiang 1/2, Ningde 5, Taipingling 3, Darlington SMR 1: IAEA PRIS lists
--     net = gross as a placeholder before operation -> net NULL (same rule as Taipingling 4 in migration 025).
--   Kuosheng 1/2 (shut 2021/2023): PRIS net 985 = gross 985 (design net 948) -> net NULL.
--   Big Rock Point net 72 -> 67, Humboldt Bay net 65 -> 63 (IAEA PRIS netElectricalCapacity, API pull 2026-10-13).
--   GE Vallecitos (24/24) and Saxton (3/3), research-scale units, are left as PRIS reports them.
-- Affected: reactors UPDATE 23 rows; capacity_changes UPDATE 8 rows. Backup: nuclear_reactors.db.bak-pre030-20261014

BEGIN TRANSACTION;

UPDATE reactors SET gross_capacity_mw = 1000, net_capacity_mw = 950, updated_at = CURRENT_TIMESTAMP WHERE id IN (354, 355, 357, 367, 369, 395);
UPDATE reactors SET gross_capacity_mw = 1042, net_capacity_mw = 989, updated_at = CURRENT_TIMESTAMP WHERE id = 394;
UPDATE reactors SET gross_capacity_mw = 691, net_capacity_mw = 661, updated_at = CURRENT_TIMESTAMP WHERE id = 439;

UPDATE capacity_changes SET gross_capacity_mw = 1000, net_capacity_mw = 950, change_type = 'thermal_uprate',
    source = 'IAEA PRIS; WNA; ru.wikipedia',
    notes = '104% thermal power programme (3000->3120 MWt); effective date unconfirmed. Published electrical rating unchanged at 1000/950.'
    WHERE id IN (41, 45, 47);
UPDATE capacity_changes SET effective_date = '2008-09-01', gross_capacity_mw = 1000, net_capacity_mw = 950,
    change_type = 'thermal_uprate', source = 'ru.wikipedia (Balakovo NPP); IAEA PRIS',
    notes = '104% thermal trial operation from September 2008. Published electrical rating unchanged at 1000/950.'
    WHERE id = 43;
UPDATE capacity_changes SET effective_date = '2013-01-01' WHERE id = 45;
UPDATE capacity_changes SET effective_date = '2012-10-01', gross_capacity_mw = 1000, net_capacity_mw = 950,
    change_type = 'thermal_uprate', source = 'ru.wikipedia (Rostov NPP); IAEA PRIS',
    notes = '104% thermal tests from October 2012. Published electrical rating unchanged at 1000/950.'
    WHERE id = 51;
UPDATE capacity_changes SET gross_capacity_mw = 1000, net_capacity_mw = 950, change_type = 'thermal_uprate',
    source = 'IAEA PRIS (thermal 3200 MWt)',
    notes = 'Thermal uprate to 3200 MWt (107% pilot); date unconfirmed. Published electrical rating unchanged at 1000/950.'
    WHERE id = 53;
UPDATE capacity_changes SET effective_date = '2009-01-01', gross_capacity_mw = 1042, net_capacity_mw = 989,
    source = 'ru.wikipedia (Rostov NPP); IAEA PRIS',
    notes = 'Operating at 104% thermal power (3200 MWt) since 2009.'
    WHERE id = 49;
UPDATE capacity_changes SET gross_capacity_mw = 691, net_capacity_mw = 661, source = 'WNA South Korea; IAEA PRIS',
    notes = 'Refurbishment (Apr 2009 - Jul 2011) restored the design level of 691 MWe gross.'
    WHERE id = 13;

UPDATE reactors SET construction_start = '2013-03-12', updated_at = CURRENT_TIMESTAMP WHERE id = 680;
UPDATE reactors SET permanent_shutdown = '2024-07-27', updated_at = CURRENT_TIMESTAMP WHERE id = 478;
UPDATE reactors SET permanent_shutdown = '2025-05-17', updated_at = CURRENT_TIMESTAMP WHERE id = 479;
UPDATE reactors SET commercial_operation = '2007-09-28', updated_at = CURRENT_TIMESTAMP WHERE id = 350;
UPDATE reactors SET construction_start = '1967-03-04', updated_at = CURRENT_TIMESTAMP WHERE id = 632;

UPDATE reactors SET net_capacity_mw = NULL, reference_power_mw = NULL, updated_at = CURRENT_TIMESTAMP
    WHERE id IN (699, 711, 712, 713, 717, 741, 474, 475);
UPDATE reactors SET net_capacity_mw = 67, updated_at = CURRENT_TIMESTAMP WHERE id = 558;
UPDATE reactors SET net_capacity_mw = 63, updated_at = CURRENT_TIMESTAMP WHERE id = 607;

COMMIT;
