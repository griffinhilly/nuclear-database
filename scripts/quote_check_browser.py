"""Second-pass citation check in headless Chrome, for quotes curl could not check.

Purpose: nrc.gov (Akamai) and some publishers block curl, and PDFs need text extraction, so scripts/quote_check.py
  leaves them FETCH_FAIL / PDF / NOT_FOUND. This re-opens those rows in real Chrome (PDFs via the browser's
  request context + pdftotext) and applies the same quote match.
Inputs:  <dir>/quote_check.tsv and the .psv it checked (same dir; columns item_id, source_url, quote)
Outputs: <dir>/quote_check_final.tsv (item_id, url, first_pass, final, coverage) + counts on stdout
Usage:   python scripts/quote_check_browser.py audit/phase2/qc_w1/wave1_changes.psv
last_run: 2026-10-14
"""
import base64
import csv
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quote_check import norm  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def match(page, quote):
    q = norm(quote.strip(' "\'….'))
    if not q:
        return "NO_QUOTE", 0.0
    # Agents join non-adjacent fragments with "..."; each fragment must be on the page.
    parts = [norm(p) for p in quote.replace("…", "...").split("...") if norm(p)]
    if all(p in page for p in parts):
        return "FOUND", 1.0
    words = [w for w in q.split() if len(w) > 2]
    cov = sum(1 for w in words if w in page) / max(1, len(words))
    runs = [" ".join(q.split()[i:i + 4]) for i in range(max(1, len(q.split()) - 3))]
    return ("PARTIAL" if cov >= 0.7 and any(r in page for r in runs) else "NOT_FOUND"), round(cov, 2)


B64 = """async (u) => { const r = await fetch(u); const blob = await r.blob();
  return await new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result.split(',')[1]); fr.readAsDataURL(blob); }); }"""


def load(pg, url):
    """Page text as Chrome sees it. PDFs: fetched from inside the page (passes bot checks) and run through pdftotext."""
    m = re.search(r"AccessionNumber=(ML\d{4})(\w+)", url)
    if m:  # ADAMS viewer link -> the document itself
        url = f"https://www.nrc.gov/docs/{m.group(1)}/{m.group(1)}{m.group(2)}.pdf"
    try:
        resp = pg.goto(url, wait_until="load", timeout=90000)
        ctype = (resp.headers.get("content-type", "") if resp else "")
        if "pdf" in ctype or url.lower().endswith(".pdf"):
            pg.wait_for_timeout(1500)
            data = base64.b64decode(pg.evaluate(B64, url))
            if data[:5] != b"%PDF-":
                return None
            with tempfile.TemporaryDirectory() as td:
                f = Path(td) / "d.pdf"
                f.write_bytes(data)
                subprocess.run(["pdftotext", str(f), str(f.with_suffix(".txt"))], capture_output=True)
                t = f.with_suffix(".txt")
                return t.read_text(encoding="utf-8", errors="replace") if t.exists() else None
        try:
            pg.wait_for_load_state("networkidle", timeout=20000)
        except Exception:  # noqa: BLE001
            pass
        pg.wait_for_timeout(2500)
        text = pg.inner_text("body")
        return None if "access denied" in text.lower()[:400] else text
    except Exception as e:  # noqa: BLE001
        print("fetch error", url, str(e)[:120])
        return None


def main():
    src = Path(sys.argv[1])
    rows = list(csv.DictReader(open(src, encoding="utf-8"), delimiter="|"))
    first = list(csv.DictReader(open(src.parent / "quote_check.tsv", encoding="utf-8"), delimiter="\t"))
    todo = {}
    for r in first:
        row = rows[int(r["row"]) - 1]
        todo[row["item_id"]] = (row, r["status"])
    cache, out = {}, []
    with sync_playwright() as p:
        # Headed, off-screen: several publishers serve stripped pages to headless Chrome.
        b = p.chromium.launch(executable_path=CHROME, headless=False, args=["--window-position=-2400,0"])
        ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                       "Chrome/130 Safari/537.36", viewport={"width": 1300, "height": 900})
        pg = ctx.new_page()
        for iid, (row, st) in todo.items():
            url = row["source_url"].split()[0].rstrip(";,)") if row["source_url"].strip() else ""
            if st in ("FOUND", "PARTIAL") or not url:
                out.append([iid, url, st, st, ""])
                continue
            if url not in cache:
                cache[url] = norm(load(pg, url) or "") or None
            page = cache[url]
            if page is None:
                out.append([iid, url, st, "FETCH_FAIL", ""])
                continue
            s, cov = match(page, row["quote"])
            out.append([iid, url, st, s, cov])
        b.close()
    with open(src.parent / "quote_check_final.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["item_id", "url", "first_pass", "final", "coverage"])
        w.writerows(out)
    print(Counter(r[3] for r in out))
    for r in out:
        if r[3] not in ("FOUND", "PARTIAL"):
            print(r)


if __name__ == "__main__":
    main()
