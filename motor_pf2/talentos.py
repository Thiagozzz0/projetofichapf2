"""Avaliação de pré-requisitos e seleção de talentos e características de 1º nível."""

from __future__ import annotations

import random
import re
from typing import Any

from .dados import BaseDados
from .magias import CLASSES_CONJURACAO_PLENA as _CLASSES_CONJURADORAS_PLENAS
from .util import GRAUS, normalizar, slugify

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


def listar_catalogo_talentos(dados: BaseDados, nivel_maximo: int = 5) -> dict[str, Any]:
    """Retorna o catálogo curado de talentos (1º ao `nivel_maximo`) para seleção na interface/API."""
    nivel_lim = max(1, int(nivel_maximo))

    def _resumir_anc(t: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": t["id"],
            "nome": t["nome"],
            "nivel": int(t.get("nivel", 1)),
            "pre_requisitos": t.get("pre_requisitos"),
            "resumo": t.get("descricao", ""),
        }

    def _agrupar_por_nivel(lista: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        agrupado: dict[str, list[dict[str, Any]]] = {}
        for item in lista:
            chave = str(int(item.get("nivel", 1)))
            agrupado.setdefault(chave, []).append(item)
        return agrupado

    ancestralidade_por_id: dict[str, list[dict[str, Any]]] = {}
    ancestralidade_por_nivel: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for aid, anc in dados.ancestralidades.items():
        lista_ate = [
            _resumir_anc(t)
            for t in anc.get("talentos_ancestralidade", [])
            if int(t.get("nivel", 1)) <= nivel_lim
        ]
        ancestralidade_por_id[aid] = [t for t in lista_ate if t["nivel"] == 1]
        ancestralidade_por_nivel[aid] = _agrupar_por_nivel(lista_ate)

    mesticos: dict[str, list[dict[str, Any]]] = {}
    mesticos_por_nivel: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for hid, lista in dados.talentos_mesticos.items():
        lista_ate = [_resumir_anc(t) for t in lista if int(t.get("nivel", 1)) <= nivel_lim]
        mesticos[hid] = [t for t in lista_ate if t["nivel"] == 1]
        mesticos_por_nivel[hid] = _agrupar_por_nivel(lista_ate)

    classe_por_id: dict[str, Any] = {}
    for cid, cls in dados.classes.items():
        nome_cls_norm = normalizar(cls["nome"])
        marcador_slot_cls = f"talento de {nome_cls_norm}"
        prog1 = [normalizar(x) for x in cls["tabela_progressao"][0]["caracteristicas"]]
        tem_slot_n1_base = any(x == marcador_slot_cls for x in prog1)
        niveis_slot_classe = [
            int(row["nivel"])
            for row in cls.get("tabela_progressao", [])
            if int(row.get("nivel", 1)) <= nivel_lim
            and any(normalizar(x) == marcador_slot_cls for x in row.get("caracteristicas", []))
        ]
        talentos_ate_max = [
            {
                "id": t["id"],
                "nome": t["nome"],
                "nivel": int(t.get("nivel", 1)),
                "pre_requisitos": t.get("pre_requisitos"),
                "tracos": list(t.get("tracos", [])),
                "eh_metamagia": _tem_traco_metamagia(t),
                "resumo": t.get("descricao", ""),
            }
            for t in cls.get("talentos_de_classe", [])
            if int(t.get("nivel", 1)) <= nivel_lim
        ]
        talentos_n1 = [t for t in talentos_ate_max if t["nivel"] == 1]
        subclasses_concedido = {
            sub["id"]: slugify(sub["talento_concedido"])
            for sub in cls.get("subclasses", {}).get("opcoes", [])
            if sub.get("talento_concedido")
        }
        classe_por_id[cid] = {
            "tem_slot_n1_base": tem_slot_n1_base,
            "niveis_slot_classe": niveis_slot_classe,
            "talentos_n1": talentos_n1,
            "talentos_por_nivel": _agrupar_por_nivel(talentos_ate_max),
            "talentos_ate_nivel_maximo": talentos_ate_max,
            "subclasses_concedido": subclasses_concedido,
        }

    def _resumir_geral_pericia(t: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": t["id"],
            "nome": t["nome"],
            "nivel": int(t.get("nivel", 1)),
            "pre_requisitos": t.get("pre_requisitos"),
            "resumo": t.get("resumo_beneficio") or t.get("descricao", ""),
        }

    pericia_ate_max = sorted(
        [
            _resumir_geral_pericia(t)
            for t in dados.talentos_gerais_pericia.values()
            if int(t.get("nivel", 1)) <= nivel_lim and t.get("categoria") == "pericia"
        ],
        key=lambda x: (x["nivel"], x["nome"]),
    )
    gerais_ate_max = sorted(
        [
            _resumir_geral_pericia(t)
            for t in dados.talentos_gerais_pericia.values()
            if int(t.get("nivel", 1)) <= nivel_lim and t.get("categoria") == "geral"
        ],
        key=lambda x: (x["nivel"], x["nome"]),
    )
    pericia_n1 = sorted([t for t in pericia_ate_max if t["nivel"] == 1], key=lambda x: x["nome"])
    gerais_n1 = sorted([t for t in gerais_ate_max if t["nivel"] == 1], key=lambda x: x["nome"])

    return {
        "nivel": 1,
        "nivel_maximo": nivel_lim,
        "ancestralidade_por_id": ancestralidade_por_id,
        "ancestralidade_por_nivel": ancestralidade_por_nivel,
        "mesticos": mesticos,
        "mesticos_por_nivel": mesticos_por_nivel,
        "classe_por_id": classe_por_id,
        "pericia_n1": pericia_n1,
        "pericia_por_nivel": _agrupar_por_nivel(pericia_ate_max),
        "pericia_ate_nivel_maximo": pericia_ate_max,
        "gerais_n1": gerais_n1,
        "gerais_por_nivel": _agrupar_por_nivel(gerais_ate_max),
        "gerais_ate_nivel_maximo": gerais_ate_max,
    }


def listar_catalogo_talentos_n1(dados: BaseDados) -> dict[str, Any]:
    """Alias retrocompatível para o catálogo de talentos (cobre até o 5º nível)."""
    return listar_catalogo_talentos(dados, nivel_maximo=5)


def atende_prerequisitos(texto_prereq: str | None, ctx: dict[str, Any]) -> bool:
    """Avalia expressões comuns de pré-requisitos de talentos (níveis 1 a 5) do PF2E."""
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

    # Preserva vírgulas internas de listas de perícias (ex.: "especialista em Arcanismo, Natureza, Ocultismo ou Religião")
    brutas = [c.strip() for c in t.split(",") if c.strip()]
    clausulas: list[str] = []
    _re_grau = re.compile(r"^(treinado|especialista|mestre|lendario) em ")
    _pericias_ou_nomes = {
        "arcanismo", "natureza", "ocultismo", "religiao", "atletismo", "acrobatismo",
        "furtividade", "ladroagem", "diplomacia", "intimidacao", "dissimulacao",
        "medicina", "manufatura", "sociedade", "sobrevivencia", "atuacao",
    }
    for parte in brutas:
        tokens_ou = [x.strip() for x in parte.split(" ou ") if x.strip()]
        eh_cont_pericia = (
            bool(clausulas)
            and bool(_re_grau.match(clausulas[-1]))
            and all(tok in _pericias_ou_nomes for tok in tokens_ou)
        )
        if eh_cont_pericia:
            clausulas[-1] = f"{clausulas[-1]}, {parte}"
        else:
            clausulas.append(parte)

    for clausula in clausulas:
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

    # Alternativas explícitas ("A ou B")
    if " ou " in c:
        return any(
            _avaliar_clausula(alt.strip(), graus, classe_id, subclasse_id, conjuracao_plena, ctx)
            for alt in c.split(" ou ")
            if alt.strip()
        )

    # Padrão: "<Atributo> <valor>" (ex.: "Inteligência 12", "Destreza 14")
    m_atb = re.match(r"^(forca|destreza|constituicao|inteligencia|sabedoria|carisma)\s+(\d+)$", c)
    if m_atb:
        atributos = ctx.get("atributos")
        if not isinstance(atributos, dict):
            return False
        aid = _ATRIBUTO_NOME_PREREQ[m_atb.group(1)]
        return int(atributos.get(aid, 10)) >= int(m_atb.group(2))

    # Capacidade de conjurar magias de N-ésimo círculo (ex.: "capacidade de conjurar magias de 3º nível")
    m_conj = re.match(r"^capacidade de conjurar magias de (\d+)o nivel$", c)
    if m_conj:
        circ_req = int(m_conj.group(1))
        return conjuracao_plena and int(ctx.get("nivel", 1)) >= (2 * circ_req - 1)

    possuidos_ids: set[str] = ctx.get("talentos_possuidos_ids", set())
    possuidos_nomes: set[str] = ctx.get("talentos_possuidos_nomes", set())

    if c == "visao na penumbra":
        return bool(ctx.get("visao_na_penumbra"))

    if c == "visao no escuro":
        return bool(ctx.get("visao_no_escuro"))

    if c == "visao agucada":
        return "visao_agucada" in possuidos_ids

    if c.startswith("musa "):
        musa_req = slugify(c.replace("musa ", ""))
        return classe_id == "bardo" and subclasse_id == musa_req

    if c.startswith("esquema de "):
        esq_req = slugify(c.replace("esquema de ", ""))
        return classe_id == "ladino" and subclasse_id == esq_req

    if c in ("reserva de foco", "reservatorio de foco"):
        return (
            classe_id in {"bardo", "campeao", "druida", "feiticeiro", "mago"}
            or (classe_id == "clerigo" and subclasse_id == "sacerdote_enclausurado")
            or bool(ctx.get("possui_reserva_foco"))
        )

    if c.startswith("causa de "):
        causa_req = slugify(c.replace("causa de ", ""))
        return classe_id == "campeao" and subclasse_id == causa_req

    if c == "principios do bem":
        return classe_id == "campeao" and ctx.get("tendencia_bondosa", True)

    if "imposicao de maos" in c:
        return classe_id == "campeao" and ctx.get("tendencia_bondosa", True)

    if c.startswith("ordem d"):
        # ex.: "ordem dos animais", "ordem da folha", "ordem da tempestade", "ordem dos selvagens"
        for nome_sub in ("animais", "folha", "tempestade", "selvagens"):
            if nome_sub in c:
                return classe_id == "druida" and subclasse_id == nome_sub
        return False

    if c == "mago universalista":
        return classe_id == "mago" and subclasse_id == "universalista"

    if c == "elo arcano":
        return classe_id == "mago"

    if c == "escola arcana":
        return classe_id == "mago" and subclasse_id != "universalista"

    if c.startswith("linhagem que concede magias "):
        trad_map = {
            "arcanas": "arcana",
            "divinas": "divina",
            "ocultistas": "ocultista",
            "primais": "primal",
        }
        alvo_trad = trad_map.get(c.replace("linhagem que concede magias ", "").strip())
        return classe_id == "feiticeiro" and bool(alvo_trad) and ctx.get("tradicao") == alvo_trad

    if c == "tendencia bondosa":
        return ctx.get("tendencia_bondosa", True)

    if c == "tendencia maligna":
        return "M" in str(ctx.get("tendencia", "")).upper()

    if c == "fonte de cura":
        return classe_id == "clerigo" and ctx.get("fonte_divina", "cura") == "cura"

    if c == "fonte de ferimento":
        return classe_id == "clerigo" and ctx.get("fonte_divina", "cura") == "ferimento"

    if "divindade que permite que clerigos escolham ambas as fontes" in c:
        div = ctx.get("divindade")
        return bool(div) and len(div.get("fontes_divinas") or []) > 1

    if c == "um familiar":
        return (
            bool({"familiar", "familiar_alquimico", "familiar_leshy"} & possuidos_ids)
            or (classe_id == "druida" and subclasse_id == "folha")
        )

    if c == "companheiro animal":
        return (
            "companheiro_animal" in possuidos_ids
            or (classe_id == "druida" and subclasse_id == "animais")
        )

    if c == "magias de ki":
        return bool({"golpe_de_ki", "disparada_de_ki"} & possuidos_ids)

    if "certeza nessa pericia" in c:
        return "certeza" in possuidos_ids

    if "magia inata de heranca/talento gnomico" in c:
        return (
            ctx.get("ancestralidade_id") == "gnomo"
            and ctx.get("heranca_id") in ("gnomo_tocado_pelas_fadas", "gnomo_manancial")
            and (bool(ctx.get("possui_reserva_foco")) or classe_id in {"bardo", "campeao", "druida", "feiticeiro", "mago"})
        )

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

    # Talento prévio possuído pelo personagem (ex.: "Familiaridade com Armas Élficas", "Aspecto Selvagem", "Gracejos da Corte")
    if slugify(c) in possuidos_ids or c in possuidos_nomes:
        return True

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
    nivel: int = 1,
    escolhas_talentos: dict[str, Any] | None = None,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Seleciona todos os talentos e características aplicáveis até `nivel` (procedural ou personalizado)."""
    nivel_alvo = max(1, int(nivel))
    keywords = list(conceito["talentos_recomendados"].get("tracos_ancestralidade_afinidade", []))
    sub_id = subclasse["id"] if subclasse else ""
    visao_na_penumbra = heranca["id"] in {"meio_elfo", "meio_orc"} or any(
        "penumbra" in normalizar(e.get("nome", "")) or "escuro" in normalizar(e.get("nome", ""))
        for e in ancestralidade.get("habilidades_especiais", [])
    )
    visao_no_escuro = any(
        "escuro" in normalizar(e.get("nome", ""))
        for e in ancestralidade.get("habilidades_especiais", [])
    ) or any(
        "escuro" in normalizar(s) for s in (heranca.get("sentidos_concedidos") or [])
    )
    prof_mag = classe["proficiencias_iniciais"].get("magias") or {}
    tradicao_cls = (
        subclasse.get("tradicao_magica")
        if (subclasse and prof_mag.get("tradicao") == "conforme_linhagem")
        else prof_mag.get("tradicao")
    )
    talentos_possuidos_ids: set[str] = set()
    talentos_possuidos_nomes: set[str] = set()

    def _registrar_talento_possuido(t_obj: dict[str, Any] | None) -> None:
        if not t_obj:
            return
        if t_obj.get("id"):
            talentos_possuidos_ids.add(str(t_obj["id"]))
        if t_obj.get("nome"):
            talentos_possuidos_nomes.add(normalizar(t_obj["nome"]))

    ctx = {
        "dados": dados,
        "nivel": nivel_alvo,
        "graus_pericias": graus_pericias,
        "classe_id": classe["id"],
        "subclasse_id": sub_id,
        "ancestralidade_id": ancestralidade["id"],
        "heranca_id": heranca["id"],
        "atributos": atributos,
        "visao_na_penumbra": visao_na_penumbra,
        "visao_no_escuro": visao_no_escuro,
        "conjuracao_plena": classe["id"] in _CLASSES_CONJURADORAS_PLENAS,
        "tradicao": tradicao_cls,
        "tendencia": tendencia,
        "tendencia_bondosa": "B" in tendencia.upper(),
        "fonte_divina": fonte_divina,
        "divindade": divindade,
        "talentos_possuidos_ids": talentos_possuidos_ids,
        "talentos_possuidos_nomes": talentos_possuidos_nomes,
    }

    esc_bruta = escolhas_talentos if isinstance(escolhas_talentos, dict) else {}
    modo_tal_req = str(esc_bruta.get("modo") or "").strip().lower()
    usar_personalizado = bool(esc_bruta) and modo_tal_req != "procedural"

    anc_escolha_id = _norm_escolha_talento(esc_bruta.get("ancestralidade_id")) if usar_personalizado else None
    anc_n5_escolha_id = _norm_escolha_talento(esc_bruta.get("ancestralidade_n5_id")) if usar_personalizado else None
    anc_adotada_req_id = _norm_escolha_talento(esc_bruta.get("ancestralidade_adotada_id")) if usar_personalizado else None
    tal_adotado_req_id = _norm_escolha_talento(esc_bruta.get("talento_ancestral_adotado_id")) if usar_personalizado else None
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
    _registrar_talento_possuido({"id": talento_bio_registro["id"], "nome": talento_bio_registro["nome"]})

    # ------------------------------------------------------------------
    # 2. Talento de Ancestralidade (1º nível)
    # ------------------------------------------------------------------
    def _coletar_pool_ancestral(nivel_lim_anc: int) -> dict[str, dict[str, Any]]:
        lista_a = [
            t for t in ancestralidade.get("talentos_ancestralidade", [])
            if int(t.get("nivel", 1)) <= nivel_lim_anc
        ]
        if heranca["id"] == "meio_elfo":
            elfo = dados.ancestralidades["elfo"]
            lista_a.extend(
                t for t in elfo.get("talentos_ancestralidade", [])
                if int(t.get("nivel", 1)) <= nivel_lim_anc
            )
            lista_a.extend(
                t for t in dados.talentos_mesticos.get("meio_elfo", [])
                if int(t.get("nivel", 1)) <= nivel_lim_anc
            )
        elif heranca["id"] == "meio_orc":
            lista_a.extend(
                t for t in dados.talentos_mesticos.get("meio_orc", [])
                if int(t.get("nivel", 1)) <= nivel_lim_anc
            )
        por_id: dict[str, dict[str, Any]] = {}
        for t in lista_a:
            if t["id"] not in por_id:
                por_id[t["id"]] = t
        return por_id

    pool_anc_por_id = _coletar_pool_ancestral(1)

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

    _registrar_talento_possuido(talento_ancestral)
    if talento_ancestral["id"] == "visao_orquica":
        ctx["visao_no_escuro"] = True
    talentos_ancestrais: list[dict[str, Any]] = [dict(talento_ancestral, nivel_slot=1)]

    # ------------------------------------------------------------------
    # 3. Talentos de Classe (N1 + N2/N4 quando nivel >= 2)
    # ------------------------------------------------------------------
    talentos_classe_todos = [
        t for t in classe["talentos_de_classe"] if int(t.get("nivel", 1)) <= nivel_alvo
    ]
    talentos_classe_por_id = {t["id"]: t for t in talentos_classe_todos}
    escolhidos_classe_ids: set[str] = set()
    talentos_classe_selecionados: list[dict[str, Any]] = []

    def adicionar_classe_talento(tid: str | None, origem: str, nivel_slot: int = 1) -> bool:
        if not tid:
            return False
        t = talentos_classe_por_id.get(tid)
        if t and tid not in escolhidos_classe_ids:
            escolhidos_classe_ids.add(tid)
            talentos_classe_selecionados.append(dict(t, origem=origem, nivel_slot=nivel_slot))
            _registrar_talento_possuido(t)
            if tid in {
                "iniciado_no_dominio",
                "dominio_de_divindade",
                "golpe_de_ki",
                "disparada_de_ki",
                "integridade_corporal",
                "aspecto_selvagem",
                "mao_do_aprendiz",
            }:
                ctx["possui_reserva_foco"] = True
            return True
        return False

    # Concedidos automaticamente pela subclasse / doutrina / tese no 1º nível
    if subclasse and "talento_concedido" in subclasse:
        adicionar_classe_talento(
            slugify(subclasse["talento_concedido"]),
            f"Subclasse ({subclasse['nome']})",
            nivel_slot=1,
        )
    if classe["id"] == "clerigo":
        if sub_id == "sacerdote_enclausurado":
            adicionar_classe_talento("iniciado_no_dominio", "Doutrina (Primeira Doutrina)", nivel_slot=1)
        elif sub_id == "capelao_da_guerra":
            wid_div = divindade.get("arma_favorecida_id") if divindade else None
            arma_div = dados.armas.get(wid_div) if wid_div else None
            arma_eh_simples = (
                divindade is None
                or wid_div == "punho"
                or (arma_div is not None and arma_div.get("categoria") == "Arma Simples")
            )
            if arma_eh_simples:
                adicionar_classe_talento("simplicidade_mortal", "Doutrina (Primeira Doutrina)", nivel_slot=1)
    if classe["id"] == "mago" and tese_arcana_id == "sintonizacao_com_familiar_aprimorada":
        adicionar_classe_talento("familiar", "Tese Arcana (Sintonização com Familiar Aprimorada)", nivel_slot=1)

    # Monta a fila exata de slots selecionáveis de classe (N1 + níveis pares 2..nivel_alvo)
    slots_classe_cfg: list[dict[str, Any]] = []
    prog1 = [normalizar(x) for x in classe["tabela_progressao"][0]["caracteristicas"]]
    tem_talento_classe_livre = any(x.startswith("talento de ") for x in prog1) or (
        classe["id"] == "mago" and sub_id == "universalista"
    )
    if tem_talento_classe_livre:
        slots_classe_cfg.append({"origem": f"Classe ({classe['nome']} 1º Nível)", "apenas_metamagia": False, "nivel": 1})
    if (
        classe["id"] == "barbaro"
        and subclasse
        and isinstance(subclasse.get("habilidade_instinto"), dict)
        and subclasse["habilidade_instinto"].get("talento_bonus_1_nivel")
    ):
        slots_classe_cfg.append({"origem": f"Subclasse ({subclasse['nome']})", "apenas_metamagia": False, "nivel": 1})
    if classe["id"] == "mago" and tese_arcana_id == "experimentacao_metamagica":
        slots_classe_cfg.append({"origem": "Tese Arcana (Experimentação Metamágica)", "apenas_metamagia": True, "nivel": 1})
    if talento_ancestral["id"] == "ambicao_natural":
        slots_classe_cfg.append({"origem": "Talento Ancestral (Ambição Natural)", "apenas_metamagia": False, "nivel": 1})

    nome_cls_norm = normalizar(classe["nome"])
    marcador_slot_cls = f"talento de {nome_cls_norm}"
    for row in classe.get("tabela_progressao", []):
        niv_row = int(row.get("nivel", 1))
        if 2 <= niv_row <= nivel_alvo and any(normalizar(x) == marcador_slot_cls for x in row.get("caracteristicas", [])):
            slots_classe_cfg.append({"origem": f"Classe ({classe['nome']} {niv_row}º Nível)", "apenas_metamagia": False, "nivel": niv_row})

    manuais_classe_explic = [x for x in classe_escolhas_req if x is not None]
    if manuais_classe_explic and not slots_classe_cfg:
        raise ValueError(
            f"A classe {classe['nome']} não possui talento de classe selecionável no {nivel_alvo}º nível "
            f"(salvo com Ambição Natural ou subclasse/tese específica)."
        )
    for idx_extra in range(len(slots_classe_cfg), len(classe_escolhas_req)):
        if classe_escolhas_req[idx_extra] is not None:
            raise ValueError(
                f"Esta combinação libera apenas {len(slots_classe_cfg)} talento(s) de classe selecionável(is) "
                f"no {nivel_alvo}º nível (slot extra #{idx_extra + 1} não está disponível)."
            )

    # Pré-reserva escolhas manuais válidas para que eventuais slots deixados em procedural não colidam com elas
    reservados_manuais_classe: set[str] = {
        tid
        for idx, tid in enumerate(classe_escolhas_req[: len(slots_classe_cfg)])
        if tid is not None and tid in talentos_classe_por_id
    }
    classe_selecionaveis_aplicados: list[dict[str, str]] = []
    recs_classe_n1 = list(conceito["talentos_recomendados"]["classe_nivel_1"])
    recs_classe_n2_mais = list(conceito["talentos_recomendados"].get("classe_nivel_2_mais") or [])

    for idx_slot, slot_cfg in enumerate(slots_classe_cfg):
        escolha_cid = classe_escolhas_req[idx_slot] if idx_slot < len(classe_escolhas_req) else None
        apenas_meta = bool(slot_cfg["apenas_metamagia"])
        origem_slot = str(slot_cfg["origem"])
        niv_slot = int(slot_cfg["nivel"])
        if escolha_cid is not None:
            cand_c = talentos_classe_por_id.get(escolha_cid)
            if cand_c is None or int(cand_c.get("nivel", 1)) > niv_slot:
                raise ValueError(
                    f"Talento de classe '{escolha_cid}' não existe para {classe['nome']} até o {niv_slot}º nível."
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
            adicionar_classe_talento(cand_c["id"], origem_slot, nivel_slot=niv_slot)
            classe_selecionaveis_aplicados.append({"id": cand_c["id"], "origem": origem_slot})
        else:
            evitar_ids = escolhidos_classe_ids | (reservados_manuais_classe - escolhidos_classe_ids)
            pool_slot = [t for t in talentos_classe_todos if int(t.get("nivel", 1)) <= niv_slot]
            if apenas_meta:
                validos_slot = [
                    t for t in pool_slot
                    if t["id"] not in evitar_ids and _tem_traco_metamagia(t)
                ]
            else:
                validos_slot = [
                    t for t in pool_slot
                    if t["id"] not in evitar_ids and atende_prerequisitos(t.get("pre_requisitos"), ctx)
                ]
            preferidos_slot = (recs_classe_n2_mais + recs_classe_n1) if niv_slot >= 2 else recs_classe_n1
            escolhido_c = _escolher_por_lista_ou_afinidade(
                validos_slot,
                preferidos_slot,
                keywords,
                evitar_ids,
                rng,
            )
            if escolhido_c and adicionar_classe_talento(escolhido_c["id"], origem_slot, nivel_slot=niv_slot):
                classe_selecionaveis_aplicados.append({"id": escolhido_c["id"], "origem": origem_slot})

    # ------------------------------------------------------------------
    # 4. Talentos Extras (Perícia N1..N5, Gerais N1/N3 e Ancestralidade N5)
    # ------------------------------------------------------------------
    talentos_bonus_slots: list[dict[str, Any]] = []
    ids_gerais_pericia_usados: set[str] = {talento_bio_registro["id"]}
    pericia_selecionaveis_aplicados: list[dict[str, str]] = []
    gerais_selecionaveis_aplicados: list[dict[str, str]] = []
    talentos_pericia_progressao: list[dict[str, Any]] = []
    talentos_gerais_progressao: list[dict[str, Any]] = []

    slots_pericia_cfg: list[tuple[str, int]] = []
    if classe["id"] == "ladino":
        slots_pericia_cfg.append(("Classe (Ladino — Talento de Perícia 1º Nível)", 1))
    if nivel_alvo >= 2:
        for row in classe.get("tabela_progressao", []):
            niv_row = int(row.get("nivel", 1))
            if 2 <= niv_row <= nivel_alvo and any(normalizar(x) == "talento de pericia" for x in row.get("caracteristicas", [])):
                slots_pericia_cfg.append((f"Talento de Perícia ({niv_row}º Nível)", niv_row))

    slots_pericia_total = len(slots_pericia_cfg)
    if any(x is not None for x in pericia_escolhas_req) and slots_pericia_total == 0:
        raise ValueError(
            "No 1º nível, apenas o Ladino libera talento de perícia adicional selecionável além da Biografia."
        )
    if len(pericia_escolhas_req) > slots_pericia_total and any(x is not None for x in pericia_escolhas_req[slots_pericia_total:]):
        raise ValueError(f"Há apenas {slots_pericia_total} slot(s) de talento de perícia adicional disponível(is) no {nivel_alvo}º nível.")

    for idx_per, (origem_per, niv_per) in enumerate(slots_pericia_cfg):
        escolha_pid = pericia_escolhas_req[idx_per] if idx_per < len(pericia_escolhas_req) else None
        if escolha_pid is not None:
            cand_p = dados.talentos_gerais_pericia.get(escolha_pid)
            if not cand_p or int(cand_p.get("nivel", 1)) > niv_per or cand_p.get("categoria") != "pericia":
                raise ValueError(
                    f"Talento de perícia '{escolha_pid}' não é um talento de perícia válido até o {niv_per}º nível."
                )
            if escolha_pid in ids_gerais_pericia_usados:
                raise ValueError(
                    f"Talento de perícia '{cand_p['nome']}' já foi concedido ou selecionado em outro slot."
                )
            if not atende_prerequisitos(cand_p.get("pre_requisitos"), ctx):
                raise ValueError(
                    f"O personagem não atende ao pré-requisito do talento '{cand_p['nome']}': "
                    f"{cand_p.get('pre_requisitos')}."
                )
            tp_esc = cand_p
        else:
            candidatos_tp = [
                t for t in dados.talentos_gerais_pericia.values()
                if int(t.get("nivel", 1)) <= niv_per
                and t.get("categoria") == "pericia"
                and t["id"] not in ids_gerais_pericia_usados
                and atende_prerequisitos(t.get("pre_requisitos"), ctx)
            ]
            tp_esc = _escolher_por_lista_ou_afinidade(
                candidatos_tp,
                conceito["talentos_recomendados"]["pericia"],
                keywords,
                ids_gerais_pericia_usados,
                rng,
            )
        if tp_esc:
            ids_gerais_pericia_usados.add(tp_esc["id"])
            _registrar_talento_possuido(tp_esc)
            pericia_selecionaveis_aplicados.append({"id": tp_esc["id"], "origem": origem_per})
            reg_per = {
                "nome": tp_esc["nome"],
                "categoria": "pericia",
                "nivel_slot": niv_per,
                "origem_regra": origem_per,
                "pagina": None,
                "resumo": tp_esc.get("resumo_beneficio") or tp_esc.get("descricao", ""),
                "dados_completos": tp_esc,
            }
            talentos_bonus_slots.append(reg_per)
            if niv_per >= 2:
                talentos_pericia_progressao.append(reg_per)

    talentos_gerais_ativos: set[str] = set()
    # Bloqueio com Escudo automático para Guerreiro, Campeão, Druida e Capelão da Guerra
    tem_bloqueio_escudo = classe["id"] in {"guerreiro", "campeao", "druida"} or (
        classe["id"] == "clerigo" and sub_id == "capelao_da_guerra"
    )
    if tem_bloqueio_escudo:
        talentos_gerais_ativos.add("bloqueio_com_escudo")
        ids_gerais_pericia_usados.add("bloqueio_com_escudo")
        talentos_possuidos_ids.add("bloqueio_com_escudo")
        talentos_possuidos_nomes.add("bloqueio com escudo")

    if talento_ancestral["id"] == "cavaleiro_brusco" and "cavalgar" not in ids_gerais_pericia_usados:
        tal_cav = dados.talentos_gerais_pericia.get("cavalgar")
        if tal_cav:
            ids_gerais_pericia_usados.add("cavalgar")
            talentos_gerais_ativos.add("cavalgar")
            _registrar_talento_possuido(tal_cav)
            talentos_bonus_slots.append(
                {
                    "nome": tal_cav["nome"],
                    "categoria": "geral",
                    "nivel_slot": 1,
                    "origem_regra": "Talento Ancestral (Cavaleiro Brusco)",
                    "pagina": None,
                    "resumo": tal_cav.get("resumo_beneficio") or tal_cav.get("descricao", ""),
                    "dados_completos": tal_cav,
                }
            )

    origens_extras_gerais_cfg: list[tuple[str, int]] = []
    if heranca["id"] == "heranca_versatil":
        origens_extras_gerais_cfg.append(("Herança Versátil (Humano)", 1))
    if talento_ancestral["id"] == "treinamento_geral":
        origens_extras_gerais_cfg.append(("Talento Ancestral (Treinamento Geral)", 1))
    if nivel_alvo >= 3:
        origens_extras_gerais_cfg.append(("Talento Geral (3º Nível)", 3))

    manuais_gerais_explic = [x for x in gerais_escolhas_req if x is not None]
    if manuais_gerais_explic and not origens_extras_gerais_cfg:
        raise ValueError(
            "Talentos gerais só são liberados no 3º nível (ou no 1º nível com Herança Versátil / Treinamento Geral)."
        )
    for idx_extra in range(len(origens_extras_gerais_cfg), len(gerais_escolhas_req)):
        if gerais_escolhas_req[idx_extra] is not None:
            raise ValueError(
                f"Esta combinação libera apenas {len(origens_extras_gerais_cfg)} talento(s) geral(is) no {nivel_alvo}º nível."
            )

    reservados_manuais_gerais: set[str] = {
        tid
        for tid in gerais_escolhas_req[: len(origens_extras_gerais_cfg)]
        if tid is not None and tid in dados.talentos_gerais_pericia
    }

    for i, (origem_geral, niv_geral) in enumerate(origens_extras_gerais_cfg):
        escolha_gid = gerais_escolhas_req[i] if i < len(gerais_escolhas_req) else None
        if escolha_gid is not None:
            cand_g = dados.talentos_gerais_pericia.get(escolha_gid)
            if not cand_g or int(cand_g.get("nivel", 1)) > niv_geral or cand_g.get("categoria") != "geral":
                raise ValueError(
                    f"Talento geral '{escolha_gid}' não é um talento geral válido até o {niv_geral}º nível."
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
                if int(t.get("nivel", 1)) <= niv_geral
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
            _registrar_talento_possuido(tg)
            gerais_selecionaveis_aplicados.append({"id": tg["id"], "origem": origem_geral})
            reg_g = {
                "nome": tg["nome"],
                "categoria": "geral",
                "nivel_slot": niv_geral,
                "origem_regra": origem_geral,
                "pagina": None,
                "resumo": tg.get("resumo_beneficio") or tg.get("descricao", ""),
                "dados_completos": tg,
            }
            talentos_bonus_slots.append(reg_g)
            if niv_geral >= 3:
                talentos_gerais_progressao.append(reg_g)

    # Talento de Ancestralidade Adotada (1º Nível de outra ancestralidade escolhida pelo jogador)
    anc_adotada_id_aplicada: str | None = None
    tal_adotado_id_aplicado: str | None = None
    if "ancestralidade_adotada" in talentos_gerais_ativos and (anc_adotada_req_id or tal_adotado_req_id):
        if not anc_adotada_req_id:
            raise ValueError("Selecione a ancestralidade adotada para escolher o talento correspondente.")
        anc_adotada_obj = dados.ancestralidades.get(anc_adotada_req_id)
        if not anc_adotada_obj:
            raise ValueError(f"Ancestralidade adotada inválida: '{anc_adotada_req_id}'.")
        if anc_adotada_req_id == ancestralidade["id"]:
            raise ValueError(
                f"Ancestralidade Adotada exige escolher uma ancestralidade diferente da sua ({ancestralidade['nome']})."
            )
        anc_adotada_id_aplicada = anc_adotada_req_id

        for reg_b in talentos_bonus_slots:
            if (reg_b.get("dados_completos") or {}).get("id") == "ancestralidade_adotada":
                reg_b["nome"] = f"Ancestralidade Adotada ({anc_adotada_obj['nome']})"

        if tal_adotado_req_id:
            pool_adotado_n1 = {
                t["id"]: t
                for t in anc_adotada_obj.get("talentos_ancestralidade", [])
                if int(t.get("nivel", 1)) == 1
            }
            cand_adotado = pool_adotado_n1.get(tal_adotado_req_id)
            if cand_adotado is None:
                raise ValueError(
                    f"Talento '{tal_adotado_req_id}' não pertence aos talentos de 1º nível de {anc_adotada_obj['nome']}."
                )
            if cand_adotado["id"] in talentos_possuidos_ids:
                raise ValueError(
                    f"O talento adotado '{cand_adotado['nome']}' já está selecionado em outro slot do personagem."
                )
            if not atende_prerequisitos(cand_adotado.get("pre_requisitos"), ctx):
                raise ValueError(
                    f"O personagem não atende ao pré-requisito do talento adotado '{cand_adotado['nome']}': "
                    f"{cand_adotado.get('pre_requisitos')}."
                )

            _registrar_talento_possuido(cand_adotado)
            if cand_adotado["id"] == "visao_orquica":
                ctx["visao_no_escuro"] = True
            origem_adotada = f"Ancestralidade Adotada ({anc_adotada_obj['nome']})"
            talentos_ancestrais.append(dict(cand_adotado, nivel_slot=1, origem=origem_adotada))
            talentos_bonus_slots.append(
                {
                    "nome": f"{cand_adotado['nome']} ({anc_adotada_obj['nome']})",
                    "categoria": "ancestralidade_adotada",
                    "nivel_slot": 1,
                    "origem_regra": origem_adotada,
                    "pagina": None,
                    "resumo": cand_adotado.get("descricao", ""),
                    "dados_completos": cand_adotado,
                }
            )
            tal_adotado_id_aplicado = cand_adotado["id"]

    # Talento de Ancestralidade de 5º Nível
    talento_ancestral_n5: dict[str, Any] | None = None
    if nivel_alvo >= 5:
        pool_anc_n5 = _coletar_pool_ancestral(5)
        if anc_n5_escolha_id is not None:
            cand_anc5 = pool_anc_n5.get(anc_n5_escolha_id)
            if cand_anc5 is None:
                raise ValueError(
                    f"Talento de ancestralidade '{anc_n5_escolha_id}' não pertence a "
                    f"{ancestralidade['nome']} ({heranca['nome']}) até o 5º nível."
                )
            if cand_anc5["id"] == talento_ancestral["id"]:
                raise ValueError(
                    f"O talento ancestral '{cand_anc5['nome']}' já foi escolhido no 1º nível."
                )
            if not atende_prerequisitos(cand_anc5.get("pre_requisitos"), ctx):
                raise ValueError(
                    f"O personagem não atende ao pré-requisito do talento ancestral '{cand_anc5['nome']}': "
                    f"{cand_anc5.get('pre_requisitos')}."
                )
            talento_ancestral_n5 = cand_anc5
        else:
            candidatos_anc5 = [
                t for t in pool_anc_n5.values()
                if t["id"] != talento_ancestral["id"] and atende_prerequisitos(t.get("pre_requisitos"), ctx)
            ]
            if candidatos_anc5:
                scored_anc5 = []
                for t in candidatos_anc5:
                    pts = _pontuar_afinidade(t, keywords) + (2 if int(t.get("nivel", 1)) == 5 else 0)
                    scored_anc5.append((pts, t))
                scored_anc5.sort(key=lambda x: x[0], reverse=True)
                melhor_anc5 = scored_anc5[0][0]
                elegiveis_anc5 = [t for p, t in scored_anc5 if p >= max(0, melhor_anc5 - 2)][:3]
                talento_ancestral_n5 = (
                    rng.choice(elegiveis_anc5) if (rng and len(elegiveis_anc5) > 1) else elegiveis_anc5[0]
                )
        if talento_ancestral_n5:
            _registrar_talento_possuido(talento_ancestral_n5)
            talentos_ancestrais.append(dict(talento_ancestral_n5, nivel_slot=5))

    # ------------------------------------------------------------------
    # 5. Características de Classe até `nivel_alvo` (filtrando metas genéricas)
    # ------------------------------------------------------------------
    ignorar_ids = {"ancestralidade_e_biografia", "proficiencias_iniciais"}
    caracteristicas_classe = [
        c for c in classe["caracteristicas_de_classe"]
        if int(c.get("nivel", 1)) <= nivel_alvo
        and c["id"] not in ignorar_ids
        and not c["id"].startswith("talentos_de_")
    ]
    caracteristicas_n1 = [c for c in caracteristicas_classe if int(c.get("nivel", 1)) == 1]

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

    ids_anc_ativos = {t["id"] for t in talentos_ancestrais}
    pericias_anc_fixas: list[str] = []
    saber_anc: tuple[str, str] | None = None
    for t_anc_item in talentos_ancestrais:
        p_fixas_item, nome_saber_anc = _SABERES_ANCESTRAIS.get(t_anc_item["id"], ([], None))
        for p_f in p_fixas_item:
            if p_f not in pericias_anc_fixas:
                pericias_anc_fixas.append(p_f)
        if nome_saber_anc and saber_anc is None:
            saber_anc = (nome_saber_anc, f"Talento Ancestral ({t_anc_item['nome']})")
        if t_anc_item["id"] == "obsessao_gnomica" and saber_anc is None:
            saber_anc = (
                conceito.get("saber_sugerido") or "Saber Gnômico",
                "Talento Ancestral (Obsessão Gnômica)",
            )

    efeitos = {
        "extras_pericias": (2 if "pericia_natural" in ids_anc_ativos else 0)
        + (1 if "longevidade_ancestral" in ids_anc_ativos else 0)
        + (1 if "evolucao_arcana" in escolhidos_classe_ids else 0)
        + (1 if "evolucao_ocultista" in escolhidos_classe_ids else 0),
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
        "elfo_ligeiro": "elfo_ligeiro" in ids_anc_ativos,
        "ferro_desimpedido": "ferro_desimpedido" in ids_anc_ativos,
        "visao_orquica": "visao_orquica" in ids_anc_ativos,
        "dentes_de_navalha": heranca["id"] == "goblin_dentes_de_navalha",
        "talento_ancestral_id": talento_ancestral["id"],
        "talentos_ancestrais_ids": [t["id"] for t in talentos_ancestrais],
    }

    escolhas_resumo = {
        "modo": "personalizado"
        if any(
            [
                anc_escolha_id is not None,
                anc_n5_escolha_id is not None,
                any(x is not None for x in classe_escolhas_req),
                any(x is not None for x in pericia_escolhas_req),
                any(x is not None for x in gerais_escolhas_req),
            ]
        )
        else "procedural",
        "ancestralidade_id": talento_ancestral["id"],
        "ancestralidade_n5_id": talento_ancestral_n5["id"] if talento_ancestral_n5 else None,
        "ancestralidade_adotada_id": anc_adotada_id_aplicada,
        "talento_ancestral_adotado_id": tal_adotado_id_aplicado,
        "ancestralidade_procedural": anc_escolha_id is None,
        "classe_ids": [item["id"] for item in classe_selecionaveis_aplicados],
        "classe_origens": [item["origem"] for item in classe_selecionaveis_aplicados],
        "pericia_ids": [item["id"] for item in pericia_selecionaveis_aplicados],
        "gerais_ids": [item["id"] for item in gerais_selecionaveis_aplicados],
        "slots_disponiveis": {
            "ancestralidade": 2 if nivel_alvo >= 5 else 1,
            "classe": len(slots_classe_cfg),
            "pericia": slots_pericia_total,
            "gerais": len(origens_extras_gerais_cfg),
        },
    }

    return {
        "talento_biografia": talento_bio_registro,
        "talento_ancestral": talento_ancestral,
        "talento_ancestral_n5": talento_ancestral_n5,
        "talentos_ancestrais": talentos_ancestrais,
        "talentos_classe": talentos_classe_selecionados,
        "talentos_classe_ids": [t["id"] for t in talentos_classe_selecionados],
        "talentos_bonus": talentos_bonus_slots,
        "talentos_pericia_progressao": talentos_pericia_progressao,
        "talentos_gerais_progressao": talentos_gerais_progressao,
        "talentos_gerais_ids": sorted(talentos_gerais_ativos),
        "caracteristicas_classe": caracteristicas_classe,
        "caracteristicas_classe_n1": caracteristicas_n1,
        "efeitos": efeitos,
        "escolhas_talentos": escolhas_resumo,
    }
