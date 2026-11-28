from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "dadospf2" / "talentos.json"


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


def construir_entrada_tabela(
    nome: str,
    nivel: int,
    pre_requisitos: str | None,
    beneficios: str,
) -> dict[str, Any]:
    return {
        "id": slugify(nome),
        "nome": nome,
        "nivel": nivel,
        "pre_requisitos": pre_requisitos,
        "beneficios": beneficios,
    }


def construir_talento(
    nome: str,
    nivel: int,
    tracos: list[str],
    descricao: str,
    *,
    acoes: str | None = None,
    pre_requisitos: str | None = None,
    acionamento: str | None = None,
    requerimentos: str | None = None,
    especial: str | None = None,
    resultados: dict[str, str] | None = None,
    opcoes_tabela: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "id": slugify(nome),
        "nome": nome,
        "nivel": nivel,
        "categoria": "pericia" if "Perícia" in tracos else "geral",
        "grupo_pericia": None,
        "resumo_beneficio": None,
        "tracos": tracos,
        "acoes": acoes,
        "pre_requisitos": pre_requisitos,
        "acionamento": acionamento,
        "requerimentos": requerimentos,
        "especial": especial,
        "resultados": resultados,
        "opcoes_tabela": opcoes_tabela,
        "descricao": descricao,
    }


def construir_tabela_5_1() -> list[dict[str, Any]]:
    return [
        construir_entrada_tabela("Ancestralidade Adotada", 1, None, "Obtém acesso a talentos de outra ancestralidade"),
        construir_entrada_tabela("Bloqueio com Escudo", 1, None, "Apara um golpe com seu escudo"),
        construir_entrada_tabela("Cavalgar", 1, None, "Obtém sucesso automaticamente ao comandar sua montaria para se mover"),
        construir_entrada_tabela("Controlar a Respiração", 1, None, "Prende sua respiração por mais tempo e recebe benefícios contra ameaças inaladas"),
        construir_entrada_tabela("Duro de Matar", 1, None, "Morre em morrendo 5 (em vez de morrendo 4)"),
        construir_entrada_tabela("Iniciativa Incrível", 1, None, "+2 em rolagens de iniciativa"),
        construir_entrada_tabela("Passo Aprumado", 1, "Destreza 14", "Dá um Passo em terreno difícil"),
        construir_entrada_tabela("Perspicácia Astuta", 1, None, "Se torna especialista em um salvamento ou em Percepção"),
        construir_entrada_tabela("Proficiência com Armas", 1, None, "Se torna treinado em um tipo de arma"),
        construir_entrada_tabela("Proficiência com Armaduras", 1, None, "Se torna treinado em um tipo de armadura"),
        construir_entrada_tabela("Recuperação Rápida", 1, "Constituição 14", "Recupera mais PV descansando e recupera-se rápido de doenças e venenos"),
        construir_entrada_tabela("Veloz", 1, None, "Aumenta sua Velocidade em 1,5 metros"),
        construir_entrada_tabela("Vitalidade", 1, None, "Aumenta seus PV máximos e reduz a CD de testes de recuperação"),
        construir_entrada_tabela("Exemplar Ancestral", 3, None, "Recebe um talento de ancestralidade de 1º nível"),
        construir_entrada_tabela("Improvisação Destreinada", 3, None, "Se torna mais habilidoso em usar perícias destreinadas"),
        construir_entrada_tabela("Procura Acelerada", 7, "Mestre em Percepção", "Procura em áreas na metade do tempo"),
        construir_entrada_tabela("Investidura Incrível", 11, "Carisma 16", "Investe em até 12 itens mágicos"),
    ]


def construir_tabela_5_2() -> list[dict[str, Any]]:
    grupos: list[tuple[str, str, str, list[tuple[str, int, str | None, str]]]] = [
        (
            "pericias_variadas",
            "Talentos de Perícias Variadas",
            "variadas",
            [
                ("Certeza", 1, "Treinado em pelo menos uma perícia", "Obtém um resultado fixo em um teste de perícia"),
                ("Conhecimento Duvidoso", 1, "Treinado em uma perícia com a ação Recordar Conhecimento", "Obtém conhecimento errado e verdadeiro em uma falha"),
                ("Enganar Item Mágico", 1, "Treinado em Arcanismo, Natureza, Ocultismo ou Religião", "Ativa um item mágico que normalmente não poderia"),
                ("Identificação Rápida", 1, "Treinado em Arcanismo, Natureza, Ocultismo ou Religião", "Identifica Magia em 1 minuto ou menos"),
                ("Reconhecer Magia", 1, "Treinado em Arcanismo, Natureza, Ocultismo ou Religião", "Identifica uma magia como uma reação enquanto ela é conjurada"),
                ("Treinamento em Perícia", 1, "Inteligência 12", "Se torna treinado em uma perícia"),
                ("Atalho Mágico", 2, "Especialista em Arcanismo, Natureza, Ocultismo ou Religião", "Aprende magias rapidamente e com custo reduzido"),
                ("Conhecimento Automático", 2, "Especialista em uma perícia com a ação Recordar Conhecimento", "Recorda Conhecimento como uma ação livre uma vez por rodada"),
                ("Reconhecimento Rápido", 7, "Mestre em Arcanismo, Natureza, Ocultismo ou Religião; Reconhecer Magia", "Identifica magias como uma ação livre"),
            ],
        ),
        (
            "acrobatismo",
            "Talentos de Acrobatismo",
            "acrobatismo",
            [
                ("Equilíbrio Estável", 1, "Treinado em Acrobatismo", "Mantém seu equilíbrio em condições adversas"),
                ("Espremer-se Rapidamente", 1, "Treinado em Acrobatismo", "Move-se rapidamente enquanto se Espreme"),
                ("Queda do Gato", 1, "Treinado em Acrobatismo", "Trata quedas como mais curtas do que são"),
                ("Rastejo Ligeiro", 2, "Especialista em Acrobatismo", "Rasteja mais rápido"),
                ("Levantar Rapidamente", 7, "Mestre em Acrobatismo", "Fica de pé livremente sem acionar reações"),
            ],
        ),
        (
            "arcanismo",
            "Talentos de Arcanismo",
            "arcanismo",
            [
                ("Sentido Arcano", 1, "Treinado em Arcanismo", "Conjura detectar magia à vontade como uma magia arcana inata"),
                ("Teoria Unificada", 15, "Lendário em Arcanismo", "Utiliza Arcanismo para testes de todas as tradições"),
            ],
        ),
        (
            "atletismo",
            "Talentos de Atletismo",
            "atletismo",
            [
                ("Carregador Robusto", 1, "Treinado em Atletismo", "Aumenta seu limite de Volume em 2 pontos"),
                ("Escalador de Combate", 1, "Treinado em Atletismo", "Luta de forma mais eficaz enquanto Escala"),
                ("Lutador Titânico", 1, "Treinado em Atletismo", "Agarra, Desarma, Derruba ou Empurra criaturas maiores"),
                ("Salto Rápido", 1, "Treinado em Atletismo", "Salta em Altura ou à Distância como uma ação única"),
                ("Saqueador Subaquático", 1, "Treinado em Atletismo", "Luta de forma mais eficaz embaixo d'água"),
                ("Salto Poderoso", 2, "Especialista em Atletismo", "Salta mais alto e mais longe"),
                ("Segurar-se Rapidamente", 2, "Especialista em Atletismo", "Se ergue de beiradas rapidamente"),
                ("Escalada Rápida", 7, "Mestre em Atletismo", "Escala rapidamente"),
                ("Natação Rápida", 7, "Mestre em Atletismo", "Nada rapidamente"),
                ("Salto na Parede", 7, "Mestre em Atletismo", "Salta pelas paredes"),
                ("Salto nas Nuvens", 15, "Lendário em Atletismo", "Salta distâncias impossíveis"),
            ],
        ),
        (
            "diplomacia",
            "Talentos de Diplomacia",
            "diplomacia",
            [
                ("Camarada", 1, "Treinado em Diplomacia", "Obtém Informação rapidamente"),
                ("Impressionar Grupo", 1, "Treinado em Diplomacia", "Impressiona múltiplos alvos de uma vez"),
                ("Pechinchador", 1, "Treinado em Diplomacia", "Ganha Proventos ao procurar por pechinchas"),
                ("Cumprimento Caloroso", 2, "Especialista em Diplomacia", "Impressiona um alvo que acabou de conhecer"),
                ("Pedido Desavergonhado", 7, "Mestre em Diplomacia", "Faz Pedidos para outras pessoas com consequências mais brandas"),
                ("Negociação Lendária", 15, "Lendário em Diplomacia", "Negocia rapidamente com adversários"),
            ],
        ),
        (
            "dissimulacao",
            "Talentos de Dissimulação",
            "dissimulacao",
            [
                ("Distração Prolongada", 1, "Treinado em Dissimulação", "Permanece escondido após Criar uma Distração"),
                ("Mente na Minha Cara", 1, "Treinado em Dissimulação", "Utiliza Dissimulação para detectar mentiras"),
                ("Mentiroso Charmoso", 1, "Treinado em Dissimulação", "Aprimora a atitude de um alvo com suas mentiras"),
                ("Confabulador", 2, "Especialista em Dissimulação", "Reduz os bônus contra suas repetidas mentiras"),
                ("Disfarce Rápido", 2, "Especialista em Dissimulação", "Monta um disfarce em metade do tempo"),
                ("Segredos Escorregadios", 7, "Mestre em Dissimulação", "Evita que descubram sua verdadeira natureza"),
            ],
        ),
        (
            "furtividade",
            "Talentos de Furtividade",
            "furtividade",
            [
                ("Contrabandista Experiente", 1, "Treinado em Furtividade", "Oculta itens de forma mais eficaz contra observadores"),
                ("Esgueirador de Terreno", 1, "Treinado em Furtividade", "Se esgueira em certos terrenos sem fazer um teste"),
                ("Aliados Quietos", 2, "Especialista em Furtividade", "Rola um único teste de Furtividade quando se esgueira com aliados"),
                ("Enganar Sentidos", 7, "Mestre em Furtividade", "Toma precauções contra sentidos especiais"),
                ("Esgueirar-se Rapidamente", 7, "Mestre em Furtividade", "Se move à sua Velocidade total enquanto Esgueira"),
                ("Esgueirador Lendário", 15, "Lendário em Furtividade, Esgueirar-se Rapidamente", "Esconde e Esgueira sem cobertura ou sem estar ocultado"),
            ],
        ),
        (
            "intimidacao",
            "Talentos de Intimidação",
            "intimidacao",
            [
                ("Coagir Grupo", 1, "Treinado em Intimidação", "Coage vários alvos simultaneamente"),
                ("Coerção Rápida", 1, "Treinado em Intimidação", "Coage uma criatura rapidamente"),
                ("Olhar Intimidante", 1, "Treinado em Intimidação", "Desmoraliza uma criatura sem precisar falar"),
                ("Coerção Duradoura", 2, "Especialista em Intimidação", "Coage um alvo a ajudá-lo por mais tempo"),
                ("Intrepidez Intimidante", 2, "Força 16, Especialista em Intimidação", "Recebe um bônus para Desmoralizar fisicamente"),
                ("Brado de Batalha", 7, "Mestre em Intimidação", "Desmoraliza adversários quando rola sua iniciativa"),
                ("Retirada Aterrorizada", 7, "Mestre em Intimidação", "Faz adversários Desmoralizados por você fugirem"),
                ("Matar de Medo", 15, "Lendário em Intimidação", "Assusta tanto um alvo, que pode até matá-lo"),
            ],
        ),
        (
            "ladroagem",
            "Talentos de Ladroagem",
            "ladroagem",
            [
                ("Furto Súbito", 1, "Treinado em Ladroagem", "Seus furtos são mais difíceis de perceber"),
                ("Punga", 1, "Treinado em Ladroagem", "Furta ou Empalma um Objeto de forma mais eficaz"),
                ("Desarmamento Prudente", 2, "Especialista em Ladroagem", "+2 na CA ou salvamentos contra dispositivos ou armadilhas que acionar enquanto estiver desarmando-os"),
                ("Destrancar Rapidamente", 7, "Mestre em Ladroagem", "Abre uma Fechadura com 1 ação"),
                ("Ladrão Lendário", 15, "Lendário em Ladroagem, Punga", "Rouba algo que normalmente seria impossível"),
            ],
        ),
        (
            "manufatura",
            "Talentos de Manufatura",
            "manufatura",
            [
                ("Especialidade de Manufatura", 1, "Treinado em Manufatura", "Recebe bônus para Manufaturar certos itens"),
                ("Manufatura Alquímica", 1, "Treinado em Manufatura", "Manufatura itens alquímicos"),
                ("Manufatura de Arapuca", 1, "Treinado em Manufatura", "Manufatura arapucas"),
                ("Reparo Rápido", 1, "Treinado em Manufatura", "Repara itens rapidamente"),
                ("Manufatura Mágica", 2, "Especialista em Manufatura", "Manufatura itens mágicos"),
                ("Inventor", 7, "Mestre em Manufatura", "Usa Manufatura para criar fórmulas de itens"),
                ("Manufatura Impecável", 7, "Mestre em Manufatura, Especialidade de Manufatura", "Manufatura itens de forma mais eficaz"),
                ("Manufaturar Qualquer Coisa", 15, "Lendário em Manufatura", "Ignora a maioria dos requerimentos para manufaturar"),
            ],
        ),
        (
            "medicina",
            "Talentos de Medicina",
            "medicina",
            [
                ("Medicina de Batalha", 1, "Treinado em Medicina", "Cura a si ou um aliado em batalha"),
                ("Médico de Enfermaria", 2, "Especialista em Medicina", "Trata vários pacientes de uma vez"),
                ("Recuperação Contínua", 2, "Especialista em Medicina", "Trata Ferimentos em um paciente com maior frequência"),
                ("Recuperação Robusta", 2, "Especialista em Medicina", "Benefícios melhores de Tratar Doença ou Tratar Veneno"),
                ("Médico Lendário", 15, "Lendário em Medicina", "Remove doenças ou a condição cego, condenado, drenado ou surdo"),
            ],
        ),
        (
            "natureza",
            "Talentos de Natureza",
            "natureza",
            [
                ("Medicina Natural", 1, "Treinado em Natureza", "Utiliza Natureza para Tratar Ferimentos"),
                ("Treinar Animal", 1, "Treinado em Natureza", "Ensina um truque para um animal"),
                ("Elo com Animal", 2, "Especialista em Natureza", "Um animal se torna permanentemente prestativo"),
            ],
        ),
        (
            "ocultismo",
            "Talentos de Ocultismo",
            "ocultismo",
            [
                ("Identificar Estranhezas", 1, "Treinado em Ocultismo", "+2 em testes de Ocultismo para Identificar Magia com certos traços"),
                ("Magia Bizarra", 7, "Mestre em Ocultismo", "Sua magia se torna mais difícil de identificar"),
            ],
        ),
        (
            "performance",
            "Talentos de Performance",
            "performance",
            [
                ("Artista Virtuoso", 1, "Treinado em Performance", "+1 com um certo tipo de performance"),
                ("Performance Fascinante", 1, "Treinado em Performance", "Performa para fascinar observadores"),
                ("Performance Impressionante", 1, "Treinado em Performance", "Impressiona com Performance"),
                ("Artista Lendário", 15, "Lendário em Performance, Artista Virtuoso", "Obtém reconhecimento por sua Performance"),
            ],
        ),
        (
            "religiao",
            "Talentos de Religião",
            "religiao",
            [
                ("Estudante do Cânone", 1, "Treinado em Religião", "Reconhece melhor os princípios de sua fé ou filosofia"),
                ("Orientação Divina", 15, "Lendário em Religião", "Encontra orientação nas escritas de sua fé"),
            ],
        ),
        (
            "saber",
            "Talentos de Perícias de Saber",
            "saber",
            [
                ("Profissional Experiente", 1, "Treinado em Saber", "Impede falhas críticas quando Ganhar Proventos"),
                ("Saber Adicional", 1, "Treinado em Saber", "Se torna treinado em outra subcategoria de Saber"),
                ("Saber Inconfundível", 2, "Especialista em Saber", "Recorda Conhecimento de Saber de forma mais eficaz"),
                ("Profissional Lendário", 15, "Lendário em Saber", "Obtém reconhecimento por seu Saber"),
            ],
        ),
        (
            "sobrevivencia",
            "Talentos de Sobrevivência",
            "sobrevivencia",
            [
                ("Especialidade em Terreno", 1, "Treinado em Sobrevivência", "+1 em testes de Sobrevivência em certos terrenos"),
                ("Forrageador", 1, "Treinado em Sobrevivência", "Forrageia por suprimentos para várias criaturas"),
                ("Procurar Vida Selvagem", 1, "Treinado em Sobrevivência", "Identifica criaturas próximas através de pistas e sinais"),
                ("Rastreador Experiente", 1, "Treinado em Sobrevivência", "Rastreia à sua Velocidade total com –5 de penalidade"),
                ("Sobrevivência Planar", 7, "Mestre em Sobrevivência", "Utiliza Sobrevivência para Subsistir em planos diferentes"),
                ("Sobrevivente Lendário", 15, "Lendário em Sobrevivência", "Sobrevive a condições extremas"),
            ],
        ),
        (
            "sociedade",
            "Talentos de Sociedade",
            "sociedade",
            [
                ("Gracejos da Corte", 1, "Treinado em Sociedade", "Utiliza Sociedade para se relacionar na sociedade nobre"),
                ("Ler Lábios", 1, "Treinado em Sociedade", "Lê os lábios de pessoas que pode ver"),
                ("Língua de Sinais", 1, "Treinado em Sociedade", "Aprende língua de sinais"),
                ("Manha das Ruas", 1, "Treinado em Sociedade", "Utiliza Sociedade para Obter Informação e Recordar Conhecimento"),
                ("Poliglota", 1, "Treinado em Sociedade", "Aprende dois idiomas novos"),
                ("Conexões", 2, "Especialista em Sociedade, Gracejos da Corte", "Utiliza suas conexões para conseguir favores e reuniões"),
                ("Decodificador Lendário", 15, "Lendário em Sociedade", "Decifra Escrita mais rapidamente utilizando Sociedade"),
                ("Linguista Lendário", 15, "Lendário em Sociedade, Poliglota", "Cria idiomas de contato para se comunicar"),
            ],
        ),
    ]

    resultado: list[dict[str, Any]] = []
    for grupo_id, titulo, pericia_id, entradas in grupos:
        resultado.append(
            {
                "grupo_id": grupo_id,
                "titulo": titulo,
                "pericia_id": pericia_id,
                "talentos": [
                    construir_entrada_tabela(nome, nivel, pre_req, benef)
                    for nome, nivel, pre_req, benef in entradas
                ],
            }
        )
    return resultado


