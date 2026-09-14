# Arquitectura de WinLux OS

## Idea general

WinLux OS **no** es un kernel ni un sistema operativo escrito desde cero.
Es una **distribución Linux personalizada** (un "respin" de Debian/Ubuntu)
que:

1. Usa el **kernel Linux** y la base de Debian/Ubuntu tal cual, para heredar
   soporte de hardware, drivers, seguridad y actualizaciones.
2. Reemplaza la capa de **escritorio y experiencia de usuario** por una
   configuración propia (tema, layout, atajos, menú inicio, barra de tareas)
   inspirada en Windows.
3. Se empaqueta como **imagen ISO booteable e instalable** usando
   [`live-build`](https://manpages.debian.org/testing/live-build/lb.1.en.html),
   la herramienta oficial de Debian para construir distribuciones live/
   instalables.

Este enfoque es el que usan distribuciones reales y exitosas con el mismo
objetivo (dar a Linux una cara familiar para usuarios de Windows), como
Zorin OS o Linuxfx/Windowsfx. Nos permite tener algo **robusto y usable en
semanas**, en vez de años, sin sacrificar la posibilidad de personalizar
todo el sistema.

## Por qué no un kernel/OS desde cero

Escribir un sistema operativo completo desde cero (kernel, drivers,
scheduler, stack de red, sistema de archivos, entorno gráfico) es un
proyecto de investigación de varios años-persona, y aun así no llegaría a
tener la compatibilidad de hardware ni la robustez de Linux, que ya tiene
más de 30 años de desarrollo. Por eso la estrategia de este proyecto es
**construir sobre Linux**, no competir con él.

## Componentes por capa

| Capa | Tecnología | Notas |
|---|---|---|
| Kernel | Linux (kernel de Debian/Ubuntu) | Sin modificaciones en Legacy/Standard. En Pro se puede usar un kernel más nuevo (`linux-image-*-generic` o `liquorix`) para mejor soporte de hardware reciente. |
| Init / servicios | systemd | Estándar de Debian/Ubuntu. |
| Gestor de paquetes | APT / dpkg | Mismo ecosistema que Debian/Ubuntu, sin cambios. |
| Entorno gráfico base | X11 (Wayland opcional en Pro) | Depende de la edición. |
| Escritorio | XFCE (Legacy) / Cinnamon o XFCE (Standard) / KDE Plasma (Pro) | Elegidos por consumo de recursos vs. features. |
| Apariencia "Windows" | Temas GTK/Qt, iconos, layout de panel/taskbar, menú inicio | Vive en `shared/branding/` y en `editions/*/branding/`. |
| Build system | `live-build` | Config declarativa en `editions/*/config/`. |

## Las tres ediciones

### WinLux Legacy (`editions/winlux-legacy`)

- Público: PCs con hardware equivalente a la era de Windows XP (Pentium 4 /
  Core 2 Duo, 512MB–2GB RAM, sin aceleración 3D confiable).
- Escritorio: **XFCE**, con compositor desactivado por defecto, tema visual
  tipo "clásico" (barra de tareas simple, menú inicio con lista de programas).
- Arquitectura: `i386` (32 bits) además de `amd64`, para máxima compatibilidad.
- Prioridad: arrancar rápido y consumir poca RAM, no efectos visuales.

### WinLux Standard (`editions/winlux-standard`)

- Público: uso doméstico/oficina, hardware equivalente a Windows 7 en
  adelante (Core i3+, 4GB+ RAM).
- Escritorio: **Cinnamon** (o XFCE con compositor activado, a definir en la
  implementación) con menú inicio, barra de tareas y bandeja del sistema
  con la disposición clásica de Windows 7/10.
- Arquitectura: `amd64`.
- Prioridad: balance entre estética moderna y bajo consumo de recursos.

### WinLux Pro (`editions/winlux-pro`)

- Público: hardware potente (multinúcleo, GPU dedicada, SSD, 16GB+ RAM).
- Escritorio: **KDE Plasma**, con todos los efectos de composición
  habilitados, soporte Wayland, y ajustes de kernel/scheduler orientados a
  aprovechar múltiples núcleos y GPU.
- Arquitectura: `amd64` (con perfiles opcionales para `arm64` a futuro).
- Prioridad: máximo aprovechamiento del hardware disponible, sin resignar
  robustez.

## Flujo de build

```
editions/<edicion>/config/   →  lb config (auto-generado por live-build)
                              →  lb build
                              →  editions/<edicion>/build/*.iso
```

Ver [`BUILD.md`](BUILD.md) para el detalle paso a paso.
