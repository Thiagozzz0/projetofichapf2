"""Regras de geração de atributos, modificadores C&C, Primários e Sistema SIEGE."""

from __future__ import annotations

import random
from typing import Any

from motor_cc.dados import carregar_introducao, listar_classes, mapa_classes, mapa_racas

ORDEM_ATRIBUTOS: tuple[str, ...] = (
    "forca",
    "destreza",
    "constituicao",
    "inteligencia",
    "sabedoria",
    "carisma",
)

SIGLAS_ATRIBUTOS: dict[str, str] = {
    "forca": "FOR",
    "destreza": "DES",
    "constituicao": "CON",
    "inteligencia": "INT",
    "sabedoria": "SAB",
    "carisma": "CAR",
}

NOMES_ATRIBUTOS: dict[str, str] = {
    "forca": "Força",
    "destreza": "Destreza",
    "constituicao": "Constituição",
    "inteligencia": "Inteligência",
    "sabedoria": "Sabedoria",
    "carisma": "Carisma",
}

JOGADAS_PROTECAO_POR_ATRIBUTO: dict[str, list[str]] = {
    "forca": ["Paralisia", "Constrição"],
    "destreza": ["Arma de Sopro", "Armadilhas"],
    "constituicao": ["Doenças", "Dreno de Energia", "Veneno"],
    "inteligencia": ["Magia Arcana", "Ilusões"],
    "sabedoria": ["Confusão", "Ataques Visuais", "Magia Divina", "Petrificação", "Polimorfia"],
    "carisma": ["Ataques Mortais", "Encantamento", "Medo"],
}

PONTOS_DISTRIBUIDOS_PADRAO = 62
VALOR_MINIMO_BASE = 3
VALOR_MAXIMO_BASE = 18

METODOS_GERACAO: dict[str, dict[str, Any]] = {
    "old_school_3d6_ordem": {
        "id": "old_school_3d6_ordem",
        "nome": "Old School (3d6 em ordem)",
        "rotulo_ficha": "Old School: 3d6 em ordem",
        "descricao": "Rola 3d6 na ordem fixa FOR → DES → CON → INT → SAB → CAR (estilo AD&D); escolha raça e classe a partir dos valores sorteados.",
        "alocacao_livre": False,
    },
    "classico_3d6_livre": {
        "id": "classico_3d6_livre",
        "nome": "Clássico (3d6 livre)",
        "rotulo_ficha": "Clássico: 3d6",
        "descricao": "Padrão oficial de Castles & Crusades: rola 3d6 seis vezes e aloca cada resultado no atributo desejado.",
        "alocacao_livre": True,
    },
    "heroico_4d6": {
        "id": "heroico_4d6",
        "nome": "Heróico (4d6 descarta menor)",
        "rotulo_ficha": "Heróico: 4d6",
        "descricao": "Rola 4d6 descartando o menor dado seis vezes e aloca os resultados livremente entre os atributos.",
        "alocacao_livre": True,
    },
    "distribuido_62": {
        "id": "distribuido_62",
        "nome": f"Distribuído ({PONTOS_DISTRIBUIDOS_PADRAO} pontos)",
        "rotulo_ficha": f"Distribuído: {PONTOS_DISTRIBUIDOS_PADRAO} pontos",
        "descricao": f"Distribui livremente {PONTOS_DISTRIBUIDOS_PADRAO} pontos entre os 6 atributos (entre 3 e 18 cada, antes dos ajustes raciais).",
        "alocacao_livre": True,
        "total_pontos": PONTOS_DISTRIBUIDOS_PADRAO,
    },
}


