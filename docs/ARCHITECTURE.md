# Arquitectura de Antü OS

## Idea general

Antü OS **no** es un kernel ni un sistema operativo escrito desde cero.
Es una **distribución Linux personalizada** (un "respin" de Debian/Ubuntu)
que:

1. Usa el **kernel Linux** y la base de Debian/Ubuntu tal cual, para heredar
   soporte de hardware, drivers, seguridad y actualizaciones.
2. Reemplaza la capa de **escritorio y experiencia de usuario** por un
   diseño propio: familiar y fácil de usar para cualquiera que venga de
   Windows o mac, pero sin copiar a ninguno de los dos (ver sección
   "Shell de escritorio" más abajo).
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
| Escritorio | XFCE (Legacy) / Cinnamon (Standard) / KDE Plasma (Pro) | Elegidos por consumo de recursos vs. features. |
| Shell / identidad | Barra superior única propia de Antü, wallpaper, logo | Configurada por edición en `editions/*/config/includes.chroot/`, assets en `shared/branding/`. Ver sección "Shell de escritorio". |
| Build system | `live-build` | Config declarativa en `editions/*/config/`. |

## Las tres ediciones

### Antü Legacy (`editions/antu-legacy`)

- Público: PCs con hardware equivalente a la era de Windows XP (Pentium 4 /
  Core 2 Duo, 512MB–2GB RAM, sin aceleración 3D confiable).
- Escritorio: **XFCE**, con compositor desactivado por defecto. Shell:
  barra superior única (ver "Shell de escritorio"), sin dock ni animaciones.
- Arquitectura: `i386` (32 bits). `live-build` solo permite una arquitectura
  por configuración, y `i386` corre tanto en hardware de 32 como de 64 bits,
  a diferencia de `amd64` (que no arranca en máquinas puramente de 32 bits) —
  por eso es la opción que da máxima compatibilidad con hardware viejo.
- Prioridad: arrancar rápido y consumir poca RAM, no efectos visuales.

### Antü Standard (`editions/antu-standard`)

- Público: uso doméstico/oficina, hardware equivalente a Windows 7 en
  adelante (Core i3+, 4GB+ RAM).
