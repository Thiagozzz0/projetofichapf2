"""Regras de conjuração, espaços diários, feitiços bônus por atributo e listas de magias de C&C."""

from __future__ import annotations

from typing import Any

from motor_cc.dados import carregar_listas_magias, mapa_magias


def calcular_conjuracao(
    classe: dict[str, Any],
    nivel: int,
    atributos_detalhes: dict[str, dict[str, Any]],
    feiticos_escolhidos: dict[str, list[str]] | None = None,
    auto_completar: bool = False,
) -> dict[str, Any]:
    """Calcula espaços diários (incluindo feitiços bônus por INT/SAB) e resolve os feitiços escolhidos."""
    if not classe.get("conjurador"):
        return {
            "conjurador": False,
            "tradicao": None,
            "atributo_conjuracao": None,
            "espacos_por_circulo": {},
            "feiticos_por_circulo": {},
        }

    conj = classe.get("conjuracao", {})
    tradicao = conj.get("tradicao")
    attr_conj = conj.get("atributo_conjuracao", classe["atributo_principal"])
    valor_attr = int(atributos_detalhes[attr_conj]["valor"])

    # Tabela de espaços base por nível da classe
    tabela_diarios: dict[str, dict[str, int]] = conj.get("feiticos_diarios", {})
    chave_nv = str(nivel)
    if chave_nv not in tabela_diarios and tabela_diarios:
        # Usa o maior nível <= nivel presente na tabela (para níveis 13-24 caso a tabela pare em 12 ou 20)
        niveis_disp = sorted(int(k) for k in tabela_diarios.keys() if int(k) <= nivel)
        chave_nv = str(niveis_disp[-1]) if niveis_disp else str(min(int(k) for k in tabela_diarios.keys()))

    espacos_base: dict[str, int] = {
        str(circ): int(qtd) for circ, qtd in tabela_diarios.get(chave_nv, {}).items() if int(qtd) > 0
    }

    # Feitiços bônus cumulativos por atributo (13-15: +1 de 1º; 16-17: +1 de 2º; 18-19: +1 de 3º)
    regras_bonus = conj.get("feiticos_bonus_por_atributo", [])
    cumulativo = bool(conj.get("feiticos_bonus_cumulativos", True))
    requer_acesso = bool(conj.get("feiticos_bonus_requer_acesso_circulo", True))

    bonus_por_circulo: dict[str, int] = {}
    for regra in regras_bonus:
        min_v = int(regra["min"])
        max_v = int(regra["max"])
        circ_str = str(regra["circulo"])
        qtd_b = int(regra["quantidade"])

        elegivel = (valor_attr >= min_v) if cumulativo else (min_v <= valor_attr <= max_v)
        if not elegivel:
            continue
        if requer_acesso and espacos_base.get(circ_str, 0) <= 0:
            continue
        bonus_por_circulo[circ_str] = bonus_por_circulo.get(circ_str, 0) + qtd_b

    espacos_totais: dict[str, dict[str, int]] = {}
    for circ in sorted(espacos_base.keys(), key=int):
        base_q = espacos_base[circ]
        bonus_q = bonus_por_circulo.get(circ, 0)
        espacos_totais[circ] = {
            "base": base_q,
            "bonus_atributo": bonus_q,
            "total": base_q + bonus_q,
        }

    # Resolver feitiços escolhidos na lista da classe
    listas = carregar_listas_magias()
    lista_classe = listas.get(classe["id"], {})
    descricoes_mapa = mapa_magias()

    escolhidos_in = feiticos_escolhidos or {}
    feiticos_resolvidos: dict[str, list[dict[str, Any]]] = {}
    avisos: list[str] = []

    for circ, info_esp in espacos_totais.items():
        disponiveis = lista_classe.get(circ, [])
        por_id = {f["id"]: f for f in disponiveis}
        ids_sel = list(escolhidos_in.get(circ, []))

        if auto_completar and not ids_sel:
            ids_sel = [f["id"] for f in disponiveis[: info_esp["total"]]]

        resolvidos_circ: list[dict[str, Any]] = []
        for fid in ids_sel:
            ent = por_id.get(fid)
            if not ent:
                avisos.append(f"Feitiço {fid!r} não encontrado na lista de {classe['nome']} (círculo {circ}).")
                continue
            desc_obj = descricoes_mapa.get(fid)
            resolvidos_circ.append(
                {
                    "id": ent["id"],
                    "nome": ent["nome"],
                    "reversivel": ent.get("reversivel", False),
                    "resumo": ent.get("resumo", ""),
                    "pagina_livro": ent.get("pagina_livro"),
                    "componentes": desc_obj.get("componentes", "") if desc_obj else "",
                }
            )

        if len(resolvidos_circ) > info_esp["total"]:
            avisos.append(
                f"Círculo {circ}: selecionados {len(resolvidos_circ)} feitiços, mas o limite diário é {info_esp['total']}."
            )

        feiticos_resolvidos[circ] = resolvidos_circ

    return {
        "conjurador": True,
        "tradicao": tradicao,
        "atributo_conjuracao": attr_conj,
        "valor_atributo_conjuracao": valor_attr,
        "preparacao": conj.get("preparacao"),
        "espacos_por_circulo": espacos_totais,
        "feiticos_por_circulo": feiticos_resolvidos,
        "avisos": avisos,
    }
