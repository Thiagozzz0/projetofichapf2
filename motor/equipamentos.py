"""Proficiências de combate e comprador procedural de equipamentos (orçamento 15 po)."""

from __future__ import annotations

from typing import Any

from .dados import BaseDados
from .util import grau_normalizado, normalizar, pc_para_moedas


ORCAMENTO_INICIAL_PC = 1500  # 15 po = 150 pp = 1.500 pc


def calcular_proficiencias_combate(
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
) -> dict[str, Any]:
    """Resolve as proficiências de armaduras e armas considerando classe e subclasse."""
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

    armas = {
        "simples": grau_normalizado(ataques_brutos.get("armas_simples")),
        "marcial": grau_normalizado(ataques_brutos.get("armas_marciais")),
        "avancada": grau_normalizado(ataques_brutos.get("armas_avancadas")),
        "desarmado": grau_normalizado(ataques_brutos.get("ataques_desarmados")),
        "bombas_alquimicas": grau_normalizado(ataques_brutos.get("bombas_alquimicas")),
        "especificas_lista": lista_esp,
        "especificas_grau": grau_esp,
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

    if arma.get("id") == "bomba_alquimica":
        return profs_armas.get("bombas_alquimicas", "destreinado") or profs_armas.get("marcial", "destreinado")
    if "desarmado" in cat:
        return profs_armas["desarmado"]
    if nome_norm in profs_armas["especificas_lista"]:
        return profs_armas["especificas_grau"]
    if "simples" in cat:
        return profs_armas["simples"]
    if "marcial" in cat:
        return profs_armas["marcial"]
    if "avancada" in cat:
        return profs_armas["avancada"]
    return "destreinado"


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


def _ferramenta_essencial(classe_id: str, conceito_id: str) -> list[str]:
    mapa = {
        "alquimista": ["ferramentas_de_alquimista", "livro_basico_de_manufatura"],
        "bardo": ["instrumento_musical_portatil"],
        "clerigo": ["simbolo_religioso_madeira"],
        "druida": ["azevinho_e_visco"],
        "ladino": ["ferramentas_de_ladrao"],
        "mago": ["bolsa_de_componentes_materiais", "conjunto_de_escrita"],
    }
    itens = list(mapa.get(classe_id, []))
    if "cirurgiao" in conceito_id or "curandeiro" in conceito_id:
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
) -> dict[str, Any]:
    """Executa a compra procedural dentro de 15 po (1.500 pc) e calcula o Volume."""
    saldo_pc = ORCAMENTO_INICIAL_PC
    defesas = profs_combate["defesas"]
    armas_prof = profs_combate["armas"]
    nao_metal = profs_combate["restricao_nao_metal"]

    eq_rec = conceito["equipamento_recomendado"]
    estilo = eq_rec["estilo_empunhadura"]

    # Reserva mínima para comprar pelo menos o kit de aventureiro (70 pc) e 1 arma viável
    reserva_kit = 70
    armas_candidatas_preco = [
        dados.armas[wid]["preco_pc"]
        for wid in eq_rec["armas_corpo_a_corpo_ids"] + eq_rec["armas_distancia_ids"]
        if wid in dados.armas and dados.armas[wid].get("preco_pc") is not None
        and grau_arma(dados.armas[wid], armas_prof) != "destreinado"
    ]
    reserva_arma = min(armas_candidatas_preco) if armas_candidatas_preco else 0
    reserva_escudo = (
        min(
            (dados.escudos[sid]["preco_pc"] for sid in eq_rec["escudos_ids"] if sid in dados.escudos),
            default=0,
        )
        if eq_rec["usa_escudo"]
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
        if grau_arma(w, armas_prof) == "destreinado":
            return False
        preco = w.get("preco_pc") or 0
        if preco > saldo_pc:
            return False
        armas_compradas.append(w)
        saldo_pc -= preco
        return True

    if estilo == "distancia":
        for wid in eq_rec["armas_distancia_ids"]:
            if tentar_comprar_arma(wid):
                break
        for wid in eq_rec["armas_corpo_a_corpo_ids"]:
            if tentar_comprar_arma(wid):
                break
    elif estilo == "duas_armas":
        for wid in eq_rec["armas_corpo_a_corpo_ids"]:
            if len(armas_compradas) >= 2:
                break
            tentar_comprar_arma(wid)
        if len(armas_compradas) < 2 and eq_rec["armas_corpo_a_corpo_ids"]:
            # Caso só tenha 1 arma viável no saldo, permite par da arma barata se houver saldo
            tentar_comprar_arma("adaga")
        for wid in eq_rec["armas_distancia_ids"]:
            if tentar_comprar_arma(wid):
                break
    else:
        for wid in eq_rec["armas_corpo_a_corpo_ids"]:
            if tentar_comprar_arma(wid):
                break
        for wid in eq_rec["armas_distancia_ids"]:
            if tentar_comprar_arma(wid):
                break

    # Se não conseguiu nenhuma arma (ex: classe conjuradora sem saldo), cajado/funda custam 0 pc
    if not armas_compradas:
        for gratuita in ("cajado", "clava", "funda"):
            if tentar_comprar_arma(gratuita):
                break

    # 3. Escudo
    escudo_escolhido: dict[str, Any] | None = None
    if eq_rec["usa_escudo"]:
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
        armas_compradas.append(adaga_cla)
        registrar_item(itens_vestidos, f"{adaga_cla['nome']} (Ancestral)", 1, adaga_cla["volume"], float(adaga_cla["volume_valor"]), 0)

    if classe["id"] == "mago":
        registrar_item(outros_itens, "Grimório Inicial (Classe)", 1, "L", 0.1, 0)

    if classe["id"] == "alquimista":
        reagentes_qtd = max(1, 1 + mod_int)
        registrar_item(itens_preparados, "Livro de Fórmulas e Reagentes Infundidos", reagentes_qtd, "L", 0.1, 0)

    # Ferramentas essenciais da classe
    for fid in _ferramenta_essencial(classe["id"], conceito["id"]):
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

    # Cálculo exato de Volume PF2E: inteiros + floor(qtd_leves / 10)
    todos = itens_vestidos + itens_preparados + outros_itens
    soma_inteiros = 0
    soma_leves = 0
    for item in todos:
        vv = float(item.get("volume_valor") or 0.0)
        if vv >= 1.0:
            soma_inteiros += int(round(vv))
        elif 0.05 <= vv < 1.0:
            soma_leves += max(1, int(round(vv * 10)))

    volume_total = soma_inteiros + (soma_leves // 10)
    sobrecarregado_lim = 5 + mod_for
    maximo_lim = 10 + mod_for

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
