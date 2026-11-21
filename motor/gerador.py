"""Orquestrador principal de geração procedural de fichas PF2E (1º nível)."""

from __future__ import annotations

import random
from copy import deepcopy
from typing import Any

from .biografia_pericias import calcular_idiomas, calcular_pericias, selecionar_biografia
from .combate_matematica import calcular_matematica_final
from .companheiros import gerar_companheiro_ou_familiar
from .dados import BaseDados, carregar_dados
from .equipamentos import calcular_proficiencias_combate, comprar_equipamentos
from .magias import gerar_conjuracao, preencher_bloco_conjuracao_ficha
from .regras_atributos import calcular_atributos
from .talentos import selecionar_talentos
from .util import formatar_preco, normalizar


class ErroValidacao(ValueError):
    """Erro levantado quando parâmetros de entrada da geração são inválidos."""


CLASSES_DIVINDADE_OBRIGATORIA = frozenset({"clerigo", "campeao"})


_NOMES_HUMANOS_PADRAO = [
    "Alden", "Beatriz", "Caio", "Darian", "Elena", "Ezren",
    "Helena", "Henrique", "Kyra", "Lorian", "Rafael", "Seoni",
    "Teresa", "Valeros",
]


def _sortear_nome_personagem(ancestralidade: dict[str, Any], rng: random.Random) -> str:
    exemplos = [
        n for n in ancestralidade.get("exemplos_nomes", [])
        if n and "variados" not in normalizar(n) and len(n) <= 30
    ]
    pool = exemplos or _NOMES_HUMANOS_PADRAO
    return rng.choice(pool)


def _determinar_tendencia(
    classe_id: str,
    subclasse_id: str,
    conceito: dict[str, Any] | None = None,
) -> str:
    if conceito and conceito.get("tendencia_preferida"):
        return str(conceito["tendencia_preferida"])
    if classe_id == "campeao":
        return {"paladino": "OB", "redentor": "NB", "libertador": "CB"}.get(subclasse_id, "NB")
    if classe_id == "druida":
        return "N"
    return "NB"


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
        tends_aceitas = {_determinar_tendencia("campeao", sid) for sid in candidatas}
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


