-- 028_status_updates.sql
-- Date: 2026-10-13
-- Description: Status decisions from audit batch C (Griffin approved "statuses as recommended").
--   Sanao 1 -> Operational: grid-connected 2026-03-12 (world-nuclear-news.org/articles/first-sanao-unit-connected-to-the-grid).
--   Tarapur 1, 2 -> Operational: back on the grid after refurbishment; AERB approved unit 2 restart on 7 May
--     (world-nuclear-news.org/articles/worlds-oldest-operating-nuclear-units-back-on-indias-grid).
--   Tsuruga 2 -> Suspended: NRA rejected restart (Nov 2024) but JAPC has not permanently closed the unit,
--     so the 2024-11-13 "permanent shutdown" date is cleared (en.wikipedia.org/wiki/Tsuruga_Nuclear_Power_Plant; IAEA PRIS: Suspended).
--   Unchanged after research: Kashiwazaki-Kariwa 6 stays Operational (resumed commercial operation Apr 2026;
--     PRIS stale), Palisades stays Suspended (fuel loading, no restart reported by 2026-10-13), Bushehr 3 stays
--     planned (no source reports first concrete).
-- Ledger: audit/batch_c/triage.json (local). Rows: 4 reactors. Backup: nuclear_reactors.db.bak-pre028-20261013

BEGIN TRANSACTION;
UPDATE reactors SET status = 'Operational', updated_at = CURRENT_TIMESTAMP WHERE plant_name = 'Sanao' AND unit_number = '1';
UPDATE reactors SET status = 'Operational', notes = 'Offline 2020-2026 for refurbishment; back on the grid 2026 (WNN).',
       updated_at = CURRENT_TIMESTAMP WHERE plant_name = 'Tarapur' AND unit_number = '1';
UPDATE reactors SET status = 'Operational', notes = 'Offline 2020-2026 for refurbishment; AERB approved restart 7 May 2026 (WNN).',
       updated_at = CURRENT_TIMESTAMP WHERE plant_name = 'Tarapur' AND unit_number = '2';
UPDATE reactors SET status = 'Suspended', permanent_shutdown = NULL,
       notes = 'NRA rejected restart Nov 2024 (active-fault finding); not permanently closed by JAPC — Suspended per IAEA PRIS.',
       updated_at = CURRENT_TIMESTAMP WHERE plant_name = 'Tsuruga' AND unit_number = '2';
COMMIT;
