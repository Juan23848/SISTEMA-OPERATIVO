"""Punto de entrada de Transcriptor.exe (PyInstaller no acepta imports relativos acá).

Abre la ventana. Con --cli adelante funciona como el comando `transcribir`
(lo usan las pruebas automáticas y quien prefiera la terminal).
"""

import os
import sys
from pathlib import Path


def _registro_si_no_hay_consola() -> None:
    # Un .exe con ventana no tiene consola: sys.stdout/stderr son None y
    # cualquier librería que imprima (barras de descarga, avisos) se caería.
    # Todo va a un archivo que sirve para diagnosticar si algo falla.
    if sys.stdout is not None and sys.stderr is not None:
        return
    carpeta = Path(os.environ.get("APPDATA") or Path.home()) / "Transcriptor"
    carpeta.mkdir(parents=True, exist_ok=True)
    registro = open(carpeta / "registro.txt", "w", encoding="utf-8", buffering=1)
    sys.stdout = sys.stdout or registro
    sys.stderr = sys.stderr or registro


if __name__ == "__main__":
    _registro_si_no_hay_consola()
    if sys.argv[1:2] == ["--cli"]:
        from transcriptor.cli import main
        sys.exit(main(sys.argv[2:]))
    from transcriptor.gui import main
    sys.exit(main(sys.argv[1:]))
