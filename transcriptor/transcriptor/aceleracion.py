"""Usar la placa de video NVIDIA en el .exe de Windows.

El motor (CTranslate2) ya sabe usar la placa, pero necesita dos bibliotecas de
NVIDIA que Windows no trae: cuBLAS y cuDNN (~1,4 GB). En vez de meterlas en el
.zip para todos, se bajan una sola vez, solo en las compus con NVIDIA, de los
mismos paquetes oficiales que usa pip (PyPI), y se guardan en
%LOCALAPPDATA%\\Transcriptor\\cuda.

Antes de usar la placa se la prueba en un proceso aparte: si a CTranslate2
le falta algo, no lanza un error sino que cierra el programa de golpe, y así
el que se cierra es el proceso de prueba, no la ventana.
"""

import json
import os
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable, Optional

# Las versiones nuevas de cada uno, dentro de la versión mayor que usa
# CTranslate2 4.x (CUDA 12, cuDNN 9). cuBLAS 12.8 o más es lo que soporta las
# RTX 50 (Blackwell). nvrtc lo pide cuBLAS para algunas operaciones.
PAQUETES = (
    ("nvidia-cublas-cu12", "12.", (12, 8)),
    ("nvidia-cuda-nvrtc-cu12", "12.", (12, 8)),
    ("nvidia-cudnn-cu12", "9.", (9, 0)),
)
TAMANO_APROXIMADO = "1,4 GB"

_SIN_VENTANA = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class ErrorAceleracion(Exception):
    pass


def carpeta_base() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.path.join(Path.home(), ".local", "share")
    return Path(base) / "Transcriptor"


def carpeta_cuda() -> Path:
    return carpeta_base() / "cuda"


def _ruta_estado() -> Path:
    return carpeta_base() / "aceleracion.json"


def leer_estado() -> dict:
    try:
        return json.loads(_ruta_estado().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _guardar_estado(**datos) -> None:
    estado = leer_estado()
    estado.update(datos)
    try:
        _ruta_estado().parent.mkdir(parents=True, exist_ok=True)
        _ruta_estado().write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def aplica() -> bool:
    """Solo el .exe de Windows maneja esto; con pip, CUDA se instala como siempre."""
    return sys.platform == "win32" and getattr(sys, "frozen", False)


def placa_nvidia() -> Optional[str]:
    """Nombre de la placa NVIDIA si hay una con su controlador instalado; si no, None."""
    if sys.platform != "win32":
        return None
    try:
        salida = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                                capture_output=True, text=True, timeout=15, creationflags=_SIN_VENTANA)
    except (OSError, subprocess.SubprocessError):
        return None
    nombre = salida.stdout.strip().splitlines()[0].strip() if salida.stdout.strip() else ""
    return nombre if salida.returncode == 0 and nombre else None


def instalada() -> bool:
    return bool(leer_estado().get("instalada")) and carpeta_cuda().is_dir()


def gpu_lista() -> bool:
    """La placa se puede usar: bibliotecas bajadas y prueba superada."""
    return aplica() and instalada() and leer_estado().get("prueba") == "ok"


def preparar_bibliotecas() -> None:
    """Que Windows encuentre las DLL de NVIDIA bajadas. Llamar antes de crear el modelo."""
    carpeta = carpeta_cuda()
    if sys.platform != "win32" or not carpeta.is_dir():
        return
    os.environ["PATH"] = str(carpeta) + os.pathsep + os.environ.get("PATH", "")
    try:
        os.add_dll_directory(str(carpeta))
    except (AttributeError, OSError):
        pass


# ------------------------------------------------------------------ descarga


def _version(texto: str) -> tuple:
    partes = []
    for p in texto.split("."):
        if not p.isdigit():
            break
        partes.append(int(p))
    return tuple(partes)


def elegir_rueda(datos_pypi: dict, prefijo: str, minima: tuple, plataforma: str = "win_amd64") -> dict:
    """De la respuesta JSON de PyPI, el archivo .whl más nuevo de esa versión mayor."""
    candidatas = []
    for version, archivos in datos_pypi.get("releases", {}).items():
        if not version.startswith(prefijo) or _version(version) < minima:
            continue
        for archivo in archivos:
            if archivo["filename"].endswith(f"{plataforma}.whl") and not archivo.get("yanked"):
                candidatas.append((_version(version), archivo))
    if not candidatas:
        raise ErrorAceleracion(f"No encontré una versión {prefijo}x para {plataforma}.")
    return max(candidatas, key=lambda c: c[0])[1]


