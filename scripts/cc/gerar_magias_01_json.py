"""Gera dados/dadosc&c/magias01.json a partir de ref/cc/Magias 01.pdf (pp. 113-147).

Extrai:
1. Regras gerais de magia (pp. 113-121, 132)
2. Listas completas de feitiços por classe (Clérigo, Druida, Mago, Ilusionista; níveis 0-9; pp. 122-131)
3. Descrições completas de feitiços de A a C (pp. 133-147)

Execução:
    .venv\\Scripts\\python.exe scripts/cc/gerar_magias_01_json.py
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import pymupdf

RAIZ = Path(__file__).resolve().parents[2]
PDF_PATH = RAIZ / "ref" / "cc" / "Magias 01.pdf"
SAIDA_PATH = RAIZ / "dados" / "dadosc&c" / "magias01.json"

# Palavras compostas que mantêm hífen mesmo quando a quebra de linha cai logo após o hífen.
PREFIXOS_HIFEN_REAL = {
    "alterar",
    "arco",
    "auto",
    "bem",
    "contra",
    "guarda",
    "mal",
    "meio",
    "morto",
    "mortos",
    "nao",
    "não",
    "pós",
    "pos",
    "pré",
    "pre",
    "recém",
    "recem",
    "semi",
    "sub",
    "super",
    "vice",
}

SUFIXOS_HIFEN_REAL = {
    "se",
    "me",
    "te",
    "nos",
    "vos",
    "o",
    "a",
    "os",
    "as",
    "lo",
    "la",
    "los",
    "las",
    "lhe",
    "lhes",
    "vivos",
    "vivo",
    "sucedido",
    "sucedida",
    "sucedidos",
    "sucedidas",
    "íris",
    "iris",
}


def slugify(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    limpo = re.sub(r"[^a-zA-Z0-9]+", "_", sem_acento.lower()).strip("_")
    return limpo


def limpar_espacos(texto: str) -> str:
    texto = texto.replace("\u200b", "").replace("\ufeff", "").replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto.strip()


def desfazer_hifenizacao(texto: str) -> str:
    """Junta linhas quebradas removendo hífens de translineação, preservando hífens reais."""
    texto = texto.replace("\u200b", "").replace("\xa0", " ")

    def _subst(match: re.Match[str]) -> str:
        antes = match.group(1)
        depois = match.group(2)
        if antes.lower() in PREFIXOS_HIFEN_REAL or depois.lower() in SUFIXOS_HIFEN_REAL:
            return f"{antes}-{depois}"
        return f"{antes}{depois}"

    # Hífen seguido de quebra de linha e letra minúscula
    texto = re.sub(r"([A-Za-zÀ-ÿ]+)-\s*\n\s*([a-zà-ÿ]+)", _subst, texto)
    # Quebras de linha simples viram espaço
    texto = re.sub(r"\s*\n\s*", " ", texto)
    return limpar_espacos(texto)


def normalizar_classe(nome: str) -> str:
    chave = slugify(nome)
    mapa = {
        "clerigo": "clerigo",
        "druida": "druida",
        "mago": "mago",
        "ilusionista": "ilusionista",
    }
    if chave not in mapa:
        raise ValueError(f"Classe desconhecida: {nome!r}")
    return mapa[chave]


def extrair_regras_gerais() -> dict[str, Any]:
    """Estrutura fiel das regras gerais de magia (pp. 113-121 e 132)."""
    return {
        "paginas_livro": "113-121, 132",
        "tipos_magia": {
            "arcana": {
                "classes": ["mago", "ilusionista"],
                "descricao": (
                    "Manipulação direta da magia inata ao mundo por estudo, prática e "
                    "grimórios. Exige preparação prévia e componentes."
                ),
            },
            "divina": {
                "classes": ["clerigo", "druida"],
                "descricao": (
                    "Canalizada a partir de divindades (clérigos) ou da natureza (druidas) "
                    "por meio de oração e meditação; não usa grimório."
                ),
            },
            "ilusao": {
                "classe": "ilusionista",
                "observacoes": (
                    "Em Castles & Crusades a magia de ilusão não depende da crença do alvo; "
                    "muitos feitiços têm efeitos reais e tangíveis moldados pelo poder do ilusionista."
                ),
                "ilusionista_e_cura": (
                    "Ilusionistas podem curar dano projetando seu próprio poder mágico no alvo "
                    "e alterando a natureza do tempo e da substância, usando a mente do alvo "
                    "como ponte."
                ),
            },
        },
        "preparacao_e_conjuracao": {
            "preparacao_arcana": (
                "Exige 8 horas de descanso (incluindo sono) mais tempo de estudo do grimório "
                "para preparar os feitiços do dia até o limite da tabela da classe."
            ),
            "preparacao_divina": (
                "Exige 8 horas de descanso e oração/meditação diária; conjuradores divinos têm "
                "acesso a toda a lista de sua classe para os níveis que podem conjurar."
            ),
            "grimorios": (
                "Magos e ilusionistas registram feitiços arcanos em grimórios. Decifrar escritos "
                "arcanos de outro conjurador exige o feitiço Decifrar Escrita Arcana (Ler Escrita Arcana)."
            ),
            "adquirir_e_copiar_feiticos": (
                "Feitiços podem ser copiados de pergaminhos ou outros grimórios após decifração; "
                "copiar de um pergaminho não o destrói. Conjuradores divinos podem decifrar e "
                "aprender novos feitiços de pergaminhos divinos estudando 1 dia + 1 dia por nível do feitiço."
            ),
            "concentracao": (
                "Conjurar exige concentração. Sofrer dano, falhar em jogada de proteção ou "
                "sofrer distração severa durante o lançamento interrompe e desperdiça o feitiço "
                "(o GC pode permitir teste de concentração, geralmente Inteligência ou Destreza). "
                "Agarrado ou amarrado só conjura se exigir apenas fala (ou fala + componente em mãos)."
            ),
            "pergaminhos": {
                "uso": (
                    "Contêm todos os componentes exceto a fala. Exigem decifração prévia "
                    "(Decifrar Escrita Arcana para arcanos), pertencer à classe compatível e "
                    "ler em voz alta. Uso único (o feitiço desaparece ou destrói o pergaminho)."
                ),
                "nivel_acima": (
                    "Conjurar feitiço de nível acima da capacidade atual exige teste de "
                    "Inteligência com penalidade/ND igual ao nível do feitiço; falha arruína "
                    "o feitiço e destrói o pergaminho."
                ),
            },
        },
        "terminologia": {
            "tempo_conjuracao": (
                "Normalmente 1 rodada (10 segundos). Feitiços complexos podem levar várias "
                "rodadas (rd), minutos (min), turnos (tn = 1 min = 6 rd), horas (hr) ou dias (d)."
            ),
            "alcance": (
                "Distância máxima do conjurador ao alvo ou ponto de origem: pessoal (próprio), "
                "toque, distância em metros ou ilimitado (no plano atual)."
            ),
            "alvo_e_area_efeito": {
                "feiticos_alvo": (
                    "Direcionados a criaturas, itens ou áreas específicas; exigem visão ou toque "
                    "no escuro. O conjurador como alvo não faz JP nem aplica RM."
                ),
                "categorias_area": [
                    "Explosão (irradia de um ponto central)",
                    "Cone (origina-se no conjurador; largura igual à distância)",
                    "Cilindro (círculo horizontal expandido verticalmente)",
                    "Emanação (irradia continuamente durante a duração)",
                    "Raio (age como ataque à distância; bloqueado por objetos sólidos)",
                ],
                "obstaculos": (
                    "Explosões, cones, cilindros e emanações são bloqueados por barreiras sólidas, "
                    "exigindo abertura de ao menos 1 pé quadrado para contornar."
                ),
            },
            "duracao": (
                "Medida em rodadas (R), minutos, horas (H), dias (D), semanas (S), meses (M), "
                "anos (A), instantânea ou permanente. Feitiços pessoais podem ser dispensados à vontade."
            ),
            "jogada_protecao": {
                "nivel_desafio": "Igual ao nível do conjurador, salvo indicação contrária.",
                "resultados": {
                    "anula": "Nega completamente os efeitos do feitiço.",
                    "parcial": "Reduz ou limita os efeitos.",
                    "metade": "Reduz o dano à metade (arredondado para baixo).",
                    "nenhum": "Não permite jogada de proteção (padrão quando omitido).",
                    "objeto": "Objeto recebe JP se for mágico ou se o feitiço exigir.",
                    "inofensivo": "Indicado por (i) ou (h); alvo pode fazer JP se desejar ou abdicar.",
                },
            },
            "resistencia_magia": (
                "Funciona como CA contra magia (mínimo 1). Conjurador rola 1d20 >= RM do alvo "
                "para o feitiço afetá-lo; aplicada antes da JP. Pode ser suprimida voluntariamente. "
                "Se omitida na descrição, não se aplica."
            ),
            "componentes": {
                "fala": "Invocação verbal (palavra, frase, estrofe ou poema).",
                "gestual": "Movimentos com mãos e dedos; exige uma mão livre.",
                "material": "Item físico consumido/destruído durante a conjuração.",
                "foco": "Item físico que canaliza o feitiço e não é destruído.",
                "simbolo_sagrado": (
                    "Exigido apenas para conjuradores divinos (símbolo religioso para clérigos; "
                    "plantas/visco/azevinho para druidas, a critério do GC)."
                ),
            },
            "reversivel": "Feitiços marcados com asterisco (*) possuem uma versão reversa.",
        },
    }


def _blocos_ordenados_pagina(page: pymupdf.Page) -> list[tuple[int, float, float, str]]:
    mid = page.rect.width / 2.0
    h = page.rect.height
    itens: list[tuple[int, float, float, str]] = []
    for blk in page.get_text("blocks"):
        if blk[6] != 0:
            continue
        x0, y0, x1, y1, texto = blk[0], blk[1], blk[2], blk[3], blk[4]
        if y0 <= 42 or y0 >= h - 42:
            continue
        limpo = texto.strip()
        if not limpo:
            continue
        if limpo in {"FEITIÇOS", "MAGIA", "LISTAS DE FEITIÇOS"}:
            continue
        if "CASTLES & CRUSADES" in limpo or "LIVRO DO JOGADOR" in limpo:
            continue
        if limpo.startswith("MAGIA -") or limpo.startswith("MAGIA –"):
            continue
        col = 0 if (x0 + x1) / 2.0 < mid else 1
        itens.append((col, y0, x0, limpo))
    itens.sort(key=lambda t: (t[0], t[1], t[2]))
    return itens


def extrair_listas_por_classe(doc: pymupdf.Document) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Extrai todas as 4 listas de feitiços (níveis 0 a 9) das páginas 10-19 (pp. 122-131)."""
    listas: dict[str, dict[str, list[dict[str, Any]]]] = {
        "clerigo": {},
        "druida": {},
        "mago": {},
        "ilusionista": {},
    }

    classe_atual: str | None = None
    nivel_atual: str | None = None

    re_classe = re.compile(r"^FEITIÇOS DE (CLÉRIGO|DRUIDA|MAGO|ILUSIONISTA)", re.IGNORECASE)
    re_nivel = re.compile(
        r"^FEITIÇOS? DE NÍVEL (\d)\s+DE\s+(CLÉRIGO|DRUIDA|MAGO|ILUSIONISTA)",
        re.IGNORECASE,
    )
    re_num_inicio = re.compile(r"^(\d{1,2})\.?\s*\n(.*)$", re.DOTALL)
    re_pagina_fim = re.compile(r"^(.*?)\s+(\d{3})$", re.DOTALL)

    for pno in range(9, 19):  # P10..P19 (pp. 122..131)
        page = doc[pno]
        blocos = _blocos_ordenados_pagina(page)

        # Pré-agrupar linhas/blocos para lidar com números de página isolados ou entradas quebradas
        i = 0
        while i < len(blocos):
            col, y0, x0, texto = blocos[i]
            primeira_linha = texto.splitlines()[0].strip()

            # Cabeçalho de nível? (checar antes de cabeçalho de classe)
            m_niv = re_nivel.match(primeira_linha)
            if m_niv:
                nivel_atual = m_niv.group(1)
                classe_atual = normalizar_classe(m_niv.group(2))
                listas[classe_atual].setdefault(nivel_atual, [])
                # Pode haver resto do bloco após o cabeçalho?
                resto_linhas = [ln.strip() for ln in texto.splitlines()[1:] if ln.strip()]
                # Ignorar "(TRUQUES)" etc.
                resto_linhas = [ln for ln in resto_linhas if not ln.startswith("(")]
                if not resto_linhas:
                    i += 1
                    continue
                texto = "\n".join(resto_linhas)
                primeira_linha = texto.splitlines()[0].strip()

            m_cls = re_classe.match(primeira_linha)
            if m_cls and not re_nivel.match(primeira_linha):
                classe_atual = normalizar_classe(m_cls.group(1))
                # Verifica se a segunda linha já traz o cabeçalho de nível
                resto_linhas = [ln.strip() for ln in texto.splitlines()[1:] if ln.strip()]
                if resto_linhas:
                    m_niv2 = re_nivel.match(resto_linhas[0])
                    if m_niv2:
                        nivel_atual = m_niv2.group(1)
                        classe_atual = normalizar_classe(m_niv2.group(2))
                        listas[classe_atual].setdefault(nivel_atual, [])
                i += 1
                continue

            if primeira_linha.startswith("(") and primeira_linha.endswith(")"):
                i += 1
                continue

            # Bloco contendo apenas número de página pertencente ao feitiço anterior
            if re.fullmatch(r"\d{3}", texto):
                if classe_atual and nivel_atual and listas[classe_atual][nivel_atual]:
                    ultimo = listas[classe_atual][nivel_atual][-1]
                    if ultimo["pagina_livro"] is None:
                        ultimo["pagina_livro"] = int(texto)
                i += 1
                continue

            # Entrada de feitiço (pode conter mais de uma entrada no mesmo bloco? Normalmente 1)
            m_ent = re_num_inicio.match(texto)
            if m_ent and classe_atual and nivel_atual is not None:
                numero = int(m_ent.group(1))
                corpo = m_ent.group(2).strip()
                linhas_corpo = [limpar_espacos(ln) for ln in corpo.splitlines() if limpar_espacos(ln)]

                pagina_livro: int | None = None
                if linhas_corpo and re.fullmatch(r"\d{3}", linhas_corpo[-1]):
                    pagina_livro = int(linhas_corpo.pop())
                elif linhas_corpo:
                    m_pg = re_pagina_fim.match(linhas_corpo[-1])
                    if m_pg:
                        linhas_corpo[-1] = m_pg.group(1).strip()
                        pagina_livro = int(m_pg.group(2))

                if not linhas_corpo:
                    i += 1
                    continue

                nome_bruto = linhas_corpo[0].rstrip(".").strip()
                # Se o resumo veio no próximo bloco (quando o nome era muito longo ou tabulado)
                resumo_linhas = linhas_corpo[1:]

                # Verificar se o próximo bloco é continuação (não começa com número nem FEITIÇO)
                while i + 1 < len(blocos) and blocos[i + 1][0] == col:
                    prox_txt = blocos[i + 1][3]
                    prox_l0 = prox_txt.splitlines()[0].strip()
                    if (
                        re_nivel.match(prox_l0)
                        or re_classe.match(prox_l0)
                        or re_num_inicio.match(prox_txt)
                    ):
                        break
                    if re.fullmatch(r"\d{3}", prox_txt):
                        if pagina_livro is None:
                            pagina_livro = int(prox_txt)
                            i += 1
                            continue
                        break
                    # Caso de número isolado no próximo bloco (ex: "12." seguido de nome em outro bloco)
                    if re.fullmatch(r"\d{1,2}\.?", prox_txt):
                        break
                    # Caso contrário, é continuação do resumo (ou página no fim)
                    if pagina_livro is None:
                        extra_linhas = [limpar_espacos(ln) for ln in prox_txt.splitlines() if limpar_espacos(ln)]
                        if extra_linhas and re.fullmatch(r"\d{3}", extra_linhas[-1]):
                            pagina_livro = int(extra_linhas.pop())
                        resumo_linhas.extend(extra_linhas)
                        i += 1
                        continue
                    break

                reversivel = nome_bruto.endswith("*")
                nome_limpo = nome_bruto.rstrip("*").strip()
                resumo = limpar_espacos(" ".join(resumo_linhas))

                listas[classe_atual][nivel_atual].append(
                    {
                        "numero": numero,
                        "id": slugify(nome_limpo),
                        "nome": nome_limpo,
                        "reversivel": reversivel,
                        "resumo": resumo,
                        "pagina_livro": pagina_livro,
                    }
                )
                i += 1
                continue

            # Caso raro: número sozinho em um bloco ("12.") e nome+resumo no bloco seguinte
            if re.fullmatch(r"\d{1,2}\.?", texto) and i + 1 < len(blocos) and classe_atual and nivel_atual is not None:
                numero = int(texto.rstrip("."))
                prox_txt = blocos[i + 1][3]
                linhas_corpo = [limpar_espacos(ln) for ln in prox_txt.splitlines() if limpar_espacos(ln)]
                pagina_livro = None
                if linhas_corpo and re.fullmatch(r"\d{3}", linhas_corpo[-1]):
                    pagina_livro = int(linhas_corpo.pop())
                nome_bruto = linhas_corpo[0].rstrip(".").strip() if linhas_corpo else ""
                reversivel = nome_bruto.endswith("*")
                nome_limpo = nome_bruto.rstrip("*").strip()
                resumo = limpar_espacos(" ".join(linhas_corpo[1:]))
                listas[classe_atual][nivel_atual].append(
                    {
                        "numero": numero,
                        "id": slugify(nome_limpo),
                        "nome": nome_limpo,
                        "reversivel": reversivel,
                        "resumo": resumo,
                        "pagina_livro": pagina_livro,
                    }
                )
                i += 2
                continue

            i += 1

    return listas


