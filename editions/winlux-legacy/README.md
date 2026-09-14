# WinLux Legacy

Edición pensada para PCs con hardware equivalente a la era de **Windows XP**:
procesadores de 1-2 núcleos, 512MB–2GB de RAM, sin aceleración 3D confiable.

## Características

- Arquitecturas: `i386` (32 bits) y `amd64`.
- Escritorio: **XFCE**, sin compositor activado por defecto.
- Apariencia: barra de tareas simple y menú inicio con lista de programas,
  estilo clásico.
- Paquetes mínimos: se prioriza el arranque rápido y el bajo consumo de RAM
  sobre las funcionalidades extra.

## Compilar esta edición

Desde la raíz del repositorio:

```bash
./scripts/build.sh winlux-legacy
```

Ver [`docs/BUILD.md`](../../docs/BUILD.md) para más detalle.

## Estructura

```
config/
├── auto/               # Scripts config/build/clean de live-build
├── package-lists/      # Paquetes de escritorio y aplicaciones
├── includes.chroot/    # Branding y archivos de configuración propios
└── hooks/              # Scripts que corren durante el build
```
