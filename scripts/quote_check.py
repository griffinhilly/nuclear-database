"""Re-find each agent-cited quote on its source page (deterministic citation check).

Purpose: agents must back every verdict with a URL + verbatim quote; this fetches the page and
  checks the quote is really there, catching fabricated or paraphrased citations.
Inputs:  one or more pipe-separated result files with columns source_url and quote.
Outputs: <first input dir>/quote_check.tsv (file, row, url, status, coverage) + counts on stdout.
  Pages that block curl (nrc.gov, some PDFs): re-check with scripts/quote_check_browser.py.
  status: FOUND (whole quote present), PARTIAL (>=70% of the quote's words found in order-free
  window match), NOT_FOUND, FETCH_FAIL, PDF (pdftotext failed), NO_QUOTE. PDFs are read with pdftotext.
Usage:   python scripts/quote_check.py audit/batch_c/results_*.psv
last_run: 2026-10-13
"""
import csv
import html
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
_cache = {}


def norm(s):
    s = html.unescape(s)
    s = unicodedata.normalize("NFKC", s).lower()
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s%.,'-]", " ", s)).strip()


def fetch(url):
    if url in _cache:
        return _cache[url]
    if not url.startswith("http"):
        url = "https://" + url
    r = subprocess.run(["curl", "-sS", "-L", "--max-time", "40", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True)
    body, _, code = r.stdout.rpartition(b"\n")
    # A 4xx/5xx page (e.g. nrc.gov's "Access Denied" bot block) is a failed fetch, not a page without the quote.
    if r.returncode != 0 or not body or not code.strip().startswith(b"2"):
        _cache[url] = None
    elif body[:5] == b"%PDF-":
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "d.pdf"
            f.write_bytes(body)
            subprocess.run(["pdftotext", str(f), str(f.with_suffix(".txt"))], capture_output=True)
            t = f.with_suffix(".txt")
            _cache[url] = norm(t.read_text(encoding="utf-8", errors="replace")) if t.exists() else "PDF"
    else:
        text = body.decode("utf-8", errors="replace")
        text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
        _cache[url] = norm(re.sub(r"(?s)<[^>]+>", " ", text))
    time.sleep(0.5)
    return _cache[url]


def check(url, quote):
    if not quote.strip():
        return "NO_QUOTE", 0.0
    page = fetch(url.split()[0].rstrip(";,)"))
    if page is None:
        return "FETCH_FAIL", 0.0
    if page == "PDF":
        return "PDF", 0.0
    q = norm(quote.strip(' "\'….'))
    if q and q in page:
        return "FOUND", 1.0
    words = [w for w in q.split() if len(w) > 2]
    if not words:
        return "NOT_FOUND", 0.0
    cov = sum(1 for w in words if w in page) / len(words)
    # also require some 4-word run to appear, so scattered common words don't pass
    runs = [" ".join(q.split()[i:i + 4]) for i in range(max(1, len(q.split()) - 3))]
    has_run = any(r in page for r in runs)
    return ("PARTIAL" if cov >= 0.7 and has_run else "NOT_FOUND"), round(cov, 2)


def main():
    # Optional: --cols <url_col>,<quote_col> (default source_url,quote) and --out <file name>.
    args, url_col, quote_col, out_name = sys.argv[1:], "source_url", "quote", "quote_check.tsv"
    if "--cols" in args:
        i = args.index("--cols"); url_col, quote_col = args[i + 1].split(","); del args[i:i + 2]
    if "--out" in args:
        i = args.index("--out"); out_name = args[i + 1]; del args[i:i + 2]
    files = args
    out_rows = []
    for f in files:
        lines = Path(f).read_text(encoding="utf-8").splitlines()
        hdr = lines[0].split("|")
        iu, iq = hdr.index(url_col), hdr.index(quote_col)
        iv = hdr.index("verdict") if "verdict" in hdr else None
        for n, line in enumerate(lines[1:], start=1):
            p = line.split("|")
            if (iv is not None and p[iv] in ("BLOCKED",)) or not p[iu].strip():
                out_rows.append([Path(f).name, n, p[iu], "NO_SOURCE", 0.0]); continue
            status, cov = check(p[iu].strip(), p[iq])
            out_rows.append([Path(f).name, n, p[iu], status, cov])
    out = Path(files[0]).parent / out_name
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["file", "row", "url", "status", "coverage"])
        w.writerows(out_rows)
    print(out, Counter(r[3] for r in out_rows))


if __name__ == "__main__":
    main()
