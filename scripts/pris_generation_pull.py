"""Pull IAEA PRIS per-reactor generation (monthly + annual tables) from the pris-stats Power BI model.

Purpose: reproducible, machine-readable copy of PRIS "electricity supplied" (GWh net) per reactor
  and year, for diffing against generation_annual (scripts/pris_generation_diff.py).
  Route (recipe: audit/pris_generation_route_2026-10-14.md): the pris-stats.iaea.org app hands any
  anonymous visitor a Power BI embed token; with it the Power BI /explore/querydata endpoint returns
  the PRIS semantic model. We use Fact_ReactorMonthlyProduction summed to years (the annual table
  is missing ~20 US units for 2024), and pull Fact_ReactorAnnualProduction for comparison + LoadFactor.
Inputs:  network only. ~20 serial requests with 1.5 s gaps:
           1 GET  pris-stats.iaea.org/reactor/reactor-detailed-report   (embed token, ~1 h life)
           1 GET  {cluster}/explore/reports/{id}/modelsAndExploration     (modelId, DatasetId)
           1 POST querydata  Dim_Reactor (names, country, grid/shutdown dates)
           1 POST querydata  monthly table, server-side SUM/COUNT per reactor-year (cross-check)
           ~13 POST querydata monthly table per month, in year blocks (<30k rows each)
           1 POST querydata  annual table (Energy, LoadFactor)
Outputs: audit/pris_generation/monthly_raw.json   per-month rows [ReactorId, Year, Month, Energy] + metadata
         audit/pris_generation/annual_raw.json    annual-table rows + metadata
         audit/pris_generation/reactors_dim.json  Dim_Reactor rows (id, unit name, country, status, dates)
         audit/pris_generation/reactor_year.csv   pris_reactor_id, unit_name, country_code, year,
             gwh_net_from_monthly, months_present, gwh_net_annual_table, load_factor
Usage:   python scripts/pris_generation_pull.py            # pull (network) + build CSV + validate
         python scripts/pris_generation_pull.py --cached   # rebuild CSV + validate from saved JSON only
Validate: world 2024 monthly-sum total ~2,617.5 TWh; BYRON-2 (736) 2024 ~10,204.3 GWh. Exit 1 if off.
Attribution: data is IAEA PRIS (terms of use apply). Source string for DB rows:
  "IAEA PRIS data browser (pris-stats.iaea.org), pulled <date>".
last_run: 2026-10-14
"""
import base64
import csv
import json
import sys
import time
import urllib.parse
import uuid
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "audit" / "pris_generation"
TOKEN_URL = "https://pris-stats.iaea.org/reactor/reactor-detailed-report"
GAP_S = 1.5
WINDOW = 30000
N_REQ = 0


def _sleep():
    time.sleep(GAP_S)


