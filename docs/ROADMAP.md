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
Las 3 ediciones también tienen **español (Argentina) como idioma por
defecto** y un **set de íconos propios** (tema `Antu`) instalado como
tema de sistema real — ver Fase 0.5. Además ya tienen la **capa de
compatibilidad para migrar desde Windows**: montaje automático de
pendrives/discos externos (NTFS/exFAT/FAT32), Flatpak+Flathub, soporte
de AppImage, LibreOffice con fuentes compatibles con Office, y
wifi/bluetooth/impresoras — ver Fase 0.6. Y ya arrancó la **fusión
funcional** (no solo visual) entre Windows y Linux: Wine integrado para
correr `.exe`/`.msi` con doble clic, validado con el motor corriendo de
verdad contra una pantalla virtual — ver Fase 0.7.

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

## Fase 0.5 — Identidad propia (despegarse de Linux/Windows)

Criterio del proyecto: que Antü se sienta propio, no "Linux con logo
pegado". Aplica a las 3 ediciones por igual.

- [x] **Español (Argentina) como idioma por defecto** de las 3 ediciones
      (`hooks/0300-locale-es.hook.chroot`, genera y activa
      `es_AR.UTF-8`). Validado con una sesión XFCE real: los nombres y
      categorías de las aplicaciones se traducen correctamente. La
      cobertura de los textos propios de cada herramienta (botones,
      títulos de ventana) depende de la traducción que traiga cada
      paquete — confirmar en Debian real (se probó en un entorno de
      desarrollo basado en Ubuntu). Ver `docs/ARCHITECTURE.md`.
- [x] **Set de íconos propios** (tema `Antu`, skeuomórfico, lenguaje
      visual de Antü: vidrio/metal azul + arco de luz cian), instalado
      como tema freedesktop real (`shared/branding/icons/antu-icons/`,
      3 tamaños: 256/48/24px) y fijado por defecto en las 3 ediciones.
      Cubre: papelera vacía/llena (con swap automático nativo del
      estándar `user-trash`/`user-trash-full`), carpeta genérica,
      carpeta Descargas, Equipo, Red y la insignia "Bienvenida a Antü".
      Ver `docs/ARCHITECTURE.md`, sección "Íconos propios". Pendiente
      para más adelante: el resto de los íconos de sistema
      (configuración, terminal, etc.), que por ahora usan la base
      genérica heredada (`hicolor`).

## Fase 0.6 — Compatibilidad veniendo de Windows

Criterio del proyecto: alguien que usaba Windows migra sin sentir que
perdió funcionalidad. Aplica a las 3 ediciones (`compat.list.chroot` y
`hardware.list.chroot` nuevos, ver `docs/ARCHITECTURE.md` sección
"Compatibilidad: veniendo de Windows").

- [x] **Pendrives/discos externos**: montaje automático (`udisks2` +
      `gvfs` + `policykit-1`) con lectura/escritura NTFS (`ntfs-3g`),
      exFAT (`exfatprogs`) y FAT32 (`dosfstools`). Validado con
      imágenes de disco de prueba: el ciclo completo montar → escribir →
      leer → desmontar se confirmó de punta a punta para NTFS. FAT32 y
      exFAT no se pudieron probar en este entorno de desarrollo porque
      su kernel recortado no trae los módulos `vfat`/`exfat` (el kernel
      real de Debian sí los trae) — validar en una máquina/VM real.
- [x] **Apps fuera de los repos de Debian**: Flatpak + repositorio de
      Flathub agregado de fábrica, con tienda gráfica (GNOME Software en
      Standard, Discover en Pro) y soporte de AppImage (`libfuse2`) en
      las 3.
- [x] **Ofimática**: LibreOffice (ya estaba en Standard/Pro) + fuentes
      métricamente compatibles con Arial/Calibri/Cambria/Times New Roman
      (`fonts-liberation2`, `fonts-crosextra-carlito`,
      `fonts-crosextra-caladea`), para que un `.docx` de Word no se vea
      corrido al abrirlo.
