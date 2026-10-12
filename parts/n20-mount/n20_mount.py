"""N20 gear motor cradle - smoke-test part for the Claude <-> Fusion pipeline.

Motor axis runs along Y. The motor slides into a rectangular slot and is held by
friction (add a zip tie or a drop of hot glue if it wiggles).
Print orientation: flange flat on the bed, no supports.
"""
import importlib
import sys

sys.path.insert(0, r"D:\programming\fusion-mcp-test\lib")
import fusion_helpers as fh  # noqa: E402

importlib.reload(fh)

# All sizes in mm. Change here and re-run - the component is rebuilt from scratch.
P = {
    "motor_w": 12.0,   # N20 body width
    "motor_h": 10.0,   # N20 body height (across the flats)
    "clearance": 0.2,  # per side
    "wall": 1.6,
    "base_t": 2.0,     # flange / floor thickness
    "length": 12.0,    # how much of the gearbox the cradle grips
    "ear": 7.0,        # flange width beyond the housing, each side
    "hole_d": 3.2,     # M3 clearance
}


def run(context):
    comp = fh.fresh_component("n20_mount")

    slot_half = P["motor_w"] / 2 + P["clearance"]
    outer_half = slot_half + P["wall"]
    slot_top = P["base_t"] + P["motor_h"] + 2 * P["clearance"]
    outer_top = slot_top + P["wall"]
    flange_half = outer_half + P["ear"]

    # Flange
    sk = comp.sketches.add(comp.xZConstructionPlane)
    fh.rect(sk, (-flange_half, 0, 0), (flange_half, 0, P["base_t"]))
    fh.extrude(comp, sk.profiles.item(0), P["length"], op="new", symmetric=True)

    # Housing around the motor
    sk = comp.sketches.add(comp.xZConstructionPlane)
    fh.rect(sk, (-outer_half, 0, 0), (outer_half, 0, outer_top))
    fh.extrude(comp, sk.profiles.item(0), P["length"], op="join", symmetric=True)

    # Motor slot
    sk = comp.sketches.add(comp.xZConstructionPlane)
    fh.rect(sk, (-slot_half, 0, P["base_t"]), (slot_half, 0, slot_top))
    fh.extrude(comp, sk.profiles.item(0), op="cut", through_all=True)

    # Screw holes in the flange
    sk = comp.sketches.add(comp.xYConstructionPlane)
    hole_x = outer_half + P["ear"] / 2
    fh.circle(sk, (-hole_x, 0, 0), P["hole_d"])
    fh.circle(sk, (hole_x, 0, 0), P["hole_d"])
    fh.extrude(comp, fh.all_profiles(sk), op="cut", through_all=True)

    print(f"n20_mount built: {2 * flange_half:.1f} x {P['length']:.1f} x {outer_top:.1f} mm")