class PBI:
    """Minimal Power BI embed-token client (explore/querydata)."""

    def __init__(self):
        global N_REQ
        r = requests.get(TOKEN_URL, headers={"Accept": "application/json"}, timeout=60)
        N_REQ += 1
        r.raise_for_status()
        cfg = r.json()
        cfg = json.loads(cfg) if isinstance(cfg, str) else cfg
        self.token = cfg["EmbedToken"]["Token"]
        self.expires = cfg["EmbedToken"]["Expiration"]
        rep = cfg["EmbedReport"][0]
        self.report_id = rep["ReportId"]
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(rep["EmbedUrl"]).query)
        conf = json.loads(base64.b64decode(qs["config"][0] + "==").decode("utf-8"))
        self.cluster = conf["clusterUrl"].rstrip("/")
        _sleep()
        m = requests.get(f"{self.cluster}/explore/reports/{self.report_id}/modelsAndExploration"
                         "?preferReadOnlySession=true", headers=self._h(), timeout=60)
        N_REQ += 1
        m.raise_for_status()
        model = m.json()["models"][0]
        self.model_id, self.dataset = model["id"], model["dbName"]
        print(f"token ok (expires {self.expires}); report {self.report_id}; cluster {self.cluster}; "
              f"model {self.model_id}; dataset {self.dataset}")

    def _h(self):
        return {"Authorization": "EmbedToken " + self.token, "Content-Type": "application/json",
                "ActivityId": str(uuid.uuid4()), "RequestId": str(uuid.uuid4())}

    def meta(self):
        return {"report_id": self.report_id, "cluster": self.cluster, "model_id": self.model_id,
                "dataset_id": self.dataset}

    def query(self, frm, select, where=None):
        """Run one semantic query; return (rows as dicts keyed by select Name, is_complete)."""
        global N_REQ
        q = {"Version": 2, "From": [{"Name": n, "Entity": e, "Type": 0} for n, e in frm], "Select": select}
        if where:
            q["Where"] = where
        body = {"version": "1.0.0", "cancelQueries": [], "modelId": self.model_id, "queries": [{
            "QueryId": "", "ApplicationContext": {"DatasetId": self.dataset,
                                                  "Sources": [{"ReportId": self.report_id, "VisualId": "pull"}]},
            "Query": {"Commands": [{"SemanticQueryDataShapeCommand": {
                "Query": q,
                "Binding": {"Primary": {"Groupings": [{"Projections": list(range(len(select)))}]},
                            "DataReduction": {"DataVolume": 4, "Primary": {"Window": {"Count": WINDOW}}},
                            "Version": 1},
                "ExecutionMetricsKind": 1}}]}}]}
        _sleep()
        r = requests.post(f"{self.cluster}/explore/querydata?synchronous=true", headers=self._h(),
                          json=body, timeout=180)
        N_REQ += 1
        r.raise_for_status()
        resp = json.loads(r.content.decode("utf-8-sig"))
        return decode(resp, [s["Name"] for s in select])


def col(src, prop):
    return {"Column": {"Expression": {"SourceRef": {"Source": src}}, "Property": prop}, "Name": f"{src}.{prop}"}


def agg(src, prop, fn, name):
    # fn: 0 Sum, 3 Min, 4 Max, 5 CountNonNull (codes checked against known rows 2026-10-14)
    return {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": src}},
                                                      "Property": prop}}, "Function": fn}, "Name": name}


def where_in(src, prop, values):
    return {"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": src}},
                                                             "Property": prop}}],
                                 "Values": [[{"Literal": {"Value": f"{v}L"}}] for v in values]}}}


def decode(resp, names):
    """Decode a DSR response (R = repeat-previous bitmask, Ø = null bitmask, DN = value dictionary)."""
    ds = resp["results"][0]["result"]["data"]["dsr"]["DS"][0]
    vd = ds.get("ValueDicts", {})
    schema, prev, out = None, [None] * len(names), []
    for row in ds["PH"][0]["DM0"]:
        if "S" in row:
            schema = row["S"]
        rep, nul = row.get("R", 0), row.get("Ø", 0)
        it = iter(row.get("C", []))
        vals = []
        for k, sc in enumerate(schema):
            if rep >> k & 1:
                v = prev[k]
            elif nul >> k & 1:
                v = None
            else:
                v = next(it)
                if "DN" in sc and isinstance(v, int):
                    v = vd[sc["DN"]][v]
            vals.append(v)
        prev = vals
        out.append(dict(zip(names, vals)))
    return out, bool(ds.get("IC"))


def num(v):
    return None if v is None else float(v)


