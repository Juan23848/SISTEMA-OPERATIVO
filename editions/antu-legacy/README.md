# Antü Legacy

Edición pensada para PCs modestas: Celeron o i3/i5 desde ~3ra generación en
adelante, con 4GB de RAM, sin aceleración 3D confiable. "Legacy" describe el
perfil de escritorio (liviano, sin efectos), no la arquitectura del CPU.

## Características

- Arquitectura: `amd64` (64 bits), igual que Standard y Pro. Todo el hardware
  al que apunta esta edición ya es de 64 bits desde hace más de una década;
  usar `i386` solo perdería compatibilidad con equipos modernos sin arranque
  BIOS/CSM (UEFI puro), sin sumar nada a cambio.
- Escritorio: **XFCE**, sin compositor activado por defecto.
- Apariencia: identidad Antü con glow reducido y sin blur (colores planos),
  para que se vea bien incluso sin aceleración gráfica.
- Paquetes mínimos: se prioriza el arranque rápido y el bajo consumo de RAM
  sobre las funcionalidades extra.

## Compilar esta edición

Desde la raíz del repositorio:

```bash
./scripts/build.sh antu-legacy
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