def construir_talentos_a_e() -> list[dict[str, Any]]:
    return [
        construir_talento(
            "Aliados Quietos",
            2,
            ["Geral", "Perícia"],
            "Você é habilidoso em se mover com um grupo. Quando estiver Evitando Ser Percebido e seus aliados Seguirem o Especialista, você e esses aliados podem rolar um único teste de Furtividade utilizando o menor modificador, em vez de rolar separadamente. Isto não se aplica a rolagens de iniciativa.",
            pre_requisitos="especialista em Furtividade",
        ),
        construir_talento(
            "Ancestralidade Adotada",
            1,
            ["Geral"],
            "Você é completamente imerso na cultura e tradições de outra ancestralidade, seja por ter nascido nela, obtido essa familiaridade através de um rito de passagem ou se vinculado através de uma grande amizade ou romance. Escolha uma ancestralidade comum. Você pode selecionar os talentos de ancestralidade da ancestralidade escolhida com este talento além dos talentos de sua própria ancestralidade, desde que não exijam quaisquer características fisiológicas que você não possua (conforme determinado pelo MJ).",
        ),
        construir_talento(
            "Artista Lendário",
            15,
            ["Geral", "Perícia"],
            "Sua fama se espalhou pelas terras. PdMs que obtiverem sucesso em um teste de Sociedade CD 10 para Recordar Conhecimento já ouviram falar de você e normalmente possuem uma atitude em relação a você um passo melhor do que o normal, dependendo de sua reputação e da disposição do PdM. Por exemplo: se você for reconhecido por crueldade e comportamento exigente, criaturas podem se sentir intimidadas em vez de amistosas. Quando Ganhar Proventos com Performance, você atrai uma audiência de nível superior à que o local permitiria, já que elas se deslocam para assisti-lo. Por exemplo: governantes e anjos podem viajar para sua pequena torre na mata para ouvi-lo tocar. Tipicamente, isto aumenta as audiências disponíveis em 2 níveis ou mais, determinado pelo MJ.",
            pre_requisitos="lendário em Performance, Artista Virtuoso",
        ),
        construir_talento(
            "Artista Virtuoso",
            1,
            ["Geral", "Perícia"],
            "Você possui talento excepcional com um tipo de performance. Você recebe +1 de bônus de circunstância quando realizar um determinado tipo de performance. Se você for mestre em Performance, este bônus aumenta para +2. Selecione uma das especialidades a seguir e aplique o bônus quando realizar testes de Performance desse tipo. Se não for claro quando uma especialidade se aplica, o MJ decide.",
            pre_requisitos="treinado em Performance",
            opcoes_tabela=[
                {"especialidade": "Atuação", "exemplo": "Drama, marionetes, pantomima"},
                {"especialidade": "Canto", "exemplo": "Balada, cântico, melodia, rimas"},
                {"especialidade": "Comédia", "exemplo": "Bobice, contar piadas, limeriques"},
                {"especialidade": "Cordas", "exemplo": "Alaúde, harpa, viola, violino"},
                {"especialidade": "Dança", "exemplo": "Balé, hulara, jig, macru"},
                {"especialidade": "Oratória", "exemplo": "Épico, narrativa, ode, poesia"},
                {"especialidade": "Percussão", "exemplo": "Carrilhão, gongo, tambor, xilofone"},
                {"especialidade": "Sopro", "exemplo": "Flauta, flauta doce, gaita de fole, trombeta"},
                {"especialidade": "Teclados", "exemplo": "Cravo, órgão, piano"},
            ],
        ),
        construir_talento(
            "Atalho Mágico",
            2,
            ["Geral", "Perícia"],
            "Você tem facilidade em aprender magias. Se for especialista na tradição associada à perícia, você leva 10 minutos por nível de magia para aprender uma magia dessa tradição em vez de 1 hora por nível de magia. Se falhar em aprender a magia, você pode tentar novamente após 1 semana ou após ganhar um nível, o que ocorrer primeiro. Se for mestre na tradição associada à perícia, aprender a magia leva 5 minutos por nível de magia e, se for lendário, leva apenas 1 minuto por nível de magia. Você pode usar recesso para aprender e escrever novas magias. Isto funciona como se estivesse usando Ganhar Proventos com a perícia associada à tradição, mas em vez de ganhar dinheiro, você escolhe uma magia disponível para aprender e ganha um desconto para aprendê-la, aprendendo-a gratuitamente se seu ganho de proventos igualar ou exceder o custo dela.",
            pre_requisitos="especialista em Arcanismo, Natureza, Ocultismo ou Religião",
        ),
        construir_talento(
            "Bloqueio com Escudo",
            1,
            ["Geral"],
            "Você posiciona seu escudo na frente de um golpe para bloqueá-lo. Seu escudo o impede de sofrer uma quantidade de dano igual à dureza do escudo. Tanto você quanto o escudo sofrem o dano remanescente (ambos sofrem o mesmo dano), o que pode quebrar ou até mesmo destruir o escudo.",
            acoes="reacao",
            acionamento="Enquanto estiver com seu escudo erguido, você sofreria dano de um ataque físico.",
        ),
        construir_talento(
            "Brado de Batalha",
            7,
            ["Geral", "Perícia"],
            "Quando rolar iniciativa, você pode gritar um poderoso brado de batalha e Desmoralizar um adversário observado como uma ação livre. Se for lendário em Intimidação, você pode usar uma reação para Desmoralizar seu adversário quando obtiver sucesso crítico em uma rolagem de ataque.",
            pre_requisitos="mestre em Intimidação",
        ),
        construir_talento(
            "Camarada",
            1,
            ["Geral", "Perícia"],
            "Você é habilidoso em descobrir informações através de conversa. Você pode usar a atividade de exploração Obter Informação em metade do tempo normal (geralmente reduzindo o tempo necessário para 1 hora). Se você for mestre em Diplomacia e decidir Obter Informação na velocidade normal, quando o fizer e rolar uma falha crítica, trate o resultado como uma falha. Contudo, ainda não há garantia de que um rumor que você descubra com Obter Informação seja preciso.",
            pre_requisitos="treinado em Diplomacia",
        ),
        construir_talento(
            "Carregador Robusto",
            1,
            ["Geral", "Perícia"],
            "Você pode carregar mais do que sua estrutura indica. Aumente seus limites de Volume máximo e sobrecarregado em 2 pontos.",
            pre_requisitos="treinado em Atletismo",
        ),
        construir_talento(
            "Cavalgar",
            1,
            ["Geral"],
            "Quando Comandar um Animal em que estiver montado para realizar uma ação de movimento (como Andar), você obtém sucesso automaticamente em vez de precisar fazer um teste. Qualquer animal em que você estiver montado age em seu turno, como um lacaio. Se você Montar um animal no meio de um encontro, ele pula o próximo turno dele e age somente em seu próximo turno. A página 250 possui mais informações sobre Comandar um Animal.",
        ),
        construir_talento(
            "Certeza",
            1,
            ["Fortuna", "Geral", "Perícia"],
            "Mesmo nas piores circunstâncias, você pode realizar tarefas básicas. Escolha uma perícia na qual é treinado. Você pode abrir mão de rolar um teste de perícia para essa perícia e em vez disso obter um resultado de 10 + seu bônus de proficiência (não aplique quaisquer outros bônus, penalidades ou modificadores).",
            pre_requisitos="treinado em pelo menos uma perícia",
            especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, escolha uma perícia diferente e receba os benefícios para essa perícia.",
        ),
        construir_talento(
            "Coagir Grupo",
            1,
            ["Geral", "Perícia"],
            "Quando Coagir, você pode comparar o resultado de seu teste de Intimidação às CDs de Vontade de dois alvos em vez de um. É possível obter um grau de sucesso diferente para cada alvo. A quantidade de alvos que você pode Coagir em uma única ação aumenta para quatro se você for especialista, 10 se for mestre e 25 se for lendário.",
            pre_requisitos="treinado em Intimidação",
        ),
        construir_talento(
            "Coerção Duradoura",
            2,
            ["Geral", "Perícia"],
            "Quando obtiver sucesso em Coagir alguém, o tempo máximo que ele consente aumenta para uma semana (embora ainda seja determinado pelo MJ). Se você for lendário, o máximo aumenta para um mês.",
            pre_requisitos="especialista em Intimidação",
        ),
        construir_talento(
            "Coerção Rápida",
            1,
            ["Geral", "Perícia"],
            "Você pode ameaçar os outros com a simples implicação de algumas escolhas. Você pode Coagir uma criatura após 1 rodada de conversa em vez de 1 minuto. Você ainda não pode Coagir uma criatura no meio do combate, ou sem engajar em uma conversa.",
            pre_requisitos="treinado em Intimidação",
        ),
        construir_talento(
            "Conexões",
            2,
            ["Geral", "Perícia"],
            "Você possui conexões sociais que pode usar para trocar favores ou encontrar pessoas importantes. Quando estiver em uma área com conexões (tipicamente um assentamento onde passou tempo em recesso formando conexões ou possivelmente outra área na mesma nação), você pode realizar um teste de Sociedade para arranjar um encontro com uma figura política importante ou pedir por um favor em troca de um favor posterior à escolha de seu contato. O MJ decide a CD baseado na dificuldade do favor e da proeminência da figura.",
            pre_requisitos="especialista em Sociedade, Gracejos da Corte",
        ),
        construir_talento(
            "Confabulador",
            2,
            ["Geral", "Perícia"],
            "Mesmo quando pego em suas inverdades, você joga mentira após mentira. Reduza o bônus de circunstância que um alvo recebe por suas tentativas prévias de Criar uma Distração ou Mentir de +4 para +2. Se você for mestre em Dissimulação, reduza o bônus para +1 e, se for lendário em Dissimulação, seus alvos não recebem quaisquer desses bônus.",
            pre_requisitos="especialista em Dissimulação",
        ),
        construir_talento(
            "Conhecimento Automático",
            2,
            ["Geral", "Perícia"],
            "Você recorda fatos básicos prontamente. Escolha uma perícia na qual seja especialista que tenha a ação Recordar Conhecimento e para a qual você possui o talento Certeza. Você pode usar a ação Recordar Conhecimento com essa perícia como uma ação livre uma vez por rodada. Se o fizer, você deve usar Certeza no teste de perícia.",
            pre_requisitos="especialista em uma perícia com a ação Recordar Conhecimento, Certeza nessa perícia",
            especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, escolha uma perícia diferente. Você pode usar Conhecimento Automático com quaisquer perícias que tiver escolhido, mas ainda pode usar Conhecimento Automático somente uma vez por rodada.",
        ),
        construir_talento(
            "Conhecimento Duvidoso",
            1,
            ["Geral", "Perícia"],
            "Você tem praticamente um tesouro de informações, mas nem todas vêm de fontes confiáveis. Quando falhar em Recordar Conhecimento usando qualquer perícia, você recorda um pouco de conhecimento verdadeiro e um pouco de conhecimento errôneo, mas não tem qualquer forma de diferenciar qual é cada um.",
            pre_requisitos="treinado em uma perícia com a ação Recordar Conhecimento",
        ),
        construir_talento(
            "Contrabandista Experiente",
            1,
            ["Geral", "Perícia"],
            "Você frequentemente contrabandeia coisas pelas autoridades. Quando o MJ rolar seu teste de Furtividade para um observador passivo perceber um item pequeno que você tenha ocultado, ele usa o número rolado ou 10 — o que for maior — como resultado de sua rolagem de dado, adicionando-o ao seu modificador de Furtividade para determinar o resultado de seu teste. Se você for mestre em Furtividade, o MJ usa o número rolado ou 15 e, se for lendário em Furtividade, você automaticamente obtém sucesso em esconder um item pequeno ocultado de observadores passivos. Isto não fornece benefícios quando uma criatura faz um teste de Percepção enquanto procura ativamente em você para encontrar itens escondidos. Devido à sua perícia em contrabando, você tem mais facilidade em encontrar trabalhos de contrabando mais lucrativos quando usar Saber de Submundo para Ganhar Proventos.",
            pre_requisitos="treinado em Furtividade",
        ),
        construir_talento(
            "Controlar a Respiração",
            1,
            ["Geral"],
            "Você possui um controle incrível sobre sua respiração, o que lhe concede vantagens onde o ar seja perigoso ou escasso. Você pode prender sua respiração por 25 vezes o tempo usual antes de sufocar. Você recebe +1 de bônus de circunstância em jogadas de salvamento contra ameaças inaladas (como venenos inalados) e, se rolar um sucesso numa jogada de salvamento dessas, trate o resultado como um sucesso crítico.",
        ),
        construir_talento(
            "Cumprimento Caloroso",
            2,
            ["Geral", "Perícia"],
            "A primeira impressão é seu ponto forte. Quando encontrar alguém em uma situação casual ou social, você pode imediatamente fazer um teste de Diplomacia para Impressionar essa criatura em vez de precisar conversar por 1 minuto. Você sofre –5 de penalidade no teste. Se falhar ou falhar criticamente, você pode engajar em 1 minuto de conversa e fazer um novo teste ao final desse período em vez de aceitar o resultado da falha ou falha crítica.",
            pre_requisitos="especialista em Diplomacia",
        ),
        construir_talento(
            "Decodificador Lendário",
            15,
            ["Geral", "Perícia"],
            "Sua competência com idiomas e códigos é tão grande que você pode decifrar informações com pouco mais do que uma leitura rápida de um texto. Você pode Decifrar Escrita utilizando Sociedade enquanto lê em velocidade normal. Se desacelerar e gastar a quantidade de tempo total normalmente necessária e rolar um sucesso, trate o resultado como um sucesso crítico; se você obtiver um sucesso crítico enquanto gasta a quantidade normal de tempo, você obtém uma compreensão quase palavra por palavra do documento.",
            pre_requisitos="lendário em Sociedade",
        ),
        construir_talento(
            "Desarmamento Prudente",
            2,
            ["Geral", "Perícia"],
            "Se acionar um dispositivo ou ativar uma armadilha enquanto estiver desarmando-a, você recebe +2 de bônus de circunstância na CA ou jogada de salvamento contra o dispositivo ou armadilha. Isto se aplica somente para ataques ou efeitos acionados por sua tentativa falha, não para rolagens posteriores (como ataques adicionais de uma armadilha complexa).",
            pre_requisitos="especialista em Ladroagem",
        ),
        construir_talento(
            "Destrancar Rapidamente",
            7,
            ["Geral", "Perícia"],
            "Você pode Abrir uma Fechadura usando 1 ação em vez de 2.",
            pre_requisitos="mestre em Ladroagem",
        ),
        construir_talento(
            "Disfarce Rápido",
            2,
            ["Geral", "Perícia"],
            "Você pode montar um Disfarce na metade do tempo normal (geralmente 5 minutos). Se for mestre em Dissimulação, você leva um décimo do tempo normal (normalmente 1 minuto). Se for lendário, você pode criar um disfarce completo e Personificar como uma atividade de 3 ações.",
            pre_requisitos="especialista em Dissimulação",
        ),
        construir_talento(
            "Distração Prolongada",
            1,
            ["Geral", "Perícia"],
            "Quando obtiver um sucesso crítico para Criar uma Distração, você permanece escondido após o final do seu turno. Este efeito dura uma quantidade de tempo que depende da distração e situação, conforme determinado pelo MJ (mínimo 1 rodada adicional).",
            pre_requisitos="treinado em Dissimulação",
        ),
        construir_talento(
            "Duro de Matar",
            1,
            ["Geral"],
            "Você é mais difícil de ser morto do que a maioria. Você só morre quando o valor de sua condição morrendo chegar a 5 (em vez de morrendo 4).",
        ),
        construir_talento(
            "Elo com Animal",
            2,
            ["Geral", "Perícia", "Recesso"],
            "Você forja fortes conexões com um animal. Você pode gastar 7 dias de recesso tentando ligar-se a um animal normal (não um companheiro animal ou outro animal especial). Após esta duração, faça um teste de Natureza CD 20. Se bem-sucedido, você cria um elo com o animal. O animal fica permanentemente prestativo para você, a menos que você faça algo notório para quebrar o elo. Um animal prestativo é mais fácil de direcionar, conforme descrito sob Comandar um Animal na página 250. Criar um elo com um novo animal encerra qualquer elo prévio que você possuir. Você não pode ter um elo com animal e um companheiro animal (embora possa ter um elo com animal e um familiar).",
            pre_requisitos="especialista em Natureza",
        ),
        construir_talento(
            "Enganar Item Mágico",
            1,
            ["Geral", "Manuseio", "Perícia"],
            "Você examina um item mágico que normalmente não poderia usar em um esforço para enganá-lo e ativá-lo temporariamente. Por exemplo: com isto, um guerreiro pode conjurar uma magia de uma varinha ou um mago pode conjurar uma magia que não está na lista arcana dele usando um pergaminho. Você deve saber o que ocorre ao ativar o item, caso contrário, é incapaz de enganá-lo. Faça um teste utilizando a perícia apropriada à tradição do item mágico ou, se estiver tentando conjurar uma magia do item, à tradição que possua a magia em sua lista. As perícias relevantes são Arcanismo para magia arcana, Natureza para magia primal, Ocultismo para magia ocultista, Religião para magia divina ou qualquer uma das quatro perícias para um item que tenha o traço mágico, mas nenhum traço de tradição. O MJ determina a CD baseado no nível do item (possivelmente ajustada dependendo do item ou situação). Se você ativar um item mágico que requer uma rolagem de ataque de magia ou CD de magia e não possuir a habilidade de conjurar magias da tradição relevante, utilize seu nível como bônus de proficiência e o maior de seus modificadores entre Inteligência, Sabedoria ou Carisma. Se você for mestre na perícia apropriada para a tradição do item, em vez disso utilize o bônus de proficiência treinado e, se for lendário, utilize o bônus de proficiência de especialista.",
            acoes="1",
            pre_requisitos="treinado em Arcanismo, Natureza, Ocultismo ou Religião",
            resultados={
                "sucesso": "Pelo resto de seu turno atual, você pode gastar ações para ativar o item como se pudesse fazê-lo normalmente.",
                "falha": "Você não pode usar o item ou tentar enganá-lo novamente neste turno, mas pode tentar novamente em turnos subsequentes.",
                "falha_critica": "Você não pode usar o item e não pode tentar enganá-lo novamente até suas próximas preparações diárias.",
            },
        ),
        construir_talento(
            "Enganar Sentidos",
            7,
            ["Geral", "Perícia"],
            "Você é perito em enganar os sentidos especiais de criaturas e cauteloso o suficiente para se prevenir contra eles a todo momento. Sempre que usar as ações Esconder, Esgueirar ou Evitar Ser Percebido, você sempre é considerado como tomando precauções contra sentidos especiais (veja o quadro Detectando com Outros Sentidos, na página 465).",
            pre_requisitos="mestre em Furtividade",
        ),
        construir_talento(
            "Equilíbrio Estável",
            1,
            ["Geral", "Perícia"],
            "Você consegue manter seu equilíbrio facilmente, mesmo em condições adversas. Sempre que rolar um sucesso usando a ação Equilibrar, trate o resultado como um sucesso crítico. Você não fica desprevenido enquanto tenta se Equilibrar em superfícies estreitas e solo irregular. Graças ao seu equilíbrio incrível, você pode utilizar Acrobatismo em vez de Reflexos para Segurar numa Beirada.",
            pre_requisitos="treinado em Acrobatismo",
        ),
        construir_talento(
            "Escalada Rápida",
            7,
            ["Geral", "Perícia"],
            "Quando Escalar, você se move 1,5 metros a mais em um sucesso e 3 metros a mais em um sucesso crítico (até o máximo de sua Velocidade). Se for lendário em Atletismo, você recebe uma Velocidade de escalada igual à sua Velocidade.",
            pre_requisitos="mestre em Atletismo",
        ),
        construir_talento(
            "Escalador de Combate",
            1,
            ["Geral", "Perícia"],
            "Suas técnicas permitem que você lute enquanto escala. Você não fica desprevenido enquanto Escala e pode Escalar com uma mão ocupada. Você ainda deve usar uma outra mão e ambas as pernas para Escalar.",
            pre_requisitos="treinado em Atletismo",
        ),
        construir_talento(
            "Esgueirador de Terreno",
            1,
            ["Geral", "Perícia"],
            "Selecione um tipo de terreno difícil da lista a seguir: detritos, matagal ou neve. Enquanto estiver indetectado por todos não-aliados nesse tipo de terreno, você pode Esgueirar sem fazer um teste de Furtividade desde que não se mova mais do que 1,5 metros e não se aproxime a 3 metros ou menos de um inimigo durante seu movimento. Este talento também permite que você se aproxime automaticamente de criaturas a até 4,5 metros enquanto Evitar Ser Percebido durante a exploração, desde que elas não estejam ativamente Procurando ou em guarda.",
            pre_requisitos="treinado em Furtividade",
            especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você deve escolher um tipo de terreno diferente.",
        ),
        construir_talento(
            "Esgueirador Lendário",
            15,
            ["Geral", "Perícia"],
            "Você sempre está se esgueirando a menos que escolha ser visto, mesmo quando não houver onde se esconder. Você pode Esconder-se e Esgueirar mesmo sem cobertura ou sem estar ocultado. Quando empregar uma tática de exploração diferente de Evitar Ser Percebido, você também recebe os benefícios de Evitar Ser Percebido a menos que escolha não fazê-lo. Veja a página 479 para mais informações sobre táticas de exploração.",
            pre_requisitos="lendário em Furtividade, Esgueirar-se Rapidamente",
        ),
        construir_talento(
            "Esgueirar-se Rapidamente",
            7,
            ["Geral", "Perícia"],
            "Você pode mover-se sua Velocidade total quando Esgueirar. Você pode usar Esgueirar-se Rapidamente enquanto Escalar, Escavar, Nadar ou Voar em vez de Andar se possuir o tipo de movimento correspondente.",
            pre_requisitos="mestre em Furtividade",
        ),
        construir_talento(
            "Especialidade de Manufatura",
            1,
            ["Geral", "Perícia"],
            "Seu treinamento focou em Manufaturar um tipo particular de item. Selecione uma das especialidades listadas na tabela; você recebe +1 de bônus de circunstância em testes de Manufatura para Manufaturar itens desse tipo. Se você for mestre em Manufatura, este bônus aumenta para +2. Se não for claro quando uma especialidade se aplica, o MJ decide. Algumas especialidades podem se aplicar apenas parcialmente. Por exemplo: se estiver criando uma maça-estrela e possuir especialidade em carpintaria, o MJ pode lhe dar metade de seu bônus devido ao item requerer carpintaria e ferraria.",
            pre_requisitos="treinado em Manufatura",
            opcoes_tabela=[
                {"especialidade": "Alfaiataria", "itens_aplicaveis": "Roupas"},
                {"especialidade": "Alquimia*", "itens_aplicaveis": "Itens alquímicos (como elixires). *Você deve possuir o talento de perícia Manufatura Alquímica para Manufaturar itens alquímicos."},
                {"especialidade": "Alvenaria", "itens_aplicaveis": "Bens de pedra e estruturas"},
                {"especialidade": "Arte", "itens_aplicaveis": "Artes finas, incluindo joalheria"},
                {"especialidade": "Carpintaria", "itens_aplicaveis": "Bens de madeira e estruturas"},
                {"especialidade": "Carpintaria naval", "itens_aplicaveis": "Navios e barcos"},
                {"especialidade": "Curtume", "itens_aplicaveis": "Bens de couro, incluindo armaduras de couro"},
                {"especialidade": "Encadernação", "itens_aplicaveis": "Livros e papéis"},
                {"especialidade": "Ferraria", "itens_aplicaveis": "Bens metálicos duráveis, incluindo armaduras"},
                {"especialidade": "Olaria", "itens_aplicaveis": "Bens de cerâmica"},
                {"especialidade": "Tecelagem", "itens_aplicaveis": "Tecidos, cestos e tapetes"},
                {"especialidade": "Vidraçaria", "itens_aplicaveis": "Vidro, incluindo vitrais e janelas"},
            ],
        ),
        construir_talento(
            "Especialidade em Terreno",
            1,
            ["Geral", "Perícia"],
            "Sua experiência em viajar por um determinado tipo de terreno lhe torna extremamente confiante ao fazê-lo. Você recebe +1 de bônus de circunstância em testes de Sobrevivência em um dos seguintes tipos de terreno, escolhido ao selecionar este talento: aquático, ártico, céu, deserto, floresta, montanha, pântano, planície ou subterrâneo.",
            pre_requisitos="treinado em Sobrevivência",
            especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você deve escolher um tipo de terreno diferente.",
        ),
        construir_talento(
            "Espremer-se Rapidamente",
            1,
            ["Geral", "Perícia"],
            "Você se Espreme 1,5 metros por rodada (3 metros em um sucesso crítico). Se for lendário em Acrobatismo, você se Espreme à Velocidade total.",
            pre_requisitos="treinado em Acrobatismo",
        ),
        construir_talento(
            "Estudante do Cânone",
            1,
            ["Geral", "Perícia"],
            "Você pesquisou muitas fés e religiões e, por isso, é capaz de reconhecer noções religiosas imprecisas ou errôneas. Se rolar uma falha crítica em um teste de Religião para Decifrar uma Escrita de natureza religiosa ou para Recordar Conhecimento sobre os princípios de religiões, trate o resultado como uma falha. Quando tentar Recordar Conhecimento sobre os princípios de sua própria fé, se rolar uma falha crítica, trate o resultado como uma falha e, se rolar um sucesso, trate o resultado como um sucesso crítico.",
            pre_requisitos="treinado em Religião",
        ),
        construir_talento(
            "Exemplar Ancestral",
            3,
            ["Geral"],
            "Através de instinto, estudo ou magia, você sente uma conexão mais profunda com sua ancestralidade. Você recebe um talento de ancestralidade de 1º nível.",
        ),
    ]


