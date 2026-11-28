"""Gerador e validador de dados/ancestralidades_biografias.json a partir de ref/Anc Race.pdf."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "dadospf2" / "ancestralidades_biografias.json"


def slugify(texto: str) -> str:
    """Converte um nome em identificador snake_case ASCII."""
    normalizado = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(c for c in normalizado if not unicodedata.combining(c))
    return re.sub(r"[^a-zA-Z0-9]+", "_", sem_acentos.lower()).strip("_")


def construir_heranca(
    nome: str,
    descricao: str,
    sentidos_concedidos: list[str] | None = None,
    resistencias: list[str] | None = None,
    tracos_adicionais: list[str] | None = None,
    pv_ancestral_substituto: int | None = None,
    idiomas_adicionais: int = 0,
    habilidade_acao: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Monta entrada normalizada de herança ancestral."""
    entrada: dict[str, Any] = {
        "id": slugify(nome),
        "nome": nome,
        "descricao": descricao,
    }
    if sentidos_concedidos:
        entrada["sentidos_concedidos"] = sentidos_concedidos
    if resistencias:
        entrada["resistencias"] = resistencias
    if tracos_adicionais:
        entrada["tracos_adicionais"] = tracos_adicionais
    if pv_ancestral_substituto is not None:
        entrada["pv_ancestral_substituto"] = pv_ancestral_substituto
    if idiomas_adicionais:
        entrada["idiomas_adicionais"] = idiomas_adicionais
    if habilidade_acao:
        entrada["habilidade_acao"] = habilidade_acao
    return entrada


def construir_talento_ancestralidade(
    nome: str,
    nivel: int,
    tracos: list[str],
    descricao: str,
    acoes: str | None = None,
    pre_requisitos: str | None = None,
    frequencia: str | None = None,
    acionamento: str | None = None,
    especial: str | None = None,
    observacao_livro: str | None = None,
) -> dict[str, Any]:
    """Monta entrada normalizada de talento de ancestralidade."""
    entrada: dict[str, Any] = {
        "id": slugify(nome),
        "nome": nome,
        "nivel": nivel,
        "tracos": tracos,
        "acoes": acoes,
        "pre_requisitos": pre_requisitos,
        "frequencia": frequencia,
        "acionamento": acionamento,
        "especial": especial,
        "descricao": descricao,
    }
    if observacao_livro:
        entrada["observacao_livro"] = observacao_livro
    return entrada


def construir_biografia(
    nome: str,
    melhorias_atributo_opcoes: list[str],
    pericia_treinada_opcoes: list[str],
    saber_treinado: str,
    talento_pericia: str,
    descricao: str,
    talento_pericia_condicional: dict[str, str] | None = None,
    saber_tematico: bool = False,
) -> dict[str, Any]:
    """Monta entrada normalizada de biografia (antecedente)."""
    entrada: dict[str, Any] = {
        "id": slugify(nome),
        "nome": nome,
        "melhorias_atributo_opcoes": melhorias_atributo_opcoes,
        "melhoria_livre": True,
        "pericia_treinada_opcoes": pericia_treinada_opcoes,
        "saber_treinado": saber_treinado,
        "saber_tematico": saber_tematico,
        "talento_pericia": talento_pericia,
        "descricao": descricao,
    }
    if talento_pericia_condicional:
        entrada["talento_pericia_condicional"] = talento_pericia_condicional
    return entrada


