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

## Español como idioma por defecto

Antü busca despegarse de Linux/Windows también en el idioma: en vez de
dejar el sistema en inglés (lo habitual en la mayoría de las distros),
**español (Argentina) es el idioma por defecto** de las 3 ediciones,
configurado vía `hooks/0300-locale-es.hook.chroot` (genera y activa el
locale `es_AR.UTF-8` durante el build).

Esto traduce automáticamente casi todos los menús, categorías y textos
genéricos del sistema, porque tira de la traducción que la gran mayoría
de las aplicaciones de escritorio ya traen incluida — no hace falta
tocar cada aplicación a mano. Los nombres propios de las apps (Firefox,
LibreOffice, VLC) no se traducen, son marcas.

Se validó con una sesión XFCE real (`xfce4-appfinder`) que los nombres y
categorías de las aplicaciones efectivamente aparecen en español
("Accesibilidad", "Archivos", "Aplicaciones predeterminadas", etc.). La
cobertura de los textos propios de cada herramienta (botones, títulos de
ventana) depende de qué tan completa sea la traducción que traiga cada
paquete empaquetado — variará de programa a programa, y conviene
reconfirmarlo en Debian real (esto se probó en un entorno de desarrollo
basado en Ubuntu, que maneja los paquetes de idioma de forma distinta a
Debian).

## Íconos propios

Antü tiene su **propio tema de íconos** (`Antu`) en vez de reusar el
genérico de Linux, con el mismo lenguaje visual del logo: skeuomórfico,
en vidrio/metal azul con acentos cian y el "arco de luz" cruzando cada
pieza. Las fuentes originales (renders de alta resolución, 1254×1254,
con transparencia real) viven en `shared/branding/icons/png/`; a partir
de ahí se generó el tema instalable en
`shared/branding/icons/antu-icons/` siguiendo el estándar freedesktop
(hicolor), en 3 tamaños (256×256, 48×48 y 24×24 — se revisaron los tres
a mano para confirmar que se siguen leyendo bien en el tamaño chico de
panel/lista, no solo a full size):

| Ícono | Nombre freedesktop | Contexto |
|---|---|---|
| Papelera vacía | `user-trash` | Places |
| Papelera llena | `user-trash-full` | Places |
| Carpeta (genérica) | `folder` | Places |
| Carpeta (variante) | `folder-open` | Places |
| Descargas | `folder-download` | Places |
| Equipo | `computer` | Devices |
| Red | `network-workgroup` | Devices |
| Bienvenida a Antü | `start-here` | Applications |

La papelera usa el mecanismo nativo del estándar freedesktop
(`user-trash` / `user-trash-full`): el gestor de archivos elige sola cuál
mostrar según si la papelera tiene contenido, sin ninguna lógica
adicional de nuestra parte — es un cambio de nombre de archivo, no de
comportamiento. Las carpetas no tienen un estado "vacía/llena" nativo en
el estándar (a diferencia de la papelera); se usa `folder` como ícono
genérico por defecto (la variante con hojas asomando, que es la más
"Antü"), dejando `folder-open` disponible como alternativa.

El tema se instala en cada edición vía
`shared/scripts/install-branding.sh` (copia
`shared/branding/icons/antu-icons/` a
`includes.chroot/usr/share/icons/Antu/`) y se fija como tema por
defecto en la configuración de cada escritorio: `xsettings.xml`
(`Net/IconThemeName`) en XFCE/Legacy, `icon-theme` en
`org/cinnamon/desktop/interface` vía dconf en Cinnamon/Standard, y
`[Icons] Theme=Antu` en `kdeglobals` en Plasma/Pro.

Queda para una próxima sesión: cubrir el resto de los íconos de sistema
(configuración, terminal, etc.) con el mismo lenguaje visual — por ahora
esos quedan con la base genérica del tema heredado (`hicolor`) hasta ir
reemplazándolos de a poco.

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
abre el menú nativo de Cinnamon; el atajo de teclado sí es de Antü). El
buscador ya hereda el tema de íconos propio (`Antu`) para las carpetas
del sistema; los íconos por app individual dependen de que cada paquete
tenga su propio ícono en el tema activo, algo fuera del alcance de
`antu-icons`.

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

## Compatibilidad: veniendo de Windows

Objetivo explícito: alguien que usaba Windows tiene que poder migrar a
Antü sin sentir que perdió funcionalidad. Esto no es un tema visual —
son paquetes y configuración concreta, en las 3 ediciones
(`package-lists/compat.list.chroot` y `hardware.list.chroot`).

### Dos aclaraciones importantes (para no vender humo)

- **No existe una app de escritorio de Claude para Linux** (Anthropic
  solo publica binarios para Mac/Windows). El camino real y sin parches
  es usar **claude.ai desde el navegador** — misma cuenta, mismo
  historial, funciona perfecto. Se puede armar un acceso directo que lo
  abra "como app" (misma técnica que "Instalar como aplicación" de
  Chrome/Edge), pero eso es un acceso directo al sitio, no una app
  nativa instalada.
