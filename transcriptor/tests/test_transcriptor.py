import sys
import types
import wave
from pathlib import Path

import numpy as np
import pytest

from transcriptor import cli, fuentes, salida
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
    def falso(audio, modelo, idioma, dispositivo, al_segmento):
        llamadas.append((audio, modelo, idioma, dispositivo))
        segs = [Segmento(0, 2, "Esto es una prueba."), Segmento(2, 4, "Segunda oración.")]
        for s in segs:
            al_segmento(s)
        return segs, 4.0

    monkeypatch.setattr(cli, "transcribir", falso)


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
    assert "Del subtítulo." in (tmp_path / "Video.md").read_text(encoding="utf-8")


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