def parse_cabecalho_magia(texto_cabecalho: str) -> tuple[str, bool, dict[str, int]]:
    """Extrai (nome, reversivel, classes_niveis) de um título de magia."""
    limpo = limpar_espacos(texto_cabecalho).rstrip(".")
    # Encontra a primeira ocorrência de nome de classe + nível (com ou sem "Feitiço de ")
    m_cls = re.search(
        r"(?:[-–,]\s*)?(?:feiti[çc]o\s+de\s+)?(cl[eé]rigo|druida|mago|ilusionista)\s+\d+",
        limpo,
        re.IGNORECASE,
    )
    if not m_cls:
        raise ValueError(f"Cabeçalho de magia inválido: {texto_cabecalho!r}")

    nome_bruto = limpo[: m_cls.start()].strip().rstrip("-–,").strip()
    parte_classes = limpo[m_cls.start() :]

    reversivel = "*" in nome_bruto
    nome = nome_bruto.replace("*", "").strip()

    classes_niveis: dict[str, int] = {}
    for m in re.finditer(
        r"(cl[eé]rigo|druida|mago|ilusionista)\s+(\d+)",
        parte_classes,
        re.IGNORECASE,
    ):
        cls = normalizar_classe(m.group(1))
        niv = int(m.group(2))
        classes_niveis[cls] = niv

    if not classes_niveis:
        raise ValueError(f"Sem classes/níveis no cabeçalho: {texto_cabecalho!r}")

    return nome, reversivel, classes_niveis


