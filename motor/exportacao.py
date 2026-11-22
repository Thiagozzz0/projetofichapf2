"""Exportadores oficiais da ficha de personagem PF2E em `.txt`, `.docx` (OOXML) e `.pdf` (Livro Básico)."""

from __future__ import annotations

import io
from pathlib import Path
import re
import zipfile
from typing import Any
from xml.sax.saxutils import escape

from .util import formatar_bonus, formatar_metros, SIGLA_GRAU, slugify


_NOME_ATRIBUTO_SIGLA = {
    "for": ("FOR", "Força"),
    "des": ("DES", "Destreza"),
    "con": ("CON", "Constituição"),
    "int": ("INT", "Inteligência"),
    "sab": ("SAB", "Sabedoria"),
    "car": ("CAR", "Carisma"),
}

_RE_XML_INVALIDO = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _limpar_xml(texto: Any) -> str:
    """Remove caracteres inválidos em XML 1.0 e escapa entidades XML."""
    bruto = "" if texto is None else str(texto)
    limpo = _RE_XML_INVALIDO.sub("", bruto)
    return escape(limpo)


def nome_arquivo_seguro(
    nome_personagem: str | None,
    classe_texto: str | None,
    nivel: int,
    extensao: str,
) -> str:
    """Gera nome de arquivo ASCII seguro no padrão `ficha_<nome>_<classe>_n<nivel>.<ext>`."""
    nome_slug = slugify(nome_personagem) or "personagem"
    classe_base = (classe_texto or "ficha").split("—")[0].strip()
    classe_slug = slugify(classe_base) or "ficha"
    ext = extensao.lstrip(".").lower()
    return f"ficha_{nome_slug}_{classe_slug}_n{int(nivel)}.{ext}"


def _formatar_grau_curto(grau: str | None) -> str:
    if not grau:
        return "D"
    return SIGLA_GRAU.get(grau, grau[:1].upper())


def _formatar_custo_acao(acoes: Any) -> str:
    ac = str(acoes or "1").strip()
    if ac == "1":
        return "1 ação"
    if ac in ("2", "3", "1 a 2", "1 a 3", "1 ou mais"):
        return f"{ac} ações"
    if ac.lower() in ("livre", "ação livre", "acao livre"):
        return "ação livre"
    if ac.lower() in ("reacao", "reação"):
        return "reação"
    return ac


def _formatar_linha_golpe(golpe: dict[str, Any]) -> tuple[str, str, str, str]:
    arma = golpe.get("arma", "")
    atk = formatar_bonus(int(golpe["ataque"]["total"]))
    dano_info = golpe["dano"]
    mod_dano = dano_info.get("for")
    if mod_dano is None:
        mod_dano = dano_info.get("especial", 0)
    mod_txt = formatar_bonus(int(mod_dano)) if mod_dano else ""
    tipos = "/".join(dano_info.get("tipos_dano") or [])
    dano_str = f"{dano_info.get('dados', '')}{mod_txt} {tipos}".strip()
    tracos = ", ".join(dano_info.get("tracos") or []) or "—"
    return arma, atk, dano_str, tracos


def _formatar_item_inventario(item: dict[str, Any]) -> str:
    """Formata item do inventário evitando duplicar quantidade já embutida no nome."""
    nome = str(item.get("nome") or "")
    qtd_num = item.get("quantidade") or 1
    ja_tem_qtd = "(Qtd:" in nome or f"({qtd_num})" in nome
    qtd = f" ×{qtd_num}" if qtd_num > 1 and not ja_tem_qtd else ""
    return f"{nome}{qtd}"


def _coletar_talentos_preenchidos(ficha: dict[str, Any]) -> list[tuple[str, str, str, str]]:
    """Retorna `(categoria, rotulo_nivel, nome, origem)` apenas dos slots preenchidos."""
    hab = ficha["habilidades_e_talentos"]
    grupos = [
        ("Ancestralidade", hab["ancestralidade"]),
        ("Perícia", hab["pericia"]),
        ("Geral", hab["gerais"]),
        ("Classe", hab["classe"]),
        ("Bônus", hab["bonus"]),
    ]
    linhas: list[tuple[str, str, str, str]] = []
    for cat, slots in grupos:
        for slot in slots:
            nome = (slot.get("nome") or "").strip()
            if nome and nome != "—":
                linhas.append(
                    (
                        cat,
                        slot.get("rotulo_oficial", ""),
                        nome,
                        slot.get("origem_regra", ""),
                    )
                )
    return linhas


def _tem_conjuracao(conjuracao: dict[str, Any]) -> bool:
    return (
        any(conjuracao["tradicoes_marcadas"].values())
        or any(s.get("nome") for s in conjuracao["truques_magicos"])
        or any(s.get("nome") for s in conjuracao["magias"])
        or any(s.get("nome") for s in conjuracao["magias_foco"]["slots"])
        or any(s.get("nome") for s in conjuracao["magias_inatas"])
    )


def _tradicao_e_estilo_texto(conjuracao: dict[str, Any]) -> tuple[str, str]:
    nomes_trad = {
        "arcana": "Arcana",
        "divina": "Divina",
        "ocultista": "Ocultista",
        "primal": "Primal",
    }
    trads = [nomes_trad[k] for k, v in conjuracao["tradicoes_marcadas"].items() if v]
    est = conjuracao["estilo_conjuracao"]
    estilos = []
    if est.get("preparada"):
        estilos.append("Preparada")
    if est.get("espontanea"):
        estilos.append("Espontânea")
    return (", ".join(trads) or "Inata/Foco"), (", ".join(estilos) or "Foco / Inata")


# ==============================================================================
# Exportação TXT (UTF-8 legível e estruturado nas 4 páginas oficiais)
# ==============================================================================

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


# ==============================================================================
# Exportação DOCX (OOXML ECMA-376 completo em Python puro via zipfile)
# ==============================================================================

_CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>
"""

_ROOT_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

_DOC_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""

_STYLES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>
        <w:sz w:val="20"/>
        <w:szCs w:val="20"/>
        <w:color w:val="221D18"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:after="60" w:line="240" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="TituloPrincipal">
    <w:name w:val="TituloPrincipal"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:before="0" w:after="40"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="6F1D1B"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="SubtituloFicha">
    <w:name w:val="SubtituloFicha"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:before="0" w:after="120"/></w:pPr>
    <w:rPr><w:i/><w:sz w:val="20"/><w:color w:val="5A4A3F"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="SecaoTitulo">
    <w:name w:val="SecaoTitulo"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="180" w:after="60"/>
      <w:pBdr><w:bottom w:val="single" w:sz="10" w:space="3" w:color="6F1D1B"/></w:pBdr>
    </w:pPr>
    <w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="6F1D1B"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="SubsecaoTitulo">
    <w:name w:val="SubsecaoTitulo"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="120" w:after="40"/>
    </w:pPr>
    <w:rPr><w:b/><w:sz w:val="21"/><w:color w:val="5A4A3F"/></w:rPr>
  </w:style>
</w:styles>
"""


def _xml_p(texto: str, estilo: str | None = None, negrito: bool = False, cor: str | None = None, tam_half_pt: int | None = None) -> str:
    ppr = f"<w:pPr><w:pStyle w:val=\"{estilo}\"/></w:pPr>" if estilo else ""
    rpr_parts = []
    if negrito:
        rpr_parts.append("<w:b/>")
    if cor:
        rpr_parts.append(f"<w:color w:val=\"{cor}\"/>")
    if tam_half_pt:
        rpr_parts.append(f"<w:sz w:val=\"{tam_half_pt}\"/><w:szCs w:val=\"{tam_half_pt}\"/>")
    rpr = f"<w:rPr>{''.join(rpr_parts)}</w:rPr>" if rpr_parts else ""
    return f"<w:p>{ppr}<w:r>{rpr}<w:t xml:space=\"preserve\">{_limpar_xml(texto)}</w:t></w:r></w:p>"


def _xml_p_rotulo(rotulo: str, valor: str) -> str:
    return (
        "<w:p><w:r><w:rPr><w:b/><w:color w:val=\"5A4A3F\"/></w:rPr>"
        f"<w:t xml:space=\"preserve\">{_limpar_xml(rotulo)}: </w:t></w:r>"
        f"<w:r><w:t xml:space=\"preserve\">{_limpar_xml(valor)}</w:t></w:r></w:p>"
    )


