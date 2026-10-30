"""Transcripción local con Whisper (vía faster-whisper).

Corre en tu propia compu, sin internet (salvo la primera vez, que descarga el
modelo) y sin pagar nada. Si hay una placa de video NVIDIA con CUDA la usa sola;
si no, usa el procesador.
"""

import os
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
    from . import aceleracion

    aceleracion.preparar_bibliotecas()
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


# Todos los núcleos del procesador (CTranslate2 usa solo 4 si no se le dice).
HILOS_CPU = os.cpu_count() or 4


def _crear_modelo(WhisperModel, nombre: str, dispositivo: str):
    if dispositivo == "auto":
        import ctranslate2

        from . import aceleracion
        # En el .exe de Windows la placa se usa solo si ya se bajaron las
        # bibliotecas de NVIDIA y pasó la prueba en un proceso aparte: si falta
        # cuDNN, CTranslate2 cierra el programa de golpe (no es un error atrapable).
        if aceleracion.aplica():
            hay_gpu = aceleracion.gpu_lista()
        else:
            hay_gpu = ctranslate2.get_cuda_device_count() > 0
        dispositivo = "cuda" if hay_gpu else "cpu"
    if dispositivo == "cpu":
        modelo = WhisperModel(nombre, device="cpu", compute_type="int8", cpu_threads=HILOS_CPU)
    else:
        try:
            # float16 explícito: el automático elige int8_float16, que las RTX 50
            # (Blackwell) no soportan ("CUBLAS_STATUS_NOT_SUPPORTED").
            modelo = WhisperModel(nombre, device="cuda", compute_type="float16")
        except (RuntimeError, ValueError) as e:
            # Típico: hay GPU pero faltan las librerías de CUDA. Caemos al procesador.
            print(f"  No pude usar la placa de video ({e}); uso el procesador.")
            modelo = WhisperModel(nombre, device="cpu", compute_type="int8", cpu_threads=HILOS_CPU)
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
                al_segmento: Optional[Callable[[Segmento], None]] = None,
                al_progreso: Optional[Callable[[float, float], None]] = None) -> Tuple[List[Segmento], float]:
    """Devuelve (segmentos, duración en segundos).

    `al_segmento` se llama con cada fragmento apenas sale, para ir guardando
    el avance: si se corta la luz en la hora 2 de 3, no se pierde todo.
    `al_progreso(segundos_hechos, segundos_totales)` es para la barra de la ventana.
    """
    whisper = cargar_modelo(modelo, dispositivo)
    en_gpu = whisper.model.device == "cuda"
    try:
        return _transcribir_con(whisper, en_gpu, audio, idioma, al_segmento, al_progreso)
    except RuntimeError as e:
        if not en_gpu or isinstance(e, _YaEmpezado):
            raise getattr(e, "original", e)
        # La placa falló (bibliotecas incompatibles, memoria...): se marca para
        # no volver a intentarlo hasta que la persona reintente, y se hace en el procesador.
        from . import aceleracion
        aceleracion.marcar_falla()
        _cache_modelos.clear()  # que el próximo "auto" no reuse el modelo de la placa
        print(f"  La placa de video falló ({e}); sigo con el procesador.")
        return transcribir(audio, modelo, idioma, "cpu", al_segmento, al_progreso)


class _YaEmpezado(RuntimeError):
    """Un error después de haber entregado texto: no se reintenta (se duplicaría)."""

    def __init__(self, original: BaseException):
        super().__init__(str(original))
        self.original = original


def _transcribir_con(whisper, en_gpu: bool, audio: Path, idioma: Optional[str], al_segmento,
                     al_progreso) -> Tuple[List[Segmento], float]:
    from faster_whisper import BatchedInferencePipeline

    print("  Procesando con " + ("la placa de video." if en_gpu else f"el procesador ({HILOS_CPU} hilos)."))
    # En lotes: corta el audio en las pausas (detector de voz) y procesa varios
    # pedazos a la vez en vez de uno detrás del otro. Es entre 2 y 4 veces más
    # rápido, también en procesador, y como cada pedazo es independiente no
    # arrastra errores ni repite frases en bucle en clases largas.
    segmentos_gen, info = BatchedInferencePipeline(model=whisper).transcribe(
        str(audio),
        language=idioma or None,  # None = que lo detecte solo
        batch_size=16 if en_gpu else 8,
        beam_size=5,
    )
    if not idioma:
        print(f"  Idioma detectado: {info.language} ({info.language_probability:.0%})")

    duracion = info.duration or 0.0
    inicio = time.monotonic()
    segmentos: List[Segmento] = []
    interactivo = sys.stdout.isatty()
    segmentos_gen = _marcar_si_ya_empezo(segmentos_gen)
    for s in segmentos_gen:
        seg = Segmento(s.start, s.end, s.text.strip())
        segmentos.append(seg)
        if al_segmento:
            al_segmento(seg)
        if al_progreso:
            al_progreso(seg.fin, duracion)
        if interactivo:
            print(_barra(seg.fin, duracion, inicio), end="", flush=True)
    if interactivo:
        print(_barra(duracion, duracion, inicio))
    return segmentos, duracion


def _marcar_si_ya_empezo(generador):
    """Deja pasar los errores del primer pedazo tal cual (ahí se puede reintentar en
    el procesador) y envuelve los de después, cuando ya se entregó texto."""
    primero = True
    iterador = iter(generador)
    while True:
        try:
            s = next(iterador)
        except StopIteration:
            return
        except RuntimeError as e:
            if primero:
                raise
            raise _YaEmpezado(e) from e
        primero = False
        yield s
