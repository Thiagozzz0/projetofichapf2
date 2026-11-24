"""Carregamento e resolução das Regras da Casa (Homebrew) em `dados_houserules/`."""

from __future__ import annotations

import json
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any

from .util import normalizar

DIR_HOUSERULES_PADRAO = Path(__file__).resolve().parent.parent / "dados_houserules"
ITENS_LEVES_OFICIAL = 10

_cache_lock = threading.Lock()
_cache_regras: dict[Path, dict[str, Any]] = {}


def carregar_regras_casa(diretorio: Path | str | None = None) -> dict[str, Any]:
    """Lê e indexa `catalogo_regras.json` e `perfis_regras.json` de `dados_houserules/`."""
    caminho = Path(diretorio).resolve() if diretorio else DIR_HOUSERULES_PADRAO
    with _cache_lock:
        if caminho not in _cache_regras:
            arq_catalogo = caminho / "catalogo_regras.json"
            arq_perfis = caminho / "perfis_regras.json"
            if not arq_catalogo.exists() or not arq_perfis.exists():
                _cache_regras[caminho] = {
                    "catalogo_regras": [],
                    "regras_por_id": {},
                    "perfis": [],
                    "perfis_por_id": {},
                    "padrao_modo": "oficial",
                }
            else:
                catalogo_raw = json.loads(arq_catalogo.read_text(encoding="utf-8"))
                perfis_raw = json.loads(arq_perfis.read_text(encoding="utf-8"))
                regras_lista = list(catalogo_raw.get("regras") or [])
                perfis_lista = list(perfis_raw.get("perfis") or [])
                _cache_regras[caminho] = {
                    "catalogo_regras": regras_lista,
                    "regras_por_id": {r["id"]: r for r in regras_lista},
                    "perfis": perfis_lista,
                    "perfis_por_id": {p["id"]: p for p in perfis_lista},
                    "padrao_modo": perfis_raw.get("padrao_modo", "oficial"),
                }
        return _cache_regras[caminho]


def listar_opcoes_regras_casa(diretorio: Path | str | None = None) -> dict[str, Any]:
    """Retorna perfis e regras disponíveis para API/UI sem expor mutações internas."""
    dados_rc = carregar_regras_casa(diretorio)
    return {
        "perfis": deepcopy(dados_rc["perfis"]),
        "regras": deepcopy(dados_rc["catalogo_regras"]),
        "padrao_modo": dados_rc["padrao_modo"],
        "oficial_itens_leves_por_volume": ITENS_LEVES_OFICIAL,
    }


def _combinar_override_item(destino: dict[str, Any], novo: dict[str, Any]) -> None:
    for chave, valor in novo.items():
        if chave == "substituir_conteudo":
            mapa_sub = dict(destino.get("substituir_conteudo") or {})
            mapa_sub.update(valor or {})
            destino["substituir_conteudo"] = mapa_sub
        else:
            destino[chave] = deepcopy(valor)


