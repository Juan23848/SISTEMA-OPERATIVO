"""Último recurso: grabar lo que suena en la compu (o el micrófono) y transcribirlo.

Sirve para TODO lo que se pueda reproducir aunque no se pueda descargar:
un video de Drive protegido, una clase en vivo por Zoom/Meet/Teams, un
reproductor raro de un campus virtual, etc. Se pone a reproducir (puede ser
a 1.5x o 2x, Whisper lo entiende igual en la mayoría de los casos) y se graba.

Usa la librería `soundcard`, que permite grabar la salida de audio ("loopback")
en Windows y Linux sin instalar nada extra. En macOS la salida no se puede
grabar directamente: hay que instalar BlackHole (gratis) y elegirlo como
dispositivo; ver el README.
"""

import time
import wave
from pathlib import Path
from typing import Optional

import numpy as np

FRECUENCIA = 16_000  # lo que usa Whisper internamente; graba liviano (~115 MB por hora)
BLOQUE = FRECUENCIA // 2  # medio segundo por lectura


def _soundcard():
    try:
        import soundcard
    except ImportError as e:
        raise RuntimeError("Falta soundcard. Instalalo con: pip install -U soundcard") from e
    except Exception as e:  # p. ej. Linux sin PulseAudio/PipeWire
        raise RuntimeError(
            f"No pude acceder al sistema de audio ({e.__class__.__name__}: {e}).\n"
            "En Linux hace falta PulseAudio o PipeWire (con pipewire-pulse) funcionando."
        ) from e
    return soundcard


def listar_dispositivos() -> None:
    sc = _soundcard()
    print("Salidas (lo que suena en la compu; se graban con --dispositivo):")
    for m in sc.all_microphones(include_loopback=True):
        if m.isloopback:
            print(f"  - {m.name}")
    print("\nMicrófonos (se graban con --microfono --dispositivo):")
    for m in sc.all_microphones(include_loopback=False):
        print(f"  - {m.name}")


def _elegir_entrada(microfono: bool, dispositivo: Optional[str]):
    sc = _soundcard()
    if dispositivo:
        try:
            return sc.get_microphone(dispositivo, include_loopback=not microfono)
        except IndexError:
            raise RuntimeError(f"No encontré el dispositivo '{dispositivo}'. "
                               "Mirá los disponibles con: transcribir dispositivos")
    if microfono:
        return sc.default_microphone()
    # La salida por defecto (parlantes/auriculares) vista como "micrófono".
    return sc.get_microphone(str(sc.default_speaker().name), include_loopback=True)


def grabar(destino: Path, microfono: bool = False, dispositivo: Optional[str] = None,
           duracion: Optional[float] = None) -> float:
    """Graba en `destino` (WAV mono 16 kHz) hasta Ctrl+C o hasta `duracion` segundos.

    Escribe a disco a medida que graba, así una clase de 3 horas no llena la
    memoria y, si algo se corta, lo grabado hasta ese momento queda guardado.
    Devuelve los segundos grabados.
    """
    entrada = _elegir_entrada(microfono, dispositivo)
    print(f"Grabando desde: {entrada.name}")
    if duracion:
        print(f"Se detiene sola a los {int(duracion // 60)} min {int(duracion % 60)} s, o antes con Ctrl+C.")
    else:
        print("Poné a reproducir el video/audio. Cuando termine, apretá Ctrl+C.")

    grabados = 0
    inicio = time.monotonic()
    with wave.open(str(destino), "wb") as wav, entrada.recorder(samplerate=FRECUENCIA, channels=1) as rec:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(FRECUENCIA)
        try:
            while duracion is None or grabados < duracion * FRECUENCIA:
                datos = rec.record(numframes=BLOQUE)
                if datos.ndim > 1:
                    datos = datos.mean(axis=1)
                pcm = (np.clip(datos, -1.0, 1.0) * 32767).astype("<i2")
                wav.writeframes(pcm.tobytes())
                grabados += len(pcm)
                nivel = float(np.abs(datos).max()) if len(datos) else 0.0
                medidor = "|" * int(min(nivel, 1.0) * 20)
                print(f"\r  {time.strftime('%H:%M:%S', time.gmtime(time.monotonic() - inicio))}  "
                      f"nivel [{medidor:<20}]", end="", flush=True)
        except KeyboardInterrupt:
            pass
    print("\nGrabación terminada.")
    segundos = grabados / FRECUENCIA
    if segundos < 1:
        raise RuntimeError("No se grabó nada.")
    return segundos
