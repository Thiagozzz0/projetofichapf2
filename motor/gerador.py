"""Orquestrador principal de geração procedural de fichas PF2E (1º nível)."""

from __future__ import annotations

import random
from copy import deepcopy
from typing import Any

from .biografia_pericias import calcular_idiomas, calcular_pericias, selecionar_biografia
from .combate_matematica import calcular_matematica_final
from .dados import BaseDados, carregar_dados
from .equipamentos import calcular_proficiencias_combate, comprar_equipamentos
from .magias import gerar_conjuracao, preencher_bloco_conjuracao_ficha
from .regras_atributos import calcular_atributos
from .talentos import selecionar_talentos
from .util import formatar_preco, normalizar


class ErroValidacao(ValueError):
    """Erro levantado quando parâmetros de entrada da geração são inválidos."""


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


def _determinar_tendencia(classe_id: str, subclasse_id: str) -> str:
    if classe_id == "campeao":
        return {"paladino": "OB", "redentor": "NB", "libertador": "CB"}.get(subclasse_id, "NB")
    if classe_id == "druida":
        return "N"
    return "NB"


def _preencher_pagina_talentos(
    ficha: dict[str, Any],
    ancestralidade: dict[str, Any],
    heranca: dict[str, Any],
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    talentos_res: dict[str, Any],
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
    if subclasse:
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
                    "origem_regra": t_extra["origem"],
                    "pagina": None,
                    "resumo": t_extra["descricao"],
                }
            )
    else:
        hab_tal["classe"][2]["nome"] = "—"
        hab_tal["classe"][2]["origem_regra"] = f"{classe['nome']} não escolhe talento livre no 1º nível"
        hab_tal["classe"][2]["resumo"] = ""

    # Bônus — até 2 slots oficiais
    for idx, b in enumerate(bonus_extras[: len(hab_tal["bonus"])]):
        hab_tal["bonus"][idx]["nome"] = b["nome"]
        hab_tal["bonus"][idx]["origem_regra"] = b["origem_regra"]
        hab_tal["bonus"][idx]["pagina"] = b.get("pagina")
        hab_tal["bonus"][idx]["resumo"] = b["resumo"]


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
            "conceitos": [
                {
                    "id": con["id"],
                    "nome": con["nome"],
                    "titulo_completo": con["titulo_completo"],
                    "subclasse_oficial_nome": con["subclasse_oficial_nome"],
                    "resumo_proposta": con["resumo_proposta"],
                }
                for con in db.conceitos_da_classe(c["id"])
            ],
        }
        for c in db.classes.values()
    ]

    return {
        "ancestralidades": ancestralidades,
        "biografias": biografias,
        "classes": classes,
        "total_conceitos": len(db.conceitos),
    }


def gerar_personagem(
    ancestralidade_id: str,
    heranca_id: str,
    classe_id: str,
    conceito_id: str,
    biografia_id: str | None = None,
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

    subclasse = db.subclasse(classe_id, conceito["subclasse_oficial_id"])

    # Seed opcional: se não informada, cria uma seed aleatória rastreável
    if seed is None or str(seed).strip() == "":
        seed_usada: int | str = random.SystemRandom().randint(1, 999_999_999)
    else:
        seed_str = str(seed).strip()
        seed_usada = int(seed_str) if seed_str.isdigit() else seed_str
    rng = random.Random(seed_usada)

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
        db, ancestralidade, heranca, biografia, classe, subclasse, conceito, mod_int, extras_pericias=0, rng=rng
    )
    tendencia = _determinar_tendencia(classe_id, subclasse["id"] if subclasse else "")
    fonte_divina = "ferimento" if "exaurir" in conceito["id"] else "cura"

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
            rng=random.Random(f"{seed_usada}:pericias"),
        )
    else:
        pericias_res = pericias_base

    idiomas = calcular_idiomas(db, ancestralidade, heranca, classe, mod_int, rng=rng)

    # ------------------------------------------------------------------
    # 4. Equipamentos (15 po), Volume e Conjuração
    # ------------------------------------------------------------------
    profs_combate = calcular_proficiencias_combate(classe, subclasse)
    equip_res = comprar_equipamentos(
        db, ancestralidade, classe, conceito, mod_for, profs_combate, mod_int=mod_int
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
        "divindade": "Sarenrae / Divindade Bondosa" if classe_id in ("campeao", "clerigo") else "",
        "nivel": nivel,
        "pontos_heroismo": 1,
    }

    for aid, val in atributos_res["valores"].items():
        ficha["atributos"][aid] = {
            "valor": val,
            "modificador": atributos_res["modificadores"][aid],
        }

    _preencher_pagina_talentos(ficha, ancestralidade, heranca, classe, subclasse, talentos_res)
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
    )

    ficha["perfil_e_campanha"]["dados_biograficos"]["idade"] = str(ancestralidade.get("maturidade_anos", 20))
    ficha["perfil_e_campanha"]["anotacoes_campanha"]["anotacoes"] = (
        f"Conceito: {conceito['titulo_completo']} ({conceito['subclasse_oficial_nome']}). "
        f"{conceito['resumo_proposta']} "
        f"Biografia: {biografia['descricao']}"
    )

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
