#!/usr/bin/env python3
"""
purpose: Merge + validate design-spec verification batches (specs_01-10) into a
         single verdict file and draft migration 019.
inputs:  spec_inputs/specs_NN.psv (claims), spec_results/specs_NN.psv (verdicts)
outputs: spec_final_verdicts.psv, migration draft printed to stdout (NOT written
         to migrations/ -- reviewed first), taint report on stderr
last_run: 2026-07-22
Zero-doubt policy: CONFIRMED HIGH/MED stay visible; WRONG with sourced
corrected_value -> UPDATE; UNVERIFIABLE/BLOCKED/LOW -> NULL the DB value.
Taint screen: any result row whose source matches memory-tell phrases fails the
whole batch (provenance rule 7, CLAUDE.md Data Change Protocol).
"""
import csv, glob, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = {"CONFIRMED", "WRONG", "UNVERIFIABLE", "BLOCKED"}
# Memory-tell phrases: self-attestation instead of retrieval (Jul 21 taint pattern)
MEMORY_TELLS = re.compile(
    r"widely documented|commonly cited|standard for|well[- ]known|typical(ly)?"
    r"|design class definition|general knowledge|industry standard",
    re.I,
)
# A named retrieval anywhere in the source clears the tell (2026-07-22 review:
# tells are only damning when they REPLACE a named document, not describe one)
NAMED_SOURCE = re.compile(
    r"\.(org|com|gov|int|edu|net|de|fr|ru|hu)\b|NRC|IAEA|MDEP|OECD|INIS|OSTI"
    r"|USAR|FSAR|Wikipedia|WNA|PRIS|ARIS|TR-|ResearchGate|Springer|PNNL",
    re.I,
)

def is_taint(row):
    return (row["verdict"] in ("CONFIRMED", "WRONG")
            and MEMORY_TELLS.search(row.get("source", ""))
            and not NAMED_SOURCE.search(row.get("source", "")))

def read_psv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="|"))

# 60 Hz nuclear countries (all others in the DB are 50 Hz; Japan is mixed by zone)
HZ60 = {"USA", "Canada", "Mexico", "Brazil", "South Korea", "Taiwan"}

def series_identity(dbpath=None):
    """design_series -> (plants, countries). The identity map every entity
    check runs against — a correction sourced to a plant outside this list,
    or a grid-dependent value inconsistent with these countries, is rejected.
    Added 2026-07-22 after the SNUPPS collision (series=Sizewell B, but a
    Wolf Creek-sourced 'correction' was accepted)."""
    import sqlite3
    db = sqlite3.connect(dbpath or os.path.join(HERE, "..", "nuclear_reactors.db"))
    ident = {}
    for s, p, c in db.execute(
        "SELECT r.design_series, r.plant_name, co.name FROM reactors r "
        "JOIN countries co ON r.country_id = co.id WHERE r.design_series IS NOT NULL"):
        ident.setdefault(s, (set(), set()))
        ident[s][0].add(p); ident[s][1].add(c)
    return ident

def entity_violations(updates, ident):
    """Deterministic entity checks on proposed corrections."""
    bad = []
    for (series, field), val, src in updates:
        plants, countries = ident.get(series, (set(), set()))
        if field == "turbine_speed_rpm" and val.strip() in ("1500", "1800", "3000", "3600"):
            rpm = int(val)
            japan_mixed = countries == {"Japan"}
            if not japan_mixed:
                is60 = countries <= HZ60
                is50 = not (countries & HZ60)
                if is60 and rpm in (1500, 3000):
                    bad.append(f"{series}/{field}={rpm}: 50Hz value but series countries {sorted(countries)} are 60Hz")
                if is50 and rpm in (1800, 3600):
                    bad.append(f"{series}/{field}={rpm}: 60Hz value but series countries {sorted(countries)} are 50Hz")
        # source names a plant that is not a member of this series
        for other_series, (op, oc) in ident.items():
            if other_series == series: continue
            for plant in op - plants:
                if len(plant) > 5 and plant.lower() in src.lower():
                    bad.append(f"{series}/{field}: source cites '{plant}' which belongs to series {other_series}, not {series}")
                    break
    return bad

