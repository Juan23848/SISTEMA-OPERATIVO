# Guía de compilación

Antü OS se compila con [`live-build`](https://manpages.debian.org/testing/live-build/lb.1.en.html),
la herramienta oficial de Debian para construir imágenes live/instalables.

## Requisitos

- Una máquina o VM con **Debian estable (bookworm)** — no Ubuntu. Ver la
  advertencia de abajo sobre por qué esto ahora es un requisito, no solo
  una recomendación.
- Al menos 20GB de espacio libre y una conexión a internet estable (se
  descargan paquetes desde los repositorios oficiales).
- Privilegios de `root` (live-build necesita `chroot`, montajes, etc).

Instalar las herramientas necesarias:

```bash
sudo apt update
sudo apt install live-build qemu-system-x86 xorriso
```

### Advertencia importante: la versión de `live-build` cambia dónde busca los hooks

Dos revisiones externas independientes (Codex) encontraron que
`live-build` **no siempre lee los hooks del mismo lugar** — depende de
qué paquete/versión se instaló:

- El `live-build` de **Ubuntu** (probado en este proyecto: paquete
  `3.0~a57`) lee los hooks directo de `config/hooks/*.chroot`.
- El `live-build` **oficial de Debian bookworm** (`1:20230502`) y
  **trixie** (`1:20250505+deb13u1`) — confirmado bajando ambos tarballs
  fuente y leyendo el selector real, no solo la documentación — los
  busca en `config/hooks/normal/*.chroot` (más `config/hooks/live/` para
  hooks específicos de imagen live). Es la estructura que usa este
  repositorio.

**Por eso el requisito de arriba es compilar en Debian, no en Ubuntu**:
si se compila con el `live-build` de Ubuntu, nuestros hooks (idioma,
branding, Flathub, Samba, actualización de `dconf`) van a estar en el
lugar que Ubuntu no lee. Antes de confiar en un build real, confirmar la
versión instalada:

```bash
dpkg-query -W live-build
```

Debería empezar con `1:` (línea de versiones de Debian), no con `3.0~`
(línea de Ubuntu).

**Ya resuelto (y era más simple de lo que parecía)**: el mecanismo para
habilitar la arquitectura i386 antes de instalar paquetes (necesario
para Wine de 32 bits en Standard/Pro) no necesita ningún hook propio.
Leyendo el código fuente de esos mismos tarballs se confirmó que
`live-build` ya lo resuelve solo: cuando una entrada de un package-list
tiene el formato `paquete:arquitectura` (como `wine32:i386`, que
Standard/Pro ya tenían), lo detecta antes de instalar nada, habilita esa
arquitectura y actualiza `apt`. El hook `.chroot_early` que este
proyecto tuvo para esto (que ni siquiera existe como mecanismo en esas
versiones) se sacó. Queda un hook normal
(`hooks/normal/0070-verify-wine32.hook.chroot`) que confirma, después de
instalar los paquetes, que i386 y `wine32:i386` realmente quedaron
instalados — la presencia del paquete no garantiza que Wine vaya a
correr cualquier `.exe` de 32 bits sin problemas, pero al menos confirma
que el mecanismo de habilitación funcionó.

## Compilar una edición

Desde la raíz del repositorio:

```bash
./scripts/build.sh <edicion>
```

Donde `<edicion>` es una de: `antu-legacy`, `antu-standard`,
`antu-pro`.

Ejemplo:

```bash
./scripts/build.sh antu-standard
```

El script:

1. Copia el branding compartido (`shared/branding/`, wallpaper "noche" por
   defecto y el logo) a las rutas del sistema dentro de `includes.chroot/`
   de la edición (ver
   [`shared/scripts/install-branding.sh`](../shared/scripts/install-branding.sh)).
   Para usar el wallpaper "día" en vez del de "noche", corré ese script a
   mano con `day` como segundo parámetro antes de compilar (por ejemplo:
   `shared/scripts/install-branding.sh editions/antu-pro/config day`).
2. Copia `shared/resolver/antu-resolver` (la única fuente real del
   Resolver) a `includes.chroot/usr/bin/` de la edición. **Importante**:
   esta copia es automática desde acá — nunca editar directamente el
   `antu-resolver` dentro de `includes.chroot/`, porque `build.sh` lo
   pisa en cada build. Esto se agregó después de que una revisión
   externa encontrara que dos rondas de correcciones al Resolver nunca
   habían llegado a ninguna ISO real, por quedar copias manuales
   desactualizadas en cada edición.
3. Entra a `editions/<edicion>/` (la raíz de la edición, **no**
   `editions/<edicion>/config/`: `live-build` necesita correr desde el
   directorio que tiene a `auto/` y `config/` como hermanos — ver la
   sección de estructura más abajo para el porqué exacto).
4. Corre `lb clean` para asegurar un build limpio.
5. Corre `lb build`, que descarga paquetes y arma la imagen.
6. Deja la ISO resultante en `editions/<edicion>/build/`.

Un build completo puede tardar entre 30 minutos y varias horas, según la
conexión a internet y el hardware de la máquina que compila.

## Probar la ISO en una máquina virtual

```bash
./scripts/test-qemu.sh editions/antu-standard/build/*.iso
```

Esto levanta QEMU con RAM y CPU razonables para probar el arranque en modo
live sin necesidad de instalar en hardware real.

## Estructura de la configuración de `live-build`

Cada edición sigue la estructura estándar de un proyecto de `live-build`:
`auto/` y `config/` como **hermanos**, ambos hijos directos de la raíz de
la edición:

```
editions/<edicion>/
├── auto/                    # Scripts auto/config, auto/build, auto/clean (parámetros de lb config)
└── config/
    ├── package-lists/       # Listas .list.chroot con los paquetes a instalar
    ├── includes.chroot/     # Archivos que se copian tal cual dentro del sistema final
    └── hooks/
        └── normal/          # Hooks .chroot que corren DESPUÉS de instalar los paquetes
```

**Por qué importa el orden exacto**: `live-build` se invoca desde la raíz
de la edición (el directorio que contiene `auto/`), y sus scripts internos
(`lb_chroot_package-lists`, `lb_chroot_hooks`, `lb_chroot_includes`) leen
`config/package-lists/*.list.chroot`, `config/includes.chroot/` y
`config/hooks/normal/*.chroot` como rutas relativas a ese directorio — no
a `config/` mismo. Si `auto/` quedara *adentro* de `config/` (como pasó en
una versión anterior de este proyecto) y se corriera `lb build` desde ahí
adentro, `lb config` crearía un `config/config/` vacío al lado de nuestros
`package-lists/`, `hooks/` e `includes.chroot/` reales, y el build
terminaría instalando solo lo mínimo de Debian — sin Cinnamon/XFCE/Plasma,
sin Wine, sin el Resolver, sin branding — sin ningún error visible que lo
avise. Se confirmó este comportamiento corriendo `lb config` de verdad
contra ambas estructuras (la rota y la corregida) y comparando qué
directorios terminaba leyendo cada una.

**Por qué los hooks están en `hooks/normal/` y no directo en `hooks/`**:
ver la advertencia sobre versiones de `live-build` más arriba — es la
ubicación real que usa el `live-build` de Debian bookworm/trixie
(confirmado contra el código fuente oficial), a diferencia del de Ubuntu.

El branding (wallpapers, temas, iconos) se copia dentro de
`includes.chroot/` para terminar en las rutas correspondientes del sistema
de archivos final (por ejemplo `/usr/share/backgrounds/`).

`lb config` genera además, dentro de `config/`, varios directorios propios
(`archives/`, `binary*/`, `bootstrap/`, `chroot/`, etc.) y, en la raíz de
la edición, `.build/` y `local/` — todos ignorados en `.gitignore`, no son
contenido de Antü.

## Limpieza

Para borrar los artefactos de un build y empezar de cero:

```bash
cd editions/<edicion>
sudo lb clean --purge
```
