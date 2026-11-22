"""Cálculo de atributos e modificadores pelo sistema ABCD de Pathfinder 2E."""

from __future__ import annotations

import random
from typing import Any

from .util import ATRIBUTOS, NOME_ATRIBUTO, atributo_id, modificador, normalizar


_MODOS_PROCEDURAIS = frozenset({"", "procedural", "auto", "automatico", "automatica", "conceito"})
_MODOS_ALEATORIOS = frozenset({"aleatorio", "aleatoria", "random"})


def normalizar_escolha_atributo(valor: Any) -> str:
    """Converte entrada de melhoria de atributo em 'procedural', 'aleatorio' ou ID canônico."""
    if valor is None:
        return "procedural"
    bruto = str(valor).strip()
    norm = normalizar(bruto)
    if norm in _MODOS_PROCEDURAIS:
        return "procedural"
    if norm in _MODOS_ALEATORIOS:
        return "aleatorio"
    aid = atributo_id(bruto)
    if aid:
        return aid
    raise ValueError(f"Atributo ou modo inválido para melhoria: {valor!r}.")


_normalizar_escolha_atributo = normalizar_escolha_atributo


def _resolver_lista_modos(bruto: Any, quantidade: int) -> list[str]:
    """Normaliza uma lista (ou valor único) de escolhas de melhoria para tamanho fixo."""
    if quantidade <= 0:
        return []
    if bruto is None:
        return ["procedural"] * quantidade
    itens = [bruto] if isinstance(bruto, str) else list(bruto)
    modos = [_normalizar_escolha_atributo(x) for x in itens[:quantidade]]
    while len(modos) < quantidade:
        modos.append("procedural")
    return modos


def _aplicar_slots_livres(
    modos: list[str],
    valores: dict[str, int],
    ja_usados: set[str],
    deltas: dict[str, int],
    prioridade: list[str],
    rng_efetivo: random.Random,
    teto: int | None,
    nome_etapa: str,
    *,
    fixos_bloqueados: set[str] | None = None,
) -> list[str]:
    """Aplica slots livres em duas passadas: manuais primeiro, depois procedurais/aleatórios."""
    escolhidos = [""] * len(modos)

    # 1ª passada: escolhas manuais fixadas pelo jogador
    for idx, modo in enumerate(modos):
        if modo not in ATRIBUTOS:
            continue
        if fixos_bloqueados and modo in fixos_bloqueados:
            raise ValueError(
                f"A melhoria livre de {nome_etapa} não pode ser aplicada em "
                f"{NOME_ATRIBUTO[modo]}, pois este atributo já foi alterado (bônus fixo ou penalidade) nesta etapa."
            )
        if modo in ja_usados:
            raise ValueError(
                f"As melhorias de {nome_etapa} devem ser aplicadas em atributos distintos "
                f"(repetido: {NOME_ATRIBUTO[modo]})."
            )
        delta = _aplicar_melhoria(valores, modo, teto=teto)
        ja_usados.add(modo)
        deltas[modo] = deltas.get(modo, 0) + delta
        escolhidos[idx] = modo

    # 2ª passada: procedurais (prioridade do conceito) e depois aleatórios
    for modo_alvo in ("procedural", "aleatorio"):
        for idx, modo in enumerate(modos):
            if modo != modo_alvo or escolhidos[idx]:
                continue
            if modo_alvo == "procedural":
                candidatos = [
                    a for a in prioridade if a not in ja_usados and (teto is None or valores[a] < teto)
                ]
                escolhido = _melhor_por_prioridade(candidatos or prioridade, prioridade, excluir=ja_usados)
            else:
                candidatos = [
                    a for a in ATRIBUTOS if a not in ja_usados and (teto is None or valores[a] < teto)
                ]
                if not candidatos:
                    candidatos = [a for a in ATRIBUTOS if a not in ja_usados]
                escolhido = rng_efetivo.choice(candidatos)

            delta = _aplicar_melhoria(valores, escolhido, teto=teto)
            ja_usados.add(escolhido)
            deltas[escolhido] = deltas.get(escolhido, 0) + delta
            escolhidos[idx] = escolhido

    return escolhidos


def _aplicar_melhoria(valores: dict[str, int], attr: str, teto: int | None = None) -> int:
    """Aplica uma melhoria de atributo (+2 se < 18, +1 se >= 18). Retorna o delta aplicado."""
    atual = valores[attr]
    incremento = 2 if atual < 18 else 1
    novo = atual + incremento
    if teto is not None:
        novo = min(teto, novo)
    delta = novo - atual
    valores[attr] = novo
    return delta