- Escritorio: **Cinnamon**. Shell: barra superior única (ver "Shell de
  escritorio"); el dock separado y más applets quedan para una siguiente
  etapa (ver `docs/ROADMAP.md`).
- Arquitectura: `amd64`.
- Prioridad: balance entre estética moderna y bajo consumo de recursos.

### Antü Pro (`editions/antu-pro`)

- Público: hardware potente (multinúcleo, GPU dedicada, SSD, 16GB+ RAM).
- Escritorio: **KDE Plasma**, con todos los efectos de composición
  habilitados, soporte Wayland, y ajustes de kernel/scheduler orientados a
  aprovechar múltiples núcleos y GPU.
- Arquitectura: `amd64` (con perfiles opcionales para `arm64` a futuro).
- Prioridad: máximo aprovechamiento del hardware disponible, sin resignar
  robustez.

## Shell de escritorio

Antü no copia ni a Windows ni a mac: toma la idea de una **barra global
única** (como mac, en vez de la barra de tareas de Windows) porque es un
patrón de interacción probado y fácil de aprender, pero la usa a su manera
y con la identidad visual propia (el arco de luz del logo, la paleta azul
profunda).

**Base común a las 3 ediciones** (implementada):

- Una barra fija arriba de la pantalla, con:
  - Lanzador de aplicaciones a la izquierda, con el logo de Antü.
  - Bandeja del sistema y reloj a la derecha.
- Un **dock** fijo abajo (Standard y Pro; Legacy no lo tiene, ver más
  abajo) con las apps fijadas y abiertas — ahí vive el cambio de ventana,
  no en la barra de arriba.
- Wallpaper de Antü como fondo por defecto.

En **Legacy** no hay dock separado (para no gastar recursos en un panel
extra): la lista de ventanas abiertas queda directamente en la barra de
arriba, como única barra.

Esto está configurado de fábrica en cada edición usando el mecanismo nativo
de cada entorno de escritorio (no es un tema visual superficial, son los
archivos de configuración reales que lee cada DE al iniciar sesión):

| Edición | Mecanismo | Archivos |
|---|---|---|
| Legacy (XFCE) | `xfconf` vía `/etc/skel` | `editions/antu-legacy/config/includes.chroot/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/` |
| Standard (Cinnamon) | Defaults de `dconf` | `editions/antu-standard/config/includes.chroot/etc/dconf/db/local.d/00-antu-desktop` |
| Pro (KDE Plasma) | Paquete "Look and Feel" propio (`org.antu.desktop`) | `editions/antu-pro/config/includes.chroot/usr/share/plasma/look-and-feel/org.antu.desktop/` |

### Legacy: probado con una sesión XFCE real, no solo a mano

A diferencia del resto (validado solo por sintaxis), **Antü Legacy se
probó levantando una sesión XFCE real** (`xfce4-session`, con `xfwm4` +
`xfdesktop` + `xfce4-panel`) contra una pantalla virtual (`Xvfb`). Esto
encontró y corrigió dos bugs reales que ningún chequeo de sintaxis iba a
detectar:

1. **El wallpaper no se aplicaba.** `xfce4-desktop` nombra la propiedad
   del fondo según el monitor que detecta en cada máquina (`monitor0`,
   `monitorVGA-1`, `monitorHDMI-1`... varía según el hardware/driver de
   video). El XML estático que se había escrito a mano adivinaba un
   nombre que no coincidía con el real, así que el wallpaper de Antü
   nunca se veía — quedaba el de Debian/Xubuntu por defecto.
2. **XFCE tiene 4 escritorios virtuales**, cada uno con wallpaper propio.
   Aplicar el cambio solo al primero no alcanzaba: al abrir sesión en
   otro escritorio, volvía a aparecer el fondo por defecto.

La solución: en vez de adivinar nombres en un XML estático, un script
(`usr/local/bin/antu-set-wallpaper`, disparado por un autostart en
`etc/xdg/autostart/antu-wallpaper.desktop`) le pregunta a `xfconf` qué
monitores y escritorios existen de verdad al iniciar sesión, y aplica el
wallpaper de Antü a todas las combinaciones — y fuerza el redibujado con
`xfdesktop --reload`, porque tampoco se actualiza solo.

Con este fix, una sesión completamente nueva (sin ningún ajuste manual)
ya muestra el wallpaper y el logo de Antü correctamente:

![Escritorio de Antü Legacy](screenshots/antu-legacy-desktop.png)

### Standard: también probado con una sesión Cinnamon real

Le fue igual de bien que a Legacy. Se levantó `cinnamon` de verdad (no
`cinnamon-session` completo, que en este entorno de desarrollo específico
no llegaba a arrancar el shell por limitaciones del propio contenedor —
ver nota abajo) contra `Xvfb`, con nuestros defaults de `dconf` ya
aplicados. Resultado: **el mecanismo central funciona tal cual se
diseñó**, sin necesitar ningún fix como el de Legacy (Cinnamon guarda el
wallpaper en una clave de `gsettings` simple, sin nombres de monitor que
adivinar):

![Escritorio de Antü Standard](screenshots/antu-standard-desktop.png)

Se ve la barra superior (menú a la izquierda, reloj a la derecha) y el
dock abajo (`grouped-window-list`), ambos cargando los applets que
configuramos, con el wallpaper y el logo de Antü de fondo. Quedó
confirmado también un pendiente que ya estaba anotado: el ícono del
lanzador sigue siendo el genérico de Cinnamon, no el logo de Antü —
cambiarlo requiere tocar una configuración específica de esa instancia
del applet, más delicada que una propiedad global, y se dejó pendiente a
propósito (ver `docs/ROADMAP.md`).

*Nota sobre cómo se probó:* en este entorno de desarrollo puntual, correr
`cinnamon-session` completo (el gestor de sesión real) no llegaba a
mostrar el shell — dos causas, ninguna relacionada con la configuración
de Antü: el `python3` por defecto de este contenedor en particular no
coincidía con la versión para la que estaban compiladas las bindings de
`gi` (un contenedor de desarrollo normal, o la máquina de un usuario
final, no tiene este conflicto), y Cinnamon necesitaba variables de
entorno de sesión (`XDG_SESSION_TYPE`) que `cinnamon-session` no llegaba
a exportar antes de fallar. Arrancar `cinnamon` directamente, ya con esas
dos cosas resueltas a mano, funcionó de punta a punta.

### Pro: todavía sin sesión real

La pieza de Plasma sigue el formato y la API de scripting documentados de
KDE, pero **no se pudo probar en una sesión gráfica real** — KWin (el
compositor de Plasma) tiene requisitos más pesados que XFCE y Cinnamon, y
no se llegó a levantar en el tiempo disponible. Queda pendiente la misma
validación que ya le hizo bien a Legacy y Standard (ver
`docs/ROADMAP.md`).

### Lanzador de Antü (Standard)

En vez de un menú de carpetas, Antü Standard abre con **Super+Espacio** un
buscador de aplicaciones (`rofi`, con un tema propio en
`shared/branding/` → `editions/antu-standard/config/includes.chroot/usr/share/rofi/themes/antu.rasi`):
escribís y filtra al toque, sin scrollear menús.

A diferencia del resto del shell, esta pieza **sí se pudo probar
visualmente de verdad**: se armó una pantalla virtual (`Xvfb`) en el
entorno de desarrollo, se abrió el lanzador contra esa pantalla y se sacó
una captura real en cada iteración. Eso hizo aparecer varios bugs reales,
ya corregidos:

- El nombre técnico del modo ("drun") se colaba pegado al texto de
  búsqueda.
- Sin especificar una fuente, el tema usaba la tipografía monoespaciada
  por defecto de rofi (daba un aire a terminal/DOS de los 90) — ahora usa
  **Inter** (`fonts-inter`, agregado a `package-lists`).
- La primera versión se veía plana/rudimentaria. Se le agregó
  profundidad real: un degradé de fondo (más claro arriba, más oscuro
  abajo) y el ítem seleccionado con su propio degradé tipo "botón con
  relieve" — una referencia directa a cómo Windows viene resolviendo esto
  desde siempre, para que se sienta familiar.
- Al armar el degradé aparecieron 2 límites reales de esta versión de
  rofi (1.7.5), no evidentes sin probar: `linear-gradient()` no acepta
  variables `@nombre` como color (hay que poner el hex literal), y
  `border-color` no admite un color distinto por lado (no se pudo hacer
  el bisel de dos tonos que se había probado primero). También un
  separador visual se infló y ocupó toda la ventana por faltarle
  `expand: false` — quedó como una línea fina de 1px.
- El texto del ítem seleccionado (celeste claro) quedaba en blanco y no
  se leía — el color de texto que se le pone a `element` no lo hereda el
  sub-widget `element-text`, que es el que en realidad dibuja el texto
  (y el fragmento resaltado por la búsqueda). Hubo que fijarlo ahí
  también, explícitamente.

![Lanzador de Antü](screenshots/antu-launcher.png)

*(El fondo negro liso de la captura es una limitación del banco de
pruebas — una pantalla X vacía sin el escritorio corriendo detrás — no
del diseño: en el sistema real se ve el wallpaper de Antü, que se
configura por otro lado y ya está validado — ver la sección de Cinnamon
más arriba.)*

Todavía falta: que el logo de la barra superior abra este lanzador (hoy
abre el menú nativo de Cinnamon; el atajo de teclado sí es de Antü), e
íconos por app en el buscador (dependen del tema de íconos, que también es
un pendiente).

**Lo que falta, y que se piensa agregar de forma incremental por edición**
(de más simple a más compleja, ver `docs/ROADMAP.md`):

- El indicador de "app abierta" en el dock usando el arco de luz del logo
  en vez del puntito genérico de cada DE — requiere un tema visual propio
  (CSS/Qt), todavía no existe.
- Que el logo de la barra abra el lanzador de Antü (por ahora solo el
  atajo de teclado lo hace).
- El lanzador con buscador en Legacy y Pro (por ahora solo en Standard).
- Un panel de **ajustes rápidos** (red, volumen, brillo) desplegable desde
  la derecha de la barra.
- Efectos visuales (blur, animaciones) en las ediciones con más recursos
  (Pro primero, después Standard). Legacy se mantiene siempre simple.

## Flujo de build

```
editions/<edicion>/config/   →  lb config (auto-generado por live-build)
                              →  lb build
                              →  editions/<edicion>/build/*.iso
```

Ver [`BUILD.md`](BUILD.md) para el detalle paso a paso.
