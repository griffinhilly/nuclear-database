-- Migration 017: Turbine-speed sweep — remaining 87 design series
-- Ledger: constants_audit_2026-07.md (finding F1 extension). 2026-07-20.
-- Two research agents classified every series not covered by migration 016;
-- orchestrator overrode three agent verdicts on grid-frequency grounds
-- (Monju/MHI/ATR are in Japan's 60 Hz zone — see ledger).
-- Source-note convention: "(cited)" = plant/turbine-specific document;
-- "(family inference)" = design-class or national-practice evidence only.

-- Soviet/Russian full-speed families, directly cited turbine models
UPDATE design_series_specs SET turbine_speed_rpm = 3000,
  source = source || '; turbine speed corrected 2026-07 sweep (cited)'
  WHERE design_series IN ('VVER-1000/187','VVER-1000/302','VVER-1000/338',
    'VVER-1000/412','VVER-1000/428','VVER-1000/428M','VVER-1000/446',
    'VVER-1200/392M','VVER-1200/523','VVER-440/179','VVER-440/270',
    'RBMK','RBMK-1500','BN-600','BN-800','SNUPPS');

-- Soviet/UK full-speed, family/national-practice inference only
UPDATE design_series_specs SET turbine_speed_rpm = 3000,
  source = source || '; turbine speed corrected 2026-07 sweep (family inference)'
  WHERE design_series IN ('VVER-1200','VVER-1200/392B','VVER-210','VVER-365',
    'EGP-6','AMB-100','AMB-200','BN-350','PFR','SGHWR');

-- Gas-cooled / sodium-cooled superheated-steam designs on 50 Hz grids:
-- full-speed 3000 rpm (HTR-PM cited steam conditions; others design-class)
UPDATE design_series_specs SET turbine_speed_rpm = 3000,
  source = source || '; turbine speed corrected 2026-07 sweep (superheated-cycle class)'
  WHERE design_series IN ('HTR-PM','CFR-600','EL-4','Phenix','Super-Phenix',
    'AVR','THTR-300','KNK','HWGCR','PFBR');

-- US 60 Hz superheated HTGRs: full-speed 3600 (Fort St. Vrain cited, OSTI
-- GA-A13602 "standard 3600-rpm tandem-compound"; Peach Bottom family)
UPDATE design_series_specs SET turbine_speed_rpm = 3600,
  source = source || '; turbine speed corrected 2026-07 sweep (OSTI GA-A13602 / family)'
  WHERE design_series IN ('Fort St. Vrain','Peach Bottom HTGR');

-- Japan 60 Hz-zone wet-steam fleets: the naive rule assumed Japan = 50 Hz.
-- MHI PWR fleet + Fugen are Kansai/Hokuriku/Kyushu-side (60 Hz) -> 1800.
-- Hokkaido's Tomari units (50 Hz) are the exception, noted here.
UPDATE design_series_specs SET turbine_speed_rpm = 1800,
  source = source || '; turbine speed corrected 2026-07 sweep (60 Hz zone; Tomari units 1500)'
  WHERE design_series IN ('MHI 2-Loop','MHI 3-Loop','MHI 4-Loop');
UPDATE design_series_specs SET turbine_speed_rpm = 1800,
  source = source || '; turbine speed corrected 2026-07 sweep (Tsuruga 60 Hz zone)'
  WHERE design_series = 'ATR';

-- Jose Cabrera: 1800 impossible on Spain's 50 Hz grid
UPDATE design_series_specs SET turbine_speed_rpm = 1500,
  source = source || '; turbine speed corrected 2026-07 sweep (50 Hz grid)'
  WHERE design_series = 'W 1-Loop';

-- No honest single value: mixed-grid series, undocumented prototypes,
-- and Monju (60 Hz zone makes the old 1500 impossible; no document
-- supports a replacement value)
UPDATE design_series_specs SET turbine_speed_rpm = NULL,
  source = source || '; turbine speed nulled 2026-07 sweep (mixed-grid or undocumented)'
  WHERE design_series IN ('CANDU','BWR/1','BLWR-250','AM-1','DFR','KLT-40S',
    'BREST-OD-300','OCR','SGR','LMFBR','PLWBR','Saxton','Monju');

-- KEEP (verified correct, no change): all Chinese wet-steam PWRs (ACP100,
-- ACPR-1000, M310, CNP-*, CAP1000, CAP1400), Akkuyu VVER-1200/509 (GE
-- Arabelle half-speed export — the one legitimate 1500 rpm VVER), Konvoi/
-- Pre-Konvoi, Siemens 2/3-Loop, B&W 2-Loop, BWR/72/75/G1/G2/G3, N4, CAREM,
-- PHWR (KWU), KWU PHWR, PHWR-700, CANDU 500/750/850, CE System 80,
-- B&W Raised-Loop, BWR/2, CVTR, BR-3.
