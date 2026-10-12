"""Gear geometry for part scripts.

Outlines are plain 2D point lists (mm) around the gear centre. Map them into a sketch plane
with to_model() and draw them with fh.polygon(). generate_face_gear() works on temporary
B-Rep bodies only (no timeline features).

Typical crown + pinion (90 deg drive):
    pts = gears.involute_outline(12, 1.25, thin=0.15)                 # printed pinion, with backlash
    cut = gears.involute_outline(12, 1.25, tip=7.5 + 1.25 * 1.25)     # cutter: full teeth, deeper tip
    ... extrude both, fh.copy() the cutter body ...
    ring = gears.generate_face_gear(cutter, ...)
"""
import math

import fusion_helpers as fh


def involute_outline(teeth, module, pressure_angle=20.0, thin=0.0, tip=None, steps=8):
    """Closed involute spur gear outline, centred on (0, 0), tooth 0 pointing to -u.

    thin: removed from the tooth thickness at the pitch circle (backlash).
    tip:  tip radius; default pitch radius + 1 module.
    """
    n, m = teeth, module
    rp = m * n / 2
    alpha = math.radians(pressure_angle)
    rb = rp * math.cos(alpha)
    r_root = rp - 1.25 * m
    r_tip = tip if tip is not None else rp + m

    def inv(a):
        return math.tan(a) - a

    half = (math.pi * m / 2 - thin) / (2 * rp) + inv(alpha)  # tooth half-angle at the base circle

    def flank(r):
        return half if r <= rb else half - inv(math.acos(rb / r))

    def polar(r, a):
        return (r * math.cos(a), r * math.sin(a))

    r0 = max(r_root, rb)
    pts = []
    for k in range(n):
        c = math.pi + 2 * math.pi * k / n
        if r_root < rb:
            pts.append(polar(r_root, c - half))
        for i in range(steps + 1):
            r = r0 + (r_tip - r0) * i / steps
            pts.append(polar(r, c - flank(r)))
        a0, a1 = c - flank(r_tip), c + flank(r_tip)
        pts += [polar(r_tip, a0 + (a1 - a0) * j / 3) for j in (1, 2)]
        for i in range(steps, -1, -1):
            r = r0 + (r_tip - r0) * i / steps
            pts.append(polar(r, c + flank(r)))
        if r_root < rb:
            pts.append(polar(r_root, c + half))
        a0, a1 = c + flank(r0), c + 2 * math.pi / n - flank(r0)
        pts += [polar(r_root, a0 + (a1 - a0) * j / 3) for j in (1, 2)]
    return pts


def d_bore(d, flat, steps=16):
    """D-shaped bore outline (e.g. N20 / TT motor shafts), flat towards +v.

    flat: distance across the flat (e.g. 2.5 for an N20 Ø3 shaft).
    """
    r = d / 2
    a1 = math.asin((flat - r) / r)
    return [(r * math.cos(a), r * math.sin(a))
            for a in ((math.pi - a1) + (math.pi + 2 * a1) * i / steps for i in range(steps + 1))]


def to_model(pts2d, origin, u_axis, v_axis):
    """Map 2D (u, v) points into model space: origin + u * u_axis + v * v_axis (all mm)."""
    return [tuple(o + u * a + v * b for o, a, b in zip(origin, u_axis, v_axis)) for u, v in pts2d]


def generate_face_gear(cutter, ratio, cutter_axis, cutter_origin, teeth, r_in, r_out, x0, x1,
                       step=1.0, sector_axis_angle=0.0):
    """Face (crown) gear teeth on a gear turning about the X axis, cut by rolling `cutter`.

    cutter:        temporary body of the mating pinion at its assembled position, with full-thickness
                   teeth and a tip ~0.25 module longer than the real pinion (gives root clearance).
                   Make the real pinion thinner (involute_outline thin=...) for backlash.
    ratio:         crown teeth / pinion teeth.
    cutter_axis:   pinion axis direction, e.g. (0, 1, 0). Its sense sets the rolling direction:
                   if the result is chewed up, flip it.
    cutter_origin: a point on the pinion axis (mm).
    r_in, r_out:   tooth band radii. x0, x1: axial extent of the tooth ring (x0 = slab under the gaps).
    sector_axis_angle: angle (deg, from +Y towards +Z) at which the cutter sits; a gap is cut there.
    Returns the ring of teeth (union it with your web/hub).
    """
    pitch = 360.0 / teeth
    a0 = sector_axis_angle

    def halfspace(theta_deg, above):
        t = math.radians(theta_deg)
        n = (0, -math.sin(t), math.cos(t))
        s = 1 if above else -1
        R = 2 * r_out + 20
        c = ((x0 + x1) / 2, s * n[1] * R / 2, s * n[2] * R / 2)
        return fh.obox(c, (1, 0, 0), (0, math.cos(t), math.sin(t)), abs(x1 - x0) + 2, 2 * R, R)

    # One tooth: gap centre to gap centre, plus a little overlap so the copies fuse.
    tooth = fh.cyl((x0, 0, 0), (x1, 0, 0), 2 * r_out)
    fh.subtract(tooth, fh.cyl((x0 - 1, 0, 0), (x1 + 1, 0, 0), 2 * r_in))
    fh.intersect(tooth, halfspace(a0 - 0.1 * pitch, True), halfspace(a0 + 1.1 * pitch, False))

    # Gear turns phi, pinion turns ratio * phi. In the gear's frame the pinion spins, then orbits by -phi.
    phi0, phi1 = -2.7 * pitch, 1.7 * pitch
    n = int(round((phi1 - phi0) / step))
    for i in range(n + 1):
        phi = phi0 + (phi1 - phi0) * i / n
        c = fh.copy(cutter)
        fh.rotate(c, ratio * phi, cutter_axis, cutter_origin)
        fh.rotate(c, -phi, (1, 0, 0))
        fh.subtract(tooth, c)

    ring = fh.copy(tooth)
    for k in range(1, teeth):
        fh.union(ring, fh.rotate(fh.copy(tooth), k * pitch, (1, 0, 0)))
    return ring
