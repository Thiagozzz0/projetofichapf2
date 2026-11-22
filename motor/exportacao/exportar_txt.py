"""Exportador da ficha de personagem PF2E em texto plano UTF-8 (`.txt`)."""

from __future__ import annotations

from typing import Any

from ..util import formatar_bonus, formatar_metros
from .comum import (
    _NOME_ATRIBUTO_SIGLA,
    _coletar_talentos_preenchidos,
    _formatar_custo_acao,
    _formatar_grau_curto,
    _formatar_item_inventario,
    _formatar_linha_golpe,
    _tem_conjuracao,
    _tradicao_e_estilo_texto,
)


def exportar_ficha_txt(resultado: dict[str, Any]) -> str:
    """Exporta a ficha completa formatada em texto plano UTF-8 (4 páginas oficiais)."""
    meta = resultado.get("meta_geracao", {})
    ficha = resultado["ficha"]
    cab = ficha["cabecalho"]
    linhas: list[str] = []

    def sec(titulo: str) -> None:
        linhas.append("")
        linhas.append("=" * 78)
        linhas.append(titulo)
        linhas.append("=" * 78)

    def sub(titulo: str) -> None:
        linhas.append("")
        linhas.append(f"--- {titulo} ---")

    linhas.append("==============================================================================")
    linhas.append("PATHFINDER 2ª EDIÇÃO — FICHA DE PERSONAGEM (GERAÇÃO PROCEDURAL)")
    linhas.append("==============================================================================")
    linhas.append(f"Personagem : {cab['nome_personagem']} (Nível {cab['nivel']})")
    if cab.get("nome_jogador"):
        linhas.append(f"Jogador    : {cab['nome_jogador']}")
    linhas.append(f"Ancest/Her.: {cab['ancestralidade_e_heranca']}")
    bio_modo = "Procedural" if meta.get("biografia_procedural", True) else "Manual"
    linhas.append(f"Biografia  : {cab['biografia']} ({bio_modo})")
    linhas.append(f"Classe     : {cab['classe']}")
    if meta.get("subclasse_oficial_nome"):
        tese_txt = f" | Tese Arcana: {meta['tese_arcana_nome']}" if meta.get("tese_arcana_nome") else ""
        linhas.append(f"Subclasse  : {meta['subclasse_oficial_nome']}{tese_txt}")
    linhas.append(
        f"Tamanho    : {cab['tamanho']} | Tendência: {cab['tendencia']} | "
        f"Pontos de Heroísmo: {cab['pontos_heroismo']}"
    )
    if cab.get("divindade"):
        linhas.append(f"Divindade  : {cab['divindade']}")
    linhas.append(f"Traços     : {', '.join(cab.get('tracos') or [])}")
    if meta.get("seed") is not None:
        linhas.append(
            f"Seed       : {meta['seed']} | Orçamento: {meta.get('orcamento_inicial', '15 po')} | "
            f"Gasto: {meta.get('gasto_equipamentos', '—')} | Saldo: {meta.get('saldo_restante', '—')}"
        )

    # PÁGINA 1
    sec("PÁGINA 1 (p. 580) — ESTATÍSTICAS PRINCIPAIS, COMBATE E PERÍCIAS")

    sub("ATRIBUTOS")
    for aid, (sigla, nome_atr) in _NOME_ATRIBUTO_SIGLA.items():
        atr = ficha["atributos"][aid]
        linhas.append(f"  {sigla} ({nome_atr:<12}): {atr['valor']:>2}  ({formatar_bonus(atr['modificador'])})")
    if meta.get("historico_abcd"):
        linhas.append("  Histórico ABCD:")
        for step in meta["historico_abcd"]:
            deltas = ", ".join(
                f"{k.upper()} {formatar_bonus(v)}" for k, v in step["deltas"].items()
            )
            linhas.append(f"    [{step['etapa']}] {step['origem']}: {deltas}")

    sub("COMBATE, DEFESAS E SALVAMENTOS")
    pv = ficha["pontos_vida"]
    ca = ficha["classe_armadura"]
    vel = ficha["velocidade"]
    perc = ficha["percepcao"]
    cd = ficha["cd_classe"]
    salv = ficha["jogadas_salvamento"]
    obs_comb = meta.get("observacoes_combate") or {}
    morr_lim = meta.get("limite_morrendo") or obs_comb.get("limite_morrendo")
    cd_rec = meta.get("cd_recuperacao_base") or obs_comb.get("cd_recuperacao_base")
    morr_txt = f" | Morrendo Máx: {morr_lim} (CD Recup. {cd_rec}+)" if morr_lim and morr_lim != 4 else ""
    linhas.append(f"  Pontos de Vida : {pv['max']} (Atuais: {pv['atuais']}){morr_txt}")
    if pv.get("resistencias_e_imunidades"):
        linhas.append(f"  Resistências   : {pv['resistencias_e_imunidades']}")
    ca_esc_txt = f" | {obs_comb['ca_com_escudo']} c/ Escudo Erguido" if obs_comb.get("ca_com_escudo") else ""
    linhas.append(
        f"  Classe Armad.  : {ca['total']}{ca_esc_txt} "
        f"(10 + DES/Lim {formatar_bonus(ca['des_ou_limite'])} + Prof {formatar_bonus(ca['proficiencia'])} "
        f"[{_formatar_grau_curto(ca['grau_proficiencia'])}] + Item {formatar_bonus(ca['item'])})"
    )
    linhas.append(f"  Armadura       : {meta.get('armadura_equipada_resumo') or meta.get('armadura_equipada', 'Nenhuma armadura')}")
    if obs_comb.get("nota_postura"):
        linhas.append(f"  Postura        : {obs_comb['nota_postura']}")
    esc = ca["escudo"]
    if esc.get("nome"):
        linhas.append(
            f"  Escudo         : {esc['nome']} (+{esc['bonus_ca']} CA ao Erguer | "
            f"Dureza {esc['dureza']} | PV {esc['pv_max']} | LQ {esc['limiar_quebra']})"
        )
    vel_obs = f" ({vel['tipos_movimento_anotacoes']})" if vel.get("tipos_movimento_anotacoes") else ""
    linhas.append(f"  Velocidade     : {formatar_metros(vel['metros'])} metros{vel_obs}")
    linhas.append(
        f"  CD de Classe   : {cd['total']} [{_formatar_grau_curto(cd['grau_proficiencia'])}] | "
        f"Percepção: {formatar_bonus(perc['total'])} [{_formatar_grau_curto(perc['grau_proficiencia'])}]"
    )
    if perc.get("sentidos"):
        linhas.append(f"  Sentidos       : {', '.join(perc['sentidos'])}")
    linhas.append(
        "  Salvamentos    : "
        f"Fortitude {formatar_bonus(salv['fortitude']['total'])} [{_formatar_grau_curto(salv['fortitude']['grau_proficiencia'])}] | "
        f"Reflexos {formatar_bonus(salv['reflexos']['total'])} [{_formatar_grau_curto(salv['reflexos']['grau_proficiencia'])}] | "
        f"Vontade {formatar_bonus(salv['vontade']['total'])} [{_formatar_grau_curto(salv['vontade']['grau_proficiencia'])}]"
    )
    if salv.get("anotacoes"):
        linhas.append(f"  Anot. Salvam.  : {salv['anotacoes']}")

    sub("GOLPES (ATAQUES)")
    for grupo_nome, lista_g in (
        ("Corpo a Corpo", ficha["golpes_corpo_a_corpo"]),
        ("À Distância", ficha["golpes_a_distancia"]),
    ):
        preenchidos = [g for g in lista_g if g.get("arma")]
        if preenchidos:
            linhas.append(f"  {grupo_nome}:")
            for g in preenchidos:
                arma, atk, dano_str, tracos = _formatar_linha_golpe(g)
                linhas.append(f"    - {arma:<24} | Ataque {atk:<4} | Dano {dano_str:<12} | Traços: {tracos}")

    sub("PROFICIÊNCIAS COM ARMAS E ARMADURAS")
    arm_prof = " | ".join(
        f"{p['rotulo']}: {_formatar_grau_curto(p['grau_proficiencia'])}"
        for p in ficha["proficiencia_armas"]
    )
    def_prof = " | ".join(
        f"{k.replace('_', ' ').title()}: {_formatar_grau_curto(v)}"
        for k, v in ca["proficiencias_armadura"].items()
    )
    linhas.append(f"  Armas     : {arm_prof}")
    linhas.append(f"  Armaduras : {def_prof}")

    sub("PERÍCIAS (18 LINHAS OFICIAIS) E IDIOMAS")
    for per in ficha["pericias"]:
        nome_exib = per["rotulo_oficial"]
        if per.get("especializacao"):
            nome_exib = f"{nome_exib} ({per['especializacao']})"
        elif per["id"] in ("saber_1", "saber_2"):
            nome_exib = f"{nome_exib} (—)"
        sigla_g = _formatar_grau_curto(per["grau_proficiencia"])
        pen_txt = f" [Arm {per['penalidade_armadura']}]" if per.get("penalidade_armadura") else ""
        linhas.append(
            f"  {nome_exib:<34} {formatar_bonus(per['total']):>3}  "
            f"[{sigla_g}] ({per['atributo_chave'].upper()} {formatar_bonus(per['mod_atributo'])}{pen_txt})"
        )
    linhas.append(f"  Idiomas: {', '.join(ficha.get('idiomas') or [])}")

    # PÁGINA 2
    sec("PÁGINA 2 (p. 581) — HABILIDADES, TALENTOS E INVENTÁRIO")

    sub("HABILIDADES E TALENTOS")
    for cat, rot, nome, origem in _coletar_talentos_preenchidos(ficha):
        linhas.append(f"  [{cat} • {rot}] {nome} — {origem}")

    sub("INVENTÁRIO, VOLUME E MOEDAS")
    inv = ficha["inventario"]
    for titulo_sec, chave in (
        ("Itens Vestidos", "itens_vestidos"),
        ("Itens Preparados", "itens_preparados"),
        ("Outros Itens", "outros_itens"),
    ):
        itens = inv[chave]
        linhas.append(f"  {titulo_sec}:")
        if itens:
            for item in itens:
                linhas.append(f"    - {_formatar_item_inventario(item)} (Vol: {item['volume']})")
        else:
            linhas.append("    - (vazio)")
    riq = inv["riqueza"]
    linhas.append(
        f"  Volume Total: {inv['volume_total']} "
        f"(Sobrecarregado > {inv['volume_sobrecarregado']} / Máximo {inv['volume_maximo']})"
    )
    linhas.append(f"  Moedas      : {riq['po']} po, {riq['pp']} pp, {riq['pc']} pc ({riq['pl']} pl)")

    # PÁGINA 3
    sec("PÁGINA 3 (p. 582) — PERFIL, CAMPANHA E AÇÕES")
    perfil = ficha["perfil_e_campanha"]
    linhas.append(f"  Idade Base  : {perfil['dados_biograficos'].get('idade') or '—'}")
    if perfil["anotacoes_campanha"].get("anotacoes"):
        linhas.append(f"  Anotações   : {perfil['anotacoes_campanha']['anotacoes']}")

    div_det = meta.get("divindade_detalhes")
    if div_det:
        sub(f"DIVINDADE — {div_det['nome']} ({div_det['tendencia']})")
        linhas.append(
            f"  Arma Favorecida: {div_det['arma_favorecida_nome']} | "
            f"Domínios: {', '.join(div_det['dominios'])}"
        )
        linhas.append(f"  Éditos         : {div_det['editos']}")
        linhas.append(f"  Anátema        : {div_det['anatema']}")

    comp = meta.get("companheiro_ou_familiar")
    if comp:
        sub(f"{comp['categoria'].upper()} — {comp['nome']}")
        if comp["categoria"] == "Companheiro Animal":
            linhas.append(
                f"  Estágio: {comp['estagio']} ({comp['tamanho']}) | PV {comp['pv_max']} | CA {comp['ca']} | "
                f"Vel: {comp['velocidades']}"
            )
            linhas.append(
                f"  Percepção {formatar_bonus(comp['percepcao'])} | "
                f"Fort {formatar_bonus(comp['fortitude'])}, Ref {formatar_bonus(comp['reflexos'])}, Von {formatar_bonus(comp['vontade'])}"
            )
            atks = "; ".join(
                f"{a['nome']} {formatar_bonus(a['ataque_total'])} ({a['dano']})" for a in comp["ataques"]
            )
            linhas.append(f"  Ataques        : {atks}")
            linhas.append(f"  Suporte        : {comp['beneficio_de_suporte']}")
        else:
            linhas.append(
                f"  Tamanho: {comp['tamanho']} | PV {comp['pv_max']} | CA {comp['ca']} | Vel: {comp['velocidade']}"
            )
            linhas.append(
                f"  Percepção/Acrob./Furt.: {formatar_bonus(comp['percepcao'])} | "
                f"Habilidades ({comp['habilidades_diarias_max']}): "
                + ", ".join(h["nome"] for h in comp["habilidades_selecionadas"])
            )

    acoes_at = [a for a in ficha["acoes_e_atividades"] if a.get("nome")]
    if acoes_at:
        sub("AÇÕES E ATIVIDADES")
        for a in acoes_at:
            tr = ", ".join(a.get("tracos") or [])
            linhas.append(f"  - [{_formatar_custo_acao(a.get('acoes', '1'))}] {a['nome']} ({tr})")
            if a.get("descricao"):
                linhas.append(f"    {a['descricao']}")

    acoes_reat = [a for a in ficha["acoes_livres_e_reacoes"] if a.get("nome")]
    if acoes_reat:
        sub("AÇÕES LIVRES E REAÇÕES")
        for a in acoes_reat:
            linhas.append(f"  - [{a.get('tipo', 'REAÇÃO')}] {a['nome']}")
            if a.get("acionamento"):
                linhas.append(f"    Acionamento: {a['acionamento']}")
            if a.get("descricao"):
                linhas.append(f"    {a['descricao']}")

    # PÁGINA 4
    conj = ficha["conjuracao"]
    if _tem_conjuracao(conj):
        sec("PÁGINA 4 (p. 583) — CONJURAÇÃO E MAGIAS")
        trad_txt, est_txt = _tradicao_e_estilo_texto(conj)
        linhas.append(
            f"  Tradição: {trad_txt} | Estilo: {est_txt} | "
            f"Ataque de Magia: {formatar_bonus(conj['ataque_magia']['total'])} "
            f"[{_formatar_grau_curto(conj['ataque_magia']['grau_proficiencia'])}] | "
            f"CD de Magia: {conj['cd_magia']['total']} "
            f"[{_formatar_grau_curto(conj['cd_magia']['grau_proficiencia'])}]"
        )
        linhas.append(
            f"  Nível de Truque: {conj['nivel_truque']} | "
            f"Espaços de 1º Círculo/Dia: {conj['espacos_magia_por_dia'].get('1', 0)} | "
            f"Pontos de Foco: {conj['magias_foco']['pontos_foco']['maximo']}"
        )
        for titulo_m, lista_m, mostrar_prep in (
            ("Truques Mágicos", conj["truques_magicos"], False),
            ("Magias de Foco", conj["magias_foco"]["slots"], False),
            ("Magias Inatas", conj["magias_inatas"], False),
            ("Magias de 1º Círculo", conj["magias"], True),
        ):
            itens_m = [m for m in lista_m if m.get("nome")]
            if itens_m:
                sub(titulo_m)
                for m in itens_m:
                    comp = ",".join(m.get("componentes") or [])
                    prep = " [Preparada]" if (mostrar_prep and m.get("preparada")) else ""
                    freq = f" ({m['frequencia']})" if m.get("frequencia") else ""
                    linhas.append(
                        f"  - {m['nome']}{prep}{freq} | Ações: {m.get('acoes') or '—'} | "
                        f"Comp: {comp or '—'} | {m.get('anotacoes') or ''}"
                    )

    linhas.append("")
    return "\n".join(linhas)
