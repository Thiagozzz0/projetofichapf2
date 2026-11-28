"""Gerador e validador de dados/dadosc&c/introducao.json a partir de ref/cc/C&C introdução.pdf (pp. 7–15)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "dadosc&c" / "introducao.json"


def _mapa_modificadores_por_valor(faixas: list[dict[str, Any]]) -> dict[str, int]:
    """Expande a tabela de faixas de atributo (1..19) em um mapa direto valor -> modificador."""
    mapa: dict[str, int] = {}
    for faixa in faixas:
        for valor in range(faixa["min"], faixa["max"] + 1):
            mapa[str(valor)] = faixa["modificador"]
    return mapa


def construir_introducao() -> dict[str, Any]:
    """Monta o schema estruturado completo de `dados/dadosc&c/introducao.json`."""
    faixas_modificadores = [
        {"faixa": "1", "min": 1, "max": 1, "modificador": -4},
        {"faixa": "2-3", "min": 2, "max": 3, "modificador": -3},
        {"faixa": "4-5", "min": 4, "max": 5, "modificador": -2},
        {"faixa": "6-8", "min": 6, "max": 8, "modificador": -1},
        {"faixa": "9-12", "min": 9, "max": 12, "modificador": 0},
        {"faixa": "13-15", "min": 13, "max": 15, "modificador": 1},
        {"faixa": "16-17", "min": 16, "max": 17, "modificador": 2},
        {"faixa": "18-19", "min": 18, "max": 19, "modificador": 3},
    ]

    return {
        "metadados": {
            "sistema": "Castles & Crusades",
            "edicao": "1ª Edição Brasileira (Livro do Jogador)",
            "arquivo_fonte": "ref/cc/C&C introdução.pdf",
            "paginas_livro": "7–15",
            "total_paginas_pdf": 9,
            "versao_schema": 1,
            "idioma": "pt-BR",
        },
        "conceitos_gerais": {
            "papel_mestre": {
                "nome": "Guardião do Castelo",
                "sigla": "GC",
                "descricao": (
                    "Responsável por criar o cenário, conduzir o enredo, interpretar coadjuvantes, "
                    "vilões e monstros, e atuar como árbitro imparcial das regras."
                ),
            },
            "filosofia_jogo": (
                "Regras leves, rápidas e adaptáveis com foco em narrativa, emoção e imaginação; "
                "regras básicas concebidas para serem compreendidas em cerca de quinze minutos."
            ),
            "dados_e_notacao": {
                "dados_fisicos": ["d4", "d6", "d8", "d10", "d12", "d20", "d100"],
                "d100": "Rolagem de 2d10 designando um dado para as dezenas e outro para as unidades.",
                "dados_simulados": {
                    "d2": {
                        "dado_base": "d6",
                        "mapeamento": {"1-3": 1, "4-6": 2},
                    },
                    "d3": {
                        "dado_base": "d6",
                        "mapeamento": {"1-2": 1, "3-4": 2, "5-6": 3},
                    },
                },
                "formato_rolagem": "[# de dados]tipo de dado[+/- modificadores] (ex.: 3d6, 3d6+3).",
                "regra_arredondamento": "Sempre descartar a fração (truncamento para baixo), salvo exceção explícita nas regras (como mínimo de 1).",
            },
        },
        "criacao_personagem": {
            "etapas": [
                {
                    "ordem": 1,
                    "id": "imaginar_personagem",
                    "nome": "Imagine um Personagem",
                    "descricao": "Definir o conceito geral, estilo e inspiração do herói ou vilão.",
                },
                {
                    "ordem": 2,
                    "id": "rolar_atributos",
                    "nome": "Role os Atributos",
                    "descricao": "Rolar 3d6 seis vezes (valores entre 3 e 18) e distribuir os resultados entre os seis atributos na ordem escolhida pelo jogador.",
                },
                {
                    "ordem": 3,
                    "id": "escolher_classe",
                    "nome": "Escolha uma Classe",
                    "descricao": "Selecionar um dos 13 arquétipos de classe oficiais, definindo atributo principal fixo, PV, BpA, proficiências e habilidades.",
                },
                {
                    "ordem": 4,
                    "id": "escolher_raca",
                    "nome": "Escolha uma Raça",
                    "descricao": "Selecionar uma das 7 raças oficiais, aplicando modificadores raciais, habilidades especiais e quantidade total de atributos primários.",
                },
                {
                    "ordem": 5,
                    "id": "definir_primarios_e_pv",
                    "nome": "Atributos Primários e Pontos de Vida",
                    "descricao": "Escolher os atributos primários adicionais (2 para humanos, 1 para não-humanos) e determinar os Pontos de Vida iniciais.",
                },
                {
                    "ordem": 6,
                    "id": "detalhar_e_equipar",
                    "nome": "Dando Corpo ao Personagem",
                    "descricao": "Definir personalidade, descrição física, histórico, disposição moral, dinheiro inicial e comprar armaduras, armas e equipamentos.",
                },
            ],
            "regras_pontos_de_vida": {
                "descricao": "Rolados na criação e a cada novo nível usando o dado de vida da classe, somando ou subtraindo o modificador de Constituição.",
                "padrao": {
                    "id": "padrao",
                    "nome": "Regra Padrão",
                    "descricao": "Rolar o dado de vida da classe e somar/subtrair o modificador de Constituição na criação e em cada nível.",
                },
                "opcionais": [
                    {
                        "id": "opcional_1_maximo_n1",
                        "nome": "Regra Opcional #1 (Máximo no 1º Nível)",
                        "descricao": "O personagem começa o jogo com o valor máximo do dado de vida no 1º nível, somando ou subtraindo o modificador de Constituição.",
                    },
                    {
                        "id": "opcional_2_multiplas_rolagens_con",
                        "nome": "Regra Opcional #2 (Múltiplas Rolagens por CON)",
                        "descricao": "Rolar o dado de vida um número de vezes igual a 1 + bônus de Constituição e ficar com o maior resultado (na criação e a cada nível), somando ou subtraindo o modificador de Constituição.",
                    },
                ],
            },
        },
        "atributos": {
            "geracao_padrao": {
                "rolagem": "3d6",
                "repeticoes": 6,
                "valor_minimo_inicial": 3,
                "valor_maximo_inicial": 18,
                "distribuicao": "livre_entre_os_seis_atributos",
                "observacao": "Modificadores raciais podem alterar as pontuações. Em jogo, magia, veneno ou maldições podem reduzir abaixo de 3 ou elevar acima de 18.",
            },
            "lista": [
                {
                    "id": "forca",
                    "sigla": "For",
                    "nome": "Força",
                    "categoria": "fisico",
                    "descricao": "Reflete a força física, capacidade de levantar ou mover objetos pesados e realizar ataques poderosos.",
                    "efeitos": [
                        "Modificador aplicado ao ataque corpo a corpo",
                        "Modificador aplicado ao dano corpo a corpo",
                        "Todos os testes envolvendo Força",
                    ],
                    "capacidade_esforco": {
                        "barra_fixa_multiplicador_forca": 10,
                        "levantamento_terra_multiplicador_forca": 15,
                    },
                },
                {
                    "id": "destreza",
                    "sigla": "Des",
                    "nome": "Destreza",
                    "categoria": "fisico",
                    "descricao": "Representa reflexos, destreza manual, coordenação olho-mão e capacidade de esquivar e defender-se.",
                    "efeitos": [
                        "Modificador aplicado à Classe de Armadura (CA)",
                        "Modificador aplicado ao combate à distância",
                        "Todos os testes envolvendo Destreza",
                    ],
                },
                {
                    "id": "constituicao",
                    "sigla": "Con",
                    "nome": "Constituição",
                    "categoria": "fisico",
                    "descricao": "Reflete a saúde geral, capacidade de suportar dor, tolerar dano físico, evitar fadiga e resistir a doenças e venenos.",
                    "efeitos": [
                        "Modificador aplicado aos Pontos de Vida (PV)",
                        "Todos os testes envolvendo Constituição",
                    ],
                },
                {
                    "id": "inteligencia",
                    "sigla": "Int",
                    "nome": "Inteligência",
                    "categoria": "mental",
                    "descricao": "Reflete a aptidão mental, capacidade de aprendizado rápido, aplicação do conhecimento e raciocínio dedutivo.",
                    "efeitos": [
                        "Afeta o número de feitiços arcanos por dia",
                        "Afeta o número de idiomas adicionais aprendidos",
                        "Todos os testes envolvendo Inteligência",
                    ],
                },
                {
                    "id": "sabedoria",
                    "sigla": "Sab",
                    "nome": "Sabedoria",
                    "categoria": "mental",
                    "descricao": "Reflete a profundidade da experiência pessoal, julgamento ponderado e conexão espiritual com uma divindade.",
                    "efeitos": [
                        "Afeta o número de feitiços divinos por dia",
                        "Afeta tentativas de afastar mortos-vivos",
                        "Todos os testes envolvendo Sabedoria",
                    ],
                },
                {
                    "id": "carisma",
                    "sigla": "Car",
                    "nome": "Carisma",
                    "categoria": "mental",
                    "descricao": "Representa magnetismo pessoal, força de vontade, personalidade, liderança e capacidade de influenciar outros.",
                    "efeitos": [
                        "Afeta lealdade e reações de criaturas",
                        "Afeta o número de mortos-vivos que podem ser afastados",
                        "Todos os testes envolvendo Carisma",
                    ],
                },
            ],
            "tabela_modificadores": faixas_modificadores,
            "modificador_por_valor": _mapa_modificadores_por_valor(faixas_modificadores),
        },
        "sistema_siege": {
            "nome": "SIEGE Engine",
            "atributos_primarios": {
                "humano": {
                    "total_primarios": 3,
                    "fixo_classe": 1,
                    "escolha_jogador": 2,
                    "total_secundarios": 3,
                },
                "nao_humano": {
                    "racas": ["anao", "elfo", "gnomo", "meio_elfo", "pequenino", "meio_orc"],
                    "total_primarios": 2,
                    "fixo_classe": 1,
                    "escolha_jogador": 1,
                    "total_secundarios": 4,
                },
                "regra_classe": "Cada classe define 1 atributo principal fixo que não pode ser alterado; o jogador escolhe os primários restantes.",
            },
            "testes_de_atributo": {
                "dado": "1d20",
                "base_desafio_primario": 12,
                "base_desafio_secundario": 18,
                "nivel_desafio_faixa_tipica": "0 a 10 (podendo ser maior)",
                "formula_classe_desafio": "Base do Desafio (12 primário / 18 secundário) + Nível de Desafio (ND)",
                "formula_rolagem": "1d20 + modificador do atributo + nível do personagem (se aplicável) + bônus racial (se aplicável)",
                "condicao_sucesso": "resultado_total >= classe_de_desafio",
                "exemplo_oficial": {
                    "personagem": "Explorador Elfo nível 3 com Sabedoria 15 (+1) como atributo primário",
                    "acao": "Rastrear kobolds (ND 3)",
                    "classe_de_desafio": 15,
                    "rolagem_exemplo": "13 (d20) + 3 (nível) + 1 (Sabedoria) = 17 >= 15 (Sucesso)",
                },
            },
        },
        "racas_resumo": [
            {"id": "humano", "nome": "Humano", "resumo": "Versátil", "total_atributos_primarios": 3, "primarios_escolha_jogador": 2},
            {"id": "elfo", "nome": "Elfo", "resumo": "De vida longa", "total_atributos_primarios": 2, "primarios_escolha_jogador": 1},
            {"id": "anao", "nome": "Anão", "resumo": "Teimoso", "total_atributos_primarios": 2, "primarios_escolha_jogador": 1},
            {"id": "gnomo", "nome": "Gnomo", "resumo": "Curioso", "total_atributos_primarios": 2, "primarios_escolha_jogador": 1},
            {"id": "pequenino", "nome": "Pequenino", "resumo": "De pés ligeiros", "total_atributos_primarios": 2, "primarios_escolha_jogador": 1},
            {"id": "meio_elfo", "nome": "Meio-Elfo", "resumo": "Melancólico", "total_atributos_primarios": 2, "primarios_escolha_jogador": 1},
            {"id": "meio_orc", "nome": "Meio-Orc", "resumo": "Pernicioso", "total_atributos_primarios": 2, "primarios_escolha_jogador": 1},
        ],
        "classes_introducao": {
            "total_classes": 13,
            "penalidade_arma_nao_proficiente": -4,
            "regras_armadura": {
                "mago_e_ilusionista": "Se um mago vestir qualquer armadura, não poderá conjurar feitiços.",
                "classes_efeitos_variaveis": ["barbaro", "explorador", "trapaceiro", "assassino"],
                "regra_geral": (
                    "Qualquer personagem pode vestir qualquer armadura, mas usar armadura fora da lista da classe "
                    "pode impedir ou penalizar o uso de habilidades de classe, salvo indicação contrária na habilidade."
                ),
            },
            "multiclasse_e_classe_e_meia": (
                "Combina habilidades, com algumas limitações, de duas classes em uma, permitindo criar arquétipos próprios."
            ),
            "terminologia": {
                "atributo_principal": "Atributo primário fixo da classe (não pode ser alterado).",
                "pontos_de_vida": "Tipo de dado rolado a cada nível (cumulativo) + modificador de Constituição.",
                "bonus_para_acertar": "BpA: modificador somado às jogadas para acertar em ataques corpo a corpo ou à distância.",
                "disposicao": "Tendência moral/ética sugerida para a classe.",
                "armas": "Lista de armas com as quais a classe é treinada; armas fora da lista impõem penalidade de -4 nos ataques.",
                "armadura": "Lista de armaduras, escudos e elmos permitidos sem restringir habilidades de classe.",
                "habilidades": "Lista de capacidades especiais; um atributo entre parênteses indica teste de atributo (SIEGE).",
                "nivel": "Escala de evolução do personagem conforme ganha experiência.",
                "ppe": "Progressão por Pontos de Experiência: tabela de XP necessária para atingir cada nível.",
            },
            "classes": [
                {
                    "id": "assassino",
                    "nome": "Assassino",
                    "resumo_curto": "Especialista em eliminar inimigos específicos.",
                    "descricao_arquetipo": "Furtivos e astutos, matadores especializados que raramente têm outros motivos além do pagamento por um trabalho bem executado.",
                },
                {
                    "id": "barbaro",
                    "nome": "Bárbaro",
                    "resumo_curto": "Baseado na força de vontade e instinto em combate.",
                    "descricao_arquetipo": "Vivem fora do mundo civilizado, apreciam a liberdade e desprezam as convenções rígidas das sociedades urbanas.",
                },
                {
                    "id": "bardo",
                    "nome": "Bardo",
                    "resumo_curto": "Influencia os outros através do poder das palavras.",
                    "descricao_arquetipo": "Através da canção, oratória e ação, inspiram, transmitem história e tradição e influenciam crenças e comportamentos.",
                },
                {
                    "id": "cavaleiro",
                    "nome": "Cavaleiro",
                    "resumo_curto": "Líder natural e forte guerreiro.",
                    "descricao_arquetipo": "Pertencem às castas guerreiras; usam status social, carisma, bravura e códigos de honra para inspirar e liderar.",
                },
                {
                    "id": "clerigo",
                    "nome": "Clérigo",
                    "resumo_curto": "Devoto a uma divindade e aplica a justiça divina.",
                    "descricao_arquetipo": "Espiritualmente ligados a uma divindade, exercem magia divina e armamentos de guerra como emissários de sua fé.",
                },
                {
                    "id": "combatente",
                    "nome": "Combatente",
                    "resumo_curto": "Guerreiro voraz no campo de batalha.",
                    "descricao_arquetipo": "Guerreiros corajosos que contam com sua maestria marcial e armamento para superar qualquer desafio em batalha.",
                },
                {
                    "id": "druida",
                    "nome": "Druida",
                    "resumo_curto": "Deve lealdade aos poderes naturais do mundo.",
                    "descricao_arquetipo": "Chamados a uma espiritualidade primordial, voltam-se ao mundo natural e seguem os princípios da ordem da natureza.",
                },
                {
                    "id": "explorador",
                    "nome": "Explorador",
                    "resumo_curto": "Caçador e guerreiro extraordinário.",
                    "descricao_arquetipo": "Especialistas solitários em sobrevivência nas terras selvagens, dedicados a proteger a civilização de ameaças malignas.",
                },
                {
                    "id": "ilusionista",
                    "nome": "Ilusionista",
                    "resumo_curto": "Distorce magicamente as percepções dos outros.",
                    "descricao_arquetipo": "Estudam o arcano e usam oratória e feitiçaria para conjurar manifestações e sonhos, tornando o irreal real.",
                },
                {
                    "id": "lutador",
                    "nome": "Lutador",
                    "resumo_curto": "Treina o corpo para resistir às agruras da guerra e clima.",
                    "descricao_arquetipo": "Guerreiros mortais que dependem da força de seus corpos e vontade, aperfeiçoando o próprio corpo em arma letal.",
                },
                {
                    "id": "mago",
                    "nome": "Mago",
                    "resumo_curto": "Praticante de magias arcanas poderosas.",
                    "descricao_arquetipo": "Mergulham nos mistérios do arcano empunhando a magia como arma, movidos por sede de conhecimento e poder.",
                },
                {
                    "id": "paladino",
                    "nome": "Paladino",
                    "resumo_curto": "Guerreiro sagrado, um exemplo do bem.",
                    "descricao_arquetipo": "Os mais sagrados guerreiros, vivem em pureza e bondade servindo aos preceitos religiosos de sua divindade.",
                },
                {
                    "id": "trapaceiro",
                    "nome": "Trapaceiro",
                    "resumo_curto": "Velhaco e oportunista.",
                    "descricao_arquetipo": "Vagabundos e astutos que vivem no limite da ética, ganhando a vida por meio de façanhas furtivas e oportunismo.",
                },
            ],
            "tabela_referencia_armaduras_escudos_elmos": {
                "assassino": {
                    "armaduras_qualquer": False,
                    "armaduras_nenhuma": False,
                    "armaduras": ["Couro", "Casaco de Couro", "Acolchoada"],
                    "armaduras_observacao": "e veja a classe",
                    "escudos_qualquer": False,
                    "escudos_nenhum": False,
                    "escudos": ["Pequeno", "Pavis"],
                    "elmos_qualquer": False,
                    "elmos_nenhum": False,
                    "elmos": ["Capuz de Couro"],
                },
                "barbaro": {
                    "armaduras_qualquer": True,
                    "armaduras_nenhuma": False,
                    "armaduras": ["Qualquer"],
                    "armaduras_observacao": None,
                    "escudos_qualquer": True,
                    "escudos_nenhum": False,
                    "escudos": ["Qualquer"],
                    "elmos_qualquer": True,
                    "elmos_nenhum": False,
                    "elmos": ["Qualquer"],
                },
                "bardo": {
                    "armaduras_qualquer": False,
                    "armaduras_nenhuma": False,
                    "armaduras": [
                        "Peitorais",
                        "Cota de Malha",
                        "Couro Cozido",
                        "Conjunto Grego",
                        "Couro Fervido",
                        "Couro Segmentado",
                        "Casaco de Couro",
                        "Malha de Anéis",
                        "Couro Cravejado",
                        "Acolchoada",
                    ],
                    "armaduras_observacao": None,
                    "escudos_qualquer": False,
                    "escudos_nenhum": False,
                    "escudos": ["Pequeno", "Médio"],
                    "elmos_qualquer": False,
                    "elmos_nenhum": False,
                    "elmos": [
                        "Basineto",
                        "Casquetel",
                        "Cota de Malha",
                        "Capuz de Couro",
                        "Elmo",
                        "Elmo Barril",
                        "Elmo Grande",
                    ],
                },
                "cavaleiro": {
                    "armaduras_qualquer": True,
                    "armaduras_nenhuma": False,
                    "armaduras": ["Qualquer"],
                    "armaduras_observacao": None,
                    "escudos_qualquer": True,
                    "escudos_nenhum": False,
                    "escudos": ["Qualquer"],
                    "elmos_qualquer": True,
                    "elmos_nenhum": False,
                    "elmos": ["Qualquer"],
                },
                "clerigo": {
                    "armaduras_qualquer": True,
                    "armaduras_nenhuma": False,
                    "armaduras": ["Qualquer"],
                    "armaduras_observacao": None,
                    "escudos_qualquer": True,
                    "escudos_nenhum": False,
                    "escudos": ["Qualquer"],
                    "elmos_qualquer": True,
                    "elmos_nenhum": False,
                    "elmos": ["Qualquer"],
                },
                "combatente": {
                    "armaduras_qualquer": True,
                    "armaduras_nenhuma": False,
                    "armaduras": ["Qualquer"],
                    "armaduras_observacao": None,
                    "escudos_qualquer": True,
                    "escudos_nenhum": False,
                    "escudos": ["Qualquer"],
                    "elmos_qualquer": True,
                    "elmos_nenhum": False,
                    "elmos": ["Qualquer"],
                },
                "druida": {
                    "armaduras_qualquer": False,
                    "armaduras_nenhuma": False,
                    "armaduras": [
                        "Couro Cozido",
                        "Couro Segmentado",
                        "Acolchoada",
                        "Couro",
                        "Casaco de Couro",
                        "Peles",
                    ],
                    "armaduras_observacao": None,
                    "escudos_qualquer": False,
                    "escudos_nenhum": False,
                    "escudos": ["Madeira"],
                    "elmos_qualquer": False,
                    "elmos_nenhum": False,
                    "elmos": ["Capuz de Couro"],
                },
                "explorador": {
                    "armaduras_qualquer": False,
                    "armaduras_nenhuma": False,
                    "armaduras": [
                        "Peitorais",
                        "Cota de Malha Completa",
                        "Couro Cozido",
                        "Conjunto Grego",
                        "Couro Cru",
                        "Casaco de Couro",
                        "Acolchoada",
                        "Malha de Anéis",
                        "Malha de Escamas",
                        "Couro Cravejado",
                    ],
                    "armaduras_observacao": None,
                    "escudos_qualquer": False,
                    "escudos_nenhum": False,
                    "escudos": ["Pequeno", "Médio", "Pavis"],
                    "elmos_qualquer": False,
                    "elmos_nenhum": False,
                    "elmos": [
                        "Benim",
                        "Casquetel",
                        "Cota de Malha",
                        "Coifa de Couro",
                        "Elmo Normando",
                        "Grande Elmo (ou Elmo-Barril)",
                        "Chapéu-de-Ferro",
                    ],
                },
                "ilusionista": {
                    "armaduras_qualquer": False,
                    "armaduras_nenhuma": True,
                    "armaduras": [],
                    "armaduras_observacao": None,
                    "escudos_qualquer": False,
                    "escudos_nenhum": True,
                    "escudos": [],
                    "elmos_qualquer": False,
                    "elmos_nenhum": True,
                    "elmos": [],
                },
                "lutador": {
                    "armaduras_qualquer": False,
                    "armaduras_nenhuma": True,
                    "armaduras": [],
                    "armaduras_observacao": None,
                    "escudos_qualquer": False,
                    "escudos_nenhum": True,
                    "escudos": [],
                    "elmos_qualquer": False,
                    "elmos_nenhum": True,
                    "elmos": [],
                },
                "mago": {
                    "armaduras_qualquer": False,
                    "armaduras_nenhuma": True,
                    "armaduras": [],
                    "armaduras_observacao": None,
                    "escudos_qualquer": False,
                    "escudos_nenhum": True,
                    "escudos": [],
                    "elmos_qualquer": False,
                    "elmos_nenhum": True,
                    "elmos": [],
                },
                "paladino": {
                    "armaduras_qualquer": True,
                    "armaduras_nenhuma": False,
                    "armaduras": ["Qualquer"],
                    "armaduras_observacao": None,
                    "escudos_qualquer": True,
                    "escudos_nenhum": False,
                    "escudos": ["Qualquer"],
                    "elmos_qualquer": True,
                    "elmos_nenhum": False,
                    "elmos": ["Qualquer"],
                },
                "trapaceiro": {
                    "armaduras_qualquer": False,
                    "armaduras_nenhuma": False,
                    "armaduras": ["Couro Cru", "Jaqueta de Couro", "Acolchoada"],
                    "armaduras_observacao": "e veja a classe",
                    "escudos_qualquer": False,
                    "escudos_nenhum": False,
                    "escudos": ["Pequeno", "Médio", "Pavis"],
                    "elmos_qualquer": False,
                    "elmos_nenhum": False,
                    "elmos": ["Capuz de Couro", "Chapéu-de-Ferro"],
                },
            },
        },
    }


def validar_introducao(dados: dict[str, Any]) -> None:
    """Valida integridade estrutural, numérica e completude de `dados/dadosc&c/introducao.json`."""
    assert dados["metadados"]["sistema"] == "Castles & Crusades"
    assert dados["metadados"]["total_paginas_pdf"] == 9

    # 6 atributos (3 físicos + 3 mentais)
    atbs = dados["atributos"]["lista"]
    assert len(atbs) == 6
    assert sum(1 for a in atbs if a["categoria"] == "fisico") == 3
    assert sum(1 for a in atbs if a["categoria"] == "mental") == 3

    # Tabela de modificadores cobrindo 1..19 sem lacunas
    mod_map = dados["atributos"]["modificador_por_valor"]
    assert len(mod_map) == 19
    assert mod_map["1"] == -4
    assert mod_map["3"] == -3
    assert mod_map["5"] == -2
    assert mod_map["8"] == -1
    assert mod_map["9"] == 0 and mod_map["12"] == 0
    assert mod_map["13"] == 1 and mod_map["15"] == 1
    assert mod_map["16"] == 2 and mod_map["17"] == 2
    assert mod_map["18"] == 3 and mod_map["19"] == 3

    # Regras SIEGE Engine
    siege = dados["sistema_siege"]
    assert siege["atributos_primarios"]["humano"]["total_primarios"] == 3
    assert siege["atributos_primarios"]["nao_humano"]["total_primarios"] == 2
    assert siege["testes_de_atributo"]["base_desafio_primario"] == 12
    assert siege["testes_de_atributo"]["base_desafio_secundario"] == 18

    # 7 raças e 13 classes
    racas = dados["racas_resumo"]
    assert len(racas) == 7
    assert {r["id"] for r in racas} == {"humano", "elfo", "anao", "gnomo", "pequenino", "meio_elfo", "meio_orc"}

    classes = dados["classes_introducao"]["classes"]
    assert len(classes) == 13
    ids_classes = {c["id"] for c in classes}
    tabela_arm = dados["classes_introducao"]["tabela_referencia_armaduras_escudos_elmos"]
    assert set(tabela_arm.keys()) == ids_classes
    assert dados["classes_introducao"]["penalidade_arma_nao_proficiente"] == -4
    for sem_arm in ("ilusionista", "lutador", "mago"):
        assert tabela_arm[sem_arm]["armaduras_nenhuma"] is True
        assert tabela_arm[sem_arm]["escudos_nenhum"] is True
        assert tabela_arm[sem_arm]["elmos_nenhum"] is True


def main() -> None:
    """Gera `dados/dadosc&c/introducao.json`, recarrega do disco e valida."""
    dados = construir_introducao()
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_SAIDA.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    recarregado = json.loads(CAMINHO_SAIDA.read_text(encoding="utf-8"))
    validar_introducao(recarregado)
    print(f"OK — {CAMINHO_SAIDA.relative_to(RAIZ_PROJETO)} gerado e validado com sucesso!")
    print(
        f"Atributos: {len(recarregado['atributos']['lista'])} | "
        f"Faixas mod.: {len(recarregado['atributos']['tabela_modificadores'])} (1..19) | "
        f"Raças: {len(recarregado['racas_resumo'])} | "
        f"Classes (resumo + tabela armaduras): {len(recarregado['classes_introducao']['classes'])}"
    )


if __name__ == "__main__":
    main()