def construir_talentos_f_p() -> list[dict[str, Any]]:
    return [
        construir_talento(
            "Forrageador",
            1,
            ["Geral", "Perícia"],
            "Enquanto utilizar Sobrevivência para Subsistir, se rolar qualquer resultado pior que um sucesso, você obtém um sucesso. Se rolar um sucesso, você pode fornecer subsistência para si mesmo e quatro criaturas adicionais. Se rolar um sucesso crítico, você pode cuidar do dobro de criaturas que poderia em um sucesso. Cada vez que sua graduação de proficiência em Sobrevivência aumentar, dobre a quantidade de criaturas adicionais que você pode cuidar em um sucesso (para oito se for especialista, 16 se for mestre ou 32 se for lendário). Você pode escolher cuidar de metade da quantidade de criaturas adicionais e fornecer um padrão de vida confortável em vez de simples subsistência. Várias criaturas menores ou criaturas com apetites significativamente menores do que um humano contam como uma única criatura para este talento, e criaturas maiores ou com apetites maiores contam como várias criaturas. O MJ determina o quanto uma criatura não-humana precisa comer.",
            pre_requisitos="treinado em Sobrevivência",
        ),
        construir_talento(
            "Furto Súbito",
            1,
            ["Geral", "Perícia"],
            "Quando obtiver sucesso em Furtar algo, observadores (criaturas diferentes da que está sendo furtada) sofrem –2 de penalidade de circunstância em suas CDs de Percepção para detectar seu furto. Adicionalmente, se você Criar uma Distração utilizando Dissimulação antes de usar uma ação para Empalmar um Objeto ou Furtar, essa última ação não encerra sua condição indetectado.",
            pre_requisitos="treinado em Ladroagem",
        ),
        construir_talento(
            "Gracejos da Corte",
            1,
            ["Geral", "Perícia"],
            "Você foi criado entre a nobreza ou aprendeu a etiqueta e comportamento apropriados, permitindo que se apresente como um nobre e jogue com influências e políticas. Você pode utilizar Sociedade para Impressionar um nobre ou para Personificar fingindo ser um nobre se não for um. Se quiser personificar um nobre específico, você ainda precisa utilizar Dissimulação para Personificar normalmente e para Mentir quando necessário.",
            pre_requisitos="treinado em Sociedade",
        ),
        construir_talento(
            "Identificação Rápida",
            1,
            ["Geral", "Perícia"],
            "Você pode Identificar Magia rapidamente. Você leva somente 1 minuto em vez de 10 minutos quando usa Identificar Magia para determinar as propriedades de um efeito contínuo, item ou local. Se for mestre na perícia, você faz isso usando uma atividade de 3 ações e, se for lendário na perícia, usando somente 1 ação.",
            pre_requisitos="treinado em Arcanismo, Natureza, Ocultismo ou Religião",
        ),
        construir_talento(
            "Identificar Estranhezas",
            1,
            ["Geral", "Perícia"],
            "Você possui um sentido para magias que distorcem mentes ou revelam segredos. Você recebe +2 de bônus de circunstância em testes de Ocultismo para Identificar Magias que possuam os traços mental, possessão, predição ou vidência.",
            pre_requisitos="treinado em Ocultismo",
        ),
        construir_talento(
            "Impressionar Grupo",
            1,
            ["Geral", "Perícia"],
            "Quando Impressionar, você pode comparar o resultado de seu teste de Diplomacia às CDs de Vontade de dois alvos em vez de um. É possível obter um grau de sucesso diferente para cada alvo. A quantidade de alvos que você pode Impressionar em uma única ação aumenta para quatro se você for especialista, 10 se for mestre e 25 se for lendário.",
            pre_requisitos="treinado em Diplomacia",
        ),
        construir_talento(
            "Improvisação Destreinada",
            3,
            ["Geral"],
            "Você aprendeu a lidar com situações que estejam fora do seu domínio. Seu bônus de proficiência para testes de perícia destreinados é igual à metade de seu nível em vez de +0. Se você for de 7º nível ou superior, o bônus se torna igual ao seu nível. Isto não permite usar as ações de perícia treinadas.",
        ),
        construir_talento(
            "Iniciativa Incrível",
            1,
            ["Geral"],
            "Você reage mais rapidamente do que os outros. Você recebe +2 de bônus de circunstância em rolagens de iniciativa.",
        ),
        construir_talento(
            "Intrepidez Intimidante",
            2,
            ["Geral", "Perícia"],
            "Em situações onde você pode ameaçar o alvo fisicamente ao Coagir ou Desmoralizar, você recebe +1 de bônus de circunstância em seu teste de Intimidação e ignora a penalidade por não compartilhar um idioma. Se seu valor de Força for 20 ou maior e você for mestre em Intimidação, este bônus aumenta para +2.",
            pre_requisitos="Força 16, especialista em Intimidação",
        ),
        construir_talento(
            "Inventor",
            7,
            ["Geral", "Perícia", "Recesso"],
            "Você é um gênio em Manufatura, facilmente capaz de determinar como as coisas são feitas e de criar novas invenções. Você pode usar recesso para inventar uma fórmula comum que não conheça. Isto funciona como a atividade Manufaturar: você gasta metade do Preço da fórmula adiantado, faz um teste de Manufatura e, em um sucesso, finaliza a fórmula pagando a diferença ou trabalhando por mais tempo para diminuir o Preço. A diferença é que você gasta o tempo adicional em pesquisa, projeto e desenvolvimento, em vez de criar um item. Após completá-la, você adiciona a nova fórmula inventada ao seu livro de fórmulas.",
            pre_requisitos="mestre em Manufatura",
        ),
        construir_talento(
            "Investidura Incrível",
            11,
            ["Geral"],
            "Você possui uma habilidade incrível para investir em mais itens mágicos. Aumente seu limite de itens investidos de 10 para 12.",
            pre_requisitos="Carisma 16",
        ),
        construir_talento(
            "Ladrão Lendário",
            15,
            ["Geral", "Perícia"],
            "Sua habilidade de Furtar desafia o possível. Você pode tentar Furtar algo que está sendo ativamente empunhado, que seria extremamente perceptível ou que consumisse tempo para remover (como sapatos calçados ou uma armadura vestida). Você deve fazê-lo lenta e cuidadosamente, gastando pelo menos 1 minuto (e significativamente mais tempo para itens que normalmente consomem tempo para remover, como armaduras). Durante toda esta duração, você deve ter meios de permanecer escondido, como a cobertura de escuridão ou uma multidão lotada. Você sofre –5 de penalidade em seu teste de Ladroagem. Mesmo se obtiver sucesso, se o item for extremamente notável — como uma armadura completa — seu sumiço será rapidamente notado por observadores após o furto.",
            pre_requisitos="lendário em Ladroagem, Punga",
        ),
        construir_talento(
            "Ler Lábios",
            1,
            ["Geral", "Perícia"],
            "Você pode ler os lábios de pessoas próximas que possa ver claramente. Em situações calmas ou comuns, você pode fazer isto automaticamente. Em modo de encontro ou quando tentar um feito mais difícil de leitura labial, você fica fascinado e desprevenido durante cada rodada que passar focando em movimentos de lábios e deve obter sucesso em um teste de Sociedade (CD determinada pelo MJ) para conseguir ler os lábios de alguém. Em ambos os casos, você deve conhecer o idioma para conseguir lê-lo. Se tiver problemas de audição (ou for surdo) e possuir Ler Lábios, você reconhece os movimentos labiais para a forma falada de seus idiomas. Você também pode falar a forma falada de seus idiomas de forma clara o suficiente para que outros possam entendê-lo.",
            pre_requisitos="treinado em Sociedade",
        ),
        construir_talento(
            "Levantar Rapidamente",
            7,
            ["Geral", "Perícia"],
            "Você se Levanta. Este movimento não aciona reações.",
            acoes="livre",
            pre_requisitos="mestre em Acrobatismo",
        ),
        construir_talento(
            "Língua de Sinais",
            1,
            ["Geral", "Perícia"],
            "Você aprende a língua de sinais associada com os idiomas que conhece, permitindo-lhe fazer e entender sinais. Línguas de sinais tipicamente requerem ambas as mãos para transmitir conceitos mais complexos, e são visuais em vez de auditivas. Língua de sinais é difícil de compreender durante o combate devido ao alto nível de atenção exigida, ao contrário de gestos básicos como apontar para um adversário ou sugerir um alvo. Língua de sinais é difícil de usar em áreas de baixa visibilidade, assim como a fala é difícil em um ambiente barulhento.",
            pre_requisitos="treinado em Sociedade",
        ),
        construir_talento(
            "Linguista Lendário",
            15,
            ["Geral", "Perícia"],
            "Você é tão competente com idiomas que consegue criar uma língua de contato instantaneamente. Você sempre pode falar com qualquer criatura que possua um idioma — mesmo um idioma que você não conhece — criando um novo idioma de contato que utiliza termos simplificados e transmite conceitos básicos. Para fazê-lo, você primeiro deve compreender pelo menos o meio de comunicação utilizado pela criatura (fala, língua de sinais e assim por diante).",
            pre_requisitos="lendário em Sociedade, Poliglota",
        ),
        construir_talento(
            "Lutador Titânico",
            1,
            ["Geral", "Perícia"],
            "Você pode tentar Agarrar, Derrubar, Desarmar ou Empurrar criaturas até dois tamanhos maior do que você, ou até três tamanhos maior do que o seu se você for lendário em Atletismo.",
            pre_requisitos="treinado em Atletismo",
        ),
        construir_talento(
            "Magia Bizarra",
            7,
            ["Geral", "Perícia"],
            "Você pode imbuir variações estranhas em sua conjuração, esteja conjurando magias ocultistas ou não. As CDs para Reconhecer Magias e Identificar Magias que você conjurar aumentam em 5 pontos.",
            pre_requisitos="mestre em Ocultismo",
        ),
        construir_talento(
            "Manha das Ruas",
            1,
            ["Geral", "Perícia"],
            "Você conhece a vida nas ruas e sente o ritmo de seu assentamento local. Você pode utilizar seu modificador de Sociedade em vez de seu modificador de Diplomacia para Obter Informação. Em qualquer assentamento que frequentar regularmente, você pode usar a ação Recordar Conhecimento com Sociedade para saber os mesmos tipos de informação que poderia descobrir com Diplomacia para Obter Informação. A CD normalmente é significativamente maior, mas você sabe a informação sem gastar tempo coletando-a. Se falhar em recordar a informação, você ainda pode tentar Obter Informação em seguida normalmente.",
            pre_requisitos="treinado em Sociedade",
        ),
        construir_talento(
            "Manufatura Alquímica",
            1,
            ["Geral", "Perícia"],
            "Você pode usar a atividade Manufaturar para criar itens alquímicos. Quando selecionar este talento, você imediatamente acrescenta as fórmulas para quatro itens alquímicos comuns de 1º nível ao seu livro de fórmulas.",
            pre_requisitos="treinado em Manufatura",
        ),
        construir_talento(
            "Manufatura de Arapuca",
            1,
            ["Geral", "Perícia"],
            "Você pode usar a atividade Manufaturar para criar arapucas, utilizando as regras da página 248. Quando selecionar este talento, você acrescenta as fórmulas para quatro arapucas comuns ao seu livro de fórmulas.",
            pre_requisitos="treinado em Manufatura",
        ),
        construir_talento(
            "Manufatura Impecável",
            7,
            ["Geral", "Perícia"],
            "Você manufatura criações impecáveis com grande eficiência. Sempre que rolar um sucesso em um teste de Manufatura para criar um item do tipo escolhido com Especialidade de Manufatura, trate o resultado como um sucesso crítico.",
            pre_requisitos="mestre em Manufatura, Especialidade de Manufatura",
        ),
        construir_talento(
            "Manufatura Mágica",
            2,
            ["Geral", "Perícia"],
            "Você pode Manufaturar itens mágicos, embora alguns tenham outros requerimentos, conforme listado no Capítulo 11. Quando selecionar este talento, você recebe fórmulas para quatro itens mágicos comuns de 2º nível ou inferior.",
            pre_requisitos="especialista em Manufatura",
        ),
        construir_talento(
            "Manufaturar Qualquer Coisa",
            15,
            ["Geral", "Perícia"],
            "Você pode encontrar formas de criar quase qualquer coisa, a despeito das restrições. Desde que tenha o talento de perícia de Manufatura apropriado (como Manufatura Mágica para itens mágicos) e atenda aos requerimentos de nível do item e proficiência, você ignora quase qualquer outro requerimento (como ser de uma ancestralidade específica ou fornecer magias). As únicas exceções são requerimentos que adicionam custos ao item, incluindo conjurações de magias que tenham um custo, e requerimentos de itens especiais (como a pedra filosofal) que possuam meios exclusivos de acesso e Manufatura. O MJ decide se você pode ignorar um requerimento.",
            pre_requisitos="lendário em Manufatura",
        ),
        construir_talento(
            "Matar de Medo",
            15,
            ["Emoção", "Geral", "Incapacitação", "Medo", "Morte", "Perícia"],
            "Você pode literalmente matar seu adversário de medo. Faça um teste de Intimidação contra a CD de Vontade de uma criatura viva a até 9 metros que você consiga sentir ou observar e que pode lhe sentir ou observar. Se o alvo não puder ouvi-lo ou não compreender o idioma que você está falando, você sofre –4 de penalidade de circunstância. A criatura fica temporariamente imune por 1 minuto.",
            acoes="1",
            pre_requisitos="lendário em Intimidação",
            resultados={
                "sucesso_critico": "O alvo deve obter sucesso em um salvamento de Fortitude contra sua CD de Intimidação ou morre. Se o alvo obtiver sucesso no salvamento dele, ele fica assustado 2 e fugindo por 1 rodada; ele não sofre efeito em um sucesso crítico.",
                "sucesso": "O alvo fica assustado 2.",
                "falha": "O alvo fica assustado 1.",
                "falha_critica": "O alvo não é afetado.",
            },
        ),
        construir_talento(
            "Medicina de Batalha",
            1,
            ["Cura", "Geral", "Manuseio", "Perícia"],
            "Você pode curar a si mesmo ou um aliado adjacente, mesmo em combate. Faça um teste de Medicina com a mesma CD de Tratar Ferimentos e forneça a quantidade correspondente de cura; usar este talento não remove a condição ferido. Da mesma forma que Tratar Ferimentos, você pode fazer teste contra CDs mais altas se possuir a graduação de proficiência mínima. O alvo fica temporariamente imune à sua Medicina de Batalha por 1 dia.",
            acoes="1",
            pre_requisitos="treinado em Medicina",
        ),
        construir_talento(
            "Medicina Natural",
            1,
            ["Geral", "Perícia"],
            "Você pode aplicar curativos naturais para curar seus aliados. Você pode utilizar Natureza em vez de Medicina para Tratar Ferimentos. Em terras ermas, você pode ter acesso mais fácil a ingredientes frescos, recebendo +2 de bônus de circunstância em seu teste para Tratar Ferimentos utilizando Natureza (sujeito ao julgamento do MJ).",
            pre_requisitos="treinado em Natureza",
        ),
        construir_talento(
            "Médico de Enfermaria",
            2,
            ["Geral", "Perícia"],
            "Você estudou em grandes enfermarias médicas, tratando vários pacientes de uma vez e cuidando de todas suas necessidades. Quando usar Tratar Doença ou Tratar Ferimentos, você pode tratar até dois alvos. Se for mestre em Medicina, você pode tratar até quatro alvos e, se for lendário em Medicina, pode tratar até oito alvos.",
            pre_requisitos="especialista em Medicina",
        ),
        construir_talento(
            "Médico Lendário",
            15,
            ["Geral", "Perícia"],
            "Você descobriu avanços ou técnicas médicas que possibilitam resultados milagrosos. Uma vez por dia para cada alvo, você pode gastar 1 hora tratando-o e fazer um teste de Medicina para remover uma doença ou a condição cego, condenado, drenado ou surdo. Utilize a CD da doença, magia ou efeito que criou a condição. Se a fonte do efeito for acima do 20º nível, um artefato ou algo de poder similar, aumente a CD em 10.",
            pre_requisitos="lendário em Medicina",
        ),
        construir_talento(
            "Mente na Minha Cara",
            1,
            ["Geral", "Perícia"],
            "Você pode utilizar Dissimulação para tecer armadilhas e pegar qualquer um tentando enganá-lo. Se puder conversar com alguém tentando Mentir para você, utilize sua CD de Dissimulação se for maior que sua CD de Percepção para determinar se esse alguém obtém sucesso. Isto não se aplica se você não for capaz de dialogar contra-argumentando, como quando alguém tenta Mentir durante um discurso longo.",
            pre_requisitos="treinado em Dissimulação",
        ),
        construir_talento(
            "Mentiroso Charmoso",
            1,
            ["Geral", "Perícia"],
            "Seu charme o permite persuadir pessoas através de suas mentiras. Quando obtiver um sucesso crítico usando a ação Mentir, a atitude do alvo em relação a você melhora em um passo, como se tivesse obtido sucesso em Diplomacia para Impressionar. Isto funciona somente uma vez por conversa, e se você tiver obtido um sucesso crítico contra vários alvos usando o mesmo resultado, escolha a atitude de uma única criatura para aprimorar. Você deve estar mentindo para contar uma informação aparentemente importante, inflar sua reputação ou se colocar nas graças de alguém — algo inalcançável com mentiras triviais e irrelevantes.",
            pre_requisitos="treinado em Dissimulação",
        ),
        construir_talento(
            "Natação Rápida",
            7,
            ["Geral", "Perícia"],
            "Quando Nadar, você se move 1,5 metros a mais em um sucesso e 3 metros a mais em um sucesso crítico, até o máximo de sua Velocidade. Se for lendário em Atletismo, você recebe uma Velocidade de natação igual à sua Velocidade.",
            pre_requisitos="mestre em Atletismo",
        ),
        construir_talento(
            "Negociação Lendária",
            15,
            ["Geral", "Perícia"],
            "Você pode negociar incrivelmente rápido em situações adversas. Você pode tentar Impressionar e então Pedir que seu oponente pare a atividade atual dele e engaje em negociações. Você sofre –5 de penalidade em seu teste de Diplomacia. O MJ determina a CD do Pedido baseado nas circunstâncias — isso normalmente possui uma CD pelo menos muito difícil do mesmo nível da criatura. Algumas criaturas podem simplesmente recusar, e mesmo criaturas que concordarem em negociar podem achar seus argumentos infundados e retornar à violência.",
            acoes="3",
            pre_requisitos="lendário em Diplomacia",
        ),
        construir_talento(
            "Olhar Intimidante",
            1,
            ["Geral", "Perícia"],
            "Você pode Desmoralizar com um mero olhar. Quando o fizer, Desmoralizar perde o traço auditivo e adquire o traço visual, e você não sofre uma penalidade se a criatura não compreender seu idioma.",
            pre_requisitos="treinado em Intimidação",
        ),
        construir_talento(
            "Orientação Divina",
            15,
            ["Geral", "Perícia"],
            "Você é tão imerso em escrituras divinas que encontra significado e orientação em seus textos para qualquer situação. Gaste 10 minutos Decifrando Escrita em escrituras religiosas de sua divindade ou filosofia enquanto pensa sobre um problema em particular ou questão difícil enfrentada por você, e depois faça um teste de Religião (CD determinada pelo MJ). Se obtiver sucesso, você descobre uma passagem, parábola ou aforismo relevante que pode lhe ajudar a seguir ou mudar seu pensamento para solucionar seu problema. Por exemplo: o MJ pode lhe fornecer uma dica ou poema enigmático que o guiará ao próximo passo para solucionar seu problema.",
            pre_requisitos="lendário em Religião",
        ),
        construir_talento(
            "Passo Aprumado",
            1,
            ["Geral"],
            "Você dá um passo de forma rápida e cuidadosa. Você pode Dar um Passo em terreno difícil.",
            pre_requisitos="Destreza 14",
        ),
        construir_talento(
            "Pechinchador",
            1,
            ["Geral", "Perícia"],
            "Você pode Ganhar Proventos (página 237) utilizando Diplomacia, gastando seus dias procurando barganhas e revendendo mercadorias para gerar lucro. Você também pode gastar tempo especificamente procurando por uma boa barganha de um item; isto funciona como se você estivesse usando Ganhar Proventos com Diplomacia, exceto que em vez de ganhar dinheiro, você compra o item com um desconto igual ao dinheiro que teria ganho (recebendo o item gratuitamente se seu ganho de proventos igualar ou exceder o custo dele). Finalmente, se selecionar Pechinchador durante a criação de personagem no 1º nível, você começa o jogo com 2 po adicionais.",
            pre_requisitos="treinado em Diplomacia",
        ),
        construir_talento(
            "Pedido Desavergonhado",
            7,
            ["Geral", "Perícia"],
            "Você pode minimizar as consequências ou ultraje de seus pedidos usando puro charme e insolência. Quando Pedir alguma coisa, você reduz qualquer aumento na CD devido a um pedido ultrajante em 2 pontos e, se rolar uma falha crítica para seu Pedido, trate o resultado como uma falha. Embora isto signifique que você nunca faz seu alvo piorar a atitude dele em relação a você fazendo um Pedido, eventualmente ele se cansará de seus pedidos mesmo que tenha uma atitude positiva em relação a você.",
            pre_requisitos="mestre em Diplomacia",
        ),
        construir_talento(
            "Performance Fascinante",
            1,
            ["Geral", "Perícia"],
            "Quando Performar, compare seu resultado à CD de Vontade de um observador. Se obtiver sucesso, o alvo fica fascinado por você durante 1 rodada. Se o observador estiver em uma situação que exige atenção imediata, tal como um combate, você deve obter um sucesso crítico para fasciná-lo e a ação Performar adquire o traço incapacitação. Você deve escolher qual criatura está tentando fascinar antes de rolar seu teste, e depois dele o alvo fica temporariamente imune por 1 hora. Se for especialista em Performance, você pode fascinar até quatro observadores; se for mestre em Performance, pode fascinar até 10 observadores; e se for lendário em Performance, pode fascinar qualquer quantidade de observadores ao mesmo tempo.",
            pre_requisitos="treinado em Performance",
        ),
        construir_talento(
            "Performance Impressionante",
            1,
            ["Geral", "Perícia"],
            "Suas performances inspiram admiração e lhe garantem fãs. Você pode Impressionar utilizando Performance em vez de Diplomacia.",
            pre_requisitos="treinado em Performance",
        ),
        construir_talento(
            "Perspicácia Astuta",
            1,
            ["Geral"],
            "Sua capacidade de evitar ou perceber ameaças está além do comum para a maioria das pessoas em sua profissão. Escolha entre Percepção ou um único tipo de salvamento (Fortitude, Reflexos ou Vontade). Você se torna especialista na característica escolhida. No 17º nível, você se torna mestre na característica escolhida.",
        ),
        construir_talento(
            "Poliglota",
            1,
            ["Geral", "Perícia"],
            "Você compreende facilmente novos idiomas. Você aprende dois novos idiomas, escolhidos dentre os idiomas comuns, idiomas incomuns e quaisquer outros idiomas aos quais tenha acesso. Você aprende um idioma adicional se já for (ou se tornar) mestre em Sociedade e mais um se já for (ou se tornar) lendário.",
            pre_requisitos="treinado em Sociedade",
            especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você aprende idiomas adicionais.",
        ),
        construir_talento(
            "Procura Acelerada",
            7,
            ["Geral"],
            "Você desenvolveu um sistema para procurar em grande velocidade, encontrando detalhes e segredos duas vezes mais rápido do que outros. Quando Procurar, você leva metade do tempo usual para Procurar em uma determinada área. Isto significa que, enquanto estiver explorando, você dobra a Velocidade em que pode se mover enquanto Procura em uma área antes de atravessá-la (até metade de sua Velocidade). Se for lendário em Percepção, em vez disso você pode Procurar quatro vezes mais rápido.",
            pre_requisitos="mestre em Percepção",
        ),
        construir_talento(
            "Procurar Vida Selvagem",
            1,
            ["Geral", "Perícia"],
            "Você pode estudar detalhes nos ermos para determinar a presença de criaturas próximas. Você pode gastar 10 minutos aferindo a área ao seu redor para descobrir quais criaturas há nos arredores, baseado em ninhos, excrementos e marcas na vegetação. Faça um teste de Sobrevivência contra a CD determinada pelo MJ baseado em quão óbvios são os sinais. Em um sucesso, você pode fazer um teste de Recordar Conhecimento com –2 de penalidade para aprender mais sobre as criaturas somente a partir destes sinais. Se for mestre em Sobrevivência, você não sofre essa penalidade.",
            pre_requisitos="treinado em Sobrevivência",
        ),
        construir_talento(
            "Proficiência com Armas",
            1,
            ["Geral"],
            "Você se torna treinado em todas as armas simples. Se já for treinado em todas as armas simples, você recebe treinamento em todas as armas marciais. Se já for treinado em todas as armas simples e marciais, você recebe treinamento em uma arma avançada à sua escolha.",
            especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você se torna treinado no próximo tipo de arma seguindo a progressão acima.",
        ),
        construir_talento(
            "Proficiência com Armaduras",
            1,
            ["Geral"],
            "Você se torna treinado em armaduras leves. Se já for treinado em armaduras leves, você recebe treinamento em armaduras médias. Se já for treinado em armaduras leves e médias, você recebe treinamento em armaduras pesadas.",
            especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você se torna treinado no próximo tipo de armadura seguindo a progressão acima.",
        ),
        construir_talento(
            "Profissional Experiente",
            1,
            ["Geral", "Perícia"],
            "Você assegura cuidadosamente suas empreitadas profissionais para evitar desastres. Quando utilizar Saber para Ganhar Proventos, se rolar uma falha crítica, trate o resultado como uma falha. Se for especialista em Saber, você dobra a quantidade de proventos recebidos por uma falha em um teste para Ganhar Proventos (a menos que o resultado original tenha sido uma falha crítica).",
            pre_requisitos="treinado em Saber",
        ),
        construir_talento(
            "Profissional Lendário",
            15,
            ["Geral", "Perícia"],
            "Sua fama se espalhou por todo lugar (se possuir Saber de Guerra, por exemplo, você pode ser um lendário estrategista ou general). Isto funciona como Artista Lendário (página 258), exceto que você consegue trabalhos de níveis superiores quando Ganhar Proventos com Saber.",
            pre_requisitos="lendário em Saber",
        ),
        construir_talento(
            "Punga",
            1,
            ["Geral", "Perícia"],
            "Você pode Furtar ou Empalmar um Objeto que esteja bem guardado, como algo dentro de um bolso, sem sofrer os –5 de penalidade normais. Você não pode furtar objetos que seriam extremamente perceptíveis ou que consumam tempo para remover (como sapatos calçados, armaduras vestidas ou objetos ativamente empunhados). Se for mestre em Ladroagem, você pode tentar Furtar de uma criatura que esteja em combate ou em guarda. Quando o fizer, Furtar requer 2 ações de manuseio (em vez de 1) e você sofre –5 de penalidade.",
            pre_requisitos="treinado em Ladroagem",
        ),
    ]


