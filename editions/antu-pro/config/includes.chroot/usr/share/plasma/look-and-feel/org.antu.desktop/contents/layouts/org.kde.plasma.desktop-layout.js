// Layout de escritorio por defecto de Antü Pro.
//
// - Barra superior: lanzador (kickoff) con el logo de Antü + bandeja del
//   sistema + reloj. Sin lista de ventanas: eso vive en el dock de abajo.
// - Dock: icontasks (apps fijadas + abiertas) en un panel aparte, abajo.
//   Los efectos extra (auto-hide, magnificación al pasar el mouse) quedan
//   para una siguiente etapa (ver docs/ROADMAP.md).
//
// NOTA: esta capa de KDE Plasma no se pudo probar en una sesión gráfica
// real (este proyecto se desarrolló sin entorno gráfico disponible). Usa
// la API de scripting documentada de Plasma, pero antes de darla por
// definitiva conviene bootear la ISO y confirmar que los paneles se arman
// como se espera.

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
launcher.writeConfig("icon", "/usr/share/pixmaps/antu/antu-logo.png");

topBar.addWidget("org.kde.plasma.systemtray");
topBar.addWidget("org.kde.plasma.digitalclock");

var dock = new Panel;
dock.location = "bottom";
dock.height = 56;
dock.addWidget("org.kde.plasma.icontasks");
