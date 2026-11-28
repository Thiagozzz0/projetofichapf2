"""Utilitários e formatadores compartilhados entre os exportadores da ficha PF2E."""

from __future__ import annotations

import re
from typing import Any
from xml.sax.saxutils import escape

from ..util import SIGLA_GRAU, formatar_bonus, slugify


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
