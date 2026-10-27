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

Por cada video/audio, en `Documentos/Transcripciones/`:

| Archivo | Para qué |
|---|---|
| `Nombre.docx` | **Documento de Word** con título, datos de la clase y el texto en párrafos. Cada párrafo empieza con el minuto en gris chiquito (`[01:23:45]`), para volver al video justo en la parte que no entendiste. Se abre en Word (Windows, o Antü con el asistente de Office), en LibreOffice y en Google Docs. Viene en Calibri y con el corrector en español. |
| `Nombre.txt` | Texto corrido en párrafos, sin nada más. Para copiar y pegar, o pasárselo a una IA. |
| `Nombre.md` | (opcional) Igual que el .txt, pero con el minuto en cada párrafo. |
| `Nombre.srt` | (opcional) Subtítulos para ver el video en VLC con texto. |

Y si querés **el texto para pegarlo directo** en otro lado, agregá `--copiar`:
al terminar queda en el portapapeles y lo pegás con Ctrl+V. Si abrís el
programa sin opciones (escribiendo `transcribir` solo, o desde el menú en Antü),
copia el texto y abre el documento automáticamente.

Mientras transcribe va guardando un `Nombre.parcial.txt`: si se corta la luz
o cerrás la ventana en la hora 2 de 3, lo hecho no se pierde.

## Instalación

### Windows (lo más fácil: sin instalar nada)

1. Bajá **Transcriptor-Windows.zip** de la
   [página de descarga](https://github.com/Juan23848/SISTEMA-OPERATIVO/releases/tag/transcriptor-windows).
2. Descomprimilo (clic derecho → *Extraer todo...*) donde quieras, por ejemplo en Documentos.
3. Abrí la carpeta y hacé doble clic en **transcribir.exe**. La primera vez
   Windows puede decir *"Windows protegió su PC"*, porque el programa no está
   firmado: *Más información* → *Ejecutar de todas formas*.

Se usa así:
- **Doble clic** en `transcribir.exe`: pegás un link o arrastrás el archivo a
  la ventana, Enter dos veces, y listo.
- O **arrastrás** videos, audios o una carpeta **encima del ícono** de `transcribir.exe`.

Al terminar se abre el Word y el texto queda copiado (Ctrl+V). Tip: clic
derecho en `transcribir.exe` → *Enviar a* → *Escritorio (crear acceso directo)*.

En el `.exe` la placa de video está apagada por defecto, porque sin CUDA
instalado haría que el programa se cierre de golpe. Si tenés NVIDIA con
CUDA 12 y cuDNN 9, usá `--gpu`.

Esa versión la arma GitHub solo (`.github/workflows/transcriptor-windows.yml`)
cada vez que cambia el código, y antes de publicarla la prueba transcribiendo
un audio real.

### Windows con Python (para desarrollar)

Instalá Python 3.9 o más nuevo desde [python.org](https://www.python.org/downloads/)
(tildá *"Add python.exe to PATH"*). Después, en PowerShell:

```powershell
pip install pipx
pipx ensurepath
# cerrá y volvé a abrir la terminal
pipx install "ruta\a\esta\carpeta\transcriptor"
```

**Antü OS** (y cualquier Debian/Ubuntu): desde esta carpeta,

```bash
./instalar-antu.sh
```

Instala lo necesario (pipx, ffmpeg y xclip para copiar el texto), el
programa, y un ícono **"Transcriptor"** en el menú de aplicaciones: lo abrís
desde ahí como cualquier otro programa, pegás el link o arrastrás el archivo,
y al terminar se abre el Word. Los `.docx` se abren con Word si lo instalaste
con el asistente de Office de Antü; si no, con el programa que tengas para
documentos.

**Otras distribuciones de Linux**:

```bash
sudo apt install pipx ffmpeg xclip     # o el equivalente de tu distro
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
| `--copiar` | Copia el texto al portapapeles al terminar (pegalo con Ctrl+V). |
| `--abrir` | Abre el documento de Word al terminar. |
| `-o carpeta` | Dónde guardar los textos (por defecto: `Documentos/Transcripciones`). |
| `-f docx,txt,md,srt` | Qué formatos generar (por defecto: `docx,txt`). Ej.: `-f docx` solo Word. |
| `--cookies-navegador chrome` | Para videos privados o compartidos con tu cuenta (Drive de la facultad, etc.). Usa la sesión que ya tenés abierta en Chrome / Firefox / Edge / Brave. |
| `--subtitulos` | Si el video ya tiene subtítulos **escritos por una persona**, los usa directamente (instantáneo). Los automáticos de YouTube se ignoran porque Whisper los hace mejor. |
| `--conservar-audio` | Guarda también el audio bajado de un link. |
| `--cpu` / `--gpu` | Forzar procesador o placa de video NVIDIA. |

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
| Drive con descarga deshabilitada, pero compartido "con cualquier persona con el link" | `transcribir link`. El programa baja el mismo audio que usa el reproductor, así que no le importa que esté sacado el botón de descarga. |
| Drive compartido solo con tu cuenta (por ejemplo, la cuenta de la facultad) | `transcribir link --cookies-navegador firefox` con esa cuenta abierta en el navegador. **En Windows usá Firefox**: Chrome y Edge cifran sus cookies de una forma que yt-dlp no puede leer. En Antü/Linux, Chrome también funciona. |
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
  `transcribir "Documentos/Transcripciones/Grabación ....wav"`.

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
├── salida.py         # párrafos y archivos .docx / .txt / .md / .srt
├── sistema.py        # portapapeles, abrir archivos, carpeta Documentos
└── segmentos.py      # tipo común de fragmento con tiempo
windows/
├── construir.py      # arma transcribir.exe con PyInstaller
├── lanzador.py       # punto de entrada del .exe
└── LEEME.txt         # instrucciones que van dentro del .zip
```
