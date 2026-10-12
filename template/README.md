# Fusion + Claude Code project template

Claude Code drives Autodesk Fusion through Fusion's built-in MCP server. For each part it writes a Python script,
runs it in your open design, checks the result with screenshots and a collision check, and exports a 3MF for your slicer.

This repo is a **template**. Each project is a copy that keeps a link back to it, so template improvements can be pulled into running projects.

## One-time setup (per PC)
1. **Enable the MCP server in Fusion.** Go to *Preferences* → *General* → *API* and tick **Fusion MCP Server** (default port **27182**).
   Click **Apply**, then restart Fusion.
2. **Open a design** in Fusion (File → New Design) and leave Fusion running.
3. **Start Claude Code in the project folder** (a new session, since `.mcp.json` is read at startup) and run `/mcp`.
   `fusion` should show as connected. If Fusion uses another port, change it in `.mcp.json`.

## Starting a new project
Don't use GitHub's "Use this template" button: it cuts the history, and then template updates won't merge.
GitHub also won't let you fork your own repo into the same account. Instead:
```sh
git clone <template-url> my-project
cd my-project
git remote rename origin template      # the template stays reachable as "template"
# create an EMPTY repo for the project on GitHub (no README), then:
git remote add origin <project-url>
git push -u origin master
```
Then in Claude Code: run **`/kickoff`**, print the fit test, and build parts with **`/new-part <name>`**.

## Pulling template updates into a project
```sh
git fetch template
git merge template/master
```
This merges cleanly as long as the ownership rule holds. Template-owned files are only changed in the template repo.
Project-owned files are only changed in the project.

| Template-owned | Project-owned |
|---|---|
| `template/**` | `CLAUDE.md`, `README.md` |
| `.claude/skills/{kickoff,new-part,fit-fix}/` | `layout.py`, `hardware.md`, `decisions.md` |
| `.claude/settings.json`, `.mcp.json`, `.gitignore` | `parts/**`, `reference/**` |

How each kind of change stays inside its owner's files:
- **Project permissions:** `.claude/settings.local.json` (git-ignored).
- **Project skills:** `.claude/skills/<own-name>/`.
- **Project helpers:** `parts/_lib/`.
- **Fit values:** `layout.py` `FIT` holds only the project's overrides. Defaults live in `template/lib/fusion_helpers.py`.
- **Fit-test rows:** `layout.py` `FIT_TEST_HOLES`.
- **Rules:** `CLAUDE.md` only imports `@template/RULES.md` and adds the project's own section, so new rules arrive with the merge.

If you improve something template-owned while working on a project: copy the change into the template repo, commit it
there, and merge it back into the project as above. Never commit it in the project directly.

**Changing the template itself:** keep project-owned stubs (`layout.py`, `CLAUDE.md`, ...) stable. Projects have already
filled them in, so changing a stub *will* conflict. New settings get a default in template code (e.g. `FIT_DEFAULTS`,
`getattr(L, "NEW_THING", default)`) instead of a new required entry in `layout.py`.

## Repo layout
| Path | What |
|---|---|
| `template/RULES.md` | Rules Claude follows (imported by `CLAUDE.md`) |
| `template/lib/fusion_helpers.py` | mm-based helpers: sketches, extrudes, fast solids, collision check, lock parts, fits, export |
| `template/lib/gears.py` | Involute gears, D-bores, generated crown (face) gears |
| `template/assembly.py` | Builds all parts, locks them together, reports collisions |
| `template/fit_test.py` | Clearance test print |
| `.claude/skills/` | `/kickoff`, `/new-part`, `/fit-fix` |
| `CLAUDE.md` | Imports the rules, plus this project's summary |
| `layout.py` | **The project's shared numbers:** sizes, part positions, connection points, fit overrides |
| `parts/<name>/` | One script per part |
| `decisions.md` | Why big choices were made, their risks, plan B |
| `hardware.md` | Real sizes of bought parts |
| `reference/` | Photos and real-world sizes |
| `exports/` | Generated 3MF/STL (not committed) |

## Limitations
- **Boxy is easy, curvy is hard.** Brackets, housings, gears and frames come out well. Organic shapes come out blocky
  or lofted, so sculpt those by hand in Fusion's Form workspace if needed.
- **Claude sees only screenshots and numbers.** The collision check catches clashes, but you judge looks.
- **Fusion must be open**, and the connection is local to this PC. Scripts edit the active design, so keep one design per project and save it now and then.
- **Bought-part libraries** (McMaster, fasteners) are dialogs in Fusion, not available to scripts. Download a STEP into
  `reference/hardware/` and Claude can import it, or Claude models a simple stand-in.
- **Script approval:** you approve each script run by default. To skip prompts in one project, allow
  `mcp__fusion__fusion_mcp_execute` in `.claude/settings.local.json`.
- **FDM detail limit:** features thinner than ~0.8 mm won't print cleanly.
