"""Lo que depende del sistema operativo: portapapeles, abrir archivos y la carpeta Documentos.

Pensado para Windows, macOS y Linux, incluido Antü OS (Debian), donde el .docx
se abre con lo que esté asociado: Word vía Wine (asistente de Office de Antü)
o LibreOffice si lo instalaste.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def carpeta_documentos() -> Path:
    """~/Documentos/Transcripciones (o ~/Documents/... según el idioma del sistema)."""
    casa = Path.home()
    documentos: Optional[Path] = None
    if sys.platform.startswith("linux"):
        # xdg-user-dir conoce el nombre real ("Documentos" en Antü en español).
        try:
            salida = subprocess.run(["xdg-user-dir", "DOCUMENTS"], capture_output=True,
                                    text=True, timeout=5).stdout.strip()
            if salida and Path(salida) != casa:
                documentos = Path(salida)
        except (OSError, subprocess.SubprocessError):
            pass
    if documentos is None:
        for nombre in ("Documentos", "Documents"):
            if (casa / nombre).is_dir():
                documentos = casa / nombre
                break
    return (documentos or casa) / "Transcripciones"


def _comando_portapapeles() -> Optional[List[str]]:
    if sys.platform == "win32":
        return ["clip"]
    if sys.platform == "darwin":
        return ["pbcopy"]
    if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wl-copy"):
        return ["wl-copy"]
    if shutil.which("xclip"):
        return ["xclip", "-selection", "clipboard"]
    if shutil.which("xsel"):
        return ["xsel", "--clipboard", "--input"]
    return None


def copiar_al_portapapeles(texto: str) -> bool:
    comando = _comando_portapapeles()
    if comando is None:
        return False
    # clip de Windows interpreta la entrada como UTF-16 si trae BOM; así no rompe tildes.
    datos = ("﻿" + texto).encode("utf-16-le") if comando == ["clip"] else texto.encode("utf-8")
    try:
        # xclip/xsel se quedan vivos sirviendo el portapapeles: no hay que esperarlos.
        proceso = subprocess.Popen(comando, stdin=subprocess.PIPE,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proceso.communicate(datos, timeout=5)
    except subprocess.TimeoutExpired:
        return True
    except OSError:
        return False
    return proceso.returncode == 0


def abrir(ruta: Path) -> None:
    """Abre el archivo con el programa asociado (Word, LibreOffice...)."""
    try:
        if sys.platform == "win32":
            os.startfile(str(ruta))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(ruta)])
        else:
            subprocess.Popen(["xdg-open", str(ruta)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as e:
        print(f"  No pude abrirlo automáticamente ({e}). Está en: {ruta}")
