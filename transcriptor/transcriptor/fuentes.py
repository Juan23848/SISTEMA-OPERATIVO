"""Resuelve "lo que me pasaste" (archivo, carpeta o link) en un audio local listo para transcribir.

- Archivos locales: cualquier formato que entienda FFmpeg (mp4, mkv, avi, mov,
  mp3, m4a, wav, y los .opus/.ogg de WhatsApp). No hace falta convertirlos.
- Carpetas: se transcriben todos los archivos de audio/video que tengan adentro.
- Links: yt-dlp, que soporta más de mil sitios (YouTube, Google Drive, Vimeo,
  Instagram, TikTok, Facebook, X/Twitter, Twitch, links directos a .mp4/.m3u8...).
  Para Google Drive descarga el stream del reproductor, así que funciona aunque
  el dueño haya deshabilitado el botón de descarga, siempre que vos puedas
  reproducir el video. Si el archivo es privado (compartido con tu cuenta),
  se usan las cookies de tu navegador para entrar como vos.
"""

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .segmentos import Segmento

EXTENSIONES_MEDIA = {
    ".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv", ".m4v", ".3gp", ".mpg", ".mpeg", ".ts",
    ".mp3", ".m4a", ".wav", ".ogg", ".opus", ".oga", ".flac", ".aac", ".wma", ".amr", ".aiff", ".aif",
}


@dataclass
class Fuente:
    titulo: str
    origen: str  # ruta o URL original, para dejarlo anotado en la transcripción
    audio: Optional[Path] = None
    # Si el sitio ya tenía subtítulos escritos por una persona y se pidieron,
    # vienen acá y no hace falta pasar por Whisper.
    subtitulos: Optional[List[Segmento]] = None


class ErrorFuente(Exception):
    pass


def es_url(texto: str) -> bool:
    return bool(re.match(r"^https?://", texto.strip(), re.IGNORECASE))


def archivos_de_carpeta(carpeta: Path) -> List[Path]:
    return sorted(p for p in carpeta.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONES_MEDIA)


def expandir(entradas: List[str]) -> List[str]:
    """Reemplaza cada carpeta por los archivos de audio/video que contiene."""
    resultado = []
    for entrada in entradas:
        ruta = Path(entrada).expanduser()
        if not es_url(entrada) and ruta.is_dir():
            encontrados = archivos_de_carpeta(ruta)
            if not encontrados:
                print(f"Aviso: no encontré archivos de audio/video en {ruta}")
            resultado += [str(p) for p in encontrados]
        else:
            resultado.append(entrada)
    return resultado


def desde_archivo(entrada: str) -> Fuente:
    ruta = Path(entrada).expanduser()
    if not ruta.is_file():
        raise ErrorFuente(f"No existe el archivo: {ruta}")
    return Fuente(titulo=ruta.stem, origen=str(ruta.resolve()), audio=ruta)