def _xml_tabela(cabecalhos: list[str], linhas: list[list[Any]], larguras: list[int]) -> str:
    """Constrói uma tabela OOXML estilizada; largura total útil A4 = 10466 dxa."""
    grid = "".join(f"<w:gridCol w:w=\"{w}\"/>" for w in larguras)
    tbl_pr = (
        "<w:tblPr>"
        f"<w:tblW w:w=\"{sum(larguras)}\" w:type=\"dxa\"/>"
        "<w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"C7B69D\"/>"
        "<w:left w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"C7B69D\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"C7B69D\"/>"
        "<w:right w:val=\"single\" w:sz=\"6\" w:space=\"0\" w:color=\"C7B69D\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"E2D6C3\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"E2D6C3\"/>"
        "</w:tblBorders>"
        "<w:tblCellMar>"
        "<w:top w:w=\"60\" w:type=\"dxa\"/><w:left w:w=\"90\" w:type=\"dxa\"/>"
        "<w:bottom w:w=\"60\" w:type=\"dxa\"/><w:right w:w=\"90\" w:type=\"dxa\"/>"
        "</w:tblCellMar>"
        "</w:tblPr>"
    )

    def _celula(texto: Any, largura: int, fundo: str | None = None, eh_header: bool = False) -> str:
        shd = f"<w:shd w:val=\"clear\" w:color=\"auto\" w:fill=\"{fundo}\"/>" if fundo else ""
        tcpr = f"<w:tcPr><w:tcW w:w=\"{largura}\" w:type=\"dxa\"/>{shd}</w:tcPr>"
        valor_str = "" if texto is None else str(texto)
        if eh_header:
            par = _xml_p(valor_str, negrito=True, cor="6F1D1B", tam_half_pt=18)
        else:
            par = _xml_p(valor_str, tam_half_pt=18)
        return f"<w:tc>{tcpr}{par}</w:tc>"

    trs = []
    hdr_cells = "".join(_celula(h, larguras[i], fundo="F4ECE1", eh_header=True) for i, h in enumerate(cabecalhos))
    trs.append(f"<w:tr><w:trPr><w:tblHeader/></w:trPr>{hdr_cells}</w:tr>")

    for idx_row, linha in enumerate(linhas):
        fundo_row = "FCF9F3" if idx_row % 2 == 1 else None
        cells = "".join(_celula(linha[i], larguras[i], fundo=fundo_row) for i in range(len(cabecalhos)))
        trs.append(f"<w:tr>{cells}</w:tr>")

    return f"<w:tbl>{tbl_pr}<w:tblGrid>{grid}</w:tblGrid>{''.join(trs)}</w:tbl>"


def _montar_document_xml(resultado: dict[str, Any]) -> str:
    meta = resultado.get("meta_geracao", {})
    ficha = resultado["ficha"]
    cab = ficha["cabecalho"]
    partes: list[str] = []

    # Cabeçalho Principal
    partes.append(_xml_p(cab["nome_personagem"], estilo="TituloPrincipal"))
    partes.append(
        _xml_p(
            f"Pathfinder 2ª Edição • Nível {cab['nivel']} • {cab['ancestralidade_e_heranca']} • {cab['classe']}",
            estilo="SubtituloFicha",
        )
    )
    bio_modo = "Procedural" if meta.get("biografia_procedural", True) else "Manual"
    sub_doc_txt = meta.get("subclasse_oficial_nome") or "—"
    if meta.get("tese_arcana_nome"):
        sub_doc_txt = f"{sub_doc_txt} • Tese: {meta['tese_arcana_nome']}"
    info_geral = [
        ["Biografia", f"{cab['biografia']} ({bio_modo})", "Tamanho / Tendência", f"{cab['tamanho']} / {cab['tendencia']}"],
        ["Subclasse PF2E", sub_doc_txt, "Pontos de Heroísmo", f"{cab['pontos_heroismo']} / 3"],
        ["Divindade", cab.get("divindade") or "—", "Seed / Saldo", f"{meta.get('seed', '—')} / {meta.get('saldo_restante', '—')}"],
        ["Jogador", cab.get("nome_jogador") or "—", "Traços", ", ".join(cab.get("tracos") or []) or "—"],
    ]
    partes.append(_xml_tabela(["Campo", "Valor", "Campo", "Valor"], info_geral, [1700, 3533, 1900, 3333]))

    # Página 1 — Atributos e Combate
    partes.append(_xml_p("Página 1 (p. 580) — Atributos, Combate e Perícias", estilo="SecaoTitulo"))

    partes.append(_xml_p("Atributos (Sistema ABCD)", estilo="SubsecaoTitulo"))
    linhas_atr = []
    for aid, (sigla, nome_atr) in _NOME_ATRIBUTO_SIGLA.items():
        atr = ficha["atributos"][aid]
        linhas_atr.append([sigla, nome_atr, atr["valor"], formatar_bonus(atr["modificador"])])
    partes.append(_xml_tabela(["Sigla", "Atributo", "Valor", "Modificador"], linhas_atr, [1200, 4266, 2500, 2500]))

    if meta.get("historico_abcd"):
        resumo_abcd = " | ".join(
            f"[{s['etapa']}] " + ", ".join(f"{k.upper()} {formatar_bonus(v)}" for k, v in s["deltas"].items())
            for s in meta["historico_abcd"]
        )
        partes.append(_xml_p_rotulo("Composição ABCD", resumo_abcd))

    partes.append(_xml_p("Defesas, Pontos de Vida e Salvamentos", estilo="SubsecaoTitulo"))
    pv = ficha["pontos_vida"]
    ca = ficha["classe_armadura"]
    vel = ficha["velocidade"]
    perc = ficha["percepcao"]
    cd = ficha["cd_classe"]
    salv = ficha["jogadas_salvamento"]
    obs_comb = meta.get("observacoes_combate") or {}
    morr_lim = meta.get("limite_morrendo") or obs_comb.get("limite_morrendo")
    pv_txt = f"{pv['max']} PV" + (f" (Morrendo Máx {morr_lim})" if morr_lim and morr_lim != 4 else "")
    ca_txt = f"{ca['total']} [{_formatar_grau_curto(ca['grau_proficiencia'])}]"
    if obs_comb.get("ca_com_escudo"):
        ca_txt += f" ({obs_comb['ca_com_escudo']} c/ Escudo)"
    linhas_comb = [
        ["Pontos de Vida", pv_txt, "Classe de Armadura", ca_txt],
        ["Velocidade", f"{formatar_metros(vel['metros'])} m", "Percepção", f"{formatar_bonus(perc['total'])} [{_formatar_grau_curto(perc['grau_proficiencia'])}]"],
        ["CD de Classe", f"{cd['total']} [{_formatar_grau_curto(cd['grau_proficiencia'])}]", "Fortitude", f"{formatar_bonus(salv['fortitude']['total'])} [{_formatar_grau_curto(salv['fortitude']['grau_proficiencia'])}]"],
        ["Reflexos", f"{formatar_bonus(salv['reflexos']['total'])} [{_formatar_grau_curto(salv['reflexos']['grau_proficiencia'])}]", "Vontade", f"{formatar_bonus(salv['vontade']['total'])} [{_formatar_grau_curto(salv['vontade']['grau_proficiencia'])}]"],
    ]
    partes.append(_xml_tabela(["Estatística", "Valor", "Estatística", "Valor"], linhas_comb, [2300, 2933, 2300, 2933]))
    partes.append(_xml_p_rotulo("Armadura", meta.get("armadura_equipada_resumo") or meta.get("armadura_equipada", "Nenhuma armadura")))

    if obs_comb.get("nota_postura"):
        partes.append(_xml_p_rotulo("Postura de Combate", obs_comb["nota_postura"]))

    if perc.get("sentidos"):
        partes.append(_xml_p_rotulo("Sentidos", ", ".join(perc["sentidos"])))
    if pv.get("resistencias_e_imunidades"):
        partes.append(_xml_p_rotulo("Resistências e Imunidades", pv["resistencias_e_imunidades"]))
    esc = ca["escudo"]
    if esc.get("nome"):
        partes.append(
            _xml_p_rotulo(
                "Escudo",
                f"{esc['nome']} (+{esc['bonus_ca']} CA ao Erguer | Dureza {esc['dureza']} | PV {esc['pv_max']} | LQ {esc['limiar_quebra']})",
            )
        )

    partes.append(_xml_p("Golpes e Proficiências de Combate", estilo="SubsecaoTitulo"))
    linhas_golpes = []
    for tipo_rot, lista_g in (("Corpo a Corpo", ficha["golpes_corpo_a_corpo"]), ("À Distância", ficha["golpes_a_distancia"])):
        for g in lista_g:
            if g.get("arma"):
                arma, atk, dano_str, tracos = _formatar_linha_golpe(g)
                linhas_golpes.append([tipo_rot, arma, atk, dano_str, tracos])
    if linhas_golpes:
        partes.append(_xml_tabela(["Tipo", "Arma", "Ataque", "Dano", "Traços"], linhas_golpes, [1700, 2500, 1100, 1900, 3266]))

    arm_prof = " | ".join(f"{p['rotulo']}: {_formatar_grau_curto(p['grau_proficiencia'])}" for p in ficha["proficiencia_armas"])
    def_prof = " | ".join(f"{k.replace('_', ' ').title()}: {_formatar_grau_curto(v)}" for k, v in ca["proficiencias_armadura"].items())
    partes.append(_xml_p_rotulo("Proficiência com Armas", arm_prof))
    partes.append(_xml_p_rotulo("Proficiência com Armaduras", def_prof))

    partes.append(_xml_p("Perícias (18 Linhas Oficiais) e Idiomas", estilo="SubsecaoTitulo"))
    linhas_per = []
    for per in ficha["pericias"]:
        nome_exib = per["rotulo_oficial"]
        if per.get("especializacao"):
            nome_exib = f"{nome_exib} ({per['especializacao']})"
        elif per["id"] in ("saber_1", "saber_2"):
            nome_exib = f"{nome_exib} (—)"
        pen_txt = str(per["penalidade_armadura"]) if per.get("penalidade_armadura") else "—"
        linhas_per.append(
            [
                nome_exib,
                formatar_bonus(per["total"]),
                _formatar_grau_curto(per["grau_proficiencia"]),
                f"{per['atributo_chave'].upper()} ({formatar_bonus(per['mod_atributo'])})",
                pen_txt,
            ]
        )
    partes.append(_xml_tabela(["Perícia", "Total", "Grau", "Atributo", "Armadura"], linhas_per, [4366, 1200, 1000, 2400, 1500]))
    partes.append(_xml_p_rotulo("Idiomas", ", ".join(ficha.get("idiomas") or [])))

    # Página 2 — Talentos e Inventário
    partes.append(_xml_p("Página 2 (p. 581) — Habilidades, Talentos e Inventário", estilo="SecaoTitulo"))
    partes.append(_xml_p("Habilidades e Talentos", estilo="SubsecaoTitulo"))
    linhas_tal = [[cat, rot, nome, orig] for cat, rot, nome, orig in _coletar_talentos_preenchidos(ficha)]
    partes.append(_xml_tabela(["Categoria", "Nível/Slot", "Nome", "Origem"], linhas_tal, [1800, 1800, 3200, 3666]))

    partes.append(_xml_p("Inventário, Volume e Riqueza", estilo="SubsecaoTitulo"))
    inv = ficha["inventario"]
    linhas_inv = []
    for sec_nome, chave in (("Vestido", "itens_vestidos"), ("Preparado", "itens_preparados"), ("Outros", "outros_itens")):
        for item in inv[chave]:
            linhas_inv.append([sec_nome, item["nome"], item.get("quantidade", 1), item["volume"]])
    if linhas_inv:
        partes.append(_xml_tabela(["Local", "Item", "Qtd", "Volume"], linhas_inv, [1600, 6266, 1100, 1500]))
    riq = inv["riqueza"]
    partes.append(
        _xml_p_rotulo(
            "Carga e Moedas",
            f"Volume {inv['volume_total']} (Sobrecarregado > {inv['volume_sobrecarregado']} / Máximo {inv['volume_maximo']}) | "
            f"{riq['po']} po, {riq['pp']} pp, {riq['pc']} pc ({riq['pl']} pl)",
        )
    )

    # Página 3 — Perfil e Ações
    partes.append(_xml_p("Página 3 (p. 582) — Perfil, Campanha e Ações", estilo="SecaoTitulo"))
    anot = ficha["perfil_e_campanha"]["anotacoes_campanha"].get("anotacoes")
    if anot:
        partes.append(_xml_p_rotulo("Proposta e Campanha", anot))
    div_det = meta.get("divindade_detalhes")
    if div_det:
        partes.append(_xml_p(f"Divindade — {div_det['nome']} ({div_det['tendencia']})", estilo="SubsecaoTitulo"))
        partes.append(
            _xml_tabela(
                ["Arma Favorecida", "Domínios", "Éditos", "Anátema"],
                [[div_det["arma_favorecida_nome"], ", ".join(div_det["dominios"]), div_det["editos"], div_det["anatema"]]],
                [1800, 2300, 3183, 3183],
            )
        )
    comp = meta.get("companheiro_ou_familiar")
    if comp:
        partes.append(_xml_p(f"{comp['categoria']} — {comp['nome']}", estilo="SubsecaoTitulo"))
        if comp["categoria"] == "Companheiro Animal":
            atks_txt = "; ".join(f"{a['nome']} {formatar_bonus(a['ataque_total'])} ({a['dano']})" for a in comp["ataques"])
            partes.append(
                _xml_tabela(
                    ["Estágio / Tamanho", "PV / CA / Vel", "Ataques", "Benefício de Suporte"],
                    [[
                        f"{comp['estagio']} ({comp['tamanho']})",
                        f"PV {comp['pv_max']} | CA {comp['ca']} | {comp['velocidades']}",
                        atks_txt,
                        comp["beneficio_de_suporte"],
                    ]],
                    [2000, 2200, 2500, 3766],
                )
            )
        else:
            habs_txt = "; ".join(f"{h['nome']}: {h['descricao']}" for h in comp["habilidades_selecionadas"])
            partes.append(
                _xml_tabela(
                    ["Espécie / Tamanho", "PV / CA / Percepção", "Habilidades Selecionadas"],
                    [[
                        f"{comp['nome']} ({comp['tamanho']})",
                        f"PV {comp['pv_max']} | CA {comp['ca']} | Perc/Acrob/Furt {formatar_bonus(comp['percepcao'])}",
                        habs_txt,
                    ]],
                    [2300, 2400, 5766],
                )
            )
    linhas_acoes = []
    for a in ficha["acoes_e_atividades"]:
        if a.get("nome"):
            linhas_acoes.append([_formatar_custo_acao(a.get("acoes", "1")), a["nome"], ", ".join(a.get("tracos") or []) or "—", a.get("descricao", "")])
    for a in ficha["acoes_livres_e_reacoes"]:
        if a.get("nome"):
            desc_full = (f"Acionamento: {a['acionamento']} " if a.get("acionamento") else "") + a.get("descricao", "")
            linhas_acoes.append([a.get("tipo", "REAÇÃO"), a["nome"], ", ".join(a.get("tracos") or []) or "—", desc_full])
    if linhas_acoes:
        partes.append(_xml_tabela(["Tipo", "Ação / Habilidade", "Traços", "Efeito"], linhas_acoes, [1400, 2200, 2100, 4766]))

    # Página 4 — Conjuração
    conj = ficha["conjuracao"]
    if _tem_conjuracao(conj):
        partes.append(_xml_p("Página 4 (p. 583) — Conjuração e Magias", estilo="SecaoTitulo"))
        trad_txt, est_txt = _tradicao_e_estilo_texto(conj)
        partes.append(
            _xml_p_rotulo(
                "Atributos de Conjuração",
                f"Tradição {trad_txt} ({est_txt}) | Ataque de Magia {formatar_bonus(conj['ataque_magia']['total'])} | "
                f"CD {conj['cd_magia']['total']} | Nível de Truque {conj['nivel_truque']} | "
                f"Espaços 1º Círculo/Dia: {conj['espacos_magia_por_dia'].get('1', 0)} | "
                f"Pontos de Foco: {conj['magias_foco']['pontos_foco']['maximo']}",
            )
        )
        linhas_mag = []
        for grp, lst, mostrar_prep in (
            ("Truque", conj["truques_magicos"], False),
            ("Foco", conj["magias_foco"]["slots"], False),
            ("Inata", conj["magias_inatas"], False),
            ("1º Círculo", conj["magias"], True),
        ):
            for m in lst:
                if m.get("nome"):
                    notas_base = m.get("frequencia") or m.get("anotacoes") or ""
                    if mostrar_prep and m.get("preparada"):
                        extra = f"Preparada • {notas_base}" if notas_base else "Preparada"
                    else:
                        extra = notas_base or "—"
                    linhas_mag.append([grp, m["nome"], m.get("acoes") or "—", ",".join(m.get("componentes") or []) or "—", extra])
        if linhas_mag:
            partes.append(_xml_tabela(["Categoria", "Magia", "Ações", "Comp.", "Observações"], linhas_mag, [1400, 2800, 1000, 1200, 4066]))

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        "<w:body>"
        + "".join(partes)
        + "<w:sectPr>"
        "<w:pgSz w:w=\"11906\" w:h=\"16838\"/>"
        "<w:pgMar w:top=\"720\" w:right=\"720\" w:bottom=\"720\" w:left=\"720\" w:header=\"450\" w:footer=\"450\" w:gutter=\"0\"/>"
        "</w:sectPr>"
        "</w:body></w:document>"
    )