def _selecionar_subclasse_procedural(
    db: BaseDados,
    classe_id: str,
    conceito: dict[str, Any],
    rng: random.Random,
    divindade_explicita: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Resolve a subclasse oficial a partir do conceito (exata ou dentre candidatas)."""
    candidatas = list(conceito.get("subclasses_oficiais_candidatas") or [])
    if not candidatas and conceito.get("subclasse_oficial_id"):
        candidatas = [conceito["subclasse_oficial_id"]]
    validas = [s for sid in candidatas if (s := db.subclasse(classe_id, sid)) is not None]
    if not validas:
        return db.subclasse(classe_id, conceito.get("subclasse_oficial_id", ""))
    if classe_id == "campeao" and divindade_explicita is not None:
        tends_div = set(divindade_explicita["tendencias_seguidores"])
        compativeis = [s for s in validas if _determinar_tendencia("campeao", s["id"]) in tends_div]
        if not compativeis:
            tends_req = ", ".join(
                sorted({_determinar_tendencia("campeao", s["id"]) for s in validas})
            )
            raise ErroValidacao(
                f"A divindade '{divindade_explicita['nome']}' não aceita seguidores de tendência "
                f"'{tends_req}' (exigida pelo conceito '{conceito['nome']}')."
            )
        validas = compativeis
    return validas[0] if len(validas) == 1 else rng.choice(validas)


def _resolver_tese_arcana(classe: dict[str, Any], tese_id: str | None) -> dict[str, Any] | None:
    if not tese_id:
        return None
    for car in classe.get("caracteristicas_de_classe", []):
        if car.get("id") == "tese_arcana":
            opcoes = car.get("detalhes", {}).get("opcoes", [])
            for op in opcoes:
                if op.get("id") == tese_id:
                    return op
    return None


def _selecionar_divindade(
    db: BaseDados,
    classe_id: str,
    subclasse: dict[str, Any] | None,
    conceito: dict[str, Any],
    fonte_divina: str,
    divindade_id: str | None,
    rng: random.Random,
) -> dict[str, Any] | None:
    """Resolve a divindade real do personagem (manual ou procedural para Clérigo e Campeão)."""
    if divindade_id and divindade_id != "procedural":
        div = db.divindades.get(divindade_id)
        if not div:
            raise ErroValidacao(f"Divindade desconhecida: '{divindade_id}'.")
        if classe_id == "campeao":
            tend_causa = _determinar_tendencia("campeao", subclasse["id"] if subclasse else "")
            if tend_causa not in div["tendencias_seguidores"]:
                raise ErroValidacao(
                    f"A divindade '{div['nome']}' não aceita seguidores de tendência '{tend_causa}' "
                    f"(exigida pela Causa '{subclasse['nome'] if subclasse else ''}')."
                )
        elif classe_id == "clerigo":
            fonte_chave = "ferir" if fonte_divina == "ferimento" else "curar"
            if fonte_chave not in div["fontes_divinas"]:
                raise ErroValidacao(
                    f"A divindade '{div['nome']}' não concede Fonte Divina '{fonte_chave}'."
                )
        return div

    if classe_id not in ("campeao", "clerigo"):
        return None

    candidatos = list(db.divindades.values())
    if classe_id == "campeao":
        tend_causa = _determinar_tendencia("campeao", subclasse["id"] if subclasse else "")
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


def _preencher_pagina_talentos(
    ficha: dict[str, Any],
    ancestralidade: dict[str, Any],
    heranca: dict[str, Any],
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    talentos_res: dict[str, Any],
    tese_arcana: dict[str, Any] | None = None,
) -> None:
    hab_tal = ficha["habilidades_e_talentos"]

    # Ancestralidade (slots 0..2 de 7)
    especiais = ancestralidade.get("habilidades_especiais", [])
    if especiais:
        hab_tal["ancestralidade"][0]["nome"] = "; ".join(e["nome"] for e in especiais)
        hab_tal["ancestralidade"][0]["origem_regra"] = f"Ancestralidade ({ancestralidade['nome']})"
        hab_tal["ancestralidade"][0]["resumo"] = " ".join(e["descricao"] for e in especiais)
    else:
        hab_tal["ancestralidade"][0]["nome"] = "Versatilidade Humana"
        hab_tal["ancestralidade"][0]["origem_regra"] = f"Ancestralidade ({ancestralidade['nome']})"
        hab_tal["ancestralidade"][0]["resumo"] = "Sem habilidade especial fixa além da herança."

    hab_tal["ancestralidade"][1]["nome"] = heranca["nome"]
    hab_tal["ancestralidade"][1]["origem_regra"] = f"Herança ({ancestralidade['nome']})"
    hab_tal["ancestralidade"][1]["resumo"] = heranca["descricao"]

    t_anc = talentos_res["talento_ancestral"]
    hab_tal["ancestralidade"][2]["nome"] = t_anc["nome"]
    hab_tal["ancestralidade"][2]["origem_regra"] = f"Talento de Ancestralidade ({ancestralidade['nome']} N1)"
    hab_tal["ancestralidade"][2]["resumo"] = t_anc["descricao"]

    # Perícia — slot 0 (BIOGRAFIA)
    tb = talentos_res["talento_biografia"]
    hab_tal["pericia"][0]["nome"] = tb["nome"]
    hab_tal["pericia"][0]["origem_regra"] = tb["origem"]
    hab_tal["pericia"][0]["resumo"] = tb["resumo"]

    # Classe — slots 0 e 1 (CARACTERÍSTICA 1º) e slot 2 (TALENTO 1º)
    caracts = talentos_res["caracteristicas_classe_n1"]
    if subclasse and tese_arcana:
        hab_tal["classe"][0]["nome"] = (
            f"{classe['subclasses']['nome_tipo']}: {subclasse['nome']} | Tese: {tese_arcana['nome']}"
        )
        hab_tal["classe"][0]["origem_regra"] = f"Classe ({classe['nome']})"
        hab_tal["classe"][0]["resumo"] = (
            f"{subclasse.get('descricao', '')} | Tese Arcana ({tese_arcana['nome']}): "
            f"{tese_arcana.get('descricao', '')}"
        ).strip()
    elif subclasse:
        hab_tal["classe"][0]["nome"] = f"{classe['subclasses']['nome_tipo']}: {subclasse['nome']}"
        hab_tal["classe"][0]["origem_regra"] = f"Classe ({classe['nome']})"
        hab_tal["classe"][0]["resumo"] = subclasse.get("descricao", "")
    elif caracts:
        hab_tal["classe"][0]["nome"] = caracts[0]["nome"]
        hab_tal["classe"][0]["origem_regra"] = f"Classe ({classe['nome']})"
        hab_tal["classe"][0]["resumo"] = caracts[0].get("descricao", "")

    nomes_caract = [c["nome"] for c in caracts]
    if talentos_res["efeitos"].get("bloqueio_com_escudo") and "Bloqueio com Escudo" not in nomes_caract:
        nomes_caract.append("Bloqueio com Escudo")
    if nomes_caract:
        hab_tal["classe"][1]["nome"] = "; ".join(nomes_caract)
        hab_tal["classe"][1]["origem_regra"] = f"Características de 1º Nível ({classe['nome']})"
        hab_tal["classe"][1]["resumo"] = " | ".join(
            f"{c['nome']}: {c.get('descricao', '')[:160]}" for c in caracts[:3]
        )

    talentos_classe = talentos_res["talentos_classe"]
    bonus_extras = list(talentos_res["talentos_bonus"])

    if talentos_classe:
        t0 = talentos_classe[0]
        hab_tal["classe"][2]["nome"] = t0["nome"]
        hab_tal["classe"][2]["origem_regra"] = t0["origem"]
        hab_tal["classe"][2]["resumo"] = t0["descricao"]
        for t_extra in talentos_classe[1:]:
            bonus_extras.append(
                {
                    "nome": t_extra["nome"],
                    "categoria": "classe",
                    "origem_regra": t_extra["origem"],
                    "pagina": None,
                    "resumo": t_extra["descricao"],
                }
            )
    else:
        hab_tal["classe"][2]["nome"] = "—"
        hab_tal["classe"][2]["origem_regra"] = f"{classe['nome']} não escolhe talento livre no 1º nível"
        hab_tal["classe"][2]["resumo"] = ""

    # Bônus — até 2 slots oficiais; eventuais extras vão para o 1º slot livre da categoria (sem descarte)
    mapa_cat_slots = {
        "pericia": hab_tal["pericia"],
        "geral": hab_tal["gerais"],
        "classe": hab_tal["classe"],
    }
    for idx, b in enumerate(bonus_extras):
        if idx < len(hab_tal["bonus"]):
            destino = hab_tal["bonus"][idx]
            origem_txt = b["origem_regra"]
        else:
            lista_cat = mapa_cat_slots.get(b.get("categoria", "classe"), hab_tal["classe"])
            destino = next((s for s in lista_cat if not (s.get("nome") or "").strip()), None)
            if destino is None:
                continue
            origem_txt = f"{b['origem_regra']} (Bônus 1º Nível)"
        destino["nome"] = b["nome"]
        destino["origem_regra"] = origem_txt
        destino["pagina"] = b.get("pagina")
        destino["resumo"] = b["resumo"]


def listar_opcoes_criacao(dados: BaseDados | None = None) -> dict[str, Any]:
    """Retorna listas resumidas de ancestralidades, biografias, classes e conceitos para a API/UI."""
    db = dados or carregar_dados()

    ancestralidades = [
        {
            "id": a["id"],
            "nome": a["nome"],
            "pontos_vida": a["pontos_vida"],
            "tamanho": a["tamanho"],
            "velocidade_m": a["velocidade_m"],
            "melhorias_atributo": a["melhorias_atributo"],
            "defeito_atributo": a.get("defeito_atributo"),
            "herancas": [{"id": h["id"], "nome": h["nome"], "descricao": h["descricao"]} for h in a["herancas"]],
        }
        for a in db.ancestralidades.values()
    ]

    biografias = [
        {
            "id": b["id"],
            "nome": b["nome"],
            "melhorias_atributo_opcoes": b["melhorias_atributo_opcoes"],
            "pericia_treinada_opcoes": b["pericia_treinada_opcoes"],
            "saber_treinado": b["saber_treinado"],
            "talento_pericia": b["talento_pericia"],
        }
        for b in db.biografias.values()
    ]

    classes = [
        {
            "id": c["id"],
            "nome": c["nome"],
            "pontos_de_vida_por_nivel": c["pontos_de_vida_por_nivel"],
            "atributo_chave": c["atributo_chave"]["opcoes"],
            "divindade_obrigatoria": c["id"] in CLASSES_DIVINDADE_OBRIGATORIA,
            "conceitos": [
                {
                    "id": con["id"],
                    "nome": con["nome"],
                    "titulo_completo": con["titulo_completo"],
                    "subclasse_oficial_id": con["subclasse_oficial_id"],
                    "subclasse_oficial_nome": con["subclasse_oficial_nome"],
                    "subclasses_oficiais_candidatas": con.get(
                        "subclasses_oficiais_candidatas", [con["subclasse_oficial_id"]]
                    ),
                    "subclasses_oficiais_nomes": con.get(
                        "subclasses_oficiais_nomes", [con["subclasse_oficial_nome"]]
                    ),
                    "resumo_proposta": con["resumo_proposta"],
                    "sinergia_mecanica": con.get("sinergia_mecanica", ""),
                    "divindades_compativeis_ids": divindades_compativeis_conceito(db, c["id"], con),
                }
                for con in db.conceitos_da_classe(c["id"])
            ],
        }
        for c in db.classes.values()
    ]

    divindades = [
        {
            "id": d["id"],
            "nome": d["nome"],
            "tendencia": d["tendencia"],
            "tendencias_seguidores": d["tendencias_seguidores"],
            "fontes_divinas": d["fontes_divinas"],
            "arma_favorecida_nome": d["arma_favorecida_nome"],
            "pericia_divina": d["pericia_divina"],
            "dominios": d["dominios"],
        }
        for d in db.divindades.values()
    ]

    return {
        "ancestralidades": ancestralidades,
        "biografias": biografias,
        "classes": classes,
        "divindades": divindades,
        "total_conceitos": len(db.conceitos),
    }


def gerar_personagem(
    ancestralidade_id: str,
    heranca_id: str,
    classe_id: str,
    conceito_id: str,
    biografia_id: str | None = None,
    divindade_id: str | None = None,
    nome_personagem: str | None = None,
    nome_jogador: str = "",
    nivel: int = 1,
    seed: int | str | None = None,
    dados: BaseDados | None = None,
) -> dict[str, Any]:
    """Gera uma ficha completa e válida de Pathfinder 2E guiada pelo conceito escolhido."""
    db = dados or carregar_dados()

    # ------------------------------------------------------------------
    # 1. Validação rigorosa das entradas
    # ------------------------------------------------------------------
    if nivel != 1:
        raise ErroValidacao("Esta versão do motor gera personagens de 1º nível (nivel=1).")

    ancestralidade = db.ancestralidades.get(ancestralidade_id)
    if not ancestralidade:
        raise ErroValidacao(f"Ancestralidade desconhecida: '{ancestralidade_id}'.")

    heranca = db.heranca(ancestralidade_id, heranca_id)
    if not heranca:
        raise ErroValidacao(f"Herança '{heranca_id}' não pertence à ancestralidade '{ancestralidade_id}'.")

    classe = db.classes.get(classe_id)
    if not classe:
        raise ErroValidacao(f"Classe desconhecida: '{classe_id}'.")

    conceito = db.conceitos.get(conceito_id)
    if not conceito:
        raise ErroValidacao(f"Conceito desconhecido: '{conceito_id}'.")
    if conceito["classe_id"] != classe_id:
        raise ErroValidacao(
            f"O conceito '{conceito_id}' pertence à classe '{conceito['classe_id']}', não a '{classe_id}'."
        )

    # Seed opcional: se não informada, cria uma seed aleatória rastreável
    if seed is None or str(seed).strip() == "":
        seed_usada: int | str = random.SystemRandom().randint(1, 999_999_999)
    else:
        seed_str = str(seed).strip()
        seed_usada = int(seed_str) if seed_str.isdigit() else seed_str
    rng = random.Random(seed_usada)

    div_req = None if divindade_id is None else str(divindade_id).strip()
    if classe_id in CLASSES_DIVINDADE_OBRIGATORIA and div_req in ("", "nenhuma"):
        raise ErroValidacao(f"A classe {classe['nome']} exige obrigatoriamente a seleção de uma divindade.")

    divindade_explicita: dict[str, Any] | None = None
    if div_req not in (None, "", "nenhuma", "procedural", "aleatoria"):
        divindade_explicita = db.divindades.get(div_req)
        if not divindade_explicita:
            raise ErroValidacao(f"Divindade desconhecida: '{div_req}'.")

    subclasse = _selecionar_subclasse_procedural(
        db, classe_id, conceito, rng, divindade_explicita=divindade_explicita
    )
    tese_arcana = _resolver_tese_arcana(classe, conceito.get("tese_arcana_id")) if classe_id == "mago" else None

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
                raise ErroValidacao(
                    f"A divindade '{divindade_explicita['nome']}' não concede Fonte Divina "
                    f"compatível com o conceito '{conceito['nome']}'."
                )
            fonte_divina = alternativa

    if divindade_explicita is not None:
        divindade = divindade_explicita
    elif div_req == "aleatoria":
        if classe_id == "campeao":
            tend_causa = _determinar_tendencia("campeao", subclasse["id"] if subclasse else "")
            compat = [d for d in db.divindades.values() if tend_causa in d["tendencias_seguidores"]]
            divindade = rng.choice(compat) if compat else None
        elif classe_id == "clerigo":
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
        else:
            divindade = rng.choice(list(db.divindades.values()))
    elif classe_id in CLASSES_DIVINDADE_OBRIGATORIA:
        divindade = _selecionar_divindade(db, classe_id, subclasse, conceito, fonte_divina, None, rng)
    else:
        divindade = None

    # ------------------------------------------------------------------
    # 2. Seleção de Biografia (Manual ou Procedural) + Atributos (ABCD)
    # ------------------------------------------------------------------
    try:
        biografia, biografia_procedural = selecionar_biografia(
            db, conceito, ancestralidade, biografia_id=biografia_id, rng=rng
        )
    except ValueError as exc:
        raise ErroValidacao(str(exc)) from exc

    atributos_res = calcular_atributos(ancestralidade, biografia, classe, subclasse, conceito, nivel=nivel)
    mod_int = atributos_res["modificadores"]["int"]
    mod_for = atributos_res["modificadores"]["for"]

    # ------------------------------------------------------------------
    # 3. Perícias base -> Talentos -> Perícias extras (ex.: Perícia Natural)
    # ------------------------------------------------------------------
    pericias_base = calcular_pericias(
        db,
        ancestralidade,
        heranca,
        biografia,
        classe,
        subclasse,
        conceito,
        mod_int,
        extras_pericias=0,
        divindade=divindade,
        rng=rng,
    )
    tendencia = _determinar_tendencia(classe_id, subclasse["id"] if subclasse else "", conceito=conceito)
    if classe_id == "clerigo" and divindade and tendencia not in divindade["tendencias_seguidores"]:
        if "NB" in divindade["tendencias_seguidores"]:
            tendencia = "NB"
        elif divindade["tendencia"] in divindade["tendencias_seguidores"]:
            tendencia = divindade["tendencia"]
        else:
            tendencia = divindade["tendencias_seguidores"][0]

    talentos_res = selecionar_talentos(
        db,
        ancestralidade,
        heranca,
        biografia,
        classe,
        subclasse,
        conceito,
        graus_pericias=pericias_base["graus"],
        pericia_bio_id=pericias_base["pericia_biografia_id"],
        tendencia=tendencia,
        fonte_divina=fonte_divina,
        tese_arcana_id=tese_arcana["id"] if tese_arcana else None,
        divindade=divindade,
        rng=rng,
    )

    extras_per = talentos_res["efeitos"]["extras_pericias"]
    if extras_per > 0:
        # Recalcula com determinismo preservado a partir da mesma derivação de RNG
        pericias_res = calcular_pericias(
            db,
            ancestralidade,
            heranca,
            biografia,
            classe,
            subclasse,
            conceito,
            mod_int,
            extras_pericias=extras_per,
            divindade=divindade,
            rng=random.Random(f"{seed_usada}:pericias"),
        )
    else:
        pericias_res = pericias_base

    idiomas = calcular_idiomas(db, ancestralidade, heranca, classe, mod_int, rng=rng)

    # ------------------------------------------------------------------
    # 4. Equipamentos (15 po), Volume e Conjuração
    # ------------------------------------------------------------------
    profs_combate = calcular_proficiencias_combate(
        classe,
        subclasse,
        talentos_classe_ids=talentos_res["talentos_classe_ids"],
        divindade=divindade,
    )
    equip_res = comprar_equipamentos(
        db,
        ancestralidade,
        classe,
        conceito,
        mod_for,
        profs_combate,
        mod_int=mod_int,
        subclasse=subclasse,
        efeitos_talentos=talentos_res["efeitos"],
        divindade=divindade,
    )
    magias_res = gerar_conjuracao(
        db,
        heranca,
        classe,
        subclasse,
        conceito,
        atributos_res["modificadores"],
        talentos_res["talentos_classe_ids"],
        nivel=nivel,
        fonte_divina=fonte_divina,
        divindade=divindade,
        rng=rng,
    )

    # ------------------------------------------------------------------
    # 5. Montagem fiel ao contrato `modelo_ficha_vazia`
    # ------------------------------------------------------------------
    ficha = deepcopy(db.estrutura_ficha["modelo_ficha_vazia"])

    nome_final = (nome_personagem or "").strip() or _sortear_nome_personagem(ancestralidade, rng)
    tracos: list[str] = []
    for t in (
        list(ancestralidade.get("tracos", []))
        + list(heranca.get("tracos_adicionais", []) or [])
        + [classe["nome"]]
    ):
        if t and normalizar(t) not in {normalizar(x) for x in tracos}:
            tracos.append(t)

    divindade_texto = ""
    divindade_detalhes = None
    if divindade:
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

    ficha["cabecalho"] = {
        "nome_personagem": nome_final,
        "nome_jogador": nome_jogador.strip(),
        "pontos_experiencia": 0,
        "ancestralidade_e_heranca": f"{ancestralidade['nome']} ({heranca['nome']})",
        "biografia": biografia["nome"],
        "classe": f"{classe['nome']} — {conceito['nome']}",
        "tamanho": ancestralidade["tamanho"],
        "tendencia": tendencia,
        "tracos": tracos,
        "divindade": divindade_texto,
        "nivel": nivel,
        "pontos_heroismo": 1,
    }

    for aid, val in atributos_res["valores"].items():
        ficha["atributos"][aid] = {
            "valor": val,
            "modificador": atributos_res["modificadores"][aid],
        }

    _preencher_pagina_talentos(
        ficha, ancestralidade, heranca, classe, subclasse, talentos_res, tese_arcana=tese_arcana
    )
    preencher_bloco_conjuracao_ficha(ficha["conjuracao"], magias_res)
    notas_combate = calcular_matematica_final(
        ficha=ficha,
        dados=db,
        ancestralidade=ancestralidade,
        heranca=heranca,
        classe=classe,
        subclasse=subclasse,
        atributos_res=atributos_res,
        pericias_res=pericias_res,
        idiomas=idiomas,
        talentos_res=talentos_res,
        profs_combate=profs_combate,
        equip_res=equip_res,
        nivel=nivel,
        tese_arcana=tese_arcana,
        divindade=divindade,
    )

    companheiro_ou_familiar = gerar_companheiro_ou_familiar(
        dados=db,
        classe=classe,
        subclasse=subclasse,
        conceito=conceito,
        talentos_classe_ids=talentos_res["talentos_classe_ids"],
        ficha_mestre=ficha,
        modificadores_mestre=atributos_res["modificadores"],
        tese_arcana_id=tese_arcana["id"] if tese_arcana else None,
        nivel=nivel,
        rng=rng,
    )

    sub_nome_final = subclasse["nome"] if subclasse else conceito["subclasse_oficial_nome"]
    tese_nota = f" | Tese: {tese_arcana['nome']}" if tese_arcana else ""
    ficha["perfil_e_campanha"]["dados_biograficos"]["idade"] = str(ancestralidade.get("maturidade_anos", 20))
    ficha["perfil_e_campanha"]["anotacoes_campanha"]["anotacoes"] = (
        f"Conceito: {conceito['titulo_completo']} (Subclasse PF2E: {sub_nome_final}{tese_nota}). "
        f"{conceito['resumo_proposta']} "
        f"Sinergia: {conceito.get('sinergia_mecanica', '')} "
        f"Biografia: {biografia['descricao']}"
    ).strip()

    return {
        "meta_geracao": {
            "seed": seed_usada,
            "nivel": nivel,
            "biografia_procedural": biografia_procedural,
            "ancestralidade_id": ancestralidade_id,
            "heranca_id": heranca_id,
            "biografia_id": biografia["id"],
            "classe_id": classe_id,
            "conceito_id": conceito_id,
            "subclasse_oficial_id": subclasse["id"] if subclasse else None,
            "subclasse_oficial_nome": sub_nome_final,
            "tese_arcana_id": tese_arcana["id"] if tese_arcana else None,
            "tese_arcana_nome": tese_arcana["nome"] if tese_arcana else None,
            "divindade_id": divindade["id"] if divindade else None,
            "divindade_obrigatoria": classe_id in CLASSES_DIVINDADE_OBRIGATORIA,
            "divindade_procedural": (div_req in (None, "procedural", "aleatoria")) and (divindade is not None),
            "divindade_detalhes": divindade_detalhes,
            "companheiro_ou_familiar": companheiro_ou_familiar,
            "limite_morrendo": notas_combate["limite_morrendo"],
            "cd_recuperacao_base": notas_combate["cd_recuperacao_base"],
            "atributo_chave": atributos_res["atributo_chave"],
            "historico_abcd": atributos_res["historico_abcd"],
            "orcamento_inicial": "15 po",
            "gasto_equipamentos": formatar_preco(equip_res["gasto_pc"]),
            "saldo_restante": formatar_preco(equip_res["saldo_pc"]),
            "gasto_pc": equip_res["gasto_pc"],
            "saldo_pc": equip_res["saldo_pc"],
            "armadura_equipada": equip_res["armadura"]["nome"],
            "observacoes_combate": notas_combate,
        },
        "ficha": ficha,
    }
