#!/bin/bash
# Asistente "Instalar Google Chrome": el repositorio oficial ya está
# configurado y verificado (ver hooks/normal/0700-google-chrome-repo),
# así que instalar el navegador real es un solo apt install. No viene
# preinstalado porque Chrome es un binario propietario de Google y no
# es nuestro para redistribuir dentro de la ISO.
set -u

notify() {
    if command -v notify-send >/dev/null 2>&1; then
        notify-send -i web-browser "Antü" "$1" || true
    fi
}

if ! zenity --question --title="Antü" \
    --text="¿Instalar Google Chrome? Vas a necesitar tu contraseña de administrador." \
    2>/dev/null; then
    exit 0
fi

notify "Instalando Google Chrome..."

if pkexec sh -c 'apt-get update && apt-get install -y google-chrome-stable'; then
    notify "Google Chrome instalado."
else
    zenity --error --title="Antü" \
        --text="No se pudo instalar Google Chrome. Revisá la conexión a internet e intentá de nuevo." \
        2>/dev/null
fi
