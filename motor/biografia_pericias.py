"""Seleção de Biografia e cálculo de Perícias, Saberes e Idiomas."""

from __future__ import annotations

import random
from typing import Any

from .dados import BaseDados
from .util import atributo_id, normalizar


def _saberes_equivalentes(a: str, b: str) -> bool:
    return normalizar(a) == normalizar(b)


def _limpar_nome_saber(saber_bruto: str, conceito: dict[str, Any]) -> str:
    """Resolve saberes genéricos com exemplos entre parênteses (saber_tematico=True)."""
    if "ex.:" in saber_bruto or "(" in saber_bruto:
        return conceito.get("saber_sugerido") or saber_bruto.split("(")[0].strip()
    return saber_bruto


def selecionar_biografia(
    dados: BaseDados,
    conceito: dict[str, Any],
    ancestralidade: dict[str, Any],
    biografia_id: str | None = None,
    rng: random.Random | None = None,
) -> tuple[dict[str, Any], bool]:
    """Retorna `(biografia_dict, foi_procedural)`.

    No modo procedural, pontua as biografias recomendadas pelo conceito pela
    sinergia de atributos com a prioridade do conceito e afinidade com a
    ancestralidade, escolhendo dentre as melhores candidatas usando `rng`.
    """
    if biografia_id and biografia_id != "procedural":
        bio = dados.biografias.get(biografia_id)
        if bio is None:
            raise ValueError(f"Biografia inválida: '{biografia_id}'.")
        return bio, False

    prioridade = conceito["prioridade_atributos"]
    top3_atr = set(prioridade[:3])
    tipicas_anc = {normalizar(nome) for nome in ancestralidade.get("biografias_tipicas", [])}

    candidatos_ids = list(conceito.get("biografias_recomendadas", [])) or list(dados.biografias.keys())
    avaliados: list[tuple[int, dict[str, Any]]] = []

    for idx, bid in enumerate(candidatos_ids):
        bio = dados.biografias[bid]
        pontos = max(1, 8 - idx * 2)
        opcoes_atr = [atributo_id(o) for o in bio["melhorias_atributo_opcoes"]]
        for atr in opcoes_atr:
            if atr == prioridade[0]:
                pontos += 20
            elif atr == prioridade[1]:
                pontos += 12
            elif atr in top3_atr:
                pontos += 6
        if normalizar(bio["nome"]) in tipicas_anc:
            pontos += 4
        avaliados.append((pontos, bio))

    avaliados.sort(key=lambda par: par[0], reverse=True)
    melhor_nota = avaliados[0][0]
    elegiveis = [bio for nota, bio in avaliados if nota >= melhor_nota - 6][:3]

    if rng is not None and len(elegiveis) > 1:
        escolhida = rng.choice(elegiveis)
    else:
        escolhida = elegiveis[0]

    return escolhida, True


