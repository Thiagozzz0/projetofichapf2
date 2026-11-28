"""Exportador de ficha de Castles & Crusades em texto plano (.txt UTF-8)."""

from __future__ import annotations

from typing import Any

from motor_cc.atributos import ORDEM_ATRIBUTOS
from motor_cc.exportacao.comum import fmt_mod, fmt_movimento


def exportar_ficha_cc_txt(ficha: dict[str, Any]) -> str:
    """Formata uma ficha gerada pelo motor_cc em texto estruturado UTF-8."""
    cab = ficha["cabecalho"]
    attr_bloco = ficha["atributos"]
    attrs = attr_bloco["atributos"]
    comb = ficha["combate"]
    ca = comb["ca"]
    pv = comb["pv"]
    habs = ficha["habilidades"]
    eq = ficha["equipamentos"]
    magias = ficha["magias"]
    notas = ficha.get("notas", {})
    avisos = ficha.get("avisos", [])

    linhas: list[str] = []
    sep = "=" * 72
    subsep = "-" * 72

    linhas.append(sep)
    linhas.append("CASTLES & CRUSADES (1ª Edição Brasileira) — FICHA DE PERSONAGEM")
    linhas.append(sep)
    linhas.append(f"Método de Atributos: {cab['rotulo_metodo']}")
    linhas.append(f"Nome: {cab['nome']} | Títulos: {cab.get('titulos') or '—'}")
    if cab.get("jogador"):
        linhas.append(f"Jogador: {cab['jogador']}")
    raca_txt = cab["raca_nome"]
    if cab.get("linhagem_meio_elfo"):
        raca_txt += f" (Linhagem {cab['linhagem_meio_elfo'].capitalize()})"
    linhas.append(
        f"Raça: {raca_txt} | Classe: {cab['classe_nome']} | Nível: {cab['nivel']} | Disposição: {cab['disposicao_nome']}"
    )
    prox = cab["prox_exp"] if cab.get("prox_exp") is not None else "Máx."
    linhas.append(
        f"Idiomas: {', '.join(cab.get('idiomas', [])) or 'Comum'} | Movimento: {fmt_movimento(cab['movimento_m'])} | Exp: {cab['exp']} / Próx: {prox}"
    )

    linhas.append("")
    linhas.append("[ ATRIBUTOS & SISTEMA SIEGE ]")
    linhas.append(subsep)
    for key in ORDEM_ATRIBUTOS:
        a = attrs[key]
        tag = "[P]" if a["primario"] else "[S]"
        cb = a["classe_base_siege"]
        extra = f" | Bônus Meio-Elfo: +{a['bonus_extra_teste']}" if a.get("bonus_extra_teste") else ""
        jps = ", ".join(a.get("jogadas_protecao", []))
        linhas.append(
            f"  {a['sigla']:<3} {tag}  Valor: {a['valor']:>2}  Mod: {fmt_mod(a['modificador']):>3}  "
            f"(CB {cb}{extra})  —  JP: {jps}"
        )

    linhas.append("")
    linhas.append("[ COMBATE ]")
    linhas.append(subsep)
    linhas.append(
        f"CA: {ca['total']}  (= 10 + Armadura {ca['armadura']} + Escudo {ca['escudo']} + "
        f"DES {fmt_mod(ca['mod_destreza'])} + Magia {ca['magia']} + Var {ca['var']})"
    )
    linhas.append(
        f"Proteções: Armadura: {ca['armadura_nome']} | Escudo: {ca['escudo_nome']} | Elmo: {ca['elmo_nome']}"
    )
    pv_lista = ", ".join(f"{p['nivel']}º:{p['pv']}" for p in pv.get("por_nivel", []))
    linhas.append(f"PV Total: {pv['total']} ({pv['dado_vida']}) | BpA: {fmt_mod(comb['bpa'])}")
    linhas.append(f"PV por Nível: {pv_lista}")
    if comb.get("ferimentos_e_condicoes"):
        linhas.append(f"Ferimentos e Condições: {comb['ferimentos_e_condicoes']}")

    if comb.get("ataques"):
        linhas.append("Armas:")
        for atq in comb["ataques"]:
            linhas.append(
                f"  - {atq['nome']} | Ataque: {fmt_mod(atq['total_ataque'])} "
                f"(BpA {atq['bpa']} + Mod {fmt_mod(atq['mod_ataque'])}) | Dano: {atq['total_dano']} | Alcance: {atq['alcance']}"
            )
    else:
        linhas.append("Armas: Nenhuma arma equipada.")

    linhas.append("")
    linhas.append("[ HABILIDADES DA RAÇA ]")
    linhas.append(subsep)
    for h in habs.get("raca", []):
        linhas.append(f"  * {h['nome']}: {h['descricao']}")

    linhas.append("")
    linhas.append("[ HABILIDADES DA CLASSE ]")
    linhas.append(subsep)
    for h in habs.get("classe", []):
        teste_str = f" [Teste: {h['teste'].upper()}]" if h.get("teste") else ""
        linhas.append(f"  * Nv.{h['nivel']} {h['nome']}{teste_str}: {h['resumo']}")

    linhas.append("")
    linhas.append("[ EQUIPAMENTOS, SOBRECARGA E MOEDAS ]")
    linhas.append(subsep)
    sc = eq["sobrecarga"]
    linhas.append(
        f"Sobrecarga: SB {sc['sb_total']} / CS {sc['categoria_sobrecarga_cs']} -> {sc['categoria_nome']} ({sc['efeito']})"
    )
    moedas = eq["moedas_restantes"]
    linhas.append(f"Moedas: Ouro: {moedas['ouro']} po | Prata: {moedas['prata']} pp | Cobre: {moedas['cobre']} pc")
    if eq.get("todos_itens_resumo"):
        for it in eq["todos_itens_resumo"]:
            linhas.append(f"  - {it['nome']} (SB {it['sb']}, {it['custo']})")
    else:
        linhas.append("  - Nenhum item comprado.")

    if notas.get("itens_magicos"):
        linhas.append("Itens Mágicos: " + ", ".join(str(x) for x in notas["itens_magicos"]))
    if notas.get("pocoes"):
        linhas.append("Poções: " + ", ".join(str(x) for x in notas["pocoes"]))
    if notas.get("anotacoes"):
        linhas.append("Anotações: " + notas["anotacoes"])

    if magias.get("conjurador"):
        linhas.append("")
        linhas.append("[ MAGIAS E FEITIÇOS ]")
        linhas.append(subsep)
        linhas.append(
            f"Tradição: {str(magias['tradicao']).capitalize()} | Atributo: {str(magias['atributo_conjuracao']).upper()} "
            f"({magias.get('valor_atributo_conjuracao')})"
        )
        espacos = magias.get("espacos_por_circulo", {})
        lista_feit = magias.get("feiticos_por_circulo", {})
        for circ in sorted(espacos.keys(), key=int):
            info = espacos[circ]
            bonus_txt = f" (+{info['bonus_atributo']} bônus)" if info["bonus_atributo"] else ""
            linhas.append(f"  Nível {circ} [{info['total']} espaços/dia{bonus_txt}]:")
            feitos = lista_feit.get(circ, [])
            if feitos:
                for f in feitos:
                    rev = "*" if f.get("reversivel") else ""
                    linhas.append(f"    - {f['nome']}{rev}: {f.get('resumo', '')}")
            else:
                linhas.append("    - (Nenhum feitiço selecionado)")

    if avisos:
        linhas.append("")
        linhas.append("[ AVISOS ]")
        linhas.append(subsep)
        for av in avisos:
            linhas.append(f"  ! {av}")

    linhas.append(sep)
    return "\n".join(linhas) + "\n"
