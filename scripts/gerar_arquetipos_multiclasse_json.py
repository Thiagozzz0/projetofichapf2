from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "dadospf2" / "arquetipos_multiclasse.json"


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


def construir_talento_arquetipo(
    nome: str,
    nivel: int,
    tracos: list[str],
    descricao: str,
    *,
    acoes: str | None = None,
    pre_requisitos: str | None = None,
    especial: str | None = None,
) -> dict[str, Any]:
    return {
        "id": slugify(nome),
        "nome": nome,
        "nivel": nivel,
        "tracos": tracos,
        "acoes": acoes,
        "pre_requisitos": pre_requisitos,
        "especial": especial,
        "descricao": descricao,
    }


def construir_primeiros_arquetipos() -> list[dict[str, Any]]:
    alquimista = {
        "id": "alquimista",
        "nome": "Alquimista",
        "classe_relacionada_id": "alquimista",
        "pagina": 220,
        "conjurador": False,
        "resumo": "Você aprecia mexer com fórmulas e substâncias alquímicas em seu tempo livre, e seus estudos progrediram além da simples experimentação.",
        "personagens_multiclasse": {
            "descricao": "Os itens alquímicos gratuitos do arquétipo alquimista são extremamente úteis para personagens de qualquer classe. A seguir são apresentadas somente algumas das combinações possíveis.",
            "combinacoes": [
                "Bárbaros alquimistas podem misturar mutagênicos com sua fúria para efeitos realmente ferozes.",
                "Campeões alquimistas podem focar em itens alquímicos que melhoram defesas e curam os outros, permitindo que a sua reação de campeão e imposição de mãos durem mais.",
                "Guerreiros alquimistas podem utilizar a alquimia para criar opções adicionais em situações além de suas táticas convencionais.",
                "Ladinos alquimistas podem combinar os talentos de veneno de ladino com venenos gratuitos diários, enquanto bombas oferecem uma forma interessante de atacar furtivamente com vários tipos de dano de energia.",
                "Patrulheiros alquimistas focam em alquimia e arapucas, usando mais amplamente sua perícia Manufatura e fornecendo bombas para arapucas de bomba.",
                "Conjuradores alquimistas frequentemente usam itens alquímicos para aliviar a pressão sobre seu repertório ou magias preparadas. Por exemplo, um mago alquimista capaz de criar elixires de visão no escuro pode preparar outra magia em vez de visão no escuro.",
            ],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Alquimista",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Você coloca seu interesse alquímico em prática. Você se torna treinado em bombas alquímicas e Manufatura; se já for treinado em Manufatura, em vez disso você se torna treinado em outra perícia à sua escolha. Você se torna treinado na CD de classe de alquimista. Você recebe a característica de classe reagentes infundidos do alquimista, gerando uma quantidade de reagentes a cada dia igual ao seu nível. Você também recebe o talento Manufatura Alquímica e quatro fórmulas adicionais de 1º nível de itens alquímicos, assim como a habilidade de criar itens sem custo durante suas preparações diárias. Seu nível de alquimia avançada é apenas 1 e não aumenta sozinho.",
                pre_requisitos="Inteligência 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de alquimista.",
            ),
            construir_talento_arquetipo(
                "Alquimia Rápida",
                4,
                ["Arquétipo"],
                "Você ganha a ação Alquimia Rápida (página 72).",
                pre_requisitos="Dedicação de Alquimista",
            ),
            construir_talento_arquetipo(
                "Concocção Básica",
                4,
                ["Arquétipo"],
                "Você recebe um talento de alquimista de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Alquimista",
            ),
            construir_talento_arquetipo(
                "Alquimista Especialista",
                6,
                ["Arquétipo"],
                "Seu nível de alquimia avançada aumenta para 3. No 10º nível, ele aumenta para 5.",
                pre_requisitos="especialista em Manufatura, Dedicação de Alquimista",
            ),
            construir_talento_arquetipo(
                "Concocção Avançada",
                6,
                ["Arquétipo"],
                "Você recebe um talento de alquimista. Para o propósito de atender seus pré-requisitos, seu nível de alquimista é igual à metade de seu nível de personagem.",
                pre_requisitos="Concocção Básica",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de alquimista.",
            ),
            construir_talento_arquetipo(
                "Alquimista Mestre",
                12,
                ["Arquétipo"],
                "Seu nível de alquimia avançada aumenta para 7. Para cada quatro níveis que você possuir além do 12º, seu nível de alquimia avançada aumenta em 1.",
                pre_requisitos="mestre em Manufatura, Alquimia Especialista",
            ),
        ],
    }

    barbaro = {
        "id": "barbaro",
        "nome": "Bárbaro",
        "classe_relacionada_id": "barbaro",
        "pagina": 221,
        "conjurador": False,
        "resumo": "Você carrega uma fúria profunda em seu interior que irrompe ocasionalmente, concedendo-lhe parte do poder de um bárbaro além de suas outras habilidades.",
        "personagens_multiclasse": {
            "descricao": "O arquétipo de bárbaro é uma ótima escolha para personagens que enfatizam enormemente a Força e ataques corpo a corpo além do normal para a sua classe, desde que consigam lidar com a restrição de conjuração imposta pela Fúria. Ele é especialmente proveitoso para personagens que desejem causar mais dano.",
            "combinacoes": [],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Bárbaro",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Você se torna treinado em Atletismo; se já for treinado em Atletismo, em vez disso você se torna treinado em outra perícia à sua escolha. Você se torna treinado na CD de classe de bárbaro. Você pode usar a ação Fúria (página 84). Escolha um instinto como se fosse um bárbaro. Você possui esse instinto para todos os propósitos e é limitado pelo anátema dele, mas não recebe as outras habilidades concedidas por ele.",
                pre_requisitos="Força 14, Constituição 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de bárbaro.",
            ),
            construir_talento_arquetipo(
                "Furor Básico",
                4,
                ["Arquétipo"],
                "Você recebe um talento de bárbaro de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Bárbaro",
            ),
            construir_talento_arquetipo(
                "Resiliência de Bárbaro",
                4,
                ["Arquétipo"],
                "Você recebe 3 Pontos de Vida adicionais para cada talento de classe do arquétipo de bárbaro que possuir. Conforme continuar selecionando talentos de classe de arquétipo de bárbaro, você continuará a receber Pontos de Vida desta forma.",
                pre_requisitos="Dedicação de Bárbaro, sua classe concede no máximo uma quantidade de Pontos de Vida por nível igual a 10 + seu modificador de Constituição",
            ),
            construir_talento_arquetipo(
                "Furor Avançado",
                6,
                ["Arquétipo"],
                "Você recebe um talento de bárbaro. Para o propósito de atender seus pré-requisitos, seu nível de bárbaro é igual à metade de seu nível de personagem.",
                pre_requisitos="Furor Básico",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de bárbaro.",
            ),
            construir_talento_arquetipo(
                "Habilidade de Instinto",
                6,
                ["Arquétipo"],
                "Você recebe a habilidade de instinto do instinto selecionado em Dedicação de Bárbaro.",
                pre_requisitos="Dedicação de Bárbaro",
            ),
            construir_talento_arquetipo(
                "Fortitude do Irrefreável",
                12,
                ["Arquétipo"],
                "Sua graduação de proficiência em salvamentos de Fortitude aumenta para mestre.",
                pre_requisitos="especialista em salvamentos de Fortitude, Dedicação de Bárbaro",
            ),
        ],
    }

    bardo = {
        "id": "bardo",
        "nome": "Bardo",
        "classe_relacionada_id": "bardo",
        "pagina": 222,
        "conjurador": True,
        "tradicao_magica": "ocultista",
        "atributo_conjuracao": "carisma",
        "resumo": "Uma musa lhe inspirou a arriscar-se nos saberes ocultistas, permitindo-lhe conjurar algumas magias. Quanto mais você se aprofunda, mais poderosas suas performances se tornam.",
        "personagens_multiclasse": {
            "descricao": "O arquétipo de bardo concede efeitos poderosos que geralmente usam ações; ele é uma ótima escolha se você tiver ações para gastar.",
            "combinacoes": [],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Bardo",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Você conjura magias como um bardo e ganha a atividade Conjurar uma Magia. Você adquire um repertório de magias com dois truques mágicos comuns da lista de magias ocultistas, ou quaisquer outros truques mágicos dessa tradição que você conseguir aprender ou descobrir. Você é treinado em ataques de magia e CDs de magias para magias ocultistas. Seu atributo de conjuração para as magias do arquétipo de bardo é Carisma, e elas são consideradas magias ocultistas de bardo. Você se torna treinado em Ocultismo e Performance — para cada uma dessas perícias na qual já seja treinado, você se torna treinado em outra perícia à sua escolha. Escolha uma musa como se fosse um bardo. Você possui essa musa para todos os propósitos, inclusive para selecionar talentos dessa musa (mas não recebe quaisquer outras habilidades concedidas por ela).",
                pre_requisitos="Carisma 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de bardo.",
            ),
            construir_talento_arquetipo(
                "Conjuração Básica de Bardo",
                4,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração básica (página 219). Cada vez que receber um espaço de magia de um novo nível do arquétipo de bardo, acrescente uma magia ocultista comum ou outra magia que você tenha aprendido ou descoberto ao seu repertório (desde que seja do nível de magia e tradição mágica apropriados).",
                pre_requisitos="Dedicação de Bardo",
            ),
            construir_talento_arquetipo(
                "Sussurros da Musa Básico",
                4,
                ["Arquétipo"],
                "Você recebe um talento de bardo de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Bardo",
            ),
            construir_talento_arquetipo(
                "Contraperformance",
                6,
                ["Arquétipo"],
                "Você recebe a magia de composição contraperformance. Se ainda não possuir, você recebe uma reserva de foco com 1 Ponto de Foco, que pode Refocar engajando-se com sua musa (para mais sobre magias de composição, veja a página 97).",
                pre_requisitos="Dedicação de Bardo",
            ),
            construir_talento_arquetipo(
                "Sussurros da Musa Avançado",
                6,
                ["Arquétipo"],
                "Você recebe um talento de bardo. Para o propósito de atender seus pré-requisitos, seu nível de bardo é igual à metade de seu nível de personagem.",
                pre_requisitos="Sussurros da Musa Básico",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de bardo.",
            ),
            construir_talento_arquetipo(
                "Amplitude Ocultista",
                8,
                ["Arquétipo"],
                "Seu repertório é expandido, e você pode conjurar mais magias ocultistas a cada dia. Aumente a quantidade de magias em seu repertório e de espaços de magia que você recebe através de talentos de arquétipo de bardo em 1 para cada nível de magia (exceto pelos seus dois níveis de magia mais altos).",
                pre_requisitos="Conjuração Básica de Bardo",
            ),
            construir_talento_arquetipo(
                "Performance Inspiradora",
                8,
                ["Arquétipo"],
                "Você recebe o truque mágico de composição inspirar coragem.",
                pre_requisitos="Dedicação de Bardo",
            ),
            construir_talento_arquetipo(
                "Conjuração Especialista de Bardo",
                12,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração especialista (página 219).",
                pre_requisitos="mestre em Ocultismo, Conjuração Básica de Bardo",
            ),
            construir_talento_arquetipo(
                "Conjuração Mestre de Bardo",
                18,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração mestre (página 219).",
                pre_requisitos="lendário em Ocultismo, Conjuração Especialista de Bardo",
            ),
        ],
    }

    campeao = {
        "id": "campeao",
        "nome": "Campeão",
        "classe_relacionada_id": "campeao",
        "pagina": 223,
        "conjurador": False,
        "resumo": "Você fez um juramento solene à sua divindade, que lhe concedeu poderes de campeão para ajudá-lo em sua causa.",
        "personagens_multiclasse": {
            "descricao": "O arquétipo de campeão melhora consideravelmente suas defesas, especialmente usando armaduras. Ele é uma ótima forma para um personagem obter proficiência em armaduras ou uma reação defensiva poderosa.",
            "combinacoes": [],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Campeão",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Escolha uma divindade e uma causa como se fosse um campeão. Você se torna treinado em armaduras leves, médias e pesadas. Você se torna treinado em Religião e na perícia associada de sua divindade; para cada uma dessas perícias na qual já seja treinado, você se torna treinado em outra perícia à sua escolha. Você também se torna treinado na CD de classe de campeão. Você fica limitado pelo anátema de sua divindade e deve seguir o código de campeão e requerimento de tendência para sua causa. Você não recebe quaisquer outras habilidades da divindade ou causa escolhida.",
                pre_requisitos="Força 14, Carisma 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de campeão.",
            ),
            construir_talento_arquetipo(
                "Devoção Básica",
                4,
                ["Arquétipo"],
                "Você recebe um talento de campeão de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Campeão",
            ),
            construir_talento_arquetipo(
                "Resiliência de Campeão",
                4,
                ["Arquétipo"],
                "Você recebe 3 Pontos de Vida adicionais para cada talento de classe do arquétipo de campeão que possuir. Conforme continuar selecionando talentos de classe de arquétipo de campeão, você continuará a receber Pontos de Vida desta forma.",
                pre_requisitos="Dedicação de Campeão, sua classe concede no máximo uma quantidade de Pontos de Vida por nível igual a 8 + seu modificador de Constituição",
            ),
            construir_talento_arquetipo(
                "Toque de Cura",
                4,
                ["Arquétipo"],
                "Você recebe a magia de devoção apropriada para sua causa (imposição de mãos para o paladino, redentor e libertador). Se ainda não possuir, você recebe uma reserva de foco com 1 Ponto de Foco, que pode Refocar orando ou servindo sua divindade (para mais sobre magias de devoção, veja a página 108).",
                pre_requisitos="Dedicação de Campeão",
            ),
            construir_talento_arquetipo(
                "Aliado Divino",
                6,
                ["Arquétipo"],
                "Você recebe um aliado divino à sua escolha (página 108).",
                pre_requisitos="Dedicação de Campeão",
            ),
            construir_talento_arquetipo(
                "Devoção Avançada",
                6,
                ["Arquétipo"],
                "Você recebe um talento de campeão. Para o propósito de atender seus pré-requisitos, seu nível de campeão é igual à metade de seu nível de personagem.",
                pre_requisitos="Devoção Básica",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de campeão.",
            ),
            construir_talento_arquetipo(
                "Reação de Campeão",
                6,
                ["Arquétipo"],
                "Você pode usar a reação de campeão associada com sua causa.",
                pre_requisitos="Dedicação de Campeão",
            ),
            construir_talento_arquetipo(
                "Especialidade em Armaduras Diversas",
                14,
                ["Arquétipo"],
                "Suas graduações de proficiência em armaduras leves, médias e pesadas, assim como em defesa sem armadura, aumentam para especialista.",
                pre_requisitos="especialista em defesa sem armadura ou em um pelo menos um tipo de armadura, Dedicação de Campeão",
            ),
        ],
    }

    clerigo = {
        "id": "clerigo",
        "nome": "Clérigo",
        "classe_relacionada_id": "clerigo",
        "pagina": 224,
        "conjurador": True,
        "tradicao_magica": "divina",
        "atributo_conjuracao": "sabedoria",
        "resumo": "Você é um sacerdote ordenado de sua divindade e aprendeu até mesmo a conjurar algumas magias divinas. Embora seu treinamento principal seja outro, seu chamado religioso lhe fornece dons divinos.",
        "personagens_multiclasse": {
            "descricao": "O arquétipo de clérigo é uma ótima forma para criar um personagem de outra classe que seja devoto de uma divindade em particular. Os muitos domínios disponíveis para clérigos de divindades diferentes apresentam uma variedade de opções para magias de foco.",
            "combinacoes": [
                "Alquimistas clérigos funcionam bem em conjunto com o campo de cirurgião, curando várias aflições através de alquimia ou magias.",
                "Personagens de classes marciais que se tornem clérigos tipicamente procuram por uma magia de domínio potente ou alguma cura para usar em caso de necessidade.",
                "Feiticeiros divinos que se tornem clérigos se fortalecem como os conjuradores divinos supremos.",
                "Conjuradores de outras classes clérigos diversificam suas opções, tornando-se personagens teúrgicos que combinam duas tradições mágicas.",
            ],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Clérigo",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Você conjura magias como um clérigo e ganha a atividade Conjurar uma Magia. A cada dia, você pode preparar dois truques mágicos comuns da lista de magias divinas, ou quaisquer outros truques mágicos dessa tradição que conseguir aprender ou descobrir. Você é treinado em ataques de magia e CDs de magias para magias divinas. Seu atributo de conjuração para magias do arquétipo de clérigo é Sabedoria, e elas são consideradas magias divinas de clérigo. Escolha uma divindade como se fosse um clérigo. Você fica limitado pelo anátema dessa divindade. Você se torna treinado em Religião e na perícia associada de sua divindade; para cada uma dessas perícias na qual já seja treinado, você se torna treinado em outra perícia à sua escolha. Você não recebe quaisquer outras habilidades de sua divindade escolhida.",
                pre_requisitos="Sabedoria 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de clérigo.",
            ),
            construir_talento_arquetipo(
                "Conjuração Básica de Clérigo",
                4,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração básica (página 219). Você pode preparar magias de sua divindade nos espaços de magia de seu arquétipo de clérigo do nível de magia apropriado.",
                pre_requisitos="Dedicação de Clérigo",
            ),
            construir_talento_arquetipo(
                "Dogma Básico",
                4,
                ["Arquétipo"],
                "Você recebe um talento de clérigo de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Clérigo",
            ),
            construir_talento_arquetipo(
                "Dogma Avançado",
                6,
                ["Arquétipo"],
                "Você recebe um talento de clérigo. Para o propósito de atender seus pré-requisitos, seu nível de clérigo é igual à metade de seu nível de personagem.",
                pre_requisitos="Dogma Básico",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de clérigo.",
            ),
            construir_talento_arquetipo(
                "Amplitude Divina",
                8,
                ["Arquétipo"],
                "Você pode conjurar mais magias divinas a cada dia. Aumente a quantidade de espaços de magia que você recebe através de talentos de arquétipo de clérigo em 1 para cada nível de magia (exceto pelos seus dois níveis de magia mais altos).",
                pre_requisitos="Conjuração Básica de Clérigo",
            ),
            construir_talento_arquetipo(
                "Conjuração Especialista de Clérigo",
                12,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração especialista (página 219).",
                pre_requisitos="mestre em Religião, Conjuração Básica de Clérigo",
            ),
            construir_talento_arquetipo(
                "Conjuração Mestre de Clérigo",
                18,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração mestre (página 219).",
                pre_requisitos="lendário em Religião, Conjuração Especialista de Clérigo",
            ),
        ],
    }

    druida = {
        "id": "druida",
        "nome": "Druida",
        "classe_relacionada_id": "druida",
        "pagina": 225,
        "conjurador": True,
        "tradicao_magica": "primal",
        "atributo_conjuracao": "sabedoria",
        "resumo": "Você adentrou um círculo druídico e aprendeu alguns dos segredos dessa ordem, desenvolvendo poderes primais.",
        "personagens_multiclasse": {
            "descricao": "O arquétipo de druida pode fornecer um pouco de cura ou dano elemental e também pode aumentar sua utilidade em um ambiente natural através de magias como falar com animais e mesclar-se às rochas.",
            "combinacoes": [],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Druida",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Você conjura magias como um druida e ganha a atividade Conjurar uma Magia. A cada dia, você pode preparar dois truques mágicos comuns da lista de magias primais, ou quaisquer outros truques mágicos dessa tradição que conseguir aprender ou descobrir. Você é treinado em ataques de magia e CDs de magias para magias primais. Seu atributo de conjuração para magias do arquétipo de druida é Sabedoria, e elas são consideradas magias primais de druida. Você aprende o idioma Druídico. Escolha uma ordem como se fosse um druida. Você se torna um membro dessa ordem e fica limitado pelo anátema dela, o que lhe permite selecionar talentos dessa ordem. Você se torna treinado em Natureza e na perícia associada de sua ordem; para cada uma dessas perícias na qual já seja treinado, você se torna treinado em outra perícia à sua escolha. Você não recebe quaisquer outras habilidades da ordem escolhida.",
                pre_requisitos="Sabedoria 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de druida.",
            ),
            construir_talento_arquetipo(
                "Conjuração Básica de Druida",
                4,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração básica (página 219).",
                pre_requisitos="Dedicação de Druida",
            ),
            construir_talento_arquetipo(
                "Magia de Ordem",
                4,
                ["Arquétipo"],
                "Você recebe a magia de ordem inicial de sua ordem. Se ainda não possuir, você recebe uma reserva de foco com 1 Ponto de Foco, que pode Refocar comungando com a natureza (para mais sobre magias de ordem, veja a página 130).",
                pre_requisitos="Dedicação de Druida",
            ),
            construir_talento_arquetipo(
                "Selvageria Básica",
                4,
                ["Arquétipo"],
                "Você recebe um talento de druida de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Druida",
            ),
            construir_talento_arquetipo(
                "Selvageria Avançada",
                6,
                ["Arquétipo"],
                "Você recebe um talento de druida. Para o propósito de atender seus pré-requisitos, seu nível de druida é igual à metade de seu nível de personagem.",
                pre_requisitos="Selvageria Básica",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de druida.",
            ),
            construir_talento_arquetipo(
                "Amplitude Primal",
                8,
                ["Arquétipo"],
                "Você pode conjurar mais magias primais a cada dia. Aumente a quantidade de espaços de magia que você recebe através de talentos de arquétipo de druida em 1 para cada nível de magia (exceto pelos seus dois níveis de magia mais altos).",
                pre_requisitos="Conjuração Básica de Druida",
            ),
            construir_talento_arquetipo(
                "Conjuração Especialista de Druida",
                12,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração especialista (página 219).",
                pre_requisitos="mestre em Natureza, Conjuração Básica de Druida",
            ),
            construir_talento_arquetipo(
                "Conjuração Mestre de Druida",
                18,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração mestre (página 219).",
                pre_requisitos="lendário em Natureza, Conjuração Especialista de Druida",
            ),
        ],
    }

    return [alquimista, barbaro, bardo, campeao, clerigo, druida]


