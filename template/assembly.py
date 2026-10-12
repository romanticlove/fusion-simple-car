"""Build every part in layout.py PARTS, lock them together, and check for collisions.

Run it via the loader (see template/RULES.md) after changing layout.py or any part that touches another.
Prints every pair of bodies from different parts that overlap. Anything > ~0.01 mm^3 is a real clash.
"""
import importlib
import itertools
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path[:0] = [os.path.join(ROOT, "template", "lib"), ROOT]
import fusion_helpers as fh  # noqa: E402
import layout as L  # noqa: E402

importlib.reload(fh)
importlib.reload(L)

TOLERANCE = 0.01  # mm^3


def run(context):
    root = fh.design().rootComponent
    for path in L.PARTS:
        fh.run_script(path, context)
        print(f"built {path}")

    # Every top-level component in the design takes part (keep one design per project).
    built = list(dict.fromkeys(o.component.name for o in root.occurrences))
    fh.lock_assembly(built)

    bodies = {n: [b for o in root.occurrences if o.component.name == n for b in o.bRepBodies] for n in built}
    clashes = 0
    for a, b in itertools.combinations(built, 2):
        v = sum(fh.overlap_mm3(x, y) for x in bodies[a] for y in bodies[b])
        if v > TOLERANCE:
            clashes += 1
            print(f"CLASH {a} x {b}: {v:.2f} mm^3")
    print(f"assembly: {len(built)} components locked, {clashes} clashes")
