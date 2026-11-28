"""Exportador da ficha de personagem Castles & Crusades em `.docx` (OOXML ECMA-376)."""

from __future__ import annotations

import io
import re
import zipfile
from typing import Any
from xml.sax.saxutils import escape

from motor_cc.atributos import ORDEM_ATRIBUTOS
from motor_cc.exportacao.comum import fmt_mod, fmt_movimento

_RE_XML_INVALIDO = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _limpar_xml(texto: Any) -> str:
    bruto = "" if texto is None else str(texto)
    return escape(_RE_XML_INVALIDO.sub("", bruto))


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
        <w:color w:val="1F242B"/>
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
    <w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="1C3D5A"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="SubtituloFicha">
    <w:name w:val="SubtituloFicha"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:spacing w:before="0" w:after="100"/></w:pPr>
    <w:rPr><w:i/><w:sz w:val="20"/><w:color w:val="4B5563"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="SecaoTitulo">
    <w:name w:val="SecaoTitulo"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="180" w:after="60"/>
      <w:pBdr><w:bottom w:val="single" w:sz="10" w:space="3" w:color="1C3D5A"/></w:pBdr>
    </w:pPr>
    <w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="1C3D5A"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="SubsecaoTitulo">
    <w:name w:val="SubsecaoTitulo"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="120" w:after="40"/>
    </w:pPr>
    <w:rPr><w:b/><w:sz w:val="21"/><w:color w:val="374151"/></w:rPr>
  </w:style>
