# Guía de compilación

Antü OS se compila con [`live-build`](https://manpages.debian.org/testing/live-build/lb.1.en.html),
la herramienta oficial de Debian para construir imágenes live/instalables.

## Requisitos

- Una máquina o VM con **Debian o Ubuntu** (recomendado: Debian estable).
- Al menos 20GB de espacio libre y una conexión a internet estable (se
  descargan paquetes desde los repositorios oficiales).
- Privilegios de `root` (live-build necesita `chroot`, montajes, etc).

Instalar las herramientas necesarias:

```bash
sudo apt update
sudo apt install live-build qemu-system-x86 xorriso
```

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
2. Entra a `editions/<edicion>/` (la raíz de la edición, **no**
   `editions/<edicion>/config/`: `live-build` necesita correr desde el
   directorio que tiene a `auto/` y `config/` como hermanos — ver la
   sección de estructura más abajo para el porqué exacto).
3. Corre `lb clean` para asegurar un build limpio.
4. Corre `lb build`, que descarga paquetes y arma la imagen.
5. Deja la ISO resultante en `editions/<edicion>/build/`.

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
    └── hooks/                # Scripts que corren durante el build (chroot y binary hooks)
```

**Por qué importa el orden exacto**: `live-build` se invoca desde la raíz
de la edición (el directorio que contiene `auto/`), y sus scripts internos
(`lb_chroot_package-lists`, `lb_chroot_hooks`, `lb_chroot_includes`) leen
`config/package-lists/*.list.chroot`, `config/hooks/*.chroot` y
`config/includes.chroot/` como rutas relativas a ese directorio — no a
`config/` mismo. Si `auto/` quedara *adentro* de `config/` (como pasó en
una versión anterior de este proyecto) y se corriera `lb build` desde ahí
adentro, `lb config` crearía un `config/config/` vacío al lado de nuestros
`package-lists/`, `hooks/` e `includes.chroot/` reales, y el build
terminaría instalando solo lo mínimo de Debian — sin Cinnamon/XFCE/Plasma,
sin Wine, sin el Resolver, sin branding — sin ningún error visible que lo
avise. Se confirmó este comportamiento corriendo `lb config` de verdad
contra ambas estructuras (la rota y la corregida) y comparando qué
directorios terminaba leyendo cada una.

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
