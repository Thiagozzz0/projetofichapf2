"""Exportadores oficiais da ficha de personagem PF2E em `.txt` e `.docx` (OOXML)."""

from __future__ import annotations

import io
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
    linhas.append(f"  Pontos de Vida : {pv['max']} (Atuais: {pv['atuais']})")
    if pv.get("resistencias_e_imunidades"):
        linhas.append(f"  Resistências   : {pv['resistencias_e_imunidades']}")
    linhas.append(
        f"  Classe Armad.  : {ca['total']} "
        f"(10 + DES/Lim {formatar_bonus(ca['des_ou_limite'])} + Prof {formatar_bonus(ca['proficiencia'])} "
        f"[{_formatar_grau_curto(ca['grau_proficiencia'])}] + Item {formatar_bonus(ca['item'])})"
    )
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
                qtd = f" ×{item['quantidade']}" if (item.get("quantidade") or 1) > 1 else ""
                linhas.append(f"    - {item['nome']}{qtd} (Vol: {item['volume']})")
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

    acoes_at = [a for a in ficha["acoes_e_atividades"] if a.get("nome")]
    if acoes_at:
        sub("AÇÕES E ATIVIDADES")
        for a in acoes_at:
            tr = ", ".join(a.get("tracos") or [])
            linhas.append(f"  - [{a.get('acoes', '1')} ação] {a['nome']} ({tr})")
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
    info_geral = [
        ["Biografia", f"{cab['biografia']} ({bio_modo})", "Tamanho / Tendência", f"{cab['tamanho']} / {cab['tendencia']}"],
        ["Jogador", cab.get("nome_jogador") or "—", "Pontos de Heroísmo", f"{cab['pontos_heroismo']} / 3"],
        ["Divindade", cab.get("divindade") or "—", "Seed / Saldo", f"{meta.get('seed', '—')} / {meta.get('saldo_restante', '—')}"],
    ]
    partes.append(_xml_tabela(["Campo", "Valor", "Campo", "Valor"], info_geral, [1700, 3533, 1900, 3333]))
    partes.append(_xml_p_rotulo("Traços", ", ".join(cab.get("tracos") or [])))

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
    linhas_comb = [
        ["Pontos de Vida", f"{pv['max']} PV", "Classe de Armadura", f"{ca['total']} [{_formatar_grau_curto(ca['grau_proficiencia'])}]"],
        ["Velocidade", f"{formatar_metros(vel['metros'])} m", "Percepção", f"{formatar_bonus(perc['total'])} [{_formatar_grau_curto(perc['grau_proficiencia'])}]"],
        ["CD de Classe", f"{cd['total']} [{_formatar_grau_curto(cd['grau_proficiencia'])}]", "Fortitude", f"{formatar_bonus(salv['fortitude']['total'])} [{_formatar_grau_curto(salv['fortitude']['grau_proficiencia'])}]"],
        ["Reflexos", f"{formatar_bonus(salv['reflexos']['total'])} [{_formatar_grau_curto(salv['reflexos']['grau_proficiencia'])}]", "Vontade", f"{formatar_bonus(salv['vontade']['total'])} [{_formatar_grau_curto(salv['vontade']['grau_proficiencia'])}]"],
    ]
    partes.append(_xml_tabela(["Estatística", "Valor", "Estatística", "Valor"], linhas_comb, [2300, 2933, 2300, 2933]))

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
    linhas_acoes = []
    for a in ficha["acoes_e_atividades"]:
        if a.get("nome"):
            linhas_acoes.append([f"{a.get('acoes', '1')} ação", a["nome"], ", ".join(a.get("tracos") or []) or "—", a.get("descricao", "")])
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
                    extra = "Preparada" if (mostrar_prep and m.get("preparada")) else (m.get("frequencia") or m.get("anotacoes") or "—")
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
