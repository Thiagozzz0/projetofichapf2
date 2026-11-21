"""Avaliação de pré-requisitos e seleção de talentos e características de 1º nível."""

from __future__ import annotations

import random
import re
from typing import Any

from .dados import BaseDados
from .util import GRAUS, normalizar, slugify


_CLASSES_CONJURADORAS_PLENAS = {"bardo", "clerigo", "druida", "feiticeiro", "mago"}


def atende_prerequisitos(texto_prereq: str | None, ctx: dict[str, Any]) -> bool:
    """Avalia expressões comuns de pré-requisitos de talentos de 1º nível do PF2E."""
    if not texto_prereq:
        return True

    t = normalizar(texto_prereq)

    # Observação editorial presente no dado de passadela_goblin (texto de acionamento)
    if "termina uma acao de movimento" in t:
        return True

    graus_pericias: dict[str, str] = ctx.get("graus_pericias", {})
    classe_id: str = ctx.get("classe_id", "")
    subclasse_id: str = ctx.get("subclasse_id", "")
    tradicoes_foco = ctx.get("conjuracao_plena", False)

    for clausula in [c.strip() for c in t.split(",") if c.strip()]:
        if not _avaliar_clausula(
            clausula, graus_pericias, classe_id, subclasse_id, tradicoes_foco, ctx
        ):
            return False
    return True


def _tem_grau_minimo(grau_atual: str | None, grau_req: str) -> bool:
    if not grau_atual or grau_atual not in GRAUS or grau_req not in GRAUS:
        return False
    return GRAUS.index(grau_atual) >= GRAUS.index(grau_req)


def _avaliar_clausula(
    c: str,
    graus: dict[str, str],
    classe_id: str,
    subclasse_id: str,
    conjuracao_plena: bool,
    ctx: dict[str, Any],
) -> bool:
    # Padrão: "<grau> em <perícia(s)>"
    m = re.match(r"^(treinado|especialista|mestre|lendario) em (.+)$", c)
    if m:
        grau_req, alvo = m.group(1), m.group(2)
        if "pelo menos uma pericia" in alvo or "uma pericia com a acao recordar conhecimento" in alvo:
            return any(_tem_grau_minimo(g, grau_req) for g in graus.values())
        if "arma favorita" in alvo:
            return True  # Divindade compatível com arma simples no Capelão da Guerra
        # Separa opções "Arcanismo, Natureza, Ocultismo ou Religião"
        opcoes = [p.strip() for p in re.split(r",| ou ", alvo) if p.strip()]
        dados: BaseDados | None = ctx.get("dados")
        for opt in opcoes:
            pid = dados.pericia_id(opt) if dados else slugify(opt)
            if pid and _tem_grau_minimo(graus.get(pid), grau_req):
                return True
        return False

    if c.startswith("musa "):
        musa_req = slugify(c.replace("musa ", ""))
        return classe_id == "bardo" and subclasse_id == musa_req

    if c == "reserva de foco":
        return classe_id in {"bardo", "campeao", "druida", "feiticeiro", "mago"}

    if c.startswith("causa de "):
        causa_req = slugify(c.replace("causa de ", ""))
        return classe_id == "campeao" and subclasse_id == causa_req

    if c.startswith("ordem d"):
        # ex.: "ordem dos animais", "ordem da folha", "ordem da tempestade", "ordem dos selvagens"
        for nome_sub in ("animais", "folha", "tempestade", "selvagens"):
            if nome_sub in c:
                return classe_id == "druida" and subclasse_id == nome_sub
        return False

    if c == "mago universalista":
        return classe_id == "mago" and subclasse_id == "universalista"

    if c == "tendencia bondosa":
        return ctx.get("tendencia_bondosa", True)

    if c == "fonte de cura":
        return classe_id == "clerigo" and ctx.get("fonte_divina", "cura") == "cura"

    if c == "fonte de ferimento":
        return classe_id == "clerigo" and ctx.get("fonte_divina", "cura") == "ferimento"

    if "arma favorita simples" in c:
        return classe_id == "clerigo" and subclasse_id == "capelao_da_guerra"

    if "caracteristica de classe de conjuracao" in c:
        return conjuracao_plena

    if "pelo menos 100 anos" in c:
        return ctx.get("ancestralidade_id") == "elfo"

    # Cláusulas específicas conhecidas de pré-requisitos em talentos de perícia N1 (ex.: Certeza, Gracejos da Corte)
    return False


