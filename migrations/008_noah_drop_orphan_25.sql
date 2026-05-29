-- 008_noah_drop_orphan_25.sql
-- Date: 2026-05-28
-- Description: Delete the orphaned "25" model that migration 005 missed. Root cause:
--   the model name is literally the 4-character string `"25"` (with quote chars — itself
--   part of the PRIS reactor-type-code artifact), so 005's `WHERE name='25'` never matched.
--   Its two reactors (GE Vallecitos -> VBWR, Saxton -> NULL) were already reassigned in 005,
--   so the row is now orphaned and safe to delete.
-- Affected tables: models (DELETE 1 row)
DELETE FROM models
 WHERE name = '"25"'
   AND id NOT IN (SELECT DISTINCT model_id FROM reactors WHERE model_id IS NOT NULL);
