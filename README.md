# Fusion + Claude Code project template

<!-- PROJECT-OWNED. In a project, /kickoff replaces this title and intro with the project's own description.
     The template should rarely change this file (projects rewrite it), so keep detailed docs in template/README.md. -->

Claude Code drives Autodesk Fusion through Fusion's built-in MCP server. For each part it writes a Python script,
runs it in your open design, checks the result with screenshots and a collision check, and exports a 3MF for your slicer.

This repo is a **template**. Each project is a copy that keeps a link back to it, so template improvements can be
pulled into running projects without merge conflicts.

## Start a new project
Don't use GitHub's **"Use this template"** button: it creates a repo with unrelated history, so template updates will
never merge cleanly. GitHub also won't let you fork your own repo into the same account. Clone instead:

```sh
git clone <template-url> my-project
cd my-project
git remote rename origin template          # the template stays reachable as "template"
# create an EMPTY repo for the project on GitHub (no README, no license), then:
git remote add origin <project-url>
git push -u origin master
```

Then:
1. Open Fusion with a new design. Start Claude Code in `my-project` and check `/mcp` shows `fusion` connected
   (first time on this PC: see [template/README.md](template/README.md#one-time-setup-per-pc)).
2. Run **`/kickoff`**. Claude asks what you're building, checks the key hardware with numbers, fills in the project
   files, and builds a rough blocks model of the whole thing.
3. Print the fit test and tell Claude which holes fit. Use **`/fit-fix`** to record it.
4. Build parts with **`/new-part <name>`**. Fix real-world fit problems with **`/fit-fix <what's wrong>`**.

## Pull template updates into a project
```sh
git fetch template
git merge template/master
```
That's it, as long as the ownership rule below has been respected.

## Who owns which file
Every file has exactly one owner. Template files are only ever changed **in the template repo**. Project files are
only ever changed **in the project**. Git then never sees both sides edit the same file, so merges are clean.

| Template-owned (change only in the template repo) | Project-owned (template ships a stub, then never touches it) |
|---|---|
| `template/**`: rules, helpers, gears, assembly, fit test | `CLAUDE.md`: imports `@template/RULES.md`, plus `## Project` |
| `.claude/skills/kickoff`, `new-part`, `fit-fix` | `README.md` (this file) |
| `.claude/settings.json`, `.mcp.json`, `.gitignore` | `layout.py`, `hardware.md`, `decisions.md` |
| | `parts/**`, `reference/**` |

Where project-specific things go, so they never touch template files:

| You want to… | Put it in |
|---|---|
| Change a printer fit (hole sizes, clearance) | `layout.py` → `FIT` (only the keys that differ from the defaults) |
| Test your own hardware on the fit-test print | `layout.py` → `FIT_TEST_HOLES` |
| Add a project rule for Claude | `CLAUDE.md`, below `## Project` |
| Allow tools / skip permission prompts | `.claude/settings.local.json` (git-ignored) |
| Add a helper used by several parts | `parts/_lib/` |
| Add a workflow skill | `.claude/skills/<new-name>/` |

### Improving the template from inside a project
Found a bug in a template helper, or a better rule? Don't commit it in the project.
1. Make the change in the **template repo** and commit it there.
2. In the project: `git fetch template` then `git merge template/master`.

Claude follows the same rule: it never edits `template/` inside a project. It tells you what should change instead.

### Changing the template safely
- Projects have already filled in their stubs (`layout.py`, `CLAUDE.md`, `README.md`, ...). Changing a stub **will** conflict, so leave them alone.
- New settings get a default in template code (like `FIT_DEFAULTS` in `template/lib/fusion_helpers.py`, or
  `getattr(L, "NEW_SETTING", default)`), never a new required entry in `layout.py`.
- Keep renames and moves of template files rare. Every project has to follow them.

### If a merge conflicts anyway
It means a file was edited on both sides. Usually that's a template file changed inside a project.
- **Template-owned file:** take the template's version (`git checkout --theirs <file>`), then redo the project's change the proper way (see the table above).
- **Project-owned file:** keep the project's version (`git checkout --ours <file>`).

Then `git add <file>` and `git commit` to finish the merge.

## More
Setup, workflow, repo layout and limitations: [template/README.md](template/README.md).
