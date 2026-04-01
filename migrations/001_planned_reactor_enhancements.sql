-- Migration 001: Planned reactor detail page support
-- Date: 2026-04-01
-- Description: Add columns for planned reactor detail pages (coordinates, description, developer)
--              Insert Sizewell C (2 units) as a planned reactor
-- Affected tables: planned_reactors
-- New rows: 2

-- Add new columns for detail page support
ALTER TABLE planned_reactors ADD COLUMN latitude REAL;
ALTER TABLE planned_reactors ADD COLUMN longitude REAL;
ALTER TABLE planned_reactors ADD COLUMN description TEXT;
ALTER TABLE planned_reactors ADD COLUMN developer TEXT;
ALTER TABLE planned_reactors ADD COLUMN thermal_capacity_mw REAL;
ALTER TABLE planned_reactors ADD COLUMN cost_estimate TEXT;

-- Insert Sizewell C Unit 1
INSERT INTO planned_reactors (
    project_name, unit_number, country_id, site_location,
    technology_id, model, gross_capacity_mw, net_capacity_mw,
    thermal_capacity_mw, vendor, vendor_country, is_export,
    expected_construction_start, expected_online,
    likelihood, likelihood_rating, status, notes,
    latitude, longitude, developer, cost_estimate, description
) VALUES (
    'Sizewell C', '1', 36, 'Suffolk',
    2, 'EPR', 1720.0, 1630.0,
    4524.0, 'Framatome', 'France', 0,
    2026, 2035,
    'High', 1, 'FID achieved',
    'Development Consent Order granted July 2022. Site preparation began January 2024. Final Investment Decision achieved 22 July 2025 with estimated construction cost of £38 billion. Replicates Hinkley Point C EPR design. Ownership: UK Government 44.9%, CDPQ 20%, Centrica 15%, EDF 12.5%, Amber Infrastructure 7.6%. 60-year operational lifespan projected. Expected to supply ~7% of UK electricity demand.',
    52.2193, 1.6203, 'NNB Generation Company (SZC) Limited',
    '£38 billion (July 2025 estimate)',
    'Sizewell C is a planned two-unit EPR nuclear power station on the Suffolk coast in eastern England, adjacent to the operating Sizewell B PWR and decommissioned Sizewell A Magnox station. The project replicates the Hinkley Point C design to achieve construction and cost efficiencies, with each EPR unit rated at 1,630 MWe net. Developed by NNB Generation Company (SZC) Limited — a consortium led by the UK Government (44.9%), with stakes from CDPQ, Centrica, EDF, and Amber Infrastructure — the project received its Development Consent Order in July 2022 and achieved Final Investment Decision in July 2025 at an estimated construction cost of £38 billion. Site preparation began in January 2024, with core construction expected to follow. Once operational, Sizewell C is expected to supply approximately 7% of UK electricity demand over a 60-year operational lifespan.'
);

-- Insert Sizewell C Unit 2
INSERT INTO planned_reactors (
    project_name, unit_number, country_id, site_location,
    technology_id, model, gross_capacity_mw, net_capacity_mw,
    thermal_capacity_mw, vendor, vendor_country, is_export,
    expected_construction_start, expected_online,
    likelihood, likelihood_rating, status, notes,
    latitude, longitude, developer, cost_estimate, description
) VALUES (
    'Sizewell C', '2', 36, 'Suffolk',
    2, 'EPR', 1720.0, 1630.0,
    4524.0, 'Framatome', 'France', 0,
    2026, 2036,
    'High', 1, 'FID achieved',
    'Development Consent Order granted July 2022. Site preparation began January 2024. Final Investment Decision achieved 22 July 2025 with estimated construction cost of £38 billion. Replicates Hinkley Point C EPR design. Ownership: UK Government 44.9%, CDPQ 20%, Centrica 15%, EDF 12.5%, Amber Infrastructure 7.6%. 60-year operational lifespan projected. Expected to supply ~7% of UK electricity demand.',
    52.2193, 1.6203, 'NNB Generation Company (SZC) Limited',
    '£38 billion (July 2025 estimate)',
    'Sizewell C is a planned two-unit EPR nuclear power station on the Suffolk coast in eastern England, adjacent to the operating Sizewell B PWR and decommissioned Sizewell A Magnox station. The project replicates the Hinkley Point C design to achieve construction and cost efficiencies, with each EPR unit rated at 1,630 MWe net. Developed by NNB Generation Company (SZC) Limited — a consortium led by the UK Government (44.9%), with stakes from CDPQ, Centrica, EDF, and Amber Infrastructure — the project received its Development Consent Order in July 2022 and achieved Final Investment Decision in July 2025 at an estimated construction cost of £38 billion. Site preparation began in January 2024, with core construction expected to follow. Once operational, Sizewell C is expected to supply approximately 7% of UK electricity demand over a 60-year operational lifespan.'
);