def obter_regras_criacao_personagem() -> dict[str, Any]:
    """Retorna todas as regras de criação de personagem e matemática ABCD do Capítulo 1."""
    tabela_modificadores = [
        {"faixa": "1", "min": 1, "max": 1, "modificador": -5},
        {"faixa": "2-3", "min": 2, "max": 3, "modificador": -4},
        {"faixa": "4-5", "min": 4, "max": 5, "modificador": -3},
        {"faixa": "6-7", "min": 6, "max": 7, "modificador": -2},
        {"faixa": "8-9", "min": 8, "max": 9, "modificador": -1},
        {"faixa": "10-11", "min": 10, "max": 11, "modificador": 0},
        {"faixa": "12-13", "min": 12, "max": 13, "modificador": 1},
        {"faixa": "14-15", "min": 14, "max": 15, "modificador": 2},
        {"faixa": "16-17", "min": 16, "max": 17, "modificador": 3},
        {"faixa": "18-19", "min": 18, "max": 19, "modificador": 4},
        {"faixa": "20-21", "min": 20, "max": 21, "modificador": 5},
        {"faixa": "22-23", "min": 22, "max": 23, "modificador": 6},
        {"faixa": "24-25", "min": 24, "max": 25, "modificador": 7},
    ]

    return {
        "atributos": [
            {
                "id": "forca",
                "sigla": "FOR",
                "nome": "Força",
                "categoria": "Físico",
                "descricao": "Mede o poder físico; adicionada a rolagens de ataque/dano corpo a corpo (e dano de arremesso) e define o limite de Volume.",
            },
            {
                "id": "destreza",
                "sigla": "DES",
                "nome": "Destreza",
                "categoria": "Físico",
                "descricao": "Mede agilidade, equilíbrio e reflexos; adicionada a ataques à distância, ataques corpo a corpo com acuidade, CA e salvamentos de Reflexos.",
            },
            {
                "id": "constituicao",
                "sigla": "CON",
                "nome": "Constituição",
                "categoria": "Físico",
                "descricao": "Mede saúde geral e estamina; adicionada aos Pontos de Vida por nível e salvamentos de Fortitude.",
            },
            {
                "id": "inteligencia",
                "sigla": "INT",
                "nome": "Inteligência",
                "categoria": "Mental",
                "descricao": "Mede facilidade em aprender e raciocinar; concede perícias treinadas e idiomas adicionais no 1º nível quando positiva.",
            },
            {
                "id": "sabedoria",
                "sigla": "SAB",
                "nome": "Sabedoria",
                "categoria": "Mental",
                "descricao": "Mede bom senso, consciência e intuição; adicionada à Percepção e salvamentos de Vontade.",
            },
            {
                "id": "carisma",
                "sigla": "CAR",
                "nome": "Carisma",
                "categoria": "Mental",
                "descricao": "Mede magnetismo pessoal e força de personalidade; influencia interações sociais e habilidades de conjuração carismáticas.",
            },
        ],
        "sistema_abcd": {
            "valor_inicial": 10,
            "minimo_nivel_1": 8,
            "maximo_nivel_1": 18,
            "regra_melhoria": {
                "incremento_padrao": 2,
                "incremento_acima_ou_igual_18": 1,
                "regra_mesmo_passo": (
                    "Sempre que receber múltiplas melhorias de atributo ao mesmo tempo, "
                    "cada melhoria deve ser aplicada a um atributo diferente."
                ),
            },
            "regra_defeito": {
                "decremento": -2,
                "descricao": "Reduz o valor do atributo relacionado em 2 pontos.",
            },
            "etapas": [
                {"codigo": "A", "nome": "Ancestralidade", "descricao": "Melhorias e defeito da ancestralidade escolhida (além de eventuais defeitos voluntários)."},
                {"codigo": "B", "nome": "Biografia", "descricao": "Duas melhorias de atributo: 1 dentre duas opções da biografia e 1 melhoria livre."},
                {"codigo": "C", "nome": "Classe", "descricao": "Uma melhoria no atributo-chave da classe."},
                {"codigo": "D", "nome": "Determine os Valores", "descricao": "Quatro melhorias de atributo livres aplicadas a quatro atributos diferentes."},
            ],
            "defeitos_voluntarios": {
                "defeitos_sofridos": 2,
                "melhorias_livres_concedidas": 1,
                "regra": (
                    "No passo da ancestralidade, você pode optar por sofrer 2 defeitos adicionais "
                    "para ganhar 1 melhoria livre adicional. Não é permitido aplicar mais de um "
                    "defeito voluntário ao mesmo atributo, salvo se já tiver recebido melhoria nesse "
                    "mesmo passo (primeiro cancela a melhoria, segundo reduz em 2). Como exceção, "
                    "você pode aplicar duas melhorias livres a um atributo que sofreu defeito nesse passo."
                ),
            },
            "metodo_alternativo_rolagem": {
                "dados": "4d6 descartando o menor (6 vezes)",
                "ajuste_ancestralidade": "1 melhoria livre a menos do que o normal (defeitos aplicados normalmente).",
                "ajuste_biografia": "Apenas 1 melhoria em um dos atributos especificados (sem melhoria livre da biografia).",
                "teto_nivel_1": 18,
            },
            "tabela_1_1_modificadores": tabela_modificadores,
            "formula_modificador": "(valor - 10) // 2",
        },
        "resumo_classes_atributos": [
            {"id": "alquimista", "nome": "Alquimista", "atributo_chave": ["Inteligência"], "atributos_secundarios": ["Constituição", "Destreza"], "descricao_curta": "O alquimista arremessa bombas alquímicas e bebe concocções feitas por ele mesmo."},
            {"id": "barbaro", "nome": "Bárbaro", "atributo_chave": ["Força"], "atributos_secundarios": ["Constituição", "Destreza"], "descricao_curta": "O bárbaro corre em fúria pelo campo de batalha, esmagando adversários com temeridade."},
            {"id": "bardo", "nome": "Bardo", "atributo_chave": ["Carisma"], "atributos_secundarios": ["Constituição", "Destreza"], "descricao_curta": "O bardo usa performances e segredos de ocultismo para distrair adversários e inspirar aliados."},
            {"id": "campeao", "nome": "Campeão", "atributo_chave": ["Força", "Destreza"], "atributos_secundarios": ["Carisma", "Constituição"], "descricao_curta": "O campeão é um combatente dedicado a uma divindade que usa seu poder divino para se aprimorar e proteger aliados."},
            {"id": "clerigo", "nome": "Clérigo", "atributo_chave": ["Sabedoria"], "atributos_secundarios": ["Carisma", "Constituição"], "descricao_curta": "O clérigo convoca o poder de uma divindade para conjurar magias que curam aliados ou ferem seus adversários."},
            {"id": "druida", "nome": "Druida", "atributo_chave": ["Sabedoria"], "atributos_secundarios": ["Constituição", "Destreza"], "descricao_curta": "O druida usa a magia do mundo natural para fortalecer aliados e subjugar inimigos."},
            {"id": "feiticeiro", "nome": "Feiticeiro", "atributo_chave": ["Carisma"], "atributos_secundarios": ["Destreza", "Constituição"], "descricao_curta": "O poder mágico do feiticeiro flui de seu sangue e se manifesta como magias e habilidades fantásticas."},
            {"id": "guerreiro", "nome": "Guerreiro", "atributo_chave": ["Destreza", "Força"], "atributos_secundarios": ["Constituição"], "descricao_curta": "O guerreiro é um mestre de armas, técnicas marciais e poderosas combinações de ataque."},
            {"id": "ladino", "nome": "Ladino", "atributo_chave": ["Destreza", "Outro"], "atributos_secundarios": ["Carisma", "Constituição"], "descricao_curta": "O ladino é um mestre talentoso de malandragens que ataca seus inimigos quando eles menos esperam."},
            {"id": "mago", "nome": "Mago", "atributo_chave": ["Inteligência"], "atributos_secundarios": ["Destreza", "Constituição"], "descricao_curta": "O mago é um estudioso cuja reserva de conhecimento arcano energiza suas habilidades e magias maravilhosas."},
            {"id": "monge", "nome": "Monge", "atributo_chave": ["Destreza", "Força"], "atributos_secundarios": ["Constituição", "Sabedoria"], "descricao_curta": "O monge porta os segredos das artes marciais, demonstrando-os através de proezas impressionantes em batalha."},
            {"id": "patrulheiro", "nome": "Patrulheiro", "atributo_chave": ["Destreza", "Força"], "atributos_secundarios": ["Constituição", "Sabedoria"], "descricao_curta": "O patrulheiro é um mestre no uso de seus arredores, armadilhas e aliados animais para assolar inimigos."},
        ],
        "passos_criacao": [
            {"passo": 1, "titulo": "Crie um Conceito", "descricao": "Defina personalidade, passado, visão de mundo, fé, relação com aliados e ideias gerais do herói."},
            {"passo": 2, "titulo": "Comece a Definir seus Atributos", "descricao": "Inicie todos os seis valores de atributo em 10."},
            {"passo": 3, "titulo": "Selecione uma Ancestralidade", "descricao": "Escolha ancestralidade, melhorias/defeitos ancestrais (e eventuais defeitos voluntários), herança e talento de ancestralidade de 1º nível."},
            {"passo": 4, "titulo": "Determine a Biografia", "descricao": "Escolha a biografia, aplique suas 2 melhorias de atributo, treinamento em perícia e Saber, e anote o talento de perícia."},
            {"passo": 5, "titulo": "Escolha uma Classe", "descricao": "Defina a classe, nível 1 e aplique +2 no atributo-chave."},
            {"passo": 6, "titulo": "Defina seus Atributos", "descricao": "Aplique mais 4 melhorias de atributo livres (em atributos diferentes) e calcule os modificadores pela Tabela 1-1."},
            {"passo": 7, "titulo": "Registre Detalhes da Classe", "descricao": "Calcule PV iniciais (ancestralidade + classe + mod. CON), registre proficiências iniciais, perícias treinadas e características de 1º nível (incluindo magias)."},
            {"passo": 8, "titulo": "Compre Equipamentos", "descricao": "Gaste as 15 peças de ouro (150 pp) iniciais em armadura, armas e equipamentos, registrando moedas restantes."},
            {"passo": 9, "titulo": "Calcule Modificadores", "descricao": "Calcule Percepção, Salvamentos (Fortitude, Reflexos, Vontade), Golpes corpo a corpo e à distância, e Perícias."},
            {"passo": 10, "titulo": "Finalize os Detalhes", "descricao": "Defina tendência, divindade, idade, gênero/pronomes, CD de classe, Pontos de Heroísmo (1), CA e limites de Volume."},
        ],
        "graus_proficiencia": [
            {"id": "destreinado", "nome": "Destreinado", "sigla": "D", "bonus_fixo": 0, "soma_nivel": False, "formula": "0"},
            {"id": "treinado", "nome": "Treinado", "sigla": "T", "bonus_fixo": 2, "soma_nivel": True, "formula": "2 + nível"},
            {"id": "especialista", "nome": "Especialista", "sigla": "E", "bonus_fixo": 4, "soma_nivel": True, "formula": "4 + nível"},
            {"id": "mestre", "nome": "Mestre", "sigla": "M", "bonus_fixo": 6, "soma_nivel": True, "formula": "6 + nível"},
            {"id": "lendario", "nome": "Lendário", "sigla": "L", "bonus_fixo": 8, "soma_nivel": True, "formula": "8 + nível"},
        ],
        "formulas_ficha": {
            "pontos_vida": "pv_ancestralidade + (pv_classe + mod_constituicao) * nivel",
            "percepcao": "proficiencia_percepcao + mod_sabedoria + bonus_permanentes",
            "fortitude": "proficiencia_fortitude + mod_constituicao + bonus_permanentes",
            "reflexos": "proficiencia_reflexos + mod_destreza + bonus_permanentes",
            "vontade": "proficiencia_vontade + mod_sabedoria + bonus_permanentes",
            "cd_classe": "10 + proficiencia_cd_classe + mod_atributo_chave",
            "ca": "10 + min(mod_destreza, limite_des_armadura) + proficiencia_armadura + bonus_item_armadura + bonus_permanentes",
            "golpe_corpo_a_corpo": "mod_forca (ou mod_destreza se acuidade) + proficiencia_arma + bonus_item_arma",
            "golpe_distancia": "mod_destreza + proficiencia_arma + bonus_item_arma",
            "pericia": "mod_atributo_pericia + proficiencia_pericia + bonus_item + penalidade_armadura_se_aplicavel",
            "volume_sobrecarregado": "5 + mod_forca",
            "volume_maximo": "10 + mod_forca",
            "pontos_heroismo_inicial": 1,
        },
        "tabela_1_2_tendencias": [
            {"sigla": "OB", "nome": "Ordeiro e Bom", "eixo_ordem_caos": "Ordeiro", "eixo_bem_mal": "Bom", "tracos": ["Ordeiro", "Bom"]},
            {"sigla": "ON", "nome": "Ordeiro e Neutro", "eixo_ordem_caos": "Ordeiro", "eixo_bem_mal": "Neutro", "tracos": ["Ordeiro"]},
            {"sigla": "OM", "nome": "Ordeiro e Mau", "eixo_ordem_caos": "Ordeiro", "eixo_bem_mal": "Mau", "tracos": ["Ordeiro", "Mau"]},
            {"sigla": "NB", "nome": "Neutro e Bom", "eixo_ordem_caos": "Neutro", "eixo_bem_mal": "Bom", "tracos": ["Bom"]},
            {"sigla": "N", "nome": "Neutro Verdadeiro", "eixo_ordem_caos": "Neutro", "eixo_bem_mal": "Neutro", "tracos": []},
            {"sigla": "NM", "nome": "Neutro e Mau", "eixo_ordem_caos": "Neutro", "eixo_bem_mal": "Mau", "tracos": ["Mau"]},
            {"sigla": "CB", "nome": "Caótico e Bom", "eixo_ordem_caos": "Caótico", "eixo_bem_mal": "Bom", "tracos": ["Caótico", "Bom"]},
            {"sigla": "CN", "nome": "Caótico e Neutro", "eixo_ordem_caos": "Caótico", "eixo_bem_mal": "Neutro", "tracos": ["Caótico"]},
            {"sigla": "CM", "nome": "Caótico e Mau", "eixo_ordem_caos": "Caótico", "eixo_bem_mal": "Mau", "tracos": ["Caótico", "Mau"]},
        ],
        "subindo_de_nivel": {
            "xp_por_nivel": 1000,
            "niveis_melhoria_atributo": [5, 10, 15, 20],
            "niveis_talento_ancestralidade": [1, 5, 9, 13, 17],
            "lista_verificacao": [
                "Aumentar o nível em 1 e subtrair 1.000 XP do total de XP.",
                "Aumentar o máximo de Pontos de Vida pelo valor listado na classe.",
                "Acrescentar características da tabela de progressão da classe, melhorias de atributo e incrementos de perícia.",
                "Selecionar talentos conforme a tabela de progressão da classe (ancestralidade, classe, gerais e perícia).",
                "Adicionar magias e espaços de magia se a classe conceder conjuração.",
                "Aumentar bônus de proficiência em +1 pelo novo nível e recalcular estatísticas derivadas (CA, ataques, Percepção, salvamentos, perícias, CDs).",
                "Ajustar bônus de talentos e habilidades escalonados por nível (como Vitalidade) e bônus de CON/INT.",
            ],
        },
    }