</w:styles>
"""


def _xml_p(
    texto: str,
    estilo: str | None = None,
    negrito: bool = False,
    cor: str | None = None,
    tam_half_pt: int | None = None,
) -> str:
    ppr = f'<w:pPr><w:pStyle w:val="{estilo}"/></w:pPr>' if estilo else ""
    rpr_parts = []
    if negrito:
        rpr_parts.append("<w:b/>")
    if cor:
        rpr_parts.append(f'<w:color w:val="{cor}"/>')
    if tam_half_pt:
        rpr_parts.append(f'<w:sz w:val="{tam_half_pt}"/><w:szCs w:val="{tam_half_pt}"/>')
    rpr = f"<w:rPr>{''.join(rpr_parts)}</w:rPr>" if rpr_parts else ""
    return f'<w:p>{ppr}<w:r>{rpr}<w:t xml:space="preserve">{_limpar_xml(texto)}</w:t></w:r></w:p>'


def _xml_tabela(cabecalhos: list[str], linhas: list[list[Any]], larguras: list[int]) -> str:
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in larguras)
    tbl_pr = (
        "<w:tblPr>"
        f'<w:tblW w:w="{sum(larguras)}" w:type="dxa"/>'
        "<w:tblBorders>"
        '<w:top w:val="single" w:sz="6" w:space="0" w:color="B8C4D0"/>'
        '<w:left w:val="single" w:sz="6" w:space="0" w:color="B8C4D0"/>'
        '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="B8C4D0"/>'
        '<w:right w:val="single" w:sz="6" w:space="0" w:color="B8C4D0"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="DCE3EA"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="DCE3EA"/>'
        "</w:tblBorders>"
        "<w:tblCellMar>"
        '<w:top w:w="60" w:type="dxa"/><w:left w:w="90" w:type="dxa"/>'
        '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="90" w:type="dxa"/>'
        "</w:tblCellMar>"
        "</w:tblPr>"
    )

    def _celula(texto: Any, largura: int, fundo: str | None = None, eh_header: bool = False) -> str:
        shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{fundo}"/>' if fundo else ""
        tcpr = f'<w:tcPr><w:tcW w:w="{largura}" w:type="dxa"/>{shd}</w:tcPr>'
        valor_str = "" if texto is None else str(texto)
        if eh_header:
            par = _xml_p(valor_str, negrito=True, cor="1C3D5A", tam_half_pt=18)
        else:
            par = _xml_p(valor_str, tam_half_pt=18)
        return f"<w:tc>{tcpr}{par}</w:tc>"

    trs = []
    hdr_cells = "".join(_celula(h, larguras[i], fundo="EDF2F7", eh_header=True) for i, h in enumerate(cabecalhos))
    trs.append(f"<w:tr><w:trPr><w:tblHeader/></w:trPr>{hdr_cells}</w:tr>")

    for idx_row, linha in enumerate(linhas):
        fundo_row = "F8FAFC" if idx_row % 2 == 1 else None
        cells = "".join(_celula(linha[i], larguras[i], fundo=fundo_row) for i in range(len(cabecalhos)))
        trs.append(f"<w:tr>{cells}</w:tr>")

    return f"<w:tbl>{tbl_pr}<w:tblGrid>{grid}</w:tblGrid>{''.join(trs)}</w:tbl>"


def _montar_document_xml(ficha: dict[str, Any]) -> str:
    cab = ficha["cabecalho"]
    attrs = ficha["atributos"]["atributos"]
    comb = ficha["combate"]
    ca = comb["ca"]
    pv = comb["pv"]
    habs = ficha["habilidades"]
    eq = ficha["equipamentos"]
    magias = ficha["magias"]
    notas = ficha.get("notas", {})
    avisos = ficha.get("avisos", [])

    partes: list[str] = []

    raca_txt = cab["raca_nome"]
    if cab.get("linhagem_meio_elfo"):
        raca_txt += f" ({cab['linhagem_meio_elfo'].capitalize()})"

    partes.append(_xml_p(cab["nome"], estilo="TituloPrincipal"))
    partes.append(
        _xml_p(
            f"Castles & Crusades (1ª Ed. Brasileira) • Nível {cab['nivel']} • {raca_txt} • {cab['classe_nome']}",
            estilo="SubtituloFicha",
        )
    )
    partes.append(_xml_p(f"Método de Atributos: {cab['rotulo_metodo']}", negrito=True, cor="1C3D5A"))

    prox = cab["prox_exp"] if cab.get("prox_exp") is not None else "Máx."
    info_geral = [
        ["Método de Atributos", cab["rotulo_metodo"], "Títulos", cab.get("titulos") or "—"],
        ["Disposição", cab["disposicao_nome"], "Idiomas", ", ".join(cab.get("idiomas", [])) or "Comum"],
        ["Movimento", fmt_movimento(cab["movimento_m"]), "Exp / Próx", f"{cab['exp']} / {prox}"],
        ["Jogador", cab.get("jogador") or "—", "BpA", fmt_mod(comb["bpa"])],
    ]
    partes.append(_xml_tabela(["Campo", "Valor", "Campo", "Valor"], info_geral, [1900, 3333, 1900, 3333]))

    # Atributos & SIEGE
    partes.append(_xml_p("Atributos e Sistema SIEGE", estilo="SecaoTitulo"))
    linhas_attr = []
    for key in ORDEM_ATRIBUTOS:
        a = attrs[key]
        tipo_siege = "Primário (CB 12)" if a["primario"] else "Secundário (CB 18)"
        if a.get("bonus_extra_teste"):
            tipo_siege += f" (+{a['bonus_extra_teste']} teste)"
        linhas_attr.append(
            [
                f"{a['sigla']} — {a['nome']}",
                a["valor"],
                fmt_mod(a["modificador"]),
                tipo_siege,
                ", ".join(a.get("jogadas_protecao", [])),
            ]
        )
    partes.append(
        _xml_tabela(
            ["Atributo", "Valor", "Mod", "SIEGE", "Jogadas de Proteção"],
            linhas_attr,
            [2200, 800, 800, 2366, 4300],
        )
    )

    # Combate
    partes.append(_xml_p("Combate, Defesa e Pontos de Vida", estilo="SecaoTitulo"))
    pv_detalhe = ", ".join(f"{p['nivel']}º: {p['pv']}" for p in pv.get("por_nivel", []))
    comb_rows = [
        [
            "Classe de Armadura (CA)",
            f"{ca['total']}  (= 10 + Armadura {ca['armadura']} + Escudo {ca['escudo']} + DES {fmt_mod(ca['mod_destreza'])} + Magia {ca['magia']} + Var {ca['var']})",
        ],
        [
            "Proteções Equipadas",
            f"Armadura: {ca['armadura_nome']} | Escudo: {ca['escudo_nome']} | Elmo: {ca['elmo_nome']}",
        ],
        ["Pontos de Vida (PV)", f"{pv['total']} ({pv['dado_vida']}) — [{pv_detalhe}]"],
        ["Ferimentos e Condições", comb.get("ferimentos_e_condicoes") or "—"],
    ]
    partes.append(_xml_tabela(["Estatística", "Detalhamento"], comb_rows, [2600, 7866]))

    if comb.get("ataques"):
        partes.append(_xml_p("Armas e Ataques", estilo="SubsecaoTitulo"))
        armas_rows = [
            [
                atq["nome"],
                fmt_mod(atq["total_ataque"]),
                f"BpA {atq['bpa']} + Mod {fmt_mod(atq['mod_ataque'])}",
                atq["total_dano"],
                atq["alcance"],
            ]
            for atq in comb["ataques"]
        ]
        partes.append(_xml_tabela(["Arma", "Total", "Cálculo", "Dano", "Alcance"], armas_rows, [2800, 1000, 2666, 1800, 2200]))

    # Habilidades
    partes.append(_xml_p("Habilidades da Raça e da Classe", estilo="SecaoTitulo"))
    if habs.get("raca"):
        partes.append(_xml_p("Habilidades da Raça", estilo="SubsecaoTitulo"))
        partes.append(
            _xml_tabela(
                ["Habilidade", "Descrição"],
                [[h["nome"], h["descricao"]] for h in habs["raca"]],
                [2600, 7866],
            )
        )
    if habs.get("classe"):
        partes.append(_xml_p("Habilidades da Classe", estilo="SubsecaoTitulo"))
        partes.append(
            _xml_tabela(
                ["Nível", "Habilidade", "Resumo"],
                [[f"{h['nivel']}º", h["nome"], h["resumo"]] for h in habs["classe"]],
                [900, 2500, 7066],
            )
        )

    # Equipamentos, Sobrecarga e Moedas
    partes.append(_xml_p("Equipamentos, Sobrecarga (SB) e Moedas", estilo="SecaoTitulo"))
    sc = eq["sobrecarga"]
    moedas = eq["moedas_restantes"]
    partes.append(
        _xml_p(
            f"Sobrecarga: SB {sc['sb_total']} / CS {sc['categoria_sobrecarga_cs']} ({sc['categoria_nome']}) — {sc['efeito']} | "
            f"Moedas: {moedas['ouro']} po, {moedas['prata']} pp, {moedas['cobre']} pc"
        )
    )
    if eq.get("todos_itens_resumo"):
        itens_rows = [[it["nome"], it["categoria"], it["sb"], it["custo"]] for it in eq["todos_itens_resumo"]]
        partes.append(_xml_tabela(["Item", "Categoria", "SB", "Custo"], itens_rows, [4500, 2966, 1200, 1800]))

    if notas.get("itens_magicos") or notas.get("pocoes") or notas.get("anotacoes"):
        partes.append(_xml_p("Itens Mágicos, Poções e Anotações", estilo="SubsecaoTitulo"))
        if notas.get("itens_magicos"):
            partes.append(_xml_p("Itens Mágicos: " + ", ".join(str(x) for x in notas["itens_magicos"])))
        if notas.get("pocoes"):
            partes.append(_xml_p("Poções: " + ", ".join(str(x) for x in notas["pocoes"])))
        if notas.get("anotacoes"):
            partes.append(_xml_p("Anotações: " + notas["anotacoes"]))

    # Magias
    if magias.get("conjurador"):
        partes.append(_xml_p("Magias e Feitiços Conhecidos", estilo="SecaoTitulo"))
        partes.append(
            _xml_p(
                f"Tradição: {str(magias['tradicao']).capitalize()} | "
                f"Atributo de Conjuração: {str(magias['atributo_conjuracao']).upper()} ({magias.get('valor_atributo_conjuracao')})"
            )
        )
        espacos = magias.get("espacos_por_circulo", {})
        feiticos = magias.get("feiticos_por_circulo", {})
        mag_rows = []
        for circ in sorted(espacos.keys(), key=int):
            info = espacos[circ]
            esp_txt = f"{info['total']}/dia"
            if info["bonus_atributo"]:
                esp_txt += f" ({info['base']} + {info['bonus_atributo']} bônus)"
            nomes_f = ", ".join(f"{f['nome']}{'*' if f.get('reversivel') else ''}" for f in feiticos.get(circ, []))
            mag_rows.append([f"Nível {circ}", esp_txt, nomes_f or "(Nenhum selecionado)"])
        if mag_rows:
            partes.append(_xml_tabela(["Círculo", "Espaços/Dia", "Feitiços"], mag_rows, [1400, 2200, 6866]))

    if avisos:
        partes.append(_xml_p("Avisos", estilo="SecaoTitulo"))
        for av in avisos:
            partes.append(_xml_p(f"• {av}"))

    sect_pr = (
        "<w:sectPr>"
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="850" w:right="720" w:bottom="850" w:left="720" w:header="450" w:footer="450" w:gutter="0"/>'
        "</w:sectPr>"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(partes)}{sect_pr}</w:body>"
        "</w:document>"
    )


def exportar_ficha_cc_docx(ficha: dict[str, Any]) -> bytes:
    """Gera o arquivo `.docx` completo em memória (bytes) a partir de uma ficha C&C."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _CONTENT_TYPES_XML)
        zf.writestr("_rels/.rels", _ROOT_RELS_XML)
        zf.writestr("word/_rels/document.xml.rels", _DOC_RELS_XML)
        zf.writestr("word/styles.xml", _STYLES_XML)
        zf.writestr("word/document.xml", _montar_document_xml(ficha))
    return buf.getvalue()
