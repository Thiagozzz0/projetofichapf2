"""Orquestrador principal de geração procedural de fichas PF2E (1º ao 5º nível)."""

from __future__ import annotations

import random
from copy import deepcopy
from typing import Any

from .biografia_pericias import (
    calcular_idiomas,
    calcular_pericias,
    listar_catalogo_pericias,
    resumo_pericias_classe,
    selecionar_biografia,
)
from .combate_matematica import calcular_matematica_final
from .companheiros import gerar_companheiro_ou_familiar, listar_catalogo_companheiros_familiares
from .dados import BaseDados, carregar_dados
from .divindades import (
    CLASSES_DIVINDADE_OBRIGATORIA,
    determinar_tendencia as _determinar_tendencia,
    divindades_compativeis_conceito,
    fontes_divinas_aceitas_conceito,
    montar_resumo_divindade_ficha,
    resolver_divindade_e_fonte,
    selecionar_divindade as _selecionar_divindade,
)
from .equipamentos import (
    calcular_proficiencias_combate,
    comprar_equipamentos,
    listar_catalogo_equipamentos_loja,
    resumo_proficiencias_equipamento_classe,
)
from .magias import (
    gerar_conjuracao,
    listar_catalogo_magias,
    listar_catalogo_magias_n1,
    preencher_bloco_conjuracao_ficha,
    resumo_conjuracao_classe,
)
from .regras_atributos import calcular_atributos, normalizar_escolha_atributo, opcoes_atributo_classe
from .regras_casa import listar_opcoes_regras_casa, resolver_configuracao_regras_casa
from .talentos import listar_catalogo_talentos, listar_catalogo_talentos_n1, selecionar_talentos
from .util import ATRIBUTOS, atributo_id, formatar_preco, normalizar


class ErroValidacao(ValueError):
    """Erro levantado quando parâmetros de entrada da geração são inválidos."""


VALORES_ALEATORIOS = frozenset({"aleatorio", "aleatoria", "procedural", "random"})
NIVEL_MINIMO = 1
NIVEL_MAXIMO_CATALOGO = 5
NIVEIS_CATALOGO = (1, 2, 3, 4, 5)


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


def _atributo_chave_opcoes(
    db: BaseDados,
    classe: dict[str, Any],
    conceito: dict[str, Any] | None = None,
) -> list[str]:
    """Retorna os IDs de atributos-chave válidos para a classe ou para um conceito específico."""
    subs_todas = {s["id"]: s for s in classe.get("subclasses", {}).get("opcoes", [])}
    if conceito is not None:
        candidatas = list(conceito.get("subclasses_oficiais_candidatas") or [])
        if not candidatas and conceito.get("subclasse_oficial_id"):
            candidatas = [conceito["subclasse_oficial_id"]]
        subs_alvos = [subs_todas[sid] for sid in candidatas if sid in subs_todas]
    else:
        subs_alvos = list(subs_todas.values())

    opcoes: list[str] = []
    if subs_alvos:
        for sub in subs_alvos:
            for aid in opcoes_atributo_classe(classe, sub):
                if aid not in opcoes:
                    opcoes.append(aid)
    else:
        for aid in opcoes_atributo_classe(classe, None):
            if aid not in opcoes:
                opcoes.append(aid)
    return opcoes


