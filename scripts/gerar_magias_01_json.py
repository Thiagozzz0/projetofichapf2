from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

import pymupdf


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_PDF = RAIZ_PROJETO / "ref" / "Enchanced 01.pdf"
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "magias01.json"

DESLOCAMENTO_PAGINA_LIVRO = 297  # Índice 0 do PDF corresponde à pág. 297 do Livro Básico

TRADICOES_CABECALHO = {
    "MAGIAS ARCANAS": "arcana",
    "MAGIAS DIVINAS": "divina",
    "MAGIAS OCULTISTAS": "ocultista",
    "MAGIAS PRIMAIS": "primal",
}

ESCOLAS_ABREV = {
    "abj": "Abjuração",
    "adv": "Adivinhação",
    "con": "Conjuração",
    "enc": "Encantamento",
    "evo": "Evocação",
    "ilu": "Ilusão",
    "nec": "Necromancia",
    "tra": "Transmutação",
}

ESCOLAS_MAIUSCULAS = {
    "ABJURAÇÃO": "Abjuração",
    "ADIVINHAÇÃO": "Adivinhação",
    "CONJURAÇÃO": "Conjuração",
    "ENCANTAMENTO": "Encantamento",
    "EVOCAÇÃO": "Evocação",
    "ILUSÃO": "Ilusão",
    "NECROMANCIA": "Necromancia",
    "TRANSMUTAÇÃO": "Transmutação",
}

MAPA_TRACOS_CANONICOS = {
    "TRUQUE-MÁGICO": "Truque Mágico",
    "TRUQUE MÁGICO": "Truque Mágico",
    "NÃO-LETAL": "Não-Letal",
}

ROTULOS_METADADOS = {
    "Tradições",
    "Execução",
    "Acionamento",
    "Requerimentos",
    "Custo",
    "Distância",
    "Área",
    "Alvos",
    "Alvo",
    "Salvamento",
    "Duração",
}

ROTULOS_RESULTADOS = {
    "Sucesso Crítico": "sucesso_critico",
    "Sucesso": "sucesso",
    "Falha": "falha",
    "Falha Crítica": "falha_critica",
}

PRESERVAR_HIFEN_DIR = {
    "a",
    "as",
    "o",
    "os",
    "lo",
    "la",
    "los",
    "las",
    "no",
    "nos",
    "nas",
    "lhe",
    "lhes",
    "me",
    "te",
    "se",
    "vos",
    "vivo",
    "viva",
    "vivos",
    "vivas",
    "mágico",
    "mágica",
    "mágicos",
    "mágicas",
    "nativo",
    "nativa",
    "nativos",
    "nativas",
    "combativo",
    "sucedido",
    "sucedida",
    "sucedidos",
    "sucedidas",
    "armado",
    "armada",
    "armados",
    "armadas",
    "action",
    "actions",
    "íris",
}

PRESERVAR_HIFEN_ESQ = {
    "arco",
    "bem",
    "mal",
    "não",
    "nao",
    "morto",
    "morta",
    "mortos",
    "mortas",
    "louva",
    "recém",
    "pré",
    "pós",
    "sub",
    "vice",
    "povo",
    "planta",
    "faca",
    "one",
    "two",
    "three",
    "free",
}


def slugify(texto: str) -> str:
    """Converte um título em identificador snake_case ASCII sem acentos."""
    normalizado = unicodedata.normalize("NFD", texto)
    sem_acentos = "".join(ch for ch in normalizado if unicodedata.category(ch) != "Mn")
    slug: list[str] = []
    anterior_sep = False
    for ch in sem_acentos.lower():
        if ch.isalnum():
            slug.append(ch)
            anterior_sep = False
        elif not anterior_sep:
            slug.append("_")
            anterior_sep = True
    return "".join(slug).strip("_")


def limpar_texto(texto: str) -> str:
    """Normaliza espaços, remove marcadores `\x08` e corrige ícones de ação quebrados."""
    limpo = texto.replace("\x08", " ").replace("\xa0", " ")
    limpo = re.sub(r"\[(one|two|three|free)-\s*(actions?|action)\]", r"[\1-\2]", limpo)
    limpo = re.sub(r"\[reaction\s*\]", "[reaction]", limpo)
    return re.sub(r"[ \t]+", " ", limpo).strip()


def formatar_traco(traco_bruto: str) -> str:
    """Converte traço em CAIXA ALTA do PDF para forma legível em português."""
    t = limpar_texto(traco_bruto).upper()
    if t in MAPA_TRACOS_CANONICOS:
        return MAPA_TRACOS_CANONICOS[t]
    if "-" in t:
        return "-".join(p.capitalize() for p in t.split("-"))
    return " ".join(p.capitalize() for p in t.split())


def deve_preservar_hifen(esquerda: str, direita: str) -> bool:
    """Decide se uma quebra de linha com `-` representa hífen lexical real."""
    esq_lower = esquerda.lower()
    dir_lower = direita.lower()
    if esq_lower in PRESERVAR_HIFEN_ESQ or dir_lower in PRESERVAR_HIFEN_DIR:
        return True
    return False


def concatenar_segmentos_linha(segmentos: list[str]) -> str:
    """Une linhas sequenciais respeitando hifenização em português."""
    acumulado = ""
    for seg in segmentos:
        s = limpar_texto(seg)
        if not s:
            continue
        if not acumulado:
            acumulado = s
            continue
        m_esq = re.search(r"([A-Za-zÀ-ÿ]+)-$", acumulado)
        m_dir = re.match(r"^([a-zà-ÿ]+)(.*)$", s)
        if m_esq and m_dir:
            palavra_esq = m_esq.group(1)
            palavra_dir = m_dir.group(1)
            if deve_preservar_hifen(palavra_esq, palavra_dir):
                acumulado = f"{acumulado}{s}"
            else:
                acumulado = f"{acumulado[:-1]}{s}"
        elif acumulado.endswith("[one-") and s.startswith("action]"):
            acumulado = f"{acumulado}{s}"
        else:
            acumulado = f"{acumulado} {s}"
    return limpar_texto(acumulado)


def dehifenizar_texto_corrido(texto: str) -> str:
    """Aplica de-hifenização em texto previamente unido com ou sem espaços após hífen."""
    texto = limpar_texto(texto)

    def _substituir(m: re.Match[str]) -> str:
        esq, esp, dir_ = m.group(1), m.group(2), m.group(3)
        if deve_preservar_hifen(esq, dir_):
            return f"{esq}-{dir_}" if esp else m.group(0)
        return f"{esq}{dir_}"

    return re.sub(r"\b([A-Za-zÀ-ÿ]+)-(\s*)([a-zà-ÿ]+)", _substituir, texto)


def traduzir_tokens_acao_pt(texto: str | None) -> str | None:
    """Converte marcadores de ícone do PDF em inglês para português canônico."""
    if not texto:
        return texto
    for en, pt in (
        ("[one-action]", "[1 ação]"),
        ("[two-actions]", "[2 ações]"),
        ("[three-actions]", "[3 ações]"),
        ("[free-action]", "[ação livre]"),
        ("[reaction]", "[reação]"),
    ):
        texto = texto.replace(en, pt)
    return texto


def coluna_x0_base(pagina_livro: int, col: int) -> float:
    """Retorna a margem esquerda padrão da coluna nas páginas de descrições (316–358)."""
    if pagina_livro % 2 == 0:
        return 76.5 if col == 1 else 315.0
    return 67.5 if col == 1 else 306.0


def deve_ignorar_regiao_quadro(pagina_livro: int, col: int, y0: float) -> bool:
    """Exclui exatamente os 3 quadros laterais presentes nas pp. 323, 334 e 338."""
    if pagina_livro == 323 and col == 2 and y0 < 380.0:
        return True
    if pagina_livro == 334 and col == 1 and y0 >= 575.0:
        return True
    if pagina_livro == 338 and col == 2 and y0 >= 575.0:
        return True
    return False


