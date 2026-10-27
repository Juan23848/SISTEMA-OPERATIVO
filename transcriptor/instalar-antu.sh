#!/usr/bin/env bash
# Instala Transcriptor en Antü OS (o cualquier Debian/Ubuntu) y le agrega un
# ícono en el menú de aplicaciones. Uso, desde esta carpeta:
#     ./instalar-antu.sh
set -euo pipefail

carpeta="$(cd "$(dirname "$0")" && pwd)"

echo "==> Instalando dependencias del sistema (pide tu contraseña)..."
# pipx: instala el programa aislado, sin romper el Python del sistema.
# ffmpeg: algunos sitios lo necesitan para bajar el audio.
# xclip: para la opción --copiar (pegar el texto con Ctrl+V).
sudo apt-get update -qq
sudo apt-get install -y pipx ffmpeg xclip

echo "==> Instalando Transcriptor..."
pipx install --force "$carpeta"
pipx ensurepath >/dev/null

echo "==> Agregando el ícono al menú de aplicaciones..."
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/transcriptor.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Transcriptor
GenericName=Video y audio a texto
Comment=Pasa clases, videos y audios de WhatsApp a texto y a documentos de Word
Exec=$HOME/.local/bin/transcribir
Icon=accessories-text-editor
Terminal=true
Categories=AudioVideo;Office;Education;
Keywords=transcribir;desgrabar;whisper;audio;video;texto;word;docx;
EOF
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo
echo "Listo. Abrilo desde el menú (\"Transcriptor\") o, en una terminal nueva:"
echo "    transcribir"
echo "Los documentos quedan en: $(xdg-user-dir DOCUMENTS 2>/dev/null || echo "$HOME/Documentos")/Transcripciones"