def exportar_ficha_docx(resultado: dict[str, Any]) -> bytes:
    """Exporta a ficha completa em bytes `.docx` válidos (OOXML ECMA-376)."""
    documento_xml = _montar_document_xml(resultado)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _CONTENT_TYPES_XML.encode("utf-8"))
        zf.writestr("_rels/.rels", _ROOT_RELS_XML.encode("utf-8"))
        zf.writestr("word/_rels/document.xml.rels", _DOC_RELS_XML.encode("utf-8"))
        zf.writestr("word/styles.xml", _STYLES_XML.encode("utf-8"))
        zf.writestr("word/document.xml", documento_xml.encode("utf-8"))
    return buffer.getvalue()


# ==============================================================================
# Exportação PDF Oficial (sobreposto em `ref/Sheet Update.pdf` + `estrutura_ficha.json`)
# ==============================================================================

_RAIZ_PROJETO = Path(__file__).resolve().parent.parent
_TEMPLATE_PDF_OFICIAL = _RAIZ_PROJETO / "ref" / "Sheet Update.pdf"

_PDF_COR_TINTA = (0.06, 0.09, 0.22)
_PDF_COR_DESTAQUE = (0.48, 0.08, 0.08)
_PDF_COR_CAIXA_TEML = (0.12, 0.10, 0.09)

_PDF_MAPA_GRAU_INDICE = {
    "treinado": 0,
    "especialista": 1,
    "mestre": 2,
    "lendario": 3,
}
_PDF_SIGLAS_TEML = ("T", "E", "M", "L")

_PDF_PERICIAS_YS = (
    344.2, 365.8, 387.4, 409.1, 430.7, 452.3,
    474.0, 495.6, 517.2, 538.8, 560.5, 582.1,
    603.7, 625.4, 647.0, 668.8, 690.2, 711.9,
)

_PDF_TALENTOS_ANCESTRALIDADE_YS = (34.5, 53.7, 73.4, 92.5, 112.2, 131.3, 151.0)
_PDF_TALENTOS_PERICIA_YS = (
    190.0, 210.0, 229.6, 248.7, 268.2, 288.3, 307.4, 326.9, 347.0, 366.5, 385.6,
)
_PDF_TALENTOS_GERAIS_YS = (423.3, 442.6, 462.4, 482.2, 502.1)
_PDF_TALENTOS_CLASSE_YS = (
    34.1, 53.6, 73.1, 92.6, 112.2, 131.7, 151.2, 170.7, 190.2, 209.7, 229.3,
    248.8, 268.3, 287.8, 307.3, 326.8, 346.4, 365.9, 385.4, 404.9, 424.9, 444.4,
)
_PDF_TALENTOS_BONUS_YS = (481.6, 501.8)