def _selecionar_subclasse_procedural(
    db: BaseDados,
    classe_id: str,
    conceito: dict[str, Any],
    rng: random.Random,
    divindade_explicita: dict[str, Any] | None = None,
    classe_chave_escolha: Any = None,
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
    if classe_chave_escolha is not None:
        try:
            modo_chave = normalizar_escolha_atributo(classe_chave_escolha)
        except ValueError:
            modo_chave = "procedural"
        if modo_chave in ATRIBUTOS:
            classe_obj = db.classes[classe_id]
            compativeis_chave = [s for s in validas if modo_chave in opcoes_atributo_classe(classe_obj, s)]
            if compativeis_chave:
                validas = compativeis_chave
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

    t_anc5 = talentos_res.get("talento_ancestral_n5")
    if t_anc5 and len(hab_tal["ancestralidade"]) > 3:
        hab_tal["ancestralidade"][3]["nome"] = t_anc5["nome"]
        hab_tal["ancestralidade"][3]["origem_regra"] = f"Talento de Ancestralidade ({ancestralidade['nome']} N5)"
        hab_tal["ancestralidade"][3]["resumo"] = t_anc5["descricao"]

    # Perícia — slot 0 (BIOGRAFIA), slot 1 (2º), slot 2 (4º)
    tb = talentos_res["talento_biografia"]
    hab_tal["pericia"][0]["nome"] = tb["nome"]
    hab_tal["pericia"][0]["origem_regra"] = tb["origem"]
    hab_tal["pericia"][0]["resumo"] = tb["resumo"]

    mapa_slot_pericia_nivel = {2: 1, 4: 2}
    for tp_prog in talentos_res.get("talentos_pericia_progressao") or []:
        idx_p = mapa_slot_pericia_nivel.get(tp_prog.get("nivel_slot"))
        if idx_p is not None and idx_p < len(hab_tal["pericia"]):
            hab_tal["pericia"][idx_p]["nome"] = tp_prog["nome"]
            hab_tal["pericia"][idx_p]["origem_regra"] = tp_prog["origem_regra"]
            hab_tal["pericia"][idx_p]["resumo"] = tp_prog["resumo"]

    # Gerais — slot 0 (3º nível)
    for tg_prog in talentos_res.get("talentos_gerais_progressao") or []:
        if tg_prog.get("nivel_slot") == 3 and hab_tal["gerais"]:
            hab_tal["gerais"][0]["nome"] = tg_prog["nome"]
            hab_tal["gerais"][0]["origem_regra"] = tg_prog["origem_regra"]
            hab_tal["gerais"][0]["resumo"] = tg_prog["resumo"]
            break

    # Classe — slots 0 e 1 (CARACTERÍSTICA 1º), slot 2 (TALENTO 1º), slot 3 (TALENTO 2º),
    # slot 4 (CARACTERÍSTICA 3º), slot 5 (TALENTO 4º), slot 6 (CARACTERÍSTICA 5º)
    caracts_todas = talentos_res.get("caracteristicas_classe") or talentos_res["caracteristicas_classe_n1"]
    caracts_n1 = [c for c in caracts_todas if int(c.get("nivel", 1)) == 1]
    caracts_2_3 = [c for c in caracts_todas if 2 <= int(c.get("nivel", 1)) <= 3]
    caracts_4_5 = [c for c in caracts_todas if 4 <= int(c.get("nivel", 1)) <= 5]

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
    elif caracts_n1:
        hab_tal["classe"][0]["nome"] = caracts_n1[0]["nome"]
        hab_tal["classe"][0]["origem_regra"] = f"Classe ({classe['nome']})"
        hab_tal["classe"][0]["resumo"] = caracts_n1[0].get("descricao", "")

    nomes_caract = [c["nome"] for c in caracts_n1]
    if talentos_res["efeitos"].get("bloqueio_com_escudo") and "Bloqueio com Escudo" not in nomes_caract:
        nomes_caract.append("Bloqueio com Escudo")
    if nomes_caract:
        hab_tal["classe"][1]["nome"] = "; ".join(nomes_caract)
        hab_tal["classe"][1]["origem_regra"] = f"Características de 1º Nível ({classe['nome']})"
        hab_tal["classe"][1]["resumo"] = " | ".join(
            f"{c['nome']}: {c.get('descricao', '')[:160]}" for c in caracts_n1[:3]
        )

    if caracts_2_3 and len(hab_tal["classe"]) > 4:
        hab_tal["classe"][4]["nome"] = "; ".join(c["nome"] for c in caracts_2_3)
        hab_tal["classe"][4]["origem_regra"] = f"Características de 2º–3º Nível ({classe['nome']})"
        hab_tal["classe"][4]["resumo"] = " | ".join(
            f"{c['nome']}: {c.get('descricao', '')[:160]}" for c in caracts_2_3[:3]
        )
    if caracts_4_5 and len(hab_tal["classe"]) > 6:
        hab_tal["classe"][6]["nome"] = "; ".join(c["nome"] for c in caracts_4_5)
        hab_tal["classe"][6]["origem_regra"] = f"Características de 4º–5º Nível ({classe['nome']})"
        hab_tal["classe"][6]["resumo"] = " | ".join(
            f"{c['nome']}: {c.get('descricao', '')[:160]}" for c in caracts_4_5[:3]
        )

    talentos_classe = talentos_res["talentos_classe"]
    talentos_classe_n1 = [t for t in talentos_classe if int(t.get("nivel_slot", 1)) == 1]
    talentos_classe_n2 = [t for t in talentos_classe if int(t.get("nivel_slot", 1)) == 2]
    talentos_classe_n4 = [t for t in talentos_classe if int(t.get("nivel_slot", 1)) == 4]

    # Filtra talentos_bonus para evitar duplicar os que já ocupam slots dedicados (perícia N2/N4 e geral N3)
    bonus_extras = [
        b for b in talentos_res["talentos_bonus"]
        if not (
            (b.get("categoria") == "pericia" and b.get("nivel_slot") in (2, 4))
            or (b.get("categoria") == "geral" and b.get("nivel_slot") == 3)
        )
    ]

    if talentos_classe_n1:
        t0 = talentos_classe_n1[0]
        hab_tal["classe"][2]["nome"] = t0["nome"]
        hab_tal["classe"][2]["origem_regra"] = t0["origem"]
        hab_tal["classe"][2]["resumo"] = t0["descricao"]
        for t_extra in talentos_classe_n1[1:]:
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

    if talentos_classe_n2 and len(hab_tal["classe"]) > 3:
        t2 = talentos_classe_n2[0]
        hab_tal["classe"][3]["nome"] = t2["nome"]
        hab_tal["classe"][3]["origem_regra"] = t2["origem"]
        hab_tal["classe"][3]["resumo"] = t2["descricao"]
    if talentos_classe_n4 and len(hab_tal["classe"]) > 5:
        t4 = talentos_classe_n4[0]
        hab_tal["classe"][5]["nome"] = t4["nome"]
        hab_tal["classe"][5]["origem_regra"] = t4["origem"]
        hab_tal["classe"][5]["resumo"] = t4["descricao"]

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
            "melhorias_fixas_ids": (
                fixos := [aid for m in a["melhorias_atributo"] if (aid := atributo_id(m)) is not None]
            ),
            "qtd_melhorias_livres": sum(1 for m in a["melhorias_atributo"] if atributo_id(m) is None),
            "defeito_atributo": a.get("defeito_atributo"),
            "defeito_atributo_id": (
                defeito := (atributo_id(a["defeito_atributo"]) if a.get("defeito_atributo") else None)
            ),
            "atributos_bloqueados_livres_ids": list(dict.fromkeys([*fixos, *([defeito] if defeito else [])])),
            "herancas": [{"id": h["id"], "nome": h["nome"], "descricao": h["descricao"]} for h in a["herancas"]],
        }
        for a in db.ancestralidades.values()
    ]

    biografias = [
        {
            "id": b["id"],
            "nome": b["nome"],
            "melhorias_atributo_opcoes": b["melhorias_atributo_opcoes"],
            "melhorias_atributo_ids": [
                aid for opt in b["melhorias_atributo_opcoes"] if (aid := atributo_id(opt)) is not None
            ],
            "melhoria_livre": b.get("melhoria_livre", True),
            "pericia_treinada_opcoes": b["pericia_treinada_opcoes"],
            "pericia_treinada_ids": [pid for n in b["pericia_treinada_opcoes"] if (pid := db.pericia_id(n))],
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
            "atributo_chave_ids": _atributo_chave_opcoes(db, c, None),
            "permite_escolha_atributo_chave": len(_atributo_chave_opcoes(db, c, None)) > 1,
            "divindade_obrigatoria": c["id"] in CLASSES_DIVINDADE_OBRIGATORIA,
            "proficiencias_equipamento": resumo_proficiencias_equipamento_classe(c),
            "pericias_classe": resumo_pericias_classe(db, c),
            "conjuracao_classe": resumo_conjuracao_classe(db, c),
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
                    "tese_arcana_id": con.get("tese_arcana_id"),
                    "mago_universalista": (
                        c["id"] == "mago" and con.get("subclasse_oficial_id") == "universalista"
                    ),
                    "companheiro_padrao_conceito": (
                        "companheiro_animal"
                        if (
                            (c["id"] == "druida" and con.get("subclasse_oficial_id") == "animais")
                            or ((con.get("talentos_recomendados", {}).get("classe_nivel_1") or [None])[0] == "companheiro_animal")
                        )
                        else (
                            "familiar"
                            if (
                                (c["id"] == "druida" and con.get("subclasse_oficial_id") == "folha")
                                or con.get("tese_arcana_id") == "sintonizacao_com_familiar_aprimorada"
                                or ((con.get("talentos_recomendados", {}).get("classe_nivel_1") or [None])[0] in ("familiar", "familiar_alquimico", "familiar_leshy"))
                            )
                            else None
                        )
                    ),
                    "desbloqueia_talento_classe_n1_extra": (
                        con.get("subclasse_oficial_id") == "instinto_do_furor"
                        or con.get("tese_arcana_id") == "experimentacao_metamagica"
                    ),
                    "atributo_chave_opcoes": _atributo_chave_opcoes(db, c, con),
                    "prioridade_atributos": list(con.get("prioridade_atributos", [])),
                    "estilo_empunhadura": (con.get("equipamento_recomendado") or {}).get("estilo_empunhadura", ""),
                    "saber_sugerido": con.get("saber_sugerido", ""),
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
            "arma_favorecida_id": d.get("arma_favorecida_id"),
            "arma_favorecida_nome": d["arma_favorecida_nome"],
            "pericia_divina": d["pericia_divina"],
            "magia_clerigo_n1_id": (d.get("magias_clerigo") or {}).get("1"),
            "dominios": d["dominios"],
        }
        for d in db.divindades.values()
    ]

    return {
        "nivel_minimo": NIVEL_MINIMO,
        "nivel_maximo_catalogo": NIVEL_MAXIMO_CATALOGO,
        "niveis_catalogo": list(NIVEIS_CATALOGO),
        "ancestralidades": ancestralidades,
        "biografias": biografias,
        "classes": classes,
        "divindades": divindades,
        "catalogo_pericias": listar_catalogo_pericias(db),
        "catalogo_talentos": listar_catalogo_talentos(db, nivel_maximo=NIVEL_MAXIMO_CATALOGO),
        "catalogo_magias": listar_catalogo_magias(db, circulo_maximo=3),
        "catalogo_equipamentos": listar_catalogo_equipamentos_loja(db),
        "catalogo_companheiros": listar_catalogo_companheiros_familiares(db),
        "catalogo_regras_casa": listar_opcoes_regras_casa(),
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
    nivel: int | str = 1,
    seed: int | str | None = None,
    escolhas_atributos: dict[str, Any] | None = None,
    escolhas_pericias: dict[str, Any] | None = None,
    escolhas_talentos: dict[str, Any] | None = None,
    escolhas_magias: dict[str, Any] | None = None,
    escolhas_equipamentos: dict[str, Any] | None = None,
    escolhas_perfil: dict[str, Any] | None = None,
    escolhas_companheiro: dict[str, Any] | None = None,
    escolhas_regras_casa: dict[str, Any] | str | None = None,
    dados: BaseDados | None = None,
) -> dict[str, Any]:
    """Gera uma ficha completa e válida de Pathfinder 2E guiada pelo conceito escolhido."""
    db = dados or carregar_dados()

    try:
        config_regras_casa = resolver_configuracao_regras_casa(escolhas_regras_casa)
    except ValueError as exc:
        raise ErroValidacao(str(exc)) from exc

    # Seed opcional no início para tornar determinísticos também os sorteios de entrada
    if seed is None or str(seed).strip() == "":
        seed_usada: int | str = random.SystemRandom().randint(1, 999_999_999)
    else:
        seed_str = str(seed).strip()
        seed_usada = int(seed_str) if seed_str.isdigit() else seed_str
    rng = random.Random(seed_usada)

    # ------------------------------------------------------------------
    # 1. Validação e resolução (manual ou aleatória) das entradas
    # ------------------------------------------------------------------
    if str(nivel or "").strip().lower() in VALORES_ALEATORIOS:
        nivel_int = rng.randint(NIVEL_MINIMO, NIVEL_MAXIMO_CATALOGO)
    else:
        try:
            nivel_int = int(nivel)
        except (TypeError, ValueError) as exc:
            raise ErroValidacao(f"Valor inválido para 'nivel': {nivel!r}.") from exc
    if not (NIVEL_MINIMO <= nivel_int <= NIVEL_MAXIMO_CATALOGO):
        raise ErroValidacao(
            f"Esta versão do motor gera personagens do {NIVEL_MINIMO}º ao {NIVEL_MAXIMO_CATALOGO}º nível "
            f"(nivel={NIVEL_MINIMO}..{NIVEL_MAXIMO_CATALOGO})."
        )
    nivel = nivel_int

    div_req = None if divindade_id is None else str(divindade_id).strip()
    div_req_norm = (div_req or "").lower()
    divindade_explicita: dict[str, Any] | None = None
    if div_req_norm not in ("", "nenhuma", "procedural", "aleatoria", "aleatorio", "random"):
        divindade_explicita = db.divindades.get(div_req)
        if not divindade_explicita:
            raise ErroValidacao(f"Divindade desconhecida: '{div_req}'.")

    if str(ancestralidade_id or "").strip().lower() in VALORES_ALEATORIOS:
        ancestralidade = rng.choice(list(db.ancestralidades.values()))
        ancestralidade_id = ancestralidade["id"]
    else:
        ancestralidade = db.ancestralidades.get(ancestralidade_id)
        if not ancestralidade:
            raise ErroValidacao(f"Ancestralidade desconhecida: '{ancestralidade_id}'.")

    if str(heranca_id or "").strip().lower() in VALORES_ALEATORIOS:
        heranca = rng.choice(ancestralidade["herancas"])
        heranca_id = heranca["id"]
    else:
        heranca = db.heranca(ancestralidade_id, heranca_id)
        if not heranca:
            raise ErroValidacao(f"Herança '{heranca_id}' não pertence à ancestralidade '{ancestralidade_id}'.")

    def _conceitos_compativeis_divindade(cls_cand_id: str) -> list[dict[str, Any]]:
        cons = db.conceitos_da_classe(cls_cand_id)
        if divindade_explicita is None or cls_cand_id not in CLASSES_DIVINDADE_OBRIGATORIA:
            return cons
        did_exp = divindade_explicita["id"]
        return [c for c in cons if did_exp in divindades_compativeis_conceito(db, cls_cand_id, c)]

    if str(classe_id or "").strip().lower() in VALORES_ALEATORIOS:
        classes_pool = list(db.classes.values())
        if div_req_norm == "nenhuma":
            classes_pool = [c for c in classes_pool if c["id"] not in CLASSES_DIVINDADE_OBRIGATORIA]
        elif divindade_explicita is not None:
            compat_cls = [c for c in classes_pool if _conceitos_compativeis_divindade(c["id"])]
            if compat_cls:
                classes_pool = compat_cls
        classe = rng.choice(classes_pool)
        classe_id = classe["id"]
    else:
        classe = db.classes.get(classe_id)
        if not classe:
            raise ErroValidacao(f"Classe desconhecida: '{classe_id}'.")

    if str(conceito_id or "").strip().lower() in VALORES_ALEATORIOS:
        cons_pool = _conceitos_compativeis_divindade(classe_id)
        if not cons_pool:
            raise ErroValidacao(
                f"Nenhum conceito da classe '{classe['nome']}' é compatível com a divindade '{divindade_explicita['nome']}'."
            )
        conceito = rng.choice(cons_pool)
        conceito_id = conceito["id"]
    else:
        conceito = db.conceitos.get(conceito_id)
        if not conceito:
            raise ErroValidacao(f"Conceito desconhecido: '{conceito_id}'.")
        if conceito["classe_id"] != classe_id:
            raise ErroValidacao(
                f"O conceito '{conceito_id}' pertence à classe '{conceito['classe_id']}', não a '{classe_id}'."
            )

    if classe_id in CLASSES_DIVINDADE_OBRIGATORIA and div_req is not None and div_req_norm in ("", "nenhuma"):
        raise ErroValidacao(f"A classe {classe['nome']} exige obrigatoriamente a seleção de uma divindade.")

    subclasse = _selecionar_subclasse_procedural(
        db,
        classe_id,
        conceito,
        rng,
        divindade_explicita=divindade_explicita,
        classe_chave_escolha=escolhas_atributos.get("classe_chave") if escolhas_atributos else None,
    )
    tese_arcana = _resolver_tese_arcana(classe, conceito.get("tese_arcana_id")) if classe_id == "mago" else None

    try:
        divindade, fonte_divina = resolver_divindade_e_fonte(
            db, classe, subclasse, conceito, div_req_norm, divindade_explicita, rng
        )
    except ValueError as exc:
        raise ErroValidacao(str(exc)) from exc

    # ------------------------------------------------------------------
    # 2. Seleção de Biografia (Manual ou Procedural) + Atributos (ABCD)
    # ------------------------------------------------------------------
    try:
        biografia, biografia_procedural = selecionar_biografia(
            db,
            conceito,
            ancestralidade,
            biografia_id=biografia_id,
            rng=rng,
            escolhas_atributos=escolhas_atributos,
        )
        atributos_res = calcular_atributos(
            ancestralidade,
            biografia,
            classe,
            subclasse,
            conceito,
            nivel=nivel,
            escolhas_atributos=escolhas_atributos,
            rng=rng,
        )
    except ValueError as exc:
        raise ErroValidacao(str(exc)) from exc
    mod_int = atributos_res["modificadores"]["int"]
    mod_for = atributos_res["modificadores"]["for"]

    # ------------------------------------------------------------------
    # 3. Perícias base -> Talentos -> Perícias extras (ex.: Perícia Natural)
    # ------------------------------------------------------------------
    try:
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
            nivel=nivel,
            escolhas_pericias=escolhas_pericias,
            validar_limite=False,
            rng=rng,
        )
    except ValueError as exc:
        raise ErroValidacao(str(exc)) from exc
    perfil_req = escolhas_perfil or {}
    try:
        tendencia = _determinar_tendencia(
            classe_id,
            subclasse["id"] if subclasse else "",
            conceito=conceito,
            divindade=divindade,
            tendencia_manual=perfil_req.get("tendencia"),
        )
    except ValueError as exc:
        raise ErroValidacao(str(exc)) from exc

    try:
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
            atributos=atributos_res["valores"],
            nivel=nivel,
            escolhas_talentos=escolhas_talentos,
            rng=rng,
        )
    except ValueError as exc:
        raise ErroValidacao(str(exc)) from exc

    extras_per = talentos_res["efeitos"]["extras_pericias"]
    pericias_anc_fixas = talentos_res["efeitos"].get("pericias_ancestrais_fixas") or []
    saber_anc = talentos_res["efeitos"].get("saber_ancestral")
    if extras_per > 0 or pericias_anc_fixas or saber_anc or escolhas_pericias:
        # Recalcula com determinismo preservado e validação estrita de teto de vagas
        try:
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
                pericias_ancestrais_fixas=pericias_anc_fixas,
                saber_ancestral=saber_anc,
                nivel=nivel,
                escolhas_pericias=escolhas_pericias,
                validar_limite=True,
                rng=random.Random(f"{seed_usada}:pericias"),
            )
        except ValueError as exc:
            raise ErroValidacao(str(exc)) from exc
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
        efeitos_talentos=talentos_res["efeitos"],
        nivel=nivel,
        conceito=conceito,
        dados=db,
    )
    try:
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
            biografia=biografia,
            nivel=nivel,
            escolhas_equipamentos=escolhas_equipamentos,
            regras_casa=config_regras_casa,
        )
    except ValueError as exc:
        raise ErroValidacao(str(exc)) from exc
    try:
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
            talento_ancestral_id=talentos_res["efeitos"].get("talento_ancestral_id"),
            escolhas_magias=escolhas_magias,
            rng=rng,
        )
    except ValueError as exc:
        raise ErroValidacao(str(exc)) from exc

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

    divindade_texto, divindade_detalhes = montar_resumo_divindade_ficha(
        divindade, classe_id, fonte_divina
    )

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

    try:
        companheiro_ou_familiar = gerar_companheiro_ou_familiar(
            dados=db,
            classe=classe,
            subclasse=subclasse,
            conceito=conceito,
            talentos_classe_ids=talentos_res["talentos_classe_ids"],
            ficha_mestre=ficha,
            modificadores_mestre=atributos_res["modificadores"],
            tese_arcana_id=tese_arcana["id"] if tese_arcana else None,
            talento_ancestral_id=talentos_res["efeitos"].get("talento_ancestral_id"),
            ancestralidade=ancestralidade,
            biografia=biografia,
            nivel=nivel,
            escolhas_companheiro=escolhas_companheiro,
            rng=rng,
        )
    except ValueError as exc:
        raise ErroValidacao(str(exc)) from exc

    sub_nome_final = subclasse["nome"] if subclasse else conceito["subclasse_oficial_nome"]
    tese_nota = f" | Tese: {tese_arcana['nome']}" if tese_arcana else ""

    dados_bio_ficha = ficha["perfil_e_campanha"]["dados_biograficos"]
    idade_req = str(perfil_req.get("idade") or "").strip()
    dados_bio_ficha["idade"] = idade_req or str(ancestralidade.get("maturidade_anos", 20))
    for campo_bio in ("etnia", "nacionalidade", "local_nascimento", "genero_pronomes", "altura", "peso", "aparencia"):
        val_b = str(perfil_req.get(campo_bio) or "").strip()
        if val_b:
            dados_bio_ficha[campo_bio] = val_b

    pers_ficha = ficha["perfil_e_campanha"]["personalidade"]
    for campo_p in ("atitude", "crencas", "gostos", "aversoes", "bordoes"):
        val_p = str(perfil_req.get(campo_p) or "").strip()
        if val_p:
            pers_ficha[campo_p] = val_p

    ficha["perfil_e_campanha"]["anotacoes_campanha"]["anotacoes"] = (
        f"Conceito: {conceito['titulo_completo']} (Subclasse PF2E: {sub_nome_final}{tese_nota}). "
        f"{conceito['resumo_proposta']} "
        f"Sinergia: {conceito.get('sinergia_mecanica', '')} "
        f"Biografia: {biografia['descricao']}"
    ).strip()

    escolhas_perfil_aplicadas = {
        "tendencia": tendencia,
        "idade": dados_bio_ficha["idade"],
        "genero_pronomes": dados_bio_ficha["genero_pronomes"],
        "aparencia": dados_bio_ficha["aparencia"],
        "crencas": pers_ficha["crencas"],
        "aversoes": pers_ficha["aversoes"],
    }

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
            "divindade_procedural": (div_req_norm in ("", "procedural", "aleatoria", "aleatorio", "random")) and (divindade is not None),
            "divindade_detalhes": divindade_detalhes,
            "companheiro_ou_familiar": companheiro_ou_familiar,
            "limite_morrendo": notas_combate["limite_morrendo"],
            "cd_recuperacao_base": notas_combate["cd_recuperacao_base"],
            "atributo_chave": atributos_res["atributo_chave"],
            "escolhas_atributos": atributos_res["escolhas_aplicadas"],
            "historico_abcd": atributos_res["historico_abcd"],
            "escolhas_pericias": pericias_res["escolhas_pericias"],
            "escolhas_talentos": talentos_res["escolhas_talentos"],
            "escolhas_magias": magias_res.get("escolhas_magias"),
            "escolhas_perfil": escolhas_perfil_aplicadas,
            "orcamento_inicial": formatar_preco(equip_res.get("orcamento_pc", 1500)),
            "orcamento_pc": equip_res.get("orcamento_pc", 1500),
            "escolhas_equipamentos": equip_res["escolhas_equipamentos"],
            "gasto_equipamentos": formatar_preco(equip_res["gasto_pc"]),
            "saldo_restante": formatar_preco(equip_res["saldo_pc"]),
            "gasto_pc": equip_res["gasto_pc"],
            "saldo_pc": equip_res["saldo_pc"],
            "armadura_equipada": equip_res["armadura"]["nome"],
            "armadura_equipada_resumo": equip_res["armadura_resumo"],
            "volume_leves_soltos": equip_res["volume_leves_soltos"],
            "itens_leves_por_volume": equip_res["itens_leves_por_volume"],
            "regras_casa": {
                "modo": config_regras_casa["modo"],
                "nome_perfil": config_regras_casa["nome_perfil"],
                "ativa": config_regras_casa["ativa"],
                "regras_ativas_ids": config_regras_casa["regras_ativas_ids"],
                "regras_ativas_resumo": config_regras_casa["regras_ativas_resumo"],
                "itens_leves_por_volume": config_regras_casa["itens_leves_por_volume"],
            },
            "observacoes_combate": notas_combate,
        },
        "ficha": ficha,
    }
