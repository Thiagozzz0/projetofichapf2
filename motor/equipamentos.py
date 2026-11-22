"""Proficiências de combate e comprador procedural de equipamentos (orçamento 15 po)."""

from __future__ import annotations

from typing import Any

from .dados import BaseDados
from .util import grau_normalizado, normalizar, pc_para_moedas


ORCAMENTO_INICIAL_PC = 1500  # 15 po = 150 pp = 1.500 pc

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


def calcular_proficiencias_combate(
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    talentos_classe_ids: list[str] | None = None,
    divindade: dict[str, Any] | None = None,
    efeitos_talentos: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve as proficiências de armaduras e armas considerando classe, subclasse, talentos e divindade."""
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

    tal_anc_id = efeitos.get("talento_ancestral_id") or ""
    armas_anc_lista, traco_anc_armas = _FAMILIARIDADE_ARMAS_ANCESTRAL.get(tal_anc_id, ([], None))

    armas = {
        "simples": simples_g,
        "marcial": marcial_g,
        "avancada": avancada_g,
        "desarmado": desarmado_grau,
        "bombas_alquimicas": grau_normalizado(ataques_brutos.get("bombas_alquimicas")),
        "armas_traco_monge": "treinado" if armas_monge_treinadas else "destreinado",
        "especificas_lista": lista_esp,
        "especificas_grau": grau_esp,
        "armas_ancestrais_lista": list(armas_anc_lista),
        "traco_ancestral_armas": traco_anc_armas,
        "armamento_nao_convencional": tal_anc_id == "armamento_nao_convencional",
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
        return "treinado"
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


def _ferramenta_essencial(classe_id: str, conceito_id: str, subclasse_id: str = "") -> list[str]:
    mapa = {
        "alquimista": ["ferramentas_de_alquimista", "livro_basico_de_manufatura"],
        "bardo": ["instrumento_musical_portatil"],
        "clerigo": ["simbolo_religioso_madeira"],
        "druida": ["azevinho_e_visco"],
        "ladino": ["ferramentas_de_ladrao"],
        "mago": ["bolsa_de_componentes_materiais", "conjunto_de_escrita"],
    }
    itens = list(mapa.get(classe_id, []))
    if subclasse_id == "cirurgiao" or any(
        termo in conceito_id for termo in ("cirurgiao", "curandeiro", "medico", "hospitalario")
    ):
        itens.append("ferramentas_de_curandeiro")
    return itens


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
) -> dict[str, Any]:
    """Executa a compra procedural dentro de 15 po (1.500 pc) e calcula o Volume."""
    saldo_pc = ORCAMENTO_INICIAL_PC
    defesas = profs_combate["defesas"]
    armas_prof = profs_combate["armas"]
    nao_metal = profs_combate["restricao_nao_metal"]

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

    # Reserva mínima para comprar pelo menos o kit de aventureiro (70 pc) e 1 arma viável
    reserva_kit = 70
    armas_candidatas_preco = [
        dados.armas[wid]["preco_pc"]
        for wid in armas_cc_ids + armas_dist_ids
        if wid in dados.armas
        and dados.armas[wid].get("preco_pc") is not None
        and grau_arma(dados.armas[wid], armas_prof) != "destreinado"
        and not (usa_escudo_efetivo and dados.armas[wid].get("tipo_ataque") == "corpo_a_corpo" and str(dados.armas[wid].get("maos")) == "2")
    ]
    reserva_arma = min(armas_candidatas_preco) if armas_candidatas_preco else 0
    reserva_escudo = (
        min(
            (dados.escudos[sid]["preco_pc"] for sid in eq_rec["escudos_ids"] if sid in dados.escudos),
            default=0,
        )
        if usa_escudo_efetivo
        else 0
    )

    # 1. Armadura
    armadura_escolhida = dados.armaduras["nenhuma_armadura"]
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
        if saldo_pc - preco >= (reserva_arma + reserva_escudo + reserva_kit):
            armadura_escolhida = arm
            saldo_pc -= preco
            break

    # Se não couber nenhuma com reserva de kit, ainda assim garante armadura acessível
    if armadura_escolhida["id"] == "nenhuma_armadura" and defesas["leve"] != "destreinado":
        for fallback_id in ("roupa_de_explorador", "couro", "armadura_acolchoada"):
            arm = dados.armaduras[fallback_id]
            preco = arm.get("preco_pc") or 0
            if preco <= saldo_pc:
                armadura_escolhida = arm
                saldo_pc -= preco
                break

    # 2. Armas
    armas_compradas: list[dict[str, Any]] = []

    def tentar_comprar_arma(wid: str) -> bool:
        nonlocal saldo_pc
        w = dados.armas.get(wid)
        if not w:
            return False
        if w["id"] == "bomba_alquimica":
            return False  # Alquimista produz bombas com Reagentes Infundidos diários
        if usa_escudo_efetivo and w.get("tipo_ataque") == "corpo_a_corpo" and str(w.get("maos")) == "2":
            return False  # Não equipa arma corpo a corpo de 2 mãos junto de escudo
        if grau_arma(w, armas_prof) == "destreinado":
            return False
        preco = w.get("preco_pc") or 0
        if preco > saldo_pc:
            return False
        armas_compradas.append(w)
        saldo_pc -= preco
        return True

    if estilo == "distancia":
        for wid in armas_dist_ids:
            if tentar_comprar_arma(wid):
                break
        for wid in armas_cc_ids:
            if tentar_comprar_arma(wid):
                break
    elif estilo == "duas_armas":
        for wid in armas_cc_ids:
            if len(armas_compradas) >= 2:
                break
            tentar_comprar_arma(wid)
        if len(armas_compradas) < 2 and armas_cc_ids:
            # Caso só tenha 1 arma viável no saldo, permite par da arma barata se houver saldo
            tentar_comprar_arma("adaga")
        for wid in armas_dist_ids:
            if tentar_comprar_arma(wid):
                break
    else:
        for wid in armas_cc_ids:
            if tentar_comprar_arma(wid):
                break
        for wid in armas_dist_ids:
            if tentar_comprar_arma(wid):
                break

    # Se não conseguiu nenhuma arma (ex: classe conjuradora sem saldo), cajado/funda custam 0 pc
    if not armas_compradas:
        for gratuita in ("cajado", "clava", "funda"):
            if tentar_comprar_arma(gratuita):
                break

    # 3. Escudo (apenas se não houver arma corpo a corpo de 2 mãos equipada)
    escudo_escolhido: dict[str, Any] | None = None
    empunha_cc_2m = any(
        w.get("tipo_ataque") == "corpo_a_corpo" and str(w.get("maos")) == "2" for w in armas_compradas
    )
    if usa_escudo_efetivo and not empunha_cc_2m:
        for sid in eq_rec["escudos_ids"]:
            esc = dados.escudos.get(sid)
            if not esc:
                continue
            if nao_metal and "aco" in sid:
                continue
            preco = esc.get("preco_pc") or 0
            if preco <= saldo_pc:
                escudo_escolhido = esc
                saldo_pc -= preco
                break

    # 4. Itens Vestidos, Preparados e Outros Itens
    itens_vestidos: list[dict[str, Any]] = []
    itens_preparados: list[dict[str, Any]] = []
    outros_itens: list[dict[str, Any]] = []

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

    if armadura_escolhida["id"] != "nenhuma_armadura":
        registrar_item(
            itens_vestidos,
            armadura_escolhida["nome"],
            1,
            armadura_escolhida["volume"],
            float(armadura_escolhida.get("volume_valor") or 0.0),
            armadura_escolhida.get("preco_pc"),
        )

    for w in armas_compradas:
        registrar_item(
            itens_vestidos,
            w["nome"],
            1,
            w["volume"],
            float(w.get("volume_valor") or 0.0),
            w.get("preco_pc"),
        )
        mun = _municao_para_arma(dados, w)
        if mun:
            # 2 lotes (20 munições) quando houver saldo, senão 1 lote
            lotes = 2 if (mun["preco_pc"] * 2) <= saldo_pc else (1 if mun["preco_pc"] <= saldo_pc else 0)
            if lotes > 0:
                saldo_pc -= mun["preco_pc"] * lotes
                registrar_item(
                    itens_vestidos,
                    f"{mun['nome']} ({lotes * mun['quantidade']})",
                    lotes * mun["quantidade"],
                    "L" if lotes == 1 else f"{lotes}L",
                    round(0.1 * lotes, 2),
                    mun["preco_pc"] * lotes,
                )

    if escudo_escolhido:
        registrar_item(
            itens_vestidos,
            escudo_escolhido["nome"],
            1,
            escudo_escolhido["volume"],
            float(escudo_escolhido.get("volume_valor") or 0.0),
            escudo_escolhido.get("preco_pc"),
        )

    # Anão recebe Adaga de Clã gratuita no 1º nível; Mago recebe Grimório gratuito
    if ancestralidade["id"] == "anao":
        adaga_cla = dados.armas["adaga_de_cla"]
        if grau_arma(adaga_cla, armas_prof) != "destreinado":
            armas_compradas.append(adaga_cla)
        registrar_item(itens_vestidos, f"{adaga_cla['nome']} (Ancestral)", 1, adaga_cla["volume"], float(adaga_cla["volume_valor"]), 0)

    if classe["id"] == "mago":
        registrar_item(outros_itens, "Grimório Inicial (Classe)", 1, "L", 0.1, 0)

    if classe["id"] == "alquimista":
        reagentes_qtd = max(1, 1 + mod_int)
        registrar_item(itens_preparados, "Livro de Fórmulas e Reagentes Infundidos", reagentes_qtd, "L", 0.1, 0)

    # Ferramentas essenciais da classe
    sub_id = subclasse["id"] if subclasse else ""
    for fid in _ferramenta_essencial(classe["id"], conceito["id"], sub_id):
        fitem = dados.itens_gerais.get(fid)
        if fitem and (fitem.get("preco_pc") or 0) <= saldo_pc:
            saldo_pc -= fitem.get("preco_pc") or 0
            registrar_item(
                itens_preparados,
                fitem["nome"],
                1,
                fitem["volume"],
                float(fitem.get("volume_valor") or 0.0),
                fitem.get("preco_pc"),
            )

    # Kit de aventureiro (mochila + bens básicos)
    kit_av = dados.itens_gerais.get("kit_de_aventureiro")
    if kit_av and kit_av["preco_pc"] <= saldo_pc:
        saldo_pc -= kit_av["preco_pc"]
        registrar_item(
            outros_itens,
            kit_av["nome"],
            1,
            kit_av["volume"],
            float(kit_av.get("volume_valor") or 0.0),
            kit_av["preco_pc"],
        )

    # Cálculo exato de Volume PF2E: inteiros + floor(qtd_leves / 10) + isenção da mochila (2 Vol)
    def _somar_volumes(lista_itens: list[dict[str, Any]]) -> tuple[int, int]:
        inteiros, leves = 0, 0
        for item in lista_itens:
            vv = float(item.get("volume_valor") or 0.0)
            if vv >= 1.0:
                inteiros += int(round(vv))
            elif 0.05 <= vv < 1.0:
                leves += max(1, int(round(vv * 10)))
        return inteiros, leves

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
            folga_leves = (2 - int_outros) * 10
            int_outros_efetivo = 0
            lev_outros_efetivo = max(0, lev_outros - folga_leves)
    else:
        int_outros_efetivo, lev_outros_efetivo = int_outros, lev_outros

    soma_inteiros = int_vest + int_outros_efetivo
    soma_leves = lev_vest + lev_outros_efetivo
    volume_total = soma_inteiros + (soma_leves // 10)

    bonus_carga = 2 if (efeitos_talentos or {}).get("carregador_robusto") else 0
    sobrecarregado_lim = 5 + mod_for + bonus_carga
    maximo_lim = 10 + mod_for + bonus_carga

    return {
        "armadura": armadura_escolhida,
        "escudo": escudo_escolhido,
        "armas": armas_compradas,
        "itens_vestidos": itens_vestidos,
        "itens_preparados": itens_preparados,
        "outros_itens": outros_itens,
        "volume_total": float(volume_total),
        "volume_leves_soltos": soma_leves % 10,
        "volume_sobrecarregado": sobrecarregado_lim,
        "volume_maximo": maximo_lim,
        "esta_sobrecarregado": volume_total > sobrecarregado_lim,
        "gasto_pc": ORCAMENTO_INICIAL_PC - saldo_pc,
        "saldo_pc": saldo_pc,
        "riqueza": pc_para_moedas(saldo_pc),
    }