def calcular_modificador(valor: int) -> int:
    """Retorna o modificador oficial de Castles & Crusades (tabela de introducao.json)."""
    tabela = carregar_introducao()["atributos"]["tabela_modificadores"]
    if valor <= 1:
        return -4
    for faixa in tabela:
        if faixa["min"] <= valor <= faixa["max"]:
            return int(faixa["modificador"])
    # Acima de 19 (via magia/itens): escala continua +1 a cada 2 pontos (20-21 -> +4, etc.)
    return 3 + ((valor - 18) // 2)


def sugerir_classes_para_atributos(valores: dict[str, int]) -> list[dict[str, Any]]:
    """Ordena as 13 classes por afinidade com os valores sorteados (útil no modo Old School)."""
    sugestoes: list[dict[str, Any]] = []
    for cls in listar_classes():
        attr_p = cls["atributo_principal"]
        val = int(valores.get(attr_p, 10))
        mod = calcular_modificador(val)
        sugestoes.append(
            {
                "classe_id": cls["id"],
                "classe_nome": cls["nome"],
                "atributo_principal": attr_p,
                "sigla": SIGLAS_ATRIBUTOS[attr_p],
                "valor": val,
                "modificador": mod,
            }
        )
    sugestoes.sort(key=lambda s: (-s["valor"], s["classe_nome"]))
    return sugestoes


def rolar_atributos(metodo: str = "classico_3d6_livre", seed: int | None = None) -> dict[str, Any]:
    """Executa uma rolagem de atributos conforme o método escolhido."""
    if metodo not in METODOS_GERACAO:
        raise ValueError(f"Método de geração inválido: {metodo!r}. Use um de {list(METODOS_GERACAO)}")

    rng = random.Random(seed)
    meta = METODOS_GERACAO[metodo]

    if metodo == "distribuido_62":
        # Distribuição inicial equilibrada somando exatamente 62 (11, 11, 10, 10, 10, 10)
        iniciais = {
            "forca": 11,
            "destreza": 11,
            "constituicao": 10,
            "inteligencia": 10,
            "sabedoria": 10,
            "carisma": 10,
        }
        return {
            "metodo": metodo,
            "rotulo_ficha": meta["rotulo_ficha"],
            "alocacao_livre": True,
            "total_pontos": PONTOS_DISTRIBUIDOS_PADRAO,
            "valores": iniciais,
            "rolagens": [],
            "sugestoes_classes": sugerir_classes_para_atributos(iniciais),
        }

    rolagens: list[dict[str, Any]] = []
    totais: list[int] = []

    for idx in range(6):
        if metodo == "heroico_4d6":
            dados = [rng.randint(1, 6) for _ in range(4)]
            ordenados = sorted(dados, reverse=True)
            total = sum(ordenados[:3])
            descartado = ordenados[3]
            rolagens.append({"indice": idx + 1, "dados": dados, "descartado": descartado, "total": total})
        else:
            dados = [rng.randint(1, 6) for _ in range(3)]
            total = sum(dados)
            rolagens.append({"indice": idx + 1, "dados": dados, "descartado": None, "total": total})
        totais.append(total)

    valores = {attr: totais[i] for i, attr in enumerate(ORDEM_ATRIBUTOS)}

    return {
        "metodo": metodo,
        "rotulo_ficha": meta["rotulo_ficha"],
        "alocacao_livre": meta["alocacao_livre"],
        "valores_lista": totais,
        "valores": valores,
        "rolagens": rolagens,
        "sugestoes_classes": sugerir_classes_para_atributos(valores),
    }


def resolver_atributos_personagem(
    valores_base: dict[str, int],
    raca_id: str,
    classe_id: str,
    primarios_escolhidos: list[str] | None = None,
    metodo_geracao: str = "classico_3d6_livre",
    linhagem_meio_elfo: str | None = None,
    atributo_secundario_meio_elfo: str | None = None,
) -> dict[str, Any]:
    """Aplica modificadores raciais, calcula modificadores C&C e resolve Primários/SIEGE."""
    if metodo_geracao not in METODOS_GERACAO:
        raise ValueError(f"Método de geração inválido: {metodo_geracao!r}")

    racas = mapa_racas()
    classes = mapa_classes()
    if raca_id not in racas:
        raise ValueError(f"Raça desconhecida: {raca_id!r}")
    if classe_id not in classes:
        raise ValueError(f"Classe desconhecida: {classe_id!r}")

    raca = racas[raca_id]
    classe = classes[classe_id]

    # Validar os 6 valores base
    base_limpo: dict[str, int] = {}
    for attr in ORDEM_ATRIBUTOS:
        if attr not in valores_base:
            raise ValueError(f"Atributo obrigatório ausente: {attr!r}")
        v = int(valores_base[attr])
        if v < VALOR_MINIMO_BASE or v > VALOR_MAXIMO_BASE:
            raise ValueError(
                f"Atributo {NOMES_ATRIBUTOS[attr]} ({v}) fora da faixa permitida ({VALOR_MINIMO_BASE}–{VALOR_MAXIMO_BASE})."
            )
        base_limpo[attr] = v

    if metodo_geracao == "distribuido_62":
        soma = sum(base_limpo.values())
        if soma != PONTOS_DISTRIBUIDOS_PADRAO:
            raise ValueError(
                f"No método Distribuído, a soma dos 6 atributos base deve ser exatamente "
                f"{PONTOS_DISTRIBUIDOS_PADRAO} pontos (atual: {soma})."
            )

    # Modificadores raciais (incluindo linhagem do Meio-Elfo)
    mods_raciais: dict[str, int] = dict(raca.get("modificadores_atributos", {}))
    linhagem_info: dict[str, Any] | None = None
    if raca_id == "meio_elfo":
        linhagens = raca.get("linhagens", {})
        lin_id = linhagem_meio_elfo or "elfica"
        if lin_id not in linhagens:
            raise ValueError(f"Linhagem de Meio-Elfo inválida: {lin_id!r}. Use 'humana' ou 'elfica'.")
        linhagem_info = linhagens[lin_id]
        for k, v in linhagem_info.get("modificadores_atributos", {}).items():
            mods_raciais[k] = mods_raciais.get(k, 0) + int(v)

    # Atributos Primários: 1 obrigatório da classe + livres conforme raça (2 humano, 1 não-humano)
    primario_classe = classe["atributo_principal"]
    qtd_livres = int(raca.get("primarios_escolha_jogador", 1))
    primarios: list[str] = [primario_classe]

    for p in (primarios_escolhidos or []):
        if p not in ORDEM_ATRIBUTOS:
            raise ValueError(f"Atributo primário inválido: {p!r}")
        if p not in primarios and len(primarios) < 1 + qtd_livres:
            primarios.append(p)

    # Se o usuário não escolheu todos os primários livres, completa automaticamente pelos maiores valores finais
    finais_temp = {a: max(1, base_limpo[a] + int(mods_raciais.get(a, 0))) for a in ORDEM_ATRIBUTOS}
    if len(primarios) < 1 + qtd_livres:
        candidatos = sorted(
            [a for a in ORDEM_ATRIBUTOS if a not in primarios],
            key=lambda a: (-finais_temp[a], ORDEM_ATRIBUTOS.index(a)),
        )
        for cand in candidatos:
            if len(primarios) >= 1 + qtd_livres:
                break
            primarios.append(cand)

    # Bônus de atributo secundário do Meio-Elfo (Linhagem Humana: +2 em testes de 1 atributo secundário)
    bonus_secundario_meio_elfo: str | None = None
    if raca_id == "meio_elfo" and linhagem_info and linhagem_info["id"] == "humana":
        secundarios = [a for a in ORDEM_ATRIBUTOS if a not in primarios]
        if atributo_secundario_meio_elfo in secundarios:
            bonus_secundario_meio_elfo = atributo_secundario_meio_elfo
        elif secundarios:
            bonus_secundario_meio_elfo = secundarios[0]

    # Monta dicionário detalhado de cada atributo
    detalhes: dict[str, dict[str, Any]] = {}
    for attr in ORDEM_ATRIBUTOS:
        base_v = base_limpo[attr]
        mod_r = int(mods_raciais.get(attr, 0))
        final_v = max(1, base_v + mod_r)
        mod_v = calcular_modificador(final_v)
        is_primario = attr in primarios
        bonus_extra_teste = 2 if attr == bonus_secundario_meio_elfo else 0
        detalhes[attr] = {
            "id": attr,
            "sigla": SIGLAS_ATRIBUTOS[attr],
            "nome": NOMES_ATRIBUTOS[attr],
            "base": base_v,
            "ajuste_racial": mod_r,
            "valor": final_v,
            "modificador": mod_v,
            "primario": is_primario,
            "origem_primario": (
                "classe" if attr == primario_classe else ("escolha_jogador" if is_primario else None)
            ),
            "classe_base_siege": 12 if is_primario else 18,
            "bonus_extra_teste": bonus_extra_teste,
            "jogadas_protecao": JOGADAS_PROTECAO_POR_ATRIBUTO[attr],
        }

    return {
        "metodo_geracao": metodo_geracao,
        "rotulo_metodo": METODOS_GERACAO[metodo_geracao]["rotulo_ficha"],
        "soma_base": sum(base_limpo.values()),
        "primario_classe": primario_classe,
        "primarios": primarios,
        "secundarios": [a for a in ORDEM_ATRIBUTOS if a not in primarios],
        "total_primarios": len(primarios),
        "linhagem_meio_elfo": linhagem_info["id"] if linhagem_info else None,
        "atributo_secundario_meio_elfo": bonus_secundario_meio_elfo,
        "atributos": detalhes,
    }
