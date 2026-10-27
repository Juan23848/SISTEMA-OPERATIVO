"""Punto de entrada: `transcribir ...`.

Uso rápido:
    transcribir clase.mp4
    transcribir "audio de WhatsApp.opus"
    transcribir https://www.youtube.com/watch?v=...
    transcribir https://drive.google.com/file/d/.../view --cookies-navegador chrome
    transcribir ~/Descargas/audios-whatsapp/          (toda la carpeta)
    transcribir grabar                                 (graba lo que suena)
    transcribir                                        (te pregunta todo)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from . import __version__
from .fuentes import ErrorFuente, Fuente, carpeta_temporal, desde_archivo, desde_url, es_url, expandir
from .salida import FORMATOS_VALIDOS, guardar, nombre_seguro
from .segmentos import Segmento, formato_tiempo
from .transcripcion import MODELO_POR_DEFECTO, MODELOS, transcribir


def _formatos(texto: str) -> List[str]:
    formatos = [f.strip().lower().lstrip(".") for f in texto.split(",") if f.strip()]
    invalidos = [f for f in formatos if f not in FORMATOS_VALIDOS]
    if invalidos or not formatos:
        raise argparse.ArgumentTypeError(
            f"formato inválido: {', '.join(invalidos) or texto!r}. Opciones: {', '.join(FORMATOS_VALIDOS)}")
    return formatos


def _duracion(texto: str) -> float:
    """'90' o '90m' -> minutos; '1h30m', '45s' también valen."""
    import re
    texto = texto.strip().lower()
    if texto.isdigit():
        return int(texto) * 60.0
    m = re.fullmatch(r"(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?", texto)
    if not m or not any(m.groups()):
        raise argparse.ArgumentTypeError(f"duración inválida: {texto!r} (ejemplos: 90, 90m, 1h30m)")
    h, mi, s = (int(g or 0) for g in m.groups())
    return h * 3600.0 + mi * 60 + s


def _opciones_comunes(p: argparse.ArgumentParser) -> None:
    p.add_argument("-m", "--modelo", default=MODELO_POR_DEFECTO, choices=MODELOS,
                   help=f"precisión vs. velocidad (por defecto: {MODELO_POR_DEFECTO}). "
                        "'turbo' es mucho más preciso; conviene si tenés placa de video.")
    p.add_argument("-i", "--idioma", default="es",
                   help="código de idioma del audio: es, en, pt, fr... "
                        "o 'auto' para que lo detecte (por defecto: es)")
    p.add_argument("-o", "--salida", type=Path, default=Path("transcripciones"),
                   help="carpeta donde guardar los textos (por defecto: ./transcripciones)")
    p.add_argument("-f", "--formatos", type=_formatos, default=["txt", "md"],
                   help="formatos a generar, separados por coma: txt, md, srt (por defecto: txt,md)")
    p.add_argument("--cpu", action="store_true",
                   help="forzar el uso del procesador aunque haya placa de video")


def _parser_principal() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="transcribir",
        description="Pasa video y audio a texto: archivos, audios de WhatsApp, carpetas o links "
                    "(YouTube, Google Drive, Vimeo, Instagram, TikTok y +1000 sitios).",
        epilog="Otros comandos:  'transcribir grabar' graba lo que suena en la compu y lo transcribe; "
               "'transcribir dispositivos' lista las entradas/salidas de audio.",
    )
    p.add_argument("fuentes", nargs="*", help="archivos, carpetas o links (podés pasar varios)")
    _opciones_comunes(p)
    p.add_argument("--cookies-navegador", metavar="NAVEGADOR",
                   help="usar tu sesión del navegador para videos privados o compartidos con vos "
                        "(chrome, firefox, edge, brave, opera, safari...)")
    p.add_argument("--subtitulos", action="store_true",
                   help="si el video ya tiene subtítulos escritos por una persona, usarlos "
                        "en vez de transcribir (instantáneo)")
    p.add_argument("--conservar-audio", action="store_true",
                   help="guardar también el audio descargado de los links")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def _parser_grabar() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="transcribir grabar",
        description="Graba lo que suena en la compu (o el micrófono) y después lo transcribe. "
                    "Funciona con cualquier cosa que se pueda reproducir.",
    )
    _opciones_comunes(p)
    p.add_argument("-t", "--titulo", help="nombre para la transcripción (por defecto: fecha y hora)")
    p.add_argument("-d", "--duracion", type=_duracion,
                   help="detener sola después de este tiempo: 90 (minutos), 1h30m, 45s...")
    p.add_argument("--microfono", action="store_true",
                   help="grabar el micrófono en vez de la salida de audio (ej.: una clase presencial)")
    p.add_argument("--dispositivo", help="nombre (o parte del nombre) de la entrada a grabar; "
                                         "ver 'transcribir dispositivos'")
    p.add_argument("--solo-grabar", action="store_true",
                   help="solo guardar el audio, sin transcribir (para transcribirlo más tarde)")
    return p


def _procesar(fuente: Fuente, args) -> None:
    idioma = None if args.idioma == "auto" else args.idioma
    if fuente.subtitulos:
        segmentos = fuente.subtitulos
        duracion = segmentos[-1].fin
    else:
        args.salida.mkdir(parents=True, exist_ok=True)
        # Se va guardando a medida que avanza: si se corta, queda lo hecho.
        parcial = args.salida / (nombre_seguro(fuente.titulo) + ".parcial.txt")
        with parcial.open("w", encoding="utf-8") as f:
            def al_segmento(seg: Segmento) -> None:
                f.write(f"[{formato_tiempo(seg.inicio)}] {seg.texto}\n")
                f.flush()

            segmentos, duracion = transcribir(fuente.audio, args.modelo, idioma,
                                              "cpu" if args.cpu else "auto", al_segmento)
        parcial.unlink()
    if not segmentos:
        print("  No se detectó voz en este audio.")
        return
    for ruta in guardar(segmentos, fuente.titulo, fuente.origen, duracion, args.salida, args.formatos):
        print(f"  Listo: {ruta}")


def _transcribir_fuentes(args) -> int:
    entradas = expandir(args.fuentes)
    errores = 0
    for n, entrada in enumerate(entradas, 1):
        print(f"\n[{n}/{len(entradas)}] {entrada}")
        try:
            if es_url(entrada):
                with carpeta_temporal() as tmp:
                    fuente = desde_url(entrada, Path(tmp), args.cookies_navegador,
                                       args.subtitulos, None if args.idioma == "auto" else args.idioma)
                    if args.conservar_audio and fuente.audio:
                        args.salida.mkdir(parents=True, exist_ok=True)
                        copia = args.salida / (nombre_seguro(fuente.titulo) + fuente.audio.suffix)
                        copia.write_bytes(fuente.audio.read_bytes())
                        print(f"  Audio guardado: {copia}")
                    _procesar(fuente, args)
            else:
                _procesar(desde_archivo(entrada), args)
        except ErrorFuente as e:
            errores += 1
            print(f"  {e}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\nCancelado. Lo transcripto hasta ahora quedó en el archivo .parcial.txt.")
            return 130
        except Exception as e:  # que un archivo roto no frene una carpeta entera
            errores += 1
            print(f"  Error con {entrada}: {e}", file=sys.stderr)
    if len(entradas) > 1:
        print(f"\nTerminado: {len(entradas) - errores} de {len(entradas)} bien.")
    return 1 if errores else 0


def _grabar(argv: List[str]) -> int:
    from .grabacion import grabar
    args = _parser_grabar().parse_args(argv)
    titulo = args.titulo or f"Grabación {datetime.now():%Y-%m-%d %H-%M}"
    args.salida.mkdir(parents=True, exist_ok=True)
    audio = args.salida / (nombre_seguro(titulo) + ".wav")
    try:
        grabar(audio, args.microfono, args.dispositivo, args.duracion)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"Audio guardado: {audio}")
    if args.solo_grabar:
        return 0
    try:
        _procesar(Fuente(titulo=titulo, origen="grabación del audio de la compu"
                         if not args.microfono else "grabación del micrófono", audio=audio), args)
    except KeyboardInterrupt:
        print(f"\nCancelado. El audio sigue en {audio}; podés transcribirlo después con:\n"
              f'    transcribir "{audio}"')
        return 130
    return 0


def _interactivo() -> Optional[List[str]]:
    print(f"Transcriptor {__version__} — pasá video o audio a texto.\n")
    print("Pegá un link, o arrastrá acá un archivo o carpeta (varios separados por Enter).")
    print("Escribí 'grabar' para grabar lo que suena en la compu. Enter vacío para empezar.\n")
    entradas = []
    while True:
        try:
            linea = input("> ").strip().strip('"').strip("'")
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if not linea:
            break
        if linea.lower() == "grabar":
            return ["grabar"]
        entradas.append(linea)
    return entradas or None


def main(argv: Optional[List[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        argv = _interactivo()
        if argv is None:
            return 0
    if argv[0] == "grabar":
        return _grabar(argv[1:])
    if argv[0] == "dispositivos":
        from .grabacion import listar_dispositivos
        try:
            listar_dispositivos()
        except RuntimeError as e:
            print(e, file=sys.stderr)
            return 1
        return 0
    args = _parser_principal().parse_args(argv)
    if not args.fuentes:
        _parser_principal().print_help()
        return 2
    return _transcribir_fuentes(args)