def construir_regras_gerais() -> dict[str, Any]:
    """Estrutura integralmente as regras do Capítulo 7 presentes nas páginas 297–306."""
    return {
        "paginas": "297-306",
        "introducao": (
            "Seja na forma de artefatos místicos, criaturas misteriosas ou magos tecendo magias estranhas, a magia traz "
            "fantasia e maravilha ao Pathfinder. Este capítulo explica como magias funcionam e como conjuradores preparam "
            "e conjuram suas magias.\n\n"
            "Com gestos e enunciações especiais, um conjurador pode invocar energias místicas, distorcer a mente, se proteger "
            "contra o perigo ou até mesmo criar algo do nada. Cada classe tem seu próprio método de aprendizado, preparação e "
            "conjuração de magias, e cada magia individual produz um efeito específico, portanto, aprender novas magias "
            "fornece a um conjurador uma matriz crescente de opções para atingir seus objetivos."
        ),
        "tradicao_e_escola": (
            "Os blocos fundamentais da magia são as tradições mágicas e as escolas de magia. As quatro tradições são arcana, "
            "divina, ocultista e primal. A tradição mágica de uma magia pode variar, pois muitas magias podem ser conjuradas "
            "utilizando tradições diferentes. Uma escola de magia, por outro lado, é intrínseca à magia e estabelece do que a "
            "magia é capaz. Por exemplo, magias de abjuração podem erguer proteções, magias de encantamento podem mudar "
            "pensamentos e magias de evocação podem criar explosões de fogo."
        ),
        "grimorios": {
            "titulo": "Grimórios",
            "pagina": 297,
            "descricao": (
                "Cuidadosamente mantidos e guardados com bastante ciúme, existem poucas coisas mais valiosas para um mago do que "
                "um grimório. Estes repositórios de conhecimento mágico frequentemente possuem armadilhas e proteções para garantir "
                "que ninguém bisbilhote seus segredos.\n\n"
                "Embora grimórios possuam uma função central na rotina diária de um mago, outras classes de conjuradores preparadores "
                "são conhecidas por usarem grimórios para registrar magias incomuns ou mesmo raras. Tais recursos permitem que um "
                "conjurador trate a magia como qualquer outra magia comum, desde que ele possa usar o livro como referência durante "
                "suas preparações diárias."
            ),
        },
        "escolas_magicas": [
            {
                "id": "abjuracao",
                "nome": "Abjuração",
                "abreviacao": "abj",
                "pagina": 297,
                "descricao": (
                    "Abjurações protegem e guarnecem. Elas criam barreiras que afastam ataques, efeitos ou até certos tipos de "
                    "criaturas. Elas também criam efeitos que prejudicam invasores ou banem intrusos."
                ),
            },
            {
                "id": "adivinhacao",
                "nome": "Adivinhação",
                "abreviacao": "adv",
                "pagina": 297,
                "descricao": (
                    "Adivinhações permitem que você aprenda os segredos do presente, passado e futuro. Elas fornecem boa sorte, "
                    "concedem a habilidade de perceber localidades remotas e revelam conhecimentos secretos.\n\n"
                    "Adivinhações geralmente possuem o traço detecção se encontrarem algo, o traço predição se fornecerem intuições "
                    "sobre o que pode ocorrer no futuro, o traço revelação se mostrarem as coisas como verdadeiramente são ou o "
                    "traço vidência se deixarem você perceber outro local."
                ),
            },
            {
                "id": "conjuracao",
                "nome": "Conjuração",
                "abreviacao": "con",
                "pagina": 297,
                "descricao": (
                    "Magias de conjuração transportam criaturas através de teleporte, criam um objeto ou trazem uma criatura ou "
                    "objeto de outro lugar (tipicamente outro plano) para seguir seus comandos.\n\n"
                    "Magias de conjuração frequentemente possuem o traço teleportação; e criaturas convocadas por magias de "
                    "conjuração possuem o traço convocado."
                ),
            },
            {
                "id": "encantamento",
                "nome": "Encantamento",
                "abreviacao": "enc",
                "pagina": 297,
                "descricao": (
                    "Encantamentos afetam as mentes e emoções de outras criaturas — às vezes para influenciá-los e controlá-los e "
                    "outras vezes para elevá-los a novos patamares de coragem. Magias de encantamento quase sempre possuem o traço "
                    "mental e muitas possuem os traços emoção ou medo."
                ),
            },
            {
                "id": "evocacao",
                "nome": "Evocação",
                "abreviacao": "evo",
                "pagina": 297,
                "descricao": (
                    "Evocações capturam energias mágicas e as moldam para ferir seus inimigos ou proteger seus aliados. Magias de "
                    "evocação frequentemente possuem um traço relacionado ao tipo de dano que causam, como ácido, eletricidade, fogo, "
                    "força, frio ou sônico."
                ),
            },
            {
                "id": "ilusao",
                "nome": "Ilusão",
                "abreviacao": "ilu",
                "pagina": 298,
                "descricao": (
                    "Ilusões criam a aparência de algo real, enganando os olhos, ouvidos e outros sentidos. Elas quase sempre possuem "
                    "o traço mental e, dependendo de como a ilusão é percebida, também podem ter os traços auditivo ou visual."
                ),
            },
            {
                "id": "necromancia",
                "nome": "Necromancia",
                "abreviacao": "nec",
                "pagina": 298,
                "descricao": (
                    "Magias de necromancia utilizam os poderes da vida e da morte. Elas podem esgotar a essência vital ou sustentar "
                    "criaturas com curas milagrosas. Magias de necromancia frequentemente possuem os traços cura, maldição, morte, "
                    "negativo ou positivo."
                ),
            },
            {
                "id": "transmutacao",
                "nome": "Transmutação",
                "abreviacao": "tra",
                "pagina": 298,
                "descricao": (
                    "Magias de transmutação fazem alterações ou transformam a forma física de uma criatura ou objeto. Os traços morfia "
                    "ou polimorfia aparecem principalmente em magias de transmutação."
                ),
            },
        ],
        "rolagens_ataque_e_cd_magia": {
            "titulo": "Rolagens de Ataque de Magia e CD de Magia",
            "pagina": 298,
            "formula_ataque_magia": (
                "Rolagens de ataque de magia = o modificador de seu atributo de conjuração + bônus de proficiência + outros "
                "bônus + penalidades"
            ),
            "formula_cd_magia": (
                "CD de magia = 10 + o modificador de seu atributo de conjuração + bônus de proficiência + outros bônus + "
                "penalidades"
            ),
            "descricao": (
                "Muitas magias permitem que as criaturas se defendam de seus efeitos utilizando CA ou uma jogada de salvamento. "
                "Duas estatísticas governam a potência das suas magias contra estas defesas: suas rolagens de ataque de magia e "
                "sua CD de magia. Quando as registrar em sua ficha de personagem, some apenas os valores que sempre se aplicam — "
                "normalmente apenas seu modificador de atributo e bônus de proficiência.\n\n"
                "Uma rolagem de ataque de magia é como qualquer outra rolagem de ataque, portanto, quaisquer bônus ou penalidades "
                "que se aplicam a todas suas rolagens de ataque devem ser incluídos no cálculo. Por exemplo, o +1 de bônus de "
                "estado da magia benção beneficiaria sua magia de raio assim como faria com uma flecha. Entretanto, note que a "
                "rolagem de ataque de magia não recebe bônus e penalidades que se apliquem especificamente a ataques desarmados ou "
                "com armas. A penalidade por ataques múltiplos se aplicam a magias de ataque, portanto, normalmente é uma má ideia "
                "conjurar uma magia que possui uma rolagem de ataque de magia se você já desferiu um ataque neste turno.\n\n"
                "Como em outros testes e CDs, bônus podem aumentar o resultado de sua rolagem de ataque de magia ou sua CD de "
                "magia; enquanto penalidades podem diminuir o resultado da sua rolagem de ataque de magia ou de sua CD de magia. "
                "Veja as páginas 444 e 445 no Capítulo 9: Regras do Jogo para mais informações sobre modificadores, bônus e penalidades."
            ),
        },
        "desacreditando_ilusoes": {
            "titulo": "Desacreditando Ilusões",
            "pagina": 298,
            "descricao": (
                "Algumas ilusões permitem que uma criatura afetada tenha uma chance de desacreditar a magia — o que permite à "
                "criatura efetivamente ignorar a magia se ela obtiver sucesso em fazê-lo. Isto normalmente ocorre quando a criatura "
                "Buscar ou de outra forma usar ações para interagir com a ilusão, comparando o resultado do teste de Percepção dela "
                "(ou outro teste ou jogada de salvamento, de acordo o MJ) à CD de magia do conjurador. Ilusões mentais tipicamente "
                "fornecem regras na descrição da magia para desacreditar o efeito (frequentemente permitindo que a criatura afetada "
                "tente um salvamento de Vontade).\n\n"
                "Se a ilusão é visual e a criatura interagir com a ilusão de forma que prove que ela não é o que parece, a criatura "
                "pode saber que uma ilusão está presente, mas ainda não é capaz de ignorar a ilusão sem obter sucesso em desacreditá-la. "
                "Por exemplo: se um personagem for empurrado através da ilusão de uma porta, ele saberá que aquela porta é uma ilusão, "
                "mas ainda não verá através dela. Desacreditar uma ilusão torna ela e as coisas bloqueadas por ela enevoadas e "
                "indistintas, portanto, mesmo nos casos em que uma ilusão visual é desacreditada, ela pode, ao critério do MJ, bloquear "
                "o suficiente da visão para deixar quem está do outro lado ocultado."
            ),
        },
        "espacos_de_magia": {
            "pagina": "298-299",
            "resumo": (
                "Personagens de classes conjuradoras podem conjurar uma determinada quantidade de magias por dia; as magias que você "
                "pode conjurar em um dia são chamadas de espaços de magia. No 1º nível, o personagem possui apenas uma pequena "
                "quantidade de espaços de magia de 1º nível por dia mas, conforme avança de nível, você ganha mais espaços de magia e "
                "novos espaços para magias de níveis mais elevados. O nível de uma magia indica o poder geral dela, variando do 1º ao "
                "10º nível de magia."
            ),
            "magias_preparadas": (
                "Se for um conjurador preparador — como clérigo, druida ou mago — você deve gastar um tempo todos os dias preparando "
                "magias para aquele dia. No começo de suas preparações diárias, você seleciona uma quantidade de magias de diferentes "
                "níveis de magia determinados por seu nível e classe. Suas magias continuam preparadas até que você as conjure ou até "
                "que prepare magias novamente.\n\n"
                "Cada magia preparada é gasta após uma única conjuração, portanto, se quiser conjurar uma magia em particular mais de "
                "uma vez por dia, você precisará prepará-la várias vezes. As exceções a esta regra são magias com o traço truque mágico; "
                "uma vez que tenha preparado um truque mágico, você pode conjurá-lo quantas vezes quiser até a próxima vez em que "
                "preparar magias. Veja a página 299 para mais informações sobre truques mágicos.\n\n"
                "Você pode ganhar uma habilidade que lhe permite trocar magias preparadas ou executar outros aspectos da preparação de "
                "magias em momentos diferentes ao longo do dia, mas apenas suas preparações diárias contam para o propósito de efeitos "
                "que duram até a próxima vez que você preparar magias."
            ),
            "magias_espontaneas": (
                "Se você for um conjurador espontâneo — como um bardo ou feiticeiro — você escolhe qual magia está usando naquele espaço "
                "no momento em que decidir conjurá-la. Isto lhe fornece mais liberdade em sua conjuração, mas você possui menos magias "
                "em seu repertório, conforme determinado por seu nível e classe. Quando faz suas preparações diárias, todos os seus "
                "espaços de magia são recarregados, mas você não muda as magias do seu repertório."
            ),
        },
        "tradicoes_magicas": {
            "pagina": 299,
            "resumo": (
                "Conjuradores conjuram magias de uma das quatro listas diferentes, cada uma representando uma tradição mágica distinta: "
                "arcana, divina, ocultista e primal.\n\n"
                "Sua classe determina qual tradição de magia suas magias utilizam. Em alguns casos, como quando um clérigo recebe magias "
                "de sua divindade ou quando um feiticeiro recebe magias de sua linhagem, você pode ser capaz de conjurar magias de uma "
                "lista de magias diferente. Nestes casos, a magia utiliza sua tradição mágica em vez da lista de magias normal para ela. "
                "Quando conjura a magia, você adiciona o traço da sua tradição à magia.\n\n"
                "Alguns tipos de magia, assim como a presente na maioria dos itens mágicos, não pertencem a uma única tradição. Elas "
                "possuem o traço mágico em vez de um traço de tradição."
            ),
            "tradicoes": [
                {
                    "id": "arcana",
                    "nome": "Arcana",
                    "pericia_identificacao": "Arcanismo",
                    "essencias": ["Matéria", "Mente"],
                    "conjuradores_iconicos": ["Mago", "Feiticeiro (linhagem arcana)"],
                    "descricao": (
                        "Conjuradores arcanos utilizam lógica e racionalidade para categorizar a magia inerente ao mundo ao seu redor. "
                        "Devido à sua abordagem extensa, a tradição arcana possui a lista de magias mais ampla, embora geralmente seja "
                        "ruim para afetar o espírito ou a alma. Magos são os mais icônicos conjuradores arcanos — debruçados sobre tomos e "
                        "grimórios — embora alguns feiticeiros arcanos estudem os segredos de seu sangue para destravar os seus poderes "
                        "interiores."
                    ),
                },
                {
                    "id": "divina",
                    "nome": "Divina",
                    "pericia_identificacao": "Religião",
                    "essencias": ["Espírito", "Vida"],
                    "conjuradores_iconicos": ["Clérigo", "Feiticeiro (linhagem divina)", "Campeão"],
                    "descricao": (
                        "O poder do divino é baseado na fé, no que não é visto e na crença em uma fonte de poder além do Plano Material. "
                        "Clérigos são os mais icônicos conjuradores divinos, suplicando aos deuses para que concedam a eles sua magia. "
                        "Feiticeiros divinos podem usar o sangue de seus ancestrais celestiais ou ínferos como conduítes divinos, e "
                        "campeões pedem a seus deuses que lhes concedam proeza marcial através da orientação divina."
                    ),
                },
                {
                    "id": "ocultista",
                    "nome": "Ocultista",
                    "pericia_identificacao": "Ocultismo",
                    "essencias": ["Espírito", "Mente"],
                    "conjuradores_iconicos": ["Bardo", "Feiticeiro (linhagem ocultista)"],
                    "descricao": (
                        "Os praticantes das tradições ocultistas buscam compreender o inexplicável, categorizar o bizarro e acessar o "
                        "efêmero de forma sistemática. Bardos são os mais icônicos conjuradores ocultistas, coletando esoterismos estranhos "
                        "e utilizando suas performances para influenciar a mente ou elevar a alma, enquanto feiticeiros ocultistas lutam "
                        "para compreender os poderes misteriosos em seu sangue."
                    ),
                },
                {
                    "id": "primal",
                    "nome": "Primal",
                    "pericia_identificacao": "Natureza",
                    "essencias": ["Matéria", "Vida"],
                    "conjuradores_iconicos": ["Druida", "Feiticeiro (linhagem primal)"],
                    "descricao": (
                        "Uma conexão instintiva e fé no mundo, o ciclo de dia e noite, a mudança das estações e a seleção natural de "
                        "predador e presa guiam a tradição primal. Druidas são os mais icônicos conjuradores primais, invocando a magia "
                        "da natureza através de uma fé profunda e conexão com as plantas e animais ao seu redor, enquanto feiticeiros "
                        "primais recorrem ao sangue de fadas ou feras para guiar as mesmas energias naturais."
                    ),
                },
            ],
        },
        "as_quatro_essencias": {
            "pagina": 300,
            "resumo": (
                "Magias que afetam certas forças físicas ou metafísicas tendem a ser agrupadas em tradições mágicas específicas. "
                "Estudiosos da magia majoritariamente concordam que toda a existência é composta da combinação de quatro essências, "
                "embora discordem dos nomes e qualidades particulares de cada essência.\n\n"
                "As colunas a seguir discutem cada essência e as tradições e escolas de magia relevantes para elas; por exemplo, "
                "magias de evocação tendem a manipular a matéria. A escola de abjuração é um caso incomum, pois magias de abjuração "
                "utilizam essências diferentes dependendo de quem estão guarnecendo ou do que estão protegendo."
            ),
            "essencias": [
                {
                    "id": "materia",
                    "nome": "Matéria",
                    "outros_nomes": ["corpo", "essência material", "essência física"],
                    "tradicoes_associadas": ["arcana", "primal"],
                    "escolas_frequentes": ["Conjuração", "Evocação", "Transmutação"],
                    "descricao": (
                        "Também chamada de corpo, essência material ou essência física, matéria é o bloco de construção fundamental que "
                        "forma todas as coisas físicas no universo. As tradições arcana e primal são especialmente sintonizadas com a "
                        "manipulação e moldagem da matéria. Magias que são utilizadas para criar ou alterar matéria mais frequentemente "
                        "pertencem às escolas de conjuração, evocação ou transmutação."
                    ),
                },
                {
                    "id": "espirito",
                    "nome": "Espírito",
                    "outros_nomes": ["alma", "essência etérea", "essência espiritual"],
                    "tradicoes_associadas": ["divina", "ocultista"],
                    "escolas_frequentes": ["Adivinhação", "Necromancia"],
                    "descricao": (
                        "Também chamada de alma, essência etérea ou essência espiritual, espírito é um bloco de construção extraterreno "
                        "que forma o eu imaterial e imortal do ser. O espírito viaja através do Plano Etéreo até o Grande Além após a "
                        "morte de seu corpo físico. O espírito é mais facilmente afetado por magias divinas e ocultistas. Magias de "
                        "espírito normalmente são das escolas de adivinhação ou necromancia."
                    ),
                },
                {
                    "id": "mente",
                    "nome": "Mente",
                    "outros_nomes": ["pensamento", "essência astral"],
                    "tradicoes_associadas": ["arcana", "ocultista"],
                    "escolas_frequentes": ["Adivinhação", "Encantamento", "Ilusão"],
                    "descricao": (
                        "Também chamada de pensamento ou essência astral, a essência da mente permite que criaturas tenham pensamentos "
                        "racionais, ideias, planos, lógica e memórias. A mente toca até mesmo seres irracionais como animais, mesmo que "
                        "de forma limitada. Conjuradores arcanos e ocultistas normalmente se destacam em magias da mente. Magias da "
                        "essência da mente normalmente são das escolas de adivinhação, encantamento e ilusão."
                    ),
                },
                {
                    "id": "vida",
                    "nome": "Vida",
                    "outros_nomes": ["coração", "fé", "instinto", "essência vital"],
                    "tradicoes_associadas": ["divina", "primal"],
                    "escolas_frequentes": ["Necromancia"],
                    "descricao": (
                        "Também chamada de coração, fé, instinto ou essência vital, a vida representa a força universal que anima todas "
                        "as coisas. Onde a matéria fornece os materiais básicos para o corpo, a vida o mantém vivo e bem. Esta essência "
                        "é responsável por respostas inconscientes e crenças, como instintos ancestrais e orientação divina. As tradições "
                        "divina e primal detêm poder sobre a vida. Magias de vida normalmente são de necromancia."
                    ),
                },
            ],
        },
        "magias_elevadas": {
            "pagina": 299,
            "regras": (
                "Tanto conjuradores preparadores quanto espontâneos podem conjurar uma magia em um nível mais alto do que o listado "
                "para aquela magia. Isto é chamado de elevar a magia. Um conjurador preparador pode elevar uma magia ao prepará-la em "
                "um espaço de nível mais alto do que o nível normal da magia, enquanto um conjurador espontâneo pode elevar uma magia ao "
                "conjurá-la usando um espaço de magia de nível mais alto, desde que conheça a magia naquele nível (veja Magias "
                "Espontâneas Elevadas, abaixo). Quando elevar sua magia, o nível da magia aumenta para igualar o nível superior do espaço "
                "de magia usado para prepará-la ou conjurá-la. Isto é útil para qualquer magia, pois alguns efeitos, como neutralização, "
                "dependem do nível da magia.\n\n"
                "Além disso, muitas magias possuem benefícios adicionais quando são elevadas, como dano aumentado. Estes benefícios "
                "extras são descritos ao final do bloco de estatísticas da magia. Algumas seções “elevadas” especificam um ou mais níveis "
                "no qual a magia deve ser preparada ou conjurada para receber estes benefícios extras. Cada uma destas seções “elevadas” "
                "indicam especificamente quais aspectos da magia mudam naquele nível. Leia a seção “elevada” somente para o nível de magia "
                "que você estiver usando ou preparando; se os benefícios dela incluírem quaisquer efeitos de uma seção de nível elevado "
                "mais baixo, esses benefícios serão incluídos na seção.\n\n"
                "Outras seções “elevadas” fornecem um número após um sinal de adição, indicando que a elevação concede vantagens extras "
                "com vários níveis. O efeito listado se aplica para cada nível de magia elevado acima de seu menor nível de magia, e o "
                "benefício é cumulativo. Por exemplo, bola de fogo diz “Elevada (+1) O dano aumenta em 2d6”. Como bola de fogo causa 6d6 "
                "de dano de fogo no 3º nível, uma bola de fogo de 4º nível causaria 8d6 de dano de fogo, sua versão de 5º nível causaria "
                "10d6 de dano de fogo e assim por diante."
            ),
            "magias_espontaneas_elevadas": (
                "Se for um conjurador espontâneo, você deve conhecer a magia no nível específico que deseja conjurá-la para poder "
                "elevá-la. Você pode adicionar uma magia ao seu repertório de magias em mais de um único nível para que tenha mais opções "
                "quando for conjurá-la. Por exemplo: se tiver adicionado bola de fogo ao seu repertório como uma magia de 3º nível e "
                "novamente como magia de 5º nível, você pode conjurá-la como uma magia de 3º nível ou como uma magia de 5º nível; contudo, "
                "você não poderia conjurá-la como uma magia de 4º nível.\n\n"
                "Muitas classes de conjuradores espontâneos fornecem habilidades como a característica de classe magias emblemáticas, que "
                "lhe permitem conjurar uma quantidade limitada de magias como versões elevadas mesmo que você conheça a magia apenas em "
                "um único nível."
            ),
        },
        "truques_magicos": {
            "pagina": "299-300",
            "descricao": (
                "Um truque mágico é um tipo especial de magia mais fraca do que outras magias, mas que pode ser usado com maior liberdade "
                "e flexibilidade. O título de um bloco de estatísticas de um truque mágico diz “Truque Mágico” em vez de “Magia.”\n\n"
                "Conjurar um truque mágico não usa seus espaços de magia; você pode conjurar um truque mágico à vontade, qualquer "
                "quantidade de vezes por dia. Se for um conjurador preparador, você possui uma quantidade de espaços de truques mágicos "
                "que usa para preparar seus truques mágicos. Você não pode preparar um truque mágico em qualquer outro espaço.\n\n"
                "Um truque mágico sempre é automaticamente elevado à metade de seu nível de personagem arredondada para cima. "
                "Para um conjurador típico, isto significa que o nível do truque mágico é igual ao nível do espaço de magia mais alto que "
                "você possui."
            ),
        },
        "magias_de_foco": {
            "pagina": "300, 302",
            "regras": (
                "Magias de foco são um tipo especial de magia obtida diretamente de um ramo de estudo, de uma divindade ou de outra "
                "fonte específica. Você pode aprender magias de foco apenas através de características ou talentos especiais de classe em "
                "vez de escolhê-las de uma lista de magia. Além disso, você pode conjurar magias de foco utilizando um reservatório especial "
                "de Pontos de Foco — você não prepara uma magia de foco em um espaço de magia ou usa seus espaços de magia para conjurar "
                "magias de foco; da mesma forma, você não pode gastar seus Pontos de Foco para conjurar magias que não sejam magias de foco. "
                "Mesmo algumas classes que normalmente não concedem conjuração, como campeão e monge, podem fornecer magias de foco.\n\n"
                "Magias de foco são automaticamente elevadas até a metade de seu nível arredondada para cima, assim como truques mágicos. "
                "Você não pode conjurar uma magia de foco se o nível mínimo dela for maior do que a metade de seu nível arredondada para "
                "cima, mesmo que obtenha acesso a ela de alguma forma.\n\n"
                "Conjurar qualquer uma de suas magias de foco custa 1 Ponto de Foco. Você automaticamente adquire uma reserva de foco de "
                "1 Ponto de Foco na primeira vez que ganhar uma habilidade que lhe fornecer uma magia de foco.\n\n"
                "Você recupera todos os Pontos de Foco em sua reserva de foco durante suas preparações diárias. Você também pode usar a "
                "atividade Refocar para orar, estudar, meditar ou de alguma outra forma ressintonizar-se com a fonte da sua magia de foco, "
                "recuperando um Ponto de Foco.\n\n"
                "Algumas habilidades lhe permitem aumentar os Pontos de Foco em sua reserva acima de 1. Tipicamente, isto ocorre através de "
                "talentos que lhe concedem uma nova magia de foco e aumentam a quantidade de pontos em sua reserva em 1. Sua reserva de foco "
                "nunca pode ter uma capacidade além de 3 Pontos de Foco, mesmo se selecionar talentos que aumentariam sua reserva acima "
                "deste valor."
            ),
            "refocar": {
                "nome": "Refocar",
                "tracos": ["Concentração", "Exploração"],
                "requerimentos": (
                    "Você possui uma reserva de foco e gastou pelo menos 1 Ponto de Foco desde a última vez que recuperou qualquer "
                    "Ponto de Foco."
                ),
                "descricao": (
                    "Você gasta 10 minutos executando algum feito para restaurar sua conexão mágica. Isto restaura 1 Ponto de Foco à sua "
                    "reserva de foco. Os feitos que você precisa executar são especificados na classe ou habilidade que lhe fornece suas "
                    "magias de foco. Estes feitos normalmente podem se acumular com outras tarefas relacionadas à fonte de suas magias. Por "
                    "exemplo: um clérigo com magias de foco de uma divindade normalmente pode Refocar enquanto cuida dos ferimentos de seus "
                    "aliados, e um mago da escola de ilusão pode ser capaz de Refocar enquanto tenta Identificar uma Magia da escola de "
                    "ilusão."
                ),
            },
            "pontos_de_foco_de_fontes_variadas": {
                "pagina": 302,
                "descricao": (
                    "É possível, especialmente através de arquétipos, receber magias de foco e Pontos de Foco de mais de uma fonte. Se "
                    "isto ocorrer, você possui apenas uma reserva de foco e soma todos os Pontos de Foco para determinar o tamanho total de "
                    "sua reserva. (Lembre-se que a quantidade máxima de Pontos de Foco que uma reserva pode ter é de 3 pontos.) Se possuir "
                    "várias habilidades que fornecem uma reserva de foco, cada uma adiciona 1 Ponto de Foco à sua reserva. Por exemplo, um "
                    "clérigo com o talento Iniciado no Domínio possui uma reserva com 1 Ponto de Foco. Digamos que você selecionou o arquétipo "
                    "de multiclasse de campeão e o talento Toque de Cura. Normalmente este talento lhe daria uma reserva de foco. Como você "
                    "já possui uma, em vez disso ele aumenta a capacidade de sua reserva existente em 1 ponto.\n\n"
                    "Pontos de Foco não são diferenciados por fonte; você pode gastar qualquer um de seus Pontos de Foco em qualquer uma de "
                    "suas magias de foco. Similarmente, quando Refoca, você recupera um ponto desde que siga as orientações de qualquer "
                    "habilidade que tenha lhe concedido magias de foco. Ter Pontos de Foco de várias fontes não muda a tradição de suas "
                    "magias; se possuir tanto magias de domínio de clérigo quanto magias de ordem druídica, suas magias de domínio continuam "
                    "sendo divinas e suas magias de ordem continuam sendo primais. Isto pode significar que você precisa registrar "
                    "proficiências e modificadores de atributo diferentes para CDs de magia e rolagens de ataque de magia de diferentes magias "
                    "de foco."
                ),
            },
            "conjuradores_com_magias_de_foco": (
                "Se for um conjurador, suas magias de foco são da mesma tradição de magia que a classe que lhe forneceu essas magias de "
                "foco. As magias de foco de um bardo são ocultistas, as de um clérigo são divinas, as de um druida são primais, as de um "
                "mago são arcanas e as de um feiticeiro são determinadas por sua linhagem."
            ),
            "nao_conjuradores_com_magias_de_foco": (
                "Se você recebe magias de foco de uma classe ou outra fonte que não concede habilidades de conjuração (como um monge com "
                "o talento Golpe de Ki), a habilidade que fornece magias de foco também fornece sua graduação de proficiência para ataques "
                "de magia e CDs de magia, assim como a tradição mágica de suas magias de foco. Você adquire a habilidade de Conjurar uma "
                "Magia e usar quaisquer ações de conjuração necessárias para conjurar suas magias de foco (veja abaixo). Entretanto, você "
                "não se qualifica para talentos e outras regras que requeiram que você seja um conjurador."
            ),
        },
        "outros_tracos_de_magia": {
            "pagina": 301,
            "resumo": (
                "Algumas magias e efeitos possuem traços como “mental” ou “bom”. Eles lhe dizem mais sobre a magia e como ela funciona, "
                "e outras regras podem fazer referência a eles. Uma criatura pode, por exemplo, sofrer –2 de penalidade de circunstância "
                "em jogadas de salvamento contra efeitos mentais. Abaixo é apresentado um glossário de alguns traços que possuem regras "
                "importantes."
            ),
            "tracos": [
                {
                    "id": "auditivo",
                    "nome": "Auditivo",
                    "descricao": (
                        "Magias auditivas dependem de som. Uma magia com o traço auditivo faz efeito apenas se o alvo puder ouvi-la. Isto é "
                        "diferente de um efeito sônico, que ainda afeta alvos que não podem ouvi-lo (como alvos surdos), desde que o efeito "
                        "faça som."
                    ),
                },
                {
                    "id": "convocado",
                    "nome": "Convocado",
                    "descricao": (
                        "Uma criatura convocada por uma magia ou efeito de conjuração adquire o traço convocado. Uma criatura convocada não "
                        "pode convocar outra criatura, criar coisas de valor ou conjurar magias que requerem um custo. Ela possui o traço "
                        "lacaio. Se ela tentar conjurar uma magia de nível igual ou maior do que a magia que a convocou, a magia falha e a "
                        "convocação termina. Fora isso, ela usa as habilidades padrão de uma criatura do tipo dela. Ela geralmente ataca seus "
                        "inimigos com o melhor das habilidades à disposição dela. Se puder se comunicar com a criatura, você pode tentar "
                        "comandá-la, mas o MJ determina até que ponto ela segue seus comandos.\n\n"
                        "Imediatamente quando você terminar de Conjurar a Magia, a criatura convocada usa as 2 ações dela para esse turno.\n\n"
                        "Criaturas convocadas podem ser banidas por várias magias e efeitos. Eles são automaticamente banidas se reduzidas "
                        "a 0 Pontos de Vida ou se a magia que as convocou terminar."
                    ),
                },
                {
                    "id": "escuridao_e_luz",
                    "nome": "Escuridão e Luz",
                    "descricao": (
                        "Efeitos com os traços escuridão e luz interagem de formas específicas. Luz não-mágica sempre brilha em escuridão "
                        "não-mágica e sempre perde o brilho em escuridão mágica. Luz mágica sempre brilha em escuridão não-mágica, mas brilha "
                        "em escuridão mágica apenas se a magia de luz possuir um nível maior que o nível do efeito de escuridão. Magias com o "
                        "traço escuridão ou luz sempre podem anular uma à outra, mas colocar luz e escuridão em contato não faz isso "
                        "automaticamente. Você normalmente deve conjurar uma magia de luz diretamente em um efeito de escuridão para neutralizá-lo "
                        "(e vice-versa), mas algumas magias tentam anular efeitos opostos automaticamente."
                    ),
                },
                {
                    "id": "incapacitacao",
                    "nome": "Incapacitação",
                    "descricao": (
                        "Uma habilidade com este traço pode deixar um personagem completamente fora da luta ou até mesmo matá-lo e é mais difícil "
                        "de usá-la em um personagem mais poderoso. Se uma magia possuir o traço incapacitação, qualquer criatura que possua um "
                        "nível maior que o dobro do nível da magia trata o resultado do teste dela para prevenir incapacitação como um grau de "
                        "sucesso melhor, ou o resultado de qualquer teste feito pelo conjurador para incapacitá-la como um grau de sucesso pior. "
                        "Se qualquer outro efeito possuir o traço incapacitação, uma criatura de nível maior do que o do item, criatura ou perigo "
                        "gerando o efeito recebe os mesmos benefícios."
                    ),
                },
                {
                    "id": "lacaio",
                    "nome": "Lacaio",
                    "descricao": (
                        "Lacaios são criaturas que servem diretamente a outras criaturas. Uma criatura com este traço pode usar somente 2 ações "
                        "por turno e não pode usar reações. Seus lacaios agem em seu turno de combate, uma vez por turno, quando você gastar uma "
                        "ação para emitir comandos. Para um companheiro animal, você Comanda um Animal; para um lacaio que seja um efeito de "
                        "item mágico ou magia, como um lacaio convocado, você Sustenta uma Magia ou Sustenta uma Ativação; e se não for "
                        "especificado de outra forma, você emite um comando verbal, que é uma ação única com os traços auditivo e concentração. "
                        "Se não receberem comandos, por padrão seus lacaios não usam nenhuma ação a não ser para se defenderem ou escaparem de "
                        "perigos óbvios. Se forem deixados sem atenção pelo menos por 1 minuto, lacaios acéfalos não agem, animais frequentemente "
                        "buscam o próprio conforto e lacaios inteligentes agem como quiserem."
                    ),
                },
                {
                    "id": "morfia",
                    "nome": "Morfia",
                    "descricao": (
                        "Magias que alteram levemente a forma de uma criatura possuem o traço morfia. Quaisquer Golpes especificamente "
                        "concedidos por um efeito de morfia são mágicos. Você pode ser afetado por múltiplos efeitos de morfia ao mesmo tempo, "
                        "mas se morfar a mesma parte do corpo mais de uma vez, o segundo efeito de morfia tenta neutralizar o primeiro (da mesma "
                        "maneira que dois efeitos de polimorfia, descrito abaixo).\n\n"
                        "Seus efeitos de morfia podem acabar se você estiver polimorfado e o efeito de polimorfia invalidar ou sobrepuser seu "
                        "efeito de morfia. Por exemplo, uma morfia que fornece asas seria dispensada se você polimorfar-se em uma forma que "
                        "possui asas próprias (embora, se a sua nova forma não possuísse asas, você manteria as asas de sua morfia). O MJ "
                        "determina quais efeitos de morfia podem ser utilizados em conjunto e quais não podem."
                    ),
                },
                {
                    "id": "polimorfia",
                    "nome": "Polimorfia",
                    "descricao": (
                        "Estes efeitos transformam o alvo em uma nova forma. Um alvo não pode estar sob o efeito de mais de um efeito de "
                        "polimorfia por vez. Se ficar sob o efeito de um segundo efeito de polimorfia, o segundo efeito de polimorfia tenta "
                        "neutralizar o primeiro. Se for bem-sucedido, ele surte efeito; se falhar, a magia não surte efeito no alvo. Quaisquer "
                        "Golpes especificamente concedidos por um efeito de polimorfia são mágicos. Exceto se especificado o contrário, magias "
                        "de polimorfia não permitem que o alvo assuma a aparência de um indivíduo específico, somente uma criatura genérica de um "
                        "tipo ou ancestralidade em geral.\n\n"
                        "Se assumir uma forma de batalha com uma magia de polimorfia, suas estatísticas especiais só podem ser ajustadas por "
                        "bônus de circunstância, bônus de estado e penalidades. Exceto se especificado o contrário, a forma de batalha impede "
                        "que você conjure magias, fale e use a maioria das ações de manuseio que requerem mãos. (Se houver dúvidas se você pode "
                        "usar uma ação, a decisão cabe ao MJ.) Seus equipamentos são absorvidos pela sua nova forma; as habilidades constantes de "
                        "seus equipamentos ainda funcionam, mas você não pode ativar quaisquer itens."
                    ),
                },
                {
                    "id": "visual",
                    "nome": "Visual",
                    "descricao": "Uma magia visual só pode afetar criaturas que possam vê-la.",
                },
            ],
        },
        "magias_inatas": {
            "pagina": 302,
            "atributo_padrao": "Carisma",
            "descricao": (
                "Certas magias são naturais ao seu personagem, tipicamente originando de sua ancestralidade ou de um item mágico em vez "
                "de sua classe. Você pode conjurar suas magias inatas mesmo se não for membro de uma classe conjuradora. A habilidade "
                "que lhe fornece uma magia inata diz o quão frequentemente você pode usá-la — normalmente uma vez por dia — e a tradição "
                "mágica dela. Magias inatas são recuperadas durante suas preparações diárias. Truques mágicos inatos são conjurados à "
                "vontade e automaticamente elevados como o normal para truques mágicos (veja Truques Mágicos na página 299), exceto se "
                "especificado o contrário.\n\n"
                "Você sempre é treinado em ataques de magia e CDs de magia para suas magias inatas, mesmo que não seja treinado em ataques "
                "de magia ou CDs de magia de qualquer outra forma. Se sua proficiência em ataques de magia ou CDs de magia for especialista "
                "ou melhor, aplique essa proficiência às suas magias inatas também. Você utiliza seu modificador de Carisma como modificador "
                "de atributo de conjuração para magias inatas exceto se especificado o contrário.\n\n"
                "Se possuir uma magia inata, você pode conjurá-la mesmo que ela não seja de um nível que normalmente possa conjurar. Isto é "
                "especialmente comum para monstros, que podem ser capazes de conjurar magias inatas muito além do que um personagem de mesmo "
                "nível poderia.\n\n"
                "Você não pode usar seus espaços de magia para conjurar suas magias inatas, mas pode ter uma magia inata e também ser "
                "capaz de preparar e conjurar a mesma magia através de sua classe. Você também não pode elevar magias inatas, mas algumas "
                "habilidades que concedem magias inatas podem fornecer uma magia de nível mais elevado do que seu nível base ou mudar o "
                "nível em que a magia é conjurada."
            ),
        },
        "conjurando_magias": {
            "pagina": "302-303",
            "resumo": (
                "A conjuração de uma magia pode variar de uma simples palavra de poder mágico que cria um efeito passageiro a uma conjuração "
                "complexa que demora minutos ou mesmo horas para produzir efeitos duradouros. Conjurar uma Magia é uma atividade especial "
                "que gasta uma quantidade de ações definida pela magia. Quando Conjura uma Magia, sua conjuração cria manifestações "
                "visuais óbvias ao reunir a magia, embora talentos como Magia Melodiosa (página 101) e Ocultar Magia (página 186) possam "
                "ajudar a esconder tais manifestações ou de alguma forma impedir observadores de notarem sua conjuração."
            ),
            "atividade_conjurar_uma_magia": {
                "nome": "Conjurar uma Magia",
                "descricao": (
                    "Você conjura uma magia que tenha preparada ou conste em seu repertório. Conjurar uma Magia é uma atividade especial "
                    "que gasta uma quantidade variável de ações dependendo da magia, conforme listado no bloco de estatísticas de cada "
                    "magia. Assim que as ações de conjuração são completadas, o efeito da magia ocorre.\n\n"
                    "Algumas magias são conjuradas como uma reação ou ação livre. Nesses casos, você Conjura uma Magia como uma reação "
                    "ou ação livre (conforme apropriado) em vez de uma atividade. Tais casos serão notados no bloco de estatísticas da "
                    "magia — por exemplo, “[reaction] verbal”."
                ),
            },
            "tempos_de_execucao_longos": (
                "Algumas magias demoram minutos ou horas para conjurar. As atividades Conjurar uma Magia destas magias incluem o conjunto "
                "dos componentes de magia listados, mas não é necessário estabelecer qual você está fornecendo em cada período. Você não "
                "pode usar outras ações ou reações enquanto conjurar uma magia dessas, mas a critério do MJ, você pode ser capaz de falar "
                "algumas poucas frases. Como com outras atividades que levam um longo período de tempo, estas magias possuem o traço "
                "exploração e você não pode conjurá-las durante um encontro. Se um combate irromper enquanto você estiver conjurando uma "
                "magia dessas, ela é interrompida (veja Magias Interrompidas e Perdidas na página 303)."
            ),
            "componentes_resumo": (
                "Cada magia lista os componentes necessários para conjurá-la depois do texto ou ícones de ação, como em “[three-actions] "
                "material, somático, verbal”. Os componentes de magia, descritos abaixo em detalhes, adicionam traços e requerimentos à "
                "atividade Conjurar uma Magia. Se não puder fornecer os componentes, você falha em Conjurar a Magia.\n"
                "• Foco (manuseio)\n"
                "• Material (manuseio)\n"
                "• Somático (manuseio)\n"
                "• Verbal (concentração)"
            ),
            "magias_interrompidas_e_perdidas": (
                "Algumas habilidades e magias podem interromper uma magia, fazendo com que ela não tenha efeito e seja perdida. Quando "
                "perde uma magia, você já gastou o espaço de magia, os custos e ações da magia e usou a atividade Conjurar uma Magia. Se "
                "uma magia for interrompida durante a ação Sustentar uma Magia, ela é encerrada imediatamente. As regras completas para "
                "interromper ações aparecem na página 463."
            ),
            "componentes_de_magia": [
                {
                    "id": "foco",
                    "nome": "Foco",
                    "traco_adicionado": "Manuseio",
                    "descricao": (
                        "Um foco é um objeto que canaliza a energia da magia. A magia adquire o traço manuseio e requer que você tenha uma "
                        "mão livre para pegar o foco listado na magia ou que você já esteja segurando o foco. Como parte de Conjurar uma "
                        "Magia, você pega o foco (se necessário), o manuseia e pode guardá-lo novamente se quiser.\n\n"
                        "Focos tendem a ser caros e você precisa adquiri-los antes para Conjurar a Magia."
                    ),
                },
                {
                    "id": "material",
                    "nome": "Material",
                    "traco_adicionado": "Manuseio",
                    "descricao": (
                        "Um componente material é um punhado de matéria física consumida na conjuração da magia. A magia adquire o traço "
                        "manuseio e requer que você tenha uma mão livre para pegar e manusear o componente material. Este componente é gasto "
                        "na conjuração (mesmo se a magia for interrompida).\n\n"
                        "Exceto em circunstâncias extremas, você pode assumir que todos os componentes comuns estão incluídos em uma bolsa "
                        "de componentes materiais (página 287)."
                    ),
                },
                {
                    "id": "somatico",
                    "nome": "Somático",
                    "traco_adicionado": "Manuseio",
                    "descricao": (
                        "Um componente somático é um movimento de mão específico ou um gesto que gera um nexo mágico. A magia adquire o "
                        "traço manuseio e requer que você faça gestos. Você pode usar este componente enquanto segura algo em sua mão, mas "
                        "não se estiver restrito ou de alguma forma incapaz de gesticular livremente.\n\n"
                        "Magias que requeiram que você toque o alvo requerem um componente somático. Você pode fazer isto enquanto segura "
                        "algo desde que parte de sua mão seja capaz de tocar o alvo (mesmo se através de uma luva ou manopla)."
                    ),
                },
                {
                    "id": "verbal",
                    "nome": "Verbal",
                    "traco_adicionado": "Concentração",
                    "descricao": (
                        "Um componente verbal é uma vocalização de palavras de poder. Você deve pronunciá-los com uma voz forte, o que torna "
                        "difícil ocultar que você está Conjurando uma Magia. A magia adquire o traço concentração. Você deve ser capaz de "
                        "falar para fornecer este componente."
                    ),
                },
            ],
            "substituicao_de_componentes": {
                "pagina": 303,
                "resumo": "Algumas classes podem substituir um componente por outro ou alterar como um componente funciona.",
                "classes": {
                    "bardo": (
                        "Se for um bardo Conjurando uma Magia da tradição ocultista, você pode tocar um instrumento musical para magias que "
                        "requeiram componentes somático ou material, desde que o instrumento ocupe ao menos uma de suas mãos para ser tocado. "
                        "Se usar um instrumento musical, você não precisa de uma bolsa de componentes de magia ou outra mão livre. Você "
                        "normalmente também pode tocar um instrumento para magias que requeiram componentes verbais em vez de falar."
                    ),
                    "clerigo": (
                        "Se for um clérigo Conjurando uma Magia da tradição divina enquanto segurar um foco divino (como um símbolo ou texto "
                        "religioso), você pode substituir qualquer componente material que a magia requeira usando o foco divino como "
                        "componente de foco no lugar dele. Diferente das regras normais para um componente de foco, você não pode pegar ou "
                        "guardar o foco quando fizer esta substituição."
                    ),
                    "druida": (
                        "Se for um druida Conjurando uma Magia da tradição primal enquanto segurar um foco primal (como azevinho e visco), "
                        "você pode substituir qualquer componente material que a magia requeira usando o foco primal como componente de foco "
                        "no lugar dele. Diferente das regras normais para um componente de foco, você não pode pegar ou guardar o foco quando "
                        "fizer esta substituição."
                    ),
                    "feiticeiro": (
                        "Se for um feiticeiro Conjurando uma Magia da tradição de sua linhagem, você pode usar a mágica em seu próprio sangue "
                        "para substituir qualquer componente material por um componente somático."
                    ),
                },
            },
        },
        "metamagia": {
            "titulo": "Metamagia",
            "pagina": 304,
            "descricao": (
                "Muitos conjuradores obtêm acesso a ações metamágicas, tipicamente ao selecionarem talentos metamágicos. Ações com o "
                "traço metamágico distorcem as propriedades de suas magias, alterando sua distância, dano ou quaisquer de suas outras "
                "propriedades. Você deve usar uma ação de metamagia imediatamente antes da magia que quer alterar. Se usar qualquer ação "
                "(incluindo ações livres, reações e ações metamágicas adicionais) diferentes de Conjurar a Magia diretamente depois, "
                "você desperdiça os benefícios da ação metamágica. Quaisquer efeitos adicionados por uma ação metamágica são parte do "
                "efeito da magia, não da ação metamágica em si."
            ),
        },
        "distancias_areas_e_alvos": {
            "pagina": 304,
            "resumo": (
                "Magias com um valor de distância podem afetar alvos, criar áreas ou fazer coisas aparecerem apenas dentro dessa distância. "
                "A maioria das distâncias de magias são medidas em metros, embora algumas possam se estender por quilômetros, alcançar "
                "qualquer lugar no planeta ou ir ainda mais longe!"
            ),
            "distancia_de_toque": (
                "Uma magia com distância de toque requer que você toque o alvo fisicamente. Você utiliza seu alcance desarmado para "
                "determinar se pode tocar a criatura. Você normalmente pode tocar o alvo automaticamente, embora a magia possa especificar "
                "que o alvo pode tentar uma jogada de salvamento ou que você deve fazer uma rolagem de ataque de magia. Se uma habilidade "
                "aumentar a distância de uma magia de toque, comece em 0 metros e aumente a partir desse valor."
            ),
            "areas": (
                "Às vezes uma magia possui uma área, que pode ser um cone, emanação, explosão ou linha. O método para medir estas áreas "
                "pode ser encontrado na página 456. Se a magia se originar da sua posição, ela possui apenas uma área; se você puder "
                "fazer a área da magia aparecer longe de você, a magia possui tanto uma distância quanto uma área."
            ),
            "alvos": (
                "Algumas magias permitem que você afete diretamente uma criatura, um objeto ou algo que se encaixe em uma categoria mais "
                "específica. O alvo deve estar dentro da distância da magia e você deve ser capaz de vê-lo (ou percebê-lo de outra forma "
                "com um sentido preciso) para afetá-lo normalmente. A critério do MJ, você pode tentar afetar uma criatura que não "
                "consiga ver, conforme descrito em Detectando Criaturas nas páginas 465 e 467. Se falhar em afetar uma criatura em "
                "particular, isto não muda como a magia afeta quaisquer outros alvos que possa ter.\n\n"
                "Se escolher um alvo inválido, como quando achar que um vampiro é uma criatura viva e o mirar com uma magia que afeta "
                "apenas criaturas vivas, sua magia não o afeta. Se a criatura começar como um alvo válido mas deixar de sê-lo ao longo da "
                "duração da magia, o efeito normalmente acaba, embora o MJ possa decidir o contrário em determinadas situações.\n\n"
                "Magias que afetam várias criaturas em uma área podem ter tanto uma seção de Área como uma de Alvos. Uma magia que "
                "possui uma área, mas não lista alvos, normalmente afeta todas as criaturas na área indiscriminadamente.\n\n"
                "Algumas magias afetam somente alvos voluntários. Um jogador pode declarar que o personagem dele é um alvo voluntário ou "
                "não a qualquer momento, independentemente da ordem no turno ou da condição desse personagem (como quando o personagem "
                "está paralisado, inconsciente ou até mesmo morto)."
            ),
            "linha_de_efeito": (
                "Você normalmente precisa de um caminho desobstruído para o alvo de uma magia, o ponto de origem de uma área ou o lugar "
                "onde irá criar algo com a magia. Mais informações sobre linha de efeito podem ser encontradas na página 457."
            ),
        },
        "duracoes": {
            "pagina": "304-305",
            "resumo": (
                "A duração de uma magia é o quanto o efeito dela dura. Magias que duram por mais que um instante possuem uma seção de "
                "Duração. Uma magia pode durar até o começo ou o final de um turno, por algumas rodadas, por minutos ou ainda mais tempo. "
                "Se a duração de uma magia for dada em rodadas, a quantidade de rodadas diminui em 1 no começo de cada turno do conjurador, "
                "terminando quando a duração chega a 0.\n\n"
                "Algumas magias possuem efeitos que continuam mesmo após a magia acabar. Qualquer efeito contínuo que não seja parte da "
                "seção duração da magia não é considerado mágico. Por exemplo, uma magia que cria um som alto e não possui duração pode "
                "ensurdecer alguém por um tempo, ou até mesmo permanentemente. Esta surdez não pode ser neutralizada porque não é magia "
                "em si (embora possa ser curada por outras magias, como restaurar sentidos).\n\n"
                "Se o conjurador morrer ou for incapacitado em algum momento da duração de uma magia, ela continua em efeito até que sua "
                "duração termine. Você pode precisar manter o controle da iniciativa do conjurador depois de sua incapacitação para "
                "monitorar durações das magias conjuradas por ele."
            ),
            "sustentando_magias": (
                "Se a duração da magia for “sustentada”, ela dura até o final de seu próximo turno a menos que você use a ação Sustentar "
                "uma Magia naquele turno para prolongar a duração dessa magia."
            ),
            "acao_sustentar_uma_magia": {
                "nome": "Sustentar uma Magia",
                "acoes": "1",
                "tracos": ["Concentração"],
                "requerimentos": "Você possui pelo menos uma magia ativa com duração sustentada e não está fatigado.",
                "descricao": (
                    "Escolha uma magia com uma duração sustentada que você tenha em vigor. A duração dessa magia continua até o final de "
                    "seu próximo turno. Algumas magias podem possuir efeitos levemente diferentes ou expandidos se você sustentá-las. "
                    "Sustentar uma Magia por mais de 10 minutos (100 rodadas) encerra a magia e o deixa fatigado a menos que a magia liste "
                    "uma duração máxima diferente (como “sustentada por até 1 minuto” ou “sustentada por até 1 hora”).\n\n"
                    "Se sua ação Sustentar uma Magia for interrompida, a magia acaba imediatamente."
                ),
            },
            "duracoes_longas": (
                "Se a duração de uma magia disser que ela dura até suas próximas preparações diárias, no próximo dia você pode recusar-se a "
                "preparar uma nova magia naquele espaço. (Se você for um conjurador espontâneo, você pode gastar um espaço de magia durante "
                "suas preparações.) Fazer isto prolonga a duração da magia até suas próximas preparações diárias. Isto efetivamente "
                "Sustenta a Magia por um longo período de tempo. Se preparar uma magia nova no espaço (ou não gastar o espaço de magia), a "
                "magia acaba. Você não pode fazer isso se a magia não se originar de um de seus espaços de magia. Se estiver morto ou de "
                "alguma forma incapacitado ao se completarem as 24 horas após o período em que Conjurou a Magia ou da última vez que "
                "prolongou a duração dela, a magia acaba. Magias com duração ilimitada duram até que sejam neutralizadas ou Dispensadas. "
                "Você não precisa manter um espaço de magia aberto para estas magias."
            ),
            "dispensando_magias": (
                "Algumas magias podem ser dispensadas, encerrando a duração delas mais cedo. Isto requer que o conjurador ou o alvo use a "
                "ação Dispensar."
            ),
            "acao_dispensar": {
                "nome": "Dispensar",
                "acoes": "1",
                "tracos": ["Concentração"],
                "descricao": (
                    "Você encerra o efeito de uma magia ou item mágico. Ele deve ser um efeito que você possa dispensar, conforme definido "
                    "pela magia ou item. Dispensar pode encerrar inteiramente o efeito ou encerrá-lo apenas para determinado alvo ou alvos, "
                    "dependendo da magia ou item."
                ),
            },
        },
        "jogadas_de_salvamento": {
            "pagina": 305,
            "resumo": (
                "Magias que requeiram que o alvo faça uma jogada de salvamento para resistir a parte ou todo o efeito da magia possuem a "
                "seção Salvamento. Esta seção apresenta o tipo de salvamento para referência rápida e detalhes específicos aparecem na "
                "descrição da magia. Sempre que uma magia permitir uma jogada de salvamento, ela utiliza a CD de magia do conjurador."
            ),
            "jogadas_de_salvamento_basicas": {
                "resumo": (
                    "Se a seção Salvamento de uma magia especificar um salvamento “básico”, todos os efeitos potenciais da magia são "
                    "relacionados ao dano listado na descrição da magia. As regras para jogadas de salvamento básicas são encontradas na "
                    "página 449."
                ),
                "sucesso_critico": "O alvo não sofre dano.",
                "sucesso": "O alvo sofre metade do dano.",
                "falha": "O alvo sofre o dano inteiro.",
                "falha_critica": "O alvo sofre o dobro do dano.",
            },
        },
        "ataques_de_magia": {
            "pagina": 305,
            "descricao": (
                "Algumas magias requerem que você tenha sucesso em uma rolagem de ataque de magia para afetar o alvo. Normalmente isto "
                "ocorre porque você precisa mirar precisamente um raio ou de alguma forma fazer um ataque preciso. Uma rolagem de ataque de "
                "magia é comparada à CA do alvo. Rolagens de ataque de magia se beneficiam de quaisquer bônus ou penalidades em rolagens de "
                "ataque, incluindo sua penalidade por ataques múltiplos, mas não quaisquer benefícios ou penalidades especiais que se aplicam "
                "apenas a ataques desarmados ou com armas. Ataques de magia não causam qualquer dano além do listado na descrição da magia.\n\n"
                "Em casos raros, uma magia pode fazer com que você desfira algum outro tipo de ataque, como um Golpe com arma. Esses ataques "
                "usam as regras e bônus de ataque normais para esse tipo de ataque."
            ),
        },
        "identificando_magias": {
            "pagina": 305,
            "descricao": (
                "Às vezes você precisa identificar uma magia, especialmente se os efeitos dela não forem prontamente óbvios. Se notar uma "
                "magia sendo conjurada e a tiver preparada ou em seu repertório, você automaticamente sabe qual magia ela é, incluindo o "
                "nível para o qual foi elevada.\n\n"
                "Se quiser identificar uma magia, mas não a tiver preparada ou em seu repertório, você deve gastar uma ação no seu turno "
                "para tentar identificá-la usando Recordar Conhecimento. Você tipicamente nota uma magia sendo conjurada ao ver as "
                "manifestações visuais ou ouvir os componentes verbais dela durante a conjuração. Identificar magias duradouras que já "
                "estão exercendo efeito requer o uso de Identificar Magia em vez de Recordar Conhecimento porque você não possui a vantagem "
                "de observar a magia sendo conjurada."
            ),
        },
        "neutralizando_magias": {
            "pagina": 305,
            "descricao": (
                "Algumas magias, como dissipar magia, podem ser usadas para eliminar os efeitos de outras magias. Pelo menos uma criatura, "
                "objeto ou manifestação da magia que você estiver tentando neutralizar deve estar dentro da distância da magia usada para a "
                "neutralização. Você faz um teste de neutralização (página 459) utilizando o modificador de seu atributo de conjuração e "
                "seu bônus de proficiência em rolagens de ataque de magia."
            ),
        },
        "acoes_hostis": {
            "pagina": 305,
            "descricao": (
                "Alguns efeitos de magia impedem o alvo de usar ações hostis; ou então a magia acaba se uma criatura usar quaisquer ações "
                "hostis. Uma ação hostil é uma ação que pode prejudicar ou causar dano a outra criatura, seja direta ou indiretamente, mas "
                "não uma ação que a criatura não saiba que poderia ser prejudicial. Por exemplo: lançar uma bola de fogo em uma multidão "
                "seria uma ação hostil, mas abrir uma porta e acidentalmente libertar um monstro horrível não seria. O MJ é o árbitro "
                "final do que constitui uma ação hostil."
            ),
        },
        "determinando_acionamentos": {
            "pagina": "305-306",
            "descricao": (
                "Se uma magia for feita para responder somente a determinados eventos ou sob determinadas condições — como a magia boca mágica "
                "— ela pode requerer que você determine um acionamento. Isto é uma simples sugestão sensorial que faz a magia ser ativada. "
                "A magia é ativada como uma reação quando o sensor da magia observar algo que atende ao acionamento dela. Dependendo da "
                "magia, o acionamento pode ser a presença de um tipo de criatura, como uma “mulher anã ruiva”, ou pode ser uma ação "
                "observada como “sempre que alguém entrar na área da magia”.\n\n"
                "Disfarces e ilusões enganam a magia desde que pareçam atender seus parâmetros. Para uma magia detectar algo visualmente, "
                "o ponto de origem da magia deve possuir linha de visão. Escuridão não impede isto, mas invisibilidade sim, assim como um "
                "teste de Furtividade bem-sucedido para se Esconder (contra a CD da magia). Para detecção auditiva, linha de visão não é "
                "necessária, embora o som deva ser audível no ponto de origem da magia. Um teste de Furtividade para se Esgueirar pode "
                "enganar o sensor."
            ),
        },
        "muralhas": {
            "pagina": 306,
            "descricao": (
                "Magias que criam paredes listam espessura, comprimento e altura da muralha, assim como a forma em que podem ser "
                "posicionadas. Algumas muralhas podem ser moldadas; você pode manipular uma muralha em formas diferentes de uma linha reta, "
                "escolhendo seu caminho contínuo quadrado por quadrado. O caminho de uma muralha moldada não pode atravessar o mesmo "
                "espaço mais de uma vez, mas pode retornar de forma que uma seção esteja adjacente a outra."
            ),
        },
        "lendo_magias": {
            "pagina": 306,
            "resumo": (
                "Todas as magias utilizam o formato a seguir. Seções aparecem somente quando aplicáveis, então nem todas as magias possuem "
                "cada seção descrita aqui. A linha do nome da magia também lista o tipo da magia — se é um truque mágico ou uma magia de "
                "foco — assim como o seu nível."
            ),
            "secoes": {
                "tradicoes": (
                    "Esta seção lista as tradições mágicas às quais a magia pertence. Alguns talentos e outras habilidades podem adicionar "
                    "uma magia à sua lista de magias mesmo que você não siga as tradições listadas."
                ),
                "execucao": (
                    "A quantidade de ações requeridas para Conjurar a Magia é listada aqui. Magias que podem ser conjuradas durante um único "
                    "turno possuem o ícone apropriado, assim como as que podem ser conjuradas como uma ação livre ou reação. Magias que demoram "
                    "mais para serem conjuradas listam o tempo necessário, como “1 minuto”. Depois disto, são listados os componentes da magia. "
                    "Se Conjurar a Magia exigir um custo, requerimentos ou acionamento, esta informação também é listada nesta seção. Um custo "
                    "inclui quaisquer valores em dinheiro, materiais valiosos e outros recursos que devem ser gastos para conjurar a magia."
                ),
                "distancia_area_alvos": (
                    "Esta seção lista a distância da magia, a área que ela afeta e os alvos que pode afetar (se houver). Se nenhuma destas "
                    "seções estiver presente, a magia afeta apenas o conjurador."
                ),
                "salvamento_e_duracao": (
                    "Se a magia permitir que o alvo faça uma jogada de salvamento, o tipo de salvamento aparece aqui. Quaisquer detalhes sobre "
                    "os resultados e efeitos particulares do salvamento aparecem no texto a menos que a seção especifique uma jogada de "
                    "salvamento básica, que segue as regras encontradas na página 449. Se a magia requerer um salvamento apenas sob "
                    "determinadas circunstâncias ou em um determinado momento, esta seção é omitida, já que o texto precisa explicar em mais "
                    "detalhes. Uma magia que não listar uma duração ocorre instantaneamente e qualquer coisa criada por ela persiste após a magia.\n\n"
                    "Uma linha horizontal segue o salvamento e a duração, e os efeitos da magia são descritos após esta linha. Esta seção também "
                    "pode detalhar os possíveis resultados de uma jogada de salvamento: sucesso crítico, sucesso, falha e falha crítica."
                ),
                "elevada": "Se a magia puder ser elevada, os efeitos de elevá-la aparecem ao final do bloco de estatísticas.",
            },
        },
    }


