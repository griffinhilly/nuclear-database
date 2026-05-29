-- 005_noah_artifact_canada.sql
-- Date: 2026-05-28
-- Description: (R2) Remove the PRIS reactor-type-code artifact "25" leaked into the
--   models table for two US prototypes; and unify Canadian CANDU model-name casing
--   (lowercase a/b suffixes -> uppercase A/B). Depends on 002 (VBWR model).
-- Affected tables: models (UPDATE name, DELETE orphans), reactors (UPDATE model_id)
-- Source: Noah review 2026-05-28 (noah_review.md).

-- ── R2: "25" artifact (PRIS prototype type-code, not a real model) ──────────
-- GE Vallecitos -> VBWR (Vallecitos Boiling Water Reactor, GE prototype)
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='VBWR')
 WHERE plant_name='GE Vallecitos';
-- Saxton -> NULL model (unique experimental PWR; design_series 'Saxton' carries identity)
UPDATE reactors SET model_id=NULL
 WHERE plant_name='Saxton';
-- delete the now-orphan "25" model
DELETE FROM models WHERE name='25';

-- ── Canadian CANDU casing unification ──────────────────────────────────────
-- Pickering A units 1/4 used "CANDU 500a"; units 2/3 used "CANDU 500A". Merge to 500A.
UPDATE reactors SET model_id=(SELECT id FROM models WHERE name='CANDU 500A')
 WHERE model_id=(SELECT id FROM models WHERE name='CANDU 500a');
DELETE FROM models WHERE name='CANDU 500a';
-- Uppercase the remaining lowercase suffixes (no name collisions exist)
UPDATE models SET name='CANDU 500B' WHERE name='CANDU 500b';
UPDATE models SET name='CANDU 750A' WHERE name='CANDU 750a';
UPDATE models SET name='CANDU 750B' WHERE name='CANDU 750b';
-- (CANDU 791 left as-is: a distinct designation, not a casing issue)
