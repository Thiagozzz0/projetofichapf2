"""Funções auxiliares compartilhadas pelos exportadores de Castles & Crusades."""

from __future__ import annotations

import re
import unicodedata


def nome_arquivo_seguro_cc(nome: str | None, classe: str | None, nivel: int, extensao: str) -> str:
    """Gera nome de arquivo seguro (ASCII/slug) para download da ficha C&C."""
    base = f"{nome or 'personagem'}_{classe or 'classe'}_nv{int(nivel)}"
    sem_acento = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", sem_acento.lower()).strip("_")
    ext = extensao.lstrip(".").lower()
    return f"ficha_cc_{slug}.{ext}"


def fmt_mod(valor: int | float) -> str:
    """Formata modificador com sinal (+N, 0, -N)."""
    iv = int(valor)
    if iv > 0:
        return f"+{iv}"
    return str(iv)


def fmt_movimento(metros: float | int) -> str:
    """Formata deslocamento em metros sem .0 desnecessário."""
    f = float(metros)
    if f.is_integer():
        return f"{int(f)} m"
    return f"{str(round(f, 1)).replace('.', ',')} m"
