"""Project layout: the single source of truth for how this project's parts fit together.

PROJECT-OWNED: the template never changes this file after you copy it.
Every part script imports it. Positions, connection points and fit overrides live HERE,
never hard-coded inside a part, so two parts that bolt together always agree.

Conventions: millimetres. X = across (left/right), Y = forward, Z = up.
Origin: pick one meaningful point (e.g. ground under the main axle) and write it here.
ORIGIN = "..."
"""

# Fit overrides from the fit-test print. Only keys that differ from the template defaults
# (template/lib/fusion_helpers.py FIT_DEFAULTS), e.g. {"m3_tap": 2.6, "press": 0.05}.
FIT = {}

# Extra rows for the fit-test print (template/fit_test.py): this project's hardware, (label, diameter).
# Screw holes are always included. Labels: keep them short (≤ 6 characters).
FIT_TEST_HOLES = [
    # ("608 OD", 22.0), ("D8", 8.0),
]

# Overall sizes and positions (filled in by /kickoff), e.g.
#   "length": 480, "width": 250, "wheelbase": 260, "axle_z": 90
MAIN = {}

# Connection points between parts. Both sides of a joint read the same entry. Example:
#   "axle_to_chassis": {"screw": "M3", "holes": [(-30, 0, 30), (30, 0, 30)]},
INTERFACES = {}

# Part scripts in build order (repo-relative). template/assembly.py builds, locks and collision-checks these.
PARTS = [
    # "parts/chassis/chassis.py",
]
