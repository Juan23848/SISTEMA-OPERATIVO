#!/bin/bash
# Copia los assets de shared/branding/ a las rutas estándar del sistema
# dentro de includes.chroot de una edición, para que terminen instalados
# en el sistema final (fondos de escritorio, ícono de la app).
#
# Uso: shared/scripts/install-branding.sh <config-dir-de-la-edicion> [day|night]
set -euo pipefail

CONFIG_DIR="${1:?Falta indicar el directorio config/ de la edición}"
WALLPAPER_VARIANT="${2:-night}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BRANDING_SRC="$REPO_ROOT/shared/branding"

BG_DEST="$CONFIG_DIR/includes.chroot/usr/share/backgrounds/antu"
ICON_DEST="$CONFIG_DIR/includes.chroot/usr/share/pixmaps/antu"
THEME_DEST="$CONFIG_DIR/includes.chroot/usr/share/icons/Antu"

mkdir -p "$BG_DEST" "$ICON_DEST" "$THEME_DEST"

echo "==> Instalando wallpaper ($WALLPAPER_VARIANT) y logo de Antü"
cp "$BRANDING_SRC/wallpaper-$WALLPAPER_VARIANT.png" "$BG_DEST/wallpaper.png"
cp "$BRANDING_SRC/logo.png" "$ICON_DEST/antu-logo.png"

echo "==> Instalando tema de íconos propio de Antü"
cp -r "$BRANDING_SRC/icons/antu-icons/." "$THEME_DEST/"
