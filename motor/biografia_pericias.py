"""Seleção de Biografia e cálculo de Perícias, Saberes e Idiomas."""

from __future__ import annotations

import random
from typing import Any

from .dados import BaseDados
from .regras_atributos import normalizar_escolha_atributo
from .util import ATRIBUTOS, atributo_id, normalizar


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
    escolhas_atributos: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], bool]:
    """Retorna `(biografia_dict, foi_procedural)`.

    No modo procedural, pontua as biografias recomendadas pelo conceito pela
    sinergia de atributos com a prioridade do conceito e afinidade com a
    ancestralidade, escolhendo dentre as melhores candidatas usando `rng`.
    Caso o jogador tenha escolhido manualmente um atributo para o bônus restrito
    da biografia, apenas biografias que oferecem esse atributo são consideradas.
    """
    escolhas = escolhas_atributos or {}
    modo_bio_res = normalizar_escolha_atributo(escolhas.get("biografia_restrito"))
    modo_bio_liv = normalizar_escolha_atributo(escolhas.get("biografia_livre"))
    atr_restrito_manual = modo_bio_res if modo_bio_res in ATRIBUTOS else None

    def _opcoes_bio_ids(bio: dict[str, Any]) -> list[str]:
        return [
            aid
            for o in bio["melhorias_atributo_opcoes"]
            if (aid := atributo_id(o)) is not None
        ]

    biografia_id_norm = str(biografia_id or "").strip().lower()
    if biografia_id_norm in {"aleatorio", "aleatoria", "random"}:
        todas = list(dados.biografias.values())
        if atr_restrito_manual:
            compat = [b for b in todas if atr_restrito_manual in _opcoes_bio_ids(b)]
            if compat:
                todas = compat
        escolhida = rng.choice(todas) if rng is not None else todas[0]
        return escolhida, True

    if biografia_id and biografia_id_norm != "procedural":
        bio = dados.biografias.get(biografia_id)
        if bio is None:
            raise ValueError(f"Biografia inválida: '{biografia_id}'.")
        return bio, False

    prioridade = conceito["prioridade_atributos"]
    top3_atr = set(prioridade[:3])
    tipicas_anc = {normalizar(nome) for nome in ancestralidade.get("biografias_tipicas", [])}

    candidatos_ids = list(conceito.get("biografias_recomendadas", [])) or list(dados.biografias.keys())
    if atr_restrito_manual:
        filtrados = [
            bid for bid in candidatos_ids if atr_restrito_manual in _opcoes_bio_ids(dados.biografias[bid])
        ]
        if not filtrados:
            filtrados = [
                bid
                for bid, b in dados.biografias.items()
                if atr_restrito_manual in _opcoes_bio_ids(b)
            ]
        candidatos_ids = filtrados

    avaliados: list[tuple[int, dict[str, Any]]] = []

    for idx, bid in enumerate(candidatos_ids):
        bio = dados.biografias[bid]
        pontos = max(1, 8 - idx * 2)
        opcoes_atr = _opcoes_bio_ids(bio)
        for atr in opcoes_atr:
            if atr == prioridade[0]:
                pontos += 20
            elif atr == prioridade[1]:
                pontos += 12
            elif atr in top3_atr:
                pontos += 6
        if modo_bio_liv in ATRIBUTOS and any(atr != modo_bio_liv for atr in opcoes_atr):
            pontos += 10
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


def listar_catalogo_pericias(dados: BaseDados) -> list[dict[str, Any]]:
    """Retorna as 16 perícias treináveis (excluindo Saber) a partir de dados/pericias.json."""
    return [
        {
            "id": p["id"],
            "nome": p["nome"],
            "atributo_chave": p.get("atributo_chave", ""),
            "atributo_sigla": p.get("atributo_sigla", ""),
            "sofre_penalidade_armadura": bool(p.get("sofre_penalidade_armadura", False)),
            "descricao": p.get("descricao", ""),
        }
        for p in dados.pericias.values()
        if p["id"] != "saber"
    ]


