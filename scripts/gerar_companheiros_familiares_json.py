from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "companheiros_familiares.json"


def slugify(texto: str) -> str:
    normalizado = unicodedata.normalize("NFD", texto)
    sem_acentos = "".join(ch for ch in normalizado if unicodedata.category(ch) != "Mn")
    slug = []
    anterior_sep = False
    for ch in sem_acentos.lower():
        if ch.isalnum():
            slug.append(ch)
            anterior_sep = False
        elif not anterior_sep:
            slug.append("_")
            anterior_sep = True
    return "".join(slug).strip("_")


def construir_acao_companheiro(
    nome: str,
    acoes: str,
    tracos: list[str],
    descricao: str,
    *,
    requerimentos: str | None = None,
) -> dict[str, Any]:
    return {
        "id": slugify(nome),
        "nome": nome,
        "acoes": acoes,
        "tracos": tracos,
        "requerimentos": requerimentos,
        "descricao": descricao,
    }


def montar_dados_companheiros_familiares() -> dict[str, Any]:
    estagios_evolucao = [
        {
            "id": "jovem",
            "nome": "Companheiro Animal Jovem",
            "descricao": "O primeiro companheiro animal obtido pela maioria dos personagens. Utiliza seu nível de personagem para determinar os bônus de proficiência dele. Os únicos bônus de item que companheiros animais podem receber são em Velocidade e CA (bônus máximo de item na CA = +3).",
            "proficiencias": {
                "ataques_desarmados": "treinado",
                "defesa_sem_armadura": "treinado",
                "armadura_de_animal": "treinado",
                "salvamentos": "treinado",
                "percepcao": "treinado",
                "pericias": ["Acrobatismo", "Atletismo"],
                "observacao": "Um companheiro animal não pode usar habilidades que exijam muita Inteligência, como Coagir ou Decifrar Escrita, mesmo se for treinado na perícia apropriada (a menos que possua uma especialização que o permita fazer isso).",
            },
            "modificadores_atributo_base": {
                "forca": 2,
                "destreza": 2,
                "constituicao": 1,
                "inteligencia": -4,
                "sabedoria": 1,
                "carisma": 0,
            },
            "nota_modificadores": "Cada tipo de companheiro incrementa dois destes modificadores base em +1 ponto cada (já calculados nos blocos de estatísticas dos tipos).",
            "formula_pv": "PV de ancestralidade do tipo + ((6 + modificador de Constituição) * nível do personagem)",
        },
        {
            "id": "maduro",
            "nome": "Companheiro Animal Maduro",
            "descricao": "Quando um companheiro animal jovem evolui para um companheiro animal maduro (usualmente resultado da escolha de um de seus talentos de classe):",
            "ajustes": {
                "atributos": {"forca": 1, "destreza": 1, "constituicao": 1, "sabedoria": 1},
                "dados_dano_desarmado": "aumenta de 1 para 2 dados (por exemplo, de 1d8 para 2d8)",
                "percepcao": "especialista",
                "salvamentos": "especialista",
                "pericias_treinadas_ou_especialista": ["Furtividade", "Intimidação", "Sobrevivência"],
                "tamanho": "Se seu companheiro for Médio ou menor, ele cresce um tamanho.",
            },
        },
        {
            "id": "agil",
            "nome": "Companheiro Animal Ágil",
            "pre_requisito_estagio": "maduro",
            "descricao": "Para evoluir um companheiro animal maduro para um companheiro animal ágil:",
            "ajustes": {
                "atributos": {"destreza": 2, "forca": 1, "constituicao": 1, "sabedoria": 1},
                "dano_adicional_desarmado": 2,
                "acrobatismo": "especialista",
                "defesa_sem_armadura": "especialista",
                "manobra_avancada": True,
                "ataques_magicos": True,
            },
        },
        {
            "id": "selvagem",
            "nome": "Companheiro Animal Selvagem",
            "pre_requisito_estagio": "maduro",
            "descricao": "Para evoluir um companheiro animal maduro para um companheiro animal selvagem:",
            "ajustes": {
                "atributos": {"forca": 2, "destreza": 1, "constituicao": 1, "sabedoria": 1},
                "dano_adicional_desarmado": 3,
                "atletismo": "especialista",
                "manobra_avancada": True,
                "tamanho": "Se seu companheiro for Médio ou menor, ele cresce um tamanho.",
                "ataques_magicos": True,
            },
        },
    ]

    tipos_companheiro = [
        {
            "id": "cavalo",
            "nome": "Cavalo",
            "descricao": "Seu companheiro é um cavalo, pônei ou equino similar.",
            "tamanho": "Médio ou Grande",
            "ataques": [
                {
                    "nome": "casco",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d6 contundente",
                    "tracos": ["ágil"],
                }
            ],
            "modificadores_atributo": {
                "forca": 3,
                "destreza": 2,
                "constituicao": 2,
                "inteligencia": -4,
                "sabedoria": 1,
                "carisma": 0,
            },
            "pontos_de_vida_ancestralidade": 8,
            "pericia": "Sobrevivência",
            "sentidos": "faro (impreciso, 9 metros), visão na penumbra",
            "velocidades": {"terra": 12.0},
            "velocidades_texto": "12 metros",
            "especial": "montaria",
            "beneficio_de_suporte": "Seu cavalo adiciona impulso à sua investida. Até o início de seu próximo turno, se você tiver se movido pelo menos 3 metros na ação anterior a seu ataque, adicione um bônus de circunstância ao dano desse ataque igual ao dobro da quantidade de dados de dano. Se sua arma possuir o traço de justa, aumente o bônus de dano do traço em 2 pontos por dado.",
            "manobra_avancada": construir_acao_companheiro(
                "Galopar",
                "2",
                ["Movimento"],
                "O cavalo Anda duas vezes com +3 metros de bônus de circunstância em sua Velocidade.",
            ),
        },
        {
            "id": "dromaeossauro",
            "nome": "Dromaeossauro",
            "descricao": "Seu companheiro é um dromaeossauro (também chamado de raptor), como um velociraptor ou deinonico.",
            "tamanho": "Pequeno",
            "ataques": [
                {
                    "nome": "mandíbulas",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d8 perfurante",
                    "tracos": ["acuidade"],
                },
                {
                    "nome": "unha",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d6 cortante",
                    "tracos": ["acuidade", "ágil"],
                },
            ],
            "modificadores_atributo": {
                "forca": 2,
                "destreza": 3,
                "constituicao": 2,
                "inteligencia": -4,
                "sabedoria": 1,
                "carisma": 0,
            },
            "pontos_de_vida_ancestralidade": 6,
            "pericia": "Furtividade",
            "sentidos": "faro (impreciso, 9 metros), visão na penumbra",
            "velocidades": {"terra": 15.0},
            "velocidades_texto": "15 metros",
            "especial": None,
            "beneficio_de_suporte": "Seu raptor constantemente se move para uma posição de flanco. Até o início do seu próximo turno, ele conta como se estivesse no espaço dele ou em um espaço vazio à sua escolha a até 3 metros para determinar se você e seu companheiro estão flanqueando (você pode escolher um espaço diferente para cada um de seus ataques).",
            "manobra_avancada": construir_acao_companheiro(
                "Ataque Dardejante",
                "1",
                ["Floreio"],
                "O raptor Dá um Passo de até 3 metros e então Golpeia, ou Golpeia e então Dá um Passo de até 3 metros.",
            ),
        },
        {
            "id": "felino",
            "nome": "Felino",
            "descricao": "Seu companheiro é um grande felino, como um leopardo ou tigre.",
            "tamanho": "Pequeno",
            "ataques": [
                {
                    "nome": "mandíbulas",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d6 perfurante",
                    "tracos": ["acuidade"],
                },
                {
                    "nome": "garra",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d4 cortante",
                    "tracos": ["acuidade", "ágil"],
                },
            ],
            "modificadores_atributo": {
                "forca": 2,
                "destreza": 3,
                "constituicao": 1,
                "inteligencia": -4,
                "sabedoria": 2,
                "carisma": 0,
            },
            "pontos_de_vida_ancestralidade": 4,
            "pericia": "Furtividade",
            "sentidos": "faro (impreciso, 9 metros), visão na penumbra",
            "velocidades": {"terra": 10.5},
            "velocidades_texto": "10,5 metros",
            "especial": "Seu felino causa 1d4 de dano de precisão adicional contra alvos desprevenidos.",
            "beneficio_de_suporte": "Seu felino desequilibra seus inimigos quando você abre uma brecha. Até o início de seu próximo turno, seus Golpes que causarem dano a uma criatura ameaçada pelo seu felino deixam o alvo desprevenido até o final de seu próximo turno.",
            "manobra_avancada": construir_acao_companheiro(
                "Bote de Felino",
                "1",
                ["Floreio"],
                "O felino Anda e depois Golpeia. Se estiver indetectado no início de seu Bote de Felino, ele permanece indetectado até após o ataque.",
            ),
        },
        {
            "id": "lobo",
            "nome": "Lobo",
            "descricao": "Seu companheiro é um lobo ou outra criatura canina, como um cachorro.",
            "tamanho": "Pequeno",
            "ataques": [
                {
                    "nome": "mandíbulas",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d8 perfurante",
                    "tracos": ["acuidade"],
                }
            ],
            "modificadores_atributo": {
                "forca": 2,
                "destreza": 3,
                "constituicao": 2,
                "inteligencia": -4,
                "sabedoria": 1,
                "carisma": 0,
            },
            "pontos_de_vida_ancestralidade": 6,
            "pericia": "Sobrevivência",
            "sentidos": "faro (impreciso, 9 metros), visão na penumbra",
            "velocidades": {"terra": 12.0},
            "velocidades_texto": "12 metros",
            "especial": None,
            "beneficio_de_suporte": "Seu lobo rasga tendões em cada abertura. Até o início de seu próximo turno, seus Golpes que causarem dano a criaturas ameaçadas pelo seu lobo impõem –1,5 metros de penalidade de estado em suas Velocidades por 1 minuto (–3 metros em um sucesso crítico).",
            "manobra_avancada": construir_acao_companheiro(
                "Jogar no Chão",
                "1",
                [],
                "O lobo automaticamente deixa o alvo de seu Golpe com mandíbulas prostrado.",
                requerimentos="A última ação do companheiro animal foi um Golpe bem-sucedido com mandíbulas.",
            ),
        },
        {
            "id": "passaro",
            "nome": "Pássaro",
            "descricao": "Seu companheiro é uma ave de rapina, como uma águia, coruja ou gavião.",
            "tamanho": "Pequeno",
            "ataques": [
                {
                    "nome": "mandíbulas",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d6 perfurante",
                    "tracos": ["acuidade"],
                },
                {
                    "nome": "unha",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d4 perfurante",
                    "tracos": ["acuidade", "ágil"],
                },
            ],
            "modificadores_atributo": {
                "forca": 2,
                "destreza": 3,
                "constituicao": 1,
                "inteligencia": -4,
                "sabedoria": 2,
                "carisma": 0,
            },
            "pontos_de_vida_ancestralidade": 4,
            "pericia": "Furtividade",
            "sentidos": "visão na penumbra",
            "velocidades": {"terra": 3.0, "voo": 18.0},
            "velocidades_texto": "3 metros, voo 18 metros",
            "especial": None,
            "beneficio_de_suporte": "O pássaro bica os olhos de seus adversários quando você abre uma brecha. Até o início de seu próximo turno, seus Golpes que causarem dano a uma criatura ameaçada pelo seu pássaro também causam 1d4 de dano persistente de sangramento, e o alvo fica ofuscado até remover o dano de sangramento. Se seu pássaro for ágil ou selvagem, o dano persistente de sangramento aumenta para 2d4.",
            "manobra_avancada": construir_acao_companheiro(
                "Ataque Rasante",
                "2",
                [],
                "O pássaro Voa e faz um Golpe de unha a qualquer momento durante o deslocamento.",
            ),
        },
        {
            "id": "serpente",
            "nome": "Serpente",
            "descricao": "Seu companheiro é uma serpente constritora, como uma jiboia ou píton.",
            "tamanho": "Pequeno",
            "ataques": [
                {
                    "nome": "mandíbulas",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d8 perfurante",
                    "tracos": ["acuidade"],
                }
            ],
            "modificadores_atributo": {
                "forca": 3,
                "destreza": 3,
                "constituicao": 1,
                "inteligencia": -4,
                "sabedoria": 1,
                "carisma": 0,
            },
            "pontos_de_vida_ancestralidade": 6,
            "pericia": "Furtividade",
            "sentidos": "faro (impreciso, 9 metros), visão na penumbra",
            "velocidades": {"terra": 6.0, "escalada": 6.0, "natacao": 6.0},
            "velocidades_texto": "6 metros, escalada 6 metros, natação 6 metros",
            "especial": None,
            "beneficio_de_suporte": "Sua serpente se enrosca em seus inimigos e os prende, interferindo em suas reações. Até o início de seu próximo turno, qualquer criatura ameaçada por sua serpente não pode usar reações acionadas por suas ações a menos que possua um nível maior que o seu.",
            "manobra_avancada": construir_acao_companheiro(
                "Constringir",
                "1",
                [],
                "A serpente causa 12 de dano contundente à criatura agarrada; a criatura deve tentar um salvamento básico de Fortitude. Se a serpente for um companheiro animal especializado, aumente este dano para 20 pontos.",
                requerimentos="A serpente possui uma criatura menor do que ela agarrada.",
            ),
        },
        {
            "id": "texugo",
            "nome": "Texugo",
            "descricao": "Seu companheiro é um texugo, carcaju ou outro mustelídeo volumoso.",
            "tamanho": "Pequeno",
            "ataques": [
                {
                    "nome": "mandíbulas",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d8 perfurante",
                    "tracos": [],
                },
                {
                    "nome": "garra",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d6 cortante",
                    "tracos": ["ágil"],
                },
            ],
            "modificadores_atributo": {
                "forca": 2,
                "destreza": 2,
                "constituicao": 2,
                "inteligencia": -4,
                "sabedoria": 2,
                "carisma": 0,
            },
            "pontos_de_vida_ancestralidade": 8,
            "pericia": "Sobrevivência",
            "sentidos": "faro (impreciso, 9 metros), visão na penumbra",
            "velocidades": {"terra": 7.5, "escalada": 3.0, "escavacao": 3.0},
            "velocidades_texto": "7,5 metros, escalada 3 metros, escavação 3 metros",
            "especial": None,
            "beneficio_de_suporte": "Seu texugo escava ao redor da posição de seu adversário, interferindo no apoio e equilíbrio dele. Até o início de seu próximo turno, se você acertar e causar dano a uma criatura ameaçada pelo seu texugo, o alvo não pode usar uma ação de Dar um Passo (a menos que possa Dar um Passo em terreno difícil) até se mover de sua posição atual.",
            "manobra_avancada": construir_acao_companheiro(
                "Fúria de Texugo",
                "1",
                ["Concentração", "Emoção", "Mental"],
                "O texugo entra em um estado de pura fúria que dura por 1 minuto, até que não perceba nenhum inimigo ao redor dele ou até ficar inconsciente (o que ocorrer primeiro). Ele não pode encerrar sua fúria voluntariamente. Enquanto estiver em fúria, o texugo é afetado das seguintes maneiras:\n• Ele causa 4 pontos de dano adicionais com ataques de mordida e 2 pontos de dano adicionais com ataques de garra.\n• Ele sofre –1 de penalidade na CA.\n• Ele não pode usar ações com o traço concentração a menos que elas também possuam o traço fúria. O companheiro animal pode Buscar enquanto estiver em fúria.\nApós encerrar sua fúria, ele não pode usar Fúria de Texugo novamente por 1 minuto.",
                requerimentos="O texugo não está fatigado ou em fúria.",
            ),
        },
        {
            "id": "urso",
            "nome": "Urso",
            "descricao": "Seu companheiro é um urso negro, marrom, polar ou de outro tipo.",
            "tamanho": "Pequeno",
            "ataques": [
                {
                    "nome": "mandíbulas",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d8 perfurante",
                    "tracos": [],
                },
                {
                    "nome": "garra",
                    "tipo": "corpo_a_corpo",
                    "acoes": "1",
                    "dano": "1d6 cortante",
                    "tracos": ["ágil"],
                },
            ],
            "modificadores_atributo": {
                "forca": 3,
                "destreza": 2,
                "constituicao": 2,
                "inteligencia": -4,
                "sabedoria": 1,
                "carisma": 0,
            },
            "pontos_de_vida_ancestralidade": 8,
            "pericia": "Intimidação",
            "sentidos": "faro (impreciso, 9 metros), visão na penumbra",
            "velocidades": {"terra": 10.5},
            "velocidades_texto": "10,5 metros",
            "especial": None,
            "beneficio_de_suporte": "Seu urso rasga seus inimigos quando você abre uma brecha. Até o início de seu próximo turno, cada vez que você acertar uma criatura no alcance do urso com um Golpe, o urso causa 1d8 de dano cortante na criatura. Se seu urso for ágil ou selvagem, o dano cortante aumenta para 2d8.",
            "manobra_avancada": construir_acao_companheiro(
                "Abraço de Urso",
                "1",
                [],
                "O urso faz outro Golpe com garra contra o mesmo alvo. Se esse Golpe acertar, o alvo também fica agarrado (como se o urso tivesse obtido sucesso em Agarrá-lo).",
                requerimentos="A última ação do urso foi um Golpe bem-sucedido com garra.",
            ),
        },
    ]

    especializacoes = {
        "descricao": "Companheiros animais especializados são mais inteligentes e possuem comportamentos mais complexos. A maioria dos companheiros animais pode ter somente uma especialização.",
        "beneficios_gerais_primeira_vez": {
            "ataques_desarmados": "especialista",
            "salvamentos": "mestre",
            "percepcao": "mestre",
            "modificadores_atributo": {"destreza": 1, "inteligencia": 2},
            "dados_dano_desarmado": "aumenta de 2 para 3 dados",
            "dano_adicional_desarmado": "aumenta de 2 para 4 pontos de dano ou de 3 para 6 pontos de dano",
        },
        "opcoes": [
            {
                "id": "ameacador",
                "nome": "Ameaçador",
                "descricao": "Seu companheiro aterroriza adversários com demonstrações de dominância e os afasta de um lado para o outro do campo de batalha. As graduações de proficiência dele em Atletismo e Intimidação aumentam para especialista (ou mestre se já for especialista devido a seu tipo), o modificador de Força dele aumenta em 1 ponto, e o modificador de Carisma dele aumenta em 3 pontos.",
            },
            {
                "id": "audacioso",
                "nome": "Audacioso",
                "descricao": "Seu companheiro entra na peleja com saltos e mergulhos graciosos. Ele adquire a habilidade negar vantagem, portanto, não fica desprevenido para criaturas escondidas, indetectadas ou que estejam flanqueando-o a menos que o nível da criatura seja maior do que o seu. A graduação de proficiência dele em Acrobatismo aumenta para especialista, e o modificador de Destreza dele aumenta em 1 ponto. A graduação de proficiência dele em defesa sem armadura aumenta para especialista, ou para mestre se for ágil.",
            },
            {
                "id": "corredor",
                "nome": "Corredor",
                "descricao": "Seu companheiro tem grande capacidade para correr. Ele recebe +3 metros de bônus de estado em sua Velocidade, Velocidade de natação ou Velocidade de voo (à sua escolha). A graduação de proficiência dele em Fortitude aumenta para lendário e o modificador de Constituição dele aumenta em 1 ponto.",
            },
            {
                "id": "demolidor",
                "nome": "Demolidor",
                "descricao": "Seu companheiro destrói coisas. Os ataques desarmados dele ignoram metade da Dureza do objeto. A graduação de proficiência dele em Atletismo aumenta para mestre, e o modificador de Força dele aumenta em 1 ponto.",
            },
            {
                "id": "emboscador",
                "nome": "Emboscador",
                "descricao": "Em seu ambiente natural, seu companheiro pode usar a ação Esgueirar mesmo se estiver sendo presentemente observado. A graduação de proficiência dele em Furtividade aumenta para especialista (ou mestre se já for especialista devido a seu tipo) e o modificador de Destreza dele aumenta em 1 ponto. A graduação de proficiência dele em defesa sem armadura aumenta para especialista, ou para mestre se ele for ágil.",
            },
            {
                "id": "rastreador",
                "nome": "Rastreador",
                "descricao": "Seu companheiro é um rastreador incrível. Ele pode se mover em Velocidade total enquanto segue rastros. A graduação de proficiência dele em Sobrevivência aumenta para especialista (ou mestre se já for especialista devido a seu tipo), e o modificador de Sabedoria dele aumenta em 1 ponto.",
            },
        ],
    }

    habilidades_familiar = [
        {
            "id": "anfibio",
            "nome": "Anfíbio",
            "descricao": "Ele recebe Velocidade de natação de 7,5 metros (ou Velocidade de 7,5 metros se já possuir Velocidade de natação).",
        },
        {
            "id": "anulacao_de_dano",
            "nome": "Anulação de Dano",
            "descricao": "Escolha um tipo de salvamento. Ele não sofre dano quando obtiver sucesso nesse tipo de salvamento; isto não impede efeitos além de dano.",
        },
        {
            "id": "assistente_de_laboratorio",
            "nome": "Assistente de Laboratório",
            "descricao": "Ele pode usar sua ação Alquimia Rápida. Você deve possuir Alquimia Rápida, e seu familiar deve estar em seu espaço. Este efeito tem o mesmo custo e requerimentos como se você estivesse usando o talento. O familiar deve possuir a habilidade destreza manual para selecionar esta habilidade.",
        },
        {
            "id": "destreza_manual",
            "nome": "Destreza Manual",
            "descricao": "Ele pode usar até dois dos membros dele como se fossem mãos para usar ações de manuseio.",
        },
        {
            "id": "escalador",
            "nome": "Escalador",
            "descricao": "Ele recebe Velocidade de escalada de 7,5 metros.",
        },
        {
            "id": "escavador",
            "nome": "Escavador",
            "descricao": "Ele recebe Velocidade de escavação de 1,5 metros, permitindo-o cavar buracos Minúsculos.",
        },
        {
            "id": "fala",
            "nome": "Fala",
            "descricao": "Ele compreende e fala um idioma que você conhece.",
        },
        {
            "id": "falar_com_a_propria_especie",
            "nome": "Falar com a Própria Espécie",
            "descricao": "Ele pode compreender e falar com animais da mesma espécie. Para selecionar esta habilidade, seu familiar deve ser um animal e possuir a habilidade de fala e você deve ser pelo menos de 6º nível para selecionar esta habilidade.",
        },
        {
            "id": "faro",
            "nome": "Faro",
            "descricao": "Ele recebe faro (impreciso, 9 metros).",
        },
        {
            "id": "movimento_rapido",
            "nome": "Movimento Rápido",
            "descricao": "Aumente uma das Velocidades do familiar de 7,5 metros para 12 metros.",
        },
        {
            "id": "visao_no_escuro",
            "nome": "Visão no Escuro",
            "descricao": "Ele recebe visão no escuro.",
        },
        {
            "id": "voador",
            "nome": "Voador",
            "descricao": "Ele recebe Velocidade de voo de 7,5 metros.",
        },
    ]

    habilidades_mestre = [
        {
            "id": "bateria_de_magia",
            "nome": "Bateria de Magia",
            "descricao": "Você recebe um espaço de magia adicional pelo menos 3 níveis inferior ao seu maior nível de espaço de magia; você deve ser capaz de conjurar magias de 4º nível usando espaços de magia para selecionar esta habilidade.",
        },
        {
            "id": "conexao_de_truque_magico",
            "nome": "Conexão de Truque Mágico",
            "descricao": "Você pode preparar um truque mágico adicional ou, se tiver um repertório, designar um único truque mágico para acrescentar ao seu repertório toda vez que selecionar esta habilidade; esse truque pode ser retreinado, mas não pode ser trocado de outras formas. Você deve ser capaz de preparar truques mágicos ou acrescentá-los ao seu repertório para selecionar esta habilidade.",
        },
        {
            "id": "foco_de_familiar",
            "nome": "Foco de Familiar",
            "descricao": "Uma vez por dia, seu familiar pode usar 2 ações com o traço concentração para recuperar 1 Ponto de Foco seu, até o seu máximo usual. Você deve possuir um reservatório de foco para selecionar esta habilidade.",
        },
        {
            "id": "reagentes_extras",
            "nome": "Reagentes Extras",
            "descricao": "Seu familiar cria reagentes infundidos extras no corpo dele ou em seu interior. Você recebe um lote adicional de reagentes infundidos. Você deve possuir a habilidade reagentes infundidos para selecionar esta habilidade.",
        },
        {
            "id": "transmitir_magia",
            "nome": "Transmitir Magia",
            "descricao": "Se seu familiar estiver em seu espaço, você pode conjurar uma magia com distância de toque, transferir o poder dela para seu familiar e comandar o familiar para transmitir a magia. Se o fizer, o familiar usa as 2 ações dele nessa rodada para se mover até um alvo à sua escolha e tocar esse alvo. Se ele não alcançar o alvo para tocá-lo neste turno, a magia não surte efeito.",
        },
        {
            "id": "vinculo_vital",
            "nome": "Vínculo Vital",
            "descricao": "Se seu familiar seria reduzido a 0 PV por dano, você pode usar uma reação com o traço concentração para sofrer o dano no lugar dele. Se o fizer, você sofre todo o dano e seu familiar não sofre dano algum. Entretanto, efeitos especiais que aconteceriam ao sofrer esse dano (como veneno de serpente) ainda se aplicam ao seu familiar.",
        },
    ]

    return {
        "meta": {
            "titulo": "Capítulo 3: Companheiros Animais e Familiares — Pathfinder 2E Livro Básico",
            "arquivo_origem": "ref/Classes 03.pdf",
            "paginas_livro_basico": "214-218",
            "versao": "1.0.0",
            "observacoes": "Regras completas de Companheiros Animais (estágios Jovem, Maduro, Ágil e Selvagem, 8 tipos de companheiro, manobras avançadas e 6 especializações) e Familiares (estatísticas base, 12 habilidades de familiar e 6 habilidades de mestre).",
        },
        "companheiros_animais": {
            "paginas": "214-217",
            "descricao": "Um companheiro animal é um parceiro leal que segue suas ordens. Seu companheiro animal possui o traço lacaio e recebe 2 ações durante o seu turno se você comandá-lo através da ação Comandar um Animal; isto substitui os efeitos convencionais dessa ação e você não precisa realizar um teste de Natureza para isso. Se seu companheiro morrer, você pode gastar uma semana de recesso para substituí-lo sem custo. Você pode possuir somente um único companheiro animal em um determinado momento.",
            "cavalgando_companheiros_animais": "Você ou um aliado pode cavalgar seu companheiro animal desde que ele seja pelo menos um tamanho maior que seu cavaleiro. Se estiver carregando um cavaleiro, o companheiro animal pode usar somente sua Velocidade em terra e não pode se mover e Prestar Suporte a você no mesmo turno. Entretanto, se seu companheiro animal possuir a habilidade especial montaria, ele é especialmente adequado para cavalgar e ignora estas restrições.",
            "acao_base": construir_acao_companheiro(
                "Prestar Suporte",
                "1",
                [],
                "Seu companheiro animal presta suporte a você. Você recebe os benefícios listados na seção Benefício de Suporte do tipo de seu companheiro. Se o animal usar a ação Prestar Suporte, as únicas outras ações que ele pode usar neste turno são ações de movimento básicas para ficar em posição e aproveitar-se dos benefícios de Prestar Suporte; ele não poderá Prestar Suporte para você se já tiver usado qualquer outra ação neste turno.",
                requerimentos="A criatura é um companheiro animal.",
            ),
            "estagios_evolucao": estagios_evolucao,
            "tipos_de_companheiro": tipos_companheiro,
            "especializacoes": especializacoes,
        },
        "familiares": {
            "paginas": "217-218",
            "descricao": "Familiares são criaturas misticamente ligadas à sua magia. A maioria dos familiares foram animais comuns um dia, tornando-se algo além disso durante o ritual que os transformou em familiares. Você pode escolher um animal Minúsculo como seu familiar, tal como um corvo, gato, morcego ou serpente. Alguns familiares são de espécies diferentes, normalmente descritas na habilidade que concede o familiar (por exemplo, o familiar leshy de um druida é uma planta Minúscula em vez de um animal, formado a partir de um espírito da natureza). Familiares possuem o traço lacaio (página 633), portanto, durante um encontro recebem 2 ações em uma rodada em que você gastar uma ação para comandá-los. Se seu familiar morrer, você pode gastar uma semana de recesso para substituí-lo sem custo. Você pode ter somente um único familiar em um determinado momento.",
            "estatisticas_base": {
                "modificadores_e_ca": "Os modificadores de salvamento e CA de seu familiar são iguais aos seus antes de aplicar quaisquer bônus ou penalidades de circunstância ou de estado. Os modificadores de Percepção, Acrobatismo e Furtividade dele são iguais ao seu nível mais o modificador de seu atributo de conjuração (ou Carisma se você não tiver um, exceto se especificado o contrário). Se fizer uma rolagem de ataque ou outro teste de perícia, ele utiliza seu nível como modificador. Ele não possui ou utiliza seus próprios modificadores de atributo e nunca pode se beneficiar de bônus de itens.",
                "pontos_de_vida_por_nivel": 5,
                "pontos_de_vida_texto": "Seu familiar possui 5 Pontos de Vida para cada nível que você possuir.",
                "tamanho": "Minúsculo",
                "sentidos": "Seu familiar possui visão na penumbra e pode receber sentidos adicionais de habilidades de familiar. Ele pode comunicar-se empaticamente com você desde que estejam a no máximo 1,5 quilômetros de distância, compartilhando emoções. Ele normalmente não compreende ou fala idiomas, mas pode receber a capacidade de fala de uma habilidade de familiar.",
                "movimento": "Seu familiar possui uma Velocidade de 7,5 metros ou uma Velocidade de Natação de 7,5 metros (escolha uma ao obter o familiar). Ele pode receber outros tipos de movimento de habilidades de familiar.",
                "habilidades_diarias_base": 2,
                "habilidades_de_familiar_e_mestre_texto": "Todo dia, você canaliza sua magia em duas habilidades, que podem ser habilidades de familiar ou de mestre. Se seu familiar for um animal que naturalmente possui uma destas habilidades (por exemplo, uma coruja possui Velocidade de voo), você deve selecioná-la. Seu familiar não pode ser um animal que naturalmente tenha mais habilidades de familiar que o seu máximo de habilidades de familiar diárias.",
            },
            "habilidades_de_familiar": habilidades_familiar,
            "habilidades_de_mestre": habilidades_mestre,
        },
    }