def construir_talentos_q_v() -> list[dict[str, Any]]:
    return [
        construir_talento(
            "Queda do Gato",
            1,
            ["Geral", "Perícia"],
            "Suas felinas acrobacias aéreas permitem que você amorteça suas quedas. Trate quedas como se fossem 3 metros mais curtas. Se for especialista em Acrobatismo, trate quedas como se fossem 7,5 metros mais curtas. Se for mestre em Acrobatismo, trate quedas como se fossem 15 metros mais curtas. Se for lendário em Acrobatismo, você sempre cai de pé e não sofre dano (independentemente da distância caída).",
            pre_requisitos="treinado em Acrobatismo",
        ),
        construir_talento(
            "Rastejo Ligeiro",
            2,
            ["Geral", "Perícia"],
            "Você pode Rastejar incrivelmente rápido — até metade de sua Velocidade em vez de 1,5 metros. Se for mestre em Acrobatismo, você pode Rastejar à sua Velocidade total e, se for lendário, você não fica desprevenido enquanto estiver prostrado.",
            pre_requisitos="especialista em Acrobatismo",
        ),
        construir_talento(
            "Rastreador Experiente",
            1,
            ["Geral", "Perícia"],
            "Rastrear está enraizado em sua natureza e, quando necessário, você pode seguir uma trilha sem hesitar. Você pode Rastrear enquanto se move à sua Velocidade total sofrendo –5 de penalidade em seu teste de Sobrevivência. Se for mestre em Sobrevivência, você não sofre os –5 de penalidade. Se for lendário em Sobrevivência, você não precisa mais rolar um novo teste de Sobrevivência a cada hora em que estiver rastreando, embora ainda precise rolar sempre que houver mudanças significativas na trilha.",
            pre_requisitos="treinado em Sobrevivência",
        ),
        construir_talento(
            "Reconhecer Magia",
            1,
            ["Geral", "Perícia", "Secreto"],
            "Se for treinado na perícia apropriada para a tradição da magia sendo conjurada e ela for uma magia comum de 2º nível ou inferior, você a identifica automaticamente (embora ainda precise rolar para tentar obter um sucesso crítico, você não corre o risco de obter um resultado pior do que um sucesso). O nível mais alto de magia que pode identificar automaticamente aumenta para 4 se você for especialista, 6 se for mestre e 10 se for lendário. O MJ rola um teste secreto de Arcanismo, Natureza, Ocultismo ou Religião (o que corresponder à tradição da magia sendo conjurada). Se não for treinado na perícia, você não pode obter um resultado melhor que uma falha.",
            acoes="reacao",
            pre_requisitos="treinado em Arcanismo, Natureza, Ocultismo ou Religião",
            acionamento="Uma criatura em sua linha de visão conjura uma magia que você não possui preparada ou que não consta em seu repertório de magias, ou uma armadilha ou objeto similar conjura uma magia dessas. Você deve estar ciente da conjuração.",
            resultados={
                "sucesso_critico": "Você reconhece corretamente a magia e recebe +1 de bônus de circunstância em sua jogada de salvamento ou CA contra ela.",
                "sucesso": "Você reconhece corretamente a magia.",
                "falha": "Você falha em reconhecer a magia.",
                "falha_critica": "Você identifica a magia erroneamente como outra magia completamente diferente à escolha do MJ.",
            },
        ),
        construir_talento(
            "Reconhecimento Rápido",
            7,
            ["Geral", "Perícia"],
            "Você Reconhece Magias rapidamente. Uma vez por rodada, você pode Reconhecer uma Magia utilizando uma perícia na qual você seja mestre como uma ação livre.",
            pre_requisitos="mestre em Arcanismo, Natureza, Ocultismo ou Religião; Reconhecer Magia",
        ),
        construir_talento(
            "Recuperação Contínua",
            2,
            ["Geral", "Perícia"],
            "Você monitora zelosamente o progresso de um paciente para administrar um tratamento mais rápido. Quando você Tratar Ferimentos, seu paciente fica imune por apenas 10 minutos (em vez de 1 hora). Isto se aplica somente às suas atividades de Tratar Ferimentos, não a outros tratamentos recebidos pelo paciente.",
            pre_requisitos="especialista em Medicina",
        ),
        construir_talento(
            "Recuperação Rápida",
            1,
            ["Geral"],
            "Seu corpo combate aflições rapidamente. Você recupera o dobro de Pontos de Vida por descansar. Cada vez que obtiver sucesso em um salvamento de Fortitude contra uma doença ou veneno em efeito, você reduz seu estágio em 2, ou em 1 contra uma doença ou veneno virulento. Cada sucesso crítico que você obtiver contra uma doença ou veneno em efeito reduz seu estágio em 3, ou em 2 contra uma doença ou veneno virulento. Além disso, você reduz a severidade de sua condição drenado em 2 quando descansar por uma noite (em vez de reduzi-la apenas em 1).",
            pre_requisitos="Constituição 14",
        ),
        construir_talento(
            "Recuperação Robusta",
            2,
            ["Geral", "Perícia"],
            "Você aprendeu medicina popular para melhorar a recuperação de doenças e venenos, e o seu uso contínuo o tornou especialmente resiliente. Quando você Tratar uma Doença ou Veneno, ou quando alguém usar uma destas ações em você, aumente o bônus de circunstância concedido em um sucesso para +4 e, se o resultado da jogada de salvamento do paciente for um sucesso, o paciente trata o resultado como um sucesso crítico.",
            pre_requisitos="especialista em Medicina",
        ),
        construir_talento(
            "Reparo Rápido",
            1,
            ["Geral", "Perícia"],
            "Você leva 1 minuto para Reparar um item. Se você for mestre em Manufatura, isso leva 3 ações. Se for lendário em Manufatura, isso leva 1 ação.",
            pre_requisitos="treinado em Manufatura",
        ),
        construir_talento(
            "Retirada Aterrorizada",
            7,
            ["Geral", "Perícia"],
            "Quando você obtiver um sucesso crítico na ação Desmoralizar, se o nível do alvo for menor que o seu, ele fica fugindo por 1 rodada.",
            pre_requisitos="mestre em Intimidação",
        ),
        construir_talento(
            "Saber Adicional",
            1,
            ["Geral", "Perícia"],
            "Seu conhecimento expandiu para abranger um novo campo. Escolha uma subcategoria adicional da perícia Saber. Você se torna treinado nela. No 3º, 7º e 15º níveis, você recebe um incremento de perícia adicional que você pode aplicar somente à subcategoria escolhida de Saber.",
            pre_requisitos="treinado em Saber",
            especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você deve selecionar uma nova subcategoria de Saber e recebe os incrementos de perícia adicionais para essa subcategoria nos níveis listados.",
        ),
        construir_talento(
            "Saber Inconfundível",
            2,
            ["Geral", "Perícia"],
            "Você nunca obtém informações errôneas sobre suas áreas de especialidade. Quando Recordar Conhecimento utilizando qualquer subcategoria de Saber na qual é treinado, se rolar uma falha crítica, trate o resultado como falha. Se for mestre em uma subcategoria de Saber, em um sucesso crítico, você obtém ainda mais informações ou contexto do que o comum.",
            pre_requisitos="especialista em Saber",
        ),
        construir_talento(
            "Salto na Parede",
            7,
            ["Geral", "Perícia"],
            "Você pode usar o impulso de um salto para se lançar de uma parede. Se estiver adjacente a uma parede ao final de um salto (seja realizando um Salto, Salto em Altura ou Salto em Distância), você não cai desde que sua próxima ação seja outro salto. Além disso, como seu salto prévio lhe dá impulso, você pode usar Salto em Altura ou Salto em Distância como uma ação única, mas sem Andar como parte da atividade. Você pode usar Salto na Parede somente uma vez por turno, a menos que seja lendário em Atletismo, sendo que nesse caso você pode Saltar na Parede uma vez por cada ação consecutiva usada nesse turno.",
            pre_requisitos="mestre em Atletismo",
        ),
        construir_talento(
            "Salto nas Nuvens",
            15,
            ["Geral", "Perícia"],
            "Sua capacidade atlética inigualável lhe permite saltar distâncias impossíveis. Triplique a distância de seu Salto em Distância (portanto, você poderia saltar 18 metros em um teste bem-sucedido de CD 20). Quando Saltar em Altura, utilize o cálculo para Salto em Distância, mas não triplique a distância percorrida. Quando Saltar em Altura ou Saltar em Distância, você também pode aumentar a quantidade de ações usadas (até a quantidade de ações remanescentes em seu turno) para saltar ainda mais longe. Para cada ação extra, adicione sua Velocidade à distância máxima que você salta.",
            pre_requisitos="lendário em Atletismo",
        ),
        construir_talento(
            "Salto Poderoso",
            2,
            ["Geral", "Perícia"],
            "Quando Saltar, você pode saltar até 1,5 metros em um Salto vertical e também aumenta a distância que pode saltar horizontalmente em 1,5 metros.",
            pre_requisitos="especialista em Atletismo",
        ),
        construir_talento(
            "Salto Rápido",
            1,
            ["Geral", "Perícia"],
            "Você pode usar Salto em Altura ou Salto em Distância como uma ação única em vez de 2 ações. Se o fizer, você não realiza o Andar inicial (nem falha se não Andar 3 metros).",
            pre_requisitos="treinado em Atletismo",
        ),
        construir_talento(
            "Saqueador Subaquático",
            1,
            ["Geral", "Perícia"],
            "Você aprendeu a lutar embaixo d’água. Você não fica desprevenido enquanto estiver na água e não sofre as penalidades normais por usar uma arma corpo a corpo contundente ou cortante dentro da água.",
            pre_requisitos="treinado em Atletismo",
        ),
        construir_talento(
            "Segredos Escorregadios",
            7,
            ["Geral", "Perícia"],
            "Você engana e evita tentativas de descobrir suas intenções ou sua verdadeira natureza. Quando uma magia ou efeito mágico tentar ler sua mente, detectar se você está mentindo ou revelar sua tendência, você pode fazer um teste de Dissimulação contra a CD da magia ou efeito. Se obtiver sucesso neste teste, o efeito não revela nada.",
            pre_requisitos="mestre em Dissimulação",
        ),
        construir_talento(
            "Segurar-se Rapidamente",
            2,
            ["Geral", "Perícia"],
            "Você pode facilmente se erguer de beiradas. Quando Segurar numa Beirada, você pode se erguer até a superfície e se levantar. Você pode utilizar Atletismo em vez de Reflexos para Segurar numa Beirada.",
            pre_requisitos="especialista em Atletismo",
        ),
        construir_talento(
            "Sentido Arcano",
            1,
            ["Geral", "Perícia"],
            "Seu estudo da magia permite que você sinta a presença dela instintivamente. Você pode conjurar detectar magia de 1º nível à vontade, como uma magia arcana inata. Se você for mestre em Arcanismo, a magia é elevada para o 3º nível; se for lendário, a magia é elevada para o 4º nível.",
            pre_requisitos="treinado em Arcanismo",
        ),
        construir_talento(
            "Sobrevivência Planar",
            7,
            ["Geral", "Perícia"],
            "Você pode Subsistir utilizando Sobrevivência em planos diferentes, mesmo naqueles sem os recursos ou fenômenos naturais normalmente necessários. Por exemplo: você pode forragear por comida até mesmo em planos que não tenham comida que normalmente o sustentaria. Um sucesso em seu teste para Subsistir também pode reduzir o dano causado pelo plano, a critério do MJ.",
            pre_requisitos="mestre em Sobrevivência",
        ),
        construir_talento(
            "Sobrevivente Lendário",
            15,
            ["Geral", "Perícia"],
            "Você pode sobreviver indefinidamente sem comida ou água e pode tolerar calor ou frio severos, extremos e incríveis sem sofrer dano por isso.",
            pre_requisitos="lendário em Sobrevivência",
        ),
        construir_talento(
            "Teoria Unificada",
            15,
            ["Geral", "Perícia"],
            "Você começou a conectar de maneira significativa os fundamentos comuns das quatro tradições de magia e essências mágicas, permitindo-lhe compreender todas através de uma única visão arcana. Sempre que você usar uma ação ou talento de perícia que requeira um teste de Natureza, Ocultismo ou Religião (dependendo da tradição mágica), você pode utilizar Arcanismo em vez dessas perícias. Se normalmente sofreria uma penalidade ou rolaria contra uma CD maior por utilizar Arcanismo para outras magias (como quando Identificar Magia), isso não ocorre mais.",
            pre_requisitos="lendário em Arcanismo",
        ),
        construir_talento(
            "Treinamento em Perícia",
            1,
            ["Geral", "Perícia"],
            "Você se torna treinado em uma perícia à sua escolha.",
            pre_requisitos="Inteligência 12",
            especial="Você pode selecionar este talento várias vezes. Cada vez que o fizer, você deve selecionar uma nova perícia para se tornar treinado.",
        ),
        construir_talento(
            "Treinar Animal",
            1,
            ["Geral", "Manuseio", "Perícia", "Recesso"],
            "Você passa tempo ensinando um animal para fazer uma certa ação. Você pode selecionar uma ação básica que o animal já saiba como fazer (geralmente uma das listadas na ação Comandar um Animal, na página 250) ou tentar ensinar uma nova ação básica ao animal. O MJ determina a CD de qualquer teste necessário e a quantidade de tempo que o treinamento leva (normalmente pelo menos uma semana). Geralmente é impossível ensinar a um animal um truque que exija pensamento crítico. Se for especialista, mestre ou lendário em Natureza, você pode ser capaz de treinar criaturas mais inusitadas (a critério do MJ).",
            pre_requisitos="treinado em Natureza",
            resultados={
                "sucesso": "O animal aprende a ação. Se o animal já conhecia essa ação, você pode Comandar o Animal a fazê-la sem precisar de um teste de Natureza. Se for uma ação básica nova, acrescente-a às ações que o animal pode realizar quando Comandado (embora você ainda precise fazer a rolagem para Comandá-lo).",
                "falha": "O animal não aprende o truque.",
            },
        ),
        construir_talento(
            "Veloz",
            1,
            ["Geral"],
            "Você se move mais rápido a pé. Sua Velocidade aumenta em 1,5 metros.",
        ),
        construir_talento(
            "Vitalidade",
            1,
            ["Geral"],
            "Você pode suportar mais punição que a maioria antes de sucumbir. Aumente seus Pontos de Vida máximos em uma quantidade igual ao seu nível. A CD de seus testes de recuperação é igual a 9 + seu valor atual de morrendo (página 459).",
        ),
    ]