def resumo_pericias_classe(dados: BaseDados, classe: dict[str, Any]) -> dict[str, Any]:
    """Extrai de dados/classes*.json as regras de perícias iniciais da classe e suas subclasses."""
    prof = classe["proficiencias_iniciais"]["pericias"]
    fixas = [dados.pericia_id(p) or p for p in prof.get("fixas", [])]
    fixas = [p for p in fixas if p in dados.pericias and p != "saber"]
    opcoes_fixas = [dados.pericia_id(p) or p for p in prof.get("opcoes_fixas", [])]
    opcoes_fixas = [p for p in opcoes_fixas if p in dados.pericias and p != "saber"]

    subclasses_pericias: dict[str, list[str]] = {}
    for sub in classe.get("subclasses", {}).get("opcoes", []):
        lista: list[str] = []
        pt = sub.get("pericia_treinada")
        if pt:
            for item in (pt if isinstance(pt, list) else [pt]):
                pid = dados.pericia_id(item)
                if pid and pid != "saber" and pid not in lista:
                    lista.append(pid)
        for item in sub.get("pericias_linhagem") or []:
            pid = dados.pericia_id(item)
            if pid and pid != "saber" and pid not in lista:
                lista.append(pid)
        if lista:
            subclasses_pericias[sub["id"]] = lista

    return {
        "fixas": fixas,
        "opcoes_fixas": opcoes_fixas,
        "adicionais_base": int(prof.get("adicionais_base", 0) or 0),
        "soma_modificador_inteligencia": bool(prof.get("soma_modificador_inteligencia", True)),
        "usa_pericia_divindade": "pericia_determinada_pela_divindade" in (prof.get("condicionais") or []),
        "subclasses_pericias": subclasses_pericias,
    }


