---
name: new-part
description: Create or rebuild one printable part as a script under parts/<name>/ that reads its position and connection points from layout.py, run it in Fusion, screenshot it, and collision-check it against the other parts. Use for /new-part <name> or any request to model a new part.
---

# New part

## Before writing code
- Read `layout.py` and `decisions.md`. If the part connects to something that has no `INTERFACES` entry yet,
  agree on the interface with the user first (screw size, hole positions) and add it to `layout.py`.
- If the part depends on hardware whose suitability hasn't been checked (motor torque, bearing load), do the numbers check first (see /kickoff step 2).
- Ask only about choices that change the design (mechanism type, fastening style). Recommend one option.

## Script skeleton: `parts/<part-name>/<part_name>.py`
```python
"""<What it is, how it connects (which INTERFACES), what hardware it holds>.

Print orientation: <face on bed, supports yes/no>.
"""
import importlib
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "template", "lib"), ROOT, os.path.join(ROOT, "parts", "_lib")]
import fusion_helpers as fh  # noqa: E402
import layout as L  # noqa: E402

importlib.reload(fh)
importlib.reload(L)
F = fh.fits(L)  # printer fits: template defaults + layout.FIT overrides

# Part-only sizes in mm. Positions and connection points come from layout.py.
P = {
}


def run(context):
    comp = fh.fresh_component("<part_name>")
    ...
    print("<part_name> built: <key dimensions>")
```
Rules:
- Positions, hole patterns and shared sizes come from `L.MAIN` / `L.INTERFACES`, and fits from `F = fh.fits(L)`. Never copy those numbers into `P`.
- Hardware fits use real sizes from `hardware.md`.
- Use temporary solids (`fh.cyl`, `fh.box`, `fh.union`... then `fh.add_body`) for housings and shafts. Use sketches plus `fh.extrude` for profiles. Use `template/lib/gears.py` for gears.
- Multi-piece parts: one component per printed piece, all built by the same script.
- Helpers shared by several parts of THIS project go in `parts/_lib/`. Never edit anything under `template/`
  (template-owned, see the ownership table in template/RULES.md). If a template helper is wrong or missing, tell the user.
- Respect the print rules in template/RULES.md, and keep each piece under the bed size.

## Run and check
1. Add the script to `L.PARTS` (build order: things it connects to come first).
2. Run it with the loader from template/RULES.md. Fix errors until it builds.
3. Screenshot: iso plus the ortho view that shows the important fit.
4. Run `template/assembly.py` (loader) and report its collision lines. Treat any clash > 0.01 mm³ as a bug to fix.
5. Show the user the screenshots, the key dimensions and anything marginal. Iterate on `P` / `layout.py`.
6. Only after the user approves: `fh.export(comp, "<name>")` for each printed component, then offer to commit.
