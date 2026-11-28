"""Gerador e validador de dados/magias02.json a partir de ref/Enchacent02.pdf."""

from __future__ import annotations

import json
import re
import unicodedata
import zlib
from collections import Counter
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_PDF = RAIZ_PROJETO / "ref" / "Enchacent02.pdf"
CAMINHO_MAGIAS_01 = RAIZ_PROJETO / "dados" / "dadospf2" / "magias01.json"
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "dadospf2" / "magias02.json"

DESLOCAMENTO_PAGINA_LIVRO = 359  # Índice 0 do PDF corresponde à pág. 359 do Livro Básico

ESCOLAS_MAIUSCULAS = {
    "ABJURAÇÃO": "Abjuração",
    "ADIVINHAÇÃO": "Adivinhação",
    "CONJURAÇÃO": "Conjuração",
    "CONJURAÇÅO": "Conjuração",
    "ENCANTAMENTO": "Encantamento",
    "EVOCAÇÃO": "Evocação",
    "ILUSÃO": "Ilusão",
    "NECROMANCIA": "Necromancia",
    "TRANSMUTAÇÃO": "Transmutação",
}

MAPA_TRACOS_CANONICOS = {
    "TRUQUE-MÁGICO": "Truque Mágico",
    "TRUQUE MÁGICO": "Truque Mágico",
    "NÃO-LETAL": "Não-Letal",
    "CONJURAÇÅO": "Conjuração",
    "INCAPACITAÇAO": "Incapacitação",
    "CONCETRAÇÃO": "Concentração",
    "MALIGNO": "Mal",
    "SOMBRAS": "Sombra",
}

ROTULOS_METADADOS = {
    "Tradições",
    "Domínio",
    "Execução",
    "Acionamento",
    "Requerimentos",
    "Custo",
    "Conjuradores Secundários",
    "Teste Primário",
    "Testes Secundários",
    "Distância",
    "Área",
    "Áreas",
    "Alvos",
    "Alvo",
    "Salvamento",
    "Duração",
}

ROTULOS_RESULTADOS = {
    "Sucesso Crítico": "sucesso_critico",
    "Sucesso": "sucesso",
    "Falha": "falha",
    "Falha Crítica": "falha_critica",
}

CLASSES_FOCO = {
    "BARDO": ("bardo", "Bardo", "composicao"),
    "CAMPEÃO": ("campeao", "Campeão", "devocao"),
    "CLÉRIGO": ("clerigo", "Clérigo", "dominio"),
    "DRUIDA": ("druida", "Druida", "ordem"),
    "FEITICEIRO": ("feiticeiro", "Feiticeiro", "linhagem"),
    "MAGO": ("mago", "Mago", "escola"),
    "MONGE": ("monge", "Monge", "ki"),
}

PARTICULAS_TITULO = {
    "a",
    "à",
    "às",
    "ao",
    "aos",
    "com",
    "contra",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "ou",
    "para",
    "pela",
    "pelas",
    "pelo",
    "pelos",
    "por",
    "sem",
    "sob",
}

PRESERVAR_HIFEN_DIR = {
    "a",
    "as",
    "o",
    "os",
    "lo",
    "la",
    "los",
    "las",
    "no",
    "nos",
    "nas",
    "lhe",
    "lhes",
    "me",
    "te",
    "se",
    "vos",
    "vivo",
    "viva",
    "vivos",
    "vivas",
    "mágico",
    "mágica",
    "mágicos",
    "mágicas",
    "morte",
    "letal",
    "letais",
    "nativo",
    "nativa",
    "nativos",
    "nativas",
    "combativo",
    "sucedido",
    "sucedida",
    "sucedidos",
    "sucedidas",
    "armado",
    "armada",
    "armados",
    "armadas",
    "action",
    "actions",
    "círculo",
    "íris",
}

PRESERVAR_HIFEN_ESQ = {
    "arco",
    "bem",
    "mal",
    "não",
    "nao",
    "morto",
    "morta",
    "mortos",
    "mortas",
    "louva",
    "recém",
    "pré",
    "pós",
    "sub",
    "semi",
    "anti",
    "extra",
    "vice",
    "povo",
    "planta",
    "faca",
    "one",
    "two",
    "three",
    "free",
}


def slugify(texto: str) -> str:
    """Converte um título em identificador snake_case ASCII sem acentos."""
    normalizado = unicodedata.normalize("NFD", texto)
    sem_acentos = "".join(ch for ch in normalizado if unicodedata.category(ch) != "Mn")
    slug: list[str] = []
    anterior_sep = False
    for ch in sem_acentos.lower():
        if ch.isalnum():
            slug.append(ch)
            anterior_sep = False
        elif not anterior_sep:
            slug.append("_")
            anterior_sep = True
    return "".join(slug).strip("_")


def formatar_titulo_pt(titulo_upper: str) -> str:
    """Converte títulos em caixa alta para capitalização natural em português."""
    palavras = limpar_texto(titulo_upper).split()
    resultado: list[str] = []
    for i, pal in enumerate(palavras):
        low = pal.lower()
        if "-" in low:
            sub = [
                sp if (idx > 0 and sp in PARTICULAS_TITULO) else sp.capitalize()
                for idx, sp in enumerate(low.split("-"))
            ]
            resultado.append("-".join(sub))
        elif i > 0 and low in PARTICULAS_TITULO:
            resultado.append(low)
        else:
            resultado.append(low.capitalize())
    return " ".join(resultado)


def preco_para_pc(texto: str) -> int:
    """Converte valores como '15 po' ou '45.000 po' em peças de cobre."""
    multiplicadores = {"pl": 1000, "po": 100, "pp": 10, "pc": 1}
    total = 0
    for parte in texto.split(","):
        m = re.search(r"([\d.]+)\s*(pl|po|pp|pc)\b", parte.strip().lower())
        if m:
            total += int(m.group(1).replace(".", "")) * multiplicadores[m.group(2)]
    return total


def limpar_texto(texto: str) -> str:
    """Normaliza espaços, remove marcadores `\x08` e corrige ícones de ação quebrados."""
    limpo = texto.replace("\x08", " ").replace("\xa0", " ")
    limpo = re.sub(r"\[(one|two|three|free)-\s*(actions?|action)\]", r"[\1-\2]", limpo)
    limpo = re.sub(r"\[reaction\s*\]", "[reaction]", limpo)
    return re.sub(r"[ \t]+", " ", limpo).strip()


def formatar_traco(traco_bruto: str) -> str:
    """Converte traço em CAIXA ALTA do PDF para forma canônica em português."""
    t = limpar_texto(traco_bruto).upper()
    if t in MAPA_TRACOS_CANONICOS:
        return MAPA_TRACOS_CANONICOS[t]
    if "-" in t:
        partes = t.split("-")
        return "-".join(
            p.lower() if (idx > 0 and p.lower() in PARTICULAS_TITULO) else p.capitalize()
            for idx, p in enumerate(partes)
        )
    palavras = t.split()
    return " ".join(
        p.lower() if (idx > 0 and p.lower() in PARTICULAS_TITULO) else p.capitalize()
        for idx, p in enumerate(palavras)
    )


def deve_preservar_hifen(esquerda: str, direita: str) -> bool:
    """Decide se uma quebra de linha com `-` representa hífen lexical real."""
    esq_lower = esquerda.lower()
    dir_lower = direita.lower()
    return esq_lower in PRESERVAR_HIFEN_ESQ or dir_lower in PRESERVAR_HIFEN_DIR


def concatenar_segmentos_linha(segmentos: list[str]) -> str:
    """Une linhas sequenciais respeitando hifenização em português."""
    acumulado = ""
    for seg in segmentos:
        s = limpar_texto(seg)
        if not s:
            continue
        if not acumulado:
            acumulado = s
            continue
        m_esq = re.search(r"([A-Za-zÀ-ÿ]+)-$", acumulado)
        m_dir = re.match(r"^([A-Za-zÀ-ÿ]+)(.*)$", s)
        if m_esq and m_dir:
            palavra_esq = m_esq.group(1)
            palavra_dir = m_dir.group(1)
            if deve_preservar_hifen(palavra_esq, palavra_dir):
                acumulado = f"{acumulado}{s}"
            else:
                acumulado = f"{acumulado[:-1]}{s}"
        elif acumulado.endswith("[one-") and s.startswith("action]"):
            acumulado = f"{acumulado}{s}"
        else:
            acumulado = f"{acumulado} {s}"
    return limpar_texto(acumulado)


def dehifenizar_texto_corrido(texto: str) -> str:
    """Aplica de-hifenização em texto previamente unido com ou sem espaços após hífen."""
    texto = limpar_texto(texto)

    def _substituir(m: re.Match[str]) -> str:
        esq, esp, dir_ = m.group(1), m.group(2), m.group(3)
        if deve_preservar_hifen(esq, dir_):
            return f"{esq}-{dir_}" if esp else m.group(0)
        return f"{esq}{dir_}"

    return re.sub(r"\b([A-Za-zÀ-ÿ]+)-(\s*)([a-zà-ÿ]+)", _substituir, texto)


def traduzir_tokens_acao_pt(texto: str | None) -> str | None:
    """Converte marcadores de ícone do PDF em inglês para português canônico."""
    if not texto:
        return texto
    for en, pt in (
        ("[one-action]", "[1 ação]"),
        ("[two-actions]", "[2 ações]"),
        ("[three-actions]", "[3 ações]"),
        ("[free-action]", "[ação livre]"),
        ("[reaction]", "[reação]"),
    ):
        texto = texto.replace(en, pt)
    return texto


# ==============================================================================
# Leitor PDF 100% em Python puro (stdlib) para parsing estrutural preciso
# ==============================================================================


