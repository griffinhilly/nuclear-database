-- 034_phase2_wave1.sql
-- Date: 2026-10-14 (approved by Griffin 2026-10-14; Indian Point 1 design series option 1)
-- Description: Phase 2 fleet audit, wave 1. Three tiers per batch: 3 Haiku researchers -> Sonnet
--   adjudication -> Opus refutation with an independent second source. Only Opus-UPHELD changes are written;
--   values mapped to existing house spellings. Each UPDATE is guarded on the old value.
--   Per-change sources and quotes: audit/phase2/wave1_changes.psv (local).
-- Writes: 170. Skipped: 25 (see audit/phase2/wave1_skipped.psv).
-- Vendor values are appended to the whitelist (verification_2026-07/final_verdicts.psv) in the same change.
-- Backup: nuclear_reactors.db.bak-pre034-20261014

BEGIN TRANSACTION;
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 600 AND (architect_engineer IS NULL);  -- Grand Gulf 1
UPDATE reactors SET licensed_until = '2047' WHERE id = 557 AND (licensed_until = '2036');  -- Beaver Valley 2
UPDATE reactor_details SET constructor = 'Peter Kiewit Sons' WHERE reactor_id = 602 AND (constructor IS NULL);  -- Hallam 1
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 602 AND (architect_engineer IS NULL);  -- Hallam 1
UPDATE reactor_details SET constructor = 'Brown & Root' WHERE reactor_id = 565 AND (constructor IS NULL);  -- Brunswick 1
UPDATE reactor_details SET constructor = 'Brown & Root' WHERE reactor_id = 566 AND (constructor IS NULL);  -- Brunswick 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Chicago Bridge & Iron' WHERE reactor_id = 566 AND (pressure_vessel_manufacturer IS NULL);  -- Brunswick 2
UPDATE reactors SET licensed_until = '2050' WHERE id = 643 AND (licensed_until = '2030');  -- Point Beach 1
UPDATE reactors SET licensed_until = '2053' WHERE id = 644 AND (licensed_until = '2033');  -- Point Beach 2
UPDATE reactor_details SET architect_engineer = 'Stone & Webster' WHERE reactor_id = 582 AND (architect_engineer IS NULL);  -- CVTR 1
UPDATE reactor_details SET constructor = 'Aecon Kiewit Nuclear Partners' WHERE reactor_id = 741 AND (constructor IS NULL);  -- Darlington SMR 1
UPDATE reactor_details SET turbine_supplier = 'Arabelle Solutions' WHERE reactor_id = 741 AND (turbine_supplier IS NULL);  -- Darlington SMR 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'BWX Technologies' WHERE reactor_id = 741 AND (pressure_vessel_manufacturer IS NULL);  -- Darlington SMR 1
UPDATE reactor_details SET constructor = 'Ebasco' WHERE reactor_id = 677 AND (constructor IS NULL);  -- Vermont Yankee 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 654 AND (constructor IS NULL);  -- San Onofre 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Combustion Engineering' WHERE reactor_id = 654 AND (pressure_vessel_manufacturer IS NULL);  -- San Onofre 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 655 AND (constructor IS NULL);  -- San Onofre 2
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 655 AND (architect_engineer IS NULL);  -- San Onofre 2
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 656 AND (constructor IS NULL);  -- San Onofre 3
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 656 AND (architect_engineer IS NULL);  -- San Onofre 3
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 623 AND (constructor IS NULL);  -- Monticello 1
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 623 AND (architect_engineer IS NULL);  -- Monticello 1
UPDATE reactors SET licensed_until = '2050' WHERE id = 623 AND (licensed_until = '2030');  -- Monticello 1
UPDATE reactors SET licensed_until = '2044' WHERE id = 19 AND (licensed_until IS NULL);  -- Angra 1
UPDATE reactors SET licensed_until = '2041' WHERE id = 20 AND (licensed_until IS NULL);  -- Angra 2
UPDATE reactor_details SET architect_engineer = 'Sargent & Lundy' WHERE reactor_id = 613 AND (architect_engineer IS NULL);  -- LaSalle 1
UPDATE reactor_details SET architect_engineer = 'Sargent & Lundy' WHERE reactor_id = 614 AND (architect_engineer IS NULL);  -- LaSalle 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Combustion Engineering' WHERE reactor_id = 596 AND (pressure_vessel_manufacturer IS NULL);  -- Fort Calhoun 1
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 584 AND (containment_type IS NULL);  -- Diablo Canyon 1
UPDATE reactor_details SET constructor = 'Pacific Gas & Electric' WHERE reactor_id = 584 AND (constructor IS NULL);  -- Diablo Canyon 1
UPDATE reactor_details SET architect_engineer = 'Pacific Gas & Electric' WHERE reactor_id = 584 AND (architect_engineer IS NULL);  -- Diablo Canyon 1
UPDATE reactor_details SET constructor = 'Pacific Gas & Electric' WHERE reactor_id = 585 AND (constructor IS NULL);  -- Diablo Canyon 2
UPDATE reactor_details SET architect_engineer = 'Pacific Gas & Electric' WHERE reactor_id = 585 AND (architect_engineer IS NULL);  -- Diablo Canyon 2
UPDATE reactors SET licensed_until = '2036' WHERE id = 2 AND (licensed_until IS NULL);  -- Atucha 2
UPDATE reactor_details SET architect_engineer = 'Pioneer Service & Engineering' WHERE reactor_id = 645 AND (architect_engineer IS NULL);  -- Prairie Island 1
UPDATE reactor_details SET architect_engineer = 'Pioneer Service & Engineering' WHERE reactor_id = 646 AND (architect_engineer IS NULL);  -- Prairie Island 2
UPDATE reactors SET design_series = 'Indian Point 1' WHERE id = 608 AND (design_series = 'W 4-Loop');  -- Indian Point 1
UPDATE reactor_details SET architect_engineer = 'TVA' WHERE reactor_id = 660 AND (architect_engineer IS NULL);  -- Sequoyah 2
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 663 AND (containment_type IS NULL);  -- South Texas Project 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 589 AND (constructor IS NULL);  -- Duane Arnold 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Babcock & Wilcox' WHERE reactor_id = 628 AND (pressure_vessel_manufacturer IS NULL);  -- Oconee 1
UPDATE reactors SET licensed_until = '2053' WHERE id = 628 AND (licensed_until = '2033');  -- Oconee 1
UPDATE reactor_details SET constructor = 'Duke Power' WHERE reactor_id = 629 AND (constructor IS NULL);  -- Oconee 2
UPDATE reactor_details SET architect_engineer = 'Duke Power' WHERE reactor_id = 629 AND (architect_engineer IS NULL);  -- Oconee 2
UPDATE reactors SET licensed_until = '2053' WHERE id = 629 AND (licensed_until = '2033');  -- Oconee 2
UPDATE reactor_details SET constructor = 'Duke Power' WHERE reactor_id = 630 AND (constructor IS NULL);  -- Oconee 3
UPDATE reactor_details SET architect_engineer = 'Duke Power' WHERE reactor_id = 630 AND (architect_engineer IS NULL);  -- Oconee 3
UPDATE reactors SET licensed_until = '2054' WHERE id = 630 AND (licensed_until = '2034');  -- Oconee 3
UPDATE reactors SET licensed_until = '2047' WHERE id = 574 AND (licensed_until = '2026');  -- Clinton 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Combustion Engineering' WHERE reactor_id = 580 AND (pressure_vessel_manufacturer IS NULL);  -- Cooper 1
UPDATE reactor_details SET architect_engineer = 'Burns & Roe' WHERE reactor_id = 631 AND (architect_engineer IS NULL);  -- Oyster Creek 1
UPDATE reactors SET licensed_until = '2032' WHERE id = 51 AND (licensed_until IS NULL);  -- Point Lepreau 1
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 599 AND (containment_type IS NULL);  -- Ginna (R. E. Ginna) 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 599 AND (constructor IS NULL);  -- Ginna (R. E. Ginna) 1
UPDATE reactor_details SET architect_engineer = 'Gilbert Associates' WHERE reactor_id = 599 AND (architect_engineer IS NULL);  -- Ginna (R. E. Ginna) 1
UPDATE reactor_details SET architect_engineer = 'Gilbert Associates' WHERE reactor_id = 640 AND (architect_engineer IS NULL);  -- Perry 1
UPDATE reactors SET licensed_until = '2046' WHERE id = 640 AND (licensed_until = '2026');  -- Perry 1
UPDATE reactor_details SET constructor = 'Atomics International' WHERE reactor_id = 642 AND (constructor IS NULL);  -- Piqua 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 583 AND (constructor IS NULL);  -- Davis Besse 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 641 AND (constructor IS NULL);  -- Pilgrim 1
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 641 AND (architect_engineer IS NULL);  -- Pilgrim 1
UPDATE reactor_details SET constructor = 'Nucleoeléctrica Argentina (NA-SA)' WHERE reactor_id = 3 AND (constructor = 'CNEA');  -- Carem25 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'IMPSA' WHERE reactor_id = 3 AND (pressure_vessel_manufacturer IS NULL);  -- Carem25 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 621 AND (constructor IS NULL);  -- Millstone 2
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 621 AND (architect_engineer IS NULL);  -- Millstone 2
UPDATE reactor_details SET architect_engineer = 'Stone & Webster' WHERE reactor_id = 622 AND (architect_engineer IS NULL);  -- Millstone 3
UPDATE reactor_details SET architect_engineer = 'TVA' WHERE reactor_id = 562 AND (architect_engineer IS NULL);  -- Browns Ferry 1
UPDATE reactors SET licensed_until = '2053' WHERE id = 562 AND (licensed_until = '2033');  -- Browns Ferry 1
UPDATE reactor_details SET architect_engineer = 'TVA' WHERE reactor_id = 563 AND (architect_engineer IS NULL);  -- Browns Ferry 2
UPDATE reactors SET licensed_until = '2054' WHERE id = 563 AND (licensed_until = '2034');  -- Browns Ferry 2
UPDATE reactor_details SET constructor = 'TVA' WHERE reactor_id = 564 AND (constructor IS NULL);  -- Browns Ferry 3
UPDATE reactor_details SET architect_engineer = 'TVA' WHERE reactor_id = 564 AND (architect_engineer IS NULL);  -- Browns Ferry 3
UPDATE reactors SET licensed_until = '2056' WHERE id = 564 AND (licensed_until = '2036');  -- Browns Ferry 3
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 598 AND (architect_engineer IS NULL);  -- GE Vallecitos 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Combustion Engineering' WHERE reactor_id = 665 AND (pressure_vessel_manufacturer IS NULL);  -- St Lucie 1
UPDATE reactors SET licensed_until = '2056' WHERE id = 665 AND (licensed_until = '2036');  -- St Lucie 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Combustion Engineering' WHERE reactor_id = 666 AND (pressure_vessel_manufacturer IS NULL);  -- St Lucie 2
UPDATE reactors SET licensed_until = '2063' WHERE id = 666 AND (licensed_until = '2043');  -- St Lucie 2
UPDATE reactors SET licensed_until = '2058' WHERE id = 626 AND (licensed_until = '2038');  -- North Anna 1
UPDATE reactor_details SET architect_engineer = 'Stone & Webster' WHERE reactor_id = 627 AND (architect_engineer IS NULL);  -- North Anna 2
UPDATE reactors SET licensed_until = '2060' WHERE id = 627 AND (licensed_until = '2040');  -- North Anna 2
UPDATE reactor_details SET constructor = 'Ontario Hydro' WHERE reactor_id = 43 AND (constructor IS NULL);  -- Pickering 1
UPDATE reactor_details SET constructor = 'Ontario Hydro' WHERE reactor_id = 44 AND (constructor IS NULL);  -- Pickering 2
UPDATE reactor_details SET constructor = 'Ontario Hydro' WHERE reactor_id = 45 AND (constructor IS NULL);  -- Pickering 3
UPDATE reactor_details SET constructor = 'Ontario Hydro' WHERE reactor_id = 46 AND (constructor IS NULL);  -- Pickering 4
UPDATE reactors SET licensed_until = '2028' WHERE id = 50 AND (licensed_until IS NULL);  -- Pickering 8
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 615 AND (constructor IS NULL);  -- Limerick 1
UPDATE reactor_details SET constructor = 'Daniel International' WHERE reactor_id = 569 AND (constructor IS NULL);  -- Callaway 1
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 569 AND (architect_engineer IS NULL);  -- Callaway 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Combustion Engineering' WHERE reactor_id = 661 AND (pressure_vessel_manufacturer IS NULL);  -- Shippingport 1
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 591 AND (containment_type IS NULL);  -- Farley (Joseph M. Farley) 1
UPDATE reactor_details SET architect_engineer = 'American Electric Power' WHERE reactor_id = 578 AND (architect_engineer IS NULL);  -- Cook (Donald C. Cook) 1
UPDATE reactor_details SET architect_engineer = 'American Electric Power' WHERE reactor_id = 579 AND (architect_engineer IS NULL);  -- Cook (Donald C. Cook) 2
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 558 AND (constructor IS NULL);  -- Big Rock Point 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 586 AND (constructor = 'GE');  -- Dresden 1
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 586 AND (architect_engineer IS NULL);  -- Dresden 1
UPDATE reactors SET licensed_until = '2051' WHERE id = 588 AND (licensed_until = '2031');  -- Dresden 3
UPDATE reactor_details SET constructor = 'Stone & Webster' WHERE reactor_id = 686 AND (constructor IS NULL);  -- Yankee NPS 1
UPDATE reactor_details SET architect_engineer = 'Stone & Webster' WHERE reactor_id = 686 AND (architect_engineer IS NULL);  -- Yankee NPS 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Babcock & Wilcox' WHERE reactor_id = 686 AND (pressure_vessel_manufacturer IS NULL);  -- Yankee NPS 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 675 AND (constructor IS NULL);  -- Turkey Point 3
UPDATE reactors SET licensed_until = '2052' WHERE id = 675 AND (licensed_until = '2032');  -- Turkey Point 3
UPDATE reactors SET licensed_until = '2053' WHERE id = 676 AND (licensed_until = '2033');  -- Turkey Point 4
UPDATE reactor_details SET constructor = 'Westinghouse' WHERE reactor_id = 657 AND (constructor IS NULL);  -- Saxton 1
UPDATE reactor_details SET architect_engineer = 'Gilbert Associates' WHERE reactor_id = 657 AND (architect_engineer IS NULL);  -- Saxton 1
UPDATE reactors SET planned_retirement = NULL WHERE id = 567 AND (planned_retirement = '2028');  -- Byron 1
UPDATE reactors SET planned_retirement = NULL WHERE id = 568 AND (planned_retirement = '2028');  -- Byron 2
UPDATE reactor_details SET architect_engineer = 'Sargent & Lundy' WHERE reactor_id = 648 AND (architect_engineer IS NULL);  -- Quad Cities 2
UPDATE reactor_details SET constructor = 'Ebasco' WHERE reactor_id = 597 AND (constructor IS NULL);  -- Fort St. Vrain 1
UPDATE reactor_details SET architect_engineer = 'Sargent & Lundy' WHERE reactor_id = 597 AND (architect_engineer IS NULL);  -- Fort St. Vrain 1
UPDATE reactors SET design_series = 'BWR/4' WHERE id = 662 AND (design_series = 'BWR/5');  -- Shoreham 1
UPDATE reactors SET licensed_until = '2045' WHERE id = 36 AND (licensed_until IS NULL);  -- Darlington 1
UPDATE reactors SET licensed_until = '2045' WHERE id = 37 AND (licensed_until IS NULL);  -- Darlington 2
UPDATE reactors SET licensed_until = '2045' WHERE id = 38 AND (licensed_until IS NULL);  -- Darlington 3
UPDATE reactors SET licensed_until = '2045' WHERE id = 39 AND (licensed_until IS NULL);  -- Darlington 4
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 560 AND (containment_type IS NULL);  -- Braidwood 1
UPDATE reactor_details SET architect_engineer = 'Sargent & Lundy' WHERE reactor_id = 560 AND (architect_engineer IS NULL);  -- Braidwood 1
UPDATE reactor_details SET architect_engineer = 'Sargent & Lundy' WHERE reactor_id = 561 AND (architect_engineer IS NULL);  -- Braidwood 2
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Combustion Engineering' WHERE reactor_id = 618 AND (pressure_vessel_manufacturer IS NULL);  -- McGuire 1
UPDATE reactor_details SET pressure_vessel_manufacturer = 'Rotterdam Dockyard (RDM)' WHERE reactor_id = 619 AND (pressure_vessel_manufacturer IS NULL);  -- McGuire 2
UPDATE reactor_details SET constructor = 'Comision Federal de Electricidad' WHERE reactor_id = 338 AND (constructor = 'GE');  -- Laguna Verde 1
UPDATE reactor_details SET architect_engineer = 'Ebasco' WHERE reactor_id = 338 AND (architect_engineer IS NULL);  -- Laguna Verde 1
UPDATE reactors SET licensed_until = '2050' WHERE id = 338 AND (licensed_until IS NULL);  -- Laguna Verde 1
UPDATE reactor_details SET constructor = 'Comision Federal de Electricidad' WHERE reactor_id = 339 AND (constructor = 'GE');  -- Laguna Verde 2
UPDATE reactors SET licensed_until = '2055' WHERE id = 339 AND (licensed_until IS NULL);  -- Laguna Verde 2
UPDATE reactor_details SET architect_engineer = 'Pioneer Service & Engineering' WHERE reactor_id = 636 AND (architect_engineer IS NULL);  -- Pathfinder 1
UPDATE reactors SET licensed_until = '2062' WHERE id = 667 AND (licensed_until = '2042');  -- Summer (V C Summer) 1
UPDATE reactors SET planned_retirement = NULL WHERE id = 632 AND (planned_retirement = '2022');  -- Palisades 1
UPDATE reactors SET licensed_until = '2062' WHERE id = 680 AND (licensed_until = '2061');  -- Vogtle 3
UPDATE reactors SET licensed_until = '2063' WHERE id = 681 AND (licensed_until = '2062');  -- Vogtle 4
UPDATE reactors SET licensed_until = '2052' WHERE id = 668 AND (licensed_until = '2032');  -- Surry 1
UPDATE reactors SET licensed_until = '2053' WHERE id = 669 AND (licensed_until = '2033');  -- Surry 2
UPDATE reactors SET licensed_until = '2036' WHERE id = 683 AND (licensed_until = '2035');  -- Watts Bar 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 633 AND (constructor IS NULL);  -- Palo Verde 1
UPDATE reactors SET design_series = 'CE System 80' WHERE id = 633 AND (design_series = 'CE Pre-System 80');  -- Palo Verde 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 634 AND (constructor IS NULL);  -- Palo Verde 2
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 635 AND (constructor IS NULL);  -- Palo Verde 3
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 670 AND (constructor IS NULL);  -- Susquehanna 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 671 AND (constructor IS NULL);  -- Susquehanna 2
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 570 AND (architect_engineer IS NULL);  -- Calvert Cliffs 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 571 AND (constructor IS NULL);  -- Calvert Cliffs 2
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 571 AND (architect_engineer IS NULL);  -- Calvert Cliffs 2
UPDATE reactor_details SET constructor = 'Stone & Webster' WHERE reactor_id = 624 AND (constructor IS NULL);  -- Nine Mile Point 1
UPDATE reactor_details SET constructor = 'Stone & Webster' WHERE reactor_id = 625 AND (constructor IS NULL);  -- Nine Mile Point 2
UPDATE reactor_details SET architect_engineer = 'Stone & Webster' WHERE reactor_id = 625 AND (architect_engineer IS NULL);  -- Nine Mile Point 2
UPDATE reactor_details SET constructor = 'Stone & Webster' WHERE reactor_id = 595 AND (constructor IS NULL);  -- Fitzpatrick (James A. Fitzpatrick) 1
UPDATE reactors SET licensed_until = '2050' WHERE id = 651 AND (licensed_until = '2030');  -- Robinson (H B Robinson) 2
UPDATE reactor_details SET constructor = 'Stone & Webster' WHERE reactor_id = 617 AND (constructor IS NULL);  -- Maine Yankee 1
UPDATE reactor_details SET architect_engineer = 'Stone & Webster' WHERE reactor_id = 617 AND (architect_engineer IS NULL);  -- Maine Yankee 1
UPDATE reactors SET containment_type = 'Large Dry' WHERE id = 685 AND (containment_type IS NULL);  -- Wolf Creek 1
UPDATE reactor_details SET constructor = 'Bechtel' WHERE reactor_id = 606 AND (constructor IS NULL);  -- Hope Creek 1
UPDATE reactor_details SET architect_engineer = 'Bechtel' WHERE reactor_id = 606 AND (architect_engineer IS NULL);  -- Hope Creek 1
UPDATE reactor_details SET constructor = 'Stone & Webster' WHERE reactor_id = 650 AND (constructor IS NULL);  -- River Bend 1
UPDATE reactor_details SET architect_engineer = 'Stone & Webster' WHERE reactor_id = 650 AND (architect_engineer IS NULL);  -- River Bend 1
UPDATE reactors SET licensed_until = '2028' WHERE id = 28 AND (licensed_until IS NULL);  -- Bruce 1
UPDATE reactors SET licensed_until = '2028' WHERE id = 29 AND (licensed_until IS NULL);  -- Bruce 2
UPDATE reactors SET licensed_until = '2028' WHERE id = 30 AND (licensed_until IS NULL);  -- Bruce 3
UPDATE reactors SET licensed_until = '2028' WHERE id = 31 AND (licensed_until IS NULL);  -- Bruce 4
UPDATE reactors SET licensed_until = '2028' WHERE id = 32 AND (licensed_until IS NULL);  -- Bruce 5
UPDATE reactor_details SET constructor = 'Ontario Hydro' WHERE reactor_id = 33 AND (constructor IS NULL);  -- Bruce 6
UPDATE reactors SET licensed_until = '2028' WHERE id = 33 AND (licensed_until IS NULL);  -- Bruce 6
UPDATE reactor_details SET constructor = 'Ontario Hydro' WHERE reactor_id = 34 AND (constructor IS NULL);  -- Bruce 7
UPDATE reactors SET licensed_until = '2028' WHERE id = 34 AND (licensed_until IS NULL);  -- Bruce 7
UPDATE reactors SET licensed_until = '2028' WHERE id = 35 AND (licensed_until IS NULL);  -- Bruce 8
UPDATE reactors SET licensed_until = '2054' WHERE id = 604 AND (licensed_until = '2034');  -- Hatch (Edwin I. Hatch) 1
UPDATE reactors SET licensed_until = '2058' WHERE id = 605 AND (licensed_until = '2038');  -- Hatch (Edwin I. Hatch) 2
UPDATE reactor_details SET constructor = 'Brown & Root' WHERE reactor_id = 576 AND (constructor IS NULL);  -- Comanche Peak 1
UPDATE reactor_details SET architect_engineer = 'Gibbs & Hill' WHERE reactor_id = 576 AND (architect_engineer IS NULL);  -- Comanche Peak 1
UPDATE reactors SET licensed_until = '2050' WHERE id = 576 AND (licensed_until = '2030');  -- Comanche Peak 1
UPDATE reactors SET licensed_until = '2053' WHERE id = 577 AND (licensed_until = '2033');  -- Comanche Peak 2
COMMIT;
