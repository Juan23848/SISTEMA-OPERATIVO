# Antü Standard

Edición para uso **doméstico y de oficina**, en hardware equivalente al de
**Windows 7 en adelante**: procesadores multinúcleo modernos, 4GB+ de RAM.

## Características

- Arquitectura: `amd64`.
- Escritorio: **Cinnamon**, con menú inicio, barra de tareas y bandeja del
  sistema con la disposición clásica de Windows 7/10.
- Apariencia: identidad Antü con glow moderado (fondo azul profundo, líneas
  de luz), balance entre estética y recursos.
- Aplicaciones base: navegador, suite ofimática, reproductor multimedia,
  editor de imágenes.

Esta es la edición **prioritaria** del proyecto (ver
[`docs/ROADMAP.md`](../../docs/ROADMAP.md), Fase 1), por ser la que cubre al
público más amplio.

## Compilar esta edición

Desde la raíz del repositorio:

```bash
./scripts/build.sh antu-standard
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
