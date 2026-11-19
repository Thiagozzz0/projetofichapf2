"""Cálculo de atributos e modificadores pelo sistema ABCD de Pathfinder 2E."""

from __future__ import annotations

from typing import Any

from .util import ATRIBUTOS, NOME_ATRIBUTO, atributo_id, modificador


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


def _opcoes_atributo_classe(classe: dict[str, Any], subclasse: dict[str, Any] | None) -> list[str]:
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
) -> dict[str, Any]:
    """Executa o fluxo ABCD do 1º nível guiado pela prioridade de atributos do conceito.

    Estrutura preparada para futura extensão de melhorias a cada 5 níveis.
    """
    prioridade = list(conceito["prioridade_atributos"])
    teto_n1 = 18 if nivel == 1 else None
    valores: dict[str, int] = {attr: 10 for attr in ATRIBUTOS}
    historico_abcd: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Etapa A — Ancestralidade (melhorias fixas, defeito, melhoria livre)
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

    defeito_nome = ancestralidade.get("defeito_atributo")
    defeito_id = atributo_id(defeito_nome) if defeito_nome else None
    if defeito_id:
        valores[defeito_id] -= 2
        deltas_a[defeito_id] = deltas_a.get(defeito_id, 0) - 2

    for _ in range(livres_a):
        escolhido = _melhor_por_prioridade(prioridade, prioridade, excluir=melhorados_a)
        delta = _aplicar_melhoria(valores, escolhido, teto=teto_n1)
        melhorados_a.add(escolhido)
        deltas_a[escolhido] = deltas_a.get(escolhido, 0) + delta

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
    escolhido_b_restrito = _melhor_por_prioridade(opcoes_bio, prioridade)
    deltas_b[escolhido_b_restrito] = _aplicar_melhoria(valores, escolhido_b_restrito, teto=teto_n1)
    melhorados_b.add(escolhido_b_restrito)

    if biografia.get("melhoria_livre", True):
        candidatos_livres_b = [
            a for a in prioridade if a not in melhorados_b and (teto_n1 is None or valores[a] < teto_n1)
        ]
        escolhido_b_livre = _melhor_por_prioridade(candidatos_livres_b or prioridade, prioridade, excluir=melhorados_b)
        deltas_b[escolhido_b_livre] = _aplicar_melhoria(valores, escolhido_b_livre, teto=teto_n1)
        melhorados_b.add(escolhido_b_livre)

    historico_abcd.append(
        {
            "etapa": "B",
            "origem": f"Biografia: {biografia['nome']}",
            "deltas": deltas_b,
        }
    )

    # ------------------------------------------------------------------
    # Etapa C — Classe (atributo-chave)
    # ------------------------------------------------------------------
    opcoes_classe = _opcoes_atributo_classe(classe, subclasse)
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

    for _ in range(4):
        candidatos_d = [
            a
            for a in prioridade
            if a not in melhorados_d and (teto_n1 is None or valores[a] < teto_n1)
        ]
        if not candidatos_d:
            candidatos_d = [a for a in prioridade if a not in melhorados_d]
        escolhido_d = candidatos_d[0]
        deltas_d[escolhido_d] = _aplicar_melhoria(valores, escolhido_d, teto=teto_n1)
        melhorados_d.add(escolhido_d)

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
    }
