"""Transcripción local con Whisper (vía faster-whisper).

Corre en tu propia compu, sin internet (salvo la primera vez, que descarga el
modelo) y sin pagar nada. Si hay una placa de video NVIDIA con CUDA la usa sola;
si no, usa el procesador.
"""

import sys
import time
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from .segmentos import Segmento, formato_tiempo

# Del más rápido al más preciso. "small" anda bien en cualquier notebook;
# "turbo" (large-v3-turbo) es casi tan preciso como "large-v3" y bastante
# más rápido, ideal si tenés GPU o paciencia.
MODELOS = ("tiny", "base", "small", "medium", "turbo", "large-v3")
MODELO_POR_DEFECTO = "small"

_cache_modelos = {}


def cargar_modelo(nombre: str, dispositivo: str = "auto"):
    clave = (nombre, dispositivo)
    if clave in _cache_modelos:
        return _cache_modelos[clave]
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise RuntimeError("Falta faster-whisper. Instalalo con: pip install -U faster-whisper") from e

    print(f"Cargando el modelo '{nombre}' (la primera vez se descarga, puede tardar)...")
    try:
        modelo = _crear_modelo(WhisperModel, nombre, dispositivo)
    except Exception as e:
        red = ("requests", "huggingface_hub", "httpx", "httpcore", "urllib3")
        if isinstance(e, ConnectionError) or e.__class__.__module__.startswith(red):
            raise RuntimeError(
                f"No pude descargar el modelo '{nombre}' ({e}). La primera vez hace falta internet; "
                "después funciona sin conexión."
            ) from e
        raise
    _cache_modelos[clave] = modelo
    return modelo


def _crear_modelo(WhisperModel, nombre: str, dispositivo: str):
    if dispositivo == "auto":
        import ctranslate2
        # En el .exe de Windows no se usa la placa de video salvo que se pida
        # con --gpu: si falta cuDNN, CTranslate2 cierra el programa de golpe
        # (no es un error que se pueda atrapar), y casi nadie lo tiene instalado.
        empaquetado = getattr(sys, "frozen", False)
        hay_gpu = not empaquetado and ctranslate2.get_cuda_device_count() > 0
        dispositivo = "cuda" if hay_gpu else "cpu"
    if dispositivo == "cpu":
        modelo = WhisperModel(nombre, device="cpu", compute_type="int8")
    else:
        try:
            modelo = WhisperModel(nombre, device="cuda", compute_type="auto")
        except (RuntimeError, ValueError) as e:
            # Típico: hay GPU pero faltan las librerías de CUDA. Caemos al procesador.
            print(f"  No pude usar la placa de video ({e}); uso el procesador.")
            modelo = WhisperModel(nombre, device="cpu", compute_type="int8")
    return modelo


def _barra(hecho: float, total: float, inicio: float) -> str:
    fraccion = min(hecho / total, 1.0) if total else 0.0
    llenos = int(fraccion * 30)
    transcurrido = time.monotonic() - inicio
    restante = ""
    if fraccion > 0.02:
        restante = f" · faltan ~{formato_tiempo(transcurrido / fraccion - transcurrido)}"
    return (f"\r  [{'#' * llenos}{'.' * (30 - llenos)}] {fraccion:5.1%} "
            f"({formato_tiempo(hecho)} de {formato_tiempo(total)}){restante}   ")


def transcribir(audio: Path, modelo: str = MODELO_POR_DEFECTO, idioma: Optional[str] = "es",
                dispositivo: str = "auto",
                al_segmento: Optional[Callable[[Segmento], None]] = None) -> Tuple[List[Segmento], float]:
    """Devuelve (segmentos, duración en segundos).

    `al_segmento` se llama con cada fragmento apenas sale, para ir guardando
    el avance: si se corta la luz en la hora 2 de 3, no se pierde todo.
    """
    whisper = cargar_modelo(modelo, dispositivo)
    segmentos_gen, info = whisper.transcribe(
        str(audio),
        language=idioma or None,  # None = que lo detecte solo
        vad_filter=True,  # saltea silencios: más rápido y menos "alucinaciones"
        beam_size=5,
        condition_on_previous_text=False,  # evita que repita frases en bucle en clases largas
    )
    if not idioma:
        print(f"  Idioma detectado: {info.language} ({info.language_probability:.0%})")

    duracion = info.duration or 0.0
    inicio = time.monotonic()
    segmentos: List[Segmento] = []
    interactivo = sys.stdout.isatty()
    for s in segmentos_gen:
        seg = Segmento(s.start, s.end, s.text.strip())
        segmentos.append(seg)
        if al_segmento:
            al_segmento(seg)
        if interactivo:
            print(_barra(seg.fin, duracion, inicio), end="", flush=True)
    if interactivo:
        print(_barra(duracion, duracion, inicio))
    return segmentos, duracion
