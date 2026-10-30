import sys
import types
import time
import wave
from pathlib import Path

import numpy as np
import pytest

from transcriptor import cli, fuentes, salida, trabajo
from transcriptor.segmentos import Segmento, formato_tiempo


def test_formato_tiempo():
    assert formato_tiempo(0) == "00:00:00"
    assert formato_tiempo(3725.5) == "01:02:05"
    assert formato_tiempo(3725.5, con_ms=True) == "01:02:05,500"


def test_parrafos_cortan_en_pausas_largas():
    segs = [
        Segmento(0, 2, "Hola a todos."),
        Segmento(2.2, 4, "Hoy vemos derivadas."),
        Segmento(10, 12, "Primer ejemplo."),
    ]
    parrafos = salida.armar_parrafos(segs)
    assert [p.texto for p in parrafos] == ["Hola a todos. Hoy vemos derivadas.", "Primer ejemplo."]
    assert parrafos[1].inicio == 10


def test_parrafos_largos_se_parten_al_final_de_oracion():
    segs = [Segmento(i, i + 1, "palabra " * 20 + "fin.") for i in range(10)]
    parrafos = salida.armar_parrafos(segs)
    assert len(parrafos) > 1
    assert all(p.texto.endswith("fin.") for p in parrafos)


def test_nombre_seguro():
    assert salida.nombre_seguro('Clase 3: "Límites" / parte 1?') == "Clase 3 Límites parte 1"
    assert salida.nombre_seguro("...") == "transcripcion"


def test_guardar_genera_los_tres_formatos(tmp_path):
    segs = [Segmento(0, 1.5, "Hola."), Segmento(5, 6, "Chau.")]
    rutas = salida.guardar(segs, "Clase 1", "clase1.mp4", 6, tmp_path, ["txt", "md", "srt"])
    assert [r.suffix for r in rutas] == [".txt", ".md", ".srt"]
    md = (tmp_path / "Clase 1.md").read_text(encoding="utf-8")
    assert "**[00:00:05]** Chau." in md
    srt = (tmp_path / "Clase 1.srt").read_text(encoding="utf-8")
    assert "1\n00:00:00,000 --> 00:00:01,500\nHola." in srt
    txt = (tmp_path / "Clase 1.txt").read_text(encoding="utf-8")
    assert "Hola." in txt and "[00:" not in txt.split("\n", 5)[-1]


def test_parsear_vtt():
    vtt = """WEBVTT

00:00:01.000 --> 00:00:03.500 align:start
<c>Bienvenidos</c> a la clase

00:00:03.500 --> 00:00:05.000
Bienvenidos a la clase

01:00:00.000 --> 01:00:02.000
Última frase
"""
    segs = fuentes.parsear_vtt(vtt)
    assert [s.texto for s in segs] == ["Bienvenidos a la clase", "Última frase"]
    assert segs[0].inicio == 1.0 and segs[0].fin == 3.5
    assert segs[1].inicio == 3600


def test_elegir_subtitulos_prefiere_idioma_y_ignora_automaticos():
    info = {
        "subtitles": {"en": [{"ext": "vtt", "url": "en"}], "es-419": [{"ext": "vtt", "url": "es"}]},
        "automatic_captions": {"es": [{"ext": "vtt", "url": "auto"}]},
    }
    assert fuentes._elegir_subtitulos(info, "es")["url"] == "es"
    assert fuentes._elegir_subtitulos(info, "fr") is None
    assert fuentes._elegir_subtitulos({"automatic_captions": info["automatic_captions"]}, "es") is None


def test_es_url_y_expandir_carpeta(tmp_path):
    assert fuentes.es_url("https://drive.google.com/file/d/x/view")
    assert not fuentes.es_url("C:\\clases\\video.mp4")
    (tmp_path / "PTT-20260101-WA0001.opus").write_bytes(b"")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "clase.MP4").write_bytes(b"")
    (tmp_path / "notas.pdf").write_bytes(b"")
    encontrados = fuentes.expandir([str(tmp_path), "https://youtu.be/x"])
    assert [Path(p).name for p in encontrados[:2]] == ["PTT-20260101-WA0001.opus", "clase.MP4"]
    assert encontrados[2] == "https://youtu.be/x"


def test_cookies_navegador_con_perfil(tmp_path):
    op = fuentes._opciones_ytdlp(tmp_path, "chrome:Profile 1")
    assert op["cookiesfrombrowser"] == ("chrome", "Profile 1", None, None)
    assert "cookiesfrombrowser" not in fuentes._opciones_ytdlp(tmp_path, None)