class LeitorPDFPuro:
    """Extrator de spans posicionados (com fonte, tamanho e bbox) e linhas horizontais de PDFs 1.7."""

    def __init__(self, caminho_pdf: Path) -> None:
        raw = caminho_pdf.read_bytes()
        self.objs: dict[int, bytes] = {
            int(m.group(1)): m.group(2)
            for m in re.finditer(rb"(\d+)\s+0\s+obj\b(.*?)endobj", raw, re.S)
        }
        self.font_info = self._carregar_fontes()
        root = next(
            v for v in self.objs.values() if b"/Type/Pages" in v or b"/Type /Pages" in v
        )
        kids_m = re.search(rb"/Kids\s*\[([^\]]+)\]", root)
        assert kids_m is not None, "Nó /Kids ausente no PDF"
        self.page_nums = [int(x) for x in re.findall(rb"(\d+)\s+0\s+R", kids_m.group(1))]

    def _get_stream(self, obj_num: int) -> bytes:
        data = self.objs[obj_num]
        m = re.search(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S)
        if not m:
            return b""
        st = m.group(1)
        return zlib.decompress(st) if b"/FlateDecode" in data else st

    def _parse_cmap(self, obj_num: int) -> dict[int, str]:
        txt = self._get_stream(obj_num).decode("latin1", errors="replace")
        cmap: dict[int, str] = {}
        for sec in re.findall(r"beginbfchar(.*?)endbfchar", txt, re.S):
            for k, v in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", sec):
                cmap[int(k, 16)] = bytes.fromhex(v).decode("utf-16-be", errors="replace")
        for sec in re.findall(r"beginbfrange(.*?)endbfrange", txt, re.S):
            for line in sec.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                m1 = re.match(
                    r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", line
                )
                if m1:
                    s, e, b = int(m1.group(1), 16), int(m1.group(2), 16), int(m1.group(3), 16)
                    for i, c in enumerate(range(s, e + 1)):
                        cmap[c] = chr(b + i)
                    continue
                m2 = re.match(
                    r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\[(.*)\]", line
                )
                if m2:
                    s = int(m2.group(1), 16)
                    for i, v in enumerate(re.findall(r"<([0-9A-Fa-f]+)>", m2.group(3))):
                        cmap[s + i] = bytes.fromhex(v).decode("utf-16-be", errors="replace")
        return cmap

    def _carregar_fontes(self) -> dict[int, dict[str, Any]]:
        font_info: dict[int, dict[str, Any]] = {}
        for k, v in self.objs.items():
            if b"/Type/Font" not in v and b"/Type /Font" not in v:
                continue
            bf = re.search(rb"/BaseFont\s*/([^\s/<>\[\]]+)", v)
            if not bf:
                continue
            name = bf.group(1).decode("latin1").split("+", 1)[-1]
            is2 = b"/Subtype/Type0" in v or b"/Subtype /Type0" in v
            tu = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", v)
            cmap = self._parse_cmap(int(tu.group(1))) if tu else {}
            fc_m = re.search(rb"/FirstChar\s+(\d+)", v)
            wm = re.search(rb"/Widths\s*\[([^\]]+)\]", v)
            first_char = int(fc_m.group(1)) if fc_m else 0
            widths = [float(x) for x in wm.group(1).split()] if wm else []
            font_info[k] = {
                "name": name,
                "cmap": cmap,
                "is2": is2,
                "first_char": first_char,
                "widths": widths,
            }
        return font_info

    @staticmethod
    def _decode_str(
        raw_bytes: bytes,
        finfo: dict[str, Any],
        eff_size: float,
        tc_eff: float = 0.0,
        tw_eff: float = 0.0,
    ) -> tuple[str, float]:
        cmap = finfo["cmap"]
        is2 = finfo["is2"]
        fc = finfo["first_char"]
        widths = finfo["widths"]
        out: list[str] = []
        width_pt = 0.0
        if is2:
            for i in range(0, len(raw_bytes) - 1, 2):
                code = (raw_bytes[i] << 8) | raw_bytes[i + 1]
                ch = cmap.get(code, "")
                out.append(ch)
                width_pt += eff_size * (0.9 if "[" in ch else 0.5)
        else:
            for b in raw_bytes:
                out.append(cmap[b] if b in cmap else bytes([b]).decode("cp1252", errors="replace"))
                idx_w = b - fc
                w = widths[idx_w] if (0 <= idx_w < len(widths)) else 500.0
                width_pt += (w / 1000.0) * eff_size + tc_eff + (tw_eff if b == 32 else 0.0)
        return "".join(out), width_pt

    @staticmethod
    def _tokenize(data_bytes: bytes) -> list[tuple[str, Any]]:
        i, n = 0, len(data_bytes)
        tokens: list[tuple[str, Any]] = []
        ws, delim = b" \t\r\n\x0c\x00", b"()<>[]{}/%"
        while i < n:
            c = data_bytes[i : i + 1]
            if c in ws:
                i += 1
                continue
            if c == b"%":
                while i < n and data_bytes[i : i + 1] not in b"\r\n":
                    i += 1
                continue
            if c == b"(":
                i += 1
                depth = 1
                buf = bytearray()
                while i < n and depth > 0:
                    ch = data_bytes[i]
                    if ch == 92:
                        i += 1
                        if i >= n:
                            break
                        nc = data_bytes[i]
                        if nc in b"01234567":
                            octs = bytes([nc])
                            for _ in range(2):
                                if i + 1 < n and data_bytes[i + 1] in b"01234567":
                                    i += 1
                                    octs += bytes([data_bytes[i]])
                                else:
                                    break
                            buf.append(int(octs, 8) & 0xFF)
                        elif nc == ord("n"):
                            buf.append(10)
                        elif nc == ord("r"):
                            buf.append(13)
                        elif nc == ord("t"):
                            buf.append(9)
                        elif nc == ord("b"):
                            buf.append(8)
                        elif nc == ord("f"):
                            buf.append(12)
                        elif nc in (13, 10):
                            if nc == 13 and i + 1 < n and data_bytes[i + 1] == 10:
                                i += 1
                        else:
                            buf.append(nc)
                    elif ch == 40:
                        depth += 1
                        buf.append(ch)
                    elif ch == 41:
                        depth -= 1
                        if depth > 0:
                            buf.append(ch)
                    else:
                        buf.append(ch)
                    i += 1
                tokens.append(("STR", bytes(buf)))
                continue
            if c == b"<":
                if i + 1 < n and data_bytes[i + 1 : i + 2] == b"<":
                    tokens.append(("OP", "<<"))
                    i += 2
                    continue
                j = data_bytes.find(b">", i + 1)
                hex_s = re.sub(rb"\s+", b"", data_bytes[i + 1 : j])
                if len(hex_s) % 2:
                    hex_s += b"0"
                tokens.append(("STR", bytes.fromhex(hex_s.decode("ascii"))))
                i = j + 1
                continue
            if c == b">":
                if i + 1 < n and data_bytes[i + 1 : i + 2] == b">>":
                    tokens.append(("OP", ">>"))
                    i += 2
                    continue
                i += 1
                continue
            if c in b"[]":
                tokens.append(("OP", c.decode("ascii")))
                i += 1
                continue
            if c == b"/":
                j = i + 1
                while j < n and data_bytes[j : j + 1] not in ws + delim:
                    j += 1
                tokens.append(("NAME", data_bytes[i + 1 : j].decode("latin1")))
                i = j
                continue
            j = i
            while j < n and data_bytes[j : j + 1] not in ws + delim:
                j += 1
            word = data_bytes[i:j].decode("latin1")
            try:
                tokens.append(("NUM", float(word)))
            except ValueError:
                tokens.append(("OP", word))
            i = j
        return tokens

    @staticmethod
    def _mat_mul(m1: list[float], m2: list[float]) -> list[float]:
        a1, b1, c1, d1, e1, f1 = m1
        a2, b2, c2, d2, e2, f2 = m2
        return [
            a1 * a2 + b1 * c2,
            a1 * b2 + b1 * d2,
            c1 * a2 + d1 * c2,
            c1 * b2 + d1 * d2,
            e1 * a2 + f1 * c2 + e2,
            e1 * b2 + f1 * d2 + f2,
        ]

    def extrair_pagina(self, idx: int) -> tuple[list[dict[str, Any]], list[tuple[float, float, float]]]:
        """Retorna (spans, hrules) em coordenadas top-down da página de índice `idx`."""
        pdict = self.objs[self.page_nums[idx]]
        mb = re.search(
            rb"/MediaBox\s*\[\s*([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s*\]", pdict
        )
        altura_pagina = float(mb.group(4)) if mb else 783.0

        f_res: dict[str, dict[str, Any]] = {}
        fm = re.search(rb"/Font\s*<<(.*?)>>", pdict, re.S)
        if fm:
            for fn, fobj in re.findall(rb"/([^\s/<>]+)\s+(\d+)\s+0\s+R", fm.group(1)):
                f_res[fn.decode("latin1")] = self.font_info.get(
                    int(fobj), {"name": "Unknown", "cmap": {}, "is2": False, "first_char": 0, "widths": []}
                )

        cm = re.search(rb"/Contents\s+(\d+)\s+0\s+R", pdict)
        if cm:
            st_bytes = self._get_stream(int(cm.group(1)))
        else:
            arr = re.search(rb"/Contents\s*\[([^\]]+)\]", pdict)
            assert arr is not None
            st_bytes = b"\n".join(
                self._get_stream(int(x)) for x in re.findall(rb"(\d+)\s+0\s+R", arr.group(1))
            )

        toks = self._tokenize(st_bytes)
        spans: list[dict[str, Any]] = []
        hrules: list[tuple[float, float, float]] = []
        stack: list[tuple[str, Any]] = []
        ctm_stack: list[tuple[list[float], float, float]] = []
        ctm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        tm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        tlm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        tl = 0.0
        tc = 0.0
        tw = 0.0
        cur_font: dict[str, Any] = {
            "name": "Unknown",
            "cmap": {},
            "is2": False,
            "first_char": 0,
            "widths": [],
        }
        cur_fsize = 1.0
        in_arr = False
        arr_buf: list[tuple[str, Any]] = []
        path_pts: list[tuple[float, float]] = []

        for typ, val in toks:
            if typ == "OP" and val == "[":
                in_arr = True
                arr_buf = []
                continue
            if typ == "OP" and val == "]":
                in_arr = False
                stack.append(("ARR", arr_buf))
                continue
            if in_arr:
                arr_buf.append((typ, val))
                continue
            if typ != "OP":
                stack.append((typ, val))
                continue

            op = val
            if op == "q":
                ctm_stack.append((list(ctm), tc, tw))
                stack.clear()
            elif op == "Q":
                if ctm_stack:
                    ctm, tc, tw = ctm_stack.pop()
                stack.clear()
            elif op == "cm" and len(stack) >= 6:
                ctm = self._mat_mul([float(stack[-6 + i][1]) for i in range(6)], ctm)
                stack.clear()
            elif op == "BT":
                tm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
                tlm = list(tm)
                stack.clear()
            elif op == "ET":
                stack.clear()
            elif op == "Tc" and len(stack) >= 1:
                tc = float(stack[-1][1])
                stack.clear()
            elif op == "Tw" and len(stack) >= 1:
                tw = float(stack[-1][1])
                stack.clear()
            elif op == "Tf" and len(stack) >= 2:
                cur_font = f_res.get(stack[-2][1], cur_font)
                cur_fsize = float(stack[-1][1])
                stack.clear()
            elif op == "TL" and len(stack) >= 1:
                tl = float(stack[-1][1])
                stack.clear()
            elif op == "Tm" and len(stack) >= 6:
                tm = [float(stack[-6 + i][1]) for i in range(6)]
                tlm = list(tm)
                stack.clear()
            elif op in ("Td", "TD") and len(stack) >= 2:
                tx, ty = float(stack[-2][1]), float(stack[-1][1])
                if op == "TD":
                    tl = -ty
                tlm = self._mat_mul([1.0, 0.0, 0.0, 1.0, tx, ty], tlm)
                tm = list(tlm)
                stack.clear()
            elif op == "T*":
                tlm = self._mat_mul([1.0, 0.0, 0.0, 1.0, 0.0, -tl], tlm)
                tm = list(tlm)
                stack.clear()
            elif op in ("Tj", "TJ", "'", '"'):
                if op == '"' and len(stack) >= 3:
                    tw = float(stack[-3][1])
                    tc = float(stack[-2][1])
                if op in ("'", '"'):
                    tlm = self._mat_mul([1.0, 0.0, 0.0, 1.0, 0.0, -tl], tlm)
                    tm = list(tlm)
                fm_atual = self._mat_mul(tm, ctm)
                x0 = fm_atual[4]
                y0 = altura_pagina - fm_atual[5]
                eff_size = round(abs(fm_atual[3]) * cur_fsize, 2)
                escala_x = abs(fm_atual[0])
                tc_eff = tc * escala_x
                tw_eff = tw * escala_x

                parts: list[str] = []
                total_w = 0.0
                sub_x0 = x0

                def _emitir_subspan(fim_w: float) -> None:
                    txt_sub = "".join(parts)
                    if txt_sub:
                        spans.append(
                            {
                                "y0": round(y0, 2),
                                "x0": round(sub_x0, 2),
                                "x1": round(x0 + fim_w, 2),
                                "y1": round(y0 + eff_size, 2),
                                "font": cur_font["name"],
                                "size": eff_size,
                                "text": txt_sub,
                            }
                        )
                    parts.clear()

                if op == "TJ" and stack and stack[-1][0] == "ARR":
                    for et, ev in stack[-1][1]:
                        if et == "STR":
                            txt_p, w_p = self._decode_str(ev, cur_font, eff_size, tc_eff, tw_eff)
                            parts.append(txt_p)
                            total_w += w_p
                        elif et == "NUM":
                            if ev < -500:
                                _emitir_subspan(total_w)
                                total_w -= (ev / 1000.0) * eff_size
                                sub_x0 = x0 + total_w
                            else:
                                if ev < -180:
                                    parts.append(" ")
                                total_w -= (ev / 1000.0) * eff_size
                elif stack and stack[-1][0] == "STR":
                    txt_p, w_p = self._decode_str(stack[-1][1], cur_font, eff_size, tc_eff, tw_eff)
                    parts.append(txt_p)
                    total_w += w_p

                _emitir_subspan(total_w)
                if total_w > 0:
                    tm = self._mat_mul([1.0, 0.0, 0.0, 1.0, total_w / max(escala_x, 1e-6), 0.0], tm)
                stack.clear()
            elif op == "m" and len(stack) >= 2:
                path_pts = [(float(stack[-2][1]), float(stack[-1][1]))]
                stack.clear()
            elif op == "l" and len(stack) >= 2:
                path_pts.append((float(stack[-2][1]), float(stack[-1][1])))
                stack.clear()
            elif op == "re" and len(stack) >= 4:
                rx, ry, rw, rh = [float(stack[-4 + i][1]) for i in range(4)]
                p0 = self._mat_mul([1, 0, 0, 1, rx, ry], ctm)
                p1 = self._mat_mul([1, 0, 0, 1, rx + rw, ry + rh], ctm)
                w, h = abs(p1[4] - p0[4]), abs(p1[5] - p0[5])
                if w > 180.0 and h < 3.0:
                    hrules.append(
                        (
                            round(altura_pagina - max(p0[5], p1[5]), 2),
                            round(min(p0[4], p1[4]), 2),
                            round(w, 2),
                        )
                    )
                stack.clear()
            elif op in ("S", "s", "f", "F", "f*", "B", "B*", "b", "b*", "n"):
                if len(path_pts) == 2:
                    p0 = self._mat_mul([1, 0, 0, 1, path_pts[0][0], path_pts[0][1]], ctm)
                    p1 = self._mat_mul([1, 0, 0, 1, path_pts[1][0], path_pts[1][1]], ctm)
                    w, h = abs(p1[4] - p0[4]), abs(p1[5] - p0[5])
                    if w > 180.0 and h < 3.0:
                        hrules.append(
                            (
                                round(altura_pagina - p0[5], 2),
                                round(min(p0[4], p1[4]), 2),
                                round(w, 2),
                            )
                        )
                path_pts = []
                stack.clear()
            else:
                stack.clear()

        return spans, hrules


