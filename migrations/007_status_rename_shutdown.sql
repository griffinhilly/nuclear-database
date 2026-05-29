-- 007_status_rename_shutdown.sql
-- Date: 2026-05-28
-- Description: Rename status value "Permanent Shutdown" -> "Shutdown" fleet-wide.
--   Rationale (Noah + REG editorial): REG argues several German/Belgian units should
--   be refurbished and restarted, so "Permanent" contradicts the firm's own position.
--   "Suspended" remains the shorter-term-offline category.
-- Affected tables: reactors.status (~223 rows after migration 006 moved out 3 never-operated),
--   entity_descriptions (status row).
-- IMPORTANT: the matching code-side replacement ('Permanent Shutdown'->'Shutdown' in
--   app.py / database.py / templates) ships in the same commit — DB and code must deploy together.

UPDATE reactors SET status='Shutdown' WHERE status='Permanent Shutdown';

UPDATE entity_descriptions
   SET entity_name='Shutdown',
       description='The reactor has been taken out of service and is not currently generating electricity. (Formerly labelled "Permanent Shutdown"; renamed because shutdown is not always irreversible — some units may be refurbished and returned to service.)',
       updated_at=CURRENT_TIMESTAMP
 WHERE entity_type='status' AND entity_name='Permanent Shutdown';
