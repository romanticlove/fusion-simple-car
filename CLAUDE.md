# RC John Deere 6M — Claude working rules

Hobby project: a 3D-printed RC model that *looks like* a John Deere 6M at 1:10 or 1:12.
"Looks right" is the bar, not exact dimensions. Keep things simple, iterate fast, don't over-engineer.

Drivetrain: one **N20 gear motor** drives the rear axle. A **micro servo** (SG90/MG90S) steers the front axle.
Hardware sizes live in [hardware.md](hardware.md); rough tractor proportions in [reference/README.md](reference/README.md).

## Fusion connection
- Fusion's built-in MCP server (`fusion` in `.mcp.json`, `http://127.0.0.1:27182/mcp`). Fusion must be running with a design open.
- `fusion_mcp_execute` (script) runs Python. The script must define `run(context)`. Don't wrap it in try/except; let errors surface.
- `fusion_mcp_read` (screenshot) shows the result. Use it after every build.

## Workflow
1. Each part is one script: `parts/<part-name>/<part_name>.py`. The repo is the source of truth, so don't model with throwaway scripts.
2. Sizes go in the `P` dict at the top of the script (mm). To change the part, edit `P` and re-run.
3. Use the helpers in [lib/fusion_helpers.py](lib/fusion_helpers.py). `fresh_component(name)` deletes and rebuilds the part on every run.
4. Run the script, take a screenshot (iso plus whichever ortho view matters), show it to the user, and adjust.
5. Once the user is happy: `fh.export(comp, "<name>")` → `exports/<name>.3mf`.
6. Put each part in its own component. Don't close, save, or open documents without asking.

## Scale
- Body/appearance sizes = real size ÷ scale (10 or 12; ask if it hasn't been decided yet).
- Motor, servo, screw, bearing, and axle fits use **real** sizes. Never scale these.

## Print-friendly defaults (Bambu Lab, 0.4 mm nozzle)
- Walls 1.2–1.6 mm, small cosmetic detail ≥ 0.8 mm.
- Fit clearance 0.2 mm per side (update this after the first test prints).
- Avoid overhangs steeper than 45° and design so parts print without supports where possible.
- Max part size 256 mm (180 mm on an A1 mini). Split bigger parts and join them with pins or tabs plus glue.
- PLA/PETG for parts, TPU for tires. Keep the model light, because the N20 is weak.
- Write the print orientation in the docstring at the top of each part script.
