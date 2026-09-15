# Roadmap

## Estado actual

Existe el scaffold de las 3 ediciones (estructura de configuración de
`live-build`, listas de paquetes iniciales, branding real) y la
configuración de `live-build` de las 3 **ya fue probada y corre sin
errores** hasta el punto de descargar paquetes de Debian. Las 3 ediciones
también tienen ya un **shell de escritorio propio** (barra superior única
con la identidad de Antü, ver `docs/ARCHITECTURE.md`). **Todavía no se
compiló ninguna ISO completa**, porque eso requiere una máquina con acceso
a internet a los mirrors de Debian (no disponible en el entorno donde se
desarrolló este proyecto) — por lo tanto tampoco se pudo ver el shell de
escritorio funcionando en una sesión gráfica real todavía.

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
- [x] Shell de escritorio propio (barra superior única: lanzador, tareas,
      bandeja, reloj) — ver `docs/ARCHITECTURE.md`, sección "Shell de
      escritorio". Configurado vía `dconf`, validado con `dconf update`
      pero sin probar en una sesión gráfica real.
- [ ] Dock inferior (apps fijadas + abiertas) con indicador propio (el
      arco de luz del logo en vez de un puntito).
- [ ] Lanzador de apps a pantalla completa con buscador.
- [ ] Panel de ajustes rápidos (red, volumen, brillo) desde la barra.
- [ ] Tema visual propio (iconos, cursores, colores, GTK theme oscuro).
- [ ] Paquetería base: navegador, ofimática, reproductor multimedia,
      gestor de archivos.
- [ ] Probar en hardware real (no solo QEMU).

## Fase 2 — Antü Legacy

- [x] Configurar la edición en `i386` (`live-build` no soporta múltiples
      arquitecturas en una misma configuración; `i386` corre en hardware de
      32 y 64 bits, a diferencia de `amd64`).
- [x] Shell de escritorio propio en XFCE (barra superior única), validado
      con `xmllint` (XML bien formado, sin probar en sesión gráfica real).
- [ ] Reducir el set de paquetes y desactivar composición/efectos.
- [ ] Validar arranque y uso fluido en hardware con ≤2GB RAM.

## Fase 3 — Antü Pro

- [x] Shell de escritorio propio vía un paquete "Look and Feel" de Plasma
      (`org.antu.desktop`). Es la pieza con más riesgo de las 3 (formato
      de Plasma más complejo) y la que más necesita probarse en una
      sesión gráfica real antes de darla por buena.
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