def coluna_x0_base(pagina_livro: int, col: int) -> float:
    """Retorna a margem esquerda padrão da coluna nas páginas pares e ímpares."""
    if pagina_livro % 2 == 0:
        return 76.5 if col == 1 else 315.0
    return 67.5 if col == 1 else 306.0


def unir_texto_spans(spans: list[dict[str, Any]]) -> str:
    """Concatena spans horizontais preservando espaços reais e removendo `\x08`."""
    sps = sorted(spans, key=lambda s: s["x0"])
    partes: list[str] = []
    prev_x1: float | None = None
    prev_txt = ""
    for sp in sps:
        t = sp["text"].replace("\x08", " ")
        if not t:
            continue
        if prev_x1 is not None:
            gap = sp["x0"] - prev_x1
            eh_hifen_fim_linha = t == "-" and prev_txt[-1:].isalpha()
            if (
                gap > 2.2
                and not eh_hifen_fim_linha
                and not prev_txt.endswith((" ", "[", "("))
                and not t.startswith((" ", ".", ",", ";", ":", ")", "]", "×"))
            ):
                partes.append(" ")
        partes.append(t)
        prev_x1 = max(prev_x1 or sp["x1"], sp["x1"])
        prev_txt = t
    return limpar_texto("".join(partes))


def construir_eventos_coluna(
    spans: list[dict[str, Any]],
    hrules: list[tuple[float, float, float]],
    bp: int,
    col: int,
    *,
    y_min: float = 45.0,
    y_max: float = 745.0,
    excluir_faixas: list[tuple[int, int, float, float]] | None = None,
) -> list[tuple[str, float, Any]]:
    """Agrupa spans em linhas mescladas na coluna e intercala regras horizontais."""
    faixas = excluir_faixas or []

    def _ignorar(y_val: float) -> bool:
        return any(fbp == bp and fcol == col and fy0 <= y_val <= fy1 for fbp, fcol, fy0, fy1 in faixas)

    cl = [
        sp
        for sp in spans
        if y_min <= sp["y0"] <= y_max
        and ((col == 1 and sp["x0"] < 300.0) or (col == 2 and sp["x0"] >= 300.0))
        and not _ignorar(sp["y0"])
    ]
    cl.sort(key=lambda s: (s["y0"], s["x0"]))

    mescladas: list[list[Any]] = []
    for sp in cl:
        if mescladas and abs(mescladas[-1][0] - sp["y0"]) < 3.0:
            mescladas[-1][4].append(sp)
            mescladas[-1][4].sort(key=lambda s: s["x0"])
            mescladas[-1][1] = min(mescladas[-1][1], sp["x0"])
            mescladas[-1][2] = max(mescladas[-1][2], sp["x1"])
            mescladas[-1][3] = max(mescladas[-1][3], sp["y1"])
        else:
            mescladas.append([sp["y0"], sp["x0"], sp["x1"], sp["y1"], [sp]])

    col_hr = sorted(
        {
            hy
            for hy, hx, _hw in hrules
            if y_min <= hy <= y_max
            and ((col == 1 and hx < 300.0) or (col == 2 and hx >= 300.0))
            and not _ignorar(hy)
        }
    )

    eventos: list[tuple[str, float, Any]] = [("LINE", l[0], l) for l in mescladas] + [
        ("HRULE", hy, None) for hy in col_hr
    ]
    eventos.sort(key=lambda e: (e[1], 0 if e[0] == "HRULE" else 1))
    return eventos


# ==============================================================================
# Quadros Auxiliares e Tabelas Embutidas / Rituais
# ==============================================================================


def extrair_quadro_servo_invisivel(leitor: LeitorPDFPuro) -> dict[str, Any]:
    """Extrai e estrutura o bloco `SERVO INVISÍVEL CRIATURA –1` da pág. 377 (col. 2)."""
    spans, _ = leitor.extrair_pagina(377 - DESLOCAMENTO_PAGINA_LIVRO)
    bloco = [
        sp
        for sp in spans
        if sp["x0"] >= 300.0 and 170.0 <= sp["y0"] <= 425.0
    ]
    bloco.sort(key=lambda s: (round(s["y0"] / 3.0), s["x0"]))
    linhas_txt = []
    atual_y = None
    buf: list[dict[str, Any]] = []
    for sp in bloco:
        if atual_y is None or abs(sp["y0"] - atual_y) < 3.0:
            buf.append(sp)
            if atual_y is None:
                atual_y = sp["y0"]
        else:
            linhas_txt.append(unir_texto_spans(buf))
            buf = [sp]
            atual_y = sp["y0"]
    if buf:
        linhas_txt.append(unir_texto_spans(buf))

    assert any("SERVO INVISÍVEL CRIATURA –1" in l for l in linhas_txt), f"Quadro ausente: {linhas_txt}"

    return {
        "id": "servo_invisivel_criatura",
        "titulo": "Servo Invisível",
        "pagina": 377,
        "magia_relacionada": "servo_invisivel",
        "subtitulo": "Utilize este bloco de estatísticas para um servo invisível.",
        "criatura": {
            "id": "servo_invisivel",
            "nome": "Servo Invisível",
            "nivel": -1,
            "tracos": ["Médio", "Acéfalo"],
            "percepcao": "+0; visão no escuro",
            "idiomas": "— (compreende o criador dele)",
            "pericias": "Furtividade +8",
            "atributos": {
                "forca": -4,
                "destreza": 2,
                "constituicao": 0,
                "inteligencia": -5,
                "sabedoria": 0,
                "carisma": 0,
            },
            "habilidades_interacao": [
                {
                    "nome": "Invisível",
                    "descricao": (
                        "Um servo invisível é invisível, embora normalmente não se Esgueire, "
                        "ficando, portanto, apenas escondido."
                    ),
                }
            ],
            "ca": 13,
            "salvamentos": {"fortitude": 0, "reflexos": 4, "vontade": 0},
            "pv": 4,
            "imunidades": [
                "ataques não-mágicos",
                "doenças",
                "inconsciente",
                "mental",
                "paralisia",
                "precisão",
                "veneno",
            ],
            "resistencias": "todo dano 5 (exceto força ou toque fantasma)",
            "velocidade": "voo 9 metros",
            "habilidades_ofensivas_ou_especiais": [
                {
                    "nome": "Corpo de Força",
                    "descricao": (
                        "O corpo físico de um servo invisível é feito de força. Ele não pode usar ações "
                        "de ataque. Ele pode mover e usar ações de Interagir para fazer coisas como "
                        "carregar objetos, abrir portas destravadas ou destrancadas, segurar cadeiras e "
                        "limpar. Ele não pode atravessar objetos sólidos."
                    ),
                }
            ],
        },
        "texto_original": "\n".join(linhas_txt),
    }


def extrair_linhas_agrupadas_tabela(
    leitor: LeitorPDFPuro,
    pagina_livro: int,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
) -> list[tuple[float, list[dict[str, Any]]]]:
    """Agrupa spans de uma região de tabela por coordenada Y."""
    spans, _ = leitor.extrair_pagina(pagina_livro - DESLOCAMENTO_PAGINA_LIVRO)
    sel = [
        sp
        for sp in spans
        if x_min <= sp["x0"] <= x_max and y_min <= sp["y0"] <= y_max
    ]
    sel.sort(key=lambda s: (s["y0"], s["x0"]))
    grupos: list[tuple[float, list[dict[str, Any]]]] = []
    for sp in sel:
        if grupos and abs(grupos[-1][0] - sp["y0"]) < 3.0:
            grupos[-1][1].append(sp)
        else:
            grupos.append((sp["y0"], [sp]))
    return grupos


def extrair_tabela_rajada_prismatica(leitor: LeitorPDFPuro) -> list[dict[str, str]]:
    """Extrai as 8 linhas da tabela `1d8` de `Rajada Prismática` (p. 372, col. 2)."""
    grupos = extrair_linhas_agrupadas_tabela(leitor, 372, 315.0, 540.0, 445.0, 655.0)
    linhas: list[dict[str, str]] = []
    for _y, sps in grupos:
        col_1d8 = unir_texto_spans([s for s in sps if s["x0"] < 330.0])
        col_cor = unir_texto_spans([s for s in sps if 330.0 <= s["x0"] < 385.0])
        col_salv = unir_texto_spans([s for s in sps if 385.0 <= s["x0"] < 435.0])
        col_ef = unir_texto_spans([s for s in sps if s["x0"] >= 435.0])
        if re.fullmatch(r"[1-8]", col_1d8):
            linhas.append(
                {
                    "1d8": col_1d8,
                    "cor": col_cor,
                    "salvamento": col_salv,
                    "efeito": col_ef,
                }
            )
        elif linhas:
            if col_cor:
                linhas[-1]["cor"] = f"{linhas[-1]['cor']} {col_cor}".strip()
            if col_ef:
                linhas[-1]["efeito"] = f"{linhas[-1]['efeito']} {col_ef}".strip()

    assert [r["1d8"] for r in linhas] == [str(i) for i in range(1, 9)], f"Rajada Prismática inválida: {linhas}"
    return linhas


def extrair_tabela_salpico_de_arte(leitor: LeitorPDFPuro) -> list[dict[str, str]]:
    """Extrai as 4 linhas da tabela `1d4` de `Salpico de Arte` (p. 396, col. 2)."""
    grupos = extrair_linhas_agrupadas_tabela(leitor, 396, 315.0, 540.0, 435.0, 515.0)
    linhas: list[dict[str, str]] = []
    for _y, sps in grupos:
        c_d4 = unir_texto_spans([s for s in sps if s["x0"] < 332.0])
        c_cor = unir_texto_spans([s for s in sps if 332.0 <= s["x0"] < 378.0])
        c_fal = unir_texto_spans([s for s in sps if 378.0 <= s["x0"] < 438.0])
        c_fc = unir_texto_spans([s for s in sps if s["x0"] >= 438.0])
        if re.fullmatch(r"[1-4]", c_d4):
            linhas.append({"1d4": c_d4, "cor": c_cor, "falha": c_fal, "falha_critica": c_fc})
        elif linhas:
            if c_fal:
                linhas[-1]["falha"] = f"{linhas[-1]['falha']} {c_fal}".strip()
            if c_fc:
                linhas[-1]["falha_critica"] = f"{linhas[-1]['falha_critica']} {c_fc}".strip()
    assert [r["1d4"] for r in linhas] == ["1", "2", "3", "4"], f"Salpico de Arte inválido: {linhas}"
    return linhas


def extrair_tabela_ira_abissal(leitor: LeitorPDFPuro) -> list[dict[str, str]]:
    """Extrai as 4 linhas da tabela `1d4` de `Ira Abissal` (p. 403, col. 1)."""
    grupos = extrair_linhas_agrupadas_tabela(leitor, 403, 68.0, 295.0, 570.0, 655.0)
    linhas: list[dict[str, str]] = []
    for _y, sps in grupos:
        c_d4 = unir_texto_spans([s for s in sps if s["x0"] < 85.0])
        c_reino = unir_texto_spans([s for s in sps if 85.0 <= s["x0"] < 140.0])
        c_manif = unir_texto_spans([s for s in sps if 140.0 <= s["x0"] < 215.0])
        c_dano = unir_texto_spans([s for s in sps if s["x0"] >= 215.0])
        if re.fullmatch(r"[1-4]", c_d4):
            linhas.append(
                {
                    "1d4": c_d4,
                    "reino": c_reino,
                    "manifestacao": c_manif,
                    "tipo_de_dano": c_dano,
                }
            )
        elif linhas:
            if c_manif:
                linhas[-1]["manifestacao"] = f"{linhas[-1]['manifestacao']} {c_manif}".strip()
            if c_dano:
                linhas[-1]["tipo_de_dano"] = f"{linhas[-1]['tipo_de_dano']} {c_dano}".strip()
    assert [r["1d4"] for r in linhas] == ["1", "2", "3", "4"], f"Ira Abissal inválida: {linhas}"
    return linhas


