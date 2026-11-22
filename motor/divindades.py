"""Regras de Divindades, Fontes Divinas e Tendências para Pathfinder 2E."""

from __future__ import annotations

import random
from typing import Any

from .dados import BaseDados
from .util import normalizar


CLASSES_DIVINDADE_OBRIGATORIA = frozenset({"clerigo", "campeao"})


def determinar_tendencia(
    classe_id: str,
    subclasse_id: str,
    conceito: dict[str, Any] | None = None,
    divindade: dict[str, Any] | None = None,
) -> str:
    """Determina a tendência inicial considerando classe, causa/subclasse, conceito e divindade."""
    if conceito and conceito.get("tendencia_preferida"):
        tendencia = str(conceito["tendencia_preferida"])
    elif classe_id == "campeao":
        tendencia = {"paladino": "OB", "redentor": "NB", "libertador": "CB"}.get(subclasse_id, "NB")
    elif classe_id == "druida":
        tendencia = "N"
    else:
        tendencia = "NB"

    if classe_id == "clerigo" and divindade and tendencia not in divindade["tendencias_seguidores"]:
        if "NB" in divindade["tendencias_seguidores"]:
            tendencia = "NB"
        elif divindade["tendencia"] in divindade["tendencias_seguidores"]:
            tendencia = divindade["tendencia"]
        else:
            tendencia = divindade["tendencias_seguidores"][0]
    return tendencia


def fontes_divinas_aceitas_conceito(conceito: dict[str, Any]) -> list[str]:
    """Retorna as fontes divinas aceitas pelo conceito de Clérigo."""
    explicitas = conceito.get("fontes_divinas_aceitas")
    if explicitas:
        return list(explicitas)
    fonte_pref = conceito.get("fonte_divina_preferida") or (
        "ferimento" if ("ceifador" in conceito["id"] or "exaurir" in conceito["id"]) else "cura"
    )
    return [fonte_pref]


def divindades_compativeis_conceito(
    db: BaseDados,
    classe_id: str,
    conceito: dict[str, Any],
) -> list[str]:
    """Lista os IDs de divindades compatíveis com a classe e o conceito."""
    if classe_id == "campeao":
        candidatas = list(
            conceito.get("subclasses_oficiais_candidatas") or [conceito["subclasse_oficial_id"]]
        )
        tends_aceitas = {determinar_tendencia("campeao", sid) for sid in candidatas}
        return [
            d["id"]
            for d in db.divindades.values()
            if any(t in d["tendencias_seguidores"] for t in tends_aceitas)
        ]
    if classe_id == "clerigo":
        chaves_fonte = {
            "ferir" if f == "ferimento" else "curar"
            for f in fontes_divinas_aceitas_conceito(conceito)
        }
        return [
            d["id"]
            for d in db.divindades.values()
            if any(cf in d["fontes_divinas"] for cf in chaves_fonte)
        ]
    return list(db.divindades.keys())


def selecionar_divindade(
    db: BaseDados,
    classe_id: str,
    subclasse: dict[str, Any] | None,
    conceito: dict[str, Any],
    fonte_divina: str,
    rng: random.Random,
) -> dict[str, Any] | None:
    """Seleciona proceduralmente a divindade mais afinada para Clérigo e Campeão."""
    if classe_id not in CLASSES_DIVINDADE_OBRIGATORIA:
        return None

    candidatos = list(db.divindades.values())
    if classe_id == "campeao":
        tend_causa = determinar_tendencia("campeao", subclasse["id"] if subclasse else "")
        candidatos = [d for d in candidatos if tend_causa in d["tendencias_seguidores"]]
    else:
        fonte_chave = "ferir" if fonte_divina == "ferimento" else "curar"
        candidatos = [d for d in candidatos if fonte_chave in d["fontes_divinas"]]
        tend_pref = conceito.get("tendencia_preferida")
        if tend_pref:
            compativeis_tend = [d for d in candidatos if tend_pref in d["tendencias_seguidores"]]
            if compativeis_tend:
                candidatos = compativeis_tend

    if not candidatos:
        return None

    armas_conceito = set(
        conceito["equipamento_recomendado"]["armas_corpo_a_corpo_ids"]
        + conceito["equipamento_recomendado"]["armas_distancia_ids"]
    )
    per_pri = set(conceito.get("pericias_prioritarias", [])[:3])
    keywords = [normalizar(k) for k in conceito["talentos_recomendados"].get("tracos_ancestralidade_afinidade", [])]
    conj_rec = conceito.get("conjuracao_recomendada") or {}
    keywords.extend(normalizar(k) for k in conj_rec.get("tracos_prioritarios", []))

    avaliados: list[tuple[int, dict[str, Any]]] = []
    for d in candidatos:
        pts = 0
        if d["arma_favorecida_id"] in armas_conceito:
            pts += 16
        if any(p in per_pri for p in d["pericia_divina"]):
            pts += 12
        tend_pref = conceito.get("tendencia_preferida")
        if tend_pref and tend_pref in d["tendencias_seguidores"]:
            pts += 8
        texto_div = normalizar(f"{d['resumo']} {' '.join(d['dominios'])}")
        pts += sum(4 for kw in keywords if kw and kw in texto_div)
        if classe_id == "clerigo" and subclasse and subclasse["id"] == "capelao_da_guerra":
            if d["arma_favorecida_id"] in {"espada_longa", "martelo_de_guerra", "montante", "cimitarra", "maca"}:
                pts += 6
        avaliados.append((pts, d))

    avaliados.sort(key=lambda x: x[0], reverse=True)
    topo = avaliados[0][0]
    elegiveis = [d for pts, d in avaliados if pts >= topo - 4]
    return rng.choice(elegiveis) if len(elegiveis) > 1 else elegiveis[0]


