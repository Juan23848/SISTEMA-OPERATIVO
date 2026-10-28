"""El paso común a la ventana y a la línea de comandos: de una fuente ya
resuelta (archivo local, audio bajado o subtítulos) a los documentos guardados."""

from pathlib import Path
from typing import Callable, Iterable, List, Optional, Tuple

from .fuentes import Fuente
from .salida import armar_parrafos, guardar, nombre_seguro
from .segmentos import Cancelado, Segmento, formato_tiempo
from .transcripcion import transcribir


def texto_limpio(titulo: str, segmentos: List[Segmento]) -> str:
    """Título y párrafos, sin marcas de tiempo: lo que se copia al portapapeles."""
    return titulo + "\n\n" + "\n\n".join(p.texto for p in armar_parrafos(segmentos))


def transcribir_fuente(fuente: Fuente, carpeta: Path, modelo: str, idioma: Optional[str],
                       dispositivo: str, formatos: Iterable[str],
                       al_progreso: Optional[Callable[[float, float], None]] = None,
                       cancelado: Optional[Callable[[], bool]] = None) -> Tuple[List[Path], str]:
    """Transcribe y guarda. Devuelve (archivos escritos, texto limpio); ([], "") si no hubo voz."""
    if fuente.subtitulos:
        segmentos = fuente.subtitulos
        duracion = segmentos[-1].fin
    else:
        carpeta.mkdir(parents=True, exist_ok=True)
        # Se va guardando a medida que avanza: si se corta, queda lo hecho.
        parcial = carpeta / (nombre_seguro(fuente.titulo) + ".parcial.txt")
        with parcial.open("w", encoding="utf-8") as f:
            def al_segmento(seg: Segmento) -> None:
                f.write(f"[{formato_tiempo(seg.inicio)}] {seg.texto}\n")
                f.flush()
                if cancelado and cancelado():
                    raise Cancelado()

            segmentos, duracion = transcribir(fuente.audio, modelo, idioma, dispositivo,
                                              al_segmento=al_segmento, al_progreso=al_progreso)
        parcial.unlink()
    if not segmentos:
        return [], ""
    rutas = guardar(segmentos, fuente.titulo, fuente.origen, duracion, carpeta, formatos)
    return rutas, texto_limpio(fuente.titulo, segmentos)