def resolver_configuracao_regras_casa(
    escolhas: dict[str, Any] | str | None = None,
    diretorio: Path | str | None = None,
) -> dict[str, Any]:
    """Resolve o modo ('oficial', 'regras_da_casa', 'personalizado') e flags ativas."""
    dados_rc = carregar_regras_casa(diretorio)
    regras_por_id = dados_rc["regras_por_id"]
    perfis_por_id = dados_rc["perfis_por_id"]

    if escolhas is None or (isinstance(escolhas, str) and not escolhas.strip()):
        modo = "oficial"
        req_regras: list[str] = []
        flags_map: dict[str, Any] = {}
    elif isinstance(escolhas, str):
        modo_norm = normalizar(escolhas)
        if modo_norm in ("", "oficial", "padrao", "livro"):
            modo = "oficial"
            req_regras = []
        elif modo_norm in ("regras_da_casa", "homebrew", "casa"):
            modo = "regras_da_casa"
            req_regras = list((perfis_por_id.get("regras_da_casa") or {}).get("regras_ativas") or [])
        elif modo_norm in perfis_por_id:
            modo = modo_norm
            req_regras = list(perfis_por_id[modo_norm].get("regras_ativas") or [])
        else:
            raise ValueError(f"Modo de regras da casa desconhecido: '{escolhas}'.")
        flags_map = {}
    elif isinstance(escolhas, dict):
        modo_bruto = normalizar(str(escolhas.get("modo") or escolhas.get("perfil") or "oficial"))
        if modo_bruto in ("", "oficial", "padrao", "livro"):
            modo = "oficial"
        elif modo_bruto in ("regras_da_casa", "homebrew", "casa"):
            modo = "regras_da_casa"
        elif modo_bruto in ("personalizado", "custom"):
            modo = "personalizado"
        elif modo_bruto in perfis_por_id:
            modo = modo_bruto
        else:
            raise ValueError(f"Modo de regras da casa desconhecido: '{escolhas.get('modo') or escolhas.get('perfil')}'.")

        bruto_ativas = escolhas.get("regras_ativas")
        bruto_flags = escolhas.get("flags")
        flags_map = dict(bruto_flags) if isinstance(bruto_flags, dict) else {}

        if modo == "oficial":
            req_regras = []
        elif modo in perfis_por_id and modo != "personalizado" and bruto_ativas is None and not flags_map:
            req_regras = list(perfis_por_id[modo].get("regras_ativas") or [])
        else:
            req_regras = []
            if bruto_ativas is not None:
                if not isinstance(bruto_ativas, list):
                    raise ValueError("Campo 'regras_ativas' deve ser uma lista de IDs de regras.")
                for rid in bruto_ativas:
                    rid_str = str(rid).strip()
                    if rid_str and rid_str not in req_regras:
                        req_regras.append(rid_str)
            for rid, ativo in flags_map.items():
                rid_str = str(rid).strip()
                if rid_str not in regras_por_id:
                    raise ValueError(f"Regra da casa desconhecida: '{rid_str}'.")
                if bool(ativo) and rid_str not in req_regras:
                    req_regras.append(rid_str)
                elif not bool(ativo) and rid_str in req_regras:
                    req_regras.remove(rid_str)
    else:
        raise ValueError("Campo 'escolhas_regras_casa' deve ser um objeto JSON ou string.")

    for rid in req_regras:
        if rid not in regras_por_id:
            raise ValueError(f"Regra da casa desconhecida: '{rid}'.")

    if modo == "personalizado" and not req_regras:
        # Personalizado sem nenhuma regra marcada equivale mecanicamente ao Oficial, mantendo o modo explícito.
        pass

    itens_leves_por_volume = ITENS_LEVES_OFICIAL
    overrides_itens: dict[str, dict[str, Any]] = {}
    resumos_ativos: list[str] = []

    for rid in req_regras:
        regra = regras_por_id[rid]
        resumos_ativos.append(regra.get("resumo_curto") or regra["nome"])
        params = regra.get("parametros") or {}
        if "itens_leves_por_volume" in params:
            itens_leves_por_volume = max(1, int(params["itens_leves_por_volume"]))
        for item_id, ov in (regra.get("overrides_itens") or {}).items():
            alvo = overrides_itens.setdefault(item_id, {})
            _combinar_override_item(alvo, ov)

    perfil_obj = perfis_por_id.get(modo) or {}
    return {
        "modo": modo,
        "nome_perfil": perfil_obj.get("nome") or modo,
        "ativa": bool(req_regras),
        "regras_ativas_ids": req_regras,
        "regras_ativas_resumo": resumos_ativos,
        "itens_leves_por_volume": itens_leves_por_volume,
        "overrides_itens": overrides_itens,
    }


def aplicar_override_item_casa(
    item: dict[str, Any],
    config_regras: dict[str, Any] | None,
) -> dict[str, Any]:
    """Retorna uma cópia do item com eventuais overrides da regra da casa aplicados (sem mutar BaseDados)."""
    if not item or not config_regras or not config_regras.get("ativa"):
        return item
    overrides_itens = config_regras.get("overrides_itens") or {}
    ov = overrides_itens.get(item.get("id"))
    if not ov:
        return item

    copia = deepcopy(item)
    for campo in ("nome", "quantidade_pacote", "volume", "volume_valor", "descricao"):
        if campo in ov:
            copia[campo] = ov[campo]

    substituicoes = ov.get("substituir_conteudo")
    if substituicoes and isinstance(copia.get("conteudo"), list):
        copia["conteudo"] = [substituicoes.get(c, c) for c in copia["conteudo"]]

    return copia
