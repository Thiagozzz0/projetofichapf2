"""Funções utilitárias compartilhadas pelo motor procedural."""

from __future__ import annotations

import math
import re
import unicodedata
from typing import Iterable

# ---------------------------------------------------------------------------
# Atributos
# ---------------------------------------------------------------------------
ATRIBUTOS = ["for", "des", "con", "int", "sab", "car"]

NOME_ATRIBUTO = {
    "for": "Força",
    "des": "Destreza",
    "con": "Constituição",
    "int": "Inteligência",
    "sab": "Sabedoria",
    "car": "Carisma",
}

_ALIASES_ATRIBUTO = {
    "for": "for", "forca": "for", "str": "for",
    "des": "des", "destreza": "des", "dex": "des",
    "con": "con", "constituicao": "con",
    "int": "int", "inteligencia": "int",
    "sab": "sab", "sabedoria": "sab", "wis": "sab",
    "car": "car", "carisma": "car", "cha": "car",
}


def normalizar(texto: str | None) -> str:
    """Minúsculas, sem acentos e com espaços simples."""
    if not texto:
        return ""
    sem_acento = unicodedata.normalize("NFKD", str(texto))
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.lower()).strip()


def slugify(texto: str | None, remover_parenteses: bool = True) -> str:
    """Converte um nome do livro em um ID no padrão dos JSONs (ex.: 'Mãos Flamejantes*' -> 'maos_flamejantes')."""
    t = normalizar(texto)
    if remover_parenteses:
        t = re.sub(r"\(.*?\)", " ", t)
    t = t.replace("*", " ")
    t = re.sub(r"[^a-z0-9]+", "_", t)
    return t.strip("_")


def atributo_id(nome: str | None) -> str | None:
    """Converte 'Constituição', 'forca', 'FOR' etc. para o ID curto ('con', 'for'...)."""
    chave = slugify(nome)
    return _ALIASES_ATRIBUTO.get(chave)


def modificador(valor: int) -> int:
    """Modificador de atributo: floor((valor - 10) / 2)."""
    return math.floor((valor - 10) / 2)


# ---------------------------------------------------------------------------
# Proficiência
# ---------------------------------------------------------------------------
GRAUS = ["destreinado", "treinado", "especialista", "mestre", "lendario"]
BONUS_GRAU = {"destreinado": 0, "treinado": 2, "especialista": 4, "mestre": 6, "lendario": 8}
SIGLA_GRAU = {"destreinado": "D", "treinado": "T", "especialista": "E", "mestre": "M", "lendario": "L"}


def grau_normalizado(texto: str | dict | None) -> str:
    """Extrai o grau de proficiência de textos como 'destreinado (embora ...)' ou {'graduacao': 'treinado'}."""
    if isinstance(texto, dict):
        texto = texto.get("graduacao")
    t = normalizar(texto if isinstance(texto, str) else "")
    for grau in reversed(GRAUS):
        if t.startswith(grau):
            return grau
    return "destreinado"


def melhor_grau(*graus: str) -> str:
    return max(graus, key=lambda g: GRAUS.index(g))


def bonus_proficiencia(grau: str, nivel: int) -> int:
    """Destreinado = 0; demais = bônus do grau + nível."""
    if grau == "destreinado":
        return 0
    return BONUS_GRAU[grau] + nivel


# ---------------------------------------------------------------------------
# Moedas e Volume
# ---------------------------------------------------------------------------
def pc_para_moedas(total_pc: int) -> dict[str, int]:
    """Converte peças de cobre para po/pp/pc (sem usar platina no 1º nível)."""
    po, resto = divmod(max(0, int(total_pc)), 100)
    pp, pc = divmod(resto, 10)
    return {"pl": 0, "po": po, "pp": pp, "pc": pc}


def formatar_preco(total_pc: int | None) -> str:
    if total_pc is None:
        return "—"
    m = pc_para_moedas(total_pc)
    partes = [f"{m[k]} {k}" for k in ("po", "pp", "pc") if m[k]]
    return ", ".join(partes) if partes else "0 pc"


def formatar_volume(volume_inteiro: int, leves: int) -> str:
    if volume_inteiro and leves:
        return f"{volume_inteiro}, {leves}L"
    if leves:
        return f"{leves}L"
    return str(volume_inteiro)


def primeiro(iteravel: Iterable, padrao=None):
    for item in iteravel:
        return item
    return padrao


def formatar_bonus(valor: int) -> str:
    return f"+{valor}" if valor >= 0 else str(valor)


def formatar_metros(valor: float) -> str:
    texto = f"{valor:.1f}".replace(".", ",")
    return texto[:-2] if texto.endswith(",0") else texto