def _pontuar_afinidade(item: dict[str, Any], keywords: list[str]) -> int:
    texto = normalizar(
        " ".join(
            [item.get("nome", ""), item.get("descricao", "")]
            + list(item.get("tracos", []))
        )
    )
    score = 0
    for kw in keywords:
        k = normalizar(kw)
        if k and k in texto:
            score += 3
    return score


def _escolher_por_lista_ou_afinidade(
    candidatos: list[dict[str, Any]],
    preferidos_ids: list[str],
    keywords: list[str],
    ja_escolhidos: set[str],
    rng: random.Random | None,
) -> dict[str, Any] | None:
    validos = [t for t in candidatos if t["id"] not in ja_escolhidos]
    if not validos:
        return None

    por_id = {t["id"]: t for t in validos}
    for tid in preferidos_ids:
        if tid in por_id:
            return por_id[tid]

    # Fallback pontuado por afinidade temática
    avaliados = sorted(
        validos,
        key=lambda t: _pontuar_afinidade(t, keywords),
        reverse=True,
    )
    melhor = _pontuar_afinidade(avaliados[0], keywords)
    empate = [t for t in avaliados if _pontuar_afinidade(t, keywords) == melhor]
    if rng is not None and len(empate) > 1:
        return rng.choice(empate)
    return empate[0]


