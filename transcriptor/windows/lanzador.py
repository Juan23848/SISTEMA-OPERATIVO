"""Punto de entrada del .exe (PyInstaller no acepta imports relativos acá)."""

import sys

from transcriptor.cli import main

if __name__ == "__main__":
    sys.exit(main())
