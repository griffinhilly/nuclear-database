"""Pull every reactor from the IAEA PRIS JSON API (pris-stats.iaea.org).

Purpose: cache the full PRIS fleet (all statuses) for deterministic diffs against the DB.
  PRIS moved from pris.iaea.org (HTML) to an Angular app in 2026; the old scrapers are dead.
  Endpoints (found 2026-10-13 in the app bundle):
    /country/countries/                 -> 38 country codes
    /reactor/reactors-by-code/<CC>      -> every reactor in a country, incl. shutdown
    /reactor/reactor-by-id/<id>         -> one reactor + lifetime factors
Inputs:  network (curl, ~1 request/second).
Outputs: audit/pris_api/<CC>.json per country + audit/pris_api/all_reactors.json (flat list).
Usage:   python scripts/pris_api_pull.py [--force]
last_run: 2026-10-13
"""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = "https://pris-stats.iaea.org"
OUT = Path(__file__).resolve().parent.parent / "audit" / "pris_api"


def get(path):
    # curl, not requests: the old PRIS host fingerprinted Python's TLS; keep the proven path.
    r = subprocess.run(["curl", "-sS", "-f", "--max-time", "60", "-H", "Accept: application/json", f"{BASE}/{path}"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(f"{path}: curl exit {r.returncode} {r.stderr.strip()}")
    return json.loads(r.stdout)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    force = "--force" in sys.argv
    codes = sorted(c["countryCode"] for c in get("country/countries/")["items"])
    print(f"{len(codes)} countries")
    everything = []
    for cc in codes:
        f = OUT / f"{cc}.json"
        if f.exists() and not force:
            items = json.loads(f.read_text(encoding="utf-8"))
        else:
            items = get(f"reactor/reactors-by-code/{cc}")["items"]
            f.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
            time.sleep(1)
        everything.extend(items)
        print(f"  {cc}: {len(items)}")
    (OUT / "all_reactors.json").write_text(json.dumps(everything, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"total {len(everything)} reactors -> {OUT / 'all_reactors.json'}")


if __name__ == "__main__":
    main()
