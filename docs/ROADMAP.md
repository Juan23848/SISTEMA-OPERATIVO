# Roadmap

## Estado actual

Existe el scaffold de las 3 ediciones (estructura de configuración de
`live-build`, listas de paquetes iniciales, branding real) y la
configuración de `live-build` de las 3 **ya fue probada y corre sin
errores** hasta el punto de descargar paquetes de Debian. Las 3 ediciones
también tienen ya un **shell de escritorio propio** (barra superior +
dock, con la identidad de Antü, ver `docs/ARCHITECTURE.md`) y Standard
suma un **lanzador con buscador** (rofi). **Todavía no se compiló ninguna
ISO completa**, porque eso requiere una máquina con acceso a internet a
los mirrors de Debian (no disponible en el entorno donde se desarrolló
este proyecto). Pese a eso, **Legacy y Standard sí se probaron con
sesiones de escritorio reales** (XFCE y Cinnamon, contra una pantalla
virtual) — no solo por sintaxis — y encontraron y corrigieron bugs reales
en el camino (ver `docs/ARCHITECTURE.md` y las capturas en
`docs/screenshots/`). Pro (KDE Plasma) todavía no se pudo probar así.

## Fase 0 — Scaffold (completa)

- [x] Definir arquitectura y las 3 ediciones.
- [x] Estructura de carpetas y documentación base.
- [x] Configuración inicial de `live-build` por edición (package-lists
      base, hooks, branding real).
- [x] Scripts `build.sh` y `test-qemu.sh`.
- [x] Validar que `lb config` y `lb build` corren sin errores en las 3
      ediciones (se instaló `live-build` y se corrió de verdad, no solo se
      escribió a mano). Esto encontró y corrigió 3 bugs reales:
      1. Los scripts `auto/build`/`auto/clean` no pasaban `noauto`, lo que
         causaba una **recursión infinita** (`lb build` volvía a ejecutar
         `auto/build`, que volvía a llamar a `lb build`...).
      2. `--mode debian` faltaba: sin él, `lb config` detecta el modo según
         el sistema operativo donde se compila, y en una máquina Ubuntu
         terminaría mezclando la distribución `bookworm` (Debian) con
         mirrors de Ubuntu, rompiendo el build.
      3. `winlux-legacy` (ahora `antu-legacy`) pedía `i386 amd64` juntas,
         pero `live-build` solo soporta **una arquitectura por
         configuración**. Se dejó en `i386` (compatible con hardware de
         32 y 64 bits).
- [ ] Primera compilación **completa** de una ISO (Standard), en una
      máquina con acceso real a los mirrors de Debian.

## Fase 1 — Antü Standard (MVP)

Se prioriza esta edición porque cubre el público más amplio (uso
doméstico/oficina).

- [ ] Compilar ISO booteable en modo live (sin instalar).
- [ ] Instalador funcional (usar `calamares` o el instalador de Debian).
- [x] Shell de escritorio propio (barra superior: lanzador, bandeja,
      reloj) — ver `docs/ARCHITECTURE.md`, sección "Shell de escritorio".
      **Probado con una sesión Cinnamon real** (Xvfb): funciona tal cual
      se diseñó, sin necesitar fixes como los de Legacy. Ver captura real
      en `docs/screenshots/antu-standard-desktop.png`.
- [x] Dock inferior (grouped-window-list: apps fijadas + abiertas en un
      panel aparte), también confirmado con la sesión real. Falta el
      indicador propio (el arco de luz del logo en vez de un puntito),
      que necesita un tema visual propio.
- [ ] Ícono del lanzador con el logo de Antü (hoy usa el genérico de
      Cinnamon — confirmado al probar con sesión real; cambiarlo requiere
      tocar la configuración específica de esa instancia del applet).
- [x] Lanzador con buscador (rofi + tema propio, Super+Espacio). **Es la
      única pieza del shell que se pudo probar visualmente de verdad**
      (con una pantalla virtual Xvfb) — ver captura en
      `docs/ARCHITECTURE.md`. Falta que el logo de la barra también lo
      abra (hoy abre el menú nativo de Cinnamon).
- [ ] Panel de ajustes rápidos (red, volumen, brillo) desde la barra.
- [ ] Tema visual propio (iconos, cursores, colores, GTK theme oscuro).
- [ ] Paquetería base: navegador, ofimática, reproductor multimedia,
      gestor de archivos.
- [ ] Probar en hardware real (no solo QEMU).

## Fase 2 — Antü Legacy

- [x] Configurar la edición en `i386` (`live-build` no soporta múltiples
      arquitecturas en una misma configuración; `i386` corre en hardware de
      32 y 64 bits, a diferencia de `amd64`).
- [x] Shell de escritorio propio en XFCE (barra superior única),
      **probado con una sesión XFCE real** (Xvfb + xfce4-session) — la
      única de las 3 ediciones validada así hasta ahora. Encontró y
      corrigió 2 bugs reales: el wallpaper no se aplicaba (el nombre del
      monitor varía por hardware, no se puede adivinar en un XML
      estático) y XFCE tiene 4 escritorios virtuales con wallpaper
      independiente cada uno. Solución: `usr/local/bin/antu-set-wallpaper`
      + autostart, que detecta los nombres reales en vez de adivinarlos.
      Ver `docs/ARCHITECTURE.md` y la captura real en
      `docs/screenshots/antu-legacy-desktop.png`.
- [ ] Reducir el set de paquetes y desactivar composición/efectos.
- [ ] Validar arranque y uso fluido en hardware con ≤2GB RAM.

## Fase 3 — Antü Pro

- [x] Shell de escritorio propio vía un paquete "Look and Feel" de Plasma
      (`org.antu.desktop`): barra superior (lanzador, bandeja, reloj) +
      dock inferior (icontasks). Es la pieza con más riesgo de las 3
      (formato de Plasma más complejo) y la que más necesita probarse en
      una sesión gráfica real antes de darla por buena.
- [ ] Efectos del dock (auto-hide, magnificación al pasar el mouse) y
      efectos visuales en general (blur, animaciones).
- [ ] Entorno KDE Plasma con efectos completos.
- [ ] Ajustes de kernel/scheduler para multinúcleo.
- [ ] Soporte de drivers propietarios de GPU (NVIDIA/AMD) opcional durante
      la instalación.
- [ ] Soporte Wayland.

## Fase 4 — Pulido y distribución

- [ ] Documentación de usuario final (instalación, primeros pasos).
- [ ] Sistema de actualizaciones propio o wrapper sobre APT.
- [ ] Publicar imágenes ISO de cada edición como releases del repositorio.
- [ ] Sitio/landing simple con capturas y descargas.

## Cómo contribuir a una fase

Cada tarea de este roadmap puede convertirse en un issue del repositorio.
Al tomar una tarea, actualizar el checkbox correspondiente en el PR que la
resuelve.