def extrair_tabela_sopro_de_dragao(leitor: LeitorPDFPuro) -> list[dict[str, str]]:
    """Extrai as 6 linhas da tabela `Tipo de Dragão` de `Sopro de Dragão` (p. 404, col. 2)."""
    grupos = extrair_linhas_agrupadas_tabela(leitor, 404, 315.0, 540.0, 330.0, 400.0)
    linhas: list[dict[str, str]] = []
    for _y, sps in grupos:
        c_drag = unir_texto_spans([s for s in sps if s["x0"] < 380.0])
        c_area = unir_texto_spans([s for s in sps if 380.0 <= s["x0"] < 485.0])
        c_salv = unir_texto_spans([s for s in sps if s["x0"] >= 485.0])
        if c_drag and c_area and c_salv:
            linhas.append(
                {
                    "tipo_de_dragao": c_drag,
                    "area_e_tipo_de_dano": c_area,
                    "salvamento": c_salv,
                }
            )
    assert len(linhas) == 6, f"Sopro de Dragão inválido: {linhas}"
    return linhas


def extrair_tabela_7_1(leitor: LeitorPDFPuro) -> list[dict[str, Any]]:
    """Extrai as 18 linhas da `Tabela 7–1: Rituais de Criação de Criaturas` (p. 408, col. 2)."""
    grupos = extrair_linhas_agrupadas_tabela(leitor, 408, 315.0, 540.0, 170.0, 375.0)
    linhas: list[dict[str, Any]] = []
    for _y, sps in grupos:
        c_nc = unir_texto_spans([s for s in sps if s["x0"] < 410.0])
        c_nm = unir_texto_spans([s for s in sps if 410.0 <= s["x0"] < 470.0])
        c_cu = unir_texto_spans([s for s in sps if s["x0"] >= 470.0])
        if c_nc and c_nm and c_cu:
            linhas.append(
                {
                    "nivel_criatura": c_nc,
                    "nivel_magia_requerido": int(c_nm),
                    "custo": c_cu,
                    "custo_pc": preco_para_pc(c_cu),
                }
            )
    assert len(linhas) == 18, f"Esperado 18 linhas na Tabela 7–1, obtido {len(linhas)}"
    return linhas


def extrair_tabela_7_2(leitor: LeitorPDFPuro) -> list[dict[str, Any]]:
    """Extrai as 20 linhas da `Tabela 7–2: Rituais por Nível` (p. 409, col. 2)."""
    grupos = extrair_linhas_agrupadas_tabela(leitor, 409, 340.0, 540.0, 90.0, 320.0)
    linhas: list[dict[str, Any]] = []
    for _y, sps in grupos:
        c_niv = unir_texto_spans([s for s in sps if s["x0"] < 395.0])
        c_nome = unir_texto_spans([s for s in sps if s["x0"] >= 395.0])
        if c_niv.isdigit() and c_nome:
            linhas.append(
                {
                    "id": slugify(c_nome),
                    "nivel": int(c_niv),
                    "nome": c_nome,
                }
            )
    assert len(linhas) == 20, f"Esperado 20 linhas na Tabela 7–2, obtido {len(linhas)}"
    return linhas


# ==============================================================================
# Parsing de Metadados, Corpo e Elevada (compartilhado entre magias, foco e rituais)
# ==============================================================================


def _extrair_acoes_execucao(execucao: str) -> str | None:
    """Deriva representação normalizada de custo de ação/tempo a partir da linha de Execução."""
    if not execucao:
        return None
    if "[one-action] a [three-actions]" in execucao:
        return "1 a 3"
    if "[one-action] a [two-actions]" in execucao:
        return "1 a 2"
    if "[one-action] ou mais" in execucao:
        return "1 ou mais"
    mapa = {
        "[one-action]": "1",
        "[two-actions]": "2",
        "[three-actions]": "3",
        "[free-action]": "livre",
        "[reaction]": "reacao",
    }
    for tok, val in mapa.items():
        if tok in execucao:
            return val
    if "(" in execucao:
        return execucao.split("(", 1)[0].strip()
    return execucao


def _extrair_componentes_execucao(execucao: str, eh_ritual: bool = False) -> list[str]:
    """Extrai a lista ordenada de componentes mágicos a partir da Execução."""
    presentes: list[str] = []
    texto_lower = execucao.lower()
    for comp in ("foco", "material", "somático", "verbal"):
        if re.search(rf"\b{comp}\b", texto_lower):
            presentes.append(comp)
    if eh_ritual and not presentes:
        # Regra da pág. 408: "Todos os rituais requerem componentes materiais, somáticos e verbais"
        return ["material", "somático", "verbal"]
    return presentes


def _normalizar_rotulo_bold(texto: str) -> str | None:
    limpo = limpar_texto(texto).rstrip(":").strip()
    if limpo in ROTULOS_METADADOS:
        return limpo
    return None


def _parsear_metadados(
    linhas_meta: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]],
    *,
    eh_ritual: bool = False,
) -> dict[str, Any]:
    """Extrai campos estruturados de metadados, tratando rótulos compostos ou quebrados em duas linhas."""
    tokens_linha: list[list[tuple[bool, str]]] = []
    for _bp, _col, _x0, _y0, _x1, _y1, spans in linhas_meta:
        # Primeiro agrupa spans adjacentes de mesma categoria (GoodOT-Bold vs demais) na mesma linha
        grupos_linha: list[tuple[bool, str]] = []
        for sp in sorted(spans, key=lambda s: s["x0"]):
            eh_bold = sp["font"] == "GoodOT-Bold"
            txt = sp["text"].replace("\x08", " ")
            if not txt:
                continue
            if grupos_linha and grupos_linha[-1][0] == eh_bold:
                anterior = grupos_linha[-1][1]
                grupos_linha[-1] = (eh_bold, f"{anterior}{txt}")
            else:
                grupos_linha.append((eh_bold, txt))
        tokens_linha.append(grupos_linha)

    # Normaliza tokens sequenciais e une rótulos quebrados entre linhas ("Conjuradores\nSecundários", "Testes Se-\ncundários")
    tokens_seq: list[tuple[bool, str]] = []
    for idx_l, grp in enumerate(tokens_linha):
        if idx_l > 0 and tokens_seq:
            # Verifica se o último token é bold e o primeiro token desta linha também é bold formando um rótulo conhecido
            if (
                tokens_seq[-1][0]
                and grp
                and grp[0][0]
            ):
                prev_b = limpar_texto(tokens_seq[-1][1])
                curr_b = limpar_texto(grp[0][1])
                comb = (
                    f"{prev_b[:-1]}{curr_b}"
                    if prev_b.endswith("-")
                    else f"{prev_b} {curr_b}"
                )
                if _normalizar_rotulo_bold(comb):
                    tokens_seq[-1] = (True, comb)
                    grp = grp[1:]
            # Se o token anterior não era rótulo, trata hifenização da continuação de valor
            if grp and not tokens_seq[-1][0]:
                prox_texto = "".join(p[1] for p in grp).lstrip()
                prev_texto = tokens_seq[-1][1]
                m_esq = re.search(r"([A-Za-zÀ-ÿ]+)-$", prev_texto.rstrip())
                m_dir = re.match(r"^([A-Za-zÀ-ÿ]+)", prox_texto)
                if m_esq and m_dir:
                    if deve_preservar_hifen(m_esq.group(1), m_dir.group(1)):
                        tokens_seq[-1] = (False, prev_texto.rstrip())
                    else:
                        tokens_seq[-1] = (False, prev_texto.rstrip()[:-1])
                elif not prev_texto.endswith((" ", ";")):
                    tokens_seq[-1] = (False, f"{prev_texto} ")

        for eh_bold, raw_txt in grp:
            if eh_bold:
                rot = _normalizar_rotulo_bold(raw_txt)
                if rot:
                    tokens_seq.append((True, rot))
                    continue
                # Caso dois rótulos estejam ou sobrem espaços, tenta quebrar se contiver rótulo válido
                tokens_seq.append((True, limpar_texto(raw_txt)))
            else:
                tokens_seq.append((False, raw_txt))

    # Converte apenas bolds que são rótulos exatos em marcadores de campo
    campos_brutos: dict[str, str] = {}
    rotulo_atual: str | None = None
    buf_val: list[str] = []
    for eh_bold, val in tokens_seq:
        rot = _normalizar_rotulo_bold(val) if eh_bold else None
        if rot:
            if rotulo_atual is not None:
                campos_brutos[rotulo_atual] = limpar_texto("".join(buf_val)).rstrip(";").strip()
            rotulo_atual = rot
            buf_val = []
        elif rotulo_atual is not None:
            buf_val.append(val)
    if rotulo_atual is not None:
        campos_brutos[rotulo_atual] = limpar_texto("".join(buf_val)).rstrip(";").strip()

    tradicoes = sorted(
        {limpar_texto(t).lower() for t in campos_brutos.get("Tradições", "").split(",") if limpar_texto(t)}
    )
    execucao = limpar_texto(campos_brutos.get("Execução", ""))
    acoes = _extrair_acoes_execucao(execucao)
    componentes = _extrair_componentes_execucao(execucao, eh_ritual=eh_ritual)

    area = campos_brutos.get("Área") or campos_brutos.get("Áreas")
    alvos = campos_brutos.get("Alvos") or campos_brutos.get("Alvo")
    if area and alvos and area.endswith(" ou"):
        area = f"{area[:-3].strip()} (ou Alvos)"

    return {
        "tradicoes": tradicoes,
        "dominio": campos_brutos.get("Domínio") or None,
        "execucao": execucao,
        "acoes": acoes,
        "componentes": componentes,
        "custo": campos_brutos.get("Custo") or None,
        "acionamento": campos_brutos.get("Acionamento") or None,
        "requerimentos": campos_brutos.get("Requerimentos") or None,
        "conjuradores_secundarios": campos_brutos.get("Conjuradores Secundários") or None,
        "teste_primario": campos_brutos.get("Teste Primário") or None,
        "testes_secundarios": campos_brutos.get("Testes Secundários") or None,
        "distancia": campos_brutos.get("Distância") or None,
        "area": area or None,
        "alvos": alvos or None,
        "salvamento": campos_brutos.get("Salvamento") or None,
        "duracao": campos_brutos.get("Duração") or None,
    }


def _separar_meta_e_corpo_sem_hrule(
    linhas_sec1: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]]
) -> tuple[
    list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]],
    list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]],
]:
    """Separa metadados e corpo quando a diagramação omite a linha horizontal divisória."""
    linhas_meta: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]] = []
    linhas_corpo: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]] = []
    em_meta = True
    for item in linhas_sec1:
        spans = item[6]
        primeiro = next((s for s in spans if s["text"].strip()), None)
        if (
            em_meta
            and primeiro is not None
            and primeiro["font"] == "GoodOT-Bold"
            and primeiro["text"].strip().rstrip(":") in ROTULOS_METADADOS
        ):
            linhas_meta.append(item)
        else:
            em_meta = False
            linhas_corpo.append(item)
    return linhas_meta, linhas_corpo


def _secao_comeca_com_elevada(secao: list[Any]) -> bool:
    """Verifica se uma seção começa diretamente com cabeçalho em negrito `Elevada` ou `Elevado`."""
    if not secao:
        return False
    spans = secao[0][4][4]
    primeiro = next((s for s in spans if s["text"].strip()), None)
    if primeiro is None or primeiro["font"] != "GoodOT-Bold":
        return False
    txt = limpar_texto(primeiro["text"])
    return txt.startswith("Elevada") or txt.startswith("Elevado")


def _eh_item_numerado_cromatica(spans: list[dict[str, Any]]) -> bool:
    """Detecta itens `1. Vermelha`..`8. Rerrole` na magia Muralha Cromática."""
    txt = unir_texto_spans(spans)
    primeiro = next((s for s in spans if s["text"].strip()), None)
    return (
        primeiro is not None
        and primeiro["font"] == "GoodOT-Bold"
        and bool(re.match(r"^[1-8]\.\s", txt))
    )


