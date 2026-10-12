# Blender element particles

Nine transparent 1152×384 atlases, each with twelve 192×192 frames in six columns. Frame order is left to right, top to bottom. Geometry is rendered with an orthographic camera, at 20 fps (0.6-second burst). Runtime casts/impacts fit that animation to the existing feedback duration; projectiles and persistent fields cycle it. Gameplay timing and collision geometry are unchanged.

Pyro has rising flame ribbons and embers; Hydro has droplet shards and ripples; Anemo has spiral ribbons; Geo has angular fault lines and rock chunks; Dendro has leaf outlines; Cryo has ice stars and shards; Electro has jagged arcs; Gravity has contracting orbits; Antimatter has fractured rings and triangular shards.

Open `preview.html` for all nine animations and the icon library. Editable scenes and particle location/rotation/scale keys are in `art-src/blender/element-effects.blend`. Rebuild with `blender -b -t 4 -P scripts/blender/build_polish.py`. The same script renders 24 metal/enamel symbols into `assets/ui/icons.png`.

`src/render/effects.lua` caches at most nine small atlases (one per valid element). It clamps frame indices, ignores unknown elements, falls back when art is unavailable, and uses a dimmed fixed frame in reduced motion. Existing warning geometry stays visible. Run `python3 scripts/verify-polish.py` and `node scripts/browser-test.cjs --polish-only` after rebuilding the game.
