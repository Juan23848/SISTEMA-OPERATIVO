# Roadmap

## Estado actual

Proyecto recién iniciado. Existe el scaffold de las 3 ediciones (estructura
de configuración de `live-build`, listas de paquetes iniciales, branding
placeholder) pero **todavía no se compiló ninguna ISO**.

## Fase 0 — Scaffold (actual)

- [x] Definir arquitectura y las 3 ediciones.
- [x] Estructura de carpetas y documentación base.
- [x] Configuración inicial de `live-build` por edición (package-lists
      base, hooks vacíos, branding placeholder).
- [x] Scripts `build.sh` y `test-qemu.sh`.
- [ ] Primera compilación exitosa de una ISO (Standard) en un entorno con
      `live-build`.

## Fase 1 — Antü Standard (MVP)

Se prioriza esta edición porque cubre el público más amplio (uso
doméstico/oficina).

- [ ] Compilar ISO booteable en modo live (sin instalar).
- [ ] Instalador funcional (usar `calamares` o el instalador de Debian).
- [ ] Entorno de escritorio con menú inicio, barra de tareas y bandeja del
      sistema con layout tipo Windows.
- [ ] Tema visual propio (iconos, cursores, colores).
- [ ] Paquetería base: navegador, ofimática, reproductor multimedia,
      gestor de archivos.
- [ ] Probar en hardware real (no solo QEMU).

## Fase 2 — Antü Legacy

- [ ] Adaptar la configuración a `i386` además de `amd64`.
- [ ] Reducir el set de paquetes y desactivar composición/efectos.
- [ ] Validar arranque y uso fluido en hardware con ≤2GB RAM.

## Fase 3 — Antü Pro

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