_PDF_MAGIAS_YS = (
    114.2, 154.7, 195.2, 235.7, 276.2, 316.7, 357.2, 397.7,
    438.2, 478.6, 519.1, 559.6, 600.1, 640.6, 681.1, 721.6,
)
_PDF_TRUQUES_YS = (217.8, 260.5, 303.2, 346.0, 388.8, 431.5, 474.2)


def _pdf_sanitizar_texto(texto: Any) -> str:
    """Normaliza símbolos Unicode não cobertos por Latin-1 Base14 Helvetica."""
    bruto = "" if texto is None else str(texto)
    substituicoes = (
        ("◆", "[1A]"),
        ("◇", "[L]"),
        ("↺", "[R]"),
        ("—", " - "),
        ("–", "-"),
        ("•", " / "),
        ("“", '"'),
        ("”", '"'),
        ("‘", "'"),
        ("’", "'"),
        ("…", "..."),
        ("\u00a0", " "),
    )
    for antigo, novo in substituicoes:
        bruto = bruto.replace(antigo, novo)
    return bruto.encode("latin-1", errors="replace").decode("latin-1").strip()


def _pdf_acao_curta(acoes: Any) -> str:
    ac = str(acoes or "").strip().lower()
    mapa = {
        "1": "1A",
        "2": "2A",
        "3": "3A",
        "livre": "Livre",
        "ação livre": "Livre",
        "acao livre": "Livre",
        "reacao": "Reação",
        "reação": "Reação",
    }
    return mapa.get(ac, _pdf_sanitizar_texto(acoes))


def _pdf_inserir_linha(
    page: Any,
    pymupdf: Any,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    texto: Any,
    *,
    fontsize: float = 9.0,
    align: int = 0,
    bold: bool = False,
    color: tuple[float, float, float] = _PDF_COR_TINTA,
    min_fontsize: float = 4.2,
) -> None:
    """Escreve texto de linha única ajustando a fonte e alinhamento dentro da caixa."""
    txt = _pdf_sanitizar_texto(texto)
    if not txt:
        return
    fontname = "hebo" if bold else "helv"
    rect_w = x1 - x0
    rect_h = y1 - y0
    max_w = max(4.0, rect_w - 3.0)
    fs = min(fontsize, max(min_fontsize, (rect_h - 0.8) / 0.82))
    while fs > min_fontsize and pymupdf.get_text_length(txt, fontname=fontname, fontsize=fs) > max_w:
        fs = round(fs - 0.4, 2)
    fs = max(fs, min_fontsize)

    if pymupdf.get_text_length(txt, fontname=fontname, fontsize=fs) > max_w:
        base = txt
        while len(base) > 1 and pymupdf.get_text_length(base + "...", fontname=fontname, fontsize=fs) > max_w:
            base = base[:-1]
        txt = (base.rstrip() + "...") if len(base) > 1 else txt[:1]

    tw = pymupdf.get_text_length(txt, fontname=fontname, fontsize=fs)
    if align == 1:
        px = x0 + max(1.0, (rect_w - tw) / 2.0)
    elif align == 2:
        px = x1 - tw - 1.5
    else:
        px = x0 + 1.5
    baseline_y = y0 + (rect_h + fs * 0.68) / 2.0
    page.insert_text(pymupdf.Point(px, baseline_y), txt, fontsize=fs, fontname=fontname, color=color)


def _pdf_inserir_bloco(
    page: Any,
    pymupdf: Any,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    texto: Any,
    *,
    fontsize: float = 7.5,
    bold: bool = False,
    color: tuple[float, float, float] = _PDF_COR_TINTA,
    min_fontsize: float = 4.5,
) -> None:
    """Escreve texto multilinha garantindo encaixe dentro de `Rect(x0, y0, x1, y1)`."""
    txt = _pdf_sanitizar_texto(texto)
    if not txt:
        return
    fontname = "hebo" if bold else "helv"
    rect = pymupdf.Rect(x0, y0, x1, y1)
    fs = fontsize
    while fs >= min_fontsize:
        shape = page.new_shape()
        rc = shape.insert_textbox(
            rect, txt, fontsize=fs, fontname=fontname, color=color, align=0, lineheight=1.1
        )
        if rc >= 0:
            shape.commit()
            return
        fs = round(fs - 0.5, 2)

    palavras = txt.split()
    while len(palavras) > 1:
        palavras.pop()
        candidato = " ".join(palavras) + "..."
        shape = page.new_shape()
        rc = shape.insert_textbox(
            rect, candidato, fontsize=min_fontsize, fontname=fontname, color=color, align=0, lineheight=1.08
        )
        if rc >= 0:
            shape.commit()
            return
    _pdf_inserir_linha(page, pymupdf, x0, y0, x1, y1, txt, fontsize=min_fontsize, bold=bold, color=color)


def _pdf_marcar_teml(
    page: Any,
    pymupdf: Any,
    grau: str | None,
    xs_teml: tuple[float, float, float, float],
    y_top: float,
    *,
    w: float = 7.0,
    h: float = 10.8,
) -> None:
    """Destaca a caixinha T/E/M/L oficial para o grau informado."""
    idx = _PDF_MAPA_GRAU_INDICE.get((grau or "").strip().lower())
    if idx is None:
        return
    x = xs_teml[idx]
    rect = pymupdf.Rect(x, y_top, x + w, y_top + h)
    page.draw_rect(rect, color=None, fill=_PDF_COR_CAIXA_TEML)
    _pdf_inserir_linha(
        page, pymupdf, x, y_top, x + w, y_top + h,
        _PDF_SIGLAS_TEML[idx],
        fontsize=max(4.4, min(6.2, h * 0.72)),
        align=1,
        bold=True,
        color=(1.0, 1.0, 1.0),
        min_fontsize=3.6,
    )


def _pdf_marcar_checkbox(
    page: Any,
    pymupdf: Any,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    ativo: bool,
) -> None:
    """Marca um pequeno quadrado da ficha oficial quando `ativo` for verdadeiro."""
    if not ativo:
        return
    rect = pymupdf.Rect(x0, y0, x1, y1)
    page.draw_rect(rect, color=_PDF_COR_DESTAQUE, fill=(0.94, 0.87, 0.85), width=0.6)
    _pdf_inserir_linha(
        page, pymupdf, x0, y0, x1, y1, "X",
        fontsize=max(4.2, (y1 - y0) * 0.82), align=1, bold=True, color=_PDF_COR_DESTAQUE, min_fontsize=3.5,
    )


def _pdf_preencher_golpe(page: Any, pymupdf: Any, golpe: dict[str, Any], y_base: float, *, distancia: bool) -> None:
    """Preenche um slot de Golpe Corpo a Corpo ou À Distância nas coordenadas oficiais."""
    arma = golpe.get("arma") or ""
    if not arma:
        return
    atk = golpe["ataque"]
    dano = golpe["dano"]
    _pdf_inserir_linha(page, pymupdf, 22.0, y_base + 7.5, 145.5, y_base + 23.0, arma, fontsize=8.5, bold=True)
    _pdf_inserir_linha(
        page, pymupdf, 151.5, y_base + 2.5, 187.5, y_base + 28.5,
        formatar_bonus(atk["total"]), fontsize=12.0, align=1, bold=True,
    )
    _pdf_inserir_linha(page, pymupdf, 200.5, y_base + 8.5, 223.5, y_base + 25.5, formatar_bonus(atk["mod_atributo"]), fontsize=8.5, align=1)
    _pdf_inserir_linha(page, pymupdf, 226.0, y_base + 8.5, 249.5, y_base + 25.5, formatar_bonus(atk["proficiencia"]), fontsize=8.5, align=1)
    _pdf_marcar_teml(page, pymupdf, atk.get("grau_proficiencia"), (252.0, 259.9, 267.9, 275.9), y_base + 12.4)
    if atk.get("item"):
        _pdf_inserir_linha(page, pymupdf, 286.0, y_base + 8.5, 309.0, y_base + 25.5, formatar_bonus(atk["item"]), fontsize=8.5, align=1)

    _pdf_inserir_linha(page, pymupdf, 21.5, y_base + 39.5, 45.2, y_base + 54.5, dano.get("dados") or "", fontsize=8.5, align=1, bold=True)
    mod_dano = dano.get("especial") if distancia else dano.get("for")
    if mod_dano:
        _pdf_inserir_linha(page, pymupdf, 51.8, y_base + 39.5, 75.5, y_base + 54.5, formatar_bonus(mod_dano), fontsize=8.5, align=1)

    tipos_norm = {t.strip().upper() for t in (dano.get("tipos_dano") or [])}
    _pdf_marcar_checkbox(page, pymupdf, 81.4, y_base + 33.7, 87.7, y_base + 39.4, "CN" in tipos_norm or "C" in tipos_norm)
    _pdf_marcar_checkbox(page, pymupdf, 81.4, y_base + 41.4, 87.7, y_base + 47.1, "CT" in tipos_norm)
    _pdf_marcar_checkbox(page, pymupdf, 81.4, y_base + 49.0, 87.7, y_base + 54.7, "PF" in tipos_norm or "P" in tipos_norm)

    if not distancia and dano.get("especial"):
        _pdf_inserir_linha(page, pymupdf, 101.5, y_base + 39.5, 125.5, y_base + 54.5, formatar_bonus(dano["especial"]), fontsize=8.0, align=1)
    outro_txt = dano.get("outro") or (f"Alc. {golpe['alcance_ou_incremento']}" if distancia and golpe.get("alcance_ou_incremento") else "")
    _pdf_inserir_linha(page, pymupdf, 129.5, y_base + 39.5, 197.0, y_base + 54.5, outro_txt, fontsize=6.8)
    _pdf_inserir_linha(page, pymupdf, 200.0, y_base + 39.5, 309.5, y_base + 54.5, ", ".join(dano.get("tracos") or []), fontsize=6.5)


