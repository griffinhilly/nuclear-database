"""Run numbered SQL migrations against nuclear_reactors.db.

Usage:
  python migrations/run.py              # Run all migrations
  python migrations/run.py 005          # Run specific migration
  python migrations/run.py --status     # Show which migrations have been applied
  python migrations/run.py --dry-run    # Show what would be run without applying
"""
import sqlite3
import sys
import os
import glob
import argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MIGRATIONS_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(MIGRATIONS_DIR), "nuclear_reactors.db")


def ensure_tracking_table(conn):
    """Create migrations tracking table if it doesn't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def get_applied(conn):
    """Return set of already-applied migration filenames."""
    try:
        rows = conn.execute("SELECT filename FROM _migrations ORDER BY filename").fetchall()
        return {r[0] for r in rows}
    except sqlite3.OperationalError:
        return set()


def get_migrations():
    """Return sorted list of (filename, path) for all .sql files in migrations dir."""
    pattern = os.path.join(MIGRATIONS_DIR, "[0-9]*.sql")
    files = glob.glob(pattern)
    return sorted([(os.path.basename(f), f) for f in files])


def run_migration(conn, filename, filepath, dry_run=False):
    """Execute a single migration file."""
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()

    if dry_run:
        print(f"  [DRY RUN] Would apply: {filename}")
        return

    print(f"  Applying: {filename} ... ", end="")
    try:
        conn.executescript(sql)
        conn.execute("INSERT INTO _migrations (filename) VALUES (?)", (filename,))
        conn.commit()
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")
        conn.rollback()
        raise


def main():
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument("migration", nargs="?", help="Specific migration number to run (e.g., '005')")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run without applying")
    parser.add_argument("--db", default=DB_PATH, help="Database path")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    ensure_tracking_table(conn)
    applied = get_applied(conn)
    migrations = get_migrations()

    if args.status:
        print(f"Migrations directory: {MIGRATIONS_DIR}")
        print(f"Database: {args.db}")
        print()
        for filename, _ in migrations:
            status = "APPLIED" if filename in applied else "PENDING"
            print(f"  [{status}] {filename}")
        pending = len([f for f, _ in migrations if f not in applied])
        print(f"\n{len(applied)} applied, {pending} pending")
        conn.close()
        return 0

    if args.migration:
        # Run specific migration
        matches = [(f, p) for f, p in migrations if f.startswith(args.migration)]
        if not matches:
            print(f"No migration found matching '{args.migration}'")
            conn.close()
            return 1
        filename, filepath = matches[0]
        if filename in applied and not args.dry_run:
            print(f"  {filename} already applied. Use --dry-run to preview.")
            conn.close()
            return 0
        run_migration(conn, filename, filepath, args.dry_run)
    else:
        # Run all pending
        pending = [(f, p) for f, p in migrations if f not in applied]
        if not pending:
            print("All migrations already applied.")
            conn.close()
            return 0
        print(f"Running {len(pending)} pending migration(s):")
        for filename, filepath in pending:
            run_migration(conn, filename, filepath, args.dry_run)

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
