"""Small helpers shared by part scripts.

Fusion's API works in centimeters internally. Every helper here takes
millimeters and converts, so part scripts can think in mm only.

Part scripts (parts/<name>/<name>.py) import this with:
    LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib")
    sys.path.insert(0, os.path.normpath(LIB))
    import fusion_helpers as fh
    importlib.reload(fh)   # Fusion keeps its Python process alive between runs
"""
import math
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
    if op == "cut":
        inp.participantBodies = own_bodies(comp)
    if through_all:
        inp.setAllExtent(adsk.fusion.ExtentDirections.SymmetricExtentDirection)
    elif symmetric:
        inp.setSymmetricExtent(val(distance_mm), True)
    else:
        inp.setDistanceExtent(False, val(distance_mm))
    return ext.add(inp)


def own_bodies(comp):
    """The component's own bodies. Use as participantBodies so a cut never reaches into other parts."""
    return [b for b in comp.bRepBodies]


def all_profiles(sketch):
    col = adsk.core.ObjectCollection.create()
    for p in sketch.profiles:
        col.add(p)
    return col


def largest_profile(sketch):
    """The profile with the biggest area (e.g. a gear outline with its bore removed)."""
    return max(sketch.profiles, key=lambda p: p.areaProperties().area)


def polygon(sketch, pts):
    """Closed polyline through model-space points (mm)."""
    sp = [sketch.modelToSketchSpace(pt(p)) for p in pts]
    lines = sketch.sketchCurves.sketchLines
    first = prev = lines.addByTwoPoints(sp[0], sp[1])
    for p in sp[2:]:
        prev = lines.addByTwoPoints(prev.endSketchPoint, p)
    lines.addByTwoPoints(prev.endSketchPoint, first.startSketchPoint)


def plane_at(comp, axis, value_mm):
    """Construction plane perpendicular to `axis` ("x"|"y"|"z") at that model coordinate.

    Handles origin planes whose normal points the "wrong" way (XZ's normal is -Y).
    """
    base = {"x": comp.yZConstructionPlane, "y": comp.xZConstructionPlane, "z": comp.xYConstructionPlane}[axis]
    sign = getattr(base.geometry.normal, axis)
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(base, val(value_mm * sign))
    return comp.constructionPlanes.add(inp)


# --- Temporary B-Rep solids -------------------------------------------------
# Fast, feature-less solid modelling for primitive-heavy parts (housings, shafts).
# Build with these, then put the result into a component with add_body().

def pt(p):
    """Model-space point from an (x, y, z) tuple in mm."""
    return adsk.core.Point3D.create(*[mm(c) for c in p])


def vec(v):
    return adsk.core.Vector3D.create(*v)


def tbm():
    return adsk.fusion.TemporaryBRepManager.get()


def cyl(p0, p1, d):
    """Solid cylinder between two axis points (mm) with diameter d."""
    return tbm().createCylinderOrCone(pt(p0), mm(d) / 2, pt(p1), mm(d) / 2)


def obox(center, length_dir, width_dir, length, width, height):
    """Oriented box (mm). Height runs along length_dir x width_dir."""
    obb = adsk.core.OrientedBoundingBox3D.create(
        pt(center), vec(length_dir), vec(width_dir), mm(length), mm(width), mm(height))
    return tbm().createBox(obb)


def box(p0, p1):
    """Axis-aligned box from two opposite corners (mm)."""
    c = [(a + b) / 2 for a, b in zip(p0, p1)]
    s = [abs(b - a) for a, b in zip(p0, p1)]
    return obox(c, (1, 0, 0), (0, 1, 0), *s)


def hex_x(x0, x1, af):
    """Hexagonal prism along X from x0 to x1 (mm), `af` across the flats."""
    c = ((x0 + x1) / 2, 0, 0)
    body = None
    for k in range(3):
        a = math.radians(60 * k)
        b = obox(c, (1, 0, 0), (0, math.cos(a), math.sin(a)), abs(x1 - x0), af, 3 * af)
        body = b if body is None else intersect(body, b)
    return body


def _boolean(kind, target, tools):
    for t in tools:
        tbm().booleanOperation(target, t, kind)
    return target


def union(target, *tools):
    return _boolean(adsk.fusion.BooleanTypes.UnionBooleanType, target, tools)


def subtract(target, *tools):
    return _boolean(adsk.fusion.BooleanTypes.DifferenceBooleanType, target, tools)


def intersect(target, *tools):
    return _boolean(adsk.fusion.BooleanTypes.IntersectionBooleanType, target, tools)


def copy(body):
    return tbm().copy(body)


def rotate(body, deg, axis, origin=(0, 0, 0)):
    """Rotate a temporary body in place about an axis through `origin` (mm). Returns it."""
    m = adsk.core.Matrix3D.create()
    m.setToRotation(math.radians(deg), vec(axis), pt(origin))
    tbm().transform(body, m)
    return body


def overlap_mm3(a, b):
    """Volume (mm^3) where two bodies (real or temporary) intersect. ~0 means no interference."""
    t = copy(a)
    if not tbm().booleanOperation(t, copy(b), adsk.fusion.BooleanTypes.IntersectionBooleanType):
        return 0.0
    return t.volume * 1000.0


def add_body(comp, body, name):
    """Put a temporary body into `comp` (via a base feature in parametric designs)."""
    if design().designType == adsk.fusion.DesignTypes.ParametricDesignType:
        bf = comp.features.baseFeatures.add()
        bf.startEdit()
        comp.bRepBodies.add(body, bf)
        bf.finishEdit()
        b = bf.bodies.item(bf.bodies.count - 1)
    else:
        b = comp.bRepBodies.add(body)
    b.name = name
    return b


def run_script(path, context=None):
    """Load a part script by path (absolute or repo-relative) and call its run()."""
    import importlib.util
    if not os.path.isabs(path):
        path = os.path.join(REPO, path)
    spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(path))[0], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.run(context)
    return mod


def occurrence(name):
    """First root-level occurrence whose component is called `name` (or None)."""
    for occ in design().rootComponent.occurrences:
        if occ.component.name == name:
            return occ
    return None


def lock_assembly(names):
    """Ground the first named component and tie all of them into one rigid group.

    Stops parts being dragged apart in the viewport. Re-run after rebuilding parts,
    because fresh_component() deletes the old occurrences (and with them the group).
    """
    root = design().rootComponent
    for rg in list(root.rigidGroups):
        rg.deleteMe()
    occs = adsk.core.ObjectCollection.create()
    for n in names:
        occ = occurrence(n)
        if occ:
            occs.add(occ)
    if occs.count == 0:
        return None
    occs.item(0).isGrounded = True
    if occs.count > 1:
        return root.rigidGroups.add(occs, True)
    return None


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
