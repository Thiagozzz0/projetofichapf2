"""Gerador e validador de dados/dadosc&c/classes02.json (Leva 02: Druida, Explorador, Ilusionista, Lutador) a partir de ref/cc/C&C classes 02.pdf (pp. 40–62)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "dadosc&c" / "classes02.json"
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


def _druida() -> dict[str, Any]:
    ppes = [
        0, 2001, 4251, 8501, 17001, 35001, 70001, 180001, 275001, 400001, 525001, 650001,
        825001, 1000001, 1175001, 1350001, 1525001, 1700001, 1875001, 2050001, 2225001, 2400001, 2575001, 2750001,
    ]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Conjuração", "Conjura magias divinas (feitiços bônus com Sabedoria 13-15 [1º], 16-17 [2º], 18-19 [3º])."),
            _hab_prog("Idioma Adicional", "Aprende Druídico (linguagem secreta dos druidas)."),
            _hab_prog("Conhecimento da Natureza", "Encontra abrigo, busca comida/água e identifica espécies de plantas e animais.", "sabedoria"),
        ],
        2: [
            _hab_prog("Resistência Elemental", "+2 em JP contra ataques de ar, terra, fogo, água, frio e relâmpagos."),
        ],
        3: [
            _hab_prog("Passo Silvestre", "Move-se pela mata densa sem impedimentos e sem deixar rastros."),
        ],
        6: [
            _hab_prog("Forma do Totem", "Assume a forma de 1 animal pequeno ou médio (1x/dia, seleção permanente, cura 1d4 PV)."),
        ],
        7: [
            _hab_prog("Forma do Totem", "Escolhe uma 2ª forma de animal pequeno ou médio (1x/dia, seleção permanente)."),
        ],
        8: [
            _hab_prog("Forma do Totem", "Escolhe uma 3ª forma de animal pequeno ou médio (1x/dia, seleção permanente)."),
        ],
        12: [
            _hab_prog("Forma do Totem", "1x/dia assume uma das formas de totem em tamanho Grande, curando 5d8 PV.", "sabedoria"),
        ],
        13: [
            _hab_prog("Conhecimento Avançado da Natureza", "Expande Conhecimento da Natureza para uma 2ª região/bioma."),
            _hab_prog("Resistência Elemental Avançada", "Bônus de Resistência Elemental aumenta para +3."),
        ],
        15: [
            _hab_prog("Forma do Totem", "Pode assumir forma de totem 2x/dia."),
            _hab_prog("Bônus de Sabedoria", "Ganha +1 ponto permanente em Sabedoria."),
        ],
        18: [
            _hab_prog("Resistência Elemental Avançada", "Bônus de Resistência Elemental aumenta para +4."),
            _hab_prog("Dispersar Criaturas da Mata", "Dispersa animais, feras, plantas ou pragas da sua região.", "carisma"),
            _hab_prog("Forma do Totem", "Pode assumir forma de totem 3x/dia."),
        ],
        20: [
            _hab_prog("Recordação Perfeita", "Recorda 1x/dia feitiço de nível 0 conjurado anteriormente (ND 0).", "sabedoria"),
            _hab_prog("Maestria Elemental", "Imunidade ao dano de 1 elemento escolhido e possibilidade de redirecionar feitiços dele."),
        ],
        21: [
            _hab_prog("Linguagem das Terras Selvagens", "Compreende e se comunica com pássaros, feras, árvores e plantas."),
            _hab_prog("Conhecimento Avançado da Natureza", "Ganha uma 3ª região/bioma de especialização."),
        ],
        22: [
            _hab_prog("Resistência Elemental Avançada", "Bônus de Resistência Elemental aumenta para +5."),
        ],
        24: [
            _hab_prog("Recordação Perfeita", "Recorda 1x/dia feitiço de 1º nível conjurado anteriormente (ND 0).", "sabedoria"),
            _hab_prog("Despertar o Espírito das Matas", "Desperta consciência comparável à humana em plantas e animais."),
        ],
    }
    progressao = [
        _linha_prog(n, "d8" if n <= 10 else "+3 PV", n // 2, ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
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
        "id": "druida",
        "nome": "Druida",
        "paginas_livro": "40–44",
        "atributo_principal": "sabedoria",
        "dado_vida": "d8",
        "pv_apos_nivel_10": 3,
        "disposicao": "neutra (qualquer)",
        "armas": {
            "qualquer": False,
            "lista": [
                "Arco", "Clava", "Adaga", "Dardo", "Machadinha", "Martelos",
                "Foices", "Funda", "Lanças", "Espada (todas)", "Cajado",
            ],
            "observacao": "Usa armas de matérias-primas naturais (madeira, couro, pedra, ferro/cobre forjado a frio; evita aço/bronze forjados).",
        },
        "armaduras": {
            "qualquer": False,
            "nenhuma": False,
            "lista": ["Couro Cozido", "Laminar de Couro", "Peles", "Couro", "Cota de Couro", "Couro Batido"],
            "observacao": "Apenas armaduras naturais (couro/madeira); escudos de madeira e capuz de couro.",
        },
        "idiomas_bonus_disponiveis": ["Druídico (secreto)", "Aquan", "Auran", "Élfico", "Fada", "Gigante", "Gnomo", "Silvano", "Terran"],
        "conjurador": True,
        "conjuracao": {
            "tradicao": "divina_natural",
            "atributo_conjuracao": "sabedoria",
            "preparacao": "oracao",
            "feiticos_bonus_por_atributo": [
                {"min": 13, "max": 15, "circulo": 1, "quantidade": 1},
                {"min": 16, "max": 17, "circulo": 2, "quantidade": 1},
                {"min": 18, "max": 19, "circulo": 3, "quantidade": 1},
            ],
            "feiticos_bonus_cumulativos": True,
            "feiticos_bonus_requer_acesso_circulo": True,
            "feiticos_diarios": feiticos_diarios,
        },
        "descricao": "Guardiões da ordem natural que comungam com os espíritos da terra, da água, do vento e da vida selvagem.",
        "habilidades": [
            {
                "id": "idiomas_bonus_druida",
                "nome": "Idiomas Bônus (Druídico)",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Conhece o idioma secreto Druídico (proibido ensinar a não-druidas). Com INT suficiente, pode aprender Aquan, Auran, Élfico, Fada, Gigante, Gnomo, Silvano e Terran.",
            },
            {
                "id": "conhecimento_da_natureza",
                "nome": "Conhecimento da Natureza",
                "nivel_aquisicao": 1,
                "atributo_teste": "sabedoria",
                "descricao": "Identifica plantas, animais e água contaminada sem teste no bioma nativo (teste de Sabedoria em biomas desconhecidos). Sustenta a si mesmo sem teste; 6 h alimenta 2d4 pessoas (até 3 tentativas/dia: 2ª com teste SAB +2d4, 3ª com SAB -4 +1d4; total 5–20 criaturas).",
            },
            {
                "id": "feiticos_druida",
                "nome": "Feitiços (Magia Divina)",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Prepara e conjura feitiços da lista de druida via oração conforme a Tabela de Feitiços por Dia + Feitiços Bônus cumulativos por Sabedoria.",
            },
            {
                "id": "resistencia_elemental",
                "nome": "Resistência Elemental",
                "nivel_aquisicao": 2,
                "atributo_teste": None,
                "descricao": "+2 em JP contra ataques de fogo, água, terra, ar, frio e relâmpagos (evolui para +3 no N13, +4 no N18 e +5 no N22).",
            },
            {
                "id": "passo_silvestre",
                "nome": "Passo Silvestre",
                "nivel_aquisicao": 3,
                "atributo_teste": None,
                "descricao": "Move-se sem impedimentos por mata densa e vegetação natural sem deixar rastros (não se aplica a vegetação encantada).",
            },
            {
                "id": "forma_do_totem",
                "nome": "A Forma do Totem",
                "nivel_aquisicao": 6,
                "atributo_teste": None,
                "descricao": "Escolhe forma animal pequena ou média permanente (como polimorfar a si mesmo, cura 1d4 PV; novas formas no N7 e N8). No N12 assume versão Grande 1x/dia curando 5d8 PV. Usos diários aumentam para 2x/dia (N15) e 3x/dia (N18).",
            },
            {
                "id": "conhecimento_avancado_da_natureza",
                "nome": "Conhecimento Avançado da Natureza",
                "nivel_aquisicao": 13,
                "atributo_teste": None,
                "descricao": "Adiciona uma 2ª região/bioma de especialização no N13 e uma 3ª região/bioma no N21.",
            },
            {
                "id": "bonus_de_sabedoria",
                "nome": "Bônus de Sabedoria",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Sabedoria em +1.",
            },
            {
                "id": "dispersar_criaturas_da_mata",
                "nome": "Dispersar Criaturas da Mata",
                "nivel_aquisicao": 18,
                "atributo_teste": "carisma",
                "descricao": "Teste de Carisma (ND = total de níveis das criaturas) para afugentar animais, bestas, plantas ou pragas nativos das suas regiões; limite diário sem penalidade de (10 + mod. CAR) níveis.",
            },
            {
                "id": "recordacao_perfeita",
                "nome": "Recordação Perfeita",
                "nivel_aquisicao": 20,
                "atributo_teste": "sabedoria",
                "descricao": "Teste de Sabedoria (ND 0) para recordar 1x/dia um feitiço de druida já conjurado de nível 0 (N20) ou de 1º nível (N24).",
            },
            {
                "id": "maestria_elemental",
                "nome": "Maestria Elemental",
                "nivel_aquisicao": 20,
                "atributo_teste": "sabedoria",
                "descricao": "Imunidade a 1 elemento escolhido (fogo/calor, eletricidade, gelo/frio, terra, água ou ar). Com JP Sabedoria (ND = nível do atacante), redireciona feitiços desse elemento contra outro alvo dentro do alcance.",
            },
            {
                "id": "linguagem_das_terras_selvagens",
                "nome": "Linguagem das Terras Selvagens",
                "nivel_aquisicao": 21,
                "atributo_teste": None,
                "descricao": "Compreende a comunicação natural de todos os pássaros, feras, árvores e plantas.",
            },
            {
                "id": "despertar_o_espirito_das_matas",
                "nome": "Despertar o Espírito das Matas",
                "nivel_aquisicao": 24,
                "atributo_teste": None,
                "descricao": "Após vários dias, desperta consciência comparável à humana em uma planta ou animal (+2 níveis, PV máximos, +2 CA, dano e JP; +1 ser a cada 2 níveis após N24; limite total de 5 × Carisma em níveis).",
            },
        ],
        "progressao": progressao,
    }


def _explorador() -> dict[str, Any]:
    ppes = [
        0, 2251, 4501, 9001, 18001, 40001, 75001, 150001, 250001, 500001, 725001, 950001,
        1175001, 1400001, 1625001, 1850001, 2075001, 2300001, 2525001, 2750001, 2975001, 3200001, 3425001, 3650001,
    ]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Combate Devastador", "Dano +1 por nível contra humanoides e gigantes (requer armadura permitida)."),
            _hab_prog("Camuflagem (Ocultar)", "Oculta-se em áreas selvagens.", "destreza"),
            _hab_prog("Retardar/Neutralizar Venenos", "Retarda veneno natural por 1 h/nível (ou neutraliza se superar em 6+).", "sabedoria"),
            _hab_prog("Mover-se em Silêncio", "Move-se silenciosamente em áreas selvagens.", "destreza"),
            _hab_prog("Alpinismo", "Escala superfícies naturais sem teste e encostas perigosas com teste.", "destreza"),
            _hab_prog("Armadilhas", "Detecta (+2 procurando), constrói e desativa armadilhas selvagens simples.", "sabedoria"),
            _hab_prog("Sobrevivência", "Encontra abrigo, comida e água para si e grupos (2d4 em 8 h), norte e fogueira.", "sabedoria"),
            _hab_prog("Rastrear", "Rastreia criaturas ou esconde rastros (+2 vs humanoides/gigantes).", "sabedoria"),
        ],
        3: [
            _hab_prog("Rastrear", "Discerne características marcantes das criaturas rastreadas.", "sabedoria"),
        ],
        5: [
            _hab_prog("Camuflagem (Ocultar)", "Pode camuflar-se e mover-se em silêncio ao mesmo tempo com penalidade de -5.", "destreza"),
            _hab_prog("Rastrear", "Determina o tipo específico das criaturas rastreadas.", "sabedoria"),
        ],
        6: [
            _hab_prog("Inimigo Predileto", "+2 na CA, no ataque e no rastreamento contra um tipo específico de criatura; neutraliza seus venenos."),
        ],
        13: [
            _hab_prog("Encontrar o Caminho", "Reduz pela metade penalidades de movimento de terreno (1/4 para aliados)."),
            _hab_prog("Armadilheiro", "Bônus de procura aumenta para +3; armadilhas criadas causam 2d4 de dano.", "sabedoria"),
            _hab_prog("Inimigo Predileto Avançado", "Bônus contra inimigo predileto aumenta para +3 (ataque, CA, rastrear)."),
        ],
        15: [
            _hab_prog("Instintos de Sobrevivência", "+2 em testes de Sabedoria contra surpresa.", "sabedoria"),
            _hab_prog("Bônus de Força", "Ganha +1 ponto permanente em Força."),
        ],
        17: [
            _hab_prog("Instintos de Sobrevivência", "+3 em testes de Sabedoria contra surpresa."),
            _hab_prog("Rastreamento Avançado", "Determina número exato, composição, armamento, velocidade, hábitos e prevê rota/destino.", "sabedoria"),
        ],
        18: [
            _hab_prog("Armadilheiro", "Bônus de procura +4; armadilhas criadas causam 3d4 de dano.", "sabedoria"),
        ],
        19: [
            _hab_prog("Instintos de Sobrevivência", "+4 em testes de Sabedoria contra surpresa.", "sabedoria"),
        ],
        20: [
            _hab_prog("Inimigo Predileto Avançado", "Intimida até 15 inimigos prediletos (-2 em ataque, dano e testes de atributo).", "carisma"),
        ],
        21: [
            _hab_prog("Instintos de Sobrevivência", "+5 em testes de Sabedoria contra surpresa."),
        ],
        23: [
            _hab_prog("Instintos de Sobrevivência", "+6 em testes de Sabedoria contra surpresa.", "sabedoria"),
        ],
        24: [
            _hab_prog("Armadilheiro", "Bônus de procura +6; armadilhas criadas causam 4d4 de dano.", "sabedoria"),
        ],
    }
    progressao = [
        _linha_prog(n, "d10" if n <= 10 else "+4 PV", n - 1, ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    return {
        "id": "explorador",
        "nome": "Explorador",
        "paginas_livro": "45–53",
        "atributo_principal": "forca",
        "dado_vida": "d10",
        "pv_apos_nivel_10": 4,
        "disposicao": "qualquer",
        "armas": {"qualquer": True, "lista": ["Qualquer"], "observacao": None},
        "armaduras": {
            "qualquer": False,
            "nenhuma": False,
            "lista": [
                "Peitorais", "Cota de Malha", "Camisa de Malha", "Couro Cozido", "Conjunto Grego",
                "Couro", "Coifa de Malha", "Jaqueta de Couro", "Gibão de Peles", "Cota de Anéis",
                "Cota de Escamas", "Couro Batido",
            ],
            "observacao": "Escudo até médio e elmo até normal; armaduras fora da lista bloqueiam Combate Devastador, Camuflagem, Mover-se em Silêncio, Alpinismo e bônus de combate de Inimigo Predileto.",
        },
        "conjurador": False,
        "descricao": "Batedores, caçadores e guardiões das fronteiras selvagens, mestres em rastreamento, sobrevivência e combate contra humanoides e gigantes.",
        "tabelas_rastreamento": {
            "penalidade_nao_explorador": -10,
            "bonus_bastao_rastreamento": 1,
            "terreno": [
                {"terreno": "Depressões", "nd": 2},
                {"terreno": "Deserto", "nd": 2},
                {"terreno": "Floresta transitória", "nd": 0},
                {"terreno": "Floresta nortenha ou sulista", "nd": 0},
                {"terreno": "Terras baixas", "nd": 1},
                {"terreno": "Montanhas e colinas", "nd": 4},
                {"terreno": "Rios e leitos", "nd": 3},
                {"terreno": "Zonas úmidas/pântanos/brejos", "nd": 4},
            ],
            "periodo_do_dia": [
                {"periodo": "Manhã", "nd": -1},
                {"periodo": "Metade da Manhã", "nd": 0},
                {"periodo": "Meio Dia", "nd": 1},
                {"periodo": "Metade da Tarde", "nd": -1},
                {"periodo": "Fim da Tarde", "nd": 0},
                {"periodo": "Crepúsculo", "nd": 2},
                {"periodo": "Noite", "nd": 9},
            ],
            "tempo_decorrido": [
                {"tempo": "6 hrs", "nd": -2},
                {"tempo": "12 hrs", "nd": 0},
                {"tempo": "18 hrs", "nd": 2},
                {"tempo": "24 hrs+", "nd": 4},
            ],
            "tamanho_criatura": [
                {"tamanho": "Minúsculo", "nd": 7},
                {"tamanho": "Pequeno", "nd": 3},
                {"tamanho": "Médio", "nd": 0},
                {"tamanho": "Grande", "nd": -3},
                {"tamanho": "Enorme", "nd": -5},
            ],
            "quantidade_encontrada": [
                {"quantidade": "1", "nd": 4},
                {"quantidade": "2-4", "nd": 2},
                {"quantidade": "5-13", "nd": 1},
                {"quantidade": "14+", "nd": 0},
            ],
            "condicao_climatica": [
                {"clima": "Seco", "nd": 0},
                {"clima": "Chuvoso", "nd": -1},
                {"clima": "Nevado", "nd": -3},
            ],
            "tipo_de_solo": [
                {"condicao": "Brejo", "nd": 4},
                {"condicao": "Seco", "nd": 0},
                {"condicao": "Lamacento", "nd": -2},
                {"condicao": "Pisado", "nd": 1},
                {"condicao": "Batido", "nd": 1},
                {"condicao": "Nevado", "nd": -5, "observacao": "Não acumula com clima Nevado (juntos contam como -5)."},
                {"condicao": "Trilha", "nd": 0},
            ],
        },
        "habilidades": [
            {
                "id": "combate_devastador",
                "nome": "Combate Devastador",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "+1 de dano por nível contra humanoides (bugbears, gnolls, goblins, hobgoblins, kobolds, orcs etc.) e gigantes (gigantes, ogros etc.). Requer armadura permitida.",
            },
            {
                "id": "camuflagem",
                "nome": "Camuflagem (Ocultar)",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Oculta-se em áreas selvagens (-10 se observador momentaneamente distraído). A partir do N5 pode mover-se em silêncio simultaneamente com -5 (1/4 do movimento). Requer armadura permitida.",
            },
            {
                "id": "retardar_neutralizar_venenos",
                "nome": "Retardar/Neutralizar Venenos",
                "nivel_aquisicao": 1,
                "atributo_teste": "sabedoria",
                "descricao": "1 rodada, 1 tentativa, com ervas/antídotos para venenos naturais familiares (ou do Inimigo Predileto). Retarda por 1 h/nível; se exceder o alvo em 6+, neutraliza o veneno.",
            },
            {
                "id": "mover_se_em_silencio",
                "nome": "Mover-se em Silêncio",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Apenas em áreas selvagens e com armadura permitida: até 1/2 movimento sem penalidade; acima até velocidade normal -5; correndo/investida -20.",
            },
            {
                "id": "alpinismo",
                "nome": "Alpinismo",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Escala encostas naturais sem teste; encostas perigosas/invertidas com teste DES a 1/2 movimento (falha por 5+ causa queda). Mãos livres e armadura permitida.",
            },
            {
                "id": "armadilhas",
                "nome": "Armadilhas",
                "nivel_aquisicao": 1,
                "atributo_teste": "sabedoria",
                "descricao": "Detecta armadilhas selvagens não mágicas a 7,5 m (+2 procurando ativamente), desativa armadilhas simples sem teste e constrói laços (até tamanho médio) ou poços (1d4 dano, JP DES metade).",
            },
            {
                "id": "sobrevivencia",
                "nome": "Sobrevivência",
                "nivel_aquisicao": 1,
                "atributo_teste": "sabedoria",
                "descricao": "Abrigo, comida e água para si sem teste; fogueira em 1d10 min; norte verdadeiro. Em 8 h alimenta 2d4 pessoas sem teste (2ª tentativa de 8 h com teste SAB para +2d4, máx. 2x/dia).",
            },
            {
                "id": "rastrear",
                "nome": "Rastrear",
                "nivel_aquisicao": 1,
                "atributo_teste": "sabedoria",
                "descricao": "Rastreia ou esconde rastros em áreas selvagens (+2 vs humanoides/gigantes). N1: quantidade geral e categoria; N3: características marcantes; N5: tipo específico de criatura.",
            },
            {
                "id": "inimigo_predileto",
                "nome": "Inimigo Predileto",
                "nivel_aquisicao": 6,
                "atributo_teste": None,
                "descricao": "Escolhe 1 tipo de criatura: +2 ataque, +2 CA (requer armadura permitida), +2 rastrear e pode neutralizar venenos desse inimigo. No N13 os bônus sobem para +3; no N20 pode intimidar até 15 inimigos prediletos (teste CAR, -2 em ataque, dano e testes).",
            },
            {
                "id": "encontrar_o_caminho",
                "nome": "Encontrar o Caminho",
                "nivel_aquisicao": 13,
                "atributo_teste": None,
                "descricao": "Reduz pela metade penalidades de movimento de terrenos terrestres conhecidos (inclusive escalada); aliados que o sigam reduzem em 1/4.",
            },
            {
                "id": "armadilheiro",
                "nome": "Armadilheiro",
                "nivel_aquisicao": 13,
                "atributo_teste": "sabedoria",
                "descricao": "Evolução de Armadilhas: N13 (+3 procura / 2d4 dano / animais grandes), N18 (+4 procura / 3d4 dano), N24 (+6 procura / 4d4 dano).",
            },
            {
                "id": "instintos_de_sobrevivencia",
                "nome": "Instintos de Sobrevivência",
                "nivel_aquisicao": 15,
                "atributo_teste": "sabedoria",
                "descricao": "Bônus em testes de Sabedoria contra surpresa: +2 (N15), +3 (N17), +4 (N19), +5 (N21), +6 (N23).",
            },
            {
                "id": "bonus_de_forca",
                "nome": "Bônus de Força",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Força em +1.",
            },
            {
                "id": "rastreamento_avancado",
                "nome": "Rastreamento Avançado",
                "nivel_aquisicao": 17,
                "atributo_teste": "sabedoria",
                "descricao": "Determina número preciso, composição, armamento, velocidade e hábitos do grupo rastreado, além de testes adicionais para prever rota e destino final.",
            },
        ],
        "progressao": progressao,
    }


def _ilusionista() -> dict[str, Any]:
    ppes = [
        0, 2601, 5201, 10401, 20801, 42501, 85001, 170001, 340001, 500001, 750001, 900001,
        1050001, 1200001, 1350001, 1500001, 1650001, 1800001, 1950001, 2100001, 2250001, 2400001, 2550001, 2700001,
    ]
    bpas = [0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Conjuração", "Conjura magias arcanas de ilusão (feitiços bônus com Inteligência 13-15 [1º], 16-17 [2º], 18-19 [3º])."),
            _hab_prog("Disfarce", "Disfarça-se e personifica outra pessoa (1d3×10 min).", "carisma"),
            _hab_prog("Sentidos Aguçados", "+1 de bônus em todas as jogadas de proteção contra ilusões."),
        ],
        4: [
            _hab_prog("Sentidos Aguçados", "+2 de bônus em jogadas de proteção contra ilusões."),
        ],
        7: [
            _hab_prog("Sentidos Aguçados", "+3 de bônus em jogadas de proteção contra ilusões."),
        ],
        10: [
            _hab_prog("Sentidos Aguçados", "+4 de bônus em jogadas de proteção contra ilusões."),
        ],
        13: [
            _hab_prog("Ver o Invisível", "Enxerga localização geral e movimento de pessoas/objetos invisíveis.", "inteligencia"),
            _hab_prog("Sentidos Aguçados", "+5 de bônus em jogadas de proteção contra ilusões."),
        ],
        15: [
            _hab_prog("Bônus de Inteligência", "Ganha +1 ponto permanente em Inteligência."),
        ],
        16: [
            _hab_prog("Detectar Magia", "Após 5 rodadas de estudo, detecta magia e identifica sua origem.", "inteligencia"),
            _hab_prog("Sentidos Aguçados", "+6 de bônus em jogadas de proteção contra ilusões."),
        ],
        18: [
            _hab_prog("Detectar Magia", "Determina o nível de poder relativo do item e sua importância.", "inteligencia"),
            _hab_prog("Ver o Invisível", "Determina forma e tamanho de pessoas/objetos invisíveis.", "inteligencia"),
        ],
        19: [
            _hab_prog("Alterar-se", "1x/dia altera aparência, raça, cheiro, som e tato até dissipar."),
        ],
        20: [
            _hab_prog("Recordação Perfeita", "Recobra 1x/dia magia de nível 0 conjurada anteriormente (ND 0).", "inteligencia"),
        ],
        24: [
            _hab_prog("Ver o Invisível", "Segunda visão permanente equivalente ao feitiço Verdade Revelada.", "inteligencia"),
            _hab_prog("Recordação Perfeita", "Recobra 1x/dia feitiço de 1º nível conjurado anteriormente (ND 0).", "inteligencia"),
            _hab_prog("Magnum Opus", "Ritual de 1 dia (1x/mês) que cria objeto, ser ou área ilusória com 1%/nível de tornar-se real."),
        ],
    }
    progressao = [
        _linha_prog(n, "d4" if n <= 10 else "+1 PV", bpas[n - 1], ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    feiticos_diarios: dict[str, dict[str, int]] = {
        "1":  {"0": 4, "1": 2},
        "2":  {"0": 4, "1": 3},
        "3":  {"0": 4, "1": 3, "2": 1},
        "4":  {"0": 4, "1": 3, "2": 2},
        "5":  {"0": 5, "1": 4, "2": 2, "3": 1},
        "6":  {"0": 5, "1": 4, "2": 3, "3": 2},
        "7":  {"0": 5, "1": 4, "2": 3, "3": 2, "4": 1},
        "8":  {"0": 5, "1": 4, "2": 3, "3": 3, "4": 2},
        "9":  {"0": 5, "1": 5, "2": 4, "3": 3, "4": 2, "5": 1},
        "10": {"0": 6, "1": 5, "2": 4, "3": 3, "4": 3, "5": 2},
        "11": {"0": 6, "1": 5, "2": 4, "3": 4, "4": 3, "5": 2, "6": 1},
        "12": {"0": 6, "1": 5, "2": 4, "3": 4, "4": 3, "5": 3, "6": 2},
        "13": {"0": 6, "1": 5, "2": 5, "3": 4, "4": 4, "5": 3, "6": 2, "7": 1},
        "14": {"0": 6, "1": 6, "2": 5, "3": 4, "4": 4, "5": 3, "6": 3, "7": 2},
        "15": {"0": 6, "1": 6, "2": 5, "3": 5, "4": 4, "5": 4, "6": 3, "7": 2, "8": 1},
        "16": {"0": 7, "1": 6, "2": 5, "3": 5, "4": 4, "5": 4, "6": 3, "7": 3, "8": 2},
        "17": {"0": 7, "1": 6, "2": 5, "3": 5, "4": 5, "5": 4, "6": 4, "7": 3, "8": 2, "9": 1},
        "18": {"0": 7, "1": 6, "2": 6, "3": 5, "4": 5, "5": 4, "6": 4, "7": 3, "8": 3, "9": 2},
        "19": {"0": 7, "1": 6, "2": 6, "3": 5, "4": 5, "5": 5, "6": 4, "7": 4, "8": 3, "9": 2},
        "20": {"0": 7, "1": 7, "2": 6, "3": 6, "4": 5, "5": 5, "6": 4, "7": 4, "8": 3, "9": 3},
        "21": {"0": 7, "1": 7, "2": 6, "3": 6, "4": 5, "5": 5, "6": 5, "7": 4, "8": 4, "9": 3},
        "22": {"0": 7, "1": 7, "2": 6, "3": 6, "4": 6, "5": 5, "6": 5, "7": 4, "8": 4, "9": 3},
        "23": {"0": 8, "1": 7, "2": 6, "3": 6, "4": 6, "5": 5, "6": 5, "7": 5, "8": 4, "9": 4},
        "24": {"0": 8, "1": 7, "2": 7, "3": 6, "4": 6, "5": 6, "6": 5, "7": 5, "8": 4, "9": 4},
    }
    return {
        "id": "ilusionista",
        "nome": "Ilusionista",
        "paginas_livro": "54–57",
        "atributo_principal": "inteligencia",
        "dado_vida": "d4",
        "pv_apos_nivel_10": 1,
        "disposicao": "qualquer",
        "armas": {
            "qualquer": False,
            "lista": ["Clava", "Adaga", "Lança de Mão", "Cajado"],
            "observacao": None,
        },
        "armaduras": {
            "qualquer": False,
            "nenhuma": True,
            "lista": [],
            "observacao": "Qualquer uso de armadura ou escudo impede o ilusionista de conjurar feitiços.",
        },
        "conjurador": True,
        "conjuracao": {
            "tradicao": "arcana_ilusao",
            "atributo_conjuracao": "inteligencia",
            "preparacao": "grimorio",
            "grimorio_inicial": "Igual ao número total de feitiços que pode conjurar no 1º nível (incluindo feitiços bônus de Inteligência).",
            "feiticos_bonus_por_atributo": [
                {"min": 13, "max": 15, "circulo": 1, "quantidade": 1},
                {"min": 16, "max": 17, "circulo": 2, "quantidade": 1},
                {"min": 18, "max": 19, "circulo": 3, "quantidade": 1},
            ],
            "feiticos_bonus_cumulativos": True,
            "feiticos_bonus_requer_acesso_circulo": True,
            "feiticos_diarios": feiticos_diarios,
        },
        "descricao": "Conjuradores arcanos especializados em manipular sentidos, mentes e percepções até confundir ilusão e realidade.",
        "habilidades": [
            {
                "id": "feiticos_ilusionista",
                "nome": "Feitiços e Grimório",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Prepara feitiços da lista de ilusionista a partir de seu grimório conforme Tabela de Feitiços por Dia + Feitiços Bônus cumulativos por Inteligência. Grimório inicial contém tantos feitiços quanto pode conjurar no N1.",
            },
            {
                "id": "sentidos_agucados",
                "nome": "Sentidos Aguçados",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Bônus em todas as jogadas de proteção contra ilusões: +1 (N1), +2 (N4), +3 (N7), +4 (N10), +5 (N13), +6 (N16).",
            },
            {
                "id": "disfarce",
                "nome": "Disfarce",
                "nivel_aquisicao": 1,
                "atributo_teste": "carisma",
                "descricao": "1d3×10 min (teste secreto pelo GC; altura/peso até ±10%). Modificadores: sexo diferente -2, raça diferente -2, idade -2 a cada 10 anos. Observadores familiarizados ganham +4 (próximos/amigos +8) em INT para perceber.",
            },
            {
                "id": "ver_o_invisivel",
                "nome": "Ver o Invisível",
                "nivel_aquisicao": 13,
                "atributo_teste": "inteligencia",
                "descricao": "N13: percebe localização geral e movimento de alvos invisíveis com teste INT; N18: determina forma e tamanho; N24: segunda visão permanente como Verdade Revelada.",
            },
            {
                "id": "bonus_de_inteligencia",
                "nome": "Bônus de Inteligência",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Inteligência em +1.",
            },
            {
                "id": "detectar_magia_ilusionista",
                "nome": "Detectar Magia",
                "nivel_aquisicao": 16,
                "atributo_teste": "inteligencia",
                "descricao": "Após 5 rodadas de concentração, detecta se um item é mágico e, com teste INT, identifica sua origem (se já conhecida). No N18 determina poder relativo e importância histórica.",
            },
            {
                "id": "alterar_se",
                "nome": "Alterar-se",
                "nivel_aquisicao": 19,
                "atributo_teste": None,
                "descricao": "1x/dia altera sua aparência racial, cheiro, som e sensações táteis até dissipar.",
            },
            {
                "id": "recordacao_perfeita",
                "nome": "Recordação Perfeita",
                "nivel_aquisicao": 20,
                "atributo_teste": "inteligencia",
                "descricao": "Teste de Inteligência (ND 0) para recordar 1x/dia um feitiço já conjurado de nível 0 (N20) ou 1º nível (N24).",
            },
            {
                "id": "magnum_opus",
                "nome": "Magnum Opus",
                "nivel_aquisicao": 24,
                "atributo_teste": None,
                "descricao": "1x/mês (ritual de 1 dia inteiro). Cria objeto, ser (até metade do nível do ilusionista) ou área de 3×3 m por nível; não pode ser dissipado por 1 dia/nível por conjurador inferior; 1% de chance por nível de tornar-se real permanentemente.",
            },
        ],
        "progressao": progressao,
    }


def _lutador() -> dict[str, Any]:
    ppes = [
        0, 1751, 4001, 8501, 20001, 40001, 80001, 160001, 325001, 550001, 750001, 1250001,
        1500001, 1750001, 2000001, 2250001, 2500001, 2750001, 3000001, 3250001, 3500001, 3750001, 4000001, 4250001,
    ]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Movimento Rápido", "Move-se 10,5 m por rodada (com carga leve)."),
            _hab_prog("Corpo de Ferro", "+1 em JP contra doença, veneno, paralisia, polimorfia, petrificação e morte."),
            _hab_prog("Ataque Atordoante", "Atordoa por 1d4 rodadas (JP CON); 1x/rodada, 1x/nível por dia."),
            _hab_prog("Combate Corpo a Corpo", "CA base 11, ataque desarmado 1d4 e +2 para agarrar/subjugar."),
        ],
        2: [
            _hab_prog("Desviar Projéteis", "Desvia projéteis não mágicos 1x/rodada.", "destreza"),
        ],
        3: [
            _hab_prog("Movimento Rápido", "Move-se 12 m por rodada."),
            _hab_prog("Corpo de Ferro", "+2 contra toxinas, paralisia, polimorfia, petrificação e morte."),
            _hab_prog("Punhos de Ferro", "Ataques desarmados atingem como arma mágica +1."),
        ],
        4: [
            _hab_prog("Queda Lenta", "Reduz dano de queda em 6 m próximo a parede/superfície."),
        ],
        5: [
            _hab_prog("Punhos de Ferro", "Ataques desarmados atingem como arma mágica +2."),
        ],
        6: [
            _hab_prog("Movimento Rápido", "Move-se 13,5 m por rodada."),
            _hab_prog("Fingir de Morto", "Diminui funções vitais para parecer morto (1 min/nível)."),
            _hab_prog("Corpo de Ferro", "+3 contra toxinas, paralisia, polimorfia, petrificação e morte."),
            _hab_prog("Desviar Projéteis", "Desvia projéteis 2x/rodada.", "destreza"),
            _hab_prog("Combate Corpo a Corpo", "Ganha ataque secundário desarmado (1d4)."),
            _hab_prog("Queda Lenta", "Reduz dano de queda em 7,5 m."),
        ],
        7: [
            _hab_prog("Cura Rápida (Acelerada)", "Cura 1d4+1 PV por nível a cada dia com descanso completo."),
        ],
        8: [
            _hab_prog("Punhos de Ferro", "Ataques desarmados atingem como arma mágica +3."),
        ],
        9: [
            _hab_prog("Mente de Ferro", "+3 em JP contra confusão, encantamento, medo e efeitos mentais."),
            _hab_prog("Queda Lenta", "Reduz dano de queda em 9 m."),
        ],
        10: [
            _hab_prog("Movimento Rápido", "Move-se 15 m por rodada."),
            _hab_prog("Corpo de Ferro", "+4 contra toxinas, paralisia, polimorfia, petrificação e morte."),
            _hab_prog("Golpe Mortal", "1x/semana: ataque contra alvo de nível inferior pode causar morte instantânea (JP CON)."),
        ],
        11: [
            _hab_prog("Desviar Projéteis", "Desvia projéteis 3x/rodada.", "destreza"),
            _hab_prog("Mente de Ferro", "+4 contra confusão, encantamento, medo e efeitos mentais."),
        ],
        12: [
            _hab_prog("Punhos de Ferro", "Ataques desarmados atingem como arma mágica +4."),
            _hab_prog("Golpe Mortal", "Pode atrasar a morte da vítima em até 1 rodada por nível (ou liberá-la por toque)."),
        ],
        13: [
            _hab_prog("Desviar Golpe", "Desvia um golpe corpo a corpo com teste DES (ND = BpA do oponente).", "destreza"),
            _hab_prog("Queda Lenta", "Reduz dano de queda em 10,5 m."),
        ],
        14: [
            _hab_prog("Mente de Ferro", "+5 contra confusão, encantamento, medo e efeitos mentais."),
        ],
        15: [
            _hab_prog("Bônus de Constituição", "Ganha +1 ponto permanente em Constituição."),
            _hab_prog("Corpo de Ferro", "+5 contra toxinas, paralisia, polimorfia, petrificação e morte."),
        ],
        16: [
            _hab_prog("Desviar Projéteis", "Desvia projéteis 4x/rodada.", "destreza"),
        ],
        17: [
            _hab_prog("Agarrar Arma", "1x/rodada agarra arma do oponente usando ataque de Destreza contra CA 15 + BpA.", "destreza"),
            _hab_prog("Punhos de Ferro", "Ataques desarmados atingem como arma mágica +5."),
        ],
        18: [
            _hab_prog("Reação Rápida", "+1 em jogadas de iniciativa."),
            _hab_prog("Queda Lenta", "Reduz dano de queda em 12 m."),
        ],
        20: [
            _hab_prog("Desviar Projéteis", "Desvia projéteis 5x/rodada.", "destreza"),
            _hab_prog("Maestria em Armas", "Escolhe 1 arma: +1 ataque, dano e testes de atributo, estendendo habilidades marciais."),
        ],
        24: [
            _hab_prog("Reação Rápida", "+2 iniciativa; com resultado 11+ ganha ação extra no fim da rodada."),
        ],
    }
    progressao = [
        _linha_prog(n, "d12" if n <= 10 else "+5 PV", n - 1, ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    tabela_especial = [
        {"nivel": 1,  "ca_base": 11, "ataque_primario": "1d4",  "ataque_secundario": None,   "ataque_terciario": None,  "movimento_m": 10.5},
        {"nivel": 2,  "ca_base": 12, "ataque_primario": "1d6",  "ataque_secundario": None,   "ataque_terciario": None,  "movimento_m": 10.5},
        {"nivel": 3,  "ca_base": 12, "ataque_primario": "1d6",  "ataque_secundario": None,   "ataque_terciario": None,  "movimento_m": 12.0},
        {"nivel": 4,  "ca_base": 13, "ataque_primario": "1d8",  "ataque_secundario": None,   "ataque_terciario": None,  "movimento_m": 12.0},
        {"nivel": 5,  "ca_base": 13, "ataque_primario": "1d8",  "ataque_secundario": None,   "ataque_terciario": None,  "movimento_m": 12.0},
        {"nivel": 6,  "ca_base": 13, "ataque_primario": "1d8",  "ataque_secundario": "1d4",  "ataque_terciario": None,  "movimento_m": 13.5},
        {"nivel": 7,  "ca_base": 14, "ataque_primario": "1d10", "ataque_secundario": "1d4",  "ataque_terciario": None,  "movimento_m": 13.5},
        {"nivel": 8,  "ca_base": 14, "ataque_primario": "1d10", "ataque_secundario": "1d4",  "ataque_terciario": None,  "movimento_m": 13.5},
        {"nivel": 9,  "ca_base": 14, "ataque_primario": "1d10", "ataque_secundario": "1d6",  "ataque_terciario": None,  "movimento_m": 13.5},
        {"nivel": 10, "ca_base": 14, "ataque_primario": "1d10", "ataque_secundario": "1d6",  "ataque_terciario": None,  "movimento_m": 15.0},
        {"nivel": 11, "ca_base": 15, "ataque_primario": "1d10", "ataque_secundario": "1d6",  "ataque_terciario": None,  "movimento_m": 15.0},
        {"nivel": 12, "ca_base": 15, "ataque_primario": "1d10", "ataque_secundario": "1d6",  "ataque_terciario": None,  "movimento_m": 15.0},
        {"nivel": 13, "ca_base": 15, "ataque_primario": "1d10", "ataque_secundario": "1d8",  "ataque_terciario": None,  "movimento_m": 15.0},
        {"nivel": 14, "ca_base": 15, "ataque_primario": "1d10", "ataque_secundario": "1d8",  "ataque_terciario": None,  "movimento_m": 15.0},
        {"nivel": 15, "ca_base": 16, "ataque_primario": "1d10", "ataque_secundario": "1d8",  "ataque_terciario": None,  "movimento_m": 15.0},
        {"nivel": 16, "ca_base": 16, "ataque_primario": "1d10", "ataque_secundario": "1d8",  "ataque_terciario": "1d4", "movimento_m": 15.0},
        {"nivel": 17, "ca_base": 16, "ataque_primario": "1d10", "ataque_secundario": "1d8",  "ataque_terciario": "1d4", "movimento_m": 15.0},
        {"nivel": 18, "ca_base": 16, "ataque_primario": "1d10", "ataque_secundario": "1d10", "ataque_terciario": "1d4", "movimento_m": 15.0},
        {"nivel": 19, "ca_base": 16, "ataque_primario": "1d10", "ataque_secundario": "1d10", "ataque_terciario": "1d6", "movimento_m": 15.0},
        {"nivel": 20, "ca_base": 16, "ataque_primario": "1d10", "ataque_secundario": "1d10", "ataque_terciario": "1d6", "movimento_m": 15.0},
        {"nivel": 21, "ca_base": 17, "ataque_primario": "1d10", "ataque_secundario": "1d10", "ataque_terciario": "1d6", "movimento_m": 15.0},
        {"nivel": 22, "ca_base": 17, "ataque_primario": "1d10", "ataque_secundario": "1d10", "ataque_terciario": "1d8", "movimento_m": 15.0},
        {"nivel": 23, "ca_base": 17, "ataque_primario": "1d10", "ataque_secundario": "1d10", "ataque_terciario": "1d8", "movimento_m": 15.0},
        {"nivel": 24, "ca_base": 17, "ataque_primario": "1d10", "ataque_secundario": "1d10", "ataque_terciario": "1d8", "movimento_m": 15.0},
    ]
    return {
        "id": "lutador",
        "nome": "Lutador",
        "paginas_livro": "58–62",
        "atributo_principal": "constituicao",
        "dado_vida": "d12",
        "pv_apos_nivel_10": 5,
        "disposicao": "qualquer",
        "armas": {
            "qualquer": False,
            "lista": [
                "Aclis", "Zarabatana", "Bola", "Arcos", "Soco Inglês", "Gato de Nove Caudas",
                "Cestus", "Cutelo", "Clava", "Adaga", "Lança de Mão", "Punhal", "Falcione",
                "Gancho com Cabo", "Machado de Mão", "Machadinha", "Espada-Gancho", "Azagaia",
                "Punhal Katar", "Faca", "Mangual Leve", "Maça Leve", "Espada Larga de Nove Anéis",
                "Armas de Haste", "Pedra", "Porrete", "Foice", "Cimitarra", "Foice Longa",
                "Funda", "Lança", "Manopla com Espinhos", "Cajado", "Chicote",
            ],
            "observacao": None,
        },
        "armaduras": {
            "qualquer": False,
            "nenhuma": True,
            "lista": [],
            "observacao": "Não usa armaduras, escudos nem elmos; confia na CA progressiva corporal.",
        },
        "conjurador": False,
        "tabela_habilidades_especiais": tabela_especial,
        "descricao": "Artistas marciais devotados à perfeição do corpo e da mente, transformando o próprio corpo em arma letal.",
        "habilidades": [
            {
                "id": "movimento_rapido",
                "nome": "Movimento Rápido",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Velocidade progressiva de 10,5 m (N1) até 15 m (N10+). Carga média ou pesada reduz para 9 m.",
            },
            {
                "id": "combate_corpo_a_corpo",
                "nome": "Combate Corpo a Corpo",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "CA base progressiva (11 a 17), dano desarmado normal ou contundente (primário 1d4→1d10, secundário no N6 1d4→1d10, terciário no N16 1d4→1d8) e +2 em agarrar/subjugar.",
            },
            {
                "id": "corpo_de_ferro",
                "nome": "Corpo de Ferro",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Bônus em JP contra doença, veneno, paralisia, polimorfia, petrificação e morte: +1 (N1), +2 (N3), +3 (N6; texto diz N4), +4 (N10), +5 (N15).",
            },
            {
                "id": "ataque_atordoante",
                "nome": "Ataque Atordoante",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Declarado antes do ataque primário (1x/rodada, 1x/nível por dia). Causa dano normal; alvo faz JP CON ou fica atordoado por 1d4 rodadas.",
            },
            {
                "id": "desviar_projeteis",
                "nome": "Desviar Projéteis",
                "nivel_aquisicao": 2,
                "atributo_teste": "destreza",
                "descricao": "Com mão livre e ciente do ataque, desvia projéteis não mágicos (não armas de cerco). Usos/rodada: 1 (N2), 2 (N6), 3 (N11), 4 (N16), 5 (N20+). Conta como ataque primário (3+ consome secundário).",
            },
            {
                "id": "punhos_de_ferro",
                "nome": "Punhos de Ferro",
                "nivel_aquisicao": 3,
                "atributo_teste": None,
                "descricao": "Ataques desarmados atingem criaturas vulneráveis apenas a armas mágicas (sem dar bônus real de ataque/dano): +1 (N3), +2 (N5), +3 (N8), +4 (N12), +5 (N17).",
            },
            {
                "id": "queda_lenta",
                "nome": "Queda Lenta",
                "nivel_aquisicao": 4,
                "atributo_teste": None,
                "descricao": "A até 3 m de superfície vertical, reduz altura efetiva da queda em: 6 m (N4), 7,5 m (N6), 9 m (N9), 10,5 m (N13), 12 m (N18).",
            },
            {
                "id": "fingir_de_morto",
                "nome": "Fingir de Morto",
                "nivel_aquisicao": 6,
                "atributo_teste": None,
                "descricao": "Reduz funções vitais aparentando estar morto por 1 minuto por nível.",
            },
            {
                "id": "cura_rapida",
                "nome": "Cura Rápida (Acelerada)",
                "nivel_aquisicao": 7,
                "atributo_teste": None,
                "descricao": "Cura 1d4+1 PV por nível a cada dia mediante 12 h de sono + 6 h de descanso calmo com comida e água.",
            },
            {
                "id": "mente_de_ferro",
                "nome": "Mente de Ferro",
                "nivel_aquisicao": 9,
                "atributo_teste": None,
                "descricao": "Bônus em JP contra confusão, encantamento, medo e efeitos mentais: +3 (N9; texto menciona N7), +4 (N11), +5 (N14).",
            },
            {
                "id": "golpe_mortal",
                "nome": "Golpe Mortal",
                "nivel_aquisicao": 10,
                "atributo_teste": None,
                "descricao": "1x/semana contra alvo de nível inferior (declarado antes). Se causar dano, alvo faz JP CON ou morre instantaneamente. No N12 pode atrasar a morte em até 1 rodada/nível ou liberar por toque.",
            },
            {
                "id": "desviar_golpe",
                "nome": "Desviar Golpe",
                "nivel_aquisicao": 13,
                "atributo_teste": "destreza",
                "descricao": "Desvia um golpe corpo a corpo com teste DES (ND >= BpA do oponente), consumindo o ataque primário.",
            },
            {
                "id": "bonus_de_constituicao",
                "nome": "Bônus de Constituição",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Constituição em +1.",
            },
            {
                "id": "agarrar_arma",
                "nome": "Agarrar Arma",
                "nivel_aquisicao": 17,
                "atributo_teste": "destreza",
                "descricao": "1x/rodada faz ataque usando DES contra CA (15 + BpA do oponente) para agarrar a arma; na rodada seguinte pode tentar arrancar com teste de CON.",
            },
            {
                "id": "reacao_rapida",
                "nome": "Reação Rápida",
                "nivel_aquisicao": 18,
                "atributo_teste": None,
                "descricao": "+1 em iniciativa no N18 (+2 no N24; com resultado 11+ após N24 ganha uma ação adicional no final de cada rodada).",
            },
            {
                "id": "maestria_em_armas",
                "nome": "Maestria em Armas",
                "nivel_aquisicao": 20,
                "atributo_teste": None,
                "descricao": "Escolhe 1 arma: +1 em ataque, dano e testes de atributo ao usá-la, podendo executar atordoar, desviar projéteis, queda lenta e Golpe Mortal com ela.",
            },
        ],
        "progressao": progressao,
    }


def construir_classes_02() -> dict[str, Any]:
    """Monta o dicionário completo de `dados/dadosc&c/classes02.json` (Leva 02)."""
    return {
        "metadados": {
            "sistema": "Castles & Crusades",
            "edicao": "1ª Edição Brasileira (Livro do Jogador)",
            "arquivo_fonte": "ref/cc/C&C classes 02.pdf",
            "paginas_livro": "40–62",
            "total_paginas_pdf": 23,
            "leva": 2,
            "niveis_cobertos": "1–24",
            "versao_schema": 1,
            "idioma": "pt-BR",
        },
        "classes": [
            _druida(),
            _explorador(),
            _ilusionista(),
            _lutador(),
        ],
    }


def validar_classes_02(dados: dict[str, Any]) -> None:
    """Valida completude, progressão N1–N24, tabelas especiais e cruzamento com `introducao.json`."""
    assert dados["metadados"]["sistema"] == "Castles & Crusades"
    classes = dados["classes"]
    assert len(classes) == 4
    assert [c["id"] for c in classes] == ["druida", "explorador", "ilusionista", "lutador"]

    intro = json.loads(CAMINHO_INTRODUCAO.read_text(encoding="utf-8"))
    ids_intro = {c["id"] for c in intro["classes_introducao"]["classes"]}
    atbs_validos = {a["id"] for a in intro["atributos"]["lista"]}

    for cls in classes:
        assert cls["id"] in ids_intro
        assert cls["atributo_principal"] in atbs_validos
        prog = cls["progressao"]
        assert len(prog) == 24
        assert [p["nivel"] for p in prog] == list(range(1, 25))
        ppes = [p["ppe"] for p in prog]
        assert ppes[0] == 0 and all(ppes[i] < ppes[i + 1] for i in range(len(ppes) - 1))
        bpas = [p["bpa"] for p in prog]
        assert all(bpas[i] <= bpas[i + 1] for i in range(len(bpas) - 1))

    por_id = {c["id"]: c for c in classes}
    assert len(por_id["druida"]["conjuracao"]["feiticos_diarios"]) == 24
    assert por_id["druida"]["conjuracao"]["feiticos_diarios"]["1"] == {"0": 3, "1": 1}
    assert len(por_id["ilusionista"]["conjuracao"]["feiticos_diarios"]) == 24
    assert por_id["ilusionista"]["conjuracao"]["feiticos_diarios"]["1"] == {"0": 4, "1": 2}
    assert por_id["ilusionista"]["progressao"][-1]["bpa"] == 6
    assert len(por_id["lutador"]["tabela_habilidades_especiais"]) == 24
    assert por_id["lutador"]["tabela_habilidades_especiais"][0]["ca_base"] == 11
    assert por_id["lutador"]["tabela_habilidades_especiais"][-1]["ca_base"] == 17
    assert por_id["explorador"]["tabelas_rastreamento"]["penalidade_nao_explorador"] == -10


def main() -> None:
    """Gera `dados/dadosc&c/classes02.json`, recarrega do disco e valida."""
    dados = construir_classes_02()
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_SAIDA.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    recarregado = json.loads(CAMINHO_SAIDA.read_text(encoding="utf-8"))
    validar_classes_02(recarregado)
    total_habs = sum(len(c["habilidades"]) for c in recarregado["classes"])
    print(f"OK — {CAMINHO_SAIDA.relative_to(RAIZ_PROJETO)} gerado e validado com sucesso!")
    print(
        f"Classes: {len(recarregado['classes'])} (Druida, Explorador, Ilusionista, Lutador) | "
        f"Níveis por classe: 24 | Habilidades detalhadas: {total_habs} | "
        f"Tabelas especiais: Feitiços Druida/Ilusionista, Rastreamento Explorador, Combate Lutador"
    )


if __name__ == "__main__":
    main()