def calcular_pericias(
    dados: BaseDados,
    ancestralidade: dict[str, Any],
    heranca: dict[str, Any],
    biografia: dict[str, Any],
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    conceito: dict[str, Any],
    mod_int: int,
    extras_pericias: int = 0,
    divindade: dict[str, Any] | None = None,
    pericias_ancestrais_fixas: list[str] | None = None,
    saber_ancestral: tuple[str, str] | None = None,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Determina todas as perícias treinadas e os 2 slots de Saber do personagem."""
    treinadas: dict[str, str] = {}
    origens: dict[str, str] = {}
    escolhas_livres = 0

    def conceder(pid: str | None, origem: str) -> None:
        nonlocal escolhas_livres
        if not pid or pid not in dados.pericias:
            return
        if pid in treinadas:
            # Regra PF2E: se receber treinamento em perícia já treinada, ganha 1 escolha livre
            escolhas_livres += 1
        else:
            treinadas[pid] = "treinado"
            origens[pid] = origem

    prioridades = list(conceito["pericias_prioritarias"])

    def escolher_melhor_opcao(opcoes_ids: list[str]) -> str | None:
        disponiveis = [p for p in opcoes_ids if p and p not in treinadas]
        base = disponiveis or opcoes_ids
        ordem_pri = {p: i for i, p in enumerate(prioridades)}
        return min(base, key=lambda p: ordem_pri.get(p, 99)) if base else None

    # 1. Biografia (se biografia tiver mais de 1 opção, ex: Discípulo Marcial -> Acrobatismo ou Atletismo)
    opcoes_bio = [dados.pericia_id(nome) for nome in biografia.get("pericia_treinada_opcoes", [])]
    opcoes_bio = [p for p in opcoes_bio if p]
    pericia_bio = escolher_melhor_opcao(opcoes_bio)
    conceder(pericia_bio, f"Biografia ({biografia['nome']})")

    # 2. Classe — perícias fixas e escolhas fixas (ex: Guerreiro: Acrobatismo ou Atletismo)
    prof_pericias = classe["proficiencias_iniciais"]["pericias"]
    for pid in prof_pericias.get("fixas", []):
        conceder(dados.pericia_id(pid) or pid, f"Classe ({classe['nome']})")

    opcoes_fixas = [dados.pericia_id(p) or p for p in prof_pericias.get("opcoes_fixas", [])]
    if opcoes_fixas:
        escolhida_fixa = escolher_melhor_opcao(opcoes_fixas)
        conceder(escolhida_fixa, f"Classe ({classe['nome']})")

    # 3. Condicionais de Subclasse / Ordem / Linhagem / Esquema / Divindade
    if subclasse:
        if "pericia_treinada" in subclasse:
            pt = subclasse["pericia_treinada"]
            lista_pt = pt if isinstance(pt, list) else [pt]
            for item in lista_pt:
                conceder(dados.pericia_id(item), f"Subclasse ({subclasse['nome']})")
        if "pericias_linhagem" in subclasse:
            for item in subclasse["pericias_linhagem"]:
                conceder(dados.pericia_id(item), f"Linhagem ({subclasse['nome']})")

    condicionais = prof_pericias.get("condicionais", [])
    if "pericia_determinada_pela_divindade" in condicionais:
        if divindade and divindade.get("pericia_divina"):
            opcoes_div = [p for p in divindade["pericia_divina"] if p in dados.pericias]
            div_p = escolher_melhor_opcao(opcoes_div)
            conceder(div_p, f"Divindade ({divindade['nome']})")
        else:
            candidatos_div = [p for p in prioridades if p not in treinadas and p != "religiao"]
            div_p = candidatos_div[0] if candidatos_div else "diplomacia"
            conceder(div_p, "Divindade (Conceito)")

    for pid_anc in pericias_ancestrais_fixas or ():
        conceder(pid_anc, "Talento Ancestral")

    # 4. Herança Perita (+1 perícia) e talentos extras (ex: Perícia Natural humano = +2)
    if heranca.get("id") == "heranca_perita":
        escolhas_livres += 1
    escolhas_livres += extras_pericias

    # 5. Pool base da classe + mod INT (em PF2E, se mod INT < 0 reduz adicionais, mínimo 0 total do bloco)
    adicionais_classe = prof_pericias.get("adicionais_base", 0)
    if prof_pericias.get("soma_modificador_inteligencia", True):
        adicionais_classe = max(0, adicionais_classe + mod_int)
    escolhas_livres += adicionais_classe

    # Alocar escolhas livres: garantir topo das prioridades do conceito e variar secundárias com rng
    for p in prioridades:
        if escolhas_livres <= 0:
            break
        if p not in treinadas:
            conceder(p, "Escolha Livre (Conceito)")
            escolhas_livres -= 1

    # Caso ainda sobrem vagas (ex.: Ladino com INT alta), completa com outras perícias destreinadas
    if escolhas_livres > 0:
        restantes = [pid for pid in dados.pericias if pid not in treinadas and pid != "saber"]
        if rng is not None:
            rng.shuffle(restantes)
        for pid in restantes:
            if escolhas_livres <= 0:
                break
            conceder(pid, "Escolha Livre (Adicional)")
            escolhas_livres -= 1

    # Saberes (Página 1 tem 2 slots: saber_1 e saber_2)
    saber_bio = _limpar_nome_saber(biografia["saber_treinado"], conceito)
    saber_conceito = conceito.get("saber_sugerido", "")
    saber_2 = saber_conceito if saber_conceito and not _saberes_equivalentes(saber_conceito, saber_bio) else ""

    if saber_ancestral:
        nome_sab_anc = (
            saber_ancestral[0]
            if not _saberes_equivalentes(saber_ancestral[0], saber_bio)
            else "Saber Ancestral"
        )
        saber_2_dict = {
            "especializacao": nome_sab_anc,
            "grau": "treinado",
            "origem": saber_ancestral[1],
        }
    else:
        saber_2_dict = {
            "especializacao": saber_2,
            "grau": "destreinado",
            "origem": "Sugestão do Conceito" if saber_2 else "",
        }

    saberes = {
        "saber_1": {
            "especializacao": saber_bio,
            "grau": "treinado",
            "origem": f"Biografia ({biografia['nome']})",
        },
        "saber_2": saber_2_dict,
    }

    return {
        "graus": treinadas,
        "origens": origens,
        "saberes": saberes,
        "pericia_biografia_id": pericia_bio,
    }


def calcular_idiomas(
    dados: BaseDados,
    ancestralidade: dict[str, Any],
    heranca: dict[str, Any],
    classe: dict[str, Any],
    mod_int: int,
    rng: random.Random | None = None,
) -> list[str]:
    """Calcula os idiomas iniciais conforme ancestralidade, classe, herança e mod INT."""
    idiomas = list(ancestralidade.get("idiomas_iniciais", ["Comum"]))
    if classe["id"] == "druida" and "Druídico" not in idiomas:
        idiomas.append("Druídico")

    regra_idiomas = normalizar(ancestralidade.get("regra_idiomas_adicionais", ""))
    if ancestralidade["id"] == "humano" or "1 + modificador" in regra_idiomas:
        base_extras = max(1, 1 + mod_int)
    else:
        base_extras = max(0, mod_int)
    qtd_extras = base_extras + int(heranca.get("idiomas_adicionais", 0) or 0)
    if qtd_extras <= 0:
        return idiomas

    pool_anc = [
        i
        for i in ancestralidade.get("idiomas_adicionais_opcoes", [])
        if i not in idiomas and "qualquer" not in normalizar(i) and len(i) <= 25
    ]
    tabela_comuns = [
        item["idioma"]
        for item in dados.json("ancestralidades_biografias.json")["idiomas"]["tabela_2_1_idiomas_comuns"]
        if item["idioma"] not in idiomas
    ]

    if rng is not None:
        rng.shuffle(pool_anc)
        rng.shuffle(tabela_comuns)

    for candidato in pool_anc + tabela_comuns:
        if qtd_extras <= 0:
            break
        if candidato not in idiomas:
            idiomas.append(candidato)
            qtd_extras -= 1

    return idiomas
