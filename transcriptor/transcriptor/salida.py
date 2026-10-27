"""Convierte la lista de segmentos en archivos pensados para estudiar.

- .txt: texto corrido en párrafos, sin marcas de tiempo (para leer/resumir).
- .md:  mismos párrafos con la marca de tiempo al inicio de cada uno, para
        volver al minuto exacto del video si algo no se entiende.
- .srt: subtítulos estándar (sirven para cargarlos en VLC junto al video).
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from .segmentos import Segmento, formato_tiempo

FORMATOS_VALIDOS = ("txt", "md", "srt")

# Un párrafo nuevo arranca si hubo un silencio largo o si el actual ya es largo
# y la oración terminó. Así el texto queda en bloques legibles, no en una pared.
PAUSA_PARRAFO = 2.5  # segundos
LARGO_PARRAFO = 700  # caracteres


def armar_parrafos(segmentos: Iterable[Segmento]) -> List[Segmento]:
    parrafos: List[Segmento] = []
    actual = None
    for seg in segmentos:
        texto = seg.texto.strip()
        if not texto:
            continue
        if actual is None:
            actual = Segmento(seg.inicio, seg.fin, texto)
            continue
        pausa = seg.inicio - actual.fin
        termino_oracion = actual.texto.rstrip().endswith((".", "?", "!", "…"))
        if pausa >= PAUSA_PARRAFO or (len(actual.texto) >= LARGO_PARRAFO and termino_oracion):
            parrafos.append(actual)
            actual = Segmento(seg.inicio, seg.fin, texto)
        else:
            actual.texto += " " + texto
            actual.fin = seg.fin
    if actual is not None:
        parrafos.append(actual)
    return parrafos


def nombre_seguro(titulo: str) -> str:
    """Convierte un título cualquiera en un nombre de archivo válido en Windows/Linux/macOS."""
    limpio = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", titulo).strip().strip(".")
    limpio = re.sub(r"\s+", " ", limpio)
    return limpio[:120] or "transcripcion"


def _encabezado(origen: str, duracion: float) -> List[str]:
    return [
        f"Fuente: {origen}",
        f"Duración: {formato_tiempo(duracion)}",
        f"Transcripto: {datetime.now():%Y-%m-%d %H:%M}",
    ]


def texto_txt(segmentos, titulo, origen, duracion) -> str:
    lineas = [titulo, "=" * len(titulo), *_encabezado(origen, duracion), ""]
    lineas += [p.texto + "\n" for p in armar_parrafos(segmentos)]
    return "\n".join(lineas)


def texto_md(segmentos, titulo, origen, duracion) -> str:
    lineas = [f"# {titulo}", ""]
    lineas += [f"- {l}" for l in _encabezado(origen, duracion)]
    lineas.append("")
    for p in armar_parrafos(segmentos):
        lineas.append(f"**[{formato_tiempo(p.inicio)}]** {p.texto}")
        lineas.append("")
    return "\n".join(lineas)


def texto_srt(segmentos) -> str:
    bloques = []
    numero = 0
    for seg in segmentos:
        texto = seg.texto.strip()
        if not texto:
            continue
        numero += 1
        bloques.append(
            f"{numero}\n{formato_tiempo(seg.inicio, True)} --> {formato_tiempo(seg.fin, True)}\n{texto}\n"
        )
    return "\n".join(bloques)


def guardar(segmentos: List[Segmento], titulo: str, origen: str, duracion: float,
            carpeta: Path, formatos: Iterable[str]) -> List[Path]:
    carpeta.mkdir(parents=True, exist_ok=True)
    base = carpeta / nombre_seguro(titulo)
    escritos = []
    for fmt in formatos:
        if fmt == "txt":
            contenido = texto_txt(segmentos, titulo, origen, duracion)
        elif fmt == "md":
            contenido = texto_md(segmentos, titulo, origen, duracion)
        elif fmt == "srt":
            contenido = texto_srt(segmentos)
        else:
            raise ValueError(f"Formato desconocido: {fmt}")
        ruta = base.with_name(base.name + "." + fmt)
        ruta.write_text(contenido, encoding="utf-8")
        escritos.append(ruta)
    return escritos
