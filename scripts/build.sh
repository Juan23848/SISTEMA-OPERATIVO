#!/bin/bash
# Compila la ISO de una edición de Antü OS usando live-build.
#
# Uso: ./scripts/build.sh <antu-legacy|antu-standard|antu-pro>
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EDITION="${1:-}"
VALID_EDITIONS=(antu-legacy antu-standard antu-pro)

usage() {
    echo "Uso: $0 <${VALID_EDITIONS[*]// /|}>"
    exit 1
}

if [[ -z "$EDITION" ]]; then
    usage
fi

if [[ ! " ${VALID_EDITIONS[*]} " =~ " ${EDITION} " ]]; then
    echo "Edición desconocida: '$EDITION'"
    usage
fi

EDITION_DIR="$REPO_ROOT/editions/$EDITION"
CONFIG_DIR="$EDITION_DIR/config"

if [[ ! -d "$EDITION_DIR/auto" || ! -d "$CONFIG_DIR" ]]; then
    echo "No se encontró la configuración en $EDITION_DIR"
    exit 1
fi

if ! command -v lb >/dev/null 2>&1; then
    echo "live-build no está instalado. Instalalo con:"
    echo "  sudo apt install live-build"
    exit 1
fi

if [[ "$(id -u)" -ne 0 ]]; then
    echo "live-build necesita privilegios de root. Volviendo a ejecutar con sudo..."
    exec sudo "$0" "$EDITION"
fi

echo "==> Instalando branding compartido"
"$REPO_ROOT/shared/scripts/install-branding.sh" "$CONFIG_DIR"

echo "==> Instalando Antü Resolver"
# Copiado automático desde la fuente única (shared/resolver/), nunca a
# mano: tener una copia propia por edición en el repo fue exactamente lo
# que causó que dos rondas de correcciones al Resolver nunca llegaran a
# ninguna ISO real (encontrado en una revisión externa, Codex) — se
# corrigieron los bugs en shared/resolver/antu-resolver pero las 3
# copias empaquetadas seguían con el código viejo, sin que nada lo
# avisara. Ahora las copias ya ni se versionan (ver .gitignore): se
# generan en cada build a partir de la única fuente real.
RESOLVER_DEST="$CONFIG_DIR/includes.chroot/usr/bin"
mkdir -p "$RESOLVER_DEST"
install -m 0755 "$REPO_ROOT/shared/resolver/antu-resolver" "$RESOLVER_DEST/antu-resolver"

echo "==> Instalando asistente de Office"
# Mismo criterio que el Resolver: fuente única en shared/scripts/,
# nunca una copia versionada por edición.
install -m 0755 "$REPO_ROOT/shared/scripts/instalar-office.sh" "$RESOLVER_DEST/antu-instalar-office"

echo "==> Instalando asistente de Chrome"
# Google Chrome no tiene versión de 32 bits desde hace años (requisito
# oficial: Linux de 64 bits) — antes se excluía en Legacy porque esa
# edición era i386, pero las 3 ediciones son "amd64" ahora, así que el
# asistente aplica a las 3 por igual.
install -m 0755 "$REPO_ROOT/shared/scripts/instalar-chrome.sh" "$RESOLVER_DEST/antu-instalar-chrome"

echo "==> Branding del menú de arranque bajo UEFI (grub-efi)"
# El menú de isolinux (BIOS) ya tiene la marca de Antü, pero el de
# grub-efi (UEFI) seguía mostrando "Live system (amd64)" -- confirmado
# arrancando una ISO real bajo firmware OVMF (ver docs/ARCHITECTURE.md,
# "Soporte UEFI"). A diferencia de isolinux, ese texto no sale de
# ningún archivo que config/bootloaders/grub-pc/ pueda pisar: está
# hardcodeado como argumento literal de "Live system (${_FLAVOUR})" (y
# 5 variantes más: autodetect, fail-safe, multi-kernel) dentro del
# propio script /usr/lib/live/build/binary_grub_cfg -- confirmado
# leyendo el script real de Debian bookworm (1:20230502) en CI, no
# asumido. Las 6 variantes empiezan igual ("Live system"), así que un
# solo sed cubre las 6. "Antu" sin diéresis a propósito, mismo motivo
# que en el menú de isolinux (la fuente de GRUB tampoco renderiza bien
# la "ü" en este contexto de arranque).
case "$EDITION" in
    antu-legacy) EDITION_DISPLAY="Antu Legacy" ;;
    antu-standard) EDITION_DISPLAY="Antu Standard" ;;
    antu-pro) EDITION_DISPLAY="Antu Pro" ;;
esac
GRUB_CFG_SCRIPT="/usr/lib/live/build/binary_grub_cfg"
if [[ -f "$GRUB_CFG_SCRIPT" ]]; then
    sed -i "s/Live system/$EDITION_DISPLAY/g" "$GRUB_CFG_SCRIPT"
else
    echo "ADVERTENCIA: no se encontró $GRUB_CFG_SCRIPT -- el menú de" \
         "grub-efi va a quedar sin la marca de Antü (¿versión distinta" \
         "de live-build?)."
fi

echo "==> Compilando $EDITION"
# live-build espera correr desde el directorio que tiene a auto/ y
# config/ como hermanos (auto/config genera/actualiza config/ en base
# a esa ubicación). Si se entrara a config/ directamente, "lb config"
# crearía un config/config/ vacío al lado de nuestros package-lists/
# hooks/includes.chroot reales, y live-build jamás los encontraría —
# bug real que tuvo el proyecto hasta que se detectó y corrigió acá.
cd "$EDITION_DIR"

./auto/clean
./auto/config
lb build

mkdir -p "$EDITION_DIR/build"
find . -maxdepth 1 -iname '*.iso' -exec mv {} "$EDITION_DIR/build/" \;

echo "==> Listo. ISO en $EDITION_DIR/build/"
