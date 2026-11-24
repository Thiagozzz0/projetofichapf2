"""Carregamento e resolução das Regras da Casa (Homebrew) em `dados_houserules/`."""

from __future__ import annotations

import hmac
import json
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any

from .util import normalizar

DIR_HOUSERULES_PADRAO = Path(__file__).resolve().parent.parent / "dados_houserules"
ARQUIVO_ACESSO_MESTRE = "acesso_mestre.json"
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
                    "padrao_modo": "regras_da_casa",
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
                    "padrao_modo": perfis_raw.get("padrao_modo", "regras_da_casa"),
                }
        return _cache_regras[caminho]


def carregar_acesso_mestre(diretorio: Path | str | None = None) -> dict[str, Any]:
    """Lê o arquivo de controle `acesso_mestre.json` diretamente do disco."""
    caminho = Path(diretorio).resolve() if diretorio else DIR_HOUSERULES_PADRAO
    arq_acesso = caminho / ARQUIVO_ACESSO_MESTRE
    padrao = {
        "versao": 1,
        "padrao_modo": "regras_da_casa",
        "exigir_senha_a_cada_troca": True,
        "senha": "",
    }
    if not arq_acesso.exists():
        return padrao
    try:
        dados = json.loads(arq_acesso.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return padrao
    if not isinstance(dados, dict):
        return padrao
    return {
        "versao": dados.get("versao", 1),
        "padrao_modo": str(dados.get("padrao_modo") or "regras_da_casa"),
        "exigir_senha_a_cada_troca": bool(dados.get("exigir_senha_a_cada_troca", True)),
        "senha": str(dados.get("senha") or ""),
    }


def validar_senha_regras_casa(
    senha_informada: str | None,
    diretorio: Path | str | None = None,
) -> bool:
    """Valida a senha do mestre contra `dados_houserules/acesso_mestre.json`."""
    acesso = carregar_acesso_mestre(diretorio)
    senha_esperada = str(acesso.get("senha") or "").strip()
    tentativa = str(senha_informada or "").strip()
    if not senha_esperada or not tentativa:
        return False
    return hmac.compare_digest(tentativa, senha_esperada)


def listar_opcoes_regras_casa(diretorio: Path | str | None = None) -> dict[str, Any]:
    """Retorna perfis e regras disponíveis para API/UI sem expor mutações internas."""
    dados_rc = carregar_regras_casa(diretorio)
    acesso = carregar_acesso_mestre(diretorio)
    return {
        "perfis": deepcopy(dados_rc["perfis"]),
        "regras": deepcopy(dados_rc["catalogo_regras"]),
        "padrao_modo": acesso.get("padrao_modo") or dados_rc["padrao_modo"],
        "oficial_itens_leves_por_volume": ITENS_LEVES_OFICIAL,
        "protegido_por_senha": True,
        "exigir_senha_a_cada_troca": bool(acesso.get("exigir_senha_a_cada_troca", True)),
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
    """Resolve o modo ('oficial' ou 'regras_da_casa') e flags ativas."""
    dados_rc = carregar_regras_casa(diretorio)
    regras_por_id = dados_rc["regras_por_id"]
    perfis_por_id = dados_rc["perfis_por_id"]

    if escolhas is None or (isinstance(escolhas, str) and not escolhas.strip()):
        modo = "oficial"
    elif isinstance(escolhas, str):
        modo_norm = normalizar(escolhas)
        if modo_norm in ("", "oficial", "padrao", "livro", "originais", "regras_originais"):
            modo = "oficial"
        elif modo_norm in ("regras_da_casa", "homebrew", "casa"):
            modo = "regras_da_casa"
        else:
            raise ValueError(f"Modo de regras da casa desconhecido: '{escolhas}'.")
    elif isinstance(escolhas, dict):
        modo_bruto = normalizar(str(escolhas.get("modo") or escolhas.get("perfil") or "oficial"))
        if modo_bruto in ("", "oficial", "padrao", "livro", "originais", "regras_originais"):
            modo = "oficial"
        elif modo_bruto in ("regras_da_casa", "homebrew", "casa"):
            modo = "regras_da_casa"
        else:
            raise ValueError(
                f"Modo de regras da casa desconhecido: '{escolhas.get('modo') or escolhas.get('perfil')}'."
            )
    else:
        raise ValueError("Campo 'escolhas_regras_casa' deve ser um objeto JSON ou string.")

    req_regras = (
        list((perfis_por_id.get("regras_da_casa") or {}).get("regras_ativas") or [])
        if modo == "regras_da_casa"
        else []
    )

    for rid in req_regras:
        if rid not in regras_por_id:
            raise ValueError(f"Regra da casa desconhecida: '{rid}'.")

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