def extraer_bibliotecas(rueda: Path, destino: Path) -> int:
    """Copia solo las DLL (nvidia/<paquete>/bin/*.dll) de la rueda a `destino`. Devuelve cuántas."""
    destino.mkdir(parents=True, exist_ok=True)
    cantidad = 0
    with zipfile.ZipFile(rueda) as z:
        for info in z.infolist():
            partes = info.filename.split("/")
            if len(partes) >= 3 and partes[0] == "nvidia" and partes[-2] == "bin" and partes[-1].lower().endswith(".dll"):
                with z.open(info) as origen, open(destino / partes[-1], "wb") as salida:
                    while bloque := origen.read(1 << 20):
                        salida.write(bloque)
                cantidad += 1
    return cantidad


def instalar(al_progreso: Optional[Callable[[float, str], None]] = None,
             cancelado: Optional[Callable[[], bool]] = None) -> None:
    """Baja y extrae cuBLAS, nvrtc y cuDNN. `al_progreso(fraccion_total, texto)`."""
    destino = carpeta_cuda()
    temporal = carpeta_base() / "descarga"
    temporal.mkdir(parents=True, exist_ok=True)
    _guardar_estado(instalada=False, prueba=None)

    ruedas = []
    for nombre, prefijo, minima in PAQUETES:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{nombre}/json", timeout=60) as r:
            ruedas.append((nombre, elegir_rueda(json.load(r), prefijo, minima)))
    total = sum(r["size"] for _, r in ruedas) or 1
    hecho = 0

    for nombre, rueda in ruedas:
        archivo = temporal / rueda["filename"]
        with urllib.request.urlopen(rueda["url"], timeout=60) as r, open(archivo, "wb") as salida:
            while bloque := r.read(1 << 20):
                if cancelado and cancelado():
                    raise ErrorAceleracion("Descarga cancelada.")
                salida.write(bloque)
                hecho += len(bloque)
                if al_progreso:
                    al_progreso(hecho / total, f"Bajando {nombre} ({hecho / 1e6:,.0f} de {total / 1e6:,.0f} MB)")
        if al_progreso:
            al_progreso(hecho / total, f"Descomprimiendo {nombre}…")
        if extraer_bibliotecas(archivo, destino) == 0:
            raise ErrorAceleracion(f"El paquete {nombre} no trae las bibliotecas esperadas.")
        archivo.unlink()

    try:
        temporal.rmdir()
    except OSError:
        pass
    _guardar_estado(instalada=True, versiones={n: r["filename"] for n, r in ruedas})


# -------------------------------------------------------------------- prueba


def _comando_prueba() -> list:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--probar-gpu"]
    return [sys.executable, "-m", "transcriptor.aceleracion"]


def probar() -> bool:
    """Prueba la placa en otro proceso (si algo falla de verdad, se cae ese, no la ventana)."""
    try:
        resultado = subprocess.run(_comando_prueba(), timeout=600, creationflags=_SIN_VENTANA,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ok = resultado.returncode == 0
    except (OSError, subprocess.SubprocessError):
        ok = False
    _guardar_estado(prueba="ok" if ok else "falla")
    return ok


def marcar_falla() -> None:
    """La placa falló en una transcripción real: se vuelve al procesador hasta reintentar."""
    _guardar_estado(prueba="falla")


def prueba_en_este_proceso() -> int:
    """Lo que corre el proceso de prueba: un modelo chico en la placa, sobre 3 s de audio."""
    try:
        import numpy as np

        preparar_bibliotecas()
        from faster_whisper import WhisperModel

        # float16 explícito: el automático elige int8_float16, que las RTX 50 no soportan.
        modelo = WhisperModel("tiny", device="cuda", compute_type="float16")
        ruido = (np.random.default_rng(0).standard_normal(16000 * 3) * 0.01).astype("float32")
        segmentos, _ = modelo.transcribe(ruido, language="es", vad_filter=False, beam_size=1)
        list(segmentos)
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(prueba_en_este_proceso())
