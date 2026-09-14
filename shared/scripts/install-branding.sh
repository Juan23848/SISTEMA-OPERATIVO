#!/bin/bash
# Copia los assets de shared/branding/ a las rutas estándar del sistema
# dentro de includes.chroot de una edición, para que terminen instalados
# en el sistema final (fondos de escritorio, ícono de la app).
#
# Uso: shared/scripts/install-branding.sh <config-dir-de-la-edicion>
set -euo pipefail

CONFIG_DIR="${1:?Falta indicar el directorio config/ de la edición}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BRANDING_SRC="$REPO_ROOT/shared/branding"

BG_DEST="$CONFIG_DIR/includes.chroot/usr/share/backgrounds/winlux"
ICON_DEST="$CONFIG_DIR/includes.chroot/usr/share/pixmaps/winlux"

mkdir -p "$BG_DEST" "$ICON_DEST"

if command -v rsvg-convert >/dev/null 2>&1; then
    echo "==> Convirtiendo assets SVG a PNG con rsvg-convert"
    rsvg-convert -w 1920 -h 1080 "$BRANDING_SRC/wallpaper.svg" -o "$BG_DEST/wallpaper.png"
    rsvg-convert -w 256 -h 256 "$BRANDING_SRC/logo.svg" -o "$ICON_DEST/winlux-logo.png"
else
    echo "==> rsvg-convert no está instalado, copiando los SVG originales"
    echo "    (instalá 'librsvg2-bin' para generar PNG en su lugar: sudo apt install librsvg2-bin)"
    cp "$BRANDING_SRC/wallpaper.svg" "$BG_DEST/wallpaper.svg"
    cp "$BRANDING_SRC/logo.svg" "$ICON_DEST/winlux-logo.svg"
fi
