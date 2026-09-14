#!/bin/bash
# Bootea una ISO de WinLux OS en una VM QEMU para pruebas rápidas.
#
# Uso: ./scripts/test-qemu.sh <ruta-a-la-iso> [RAM_MB]
set -euo pipefail

ISO="${1:-}"
RAM_MB="${2:-4096}"

if [[ -z "$ISO" || ! -f "$ISO" ]]; then
    echo "Uso: $0 <ruta-a-la-iso> [RAM_MB]"
    echo "No se encontró el archivo ISO indicado."
    exit 1
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
    echo "QEMU no está instalado. Instalalo con:"
    echo "  sudo apt install qemu-system-x86"
    exit 1
fi

echo "==> Booteando $ISO con ${RAM_MB}MB de RAM"
qemu-system-x86_64 \
    -enable-kvm \
    -m "$RAM_MB" \
    -smp 2 \
    -boot d \
    -cdrom "$ISO" \
    -vga std
