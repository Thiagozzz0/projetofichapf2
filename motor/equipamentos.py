"""Proficiências de combate e comprador procedural de equipamentos (orçamento 15 po)."""

from __future__ import annotations

import re
from typing import Any

from .dados import BaseDados
from .regras_casa import aplicar_override_item_casa
from .util import GRAUS, formatar_preco, grau_normalizado, normalizar, pc_para_moedas


ORCAMENTO_POR_NIVEL_PC: dict[int, int] = {
    1: 1500,   # 15 po (150 pp)
    2: 3000,   # 30 po (300 pp)
    3: 7500,   # 75 po (750 pp)
    4: 14000,  # 140 po (1.400 pp)
    5: 27000,  # 270 po (2.700 pp)
}
ORCAMENTO_INICIAL_PC = ORCAMENTO_POR_NIVEL_PC[1]  # 15 po = 150 pp = 1.500 pc
RESERVA_MOEDAS_MIN_PC = 150  # 10% (1 po e 5 pp) reservados em moedas no modo procedural N1
TETO_GASTO_PROCEDURAL_PC = ORCAMENTO_INICIAL_PC - RESERVA_MOEDAS_MIN_PC  # 1.350 pc (90%)


def orcamento_por_nivel_pc(nivel: int = 1) -> int:
    """Retorna o orçamento inicial em peças de cobre para criação de personagem no `nivel` (1–5)."""
    return ORCAMENTO_POR_NIVEL_PC.get(max(1, int(nivel)), ORCAMENTO_INICIAL_PC)

# Etapa 55: pacotes compostos (que trazem rações/corda/cantil embutidos) saem da loja
# para não quebrar a matemática de compra item a item. Kits específicos de perícia
# (escalada, disfarce, reparo, pesca, arapuca, montaria...) continuam disponíveis.
IDS_KITS_COMPOSTOS_REMOVIDOS: frozenset[str] = frozenset({"kit_de_aventureiro"})