def montar_dados_talentos() -> dict[str, Any]:
    tabela_5_1 = construir_tabela_5_1()
    tabela_5_2 = construir_tabela_5_2()

    resumo_por_id: dict[str, tuple[str | None, str]] = {}
    for entrada in tabela_5_1:
        resumo_por_id[entrada["id"]] = (None, entrada["beneficios"])
    for grupo in tabela_5_2:
        for entrada in grupo["talentos"]:
            resumo_por_id[entrada["id"]] = (grupo["grupo_id"], entrada["beneficios"])

    talentos = (
        construir_talentos_a_e()
        + construir_talentos_f_p()
        + construir_talentos_q_v()
    )
    talentos.sort(key=lambda t: t["id"])

    for talento in talentos:
        if talento["id"] in resumo_por_id:
            grupo_id, beneficios = resumo_por_id[talento["id"]]
            talento["grupo_pericia"] = grupo_id
            talento["resumo_beneficio"] = beneficios

    regras_gerais = {
        "paginas": "255",
        "descricao": "Todos os tipos de experiências e treinamentos podem moldar seu personagem além do que ele aprendeu evoluindo em sua classe. Habilidades que requerem um grau de treinamento, mas que podem ser aprendidas por qualquer um — não somente membros de determinadas ancestralidades ou classes — são chamadas de talentos gerais.",
        "talentos_gerais": {
            "progressao_padrao": "Para a maioria das classes, você recebe um talento geral quando alcança o 3º nível e a cada 4 níveis subsequentes.",
            "regra_selecao": "Cada vez que receber um talento geral, você pode selecionar qualquer talento com o traço geral ao qual satisfaça os pré-requisitos. Talentos gerais também incluem a subcategoria de talentos de perícia.",
        },
        "talentos_de_pericia": {
            "progressao_padrao": "A maioria dos personagens recebe talentos de perícia no 2º nível e a cada 2 níveis subsequentes.",
            "regra_selecao": "Quando receber um talento de perícia, você deve selecionar um talento geral com o traço perícia; você não pode selecionar um talento geral que não possua o traço perícia. O nível de um talento de perícia tipicamente é o nível mínimo no qual um personagem poderia atender a seu pré-requisito de proficiência.",
        },
    }

    return {
        "meta": {
            "titulo": "Capítulo 5: Talentos (Talentos Gerais e Talentos de Perícia) — Pathfinder 2E Livro Básico",
            "arquivo_origem": "ref/Gifts.pdf",
            "paginas_livro_basico": "255-269",
            "versao": "1.0.0",
            "total_talentos": len(talentos),
            "total_talentos_gerais": len(tabela_5_1),
            "total_talentos_de_pericia": sum(len(g["talentos"]) for g in tabela_5_2),
        },
        "regras_gerais": regras_gerais,
        "tabela_5_1_talentos_gerais": tabela_5_1,
        "tabela_5_2_talentos_gerais_de_pericia": tabela_5_2,
        "talentos": talentos,
    }