def resolver_divindade_e_fonte(
    db: BaseDados,
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    conceito: dict[str, Any],
    div_req_norm: str,
    divindade_explicita: dict[str, Any] | None,
    rng: random.Random,
) -> tuple[dict[str, Any] | None, str]:
    """Resolve a divindade final e a Fonte Divina válida do personagem."""
    classe_id = classe["id"]
    fontes_aceitas = fontes_divinas_aceitas_conceito(conceito)
    fonte_divina = conceito.get("fonte_divina_preferida") or fontes_aceitas[0]

    if classe_id == "clerigo" and divindade_explicita is not None:
        chave_pref = "ferir" if fonte_divina == "ferimento" else "curar"
        if chave_pref not in divindade_explicita["fontes_divinas"]:
            alternativa = next(
                (
                    f
                    for f in fontes_aceitas
                    if ("ferir" if f == "ferimento" else "curar") in divindade_explicita["fontes_divinas"]
                ),
                None,
            )
            if alternativa is None:
                raise ValueError(
                    f"A divindade '{divindade_explicita['nome']}' não concede Fonte Divina "
                    f"compatível com o conceito '{conceito['nome']}'."
                )
            fonte_divina = alternativa

    if divindade_explicita is not None:
        return divindade_explicita, fonte_divina

    if div_req_norm in ("aleatoria", "aleatorio", "random"):
        if classe_id == "campeao":
            tend_causa = determinar_tendencia("campeao", subclasse["id"] if subclasse else "")
            compat = [d for d in db.divindades.values() if tend_causa in d["tendencias_seguidores"]]
            return (rng.choice(compat) if compat else None), fonte_divina
        if classe_id == "clerigo":
            chaves_ok = {"ferir" if f == "ferimento" else "curar" for f in fontes_aceitas}
            compat = [
                d for d in db.divindades.values() if any(cf in d["fontes_divinas"] for cf in chaves_ok)
            ]
            divindade = rng.choice(compat) if compat else None
            if divindade:
                chave_pref = "ferir" if fonte_divina == "ferimento" else "curar"
                if chave_pref not in divindade["fontes_divinas"]:
                    fonte_divina = next(
                        f
                        for f in fontes_aceitas
                        if ("ferir" if f == "ferimento" else "curar") in divindade["fontes_divinas"]
                    )
            return divindade, fonte_divina
        return rng.choice(list(db.divindades.values())), fonte_divina

    if classe_id in CLASSES_DIVINDADE_OBRIGATORIA:
        return selecionar_divindade(db, classe_id, subclasse, conceito, fonte_divina, rng), fonte_divina

    return None, fonte_divina


def montar_resumo_divindade_ficha(
    divindade: dict[str, Any] | None,
    classe_id: str,
    fonte_divina: str,
) -> tuple[str, dict[str, Any] | None]:
    """Formata o texto curto do cabeçalho e o dicionário de detalhes da divindade."""
    if not divindade:
        return "", None
    divindade_texto = f"{divindade['nome']} ({divindade['tendencia']})"
    divindade_detalhes = {
        "id": divindade["id"],
        "nome": divindade["nome"],
        "tendencia": divindade["tendencia"],
        "arma_favorecida_id": divindade["arma_favorecida_id"],
        "arma_favorecida_nome": divindade["arma_favorecida_nome"],
        "pericia_divina": list(divindade["pericia_divina"]),
        "dominios": list(divindade["dominios"]),
        "editos": divindade["editos"],
        "anatema": divindade["anatema"],
        "fonte_divina": fonte_divina if classe_id == "clerigo" else None,
    }
    return divindade_texto, divindade_detalhes