def test_explicar_error_sugiere_cookies_si_es_privado():
    msg = fuentes._explicar_error("ERROR: Sign in to confirm", "https://x", None)
    assert "--cookies-navegador" in msg and "transcribir grabar" in msg


@pytest.mark.parametrize("texto,segundos", [("90", 5400), ("90m", 5400), ("1h30m", 5400), ("45s", 45)])
def test_duracion(texto, segundos):
    assert cli._duracion(texto) == segundos


def test_formatos_invalidos():
    with pytest.raises(Exception):
        cli._formatos("txt,pdf")
    assert cli._formatos(".TXT, srt") == ["txt", "srt"]


def _whisper_falso(monkeypatch, llamadas):
    def falso(audio, modelo, idioma, dispositivo, al_segmento, al_progreso=None):
        llamadas.append((audio, modelo, idioma, dispositivo))
        segs = [Segmento(0, 2, "Esto es una prueba."), Segmento(2, 4, "Segunda oración.")]
        for s in segs:
            al_segmento(s)
        return segs, 4.0

    monkeypatch.setattr(trabajo, "transcribir", falso)


def test_cli_archivo_local_de_punta_a_punta(tmp_path, monkeypatch):
    llamadas = []
    _whisper_falso(monkeypatch, llamadas)
    audio = tmp_path / "PTT-WA0001.opus"
    audio.write_bytes(b"x")
    out = tmp_path / "out"
    codigo = cli.main([str(audio), "-o", str(out), "-m", "turbo", "-i", "auto", "--cpu", "-f", "txt,srt"])
    assert codigo == 0
    assert llamadas == [(audio, "turbo", None, "cpu")]
    assert sorted(p.name for p in out.iterdir()) == ["PTT-WA0001.srt", "PTT-WA0001.txt"]
    assert "Esto es una prueba. Segunda oración." in (out / "PTT-WA0001.txt").read_text(encoding="utf-8")


def test_cli_archivo_inexistente_no_frena_el_resto(tmp_path, monkeypatch):
    llamadas = []
    _whisper_falso(monkeypatch, llamadas)
    bueno = tmp_path / "bueno.mp3"
    bueno.write_bytes(b"x")
    codigo = cli.main([str(tmp_path / "no-existe.mp4"), str(bueno), "-o", str(tmp_path / "out")])
    assert codigo == 1
    assert len(llamadas) == 1


def test_cli_url_usa_subtitulos_sin_transcribir(tmp_path, monkeypatch):
    llamadas = []
    _whisper_falso(monkeypatch, llamadas)

    def desde_url_falso(url, carpeta, cookies, usar_subs, idioma):
        assert usar_subs and idioma == "es"
        return fuentes.Fuente("Video", url, subtitulos=[Segmento(0, 3, "Del subtítulo.")])

    monkeypatch.setattr(cli, "desde_url", desde_url_falso)
    assert cli.main(["https://youtu.be/abc", "--subtitulos", "-o", str(tmp_path)]) == 0
    assert llamadas == []
    assert "Del subtítulo." in (tmp_path / "Video.txt").read_text(encoding="utf-8")


def test_grabar_escribe_wav_valido(tmp_path, monkeypatch):
    class Grabador:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def record(self, numframes):
            return np.full((numframes, 2), 0.5, dtype="float32")

    class Entrada:
        name = "Parlantes (monitor)"

        def recorder(self, samplerate, channels):
            return Grabador()

    sc = types.SimpleNamespace(
        get_microphone=lambda nombre, include_loopback: Entrada(),
        default_speaker=lambda: types.SimpleNamespace(name="Parlantes"),
        default_microphone=lambda: Entrada(),
    )
    monkeypatch.setitem(sys.modules, "soundcard", sc)
    from transcriptor import grabacion

    destino = tmp_path / "g.wav"
    segundos = grabacion.grabar(destino, duracion=2)
    assert segundos == 2
    with wave.open(str(destino)) as w:
        assert (w.getnchannels(), w.getframerate(), w.getnframes()) == (1, 16000, 32000)
        muestras = np.frombuffer(w.readframes(10), dtype="<i2")
        assert (muestras == int(0.5 * 32767)).all()


def test_docx_se_abre_y_tiene_el_texto(tmp_path):
    from docx import Document

    segs = [Segmento(0, 2, "Hoy vemos límites y derivadas."), Segmento(9, 11, "Ejercicio uno.")]
    salida.guardar(segs, "Análisis I - Clase 3", "https://drive.google.com/x", 11, tmp_path, ["docx"])
    doc = Document(str(tmp_path / "Análisis I - Clase 3.docx"))
    textos = [p.text for p in doc.paragraphs]
    assert textos[0] == "Análisis I - Clase 3"
    assert "[00:00:00]  Hoy vemos límites y derivadas." in textos
    assert "[00:00:09]  Ejercicio uno." in textos
    assert doc.styles["Normal"].font.name == "Calibri"


