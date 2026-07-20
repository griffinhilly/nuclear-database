-- Migration 016: Hardcoded-constants audit — confirmed fixes
-- Ledger: constants_audit_2026-07.md (findings F1/F2/F4). 2026-07-20.
-- Scope: design_series_specs values proven WRONG by sourced verification,
-- Magnox/UNGG unrepresentable values set NULL (matches the BWR/1 "too
-- variable" convention), turbine speeds for the 7 series confirmed wrong
-- (remaining series await the sweep -> migration 017), and 4 planned_reactors
-- corrections. reactor_details is untouched here (fields hidden in app pending
-- full re-verification).

-- === F2: thermal power / fuel / pressure corrections ===

-- CP1/CP2 (CPY palier) thermal power: 2660 is the CP0 figure; palier value is
-- 2785 MWth (PRIS unit pages for Dampierre/Gravelines/Tricastin; palier docs).
UPDATE design_series_specs SET thermal_power_mwth = 2785,
  source = source || '; thermal corrected 2026-07 audit (PRIS palier CPY)'
  WHERE design_series IN ('CP1', 'CP2');

-- Siemens 4-Loop (Konvoi class): 3690 matches no source; Konvoi design = 3765.
UPDATE design_series_specs SET thermal_power_mwth = 3765,
  source = source || '; thermal corrected 2026-07 audit (Konvoi design value)'
  WHERE design_series = 'Siemens 4-Loop';

-- IPHWR-220: IAEA ARIS Status Report 74 gives 754.5 MWth; PHT pressure
-- ~87 kg/cm2(g) ~ 85 bar, not 95.
UPDATE design_series_specs SET thermal_power_mwth = 754.5,
  operating_pressure_bar = 85.0,
  source = source || '; thermal+pressure corrected 2026-07 audit (IAEA ARIS SR-74)'
  WHERE design_series = 'IPHWR';

-- HPR1000: official CGN/CNNC design paper gives 3050 MWth, not 3150.
UPDATE design_series_specs SET thermal_power_mwth = 3050,
  source = source || '; thermal corrected 2026-07 audit (HPR1000 design paper, Engineering)'
  WHERE design_series = 'HPR1000';

-- BWR/5: row was a copy of BWR/4; reference BWR/5 (LaSalle) = 3323 MWth.
UPDATE design_series_specs SET thermal_power_mwth = 3323,
  source = source || '; thermal corrected 2026-07 audit (LaSalle original rating)'
  WHERE design_series = 'BWR/5';

-- BWR/3: 2381 matches no BWR/3 unit; reference-plant convention (largest
-- standard, Dresden 2/3 original license) = 2527 MWth.
UPDATE design_series_specs SET thermal_power_mwth = 2527,
  source = source || '; thermal corrected 2026-07 audit (Dresden 2/3 original license)'
  WHERE design_series = 'BWR/3';

-- BWR/69 franken-row: 2575 MWth is Isar 1, 840 assemblies is Kruemmel.
-- Align the row to the Isar-1 reference: 592 fuel elements.
UPDATE design_series_specs SET number_of_fuel_assemblies = 592,
  source = source || '; fuel count corrected 2026-07 audit (Isar 1, was Kruemmel''s)'
  WHERE design_series = 'BWR/69';

-- Magnox: single series values are unrepresentable (stations spanned
-- ~200-1875 MWth, 6.9-27 bar, widely varying element counts and turbine
-- layouts). NULL per the established "too variable" convention.
UPDATE design_series_specs SET thermal_power_mwth = NULL,
  number_of_fuel_assemblies = NULL, operating_pressure_bar = NULL,
  number_of_turbines = NULL, live_steam_pressure_bar = NULL,
  source = source || '; station-variant fields nulled 2026-07 audit (too variable across fleet)'
  WHERE design_series = 'Magnox';

-- UNGG: same problem (Chinon A1 ~300 MWth to Bugey 1 ~1950), values were
-- unsourced. NULL thermal + turbine fields; keep pressure? No - unverified.
UPDATE design_series_specs SET thermal_power_mwth = NULL,
  operating_pressure_bar = NULL, number_of_turbines = NULL,
  live_steam_pressure_bar = NULL, turbine_speed_rpm = NULL,
  source = source || '; station-variant fields nulled 2026-07 audit (too variable, unsourced)'
  WHERE design_series = 'UNGG';

-- === F1: turbine speeds confirmed wrong (full-speed 3000 rpm machines) ===
-- VVER: LMZ K-1000-60/3000 (V-320), K-220-44 (V-213/V-230), K-1200-6.8/50
-- (V-491 domestic). RBMK: K-500-65/3000. Magnox: Calder Hall 3000 rpm.
-- AGR: full-speed fleet per Sizewell-B comparison sources.
UPDATE design_series_specs SET turbine_speed_rpm = 3000,
  source = source || '; turbine speed corrected 2026-07 audit (full-speed machines)'
  WHERE design_series IN ('VVER-1000/320', 'VVER-440/213', 'VVER-440/230',
                          'VVER-1200/491', 'RBMK-1000', 'Magnox', 'AGR');

-- === F4: planned_reactors corrections ===

-- Duwayhin (Saudi Arabia): entry fabricated specifics. WNA: no vendor
-- selected, no construction date announced. Strip to honest TBD; keep
-- integer year estimates (schema requires int; app sorts them), demote
-- likelihood High->Low pending vendor award.
UPDATE planned_reactors SET model = 'TBD', vendor = 'TBD',
  vendor_country = NULL, gross_capacity_mw = NULL, net_capacity_mw = NULL,
  likelihood = 'Low', likelihood_rating = 3,
  notes = 'First NPP program for Saudi Arabia; bids solicited from Chinese, French, Korean and Russian vendors. No vendor selected and no construction start announced as of Jul 2026 (WNA Saudi Arabia profile). Prior entry claimed APR1400/Q1-2026 start without source support - corrected 2026-07 audit.'
  WHERE project_name = 'Duwayhin';

-- Novocherkassk: WNN coverage of Russia's draft general scheme describes the
-- planned units as VVER-optimum, not VVER-TOI. Capacities kept as class
-- estimates, marked provisional.
UPDATE planned_reactors SET model = 'VVER-optimum (provisional)',
  notes = 'In Russia''s draft general scheme; WNN reports planned units as VVER-optimum (not VVER-TOI as previously listed - corrected 2026-07 audit). Capacity figures are class estimates.'
  WHERE project_name = 'Novocherkassk';

-- Almaty Region NPP: resolution dated Jan 26 2026; reports indicate CNNC
-- awarded the contract for this second plant.
UPDATE planned_reactors SET vendor = 'CNNC (reported)', vendor_country = 'China',
  notes = 'Second NPP approved by Government Resolution No. 40 of Jan 26, 2026, Ulken/Zhambyl district, Almaty Region. CNNC reported awarded the contract. Updated 2026-07 audit.'
  WHERE project_name = 'Almaty Region NPP';

-- Kalpakkam FBR-600: note overstated certainty; only pre-project activities
-- approved, construction start not sanctioned.
UPDATE planned_reactors SET
  notes = 'Follow-on fast breeder reactors at Kalpakkam (FBR-600 class). Only pre-project activities approved; formal financial sanction pending as of early 2026. Year figures are speculative. Source: WNA India; softened 2026-07 audit.'
  WHERE project_name = 'Kalpakkam FBR';
