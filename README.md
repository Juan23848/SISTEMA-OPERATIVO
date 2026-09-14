# Antü OS

**Un sistema operativo basado en Linux, tan fácil de programar y mantener como
Linux, con la robustez y el entorno gráfico familiar de Windows.**

*Antü* significa "sol" en mapudungún: la luz que se abre paso en la
oscuridad. Es la idea detrás de este proyecto y de su identidad visual.

Antü OS es una distribución basada en Debian/Ubuntu que reemplaza el
escritorio por defecto con un entorno gráfico propio inspirado en Windows,
manteniendo por debajo toda la base técnica de Linux: kernel, gestor de
paquetes (APT), compatibilidad de hardware y drivers.

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
- **Entorno gráfico tipo Windows**: menú inicio, barra de tareas, bandeja del
  sistema y explorador de archivos con una experiencia familiar para usuarios
  de Windows, pero corriendo sobre entornos de escritorio Linux existentes
  (XFCE / Cinnamon / KDE Plasma según la edición) con temas y layouts propios.
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

Este proyecto está arrancando. Ver [`docs/ROADMAP.md`](docs/ROADMAP.md) para
el plan de trabajo y el estado actual de cada edición.

## Contribuir

Cualquier mejora, corrección o nueva funcionalidad es bienvenida. Abrí un
issue o un pull request.

## Licencia

El código, los scripts y los assets de marca propios de este proyecto están
bajo licencia [MIT](LICENSE). El software de terceros que se empaqueta
dentro de cada edición (entornos de escritorio, aplicaciones, el kernel
Linux, etc.) mantiene sus propias licencias originales.
