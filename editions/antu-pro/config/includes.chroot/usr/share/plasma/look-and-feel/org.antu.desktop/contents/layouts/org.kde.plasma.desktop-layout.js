// Layout de escritorio por defecto de Antü Pro.
//
// Mismo esquema que las otras 2 ediciones (barra superior única: lanzador
// con el logo de Antü + tareas + bandeja + reloj). El dock separado y los
// efectos extra quedan para una siguiente etapa (ver docs/ROADMAP.md).
//
// NOTA: esta capa de KDE Plasma no se pudo probar en una sesión gráfica
// real (este proyecto se desarrolló sin entorno gráfico disponible). Usa
// la API de scripting documentada de Plasma, pero antes de darla por
// definitiva conviene bootear la ISO y confirmar que el panel se arma
// como se espera.

var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; i++) {
    allDesktops[i].wallpaperPlugin = "org.kde.image";
    allDesktops[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    allDesktops[i].writeConfig("Image", "file:///usr/share/backgrounds/antu/wallpaper.png");
}

var panel = new Panel;
panel.location = "top";
panel.height = 32;

var launcher = panel.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "/usr/share/pixmaps/antu/antu-logo.png");

panel.addWidget("org.kde.plasma.icontasks");
panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.digitalclock");
