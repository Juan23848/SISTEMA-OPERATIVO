# Antü Legacy

Edición pensada para PCs con hardware equivalente a la era de **Windows XP**:
procesadores de 1-2 núcleos, 512MB–2GB de RAM, sin aceleración 3D confiable.

## Características

- Arquitectura: `i386` (32 bits). Corre tanto en hardware de 32 como de 64
  bits, a diferencia de `amd64` — por eso es la elegida para esta edición.
- Escritorio: **XFCE**, sin compositor activado por defecto.
- Apariencia: identidad Antü con glow reducido y sin blur (colores planos),
  para que se vea bien incluso sin aceleración gráfica.
- Paquetes mínimos: se prioriza el arranque rápido y el bajo consumo de RAM
  sobre las funcionalidades extra.

## Compilar esta edición

Desde la raíz del repositorio:

```bash
./scripts/build.sh antu-legacy
```

Ver [`docs/BUILD.md`](../../docs/BUILD.md) para más detalle.

## Estructura

```
config/
├── auto/               # Scripts config/build/clean de live-build
├── package-lists/      # Paquetes de escritorio y aplicaciones
├── includes.chroot/    # Branding y archivos de configuración propios
└── hooks/              # Scripts que corren durante el build
```
