"""Gera e valida o contrato JSON oficial da Ficha de Personagem PF2E (`dados/estrutura_ficha.json`).

Baseado integralmente em `ref/Sheet Update.pdf` (Livro Básico Pathfinder 2ª Edição em
português, páginas 580–583), estruturando:
1. Metadados e observações editoriais da ficha oficial (`meta`).
2. Legendas de proficiência e ícones de ação (`legenda_referencia`).
3. Blueprint visual fiel das 4 páginas oficiais (`paginas`).
4. Fórmulas determinísticas de cálculo derivado (`regras_calculo_ficha`).
5. Mapeamento das fontes de dados em `dados/` (`mapeamento_fontes_dados`).
6. Contrato vazio padrão para o gerador procedural de fichas (`modelo_ficha_vazia`).
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "dadospf2" / "estrutura_ficha.json"
CAMINHO_PERICIAS = RAIZ_PROJETO / "dados" / "dadospf2" / "pericias.json"

NIVEIS_PROFICIENCIA = ["T", "E", "M", "L"]


def _campo(
    id_campo: str,
    rotulo: str,
    tipo: str = "texto",
    **extras: Any,
) -> dict[str, Any]:
    """Cria a definição padrão de um campo de formulário da ficha."""
    definicao: dict[str, Any] = {
        "id": id_campo,
        "rotulo": rotulo,
        "tipo": tipo,
    }
    definicao.update(extras)
    return definicao


def _slot_talento(indice: int, rotulo_nivel: str, categoria: str) -> dict[str, Any]:
    """Cria a definição de uma linha de habilidade ou talento na página 2."""
    return {
        "indice": indice,
        "rotulo_oficial": rotulo_nivel,
        "categoria": categoria,
        "campos": ["nome", "origem_regra", "pagina_ou_referencia", "resumo"],
    }


def _slot_golpe(indice: int, tipo_golpe: str) -> dict[str, Any]:
    """Cria a definição de um slot de Golpe (Corpo a Corpo ou À Distância)."""
    atributo_ataque = "for" if tipo_golpe == "corpo_a_corpo" else "des"
    terceiro_termo_dano = "for" if tipo_golpe == "corpo_a_corpo" else "especial"
    rotulo_terceiro_termo = "FOR" if tipo_golpe == "corpo_a_corpo" else "ESPECIAL"

    return {
        "indice": indice,
        "tipo": tipo_golpe,
        "ataque": {
            "formula": [atributo_ataque.upper(), "PROF", "ITEM"],
            "atributos_possiveis": [atributo_ataque.upper()],
            "niveis_proficiencia": NIVEIS_PROFICIENCIA,
            "campos": ["arma", "bonus_total", "mod_atributo", "proficiencia", "grau_proficiencia", "item"],
        },
        "dano": {
            "formula": ["DADOS", rotulo_terceiro_termo, "ESPEC", "OUTRO"],
            "tipos_dano": [
                {"sigla": "Cn", "nome": "Concussão"},
                {"sigla": "Ct", "nome": "Cortante"},
                {"sigla": "Pf", "nome": "Perfurante"},
            ],
            "campos": [
                "dados",
                terceiro_termo_dano,
                "tipos_dano_marcados",
                "especializacao",
                "outro",
                "tracos",
            ],
        },
    }


def _slot_pericia_oficial(
    ordem_visual: int,
    id_slot: str,
    id_pericia_dados: str,
    rotulo_oficial: str,
    atributo_chave: str,
    tem_penalidade_armadura: bool = False,
    espaco_especializacao: bool = False,
) -> dict[str, Any]:
    """Cria a definição oficial de uma linha na tabela de Perícias da Página 1."""
    formula = [atributo_chave.upper(), "PROF", "ITEM"]
    if tem_penalidade_armadura:
        formula.append("ARMADURA")

    return {
        "ordem_visual": ordem_visual,
        "id": id_slot,
        "id_pericia_dados": id_pericia_dados,
        "rotulo_oficial": rotulo_oficial,
        "atributo_chave": atributo_chave,
        "tem_penalidade_armadura": tem_penalidade_armadura,
        "espaco_especializacao": espaco_especializacao,
        "formula": formula,
        "niveis_proficiencia": NIVEIS_PROFICIENCIA,
    }


def _slot_magia_pagina4(
    indice: int,
    categoria: str,
    tem_checkbox_preparada: bool = True,
    tem_frequencia: bool = False,
) -> dict[str, Any]:
    """Cria a definição de um slot de magia da Página 4."""
    campos = ["nome", "nivel_ou_efeito", "acoes", "componentes", "anotacoes"]
    if tem_checkbox_preparada:
        campos.append("preparada")
    if tem_frequencia:
        campos.append("frequencia")

    return {
        "indice": indice,
        "categoria": categoria,
        "tem_checkbox_preparada": tem_checkbox_preparada,
        "tem_frequencia": tem_frequencia,
        "componentes_disponiveis": [
            {"sigla": "M", "nome": "Material"},
            {"sigla": "S", "nome": "Somático"},
            {"sigla": "V", "nome": "Verbal"},
        ],
        "campos": campos,
    }


def construir_legenda_referencia() -> dict[str, Any]:
    """Constrói a legenda superior esquerda da Página 1."""
    return {
        "proficiencia": [
            {
                "id": "destreinado",
                "sigla": "D",
                "rotulo_oficial": "Destreinado",
                "formula_texto": "+0",
                "bonus_base": 0,
                "soma_nivel": False,
            },
            {
                "id": "treinado",
                "sigla": "T",
                "rotulo_oficial": "Treinado",
                "formula_texto": "2+Nível",
                "bonus_base": 2,
                "soma_nivel": True,
            },
            {
                "id": "especialista",
                "sigla": "E",
                "rotulo_oficial": "Especialista",
                "formula_texto": "4+Nível",
                "bonus_base": 4,
                "soma_nivel": True,
            },
            {
                "id": "mestre",
                "sigla": "M",
                "rotulo_oficial": "Mestre",
                "formula_texto": "6+Nível",
                "bonus_base": 6,
                "soma_nivel": True,
            },
            {
                "id": "lendario",
                "sigla": "L",
                "rotulo_oficial": "Lendário",
                "formula_texto": "8+Nível",
                "bonus_base": 8,
                "soma_nivel": True,
            },
        ],
        "icones_acao": [
            {
                "id": "acao_unica",
                "rotulo_oficial": "Ação Única",
                "custo_acoes": 1,
                "simbolo": "1_acao",
            },
            {
                "id": "atividade_duas_acoes",
                "rotulo_oficial": "Atividade de Duas Ações",
                "custo_acoes": 2,
                "simbolo": "2_acoes",
            },
            {
                "id": "atividade_tres_acoes",
                "rotulo_oficial": "Atividade de Três Ações",
                "custo_acoes": 3,
                "simbolo": "3_acoes",
            },
            {
                "id": "acao_livre",
                "rotulo_oficial": "Ação Livre",
                "custo_acoes": 0,
                "simbolo": "acao_livre",
            },
            {
                "id": "reacao",
                "rotulo_oficial": "Reação",
                "custo_acoes": 0,
                "simbolo": "reacao",
            },
        ],
    }


def construir_pagina_1() -> dict[str, Any]:
    """Constrói a estrutura da Página 1 (p. 580): Estatísticas Principais, Combate e Perícias."""
    atributos = [
        {"id": "for", "sigla": "FOR", "rotulo_oficial": "FORÇA"},
        {"id": "des", "sigla": "DES", "rotulo_oficial": "DESTREZA"},
        {"id": "con", "sigla": "CON", "rotulo_oficial": "CONSTITUIÇÃO"},
        {"id": "int", "sigla": "INT", "rotulo_oficial": "INTELIGÊNCIA"},
        {"id": "sab", "sigla": "SAB", "rotulo_oficial": "SABEDORIA"},
        {"id": "car", "sigla": "CAR", "rotulo_oficial": "CARISMA"},
    ]

    salvamentos = [
        {"id": "fortitude", "rotulo_oficial": "FORTITUDE", "atributo_chave": "con", "niveis_proficiencia": NIVEIS_PROFICIENCIA},
        {"id": "reflexos", "rotulo_oficial": "REFLEXOS", "atributo_chave": "des", "niveis_proficiencia": NIVEIS_PROFICIENCIA},
        {"id": "vontade", "rotulo_oficial": "VONTADE", "atributo_chave": "sab", "niveis_proficiencia": NIVEIS_PROFICIENCIA},
    ]

    pericias = [
        _slot_pericia_oficial(1, "acrobatismo", "acrobatismo", "ACROBATISMO", "des", tem_penalidade_armadura=True),
        _slot_pericia_oficial(2, "arcanismo", "arcanismo", "ARCANISMO", "int"),
        _slot_pericia_oficial(3, "atletismo", "atletismo", "ATLETISMO", "for", tem_penalidade_armadura=True),
        _slot_pericia_oficial(4, "diplomacia", "diplomacia", "DIPLOMACIA", "car"),
        _slot_pericia_oficial(5, "dissimulacao", "dissimulacao", "DISSIMULAÇÃO", "car"),
        _slot_pericia_oficial(6, "furtividade", "furtividade", "FURTIVIDADE", "des", tem_penalidade_armadura=True),
        _slot_pericia_oficial(7, "intimidacao", "intimidacao", "INTIMIDAÇÃO", "car"),
        _slot_pericia_oficial(8, "ladroagem", "ladroagem", "LADROAGEM", "des", tem_penalidade_armadura=True),
        _slot_pericia_oficial(9, "manufatura", "manufatura", "MANUFATURA", "int"),
        _slot_pericia_oficial(10, "medicina", "medicina", "MEDICINA", "sab"),
        _slot_pericia_oficial(11, "natureza", "natureza", "NATUREZA", "sab"),
        _slot_pericia_oficial(12, "ocultismo", "ocultismo", "OCULTISMO", "int"),
        _slot_pericia_oficial(13, "performance", "performance", "PERFORMANCE", "car"),
        _slot_pericia_oficial(14, "religiao", "religiao", "RELIGIÃO", "sab"),
        _slot_pericia_oficial(15, "saber_1", "saber", "SABER", "int", espaco_especializacao=True),
        _slot_pericia_oficial(16, "saber_2", "saber", "SABER", "int", espaco_especializacao=True),
        _slot_pericia_oficial(17, "sociedade", "sociedade", "SOCIEDADE", "int"),
        _slot_pericia_oficial(18, "sobrevivencia", "sobrevivencia", "SOBREVIVÊNCIA", "sab"),
    ]

    return {
        "numero_pagina_pdf": 1,
        "pagina_livro": 580,
        "titulo": "Estatísticas Principais, Combate e Perícias",
        "blocos": {
            "cabecalho": {
                "rotulo_oficial": "CABEÇALHO DO PERSONAGEM",
                "campos": [
                    _campo("nome_personagem", "NOME DO PERSONAGEM"),
                    _campo("nome_jogador", "NOME DO JOGADOR"),
                    _campo("pontos_experiencia", "PONTOS DE EXPERIÊNCIA (XP)", "numero"),
                    _campo("ancestralidade_e_heranca", "ANCESTRALIDADE E HERANÇA"),
                    _campo("biografia", "BIOGRAFIA"),
                    _campo("classe", "CLASSE"),
                    _campo("tamanho", "TAMANHO"),
                    _campo("tendencia", "TENDÊNCIA"),
                    _campo("tracos", "TRAÇOS", "lista_texto"),
                    _campo("divindade", "DIVINDADE"),
                    _campo("nivel", "NÍVEL", "numero", minimo=1, maximo=20),
                    _campo("pontos_heroismo", "PONTOS DE HEROÍSMO", "marcadores", maximo=3),
                ],
            },
            "atributos": {
                "rotulo_oficial": "ATRIBUTOS",
                "colunas_por_atributo": ["modificador", "valor"],
                "itens": atributos,
            },
            "cd_classe": {
                "rotulo_oficial": "CD DE CLASSE",
                "formula": ["10", "ATB_CHAVE", "PROF", "ITEM"],
                "rotulo_base_impresso": "CD BASE = 10",
                "niveis_proficiencia": NIVEIS_PROFICIENCIA,
                "campos": ["total", "mod_atributo_chave", "proficiencia", "grau_proficiencia", "item"],
            },
            "velocidade": {
                "rotulo_oficial": "VELOC",
                "unidade": "METROS",
                "campos": [
                    _campo("metros", "VELOC (METROS)", "numero_decimal"),
                    _campo("tipos_movimento_anotacoes", "TIPOS DE MOVIMENTO & ANOTAÇÕES"),
                ],
            },
            "classe_armadura": {
                "rotulo_oficial": "CLASSE DE ARMADURA",
                "rotulo_base_impresso": "CD BASE = 10",
                "formula": ["10", "DES_OU_LIMITE", "PROF", "ITEM"],
                "niveis_proficiencia": NIVEIS_PROFICIENCIA,
                "campos_ca": ["total", "des_ou_limite", "limite_des_armadura", "proficiencia", "grau_proficiencia", "item"],
                "proficiencias_armadura": [
                    {"id": "sem_armadura", "rotulo_oficial": "SEM ARMADURA", "niveis_proficiencia": NIVEIS_PROFICIENCIA},
                    {"id": "leve", "rotulo_oficial": "LEVE", "niveis_proficiencia": NIVEIS_PROFICIENCIA},
                    {"id": "media", "rotulo_oficial": "MÉDIA", "niveis_proficiencia": NIVEIS_PROFICIENCIA},
                    {"id": "pesada", "rotulo_oficial": "PESADA", "niveis_proficiencia": NIVEIS_PROFICIENCIA},
                ],
                "escudo": {
                    "rotulo_oficial": "Escudo",
                    "campos": [
                        _campo("bonus_ca", "+", "numero"),
                        _campo("dureza", "DUREZA", "numero"),
                        _campo("pv_max", "PV MÁX", "numero"),
                        _campo("limiar_quebra", "LQ", "numero"),
                        _campo("pv_atuais", "PV ATUAIS", "numero"),
                    ],
                },
            },
            "jogadas_salvamento": {
                "rotulo_oficial": "JOGADAS DE SALVAMENTO",
                "salvamentos": salvamentos,
                "anotacoes": _campo("anotacoes", "ANOTAÇÕES"),
            },
            "pontos_vida": {
                "rotulo_oficial": "PONTOS DE VIDA",
                "campos": [
                    _campo("max", "MÁX", "numero"),
                    _campo("atuais", "ATUAIS", "numero"),
                    _campo("temporarios", "TEMPORÁRIOS", "numero"),
                    _campo("ferido", "FERIDO", "numero"),
                    _campo("morrendo", "MORRENDO", "numero"),
                    _campo("resistencias_e_imunidades", "RESISTÊNCIAS E IMUNIDADES"),
                    _campo("condicoes", "CONDIÇÕES"),
                ],
            },
            "percepcao": {
                "rotulo_oficial": "PERCEPÇÃO",
                "formula": ["SAB", "PROF", "ITEM"],
                "niveis_proficiencia": NIVEIS_PROFICIENCIA,
                "campos": ["total", "sab", "proficiencia", "grau_proficiencia", "item", "sentidos"],
            },
            "golpes_corpo_a_corpo": {
                "rotulo_oficial": "GOLPES CORPO A CORPO",
                "quantidade_slots": 3,
                "slots": [_slot_golpe(i, "corpo_a_corpo") for i in range(1, 4)],
            },
            "golpes_a_distancia": {
                "rotulo_oficial": "GOLPES À DISTÂNCIA",
                "quantidade_slots": 3,
                "slots": [_slot_golpe(i, "distancia") for i in range(1, 4)],
            },
            "proficiencia_armas": {
                "rotulo_oficial": "PROFICIÊNCIA COM ARMAS",
                "quantidade_slots": 4,
                "itens": [
                    {"id": "simples", "rotulo_oficial": "SIMPLES", "niveis_proficiencia": NIVEIS_PROFICIENCIA, "permite_rotulo_customizado": False},
                    {"id": "marcial", "rotulo_oficial": "MARCIAL", "niveis_proficiencia": NIVEIS_PROFICIENCIA, "permite_rotulo_customizado": False},
                    {"id": "outra_1", "rotulo_oficial": "OUTRA", "niveis_proficiencia": NIVEIS_PROFICIENCIA, "permite_rotulo_customizado": True},
                    {"id": "outra_2", "rotulo_oficial": "OUTRA", "niveis_proficiencia": NIVEIS_PROFICIENCIA, "permite_rotulo_customizado": True},
                ],
            },
            "pericias": {
                "rotulo_oficial": "PERÍCIAS",
                "quantidade_linhas": 18,
                "quantidade_fixas": 16,
                "quantidade_saber": 2,
                "itens": pericias,
            },
            "idiomas": {
                "rotulo_oficial": "IDIOMAS",
                "tipo": "lista_texto",
            },
        },
    }


def construir_pagina_2() -> dict[str, Any]:
    """Constrói a estrutura da Página 2 (p. 581): Habilidades, Talentos e Inventário."""
    ancestralidade = [
        _slot_talento(1, "ESPECIAL 1º", "caracteristica_ancestralidade"),
        _slot_talento(2, "HERANÇA 1º", "heranca"),
        _slot_talento(3, "TALENTO 1º", "talento_ancestralidade"),
        _slot_talento(4, "TALENTO 5º", "talento_ancestralidade"),
        _slot_talento(5, "TALENTO 9º", "talento_ancestralidade"),
        _slot_talento(6, "TALENTO 13º", "talento_ancestralidade"),
        _slot_talento(7, "TALENTO 17º", "talento_ancestralidade"),
    ]

    rotulos_pericia = ["BIOGRAFIA", "2º", "4º", "6º", "8º", "10º", "12º", "14º", "16º", "18º", "20º"]
    talentos_pericia = [
        _slot_talento(i, rotulo, "talento_pericia")
        for i, rotulo in enumerate(rotulos_pericia, start=1)
    ]

    rotulos_gerais = ["3º", "7º", "11º", "15º", "19º"]
    talentos_gerais = [
        _slot_talento(i, rotulo, "talento_geral")
        for i, rotulo in enumerate(rotulos_gerais, start=1)
    ]

    classe_itens = [
        _slot_talento(1, "CARACTERÍSTICA 1º", "caracteristica_classe"),
        _slot_talento(2, "CARACTERÍSTICA 1º", "caracteristica_classe"),
        _slot_talento(3, "TALENTO 1º", "talento_classe"),
        _slot_talento(4, "TALENTO 2º", "talento_classe"),
        _slot_talento(5, "CARACTERÍSTICA 3º", "caracteristica_classe"),
        _slot_talento(6, "TALENTO 4º", "talento_classe"),
        _slot_talento(7, "CARACTERÍSTICA 5º", "caracteristica_classe"),
        _slot_talento(8, "TALENTO 6º", "talento_classe"),
        _slot_talento(9, "CARACTERÍSTICA 7º", "caracteristica_classe"),
        _slot_talento(10, "TALENTO 8º", "talento_classe"),
        _slot_talento(11, "CARACTERÍSTICA 9º", "caracteristica_classe"),
        _slot_talento(12, "TALENTO 10º", "talento_classe"),
        _slot_talento(13, "CARACTERÍSTICA 11º", "caracteristica_classe"),
        _slot_talento(14, "TALENTO 12º", "talento_classe"),
        _slot_talento(15, "CARACTERÍSTICA 13º", "caracteristica_classe"),
        _slot_talento(16, "TALENTO 14º", "talento_classe"),
        _slot_talento(17, "CARACTERÍSTICA 15º", "caracteristica_classe"),
        _slot_talento(18, "TALENTO 16º", "talento_classe"),
        _slot_talento(19, "CARACTERÍSTICA 17º", "caracteristica_classe"),
        _slot_talento(20, "TALENTO 18º", "talento_classe"),
        _slot_talento(21, "CARACTERÍSTICA 19º", "caracteristica_classe"),
        _slot_talento(22, "TALENTO 20º", "talento_classe"),
    ]

    talentos_bonus = [
        _slot_talento(1, "BÔNUS 1", "talento_bonus"),
        _slot_talento(2, "BÔNUS 2", "talento_bonus"),
    ]

    return {
        "numero_pagina_pdf": 2,
        "pagina_livro": 581,
        "titulo": "Habilidades, Talentos e Inventário",
        "blocos": {
            "habilidades_e_talentos_ancestralidade": {
                "rotulo_oficial": "HABILIDADES E TALENTOS DE ANCESTRALIDADE",
                "quantidade_slots": 7,
                "slots": ancestralidade,
            },
            "talentos_pericia": {
                "rotulo_oficial": "TALENTOS DE PERÍCIA",
                "quantidade_slots": 11,
                "slots": talentos_pericia,
            },
            "talentos_gerais": {
                "rotulo_oficial": "TALENTOS GERAIS",
                "quantidade_slots": 5,
                "slots": talentos_gerais,
            },
            "habilidades_e_talentos_classe": {
                "rotulo_oficial": "HABILIDADES E TALENTOS DE CLASSE",
                "quantidade_slots": 22,
                "slots": classe_itens,
            },
            "talentos_bonus": {
                "rotulo_oficial": "TALENTOS BÔNUS",
                "quantidade_slots": 2,
                "slots": talentos_bonus,
            },
            "inventario": {
                "rotulo_oficial": "INVENTÁRIO",
                "secoes": [
                    {
                        "id": "itens_vestidos",
                        "rotulo_oficial": "ITENS VESTIDOS",
                        "colunas": ["nome", "investido", "volume"],
                        "limite_investidos": 10,
                        "rotulo_investido": "INVESTIDO (MÁX 10)",
                    },
                    {
                        "id": "itens_preparados",
                        "rotulo_oficial": "ITENS PREPARADOS",
                        "colunas": ["nome", "quantidade", "volume"],
                    },
                    {
                        "id": "outros_itens",
                        "rotulo_oficial": "OUTROS ITENS",
                        "colunas": ["nome", "quantidade", "volume"],
                    },
                ],
                "resumo_carga": {
                    "rotulo_volume": "VOLUME",
                    "sobrecarregado": {
                        "rotulo_oficial": "SOBRECARREGADO = BASE 5 + FOR",
                        "base": 5,
                        "soma_atributo": "for",
                    },
                    "maximo": {
                        "rotulo_oficial": "MÁXIMO = BASE 10 + FOR",
                        "base": 10,
                        "soma_atributo": "for",
                    },
                },
                "riqueza": {
                    "moedas": [
                        {"id": "pc", "sigla": "PC", "nome": "Peças de Cobre", "valor_em_po": 0.01},
                        {"id": "pp", "sigla": "PP", "nome": "Peças de Prata", "valor_em_po": 0.1},
                        {"id": "po", "sigla": "PO", "nome": "Peças de Ouro", "valor_em_po": 1.0},
                        {"id": "pl", "sigla": "PL", "nome": "Peças de Platina", "valor_em_po": 10.0},
                    ],
                },
            },
        },
    }


def construir_pagina_3() -> dict[str, Any]:
    """Constrói a estrutura da Página 3 (p. 582): Perfil, Campanha e Ações."""
    slots_acoes_atividades = [
        {
            "indice": i,
            "campos": ["nome", "acoes", "tracos", "pagina", "descricao"],
        }
        for i in range(1, 7)
    ]

    slots_livres_reacoes = [
        {
            "indice": i,
            "tipos_marcacao": ["AÇÃO LIVRE", "REAÇÃO"],
            "campos": ["nome", "tipo", "tracos", "pagina", "acionamento", "descricao"],
        }
        for i in range(1, 5)
    ]

    return {
        "numero_pagina_pdf": 3,
        "pagina_livro": 582,
        "titulo": "Perfil, Campanha e Ações",
        "blocos": {
            "rascunho_personagem": {
                "rotulo_oficial": "RASCUNHO DO PERSONAGEM",
                "tipo": "area_visual",
            },
            "dados_biograficos": {
                "rotulo_oficial": "DADOS BIOGRÁFICOS",
                "campos": [
                    _campo("etnia", "ETNIA"),
                    _campo("nacionalidade", "NACIONALIDADE"),
                    _campo("local_nascimento", "LOCAL DE NASCIMENTO"),
                    _campo("idade", "IDADE"),
                    _campo("genero_pronomes", "GÊNERO E PRONOMES"),
                    _campo("altura", "ALTURA"),
                    _campo("peso", "PESO"),
                    _campo("aparencia", "APARÊNCIA", "texto_longo"),
                ],
            },
            "personalidade": {
                "rotulo_oficial": "PERSONALIDADE",
                "campos": [
                    _campo("atitude", "ATITUDE"),
                    _campo("crencas", "CRENÇAS"),
                    _campo("gostos", "GOSTOS"),
                    _campo("aversoes", "AVERSÕES"),
                    _campo("bordoes", "BORDÕES"),
                ],
            },
            "anotacoes_campanha": {
                "rotulo_oficial": "ANOTAÇÕES DE CAMPANHA",
                "campos": [
                    _campo("anotacoes", "ANOTAÇÕES", "texto_longo"),
                    _campo("aliados", "ALIADOS", "texto_longo"),
                    _campo("inimigos", "INIMIGOS", "texto_longo"),
                    _campo("organizacoes", "ORGANIZAÇÕES", "texto_longo"),
                ],
            },
            "acoes_e_atividades": {
                "rotulo_oficial": "AÇÕES E ATIVIDADES",
                "layout": "2 colunas x 3 linhas",
                "quantidade_slots": 6,
                "slots": slots_acoes_atividades,
            },
            "acoes_livres_e_reacoes": {
                "rotulo_oficial": "AÇÕES LIVRES E REAÇÕES",
                "layout": "2 colunas x 2 linhas",
                "quantidade_slots": 4,
                "slots": slots_livres_reacoes,
            },
        },
    }


def construir_pagina_4() -> dict[str, Any]:
    """Constrói a estrutura da Página 4 (p. 583): Conjuração e Magias."""
    return {
        "numero_pagina_pdf": 4,
        "pagina_livro": 583,
        "titulo": "Conjuração e Magias",
        "blocos": {
            "ataque_magia": {
                "rotulo_oficial": "ATAQUE DE MAGIA",
                "formula": ["ATB_CHAVE", "PROF"],
                "niveis_proficiencia": NIVEIS_PROFICIENCIA,
                "campos": ["total", "mod_atributo_chave", "proficiencia", "grau_proficiencia"],
            },
            "cd_magia": {
                "rotulo_oficial": "CD DE MAGIA",
                "formula": ["10", "ATB_CHAVE", "PROF"],
                "rotulo_base_impresso": "CD BASE 10",
                "niveis_proficiencia": NIVEIS_PROFICIENCIA,
                "campos": ["total", "mod_atributo_chave", "proficiencia", "grau_proficiencia"],
            },
            "tradicoes_magicas": {
                "rotulo_oficial": "TRADIÇÕES MÁGICAS",
                "tradicoes": [
                    {"id": "arcana", "rotulo_oficial": "ARCANAS"},
                    {"id": "ocultista", "rotulo_oficial": "OCULTISTAS"},
                    {"id": "primal", "rotulo_oficial": "PRIMAIS"},
                    {"id": "divina", "rotulo_oficial": "DIVINAS"},
                ],
                "estilos_conjuracao": [
                    {"id": "preparada", "rotulo_oficial": "PREPARADAS"},
                    {"id": "espontanea", "rotulo_oficial": "ESPONTÂNEAS"},
                ],
            },
            "espacos_magia_por_dia": {
                "rotulo_oficial": "ESPAÇOS DE MAGIA POR DIA",
                "nivel_truque_rotulo": "NÍVEL DE TRUQUE",
                "niveis_magia": list(range(1, 11)),
                "rotulo_remanescentes": "ESPAÇOS DE MAGIA ESPONTÂNEA REMANESCENTES",
            },
            "truques_magicos": {
                "rotulo_oficial": "TRUQUES MÁGICOS",
                "quantidade_slots": 7,
                "slots": [_slot_magia_pagina4(i, "truque", tem_checkbox_preparada=True) for i in range(1, 8)],
            },
            "magias_inatas": {
                "rotulo_oficial": "MAGIAS INATAS",
                "quantidade_slots": 2,
                "slots": [
                    _slot_magia_pagina4(i, "inata", tem_checkbox_preparada=False, tem_frequencia=True)
                    for i in range(1, 3)
                ],
            },
            "magias_foco": {
                "rotulo_oficial": "MAGIAS DE FOCO",
                "pontos_foco": {
                    "rotulo_oficial": "PONTOS DE FOCO",
                    "campos": ["atuais", "maximo"],
                },
                "quantidade_slots": 4,
                "slots": [_slot_magia_pagina4(i, "foco", tem_checkbox_preparada=False) for i in range(1, 5)],
            },
            "magias": {
                "rotulo_oficial": "MAGIAS",
                "layout": "16 linhas x 2 colunas",
                "quantidade_slots": 32,
                "slots": [_slot_magia_pagina4(i, "magia", tem_checkbox_preparada=True) for i in range(1, 33)],
            },
        },
    }


def construir_regras_calculo() -> dict[str, Any]:
    """Define as fórmulas mecânicas oficiais exibidas ou implícitas na ficha."""
    return {
        "modificador_atributo": "floor((valor - 10) / 2)",
        "bonus_proficiencia": {
            "destreinado": "0",
            "treinado": "2 + nivel",
            "especialista": "4 + nivel",
            "mestre": "6 + nivel",
            "lendario": "8 + nivel",
        },
        "classe_armadura": "10 + min(mod_des, limite_des_armadura) + proficiencia_armadura + bonus_item_armadura + bonus_escudo_se_erguido",
        "cd_classe": "10 + mod_atributo_chave_classe + proficiencia_cd_classe + bonus_item",
        "jogadas_salvamento": {
            "fortitude": "mod_con + proficiencia_fortitude + bonus_item",
            "reflexos": "mod_des + proficiencia_reflexos + bonus_item",
            "vontade": "mod_sab + proficiencia_vontade + bonus_item",
        },
        "percepcao": "mod_sab + proficiencia_percepcao + bonus_item",
        "pericias": "mod_atributo_chave + proficiencia_pericia + bonus_item + penalidade_armadura_se_aplicavel",
        "golpe_corpo_a_corpo": {
            "ataque": "mod_for_ou_acuidade_des + proficiencia_arma + bonus_item",
            "dano": "dados_arma + mod_for + especializacao_arma + outro",
        },
        "golpe_distancia": {
            "ataque": "mod_des + proficiencia_arma + bonus_item",
            "dano": "dados_arma + especial_ou_propulsivo_ou_arremesso + especializacao_arma + outro",
        },
        "pontos_vida": "pv_ancestralidade + (pv_classe + mod_con) * nivel + bonus_talentos",
        "ataque_magia": "mod_atributo_conjuracao + proficiencia_ataque_magia",
        "cd_magia": "10 + mod_atributo_conjuracao + proficiencia_cd_magia",
        "nivel_truque": "ceil(nivel / 2)",
        "limites_carga": {
            "sobrecarregado": "5 + mod_for",
            "maximo": "10 + mod_for",
            "limite_itens_investidos": 10,
        },
    }


def construir_mapeamento_fontes() -> dict[str, Any]:
    """Associa blocos da ficha oficial aos arquivos JSON em `dados/`."""
    return {
        "ancestralidade_e_heranca": "dados/ancestralidades_biografias.json",
        "biografia": "dados/ancestralidades_biografias.json",
        "idiomas": "dados/ancestralidades_biografias.json",
        "classe_e_cd_classe": ["dados/classes01.json", "dados/classes02.json", "dados/classes03.json"],
        "arquetipos_multiclasse": "dados/arquetipos_multiclasse.json",
        "pericias": "dados/pericias.json",
        "talentos_gerais_e_pericia": "dados/talentos.json",
        "equipamentos_armas_armaduras_inventario": "dados/equipamentos.json",
        "magias_e_foco": ["dados/magias01.json", "dados/magias02.json"],
        "companheiros_e_familiares": "dados/companheiros_familiares.json",
        "itens_magicos_e_investidos": "dados/itens_magicos_tesouros.json (pendente)",
        "conceitos_e_subclasses": "dados/conceitos_subclasses.json (pendente - Etapa 2)",
    }


def _slot_golpe_vazio(indice: int, tipo_golpe: str) -> dict[str, Any]:
    terceiro = "for" if tipo_golpe == "corpo_a_corpo" else "especial"
    return {
        "indice": indice,
        "arma": "",
        "ataque": {
            "total": 0,
            "mod_atributo": 0,
            "proficiencia": 0,
            "grau_proficiencia": "destreinado",
            "item": 0,
        },
        "dano": {
            "dados": "",
            terceiro: 0,
            "tipos_dano": [],
            "especializacao": 0,
            "outro": 0,
            "tracos": [],
        },
    }


def _slot_talento_vazio(slot: dict[str, Any]) -> dict[str, Any]:
    return {
        "indice": slot["indice"],
        "rotulo_oficial": slot["rotulo_oficial"],
        "categoria": slot["categoria"],
        "nome": "",
        "origem_regra": "",
        "pagina": None,
        "resumo": "",
    }


def _slot_magia_vazio(slot: dict[str, Any]) -> dict[str, Any]:
    item: dict[str, Any] = {
        "indice": slot["indice"],
        "nome": "",
        "nivel": None,
        "acoes": "",
        "componentes": [],
        "anotacoes": "",
    }
    if slot["tem_checkbox_preparada"]:
        item["preparada"] = False
    if slot["tem_frequencia"]:
        item["frequencia"] = ""
    return item


def construir_modelo_ficha_vazia(paginas: list[dict[str, Any]]) -> dict[str, Any]:
    """Gera o contrato de ficha vazia pronta para clonagem e preenchimento em Python."""
    p1 = paginas[0]["blocos"]
    p2 = paginas[1]["blocos"]
    p4 = paginas[3]["blocos"]

    pericias_vazias = [
        {
            "ordem_visual": p["ordem_visual"],
            "id": p["id"],
            "id_pericia_dados": p["id_pericia_dados"],
            "rotulo_oficial": p["rotulo_oficial"],
            "especializacao": "" if p["espaco_especializacao"] else None,
            "atributo_chave": p["atributo_chave"],
            "total": 0,
            "mod_atributo": 0,
            "proficiencia": 0,
            "grau_proficiencia": "destreinado",
            "item": 0,
            "penalidade_armadura": 0 if p["tem_penalidade_armadura"] else None,
        }
        for p in p1["pericias"]["itens"]
    ]

    return {
        "cabecalho": {
            "nome_personagem": "",
            "nome_jogador": "",
            "pontos_experiencia": 0,
            "ancestralidade_e_heranca": "",
            "biografia": "",
            "classe": "",
            "tamanho": "",
            "tendencia": "",
            "tracos": [],
            "divindade": "",
            "nivel": 1,
            "pontos_heroismo": 1,
        },
        "atributos": {
            atr["id"]: {"valor": 10, "modificador": 0}
            for atr in p1["atributos"]["itens"]
        },
        "cd_classe": {
            "total": 10,
            "mod_atributo_chave": 0,
            "proficiencia": 0,
            "grau_proficiencia": "destreinado",
            "item": 0,
        },
        "velocidade": {
            "metros": 0.0,
            "tipos_movimento_anotacoes": "",
        },
        "classe_armadura": {
            "total": 10,
            "des_ou_limite": 0,
            "limite_des_armadura": None,
            "proficiencia": 0,
            "grau_proficiencia": "destreinado",
            "item": 0,
            "proficiencias_armadura": {
                arm["id"]: "destreinado"
                for arm in p1["classe_armadura"]["proficiencias_armadura"]
            },
            "escudo": {
                "nome": "",
                "bonus_ca": 0,
                "dureza": 0,
                "pv_max": 0,
                "limiar_quebra": 0,
                "pv_atuais": 0,
            },
        },
        "jogadas_salvamento": {
            salv["id"]: {
                "atributo_chave": salv["atributo_chave"],
                "total": 0,
                "mod_atributo": 0,
                "proficiencia": 0,
                "grau_proficiencia": "destreinado",
                "item": 0,
            }
            for salv in p1["jogadas_salvamento"]["salvamentos"]
        } | {"anotacoes": ""},
        "pontos_vida": {
            "max": 0,
            "atuais": 0,
            "temporarios": 0,
            "ferido": 0,
            "morrendo": 0,
            "resistencias_e_imunidades": "",
            "condicoes": "",
        },
        "percepcao": {
            "total": 0,
            "mod_sab": 0,
            "proficiencia": 0,
            "grau_proficiencia": "destreinado",
            "item": 0,
            "sentidos": [],
        },
        "golpes_corpo_a_corpo": [_slot_golpe_vazio(i, "corpo_a_corpo") for i in range(1, 4)],
        "golpes_a_distancia": [_slot_golpe_vazio(i, "distancia") for i in range(1, 4)],
        "proficiencia_armas": [
            {
                "id": wp["id"],
                "rotulo": wp["rotulo_oficial"],
                "grau_proficiencia": "destreinado",
            }
            for wp in p1["proficiencia_armas"]["itens"]
        ],
        "pericias": pericias_vazias,
        "idiomas": [],
        "habilidades_e_talentos": {
            "ancestralidade": [
                _slot_talento_vazio(s)
                for s in p2["habilidades_e_talentos_ancestralidade"]["slots"]
            ],
            "pericia": [_slot_talento_vazio(s) for s in p2["talentos_pericia"]["slots"]],
            "gerais": [_slot_talento_vazio(s) for s in p2["talentos_gerais"]["slots"]],
            "classe": [
                _slot_talento_vazio(s)
                for s in p2["habilidades_e_talentos_classe"]["slots"]
            ],
            "bonus": [_slot_talento_vazio(s) for s in p2["talentos_bonus"]["slots"]],
        },
        "inventario": {
            "itens_vestidos": [],
            "itens_preparados": [],
            "outros_itens": [],
            "volume_total": 0.0,
            "volume_sobrecarregado": 5,
            "volume_maximo": 10,
            "itens_investidos_total": 0,
            "riqueza": {"pc": 0, "pp": 0, "po": 0, "pl": 0},
        },
        "perfil_e_campanha": {
            "rascunho_url": None,
            "dados_biograficos": {
                "etnia": "",
                "nacionalidade": "",
                "local_nascimento": "",
                "idade": "",
                "genero_pronomes": "",
                "altura": "",
                "peso": "",
                "aparencia": "",
            },
            "personalidade": {
                "atitude": "",
                "crencas": "",
                "gostos": "",
                "aversoes": "",
                "bordoes": "",
            },
            "anotacoes_campanha": {
                "anotacoes": "",
                "aliados": "",
                "inimigos": "",
                "organizacoes": "",
            },
        },
        "acoes_e_atividades": [
            {"indice": i, "nome": "", "acoes": "", "tracos": [], "pagina": None, "descricao": ""}
            for i in range(1, 7)
        ],
        "acoes_livres_e_reacoes": [
            {
                "indice": i,
                "nome": "",
                "tipo": "",
                "tracos": [],
                "pagina": None,
                "acionamento": "",
                "descricao": "",
            }
            for i in range(1, 5)
        ],
        "conjuracao": {
            "ataque_magia": {
                "total": 0,
                "mod_atributo_chave": 0,
                "proficiencia": 0,
                "grau_proficiencia": "destreinado",
            },
            "cd_magia": {
                "total": 10,
                "mod_atributo_chave": 0,
                "proficiencia": 0,
                "grau_proficiencia": "destreinado",
            },
            "tradicoes_marcadas": {
                "arcana": False,
                "ocultista": False,
                "primal": False,
                "divina": False,
            },
            "estilo_conjuracao": {
                "preparada": False,
                "espontanea": False,
            },
            "nivel_truque": 1,
            "espacos_magia_por_dia": {str(n): 0 for n in range(1, 11)},
            "espacos_magia_espontanea_remanescentes": {str(n): 0 for n in range(1, 11)},
            "truques_magicos": [_slot_magia_vazio(s) for s in p4["truques_magicos"]["slots"]],
            "magias_inatas": [_slot_magia_vazio(s) for s in p4["magias_inatas"]["slots"]],
            "magias_foco": {
                "pontos_foco": {"atuais": 0, "maximo": 0},
                "slots": [_slot_magia_vazio(s) for s in p4["magias_foco"]["slots"]],
            },
            "magias": [_slot_magia_vazio(s) for s in p4["magias"]["slots"]],
        },
    }


def gerar_estrutura_ficha() -> dict[str, Any]:
    """Monta o dicionário completo de `dados/estrutura_ficha.json`."""
    paginas = [
        construir_pagina_1(),
        construir_pagina_2(),
        construir_pagina_3(),
        construir_pagina_4(),
    ]

    return {
        "meta": {
            "titulo": "Pathfinder 2ª Edição — Estrutura Oficial da Ficha de Personagem",
            "fonte_pdf": "ref/Sheet Update.pdf",
            "paginas_livro": "580–583",
            "total_paginas": 4,
            "sistema": "Pathfinder 2E (PT-BR)",
            "observacoes_ficha_oficial": [
                "Na Página 1 (p. 580), a lista de Perícias imprime SOCIEDADE antes de SOBREVIVÊNCIA (seguindo a ordem alfabética do original em inglês Society -> Survival); a ordem visual oficial foi preservada integralmente.",
                "No PDF fonte, a camada OCR da Página 2 (p. 581) contém texto oculto duplicado da Página 1 herdado da diagramação (CharacterSheet.indd); a inspeção visual confirmou que a Página 2 exibe exclusivamente Habilidades/Talentos e Inventário.",
                "Na Página 1 (p. 580), o terceiro termo da fórmula de dano dos Golpes Corpo a Corpo é rotulado como FOR, enquanto nos Golpes À Distância o termo correspondente é rotulado como ESPECIAL (para arcos propulsivos/armas de arremesso).",
            ],
        },
        "legenda_referencia": construir_legenda_referencia(),
        "paginas": paginas,
        "regras_calculo_ficha": construir_regras_calculo(),
        "mapeamento_fontes_dados": construir_mapeamento_fontes(),
        "modelo_ficha_vazia": construir_modelo_ficha_vazia(paginas),
    }


def validar_estrutura_ficha(dados: dict[str, Any], caminho_pericias: Path = CAMINHO_PERICIAS) -> None:
    """Executa verificações estruturais e cruzamento de IDs com `dados/pericias.json`."""
    paginas = dados["paginas"]
    assert len(paginas) == 4, f"Esperadas 4 páginas, encontradas {len(paginas)}"
    assert [p["pagina_livro"] for p in paginas] == [580, 581, 582, 583]

    legenda = dados["legenda_referencia"]
    assert len(legenda["proficiencia"]) == 5
    assert len(legenda["icones_acao"]) == 5

    # Página 1
    p1 = paginas[0]["blocos"]
    assert len(p1["atributos"]["itens"]) == 6
    assert len(p1["jogadas_salvamento"]["salvamentos"]) == 3
    assert len(p1["classe_armadura"]["proficiencias_armadura"]) == 4
    assert len(p1["proficiencia_armas"]["itens"]) == 4
    assert len(p1["golpes_corpo_a_corpo"]["slots"]) == 3
    assert len(p1["golpes_a_distancia"]["slots"]) == 3

    pericias_p1 = p1["pericias"]["itens"]
    assert len(pericias_p1) == 18, f"Esperadas 18 linhas de perícia, encontradas {len(pericias_p1)}"
    ordem_rotulos = [p["rotulo_oficial"] for p in pericias_p1]
    assert ordem_rotulos.index("SOCIEDADE") < ordem_rotulos.index("SOBREVIVÊNCIA"), (
        "SOCIEDADE deve preceder SOBREVIVÊNCIA conforme layout oficial impresso na p. 580"
    )
    com_armadura = [p["id"] for p in pericias_p1 if p["tem_penalidade_armadura"]]
    assert com_armadura == ["acrobatismo", "atletismo", "furtividade", "ladroagem"]

    # Cruzamento 1:1 com dados/pericias.json
    with caminho_pericias.open("r", encoding="utf-8") as f:
        dados_pericias = json.load(f)
    ids_pericias_validos = {item["id"] for item in dados_pericias["pericias"]}
    for p in pericias_p1:
        assert p["id_pericia_dados"] in ids_pericias_validos, (
            f"id_pericia_dados '{p['id_pericia_dados']}' não encontrado em dados/pericias.json"
        )
    assert len({p["id_pericia_dados"] for p in pericias_p1}) == 17

    # Página 2
    p2 = paginas[1]["blocos"]
    assert len(p2["habilidades_e_talentos_ancestralidade"]["slots"]) == 7
    assert len(p2["talentos_pericia"]["slots"]) == 11
    assert len(p2["talentos_gerais"]["slots"]) == 5
    slots_classe = p2["habilidades_e_talentos_classe"]["slots"]
    assert len(slots_classe) == 22
    assert sum(1 for s in slots_classe if s["categoria"] == "caracteristica_classe") == 11
    assert sum(1 for s in slots_classe if s["categoria"] == "talento_classe") == 11
    assert len(p2["talentos_bonus"]["slots"]) == 2
    assert len(p2["inventario"]["secoes"]) == 3
    assert [m["id"] for m in p2["inventario"]["riqueza"]["moedas"]] == ["pc", "pp", "po", "pl"]

    # Página 3
    p3 = paginas[2]["blocos"]
    assert len(p3["dados_biograficos"]["campos"]) == 8
    assert len(p3["personalidade"]["campos"]) == 5
    assert len(p3["anotacoes_campanha"]["campos"]) == 4
    assert len(p3["acoes_e_atividades"]["slots"]) == 6
    assert len(p3["acoes_livres_e_reacoes"]["slots"]) == 4

    # Página 4
    p4 = paginas[3]["blocos"]
    assert len(p4["tradicoes_magicas"]["tradicoes"]) == 4
    assert len(p4["tradicoes_magicas"]["estilos_conjuracao"]) == 2
    assert p4["espacos_magia_por_dia"]["niveis_magia"] == list(range(1, 11))
    assert len(p4["truques_magicos"]["slots"]) == 7
    assert len(p4["magias_inatas"]["slots"]) == 2
    assert len(p4["magias_foco"]["slots"]) == 4
    assert len(p4["magias"]["slots"]) == 32

    # Alinhamento com modelo_ficha_vazia
    modelo = dados["modelo_ficha_vazia"]
    assert len(modelo["atributos"]) == 6
    assert len(modelo["golpes_corpo_a_corpo"]) == 3
    assert len(modelo["golpes_a_distancia"]) == 3
    assert len(modelo["proficiencia_armas"]) == 4
    assert len(modelo["pericias"]) == 18
    assert len(modelo["habilidades_e_talentos"]["ancestralidade"]) == 7
    assert len(modelo["habilidades_e_talentos"]["pericia"]) == 11
    assert len(modelo["habilidades_e_talentos"]["gerais"]) == 5
    assert len(modelo["habilidades_e_talentos"]["classe"]) == 22
    assert len(modelo["habilidades_e_talentos"]["bonus"]) == 2
    assert set(modelo["inventario"]["riqueza"].keys()) == {"pc", "pp", "po", "pl"}
    assert len(modelo["perfil_e_campanha"]["dados_biograficos"]) == 8
    assert len(modelo["perfil_e_campanha"]["personalidade"]) == 5
    assert len(modelo["perfil_e_campanha"]["anotacoes_campanha"]) == 4
    assert len(modelo["acoes_e_atividades"]) == 6
    assert len(modelo["acoes_livres_e_reacoes"]) == 4
    assert len(modelo["conjuracao"]["espacos_magia_por_dia"]) == 10
    assert len(modelo["conjuracao"]["espacos_magia_espontanea_remanescentes"]) == 10
    assert len(modelo["conjuracao"]["truques_magicos"]) == 7
    assert len(modelo["conjuracao"]["magias_inatas"]) == 2
    assert len(modelo["conjuracao"]["magias_foco"]["slots"]) == 4
    assert len(modelo["conjuracao"]["magias"]) == 32

    # Teste simples de clonagem sem compartilhamento de referência
    copia = deepcopy(modelo)
    assert copia == modelo


def main() -> None:
    """Gera `dados/estrutura_ficha.json`, valida todas as regras e imprime resumo."""
    estrutura = gerar_estrutura_ficha()
    validar_estrutura_ficha(estrutura)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_SAIDA.open("w", encoding="utf-8") as f:
        json.dump(estrutura, f, ensure_ascii=False, indent=2)
        f.write("\n")

    tamanho = CAMINHO_SAIDA.stat().st_size
    print(f"Arquivo gerado com sucesso: {CAMINHO_SAIDA} ({tamanho} bytes)")
    print(f"Páginas mapeadas: {[p['pagina_livro'] for p in estrutura['paginas']]}")
    print(f"Linhas de perícia validadas com pericias.json: {len(estrutura['modelo_ficha_vazia']['pericias'])}")
    print(
        "Slots Pág. 2 — Ancestralidade: "
        f"{len(estrutura['modelo_ficha_vazia']['habilidades_e_talentos']['ancestralidade'])}, "
        f"Perícia: {len(estrutura['modelo_ficha_vazia']['habilidades_e_talentos']['pericia'])}, "
        f"Gerais: {len(estrutura['modelo_ficha_vazia']['habilidades_e_talentos']['gerais'])}, "
        f"Classe: {len(estrutura['modelo_ficha_vazia']['habilidades_e_talentos']['classe'])}, "
        f"Bônus: {len(estrutura['modelo_ficha_vazia']['habilidades_e_talentos']['bonus'])}"
    )
    print(
        "Slots Pág. 3 — Ações/Atividades: "
        f"{len(estrutura['modelo_ficha_vazia']['acoes_e_atividades'])}, "
        f"Ações Livres/Reações: {len(estrutura['modelo_ficha_vazia']['acoes_livres_e_reacoes'])}"
    )
    print(
        "Slots Pág. 4 — Truques: "
        f"{len(estrutura['modelo_ficha_vazia']['conjuracao']['truques_magicos'])}, "
        f"Inatas: {len(estrutura['modelo_ficha_vazia']['conjuracao']['magias_inatas'])}, "
        f"Foco: {len(estrutura['modelo_ficha_vazia']['conjuracao']['magias_foco']['slots'])}, "
        f"Magias: {len(estrutura['modelo_ficha_vazia']['conjuracao']['magias'])}"
    )


if __name__ == "__main__":
    main()
