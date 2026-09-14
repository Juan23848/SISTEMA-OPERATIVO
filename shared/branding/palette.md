# Paleta e identidad visual de WinLux OS

Identidad visual base, común a las 3 ediciones. Cada edición puede aplicar
variaciones de tono (ver abajo) manteniendo estos colores y esta tipografía
como base.

## Colores

| Uso | Nombre | Hex |
|---|---|---|
| Primario | WinLux Blue | `#1565C0` |
| Secundario / acento | WinLux Teal | `#26C6DA` |
| Superficie oscura | Slate | `#1B2733` |
| Superficie clara | Cloud | `#F4F7FA` |
| Texto sobre oscuro | White | `#FFFFFF` |
| Texto sobre claro | Ink | `#1B2733` |

El degradé principal de marca va de **WinLux Blue** a **WinLux Teal**,
en diagonal (135°). Se usa en el logo, el wallpaper y las pantallas de
arranque (splash/GRUB).

## Variación por edición

- **WinLux Legacy**: mismos colores, pero sin degradé ni transparencias
  (colores planos), para que se vea bien incluso sin aceleración gráfica.
- **WinLux Standard**: degradé suave, como está definido acá.
- **WinLux Pro**: degradé + un sutil efecto de brillo/blur, aprovechando
  que el hardware soporta composición avanzada.

## Tipografía

- Interfaz: la fuente por defecto de cada entorno de escritorio (evita
  problemas de licencias y de renderizado). Recomendado: **Inter** o
  **Noto Sans** si se quiere unificar look entre ediciones.
- Wordmark/logo: geométrica, peso bold, todo en un solo peso para que se
  vea consistente en tamaños chicos (íconos) y grandes (wallpaper).

## Archivos de esta carpeta

- `logo.svg` — ícono cuadrado (para pixmaps, launcher, favicon del proyecto).
- `wordmark.svg` — logo horizontal con texto "WinLux OS", para documentación,
  splash screens y el instalador.
- `wallpaper.svg` — fondo de escritorio 1920x1080 con la identidad de marca.

Estos son los assets **fuente** (editables). `scripts/build.sh` los copia
automáticamente a las rutas del sistema dentro de cada edición al compilar,
así que no hace falta duplicarlos a mano en cada `editions/*/config/`.
