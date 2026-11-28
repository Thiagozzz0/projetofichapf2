"""Exportador de ficha oficial de Castles & Crusades em PDF vetorial preenchido."""

from __future__ import annotations

from typing import Any

import pymupdf

from motor_cc.atributos import ORDEM_ATRIBUTOS
from motor_cc.dados import TEMPLATE_PDF_CC, carregar_estrutura_ficha
from motor_cc.exportacao.comum import fmt_mod, fmt_movimento

_COR_TINTA = (0.08, 0.11, 0.17)
_COR_SUBTITULO = (0.28, 0.33, 0.40)


def _escrever_caixa(
    page: pymupdf.Page,
    rect_coords: list[float],
    texto: str,
    fontsize: float = 9.0,
    min_fontsize: float = 4.5,
    fontname: str = "helv",
    align: int = pymupdf.TEXT_ALIGN_LEFT,
    color: tuple[float, float, float] = _COR_TINTA,
) -> None:
    """Insere texto dentro de `rect_coords`, reduzindo a fonte em scratch se preciso para não cortar."""
    if not texto:
        return
    rect = pymupdf.Rect(rect_coords)

    # Usa documento scratch de 1 página para medir o ajuste sem sujar a página real
    scratch_doc = pymupdf.open()
    try:
        scratch_page = scratch_doc.new_page(width=page.rect.width, height=page.rect.height)
        tam = fontsize
        escolhido = min_fontsize
        while tam >= min_fontsize:
            rc = scratch_page.insert_textbox(
                rect,
                texto,
                fontsize=tam,
                fontname=fontname,
                align=align,
                color=color,
            )
            if rc >= 0:
                escolhido = tam
                break
            tam = round(tam - 0.5, 2)
    finally:
        scratch_doc.close()

    page.insert_textbox(
        rect,
        texto,
        fontsize=escolhido,
        fontname=fontname,
        align=align,
        color=color,
    )


def _desenhar_losango_preenchido(page: pymupdf.Page, rect_coords: list[float]) -> None:
    r = pymupdf.Rect(rect_coords)
    cx = (r.x0 + r.x1) / 2.0
    cy = (r.y0 + r.y1) / 2.0
    dx = max(1.6, r.width * 0.28)
    dy = max(1.6, r.height * 0.28)
    pontos = [
        pymupdf.Point(cx, cy - dy),
        pymupdf.Point(cx + dx, cy),
        pymupdf.Point(cx, cy + dy),
        pymupdf.Point(cx - dx, cy),
    ]
    page.draw_polyline(pontos, color=_COR_TINTA, fill=_COR_TINTA, closePath=True, width=0.5)


