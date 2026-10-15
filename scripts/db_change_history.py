"""Cell-level change history of nuclear_reactors.db across every git commit that touched it (+ working copy + pending drafts).

Purpose: one deterministic ledger of every data change ever made, for the change-history review page.
Inputs:  git history of nuclear_reactors.db; the working-tree DB; optional pending migrations applied to a copy
         (--pending migrations/036_phase2_wave3.sql ...).
Outputs: audit/change_history/cells.tsv     one row per changed cell / inserted row / deleted row
         audit/change_history/versions.tsv  one row per version (commit, date, subject, counts)
Method:  each version is diffed against the previous one table by table, keyed on a stable key
         (reactors.id, reactor_details.reactor_id, generation_annual (reactor_id, year), ...). Bookkeeping
         columns (created_at, updated_at, retrieved) are ignored. Each changed cell gets a kind
         (FILL / CLEAR / REPLACE / RESPELL) and a size bucket (see classify()).
last_run: 2026-10-15
"""
import argparse
import csv
import math
import shutil
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "audit" / "change_history"
DBNAME = "nuclear_reactors.db"

KEYS = {
    "reactors": ("id",),
    "reactor_details": ("reactor_id",),
    "generation_annual": ("reactor_id", "year"),
    "capacity_changes": ("reactor_id", "effective_date", "change_type"),
    "planned_reactors": ("id",),
    "models": ("id",),
    "design_series_specs": ("design_series",),
    "design_series_info": ("design_series",),
    "design_lineages": ("id",),
    "entity_descriptions": ("entity_type", "entity_name"),
    "external_series": ("series", "country_code", "year"),
    "suppliers": ("id",),
    "technologies": ("id",),
    "countries": ("id",),
}
IGNORE_COLS = {"created_at", "updated_at", "retrieved"}
COORD = {"latitude", "longitude"}
DATE_COLS = {"construction_start", "first_criticality", "grid_connection", "commercial_operation",
             "permanent_shutdown", "planned_retirement", "licensed_until", "suspended_since",
             "expected_operation", "effective_date", "expected_construction_start", "expected_online"}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout


def versions():
    log = git("log", "--reverse", "--first-parent", "--format=%h|%ad|%s", "--date=short", "--", DBNAME).decode("utf-8", "replace")
    return [tuple(line.split("|", 2)) for line in log.splitlines() if line]


def load(path):
    c = sqlite3.connect(path)
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    data = {}
    for t, key in KEYS.items():
        if t not in tables:
            continue
        cols = [r[1] for r in c.execute(f"PRAGMA table_info({t})")]
        if not all(k in cols for k in key):
            continue
        rows = {}
        for r in c.execute(f"SELECT * FROM {t}"):
            d = dict(zip(cols, r))
            rows[tuple(d[k] for k in key)] = d
        data[t] = rows
    labels = {}
    if "reactors" in data:
        for r in data["reactors"].values():
            labels[r["id"]] = f"{r.get('plant_name')} {r.get('unit_number') or ''}".strip()
    c.close()
    return data, labels


def num(v):
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


def year_frac(v):
    s = str(v)
    try:
        y = int(s[:4])
    except ValueError:
        return None
    m = int(s[5:7]) if len(s) >= 7 and s[5:7].isdigit() else 6
    d = int(s[8:10]) if len(s) >= 10 and s[8:10].isdigit() else 15
    return y + (m - 1) / 12 + (d - 1) / 365


def norm(v):
    return "".join(ch for ch in str(v).lower() if ch.isalnum())


def classify(col, old, new):
    """(kind, bucket). kind: FILL / CLEAR / REPLACE / RESPELL. bucket: a size label by field type."""
    if old in (None, "") and new not in (None, ""):
        return "FILL", "fill"
    if new in (None, "") and old not in (None, ""):
        return "CLEAR", "clear"
    if col == "status":
        return "REPLACE", "status"
    if col in COORD:
        a, b = num(old), num(new)
        if a is not None and b is not None:
            km = abs(a - b) * 111.0
            return "REPLACE", ("coord <1 km" if km < 1 else "coord 1-10 km" if km < 10 else "coord >10 km")
    if col in DATE_COLS:
        a, b = year_frac(old), year_frac(new)
        if a is not None and b is not None:
            dy = abs(a - b)
            if str(old)[:4] == str(new)[:4] and dy < 1 / 12 + 1e-9:
                return "REPLACE", "date <1 month"
            return "REPLACE", ("date <1 month" if dy < 1 / 12 else "date 1-12 months" if dy < 1
                               else "date 1-5 years" if dy < 5 else "date >5 years")
    a, b = num(old), num(new)
    if a is not None and b is not None and col != "unit_number":
        rel = abs(b - a) / abs(a) if a else float("inf")
        return "REPLACE", ("number <1%" if rel < 0.01 else "number 1-5%" if rel < 0.05
                           else "number 5-20%" if rel < 0.20 else "number >20%")
    if norm(old) == norm(new):
        return "RESPELL", "text respelling"
    return "REPLACE", "text replace"