def construir_quadros_auxiliares() -> list[dict[str, Any]]:
    """Retorna os 3 quadros auxiliares embutidos nas páginas das descrições (pp. 323, 334, 338)."""
    return [
        {
            "id": "magia_e_moralidade",
            "titulo": "Magia e Moralidade",
            "pagina": 323,
            "magia_relacionada": None,
            "descricao": (
                "Embora a magia permita realizar atos maravilhosos no jogo, ela pode ser usada para propósitos terríveis. Embora algumas "
                "magias sejam obviamente vis ou possuam o traço maligno e conexão direta ao profano, outras podem ser usadas para o bem ou "
                "para o mal. Usar magia não o liberta da moralidade do resultado.\n\n"
                "Em nenhuma situação isto é mais verdade do que com magias de encantamento, especialmente aquelas usadas para compelir uma "
                "criatura a fazer algo. Estas magias podem remover o poder de escolha de um personagem e ser muito facilmente usadas de forma "
                "maligna. Dominar um ogro e forçá-lo a abandonar seu posto de guarda não é necessariamente maligno, mas usar a mesma magia "
                "para forçar um mercador a dar toda sua mercadoria certamente é. Usar uma magia para um propósito maligno pode fazer a "
                "tendência de um personagem jogador mudar para mau, com o julgamento final se o jogador está ou não usando uma magia para "
                "um propósito maligno ficando a cargo do MJ.\n\n"
                "Independentemente dos efeitos em jogo, todos os jogadores devem ter cautela com essas magias. Estes efeitos podem afetar "
                "negativamente pessoas à mesa, já que podem criar situações que encenem experiências verdadeiramente ruins que jogadores "
                "tenham tido, criando ambientes desconfortáveis e hostis. Jogadores e MJs devem trabalhar para impedir estas situações para "
                "que todos possam se focar e divertir-se à mesa."
            ),
        },
        {
            "id": "aura_de_tendencia",
            "titulo": "Aura de Tendência",
            "pagina": 334,
            "magia_relacionada": "detectar_tendencia",
            "descricao": (
                "A força de uma aura de tendência depende do nível da criatura, item ou magia. As auras de mortos-vivos, clérigos e outros "
                "conjuradores divinos com uma divindade patrona e de criaturas da Esfera Externa são um passo mais forte do que o normal "
                "(tênue em vez de nenhuma, por exemplo)."
            ),
            "tabela": [
                {"nivel_criatura_ou_item": "0–5", "nivel_magia_ou_efeito": "—", "forca_aura": "Nenhuma"},
                {"nivel_criatura_ou_item": "6–10", "nivel_magia_ou_efeito": "0–3", "forca_aura": "Tênue"},
                {"nivel_criatura_ou_item": "11–15", "nivel_magia_ou_efeito": "4–7", "forca_aura": "Moderada"},
                {"nivel_criatura_ou_item": "16–20", "nivel_magia_ou_efeito": "8–9", "forca_aura": "Poderosa"},
                {"nivel_criatura_ou_item": "21+", "nivel_magia_ou_efeito": "10", "forca_aura": "Avassaladora"},
            ],
        },
        {
            "id": "acoes_de_escudo",
            "titulo": "Ações de Escudo",
            "pagina": 338,
            "magia_relacionada": "escudo_mistico",
            "descricao": (
                "A magia escudo místico funciona como um escudo erguido e também lhe concede a habilidade de usar a reação Bloqueio com Escudo."
            ),
            "acao": {
                "nome": "Bloqueio com Escudo",
                "acoes": "reacao",
                "acionamento": "Enquanto estiver com seu escudo erguido, você sofreria dano de um ataque físico.",
                "descricao": (
                    "Você posiciona seu escudo na frente de um golpe para bloqueá-lo. Seu escudo o impede de sofrer uma quantidade de dano "
                    "igual à dureza do escudo. Tanto você quanto o escudo sofrem o dano remanescente (ambos sofrem o mesmo dano), o que "
                    "pode quebrar ou até mesmo destruir o escudo."
                ),
            },
        },
    ]