def _pdf_preencher_pagina_1(page: Any, pymupdf: Any, resultado: dict[str, Any]) -> None:
    """Preenche todos os blocos da Página 1 (p. 580)."""
    ficha = resultado["ficha"]
    meta = resultado.get("meta_geracao") or {}
    cab = ficha["cabecalho"]

    # Cabeçalho
    _pdf_inserir_linha(page, pymupdf, 141.0, 33.0, 336.0, 57.5, cab["nome_personagem"], fontsize=13.5, bold=True)
    _pdf_inserir_linha(page, pymupdf, 168.0, 63.0, 336.0, 81.0, cab.get("nome_jogador") or "", fontsize=9.0)
    _pdf_inserir_linha(page, pymupdf, 197.0, 86.0, 336.0, 99.0, str(cab.get("pontos_experiencia", 0)), fontsize=8.0)
    _pdf_inserir_linha(page, pymupdf, 344.0, 25.0, 527.5, 35.0, cab["ancestralidade_e_heranca"], fontsize=7.8, bold=True)
    _pdf_inserir_linha(page, pymupdf, 344.0, 44.0, 527.5, 54.0, cab["biografia"], fontsize=7.8)
    classe_full = cab["classe"]
    if meta.get("subclasse_oficial_nome"):
        classe_full = f"{classe_full} ({meta['subclasse_oficial_nome']})"
    _pdf_inserir_linha(page, pymupdf, 344.0, 63.0, 527.5, 73.0, classe_full, fontsize=7.8, bold=True)
    _pdf_inserir_linha(page, pymupdf, 342.0, 81.2, 372.0, 87.0, cab["tamanho"], fontsize=5.8, align=1, min_fontsize=4.0)
    _pdf_inserir_linha(page, pymupdf, 375.0, 81.2, 421.0, 87.0, cab["tendencia"], fontsize=6.0, align=1, bold=True, min_fontsize=4.0)
    _pdf_inserir_linha(page, pymupdf, 424.0, 81.2, 528.5, 87.0, ", ".join(cab.get("tracos") or []), fontsize=5.5, min_fontsize=3.8)
    _pdf_inserir_linha(page, pymupdf, 378.0, 89.2, 528.5, 99.5, cab.get("divindade") or "", fontsize=7.2)
    _pdf_inserir_linha(page, pymupdf, 535.0, 33.0, 583.0, 58.0, str(cab["nivel"]), fontsize=16.0, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 540.0, 76.0, 578.0, 97.5, f"{cab.get('pontos_heroismo', 1)} / 3", fontsize=9.5, align=1, bold=True)

    # Atributos
    ordem_atb = ("for", "des", "con", "int", "sab", "car")
    ys_atb = (121.5, 149.0, 176.5, 204.1, 231.6, 259.1)
    for aid, y0 in zip(ordem_atb, ys_atb):
        atb = ficha["atributos"][aid]
        _pdf_inserir_linha(page, pymupdf, 20.5, y0 + 1.0, 54.0, y0 + 21.5, formatar_bonus(atb["modificador"]), fontsize=12.5, align=1, bold=True)
        _pdf_inserir_linha(page, pymupdf, 165.5, y0 + 1.0, 193.0, y0 + 18.5, str(atb["valor"]), fontsize=10.5, align=1, bold=True)

    # Classe de Armadura & Escudo
    ca = ficha["classe_armadura"]
    mod_des_ficha = ficha["atributos"]["des"]["modificador"]
    _pdf_inserir_linha(page, pymupdf, 232.0, 134.5, 271.0, 159.5, str(ca["total"]), fontsize=15.0, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 303.5, 128.0, 325.0, 145.0, formatar_bonus(mod_des_ficha), fontsize=8.5, align=1)
    if ca.get("limite_des_armadura") is not None:
        _pdf_inserir_linha(page, pymupdf, 331.5, 128.0, 353.0, 145.0, formatar_bonus(ca["limite_des_armadura"]), fontsize=8.5, align=1)
    _pdf_inserir_linha(page, pymupdf, 355.5, 128.0, 378.5, 145.0, formatar_bonus(ca["proficiencia"]), fontsize=8.5, align=1)
    _pdf_marcar_teml(page, pymupdf, ca.get("grau_proficiencia"), (381.6, 389.5, 397.6, 405.5), 131.4)
    if ca.get("item"):
        _pdf_inserir_linha(page, pymupdf, 415.5, 127.0, 438.5, 144.5, formatar_bonus(ca["item"]), fontsize=8.5, align=1)

    profs_arm = ca["proficiencias_armadura"]
    _pdf_marcar_teml(page, pymupdf, profs_arm.get("sem_armadura"), (289.8, 297.7, 305.8, 313.7), 159.4, h=6.3)
    _pdf_marcar_teml(page, pymupdf, profs_arm.get("leve"), (326.9, 334.8, 342.9, 350.8), 159.4, h=6.3)
    _pdf_marcar_teml(page, pymupdf, profs_arm.get("media"), (364.1, 372.0, 380.0, 388.0), 159.4, h=6.3)
    _pdf_marcar_teml(page, pymupdf, profs_arm.get("pesada"), (401.2, 409.1, 417.2, 425.1), 159.7, h=6.3)

    arm_resumo = meta.get("armadura_equipada_resumo") or meta.get("armadura_equipada") or ""
    if arm_resumo:
        page.draw_rect(
            pymupdf.Rect(206.5, 168.0, 276.0, 195.8),
            color=(0.50, 0.36, 0.24),
            fill=(0.98, 0.96, 0.92),
            width=0.6,
        )
        _pdf_inserir_bloco(page, pymupdf, 208.5, 169.5, 274.5, 194.5, arm_resumo, fontsize=6.0, bold=False, min_fontsize=4.2)

    esc = ca["escudo"]
    if esc.get("nome"):
        _pdf_inserir_linha(page, pymupdf, 306.0, 174.0, 327.0, 194.5, formatar_bonus(esc["bonus_ca"]), fontsize=9.5, align=1, bold=True)
        _pdf_inserir_linha(page, pymupdf, 334.5, 180.2, 364.5, 193.5, str(esc["dureza"]), fontsize=8.0, align=1)
        _pdf_inserir_linha(page, pymupdf, 372.0, 180.2, 391.0, 193.5, str(esc["pv_max"]), fontsize=7.2, align=1)
        _pdf_inserir_linha(page, pymupdf, 396.5, 180.2, 407.0, 193.5, str(esc["limiar_quebra"]), fontsize=7.2, align=1)
        _pdf_inserir_linha(page, pymupdf, 414.0, 180.2, 447.0, 193.5, str(esc["pv_atuais"]), fontsize=8.0, align=1)

    # Pontos de Vida
    pv = ficha["pontos_vida"]
    _pdf_inserir_linha(page, pymupdf, 464.5, 108.5, 489.0, 132.5, str(pv["max"]), fontsize=12.0, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 465.5, 132.0, 521.0, 173.0, str(pv["atuais"]), fontsize=13.5, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 526.0, 130.5, 580.5, 149.0, str(pv.get("temporarios", 0) or ""), fontsize=9.0, align=1)
    _pdf_inserir_linha(page, pymupdf, 526.0, 158.5, 548.0, 174.0, str(pv.get("ferido", 0) or "0"), fontsize=8.0, align=1)
    morr_lim = meta.get("limite_morrendo")
    morr_txt = f"0/{morr_lim}" if morr_lim and morr_lim != 4 else str(pv.get("morrendo", 0) or "0")
    _pdf_inserir_linha(page, pymupdf, 551.0, 158.5, 580.8, 174.0, morr_txt, fontsize=8.0, align=1)
    _pdf_inserir_bloco(page, pymupdf, 466.0, 185.0, 580.0, 206.0, pv.get("resistencias_e_imunidades") or "", fontsize=6.5)
    _pdf_inserir_bloco(page, pymupdf, 466.0, 218.5, 580.0, 240.0, pv.get("condicoes") or "", fontsize=6.5)

    # Jogadas de Salvamento
    salv = ficha["jogadas_salvamento"]
    configs_salv = (
        ("fortitude", 235.0, 267.5, 223.2, 251.3),
        ("reflexos", 315.5, 348.0, 303.5, 331.2),
        ("vontade", 395.0, 427.5, 383.0, 410.2),
    )
    for sid, xt0, xt1, xcol, xteml in configs_salv:
        sv = salv[sid]
        _pdf_inserir_linha(page, pymupdf, xt0, 227.5, xt1, 244.5, formatar_bonus(sv["total"]), fontsize=11.5, align=1, bold=True)
        _pdf_inserir_linha(page, pymupdf, xcol, 254.5, xcol + 22.8, 270.5, formatar_bonus(sv["mod_atributo"]), fontsize=8.5, align=1)
        _pdf_inserir_linha(page, pymupdf, xcol + 31.0, 254.5, xcol + 53.8, 270.5, formatar_bonus(sv["proficiencia"]), fontsize=8.5, align=1)
        _pdf_marcar_teml(page, pymupdf, sv.get("grau_proficiencia"), (xteml, xteml + 7.9, xteml + 15.9, xteml + 23.9), 282.8)
        if sv.get("item"):
            _pdf_inserir_linha(page, pymupdf, xcol, 279.0, xcol + 22.8, 295.0, formatar_bonus(sv["item"]), fontsize=8.5, align=1)
    _pdf_inserir_linha(page, pymupdf, 223.0, 306.5, 436.0, 316.5, salv.get("anotacoes") or "", fontsize=6.5)

    # Percepção
    perc = ficha["percepcao"]
    _pdf_inserir_linha(page, pymupdf, 456.0, 246.5, 486.5, 276.5, formatar_bonus(perc["total"]), fontsize=12.5, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 483.0, 272.5, 503.0, 288.5, formatar_bonus(perc["mod_sab"]), fontsize=8.5, align=1)
    _pdf_inserir_linha(page, pymupdf, 506.0, 272.5, 525.5, 288.5, formatar_bonus(perc["proficiencia"]), fontsize=8.5, align=1)
    _pdf_marcar_teml(page, pymupdf, perc.get("grau_proficiencia"), (528.5, 536.4, 544.5, 552.4), 274.4)
    if perc.get("item"):
        _pdf_inserir_linha(page, pymupdf, 562.2, 272.5, 581.0, 288.5, formatar_bonus(perc["item"]), fontsize=8.5, align=1)
    _pdf_inserir_bloco(page, pymupdf, 475.0, 300.5, 580.0, 317.8, ", ".join(perc.get("sentidos") or []), fontsize=6.5)

    # CD de Classe & Velocidade
    cd = ficha["cd_classe"]
    _pdf_inserir_linha(page, pymupdf, 20.5, 299.5, 54.0, 321.0, str(cd["total"]), fontsize=12.0, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 86.2, 306.0, 108.8, 320.0, formatar_bonus(cd["mod_atributo_chave"]), fontsize=8.5, align=1)
    _pdf_inserir_linha(page, pymupdf, 112.0, 306.0, 134.5, 320.0, formatar_bonus(cd["proficiencia"]), fontsize=8.5, align=1)
    _pdf_marcar_teml(page, pymupdf, cd.get("grau_proficiencia"), (137.4, 145.4, 153.6, 161.7), 307.8)
    if cd.get("item"):
        _pdf_inserir_linha(page, pymupdf, 171.5, 306.0, 194.0, 320.0, formatar_bonus(cd["item"]), fontsize=8.5, align=1)

    vel = ficha["velocidade"]
    _pdf_inserir_linha(page, pymupdf, 76.0, 327.5, 118.8, 345.0, formatar_metros(vel["metros"]), fontsize=11.0, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 156.0, 334.0, 310.5, 347.0, vel.get("tipos_movimento_anotacoes") or "", fontsize=6.5)

    # Golpes Corpo a Corpo & À Distância
    for g, y_b in zip(ficha["golpes_corpo_a_corpo"], (366.1, 423.8, 482.1)):
        _pdf_preencher_golpe(page, pymupdf, g, y_b, distancia=False)
    for g, y_b in zip(ficha["golpes_a_distancia"], (555.5, 612.2, 668.9)):
        _pdf_preencher_golpe(page, pymupdf, g, y_b, distancia=True)

    # Proficiência com Armas
    profs_armas = ficha["proficiencia_armas"]
    specs_armas = (
        (0, (21.0, 29.0, 37.1, 45.1), 756.4, None),
        (1, (59.3, 67.3, 75.5, 83.4), 756.5, None),
        (2, (99.7, 107.7, 115.8, 123.8), 756.3, (134.5, 745.5, 200.5, 762.0)),
        (3, (208.7, 216.7, 224.8, 232.8), 756.3, (243.5, 745.5, 309.0, 762.0)),
    )
    for idx, xs, y_t, caixa_txt in specs_armas:
        if idx < len(profs_armas):
            pa = profs_armas[idx]
            _pdf_marcar_teml(page, pymupdf, pa.get("grau_proficiencia"), xs, y_t, h=6.3)
            if caixa_txt and pa.get("rotulo") and pa["rotulo"] != "OUTRA":
                _pdf_inserir_linha(page, pymupdf, caixa_txt[0], caixa_txt[1], caixa_txt[2], caixa_txt[3], pa["rotulo"], fontsize=6.5, min_fontsize=3.8)

    # Perícias (18 linhas visuais oficiais)
    for per, y_row in zip(ficha["pericias"], _PDF_PERICIAS_YS):
        if per["id"] in ("saber_1", "saber_2") and per.get("especializacao"):
            _pdf_inserir_linha(page, pymupdf, 319.0, y_row + 1.0, 376.0, y_row + 16.0, per["especializacao"], fontsize=6.5, align=2, min_fontsize=4.2)
        _pdf_inserir_linha(page, pymupdf, 406.0, y_row + 0.5, 435.5, y_row + 16.2, formatar_bonus(per["total"]), fontsize=10.0, align=1, bold=True)
        _pdf_inserir_linha(page, pymupdf, 443.5, y_row + 2.0, 467.2, y_row + 16.2, formatar_bonus(per["mod_atributo"]), fontsize=8.0, align=1)
        _pdf_inserir_linha(page, pymupdf, 470.2, y_row + 2.0, 494.0, y_row + 16.2, formatar_bonus(per["proficiencia"]), fontsize=8.0, align=1)
        _pdf_marcar_teml(page, pymupdf, per.get("grau_proficiencia"), (496.7, 504.6, 512.7, 520.7), y_row + 5.5)
        if per.get("item"):
            _pdf_inserir_linha(page, pymupdf, 530.2, y_row + 2.0, 554.0, y_row + 16.2, formatar_bonus(per["item"]), fontsize=8.0, align=1)
        if per.get("penalidade_armadura"):
            _pdf_inserir_linha(page, pymupdf, 567.0, y_row + 2.0, 581.0, y_row + 16.2, str(abs(int(per["penalidade_armadura"]))), fontsize=8.0, align=1)

    # Idiomas
    _pdf_inserir_linha(page, pymupdf, 320.0, 748.5, 582.5, 763.5, ", ".join(ficha.get("idiomas") or []), fontsize=8.0)


