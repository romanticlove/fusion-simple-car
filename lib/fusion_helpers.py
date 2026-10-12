"""Small helpers shared by part scripts.

Fusion's API works in centimeters internally. Every helper here takes
millimeters and converts, so part scripts can think in mm only.

Part scripts import this with:
    sys.path.insert(0, r"D:\\programming\\fusion-mcp-test\\lib")
    import fusion_helpers as fh
    importlib.reload(fh)   # Fusion keeps its Python process alive between runs
"""
import os

import adsk.core
import adsk.fusion

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS = os.path.join(REPO, "exports")


def mm(v):
    """Millimeters -> Fusion internal centimeters."""
    return v / 10.0


def val(v_mm):
    """ValueInput for a length in mm."""
    return adsk.core.ValueInput.createByReal(mm(v_mm))


def design():
    d = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    if not d:
        raise RuntimeError("No active Fusion design - open or create a design first.")
    d.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    return d


def fresh_component(name):
    """Return an empty component called `name`, deleting any previous one.

    Re-running a part script therefore rebuilds the part instead of stacking copies.
    """
    root = design().rootComponent
    old = [o for o in root.occurrences if o.component.name == name]
    for occ in old:
        occ.deleteMe()
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def rect(sketch, p0, p1):
    """Rectangle from two opposite corners given in model space (mm, (x, y, z)).

    Converting from model space avoids the XZ-plane axis flip in sketch coordinates.
    """
    a = sketch.modelToSketchSpace(adsk.core.Point3D.create(*[mm(c) for c in p0]))
    b = sketch.modelToSketchSpace(adsk.core.Point3D.create(*[mm(c) for c in p1]))
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(a, b)


def circle(sketch, center, diameter):
    """Circle at a model-space center (mm) with the given diameter (mm)."""
    c = sketch.modelToSketchSpace(adsk.core.Point3D.create(*[mm(v) for v in center]))
    sketch.sketchCurves.sketchCircles.addByCenterRadius(c, mm(diameter) / 2)


def extrude(comp, profiles, distance_mm=None, op="new", symmetric=False, through_all=False):
    """Extrude one profile or an ObjectCollection of profiles.

    op: "new" | "join" | "cut"
    """
    ops = {
        "new": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        "join": adsk.fusion.FeatureOperations.JoinFeatureOperation,
        "cut": adsk.fusion.FeatureOperations.CutFeatureOperation,
    }
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(profiles, ops[op])
    if through_all:
        inp.setAllExtent(adsk.fusion.ExtentDirections.SymmetricExtentDirection)
    elif symmetric:
        inp.setSymmetricExtent(val(distance_mm), True)
    else:
        inp.setDistanceExtent(False, val(distance_mm))
    return ext.add(inp)


def all_profiles(sketch):
    col = adsk.core.ObjectCollection.create()
    for p in sketch.profiles:
        col.add(p)
    return col


def export(comp, name, fmt="3mf"):
    """Export a component to exports/<name>.<fmt> ("3mf" or "stl"). Returns the path."""
    os.makedirs(EXPORTS, exist_ok=True)
    path = os.path.join(EXPORTS, f"{name}.{fmt}")
    em = design().exportManager
    if fmt == "stl":
        opts = em.createSTLExportOptions(comp, path)
        opts.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    elif fmt == "3mf":
        opts = em.createC3MFExportOptions(comp, path)
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    em.execute(opts)
    return path
