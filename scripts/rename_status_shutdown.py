# One-off: code-side of the 'Permanent Shutdown' -> 'Shutdown' status rename (Noah review,
# pairs with migration 007). Replaces the exact literal only (won't touch 'Long-term Shutdown').
# Scope: live app surface (app.py, database.py, templates/*.html). Historical one-off scripts
# (wna_*, status_audit, insert_*) are left as archival. Safe to delete after commit.
import glob, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD, NEW = "Permanent Shutdown", "Shutdown"

targets = [os.path.join(root, "app.py"), os.path.join(root, "database.py")]
targets += sorted(glob.glob(os.path.join(root, "templates", "*.html")))

total = 0
for path in targets:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    n = text.count(OLD)
    if n:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace(OLD, NEW))
        total += n
        print(f"  {os.path.relpath(path, root):40s} {n} replacement(s)")
print(f"TOTAL: {total} replacement(s) across {sum(1 for p in targets if True)} files scanned")

# sanity: confirm no 'Permanent Shutdown' remains in the live surface, and 'Long-term Shutdown' untouched
remain = sum(open(p, encoding="utf-8").read().count(OLD) for p in targets)
lt = sum(open(p, encoding="utf-8").read().count("Long-term Shutdown") for p in targets)
print(f"Remaining '{OLD}' in live surface: {remain}  (must be 0)")
print(f"'Long-term Shutdown' occurrences preserved: {lt}")
