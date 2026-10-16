"""Build static/og-card.png, the 1200x630 link-preview image (Open Graph / Twitter card).

purpose:  one branded card for every shared link: REG logo, site name, one-line description,
          and the world operating-capacity line from /api/capacity/history (history only).
inputs:   nuclear_reactors.db via the Flask app; static/reg-v2-logo-main.svg
outputs:  static/og-card.png
run:      python scripts/build_og_card.py   (re-run after big data changes; the line moves slowly)
last_run: 2026-10-16
"""
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import app as site  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

hist = site.app.test_client().get('/api/capacity/history').get_json()
rows = hist.get('history') or hist.get('data') or []
pts = [(int(r['year']), float(r.get('capacity_gw') or 0)) for r in rows if r.get('year') is not None]
pts.sort()
x0, x1 = pts[0][0], pts[-1][0]
ymax = max(v for _, v in pts) * 1.08
W, H = 1040, 250


def xy(y, v):
    return (y - x0) / (x1 - x0) * W, H - v / ymax * H


line = " ".join(f"{x:.1f},{y:.1f}" for x, y in (xy(*p) for p in pts))
area = f"0,{H} " + line + f" {W},{H}"
lx, ly = xy(*pts[-1])
latest = pts[-1][1]
logo = base64.b64encode((ROOT / 'static/reg-v2-logo-main.svg').read_bytes()).decode()

page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html, body {{ margin: 0; }}
body {{ width: 1200px; height: 630px; background: #F4F4F4; font-family: 'Segoe UI', Roboto, Arial, sans-serif; color: #474853; position: relative; overflow: hidden; }}
.bar {{ position: absolute; left: 0; top: 0; width: 1200px; height: 10px; background: #FFBF00; }}
.logo {{ position: absolute; left: 80px; top: 58px; height: 52px; }}
h1 {{ position: absolute; left: 80px; top: 136px; margin: 0; font-size: 66px; font-weight: 600; letter-spacing: -0.5px; color: #1E2C5B; }}
p {{ position: absolute; left: 82px; top: 228px; margin: 0; font-size: 28px; color: #5F6270; }}
svg {{ position: absolute; left: 80px; top: 318px; }}
.lab {{ position: absolute; font-size: 20px; color: #8E919C; }}
</style></head><body><div class="bar"></div>
<img class="logo" src="data:image/svg+xml;base64,{logo}">
<h1>Global Nuclear Database</h1>
<p>Every nuclear power reactor in the world, {x0} to today. Free and sourced.</p>
<svg width="{W + 12}" height="{H + 12}" viewBox="0 -6 {W + 12} {H + 12}">
  <polygon points="{area}" fill="#40774A" fill-opacity="0.12"/>
  <polyline points="{line}" fill="none" stroke="#40774A" stroke-width="5" stroke-linejoin="round"/>
  <circle cx="{lx:.1f}" cy="{ly:.1f}" r="9" fill="#40774A"/>
</svg>
<div class="lab" style="left:80px; top:578px">{x0}</div>
<div class="lab" style="left:{80 + W - 38}px; top:578px">{x1}</div>
<div class="lab" style="left:80px; top:318px; color:#40774A; font-weight:600">World nuclear capacity in operation</div>
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    pg = b.new_page(viewport={'width': 1200, 'height': 630})
    pg.set_content(page)
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(ROOT / 'static/og-card.png'))
    b.close()
print('static/og-card.png', len(pts), 'points', x0, x1, round(latest, 1))
