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
2. Entra a `editions/<edicion>/config/`.
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

Cada edición sigue la estructura estándar que genera `lb config`:

```
editions/<edicion>/config/
├── auto/               # Scripts auto/config y auto/build (parámetros de lb config)
├── package-lists/      # Listas .list.chroot con los paquetes a instalar
├── includes.chroot/    # Archivos que se copian tal cual dentro del sistema final
└── hooks/              # Scripts que corren durante el build (chroot y binary hooks)
```

El branding (wallpapers, temas, iconos) se copia dentro de
`includes.chroot/` para terminar en las rutas correspondientes del sistema
de archivos final (por ejemplo `/usr/share/backgrounds/`).

## Limpieza

Para borrar los artefactos de un build y empezar de cero:

```bash
cd editions/<edicion>/config
sudo lb clean --purge
```
