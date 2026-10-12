"""Procedurally build pixel-styled UI art for Gate to Hell in Blender.

Run inside Blender (from the repository root):

    blender -b -P scripts/blender/build_ui.py -- all

or drive it from a live Blender session:

    import importlib, sys
    sys.path.insert(0, "scripts/blender")
    import build_ui; importlib.reload(build_ui)
    build_ui.setup()
    build_ui.render("button")

Everything is modelled from a handful of flat-shaded, bevelled primitives and
rendered with an orthographic top-down camera using the game's palette, so the
result reads as hand-made 2D game UI. Nothing here touches the Bailiff file's
own scene.
"""

import math
import os
import sys

import bpy
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(REPO, "assets", "ui")

# Collection every generated object is linked into (set by setup()).
COLL = None

# When True every material emits its exact palette colour, giving flat,
# pixel-clean art with no lighting gradients. Set False for shaded 3D previews.
FLAT = True

# Gate to Hell palette (linear sRGB values fed to Principled base colours).
C = {
    "gold_hi": (1.00, 0.86, 0.48),
    "gold": (0.86, 0.62, 0.20),
    "gold_dk": (0.40, 0.26, 0.07),
    "teal": (0.09, 0.28, 0.27),
    "teal_hi": (0.19, 0.45, 0.41),
    "teal_dk": (0.04, 0.13, 0.14),
    "ink": (0.028, 0.055, 0.062),
    "ink_hi": (0.07, 0.13, 0.14),
    "felt": (0.05, 0.14, 0.14),
    "ember": (1.00, 0.42, 0.12),
    "wood": (0.20, 0.10, 0.055),
    "wood_dk": (0.09, 0.045, 0.025),
    "bone": (0.90, 0.85, 0.68),
    "grey": (0.28, 0.31, 0.30),
    "grey_dk": (0.10, 0.12, 0.12),
}