def diff(prev, cur, plabels, clabels):
    out = []
    for t in sorted(set(prev) | set(cur)):
        a, b = prev.get(t, {}), cur.get(t, {})
        rid_of = (lambda k, row: row.get("id") if t == "reactors" else row.get("reactor_id"))
        for k in b.keys() - a.keys():
            row = b[k]; rid = rid_of(k, row)
            out.append((t, "|".join(map(str, k)), rid, clabels.get(rid, ""), "*", "", "", "INSERT", "row added"))
        for k in a.keys() - b.keys():
            row = a[k]; rid = rid_of(k, row)
            out.append((t, "|".join(map(str, k)), rid, plabels.get(rid, ""), "*", "", "", "DELETE", "row removed"))
        for k in a.keys() & b.keys():
            ra, rb = a[k], b[k]
            for col in rb:
                if col in IGNORE_COLS:
                    continue
                ov, nv = ra.get(col), rb[col]
                if ov == nv or (num(ov) is not None and num(ov) == num(nv)):
                    continue
                if (ov in (None, "")) and (nv in (None, "")):
                    continue
                kind, bucket = classify(col, ov, nv)
                rid = rid_of(k, rb)
                out.append((t, "|".join(map(str, k)), rid, clabels.get(rid, ""), col, ov, nv, kind, bucket))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pending", nargs="*", default=[], help="migration files to apply to a copy as the final 'pending' version")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "_tmp"; tmp.mkdir(exist_ok=True)
    vers = versions()
    seq = []
    for h, d, s in vers:
        p = tmp / f"{h}.db"
        if not p.exists():
            p.write_bytes(git("show", f"{h}:{DBNAME}"))
        seq.append((h, d, s, p))
    seq.append(("working", date.today().isoformat(), "Working copy (applied, not yet committed if different)", ROOT / DBNAME))
    if args.pending:
        p = tmp / "pending.db"
        shutil.copy(ROOT / DBNAME, p)
        c = sqlite3.connect(p)
        for m in args.pending:
            c.executescript(Path(m).read_text(encoding="utf-8"))
        c.commit(); c.close()
        seq.append(("pending", date.today().isoformat(), "Drafts not yet applied: " + ", ".join(Path(m).stem for m in args.pending), p))

    with open(OUT / "cells.tsv", "w", newline="", encoding="utf-8") as fc, open(OUT / "versions.tsv", "w", newline="", encoding="utf-8") as fv:
        wc = csv.writer(fc, delimiter="\t"); wv = csv.writer(fv, delimiter="\t")
        wc.writerow(["version", "date", "table", "key", "reactor_id", "unit", "field", "old", "new", "kind", "bucket"])
        wv.writerow(["version", "date", "subject", "cells", "inserts", "deletes", "reactor_cells"])
        prev, plabels = None, {}
        for h, d, s, p in seq:
            cur, clabels = load(p)
            if prev is None:
                wv.writerow([h, d, s + " [baseline]", 0, 0, 0, 0])
            else:
                rows = diff(prev, cur, plabels, clabels)
                for r in rows:
                    wc.writerow([h, d, *[("" if v is None else str(v).replace("\t", " ").replace("\n", " ")) for v in r]])
                wv.writerow([h, d, s, sum(r[7] not in ("INSERT", "DELETE") for r in rows),
                             sum(r[7] == "INSERT" for r in rows), sum(r[7] == "DELETE" for r in rows),
                             sum(r[0] in ("reactors", "reactor_details") and r[7] not in ("INSERT", "DELETE") for r in rows)])
                print(h, d, len(rows), s[:70], file=sys.stderr)
            prev, plabels = cur, clabels


if __name__ == "__main__":
    main()
