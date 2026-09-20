// Layout de escritorio por defecto de Antü Pro.
//
// - Barra superior: lanzador (kickoff) con el logo de Antü + bandeja del
//   sistema + reloj. Sin lista de ventanas: eso vive en el dock de abajo.
// - Dock: icontasks (apps fijadas + abiertas) en un panel aparte, abajo.
//   Los efectos extra (auto-hide, magnificación al pasar el mouse) quedan
//   para una siguiente etapa (ver docs/ROADMAP.md).
//
// Probado con una sesión Plasma real (kwin_x11 + plasmashell contra Xvfb,
// mismo mecanismo que ya se usó con Legacy/Standard) — ver
// docs/ARCHITECTURE.md. Encontró y corrigió 2 bugs reales: el ícono del
// lanzador usaba el logo completo (ícono + texto "ANTÜ"), ilegible a 22px
// de panel; y sin un spacer explícito, la bandeja del sistema quedaba
// pegada al lanzador (izquierda) en vez de junto al reloj (derecha), como
// pide el diseño.

var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; i++) {
    allDesktops[i].wallpaperPlugin = "org.kde.image";
    allDesktops[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    allDesktops[i].writeConfig("Image", "file:///usr/share/backgrounds/antu/wallpaper.png");
}

var topBar = new Panel;
topBar.location = "top";
topBar.height = 32;

var launcher = topBar.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "start-here");

topBar.addWidget("org.kde.plasma.panelspacer");
topBar.addWidget("org.kde.plasma.systemtray");
topBar.addWidget("org.kde.plasma.digitalclock");

var dock = new Panel;
dock.location = "bottom";
dock.height = 56;
dock.addWidget("org.kde.plasma.icontasks");
