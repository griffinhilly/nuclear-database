-- Migration 020: revert SNUPPS turbine speed (entity-collision error in 019)
-- 2026-07-22. DB series SNUPPS = Sizewell B ONLY (UK, 50 Hz grid).
-- 019 accepted a Wolf Creek USAR-sourced "correction" to 1800 rpm — Wolf Creek
-- is a real SNUPPS plant but NOT this series' member. 50 Hz wet-steam PWR
-- forces full-speed 3000 rpm (same deterministic grid-physics class as
-- migration 017's Jose Cabrera entry). Ledger: session 2026-07-22.
BEGIN TRANSACTION;
UPDATE design_series_specs SET turbine_speed_rpm = 3000,
  source = source || '; turbine speed reverted 2026-07-22 (entity-collision fix: series=Sizewell B, 50 Hz grid)'
  WHERE design_series = 'SNUPPS';
COMMIT;
