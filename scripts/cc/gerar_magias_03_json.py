"""Gera dados/dadosc&c/magias03.json a partir de ref/cc/Magias 03.pdf (pp. 185-220).

Extrai todas as descrições completas de feitiços de L (Localizar Outro) a V (Voar),
incluindo componentes, versões reversas (*), tabelas embutidas e a nota especial de
Polimorfia, validando contra as listas de feitiços de dados/dadosc&c/magias01.json.

Execução:
    .venv\\Scripts\\python.exe scripts/cc/gerar_magias_03_json.py
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import pymupdf

RAIZ = Path(__file__).resolve().parents[2]
PDF_PATH = RAIZ / "ref" / "cc" / "Magias 03.pdf"
MAGIAS01_PATH = RAIZ / "dados" / "dadosc&c" / "magias01.json"
MAGIAS02_PATH = RAIZ / "dados" / "dadosc&c" / "magias02.json"
SAIDA_PATH = RAIZ / "dados" / "dadosc&c" / "magias03.json"

PAGINA_INICIAL_LIVRO = 185

PREFIXOS_HIFEN_REAL = {
    "alterar",
    "anti",
    "arco",
    "auto",
    "bem",
    "contra",
    "extra",
    "guarda",
    "infra",
    "inter",
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
    "ultra",
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

LETRAS_SECAO = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

RE_TEM_CLASSE = re.compile(
    r"(cl[eé]rigo|druida|mago|ilusionista)\s*(?:[-–]\s*)?(?:n[íi]vel\s+)?\d+",
    re.IGNORECASE,
)


def slugify(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "_", sem_acento.lower()).strip("_")


def limpar_espacos(texto: str) -> str:
    texto = texto.replace("\u200b", "").replace("\ufeff", "").replace("\xa0", " ")
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto.strip()


def desfazer_hifenizacao(texto: str) -> str:
    texto = texto.replace("\u200b", "").replace("\xa0", " ")

    def _subst(match: re.Match[str]) -> str:
        antes = match.group(1)
        depois = match.group(2)
        if antes.lower() in PREFIXOS_HIFEN_REAL or depois.lower() in SUFIXOS_HIFEN_REAL:
            return f"{antes}-{depois}"
        return f"{antes}{depois}"

    texto = re.sub(r"([A-Za-zÀ-ÿ]+)-\s*\n\s*([a-zà-ÿ]+)", _subst, texto)
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


def parse_cabecalho_magia(texto_cabecalho: str) -> tuple[str, bool, dict[str, int]]:
    limpo = limpar_espacos(texto_cabecalho).rstrip(".")
    m_cls = re.search(
        r"(?:[-–,]\s*)?(?:feiti[çc]o\s+de\s+)?(cl[eé]rigo|druida|mago|ilusionista)\s*(?:[-–]\s*)?(?:n[íi]vel\s+)?\d+",
        limpo,
        re.IGNORECASE,
    )
    if not m_cls:
        raise ValueError(f"Cabeçalho de magia inválido: {texto_cabecalho!r}")

    nome_bruto = limpo[: m_cls.start()].strip().rstrip("-–,").strip()
    parte_classes = limpo[m_cls.start() :]

    reversivel = ("*" in nome_bruto) or ("*" in parte_classes)
    nome = nome_bruto.replace("*", "").strip()

    classes_niveis: dict[str, int] = {}
    for m in re.finditer(
        r"(cl[eé]rigo|druida|mago|ilusionista)\s*(?:[-–]\s*)?(?:n[íi]vel\s+)?(\d+)",
        parte_classes,
        re.IGNORECASE,
    ):
        cls = normalizar_classe(m.group(1))
        niv = int(m.group(2))
        classes_niveis[cls] = niv

    if not classes_niveis:
        raise ValueError(f"Sem classes/níveis no cabeçalho: {texto_cabecalho!r}")

    return nome, reversivel, classes_niveis


def extrair_descricoes_magias(doc: pymupdf.Document) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    eventos: list[dict[str, Any]] = []

    for pno in range(len(doc)):
        pagina_livro = PAGINA_INICIAL_LIVRO + pno
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
            tamanhos_primeira: set[float] = set()
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
                        tamanhos_primeira.add(round(s["size"], 1))

            if not linhas_txt:
                continue

            texto_bruto = "\n".join(linhas_txt).strip()
            if not texto_bruto:
                continue
            if texto_bruto in {"FEITIÇOS", "MAGIA", "DESCRIÇÃO DOS FEITIÇOS"}:
                continue
            if texto_bruto in LETRAS_SECAO:
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
                    "tamanhos": tamanhos_primeira,
                }
            )

    magias_brutas: list[dict[str, Any]] = []
    notas_especiais: list[dict[str, Any]] = []
    atual: dict[str, Any] | None = None
    nota_atual: dict[str, Any] | None = None

    idx_ev = 0
    while idx_ev < len(eventos):
        ev = eventos[idx_ev]
        if ev["is_titulo"]:
            cab_txt = ev["texto_bruto"]
            if cab_txt.rstrip().endswith(",") and idx_ev + 1 < len(eventos):
                prox_txt = eventos[idx_ev + 1]["texto_bruto"]
                if RE_TEM_CLASSE.match(prox_txt.strip()):
                    cab_txt = f"{cab_txt} {prox_txt}"
                    idx_ev += 1
            if not RE_TEM_CLASSE.search(cab_txt):
                # Verifica se o próximo bloco contém as classes
                if idx_ev + 1 < len(eventos) and RE_TEM_CLASSE.search(eventos[idx_ev + 1]["texto_bruto"]):
                    cab_txt = f"{cab_txt} - {eventos[idx_ev + 1]['texto_bruto']}"
                    idx_ev += 1
                else:
                    # Nota introdutória de seção (ex.: "Polimorfia" na p. 196)
                    if atual is not None:
                        magias_brutas.append(atual)
                        atual = None
                    nota_atual = {
                        "titulo": limpar_espacos(cab_txt),
                        "pagina_livro": ev["pagina_livro"],
                        "blocos": [],
                    }
                    notas_especiais.append(nota_atual)
                    idx_ev += 1
                    continue

            nota_atual = None
            if atual is not None:
                magias_brutas.append(atual)
            nome, reversivel, classes_niveis = parse_cabecalho_magia(cab_txt)
            atual = {
                "nome": nome,
                "reversivel": reversivel,
                "classes_niveis": classes_niveis,
                "pagina_livro": ev["pagina_livro"],
                "blocos": [],
            }
        else:
            if nota_atual is not None:
                nota_atual["blocos"].append(ev)
            elif atual is not None:
                atual["blocos"].append(ev)
        idx_ev += 1

    if atual is not None:
        magias_brutas.append(atual)

    notas_finais = [
        {
            "titulo": n["titulo"],
            "pagina_livro": n["pagina_livro"],
            "texto": "\n\n".join(desfazer_hifenizacao(b["texto_bruto"]) for b in n["blocos"]).strip(),
        }
        for n in notas_especiais
    ]

    magias_finais: list[dict[str, Any]] = []
    ids_vistos: dict[str, int] = {}

    re_comp_inicio = re.compile(
        r"(?:Os\s+componentes\s+necess[áa]rios\s+s[ãa]o\s*:|Componentes\s+de\s+Conjura[çc][ãa]o(?:\s+s[ãa]o)?\s*:?)",
        re.IGNORECASE,
    )

    for mb in magias_brutas:
        blocos = mb["blocos"]
        paragrafos: list[str] = []
        tabelas: list[dict[str, Any]] = []

        i = 0
        while i < len(blocos):
            ev = blocos[i]
            if ev["is_tabela_titulo"]:
                linhas_raw = [limpar_espacos(ln) for ln in ev["texto_bruto"].splitlines() if limpar_espacos(ln)]
                titulo_tab = linhas_raw[0]
                linhas_tab = linhas_raw[1:]
                i += 1
                while i < len(blocos):
                    prox = blocos[i]
                    if prox["is_tabela_titulo"]:
                        break
                    t_b = prox["texto_bruto"]
                    max_sz = max(prox["tamanhos"] or {0})
                    if t_b.startswith("Componentes de ") or t_b.startswith("*"):
                        break
                    if max_sz >= 9.5 and not re.match(
                        r"^(?:\d+[-–]\d+|\d+|1d\d+|d\d+|Rodada|Material|Nível|Familiaridade|Tendência)",
                        t_b,
                    ):
                        break
                    linhas_tab.extend([limpar_espacos(ln) for ln in t_b.splitlines() if limpar_espacos(ln)])
                    i += 1
                tabelas.append({"titulo": titulo_tab, "linhas": linhas_tab})
                continue

            txt_limpo = desfazer_hifenizacao(ev["texto_bruto"])
            if (
                paragrafos
                and txt_limpo
                and not txt_limpo.startswith("Componentes de Conjuração")
                and not txt_limpo.startswith("*")
                and not paragrafos[-1].endswith((".", "!", "?", ":", ")"))
            ):
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

        paragrafos_expandidos: list[str] = []
        for p in paragrafos:
            partes = re.split(
                r"(?=(?:Os\s+componentes\s+necess[áa]rios\s+s[ãa]o\s*:|Componentes\s+de\s+Conjura[çc][ãa]o(?:\s+s[ãa]o)?\s*:?))",
                p,
                flags=re.IGNORECASE,
            )
            for pt in partes:
                pt = pt.strip()
                if not pt:
                    continue
                subpartes = re.split(r"(?<=[.!?])\s+(?=\*[A-ZÀ-Ý][^:]{1,70}:)", pt)
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

            if re_comp_inicio.match(p):
                valor_comp = re_comp_inicio.sub("", p, count=1).strip()
                if em_reverso and reverso_obj is not None:
                    reverso_obj["componentes"] = valor_comp
                else:
                    componentes_principal = valor_comp
                continue

            if em_reverso and reverso_obj is not None:
                reverso_obj["descricao"] = (reverso_obj["descricao"] + "\n\n" + p).strip()
            else:
                desc_principal.append(p)

        base_id = slugify(mb["nome"])
        if base_id in ids_vistos:
            prev = next((x for x in magias_finais if x["id"] == base_id), None)
            if prev and prev["pagina_livro"] == mb["pagina_livro"]:
                continue
            ids_vistos[base_id] += 1
            spell_id = f"{base_id}_{ids_vistos[base_id]}"
        else:
            ids_vistos[base_id] = 1
            spell_id = base_id

        item: dict[str, Any] = {
            "id": spell_id,
            "nome": mb["nome"],
            "reversivel": mb["reversivel"],
            "classes_niveis": mb["classes_niveis"],
            "pagina_livro": mb["pagina_livro"],
            "descricao": "\n\n".join(desc_principal).strip(),
            "componentes": componentes_principal or "",
        }
        if reverso_obj is not None:
            item["reverso"] = reverso_obj
        if tabelas:
            item["tabelas"] = tabelas

        magias_finais.append(item)

    return magias_finais, notas_finais


def validar_dados(dados: dict[str, Any]) -> None:
    magias = dados["magias"]
    ids = [m["id"] for m in magias]
    duplicados = [x for x in set(ids) if ids.count(x) > 1]
    assert not duplicados, f"IDs duplicados: {duplicados}"

    sem_desc = [m["nome"] for m in magias if not m["descricao"]]
    assert not sem_desc, f"Magias sem descrição: {sem_desc}"

    sem_comp = [m["nome"] for m in magias if not m["componentes"]]
    com_tabelas = [(m["nome"], len(m["tabelas"])) for m in magias if "tabelas" in m]

    print(f"[OK] Descrições L-V (pp. 185-220): {len(magias)} magias extraídas.")
    print(f"     - Primeira: {magias[0]['nome']} (p. {magias[0]['pagina_livro']})")
    print(f"     - Última:   {magias[-1]['nome']} (p. {magias[-1]['pagina_livro']})")
    print(f"     - Reversíveis (*): {sum(1 for m in magias if m['reversivel'])}")
    print(f"     - Com bloco reverso: {sum(1 for m in magias if 'reverso' in m)}")
    print(f"     - Com tabelas ({len(com_tabelas)}): {com_tabelas}")
    print(f"     - Notas especiais: {[n['titulo'] for n in dados.get('notas_especiais', [])]}")
    if sem_comp:
        print(f"[AVISO] Magias sem 'Componentes de Conjuração' ({len(sem_comp)}): {sem_comp}")
    else:
        print("[OK] 100% das magias possuem 'Componentes de Conjuração' preenchido.")

    # Cruzamento com listas_por_classe de magias01.json (faixa 185-220 + total global)
    if MAGIAS01_PATH.exists():
        m01 = json.loads(MAGIAS01_PATH.read_text(encoding="utf-8"))
        listas = m01.get("listas_por_classe", {})
        entradas_faixa: dict[str, set[int]] = {}
        todas_entradas_listas: set[str] = set()
        for cls, niveis in listas.items():
            for niv, itens in niveis.items():
                for ent in itens:
                    todas_entradas_listas.add(ent["id"])
                    pg = ent["pagina_livro"]
                    if 185 <= pg <= 220:
                        entradas_faixa.setdefault(ent["id"], set()).add(pg)
        desc_ids = {m["id"] for m in magias}
        diff = sorted(set(entradas_faixa.keys()) - desc_ids)
        print(f"[INFO] Entradas únicas nas listas (pp. 185-220): {len(entradas_faixa)}")
        if diff:
            print(f"[INFO] IDs nas listas com grafia diferente ({len(diff)}): {diff}")

        if MAGIAS02_PATH.exists():
            m02 = json.loads(MAGIAS02_PATH.read_text(encoding="utf-8"))
            total_desc = len(m01["magias"]) + len(m02["magias"]) + len(magias)
            print(
                f"[OK] TOTAL GLOBAL DE DESCRIÇÕES (magias01+02+03): {total_desc} feitiços "
                f"({len(m01['magias'])} + {len(m02['magias'])} + {len(magias)}) | "
                f"IDs únicos nas 4 listas: {len(todas_entradas_listas)}"
            )


def main() -> None:
    doc = pymupdf.open(str(PDF_PATH))
    try:
        total_paginas = len(doc)
        magias, notas = extrair_descricoes_magias(doc)
    finally:
        doc.close()

    dados: dict[str, Any] = {
        "metadados": {
            "sistema": "Castles & Crusades",
            "edicao": "1ª Edição Brasileira (Livro do Jogador)",
            "fonte": "ref/cc/Magias 03.pdf",
            "paginas_livro": f"{PAGINA_INICIAL_LIVRO}-{PAGINA_INICIAL_LIVRO + total_paginas - 1}",
            "total_paginas_pdf": total_paginas,
            "escopo": "Descrições completas de feitiços de L (Localizar Outro) a V (Voar), finalizando o capítulo de Magia.",
            "estatisticas": {
                "total_descricoes": len(magias),
                "total_reversiveis": sum(1 for m in magias if m["reversivel"]),
                "total_com_tabelas": sum(1 for m in magias if "tabelas" in m),
            },
        },
        "notas_especiais": notas,
        "magias": magias,
    }

    validar_dados(dados)

    SAIDA_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_PATH.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Arquivo gerado com sucesso em: {SAIDA_PATH}")


if __name__ == "__main__":
    main()
