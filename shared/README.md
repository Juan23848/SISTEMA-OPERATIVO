# shared/

Recursos compartidos por las tres ediciones de Antü OS.

- `branding/`: logo, wallpapers e iconos comunes. Cada edición puede
  agregar o sobrescribir assets propios en su carpeta
  `editions/<edicion>/config/includes.chroot/`.
- `scripts/`: utilidades de shell reutilizadas por `scripts/build.sh` u
  otros scripts de build (por ahora vacío, se completa a medida que haga
  falta compartir lógica entre ediciones).
