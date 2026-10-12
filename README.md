# Fusion + Claude Code project template

Claude Code drives Autodesk Fusion through Fusion's built-in MCP server. For each part it writes a Python script,
runs it in your open design, checks the result with screenshots and a collision check, and exports a 3MF for your slicer.

This repo is a **template**: fork or copy it once per project.

## One-time setup (per PC)
1. **Enable the MCP server in Fusion.** Go to *Preferences* → *General* → *API* and tick **Fusion MCP Server** (default port **27182**).
   Click **Apply**, then restart Fusion.
2. **Open a design** in Fusion (File → New Design) and leave Fusion running.
3. **Start Claude Code in the project folder** (a new session, since `.mcp.json` is read at startup) and run `/mcp`.
   `fusion` should show as connected. If Fusion uses another port, change it in `.mcp.json`.

## Starting a new project
1. Fork or copy this repo and open it in VS Code / Claude Code.
2. Run **`/kickoff`**. Claude asks what you're building, does the sanity maths (will the motor cope, does it fit
   the bed), and fills in the project sections. Then it builds a rough "blocks" model of the whole thing for you to judge.
3. **Print the fit test** ([parts/_fit-test](parts/_fit-test/fit_test.py)) and tell Claude which holes fit. That tunes the clearances for every part.
4. Build parts one by one with **`/new-part <name>`**. Claude scripts the part, runs it, shows screenshots and checks collisions.
   You say what to change ("taller", "move the holes outward").
5. When something printed doesn't fit, use **`/fit-fix <what's wrong>`**. Claude changes the controlling number and tells you what to reprint.
6. Commit whenever a part is good. Git history is your undo across sessions.

## Repo layout
| Path | What |
|---|---|
| `CLAUDE.md` | Rules Claude follows, plus this project's summary (filled by `/kickoff`) |
| `lib/layout.py` | **The shared numbers:** overall sizes, part positions, connection points, printer fits |
| `lib/fusion_helpers.py` | mm-based helpers: sketches, extrudes, fast solids, collision check, lock parts, export |
| `lib/gears.py` | Involute gears, D-bores, generated crown (face) gears |
| `parts/<name>/` | One script per part. `_fit-test` ships with the template |
| `assembly.py` | Builds all parts, locks them together, reports collisions |
| `decisions.md` | Why big choices were made, their risks, plan B |
| `hardware.md` | Real sizes of bought parts (motors, bearings, screws) |
| `reference/` | Photos and real-world sizes of what's being modelled |
| `.claude/skills/` | `/kickoff`, `/new-part`, `/fit-fix` |
| `exports/` | Generated 3MF/STL (not committed) |

## Limitations
- **Boxy is easy, curvy is hard.** Brackets, housings, gears and frames come out well. Organic shapes come out blocky
  or lofted, so sculpt those by hand in Fusion's Form workspace if needed.
- **Claude sees only screenshots and numbers.** The collision check catches clashes, but you judge looks.
- **Fusion must be open**, and the connection is local to this PC. Scripts edit the active design, so keep one design per project and save it now and then.
- **Bought-part libraries** (McMaster, fasteners) are dialogs in Fusion, not available to scripts. Download a STEP into
  `reference/hardware/` and Claude can import it, or Claude models a simple stand-in.
- **Script approval:** you approve each script run by default. Allow `mcp__fusion__fusion_mcp_execute` in
  `.claude/settings.json` to skip the prompts once you trust the flow.
- **FDM detail limit:** features thinner than ~0.8 mm won't print cleanly.