def construir_demais_arquetipos() -> list[dict[str, Any]]:
    feiticeiro = {
        "id": "feiticeiro",
        "nome": "Feiticeiro",
        "classe_relacionada_id": "feiticeiro",
        "pagina": 226,
        "conjurador": True,
        "tradicao_magica": "determinada_pela_linhagem",
        "atributo_conjuracao": "carisma",
        "resumo": "Você persuade o poder mágico em seu sangue a se manifestar, acessando magia que ninguém espera que você possua.",
        "personagens_multiclasse": {
            "descricao": "Escolher o arquétipo de feiticeiro é um método simples para escolher algumas magias bem úteis, como invisibilidade e rapidez.",
            "combinacoes": [],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Feiticeiro",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Escolha uma linhagem. Você se torna treinado nas duas perícias dessa linhagem; para cada uma dessas perícias na qual já seja treinado, você se torna treinado em outra perícia à sua escolha. Você conjura magias como um feiticeiro e ganha a atividade Conjurar uma Magia. Você adquire um repertório de magias com dois truques mágicos comuns da lista de magias associada à sua linhagem, das magias concedidas por sua linhagem, ou quaisquer outros truques mágicos dessa tradição que consiga aprender ou descobrir. Você é treinado em ataques de magia e CDs de magias para magias da tradição de sua linhagem. Seu atributo de conjuração para magias do arquétipo de feiticeiro é Carisma, e elas são consideradas magias de feiticeiro da tradição de sua linhagem.",
                pre_requisitos="Carisma 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de feiticeiro.",
            ),
            construir_talento_arquetipo(
                "Conjuração Básica de Feiticeiro",
                4,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração básica (página 219). Cada vez que receber um espaço de magia de um novo nível do arquétipo de feiticeiro, acrescente uma magia comum da tradição de sua linhagem, uma magia concedida da linhagem escolhida ou uma magia que você tenha aprendido ou descoberto ao seu repertório (desde que seja do nível de magia e tradição mágica apropriados).",
                pre_requisitos="Dedicação de Feiticeiro",
            ),
            construir_talento_arquetipo(
                "Magia de Linhagem Básica",
                4,
                ["Arquétipo"],
                "Você recebe a magia de linhagem inicial de sua linhagem. Se ainda não possuir, você recebe uma reserva de foco com 1 Ponto de Foco, que pode Refocar sem qualquer esforço especial (para mais sobre magias de linhagem, veja a página 194).",
                pre_requisitos="Dedicação de Feiticeiro",
            ),
            construir_talento_arquetipo(
                "Potência Sanguínea Básica",
                4,
                ["Arquétipo"],
                "Você recebe um talento de feiticeiro de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Feiticeiro",
            ),
            construir_talento_arquetipo(
                "Potência Sanguínea Avançada",
                6,
                ["Arquétipo"],
                "Você recebe um talento de feiticeiro. Para o propósito de atender seus pré-requisitos, seu nível de feiticeiro é igual à metade de seu nível de personagem.",
                pre_requisitos="Potência Sanguínea Básica",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de feiticeiro.",
            ),
            construir_talento_arquetipo(
                "Amplitude de Linhagem",
                8,
                ["Arquétipo"],
                "Seu repertório é expandido, e você pode conjurar mais magias da tradição de sua linhagem a cada dia. Aumente a quantidade de magias em seu repertório e de espaços de magia que você recebe através de talentos de arquétipo de feiticeiro em 1 para cada nível de magia (exceto pelos seus dois níveis de magia mais altos).",
                pre_requisitos="Conjuração Básica de Feiticeiro",
            ),
            construir_talento_arquetipo(
                "Conjuração Especialista de Feiticeiro",
                12,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração especialista (página 219).",
                pre_requisitos="mestre em Arcanismo, Natureza, Ocultismo ou Religião, dependendo de sua linhagem; Conjuração Básica de Feiticeiro",
            ),
            construir_talento_arquetipo(
                "Conjuração Mestre de Feiticeiro",
                18,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração mestre (página 219).",
                pre_requisitos="lendário em Arcanismo, Natureza, Ocultismo ou Religião, dependendo de sua linhagem; Conjuração Especialista de Feiticeiro",
            ),
        ],
    }

    guerreiro = {
        "id": "guerreiro",
        "nome": "Guerreiro",
        "classe_relacionada_id": "guerreiro",
        "pagina": 227,
        "conjurador": False,
        "resumo": "Você passou certo tempo aprendendo a arte da guerra, aumentando sua habilidade com armas marciais e em vestir armaduras. Com mais treinamento, você pode se tornar um verdadeiro especialista em combate.",
        "personagens_multiclasse": {
            "descricao": "O arquétipo de guerreiro concede acesso a ótimos talentos para personagens dedicados a qualquer estilo de combate, e é particularmente útil para personagens buscando diversificar suas habilidades ofensivas ou focar em armas mais poderosas.",
            "combinacoes": [
                "Bárbaros guerreiros podem combinar suas habilidades de armas de duas mãos com alguns dos talentos de duas mãos do guerreiro para efeitos devastadores.",
                "Campeões guerreiros focam em um estilo de combate exemplificado por sua divindade. Um campeão que usa escudo tem o melhor dos dois mundos no que diz respeito a talentos de escudo.",
                "Ladinos guerreiros podem fazer bom uso dos talentos de guerreiro dedicado aos estilos de combate de mão livre, com duas armas ou de arquearia.",
                "Monges guerreiros são ótimos em combinar estilos de armas incomuns. Por exemplo, monges não se restringem ao manter uma mão livre, pois ainda podem usá-la para socar da mesma forma.",
                "Patrulheiros guerreiros podem se especializar em arquearia ou usar seus talentos de guerreiro para combinar estilos de combate de forma inusitada.",
                "Conjuradores guerreiros se beneficiam bastante das proficiências adicionais em armas, e o guerreiro é uma escolha sólida para qualquer conjurador particularmente inclinado ao combate marcial.",
            ],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Guerreiro",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Você se torna treinado em armas simples e armas marciais. Você se torna treinado em Acrobatismo ou Atletismo; se já for treinado nestas duas perícias, você se torna treinado em outra perícia à sua escolha. Você também se torna treinado em CD de classe de guerreiro.",
                pre_requisitos="Força 14, Destreza 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de guerreiro.",
            ),
            construir_talento_arquetipo(
                "Manobra Básica",
                4,
                ["Arquétipo"],
                "Você recebe um talento de guerreiro de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Guerreiro",
            ),
            construir_talento_arquetipo(
                "Oportunista",
                4,
                ["Arquétipo"],
                "Você ganha a reação Ataque de Oportunidade (página 154).",
                pre_requisitos="Dedicação de Guerreiro",
            ),
            construir_talento_arquetipo(
                "Resiliência de Guerreiro",
                4,
                ["Arquétipo"],
                "Você recebe 3 Pontos de Vida adicionais para cada talento de classe do arquétipo de guerreiro que possuir. Conforme continuar selecionando talentos de classe de arquétipo de guerreiro, você continuará a receber Pontos de Vida desta forma.",
                pre_requisitos="Dedicação de Guerreiro, sua classe concede no máximo uma quantidade de Pontos de Vida por nível igual a 8 + seu modificador de Constituição",
            ),
            construir_talento_arquetipo(
                "Manobra Avançada",
                6,
                ["Arquétipo"],
                "Você recebe um talento de guerreiro. Para o propósito de atender seus pré-requisitos, seu nível de guerreiro é igual à metade de seu nível de personagem.",
                pre_requisitos="Manobra Básica",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de guerreiro.",
            ),
            construir_talento_arquetipo(
                "Especialidade em Armas Diversas",
                12,
                ["Arquétipo"],
                "Suas graduações de proficiência em armas simples e marciais aumentam para especialista, e sua graduação de proficiência em armas avançadas aumenta para treinado.",
                pre_requisitos="especialista em qualquer tipo de arma ou ataque desarmado, Dedicação de Guerreiro",
            ),
        ],
    }

    ladino = {
        "id": "ladino",
        "nome": "Ladino",
        "classe_relacionada_id": "ladino",
        "pagina": 228,
        "conjurador": False,
        "resumo": "Você aprendeu a se esgueirar, roubar e desativar armadilhas. Com tempo e sorte, você se tornará capaz de mover-se pelas sombras, atacar sem ser visto e escapar sem ser percebido.",
        "personagens_multiclasse": {
            "descricao": "Quase qualquer personagem pode se beneficiar das várias perícias e truques concedidos pelo arquétipo de ladino.",
            "combinacoes": [
                "Alquimistas ladinos podem usar Envenenar Arma de ladino com seus venenos diários, e o ataque furtivo é uma ótima melhoria para o dano de suas bombas.",
                "Bárbaros ladinos podem se tornar mestres em todos os salvamentos e diversificar suas perícias.",
                "Campeões ladinos adicionam o dano de ataque furtivo enquanto protegem seus parceiros de flanqueamento do perigo.",
                "Guerreiros ladinos combinam a precisão do guerreiro com dano extra — uma combinação mortal para guerreiros arqueiros e de acuidade.",
                "Monges ladinos possuem grande sinergia, já que muitas posturas concedem Golpes poderosos que funcionam com ataque furtivo.",
                "Patrulheiros ladinos se beneficiam do foco compartilhado em rastrear adversários e pegá-los desprevenidos. A excelência de rajada lhe permite desferir muitos ataques furtivos, e a excelência de precisão reforça o dano de precisão.",
                "Conjuradores ladinos usam essa multiclasse para aumentar suas perícias ou selecionar talentos de truques de ladino que os mantenham a salvo, como Mobilidade.",
            ],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Ladino",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Você recebe um talento de perícia e a característica de classe de ladino ataque surpresa (página 169). Você se torna treinado em armaduras leves. Você se torna treinado em Furtividade ou Ladroagem e em uma outra perícia à sua escolha; se já for treinado em Furtividade e Ladroagem, você se torna treinado em uma outra perícia à sua escolha. Você se torna treinado na CD de classe de ladino.",
                pre_requisitos="Destreza 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de ladino.",
            ),
            construir_talento_arquetipo(
                "Atacante Furtivo",
                4,
                ["Arquétipo"],
                "Você recebe a característica de classe ataque furtivo (página 169), exceto que ela causa 1d4 de dano e aumenta para 1d6 no 6º nível. Você não aumenta a quantidade de dados conforme adquire níveis.",
                pre_requisitos="Dedicação de Ladino",
            ),
            construir_talento_arquetipo(
                "Trapaça Básica",
                4,
                ["Arquétipo"],
                "Você recebe um talento de ladino de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Ladino",
            ),
            construir_talento_arquetipo(
                "Trapaça Avançada",
                6,
                ["Arquétipo"],
                "Você recebe um talento de ladino. Para o propósito de atender seus pré-requisitos, seu nível de ladino é igual à metade de seu nível de personagem.",
                pre_requisitos="Trapaça Básica",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de ladino.",
            ),
            construir_talento_arquetipo(
                "Maestria em Perícia",
                8,
                ["Arquétipo"],
                "Aumente sua graduação de proficiência em uma de suas perícias de especialista para mestre e em outra de suas perícias de treinado para especialista. Você recebe um talento de perícia associado com uma dessas perícias escolhidas.",
                pre_requisitos="Dedicação de Ladino, treinado em pelo menos uma perícia, especialista em pelo menos uma perícia",
                especial="Você pode selecionar este talento até cinco vezes.",
            ),
            construir_talento_arquetipo(
                "Esquiva Excepcional",
                10,
                ["Arquétipo"],
                "Você recebe a característica de classe negar vantagem (página 169).",
                pre_requisitos="Dedicação de Ladino",
            ),
            construir_talento_arquetipo(
                "Evasividade",
                12,
                ["Arquétipo"],
                "Sua graduação de proficiência em salvamentos de Reflexos aumenta para mestre.",
                pre_requisitos="Dedicação de Ladino, especialista em salvamento de Reflexos",
            ),
        ],
    }

    mago = {
        "id": "mago",
        "nome": "Mago",
        "classe_relacionada_id": "mago",
        "pagina": 229,
        "conjurador": True,
        "tradicao_magica": "arcana",
        "atributo_conjuracao": "inteligencia",
        "resumo": "Você tem explorado as artes arcanas e, através de disciplina e estudo acadêmico, aprendeu a conjurar algumas magias.",
        "personagens_multiclasse": {
            "descricao": "O arquétipo de mago concede versáteis magias preparadas, sendo perfeito para personagens buscando alguma utilidade extra.",
            "combinacoes": [],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Mago",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Você conjura magias como um mago, recebendo um grimório com quatro truques mágicos comuns e a atividade Conjurar uma Magia. A cada dia, você pode preparar dois truques mágicos da tradição arcana que estejam registrados em seu grimório. Você é treinado em ataques de magia e CDs de magias para magias arcanas. Seu atributo de conjuração para magias do arquétipo de mago é Inteligência, e elas são consideradas magias arcanas de mago. Você se torna treinado em Arcanismo; se já for treinado em Arcanismo, em vez disso você se torna treinado em outra perícia à sua escolha.",
                pre_requisitos="Inteligência 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de mago.",
            ),
            construir_talento_arquetipo(
                "Arcana Básica",
                4,
                ["Arquétipo"],
                "Você recebe um talento de mago de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Mago",
            ),
            construir_talento_arquetipo(
                "Conjuração Básica de Mago",
                4,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração básica (página 219). Cada vez que receber um espaço de magia de um novo nível do arquétipo de mago, acrescente duas magias comuns da tradição arcana do mesmo nível ao seu grimório.",
                pre_requisitos="Dedicação de Mago",
            ),
            construir_talento_arquetipo(
                "Magia de Escola Arcana",
                4,
                ["Arquétipo"],
                "Selecione uma escola de magia. Você recebe a magia de escola inicial dessa escola. Se ainda não possuir, você recebe uma reserva de foco com 1 Ponto de Foco, que pode Refocar estudando (para mais sobre magias de escola, veja a página 180).",
                pre_requisitos="Dedicação de Mago",
            ),
            construir_talento_arquetipo(
                "Arcana Avançada",
                6,
                ["Arquétipo"],
                "Você recebe um talento de mago. Para o propósito de atender seus pré-requisitos, seu nível de mago é igual à metade de seu nível de personagem.",
                pre_requisitos="Arcana Básica",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de mago.",
            ),
            construir_talento_arquetipo(
                "Amplitude Arcana",
                8,
                ["Arquétipo"],
                "Você pode conjurar mais magias arcanas a cada dia. Aumente a quantidade de espaços de magia que você recebe através de talentos de arquétipo de mago em 1 para cada nível de magia (exceto pelos seus dois níveis de magia mais altos).",
                pre_requisitos="Conjuração Básica de Mago",
            ),
            construir_talento_arquetipo(
                "Conjuração Especialista de Mago",
                12,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração especialista (página 219).",
                pre_requisitos="mestre em Arcanismo, Conjuração Básica de Mago",
            ),
            construir_talento_arquetipo(
                "Conjuração Mestre de Mago",
                18,
                ["Arquétipo"],
                "Você recebe os benefícios de conjuração mestre (página 219).",
                pre_requisitos="lendário em Arcanismo, Conjuração Especialista de Mago",
            ),
        ],
    }

    monge = {
        "id": "monge",
        "nome": "Monge",
        "classe_relacionada_id": "monge",
        "pagina": 230,
        "conjurador": False,
        "resumo": "O treinamento monástico lhe ensinou artes marciais e o permitiu levar sua mente, corpo e espírito a novos patamares.",
        "personagens_multiclasse": {
            "descricao": "O arquétipo de monge é uma escolha forte para qualquer personagem que luta sem armadura ou com ataques desarmados.",
            "combinacoes": [
                "Bárbaros monges com o instinto animal podem combinar o excelente dano desarmado do bárbaro com as diversas habilidades especiais desarmadas de monge.",
                "Campeões monges são perfeitos para representar devotos de Irori ou outras divindades que favorecem ataques desarmados.",
                "Guerreiros monges podem aprimorar seu combate de mão livre e acrescentar mobilidade às opções do guerreiro.",
                "Ladinos monges são incrivelmente efetivos devido a posturas que concedem alguns dos melhores ataques ágeis de acuidade e pela rajada permitir mais ataques furtivos.",
                "Conjuradores monges podem lutar com uma mão livre e ainda usar componentes materiais para conjurar magias.",
            ],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Monge",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Você se torna treinado em ataques desarmados e ganha a característica de classe punho poderoso (página 192). Você se torna treinado em Acrobatismo ou Atletismo; se já for treinado nestas duas perícias, você se torna treinado em outra perícia à sua escolha. Você também se torna treinado em CD de classe de monge.",
                pre_requisitos="Força 14, Destreza 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de monge.",
            ),
            construir_talento_arquetipo(
                "Kata Básico",
                4,
                ["Arquétipo"],
                "Você recebe um talento de monge de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Monge",
            ),
            construir_talento_arquetipo(
                "Resiliência de Monge",
                4,
                ["Arquétipo"],
                "Você recebe 3 Pontos de Vida adicionais para cada talento de classe do arquétipo de monge que possuir. Conforme continuar selecionando talentos de classe de arquétipo de monge, você continuará a receber Pontos de Vida desta forma.",
                pre_requisitos="Dedicação de Monge, sua classe concede no máximo uma quantidade de Pontos de Vida por nível igual a 8 + seu modificador de Constituição",
            ),
            construir_talento_arquetipo(
                "Kata Avançado",
                6,
                ["Arquétipo"],
                "Você recebe um talento de monge. Para o propósito de atender seus pré-requisitos, seu nível de monge é igual à metade de seu nível de personagem.",
                pre_requisitos="Kata Básico",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de monge.",
            ),
            construir_talento_arquetipo(
                "Movimentos de Monge",
                8,
                ["Arquétipo"],
                "Você recebe +3 metros de bônus de estado em sua Velocidade quando não estiver vestindo armadura.",
                pre_requisitos="Dedicação de Monge",
            ),
            construir_talento_arquetipo(
                "Rajada de Monge",
                10,
                ["Arquétipo"],
                "Você ganha a ação Rajada de Golpes (página 192).",
                pre_requisitos="Dedicação de Monge",
            ),
            construir_talento_arquetipo(
                "Caminho da Perfeição",
                12,
                ["Arquétipo"],
                "Escolha uma jogada de salvamento (Fortitude, Reflexos ou Vontade) na qual você seja especialista. Sua graduação de proficiência na jogada de salvamento escolhida aumenta para mestre.",
                pre_requisitos="especialista em pelo menos uma jogada de salvamento, Dedicação de Monge",
            ),
        ],
    }

    patrulheiro = {
        "id": "patrulheiro",
        "nome": "Patrulheiro",
        "classe_relacionada_id": "patrulheiro",
        "pagina": 231,
        "conjurador": False,
        "resumo": "Você estudou caça, rastreamento e sobrevivência nos ermos, acrescentando habilidades de patrulheiro ao seu conjunto de perícias.",
        "personagens_multiclasse": {
            "descricao": "O arquétipo de patrulheiro oferece acesso a opções excelentes para aprimorar o conhecimento sobre monstros e perícias de sobrevivência de um personagem, mas o patrulheiro é particularmente interessante para qualquer personagem que queira se tornar um arqueiro dedicado.",
            "combinacoes": [
                "Alquimistas patrulheiros podem acrescentar arapucas a seus itens gratuitos diários, beneficiando-se de um bom modificador de Manufatura e usando sua alta Inteligência de forma excepcional com os talentos de conhecimento sobre monstros. O arquétipo de patrulheiro também é útil para bombardeiros que desejam alternar com ataques de arco.",
                "Campeões patrulheiros são particularmente adequados para divindades ligadas tematicamente à natureza ou que têm o arco como sua arma favorita (ou, no caso de Erastil, ambos!).",
                "Guerreiros patrulheiros formam os mais formidáveis arqueiros, combinando os melhores talentos de arquearia de ambas as classes para criar um estilo de combate único para cada guerreiro patrulheiro.",
                "Ladinos patrulheiros são excelente franco-atiradores ou escaramuçadores à distância, e as arapucas permitem que eles fiquem do outro lado das armadilhas para variar.",
                "Conjuradores patrulheiros se beneficiam bastante dos talentos de suporte do patrulheiro, alternando suas magias com ataques com armas à distância. Entre os conjuradores, druidas oferecem a combinação mais temática com patrulheiros, permitindo-lhe criar um verdadeiro mestre dos ermos.",
            ],
        },
        "talentos": [
            construir_talento_arquetipo(
                "Dedicação de Patrulheiro",
                2,
                ["Arquétipo", "Dedicação", "Multiclasse"],
                "Você se torna treinado em Sobrevivência; se já for treinado em Sobrevivência, em vez disso você se torna treinado em outra perícia à sua escolha. Você se torna treinado na CD de classe de patrulheiro. Você pode usar a ação Caçar Presa (página 204).",
                pre_requisitos="Destreza 14",
                especial="Você não pode selecionar outro talento de dedicação até ter recebido dois outros talentos do arquétipo de patrulheiro.",
            ),
            construir_talento_arquetipo(
                "Resiliência de Patrulheiro",
                4,
                ["Arquétipo"],
                "Você recebe 3 Pontos de Vida adicionais para cada talento de classe do arquétipo de patrulheiro que possuir. Conforme continuar selecionando talentos de classe de arquétipo de patrulheiro, você continuará a receber Pontos de Vida desta forma.",
                pre_requisitos="Dedicação de Patrulheiro, sua classe concede no máximo uma quantidade de Pontos de Vida por nível igual a 8 + seu modificador de Constituição",
            ),
            construir_talento_arquetipo(
                "Truque de Caçador Básico",
                4,
                ["Arquétipo"],
                "Você recebe um talento de patrulheiro de 1º ou 2º nível.",
                pre_requisitos="Dedicação de Patrulheiro",
            ),
            construir_talento_arquetipo(
                "Truque de Caçador Avançado",
                6,
                ["Arquétipo"],
                "Você recebe um talento de patrulheiro. Para o propósito de atender seus pré-requisitos, seu nível de patrulheiro é igual à metade de seu nível de personagem.",
                pre_requisitos="Truque de Caçador Básico",
                especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você recebe outro talento de patrulheiro.",
            ),
            construir_talento_arquetipo(
                "Mestre Observador",
                12,
                ["Arquétipo"],
                "Sua graduação de proficiência em Percepção aumenta para mestre.",
                pre_requisitos="especialista em Percepção, Dedicação de Patrulheiro",
            ),
        ],
    }

    return [feiticeiro, guerreiro, ladino, mago, monge, patrulheiro]


