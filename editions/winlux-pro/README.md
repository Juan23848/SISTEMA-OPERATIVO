# WinLux Pro

Edición para **hardware potente actual**: multinúcleo, GPU dedicada, SSD,
16GB+ de RAM. Es la edición "WinLux" propiamente dicha: máximo
aprovechamiento del hardware sin resignar robustez.

## Características

- Arquitectura: `amd64`.
- Escritorio: **KDE Plasma**, con todos los efectos de composición
  habilitados y soporte Wayland.
- Audio: PipeWire + PulseAudio para mejor rendimiento y compatibilidad.
- Firmware: incluye `firmware-linux` y `firmware-misc-nonfree` para máxima
  compatibilidad con hardware reciente (GPU, WiFi, etc).
- Utilidades incluidas para diagnóstico y ajuste de rendimiento (`htop`,
  `cpufrequtils`, `gparted`).

## Compilar esta edición

Desde la raíz del repositorio:

```bash
./scripts/build.sh winlux-pro
```

Ver [`docs/BUILD.md`](../../docs/BUILD.md) para más detalle.

## Estructura

```
config/
├── auto/               # Scripts config/build/clean de live-build
├── package-lists/      # Paquetes de escritorio, aplicaciones y hardware
├── includes.chroot/    # Branding y archivos de configuración propios
└── hooks/              # Scripts que corren durante el build
```
