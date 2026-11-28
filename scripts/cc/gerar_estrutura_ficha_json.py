"""Mapeia ref/cc/C&C_ficha.pdf -> dados/dadosc&c/estrutura_ficha.json
e copia o template oficial para dados/dadosc&c/templates/ficha_oficial_cc.pdf.

Extrai coordenadas vetoriais exatas (em pontos PDF, origem no canto superior esquerdo)
de todos os blocos e campos da ficha oficial de 1 página de Castles & Crusades (PT-BR),
deixando o mapa pronto para preenchimento automático pelo exportador PDF (motor_cc).

Execução:
    .venv\\Scripts\\python.exe scripts/cc/gerar_estrutura_ficha_json.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pymupdf

RAIZ = Path(__file__).resolve().parents[2]
PDF_ORIGEM = RAIZ / "ref" / "cc" / "C&C_ficha.pdf"
PDF_TEMPLATE = RAIZ / "dados" / "dadosc&c" / "templates" / "ficha_oficial_cc.pdf"
SAIDA_PATH = RAIZ / "dados" / "dadosc&c" / "estrutura_ficha.json"


def _rect_list(r: pymupdf.Rect) -> list[float]:
    return [round(float(r.x0), 1), round(float(r.y0), 1), round(float(r.x1), 1), round(float(r.y1), 1)]


def construir_estrutura(doc: pymupdf.Document) -> dict[str, Any]:
    page = doc[0]
    largura = round(float(page.rect.width), 1)
    altura = round(float(page.rect.height), 1)
    drawings = page.get_drawings()

    # 1. Bolinhas de Atributos Primários (6 círculos em x ~ 50.7..57.5)
    bolinhas = sorted(
        [
            _rect_list(d["rect"])
            for d in drawings
            if 40 <= d["rect"].x0 <= 70 and 5 <= d["rect"].width <= 12 and 5 <= d["rect"].height <= 12
        ],
        key=lambda r: r[1],
    )
    assert len(bolinhas) == 6, f"Esperado 6 bolinhas de atributos primários, obtido {len(bolinhas)}"

    # 2. 12 caixas de PV por nível (1º ao 12º, y ~ 190..206)
    caixas_pv = sorted(
        [
            _rect_list(d["rect"])
            for d in drawings
            if 188 <= d["rect"].y0 <= 194 and 17 <= d["rect"].width <= 22 and 13 <= d["rect"].height <= 18
        ],
        key=lambda r: r[0],
    )
    assert len(caixas_pv) == 12, f"Esperado 12 caixas de PV por nível, obtido {len(caixas_pv)}"

    # 3. 5 caixas brancas da fórmula de CA (Armadura, Escudo, Mod, Magia, Var)
    caixas_ca = sorted(
        [
            _rect_list(d["rect"])
            for d in drawings
            if 132 <= d["rect"].y0 <= 135
            and 22 <= d["rect"].width <= 26
            and 13 <= d["rect"].height <= 17
            and d.get("fill") == (1.0, 1.0, 1.0)
        ],
        key=lambda r: r[0],
    )
    assert len(caixas_ca) == 5, f"Esperado 5 caixas da fórmula de CA, obtido {len(caixas_ca)}"

    # 4. 28 losangos de Feitiços Conhecidos (4 níveis x 7 linhas)
    losangos = sorted(
        [
            _rect_list(d["rect"])
            for d in drawings
            if 425 <= d["rect"].x0 <= 450 and 4 <= d["rect"].width <= 12 and 4 <= d["rect"].height <= 12
        ],
        key=lambda r: r[1],
    )
    assert len(losangos) == 28, f"Esperado 28 losangos de feitiços, obtido {len(losangos)}"

    # 5. 3 caixas de Moedas (Ouro, Prata, Cobre)
    caixas_moedas = sorted(
        [
            _rect_list(d["rect"])
            for d in drawings
            if d["rect"].y0 > 670 and d["rect"].x0 < 200 and d["rect"].width > 50
        ],
        key=lambda r: r[1],
    )
    assert len(caixas_moedas) == 3, f"Esperado 3 caixas de moedas, obtido {len(caixas_moedas)}"

    # Montagem estruturada dos atributos
    specs_atributos = [
        ("forca", "FOR", "Força", ["Paralisia", "Constrição"]),
        ("destreza", "DES", "Destreza", ["Arma de Sopro", "Armadilhas"]),
        ("constituicao", "CON", "Constituição", ["Doenças", "Dreno de Energia", "Veneno"]),
        ("inteligencia", "INT", "Inteligência", ["Magia Arcana", "Ilusões"]),
        (
            "sabedoria",
            "SAB",
            "Sabedoria",
            ["Confusão", "Ataques Visuais", "Magia Divina", "Petrificação", "Polimorfia"],
        ),
        ("carisma", "CAR", "Carisma", ["Ataques Mortais", "Encantamento", "Medo"]),
    ]
    atributos_campos = []
    for (aid, sigla, nome, salvamentos), bol in zip(specs_atributos, bolinhas):
        y_centro = round((bol[1] + bol[3]) / 2.0, 1)
        atributos_campos.append(
            {
                "id": aid,
                "sigla": sigla,
                "rotulo": nome,
                "jogadas_protecao": salvamentos,
                "primario_circulo_rect": bol,
                "valor_rect": [116.0, round(y_centro - 10.0, 1), 144.0, round(y_centro + 10.0, 1)],
                "modificador_rect": [147.0, round(y_centro - 10.0, 1), 174.0, round(y_centro + 10.0, 1)],
            }
        )

    # Montagem dos 4 níveis de Feitiços Conhecidos (Nível 0..3, 7 linhas cada)
    niveis_feiticos = []
    y_cabecalhos_nivel = [298.0, 414.0, 525.0, 637.0]
    for niv in range(4):
        grupo = losangos[niv * 7 : (niv + 1) * 7]
        linhas_nivel = []
        for idx_l, los in enumerate(grupo, start=1):
            linhas_nivel.append(
                {
                    "linha": idx_l,
                    "preparado_losango_rect": los,
                    "nome_rect": [451.0, round(los[1] - 1.5, 1), 558.8, round(los[3] + 1.5, 1)],
                }
            )
        niveis_feiticos.append(
            {
                "nivel": niv,
                "rotulo": f"Nível {niv}",
                "espacos_dia_rect": [488.0, y_cabecalhos_nivel[niv], 545.0, round(y_cabecalhos_nivel[niv] + 12.0, 1)],
                "linhas": linhas_nivel,
            }
        )

    # 2 blocos de Armas
    armas_blocos = []
    for idx_a, y0_a in enumerate([218.3, 249.9], start=1):
        y1_a = round(y0_a + 26.9, 1)
        y_val0 = round(y0_a + 12.0, 1)
        armas_blocos.append(
            {
                "indice": idx_a,
                "box_rect": [178.7, y0_a, 560.7, y1_a],
                "campos": {
                    "nome_arma": [182.0, y_val0, 265.0, y1_a],
                    "bpa": [268.0, y_val0, 286.0, y1_a],
                    "mod_ataque": [294.0, y_val0, 312.0, y1_a],
                    "var_ataque": [318.0, y_val0, 336.0, y1_a],
                    "magia_ataque": [344.0, y_val0, 366.0, y1_a],
                    "total_ataque": [373.0, y_val0, 398.0, y1_a],
                    "dano_base": [404.0, y_val0, 434.0, y1_a],
                    "mod_dano": [442.0, y_val0, 462.0, y1_a],
                    "var_dano": [472.0, y_val0, 492.0, y1_a],
                    "magia_dano": [500.0, y_val0, 524.0, y1_a],
                    "total_dano": [531.0, y_val0, 558.0, y1_a],
                },
            }
        )

    return {
        "meta": {
            "titulo": "Castles & Crusades — Estrutura Oficial da Ficha de Personagem",
            "sistema": "Castles & Crusades (1ª Edição Brasileira)",
            "fonte_pdf": "ref/cc/C&C_ficha.pdf",
            "template_pdf": "dados/dadosc&c/templates/ficha_oficial_cc.pdf",
            "total_paginas": len(doc),
            "dimensoes_pt": {"largura": largura, "altura": altura},
            "tipo_formulario": "estatico_vetorial_sem_acroform",
            "observacoes": [
                "Ficha oficial de página única (US Letter 612 x 792 pt), sem campos AcroForm; preenchimento via coordenadas vetoriais [x0, y0, x1, y1].",
                "Na seção Feitiços Conhecidos há espaço impresso para Níveis 0 a 3 (7 linhas com losango de preparação cada); personagens com feitiços de níveis 4–9 podem usar folha anexa no exportador.",
                "Na seção PV há 12 quadrinhos individuais (1º ao 12º nível); personagens de nível 13+ registram o total na caixa PV e o detalhamento no resumo textual.",
            ],
        },
        "paginas": [
            {
                "numero_pagina_pdf": 1,
                "titulo": "Ficha Completa de Personagem — Castles & Crusades",
                "blocos": {
                    "cabecalho": {
                        "rotulo_oficial": "IDENTIFICAÇÃO DO PERSONAGEM",
                        "campos": [
                            {"id": "nome", "rotulo": "Nome:", "tipo": "texto", "rect": [230.7, 36.9, 390.0, 48.8]},
                            {"id": "titulos", "rotulo": "Títulos:", "tipo": "texto", "rect": [431.9, 36.9, 562.2, 48.8]},
                            {"id": "raca", "rotulo": "Raça:", "tipo": "texto", "rect": [228.2, 54.0, 315.2, 65.9]},
                            {"id": "classe", "rotulo": "Classe:", "tipo": "texto", "rect": [353.5, 55.5, 440.6, 67.3]},
                            {"id": "nivel", "rotulo": "Nível:", "tipo": "numero", "rect": [473.8, 54.6, 564.5, 65.9]},
                            {"id": "disposicao", "rotulo": "Disposição:", "tipo": "texto", "rect": [254.1, 70.8, 328.2, 83.1]},
                            {"id": "idiomas", "rotulo": "Idiomas:", "tipo": "texto", "rect": [370.3, 72.2, 561.2, 84.5]},
                            {"id": "movimento", "rotulo": "Movimento:", "tipo": "texto", "rect": [255.0, 88.5, 300.0, 101.0]},
                            {"id": "exp", "rotulo": "Exp:", "tipo": "numero", "rect": [343.7, 88.8, 417.8, 101.0]},
                            {"id": "prox_exp", "rotulo": "Próx:", "tipo": "numero", "rect": [464.1, 88.8, 559.5, 100.7]},
                        ],
                    },
                    "atributos": {
                        "rotulo_oficial": "ATRIBUTOS",
                        "formula_siege": "d20 + Nv + Modificador",
                        "campos": atributos_campos,
                    },
                    "classe_armadura": {
                        "rotulo_oficial": "CA",
                        "formula": "10 + Armadura + Escudo + Mod + Magia + Var",
                        "ca_total_rect": [184.7, 124.9, 230.8, 156.1],
                        "parcelas": [
                            {"id": "armadura", "rotulo": "Armadura", "rect": caixas_ca[0]},
                            {"id": "escudo", "rotulo": "Escudo", "rect": caixas_ca[1]},
                            {"id": "mod_destreza", "rotulo": "Mod", "rect": caixas_ca[2]},
                            {"id": "magia", "rotulo": "Magia", "rect": caixas_ca[3]},
                            {"id": "var", "rotulo": "Var", "rect": caixas_ca[4]},
                        ],
                        "ferimentos_e_condicoes_rect": [449.6, 109.3, 559.5, 152.4],
                        "equipamento_defensivo": {
                            "faixa_rect": [179.2, 161.6, 561.2, 176.8],
                            "armadura_rect": [222.0, 162.5, 330.0, 176.0],
                            "escudo_rect": [365.0, 162.5, 438.0, 176.0],
                            "elmo_rect": [468.0, 162.5, 559.0, 176.0],
                        },
                    },
                    "pontos_de_vida": {
                        "rotulo_oficial": "PV",
                        "pv_total_rect": [212.0, 184.0, 286.0, 210.0],
                        "por_nivel": [
                            {"nivel": i + 1, "rotulo": f"{i + 1}º", "rect": r}
                            for i, r in enumerate(caixas_pv)
                        ],
                    },
                    "armas": {
                        "rotulo_oficial": "ARMAS",
                        "slots": armas_blocos,
                    },
                    "habilidades": {
                        "habilidades_raca": {
                            "rotulo_oficial": "Habilidades da Raça",
                            "rect": [213.0, 302.1, 420.7, 401.1],
                        },
                        "habilidades_classe": {
                            "rotulo_oficial": "Habilidades da Classe",
                            "rect": [212.4, 409.6, 420.0, 513.3],
                        },
                    },
                    "equipamentos_e_moedas": {
                        "itens_e_equipamentos": {
                            "rotulo_oficial": "Itens e Equipamentos",
                            "rect": [37.5, 468.7, 173.9, 672.3],
                        },
                        "itens_magicos": {
                            "rotulo_oficial": "Itens Mágicos",
                            "rect": [184.1, 541.9, 299.5, 635.1],
                        },
                        "pocoes": {
                            "rotulo_oficial": "Poções",
                            "rect": [307.5, 541.9, 422.8, 635.1],
                        },
                        "recursos_viagem": {
                            "rotulo_oficial": "Recursos de Viagem",
                            "agua_quadrinhos": 42,
                            "comida_quadrinhos": 42,
                            "notas_rect": [332.7, 656.5, 427.4, 741.0],
                        },
                        "moedas": [
                            {"id": "ouro", "rotulo": "Ouro:", "rect": caixas_moedas[0]},
                            {"id": "prata", "rotulo": "Prata:", "rect": caixas_moedas[1]},
                            {"id": "cobre", "rotulo": "Cobre:", "rect": caixas_moedas[2]},
                        ],
                    },
                    "feiticos_conhecidos": {
                        "rotulo_oficial": "Feitiços Conhecidos",
                        "niveis": niveis_feiticos,
                    },
                },
            }
        ],
    }


def main() -> None:
    assert PDF_ORIGEM.exists(), f"PDF da ficha não encontrado em {PDF_ORIGEM}"

    # Copia para dados/dadosc&c/templates/ficha_oficial_cc.pdf
    PDF_TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PDF_ORIGEM, PDF_TEMPLATE)

    doc = pymupdf.open(str(PDF_ORIGEM))
    try:
        estrutura = construir_estrutura(doc)
    finally:
        doc.close()

    SAIDA_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_PATH.write_text(json.dumps(estrutura, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    p1 = estrutura["paginas"][0]["blocos"]
    print(f"[OK] Template copiado para: {PDF_TEMPLATE}")
    print(f"[OK] Estrutura gerada em:   {SAIDA_PATH}")
    print(f"     - Cabeçalho: {len(p1['cabecalho']['campos'])} campos")
    print(f"     - Atributos: {len(p1['atributos']['campos'])} atributos com círculos de Primários")
    print(f"     - CA: total + {len(p1['classe_armadura']['parcelas'])} parcelas + Armadura/Escudo/Elmo")
    print(f"     - PV: total + {len(p1['pontos_de_vida']['por_nivel'])} caixas por nível (1º-12º)")
    print(f"     - Armas: {len(p1['armas']['slots'])} slots completos")
    print(f"     - Feitiços: {len(p1['feiticos_conhecidos']['niveis'])} níveis (0-3) x 7 linhas = 28 slots")
    print(f"     - Moedas: {len(p1['equipamentos_e_moedas']['moedas'])} campos (Ouro/Prata/Cobre)")


if __name__ == "__main__":
    main()