def montar_dados_arquetipos_multiclasse() -> dict[str, Any]:
    regras_gerais = {
        "pagina": 219,
        "descricao": "Existem infinitos conceitos de personagem possíveis, mas você pode achar que os talentos e opções de habilidades de uma única classe não são o suficiente para dar vida ao seu personagem. Arquétipos lhe permitem expandir o escopo da classe de seu personagem recebendo outras habilidades inusitadas. Aplicar um arquétipo requer que você selecione talentos de arquétipo em vez de talentos de classe. Uma vez que tenha escolhido o talento de dedicação, você pode selecionar qualquer talento desse arquétipo no lugar de um talento de classe (desde que atenda a seus pré-requisitos). O talento de arquétipo selecionado ainda estará sujeito a quaisquer restrições de seleção do talento de classe que ele substituir. Talentos de arquétipo recebidos no lugar de um talento de classe são chamados de talentos de classe de arquétipo.",
        "talentos_pericia_de_arquetipo": "Ocasionalmente, um talento de arquétipo funciona como um talento de perícia em vez de um talento de classe (possuem o traço perícia e são selecionados no lugar de um talento de perícia). Eles não são considerados talentos de classe de arquétipo.",
        "regra_dedicacao": "Após selecionar um talento de dedicação de um arquétipo, você deve atender a todos os requerimentos dele antes de selecionar um talento de dedicação de outro arquétipo (tipicamente obtendo dois outros talentos da lista do arquétipo). Você não pode retreinar um talento de dedicação enquanto possuir quaisquer outros talentos desse arquétipo.",
        "pre_requisitos_talentos_concedidos": "Às vezes um talento de arquétipo lhe permite receber outro talento (como Concocção Básica de Alquimista). Você ainda deve sempre atender aos pré-requisitos do talento recebido desta forma.",
        "tipos_especiais": {
            "arquetipos_de_multiclasse": {
                "traco": "Multiclasse",
                "descricao": "Arquétipos com o traço multiclasse representam uma diversificação do seu treinamento aprendendo especialidades de outra classe. Você não pode selecionar um talento de dedicação de arquétipo de multiclasse se for membro da classe de mesmo nome (por exemplo, um guerreiro não pode selecionar o talento Dedicação de Guerreiro). Todos os arquétipos apresentados no Livro Básico são de multiclasse.",
            },
            "arquetipos_de_classe": {
                "traco": "Classe",
                "descricao": "Arquétipos com o traço classe representam uma divergência fundamental das especialidades de sua classe, mas uma que existe dentro do contexto geral de sua classe. Você pode selecionar um arquétipo de classe somente se for membro da classe de mesmo nome. Se um arquétipo de classe alterar características iniciais no 1º nível, você deve selecionar o talento de dedicação correspondente no 2º nível. Você nunca pode possuir mais de um arquétipo de classe.",
            },
        },
        "arquetipos_de_conjurador": {
            "descricao": "Alguns arquétipos lhe concedem um grau substancial de conjuração, embora um pouco mais lento que um personagem de uma classe conjuradora. No Livro Básico, os arquétipos de conjuração são bardo, clérigo, druida, feiticeiro e mago. Um arquétipo de conjurador lhe permite usar pergaminhos, cajados e varinhas da mesma forma que um membro de uma classe conjuradora. Todos os espaços de magia recebidos de arquétipos de conjurador possuem restrições dependendo do arquétipo.",
            "arquetipos_aplicaveis": ["bardo", "clerigo", "druida", "feiticeiro", "mago"],
            "niveis_conjuracao": [
                {
                    "id": "conjuracao_basica",
                    "nome": "Talento de Conjuração Básica",
                    "nivel_minimo": 4,
                    "progressao_espacos": {"4": 1, "6": 2, "8": 3},
                    "descricao": "Disponível no 4º nível, concede um espaço de magia de 1º nível. No 6º nível, concede um espaço de magia de 2º nível e, se possuir um repertório de magias, permite selecionar uma magia do repertório como uma magia emblemática. No 8º nível, concede um espaço de magia de 3º nível.",
                },
                {
                    "id": "conjuracao_especialista",
                    "nome": "Talento de Conjuração Especialista",
                    "nivel_minimo": 12,
                    "proficiencia_concedida": "especialista em ataques de magia e CDs de magias da tradição mágica apropriada",
                    "progressao_espacos": {"12": 4, "14": 5, "16": 6},
                    "descricao": "Selecionável a partir do 12º nível, torna especialista em ataques de magia e CDs de magias da tradição apropriada e concede um espaço de magia de 4º nível (e uma segunda magia emblemática se possuir repertório). No 14º nível, concede um espaço de 5º nível. No 16º nível, concede um espaço de 6º nível.",
                },
                {
                    "id": "conjuracao_mestre",
                    "nome": "Talento de Conjuração Mestre",
                    "nivel_minimo": 18,
                    "proficiencia_concedida": "mestre em ataques de magia e CDs de magias da tradição mágica apropriada",
                    "progressao_espacos": {"18": 7, "20": 8},
                    "descricao": "Ao alcançar o 18º nível, torna mestre em ataques de magia e CDs de magias da tradição apropriada e concede um espaço de magia de 7º nível (e uma terceira magia emblemática se possuir repertório). No 20º nível, concede um espaço de 8º nível.",
                },
            ],
        },
    }

    arquetipos = construir_primeiros_arquetipos() + construir_demais_arquetipos()

    return {
        "meta": {
            "titulo": "Capítulo 3: Arquétipos e Multiclasse — Pathfinder 2E Livro Básico",
            "arquivo_origem": "ref/Classes 03.pdf",
            "paginas_livro_basico": "219-231",
            "versao": "1.0.0",
            "observacoes": "Regras gerais de Arquétipos, Arquétipos de Multiclasse, Arquétipos de Classe e Arquétipos de Conjurador, além dos 12 arquétipos de multiclasse do Livro Básico e seus 85 talentos.",
        },
        "regras_gerais": regras_gerais,
        "arquetipos": arquetipos,
    }