def contar_incrementos_pericia(classe: dict[str, Any], nivel: int = 1) -> int:
    """Conta quantos Incrementos de Perícia a classe recebe entre o 2º nível e `nivel`."""
    nivel_lim = max(1, int(nivel))
    if nivel_lim < 2:
        return 0
    total = 0
    for row in classe.get("tabela_progressao", []):
        niv_row = int(row.get("nivel", 1))
        if 2 <= niv_row <= nivel_lim:
            if any(normalizar(x) == "incremento de pericia" for x in row.get("caracteristicas", [])):
                total += 1
    return total


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
    nivel: int = 1,
    escolhas_pericias: dict[str, Any] | None = None,
    validar_limite: bool = True,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Determina todas as perícias treinadas, incrementos (N2–N5) e os 2 slots de Saber."""
    nivel_alvo = max(1, int(nivel))
    treinadas: dict[str, str] = {}
    origens: dict[str, str] = {}
    escolhas_livres = 0
    sobreposicoes: list[str] = []

    esc = escolhas_pericias or {}
    modo_esc = normalizar(str(esc.get("modo") or "procedural"))
    modo_manual = modo_esc in ("personalizado", "manual") or any(
        esc.get(k) not in (None, "", "procedural", [])
        for k in (
            "pericia_biografia_id",
            "pericia_classe_fixa_id",
            "pericia_divindade_id",
            "pericias_livres",
            "incrementos_pericias",
        )
    )

    def _eh_proc_per(val: Any) -> bool:
        return val is None or (isinstance(val, str) and normalizar(val) in ("", "procedural", "auto", "automatico", "aleatorio"))

    def conceder(pid: str | None, origem: str) -> None:
        nonlocal escolhas_livres
        if not pid or pid not in dados.pericias:
            return
        if pid in treinadas:
            # Regra PF2E: se receber treinamento em perícia já treinada, ganha 1 escolha livre
            escolhas_livres += 1
            sobreposicoes.append(pid)
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
    bio_req = esc.get("pericia_biografia_id") if modo_manual else None
    if not _eh_proc_per(bio_req):
        bio_req_id = dados.pericia_id(str(bio_req)) or str(bio_req).strip()
        if opcoes_bio and bio_req_id not in opcoes_bio:
            raise ValueError(
                f"Perícia de biografia '{bio_req}' inválida para '{biografia['nome']}' "
                f"(opções: {', '.join(opcoes_bio)})."
            )
        pericia_bio = bio_req_id
    else:
        pericia_bio = escolher_melhor_opcao(opcoes_bio)
    conceder(pericia_bio, f"Biografia ({biografia['nome']})")

    # 2. Classe — perícias fixas e escolhas fixas (ex: Guerreiro: Acrobatismo ou Atletismo)
    prof_pericias = classe["proficiencias_iniciais"]["pericias"]
    for pid in prof_pericias.get("fixas", []):
        conceder(dados.pericia_id(pid) or pid, f"Classe ({classe['nome']})")

    opcoes_fixas = [dados.pericia_id(p) or p for p in prof_pericias.get("opcoes_fixas", [])]
    if opcoes_fixas:
        cls_req = esc.get("pericia_classe_fixa_id") if modo_manual else None
        if not _eh_proc_per(cls_req):
            cls_req_id = dados.pericia_id(str(cls_req)) or str(cls_req).strip()
            if cls_req_id not in opcoes_fixas:
                raise ValueError(
                    f"Perícia inicial '{cls_req}' inválida para {classe['nome']} "
                    f"(opções: {', '.join(opcoes_fixas)})."
                )
            escolhida_fixa = cls_req_id
        else:
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
            div_req = esc.get("pericia_divindade_id") if modo_manual else None
            if not _eh_proc_per(div_req) and len(opcoes_div) > 1:
                div_req_id = dados.pericia_id(str(div_req)) or str(div_req).strip()
                if div_req_id not in opcoes_div:
                    raise ValueError(
                        f"Perícia divina '{div_req}' inválida para {divindade['nome']} "
                        f"(opções: {', '.join(opcoes_div)})."
                    )
                div_p = div_req_id
            else:
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

    vagas_livres_total = escolhas_livres
    manuais_aplicadas: list[str] = []

    # 6. Aplicar escolhas livres manuais (se fornecidas) respeitando o teto exato de vagas
    if modo_manual and esc.get("pericias_livres") is not None and not _eh_proc_per(esc.get("pericias_livres")):
        raw_livres = esc.get("pericias_livres")
        if not isinstance(raw_livres, list):
            raise ValueError("Campo 'pericias_livres' deve ser uma lista de IDs de perícias.")
        vistos_man: set[str] = set()
        livres_req: list[str] = []
        for item in raw_livres:
            pid = dados.pericia_id(str(item)) or str(item).strip()
            if pid not in dados.pericias or pid == "saber":
                raise ValueError(f"Perícia livre desconhecida ou inválida: '{item}'.")
            if pid in vistos_man:
                raise ValueError(f"Perícia duplicada na seleção manual: '{dados.pericias[pid]['nome']}'.")
            vistos_man.add(pid)
            livres_req.append(pid)

        novas_manuais = [pid for pid in livres_req if pid not in treinadas]
        if validar_limite and len(novas_manuais) > escolhas_livres:
            raise ValueError(
                f"Você selecionou {len(novas_manuais)} perícias livres, mas o personagem possui apenas "
                f"{escolhas_livres} vaga(s) disponível(is)."
            )
        for pid in novas_manuais[: max(0, escolhas_livres)]:
            conceder(pid, "Escolha Manual (Jogador)")
            escolhas_livres -= 1
            manuais_aplicadas.append(pid)

    # 7. Alocar vagas livres restantes de forma procedural: prioridades do conceito + restantes
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

    # 8. Incrementos de Perícia dos níveis 2 a 5 (treinado -> especialista ou destreinado -> treinado)
    qtd_incrementos = contar_incrementos_pericia(classe, nivel_alvo)
    incrementos_aplicados: list[str] = []
    if qtd_incrementos > 0:
        incrementos_restantes = qtd_incrementos
        inc_req = esc.get("incrementos_pericias") if modo_manual else None
        if inc_req is not None and not _eh_proc_per(inc_req):
            if not isinstance(inc_req, list):
                raise ValueError("Campo 'incrementos_pericias' deve ser uma lista de IDs de perícias.")
            if validar_limite and len(inc_req) > qtd_incrementos:
                raise ValueError(
                    f"Você selecionou {len(inc_req)} incremento(s) de perícia, mas no {nivel_alvo}º nível "
                    f"há apenas {qtd_incrementos} incremento(s) disponível(is)."
                )
            for item in inc_req[:qtd_incrementos]:
                pid = dados.pericia_id(str(item)) or str(item).strip()
                if pid not in dados.pericias or pid == "saber":
                    raise ValueError(f"Perícia inválida em 'incrementos_pericias': '{item}'.")
                grau_atual = treinadas.get(pid, "destreinado")
                if grau_atual == "especialista":
                    raise ValueError(
                        f"A perícia '{dados.pericias[pid]['nome']}' já é Especialista e não pode subir para "
                        f"Mestre antes do 7º nível."
                    )
                novo_grau = "especialista" if grau_atual == "treinado" else "treinado"
                treinadas[pid] = novo_grau
                origens[pid] = (
                    f"{origens[pid]} + Incremento ({novo_grau.title()})"
                    if pid in origens
                    else f"Incremento de Perícia ({novo_grau.title()})"
                )
                incrementos_aplicados.append(pid)
                incrementos_restantes -= 1

        # Preenchimento procedural dos incrementos restantes: prioriza subir prioridades treinadas -> especialista
        while incrementos_restantes > 0:
            candidatos_esp = [p for p in prioridades if treinadas.get(p) == "treinado"]
            if not candidatos_esp:
                candidatos_esp = [p for p, g in treinadas.items() if g == "treinado" and p != "saber"]
            if candidatos_esp:
                pid_inc = candidatos_esp[0]
                treinadas[pid_inc] = "especialista"
                origens[pid_inc] = f"{origens[pid_inc]} + Incremento (Especialista)"
            else:
                candidatos_tr = [p for p in prioridades if p not in treinadas] or [
                    p for p in dados.pericias if p not in treinadas and p != "saber"
                ]
                if not candidatos_tr:
                    break
                pid_inc = candidatos_tr[0]
                treinadas[pid_inc] = "treinado"
                origens[pid_inc] = "Incremento de Perícia (Treinado)"
            incrementos_aplicados.append(pid_inc)
            incrementos_restantes -= 1

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
        "escolhas_pericias": {
            "modo": "personalizado" if modo_manual else "procedural",
            "vagas_livres_total": vagas_livres_total,
            "sobreposicoes": sobreposicoes,
            "manuais_aplicadas": manuais_aplicadas,
            "pericia_biografia_id": pericia_bio,
            "incrementos_disponiveis": qtd_incrementos,
            "incrementos_aplicados": incrementos_aplicados,
        },
    }


def listar_catalogo_idiomas(dados: BaseDados) -> dict[str, Any]:
    """Retorna o catálogo de idiomas comuns e incomuns do Livro Básico."""
    idiomas_blk = dados.json("ancestralidades_biografias.json").get("idiomas", {})
    comuns = [
        {
            "nome": item["idioma"],
            "regioes_falantes": item.get("regioes_falantes", ""),
            "categoria": "comum",
        }
        for item in idiomas_blk.get("tabela_2_1_idiomas_comuns", [])
    ]
    incomuns = [
        {
            "nome": item["idioma"],
            "falantes": item.get("falantes", ""),
            "categoria": "incomum",
        }
        for item in idiomas_blk.get("tabela_2_2_idiomas_incomuns", [])
    ]
    return {
        "comuns": comuns,
        "incomuns": incomuns,
        "nomes_comuns": [c["nome"] for c in comuns],
        "nomes_incomuns": [i["nome"] for i in incomuns],
    }


def calcular_idiomas(
    dados: BaseDados,
    ancestralidade: dict[str, Any],
    heranca: dict[str, Any],
    classe: dict[str, Any],
    mod_int: int,
    rng: random.Random | None = None,
    escolhas_idiomas: list[str] | str | None = None,
    retornar_detalhes: bool = False,
) -> list[str] | dict[str, Any]:
    """Calcula os idiomas iniciais e extras conforme ancestralidade, classe, herança, mod INT e escolhas manuais."""
    iniciais = list(ancestralidade.get("idiomas_iniciais", ["Comum"]))
    if classe["id"] == "druida" and "Druídico" not in iniciais:
        iniciais.append("Druídico")
    idiomas = list(iniciais)

    regra_idiomas = normalizar(ancestralidade.get("regra_idiomas_adicionais", ""))
    if ancestralidade["id"] == "humano" or "1 + modificador" in regra_idiomas:
        base_extras = max(1, 1 + mod_int)
    else:
        base_extras = max(0, mod_int)
    qtd_extras = base_extras + int(heranca.get("idiomas_adicionais", 0) or 0)

    catalogo = listar_catalogo_idiomas(dados)
    nomes_comuns = catalogo["nomes_comuns"]
    pool_anc_raw = [
        i
        for i in ancestralidade.get("idiomas_adicionais_opcoes", [])
        if "qualquer" not in normalizar(i) and len(i) <= 25
    ]

    mapa_validos: dict[str, str] = {}
    for nome in [*pool_anc_raw, *nomes_comuns]:
        mapa_validos.setdefault(normalizar(nome), nome)

    if escolhas_idiomas is None or (
        isinstance(escolhas_idiomas, str)
        and normalizar(escolhas_idiomas) in ("", "procedural", "aleatorio", "aleatoria", "random")
    ):
        lista_solicitada: list[str] = []
    elif isinstance(escolhas_idiomas, (list, tuple)):
        lista_solicitada = [
            str(item).strip()
            for item in escolhas_idiomas
            if str(item).strip() and normalizar(str(item)) != "procedural"
        ]
    else:
        raise ValueError("Formato inválido para 'escolhas_idiomas' (esperado lista de idiomas ou 'procedural').")

    if len(lista_solicitada) > max(0, qtd_extras):
        raise ValueError(
            f"Quantidade de idiomas extras selecionados ({len(lista_solicitada)}) excede o limite permitido ({max(0, qtd_extras)})."
        )

    iniciais_norm = {normalizar(i) for i in iniciais}
    manuais_resolvidos: list[str] = []
    vistos_norm: set[str] = set()
    for item in lista_solicitada:
        chave = normalizar(item)
        if chave in iniciais_norm:
            raise ValueError(f"O idioma '{item}' já faz parte dos idiomas iniciais automáticos do personagem.")
        if chave not in mapa_validos:
            raise ValueError(
                f"Idioma extra inválido ou sem acesso pela ancestralidade ({ancestralidade['nome']}): '{item}'."
            )
        canonico = mapa_validos[chave]
        if chave in vistos_norm:
            raise ValueError(f"Idioma extra duplicado na seleção: '{canonico}'.")
        vistos_norm.add(chave)
        manuais_resolvidos.append(canonico)
        idiomas.append(canonico)

    restantes = max(0, qtd_extras - len(manuais_resolvidos))
    adicionados_procedurais: list[str] = []
    if restantes > 0:
        pool_anc = [i for i in pool_anc_raw if i not in idiomas]
        tabela_comuns = [i for i in nomes_comuns if i not in idiomas]

        if rng is not None:
            rng.shuffle(pool_anc)
            rng.shuffle(tabela_comuns)

        for candidato in pool_anc + tabela_comuns:
            if restantes <= 0:
                break
            if candidato not in idiomas:
                idiomas.append(candidato)
                adicionados_procedurais.append(candidato)
                restantes -= 1

    if not retornar_detalhes:
        return idiomas

    modo = (
        "manual"
        if manuais_resolvidos and not adicionados_procedurais
        else ("hibrido" if manuais_resolvidos else "procedural")
    )
    return {
        "idiomas": idiomas,
        "idiomas_iniciais": iniciais,
        "qtd_extras": max(0, qtd_extras),
        "escolhas_manuais": manuais_resolvidos,
        "escolhas_procedurais": adicionados_procedurais,
        "modo": modo,
    }