def obter_ancestralidades() -> list[dict[str, Any]]:
    """Retorna as 6 ancestralidades básicas com suas 29 heranças e 78 talentos."""
    anao = {
        "id": "anao",
        "nome": "Anão",
        "raridade": "Comum",
        "pontos_vida": 10,
        "tamanho": "Médio",
        "velocidade_m": 6.0,
        "melhorias_atributo": ["Constituição", "Sabedoria", "Livre"],
        "defeito_atributo": "Carisma",
        "idiomas_iniciais": ["Comum", "Enânico"],
        "idiomas_adicionais_opcoes": ["Gnômico", "Goblin", "Jotun", "Órquico", "Subterrâneo", "Terran"],
        "regra_idiomas_adicionais": "Quantidade igual ao modificador de Inteligência (se positivo), mais idiomas prevalentes na região.",
        "tracos": ["Anão", "Humanoide"],
        "habilidades_especiais": [
            {
                "nome": "Visão no Escuro",
                "descricao": "Você enxerga na escuridão e sob luz fraca tão bem quanto é capaz de enxergar sob luz brilhante, embora sua visão na escuridão seja em preto e branco.",
            },
            {
                "nome": "Adaga de Clã",
                "descricao": "Você recebe uma adaga de clã (páginas 280 e 284) gratuitamente de seu clã, dada em seu nascimento. Vender esta adaga é um tabu terrível.",
            },
        ],
        "maturidade_anos": 25,
        "expectativa_vida_anos": 350,
        "exemplos_nomes": ["Agna", "Bodill", "Dolgrin", "Edrukk", "Grunyar", "Ingra", "Kazmuk", "Kotri", "Lupp", "Morgrym", "Rogar", "Rusilka", "Torra", "Yangrit"],
        "biografias_tipicas": ["Acólito", "Artesão", "Combatente", "Mercador", "Mineiro"],
        "classes_tipicas": ["Bárbaro", "Guerreiro", "Monge", "Patrulheiro", "Clérigo", "Druida"],
        "descricao": "Anões possuem uma reputação merecida como um povo estoico e austero, arraigado em cidadelas e cidades esculpidas de rocha sólida.",
        "herancas": [
            construir_heranca(
                "Anão da Forja",
                "Você adquire resistência a fogo igual à metade de seu nível (mínimo 1) e trata efeitos ambientais de calor como um passo menos extremo.",
                resistencias=["Fogo (metade do nível, mín. 1)"],
            ),
            construir_heranca(
                "Anão Guardião da Morte",
                "Quando rolar um sucesso em uma jogada de salvamento contra um efeito de necromancia, trate o resultado como um sucesso crítico.",
            ),
            construir_heranca(
                "Anão das Rochas",
                "Você recebe +2 de bônus de circunstância em CDs de Fortitude ou Reflexos contra Empurrar ou Derrubar e em salvamentos contra efeitos que tentem deixá-lo prostrado. Se qualquer efeito fosse forçá-lo a mover-se 3 metros ou mais, você é movido apenas metade da distância.",
            ),
            construir_heranca(
                "Anão de Sangue Ancestral",
                "Os heróis enânicos de antigamente conseguiam ignorar as magias de seus inimigos, e parte dessa resistência manifesta-se em você. Você ganha a reação Invocar Sangue Ancestral.",
                habilidade_acao={
                    "nome": "Invocar Sangue Ancestral",
                    "acoes": "reacao",
                    "acionamento": "Você tenta uma jogada de salvamento contra um efeito mágico, mas ainda não efetuou a rolagem.",
                    "efeito": "Você recebe +1 de bônus de circunstância na jogada de salvamento acionadora e até o final deste turno.",
                },
            ),
            construir_heranca(
                "Anão de Sangue Forte",
                "Você adquire resistência a veneno igual à metade de seu nível (mínimo 1). Cada salvamento bem-sucedido contra uma aflição de veneno reduz o estágio em 2 passos (ou 1 para veneno virulento), e cada sucesso crítico reduz em 3 passos (ou 2 para virulento).",
                resistencias=["Veneno (metade do nível, mín. 1)"],
            ),
        ],
        "talentos_ancestralidade": [
            construir_talento_ancestralidade("Aptidão com Pedras", 1, ["Anão"], "Recebe +2 de bônus de circunstância em Percepção para notar trabalhos incomuns e armadilhas mecânicas feitas ou escondidas em pedra. O MJ rola teste secreto automático com -2 de penalidade mesmo sem Buscar."),
            construir_talento_ancestralidade("Correr nas Rochas", 1, ["Anão"], "Ignora terreno difícil causado por detritos e solo irregular de pedra e terra. Ao usar Acrobatismo para se Equilibrar em pedra ou terra, não fica desprevenido e trata sucesso como sucesso crítico."),
            construir_talento_ancestralidade("Familiaridade com Armas Enânicas", 1, ["Anão"], "Treinado em machado de batalha, martelo de guerra e picareta. Obtém acesso a armas enânicas incomuns; trata armas enânicas marciais como simples e avançadas como marciais para proficiência."),
            construir_talento_ancestralidade("Ferro Desimpedido", 1, ["Anão"], "Ignora a redução de Velocidade de qualquer armadura que vestir. Reduz em 1,5 metros outra penalidade de Velocidade (como sobrecarregado ou magia; se múltiplas, reduza apenas uma)."),
            construir_talento_ancestralidade("Ódio Vingativo", 1, ["Anão"], "Escolha drow, duergar, gigante ou orc. Recebe +1 de bônus de circunstância no dano com armas e ataques desarmados (igual à quantidade de dados de dano da arma) contra criaturas com esse traço, ou contra uma criatura que cause dano crítico a você por 1 minuto.", especial="O MJ pode adicionar outros traços apropriados à lista de adversários ancestrais."),
            construir_talento_ancestralidade("Saber Enânico", 1, ["Anão"], "Recebe proficiência treinado em Manufatura e Religião (se já treinado em alguma, escolhe outra perícia) e torna-se treinado em Saber Enânico."),
            construir_talento_ancestralidade("Ardil com Armas Enânicas", 5, ["Anão"], "Sempre que atingir um acerto crítico usando machado de batalha, martelo de guerra, picareta ou qualquer arma enânica, aplica o efeito de especialização de crítico da arma.", pre_requisitos="Familiaridade com Armas Enânicas"),
            construir_talento_ancestralidade("Rolagem de Pedregulho", 5, ["Anão"], "Dê um Passo para o quadrado de um adversário do seu tamanho ou inferior, empurrando-o para trás de você (Fortitude contra CD de Atletismo para bloquear; se tentar o salvamento, sofre dano contundente igual ao seu nível + mod. Força, exceto em sucesso crítico).", acoes="2", pre_requisitos="Correr nas Rochas"),
            construir_talento_ancestralidade("Caminhar pelas Rochas", 9, ["Anão"], "Ganha mesclar-se às rochas como magia divina inata de 3º nível 1/dia. Permite encontrar trabalhos e armadilhas em pedra de proficiência lendária com Aptidão com Pedras (sem a penalidade de -2 se for lendário em Percepção)."),
            construir_talento_ancestralidade("Firmeza da Montanha", 9, ["Anão"], "Aumenta seus PV máximos em valor igual ao seu nível. CD de testes de recuperação sob morrendo passa a ser 9 + valor atual de morrendo (ou 6 + valor atual de morrendo se também possuir Vitalidade, cumulativo em PV)."),
            construir_talento_ancestralidade("Especialidade com Armas Enânicas", 13, ["Anão"], "Sempre que receber proficiência de especialista ou maior em determinadas armas pela classe, recebe essa mesma proficiência em machado de batalha, martelo de guerra, picareta e todas as armas enânicas treinadas.", pre_requisitos="Familiaridade com Armas Enânicas"),
        ],
    }

    elfo = {
        "id": "elfo",
        "nome": "Elfo",
        "raridade": "Comum",
        "pontos_vida": 6,
        "tamanho": "Médio",
        "velocidade_m": 9.0,
        "melhorias_atributo": ["Destreza", "Inteligência", "Livre"],
        "defeito_atributo": "Constituição",
        "idiomas_iniciais": ["Comum", "Élfico"],
        "idiomas_adicionais_opcoes": ["Celestial", "Dracônico", "Gnoll", "Gnômico", "Goblin", "Órquico", "Silvestre"],
        "regra_idiomas_adicionais": "Quantidade igual ao modificador de Inteligência (se positivo), mais idiomas prevalentes na região.",
        "tracos": ["Elfo", "Humanoide"],
        "habilidades_especiais": [
            {
                "nome": "Visão na Penumbra",
                "descricao": "Você enxerga sob luz fraca tão bem quanto é capaz de enxergar sob luz brilhante, ignorando a condição ocultado devido a luz fraca.",
            }
        ],
        "maturidade_anos": 20,
        "expectativa_vida_anos": 600,
        "exemplos_nomes": ["Aerel", "Amrunelara", "Caladrel", "Dardlara", "Faunra", "Heldalel", "Jathal", "Lanliss", "Oparal", "Seldlon", "Soumral", "Talathel", "Tessara", "Variel", "Yalandlara", "Zordlon"],
        "biografias_tipicas": ["Batedor", "Caçador", "Emissário", "Estudioso", "Nobre"],
        "classes_tipicas": ["Ladino", "Patrulheiro", "Alquimista", "Mago"],
        "descricao": "Elfos combinam uma graça extraterrena, intelecto apurado e uma conexão profunda com magia e longevidade.",
        "herancas": [
            construir_heranca(
                "Elfo Ártico",
                "Você adquire resistência a frio igual à metade de seu nível (mínimo 1) e trata efeitos ambientais de frio como um passo menos extremo.",
                resistencias=["Frio (metade do nível, mín. 1)"],
            ),
            construir_heranca(
                "Elfo das Cavernas",
                "Você nasceu ou passou muitos anos em túneis subterrâneos ou cavernas onde a luz é escassa. Você adquire visão no escuro.",
                sentidos_concedidos=["Visão no Escuro"],
            ),
            construir_heranca(
                "Elfo das Florestas",
                "Quando Escalar árvores, vinhas e folhagens, move-se à metade da Velocidade em sucesso e à Velocidade total em sucesso crítico (ou em sucesso com Escalada Rápida). Pode sempre usar Obter Cobertura em terreno de floresta mesmo sem obstáculo adjacente.",
            ),
            construir_heranca(
                "Elfo dos Sussurros",
                "Enquanto puder ouvir normalmente, usa Buscar para sentir criaturas indetectadas em cone de 18 metros (em vez de 9 m) e recebe +2 de bônus de circunstância ao usar Buscar para localizar criaturas indetectadas que possa ouvir a até 9 metros.",
            ),
            construir_heranca(
                "Elfo Vidente",
                "Pode conjurar o truque mágico detectar magia como magia arcana inata à vontade (elevado à metade do nível arredondada para cima) e recebe +1 de bônus de circunstância para Identificar Magia e Decifrar Escrita mágica.",
            ),
        ],
        "talentos_ancestralidade": [
            construir_talento_ancestralidade("Abandonado", 1, ["Elfo"], "Recebe +1 de bônus de circunstância em salvamentos contra efeitos de emoção e trata um sucesso como sucesso crítico."),
            construir_talento_ancestralidade("Elfo Ligeiro", 1, ["Elfo"], "Sua Velocidade aumenta em 1,5 metros."),
            construir_talento_ancestralidade("Familiaridade com Armas Élficas", 1, ["Elfo"], "Treinado em arco curto, arco curto composto, arco longo, arco longo composto, espada longa e rapieira. Obtém acesso a armas élficas incomuns; trata marciais como simples e avançadas como marciais."),
            construir_talento_ancestralidade("Longevidade Ancestral", 1, ["Elfo"], "Durante preparações diárias, ganha proficiência treinado temporária em uma perícia à sua escolha até as próximas preparações diárias.", pre_requisitos="pelo menos 100 anos de idade"),
            construir_talento_ancestralidade("Magia Extraterrena", 1, ["Elfo"], "Escolha um truque mágico da lista de magias arcanas; você pode conjurá-lo como magia arcana inata à vontade."),
            construir_talento_ancestralidade("Saber Élfico", 1, ["Elfo"], "Recebe proficiência treinado em Arcanismo e Natureza (ou outra perícia se já treinado) e torna-se treinado em Saber Élfico."),
            construir_talento_ancestralidade("Semblante Inabalável", 1, ["Elfo"], "Reduz em 1 rodada a duração de qualquer efeito mental que dure pelo menos 2 rodadas e melhora em um grau o sucesso em salvamentos contra efeitos de sono."),
            construir_talento_ancestralidade("Elegância com Armas Élficas", 5, ["Elfo"], "Aplica o efeito de especialização de crítico ao atingir acerto crítico com uma arma élfica ou listada em Familiaridade com Armas Élficas.", pre_requisitos="Familiaridade com Armas Élficas"),
            construir_talento_ancestralidade("Paciência Eterna", 5, ["Elfo"], "Pode gastar o dobro do tempo normal em um teste de Percepção ou perícia para obter +2 de bônus de circunstância e só falhar criticamente se o resultado for 10 abaixo da CD (1 natural não piora um grau)."),
            construir_talento_ancestralidade("Longevidade de Especialista", 9, ["Elfo"], "Ao usar Longevidade Ancestral, também torna-se especialista em uma perícia já treinada. Ao término, pode retreinar um incremento de perícia para tornar permanente uma dessas escolhas.", pre_requisitos="Longevidade Ancestral"),
            construir_talento_ancestralidade("Passada Élfica", 9, ["Elfo"], "Você pode Dar um Passo de 1,5 metros duas vezes gastando uma única ação.", acoes="1"),
            construir_talento_ancestralidade("Especialidade com Armas Élficas", 13, ["Elfo"], "Sempre que receber proficiência de especialista ou maior em armas pela classe, também recebe essa proficiência em arco curto, arco curto composto, arco longo, arco longo composto, espada longa, rapieira e armas élficas treinadas.", pre_requisitos="Familiaridade com Armas Élficas"),
            construir_talento_ancestralidade("Longevidade Universal", 13, ["Elfo"], "Uma vez por dia, pode refletir sobre suas experiências de vida e alterar as perícias escolhidas com Longevidade Ancestral e Longevidade de Especialista.", acoes="1", pre_requisitos="Longevidade de Especialista", frequencia="uma vez por dia"),
        ],
    }

    gnomo = {
        "id": "gnomo",
        "nome": "Gnomo",
        "raridade": "Comum",
        "pontos_vida": 8,
        "tamanho": "Pequeno",
        "velocidade_m": 7.5,
        "melhorias_atributo": ["Constituição", "Carisma", "Livre"],
        "defeito_atributo": "Força",
        "idiomas_iniciais": ["Comum", "Gnômico", "Silvestre"],
        "idiomas_adicionais_opcoes": ["Dracônico", "Élfico", "Enânico", "Goblin", "Jotun", "Órquico"],
        "regra_idiomas_adicionais": "Quantidade igual ao modificador de Inteligência (se positivo), mais idiomas prevalentes na região.",
        "tracos": ["Gnomo", "Humanoide"],
        "habilidades_especiais": [
            {
                "nome": "Visão na Penumbra",
                "descricao": "Você enxerga sob luz fraca tão bem quanto é capaz de enxergar sob luz brilhante, ignorando a condição ocultado devido a luz fraca.",
            }
        ],
        "maturidade_anos": 18,
        "expectativa_vida_anos": 400,
        "exemplos_nomes": ["Abroshtor", "Bastargre", "Besh", "Fijit", "Halungalom", "Krolmnite", "Neji", "Majet", "Pai", "Poshment", "Queck", "Trig", "Zarzuket", "Zatqualmie"],
        "biografias_tipicas": ["Apresentador", "Mercador", "Nômade", "Apostador", "Encantador de Animais", "Funileiro", "Taverneiro"],
        "classes_tipicas": ["Druida", "Feiticeiro"],
        "descricao": "Descendentes do Primeiro Mundo feérico, gnomos são curiosos, excêntricos e dependem de novidades e magia para evitar o Descoloramento.",
        "herancas": [
            construir_heranca(
                "Gnomo Camaleão",
                "Pode mudar a cor base e saturação da pele e cabelo (1 ação para mudanças menores; 1 hora para todo o corpo). Quando em ambiente similar, usa 1 ação para receber +2 de bônus de circunstância em Furtividade.",
            ),
            construir_heranca(
                "Gnomo Manancial",
                "Escolha arcana, divina ou ocultista. Ganha um truque mágico dessa tradição como magia inata à vontade e converte a tradição de futuras magias inatas de talentos de gnomo para a escolhida.",
            ),
            construir_heranca(
                "Gnomo Sensitivo",
                "Recebe faro impreciso de 9 metros e +2 de bônus de circunstância em Percepção para localizar uma criatura indetectada dentro do alcance do faro.",
                sentidos_concedidos=["Faro (impreciso 9 m)"],
            ),
            construir_heranca(
                "Gnomo Tocado-pelas-Fadas",
                "Recebe o traço fada além de gnomo e humanoide. Escolhe um truque mágico primal para conjurar à vontade e pode trocá-lo 1/dia meditando por 10 minutos.",
                tracos_adicionais=["Fada"],
            ),
            construir_heranca(
                "Gnomo Umbral",
                "Uma conexão com svirfneblin, fadas sombrias ou outra fonte permite enxergar na escuridão completa. Você adquire visão no escuro.",
                sentidos_concedidos=["Visão no Escuro"],
            ),
        ],
        "talentos_ancestralidade": [
            construir_talento_ancestralidade("Companheiro das Fadas", 1, ["Gnomo"], "Recebe +2 de bônus de circunstância em Percepção e salvamentos contra fadas. Pode Impressionar uma fada imediatamente sem 1 minuto de conversa com -5 de penalidade (e repetir após 1 minuto se falhar).", especial="Sem penalidade se possuir o talento de perícia Cumprimento Caloroso."),
            construir_talento_ancestralidade("Cúmplice Animal", 1, ["Gnomo"], "Você adquire um familiar utilizando as regras da página 217."),
            construir_talento_ancestralidade("Elocucionista de Escavadores", 1, ["Gnomo"], "Pode fazer perguntas, receber respostas e usar Diplomacia com animais que tenham Velocidade de escavação."),
            construir_talento_ancestralidade("Familiaridade com Armas Gnômicas", 1, ["Gnomo"], "Treinado em glaive e kukri. Obtém acesso a kukris e armas gnômicas incomuns; trata marciais como simples e avançadas como marciais."),
            construir_talento_ancestralidade("Magia do Primeiro Mundo", 1, ["Gnomo"], "Escolha um truque mágico da lista de magias primais para conjurar como magia primal inata à vontade."),
            construir_talento_ancestralidade("Obsessão Gnômica", 1, ["Gnomo"], "Torna-se treinado em uma perícia de Saber escolhida. Escala para especialista (2º nível), mestre (7º nível) e lendário (15º nível) tanto nesse Saber quanto no Saber concedido pela biografia."),
            construir_talento_ancestralidade("Sentir Ilusão", 1, ["Gnomo"], "Recebe +1 de bônus de circunstância em Percepção e salvamentos de Vontade contra ilusões; o MJ rola teste secreto automático para desacreditar ilusões a até 3 metros."),
            construir_talento_ancestralidade("Elocucionista Animal", 5, ["Gnomo"], "Pode falar com todos os animais e recebe +1 de bônus de circunstância para Impressionar animais.", pre_requisitos="Elocucionista de Escavadores"),
            construir_talento_ancestralidade("Fonte Energizada", 5, ["Gnomo"], "Recupera 1 Ponto de Foco até seu máximo normal.", acoes="1", pre_requisitos="reservatório de foco e pelo menos uma magia inata de herança/talento gnômico da mesma tradição de alguma magia de foco", frequencia="uma vez por dia"),
            construir_talento_ancestralidade("Inovação com Armas Gnômicas", 5, ["Gnomo"], "Aplica o efeito de especialização de crítico da arma em acertos críticos com glaive, kukri ou qualquer arma gnômica.", pre_requisitos="Familiaridade com Armas Gnômicas"),
            construir_talento_ancestralidade("Adepto do Primeiro Mundo", 9, ["Gnomo"], "Adquire fogo feérico e invisibilidade como magias primais inatas de 2º nível (1/dia cada).", pre_requisitos="pelo menos uma magia primal inata"),
            construir_talento_ancestralidade("Conduíte Vivaz", 9, ["Gnomo"], "Ao descansar por 10 minutos, ganha PV igual a modificador de Constituição × metade do seu nível, cumulativo com Tratar Ferimentos."),
            construir_talento_ancestralidade("Especialidade com Armas Gnômicas", 13, ["Gnomo"], "Sempre que receber proficiência de especialista ou maior em armas pela classe, recebe a mesma proficiência em glaive, kukri e armas gnômicas treinadas.", pre_requisitos="Familiaridade com Armas Gnômicas"),
        ],
    }

    goblin = {
        "id": "goblin",
        "nome": "Goblin",
        "raridade": "Comum",
        "pontos_vida": 6,
        "tamanho": "Pequeno",
        "velocidade_m": 7.5,
        "melhorias_atributo": ["Destreza", "Carisma", "Livre"],
        "defeito_atributo": "Sabedoria",
        "idiomas_iniciais": ["Comum", "Goblin"],
        "idiomas_adicionais_opcoes": ["Dracônico", "Enânico", "Gnoll", "Gnômico", "Halfling", "Órquico"],
        "regra_idiomas_adicionais": "Quantidade igual ao modificador de Inteligência (se positivo), mais idiomas prevalentes na região.",
        "tracos": ["Goblin", "Humanoide"],
        "habilidades_especiais": [
            {
                "nome": "Visão no Escuro",
                "descricao": "Você enxerga na escuridão e sob luz fraca tão bem quanto é capaz de enxergar sob luz brilhante, embora sua visão na escuridão seja em preto e branco.",
            }
        ],
        "maturidade_anos": 8,
        "expectativa_vida_anos": 50,
        "exemplos_nomes": ["Ak", "Bokker", "Frum", "Guzmuk", "Krobby", "Loohi", "Mazmord", "Neeka", "Omgot", "Ranzak", "Rickle", "Tup", "Wakla", "Yonk", "Zibini"],
        "biografias_tipicas": ["Acrobata", "Apresentador", "Caçador", "Criança de Rua", "Criminoso", "Gladiador"],
        "classes_tipicas": ["Alquimista", "Bardo", "Ladino", "Feiticeiro"],
        "descricao": "Enérgicos, inventivos e adaptáveis, goblins vivem o momento e buscam seu lugar entre os povos civilizados.",
        "herancas": [
            construir_heranca(
                "Goblin Bucho-de-Ferro",
                "Pode subsistir com lixo em assentamentos sem usar Subsistir e comer/beber enquanto enjoado. Recebe +2 de bônus de circunstância em salvamentos contra aflições/condição enjoado de coisas ingeridas (sucessos em Fortitude viram sucesso crítico).",
            ),
            construir_heranca(
                "Goblin Couro-Chamuscado",
                "Recebe resistência a fogo igual à metade de seu nível (mínimo 1). Teste simples para remover dano persistente de fogo tem CD 10 (ou CD 5 com ajuda).",
                resistencias=["Fogo (metade do nível, mín. 1)"],
            ),
            construir_heranca(
                "Goblin Dentes-de-Navalha",
                "Adquire um ataque desarmado com mandíbulas que causa 1d6 de dano perfurante (grupo pugilato, traços acuidade e desarmado).",
            ),
            construir_heranca(
                "Goblin Inquebrável",
                "Recebe 10 Pontos de Vida de sua ancestralidade em vez de 6. Reduz o dano de queda como se tivesse caído apenas metade da distância.",
                pv_ancestral_substituto=10,
            ),
            construir_heranca(
                "Goblin das Neves",
                "Recebe resistência a frio igual à metade de seu nível (mínimo 1) e trata efeitos ambientais de frio como um passo menos extremo.",
                resistencias=["Frio (metade do nível, mín. 1)"],
            ),
        ],
        "talentos_ancestralidade": [
            construir_talento_ancestralidade("Canção Goblin", 1, ["Goblin"], "Teste de Performance contra CD de Vontade de 1 inimigo a até 9 m (2 em especialista, 4 em mestre, 8 em lendário); sucesso aplica -1 de estado em Percepção e Vontade por 1 rodada (1 minuto em crítico).", acoes="1"),
            construir_talento_ancestralidade("Catador da Cidade", 1, ["Goblin"], "Recebe +1 de bônus de circunstância para Subsistir usando Sociedade ou Sobrevivência em assentamento e pode Ganhar Proventos simultaneamente (+1 bônus; +2 com Bucho-de-Ferro).", especial="Com a herança goblin bucho-de-ferro, aumente o bônus para +2."),
            construir_talento_ancestralidade("Cavaleiro Brusco", 1, ["Goblin"], "Recebe o talento Cavalgar, +1 de bônus de circunstância em Natureza para Comandar um Animal em cão goblin ou lobo de montaria, e pode escolher lobo como companheiro animal montaria."),
            construir_talento_ancestralidade("Familiaridade com Armas Goblinoides", 1, ["Goblin"], "Treinado em cortacão e fatia-cavalo. Obtém acesso a armas goblinoides incomuns; trata marciais como simples e avançadas como marciais."),
            construir_talento_ancestralidade("Funileiro de Sucata", 1, ["Goblin"], "Manufatura itens de nível 0 (armas, não armaduras) por 1/4 do Preço como itens de má qualidade sem sofrer a penalidade deles; pode usar sucatas para descontar 1 dia extra ao Manufaturar."),
            construir_talento_ancestralidade("Muito Sorrateiro", 1, ["Goblin"], "Move 1,5 metros a mais ao Esgueirar (até sua Velocidade) e não se torna observado entre ações sequenciais de Esgueirar se terminar o turno com cobertura ou ocultado."),
            construir_talento_ancestralidade(
                "Passadela Goblin",
                1,
                ["Goblin"],
                "Você aproveita o movimento de um aliado adjacente para ajustar sua posição. Você Dá um Passo.",
                acoes="reacao",
                acionamento="Um aliado termina uma ação de movimento adjacente a você.",
                observacao_livro="Errata editorial do Livro Básico PT-BR (p. 49 / Anc Race.pdf pág. 31): o texto do acionamento foi impresso sob o rótulo 'Pré-requisitos'.",
            ),
            construir_talento_ancestralidade("Saber Goblin", 1, ["Goblin"], "Recebe proficiência treinado em Furtividade e Natureza (ou outra perícia se já treinado) e torna-se treinado em Saber Goblin."),
            construir_talento_ancestralidade("Taca Fogo!", 1, ["Goblin"], "Magias e itens alquímicos que causem dano de fogo recebem bônus de estado no dano igual à metade do nível da magia ou 1/4 do nível do item (mínimo 1), além de +1 de estado em dano persistente de fogo."),
            construir_talento_ancestralidade("Frenesi com Armas Goblinoides", 5, ["Goblin"], "Aplica o efeito de especialização de crítico da arma em acertos críticos usando cortacão, fatia-cavalo ou qualquer arma goblinoide.", pre_requisitos="Familiaridade com Armas Goblinoides"),
            construir_talento_ancestralidade("Escalador de Cavernas", 9, ["Goblin"], "Você adquire uma Velocidade de escalada de 3 metros."),
            construir_talento_ancestralidade("Passadela Apressada", 9, ["Goblin"], "Quando usar Passadela Goblin, pode Andar até metade de sua Velocidade em vez de Dar um Passo.", pre_requisitos="Passadela Goblin"),
            construir_talento_ancestralidade("Especialidade com Armas Goblinoides", 13, ["Goblin"], "Sempre que receber proficiência de especialista ou maior em armas pela classe, recebe essa proficiência em cortacão, fatia-cavalo e armas goblinoides treinadas.", pre_requisitos="Familiaridade com Armas Goblinoides"),
            construir_talento_ancestralidade("Muito, Muito Sorrateiro", 13, ["Goblin"], "Pode mover-se até sua Velocidade completa ao Esgueirar e não precisa mais de cobertura ou ocultação para se Esconder ou se Esgueirar.", pre_requisitos="Muito Sorrateiro"),
        ],
    }

    halfling = {
        "id": "halfling",
        "nome": "Halfling",
        "raridade": "Comum",
        "pontos_vida": 6,
        "tamanho": "Pequeno",
        "velocidade_m": 7.5,
        "melhorias_atributo": ["Destreza", "Sabedoria", "Livre"],
        "defeito_atributo": "Força",
        "idiomas_iniciais": ["Comum", "Halfling"],
        "idiomas_adicionais_opcoes": ["Élfico", "Enânico", "Gnômico", "Goblin"],
        "regra_idiomas_adicionais": "Quantidade igual ao modificador de Inteligência (se positivo), mais idiomas prevalentes na região.",
        "tracos": ["Halfling", "Humanoide"],
        "habilidades_especiais": [
            {
                "nome": "Olhos Aguçados",
                "descricao": "Recebe +2 de bônus de circunstância ao usar Buscar para encontrar criaturas escondidas ou indetectadas a até 9 metros. Reduz a CD do teste simples para 3 contra alvo ocultado ou 9 contra alvo escondido.",
            }
        ],
        "maturidade_anos": 20,
        "expectativa_vida_anos": 150,
        "exemplos_nomes": ["Anafa", "Antal", "Bellis", "Boram", "Etune", "Filiu", "Jamir", "Kaleb", "Linna", "Marra", "Miro", "Rillka", "Sistra", "Sumak", "Yamyra"],
        "biografias_tipicas": ["Acrobata", "Apresentador", "Criança de Rua", "Criminoso", "Emissário", "Operário"],
        "classes_tipicas": ["Clérigo", "Ladino", "Monge", "Patrulheiro"],
        "descricao": "Otimistas, adaptáveis e dotados de sorte excepcional, halflings equilibram a vontade de viajar com o apego ao conforto do lar.",
        "herancas": [
            construir_heranca(
                "Halfling das Colinas",
                "Ao recuperar PV durante a noite, adicione seu nível aos PV recuperados. Quando alguém usar Medicina para Tratar seus Ferimentos, pode comer um lanche para adicionar seu nível aos PV recuperados.",
            ),
            construir_heranca(
                "Halfling do Crepúsculo",
                "Você adquire visão na penumbra.",
                sentidos_concedidos=["Visão na Penumbra"],
            ),
            construir_heranca(
                "Halfling Intrépido",
                "Quando rolar um sucesso em uma jogada de salvamento contra um efeito de emoção, trate o resultado como um sucesso crítico.",
            ),
            construir_heranca(
                "Halfling das Matas",
                "Você ignora o terreno difícil de árvores, folhagens e matagais.",
            ),
            construir_heranca(
                "Halfling Nômade",
                "Você adquire dois idiomas adicionais (comuns ou incomuns disponíveis) e ganha outro idioma novo sempre que selecionar o talento Poliglota.",
                idiomas_adicionais=2,
            ),
        ],
        "talentos_ancestralidade": [
            construir_talento_ancestralidade("Distração nas Sombras", 1, ["Halfling"], "Pode usar criaturas pelo menos um tamanho maior que você (Médio ou maior) como cobertura para Esconder e Esgueirar."),
            construir_talento_ancestralidade("Familiaridade com Armas Halflings", 1, ["Halfling"], "Treinado em cajado-funda halfling, espada curta e funda. Obtém acesso a armas halflings incomuns; trata marciais como simples e avançadas como marciais."),
            construir_talento_ancestralidade("Fundeiro Titânico", 1, ["Halfling"], "Ao acertar um ataque com funda contra uma criatura Grande ou maior, aumenta o tamanho do dado de dano da arma em um passo."),
            construir_talento_ancestralidade("Halfling Atento", 1, ["Halfling"], "Recebe +2 de bônus de circunstância em Percepção com Sentir Motivação para perceber encantados/possuídos (teste secreto automático com -2 se não estiver usando ativamente). Pode usar Auxiliar em salvamentos contra encantamento ou possessão."),
            construir_talento_ancestralidade("Halfling Liberto", 1, ["Halfling"], "Sucessos para Escapar ou salvamentos contra agarrado/restringido viram sucesso crítico; falhas inimigas para Agarrar viram falha crítica; Atracar exige teste de Atletismo."),
            construir_talento_ancestralidade("Pés Firmes", 1, ["Halfling"], "Sucessos em Acrobatismo para Equilibrar ou Atletismo para Escalar viram sucesso crítico e você não fica desprevenido nessas ações."),
            construir_talento_ancestralidade("Saber Halfling", 1, ["Halfling"], "Recebe proficiência treinado em Acrobatismo e Furtividade (ou outra perícia se já treinado) e torna-se treinado em Saber Halfling."),
            construir_talento_ancestralidade("Sorte de Halfling", 1, ["Fortuna", "Halfling"], "Permite rerrolar o teste de perícia ou jogada de salvamento que falhou, devendo usar o novo resultado.", acoes="reacao", frequencia="uma vez por dia", acionamento="Você falha em um teste de perícia ou jogada de salvamento."),
            construir_talento_ancestralidade("Adaptabilidade Cultural", 5, ["Halfling"], "Recebe o talento geral Ancestralidade Adotada e um talento de ancestralidade de 1º nível da ancestralidade escolhida."),
            construir_talento_ancestralidade("Embuste com Armas Halflings", 5, ["Halfling"], "Aplica o efeito de especialização de crítico ao atingir acerto crítico usando uma arma halfling ou listada em Familiaridade com Armas Halflings.", pre_requisitos="Familiaridade com Armas Halflings"),
            construir_talento_ancestralidade("Irreprimível", 9, ["Halfling"], "Sucessos contra efeitos de emoção viram sucesso crítico; se possuir herança halfling intrépido, falhas críticas contra efeitos de emoção viram falhas normais."),
            construir_talento_ancestralidade("Sorte Guiada", 9, ["Halfling"], "Pode usar Sorte de Halfling 2/dia: uma no acionamento normal e outra ao falhar em teste de Percepção ou rolagem de ataque.", pre_requisitos="Sorte de Halfling"),
            construir_talento_ancestralidade("Especialidade com Armas Halflings", 13, ["Halfling"], "Sempre que receber proficiência de especialista ou maior em armas pela classe, recebe essa proficiência em cajado-funda halfling, espada curta, funda e armas halflings treinadas.", pre_requisitos="Familiaridade com Armas Halflings"),
            construir_talento_ancestralidade("Sombras Incessantes", 13, ["Halfling"], "Não precisa de cobertura ou ocultação para se Esconder ou Esgueirar; recebe cobertura (em vez de cobertura menor) e cobertura maior (em vez de cobertura) de outras criaturas.", pre_requisitos="Distração nas Sombras"),
        ],
    }

    humano = {
        "id": "humano",
        "nome": "Humano",
        "raridade": "Comum",
        "pontos_vida": 8,
        "tamanho": "Médio",
        "velocidade_m": 7.5,
        "melhorias_atributo": ["Livre", "Livre"],
        "defeito_atributo": None,
        "idiomas_iniciais": ["Comum"],
        "idiomas_adicionais_opcoes": ["Qualquer idioma comum ou regional com acesso"],
        "regra_idiomas_adicionais": "Quantidade igual a 1 + modificador de Inteligência (mínimo 1).",
        "tracos": ["Humano", "Humanoide"],
        "habilidades_especiais": [],
        "maturidade_anos": 15,
        "expectativa_vida_anos": 90,
        "exemplos_nomes": ["Variados conforme etnia e região do Mar Interior (ver Capítulo 8, p. 430)"],
        "biografias_tipicas": ["Todas (ancestralidade altamente versátil)"],
        "classes_tipicas": ["Todas"],
        "descricao": "Ambiciosos, adaptáveis e diversos, humanos formam a ancestralidade mais populosa do Mar Interior.",
        "herancas": [
            construir_heranca(
                "Herança Perita",
                "Você se torna treinado em uma perícia à sua escolha. No 5º nível, você se torna especialista na perícia escolhida.",
            ),
            construir_heranca(
                "Herança Versátil",
                "Selecione um talento geral para o qual você atenda aos pré-requisitos (pode ser escolhido em qualquer momento da criação de personagem).",
            ),
            construir_heranca(
                "Meio-Elfo",
                "Você recebe o traço elfo e visão na penumbra. Pode selecionar talentos de ancestralidade de elfo, humano e meio-elfo.",
                sentidos_concedidos=["Visão na Penumbra"],
                tracos_adicionais=["Elfo"],
            ),
            construir_heranca(
                "Meio-Orc",
                "Você recebe o traço orc e visão na penumbra. Pode selecionar talentos de ancestralidade de humano, meio-orc e orc.",
                sentidos_concedidos=["Visão na Penumbra"],
                tracos_adicionais=["Orc"],
            ),
        ],
        "talentos_ancestralidade": [
            construir_talento_ancestralidade("Ambição Natural", 1, ["Humano"], "Você recebe um talento de classe de 1º nível para sua classe, atendendo aos pré-requisitos normalmente (pode escolher ao fim da criação)."),
            construir_talento_ancestralidade("Armamento Não Convencional", 1, ["Humano"], "Escolha uma arma incomum simples ou marcial com traço de ancestralidade ou cultura; obtém acesso e a considera simples (ou arma avançada incomum considerada marcial se já treinado em todas as armas marciais)."),
            construir_talento_ancestralidade("Natureza Cooperativa", 1, ["Humano"], "Você recebe +4 de bônus de circunstância em testes para Auxiliar."),
            construir_talento_ancestralidade("Obstinação Altiva", 1, ["Humano"], "Sucessos contra efeitos que tentem controlar diretamente suas ações viram sucesso crítico. Falhas em testes de Intimidação para Coagi-lo viram falha crítica."),
            construir_talento_ancestralidade("Perícia Natural", 1, ["Humano"], "Você recebe a graduação de proficiência treinado em duas perícias à sua escolha."),
            construir_talento_ancestralidade("Treinamento Geral", 1, ["Humano"], "Recebe um talento geral de 1º nível, atendendo aos pré-requisitos.", especial="Pode selecionar este talento várias vezes, escolhendo um talento diferente a cada vez."),
            construir_talento_ancestralidade("Truque Mágico Adaptado", 1, ["Humano"], "Escolha um truque mágico de uma tradição diferente da sua para substituir um dos seus truques mágicos e conjurá-lo como magia da tradição da sua classe.", pre_requisitos="característica de classe de conjuração"),
            construir_talento_ancestralidade("Discípulo Adaptativo", 5, ["Humano"], "Escolha um truque mágico ou magia de 1º nível da mesma tradição do Truque Mágico Adaptado e adicione-o à sua lista como magia da sua tradição.", pre_requisitos="Truque Mágico Adaptado, capacidade de conjurar magias de 3º nível"),
            construir_talento_ancestralidade("Improvisador Astuto", 5, ["Humano"], "Recebe o talento geral Improvisação Destreinada e pode tentar ações de perícia que exigem treinamento mesmo sendo destreinado."),
            construir_talento_ancestralidade("Alma Cooperativa", 9, ["Humano"], "Se for pelo menos especialista na perícia ao Auxiliar, obtém sucesso em qualquer resultado rolado para Auxiliar (que não tenha sido sucesso crítico).", pre_requisitos="Natureza Cooperativa"),
            construir_talento_ancestralidade("Improvisação Incrível", 9, ["Humano"], "Recebe +4 de bônus de circunstância no teste de perícia acionador em que é destreinado.", acoes="reacao", pre_requisitos="Improvisador Astuto", frequencia="uma vez por dia", acionamento="Você realiza um teste utilizando uma perícia em que é destreinado."),
            construir_talento_ancestralidade("Talentos Múltiplos", 9, ["Humano"], "Recebe um talento de dedicação de multiclasse de 2º nível mesmo sem completar restrições de arquétipo atual. Meio-elfos ignoram pré-requisitos de valor de atributo."),
            construir_talento_ancestralidade("Especialidade Não Convencional", 13, ["Humano"], "Sempre que receber proficiência de especialista ou maior em armas pela classe, ganha essa proficiência na arma escolhida por Armamento Não Convencional.", pre_requisitos="Armamento Não Convencional"),
        ],
    }

    return [anao, elfo, gnomo, goblin, halfling, humano]


