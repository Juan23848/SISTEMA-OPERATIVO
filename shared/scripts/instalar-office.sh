#!/bin/bash
# Asistente "Instalar Microsoft Office": prepara el prefix de Wine con
# las dependencias que suelen pedir los instaladores de Office
# (fuentes, riched20, gdiplus, msxml — componentes de Windows que Wine
# no trae por sí solo) y después deja que el usuario elija su propio
# instalador (.exe/.msi) con licencia propia.
#
# No podemos empaquetar el instalador de Office en la ISO: es software
# con licencia comercial de Microsoft, no nuestro para redistribuir.
# Por eso el usuario lo aporta — exactamente como en Windows, donde
# tampoco viene incluido de fábrica.
#
# Una vez elegido el instalador, la instalación en sí la maneja
# antu-resolver (el mismo motor que ya abre cualquier .exe/.msi), para
# no duplicar la lógica de Wine en dos lugares distintos.
#
# Pendiente de validar con un instalador de Office real (ver
# docs/ROADMAP.md): las dependencias de abajo son las que recomienda la
# comunidad de WineHQ para Office en general, pero cada versión puede
# necesitar algo más — si falla, winetricks deja un log en
# ~/.cache/winetricks/.
set -u

notify() {
    if command -v notify-send >/dev/null 2>&1; then
        notify-send -i office-word "Antü" "$1" || true
    fi
}

if ! command -v wine >/dev/null 2>&1; then
    zenity --error --title="Antü" \
        --text="Wine no está instalado. No se puede preparar Office." 2>/dev/null
    exit 1
fi

notify "Preparando el entorno de Wine para Office. Puede tardar un par de minutos..."

# corefonts: fuentes de Windows que Office espera encontrar.
# riched20/riched30: cuadro de texto enriquecido que usan varios
# instaladores y diálogos de Office.
# gdiplus: dibujo 2D que usan las interfaces de instalación.
# msxml6: varias rutinas de Office dependen de este parser XML.
#
# El log completo (no solo las últimas líneas) queda en un archivo
# aparte para poder mostrarlo si algo falla — un pipe directo a "tail"
# esconde el código de salida real de winetricks (hallazgo real de una
# revisión externa, ChatGPT/Codex): si una descarga o una dependencia
# fallaba, el asistente seguía igual pidiendo el instalador, sin avisar
# nada.
WINETRICKS_LOG="$(mktemp)"
if ! winetricks -q corefonts riched20 riched30 gdiplus msxml6 >"$WINETRICKS_LOG" 2>&1; then
    zenity --error --title="Antü" \
        --text="No se pudo preparar Wine para Office (falló winetricks). Detalle:\n\n$(tail -n 20 "$WINETRICKS_LOG")" \
        2>/dev/null
    rm -f "$WINETRICKS_LOG"
    exit 1
fi
rm -f "$WINETRICKS_LOG"

INSTALADOR=$(zenity --file-selection \
    --title="Elegí tu instalador de Microsoft Office" \
    --file-filter="Instaladores de Windows | *.exe *.msi" 2>/dev/null)

if [ -z "$INSTALADOR" ]; then
    exit 0
fi

notify "Instalando Office. Seguí el instalador como en Windows."
exec antu-resolver install "$INSTALADOR"