def main():
    problems, all_rows, batch_stats = [], [], {}
    inputs = sorted(glob.glob(os.path.join(HERE, "spec_inputs", "specs_*.psv")))
    for inp in inputs:
        nn = os.path.basename(inp)
        res = os.path.join(HERE, "spec_results", nn)
        if not os.path.exists(res):
            problems.append(f"{nn}: MISSING result file")
            continue
        claims = read_psv(inp)
        rows = read_psv(res)
        claimed_series = {c["design_series"] for c in claims}
        got_series = {r["design_series"] for r in rows}
        missing = claimed_series - got_series
        if missing:
            problems.append(f"{nn}: no verdicts for series {sorted(missing)}")
        tainted = [r for r in rows if is_taint(r)]
        if tainted:
            problems.append(
                f"{nn}: TAINT — {len(tainted)} rows with memory-tell sources "
                f"(e.g. {tainted[0]['design_series']}/{tainted[0]['field']}: "
                f"'{tainted[0]['source'][:60]}') — batch quarantined"
            )
            continue
        bad_v = [r for r in rows if r["verdict"] not in VERDICTS]
        if bad_v:
            problems.append(f"{nn}: invalid verdicts {sorted({r['verdict'] for r in bad_v})}")
            continue
        wrong_unsourced = [
            r for r in rows
            if r["verdict"] == "WRONG" and not (r["corrected_value"].strip() and r["source"].strip())
        ]
        if wrong_unsourced:
            problems.append(f"{nn}: {len(wrong_unsourced)} WRONG rows lack corrected_value/source")
            continue
        for r in rows:
            r["batch"] = nn
        all_rows.extend(rows)
        c = {v: sum(1 for r in rows if r["verdict"] == v) for v in VERDICTS}
        batch_stats[nn] = c

    print("=== BATCH STATS ===")
    for nn, c in batch_stats.items():
        total = sum(c.values())
        print(f"{nn}: {total:4d} rows | " + " ".join(f"{v}={c[v]}" for v in
              ("CONFIRMED", "WRONG", "UNVERIFIABLE", "BLOCKED")))
    if problems:
        print("\n=== PROBLEMS (fix before merge) ===", file=sys.stderr)
        for p in problems:
            print(" -", p, file=sys.stderr)
        sys.exit(1)

    out = os.path.join(HERE, "spec_final_verdicts.psv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=["design_series", "field", "verdict", "corrected_value",
                           "confidence", "source", "batch"], delimiter="|")
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nMerged {len(all_rows)} verdicts -> {out}")

    # Draft migration 019 actions.
    # BLOCKED rows are NOT nulled — they were never examined (quota), they go
    # to the re-run manifest and keep their interim sampled-only status.
    updates = [r for r in all_rows if r["verdict"] == "WRONG"]
    nulls = [r for r in all_rows if r["verdict"] == "UNVERIFIABLE"
             or (r["verdict"] == "CONFIRMED" and r["confidence"] == "LOW")]
    # Entity gate (2026-07-22): reject corrections that collide with the
    # series' actual member plants / grid frequency
    ident = series_identity()
    viol = entity_violations(
        [((r["design_series"], r["field"]), r["corrected_value"], r["source"]) for r in updates], ident)
    if viol:
        print("\n=== ENTITY-GATE REJECTIONS (excluded from draft; review manually) ===")
        rejected_keys = set()
        for v in viol:
            print(" -", v)
            rejected_keys.add(v.split("/")[0])
        updates = [r for r in updates
                   if not any(v.startswith(f"{r['design_series']}/{r['field']}") for v in viol)]
    blocked = [r for r in all_rows if r["verdict"] == "BLOCKED"]
    rerun = os.path.join(HERE, "spec_rerun_manifest.psv")
    with open(rerun, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["design_series", "field", "batch"], delimiter="|")
        w.writeheader()
        w.writerows([{k: r[k] for k in ("design_series", "field", "batch")} for r in blocked])
    print(f"\n{len(blocked)} BLOCKED rows -> {rerun} (re-run next quota window)")
    print(f"\n=== MIGRATION 019 DRAFT: {len(updates)} UPDATEs, {len(nulls)} NULLs ===")
    for r in updates:
        print(f"-- {r['source']}")
        print(f"UPDATE design_series_specs SET {r['field']} = "
              f"'{r['corrected_value']}' WHERE design_series = '{r['design_series']}';")
    print("-- NULL pass (unverifiable under zero-doubt):")
    for r in nulls:
        print(f"UPDATE design_series_specs SET {r['field']} = NULL "
              f"WHERE design_series = '{r['design_series']}';  -- {r['verdict']}/{r['confidence']}")

if __name__ == "__main__":
    main()
