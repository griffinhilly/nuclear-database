"""Review reader correction submissions from every Fly machine.

purpose:  list new "Suggest a correction" submissions and mark them accepted or declined.
          Accepting also adds a public line to data/contributions.json (commit + deploy to
          publish it on /contributions). The data change itself still goes through a migration.
inputs:   the live site's /admin/api/submissions endpoints, one call per Fly machine
          (each machine keeps its own /data/submissions.db). Admin credential: env NDB_ADMIN_TOKEN,
          else the file ~/.config/nuclear-database/admin_token (never in the repo).
          Machine ids: --machines a,b,c, else `flyctl machines list --json`.
outputs:  status updates on the machine that holds each row; data/contributions.json on accept.
usage:
  python scripts/review_submissions.py list [--all]
  python scripts/review_submissions.py accept MACHINE:ID "Public one-line summary of the update"
  python scripts/review_submissions.py decline MACHINE:ID
  options: --site URL (default env NDB_SITE_URL or https://nuclear-database.fly.dev)
           --machines id1,id2    --local (talk to http://127.0.0.1:5001, no machine routing)
last_run: 2026-10-16
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
CONTRIB = ROOT / "data" / "contributions.json"
CRED_FILE = Path.home() / ".config" / "nuclear-database" / "admin_token"
FLYCTL = [Path.home() / ".fly" / "bin" / "flyctl.exe.old", Path.home() / ".fly" / "bin" / "flyctl.exe"]


def opt(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        val = argv[i + 1]
        del argv[i:i + 2]
        return val
    return default


def credential():
    v = os.environ.get("NDB_ADMIN_TOKEN", "").strip()
    if not v and CRED_FILE.exists():
        v = CRED_FILE.read_text(encoding="utf-8").strip()
    if not v:
        sys.exit(f"No admin credential: set NDB_ADMIN_TOKEN or write it to {CRED_FILE}")
    return v


def machine_ids():
    for exe in FLYCTL:
        if exe.exists():
            try:
                out = subprocess.run([str(exe), "machines", "list", "--json", "-a", "nuclear-database"],
                                     capture_output=True, text=True, timeout=60)
                if out.returncode == 0:
                    return [m["id"] for m in json.loads(out.stdout) if m.get("state") != "destroyed"]
            except (OSError, ValueError, subprocess.TimeoutExpired):
                continue
    sys.exit("Could not list Fly machines; pass --machines id1,id2,id3")


def call(site, path, machine, cred, body=None):
    headers = {"Authorization": f"Bearer {cred}", "User-Agent": "review-submissions"}
    if machine != "local":
        headers["fly-force-instance-id"] = machine
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(site + path, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"{machine}: HTTP {e.code} on {path}")


def main(argv):
    local = "--local" in argv
    if local:
        argv.remove("--local")
    site = opt(argv, "--site", os.environ.get("NDB_SITE_URL", "https://nuclear-database.fly.dev")).rstrip("/")
    machines = opt(argv, "--machines")
    if local:
        site, machines = "http://127.0.0.1:5001", ["local"]
    else:
        machines = machines.split(",") if machines else machine_ids()
    cred = credential()
    cmd = argv[0] if argv else "list"

    if cmd == "list":
        q = "?status=all" if "--all" in argv else ""
        total = 0
        for m in machines:
            res = call(site, "/admin/api/submissions" + q, m, cred)
            if res.get("machine") not in (m, "local"):
                print(f"WARNING: asked for machine {m}, answered by {res.get('machine')}")
            for r in res["submissions"]:
                total += 1
                print(f"{m}:{r['id']} [{r['status']}] {r['created_at']}  {r['page_title']} ({r['page_url']})")
                print(f"   what:     {r['what']}")
                print(f"   proposed: {r['proposed']}")
                print(f"   source:   {r['source']}")
                print(f"   from:     {r['name'] or '-'} <{r['email'] or '-'}>  credit_ok={r['credit_ok']}")
        print(f"{total} submission(s) across {len(machines)} machine(s)")
        return 0

    if cmd in ("accept", "decline") and len(argv) >= 2 and ":" in argv[1]:
        m, sid = argv[1].rsplit(":", 1)
        status = "accepted" if cmd == "accept" else "declined"
        summary = argv[2] if len(argv) > 2 else None
        if status == "accepted" and not summary:
            print("accept needs a public one-line summary")
            return 1
        rows = {str(r["id"]): r for r in call(site, "/admin/api/submissions?status=all", m, cred)["submissions"]}
        if sid not in rows:
            sys.exit(f"No submission {sid} on machine {m}")
        res = call(site, f"/admin/api/submissions/{sid}", m, cred, {"status": status, "public_summary": summary})
        print(f"{res['updated']} row(s) marked {status} on {res['machine']}")
        if status == "accepted" and res["updated"]:
            r = rows[sid]
            entries = json.loads(CONTRIB.read_text(encoding="utf-8")) if CONTRIB.exists() else []
            entries.append({"date": date.today().isoformat(), "summary": summary,
                            "page_url": r["page_url"], "page_title": r["page_title"],
                            "credit": r["name"] if r["credit_ok"] and (r["name"] or "").strip() else None,
                            "ref": f"{m}:{sid}"})
            CONTRIB.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"Added to {CONTRIB.relative_to(ROOT)}; commit and deploy to publish.")
        return 0

    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