- [x] **Wifi/bluetooth/impresoras**: firmware no libre de los chipsets
      más comunes, `bluez`+`blueman`, y `cups` con drivers + `avahi` para
      detectar impresoras de red solas. No se pudo probar contra
      hardware real (no hay wifi/bluetooth/impresora físicos en este
      entorno) — pendiente de validar en una máquina real.
- [ ] **Claude y Microsoft Office no tienen versión nativa para Linux**
      (aclarado en `docs/ARCHITECTURE.md`): el camino real es claude.ai
      desde el navegador y LibreOffice respectivamente. Queda pendiente,
      si se quiere, armar un acceso directo de escritorio que abra
      claude.ai "como app".
## Fase 0.7 — Fusión funcional (WinLux de verdad)

Criterio del proyecto, dicho por Juan desde el arranque: Antü no es
"Linux con logo de Antü" — es una fusión real de Windows y Linux, no
solo visual. Esta fase es donde eso se hace ingeniería concreta, sin
apuro (plazo: el año que viene).

- [x] **Wine**: correr `.exe`/`.msi` de Windows directo, con doble
      clic, integrado al sistema (no como "opción avanzada" en una
      terminal). Multiarch i386 en Standard/Pro (necesario para el
      software de 32 bits, la mayoría del software viejo) vía
      `hooks/0050-multiarch-i386.chroot_early` — tiene que correr antes
      de instalar paquetes, no después. Asociación de tipo de archivo
      (`.exe`→`wine`, `.msi`→`wine msiexec /i`) validada de verdad:
      un archivo con el encabezado real de un ejecutable de Windows se
      reconoce solo y el sistema resuelve que se abre con Wine, sin
      configurar nada (`xdg-mime query default` lo confirma). También
      se probó el motor completo: Wine corriendo una app de Windows con
      ventana real contra una pantalla virtual, más el puente de
      archivos Windows↔Linux funcionando (escribir desde el lado
      Windows, leer desde el lado Linux). Ver `docs/ARCHITECTURE.md`,
      sección "Fusión funcional: correr programas de Windows (Wine)".
- [ ] **Bottles**: interfaz gráfica sobre Wine (un "prefijo" aislado por
      app, instalador visual) — mucho más amigable que Wine pelado.
      Se instala como Flatpak desde la tienda de apps que ya está
      configurada (Fase 0.6); no se bakea en la ISO porque necesitaría
      internet real a Flathub durante el build, algo no probado en este
      entorno.
- [ ] **Red mixta con PCs Windows (Samba)**: ver el ícono "Red" (Fase
      0.5) poblado con las PCs Windows de la misma red, copiar archivos
      para los dos lados sin configurar nada. `samba` + `cifs-utils` +
      `winbind`. No arrancado todavía.
- [ ] **Gaming (Proton/Steam)**: que la biblioteca de Steam con juegos
      de Windows funcione, pensado sobre todo para Antü Pro (hardware
      potente). No arrancado todavía.
- [ ] **.NET nativo** (`dotnet-runtime`, sin pasar por Wine) para
      software moderno hecho en .NET Core/5+, que corre nativo en
      Linux sin necesitar ningún traductor. No arrancado todavía.
- [ ] **Antü Store propia**: una única app (no la Store genérica de
      cada DE) que unifique apt + Flatpak + AppImage + instaladores de
      Wine en una sola interfaz — "instalar" sin que el usuario sepa ni
      le importe qué mecanismo hay detrás. Es la pieza más ambiciosa de
      toda la fusión (desarrollo de una aplicación propia, no solo
      configuración) — dejarla para cuando el resto de esta fase esté
      maduro. No arrancado todavía.

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
- [ ] Tema visual propio (cursores, colores, GTK theme oscuro — los
      íconos ya están, ver Fase 0.5).
- [x] Paquetería base: navegador (Firefox), ofimática (LibreOffice +
      fuentes compatibles con Office), reproductor multimedia (VLC),
      gestor de archivos (Nemo, viene con Cinnamon). Ver Fase 0.6.
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