- **Microsoft Office tampoco existe para Linux.** El equivalente real es
  **LibreOffice** (ya instalado en Standard y Pro): abre y guarda
  `.docx`/`.xlsx`/`.pptx` de forma nativa. Para que un documento hecho en
  Word no se vea "corrido" al abrirlo acá, hace falta además que las
  fuentes que usó (Arial, Calibri, Times New Roman, Cambria) tengan un
  reemplazo con el mismo ancho de letra — ver más abajo.

### Pendrives y discos externos (montaje automático)

`udisks2` + `gvfs`/`gvfs-backends` + `policykit-1` son la base por la
que XFCE (Thunar), Cinnamon (Nemo) y Plasma (Dolphin) detectan un
dispositivo nuevo y lo montan solos, sin que el usuario configure nada.
A eso se le suma soporte de lectura/escritura para los 3 formatos que un
pendrive o disco externo puede traer si se usó antes en Windows:

- **NTFS** → `ntfs-3g` (controlador en espacio de usuario vía FUSE).
- **exFAT** (típico en pendrives y tarjetas SD modernas) → `exfatprogs`
  + el driver `exfat` del kernel de Linux (incluido de fábrica en el
  kernel que trae Debian).
- **FAT32** → `dosfstools` + el driver `vfat` del kernel.

**Validado de verdad, no solo instalado**: se armaron 3 imágenes de
disco de prueba (formateadas FAT32, exFAT y NTFS con las mismas
herramientas que se instalan acá) y se probó montarlas como si fueran un
pendrive recién enchufado. El montaje NTFS vía `ntfs-3g` (que no
depende de un módulo del kernel, corre entero en espacio de usuario) se
probó de punta a punta: montar, escribir un archivo, leerlo, desmontar —
funcionó igual que en un sistema real. El montaje de FAT32/exFAT no se
pudo completar en este entorno de desarrollo porque el kernel del
sandbox donde se corre este proyecto no trae compilados los módulos
`vfat`/`exfat` (es un contenedor recortado, no una instalación real de
Debian) — **no es una limitación de la configuración de Antü**: el
kernel que trae Debian de fábrica sí incluye esos módulos, y es el mismo
mecanismo (`mount -t vfat`/`mount -t exfat`) que ya se confirmó
funcionando para NTFS. Queda para validar en una máquina/VM real, igual
que Plasma (ver más abajo).

### Apps que no vienen empaquetadas para Debian

Para que "quiero instalar tal programa" no dependa de que ese programa
tenga paquete `.deb`, las 3 ediciones traen:

- **Flatpak**, con el repositorio de **Flathub** ya agregado de fábrica
  (`hooks/0400-flatpak-flathub.hook.chroot`) — miles de apps modernas se
  empaquetan ahí. Standard suma **GNOME Software** y Pro **Discover**
  (la tienda nativa de Plasma) con el backend de Flatpak, para instalar
  con una interfaz gráfica tipo "tienda de apps". Legacy se queda solo
  con la línea de comandos (`flatpak install ...`), para no cargar
  hardware de la era XP con una tienda gráfica pesada.
- **Soporte de AppImage** (`libfuse2`): un `.AppImage` descargado
  funciona con solo marcarlo ejecutable y hacerle doble clic, como un
  `.exe` portable en Windows — no necesita instalación.

### Ofimática: que un documento de Word no se vea roto

Además de LibreOffice, las 3 ediciones instalan fuentes **métricamente
compatibles** con las de Office: `fonts-liberation2` (sustituto de
Arial/Times New Roman/Courier New) y `fonts-crosextra-carlito`/
`fonts-crosextra-caladea` (sustitutos de Calibri/Cambria, las fuentes
por defecto de Word/Excel desde 2007). "Métricamente compatible" quiere
decir que cada letra ocupa el mismo ancho que la original: un documento
hecho en Word con esas fuentes mantiene los saltos de línea y de página
al abrirlo acá, aunque la tipografía use un dibujo distinto (no son
copias pixel a pixel de las fuentes de Microsoft, que son privativas).

### Hardware: wifi, bluetooth e impresoras

`hardware.list.chroot` (existía solo en Pro; ahora está en las 3, con
Legacy usando un set más liviano) agrega:

- Firmware no libre de los chipsets de wifi/bluetooth más comunes
  (`firmware-realtek`, `firmware-iwlwifi`, `firmware-atheros`,
  `firmware-brcm80211`) — la causa más común de "no me detecta el wifi"
  en una instalación de Linux nueva.
- `bluez` + `blueman` para emparejar mouse/teclado/auriculares
  inalámbricos desde una interfaz gráfica.
- `cups` + drivers de impresora (`printer-driver-all` en Standard/Pro;
  un set más chico de Gutenprint/HP en Legacy) + `avahi-daemon`, que
  detecta impresoras de red/AirPrint solas, sin cargar una IP a mano.

No se pudo probar contra hardware real (wifi/bluetooth/impresora físicos
no existen en este entorno de desarrollo) — igual que Plasma, queda
pendiente de validar en una máquina real.

## Flujo de build

```
editions/<edicion>/config/   →  lb config (auto-generado por live-build)
                              →  lb build
                              →  editions/<edicion>/build/*.iso
```

Ver [`BUILD.md`](BUILD.md) para el detalle paso a paso.
