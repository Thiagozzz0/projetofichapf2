"""Carregamento e cache em memória dos dados JSON de Castles & Crusades (1ª Ed. Brasileira)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
DIR_DADOS_CC = RAIZ_PROJETO / "dados" / "dadosc&c"
TEMPLATE_PDF_CC = DIR_DADOS_CC / "templates" / "ficha_oficial_cc.pdf"

CATEGORIAS_EQUIPAMENTOS = (
    "elmos",
    "armaduras",
    "escudos",
    "armas_corpo_a_corpo",
    "armas_projeteis",
    "transporte_e_arreios",
    "equipamento_geral",
    "roupas",
    "provisoes_e_alojamento",
)


@lru_cache(maxsize=32)
def _ler_json(nome_arquivo: str) -> dict[str, Any]:
    caminho = DIR_DADOS_CC / nome_arquivo
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de dados C&C não encontrado: {caminho}")
    return json.loads(caminho.read_text(encoding="utf-8"))


def carregar_introducao() -> dict[str, Any]:
    return _ler_json("introducao.json")


def carregar_racas_tendencias() -> dict[str, Any]:
    return _ler_json("racas_tendencias.json")


def carregar_equipamentos() -> dict[str, Any]:
    return _ler_json("equipamentos.json")


def carregar_estrutura_ficha() -> dict[str, Any]:
    return _ler_json("estrutura_ficha.json")


@lru_cache(maxsize=1)
def listar_classes() -> tuple[dict[str, Any], ...]:
    classes: list[dict[str, Any]] = []
    for arq in ("classes01.json", "classes02.json", "classes03.json"):
        dados = _ler_json(arq)
        classes.extend(dados.get("classes", []))
    return tuple(classes)


@lru_cache(maxsize=1)
def mapa_classes() -> dict[str, dict[str, Any]]:
    return {c["id"]: c for c in listar_classes()}


def carregar_multiclasse() -> dict[str, Any]:
    return _ler_json("classes03.json").get("multiclasse_e_classe_e_meia", {})


@lru_cache(maxsize=1)
def listar_racas() -> tuple[dict[str, Any], ...]:
    return tuple(carregar_racas_tendencias().get("racas", []))


@lru_cache(maxsize=1)
def mapa_racas() -> dict[str, dict[str, Any]]:
    return {r["id"]: r for r in listar_racas()}


@lru_cache(maxsize=1)
def listar_disposicoes() -> tuple[dict[str, Any], ...]:
    disp = carregar_racas_tendencias().get("disposicoes", {})
    combinacoes = disp.get("combinacoes", [])
    if isinstance(combinacoes, dict):
        return tuple(combinacoes.values())
    return tuple(combinacoes)


@lru_cache(maxsize=1)
def mapa_disposicoes() -> dict[str, dict[str, Any]]:
    return {d["id"]: d for d in listar_disposicoes()}


def carregar_regras_magia() -> dict[str, Any]:
    return _ler_json("magias01.json").get("regras_gerais_magia", {})


def carregar_listas_magias() -> dict[str, dict[str, list[dict[str, Any]]]]:
    return _ler_json("magias01.json").get("listas_por_classe", {})


@lru_cache(maxsize=1)
def listar_magias() -> tuple[dict[str, Any], ...]:
    magias: list[dict[str, Any]] = []
    for arq in ("magias01.json", "magias02.json", "magias03.json"):
        magias.extend(_ler_json(arq).get("magias", []))
    return tuple(magias)


@lru_cache(maxsize=1)
def mapa_magias() -> dict[str, dict[str, Any]]:
    return {m["id"]: m for m in listar_magias()}


@lru_cache(maxsize=1)
def mapa_todos_equipamentos() -> dict[str, dict[str, Any]]:
    eq = carregar_equipamentos()
    resultado: dict[str, dict[str, Any]] = {}
    for cat in CATEGORIAS_EQUIPAMENTOS:
        for item in eq.get(cat, []):
            copia = dict(item)
            copia["categoria"] = cat
            resultado[item["id"]] = copia
    return resultado


def limpar_cache() -> None:
    _ler_json.cache_clear()
    listar_classes.cache_clear()
    mapa_classes.cache_clear()
    listar_racas.cache_clear()
    mapa_racas.cache_clear()
    listar_disposicoes.cache_clear()
    mapa_disposicoes.cache_clear()
    listar_magias.cache_clear()
    mapa_magias.cache_clear()
    mapa_todos_equipamentos.cache_clear()
