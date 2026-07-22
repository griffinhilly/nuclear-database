-- Migration 021: Opus re-attestation pass — corrections + conflict resolutions
-- 2026-07-22. Ledger: verification_2026-07/union_corrections_draft.psv +
-- rerun_results/*.psv. Policy (c) union merge; entity gate: 0 violations.
-- MIXED = series spans plants with genuinely different values -> NULL.
BEGIN TRANSACTION;
UPDATE design_series_specs SET number_of_fuel_assemblies = NULL, source = source || '; number_of_fuel_assemblies nulled 2026-07-22 opus pass (mixed-within-series)' WHERE design_series = 'AGR';
UPDATE design_series_specs SET thermal_power_mwth = NULL, source = source || '; thermal_power_mwth nulled 2026-07-22 opus pass (mixed-within-series)' WHERE design_series = 'AGR';
UPDATE design_series_specs SET enrichment_pct = 3.0, source = source || '; enrichment_pct corrected 2026-07-22 opus pass (union_corrections_draft.psv)' WHERE design_series = 'AMB-200';
UPDATE design_series_specs SET number_of_turbines = 2, source = source || '; number_of_turbines corrected 2026-07-22 opus pass (union_corrections_draft.psv)' WHERE design_series = 'AMB-200';
UPDATE design_series_specs SET thermal_power_mwth = 2776, source = source || '; thermal_power_mwth corrected 2026-07-22 opus pass (union_corrections_draft.psv)' WHERE design_series = 'CANDU 850';
UPDATE design_series_specs SET thermal_power_mwth = 60.0, source = source || '; thermal_power_mwth corrected 2026-07-22 opus pass (union_corrections_draft.psv)' WHERE design_series = 'DFR';
UPDATE design_series_specs SET thermal_power_mwth = NULL, source = source || '; thermal_power_mwth nulled 2026-07-22 opus pass (mixed-within-series)' WHERE design_series = 'KWU PHWR';
UPDATE design_series_specs SET core_diameter_m = NULL, source = source || '; core_diameter_m nulled 2026-07-22 opus pass (mixed-within-series)' WHERE design_series = 'Magnox';
UPDATE design_series_specs SET core_height_m = NULL, source = source || '; core_height_m nulled 2026-07-22 opus pass (mixed-within-series)' WHERE design_series = 'Magnox';
UPDATE design_series_specs SET number_of_control_elements = NULL, source = source || '; number_of_control_elements nulled 2026-07-22 opus pass (mixed-within-series)' WHERE design_series = 'Magnox';
UPDATE design_series_specs SET low_pressure_sections = 4, source = source || '; low_pressure_sections corrected 2026-07-22 opus pass (union_corrections_draft.psv)' WHERE design_series = 'RBMK';
UPDATE design_series_specs SET fuel_type = 'Metallic uranium-molybdenum alloy (first core); uranium carbide (later core) — not oxide', source = source || '; fuel_type corrected 2026-07-22 opus pass (union_corrections_draft.psv)' WHERE design_series = 'SGR';
UPDATE design_series_specs SET number_of_control_elements = NULL, source = source || '; number_of_control_elements nulled 2026-07-22 opus pass (mixed-within-series, conflict resolved v sonnet)' WHERE design_series = 'BWR/4';
UPDATE design_series_specs SET number_of_fuel_assemblies = NULL, source = source || '; number_of_fuel_assemblies nulled 2026-07-22 opus pass (mixed-within-series, conflict resolved v sonnet)' WHERE design_series = 'BWR/4';
UPDATE design_series_specs SET thermal_power_mwth = NULL, source = source || '; thermal_power_mwth nulled 2026-07-22 opus pass (mixed-within-series, conflict resolved v sonnet)' WHERE design_series = 'BWR/4';
UPDATE design_series_specs SET thermal_power_mwth = 3425, source = source || '; thermal corrected 2026-07-22 opus pass (Sizewell B-specific, conflict resolved v sonnet)' WHERE design_series = 'SNUPPS';
COMMIT;
