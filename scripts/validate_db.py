"""Post-update database validation script.

Run after any bulk data change to verify internal consistency.
Usage: python scripts/validate_db.py [--fix-whitespace]

Checks:
  1. Capacity alignment: net_capacity_mw vs reference_power_mw
  2. Capacity changes consistency: latest cc record vs reactor net_capacity
  3. Whitespace in key text columns
  4. Orphan foreign keys
  5. Null checks on required fields
  6. Status enum (canonical status set; catches drift / the Shutdown rename)
  7. Model-name artifacts: numeric-only names (e.g. leaked PRIS reactor-type codes)
  8. VVER series specificity (advisory, non-blocking)
  9. Cooling-type NULLs on non-Shutdown reactors (advisory, non-blocking)
 10. Cooling-type enum (all non-NULL values in the 6-value set)
 11. Uniform cooling across 4+ unit plants (advisory review candidates, non-blocking)
"""
import os
import sqlite3
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    parser = argparse.ArgumentParser(description="Validate nuclear_reactors.db consistency")
    parser.add_argument("--fix-whitespace", action="store_true", help="Auto-fix whitespace issues")
    parser.add_argument("--db", default="nuclear_reactors.db", help="Database path")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    issues = 0

    # 1. Capacity alignment: net vs ref
    print("=" * 60)
    print("1. CAPACITY ALIGNMENT (net_capacity_mw vs reference_power_mw)")
    print("=" * 60)
    rows = conn.execute("""
        SELECT r.id, r.plant_name, r.unit_number, r.net_capacity_mw, r.reference_power_mw,
               r.status, (r.reference_power_mw - r.net_capacity_mw) as diff
        FROM reactors r
        WHERE r.reference_power_mw IS NOT NULL AND r.net_capacity_mw IS NOT NULL
        AND ABS(r.reference_power_mw - r.net_capacity_mw) > 5
        ORDER BY ABS(r.reference_power_mw - r.net_capacity_mw) DESC
    """).fetchall()
    if rows:
        print(f"  FAIL: {len(rows)} reactors with >5 MWe gap")
        for r in rows:
            print(f"    id={r['id']:4d} | {r['plant_name']} {r['unit_number']} | "
                  f"net={r['net_capacity_mw']:.0f} | ref={r['reference_power_mw']:.0f} | "
                  f"diff={r['diff']:+.0f} | {r['status']}")
        issues += len(rows)
    else:
        print("  OK: All reactors aligned (0 gaps > 5 MWe)")

    # 2. Capacity changes consistency
    print()
    print("=" * 60)
    print("2. CAPACITY CHANGES vs REACTOR NET CAPACITY")
    print("=" * 60)
    rows = conn.execute("""
        SELECT r.id, r.plant_name, r.unit_number, r.net_capacity_mw,
               cc.net_capacity_mw as cc_net, cc.effective_date
        FROM reactors r
        JOIN capacity_changes cc ON cc.reactor_id = r.id
        WHERE cc.effective_date = (
            SELECT MAX(cc2.effective_date) FROM capacity_changes cc2
            WHERE cc2.reactor_id = r.id
        )
        AND ABS(cc.net_capacity_mw - r.net_capacity_mw) > 1
        ORDER BY ABS(cc.net_capacity_mw - r.net_capacity_mw) DESC
    """).fetchall()
    if rows:
        print(f"  WARN: {len(rows)} reactors where latest cc != net_capacity")
        for r in rows:
            diff = r['cc_net'] - r['net_capacity_mw']
            print(f"    id={r['id']:4d} | {r['plant_name']} {r['unit_number']} | "
                  f"net={r['net_capacity_mw']:.0f} | cc_latest={r['cc_net']:.0f} ({diff:+.0f}) | "
                  f"date={r['effective_date']}")
        issues += len(rows)
    else:
        print("  OK: All capacity_changes records consistent with reactor net_capacity")

    # 3. Whitespace issues
    print()
    print("=" * 60)
    print("3. WHITESPACE IN TEXT COLUMNS")
    print("=" * 60)
    checks = [
        ("models", "name", "id"),
        ("reactors", "plant_name", "id"),
        ("reactors", "design_series", "id"),
        ("reactors", "owner", "id"),
        ("suppliers", "name", "id"),
        ("countries", "name", "id"),
    ]
    ws_found = False
    for table, col, pk in checks:
        rows = conn.execute(
            f"SELECT {pk}, {col} FROM {table} WHERE {col} IS NOT NULL AND {col} != TRIM({col})"
        ).fetchall()
        if rows:
            ws_found = True
            print(f"  FAIL: {table}.{col} — {len(rows)} rows with whitespace")
            for r in rows:
                print(f"    {pk}={r[0]} | \"{r[1]}\"")
            if args.fix_whitespace:
                conn.execute(f"UPDATE {table} SET {col} = TRIM({col}) WHERE {col} != TRIM({col})")
                print(f"    -> Fixed (trimmed)")
            issues += len(rows)
    if not ws_found:
        print("  OK: No whitespace issues")

    # 4. Orphan foreign keys
    print()
    print("=" * 60)
    print("4. ORPHAN FOREIGN KEYS")
    print("=" * 60)
    fk_checks = [
        ("reactors", "model_id", "models", "id"),
        ("reactors", "country_id", "countries", "id"),
        ("reactors", "technology_id", "technologies", "id"),
        ("reactors", "supplier_id", "suppliers", "id"),
        ("capacity_changes", "reactor_id", "reactors", "id"),
    ]
    orphans_found = False
    for child_table, child_col, parent_table, parent_col in fk_checks:
        count = conn.execute(f"""
            SELECT COUNT(*) FROM {child_table} c
            WHERE c.{child_col} IS NOT NULL
            AND c.{child_col} NOT IN (SELECT {parent_col} FROM {parent_table})
        """).fetchone()[0]
        if count > 0:
            orphans_found = True
            print(f"  FAIL: {child_table}.{child_col} has {count} orphan references")
            issues += count
    if not orphans_found:
        print("  OK: No orphan foreign keys")

    # 5. Required fields null check
    print()
    print("=" * 60)
    print("5. REQUIRED FIELDS NULL CHECK")
    print("=" * 60)
    null_checks = [
        ("reactors", "plant_name"),
        ("reactors", "status"),
        ("reactors", "country_id"),
        ("reactors", "technology_id"),
        ("reactors", "net_capacity_mw"),
        ("reactors", "latitude"),
        ("reactors", "longitude"),
        ("reactors", "design_series"),
    ]
    nulls_found = False
    for table, col in null_checks:
        count = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL"
        ).fetchone()[0]
        if count > 0:
            nulls_found = True
            print(f"  WARN: {table}.{col} has {count} NULL values")
            issues += count
    if not nulls_found:
        print("  OK: All required fields populated")

    # 6. Status enum (locks in the "Shutdown" rename; catches status drift)
    print()
    print("=" * 60)
    print("6. STATUS ENUM")
    print("=" * 60)
    allowed_status = ("Operational", "Under Construction", "Suspended", "Shutdown")
    rows = conn.execute(
        f"SELECT id, plant_name, unit_number, status FROM reactors "
        f"WHERE status NOT IN ({','.join('?' * len(allowed_status))})",
        allowed_status,
    ).fetchall()
    if rows:
        print(f"  FAIL: {len(rows)} reactor(s) with unexpected status value")
        for r in rows:
            print(f"    id={r['id']} | {r['plant_name']} {r['unit_number']} | status='{r['status']}'")
        issues += len(rows)
    else:
        print(f"  OK: all reactor statuses in {allowed_status}")

    # 7. Model-name artifacts (R2): numeric-only names = leaked PRIS reactor-type codes (e.g. "25")
    print()
    print("=" * 60)
    print("7. MODEL-NAME ARTIFACTS (numeric-only model names)")
    print("=" * 60)
    rows = conn.execute(
        "SELECT id, name FROM models WHERE name GLOB '*[0-9]*' AND NOT name GLOB '*[A-Za-z]*'"
    ).fetchall()
    if rows:
        print(f"  FAIL: {len(rows)} model(s) with numeric-only names (likely PRIS type-code leak)")
        for r in rows:
            print(f"    model id={r['id']} | name=\"{r['name']}\"")
        issues += len(rows)
    else:
        print("  OK: no numeric-only model names")

    # 8. VVER series specificity (R3) — ADVISORY, does not increment `issues`
    print()
    print("=" * 60)
    print("8. VVER SERIES SPECIFICITY (advisory — non-blocking)")
    print("=" * 60)
    rows = conn.execute(
        "SELECT plant_name, unit_number, design_series FROM reactors "
        "WHERE design_series IN ('VVER-1200', 'VVER-1000', 'VVER-440') "
        "ORDER BY plant_name, unit_number"
    ).fetchall()
    if rows:
        print(f"  ADVISORY: {len(rows)} VVER reactor(s) with a generic series (no V-xxx project suffix):")
        for r in rows:
            print(f"    {r['plant_name']} {r['unit_number']} | series='{r['design_series']}'")
        print("  (review candidates — assign a specific V-code where known; NOT counted as blocking)")
    else:
        print("  OK: no generic VVER series in reactors")

    # 9. Cooling-type NULLs on non-Shutdown reactors (R4) — ADVISORY, does not increment issues
    print()
    print("=" * 60)
    print("9. COOLING-TYPE NULLs (non-Shutdown reactors) — advisory, non-blocking")
    print("=" * 60)
    rows = conn.execute(
        "SELECT r.plant_name, r.unit_number, r.status "
        "FROM reactors r "
        "LEFT JOIN reactor_details rd ON rd.reactor_id = r.id "
        "WHERE r.status != 'Shutdown' "
        "AND (rd.cooling_type IS NULL OR rd.reactor_id IS NULL) "
        "ORDER BY r.plant_name, r.unit_number"
    ).fetchall()
    if rows:
        print(f"  ADVISORY: {len(rows)} non-Shutdown reactor(s) with no cooling_type:")
        for r in rows:
            print(f"    {r['plant_name']} {r['unit_number']} | status={r['status']}")
        print("  (fill where a reliable source exists; NOT counted as blocking)")
    else:
        print("  OK: all non-Shutdown reactors have a cooling_type")

    # 10. Cooling-type enum (R5) — HARD check
    print()
    print("=" * 60)
    print("10. COOLING-TYPE ENUM")
    print("=" * 60)
    allowed_cooling = (
        'Once-through (seawater)', 'Once-through (river)', 'Once-through (lake)',
        'Cooling tower (natural draft)', 'Cooling tower (mechanical draft)', 'Cooling pond',
    )
    rows = conn.execute(
        f"SELECT rd.reactor_id, r.plant_name, r.unit_number, rd.cooling_type "
        f"FROM reactor_details rd JOIN reactors r ON r.id = rd.reactor_id "
        f"WHERE rd.cooling_type IS NOT NULL "
        f"AND rd.cooling_type NOT IN ({','.join('?' * len(allowed_cooling))})",
        allowed_cooling,
    ).fetchall()
    if rows:
        print(f"  FAIL: {len(rows)} reactor(s) with cooling_type outside the 6-value enum")
        for r in rows:
            print(f"    id={r['reactor_id']} | {r['plant_name']} {r['unit_number']} | "
                  f"cooling_type='{r['cooling_type']}'")
        issues += len(rows)
    else:
        print("  OK: all non-NULL cooling_type values are in the 6-value enum")

    # 11. Uniform cooling across 4+ unit plants (R6) — ADVISORY, does not increment issues
    print()
    print("=" * 60)
    print("11. UNIFORM COOLING ACROSS 4+ UNIT PLANTS — advisory, non-blocking")
    print("=" * 60)
    rows = conn.execute(
        "SELECT r.plant_name, COUNT(*) AS n_units, MIN(rd.cooling_type) AS ct "
        "FROM reactors r JOIN reactor_details rd ON rd.reactor_id = r.id "
        "WHERE rd.cooling_type IS NOT NULL "
        "GROUP BY r.plant_name "
        "HAVING COUNT(*) >= 4 AND COUNT(DISTINCT rd.cooling_type) = 1 "
        "ORDER BY r.plant_name"
    ).fetchall()
    if rows:
        print(f"  ADVISORY: {len(rows)} plant(s) with 4+ units all sharing one cooling_type "
              "(the original per-plant bug looked like this — confirm uniformity is real):")
        for r in rows:
            print(f"    {r['plant_name']} | {r['n_units']} units | all '{r['ct']}'")
        print("  (per-unit variation is common; NOT counted as blocking)")
    else:
        print("  OK: no 4+ unit plants with fully uniform cooling_type")

    # 12. Duplicate pris_id — HARD check (a shared id makes pris_id-keyed
    # backfills write one reactor's output onto another)
    print()
    print("=" * 60)
    print("12. DUPLICATE PRIS IDs")
    print("=" * 60)
    rows = conn.execute(
        "SELECT pris_id, COUNT(*) AS n, "
        "GROUP_CONCAT(plant_name || ' ' || unit_number, ' / ') AS members "
        "FROM reactors WHERE pris_id IS NOT NULL "
        "GROUP BY pris_id HAVING COUNT(*) > 1 ORDER BY pris_id"
    ).fetchall()
    if rows:
        print(f"  FAIL: {len(rows)} pris_id value(s) shared by multiple reactors:")
        for r in rows:
            print(f"    pris_id={r['pris_id']}: {r['members']}")
        issues += len(rows)
    else:
        print("  OK: all pris_id values unique")

    # 13. Generation after permanent shutdown — HARD check
    print()
    print("=" * 60)
    print("13. GENERATION ROWS AFTER PERMANENT SHUTDOWN")
    print("=" * 60)
    rows = conn.execute(
        "SELECT r.plant_name, r.unit_number, r.permanent_shutdown, g.year, g.electricity_gwh "
        "FROM generation_annual g JOIN reactors r ON g.reactor_id = r.id "
        "WHERE r.status = 'Shutdown' AND r.permanent_shutdown IS NOT NULL "
        "AND g.year > CAST(strftime('%Y', r.permanent_shutdown) AS INTEGER) "
        "ORDER BY r.plant_name, g.year"
    ).fetchall()
    if rows:
        print(f"  FAIL: {len(rows)} generation row(s) dated after the reactor's shutdown year:")
        for r in rows:
            print(f"    {r['plant_name']} {r['unit_number']} (shut {r['permanent_shutdown']}) "
                  f"| {r['year']}: {r['electricity_gwh']} GWh")
        issues += len(rows)
    else:
        print("  OK: no generation rows after permanent shutdown")

    # 14. Impossible capacity factors — HARD check. Mirrors the public
    # /api/data/validation anomaly query (historical GROSS capacity via
    # capacity_changes, >105%): the site's own anomaly surface must be empty.
    print()
    print("=" * 60)
    print("14. IMPOSSIBLE CAPACITY FACTORS (>105% vs historical gross)")
    print("=" * 60)
    rows = conn.execute(
        "SELECT r.plant_name, r.unit_number, g.year, g.electricity_gwh, "
        "COALESCE((SELECT cc.gross_capacity_mw FROM capacity_changes cc "
        "          WHERE cc.reactor_id = r.id AND cc.effective_date <= g.year || '-12-31' "
        "          ORDER BY cc.effective_date DESC LIMIT 1), "
        "         r.gross_capacity_mw) AS eff_mw "
        "FROM generation_annual g JOIN reactors r ON g.reactor_id = r.id "
        "WHERE r.gross_capacity_mw > 0 AND eff_mw > 0 "
        "AND g.electricity_gwh * 1000.0 / (eff_mw * 8760) > 1.05 "
        "ORDER BY g.electricity_gwh * 1000.0 / (eff_mw * 8760) DESC"
    ).fetchall()
    if rows:
        print(f"  FAIL: {len(rows)} generation row(s) exceed 105% CF vs historical gross "
              "(these render on the public validation endpoint):")
        for r in rows:
            cf = r["electricity_gwh"] * 1000.0 / (r["eff_mw"] * 8760)
            print(f"    {r['plant_name']} {r['unit_number']} | {r['year']}: "
                  f"{r['electricity_gwh']} GWh vs {r['eff_mw']} MW -> CF {cf:.0%}")
        issues += len(rows)
    else:
        print("  OK: no generation rows above 105% CF vs historical gross capacity")

    # 15. Vendor-field drift guard (constants audit 2026-07): every non-NULL
    # supply-chain value in reactor_details must appear as a visible verdict in
    # verification_2026-07/final_verdicts.psv. A hit means some session wrote
    # an unattested value back into a verified field. When Noah/Dirk attest new
    # values, append them to final_verdicts.psv (visible=yes) in the same change.
    print()
    print("=" * 60)
    print("15. VENDOR-FIELD DRIFT GUARD (unattested values in reactor_details)")
    print("=" * 60)
    verdicts_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "verification_2026-07", "final_verdicts.psv")
    if not os.path.exists(verdicts_path):
        print(f"  FAIL: whitelist file missing: {verdicts_path}")
        issues += 1
    else:
        whitelist = set()
        with open(verdicts_path, encoding="utf-8") as vf:
            for ln in vf:
                p = ln.rstrip("\n").split("|")
                if len(p) >= 7 and p[6] == "yes":
                    whitelist.add((int(p[0]), p[3]))
        colmap = {"constructor": "constructor", "architect_engineer": "architect_engineer",
                  "turbine_supplier": "turbine_supplier",
                  "rpv_manufacturer": "pressure_vessel_manufacturer"}
        drift = []
        for field, col in colmap.items():
            for r in conn.execute(
                    f"SELECT d.reactor_id, r.plant_name, r.unit_number, d.{col} AS val "
                    f"FROM reactor_details d JOIN reactors r ON r.id = d.reactor_id "
                    f"WHERE d.{col} IS NOT NULL"):
                if (r["reactor_id"], field) not in whitelist:
                    drift.append((r["plant_name"], r["unit_number"], field, r["val"]))
        if drift:
            print(f"  FAIL: {len(drift)} unattested vendor value(s) present:")
            for plant, unit, field, val in drift[:20]:
                print(f"    {plant} {unit} | {field} = {val}")
            issues += len(drift)
        else:
            print("  OK: all non-NULL vendor fields are attested in final_verdicts.psv")

    # Summary
    print()
    print("=" * 60)
    if issues == 0:
        print("VALIDATION PASSED — 0 issues found")
    else:
        print(f"VALIDATION FOUND {issues} ISSUE(S)")
    print("=" * 60)

    if args.fix_whitespace:
        conn.commit()
    conn.close()
    return 1 if issues > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
