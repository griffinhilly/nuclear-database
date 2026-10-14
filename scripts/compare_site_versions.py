"""Before/after review of a release: every number the site serves, old code + old DB vs new code + new DB.

Purpose: before a deploy that changes data or derivation rules, list every displayed value that changes,
  ranked by size, so a human and fresh reviewers can sanity-check the biggest moves (2026-10-14 release:
  homepage rules, migrations 029-031).
Inputs:  --old-app (a copy of the deployed app.py, e.g. `git show HEAD:app.py > old_app.py`), --old-db,
         --new-app (default ./app.py), --new-db. Runs both through the Flask test client; no server.
Outputs: <out>/changes.tsv (endpoint, key path, old, new, delta, rel), <out>/endpoint_summary.tsv,
         <out>/reactor_field_changes.tsv (reactors table, field level), <out>/generation_country_year.tsv.
Usage:   python scripts/compare_site_versions.py --old-app OLD.py --old-db OLD.db --new-db NEW.db --out audit/change_review
last_run: 2026-10-14
"""
import argparse
import csv
import importlib.util
import os
import sqlite3
import sys
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ID_KEYS = ["year", "id", "reactor_id", "name", "country", "code", "iso_code", "status", "bracket", "decade",
           "technology", "plant_name", "unit_number", "series", "slug", "model", "owner", "supplier", "project_name"]


def load_app(path, db, name):
    os.environ["DATABASE_PATH"] = str(db)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT))
    spec.loader.exec_module(mod)
    mod.DB_PATH = Path(db)  # belt and braces: the module read the env var at import
    return mod


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = str(i)
            if isinstance(v, dict):
                ids = [f"{k}={v[k]}" for k in ID_KEYS if k in v and not isinstance(v[k], (dict, list))][:2]
                if ids:
                    key = ",".join(ids)
            out.update(flatten(v, f"{prefix}[{key}]"))
    else:
        out[prefix] = obj
    return out


def endpoints(db):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    q = lambda s: [r[0] for r in con.execute(s)]
    eps = ["/api/stats", "/api/stats/history", "/api/capacity/history", "/api/generation/annual",
           "/api/generation/decades", "/api/technologies", "/api/countries", "/api/reactors/count",
           "/api/reactors/age-distribution", "/api/construction-map", "/api/lineages", "/api/containment/overview"]
    for c in q("SELECT DISTINCT c.name FROM countries c JOIN reactors r ON r.country_id = c.id"):
        eps += [f"/api/countries/{quote(c)}/detail", f"/api/capacity/history?country={quote(c)}"]
    for t in q("SELECT DISTINCT t.code FROM technologies t JOIN reactors r ON r.technology_id = t.id"):
        eps += [f"/api/technologies/{quote(t)}/detail", f"/api/capacity/history?technology={quote(t)}"]
    for s in q("SELECT DISTINCT status FROM reactors"):
        eps.append(f"/api/statuses/{quote(s)}/detail")
    for s in q("SELECT DISTINCT s.name FROM suppliers s JOIN reactors r ON r.supplier_id = s.id"):
        eps.append(f"/api/suppliers/{quote(s)}/detail")
    for o in q("SELECT DISTINCT owner FROM reactors WHERE owner IS NOT NULL"):
        eps.append(f"/api/owners/{quote(o, safe='/')}/detail")
    for p in q("SELECT DISTINCT plant_name FROM reactors"):
        eps.append(f"/api/plants/{quote(p)}")
    for i in q("SELECT id FROM reactors"):
        eps.append(f"/api/reactors/{i}")
    return eps


def fetch_all(mod, eps):
    c = mod.app.test_client()
    paid = next(k for k, v in mod.VALID_API_KEYS.items() if v.get("tier") == "paid")
    res = {}
    for e in eps:
        sep = "&" if "?" in e else "?"
        r = c.get(f"{e}{sep}api_key={paid}")
        res[e] = flatten(r.get_json()) if r.status_code == 200 and r.is_json else {"__status__": r.status_code}
    return res


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-app", required=True)
    ap.add_argument("--old-db", required=True)
    ap.add_argument("--new-app", default=str(ROOT / "app.py"))
    ap.add_argument("--new-db", required=True)
    ap.add_argument("--out", default=str(ROOT / "audit" / "change_review"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    eps = sorted(set(endpoints(a.old_db)) | set(endpoints(a.new_db)))
    old = fetch_all(load_app(a.old_app, a.old_db, "site_old"), eps)
    new = fetch_all(load_app(a.new_app, a.new_db, "site_new"), eps)

    rows, summary = [], []
    for e in eps:
        o, n = old.get(e, {}), new.get(e, {})
        changed = 0
        for k in sorted(set(o) | set(n)):
            ov, nv = o.get(k, "<absent>"), n.get(k, "<absent>")
            if ov == nv:
                continue
            if k.endswith(("updated_at", "applied_at")) or k in ("data_coverage.last_updated",):
                continue
            changed += 1
            if num(ov) and num(nv):
                d = nv - ov
                rel = d / abs(ov) if ov else None
            else:
                d, rel = None, None
            rows.append([e, k, ov, nv, d, rel])
        summary.append([e, len(o), len(n), changed])
    with open(out / "changes.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["endpoint", "path", "old", "new", "delta", "rel"])
        w.writerows(rows)
    with open(out / "endpoint_summary.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["endpoint", "old_values", "new_values", "changed"])
        w.writerows(summary)

    # Database-level: reactors field changes and generation by country-year.
    od = sqlite3.connect(f"file:{a.old_db}?mode=ro", uri=True)
    nd = sqlite3.connect(f"file:{a.new_db}?mode=ro", uri=True)
    cols = [r[1] for r in od.execute("PRAGMA table_info(reactors)") if r[1] not in ("updated_at",)]
    ov = {r[0]: r for r in od.execute(f"SELECT {', '.join(cols)} FROM reactors")}
    nv = {r[0]: r for r in nd.execute(f"SELECT {', '.join(cols)} FROM reactors")}
    with open(out / "reactor_field_changes.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["reactor_id", "reactor", "field", "old", "new"])
        for rid in sorted(set(ov) | set(nv)):
            o, n = ov.get(rid), nv.get(rid)
            if not o or not n:
                w.writerow([rid, (o or n)[1], "<row>", "present" if o else "absent", "present" if n else "absent"])
                continue
            for i, c in enumerate(cols):
                if o[i] != n[i]:
                    w.writerow([rid, f"{n[1]} {n[2]}", c, o[i], n[i]])
    gq = """SELECT c.name, g.year, SUM(g.electricity_gwh) / 1000.0 FROM generation_annual g
            JOIN reactors r ON r.id = g.reactor_id JOIN countries c ON c.id = r.country_id GROUP BY c.name, g.year"""
    og = {(r[0], r[1]): r[2] for r in od.execute(gq)}
    ng = {(r[0], r[1]): r[2] for r in nd.execute(gq)}
    with open(out / "generation_country_year.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["country", "year", "old_twh", "new_twh", "delta_twh"])
        for k in sorted(set(og) | set(ng)):
            o, n = og.get(k, 0) or 0, ng.get(k, 0) or 0
            if abs(n - o) > 0.05:
                w.writerow([k[0], k[1], round(o, 2), round(n, 2), round(n - o, 2)])
    print(f"{len(eps)} endpoints; {len(rows)} changed values; outputs in {out}")


if __name__ == "__main__":
    main()
