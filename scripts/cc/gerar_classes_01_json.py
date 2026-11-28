"""Gerador e validador de dados/dadosc&c/classes01.json (Leva 01: Bárbaro, Bardo, Cavaleiro, Clérigo, Combatente) a partir de ref/cc/C&C Classes 01.pdf (pp. 16–39)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "dadosc&c" / "classes01.json"
CAMINHO_INTRODUCAO = RAIZ_PROJETO / "dados" / "dadosc&c" / "introducao.json"


def _linha_prog(
    nivel: int,
    pv: str,
    bpa: int,
    ppe: int,
    habilidades: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "nivel": nivel,
        "pv": pv,
        "bpa": bpa,
        "ppe": ppe,
        "habilidades": habilidades or [],
    }


def _hab_prog(nome: str, resumo: str, teste: str | None = None) -> dict[str, Any]:
    return {"nome": nome, "teste": teste, "resumo": resumo}


def _barbaro() -> dict[str, Any]:
    ppes = [
        0, 2101, 4701, 9401, 20001, 40001, 80001, 170001, 340001, 600001, 800001, 1000001,
        1200001, 1400001, 1600001, 1800001, 2000001, 2200001, 2400001, 2600001, 2800001, 3000001, 3200001, 3400001,
    ]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Senso de Combate", "+2 de bônus para testes de surpresa e reduz pela metade bônus de ataque pelas costas."),
            _hab_prog("Caçador de Cervos", "Sobrevivência em ambientes naturais, determinar direções, encontrar abrigo e comida, escalar e nadar."),
            _hab_prog("Intimidação", "-2 para testes de combate, testes de atributos e jogadas de proteção de 1 oponente.", "constituicao"),
            _hab_prog("Instinto Primitivo", "Ação imediata garante +4 em qualquer teste físico."),
        ],
        3: [
            _hab_prog("Intimidação", "-2 para testes de combate, testes de atributos e jogadas de proteção de 2 oponentes.", "constituicao"),
        ],
        4: [
            _hab_prog("Turbilhão", "Ataque dois oponentes com até metade do nível do bárbaro."),
        ],
        6: [
            _hab_prog("Intimidação", "-2 para testes de combate, testes de atributos e jogadas de proteção de 4 oponentes.", "constituicao"),
            _hab_prog("Turbilhão", "Ataque três oponentes com até metade do nível do bárbaro."),
            _hab_prog("Vontade Primitiva", "Quando ferido, ganha imediatamente 12 pontos de vida temporários."),
        ],
        10: [
            _hab_prog("Intimidação", "-2 para testes de combate, testes de atributos e jogadas de proteção de 8 oponentes.", "constituicao"),
            _hab_prog("Turbilhão", "Ataque quatro oponentes com até metade do nível do bárbaro."),
            _hab_prog("Chamado Ancestral", "Concede pontos de vida extras aos aliados."),
        ],
        13: [
            _hab_prog("Tendões de Ferro", "Pode usar armas não mágicas para atingir criaturas que exigem armas mágicas (até o mod. de Constituição)."),
        ],
        15: [
            _hab_prog("Bônus de Constituição", "Ganha +1 ponto permanente em Constituição."),
            _hab_prog("Intimidação", "-2 para testes de combate, testes de atributos e jogadas de proteção de 16 oponentes.", "constituicao"),
        ],
        16: [
            _hab_prog("Força da Natureza", "Ganha RM 2 natural (ou +2 em RM existente)."),
        ],
        19: [
            _hab_prog("Força da Natureza", "Ganha +1 ponto de RM (total RM 3)."),
        ],
        20: [
            _hab_prog("Senhor da Guerra", "Convoca 10–100 seguidores bárbaros de nível 1 (1 de nível 3 para cada 20)."),
        ],
        22: [
            _hab_prog("Força da Natureza", "Ganha +1 ponto de RM (total RM 4)."),
        ],
    }
    progressao = [
        _linha_prog(n, "d12" if n <= 10 else "+5 PV", n - 1, ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    return {
        "id": "barbaro",
        "nome": "Bárbaro",
        "paginas_livro": "16–20",
        "atributo_principal": "constituicao",
        "dado_vida": "d12",
        "pv_apos_nivel_10": 5,
        "disposicao": "qualquer",
        "armas": {"qualquer": True, "lista": ["Qualquer"], "observacao": None},
        "armaduras": {"qualquer": True, "nenhuma": False, "lista": ["Qualquer"], "observacao": "Escalar/nadar e Instinto Primitivo limitam armadura a 11 kg."},
        "conjurador": False,
        "descricao": "Guerreiros livres das fronteiras além da civilização, guiados por força, instinto primordial e resistência sobre-humana.",
        "habilidades": [
            {
                "id": "senso_de_combate",
                "nome": "Senso de Combate",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "+2 em testes de surpresa; atacantes não recebem bônus ao flanquear; bônus de ataques pelas costas/retaguarda (como Ataque pelas Costas do Trapaceiro) são reduzidos pela metade.",
            },
            {
                "id": "cacador_de_cervos",
                "nome": "Caçador de Cervos",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Encontra abrigo, comida e água para si em 1d6+2 horas sem teste; acende fogueira em 1d10 min; determina o norte verdadeiro; escala encostas naturais e nada em rios a metade do movimento sem teste (armadura/acessórios até 11 kg).",
            },
            {
                "id": "intimidacao",
                "nome": "Intimidação",
                "nivel_aquisicao": 1,
                "atributo_teste": "constituicao",
                "descricao": "Declarada antes da iniciativa com teste de Constituição (1x/combate, raio 4,5 m). Criaturas de nível igual ou inferior sofrem -2 em todas as rolagens (iniciativa, ataque, dano, testes). Alvos: 1 (N1), 2 (N3), 4 (N6), 8 (N10), 16 (N15). Termina para um alvo se o bárbaro errar ataque contra ele.",
            },
            {
                "id": "instinto_primitivo",
                "nome": "Instinto Primitivo",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Ao lançar-se ao combate sem hesitar/fugir (armadura até 11 kg), recebe +4 em testes de atributo físico (FOR, DES ou CON). Também permite prender a respiração por rodadas iguais à pontuação de CON, suportar climas extremos por +1 dia e dobrar a distância de corrida diária.",
            },
            {
                "id": "turbilhao",
                "nome": "Turbilhão",
                "nivel_aquisicao": 4,
                "atributo_teste": None,
                "descricao": "1x/combate, substitui o ataque normal (anunciado antes de atacar, sem recuar). Permite atacar múltiplos oponentes a até 1,5 m com até metade do nível do bárbaro: 2 oponentes (N4), 3 (N6) e 4 (N10).",
            },
            {
                "id": "vontade_primitiva",
                "nome": "Vontade Primitiva",
                "nivel_aquisicao": 6,
                "atributo_teste": None,
                "descricao": "1x/dia. Quando reduzido a 12 PV ou menos (N6–9), 18 PV (N10–14) ou 24 PV (N15+), ganha imediatamente 12 PV temporários para o combate. Ativa automaticamente se cair a 0 ou negativo (exceto -10 ou menos); a remoção posterior não reduz abaixo de 1 PV.",
            },
            {
                "id": "chamado_ancestral",
                "nome": "Chamado Ancestral",
                "nivel_aquisicao": 10,
                "atributo_teste": None,
                "descricao": "1x/semana. Concede a até (2 × nível) aliados de nível igual ou menor PV extras iguais ao máximo de um nível adicional da criatura, durando até 1 dia ou conclusão da tarefa.",
            },
            {
                "id": "tendoes_de_ferro",
                "nome": "Tendões de Ferro",
                "nivel_aquisicao": 13,
                "atributo_teste": None,
                "descricao": "Permite atingir com arma não mágica criaturas que exigem armas mágicas até o bônus do modificador de Constituição do bárbaro (nota: texto menciona N10, tabela de progressão lista N13).",
            },
            {
                "id": "bonus_de_constituicao",
                "nome": "Bônus de Constituição",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Constituição em +1.",
            },
            {
                "id": "forca_da_natureza",
                "nome": "Força da Natureza",
                "nivel_aquisicao": 16,
                "atributo_teste": None,
                "descricao": "Concede Resistência à Magia (RM) natural de 2 (ou +2 em RM existente) no N16, aumentando em +1 a cada 3 níveis (RM 3 no N19, RM 4 no N22).",
            },
            {
                "id": "senhor_da_guerra",
                "nome": "Senhor da Guerra",
                "nivel_aquisicao": 20,
                "atributo_teste": None,
                "descricao": "1x/mês em região que conheça sua reputação (500 habitantes por 10 guerreiros). Convoca 10–100 bárbaros N1 (CA 13) e 1 bárbaro N3 a cada 20, lutando por até 30 dias sem pagamento.",
            },
        ],
        "progressao": progressao,
    }


def _bardo() -> dict[str, Any]:
    ppes = [
        0, 1501, 3251, 7501, 15001, 30001, 60001, 120001, 240001, 450001, 625001, 800001,
        975001, 1150001, 1325001, 1500001, 1675001, 1850001, 2025001, 2200001, 2375001, 2550001, 2725001, 2900001,
    ]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Decifrar Escrita", "Decifra escrita desconhecida, arcaica ou em código (10 min/página).", "inteligencia"),
            _hab_prog("Exaltar", "Inspira companheiros a até 18 m: +2 em testes de atributo/proteção/habilidade (1x/dia por nível).", "carisma"),
            _hab_prog("Conhecimento de Lendas", "Verifica fatos, lendas, itens lendários ou idiomas secretos.", "carisma"),
        ],
        4: [
            _hab_prog("Fascinar", "Fascina até 2 criaturas, 3x/dia (JP Carisma)."),
        ],
        5: [
            _hab_prog("Fascinar", "Pode usar Encantar Humanoide em criatura fascinada."),
        ],
        6: [
            _hab_prog("Fascinar", "Fascina até 4 criaturas."),
            _hab_prog("Exaltar", "Bônus de exaltação aumenta para +3.", "carisma"),
        ],
        8: [
            _hab_prog("Fascinar", "Pode implantar Sugestão em criatura fascinada."),
        ],
        9: [
            _hab_prog("Inspirar Grandeza", "1 companheiro a até 9 m recebe +2 para acertar e 2 níveis temporários de PV."),
        ],
        11: [
            _hab_prog("Inspirar Grandeza", "2 companheiros recebem +2 para acertar e 2 níveis temporários."),
        ],
        12: [
            _hab_prog("Fascinar", "Pode tentar Antipatia/Simpatia; fascina até 10 criaturas."),
            _hab_prog("Exaltar", "Bônus de exaltação aumenta para +4.", "carisma"),
        ],
        13: [
            _hab_prog("Inspirar Grandeza", "3 companheiros recebem +2 para acertar e 2 níveis temporários."),
            _hab_prog("Influenciar Multidão", "Deixa em êxtase uma plateia de até 20 níveis."),
        ],
        15: [
            _hab_prog("Bônus de Carisma", "Ganha +1 ponto permanente em Carisma."),
            _hab_prog("Inspirar Grandeza", "4 companheiros recebem +2 para acertar e 2 níveis temporários."),
        ],
        16: [
            _hab_prog("Influenciar Multidão", "Deixa em êxtase uma plateia de até 40 níveis."),
        ],
        17: [
            _hab_prog("Inspirar Grandeza", "5 companheiros recebem +2 para acertar e 2 níveis temporários."),
            _hab_prog("Palavras de Poder", "1x/dia: mata, paralisa, cega ou ensurdece alvo conforme nível (JP Carisma)."),
        ],
        18: [
            _hab_prog("Exaltar", "Bônus de exaltação aumenta para +5."),
            _hab_prog("Fascinar", "Pode tentar Sugestão em Área em criaturas fascinadas."),
            _hab_prog("Reunir", "1x/dia: concede nova JP contra medo/moral a aliados ao alcance da voz."),
        ],
        19: [
            _hab_prog("Inspirar Grandeza", "6 companheiros recebem +2 para acertar e 2 níveis temporários."),
            _hab_prog("Influenciar Multidão", "Deixa em êxtase uma plateia de até 80 níveis."),
        ],
        20: [
            _hab_prog("Missão", "Impõe uma missão (como feitiço Obrigação; JP Carisma)."),
        ],
        21: [
            _hab_prog("Inspirar Grandeza", "7 companheiros recebem +2 para acertar e 2 níveis temporários."),
        ],
        22: [
            _hab_prog("Influenciar Multidão", "Deixa em êxtase uma plateia de até 160 níveis."),
        ],
        23: [
            _hab_prog("Inspirar Grandeza", "8 companheiros recebem +2 para acertar e 2 níveis temporários."),
        ],
        24: [
            _hab_prog("Mudar Disposição", "Pode alterar a disposição de um PNJ ao longo de 1 mês de convivência."),
            _hab_prog("Palavras de Poder", "1x/semana: cria Esfera Antimagia (12 m) ou corrói ilusões com a voz."),
        ],
    }
    progressao = [
        _linha_prog(n, "d10" if n <= 10 else "+4 PV", n - 1, ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    return {
        "id": "bardo",
        "nome": "Bardo",
        "paginas_livro": "21–25",
        "atributo_principal": "carisma",
        "dado_vida": "d10",
        "pv_apos_nivel_10": 4,
        "disposicao": "qualquer",
        "armas": {
            "qualquer": False,
            "lista": [
                "Espada Larga", "Arcos", "Clava", "Adaga", "Dardo", "Machado de Mão",
                "Martelos", "Espada Longa", "Florete", "Cimitarra", "Espada Curta",
                "Funda", "Lança", "Bastão",
            ],
            "observacao": None,
        },
        "armaduras": {
            "qualquer": False,
            "nenhuma": False,
            "lista": [
                "Peitorais", "Camisa de Cota de Malha", "Couro Cozido", "Conjunto Grego",
                "Peles", "Laminar de Couro", "Couro", "Jaqueta de Couro", "Acolchoada",
                "Cota de Anéis", "Couro Tachado",
            ],
            "observacao": None,
        },
        "conjurador": False,
        "descricao": "Guerreiros-poetas, cronistas e oradores que inspiram aliados, preservam lendas e dobram corações através da voz e da música.",
        "habilidades": [
            {
                "id": "decifrar_escrita",
                "nome": "Decifrar Escrita",
                "nivel_aquisicao": 1,
                "atributo_teste": "inteligencia",
                "descricao": "Decifra idiomas desconhecidos, textos arcaicos ou códigos (10 min/página, 1 tentativa por escrito). Pode usar pergaminho arcano com penalidade de -10 no teste (não funciona com pergaminhos divinos).",
            },
            {
                "id": "exaltar",
                "nome": "Exaltar",
                "nivel_aquisicao": 1,
                "atributo_teste": "carisma",
                "descricao": "1x/dia por nível, duração de rodadas igual ao nível, raio 18 m. Concede bônus em testes de atributo, habilidade e JP (não afeta ataque): +2 (N1), +3 (N6), +4 (N12), +5 (N18).",
            },
            {
                "id": "conhecimento_de_lendas",
                "nome": "Conhecimento de Lendas",
                "nivel_aquisicao": 1,
                "atributo_teste": "carisma",
                "descricao": "Recorda ou pesquisa informações sobre locais, notáveis, itens lendários ou idiomas secretos (gíria dos trapaceiros, druídico, sinais dos exploradores). Categorias de ND: Comum, Incomum, Obscuro e Extremamente Obscuro.",
            },
            {
                "id": "fascinar",
                "nome": "Fascinar",
                "nivel_aquisicao": 4,
                "atributo_teste": None,
                "descricao": "3x/dia, dura rodadas iguais ao nível (requer concentração). Alvo faz JP de Carisma; em falha fica em transe (tratado como caído, -4 JP, -5 CA). Alvos = nível - 2 (N4: 2, N6: 4, N12: 10). Efeitos extras em fascinados: N5 Encantar Humanoide, N8 Sugestão, N12 Antipatia/Simpatia, N18 Sugestão em Área.",
            },
            {
                "id": "inspirar_grandeza",
                "nome": "Inspirar Grandeza",
                "nivel_aquisicao": 9,
                "atributo_teste": None,
                "descricao": "Raio 9 m, dura 6 rodadas (+1 rodada por nível acima de 9). Concede +2 para acertar e PV temporários equivalentes a 2 níveis extras (+ mod CON). Afeta 1 aliado no N9 e +1 a cada 2 níveis (N11: 2, N13: 3, ..., N23: 8).",
            },
            {
                "id": "influenciar_multidao",
                "nome": "Influenciar Multidão",
                "nivel_aquisicao": 13,
                "atributo_teste": None,
                "descricao": "Ouvintes fazem JP Carisma ou ficam em êxtase enquanto o bardo se apresenta + 1 rodada/nível depois. Afeta até 20 níveis de alvos (N13), dobrando a cada 3 níveis (N16: 40, N19: 80, N22: 160).",
            },
            {
                "id": "bonus_de_carisma",
                "nome": "Bônus de Carisma",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Carisma em +1.",
            },
            {
                "id": "palavras_de_poder",
                "nome": "Palavras de Poder",
                "nivel_aquisicao": 17,
                "atributo_teste": None,
                "descricao": "1x/dia (JP Carisma): nível <=4 Morte; 5-7 Paralisia (1d10 rod), Cegueira (2d4), Surdez (1d4); 8-11 Cegueira/Surdez; >=12 Surdez. No N24 (1x/semana): Esfera Antimagia (12 m) ou corroer ilusões com JP Inteligência.",
                "tabela_efeitos": [
                    {"nivel_alvo": "4 ou menor", "efeito": "Morte"},
                    {"nivel_alvo": "5-7", "efeito": "Paralisia, Cegueira, Surdez"},
                    {"nivel_alvo": "8-11", "efeito": "Cegueira, Surdez"},
                    {"nivel_alvo": "12 ou maior", "efeito": "Surdez"},
                ],
            },
            {
                "id": "reunir",
                "nome": "Reunir",
                "nivel_aquisicao": 18,
                "atributo_teste": None,
                "descricao": "1x/dia. Aliados ao alcance da voz ganham nova JP contra medo ou moral (incluindo medo de dragão) e ficam imunes por 1 rodada por nível do bardo.",
            },
            {
                "id": "missao",
                "nome": "Missão",
                "nivel_aquisicao": 20,
                "atributo_teste": None,
                "descricao": "Alvo faz JP Carisma ou recebe uma obrigação idêntica ao feitiço Obrigação.",
            },
            {
                "id": "mudar_disposicao",
                "nome": "Mudar Disposição",
                "nivel_aquisicao": 22,
                "atributo_teste": None,
                "descricao": "Convivendo 1 h/dia por 1 mês com um PNJ disposto, impõe teste de Carisma (ND = nível do bardo) para mudar a disposição em 1 passo (nota: texto menciona N22, tabela lista N24).",
            },
        ],
        "progressao": progressao,
    }


def _cavaleiro() -> dict[str, Any]:
    ppes = [
        0, 2251, 4501, 9001, 18001, 36001, 72001, 150001, 300001, 600001, 725001, 900001,
        1075001, 1250001, 1425001, 1600001, 1775001, 1950001, 2125001, 2300001, 2475001, 2650001, 2825001, 3000001,
    ]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Montaria Herdada", "Começa com um cavalo de montaria totalmente equipado."),
            _hab_prog("Equitação", "Combate montado e manobras: cobertura, desviar, queda suave, saltar e investida.", "destreza"),
            _hab_prog("Inspirar", "Até 12 aliados recebem o modificador de Carisma do cavaleiro para acertar."),
        ],
        3: [
            _hab_prog("Encorajar", "Aliados num raio de 9 m recebem +1 em JP físicas/INT e +2 em JP SAB/CAR."),
            _hab_prog("Inspirar", "Até 25 aliados recebem o modificador de Carisma para acertar."),
        ],
        5: [
            _hab_prog("Desmoralizar", "Até 25 oponentes sofrem -4 em testes de Carisma e JP medo (-1 ataque se falhar)."),
            _hab_prog("Inspirar", "Até 50 aliados recebem o modificador de Carisma para acertar."),
        ],
        7: [
            _hab_prog("Inspirar", "Até 250 aliados recebem o modificador de Carisma para acertar."),
            _hab_prog("Desmoralizar", "Desmoraliza até 100 oponentes."),
        ],
        8: [
            _hab_prog("Domínio do Campo de Batalha", "Pode usar Inspirar, Encorajar e Desmoralizar na mesma rodada."),
        ],
        9: [
            _hab_prog("Inspirar", "Até 1.000 aliados recebem o modificador de Carisma para acertar."),
            _hab_prog("Desmoralizar", "Desmoraliza até 250 oponentes."),
        ],
        10: [
            _hab_prog("Chamado às Armas", "Atrai 2d10 seguidores de nível 0 por mês ao estabelecer fortaleza."),
        ],
        12: [
            _hab_prog("Inspirar", "Até 5.000 aliados recebem o modificador de Carisma para acertar."),
            _hab_prog("Desmoralizar", "Desmoraliza até 1.000 oponentes."),
        ],
        13: [
            _hab_prog("Especialista em Armas", "Aliados a até 12 m ganham ±1 em manobras de combate sob seu comando."),
        ],
        15: [
            _hab_prog("Bônus de Carisma", "Ganha +1 ponto permanente em Carisma."),
        ],
        16: [
            _hab_prog("Inspirar", "Até 20.000 aliados recebem o modificador de Carisma para acertar."),
            _hab_prog("Desmoralizar", "Desmoraliza até 5.000 oponentes."),
        ],
        17: [
            _hab_prog("Golpe de Honra", "Em duelo formal, reduz CA do oponente pelo mod. CAR, soma CAR no ataque e causa dano dobrado."),
            _hab_prog("Especialista em Armas", "Aliados a até 12 m ganham ±2 em manobras de combate."),
        ],
        20: [
            _hab_prog("Senhor da Batalha", "Tropas em combate em massa somam mod. CAR em ataque/dano/moral e +1 CA."),
        ],
        21: [
            _hab_prog("Conversão para Cavalaria", "Pode conferir cavalaria a PNJs escolhidos (tornam-se cavaleiros N1)."),
        ],
        24: [
            _hab_prog("Senhor da Batalha", "Bônus de combate em massa dobra (2× mod. CAR), +2 CA e +2 moral."),
            _hab_prog("Caminho da Grandeza", "Escolha lendária: bônus contra oponentes mais fortes, controlar atmosfera 1x/mês e imunidade a moral baixa para aliados."),
        ],
    }
    progressao = [
        _linha_prog(n, "d10" if n <= 10 else "+4 PV", n - 1, ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    return {
        "id": "cavaleiro",
        "nome": "Cavaleiro",
        "paginas_livro": "26–31",
        "atributo_principal": "carisma",
        "dado_vida": "d10",
        "pv_apos_nivel_10": 4,
        "disposicao": "qualquer",
        "armas": {
            "qualquer": True,
            "lista": ["Qualquer (exceto limitadas pelo Código de Conduta)"],
            "observacao": "Não pode usar chicotes, porrete, correntes ou armas associadas a covardia; arcos raramente usados (a critério do GC).",
        },
        "armaduras": {"qualquer": True, "nenhuma": False, "lista": ["Qualquer"], "observacao": "Ao menos 10% da renda deve ser dada como tributo ao senhor ou ordem."},
        "conjurador": False,
        "descricao": "Líderes militares profissionais e guerreiros montados guiados por um rigoroso código de conduta e honra.",
        "montarias_estatisticas": [
            {"nome": "Cavalo de Montaria", "pv": "2d8+2", "ca": 13, "movimento": "18 m", "primarios": "físicos", "ataques": "2 cascos (1d4+1)"},
            {"nome": "Cavalo de Guerra Leve", "pv": "3d10", "ca": 14, "movimento": "18 m", "primarios": "físicos", "ataques": "2 cascos (1d4+2) ou 1 mordida (1d4)"},
        ],
        "codigo_de_honra_virtudes": [
            "Coragem", "Defesa", "Discrição", "Excelência", "Fé", "Honra",
            "Humildade", "Justiça", "Generosidade", "Lealdade", "Nobreza", "Valor",
        ],
        "habilidades": [
            {
                "id": "montaria_herdada",
                "nome": "Montaria Herdada",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Começa com cavalo de montaria totalmente equipado (sela, manta, alforjes, freio, bridão, arreio, ferraduras e comida) com 2d8+2 PV, além do dinheiro inicial.",
            },
            {
                "id": "equitacao",
                "nome": "Equitação",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Sem teste: selar, montar, lutar montado sem penalidade, guiar com joelhos, avaliar cavalos e ordenar ataque de cavalo de guerra. Com teste (renunciando a ataque): Cobertura (+6 CA), Desviar (+4 CA cavaleiro / +2 CA montaria), Queda Suave (evita 1d6), Saltar (até 2/3 da altura do cavalo) e Investida (dano triplo com lança).",
            },
            {
                "id": "inspirar",
                "nome": "Inspirar",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "1x/dia, dura rodadas iguais ao nível. Aliados ganham mod. CAR para acertar: 12 (N1), 25 (N3), 50 (N5), 250 (N7), 1.000 (N9), 5.000 (N12), 20.000 (N16). Não acumula com Encorajar/Desmoralizar antes do N8.",
            },
            {
                "id": "encorajar",
                "nome": "Encorajar",
                "nivel_aquisicao": 3,
                "atributo_teste": None,
                "descricao": "1x/dia, raio 9 m, dura rodadas iguais ao nível. Aliados ganham +1 em JP de FOR/CON/DES/INT e +2 em JP de SAB/CAR.",
            },
            {
                "id": "desmoralizar",
                "nome": "Desmoralizar",
                "nivel_aquisicao": 5,
                "atributo_teste": None,
                "descricao": "1x/dia, dura rodadas iguais ao nível. Inimigos sofrem -4 em testes de Carisma e devem passar em JP contra medo (-4) ou sofrer -1 para acertar. Alvos: 25 (N5), 100 (N7), 250 (N9), 1.000 (N12), 5.000 (N16).",
            },
            {
                "id": "dominio_do_campo_de_batalha",
                "nome": "Domínio do Campo de Batalha",
                "nivel_aquisicao": 8,
                "atributo_teste": None,
                "descricao": "Pode usar Inspirar, Encorajar e Desmoralizar na mesma rodada (adicional aos usos normais).",
            },
            {
                "id": "chamado_as_armas",
                "nome": "Chamado às Armas",
                "nivel_aquisicao": 10,
                "atributo_teste": None,
                "descricao": "Ao estabelecer fortaleza, atrai 2d10 seguidores N0/mês (2 po/mês). A cada 40 seguidores chega 1 cavaleiro N1 (100 po/mês); a cada 80 chega 1 cavaleiro N5 (100 po/nível/mês).",
            },
            {
                "id": "especialista_em_armas",
                "nome": "Especialista em Armas",
                "nivel_aquisicao": 13,
                "atributo_teste": None,
                "descricao": "Sob seu comando, aliados a até 12 m recebem ±1 em manobras de combate (±2 no N17).",
            },
            {
                "id": "bonus_de_carisma",
                "nome": "Bônus de Carisma",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Carisma em +1.",
            },
            {
                "id": "golpe_de_honra",
                "nome": "Golpe de Honra",
                "nivel_aquisicao": 17,
                "atributo_teste": None,
                "descricao": "1x/dia por alvo em combate formal/individual sem recuar. Reduz a CA do oponente pelo mod. CAR, soma mod. CAR no ataque e causa dano dobrado.",
            },
            {
                "id": "senhor_da_batalha",
                "nome": "Senhor da Batalha",
                "nivel_aquisicao": 20,
                "atributo_teste": None,
                "descricao": "Em combate em massa (não afeta PJs), tropas que o vejam somam mod. CAR em ataque, dano e moral, e +1 CA (+2× CAR, +2 CA e +2 moral no N24).",
            },
            {
                "id": "conversao_para_cavalaria",
                "nome": "Conversão para Cavalaria",
                "nivel_aquisicao": 21,
                "atributo_teste": None,
                "descricao": "Confere cavalaria a PNJs escolhidos; PNJs sem classe tornam-se cavaleiros N1 com +1 permanente em ataque e CA.",
            },
            {
                "id": "caminho_da_grandeza",
                "nome": "Caminho da Grandeza",
                "nivel_aquisicao": 24,
                "atributo_teste": None,
                "descricao": "Escolha permanente: nunca pode recuar; recebe a diferença de nível em ataque/dano contra inimigos mais fortes; inimigos com <= metade do nível evitam/fogem; 1x/mês Controlar Atmosfera (N10); aliados não sofrem moral baixa. Covardia faz perder todas as habilidades de cavaleiro.",
            },
        ],
        "progressao": progressao,
    }


def _clerigo() -> dict[str, Any]:
    ppes = [
        0, 2251, 5001, 9001, 18001, 35001, 70001, 140001, 300001, 425001, 650001, 900001,
        1150001, 1400001, 1650001, 1900001, 2150001, 2400001, 2650001, 2900001, 3150001, 3400001, 3650001, 3900001,
    ]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Usar Magia", "Conjura feitiços divinos (feitiços bônus com Sabedoria 13-15 [1º], 16-17 [2º], 18-19 [3º])."),
            _hab_prog("Afastar Mortos-Vivos", "Afasta (1d12 + mod. CAR) ou destrói (5+ níveis acima) mortos-vivos a até 18 m.", "sabedoria"),
            _hab_prog("Seleção de Armas", "Pode escolher uma arma especial favorita da sua divindade."),
        ],
        15: [
            _hab_prog("Bônus de Sabedoria", "Ganha +1 ponto permanente em Sabedoria."),
        ],
        18: [
            _hab_prog("Campanha Sagrada", "Convoca adeptos armados (d8 PV) e desarmados (d4 PV) com +1 nos testes."),
        ],
        19: [
            _hab_prog("Campanha Sagrada", "Dobra o número de seguidores convocados e aumenta bônus para +2."),
        ],
        20: [
            _hab_prog("Recordação Perfeita", "Recorda feitiços de nível 0 já conjurados no dia (ND 0, 1x por feitiço).", "sabedoria"),
        ],
        21: [
            _hab_prog("Banir", "Expulsa criaturas extraplanares do plano material por dias iguais ao nível.", "sabedoria"),
        ],
        22: [
            _hab_prog("Monólito Divino", "Irradia aura permanente: imune a ataques de morte, +3 afastar e +2 em testes/JP."),
        ],
        23: [
            _hab_prog("Campanha Sagrada", "Quadruplica seguidores convocados, com líderes N1–N3 e bônus +3."),
            _hab_prog("Marca do Santo", "Atrai 1d10 seguidores/SAB + líderes clérigos; concede feitiços extras sagrados."),
        ],
        24: [
            _hab_prog("Recordação Perfeita", "Recorda feitiços de 1º nível já conjurados no dia (ND 0).", "sabedoria"),
        ],
    }
    progressao = [
        _linha_prog(n, "d8" if n <= 10 else "+3 PV", n // 2, ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    # Tabela oficial: Feitiços Diários do Clérigo (p. 33) — níveis 1..24, círculos 0..9
    feiticos_diarios: dict[str, dict[str, int]] = {
        "1":  {"0": 3, "1": 1},
        "2":  {"0": 4, "1": 2},
        "3":  {"0": 4, "1": 2, "2": 1},
        "4":  {"0": 4, "1": 3, "2": 2},
        "5":  {"0": 4, "1": 3, "2": 2, "3": 1},
        "6":  {"0": 5, "1": 3, "2": 3, "3": 2},
        "7":  {"0": 5, "1": 4, "2": 3, "3": 2, "4": 1},
        "8":  {"0": 5, "1": 4, "2": 3, "3": 3, "4": 2},
        "9":  {"0": 5, "1": 4, "2": 4, "3": 3, "4": 2, "5": 1},
        "10": {"0": 5, "1": 4, "2": 4, "3": 3, "4": 3, "5": 2},
        "11": {"0": 6, "1": 5, "2": 4, "3": 4, "4": 3, "5": 2, "6": 1},
        "12": {"0": 6, "1": 5, "2": 4, "3": 4, "4": 3, "5": 3, "6": 2},
        "13": {"0": 6, "1": 5, "2": 5, "3": 4, "4": 4, "5": 3, "6": 2, "7": 1},
        "14": {"0": 6, "1": 5, "2": 5, "3": 4, "4": 4, "5": 3, "6": 3, "7": 2},
        "15": {"0": 6, "1": 5, "2": 5, "3": 5, "4": 4, "5": 4, "6": 3, "7": 2, "8": 1},
        "16": {"0": 6, "1": 6, "2": 5, "3": 5, "4": 4, "5": 4, "6": 3, "7": 3, "8": 2},
        "17": {"0": 7, "1": 6, "2": 5, "3": 5, "4": 5, "5": 4, "6": 4, "7": 3, "8": 2, "9": 1},
        "18": {"0": 7, "1": 6, "2": 6, "3": 5, "4": 5, "5": 4, "6": 4, "7": 3, "8": 3, "9": 2},
        "19": {"0": 7, "1": 6, "2": 6, "3": 5, "4": 5, "5": 5, "6": 4, "7": 4, "8": 3, "9": 2},
        "20": {"0": 7, "1": 6, "2": 6, "3": 6, "4": 5, "5": 5, "6": 4, "7": 4, "8": 3, "9": 3},
        "21": {"0": 7, "1": 6, "2": 6, "3": 6, "4": 5, "5": 5, "6": 5, "7": 4, "8": 4, "9": 3},
        "22": {"0": 7, "1": 7, "2": 6, "3": 6, "4": 6, "5": 5, "6": 5, "7": 4, "8": 4, "9": 3},
        "23": {"0": 7, "1": 7, "2": 6, "3": 6, "4": 6, "5": 5, "6": 5, "7": 5, "8": 4, "9": 4},
        "24": {"0": 8, "1": 7, "2": 7, "3": 6, "4": 6, "5": 6, "6": 6, "7": 5, "8": 4, "9": 4},
    }
    return {
        "id": "clerigo",
        "nome": "Clérigo",
        "paginas_livro": "32–35",
        "atributo_principal": "sabedoria",
        "dado_vida": "d8",
        "pv_apos_nivel_10": 3,
        "disposicao": "qualquer",
        "armas": {
            "qualquer": False,
            "lista": [
                "Especial (arma da divindade)", "Clava", "Picareta de Guerra", "Adaga",
                "Mangual Leve", "Mangual Pesado", "Martelo Leve", "Maça Leve",
                "Maça Pesada", "Maça-Estrela", "Bordão", "Martelo de Guerra",
            ],
            "observacao": "Pode adicionar a arma principal da divindade adorada via Seleção de Armas.",
        },
        "armaduras": {"qualquer": True, "nenhuma": False, "lista": ["Qualquer"], "observacao": None},
        "conjurador": True,
        "conjuracao": {
            "tradicao": "divina",
            "atributo_conjuracao": "sabedoria",
            "preparacao": "oracao_contemplacao_estudo",
            "feiticos_bonus_por_atributo": [
                {"min": 13, "max": 15, "circulo": 1, "quantidade": 1},
                {"min": 16, "max": 17, "circulo": 2, "quantidade": 1},
                {"min": 18, "max": 19, "circulo": 3, "quantidade": 1},
            ],
            "feiticos_bonus_cumulativos": True,
            "feiticos_bonus_requer_acesso_circulo": True,
            "feiticos_diarios": feiticos_diarios,
        },
        "descricao": "Sacerdotes-guerreiros devotados a uma divindade ou panteão, canalizando magia divina e poder marcial no campo de batalha.",
        "habilidades": [
            {
                "id": "usar_magia_divina",
                "nome": "Feitiços (Magia Divina)",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Prepara e conjura feitiços divinos por oração conforme a Tabela de Feitiços Diários + Feitiços Bônus cumulativos por Sabedoria elevada (13-15: +1 de 1º; 16-17: +1 de 2º; 18-19: +1 de 3º).",
            },
            {
                "id": "afastar_mortos_vivos",
                "nome": "Afastar Mortos-Vivos",
                "nivel_aquisicao": 1,
                "atributo_teste": "sabedoria",
                "descricao": "Ação especial de 1 rodada exibindo símbolo sagrado (alcance 18 m). Afeta 1d12 + mod. CAR mortos-vivos; destrói (ou controla, se maligno) quando 5+ níveis acima. Clérigos malignos também podem afastar paladinos.",
            },
            {
                "id": "selecao_de_armas",
                "nome": "Seleção de Armas",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Permite escolher uma arma fora da lista padrão caso seja a arma principal da divindade adorada.",
            },
            {
                "id": "bonus_de_sabedoria",
                "nome": "Bônus de Sabedoria",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Sabedoria em +1.",
            },
            {
                "id": "campanha_sagrada",
                "nome": "Campanha Sagrada",
                "nivel_aquisicao": 18,
                "atributo_teste": None,
                "descricao": "Convoca adeptos armados (d8 PV) e desarmados (d4 PV) por até 1 semana/ponto de CAR com +1 nos testes (N19: dobro e +2; N23: quádruplo e +3 com líderes N1–N3).",
            },
            {
                "id": "recordacao_perfeita",
                "nome": "Recordação Perfeita",
                "nivel_aquisicao": 20,
                "atributo_teste": "sabedoria",
                "descricao": "Teste de Sabedoria (ND 0) para recordar e relançar 1x/dia um feitiço já conjurado de nível 0 (N20) ou de 1º nível (N24).",
            },
            {
                "id": "banir",
                "nome": "Banir",
                "nivel_aquisicao": 21,
                "atributo_teste": "sabedoria",
                "descricao": "Age como Afastar Mortos-Vivos contra criaturas extraplanares (1d12 menores, 1d6 superiores ou 1 senhor demônio/arquidiabo), expulsando por dias iguais ao nível do clérigo.",
            },
            {
                "id": "monolito_divino",
                "nome": "Monólito Divino",
                "nivel_aquisicao": 22,
                "atributo_teste": None,
                "descricao": "Aura permanente (texto: N21 / raio 6 m; tabela: N22 / raio 4 m): imune a ataques de morte, +3 em testes de afastar dentro do raio e +2 em testes, JP e atributos.",
            },
            {
                "id": "marca_do_santo",
                "nome": "Marca do Santo",
                "nivel_aquisicao": 23,
                "atributo_teste": None,
                "descricao": "Atrai 1d10 seguidores/SAB (com líderes clérigos N1/N4/N8/N10 se possuir templo). Sem oração: 1x/semana Curar, Restaurar Visão, Remover Enfermidade e Ressurreição; 1x/dia Criar Água Benta e Palavra Sagrada/Profana.",
            },
        ],
        "progressao": progressao,
    }


def _combatente() -> dict[str, Any]:
    ppes = [
        0, 2001, 4001, 8501, 17001, 34001, 68001, 136001, 272001, 500001, 750001, 1000001,
        1250001, 1500001, 1750001, 2000001, 2250001, 2500001, 2750001, 3000001, 3250001, 3500001, 3750001, 4000001,
    ]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Especialização em Armas", "Escolhe 1 arma: +1 para ataque e dano."),
        ],
        4: [
            _hab_prog("Domínio de Combate", "1 ataque extra corpo a corpo contra monstros de nível 1 ou menos."),
        ],
        7: [
            _hab_prog("Especialização em Armas", "Bônus com a arma escolhida aumenta para +2 em ataque e dano."),
        ],
        8: [
            _hab_prog("Domínio de Combate", "2 ataques extras corpo a corpo contra monstros de nível 1 ou menos."),
        ],
        10: [
            _hab_prog("Ataque Extra", "1 ataque adicional por rodada com qualquer arma (não combina com Domínio de Combate)."),
        ],
        12: [
            _hab_prog("Domínio de Combate", "3 ataques extras corpo a corpo contra monstros de nível 1 ou menos."),
        ],
        13: [
            _hab_prog("Especialização Avançada em Armas", "Segunda especialização em arma (+1/+1; pode acumular na 1ª arma)."),
            _hab_prog("Espaço de Batalha (Consciência Tática)", "+1 na CA enquanto não usar arma de duas mãos (acumula com escudo)."),
        ],
        14: [
            _hab_prog("Golpe de Escudo", "Usa escudo médio (1d4) ou grande (1d6) de metal como ataque extra sem penalidade."),
        ],
        15: [
            _hab_prog("Bônus de Força", "Ganha +1 ponto permanente em Força."),
        ],
        16: [
            _hab_prog("Domínio de Combate", "4 ataques extras contra monstros de nível 1 ou menor."),
            _hab_prog("Domínio de Combate Avançado", "1 ataque extra contra monstros de nível 2."),
        ],
        17: [
            _hab_prog("Espaço de Batalha (Consciência Tática)", "Bônus de manobras: esquiva +3, desengajar -1, evasão +5, flanquear +2, ataque pelas costas +3."),
        ],
        19: [
            _hab_prog("Especialização em Armas", "Bônus da 1ª arma aumenta para +3 em ataque e dano."),
            _hab_prog("Especialização Avançada em Armas", "Bônus da 2ª especialização aumenta para +2 em ataque e dano."),
            _hab_prog("Bônus de Atributo", "Ganha +1 ponto permanente em Força ou Destreza."),
        ],
        20: [
            _hab_prog("Domínio de Combate", "5 ataques extras contra monstros de nível 1 ou menor."),
            _hab_prog("Domínio de Combate Avançado", "2 ataques extras contra monstros N2 e 1 ataque extra contra monstros N3."),
        ],
        22: [
            _hab_prog("Espaço de Batalha (Consciência Tática)", "Bônus de manobras: esquiva +4, desengajar 0, evasão +6, flanquear +3, ataque pelas costas +4."),
        ],
        24: [
            _hab_prog("Domínio de Combate", "6 ataques extras contra monstros de nível 1 ou menor."),
            _hab_prog("Domínio de Combate Avançado", "3 ataques extras vs N2, 2 ataques extras vs N3 e 1 ataque extra vs N4."),
        ],
    }
    progressao = [
        _linha_prog(n, "d10" if n <= 10 else "+4 PV", n, ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    return {
        "id": "combatente",
        "nome": "Combatente",
        "paginas_livro": "36–39",
        "atributo_principal": "forca",
        "dado_vida": "d10",
        "pv_apos_nivel_10": 4,
        "disposicao": "qualquer",
        "armas": {"qualquer": True, "lista": ["Qualquer"], "observacao": None},
        "armaduras": {"qualquer": True, "nenhuma": False, "lista": ["Qualquer"], "observacao": None},
        "conjurador": False,
        "descricao": "O guerreiro arquetípico, superior em maestria marcial, especialização de armas e domínio do combate armado.",
        "habilidades": [
            {
                "id": "especializacao_em_armas",
                "nome": "Especialização em Armas",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Escolhe permanentemente 1 arma (corpo a corpo ou distância): +1 ataque/dano (N1–6), +2/+2 (N7–18), +3/+3 (N19+).",
            },
            {
                "id": "dominio_de_combate",
                "nome": "Domínio de Combate",
                "nivel_aquisicao": 4,
                "atributo_teste": None,
                "descricao": "Ataques extras corpo a corpo contra inimigos de nível 1 ou menos (todos os ataques da rodada devem visar alvos qualificados; não combina com Ataque Extra): +1 (N4), +2 (N8), +3 (N12), +4 (N16), +5 (N20), +6 (N24).",
            },
            {
                "id": "ataque_extra",
                "nome": "Ataque Extra",
                "nivel_aquisicao": 10,
                "atributo_teste": None,
                "descricao": "+1 ataque adicional por rodada com qualquer arma (corpo a corpo ou distância). Não combina com Domínio de Combate.",
            },
            {
                "id": "espaco_de_batalha",
                "nome": "Espaço de Batalha (Consciência Tática)",
                "nivel_aquisicao": 13,
                "atributo_teste": None,
                "descricao": "+1 CA usando segunda arma/escudo/objeto defensivo (não se aplica com arma de duas mãos; acumula com escudo). No N17: esquiva +3, desengajar -1, evasão +5, flanquear +2, ataque pelas costas +3. No N22: +4 / 0 / +6 / +3 / +4.",
            },
            {
                "id": "especializacao_avancada_em_armas",
                "nome": "Especialização Avançada em Armas",
                "nivel_aquisicao": 13,
                "atributo_teste": None,
                "descricao": "Segunda especialização em arma (+1/+1 no N13, +2/+2 no N19). Pode acumular na 1ª arma (total +3/+3 no N13 e +5/+5 no N19).",
            },
            {
                "id": "golpe_de_escudo",
                "nome": "Golpe de Escudo",
                "nivel_aquisicao": 14,
                "atributo_teste": None,
                "descricao": "Ataca com escudo de metal médio (1d4) ou grande (1d6) sem penalidade (perde bônus de CA do escudo quando usado ofensivamente). Acumula com Ataque Extra (até 3 ataques/rodada), mas não com Domínio de Combate.",
            },
            {
                "id": "bonus_de_forca",
                "nome": "Bônus de Força",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Força em +1.",
            },
            {
                "id": "dominio_de_combate_avancado",
                "nome": "Domínio de Combate Avançado",
                "nivel_aquisicao": 16,
                "atributo_teste": None,
                "descricao": "Estende Domínio de Combate para criaturas de nível 2 (N16: +1; N20: +2; N24: +3), nível 3 (N20: +1; N24: +2) e nível 4 (N24: +1).",
            },
            {
                "id": "bonus_de_atributo",
                "nome": "Bônus de Atributo",
                "nivel_aquisicao": 19,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente Força ou Destreza em +1.",
            },
        ],
        "progressao": progressao,
    }


def construir_classes_01() -> dict[str, Any]:
    """Monta o dicionário completo de `dados/dadosc&c/classes01.json` (Leva 01)."""
    return {
        "metadados": {
            "sistema": "Castles & Crusades",
            "edicao": "1ª Edição Brasileira (Livro do Jogador)",
            "arquivo_fonte": "ref/cc/C&C Classes 01.pdf",
            "paginas_livro": "16–39",
            "total_paginas_pdf": 24,
            "leva": 1,
            "niveis_cobertos": "1–24",
            "versao_schema": 1,
            "idioma": "pt-BR",
        },
        "classes": [
            _barbaro(),
            _bardo(),
            _cavaleiro(),
            _clerigo(),
            _combatente(),
        ],
    }


def validar_classes_01(dados: dict[str, Any]) -> None:
    """Valida completude, progressão N1–N24, BpA, PPE, feitiços e cruzamento com `introducao.json`."""
    assert dados["metadados"]["sistema"] == "Castles & Crusades"
    classes = dados["classes"]
    assert len(classes) == 5
    ids = [c["id"] for c in classes]
    assert ids == ["barbaro", "bardo", "cavaleiro", "clerigo", "combatente"]

    intro = json.loads(CAMINHO_INTRODUCAO.read_text(encoding="utf-8"))
    ids_intro = {c["id"] for c in intro["classes_introducao"]["classes"]}
    atbs_validos = {a["id"] for a in intro["atributos"]["lista"]}

    for cls in classes:
        assert cls["id"] in ids_intro
        assert cls["atributo_principal"] in atbs_validos
        prog = cls["progressao"]
        assert len(prog) == 24, f"{cls['id']} deve ter 24 níveis de progressão"
        assert [p["nivel"] for p in prog] == list(range(1, 25))
        # PPE estritamente crescente
        ppes = [p["ppe"] for p in prog]
        assert ppes[0] == 0
        assert all(ppes[i] < ppes[i + 1] for i in range(len(ppes) - 1)), f"PPE fora de ordem em {cls['id']}"
        # BpA monotônico não-decrescente
        bpas = [p["bpa"] for p in prog]
        assert all(bpas[i] <= bpas[i + 1] for i in range(len(bpas) - 1)), f"BpA fora de ordem em {cls['id']}"

    # Checagens específicas
    por_id = {c["id"]: c for c in classes}
    assert por_id["combatente"]["progressao"][0]["bpa"] == 1
    assert por_id["combatente"]["progressao"][-1]["bpa"] == 24
    assert por_id["barbaro"]["progressao"][0]["bpa"] == 0
    assert por_id["barbaro"]["progressao"][-1]["bpa"] == 23
    assert por_id["clerigo"]["progressao"][0]["bpa"] == 0
    assert por_id["clerigo"]["progressao"][-1]["bpa"] == 12
    assert len(por_id["clerigo"]["conjuracao"]["feiticos_diarios"]) == 24
    assert por_id["clerigo"]["conjuracao"]["feiticos_diarios"]["1"] == {"0": 3, "1": 1}
    assert por_id["clerigo"]["conjuracao"]["feiticos_diarios"]["24"] == {
        "0": 8, "1": 7, "2": 7, "3": 6, "4": 6, "5": 6, "6": 6, "7": 5, "8": 4, "9": 4
    }
    assert len(por_id["cavaleiro"]["codigo_de_honra_virtudes"]) == 12
    assert len(por_id["bardo"]["habilidades"][7]["tabela_efeitos"]) == 4


def main() -> None:
    """Gera `dados/dadosc&c/classes01.json`, recarrega do disco e valida."""
    dados = construir_classes_01()
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_SAIDA.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    recarregado = json.loads(CAMINHO_SAIDA.read_text(encoding="utf-8"))
    validar_classes_01(recarregado)
    total_habs = sum(len(c["habilidades"]) for c in recarregado["classes"])
    print(f"OK — {CAMINHO_SAIDA.relative_to(RAIZ_PROJETO)} gerado e validado com sucesso!")
    print(
        f"Classes: {len(recarregado['classes'])} (Bárbaro, Bardo, Cavaleiro, Clérigo, Combatente) | "
        f"Níveis por classe: 24 | Habilidades detalhadas: {total_habs} | "
        f"Feitiços diários Clérigo: 24 níveis (círculos 0–9)"
    )


if __name__ == "__main__":
    main()