def obter_herancas_mesticas_talentos() -> dict[str, Any]:
    """Retorna os talentos exclusivos de Meio-Elfo (3) e Meio-Orc/Orc (10) das páginas 58-59."""
    return {
        "observacao": (
            "Por padrão meio-elfos e meio-orcs são heranças humanas, mas a critério do MJ podem "
            "ser escolhidas em outras ancestralidades (gnomos/halflings para meio-elfos; "
            "anões/goblins/halflings para meio-orcs)."
        ),
        "meio_elfo": [
            construir_talento_ancestralidade("Atavismo Élfico", 1, ["Meio-Elfo"], "Recebe os benefícios de uma herança de elfo compatível com suas características.", especial="Selecionável apenas no 1º nível; não pode ser retreinado."),
            construir_talento_ancestralidade("Charme Sobrenatural", 5, ["Meio-Elfo"], "Pode conjurar cativar como magia arcana inata de 1º nível uma vez por dia."),
            construir_talento_ancestralidade("Inspirar Imitação", 5, ["Meio-Elfo"], "Sempre que obtiver sucesso em um teste de perícia, qualifica-se automaticamente para usar a reação Auxiliar nessa perícia sem gastar ação de Preparar."),
        ],
        "meio_orc": [
            construir_talento_ancestralidade("Familiaridade com Armas Órquicas", 1, ["Orc"], "Treinado em bracamante e machado longo. Obtém acesso a armas órquicas incomuns; trata marciais como simples e avançadas como marciais."),
            construir_talento_ancestralidade("Ferocidade Órquica", 1, ["Orc"], "Evita ser nocauteado ao cair a 0 PV, permanecendo com 1 PV e aumentando sua condição ferido em 1.", acoes="reacao", frequencia="uma vez por dia", acionamento="Você seria reduzido a 0 Pontos de Vida, mas não morto imediatamente."),
            construir_talento_ancestralidade("Pacificador Monstruoso", 1, ["Meio-Orc"], "Recebe +1 de bônus de circunstância em Diplomacia e Percepção (Sentir Motivação) contra não-humanoides inteligentes e humanoides marginalizados."),
            construir_talento_ancestralidade("Superstição Órquica", 1, ["Concentração", "Orc"], "Recebe +1 de bônus de circunstância na jogada de salvamento acionadora contra magia ou efeito mágico.", acoes="reacao", acionamento="Você tenta uma jogada de salvamento contra uma magia ou efeito mágico, antes de efetuar a rolagem."),
            construir_talento_ancestralidade("Visão Órquica", 1, ["Meio-Orc"], "Você adquire visão no escuro.", pre_requisitos="visão na penumbra", especial="Selecionável apenas no 1º nível; não pode ser retreinado."),
            construir_talento_ancestralidade("Carnificina com Armas Órquicas", 5, ["Orc"], "Aplica o efeito de especialização de crítico em acertos críticos usando bracamante, machado grande (machado longo) ou arma órquica.", pre_requisitos="Familiaridade com Armas Órquicas"),
            construir_talento_ancestralidade("Vigor Vitorioso", 5, ["Orc"], "Recebe Pontos de Vida temporários igual ao seu modificador de Constituição até o final do próximo turno.", acoes="reacao", acionamento="Você reduz um adversário a 0 Pontos de Vida."),
            construir_talento_ancestralidade("Superstição Pervasiva", 9, ["Orc"], "Recebe +1 de bônus de circunstância em jogadas de salvamento contra magias e efeitos mágicos o tempo inteiro.", pre_requisitos="Superstição Órquica"),
            construir_talento_ancestralidade("Especialidade com Armas Órquicas", 13, ["Orc"], "Recebe proficiência de especialista ou maior da classe também em bracamante, machado longo e armas órquicas treinadas.", pre_requisitos="Familiaridade com Armas Órquicas"),
            construir_talento_ancestralidade("Ferocidade Incrível", 13, ["Orc"], "Pode usar Ferocidade Órquica uma vez por hora em vez de uma vez por dia.", pre_requisitos="Ferocidade Órquica"),
        ],
    }