def validar_companheiros_familiares_json(dados: dict[str, Any]) -> None:
    ca = dados["companheiros_animais"]
    assert len(ca["estagios_evolucao"]) == 4
    assert [e["id"] for e in ca["estagios_evolucao"]] == ["jovem", "maduro", "agil", "selvagem"]

    tipos = ca["tipos_de_companheiro"]
    assert len(tipos) == 8
    ids_tipos = [t["id"] for t in tipos]
    assert len(ids_tipos) == len(set(ids_tipos))
    for tipo in tipos:
        assert tipo["manobra_avancada"]["nome"]
        assert tipo["ataques"]

    specs = ca["especializacoes"]["opcoes"]
    assert len(specs) == 6
    assert len({s["id"] for s in specs}) == 6

    fam = dados["familiares"]
    assert len(fam["habilidades_de_familiar"]) == 12
    assert len({h["id"] for h in fam["habilidades_de_familiar"]}) == 12
    assert len(fam["habilidades_de_mestre"]) == 6
    assert len({h["id"] for h in fam["habilidades_de_mestre"]}) == 6


def main() -> None:
    dados = montar_dados_companheiros_familiares()
    validar_companheiros_familiares_json(dados)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_SAIDA.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")

    print(f"Arquivo gerado com sucesso: {CAMINHO_SAIDA}")
    print(f"Tipos de companheiro animal: {len(dados['companheiros_animais']['tipos_de_companheiro'])}")
    print(f"Especializações: {len(dados['companheiros_animais']['especializacoes']['opcoes'])}")
    print(f"Habilidades de familiar: {len(dados['familiares']['habilidades_de_familiar'])}")
    print(f"Habilidades de mestre: {len(dados['familiares']['habilidades_de_mestre'])}")


if __name__ == "__main__":
    main()
