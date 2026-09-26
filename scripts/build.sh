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

# Google Chrome no tiene versión de 32 bits desde hace años (requisito
# oficial: Linux de 64 bits) — no tiene sentido copiar el asistente ni
# el repo en Legacy (i386): el lanzador fallaría siempre, y encima con
# un mensaje que culpa a la conexión en vez de a la arquitectura
# (hallazgo real de una revisión externa). Standard y Pro son amd64.
if [[ "$EDITION" != "antu-legacy" ]]; then
    echo "==> Instalando asistente de Chrome"
    install -m 0755 "$REPO_ROOT/shared/scripts/instalar-chrome.sh" "$RESOLVER_DEST/antu-instalar-chrome"
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