def obter_biografias() -> dict[str, Any]:
    """Retorna as regras e todas as 35 biografias (pp. 60-64)."""
    lista = [
        construir_biografia("Acólito", ["Inteligência", "Sabedoria"], ["Religião"], "Saber de Escrita", "Estudante do Cânone", "Você passou boa parte de sua vida em um convento ou monastério religioso."),
        construir_biografia("Acrobata", ["Força", "Destreza"], ["Acrobatismo"], "Saber de Circo", "Equilíbrio Estável", "Em um circo ou nas ruas, você ganhou dinheiro se apresentando como um acrobata."),
        construir_biografia("Advogado", ["Inteligência", "Carisma"], ["Diplomacia"], "Saber de Leis", "Impressionar Grupo", "Pilhas de manuais sobre leis, professores severos e experiências na corte o instruíram em assuntos legais."),
        construir_biografia("Animador", ["Destreza", "Carisma"], ["Performance"], "Saber de Teatro", "Performance Fascinante", "Através da educação nas artes ou pura prática obstinada, você aprendeu a entreter multidões."),
        construir_biografia("Apostador", ["Destreza", "Carisma"], ["Dissimulação"], "Saber de Jogos", "Mente na Minha Cara", "A emoção da vitória o levou aos jogos de azar."),
        construir_biografia("Artesão", ["Força", "Inteligência"], ["Manufatura"], "Saber de Guildas", "Especialidade de Manufatura", "Como um aprendiz, você praticou uma forma específica de construção, manufatura ou ofício."),
        construir_biografia("Artista", ["Destreza", "Carisma"], ["Manufatura"], "Saber de Artes", "Especialidade de Manufatura", "Sua arte é sua maior paixão, independentemente da forma que ela assume."),
        construir_biografia("Batedor", ["Destreza", "Sabedoria"], ["Sobrevivência"], "Saber de Terreno (ex.: Cavernas ou Florestas)", "Forrageador", "Você chama os ermos de lar, vivendo entre trilhas e guiando viajantes.", saber_tematico=True),
        construir_biografia("Caçador", ["Destreza", "Sabedoria"], ["Sobrevivência"], "Saber de Curtume", "Procurar Vida Selvagem", "Você perseguiu e abateu animais e outras criaturas dos ermos."),
        construir_biografia("Caçador de Recompensas", ["Força", "Sabedoria"], ["Sobrevivência"], "Saber de Leis", "Rastreador Experiente", "Você enche seus bolsos capturando infratores da lei."),
        construir_biografia("Charlatão", ["Inteligência", "Carisma"], ["Dissimulação"], "Saber de Submundo", "Mentiroso Charmoso", "Você viajava de lugar em lugar aplicando golpes e assumindo identidades falsas."),
        construir_biografia("Criança de Rua", ["Destreza", "Constituição"], ["Ladroagem"], "Saber de Cidade (ex.: Absalom ou Magnimar)", "Punga", "Você sobreviveu batendo carteiras nas ruas de uma cidade grande.", saber_tematico=True),
        construir_biografia("Criminoso", ["Destreza", "Inteligência"], ["Furtividade"], "Saber de Submundo", "Contrabandista Experiente", "Como um inescrupuloso independente ou membro do submundo, você viveu uma vida de crimes."),
        construir_biografia("Detetive", ["Inteligência", "Sabedoria"], ["Sociedade"], "Saber de Submundo", "Manha das Ruas", "Você solucionou crimes como inspetor de polícia ou investigador privado."),
        construir_biografia("Discípulo Marcial", ["Força", "Destreza"], ["Acrobatismo", "Atletismo"], "Saber de Guerra", "Queda do Gato ou Salto Rápido", "Você passou por um treinamento intenso e estudo rigoroso para se tornar um grande combatente.", talento_pericia_condicional={"Acrobatismo": "Queda do Gato", "Atletismo": "Salto Rápido"}),
        construir_biografia("Emissário", ["Inteligência", "Carisma"], ["Sociedade"], "Saber de Cidade visitada com frequência", "Poliglota", "Como diplomata ou mensageiro, você viajou para várias terras distantes.", saber_tematico=True),
        construir_biografia("Encantador de Animais", ["Sabedoria", "Carisma"], ["Natureza"], "Saber de Terreno habitado por animais (ex.: Planícies ou Pântanos)", "Treinar Animal", "Você sempre sentiu uma forte ligação com os animais e aprendeu a treiná-los.", saber_tematico=True),
        construir_biografia("Eremita", ["Constituição", "Inteligência"], ["Natureza", "Ocultismo"], "Saber de Terreno onde vivia (ex.: Cavernas ou Desertos)", "Conhecimento Duvidoso", "Você viveu solitariamente em um local isolado.", saber_tematico=True),
        construir_biografia("Estudioso", ["Inteligência", "Sabedoria"], ["Arcanismo", "Natureza", "Ocultismo", "Religião"], "Saber Acadêmico", "Certeza (na perícia escolhida)", "Você tem facilidade de aprendizado e se isolou para estudar livros e saberes antigos.", talento_pericia_condicional={"Arcanismo": "Certeza (Arcanismo)", "Natureza": "Certeza (Natureza)", "Ocultismo": "Certeza (Ocultismo)", "Religião": "Certeza (Religião)"}),
        construir_biografia("Funileiro", ["Destreza", "Inteligência"], ["Manufatura"], "Saber de Engenharia", "Especialidade de Manufatura", "Você satisfaz sua necessidade de resolver problemas criando invenções menores."),
        construir_biografia("Gladiador", ["Força", "Carisma"], ["Performance"], "Saber de Gladiadores", "Performance Impressionante", "Os sanguinários jogos de arena lhe ensinaram a arte do combate."),
        construir_biografia("Guarda", ["Força", "Carisma"], ["Intimidação"], "Saber de Guerra", "Coerção Rápida", "Você serviu em uma guarda e sabe fazer um suspeito falar."),
        construir_biografia("Herbalista", ["Constituição", "Sabedoria"], ["Natureza"], "Saber de Herbalismo", "Medicina Natural", "Você aprendeu as propriedades curativas de várias ervas e como prepará-las."),
        construir_biografia("Lavrador", ["Constituição", "Sabedoria"], ["Atletismo"], "Saber de Agricultura", "Certeza para Atletismo", "Você lavrou a terra e cuidou da colheita com costas fortes e compreensão dos ciclos sazonais."),
        construir_biografia("Marinheiro", ["Força", "Destreza"], ["Atletismo"], "Saber de Navegação", "Saqueador Subaquático", "Você ouve o chamado do mar desde jovem, em embarcações mercantes, marinha ou pirataria."),
        construir_biografia("Médico de Campo", ["Constituição", "Sabedoria"], ["Medicina"], "Saber de Guerra", "Medicina de Batalha", "No caos da batalha, você tratou soldados e aprendeu sobre as logísticas da guerra."),
        construir_biografia("Mercador", ["Inteligência", "Carisma"], ["Diplomacia"], "Saber de Mercadores", "Pechinchador", "Você permutou mercadorias por dinheiro e outros bens em lojas, mercados ou caravanas."),
        construir_biografia("Mineiro", ["Força", "Sabedoria"], ["Sobrevivência"], "Saber de Mineração", "Especialidade em Terreno (subterrâneo)", "Você passou a vida arrancando minerais preciosos das profundezas escuras da terra."),
        construir_biografia("Nobre", ["Inteligência", "Carisma"], ["Sociedade"], "Saber de Genealogia ou Saber de Heráldica", "Gracejos da Corte", "Você cresceu como nobre ou aspirante à pequena nobreza entre obrigações e intrigas."),
        construir_biografia("Nômade", ["Constituição", "Sabedoria"], ["Sobrevivência"], "Saber de Terreno viajado (ex.: Desertos ou Pântanos)", "Certeza para Sobrevivência", "Viajando por toda parte, você aprendeu a sobreviver na estrada e em terras desconhecidas.", saber_tematico=True),
        construir_biografia("Operário", ["Força", "Constituição"], ["Atletismo"], "Saber de Trabalho", "Carregador Robusto", "Você passou anos realizando trabalho físico árduo."),
        construir_biografia("Prisioneiro", ["Força", "Constituição"], ["Furtividade"], "Saber de Submundo", "Contrabandista Experiente", "Você foi aprisionado ou escravizado em algum momento e agora aproveita sua liberdade."),
        construir_biografia("Soldado", ["Força", "Constituição"], ["Intimidação"], "Saber de Guerra", "Olhar Intimidante", "Em sua juventude, você entrou em batalha como mercenário, miliciano ou soldado."),
        construir_biografia("Taverneiro", ["Constituição", "Carisma"], ["Diplomacia"], "Saber de Álcool", "Camarada", "Você trabalhou em um bar, aprendendo a não derramar bebida e socializar no barulho."),
        construir_biografia("Vidente", ["Inteligência", "Carisma"], ["Ocultismo"], "Saber de Vidência", "Identificar Estranhezas", "Você aprendeu formas tradicionais de adivinhação que o conectaram aos mistérios ocultistas."),
    ]
    return {
        "regras": {
            "escolha_nivel_1": "Permanente; escolhida no 1º nível.",
            "beneficios_padrao": [
                "Duas melhorias de atributo (1 dentre dois atributos especificados e 1 melhoria livre).",
                "Graduação treinado em uma perícia específica (se já treinado depois pela classe, escolha outra).",
                "Graduação treinado em uma perícia de Saber específica.",
                "Um talento de perícia específico.",
            ],
        },
        "lista": lista,
    }


