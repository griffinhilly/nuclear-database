-- 011_novovoronezh5_vver1000_187.sql
-- Date: 2026-07-06
-- Description: Novovoronezh-5 (V-187) is the prototype VVER-1000, not a VVER-440
--   variant. Renames series VVER-440/187 -> VVER-1000/187, rewires the VVER-1000
--   predecessor chain (VVER-440/213 -> VVER-1000/187 -> VVER-1000/302), fixes the
--   V-302 series description (which wrongly claimed Novovoronezh-5), replaces the
--   VVER-440 physics on the specs row with V-187 values (uncertain fields NULLed
--   pending sourced completion), and rewrites the V-187 model description (which
--   wrongly placed it at Kola as a VVER-440 variant).
-- Affected tables: design_series_info (bump + 2 rows), design_series_specs (1),
--   reactors (1), entity_descriptions (1). ~30 rows total incl. order bump.

-- 1. Make room in the lineage display order: bump VVER rows at order >= 6
UPDATE design_series_info
SET generation_order = generation_order + 1
WHERE lineage_id = (SELECT id FROM design_lineages WHERE name = 'VVER')
  AND generation_order >= 6;

-- 2. Rename + correct the series row (was: Gen II VVER-440 variant, pred VVER-365)
UPDATE design_series_info
SET design_series = 'VVER-1000/187',
    generation_order = 6,
    typical_capacity_mwe = '950-1000',
    predecessor = 'VVER-440/213',
    description = 'Novovoronezh-5 — first VVER-1000 prototype (V-187 reactor plant). Four-loop, full containment. Established the template for all subsequent VVER-1000 variants.'
WHERE design_series = 'VVER-440/187';

-- 3. V-302 descends from the prototype; its old description claimed Novovoronezh-5
UPDATE design_series_info
SET predecessor = 'VVER-1000/187',
    description = 'South Ukraine-1. First small-series production VVER-1000 (V-302), developed from the V-187 prototype. Four-loop, full containment.'
WHERE design_series = 'VVER-1000/302';

-- 4. Reactor row: Novovoronezh 1 unit 5
UPDATE reactors
SET design_series = 'VVER-1000/187'
WHERE plant_name = 'Novovoronezh 1' AND unit_number = '5';

-- 5. Specs row held VVER-440 physics (1375 MWth, 6 loops, 349 FAs) under the
--    misnamed series. Replace with high-confidence V-187 values; NULL the rest
--    for sourced completion in the descriptions pass.
UPDATE design_series_specs
SET design_series = 'VVER-1000/187',
    thermal_power_mwth = 3000.0,
    number_of_coolant_loops = 4,
    number_of_steam_generators = 4,
    number_of_fuel_assemblies = 163,
    core_height_m = 3.55,
    core_diameter_m = NULL,
    operating_pressure_bar = NULL,
    enrichment_pct = NULL,
    number_of_control_elements = NULL,
    outlet_temperature_c = 320.0,
    inlet_temperature_c = 289.0,
    average_burnup_mwd_per_t = NULL,
    number_of_turbines = 2,
    turbine_speed_rpm = 1500,
    low_pressure_sections = NULL,
    live_steam_pressure_bar = NULL,
    source = 'IAEA PRIS, Wikipedia (V-187 prototype; NULLed fields pending sourced values)'
WHERE design_series = 'VVER-440/187';

-- 6. Model description: old text placed V-187 at Kola as a VVER-440 variant
UPDATE entity_descriptions
SET description = 'The VVER V-187 was the prototype VVER-1000 reactor plant, built as Novovoronezh unit 5 in Russia''s Voronezh Oblast and grid-connected in 1980. It introduced the four-loop, 3,000 MWth configuration and the full pressurized containment that became the template for every later VVER-1000 variant. It drives two 500 MW half-speed turbines rather than the single 1,000 MW machine used by later serial units.',
    updated_at = CURRENT_TIMESTAMP
WHERE entity_type = 'model' AND entity_name = 'VVER V-187';
