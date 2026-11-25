"""Exportador da ficha de personagem PF2E em `.docx` (OOXML ECMA-376)."""

from __future__ import annotations

import io
import zipfile
from typing import Any

from ..util import formatar_bonus, formatar_metros
from .comum import (
    _NOME_ATRIBUTO_SIGLA,
    _coletar_talentos_preenchidos,
    _formatar_custo_acao,
    _formatar_grau_curto,
    _formatar_linha_golpe,
    _limpar_xml,
    _tem_conjuracao,
    _tradicao_e_estilo_texto,
)


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
    leves_soltos = meta.get("volume_leves_soltos", 0)
    leves_por_vol = meta.get("itens_leves_por_volume") or (meta.get("regras_casa") or {}).get("itens_leves_por_volume") or 10
    partes.append(
        _xml_p_rotulo(
            "Carga e Moedas",
            f"Volume {inv['volume_total']} (Leves soltos: {leves_soltos}/{leves_por_vol} L | Regra: {leves_por_vol} L = 1 Vol | "
            f"Sobrecarregado > {inv['volume_sobrecarregado']} / Máximo {inv['volume_maximo']}) | "
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
        esp_map = conj.get("espacos_magia_por_dia") or {}
        esp_ativos = [
            (int(k), int(v))
            for k, v in esp_map.items()
            if str(k).isdigit() and int(v or 0) > 0
        ]
        esp_ativos.sort(key=lambda par: par[0])
        if not esp_ativos:
            esp_txt = "Espaços 1º Círculo/Dia: 0"
        elif len(esp_ativos) == 1 and esp_ativos[0][0] == 1:
            esp_txt = f"Espaços 1º Círculo/Dia: {esp_ativos[0][1]}"
        else:
            esp_txt = "Espaços/Dia: " + ", ".join(f"{c}º: {q}" for c, q in esp_ativos)
        partes.append(
            _xml_p_rotulo(
                "Atributos de Conjuração",
                f"Tradição {trad_txt} ({est_txt}) | Ataque de Magia {formatar_bonus(conj['ataque_magia']['total'])} | "
                f"CD {conj['cd_magia']['total']} | Nível de Truque {conj['nivel_truque']} | "
                f"{esp_txt} | "
                f"Pontos de Foco: {conj['magias_foco']['pontos_foco']['maximo']}",
            )
        )
        linhas_mag = []
        for grp, lst, mostrar_prep in (
            ("Truque", conj["truques_magicos"], False),
            ("Foco", conj["magias_foco"]["slots"], False),
            ("Inata", conj["magias_inatas"], False),
            (None, conj["magias"], True),
        ):
            for m in lst:
                if m.get("nome"):
                    cat_lbl = grp if grp is not None else f"{int(m.get('nivel') or 1)}º Círculo"
                    notas_base = m.get("frequencia") or m.get("anotacoes") or ""
                    if mostrar_prep and m.get("preparada"):
                        extra = f"Preparada • {notas_base}" if notas_base else "Preparada"
                    else:
                        extra = notas_base or "—"
                    linhas_mag.append([cat_lbl, m["nome"], m.get("acoes") or "—", ",".join(m.get("componentes") or []) or "—", extra])
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
