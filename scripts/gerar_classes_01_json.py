"""Gerador e validador de dados/classes01.json (Leva 01) a partir de ref/Classes 01.pdf."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "classes01.json"


def slugify(texto: str) -> str:
    """Converte um nome em identificador snake_case ASCII."""
    normalizado = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(c for c in normalizado if not unicodedata.combining(c))
    return re.sub(r"[^a-zA-Z0-9]+", "_", sem_acentos.lower()).strip("_")


def construir_tabela_progressao(linhas: list[tuple[int, str]]) -> list[dict[str, Any]]:
    """Converte linhas (nivel, texto_caracteristicas) em lista normalizada de 20 níveis."""
    resultado: list[dict[str, Any]] = []
    for nivel, texto in linhas:
        caracteristicas = [item.strip() for item in texto.split(",") if item.strip()]
        resultado.append(
            {
                "nivel": nivel,
                "caracteristicas": caracteristicas,
                "texto_original": texto,
            }
        )
    return resultado


def construir_caracteristica_classe(
    nome: str,
    nivel: int,
    descricao: str,
    *,
    acoes_concedidas: list[dict[str, Any]] | None = None,
    detalhes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Cria uma entrada normalizada de característica de classe."""
    entrada: dict[str, Any] = {
        "id": slugify(nome),
        "nome": nome,
        "nivel": nivel,
        "descricao": descricao,
    }
    if acoes_concedidas:
        entrada["acoes_concedidas"] = acoes_concedidas
    if detalhes:
        entrada["detalhes"] = detalhes
    return entrada