def _extrair_entrada_lista(buf_spans: list[dict[str, Any]], pagina_livro: int) -> dict[str, Any]:
    """Converte o buffer de spans de uma linha de Lista de Magias em registro estruturado."""
    # Localiza onde termina a parte em negrito com "(abj|...):"
    indice_corte: int | None = None
    pos_colon_no_span: int | None = None
    acumulado_bold = ""
    for i, sp in enumerate(buf_spans):
        t = sp["text"].replace("\x08", " ")
        acumulado_bold += t
        if "Bold" in sp.get("font", "") and ":" in t:
            antes_colon = acumulado_bold.rsplit(":", 1)[0]
            if re.search(r"\([a-z]{3}\)\s*$", antes_colon.strip()):
                indice_corte = i
                pos_colon_no_span = t.rfind(":")
                break

    if indice_corte is None or pos_colon_no_span is None:
        bruto = "".join(s["text"] for s in buf_spans)
        raise ValueError(f"Entrada inválida na Lista de Magias (p.{pagina_livro}): {bruto!r}")

    nome_partes: list[str] = []
    sup_partes: list[str] = []
    resumo_partes: list[str] = []

    for i, sp in enumerate(buf_spans):
        t = sp["text"].replace("\x08", " ")
        eh_sobrescrito = sp.get("size", 8.5) < 6.5
        if i < indice_corte:
            (sup_partes if eh_sobrescrito else nome_partes).append(t)
        elif i == indice_corte:
            antes = t[:pos_colon_no_span]
            depois = t[pos_colon_no_span + 1 :]
            (sup_partes if eh_sobrescrito else nome_partes).append(antes)
            resumo_partes.append(depois)
        else:
            resumo_partes.append(t)

    cabecalho_nome = limpar_texto("".join(nome_partes))
    sobrescrito = limpar_texto("".join(sup_partes))
    resumo = dehifenizar_texto_corrido("".join(resumo_partes))

    m = re.match(r"^(.+?)\s*\(([a-z]{3})\)$", cabecalho_nome)
    if not m:
        raise ValueError(f"Cabeçalho sem escola na lista (p.{pagina_livro}): {cabecalho_nome!r}")

    nome = m.group(1).strip()
    escola_abrev = m.group(2)
    raridade = "raro" if "R" in sobrescrito else ("incomum" if "I" in sobrescrito else "comum")
    elevavel = "E" in sobrescrito

    return {
        "id": slugify(nome),
        "nome": nome,
        "escola_abreviacao": escola_abrev,
        "escola": ESCOLAS_ABREV.get(escola_abrev, escola_abrev),
        "raridade": raridade,
        "elevavel": elevavel,
        "sobrescrito_original": sobrescrito if sobrescrito else None,
        "resumo": resumo,
        "pagina_lista": pagina_livro,
    }


