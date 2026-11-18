"""Gerador e validador de dados/pericias.json a partir de ref/Skill sfots.pdf."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "pericias.json"

SIGLAS_ATRIBUTO = {
    "Força": "For",
    "Destreza": "Des",
    "Inteligência": "Int",
    "Sabedoria": "Sab",
    "Carisma": "Car",
}


def slugify(texto: str) -> str:
    """Converte um nome em identificador snake_case ASCII."""
    normalizado = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(c for c in normalizado if not unicodedata.combining(c))
    return re.sub(r"[^a-zA-Z0-9]+", "_", sem_acentos.lower()).strip("_")


def preco_para_pc(texto: str) -> int | None:
    """Converte string de moeda PF2E ('1 po, 5 pp', '7.000 po', '—') em peças de cobre."""
    limpo = texto.strip()
    if not limpo or limpo in {"—", "-", "--"}:
        return None
    multiplicadores = {"po": 100, "pp": 10, "pc": 1, "pl": 1000}
    total = 0
    encontrou = False
    for parte in limpo.split(","):
        m = re.search(r"([\d.]+)\s*(pl|po|pp|pc)\b", parte.strip().lower())
        if m:
            valor = int(m.group(1).replace(".", ""))
            unidade = m.group(2)
            total += valor * multiplicadores[unidade]
            encontrou = True
    if not encontrou:
        raise ValueError(f"Formato de preço inesperado: {texto!r}")
    return total


def item_tabela_4_1(
    nome: str,
    custo_acoes: str | None = None,
    *,
    exploracao: bool = False,
    acao_geral: bool = False,
    recesso: bool = False,
    nota: str | None = None,
) -> dict[str, Any]:
    """Cria uma entrada normalizada de ação na Tabela 4–1."""
    entrada: dict[str, Any] = {
        "id": slugify(nome),
        "nome": nome,
        "custo_acoes": custo_acoes,
        "exploracao": exploracao,
        "acao_geral": acao_geral,
        "recesso": recesso,
    }
    if nota:
        entrada["nota"] = nota
    return entrada


def construir_acao(
    nome: str,
    *,
    proficiencia_minima: str = "destreinado",
    acao_geral: bool = False,
    custo_acoes: str | None = None,
    tracos: list[str] | None = None,
    requerimentos: str | None = None,
    cd_alvo: str | None = None,
    descricao: str = "",
    resultados: dict[str, str] | None = None,
    exemplos_tarefas: dict[str, str] | None = None,
    notas_adicionais: list[str] | None = None,
    observacao: str | None = None,
) -> dict[str, Any]:
    """Cria uma entrada normalizada de ação de perícia."""
    entrada: dict[str, Any] = {
        "id": slugify(nome),
        "nome": nome,
        "proficiencia_minima": proficiencia_minima,
        "acao_geral": acao_geral,
        "custo_acoes": custo_acoes,
        "tracos": tracos or [],
    }
    if requerimentos is not None:
        entrada["requerimentos"] = requerimentos
    if cd_alvo is not None:
        entrada["cd_alvo"] = cd_alvo
    entrada["descricao"] = descricao
    if resultados is not None:
        entrada["resultados"] = resultados
    if exemplos_tarefas is not None:
        entrada["exemplos_tarefas"] = exemplos_tarefas
    if notas_adicionais:
        entrada["notas_adicionais"] = notas_adicionais
    if observacao:
        entrada["observacao"] = observacao
    return entrada


def construir_pericia(
    nome: str,
    atributo_chave: str,
    pagina: str,
    descricao: str,
    acoes_destreinadas: list[dict[str, Any]],
    acoes_treinadas: list[dict[str, Any]],
    *,
    quadros_e_regras_especiais: dict[str, Any] | None = None,
    nota_uso_basico: str | None = None,
) -> dict[str, Any]:
    """Cria uma entrada normalizada para uma das 17 perícias do Capítulo 4."""
    entrada: dict[str, Any] = {
        "id": slugify(nome),
        "nome": nome,
        "atributo_chave": atributo_chave,
        "atributo_sigla": SIGLAS_ATRIBUTO[atributo_chave],
        "sofre_penalidade_armadura": atributo_chave in {"Força", "Destreza"},
        "pagina": pagina,
        "descricao": descricao,
    }
    if nota_uso_basico:
        entrada["nota_uso_basico"] = nota_uso_basico
    if quadros_e_regras_especiais:
        entrada["quadros_e_regras_especiais"] = quadros_e_regras_especiais
    entrada["acoes_destreinadas"] = acoes_destreinadas
    entrada["acoes_treinadas"] = acoes_treinadas
    return entrada


def construir_regras_gerais() -> dict[str, Any]:
    """Constrói todas as regras introdutórias e mecânicas gerais do Capítulo 4."""
    return {
        "conceito": (
            "Enquanto os atributos representam talento e potencial bruto, perícias representam "
            "treinamento e experiência em realizar determinadas tarefas. Cada perícia é vinculada a um "
            "atributo chave e utilizada para uma gama de ações relacionadas."
        ),
        "fontes_treinamento_nivel_1": {
            "descricao": (
                "Um personagem adquire treinamento em determinadas perícias no 1º nível: normalmente duas "
                "perícias por sua biografia, uma pequena quantidade de perícias pré-determinadas por sua "
                "classe e algumas perícias à escolha concedidas por sua classe (além de seu modificador "
                "de Inteligência, conforme o Capítulo 1)."
            ),
            "efeito": (
                "Aumenta a graduação de proficiência nessas perícias de destreinado para treinado e "
                "permite usar as ações treinadas dessas perícias."
            ),
            "regra_redundancia_treinado": (
                "Cada vez após a primeira em que você fosse receber a graduação de proficiência de "
                "treinado em uma determinada perícia (por exemplo, biografia e classe concedendo ambas "
                "Manufatura), em vez disso você aloca a proficiência de treinado em qualquer outra "
                "perícia à sua escolha."
            ),
        },
        "atributo_chave": {
            "regra": (
                "Cada perícia é ligada a um atributo chave cujo modificador é somado aos testes e CDs "
                "ao utilizar essa perícia."
            ),
            "flexibilidade_mj": (
                "Se julgar apropriado para uma determinada situação (como usar Recordar Conhecimento "
                "com uma perícia física), o MJ pode determinar que você utilize um modificador de atributo "
                "diferente para um teste de perícia ou para determinar sua CD de perícia."
            ),
        },
        "acoes_de_pericia": {
            "destreinadas": (
                "Qualquer um pode usar as ações destreinadas de uma perícia, independentemente de ser "
                "treinado ou não."
            ),
            "treinadas": (
                "Podem ser usadas somente se possuir graduação de proficiência de treinado ou melhor "
                "nessa perícia."
            ),
            "restricoes_e_graduacao_superior": (
                "Uma circunstância, condição ou efeito pode impedi-lo de realizar uma ação de perícia "
                "independentemente da proficiência. Às vezes o MJ pode exigir uma graduação de "
                "proficiência superior à listada na Tabela 4–1 para uma tarefa específica."
            ),
        },
        "aprimorando_pericias": {
            "incrementos_de_pericia": {
                "descricao": (
                    "Incrementos de perícia aprimoram sua proficiência nas perícias escolhidas nos níveis "
                    "indicados pela sua classe."
                ),
                "niveis_desbloqueio": {
                    "treinado": "Qualquer nível (1º+)",
                    "especialista": "Qualquer nível (a partir do 1º/progressão de classe; tipicamente a partir do 3º pelos incrementos padrão)",
                    "mestre": "A partir do 7º nível",
                    "lendario": "A partir do 15º nível",
                },
                "regra_redundancia_superior": (
                    "Ao contrário de quando se torna treinado em uma perícia, se duas habilidades diferentes "
                    "lhe tornariam especialista, mestre ou lendário em uma perícia, você não escolhe uma "
                    "segunda perícia para aprimorar — o benefício redundante simplesmente não tem efeito."
                ),
            },
            "talentos_de_pericia": (
                "Tipo de talento geral (sempre com o traço perícia) que frequentemente concede uma nova "
                "forma de usar uma perícia ou melhora um uso específico (apresentados no Capítulo 5)."
            ),
        },
        "testes_e_cds": {
            "formula_modificador_pericia": "modificador_atributo_chave + bonus_proficiencia + outros_bonus + penalidades",
            "formula_cd_pericia": "10 + modificador_pericia",
            "regra_ficha": (
                "Ao escrever o modificador na ficha de personagem, anote somente os números que sempre "
                "se aplicam (normalmente modificador de atributo + bônus de proficiência no 1º nível, e "
                "bônus de item contínuos em níveis superiores)."
            ),
            "graduacoes_proficiencia": {
                "destreinado": {
                    "nome": "Destreinado",
                    "codigo": "D",
                    "bonus_base": 0,
                    "soma_nivel": False,
                    "nivel_minimo_incremento": 1,
                },
                "treinado": {
                    "nome": "Treinado",
                    "codigo": "T",
                    "bonus_base": 2,
                    "soma_nivel": True,
                    "nivel_minimo_incremento": 1,
                },
                "especialista": {
                    "nome": "Especialista",
                    "codigo": "E",
                    "bonus_base": 4,
                    "soma_nivel": True,
                    "nivel_minimo_incremento": 1,
                },
                "mestre": {
                    "nome": "Mestre",
                    "codigo": "M",
                    "bonus_base": 6,
                    "soma_nivel": True,
                    "nivel_minimo_incremento": 7,
                },
                "lendario": {
                    "nome": "Lendário",
                    "codigo": "L",
                    "bonus_base": 8,
                    "soma_nivel": True,
                    "nivel_minimo_incremento": 15,
                },
            },
            "cds_simples": [
                {"dificuldade": "Destreinado", "cd": 10},
                {"dificuldade": "Treinado", "cd": 15},
                {"dificuldade": "Especialista", "cd": 20},
                {"dificuldade": "Mestre", "cd": 30},
                {"dificuldade": "Lendário", "cd": 40},
            ],
        },
        "armaduras_e_pericias": {
            "regra": (
                "Se uma criatura estiver vestindo uma armadura que impõe penalidade em perícia, essa "
                "penalidade é aplicada a seus testes e CDs de perícia baseados em Força e Destreza — "
                "exceto se a ação possuir o traço ataque."
            ),
            "atributos_afetados": ["Força", "Destreza"],
            "pericias_afetadas": ["Acrobatismo", "Atletismo", "Furtividade", "Ladroagem"],
            "excecao_traco": "ataque",
            "acoes_isentas_atletismo": ["Agarrar", "Derrubar", "Empurrar", "Forçar", "Desarmar"],
            "referencia": "Capítulo 6: Equipamentos, página 274",
        },
        "testes_secretos": {
            "regra": (
                "Se uma ação possuir o traço secreto, o MJ rola o teste para o jogador em segredo e "
                "informa o efeito sem revelar o resultado da rolagem ou o grau de sucesso (regra padrão, "
                "embora o MJ possa optar por rolagens públicas)."
            ),
        },
        "atividades_exploracao_e_recesso": {
            "exploracao": "Normalmente levam um minuto ou mais; geralmente não podem ser usadas em encontros.",
            "recesso": "Podem levar um dia ou mais; geralmente não podem ser usadas em encontros.",
        },
        "resultados_criticos_padrao": (
            "A maioria das perícias inclui seções para sucesso e falha, além de sucesso crítico e falha "
            "crítica. Se qualquer das seções de resultados críticos estiver ausente, trate esses "
            "resultados como um sucesso ou falha normal."
        ),
    }


def construir_tabelas() -> dict[str, Any]:
    """Constrói todas as tabelas do Capítulo 4 (Tabelas 4-1 a 4-4 e tabelas auxiliares)."""
    tabela_4_1 = [
        {
            "pericia": "Acrobatismo",
            "atributo_chave": "Destreza",
            "acoes_destreinadas": [
                item_tabela_4_1("Atravessar Acrobaticamente", "1 ação"),
                item_tabela_4_1("Equilibrar", "1 ação"),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Espremer", "Exploração", exploracao=True),
                item_tabela_4_1("Manobrar em Voo", "1 ação"),
            ],
        },
        {
            "pericia": "Arcanismo",
            "atributo_chave": "Inteligência",
            "acoes_destreinadas": [
                item_tabela_4_1("Recordar Conhecimento", "1 ação", acao_geral=True),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Aprender uma Magia", "Exploração", exploracao=True, acao_geral=True),
                item_tabela_4_1("Decifrar Escrita", "Exploração", exploracao=True, acao_geral=True),
                item_tabela_4_1("Emprestar uma Magia Arcana", "Exploração", exploracao=True),
                item_tabela_4_1("Identificar Magia", "Exploração", exploracao=True, acao_geral=True),
            ],
        },
        {
            "pericia": "Atletismo",
            "atributo_chave": "Força",
            "acoes_destreinadas": [
                item_tabela_4_1("Agarrar", "1 ação"),
                item_tabela_4_1("Derrubar", "1 ação"),
                item_tabela_4_1("Empurrar", "1 ação"),
                item_tabela_4_1("Escalar", "1 ação"),
                item_tabela_4_1("Forçar", "1 ação"),
                item_tabela_4_1("Nadar", "1 ação"),
                item_tabela_4_1("Salto em Altura", "2 ações"),
                item_tabela_4_1("Salto em Distância", "2 ações"),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Desarmar", "1 ação"),
            ],
        },
        {
            "pericia": "Diplomacia",
            "atributo_chave": "Carisma",
            "acoes_destreinadas": [
                item_tabela_4_1("Impressionar", "Exploração", exploracao=True),
                item_tabela_4_1("Obter Informação", "Exploração", exploracao=True),
                item_tabela_4_1("Pedir", "1 ação"),
            ],
            "acoes_treinadas": [],
        },
        {
            "pericia": "Dissimulação",
            "atributo_chave": "Carisma",
            "acoes_destreinadas": [
                item_tabela_4_1("Criar uma Distração", "1 ação"),
                item_tabela_4_1("Mentir", "Pelo menos 1 rodada"),
                item_tabela_4_1("Personificar", "Exploração", exploracao=True),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Fintar", "1 ação"),
            ],
        },
        {
            "pericia": "Furtividade",
            "atributo_chave": "Destreza",
            "acoes_destreinadas": [
                item_tabela_4_1("Esconder", "1 ação"),
                item_tabela_4_1("Esgueirar", "1 ação"),
                item_tabela_4_1("Ocultar um Objeto", "1 ação"),
            ],
            "acoes_treinadas": [],
        },
        {
            "pericia": "Intimidação",
            "atributo_chave": "Carisma",
            "acoes_destreinadas": [
                item_tabela_4_1("Coagir", "Exploração", exploracao=True),
                item_tabela_4_1("Desmoralizar", "1 ação"),
            ],
            "acoes_treinadas": [],
        },
        {
            "pericia": "Ladroagem",
            "atributo_chave": "Destreza",
            "acoes_destreinadas": [
                item_tabela_4_1("Empalmar um Objeto", "1 ação"),
                item_tabela_4_1("Furtar", "1 ação"),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Abrir uma Fechadura", "2 ações"),
                item_tabela_4_1("Desabilitar um Dispositivo", "2 ações"),
            ],
        },
        {
            "pericia": "Manufatura",
            "atributo_chave": "Inteligência",
            "acoes_destreinadas": [
                item_tabela_4_1("Recordar Conhecimento", "1 ação", acao_geral=True),
                item_tabela_4_1("Reparar", "Exploração", exploracao=True),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Ganhar Proventos", "Recesso", acao_geral=True, recesso=True),
                item_tabela_4_1("Identificar Alquimia", "Exploração", exploracao=True),
                item_tabela_4_1("Manufaturar", "Recesso", recesso=True),
            ],
        },
        {
            "pericia": "Medicina",
            "atributo_chave": "Sabedoria",
            "acoes_destreinadas": [
                item_tabela_4_1(
                    "Administrar Primeiros Socorros",
                    "2 ações",
                    nota="Na Tabela 4–1 (p. 235) aparece impresso com ícone de 1 ação, porém o bloco oficial da ação (p. 249) define 2 ações.",
                ),
                item_tabela_4_1("Recordar Conhecimento", "1 ação", acao_geral=True),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Tratar Doença", "Recesso", recesso=True),
                item_tabela_4_1("Tratar Ferimentos", "Exploração", exploracao=True),
                item_tabela_4_1("Tratar Veneno", "1 ação"),
            ],
        },
        {
            "pericia": "Natureza",
            "atributo_chave": "Sabedoria",
            "acoes_destreinadas": [
                item_tabela_4_1("Comandar um Animal", "1 ação"),
                item_tabela_4_1("Recordar Conhecimento", "1 ação", acao_geral=True),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Aprender uma Magia", "Exploração", exploracao=True, acao_geral=True),
                item_tabela_4_1("Identificar Magia", "Exploração", exploracao=True, acao_geral=True),
            ],
        },
        {
            "pericia": "Ocultismo",
            "atributo_chave": "Inteligência",
            "acoes_destreinadas": [
                item_tabela_4_1("Recordar Conhecimento", "1 ação", acao_geral=True),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Aprender uma Magia", "Exploração", exploracao=True, acao_geral=True),
                item_tabela_4_1("Decifrar Escrita", "Exploração", exploracao=True, acao_geral=True),
                item_tabela_4_1("Identificar Magia", "Exploração", exploracao=True, acao_geral=True),
            ],
        },
        {
            "pericia": "Performance",
            "atributo_chave": "Carisma",
            "acoes_destreinadas": [
                item_tabela_4_1("Performar", "1 ação"),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Ganhar Proventos", "Recesso", acao_geral=True, recesso=True),
            ],
        },
        {
            "pericia": "Religião",
            "atributo_chave": "Sabedoria",
            "acoes_destreinadas": [
                item_tabela_4_1("Recordar Conhecimento", "1 ação", acao_geral=True),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Aprender uma Magia", "Exploração", exploracao=True, acao_geral=True),
                item_tabela_4_1("Decifrar Escrita", "Exploração", exploracao=True, acao_geral=True),
                item_tabela_4_1("Identificar Magia", "Exploração", exploracao=True, acao_geral=True),
            ],
        },
        {
            "pericia": "Saber",
            "atributo_chave": "Inteligência",
            "acoes_destreinadas": [
                item_tabela_4_1("Recordar Conhecimento", "1 ação", acao_geral=True),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Ganhar Proventos", "Recesso", acao_geral=True, recesso=True),
            ],
        },
        {
            "pericia": "Sobrevivência",
            "atributo_chave": "Sabedoria",
            "acoes_destreinadas": [
                item_tabela_4_1("Intuir Direção", "Exploração", exploracao=True),
                item_tabela_4_1("Subsistir", "Recesso", acao_geral=True, recesso=True),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Cobrir Rastros", "Exploração", exploracao=True),
                item_tabela_4_1("Rastrear", "Exploração", exploracao=True),
            ],
        },
        {
            "pericia": "Sociedade",
            "atributo_chave": "Inteligência",
            "acoes_destreinadas": [
                item_tabela_4_1("Recordar Conhecimento", "1 ação", acao_geral=True),
                item_tabela_4_1("Subsistir", "Recesso", acao_geral=True, recesso=True),
            ],
            "acoes_treinadas": [
                item_tabela_4_1("Criar Falsificação", "Recesso", recesso=True),
                item_tabela_4_1("Decifrar Escrita", "Exploração", exploracao=True, acao_geral=True),
            ],
        },
    ]

    tabela_4_2_dados = [
        ("1º ou truque mágico", 1, "2 po", 15),
        ("2º", 2, "6 po", 18),
        ("3º", 3, "16 po", 20),
        ("4º", 4, "36 po", 23),
        ("5º", 5, "70 po", 26),
        ("6º", 6, "140 po", 28),
        ("7º", 7, "300 po", 31),
        ("8º", 8, "650 po", 34),
        ("9º", 9, "1.500 po", 36),
        ("10º", 10, "7.000 po", 41),
    ]
    tabela_4_2 = [
        {
            "nivel_magia": rotulo,
            "nivel_numerico": num,
            "preco_texto": preco,
            "preco_pc": preco_para_pc(preco),
            "cd_tipica": cd,
        }
        for rotulo, num, preco, cd in tabela_4_2_dados
    ]

    tabela_4_3_bruta = [
        ("0", 0, False, "1 pc", "5 pc", "5 pc", "5 pc", "5 pc"),
        ("1", 1, False, "2 pc", "2 pp", "2 pp", "2 pp", "2 pp"),
        ("2", 2, False, "4 pc", "3 pp", "3 pp", "3 pp", "3 pp"),
        ("3", 3, False, "8 pc", "5 pp", "5 pp", "5 pp", "5 pp"),
        ("4", 4, False, "1 pp", "7 pp", "8 pp", "8 pp", "8 pp"),
        ("5", 5, False, "2 pp", "9 pp", "1 po", "1 po", "1 po"),
        ("6", 6, False, "3 pp", "1 po, 5 pp", "2 po", "2 po", "2 po"),
        ("7", 7, False, "4 pp", "2 po", "2 po, 5 pp", "2 po, 5 pp", "2 po, 5 pp"),
        ("8", 8, False, "5 pp", "2 po, 5 pp", "3 po", "3 po", "3 po"),
        ("9", 9, False, "6 pp", "3 po", "4 po", "4 po", "4 po"),
        ("10", 10, False, "7 pp", "4 po", "5 po", "6 po", "6 po"),
        ("11", 11, False, "8 pp", "5 po", "6 po", "8 po", "8 po"),
        ("12", 12, False, "9 pp", "6 po", "8 po", "10 po", "10 po"),
        ("13", 13, False, "1 po", "7 po", "10 po", "15 po", "15 po"),
        ("14", 14, False, "1 po, 5 pp", "8 po", "15 po", "20 po", "20 po"),
        ("15", 15, False, "2 po", "10 po", "20 po", "28 po", "28 po"),
        ("16", 16, False, "2 po, 5 pp", "13 po", "25 po", "36 po", "40 po"),
        ("17", 17, False, "3 po", "15 po", "30 po", "45 po", "55 po"),
        ("18", 18, False, "4 po", "20 po", "45 po", "70 po", "90 po"),
        ("19", 19, False, "6 po", "30 po", "60 po", "100 po", "130 po"),
        ("20", 20, False, "8 po", "40 po", "75 po", "150 po", "200 po"),
        ("20 (sucesso crítico)", 20, True, "—", "50 po", "90 po", "175 po", "300 po"),
    ]
    tabela_4_3 = [
        {
            "nivel_tarefa": rotulo,
            "nivel_numerico": num,
            "sucesso_critico_nivel_20": sc20,
            "falha": falha,
            "falha_pc": preco_para_pc(falha),
            "treinado": treinado,
            "treinado_pc": preco_para_pc(treinado),
            "especialista": especialista,
            "especialista_pc": preco_para_pc(especialista),
            "mestre": mestre,
            "mestre_pc": preco_para_pc(mestre),
            "lendario": lendario,
            "lendario_pc": preco_para_pc(lendario),
        }
        for rotulo, num, sc20, falha, treinado, especialista, mestre, lendario in tabela_4_3_bruta
    ]

    tradicoes_magicas_e_pericias = [
        {"tradicao_magica": "Arcana", "pericia_correspondente": "Arcanismo"},
        {"tradicao_magica": "Divina", "pericia_correspondente": "Religião"},
        {"tradicao_magica": "Ocultista", "pericia_correspondente": "Ocultismo"},
        {"tradicao_magica": "Primal", "pericia_correspondente": "Natureza"},
    ]

    tabela_4_4 = [
        {
            "velocidade": "1,5–4,5 metros",
            "escalar_sucesso": "1,5 m",
            "escalar_sucesso_critico": "1,5 m",
            "nadar_sucesso": "1,5 m",
            "nadar_sucesso_critico": "3 m",
        },
        {
            "velocidade": "6–10,5 metros",
            "escalar_sucesso": "1,5 m",
            "escalar_sucesso_critico": "3 m",
            "nadar_sucesso": "3 m",
            "nadar_sucesso_critico": "4,5 m",
        },
        {
            "velocidade": "12–16,5 metros",
            "escalar_sucesso": "3 m",
            "escalar_sucesso_critico": "4,5 m",
            "nadar_sucesso": "4,5 m",
            "nadar_sucesso_critico": "6 m",
        },
        {
            "velocidade": "18–19,5 metros",
            "escalar_sucesso": "4,5 m",
            "escalar_sucesso_critico": "6 m",
            "nadar_sucesso": "6 m",
            "nadar_sucesso_critico": "7,5 m",
        },
    ]

    tracos_de_performance = [
        {"performance": "Atuação ou comédia", "tracos_adicionais": ["auditivo", "linguístico", "visual"]},
        {"performance": "Canto ou oração", "tracos_adicionais": ["auditivo", "linguístico"]},
        {"performance": "Dança", "tracos_adicionais": ["movimento", "visual"]},
        {"performance": "Tocar um instrumento", "tracos_adicionais": ["auditivo", "manuseio"]},
    ]

    return {
        "tabela_4_1_pericias_atributos_acoes": tabela_4_1,
        "tabela_4_2_aprender_uma_magia": tabela_4_2,
        "tabela_4_3_proventos_ganhos": tabela_4_3,
        "tradicoes_magicas_e_pericias": tradicoes_magicas_e_pericias,
        "tabela_4_4_distancia_escalar_e_nadar": tabela_4_4,
        "tracos_de_performance": tracos_de_performance,
    }


def construir_acoes_gerais_pericia() -> list[dict[str, Any]]:
    """Constrói as 6 ações gerais de perícia descritas nas páginas 234 a 240."""
    return [
        {
            "id": "aprender_uma_magia",
            "nome": "Aprender uma Magia",
            "proficiencia_minima": "treinado",
            "pagina": "234-236",
            "custo_acoes": None,
            "tracos": ["concentração", "exploração"],
            "pericias_aplicaveis": ["Arcanismo", "Natureza", "Ocultismo", "Religião"],
            "requerimentos": (
                "Você possui uma característica de classe de conjuração, e a magia que pretende "
                "aprender está na lista de magias de sua tradição mágica."
            ),
            "descricao": (
                "Você pode obter acesso a uma nova magia de sua tradição com alguém que conheça essa "
                "magia ou de uma escrita mágica como um grimório ou pergaminho. Se puder conjurar magias "
                "de várias tradições, deve utilizar a perícia correspondente à tradição da magia."
            ),
            "passos": [
                "Gastar 1 hora por nível da magia conversando com uma pessoa que a conheça ou examinando uma escrita mágica em sua posse.",
                "Ter materiais com o Preço indicado na Tabela 4–2: Aprender uma Magia.",
                "Fazer um teste de perícia para a perícia correspondente à sua tradição (CD determinada pelo MJ, frequentemente próxima à CD da Tabela 4–2/4–3; magias incomuns ou raras possuem CDs maiores).",
            ],
            "efeito_por_tipo_conjurador": (
                "Se possuir um grimório, acrescenta a magia ao grimório; se preparar magias de uma lista, "
                "acrescenta à lista; se possuir um repertório de magias, pode selecioná-la quando acrescentar "
                "ou trocar magias."
            ),
            "resultados": {
                "sucesso_critico": "Você gasta metade dos materiais e aprende a magia.",
                "sucesso": "Você gasta os materiais e aprende a magia.",
                "falha": "Você falha em aprender a magia, mas pode tentar novamente após subir um nível. Os materiais não são gastos.",
                "falha_critica": "Como falha, mas você gasta metade dos materiais.",
            },
        },
        {
            "id": "decifrar_escrita",
            "nome": "Decifrar Escrita",
            "proficiencia_minima": "treinado",
            "pagina": "236-237",
            "custo_acoes": None,
            "tracos": ["concentração", "exploração", "secreto"],
            "pericias_aplicaveis": ["Arcanismo", "Ocultismo", "Religião", "Sociedade"],
            "uso_por_pericia": {
                "Arcanismo": "Escritas sobre magia ou ciência.",
                "Ocultismo": "Textos esotéricos sobre mistérios e filosofia.",
                "Religião": "Escrituras.",
                "Sociedade": "Mensagens codificadas, documentos arcaicos ou texto em idioma desconhecido (a critério do MJ).",
            },
            "descricao": (
                "Você tenta decifrar uma escrita ou literatura complicada sobre um tópico obscuro. Isto "
                "normalmente leva 1 minuto por página de texto, mas pode levar mais tempo (normalmente uma "
                "hora por página para decifrar cifras ou similares). O texto deve estar em um idioma que "
                "você é capaz de ler, embora o MJ possa permitir decifrar idioma desconhecido com Sociedade."
            ),
            "resultados": {
                "sucesso_critico": "Você compreende o verdadeiro significado do texto.",
                "sucesso": "Você compreende o verdadeiro significado do texto. Se ele for um documento codificado, você descobre o significado geral, mas não consegue uma tradução palavra por palavra.",
                "falha": "Você é incapaz de compreender o texto e sofre –2 de penalidade em testes posteriores para decifrá-lo.",
                "falha_critica": "Você acredita que compreendeu o texto nessa página, mas na verdade interpretou sua mensagem erroneamente.",
            },
            "exemplos_tarefas": {
                "treinado": "dissertação básica de filosofia",
                "especialista": "código complexo, como cifras",
                "mestre": "código de um mestre espião ou anotações de pesquisa avançadas",
                "lendario": "texto planar esotérico escrito em metáforas por um celestial antigo",
            },
        },
        {
            "id": "ganhar_proventos",
            "nome": "Ganhar Proventos",
            "proficiencia_minima": "treinado",
            "pagina": "237-238",
            "custo_acoes": None,
            "tracos": ["recesso"],
            "pericias_principais": ["Manufatura", "Performance", "Saber"],
            "pericias_alternativas_mj": (
                "Em alguns casos, o MJ pode permitir utilizar outra perícia através de trabalho "
                "especializado (como Religião para estudar textos antigos, Acrobatismo em um circo ou "
                "Ladroagem para bater carteiras), normalmente com CD significativamente maior."
            ),
            "descricao": (
                "Você utiliza uma de suas perícias para fazer dinheiro durante o recesso. O MJ designa "
                "um nível de tarefa representando o trabalho mais lucrativo disponível e determina "
                "secretamente a CD. Após o primeiro dia de trabalho, role para determinar os proventos "
                "diários conforme a Tabela 4–3: Proventos Ganhos, mantendo o mesmo valor nos dias "
                "subsequentes da mesma tarefa."
            ),
            "regras_adicionais": {
                "preparacao_extra": (
                    "Gastar alguns dias de recesso se preparando para uma tarefa ajusta a CD do teste "
                    "(determinado pelo MJ); mais útil para tarefas de nível superior ao seu."
                ),
                "encerrando_ou_interrompendo_tarefas": (
                    "Ao parar no meio ou completar uma tarefa, normalmente leva 1 dia ou mais de recesso "
                    "para encontrar novo emprego. Uma tarefa pode ser pausada para aventurar-se; rolagens "
                    "boas podem ser mantidas, rolagens ruins não podem ser melhoradas apenas pausando, e "
                    "se suas estatísticas mudarem (como subir de nível), você pode fazer um novo teste."
                ),
                "manufaturar_mercadorias_para_mercado": (
                    "Usando Manufatura, cria itens comuns de nível 1 ou 2 abaixo do nível do assentamento, "
                    "ou comissões especiais usando a atividade Manufaturar."
                ),
                "encenar_uma_performance": (
                    "Usando Performance, o nível da tarefa é determinado pelas audiências disponíveis "
                    "(plebeus na rua nível 0, artesãos 2º–3º nível, mercadores/nobres/realeza superiores)."
                ),
                "exercer_profissao": (
                    "Usando Saber, aplica noções práticas de uma especialidade (administração, leis, "
                    "navegação etc.); especialidades obscuras podem ter CD maior ou apenas tarefas de "
                    "nível inferior, e ferramentas especializadas podem ser necessárias."
                ),
            },
            "resultados": {
                "sucesso_critico": "Você faz um trabalho excepcional. Ganhe a quantidade de dinheiro listada para o nível da tarefa + 1 e sua graduação de proficiência.",
                "sucesso": "Você faz um trabalho competente. Ganhe a quantidade de dinheiro listada para o nível da tarefa e sua graduação de proficiência.",
                "falha": "Você faz um trabalho mal feito e recebe o mínimo pelo seu tempo. Ganhe a quantidade de dinheiro listada na coluna de falha para o nível da tarefa. O MJ provavelmente reduzirá quanto tempo você pode continuar fazendo a tarefa.",
                "falha_critica": "Você não ganha nada pelo seu trabalho e é demitido imediatamente. Você não pode continuar a tarefa. Sua reputação é prejudicada, o que provavelmente dificultará que você encontre outros trabalhos recompensadores nessa comunidade.",
            },
            "exemplos_tarefas": {
                "treinado": "copeiro, fazer pesquisa legal",
                "especialista": "cuidar de uma adega, defender casos menores na corte",
                "mestre": "administrar uma grande cervejaria, defender casos importantes na corte",
                "lendario": "administrar uma franquia internacional de bebida, defender um caso nas cortes do Inferno",
            },
            "exemplos_ilustrativos": [
                "Harsk Faz Chá (nível 3, especialista em Saber de Chá)",
                "Lem Se Apresenta (nível 16, lendário em Performance)",
            ],
        },
        {
            "id": "identificar_magia",
            "nome": "Identificar Magia",
            "proficiencia_minima": "treinado",
            "pagina": "238",
            "custo_acoes": None,
            "tracos": ["concentração", "exploração", "secreto"],
            "pericias_aplicaveis": ["Arcanismo", "Natureza", "Ocultismo", "Religião"],
            "descricao": (
                "Após descobrir que um efeito contínuo, item ou local é mágico, você pode gastar 10 minutos "
                "para tentar identificar as particularidades de sua magia utilizando a perícia da tradição "
                "correspondente (ou qualquer uma das quatro se o alvo possuir apenas o traço mágico sem "
                "tradição específica; tradições diferentes podem ser tentadas com CD maior a critério do MJ). "
                "Se interrompida, deve começar novamente. Elevar uma magia não aumenta a CD para identificá-la."
            ),
            "resultados": {
                "sucesso_critico": "Você descobre todas as características da magia, incluindo seu nome (para um efeito), o que ela faz, quaisquer meios de ativá-la (para um item ou local) e se ela é amaldiçoada.",
                "sucesso": "Para um item ou local, você tem uma sensação do que ele faz e descobre quaisquer meios de ativá-lo. Para um efeito contínuo (como uma magia com duração), você descobre o nome do efeito e o que ele faz. Você não pode tentar novamente na esperança de obter um sucesso crítico.",
                "falha": "Você falha em identificar a magia e não pode tentar novamente por 1 dia.",
                "falha_critica": "Você identifica a magia incorretamente como alguma outra coisa à escolha do MJ.",
            },
        },
        {
            "id": "recordar_conhecimento",
            "nome": "Recordar Conhecimento",
            "proficiencia_minima": "destreinado",
            "pagina": "239-240",
            "custo_acoes": "1 ação",
            "tracos": ["concentração", "secreto"],
            "pericias_aplicaveis": [
                "Arcanismo",
                "Manufatura",
                "Medicina",
                "Natureza",
                "Ocultismo",
                "Religião",
                "Saber",
                "Sociedade",
            ],
            "topicos_por_pericia": {
                "Arcanismo": "Teorias arcanas, tradições mágicas, criaturas de significância arcana e planos arcanos.",
                "Manufatura": "Reações e criaturas alquímicas, valor de itens, engenharia, materiais inusitados e constructos.",
                "Medicina": "Doenças, venenos, ferimentos e ciência forense.",
                "Natureza": "O ambiente, flora, geografia, clima, criaturas de origem natural e planos naturais.",
                "Ocultismo": "Mistérios antigos, filosofia obscura, criaturas de significância ocultista e planos esotéricos.",
                "Religião": "Agentes divinos, planos divinos, teologia, mitos obscuros e criaturas de significância religiosa.",
                "Saber": "O assunto da subcategoria da perícia Saber.",
                "Sociedade": "História local, personalidades principais, instituições legais, estrutura social e cultura humanoide.",
            },
            "descricao": (
                "Você faz um teste de perícia para tentar lembrar algum conhecimento específico sobre um "
                "tópico relacionado a ela e aplicá-lo à situação presente. Em alguns casos pode ser "
                "necessário investigar primeiro (como conduzir uma autópsia com Medicina) ou utilizar "
                "outra perícia a critério do MJ (usando um atributo mental, normalmente Inteligência, "
                "caso seja uma perícia física)."
            ),
            "resultados": {
                "sucesso_critico": "Você recorda o conhecimento precisamente e obtém informações ou contexto adicional.",
                "sucesso": "Você recorda o conhecimento precisamente ou recebe uma pista útil sobre sua situação atual.",
                "falha_critica": "Você recorda informações incorretas ou recebe uma pista errônea ou enganosa.",
            },
            "exemplos_tarefas": {
                "destreinado": "nome de um governante, nobre principal ou divindade maior",
                "treinado": "linha de sucessão de uma família nobre maior, doutrinas principais de uma divindade maior",
                "especialista": "genealogia de um nobre menor, ensinamentos de um sacerdote antigo",
                "mestre": "hierarquia de uma nobre corte de gênios, templos extraplanares maiores de uma divindade",
                "lendario": "existência de um herdeiro nobre desaparecido há tempos, doutrinas secretas de uma religião",
            },
        },
        {
            "id": "subsistir",
            "nome": "Subsistir",
            "proficiencia_minima": "destreinado",
            "pagina": "240",
            "custo_acoes": None,
            "tracos": ["recesso"],
            "pericias_aplicaveis": ["Sobrevivência", "Sociedade"],
            "uso_por_pericia": {
                "Sociedade": "Em um assentamento (encontrando abrigo e surrupiando ou pedindo comida).",
                "Sobrevivência": "Nos ermos (forrageando comida e montando abrigo).",
            },
            "descricao": (
                "Você tenta providenciar comida e abrigo para si, e possivelmente também para outros, "
                "com um padrão de vida descrito na página 294. Ao contrário da maioria das atividades de "
                "recesso, você pode Subsistir após 8 horas ou menos de exploração, mas sofre –5 de "
                "penalidade se o fizer."
            ),
            "resultados": {
                "sucesso_critico": "Você fornece subsistência para você e uma criatura adicional, ou melhora sua própria comida e abrigo, concedendo a si um padrão de vida confortável.",
                "sucesso": "Você encontra alimentos e um abrigo com proteção básica contra as condições climáticas, conseguindo um padrão de vida de subsistência para si mesmo.",
                "falha": "Você se expõe às condições climáticas e não consegue alimentos suficientes, ficando fatigado até obter alimentos e abrigo melhores.",
                "falha_critica": "Você atrai problemas, come algo que não deveria ou de alguma outra forma piora sua situação. Você sofre –2 de penalidade em testes de Subsistir por 1 semana. Você não encontra qualquer alimento; se não possuir qualquer comida armazenada, você corre risco de passar fome ou morrer de sede se continuar falhando.",
            },
            "exemplos_tarefas": {
                "destreinado": "floresta exuberante com clima calmo ou cidade grande com plenitude de recursos",
                "treinado": "aldeia ou encosta típica",
                "especialista": "montanhas típicas ou vilarejo insular",
                "mestre": "deserto típico ou cidade sob cerco",
                "lendario": "deserto estéril ou cidade de mortos-vivos",
            },
        },
    ]


def construir_pericias() -> list[dict[str, Any]]:
    """Constrói todas as 17 perícias do Capítulo 4 com suas ações destreinadas e treinadas."""
    return [
        construir_pericia(
            "Acrobatismo",
            "Destreza",
            "240-241",
            "Acrobatismo mede sua habilidade de realizar tarefas que exigem coordenação e graça.",
            nota_uso_basico="Quando usar a ação básica Escapar (página 470), você pode utilizar seu modificador de Acrobatismo em vez de seu modificador de ataque desarmado.",
            acoes_destreinadas=[
                construir_acao(
                    "Atravessar Acrobaticamente",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["movimento"],
                    cd_alvo="CD de Reflexos do inimigo",
                    descricao=(
                        "Você Anda até sua Velocidade. Durante este movimento, pode tentar mover-se "
                        "através do espaço de um inimigo fazendo um teste de Acrobatismo contra a CD de "
                        "Reflexos dele assim que tentar entrar no espaço dele. Pode usar Escalar, Nadar, "
                        "Voar ou outra ação em vez de Andar no ambiente apropriado."
                    ),
                    resultados={
                        "sucesso": "Você se move através do espaço do inimigo, tratando os quadrados no espaço dele como terreno difícil (cada 1,5 metros custam 3 metros de movimento). Se não possuir Velocidade suficiente para mover-se por todo o espaço dele, você obtém o mesmo efeito que em uma falha.",
                        "falha": "Seu movimento é encerrado e você aciona reações como se tivesse se movido para fora do quadrado em que iniciou seu movimento.",
                    },
                ),
                construir_acao(
                    "Equilibrar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["movimento"],
                    requerimentos="Você está em um quadrado que contém uma superfície estreita, solo irregular ou outra característica similar.",
                    cd_alvo="CD de Equilibrar do local",
                    descricao=(
                        "Você se move por uma superfície estreita ou solo irregular, fazendo um teste de "
                        "Acrobatismo contra a CD de Equilibrar do local. Você fica desprevenido enquanto "
                        "estiver em uma superfície estreita ou solo irregular."
                    ),
                    resultados={
                        "sucesso_critico": "Você se move até sua Velocidade.",
                        "sucesso": "Você se move até sua Velocidade, tratando o local como terreno difícil (cada 1,5 metros custam 3 metros de movimento).",
                        "falha": "Você deve permanecer parado para manter seu equilíbrio (desperdiçando a ação) ou cai. Se cair, seu turno se encerra.",
                        "falha_critica": "Você cai e seu turno se encerra.",
                    },
                    exemplos_tarefas={
                        "destreinado": "raízes emaranhadas, calçada irregular",
                        "treinado": "viga de madeira",
                        "especialista": "cascalho solto e fundo",
                        "mestre": "corda bamba, camada de gelo macia",
                        "lendario": "fio de navalha, pedaços de chão caindo pelo ar",
                    },
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Espremer",
                    proficiencia_minima="treinado",
                    custo_acoes=None,
                    tracos=["exploração", "movimento"],
                    descricao=(
                        "Você se contorce para espremer-se através de um espaço tão pequeno em que mal pode "
                        "passar. Usada para espaços excepcionalmente pequenos; muitos espaços apertados são "
                        "apenas terreno difícil (página 475) por onde se move mais rápido sem teste."
                    ),
                    resultados={
                        "sucesso_critico": "Você se espreme através do espaço apertado em 1 minuto para cada 3 metros atravessados.",
                        "sucesso": "Você se espreme por 1 minuto para cada 1,5 metros.",
                        "falha_critica": "Você fica preso no espaço apertado. Enquanto estiver preso, você pode gastar 1 minuto fazendo outro teste de Acrobatismo contra a mesma CD. Qualquer resultado nesse teste diferente de uma falha crítica faz com que deixe de estar preso.",
                    },
                    exemplos_tarefas={
                        "treinado": "espaço mal cabe seus ombros",
                        "mestre": "espaço mal cabe sua cabeça",
                    },
                ),
                construir_acao(
                    "Manobrar em Voo",
                    proficiencia_minima="treinado",
                    custo_acoes="1 ação",
                    tracos=["movimento"],
                    requerimentos="Você possui Velocidade de voo.",
                    descricao=(
                        "Você tenta uma manobra difícil enquanto voa. Faça um teste de Acrobatismo. O MJ "
                        "determina quais manobras são possíveis, mas raramente permitem mover-se mais que "
                        "sua Velocidade de voo."
                    ),
                    resultados={
                        "sucesso": "Você obtém sucesso na manobra.",
                        "falha": "Sua manobra falha. O MJ escolhe se você simplesmente não consegue se mover ou se ocorre algum outro efeito prejudicial apropriado para a manobra (por exemplo, ser tirado de curso se tentar voar contra um vento forte).",
                        "falha_critica": "Como falha, mas a consequência é bem pior.",
                    },
                    exemplos_tarefas={
                        "treinado": "subida ou descida íngreme",
                        "especialista": "voar contra o vento, pairar no ar",
                        "mestre": "inverter sua direção",
                        "lendario": "voar através de um vendaval",
                    },
                ),
            ],
        ),
        construir_pericia(
            "Arcanismo",
            "Inteligência",
            "241",
            "Arcanismo mede o quanto você sabe sobre magia e criaturas arcanas.",
            acoes_destreinadas=[
                construir_acao(
                    "Recordar Conhecimento",
                    proficiencia_minima="destreinado",
                    acao_geral=True,
                    custo_acoes="1 ação",
                    tracos=["concentração", "secreto"],
                    descricao="Sobre teorias arcanas, tradições mágicas, criaturas de significância arcana (como dragões e bestas) e dos Planos Astral, Elementais e das Sombras.",
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Aprender uma Magia",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração"],
                    descricao="Aprender uma Magia da tradição arcana (página 234).",
                ),
                construir_acao(
                    "Decifrar Escrita",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração", "secreto"],
                    descricao="Decifrar Escrita sobre teoria arcana (página 236).",
                ),
                construir_acao(
                    "Identificar Magia",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração", "secreto"],
                    descricao="Identificar Magia, particularmente magia arcana (página 238).",
                ),
                construir_acao(
                    "Emprestar uma Magia Arcana",
                    proficiencia_minima="treinado",
                    custo_acoes=None,
                    tracos=["concentração", "exploração"],
                    descricao=(
                        "Se for um conjurador arcano que prepara magias de um grimório, você pode tentar "
                        "preparar uma magia do grimório de outra pessoa. O MJ determina a CD para o teste "
                        "baseado no nível e raridade da magia; essa CD normalmente é um pouco mais fácil "
                        "que Aprender uma Magia."
                    ),
                    resultados={
                        "sucesso": "Você prepara a magia emprestada como parte de sua preparação de magia normal.",
                        "falha": "Você falha em preparar a magia, mas o espaço de magia permanece disponível para preparar uma magia diferente. Você não pode tentar preparar esta magia até a próxima vez em que preparar magias.",
                    },
                ),
            ],
        ),
        construir_pericia(
            "Atletismo",
            "Força",
            "241-243",
            "Atletismo permite que você realize proezas físicas.",
            nota_uso_basico="Quando usar a ação básica Escapar (página 470), você pode utilizar seu modificador de Atletismo em vez de seu modificador de ataque desarmado. Ações de Atletismo com o traço ataque não sofrem a penalidade em testes por armadura.",
            quadros_e_regras_especiais={
                "movimento_forcado": (
                    "A ação Empurrar pode forçar uma criatura a se mover. Quando um efeito lhe forçar "
                    "um movimento, ou se começar a cair, a distância é definida pelo efeito que lhe "
                    "moveu, não por sua Velocidade, e não aciona reações acionadas por movimento."
                ),
                "saltar": (
                    "A ação básica Saltar é usada para Salto em Altura e Salto em Distância. Saltar "
                    "horizontalmente permite até 3 m (Velocidade >= 4,5 m) ou 4,5 m (Velocidade >= 9 m); "
                    "verticalmente até 90 cm verticalmente e 1,5 m horizontalmente."
                ),
                "queda": (
                    "Ao cair mais de 1,5 metros, sofre 1 de dano contundente para cada 60 cm caídos "
                    "(2,5 de dano a cada 1,5 m, arredondado para baixo) e fica prostrado se sofrer "
                    "qualquer dano por queda. Água, neve ou substância macia reduz o cálculo em até 6 m "
                    "(limitado à profundidade). Segurar-se numa Beirada como reação (p. 472) pode reduzir "
                    "ou eliminar o dano."
                ),
            },
            acoes_destreinadas=[
                construir_acao(
                    "Agarrar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["ataque"],
                    requerimentos="Você tem pelo menos uma mão livre. Seu alvo não pode ser mais de um tamanho maior que você.",
                    cd_alvo="CD de Fortitude do alvo",
                    descricao="Você tenta agarrar um oponente com sua mão livre (ou continuar segurando uma criatura que já tenha agarrado) contra a CD de Fortitude dele.",
                    resultados={
                        "sucesso_critico": "Seu oponente fica restringido até o final do seu próximo turno a menos que você se mova ou seu oponente Escape (página 470).",
                        "sucesso": "Seu oponente fica agarrado até o final do seu próximo turno a menos que você se mova ou seu oponente Escape.",
                        "falha": "Você falha em agarrar seu oponente. Se já tiver agarrado ou restringido o oponente usando Agarrar, essas condições são encerradas para a criatura.",
                        "falha_critica": "Se você já tiver agarrado ou restringido o oponente, ele se liberta. Seu alvo pode agarrá-lo como se tivesse obtido sucesso em usar a ação Agarrar contra você, ou forçá-lo a cair e ficar prostrado.",
                    },
                ),
                construir_acao(
                    "Derrubar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["ataque"],
                    requerimentos="Você tem pelo menos uma mão livre. Seu alvo não pode ser mais de um tamanho maior que você.",
                    cd_alvo="CD de Reflexos do alvo",
                    descricao="Você tenta derrubar um oponente no chão contra a CD de Reflexos dele.",
                    resultados={
                        "sucesso_critico": "O alvo cai, fica prostrado e sofre 1d6 de dano contundente.",
                        "sucesso": "O alvo cai e fica prostrado.",
                        "falha_critica": "Você perde o equilíbrio, cai e fica prostrado.",
                    },
                ),
                construir_acao(
                    "Empurrar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["ataque"],
                    requerimentos="Você tem pelo menos uma mão livre. Seu alvo não pode ser mais de um tamanho maior que você.",
                    cd_alvo="CD de Fortitude do alvo",
                    descricao="Você tenta empurrar um oponente para longe contra a CD de Fortitude dele.",
                    resultados={
                        "sucesso_critico": "Você empurra seu oponente até 3 metros para longe de você. Você pode Andar após isso, mas deve mover-se a mesma distância e na mesma direção.",
                        "sucesso": "Você empurra seu oponente 1,5 metros para trás. Você pode Andar após isso, mas deve mover-se a mesma distância e na mesma direção.",
                        "falha_critica": "Você perde o equilíbrio, cai e fica prostrado.",
                    },
                ),
                construir_acao(
                    "Escalar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["movimento"],
                    requerimentos="Você tem ambas as mãos livres.",
                    descricao=(
                        "Você se move para cima, para baixo ou por uma inclinação. A menos que seja "
                        "particularmente fácil, faz um teste de Atletismo. Você fica desprevenido a "
                        "menos que possua uma Velocidade de escalada."
                    ),
                    resultados={
                        "sucesso_critico": "Você se move para cima, através de, ou desce seguramente a inclinação por 1,5 metros mais 1,5 metros para cada 6 metros de sua Velocidade em terra (3 metros para a maioria dos PJs).",
                        "sucesso": "Você se move de forma segura por 1,5 metros para cada 6 metros de sua Velocidade em terra (1,5 metros para a maioria dos PJs; mínimo 1,5 metros se sua Velocidade for menor que 6 metros).",
                        "falha_critica": "Você cai. Se começou a escalar em solo estável, você cai e fica prostrado.",
                    },
                    exemplos_tarefas={
                        "destreinado": "escadas, encostas íngremes, árvores de galhos baixos",
                        "treinado": "cordames, cordas, árvore típica",
                        "especialista": "parede com pequenos apoios para mãos e pés",
                        "mestre": "teto com apoios para mãos e pés, muro de pedra",
                        "lendario": "superfície lisa",
                    },
                ),
                construir_acao(
                    "Forçar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["ataque"],
                    descricao=(
                        "Utilizando seu corpo, uma alavanca ou outra ferramenta, você tenta forçar a "
                        "abertura de uma porta, janela, recipiente ou portão pesado (ou atravessar paredes). "
                        "Sem um pé-de-cabra, sofre –2 de penalidade de item no teste de Atletismo."
                    ),
                    resultados={
                        "sucesso_critico": "Você abre a porta, janela, recipiente ou portão e pode evitar danificar o item no processo.",
                        "sucesso": "Você quebra a porta, janela, recipiente ou portão para abri-lo, e o objeto aberto sofre a condição quebrado (ou dano sem quebrar se especialmente resistente).",
                        "falha_critica": "Sua tentativa emperra a porta, janela, recipiente ou portão, impondo –2 de penalidade de circunstância em tentativas futuras de Forçá-lo.",
                    },
                    exemplos_tarefas={
                        "destreinado": "tecido, vidro frágil",
                        "treinado": "gelo, vidro resistente",
                        "especialista": "porta de madeira frágil, rastrilho de madeira",
                        "mestre": "porta de madeira resistente, rastrilho de ferro, barra de metal",
                        "lendario": "porta de pedra ou ferro",
                    },
                ),
                construir_acao(
                    "Nadar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["movimento"],
                    descricao=(
                        "Você se impulsiona pela água. Na maioria das águas calmas obtém sucesso sem teste; "
                        "em água turbulenta ou perigosa, faz teste de Atletismo. Se encerrar seu turno na "
                        "água sem obter sucesso em Nadar nesse turno, afunda 3 m ou é movido pela corrente "
                        "(exceto se sua última ação foi entrar na água). Submerso exige prender a respiração "
                        "a cada rodada (p. 478)."
                    ),
                    resultados={
                        "sucesso_critico": "Você se move até 3 metros pela água, mais 1,5 metros para cada 6 metros de sua Velocidade em terra (4,5 metros para a maioria dos PJs).",
                        "sucesso": "Você se move 1,5 metros pela água, mais 1,5 metros para cada 6 metros de sua Velocidade em terra (3 metros para a maioria dos PJs).",
                        "falha_critica": "Você não faz qualquer progresso e, se estiver prendendo sua respiração, perde 1 rodada de ar.",
                    },
                    exemplos_tarefas={
                        "destreinado": "lago ou outras águas calmas",
                        "treinado": "água corrente, como um rio",
                        "especialista": "rio com correnteza rápida",
                        "mestre": "mar revolto",
                        "lendario": "redemoinho, cachoeira",
                    },
                ),
                construir_acao(
                    "Salto em Altura",
                    proficiencia_minima="destreinado",
                    custo_acoes="2 ações",
                    tracos=[],
                    cd_alvo="CD 30 (padrão, ajustável pelo MJ)",
                    descricao=(
                        "Você Anda e depois faz um Salto vertical e um teste de Atletismo CD 30 para "
                        "aumentar a altura de seu salto. Se não tiver Andado pelo menos 3 metros, falha "
                        "automaticamente no teste."
                    ),
                    resultados={
                        "sucesso_critico": "Aumente a distância vertical máxima para 2,4 metros, ou aumente a distância vertical máxima para 1,5 metros e a distância horizontal máxima para 3 metros.",
                        "sucesso": "Aumente a distância vertical máxima para 1,5 metros.",
                        "falha": "Você Salta normalmente.",
                        "falha_critica": "Você não Salta de forma nenhuma e, em vez disso, cai prostrado em seu espaço.",
                    },
                ),
                construir_acao(
                    "Salto em Distância",
                    proficiencia_minima="destreinado",
                    custo_acoes="2 ações",
                    tracos=[],
                    cd_alvo="5 para cada 1,5 metros de distância (ex.: CD 20 para 6 m)",
                    descricao=(
                        "Você Anda e depois faz um Salto horizontal e um teste de Atletismo para aumentar o "
                        "comprimento de seu salto. Não pode Saltar mais longe do que sua Velocidade. Se não "
                        "tiver Andado pelo menos 3 metros ou se tentar saltar em direção diferente da que "
                        "Andou, falha automaticamente."
                    ),
                    resultados={
                        "sucesso": "Aumente a distância horizontal máxima que você Salta para a distância desejada.",
                        "falha": "Você Salta normalmente.",
                        "falha_critica": "Você Salta normalmente, mas cai e aterrissa prostrado.",
                    },
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Desarmar",
                    proficiencia_minima="treinado",
                    custo_acoes="1 ação",
                    tracos=["ataque"],
                    requerimentos="Você tem pelo menos uma mão livre. Seu alvo não pode ser mais de um tamanho maior que você.",
                    cd_alvo="CD de Reflexos do oponente",
                    descricao="Você tenta derrubar algo que um oponente esteja segurando contra a CD de Reflexos dele.",
                    resultados={
                        "sucesso_critico": "Você derruba o item da empunhadura do oponente. O item cai no chão no espaço do oponente.",
                        "sucesso": "Você enfraquece a empunhadura de seu oponente no item. Até o início do turno dessa criatura, tentativas de Desarmar o oponente desse item recebem +2 de bônus de circunstância e o alvo sofre –2 de penalidade de circunstância em ataques com o item ou outros testes que exijam uma empunhadura firme nesse item.",
                        "falha_critica": "Você perde o equilíbrio e fica desprevenido até o início de seu próximo turno.",
                    },
                ),
            ],
        ),
        construir_pericia(
            "Diplomacia",
            "Carisma",
            "243-244",
            "Você influencia os outros através de negociação e lisonjas.",
            quadros_e_regras_especiais={
                "alterando_atitudes": {
                    "atitudes": {
                        "Prestativa": "Disposto a ajudá-lo e responde favoravelmente a seus pedidos.",
                        "Amistosa": "Possui uma boa atitude em relação a você, mas não necessariamente arrisca seu pescoço para ajudar.",
                        "Indiferente": "Não se importa com você de maneira alguma. (A maioria dos PdMs começa indiferente.)",
                        "Inamistosa": "Não gosta de você e não quer ajudá-lo.",
                        "Hostil": "Trabalha ativamente contra você — e pode atacá-lo simplesmente por desgostar de você.",
                    },
                    "regra_pjs": (
                        "Em hipótese nenhuma alguém é capaz de mudar a atitude de um personagem jogador "
                        "com estas perícias; os jogadores fazem as decisões definitivas sobre como seus "
                        "personagens respondem."
                    ),
                },
            },
            acoes_destreinadas=[
                construir_acao(
                    "Impressionar",
                    proficiencia_minima="destreinado",
                    custo_acoes=None,
                    tracos=["auditivo", "concentração", "exploração", "linguístico", "mental"],
                    cd_alvo="CD de Vontade do alvo",
                    descricao=(
                        "Com pelo menos 1 minuto de conversa, falas carismáticas, lisonjas e outros atos "
                        "de boa vontade, você faz um teste de Diplomacia contra a CD de Vontade do alvo. "
                        "Boas impressões (ou más, em falha crítica) duram pelo menos pela interação social atual."
                    ),
                    resultados={
                        "sucesso_critico": "A atitude do alvo em relação a você melhora em dois passos.",
                        "sucesso": "A atitude do alvo em relação a você melhora em um passo.",
                        "falha_critica": "A atitude do alvo em relação a você piora em um passo.",
                    },
                ),
                construir_acao(
                    "Obter Informação",
                    proficiencia_minima="destreinado",
                    custo_acoes=None,
                    tracos=["exploração", "secreto"],
                    descricao=(
                        "Você vasculha mercados locais, tavernas e locais de reunião na tentativa de "
                        "descobrir algo sobre um indivíduo ou tópico específico (normalmente leva 2 horas, "
                        "às vezes mais; pode envolver gastos em barganhas, bebidas ou presentes)."
                    ),
                    resultados={
                        "sucesso": "Você coleta informações sobre o indivíduo ou tópico. O MJ determina as especificidades.",
                        "falha_critica": "Você coleta informações incorretas sobre o indivíduo ou tópico.",
                    },
                    exemplos_tarefas={
                        "destreinado": "fofoca atual",
                        "treinado": "rumor comum",
                        "especialista": "rumor obscuro, segredo mau guardado",
                        "mestre": "informação bem guardada ou esotérica",
                        "lendario": "informação conhecida somente por poucos incrivelmente selecionados ou apenas por seres extraordinários",
                    },
                ),
                construir_acao(
                    "Pedir",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["auditivo", "concentração", "linguístico", "mental"],
                    descricao=(
                        "Você faz um pedido a uma criatura que seja amistosa ou prestativa em relação a você, "
                        "em termos aceitáveis dada sua atitude atual."
                    ),
                    resultados={
                        "sucesso_critico": "O alvo concorda com seu pedido sem exigências.",
                        "sucesso": "O alvo concorda com seu pedido, mas pode demandar provisões adicionais ou alterações no pedido.",
                        "falha": "O alvo recusa o pedido, embora possa propor uma alternativa que pareça menos extrema.",
                        "falha_critica": "Não apenas o alvo recusa o pedido, como a atitude dele em relação a você piora em um passo devido à temeridade do pedido.",
                    },
                ),
            ],
            acoes_treinadas=[],
        ),
        construir_pericia(
            "Dissimulação",
            "Carisma",
            "244-245",
            "Você pode enganar e iludir os outros utilizando disfarces, mentiras e outras formas de subterfúgio.",
            acoes_destreinadas=[
                construir_acao(
                    "Criar uma Distração",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["mental"],
                    cd_alvo="CDs de Percepção das criaturas",
                    observacao="Adquire o traço manuseio (se usar gesto ou truque) ou os traços auditivo e linguístico (se usar palavras distrativas).",
                    descricao=(
                        "Com um gesto, truque ou palavras distrativas, faz um único teste de Dissimulação "
                        "contra as CDs de Percepção das criaturas. Seja bem-sucedido ou não, as criaturas "
                        "recebem +4 de bônus de circunstância contra suas tentativas de Criar uma Distração "
                        "por 1 minuto."
                    ),
                    resultados={
                        "sucesso": "Você se torna escondido para cada criatura com CD de Percepção <= resultado até o final do seu turno (termina se realizar ação diferente de Dar um Passo, Esconder ou Esgueirar; se Golpear, o alvo fica desprevenido contra esse ataque e você se torna observado após executá-lo).",
                        "falha": "Você não desvia a atenção de criaturas com CD de Percepção > resultado, e elas ficam cientes da tentativa de enganá-las.",
                    },
                ),
                construir_acao(
                    "Mentir",
                    proficiencia_minima="destreinado",
                    custo_acoes="Pelo menos 1 rodada",
                    tracos=["auditivo", "concentração", "linguístico", "mental", "secreto"],
                    cd_alvo="CD de Percepção de cada criatura",
                    descricao=(
                        "Você tenta enganar alguém com uma inverdade (pelo menos 1 rodada, ou mais se "
                        "elaborada), rolando um único teste de Dissimulação contra a CD de Percepção de "
                        "cada criatura. Posteriormente, a critério do MJ, quem acreditou pode fazer Percepção "
                        "para Sentir Motivação contra sua CD de Dissimulação se surgir evidência contrária."
                    ),
                    resultados={
                        "sucesso": "O alvo acredita em sua mentira.",
                        "falha": "O alvo não acredita em sua mentira e recebe +4 de bônus de circunstância contra suas tentativas de Mentir pela duração de sua conversa.",
                    },
                ),
                construir_acao(
                    "Personificar",
                    proficiencia_minima="destreinado",
                    custo_acoes=None,
                    tracos=["concentração", "exploração", "manuseio", "secreto"],
                    cd_alvo="CD de Percepção da criatura (ou oposição contra CD de Dissimulação ao Buscar)",
                    descricao=(
                        "Você cria um disfarce para se passar por alguém ou algo que não é. Montar um "
                        "disfarce convincente leva 10 minutos e requer um kit de disfarce (página 290). "
                        "Criaturas só costumam detectar com Buscar contra sua CD de Dissimulação, ou em "
                        "interação direta via teste secreto de Dissimulação contra CD de Percepção."
                    ),
                    resultados={
                        "sucesso": "Você leva a criatura a pensar que você é a pessoa em que está disfarçada. Pode ter de fazer novo teste se seu comportamento mudar.",
                        "falha": "A criatura nota que você não é quem afirma ser.",
                        "falha_critica": "A criatura nota que você não é quem afirma ser e o reconhece caso o conheça previamente sem um disfarce.",
                    },
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Fintar",
                    proficiencia_minima="treinado",
                    custo_acoes="1 ação",
                    tracos=["mental"],
                    requerimentos="Você está no alcance corpo a corpo do oponente que está tentando Fintar.",
                    cd_alvo="CD de Percepção do oponente",
                    descricao="Com um floreio enganoso, faz um teste de Dissimulação contra a CD de Percepção do oponente.",
                    resultados={
                        "sucesso_critico": "O alvo fica desprevenido contra ataques corpo a corpo que você desferir contra ele até o final do seu próximo turno.",
                        "sucesso": "O alvo fica desprevenido contra ataques corpo a corpo que você desferir contra ele até o final do seu turno atual.",
                        "falha_critica": "Sua finta se volta contra você. Você fica desprevenido contra ataques corpo a corpo que o alvo desferir contra você até o final do seu próximo turno.",
                    },
                ),
            ],
        ),
        construir_pericia(
            "Furtividade",
            "Destreza",
            "245-246",
            "Você é habilidoso em evitar detecção, permitindo que passe despercebido por adversários, se esconda ou oculte um item.",
            quadros_e_regras_especiais={
                "sendo_furtivo_estados_deteccao": {
                    "fluxo": "Combinar Esconder (ficar escondido atrás de cobertura ou ocultação) seguido de Esgueirar (mover-se à metade da Velocidade para ficar indetectado). Criaturas tentam encontrá-lo com Buscar (p. 470).",
                    "estados": {
                        "Observado": "Você está no campo de visão claro da criatura.",
                        "Escondido": "A criatura sabe sua localização, mas não consegue lhe ver.",
                        "Indetectado": "A criatura não sabe a sua localização.",
                    },
                },
            },
            acoes_destreinadas=[
                construir_acao(
                    "Esconder",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["secreto"],
                    cd_alvo="CD de Percepção de cada criatura observando",
                    descricao=(
                        "Você fica atrás de cobertura (ou cobertura maior) ou em área de ocultação para "
                        "tornar-se escondido em vez de observado, recebendo o bônus de circunstância de "
                        "cobertura (+2 ou +4) no teste secreto de Furtividade."
                    ),
                    resultados={
                        "sucesso": "Você fica escondido em vez de observado (ou mantém escondido/indetectado). Permanece até perder cobertura/ocultação ou realizar ação diferente de Dar um Passo, Esconder ou Esgueirar (se Golpear, o alvo fica desprevenido contra esse ataque e você se torna observado após executá-lo).",
                    },
                ),
                construir_acao(
                    "Esgueirar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["movimento", "secreto"],
                    cd_alvo="CD de Percepção de cada criatura para a qual estava escondido ou indetectado",
                    descricao=(
                        "Você Anda até metade de sua Velocidade (ou metade de Escalar, Escavar, Nadar ou Voar) "
                        "para mover-se enquanto estiver ou permanecer indetectado. Ao final do movimento, o "
                        "MJ rola teste secreto de Furtividade (precisa terminar com cobertura ou ocultação "
                        "contra a criatura, salvo impossibilidade física de vê-lo como invisibilidade/cegueira/"
                        "escuridão sem visão no escuro)."
                    ),
                    resultados={
                        "sucesso": "Você fica indetectado pela criatura durante e ao final do movimento (mesmas restrições de ações que quebram furtividade; falar ou fazer barulho alto torna-o escondido em vez de indetectado).",
                        "falha": "Um som revelador ou outro sinal indica sua posição; você fica escondido durante todo o movimento e permanece assim.",
                        "falha_critica": "Você é observado pela criatura durante todo o movimento e permanece assim (ou fica apenas escondido se estiver invisível e estava escondido).",
                    },
                ),
                construir_acao(
                    "Ocultar um Objeto",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["manuseio", "secreto"],
                    cd_alvo="CD de Percepção de observadores passivos (ou Percepção vs sua CD de Furtividade ao Buscar)",
                    descricao=(
                        "Você esconde um objeto pequeno em si (como uma arma de Volume leve) ou em um local "
                        "(matagal, compartimento secreto). Um único teste secreto vale contra todos os "
                        "observadores passivos; quem procurar ativamente usa Percepção contra sua CD de Furtividade."
                    ),
                    resultados={
                        "sucesso": "O objeto permanece indetectado.",
                        "falha": "O objeto é encontrado por quem o procura.",
                    },
                ),
            ],
            acoes_treinadas=[],
        ),
        construir_pericia(
            "Intimidação",
            "Carisma",
            "246-247",
            "Você curva os outros à sua vontade usando ameaças.",
            acoes_destreinadas=[
                construir_acao(
                    "Coagir",
                    proficiencia_minima="destreinado",
                    custo_acoes=None,
                    tracos=["auditivo", "concentração", "emoção", "exploração", "linguístico", "mental"],
                    cd_alvo="CD de Vontade do alvo",
                    descricao=(
                        "Com ameaças veladas ou explícitas após pelo menos 1 minuto conversando com uma "
                        "criatura que possa ver e que possa vê-lo ou senti-lo, faz um teste de Intimidação "
                        "contra a CD de Vontade do alvo."
                    ),
                    resultados={
                        "sucesso_critico": "O alvo lhe dá a informação que você busca ou concorda em seguir suas ordens (desde que não prejudiciais) por até 1 dia (definido pelo MJ), ficando então inamistoso se já não fosse inamistoso/hostil, mas amedrontado demais para retaliar a curto prazo.",
                        "sucesso": "Como sucesso crítico, mas após o alvo ficar inamistoso, ele pode decidir agir contra você (reportando às autoridades ou auxiliando seus inimigos).",
                        "falha": "O alvo não faz o que você diz e se torna inamistoso se já não estiver inamistoso ou hostil.",
                        "falha_critica": "O alvo se recusa a consentir, se torna hostil se já não estiver e não pode ser Coagido por você pelo menos por uma semana.",
                    },
                ),
                construir_acao(
                    "Desmoralizar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["auditivo", "concentração", "emoção", "mental"],
                    cd_alvo="CD de Vontade do alvo",
                    descricao=(
                        "Escolha uma criatura a até 9 metros da qual esteja ciente e faça um teste de "
                        "Intimidação contra a CD de Vontade do alvo. Se não falar um idioma, se o alvo não "
                        "compreender seu idioma ou não puder ouvi-lo, sofre –4 de penalidade de circunstância. "
                        "O alvo fica temporariamente imune a suas tentativas de Desmoralizá-lo por 10 minutos."
                    ),
                    resultados={
                        "sucesso_critico": "O alvo fica assustado 2.",
                        "sucesso": "O alvo fica assustado 1.",
                    },
                ),
            ],
            acoes_treinadas=[],
        ),
        construir_pericia(
            "Ladroagem",
            "Destreza",
            "247",
            "Você é treinado em um conjunto particular de perícias favorecidas por ladrões e meliantes.",
            acoes_destreinadas=[
                construir_acao(
                    "Empalmar um Objeto",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["manuseio"],
                    cd_alvo="CDs de Percepção de todas as criaturas observando",
                    descricao=(
                        "Empalmar um pequeno objeto desapossado (normalmente Volume insignificante) sem ser "
                        "percebido exige um único teste de Ladroagem contra as CDs de Percepção de todas as "
                        "criaturas que estão lhe observando. Você pega o objeto independente de sucesso ou falha."
                    ),
                    resultados={
                        "sucesso": "A criatura não percebe você Empalmando o Objeto.",
                        "falha": "A criatura percebe você Empalmando o Objeto e o MJ determina a resposta dela.",
                    },
                ),
                construir_acao(
                    "Furtar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["manuseio"],
                    cd_alvo="CD de Percepção do portador (e de observadores)",
                    descricao=(
                        "Você tenta pegar um objeto pequeno (normalmente Volume insignificante) de outra "
                        "criatura sem ser percebido. Falha automaticamente se a criatura estiver em combate "
                        "ou em guarda. Se estiver em um bolso ou protegido, sofre –5 de penalidade."
                    ),
                    resultados={
                        "sucesso": "Você furta o objeto sem o portador perceber, ou um observador não vê que você pega ou tenta pegar o item.",
                        "falha": "O portador do item percebe sua tentativa antes de você conseguir pegar o objeto, ou um observador vê que você pega ou tenta pegar o item.",
                    },
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Abrir uma Fechadura",
                    proficiencia_minima="treinado",
                    custo_acoes="2 ações",
                    tracos=["manuseio"],
                    requerimentos="Você possui ferramentas de ladrão (página 290).",
                    cd_alvo="CD determinada pela fechadura (página 290)",
                    descricao=(
                        "Abre fechadura sem chave (fechaduras superiores podem requerer vários sucessos). "
                        "Sem ferramentas apropriadas, o MJ pode permitir ferramentas improvisadas (tratadas "
                        "como ferramentas de má qualidade)."
                    ),
                    resultados={
                        "sucesso_critico": "Você destranca a fechadura ou obtém dois sucessos para abrir uma fechadura complexa. Você não deixa traços de sua interferência.",
                        "sucesso": "Você destranca a fechadura ou obtém um sucesso para abrir uma fechadura complexa.",
                        "falha_critica": "Você quebra suas ferramentas. Consertá-las requer usar Manufatura para Repará-las ou providenciar apetrechos de reposição (custando 3 pp; ou 3 po para ferramentas de ladrão infiltrador).",
                    },
                ),
                construir_acao(
                    "Desabilitar um Dispositivo",
                    proficiencia_minima="treinado",
                    custo_acoes="2 ações",
                    tracos=["manuseio"],
                    requerimentos="Alguns dispositivos exigem que você utilize ferramentas de ladrão (página 290) para desabilitá-los.",
                    descricao=(
                        "Permite desarmar uma armadilha ou outro dispositivo complexo (frequentemente exige "
                        "vários sucessos e, às vezes, graduação específica de proficiência em Ladroagem)."
                    ),
                    resultados={
                        "sucesso_critico": "Você desabilita o dispositivo ou obtém dois sucessos para desabilitar um dispositivo complexo. Você não deixa traços de sua interferência e pode rearmar o dispositivo posteriormente se esse tipo de dispositivo puder ser rearmado.",
                        "sucesso": "Você desabilita o dispositivo ou obtém um sucesso para desabilitar um dispositivo complexo.",
                        "falha_critica": "Você aciona o dispositivo.",
                    },
                ),
            ],
        ),
        construir_pericia(
            "Manufatura",
            "Inteligência",
            "247-249",
            "Você pode utilizar esta perícia para criar, compreender e reparar itens.",
            quadros_e_regras_especiais={
                "consumiveis_e_municao": (
                    "Você pode Manufaturar itens com o traço consumível em lotes de até 4 do mesmo item "
                    "com um único teste (suprindo matéria-prima para todos desde o início e completando "
                    "o lote de uma vez). Munição não-mágica é manufaturada em lotes conforme a Tabela 6–8 "
                    "(normalmente 10 unidades)."
                ),
                "obtendo_formulas": (
                    "Acesso às fórmulas de todos os itens comuns do Capítulo 6 ao comprar um livro básico "
                    "de manufatura (p. 291); demais fórmulas seguem regras da página 293."
                ),
            },
            acoes_destreinadas=[
                construir_acao(
                    "Recordar Conhecimento",
                    proficiencia_minima="destreinado",
                    acao_geral=True,
                    custo_acoes="1 ação",
                    tracos=["concentração", "secreto"],
                    descricao="Sobre reações alquímicas, valor de itens, engenharia, materiais inusitados e criaturas alquímicas ou mecânicas (normalmente inclui constructos).",
                ),
                construir_acao(
                    "Reparar",
                    proficiencia_minima="destreinado",
                    custo_acoes=None,
                    tracos=["exploração", "manuseio"],
                    requerimentos="Você possui um kit de reparos (página 291).",
                    cd_alvo="CD determinada pelo MJ (normalmente igual à CD de Manufatura do item)",
                    descricao="Você gasta 10 minutos consertando um item danificado com ambas as mãos sobre uma superfície estável. Não pode Reparar um item destruído.",
                    resultados={
                        "sucesso_critico": "Restaura 10 PV + 10 PV por graduação de proficiência em Manufatura (20 T, 30 E, 40 M, 50 L).",
                        "sucesso": "Restaura 5 PV + 5 PV por graduação de proficiência em Manufatura (10 T, 15 E, 20 M, 25 L).",
                        "falha_critica": "Você causa 2d6 de dano ao item. Aplique a Dureza do item a este dano.",
                    },
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Ganhar Proventos",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["recesso"],
                    descricao="Manufaturando bens para o mercado (página 237–238).",
                ),
                construir_acao(
                    "Identificar Alquimia",
                    proficiencia_minima="treinado",
                    custo_acoes=None,
                    tracos=["concentração", "exploração", "secreto"],
                    requerimentos="Você possui ferramentas de alquimista (página 290).",
                    descricao="Identifica a natureza de um item alquímico com 10 minutos de testes.",
                    resultados={
                        "sucesso": "Você identifica o item e os meios para ativá-lo.",
                        "falha": "Você falha em identificar o item, mas pode tentar novamente.",
                        "falha_critica": "Você identifica o item erroneamente como outro item à escolha do MJ.",
                    },
                ),
                construir_acao(
                    "Manufaturar",
                    proficiencia_minima="treinado",
                    custo_acoes=None,
                    tracos=["manuseio", "recesso"],
                    requerimentos=(
                        "Item de seu nível ou inferior (itens sem nível contam como 0; nível 9+ exige "
                        "Mestre, nível 16+ exige Lendário); possuir a fórmula; ferramentas apropriadas e "
                        "oficina/laboratório/forja; matéria-prima no valor de pelo menos metade do Preço; "
                        "talentos Manufatura Alquímica, Manufatura Mágica ou Manufatura de Arapuca quando "
                        "aplicável."
                    ),
                    descricao=(
                        "Após gastar 4 dias de trabalho, você faz um teste de Manufatura. Em sucesso, pode "
                        "completar imediatamente pagando o restante do Preço em materiais, ou gastar dias "
                        "adicionais de recesso reduzindo o custo restante conforme a Tabela 4–3 usando seu "
                        "próprio nível como nível da tarefa."
                    ),
                    resultados={
                        "sucesso_critico": "Sua tentativa é bem-sucedida. Cada dia adicional gasto Manufaturando reduz os materiais necessários em uma quantidade baseada em seu nível + 1 e sua graduação de proficiência.",
                        "sucesso": "Sua tentativa é bem-sucedida. Cada dia adicional gasto Manufaturando reduz os materiais necessários em uma quantidade baseada em seu nível e sua graduação de proficiência.",
                        "falha": "Você falha em completar o item. Pode recuperar 100% da matéria-prima que supriu; para tentar novamente deve recomeçar do zero.",
                        "falha_critica": "Você falha em completar o item e perde 10% da matéria-prima suprida (recupera 90%); para tentar novamente deve recomeçar do zero.",
                    },
                ),
            ],
        ),
        construir_pericia(
            "Medicina",
            "Sabedoria",
            "249-250",
            "Você pode remendar ferimentos e ajudar pessoas a se recuperarem de doenças e venenos.",
            acoes_destreinadas=[
                construir_acao(
                    "Recordar Conhecimento",
                    proficiencia_minima="destreinado",
                    acao_geral=True,
                    custo_acoes="1 ação",
                    tracos=["concentração", "secreto"],
                    descricao="Sobre doenças, ferimentos, venenos e outros padecimentos (inclui realizar autópsias gastando 10 minutos ou mais procurando padrões de ferimento).",
                ),
                construir_acao(
                    "Administrar Primeiros Socorros",
                    proficiencia_minima="destreinado",
                    custo_acoes="2 ações",
                    tracos=["manuseio"],
                    requerimentos="Você possui ferramentas de curandeiro (página 290).",
                    cd_alvo="Estabilizar: 5 + CD de rolagem de recuperação (normalmente 15 + valor de morrendo); Parar Sangramento: CD do efeito que causou o sangramento",
                    descricao=(
                        "Você presta primeiros socorros a uma criatura adjacente que está sangrando ou "
                        "morrendo (escolha um antes de rolar)."
                    ),
                    observacao="Na Tabela 4–1 (p. 235) aparece com ícone de 1 ação por erro tipográfico, mas a descrição oficial da ação na página 249 define 2 ações.",
                    resultados={
                        "sucesso": "Estabilizar: a criatura perde a condição morrendo (permanece inconsciente). Parar Sangramento: a criatura faz um teste simples para encerrar o sangramento.",
                        "falha_critica": "Estabilizar: o valor de morrendo aumenta em 1. Parar Sangramento: a criatura sofre imediatamente dano igual ao dano persistente de sangramento dela.",
                    },
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Tratar Doença",
                    proficiencia_minima="treinado",
                    custo_acoes=None,
                    tracos=["manuseio", "recesso"],
                    requerimentos="Você possui ferramentas de curandeiro (página 290).",
                    cd_alvo="CD da doença",
                    descricao="Passa pelo menos 8 horas cuidando de uma criatura adoecida. Uma tentativa por salvamento contra a doença.",
                    resultados={
                        "sucesso_critico": "Concede +4 de bônus de circunstância na próxima jogada de salvamento contra a doença.",
                        "sucesso": "Concede +2 de bônus de circunstância na próxima jogada de salvamento contra a doença.",
                        "falha_critica": "Faz a criatura sofrer –2 de penalidade de circunstância na próxima jogada de salvamento contra a doença.",
                    },
                ),
                construir_acao(
                    "Tratar Ferimentos",
                    proficiencia_minima="treinado",
                    custo_acoes=None,
                    tracos=["cura", "exploração", "manuseio"],
                    requerimentos="Você possui ferramentas de curandeiro (página 290).",
                    cd_alvo="CD 15 (padrão); Especialista pode tentar CD 20 (+10 PV); Mestre CD 30 (+30 PV); Lendário CD 40 (+50 PV)",
                    descricao=(
                        "Passa 10 minutos tratando uma criatura viva ferida (inclusive você mesmo). O alvo "
                        "fica temporariamente imune por 1 hora (sobrepõe-se ao tempo do tratamento). Se "
                        "obtiver sucesso e tratar por 1 hora completa, dobra os PV recuperados."
                    ),
                    resultados={
                        "sucesso_critico": "O alvo recupera 4d8 Pontos de Vida (+ bônus de CD elevada, se aplicável) e a condição ferido dele é removida.",
                        "sucesso": "O alvo recupera 2d8 Pontos de Vida (+ bônus de CD elevada, se aplicável) e a condição ferido dele é removida.",
                        "falha_critica": "O alvo sofre 1d8 pontos de dano.",
                    },
                ),
                construir_acao(
                    "Tratar Veneno",
                    proficiencia_minima="treinado",
                    custo_acoes="1 ação",
                    tracos=["manuseio"],
                    requerimentos="Você possui ferramentas de curandeiro (página 290).",
                    cd_alvo="CD do veneno",
                    descricao="Trata um paciente para impedir que um veneno se alastre. Uma tentativa por salvamento contra o veneno.",
                    resultados={
                        "sucesso_critico": "Concede +4 de bônus de circunstância na próxima jogada de salvamento contra o veneno.",
                        "sucesso": "Concede +2 de bônus de circunstância na próxima jogada de salvamento contra o veneno.",
                        "falha_critica": "Faz a criatura sofrer –2 de penalidade de circunstância na próxima jogada de salvamento contra o veneno.",
                    },
                ),
            ],
        ),
        construir_pericia(
            "Natureza",
            "Sabedoria",
            "250-251",
            "Você sabe muito sobre o mundo natural, além de comandar e treinar animais e bestas mágicas.",
            quadros_e_regras_especiais={
                "animais_comandados": (
                    "Um animal é criatura independente com Inteligência limitada que compreende apenas "
                    "instruções simples (ações básicas Andar, Buscar, Golpear, Levantar, Saltar ou "
                    "atividades que conheça). Age assim que puder no turno dele e esquece comandos "
                    "além do que puder executar no turno."
                ),
            },
            acoes_destreinadas=[
                construir_acao(
                    "Recordar Conhecimento",
                    proficiencia_minima="destreinado",
                    acao_geral=True,
                    custo_acoes="1 ação",
                    tracos=["concentração", "secreto"],
                    descricao="Sobre fauna, flora, geografia, clima, o ambiente, criaturas de origem natural (animais, bestas, fadas e plantas), Primeiro Mundo, os Planos Material e Elementais.",
                ),
                construir_acao(
                    "Comandar um Animal",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["auditivo", "concentração"],
                    cd_alvo="CD de Vontade do animal",
                    descricao=(
                        "Você dá uma ordem a um animal. Falha automaticamente se o animal estiver hostil ou "
                        "inamistoso. Se estiver prestativo, aumente seu grau de sucesso em um passo. Pode "
                        "gastar várias ações para o animal realizar a mesma quantidade de ações básicas."
                    ),
                    resultados={
                        "sucesso": "O animal obedece a seu comando no próximo turno dele.",
                        "falha": "O animal hesita ou resiste, e não faz nada.",
                        "falha_critica": "O animal lhe desobedece ou entende errado, e faz alguma outra ação determinada pelo MJ.",
                    },
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Aprender uma Magia",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração"],
                    descricao="Aprender uma Magia da tradição primal (página 234).",
                ),
                construir_acao(
                    "Identificar Magia",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração", "secreto"],
                    descricao="Identificar Magia, particularmente magia primal (página 238).",
                ),
            ],
        ),
        construir_pericia(
            "Ocultismo",
            "Inteligência",
            "251",
            "Você conhece muito sobre filosofias antigas, saberes esotéricos, misticismo obscuro e criaturas sobrenaturais.",
            acoes_destreinadas=[
                construir_acao(
                    "Recordar Conhecimento",
                    proficiencia_minima="destreinado",
                    acao_geral=True,
                    custo_acoes="1 ação",
                    tracos=["concentração", "secreto"],
                    descricao="Sobre mistérios antigos, filosofias obscuras, criaturas de significância ocultista (aberrações, espíritos e limos) e dos Planos Astral, de Energia Positiva, de Energia Negativa, Etéreo e das Sombras.",
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Aprender uma Magia",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração"],
                    descricao="Aprender uma Magia da tradição ocultista (página 234).",
                ),
                construir_acao(
                    "Decifrar Escrita",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração", "secreto"],
                    descricao="Decifrar Escrita em tópicos ocultistas, incluindo sistemas metafísicos complexos, princípios sincréticos, filosofias bizarras e divagações incoerentes (página 236).",
                ),
                construir_acao(
                    "Identificar Magia",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração", "secreto"],
                    descricao="Identificar Magia, particularmente magia ocultista (página 238).",
                ),
            ],
        ),
        construir_pericia(
            "Performance",
            "Carisma",
            "251",
            "Você é competente em uma forma de performance, utilizando seus talentos para impressionar uma multidão ou ganhar a vida.",
            quadros_e_regras_especiais={
                "competencia_basica": (
                    "Se você não atender às demandas físicas ou mentais da forma de arte (ex.: Destreza "
                    "negativa ao dançar, Inteligência negativa ao discursar), o MJ pode aplicar uma "
                    "penalidade baseada no atributo relevante."
                ),
                "tracos_de_performance": "Recebe traços adicionais conforme o tipo de performance (vide tabelas.tracos_de_performance).",
            },
            acoes_destreinadas=[
                construir_acao(
                    "Performar",
                    proficiencia_minima="destreinado",
                    custo_acoes="1 ação",
                    tracos=["concentração"],
                    descricao=(
                        "Você faz uma performance breve (canção, dança rápida ou piadas) para provar "
                        "capacidade ou impressionar rapidamente; pode influenciar CDs de Diplomacia "
                        "subsequentes ou mudar atitudes a critério do MJ."
                    ),
                    resultados={
                        "sucesso_critico": "Sua performance impressiona os observadores e eles provavelmente compartilharão histórias de sua habilidade.",
                        "sucesso": "Você se prova, e observadores apreciam a qualidade de sua performance.",
                        "falha": "Sua performance passa despercebida.",
                        "falha_critica": "Você demonstra somente incompetência.",
                    },
                    exemplos_tarefas={
                        "destreinado": "audiência de plebeus",
                        "treinado": "audiência de artesãos",
                        "especialista": "audiência de mercadores ou baixa nobreza",
                        "mestre": "audiência de alta nobreza ou baixa realeza",
                        "lendario": "audiência de alta realeza ou seres de outros mundos",
                    },
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Ganhar Proventos",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["recesso"],
                    descricao="Encenando uma performance diante de uma audiência (página 237–238).",
                ),
            ],
        ),
        construir_pericia(
            "Religião",
            "Sabedoria",
            "251",
            "Os segredos de divindades, dogmas, fés e dos reinos de criaturas divinas sublimes e sinistras são conhecidos por você.",
            acoes_destreinadas=[
                construir_acao(
                    "Recordar Conhecimento",
                    proficiencia_minima="destreinado",
                    acao_geral=True,
                    custo_acoes="1 ação",
                    tracos=["concentração", "secreto"],
                    descricao="Sobre agentes divinos, detalhes e nuances da teologia, mitos obscuros a respeito de uma fé, criaturas de significância religiosa (celestiais, ínferos e mortos-vivos), a Esfera Externa e os Planos de Energia Positiva e Negativa.",
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Aprender uma Magia",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração"],
                    descricao="Aprender uma Magia da tradição divina (página 234).",
                ),
                construir_acao(
                    "Decifrar Escrita",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração", "secreto"],
                    descricao="Decifrar Escrita de natureza religiosa, incluindo alegorias, homilias e provérbios (página 236).",
                ),
                construir_acao(
                    "Identificar Magia",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração", "secreto"],
                    descricao="Identificar Magia, particularmente magia divina (página 238).",
                ),
            ],
        ),
        construir_pericia(
            "Saber",
            "Inteligência",
            "251-252",
            "Você possui informações especializadas sobre um tópico estrito. Cada subcategoria de Saber conta como sua própria perícia.",
            quadros_e_regras_especiais={
                "regras_saber": [
                    "Cada subcategoria conta como sua própria perícia independente (incrementar Saber de Planos não aumenta Saber de Navegação).",
                    "Subcategorias de Saber são sempre menos abrangentes do que outras perícias de Recordar Conhecimento e nunca devem suplantá-las completamente.",
                    "Se possuir várias subcategorias aplicáveis ou que se sobreponham a outra perícia, você pode usar a perícia com o melhor modificador (ou qualquer outra que preferir).",
                ],
                "subcategorias_comuns_nomeadas": [
                    "Saber Acadêmico",
                    "Saber de Agricultura",
                    "Saber de Arquitetura",
                    "Saber de Artes",
                    "Saber de Bibliotecas",
                    "Saber de Caça",
                    "Saber de Circo",
                    "Saber de Contabilidade",
                    "Saber de Curtume",
                    "Saber de Engenharia",
                    "Saber de Escotismo",
                    "Saber de Escrita",
                    "Saber de Estábulos",
                    "Saber de Genealogia",
                    "Saber de Gladiadores",
                    "Saber de Guerra",
                    "Saber de Guildas",
                    "Saber de Heráldica",
                    "Saber de Herbalismo",
                    "Saber de Jogos",
                    "Saber de Leis",
                    "Saber de Mercadores",
                    "Saber de Mineração",
                    "Saber de Moagem",
                    "Saber de Navegação",
                    "Saber de Obstetrícia",
                    "Saber de Pesca",
                    "Saber de Submundo",
                    "Saber de Teatro",
                    "Saber de Trabalho",
                    "Saber de Vidência",
                ],
                "categorias_parametrizadas": [
                    {
                        "padrao": "Saber sobre um assentamento específico",
                        "exemplos": ["Saber de Absalom", "Saber de Magnimar"],
                    },
                    {
                        "padrao": "Saber de um tipo de comida ou bebida",
                        "exemplos": ["Saber de Açougue", "Saber de Álcool", "Saber de Bolos", "Saber de Chás", "Saber de Culinária"],
                    },
                    {
                        "padrao": "Saber sobre uma criatura específica ou categoria estrita de criaturas",
                        "exemplos": ["Saber de Demônios", "Saber de Urso-Corujas", "Saber de Vampiros"],
                    },
                    {
                        "padrao": "Saber sobre uma divindade específica",
                        "exemplos": ["Saber de Abadar", "Saber de Iomeade"],
                    },
                    {
                        "padrao": "Saber de um plano específico (que não o Plano Material, ou sobre o plano da campanha)",
                        "exemplos": ["Saber do Abismo", "Saber do Paraíso", "Saber do Plano Astral"],
                    },
                    {
                        "padrao": "Saber sobre um terreno específico",
                        "exemplos": ["Saber de Montanhas", "Saber de Rios"],
                    },
                ],
            },
            acoes_destreinadas=[
                construir_acao(
                    "Recordar Conhecimento",
                    proficiencia_minima="destreinado",
                    acao_geral=True,
                    custo_acoes="1 ação",
                    tracos=["concentração", "secreto"],
                    descricao="Sobre o assunto da subcategoria de sua perícia de Saber.",
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Ganhar Proventos",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["recesso"],
                    descricao="Utilizando seu conhecimento para exercer uma profissão (página 237–238).",
                ),
            ],
        ),
        construir_pericia(
            "Sobrevivência",
            "Sabedoria",
            "252-253",
            "Você é apto a viver nos ermos, forragear comida e montar abrigos, e com treinamento pode descobrir os segredos de rastrear e esconder sua trilha.",
            acoes_destreinadas=[
                construir_acao(
                    "Subsistir",
                    proficiencia_minima="destreinado",
                    acao_geral=True,
                    tracos=["recesso"],
                    descricao="Nos ermos ao forragear comida e montar abrigo (página 240).",
                ),
                construir_acao(
                    "Intuir Direção",
                    proficiencia_minima="destreinado",
                    custo_acoes=None,
                    tracos=["exploração", "secreto"],
                    descricao=(
                        "Usando estrelas, posição do sol, geografia, flora ou fauna, você se orienta nos "
                        "ermos (normalmente 1 vez por dia, cerca de 1 minuto). Sem uma bússola, sofre –2 "
                        "de penalidade de item em testes de Intuir Direção."
                    ),
                    resultados={
                        "sucesso_critico": "Você obtém uma noção excelente de sua localização. Em ambiente com direções cardinais, aponta-as com exatidão.",
                        "sucesso": "Você obtém orientação suficiente para evitar ficar completamente perdido e tem noção das direções cardinais.",
                    },
                    exemplos_tarefas={
                        "destreinado": "determinar uma direção cardinal usando o sol",
                        "treinado": "encontrar um caminho coberto por vegetação em uma floresta",
                        "especialista": "orientar-se em um labirinto de jardim",
                        "mestre": "orientar-se em um labirinto bizantino ou deserto relativamente sem características",
                        "lendario": "orientar-se em um reino dos sonhos em constante mudança",
                    },
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Cobrir Rastros",
                    proficiencia_minima="treinado",
                    custo_acoes=None,
                    tracos=["concentração", "exploração", "movimento"],
                    descricao=(
                        "Você cobre seus rastros movendo-se até metade de sua Velocidade de viagem (p. 479), "
                        "sem precisar de teste. Qualquer perseguidor deve obter sucesso em Sobrevivência "
                        "contra sua CD de Sobrevivência se maior que a CD normal para Rastrear. Em encontros, "
                        "pode ser usada como 1 ação (sem o traço exploração)."
                    ),
                    resultados={
                        "sucesso": "Perseguidores precisam superar sua CD de Sobrevivência (se maior que a CD normal da trilha).",
                    },
                ),
                construir_acao(
                    "Rastrear",
                    proficiencia_minima="treinado",
                    custo_acoes=None,
                    tracos=["concentração", "exploração", "movimento"],
                    descricao=(
                        "Você segue rastros movendo-se até metade de sua Velocidade de viagem (p. 479). Faz "
                        "teste ao começar, a cada hora seguinte e quando algo mudar a trilha significativamente. "
                        "Em encontros, pode ser usada como 1 ação (sem o traço exploração)."
                    ),
                    resultados={
                        "sucesso": "Você encontra a trilha ou continua a seguir uma que já esteja seguindo.",
                        "falha": "Você perde a trilha, mas pode tentar novamente após 1 hora.",
                        "falha_critica": "Você perde a trilha e não pode tentar novamente por 24 horas.",
                    },
                    exemplos_tarefas={
                        "destreinado": "o caminho de um grande exército seguindo uma estrada",
                        "treinado": "rastros relativamente recentes de um urso furioso atravessando planícies",
                        "especialista": "os rastros de uma pantera ligeira através de uma selva, rastros após uma chuva",
                        "mestre": "rastros após neve de inverno, rastros de um camundongo ou criatura menor, rastros em rocha nua",
                        "lendario": "rastros antigos pelas areias de um deserto ventoso, rastros após grande nevasca ou furacão",
                    },
                ),
            ],
        ),
        construir_pericia(
            "Sociedade",
            "Inteligência",
            "253",
            "Você compreende os povos e sistemas que estruturam a civilização, além de conhecer eventos históricos e navegar complexidades físicas, societárias e econômicas de assentamentos.",
            acoes_destreinadas=[
                construir_acao(
                    "Recordar Conhecimento",
                    proficiencia_minima="destreinado",
                    acao_geral=True,
                    custo_acoes="1 ação",
                    tracos=["concentração", "secreto"],
                    descricao="Sobre história local, personalidades principais, instituições legais, estrutura societária e culturas humanoides (ou outras criaturas centrais na sociedade local).",
                ),
                construir_acao(
                    "Subsistir",
                    proficiencia_minima="destreinado",
                    acao_geral=True,
                    tracos=["recesso"],
                    descricao="Em um assentamento encontrando abrigo e surrupiando ou pedindo comida (página 240).",
                ),
            ],
            acoes_treinadas=[
                construir_acao(
                    "Decifrar Escrita",
                    proficiencia_minima="treinado",
                    acao_geral=True,
                    tracos=["concentração", "exploração", "secreto"],
                    descricao="Mensagem codificada, texto escrito em forma arcaica/incompleta ou em idioma desconhecido (página 236).",
                ),
                construir_acao(
                    "Criar Falsificação",
                    proficiencia_minima="treinado",
                    custo_acoes=None,
                    tracos=["recesso", "secreto"],
                    requerimentos="Material de escrita apropriado (e exemplo de caligrafia se falsificar caligrafia específica).",
                    cd_alvo="CD 20 inicial; se < 20, compara com CD de Percepção ou Sociedade de observadores; exame minucioso usa Percepção/Sociedade vs sua CD de Sociedade",
                    descricao=(
                        "Cria um documento falsificado ao longo de um dia ou semana. Em teste secreto CD 20, "
                        "observadores passivos não percebem se obtiver >= 20. Caligrafia não específica a "
                        "uma pessoa concede até +4 de bônus de circunstância no teste e na CD se já tiver "
                        "visto documento similar."
                    ),
                    resultados={
                        "sucesso": "O observador não detecta a falsificação.",
                        "falha": "O observador descobre que seu documento é uma falsificação.",
                    },
                ),
            ],
        ),
    ]


def montar_dados_pericias() -> dict[str, Any]:
    """Monta o dicionário completo de dados/pericias.json."""
    return {
        "meta": {
            "titulo": "Capítulo 4: Perícias — Pathfinder 2E Livro Básico",
            "arquivo_origem": "ref/Skill sfots.pdf",
            "paginas_livro_basico": "233-253",
            "versao": "1.0.0",
            "observacoes": (
                "Conversão completa do Capítulo 4: Perícias, incluindo regras gerais de testes, "
                "proficiências, CDs simples, penalidades de armadura, Tabelas 4–1 a 4–4, ações gerais "
                "de perícia e todas as 17 perícias com suas ações destreinadas, treinadas e subcategorias de Saber."
            ),
        },
        "regras_gerais_pericias": construir_regras_gerais(),
        "tabelas": construir_tabelas(),
        "acoes_gerais_pericia": construir_acoes_gerais_pericia(),
        "pericias": construir_pericias(),
    }


def validar_pericias_json(dados: dict[str, Any]) -> None:
    """Valida contagens oficiais, distribuições por atributo e consistência interna."""
    pericias = dados["pericias"]
    assert len(pericias) == 17, f"Esperado 17 perícias, encontrado {len(pericias)}"

    ids_pericias = [p["id"] for p in pericias]
    assert len(set(ids_pericias)) == 17, "IDs duplicados entre perícias"

    esperado_por_atributo = {
        "Força": {"Atletismo"},
        "Destreza": {"Acrobatismo", "Furtividade", "Ladroagem"},
        "Inteligência": {"Arcanismo", "Manufatura", "Ocultismo", "Saber", "Sociedade"},
        "Sabedoria": {"Medicina", "Natureza", "Religião", "Sobrevivência"},
        "Carisma": {"Diplomacia", "Dissimulação", "Intimidação", "Performance"},
    }
    observado_por_atributo: dict[str, set[str]] = {k: set() for k in esperado_por_atributo}
    for p in pericias:
        observado_por_atributo[p["atributo_chave"]].add(p["nome"])
    assert observado_por_atributo == esperado_por_atributo, (
        f"Distribuição por atributo divergente: {observado_por_atributo}"
    )

    acoes_gerais = dados["acoes_gerais_pericia"]
    assert len(acoes_gerais) == 6, f"Esperado 6 ações gerais de perícia, encontrado {len(acoes_gerais)}"
    assert len({a["id"] for a in acoes_gerais}) == 6, "IDs duplicados em ações gerais"

    tabelas = dados["tabelas"]
    t41 = tabelas["tabela_4_1_pericias_atributos_acoes"]
    t42 = tabelas["tabela_4_2_aprender_uma_magia"]
    t43 = tabelas["tabela_4_3_proventos_ganhos"]
    t44 = tabelas["tabela_4_4_distancia_escalar_e_nadar"]
    assert len(t41) == 17, f"Esperado 17 linhas na Tabela 4-1, encontrado {len(t41)}"
    assert len(t42) == 10, f"Esperado 10 linhas na Tabela 4-2, encontrado {len(t42)}"
    assert len(t43) == 22, f"Esperado 22 linhas na Tabela 4-3, encontrado {len(t43)}"
    assert len(t44) == 4, f"Esperado 4 linhas na Tabela 4-4, encontrado {len(t44)}"

    mapa_t41 = {linha["pericia"]: linha for linha in t41}
    for p in pericias:
        linha = mapa_t41[p["nome"]]
        assert linha["atributo_chave"] == p["atributo_chave"]
        nomes_t41_d = {a["nome"] for a in linha["acoes_destreinadas"]}
        nomes_p_d = {a["nome"] for a in p["acoes_destreinadas"]}
        assert nomes_t41_d == nomes_p_d, f"Divergência em ações destreinadas de {p['nome']}: {nomes_t41_d} vs {nomes_p_d}"
        nomes_t41_t = {a["nome"] for a in linha["acoes_treinadas"]}
        nomes_p_t = {a["nome"] for a in p["acoes_treinadas"]}
        assert nomes_t41_t == nomes_p_t, f"Divergência em ações treinadas de {p['nome']}: {nomes_t41_t} vs {nomes_p_t}"

    saber = next(p for p in pericias if p["id"] == "saber")
    subcategorias_saber = saber["quadros_e_regras_especiais"]["subcategorias_comuns_nomeadas"]
    categorias_param = saber["quadros_e_regras_especiais"]["categorias_parametrizadas"]
    assert len(subcategorias_saber) == 31, f"Esperado 31 subcategorias nomeadas de Saber, encontrado {len(subcategorias_saber)}"
    assert len(categorias_param) == 6, f"Esperado 6 categorias parametrizadas de Saber, encontrado {len(categorias_param)}"

    cds = dados["regras_gerais_pericias"]["testes_e_cds"]["cds_simples"]
    assert [c["cd"] for c in cds] == [10, 15, 20, 30, 40], "CDs simples divergentes"


def main() -> None:
    """Gera dados/pericias.json, valida e imprime resumo estatístico."""
    dados = montar_dados_pericias()
    validar_pericias_json(dados)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    conteudo = json.dumps(dados, ensure_ascii=False, indent=2)
    CAMINHO_SAIDA.write_text(conteudo + "\n", encoding="utf-8")

    total_acoes_destreinadas = sum(len(p["acoes_destreinadas"]) for p in dados["pericias"])
    total_acoes_treinadas = sum(len(p["acoes_treinadas"]) for p in dados["pericias"])
    saber = next(p for p in dados["pericias"] if p["id"] == "saber")

    print(f"Arquivo gerado com sucesso: {CAMINHO_SAIDA}")
    print(f"- Perícias: {len(dados['pericias'])}")
    print(f"- Ações gerais de perícia: {len(dados['acoes_gerais_pericia'])}")
    print(f"- Entradas de ações destreinadas nas perícias: {total_acoes_destreinadas}")
    print(f"- Entradas de ações treinadas nas perícias: {total_acoes_treinadas}")
    print(f"- Subcategorias nomeadas de Saber: {len(saber['quadros_e_regras_especiais']['subcategorias_comuns_nomeadas'])} (+ {len(saber['quadros_e_regras_especiais']['categorias_parametrizadas'])} categorias parametrizadas)")
    print(f"- Tabela 4-1: {len(dados['tabelas']['tabela_4_1_pericias_atributos_acoes'])} linhas")
    print(f"- Tabela 4-2: {len(dados['tabelas']['tabela_4_2_aprender_uma_magia'])} linhas")
    print(f"- Tabela 4-3: {len(dados['tabelas']['tabela_4_3_proventos_ganhos'])} linhas")
    print(f"- Tabela 4-4: {len(dados['tabelas']['tabela_4_4_distancia_escalar_e_nadar'])} linhas")
    print(f"- Tamanho do arquivo: {CAMINHO_SAIDA.stat().st_size} bytes")


if __name__ == "__main__":
    main()
