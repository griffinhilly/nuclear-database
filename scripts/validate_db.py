"""Post-update database validation script.

Run after any bulk data change to verify internal consistency.
Usage: python scripts/validate_db.py [--fix-whitespace]

Checks:
  1. Capacity alignment: net_capacity_mw vs reference_power_mw
  2. Capacity changes consistency: latest cc record vs reactor net_capacity
  3. Whitespace in key text columns
  4. Orphan foreign keys
  5. Null checks on required fields
"""
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