def obter_idiomas() -> dict[str, Any]:
    """Retorna as regras de idiomas e as Tabelas 2-1, 2-2 e 2-3 (p. 65)."""
    return {
        "regras": {
            "adicionais_por_inteligencia": "Modificador de Inteligência positivo concede igual quantidade de idiomas adicionais da lista da ancestralidade ou região.",
            "druídico": "Idioma secreto disponível apenas para druidas, que são proibidos de ensiná-lo a não-druidas.",
            "lingua_sinais_leitura_labial": "Disponíveis pelos talentos de perícia Língua de Sinais e Ler Lábios (ou gratuitamente pelo MJ por conceito de personagem).",
        },
        "tabela_2_1_idiomas_comuns": [
            {"idioma": "Comum", "falantes": "Humanos, anões, elfos, halflings e outras ancestralidades comuns"},
            {"idioma": "Dracônico", "falantes": "Dragões, humanoides reptilianos"},
            {"idioma": "Enânico", "falantes": "Anões"},
            {"idioma": "Élfico", "falantes": "Elfos, meio-elfos"},
            {"idioma": "Gnômico", "falantes": "Gnomos"},
            {"idioma": "Goblin", "falantes": "Bugbears, goblins, hobgoblins"},
            {"idioma": "Halfling", "falantes": "Halflings"},
            {"idioma": "Jotun", "falantes": "Gigantes, ogros, trolls, ettins, ciclopes"},
            {"idioma": "Órquico", "falantes": "Orcs, meio-orcs"},
            {"idioma": "Silvestre", "falantes": "Fadas, centauros, plantas"},
            {"idioma": "Subterrâneo", "falantes": "Drow, duergares, xulgathes"},
        ],
        "tabela_2_2_idiomas_incomuns": [
            {"idioma": "Abissal", "falantes": "Demônios"},
            {"idioma": "Aklo", "falantes": "Deros, fadas malignas, monstros de outros mundos"},
            {"idioma": "Aquan", "falantes": "Criaturas aquáticas, elementais de água"},
            {"idioma": "Auran", "falantes": "Criaturas voadoras, elementais do ar"},
            {"idioma": "Celestial", "falantes": "Anjos"},
            {"idioma": "Gnoll", "falantes": "Gnolls"},
            {"idioma": "Ignan", "falantes": "Elementais do fogo"},
            {"idioma": "Infernal", "falantes": "Diabos"},
            {"idioma": "Língua-das-Sombras", "falantes": "Nidaleses, criaturas do Plano das Sombras"},
            {"idioma": "Necril", "falantes": "Carniçais, mortos-vivos inteligentes"},
            {"idioma": "Terran", "falantes": "Elementais da terra"},
        ],
        "tabela_2_3_idioma_secreto": [
            {"idioma": "Druídico", "falantes": "Druidas"}
        ],
    }


