#!/usr/bin/env bash
# Trim the transparent DreamLayer cutouts and export 256px game sprites.
# Sources live in art-src/raw/ (git-ignored); shipped sprites go to assets/.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p assets/heroes assets/bosses art-src/previews

export_sprite() { # input output
  magick "$1" -trim +repage \
    -filter point -resize 236x236 \
    -background none -gravity center -extent 256x256 \
    "$2"
}

heroes="jack match penny dealer gale zephyr flint mason clover briar frost whiteout volt count crown oracle null laugh"
for id in $heroes; do
  export_sprite "art-src/raw/${id}_nobg.png" "assets/heroes/${id}.png"
done
export_sprite "art-src/raw/bailiff_nobg.png" "assets/bosses/bailiff.png"

magick montage assets/heroes/*.png assets/bosses/bailiff.png -tile 5x -geometry 256x256+4+4 \
  -background '#101820' -border 2 -bordercolor '#3a4a48' art-src/previews/contact-sheet.png
echo "exported $(ls assets/heroes/*.png | wc -l) heroes + $(ls assets/bosses/*.png | wc -l) boss"
