# Identidad visual de Antü OS

**Antü** ("sol" en mapudungún) es la luz que atraviesa la oscuridad. Logo y
wallpaper diseñados por Juan y Sofi (asistente de IA del proyecto).

## Archivos de esta carpeta

- **`logo.png`** — logo oficial (1254×1254, fondo transparente): el ícono
  "A" tipo arco de luz + el wordmark "ANTÜ" debajo. Es el archivo fuente,
  úsalo tal cual (no recrear a mano).
- **`wallpaper-night.png`** (1672×941) — fondo de escritorio "noche": azul
  muy profundo con haces de luz celestes. Es el wallpaper **por defecto**
  en las 3 ediciones.
- **`wallpaper-day.png`** (1672×941) — fondo de escritorio "día": versión
  más clara, con un brillo dorado/blanco arriba a la derecha (más literal
  con lo de "sol"). Disponible como alternativa (ver
  [`docs/BUILD.md`](../../docs/BUILD.md) para cómo usarlo en vez del de
  noche).

`scripts/build.sh` copia estos archivos automáticamente a las rutas del
sistema dentro de cada edición al compilar (vía
[`shared/scripts/install-branding.sh`](../scripts/install-branding.sh)).

## Colores de referencia

Sampleados directamente de los archivos originales, para quien necesite
recrear algún elemento de UI a juego (temas, splash screens, etc.):

| Uso | Nombre | Hex | De dónde sale |
|---|---|---|---|
| Fondo profundo (noche) | Antü Void | `#00010F` | Esquina más oscura de `wallpaper-night.png` |
| Fondo base (noche) | Antü Navy | `#011954` | Fondo general de `wallpaper-night.png` |
| Brillo / línea de luz | Antü Cyan | `#1EAEFC` | Línea de horizonte del logo / haces de luz |
| Brillo intenso | Antü Glow | `#CCF5FC` | Punto más brillante del pico del logo |
| Azul del logo (bordes) | Antü Blue | `#006CE2` | Borde exterior de las "patas" de la A |
| Fondo claro (día) | Antü Dawn | `#FEF2DA` | Brillo dorado de `wallpaper-day.png` |
| Fondo base (día) | Antü Day Navy | `#092042` | Zona azul de `wallpaper-day.png` |

## Variación por edición

- **Antü Legacy**: wallpaper "noche" sin efectos extra (ya es una imagen
  estática liviana, no requiere ajuste para hardware viejo).
- **Antü Standard**: wallpaper "noche" (default).
- **Antü Pro**: se puede usar el wallpaper "día" como variante distintiva,
  o mantener "noche" — a definir cuando se arme el tema completo de esta
  edición.

## Tipografía

El wordmark ya viene renderizado dentro de `logo.png`. Para el resto de la
interfaz (menús, ventanas), usar la fuente por defecto de cada entorno de
escritorio, o unificar con **Inter** / **Noto Sans** si se busca consistencia
entre ediciones.