def validar_arquetipos_multiclasse_json(dados: dict[str, Any]) -> None:
    arquetipos = dados["arquetipos"]
    esperado_ordem = [
        "alquimista",
        "barbaro",
        "bardo",
        "campeao",
        "clerigo",
        "druida",
        "feiticeiro",
        "guerreiro",
        "ladino",
        "mago",
        "monge",
        "patrulheiro",
    ]
    assert [a["id"] for a in arquetipos] == esperado_ordem

    contagens_esperadas = {
        "alquimista": 6,
        "barbaro": 6,
        "bardo": 9,
        "campeao": 8,
        "clerigo": 7,
        "druida": 8,
        "feiticeiro": 8,
        "guerreiro": 6,
        "ladino": 7,
        "mago": 8,
        "monge": 7,
        "patrulheiro": 5,
    }

    total_talentos = 0
    todos_ids: list[str] = []
    for arq in arquetipos:
        talentos = arq["talentos"]
        assert len(talentos) == contagens_esperadas[arq["id"]], (
            f"{arq['id']}: esperado {contagens_esperadas[arq['id']]}, obtido {len(talentos)}"
        )
        ids_arq = [t["id"] for t in talentos]
        assert len(ids_arq) == len(set(ids_arq)), f"IDs duplicados em {arq['id']}"
        assert talentos[0]["nivel"] == 2 and "Dedicação" in talentos[0]["tracos"]
        total_talentos += len(talentos)
        todos_ids.extend(ids_arq)

    assert total_talentos == 85
    assert len(todos_ids) == len(set(todos_ids)), "Há IDs de talentos repetidos entre arquétipos"


def main() -> None:
    dados = montar_dados_arquetipos_multiclasse()
    validar_arquetipos_multiclasse_json(dados)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_SAIDA.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")

    print(f"Arquivo gerado com sucesso: {CAMINHO_SAIDA}")
    print(f"Total de arquétipos multiclasse: {len(dados['arquetipos'])}")
    print(f"Total de talentos de arquétipo: {sum(len(a['talentos']) for a in dados['arquetipos'])}")


if __name__ == "__main__":
    main()
