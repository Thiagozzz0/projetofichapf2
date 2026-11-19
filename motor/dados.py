"""Carregamento, cache e indexação dos arquivos JSON de `dados/`."""

from __future__ import annotations

import json
import threading
from functools import cached_property
from pathlib import Path
from typing import Any

from .util import normalizar, slugify

DIR_DADOS_PADRAO = Path(__file__).resolve().parent.parent / "dados"

_cache_lock = threading.Lock()
_cache_instancias: dict[Path, "BaseDados"] = {}


def carregar_dados(diretorio: Path | str | None = None) -> "BaseDados":
    """Retorna uma instância única (cacheada) da base de dados para o diretório informado."""
    caminho = Path(diretorio).resolve() if diretorio else DIR_DADOS_PADRAO
    with _cache_lock:
        if caminho not in _cache_instancias:
            _cache_instancias[caminho] = BaseDados(caminho)
        return _cache_instancias[caminho]


class BaseDados:
    """Acesso somente-leitura e indexado a todas as regras convertidas em JSON."""

    def __init__(self, diretorio: Path):
        self.diretorio = diretorio
        self._brutos: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Leitura básica
    # ------------------------------------------------------------------
    def json(self, nome_arquivo: str) -> Any:
        if nome_arquivo not in self._brutos:
            with (self.diretorio / nome_arquivo).open("r", encoding="utf-8") as f:
                self._brutos[nome_arquivo] = json.load(f)
        return self._brutos[nome_arquivo]

    # ------------------------------------------------------------------
    # Ancestralidades, Heranças, Biografias
    # ------------------------------------------------------------------
    @cached_property
    def ancestralidades(self) -> dict[str, dict]:
        return {a["id"]: a for a in self.json("ancestralidades_biografias.json")["ancestralidades"]}

    @cached_property
    def talentos_mesticos(self) -> dict[str, list[dict]]:
        """Talentos de ancestralidade de meio-elfo e meio-orc (indexados pelo ID da herança)."""
        bruto = self.json("ancestralidades_biografias.json")["herancas_mesticas_talentos"]
        return {k: v for k, v in bruto.items() if isinstance(v, list)}

    @cached_property
    def biografias(self) -> dict[str, dict]:
        return {b["id"]: b for b in self.json("ancestralidades_biografias.json")["biografias"]["lista"]}

    def heranca(self, ancestralidade_id: str, heranca_id: str) -> dict | None:
        anc = self.ancestralidades.get(ancestralidade_id)
        if not anc:
            return None
        return next((h for h in anc["herancas"] if h["id"] == heranca_id), None)

    # ------------------------------------------------------------------
    # Classes, Conceitos
    # ------------------------------------------------------------------
    @cached_property
    def classes(self) -> dict[str, dict]:
        resultado: dict[str, dict] = {}
        for arquivo in ("classes01.json", "classes02.json", "classes03.json"):
            for c in self.json(arquivo)["classes"]:
                resultado[c["id"]] = c
        return resultado

    def subclasse(self, classe_id: str, subclasse_id: str) -> dict | None:
        classe = self.classes.get(classe_id)
        if not classe:
            return None
        return next((o for o in classe["subclasses"]["opcoes"] if o["id"] == subclasse_id), None)

    @cached_property
    def conceitos(self) -> dict[str, dict]:
        return {c["id"]: c for c in self.json("conceitos_subclasses.json")["conceitos"]}

    def conceitos_da_classe(self, classe_id: str) -> list[dict]:
        return [c for c in self.conceitos.values() if c["classe_id"] == classe_id]

    # ------------------------------------------------------------------
    # Perícias e Talentos
    # ------------------------------------------------------------------
    @cached_property
    def pericias(self) -> dict[str, dict]:
        return {p["id"]: p for p in self.json("pericias.json")["pericias"]}

    @cached_property
    def pericias_por_nome(self) -> dict[str, str]:
        return {normalizar(p["nome"]): p["id"] for p in self.pericias.values()}

    def pericia_id(self, nome: str | None) -> str | None:
        if not nome:
            return None
        chave = normalizar(nome)
        if chave in self.pericias_por_nome:
            return self.pericias_por_nome[chave]
        slug = slugify(nome)
        return slug if slug in self.pericias else None

    @cached_property
    def talentos_gerais_pericia(self) -> dict[str, dict]:
        return {t["id"]: t for t in self.json("talentos.json")["talentos"]}

    def resolver_talento_geral_pericia(self, nome: str | None) -> dict | None:
        """Resolve nomes como 'Certeza para Atletismo' ou 'Queda do Gato ou Salto Rápido' (primeira opção)."""
        if not nome:
            return None
        for candidato in self.opcoes_de_nome_talento(nome):
            talento = self.talentos_gerais_pericia.get(slugify(candidato))
            if talento:
                return talento
        return None

    @staticmethod
    def opcoes_de_nome_talento(nome: str) -> list[str]:
        """Separa 'A ou B' e remove complementos ('para X', '(X)')."""
        opcoes = []
        for parte in normalizar(nome).split(" ou "):
            parte = parte.split(" para ")[0]
            opcoes.append(parte)
        return opcoes

    # ------------------------------------------------------------------
    # Equipamentos
    # ------------------------------------------------------------------
    @cached_property
    def equipamentos(self) -> dict:
        return self.json("equipamentos.json")

    @cached_property
    def armaduras(self) -> dict[str, dict]:
        return {a["id"]: a for a in self.equipamentos["armaduras"]["itens"]}

    @cached_property
    def escudos(self) -> dict[str, dict]:
        return {s["id"]: s for s in self.equipamentos["escudos"]["itens"]}

    @cached_property
    def armas(self) -> dict[str, dict]:
        armas = {}
        for chave in ("corpo_a_corpo", "distancia"):
            for w in self.equipamentos["armas"][chave]:
                armas[w["id"]] = dict(w, tipo_ataque=chave)
        return armas

    @cached_property
    def ataques_desarmados(self) -> dict[str, dict]:
        return {w["id"]: w for w in self.equipamentos["armas"]["ataques_desarmados"]}

    @cached_property
    def municoes(self) -> list[dict]:
        return self.equipamentos["armas"]["municoes"]

    @cached_property
    def kits_de_classe(self) -> dict[str, dict]:
        return {k["id"]: k for k in self.equipamentos["kits_de_classe"]}

    @cached_property
    def itens_gerais(self) -> dict[str, dict]:
        """Equipamentos de aventura comuns + itens alquímicos com preço definido."""
        itens: dict[str, dict] = {}
        for item in self.equipamentos["equipamentos_aventura"]["comuns"]:
            itens[item["id"]] = item
        alquimicos = self.equipamentos.get("equipamentos_alquimicos")
        for item in _achatar_itens(alquimicos):
            if isinstance(item, dict) and "id" in item and item.get("preco_pc") is not None:
                itens.setdefault(item["id"], item)
        return itens

    def resolver_item(self, nome: str) -> dict | None:
        """Resolve um nome livre de item ('arpéu', '2 bainhas', 'símbolo religioso (madeira)')."""
        for candidato in (slugify(nome, remover_parenteses=False), slugify(nome)):
            for variante in (candidato, candidato.rstrip("s"), candidato.replace("s_", "_")):
                if variante in self.itens_gerais:
                    return self.itens_gerais[variante]
                if variante in self.armas:
                    return self.armas[variante]
        return None

    # ------------------------------------------------------------------
    # Magias
    # ------------------------------------------------------------------
    @cached_property
    def magias(self) -> dict[str, dict]:
        magias = {}
        for arquivo in ("magias01.json", "magias02.json"):
            for m in self.json(arquivo)["magias"]:
                magias[m["id"]] = m
        return magias

    @cached_property
    def magias_foco(self) -> dict[str, dict]:
        return {m["id"]: m for m in self.json("magias02.json")["magias_de_foco"]["lista"]}

    def resolver_magia(self, nome: str | None) -> dict | None:
        if not nome:
            return None
        return self.magias.get(slugify(nome))

    def resolver_magia_foco(self, nome: str | None) -> dict | None:
        if not nome:
            return None
        return self.magias_foco.get(slugify(nome))

    # ------------------------------------------------------------------
    # Ficha
    # ------------------------------------------------------------------
    @cached_property
    def estrutura_ficha(self) -> dict:
        return self.json("estrutura_ficha.json")


def _achatar_itens(no: Any) -> list:
    """Percorre estruturas aninhadas (dict/list) devolvendo todos os dicts com 'id'."""
    encontrados: list = []
    if isinstance(no, dict):
        if "id" in no and "nome" in no:
            encontrados.append(no)
        for valor in no.values():
            if isinstance(valor, (dict, list)):
                encontrados.extend(_achatar_itens(valor))
    elif isinstance(no, list):
        for valor in no:
            encontrados.extend(_achatar_itens(valor))
    return encontrados