def _pdf_preencher_talentos_grupo(
    page: Any,
    pymupdf: Any,
    slots: list[dict[str, Any]],
    ys: tuple[float, ...],
    x0: float,
    x1: float,
) -> None:
    for slot, y0 in zip(slots, ys):
        nome = (slot.get("nome") or "").strip()
        if not nome or nome == "—":
            continue
        origem = (slot.get("origem_regra") or "").strip()
        resumo = (slot.get("resumo") or "").strip()
        texto = f"{nome}: {resumo}" if resumo else (f"{nome} ({origem})" if origem else nome)
        _pdf_inserir_bloco(page, pymupdf, x0, y0 + 0.6, x1, y0 + 15.0, texto, fontsize=6.0, bold=False, min_fontsize=4.3)


def _pdf_preencher_lista_inventario(
    page: Any,
    pymupdf: Any,
    itens: list[dict[str, Any]],
    x0: float,
    x1: float,
    x_vol0: float,
    x_vol1: float,
    y_start: float,
    y_end: float,
    *,
    x_inv: tuple[float, float] | None = None,
) -> None:
    if not itens:
        return
    altura_disp = y_end - y_start
    step = min(18.0, max(7.5, altura_disp / max(1, len(itens))))
    max_rows = max(1, int(altura_disp // step))
    for i, item in enumerate(itens[:max_rows]):
        ry0 = y_start + i * step
        ry1 = ry0 + step
        item_txt = _formatar_item_inventario(item)
        if step >= 14.0:
            _pdf_inserir_bloco(page, pymupdf, x0, ry0 + 0.5, x1, ry1 - 0.5, item_txt, fontsize=6.6, min_fontsize=4.4)
        else:
            _pdf_inserir_linha(page, pymupdf, x0, ry0, x1, ry1, item_txt, fontsize=6.8, min_fontsize=4.3)
        if x_inv and item.get("investido"):
            _pdf_inserir_linha(page, pymupdf, x_inv[0], ry0, x_inv[1], ry0 + min(step, 11.5), "X", fontsize=7.0, align=1, bold=True)
        _pdf_inserir_linha(page, pymupdf, x_vol0, ry0, x_vol1, ry0 + min(step, 11.5), str(item.get("volume", "-")), fontsize=7.0, align=1, min_fontsize=4.5)


def _pdf_preencher_pagina_2(page: Any, pymupdf: Any, resultado: dict[str, Any]) -> None:
    """Preenche Habilidades, Talentos e Inventário na Página 2 (p. 581)."""
    ficha = resultado["ficha"]
    hab = ficha["habilidades_e_talentos"]
    _pdf_preencher_talentos_grupo(page, pymupdf, hab["ancestralidade"], _PDF_TALENTOS_ANCESTRALIDADE_YS, 24.0, 234.0)
    _pdf_preencher_talentos_grupo(page, pymupdf, hab["pericia"], _PDF_TALENTOS_PERICIA_YS, 24.0, 240.0)
    _pdf_preencher_talentos_grupo(page, pymupdf, hab["gerais"], _PDF_TALENTOS_GERAIS_YS, 24.0, 270.0)
    _pdf_preencher_talentos_grupo(page, pymupdf, hab["classe"], _PDF_TALENTOS_CLASSE_YS, 308.0, 493.0)
    _pdf_preencher_talentos_grupo(page, pymupdf, hab["bonus"], _PDF_TALENTOS_BONUS_YS, 308.0, 578.0)

    inv = ficha["inventario"]
    _pdf_preencher_lista_inventario(
        page, pymupdf, inv["itens_vestidos"], 23.0, 238.5, 267.0, 288.5, 565.0, 758.0, x_inv=(242.0, 264.0),
    )
    _pdf_preencher_lista_inventario(
        page, pymupdf, inv["itens_preparados"], 308.0, 418.0, 421.0, 441.5, 562.0, 696.0,
    )
    _pdf_preencher_lista_inventario(
        page, pymupdf, inv["outros_itens"], 447.0, 557.0, 560.0, 580.5, 562.0, 696.0,
    )

    _pdf_inserir_linha(page, pymupdf, 315.5, 728.0, 343.0, 756.0, str(inv["volume_total"]), fontsize=10.5, align=1, bold=True)
    mod_for = ficha["atributos"]["for"]["modificador"]
    _pdf_inserir_linha(page, pymupdf, 361.0, 712.5, 387.0, 731.0, str(inv["volume_sobrecarregado"]), fontsize=9.5, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 413.2, 717.0, 435.2, 730.8, formatar_bonus(mod_for), fontsize=8.0, align=1)
    _pdf_inserir_linha(page, pymupdf, 361.0, 741.5, 387.0, 760.0, str(inv["volume_maximo"]), fontsize=9.5, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 413.2, 746.5, 435.2, 760.2, formatar_bonus(mod_for), fontsize=8.0, align=1)

    riq = inv["riqueza"]
    _pdf_inserir_linha(page, pymupdf, 444.0, 712.0, 476.0, 739.0, str(riq["pc"]), fontsize=10.0, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 479.0, 712.0, 511.0, 739.0, str(riq["pp"]), fontsize=10.0, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 514.0, 712.0, 546.0, 739.0, str(riq["po"]), fontsize=10.0, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 550.0, 712.0, 582.0, 739.0, str(riq["pl"]), fontsize=10.0, align=1, bold=True)


def _pdf_preencher_pagina_3(page: Any, pymupdf: Any, resultado: dict[str, Any]) -> None:
    """Preenche Perfil, Campanha, Divindade, Companheiro e Ações na Página 3 (p. 582)."""
    ficha = resultado["ficha"]
    meta = resultado.get("meta_geracao") or {}
    perfil = ficha["perfil_e_campanha"]
    bio_d = perfil["dados_biograficos"]
    pers = perfil["personalidade"]
    camp = perfil["anotacoes_campanha"]

    _pdf_inserir_linha(page, pymupdf, 231.0, 31.5, 287.5, 44.0, bio_d.get("etnia") or "", fontsize=7.0, align=1)
    _pdf_inserir_linha(page, pymupdf, 291.0, 31.5, 348.0, 44.0, bio_d.get("nacionalidade") or "", fontsize=7.0, align=1)
    _pdf_inserir_linha(page, pymupdf, 351.5, 31.5, 421.0, 44.0, bio_d.get("local_nascimento") or "", fontsize=7.0, align=1)
    _pdf_inserir_linha(page, pymupdf, 424.5, 31.5, 450.0, 44.0, bio_d.get("idade") or "", fontsize=7.0, align=1)
    _pdf_inserir_linha(page, pymupdf, 453.0, 31.5, 523.0, 44.0, bio_d.get("genero_pronomes") or "", fontsize=7.0, align=1)
    _pdf_inserir_linha(page, pymupdf, 526.5, 31.5, 551.5, 44.0, bio_d.get("altura") or "", fontsize=7.0, align=1)
    _pdf_inserir_linha(page, pymupdf, 555.0, 31.5, 580.0, 44.0, bio_d.get("peso") or "", fontsize=7.0, align=1)
    _pdf_inserir_bloco(page, pymupdf, 231.0, 56.8, 579.5, 73.5, bio_d.get("aparencia") or "", fontsize=6.8)

    # Resumo técnico no quadro de Rascunho do Personagem
    notas_rascunho = []
    if meta.get("conceito_titulo"):
        notas_rascunho.append(f"Conceito: {meta['conceito_titulo']}")
    if meta.get("subclasse_oficial_nome"):
        notas_rascunho.append(f"Subclasse: {meta['subclasse_oficial_nome']}")
    div_det = meta.get("divindade_detalhes")
    if div_det:
        notas_rascunho.append(
            f"Divindade: {div_det['nome']} ({div_det['tendencia']}) | Arma: {div_det['arma_favorecida_nome']} | "
            f"Éditos: {div_det['editos']}"
        )
    comp = meta.get("companheiro_ou_familiar")
    if comp:
        if comp["categoria"] == "Companheiro Animal":
            atks = "; ".join(f"{a['nome']} {formatar_bonus(a['ataque_total'])} ({a['dano']})" for a in comp["ataques"])
            notas_rascunho.append(
                f"Companheiro Animal: {comp['nome']} ({comp['estagio']}, {comp['tamanho']}) | "
                f"PV {comp['pv_max']} | CA {comp['ca']} | {comp['velocidades']} | {atks}"
            )
        else:
            habs = ", ".join(h["nome"] for h in comp["habilidades_selecionadas"])
            notas_rascunho.append(
                f"Familiar: {comp['nome']} ({comp['tamanho']}) | PV {comp['pv_max']} | CA {comp['ca']} | "
                f"Perc/Acrob/Furt {formatar_bonus(comp['percepcao'])} | Habs: {habs}"
            )
    _pdf_inserir_bloco(page, pymupdf, 25.0, 39.0, 219.0, 226.0, "\n\n".join(notas_rascunho), fontsize=7.0, min_fontsize=5.0)

    _pdf_inserir_bloco(page, pymupdf, 231.0, 98.5, 579.5, 113.5, pers.get("atitude") or "", fontsize=6.8)
    _pdf_inserir_bloco(page, pymupdf, 231.0, 126.0, 579.5, 147.0, pers.get("crencas") or "", fontsize=6.8)
    _pdf_inserir_bloco(page, pymupdf, 231.0, 160.5, 407.0, 187.5, pers.get("gostos") or "", fontsize=6.8)
    _pdf_inserir_bloco(page, pymupdf, 414.0, 160.5, 579.5, 187.5, pers.get("aversoes") or "", fontsize=6.8)
    _pdf_inserir_bloco(page, pymupdf, 231.0, 201.0, 579.5, 229.5, pers.get("bordoes") or "", fontsize=6.8)

    _pdf_inserir_bloco(page, pymupdf, 23.0, 264.0, 297.0, 393.0, camp.get("anotacoes") or "", fontsize=7.2)
    _pdf_inserir_bloco(page, pymupdf, 307.5, 264.0, 579.5, 297.0, camp.get("aliados") or "", fontsize=6.8)
    _pdf_inserir_bloco(page, pymupdf, 307.5, 312.5, 579.5, 345.0, camp.get("inimigos") or "", fontsize=6.8)
    _pdf_inserir_bloco(page, pymupdf, 307.5, 361.0, 579.5, 393.5, camp.get("organizacoes") or "", fontsize=6.8)

    # Ações e Atividades (6 slots: 2 colunas x 3 linhas)
    pos_acoes = (
        (21.7, 419.3), (305.4, 419.3),
        (21.7, 478.7), (305.4, 478.7),
        (21.7, 538.0), (305.4, 538.0),
    )
    for slot, (cx, cy) in zip(ficha["acoes_e_atividades"], pos_acoes):
        if not slot.get("nome"):
            continue
        _pdf_inserir_linha(page, pymupdf, cx + 2.0, cy + 8.0, cx + 97.5, cy + 22.0, slot["nome"], fontsize=7.8, bold=True)
        _pdf_inserir_linha(page, pymupdf, cx + 99.5, cy + 6.5, cx + 134.8, cy + 22.0, _pdf_acao_curta(slot.get("acoes")), fontsize=7.5, align=1, bold=True)
        _pdf_inserir_linha(page, pymupdf, cx + 137.0, cy + 8.0, cx + 239.0, cy + 22.0, ", ".join(slot.get("tracos") or []), fontsize=6.8)
        if slot.get("pagina") is not None:
            _pdf_inserir_linha(page, pymupdf, cx + 243.0, cy + 8.0, cx + 275.5, cy + 22.0, str(slot["pagina"]), fontsize=7.0, align=1)
        _pdf_inserir_bloco(page, pymupdf, cx + 2.0, cy + 32.5, cx + 275.5, cy + 55.2, slot.get("descricao") or "", fontsize=6.4, min_fontsize=4.2)

    # Ações Livres e Reações (4 slots: 2 colunas x 2 linhas)
    pos_reacoes = (
        (21.7, 618.3), (305.4, 618.3),
        (21.7, 691.2), (305.4, 691.2),
    )
    for slot, (cx, cy) in zip(ficha["acoes_livres_e_reacoes"], pos_reacoes):
        if not slot.get("nome"):
            continue
        tipo_norm = (slot.get("tipo") or "").strip().lower()
        eh_livre = "livre" in tipo_norm
        _pdf_inserir_linha(page, pymupdf, cx + 2.0, cy + 8.0, cx + 94.0, cy + 20.8, slot["nome"], fontsize=7.5, bold=True)
        _pdf_marcar_checkbox(page, pymupdf, cx + 96.0, cy + 3.2, cx + 101.4, cy + 8.6, eh_livre)
        _pdf_marcar_checkbox(page, pymupdf, cx + 96.0, cy + 12.5, cx + 101.4, cy + 17.9, not eh_livre)
        _pdf_inserir_linha(page, pymupdf, cx + 137.0, cy + 8.0, cx + 239.0, cy + 20.8, ", ".join(slot.get("tracos") or []), fontsize=6.8)
        if slot.get("pagina") is not None:
            _pdf_inserir_linha(page, pymupdf, cx + 243.0, cy + 8.0, cx + 275.5, cy + 20.8, str(slot["pagina"]), fontsize=7.0, align=1)
        if slot.get("acionamento"):
            _pdf_inserir_linha(page, pymupdf, cx + 40.5, cy + 24.5, cx + 275.5, cy + 33.8, slot["acionamento"], fontsize=6.4, min_fontsize=4.2)
        _pdf_inserir_bloco(page, pymupdf, cx + 2.0, cy + 43.2, cx + 275.5, cy + 68.5, slot.get("descricao") or "", fontsize=6.2, min_fontsize=4.2)


def _pdf_preencher_slot_magia(
    page: Any,
    pymupdf: Any,
    slot: dict[str, Any],
    x0: float,
    y_top: float,
    *,
    x_prep: float | None,
    x_acoes: float,
    x_comp_base: float,
    mostrar_freq: bool = False,
) -> None:
    """Preenche um card de Truque, Magia Inata ou Magia de Círculo na Página 4."""
    nome = (slot.get("nome") or "").strip()
    if not nome:
        return
    fim_nome = (x_prep - 2.0) if x_prep is not None else (x_acoes - 2.0)
    _pdf_inserir_linha(page, pymupdf, x0 + 2.0, y_top + 1.0, fim_nome, y_top + 13.4, nome, fontsize=7.5, bold=True)

    if x_prep is not None and slot.get("preparada"):
        _pdf_marcar_checkbox(page, pymupdf, x_prep + 1.0, y_top + 6.4, x_prep + 12.8, y_top + 13.8, True)
    if mostrar_freq and slot.get("frequencia"):
        freq_txt = str(slot["frequencia"]).split("(")[0].strip()
        _pdf_inserir_linha(page, pymupdf, x_acoes + 0.5, y_top + 6.2, x_acoes + 27.5, y_top + 13.8, freq_txt, fontsize=5.2, align=1, min_fontsize=3.6)

    _pdf_inserir_linha(
        page, pymupdf, x_acoes + 0.5, y_top + 20.8, x_acoes + 27.5, y_top + 31.4,
        _pdf_acao_curta(slot.get("acoes")), fontsize=6.8, align=1, bold=True,
    )

    comps = {c.strip().upper() for c in (slot.get("componentes") or [])}
    desloc_comp = (
        ("M", -0.5, 5.5),
        ("S", 9.8, 14.2),
        ("V", 18.8, 23.4),
    )
    for letra, dx0, dx1 in desloc_comp:
        if letra in comps:
            cy = y_top + 31.8
            page.draw_rect(pymupdf.Rect(x_comp_base + dx0, cy, x_comp_base + dx1, cy + 6.7), color=_PDF_COR_DESTAQUE, width=0.75)

    _pdf_inserir_bloco(page, pymupdf, x0 + 2.0, y_top + 14.5, x_acoes - 2.5, y_top + 37.8, slot.get("anotacoes") or "", fontsize=6.0, min_fontsize=4.0)


def _pdf_preencher_pagina_4(page: Any, pymupdf: Any, resultado: dict[str, Any]) -> None:
    """Preenche Conjuração e Magias na Página 4 (p. 583)."""
    conj = resultado["ficha"]["conjuracao"]
    if not _tem_conjuracao(conj):
        return

    am = conj["ataque_magia"]
    _pdf_inserir_linha(page, pymupdf, 50.0, 35.5, 76.5, 54.2, formatar_bonus(am["total"]), fontsize=11.0, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 86.2, 40.5, 109.0, 54.5, formatar_bonus(am["mod_atributo_chave"]), fontsize=8.5, align=1)
    _pdf_inserir_linha(page, pymupdf, 115.2, 40.5, 138.0, 54.5, formatar_bonus(am["proficiencia"]), fontsize=8.5, align=1)
    _pdf_marcar_teml(page, pymupdf, am.get("grau_proficiencia"), (140.9, 148.9, 157.1, 165.2), 42.3)

    cm = conj["cd_magia"]
    _pdf_inserir_linha(page, pymupdf, 39.5, 74.5, 66.0, 93.2, str(cm["total"]), fontsize=11.0, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 96.0, 79.5, 118.8, 93.5, formatar_bonus(cm["mod_atributo_chave"]), fontsize=8.5, align=1)
    _pdf_inserir_linha(page, pymupdf, 125.0, 79.5, 147.8, 93.5, formatar_bonus(cm["proficiencia"]), fontsize=8.5, align=1)
    _pdf_marcar_teml(page, pymupdf, cm.get("grau_proficiencia"), (151.7, 159.7, 167.9, 176.0), 81.3)

    trads = conj["tradicoes_marcadas"]
    caixas_trad = {
        "arcana": (23.0, 125.0, 64.0, 139.0),
        "ocultista": (154.0, 125.0, 202.0, 139.0),
        "primal": (26.0, 152.0, 64.0, 166.0),
        "divina": (154.0, 152.0, 192.0, 166.0),
    }
    for tid, rect_t in caixas_trad.items():
        if trads.get(tid):
            page.draw_rect(pymupdf.Rect(*rect_t), color=_PDF_COR_DESTAQUE, width=1.4)

    est = conj["estilo_conjuracao"]
    _pdf_marcar_checkbox(page, pymupdf, 52.8, 182.9, 65.0, 194.3, bool(est.get("preparada")))
    _pdf_marcar_checkbox(page, pymupdf, 108.4, 182.9, 120.7, 194.3, bool(est.get("espontanea")))

    _pdf_inserir_linha(page, pymupdf, 216.0, 60.5, 245.0, 79.2, str(conj["nivel_truque"]), fontsize=10.5, align=1, bold=True)

    cols_espacos_x0 = (249.2, 282.6, 316.0, 349.5, 382.9, 416.3, 449.8, 483.2, 516.6, 550.1)
    for idx, x0_col in enumerate(cols_espacos_x0, start=1):
        por_dia = conj["espacos_magia_por_dia"].get(str(idx), 0)
        reman = conj["espacos_magia_espontanea_remanescentes"].get(str(idx), 0)
        if por_dia:
            _pdf_inserir_linha(page, pymupdf, x0_col, 36.0, x0_col + 29.0, 54.5, str(por_dia), fontsize=10.0, align=1, bold=True)
        if reman:
            _pdf_inserir_linha(page, pymupdf, x0_col, 65.2, x0_col + 29.0, 82.2, str(reman), fontsize=9.5, align=1)

    for slot, y_t in zip(conj["truques_magicos"], _PDF_TRUQUES_YS):
        _pdf_preencher_slot_magia(
            page, pymupdf, slot, 20.6, y_t, x_prep=187.5, x_acoes=172.7, x_comp_base=177.3,
        )

    for slot, y_t in zip(conj["magias_inatas"], (532.2, 573.2)):
        _pdf_preencher_slot_magia(
            page, pymupdf, slot, 20.7, y_t, x_prep=None, x_acoes=172.7, x_comp_base=177.3, mostrar_freq=True,
        )

    pf = conj["magias_foco"]["pontos_foco"]
    _pdf_inserir_linha(page, pymupdf, 88.0, 637.8, 132.5, 651.0, str(pf.get("atuais", 0)), fontsize=9.5, align=1, bold=True)
    _pdf_inserir_linha(page, pymupdf, 135.5, 637.8, 180.5, 651.0, str(pf.get("maximo", 0)), fontsize=9.5, align=1, bold=True)
    for slot, y_f in zip(conj["magias_foco"]["slots"], (653.3, 680.7, 708.1, 735.6)):
        if not slot.get("nome"):
            continue
        comps = ",".join(slot.get("componentes") or [])
        detalhe = f"{slot['nome']} ({_pdf_acao_curta(slot.get('acoes'))}; {comps})"
        if slot.get("anotacoes"):
            detalhe = f"{detalhe} — {slot['anotacoes']}"
        _pdf_inserir_bloco(page, pymupdf, 22.0, y_f + 1.0, 171.5, y_f + 23.8, detalhe, fontsize=6.4, min_fontsize=4.2)
        _pdf_inserir_linha(page, pymupdf, 173.0, y_f + 6.8, 200.0, y_f + 17.5, _pdf_acao_curta(slot.get("acoes")), fontsize=6.5, align=1, bold=True)

    # Magias (32 slots = 16 na coluna 1 + 16 na coluna 2)
    for idx, slot in enumerate(conj["magias"][:32]):
        y_m = _PDF_MAGIAS_YS[idx % 16]
        if idx < 16:
            _pdf_preencher_slot_magia(page, pymupdf, slot, 214.8, y_m, x_prep=381.6, x_acoes=366.9, x_comp_base=371.4)
        else:
            _pdf_preencher_slot_magia(page, pymupdf, slot, 399.5, y_m, x_prep=566.4, x_acoes=551.6, x_comp_base=556.2)


def exportar_ficha_pdf(resultado: dict[str, Any]) -> bytes:
    """Exporta a ficha completa em bytes `.pdf` idênticos à ficha oficial do livro (4 páginas)."""
    if not _TEMPLATE_PDF_OFICIAL.exists():
        raise FileNotFoundError(
            f"Template PDF oficial não encontrado em {_TEMPLATE_PDF_OFICIAL}"
        )

    import pymupdf

    doc = pymupdf.open(str(_TEMPLATE_PDF_OFICIAL))
    try:
        if len(doc) < 4:
            raise ValueError("Template PDF oficial deve possuir 4 páginas.")
        _pdf_preencher_pagina_1(doc[0], pymupdf, resultado)
        _pdf_preencher_pagina_2(doc[1], pymupdf, resultado)
        _pdf_preencher_pagina_3(doc[2], pymupdf, resultado)
        _pdf_preencher_pagina_4(doc[3], pymupdf, resultado)
        return doc.tobytes(deflate=True)
    finally:
        doc.close()