def _montar_paragrafos_corpo(
    linhas_corpo: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]]
) -> tuple[str, dict[str, str] | None]:
    """Reconstrói parágrafos, marcadores, sub-itens e graus de sucesso do corpo."""
    blocos_logicos: list[dict[str, Any]] = []
    em_hanging = False
    prev_x1 = 0.0
    prev_txt_limpo = ""
    prev_col_base = 0.0

    for bp, col, x0, _y0, x1, _y1, spans in linhas_corpo:
        col_base = coluna_x0_base(bp, col)
        txt = unir_texto_spans(spans)
        if not txt:
            continue

        primeiro = next((s for s in spans if s["text"].strip()), None)
        eh_marcador = txt.startswith("•")
        eh_item_num = _eh_item_numerado_cromatica(spans)
        eh_subfaixa = (
            primeiro is not None
            and primeiro["font"] == "GoodOT-Bold"
            and bool(re.match(r"^\d+º\b", txt))
        )

        # Identifica rótulo exato de resultado em negrito no início da linha
        rot_resultado: str | None = None
        if primeiro is not None and primeiro["font"] == "GoodOT-Bold":
            bold_iniciais = []
            for s in sorted(spans, key=lambda sp: sp["x0"]):
                if s["font"] == "GoodOT-Bold":
                    bold_iniciais.append(s["text"].replace("\x08", " "))
                elif s["text"].strip():
                    break
            candidato = limpar_texto("".join(bold_iniciais))
            if candidato in ROTULOS_RESULTADOS:
                rot_resultado = candidato

        eh_indentada = abs(x0 - (col_base + 9.0)) < 1.8
        linha_anterior_encerrada = (
            prev_x1 < prev_col_base + 216.0
            and bool(re.search(r"[.!?:)]$", prev_txt_limpo))
        )

        if not blocos_logicos:
            tipo_ini = (
                "resultado"
                if rot_resultado
                else ("marcador" if (eh_marcador or eh_item_num) else "paragrafo")
            )
            blocos_logicos.append({"tipo": tipo_ini, "rotulo": rot_resultado, "segs": [txt]})
            em_hanging = bool(rot_resultado or eh_marcador or eh_item_num)
        elif rot_resultado:
            blocos_logicos.append({"tipo": "resultado", "rotulo": rot_resultado, "segs": [txt]})
            em_hanging = True
        elif eh_marcador or eh_item_num:
            blocos_logicos.append({"tipo": "marcador", "rotulo": None, "segs": [txt]})
            em_hanging = True
        elif eh_subfaixa:
            blocos_logicos.append({"tipo": "paragrafo", "rotulo": None, "segs": [txt]})
            em_hanging = False
        elif (
            eh_indentada
            and blocos_logicos[-1]["tipo"] != "resultado"
            and (not em_hanging or linha_anterior_encerrada)
        ):
            blocos_logicos.append({"tipo": "paragrafo", "rotulo": None, "segs": [txt]})
            em_hanging = False
        elif (
            not eh_indentada
            and em_hanging
            and abs(x0 - col_base) < 1.8
            and linha_anterior_encerrada
            and blocos_logicos[-1]["tipo"] == "resultado"
        ):
            blocos_logicos.append({"tipo": "paragrafo", "rotulo": None, "segs": [txt]})
            em_hanging = False
        else:
            blocos_logicos[-1]["segs"].append(txt)

        prev_x1 = x1
        prev_txt_limpo = txt
        prev_col_base = col_base

    paragrafos_desc: list[str] = []
    resultados: dict[str, str] = {}
    for bloco in blocos_logicos:
        texto_bloco = concatenar_segmentos_linha(bloco["segs"])
        if bloco["tipo"] == "resultado":
            rot = bloco["rotulo"]
            chave = ROTULOS_RESULTADOS[rot]
            conteudo = texto_bloco[len(rot) :].strip()
            resultados[chave] = conteudo
        elif bloco["tipo"] == "marcador":
            texto_bullet = re.sub(r"^•\s*", "• ", texto_bloco)
            paragrafos_desc.append(texto_bullet)
        else:
            paragrafos_desc.append(texto_bloco)

    partes_finais: list[str] = []
    for p in paragrafos_desc:
        if not partes_finais:
            partes_finais.append(p)
        elif (p.startswith("• ") and partes_finais[-1].startswith("• ")) or (
            re.match(r"^[1-8]\.\s", p) and re.match(r"^[1-8]\.\s", partes_finais[-1].splitlines()[-1])
        ):
            partes_finais[-1] = f"{partes_finais[-1]}\n{p}"
        else:
            partes_finais.append(p)

    descricao = "\n\n".join(partes_finais)
    return descricao, (resultados if resultados else None)


def _parsear_elevada(
    linhas_elevada: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]]
) -> tuple[str | None, list[dict[str, str]] | None]:
    """Parseia cláusulas `Elevada (...)` / `Elevado (...)` e eventuais subdivisões de Muralha Cromática."""
    if not linhas_elevada:
        return None, None

    linhas_txt = [unir_texto_spans(item[6]) for item in linhas_elevada]
    linhas_txt = [t for t in linhas_txt if t]
    if not linhas_txt:
        return None, None

    blocos: list[tuple[str, list[str]]] = []
    intro_segs: list[str] = []

    for idx_l, t in enumerate(linhas_txt):
        spans = linhas_elevada[idx_l][6]
        primeiro = next((s for s in spans if s["text"].strip()), None)
        eh_inicio_elevada = (
            primeiro is not None
            and primeiro["font"] == "GoodOT-Bold"
            and (t.startswith("Elevada") or t.startswith("Elevado"))
        ) or t.startswith("Elevada (") or t.startswith("Elevado (")

        if eh_inicio_elevada:
            m = re.match(r"^Elevad[ao]\s*\(([^)]+)\)\s*(.*)$", t)
            if m:
                blocos.append((m.group(1).strip(), [m.group(2).strip()] if m.group(2).strip() else []))
            else:
                blocos.append(("especial", [t]))
        elif not blocos:
            intro_segs.append(t)
        else:
            if _eh_item_numerado_cromatica(spans):
                blocos[-1][1].append("\n" + t)
            else:
                blocos[-1][1].append(t)

    intro = concatenar_segmentos_linha(intro_segs) if intro_segs else None
    lista_elevada: list[dict[str, str]] = []
    for niv, segs in blocos:
        # Preserva quebras `\n` antes de itens numerados (5..8 de Muralha Cromática)
        sub_grupos: list[list[str]] = [[]]
        for s in segs:
            if s.startswith("\n"):
                sub_grupos.append([s.lstrip("\n")])
            else:
                sub_grupos[-1].append(s)
        efeito = "\n".join(concatenar_segmentos_linha(g) for g in sub_grupos if g).strip()
        lista_elevada.append({"nivel": niv, "efeito": efeito})

    return intro, (lista_elevada if lista_elevada else None)


def _particionar_secoes_entrada(
    eventos: list[tuple[str, int, int, float, Any]],
) -> tuple[
    list[str],
    list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]],
    list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]],
    list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]],
]:
    """Divide eventos entre traços, metadados, corpo e seções `Elevada` (suportando >4 seções)."""
    secoes: list[list[Any]] = [[]]
    for ev in eventos:
        if ev[0] == "HRULE":
            secoes.append([])
        else:
            secoes[-1].append(ev)

    while secoes and not secoes[-1]:
        secoes.pop()

    assert len(secoes) >= 2 and len(secoes[0]) == 0, (
        f"Estrutura inesperada de seções: {[len(s) for s in secoes]}"
    )

    sec_meta = secoes[1]
    tracos_brutos: list[str] = []
    idx_meta = 0
    while idx_meta < len(sec_meta):
        spans = sec_meta[idx_meta][4][4]
        if all((s["font"] == "GoodOT-CondBold" and s["size"] <= 7.5) or not s["text"].strip() for s in spans):
            for s in sorted(spans, key=lambda sp: sp["x0"]):
                if s["text"].strip():
                    tracos_brutos.append(s["text"].strip())
            idx_meta += 1
        else:
            break

    def _conv(ev: Any) -> tuple[int, int, float, float, float, float, list[dict[str, Any]]]:
        return (ev[1], ev[2], ev[4][1], ev[4][0], ev[4][2], ev[4][3], ev[4][4])

    linhas_sec1 = [_conv(ev) for ev in sec_meta[idx_meta:]]

    if len(secoes) == 2:
        # Ex.: Página Secreta (p. 365) omite a HRULE entre Duração e corpo
        linhas_meta, linhas_corpo = _separar_meta_e_corpo_sem_hrule(linhas_sec1)
        linhas_elevada: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]] = []
    else:
        linhas_meta = linhas_sec1
        linhas_corpo = []
        linhas_elevada = []
        em_elevada = False
        for sec in secoes[2:]:
            if not sec:
                continue
            if _secao_comeca_com_elevada(sec):
                em_elevada = True
            if em_elevada:
                linhas_elevada.extend(_conv(ev) for ev in sec)
            else:
                # Preserva quebra de parágrafo quando sub-faixas de Ária Fatal (16º/17º/18º) têm HRULE
                linhas_corpo.extend(_conv(ev) for ev in sec)

    return tracos_brutos, linhas_meta, linhas_corpo, linhas_elevada


# ==============================================================================
# Extração das 3 Grandes Seções do Capítulo 7 (Parte 2)
# ==============================================================================