def _adicionar_pagina_anexa(doc: pymupdf.Document, ficha: dict[str, Any], pendencias: dict[str, Any]) -> None:
    page = doc.new_page(width=612.0, height=792.0)
    cab = ficha["cabecalho"]
    y = 40.0

    _escrever_caixa(
        page,
        [40.0, y, 572.0, y + 20.0],
        f"ANEXO DA FICHA - {cab['nome']} ({cab['raca_nome']} {cab['classe_nome']} Nv. {cab['nivel']})",
        fontsize=12.0,
        fontname="hebo",
    )
    y += 18.0
    _escrever_caixa(
        page,
        [40.0, y, 572.0, y + 14.0],
        f"Método de Atributos: {cab['rotulo_metodo']}",
        fontsize=8.5,
        fontname="helv",
        color=_COR_SUBTITULO,
    )
    y += 20.0
    page.draw_line(pymupdf.Point(40.0, y), pymupdf.Point(572.0, y), color=_COR_SUBTITULO, width=0.8)
    y += 10.0

    if pendencias.get("pv_extra"):
        _escrever_caixa(page, [40.0, y, 572.0, y + 14.0], "Pontos de Vida por Nível (13º ao 24º):", fontsize=9.5, fontname="hebo")
        y += 14.0
        pv_txt = " | ".join(f"{p['nivel']}º: {p['pv']}" for p in pendencias["pv_extra"])
        _escrever_caixa(page, [48.0, y, 572.0, y + 24.0], pv_txt, fontsize=8.5)
        y += 28.0

    if pendencias.get("armas_extra"):
        _escrever_caixa(page, [40.0, y, 572.0, y + 14.0], "Armas Adicionais:", fontsize=9.5, fontname="hebo")
        y += 14.0
        linhas_a = [
            f"- {a['nome']} - Ataque: {fmt_mod(a['total_ataque'])} (BpA {a['bpa']} + Mod {fmt_mod(a['mod_ataque'])}) | Dano: {a['total_dano']} | Alcance: {a['alcance']}"
            for a in pendencias["armas_extra"]
        ]
        bloco_h = max(18.0, 12.0 * len(linhas_a) + 4.0)
        _escrever_caixa(page, [48.0, y, 572.0, y + bloco_h], "\n".join(linhas_a), fontsize=8.5)
        y += bloco_h + 8.0

    if pendencias.get("feiticos_extra"):
        _escrever_caixa(
            page,
            [40.0, y, 572.0, y + 14.0],
            "Feitiços Conhecidos / Preparados (Círculos 4-9 e Excedentes):",
            fontsize=9.5,
            fontname="hebo",
        )
        y += 16.0
        for circ_str, info_esp, lista_f in pendencias["feiticos_extra"]:
            if y > 740.0:
                page = doc.new_page(width=612.0, height=792.0)
                y = 40.0
            cab_circ = f"Nível {circ_str} ({info_esp['total']}/dia):"
            _escrever_caixa(page, [48.0, y, 572.0, y + 13.0], cab_circ, fontsize=9.0, fontname="hebo")
            y += 13.0
            nomes_f = ", ".join(f"{f['nome'].title()}{'*' if f.get('reversivel') else ''}" for f in lista_f) or "(Nenhum selecionado)"
            est_h = max(14.0, 12.0 * (1 + len(nomes_f) // 85))
            _escrever_caixa(page, [56.0, y, 572.0, y + est_h], nomes_f, fontsize=8.2)
            y += est_h + 6.0


def exportar_ficha_cc_pdf(ficha: dict[str, Any]) -> bytes:
    """Preenche a ficha oficial vetorial de Castles & Crusades e retorna os bytes do PDF."""
    if not TEMPLATE_PDF_CC.exists():
        raise FileNotFoundError(f"Template PDF oficial de C&C não encontrado em {TEMPLATE_PDF_CC}")

    estrutura = carregar_estrutura_ficha()
    blocos = estrutura["paginas"][0]["blocos"]

    doc = pymupdf.open(str(TEMPLATE_PDF_CC))
    try:
        page = doc[0]
        cab = ficha["cabecalho"]
        attrs = ficha["atributos"]["atributos"]
        comb = ficha["combate"]
        ca = comb["ca"]
        pv = comb["pv"]
        habs = ficha["habilidades"]
        eq = ficha["equipamentos"]
        magias = ficha["magias"]
        notas = ficha.get("notas", {})

        # 0. Campo explícito do Método de Geração de Atributos na margem superior do cabeçalho
        _escrever_caixa(
            page,
            [196.0, 19.0, 562.2, 33.0],
            f"Método: {cab['rotulo_metodo']}",
            fontsize=8.0,
            fontname="hebo",
            align=pymupdf.TEXT_ALIGN_RIGHT,
            color=_COR_SUBTITULO,
        )

        # 1. Cabeçalho oficial (10 campos)
        raca_txt = cab["raca_nome"]
        if cab.get("linhagem_meio_elfo"):
            raca_txt += f" ({cab['linhagem_meio_elfo'].capitalize()})"
        disp_curta = cab["disposicao_nome"].split(" ou ")[0]
        valores_cab = {
            "nome": cab["nome"],
            "titulos": cab.get("titulos") or "",
            "raca": raca_txt,
            "classe": cab["classe_nome"],
            "nivel": str(cab["nivel"]),
            "disposicao": disp_curta,
            "idiomas": ", ".join(cab.get("idiomas") or []),
            "movimento": fmt_movimento(cab["movimento_m"]),
            "exp": str(cab["exp"]),
            "prox_exp": str(cab["prox_exp"]) if cab.get("prox_exp") is not None else "Máx.",
        }
        for campo in blocos["cabecalho"]["campos"]:
            cid = campo["id"]
            val = valores_cab.get(cid, "")
            al = pymupdf.TEXT_ALIGN_CENTER if cid in {"nivel", "movimento"} else pymupdf.TEXT_ALIGN_LEFT
            rc = list(campo["rect"])
            if al == pymupdf.TEXT_ALIGN_LEFT:
                rc[0] += 3.0
            _escrever_caixa(page, rc, val, fontsize=8.5, min_fontsize=5.5, align=al)

        # 2. Atributos e bolinhas de Primários
        for campo_attr in blocos["atributos"]["campos"]:
            aid = campo_attr["id"]
            det = attrs[aid]
            if det["primario"]:
                pr = pymupdf.Rect(campo_attr["primario_circulo_rect"])
                centro = pymupdf.Point((pr.x0 + pr.x1) / 2.0, (pr.y0 + pr.y1) / 2.0)
                page.draw_circle(centro, 2.5, color=_COR_TINTA, fill=_COR_TINTA)
            _escrever_caixa(
                page,
                campo_attr["valor_rect"],
                str(det["valor"]),
                fontsize=12.0,
                fontname="hebo",
                align=pymupdf.TEXT_ALIGN_CENTER,
            )
            _escrever_caixa(
                page,
                campo_attr["modificador_rect"],
                fmt_mod(det["modificador"]),
                fontsize=12.0,
                fontname="hebo",
                align=pymupdf.TEXT_ALIGN_CENTER,
            )

        # 3. Classe de Armadura e Equipamento Defensivo
        bl_ca = blocos["classe_armadura"]
        _escrever_caixa(
            page,
            bl_ca["ca_total_rect"],
            str(ca["total"]),
            fontsize=15.0,
            fontname="hebo",
            align=pymupdf.TEXT_ALIGN_CENTER,
        )
        for parc in bl_ca["parcelas"]:
            pid = parc["id"]
            v = ca.get(pid, 0)
            txt = fmt_mod(v) if pid == "mod_destreza" else str(v)
            _escrever_caixa(page, parc["rect"], txt, fontsize=9.0, fontname="hebo", align=pymupdf.TEXT_ALIGN_CENTER)

        if comb.get("ferimentos_e_condicoes"):
            _escrever_caixa(
                page,
                bl_ca["ferimentos_e_condicoes_rect"],
                comb["ferimentos_e_condicoes"],
                fontsize=7.5,
            )

        eq_def = bl_ca["equipamento_defensivo"]
        _escrever_caixa(page, eq_def["armadura_rect"], ca["armadura_nome"], fontsize=7.5)
        _escrever_caixa(page, eq_def["escudo_rect"], ca["escudo_nome"], fontsize=7.5)
        _escrever_caixa(page, eq_def["elmo_rect"], ca["elmo_nome"], fontsize=7.5)

        # 4. Pontos de Vida (Total + quadrinhos 1º..12º)
        bl_pv = blocos["pontos_de_vida"]
        _escrever_caixa(
            page,
            bl_pv["pv_total_rect"],
            str(pv["total"]),
            fontsize=14.0,
            fontname="hebo",
            align=pymupdf.TEXT_ALIGN_CENTER,
        )
        pv_lista = pv.get("por_nivel", [])
        for idx_box, box in enumerate(bl_pv["por_nivel"]):
            if idx_box < len(pv_lista):
                _escrever_caixa(
                    page,
                    box["rect"],
                    str(pv_lista[idx_box]["pv"]),
                    fontsize=8.5,
                    fontname="hebo",
                    align=pymupdf.TEXT_ALIGN_CENTER,
                )

        # 5. Armas (até 2 slots na página 1)
        ataques = comb.get("ataques", [])
        for idx_slot, slot in enumerate(blocos["armas"]["slots"]):
            if idx_slot >= len(ataques):
                break
            atq = ataques[idx_slot]
            cp = slot["campos"]
            mapa_arma = {
                "nome_arma": (atq["nome"], pymupdf.TEXT_ALIGN_LEFT),
                "bpa": (str(atq["bpa"]), pymupdf.TEXT_ALIGN_CENTER),
                "mod_ataque": (fmt_mod(atq["mod_ataque"]), pymupdf.TEXT_ALIGN_CENTER),
                "var_ataque": (str(atq["var_ataque"]), pymupdf.TEXT_ALIGN_CENTER),
                "magia_ataque": (str(atq["magia_ataque"]), pymupdf.TEXT_ALIGN_CENTER),
                "total_ataque": (fmt_mod(atq["total_ataque"]), pymupdf.TEXT_ALIGN_CENTER),
                "dano_base": (atq["dano_base"], pymupdf.TEXT_ALIGN_CENTER),
                "mod_dano": (fmt_mod(atq["mod_dano"]), pymupdf.TEXT_ALIGN_CENTER),
                "var_dano": (str(atq["var_dano"]), pymupdf.TEXT_ALIGN_CENTER),
                "magia_dano": (str(atq["magia_dano"]), pymupdf.TEXT_ALIGN_CENTER),
                "total_dano": (atq["total_dano"], pymupdf.TEXT_ALIGN_CENTER),
            }
            for k, (val, al) in mapa_arma.items():
                fn = "hebo" if k in {"total_ataque", "total_dano"} else "helv"
                _escrever_caixa(page, cp[k], val, fontsize=8.0, min_fontsize=5.5, fontname=fn, align=al)

        # 6. Habilidades da Raça e da Classe
        def _pad(rect_coords: list[float], dx: float = 3.0, dy: float = 2.0) -> list[float]:
            return [rect_coords[0] + dx, rect_coords[1] + dy, rect_coords[2] - dx, rect_coords[3] - dy]

        txt_raca = "\n".join(f"- {h['nome']}: {h['descricao']}" for h in habs.get("raca", []))
        _escrever_caixa(
            page,
            _pad(blocos["habilidades"]["habilidades_raca"]["rect"]),
            txt_raca,
            fontsize=7.2,
            min_fontsize=4.5,
        )

        txt_classe = "\n".join(f"- {h['nome']} ({h['nivel']}º): {h['resumo']}" for h in habs.get("classe", []))
        _escrever_caixa(
            page,
            _pad(blocos["habilidades"]["habilidades_classe"]["rect"]),
            txt_classe,
            fontsize=7.2,
            min_fontsize=4.5,
        )

        # 7. Equipamentos, Sobrecarga, Itens Mágicos, Poções e Moedas
        bl_eq = blocos["equipamentos_e_moedas"]
        sc = eq["sobrecarga"]
        linhas_itens = [f"Carga: SB {sc['sb_total']}/{sc['categoria_sobrecarga_cs']} ({sc['categoria_nome']})"]
        for it in eq.get("todos_itens_resumo", []):
            linhas_itens.append(f"- {it['nome']} (SB {it['sb']})")
        _escrever_caixa(
            page,
            _pad(bl_eq["itens_e_equipamentos"]["rect"]),
            "\n".join(linhas_itens),
            fontsize=7.5,
            min_fontsize=4.5,
        )

        if notas.get("itens_magicos"):
            _escrever_caixa(
                page,
                _pad(bl_eq["itens_magicos"]["rect"]),
                "\n".join(f"- {x}" for x in notas["itens_magicos"]),
                fontsize=7.5,
                min_fontsize=5.0,
            )
        if notas.get("pocoes"):
            _escrever_caixa(
                page,
                _pad(bl_eq["pocoes"]["rect"]),
                "\n".join(f"- {x}" for x in notas["pocoes"]),
                fontsize=7.5,
                min_fontsize=5.0,
            )
        if notas.get("anotacoes"):
            _escrever_caixa(
                page,
                _pad(bl_eq["recursos_viagem"]["notas_rect"]),
                notas["anotacoes"],
                fontsize=7.0,
                min_fontsize=4.5,
            )

        moedas = eq["moedas_restantes"]
        for m_campo in bl_eq["moedas"]:
            mid = m_campo["id"]
            _escrever_caixa(
                page,
                m_campo["rect"],
                str(moedas.get(mid, 0)),
                fontsize=8.5,
                fontname="hebo",
                align=pymupdf.TEXT_ALIGN_CENTER,
            )

        # 8. Feitiços Conhecidos (Níveis 0–3 na página 1 + excedente em anexo)
        feiticos_extra_anexo: list[tuple[str, dict[str, int], list[dict[str, Any]]]] = []
        if magias.get("conjurador"):
            espacos = magias.get("espacos_por_circulo", {})
            por_circ = magias.get("feiticos_por_circulo", {})

            for niv_bloco in blocos["feiticos_conhecidos"]["niveis"]:
                c_str = str(niv_bloco["nivel"])
                info_esp = espacos.get(c_str)
                if info_esp:
                    esp_txt = f"{info_esp['total']}/dia"
                    if info_esp["bonus_atributo"]:
                        esp_txt += f" (+{info_esp['bonus_atributo']})"
                    _escrever_caixa(
                        page,
                        niv_bloco["espacos_dia_rect"],
                        esp_txt,
                        fontsize=8.0,
                        fontname="hebo",
                        align=pymupdf.TEXT_ALIGN_CENTER,
                    )

                lista_f = por_circ.get(c_str, [])
                for idx_l, linha_cfg in enumerate(niv_bloco["linhas"]):
                    if idx_l >= len(lista_f):
                        break
                    f_obj = lista_f[idx_l]
                    _desenhar_losango_preenchido(page, linha_cfg["preparado_losango_rect"])
                    nome_f = f"{f_obj['nome'].title()}{'*' if f_obj.get('reversivel') else ''}"
                    rc_f = [linha_cfg["nome_rect"][0] + 2.0, linha_cfg["nome_rect"][1], linha_cfg["nome_rect"][2], linha_cfg["nome_rect"][3]]
                    _escrever_caixa(page, rc_f, nome_f, fontsize=7.5, min_fontsize=5.0)

                if len(lista_f) > 7 and info_esp:
                    feiticos_extra_anexo.append((f"{c_str} (restante)", info_esp, lista_f[7:]))

            # Círculos 4–9 vão para a folha anexa
            for c_str in sorted(espacos.keys(), key=int):
                if int(c_str) >= 4:
                    feiticos_extra_anexo.append((c_str, espacos[c_str], por_circ.get(c_str, [])))

        # Página anexa condicional
        pendencias_anexo: dict[str, Any] = {}
        if len(pv_lista) > 12:
            pendencias_anexo["pv_extra"] = pv_lista[12:]
        if len(ataques) > 2:
            pendencias_anexo["armas_extra"] = ataques[2:]
        if feiticos_extra_anexo:
            pendencias_anexo["feiticos_extra"] = feiticos_extra_anexo

        if pendencias_anexo:
            _adicionar_pagina_anexa(doc, ficha, pendencias_anexo)

        return doc.tobytes(garbage=3, deflate=True)
    finally:
        doc.close()
