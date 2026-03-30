# Database Migrations

Numbered SQL migration files for tracking all database schema and data changes.

## Convention

- Files named `NNN_description.sql` (e.g., `001_capacity_alignment.sql`)
- Each file is idempotent where possible (use INSERT OR IGNORE, UPDATE WHERE)
- Header comment includes: date, description, affected tables, row count
- Run with: `python migrations/run.py` or `python migrations/run.py 005` (specific migration)

## When to create a migration

- Any bulk UPDATE/INSERT/DELETE affecting >5 rows
- Schema changes (ALTER TABLE, CREATE TABLE)
- Data corrections from audits or external sources

## Replay after merge conflicts

When `nuclear_reactors.db` has a binary merge conflict:
1. Take the remote DB version (which has any new tables/schema)
2. Run `python migrations/run.py` to replay all data migrations
3. Verify with `python scripts/validate_db.py`
