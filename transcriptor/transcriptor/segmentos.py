"""Tipo común para los fragmentos de texto con tiempo, vengan de Whisper o de subtítulos."""

from dataclasses import dataclass


class Cancelado(Exception):
    """La persona apretó "Cancelar" (o Ctrl+C) en medio del trabajo."""


@dataclass
class Segmento:
    inicio: float  # segundos
    fin: float  # segundos
    texto: str


def formato_tiempo(segundos: float, con_ms: bool = False) -> str:
    """12.5 -> '00:00:12' (o '00:00:12,500' para SRT)."""
    total_ms = int(round(segundos * 1000))
    horas, resto = divmod(total_ms, 3_600_000)
    minutos, resto = divmod(resto, 60_000)
    segs, ms = divmod(resto, 1000)
    base = f"{horas:02d}:{minutos:02d}:{segs:02d}"
    return f"{base},{ms:03d}" if con_ms else base