def validar_talentos_json(dados: dict[str, Any]) -> None:
    tabela_5_1 = dados["tabela_5_1_talentos_gerais"]
    tabela_5_2 = dados["tabela_5_2_talentos_gerais_de_pericia"]
    talentos = dados["talentos"]

    assert len(tabela_5_1) == 17, f"Tabela 5-1: esperado 17, obtido {len(tabela_5_1)}"
    assert len(tabela_5_2) == 18, f"Tabela 5-2 grupos: esperado 18, obtido {len(tabela_5_2)}"

    total_tab_5_2 = sum(len(g["talentos"]) for g in tabela_5_2)
    assert total_tab_5_2 == 100, f"Tabela 5-2 itens: esperado 100, obtido {total_tab_5_2}"
    assert len(talentos) == 117, f"Talentos: esperado 117, obtido {len(talentos)}"

    ids_talentos = [t["id"] for t in talentos]
    assert len(ids_talentos) == len(set(ids_talentos)), "IDs duplicados em talentos"

    mapa_tabelas: dict[str, tuple[int, str]] = {}
    for entrada in tabela_5_1:
        assert entrada["id"] not in mapa_tabelas, f"ID duplicado nas tabelas: {entrada['id']}"
        mapa_tabelas[entrada["id"]] = (entrada["nivel"], "geral")

    for grupo in tabela_5_2:
        for entrada in grupo["talentos"]:
            assert entrada["id"] not in mapa_tabelas, f"ID duplicado nas tabelas: {entrada['id']}"
            mapa_tabelas[entrada["id"]] = (entrada["nivel"], "pericia")

    assert len(mapa_tabelas) == 117

    mapa_catalogo = {t["id"]: (t["nivel"], t["categoria"]) for t in talentos}
    assert mapa_tabelas == mapa_catalogo, (
        f"Divergência entre tabelas e catálogo:\n"
        f"Só nas tabelas: {set(mapa_tabelas) - set(mapa_catalogo)}\n"
        f"Só no catálogo: {set(mapa_catalogo) - set(mapa_tabelas)}\n"
        f"Diferenças de (nível, categoria): "
        f"{ {k: (mapa_tabelas[k], mapa_catalogo[k]) for k in mapa_tabelas.keys() & mapa_catalogo.keys() if mapa_tabelas[k] != mapa_catalogo[k]} }"
    )

    for t in talentos:
        assert t["resumo_beneficio"], f"Talento sem resumo_beneficio: {t['nome']}"
        if t["categoria"] == "pericia":
            assert t["grupo_pericia"] is not None, f"Perícia sem grupo: {t['nome']}"
            assert "Perícia" in t["tracos"], f"Traço Perícia ausente: {t['nome']}"
        else:
            assert t["grupo_pericia"] is None, f"Geral puro com grupo: {t['nome']}"
            assert "Perícia" not in t["tracos"], f"Geral puro com traço Perícia: {t['nome']}"


def main() -> None:
    dados = montar_dados_talentos()
    validar_talentos_json(dados)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_SAIDA.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")

    print(f"Arquivo gerado com sucesso: {CAMINHO_SAIDA}")
    print(f"Tabela 5-1 (Talentos Gerais): {len(dados['tabela_5_1_talentos_gerais'])}")
    print(f"Tabela 5-2 (Grupos de Perícia): {len(dados['tabela_5_2_talentos_gerais_de_pericia'])}")
    print(f"Tabela 5-2 (Talentos de Perícia): {dados['meta']['total_talentos_de_pericia']}")
    print(f"Total de talentos completos: {len(dados['talentos'])}")


if __name__ == "__main__":
    main()