def _itens_variados_loja_brutos(
    dados: BaseDados,
    regras_casa: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Retorna equipamentos de aventura (comuns/incomuns) e munições disponíveis para compra inicial."""
    av = dados.equipamentos["equipamentos_aventura"]
    itens: list[dict[str, Any]] = []
    vistos: set[str] = set()

    for grupo_nome, chave_av in (("Equipamentos de Aventura", "comuns"), ("Equipamentos Incomuns", "incomuns")):
        for item_bruto in av.get(chave_av, []):
            item = aplicar_override_item_casa(item_bruto, regras_casa)
            iid = item["id"]
            if iid in vistos or iid in IDS_KITS_COMPOSTOS_REMOVIDOS:
                continue
            vistos.add(iid)
            itens.append(
                {
                    "id": iid,
                    "nome": item["nome"],
                    "subcategoria": grupo_nome,
                    "eh_municao": False,
                    "preco": item.get("preco") or "0 pc",
                    "preco_pc": int(item.get("preco_pc") or 0),
                    "volume": item.get("volume", "—"),
                    "volume_valor": float(item.get("volume_valor") or 0.0),
                    "quantidade_pacote": int(item.get("quantidade_pacote") or 1),
                    "maos": item.get("maos"),
                    "bonus_item": item.get("bonus_item"),
                    "conteudo": list(item.get("conteudo") or []),
                    "descricao": item.get("descricao") or "",
                }
            )

    for m in dados.municoes:
        mid = m["id"]
        if mid in vistos:
            continue
        vistos.add(mid)
        comp = list(m.get("armas_compativeis") or [])
        itens.append(
            {
                "id": mid,
                "nome": m["nome"],
                "subcategoria": "Munições",
                "eh_municao": True,
                "preco": m.get("preco") or "0 pc",
                "preco_pc": int(m.get("preco_pc") or 0),
                "volume": m.get("volume", "L"),
                "volume_valor": float(m.get("volume_valor") or 0.1),
                "quantidade_pacote": int(m.get("quantidade") or 1),
                "maos": None,
                "bonus_item": None,
                "conteudo": [],
                "descricao": m.get("descricao") or (f"Munição compatível com: {', '.join(comp)}." if comp else ""),
            }
        )
    return itens


def resumo_proficiencias_equipamento_classe(classe: dict[str, Any]) -> dict[str, Any]:
    """Extrai do JSON oficial da classe as proficiências iniciais de armaduras, escudos e armas."""
    defesas_raw = classe["proficiencias_iniciais"]["defesas"]
    ataques_raw = classe["proficiencias_iniciais"]["ataques"]
    especificas_raw = ataques_raw.get("armas_especificas")
    if isinstance(especificas_raw, dict):
        armas_esp_norm = [normalizar(w) for w in especificas_raw.get("armas", [])]
        armas_esp_nomes = list(especificas_raw.get("armas", []))
    elif isinstance(especificas_raw, list):
        armas_esp_norm = [normalizar(w) for w in especificas_raw]
        armas_esp_nomes = list(especificas_raw)
    else:
        armas_esp_norm = []
        armas_esp_nomes = []

    return {
        "armaduras": {
            "sem_armadura": grau_normalizado(defesas_raw.get("defesa_sem_armadura")) != "destreinado",
            "leve": grau_normalizado(defesas_raw.get("armaduras_leves")) != "destreinado",
            "media": grau_normalizado(defesas_raw.get("armaduras_medias")) != "destreinado",
            "pesada": grau_normalizado(defesas_raw.get("armaduras_pesadas")) != "destreinado",
        },
        "armas": {
            "simples": grau_normalizado(ataques_raw.get("armas_simples")) != "destreinado",
            "marcial": grau_normalizado(ataques_raw.get("armas_marciais")) != "destreinado",
            "avancada": grau_normalizado(ataques_raw.get("armas_avancadas")) != "destreinado",
            "especificas_norm": armas_esp_norm,
            "especificas_nomes": armas_esp_nomes,
            "arma_favorita_divindade": bool(ataques_raw.get("arma_favorita_divindade")),
        },
        "restricao_nao_metal": classe["id"] == "druida",
        "ferramentas_recomendadas": _ferramenta_essencial(classe["id"], ""),
    }


def listar_catalogo_equipamentos_loja(
    dados: BaseDados,
    regras_casa: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Catálogo inicial de equipamentos para o jogador (sem itens alquímicos, mágicos ou fórmulas)."""
    armaduras = [
        {
            "id": a["id"],
            "nome": a["nome"],
            "categoria": a["categoria"],
            "material": a.get("material"),
            "preco": a.get("preco") or "0 pp",
            "preco_pc": int(a.get("preco_pc") or 0),
            "bonus_ca": int(a.get("bonus_ca") or 0),
            "limite_destreza": a.get("limite_destreza"),
            "penalidade_testes": int(a.get("penalidade_testes") or 0),
            "penalidade_velocidade_m": float(a.get("penalidade_velocidade_m") or 0.0),
            "forca_minima": a.get("forca_minima"),
            "volume": a.get("volume", "L"),
            "grupo": a.get("grupo"),
            "tracos": list(a.get("tracos") or []),
            "descricao": a.get("descricao") or "",
            "resumo": formatar_armadura_resumo(a),
        }
        for a in dados.armaduras.values()
        if a["id"] != "nenhuma_armadura"
    ]

    escudos = [
        {
            "id": s["id"],
            "nome": s["nome"],
            "eh_metal": s["id"] in ("broquel", "escudo_de_aco", "escudo_de_corpo"),
            "preco": s.get("preco") or "0 pp",
            "preco_pc": int(s.get("preco_pc") or 0),
            "bonus_ca": int(s.get("bonus_ca") or 0),
            "bonus_ca_cobertura": s.get("bonus_ca_cobertura"),
            "penalidade_velocidade_m": float(s.get("penalidade_velocidade_m") or 0.0),
            "permite_mao_livre": bool(s.get("permite_mao_livre", False)),
            "dureza": int(s.get("dureza") or 0),
            "pv": int(s.get("pv") or 0),
            "limiar_quebra": int(s.get("limiar_quebra") or 0),
            "volume": s.get("volume", "L"),
            "descricao": s.get("descricao") or "",
        }
        for s in dados.escudos.values()
    ]

    def _serializar_armas(lista: list[dict[str, Any]]) -> list[dict[str, Any]]:
        res = []
        for w in lista:
            if w["id"] == "bomba_alquimica" or w.get("preco_pc") is None:
                continue
            res.append(
                {
                    "id": w["id"],
                    "nome": w["nome"],
                    "categoria": w["categoria"],
                    "raridade": w.get("raridade", "Comum"),
                    "preco": w.get("preco") or "0 pc",
                    "preco_pc": int(w.get("preco_pc") or 0),
                    "dano": w.get("dano", ""),
                    "distancia_m": w.get("distancia_m"),
                    "recarga": w.get("recarga"),
                    "maos": str(w.get("maos") or "1"),
                    "municao": w.get("municao"),
                    "volume": w.get("volume", "—"),
                    "grupo": w.get("grupo", ""),
                    "tracos": list(w.get("tracos") or []),
                    "descricao": w.get("descricao") or "",
                }
            )
        return res

    armas_json = dados.equipamentos["armas"]
    armas_cc = _serializar_armas(armas_json["corpo_a_corpo"])
    armas_dist = _serializar_armas(armas_json["distancia"])
    variados = _itens_variados_loja_brutos(dados, regras_casa)

    return {
        "orcamento_inicial_pc": ORCAMENTO_INICIAL_PC,
        "orcamento_inicial_pp": ORCAMENTO_INICIAL_PC // 10,
        "orcamento_por_nivel_pc": {str(k): v for k, v in ORCAMENTO_POR_NIVEL_PC.items()},
        "orcamento_por_nivel_pp": {str(k): v // 10 for k, v in ORCAMENTO_POR_NIVEL_PC.items()},
        "armaduras": armaduras,
        "escudos": escudos,
        "armas_corpo_a_corpo": armas_cc,
        "armas_distancia": armas_dist,
        "equipamentos_variados": variados,
        # Etapa 55: kits de classe (pacotes prontos) removidos da loja — compra item a item.
        "kits_de_classe": {},
        "familiaridade_armas_ancestral": {
            tid: {"armas": list(armas_lista), "traco": traco}
            for tid, (armas_lista, traco) in _FAMILIARIDADE_ARMAS_ANCESTRAL.items()
        },
    }


def _listar_kits_de_classe_loja(
    dados: BaseDados,
    armaduras: list[dict[str, Any]],
    armas_cc: list[dict[str, Any]],
    armas_dist: list[dict[str, Any]],
    variados: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Resolve os 12 Kits de Classe de dados/equipamentos.json para IDs reais da loja."""
    arm_por_nome = {normalizar(a["nome"]): a for a in armaduras}
    wcc_por_nome = {normalizar(w["nome"]): w for w in armas_cc}
    wdi_por_nome = {normalizar(w["nome"]): w for w in armas_dist}
    var_por_nome = {normalizar(v["nome"]): v for v in variados}

    def _buscar_por_nome(mapa: dict[str, dict[str, Any]], texto: str) -> dict[str, Any] | None:
        n = normalizar(texto)
        if n in mapa:
            return mapa[n]
        if n.endswith("s") and n[:-1] in mapa:
            return mapa[n[:-1]]
        return None

    kits_out: dict[str, dict[str, Any]] = {}
    for k in dados.equipamentos.get("kits_de_classe") or []:
        arm_id: str | None = None
        armas_cc_ids: list[str] = []
        armas_dist_ids: list[str] = []
        variados_acum: dict[str, int] = {}
        preco_total_pc = 0
        resumo_itens: list[str] = []
        itens_omitidos: list[str] = []

        if k.get("armadura"):
            arm_obj = _buscar_por_nome(arm_por_nome, k["armadura"])
            if arm_obj:
                arm_id = arm_obj["id"]
                preco_total_pc += int(arm_obj["preco_pc"])
                resumo_itens.append(arm_obj["nome"])

        for entrada_w in k.get("armas") or []:
            m_mun = re.search(r"\(com\s+(\d+)\s+([^)]+)\)", entrada_w, flags=re.IGNORECASE)
            if m_mun:
                qtd_mun = int(m_mun.group(1))
                nome_mun = m_mun.group(2).strip()
                mun_obj = _buscar_por_nome(var_por_nome, nome_mun)
                if mun_obj:
                    pac = max(1, int(mun_obj.get("quantidade_pacote") or 1))
                    lotes = max(1, (qtd_mun + pac - 1) // pac)
                    variados_acum[mun_obj["id"]] = variados_acum.get(mun_obj["id"], 0) + lotes
                    preco_total_pc += int(mun_obj["preco_pc"]) * lotes
                    resumo_itens.append(f"{qtd_mun} {mun_obj['nome']}")

            base_w = re.sub(r"\s*\([^)]*\)", "", entrada_w).strip()
            m_qtd = re.match(r"^(\d+)\s+(.+)$", base_w)
            qtd_w = int(m_qtd.group(1)) if m_qtd else 1
            nome_w = m_qtd.group(2).strip() if m_qtd else base_w

            w_obj = _buscar_por_nome(wcc_por_nome, nome_w)
            if w_obj:
                armas_cc_ids.extend([w_obj["id"]] * qtd_w)
                preco_total_pc += int(w_obj["preco_pc"]) * qtd_w
                resumo_itens.append(f"{qtd_w}× {w_obj['nome']}" if qtd_w > 1 else w_obj["nome"])
            else:
                w_obj = _buscar_por_nome(wdi_por_nome, nome_w)
                if w_obj:
                    armas_dist_ids.extend([w_obj["id"]] * qtd_w)
                    preco_total_pc += int(w_obj["preco_pc"]) * qtd_w
                    resumo_itens.append(f"{qtd_w}× {w_obj['nome']}" if qtd_w > 1 else w_obj["nome"])
                else:
                    itens_omitidos.append(entrada_w)

        for entrada_eq in k.get("equipamentos") or []:
            m_eq = re.match(r"^(\d+)\s+(?:conjuntos?\s+de\s+)?(.+)$", entrada_eq.strip(), flags=re.IGNORECASE)
            qtd_eq = int(m_eq.group(1)) if m_eq else 1
            nome_eq = m_eq.group(2).strip() if m_eq else entrada_eq.strip()
            v_obj = _buscar_por_nome(var_por_nome, nome_eq)
            if v_obj:
                variados_acum[v_obj["id"]] = variados_acum.get(v_obj["id"], 0) + qtd_eq
                preco_total_pc += int(v_obj["preco_pc"]) * qtd_eq
                resumo_itens.append(f"{qtd_eq}× {v_obj['nome']}" if qtd_eq > 1 else v_obj["nome"])
            else:
                itens_omitidos.append(entrada_eq)

        kits_out[k["id"]] = {
            "id": k["id"],
            "classe": k["classe"],
            "armadura_id": arm_id,
            "armas_corpo_a_corpo_ids": armas_cc_ids,
            "armas_distancia_ids": armas_dist_ids,
            "equipamentos_variados": [{"id": iid, "quantidade": q} for iid, q in variados_acum.items()],
            "preco_pc": preco_total_pc,
            "resumo_itens": resumo_itens,
            "opcoes_sugeridas": list(k.get("opcoes") or []),
            "itens_omitidos": itens_omitidos,
        }
    return kits_out


def formatar_armadura_resumo(armadura: dict[str, Any]) -> str:
    """Formata o nome da armadura seguido do bônus de CA e limitadores."""
    bonus_ca = int(armadura.get("bonus_ca") or 0)
    partes = [f"+{bonus_ca} CA"]
    if armadura.get("limite_destreza") is not None:
        partes.append(f"Lim DES +{int(armadura['limite_destreza'])}")
    pen = int(armadura.get("penalidade_testes") or 0)
    if pen != 0:
        partes.append(f"Pen {pen}")
    vel_p = float(armadura.get("penalidade_velocidade_m") or 0.0)
    if vel_p < 0:
        vel_txt = f"{int(vel_p)}" if vel_p.is_integer() else str(vel_p).replace(".", ",")
        partes.append(f"Vel {vel_txt}m")
    return f"{armadura['nome']} ({', '.join(partes)})"


def _formatar_arma_inventario(arma: dict[str, Any], sufixo: str = "") -> str:
    dano = f"{arma.get('dano_quantidade', 1)}{arma.get('dano_dado', 'd4')} {arma.get('dano_tipo', '')}".strip()
    partes = [dano]
    if arma.get("bonus_item"):
        partes.append(str(arma["bonus_item"]))
    if sufixo:
        partes.append(sufixo)
    return f"{arma['nome']} ({', '.join(partes)})"


def _formatar_item_geral_inventario(item: dict[str, Any], quantidade: int = 1) -> str:
    partes: list[str] = []
    if item.get("bonus_item"):
        partes.append(str(item["bonus_item"]))
    qtd_pac = int(item.get("quantidade_pacote") or 1)
    qtd_efetiva = max(quantidade, qtd_pac)
    if qtd_efetiva > 1 and f"({qtd_efetiva})" not in item["nome"]:
        partes.append(f"Qtd: {qtd_efetiva}")
    if item.get("conteudo"):
        partes.append(", ".join(item["conteudo"]))
    return f"{item['nome']} ({'; '.join(partes)})" if partes else item["nome"]

_FAMILIARIDADE_ARMAS_ANCESTRAL: dict[str, tuple[list[str], str]] = {
    "familiaridade_com_armas_enanicas": (["machado de batalha", "martelo de guerra", "picareta"], "anao"),
    "familiaridade_com_armas_elficas": (
        ["arco curto", "arco curto composto", "arco longo", "arco longo composto", "espada longa", "rapieira"],
        "elfo",
    ),
    "familiaridade_com_armas_gnomicas": (["glaive", "kukri"], "gnomo"),
    "familiaridade_com_armas_goblinoides": (["cortacao", "fatia-cavalo"], "goblin"),
    "familiaridade_com_armas_halflings": (["cajado-funda halfling", "espada curta", "funda"], "halfling"),
    "familiaridade_com_armas_orquicas": (["bracamante", "machado longo"], "orc"),
}


def _subir_grau(atual: str, alvo: str) -> str:
    """Promove o grau de proficiência apenas se `alvo` for superior ao `atual`."""
    if atual not in GRAUS or alvo not in GRAUS:
        return atual
    return alvo if GRAUS.index(alvo) > GRAUS.index(atual) else atual


def calcular_proficiencias_combate(
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    talentos_classe_ids: list[str] | None = None,
    divindade: dict[str, Any] | None = None,
    efeitos_talentos: dict[str, Any] | None = None,
    nivel: int = 1,
    conceito: dict[str, Any] | None = None,
    dados: BaseDados | None = None,
) -> dict[str, Any]:
    """Resolve as proficiências de armaduras e armas considerando classe, subclasse, talentos, divindade e nível."""
    nivel_alvo = max(1, int(nivel))
    efeitos = efeitos_talentos or {}
    defesas_brutas = classe["proficiencias_iniciais"]["defesas"]
    defesas = {
        "sem_armadura": grau_normalizado(defesas_brutas.get("defesa_sem_armadura")),
        "leve": grau_normalizado(defesas_brutas.get("armaduras_leves")),
        "media": grau_normalizado(defesas_brutas.get("armaduras_medias")),
        "pesada": grau_normalizado(defesas_brutas.get("armaduras_pesadas")),
    }

    sub_id = subclasse["id"] if subclasse else ""
    if classe["id"] == "clerigo" and sub_id == "capelao_da_guerra":
        defesas["leve"] = "treinado"
        defesas["media"] = "treinado"
    elif classe["id"] == "ladino" and sub_id == "rufiao":
        defesas["media"] = "treinado"

    if efeitos.get("proficiencia_com_armaduras"):
        for cat_p in ("leve", "media", "pesada"):
            if defesas[cat_p] == "destreinado":
                defesas[cat_p] = "treinado"
                break

    ataques_brutos = classe["proficiencias_iniciais"]["ataques"]
    especificas = ataques_brutos.get("armas_especificas")
    if isinstance(especificas, dict):
        lista_esp = [normalizar(w) for w in especificas.get("armas", [])]
        grau_esp = grau_normalizado(especificas)
    elif isinstance(especificas, list):
        lista_esp = [normalizar(w) for w in especificas]
        grau_esp = "treinado"
    else:
        lista_esp = []
        grau_esp = "destreinado"

    desarmado_grau = grau_normalizado(ataques_brutos.get("ataques_desarmados"))
    if classe["id"] in ("clerigo", "campeao") and divindade:
        wid_fav = divindade.get("arma_favorecida_id")
        nome_fav = normalizar(divindade.get("arma_favorecida_nome"))
        if wid_fav == "punho":
            if desarmado_grau == "destreinado":
                desarmado_grau = "treinado"
        elif classe["id"] == "clerigo" and nome_fav and nome_fav not in lista_esp:
            lista_esp.append(nome_fav)
            if grau_esp == "destreinado":
                grau_esp = "treinado"

    armas_monge_treinadas = classe["id"] == "monge" and "arsenal_monastico" in (talentos_classe_ids or [])
    simples_g = grau_normalizado(ataques_brutos.get("armas_simples"))
    marcial_g = grau_normalizado(ataques_brutos.get("armas_marciais"))
    avancada_g = grau_normalizado(ataques_brutos.get("armas_avancadas"))
    if efeitos.get("proficiencia_com_armas"):
        if simples_g == "destreinado":
            simples_g = "treinado"
        elif marcial_g == "destreinado":
            marcial_g = "treinado"
        elif avancada_g == "destreinado":
            avancada_g = "treinado"

    tal_anc_ids_lista = list(efeitos.get("talentos_ancestrais_ids") or [])
    if not tal_anc_ids_lista and efeitos.get("talento_ancestral_id"):
        tal_anc_ids_lista.append(str(efeitos["talento_ancestral_id"]))
    armas_anc_lista: list[str] = []
    traco_anc_armas: str | None = None
    for tid_anc in tal_anc_ids_lista:
        if tid_anc in _FAMILIARIDADE_ARMAS_ANCESTRAL:
            armas_anc_lista, traco_anc_armas = _FAMILIARIDADE_ARMAS_ANCESTRAL[tid_anc]
            break
    armas_monge_grau = "treinado" if armas_monge_treinadas else "destreinado"
    maestria_guerreiro_grupo: str | None = None

    # Marcos de proficiência de combate dos níveis 2 a 5 (tabela_progressao)
    if nivel_alvo >= 3:
        if classe["id"] == "clerigo" and sub_id == "capelao_da_guerra":
            marcial_g = _subir_grau(marcial_g, "treinado")

    if nivel_alvo >= 5:
        cid = classe["id"]
        if cid in ("barbaro", "campeao", "patrulheiro"):
            simples_g = _subir_grau(simples_g, "especialista")
            marcial_g = _subir_grau(marcial_g, "especialista")
            desarmado_grau = _subir_grau(desarmado_grau, "especialista")
            if cid == "campeao" and grau_esp != "destreinado":
                grau_esp = _subir_grau(grau_esp, "especialista")
        elif cid == "ladino":
            simples_g = _subir_grau(simples_g, "especialista")
            desarmado_grau = _subir_grau(desarmado_grau, "especialista")
            if grau_esp != "destreinado":
                grau_esp = _subir_grau(grau_esp, "especialista")
        elif cid == "monge":
            desarmado_grau = _subir_grau(desarmado_grau, "especialista")
            simples_g = _subir_grau(simples_g, "especialista")
            if armas_monge_treinadas:
                armas_monge_grau = _subir_grau(armas_monge_grau, "especialista")
        elif cid == "guerreiro":
            if conceito and dados:
                eq_rec = conceito.get("equipamento_recomendado") or {}
                estilo_eq = eq_rec.get("estilo_empunhadura", "")
                cand_wids = (
                    list(eq_rec.get("armas_distancia_ids") or [])
                    if estilo_eq == "distancia"
                    else list(eq_rec.get("armas_corpo_a_corpo_ids") or [])
                )
                for wid in cand_wids:
                    arma_ref = dados.armas.get(wid)
                    if arma_ref and arma_ref.get("grupo"):
                        maestria_guerreiro_grupo = normalizar(arma_ref["grupo"])
                        break
            if not maestria_guerreiro_grupo:
                maestria_guerreiro_grupo = "*"

    armas = {
        "simples": simples_g,
        "marcial": marcial_g,
        "avancada": avancada_g,
        "desarmado": desarmado_grau,
        "bombas_alquimicas": grau_normalizado(ataques_brutos.get("bombas_alquimicas")),
        "armas_traco_monge": armas_monge_grau,
        "especificas_lista": lista_esp,
        "especificas_grau": grau_esp,
        "armas_ancestrais_lista": list(armas_anc_lista),
        "traco_ancestral_armas": traco_anc_armas,
        "armamento_nao_convencional": "armamento_nao_convencional" in tal_anc_ids_lista,
        "maestria_guerreiro_grupo": maestria_guerreiro_grupo,
    }

    return {
        "defesas": defesas,
        "armas": armas,
        "restricao_nao_metal": classe["id"] == "druida",
    }


def grau_arma(arma: dict[str, Any], profs_armas: dict[str, Any]) -> str:
    """Determina o grau de proficiência do personagem com uma arma específica."""
    cat = normalizar(arma.get("categoria"))
    nome_norm = normalizar(arma.get("nome"))
    tracos_norm = [normalizar(t) for t in arma.get("tracos", [])]

    if arma.get("id") == "bomba_alquimica":
        return profs_armas.get("bombas_alquimicas", "destreinado") or profs_armas.get("marcial", "destreinado")
    if "desarmado" in cat:
        return profs_armas["desarmado"]
    if (
        profs_armas.get("armas_traco_monge", "destreinado") != "destreinado"
        and "monge" in tracos_norm
        and ("simples" in cat or "marcial" in cat)
    ):
        return profs_armas["armas_traco_monge"]
    if nome_norm in profs_armas["especificas_lista"]:
        return profs_armas["especificas_grau"]

    traco_anc = profs_armas.get("traco_ancestral_armas")
    if traco_anc and traco_anc in tracos_norm:
        if "marcial" in cat:
            grau = profs_armas["simples"]
        elif "avancada" in cat:
            grau = profs_armas["marcial"]
        else:
            grau = profs_armas["simples"]
    elif profs_armas.get("armamento_nao_convencional") and normalizar(arma.get("raridade")) == "incomum":
        if "simples" in cat or "marcial" in cat:
            grau = profs_armas["marcial"] if profs_armas["marcial"] != "destreinado" else profs_armas["simples"]
        elif "avancada" in cat and profs_armas["marcial"] != "destreinado":
            grau = profs_armas["marcial"]
        else:
            grau = profs_armas["avancada"]
    elif "simples" in cat:
        grau = profs_armas["simples"]
    elif "marcial" in cat:
        grau = profs_armas["marcial"]
    elif "avancada" in cat:
        grau = profs_armas["avancada"]
    else:
        grau = "destreinado"

    if grau == "destreinado" and nome_norm in profs_armas.get("armas_ancestrais_lista", []):
        grau = "treinado"

    maestria_grp = profs_armas.get("maestria_guerreiro_grupo")
    if maestria_grp and (maestria_grp == "*" or normalizar(arma.get("grupo")) == maestria_grp):
        if "simples" in cat or "marcial" in cat or "desarmado" in cat:
            grau = _subir_grau(grau, "mestre")
        elif "avancada" in cat:
            grau = _subir_grau(grau, "especialista")
    return grau


def _chave_categoria_armadura(categoria_texto: str) -> str:
    c = normalizar(categoria_texto)
    if "sem armadura" in c:
        return "sem_armadura"
    if "leve" in c:
        return "leve"
    if "media" in c:
        return "media"
    if "pesada" in c:
        return "pesada"
    return "sem_armadura"


def _municao_para_arma(dados: BaseDados, arma: dict[str, Any]) -> dict[str, Any] | None:
    mun = arma.get("municao")
    if not mun:
        return None
    nome_arma = normalizar(arma["nome"])
    for m in dados.municoes:
        compativeis = [normalizar(x) for x in m.get("armas_compativeis", [])]
        if nome_arma in compativeis:
            return m
    return None


def _ferramenta_essencial(
    classe_id: str,
    conceito_id: str,
    subclasse_id: str = "",
    biografia_id: str = "",
) -> list[str]:
    mapa = {
        "alquimista": ["ferramentas_de_alquimista", "livro_basico_de_manufatura"],
        "bardo": ["instrumento_musical_portatil"],
        "clerigo": ["simbolo_religioso_madeira"],
        "druida": ["azevinho_e_visco"],
        "ladino": ["ferramentas_de_ladrao"],
        "mago": ["bolsa_de_componentes_materiais", "conjunto_de_escrita"],
    }
    itens = list(mapa.get(classe_id, []))
    if (
        subclasse_id == "cirurgiao"
        or any(termo in conceito_id for termo in ("cirurgiao", "curandeiro", "medico", "hospitalario"))
    ) and "ferramentas_de_curandeiro" not in itens:
        itens.append("ferramentas_de_curandeiro")

    mapa_biografia = {
        "medico_de_campo": ["ferramentas_de_curandeiro"],
        "herbalista": ["ferramentas_de_curandeiro"],
        "artesao": ["ferramentas_de_artesao"],
        "funileiro": ["ferramentas_de_artesao"],
        "artista": ["instrumento_musical_portatil"],
        "animador": ["instrumento_musical_portatil"],
        "charlatao": ["kit_de_disfarce"],
        "criminoso": ["ferramentas_de_ladrao"],
        "crianca_de_rua": ["ferramentas_de_ladrao"],
        "estudioso": ["conjunto_de_escrita"],
        "advogado": ["conjunto_de_escrita"],
        "batedor": ["kit_de_escalada"],
        "mineiro": ["kit_de_escalada"],
    }
    for fid in mapa_biografia.get(biografia_id, []):
        if fid not in itens:
            itens.append(fid)
    return itens


def _eh_modo_procedural_eq(valor: Any) -> bool:
    if valor is None:
        return True
    if isinstance(valor, str):
        return normalizar(valor) in ("", "procedural", "auto", "automatico", "automatica")
    return False


def _somar_volumes(lista_itens: list[dict[str, Any]]) -> tuple[int, int]:
    """Soma volumes de uma lista de itens respeitando itens Leves (L / 0,1) e lotes em L."""
    inteiros, leves = 0, 0
    for item in lista_itens:
        if item.get("volume_leves") is not None:
            leves += max(0, int(item["volume_leves"]))
            continue
        vol_txt = str(item.get("volume") or "").strip().upper()
        if vol_txt == "L":
            leves += 1
            continue
        if vol_txt.endswith("L") and vol_txt[:-1].isdigit():
            leves += int(vol_txt[:-1])
            continue
        vv = float(item.get("volume_valor") or 0.0)
        if vv >= 1.0:
            inteiros += int(round(vv))
        elif 0.05 <= vv < 1.0:
            leves += max(1, int(round(vv * 10)))
    return inteiros, leves


def _calcular_volume_efetivo(
    itens_vestidos: list[dict[str, Any]],
    itens_preparados: list[dict[str, Any]],
    outros_itens: list[dict[str, Any]],
    leves_por_volume: int = 10,
) -> tuple[int, int]:
    """Calcula `(volume_total, volume_leves_soltos)` aplicando a isenção de 2 Volumes da mochila."""
    divisor_leves = max(1, int(leves_por_volume or 10))
    int_vest, lev_vest = _somar_volumes(itens_vestidos + itens_preparados)
    int_outros, lev_outros = _somar_volumes(outros_itens)
    tem_mochila = any(
        "kit de aventureiro" in normalizar(it["nome"]) or "mochila" in normalizar(it["nome"])
        for it in outros_itens
    )
    if tem_mochila:
        if int_outros >= 2:
            int_outros_efetivo = int_outros - 2
            lev_outros_efetivo = lev_outros
        else:
            folga_leves = (2 - int_outros) * divisor_leves
            int_outros_efetivo = 0
            lev_outros_efetivo = max(0, lev_outros - folga_leves)
    else:
        int_outros_efetivo, lev_outros_efetivo = int_outros, lev_outros

    soma_inteiros = int_vest + int_outros_efetivo
    soma_leves = lev_vest + lev_outros_efetivo
    return soma_inteiros + (soma_leves // divisor_leves), soma_leves % divisor_leves


def _pool_equipamentos_viagem(
    classe_id: str,
    conceito: dict[str, Any],
    biografia_id: str,
    usa_escudo: bool,
) -> list[tuple[str, int]]:
    """Retorna fila priorizada de equipamentos de viagem/acampamento e utilidades temáticas."""
    fila: list[tuple[str, int]] = [
        ("tenda_individual", 1),
        ("roupas_de_inverno", 1),
        ("lanterna_coberta", 1),
        ("oleo_meio_litro", 2),
        ("bandoleira", 1),
        ("bussola", 1),
        ("racoes_1_semana", 1),
        ("apito_de_advertencia", 1),
    ]

    per_pri = {normalizar(p) for p in (conceito.get("pericias_prioritarias") or [])[:4]}
    cid_con = conceito["id"]

    if usa_escudo or classe_id in ("guerreiro", "campeao", "barbaro") or biografia_id == "artesao":
        fila.append(("kit_de_reparo", 1))

    if classe_id in ("bardo", "clerigo", "druida", "feiticeiro", "mago") or biografia_id in ("estudioso", "advogado"):
        fila.extend([("porta_pergaminho", 1), ("conjunto_de_escrita", 1), ("espelho", 1), ("ampulheta", 1)])

    if classe_id in ("clerigo", "campeao") or biografia_id == "acolito":
        fila.extend([("texto_religioso", 1), ("simbolo_religioso_prata", 1)])

    if (
        classe_id in ("ladino", "patrulheiro")
        or "furtividade" in per_pri
        or "ladroagem" in per_pri
        or biografia_id in ("batedor", "criminoso", "crianca_de_rua")
    ):
        fila.extend([("pe_de_cabra", 1), ("arpeu", 1), ("estrepes", 1), ("kit_de_escalada", 1), ("espelho", 1)])

    if classe_id == "bardo" or biografia_id in ("nobre", "artista", "animador", "emissario", "charlatao"):
        fila.extend([("roupas_finas", 1), ("espelho", 1)])

    if biografia_id in ("guarda", "cacador_de_recompensas", "soldado") or "cacador" in cid_con:
        fila.extend([("algemas_simples", 1), ("algemas_ruins", 1)])

    if classe_id in ("patrulheiro", "druida") or biografia_id in ("cacador", "marinheiro", "eremita"):
        fila.extend([("kit_de_pesca", 1), ("arpeu", 1)])

    # Utilidades gerais de viagem e acampamento para completar até ~90% sem sobrecarga
    fila.extend(
        [
            ("ferramentas_de_curandeiro", 1),
            ("kit_de_reparo", 1),
            ("roupas_finas", 1),
            ("fechadura_simples", 1),
            ("espelho", 1),
            ("utensilios_de_cozinha", 1),
            ("pe_de_cabra", 1),
            ("kit_de_escalada", 1),
            ("corda", 1),
            ("algemas_ruins", 1),
            ("arpeu", 1),
            ("saco", 1),
            ("cantil", 1),
        ]
    )

    dedup: list[tuple[str, int]] = []
    vistos: set[str] = set()
    for iid, qtd in fila:
        if iid not in vistos:
            vistos.add(iid)
            dedup.append((iid, qtd))
    return dedup


def comprar_equipamentos(
    dados: BaseDados,
    ancestralidade: dict[str, Any],
    classe: dict[str, Any],
    conceito: dict[str, Any],
    mod_for: int,
    profs_combate: dict[str, Any],
    mod_int: int = 0,
    subclasse: dict[str, Any] | None = None,
    efeitos_talentos: dict[str, Any] | None = None,
    divindade: dict[str, Any] | None = None,
    biografia: dict[str, Any] | None = None,
    nivel: int = 1,
    orcamento_pc: int | None = None,
    escolhas_equipamentos: dict[str, Any] | None = None,
    regras_casa: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Executa a compra procedural, manual ou híbrida dentro do orçamento do nível e calcula o Volume."""
    orcamento_base_pc = int(orcamento_pc) if orcamento_pc is not None else orcamento_por_nivel_pc(nivel)
    reserva_min_pc = orcamento_base_pc // 10
    saldo_pc = orcamento_base_pc
    leves_por_volume = max(1, int((regras_casa or {}).get("itens_leves_por_volume") or 10))
    defesas = profs_combate["defesas"]
    armas_prof = profs_combate["armas"]
    nao_metal = profs_combate["restricao_nao_metal"]

    escolhas = escolhas_equipamentos or {}
    modo_global = normalizar(str(escolhas.get("modo") or ""))
    if modo_global in ("procedural", "auto", "automatico") and not any(
        not _eh_modo_procedural_eq(escolhas.get(k))
        for k in ("armadura_id", "escudo_id", "armas_corpo_a_corpo_ids", "armas_distancia_ids", "equipamentos_variados")
    ):
        armadura_req: Any = "procedural"
        escudo_req: Any = "procedural"
        armas_cc_req: Any = "procedural"
        armas_dist_req: Any = "procedural"
        variados_req: Any = "procedural"
    else:
        armadura_req = escolhas.get("armadura_id", "procedural")
        escudo_req = escolhas.get("escudo_id", "procedural")
        armas_cc_req = escolhas.get("armas_corpo_a_corpo_ids", "procedural")
        armas_dist_req = escolhas.get("armas_distancia_ids", "procedural")
        variados_req = escolhas.get("equipamentos_variados", "procedural")

    armadura_manual = not _eh_modo_procedural_eq(armadura_req)
    escudo_manual = not _eh_modo_procedural_eq(escudo_req)
    armas_cc_manual = not _eh_modo_procedural_eq(armas_cc_req)
    armas_dist_manual = not _eh_modo_procedural_eq(armas_dist_req)
    variados_manual = not _eh_modo_procedural_eq(variados_req)

    eq_rec = conceito["equipamento_recomendado"]
    estilo = eq_rec["estilo_empunhadura"]

    armas_cc_ids = list(eq_rec["armas_corpo_a_corpo_ids"])
    armas_dist_ids = list(eq_rec["armas_distancia_ids"])
    usa_escudo_efetivo = bool(eq_rec["usa_escudo"])
    if classe["id"] == "clerigo" and subclasse and subclasse.get("id") == "capelao_da_guerra" and divindade:
        wid_fav = divindade.get("arma_favorecida_id")
        w_fav = dados.armas.get(wid_fav) if wid_fav else None
        if w_fav:
            if w_fav.get("tipo_ataque") == "distancia":
                armas_dist_ids = [wid_fav] + [x for x in armas_dist_ids if x != wid_fav]
            else:
                armas_cc_ids = [wid_fav] + [x for x in armas_cc_ids if x != wid_fav]
                if str(w_fav.get("maos")) == "2":
                    usa_escudo_efetivo = False
    elif classe["id"] == "campeao" and divindade:
        wid_fav = divindade.get("arma_favorecida_id")
        w_fav = dados.armas.get(wid_fav) if wid_fav else None
        if w_fav:
            if w_fav.get("tipo_ataque") == "distancia":
                armas_dist_ids = [wid_fav] + [x for x in armas_dist_ids if x != wid_fav]
            elif not usa_escudo_efetivo or str(w_fav.get("maos")) != "2":
                armas_cc_ids = [wid_fav] + [x for x in armas_cc_ids if x != wid_fav]

    # Armas de Familiaridade Ancestral (priorizadas quando o talento ancestral concede proficiência)
    tal_anc_ids_eq = list((efeitos_talentos or {}).get("talentos_ancestrais_ids") or [])
    if not tal_anc_ids_eq and (efeitos_talentos or {}).get("talento_ancestral_id"):
        tal_anc_ids_eq.append(str(efeitos_talentos["talento_ancestral_id"]))
    tal_anc_id = next((tid for tid in tal_anc_ids_eq if tid in _FAMILIARIDADE_ARMAS_ANCESTRAL), "")
    if tal_anc_id in _FAMILIARIDADE_ARMAS_ANCESTRAL:
        armas_anc_nomes, traco_anc = _FAMILIARIDADE_ARMAS_ANCESTRAL[tal_anc_id]
        nomes_anc_norm = {normalizar(n) for n in armas_anc_nomes}
        anc_cc: list[tuple[int, str]] = []
        anc_dist: list[tuple[int, str]] = []
        for w in dados.armas.values():
            if w["id"] in ("adaga_de_cla", "bomba_alquimica") or w.get("preco_pc") is None:
                continue
            if grau_arma(w, armas_prof) == "destreinado":
                continue
            tracos_w = [normalizar(t) for t in w.get("tracos", [])]
            eh_traco_anc = traco_anc in tracos_w
            eh_nome_anc = normalizar(w.get("nome")) in nomes_anc_norm
            if not (eh_traco_anc or eh_nome_anc):
                continue
            if w.get("tipo_ataque") == "distancia":
                anc_dist.append((0 if eh_traco_anc else 1, w["id"]))
            elif w.get("tipo_ataque") == "corpo_a_corpo":
                maos_w = str(w.get("maos") or "1")
                if (usa_escudo_efetivo or estilo == "duas_armas") and maos_w == "2":
                    continue
                prior_agil = 0 if (estilo == "duas_armas" and "agil" in tracos_w) else 1
                anc_cc.append((0 if eh_traco_anc else 1, prior_agil, w["id"]))
        if anc_dist:
            anc_dist.sort(key=lambda x: x[0])
            ids_dist_anc = [wid for _, wid in anc_dist]
            armas_dist_ids = ids_dist_anc + [x for x in armas_dist_ids if x not in ids_dist_anc]
        if anc_cc:
            anc_cc.sort(key=lambda x: (x[0], x[1]))
            ids_cc_anc = [wid for _, _, wid in anc_cc]
            armas_cc_ids = ids_cc_anc + [x for x in armas_cc_ids if x not in ids_cc_anc]

    # ------------------------------------------------------------------
    # 1ª Passada — Compras Manuais (deduzindo diretamente de 1.500 pc)
    # ------------------------------------------------------------------
    armadura_escolhida = dados.armaduras["nenhuma_armadura"]
    if armadura_manual:
        arm_str = str(armadura_req).strip()
        if normalizar(arm_str) in ("nenhuma", "nenhum", "nenhuma_armadura", "sem_armadura"):
            armadura_escolhida = dados.armaduras["nenhuma_armadura"]
        else:
            arm_obj = dados.armaduras.get(arm_str)
            if not arm_obj:
                raise ValueError(f"Armadura desconhecida: '{arm_str}'.")
            if nao_metal and normalizar(arm_obj.get("material")) == "metal":
                raise ValueError(
                    f"Anátema de Druida: não é permitido equipar armadura de metal ('{arm_obj['nome']}')."
                )
            armadura_escolhida = arm_obj
            saldo_pc -= int(arm_obj.get("preco_pc") or 0)

    armas_compradas: list[dict[str, Any]] = []
    armas_cc_manuais_objs: list[dict[str, Any]] = []
    if armas_cc_manual:
        lista_cc = [armas_cc_req] if isinstance(armas_cc_req, str) else list(armas_cc_req)
        for item_w in lista_cc:
            wid = str(item_w).strip()
            w = dados.armas.get(wid)
            if not w or w.get("tipo_ataque") != "corpo_a_corpo" or w["id"] == "bomba_alquimica" or w.get("preco_pc") is None:
                raise ValueError(f"Arma corporal inválida para compra: '{wid}'.")
            saldo_pc -= int(w.get("preco_pc") or 0)
            armas_compradas.append(w)
            armas_cc_manuais_objs.append(w)

    if armas_dist_manual:
        lista_dist = [armas_dist_req] if isinstance(armas_dist_req, str) else list(armas_dist_req)
        for item_w in lista_dist:
            wid = str(item_w).strip()
            w = dados.armas.get(wid)
            if not w or w.get("tipo_ataque") != "distancia" or w["id"] == "bomba_alquimica" or w.get("preco_pc") is None:
                raise ValueError(f"Arma à distância inválida para compra: '{wid}'.")
            saldo_pc -= int(w.get("preco_pc") or 0)
            armas_compradas.append(w)

    escudo_escolhido: dict[str, Any] | None = None
    if escudo_manual:
        esc_str = str(escudo_req).strip()
        if normalizar(esc_str) not in ("nenhum", "nenhuma", "sem_escudo"):
            esc_obj = dados.escudos.get(esc_str)
            if not esc_obj:
                raise ValueError(f"Escudo desconhecido: '{esc_str}'.")
            if nao_metal and esc_obj["id"] in ("broquel", "escudo_de_aco", "escudo_de_corpo"):
                raise ValueError(
                    f"Anátema de Druida: não é permitido usar escudo de metal ('{esc_obj['nome']}')."
                )
            escudo_escolhido = esc_obj
            saldo_pc -= int(esc_obj.get("preco_pc") or 0)

    variados_manuais_reg: list[tuple[dict[str, Any], int]] = []
    if variados_manual:
        mapa_variados = {it["id"]: it for it in _itens_variados_loja_brutos(dados, regras_casa)}
        lista_var = [variados_req] if isinstance(variados_req, (str, dict)) else list(variados_req)
        for entrada in lista_var:
            if isinstance(entrada, str):
                iid, qtd = entrada.strip(), 1
            elif isinstance(entrada, dict):
                iid = str(entrada.get("id") or "").strip()
                try:
                    qtd = int(entrada.get("quantidade", 1))
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Quantidade inválida para o item '{iid}'.") from exc
            else:
                raise ValueError(f"Entrada inválida em equipamentos_variados: {entrada!r}.")
            if qtd < 1:
                raise ValueError(f"A quantidade do item '{iid}' deve ser pelo menos 1.")
            item_loja = mapa_variados.get(iid)
            if not item_loja:
                raise ValueError(
                    f"Equipamento variado inválido ou indisponível na compra inicial: '{iid}'."
                )
            saldo_pc -= int(item_loja["preco_pc"]) * qtd
            variados_manuais_reg.append((item_loja, qtd))

    if saldo_pc < 0:
        gasto_manual = orcamento_base_pc - saldo_pc
        raise ValueError(
            f"Orçamento inicial de {formatar_preco(orcamento_base_pc)} excedido pelos equipamentos escolhidos "
            f"(gasto: {formatar_preco(gasto_manual)})."
        )

    # ------------------------------------------------------------------
    # 2ª Passada — Categorias deixadas em Procedural usam até 90% (reservando >= 10%)
    # e mantêm o personagem dentro do limite leve (<= sobrecarregado_lim)
    # ------------------------------------------------------------------
    bonus_carga = 2 if (efeitos_talentos or {}).get("carregador_robusto") else 0
    sobrecarregado_lim = 5 + mod_for + bonus_carga
    maximo_lim = 10 + mod_for + bonus_carga

    def _saldo_procedural_disp() -> int:
        return max(0, saldo_pc - reserva_min_pc)

    def _itens_fixos_gratuitos() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        vest_f: list[dict[str, Any]] = []
        prep_f: list[dict[str, Any]] = []
        out_f: list[dict[str, Any]] = []
        if ancestralidade["id"] == "anao":
            adaga_cla = dados.armas["adaga_de_cla"]
            vest_f.append({"nome": adaga_cla["nome"], "volume_valor": float(adaga_cla.get("volume_valor") or 0.0)})
        if classe["id"] == "mago":
            out_f.append({"nome": "Grimório Inicial (Classe)", "volume_valor": 0.1})
        if classe["id"] == "alquimista":
            prep_f.append({"nome": "Livro de Fórmulas e Reagentes Infundidos", "volume_valor": 0.1})
        for item_loja, qtd_m in variados_manuais_reg:
            vol_unit = float(item_loja["volume_valor"])
            vol_tot = round(vol_unit * qtd_m, 2)
            alvo = vest_f if item_loja["eh_municao"] else out_f
            entry_m: dict[str, Any] = {"nome": item_loja["nome"], "volume_valor": vol_tot}
            if 0.05 <= vol_unit < 1.0:
                entry_m["volume_leves"] = max(1, int(round(vol_unit * 10))) * qtd_m
            alvo.append(entry_m)
        return vest_f, prep_f, out_f

    def _vol_simulando(
        arm_cand: dict[str, Any],
        armas_cand: list[dict[str, Any]],
        esc_cand: dict[str, Any] | None,
    ) -> int:
        vest_s, prep_s, out_s = _itens_fixos_gratuitos()
        if arm_cand["id"] != "nenhuma_armadura":
            vest_s.append({"nome": arm_cand["nome"], "volume_valor": float(arm_cand.get("volume_valor") or 0.0)})
        for w_c in armas_cand:
            vest_s.append({"nome": w_c["nome"], "volume_valor": float(w_c.get("volume_valor") or 0.0)})
        if esc_cand:
            vest_s.append({"nome": esc_cand["nome"], "volume_valor": float(esc_cand.get("volume_valor") or 0.0)})
        vol_tot, _ = _calcular_volume_efetivo(vest_s, prep_s, out_s, leves_por_volume=leves_por_volume)
        return vol_tot

    reserva_kit = 0 if variados_manual else 70
    if armas_cc_manual and armas_dist_manual:
        reserva_arma = 0
    else:
        pool_reserva: list[str] = []
        if not armas_cc_manual:
            pool_reserva.extend(armas_cc_ids)
        if not armas_dist_manual:
            pool_reserva.extend(armas_dist_ids)
        escudo_planejado = bool(escudo_escolhido) if escudo_manual else usa_escudo_efetivo
        armas_candidatas_preco = [
            dados.armas[wid]["preco_pc"]
            for wid in pool_reserva
            if wid in dados.armas
            and dados.armas[wid].get("preco_pc") is not None
            and grau_arma(dados.armas[wid], armas_prof) != "destreinado"
            and not (escudo_planejado and dados.armas[wid].get("tipo_ataque") == "corpo_a_corpo" and str(dados.armas[wid].get("maos")) == "2")
        ]
        reserva_arma = min(armas_candidatas_preco) if armas_candidatas_preco else 0

    if escudo_manual or not usa_escudo_efetivo:
        reserva_escudo = 0
    else:
        reserva_escudo = min(
            (dados.escudos[sid]["preco_pc"] for sid in eq_rec["escudos_ids"] if sid in dados.escudos),
            default=0,
        )

    # 1. Armadura procedural (se não escolhida manualmente)
    if not armadura_manual:
        ja_sobrecarregado_manual = _vol_simulando(armadura_escolhida, armas_compradas, escudo_escolhido) > sobrecarregado_lim
        for aid in eq_rec["armaduras_ids"]:
            arm = dados.armaduras.get(aid)
            if not arm:
                continue
            cat_key = _chave_categoria_armadura(arm["categoria"])
            if defesas.get(cat_key, "destreinado") == "destreinado":
                continue
            if nao_metal and normalizar(arm.get("material")) == "metal":
                continue
            preco = arm.get("preco_pc") or 0
            if _saldo_procedural_disp() - preco < (reserva_arma + reserva_escudo + reserva_kit):
                continue
            if not ja_sobrecarregado_manual and _vol_simulando(arm, armas_compradas, escudo_escolhido) > sobrecarregado_lim:
                continue
            armadura_escolhida = arm
            saldo_pc -= preco
            break

        # Se não couber nenhuma com reserva de kit/peso, tenta armadura leve acessível
        if armadura_escolhida["id"] == "nenhuma_armadura" and defesas["leve"] != "destreinado":
            for fallback_id in ("roupa_de_explorador", "couro", "armadura_acolchoada"):
                arm = dados.armaduras[fallback_id]
                preco = arm.get("preco_pc") or 0
                if preco <= _saldo_procedural_disp() and (
                    ja_sobrecarregado_manual
                    or _vol_simulando(arm, armas_compradas, escudo_escolhido) <= sobrecarregado_lim
                ):
                    armadura_escolhida = arm
                    saldo_pc -= preco
                    break

    # 2. Armas procedurais (para categorias deixadas em Procedural)
    usa_escudo_para_armas = bool(escudo_escolhido) if escudo_manual else usa_escudo_efetivo

    def tentar_comprar_arma(wid: str) -> bool:
        nonlocal saldo_pc
        w = dados.armas.get(wid)
        if not w:
            return False
        if w["id"] == "bomba_alquimica":
            return False  # Alquimista produz bombas com Reagentes Infundidos diários
        if usa_escudo_para_armas and w.get("tipo_ataque") == "corpo_a_corpo" and str(w.get("maos")) == "2":
            return False  # Não equipa arma corpo a corpo de 2 mãos junto de escudo
        if grau_arma(w, armas_prof) == "destreinado":
            return False
        preco = w.get("preco_pc") or 0
        if preco > 0 and preco > _saldo_procedural_disp():
            return False
        ja_sobre = _vol_simulando(armadura_escolhida, armas_compradas, escudo_escolhido) > sobrecarregado_lim
        if not ja_sobre and _vol_simulando(armadura_escolhida, [*armas_compradas, w], escudo_escolhido) > sobrecarregado_lim:
            return False
        armas_compradas.append(w)
        saldo_pc -= preco
        return True

    if not armas_cc_manual or not armas_dist_manual:
        if estilo == "distancia":
            if not armas_dist_manual:
                for wid in armas_dist_ids:
                    if tentar_comprar_arma(wid):
                        break
            if not armas_cc_manual:
                for wid in armas_cc_ids:
                    if tentar_comprar_arma(wid):
                        break
        elif estilo == "duas_armas":
            if not armas_cc_manual:
                compradas_cc_proc = 0
                for wid in armas_cc_ids:
                    if compradas_cc_proc >= 2:
                        break
                    if tentar_comprar_arma(wid):
                        compradas_cc_proc += 1
                if compradas_cc_proc < 2 and armas_cc_ids:
                    tentar_comprar_arma("adaga")
            if not armas_dist_manual:
                for wid in armas_dist_ids:
                    if tentar_comprar_arma(wid):
                        break
        else:
            if not armas_cc_manual:
                for wid in armas_cc_ids:
                    if tentar_comprar_arma(wid):
                        break
            if not armas_dist_manual:
                for wid in armas_dist_ids:
                    if tentar_comprar_arma(wid):
                        break

        # Se nenhuma arma foi comprada e há categoria procedural, garante opção gratuita (cajado/clava/funda)
        if not armas_compradas:
            candidatas_gratuitas: list[str] = []
            if not armas_cc_manual:
                candidatas_gratuitas.extend(("clava", "cajado"))
            if not armas_dist_manual:
                candidatas_gratuitas.append("funda")
            for gratuita in candidatas_gratuitas:
                if tentar_comprar_arma(gratuita):
                    break

    # 3. Escudo procedural (apenas se não houver arma corpo a corpo de 2 mãos equipada)
    empunha_cc_2m = any(
        w.get("tipo_ataque") == "corpo_a_corpo" and str(w.get("maos")) == "2" for w in armas_compradas
    )
    if not escudo_manual and usa_escudo_efetivo and not empunha_cc_2m:
        ja_sobre_esc = _vol_simulando(armadura_escolhida, armas_compradas, None) > sobrecarregado_lim
        for sid in eq_rec["escudos_ids"]:
            esc = dados.escudos.get(sid)
            if not esc:
                continue
            if nao_metal and sid in ("broquel", "escudo_de_aco", "escudo_de_corpo"):
                continue
            preco = esc.get("preco_pc") or 0
            if preco > _saldo_procedural_disp():
                continue
            if not ja_sobre_esc and _vol_simulando(armadura_escolhida, armas_compradas, esc) > sobrecarregado_lim:
                continue
            escudo_escolhido = esc
            saldo_pc -= preco
            break

    # 4. Itens Vestidos, Preparados e Outros Itens
    itens_vestidos: list[dict[str, Any]] = []
    itens_preparados: list[dict[str, Any]] = []
    outros_itens: list[dict[str, Any]] = []
    variados_aplicados: list[dict[str, Any]] = []

    def registrar_item(lista: list[dict], nome: str, quantidade: int, volume: str, volume_valor: float, preco_pc: int | None = None, investido: bool = False) -> None:
        item = {
            "nome": nome,
            "quantidade": quantidade,
            "volume": volume,
            "volume_valor": volume_valor,
            "preco_pc": preco_pc,
        }
        if lista is itens_vestidos:
            item["investido"] = investido
        lista.append(item)

    armadura_resumo = formatar_armadura_resumo(armadura_escolhida)
    if armadura_escolhida["id"] != "nenhuma_armadura":
        registrar_item(
            itens_vestidos,
            armadura_resumo,
            1,
            armadura_escolhida["volume"],
            float(armadura_escolhida.get("volume_valor") or 0.0),
            armadura_escolhida.get("preco_pc"),
        )

    for w in armas_compradas:
        registrar_item(
            itens_vestidos,
            _formatar_arma_inventario(w),
            1,
            w["volume"],
            float(w.get("volume_valor") or 0.0),
            w.get("preco_pc"),
        )
        if not variados_manual:
            mun = _municao_para_arma(dados, w)
            if mun:
                # 2 lotes (20 munições) quando houver saldo dentro dos 90% e peso leve, senão 1 lote
                disp_m = _saldo_procedural_disp()
                vol_atual_m = _calcular_volume_efetivo(
                    itens_vestidos, itens_preparados, outros_itens, leves_por_volume=leves_por_volume
                )[0]
                lotes = 0
                for cand_lotes in (2, 1):
                    if mun["preco_pc"] * cand_lotes > disp_m:
                        continue
                    sim_m = {"nome": mun["nome"], "volume_valor": round(0.1 * cand_lotes, 2), "volume_leves": cand_lotes}
                    vol_c = _calcular_volume_efetivo(
                        [*itens_vestidos, sim_m], itens_preparados, outros_itens, leves_por_volume=leves_por_volume
                    )[0]
                    if vol_atual_m > sobrecarregado_lim or vol_c <= sobrecarregado_lim:
                        lotes = cand_lotes
                        break
                if lotes > 0:
                    saldo_pc -= mun["preco_pc"] * lotes
                    qtd_mun = lotes * mun["quantidade"]
                    registrar_item(
                        itens_vestidos,
                        f"{mun['nome']} (Qtd: {qtd_mun})",
                        qtd_mun,
                        "L" if lotes == 1 else f"{lotes}L",
                        round(0.1 * lotes, 2),
                        mun["preco_pc"] * lotes,
                    )
                    variados_aplicados.append(
                        {"id": mun["id"], "nome": mun["nome"], "quantidade": lotes, "preco_pc": mun["preco_pc"] * lotes}
                    )

    if escudo_escolhido:
        registrar_item(
            itens_vestidos,
            f"{escudo_escolhido['nome']} (+{escudo_escolhido['bonus_ca']} CA, Dureza {escudo_escolhido['dureza']}, PV {escudo_escolhido['pv']})",
            1,
            escudo_escolhido["volume"],
            float(escudo_escolhido.get("volume_valor") or 0.0),
            escudo_escolhido.get("preco_pc"),
        )

    # Anão recebe Adaga de Clã gratuita no 1º nível; Mago e Alquimista recebem itens gratuitos de classe
    if ancestralidade["id"] == "anao":
        adaga_cla = dados.armas["adaga_de_cla"]
        if grau_arma(adaga_cla, armas_prof) != "destreinado":
            armas_compradas.append(adaga_cla)
        registrar_item(itens_vestidos, _formatar_arma_inventario(adaga_cla, sufixo="Ancestral"), 1, adaga_cla["volume"], float(adaga_cla["volume_valor"]), 0)

    if classe["id"] == "mago":
        registrar_item(outros_itens, "Grimório Inicial (Classe)", 1, "L", 0.1, 0)

    if classe["id"] == "alquimista":
        reagentes_qtd = max(1, 1 + mod_int)
        registrar_item(itens_preparados, f"Livro de Fórmulas e Reagentes Infundidos (Qtd: {reagentes_qtd} lotes/dia)", reagentes_qtd, "L", 0.1, 0)

    if variados_manual:
        for item_loja, qtd in variados_manuais_reg:
            vol_unit = float(item_loja["volume_valor"])
            vol_total_it = round(vol_unit * qtd, 2)
            if qtd == 1:
                vol_str = str(item_loja["volume"])
            elif 0.05 <= vol_unit < 1.0:
                vol_str = f"{qtd}L"
            elif vol_total_it == 0:
                vol_str = "—"
            else:
                vol_str = str(int(round(vol_total_it)))
            preco_total_it = int(item_loja["preco_pc"]) * qtd
            if item_loja["eh_municao"]:
                qtd_mun = qtd * int(item_loja["quantidade_pacote"] or 1)
                registrar_item(
                    itens_vestidos,
                    f"{item_loja['nome']} (Qtd: {qtd_mun})",
                    qtd_mun,
                    vol_str,
                    vol_total_it,
                    preco_total_it,
                )
            else:
                qtd_efetiva = qtd * int(item_loja["quantidade_pacote"] or 1)
                registrar_item(
                    outros_itens,
                    _formatar_item_geral_inventario(item_loja, qtd_efetiva),
                    qtd_efetiva,
                    vol_str,
                    vol_total_it,
                    preco_total_it,
                )
            variados_aplicados.append(
                {
                    "id": item_loja["id"],
                    "nome": item_loja["nome"],
                    "quantidade": qtd,
                    "preco_pc": preco_total_it,
                }
            )
    else:
        ids_variados_comprados: set[str] = set()
        ja_sobre_var = _calcular_volume_efetivo(
            itens_vestidos, itens_preparados, outros_itens, leves_por_volume=leves_por_volume
        )[0] > sobrecarregado_lim

        def _tentar_comprar_variado_proc(
            iid: str,
            qtd: int = 1,
            *,
            destino: list[dict[str, Any]] | None = None,
        ) -> bool:
            nonlocal saldo_pc
            if iid in ids_variados_comprados:
                return False
            gitem_bruto = dados.itens_gerais.get(iid)
            if not gitem_bruto:
                return False
            gitem = aplicar_override_item_casa(gitem_bruto, regras_casa)
            preco_unit = int(gitem.get("preco_pc") or 0)
            preco_tot = preco_unit * qtd
            if preco_tot > _saldo_procedural_disp():
                return False

            vol_unit = float(gitem.get("volume_valor") or 0.0)
            vol_tot = round(vol_unit * qtd, 2)
            lista_alvo = outros_itens if destino is None else destino
            sim_item: dict[str, Any] = {"nome": gitem["nome"], "volume_valor": vol_tot}
            if 0.05 <= vol_unit < 1.0:
                sim_item["volume_leves"] = max(1, int(round(vol_unit * 10))) * qtd
            if not ja_sobre_var:
                vol_sim = _calcular_volume_efetivo(
                    itens_vestidos,
                    [*itens_preparados, sim_item] if lista_alvo is itens_preparados else itens_preparados,
                    [*outros_itens, sim_item] if lista_alvo is outros_itens else outros_itens,
                    leves_por_volume=leves_por_volume,
                )[0]
                if vol_sim > sobrecarregado_lim:
                    return False

            if qtd == 1:
                vol_str = str(gitem["volume"])
            elif 0.05 <= vol_unit < 1.0:
                vol_str = f"{qtd}L"
            elif vol_tot == 0:
                vol_str = "—"
            else:
                vol_str = str(int(round(vol_tot)))

            saldo_pc -= preco_tot
            qtd_ef = qtd * int(gitem.get("quantidade_pacote") or 1)
            registrar_item(
                lista_alvo,
                _formatar_item_geral_inventario(gitem, qtd_ef),
                qtd_ef,
                vol_str,
                vol_tot,
                preco_tot,
            )
            variados_aplicados.append(
                {"id": iid, "nome": gitem["nome"], "quantidade": qtd, "preco_pc": preco_tot}
            )
            ids_variados_comprados.add(iid)
            return True

        # 4.1 Básico de viagem comprado item a item (Etapa 55: sem kits compostos).
        # A mochila vem primeiro para liberar a isenção de 2 Volumes.
        for iid_basico, qtd_basico in (
            ("mochila", 1),
            ("esteira_de_dormir", 1),
            ("cantil", 1),
            ("pederneira_e_isqueiro", 1),
            ("racoes_1_semana", 1),
            ("tocha", 5),
            ("sabao", 1),
        ):
            _tentar_comprar_variado_proc(iid_basico, qtd_basico, destino=outros_itens)

        # 4.2 Ferramentas essenciais da classe/conceito/biografia
        sub_id = subclasse["id"] if subclasse else ""
        bio_id = biografia["id"] if biografia else ""
        for fid in _ferramenta_essencial(classe["id"], conceito["id"], sub_id, bio_id):
            _tentar_comprar_variado_proc(fid, 1, destino=itens_preparados)

        # 4.3 Equipamentos de viagem e utilidades temáticas até ~90% do orçamento (sem sobrecarga)
        for iid_v, qtd_v in _pool_equipamentos_viagem(classe["id"], conceito, bio_id, bool(escudo_escolhido)):
            if _saldo_procedural_disp() <= 0:
                break
            dest_v = itens_preparados if iid_v in ("bandoleira", "ferramentas_de_curandeiro") else outros_itens
            _tentar_comprar_variado_proc(iid_v, qtd_v, destino=dest_v)

    volume_total, volume_leves_soltos = _calcular_volume_efetivo(
        itens_vestidos, itens_preparados, outros_itens, leves_por_volume=leves_por_volume
    )

    return {
        "armadura": armadura_escolhida,
        "armadura_resumo": armadura_resumo,
        "escudo": escudo_escolhido,
        "armas": armas_compradas,
        "itens_vestidos": itens_vestidos,
        "itens_preparados": itens_preparados,
        "outros_itens": outros_itens,
        "volume_total": float(volume_total),
        "volume_leves_soltos": volume_leves_soltos,
        "itens_leves_por_volume": leves_por_volume,
        "volume_sobrecarregado": sobrecarregado_lim,
        "volume_maximo": maximo_lim,
        "esta_sobrecarregado": volume_total > sobrecarregado_lim,
        "orcamento_pc": orcamento_base_pc,
        "gasto_pc": orcamento_base_pc - saldo_pc,
        "saldo_pc": saldo_pc,
        "riqueza": pc_para_moedas(saldo_pc),
        "escolhas_equipamentos": {
            "armadura_id": "nenhuma" if armadura_escolhida["id"] == "nenhuma_armadura" else armadura_escolhida["id"],
            "escudo_id": escudo_escolhido["id"] if escudo_escolhido else None,
            "armas_corpo_a_corpo_ids": [w["id"] for w in armas_compradas if w.get("tipo_ataque") == "corpo_a_corpo"],
            "armas_distancia_ids": [w["id"] for w in armas_compradas if w.get("tipo_ataque") == "distancia"],
            "equipamentos_variados": variados_aplicados,
            "categorias_manuais": {
                "armadura": armadura_manual,
                "escudo": escudo_manual,
                "armas_corpo_a_corpo": armas_cc_manual,
                "armas_distancia": armas_dist_manual,
                "equipamentos_variados": variados_manual,
            },
        },
    }
