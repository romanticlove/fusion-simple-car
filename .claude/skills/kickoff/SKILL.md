---
name: kickoff
description: Start a new Fusion + 3D-print project in this repo - capture the goal, sanity-check the key hardware with numbers, fill CLAUDE.md / hardware.md / layout.py / decisions.md, and build a rough blocks model of the whole thing. Use when the user says /kickoff, "start a new project", or the CLAUDE.md "## Project" section is still empty.
---

# Kickoff

Goal: before any detailed part exists, everyone agrees on what is being built, that the key hardware can do the job,
and where every part sits and connects.

## 1. Ask (one AskUserQuestion round, max 4 questions; skip what the user already said)
- What is it, and what must it do? (e.g. RC model that drives, a bracket, an enclosure)
- Scale, if it's a model of something real. Do they have reference photos for `reference/photos/`?
- Key bought hardware: motors, servos, bearings, battery, electronics. Exact model if known.
- Printer and bed size, materials.

## 2. Numbers check (before modelling anything)
For each key component, do the quick maths and show it in a few lines:
- moving things: weight estimate, required torque/force (with margin for slopes or friction), speed, and how it compares with the component's spec (use ~1/3 of stall torque as usable)
- size: does it fit inside the scaled envelope, and do the parts fit the bed
- power: battery voltage/current against the motors

If something is marginal, say so plainly and propose a plan B. Log every key choice in `decisions.md` (why / risk / plan B).

## 3. Fill the project files
- `CLAUDE.md` → `## Project` section.
- `hardware.md` → one row per bought part with real sizes (mark "approx., measure").
- `reference/README.md` → real-world size table (real plus scaled), if it's a model.
- `layout.py` →
  - `ORIGIN` description
  - `MAIN` (overall sizes, axle/part positions)
  - first `INTERFACES` (how the major parts connect: screw size and hole coordinates)
  - planned `PARTS` order
  - Leave `FIT` empty until the fit test is printed.

## 4. Blocks model
Write `parts/_blocks/blocks.py`: one component `blocks` with simple solids (fh.cyl / fh.box) for every major
part and bought component, positioned from `layout.py`. Run it via the loader in template/RULES.md. Take an iso screenshot plus
the side/top views that matter, compare them with the reference photos, and adjust `layout.py` with the user until the proportions look right.

## 5. Hand-off
- Tell the user to print the fit test (`template/fit_test.py`) first. Add the project's real hardware sizes (bearing OD, shaft Ø, motor body) to `layout.FIT_TEST_HOLES`, then run it.
- Suggest the first part to build with `/new-part`, usually the one most other parts connect to (chassis, frame, base).
- Offer to commit.
