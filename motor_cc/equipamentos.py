"""Regras de equipamentos, ouro inicial, conversão de moedas e Sobrecarga (SB) de C&C."""

from __future__ import annotations

import random
import re
from typing import Any

from motor_cc.dados import carregar_equipamentos, mapa_todos_equipamentos


def _rolar_expressao_ouro(expr: str, modo: str = "media", seed: int | None = None) -> int:
    """Avalia expressões como '3d8x10' nos modos 'rolar', 'media' ou 'maximo'."""
    m = re.match(r"^(\d+)d(\d+)(?:x(\d+))?$", expr.strip(), re.IGNORECASE)
    if not m:
        raise ValueError(f"Expressão de ouro inicial inválida: {expr!r}")
    qtd = int(m.group(1))
    faces = int(m.group(2))
    mult = int(m.group(3) or 1)

    if modo == "maximo":
        return qtd * faces * mult
    if modo == "media":
        return int(round(qtd * ((faces + 1) / 2.0) * mult))
    rng = random.Random(seed)
    return sum(rng.randint(1, faces) for _ in range(qtd)) * mult


def obter_ouro_inicial(
    classe_id: str,
    modo: str = "media",
    ouro_manual_po: float | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    """Determina o ouro inicial em peças de ouro (po) conforme a tabela da classe."""
    eq = carregar_equipamentos()
    tabela = eq.get("moedas", {}).get("ouro_inicial_por_classe", {})
    regra = tabela.get(classe_id, {"rolagem": "3d6x10", "min_po": 30, "max_po": 180})

    if ouro_manual_po is not None:
        valor_po = max(0.0, float(ouro_manual_po))
        origem = "manual"
    else:
        valor_po = float(_rolar_expressao_ouro(regra["rolagem"], modo=modo, seed=seed))
        origem = modo

    return {
        "rolagem_oficial": regra["rolagem"],
        "min_po": regra.get("min_po"),
        "max_po": regra.get("max_po"),
        "inicial_po": round(valor_po, 2),
        "inicial_pc": int(round(valor_po * 100)),
        "origem": origem,
    }


def converter_pc_em_moedas(total_pc: int) -> dict[str, int]:
    """Converte peças de cobre (pc) em Ouro (100 pc), Prata (10 pc) e Cobre (1 pc)."""
    negativo = total_pc < 0
    restante = abs(int(total_pc))
    ouro = restante // 100
    restante %= 100
    prata = restante // 10
    cobre = restante % 10
    if negativo:
        ouro = -ouro
    return {"ouro": ouro, "prata": prata, "cobre": cobre, "total_pc": int(total_pc)}


def calcular_categoria_sobrecarga(
    valor_forca: int,
    forca_primario: bool,
    constituicao_primario: bool,
) -> int:
    """Calcula a Categoria de Sobrecarga (CS): FOR + 6 (ambos primários) / +3 (um primário) / +0."""
    bonus = 0
    if forca_primario and constituicao_primario:
        bonus = 6
    elif forca_primario or constituicao_primario:
        bonus = 3
    return max(1, int(valor_forca) + bonus)


def classificar_sobrecarga(
    sb_total: float,
    cs: int,
    movimento_base_m: float,
) -> dict[str, Any]:
    """Classifica o nível de carga (Descarregado, Carregado ou Sobrecarregado) e ajusta o movimento."""
    if sb_total <= cs:
        return {
            "categoria_id": "descarregado",
            "categoria_nome": "Descarregado",
            "sb_total": round(sb_total, 1),
            "categoria_sobrecarga_cs": cs,
            "limite_carregado": cs * 3,
            "movimento_ajustado_m": movimento_base_m,
            "penalidade_nd_destreza": 0,
            "perde_bonus_des_ca": False,
            "efeito": "Sem penalidades.",
        }
    if sb_total <= cs * 3:
        mov_adj = max(1.5, float(movimento_base_m) - 3.0)
        return {
            "categoria_id": "carregado",
            "categoria_nome": "Carregado",
            "sb_total": round(sb_total, 1),
            "categoria_sobrecarga_cs": cs,
            "limite_carregado": cs * 3,
            "movimento_ajustado_m": mov_adj,
            "penalidade_nd_destreza": 2,
            "perde_bonus_des_ca": False,
            "efeito": "-3 m no Movimento (mínimo 1,5 m) e +2 no ND de testes baseados em Destreza.",
        }
    return {
        "categoria_id": "sobrecarregado",
        "categoria_nome": "Sobrecarregado",
        "sb_total": round(sb_total, 1),
        "categoria_sobrecarga_cs": cs,
        "limite_carregado": cs * 3,
        "movimento_ajustado_m": 1.5,
        "penalidade_nd_destreza": None,
        "perde_bonus_des_ca": True,
        "efeito": "Movimento reduzido para 1,5 m, falha automática em testes de Destreza e perde bônus de Destreza na CA.",
    }


def processar_equipamentos(
    classe_id: str,
    valor_forca: int,
    forca_primario: bool,
    constituicao_primario: bool,
    movimento_base_m: float,
    armadura_id: str | None = None,
    escudo_id: str | None = None,
    elmo_id: str | None = None,
    armas_ids: list[str] | None = None,
    itens_ids: list[str] | None = None,
    modo_ouro: str = "media",
    ouro_manual_po: float | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    """Valida itens selecionados, calcula custo total, saldo em moedas e Sobrecarga (SB)."""
    catalogo = mapa_todos_equipamentos()

    def _buscar(item_id: str | None, esperado_cat: str | tuple[str, ...] | None = None) -> dict[str, Any] | None:
        if not item_id:
            return None
        if item_id not in catalogo:
            raise ValueError(f"Item de equipamento desconhecido: {item_id!r}")
        it = catalogo[item_id]
        if esperado_cat is not None:
            cats = (esperado_cat,) if isinstance(esperado_cat, str) else esperado_cat
            if it["categoria"] not in cats:
                raise ValueError(f"Item {item_id!r} pertence à categoria {it['categoria']!r}, esperado {cats}.")
        return it

    armadura = _buscar(armadura_id, "armaduras")
    escudo = _buscar(escudo_id, "escudos")
    elmo = _buscar(elmo_id, "elmos")

    armas: list[dict[str, Any]] = []
    for aid in (armas_ids or []):
        arma = _buscar(aid, ("armas_corpo_a_corpo", "armas_projeteis"))
        if arma:
            armas.append(arma)

    outros_itens: list[dict[str, Any]] = []
    for iid in (itens_ids or []):
        it = _buscar(iid)
        if it:
            outros_itens.append(it)

    todos_itens = [x for x in [armadura, escudo, elmo] if x is not None] + armas + outros_itens

    custo_total_pc = sum(int(x.get("custo_pc") or 0) for x in todos_itens)
    sb_total = sum(float(x.get("sb") or 0) for x in todos_itens)

    ouro_info = obter_ouro_inicial(classe_id, modo=modo_ouro, ouro_manual_po=ouro_manual_po, seed=seed)
    saldo_pc = ouro_info["inicial_pc"] - custo_total_pc
    moedas_restantes = converter_pc_em_moedas(saldo_pc)

    cs = calcular_categoria_sobrecarga(valor_forca, forca_primario, constituicao_primario)
    sobrecarga = classificar_sobrecarga(sb_total, cs, movimento_base_m)

    avisos: list[str] = []
    if saldo_pc < 0:
        avisos.append(
            f"O custo total dos equipamentos ({custo_total_pc / 100:.2f} po) excede o ouro inicial "
            f"({ouro_info['inicial_po']:.2f} po) em {abs(saldo_pc) / 100:.2f} po."
        )

    return {
        "ouro_inicial": ouro_info,
        "custo_total_pc": custo_total_pc,
        "custo_total_po": round(custo_total_pc / 100.0, 2),
        "moedas_restantes": moedas_restantes,
        "armadura": armadura,
        "escudo": escudo,
        "elmo": elmo,
        "armas": armas,
        "itens": outros_itens,
        "todos_itens_resumo": [
            {"id": x["id"], "nome": x["nome"], "categoria": x["categoria"], "sb": x.get("sb", 0), "custo": x.get("custo", "")}
            for x in todos_itens
        ],
        "sobrecarga": sobrecarga,
        "avisos": avisos,
    }
