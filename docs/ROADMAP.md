# Roadmap

## Estado actual

Existe el scaffold de las 3 ediciones (estructura de configuración de
`live-build`, listas de paquetes iniciales, branding real) y la
configuración de `live-build` de las 3 **ya fue probada y corre sin
errores** hasta el punto de descargar paquetes de Debian. Una revisión
externa (Codex) encontró que, pese a eso, la estructura de carpetas tenía
un bug real que hacía que `live-build` nunca leyera nuestras
personalizaciones (ver Fase 0, bug #4) — ya corregido y revalidado. Una
**segunda revisión externa**, ya sobre esa corrección, encontró además
que la ubicación de los hooks seguía sin coincidir con la que usa el
`live-build` real de Debian bookworm/trixie (confirmado bajando ambos
tarballs oficiales) y, más grave, que **las 3 ediciones seguían
empaquetando la versión vieja del Resolver** — se había corregido la
fuente pero nunca las copias que realmente se instalan. Ambos, junto con
otros 3 hallazgos menores, ya corregidos y revalidados (ver Fase 0 y
Fase 0.7 para el detalle). Las 3 ediciones
también tienen ya un **shell de escritorio propio** (barra superior +
dock, con la identidad de Antü, ver `docs/ARCHITECTURE.md`) y Standard
suma un **lanzador con buscador** (rofi). El criterio del proyecto
siempre fue no sacar nada booteable hasta tener confianza en que el
shell de las 3 ediciones funciona de verdad, así que primero se agotó
la validación posible sin compilar — contra sesiones de escritorio
reales en una pantalla virtual, no solo por sintaxis. **Las 3 ediciones
ya pasaron por esa validación** (XFCE, Cinnamon y KDE Plasma) y
encontraron y corrigieron bugs reales en el camino en las 3 (ver
`docs/ARCHITECTURE.md` y las capturas en `docs/screenshots/`).

Con eso resuelto, se dio el paso siguiente: **ya se compiló una ISO real
de Antü Standard** (por CI de GitHub Actions, ver Fase 0 para el detalle
— el sandbox de desarrollo no tiene acceso a los mirrors de Debian, pero
los runners de GitHub sí) y se arrancó de verdad en QEMU. La primera
prueba de arranque real **encontró un bug crítico** que ninguna revisión
anterior (ni la de código, ni las sesiones virtuales del shell) podía
haber encontrado: la ISO nunca llegaba a arrancar el sistema live por
faltarle `boot=live` en la línea de arranque real — corregido en las 3
ediciones (ver Fase 0 y `docs/ARCHITECTURE.md` para el detalle
completo). **Con el fix aplicado y una recompilación completa, Antü
Standard ya arrancó de punta a punta hasta un escritorio Cinnamon real**
— confirmado con evidencia concreta (ver Fase 0): un escritorio sostenido
corriendo durante los ~13 minutos de la prueba, con el reloj de la barra
de tareas actualizándose con normalidad y en español. **Primera versión
de Antü que compila y arranca de verdad.** Falta repetir lo mismo para
Legacy y Pro (mismo mecanismo, ya corregido en los 3 `auto/config`).
Las 3 ediciones también tienen **español (Argentina) como idioma por
defecto** y un **set de íconos propios** (tema `Antu`) instalado como
tema de sistema real — ver Fase 0.5. Además ya tienen la **capa de
compatibilidad para migrar desde Windows**: montaje automático de
pendrives/discos externos (NTFS/exFAT/FAT32), Flatpak+Flathub, soporte
de AppImage, LibreOffice con fuentes compatibles con Office, y
wifi/bluetooth/impresoras — ver Fase 0.6. Y ya arrancó la **fusión
funcional** (no solo visual) entre Windows y Linux: Wine integrado para
correr `.exe`/`.msi` con doble clic, validado con el motor corriendo de
verdad contra una pantalla virtual — ver Fase 0.7.

## Fase 0 — Scaffold (completa)

- [x] Definir arquitectura y las 3 ediciones.
- [x] Estructura de carpetas y documentación base.
- [x] Configuración inicial de `live-build` por edición (package-lists
      base, hooks, branding real).
- [x] Scripts `build.sh` y `test-qemu.sh`.
- [x] Validar que `lb config` y `lb build` corren sin errores en las 3
      ediciones (se instaló `live-build` y se corrió de verdad, no solo se
      escribió a mano). Esto encontró y corrigió 3 bugs reales:
      1. Los scripts `auto/build`/`auto/clean` no pasaban `noauto`, lo que
         causaba una **recursión infinita** (`lb build` volvía a ejecutar
         `auto/build`, que volvía a llamar a `lb build`...).
      2. `--mode debian` faltaba: sin él, `lb config` detecta el modo según
         el sistema operativo donde se compila, y en una máquina Ubuntu
         terminaría mezclando la distribución `bookworm` (Debian) con
         mirrors de Ubuntu, rompiendo el build.
      3. `winlux-legacy` (ahora `antu-legacy`) pedía `i386 amd64` juntas,
         pero `live-build` solo soporta **una arquitectura por
         configuración**. Se dejó en `i386` (compatible con hardware de
         32 y 64 bits).
- [x] **Bug crítico #4, encontrado en una revisión externa (Codex) y
      confirmado corriendo `lb config` de verdad**: `auto/` estaba
      anidado *adentro* de `config/` (`editions/<edicion>/config/auto/`)
      en vez de ser su hermano. Como `build.sh` entraba a `config/` antes
      de correr `./auto/config`, `live-build` terminaba buscando
      `config/package-lists`, `config/hooks` y `config/includes.chroot`
      **relativos a esa carpeta** — es decir, dentro de un
      `config/config/` que nunca existió con contenido real. El build
      anterior "corría sin errores" (los 3 bugs de arriba sí estaban
      resueltos) pero **nunca había incorporado ninguna de nuestras
      personalizaciones**: ni Cinnamon/XFCE/Plasma vía package-lists, ni
      Wine, ni el Resolver, ni Samba, ni el branding — todo hubiera
      terminado en un Debian base genérico, sin ningún aviso de error.
      Se corrigió moviendo `auto/` un nivel arriba (hermano de `config/`,
      la estructura estándar de `live-build`) y se validó de nuevo
      corriendo `lb config` contra ambas estructuras para confirmar la
      diferencia con evidencia real, no solo lectura de código. Ver
      `docs/BUILD.md`, sección "Estructura de la configuración de
      `live-build`". **Esto también significa que ninguna validación
      previa de este roadmap que dependiera de un build real (más allá
      de "no tira error") puede darse por buena sin repetirla** — las
      sesiones de escritorio reales (Legacy/Standard) se armaron a mano
      replicando la configuración en este entorno, no extrayéndola de un
      build real, así que esas sí siguen siendo válidas.
- [x] **Bug crítico #5, de una segunda revisión externa**: la ubicación
      de los hooks (`config/hooks/*.chroot`, confirmada contra un
      `live-build` instalado en este entorno) **no coincide con la que
      usa el `live-build` real de Debian bookworm/trixie** — confirmado
      bajando y leyendo los dos tarballs fuente oficiales, que esta vez
      sí se pudieron obtener. Esas versiones buscan
      `config/hooks/normal/*.chroot`. Se corrigió moviendo los hooks a
      esa subcarpeta en las 3 ediciones, y se agregó una advertencia en
      `docs/BUILD.md` para compilar en Debian real (no Ubuntu) y
      confirmar la versión con `dpkg-query -W live-build` antes de dar
      un build por bueno. **Aclarado en una consulta posterior, misma
      revisión**: el mecanismo para habilitar i386 antes de instalar
      paquetes no necesitaba ningún hook — `live-build` ya lo hace solo
      al detectar el formato `paquete:arquitectura` (`wine32:i386`) en
      un package-list, confirmado leyendo `functions/packagelists.sh` +
      `chroot_install-packages` de los mismos tarballs oficiales. Se
      sacó el hook `.chroot_early` (no hacía falta) y se agregó uno
      normal que confirma, después de instalar, que i386 y
      `wine32:i386` quedaron realmente instalados.
- [x] **Bug crítico #6, de la misma revisión**: los 3 bugs corregidos
      del Resolver (ver Fase 0.7) nunca habían llegado a ninguna
      edición — se había arreglado `shared/resolver/antu-resolver` pero
      las 3 copias empaquetadas en `includes.chroot/usr/bin/` seguían
      con el código viejo (confirmado comparando hashes). Corregido de
      raíz: esas copias dejaron de versionarse y ahora `scripts/build.sh`
      las genera en cada build desde la única fuente real, igual que ya
      pasa con el branding.
- [x] **Primera compilación completa de una ISO (Standard) y primer
      arranque real, vía CI de GitHub Actions.** El sandbox de
      desarrollo no tiene acceso a los mirrors de Debian, así que se
      agregó `.github/workflows/build-iso.yml`: compila la edición
      elegida adentro de un contenedor `debian:bookworm` real (los
      runners de GitHub sí tienen internet), sube la ISO como artifact,
      y un segundo job la arranca de verdad en QEMU sacando capturas de
      pantalla del boot — mismo método (captura + inspección) que ya le
      había encontrado bugs reales al shell de escritorio de las 3
      ediciones. La primera compilación de Antü Standard terminó bien
      (ISO real, ~2.9GB, sin errores) — confirma que la estructura de
      `live-build` de este repo es válida de punta a punta contra el
      `live-build` real de Debian bookworm (`20230502`), no solo contra
      supuestos.
      - El primer boot-test murió al instante: el runner tiene `/dev/kvm`
        pero sin permiso de acceso (`Permission denied`) — corregido
        abriendo el permiso a mano (`chmod 666`, runner descartable).
      - El segundo intento (ya con KVM) sacó 20 capturas idénticas — vía
        OCR (tampoco se pueden ver las capturas a simple vista desde el
        sandbox, van por Azure Blob Storage, bloqueado por el proxy del
        entorno) se confirmó que era el menú real de `isolinux`
        ("Press ENTER to boot") esperando una tecla que nada le mandaba.
        Corregido agregando un `sendkey ret` por el monitor de QEMU.
      - **Con eso apareció el bug real y más importante**: la ISO cae a
        un shell de emergencia de `initramfs` ("No root device
        specified. Boot arguments must include a root= parameter") en
        vez de arrancar. Inspeccionando el `isolinux.cfg`/`grub.cfg`
        reales dentro de la ISO se confirmó la causa: `--bootappend-live`
        **reemplaza** el `append`/`linux` de la entrada de arranque por
        defecto en vez de agregarle texto, así que esa entrada quedaba
        con `locales=es_AR.UTF-8 keyboard-layouts=latam` **sin ningún
        `boot=live`** — el kernel nunca se entera de que tiene que
        buscar el sistema live. Esto es justo lo que una revisión externa
        (Codex) había señalado originalmente; se había descartado por
        error en una revisión posterior (verificado en ese momento
        contra un `live-build` de Ubuntu viejo instalado en el sandbox,
        no contra el real de Debian). Corregido agregando
        `boot=live components` al `--bootappend-live` de las 3 ediciones
        (ver `docs/ARCHITECTURE.md`, sección "`--bootappend-live`
        reemplaza el append por defecto, no lo completa", para el
        detalle completo).
      - **Confirmado con una recompilación completa**: con el fix
        aplicado, Antü Standard compiló y arrancó de punta a punta hasta
        un **escritorio Cinnamon real** — no solo pasó del menú, sino que
        se sostuvo corriendo por los ~13 minutos completos de captura.
        Evidencia concreta (vía OCR + diferencia de píxeles entre
        capturas, mismo método indirecto que el resto de esta prueba):
        el frame inmediatamente después de pasar el menú difiere en
        ~33 mil píxeles del menú (la pantalla cambió del todo), el
        siguiente difiere en ~1 millón de píxeles más (se terminó de
        dibujar un escritorio completo), y de ahí en adelante los frames
        alternan entre "0 píxeles distintos" y "~87 píxeles distintos"
        durante el resto de la captura — el patrón exacto de un reloj de
        barra de tareas actualizándose cada tanto en un escritorio
        real e inactivo, no una pantalla trabada. El OCR de esos frames
        además lee un reloj pasando de las 06:30 a las 06:41, con el día
        abreviado en español ("dom", domingo) — confirma de paso que el
        idioma también quedó bien aplicado en la sesión live. **Primera
        ISO de Antü que compila y arranca de punta a punta.**
        Pendiente: repetir compilar+arrancar para Legacy y Pro (mismo
        mecanismo, ya corregido en los 3 `auto/config`).

## Fase 0.5 — Identidad propia (despegarse de Linux/Windows)

Criterio del proyecto: que Antü se sienta propio, no "Linux con logo
pegado". Aplica a las 3 ediciones por igual.

- [x] **Español (Argentina) como idioma por defecto** de las 3 ediciones
      (`hooks/normal/0300-locale-es.hook.chroot`, genera y activa
      `es_AR.UTF-8`). Validado con una sesión XFCE real: los nombres y
      categorías de las aplicaciones se traducen correctamente. La
      cobertura de los textos propios de cada herramienta (botones,
      títulos de ventana) depende de la traducción que traiga cada
      paquete — confirmar en Debian real (se probó en un entorno de
      desarrollo basado en Ubuntu). **Corregido tras una tercera revisión
      externa (Codex)**: ese hook alcanza para el sistema ya instalado,
      pero no para la sesión live que arranca directo desde la ISO —
      esa la arma `live-config` en cada arranque a partir de parámetros
      de arranque, no del filesystem, y por defecto usa inglés. Se
      agregó `--bootappend-live "locales=es_AR.UTF-8
      keyboard-layouts=latam"` en `auto/config` de las 3 ediciones. Ver
      `docs/ARCHITECTURE.md`.
- [x] **Set de íconos propios** (tema `Antu`, skeuomórfico, lenguaje
      visual de Antü: vidrio/metal azul + arco de luz cian), instalado
      como tema freedesktop real (`shared/branding/icons/antu-icons/`,
      3 tamaños: 256/48/24px) y fijado por defecto en las 3 ediciones.
      Cubre: papelera vacía/llena (con swap automático nativo del
      estándar `user-trash`/`user-trash-full`), carpeta genérica,
      carpeta Descargas, Equipo, Red y la insignia "Bienvenida a Antü".
      Ver `docs/ARCHITECTURE.md`, sección "Íconos propios". Pendiente
      para más adelante: el resto de los íconos de sistema
      (configuración, terminal, etc.), que por ahora usan la base
      genérica heredada (`hicolor`).

## Fase 0.6 — Compatibilidad veniendo de Windows

Criterio del proyecto: alguien que usaba Windows migra sin sentir que
perdió funcionalidad. Aplica a las 3 ediciones (`compat.list.chroot` y
`hardware.list.chroot` nuevos, ver `docs/ARCHITECTURE.md` sección
"Compatibilidad: veniendo de Windows").

- [x] **Pendrives/discos externos**: montaje automático (`udisks2` +
      `gvfs` + `policykit-1`) con lectura/escritura NTFS (`ntfs-3g`),
      exFAT (`exfatprogs`) y FAT32 (`dosfstools`). Validado con
      imágenes de disco de prueba: el ciclo completo montar → escribir →
      leer → desmontar se confirmó de punta a punta para NTFS. FAT32 y
      exFAT no se pudieron probar en este entorno de desarrollo porque
      su kernel recortado no trae los módulos `vfat`/`exfat` (el kernel
      real de Debian sí los trae) — validar en una máquina/VM real.
- [x] **Apps fuera de los repos de Debian**: Flatpak + repositorio de
      Flathub agregado de fábrica, con tienda gráfica (GNOME Software en
      Standard, Discover en Pro) y soporte de AppImage (`libfuse2`) en
      las 3.
- [x] **Ofimática**: LibreOffice (ya estaba en Standard/Pro) + fuentes
      métricamente compatibles con Arial/Calibri/Cambria/Times New Roman
      (`fonts-liberation2`, `fonts-crosextra-carlito`,
      `fonts-crosextra-caladea`), para que un `.docx` de Word no se vea
      corrido al abrirlo.
- [x] **Wifi/bluetooth/impresoras**: firmware no libre de los chipsets
      más comunes, `bluez`+`blueman`, y `cups` con drivers + `avahi` para
      detectar impresoras de red solas. No se pudo probar contra
      hardware real (no hay wifi/bluetooth/impresora físicos en este
      entorno) — pendiente de validar en una máquina real.
- [ ] **Claude y Microsoft Office no tienen versión nativa para Linux**
      (aclarado en `docs/ARCHITECTURE.md`): el camino real es claude.ai
      desde el navegador y LibreOffice respectivamente. Queda pendiente,
      si se quiere, armar un acceso directo de escritorio que abra
      claude.ai "como app".

## Fase 0.7 — Fusión funcional (WinLux de verdad)

Criterio del proyecto, dicho por Juan desde el arranque: Antü no es
"Linux con logo de Antü" — es una fusión real de Windows y Linux, no
solo visual. Esta fase es donde eso se hace ingeniería concreta, sin
apuro (plazo: el año que viene).

- [x] **Wine**: correr `.exe`/`.msi` de Windows directo, con doble
      clic, integrado al sistema (no como "opción avanzada" en una
      terminal). Multiarch i386 en Standard/Pro (necesario para el
      software de 32 bits, la mayoría del software viejo) resuelto solo
      por `live-build` al detectar `wine32:i386` en el package-list —
      sin ningún hook propio (una versión anterior tuvo uno, de más,
      sacado tras confirmar el mecanismo real leyendo el código fuente
      oficial). `hooks/normal/0070-verify-wine32.hook.chroot` confirma
      después de instalar que quedó realmente habilitado. Asociación de
      tipo de archivo
      (`.exe`→`wine`, `.msi`→`wine msiexec /i`) validada de verdad:
      un archivo con el encabezado real de un ejecutable de Windows se
      reconoce solo y el sistema resuelve que se abre con Wine, sin
      configurar nada (`xdg-mime query default` lo confirma). También
      se probó el motor completo: Wine corriendo una app de Windows con
      ventana real contra una pantalla virtual, más el puente de
      archivos Windows↔Linux funcionando (escribir desde el lado
      Windows, leer desde el lado Linux). Ver `docs/ARCHITECTURE.md`,
      sección "Fusión funcional: correr programas de Windows (Wine)".
- [x] **Antü Resolver**: componente central que decide cómo abrir/
      instalar cada archivo (`.exe`/`.msi` → Wine, `.AppImage` →
      ejecución directa, `.deb` → apt, `.flatpakref` → Flatpak), con una
      caché en disco (`~/.local/share/antu/resolver-profiles.json`) de
      qué motor le funcionó a cada app para no repetir el intento cada
      vez. Idea sugerida por Sofi; implementada como herramienta real
      (`shared/resolver/antu-resolver`, instalada en las 3 ediciones) y
      no solo como concepto. Los `.desktop` de asociación de `.exe`/
      `.msi` ahora llaman al Resolver, no a Wine directo — de cara al
      usuario dice "Abrir con Antü", no "Abrir con Wine". Validado de
      punta a punta contra una pantalla virtual. Una revisión externa
      (Codex) encontró 3 bugs reales más, los tres corregidos y
      confirmados con pruebas: el estado quedaba pegado en "éxito"
      después de un fallo tardío (ahora usa 3 estados:
      failed/started/exited), una condición de carrera podía perder
      actualizaciones con dos lanzamientos simultáneos (ahora con lock
      exclusivo), y las rutas relativas se pasaban mal a `apt` (ahora se
      normalizan a absolutas). También se blindó contra una caché
      corrupta con forma equivocada, y la identidad de cada app en la
      caché pasó a ser nombre+tamaño (no solo el nombre, que hacía
      colisionar instaladores distintos con el mismo nombre típico como
      "setup.exe"). **Una segunda revisión encontró que nada de esto
      había llegado a ninguna edición** (las copias empaquetadas seguían
      con el código viejo) y una entrada de caché puntual con forma
      inválida también podía romper — ambos corregidos, el primero de
      raíz (ver Fase 0). **Una tercera revisión encontró que esa
      protección cubría la lectura pero no la escritura**: guardar una
      actualización sobre una entrada corrupta rompía con `TypeError`.
      Corregido y probado con los 4 casos pedidos (entrada lista, nula,
      cadena y una sana de control) — las corruptas quedan reparadas, la
      sana no se toca. Ver `docs/ARCHITECTURE.md`, sección "Antü
      Resolver".
- [x] **ANTU Home** (idea de Sofi: que los documentos sean "los mismos"
      para cualquier app, sea nativa o de Windows): ya está lograda para
      todo lo que corre por Wine, gratis, sin construir nada — es cómo
      Wine mapea de fábrica `C:\Users\...\Documents` a la carpeta real
      de Linux (confirmado con la prueba de escritura/lectura cruzada
      de la Fase anterior).
- [x] **ANTU Device Bridge** (idea de Sofi: compartir portapapeles/
      impresora/audio entre apps nativas y de Windows): mismo caso,
      para Wine ya viene gratis (portapapeles de X11 compartido,
      impresión por CUPS). Solo haría falta construir algo a medida si
      más adelante se suma una VM (ver "ANTU Windows Core" más abajo).
- [ ] **Bottles**: interfaz gráfica sobre Wine (un "prefijo" aislado por
      app, instalador visual) — mucho más amigable que Wine pelado.
      Se instala como Flatpak desde la tienda de apps que ya está
      configurada (Fase 0.6); no se bakea en la ISO porque necesitaría
      internet real a Flathub durante el build, algo no probado en este
      entorno. Una vez instalado no necesita integración a medida: va a
      aparecer solo como alternativa en el "Abrir con..." de cualquier
      `.exe`, al lado del Resolver (mecanismo estándar de asociación de
      archivos, ver `docs/ARCHITECTURE.md`).
- [x] **Red mixta con PCs Windows (Samba)**: el ícono "Red" (Fase 0.5)
      ahora tiene algo real detrás. `samba` + `smbclient` + `cifs-utils`
      + `wsdd` (para que Windows 10/11 vea a Antü en la red con el
      mecanismo de descubrimiento moderno, no el NetBIOS viejo) en las
      3 ediciones, con una carpeta compartida (`/srv/antu-compartido`)
      lista de fábrica. **Corregido tras una revisión externa (Codex)**:
      la primera versión daba acceso de invitado con permisos `0777` —
      Windows 10/11 actualizado restringe ese acceso por política (puede
      directamente no dejar conectarse) y era además una escritura
      anónima demasiado abierta. Ahora la carpeta requiere una cuenta
      (`sudo antu-compartir-configurar` la habilita en un paso). Validado
      con protocolo SMB real en los dos sentidos: el acceso de invitado
      queda rechazado (`NT_STATUS_ACCESS_DENIED`) y una cuenta real sube
      y baja archivos sin problema. **Una segunda revisión señaló que
      dos cuentas autorizadas no necesariamente podían colaborar**
      (archivos quedando del grupo primario de quien los creó, no del
      grupo compartido) — corregido con `force group` y validado
      creando dos usuarios reales con grupos distintos: A crea, B
      sobrescribe y agrega contenido nuevo sin error de permisos. Ver
      `docs/ARCHITECTURE.md`, sección "Red mixta con PCs Windows
      (Samba)".
- [ ] **Gaming (Proton/Steam)**: que la biblioteca de Steam con juegos
      de Windows funcione, pensado sobre todo para Antü Pro (hardware
      potente). No arrancado todavía.
- [ ] **.NET nativo** (`dotnet-runtime`, sin pasar por Wine) para
      software moderno hecho en .NET Core/5+, que corre nativo en
      Linux sin necesitar ningún traductor. No arrancado todavía.
- [ ] **Antü Store propia**: una única app (no la Store genérica de
      cada DE) que unifique apt + Flatpak + AppImage + instaladores de
      Wine en una sola interfaz — "instalar" sin que el usuario sepa ni
      le importe qué mecanismo hay detrás. `antu-resolver` ya distingue
      `.deb`/`.flatpakref` además de `.exe`/`.msi`, así que la lógica de
      backend ya arrancó; falta la interfaz gráfica. Es la pieza más
      ambiciosa de toda la fusión — dejarla para cuando el resto de esta
      fase esté maduro.
- [ ] **ANTU Windows Core** (idea de Sofi: VM de Windows tan integrada
      que se sienta invisible, para el software que ni Wine ni Proton
      logren correr). Objetivo de largo plazo, con dos límites reales
      que no son de ingeniería: necesita que el usuario aporte su propia
      licencia e ISO de Windows (ninguna distro puede regalar Windows
      por dentro), y mostrar *solo* la ventana de la app con GPU
      acelerada es un problema serio (la técnica más conocida,
      RemoteApp, necesita Windows Server/RDS; la GPU acelerada en una
      VM en general necesita dos placas de video). Ver
      `docs/ARCHITECTURE.md` para el detalle. Una VM de Windows normal
      (ventana completa, sin el modo "invisible") sí sería simple de
      ofrecer desde ya con `virt-manager`, si en algún momento hace
      falta.
- [ ] **ANTU Link** (idea de Sofi: app complementaria para Windows que
      sincronice carpetas/preferencias, para migrar sin perder el punto
      de partida). En vez de programarlo desde cero, evaluar armarlo
      sobre **Syncthing** (software libre y maduro) con la cara de Antü
      encima.
- [ ] **Perfiles de compatibilidad comunitarios** (idea de Sofi): antes
      de construir una base propia (necesita una comunidad de usuarios
      que hoy no existe), evaluar que `antu-resolver` consulte bases ya
      existentes como [WineHQ AppDB](https://appdb.winehq.org) o
      [ProtonDB](https://www.protondb.com).

## Fase 1 — Antü Standard (MVP)

Se prioriza esta edición porque cubre el público más amplio (uso
doméstico/oficina).

- [x] Compilar ISO booteable en modo live (sin instalar). Confirmado
      por CI (GitHub Actions): compila y arranca de verdad hasta un
      escritorio Cinnamon real — ver Fase 0 para el detalle y la
      evidencia.
- [ ] Instalador funcional (usar `calamares` o el instalador de Debian).
- [x] Shell de escritorio propio (barra superior: lanzador, bandeja,
      reloj) — ver `docs/ARCHITECTURE.md`, sección "Shell de escritorio".
      **Probado con una sesión Cinnamon real** (Xvfb): funciona tal cual
      se diseñó, sin necesitar fixes como los de Legacy. Ver captura real
      en `docs/screenshots/antu-standard-desktop.png`.
- [x] Dock inferior (grouped-window-list: apps fijadas + abiertas en un
      panel aparte), también confirmado con la sesión real. Falta el
      indicador propio (el arco de luz del logo en vez de un puntito),
      que necesita un tema visual propio.
- [ ] Ícono del lanzador con el logo de Antü (hoy usa el genérico de
      Cinnamon — confirmado al probar con sesión real; cambiarlo requiere
      tocar la configuración específica de esa instancia del applet).
- [x] Lanzador con buscador (rofi + tema propio, Super+Espacio). **Es la
      única pieza del shell que se pudo probar visualmente de verdad**
      (con una pantalla virtual Xvfb) — ver captura en
      `docs/ARCHITECTURE.md`. Falta que el logo de la barra también lo
      abra (hoy abre el menú nativo de Cinnamon).
- [ ] Panel de ajustes rápidos (red, volumen, brillo) desde la barra.
- [ ] Tema visual propio (cursores, colores, GTK theme oscuro — los
      íconos ya están, ver Fase 0.5).
- [x] Paquetería base: navegador (Firefox), ofimática (LibreOffice +
      fuentes compatibles con Office), reproductor multimedia (VLC),
      gestor de archivos (Nemo, viene con Cinnamon). Ver Fase 0.6.
- [ ] Probar en hardware real (no solo QEMU).

## Fase 2 — Antü Legacy

- [x] Configurar la edición en `i386` (`live-build` no soporta múltiples
      arquitecturas en una misma configuración; `i386` corre en hardware de
      32 y 64 bits, a diferencia de `amd64`).
- [x] Shell de escritorio propio en XFCE (barra superior única),
      **probado con una sesión XFCE real** (Xvfb + xfce4-session) — la
      única de las 3 ediciones validada así hasta ahora. Encontró y
      corrigió 2 bugs reales: el wallpaper no se aplicaba (el nombre del
      monitor varía por hardware, no se puede adivinar en un XML
      estático) y XFCE tiene 4 escritorios virtuales con wallpaper
      independiente cada uno. Solución: `usr/local/bin/antu-set-wallpaper`
      + autostart, que detecta los nombres reales en vez de adivinarlos.
      **Una revisión externa (Codex) encontró un 3er bug** en ese mismo
      script: corría en todos los inicios de sesión, así que si el
      usuario elegía otro wallpaper a mano, se lo volvía a pisar en el
      siguiente login. Corregido con un centinela por usuario y
      confirmado con una prueba real (elegir otro fondo → reiniciar
      sesión → el cambio se mantiene). **Una segunda revisión encontró
      un 4to bug**: ese centinela se creaba siempre, incluso si XFCE
      tardaba demasiado y no se llegaba a aplicar nada — corregido para
      que solo se marque "hecho" tras confirmar de verdad que se aplicó,
      probado con los dos casos (con y sin `xfdesktop` a tiempo). Ver
      `docs/ARCHITECTURE.md` y la captura real en
      `docs/screenshots/antu-legacy-desktop.png`.
- [x] Desactivar composición/efectos: la documentación lo decía pero no
      existía el archivo que lo aplicaba de verdad (`xfwm4.xml`,
      `use_compositing=false`) — falta explícita señalada en la misma
      revisión externa, ya corregida.
- [ ] Reducir el set de paquetes.
- [ ] Validar arranque y uso fluido en hardware con ≤2GB RAM.

## Fase 3 — Antü Pro

- [x] Shell de escritorio propio vía un paquete "Look and Feel" de Plasma
      (`org.antu.desktop`): barra superior (lanzador, bandeja, reloj) +
      dock inferior (icontasks). Era la pieza con más riesgo de las 3
      (formato de Plasma más complejo) — **ya se probó con una sesión
      Plasma real** (`kwin_x11` + `plasmashell` contra `Xvfb`), que
      encontró y corrigió 2 bugs reales (ícono del lanzador ilegible y
      bandeja mal ubicada). Ver `docs/ARCHITECTURE.md` y la captura en
      `docs/screenshots/antu-pro-desktop.png`.
- [ ] Efectos del dock (auto-hide, magnificación al pasar el mouse) y
      efectos visuales en general (blur, animaciones).
- [ ] Entorno KDE Plasma con efectos completos.
- [ ] Ajustes de kernel/scheduler para multinúcleo.
- [ ] Soporte de drivers propietarios de GPU (NVIDIA/AMD) opcional durante
      la instalación.
- [ ] Soporte Wayland.

## Fase 4 — Pulido y distribución

- [ ] Documentación de usuario final (instalación, primeros pasos).
- [ ] Sistema de actualizaciones propio o wrapper sobre APT.
- [ ] Publicar imágenes ISO de cada edición como releases del repositorio.
- [ ] Sitio/landing simple con capturas y descargas.

## Cómo contribuir a una fase

Cada tarea de este roadmap puede convertirse en un issue del repositorio.
Al tomar una tarea, actualizar el checkbox correspondiente en el PR que la
resuelve.
