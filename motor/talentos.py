"""Avaliação de pré-requisitos e seleção de talentos e características de 1º nível."""

from __future__ import annotations

import random
import re
from typing import Any

from .dados import BaseDados
from .util import GRAUS, normalizar, slugify


_CLASSES_CONJURADORAS_PLENAS = {"bardo", "clerigo", "druida", "feiticeiro", "mago"}

_SABERES_ANCESTRAIS: dict[str, tuple[list[str], str]] = {
    "saber_enanico": (["manufatura", "religiao"], "Saber Enânico"),
    "saber_elfico": (["arcanismo", "natureza"], "Saber Élfico"),
    "saber_goblin": (["furtividade", "natureza"], "Saber Goblin"),
    "saber_halfling": (["acrobatismo", "furtividade"], "Saber Halfling"),
}


_ATRIBUTO_NOME_PREREQ = {
    "forca": "for",
    "destreza": "des",
    "constituicao": "con",
    "inteligencia": "int",
    "sabedoria": "sab",
    "carisma": "car",
}


def _norm_escolha_talento(val: Any) -> str | None:
    """Converte uma escolha de talento em ID explícito ou None (quando procedural/aleatória)."""
    if val is None:
        return None
    txt = str(val).strip()
    if not txt or txt.lower() in {"procedural", "aleatorio", "aleatoria", "random"}:
        return None
    return txt


def _norm_lista_escolhas_talentos(val: Any) -> list[str | None]:
    """Normaliza uma lista de slots de escolha de talentos preservando índices procedurais."""
    if val is None or isinstance(val, str):
        unico = _norm_escolha_talento(val)
        return [unico] if unico is not None else []
    if not isinstance(val, (list, tuple)):
        raise ValueError(f"Formato inválido para lista de escolhas de talentos: {val!r}.")
    return [_norm_escolha_talento(item) for item in val]


def _tem_traco_metamagia(talento: dict[str, Any]) -> bool:
    return any(normalizar(x).startswith("metamag") for x in talento.get("tracos", []))


