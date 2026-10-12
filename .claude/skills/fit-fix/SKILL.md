---
name: fit-fix
description: Fix a real-world fit problem reported after printing (too tight, too loose, hole misaligned, part collides, measured hardware differs) by changing the controlling number, rebuilding, and naming exactly what to reprint. Also used to record fit-test results. Use for /fit-fix or any "X doesn't fit / is loose / is tight" report.
---

# Fit fix

1. **Pin down the problem.** Which part and which feature? Get a measurement if possible (calipers: "hole is 15.9,
   bearing is 16.0"). If it's the fit-test print, ask which hole fits best in each row.
2. **Find the controlling number.** Search in this order:
   - `layout.py` FIT: printer-wide fit overrides (defaults are in template code; add the key here, never edit the template). If the same kind of fit is wrong on several parts, fix it here.
   - `hardware.md`: the bought part's real size is different from what we assumed. Update the row.
   - `layout.py` INTERFACES / MAIN: misaligned holes or positions between two parts.
   - the part's `P` dict: a one-off feature on that part only.
   Prefer the most global number that is actually wrong. Don't patch one part when the printer fit is the real cause.
3. **Change it.** Make the smallest change that fixes it (usually 0.1–0.2 mm for fits). Show the before and after values.
4. **Rebuild** the affected parts (every part that reads the changed number), run `template/assembly.py`, and screenshot if the geometry visibly changed.
5. **Tell the user what to reprint.** List only the parts whose printed geometry changed. If it's a fit, suggest printing only
   the affected region first (e.g. "cut the housing to just the bearing pocket in the slicer").
6. **Log it.** Add a line to `decisions.md` if it changes a FIT value or a hardware size, since later parts depend on it. Offer to commit.