def extrair_listas_de_magias(doc: pymupdf.Document) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Extrai integralmente as 4 Listas de Magias das páginas 307–315 (índices 10–18)."""
    por_tradicao: dict[str, dict[str, list[dict[str, Any]]]] = {
        trad: {} for trad in ("arcana", "divina", "ocultista", "primal")
    }
    estado: dict[str, Any] = {"tradicao": None, "nivel_chave": None, "nivel_num": None}

    def _flush(buf: list[dict[str, Any]], bp: int) -> None:
        if not buf or estado["tradicao"] is None or estado["nivel_chave"] is None:
            buf.clear()
            return
        entrada = _extrair_entrada_lista(buf, bp)
        trad = estado["tradicao"]
        nk = estado["nivel_chave"]
        por_tradicao[trad].setdefault(nk, []).append(entrada)
        buf.clear()

    for idx in range(10, 19):
        bp = idx + DESLOCAMENTO_PAGINA_LIVRO
        d = doc[idx].get_text("dict")
        cols: dict[int, list[tuple[float, float, list[dict[str, Any]]]]] = {1: [], 2: [], 3: []}
        for b in d["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                x0, y0, _x1, _y1 = l["bbox"]
                if y0 < 50.0 or y0 > 745.0 or x0 > 530.0 or x0 < 50.0:
                    continue
                col = 1 if x0 < 205.0 else (2 if x0 < 365.0 else 3)
                cols[col].append((y0, x0, l["spans"]))

        for col in (1, 2, 3):
            linhas = sorted(cols[col], key=lambda r: (r[0], r[1]))
            mescladas: list[list[Any]] = []
            for y0, x0, spans in linhas:
                if mescladas and abs(mescladas[-1][0] - y0) < 2.5:
                    mescladas[-1][2].extend(spans)
                    mescladas[-1][2].sort(key=lambda s: s["bbox"][0])
                else:
                    mescladas.append([y0, x0, list(spans)])

            buf: list[dict[str, Any]] = []
            for _y0, _x0, spans in mescladas:
                txt = limpar_texto("".join(s["text"] for s in spans))
                if not txt:
                    continue
                primeiro = next((s for s in spans if s["text"].strip()), None)
                if primeiro is None or primeiro["font"] in ("Taroca", "SabonLTStd-Roman"):
                    continue
                if primeiro["font"] == "Gin-Regular":
                    _flush(buf, bp)
                    estado["tradicao"] = TRADICOES_CABECALHO[txt]
                    estado["nivel_chave"] = None
                    estado["nivel_num"] = None
                    continue
                if primeiro["font"] == "Gin-Regular-SC700":
                    _flush(buf, bp)
                    if "Truques" in txt:
                        estado["nivel_num"] = 0
                        estado["nivel_chave"] = "truques_magicos"
                    else:
                        m = re.search(r"(\d+)º", txt)
                        assert m is not None, f"Cabeçalho de nível inesperado (p.{bp}): {txt!r}"
                        nivel_int = int(m.group(1))
                        estado["nivel_num"] = nivel_int
                        estado["nivel_chave"] = str(nivel_int)
                    continue

                buf_txt = "".join(s["text"] for s in buf)
                entrada_completa = bool(re.search(r"\([a-z]{3}\)\s*:", buf_txt))
                if primeiro["font"] == "GoodOT-Bold" and (not buf or entrada_completa):
                    _flush(buf, bp)
                    buf.extend(spans)
                else:
                    if buf and not buf[-1]["text"].endswith((" ", "-")):
                        buf.append({"text": " ", "font": "GoodOT", "size": 8.5, "bbox": [0, 0, 0, 0]})
                    buf.extend(spans)
            _flush(buf, bp)

    indice_unico: dict[str, dict[str, Any]] = {}
    totais_por_tradicao: dict[str, int] = {}
    for trad, niveis in por_tradicao.items():
        totais_por_tradicao[trad] = sum(len(lista) for lista in niveis.values())
        for nk, lista in niveis.items():
            nivel_int = 0 if nk == "truques_magicos" else int(nk)
            for it in lista:
                sid = it["id"]
                if sid not in indice_unico:
                    indice_unico[sid] = {
                        "id": sid,
                        "nome": it["nome"],
                        "nivel": nivel_int,
                        "escola": it["escola"],
                        "raridade": it["raridade"],
                        "elevavel": it["elevavel"],
                        "tradicoes": set(),
                        "resumos": set(),
                    }
                indice_unico[sid]["tradicoes"].add(trad)
                indice_unico[sid]["resumos"].add(it["resumo"])

    estrutura_listas = {
        "paginas": "307-315",
        "observacoes": (
            "Estas listas incluem as magias para cada tradição, incluindo truques mágicos. (Magias de foco aparecem nas páginas "
            "386 a 407.) Um “E” sobrescrito indica uma magia que possui efeitos extras quando é elevada, e uma magia cuja "
            "raridade seja maior do que comum possui a primeira letra de sua raridade sobrescrita. Uma abreviação entre parênteses "
            "indica a escola da magia."
        ),
        "totais_por_tradicao": totais_por_tradicao,
        "total_entradas": sum(totais_por_tradicao.values()),
        "total_magias_unicas": len(indice_unico),
        "por_tradicao": por_tradicao,
    }
    return estrutura_listas, indice_unico


def _parsear_metadados_magia(linhas_meta: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]]) -> dict[str, Any]:
    """Extrai campos estruturados dos metadados da magia a partir dos rótulos em negrito."""
    tokens_sequenciais: list[tuple[bool, str]] = []
    for _bp, _col, _x0, _y0, _x1, _y1, spans in linhas_meta:
        linha_str_parts: list[tuple[bool, str]] = []
        for sp in spans:
            txt = sp["text"].replace("\x08", " ")
            eh_rotulo = sp.get("font") == "GoodOT-Bold" and txt.strip().rstrip(":") in ROTULOS_METADADOS
            if eh_rotulo:
                linha_str_parts.append((True, txt.strip().rstrip(":")))
            else:
                linha_str_parts.append((False, txt))
        if tokens_sequenciais and not tokens_sequenciais[-1][0]:
            # Respeita hifenização quando o valor anterior quebra no fim da linha
            prox_texto = "".join(p[1] for p in linha_str_parts).lstrip()
            prev_texto = tokens_sequenciais[-1][1]
            m_esq = re.search(r"([A-Za-zÀ-ÿ]+)-$", prev_texto.rstrip())
            m_dir = re.match(r"^([a-zà-ÿ]+)", prox_texto)
            if m_esq and m_dir:
                if deve_preservar_hifen(m_esq.group(1), m_dir.group(1)):
                    tokens_sequenciais[-1] = (False, prev_texto.rstrip())
                else:
                    tokens_sequenciais[-1] = (False, prev_texto.rstrip()[:-1])
            else:
                tokens_sequenciais[-1] = (False, prev_texto + " ")
        tokens_sequenciais.extend(linha_str_parts)

    campos_brutos: dict[str, str] = {}
    rotulo_atual: str | None = None
    buf_val: list[str] = []
    for eh_rot, val in tokens_sequenciais:
        if eh_rot:
            if rotulo_atual is not None:
                campos_brutos[rotulo_atual] = limpar_texto("".join(buf_val)).rstrip(";").strip()
            rotulo_atual = val
            buf_val = []
        else:
            if rotulo_atual is not None:
                buf_val.append(val)
    if rotulo_atual is not None:
        campos_brutos[rotulo_atual] = limpar_texto("".join(buf_val)).rstrip(";").strip()

    tradicoes = sorted(
        {limpar_texto(t).lower() for t in campos_brutos.get("Tradições", "").split(",") if limpar_texto(t)}
    )
    execucao = limpar_texto(campos_brutos.get("Execução", ""))
    acoes = _extrair_acoes_execucao(execucao)
    componentes = _extrair_componentes_execucao(execucao)

    area = campos_brutos.get("Área")
    alvos = campos_brutos.get("Alvos") or campos_brutos.get("Alvo")
    if area and alvos and area.endswith(" ou"):
        area = f"{area[:-3].strip()} (ou Alvos)"

    return {
        "tradicoes": tradicoes,
        "execucao": execucao,
        "acoes": acoes,
        "componentes": componentes,
        "custo": campos_brutos.get("Custo") or None,
        "acionamento": campos_brutos.get("Acionamento") or None,
        "requerimentos": campos_brutos.get("Requerimentos") or None,
        "distancia": campos_brutos.get("Distância") or None,
        "area": area or None,
        "alvos": alvos or None,
        "salvamento": campos_brutos.get("Salvamento") or None,
        "duracao": campos_brutos.get("Duração") or None,
    }


def _extrair_acoes_execucao(execucao: str) -> str | None:
    """Deriva representação normalizada de custo de ação/tempo a partir da linha de Execução."""
    if not execucao:
        return None
    if "[one-action] a [three-actions]" in execucao:
        return "1 a 3"
    mapa = {
        "[one-action]": "1",
        "[two-actions]": "2",
        "[three-actions]": "3",
        "[free-action]": "livre",
        "[reaction]": "reacao",
    }
    for tok, val in mapa.items():
        if tok in execucao:
            return val
    if "(" in execucao:
        return execucao.split("(", 1)[0].strip()
    return execucao


def _extrair_componentes_execucao(execucao: str) -> list[str]:
    """Extrai a lista ordenada de componentes mágicos a partir da linha de Execução."""
    presentes: list[str] = []
    texto_lower = execucao.lower()
    for comp in ("foco", "material", "somático", "verbal"):
        if re.search(rf"\b{comp}\b", texto_lower):
            presentes.append(comp)
    return presentes


def _montar_paragrafos_corpo(
    linhas_corpo: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]]
) -> tuple[str, dict[str, str] | None]:
    """Reconstrói parágrafos, marcadores e graus de sucesso do corpo da magia."""
    blocos_logicos: list[dict[str, Any]] = []
    em_hanging = False
    prev_x1 = 0.0
    prev_txt_limpo = ""
    prev_col_base = 0.0

    for bp, col, x0, _y0, x1, _y1, spans in linhas_corpo:
        col_base = coluna_x0_base(bp, col)
        txt = limpar_texto("".join(s["text"] for s in spans))
        if not txt:
            continue

        primeiro = next((s for s in spans if s["text"].strip()), None)
        eh_marcador = txt.startswith("•")
        eh_resultado = (
            primeiro is not None
            and primeiro.get("font") == "GoodOT-Bold"
            and primeiro["text"].strip() in ROTULOS_RESULTADOS
        )

        # Verifica se a linha indentada (+9pt) inicia um novo parágrafo em vez de continuação pendente
        eh_indentada = abs(x0 - (col_base + 9.0)) < 1.5
        linha_anterior_encerrada = (
            prev_x1 < prev_col_base + 216.0
            and bool(re.search(r"[.!?:)]$", prev_txt_limpo))
        )

        if not blocos_logicos:
            blocos_logicos.append({"tipo": "resultado" if eh_resultado else ("marcador" if eh_marcador else "paragrafo"), "rotulo": primeiro["text"].strip() if eh_resultado else None, "segs": [txt]})
            em_hanging = eh_marcador or eh_resultado
        elif eh_resultado:
            blocos_logicos.append({"tipo": "resultado", "rotulo": primeiro["text"].strip(), "segs": [txt]})
            em_hanging = True
        elif eh_marcador:
            blocos_logicos.append({"tipo": "marcador", "rotulo": None, "segs": [txt]})
            em_hanging = True
        elif eh_indentada and (not em_hanging or linha_anterior_encerrada):
            blocos_logicos.append({"tipo": "paragrafo", "rotulo": None, "segs": [txt]})
            em_hanging = False
        elif not eh_indentada and em_hanging and abs(x0 - col_base) < 1.5 and linha_anterior_encerrada and blocos_logicos[-1]["tipo"] == "resultado":
            # Caso um parágrafo raro retorne exatamente à margem sem recuo após resultado
            blocos_logicos.append({"tipo": "paragrafo", "rotulo": None, "segs": [txt]})
            em_hanging = False
        else:
            blocos_logicos[-1]["segs"].append(txt)

        prev_x1 = x1
        prev_txt_limpo = txt
        prev_col_base = col_base

    paragrafos_desc: list[str] = []
    resultados: dict[str, str] = {}
    for bloco in blocos_logicos:
        texto_bloco = concatenar_segmentos_linha(bloco["segs"])
        if bloco["tipo"] == "resultado":
            rot = bloco["rotulo"]
            chave = ROTULOS_RESULTADOS[rot]
            conteudo = texto_bloco[len(rot) :].strip()
            resultados[chave] = conteudo
        elif bloco["tipo"] == "marcador":
            texto_bullet = re.sub(r"^•\s*", "• ", texto_bloco)
            paragrafos_desc.append(texto_bullet)
        else:
            paragrafos_desc.append(texto_bloco)

    # Junta parágrafos com \n\n e itens consecutivos com marcador usando \n simples
    partes_finais: list[str] = []
    for p in paragrafos_desc:
        if not partes_finais:
            partes_finais.append(p)
        elif p.startswith("• ") and partes_finais[-1].startswith("• "):
            partes_finais[-1] = f"{partes_finais[-1]}\n{p}"
        else:
            partes_finais.append(p)

    descricao = "\n\n".join(partes_finais)
    return descricao, (resultados if resultados else None)


def _parsear_elevada(
    linhas_elevada: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]]
) -> tuple[str | None, list[dict[str, str]] | None]:
    """Parseia cláusulas `Elevada (...)` e eventuais introduções anteriores na seção."""
    if not linhas_elevada:
        return None, None

    linhas_txt = [limpar_texto("".join(s["text"] for s in item[6])) for item in linhas_elevada]
    linhas_txt = [t for t in linhas_txt if t]
    if not linhas_txt:
        return None, None

    blocos: list[tuple[str, list[str]]] = []
    intro_segs: list[str] = []

    for idx_l, t in enumerate(linhas_txt):
        spans = linhas_elevada[idx_l][6] if idx_l < len(linhas_elevada) else []
        primeiro = next((s for s in spans if s["text"].strip()), None)
        eh_inicio_elevada = (
            primeiro is not None
            and primeiro.get("font") == "GoodOT-Bold"
            and t.startswith("Elevada")
        ) or t.startswith("Elevada (") or t == "Elevada Como convocar animal."

        if eh_inicio_elevada:
            m = re.match(r"^Elevada\s*\(([^)]+)\)\s*(.*)$", t)
            if m:
                blocos.append((m.group(1).strip(), [m.group(2).strip()] if m.group(2).strip() else []))
            elif t.startswith("Elevada "):
                blocos.append(("especial", [t[len("Elevada ") :].strip()]))
            else:
                blocos.append(("especial", [t]))
        elif not blocos:
            intro_segs.append(t)
        else:
            blocos[-1][1].append(t)

    intro = concatenar_segmentos_linha(intro_segs) if intro_segs else None
    lista_elevada = (
        [{"nivel": niv, "efeito": concatenar_segmentos_linha(segs)} for niv, segs in blocos]
        if blocos
        else None
    )
    return intro, lista_elevada


def _extrair_tabela_cancao_incomensuravel(doc: pymupdf.Document) -> list[dict[str, str]]:
    """Extrai estruturadamente a tabela de resultados 1–5 da magia Canção Incomensurável (p. 324)."""
    page = doc[324 - DESLOCAMENTO_PAGINA_LIVRO]
    linhas: list[tuple[float, float, str]] = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            x0, y0, _x1, _y1 = l["bbox"]
            if x0 >= 315.0 and 565.0 <= y0 <= 650.0:
                t = limpar_texto("".join(s["text"] for s in l["spans"]))
                if t and t not in ("Resultado", "Efeito", "Resultado Efeito"):
                    linhas.append((y0, x0, t))
    linhas.sort(key=lambda r: (round(r[0], 1), r[1]))

    linhas_mescladas: list[list[Any]] = []
    for y0, x0, t in linhas:
        if linhas_mescladas and abs(linhas_mescladas[-1][0] - y0) < 3.0:
            linhas_mescladas[-1][2] = f"{linhas_mescladas[-1][2]} {t}".strip()
        else:
            linhas_mescladas.append([y0, x0, t])

    tabela: list[dict[str, str]] = []
    for _y0, min_x0, t in linhas_mescladas:
        m = re.match(r"^([1-5])\s+(.+)$", t) if min_x0 < 350.0 else None
        if m:
            tabela.append({"resultado": m.group(1), "efeito": m.group(2).strip()})
        elif tabela:
            tabela[-1]["efeito"] = f"{tabela[-1]['efeito']} {t}".strip()

    assert [r["resultado"] for r in tabela] == ["1", "2", "3", "4", "5"], (
        f"Resultados inesperados na tabela de Canção Incomensurável: {tabela}"
    )
    assert "assustado 2" in tabela[0]["efeito"], f"Linha 1 inesperada: {tabela[0]}"
    assert "duração ilimitada" in tabela[4]["efeito"], f"Linha 5 inesperada: {tabela[4]}"
    return tabela


def _separar_meta_e_corpo_sem_hrule(
    linhas_sec1: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]]
) -> tuple[
    list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]],
    list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]],
]:
    """Separa metadados e corpo quando a diagramação omite a linha horizontal divisória."""
    linhas_meta: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]] = []
    linhas_corpo: list[tuple[int, int, float, float, float, float, list[dict[str, Any]]]] = []
    em_meta = True
    for item in linhas_sec1:
        spans = item[6]
        primeiro = next((s for s in spans if s["text"].strip()), None)
        if (
            em_meta
            and primeiro is not None
            and primeiro.get("font") == "GoodOT-Bold"
            and primeiro["text"].strip().rstrip(":") in ROTULOS_METADADOS
        ):
            linhas_meta.append(item)
        else:
            em_meta = False
            linhas_corpo.append(item)
    return linhas_meta, linhas_corpo


def _secao_comeca_com_elevada(secao: list[Any]) -> bool:
    """Verifica se uma seção começa diretamente com um cabeçalho em negrito `Elevada`."""
    if not secao:
        return False
    spans = secao[0][4][4]
    primeiro = next((s for s in spans if s["text"].strip()), None)
    return (
        primeiro is not None
        and primeiro.get("font") == "GoodOT-Bold"
        and limpar_texto(primeiro["text"]).startswith("Elevada")
    )


def extrair_magias_descricoes(
    doc: pymupdf.Document, indice_listas: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Extrai todas as 220 descrições completas de magias das páginas 316–358 (índices 19–61)."""
    tabela_cancao = _extrair_tabela_cancao_incomensuravel(doc)

    regras_horizontais: dict[int, dict[int, list[float]]] = {}
    for idx in range(19, len(doc)):
        bp = idx + DESLOCAMENTO_PAGINA_LIVRO
        hl: dict[int, list[float]] = {1: [], 2: []}
        for dr in doc[idx].get_drawings():
            r = dr["rect"]
            if r.width > 180.0 and r.height < 3.0 and 45.0 <= r.y0 <= 745.0:
                col = 1 if r.x0 < 300.0 else 2
                if deve_ignorar_regiao_quadro(bp, col, r.y0):
                    continue
                hl[col].append(round(r.y0, 2))
        regras_horizontais[bp] = {1: sorted(set(hl[1])), 2: sorted(set(hl[2]))}

    magias_brutas: list[dict[str, Any]] = []
    atual: dict[str, Any] | None = None

    for idx in range(19, len(doc)):
        bp = idx + DESLOCAMENTO_PAGINA_LIVRO
        d = doc[idx].get_text("dict")
        cols: dict[int, list[tuple[float, float, float, float, list[dict[str, Any]]]]] = {1: [], 2: []}
        for b in d["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                x0, y0, x1, y1 = l["bbox"]
                if y0 < 45.0 or y0 > 745.0 or x0 > 535.0 or x0 < 55.0:
                    continue
                col = 1 if x0 < 300.0 else 2
                if deve_ignorar_regiao_quadro(bp, col, y0):
                    continue
                # Separa a tabela embutida de Canção Incomensurável do texto corrido
                if bp == 324 and col == 2 and 565.0 <= y0 <= 650.0:
                    continue
                cols[col].append((y0, x0, x1, y1, l["spans"]))

        for col in (1, 2):
            linhas = sorted(cols[col], key=lambda r: (r[0], r[1]))
            mescladas: list[list[Any]] = []
            for y0, x0, x1, y1, spans in linhas:
                if mescladas and abs(mescladas[-1][0] - y0) < 3.0:
                    mescladas[-1][4].extend(spans)
                    mescladas[-1][4].sort(key=lambda s: s["bbox"][0])
                    mescladas[-1][1] = min(mescladas[-1][1], x0)
                    mescladas[-1][2] = max(mescladas[-1][2], x1)
                    mescladas[-1][3] = max(mescladas[-1][3], y1)
                else:
                    mescladas.append([y0, x0, x1, y1, list(spans)])

            eventos: list[tuple[str, float, Any]] = [("LINE", l[0], l) for l in mescladas] + [
                ("HRULE", hy, None) for hy in regras_horizontais[bp][col]
            ]
            eventos.sort(key=lambda e: (e[1], 0 if e[0] == "HRULE" else 1))

            for etype, ey, payload in eventos:
                if etype == "LINE":
                    y0, x0, x1, y1, spans = payload
                    txt = limpar_texto("".join(s["text"] for s in spans))
                    if not txt or spans[0].get("font") == "Taroca":
                        continue
                    m = re.match(r"^(.+?)\s+(MAGIA|TRUQUE MÁGICO)\s+(\d+)$", txt)
                    if m and any(s.get("font") == "GoodOT-CondBold" and s.get("size", 0) >= 11.0 for s in spans):
                        if atual is not None:
                            magias_brutas.append(atual)
                        atual = {
                            "titulo_pdf": m.group(1).strip(),
                            "tipo_cabecalho": m.group(2),
                            "nivel_cabecalho": int(m.group(3)),
                            "pagina": bp,
                            "eventos": [],
                        }
                        continue
                if atual is not None:
                    atual["eventos"].append((etype, bp, col, ey, payload))

    if atual is not None:
        magias_brutas.append(atual)

    magias: list[dict[str, Any]] = []
    for sp in magias_brutas:
        secoes: list[list[Any]] = [[]]
        for ev in sp["eventos"]:
            if ev[0] == "HRULE":
                secoes.append([])
            else:
                secoes[-1].append(ev)

        assert len(secoes) >= 2 and len(secoes[0]) == 0, (
            f"Estrutura de seções inesperada em {sp['titulo_pdf']} (p.{sp['pagina']}): {[len(s) for s in secoes]}"
        )

        # Separa traços e metadados da primeira seção útil
        sec_meta_candidata = secoes[1]
        tracos_brutos: list[str] = []
        idx_meta = 0
        while idx_meta < len(sec_meta_candidata):
            spans = sec_meta_candidata[idx_meta][4][4]
            if all((s.get("font") == "GoodOT-CondBold" and s.get("size", 0) <= 7.5) or not s["text"].strip() for s in spans):
                for s in spans:
                    if s["text"].strip():
                        tracos_brutos.append(s["text"].strip())
                idx_meta += 1
            else:
                break

        # Converter formato de payload para (bp, col, x0, y0, x1, y1, spans)
        linhas_sec1 = [
            (ev[1], ev[2], ev[4][1], ev[4][0], ev[4][2], ev[4][3], ev[4][4])
            for ev in sec_meta_candidata[idx_meta:]
        ]

        if len(secoes) == 2:
            # Desejo (p. 333): diagramação omite a linha horizontal entre Execução e corpo
            linhas_meta, linhas_corpo = _separar_meta_e_corpo_sem_hrule(linhas_sec1)
            linhas_elevada = []
        elif len(secoes) == 3 and _secao_comeca_com_elevada(secoes[2]):
            # Contingência (p. 328): omite linha horizontal entre Duração e corpo, mantendo a de Elevada
            linhas_meta, linhas_corpo = _separar_meta_e_corpo_sem_hrule(linhas_sec1)
            linhas_elevada = [
                (ev[1], ev[2], ev[4][1], ev[4][0], ev[4][2], ev[4][3], ev[4][4])
                for ev in secoes[2]
            ]
        else:
            linhas_meta = linhas_sec1
            linhas_corpo = [
                (ev[1], ev[2], ev[4][1], ev[4][0], ev[4][2], ev[4][3], ev[4][4])
                for ev in secoes[2]
            ]
            linhas_elevada = (
                [
                    (ev[1], ev[2], ev[4][1], ev[4][0], ev[4][2], ev[4][3], ev[4][4])
                    for ev in secoes[3]
                ]
                if len(secoes) >= 4
                else []
            )

        meta_parseado = _parsear_metadados_magia(linhas_meta)
        descricao, resultados = _montar_paragrafos_corpo(linhas_corpo)
        intro_elevada, elevada = _parsear_elevada(linhas_elevada)
        if intro_elevada:
            descricao = f"{descricao}\n\n{intro_elevada}" if descricao else intro_elevada

        sid = slugify(sp["titulo_pdf"])
        info_lista = indice_listas.get(sid)
        assert info_lista is not None, f"Magia {sp['titulo_pdf']} não localizada nas listas de magias"

        escola_canonica = next(
            (ESCOLAS_MAIUSCULAS[t] for t in tracos_brutos if t in ESCOLAS_MAIUSCULAS),
            info_lista["escola"],
        )
        raridade = "raro" if "RARO" in tracos_brutos else ("incomum" if "INCOMUM" in tracos_brutos else "comum")
        tracos_formatados = [formatar_traco(t) for t in tracos_brutos]

        tipo = "truque_magico" if sp["tipo_cabecalho"] == "TRUQUE MÁGICO" else "magia"
        nivel = 0 if tipo == "truque_magico" else sp["nivel_cabecalho"]

        obs_livro = None
        if sid == "conto_das_rochas":
            obs_livro = (
                "Incongruência do Livro Básico (p. 328): nas Listas de Magias (pp. 311 e 314) esta magia consta como "
                "Adivinhação (adv), porém o cabeçalho de sua descrição imprime o traço EVOCAÇÃO."
            )
        elif sid == "massacre":
            obs_livro = (
                "Incongruência do Livro Básico (p. 358): o cabeçalho lista Salvamento Fortitude, enquanto o corpo do texto "
                "impresso cita salvamento de Vontade."
            )

        resumos = sorted(info_lista["resumos"])
        resumo_lista = resumos[0] if resumos else ""

        magias.append(
            {
                "id": sid,
                "nome": info_lista["nome"],
                "tipo": tipo,
                "nivel": nivel,
                "pagina": sp["pagina"],
                "raridade": raridade,
                "tracos": tracos_formatados,
                "escola": escola_canonica,
                "tradicoes": meta_parseado["tradicoes"],
                "execucao": traduzir_tokens_acao_pt(meta_parseado["execucao"]),
                "acoes": meta_parseado["acoes"],
                "componentes": meta_parseado["componentes"],
                "custo": meta_parseado["custo"],
                "acionamento": meta_parseado["acionamento"],
                "requerimentos": meta_parseado["requerimentos"],
                "distancia": meta_parseado["distancia"],
                "area": meta_parseado["area"],
                "alvos": meta_parseado["alvos"],
                "salvamento": meta_parseado["salvamento"],
                "duracao": meta_parseado["duracao"],
                "resumo_lista": resumo_lista,
                "descricao": traduzir_tokens_acao_pt(descricao),
                "resultados": resultados,
                "elevada": elevada,
                "tabela": tabela_cancao if sid == "cancao_incomensuravel" else None,
                "observacao_livro": obs_livro,
            }
        )

    return magias


def montar_dados_magias_01() -> dict[str, Any]:
    """Orquestra a extração, consolidação e montagem do schema `dados/magias01.json`."""
    assert CAMINHO_PDF.exists(), f"Arquivo PDF não encontrado: {CAMINHO_PDF}"
    doc = pymupdf.open(str(CAMINHO_PDF))
    try:
        regras_gerais = construir_regras_gerais()
        quadros_auxiliares = construir_quadros_auxiliares()
        listas_de_magias, indice_listas = extrair_listas_de_magias(doc)
        magias = extrair_magias_descricoes(doc, indice_listas)
    finally:
        doc.close()

    ids_descritas = {m["id"] for m in magias}
    for _trad, niveis in listas_de_magias["por_tradicao"].items():
        for _nk, lista in niveis.items():
            for it in lista:
                it["disponivel_em_magias01"] = it["id"] in ids_descritas

    truques_count = sum(1 for m in magias if m["tipo"] == "truque_magico")
    magias_nivel_count = sum(1 for m in magias if m["tipo"] == "magia")

    return {
        "meta": {
            "sistema": "Pathfinder 2ª Edição (Livro Básico)",
            "capitulo": "Capítulo 7: Magias (Parte 1 — Regras Gerais, Listas Completas de Magias e Descrições A–M)",
            "fonte_pdf": "ref/Enchanced 01.pdf",
            "paginas_livro": "297-358",
            "versao": "1.0.0",
            "escopo_parte": (
                "Contém as regras gerais completas de conjuração (pp. 297–306), as 4 Listas de Magias completas A–Z "
                "(pp. 307–315), os 3 quadros auxiliares das pp. 323, 334 e 338, e as primeiras 220 descrições completas "
                "de magias (Abrandar a Melhorar Alimentos, pp. 316–358). O restante (Mensageiro Animal a Zona da Verdade "
                "e Magias de Foco) corresponde a ref/Enchacent02.pdf (dados/magias02.json)."
            ),
            "totais": {
                "escolas_magicas": len(regras_gerais["escolas_magicas"]),
                "tradicoes_magicas": len(regras_gerais["tradicoes_magicas"]["tradicoes"]),
                "essencias": len(regras_gerais["as_quatro_essencias"]["essencias"]),
                "entradas_listas_de_magias": listas_de_magias["total_entradas"],
                "magias_unicas_nas_listas": listas_de_magias["total_magias_unicas"],
                "magias_descritas_nesta_parte": len(magias),
                "truques_magicos_descritos": truques_count,
                "magias_nivel_1_a_10_descritas": magias_nivel_count,
                "quadros_auxiliares": len(quadros_auxiliares),
            },
            "incongruencias_livro": [
                {
                    "id": "conto_das_rochas_escola",
                    "magia": "Conto das Rochas",
                    "pagina": 328,
                    "descricao": (
                        "Nas Listas de Magias Divinas (p. 311) e Primais (p. 314) aparece como Adivinhação (adv), porém o "
                        "cabeçalho da descrição (p. 328) imprime o traço EVOCAÇÃO."
                    ),
                    "tratamento": "Preservado o traço impresso (Evocação) na descrição e (Adivinhação) nas listas, com nota em observacao_livro.",
                },
                {
                    "id": "massacre_salvamento",
                    "magia": "Massacre",
                    "pagina": 358,
                    "descricao": (
                        "O cabeçalho especifica Salvamento Fortitude, enquanto o corpo do texto impresso refere-se a um "
                        "salvamento de Vontade (erro de tradução da edição)."
                    ),
                    "tratamento": "Texto preservado fielmente ao PDF e registrado em observacao_livro.",
                },
                {
                    "id": "localizar_componentes",
                    "magia": "Localizar",
                    "pagina": 354,
                    "descricao": "O texto impresso omite a vírgula entre material e somático: 'Execução 10 minutos (material somático, verbal)'.",
                    "tratamento": "Campo componentes normalizado para ['material', 'somático', 'verbal'].",
                },
                {
                    "id": "avatar_token_irori",
                    "magia": "Avatar",
                    "pagina": 320,
                    "descricao": "Quebra de linha no marcador de ação de Irori ('[one-\\naction]').",
                    "tratamento": "Normalizado para '[one-action]'.",
                },
                {
                    "id": "desejo_e_contingencia_sem_linha_divisoria",
                    "magia": "Contingência (p. 328) e Desejo (p. 333)",
                    "pagina": "328, 333",
                    "descricao": (
                        "A diagramação omite a linha horizontal separadora entre o último metadado (Duração em Contingência; "
                        "Execução em Desejo) e o texto descritivo da magia."
                    ),
                    "tratamento": "Separado automaticamente pelo encerramento dos rótulos de metadados em negrito.",
                },
            ],
        },
        "regras_gerais": regras_gerais,
        "quadros_auxiliares": quadros_auxiliares,
        "listas_de_magias": listas_de_magias,
        "magias": magias,
    }


def validar_dados_magias_01(dados: dict[str, Any]) -> None:
    """Executa bateria de asserções estruturais e de integridade cruzada."""
    rg = dados["regras_gerais"]
    assert len(rg["escolas_magicas"]) == 8
    assert len(rg["tradicoes_magicas"]["tradicoes"]) == 4
    assert len(rg["as_quatro_essencias"]["essencias"]) == 4
    assert len(rg["outros_tracos_de_magia"]["tracos"]) == 8
    assert len(rg["conjurando_magias"]["componentes_de_magia"]) == 4

    quadros = dados["quadros_auxiliares"]
    assert len(quadros) == 3
    assert len(quadros[1]["tabela"]) == 5

    listas = dados["listas_de_magias"]
    assert listas["totais_por_tradicao"] == {
        "arcana": 242,
        "divina": 149,
        "ocultista": 216,
        "primal": 172,
    }, f"Totais inesperados nas listas: {listas['totais_por_tradicao']}"
    assert listas["total_entradas"] == 779
    assert listas["total_magias_unicas"] == 379

    magias = dados["magias"]
    assert len(magias) == 220, f"Esperado 220 magias descritas, obtido {len(magias)}"
    assert magias[0]["id"] == "abrandar" and magias[0]["pagina"] == 316
    assert magias[-1]["id"] == "melhorar_alimentos" and magias[-1]["pagina"] == 358

    ids = [m["id"] for m in magias]
    assert len(ids) == len(set(ids)), "Existem IDs duplicados em magias"

    # Reconstruir índice das listas para cruzamento 1:1
    mapa_listas: dict[str, dict[str, Any]] = {}
    for trad, niveis in listas["por_tradicao"].items():
        for nk, items in niveis.items():
            lvl = 0 if nk == "truques_magicos" else int(nk)
            for it in items:
                sid = it["id"]
                if sid not in mapa_listas:
                    mapa_listas[sid] = {
                        "nome": it["nome"],
                        "nivel": lvl,
                        "escola": it["escola"],
                        "raridade": it["raridade"],
                        "elevavel": it["elevavel"],
                        "tradicoes": set(),
                    }
                mapa_listas[sid]["tradicoes"].add(trad)

    # Verifica se nenhuma magia <= Melhorar Alimentos ficou de fora
    faltantes = [
        info["nome"]
        for sid, info in mapa_listas.items()
        if sid not in set(ids) and info["nome"].lower() < "mensageiro"
    ]
    assert not faltantes, f"Magias ausentes nas descrições A-M: {faltantes}"

    for m in magias:
        sid = m["id"]
        li = mapa_listas[sid]
        assert m["nivel"] == li["nivel"], f"Nível divergente em {sid}"
        assert set(m["tradicoes"]) == li["tradicoes"], f"Tradições divergentes em {sid}"
        assert m["raridade"] == li["raridade"], f"Raridade divergente em {sid}"
        assert bool(m["elevada"]) == li["elevavel"], f"Elevada divergente em {sid}"
        if sid != "conto_das_rochas":
            assert m["escola"] == li["escola"], f"Escola divergente em {sid}: {m['escola']} vs {li['escola']}"

        assert m["tradicoes"], f"Sem tradições: {sid}"
        assert m["execucao"], f"Sem execução: {sid}"
        assert m["descricao"], f"Sem descrição: {sid}"
        assert len(m["execucao"]) <= 80, f"Execução longa demais em {sid}: {m['execucao']}"
        for campo_meta in ("distancia", "area", "alvos", "salvamento", "duracao", "custo", "requerimentos"):
            val_meta = m[campo_meta]
            if val_meta:
                assert len(val_meta) <= 160, f"Campo {campo_meta} longo demais em {sid}: {val_meta}"
                if campo_meta != "requerimentos":
                    assert "Você " not in val_meta, f"Possível sangria de texto em {campo_meta} de {sid}: {val_meta}"

        tudo = json.dumps(m, ensure_ascii=False)
        assert "\x08" not in tudo, f"Caractere \\x08 residual em {sid}"
        assert "[one- " not in tudo and "[one-\n" not in tudo, f"Token quebrado em {sid}"
        for sangria in ("MAGIA E MORALIDADE", "AURA DE TENDÊNCIA", "AÇÕES DE ESCUDO", "BLOQUEIO COM ESCUDO [reaction]"):
            assert sangria not in m["descricao"], f"Sangria de quadro '{sangria}' em {sid}"

    por_id = {m["id"]: m for m in magias}
    cancao = por_id["cancao_incomensuravel"]
    assert cancao["tabela"] is not None
    assert [r["resultado"] for r in cancao["tabela"]] == ["1", "2", "3", "4", "5"]
    assert "assustado 2" in cancao["tabela"][0]["efeito"]
    assert "duração ilimitada" in cancao["tabela"][4]["efeito"]

    contingencia = por_id["contingencia"]
    assert contingencia["duracao"] == "24 horas"
    assert contingencia["descricao"].startswith("Você prepara uma magia")
    assert contingencia["elevada"] is not None and [e["nivel"] for e in contingencia["elevada"]] == ["8º", "9º", "10º"]

    arcana_ids = {
        it["id"]
        for items in listas["por_tradicao"]["arcana"].values()
        for it in items
    }
    for pid in ("palavra_de_poder_atordoar", "palavra_de_poder_cegar", "palavra_de_poder_matar"):
        assert pid in arcana_ids, f"{pid} ausente na lista arcana"


def main() -> None:
    """Executa a geração e validação completa de `dados/magias01.json`."""
    dados = montar_dados_magias_01()
    validar_dados_magias_01(dados)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_SAIDA.open("w", encoding="utf-8") as arq:
        json.dump(dados, arq, ensure_ascii=False, indent=2)
        arq.write("\n")

    tamanho = CAMINHO_SAIDA.stat().st_size
    totais = dados["meta"]["totais"]
    print(f"Arquivo gerado com sucesso: {CAMINHO_SAIDA} ({tamanho} bytes)")
    print(f"Listas de Magias: {totais['entradas_listas_de_magias']} entradas / {totais['magias_unicas_nas_listas']} únicas")
    print(f"Por tradição: {dados['listas_de_magias']['totais_por_tradicao']}")
    print(f"Magias descritas (A-M): {totais['magias_descritas_nesta_parte']} ({totais['truques_magicos_descritos']} truques + {totais['magias_nivel_1_a_10_descritas']} magias)")
    print(f"Quadros auxiliares: {totais['quadros_auxiliares']}")


if __name__ == "__main__":
    main()