def extrair_descricoes_magias(doc: pymupdf.Document) -> list[dict[str, Any]]:
    """Extrai todas as descrições de feitiços (A-C) das páginas 21-35 (pp. 133-147)."""
    # Cada bloco ordenado de P21..P35 é classificado como:
    # - titulo_magia (fonte BookmanOldStyle-Bold-SC7)
    # - tabela_titulo / tabela_conteudo (Tabela: Confusão)
    # - corpo (parágrafo narrativo, mecânico, componentes ou reverso)
    eventos: list[dict[str, Any]] = []

    for pno in range(20, 35):  # P21..P35 (pp. 133..147)
        pagina_livro = 113 + pno  # P21 (idx 20) = p. 133
        page = doc[pno]
        mid = page.rect.width / 2.0
        h = page.rect.height
        d = page.get_text("dict")

        blocos_pag = []
        for b in d["blocks"]:
            if b.get("type") != 0:
                continue
            x0, y0, x1, y1 = b["bbox"]
            if y0 <= 42 or y0 >= h - 42:
                continue
            col = 0 if (x0 + x1) / 2.0 < mid else 1
            blocos_pag.append((col, y0, x0, b))
        blocos_pag.sort(key=lambda t: (t[0], t[1], t[2]))

        for col, y0, x0, b in blocos_pag:
            linhas_txt: list[str] = []
            fontes_primeira: set[str] = set()
            fontes_todas: set[str] = set()
            for idx_l, l in enumerate(b["lines"]):
                spans = [s for s in l["spans"] if s["text"].strip()]
                if not spans:
                    continue
                txt_l = "".join(s["text"] for s in l["spans"])
                linhas_txt.append(txt_l)
                for s in spans:
                    fontes_todas.add(s["font"])
                    if idx_l == 0:
                        fontes_primeira.add(s["font"])

            if not linhas_txt:
                continue

            texto_bruto = "\n".join(linhas_txt).strip()
            if not texto_bruto:
                continue
            if texto_bruto in {"FEITIÇOS", "MAGIA", "A", "B", "C", "DESCRIÇÃO DOS FEITIÇOS"}:
                continue
            if texto_bruto.startswith("DESCRIÇÃO DOS FEITIÇOS"):
                continue
            if "CASTLES & CRUSADES" in texto_bruto or "LIVRO DO JOGADOR" in texto_bruto:
                continue
            if texto_bruto.startswith("MAGIA -") or texto_bruto.startswith("MAGIA –"):
                continue

            is_titulo = any("BookmanOldStyle-Bold-SC7" in f for f in fontes_primeira)
            is_tabela_titulo = texto_bruto.startswith("Tabela:")

            eventos.append(
                {
                    "pagina_livro": pagina_livro,
                    "col": col,
                    "y0": y0,
                    "is_titulo": is_titulo,
                    "is_tabela_titulo": is_tabela_titulo,
                    "texto_bruto": texto_bruto,
                    "fontes": fontes_todas,
                }
            )

    # Agrupar eventos por magia
    magias_brutas: list[dict[str, Any]] = []
    atual: dict[str, Any] | None = None

    for ev in eventos:
        if ev["is_titulo"]:
            if atual is not None:
                magias_brutas.append(atual)
            nome, reversivel, classes_niveis = parse_cabecalho_magia(ev["texto_bruto"])
            atual = {
                "nome": nome,
                "reversivel": reversivel,
                "classes_niveis": classes_niveis,
                "pagina_livro": ev["pagina_livro"],
                "blocos": [],
            }
        else:
            if atual is not None:
                atual["blocos"].append(ev)

    if atual is not None:
        magias_brutas.append(atual)

    # Processar cada magia agrupada
    magias_finais: list[dict[str, Any]] = []
    for mb in magias_brutas:
        blocos = mb["blocos"]
        paragrafos: list[str] = []
        tabela_extra: dict[str, Any] | None = None

        # Detectar se há "Tabela: ..." (caso de Confusão)
        i = 0
        while i < len(blocos):
            ev = blocos[i]
            if ev["is_tabela_titulo"]:
                titulo_tab = limpar_espacos(ev["texto_bruto"])
                linhas_tab: list[str] = []
                i += 1
                # Coleta blocos da tabela até encontrar parágrafo normal (GoudyOldStyleBT-Roman longo)
                while i < len(blocos):
                    t_b = blocos[i]["texto_bruto"]
                    if t_b.startswith("Criaturas que ") or t_b.startswith("Componentes de "):
                        break
                    linhas_tab.extend([limpar_espacos(ln) for ln in t_b.splitlines() if limpar_espacos(ln)])
                    i += 1
                # Monta pares (rolagem, comportamento) para Tabela: Confusão
                entradas_tab = []
                # Remove cabeçalho "1d10" / "Comportamento"
                limpas = [x for x in linhas_tab if x not in {"1d10", "Comportamento", "1d10 Comportamento"}]
                j = 0
                while j + 1 < len(limpas):
                    if re.fullmatch(r"\d+(?:-\d+)?", limpas[j]):
                        entradas_tab.append({"rolagem": limpas[j], "efeito": limpas[j + 1]})
                        j += 2
                    else:
                        # Linha já combinada "1 Vagueia..."
                        m_row = re.match(r"^(\d+(?:-\d+)?)\s+(.+)$", limpas[j])
                        if m_row:
                            entradas_tab.append({"rolagem": m_row.group(1), "efeito": m_row.group(2)})
                        j += 1
                tabela_extra = {"titulo": titulo_tab, "dado": "1d10", "entradas": entradas_tab}
                continue

            txt_limpo = desfazer_hifenizacao(ev["texto_bruto"])
            # Junta blocos quebrados no meio de frase (continuação de coluna/página)
            if (
                paragrafos
                and txt_limpo
                and not txt_limpo.startswith("Componentes de Conjuração")
                and not txt_limpo.startswith("*")
                and not paragrafos[-1].endswith((".", "!", "?", ":", ")"))
            ):
                # Re-hifenização de fronteira de bloco
                if paragrafos[-1].endswith("-"):
                    m_ult = re.search(r"([A-Za-zÀ-ÿ]+)-$", paragrafos[-1])
                    m_pri = re.match(r"^([a-zà-ÿ]+)", txt_limpo)
                    if m_ult and m_pri and m_ult.group(1).lower() not in PREFIXOS_HIFEN_REAL:
                        paragrafos[-1] = paragrafos[-1][:-1] + txt_limpo
                    else:
                        paragrafos[-1] = paragrafos[-1] + txt_limpo
                else:
                    paragrafos[-1] = paragrafos[-1] + " " + txt_limpo
            else:
                paragrafos.append(txt_limpo)
            i += 1

        # Separar descrição principal, componentes e versão reversa (*NomeReverso: ...)
        # Primeiro, quebrar parágrafos que contenham "Componentes de Conjuração:" ou "*Nome:" embutidos no meio
        paragrafos_expandidos: list[str] = []
        for p in paragrafos:
            # Quebra antes de "Componentes de Conjuração:" se não estiver no início
            partes = re.split(r"(?=(?:Componentes de Conjura[çc][ãa]o\s*:))", p, flags=re.IGNORECASE)
            for pt in partes:
                pt = pt.strip()
                if not pt:
                    continue
                # Quebra antes de "*NomeReverso:" se aparecer após frase no meio do bloco
                subpartes = re.split(r"(?<=[.!?])\s+(?=\*[A-ZÀ-Ý][^:]{1,60}:)", pt)
                for sp in subpartes:
                    sp = sp.strip()
                    if sp:
                        paragrafos_expandidos.append(sp)

        desc_principal: list[str] = []
        componentes_principal: str | None = None
        reverso_obj: dict[str, Any] | None = None
        em_reverso = False

        for p in paragrafos_expandidos:
            if p.startswith("*"):
                em_reverso = True
                m_rev = re.match(r"^\*\s*([^:]+):\s*(.*)$", p)
                if m_rev:
                    reverso_obj = {
                        "nome": limpar_espacos(m_rev.group(1)),
                        "descricao": limpar_espacos(m_rev.group(2)),
                    }
                else:
                    reverso_obj = {"nome": "", "descricao": p.lstrip("*").strip()}
                continue

            if re.match(r"^Componentes de Conjura[çc][ãa]o\s*:", p, re.IGNORECASE):
                valor_comp = re.sub(
                    r"^Componentes de Conjura[çc][ãa]o\s*:\s*", "", p, flags=re.IGNORECASE
                ).strip()
                if em_reverso and reverso_obj is not None:
                    reverso_obj["componentes"] = valor_comp
                else:
                    componentes_principal = valor_comp
                continue

            if em_reverso and reverso_obj is not None:
                reverso_obj["descricao"] = (reverso_obj["descricao"] + "\n\n" + p).strip()
            else:
                desc_principal.append(p)

        item: dict[str, Any] = {
            "id": slugify(mb["nome"]),
            "nome": mb["nome"],
            "reversivel": mb["reversivel"],
            "classes_niveis": mb["classes_niveis"],
            "pagina_livro": mb["pagina_livro"],
            "descricao": "\n\n".join(desc_principal).strip(),
            "componentes": componentes_principal or "",
        }
        if reverso_obj is not None:
            item["reverso"] = reverso_obj
        if tabela_extra is not None:
            item["tabela"] = tabela_extra

        magias_finais.append(item)

    return magias_finais


