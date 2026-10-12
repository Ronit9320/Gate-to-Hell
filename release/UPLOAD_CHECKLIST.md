# Upload package — v0.9.0

Prepared for the author's upload; nothing has been published or submitted.

1. Replace artwork if desired using ART_REPLACEMENT.md, then rebuild and repeat browser checks. The default build includes all Blender heroes, bosses, Hell appearances, combat effects and scenery. Older flat portraits remain excluded. Open `assets/art-preview.html` to review the library.
2. Create/edit an itch.io project, choose **HTML Game**, and upload `dist/house-of-cinders-web.zip`. It contains root `index.html` and all runtime dependencies. Select the upload for browser play.
3. Prefer click-to-launch fullscreen on small displays. For a large embedded view, use **1280 × 760** (720 game pixels plus 40-pixel header), Click to Play, no scrollbars, and leave Mobile Friendly off. The canvas scales to fit.
4. Copy the listing from ITCH_PAGE.md. Use the new `cover-blender.png` (630 × 500), or the preserved `cover.png` and the actual gameplay images in `screenshots/`; use the new `art-*.png` captures for the current Blender presentation. Preserve older screenshots as historical material.
5. Optionally offer `dist/house-of-cinders.love` as a download explicitly labeled **Requires LÖVE 11.4 or 11.5**. It is not a standalone executable.
6. Keep the page in draft while testing its hosted iframe: loading, keyboard/mouse, audio after gesture, fullscreen, reload/Continue, and blocked-storage behavior. Local iframe checks do not establish hosted compatibility.
7. Complete PLAYTEST_CHECKLIST.md and record the actual jam URL, deadline/timezone, theme, permitted tools, AI/code/art rules, credits and submission requirements below. Review all source/tool provenance, even though the default ZIP excludes generated portraits.
8. Verify `dist/SHA256SUMS` against the files being uploaded. Publish and submit only when you choose to do so; uploading a game page is separate from entering a jam.

Jam URL: not supplied. Deadline/timezone: not supplied. Project URL: not supplied. AI/asset/code rules: not supplied. Hosted verification: pending. Human acceptance: see PLAYTEST_CHECKLIST.md.

Official setup reference: [itch.io HTML5 upload documentation](https://itch.io/docs/creators/html5), checked 2026-10-12. The ZIP uses relative, case-correct paths and includes its own runtime files.