def _mat(name, color, rough=0.65, metal=0.0, emis=None, strength=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    if FLAT:
        # Flat pixel look: the surface emits its exact palette colour, no shading.
        bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = 1.0
        bsdf.inputs["Emission Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Emission Strength"].default_value = 1.0
        return m
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emis is not None:
        bsdf.inputs["Emission Color"].default_value = (emis[0], emis[1], emis[2], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return m


def mat(key, **kw):
    """Fetch/create a palette material by key (see C)."""
    return _mat("ui_" + key, C[key], **kw)


def _box(name, size, loc, material, bevel=0.02, segments=2, collection=None):
    w, h, d = size
    v = [
        (-0.5, -0.5, -0.5),
        (0.5, -0.5, -0.5),
        (0.5, 0.5, -0.5),
        (-0.5, 0.5, -0.5),
        (-0.5, -0.5, 0.5),
        (0.5, -0.5, 0.5),
        (0.5, 0.5, 0.5),
        (-0.5, 0.5, 0.5),
    ]
    v = [(x * w, y * h, z * d) for x, y, z in v]
    f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.data.materials.append(material)
    if bevel > 0:
        b = ob.modifiers.new("bev", "BEVEL")
        b.width = bevel
        b.segments = segments
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(50)
    (collection or COLL).objects.link(ob)
    return ob


def _prism(name, radius, depth, sides, loc, material, bevel=0.008, collection=None):
    v = []
    for i in range(sides):
        a = math.tau * i / sides
        v.append((math.cos(a) * radius, math.sin(a) * radius, -depth / 2))
    for i in range(sides):
        a = math.tau * i / sides
        v.append((math.cos(a) * radius, math.sin(a) * radius, depth / 2))
    f = [tuple(range(sides - 1, -1, -1)), tuple(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        f.append((i, j, j + sides, i + sides))
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.data.materials.append(material)
    if bevel > 0:
        b = ob.modifiers.new("bev", "BEVEL")
        b.width = bevel
        b.segments = 2
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(50)
    (collection or COLL).objects.link(ob)
    return ob


def _diamond(name, rx, ry, depth, loc, material, bevel=0.01, collection=None):
    v = [(0, -ry, 0), (rx, 0, 0), (0, ry, 0), (-rx, 0, 0)]
    v = v + [(x, y, z + depth) for (x, y, z) in v]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.data.materials.append(material)
    if bevel > 0:
        b = ob.modifiers.new("bev", "BEVEL")
        b.width = bevel
        b.segments = 2
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(50)
    (collection or COLL).objects.link(ob)
    return ob


# --------------------------------------------------------------------------
# Scene setup
# --------------------------------------------------------------------------


def setup():
    """Create a dedicated, clean 'UIArt' scene and return it."""
    global COLL
    scene = bpy.data.scenes.get("UIArt")
    if scene is None:
        scene = bpy.data.scenes.new("UIArt")
    # Wipe everything in the UI scene so re-runs are deterministic.
    for ob in list(scene.collection.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for child in list(scene.collection.children):
        for ob in list(child.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(child)
    try:
        bpy.context.window.scene = scene
    except Exception:
        pass
    COLL = bpy.data.collections.new("UIArtObjs")
    scene.collection.children.link(COLL)
    scene.world = bpy.data.worlds.get("UIWorld") or bpy.data.worlds.new("UIWorld")
    scene.world.use_nodes = True
    bg = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.02, 0.035, 0.04, 1.0)
    bg.inputs[1].default_value = 0.35
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 1
    scene.render.filter_size = 0.0
    scene.render.dither_intensity = 0.0 if FLAT else 1.0
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    # Raw = store the render buffer directly, so flat emission colours land on
    # disk byte-for-byte as the palette values (no sRGB re-encode).
    scene.view_settings.view_transform = "Raw" if FLAT else "Standard"
    scene.view_settings.look = "None"

    cam_data = bpy.data.cameras.new("UICam")
    cam_data.type = "ORTHO"
    cam = bpy.data.objects.new("UICam", cam_data)
    cam.location = (0, 0, 4)
    cam.rotation_euler = (0, 0, 0)
    scene.collection.objects.link(cam)
    scene.camera = cam

    for name, loc, rot, energy, color in [
        ("UIKey", (2.0, -2.4, 3.0), (math.radians(35), 0, math.radians(40)), 3.2, (1.0, 0.95, 0.85)),
        ("UIFill", (-2.4, -1.6, 2.2), (math.radians(30), 0, math.radians(-55)), 1.0, (0.55, 0.75, 0.75)),
        ("UIRim", (-0.5, 2.6, 2.0), (math.radians(-40), 0, math.radians(190)), 1.2, (1.0, 0.6, 0.3)),
    ]:
        ld = bpy.data.lights.new(name, "SUN")
        ld.energy = energy
        ld.color = color
        ld.angle = math.radians(6)
        lo = bpy.data.objects.new(name, ld)
        lo.location = loc
        lo.rotation_euler = rot
        scene.collection.objects.link(lo)

    _mat("world_floor", (0.05, 0.14, 0.14), rough=0.9)
    return scene


def _render(path, rx, ry, ortho, transparent=True):
    scene = bpy.data.scenes["UIArt"]
    scene.render.resolution_x = rx
    scene.render.resolution_y = ry
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = transparent
    scene.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    scene.camera.data.ortho_scale = ortho
    scene.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print("wrote", path)


# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------


def stack(prefix, specs, dz=0.03, z0=0.0, bevel=0.006):
    """Concentric flat plates; specs are (palette_key, width, height) outermost first."""
    for i, (key, w, h) in enumerate(specs):
        _box("%s%d" % (prefix, i), (w, h, dz), (0, 0, z0 + dz / 2 + i * dz), mat(key), bevel=bevel)


def _button(state):
    if state == "disabled":
        specs = [("grey_dk", 1.00, 0.50), ("grey", 0.93, 0.43), ("grey_dk", 0.86, 0.36), ("ink", 0.72, 0.24)]
        stud = "grey"
    elif state == "hover":
        specs = [("gold_hi", 1.00, 0.50), ("gold", 0.93, 0.43), ("teal_hi", 0.86, 0.36), ("ink", 0.72, 0.24)]
        stud = "ember"
    else:
        specs = [("gold_dk", 1.00, 0.50), ("gold", 0.93, 0.43), ("teal", 0.86, 0.36), ("ink", 0.72, 0.24)]
        stud = "gold_hi"
    stack("bt", specs, dz=0.03)
    for sx in (-1, 1):
        for sy in (-1, 1):
            _diamond("stud_%d_%d" % (sx, sy), 0.035, 0.035, 0.03, (sx * 0.42, sy * 0.16, 0.16), mat(stud), bevel=0.004)


def _panel():
    stack("pn", [("gold_dk", 1.00, 1.00), ("gold", 0.95, 0.95), ("teal_dk", 0.90, 0.90), ("ink", 0.82, 0.82)], dz=0.03)
    for sx in (-1, 1):
        for sy in (-1, 1):
            _diamond(
                "pcorner_%d_%d" % (sx, sy), 0.06, 0.06, 0.03, (sx * 0.44, sy * 0.44, 0.16), mat("gold_hi"), bevel=0.004
            )


def _card():
    stack("cd", [("gold_dk", 0.80, 1.00), ("gold", 0.75, 0.95), ("teal", 0.68, 0.88), ("teal_dk", 0.60, 0.78)], dz=0.03)
    _box("cbanner", (0.54, 0.10, 0.03), (0, 0.36, 0.14), mat("gold"), bevel=0.004)
    _box("cplaque", (0.30, 0.06, 0.03), (0, 0.36, 0.17), mat("gold_hi"), bevel=0.004)
    _diamond("cgemtop", 0.05, 0.06, 0.03, (0, 0.46, 0.16), mat("gold_hi"), bevel=0.004)
    _diamond("cgem", 0.09, 0.12, 0.03, (0, -0.34, 0.16), mat("gold"), bevel=0.004)
    _diamond("cgemcore", 0.04, 0.055, 0.03, (0, -0.34, 0.19), mat("ember"), bevel=0.004)


def _cardback():
    stack("kb", [("gold_dk", 0.80, 1.00), ("gold", 0.75, 0.95), ("teal_dk", 0.68, 0.88)], dz=0.03)
    _diamond("kframe", 0.52, 0.66, 0.03, (0, 0, 0.12), mat("gold_dk"), bevel=0.004)
    _diamond("kwin", 0.46, 0.58, 0.03, (0, 0, 0.15), mat("teal_dk"), bevel=0.004)
    _diamond("kemblem", 0.26, 0.32, 0.03, (0, 0, 0.18), mat("gold"), bevel=0.004)
    _diamond("kcore", 0.13, 0.16, 0.03, (0, 0, 0.21), mat("ember"), bevel=0.004)


def _slot():
    stack("sl", [("teal_dk", 1.00, 1.00), ("ink", 0.86, 0.86)], dz=0.03)
    for sx in (-1, 1):
        for sy in (-1, 1):
            _diamond("sbolt_%d_%d" % (sx, sy), 0.035, 0.035, 0.03, (sx * 0.44, sy * 0.44, 0.12), mat("gold_dk"), bevel=0.003)


def _emblem():
    _diamond("emb", 0.50, 0.62, 0.16, (0, 0, 0.08), mat("gold"), bevel=0.02)
    _diamond("embcore", 0.28, 0.36, 0.18, (0, 0, 0.12), mat("ember"), bevel=0.02)


def _build_backdrop(kind):
    """A dark felt table backdrop, optionally dressed for the title screen."""
    _box("table", (2.4, 1.4, 0.05), (0, 0, 0), mat("felt"), bevel=0.0)
    _box("trim", (2.22, 1.22, 0.05), (0, 0, 0.015), mat("gold_dk"), bevel=0.0)
    _box("trim2", (2.16, 1.16, 0.05), (0, 0, 0.02), mat("felt"), bevel=0.0)
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (1, 1), (-1, 1), (0, 0)]):
        _diamond("motif%d" % i, 0.20, 0.26, 0.02, (sx * 0.62, sy * 0.38, 0.03), mat("teal_dk"), bevel=0.0)
    if kind == "title":
        # Scattered cards, a candle and floating cinders along the lower edge.
        for i, (x, y, rot) in enumerate([(-0.85, -0.42, 14), (-0.55, -0.30, -22), (-0.70, -0.18, 6)]):
            c = _box("bgcard%d" % i, (0.30, 0.42, 0.02), (x, y, 0.05), mat("bone"), bevel=0.005)
            c.rotation_euler = (0, 0, math.radians(rot))
        _prism("candle", 0.06, 0.30, 16, (0.92, -0.5, 0.16), mat("bone"))
        _box("flame", (0.05, 0.05, 0.10), (0.92, -0.5, 0.36), mat("ember"), bevel=0.005)
        for i, (x, y, z) in enumerate([(0.4, 0.5, 0.3), (0.9, 0.2, 0.5), (0.2, -0.55, 0.4), (1.05, 0.6, 0.35)]):
            _box("cinder%d" % i, (0.035, 0.035, 0.035), (x, y, z), mat("ember"), bevel=0.004)


def _clear():
    for ob in list(COLL.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def render(name):
    scene = bpy.data.scenes["UIArt"]
    _clear()
    if name == "button":
        _button("normal")
        _render(os.path.join(OUT, "button.png"), 128, 64, 1.28)
    elif name == "button_hover":
        _button("hover")
        _render(os.path.join(OUT, "button_hover.png"), 128, 64, 1.28)
    elif name == "button_disabled":
        _button("disabled")
        _render(os.path.join(OUT, "button_disabled.png"), 128, 64, 1.28)
    elif name == "panel":
        _panel()
        _render(os.path.join(OUT, "panel.png"), 160, 160, 1.25)
    elif name == "card":
        _card()
        _render(os.path.join(OUT, "card.png"), 176, 226, 1.28)
    elif name == "cardback":
        _cardback()
        _render(os.path.join(OUT, "cardback.png"), 176, 226, 1.28)
    elif name == "slot":
        _slot()
        _render(os.path.join(OUT, "slot.png"), 128, 128, 1.15)
    elif name == "emblem":
        _emblem()
        _render(os.path.join(OUT, "emblem.png"), 64, 64, 1.3)
    elif name == "bg":
        _build_backdrop("screen")
        _render(os.path.join(OUT, "bg_screen.png"), 1280, 720, 2.4, transparent=False)
    elif name == "bg_title":
        _build_backdrop("title")
        _render(os.path.join(OUT, "bg_title.png"), 1280, 720, 2.4, transparent=False)
    else:
        raise SystemExit("unknown asset: " + name)


ALL = ["button", "button_hover", "button_disabled", "panel", "card", "cardback", "slot", "emblem", "bg", "bg_title"]


def main():
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else ["all"]
    setup()
    names = ALL if args == ["all"] else args
    for n in names:
        render(n)
    print("DONE", names)


if __name__ == "__main__":
    main()
