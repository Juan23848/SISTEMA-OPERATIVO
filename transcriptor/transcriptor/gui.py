"""Ventana del Transcriptor: arrastrar o pegar, apretar un botón, leer el texto.

El trabajo pesado (descargar, transcribir) corre en un hilo aparte y le
avisa a la ventana por una cola de eventos; la ventana nunca se congela.
"""

import contextlib
import io
import json
import os
import queue
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import customtkinter as ctk

from . import __version__
from .fuentes import ErrorFuente, carpeta_temporal, desde_archivo, desde_url, es_url, expandir
from .salida import nombre_seguro
from .segmentos import Cancelado, formato_tiempo
from .sistema import abrir, carpeta_documentos
from .trabajo import transcribir_fuente

# Paleta de Antü (shared/branding/palette.md), en pares (modo claro, modo oscuro).
AZUL = ("#006CE2", "#1E8CF0")
AZUL_HOVER = ("#0057B8", "#1EAEFC")
FONDO = ("#F4F7FB", "#0B1428")
TARJETA = ("#FFFFFF", "#12203D")
BORDE = ("#C9D6EA", "#2A3D63")
TEXTO_SUAVE = ("#5B6B85", "#9FB2D3")
ROJO = ("#C62828", "#EF5350")
ROJO_HOVER = ("#A31F1F", "#E53935")

IDIOMAS = {
    "Español": "es", "Inglés": "en", "Portugués": "pt", "Italiano": "it",
    "Francés": "fr", "Alemán": "de", "Detectar automáticamente": None,
}
CALIDADES = {
    "Rápida": "base",
    "Normal (recomendada)": "small",
    "Precisa (más lenta)": "turbo",
}
FORMATOS = ["docx", "txt"]


def _ruta_config() -> Path:
    base = os.environ.get("APPDATA") or os.path.join(Path.home(), ".config")
    return Path(base) / "Transcriptor" / "config.json"