def opcoes_atributo_classe(classe: dict[str, Any], subclasse: dict[str, Any] | None) -> list[str]:
    """Resolve os IDs de atributos-chave válidos para a classe e subclasse."""
    opcoes_brutas = list(classe["atributo_chave"]["opcoes"])
    ids_validos: list[str] = []

    for opcao in opcoes_brutas:
        if opcao == "outro_conforme_esquema":
            alt = subclasse.get("atributo_chave_alternativo") if subclasse else None
            alt_id = atributo_id(alt)
            if alt_id and alt_id not in ids_validos:
                ids_validos.append(alt_id)
        else:
            aid = atributo_id(opcao)
            if aid and aid not in ids_validos:
                ids_validos.append(aid)

    return ids_validos


_opcoes_atributo_classe = opcoes_atributo_classe


def _melhor_por_prioridade(
    candidatos: list[str],
    prioridade: list[str],
    excluir: set[str] | None = None,
) -> str:
    """Retorna o candidato que aparece primeiro na lista de prioridade do conceito."""
    bloqueados = excluir or set()
    permitidos = [c for c in candidatos if c not in bloqueados]
    if not permitidos:
        permitidos = list(candidatos)
    indice = {attr: pos for pos, attr in enumerate(prioridade)}
    return min(permitidos, key=lambda attr: indice.get(attr, 99))


