-- 002_noah_new_models_series.sql
-- Date: 2026-05-28
-- Description: Register new reactor models + design_series lineage entries needed by
--   the Noah review corrections (migrations 003-006). Setup-only: no reactor rows
--   change here. models.name is UNIQUE; design_series is the lineage-page key.
-- Affected tables: models (INSERT OR IGNORE), design_series_info (INSERT OR IGNORE)
-- Source: Noah review 2026-05-28 (noah_review.md), verified vs IAEA PRIS / WNA.

-- New models (technology_id: 2=PWR, 6=BWR, 8=HWGCR)
INSERT OR IGNORE INTO models (name, technology_id) VALUES
  ('VVER V-510K', 2),      -- Kursk II (VVER-TOI)
  ('VVER V-527', 2),       -- Paks II
  ('VVER V-528', 2),       -- Bushehr 2/3 (AES-92)
  ('VVER V-529', 2),       -- El Dabaa
  ('VVER V-213+', 2),      -- Mochovce 3/4
  ('WH 2-loop', 2),        -- Kori-1 (replaces "W?" artifact)
  ('M310+', 2),            -- Fuqing 1-4
  ('CPR-1000+', 2),        -- Yangjiang 3/4
  ('EL-4', 8),             -- Brennilis (replaces MONTS-D'ARREE)
  ('VBWR', 6),             -- GE Vallecitos (replaces "25" PRIS-code artifact)
  ('VVER-210 (V-1)', 2),   -- Novovoronezh-1 Unit 1 (first VVER)
  ('VVER-365 (V-3M)', 2);  -- Novovoronezh-1 Unit 2

-- New design_series lineage entries (lineage_id 13=VVER, 8=M310 family, 12=CPR family)
INSERT OR IGNORE INTO design_series_info
  (design_series, lineage_id, generation_order, generation_label, typical_capacity_mwe, first_commercial_year, predecessor, description) VALUES
  ('VVER-1200/510', 13, 9, 'Gen III+', '1175-1255', 2026, 'VVER-1200/491',
     'VVER-TOI (Typical Optimised, with enhanced Information). Kursk II lead units 1-3. Most advanced serial VVER-1200 sub-type.'),
  ('VVER-1200/527', 13, 9, 'Gen III+', '1200', NULL, 'VVER-1200/491',
     'Paks II (Hungary). AES-2006 / V-491 derivative adapted for the Paks site.'),
  ('VVER-1200/529', 13, 9, 'Gen III+', '1200', NULL, 'VVER-1200/509',
     'El Dabaa (Egypt). Export AES-2006 VVER-1200 variant.'),
  ('VVER-1000/528', 13, 8, 'Gen III', '1000-1050', NULL, 'VVER-1000/446',
     'Bushehr Phase II (units 2/3, Iran). AES-92 VVER-1000 variant with additional safety systems.'),
  ('M310+', 8, 4, 'Gen II', '1000-1090', 2014, 'M310',
     'CNNC-built improved M310 (Fuqing 1-4, Fangjiashan 1-2, Tianwan 5-6). Higher domestic content than the CGN M310 units.'),
  ('CPR-1000+', 12, 5, 'Gen II', '1080', 2014, 'CPR-1000',
     'Improved CPR-1000 with ~28 safety/technical modifications (e.g. Yangjiang 3/4). Bridge to ACPR-1000.');
