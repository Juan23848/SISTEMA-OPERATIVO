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
BOOTLOADER_DEST="$CONFIG_DIR/bootloaders/syslinux_common"

mkdir -p "$BG_DEST" "$ICON_DEST" "$THEME_DEST" "$BOOTLOADER_DEST"

echo "==> Instalando wallpaper ($WALLPAPER_VARIANT) y logo de Antü"
cp "$BRANDING_SRC/wallpaper-$WALLPAPER_VARIANT.png" "$BG_DEST/wallpaper.png"
cp "$BRANDING_SRC/logo.png" "$ICON_DEST/antu-logo.png"

echo "==> Instalando tema de íconos propio de Antü"
cp -r "$BRANDING_SRC/icons/antu-icons/." "$THEME_DEST/"

# El splash del menú de arranque (isolinux/syslinux) va aparte de
# includes.chroot: live-build lo lee de config/bootloaders/syslinux_common/
# ANTES de armar la ISO, no del sistema de archivos final. Reemplaza el
# splash.svg de Debian (que trae el logo de Debian + un banner de texto
# con versiones, dibujado como <text> dentro del propio SVG — confirmado
# leyendo el código real de live-build) por uno ya renderizado con la
# marca de Antü, en los dos tamaños que live-build genera
# (splash.png 640x480, splash800x600.png). Al no incluir un splash.svg
# propio, el script de live-build no reconstruye nada a partir del
# original — usa estos archivos tal cual.
echo "==> Instalando splash de arranque (isolinux/syslinux) con la marca de Antü"
cp "$BRANDING_SRC/boot-splash.png" "$BOOTLOADER_DEST/splash.png"
cp "$BRANDING_SRC/boot-splash800x600.png" "$BOOTLOADER_DEST/splash800x600.png"
