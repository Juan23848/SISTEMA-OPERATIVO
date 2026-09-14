#!/bin/bash
# Compila la ISO de una edición de WinLux OS usando live-build.
#
# Uso: ./scripts/build.sh <winlux-legacy|winlux-standard|winlux-pro>
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EDITION="${1:-}"
VALID_EDITIONS=(winlux-legacy winlux-standard winlux-pro)

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

if [[ ! -d "$CONFIG_DIR" ]]; then
    echo "No se encontró la configuración en $CONFIG_DIR"
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

echo "==> Compilando $EDITION"
cd "$CONFIG_DIR"

./auto/clean
./auto/config
lb build

mkdir -p "$EDITION_DIR/build"
find . -maxdepth 1 -iname '*.iso' -exec mv {} "$EDITION_DIR/build/" \;

echo "==> Listo. ISO en $EDITION_DIR/build/"