def test_cli_copia_al_portapapeles_y_formatos_por_defecto(tmp_path, monkeypatch):
    llamadas, copiado = [], []
    _whisper_falso(monkeypatch, llamadas)
    monkeypatch.setattr(cli, "copiar_al_portapapeles", lambda t: copiado.append(t) or True)
    audio = tmp_path / "clase.mp4"
    audio.write_bytes(b"x")
    out = tmp_path / "out"
    assert cli.main([str(audio), "-o", str(out), "--copiar"]) == 0
    assert sorted(p.name for p in out.iterdir()) == ["clase.docx", "clase.txt"]
    assert copiado == ["clase\n\nEsto es una prueba. Segunda oración."]


def test_salida_por_defecto_en_documentos(tmp_path, monkeypatch):
    llamadas = []
    _whisper_falso(monkeypatch, llamadas)
    monkeypatch.setattr(cli, "carpeta_documentos", lambda: tmp_path / "Documentos" / "Transcripciones")
    audio = tmp_path / "a.opus"
    audio.write_bytes(b"x")
    assert cli.main([str(audio), "-f", "txt"]) == 0
    assert (tmp_path / "Documentos" / "Transcripciones" / "a.txt").exists()


def _yt_dlp_falso(monkeypatch, tmp_path, navegador_que_anda):
    """yt-dlp de mentira: el link es privado y solo se puede bajar con la sesión de un navegador."""
    intentos = []

    class DownloadError(Exception):
        pass

    class YoutubeDL:
        def __init__(self, opciones):
            self.nav = (opciones.get("cookiesfrombrowser") or (None,))[0]

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def extract_info(self, url, download):
            intentos.append(self.nav)
            if self.nav is None:
                raise DownloadError("ERROR: [GoogleDrive] x: Sign in to view this file")
            if self.nav != navegador_que_anda:
                raise FileNotFoundError(f"could not find {self.nav} cookies database")
            return {"title": "Clase privada", "id": "x"}

        def process_ie_result(self, info, download):
            ruta = tmp_path / "x.m4a"
            ruta.write_bytes(b"audio")
            return {**info, "requested_downloads": [{"filepath": str(ruta)}]}

    falso = types.SimpleNamespace(YoutubeDL=YoutubeDL, utils=types.SimpleNamespace(DownloadError=DownloadError))
    monkeypatch.setitem(sys.modules, "yt_dlp", falso)
    return intentos


def test_link_privado_reintenta_solo_con_la_sesion_del_navegador(tmp_path, monkeypatch):
    intentos = _yt_dlp_falso(monkeypatch, tmp_path, "edge")
    fuente = fuentes.desde_url("https://drive.google.com/file/d/x/view", tmp_path)
    assert fuente.titulo == "Clase privada" and fuente.audio.exists()
    assert intentos == [None, "firefox", "edge"]


def test_link_privado_sin_ningun_navegador_explica_que_hacer(tmp_path, monkeypatch):
    intentos = _yt_dlp_falso(monkeypatch, tmp_path, "ninguno")
    with pytest.raises(fuentes.ErrorFuente) as error:
        fuentes.desde_url("https://drive.google.com/file/d/x/view", tmp_path)
    assert intentos == [None, *fuentes.NAVEGADORES]
    assert "Firefox" in str(error.value)


def test_separar_entradas(tmp_path):
    con_espacios = tmp_path / "clase 1.mp4"
    con_espacios.write_bytes(b"")
    assert cli._separar_entradas(f'"{con_espacios}"') == [str(con_espacios)]
    assert cli._separar_entradas(str(con_espacios)) == [str(con_espacios)]
    assert cli._separar_entradas(" https://youtu.be/abc ") == ["https://youtu.be/abc"]
    assert cli._separar_entradas('"C:\\a b.mp4" "C:\\c.opus"') == ["C:\\a b.mp4", "C:\\c.opus"]