def extrair_magias_regulares(
    leitor: LeitorPDFPuro, indice_listas: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Extrai as 159 magias restantes (Mensageiro Animal a Zona da Verdade, pp. 359–385)."""
    tabela_rajada = extrair_tabela_rajada_prismatica(leitor)
    excluir = [
        (372, 2, 435.0, 655.0),  # Tabela embutida de Rajada Prismática
        (377, 2, 168.0, 425.0),  # Quadro Servo Invisível Criatura –1
    ]

    brutas: list[dict[str, Any]] = []
    atual: dict[str, Any] | None = None

    for bp in range(359, 386):
        idx = bp - DESLOCAMENTO_PAGINA_LIVRO
        spans, hrules = leitor.extrair_pagina(idx)
        for col in (1, 2):
            eventos = construir_eventos_coluna(spans, hrules, bp, col, excluir_faixas=excluir)
            for et, ey, payload in eventos:
                if et == "LINE":
                    sps = payload[4]
                    txt = unir_texto_spans(sps)
                    if not txt or sps[0]["font"] == "Taroca":
                        continue
                    m = re.match(r"^(.+?)\s+(MAGIA|TRUQUE MÁGICO)\s+(\d+)$", txt)
                    if m and any(s["font"] == "GoodOT-CondBold" and s["size"] >= 11.0 for s in sps):
                        if atual is not None:
                            brutas.append(atual)
                        atual = {
                            "titulo_pdf": m.group(1).strip(),
                            "tipo_cabecalho": m.group(2),
                            "nivel_cabecalho": int(m.group(3)),
                            "pagina": bp,
                            "eventos": [],
                        }
                        continue
                if atual is not None:
                    atual["eventos"].append((et, bp, col, ey, payload))

    if atual is not None:
        brutas.append(atual)

    magias: list[dict[str, Any]] = []
    for sp in brutas:
        tracos_brutos, linhas_meta, linhas_corpo, linhas_elevada = _particionar_secoes_entrada(
            sp["eventos"]
        )
        meta_p = _parsear_metadados(linhas_meta)
        descricao, resultados = _montar_paragrafos_corpo(linhas_corpo)
        intro_elevada, elevada = _parsear_elevada(linhas_elevada)
        if intro_elevada:
            descricao = f"{descricao}\n\n{intro_elevada}" if descricao else intro_elevada

        sid = slugify(sp["titulo_pdf"])
        info_lista = indice_listas.get(sid)
        assert info_lista is not None, f"Magia {sp['titulo_pdf']} não localizada nas listas de magias01.json"

        escola_canonica = next(
            (ESCOLAS_MAIUSCULAS[t] for t in tracos_brutos if t in ESCOLAS_MAIUSCULAS),
            info_lista["escola"],
        )
        raridade = "raro" if "RARO" in tracos_brutos else ("incomum" if "INCOMUM" in tracos_brutos else "comum")
        tracos_formatados = [formatar_traco(t) for t in tracos_brutos]

        tipo = "truque_magico" if sp["tipo_cabecalho"] == "TRUQUE MÁGICO" else "magia"
        nivel = 0 if tipo == "truque_magico" else sp["nivel_cabecalho"]

        obs_livro = None
        if sid == "terreno_alucinatorio":
            obs_livro = (
                "Incongruência do Livro Básico (p. 381): nas Listas de Magias (pp. 308, 313 e 315) esta magia consta como "
                "arcana, ocultista e primal, porém o metadado Tradições da descrição (p. 381) imprime 'arcana, divina, ocultista'."
            )
        elif sid == "muralha_de_gelo":
            obs_livro = "Erro tipográfico no texto impresso do Livro Básico (p. 362): 'a magia é perdida.a.'."
        elif sid == "muralha_de_pedra":
            obs_livro = "Erro tipográfico no traço impresso (p. 362): 'CONJURAÇÅO' normalizado para 'Conjuração'."
        elif sid == "prender_alma":
            obs_livro = "Variante terminológica no traço impresso (p. 369): 'MALIGNO' normalizado para 'Mal'."
        elif sid == "sifonar_sombra":
            obs_livro = "Variante no traço impresso (p. 377): 'SOMBRAS' normalizado para 'Sombra'."
        elif sid == "observacao_inexoravel":
            obs_livro = "Metadado impresso no plural na p. 364 ('Áreas explosão de 6 metros'), normalizado para o campo area."

        resumos = sorted(info_lista["resumos"])
        resumo_lista = resumos[0] if resumos else ""

        magias.append(
            {
                "id": sid,
                "nome": info_lista["nome"],
                "tipo": tipo,
                "nivel": nivel,
                "pagina": sp["pagina"],
                "raridade": raridade,
                "tracos": tracos_formatados,
                "escola": escola_canonica,
                "tradicoes": meta_p["tradicoes"],
                "execucao": traduzir_tokens_acao_pt(meta_p["execucao"]),
                "acoes": meta_p["acoes"],
                "componentes": meta_p["componentes"],
                "custo": meta_p["custo"],
                "acionamento": meta_p["acionamento"],
                "requerimentos": meta_p["requerimentos"],
                "distancia": meta_p["distancia"],
                "area": meta_p["area"],
                "alvos": meta_p["alvos"],
                "salvamento": meta_p["salvamento"],
                "duracao": meta_p["duracao"],
                "resumo_lista": dehifenizar_texto_corrido(resumo_lista),
                "descricao": traduzir_tokens_acao_pt(descricao),
                "resultados": resultados,
                "elevada": elevada,
                "tabela": tabela_rajada if sid == "rajada_prismatica" else None,
                "observacao_livro": obs_livro,
            }
        )

    return magias


def extrair_magias_de_foco(leitor: LeitorPDFPuro) -> dict[str, Any]:
    """Extrai todas as 158 magias de foco de Bardo a Monge (pp. 386–407)."""
    tabelas_foco = {
        "salpico_de_arte": extrair_tabela_salpico_de_arte(leitor),
        "ira_abissal": extrair_tabela_ira_abissal(leitor),
        "sopro_de_dragao": extrair_tabela_sopro_de_dragao(leitor),
    }
    excluir = [
        (386, 1, 0.0, 145.0),    # Título 'Magias de Foco' e parágrafo introdutório
        (386, 2, 0.0, 145.0),    # HRULE do bloco de abertura
        (396, 2, 424.0, 515.0),  # Tabela Salpico de Arte
        (403, 1, 562.0, 655.0),  # Tabela Ira Abissal
        (404, 2, 320.0, 400.0),  # Tabela Sopro de Dragão
    ]

    # Extrai introdução geral da p. 386
    spans_386, _ = leitor.extrair_pagina(386 - DESLOCAMENTO_PAGINA_LIVRO)
    intro_geral = concatenar_segmentos_linha(
        [
            s["text"]
            for s in sorted(spans_386, key=lambda x: (x["y0"], x["x0"]))
            if 85.0 <= s["y0"] <= 128.0 and s["font"] == "SabonLTStd-Italic"
        ]
    )

    introducoes_classes: dict[str, list[str]] = {cid: [] for cid, _, _ in CLASSES_FOCO.values()}
    brutas: list[dict[str, Any]] = []
    atual: dict[str, Any] | None = None
    classe_atual: tuple[str, str, str] | None = None
    aguardando_hrule_classe = False

    for bp in range(386, 408):
        idx = bp - DESLOCAMENTO_PAGINA_LIVRO
        spans, hrules = leitor.extrair_pagina(idx)
        for col in (1, 2):
            eventos = construir_eventos_coluna(spans, hrules, bp, col, excluir_faixas=excluir)
            for et, ey, payload in eventos:
                if et == "LINE":
                    sps = payload[4]
                    txt = unir_texto_spans(sps)
                    if not txt:
                        continue
                    primeiro = next((s for s in sps if s["text"].strip()), None)

                    if (
                        primeiro is not None
                        and primeiro["font"] == "Gin-Regular"
                        and txt in CLASSES_FOCO
                    ):
                        if atual is not None:
                            brutas.append(atual)
                            atual = None
                        classe_atual = CLASSES_FOCO[txt]
                        aguardando_hrule_classe = True
                        continue

                    if (
                        primeiro is not None
                        and primeiro["font"] in ("SabonLTStd-Roman", "GoodOT")
                        and classe_atual is not None
                        and atual is None
                    ):
                        introducoes_classes[classe_atual[0]].append(txt)
                        continue

                    m = re.match(r"^(.+?)\s+(FOCO|TRUQUE MÁGICO)\s+(\d+)$", txt)
                    if m and any(s["font"] == "GoodOT-CondBold" and s["size"] >= 11.0 for s in sps):
                        assert classe_atual is not None
                        if atual is not None:
                            brutas.append(atual)
                        aguardando_hrule_classe = False
                        atual = {
                            "titulo_pdf": m.group(1).strip(),
                            "tipo_cabecalho": m.group(2),
                            "nivel_cabecalho": int(m.group(3)),
                            "pagina": bp,
                            "classe_id": classe_atual[0],
                            "classe_nome": classe_atual[1],
                            "categoria_foco": classe_atual[2],
                            "eventos": [],
                        }
                        continue

                if aguardando_hrule_classe and et == "HRULE":
                    aguardando_hrule_classe = False
                    continue

                if atual is not None:
                    atual["eventos"].append((et, bp, col, ey, payload))

    if atual is not None:
        brutas.append(atual)

    lista_foco: list[dict[str, Any]] = []
    contagem_por_classe: Counter[str] = Counter()
    for sp in brutas:
        tracos_brutos, linhas_meta, linhas_corpo, linhas_elevada = _particionar_secoes_entrada(
            sp["eventos"]
        )
        meta_p = _parsear_metadados(linhas_meta)
        descricao, resultados = _montar_paragrafos_corpo(linhas_corpo)
        intro_elevada, elevada = _parsear_elevada(linhas_elevada)
        if intro_elevada:
            descricao = f"{descricao}\n\n{intro_elevada}" if descricao else intro_elevada

        sid = slugify(sp["titulo_pdf"])
        escola_canonica = next(
            (ESCOLAS_MAIUSCULAS[t] for t in tracos_brutos if t in ESCOLAS_MAIUSCULAS),
            None,
        )
        raridade = "raro" if "RARO" in tracos_brutos else ("incomum" if "INCOMUM" in tracos_brutos else "comum")
        tracos_formatados = [formatar_traco(t) for t in tracos_brutos]

        tipo = "truque_magico_foco" if sp["tipo_cabecalho"] == "TRUQUE MÁGICO" else "foco"

        obs_livro = None
        if sid == "pesadelo_compartilhado":
            obs_livro = "Erro tipográfico no traço impresso (p. 395): 'INCAPACITAÇAO' normalizado para 'Incapacitação'."
        elif sid == "visao_do_adivinho":
            obs_livro = "Erro tipográfico no traço impresso (p. 406): 'CONCETRAÇÃO' normalizado para 'Concentração'."
        elif sid == "movimento_elemental":
            obs_livro = "Erro tipográfico no texto impresso do Livro Básico (p. 404): 'sua Velocidade dependo de seu elemento'."

        contagem_por_classe[sp["classe_id"]] += 1
        lista_foco.append(
            {
                "id": sid,
                "nome": formatar_titulo_pt(sp["titulo_pdf"]),
                "classe": sp["classe_nome"],
                "classe_id": sp["classe_id"],
                "categoria_foco": sp["categoria_foco"],
                "dominio": meta_p["dominio"],
                "tipo": tipo,
                "nivel": sp["nivel_cabecalho"],
                "pagina": sp["pagina"],
                "raridade": raridade,
                "tracos": tracos_formatados,
                "escola": escola_canonica,
                "execucao": traduzir_tokens_acao_pt(meta_p["execucao"]),
                "acoes": meta_p["acoes"],
                "componentes": meta_p["componentes"],
                "custo": meta_p["custo"],
                "acionamento": meta_p["acionamento"],
                "requerimentos": meta_p["requerimentos"],
                "distancia": meta_p["distancia"],
                "area": meta_p["area"],
                "alvos": meta_p["alvos"],
                "salvamento": meta_p["salvamento"],
                "duracao": meta_p["duracao"],
                "descricao": traduzir_tokens_acao_pt(descricao),
                "resultados": resultados,
                "elevada": elevada,
                "tabela": tabelas_foco.get(sid),
                "observacao_livro": obs_livro,
            }
        )

    classes_resumo = [
        {
            "id": cid,
            "nome": cname,
            "categoria_foco": cat,
            "introducao": concatenar_segmentos_linha(introducoes_classes[cid]),
            "total": contagem_por_classe[cid],
        }
        for cid, cname, cat in CLASSES_FOCO.values()
    ]

    return {
        "paginas": "386-407",
        "introducao": intro_geral,
        "total": len(lista_foco),
        "classes": classes_resumo,
        "lista": lista_foco,
    }


def extrair_regras_rituais(leitor: LeitorPDFPuro) -> dict[str, Any]:
    """Extrai regras completas de conjuração de Rituais e Tabelas 7–1 e 7–2 (pp. 408–409)."""
    tabela_7_1 = extrair_tabela_7_1(leitor)
    tabela_7_2 = extrair_tabela_7_2(leitor)

    def _ler_bloco_sabon(bp: int, col: int, y0: float, y1: float) -> list[tuple[float, float, str, str]]:
        spans, _ = leitor.extrair_pagina(bp - DESLOCAMENTO_PAGINA_LIVRO)
        cl = [
            s
            for s in spans
            if y0 <= s["y0"] <= y1
            and ((col == 1 and s["x0"] < 300.0) or (col == 2 and s["x0"] >= 300.0))
        ]
        cl.sort(key=lambda s: (s["y0"], s["x0"]))
        linhas: list[list[Any]] = []
        for sp in cl:
            if linhas and abs(linhas[-1][0] - sp["y0"]) < 3.0:
                linhas[-1][2].append(sp)
            else:
                linhas.append([sp["y0"], sp["x0"], [sp]])
        out: list[tuple[float, float, str, str]] = []
        for yv, xv, sps in linhas:
            sps.sort(key=lambda s: s["x0"])
            out.append((yv, xv, sps[0]["font"], unir_texto_spans(sps)))
        return out

    def _juntar_paragrafos(linhas: list[tuple[float, float, str, str]], x_col: float) -> str:
        pars: list[list[str]] = []
        for _y, xv, _fn, txt in linhas:
            if not pars or abs(xv - (x_col + 9.0)) < 1.8:
                pars.append([txt])
            else:
                pars[-1].append(txt)
        return "\n\n".join(concatenar_segmentos_linha(p) for p in pars if p)

    p408_c1 = _ler_bloco_sabon(408, 1, 80.0, 745.0)
    p408_c2 = _ler_bloco_sabon(408, 2, 385.0, 745.0)
    p409_c1 = _ler_bloco_sabon(409, 1, 60.0, 305.0)

    introducao = _juntar_paragrafos(
        [l for l in p408_c1 if l[0] < 120.0], 76.5
    )
    conjurando_rituais = _juntar_paragrafos(
        [l for l in p408_c1 if 158.0 <= l[0] <= 470.0], 76.5
    )
    aprendendo_rituais = _juntar_paragrafos(
        [l for l in p408_c1 if 492.0 <= l[0] <= 570.0], 76.5
    )
    custo = _juntar_paragrafos(
        [l for l in p408_c1 if 595.0 <= l[0]], 76.5
    )
    conjuradores_secundarios = _juntar_paragrafos(
        [l for l in p408_c2 if 400.0 <= l[0] <= 480.0], 315.0
    )
    testes = _juntar_paragrafos(
        [l for l in p408_c2 if 502.0 <= l[0] <= 675.0], 315.0
    )
    testes_sec_texto = (
        _juntar_paragrafos([l for l in p408_c2 if 700.0 <= l[0]], 315.0)
        + "\n\n"
        + _juntar_paragrafos([l for l in p409_c1 if l[0] <= 135.0], 67.5)
    ).strip()

    # Extrai os 4 resultados de testes secundários da p. 409 (y = 135..215)
    resultados_sec: dict[str, str] = {}
    res_atual: str | None = None
    res_buf: list[str] = []
    for _y, _x, fn, txt in [l for l in p409_c1 if 136.0 <= l[0] <= 215.0]:
        rot_achado = next(
            (r for r in ("Sucesso Crítico", "Sucesso", "Falha Crítica", "Falha") if fn == "SabonLTStd-Bold" and txt.startswith(r)),
            None,
        )
        if rot_achado:
            if res_atual:
                resultados_sec[ROTULOS_RESULTADOS[res_atual]] = concatenar_segmentos_linha(res_buf)
            res_atual = rot_achado
            res_buf = [txt[len(rot_achado) :].strip()]
        elif res_atual:
            res_buf.append(txt)
    if res_atual:
        resultados_sec[ROTULOS_RESULTADOS[res_atual]] = concatenar_segmentos_linha(res_buf)

    efeito = _juntar_paragrafos(
        [l for l in p409_c1 if 240.0 <= l[0] <= 295.0], 67.5
    )

    return {
        "paginas": "408-409",
        "introducao": introducao,
        "conjurando_rituais": conjurando_rituais,
        "aprendendo_rituais": aprendendo_rituais,
        "custo": custo,
        "conjuradores_secundarios": conjuradores_secundarios,
        "testes": testes,
        "testes_secundarios": {
            "descricao": testes_sec_texto,
            "resultados": resultados_sec,
        },
        "efeito": efeito,
        "tabela_7_1_criacao_de_criaturas": tabela_7_1,
        "tabela_7_2_rituais_por_nivel": tabela_7_2,
    }


def extrair_rituais(
    leitor: LeitorPDFPuro, tabela_7_2: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Extrai todos os 20 rituais das páginas 409–415."""
    mapa_nomes_t72 = {it["id"]: it["nome"] for it in tabela_7_2}
    excluir = [
        (409, 1, 0.0, 350.0),  # Regras anteriores ao ritual Aliado Planar
        (409, 2, 0.0, 330.0),  # Tabela 7-2 (preservando y>=330 para fim de Aliado Planar!)
    ]

    brutas: list[dict[str, Any]] = []
    atual: dict[str, Any] | None = None

    for bp in range(409, 416):
        idx = bp - DESLOCAMENTO_PAGINA_LIVRO
        spans, hrules = leitor.extrair_pagina(idx)
        for col in (1, 2):
            eventos = construir_eventos_coluna(spans, hrules, bp, col, excluir_faixas=excluir)
            for et, ey, payload in eventos:
                if et == "LINE":
                    sps = payload[4]
                    txt = unir_texto_spans(sps)
                    if not txt or sps[0]["font"] == "Taroca":
                        continue
                    m = re.match(r"^(.+?)\s+RITUAL\s+(\d+)$", txt)
                    if m and any(s["font"] == "GoodOT-CondBold" and s["size"] >= 11.0 for s in sps):
                        if atual is not None:
                            brutas.append(atual)
                        atual = {
                            "titulo_pdf": m.group(1).strip(),
                            "nivel_cabecalho": int(m.group(2)),
                            "pagina": bp,
                            "eventos": [],
                        }
                        continue
                if atual is not None:
                    atual["eventos"].append((et, bp, col, ey, payload))

    if atual is not None:
        brutas.append(atual)

    rituais: list[dict[str, Any]] = []
    for sp in brutas:
        tracos_brutos, linhas_meta, linhas_corpo, linhas_elevada = _particionar_secoes_entrada(
            sp["eventos"]
        )
        meta_p = _parsear_metadados(linhas_meta, eh_ritual=True)
        descricao, resultados = _montar_paragrafos_corpo(linhas_corpo)
        intro_elevada, elevada = _parsear_elevada(linhas_elevada)
        if intro_elevada:
            descricao = f"{descricao}\n\n{intro_elevada}" if descricao else intro_elevada

        sid = slugify(sp["titulo_pdf"])
        escolas = [ESCOLAS_MAIUSCULAS[t] for t in tracos_brutos if t in ESCOLAS_MAIUSCULAS]
        raridade = "raro" if "RARO" in tracos_brutos else ("incomum" if "INCOMUM" in tracos_brutos else "comum")
        tracos_formatados = [formatar_traco(t) for t in tracos_brutos]

        obs_livro = None
        if sid == "ressurreicao":
            obs_livro = "Erro tipográfico no PDF original (p. 415): cláusula impressa como 'Elevado (8º)' no masculino."
        elif sid == "criar_morto_vivo":
            obs_livro = None

        nome_canonico = formatar_titulo_pt(sp["titulo_pdf"])
        rituais.append(
            {
                "id": sid,
                "nome": nome_canonico,
                "tipo": "ritual",
                "nivel": sp["nivel_cabecalho"],
                "pagina": sp["pagina"],
                "raridade": raridade,
                "tracos": tracos_formatados,
                "escola": escolas[0] if escolas else None,
                "escolas": escolas,
                "execucao": meta_p["execucao"],
                "acoes": meta_p["acoes"],
                "componentes": meta_p["componentes"],
                "custo": meta_p["custo"],
                "conjuradores_secundarios": meta_p["conjuradores_secundarios"],
                "teste_primario": meta_p["teste_primario"],
                "testes_secundarios": meta_p["testes_secundarios"],
                "distancia": meta_p["distancia"],
                "area": meta_p["area"],
                "alvos": meta_p["alvos"],
                "salvamento": meta_p["salvamento"],
                "duracao": meta_p["duracao"],
                "descricao": descricao,
                "resultados": resultados,
                "elevada": elevada,
                "observacao_livro": obs_livro,
            }
        )

    return rituais


# ==============================================================================
# Consolidação e Validação
# ==============================================================================


def carregar_indice_listas_magias_01() -> tuple[dict[str, dict[str, Any]], set[str]]:
    """Carrega o índice de todas as 379 magias únicas e o conjunto das 220 já presentes em magias01.json."""
    m01 = json.loads(CAMINHO_MAGIAS_01.read_text(encoding="utf-8"))
    ids_m01 = {m["id"] for m in m01["magias"]}
    indice_listas: dict[str, dict[str, Any]] = {}
    for trad, niveis in m01["listas_de_magias"]["por_tradicao"].items():
        for nk, items in niveis.items():
            lvl = 0 if nk == "truques_magicos" else int(nk)
            for it in items:
                sid = it["id"]
                if sid not in indice_listas:
                    indice_listas[sid] = {
                        "id": sid,
                        "nome": it["nome"],
                        "nivel": lvl,
                        "escola": it["escola"],
                        "raridade": it["raridade"],
                        "elevavel": it["elevavel"],
                        "tradicoes": set(),
                        "resumos": set(),
                    }
                indice_listas[sid]["tradicoes"].add(trad)
                indice_listas[sid]["resumos"].add(it["resumo"])
    return indice_listas, ids_m01


def montar_dados_magias_02() -> dict[str, Any]:
    """Orquestra a extração, consolidação e montagem do schema `dados/magias02.json`."""
    assert CAMINHO_PDF.exists(), f"Arquivo PDF não encontrado: {CAMINHO_PDF}"
    assert CAMINHO_MAGIAS_01.exists(), f"Arquivo complementar não encontrado: {CAMINHO_MAGIAS_01}"

    indice_listas, _ids_m01 = carregar_indice_listas_magias_01()
    leitor = LeitorPDFPuro(CAMINHO_PDF)

    quadros_auxiliares = [extrair_quadro_servo_invisivel(leitor)]
    magias = extrair_magias_regulares(leitor, indice_listas)
    magias_de_foco = extrair_magias_de_foco(leitor)
    regras_rituais = extrair_regras_rituais(leitor)
    rituais = extrair_rituais(leitor, regras_rituais["tabela_7_2_rituais_por_nivel"])

    truques_reg = sum(1 for m in magias if m["tipo"] == "truque_magico")
    magias_1_10_reg = sum(1 for m in magias if m["tipo"] == "magia")
    foco_por_classe = {c["id"]: c["total"] for c in magias_de_foco["classes"]}
    truques_foco = sum(1 for f in magias_de_foco["lista"] if f["tipo"] == "truque_magico_foco")
    magias_foco = sum(1 for f in magias_de_foco["lista"] if f["tipo"] == "foco")

    return {
        "meta": {
            "sistema": "Pathfinder 2ª Edição (Livro Básico)",
            "capitulo": "Capítulo 7: Magias (Parte 2 — Descrições M–Z, Magias de Foco e Rituais)",
            "fonte_pdf": "ref/Enchacent02.pdf",
            "paginas_livro": "359-415",
            "versao": "1.0.0",
            "escopo_parte": (
                "Contém as 159 descrições de magias restantes das listas (Mensageiro Animal a Zona da Verdade, pp. 359–385), "
                "o quadro auxiliar Servo Invisível Criatura –1 (p. 377), todas as 158 Magias de Foco das 7 classes conjuradoras/ki "
                "(pp. 386–407), as regras completas de Rituais com as Tabelas 7–1 e 7–2 (pp. 408–409) e todos os 20 Rituais "
                "(pp. 409–415). Complementa diretamente dados/magias01.json (Abrandar a Melhorar Alimentos)."
            ),
            "totais": {
                "magias_descritas_nesta_parte": len(magias),
                "truques_magicos_descritos": truques_reg,
                "magias_nivel_1_a_10_descritas": magias_1_10_reg,
                "total_magias_capitulo_7_combinado": 220 + len(magias),
                "quadros_auxiliares": len(quadros_auxiliares),
                "magias_de_foco_total": len(magias_de_foco["lista"]),
                "truques_magicos_foco": truques_foco,
                "magias_foco": magias_foco,
                "magias_de_foco_por_classe": foco_por_classe,
                "rituais_total": len(rituais),
                "tabelas_embutidas_magias_e_foco": 4,
                "tabelas_rituais": 2,
            },
            "incongruencias_livro": [
                {
                    "id": "terreno_alucinatorio_tradicoes",
                    "magia": "Terreno Alucinatório",
                    "pagina": 381,
                    "descricao": (
                        "Nas Listas de Magias (dados/magias01.json, pp. 308, 313 e 315) consta como arcana, ocultista e primal, "
                        "porém na descrição da p. 381 o campo Tradições está impresso como 'arcana, divina, ocultista'."
                    ),
                    "tratamento": "Preservado o valor impresso na descrição ('arcana', 'divina', 'ocultista') com nota em observacao_livro.",
                },
                {
                    "id": "pagina_secreta_sem_linha_divisoria",
                    "magia": "Página Secreta",
                    "pagina": 365,
                    "descricao": "A diagramação omite a linha horizontal divisória entre 'Duração ilimitada' e o texto descritivo.",
                    "tratamento": "Separado automaticamente pelo encerramento dos rótulos de metadados em negrito.",
                },
                {
                    "id": "observacao_inexoravel_areas_plural",
                    "magia": "Observação Inexorável",
                    "pagina": 364,
                    "descricao": "O metadado de área aparece impresso no plural ('Áreas explosão de 6 metros').",
                    "tratamento": "Mapeado normalmente para o campo area com nota em observacao_livro.",
                },
                {
                    "id": "tracos_erros_tipograficos_e_variantes",
                    "magias": [
                        "Muralha de Pedra (p. 362)",
                        "Prender Alma (p. 369)",
                        "Sifonar Sombra (p. 377)",
                        "Pesadelo Compartilhado (p. 395)",
                        "Visão do Adivinho (p. 406)",
                    ],
                    "descricao": (
                        "Erros gráficos e variantes de tradução nos traços do PDF: 'CONJURAÇÅO' (p. 362), 'MALIGNO' (p. 369), "
                        "'SOMBRAS' (p. 377), 'INCAPACITAÇAO' (p. 395) e 'CONCETRAÇÃO' (p. 406)."
                    ),
                    "tratamento": "Normalizados respectivamente para 'Conjuração', 'Mal', 'Sombra', 'Incapacitação' e 'Concentração'.",
                },
                {
                    "id": "ressurreicao_elevado_masculino",
                    "ritual": "Ressurreição",
                    "pagina": 415,
                    "descricao": "A cláusula do 8º nível foi impressa no masculino ('Elevado (8º)') em vez de 'Elevada (8º)'.",
                    "tratamento": "Capturada normalmente na lista elevada e registrada em observacao_livro.",
                },
                {
                    "id": "erros_tipograficos_corpo",
                    "magias": ["Muralha de Gelo (p. 362)", "Movimento Elemental (p. 404)"],
                    "descricao": "Pequenos erros gráficos preservados no corpo original: 'magia é perdida.a.' (p. 362) e 'dependo de seu elemento' (p. 404).",
                    "tratamento": "Texto preservado fielmente e documentado em observacao_livro.",
                },
            ],
        },
        "quadros_auxiliares": quadros_auxiliares,
        "magias": magias,
        "magias_de_foco": magias_de_foco,
        "regras_rituais": regras_rituais,
        "rituais": rituais,
    }


def validar_dados_magias_02(dados: dict[str, Any]) -> None:
    """Executa bateria de asserções estruturais, completude e cruzamento 1:1 com magias01.json."""
    indice_listas, ids_m01 = carregar_indice_listas_magias_01()

    # 1. Quadros auxiliares
    quadros = dados["quadros_auxiliares"]
    assert len(quadros) == 1
    assert quadros[0]["id"] == "servo_invisivel_criatura"
    assert quadros[0]["criatura"]["nivel"] == -1
    assert quadros[0]["criatura"]["ca"] == 13
    assert quadros[0]["criatura"]["pv"] == 4

    # 2. Magias regulares (159 restantes A–Z, completando 379 no total)
    magias = dados["magias"]
    assert len(magias) == 159, f"Esperado 159 magias regulares, obtido {len(magias)}"
    assert magias[0]["id"] == "mensageiro_animal" and magias[0]["pagina"] == 359
    assert magias[-1]["id"] == "zona_da_verdade" and magias[-1]["pagina"] == 385

    ids_m02 = [m["id"] for m in magias]
    assert len(ids_m02) == len(set(ids_m02)), "IDs duplicados em magias"
    assert not (set(ids_m02) & ids_m01), "Sobreposição entre magias01 e magias02"
    assert set(ids_m02) | ids_m01 == set(indice_listas.keys()), (
        f"União magias01+magias02 difere das 379 listas! Faltando: {set(indice_listas.keys()) - (set(ids_m02) | ids_m01)}"
    )

    for m in magias:
        sid = m["id"]
        li = indice_listas[sid]
        assert m["nivel"] == li["nivel"], f"Nível divergente em {sid}: {m['nivel']} vs {li['nivel']}"
        assert m["escola"] == li["escola"], f"Escola divergente em {sid}: {m['escola']} vs {li['escola']}"
        assert m["raridade"] == li["raridade"], f"Raridade divergente em {sid}: {m['raridade']} vs {li['raridade']}"
        assert bool(m["elevada"]) == li["elevavel"], f"Elevada divergente em {sid}"
        if sid != "terreno_alucinatorio":
            assert set(m["tradicoes"]) == li["tradicoes"], f"Tradições divergentes em {sid}"

        assert m["tradicoes"], f"Sem tradições: {sid}"
        assert m["execucao"], f"Sem execução: {sid}"
        assert m["descricao"], f"Sem descrição: {sid}"
        assert len(m["execucao"]) <= 80, f"Execução longa demais em {sid}: {m['execucao']}"
        for campo_meta in ("distancia", "area", "alvos", "salvamento", "duracao", "custo", "requerimentos"):
            val_meta = m[campo_meta]
            if val_meta:
                assert len(val_meta) <= 170, f"{campo_meta} longo demais em {sid}: {val_meta}"
                if campo_meta != "requerimentos":
                    assert "Você " not in val_meta, f"Possível sangria em {campo_meta} de {sid}: {val_meta}"

    por_id = {m["id"]: m for m in magias}
    assert "PERCEPÇÃO +0" not in por_id["servo_invisivel"]["descricao"].upper()
    assert "Corpo de Força" not in por_id["servo_invisivel"]["descricao"]
    assert por_id["rajada_prismatica"]["tabela"] is not None
    assert len(por_id["rajada_prismatica"]["tabela"]) == 8
    assert "1 Vermelho" not in por_id["rajada_prismatica"]["descricao"]
    assert por_id["pagina_secreta"]["duracao"] == "ilimitada"
    assert por_id["pagina_secreta"]["descricao"].startswith("Você muda o texto")
    assert por_id["muralha_cromatica"]["elevada"] is not None
    assert "5. Azul" in por_id["muralha_cromatica"]["elevada"][0]["efeito"]
    assert "Conjuração" in por_id["muralha_de_pedra"]["tracos"]
    assert "Mal" in por_id["prender_alma"]["tracos"]
    assert "Sombra" in por_id["sifonar_sombra"]["tracos"]

    # 3. Magias de Foco (158)
    mf = dados["magias_de_foco"]
    lista_foco = mf["lista"]
    assert len(lista_foco) == 158, f"Esperado 158 magias de foco, obtido {len(lista_foco)}"
    ids_foco = [f["id"] for f in lista_foco]
    assert len(ids_foco) == len(set(ids_foco)), "IDs duplicados em magias_de_foco"

    esperado_foco_classes = {
        "bardo": 13,
        "campeao": 6,
        "clerigo": 74,
        "druida": 9,
        "feiticeiro": 30,
        "mago": 17,
        "monge": 9,
    }
    obs_classes = {c["id"]: c["total"] for c in mf["classes"]}
    assert obs_classes == esperado_foco_classes, f"Contagem foco por classe incorreta: {obs_classes}"
    assert sum(1 for f in lista_foco if f["tipo"] == "truque_magico_foco") == 7
    assert sum(1 for f in lista_foco if f["tipo"] == "foco") == 151
    assert sum(1 for f in lista_foco if f["classe_id"] == "clerigo" and f["dominio"]) == 74

    foco_id = {f["id"]: f for f in lista_foco}
    assert foco_id["salpico_de_arte"]["tabela"] is not None and len(foco_id["salpico_de_arte"]["tabela"]) == 4
    assert "1 Branco" not in foco_id["salpico_de_arte"]["descricao"]
    assert foco_id["ira_abissal"]["tabela"] is not None and len(foco_id["ira_abissal"]["tabela"]) == 4
    assert "1 Céus" not in foco_id["ira_abissal"]["descricao"]
    assert foco_id["sopro_de_dragao"]["tabela"] is not None and len(foco_id["sopro_de_dragao"]["tabela"]) == 6
    assert "Azul ou bronze" not in foco_id["sopro_de_dragao"]["descricao"]
    assert "16º ou Inferior" in foco_id["aria_fatal"]["descricao"]
    assert "18º ou Superior" in foco_id["aria_fatal"]["descricao"]
    assert [e["nivel"] for e in foco_id["floreio_artistico"]["elevada"]] == ["7º", "10º"]
    assert [e["nivel"] for e in foco_id["morfia_selvagem"]["elevada"]] == ["6º", "10º"]
    assert [e["nivel"] for e in foco_id["movimento_elemental"]["elevada"]] == ["6º", "9º"]
    assert [e["nivel"] for e in foco_id["manto_de_invisibilidade"]["elevada"]] == ["6º", "8º"]
    assert "Incapacitação" in foco_id["pesadelo_compartilhado"]["tracos"]
    assert "Concentração" in foco_id["visao_do_adivinho"]["tracos"]

    for f in lista_foco:
        assert f["execucao"], f"Foco sem execução: {f['id']}"
        assert f["descricao"], f"Foco sem descrição: {f['id']}"
        assert "podem receber as magias de" not in f["descricao"], f"Sangria de cabeçalho de classe em {f['id']}"

    # 4. Regras de Rituais e 20 Rituais
    rr = dados["regras_rituais"]
    assert len(rr["tabela_7_1_criacao_de_criaturas"]) == 18
    assert len(rr["tabela_7_2_rituais_por_nivel"]) == 20
    assert len(rr["testes_secundarios"]["resultados"]) == 4

    rituais = dados["rituais"]
    assert len(rituais) == 20, f"Esperado 20 rituais, obtido {len(rituais)}"
    assert [(r["id"], r["nivel"]) for r in rituais] == sorted(
        [(it["id"], it["nivel"]) for it in rr["tabela_7_2_rituais_por_nivel"]],
        key=lambda x: x[0],
    ) or {r["id"]: r["nivel"] for r in rituais} == {
        it["id"]: it["nivel"] for it in rr["tabela_7_2_rituais_por_nivel"]
    }

    rit_id = {r["id"]: r for r in rituais}
    for r in rituais:
        assert r["execucao"], f"Ritual sem execução: {r['id']}"
        assert r["teste_primario"], f"Ritual sem Teste Primário: {r['id']}"
        assert r["descricao"], f"Ritual sem descrição: {r['id']}"

    assert "ritual de expiação para recuperar a confiança de sua divindade" in rit_id["aliado_planar"]["resultados"]["falha_critica"]
    assert "ignorando todos os seus comandos subsequentes." in rit_id["criar_morto_vivo"]["resultados"]["sucesso_critico"]
    assert "Ele perseguirá" not in rit_id["criar_morto_vivo"]["descricao"]
    assert "\n\n16º ou Inferior" in foco_id["aria_fatal"]["descricao"]
    assert "\n\n18º ou Superior" in foco_id["aria_fatal"]["descricao"]
    assert "terr eno" not in por_id["muralha_de_vento"]["descricao"]
    assert "terreno difícil" in por_id["muralha_de_vento"]["descricao"]
    assert rit_id["aprisionamento"]["elevada"] is not None
    assert [e["nivel"] for e in rit_id["aprisionamento"]["elevada"]] == ["9º", "10º"]
    assert [e["nivel"] for e in rit_id["obrigacao"]["elevada"]] == ["5º", "7º", "9º"]
    assert [e["nivel"] for e in rit_id["ressurreicao"]["elevada"]] == ["6º", "7º", "8º", "9º", "10º"]
    assert "Amarra Planar" in rit_id["amarra_planar"]["nome"]
    assert "Ocultismo" in (rit_id["chamar_espirito"]["testes_secundarios"] or "")

    # 5. Qualidade global de texto (sem caracteres de controle, ícones partidos ou quebras de hífen residuais)
    padrao_hifen_quebrado = re.compile(r"[A-Za-zÀ-ÿ]+\s+-\s*[a-zà-ÿ]+|[A-Za-zÀ-ÿ]+-\s+[a-zà-ÿ]+")
    for grupo, itens in [("magias", magias), ("foco", lista_foco), ("rituais", rituais)]:
        for item in itens:
            tudo = json.dumps(item, ensure_ascii=False)
            assert "\x08" not in tudo, f"Caractere \\x08 em {grupo}:{item['id']}"
            assert "[one- " not in tudo and "[one-\n" not in tudo, f"Ícone quebrado em {grupo}:{item['id']}"
            assert not padrao_hifen_quebrado.search(item["descricao"]), (
                f"Quebra de hífen residual em {grupo}:{item['id']}: {padrao_hifen_quebrado.search(item['descricao']).group(0)!r}"
            )
            if item.get("resultados"):
                for r_k, r_v in item["resultados"].items():
                    assert not padrao_hifen_quebrado.search(r_v), (
                        f"Quebra de hífen residual em {grupo}:{item['id']}.{r_k}"
                    )
            if item.get("elevada"):
                for el in item["elevada"]:
                    assert not padrao_hifen_quebrado.search(el["efeito"]), (
                        f"Quebra de hífen residual em {grupo}:{item['id']}.elevada"
                    )


def main() -> None:
    """Executa a geração e validação completa de `dados/magias02.json`."""
    dados = montar_dados_magias_02()
    validar_dados_magias_02(dados)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_SAIDA.open("w", encoding="utf-8") as arq:
        json.dump(dados, arq, ensure_ascii=False, indent=2)
        arq.write("\n")

    tamanho = CAMINHO_SAIDA.stat().st_size
    t = dados["meta"]["totais"]
    print(f"Arquivo gerado com sucesso: {CAMINHO_SAIDA} ({tamanho} bytes)")
    print(
        f"Magias regulares (M-Z): {t['magias_descritas_nesta_parte']} "
        f"({t['truques_magicos_descritos']} truques + {t['magias_nivel_1_a_10_descritas']} magias) "
        f"| Combinado Cap. 7: {t['total_magias_capitulo_7_combinado']}/379"
    )
    print(
        f"Magias de foco: {t['magias_de_foco_total']} "
        f"({t['truques_magicos_foco']} truques de composição + {t['magias_foco']} magias de foco)"
    )
    print(f"Foco por classe: {t['magias_de_foco_por_classe']}")
    print(f"Rituais: {t['rituais_total']} | Quadros auxiliares: {t['quadros_auxiliares']}")


if __name__ == "__main__":
    main()
