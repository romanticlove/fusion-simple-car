# RC John Deere 6M with Claude Code + Fusion

Claude Code drives Autodesk Fusion through Fusion's built-in MCP server. It writes a Python script for each part,
runs it in your open Fusion design, checks the result with screenshots, and exports a 3MF for Bambu Studio.

## One-time setup

1. **Enable the MCP server in Fusion**
   - Open Fusion → *Preferences* → *General* → *API* → tick **Fusion MCP Server** (default port **27182**).
   - Click **Apply** (closing the dialog without Apply loses the setting), then restart Fusion.
   - Don't see the option? Update Fusion first. If it's still missing on the Personal license, use the fallback below.
2. **Open a new design** in Fusion (File → New Design). Leave Fusion running.
3. **Start Claude Code in this folder** (a *new* session, because `.mcp.json` is read at startup):
   ```
   cd D:\programming\fusion-mcp-test
   claude
   ```
   Then run `/mcp`. `fusion` should show as connected. If the port in Fusion isn't 27182, change it in `.mcp.json`.
4. **Smoke test.** Ask Claude:
   > Take a screenshot of the Fusion viewport.

   Then:
   > Build parts/n20-mount and show me an iso screenshot, then export it.

   You should get `exports/n20_mount.3mf`. Print it and push an N20 in to check the fit.

### Fallback if the toggle isn't there
Use the community add-in [prim-design/fusion-mcp](https://github.com/prim-design/fusion-mcp) (MIT). It installs an
add-in into Fusion plus a local MCP server. That needs Python/`uv` on this PC, which isn't installed yet. Ask Claude to set it up
and update `.mcp.json`. The workflow stays the same, but the tool names differ.

## How to work with Claude

- Talk about the part, not the code: *"Make the rear axle housing: N20 in the middle, 3 mm axle, bolts to the chassis tub with two M3."*
- Claude builds it, shows a screenshot, and you say what to change ("taller", "move the holes outward", "thinner walls").
- Drop photos into `reference/photos/` and point Claude at them for body shapes.
- Each part lives in `parts/<name>/`, so you can come back days later and say "make the fender 5 mm wider".
- Commit when a part is good. Git history is your undo across sessions.

**Suggested build order**
1. Chassis tub with the N20 rear drive.
2. Front axle with servo steering (simple bell-crank or direct link).
3. Wheels and TPU tires.
4. Body shell: hood, cab, fenders.
5. Details (mirrors, lights, steps), if you feel like it.

Pick 1:10 or 1:12 before step 1. Rough sizes are in [reference/README.md](reference/README.md).

## Repo layout

| Path | What |
|---|---|
| `CLAUDE.md` | Rules Claude follows (workflow, scale, print defaults) |
| `.mcp.json` | Fusion MCP connection |
| `.claude/settings.json` | Auto-enables the server; screenshots don't need approval, but running scripts does |
| `lib/fusion_helpers.py` | mm-based helpers: components, rectangles, extrude, export |
| `parts/` | One script per part |
| `hardware.md` | Real sizes of motor, servo, screws |
| `reference/` | Tractor proportions + photos |
| `exports/` | Generated 3MF/STL (not committed) |

## Limitations (what to expect)

- **Boxy is easy, curvy is hard.** Chassis, brackets, mounts, wheels, and cab frames come out well. The hood's curves,
  rounded fenders, and cab glass come out blocky or lofted when scripted. That's fine for a stylized model, but for smooth
  organic shapes you'd sculpt by hand in Fusion's Form workspace.
- **Claude sees only screenshots.** It can misjudge proportions or miss a broken face, so you're the final judge of how it looks.
- **Fusion must be open**, and the connection is local to this PC. Scripts edit whatever design is currently active,
  so keep a design open for this project and save it now and then. Claude can also undo.
- **Script approval.** By default you approve every script Claude runs. Once you trust the flow, allow
  `mcp__fusion__fusion_mcp_execute` in `.claude/settings.json` to skip the prompts.
- **Fusion Personal license.** Only 10 editable documents at a time, and the MCP option may not be offered (see fallback).
  STL/3MF export works.
- **FDM detail limit.** Things thinner than ~0.8 mm (grille mesh, badges, handrails) won't print cleanly, so make them chunkier.
- **The N20 is small.** Keep the model light (thin shells, 10–15% infill), use a low-RPM gearbox, and expect it to
  crawl rather than tow anything.
- **Printed mechanics wear.** Printed gears and bushings are OK for a toy, but a Ø3 steel axle in a printed hole lasts longer than a printed axle.
- **Branding.** John Deere green/yellow and logos are fine on your own model, but they're trademarks, so don't sell files or models with them.
