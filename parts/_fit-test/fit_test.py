"""Fit-test coupon: one row of holes per nominal size, one column per offset.

Print it once per printer/material before any real part. For each row, find the hole that fits best
(a screw self-taps without splitting, a bearing presses in firmly, a shaft slides), then put
nominal + that offset into lib/layout.py FIT. Edit P["holes"] to test the hardware your project uses.

Print orientation: flat on the bed, labels up, no supports.
"""
import importlib
import os
import sys

import adsk.core
import adsk.fusion

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib")
sys.path.insert(0, os.path.normpath(LIB))
import fusion_helpers as fh  # noqa: E402
import layout as L  # noqa: E402

importlib.reload(fh)
importlib.reload(L)

# All sizes in mm. Change here and re-run - the component is rebuilt from scratch.
P = {
    "holes": [                       # (label, nominal diameter)
        ("M2 tap", L.FIT["m2_tap"]),
        ("M2 clr", L.FIT["m2_clear"]),
        ("M3 tap", L.FIT["m3_tap"]),
        ("M3 clr", L.FIT["m3_clear"]),
        ("D8", 8.0),
        ("D16", 16.0),
    ],
    "offsets": [-0.1, 0.0, 0.1, 0.2],
    "thickness": 4.0,
    "gap": 4.0,           # material between holes
    "label_w": 18.0,      # column for row labels
    "text_h": 3.5,
    "engrave": 0.4,
}


def label(comp, sk, text, x, y):
    """Engrave-ready text centred on (x, y) at the top face."""
    h = P["text_h"]
    w = 0.7 * h * len(text)
    inp = sk.sketchTexts.createInput2(text, fh.mm(h))
    inp.setAsMultiLine(
        sk.modelToSketchSpace(fh.pt((x - w / 2, y - h / 2, P["thickness"]))),
        sk.modelToSketchSpace(fh.pt((x + w / 2, y + h / 2, P["thickness"]))),
        adsk.core.HorizontalAlignments.CenterHorizontalAlignment,
        adsk.core.VerticalAlignments.MiddleVerticalAlignment, 0)
    return sk.sketchTexts.add(inp)


def run(context):
    comp = fh.fresh_component("fit_test")
    t, gap = P["thickness"], P["gap"]
    max_d = max(d for _, d in P["holes"]) + max(P["offsets"])
    col = max_d + gap
    head = P["text_h"] + gap                     # header row for offset labels
    rows = [max(d + max(P["offsets"]), P["text_h"]) + gap for _, d in P["holes"]]
    width = P["label_w"] + col * len(P["offsets"])
    depth = head + sum(rows)

    sk = comp.sketches.add(comp.xYConstructionPlane)
    fh.rect(sk, (0, 0, 0), (width, depth, 0))
    fh.extrude(comp, sk.profiles.item(0), t)

    # Holes; rows run from the top (high Y) down
    sk = comp.sketches.add(comp.xYConstructionPlane)
    centres = []
    y = depth - head
    for (_, d), rh in zip(P["holes"], rows):
        yc = y - rh / 2
        centres.append(yc)
        for i, off in enumerate(P["offsets"]):
            fh.circle(sk, (P["label_w"] + col * (i + 0.5), yc, 0), d + off)
        y -= rh
    fh.extrude(comp, fh.all_profiles(sk), op="cut", through_all=True)

    # Labels, engraved into the top
    sk = comp.sketches.add(fh.plane_at(comp, "z", t))
    texts = [label(comp, sk, name, P["label_w"] / 2, yc) for (name, _), yc in zip(P["holes"], centres)]
    texts += [label(comp, sk, f"{off:+.1f}" if off else "0", P["label_w"] + col * (i + 0.5), depth - head / 2)
              for i, off in enumerate(P["offsets"])]
    ext = comp.features.extrudeFeatures
    for txt in texts:
        inp = ext.createInput(txt, adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.participantBodies = fh.own_bodies(comp)
        inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(fh.val(P["engrave"])),
                             adsk.fusion.ExtentDirections.NegativeExtentDirection)
        ext.add(inp)

    print(f"fit_test built: {width:.0f} x {depth:.0f} x {t:.0f} mm, "
          f"{len(P['holes'])} sizes x offsets {P['offsets']}")