def gerar_estrutura_completa() -> dict[str, Any]:
    """Monta a estrutura completa de criação, ancestralidades, heranças, biografias e idiomas."""
    return {
        "fonte": {
            "arquivo": "ref/Anc Race.pdf",
            "titulo": "Capítulos 1 e 2: Criação de Personagem, Ancestralidades & Biografias",
            "paginas": "19-65",
            "sistema": "Pathfinder 2ª Edição (Livro Básico)",
        },
        "regras_criacao_personagem": obter_regras_criacao_personagem(),
        "ancestralidades": obter_ancestralidades(),
        "herancas_mesticas_talentos": obter_herancas_mesticas_talentos(),
        "biografias": obter_biografias(),
        "idiomas": obter_idiomas(),
    }


def validar_dados(dados: dict[str, Any]) -> None:
    """Valida todas as contagens, unicidade de IDs e integridade contra ref/Anc Race.pdf."""
    regras = dados["regras_criacao_personagem"]
    assert len(regras["atributos"]) == 6
    assert len(regras["resumo_classes_atributos"]) == 12
    assert len(regras["passos_criacao"]) == 10
    assert len(regras["graus_proficiencia"]) == 5
    assert len(regras["tabela_1_2_tendencias"]) == 9

    ancs = dados["ancestralidades"]
    assert len(ancs) == 6
    total_herancas = sum(len(a["herancas"]) for a in ancs)
    total_talentos_principais = sum(len(a["talentos_ancestralidade"]) for a in ancs)
    assert total_herancas == 29, f"Esperado 29 heranças, encontrado {total_herancas}"
    assert total_talentos_principais == 78, f"Esperado 78 talentos principais, encontrado {total_talentos_principais}"

    mesticagem = dados["herancas_mesticas_talentos"]
    assert len(mesticagem["meio_elfo"]) == 3
    assert len(mesticagem["meio_orc"]) == 10

    bios = dados["biografias"]["lista"]
    assert len(bios) == 35, f"Esperado 35 biografias, encontrado {len(bios)}"
    bio_ids = [b["id"] for b in bios]
    assert len(bio_ids) == len(set(bio_ids))

    idiomas = dados["idiomas"]
    assert len(idiomas["tabela_2_1_idiomas_comuns"]) == 11
    assert len(idiomas["tabela_2_2_idiomas_incomuns"]) == 11
    assert len(idiomas["tabela_2_3_idioma_secreto"]) == 1

    # Unicidade de IDs em ancestralidades, heranças e talentos + padronização de ações
    assert len({a["id"] for a in ancs}) == 6
    acoes_validas = {None, "1", "2", "3", "livre", "reacao"}
    for anc in ancs:
        h_ids = [h["id"] for h in anc["herancas"]]
        t_ids = [t["id"] for t in anc["talentos_ancestralidade"]]
        assert len(h_ids) == len(set(h_ids)), f"Heranças duplicadas em {anc['nome']}"
        assert len(t_ids) == len(set(t_ids)), f"Talentos duplicados em {anc['nome']}"
        for h in anc["herancas"]:
            if h.get("habilidade_acao"):
                assert h["habilidade_acao"].get("acoes") in acoes_validas
        for t in anc["talentos_ancestralidade"]:
            assert t.get("acoes") in acoes_validas, f"Ação não padronizada em {t['id']}: {t.get('acoes')}"
    for grp in ("meio_elfo", "meio_orc"):
        for t in mesticagem[grp]:
            assert t.get("acoes") in acoes_validas, f"Ação não padronizada em {t['id']}: {t.get('acoes')}"