def listar_catalogo_talentos_n1(dados: BaseDados) -> dict[str, Any]:
    """Retorna o catálogo curado de talentos de 1º nível para seleção na interface/API."""
    def _resumir_anc(t: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": t["id"],
            "nome": t["nome"],
            "pre_requisitos": t.get("pre_requisitos"),
            "resumo": t.get("descricao", ""),
        }

    ancestralidade_por_id = {
        aid: [_resumir_anc(t) for t in anc.get("talentos_ancestralidade", []) if t.get("nivel") == 1]
        for aid, anc in dados.ancestralidades.items()
    }
    mesticos = {
        hid: [_resumir_anc(t) for t in lista if t.get("nivel") == 1]
        for hid, lista in dados.talentos_mesticos.items()
    }

    classe_por_id: dict[str, Any] = {}
    for cid, cls in dados.classes.items():
        prog1 = [normalizar(x) for x in cls["tabela_progressao"][0]["caracteristicas"]]
        tem_slot_n1_base = any(x.startswith("talento de ") for x in prog1)
        talentos_n1 = [
            {
                "id": t["id"],
                "nome": t["nome"],
                "pre_requisitos": t.get("pre_requisitos"),
                "tracos": list(t.get("tracos", [])),
                "eh_metamagia": _tem_traco_metamagia(t),
                "resumo": t.get("descricao", ""),
            }
            for t in cls.get("talentos_de_classe", [])
            if t.get("nivel") == 1
        ]
        subclasses_concedido = {
            sub["id"]: slugify(sub["talento_concedido"])
            for sub in cls.get("subclasses", {}).get("opcoes", [])
            if sub.get("talento_concedido")
        }
        classe_por_id[cid] = {
            "tem_slot_n1_base": tem_slot_n1_base,
            "talentos_n1": talentos_n1,
            "subclasses_concedido": subclasses_concedido,
        }

    pericia_n1 = sorted(
        [
            {
                "id": t["id"],
                "nome": t["nome"],
                "pre_requisitos": t.get("pre_requisitos"),
                "resumo": t.get("resumo_beneficio") or t.get("descricao", ""),
            }
            for t in dados.talentos_gerais_pericia.values()
            if t.get("nivel") == 1 and t.get("categoria") == "pericia"
        ],
        key=lambda x: x["nome"],
    )
    gerais_n1 = sorted(
        [
            {
                "id": t["id"],
                "nome": t["nome"],
                "pre_requisitos": t.get("pre_requisitos"),
                "resumo": t.get("resumo_beneficio") or t.get("descricao", ""),
            }
            for t in dados.talentos_gerais_pericia.values()
            if t.get("nivel") == 1 and t.get("categoria") == "geral"
        ],
        key=lambda x: x["nome"],
    )

    return {
        "nivel": 1,
        "ancestralidade_por_id": ancestralidade_por_id,
        "mesticos": mesticos,
        "classe_por_id": classe_por_id,
        "pericia_n1": pericia_n1,
        "gerais_n1": gerais_n1,
    }


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
        if alvo.strip() == "saber":
            return _tem_grau_minimo("treinado", grau_req)
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

    # Padrão: "<Atributo> <valor>" (ex.: "Inteligência 12", "Destreza 14")
    m_atb = re.match(r"^(forca|destreza|constituicao|inteligencia|sabedoria|carisma)\s+(\d+)$", c)
    if m_atb:
        atributos = ctx.get("atributos")
        if not isinstance(atributos, dict):
            return False
        aid = _ATRIBUTO_NOME_PREREQ[m_atb.group(1)]
        return int(atributos.get(aid, 10)) >= int(m_atb.group(2))

    if c == "visao na penumbra":
        return bool(ctx.get("visao_na_penumbra"))

    if c.startswith("musa "):
        musa_req = slugify(c.replace("musa ", ""))
        return classe_id == "bardo" and subclasse_id == musa_req

    if c == "reserva de foco":
        return (
            classe_id in {"bardo", "campeao", "druida", "feiticeiro", "mago"}
            or (classe_id == "clerigo" and subclasse_id == "sacerdote_enclausurado")
            or bool(ctx.get("possui_reserva_foco"))
        )

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
        if classe_id != "clerigo":
            return False
        div = ctx.get("divindade")
        if div:
            dados_ctx: BaseDados | None = ctx.get("dados")
            wid = div.get("arma_favorecida_id")
            if wid == "punho":
                return True
            arma = dados_ctx.armas.get(wid) if (dados_ctx and wid) else None
            return arma is not None and arma.get("categoria") == "Arma Simples"
        return subclasse_id == "capelao_da_guerra"

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
    divindade: dict[str, Any] | None = None,
    atributos: dict[str, int] | None = None,
    escolhas_talentos: dict[str, Any] | None = None,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Seleciona todos os talentos e características aplicáveis ao 1º nível (procedural ou personalizado)."""
    keywords = list(conceito["talentos_recomendados"].get("tracos_ancestralidade_afinidade", []))
    sub_id = subclasse["id"] if subclasse else ""
    visao_na_penumbra = heranca["id"] in {"meio_elfo", "meio_orc"} or any(
        "penumbra" in normalizar(e.get("nome", "")) or "escuro" in normalizar(e.get("nome", ""))
        for e in ancestralidade.get("habilidades_especiais", [])
    )
    ctx = {
        "dados": dados,
        "graus_pericias": graus_pericias,
        "classe_id": classe["id"],
        "subclasse_id": sub_id,
        "ancestralidade_id": ancestralidade["id"],
        "heranca_id": heranca["id"],
        "atributos": atributos,
        "visao_na_penumbra": visao_na_penumbra,
        "conjuracao_plena": classe["id"] in _CLASSES_CONJURADORAS_PLENAS,
        "tendencia_bondosa": "B" in tendencia.upper(),
        "fonte_divina": fonte_divina,
        "divindade": divindade,
    }

    esc_bruta = escolhas_talentos if isinstance(escolhas_talentos, dict) else {}
    modo_tal_req = str(esc_bruta.get("modo") or "").strip().lower()
    usar_personalizado = bool(esc_bruta) and modo_tal_req != "procedural"

    anc_escolha_id = _norm_escolha_talento(esc_bruta.get("ancestralidade_id")) if usar_personalizado else None
    classe_escolhas_req = _norm_lista_escolhas_talentos(esc_bruta.get("classe_ids")) if usar_personalizado else []
    pericia_escolhas_req = _norm_lista_escolhas_talentos(esc_bruta.get("pericia_ids")) if usar_personalizado else []
    gerais_escolhas_req = _norm_lista_escolhas_talentos(esc_bruta.get("gerais_ids")) if usar_personalizado else []

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

    pool_anc_por_id: dict[str, dict[str, Any]] = {}
    for t in pool_anc:
        if t["id"] not in pool_anc_por_id:
            pool_anc_por_id[t["id"]] = t

    if anc_escolha_id is not None:
        cand_anc = pool_anc_por_id.get(anc_escolha_id)
        if cand_anc is None:
            raise ValueError(
                f"Talento de ancestralidade '{anc_escolha_id}' não pertence a "
                f"{ancestralidade['nome']} ({heranca['nome']}) no 1º nível."
            )
        if not atende_prerequisitos(cand_anc.get("pre_requisitos"), ctx):
            raise ValueError(
                f"O personagem não atende ao pré-requisito do talento ancestral '{cand_anc['nome']}': "
                f"{cand_anc.get('pre_requisitos')}."
            )
        talento_ancestral = cand_anc
    else:
        # Deduplica preservando ordem e filtra por pré-requisitos
        candidatos_anc = [
            t for t in pool_anc_por_id.values() if atende_prerequisitos(t.get("pre_requisitos"), ctx)
        ]

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
    # 3. Talentos de Classe N1 (automáticos de subclasse/doutrina/tese + slots selecionáveis)
    # ------------------------------------------------------------------
    talentos_classe_n1_all = [t for t in classe["talentos_de_classe"] if t.get("nivel") == 1]
    talentos_classe_por_id = {t["id"]: t for t in talentos_classe_n1_all}
    escolhidos_classe_ids: set[str] = set()
    talentos_classe_selecionados: list[dict[str, Any]] = []

    def adicionar_classe_talento(tid: str | None, origem: str) -> bool:
        if not tid:
            return False
        t = talentos_classe_por_id.get(tid)
        if t and tid not in escolhidos_classe_ids:
            escolhidos_classe_ids.add(tid)
            talentos_classe_selecionados.append(dict(t, origem=origem))
            if tid in {"iniciado_no_dominio", "golpe_de_ki", "disparada_de_ki"}:
                ctx["possui_reserva_foco"] = True
            return True
        return False

    # Concedidos automaticamente pela subclasse / doutrina / tese no 1º nível
    if subclasse and "talento_concedido" in subclasse:
        adicionar_classe_talento(
            slugify(subclasse["talento_concedido"]),
            f"Subclasse ({subclasse['nome']})",
        )
    if classe["id"] == "clerigo":
        if sub_id == "sacerdote_enclausurado":
            adicionar_classe_talento("iniciado_no_dominio", "Doutrina (Primeira Doutrina)")
        elif sub_id == "capelao_da_guerra":
            wid_div = divindade.get("arma_favorecida_id") if divindade else None
            arma_div = dados.armas.get(wid_div) if wid_div else None
            arma_eh_simples = (
                divindade is None
                or wid_div == "punho"
                or (arma_div is not None and arma_div.get("categoria") == "Arma Simples")
            )
            if arma_eh_simples:
                adicionar_classe_talento("simplicidade_mortal", "Doutrina (Primeira Doutrina)")
    if classe["id"] == "mago" and tese_arcana_id == "sintonizacao_com_familiar_aprimorada":
        adicionar_classe_talento("familiar", "Tese Arcana (Sintonização com Familiar Aprimorada)")

    # Monta a fila exata de slots selecionáveis de classe no 1º nível
    slots_classe_cfg: list[dict[str, Any]] = []
    prog1 = [normalizar(x) for x in classe["tabela_progressao"][0]["caracteristicas"]]
    tem_talento_classe_livre = any(x.startswith("talento de ") for x in prog1) or (
        classe["id"] == "mago" and sub_id == "universalista"
    )
    if tem_talento_classe_livre:
        slots_classe_cfg.append({"origem": f"Classe ({classe['nome']} 1º Nível)", "apenas_metamagia": False})
    if (
        classe["id"] == "barbaro"
        and subclasse
        and isinstance(subclasse.get("habilidade_instinto"), dict)
        and subclasse["habilidade_instinto"].get("talento_bonus_1_nivel")
    ):
        slots_classe_cfg.append({"origem": f"Subclasse ({subclasse['nome']})", "apenas_metamagia": False})
    if classe["id"] == "mago" and tese_arcana_id == "experimentacao_metamagica":
        slots_classe_cfg.append({"origem": "Tese Arcana (Experimentação Metamágica)", "apenas_metamagia": True})
    if talento_ancestral["id"] == "ambicao_natural":
        slots_classe_cfg.append({"origem": "Talento Ancestral (Ambição Natural)", "apenas_metamagia": False})

    manuais_classe_explic = [x for x in classe_escolhas_req if x is not None]
    if manuais_classe_explic and not slots_classe_cfg:
        raise ValueError(
            f"A classe {classe['nome']} não possui talento de classe selecionável no 1º nível "
            f"(salvo com Ambição Natural ou subclasse/tese específica)."
        )
    for idx_extra in range(len(slots_classe_cfg), len(classe_escolhas_req)):
        if classe_escolhas_req[idx_extra] is not None:
            raise ValueError(
                f"Esta combinação libera apenas {len(slots_classe_cfg)} talento(s) de classe selecionável(is) "
                f"no 1º nível (slot extra #{idx_extra + 1} não está disponível)."
            )

    # Pré-reserva escolhas manuais válidas para que eventuais slots deixados em procedural não colidam com elas
    reservados_manuais_classe: set[str] = {
        tid
        for idx, tid in enumerate(classe_escolhas_req[: len(slots_classe_cfg)])
        if tid is not None and tid in talentos_classe_por_id
    }
    classe_selecionaveis_aplicados: list[dict[str, str]] = []

    for idx_slot, slot_cfg in enumerate(slots_classe_cfg):
        escolha_cid = classe_escolhas_req[idx_slot] if idx_slot < len(classe_escolhas_req) else None
        apenas_meta = bool(slot_cfg["apenas_metamagia"])
        origem_slot = str(slot_cfg["origem"])
        if escolha_cid is not None:
            cand_c = talentos_classe_por_id.get(escolha_cid)
            if cand_c is None:
                raise ValueError(
                    f"Talento de classe '{escolha_cid}' não existe para {classe['nome']} no 1º nível."
                )
            if escolha_cid in escolhidos_classe_ids:
                raise ValueError(
                    f"Talento de classe '{cand_c['nome']}' já foi concedido ou selecionado em outro slot."
                )
            if apenas_meta and not _tem_traco_metamagia(cand_c):
                raise ValueError(
                    f"O slot de Experimentação Metamágica exige um talento com traço Metamágico ('{cand_c['nome']}' não possui)."
                )
            if not apenas_meta and not atende_prerequisitos(cand_c.get("pre_requisitos"), ctx):
                raise ValueError(
                    f"O personagem não atende ao pré-requisito do talento '{cand_c['nome']}': "
                    f"{cand_c.get('pre_requisitos')}."
                )
            adicionar_classe_talento(cand_c["id"], origem_slot)
            classe_selecionaveis_aplicados.append({"id": cand_c["id"], "origem": origem_slot})
        else:
            evitar_ids = escolhidos_classe_ids | (reservados_manuais_classe - escolhidos_classe_ids)
            if apenas_meta:
                validos_slot = [
                    t for t in talentos_classe_n1_all
                    if t["id"] not in evitar_ids and _tem_traco_metamagia(t)
                ]
            else:
                validos_slot = [
                    t for t in talentos_classe_n1_all
                    if t["id"] not in evitar_ids and atende_prerequisitos(t.get("pre_requisitos"), ctx)
                ]
            escolhido_c = _escolher_por_lista_ou_afinidade(
                validos_slot,
                conceito["talentos_recomendados"]["classe_nivel_1"],
                keywords,
                evitar_ids,
                rng,
            )
            if escolhido_c and adicionar_classe_talento(escolhido_c["id"], origem_slot):
                classe_selecionaveis_aplicados.append({"id": escolhido_c["id"], "origem": origem_slot})

    # ------------------------------------------------------------------
    # 4. Talentos Extras (Ladino Perícia N1 + Gerais automáticos / Versátil / Treinamento Geral)
    # ------------------------------------------------------------------
    talentos_bonus_slots: list[dict[str, Any]] = []
    ids_gerais_pericia_usados: set[str] = {talento_bio_registro["id"]}
    pericia_selecionaveis_aplicados: list[dict[str, str]] = []
    gerais_selecionaveis_aplicados: list[dict[str, str]] = []

    slots_pericia_n1 = 1 if classe["id"] == "ladino" else 0
    if any(x is not None for x in pericia_escolhas_req) and slots_pericia_n1 == 0:
        raise ValueError(
            "No 1º nível, apenas o Ladino libera talento de perícia adicional selecionável além da Biografia."
        )
    if len(pericia_escolhas_req) > slots_pericia_n1 and any(x is not None for x in pericia_escolhas_req[slots_pericia_n1:]):
        raise ValueError("Há apenas 1 slot de talento de perícia adicional disponível no 1º nível.")

    if slots_pericia_n1 == 1:
        origem_per = "Classe (Ladino — Talento de Perícia 1º Nível)"
        escolha_pid = pericia_escolhas_req[0] if pericia_escolhas_req else None
        if escolha_pid is not None:
            cand_p = dados.talentos_gerais_pericia.get(escolha_pid)
            if not cand_p or cand_p.get("nivel") != 1 or cand_p.get("categoria") != "pericia":
                raise ValueError(
                    f"Talento de perícia '{escolha_pid}' não é um talento de perícia válido de 1º nível."
                )
            if escolha_pid in ids_gerais_pericia_usados:
                raise ValueError(
                    f"Talento de perícia '{cand_p['nome']}' já foi concedido pela Biografia ({biografia['nome']})."
                )
            if not atende_prerequisitos(cand_p.get("pre_requisitos"), ctx):
                raise ValueError(
                    f"O personagem não atende ao pré-requisito do talento '{cand_p['nome']}': "
                    f"{cand_p.get('pre_requisitos')}."
                )
            tp_ladino = cand_p
        else:
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
            pericia_selecionaveis_aplicados.append({"id": tp_ladino["id"], "origem": origem_per})
            talentos_bonus_slots.append(
                {
                    "nome": tp_ladino["nome"],
                    "categoria": "pericia",
                    "origem_regra": origem_per,
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

    if talento_ancestral["id"] == "cavaleiro_brusco" and "cavalgar" not in ids_gerais_pericia_usados:
        tal_cav = dados.talentos_gerais_pericia.get("cavalgar")
        if tal_cav:
            ids_gerais_pericia_usados.add("cavalgar")
            talentos_gerais_ativos.add("cavalgar")
            talentos_bonus_slots.append(
                {
                    "nome": tal_cav["nome"],
                    "categoria": "geral",
                    "origem_regra": "Talento Ancestral (Cavaleiro Brusco)",
                    "pagina": None,
                    "resumo": tal_cav.get("resumo_beneficio") or tal_cav.get("descricao", ""),
                    "dados_completos": tal_cav,
                }
            )

    origens_extras_gerais: list[str] = []
    if heranca["id"] == "heranca_versatil":
        origens_extras_gerais.append("Herança Versátil (Humano)")
    if talento_ancestral["id"] == "treinamento_geral":
        origens_extras_gerais.append("Talento Ancestral (Treinamento Geral)")

    manuais_gerais_explic = [x for x in gerais_escolhas_req if x is not None]
    if manuais_gerais_explic and not origens_extras_gerais:
        raise ValueError(
            "Talentos gerais só são liberados no 3º nível (ou no 1º nível com Herança Versátil / Treinamento Geral)."
        )
    for idx_extra in range(len(origens_extras_gerais), len(gerais_escolhas_req)):
        if gerais_escolhas_req[idx_extra] is not None:
            raise ValueError(
                f"Esta combinação libera apenas {len(origens_extras_gerais)} talento(s) geral(is) no 1º nível."
            )

    reservados_manuais_gerais: set[str] = {
        tid
        for tid in gerais_escolhas_req[: len(origens_extras_gerais)]
        if tid is not None and tid in dados.talentos_gerais_pericia
    }

    for i, origem_geral in enumerate(origens_extras_gerais):
        escolha_gid = gerais_escolhas_req[i] if i < len(gerais_escolhas_req) else None
        if escolha_gid is not None:
            cand_g = dados.talentos_gerais_pericia.get(escolha_gid)
            if not cand_g or cand_g.get("nivel") != 1 or cand_g.get("categoria") != "geral":
                raise ValueError(
                    f"Talento geral '{escolha_gid}' não é um talento geral válido de 1º nível."
                )
            if escolha_gid in ids_gerais_pericia_usados:
                raise ValueError(
                    f"Talento geral '{cand_g['nome']}' já foi concedido automaticamente ou selecionado em outro slot."
                )
            if not atende_prerequisitos(cand_g.get("pre_requisitos"), ctx):
                raise ValueError(
                    f"O personagem não atende ao pré-requisito do talento '{cand_g['nome']}': "
                    f"{cand_g.get('pre_requisitos')}."
                )
            tg = cand_g
        else:
            evitar_g = ids_gerais_pericia_usados | (reservados_manuais_gerais - ids_gerais_pericia_usados)
            candidatos_tg = [
                t for t in dados.talentos_gerais_pericia.values()
                if t.get("nivel") == 1
                and t.get("categoria") == "geral"
                and t["id"] not in evitar_g
                and atende_prerequisitos(t.get("pre_requisitos"), ctx)
            ]
            tg = _escolher_por_lista_ou_afinidade(
                candidatos_tg,
                conceito["talentos_recomendados"]["gerais"],
                keywords,
                evitar_g,
                rng,
            )
        if tg:
            ids_gerais_pericia_usados.add(tg["id"])
            talentos_gerais_ativos.add(tg["id"])
            gerais_selecionaveis_aplicados.append({"id": tg["id"], "origem": origem_geral})
            talentos_bonus_slots.append(
                {
                    "nome": tg["nome"],
                    "categoria": "geral",
                    "origem_regra": origem_geral,
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

    regras_morr = dados.regras_especificas.get("morrendo_e_testes_de_recuperacao", {})
    limite_morr_padrao = int(regras_morr.get("limite_morrendo_padrao", 4))
    duro_de_matar = "duro_de_matar" in talentos_gerais_ativos
    vitalidade_ativo = "vitalidade" in talentos_gerais_ativos

    wid_fav_div = divindade.get("arma_favorecida_id") if divindade else None
    arma_fav_obj = dados.armas.get(wid_fav_div) if wid_fav_div else None
    arma_deificada_ativa = classe["id"] == "campeao" and (
        wid_fav_div == "punho"
        or (arma_fav_obj is not None and arma_fav_obj.get("categoria") == "Arma Simples")
    )

    pericias_anc_fixas, nome_saber_anc = _SABERES_ANCESTRAIS.get(talento_ancestral["id"], ([], None))
    saber_anc: tuple[str, str] | None = (
        (nome_saber_anc, f"Talento Ancestral ({talento_ancestral['nome']})")
        if nome_saber_anc
        else None
    )
    if talento_ancestral["id"] == "obsessao_gnomica":
        saber_anc = (
            conceito.get("saber_sugerido") or "Saber Gnômico",
            "Talento Ancestral (Obsessão Gnômica)",
        )

    efeitos = {
        "extras_pericias": (2 if talento_ancestral["id"] == "pericia_natural" else 0)
        + (1 if talento_ancestral["id"] == "longevidade_ancestral" else 0),
        "pericias_ancestrais_fixas": pericias_anc_fixas,
        "saber_ancestral": saber_anc,
        "vitalidade": vitalidade_ativo,
        "veloz": "veloz" in talentos_gerais_ativos,
        "iniciativa_incrivel": "iniciativa_incrivel" in talentos_gerais_ativos,
        "bloqueio_com_escudo": "bloqueio_com_escudo" in talentos_gerais_ativos,
        "carregador_robusto": "carregador_robusto" in ids_gerais_pericia_usados,
        "duro_de_matar": duro_de_matar,
        "perspicacia_astuta": "perspicacia_astuta" in talentos_gerais_ativos,
        "proficiencia_com_armaduras": "proficiencia_com_armaduras" in talentos_gerais_ativos,
        "proficiencia_com_armas": "proficiencia_com_armas" in talentos_gerais_ativos,
        "simplicidade_mortal": ("simplicidade_mortal" in escolhidos_classe_ids) or arma_deificada_ativa,
        "arma_deificada": arma_deificada_ativa,
        "limite_morrendo": 5 if duro_de_matar else limite_morr_padrao,
        "cd_recuperacao_base": 9 if vitalidade_ativo else int(regras_morr.get("cd_recuperacao_base_padrao", 10)),
        "elfo_ligeiro": talento_ancestral["id"] == "elfo_ligeiro",
        "ferro_desimpedido": talento_ancestral["id"] == "ferro_desimpedido",
        "visao_orquica": talento_ancestral["id"] == "visao_orquica",
        "dentes_de_navalha": heranca["id"] == "goblin_dentes_de_navalha",
        "talento_ancestral_id": talento_ancestral["id"],
    }

    escolhas_resumo = {
        "modo": "personalizado"
        if any(
            [
                anc_escolha_id is not None,
                any(x is not None for x in classe_escolhas_req),
                any(x is not None for x in pericia_escolhas_req),
                any(x is not None for x in gerais_escolhas_req),
            ]
        )
        else "procedural",
        "ancestralidade_id": talento_ancestral["id"],
        "ancestralidade_procedural": anc_escolha_id is None,
        "classe_ids": [item["id"] for item in classe_selecionaveis_aplicados],
        "classe_origens": [item["origem"] for item in classe_selecionaveis_aplicados],
        "pericia_ids": [item["id"] for item in pericia_selecionaveis_aplicados],
        "gerais_ids": [item["id"] for item in gerais_selecionaveis_aplicados],
        "slots_disponiveis": {
            "ancestralidade": 1,
            "classe": len(slots_classe_cfg),
            "pericia": slots_pericia_n1,
            "gerais": len(origens_extras_gerais),
        },
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
        "escolhas_talentos": escolhas_resumo,
    }
