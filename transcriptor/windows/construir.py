"""Arma la carpeta del programa con PyInstaller: python windows/construir.py

Se usa en GitHub Actions para el .exe de Windows, pero funciona igual en
Linux (para probar el empaquetado sin una compu Windows).
"""

import subprocess
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent

subprocess.run([
    sys.executable, "-m", "PyInstaller",
    "--noconfirm", "--clean",
    # Carpeta y no un único .exe: arranca mucho más rápido (no se descomprime
    # cada vez) y los antivirus desconfían menos.
    "--onedir",
    "--console",
    "--name", "transcribir",
    "--distpath", str(raiz / "dist"),
    "--workpath", str(raiz / "build"),
    "--specpath", str(raiz / "build"),
    # Archivos que estas librerías cargan en tiempo de ejecución y PyInstaller
    # no ve solo: el detector de voz de faster-whisper, las DLL de CTranslate2,
    # los encabezados de soundcard y las plantillas de python-docx.
    "--collect-all", "faster_whisper",
    "--collect-all", "ctranslate2",
    "--collect-all", "soundcard",
    "--collect-data", "docx",
    "--collect-submodules", "transcriptor",
    str(raiz / "windows" / "lanzador.py"),
], check=True, cwd=raiz)
