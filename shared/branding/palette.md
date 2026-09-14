# Paleta e identidad visual de Antü OS

**Antü** ("sol" en mapudungún) es la luz que atraviesa la oscuridad. La
identidad visual toma esa idea de forma literal: fondos azules muy
profundos, casi negros, atravesados por líneas de luz curvas — el brillo
abriéndose paso en la oscuridad — en vez de un imaginario "solar" cálido.

## Colores

| Uso | Nombre | Hex |
|---|---|---|
| Fondo profundo | Antü Void | `#04070D` |
| Fondo base | Antü Navy | `#0A1730` |
| Primario (glow) | Antü Blue | `#1E6FEB` |
| Brillo / acento | Antü Cyan | `#5AD8FF` |
| Brillo intenso | Antü Glow | `#BFEFFF` |
| Texto sobre oscuro | White | `#F2F9FF` |

El degradé de marca va de **Antü Navy** (oscuridad) hacia **Antü Cyan/Glow**
(luz), siempre como si la luz emergiera desde un punto y se abriera paso
entre curvas oscuras. Se usa en el logo, el wallpaper y las pantallas de
arranque (splash/GRUB).

## Variación por edición

- **Antü Legacy**: mismo concepto pero con glow reducido y sin blur (menos
  costoso de renderizar en hardware viejo): líneas de luz más simples, casi
  planas.
- **Antü Standard**: el balance que está definido acá (glow moderado).
- **Antü Pro**: glow más intenso y capas adicionales de profundidad,
  aprovechando que el hardware soporta composición avanzada.

## Tipografía

- Interfaz: la fuente por defecto de cada entorno de escritorio. Recomendado:
  **Inter** o **Noto Sans** si se quiere unificar look entre ediciones.
- Wordmark/logo: geométrica, con **letter-spacing amplio** en mayúsculas
  ("A N T Ü"), como una señal de luz — no un logotipo compacto.

## Archivos de esta carpeta

- `logo.svg` — ícono cuadrado: arco de luz en forma de "A" con línea de
  horizonte brillante debajo (pixmaps, launcher, favicon del proyecto).
- `wordmark.svg` — logo horizontal con el ícono + "ANTÜ", para
  documentación, splash screens e instalador.
- `wallpaper.svg` — fondo de escritorio 1920x1080 con líneas de luz curvas
  sobre fondo azul profundo, basado en la referencia visual del proyecto.

Estos son los assets **fuente** (editables, en SVG). `scripts/build.sh` los
copia automáticamente a las rutas del sistema dentro de cada edición al
compilar.
