"Run `nbs/index.ipynb` and screenshot each `preview` it makes into `nbs/images/`, for the README and the docs site."
import sys
from pathlib import Path
from fastcore.nbio import read_nb
from execnb.shell import CaptureShell
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
nbs, out = root/'nbs', root/'nbs'/'images'

def run_index():
    "Run every code cell of the index, the `eval: false` server cell included, from `nbs/`."
    sh = CaptureShell(path=nbs)
    sh.run_all(read_nb(nbs/'index.ipynb'), exc_stop=True)
    return sh.user_ns

def shoot(ns, only=()):
    "One PNG per preview, or per name in `only`, at twice the pixel density."
    out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nm in ns['SHOWN']:
            if only and nm not in only: continue
            pg = b.new_page(viewport=dict(width=960, height=600), device_scale_factor=2, color_scheme='light')
            pg.goto(f"http://localhost:{ns['PORT']}/{nm}")
            pg.wait_for_load_state('networkidle')
            pg.locator('main').screenshot(path=out/f'{nm}.png')
            pg.close()
            print(out/f'{nm}.png')
        b.close()

if __name__ == '__main__':
    shoot(run_index(), sys.argv[1:])
