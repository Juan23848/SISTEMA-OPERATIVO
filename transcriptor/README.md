# Transcriptor

Pasa video y audio a texto desde casi cualquier lugar, para estudiar leyendo
en vez de mirar clases de horas.

- **Archivos**: videos descargados (mp4, mkv, avi, mov...), audios (mp3, m4a,
  wav...) y los audios de WhatsApp (`.opus` / `.ogg`), sin convertir nada.
- **Carpetas enteras**: le pasás la carpeta de audios de WhatsApp y transcribe todo.
- **Links**: YouTube, Google Drive, Vimeo, Instagram, TikTok, Facebook,
  X/Twitter, Twitch y más de mil sitios más (usa [yt-dlp](https://github.com/yt-dlp/yt-dlp)).
  En Drive funciona aunque el dueño haya **deshabilitado la descarga**,
  siempre que vos lo puedas reproducir.
- **Último recurso, que anda con todo**: graba lo que suena en la compu
  mientras reproducís el video (Zoom, Meet, Teams, el reproductor raro del
  campus...) y después lo transcribe. También puede grabar el micrófono en una
  clase presencial.

La transcripción la hace **Whisper** en tu propia compu: es gratis, no tiene
límite de minutos, no sube tus archivos a ningún lado y entiende muy bien el
español (incluido el rioplatense).

## Qué te devuelve

Por cada video/audio, en la carpeta `transcripciones/`:

| Archivo | Para qué |
|---|---|
| `Nombre.txt` | Texto corrido, separado en párrafos. Para leer, subrayar, resumir o pasárselo a una IA. |
| `Nombre.md` | Lo mismo pero cada párrafo empieza con el minuto (`**[01:23:45]**`), para volver al video justo en la parte que no entendiste. |
| `Nombre.srt` | (opcional, `-f txt,md,srt`) Subtítulos para ver el video en VLC con texto. |

Mientras transcribe va guardando un `Nombre.parcial.txt`: si se corta la luz
o cerrás la ventana en la hora 2 de 3, lo hecho no se pierde.

## Instalación

Necesitás **Python 3.9 o más nuevo**.

**Windows**: instalá Python desde [python.org](https://www.python.org/downloads/)
(tildá *"Add python.exe to PATH"*). Después, en una terminal (PowerShell):

```powershell
pip install pipx
pipx ensurepath
# cerrá y volvé a abrir la terminal
pipx install "ruta\a\esta\carpeta\transcriptor"
```

**Linux** (Debian/Ubuntu/Antü):

```bash
sudo apt install pipx ffmpeg
pipx install ./transcriptor
```

**macOS**:

```bash
brew install pipx ffmpeg
pipx install ./transcriptor
```

FFmpeg no es obligatorio para archivos locales, pero algunos sitios (YouTube
en ciertos casos) lo necesitan para descargar. En Windows: `winget install ffmpeg`.

La **primera vez** que transcribas se descarga el modelo de Whisper (entre
75 MB y 3 GB según cuál elijas). Después funciona sin internet.

## Uso

Lo más fácil: escribí `transcribir` solo y te va preguntando. Podés arrastrar
archivos a la terminal o pegar links.

```bash
transcribir clase-3.mp4
transcribir "PTT-20261027-WA0003.opus"
transcribir https://www.youtube.com/watch?v=XXXXXXXX
transcribir https://drive.google.com/file/d/XXXXXXXX/view
transcribir ~/Descargas/audios-whatsapp/          # toda una carpeta
transcribir clase1.mp4 clase2.mp4 https://...     # varios de una
transcribir grabar                                # grabar lo que suena (Ctrl+C para terminar)
```

### Opciones útiles

| Opción | Qué hace |
|---|---|
| `-m turbo` | Modelo más preciso (por defecto: `small`). Ver tabla de abajo. |
| `-i en` | El audio está en inglés (u otro: `pt`, `fr`, `it`...). `-i auto` lo detecta solo. Por defecto: español. |
| `-o carpeta` | Dónde guardar los textos. |
| `-f txt,md,srt` | Qué formatos generar. |
| `--cookies-navegador chrome` | Para videos privados o compartidos con tu cuenta (Drive de la facultad, etc.). Usa la sesión que ya tenés abierta en Chrome / Firefox / Edge / Brave. |
| `--subtitulos` | Si el video ya tiene subtítulos **escritos por una persona**, los usa directamente (instantáneo). Los automáticos de YouTube se ignoran porque Whisper los hace mejor. |
| `--conservar-audio` | Guarda también el audio bajado de un link. |
| `--cpu` | No usar la placa de video (si da errores de CUDA). |

### ¿Qué modelo uso?

| Modelo | Velocidad | Precisión | Cuándo |
|---|---|---|---|
| `tiny`, `base` | Muy rápido | Floja | Para probar o audios cortos y claros |
| `small` (por defecto) | Rápido | Buena | Cualquier notebook. Una clase de 1 h tarda aprox. 10–30 min en un procesador común |
| `medium` | Lento | Muy buena | Audio con ruido, si tenés tiempo |
| `turbo` | Rápido con GPU | Excelente | **La mejor opción si tenés placa NVIDIA**; en CPU, dejalo corriendo de noche |
| `large-v3` | El más lento | Excelente | Términos muy técnicos o audio muy malo |

## ¿De dónde viene el video? Qué hacer en cada caso

| Situación | Cómo |
|---|---|
| Video o audio en la compu | `transcribir archivo` |
| Audio de WhatsApp | En el celu: mantené apretado el audio → Compartir → mandátelo por mail/Drive, o copiá la carpeta `WhatsApp/Media/WhatsApp Voice Notes` a la compu. Después `transcribir archivo-o-carpeta`. En WhatsApp Web: menú del audio → Descargar. |
| YouTube (público o no listado) | `transcribir link` (probá `--subtitulos` primero, si el profe los subió es instantáneo) |
| Google Drive público | `transcribir link` |
| Drive compartido solo con tu cuenta, o con descarga deshabilitada | `transcribir link --cookies-navegador chrome` (con tu cuenta abierta en ese navegador). Si Chrome falla por las cookies cifradas, probá con Firefox. |
| Video incrustado en el campus / Moodle / una página | 1) Probá `transcribir link-de-la-página --cookies-navegador chrome`. 2) Si no: F12 → pestaña *Red* → reproducí el video → filtrá por `m3u8` o `mp4` → clic derecho → *Copiar URL* → `transcribir "esa URL"`. |
| Clase grabada en Zoom / Teams / Meet con link de reproducción | Igual que el anterior; si no anda, `transcribir grabar`. |
| Clase en vivo por Zoom/Meet/Teams | `transcribir grabar -t "Análisis - clase 5"` antes de que empiece, Ctrl+C al terminar. |
| Clase presencial | `transcribir grabar --microfono` (mejor si la compu está cerca del profe). |
| Cualquier otra cosa que no se deje bajar | Reproducila (podés ponerla a 1.5x o 2x) y `transcribir grabar`. Si suena, se transcribe. |

### Notas sobre `grabar`

- **Windows y Linux**: graba directamente lo que sale por los parlantes o
  auriculares, no hace falta instalar nada. Ojo: no silencies el video en el
  reproductor (ni la pestaña del navegador), porque entonces no sale sonido y
  no hay nada que grabar. Si no querés escucharlo, usá auriculares.
- **macOS**: el sistema no deja grabar la salida directamente. Instalá
  [BlackHole](https://existential.audio/blackhole/) (gratis), creá un
  "Dispositivo de salida múltiple" en *Configuración de Audio MIDI* con
  BlackHole + tus parlantes, y después: `transcribir grabar --dispositivo BlackHole`.
- `transcribir dispositivos` lista lo que se puede grabar, por si tenés
  varias placas de sonido o auriculares Bluetooth.
- `-d 1h30m` la detiene sola (útil si te vas a dormir con un video largo).
- `--solo-grabar` guarda el audio y lo podés transcribir más tarde con
  `transcribir "transcripciones/Grabación ....wav"`.

## Problemas comunes

- **"No pude bajar el audio..."**: los sitios cambian seguido. Primero
  actualizá: `pipx upgrade transcriptor` o `pipx runpip transcriptor install -U yt-dlp`.
  El mensaje de error te dice qué probar después.
- **Errores de CUDA / cuDNN**: usá `--cpu`.
- **Repite la misma frase muchas veces**: suele pasar en partes con música o
  silencio. Probá un modelo más grande (`-m medium` o `-m turbo`).
- **Es lento**: es normal en procesadores modestos con clases largas. Dejalo
  corriendo; podés transcribir una carpeta entera de una sola vez.

## Uso responsable

Pensado para estudiar material al que ya tenés acceso legítimo (tus clases,
material de tu cátedra, audios que te mandaron). Las transcripciones son para
uso personal: respetá los derechos de autor y la privacidad de quienes hablan
antes de compartirlas.

## Desarrollo

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Estructura:

```
transcriptor/
├── cli.py            # comandos y opciones (transcribir / grabar / dispositivos)
├── fuentes.py        # archivo, carpeta o link -> audio local (yt-dlp)
├── grabacion.py      # grabar la salida de audio o el micrófono (soundcard)
├── transcripcion.py  # Whisper (faster-whisper), con barra de progreso
├── salida.py         # párrafos y archivos .txt / .md / .srt
└── segmentos.py      # tipo común de fragmento con tiempo
```