def validar_dados(dados: dict[str, Any]) -> None:
    listas = dados["listas_por_classe"]
    magias = dados["magias"]

    # 1. Validar listas das 4 classes, níveis 0..9
    total_entradas_lista = 0
    saltos_numeracao: list[str] = []
    for cls in ("clerigo", "druida", "mago", "ilusionista"):
        assert cls in listas, f"Faltando classe {cls}"
        niveis = listas[cls]
        for niv in range(10):
            k = str(niv)
            assert k in niveis and len(niveis[k]) > 0, f"Classe {cls} nível {k} vazia!"
            total_entradas_lista += len(niveis[k])
            nums = [ent["numero"] for ent in niveis[k]]
            esperado = list(range(1, len(nums) + 1))
            if nums != esperado:
                saltos_numeracao.append(f"{cls} N{k}: {nums}")
            for ent in niveis[k]:
                assert ent["nome"], f"Nome vazio em {cls} nível {k}"
                assert ent["pagina_livro"] is not None, f"Sem página em {cls} N{k}: {ent}"
    if saltos_numeracao:
        print(f"[AVISO] Numeração fora de 1..N nas listas ({len(saltos_numeracao)}): {saltos_numeracao}")
    else:
        print("[OK] Numeração sequencial 1..N íntegra em todos os 40 blocos (4 classes x 10 níveis).")

    # 2. Validar descrições A-C
    ids = [m["id"] for m in magias]
    duplicados = [x for x in set(ids) if ids.count(x) > 1]
    assert not duplicados, f"IDs duplicados nas descrições: {duplicados}"

    sem_comp = [m["nome"] for m in magias if not m["componentes"]]
    sem_desc = [m["nome"] for m in magias if not m["descricao"]]
    assert not sem_desc, f"Magias sem descrição: {sem_desc}"

    # 3. Cruzamento: entradas das listas com pagina_livro entre 133 e 147 vs descrições
    nomes_desc_ids = {m["id"] for m in magias}
    entradas_133_147: dict[str, set[int]] = {}
    for cls, niveis in listas.items():
        for niv, itens in niveis.items():
            for ent in itens:
                pg = ent["pagina_livro"]
                if 133 <= pg <= 147:
                    entradas_133_147.setdefault(ent["id"], set()).add(pg)

    faltando_na_desc = sorted(set(entradas_133_147.keys()) - nomes_desc_ids)

    print(f"[OK] Listas por classe: 4 classes, níveis 0-9, {total_entradas_lista} entradas totais:")
    for cls in ("clerigo", "druida", "mago", "ilusionista"):
        cnt = sum(len(v) for v in listas[cls].values())
        por_niv = {k: len(v) for k, v in sorted(listas[cls].items(), key=lambda kv: int(kv[0]))}
        print(f"     - {cls}: {cnt} entradas -> {por_niv}")

    print(f"[OK] Descrições A-C (pp. 133-147): {len(magias)} magias extraídas.")
    print(f"     - Reversíveis (*): {sum(1 for m in magias if m['reversivel'])}")
    print(f"     - Com bloco reverso: {sum(1 for m in magias if 'reverso' in m)}")
    print(f"     - Com tabela: {[m['nome'] for m in magias if 'tabela' in m]}")
    if sem_comp:
        print(f"[AVISO] Magias sem 'Componentes de Conjuração' explícito ({len(sem_comp)}): {sem_comp}")
    if faltando_na_desc:
        print(f"[INFO] IDs nas listas (pp. 133-147) com grafia diferente nas descrições ({len(faltando_na_desc)}): {faltando_na_desc}")


def main() -> None:
    doc = pymupdf.open(str(PDF_PATH))
    try:
        listas = extrair_listas_por_classe(doc)
        magias = extrair_descricoes_magias(doc)
    finally:
        doc.close()

    total_entradas_lista = sum(
        len(itens) for niveis in listas.values() for itens in niveis.values()
    )

    dados = {
        "metadados": {
            "sistema": "Castles & Crusades",
            "edicao": "1ª Edição Brasileira (Livro do Jogador)",
            "fonte": "ref/cc/Magias 01.pdf",
            "paginas_livro": "113-147",
            "total_paginas_pdf": 35,
            "escopo": (
                "Regras gerais de magia, listas completas de feitiços (Clérigo, Druida, "
                "Mago e Ilusionista; níveis 0-9) e descrições de feitiços de A a C."
            ),
            "estatisticas": {
                "total_entradas_listas": total_entradas_lista,
                "total_descricoes_ac": len(magias),
            },
        },
        "regras_gerais_magia": extrair_regras_gerais(),
        "listas_por_classe": listas,
        "magias": magias,
    }

    validar_dados(dados)

    SAIDA_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_PATH.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Arquivo gerado com sucesso em: {SAIDA_PATH}")


if __name__ == "__main__":
    main()
