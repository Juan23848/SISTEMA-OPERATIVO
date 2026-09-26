# Antü OS

**Un sistema operativo que no te obliga a elegir entre la apertura de Linux
y no perder nada de lo que ya usás en Windows.**

*Antü* significa "sol" en mapudungún: la luz que se abre paso en la
oscuridad. Es la idea detrás de este proyecto y de su identidad visual.

Antü OS está basado en Linux (Debian) — eso no es negociable, es la base
técnica que hereda seguridad, compatibilidad de hardware y un ecosistema de
paquetes enorme. Lo que **sí** es el objetivo del proyecto es que, usándolo
para lo cotidiano (oficina, navegar, trabajar con archivos, y en la edición
Pro también jugar), no sientas ninguna limitación práctica frente a Windows.
No es un "Linux con apariencia de Windows": la interfaz familiar es solo la
puerta de entrada para no perder tiempo reaprendiendo algo que ya sabés
usar. El trabajo real está una capa más abajo — interoperabilidad de
verdad, no cosmética:

- **Office real**, no una alternativa aproximada: un asistente instala tu
  propio Microsoft Office corriendo sobre Wine (no podemos incluir el
  instalador de Office en la ISO — es software con licencia propia de
  Microsoft — pero sí podemos hacer que instalarlo sea un asistente de dos
  clics en vez de una investigación).
- **Archivos van y vienen sin fricción**: discos/pendrives NTFS/exFAT/FAT32
  montan solos, `.zip`/`.rar`/`.7z` se abren de verdad (no solo con la
  interfaz, con los códecs reales), y Samba te hace ver en la red igual que
  una PC Windows.
- **Cualquier `.exe`/`.msi`** corre con solo hacer doble clic (Wine real,
  sin necesitar Windows instalado), y Chromium viene de fábrica con el
  repositorio oficial de Google Chrome ya configurado si preferís el
  navegador real de Google.
- **Juegos en hardware potente (edición Pro)**: en el radar, con una
  limitación que nombramos de frente en vez de esconder — los pocos juegos
  con anticheat a nivel de kernel (ej. Riot Vanguard) bloquean Linux por
  decisión del fabricante del juego, no por algo que Antü pueda resolver.
  Todo lo demás es un objetivo real, no una promesa vacía.

Todo esto vive por debajo de un entorno gráfico propio con la identidad
visual de Antü (ver `docs/ARCHITECTURE.md`, "Íconos propios"), corriendo
sobre XFCE/Cinnamon/KDE Plasma según la edición.

El proyecto se distribuye en **tres ediciones**, pensadas para distinto
hardware y distinto uso:

| Edición | Carpeta | Hardware objetivo | Inspiración de escritorio |
|---|---|---|---|
| **Antü Legacy** | [`editions/antu-legacy`](editions/antu-legacy) | PCs viejas, equivalentes a las que corrían Windows XP (32 bits, poca RAM) | Escritorio clásico, mínimo consumo de recursos |
| **Antü Standard** | [`editions/antu-standard`](editions/antu-standard) | Uso doméstico/oficina, equivalente a Windows 7 en adelante | Escritorio moderno pero liviano, barra de tareas y menú inicio clásicos |
| **Antü Pro** | [`editions/antu-pro`](editions/antu-pro) | Hardware potente actual | Escritorio con efectos visuales completos, mejor aprovechamiento de CPU/GPU/multinúcleo |

## Filosofía del proyecto

- **Base sólida y probada**: no reinventamos el kernel ni el sistema de
  paquetes. Usamos Debian/Ubuntu como base para heredar compatibilidad de
  hardware, seguridad y un ecosistema de paquetes enorme.
- **Fácil de programar**: todo el sistema se define como código versionado
  (listas de paquetes, scripts, temas, configuración), reproducible con
  [`live-build`](https://manpages.debian.org/testing/live-build/lb.1.en.html).
  No hay pasos manuales ocultos.
- **Sin límite práctico frente a Windows**: no es un objetivo estético, es
  el criterio con el que se decide qué entra al proyecto — Office real (no
  una alternativa aproximada), archivos que van y vienen sin fricción,
  cualquier `.exe`/`.msi` corriendo con doble clic. La interfaz familiar
  (menú inicio, barra de tareas, bandeja del sistema) es la puerta de
  entrada para no reaprender nada, corriendo sobre entornos de escritorio
  Linux existentes (XFCE / Cinnamon / KDE Plasma según la edición) con
  temas y layouts propios — pero el objetivo real está en la capa de abajo.
- **Tres perfiles, un mismo proyecto**: comparten configuración común
  (`shared/`) y solo difieren en lo que tiene sentido que difiera: paquetes,
  entorno de escritorio, y ajustes de rendimiento.

## Estructura del repositorio

```
SISTEMA-OPERATIVO/
├── docs/                    # Documentación técnica y de arquitectura
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   └── BUILD.md
├── editions/
│   ├── antu-legacy/         # Edición para hardware antiguo (estilo XP)
│   ├── antu-standard/       # Edición hogar/oficina (estilo Windows 7+)
│   └── antu-pro/            # Edición de alto rendimiento
├── shared/
│   ├── branding/            # Logo, wallpapers y assets comunes a las 3 ediciones
│   └── scripts/             # Utilidades compartidas por los scripts de build
└── scripts/
    ├── build.sh             # Compila la ISO de una edición con live-build
    └── test-qemu.sh         # Bootea la ISO resultante en una VM QEMU
```

Cada edición tiene su propio `README.md` con el detalle de paquetes, entorno
gráfico y requisitos de hardware.

## Cómo compilar una edición

Ver [`docs/BUILD.md`](docs/BUILD.md) para la guía completa. En resumen:

```bash
# Requiere Debian/Ubuntu con live-build instalado
sudo apt install live-build

./scripts/build.sh antu-standard
```

Esto genera una imagen ISO booteable en `editions/antu-standard/build/`.

## Estado del proyecto

Antü Standard ya compila una ISO real y arranca de punta a punta hasta un
escritorio Cinnamon funcional (probado en QEMU, con la marca de Antü propia
también en el menú de arranque). Legacy y Pro comparten la misma base y
están en proceso de la misma validación. Ver
[`docs/ROADMAP.md`](docs/ROADMAP.md) para el detalle y el estado actual de
cada edición.

## Contribuir

Cualquier mejora, corrección o nueva funcionalidad es bienvenida. Abrí un
issue o un pull request.

## Licencia

El código, los scripts y los assets de marca propios de este proyecto están
bajo licencia [MIT](LICENSE). El software de terceros que se empaqueta
dentro de cada edición (entornos de escritorio, aplicaciones, el kernel
Linux, etc.) mantiene sus propias licencias originales.