def selecionar_talentos(
    dados: BaseDados,
    ancestralidade: dict[str, Any],
    heranca: dict[str, Any],
    biografia: dict[str, Any],
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    conceito: dict[str, Any],
    graus_pericias: dict[str, str],
    pericia_bio_id: str | None = None,
    tendencia: str = "NB",
    fonte_divina: str = "cura",
    tese_arcana_id: str | None = None,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Seleciona todos os talentos e características aplicáveis ao 1º nível."""
    keywords = list(conceito["talentos_recomendados"].get("tracos_ancestralidade_afinidade", []))
    sub_id = subclasse["id"] if subclasse else ""
    ctx = {
        "dados": dados,
        "graus_pericias": graus_pericias,
        "classe_id": classe["id"],
        "subclasse_id": sub_id,
        "ancestralidade_id": ancestralidade["id"],
        "conjuracao_plena": classe["id"] in _CLASSES_CONJURADORAS_PLENAS,
        "tendencia_bondosa": "B" in tendencia.upper(),
        "fonte_divina": fonte_divina,
    }

    # ------------------------------------------------------------------
    # 1. Talento de Perícia da Biografia
    # ------------------------------------------------------------------
    nome_talento_bio = biografia["talento_pericia"]
    if biografia["id"] == "discipulo_marcial":
        tal_bio = dados.resolver_talento_geral_pericia(
            "Queda do Gato" if pericia_bio_id == "acrobatismo" else "Salto Rápido"
        )
    else:
        tal_bio = dados.resolver_talento_geral_pericia(nome_talento_bio)

    talento_bio_registro = {
        "id": tal_bio["id"] if tal_bio else slugify(nome_talento_bio),
        "nome": nome_talento_bio,
        "origem": f"Biografia ({biografia['nome']})",
        "pagina": None,
        "resumo": (tal_bio.get("resumo_beneficio") or tal_bio.get("descricao", "")) if tal_bio else nome_talento_bio,
        "dados_completos": tal_bio,
    }

    # ------------------------------------------------------------------
    # 2. Talento de Ancestralidade (1º nível)
    # ------------------------------------------------------------------
    pool_anc = [t for t in ancestralidade.get("talentos_ancestralidade", []) if t.get("nivel") == 1]
    if heranca["id"] == "meio_elfo":
        elfo = dados.ancestralidades["elfo"]
        pool_anc.extend(t for t in elfo.get("talentos_ancestralidade", []) if t.get("nivel") == 1)
        pool_anc.extend(t for t in dados.talentos_mesticos.get("meio_elfo", []) if t.get("nivel") == 1)
    elif heranca["id"] == "meio_orc":
        pool_anc.extend(t for t in dados.talentos_mesticos.get("meio_orc", []) if t.get("nivel") == 1)

    # Deduplica preservando ordem e filtra por pré-requisitos
    vistos_anc: set[str] = set()
    candidatos_anc: list[dict[str, Any]] = []
    for t in pool_anc:
        if t["id"] not in vistos_anc and atende_prerequisitos(t.get("pre_requisitos"), ctx):
            vistos_anc.add(t["id"])
            candidatos_anc.append(t)

    # Pontua talentos ancestrais pelas keywords do conceito (mantendo variedade com rng entre top 3)
    scored_anc = []
    for t in candidatos_anc:
        pts = _pontuar_afinidade(t, keywords)
        if t["id"] == "ambicao_natural" and classe["id"] not in {
            "alquimista", "barbaro", "campeao", "guerreiro", "ladino", "monge", "patrulheiro"
        }:
            pts += 4
        if t["id"] == "pericia_natural" and classe["id"] in {"mago", "guerreiro", "campeao", "clerigo"}:
            pts += 2
        scored_anc.append((pts, t))
    scored_anc.sort(key=lambda x: x[0], reverse=True)
    melhor_anc = scored_anc[0][0]
    elegiveis_anc = [t for p, t in scored_anc if p >= max(0, melhor_anc - 2)][:3]
    talento_ancestral = rng.choice(elegiveis_anc) if (rng and len(elegiveis_anc) > 1) else elegiveis_anc[0]

    # ------------------------------------------------------------------
    # 3. Talentos de Classe N1 (obrigatórios de subclasse + escolha livre)
    # ------------------------------------------------------------------
    talentos_classe_n1_all = [t for t in classe["talentos_de_classe"] if t.get("nivel") == 1]
    talentos_classe_por_id = {t["id"]: t for t in talentos_classe_n1_all}
    escolhidos_classe_ids: set[str] = set()
    talentos_classe_selecionados: list[dict[str, Any]] = []

    def adicionar_classe_talento(tid: str | None, origem: str) -> None:
        if not tid:
            return
        t = talentos_classe_por_id.get(tid)
        if t and tid not in escolhidos_classe_ids:
            escolhidos_classe_ids.add(tid)
            talentos_classe_selecionados.append(dict(t, origem=origem))

    # Concedidos automaticamente pela subclasse no 1º nível
    if subclasse and "talento_concedido" in subclasse:
        adicionar_classe_talento(
            slugify(subclasse["talento_concedido"]),
            f"Subclasse ({subclasse['nome']})",
        )
    if classe["id"] == "clerigo":
        if sub_id == "sacerdote_enclausurado":
            adicionar_classe_talento("iniciado_no_dominio", "Doutrina (Primeira Doutrina)")
        elif sub_id == "capelao_da_guerra":
            adicionar_classe_talento("simplicidade_mortal", "Doutrina (Primeira Doutrina)")

    # Classes que possuem talento de classe livre no 1º nível (tabela_progressao[0])
    prog1 = [normalizar(x) for x in classe["tabela_progressao"][0]["caracteristicas"]]
    tem_talento_classe_livre = any(x.startswith("talento de ") for x in prog1) or (
        classe["id"] == "mago" and sub_id == "universalista"
    )
    if tem_talento_classe_livre:
        validos_c = [
            t for t in talentos_classe_n1_all
            if t["id"] not in escolhidos_classe_ids and atende_prerequisitos(t.get("pre_requisitos"), ctx)
        ]
        escolhido = _escolher_por_lista_ou_afinidade(
            validos_c,
            conceito["talentos_recomendados"]["classe_nivel_1"],
            keywords,
            escolhidos_classe_ids,
            rng,
        )
        if escolhido:
            adicionar_classe_talento(escolhido["id"], f"Classe ({classe['nome']} 1º Nível)")

    # Subclasse Bárbaro Instinto do Furor: concede +1 talento de bárbaro de 1º nível
    if (
        classe["id"] == "barbaro"
        and subclasse
        and isinstance(subclasse.get("habilidade_instinto"), dict)
        and subclasse["habilidade_instinto"].get("talento_bonus_1_nivel")
    ):
        validos_furor = [
            t for t in talentos_classe_n1_all
            if t["id"] not in escolhidos_classe_ids and atende_prerequisitos(t.get("pre_requisitos"), ctx)
        ]
        escolhido_furor = _escolher_por_lista_ou_afinidade(
            validos_furor,
            conceito["talentos_recomendados"]["classe_nivel_1"],
            keywords,
            escolhidos_classe_ids,
            rng,
        )
        if escolhido_furor:
            adicionar_classe_talento(escolhido_furor["id"], f"Subclasse ({subclasse['nome']})")

    # Tese Arcana do Mago que concede talento bônus de 1º nível
    if classe["id"] == "mago" and tese_arcana_id:
        if tese_arcana_id == "sintonizacao_com_familiar_aprimorada":
            adicionar_classe_talento("familiar", "Tese Arcana (Sintonização com Familiar Aprimorada)")
        elif tese_arcana_id == "experimentacao_metamagica":
            validos_meta = [
                t for t in talentos_classe_n1_all
                if t["id"] not in escolhidos_classe_ids and "metamagia" in " ".join(normalizar(x) for x in t.get("tracos", []))
            ]
            escolhido_meta = _escolher_por_lista_ou_afinidade(
                validos_meta,
                conceito["talentos_recomendados"]["classe_nivel_1"],
                keywords,
                escolhidos_classe_ids,
                rng,
            )
            if escolhido_meta:
                adicionar_classe_talento(escolhido_meta["id"], "Tese Arcana (Experimentação Metamágica)")

    # Humano: Ambição Natural concede +1 talento de classe N1
    if talento_ancestral["id"] == "ambicao_natural":
        validos_c = [
            t for t in talentos_classe_n1_all
            if t["id"] not in escolhidos_classe_ids and atende_prerequisitos(t.get("pre_requisitos"), ctx)
        ]
        escolhido_amb = _escolher_por_lista_ou_afinidade(
            validos_c,
            conceito["talentos_recomendados"]["classe_nivel_1"],
            keywords,
            escolhidos_classe_ids,
            rng,
        )
        if escolhido_amb:
            adicionar_classe_talento(escolhido_amb["id"], "Talento Ancestral (Ambição Natural)")

    # ------------------------------------------------------------------
    # 4. Talentos Extras (Ladino Perícia N1 + Gerais automáticos / Versátil / Treinamento Geral)
    # ------------------------------------------------------------------
    talentos_bonus_slots: list[dict[str, Any]] = []
    ids_gerais_pericia_usados: set[str] = {talento_bio_registro["id"]}

    if classe["id"] == "ladino":
        candidatos_tp = [
            t for t in dados.talentos_gerais_pericia.values()
            if t.get("nivel") == 1
            and t.get("categoria") == "pericia"
            and t["id"] not in ids_gerais_pericia_usados
            and atende_prerequisitos(t.get("pre_requisitos"), ctx)
        ]
        tp_ladino = _escolher_por_lista_ou_afinidade(
            candidatos_tp,
            conceito["talentos_recomendados"]["pericia"],
            keywords,
            ids_gerais_pericia_usados,
            rng,
        )
        if tp_ladino:
            ids_gerais_pericia_usados.add(tp_ladino["id"])
            talentos_bonus_slots.append(
                {
                    "nome": tp_ladino["nome"],
                    "origem_regra": "Classe (Ladino — Talento de Perícia 1º Nível)",
                    "pagina": None,
                    "resumo": tp_ladino.get("resumo_beneficio") or tp_ladino.get("descricao", ""),
                    "dados_completos": tp_ladino,
                }
            )

    talentos_gerais_ativos: set[str] = set()
    # Bloqueio com Escudo automático para Guerreiro, Campeão, Druida e Capelão da Guerra
    tem_bloqueio_escudo = classe["id"] in {"guerreiro", "campeao", "druida"} or (
        classe["id"] == "clerigo" and sub_id == "capelao_da_guerra"
    )
    if tem_bloqueio_escudo:
        talentos_gerais_ativos.add("bloqueio_com_escudo")
        ids_gerais_pericia_usados.add("bloqueio_com_escudo")

    extras_gerais = 0
    origens_extras_gerais: list[str] = []
    if heranca["id"] == "heranca_versatil":
        extras_gerais += 1
        origens_extras_gerais.append("Herança Versátil (Humano)")
    if talento_ancestral["id"] == "treinamento_geral":
        extras_gerais += 1
        origens_extras_gerais.append("Talento Ancestral (Treinamento Geral)")

    for i in range(extras_gerais):
        candidatos_tg = [
            t for t in dados.talentos_gerais_pericia.values()
            if t.get("nivel") == 1
            and t.get("categoria") == "geral"
            and t["id"] not in ids_gerais_pericia_usados
            and atende_prerequisitos(t.get("pre_requisitos"), ctx)
        ]
        tg = _escolher_por_lista_ou_afinidade(
            candidatos_tg,
            conceito["talentos_recomendados"]["gerais"],
            keywords,
            ids_gerais_pericia_usados,
            rng,
        )
        if tg:
            ids_gerais_pericia_usados.add(tg["id"])
            talentos_gerais_ativos.add(tg["id"])
            talentos_bonus_slots.append(
                {
                    "nome": tg["nome"],
                    "origem_regra": origens_extras_gerais[i],
                    "pagina": None,
                    "resumo": tg.get("resumo_beneficio") or tg.get("descricao", ""),
                    "dados_completos": tg,
                }
            )

    # ------------------------------------------------------------------
    # 5. Características de Classe de 1º nível (filtrando metas genéricas)
    # ------------------------------------------------------------------
    ignorar_ids = {"ancestralidade_e_biografia", "proficiencias_iniciais"}
    caracteristicas_n1 = [
        c for c in classe["caracteristicas_de_classe"]
        if c.get("nivel") == 1
        and c["id"] not in ignorar_ids
        and not c["id"].startswith("talentos_de_")
    ]

    efeitos = {
        "extras_pericias": 2 if talento_ancestral["id"] == "pericia_natural" else 0,
        "vitalidade": "vitalidade" in talentos_gerais_ativos,
        "veloz": "veloz" in talentos_gerais_ativos,
        "iniciativa_incrivel": "iniciativa_incrivel" in talentos_gerais_ativos,
        "bloqueio_com_escudo": "bloqueio_com_escudo" in talentos_gerais_ativos,
        "elfo_ligeiro": talento_ancestral["id"] == "elfo_ligeiro",
        "ferro_desimpedido": talento_ancestral["id"] == "ferro_desimpedido",
        "dentes_de_navalha": heranca["id"] == "goblin_dentes_de_navalha",
    }

    return {
        "talento_biografia": talento_bio_registro,
        "talento_ancestral": talento_ancestral,
        "talentos_classe": talentos_classe_selecionados,
        "talentos_classe_ids": [t["id"] for t in talentos_classe_selecionados],
        "talentos_bonus": talentos_bonus_slots,
        "talentos_gerais_ids": sorted(talentos_gerais_ativos),
        "caracteristicas_classe_n1": caracteristicas_n1,
        "efeitos": efeitos,
    }
