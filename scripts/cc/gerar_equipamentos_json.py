"""Gerador e validador de dados/dadosc&c/equipamentos.json a partir de ref/cc/Equipamentos_e_Sobrecarga_C&C.pdf (pp. 104–111)."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import pymupdf

RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
CAMINHO_PDF = RAIZ_PROJETO / "ref" / "cc" / "Equipamentos_e_Sobrecarga_C&C.pdf"
DIR_DADOS_CC = RAIZ_PROJETO / "dados" / "dadosc&c"
CAMINHO_SAIDA = DIR_DADOS_CC / "equipamentos.json"


def _slugify(texto: str) -> str:
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    limpo = re.sub(r"[^a-zA-Z0-9]+", "_", sem_acentos.lower()).strip("_")
    return limpo or "item"


def _parse_custo_pc(texto: str) -> int | None:
    """Converte custos como '15 po', '5 pp', '3 pc', '4,000 po' para peças de cobre (1 po = 100 pc, 1 pp = 10 pc)."""
    bruto = texto.strip().lower().replace(".", "").replace(",", "")
    if not bruto or bruto in {"—", "-", "varia"}:
        return None
    m = re.match(r"^(\d+)\s*\+?\s*(po|pp|sp|pc|cp|pl)$", bruto)
    if not m:
        return None
    val = int(m.group(1))
    un = m.group(2)
    if un == "pl":
        return val * 1000
    if un == "po":
        return val * 100
    if un in {"pp", "sp"}:
        return val * 10
    return val


def _parse_sb(texto: str) -> tuple[int | None, str]:
    bruto = texto.strip()
    if not bruto or bruto in {"—", "-"}:
        return None, bruto
    if bruto == "*":
        return 0, "*"
    m = re.match(r"^(\d+)", bruto)
    return (int(m.group(1)) if m else None), bruto


def _extrair_tabelas_pdf() -> list[list[list[str]]]:
    """Extrai todas as tabelas das páginas 2..6 do PDF usando PyMuPDF `find_tables()`."""
    doc = pymupdf.open(CAMINHO_PDF)
    todas: list[list[list[str]]] = []
    for idx in range(1, 6):
        page = doc[idx]
        for tab in page.find_tables().tables:
            linhas: list[list[str]] = []
            for row in tab.extract():
                limpa = [re.sub(r"\s+", " ", (c or "")).strip() for c in row]
                if any(limpa):
                    linhas.append(limpa)
            if linhas:
                todas.append(linhas)
    doc.close()
    return todas


def _garantir_ids_unicos(itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    vistos: dict[str, int] = {}
    for item in itens:
        base = item["id"]
        if base in vistos:
            vistos[base] += 1
            item["id"] = f"{base}_{vistos[base]}"
        else:
            vistos[base] = 1
    return itens


def _construir_de_linhas_texto() -> dict[str, list[dict[str, Any]]]:
    """Extrai todas as 9 tabelas diretamente das páginas 2..6 via coordenadas de blocos/linhas do PDF."""
    doc = pymupdf.open(CAMINHO_PDF)
    paginas = [doc[i].get_text("text").splitlines() for i in range(len(doc))]
    doc.close()

    def limpar(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    # 1. Elmos (pág 2: linhas entre 'Tabela: Elmos' e '* Os ajustes')
    p2 = [limpar(x) for x in paginas[1] if limpar(x)]
    p3 = [limpar(x) for x in paginas[2] if limpar(x)]
    p4 = [limpar(x) for x in paginas[3] if limpar(x)]
    p5 = [limpar(x) for x in paginas[4] if limpar(x)]
    p6 = [limpar(x) for x in paginas[5] if limpar(x)]

    def fatiar(lista: list[str], inicio: str, fim: str | None = None) -> list[str]:
        i0 = next(i for i, x in enumerate(lista) if x.startswith(inicio))
        if fim is None:
            return lista[i0:]
        i1 = next(i for i in range(i0 + 1, len(lista)) if lista[i].startswith(fim))
        return lista[i0:i1]

    # Helpers de parsing para tabelas de 5 colunas (nome, custo, ca, peso, sb)
    def parse_5col_ca(tokens: list[str]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        i = 0
        while i + 4 < len(tokens):
            nome, custo, ca, peso, sb = tokens[i:i + 5]
            i += 5
            sb_num, sb_txt = _parse_sb(sb)
            ca_m = re.search(r"([+-]?\d+)", ca)
            notas = [int(x) for x in re.findall(r"\((\d+)\)", f"{nome} {ca}")]
            out.append({
                "id": _slugify(re.sub(r"\(\d+\)", "", nome)),
                "nome": nome,
                "custo": custo,
                "custo_pc": _parse_custo_pc(custo),
                "ca": int(ca_m.group(1)) if ca_m else None,
                "ca_texto": ca,
                "peso": peso,
                "sb": sb_num,
                "sb_texto": sb_txt,
                "notas": notas,
            })
        return _garantir_ids_unicos(out)

    # Elmos
    elmos_raw = fatiar(p2, "Tabela: Elmos", "* Os ajustes")[6:]
    elmos = parse_5col_ca(elmos_raw)

    # Armaduras
    arm_raw = fatiar(p2, "Tabela: Armaduras", "1 Grego,")[6:]
    armaduras = parse_5col_ca(arm_raw)

    # Escudos (junta 'Escudo, pequeno de' + 'madeira')
    esc_raw = fatiar(p2, "Tabela: Escudos", "1 Bônus")[6:]
    esc_norm: list[str] = []
    idx = 0
    while idx < len(esc_raw):
        if esc_raw[idx] == "Escudo, pequeno de" and idx + 1 < len(esc_raw) and esc_raw[idx + 1] == "madeira":
            esc_norm.append("Escudo, pequeno de madeira")
            idx += 2
        else:
            esc_norm.append(esc_raw[idx])
            idx += 1
    escudos = parse_5col_ca(esc_norm)

    # Armas Corpo a Corpo (pág 2 fim + pág 3 até '1Armas')
    armas_p2 = fatiar(p2, "Tabela: Armas")[6:]
    armas_p3 = fatiar(p3, "Gancho, Haste", "1Armas")
    armas_raw = armas_p2 + armas_p3
    # Normaliza quebras de linha em nomes compostos
    armas_norm: list[str] = []
    idx = 0
    while idx < len(armas_raw):
        tok = armas_raw[idx]
        if tok == "Espada, Cimitarra" and idx + 1 < len(armas_raw) and armas_raw[idx + 1].startswith("grande"):
            armas_norm.append(f"{tok} {armas_raw[idx + 1]}")
            idx += 2
        elif tok == "Machado, Mão/" and idx + 1 < len(armas_raw) and armas_raw[idx + 1].startswith("Arremesso"):
            armas_norm.append(f"{tok}{armas_raw[idx + 1]}")
            idx += 2
        else:
            armas_norm.append(tok)
            idx += 1

    armas_cc: list[dict[str, Any]] = []
    i = 0
    while i + 5 < len(armas_norm):
        nome, custo, dano, alc, peso, sb = armas_norm[i:i + 6]
        i += 6
        sb_num, sb_txt = _parse_sb(sb)
        notas = [int(x) for x in re.findall(r"\((\d+)\)", nome)]
        nome_limpo = re.sub(r"\s*\(\d+\)", "", nome).strip()
        armas_cc.append({
            "id": _slugify(nome_limpo),
            "nome": nome_limpo,
            "custo": custo,
            "custo_pc": _parse_custo_pc(custo),
            "dano": dano,
            "alcance": None if alc in {"—", "-"} else alc,
            "peso": peso,
            "sb": sb_num,
            "sb_texto": sb_txt,
            "notas": notas,
            "duas_maos": 10 in notas,
            "arma_de_haste": 12 in notas,
            "arremessavel": (alc not in {"—", "-"}) or (1 in notas),
        })
    armas_cc = _garantir_ids_unicos(armas_cc)

    # Armas de Projéteis (pág 3 entre 'Tabela: Armas de Projéteis' e 'Tabela: Transporte')
    proj_raw = fatiar(p3, "Tabela: Armas de Projéteis", "Tabela: Transporte")[2:]
    proj_norm: list[str] = []
    idx = 0
    while idx < len(proj_raw):
        tok = proj_raw[idx]
        if tok == "como" and idx + 1 < len(proj_raw) and proj_raw[idx + 1] in {"Arco", "Besta"}:
            proj_norm.append(f"como {proj_raw[idx + 1]}")
            idx += 2
        elif tok == "Arco, Longo" and idx + 1 < len(proj_raw) and proj_raw[idx + 1] == "Composto":
            proj_norm.append("Arco, Longo Composto")
            idx += 2
        else:
            proj_norm.append(tok)
            idx += 1

    armas_projeteis: list[dict[str, Any]] = []
    i = 0
    while i + 5 < len(proj_norm):
        nome, custo, dano, dist, peso, sb = proj_norm[i:i + 6]
        i += 6
        sb_num, sb_txt = _parse_sb(sb)
        armas_projeteis.append({
            "id": _slugify(nome),
            "nome": nome,
            "custo": custo,
            "custo_pc": _parse_custo_pc(custo),
            "dano": dano,
            "distancia": None if dist in {"—", "-"} else dist,
            "peso": peso,
            "sb": sb_num,
            "sb_texto": sb_txt,
            "municao": dano.lower().startswith("como "),
        })
    armas_projeteis = _garantir_ids_unicos(armas_projeteis)

    # Transporte e Arreios (pág 3 fim + pág 4 até '1 Cota de Montaria')
    trans_p3 = fatiar(p3, "Alforjes")
    trans_p4 = fatiar(p4, "Bote", "1 Cota de Montaria")
    trans_raw = trans_p3 + trans_p4
    transporte: list[dict[str, Any]] = []
    i = 0
    while i + 3 < len(trans_raw):
        nome, custo, peso, sb = trans_raw[i:i + 4]
        i += 4
        sb_num, sb_txt = _parse_sb(sb)
        notas = [int(x) for x in re.findall(r"\((\d+)\)", nome)]
        nome_limpo = re.sub(r"\s*\(\d+\)", "", nome).strip()
        transporte.append({
            "id": _slugify(nome_limpo),
            "nome": nome_limpo,
            "custo": custo,
            "custo_pc": _parse_custo_pc(custo),
            "peso": peso,
            "sb": sb_num,
            "sb_texto": sb_txt,
            "notas": notas,
        })
    transporte = _garantir_ids_unicos(transporte)

    # Equipamento Geral (pág 4 após 'Cap.' + pág 5 até 'Itens marcados com *')
    eq_p4 = fatiar(p4, "Água Benta, Frasco")
    eq_p5 = fatiar(p5, "Lanterna, Corta Luz", "Itens marcados com *")
    eq_raw = eq_p4 + eq_p5
    eq_norm: list[str] = []
    idx = 0
    while idx < len(eq_raw):
        if eq_raw[idx] == "Estojo para Mapas /" and idx + 1 < len(eq_raw) and eq_raw[idx + 1] == "Pergaminho":
            eq_norm.append("Estojo para Mapas / Pergaminho")
            idx += 2
        else:
            eq_norm.append(eq_raw[idx])
            idx += 1

    equipamento_geral: list[dict[str, Any]] = []
    i = 0
    while i + 4 < len(eq_norm):
        nome, custo, peso, sb, cap = eq_norm[i:i + 5]
        i += 5
        # Corrige notas de rodapé coladas em SB no PDF ('11' -> '1 (1)' em Cantil e Estojo para Mapas)
        if nome in {"Cantil", "Estojo para Mapas / Pergaminho"} and sb == "11":
            sb = "1 (1)"
        sb_num, sb_txt = _parse_sb(sb)
        notas = [int(x) for x in re.findall(r"\((\d+)\)", f"{nome} {sb}")]
        nome_limpo = re.sub(r"\s*\(\d+\)$", "", nome).strip().rstrip("-").strip()
        equipamento_geral.append({
            "id": _slugify(nome_limpo),
            "nome": nome_limpo,
            "custo": custo,
            "custo_pc": _parse_custo_pc(custo),
            "peso": peso,
            "sb": sb_num,
            "sb_texto": sb_txt,
            "capacidade": None if cap in {"—", "-"} else cap,
            "notas": notas,
        })
    equipamento_geral = _garantir_ids_unicos(equipamento_geral)

    # Roupas (pág 5 entre 'Anel de Sinete' e 'Itens marcados com *' da seção Roupas)
    i_r0 = p5.index("Anel de Sinete")
    i_r1 = p5.index("Tabela: Provisões e Alojamento") - 2
    roupas_raw = p5[i_r0:i_r1]
    roupas: list[dict[str, Any]] = []
    i = 0
    while i + 3 < len(roupas_raw):
        nome, custo, peso, sb = roupas_raw[i:i + 4]
        i += 4
        sb_num, sb_txt = _parse_sb(sb)
        roupas.append({
            "id": _slugify(nome),
            "nome": nome,
            "custo": custo,
            "custo_pc": _parse_custo_pc(custo),
            "peso": peso,
            "sb": sb_num,
            "sb_texto": sb_txt,
        })
    roupas = _garantir_ids_unicos(roupas)

    # Provisões e Alojamento (pág 5 fim + pág 6 até 'SOBRECARGA (SB)')
    prov_p5 = fatiar(p5, "Cerveja Ale, Caneca")
    prov_p6 = fatiar(p6, "Rações (1 dia)", "SOBRECARGA (SB)")
    prov_raw = prov_p5 + prov_p6
    provisoes: list[dict[str, Any]] = []
    i = 0
    while i + 3 < len(prov_raw):
        nome, custo, peso, sb = prov_raw[i:i + 4]
        i += 4
        sb_num, sb_txt = _parse_sb(sb)
        provisoes.append({
            "id": _slugify(nome),
            "nome": nome,
            "custo": custo,
            "custo_pc": _parse_custo_pc(custo),
            "peso": peso,
            "sb": sb_num,
            "sb_texto": sb_txt,
        })
    provisoes = _garantir_ids_unicos(provisoes)

    return {
        "elmos": elmos,
        "armaduras": armaduras,
        "escudos": escudos,
        "armas_corpo_a_corpo": armas_cc,
        "armas_projeteis": armas_projeteis,
        "transporte_e_arreios": transporte,
        "equipamento_geral": equipamento_geral,
        "roupas": roupas,
        "provisoes_e_alojamento": provisoes,
    }


def construir_equipamentos() -> dict[str, Any]:
    """Monta o dicionário completo de `dados/dadosc&c/equipamentos.json`."""
    tabelas = _construir_de_linhas_texto()
    return {
        "metadados": {
            "sistema": "Castles & Crusades",
            "edicao": "1ª Edição Brasileira (Livro do Jogador)",
            "arquivo_fonte": "ref/cc/Equipamentos_e_Sobrecarga_C&C.pdf",
            "paginas_livro": "104–111",
            "total_paginas_pdf": 8,
            "versao_schema": 1,
            "idioma": "pt-BR",
        },
        "moedas": {
            "conversao": {
                "1_platina_em_ouro": 10,
                "1_ouro_em_prata": 10,
                "1_prata_em_cobre": 10,
                "valores_em_pc": {"pc": 1, "pp": 10, "po": 100, "pl": 1000},
            },
            "peso_e_sobrecarga": {
                "peso_por_moeda_g": 28,
                "moedas_por_450g": 16,
                "moedas_por_1_sb": 160,
                "regra": "450 g (16 moedas) não têm SB apreciável; 4,5 kg (160 moedas) equivalem a 1 SB.",
            },
            "ouro_inicial_por_classe": {
                "combatente": {"rolagem": "3d8x10", "min_po": 30, "max_po": 240},
                "explorador": {"rolagem": "3d8x10", "min_po": 30, "max_po": 240},
                "trapaceiro": {"rolagem": "3d4x10", "min_po": 30, "max_po": 120},
                "assassino": {"rolagem": "3d4x10", "min_po": 30, "max_po": 120},
                "bardo": {"rolagem": "3d4x10", "min_po": 30, "max_po": 120},
                "barbaro": {"rolagem": "2d4x10", "min_po": 20, "max_po": 80},
                "lutador": {"rolagem": "2d4x10", "min_po": 20, "max_po": 80},
                "mago": {"rolagem": "1d10x10", "min_po": 10, "max_po": 100},
                "ilusionista": {"rolagem": "1d10x10", "min_po": 10, "max_po": 100},
                "clerigo": {"rolagem": "2d10x10", "min_po": 20, "max_po": 200},
                "druida": {"rolagem": "2d10x10", "min_po": 20, "max_po": 200},
                "cavaleiro": {"rolagem": "6d4x10", "min_po": 60, "max_po": 240},
                "paladino": {"rolagem": "6d4x10", "min_po": 60, "max_po": 240},
            },
        },
        "notas_tabelas": {
            "elmos": (
                "Os ajustes de CA dos elmos aplicam-se apenas a ataques direcionados à cabeça, não afetando a CA geral. "
                "Elmos incluídos sem custo adicional: Cota de Escamas (Coifa de Couro), Cota de Malha (Coifa de Malha), "
                "Armadura de Placas (Elmo Normal), Armadura Completa e Hussarda Polonesa (Elmo Grande)."
            ),
            "armaduras": {
                "1": "Grego: grevas de bronze, braçais, peitoral e elmo médio.",
                "2": "Grego: grevas, braçais, peitoral e elmo médio, de ferro.",
                "3": "Romano: armadura de escamas, grevas e braçais de cobre, elmo de cobre.",
                "4": "Romano: armadura segmentada, grevas e braçais de ferro, elmo de ferro.",
            },
            "escudos": {
                "1": "Bônus de CA aplicado apenas contra 1 oponente por turno.",
                "2": "Bônus de CA aplicado apenas contra 2 oponentes por turno.",
                "3": "Bônus de CA aplicado apenas contra 3 oponentes por turno.",
                "4": "Pavis: apoiado no chão como parede móvel; bônus de CA (+6) afeta todos os inimigos à frente.",
            },
            "armas_corpo_a_corpo": {
                "1": "Armas corpo a corpo com alcance podem ser usadas como armas de arremesso/projétil.",
                "2": "+2 para acertar contra armaduras de malha, placas ou escamas.",
                "3": "Pode funcionar como arma corpo a corpo ou conceder +1 na CA (escolhido no início do turno).",
                "4": "Pode prender inimigos médios ou pequenos (declarado antes; superar CA 15 + nível; alvo livre com teste DES sofrendo 1d4 dano).",
                "5": "+3 para desarmar oponentes (se proficiente).",
                "6": "Corpo a corpo, desarmar ou subjugar (+3 para desarmar/subjugar, declarado antes).",
                "7": "Causa o dobro do dano em investida montada.",
                "8": "Causa o dobro do dano se firmada para receber uma investida.",
                "9": "Causa 1d12 de dano quando empunhada com as duas mãos.",
                "10": "Deve ser usada com as duas mãos.",
                "11": "Alcance estendido de 3 metros.",
                "12": "Considerada arma de haste.",
            },
            "cota_montaria_ponei": "Para pônei, custa metade do preço, tem 2/3 do peso e reduz a SB em 1 ponto.",
            "equipamento_geral": {
                "*": "Sem SB apreciável; se carregar mais de 10 unidades, conte 1 SB a cada 10 itens.",
                "1": "SB listada para o item cheio; se vazio, reduza a SB em 2 (mínimo 1).",
                "2": "Personagem de tamanho humano pode levar no cinto no máximo 2 bolsas grandes e 1 bolsa pequena.",
            },
        },
        **tabelas,
        "regras_sobrecarga": {
            "paginas_livro": "109–111",
            "formula_categoria_sobrecarga": {
                "base": "pontuacao_de_forca",
                "bonus_um_primario_for_ou_con": 3,
                "bonus_ambos_primarios_for_e_con": 6,
            },
            "categorias": [
                {
                    "id": "descarregado",
                    "nome": "Descarregado",
                    "limite": "Até 1× CS",
                    "efeito": "Sem efeitos.",
                },
                {
                    "id": "carregado",
                    "nome": "Carregado",
                    "limite": "Mais que 1× CS até 3× CS",
                    "efeito": "-3 m no Movimento (mínimo 1,5 m) e +2 no ND de todos os testes baseados em Destreza.",
                },
                {
                    "id": "sobrecarregado",
                    "nome": "Sobrecarregado",
                    "limite": "Mais que 3× CS",
                    "efeito": "Movimento reduzido para 1,5 m por rodada, falha automática em testes baseados em Destreza e perde o bônus de Destreza na CA.",
                },
            ],
            "itens_de_capacidade": (
                "Carregam um número de itens igual à sua Capacidade, desde que cada item interno tenha SB estritamente menor que a Capacidade. "
                "Itens dentro de um Item de Capacidade não somam sua SB ao total do personagem — conta-se apenas a SB do próprio recipiente."
            ),
            "modificadores_itens_nao_listados": {
                "peso": [
                    {"categoria": "Muito Leve", "modificador": "-2 SB", "nota": "< 0,4 kg"},
                    {"categoria": "Leve", "modificador": "-1 SB", "nota": "até 2,7 kg"},
                    {"categoria": "Pesado", "modificador": "+3 SB", "nota": "até 11 kg"},
                    {"categoria": "Muito Pesado", "modificador": "+5 SB", "nota": "> 11 kg"},
                ],
                "volume": [
                    {"categoria": "Equilibrado", "modificador": "-1 SB", "exemplo": "Várias armas"},
                    {"categoria": "Volumoso", "modificador": "×2 SB", "exemplo": "Barril, objetos > metade de um humano"},
                    {"categoria": "Disforme", "modificador": "-1 SB", "exemplo": "Roupas, formas mutáveis"},
                    {"categoria": "Estreito", "modificador": "×½ SB", "exemplo": "< 5 cm de largura"},
                ],
            },
        },
        "itens_obra_prima": {
            "armas": {
                "obra_prima": {"multiplicador_custo": 10, "beneficio": "+1 para acertar OU +1 para dano (não mágico)."},
                "obra_prima_superior": {"multiplicador_custo": 25, "beneficio": "+1 para acertar E +1 para dano (não mágico)."},
            },
            "armaduras": {
                "obra_prima": {"multiplicador_custo": 10, "beneficio": "+1 na CA."},
                "obra_prima_superior": {"multiplicador_custo": 25, "beneficio": "Absorve 1 ponto de dano de um único golpe."},
            },
        },
    }


def validar_equipamentos(dados: dict[str, Any]) -> None:
    """Valida contagens exatas, unicidade de IDs e cruzamento de classes com `introducao.json`."""
    assert dados["metadados"]["sistema"] == "Castles & Crusades"

    intro = json.loads((DIR_DADOS_CC / "introducao.json").read_text(encoding="utf-8"))
    ids_classes_intro = {c["id"] for c in intro["classes_introducao"]["classes"]}
    assert set(dados["moedas"]["ouro_inicial_por_classe"].keys()) == ids_classes_intro

    esperados = {
        "elmos": 11,
        "armaduras": 25,
        "escudos": 8,
        "armas_corpo_a_corpo": 72,
        "armas_projeteis": 19,
        "transporte_e_arreios": 32,
        "equipamento_geral": 107,
        "roupas": 29,
        "provisoes_e_alojamento": 18,
    }
    for cat, minimo in esperados.items():
        lista = dados[cat]
        assert len(lista) >= minimo, f"Categoria {cat} esperava >= {minimo}, obteve {len(lista)}"
        ids = [x["id"] for x in lista]
        assert len(ids) == len(set(ids)), f"IDs duplicados em {cat}"

    # Checagens pontuais de fidelidade
    elmos_id = {x["id"]: x for x in dados["elmos"]}
    assert elmos_id["armete"]["ca"] == 6 and elmos_id["armete"]["custo_pc"] == 1000

    arm_id = {x["id"]: x for x in dados["armaduras"]}
    assert arm_id["armadura_completa"]["ca"] == 8 and arm_id["armadura_completa"]["custo_pc"] == 100000
    assert arm_id["armadura_de_couro"]["ca"] == 2 and arm_id["armadura_de_couro"]["sb"] == 2

    esc_id = {x["id"]: x for x in dados["escudos"]}
    assert esc_id["pavis"]["ca"] == 6 and esc_id["pavis"]["sb"] == 12

    cc_id = {x["id"]: x for x in dados["armas_corpo_a_corpo"]}
    assert cc_id["espada_longa"]["dano"] == "1d8" and cc_id["espada_longa"]["custo_pc"] == 1500
    assert cc_id["espada_duas_maos"]["dano"] == "2d6" and cc_id["espada_duas_maos"]["duas_maos"] is True

    proj_id = {x["id"]: x for x in dados["armas_projeteis"]}
    assert proj_id["arco_longo"]["dano"] == "1d6" and proj_id["besta_pesada"]["dano"] == "1d10"

    eq_id = {x["id"]: x for x in dados["equipamento_geral"]}
    assert eq_id["mochila"]["sb"] == 2 and eq_id["mochila"]["capacidade"] == "8"
    assert eq_id["cantil"]["sb"] == 1


def main() -> None:
    """Gera `dados/dadosc&c/equipamentos.json`, recarrega do disco e valida."""
    dados = construir_equipamentos()
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_SAIDA.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    recarregado = json.loads(CAMINHO_SAIDA.read_text(encoding="utf-8"))
    validar_equipamentos(recarregado)
    cats = (
        "elmos", "armaduras", "escudos", "armas_corpo_a_corpo", "armas_projeteis",
        "transporte_e_arreios", "equipamento_geral", "roupas", "provisoes_e_alojamento",
    )
    resumo = " | ".join(f"{c}: {len(recarregado[c])}" for c in cats)
    total = sum(len(recarregado[c]) for c in cats)
    print(f"OK — {CAMINHO_SAIDA.relative_to(RAIZ_PROJETO)} gerado e validado com sucesso! ({total} itens)")
    print(resumo)


if __name__ == "__main__":
    main()
