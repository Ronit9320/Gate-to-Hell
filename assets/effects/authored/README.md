# Selected DreamLayer combat FX

Byte-for-byte copies of author-provided transparent PNGs from
`release/fx-dreamlayer/raw/`: hit_burst, critical_burst, slash_arc and impact_wave.
`src/render/authored_fx.lua` animates scale, opacity and slash rotation in screen
space. The renderer loads at most four images, only when first used. Reduced
motion uses fixed size/orientation and lower opacity. Missing images fall back
to the existing combat sheets. These cutouts are never used for collision masks
or hazard telegraphs. No additional generation calls were made.

The fire explosion and generated sheet are left as source candidates: the
selected neutral feedback fits more heroes without obscuring elemental identity.