def _leer_config() -> dict:
    try:
        return json.loads(_ruta_config().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _guardar_config(datos: dict) -> None:
    try:
        ruta = _ruta_config()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


class _SalidaACola(io.TextIOBase):
    """Lo que las librerías imprimen (descargas, avisos) va al registro de la ventana."""

    def __init__(self, eventos: "queue.Queue"):
        self.eventos = eventos

    def write(self, texto: str) -> int:
        for linea in texto.replace("\r", "\n").split("\n"):
            if linea.strip() and not linea.lstrip().startswith("[download]"):
                self.eventos.put(("registro", linea.rstrip()))
        return len(texto)


def _ventana_base():
    """CTk con arrastrar y soltar si tkinterdnd2 está disponible; si no, sin él."""
    try:
        from tkinterdnd2 import TkinterDnD

        class VentanaDnD(ctk.CTk, TkinterDnD.DnDWrapper):
            def __init__(self, *a, **k):
                super().__init__(*a, **k)
                self.TkdndVersion = TkinterDnD._require(self)
                self.arrastre_disponible = True

        return VentanaDnD
    except Exception:
        class VentanaSimple(ctk.CTk):
            arrastre_disponible = False

        return VentanaSimple


class Aplicacion(_ventana_base()):
    def __init__(self, entradas_iniciales: Optional[List[str]] = None):
        super().__init__()
        ctk.set_default_color_theme("blue")
        self.title("Transcriptor")
        self.geometry("880x760")
        self.minsize(720, 640)
        self.configure(fg_color=FONDO)
        self._poner_icono()

        self.config_guardada = _leer_config()
        self.carpeta_salida = Path(self.config_guardada.get("carpeta") or carpeta_documentos())
        self.cola: List[str] = []
        self.eventos: "queue.Queue" = queue.Queue()
        self.cancelar = threading.Event()
        self.detener_grabacion = threading.Event()
        self.trabajando = False
        self.ultimo_resultado: Optional[Path] = None

        self._armar()
        self.after(100, self._atender_eventos)
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        if entradas_iniciales:
            self._agregar(entradas_iniciales)
            self.after(300, self._empezar)

    # ------------------------------------------------------------------ armado

    def _poner_icono(self):
        icono = Path(__file__).parent / "recursos" / "icono.png"
        try:
            import tkinter
            self._icono = tkinter.PhotoImage(file=str(icono))
            self.iconphoto(True, self._icono)
        except Exception:
            pass

    def _tarjeta(self, padre, **kw):
        return ctk.CTkFrame(padre, fg_color=TARJETA, corner_radius=14, border_width=1,
                            border_color=BORDE, **kw)

    def _armar(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Encabezado
        cab = ctk.CTkFrame(self, fg_color="transparent")
        cab.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        ctk.CTkLabel(cab, text="Transcriptor", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(cab, text="Pasá clases, videos y audios a texto y a Word. Todo en tu compu, sin reproducir nada.",
                     text_color=TEXTO_SUAVE).pack(anchor="w")

        # Entrada: arrastrar, elegir o pegar
        entrada = self._tarjeta(self)
        entrada.grid(row=1, column=0, sticky="ew", padx=24, pady=8)
        entrada.grid_columnconfigure(0, weight=1)

        self.zona = ctk.CTkFrame(entrada, fg_color=("#EAF2FD", "#0F2A55"), corner_radius=12,
                                 border_width=2, border_color=AZUL, height=110)
        self.zona.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        self.zona.grid_propagate(False)
        self.zona.grid_columnconfigure(0, weight=1)
        texto_zona = ("Arrastrá acá videos, audios o carpetas" if self.arrastre_disponible
                      else "Elegí videos, audios o una carpeta")
        self.etiqueta_zona = ctk.CTkLabel(self.zona, text=texto_zona, font=ctk.CTkFont(size=16, weight="bold"),
                                          text_color=AZUL)
        self.etiqueta_zona.grid(row=0, column=0, pady=(18, 6))
        botones_zona = ctk.CTkFrame(self.zona, fg_color="transparent")
        botones_zona.grid(row=1, column=0)
        ctk.CTkButton(botones_zona, text="Elegir archivos…", width=150, fg_color=AZUL, hover_color=AZUL_HOVER,
                      command=self._elegir_archivos).pack(side="left", padx=6)
        ctk.CTkButton(botones_zona, text="Elegir carpeta…", width=150, fg_color="transparent", border_width=1,
                      border_color=AZUL, text_color=AZUL, hover_color=("#DCE8FA", "#173A70"),
                      command=self._elegir_carpeta).pack(side="left", padx=6)
        if self.arrastre_disponible:
            from tkinterdnd2 import DND_FILES, DND_TEXT
            for w in (self.zona, self.etiqueta_zona):
                w.drop_target_register(DND_FILES, DND_TEXT)
                w.dnd_bind("<<Drop>>", self._soltar)

        fila_link = ctk.CTkFrame(entrada, fg_color="transparent")
        fila_link.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 6))
        fila_link.grid_columnconfigure(0, weight=1)
        self.link = ctk.CTkEntry(fila_link, height=38, fg_color=("#F7F9FC", "#0E1A33"), border_color=BORDE,
                                 placeholder_text="…o pegá un link: YouTube, Google Drive, Vimeo, Instagram…")
        self.link.grid(row=0, column=0, sticky="ew")
        self.link.bind("<Return>", lambda e: self._empezar())
        ctk.CTkButton(fila_link, text="Pegar", width=80, height=38, fg_color="transparent", border_width=1,
                      border_color=BORDE, text_color=("gray20", "gray85"), hover_color=("#E4EAF3", "#1A2A4A"),
                      command=self._pegar).grid(row=0, column=1, padx=(8, 0))

        self.lista = ctk.CTkLabel(entrada, text="", text_color=TEXTO_SUAVE, justify="left", anchor="w")
        self.quitar = ctk.CTkButton(entrada, text="Quitar todo", width=90, height=24, fg_color="transparent",
                                    text_color=TEXTO_SUAVE, hover_color=("#E4EAF3", "#1A2A4A"),
                                    command=self._vaciar_cola)

        opciones = ctk.CTkFrame(entrada, fg_color="transparent")
        opciones.grid(row=4, column=0, sticky="ew", padx=16, pady=(10, 16))
        opciones.grid_columnconfigure(4, weight=1)
        ctk.CTkLabel(opciones, text="Idioma").grid(row=0, column=0, padx=(2, 6))
        self.idioma = ctk.CTkOptionMenu(opciones, values=list(IDIOMAS), width=190, fg_color=AZUL,
                                        button_color=AZUL, button_hover_color=AZUL_HOVER)
        self.idioma.set(self.config_guardada.get("idioma", "Español"))
        self.idioma.grid(row=0, column=1, padx=(0, 18))
        ctk.CTkLabel(opciones, text="Calidad").grid(row=0, column=2, padx=(0, 6))
        self.calidad = ctk.CTkOptionMenu(opciones, values=list(CALIDADES), width=190, fg_color=AZUL,
                                         button_color=AZUL, button_hover_color=AZUL_HOVER)
        self.calidad.set(self.config_guardada.get("calidad", "Normal (recomendada)"))
        self.calidad.grid(row=0, column=3)
        self.boton = ctk.CTkButton(opciones, text="Transcribir", width=170, height=42,
                                   font=ctk.CTkFont(size=15, weight="bold"), fg_color=AZUL,
                                   hover_color=AZUL_HOVER, command=self._boton_principal)
        self.boton.grid(row=0, column=5, sticky="e")

        # Progreso
        prog = self._tarjeta(self)
        prog.grid(row=2, column=0, sticky="ew", padx=24, pady=8)
        prog.grid_columnconfigure(0, weight=1)
        self.estado = ctk.CTkLabel(prog, text="Listo para empezar.", font=ctk.CTkFont(size=14, weight="bold"),
                                   anchor="w")
        self.estado.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        self.barra = ctk.CTkProgressBar(prog, height=10, progress_color=AZUL)
        self.barra.set(0)
        self.barra.grid(row=1, column=0, sticky="ew", padx=16)
        self.detalle = ctk.CTkLabel(prog, text="", text_color=TEXTO_SUAVE, anchor="w")
        self.detalle.grid(row=2, column=0, sticky="ew", padx=16, pady=(4, 12))

        # Resultado
        res = self._tarjeta(self)
        res.grid(row=3, column=0, sticky="nsew", padx=24, pady=8)
        res.grid_columnconfigure(0, weight=1)
        res.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(res, text="Texto", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").grid(
            row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        self.texto = ctk.CTkTextbox(res, wrap="word", font=ctk.CTkFont(size=13), border_width=0,
                                    fg_color=("#F7F9FC", "#0E1A33"))
        self.texto.grid(row=1, column=0, sticky="nsew", padx=16)
        self._mostrar_texto("Acá aparece el texto cuando termina. Se guarda solo como documento de Word "
                            f"y como .txt en:\n{self.carpeta_salida}")
        acciones = ctk.CTkFrame(res, fg_color="transparent")
        acciones.grid(row=2, column=0, sticky="ew", padx=16, pady=12)
        self.b_copiar = ctk.CTkButton(acciones, text="Copiar texto", width=130, fg_color=AZUL,
                                      hover_color=AZUL_HOVER, command=self._copiar, state="disabled")
        self.b_copiar.pack(side="left")
        self.b_word = ctk.CTkButton(acciones, text="Abrir en Word", width=130, fg_color=AZUL,
                                    hover_color=AZUL_HOVER, command=self._abrir_word, state="disabled")
        self.b_word.pack(side="left", padx=8)
        ctk.CTkButton(acciones, text="Abrir carpeta", width=120, fg_color="transparent", border_width=1,
                      border_color=BORDE, text_color=("gray20", "gray85"), hover_color=("#E4EAF3", "#1A2A4A"),
                      command=lambda: abrir(self._carpeta_lista())).pack(side="left")
        ctk.CTkButton(acciones, text="Cambiar carpeta…", width=130, fg_color="transparent",
                      text_color=TEXTO_SUAVE, hover_color=("#E4EAF3", "#1A2A4A"),
                      command=self._cambiar_carpeta).pack(side="left", padx=4)
        self.b_grabar = ctk.CTkButton(acciones, text="● Grabar lo que suena", width=170, fg_color="transparent",
                                      border_width=1, border_color=ROJO, text_color=ROJO,
                                      hover_color=("#FBE9E9", "#3A1A1F"), command=self._grabar)
        self.b_grabar.pack(side="right")
        self._habilitar_resultado(False)

        pie = ctk.CTkLabel(self, text=f"v{__version__} · Si un video no se puede bajar de ninguna forma, "
                                      "reproducilo y usá «Grabar lo que suena» (último recurso).",
                           text_color=TEXTO_SUAVE, font=ctk.CTkFont(size=11))
        pie.grid(row=4, column=0, sticky="w", padx=26, pady=(0, 10))

    # ------------------------------------------------------------- cola/entrada

    def _agregar(self, entradas: List[str]):
        for e in entradas:
            e = e.strip().strip('"').strip("'")
            if e and e not in self.cola:
                self.cola.append(e)
        self._actualizar_lista()

    def _actualizar_lista(self):
        if not self.cola:
            self.lista.grid_remove()
            self.quitar.grid_remove()
            return
        nombres = [c if es_url(c) else Path(c).name or c for c in self.cola]
        visibles = "\n".join(f"•  {n}" for n in nombres[:6])
        if len(nombres) > 6:
            visibles += f"\n…y {len(nombres) - 6} más"
        self.lista.configure(text=f"Para transcribir ({len(nombres)}):\n{visibles}")
        self.lista.grid(row=2, column=0, sticky="ew", padx=18, pady=(4, 0))
        self.quitar.grid(row=3, column=0, sticky="w", padx=12)

    def _vaciar_cola(self):
        self.cola.clear()
        self._actualizar_lista()

    def _soltar(self, evento):
        partes = self.tk.splitlist(evento.data)
        self._agregar(list(partes))

    def _elegir_archivos(self):
        from tkinter import filedialog
        rutas = filedialog.askopenfilenames(
            title="Elegí videos o audios",
            filetypes=[("Videos y audios", "*.mp4 *.mkv *.avi *.mov *.webm *.wmv *.flv *.m4v *.3gp *.mpg *.mpeg "
                                           "*.ts *.mp3 *.m4a *.wav *.ogg *.opus *.oga *.flac *.aac *.wma *.amr"),
                       ("Todos los archivos", "*.*")])
        if rutas:
            self._agregar(list(rutas))

    def _elegir_carpeta(self):
        from tkinter import filedialog
        carpeta = filedialog.askdirectory(title="Elegí una carpeta con videos o audios")
        if carpeta:
            self._agregar([carpeta])

    def _pegar(self):
        try:
            contenido = self.clipboard_get().strip()
        except Exception:
            return
        self.link.delete(0, "end")
        self.link.insert(0, contenido)

    def _cambiar_carpeta(self):
        from tkinter import filedialog
        carpeta = filedialog.askdirectory(title="¿Dónde guardo las transcripciones?",
                                          initialdir=str(self._carpeta_lista()))
        if carpeta:
            self.carpeta_salida = Path(carpeta)
            self._guardar_preferencias()
            self.detalle.configure(text=f"Las transcripciones se guardan en: {self.carpeta_salida}")

    def _carpeta_lista(self) -> Path:
        self.carpeta_salida.mkdir(parents=True, exist_ok=True)
        return self.carpeta_salida

    def _guardar_preferencias(self):
        _guardar_config({"idioma": self.idioma.get(), "calidad": self.calidad.get(),
                         "carpeta": str(self.carpeta_salida)})

    # ------------------------------------------------------------------ acciones

    def _boton_principal(self):
        if self.trabajando:
            self.cancelar.set()
            self.boton.configure(text="Cancelando…", state="disabled")
        else:
            self._empezar()

    def _empezar(self):
        if self.trabajando:
            return
        link = self.link.get().strip()
        if link:
            self._agregar([link])
            self.link.delete(0, "end")
        if not self.cola:
            self.estado.configure(text="Primero arrastrá un archivo, elegilo o pegá un link.")
            self.zona.configure(border_color=ROJO)
            self.after(1200, lambda: self.zona.configure(border_color=AZUL))
            return
        entradas = expandir(self.cola)
        self.cola = []
        self._actualizar_lista()
        if not entradas:
            self.estado.configure(text="No encontré videos ni audios en lo que elegiste.")
            return
        self._guardar_preferencias()
        opciones = dict(modelo=CALIDADES[self.calidad.get()], idioma=IDIOMAS[self.idioma.get()],
                        carpeta=self._carpeta_lista())
        self._modo_trabajo(True)
        threading.Thread(target=self._trabajar, args=(entradas, opciones), daemon=True).start()

    def _modo_trabajo(self, activo: bool, grabando: bool = False):
        self.trabajando = activo
        self.cancelar.clear()
        if activo:
            self.boton.configure(text="Cancelar", fg_color=ROJO, hover_color=ROJO_HOVER, state="normal")
            self.b_grabar.configure(state="disabled" if not grabando else "normal")
        else:
            self.boton.configure(text="Transcribir", fg_color=AZUL, hover_color=AZUL_HOVER, state="normal")
            self.b_grabar.configure(state="normal", text="● Grabar lo que suena")

    def _grabar(self):
        if self.trabajando and not self.detener_grabacion.is_set() and self.b_grabar.cget("text").startswith("■"):
            self.detener_grabacion.set()
            self.b_grabar.configure(text="Deteniendo…", state="disabled")
            return
        if self.trabajando:
            return
        self.detener_grabacion.clear()
        self._guardar_preferencias()
        opciones = dict(modelo=CALIDADES[self.calidad.get()], idioma=IDIOMAS[self.idioma.get()],
                        carpeta=self._carpeta_lista())
        self._modo_trabajo(True, grabando=True)
        self.b_grabar.configure(text="■ Detener y transcribir")
        threading.Thread(target=self._trabajar_grabacion, args=(opciones,), daemon=True).start()

    def _copiar(self):
        texto = self.texto.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.b_copiar.configure(text="¡Copiado!")
        self.after(1500, lambda: self.b_copiar.configure(text="Copiar texto"))

    def _abrir_word(self):
        if self.ultimo_resultado:
            abrir(self.ultimo_resultado)

    def _habilitar_resultado(self, si: bool):
        for b in (self.b_copiar, self.b_word):
            b.configure(state="normal" if si else "disabled", fg_color=AZUL if si else ("#C9D3E3", "#26385A"),
                        text_color_disabled=("#F2F5FA", "#7F93B5"))

    def _mostrar_texto(self, texto: str):
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", texto)
        self.texto.configure(state="disabled")

    def _cerrar(self):
        if self.trabajando:
            from tkinter import messagebox
            if not messagebox.askyesno("Transcriptor", "Hay una transcripción en curso. ¿Cerrar igual?\n"
                                       "Lo hecho hasta ahora queda en un archivo .parcial.txt."):
                return
            self.cancelar.set()
            self.detener_grabacion.set()
        self.destroy()

    # ------------------------------------------------- trabajo (en otro hilo)

    def _avisar(self, *evento):
        self.eventos.put(evento)

    def _cancelado(self) -> bool:
        return self.cancelar.is_set()

    def _trabajar(self, entradas: List[str], op: dict):
        terminados, errores = 0, 0
        with contextlib.redirect_stdout(_SalidaACola(self.eventos)):
            for n, entrada in enumerate(entradas, 1):
                if self._cancelado():
                    break
                prefijo = f"({n} de {len(entradas)}) " if len(entradas) > 1 else ""
                nombre = entrada if es_url(entrada) else Path(entrada).name
                try:
                    if es_url(entrada):
                        with carpeta_temporal() as tmp:
                            self._avisar("estado", f"{prefijo}Bajando el audio…", None)
                            self._avisar("detalle", nombre)

                            def al_descargar(fraccion):
                                if self._cancelado():
                                    raise Cancelado()
                                self._avisar("barra", fraccion)

                            fuente = desde_url(entrada, Path(tmp), al_descargar=al_descargar)
                            self._transcribir_una(fuente, op, prefijo)
                    else:
                        self._transcribir_una(desde_archivo(entrada), op, prefijo)
                    terminados += 1
                except Cancelado:
                    self._avisar("fin", "Cancelado. Lo transcripto hasta ahora quedó en un archivo .parcial.txt.")
                    return
                except ErrorFuente as e:
                    errores += 1
                    self._avisar("error", nombre, str(e))
                except Exception as e:  # que un archivo roto no frene el resto
                    errores += 1
                    # Los RuntimeError son mensajes nuestros, ya escritos para leer.
                    detalle = str(e) if isinstance(e, RuntimeError) else f"{e.__class__.__name__}: {e}"
                    self._avisar("error", nombre, detalle)
        if errores and not terminados:
            self._avisar("fin", "No se pudo transcribir. Mirá el detalle en el cuadro de texto.")
        elif errores:
            self._avisar("fin", f"Terminado: {terminados} bien, {errores} con problemas.")
        else:
            self._avisar("fin", "¡Listo! " + ("Ya está el documento de Word." if terminados == 1
                                               else f"Se transcribieron {terminados} archivos."))

    def _transcribir_una(self, fuente, op: dict, prefijo: str):
        titulo = fuente.titulo
        self._avisar("estado", f"{prefijo}Preparando el reconocimiento de voz…", None)
        self._avisar("detalle", "La primera vez se descarga el modelo (puede tardar unos minutos).")
        inicio = [None]

        def al_progreso(hecho: float, total: float):
            if inicio[0] is None:
                inicio[0] = time.monotonic()
                self._avisar("estado", f"{prefijo}Transcribiendo: {titulo}", 0.0)
            fraccion = min(hecho / total, 1.0) if total else 0.0
            transcurrido = time.monotonic() - inicio[0]
            falta = ""
            if fraccion > 0.03:
                falta = f" · faltan ~{formato_tiempo(transcurrido / fraccion - transcurrido)}"
            self._avisar("barra", fraccion)
            self._avisar("detalle", f"{formato_tiempo(hecho)} de {formato_tiempo(total)}{falta}")

        rutas, texto = transcribir_fuente(fuente, op["carpeta"], op["modelo"], op["idioma"], "auto",
                                          FORMATOS, al_progreso=al_progreso, cancelado=self._cancelado)
        if not rutas:
            self._avisar("error", titulo, "No se detectó voz en este audio.")
            return
        self._avisar("resultado", texto, rutas[0])

    def _trabajar_grabacion(self, op: dict):
        from .grabacion import grabar
        titulo = f"Grabación {datetime.now():%Y-%m-%d %H-%M}"
        audio = op["carpeta"] / (nombre_seguro(titulo) + ".wav")
        with contextlib.redirect_stdout(_SalidaACola(self.eventos)):
            try:
                self._avisar("estado", "Grabando lo que suena en la compu… Reproducí el video ahora.", 0.0)

                def al_avance(segundos: float, nivel: float):
                    self._avisar("barra", nivel)
                    self._avisar("detalle", f"{formato_tiempo(segundos)} grabados · cuando termine el video, "
                                            "apretá «Detener y transcribir»")

                grabar(audio, detener=self.detener_grabacion, al_avance=al_avance)
                self._avisar("grabacion_terminada")
                from .fuentes import Fuente
                self._transcribir_una(Fuente(titulo=titulo, origen="grabación del audio de la compu",
                                             audio=audio), op, "")
                self._avisar("fin", "¡Listo! Ya está el documento de Word.")
            except Cancelado:
                self._avisar("fin", f"Cancelado. El audio grabado quedó en {audio}.")
            except Exception as e:
                self._avisar("error", "Grabación", str(e))
                self._avisar("fin", "No se pudo grabar.")

    # -------------------------------------------- eventos (en el hilo de la ventana)

    def _atender_eventos(self):
        try:
            while True:
                tipo, *datos = self.eventos.get_nowait()
                if tipo == "estado":
                    texto, barra = datos
                    self.estado.configure(text=texto)
                    if barra is None:
                        self.barra.configure(mode="indeterminate")
                        self.barra.start()
                    else:
                        self.barra.stop()
                        self.barra.configure(mode="determinate")
                        self.barra.set(barra)
                elif tipo == "barra":
                    if self.barra.cget("mode") == "indeterminate":
                        self.barra.stop()
                        self.barra.configure(mode="determinate")
                    self.barra.set(datos[0])
                elif tipo == "detalle":
                    self.detalle.configure(text=datos[0])
                elif tipo == "registro":
                    linea = datos[0].strip()
                    if linea.startswith(("Probando", "No se pudo", "Funcionó", "Descargando", "Encontré")):
                        self.detalle.configure(text=linea)
                elif tipo == "grabacion_terminada":
                    self.b_grabar.configure(text="● Grabar lo que suena", state="disabled")
                elif tipo == "resultado":
                    texto, docx = datos
                    self.ultimo_resultado = docx
                    self.barra.set(1.0)
                    self._mostrar_texto(texto)
                    self._habilitar_resultado(True)
                elif tipo == "error":
                    nombre, mensaje = datos
                    self.ultimo_resultado = None
                    self._habilitar_resultado(False)
                    self._mostrar_texto(f"No se pudo con: {nombre}\n\n{mensaje}")
                elif tipo == "fin":
                    self.barra.stop()
                    self.barra.configure(mode="determinate")
                    self.estado.configure(text=datos[0])
                    self.detalle.configure(text=f"Guardado en: {self.carpeta_salida}")
                    self._modo_trabajo(False)
        except queue.Empty:
            pass
        self.after(100, self._atender_eventos)


def main(argv: Optional[List[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    ctk.set_appearance_mode("system")
    app = Aplicacion(entradas_iniciales=argv or None)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