def main() -> None:
    """Gera dados/ancestralidades_biografias.json, recarrega do disco e valida."""
    dados = gerar_estrutura_completa()
    validar_dados(dados)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    carregado = json.loads(CAMINHO_SAIDA.read_text(encoding="utf-8"))
    validar_dados(carregado)
    total_herancas = sum(len(a["herancas"]) for a in carregado["ancestralidades"])
    total_talentos = (
        sum(len(a["talentos_ancestralidade"]) for a in carregado["ancestralidades"])
        + len(carregado["herancas_mesticas_talentos"]["meio_elfo"])
        + len(carregado["herancas_mesticas_talentos"]["meio_orc"])
    )
    print(f"Arquivo gerado e validado com sucesso: {CAMINHO_SAIDA}")
    print(
        f"Resumo: {len(carregado['ancestralidades'])} ancestralidades, "
        f"{total_herancas} heranças, "
        f"{total_talentos} talentos de ancestralidade (78 principais + 13 mestiços), "
        f"{len(carregado['biografias']['lista'])} biografias, "
        f"{len(carregado['idiomas']['tabela_2_1_idiomas_comuns']) + len(carregado['idiomas']['tabela_2_2_idiomas_incomuns']) + len(carregado['idiomas']['tabela_2_3_idioma_secreto'])} idiomas."
    )


if __name__ == "__main__":
    main()
