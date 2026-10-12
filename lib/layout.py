"""Project layout: the single source of truth for how parts fit together.

Every part script imports this. Positions, connection points and fits live HERE,
never hard-coded inside a part, so two parts that bolt together always agree.

Conventions: millimetres. X = across (left/right), Y = forward, Z = up.
Origin: pick one meaningful point per project (e.g. ground under the rear axle) and write it here.
ORIGIN = "..."
"""

# Printer / material fits. Tune these from the fit-test print (parts/_fit-test), not per part.
FIT = {
    "clearance": 0.2,    # sliding fit, per side
    "press": 0.0,        # added to a hole diameter for a press fit (bearings, pins)
    "m2_tap": 1.8,
    "m2_clear": 2.2,
    "m3_tap": 2.7,
    "m3_clear": 3.2,
    "wall": 1.6,         # default wall
    "detail_min": 0.8,   # smallest printable feature
}

# Overall sizes and positions (filled in by /kickoff), e.g.
#   "length": 480, "width": 250, "wheelbase": 260, "axle_z": 90
MAIN = {}

# Connection points between parts. Both sides of a joint read the same entry. Example:
#   "axle_to_chassis": {"screw": "M3", "holes": [(-30, 0, 30), (30, 0, 30)]},
INTERFACES = {}

# Part scripts in build order (repo-relative). assembly.py builds, locks and collision-checks these.
PARTS = [
    # "parts/chassis/chassis.py",
]