def iso(v):
    """Power BI dates arrive as epoch ms or ISO strings."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc).date().isoformat()
    return str(v)[:10]


def pull_monthly_block(pbi, years):
    rows, complete = pbi.query(
        [("f", "Fact_ReactorMonthlyProduction")],
        [col("f", "ReactorId"), col("f", "Year"), col("f", "Month"),
         agg("f", "Energy", 0, "energy"), agg("f", "Energy", 5, "n")],
        [where_in("f", "Year", years)])
    if not complete or len(rows) >= WINDOW:
        if len(years) == 1:
            raise RuntimeError(f"year {years[0]} alone exceeds one window")
        mid = len(years) // 2
        print(f"    block {years[0]}-{years[-1]} incomplete ({len(rows)} rows) -> splitting")
        return pull_monthly_block(pbi, years[:mid]) + pull_monthly_block(pbi, years[mid:])
    print(f"    monthly {years[0]}-{years[-1]}: {len(rows)} rows")
    return rows


def pull():
    OUT.mkdir(parents=True, exist_ok=True)
    pulled = date.today().isoformat()
    pbi = PBI()

    dim, ic = pbi.query([("r", "Dim_Reactor")],
                        [col("r", p) for p in ("Id", "UnitName", "CountryCode", "StatusName", "GridDate",
                                               "CommercialDate", "ShutdownDate")])
    assert ic, "Dim_Reactor incomplete"
    dim = [{"id": int(d["r.Id"]), "unit_name": d["r.UnitName"], "country_code": d["r.CountryCode"],
            "status": d["r.StatusName"], "grid_date": iso(d["r.GridDate"]),
            "commercial_date": iso(d["r.CommercialDate"]), "shutdown_date": iso(d["r.ShutdownDate"])} for d in dim]
    print(f"  Dim_Reactor: {len(dim)} reactors")

    agg_rows, ic = pbi.query([("f", "Fact_ReactorMonthlyProduction")],
                             [col("f", "ReactorId"), col("f", "Year"), agg("f", "Energy", 0, "energy"),
                              agg("f", "Energy", 5, "n"), agg("f", "Month", 3, "mmin"), agg("f", "Month", 4, "mmax")])
    assert ic, "monthly aggregate incomplete"
    print(f"  monthly aggregate: {len(agg_rows)} reactor-years")
    years = sorted({int(r["f.Year"]) for r in agg_rows})
    per_year = defaultdict(int)
    for r in agg_rows:
        per_year[int(r["f.Year"])] += int(r["n"] or 0)
    # Year blocks sized to stay well under one 30k-row window.
    blocks, cur, size = [], [], 0
    for y in years:
        if cur and size + per_year[y] > 24000:
            blocks.append(cur)
            cur, size = [], 0
        cur.append(y)
        size += per_year[y]
    blocks.append(cur)
    monthly = []
    for b in blocks:
        monthly += pull_monthly_block(pbi, b)

    ann, ic = pbi.query([("a", "Fact_ReactorAnnualProduction")],
                        [col("a", "ReactorId"), col("a", "Year"), agg("a", "Energy", 0, "energy"),
                         agg("a", "Energy", 5, "n"), agg("a", "LoadFactor", 0, "lf")])
    assert ic, "annual table incomplete"
    print(f"  annual table: {len(ann)} reactor-years")

    meta = {"source": "IAEA PRIS data browser (pris-stats.iaea.org), Power BI model "
                      "PRIS_semantic_model via anonymous embed token", "pulled": pulled,
            "requests": N_REQ, **pbi.meta()}
    (OUT / "reactors_dim.json").write_text(json.dumps({"meta": meta, "rows": dim}, ensure_ascii=False, indent=0),
                                           encoding="utf-8")
    (OUT / "monthly_raw.json").write_text(json.dumps({
        "meta": {**meta, "table": "Fact_ReactorMonthlyProduction",
                 "columns": ["ReactorId", "Year", "Month", "Energy_GWh_net", "row_count"],
                 "server_side_reactor_year_sums": [[int(r["f.ReactorId"]), int(r["f.Year"]), num(r["energy"]),
                                                    int(r["n"] or 0), r["mmin"], r["mmax"]] for r in agg_rows]},
        "rows": [[int(r["f.ReactorId"]), int(r["f.Year"]), int(r["f.Month"]), num(r["energy"]), int(r["n"] or 0)]
                 for r in monthly]}, ensure_ascii=False), encoding="utf-8")
    (OUT / "annual_raw.json").write_text(json.dumps({
        "meta": {**meta, "table": "Fact_ReactorAnnualProduction",
                 "columns": ["ReactorId", "Year", "Energy_GWh_net", "row_count", "LoadFactor_pct"]},
        "rows": [[int(r["a.ReactorId"]), int(r["a.Year"]), num(r["energy"]), int(r["n"] or 0), num(r["lf"])]
                 for r in ann]}, ensure_ascii=False), encoding="utf-8")
    print(f"  {N_REQ} requests total")


def build():
    dim = {d["id"]: d for d in json.loads((OUT / "reactors_dim.json").read_text(encoding="utf-8"))["rows"]}
    mraw = json.loads((OUT / "monthly_raw.json").read_text(encoding="utf-8"))
    araw = json.loads((OUT / "annual_raw.json").read_text(encoding="utf-8"))
    ok = True

    msum, mcnt, dup = defaultdict(float), defaultdict(int), 0
    for rid, y, m, e, n in mraw["rows"]:
        if e is None:
            continue
        msum[(rid, y)] += e
        mcnt[(rid, y)] += 1
        dup += n > 1
    # Cross-check our client-side month sums against the server-side reactor-year aggregate.
    server = {(r[0], r[1]): (r[2], r[3]) for r in mraw["meta"]["server_side_reactor_year_sums"]}
    bad = [k for k in set(server) | set(msum)
           if abs((server.get(k, (0, 0))[0] or 0) - msum.get(k, 0)) > 0.01]
    print(f"monthly rows {len(mraw['rows'])}; reactor-years {len(msum)}; month cells with >1 source row: {dup}; "
          f"client vs server sum mismatches: {len(bad)}")
    ok &= not bad
    ann = {(r[0], r[1]): (r[2], r[4]) for r in araw["rows"]}
    adup = sum(1 for r in araw["rows"] if r[3] > 1)
    print(f"annual-table reactor-years {len(ann)}; with >1 source row: {adup}")

    keys = sorted(set(msum) | set(ann))
    with open(OUT / "reactor_year.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pris_reactor_id", "unit_name", "country_code", "year", "gwh_net_from_monthly",
                    "months_present", "gwh_net_annual_table", "load_factor"])
        for rid, y in keys:
            d = dim.get(rid, {})
            a_e, a_lf = ann.get((rid, y), (None, None))
            w.writerow([rid, d.get("unit_name", ""), d.get("country_code", ""), y,
                        round(msum[(rid, y)], 3) if (rid, y) in msum else "", mcnt.get((rid, y), 0),
                        "" if a_e is None else round(a_e, 3), "" if a_lf is None else round(a_lf, 3)])
    print(f"wrote {OUT / 'reactor_year.csv'}: {len(keys)} reactor-years")

    # Validation targets from the recipe (IAEA published 2,617 TWh for 2024; EIA-923 Byron-2 10,204,282 MWh).
    w24 = sum(v for (rid, y), v in msum.items() if y == 2024) / 1000
    b2 = msum.get((736, 2024))
    both = [k for k in msum if k in ann and ann[k][0] is not None]
    agree = sum(1 for k in both if abs(msum[k] - ann[k][0]) <= 0.01 * max(abs(ann[k][0]), 1e-9) or
                abs(msum[k] - ann[k][0]) < 0.5)
    print(f"VALIDATE world 2024 (monthly sum): {w24:,.1f} TWh (target ~2,617.5)")
    print(f"VALIDATE BYRON-2 2024: {b2:,.1f} GWh (target ~10,204.3; name in Dim: {dim.get(736, {}).get('unit_name')})")
    print(f"VALIDATE monthly vs annual agree within 1%: {agree} of {len(both)} reactor-years with both")
    for y in (2010, 2021, 2025):
        print(f"  world {y}: {sum(v for (rid, yy), v in msum.items() if yy == y) / 1000:,.1f} TWh")
    ok &= abs(w24 - 2617.5) < 3 and b2 is not None and abs(b2 - 10204.3) < 1
    return ok


if __name__ == "__main__":
    if "--cached" not in sys.argv:
        pull()
    sys.exit(0 if build() else 1)