def _opciones_ytdlp(carpeta: Path, cookies_navegador: Optional[str]) -> dict:
    opciones = {
        # Solo el audio: es lo único que necesitamos y pesa muchísimo menos.
        # Si el sitio no separa audio y video, baja el archivo más liviano.
        "format": "bestaudio/worst",
        "outtmpl": str(carpeta / "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 10,
        "fragment_retries": 10,
    }
    if cookies_navegador:
        # yt-dlp acepta "chrome", "firefox", "edge", "brave", "opera", "safari",
        # "chromium", "vivaldi" y opcionalmente un perfil: "chrome:Profile 1".
        nav, _, perfil = cookies_navegador.partition(":")
        opciones["cookiesfrombrowser"] = (nav, perfil or None, None, None)
    return opciones


def _elegir_subtitulos(info: dict, idioma: Optional[str]) -> Optional[dict]:
    """Devuelve la pista de subtítulos manuales (no automáticos) que mejor coincide con el idioma."""
    manuales = info.get("subtitles") or {}
    if not manuales:
        return None
    candidatos = [k for k in manuales if idioma and k.split("-")[0] == idioma] or (
        [] if idioma else list(manuales)
    )
    for clave in candidatos:
        for pista in manuales[clave]:
            if pista.get("ext") == "vtt":
                return pista
    return None


def parsear_vtt(contenido: str) -> List[Segmento]:
    segmentos = []
    patron = re.compile(r"(\d{1,2}:)?(\d{2}):(\d{2})[.,](\d{3})")

    def a_segundos(m):
        h = int(m.group(1)[:-1]) if m.group(1) else 0
        return h * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000

    for bloque in re.split(r"\n\s*\n", contenido.replace("\r", "")):
        lineas = bloque.strip().split("\n")
        for i, linea in enumerate(lineas):
            if "-->" in linea:
                tiempos = list(patron.finditer(linea))
                if len(tiempos) < 2:
                    break
                texto = " ".join(lineas[i + 1:])
                texto = re.sub(r"<[^>]+>", "", texto).strip()  # quita etiquetas de estilo
                if texto and (not segmentos or segmentos[-1].texto != texto):
                    segmentos.append(Segmento(a_segundos(tiempos[0]), a_segundos(tiempos[1]), texto))
                break
    return segmentos


def desde_url(url: str, carpeta: Path, cookies_navegador: Optional[str] = None,
              usar_subtitulos: bool = False, idioma: Optional[str] = None) -> Fuente:
    try:
        import yt_dlp
    except ImportError as e:
        raise ErrorFuente("Falta yt-dlp. Instalalo con: pip install -U yt-dlp") from e

    opciones = _opciones_ytdlp(carpeta, cookies_navegador)
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=False)
            if info.get("_type") == "playlist":
                entradas = [e for e in (info.get("entries") or []) if e]
                if not entradas:
                    raise ErrorFuente("El link es una lista vacía.")
                info = entradas[0]
            titulo = info.get("title") or info.get("id") or "transcripcion"

            if usar_subtitulos:
                pista = _elegir_subtitulos(info, idioma)
                if pista:
                    print("  Encontré subtítulos escritos por una persona; los uso en vez de transcribir.")
                    contenido = ydl.urlopen(pista["url"]).read().decode("utf-8", "replace")
                    segmentos = parsear_vtt(contenido)
                    if segmentos:
                        return Fuente(titulo=titulo, origen=url, subtitulos=segmentos)

            print("  Descargando el audio...")
            info = ydl.process_ie_result(info, download=True)
            descargas = info.get("requested_downloads") or [info]
            ruta = Path(descargas[0].get("filepath") or ydl.prepare_filename(info))
    except yt_dlp.utils.DownloadError as e:
        raise ErrorFuente(_explicar_error(str(e), url, cookies_navegador)) from e

    if not ruta.exists():
        raise ErrorFuente(f"yt-dlp terminó pero no encuentro el archivo descargado ({ruta}).")
    return Fuente(titulo=titulo, origen=url, audio=ruta)


def _explicar_error(mensaje: str, url: str, cookies_navegador: Optional[str]) -> str:
    consejos = [f"No pude bajar el audio de {url}.", f"Detalle técnico: {mensaje.strip()}", ""]
    bajo = mensaje.lower()
    privado = any(p in bajo for p in ("login", "sign in", "private", "403", "401", "cookies", "permission"))
    if privado and not cookies_navegador:
        consejos.append("Parece que hace falta estar logueado. Probá agregando, por ejemplo:")
        consejos.append("    --cookies-navegador chrome      (o firefox, edge, brave...)")
        consejos.append("con una sesión abierta en ese navegador que pueda ver el video.")
    elif "unsupported url" in bajo:
        consejos.append("Ese sitio no está soportado directamente. Opciones:")
        consejos.append("  - Si el video está incrustado en otra página (campus, Moodle, etc.), abrí")
        consejos.append("    las herramientas de desarrollador del navegador (F12 > Red), filtrá por")
        consejos.append("    'm3u8' o 'mp4', y pasale ese link directo a este programa.")
    else:
        consejos.append("Primero probá actualizar yt-dlp (los sitios cambian seguido):")
        consejos.append("    pip install -U yt-dlp")
    consejos.append("Si nada funciona, el último recurso siempre anda: reproducilo y grabalo con")
    consejos.append("    transcribir grabar")
    return "\n".join(consejos)


def carpeta_temporal() -> tempfile.TemporaryDirectory:
    return tempfile.TemporaryDirectory(prefix="transcriptor-")