def test_ventana_transcribe_y_muestra_el_texto(tmp_path, monkeypatch):
    pytest.importorskip("tkinter")
    pytest.importorskip("customtkinter")
    import tkinter
    from transcriptor import gui

    llamadas = []
    _whisper_falso(monkeypatch, llamadas)
    monkeypatch.setattr(gui, "_ruta_config", lambda: tmp_path / "config.json")
    try:
        app = gui.Aplicacion()
    except tkinter.TclError:
        pytest.skip("no hay pantalla")
    try:
        app.carpeta_salida = tmp_path / "out"
        audio = tmp_path / "clase.mp4"
        audio.write_bytes(b"x")
        app._agregar([str(audio)])
        app._empezar()
        for _ in range(100):  # el trabajo corre en otro hilo
            app.update()
            if not app.trabajando:
                break
            time.sleep(0.05)
        assert not app.trabajando
        assert "Esto es una prueba. Segunda oración." in app.texto.get("1.0", "end")
        assert app.ultimo_resultado == tmp_path / "out" / "clase.docx"
        assert app.b_copiar.cget("state") == "normal"
        assert (tmp_path / "config.json").exists()  # recuerda idioma y calidad
    finally:
        app.destroy()


def test_elegir_rueda_toma_la_mas_nueva_de_la_version_mayor():
    from transcriptor import aceleracion

    def rueda(nombre):
        return {"filename": nombre, "url": "u/" + nombre, "size": 1}

    datos = {"releases": {
        "12.4.5.8": [rueda("cublas-12.4.5.8-win_amd64.whl")],  # muy vieja para RTX 50
        "12.9.1.4": [rueda("cublas-12.9.1.4-win_amd64.whl"), rueda("cublas-12.9.1.4-manylinux.whl")],
        "12.10.0.1": [{**rueda("cublas-12.10.0.1-win_amd64.whl"), "yanked": True}],
        "13.0.0.19": [rueda("cublas-13.0.0.19-win_amd64.whl")],  # otra versión mayor: no sirve
    }}
    assert aceleracion.elegir_rueda(datos, "12.", (12, 8))["filename"] == "cublas-12.9.1.4-win_amd64.whl"
    with pytest.raises(aceleracion.ErrorAceleracion):
        aceleracion.elegir_rueda(datos, "11.", (11, 0))


def test_extraer_solo_las_dll(tmp_path):
    import zipfile
    from transcriptor import aceleracion

    rueda = tmp_path / "x.whl"
    with zipfile.ZipFile(rueda, "w") as z:
        z.writestr("nvidia/cudnn/bin/cudnn64_9.dll", b"dll")
        z.writestr("nvidia/cudnn/bin/cudnn_ops64_9.dll", b"dll")
        z.writestr("nvidia/cudnn/include/cudnn.h", b"h")
        z.writestr("nvidia_cudnn_cu12-9.dist-info/METADATA", b"m")
    destino = tmp_path / "cuda"
    assert aceleracion.extraer_bibliotecas(rueda, destino) == 2
    assert sorted(p.name for p in destino.iterdir()) == ["cudnn64_9.dll", "cudnn_ops64_9.dll"]


def test_fuera_del_exe_de_windows_no_se_ofrece_la_placa():
    from transcriptor import aceleracion
    assert not aceleracion.aplica() or sys.platform == "win32"
    assert not aceleracion.gpu_lista() or aceleracion.aplica()


def test_si_la_placa_falla_al_empezar_sigue_con_el_procesador(tmp_path, monkeypatch):
    from transcriptor import aceleracion, transcripcion

    class ModeloFalso:
        def __init__(self, device):
            self.model = types.SimpleNamespace(device=device)

    usados, fallas = [], []
    monkeypatch.setattr(transcripcion, "cargar_modelo", lambda nombre, disp: ModeloFalso(
        "cpu" if disp == "cpu" else "cuda"))
    monkeypatch.setattr(aceleracion, "marcar_falla", lambda: fallas.append(True))

    def transcribir_con(whisper, en_gpu, audio, idioma, al_segmento, al_progreso):
        usados.append(whisper.model.device)
        if en_gpu:
            raise RuntimeError("cuBLAS failed with status CUBLAS_STATUS_NOT_SUPPORTED")
        return [Segmento(0, 1, "Hola.")], 1.0

    monkeypatch.setattr(transcripcion, "_transcribir_con", transcribir_con)
    segs, _ = transcripcion.transcribir(tmp_path / "a.mp4", "small", "es", "auto")
    assert usados == ["cuda", "cpu"] and fallas == [True]
    assert segs[0].texto == "Hola."


def test_un_error_despues_de_empezar_no_se_reintenta():
    from transcriptor import transcripcion

    def generador():
        yield "primer pedazo"
        raise RuntimeError("se quedó sin memoria")

    g = transcripcion._marcar_si_ya_empezo(generador())
    assert next(g) == "primer pedazo"
    with pytest.raises(transcripcion._YaEmpezado):
        next(g)