def calcular_atributos(
    ancestralidade: dict[str, Any],
    biografia: dict[str, Any],
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    conceito: dict[str, Any],
    nivel: int = 1,
    *,
    escolhas_atributos: dict[str, Any] | None = None,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Executa o fluxo ABCD do 1º nível guiado pelo conceito ou escolhas do jogador.

    Permite escolher manualmente, deixar no modo procedural (recomendado pelo conceito)
    ou sortear aleatoriamente as melhorias livres da Ancestralidade, da Biografia e as
    4 melhorias livres de 1º nível. Estrutura preparada para melhorias a cada 5 níveis.
    """
    escolhas = escolhas_atributos or {}
    rng_efetivo = rng or random.Random()
    prioridade = list(conceito["prioridade_atributos"])
    teto_n1 = 18 if nivel == 1 else None
    valores: dict[str, int] = {attr: 10 for attr in ATRIBUTOS}
    historico_abcd: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Etapa A — Ancestralidade (melhorias fixas, defeito, melhorias livres)
    # ------------------------------------------------------------------
    melhorados_a: set[str] = set()
    deltas_a: dict[str, int] = {}
    livres_a = 0

    for item in ancestralidade["melhorias_atributo"]:
        aid = atributo_id(item)
        if aid is None:
            livres_a += 1
        else:
            delta = _aplicar_melhoria(valores, aid, teto=teto_n1)
            melhorados_a.add(aid)
            deltas_a[aid] = deltas_a.get(aid, 0) + delta

    fixos_a = set(melhorados_a)

    defeito_nome = ancestralidade.get("defeito_atributo")
    defeito_id = atributo_id(defeito_nome) if defeito_nome else None
    if defeito_id:
        valores[defeito_id] -= 2
        deltas_a[defeito_id] = deltas_a.get(defeito_id, 0) - 2
        # Cada atributo só pode ser alterado 1x na Etapa A (melhorias fixas e penalidade travam o livre da raça)
        melhorados_a.add(defeito_id)
        fixos_a.add(defeito_id)

    modos_a = _resolver_lista_modos(escolhas.get("ancestralidade_livres"), livres_a)
    escolhidos_a_livres = _aplicar_slots_livres(
        modos_a,
        valores,
        melhorados_a,
        deltas_a,
        prioridade,
        rng_efetivo,
        teto_n1,
        f"Ancestralidade ({ancestralidade['nome']})",
        fixos_bloqueados=fixos_a,
    )

    historico_abcd.append(
        {
            "etapa": "A",
            "origem": f"Ancestralidade: {ancestralidade['nome']}",
            "deltas": deltas_a,
        }
    )

    # ------------------------------------------------------------------
    # Etapa B — Biografia (1 opção restrita + 1 melhoria livre)
    # ------------------------------------------------------------------
    melhorados_b: set[str] = set()
    deltas_b: dict[str, int] = {}

    opcoes_bio = [
        aid
        for opt in biografia["melhorias_atributo_opcoes"]
        if (aid := atributo_id(opt)) is not None
    ]
    modo_b_restrito = _normalizar_escolha_atributo(escolhas.get("biografia_restrito"))
    modo_b_livre = _normalizar_escolha_atributo(escolhas.get("biografia_livre"))

    if modo_b_restrito in ATRIBUTOS:
        if modo_b_restrito not in opcoes_bio:
            nomes_op = ", ".join(NOME_ATRIBUTO[o] for o in opcoes_bio)
            raise ValueError(
                f"A biografia '{biografia['nome']}' permite no bônus restrito apenas: {nomes_op}."
            )
        if biografia.get("melhoria_livre", True) and modo_b_livre == modo_b_restrito:
            raise ValueError(
                f"O bônus livre da biografia não pode ser aplicado no mesmo atributo do bônus restrito "
                f"({NOME_ATRIBUTO[modo_b_restrito]})."
            )
        escolhido_b_restrito = modo_b_restrito
    elif modo_b_restrito == "aleatorio":
        candidatos_res = [o for o in opcoes_bio if o != modo_b_livre] or list(opcoes_bio)
        escolhido_b_restrito = rng_efetivo.choice(candidatos_res)
    else:
        candidatos_res = [o for o in opcoes_bio if o != modo_b_livre] or list(opcoes_bio)
        escolhido_b_restrito = _melhor_por_prioridade(candidatos_res, prioridade)

    deltas_b[escolhido_b_restrito] = _aplicar_melhoria(valores, escolhido_b_restrito, teto=teto_n1)
    melhorados_b.add(escolhido_b_restrito)

    escolhido_b_livre: str | None = None
    if biografia.get("melhoria_livre", True):
        escolhido_b_livre = _aplicar_slots_livres(
            [modo_b_livre],
            valores,
            melhorados_b,
            deltas_b,
            prioridade,
            rng_efetivo,
            teto_n1,
            f"Biografia ({biografia['nome']})",
        )[0]

    historico_abcd.append(
        {
            "etapa": "B",
            "origem": f"Biografia: {biografia['nome']}",
            "deltas": deltas_b,
        }
    )

    # ------------------------------------------------------------------
    # Etapa C — Classe (atributo-chave: manual, aleatório ou procedural)
    # ------------------------------------------------------------------
    opcoes_classe = opcoes_atributo_classe(classe, subclasse)
    modo_classe = normalizar_escolha_atributo(escolhas.get("classe_chave"))
    if modo_classe in ATRIBUTOS:
        if modo_classe not in opcoes_classe:
            nomes_op = ", ".join(NOME_ATRIBUTO[o] for o in opcoes_classe)
            raise ValueError(
                f"Atributo-chave inválido para {classe['nome']}: '{NOME_ATRIBUTO[modo_classe]}'. "
                f"Opções válidas: {nomes_op}."
            )
        attr_chave = modo_classe
    elif modo_classe == "aleatorio":
        attr_chave = rng_efetivo.choice(opcoes_classe)
    else:
        attr_chave = _melhor_por_prioridade(opcoes_classe, prioridade)
    delta_c = _aplicar_melhoria(valores, attr_chave, teto=teto_n1)

    historico_abcd.append(
        {
            "etapa": "C",
            "origem": f"Classe: {classe['nome']} (Atributo-Chave: {NOME_ATRIBUTO[attr_chave]})",
            "deltas": {attr_chave: delta_c},
        }
    )

    # ------------------------------------------------------------------
    # Etapa D — 4 Melhorias Livres de 1º nível (em 4 atributos distintos)
    # ------------------------------------------------------------------
    melhorados_d: set[str] = set()
    deltas_d: dict[str, int] = {}
    modos_d = _resolver_lista_modos(escolhas.get("livres_nivel_1"), 4)
    escolhidos_d = _aplicar_slots_livres(
        modos_d,
        valores,
        melhorados_d,
        deltas_d,
        prioridade,
        rng_efetivo,
        teto_n1,
        "4 Melhorias Livres (1º Nível)",
    )

    historico_abcd.append(
        {
            "etapa": "D",
            "origem": "4 Melhorias Livres (1º Nível)",
            "deltas": deltas_d,
        }
    )

    modificadores = {attr: modificador(val) for attr, val in valores.items()}
    return {
        "valores": valores,
        "modificadores": modificadores,
        "atributo_chave": attr_chave,
        "historico_abcd": historico_abcd,
        "escolhas_aplicadas": {
            "ancestralidade_livres": escolhidos_a_livres,
            "biografia_restrito": escolhido_b_restrito,
            "biografia_livre": escolhido_b_livre,
            "classe_chave": attr_chave,
            "livres_nivel_1": escolhidos_d,
        },
    }