def construir_acao_habilidade(
    nome: str,
    acoes: str,
    tracos: list[str],
    descricao: str,
    *,
    frequencia: str | None = None,
    acionamento: str | None = None,
    requerimentos: str | None = None,
    custo: str | None = None,
    resultados: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Cria uma entrada normalizada de ação ou reação concedida por classe/subclasse."""
    entrada: dict[str, Any] = {
        "id": slugify(nome),
        "nome": nome,
        "acoes": acoes,
        "tracos": tracos,
    }
    if frequencia is not None:
        entrada["frequencia"] = frequencia
    if acionamento is not None:
        entrada["acionamento"] = acionamento
    if requerimentos is not None:
        entrada["requerimentos"] = requerimentos
    if custo is not None:
        entrada["custo"] = custo
    entrada["descricao"] = descricao
    if resultados is not None:
        entrada["resultados"] = resultados
    return entrada


def construir_talento_classe(
    nome: str,
    nivel: int,
    tracos: list[str],
    descricao: str,
    *,
    acoes: str | None = None,
    pre_requisitos: str | None = None,
    frequencia: str | None = None,
    acionamento: str | None = None,
    requerimentos: str | None = None,
    custo: str | None = None,
    especial: str | None = None,
    resultados: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Cria uma entrada normalizada de talento de classe."""
    return {
        "id": slugify(nome),
        "nome": nome,
        "nivel": nivel,
        "tracos": tracos,
        "acoes": acoes,
        "pre_requisitos": pre_requisitos,
        "frequencia": frequencia,
        "acionamento": acionamento,
        "requerimentos": requerimentos,
        "custo": custo,
        "especial": especial,
        "resultados": resultados,
        "descricao": descricao,
    }


def construir_regras_gerais_classes() -> dict[str, Any]:
    """Retorna as regras introdutórias do Capítulo 3 (pp. 67–68)."""
    return {
        "paginas": "67-68",
        "descricao": (
            "Sua classe indica o treinamento que possui e que será aprimorado durante suas aventuras, "
            "fornecendo melhoria de atributo chave, Pontos de Vida por nível, proficiências iniciais, "
            "tabela de progressão, características de classe, opções de subclasse e talentos de classe."
        ),
        "referencias_capitulo": [
            {
                "titulo": "Subindo de Nível",
                "pagina": 31,
                "resumo": "Como evoluir o personagem ao acumular Pontos de Experiência para alcançar novos níveis.",
            },
            {
                "titulo": "Companheiros Animais e Familiares",
                "pagina": 214,
                "resumo": "Regras para companheiros animais ou familiares obtidos por característica de classe ou talento.",
            },
            {
                "titulo": "Arquétipos",
                "pagina": 219,
                "resumo": "Opções temáticas (incluindo arquétipos multiclasse) acessíveis a partir do 2º nível.",
            },
        ],
        "elementos_secao_classe": {
            "jogando_com_a_classe": (
                "Descreve interesses, propensões típicas de membros da classe, visão de outros personagens "
                "e sugestões para combate, encontros sociais, exploração e recesso (não obrigatórias)."
            ),
            "atributo_chave": {
                "descricao": (
                    "Atributo mais importante para a classe, usado para determinar a CD de classe e, "
                    "para conjuradores, CDs e rolagens de ataque de magias. Algumas classes permitem escolher entre duas opções."
                ),
                "melhoria_1_nivel": 2,
                "regra": "No 1º nível, sua classe concede uma melhoria de atributo (+2) em seu atributo chave.",
            },
            "pontos_de_vida": {
                "formula_inicial": "PV_ancestralidade + PV_classe + modificador_constituicao",
                "formula_por_nivel": "PV_classe + modificador_constituicao",
                "descricao": (
                    "Cada classe concede uma quantidade fixa de Pontos de Vida no 1º nível e a cada nível subsequente, "
                    "somada ao modificador de Constituição."
                ),
            },
            "proficiencias_iniciais": {
                "categorias": [
                    "Percepção",
                    "Jogadas de Salvamento",
                    "Perícias",
                    "Ataques",
                    "Defesas",
                    "Magias ou CD de Classe",
                ],
                "regra_redundancia_treinado": (
                    "Se sua classe o tornaria treinado em uma perícia na qual já é treinado "
                    "(tipicamente devido à sua biografia), você se torna treinado em outra perícia à sua escolha."
                ),
                "estatistica_nao_listada": "Destreinado (+0 de bônus de proficiência), salvo treinamento de outra fonte.",
                "bonus_por_graduacao": {
                    "destreinado": {"formula": "+0"},
                    "treinado": {"formula": "nivel + 2"},
                    "especialista": {"formula": "nivel + 4"},
                    "mestre": {"formula": "nivel + 6"},
                    "lendario": {"formula": "nivel + 8"},
                },
            },
            "tabela_de_progressao": (
                "Resume talentos, incrementos de perícia, melhorias de atributo e características recebidas "
                "do 1º ao 20º nível, incluindo no 1º nível lembrete para ancestralidade e biografia."
            ),
        },
        "caracteristicas_padrao_todas_as_classes": {
            "regra_retreino": (
                "Decisões de características de classe geralmente só podem ser alteradas através de retreino (página 481), "
                "a menos que a habilidade diga o contrário."
            ),
            "talentos_de_classe": (
                "Concedidos a partir do 1º ou 2º nível (dependendo da classe) e em níveis pares subsequentes."
            ),
            "talentos_de_pericia": (
                "A maioria das classes recebe no 2º nível e a cada 2 níveis subsequentes (ladinos recebem antes e com maior frequência). "
                "Exige graduação treinado ou melhor na perícia correspondente."
            ),
            "talentos_gerais": (
                "A maioria das classes concede no 3º nível e a cada 4 níveis subsequentes (3º, 7º, 11º, 15º, 19º). "
                "Permite escolher qualquer talento geral (incluindo talentos de perícia) atendendo aos requisitos."
            ),
            "incrementos_de_pericia": {
                "padrao": "3º nível e a cada 2 níveis subsequentes (ladinos recebem antes e com maior frequência).",
                "efeito": "Torna treinado em perícia destreinada ou especialista em perícia treinada.",
                "desbloqueio_mestre": 7,
                "desbloqueio_lendario": 15,
            },
            "melhorias_de_atributo": {
                "niveis": [5, 10, 15, 20],
                "quantidade_atributos": 4,
                "regra_incremento": "+1 se valor >= 18; +2 se valor < 18.",
            },
            "talentos_de_ancestralidade": {
                "niveis_progressao": [5, 9, 13, 17],
                "nota": "Além do talento recebido na criação de personagem (1º nível).",
            },
        },
    }


def construir_visao_geral_classes() -> list[dict[str, Any]]:
    """Retorna a lista oficial das 12 classes do Livro Básico (p. 69)."""
    itens = [
        (
            "Alquimista",
            70,
            "O alquimista utiliza sua competência em manufatura para criar itens alquímicos — como bombas, elixires e venenos — usados para derrotar adversários e ajudar aliados. Esperto e engenhoso, um alquimista geralmente tem a ferramenta certa para o trabalho e o conhecimento esotérico específico para tirar seus aliados de qualquer enrascada.",
        ),
        (
            "Bárbaro",
            82,
            "O bárbaro é a temível encarnação da fúria, canalizando o poder mortal de sua raiva contra qualquer um que ficar em seu caminho. Um bárbaro entra em combate rapidamente, e se torna imensamente forte, imprevisível e implacável ao libertar o seu furor de batalha.",
        ),
        (
            "Bardo",
            94,
            "Tanto artista quanto estudioso, o bardo utiliza performances e aprendizado esotérico para fortalecer seus companheiros e frustrar seus inimigos. Às vezes furtivo e frequentemente cativante, o bardo se aventura com vitalidade, glamour e talento apoiado em um repertório impressionante de magia ocultista.",
        ),
        (
            "Campeão",
            104,
            "Um defensor do bem vestindo uma armadura e empunhando uma arma virtuosa, o campeão protege os inocentes e reprime o mal. Resoluto em suas crenças e devotado a uma divindade e a um aspecto do bem, ele segue um rigoroso código enquanto luta para tornar o mundo um lugar melhor.",
        ),
        (
            "Clérigo",
            116,
            "O clérigo é dedicado à adoração de uma única divindade, acessando a magia divina através desta devoção. Clérigos podem ser muito diferentes dependendo da divindade que adoram, sejam eles sacerdotes enclausurados que seguem um dos domínios de sua divindade ou capelães de guerra que servem como a arma de seu deus.",
        ),
        (
            "Druida",
            128,
            "O druida caminha nos locais primordiais e selvagens do mundo sem medo, colhendo a magia primal da natureza e controlando-a com propósito. Dedicado às regiões selvagens, o druida encontra nelas sustento e poder, aliados entre suas criaturas e força em seu furor.",
        ),
        (
            "Feiticeiro",
            140,
            "A magia intensa que o feiticeiro comanda não advém de estudo ou adoração — e sim de seu sangue. Suas habilidades mágicas e poderes dependem da origem do sangue que flui em suas veias, que pode vir de dragões, anjos, fadas, criaturas aberrantes ou outros seres impressionantes.",
        ),
        (
            "Guerreiro",
            152,
            "Com audácia calculada e determinação destemida, o guerreiro persegue e confronta seus inimigos enquanto defende aliados do perigo. Mestre do campo de batalha, o guerreiro é rápido em explorar oportunidades e golpear qualquer um que vacile ao alcance de sua espada ou arco.",
        ),
        (
            "Ladino",
            166,
            "Astuto e ágil, o ladino traz perícias e especialidades que poucos companheiros podem igualar. Em batalha, ele se destaca em ataques furtivos e emboscadas. Seu esquema lhe dá as ferramentas necessárias para completar qualquer trabalho e sua ampla gama de perícias permite que se especialize no que bem desejar.",
        ),
        (
            "Mago",
            178,
            "O mago é o mestre arcano da conjuração de magias, que extrai seu poder incrível do tecido da realidade através de fórmulas mágicas complicadas. Ele caminha com confiança, sem precisar de armaduras ou armas, promulgando sua vontade sobre o mundo e trazendo desgraça a seus inimigos.",
        ),
        (
            "Monge",
            190,
            "O monge busca a perfeição em tudo que faz, incluindo transformar seu corpo em uma arma perfeita. Ele pode caminhar com calma e propósito, contemplando as sutilezas da existência em um minuto e então se transformar em um borrão de golpes mortais no outro.",
        ),
        (
            "Patrulheiro",
            202,
            "Engenhoso e astuto, o patrulheiro é um caçador, rastreador e combatente que preserva o mundo natural e protege a civilização de seus excessos. Seja usando um arco, besta, um par de armas ou arapucas, o patrulheiro é um inimigo temível e um grande aliado nos ermos.",
        ),
    ]
    return [
        {
            "id": slugify(nome),
            "nome": nome,
            "pagina_inicial": pagina,
            "resumo": resumo,
        }
        for nome, pagina, resumo in itens
    ]


def construir_alquimista() -> dict[str, Any]:
    """Constrói os dados completos da classe Alquimista (pp. 70–81)."""
    tabela_progressao = construir_tabela_progressao(
        [
            (1, "Alquimia, ancestralidade e biografia, campo de pesquisa, livro de fórmulas, proficiências iniciais, talento de alquimista"),
            (2, "Talento de alquimista, talento de perícia"),
            (3, "Incremento de perícia, talento geral"),
            (4, "Talento de alquimista, talento de perícia"),
            (5, "Descoberta de campo de pesquisa, incremento de perícia, melhorias de atributo, talento de ancestralidade"),
            (6, "Talento de alquimista, talento de perícia"),
            (7, "Especialidade em armas alquímicas, incremento de perícia, infusões perpétuas, talento geral, vontade de ferro"),
            (8, "Talento de alquimista, talento de perícia"),
            (9, "Especialidade alquímica, incremento de perícia, produção dupla, prontidão, talento de ancestralidade"),
            (10, "Melhorias de atributo, talento de alquimista, talento de perícia"),
            (11, "Incremento de perícia, irrefreável, potência perpétua, talento geral"),
            (12, "Talento de alquimista, talento de perícia"),
            (13, "Descoberta de campo de pesquisa maior, especialidade em armaduras leves, especialização em armas, incremento de perícia, talento de ancestralidade"),
            (14, "Talento de alquimista, talento de perícia"),
            (15, "Entusiasmo alquímico, evasão, incremento de perícia, melhorias de atributo, talento geral"),
            (16, "Talento de alquimista, talento de perícia"),
            (17, "Incremento de perícia, maestria alquímica, perfeição perpétua, talento de ancestralidade"),
            (18, "Talento de alquimista, talento de perícia"),
            (19, "Incremento de perícia, maestria em armaduras leves, talento geral"),
            (20, "Melhorias de atributo, talento de alquimista, talento de perícia"),
        ]
    )

    tabela_talentos_indice = [
        {"nome": "Alquimia Duradoura", "nivel": 4},
        {"nome": "Alquimia Eficiente", "nivel": 4},
        {"nome": "Alquimia Poderosa", "nivel": 8},
        {"nome": "Alquímico Sagaz", "nivel": 1},
        {"nome": "Bomba de Fumaça", "nivel": 2},
        {"nome": "Bomba Debilitante", "nivel": 6},
        {"nome": "Bomba Debilitante Maior", "nivel": 10},
        {"nome": "Bomba Debilitante Verdadeira", "nivel": 14},
        {"nome": "Bomba Grudenta", "nivel": 8},
        {"nome": "Bomba Lancinante", "nivel": 16},
        {"nome": "Bombardeiro Rápido", "nivel": 1},
        {"nome": "Bombas Direcionais", "nivel": 6},
        {"nome": "Bombas Excepcionais", "nivel": 12},
        {"nome": "Combinar Elixires", "nivel": 6},
        {"nome": "Criar Pedra Filosofal", "nivel": 20},
        {"nome": "Debilitação Perfeita", "nivel": 18},
        {"nome": "Elixir Eterno", "nivel": 16},
        {"nome": "Elixir Misericordioso", "nivel": 10},
        {"nome": "Elixir Misericordioso Maior", "nivel": 14},
        {"nome": "Elixires Improváveis", "nivel": 18},
        {"nome": "Envenenador Potente", "nivel": 10},
        {"nome": "Familiar Alquímico", "nivel": 1},
        {"nome": "Lançador Longínquo", "nivel": 1},
        {"nome": "Mega Bomba", "nivel": 20},
        {"nome": "Mutagênico de Mente Limpa", "nivel": 18},
        {"nome": "Mutagênico Elástico", "nivel": 10},
        {"nome": "Mutagênico Feral", "nivel": 8},
        {"nome": "Mutagênico Genial", "nivel": 16},
        {"nome": "Mutagênico Invencível", "nivel": 12},
        {"nome": "Mutagênico Loquaz", "nivel": 14},
        {"nome": "Mutagênico Perfeito", "nivel": 20},
        {"nome": "Mutagênico Persistente", "nivel": 16},
        {"nome": "Mutagênico Revivificante", "nivel": 2},
        {"nome": "Prolongar Elixir", "nivel": 12},
        {"nome": "Resistência a Veneno", "nivel": 2},
        {"nome": "Respingo Calculado", "nivel": 4},
        {"nome": "Respingo Expandido", "nivel": 10},
        {"nome": "Trabalhador Milagroso", "nivel": 18},
    ]

    caracteristicas_de_classe = [
        construir_caracteristica_classe(
            "Ancestralidade e Biografia",
            1,
            "Além das habilidades fornecidas por sua classe no 1º nível, você possui os benefícios da ancestralidade e biografia selecionadas, conforme descrito no Capítulo 2.",
        ),
        construir_caracteristica_classe(
            "Proficiências Iniciais",
            1,
            "No 1º nível, você recebe proficiências que representam seu treinamento básico, listadas no início desta classe.",
        ),
        construir_caracteristica_classe(
            "Alquimia",
            1,
            (
                "Você compreende as interações complexas de substâncias naturais e sobrenaturais e pode produzir itens alquímicos "
                "que atendam às suas necessidades, usando reagentes normais e Manufaturar ou reagentes infundidos especiais sem custo. "
                "Você recebe o talento Manufatura Alquímica (página 264), mesmo se não atender aos seus pré-requisitos, e recebe as quatro "
                "fórmulas alquímicas comuns de 1º nível concedidas pelo talento (catálogo a partir da página 543). "
                "Durante suas preparações diárias, você ganha uma quantidade de lotes de reagentes infundidos igual ao seu nível + seu modificador de Inteligência "
                "(juntos possuem Volume leve; reagentes do dia anterior são destruídos na próxima preparação diária e efeitos não-permanentes encerram-se). "
                "Com Alquimia Avançada (nível igual ao seu nível), cada lote gasto cria um lote de dois itens iguais do seu livro de fórmulas com o traço infundido por 24 horas ou até a próxima preparação diária. "
                "Você também pode usar a ação Alquimia Rápida."
            ),
            acoes_concedidas=[
                construir_acao_habilidade(
                    "Alquimia Rápida",
                    "1",
                    ["alquimista"],
                    (
                        "Você rapidamente mistura um item alquímico de curta duração para usar no momento. "
                        "Você cria um único item alquímico do seu nível de alquimia avançada ou inferior que conste em seu livro de fórmulas "
                        "sem precisar gastar o custo monetário normal em reagentes alquímicos ou realizar um teste de Manufatura. "
                        "Este item possui o traço infundido, mas permanece potente somente até o início de seu próximo turno."
                    ),
                    custo="1 lote de reagentes infundidos",
                    requerimentos="Você possui ferramentas de alquimista (página 290), a fórmula para o item alquímico sendo criado e uma mão livre.",
                )
            ],
            detalhes={
                "talento_bonus": "Manufatura Alquímica",
                "formulas_talento_bonus": 4,
                "lotes_reagentes_formula": "nivel + modificador_inteligencia",
                "alquimia_avancada_itens_por_lote": 2,
            },
        ),
        construir_caracteristica_classe(
            "Livro de Fórmulas",
            1,
            (
                "Você recebe gratuitamente um livro de fórmulas padrão no valor de 10 pp ou menos (página 291). "
                "O livro contém as fórmulas para dois itens alquímicos comuns de 1º nível à sua escolha, além das fórmulas recebidas pelo talento Manufatura Alquímica "
                "e pelo seu campo de pesquisa. Cada vez que ganhar um nível, você adiciona as fórmulas de dois itens alquímicos comuns de qualquer nível de item que seja capaz de criar."
            ),
            detalhes={"formulas_iniciais_livres": 2, "formulas_por_nivel": 2},
        ),
        construir_caracteristica_classe(
            "Campo de Pesquisa",
            1,
            "Seus questionamentos sobre a natureza alquímica do universo o levaram a focar em um campo de pesquisa em particular: Bombardeiro, Cirurgião ou Mutagenista.",
        ),
        construir_caracteristica_classe(
            "Talentos de Alquimista",
            1,
            "No 1º nível e a cada nível par subsequente, você recebe um talento de classe de alquimista.",
        ),
        construir_caracteristica_classe(
            "Talentos de Perícia",
            2,
            "No 2º nível e a cada 2 níveis subsequentes, você recebe um talento de perícia (Capítulo 5). Você deve possuir graduação treinado ou melhor na perícia correspondente.",
        ),
        construir_caracteristica_classe(
            "Incrementos de Perícia",
            3,
            "No 3º nível e a cada 2 níveis subsequentes, você recebe um incremento de perícia (treinado ou especialista; mestre a partir do 7º nível; lendário a partir do 15º nível).",
        ),
        construir_caracteristica_classe(
            "Talentos Gerais",
            3,
            "No 3º nível e a cada 4 níveis subsequentes, você recebe um talento geral (Capítulo 5).",
        ),
        construir_caracteristica_classe(
            "Descoberta de Campo de Pesquisa",
            5,
            (
                "Você desenvolve uma descoberta especial dependendo de seu campo de pesquisa: "
                "Bombardeiro cria três bombas quaisquer por lote com alquimia avançada; "
                "Cirurgião cria três elixires de vida por lote; "
                "Mutagenista cria três mutagênicos quaisquer por lote."
            ),
        ),
        construir_caracteristica_classe(
            "Melhorias de Atributo",
            5,
            "No 5º nível e a cada 5 níveis subsequentes, você melhora os valores de quatro atributos diferentes (+1 se já for 18 ou maior, +2 se menor que 18).",
        ),
        construir_caracteristica_classe(
            "Talentos de Ancestralidade",
            5,
            "Você recebe um talento de ancestralidade no 5º nível e a cada 4 níveis subsequentes.",
        ),
        construir_caracteristica_classe(
            "Especialidade em Armas Alquímicas",
            7,
            "Suas graduações de proficiência em armas simples, ataques desarmados e bombas alquímicas aumentam para especialista.",
        ),
        construir_caracteristica_classe(
            "Infusões Perpétuas",
            7,
            (
                "Você adquire a habilidade de criar dois itens alquímicos de 1º nível usando Alquimia Rápida sem gastar um lote de reagentes infundidos. "
                "Os itens devem ser apropriados ao seu campo de pesquisa e constar em seu livro de fórmulas."
            ),
        ),
        construir_caracteristica_classe(
            "Vontade de Ferro",
            7,
            "Suas defesas mentais são uma verdadeira fortaleza de ferro. Sua graduação de proficiência em salvamentos de Vontade aumenta para especialista.",
        ),
        construir_caracteristica_classe(
            "Especialidade Alquímica",
            9,
            "Sua graduação de proficiência em sua CD de classe de alquimista aumenta para especialista.",
        ),
        construir_caracteristica_classe(
            "Produção Dupla",
            9,
            "Quando usar a ação Alquimia Rápida, você pode gastar até dois lotes de reagentes infundidos para criar até dois itens alquímicos (não precisam ser iguais).",
        ),
        construir_caracteristica_classe(
            "Prontidão",
            9,
            "Você permanece alerta às ameaças ao seu redor. Sua graduação de proficiência em Percepção aumenta para especialista.",
        ),
        construir_caracteristica_classe(
            "Irrefreável",
            11,
            "Sua graduação de proficiência em salvamentos de Fortitude aumenta para mestre. Quando rolar um sucesso em um salvamento de Fortitude, trate o resultado como um sucesso crítico.",
        ),
        construir_caracteristica_classe(
            "Potência Perpétua",
            11,
            "Você aprimora suas infusões perpétuas para versões moderadas das escolhas de seu campo de pesquisa (que devem constar em seu livro de fórmulas).",
        ),
        construir_caracteristica_classe(
            "Descoberta de Campo de Pesquisa Maior",
            13,
            (
                "Você desenvolve uma descoberta incrível de seu campo de pesquisa: "
                "Bombardeiro pode aumentar o respingo para 3 metros (4,5 metros com Respingo Expandido); "
                "Cirurgião faz qualquer elixir de vida criado com Alquimia Rápida curar o máximo de PV possíveis; "
                "Mutagenista pode se beneficiar de dois mutagênicos simultaneamente."
            ),
        ),
        construir_caracteristica_classe(
            "Especialidade em Armaduras Leves",
            13,
            "Suas graduações de proficiência em armaduras leves e defesa sem armadura aumentam para especialista.",
        ),
        construir_caracteristica_classe(
            "Especialização em Armas",
            13,
            "Você causa 2 pontos de dano adicionais com armas e ataques desarmados nos quais é especialista (3 se mestre, 4 se lendário).",
        ),
        construir_caracteristica_classe(
            "Entusiasmo Alquímico",
            15,
            "Quando usar a ação Alquimia Rápida, você pode gastar até três lotes de reagentes infundidos para criar até três itens alquímicos (não precisam ser iguais).",
        ),
        construir_caracteristica_classe(
            "Evasão",
            15,
            "Sua graduação de proficiência em salvamentos de Reflexos aumenta para mestre. Quando rolar um sucesso em um salvamento de Reflexos, trate o resultado como um sucesso crítico.",
        ),
        construir_caracteristica_classe(
            "Maestria Alquímica",
            17,
            "Sua graduação de proficiência em sua CD de classe de alquimista aumenta para mestre.",
        ),
        construir_caracteristica_classe(
            "Perfeição Perpétua",
            17,
            "Você aperfeiçoou suas infusões perpétuas para versões maiores das escolhas de seu campo de pesquisa (que devem constar em seu livro de fórmulas).",
        ),
        construir_caracteristica_classe(
            "Maestria em Armaduras Leves",
            19,
            "Suas graduações de proficiência em armaduras leves e defesa sem armadura aumentam para mestre.",
        ),
    ]

    subclasses = {
        "tipo": "campo_de_pesquisa",
        "nome_tipo": "Campo de Pesquisa",
        "opcoes": [
            {
                "id": "bombardeiro",
                "nome": "Bombardeiro",
                "descricao": "Você se especializa em explosões e outras reações alquímicas violentas.",
                "formulas_iniciais_adicionais": "Duas bombas alquímicas de 1º nível no livro de fórmulas.",
                "beneficio_1_nivel": (
                    "Quando arremessar uma bomba alquímica com o traço respingo, você pode causar o dano de respingo apenas em seu alvo primário em vez da área de respingo usual."
                ),
                "descoberta_5_nivel": (
                    "Quando usar alquimia avançada para criar bombas durante suas preparações diárias, você pode usar um lote de reagentes para criar três bombas quaisquer em vez de apenas duas bombas iguais."
                ),
                "infusoes_perpetuas_7_nivel": [
                    "bolsa emaranhapé menor",
                    "fogo alquímico menor",
                    "frasco de ácido menor",
                    "frasco congelante menor",
                    "pedra-trovão menor",
                    "relâmpago engarrafado menor",
                ],
                "infusoes_perpetuas_regra": "Escolha duas das fórmulas listadas.",
                "potencia_perpetua_11_nivel": "As versões moderadas das bombas escolhidas em infusões perpétuas.",
                "descoberta_maior_13_nivel": (
                    "Você pode aumentar o respingo de suas bombas para causar dano a criaturas a até 3 metros (ou 4,5 metros se possuir Respingo Expandido)."
                ),
                "perfeicao_perpetua_17_nivel": "As versões maiores das bombas escolhidas em infusões perpétuas.",
            },
            {
                "id": "cirurgiao",
                "nome": "Cirurgião",
                "descricao": "Você se concentra em curar os outros com alquimia.",
                "formulas_iniciais_adicionais": "Duas fórmulas adicionais escolhidas entre: antídoto menor, antipeste menor ou elixir da vida mínimo.",
                "beneficio_1_nivel": (
                    "Enquanto sua graduação de proficiência em Medicina for treinado ou melhor, você pode realizar um teste de Manufatura em vez de Medicina para quaisquer usos destreinados e treinados de Medicina."
                ),
                "descoberta_5_nivel": (
                    "Quando usar alquimia avançada para criar elixires de vida durante suas preparações diárias, você pode usar um lote de reagentes para criar três elixires em vez de apenas dois."
                ),
                "infusoes_perpetuas_7_nivel": ["antídoto menor", "antipeste menor"],
                "infusoes_perpetuas_regra": "Recebe ambas as fórmulas listadas.",
                "potencia_perpetua_11_nivel": "Antídoto moderado e antipeste moderado.",
                "descoberta_maior_13_nivel": (
                    "Quando usar Alquimia Rápida para criar qualquer tipo de elixir de vida, a criatura que beber o elixir recebe o máximo de Pontos de Vida possíveis para o elixir em vez de rolar os dados."
                ),
                "perfeicao_perpetua_17_nivel": "Antídoto maior e antipeste maior.",
            },
            {
                "id": "mutagenista",
                "nome": "Mutagenista",
                "descricao": "Você se especializa em transformações mutagênicas bizarras que sacrificam um aspecto físico ou psicológico de uma criatura para fortalecer o outro.",
                "formulas_iniciais_adicionais": "Fórmulas adicionais para dois mutagênicos de 1º nível em seu livro de fórmulas.",
                "beneficio_1_nivel": "Você ganha a ação Retroatividade Mutagênica.",
                "acoes_concedidas": [
                    construir_acao_habilidade(
                        "Retroatividade Mutagênica",
                        "livre",
                        ["alquimista"],
                        (
                            "Você vivencia uma breve ressurgência de um mutagênico. Escolha um mutagênico que você tenha consumido desde suas últimas preparações diárias. "
                            "Você recebe os efeitos desse mutagênico por 1 minuto."
                        ),
                        frequencia="uma vez por dia",
                    )
                ],
                "descoberta_5_nivel": (
                    "Quando usar alquimia avançada para criar mutagênicos durante suas preparações diárias, você pode usar um lote de reagentes para criar três mutagênicos quaisquer em vez de apenas dois mutagênicos iguais."
                ),
                "infusoes_perpetuas_7_nivel": [
                    "mutagênico bestial menor",
                    "mutagênico cognitivo menor",
                    "mutagênico do irrefreável menor",
                    "mutagênico de língua de prata menor",
                    "mutagênico de mercúrio menor",
                    "mutagênico sereno menor",
                ],
                "infusoes_perpetuas_regra": "Escolha duas das fórmulas listadas.",
                "potencia_perpetua_11_nivel": "As versões moderadas dos mutagênicos escolhidos em infusões perpétuas.",
                "descoberta_maior_13_nivel": (
                    "Se ingerir outro mutagênico enquanto estiver sob os efeitos de um mutagênico de sua criação, você pode receber os benefícios e desvantagens de ambos ao mesmo tempo "
                    "(independente do traço polimorfia). Se ficar sob efeito de qualquer outro mutagênico posteriormente enquanto já se beneficia de dois mutagênicos, perde o benefício de um dos prévios à sua escolha — mas retém as desvantagens de todos. "
                    "Se sofrer um efeito de polimorfia não-mutagênico enquanto estiver sob efeito de dois mutagênicos, perde os benefícios de todos os mutagênicos, mas retém as desvantagens de todos."
                ),
                "perfeicao_perpetua_17_nivel": "As versões maiores dos mutagênicos escolhidos em infusões perpétuas.",
            },
        ],
    }

    termos_chave = [
        {
            "termo": "Aditivo",
            "descricao": (
                "Talentos com o traço aditivo lhe permitem gastar ações para acrescentar substâncias especiais a bombas ou elixires. "
                "Você pode acrescentar somente um único aditivo a um determinado item alquímico — tentar acrescentar outro aditivo estraga o item. "
                "Normalmente você só pode usar ações com o traço aditivo quando estiver criando um item alquímico infundido, e algumas só podem ser usadas com a ação Alquimia Rápida. "
                "O traço aditivo é sempre apresentado com um nível, como aditivo 2, que adiciona esse valor ao nível do item modificado; "
                "o nível de item da mistura não pode ser maior que seu nível de alquimia avançada."
            ),
        },
        {
            "termo": "Infundido",
            "descricao": (
                "Você criou um item alquímico com o traço infundido usando seus reagentes infundidos, e ele funciona por um tempo limitado antes de ficar inerte. "
                "Quaisquer efeitos não-permanentes de seus itens alquímicos infundidos, com exceção de aflições como venenos de ação lenta, se encerram quando você fizer suas preparações diárias novamente."
            ),
        },
    ]

    exemplos_personagens = [
        {
            "nome": "Cirurgião",
            "pagina": 74,
            "resumo": "Você utiliza a alquimia para propósitos medicinais, curando e protegendo os outros pelo mundo.",
            "atributos": "Priorize Inteligência e Sabedoria. Constituição aumenta sua capacidade de sobrevivência, e Destreza lhe ajuda a acertar ataques à distância quando a violência é necessária.",
            "pericias": ["Diplomacia", "Manufatura", "Medicina", "Natureza", "Ocultismo", "Religião", "Sociedade", "Sobrevivência"],
            "subclasse": "Cirurgião",
            "talento_inicial": "Alquímico Sagaz",
            "talentos_niveis_superiores": [
                "Resistência a Veneno (2º)",
                "Alquimia Eficiente (4º)",
                "Combinar Elixires (6º)",
                "Elixir Misericordioso (10º)",
                "Elixir Misericordioso Maior (14º)",
                "Trabalhador Milagroso (18º)",
                "Criar Pedra Filosofal (20º)",
            ],
        },
        {
            "nome": "Bombardeiro",
            "pagina": 78,
            "resumo": "Você pode criar um explosivo a partir de quase qualquer coisa!",
            "atributos": "Priorize Inteligência e Destreza. Constituição lhe ajuda a sobreviver às explosões que deram errado, e Sabedoria lhe impede de bombardear o alvo errado.",
            "pericias": ["Acrobatismo", "Arcanismo", "Dissimulação", "Furtividade", "Intimidação", "Ladroagem", "Manufatura", "Sociedade"],
            "subclasse": "Bombardeiro",
            "talento_inicial": "Bombardeiro Rápido",
            "talentos_niveis_superiores": [
                "Bomba de Fumaça (2º)",
                "Respingo Calculado (4º)",
                "Bombas Direcionais (6º)",
                "Bomba Grudenta (8º)",
                "Respingo Expandido (10º)",
                "Mega Bomba (20º)",
            ],
        },
        {
            "nome": "Mutagenista",
            "pagina": 80,
            "resumo": "Você transforma a si próprio e aos outros com mutagênicos.",
            "atributos": "Priorize Inteligência e Força. Constituição lhe ajuda a sobreviver a transformações e ao combate, e Sabedoria lhe ajuda a manter sua mente intacta apesar das mutações.",
            "pericias": ["Atletismo", "Arcanismo", "Furtividade", "Intimidação", "Manufatura", "Ocultismo", "Sociedade", "Sobrevivência"],
            "subclasse": "Mutagenista",
            "talento_inicial": "Familiar Alquímico",
            "talentos_niveis_superiores": [
                "Mutagênico Revivificante (2º)",
                "Mutagênico Feral (8º)",
                "Mutagênico Invencível (12º)",
                "Mutagênico Persistente (16º)",
                "Mutagênico Perfeito (20º)",
            ],
        },
    ]

    talentos = [
        # 1º NÍVEL (4)
        construir_talento_classe(
            "Alquímico Sagaz",
            1,
            ["Alquimista"],
            "Você consegue identificar itens alquímicos rapidamente. Quando usar a perícia Manufatura para Identificar Alquimia em um item alquímico que estiver segurando, você pode fazê-lo como uma ação única que possui os traços concentração e manuseio (em vez de gastar 10 minutos). Se tiver a fórmula do item sendo identificado, você recebe +2 de bônus de circunstância em seu teste, e se rolar uma falha crítica, trate o resultado como uma falha.",
            pre_requisitos="treinado em Manufatura",
        ),
        construir_talento_classe(
            "Bombardeiro Rápido",
            1,
            ["Alquimista"],
            "Você guarda suas bombas em bolsos fáceis de alcançar de onde consegue pegá-las sem pensar. Você Interage para sacar uma bomba e Golpear com ela.",
            acoes="1",
        ),
        construir_talento_classe(
            "Familiar Alquímico",
            1,
            ["Alquimista"],
            "Você consegue criar vida através da alquimia — uma criatura simples formada a partir de materiais alquímicos, reagentes e um pouco de seu próprio sangue. Este familiar alquímico parece ser uma pequena criatura de carne e sangue, embora possa ter algumas características inusitadas ou distintas dependendo de seu processo criativo. Como outros familiares, seu familiar alquímico o ajuda em seu laboratório e em suas aventuras. Você utiliza seu próprio modificador de Inteligência para determinar os modificadores de Percepção, Acrobatismo e Furtividade do familiar (veja Familiares na página 217 para mais informações).",
        ),
        construir_talento_classe(
            "Lançador Longínquo",
            1,
            ["Alquimista"],
            "Você aprendeu a arremessar mais longe. Quando você arremessa uma bomba alquímica, ela possui um incremento de distância de 9 metros em vez dos 6 metros usuais.",
        ),
        # 2º NÍVEL (3)
        construir_talento_classe(
            "Bomba de Fumaça",
            2,
            ["Aditivo 1", "Alquimista"],
            "Você faz a bomba criar uma nuvem de fumaça espessa além de seus efeitos normais. Quando arremessada, a bomba cria uma nuvem de fumaça em uma explosão de 3 metros de raio. A nuvem é centralizada em um canto à sua escolha no espaço do alvo (ou no espaço onde a bomba aterrissar). Criaturas dentro dessa área recebem a condição ocultada, e todas as outras criaturas estão ocultadas contra elas. A fumaça dura por 1 minuto ou até ser dissipada por um vento forte.",
            acoes="livre",
            frequencia="uma vez por rodada",
            acionamento="Você usa Alquimia Rápida para manufaturar uma bomba alquímica com nível de item pelo menos 1 nível inferior ao seu nível de alquimia avançada.",
        ),
        construir_talento_classe(
            "Mutagênico Revivificante",
            2,
            ["Alquimista"],
            "Enquanto estiver sob efeito de um mutagênico, você pode metabolizar o poder do mutagênico para se curar. Para isso, você usa uma ação única que possui os traços concentração e manuseio. Assim que a ação é completada, você recupera 1d6 Pontos de Vida para cada 2 níveis de item do mutagênico (mínimo 1d6), mas a duração do mutagênico é encerrada imediatamente (mesmo se estiver sob o efeito de Mutagênico Persistente).",
        ),
        construir_talento_classe(
            "Resistência a Veneno",
            2,
            ["Alquimista"],
            "A exposição constante a reagentes tóxicos fortificou seu corpo contra venenos de todos os tipos. Você recebe resistência a veneno igual à metade de seu nível, e recebe +1 de bônus de estado em jogadas de salvamento contra venenos.",
        ),
        # 4º NÍVEL (3)
        construir_talento_classe(
            "Alquimia Duradoura",
            4,
            ["Alquimista"],
            "Você aprendeu a fazer sua energia pessoal durar um pouco mais quando prepara rapidamente suas concocções. Quando usar Alquimia Rápida para criar uma ferramenta ou elixir alquímico, essa ferramenta ou elixir permanece potente até o final de seu próximo turno (em vez de perder sua potência no início de seu próximo turno).",
        ),
        construir_talento_classe(
            "Alquimia Eficiente",
            4,
            ["Alquimista"],
            "Graças ao tempo passado em estudos e experimentos, você sabe como extrapolar suas fórmulas para lotes maiores que não requerem qualquer atenção adicional. Quando gastar tempo em recesso para Manufaturar itens alquímicos, você pode produzir o dobro de itens alquímicos em um único lote sem gastar qualquer tempo adicional de preparação. Por exemplo: se estiver criando elixires da vida, você pode manufaturar até oito elixires, em vez de quatro, em um único lote durante o recesso. Isto não reduz a quantidade de reagentes alquímicos requeridos ou outros ingredientes necessários para manufaturar cada item, nem aumenta sua velocidade de progresso para dias gastos além do recesso base. Isto também não altera a quantidade de itens que você pode criar em um lote usando alquimia avançada.",
        ),
        construir_talento_classe(
            "Respingo Calculado",
            4,
            ["Alquimista"],
            "Você calcula todos os ângulos para maximizar o respingo de uma bomba. Quando arremessar uma bomba alquímica com o traço respingo, você pode alterar o dano de respingo causado para que seja igual ao seu modificador de Inteligência (mínimo 0) em vez da quantidade normal de dano de respingo.",
        ),
        # 6º NÍVEL (3)
        construir_talento_classe(
            "Bomba Debilitante",
            6,
            ["Aditivo 2", "Alquimista"],
            "Suas bombas impõem efeitos adicionais em seus inimigos. Você mistura uma substância na bomba que a faz causar um dos seguintes efeitos em seu alvo: desprevenido, ofuscado, surdo ou –1,5 metros de penalidade de estado em todas as Velocidades. Se o ataque com essa bomba acertar, o alvo deve obter sucesso em uma jogada de salvamento de Fortitude ou sofre esse efeito até o final de seu próximo turno. Utilize sua CD de classe para esta jogada de salvamento (mesmo se outra pessoa arremessar a bomba).",
            acoes="livre",
            frequencia="uma vez por rodada",
            acionamento="Você usa Alquimia Rápida para manufaturar uma bomba alquímica com nível de item pelo menos 2 níveis inferior ao seu nível de alquimia avançada.",
        ),
        construir_talento_classe(
            "Bombas Direcionais",
            6,
            ["Alquimista"],
            "Você consegue lançar bombas com grande força e uma trajetória precisa, angulando o respingo em um cone que jorra em uma única direção. Quando arremessar uma bomba alquímica com o traço respingo, em vez de respingar em todos os quadrados adjacentes ao alvo, você pode tratar o espaço do alvo como o primeiro quadrado afetado de um cone de 4,5 metros direcionado oposto a você — potencialmente permitindo-lhe evitar aliados e respingar mais à frente nas linhas inimigas. Se o alvo ocupar mais de um quadrado, o quadrado do alvo mais próximo de você é o primeiro afetado do cone.",
        ),
        construir_talento_classe(
            "Combinar Elixires",
            6,
            ["Aditivo 2", "Alquimista"],
            "Você descobriu como misturar dois elixires em uma única concocção híbrida. Você pode gastar 2 lotes adicionais de reagentes infundidos para acrescentar um segundo elixir ao que está sendo criado. O segundo elixir também deve ser pelo menos 2 níveis inferior ao seu nível de alquimia avançada, e o elixir combinado é um item alquímico dois níveis superior ao maior nível dentre os dois elixires combinados. Quando este elixir combinado é consumido, ambos os elixires constituintes surtem efeito. Por exemplo: você pode combinar dois elixires da vida para criar um elixir combinado que cura o dobro da quantidade normal ou pode combinar um elixir de visão no escuro menor com um elixir de olho de águia menor para receber visão no escuro e encontrar portas secretas.",
            acoes="livre",
            frequencia="uma vez por rodada",
            acionamento="Você usa Alquimia Rápida para manufaturar um item alquímico com o traço elixir com nível de item pelo menos 2 níveis inferior ao seu nível de alquimia avançada.",
        ),
        # 8º NÍVEL (3)
        construir_talento_classe(
            "Alquimia Poderosa",
            8,
            ["Alquimista"],
            "Itens alquímicos que você cria na hora são particularmente potentes. Quando usar Alquimia Rápida para criar um item alquímico infundido que permite uma jogada de salvamento, você pode substituir a CD dele pela sua CD de classe.",
        ),
        construir_talento_classe(
            "Bomba Grudenta",
            8,
            ["Aditivo 2", "Alquimista"],
            "Você mistura um aditivo que faz o conteúdo de suas bombas aderir ao alvo e continuar a causar dano. Uma criatura que sofrer um acerto direto de uma de suas bombas grudentas também sofre dano persistente igual e do mesmo tipo que o dano de respingo da bomba. Se a bomba já causar dano persistente, some os dois valores.",
            acoes="livre",
            frequencia="uma vez por rodada",
            acionamento="Você usa Alquimia Rápida para manufaturar uma bomba alquímica com nível de item pelo menos 2 níveis inferior ao seu nível de alquimia avançada.",
        ),
        construir_talento_classe(
            "Mutagênico Feral",
            8,
            ["Alquimista"],
            "Seu mutagênico bestial traz à tona a sua besta interior, concedendo-lhe garras, dentes afiados e uma aparência feroz. Sempre que for afetado por um mutagênico bestial, você recebe o bônus de item do mutagênico em seus testes de Intimidação. Além disso, suas garras e mandíbulas se tornam ainda mais ferozes, recebendo o traço mortal d10. Finalmente, você pode aumentar a penalidade do mutagênico na CA de –1 para –2 e, em troca, aumentar o tamanho do dado de dano de suas garras e mandíbulas em um passo.",
        ),
        # 10º NÍVEL (5)
        construir_talento_classe(
            "Bomba Debilitante Maior",
            10,
            ["Alquimista"],
            "Você aprendeu técnicas avançadas e segredos alquímicos para expandir as possibilidades de efeitos impostos por suas bombas. Quando usar Bomba Debilitante, adicione as seguintes opções à lista de efeitos que podem ser impostos: desajeitado 1, enfraquecido 1, estupefato 1, ou –3 metros de penalidade de estado em todas as Velocidades.",
            pre_requisitos="Bomba Debilitante",
        ),
        construir_talento_classe(
            "Elixir Misericordioso",
            10,
            ["Aditivo 2", "Alquimista"],
            "Você mistura um aditivo especial em seu elixir que acalma o corpo e a mente de quem o ingere. O elixir da vida tenta neutralizar um efeito de medo ou que imponha a condição paralisado à criatura que o ingerir, utilizando o nível do item e um modificador de neutralização igual à sua CD de classe – 10.",
            acoes="livre",
            frequencia="uma vez por rodada",
            acionamento="Você usa Alquimia Rápida para manufaturar um elixir da vida com nível de item pelo menos 2 níveis inferior ao seu nível de alquimia avançada.",
        ),
        construir_talento_classe(
            "Envenenador Potente",
            10,
            ["Alquimista"],
            "Ao concentrar os componentes tóxicos de seus venenos, você os torna mais difíceis de resistir. Quando manufaturar um item alquímico com o traço veneno através de qualquer meio, você aumenta a CD dele em até 4 pontos (até um máximo igual à sua CD de classe).",
            pre_requisitos="Alquimia Poderosa",
        ),
        construir_talento_classe(
            "Mutagênico Elástico",
            10,
            ["Alquimista"],
            "Você faz seu corpo retorcer e fluir como o mercúrio dentro de seus mutagênicos. Sempre que estiver sob os efeitos de um mutagênico de mercúrio, você pode esticar suas pernas e Dar um Passo de até 3 metros ou espremer e comprimir seu corpo, permitindo-lhe passar por espaços apertados como se fosse um tamanho menor (além dos efeitos de Espremer-se).",
        ),
        construir_talento_classe(
            "Respingo Expandido",
            10,
            ["Alquimista"],
            "Os componentes particularmente voláteis que você mistura em suas bombas resultam em explosões especialmente grandes e poderosas. Quando arremessar uma bomba alquímica e essa bomba possuir o traço respingo, você pode adicionar seu modificador de Inteligência ao dano de respingo usual da bomba, e ela causa dano de respingo a todas as criaturas a até 3 metros do alvo.",
            pre_requisitos="Respingo Calculado",
        ),
        # 12º NÍVEL (3)
        construir_talento_classe(
            "Bombas Excepcionais",
            12,
            ["Alquimista"],
            "Você lança bombas de maneira infalível, apesar de obstruções ou distância. Quando arremessar um item alquímico com o traço bomba, o incremento de distância dele aumenta para 18 metros, você também reduz quaisquer bônus de circunstância à CA do alvo por cobertura em 1 ponto, e automaticamente obtém sucesso no teste simples para mirar uma criatura ocultada.",
            pre_requisitos="Lançador Longínquo",
        ),
        construir_talento_classe(
            "Mutagênico Invencível",
            12,
            ["Alquimista"],
            "Os aditivos fortificantes que você mistura em seus mutagênicos deixam a sua forma irrefreável ainda mais impenetrável. Sempre que for afetado por um mutagênico do irrefreável, você adquire resistência a todo dano físico igual ao seu valor de Inteligência (mínimo 0).",
        ),
        construir_talento_classe(
            "Prolongar Elixir",
            12,
            ["Alquimista"],
            "Ao investir sua própria energia pessoal nos elixires que cria, você faz com que o afetem por mais tempo. Quando consumir um de seus itens alquímicos que possua os traços elixir e infundido e duração de 1 minuto ou mais, você dobra a duração desse elixir.",
        ),
        # 14º NÍVEL (3)
        construir_talento_classe(
            "Bomba Debilitante Verdadeira",
            14,
            ["Alquimista"],
            "Sempre inventivo, você descobriu formas ainda mais devastadoras para impedir e refrear seus adversários com suas bombas. Quando usar Bomba Debilitante, adicione as seguintes opções à lista de efeitos que podem ser impostos: enfraquecido 2, estupefato 2, ou –4,5 metros de penalidade de estado em todas as Velocidades. Se você resolver aplicar um dos efeitos listados em Bomba Debilitante, o alvo evita o efeito apenas se o resultado da jogada de salvamento dele for um sucesso crítico.",
            pre_requisitos="Bomba Debilitante Maior",
        ),
        construir_talento_classe(
            "Elixir Misericordioso Maior",
            14,
            ["Alquimista"],
            "Seus aditivos contêm panaceias curativas capazes de remediar várias enfermidades. Quando você usar Elixir Misericordioso, seu elixir pode tentar neutralizar a condição cego, enjoado, lento ou surdo.",
            pre_requisitos="Elixir Misericordioso",
        ),
        construir_talento_classe(
            "Mutagênico Loquaz",
            14,
            ["Alquimista"],
            "Seu mutagênico de língua de prata transcende idiomas e até a plausibilidade. Quando afetado por um mutagênico de língua de prata, você ignora penalidades de circunstância em testes de Diplomacia, Dissimulação, Intimidação e Performance. Além disso, suas palavras transcendem as barreiras linguísticas; todos que lhe ouvirem falar compreendem suas palavras como se você estivesse falando o idioma deles (embora você não fale de fato esse idioma). Esta habilidade também não lhe permite compreender quaisquer idiomas adicionais.",
        ),
        # 16º NÍVEL (4)
        construir_talento_classe(
            "Bomba Lancinante",
            16,
            ["Aditivo 2", "Alquimista"],
            "Você mistura uma substância na bomba para reduzir as resistências de seu inimigo. A bomba reduz qualquer resistência que o inimigo possua ao tipo de dano da bomba em uma quantidade igual ao seu nível, mas apenas para esse ataque.",
            acoes="livre",
            frequencia="uma vez por rodada",
            acionamento="Você usa Alquimia Rápida para manufaturar uma bomba alquímica com nível de item pelo menos 2 níveis inferior ao seu nível de alquimia avançada.",
        ),
        construir_talento_classe(
            "Elixir Eterno",
            16,
            ["Alquimista"],
            "Seu corpo prontamente aceita e retém mudanças menores. Quando consumir um de seus itens alquímicos que possua os traços elixir e infundido e duração de 1 minuto ou mais, a duração desse elixir é indefinida. Você só pode fazer isso se o nível do elixir for igual à metade de seu nível ou inferior. Se posteriormente consumir outro elixir e tornar sua duração indefinida, o efeito do elixir indefinido anterior é encerrado.",
            pre_requisitos="Prolongar Elixir",
        ),
        construir_talento_classe(
            "Mutagênico Genial",
            16,
            ["Alquimista"],
            "Você realiza ajustes especializados na fórmula de seus mutagênicos cognitivos que amplificam sua genialidade para melhorar os benefícios recebidos. Sempre que for afetado por um mutagênico cognitivo, você recebe o bônus de item do mutagênico em seus testes de Diplomacia, Dissimulação, Intimidação, Medicina, Natureza, Performance, Religião e Sobrevivência. Além disso, você pode comunicar-se telepaticamente com criaturas a até 18 metros caso compartilhem um idioma em comum. Depois de estabelecida, a comunicação passa a ser duas vias, fazendo com que uma criatura contatada também possa se comunicar com você.",
        ),
        construir_talento_classe(
            "Mutagênico Persistente",
            16,
            ["Alquimista"],
            "Você treinou sua forma física para permanecer estável em um determinado estado alterado. Uma vez por dia, quando consumir um item alquímico com os traços infundido e mutagênico, você retém os efeitos dele até a próxima vez que fizer suas preparações diárias (em vez de considerar sua duração normal).",
            pre_requisitos="Prolongar Elixir",
        ),
        # 18º NÍVEL (4)
        construir_talento_classe(
            "Debilitação Perfeita",
            18,
            ["Alquimista"],
            "Você aperfeiçoou as fórmulas de bombas que retardam seus inimigos. Quando usar Bomba Debilitante, seu alvo evita a condição imposta pela bomba apenas se obtiver um sucesso crítico em sua jogada de salvamento.",
        ),
        construir_talento_classe(
            "Elixires Improváveis",
            18,
            ["Alquimista"],
            "Seu domínio de segredos alquímicos lhe permite replicar efeitos que alguns acreditam serem possíveis apenas através de magia. Selecione uma quantidade de poções igual ao seu modificador de Inteligência (mínimo 1) de 9º nível ou inferior. Você recebe fórmulas para criar estas poções como itens alquímicos com o traço elixir. Quando criar estes elixires alquímicos, você pode substituir reagentes alquímicos por um valor equivalente de componentes mágicos e usar ferramentas de alquimista (para Alquimia Rápida) ou um laboratório de alquimista (para a atividade Manufaturar) em vez de quaisquer outros kits de ferramentas necessários. Exceto por isso, a fórmula não muda. Uma vez que tenha escolhido as fórmulas das poções, elas não podem ser alteradas.",
        ),
        construir_talento_classe(
            "Mutagênico de Mente Limpa",
            18,
            ["Alquimista"],
            "Com um ajuste mínimo nas proporções da fórmula de seu mutagênico sereno, você obtém proteções mentais. Quando for afetado por um mutagênico sereno, efeitos de detecção, revelação e vidência de 9º nível ou inferior não detectam nada em você, suas posses e auras. Por exemplo, detectar magia ainda detectaria outras magias na área, mas não qualquer magia em você.",
        ),
        construir_talento_classe(
            "Trabalhador Milagroso",
            18,
            ["Alquimista"],
            "Seu domínio da alquimia pode ressuscitar os recentemente falecidos. Você pode administrar um elixir da vida verdadeiro a uma criatura que tenha morrido a 2 rodadas ou menos. Quando o fizer, essa criatura retorna imediatamente à vida com 1 Ponto de Vida e ferida 1.",
            frequencia="uma vez a cada 10 minutos",
        ),
        # 20º NÍVEL (3)
        construir_talento_classe(
            "Criar Pedra Filosofal",
            20,
            ["Alquimista"],
            "Sua longa pesquisa deu resultado, culminando na lendária pedra filosofal. Você aprende a fórmula para a pedra filosofal (página 551) e pode acrescentá-la ao seu livro de fórmulas.",
        ),
        construir_talento_classe(
            "Mega Bomba",
            20,
            ["Aditivo 3", "Alquimista"],
            "Você acrescenta um aditivo incrivelmente poderoso à bomba segurada para criar uma mega bomba, aumentando consideravelmente sua área e poder. Você usa uma ação de Interagir (em vez de Golpear) para arremessar a mega bomba e não realiza uma rolagem de ataque. A mega bomba afeta criaturas em uma explosão de 9 metros de raio, centrada a até 18 metros de você. A bomba causa dano como se cada criatura fosse o alvo primário, permitindo que realizem um salvamento básico de Reflexos. Se fracassar no salvamento, a criatura também sofre quaisquer efeitos que afetariam um alvo primário (como o efeito desprevenido de um relâmpago engarrafado). Embora todos os alvos na área sofram o dano de respingo como alvos primários, nenhum dano de respingo é causado a qualquer outra criatura além dessa área. Se a sua próxima ação após criar uma mega bomba não for uma ação de Interagir para arremessá-la, a mega bomba perde a potência e todos seus efeitos.",
            acoes="1",
            pre_requisitos="Respingo Expandido",
            requerimentos="Você segura uma bomba alquímica infundida e que tenha nível de item pelo menos 3 níveis inferiores ao seu nível de alquimia avançada.",
        ),
        construir_talento_classe(
            "Mutagênico Perfeito",
            20,
            ["Alquimista"],
            "Você aprimorou as fórmulas de seus mutagênicos, alinhando-os perfeitamente à sua fisiologia. Quando estiver sob os efeitos de um mutagênico de sua criação, você não sofre suas desvantagens.",
        ),
    ]

    return {
        "id": "alquimista",
        "nome": "Alquimista",
        "paginas": "70-81",
        "descricao": (
            "Não há visão mais bela do que uma mistura estranha borbulhando, e você consome elixires engenhosos sem preocupação. "
            "Fascinado em descobrir os segredos da ciência e do mundo natural, você constantemente faz experimentos em seu laboratório ou em campo. "
            "Você é destemido frente ao risco, arremessando criações explosivas ou tóxicas em seus adversários. Seu único caminho à grandeza está cheio de misturas alquímicas que levam seu corpo e mente ao limite."
        ),
        "atributo_chave": {
            "opcoes": ["inteligencia"],
            "melhoria_1_nivel": 2,
            "texto": "Inteligência — No 1º nível, sua classe lhe concede uma melhoria de atributo em Inteligência.",
        },
        "pontos_de_vida_por_nivel": 8,
        "pontos_de_vida_texto": "8 mais seu modificador de Constituição no 1º nível e a cada nível subsequente.",
        "jogando_com_a_classe": {
            "encontros_combate": (
                "Você lança suas bombas nos adversários, assola seus inimigos e apoia o resto de seu grupo com elixires potentes. "
                "Em níveis superiores, seus mutagênicos distorcem seu corpo em uma arma poderosa e resiliente."
            ),
            "encontros_sociais": "Você fornece conhecimento e experiência sobre itens alquímicos e segredos relacionados, como doenças e venenos.",
            "exploracao": "Você se mantém atento a problemas com suas bombas à mão, enquanto dá conselhos sobre quaisquer assuntos alquímicos e misteriosos.",
            "recesso": "Você experimenta em um laboratório alquímico, misturando elixires, criando bombas e aprofundando seu conhecimento alquímico.",
            "voce_pode": [
                "Gostar de aprimorar fórmulas estranhas e reagentes alquímicos, frequentemente com dedicação e imprudência ímpares que fariam outras pessoas se espantarem.",
                "Ficar empolgado com a destruição causada por suas concocções alquímicas, e apreciar ver coisas queimarem, dissolverem, congelarem e se eletrocutarem.",
                "Experimentar incansavelmente para descobrir ferramentas alquímicas novas e mais potentes.",
            ],
            "outros_provavelmente": [
                "Acham que você é algum tipo de feiticeiro ou um mago excêntrico e não compreendem que você não conjura magias — e, ainda pior, os conjuradores que mexem de forma desajeitada com alquimia apenas aumentam este equívoco.",
                "Não compreendem seu entusiasmo por alquimia, criatividade e invenções.",
                "Pressupõem que se você ainda não tiver causado uma catástrofe com seus experimentos, inevitavelmente o fará.",
            ],
        },
        "proficiencias_iniciais": {
            "percepcao": "treinado",
            "salvamentos": {
                "fortitude": "especialista",
                "reflexos": "especialista",
                "vontade": "treinado",
            },
            "pericias": {
                "fixas": ["manufatura"],
                "opcoes_fixas": [],
                "adicionais_base": 3,
                "soma_modificador_inteligencia": True,
                "texto": "Treinado em Manufatura; treinado em uma quantidade de perícias adicionais igual a 3 mais seu modificador de Inteligência.",
            },
            "ataques": {
                "armas_simples": "treinado",
                "bombas_alquimicas": "treinado",
                "ataques_desarmados": "treinado",
            },
            "defesas": {
                "armaduras_leves": "treinado",
                "defesa_sem_armadura": "treinado",
            },
            "cd_classe": {
                "graduacao": "treinado",
                "texto": "Treinado em CD de classe de alquimista",
            },
            "magias": None,
        },
        "tabela_progressao": tabela_progressao,
        "tabelas_especificas": {
            "tabela_talentos_indice": tabela_talentos_indice,
            "exemplo_livro_de_formulas": {
                "nome": "Os Fundamentos da Alquimia",
                "pagina": 81,
                "formulas": [
                    "antídoto menor",
                    "antipeste menor",
                    "bastão de fumaça menor",
                    "bolsa emaranhapé menor",
                    "elixir do guepardo menor",
                    "elixir da vida mínimo",
                    "fogo alquímico menor",
                    "frasco de ácido menor",
                ],
            },
        },
        "caracteristicas_de_classe": caracteristicas_de_classe,
        "subclasses": subclasses,
        "termos_chave": termos_chave,
        "exemplos_personagens": exemplos_personagens,
        "talentos_de_classe": talentos,
    }


def construir_barbaro() -> dict[str, Any]:
    """Constrói os dados completos da classe Bárbaro (pp. 82–93)."""
    tabela_progressao = construir_tabela_progressao(
        [
            (1, "Ancestralidade e biografia, fúria, instinto, proficiências iniciais, talento de bárbaro"),
            (2, "Talento de bárbaro, talento de perícia"),
            (3, "Incremento de perícia, negar vantagem, talento geral"),
            (4, "Talento de bárbaro, talento de perícia"),
            (5, "Brutalidade, incremento de perícia, melhorias de atributo, talento de ancestralidade"),
            (6, "Talento de bárbaro, talento de perícia"),
            (7, "Especialização em armas, incremento de perícia, irrefreável, talento geral"),
            (8, "Talento de bárbaro, talento de perícia"),
            (9, "Incremento de perícia, reflexos rápidos, resistência em fúria, talento de ancestralidade"),
            (10, "Melhorias de atributo, talento de bárbaro, talento de perícia"),
            (11, "Fúria poderosa, incremento de perícia, talento geral"),
            (12, "Talento de bárbaro, talento de perícia"),
            (13, "Especialidade em armaduras médias, furor com armas, incremento de perícia, irrefreável maior, talento de ancestralidade"),
            (14, "Talento de bárbaro, talento de perícia"),
            (15, "Especialização em armas maior, incremento de perícia, melhorias de atributo, talento geral, vontade indomável"),
            (16, "Talento de bárbaro, talento de perícia"),
            (17, "Fúria rápida, incremento de perícia, sentidos elevados, talento de ancestralidade"),
            (18, "Talento de bárbaro, talento de perícia"),
            (19, "Armadura de furor, devastador, incremento de perícia, talento geral"),
            (20, "Melhorias de atributo, talento de bárbaro, talento de perícia"),
        ]
    )

    tabela_3_3_instintos_animais = [
        {
            "animal": "Felino",
            "ataques": [
                {"nome": "Garra", "dano": "1d6 Ct", "dado": "1d6", "tipo_dano": "cortante", "tracos": ["Ágil", "desarmado"]},
                {"nome": "Mandíbulas", "dano": "1d10 Pf", "dado": "1d10", "tipo_dano": "perfurante", "tracos": ["Desarmado"]},
            ],
        },
        {
            "animal": "Lobo",
            "ataques": [
                {"nome": "Mandíbulas", "dano": "1d10 Pf", "dado": "1d10", "tipo_dano": "perfurante", "tracos": ["Derrubar", "desarmado"]},
            ],
        },
        {
            "animal": "Macaco",
            "ataques": [
                {"nome": "Punho", "dano": "1d10 Cn", "dado": "1d10", "tipo_dano": "contundente", "tracos": ["Agarrar", "desarmado"]},
            ],
        },
        {
            "animal": "Sapo",
            "ataques": [
                {"nome": "Língua", "dano": "1d4 Cn", "dado": "1d4", "tipo_dano": "contundente", "tracos": ["Ágil", "desarmado"]},
                {"nome": "Mandíbulas", "dano": "1d10 Cn", "dado": "1d10", "tipo_dano": "contundente", "tracos": ["Desarmado"]},
            ],
        },
        {
            "animal": "Serpente",
            "ataques": [
                {"nome": "Presas", "dano": "1d10 Pf", "dado": "1d10", "tipo_dano": "perfurante", "tracos": ["Agarrar", "desarmado"]},
            ],
        },
        {
            "animal": "Touro",
            "ataques": [
                {"nome": "Chifre", "dano": "1d10 Pf", "dado": "1d10", "tipo_dano": "perfurante", "tracos": ["Desarmado", "empurrar"]},
            ],
        },
        {
            "animal": "Tubarão",
            "ataques": [
                {"nome": "Mandíbulas", "dano": "1d10 Pf", "dado": "1d10", "tipo_dano": "perfurante", "tracos": ["Agarrar", "desarmado"]},
            ],
        },
        {
            "animal": "Urso",
            "ataques": [
                {"nome": "Garra", "dano": "1d6 Ct", "dado": "1d6", "tipo_dano": "cortante", "tracos": ["Ágil", "desarmado"]},
                {"nome": "Mandíbulas", "dano": "1d10 Pf", "dado": "1d10", "tipo_dano": "perfurante", "tracos": ["Desarmado"]},
            ],
        },
        {
            "animal": "Veado",
            "ataques": [
                {"nome": "Galhada", "dano": "1d10 Pf", "dado": "1d10", "tipo_dano": "perfurante", "tracos": ["Agarrar", "desarmado"]},
            ],
        },
    ]

    tabela_3_4_instintos_de_dragao = [
        {"dragao": "Azul", "tipo": "Cromático", "sopro": "Linha de eletricidade", "formato_sopro": "linha", "tipo_dano": "eletricidade"},
        {"dragao": "Branco", "tipo": "Cromático", "sopro": "Cone de frio", "formato_sopro": "cone", "tipo_dano": "frio"},
        {"dragao": "Negro", "tipo": "Cromático", "sopro": "Linha de ácido", "formato_sopro": "linha", "tipo_dano": "ácido"},
        {"dragao": "Verde", "tipo": "Cromático", "sopro": "Cone de veneno", "formato_sopro": "cone", "tipo_dano": "veneno"},
        {"dragao": "Vermelho", "tipo": "Cromático", "sopro": "Cone de fogo", "formato_sopro": "cone", "tipo_dano": "fogo"},
        {"dragao": "Bronze", "tipo": "Metálico", "sopro": "Linha de eletricidade", "formato_sopro": "linha", "tipo_dano": "eletricidade"},
        {"dragao": "Cobre", "tipo": "Metálico", "sopro": "Linha de ácido", "formato_sopro": "linha", "tipo_dano": "ácido"},
        {"dragao": "Latão", "tipo": "Metálico", "sopro": "Linha de fogo", "formato_sopro": "linha", "tipo_dano": "fogo"},
        {"dragao": "Ouro", "tipo": "Metálico", "sopro": "Cone de fogo", "formato_sopro": "cone", "tipo_dano": "fogo"},
        {"dragao": "Prata", "tipo": "Metálico", "sopro": "Cone de frio", "formato_sopro": "cone", "tipo_dano": "frio"},
    ]

    tabela_talentos_indice = [
        {"nome": "Arrancada Furiosa", "nivel": 10},
        {"nome": "Arrebatar", "nivel": 4},
        {"nome": "Arrebentar", "nivel": 8},
        {"nome": "Arrebentar Colateral", "nivel": 16},
        {"nome": "Arremessador Enfurecido", "nivel": 1},
        {"nome": "Asas da Fúria do Dragão", "nivel": 12},
        {"nome": "Ataque de Oportunidade", "nivel": 6},
        {"nome": "Atleta Enfurecido", "nivel": 4},
        {"nome": "Atracar Furioso", "nivel": 12},
        {"nome": "Bote de Predador", "nivel": 12},
        {"nome": "Brado Aterrorizante", "nivel": 10},
        {"nome": "Clareza Perfeita", "nivel": 18},
        {"nome": "Compartilhar Fúria", "nivel": 8},
        {"nome": "Crítico Brutal", "nivel": 18},
        {"nome": "Estatura de Gigante", "nivel": 6},
        {"nome": "Estatura de Titã", "nivel": 12},
        {"nome": "Estocada de Gigante", "nivel": 14},
        {"nome": "Evisceração Viciosa", "nivel": 18},
        {"nome": "Faro Aguçado", "nivel": 2},
        {"nome": "Finalização Furiosa", "nivel": 2},
        {"nome": "Fúria Animal", "nivel": 8},
        {"nome": "Fúria Contagiante", "nivel": 20},
        {"nome": "Fúria Ferida", "nivel": 4},
        {"nome": "Golpe Giratório", "nivel": 14},
        {"nome": "Golpe Impressionante", "nivel": 14},
        {"nome": "Golpe Vingativo", "nivel": 14},
        {"nome": "Impetuosidade Temerária", "nivel": 16},
        {"nome": "Interferência dos Espíritos", "nivel": 6},
        {"nome": "Intimidação Enfurecida", "nivel": 1},
        {"nome": "Investida Súbita", "nivel": 1},
        {"nome": "Ira do Espírito", "nivel": 12},
        {"nome": "Jogar para Trás", "nivel": 10},
        {"nome": "Momento de Clareza", "nivel": 1},
        {"nome": "Movimento Veloz", "nivel": 4},
        {"nome": "Opressão Brutal", "nivel": 6},
        {"nome": "Opressão Furiosa", "nivel": 8},
        {"nome": "Pele de Animal", "nivel": 6},
        {"nome": "Pisão do Tremor", "nivel": 20},
        {"nome": "Restabelecer-se", "nivel": 2},
        {"nome": "Retomar o Fôlego", "nivel": 2},
        {"nome": "Salto Súbito", "nivel": 8},
        {"nome": "Sem Escapatória", "nivel": 2},
        {"nome": "Sopro de Fúria do Dragão", "nivel": 6},
        {"nome": "Transformação do Dragão", "nivel": 16},
        {"nome": "Trespassar", "nivel": 6},
        {"nome": "Trespassar Maior", "nivel": 10},
        {"nome": "Venha Me Pegar", "nivel": 10},
        {"nome": "Vigor Renovado", "nivel": 8},
        {"nome": "Visão Aguçada", "nivel": 1},
    ]

    caracteristicas_de_classe = [
        construir_caracteristica_classe(
            "Ancestralidade e Biografia",
            1,
            "Além das habilidades fornecidas por sua classe no 1º nível, você possui os benefícios da ancestralidade e biografia selecionadas, conforme descrito no Capítulo 2.",
        ),
        construir_caracteristica_classe(
            "Proficiências Iniciais",
            1,
            "No 1º nível, você recebe proficiências que representam seu treinamento básico, listadas no início desta classe.",
        ),
        construir_caracteristica_classe(
            "Fúria",
            1,
            "Você ganha a ação Fúria, que lhe permite entrar em frenesi.",
            acoes_concedidas=[
                construir_acao_habilidade(
                    "Fúria",
                    "1",
                    ["Bárbaro", "Concentração", "Emoção", "Mental"],
                    (
                        "Você acessa seu furor interior e entra em fúria. Você recebe uma quantidade de Pontos de Vida temporários igual ao seu nível "
                        "mais seu modificador de Constituição. Este frenesi dura por 1 minuto, até que não haja inimigos que você possa perceber ou até "
                        "você ficar inconsciente — o que ocorrer primeiro. Você não pode encerrar sua fúria voluntariamente. Enquanto estiver em fúria: "
                        "• Você causa 2 pontos de dano adicionais com armas corpo a corpo e ataques desarmados (dividido pela metade se a arma ou ataque desarmado for ágil); "
                        "• Você sofre –1 de penalidade na CA; "
                        "• Você não pode usar ações com o traço concentração a menos que elas também possuam o traço fúria (você pode Buscar enquanto estiver em fúria). "
                        "Após encerrar sua fúria, você perde quaisquer Pontos de Vida temporários recebidos pela Fúria e não pode entrar em Fúria novamente por 1 minuto."
                    ),
                    requerimentos="Você não está fatigado ou em fúria.",
                )
            ],
        ),
        construir_caracteristica_classe(
            "Instinto",
            1,
            (
                "Sua fúria surge de um instinto dominante — algo que você aprendeu através de uma tradição ou que irrompeu naturalmente de você. "
                "Seu instinto escolhido lhe concede uma habilidade, exige que você evite certos comportamentos (anátemas), lhe concede dano aumentado e resistências "
                "em níveis superiores e lhe permite selecionar talentos ligados a seu instinto."
            ),
        ),
        construir_caracteristica_classe(
            "Talentos de Bárbaro",
            1,
            "No 1º nível e a cada nível par subsequente, você recebe um talento de classe de bárbaro.",
        ),
        construir_caracteristica_classe(
            "Talentos de Perícia",
            2,
            "No 2º nível e a cada 2 níveis subsequentes, você recebe um talento de perícia (Capítulo 5). Você deve possuir graduação treinado ou melhor na perícia correspondente.",
        ),
        construir_caracteristica_classe(
            "Incrementos de Perícia",
            3,
            "No 3º nível e a cada 2 níveis subsequentes, você recebe um incremento de perícia (treinado ou especialista; mestre a partir do 7º nível; lendário a partir do 15º nível).",
        ),
        construir_caracteristica_classe(
            "Negar Vantagem",
            3,
            "Você não fica desprevenido para criaturas do seu nível ou inferior que estejam escondidas, indetectadas, flanqueando-lhe ou usando um ataque surpresa. Entretanto, elas ainda podem ajudar criaturas aliadas a flanqueá-lo.",
        ),
        construir_caracteristica_classe(
            "Talentos Gerais",
            3,
            "No 3º nível e a cada 4 níveis subsequentes, você recebe um talento geral (Capítulo 5).",
        ),
        construir_caracteristica_classe(
            "Brutalidade",
            5,
            "Suas graduações de proficiência em armas simples, armas marciais e ataques desarmados aumentam para especialista. Enquanto estiver em fúria, você obtém acesso aos efeitos de especialização de crítico em armas corpo a corpo e ataques desarmados.",
        ),
        construir_caracteristica_classe(
            "Melhorias de Atributo",
            5,
            "No 5º nível e a cada 5 níveis subsequentes, você melhora os valores de quatro atributos diferentes (+1 se já for 18 ou maior, +2 se menor que 18).",
        ),
        construir_caracteristica_classe(
            "Talentos de Ancestralidade",
            5,
            "Você recebe um talento de ancestralidade no 5º nível e a cada 4 níveis subsequentes.",
        ),
        construir_caracteristica_classe(
            "Especialização em Armas",
            7,
            "Você causa 2 pontos de dano adicionais com armas e ataques desarmados nos quais é especialista (3 se mestre, 4 se lendário). Você recebe a habilidade de especialização do seu instinto.",
        ),
        construir_caracteristica_classe(
            "Irrefreável",
            7,
            "Sua graduação de proficiência em salvamentos de Fortitude aumenta para mestre. Quando rolar um sucesso em um salvamento de Fortitude, trate o resultado como um sucesso crítico.",
        ),
        construir_caracteristica_classe(
            "Reflexos Rápidos",
            9,
            "Sua graduação de proficiência em salvamentos de Reflexos aumenta para especialista.",
        ),
        construir_caracteristica_classe(
            "Resistência em Fúria",
            9,
            "Enquanto estiver em fúria, você adquire resistência igual a 3 + seu modificador de Constituição aos tipos de dano indicados em seu instinto.",
        ),
        construir_caracteristica_classe(
            "Fúria Poderosa",
            11,
            "Sua graduação de proficiência em sua CD de classe de bárbaro aumenta para especialista. Você ganha a ação livre Fúria Poderosa.",
            acoes_concedidas=[
                construir_acao_habilidade(
                    "Fúria Poderosa",
                    "livre",
                    ["Bárbaro"],
                    (
                        "Você usa uma ação que possua o traço fúria. Alternativamente, você pode usar duas ações para ativar a Fúria acionadora "
                        "(em vez da ação única normalmente requerida para ativar Fúria) e usar uma atividade de duas ações que possua o traço Fúria como a ação livre desta habilidade."
                    ),
                    acionamento="Você usa a ação Fúria em seu turno.",
                )
            ],
        ),
        construir_caracteristica_classe(
            "Especialidade em Armaduras Médias",
            13,
            "Suas graduações de proficiência em armaduras leves, armaduras médias e defesa sem armadura aumentam para especialista.",
        ),
        construir_caracteristica_classe(
            "Furor com Armas",
            13,
            "Suas graduações de proficiência em armas simples, armas marciais e ataques desarmados aumentam para mestre.",
        ),
        construir_caracteristica_classe(
            "Irrefreável Maior",
            13,
            "Sua graduação de proficiência em salvamentos de Fortitude aumenta para lendário. Quando rolar uma falha crítica em um salvamento de Fortitude, trate o resultado como uma falha. Quando rolar uma falha em um salvamento de Fortitude contra um efeito que causa dano, divida o dano sofrido pela metade.",
        ),
        construir_caracteristica_classe(
            "Especialização em Armas Maior",
            15,
            "Seu dano de especialização em armas aumenta para 4 pontos com armas e ataques desarmados nos quais é especialista, 6 pontos nos quais é mestre e 8 pontos nos quais é lendário. Você recebe o benefício maior da habilidade de especialização de instinto.",
        ),
        construir_caracteristica_classe(
            "Vontade Indomável",
            15,
            "Sua graduação de proficiência em salvamentos de Vontade aumenta para mestre. Quando rolar um sucesso em um salvamento de Vontade, trate o resultado como um sucesso crítico.",
        ),
        construir_caracteristica_classe(
            "Fúria Rápida",
            17,
            "Após passar um turno completo sem estar em fúria, você pode entrar em Fúria novamente sem precisar esperar 1 minuto.",
        ),
        construir_caracteristica_classe(
            "Sentidos Elevados",
            17,
            "Sua graduação de proficiência em Percepção aumenta para mestre.",
        ),
        construir_caracteristica_classe(
            "Armadura de Furor",
            19,
            "Suas graduações de proficiência em armaduras leves, armaduras médias e defesa sem armadura aumentam para mestre.",
        ),
        construir_caracteristica_classe(
            "Devastador",
            19,
            "Sua graduação de proficiência em sua CD de classe de bárbaro aumenta para mestre. Seus Golpes corpo a corpo ignoram 10 pontos da resistência a dano físico de uma criatura.",
        ),
    ]

    subclasses = {
        "tipo": "instinto",
        "nome_tipo": "Instinto",
        "regra_anatema": (
            "Sempre que realizar atos anátemas a seu instinto, você perde as habilidades do instinto e quaisquer talentos com o traço instinto "
            "até gastar 1 dia de recesso centrando-se novamente, embora mantenha suas outras habilidades de bárbaro."
        ),
        "opcoes": [
            {
                "id": "instinto_animal",
                "nome": "Instinto Animal",
                "descricao": "O furor de um predador selvagem lhe preenche durante sua Fúria, concedendo-lhe ataques desarmados ferozes. Selecione um animal da Tabela 3–3.",
                "anatema": "Desrespeitar abertamente um animal de seu tipo escolhido é anátema a seu instinto, assim como usar armas enquanto estiver em fúria.",
                "habilidade_instinto": {
                    "nome": "Fúria Bestial",
                    "descricao": (
                        "Quando estiver em Fúria, você adquire o ataque desarmado (ou ataques desarmados) de seu animal escolhido (Tabela 3–3, grupo pugilato). "
                        "Sua ação Fúria adquire os traços morfia, primal e transmutação."
                    ),
                },
                "habilidade_especializacao_7_nivel": (
                    "Aumente o tamanho do dado de dano para os ataques desarmados concedidos por seu animal escolhido em um passo, "
                    "e aumente o dano adicional recebido de sua Fúria de 2 para 5 pontos para os ataques desarmados do animal escolhido. "
                    "O ataque de língua do sapo e o ataque de galhada do veado têm seu alcance aumentado para 3 metros."
                ),
                "habilidade_especializacao_15_nivel": "Aumente o dano de sua Fúria de 5 para 12 pontos para os ataques desarmados do animal escolhido.",
                "resistencia_em_furia": "Você resiste a dano cortante e perfurante.",
            },
            {
                "id": "instinto_de_dragao",
                "nome": "Instinto de Dragão",
                "descricao": "Você convoca o furor de um dragão poderoso e manifesta habilidades incríveis. Selecione um tipo de dragão da Tabela 3–4.",
                "anatema": (
                    "Aceitar um insulto pessoal contra você é anátema a seu instinto. Escolha se seu personagem respeita ou abomina seu tipo de dragão. "
                    "Se o respeitar, desafiar um dragão desses é anátema — se o abominar, fracassar em derrotar um dragão desses que cruzou o seu caminho é um anátema para você."
                ),
                "habilidade_instinto": {
                    "nome": "Fúria Dracônica",
                    "descricao": (
                        "Quando estiver em Fúria, você pode aumentar o dano adicional de sua Fúria de 2 para 4 pontos e alterar seu tipo de dano para corresponder com o tipo do sopro de seu dragão "
                        "em vez do tipo de dano de sua arma ou ataque desarmado. Se fizer isto, sua ação de Fúria adquire os traços arcano e evocação, assim como o traço correspondente ao tipo de dano."
                    ),
                },
                "habilidade_especializacao_7_nivel": "Quando usar fúria dracônica, você aumenta o dano adicional de sua Fúria de 4 para 8 pontos.",
                "habilidade_especializacao_15_nivel": "Aumente o dano de sua Fúria quando usar fúria dracônica de 8 para 16 pontos.",
                "resistencia_em_furia": "Você resiste a dano perfurante e ao tipo de dano do sopro de seu dragão.",
            },
            {
                "id": "instinto_espiritual",
                "nome": "Instinto Espiritual",
                "descricao": "Sua fúria assume a forma de uma possessão espiritual, seja através de sensitividade espiritual, adoração a ancestrais ou aparições.",
                "anatema": "Desrespeitar cadáveres ou espíritos é anátema para seu instinto; defender-se contra criaturas mortas-vivas não.",
                "habilidade_instinto": {
                    "nome": "Fúria Espiritual",
                    "descricao": (
                        "Quando estiver em fúria, você pode aumentar o dano de sua Fúria de 2 para 3 pontos e causar dano negativo ou dano positivo em vez do tipo de dano normal "
                        "(escolha o tipo cada vez que entrar em Fúria). Se escolher causar dano negativo ou dano positivo, sua arma ou ataque desarmado recebe os efeitos da runa de propriedade toque fantasma "
                        "e sua ação de Fúria adquire os traços divino e necromancia (além do traço negativo ou positivo, conforme apropriado)."
                    ),
                },
                "habilidade_especializacao_7_nivel": "Quando usar fúria espiritual, aumente o dano adicional de sua Fúria de 3 para 7 pontos.",
                "habilidade_especializacao_15_nivel": "Aumente o dano adicional de sua Fúria de 7 para 13 pontos.",
                "resistencia_em_furia": "Você resiste a dano negativo, assim como a todo dano causado pelos ataques e habilidades de criaturas mortas-vivas (independentemente do tipo de dano causado por elas).",
            },
            {
                "id": "instinto_do_furor",
                "nome": "Instinto do Furor",
                "descricao": "Sua fúria se origina de uma fonte interior profunda e puramente pessoal. Você usa sua fúria conforme seus próprios desejos.",
                "anatema": "Você não possui um anátema.",
                "habilidade_instinto": {
                    "nome": "Anátema e Habilidade de Instinto",
                    "descricao": "Você não possui um anátema ou habilidade de instinto. Em vez disso, você recebe um talento de bárbaro de 1º nível adicional.",
                    "talento_bonus_1_nivel": 1,
                },
                "habilidade_especializacao_7_nivel": "Aumente o dano adicional de sua Fúria de 2 para 6 pontos.",
                "habilidade_especializacao_15_nivel": "Aumente o dano adicional de sua Fúria de 6 para 12 pontos.",
                "resistencia_em_furia": "Você resiste a dano físico de armas, mas não dano físico de outras fontes (como ataques desarmados).",
            },
            {
                "id": "instinto_de_gigante",
                "nome": "Instinto de Gigante",
                "descricao": "Sua fúria lhe concede o poder bruto e o tamanho de um gigante.",
                "anatema": "Recusar ou evitar enfrentar um desafio pessoal de força é anátema para você.",
                "habilidade_instinto": {
                    "nome": "Empunhadura Titânica",
                    "descricao": (
                        "Você pode usar uma arma feita para uma criatura Grande se for Pequeno ou Médio (durante a fúria e fora dela), ou um tamanho maior que você caso contrário. "
                        "Você obtém acesso a esta arma de tamanho maior de qualquer tipo disponível na criação (com Preço e Volume normais para seu tamanho, p. 295). "
                        "Quando empunhar uma arma dessas em combate, aumente seu dano adicional de Fúria de 2 para 6 pontos, mas você sofre a condição desajeitado 1 (página 619) enquanto empunhar a arma (não removível)."
                    ),
                },
                "habilidade_especializacao_7_nivel": "Aumente o dano adicional de sua Fúria quando usar uma arma de tamanho maior de 6 para 10 pontos.",
                "habilidade_especializacao_15_nivel": "Aumente o dano adicional de sua Fúria de 10 para 18 pontos.",
                "resistencia_em_furia": "Você resiste a dano contundente e um outro tipo de dano entre eletricidade, fogo e frio, escolhido quando você adquire resistência em fúria.",
            },
        ],
    }

    termos_chave = [
        {
            "termo": "Abertura",
            "descricao": "Estas manobras funcionam apenas como sua primeira atitude em seu turno. Você pode usar uma ação de abertura apenas se ainda não tiver usado uma ação com o traço ataque ou abertura neste turno.",
        },
        {
            "termo": "Floreio",
            "descricao": "Ações de floreio são técnicas que requerem empenho demais e não podem ser realizadas várias vezes em seguida. Você pode usar apenas 1 ação com o traço floreio por turno.",
        },
        {
            "termo": "Fúria",
            "descricao": "Você deve estar em fúria para usar habilidades com o traço fúria e elas são encerradas automaticamente quando você sai de sua fúria.",
        },
        {
            "termo": "Instinto",
            "descricao": "Habilidades de instinto requerem um instinto específico; você perde acesso a essas ações se realizar atos anátemas a seu instinto.",
        },
    ]

    exemplos_personagens = [
        {
            "nome": "Furioso Animalesco",
            "pagina": 90,
            "resumo": "O animal dentro de você se liberta, transformando-o em uma criatura feral da natureza durante sua fúria. Você segue seus instintos em vez da razão, e se sente em casa nos ermos e regiões selvagens.",
            "atributos": "Aumente sua Força o máximo que puder, seguido por sua Constituição e Destreza. Uma Sabedoria alta pode aprimorar seus sentidos.",
            "pericias": ["Atletismo", "Intimidação", "Natureza", "Sobrevivência"],
            "subclasse": "Instinto Animal",
            "talento_inicial": "Intimidação Enfurecida",
            "talentos_niveis_superiores": [
                "Sem Escapatória (2º)",
                "Pele de Animal (6º)",
                "Fúria Animal (8º)",
                "Brado Aterrorizante (10º)",
                "Bote do Predador (12º)",
            ],
        },
        {
            "nome": "A Fúria",
            "pagina": 92,
            "resumo": "Você mantém uma vida simples, pois precisa de apenas uma coisa para lhe guiar: sua própria fúria interior.",
            "atributos": "Priorize sua Força, e então sua Constituição e Destreza. Sabedoria pode lhe tornar mais perceptivo.",
            "pericias": ["Acrobatismo", "Atletismo", "Furtividade", "Intimidação"],
            "subclasse": "Instinto do Furor",
            "talento_inicial": "Investida Súbita",
            "talentos_niveis_superiores": [
                "Finalização Furiosa (2º)",
                "Movimento Veloz (4º)",
                "Ataque de Oportunidade (6º)",
                "Golpe Giratório (14º)",
            ],
        },
    ]

    talentos = [
        # 1º NÍVEL (5)
        construir_talento_classe(
            "Arremessador Enfurecido",
            1,
            ["Bárbaro"],
            "As armas arremessadas por você se tornam especialmente mortais durante a fúria. Você aplica o dano adicional de Fúria em seus ataques com armas de arremesso. Se tiver o talento Crítico Brutal ou a característica de classe devastador, aplique seus benefícios a ataques com armas de arremesso.",
        ),
        construir_talento_classe(
            "Intimidação Enfurecida",
            1,
            ["Bárbaro"],
            "Seu furor enche seus adversários de medo. Enquanto estiver em fúria, suas ações Desmoralizar e Matar de Medo (da perícia Intimidação e do talento de perícia de mesmo nome, respectivamente) adquirem o traço fúria (permitindo que você as use enquanto estiver em fúria). Assim que atender aos pré-requisitos para os talentos de perícia Olhar Intimidante e Matar de Medo, você recebe estes talentos.",
        ),
        construir_talento_classe(
            "Investida Súbita",
            1,
            ["Abertura", "Bárbaro", "Floreio"],
            "Com um disparo rápido, você corre até seu adversário e faz um movimento de ataque. Ande duas vezes. Se encerrar seu movimento com pelo menos um inimigo em seu alcance corpo a corpo, você pode realizar um Golpe corpo a corpo contra esse inimigo. Você pode usar Investida Súbita ao Escalar, Escavar, Nadar ou Voar em vez de Andar se possuir o tipo de movimento correspondente.",
            acoes="2",
        ),
        construir_talento_classe(
            "Momento de Clareza",
            1,
            ["Bárbaro", "Concentração", "Fúria"],
            "Você controla sua fúria por um momento para pensar claramente. Até o final deste turno, você pode usar ações com o traço concentração mesmo que essas ações não possuam o traço fúria.",
            acoes="1",
        ),
        construir_talento_classe(
            "Visão Aguçada",
            1,
            ["Bárbaro"],
            "Quando estiver em fúria, seus sentidos visuais se aprimoram e o concedem visão no escuro.",
        ),
        # 2º NÍVEL (5)
        construir_talento_classe(
            "Faro Aguçado",
            2,
            ["Bárbaro"],
            "Quando está em Fúria, o seu sentido do olfato se aprimora. Você adquire faro impreciso com uma distância de 9 metros.",
            pre_requisitos="Visão Aguçada ou visão no escuro",
        ),
        construir_talento_classe(
            "Finalização Furiosa",
            2,
            ["Bárbaro", "Fúria"],
            "Desesperado para finalizar a luta, você canaliza toda sua fúria em um golpe final. Desfira um Golpe. Se acertar, você recebe um bônus de circunstância no dano igual à quantidade de rodadas remanescentes em sua Fúria (máximo 10). Após este Golpe, sua Fúria é encerrada imediatamente e você fica fatigado até descansar pelo menos por 10 minutos.",
            acoes="1",
        ),
        construir_talento_classe(
            "Restabelecer-se",
            2,
            ["Bárbaro", "Concentração", "Fúria"],
            "Você se concentra em sua fúria, superando o medo e lutando contra o enjoo. Reduza o valor de sua condição assustado em 1 e tente um salvamento de Fortitude para recuperar-se da condição enjoado como se tivesse gasto uma ação regurgitando; você reduz o valor de sua condição enjoado em 1 ponto em uma falha (mas não em uma falha crítica), em 2 pontos em um sucesso ou em 3 pontos em um sucesso crítico.",
            acoes="1",
        ),
        construir_talento_classe(
            "Retomar o Fôlego",
            2,
            ["Bárbaro"],
            "Você pode entrar em uma segunda fúria, mas após isso você precisa recuperar o fôlego. Você pode entrar em Fúria sem esperar por 1 minuto após sua Fúria anterior (ou 1 rodada, com fúria rápida), mas após encerrar esta segunda Fúria você fica fatigado até descansar por 10 minutos.",
        ),
        construir_talento_classe(
            "Sem Escapatória",
            2,
            ["Bárbaro", "Fúria"],
            "Você persegue um adversário em retirada. Ande até sua Velocidade, seguindo o adversário e mantendo-o ao alcance durante todo seu movimento até ele parar de se mover ou até você ter movido toda sua Velocidade. Você pode usar Sem Escapatória ao Escalar, Escavar, Nadar ou Voar em vez de Andar se possuir o tipo de movimento correspondente.",
            acoes="reacao",
            acionamento="Um adversário em seu alcance tenta se mover para longe de você.",
        ),
        # 4º NÍVEL (4)
        construir_talento_classe(
            "Arrebatar",
            4,
            ["Bárbaro", "Floreio"],
            "Você faz um movimento amplo em arco. Realize um único Golpe corpo a corpo e compare o resultado da rolagem de ataque às CAs de até dois adversários, para isso ambos devem estar ao seu alcance corpo a corpo e adjacentes um ao outro. Role o dano apenas uma vez e aplique-o a cada criatura atingida. Um Arrebatar conta como dois ataques para sua penalidade por ataques múltiplos. Se estiver usando uma arma com o traço amplitude, o modificador dela se aplica a todos os seus ataques de Arrebatar.",
            acoes="2",
        ),
        construir_talento_classe(
            "Atleta Enfurecido",
            4,
            ["Bárbaro"],
            "Obstáculos físicos são incapazes de deter o seu furor. Enquanto estiver em fúria, você adquire Velocidade de escalada e Velocidade de natação igual à sua Velocidade em terra e diminui em 10 pontos a CD de Saltos em Altura e Saltos em Distância. Além disso, a distância de seu Salto aumenta em 1,5 metros quando saltar horizontalmente e em 60 centímetros quando saltar verticalmente.",
            pre_requisitos="especialista em Atletismo",
        ),
        construir_talento_classe(
            "Fúria Ferida",
            4,
            ["Bárbaro"],
            "Você ruge de dor, despertando o furor dentro de você. Você entra em Fúria.",
            acoes="reacao",
            acionamento="Você sofre dano e está apto a entrar em fúria.",
        ),
        construir_talento_classe(
            "Movimento Veloz",
            4,
            ["Bárbaro"],
            "Sua fúria é um frenesi de movimentos rápidos. Enquanto estiver em fúria, você recebe +3 metros de bônus de estado em sua Velocidade.",
        ),
        # 6º NÍVEL (7)
        construir_talento_classe(
            "Ataque de Oportunidade",
            6,
            ["Bárbaro"],
            "Você ataca um adversário que baixa a guarda. Faça um Golpe corpo a corpo contra a criatura acionadora. Se seu ataque for um acerto crítico e o acionamento for uma ação de manuseio, você interrompe essa ação. Este Golpe não conta para sua penalidade por ataques múltiplos e sua penalidade por ataques múltiplos não se aplica a ele.",
            acoes="reacao",
            acionamento="Uma criatura em seu alcance usa uma ação de manuseio ou de movimento, desfere um ataque à distância ou sai de um quadrado usando uma ação de movimento.",
        ),
        construir_talento_classe(
            "Estatura de Gigante",
            6,
            ["Bárbaro", "Fúria", "Instinto", "Polimorfia", "Primal", "Transmutação"],
            "Você cresce a um tamanho incrível. Você fica Grande, aumentando seu alcance em 1,5 metros e sofrendo a condição desajeitado 1 (página 619) até sair de sua fúria. Seus equipamentos crescem com você.",
            acoes="1",
            pre_requisitos="instinto de gigante",
            acionamento="Você é de tamanho Médio ou menor.",
        ),
        construir_talento_classe(
            "Interferência dos Espíritos",
            6,
            ["Bárbaro", "Divino", "Fúria", "Instinto", "Necromancia"],
            "Você convoca espíritos protetores para protegê-lo contra ataques à distância. Até sua fúria encerrar, qualquer um que realizar um ataque à distância contra você deve obter sucesso em um teste simples CD 5 ou o ataque erra sem causar nenhum efeito.",
            acoes="1",
            pre_requisitos="instinto espiritual",
        ),
        construir_talento_classe(
            "Opressão Brutal",
            6,
            ["Bárbaro"],
            "Você empurra seus adversários deixando-os machucados. Enquanto estiver em fúria, quando obtiver sucesso em Agarrar, Derrubar, Desarmar ou Empurrar um adversário, você causa dano contundente igual ao seu modificador de Força a esse adversário; este dano é somado ao dano obtido por um sucesso crítico ao Derrubar.",
            pre_requisitos="especialista em Atletismo",
        ),
        construir_talento_classe(
            "Pele de Animal",
            6,
            ["Bárbaro", "Instinto", "Morfia", "Primal", "Transmutação"],
            "Sua proficiência em defesa sem armadura aumenta para especialista. Enquanto estiver em fúria e sem armadura, sua pele se transforma em um couro grosso similar à pele de seu animal. Você recebe +1 de bônus de estado na CA em vez de sofrer –1 de penalidade na CA; se tiver a característica de classe irrefreável maior, este bônus de estado aumenta para +2. A espessura de seu couro lhe impõe um limite de modificador de Destreza na CA de +3.",
            pre_requisitos="instinto animal",
        ),
        construir_talento_classe(
            "Sopro de Fúria do Dragão",
            6,
            ["Arcano", "Bárbaro", "Concentração", "Evocação", "Fúria", "Instinto"],
            "Você respira profundamente e exala uma energia poderosa em um cone de 9 metros ou em uma linha de 18 metros, causando 1d6 de dano por nível. A área e tipo de dano correspondem ao seu dragão escolhido (veja a Tabela 3–4 na página 87). Se você usou esta habilidade outra vez na última hora, a área e o dano são divididos pela metade (cone de 4,5 metros ou linha de 9 metros; 1d6 de dano a cada 2 níveis). Cada criatura na área deve tentar um salvamento básico de Reflexos.",
            acoes="2",
            pre_requisitos="instinto de dragão",
            requerimentos="Você não usou esta habilidade desde sua última Fúria.",
        ),
        construir_talento_classe(
            "Trespassar",
            6,
            ["Bárbaro", "Fúria"],
            "Seu ataque atravessa um adversário em direção a outro. Faça um Golpe corpo a corpo contra o segundo adversário.",
            acoes="reacao",
            acionamento="Seus Golpes corpo a corpo matam uma criatura ou a derrubam inconsciente, e outro adversário está adjacente a essa criatura.",
        ),
        # 8º NÍVEL (6)
        construir_talento_classe(
            "Arrebentar",
            8,
            ["Bárbaro", "Fúria"],
            "Você arrebenta o adversário agarrado. Ele sofre dano contundente igual ao seu modificador de Força mais seu dano de especialização em armas mais seu dano de Fúria. O adversário deve tentar um salvamento básico de Fortitude contra sua CD de classe.",
            acoes="1",
            requerimentos="Você possui um adversário agarrado.",
        ),
        construir_talento_classe(
            "Compartilhar Fúria",
            8,
            ["Auditivo", "Bárbaro", "Fúria", "Visual"],
            "Você alimenta o furor de um aliado. Enquanto você estiver em fúria, uma criatura aliada a até 9 metros recebe os efeitos da ação Fúria — embora ela ainda possa usar ações de concentração.",
            acoes="1",
            requerimentos="Você não usou esta habilidade desde sua última Fúria.",
        ),
        construir_talento_classe(
            "Fúria Animal",
            8,
            ["Bárbaro", "Concentração", "Fúria", "Instinto", "Polimorfia", "Primal", "Transmutação"],
            "Você se transforma em seu animal. Você recebe os benefícios da magia forma de animal de 3º nível, mas utiliza suas próprias estatísticas, Pontos de Vida temporários e ataques desarmados em vez dos concedidos por forma de animal. Você também retém as habilidades constantes de seus equipamentos. Se seu animal for um sapo, o alcance de sua língua aumenta para 4,5 metros. Dispensar a transformação recebe o traço fúria.",
            acoes="1",
            pre_requisitos="instinto animal",
        ),
        construir_talento_classe(
            "Opressão Furiosa",
            8,
            ["Bárbaro"],
            "Você oprime os adversários pelo campo de batalha. Enquanto estiver em fúria, você recebe +2 de bônus de circunstância em testes de Atletismo para ações de ataque.",
            pre_requisitos="mestre em Atletismo",
        ),
        construir_talento_classe(
            "Salto Súbito",
            8,
            ["Bárbaro"],
            "Você salta e ataca um adversário no meio do salto. Faça um Salto, Salto em Altura ou Salto em Distância e realize um Golpe corpo a corpo em qualquer ponto durante seu salto. Imediatamente após o Golpe, você cai no solo se estiver no ar mesmo se não tiver alcançado a distância máxima de seu salto. Se a distância que você cair não for maior do que a altura de seu salto, você não sofre dano da queda e aterrissa de pé. Quando realizar um Salto em Altura ou Salto em Distância durante um Salto Súbito, determine a CD de acordo com as CDs para Salto em Distância e aumente sua distância máxima até o dobro de sua Velocidade.",
            acoes="2",
        ),
        construir_talento_classe(
            "Vigor Renovado",
            8,
            ["Bárbaro", "Concentração", "Fúria"],
            "Você pausa para recuperar seu vigor furioso. Você ganha Pontos de Vida temporários igual à metade de seu nível mais seu modificador de Constituição.",
            acoes="1",
        ),
        # 10º NÍVEL (5)
        construir_talento_classe(
            "Arrancada Furiosa",
            10,
            ["Bárbaro", "Fúria"],
            "Você avança rapidamente à sua frente. Ande até cinco vezes sua Velocidade em uma linha reta. Alternativamente, você pode aumentar a quantidade de ações que compõem esta atividade para 3 ações para Andar até oito vezes sua Velocidade em linha reta.",
            acoes="2",
        ),
        construir_talento_classe(
            "Brado Aterrorizante",
            10,
            ["Auditivo", "Bárbaro", "Fúria"],
            "Você libera um brado aterrorizante. Faça testes de Intimidação para Desmoralizar cada inimigo a até 9 metros. Independentemente dos resultados de seus testes, cada inimigo fica temporariamente imune ao Brado Aterrorizante por 1 minuto.",
            acoes="1",
            pre_requisitos="Olhar Intimidante",
        ),
        construir_talento_classe(
            "Jogar para Trás",
            10,
            ["Bárbaro", "Fúria"],
            "O peso do movimento de seu ataque joga seu inimigo para trás. Você empurra o adversário 1,5 metros para trás, com os efeitos de uma manobra Empurrar bem-sucedida. Você pode seguir o adversário, como no efeito normal de um Empurrar bem-sucedido.",
            acoes="1",
            requerimentos="Sua última ação foi um Golpe bem-sucedido.",
        ),
        construir_talento_classe(
            "Trespassar Maior",
            10,
            ["Bárbaro", "Fúria"],
            "Seu furor carrega sua arma através de vários adversários. Quando Trespassar, se o seu Golpe também matar ou deixar o alvo inconsciente, você pode continuar a desferir Golpes corpo a corpo até que um deles não mate ou deixe uma criatura inconsciente, ou até que não haja mais criaturas adjacentes à criatura mais recentemente atacada pelo Trespassar — o que ocorrer primeiro.",
            pre_requisitos="Trespassar",
        ),
        construir_talento_classe(
            "Venha Me Pegar",
            10,
            ["Bárbaro", "Concentração", "Fúria"],
            "Você abre sua guarda a ataques de forma que possa retaliar fortemente. Até sua fúria encerrar, você fica desprevenido, e rolagens de dano contra você recebem +2 de bônus de circunstância. Qualquer criatura que lhe atingir fica desprevenida contra seus ataques até o final do seu próximo turno. Se acertá-la antes do final de seu próximo turno, você recebe Pontos de Vida temporários igual ao seu modificador de Constituição (o dobro disso em um acerto crítico). Estes Pontos de Vida temporários duram até o final de sua fúria.",
            acoes="1",
        ),
        # 12º NÍVEL (5)
        construir_talento_classe(
            "Asas da Fúria do Dragão",
            12,
            ["Bárbaro", "Fúria", "Instinto", "Morfia", "Primal", "Transmutação"],
            "Asas dracônicas da mesma cor que seu dragão escolhido crescem em suas costas. Enquanto estiver em fúria, você recebe uma Velocidade de voo igual à sua Velocidade em terra. Se estiver voando quando sua fúria acabar, você começa a cair, mas a transformação termina somente no último momento, de forma que você não sofre dano pela queda e aterrissa de pé.",
            acoes="1",
            pre_requisitos="instinto de dragão",
        ),
        construir_talento_classe(
            "Atracar Furioso",
            12,
            ["Bárbaro", "Fúria"],
            "Você atraca seu adversário enquanto ele está distraído por seu ataque. O adversário acertado fica agarrado, como se você tivesse obtido sucesso em um teste de Atletismo para Agarrá-lo.",
            acoes="1",
            requerimentos="Sua última ação foi um Golpe bem-sucedido, e você tem uma mão livre ou seu Golpe usou uma arma de agarrar.",
        ),
        construir_talento_classe(
            "Bote de Predador",
            12,
            ["Abertura", "Bárbaro", "Floreio", "Fúria", "Instinto"],
            "Você encurta a distância para sua presa em um borrão de movimento, atacando a criatura antes dela perceber. Você Anda até sua Velocidade e desfere um Golpe ao final de seu movimento.",
            acoes="1",
            pre_requisitos="instinto animal",
            requerimentos="Você está sem armadura ou vestindo uma armadura leve.",
        ),
        construir_talento_classe(
            "Estatura de Titã",
            12,
            ["Bárbaro", "Instinto", "Polimorfia", "Transmutação"],
            "Você cresce a um tamanho ainda maior. Quando usar Estatura de Gigante, você pode ficar Enorme (aumentando seu alcance em 3 metros se for Médio ou menor) enquanto estiver em fúria. Você sofre a condição desajeitado 1 (página 619) enquanto permanecer Enorme.",
            pre_requisitos="instinto de gigante, Estatura de Gigante",
        ),
        construir_talento_classe(
            "Ira do Espírito",
            12,
            ["Ataque", "Bárbaro", "Concentração", "Fúria", "Instinto"],
            "Você convoca uma aparição efêmera, tipicamente o fantasma de um ancestral ou um espírito da natureza, que assume a forma de um fogo-fátuo. O espírito do fogo-fátuo faz um ataque desarmado corpo a corpo contra um inimigo a até 36 metros de você. O modificador de ataque do fogo-fátuo é igual ao seu bônus de proficiência em armas marciais somado com seu modificador de Força e +2 de bônus de item, além de aplicar os mesmos bônus e penalidades de circunstância e de estado que você possuir no momento. Em um acerto, o fogo-fátuo causa 4d8 de dano mais seu modificador de Constituição (à sua escolha, esse dano é negativo ou positivo). Você não aplica seu dano de Fúria ou o dano de sua especialização em armas, mas aplica quaisquer bônus e penalidades de circunstância e de estado que também afetariam o dano do fogo-fátuo. Se o Golpe de seu fogo-fátuo for um acerto crítico, o alvo fica assustado 1. Este ataque sofre e conta para sua penalidade por ataques múltiplos como se você estivesse atacando.",
            acoes="1",
            pre_requisitos="instinto espiritual",
        ),
        # 14º NÍVEL (4)
        construir_talento_classe(
            "Estocada de Gigante",
            14,
            ["Bárbaro", "Concentração", "Fúria", "Instinto"],
            "Você estende seu corpo, preparando-se para atacar adversários fora de seu alcance normal. Até sua fúria encerrar, todos os seus ataques corpo a corpo com armas e ataques desarmados adquirem alcance de 3 metros. Este talento não aumenta o alcance de qualquer arma ou ataque desarmado que já possua o traço alcance, mas se combina com habilidades que aumentem seu alcance devido ao tamanho aumentado (como Estatura de Gigante).",
            acoes="1",
            pre_requisitos="instinto de gigante",
        ),
        construir_talento_classe(
            "Golpe Giratório",
            14,
            ["Abertura", "Bárbaro", "Floreio"],
            "Você ataca todos os adversários próximos. Faça um Golpe corpo a corpo contra cada inimigo em seu alcance corpo a corpo. Cada ataque conta para sua penalidade por ataques múltiplos, mas só aumenta sua penalidade após você ter realizado todos os seus ataques.",
            acoes="3",
        ),
        construir_talento_classe(
            "Golpe Impressionante",
            14,
            ["Bárbaro", "Concentração", "Fúria"],
            "Seus ataques são tão poderosos que podem amassar seus oponentes. Quando usar Jogar para Trás, você pode realizar um teste de Atletismo contra a CD de Fortitude de seu alvo.",
            pre_requisitos="Jogar para Trás",
            resultados={
                "sucesso_critico": "Você obtém o efeito de sucesso crítico de Empurrar, e depois o efeito de sucesso crítico de Derrubar contra o alvo.",
                "sucesso": "Você obtém o efeito de sucesso de Empurrar, e depois o efeito de Derrubar contra o alvo.",
                "falha": "Você obtém o efeito normal de Jogar para Trás.",
            },
        ),
        construir_talento_classe(
            "Golpe Vingativo",
            14,
            ["Bárbaro", "Fúria"],
            "Você contra-ataca quando é atingido por um inimigo. Faça um Golpe corpo a corpo contra a criatura acionadora. Este Golpe não conta para sua penalidade por ataques múltiplos, e sua penalidade por ataques múltiplos não se aplica a este Golpe.",
            acoes="reacao",
            pre_requisitos="Venha Me Pegar",
            acionamento="Uma criatura em seu alcance obtém um sucesso ou um sucesso crítico em um ataque contra você.",
            requerimentos="Você está sob o efeito de Venha Me Pegar.",
        ),
        # 16º NÍVEL (3)
        construir_talento_classe(
            "Arrebentar Colateral",
            16,
            ["Bárbaro", "Fúria"],
            "Quando Arrebentar um adversário agarrado, você bate esse adversário em outro próximo. Outro adversário adjacente ao adversário agarrado também sofre seu dano de Arrebentar, tentando um salvamento básico de Reflexos contra sua CD de classe.",
            pre_requisitos="Arrebentar",
        ),
        construir_talento_classe(
            "Impetuosidade Temerária",
            16,
            ["Bárbaro", "Fúria"],
            "Seu corpo fervilha em respostas aos seus ferimentos, e você abandona a cautela ao vento para finalizar o combate. Você recebe +2 de bônus de circunstância em rolagens de ataque, –2 de penalidade na CA e –1 de penalidade em salvamentos. Estes bônus e penalidades duram até sua Fúria acabar ou até você estar acima da metade de seus Pontos de Vida, o que ocorrer primeiro.",
            acoes="livre",
            acionamento="Seu turno começa e você está com metade ou menos Pontos de Vida.",
        ),
        construir_talento_classe(
            "Transformação do Dragão",
            16,
            ["Bárbaro", "Concentração", "Fúria", "Instinto", "Polimorfia", "Primal", "Transmutação"],
            "Você se transforma em um Grande dragão feroz. Você recebe os benefícios da magia forma de dragão de 6º nível, exceto que utiliza sua própria CA e modificador de ataque e também aplica o dano extra de sua Fúria. Utilize a sua CD de classe para a CD de seu sopro. A ação para Dispensar a transformação recebe o traço fúria. No 18º nível, você recebe os seguintes benefícios adicionais: +6 metros de bônus de estado em sua Velocidade de voo, seu bônus de dano com Golpes de dragão aumenta para +12 e você recebe +14 de bônus de estado no dano de seu sopro.",
            acoes="1",
            pre_requisitos="instinto de dragão, Asas da Fúria do Dragão",
        ),
        # 18º NÍVEL (3)
        construir_talento_classe(
            "Clareza Perfeita",
            18,
            ["Bárbaro", "Concentração", "Fúria", "Fortuna"],
            "Você queima toda sua fúria para garantir o acerto de seu ataque e a liberdade de sua mente. Rerrole a rolagem de ataque acionadora ou salvamento de Vontade com +2 de bônus de circunstância, use o melhor resultado, e resolva o efeito. Sua fúria acaba imediatamente.",
            acoes="reacao",
            acionamento="Você falha ou falha criticamente em uma rolagem de ataque ou salvamento de Vontade.",
        ),
        construir_talento_classe(
            "Crítico Brutal",
            18,
            ["Bárbaro"],
            "Seus acertos críticos são particularmente devastadores. Em um acerto crítico com um Golpe corpo a corpo, acrescente um dado de dano extra. Este dado é adicionado a quaisquer dados extras recebidos por uma arma fatal ou mortal. O alvo também sofre dano persistente de sangramento igual a dois dados de dano.",
        ),
        construir_talento_classe(
            "Evisceração Viciosa",
            18,
            ["Bárbaro", "Fúria"],
            "Você faz um ataque feroz que aleija seu inimigo. Faça um Golpe corpo a corpo. Se o Golpe atingir e causar dano, o alvo fica drenado 1 (ou drenado 2 em um sucesso crítico).",
            acoes="2",
        ),
        # 20º NÍVEL (2)
        construir_talento_classe(
            "Fúria Contagiante",
            20,
            ["Auditivo", "Bárbaro", "Fúria", "Visual"],
            "Você pode liderar seus aliados em um frenesi de batalha, concedendo-os benefícios incríveis. Você pode ignorar os requerimentos de Compartilhar Fúria, usando-o várias vezes em uma Fúria. Aliados afetados por Compartilhar Fúria que aceitarem seu anátema pela duração da Fúria recebem sua habilidade de instinto e a habilidade de especialização recebida por especialização em armas (mas não especialização em armas maior).",
            pre_requisitos="Compartilhar Fúria",
        ),
        construir_talento_classe(
            "Pisão do Tremor",
            20,
            ["Bárbaro", "Fúria", "Manuseio"],
            "Você pisa no chão com tanta força que cria um pequeno terremoto (com os efeitos da magia terremoto).",
            acoes="1",
            frequencia="uma vez a cada 10 minutos",
        ),
    ]

    return {
        "id": "barbaro",
        "nome": "Bárbaro",
        "paginas": "82-93",
        "descricao": (
            "A fúria de batalha o consome. Você sente prazer em causar destruição e atravessar seus inimigos com armas poderosas, "
            "contando com uma durabilidade impressionante independente de técnicas complicadas ou treinamento rígido. Sua fúria se alimenta "
            "de seus instintos brutais, que você pode associar com um animal, espírito ou alguma parte de si. Para muitos bárbaros a força bruta "
            "é um martelo e todo problema é um prego, enquanto outros tentam conter a torrente de emoções dentro de si e liberam sua fúria somente quando realmente necessário."
        ),
        "atributo_chave": {
            "opcoes": ["forca"],
            "melhoria_1_nivel": 2,
            "texto": "Força — No 1º nível, sua classe lhe concede uma melhoria de atributo em Força.",
        },
        "pontos_de_vida_por_nivel": 12,
        "pontos_de_vida_texto": "12 mais seu modificador de Constituição no 1º nível e a cada nível subsequente.",
        "jogando_com_a_classe": {
            "encontros_combate": (
                "Você invoca sua fúria e corre até a linha de frente para esmagar seus adversários. "
                "Sua melhor defesa é o ataque — você precisará derrubar os adversários antes que possam aproveitar suas defesas relativamente baixas."
            ),
            "encontros_sociais": "Você utiliza intimidação para conseguir o que precisa, especialmente quando uma persuasão mais gentil é incapaz de completar o trabalho.",
            "exploracao": (
                "Você procura pelo perigo, pronto para ser o primeiro a encarar uma batalha a qualquer instante. Você escala a parede de rocha desafiadora "
                "e joga a corda para outros subirem, ou nada nas correntes arriscadas do rio para alcançar a alavanca escondida sob a superfície da água. "
                "Se algo precisar ser quebrado, você está pronto para a tarefa!"
            ),
            "recesso": "Você pode entrar em uma taverna para farrear, disseminar as lendas de seus feitos poderosos ou recrutar seguidores para se tornar um senhor da guerra pelo seu próprio mérito.",
            "voce_pode": [
                "Ter uma profunda fonte de raiva, ódio ou frustração.",
                "Preferir uma abordagem direta a uma que requeira paciência e tédio.",
                "Engajar em um regime de exercícios físicos intensos — e socar todo mundo que disser que isto conflita com seu desgosto por paciência e tédio.",
            ],
            "outros_provavelmente": [
                "Confiam em sua coragem e força, e acreditam que você é capaz de se virar sozinho em uma luta.",
                "O veem como incivilizado ou como um indivíduo grosseiro inadequado para a alta sociedade.",
                "Acreditam que você é leal a seus amigos e aliados e que nunca irá ceder antes do fim da luta.",
            ],
        },
        "proficiencias_iniciais": {
            "percepcao": "especialista",
            "salvamentos": {
                "fortitude": "especialista",
                "reflexos": "treinado",
                "vontade": "especialista",
            },
            "pericias": {
                "fixas": ["atletismo"],
                "opcoes_fixas": [],
                "adicionais_base": 3,
                "soma_modificador_inteligencia": True,
                "texto": "Treinado em Atletismo; treinado em uma quantidade de perícias adicionais igual a 3 mais seu modificador de Inteligência.",
            },
            "ataques": {
                "armas_simples": "treinado",
                "armas_marciais": "treinado",
                "ataques_desarmados": "treinado",
            },
            "defesas": {
                "armaduras_leves": "treinado",
                "armaduras_medias": "treinado",
                "defesa_sem_armadura": "treinado",
            },
            "cd_classe": {
                "graduacao": "treinado",
                "texto": "Treinado em CD de classe de bárbaro",
            },
            "magias": None,
        },
        "tabela_progressao": tabela_progressao,
        "tabelas_especificas": {
            "tabela_3_3_instintos_animais": tabela_3_3_instintos_animais,
            "tabela_3_4_instintos_de_dragao": tabela_3_4_instintos_de_dragao,
            "tabela_talentos_indice": tabela_talentos_indice,
        },
        "caracteristicas_de_classe": caracteristicas_de_classe,
        "subclasses": subclasses,
        "termos_chave": termos_chave,
        "exemplos_personagens": exemplos_personagens,
        "talentos_de_classe": talentos,
    }


def construir_bardo() -> dict[str, Any]:
    """Constrói os dados completos da classe Bardo (pp. 94–103)."""
    tabela_progressao = construir_tabela_progressao(
        [
            (1, "Ancestralidade e biografia, conjuração ocultista, magias de composição, musa, proficiências iniciais, repertório de magias"),
            (2, "Talento de bardo, talento de perícia"),
            (3, "Incremento de perícia, magias de 2º nível, magias emblemáticas, reflexos rápidos, talento geral"),
            (4, "Talento de bardo, talento de perícia"),
            (5, "Incremento de perícia, magias de 3º nível, melhorias de atributo, talento de ancestralidade"),
            (6, "Talento de bardo, talento de perícia"),
            (7, "Conjurador especialista, incremento de perícia, magias de 4º nível, talento geral"),
            (8, "Talento de bardo, talento de perícia"),
            (9, "Determinação, grande fortitude, incremento de perícia, magias de 5º nível, talento de ancestralidade"),
            (10, "Melhorias de atributo, talento de bardo, talento de perícia"),
            (11, "Especialidade em armas de bardo, incremento de perícia, magias de 6º nível, sentidos vigilantes, talento geral"),
            (12, "Talento de bardo, talento de perícia"),
            (13, "Especialidade em armaduras leves, especialização em armas, incremento de perícia, magias de 7º nível, talento de ancestralidade"),
            (14, "Talento de bardo, talento de perícia"),
            (15, "Conjurador mestre, incremento de perícia, magias de 8º nível, melhorias de atributo, talento geral"),
            (16, "Talento de bardo, talento de perícia"),
            (17, "Determinação maior, incremento de perícia, magias de 9º nível, talento de ancestralidade"),
            (18, "Talento de bardo, talento de perícia"),
            (19, "Conjurador lendário, incremento de perícia, magnum opus, talento geral"),
            (20, "Melhorias de atributo, talento de bardo, talento de perícia"),
        ]
    )

    tabela_3_6_magias_por_dia: list[dict[str, Any]] = []
    for nivel in range(1, 21):
        espacos: dict[str, int] = {}
        for circulo in range(1, 10):
            nivel_desbloqueio = (circulo - 1) * 2 + 1
            if nivel == nivel_desbloqueio:
                espacos[str(circulo)] = 2
            elif nivel > nivel_desbloqueio:
                espacos[str(circulo)] = 3
        if nivel >= 19:
            espacos["10"] = 1
        tabela_3_6_magias_por_dia.append(
            {
                "nivel": nivel,
                "truques_magicos": 5,
                "espacos_por_circulo": espacos,
                "nota_10_nivel": (
                    "A característica de classe magnum opus lhe concede um espaço de magia de 10º nível que funciona diferente dos outros espaços de magia."
                    if nivel >= 19
                    else None
                ),
            }
        )

    tabela_talentos_indice = [
        {"nome": "Allegro", "nivel": 14},
        {"nome": "Ária Fatal", "nivel": 20},
        {"nome": "Balada Tranquilizante", "nivel": 14},
        {"nome": "Bis Perfeito", "nivel": 20},
        {"nome": "Capacidade de Estudo", "nivel": 16},
        {"nome": "Casa das Paredes Imaginárias", "nivel": 10},
        {"nome": "Composição Eterna", "nivel": 18},
        {"nome": "Composição Inusitada", "nivel": 10},
        {"nome": "Composição Prolongada", "nivel": 1},
        {"nome": "Concentração Sem Esforço", "nivel": 16},
        {"nome": "Conjuração Acelerada", "nivel": 10},
        {"nome": "Conjuração Consistente", "nivel": 6},
        {"nome": "Erudição Profunda", "nivel": 18},
        {"nome": "Étude do Mestre do Saber", "nivel": 2},
        {"nome": "Expansão de Truque Mágico", "nivel": 2},
        {"nome": "Foco Inspirador", "nivel": 12},
        {"nome": "Harmonizar", "nivel": 6},
        {"nome": "Hipercognição Verdadeira", "nivel": 14},
        {"nome": "Inspirar Competência", "nivel": 2},
        {"nome": "Inspirar Defesa", "nivel": 4},
        {"nome": "Inspirar Heroísmo", "nivel": 8},
        {"nome": "Lamento da Condenação", "nivel": 6},
        {"nome": "Magia de Alcance", "nivel": 1},
        {"nome": "Magia Melodiosa", "nivel": 4},
        {"nome": "Musa Multifacetada", "nivel": 2},
        {"nome": "Performance Versátil", "nivel": 1},
        {"nome": "Perícia Eclética", "nivel": 8},
        {"nome": "Polímata Eclético", "nivel": 12},
        {"nome": "Polímata Esotérico", "nivel": 2},
        {"nome": "Polímata Impossível", "nivel": 18},
        {"nome": "Saber Bárdico", "nivel": 1},
        {"nome": "Sabe-Tudo", "nivel": 8},
        {"nome": "Sinfonia da Musa", "nivel": 20},
        {"nome": "Tempo Triplo", "nivel": 4},
        {"nome": "Versatilidade Emblemática", "nivel": 4},
    ]

    caracteristicas_de_classe = [
        construir_caracteristica_classe(
            "Ancestralidade e Biografia",
            1,
            "Além das habilidades fornecidas por sua classe no 1º nível, você possui os benefícios da ancestralidade e biografia selecionadas, conforme descrito no Capítulo 2.",
        ),
        construir_caracteristica_classe(
            "Proficiências Iniciais",
            1,
            "No 1º nível, você recebe proficiências que representam seu treinamento básico, listadas no início desta classe.",
        ),
        construir_caracteristica_classe(
            "Conjuração Ocultista",
            1,
            (
                "Você pode conjurar magias ocultistas usando a atividade Conjurar uma Magia e providenciar componentes materiais, somáticos e verbais (página 302). "
                "Por ser um bardo, normalmente você pode tocar um instrumento para magias que exijam componentes materiais ou somáticos (usando ao menos uma mão, sem precisar de bolsa de componentes ou outra mão livre), "
                "e também pode tocar um instrumento como componente verbal em vez de falar. "
                "No 1º nível você tem dois espaços de magia de 1º nível e cinco truques mágicos (Tabela 3–6). "
                "Seu atributo chave é Carisma para ataques de magia e CDs de magias. Truques mágicos são automaticamente elevados à metade do nível arredondada para cima."
            ),
        ),
        construir_caracteristica_classe(
            "Repertório de Magias",
            1,
            (
                "No 1º nível, você aprende duas magias ocultistas de 1º nível e cinco truques mágicos ocultistas à sua escolha (página 311). "
                "Para cada espaço de magia recebido ao avançar de nível (Tabela 3–6), você adiciona uma magia do mesmo nível ao seu repertório. "
                "Cada vez que ganhar um nível e aprender novas magias, pode trocar uma magia antiga por outra diferente do mesmo nível (inclusive truques mágicos)."
            ),
            detalhes={"magias_1_nivel_iniciais": 2, "truques_iniciais": 5},
        ),
        construir_caracteristica_classe(
            "Magias de Composição",
            1,
            (
                "Você infunde suas performances com magia para criar composições, um tipo especial de magia de foco. "
                "Você adquire uma reserva de foco com 1 Ponto de Foco (máximo 3 Pontos de Foco; recupera 1 ponto com 10 minutos usando Refocar). "
                "Magias de foco são automaticamente elevadas à metade de seu nível arredondada para cima. "
                "Você aprende a magia de composição contraperformance (página 386) e o truque mágico de composição inspirar coragem (página 387), "
                "que não custa Pontos de Foco."
            ),
            detalhes={
                "reserva_foco_inicial": 1,
                "magia_composicao_inicial": "contraperformance",
                "truque_composicao_inicial": "inspirar coragem",
            },
        ),
        construir_caracteristica_classe(
            "Musa",
            1,
            "Você seleciona uma musa no 1º nível: Enigma, Maestro ou Polímata.",
        ),
        construir_caracteristica_classe(
            "Talentos de Bardo",
            2,
            "No 2º nível e a cada nível par subsequente, você recebe um talento de classe de bardo.",
        ),
        construir_caracteristica_classe(
            "Talentos de Perícia",
            2,
            "No 2º nível e a cada 2 níveis subsequentes, você recebe um talento de perícia (Capítulo 5).",
        ),
        construir_caracteristica_classe(
            "Incrementos de Perícia",
            3,
            "No 3º nível e a cada 2 níveis subsequentes, você recebe um incremento de perícia (mestre a partir do 7º nível, lendário a partir do 15º nível).",
        ),
        construir_caracteristica_classe(
            "Magias Emblemáticas",
            3,
            (
                "Para cada nível de magia que tiver acesso, escolha uma magia desse nível como uma magia emblemática. "
                "Você pode elevar essas magias livremente sem precisar aprender versões elevadas separadamente (ou conjurar suas versões de níveis inferiores)."
            ),
        ),
        construir_caracteristica_classe(
            "Talentos Gerais",
            3,
            "No 3º nível e a cada 4 níveis subsequentes, você recebe um talento geral (Capítulo 5).",
        ),
        construir_caracteristica_classe(
            "Reflexos Rápidos",
            3,
            "Sua graduação de proficiência em salvamentos de Reflexos aumenta para especialista.",
        ),
        construir_caracteristica_classe(
            "Melhorias de Atributo",
            5,
            "No 5º nível e a cada 5 níveis subsequentes, você melhora os valores de quatro atributos diferentes (+1 se >= 18, +2 se < 18).",
        ),
        construir_caracteristica_classe(
            "Talentos de Ancestralidade",
            5,
            "Você recebe um talento de ancestralidade no 5º nível e a cada 4 níveis subsequentes.",
        ),
        construir_caracteristica_classe(
            "Conjurador Especialista",
            7,
            "Suas graduações de proficiência em ataques de magia e CDs de magias ocultistas aumentam para especialista.",
        ),
        construir_caracteristica_classe(
            "Determinação",
            9,
            "Sua graduação de proficiência em salvamentos de Vontade aumenta para mestre. Quando rolar um sucesso em um salvamento de Vontade, trate o resultado como um sucesso crítico.",
        ),
        construir_caracteristica_classe(
            "Grande Fortitude",
            9,
            "Sua graduação de proficiência em salvamentos de Fortitude aumenta para especialista.",
        ),
        construir_caracteristica_classe(
            "Especialidade em Armas de Bardo",
            11,
            (
                "Suas graduações de proficiência em armas simples, arco curto, chicote, espada curta, espada longa, porrete, rapieira e ataques desarmados aumentam para especialista. "
                "Quando obtiver um sucesso crítico em uma rolagem de ataque usando uma destas armas enquanto uma de suas composições estiver ativa, você aplica o efeito de especialização de crítico da arma."
            ),
        ),
        construir_caracteristica_classe(
            "Sentidos Vigilantes",
            11,
            "Sua graduação de proficiência em Percepção aumenta para mestre.",
        ),
        construir_caracteristica_classe(
            "Especialidade em Armaduras Leves",
            13,
            "Suas graduações de proficiência em armaduras leves e defesa sem armadura aumentam para especialista.",
        ),
        construir_caracteristica_classe(
            "Especialização em Armas",
            13,
            "Você causa 2 pontos de dano adicionais com armas e ataques desarmados nos quais é especialista (3 se mestre, 4 se lendário).",
        ),
        construir_caracteristica_classe(
            "Conjurador Mestre",
            15,
            "Suas graduações de proficiência em ataques de magia e CDs de magias ocultistas aumentam para mestre.",
        ),
        construir_caracteristica_classe(
            "Determinação Maior",
            17,
            (
                "Sua graduação de proficiência em salvamentos de Vontade aumenta para lendário. "
                "Quando rolar um sucesso em um salvamento de Vontade, trate como sucesso crítico; falha crítica como falha; "
                "e falha contra efeito que cause dano divide o dano pela metade."
            ),
        ),
        construir_caracteristica_classe(
            "Conjurador Lendário",
            19,
            "Suas graduações de proficiência em ataques de magia e CDs de magias ocultistas aumentam para lendário.",
        ),
        construir_caracteristica_classe(
            "Magnum Opus",
            19,
            (
                "Adicione duas magias ocultistas comuns de 10º nível ao seu repertório de magias. "
                "Você recebe um único espaço de magia de 10º nível que pode ser usado para conjurar uma dessas duas magias (não acumula com outros bônus de espaço; pode selecionar Bis Perfeito para um segundo espaço)."
            ),
        ),
    ]

    subclasses = {
        "tipo": "musa",
        "nome_tipo": "Musa",
        "opcoes": [
            {
                "id": "enigma",
                "nome": "Enigma",
                "descricao": "Sua musa é um mistério, levando-o a descobrir os segredos escondidos do multiverso (ex.: dragão, ser transcendental/extraterreno, Irori ou Nethys).",
                "talento_concedido": "Saber Bárdico",
                "magia_adicionada_repertorio": "golpe certo",
            },
            {
                "id": "maestro",
                "nome": "Maestro",
                "descricao": "Sua musa é um virtuoso artístico, inspirando-o a maiores alturas (ex.: anjo corista, azata lillend ou Shelyn).",
                "talento_concedido": "Composição Prolongada",
                "magia_adicionada_repertorio": "abrandar",
            },
            {
                "id": "polimata",
                "nome": "Polímata",
                "descricao": "Sua musa é um faz-tudo, esvoaçando entre diferentes buscas e competências (ex.: fada, Desna ou Calístria).",
                "talento_concedido": "Performance Versátil",
                "magia_adicionada_repertorio": "servo invisível",
            },
        ],
    }

    termos_chave = [
        {
            "termo": "Composição",
            "descricao": (
                "Para conjurar uma magia de foco ou um truque mágico de composição, você usa um tipo de Performance (página 251). "
                "Se incluir componente verbal, usa performance auditiva; se incluir componente somático, usa performance visual. "
                "A magia adquire todos os traços da performance usada. Você pode conjurar apenas uma magia de composição a cada turno e ter apenas uma ativa ao mesmo tempo; "
                "conjurar uma nova composição encerra imediatamente os efeitos contínuos da anterior."
            ),
        },
        {
            "termo": "Metamágico",
            "descricao": (
                "Ações com esse traço alteram as propriedades de suas magias. Você deve usar uma ação metamágica logo antes de Conjurar a Magia que deseja alterar; "
                "qualquer outra ação (inclusive livres e reações) desperdiça o benefício. Efeitos acrescentados são parte do efeito da magia."
            ),
        },
    ]

    exemplos_personagens = [
        {
            "nome": "Dançarino",
            "pagina": 102,
            "resumo": "Através de uma miríade de estilos de dança, você inspira seus aliados e canaliza magia transcendental.",
            "atributos": "Faça do Carisma seu maior atributo, seguido por Destreza. Aumente a Constituição para ganhar mais saúde e Inteligência para mais perícias.",
            "pericias": ["Acrobatismo", "Atletismo", "Diplomacia", "Medicina", "Ocultismo", "Performance"],
            "subclasse": "Maestro",
            "talentos_niveis_superiores": [
                "Inspirar Competência (2º)",
                "Tempo Triplo (4º)",
                "Allegro (14º)",
            ],
            "repertorio_magias": {
                "1_nivel": ["abrandar", "disfarce ilusório", "leque de cores"],
                "truques_magicos": ["detectar magia", "ler aura", "luz", "mão mística", "som fantasma"],
            },
        }
    ]

    talentos = [
        # 1º NÍVEL (4)
        construir_talento_classe(
            "Composição Prolongada",
            1,
            ["Bardo"],
            "Ao acrescentar um floreio, você faz suas composições durarem mais. Você aprende a magia de foco composição prolongada (página 386). Aumente em 1 a quantidade de Pontos de Foco em sua reserva de foco.",
            pre_requisitos="musa maestro, reserva de foco",
        ),
        construir_talento_classe(
            "Magia de Alcance",
            1,
            ["Bardo", "Concentração", "Metamágico"],
            "Você amplia a distância de sua magia. Se a próxima ação que você usar for Conjurar uma Magia que possui uma distância, aumente a distância dessa magia em 9 metros. Como padrão para aumentar distâncias de magias, se a magia normalmente tiver uma distância de toque, você amplia a distância dela para 9 metros.",
            acoes="1",
        ),
        construir_talento_classe(
            "Performance Versátil",
            1,
            ["Bardo"],
            "Você confia na grandeza de suas performances em vez de perícias sociais convencionais. Você pode utilizar Performance em vez de Diplomacia para Impressionar e no lugar de Intimidação para Desmoralizar. Você também pode utilizar uma Performance de atuação em vez de Dissimulação para Personificar. Você pode utilizar sua graduação de proficiência em Performance para atender aos requerimentos de talentos de perícia que exijam uma graduação específica em Diplomacia, Dissimulação ou Intimidação.",
            pre_requisitos="musa polímata",
        ),
        construir_talento_classe(
            "Saber Bárdico",
            1,
            ["Bardo"],
            "Seus estudos o tornam informado sobre qualquer assunto. Você é treinado em Saber Bárdico, uma perícia de Saber especial que pode ser utilizada apenas para Recordar Conhecimento (embora possa recordar sobre qualquer tópico). Se tiver proficiência lendária em Ocultismo, você recebe proficiência de especialista em Saber Bárdico, mas a sua graduação de proficiência em Saber Bárdico não pode ser aumentada de nenhuma outra forma.",
            pre_requisitos="musa enigma",
        ),
        # 2º NÍVEL (5)
        construir_talento_classe(
            "Étude do Mestre do Saber",
            2,
            ["Bardo", "Fortuna"],
            "Você desbloqueia memórias magicamente, tornando-as mais fáceis de recordar. Você aprende a magia de composição étude do mestre do saber (página 386). Aumente em 1 a quantidade de Pontos de Foco em sua reserva de foco.",
            pre_requisitos="musa enigma, reserva de foco",
        ),
        construir_talento_classe(
            "Expansão de Truque Mágico",
            2,
            ["Bardo"],
            "O estudo aumenta sua gama de magias simples. Adicione dois truques mágicos de sua lista de magias ao seu repertório de magias.",
        ),
        construir_talento_classe(
            "Inspirar Competência",
            2,
            ["Bardo"],
            "Você aprende o truque mágico de composição inspirar competência (página 386), que ajuda os seus aliados a usarem suas perícias.",
            pre_requisitos="musa maestro",
        ),
        construir_talento_classe(
            "Musa Multifacetada",
            2,
            ["Bardo"],
            "Sua musa não se enquadra em um único rótulo. Escolha um tipo de musa diferente da sua. Você recebe um talento de 1º nível que requeira essa musa, e sua musa agora também é considerada uma musa desse tipo, permitindo-lhe selecionar talentos que tenham essa outra musa como pré-requisito. Você não recebe nenhum dos outros efeitos da musa escolhida.",
            especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você deve escolher uma musa diferente da sua.",
        ),
        construir_talento_classe(
            "Polímata Esotérico",
            2,
            ["Bardo"],
            "Você mantém um livro de magias ocultistas, similar ao grimório de um mago, e pode usar essas magias para suplementar seu repertório de magias. Adicione todas as magias de seu repertório a este livro sem custos. Você pode utilizar a perícia Ocultismo para Aprender Magias (página 234) e adicioná-las ao seu grimório pagando o custo apropriado, da mesma forma que um mago o faria. Durante suas preparações diárias, escolha qualquer magia de seu livro de magias ocultistas. Se essa magia já estiver em seu repertório de magias, você pode tratá-la como uma magia emblemática adicional durante esse dia. Se ela não estiver em seu repertório, trate-a como se estivesse até realizar suas próximas preparações diárias.",
            pre_requisitos="musa polímata",
        ),
        # 4º NÍVEL (4)
        construir_talento_classe(
            "Inspirar Defesa",
            4,
            ["Bardo"],
            "Você aprende o truque mágico de composição inspirar defesa (página 387), que protege seus aliados.",
            pre_requisitos="musa maestro",
        ),
        construir_talento_classe(
            "Magia Melodiosa",
            4,
            ["Bardo", "Concentração", "Manuseio", "Metamágico"],
            "Você entrelaça sutilmente uma conjuração de magia em sua performance. Se a sua próxima ação for Conjurar uma Magia, faça um teste de Performance contra as CDs de Percepção de todos os observadores. Se você obtiver sucesso em seu teste contra a CD de um observador, ele não percebe que você está Conjurando uma Magia — mesmo que ela normalmente tenha manifestações sensoriais e componentes materiais, somáticos e verbais extremamente evidentes e que tornariam a conjuração óbvia para aqueles ao seu redor. Você esconde tudo isto como parte de uma performance ordinária. Esta habilidade esconde apenas as ações de conjuração e manifestações da magia, mas não seus efeitos. Portanto, um observador ainda verá um raio saindo de você ou perceberá que você desapareceu.",
            acoes="1",
        ),
        construir_talento_classe(
            "Tempo Triplo",
            4,
            ["Bardo"],
            "Você aprende o truque mágico de composição tempo triplo (página 387), que acelera você e seus aliados por uma rodada.",
        ),
        construir_talento_classe(
            "Versatilidade Emblemática",
            4,
            ["Bardo"],
            "Embora a maioria dos bardos seja conhecida por determinadas performances e magias emblemáticas, você está sempre mudando seu repertório disponível. Quando fizer suas preparações diárias, você pode trocar uma de suas magias emblemáticas por uma magia diferente desse nível que esteja em seu repertório.",
            pre_requisitos="musa polímata",
        ),
        # 6º NÍVEL (3)
        construir_talento_classe(
            "Conjuração Consistente",
            6,
            ["Bardo"],
            "Confiante em sua técnica, você não perde a concentração facilmente quando Conjura uma Magia. Se uma reação fosse interromper sua ação de conjuração, faça um teste simples CD 15. Se obtiver sucesso, sua ação não é interrompida.",
        ),
        construir_talento_classe(
            "Harmonizar",
            6,
            ["Bardo", "Concentração", "Manuseio", "Metamágico"],
            "Você pode executar múltiplas composições simultaneamente. Se a sua próxima ação for conjurar uma composição, ela se torna uma composição harmonizada. Ao contrário de uma composição normal, uma composição harmonizada não se encerra se você conjurar outra composição, e você pode conjurar outra composição no mesmo turno em que conjurar uma composição harmonizada. Conjurar outra composição harmonizada encerra qualquer composição harmonizada que você tenha em efeito.",
            acoes="1",
            pre_requisitos="musa maestro",
        ),
        construir_talento_classe(
            "Lamento da Condenação",
            6,
            ["Bardo"],
            "Você aprende o truque mágico de composição lamento da condenação (página 387), que assusta seus inimigos.",
        ),
        # 8º NÍVEL (3)
        construir_talento_classe(
            "Inspirar Heroísmo",
            8,
            ["Bardo"],
            "Suas performances inspiram seus aliados a alcançar feitos ainda maiores. Você aprende a magia de foco metamágica inspirar heroísmo (página 387). Aumente em 1 a quantidade de Pontos de Foco em sua reserva de foco.",
            pre_requisitos="musa maestro, reserva de foco",
        ),
        construir_talento_classe(
            "Perícia Eclética",
            8,
            ["Bardo"],
            "Sua ampla experiência se traduz em uma variedade de perícias. Seu bônus de proficiência para testes de perícia destreinados é igual ao seu nível. Você pode realizar qualquer teste de perícia que normalmente requeira um nível de proficiência treinado, mesmo que seja destreinado. Se possuir proficiência lendária em Ocultismo, você pode realizar qualquer teste de perícia que normalmente requeira proficiência de especialista, seja você destreinado ou treinado.",
            pre_requisitos="musa polímata, mestre em Ocultismo",
        ),
        construir_talento_classe(
            "Sabe-Tudo",
            8,
            ["Bardo"],
            "Quando obtiver sucesso em um teste de Recordar Conhecimento, você recebe contexto ou informações adicionais. Quando obtiver um sucesso crítico em um teste de Recordar Conhecimento, a critério do MJ, você pode receber ainda mais contexto ou informações adicionais que o normal.",
            pre_requisitos="musa enigma",
        ),
        # 10º NÍVEL (3)
        construir_talento_classe(
            "Casa das Paredes Imaginárias",
            10,
            ["Bardo"],
            "Você ergue uma barreira imaginária que outros acreditam ser real. Você aprende o truque mágico de composição casa das paredes imaginárias (página 386).",
        ),
        construir_talento_classe(
            "Composição Inusitada",
            10,
            ["Bardo", "Manuseio", "Concentração", "Metamágico"],
            "Você pode traduzir a emoção e poder de uma composição para outros meios. Se a sua próxima ação for conjurar uma magia de composição, você pode usar um tipo diferente de performance do que o normal para a composição assim trocando quaisquer de seus componentes somáticos para componentes verbais (ou vice-versa). Como normal para magias de composição, esta troca muda se a composição é auditiva ou visual.",
            acoes="1",
            pre_requisitos="musa polímata",
        ),
        construir_talento_classe(
            "Conjuração Acelerada",
            10,
            ["Bardo", "Concentração", "Metamágico"],
            "Se a sua próxima ação for conjurar um truque mágico ou magia de bardo que seja pelo menos 2 níveis inferior ao maior nível de magia de bardo que você possa conjurar, reduza em 1 a quantidade de ações para conjurá-la (mínimo de 1 ação).",
            acoes="livre",
            frequencia="uma vez por dia",
        ),
        # 12º NÍVEL (2)
        construir_talento_classe(
            "Foco Inspirador",
            12,
            ["Bardo"],
            "Sua forte conexão à sua musa lhe garantiu um foco inusitado. Se tiver gastado pelo menos 2 Pontos de Foco desde a última vez que Refocou, você recupera 2 Pontos de Foco ao Refocar (em vez de recuperar somente 1 ponto).",
        ),
        construir_talento_classe(
            "Polímata Eclético",
            12,
            ["Bardo"],
            "Sua mente flexível pode rapidamente mudar magias. Se adicionar uma magia ao seu repertório durante suas preparações diárias usando Polímata Esotérico, você pode manter essa magia em seu repertório na sua próxima preparação diária, perdendo acesso a outra magia de seu repertório do mesmo nível.",
            pre_requisitos="Polímata Esotérico",
        ),
        # 14º NÍVEL (3)
        construir_talento_classe(
            "Allegro",
            14,
            ["Bardo"],
            "Você pode acelerar seus aliados com uma performance de ritmo apressado. Você aprende o truque mágico de composição allegro (página 386).",
        ),
        construir_talento_classe(
            "Balada Tranquilizante",
            14,
            ["Bardo"],
            "Você abranda os ferimentos de seus aliados com o poder de sua performance. Você aprende a magia de composição balada tranquilizante (página 386). Aumente em 1 a quantidade de Pontos de Foco em sua reserva de foco.",
            pre_requisitos="reserva de foco",
        ),
        construir_talento_classe(
            "Hipercognição Verdadeira",
            14,
            ["Bardo"],
            "Sua mente funciona em um ritmo incrível. Você instantaneamente usa até cinco ações de Recordar Conhecimento. Se possuir quaisquer habilidades especiais ou ações livres que normalmente seriam acionadas ao Recordar Conhecimento, você não pode usá-las para estas ações.",
            acoes="1",
            pre_requisitos="musa enigma",
        ),
        # 16º NÍVEL (2)
        construir_talento_classe(
            "Capacidade de Estudo",
            16,
            ["Bardo"],
            "Seu estudo contínuo de magia ocultista aumentou sua capacidade mágica, permitindo-lhe conjurar magias mesmo quando parece impossível. Você pode conjurar uma magia por dia após ter gastado todos seus espaços de magia do nível de magia apropriado. Esta habilidade, porém, não pode ser usada para conjurar uma magia de seu maior nível de magia.",
            pre_requisitos="musa enigma, lendário em Ocultismo",
        ),
        construir_talento_classe(
            "Concentração Sem Esforço",
            16,
            ["Bardo"],
            "Você pode sustentar uma magia com pouco mais do que um pensamento. Você imediatamente recebe os efeitos da ação Sustentar uma Magia, permitindo-lhe prolongar a duração de uma de suas magias de bardo ativas.",
            acoes="livre",
            pre_requisitos="Seu turno começa.",
        ),
        # 18º NÍVEL (3)
        construir_talento_classe(
            "Composição Eterna",
            18,
            ["Bardo"],
            "O mundo é um palco e você sempre está nos holofotes. Você se torna permanentemente acelerado e pode usar sua ação extra somente para conjurar um truque mágico de composição que requeira 1 ação para ser conjurado. Enquanto estiver no modo de exploração, você pode declarar que está executando um truque mágico de composição elegível enquanto usar qualquer tática de exploração. Mesmo antes de seu primeiro turno em um encontro de combate, esse truque mágico está ativo como se você o tivesse conjurado no turno anterior.",
            pre_requisitos="musa maestro",
        ),
        construir_talento_classe(
            "Erudição Profunda",
            18,
            ["Bardo"],
            "Seu repertório é vasto, contendo muito mais magias do que o normal. Adicione uma magia de cada nível que puder conjurar ao seu repertório de magias.",
            pre_requisitos="musa enigma, lendário em Ocultismo",
        ),
        construir_talento_classe(
            "Polímata Impossível",
            18,
            ["Bardo"],
            "Suas fórmulas esotéricas são tão inusitadas que permitem que você se arrisque na magia de tradições diversas não compreendidas por outros bardos. Se for treinado em Arcanismo, você pode adicionar magias arcanas ao seu grimório de Polímata Esotérico; se for treinado em Natureza, você pode adicionar magias primais ao seu grimório e; se for treinado em Religião, você pode adicionar magias divinas ao seu grimório. Como as outras magias em seu grimório, você pode usar Polímata Esotérico para adicionar uma destas magias de outra tradição ao seu repertório de magias como uma magia ocultista a cada dia, mas não pode reter quaisquer magias de outra tradição quando fizer suas preparações novamente (mesmo que possua Polímata Eclético).",
            pre_requisitos="treinado em Arcanismo, Natureza ou Religião; Polímata Esotérico",
        ),
        # 20º NÍVEL (3)
        construir_talento_classe(
            "Ária Fatal",
            20,
            ["Bardo"],
            "Suas magias esmagam o alvo com emoções insuportáveis, potencialmente matando-o imediatamente. Você aprende a magia de composição ária fatal (página 386). Aumente em 1 a quantidade de Pontos de Foco em sua reserva de foco.",
            pre_requisitos="reserva de foco",
        ),
        construir_talento_classe(
            "Bis Perfeito",
            20,
            ["Bardo"],
            "Você desenvolve outra criação incrível. Você recebe um espaço de magia adicional de 10º nível.",
            pre_requisitos="magnum opus",
        ),
        construir_talento_classe(
            "Sinfonia da Musa",
            20,
            ["Bardo"],
            "Você consegue entrelaçar performances incontáveis formando uma única sinfonia. Você não é mais limitado a uma única composição por turno ou uma única composição ao mesmo tempo; quando usar uma nova composição, os efeitos de todas as composições prévias continuam normalmente por sua duração remanescente.",
            pre_requisitos="Harmonizar",
        ),
    ]

    return {
        "id": "bardo",
        "nome": "Bardo",
        "paginas": "94-103",
        "descricao": (
            "Você é um mestre das artes, um estudioso de segredos escondidos e um persuasor cativante. "
            "Usando performances poderosas, você influencia mentes e eleva almas a novos níveis de heroísmo. "
            "Você pode usar seus poderes para se tornar um líder carismático, ou talvez possa ser um conselheiro, estudioso, malandro, manipulador ou virtuoso. "
            "A sua versatilidade faz com que alguns o vejam como um faz-tudo ou vadio irresponsável — mas menosprezá-lo como um mestre de nada é algo muito, muito perigoso."
        ),
        "atributo_chave": {
            "opcoes": ["carisma"],
            "melhoria_1_nivel": 2,
            "texto": "Carisma — No 1º nível, sua classe lhe concede uma melhoria de atributo em Carisma.",
        },
        "pontos_de_vida_por_nivel": 8,
        "pontos_de_vida_texto": "8 mais seu modificador de Constituição no 1º nível e a cada nível subsequente.",
        "jogando_com_a_classe": {
            "encontros_combate": "Você usa performances mágicas para manipular a sorte a favor de seus aliados. Você alterna confiantemente entre ataques, cura e magias de suporte conforme necessário.",
            "encontros_sociais": "Você persuade, mente, ofusca e ameaça com facilidade.",
            "exploracao": "Você é uma fonte de conhecimento, contos populares, lendas e saberes que fornecem um contexto profundo e reconhecimento útil às aventuras do grupo. Suas magias e performances inspiram seus aliados a grandes descobertas e sucessos.",
            "recesso": "Você pode ganhar dinheiro e prestígio com suas performances, fazer seu nome e adquirir patrocinadores. Em algum momento, contos de seus talentos e triunfos podem atrair outros bardos a estudarem suas técnicas em um colégio bárdico.",
            "voce_pode": [
                "Ter uma paixão tão forte por sua arte que forja uma conexão espiritual com ela.",
                "Tomar a frente quando a situação demanda soluções não-violentas e tato social.",
                "Seguir sua musa, seja ela uma criatura feérica, um conceito filosófico, uma força psíquica ou uma divindade das artes ou da música, e com a sua ajuda alcançar saberes secretos que poucos possuem.",
            ],
            "outros_provavelmente": [
                "Não perdem uma oportunidade de convidá-lo para eventos sociais, seja como centro do espetáculo ou convidado, mas ainda lhe consideram uma curiosidade em seus círculos sociais.",
                "O subestimam em comparação a outros conjuradores, acreditando que você é pouco mais do que um menestrel presunçoso e não dando atenção ao poder sutil de sua magia.",
                "Respondem favoravelmente ao seu charme e habilidades sociais, embora permaneçam suspeitos de sua magia mental.",
            ],
        },
        "proficiencias_iniciais": {
            "percepcao": "especialista",
            "salvamentos": {
                "fortitude": "treinado",
                "reflexos": "treinado",
                "vontade": "especialista",
            },
            "pericias": {
                "fixas": ["ocultismo", "performance"],
                "opcoes_fixas": [],
                "adicionais_base": 4,
                "soma_modificador_inteligencia": True,
                "texto": "Treinado em Ocultismo; treinado em Performance; treinado em uma quantidade de perícias adicionais igual a 4 mais seu modificador de Inteligência.",
            },
            "ataques": {
                "armas_simples": "treinado",
                "armas_especificas": {
                    "graduacao": "treinado",
                    "armas": ["arco curto", "chicote", "espada curta", "espada longa", "porrete", "rapieira"],
                },
                "ataques_desarmados": "treinado",
            },
            "defesas": {
                "armaduras_leves": "treinado",
                "defesa_sem_armadura": "treinado",
            },
            "cd_classe": None,
            "magias": {
                "tradicao": "ocultista",
                "tipo_conjuracao": "espontanea",
                "ataques_magia": "treinado",
                "cds_magia": "treinado",
                "atributo_conjuracao": "carisma",
                "texto": "Treinado em ataques de magias ocultistas; treinado em CDs de magias ocultistas.",
            },
        },
        "tabela_progressao": tabela_progressao,
        "tabelas_especificas": {
            "tabela_3_6_magias_por_dia": tabela_3_6_magias_por_dia,
            "tabela_talentos_indice": tabela_talentos_indice,
        },
        "caracteristicas_de_classe": caracteristicas_de_classe,
        "subclasses": subclasses,
        "termos_chave": termos_chave,
        "exemplos_personagens": exemplos_personagens,
        "talentos_de_classe": talentos,
    }


def construir_campeao() -> dict[str, Any]:
    """Constrói os dados completos da classe Campeão (pp. 104–115)."""
    tabela_progressao = construir_tabela_progressao(
        [
            (1, "Ancestralidade e biografia, arma deificada, bloqueio com escudo, código de campeão, divindade e causa, magias de devoção, proficiências iniciais, reação de campeão, talento de campeão"),
            (2, "Talento de campeão, talento de perícia"),
            (3, "Aliado divino, incremento de perícia, talento geral"),
            (4, "Talento de campeão, talento de perícia"),
            (5, "Especialidade em armas, incremento de perícia, melhorias de atributo, talento de ancestralidade"),
            (6, "Talento de campeão, talento de perícia"),
            (7, "Especialidade em armaduras, especialização em armas, incremento de perícia, talento geral"),
            (8, "Talento de campeão, talento de perícia"),
            (9, "Especialidade de campeão, incremento de perícia, irrefreável, punição divina, reflexos rápidos, talento de ancestralidade"),
            (10, "Melhorias de atributo, talento de campeão, talento de perícia"),
            (11, "Exaltação, incremento de perícia, prontidão, talento geral, vontade divina"),
            (12, "Talento de campeão, talento de perícia"),
            (13, "Incremento de perícia, maestria em armaduras, maestria em armas, talento de ancestralidade"),
            (14, "Talento de campeão, talento de perícia"),
            (15, "Especialização em armas maior, incremento de perícia, melhorias de atributo, talento geral"),
            (16, "Talento de campeão, talento de perícia"),
            (17, "Incremento de perícia, lenda de armaduras, maestria de campeão, talento de ancestralidade"),
            (18, "Talento de campeão, talento de perícia"),
            (19, "Desafio do herói, incremento de perícia, talento geral"),
            (20, "Melhorias de atributo, talento de campeão, talento de perícia"),
        ]
    )

    tabela_talentos_indice = [
        {"nome": "Andar Liberador", "nivel": 12},
        {"nome": "Ataque de Oportunidade", "nivel": 6},
        {"nome": "Aura de Ancoragem", "nivel": 14},
        {"nome": "Aura de Coragem", "nivel": 4},
        {"nome": "Aura de Fé", "nivel": 12},
        {"nome": "Aura de Retidão", "nivel": 14},
        {"nome": "Aura de Ruína das Serpes", "nivel": 14},
        {"nome": "Aura de Vida", "nivel": 14},
        {"nome": "Aura de Vingança", "nivel": 14},
        {"nome": "Bloqueio Rápido", "nivel": 8},
        {"nome": "Cavalo de Guerra Leal", "nivel": 6},
        {"nome": "Corcel Imponente", "nivel": 10},
        {"nome": "Curar Montaria", "nivel": 8},
        {"nome": "Domínio de Divindade", "nivel": 1},
        {"nome": "Domínio de Divindade Avançado", "nivel": 8},
        {"nome": "Dúvida Persistente", "nivel": 12},
        {"nome": "Escudeiro Exemplar", "nivel": 20},
        {"nome": "Escudo da Graça", "nivel": 16},
        {"nome": "Escudo da Retribuição", "nivel": 10},
        {"nome": "Espírito da Lâmina Radiante", "nivel": 10},
        {"nome": "Foco Devotado", "nivel": 10},
        {"nome": "Forma Celestial", "nivel": 18},
        {"nome": "Graça Divina", "nivel": 2},
        {"nome": "Guardião de Escudo", "nivel": 6},
        {"nome": "Instrumento de Fervor", "nivel": 16},
        {"nome": "Juramento do Matador de Dragões", "nivel": 2},
        {"nome": "Juramento Reluzente", "nivel": 2},
        {"nome": "Juramento de Ruína dos Ínferos", "nivel": 2},
        {"nome": "Juramento Vingativo", "nivel": 2},
        {"nome": "Lâmina da Justiça", "nivel": 12},
        {"nome": "Litania Contra Ira", "nivel": 6},
        {"nome": "Litania Contra Preguiça", "nivel": 10},
        {"nome": "Litania de Retidão", "nivel": 14},
        {"nome": "Mestre da Lâmina Radiante", "nivel": 20},
        {"nome": "Misericórdia", "nivel": 4},
        {"nome": "Misericórdia de Aflição", "nivel": 12},
        {"nome": "Misericórdia Definitiva", "nivel": 18},
        {"nome": "Misericórdia Maior", "nivel": 8},
        {"nome": "Montaria Auspiciosa", "nivel": 16},
        {"nome": "Montaria Celestial", "nivel": 20},
        {"nome": "Muralha Divina", "nivel": 12},
        {"nome": "Passo Desimpedido", "nivel": 1},
        {"nome": "Peso da Culpa", "nivel": 1},
        {"nome": "Punir o Mal", "nivel": 6},
        {"nome": "Reflexos Divinos", "nivel": 14},
        {"nome": "Represália à Distância", "nivel": 1},
        {"nome": "Sacrifício do Campeão", "nivel": 12},
        {"nome": "Saúde Divina", "nivel": 4},
        {"nome": "Segundo Aliado", "nivel": 8},
        {"nome": "Sentir o Mal", "nivel": 8},
    ]

    reacao_golpe_retributivo = construir_acao_habilidade(
        "Golpe Retributivo",
        "reacao",
        ["Campeão"],
        "Você protege seu aliado e golpeia seu adversário. O aliado recebe resistência a todo dano contra o dano acionador igual a 2 + seu nível. Se o adversário estiver em seu alcance, faça um Golpe corpo a corpo contra ele.",
        acionamento="Um inimigo causa dano a um aliado, e ambos estão a até 4,5 metros de você.",
    )
    reacao_vislumbre_redencao = construir_acao_habilidade(
        "Vislumbre de Redenção",
        "reacao",
        ["Campeão"],
        (
            "Seu adversário hesita sob o peso do pecado enquanto visões de redenção ocupam o centro de sua mente. O adversário deve escolher uma das seguintes opções: "
            "• O aliado não sofre o dano acionador. "
            "• O aliado recebe resistência a todo dano contra o dano acionador igual a 2 + seu nível. Após o efeito de dano ser aplicado, o inimigo fica enfraquecido 2 até o final do próximo turno dele."
        ),
        acionamento="Um inimigo causa dano a um aliado, e ambos estão a até 4,5 metros de você.",
    )
    reacao_passo_liberador = construir_acao_habilidade(
        "Passo Liberador",
        "reacao",
        ["Campeão"],
        (
            "Você libera um aliado de contenções. Se o acionamento for um aliado sofrendo dano, o aliado recebe resistência a todo dano contra o dano acionador igual a 2 + seu nível. "
            "O aliado pode tentar libertar-se de quaisquer efeitos que o estejam agarrando, restringindo, imobilizando ou paralisando. "
            "Ele tenta um novo salvamento contra um desses efeitos que permita um salvamento ou tenta Escapar de um efeito como uma ação livre. "
            "Se puder se mover, o aliado pode Dar um Passo como uma ação livre mesmo que não precise escapar."
        ),
        acionamento="Um inimigo causa dano, Agarra ou Atraca um aliado, e ambos estão a até 4,5 metros de você.",
    )

    caracteristicas_de_classe = [
        construir_caracteristica_classe(
            "Ancestralidade e Biografia",
            1,
            "Além das habilidades fornecidas por sua classe no 1º nível, você possui os benefícios da ancestralidade e biografia selecionadas, conforme descrito no Capítulo 2.",
        ),
        construir_caracteristica_classe(
            "Proficiências Iniciais",
            1,
            "No 1º nível, você recebe proficiências que representam seu treinamento básico, listadas no início desta classe.",
        ),
        construir_caracteristica_classe(
            "Código de Campeão",
            1,
            (
                "Você segue um código de conduta composto por princípios compartilhados por todos os campeões de uma tendência (tal como bom) e por princípios de sua causa. "
                "Os princípios são listados em ordem de importância, do mais importante ao menos importante. "
                "Se desviar-se de sua tendência ou violar seu código de conduta, você perde sua reserva de foco e aliado divino até demonstrar arrependimento conduzindo um ritual de expiação (página 413)."
            ),
            detalhes={
                "principios_do_bem": [
                    "Você nunca deve realizar atos anátemas à sua divindade ou voluntariamente cometer um ato maligno, como assassinato premeditado, tortura ou conjurar uma magia maligna.",
                    "Você nunca deve intencionalmente ferir um inocente, ou permitir o sofrimento imediato de um inocente através de inação quando sabe que poderia preveni-lo razoavelmente. Este princípio não o força a agir contra possíveis ferimentos ou sofrimentos de inocentes em um momento futuro indefinido ou sacrificar sua vida para protegê-los.",
                ]
            },
        ),
        construir_caracteristica_classe(
            "Divindade e Causa",
            1,
            (
                "Escolha uma divindade para seguir (páginas 437 a 440); sua tendência deve ser permitida para seguidores de sua divindade. "
                "Você segue uma das causas bondosas (Paladino, Redentor ou Libertador), que deve corresponder exatamente à sua tendência e determina sua reação de campeão, "
                "lhe concede uma magia de devoção e define parte de seu código de campeão."
            ),
        ),
        construir_caracteristica_classe(
            "Arma Deificada",
            1,
            (
                "Você empunha fervorosamente a arma favorita de sua divindade. Se ela for incomum, você obtém acesso a ela. "
                "Se ela for um ataque desarmado (com d4 como dado de dano) ou uma arma simples, aumente seu dado de dano em um passo (d4 para d6, d6 para d8, d8 para d10, d10 para d12)."
            ),
        ),
        construir_caracteristica_classe(
            "Reação de Campeão",
            1,
            "Sua causa lhe fornece uma reação especial: Golpe Retributivo para paladinos, Vislumbre de Redenção para redentores ou Passo Liberador para libertadores.",
            acoes_concedidas=[reacao_golpe_retributivo, reacao_vislumbre_redencao, reacao_passo_liberador],
        ),
        construir_caracteristica_classe(
            "Magias de Devoção",
            1,
            (
                "O poder de sua divindade lhe concede magias divinas especiais chamadas magias de devoção, que são um tipo de magia de foco. "
                "Você adquire uma reserva de foco com 1 Ponto de Foco (máximo 3 Pontos de Foco; recupera 1 ponto com 10 minutos usando Refocar orando ou prestando serviços à sua causa). "
                "Você recebe uma magia de devoção dependendo de sua causa e é treinado em ataques de magia e CDs de magias. Seu atributo de conjuração é Carisma."
            ),
            detalhes={"reserva_foco_inicial": 1, "tradicao": "divina", "atributo_conjuracao": "carisma"},
        ),
        construir_caracteristica_classe(
            "Talentos de Campeão",
            1,
            "No 1º nível e a cada nível par subsequente, você recebe um talento de classe de campeão.",
        ),
        construir_caracteristica_classe(
            "Bloqueio com Escudo",
            1,
            "Você recebe o talento geral Bloqueio com Escudo (página 258), uma reação que lhe permite reduzir dano com seu escudo.",
            detalhes={"talento_bonus": "Bloqueio com Escudo"},
        ),
        construir_caracteristica_classe(
            "Talentos de Perícia",
            2,
            "No 2º nível e a cada 2 níveis subsequentes, você recebe um talento de perícia (Capítulo 5).",
        ),
        construir_caracteristica_classe(
            "Aliado Divino",
            3,
            (
                "Sua devoção atrai um espírito da tendência de sua divindade. Uma vez que tenha escolhido um aliado (Escudo Aliado, Lâmina Aliada ou Montaria Aliada), "
                "sua escolha não pode ser alterada."
            ),
        ),
        construir_caracteristica_classe(
            "Talentos Gerais",
            3,
            "No 3º nível e a cada 4 níveis subsequentes, você recebe um talento geral (Capítulo 5).",
        ),
        construir_caracteristica_classe(
            "Incrementos de Perícia",
            3,
            "No 3º nível e a cada 2 níveis subsequentes, você recebe um incremento de perícia (mestre a partir do 7º nível, lendário a partir do 15º nível).",
        ),
        construir_caracteristica_classe(
            "Melhorias de Atributo",
            5,
            "No 5º nível e a cada 5 níveis subsequentes, você melhora os valores de quatro atributos diferentes (+1 se >= 18, +2 se < 18).",
        ),
        construir_caracteristica_classe(
            "Talentos de Ancestralidade",
            5,
            "Você recebe um talento de ancestralidade no 5º nível e a cada 4 níveis subsequentes.",
        ),
        construir_caracteristica_classe(
            "Especialidade em Armas",
            5,
            "Suas graduações de proficiência em armas simples, armas marciais e ataques desarmados aumentam para especialista.",
        ),
        construir_caracteristica_classe(
            "Especialidade em Armaduras",
            7,
            "Suas graduações de proficiência em armaduras leves, médias e pesadas e em defesa sem armadura aumentam para especialista. Você adquire os efeitos de especialização em armadura para armaduras médias e pesadas.",
        ),
        construir_caracteristica_classe(
            "Especialização em Armas",
            7,
            "Você causa 2 pontos de dano adicionais com armas e ataques desarmados nos quais é especialista (3 se mestre, 4 se lendário).",
        ),
        construir_caracteristica_classe(
            "Especialidade de Campeão",
            9,
            "Suas graduações de proficiência em sua CD de classe de campeão, ataques de magia e CDs de magias aumentam para especialista.",
        ),
        construir_caracteristica_classe(
            "Punição Divina",
            9,
            (
                "Sua reação de campeão é aprimorada conforme sua causa: "
                "Paladino causa dano persistente bondoso igual ao modificador de Carisma ao atingir com Golpe Retributivo; "
                "Redentor causa dano persistente bondoso igual ao modificador de Carisma se o inimigo escolher causar dano; "
                "Libertador causa dano persistente bondoso igual ao modificador de Carisma se o inimigo estava deixando o aliado agarrado, restringido, imobilizado ou paralisado."
            ),
        ),
        construir_caracteristica_classe(
            "Irrefreável",
            9,
            "Sua graduação de proficiência em salvamentos de Fortitude aumenta para mestre. Quando rolar um sucesso em um salvamento de Fortitude, trate o resultado como um sucesso crítico.",
        ),
        construir_caracteristica_classe(
            "Reflexos Rápidos",
            9,
            "Sua graduação de proficiência em salvamentos de Reflexos aumenta para especialista.",
        ),
        construir_caracteristica_classe(
            "Prontidão",
            11,
            "Sua graduação de proficiência em Percepção aumenta para especialista.",
        ),
        construir_caracteristica_classe(
            "Vontade Divina",
            11,
            "Sua graduação de proficiência em salvamentos de Vontade aumenta para mestre. Quando rolar um sucesso em um salvamento de Vontade, trate o resultado como um sucesso crítico.",
        ),
        construir_caracteristica_classe(
            "Exaltação",
            11,
            (
                "Sua reação de campeão exalta aliados próximos (a até 4,5 metros): "
                "Paladino permite que aliados com o alvo em seu alcance corpo a corpo gastem reação para Golpear com –5 de penalidade; "
                "Redentor aplica a resistência a si mesmo e aos aliados (reduzida em 2 pontos); "
                "Libertador permite que você e todos os aliados deem um Passo se o aliado não tentar libertar-se."
            ),
        ),
        construir_caracteristica_classe(
            "Maestria em Armaduras",
            13,
            "Suas graduações de proficiência em armaduras leves, médias e pesadas, assim como em defesa sem armadura, aumentam para mestre.",
        ),
        construir_caracteristica_classe(
            "Maestria em Armas",
            13,
            "Suas graduações de proficiência em armas simples, armas marciais e ataques desarmados aumentam para mestre.",
        ),
        construir_caracteristica_classe(
            "Especialização em Armas Maior",
            15,
            "Seu dano de especialização em armas aumenta para 4 pontos com armas e ataques desarmados nos quais é especialista, 6 pontos nos quais é mestre e 8 pontos nos quais é lendário.",
        ),
        construir_caracteristica_classe(
            "Maestria de Campeão",
            17,
            "Suas graduações de proficiência em sua CD de classe de campeão, ataques de magia e CDs de magias aumentam para mestre.",
        ),
        construir_caracteristica_classe(
            "Lenda de Armaduras",
            17,
            "Suas graduações de proficiência em armaduras leves, médias e pesadas, assim como em defesa sem armadura, aumentam para lendário.",
        ),
        construir_caracteristica_classe(
            "Desafio do Herói",
            19,
            "Você pode desafiar o destino e continuar a lutar enquanto tiver energia divina. Você recebe a magia de devoção desafio do herói.",
        ),
    ]

    subclasses = {
        "tipo": "causa",
        "nome_tipo": "Causa",
        "opcoes": [
            {
                "id": "paladino",
                "nome": "Paladino",
                "tendencia_requerida": "Ordeiro e Bom",
                "descricao": "Você é honrado, franco e comprometido a afastar as forças da crueldade.",
                "reacao_campeao": "Golpe Retributivo",
                "magia_devocao": "imposição de mãos",
                "principios_adicionais": [
                    "Você deve agir com honra, nunca tirar vantagem dos outros, mentir ou trapacear.",
                    "Você deve respeitar a autoridade legal da liderança legítima onde quer que vá, e seguir suas leis.",
                ],
                "punicao_divina_9_nivel": "Você envolve alvos malignos em uma auréola de punição. Se atingir com seu Golpe Retributivo, o alvo sofre dano persistente bondoso igual ao seu modificador de Carisma.",
                "exaltacao_11_nivel": "Quando você usar Golpe Retributivo, cada aliado a até 4,5 metros de você que tiver o alvo em seu próprio alcance corpo a corpo pode gastar uma reação para Golpear o alvo com –5 de penalidade.",
            },
            {
                "id": "redentor",
                "nome": "Redentor",
                "tendencia_requerida": "Neutro e Bom",
                "descricao": "Você carrega benevolência e perdão consigo.",
                "reacao_campeao": "Vislumbre de Redenção",
                "magia_devocao": "imposição de mãos",
                "principios_adicionais": [
                    "Você deve primeiro tentar redimir aqueles que cometeram atos malignos, em vez de matá-los ou distribuir punição. Se continuarem em um caminho perverso, você pode tomar medidas mais extremas se for necessário.",
                    "Você deve demonstrar compaixão com os outros, independentemente de sua autoridade ou condição.",
                ],
                "punicao_divina_9_nivel": "Uma consciência culpada ataca os adversários que recusarem seu Vislumbre de Redenção. Um adversário que responder ao seu Vislumbre de Redenção decidindo causar dano sofre dano persistente bondoso igual ao seu modificador de Carisma.",
                "exaltacao_11_nivel": "Você pode aplicar a resistência concedida por Vislumbre de Redenção a si mesmo e a todos os aliados a até 4,5 metros, incluindo o aliado acionador. Porém, a resistência concedida é reduzida em 2 pontos para todos.",
            },
            {
                "id": "libertador",
                "nome": "Libertador",
                "tendencia_requerida": "Caótico e Bom",
                "descricao": "Você é comprometido em defender a liberdade dos outros.",
                "reacao_campeao": "Passo Liberador",
                "magia_devocao": "imposição de mãos",
                "principios_adicionais": [
                    "Você deve respeitar as escolhas dos outros sobre suas próprias vidas, e não pode forçar alguém a agir de uma forma em particular ou ameaçar alguém se não o fizer.",
                    "Você deve exigir e lutar pela liberdade dos outros de tomarem suas próprias decisões. Você nunca pode se envolver com ou tolerar escravidão ou tirania.",
                ],
                "punicao_divina_9_nivel": "Se o inimigo acionador estava usando qualquer efeito para deixar seu aliado agarrado, restringido, imobilizado ou paralisado quando você usou Passo Liberador, esse inimigo sofre dano persistente bondoso igual ao seu modificador de Carisma.",
                "exaltacao_11_nivel": "Quando usar Passo Liberador, se seu aliado não tentar libertar-se de um efeito, você e todos seus aliados a até 4,5 metros podem Dar um Passo (incluindo o aliado acionador).",
            },
        ],
        "aliado_divino_3_nivel": {
            "tipo": "aliado_divino",
            "nome_tipo": "Aliado Divino",
            "nivel": 3,
            "opcoes": [
                {
                    "id": "escudo_aliado",
                    "nome": "Escudo Aliado",
                    "descricao": "Um espírito de proteção habita seu escudo. Em suas mãos, a Dureza do escudo aumenta em 2 pontos e seus Pontos de Vida (PV) e Limiar de Quebra (LQ) aumentam em 50%.",
                },
                {
                    "id": "lamina_aliada",
                    "nome": "Lâmina Aliada",
                    "descricao": (
                        "Um espírito de batalha habita seu armamento. Selecione uma arma ou bandagens das pancadas poderosas quando fizer suas preparações diárias. "
                        "Em suas mãos, o item adquire o efeito de uma runa de propriedade (para princípios do bem: disruptora, mutável, retornante ou toque fantasma). "
                        "Você também recebe o efeito de especialização de crítico da arma."
                    ),
                },
                {
                    "id": "montaria_aliada",
                    "nome": "Montaria Aliada",
                    "descricao": (
                        "Você adquire um companheiro animal jovem como montaria (página 214). Normalmente deve ser um animal que possua a habilidade especial montaria, como um cavalo. "
                        "Você pode selecionar um companheiro animal diferente (a critério do MJ), mas esta habilidade não lhe concede a habilidade especial montaria."
                    ),
                },
            ],
        },
    }

    termos_chave = [
        {
            "termo": "Floreio",
            "descricao": "Ações de floreio são técnicas que requerem empenho demais e não podem ser realizadas várias vezes em seguida. Você pode usar apenas 1 ação com o traço floreio por turno.",
        },
        {
            "termo": "Juramento",
            "descricao": "Juramentos adicionam um princípio ao seu código. Normalmente você pode possuir apenas um talento com este traço.",
        },
        {
            "termo": "Metamágico",
            "descricao": (
                "Ações com esse traço alteram as propriedades de suas magias. Você deve usar uma ação metamágica logo antes de Conjurar a Magia que deseja alterar; "
                "qualquer outra ação (inclusive livres e reações) desperdiça o benefício. Efeitos acrescentados são parte do efeito da magia."
            ),
        },
    ]

    exemplos_personagens = [
        {
            "nome": "Redentor",
            "pagina": 112,
            "resumo": "Sua verdade e compaixão brilham com a força do sol, trazendo o mal para a luz de sua deusa, a Flor do Alvorecer.",
            "atributos": "Coloque uma Força alta para melhorar suas habilidades de combate e um Carisma bom para suas magias de devoção.",
            "pericias": ["Atletismo", "Diplomacia", "Medicina", "Religião"],
            "divindade_e_causa": "Sarenrae, redentor",
            "talento_inicial": "Domínio de Divindade (verdade)",
            "talentos_niveis_superiores": [
                "Juramento Reluzente (2º)",
                "Misericórdia (4º)",
                "Litania Contra Ira (6º)",
                "Sentir o Mal (8º)",
                "Foco Devotado (10º)",
                "Dúvida Persistente (12º)",
                "Misericórdia Definitiva (18º)",
            ],
        },
        {
            "nome": "Libertador",
            "pagina": 114,
            "resumo": "Com o nome da Doce Ferroada em seus lábios, você liberta aqueles presos contra sua vontade e exerce vingança contra seus captores.",
            "atributos": "Foque em Destreza. Carisma melhora suas magias de devoção e Dissimulação, e bons valores em Sabedoria e Constituição aprimoram suas defesas.",
            "pericias": ["Dissimulação", "Furtividade", "Religião", "Sociedade"],
            "divindade_e_causa": "Calístria, libertador",
            "talento_inicial": "Passo Desimpedido",
            "talentos_niveis_superiores": [
                "Graça Divina (2º)",
                "Aura de Coragem (4º)",
                "Ataque de Oportunidade (6º)",
                "Deslocamento Libertador (12º)",
            ],
            "nota": "No quadro de exemplo da página 114 consta 'Deslocamento Libertador (12º)', que corresponde ao talento 'Andar Liberador (12º)' na lista de talentos.",
        },
    ]

    talentos = [
        # 1º NÍVEL (4)
        construir_talento_classe(
            "Domínio de Divindade",
            1,
            ["Campeão"],
            "Você incorpora um aspecto de sua divindade. Escolha um dos domínios de sua divindade dentre os listados na página 441. Você recebe a magia inicial de domínio como uma magia de devoção.",
        ),
        construir_talento_classe(
            "Passo Desimpedido",
            1,
            ["Campeão"],
            "Com uma explosão de libertação divina, o movimento de seu aliado recebido de seu Passo Liberador não é afetado por terreno difícil, terreno difícil maior, superfícies estreitas e solo irregular.",
            pre_requisitos="causa de libertador",
        ),
        construir_talento_classe(
            "Peso da Culpa",
            1,
            ["Campeão"],
            "A culpa anuvia a mente daqueles que ignoram seu Vislumbre de Redenção. Em vez de deixar a criatura acionadora enfraquecida 2, você pode deixá-la estupefata 2 pela mesma duração.",
            pre_requisitos="causa de redentor",
        ),
        construir_talento_classe(
            "Represália à Distância",
            1,
            ["Campeão"],
            "Você pode usar Golpe Retributivo com uma arma à distância. Além disso, se o adversário que acionou sua reação estiver a 1,5 metros além de seu alcance (mas não dentro de seu alcance), você pode Dar um Passo como parte de sua reação para colocar o adversário em seu alcance antes de realizar um Golpe Retributivo corpo a corpo.",
            pre_requisitos="causa de paladino",
        ),
        # 2º NÍVEL (5)
        construir_talento_classe(
            "Graça Divina",
            2,
            ["Campeão"],
            "Você recorre à graça de sua divindade, recebendo +2 de bônus de circunstância no salvamento.",
            acoes="reacao",
            acionamento="Você tenta um salvamento contra uma magia, antes de efetuar a rolagem.",
        ),
        construir_talento_classe(
            "Juramento do Matador de Dragões",
            2,
            ["Campeão", "Juramento"],
            "Você jurou matar dragões malignos. Acrescente o seguinte princípio ao seu código após os outros: “Você deve matar os dragões malignos que encontrar desde que tenha uma chance razoável de sucesso.” Seu Golpe Retributivo recebe +4 de bônus de circunstância de dano contra um dragão maligno, ou +6 se você possuir proficiência de mestre com a arma usada. A resistência concedida por seu Vislumbre de Redenção contra o dano de um dragão maligno é 7 + seu nível. Se usar Passo Liberador acionado por um dragão maligno, seu aliado recebe +4 de bônus de circunstância em testes concedidos pelo seu Passo Liberador, e esse aliado pode Dar um Passo duas vezes após isso. Você não considera dragões malignos como autoridades legítimas, mesmo em nações por eles governadas.",
            pre_requisitos="princípios do bem",
        ),
        construir_talento_classe(
            "Juramento Reluzente",
            2,
            ["Campeão", "Juramento"],
            "Você jurou dar o descanso final para os amaldiçoados mortos-vivos. Acrescente o seguinte princípio ao seu código após os outros: “Você deve encerrar a existência de mortos-vivos que encontrar desde que tenha uma chance razoável de sucesso; na incrivelmente improvável situação onde encontre um morto-vivo bondoso, você pode procurar uma forma mais pacífica de ajudá-lo a se recuperar de seu estado morto-vivo em vez de destruí-lo em combate, como ajudando-o a completar seus assuntos inacabados para encontrar a paz.” Seu Golpe Retributivo recebe +4 de bônus de circunstância de dano contra um morto-vivo, ou +6 se você tiver proficiência de mestre com a arma usada. A resistência concedida pelo seu Vislumbre de Redenção contra o dano de um morto-vivo é 7 + seu nível. Se usar Passo Liberador acionado por um morto-vivo, seu aliado recebe +4 de bônus de circunstância em testes concedidos pelo seu Passo Liberador, e o aliado pode Dar um Passo duas vezes após isso. Você não considera mortos-vivos como autoridades legítimas, mesmo em nações por eles governadas.",
            pre_requisitos="princípios do bem",
        ),
        construir_talento_classe(
            "Juramento de Ruína dos Ínferos",
            2,
            ["Campeão", "Juramento"],
            "Você jurou banir a corrupção de ínferos para os planos sombrios que eles chamam de lar. Acrescente o seguinte princípio ao seu código após os outros: “Você deve banir ou matar ínferos com quem cruzar desde que tenha uma chance razoável de sucesso; na incrivelmente improvável situação onde encontre um ínfero bondoso, você não precisa bani-lo ou matá-lo.” Seu Golpe Retributivo recebe +4 de bônus de circunstância de dano contra um ínfero, ou +6 se você possuir proficiência de mestre com a arma usada. A resistência concedida por seu Vislumbre de Redenção contra o dano de um ínfero é 7 + seu nível. Se usar Passo Liberador acionado por um ínfero, seu aliado recebe +4 de bônus de circunstância em testes concedidos pelo seu Passo Liberador, e esse aliado pode Dar um Passo duas vezes após isso. Você não considera ínferos como autoridades legítimas, mesmo em nações por eles governadas.",
            pre_requisitos="princípios do bem",
        ),
        construir_talento_classe(
            "Juramento Vingativo",
            2,
            ["Campeão", "Juramento"],
            "Você jurou perseguir malfeitores perversos e levá-los a seu julgamento. Acrescente o seguinte princípio ao seu código após os outros: “Você deve perseguir e exterminar criaturas malignas que cometeram atrocidades hediondas desde que tenha uma chance razoável de sucesso e não esteja engajado em uma missão que o impediria de fazê-lo.” Você pode usar imposição de mãos para ferir uma criatura que você tenha testemunhado ferindo um inocente ou um aliado bondoso tratando-a como se ela fosse um morto-vivo; neste caso, imposição de mãos causa dano bondoso em vez de dano positivo e adquire o traço bem. Este dano bondoso pode afetar criaturas não-malignas. Isto não o impede de curar essas criaturas com imposição de mãos; você escolhe se pretende curar ou ferir.",
            pre_requisitos="causa de paladino",
        ),
        # 4º NÍVEL (3)
        construir_talento_classe(
            "Aura de Coragem",
            4,
            ["Campeão"],
            "Você permanece forte frente ao perigo e inspira seus aliados a fazerem o mesmo. Sempre que ficar assustado, reduza o valor da condição em 1 (até um mínimo de 0). Ao final de seu turno quando reduziria o valor de sua condição assustado em 1, você também reduz o valor da condição assustado de todos seus aliados a até 4,5 metros de distância.",
            pre_requisitos="princípios do bem",
        ),
        construir_talento_classe(
            "Misericórdia",
            4,
            ["Campeão", "Concentração", "Metamágico"],
            "Seu toque alivia o medo e restaura o movimento perdido. Se a próxima ação que você usar for imposição de mãos, você pode tentar neutralizar um efeito de medo ou que esteja impondo a condição paralisado no alvo (além dos outros benefícios de imposição de mãos).",
            acoes="1",
            pre_requisitos="magia de devoção (imposição de mãos)",
        ),
        construir_talento_classe(
            "Saúde Divina",
            4,
            ["Campeão"],
            "Sua fé o torna resistente a doenças, protegendo-o enquanto você oferece socorro aos doentes. Você recebe +1 de bônus de estado em salvamentos contra doenças. Além disso, se rolar um sucesso em um salvamento contra uma doença, trate o resultado como um sucesso crítico.",
            pre_requisitos="princípios do bem",
        ),
        # 6º NÍVEL (5)
        construir_talento_classe(
            "Ataque de Oportunidade",
            6,
            ["Campeão"],
            "Você ataca um adversário que baixa a guarda. Faça um Golpe corpo a corpo contra a criatura acionadora. Se seu ataque for um acerto crítico e o acionamento for uma ação de manuseio, você interrompe essa ação. Este Golpe não conta para sua penalidade por ataques múltiplos e sua penalidade por ataques múltiplos não se aplica a ele.",
            acoes="reacao",
            acionamento="Uma criatura em seu alcance usa uma ação de manuseio ou de movimento, desfere um ataque à distância ou sai de um quadrado usando uma ação de movimento.",
        ),
        construir_talento_classe(
            "Cavalo de Guerra Leal",
            6,
            ["Campeão"],
            "Você e sua montaria ficam mais próximos, e a lealdade de um ao outro é inquebrável. A montaria recebida através da característica de classe aliado divino torna-se um companheiro animal maduro (página 214). Além disso, sua montaria nunca lhe ataca mesmo se for magicamente compelida a fazê-lo.",
            pre_requisitos="aliado divino (montaria)",
        ),
        construir_talento_classe(
            "Guardião de Escudo",
            6,
            ["Campeão"],
            "Você usa seu escudo para proteger seus aliados tão bem quanto a si mesmo. Quando tiver seu escudo erguido, você pode usar sua reação Bloqueio com Escudo quando um ataque for feito contra um aliado adjacente a você. Se o fizer, o escudo impede que esse aliado sofra dano (em vez de impedir que você sofra dano), seguindo as regras normais para Bloqueio com Escudo.",
            pre_requisitos="aliado divino (escudo), princípios do bem",
        ),
        construir_talento_classe(
            "Litania Contra Ira",
            6,
            ["Campeão"],
            "Você escoria um adversário, punindo-o por sua ira contra criaturas bondosas. Você pode conjurar a magia de devoção litania contra ira. Aumente em 1 a quantidade de Pontos de Foco em sua reserva de foco.",
            pre_requisitos="magias de devoção, princípios do bem",
        ),
        construir_talento_classe(
            "Punir o Mal",
            6,
            ["Campeão"],
            "Sua lâmina aliada se torna uma ferramenta ainda mais poderosa contra malfeitores. Selecione um adversário que você pode ver. Até o início de seu próximo turno, seus Golpes realizados com a arma habitada por sua lâmina aliada contra esse adversário causam 4 de dano bondoso extra, aumentando para 6 pontos de dano se você possuir proficiência de mestre com esta arma. Se o adversário atacar um de seus aliados, a duração é prolongada para até o final do próximo turno desse adversário. Se o adversário continuar a atacar seus aliados a cada turno, a duração continua a ser prolongada.",
            acoes="1",
            pre_requisitos="aliado divino (lâmina)",
        ),
        # 8º NÍVEL (6)
        construir_talento_classe(
            "Bloqueio Rápido",
            8,
            ["Campeão"],
            "Você pode bloquear com seu escudo instintivamente. No início de cada um de seus turnos, você recebe uma reação adicional que pode ser usada somente para realizar um Bloqueio com Escudo.",
        ),
        construir_talento_classe(
            "Curar Montaria",
            8,
            ["Campeão"],
            "A devoção que você possui à sua montaria se manifesta como um surto de energia positiva. Quando conjurar imposição de mãos em sua montaria, você pode restaurar 10 Pontos de Vida, mais 10 para cada nível elevado.",
            pre_requisitos="aliado divino (montaria)",
        ),
        construir_talento_classe(
            "Domínio de Divindade Avançado",
            8,
            ["Campeão"],
            "Através de sua convicção, você vislumbrou os segredos mais profundos do domínio de sua divindade. Você recebe uma magia avançada de domínio do domínio escolhido com seu talento Domínio de Divindade. Você pode conjurar essa magia como uma magia de devoção. Aumente em 1 a quantidade de Pontos de Foco em sua reserva de foco.",
            pre_requisitos="Domínio de Divindade",
        ),
        construir_talento_classe(
            "Misericórdia Maior",
            8,
            ["Campeão"],
            "Sua fé melhora ainda mais sua habilidade de remover condições. Quando usar Misericórdia, você pode tentar neutralizar as condições cego, enjoado, lento ou surdo.",
            pre_requisitos="Misericórdia",
        ),
        construir_talento_classe(
            "Segundo Aliado",
            8,
            ["Campeão"],
            "Sua graça interior atrai a atenção de um segundo espírito protetor. Escolha um segundo tipo de aliado divino e receba seus benefícios.",
            pre_requisitos="aliado divino",
        ),
        construir_talento_classe(
            "Sentir o Mal",
            8,
            ["Campeão"],
            "Você sente o mal como uma sensação desagradável ou um pressentimento de mau agouro. Quando estiver na presença de uma aura de mal poderosa ou avassaladora (página 334), você eventualmente a detecta, embora não o faça necessariamente de forma instantânea e não consiga apontar exatamente a sua localização. Isto se manifesta como um sentido vago, similar ao olfato dos humanos. Uma criatura maligna utilizando um disfarce ou de alguma outra forma tentando esconder sua presença realiza um teste de Dissimulação contra sua CD de Percepção para esconder a aura de você. Se a criatura obtiver sucesso no teste de Dissimulação, ela fica temporariamente imune ao seu Sentir o Mal por 1 dia.",
            pre_requisitos="princípios do bem",
        ),
        # 10º NÍVEL (5)
        construir_talento_classe(
            "Corcel Imponente",
            10,
            ["Campeão"],
            "Sob seus cuidados, sua montaria atingiu seu potencial inato. A montaria recebida através da característica de classe aliado divino torna-se um companheiro animal ágil ou selvagem (página 214). Durante um encontro e no seu turno, mesmo se você não usar a ação Comandar um Animal, sua montaria ainda pode usar 1 ação para Andar ou Golpear.",
            pre_requisitos="aliado divino (montaria), Cavalo de Guerra Leal",
        ),
        construir_talento_classe(
            "Espírito da Lâmina Radiante",
            10,
            ["Campeão"],
            "Seu aliado divino irradia poder, melhorando sua arma escolhida. Quando escolher a arma para sua lâmina aliada durante suas preparações diárias, adicione as seguintes runas de propriedade à lista de efeitos disponíveis para sua escolha: flamejante e quaisquer runas de tendência (anárquica, axiomática, profana ou sagrada) correspondentes à tendência de sua causa.",
            pre_requisitos="aliado divino (lâmina)",
        ),
        construir_talento_classe(
            "Escudo da Retribuição",
            10,
            ["Campeão", "Floreio"],
            "Quando defender seu aliado contra um ataque, você recorre a seu poder para protegê-lo ainda mais. Você usa a reação Bloqueio com Escudo para prevenir o dano contra um aliado e também sua reação de campeão contra o adversário que atacou seu aliado.",
            acoes="reacao",
            pre_requisitos="aliado divino (escudo), princípios do bem, reação de campeão, Guardião de Escudo",
            acionamento="O ataque de um adversário contra um aliado condiz com o acionamento para sua reação de Bloqueio com Escudo e sua reação de campeão.",
        ),
        construir_talento_classe(
            "Foco Devotado",
            10,
            ["Campeão"],
            "Sua devoção é forte o suficiente para aumentar seu foco a um grau incrível. Se tiver gastado pelo menos 2 Pontos de Foco desde a última vez que Refocou, você recupera 2 Pontos de Foco ao Refocar (em vez de recuperar somente 1 ponto).",
            pre_requisitos="magias de devoção",
        ),
        construir_talento_classe(
            "Litania Contra Preguiça",
            10,
            ["Campeão"],
            "Você professa contra o pecado da preguiça, virando a indolência de um adversário contra ele mesmo. Você pode conjurar a magia de devoção litania contra preguiça. Aumente em 1 a quantidade de Pontos de Foco em sua reserva de foco.",
            pre_requisitos="magias de devoção, princípios do bem",
        ),
        # 12º NÍVEL (7)
        construir_talento_classe(
            "Andar Liberador",
            12,
            ["Campeão"],
            "Em vez de Dar um Passo ao final de seu Passo Liberador, o aliado acionador pode Andar até metade da Velocidade dele. Mesmo que você tenha exaltação, somente o aliado acionador recebe este benefício.",
            pre_requisitos="causa de libertador",
        ),
        construir_talento_classe(
            "Aura de Fé",
            12,
            ["Campeão"],
            "Você irradia uma aura de pura crença que imbui os seus ataques e de seus aliados próximos com poder sagrado. Seus Golpes causam 1 de dano bondoso extra contra criaturas malignas. Além disso, cada aliado de tendência bondosa a até 4,5 metros recebe este benefício em seu primeiro Golpe que atingir uma criatura maligna a cada rodada.",
            pre_requisitos="princípios do bem",
        ),
        construir_talento_classe(
            "Dúvida Persistente",
            12,
            ["Campeão"],
            "Quando lançar dúvida sobre seus adversários, os efeitos duram mais do que o normal. Após ficar enfraquecido 2 por seu Vislumbre de Redenção, o adversário fica enfraquecido 1 por 1 minuto. Se você possuir o talento Peso da Culpa, após ficar estupefato 2 por seu Vislumbre de Redenção, o adversário fica estupefato 1 por 1 minuto ou até o teste simples de estupefato o fizer perder uma magia, o que ocorrer primeiro.",
            pre_requisitos="causa de redentor",
        ),
        construir_talento_classe(
            "Lâmina da Justiça",
            12,
            ["Campeão"],
            "Você recorre ao poder divino e desfere um Golpe com arma ou desarmado contra um adversário que você tiver testemunhado ferindo um aliado ou inocente. O Golpe causa dois dados de dano extras da arma se o alvo de seu Golpe for maligno. Seja o alvo maligno ou não, o Golpe aplica todos os efeitos que normalmente aplicaria em um Golpe Retributivo (como punição divina) e você pode converter todo o dano físico do ataque em dano bondoso.",
            acoes="2",
            pre_requisitos="causa de paladino",
        ),
        construir_talento_classe(
            "Misericórdia de Aflição",
            12,
            ["Campeão"],
            "A graça divina que flui por você cancela uma aflição. Quando usar sua Misericórdia, você pode tentar neutralizar uma doença, maldição ou veneno.",
            pre_requisitos="Misericórdia",
        ),
        construir_talento_classe(
            "Muralha Divina",
            12,
            ["Campeão"],
            "Você usa seu escudo para assolar seus inimigos, impedindo que se afastem ou andem ao seu redor. Todos os quadrados adjacentes a você são terreno difícil para seus inimigos.",
            requerimentos="Você está empunhando um escudo.",
        ),
        construir_talento_classe(
            "Sacrifício do Campeão",
            12,
            ["Campeão"],
            "Você pode sofrer para que outros sobrevivam. Você pode conjurar a magia de devoção sacrifício do campeão. Aumente em 1 a quantidade de Pontos de Foco em sua reserva de foco.",
            pre_requisitos="princípios do bem",
        ),
        # 14º NÍVEL (7)
        construir_talento_classe(
            "Aura de Ancoragem",
            14,
            ["Campeão"],
            "Sua aura impede a teleportação de ínferos. Sua aura tenta neutralizar magias de teleportação conjuradas por ínferos a até 4,5 metros, utilizando o nível de magia e CD de suas magias de devoção.",
            pre_requisitos="Juramento de Ruína dos Ínferos",
        ),
        construir_talento_classe(
            "Aura de Retidão",
            14,
            ["Campeão"],
            "Sua aura de retidão diminui o poder do mal. Você e todos seus aliados a até 4,5 metros adquirem resistência 5 ao mal.",
            pre_requisitos="princípios do bem",
        ),
        construir_talento_classe(
            "Aura de Ruína das Serpes",
            14,
            ["Campeão"],
            "Sua aura protege contra as energias destrutivas e sopros de dragões. Você e todos seus aliados a até 4,5 metros adquirem resistência igual ao seu modificador de Carisma contra ácido, eletricidade, fogo, frio e veneno. Se a fonte de um destes tipos de dano for o sopro de um dragão, aumente a resistência para metade do seu nível.",
            pre_requisitos="Juramento do Matador de Dragões",
        ),
        construir_talento_classe(
            "Aura de Vida",
            14,
            ["Campeão"],
            "Sua aura protege contra efeitos necromânticos. Você e todos seus aliados a até 4,5 metros adquirem resistência 5 a energia negativa e +1 de bônus de estado em salvamentos contra efeitos de necromancia.",
            pre_requisitos="Juramento Reluzente",
        ),
        construir_talento_classe(
            "Aura de Vingança",
            14,
            ["Campeão"],
            "Quando recorrer aos outros para exercer retribuição, você também guia sua mira. Quando usar Golpe Retributivo, seus aliados que desferirem Golpes sofrem apenas –2 de penalidade, em vez de –5.",
            pre_requisitos="exaltação, Juramento Vingativo",
        ),
        construir_talento_classe(
            "Litania de Retidão",
            14,
            ["Campeão"],
            "Você recorre à retidão para expor as fraquezas de um adversário. Você pode conjurar a magia de devoção litania de retidão. Aumente em 1 a quantidade de Pontos de Foco em sua reserva de foco.",
            pre_requisitos="magias de devoção, princípios do bem",
        ),
        construir_talento_classe(
            "Reflexos Divinos",
            14,
            ["Campeão"],
            "No início de cada um de seus turnos, você recebe uma reação adicional que pode ser usada somente para realizar sua reação de campeão.",
        ),
        # 16º NÍVEL (3)
        construir_talento_classe(
            "Escudo da Graça",
            16,
            ["Campeão"],
            "Você protege um aliado com seu escudo e corpo. Sempre que usar a reação Bloqueio com Escudo para prevenir dano contra um aliado, você pode dividir igualmente o dano remanescente após o Bloqueio com Escudo entre você mesmo e seu aliado.",
            pre_requisitos="Guardião de Escudo",
        ),
        construir_talento_classe(
            "Instrumento de Fervor",
            16,
            ["Campeão"],
            "Energia divina preenche sua arma. Sempre que atingir um acerto crítico contra um adversário usando Lâmina da Justiça ou Golpe Retributivo, seu ataque adiciona um dado de dano extra e o alvo fica lento 1 no próximo turno dele.",
            pre_requisitos="aliado divino (lâmina), princípios do bem",
        ),
        construir_talento_classe(
            "Montaria Auspiciosa",
            16,
            ["Campeão"],
            "Guiada por seu cuidado contínuo, sua montaria desenvolveu competência e inteligência incríveis. A montaria recebida pela característica de classe aliado divino torna-se um companheiro animal especializado (página 217). Você pode selecionar uma das especializações convencionais ou a especialização auspiciosa. Sua montaria auspiciosa recebe os benefícios de: ser marcada como uma criatura sagrada para a sua divindade pelo símbolo religioso que se manifesta em seu corpo; ter a graduação de proficiência em Religião aumentada para especialista; e poder falar o idioma associado aos servidores de sua divindade (Celestial para campeões que seguem os princípios do bem). Ainda, o modificador de Inteligência dela é aumentado em 2 pontos e o modificador de Sabedoria dela é aumentado em 1 ponto.",
            pre_requisitos="aliado divino (montaria), Corcel Imponente",
        ),
        # 18º NÍVEL (2)
        construir_talento_classe(
            "Forma Celestial",
            18,
            ["Campeão"],
            "Você assume uma fisionomia celestial, parecendo um tipo de celestial que serve à sua divindade; por exemplo, você pode ganhar a auréola e asas emplumadas de um anjo. Você adquire uma Velocidade de voo igual à sua Velocidade. Você também adquire visão no escuro (se ainda não possuir), o traço celestial e o traço apropriado para o tipo de servidor que você se torna (arconte, anjo ou azata, por exemplo).",
            pre_requisitos="princípios do bem",
        ),
        construir_talento_classe(
            "Misericórdia Definitiva",
            18,
            ["Campeão"],
            "Sua misericórdia transcende os limites da vida e da morte. Quando usar Misericórdia, você pode conjurar imposição de mãos em uma criatura que tenha morrido no máximo na rodada anterior. O alvo retorna à vida com 1 Ponto de Vida e fica ferido 1. Você não pode usar Misericórdia Definitiva se o efeito acionador for desintegrar ou um efeito de morte.",
            pre_requisitos="Misericórdia",
        ),
        # 20º NÍVEL (3)
        construir_talento_classe(
            "Escudeiro Exemplar",
            20,
            ["Campeão"],
            "Seu escudo é um receptáculo de proteção divina. Quando estiver empunhando seu escudo escolhido, ele está sempre erguido mesmo que você não use a ação Erguer um Escudo. Os PV e LQ de seu escudo escolhido são dobrados, em vez de serem aumentados em 50%. Se fosse ser destruído, ele desaparece e vai para o reino de sua divindade em vez disso, sendo reparado por seu aliado divino. Durante suas próximas preparações diárias, o escudo retorna para você completamente reparado.",
            pre_requisitos="aliado divino (escudo)",
        ),
        construir_talento_classe(
            "Mestre da Lâmina Radiante",
            20,
            ["Campeão"],
            "Seu aliado divino transforma sua arma escolhida em um exímio exemplar de seu tipo. Quando escolher a arma para sua lâmina aliada durante suas preparações diárias, adicione as seguintes runas de propriedade à lista de efeitos disponíveis para sua escolha: afiada, dançarina e disruptora maior.",
            pre_requisitos="aliado divino (lâmina), Espírito da Lâmina Radiante",
        ),
        construir_talento_classe(
            "Montaria Celestial",
            20,
            ["Campeão"],
            "Sua montaria recebe poderes celestiais incríveis concedidos por sua divindade. Ela adquire visão no escuro, seus Pontos de Vida máximos aumentam em 40, e ela adquire fraqueza 10 a dano maligno. Adicionalmente, ela desenvolve asas apropriadas para um servidor de sua divindade (como asas metálicas para um arconte), concedendo-a uma Velocidade de voo igual à Velocidade dela. Ela adquire o traço celestial e o traço apropriado para o tipo de servidor que se torna (arconte, anjo ou azata, por exemplo).",
            pre_requisitos="aliado divino (montaria), princípios do bem",
        ),
    ]

    return {
        "id": "campeao",
        "nome": "Campeão",
        "paginas": "104-115",
        "descricao": (
            "Você é um emissário de uma divindade — um servo devotado que vestiu um pesado manto de responsabilidade e adere a um código que o mantém à parte dos outros. "
            "Embora existam campeões de todas as tendências, como um campeão do bem você traz certeza e esperança aos inocentes. "
            "Você possui defesas poderosas que compartilha livremente com seus aliados e inocentes e um poder divino que usa para encerrar qualquer ameaça maligna. "
            "Sua devoção atrai até mesmo a atenção de espíritos sagrados que o ajudam em sua jornada."
        ),
        "atributo_chave": {
            "opcoes": ["forca", "destreza"],
            "melhoria_1_nivel": 2,
            "texto": "Força ou Destreza — No 1º nível, sua classe lhe concede uma melhoria de atributo à sua escolha em Força ou Destreza.",
        },
        "pontos_de_vida_por_nivel": 10,
        "pontos_de_vida_texto": "10 mais seu modificador de Constituição no 1º nível e a cada nível subsequente.",
        "jogando_com_a_classe": {
            "encontros_combate": "Você confronta inimigos em combate frente a frente enquanto se posiciona cautelosamente para proteger seus aliados.",
            "encontros_sociais": "Você é a voz da esperança, lutando para alcançar uma solução pacífica que fortaleça as alianças e traga bons resultados para todos.",
            "exploracao": "Você supera barreiras físicas e espirituais, fornecendo inspiração para seus aliados através de suas ações e oferecendo — quando seus companheiros pedem por isso — orientação ética e moral.",
            "recesso": "Você passa boa parte de seu tempo em orações e contemplação solenes, treinamento rigoroso, trabalhos de caridade e obedecendo aos princípios de seu código — mas isso não significa que não tenha tempo para assumir um ofício ou passatempo.",
            "voce_pode": [
                "Acreditar na esperança de que o bem triunfará sobre o mal, não importa quão terríveis sejam as circunstâncias.",
                "Saber que os fins não justificam os meios, já que atos malignos aumentam o poder do mal.",
                "Possuir um forte senso de certo e errado e ficar frustrado quando a ganância ou falta de visão levam ao mal.",
            ],
            "outros_provavelmente": [
                "O veem como um símbolo de esperança, especialmente em tempos de grande necessidade.",
                "Se preocupam que você não estará disposto a ceder quando for necessário ou que você os despreze secretamente por não viverem segundo seus padrões impossíveis.",
                "Sabem que você fez e serve a juramentos divinos e podem confiar que você irá mantê-los.",
            ],
        },
        "proficiencias_iniciais": {
            "percepcao": "treinado",
            "salvamentos": {
                "fortitude": "especialista",
                "reflexos": "treinado",
                "vontade": "especialista",
            },
            "pericias": {
                "fixas": ["religiao"],
                "opcoes_fixas": [],
                "condicionais": ["pericia_determinada_pela_divindade"],
                "adicionais_base": 2,
                "soma_modificador_inteligencia": True,
                "texto": "Treinado em Religião; treinado em uma perícia determinada por sua divindade; treinado em uma quantidade de perícias adicionais igual a 2 mais seu modificador de Inteligência.",
            },
            "ataques": {
                "armas_simples": "treinado",
                "armas_marciais": "treinado",
                "ataques_desarmados": "treinado",
            },
            "defesas": {
                "armaduras_leves": "treinado",
                "armaduras_medias": "treinado",
                "armaduras_pesadas": "treinado",
                "todas_armaduras": "treinado",
                "defesa_sem_armadura": "treinado",
            },
            "cd_classe": {
                "graduacao": "treinado",
                "texto": "Treinado em CD de classe de campeão",
            },
            "magias": {
                "tradicao": "divina",
                "tipo_conjuracao": "foco_devocao",
                "ataques_magia": "treinado",
                "cds_magia": "treinado",
                "atributo_conjuracao": "carisma",
                "texto": "Treinado em ataques de magias divinas; treinado em CDs de magias divinas.",
            },
        },
        "tabela_progressao": tabela_progressao,
        "tabelas_especificas": {
            "tabela_talentos_indice": tabela_talentos_indice,
        },
        "caracteristicas_de_classe": caracteristicas_de_classe,
        "subclasses": subclasses,
        "termos_chave": termos_chave,
        "exemplos_personagens": exemplos_personagens,
        "talentos_de_classe": talentos,
    }


def montar_dados_classes_01() -> dict[str, Any]:
    """Monta o dicionário completo de dados/classes.json para a Leva 01."""
    return {
        "meta": {
            "titulo": "Capítulo 3: Classes (Leva 01: Introdução, Alquimista, Bárbaro, Bardo e Campeão) — Pathfinder 2E Livro Básico",
            "arquivo_origem": "ref/Classes 01.pdf",
            "paginas_livro_basico": "67-115",
            "leva": 1,
            "classes_incluidas": ["alquimista", "barbaro", "bardo", "campeao"],
            "versao": "1.0.0",
            "observacoes": (
                "Primeira leva do Capítulo 3: Classes, contendo as regras gerais de classe (pp. 67-68), "
                "a visão geral das 12 classes básicas (p. 69) e os dados completos de Alquimista, Bárbaro, Bardo e Campeão."
            ),
        },
        "regras_gerais_classes": construir_regras_gerais_classes(),
        "visao_geral_classes": construir_visao_geral_classes(),
        "classes": [
            construir_alquimista(),
            construir_barbaro(),
            construir_bardo(),
            construir_campeao(),
        ],
    }


def validar_classes_01_json(dados: dict[str, Any]) -> None:
    """Valida todas as contagens, tabelas, subclasses, IDs e talentos da Leva 01."""
    visao_geral = dados["visao_geral_classes"]
    assert len(visao_geral) == 12, f"Esperado 12 classes na visão geral, encontrado {len(visao_geral)}"
    assert len({c["id"] for c in visao_geral}) == 12, "IDs duplicados em visao_geral_classes"

    classes = dados["classes"]
    assert len(classes) == 4, f"Esperado 4 classes na Leva 01, encontrado {len(classes)}"
    ids_classes = [c["id"] for c in classes]
    assert ids_classes == ["alquimista", "barbaro", "bardo", "campeao"], f"Classes inesperadas: {ids_classes}"

    esperado_talentos_por_nivel = {
        "alquimista": {1: 4, 2: 3, 4: 3, 6: 3, 8: 3, 10: 5, 12: 3, 14: 3, 16: 4, 18: 4, 20: 3},
        "barbaro": {1: 5, 2: 5, 4: 4, 6: 7, 8: 6, 10: 5, 12: 5, 14: 4, 16: 3, 18: 3, 20: 2},
        "bardo": {1: 4, 2: 5, 4: 4, 6: 3, 8: 3, 10: 3, 12: 2, 14: 3, 16: 2, 18: 3, 20: 3},
        "campeao": {1: 4, 2: 5, 4: 3, 6: 5, 8: 6, 10: 5, 12: 7, 14: 7, 16: 3, 18: 2, 20: 3},
    }
    esperado_totais_talentos = {"alquimista": 38, "barbaro": 49, "bardo": 35, "campeao": 50}

    for classe in classes:
        cid = classe["id"]
        prog = classe["tabela_progressao"]
        assert len(prog) == 20, f"Esperado 20 níveis na progressão de {cid}, encontrado {len(prog)}"
        assert [row["nivel"] for row in prog] == list(range(1, 21)), f"Níveis fora de ordem em {cid}"

        talentos = classe["talentos_de_classe"]
        total_esp = esperado_totais_talentos[cid]
        assert len(talentos) == total_esp, f"Esperado {total_esp} talentos em {cid}, encontrado {len(talentos)}"
        assert len({t["id"] for t in talentos}) == total_esp, f"IDs duplicados em talentos de {cid}"

        contagem_por_nivel: dict[int, int] = {}
        for t in talentos:
            contagem_por_nivel[t["nivel"]] = contagem_por_nivel.get(t["nivel"], 0) + 1
        assert contagem_por_nivel == esperado_talentos_por_nivel[cid], (
            f"Distribuição por nível divergente em {cid}: {contagem_por_nivel}"
        )

        indice = classe["tabelas_especificas"]["tabela_talentos_indice"]
        assert len(indice) == total_esp, f"Tabela índice divergente em {cid}: {len(indice)}"
        pares_talentos = {(t["nome"], t["nivel"]) for t in talentos}
        pares_indice = {(i["nome"], i["nivel"]) for i in indice}
        assert pares_talentos == pares_indice, (
            f"Diferença entre talentos e tabela índice em {cid}: {pares_talentos ^ pares_indice}"
        )

    mapa_classes = {c["id"]: c for c in classes}

    alquimista = mapa_classes["alquimista"]
    assert len(alquimista["subclasses"]["opcoes"]) == 3
    assert len(alquimista["tabelas_especificas"]["exemplo_livro_de_formulas"]["formulas"]) == 8

    barbaro = mapa_classes["barbaro"]
    assert len(barbaro["subclasses"]["opcoes"]) == 5
    assert len(barbaro["tabelas_especificas"]["tabela_3_3_instintos_animais"]) == 9
    assert len(barbaro["tabelas_especificas"]["tabela_3_4_instintos_de_dragao"]) == 10

    bardo = mapa_classes["bardo"]
    assert len(bardo["subclasses"]["opcoes"]) == 3
    assert len(bardo["tabelas_especificas"]["tabela_3_6_magias_por_dia"]) == 20

    campeao = mapa_classes["campeao"]
    assert len(campeao["subclasses"]["opcoes"]) == 3
    assert len(campeao["subclasses"]["aliado_divino_3_nivel"]["opcoes"]) == 3


def main() -> None:
    """Gera dados/classes.json (Leva 01), valida e imprime resumo estatístico."""
    dados = montar_dados_classes_01()
    validar_classes_01_json(dados)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    conteudo = json.dumps(dados, ensure_ascii=False, indent=2)
    CAMINHO_SAIDA.write_text(conteudo + "\n", encoding="utf-8")

    total_talentos = sum(len(c["talentos_de_classe"]) for c in dados["classes"])
    print(f"Arquivo gerado com sucesso: {CAMINHO_SAIDA}")
    print(f"- Visão geral de classes: {len(dados['visao_geral_classes'])} classes")
    print(f"- Classes completas nesta leva: {len(dados['classes'])} ({', '.join(c['nome'] for c in dados['classes'])})")
    for c in dados["classes"]:
        print(
            f"  * {c['nome']}: {len(c['caracteristicas_de_classe'])} características, "
            f"{len(c['subclasses']['opcoes'])} opções de {c['subclasses']['nome_tipo']}, "
            f"{len(c['talentos_de_classe'])} talentos de classe"
        )
    print(f"- Total de talentos convertidos na Leva 01: {total_talentos}")
    print(f"- Tamanho do arquivo: {CAMINHO_SAIDA.stat().st_size} bytes")


if __name__ == "__main__":
    main()
