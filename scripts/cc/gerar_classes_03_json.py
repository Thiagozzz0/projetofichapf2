"""Gerador e validador de dados/dadosc&c/classes03.json (Leva 03: Mago, Paladino, Trapaceiro, Assassino + Multiclasse/Classe e Meia) a partir de ref/cc/C&C classes 03.pdf (pp. 63–85)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent
DIR_DADOS_CC = RAIZ_PROJETO / "dados" / "dadosc&c"
CAMINHO_SAIDA = DIR_DADOS_CC / "classes03.json"


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


def _mago() -> dict[str, Any]:
    ppes = [
        0, 2601, 5201, 10401, 20801, 42501, 85001, 170001, 340001, 500001, 750001, 1000001,
        1250001, 1500001, 1750001, 2000001, 2250001, 2500001, 2750001, 3000001, 3250001, 3500001, 3750001, 4000001,
    ]
    bpas = [0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Conjuração", "Conjura feitiços arcanos (feitiços bônus com Inteligência 13-15 [1º], 16-17 [2º], 18-19 [3º])."),
        ],
        13: [
            _hab_prog("Detectar Magia", "Após 5 rodadas de estudo, detecta magia e identifica sua origem.", "inteligencia"),
        ],
        15: [
            _hab_prog("Bônus de Inteligência", "Ganha +1 ponto permanente em Inteligência."),
        ],
        17: [
            _hab_prog("Contrafeitiço", "Identifica feitiço lançado contra si por outro mago/ilusionista e tenta neutralizá-lo.", "inteligencia"),
        ],
        18: [
            _hab_prog("Detectar Magia", "Determina o poder do item e sua importância histórica/cultural.", "inteligencia"),
        ],
        20: [
            _hab_prog("Recordação Perfeita", "Recorda 1x/dia feitiço de nível 0 lançado anteriormente (ND 0).", "inteligencia"),
        ],
        24: [
            _hab_prog("Recordação Perfeita", "Recorda 1x/dia feitiço de 1º nível lançado anteriormente (ND 1).", "inteligencia"),
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
        "21": {"0": 7, "1": 7, "2": 7, "3": 6, "4": 6, "5": 5, "6": 5, "7": 4, "8": 4, "9": 3},
        "22": {"0": 7, "1": 7, "2": 7, "3": 6, "4": 6, "5": 5, "6": 5, "7": 4, "8": 4, "9": 3},
        "23": {"0": 8, "1": 8, "2": 7, "3": 7, "4": 6, "5": 6, "6": 5, "7": 5, "8": 4, "9": 4},
        "24": {"0": 8, "1": 8, "2": 7, "3": 7, "4": 6, "5": 6, "6": 5, "7": 5, "8": 4, "9": 4},
    }
    return {
        "id": "mago",
        "nome": "Mago",
        "paginas_livro": "63–66",
        "atributo_principal": "inteligencia",
        "dado_vida": "d4",
        "pv_apos_nivel_10": 1,
        "disposicao": "qualquer",
        "armas": {"qualquer": False, "lista": ["Clava", "Adaga", "Lança de Mão", "Cajado"], "observacao": None},
        "armaduras": {
            "qualquer": False,
            "nenhuma": True,
            "lista": [],
            "observacao": "Qualquer uso de armadura ou escudo impede o mago de conjurar feitiços.",
        },
        "conjurador": True,
        "conjuracao": {
            "tradicao": "arcana",
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
        "descricao": "Estudiosos arquetípicos da magia arcana, capazes de moldar a realidade através do conhecimento de antigos tomos e grimórios.",
        "habilidades": [
            {
                "id": "feiticos_mago",
                "nome": "Feitiços e Grimório",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Prepara feitiços arcanos a partir de seu grimório conforme Tabela de Feitiços por Dia + Feitiços Bônus cumulativos por Inteligência.",
            },
            {
                "id": "detectar_magia_mago",
                "nome": "Detectar Magia",
                "nivel_aquisicao": 13,
                "atributo_teste": "inteligencia",
                "descricao": "Após 5 rodadas de concentração em um item, detecta se é mágico e, com teste INT, identifica sua origem (se já conhecida). No N18 determina poder e importância histórica.",
            },
            {
                "id": "bonus_de_inteligencia",
                "nome": "Bônus de Inteligência",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Inteligência em +1.",
            },
            {
                "id": "contrafeitico",
                "nome": "Contrafeitiço",
                "nivel_aquisicao": 17,
                "atributo_teste": "inteligencia",
                "descricao": "Teste de Inteligência (ND = nível do conjurador) para reconhecer feitiço lançado contra si por outro mago/ilusionista e conjurar contrafeitiço vencendo a iniciativa.",
            },
            {
                "id": "recordacao_perfeita",
                "nome": "Recordação Perfeita",
                "nivel_aquisicao": 20,
                "atributo_teste": "inteligencia",
                "descricao": "Teste de Inteligência para recordar 1x/dia um feitiço já conjurado de nível 0 (N20, ND 0) ou 1º nível (N24, ND 1).",
            },
        ],
        "progressao": progressao,
    }


def _paladino() -> dict[str, Any]:
    ppes = [
        0, 2701, 5501, 12001, 24001, 48001, 95001, 180001, 360001, 700001, 1000001, 1300001,
        1600001, 1900001, 2200001, 2500001, 2800001, 3100001, 3400001, 3700001, 4000001, 4300001, 4600001, 4900001,
    ]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Curar Doenças", "Cura qualquer doença 1x/semana."),
            _hab_prog("Detectar o Mal", "Detecta o mal a até 18 m concentrando-se por 1 rodada (à vontade)."),
            _hab_prog("Aura Divina", "Aura permanente: +2 CA e +2 JP contra o Mal; bloqueia contato de criaturas invocadas/conjuradas."),
            _hab_prog("Saúde Divina", "Imunidade a doenças de todas as origens."),
            _hab_prog("Imposição de Mãos", "1x/dia cura 2 PV por nível em um único alvo."),
        ],
        3: [
            _hab_prog("Afastar Mortos-Vivos", "Afasta mortos-vivos como um clérigo de nível (nível do paladino - 2).", "sabedoria"),
        ],
        4: [
            _hab_prog("Montaria Divina", "Chama um cavalo de guerra pesado divino (ou pônei de guerra se Pequeno)."),
        ],
        6: [
            _hab_prog("Aura de Coragem", "Imunidade ao medo; aliados a até 3 m recebem +4 em JP contra medo."),
            _hab_prog("Curar Doenças", "Cura doenças 2x/semana."),
        ],
        9: [
            _hab_prog("Destruir o Mal", "1x/dia em 1 ataque contra criatura maligna: +mod. CAR no ataque e +1 dano/nível."),
        ],
        12: [
            _hab_prog("Curar Doenças", "Cura doenças 3x/semana."),
            _hab_prog("Cura Divina", "1x/semana cura todo dano, doenças, cegueira, surdez, venenos e distúrbios mentais."),
        ],
        13: [
            _hab_prog("Legado Virtuoso", "Encanta item (1/dia, custo temporário de -1 CON): dobra cura em repouso e recupera alvos até -5 PV para 0 PV em 24 h."),
            _hab_prog("Intervenção Divina", "1x/semana: refazer rolagem, +4 ataque e dano dobrado por 1 rodada, ou reduzir dano sofrido pela metade."),
        ],
        15: [
            _hab_prog("Destruir o Mal Avançado", "Pode usar Destruir o Mal 2x/dia."),
            _hab_prog("Aura de Coragem Avançada", "Alcance da Aura de Coragem aumenta para 9 m."),
            _hab_prog("Bônus de Carisma", "Ganha +1 ponto permanente em Carisma."),
        ],
        17: [
            _hab_prog("Intervenção Divina", "Pode usar Intervenção Divina 2x/semana."),
        ],
        18: [
            _hab_prog("Legado Virtuoso", "Estende recuperação de negativos até -7 PV."),
        ],
        20: [
            _hab_prog("Legado Virtuoso", "Estende recuperação de negativos até -9 PV."),
            _hab_prog("Destruir o Mal Avançado", "Pode usar Destruir o Mal 3x/dia."),
            _hab_prog("Vontade Divina", "1x/mês impele ouvintes (JP CAR) a aderir a causa sagrada como Obrigação."),
            _hab_prog("Aura de Coragem Avançada", "Alcance da Aura de Coragem aumenta para 15 m."),
        ],
        22: [
            _hab_prog("Intervenção Divina", "Pode usar Intervenção Divina 3x/semana."),
        ],
        24: [
            _hab_prog("Limpar Alma", "Revela enganos, ilusões e disposição, lê mentes, dissipa magia e pode exorcizar o mal."),
        ],
    }
    progressao = [
        _linha_prog(n, "d10" if n <= 10 else "+4 PV", n - 1, ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    return {
        "id": "paladino",
        "nome": "Paladino",
        "paginas_livro": "67–71",
        "atributo_principal": "carisma",
        "dado_vida": "d10",
        "pv_apos_nivel_10": 4,
        "disposicao": "Lei/Bem ou Bem/Lei",
        "armas": {"qualquer": True, "lista": ["Qualquer"], "observacao": "Evita armas associadas a ladrões/covardia e geralmente evita armas de longo alcance."},
        "armaduras": {"qualquer": True, "nenhuma": False, "lista": ["Qualquer"], "observacao": "Violar o código ou cometer ato maligno voluntário faz perder todas as habilidades até expiação."},
        "conjurador": False,
        "descricao": "Guerreiros sagrados devotados à lei, à virtude e à erradicação do mal, abençoados com aura protetora e poderes divinos.",
        "habilidades": [
            {
                "id": "curar_doencas",
                "nome": "Curar Doenças",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Cura qualquer doença: 1x/semana (N1), 2x/semana (N6), 3x/semana (N12).",
            },
            {
                "id": "detectar_o_mal",
                "nome": "Detectar o Mal",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Habilidade inata (à vontade, concentrando 1 rodada) com alcance de 18 m, como o feitiço.",
            },
            {
                "id": "aura_divina",
                "nome": "Aura Divina",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Permanente: +2 CA e +2 JP contra criaturas malignas; impede contato corporal de criaturas invocadas/conjuradas (exceto elementais/extradimensionais bons).",
            },
            {
                "id": "saude_divina",
                "nome": "Saúde Divina",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Imunidade total a doenças de qualquer origem.",
            },
            {
                "id": "imposicao_de_maos",
                "nome": "Imposição de Mãos",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "1x/dia cura 2 PV por nível do paladino em si mesmo ou em outro alvo único.",
            },
            {
                "id": "afastar_mortos_vivos_paladino",
                "nome": "Afastar Mortos-Vivos",
                "nivel_aquisicao": 3,
                "atributo_teste": "sabedoria",
                "descricao": "Afasta mortos-vivos como um clérigo de nível igual ao (nível do paladino - 2).",
            },
            {
                "id": "montaria_divina",
                "nome": "Montaria Divina",
                "nivel_aquisicao": 4,
                "atributo_teste": None,
                "descricao": "Convoca cavalo de guerra pesado (Médio) ou pônei de guerra (Pequeno). Se morrer, aguarda 1 ano e 1 dia para chamar outra.",
            },
            {
                "id": "aura_de_coragem",
                "nome": "Aura de Coragem",
                "nivel_aquisicao": 6,
                "atributo_teste": None,
                "descricao": "Imune ao medo; aliados recebem +4 em JP contra medo num raio de 3 m (N6), 9 m (N15) e 15 m (N20).",
            },
            {
                "id": "destruir_o_mal",
                "nome": "Destruir o Mal",
                "nivel_aquisicao": 9,
                "atributo_teste": None,
                "descricao": "Em 1 ataque contra criatura maligna: +mod. CAR para acertar e +1 dano por nível. Usos: 1x/dia (N9), 2x/dia (N15), 3x/dia (N20).",
            },
            {
                "id": "cura_divina",
                "nome": "Cura Divina",
                "nivel_aquisicao": 12,
                "atributo_teste": None,
                "descricao": "1x/semana cura simultaneamente todo dano de PV, doenças, cegueira, surdez, venenos, dano temporário de atributo, Ruína da Razão e distúrbios mentais.",
            },
            {
                "id": "legado_virtuoso",
                "nome": "Legado Virtuoso",
                "nivel_aquisicao": 13,
                "atributo_teste": None,
                "descricao": "1 item/dia (máx. nível itens ativos; perde 1 CON por 1 dia, ou permanente para virtude permanente). Dobra cura em repouso até 1/2 PV do paladino, estanca sangramento e traz alvos negativos a 0 PV em 24 h: até -5 PV (N13), -7 PV (N18), -9 PV (N20).",
            },
            {
                "id": "intervencao_divina",
                "nome": "Intervenção Divina",
                "nivel_aquisicao": 13,
                "atributo_teste": None,
                "descricao": "1x/semana (N13), 2x/semana (N17), 3x/semana (N22): (1) refazer 1 rolagem; (2) +4 ataque e dano dobrado por 1 rodada; ou (3) reduzir pela metade todo dano sofrido na rodada.",
            },
            {
                "id": "bonus_de_carisma",
                "nome": "Bônus de Carisma",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Carisma em +1.",
            },
            {
                "id": "vontade_divina",
                "nome": "Vontade Divina",
                "nivel_aquisicao": 20,
                "atributo_teste": None,
                "descricao": "1x/mês compele ouvintes não malignos/não PJs (JP CAR, ND = nível) como Obrigação por dias iguais ao nível do paladino.",
            },
            {
                "id": "limpar_alma",
                "nome": "Limpar Alma",
                "nivel_aquisicao": 24,
                "atributo_teste": "carisma",
                "descricao": "Restringindo o alvo por rodadas iguais ao nível dele + teste CAR (ND = nível) + superar RM: revela disposição, ilusões e pensamentos; pode exorcizar o mal (JP CAR ou destruição/cura). Exige descanso imediato de 1 h por nível do alvo.",
            },
        ],
        "progressao": progressao,
    }


def _trapaceiro() -> dict[str, Any]:
    ppes = [
        0, 1251, 2501, 6001, 12001, 24001, 48001, 80001, 120001, 175001, 325001, 450001,
        575001, 700001, 825001, 950001, 1075001, 1200001, 1325001, 1450001, 1575001, 1700001, 1825001, 1950001,
    ]
    bpas = [0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Especial (Armaduras)", "Usa couro, casaco de couro, gibão de peles/acolchoada, escudo pequeno e elmo de couro sem penalidade (-1 por ponto de CA acima de 12)."),
            _hab_prog("Ataque pelas Costas", "+4 para acertar e dano ×2 após Mover-se em Silêncio ou Esconder-se."),
            _hab_prog("A Gíria", "Linguagem codificada de rua com palavras e gestos."),
            _hab_prog("Escalar", "Escala superfícies difíceis a metade da velocidade.", "destreza"),
            _hab_prog("Decifrar Escrita", "Decifra escritos/códigos (2d8 min/pág; arcanos com -10).", "inteligencia"),
            _hab_prog("Esconder-se", "Oculta-se atrás de cobertura ou sombras.", "destreza"),
            _hab_prog("Ouvir", "Ouve ruídos suaves a até 9 m ou através de portas.", "sabedoria"),
            _hab_prog("Mover-se em Silêncio (Passos Leves)", "Desloca-se silenciosamente em ambientes fechados e abertos.", "destreza"),
            _hab_prog("Abrir Fechaduras", "Destranca fechaduras mecânicas com ferramentas de ladrão.", "destreza"),
            _hab_prog("Surrupiar (Furtar Bolsos)", "Furta bolsos/bolsas e executa prestidigitação.", "destreza"),
            _hab_prog("Encontrar/Desarmar Armadilhas", "Encontra, desarma ou arma armadilhas (inclusive mágicas).", "inteligencia"),
        ],
        3: [
            _hab_prog("Esconder-se", "Pode usar Mover-se em Silêncio enquanto escondido com penalidade de -5 (1/4 deslocamento).", "destreza"),
        ],
        4: [
            _hab_prog("Ataque Furtivo", "+2 para acertar e +4 de dano contra alvo desprevenido (distância até 9 m)."),
        ],
        5: [
            _hab_prog("Ataque pelas Costas", "+4 para acertar e dano ×3."),
        ],
        9: [
            _hab_prog("Ataque pelas Costas", "+4 para acertar e dano ×4."),
        ],
        13: [
            _hab_prog("Ataque Furtivo", "Bônus aumenta para +3 ataque e +6 dano."),
        ],
        14: [
            _hab_prog("Ataque pelas Costas", "Bônus aumenta para +6 ataque e dano ×5."),
            _hab_prog("Sexto Sentido", "+1 em testes de Sabedoria contra surpresa."),
        ],
        15: [
            _hab_prog("Detectar Portas Secretas e Ocultas", "Percebe portas ocultas a 3 m ou secretas a 1,5 m (+2 procurando).", "sabedoria"),
            _hab_prog("Bônus de Destreza", "Ganha +1 ponto permanente em Destreza."),
        ],
        17: [
            _hab_prog("Esconder-se e Mover-se em Silêncio", "Sem penalidade até metade do deslocamento; -4 acima da metade.", "destreza"),
        ],
        18: [
            _hab_prog("Ataque Furtivo", "Bônus aumenta para +4 ataque e +7 dano."),
            _hab_prog("Sexto Sentido", "+2 em testes de Sabedoria contra surpresa."),
            _hab_prog("Reação Rápida", "+1 em jogadas de iniciativa."),
        ],
        19: [
            _hab_prog("Esconder-se e Mover-se em Silêncio", "Penalidade acima da metade reduzida para -3.", "destreza"),
        ],
        20: [
            _hab_prog("Ataque pelas Costas", "Bônus aumenta para +7 ataque e dano ×6."),
            _hab_prog("Manobra Evasiva", "+4 na CA durante combate corpo a corpo (não pode estar surpreso)."),
        ],
        21: [
            _hab_prog("Esconder-se e Mover-se em Silêncio", "Penalidade acima da metade reduzida para -2.", "destreza"),
        ],
        22: [
            _hab_prog("Esconder-se e Mover-se em Silêncio", "Penalidade acima da metade reduzida para -1.", "destreza"),
            _hab_prog("Sexto Sentido", "+3 em testes de Sabedoria contra surpresa."),
        ],
        23: [
            _hab_prog("Ataque Furtivo", "Bônus aumenta para +5 ataque e +9 dano."),
        ],
        24: [
            _hab_prog("Esconder-se e Mover-se em Silêncio", "Esconde-se e move-se em silêncio sem nenhuma penalidade.", "destreza"),
            _hab_prog("Reação Rápida", "+2 iniciativa; resultado 11+ concede ação adicional no final da rodada."),
        ],
    }
    progressao = [
        _linha_prog(n, "d6" if n <= 10 else "+2 PV", bpas[n - 1], ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    return {
        "id": "trapaceiro",
        "nome": "Trapaceiro",
        "paginas_livro": "72–77",
        "atributo_principal": "destreza",
        "dado_vida": "d6",
        "pv_apos_nivel_10": 2,
        "disposicao": "qualquer",
        "armas": {
            "qualquer": False,
            "lista": [
                "Zarabatana", "Espada Larga", "Gato de Nove Caudas", "Cestus", "Clava", "Adaga",
                "Lança de Mão", "Martelo", "Machadinha", "Besta de Mão", "Azagaia", "Faca",
                "Besta Leve", "Espada Longa", "Maça", "Main Gauche", "Bastão", "Paieira",
                "Porrete", "Arco Curto", "Espada Curta", "Foice Curta", "Manopla com Cravos",
                "Funda", "Chicote", "Sodegarami",
            ],
            "observacao": None,
        },
        "armaduras": {
            "qualquer": False,
            "nenhuma": False,
            "lista": ["Couro", "Jaqueta de Couro", "Gibão de Peles", "Acolchoada"],
            "observacao": "Escudo pequeno e elmo de couro sem penalidade. Outras armaduras: -1 por ponto de CA acima de 12; elmos/escudos restritos: -1 cumulativo.",
        },
        "conjurador": False,
        "descricao": "Ladrões, infiltradores e oportunistas ágeis, especialistas em furtividade, armadilhas, fechaduras e golpes pelas costas.",
        "habilidades": [
            {
                "id": "especial_armaduras_trapaceiro",
                "nome": "Especial (Penalidade de Armadura)",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Usa couro, casaco de couro, acolchoada, escudo pequeno e elmo de couro sem penalidade. Outras armaduras impõem -1 por ponto de CA acima de 12 nas habilidades afetadas (+ -1 por escudo/elmo restrito).",
            },
            {
                "id": "ataque_pelas_costas",
                "nome": "Ataque pelas Costas",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Com arma corpo a corpo menor que o braço, após Mover-se em Silêncio ou Esconder-se atrás de alvo com costas discerníveis (não acumula com Ataque Furtivo): +4/×2 (N1), +4/×3 (N5), +4/×4 (N9), +6/×5 (N14), +7/×6 (N20).",
            },
            {
                "id": "a_giria",
                "nome": "A Gíria",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Linguagem codificada de rua composta por palavras-código e gestos.",
            },
            {
                "id": "escalar",
                "nome": "Escalar",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Escala paredes, tetos e superfícies difíceis a 1/2 velocidade (mãos livres; falha por 5+ cai). Encostas naturais/degraus sem teste.",
            },
            {
                "id": "decifrar_escrita_trapaceiro",
                "nome": "Decifrar Escrita",
                "nivel_aquisicao": 1,
                "atributo_teste": "inteligencia",
                "descricao": "2d8 min/página, 1 tentativa por escrito. Pode ler escritas arcanas com -10 (sem conjurar); não funciona com pergaminhos divinos.",
            },
            {
                "id": "esconder_se",
                "nome": "Esconder-se",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Oculta-se com cobertura/sombras (até 1/2 vel. sem penalidade, normal -5, correndo/atacando -20, observador distraído -10). N3: combina com Mover-se em Silêncio (-5, 1/4 vel.). N17–24: penalidade acima de 1/2 vel. reduz de -4 até 0.",
            },
            {
                "id": "ouvir",
                "nome": "Ouvir",
                "nivel_aquisicao": 1,
                "atributo_teste": "sabedoria",
                "descricao": "Detecta sons suaves a até 9 m ou adjacente a portas (parede de pedra -10; 1x/rodada; afetado por elmo grande/metal).",
            },
            {
                "id": "mover_se_em_silencio_trapaceiro",
                "nome": "Mover-se em Silêncio (Passos Leves)",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Ambientes fechados e abertos: até 1/2 vel. sem penalidade, até máxima -5, correndo/atacando -20.",
            },
            {
                "id": "abrir_fechadura",
                "nome": "Abrir Fechadura",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Abre fechaduras mecânicas com ferramentas de ladrão (1 tentativa por fechadura por nível; afetado por luvas pesadas/metal).",
            },
            {
                "id": "surrupiar",
                "nome": "Surrupiar (Furtar Bolsos)",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Furta bolsos/bolsas (penalidade = nível da vítima) e faz prestidigitação (penalidade = mod. SAB de observador atento).",
            },
            {
                "id": "armadilhas_trapaceiro",
                "nome": "Armadilhas",
                "nivel_aquisicao": 1,
                "atributo_teste": "inteligencia",
                "descricao": "Encontra (1 rodada ponto específico / 1 min área 3×3 m), desarma (1d4 rodadas, falha aciona) ou arma/rearma (+5) armadilhas mundanas e mágicas.",
            },
            {
                "id": "ataque_furtivo_trapaceiro",
                "nome": "Ataque Furtivo",
                "nivel_aquisicao": 4,
                "atributo_teste": None,
                "descricao": "Contra alvo que não suspeita de ataque (distância até 9 m; alvo só rola iniciativa na rodada seguinte; não acumula com Ataque pelas Costas): +2/+4 (N4), +3/+6 (N13), +4/+7 (N18), +5/+9 (N23).",
            },
            {
                "id": "sexto_sentido",
                "nome": "Sexto Sentido",
                "nivel_aquisicao": 14,
                "atributo_teste": None,
                "descricao": "Bônus em testes de Sabedoria contra surpresa: +1 (N14), +2 (N18), +3 (N22).",
            },
            {
                "id": "detectar_portas_ocultas_e_secretas",
                "nome": "Detectar Portas Ocultas e Secretas",
                "nivel_aquisicao": 15,
                "atributo_teste": "sabedoria",
                "descricao": "Teste ao passar a 3 m de porta oculta ou 1,5 m de porta secreta (+2 procurando ativamente).",
            },
            {
                "id": "bonus_de_destreza",
                "nome": "Bônus de Destreza",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Destreza em +1.",
            },
            {
                "id": "reacao_rapida_trapaceiro",
                "nome": "Reação Rápida",
                "nivel_aquisicao": 18,
                "atributo_teste": None,
                "descricao": "+1 iniciativa (N18), +2 iniciativa (N24; resultado 11+ concede ação extra no final da rodada).",
            },
            {
                "id": "manobra_evasiva",
                "nome": "Manobra Evasiva",
                "nivel_aquisicao": 20,
                "atributo_teste": None,
                "descricao": "+4 na CA em combate corpo a corpo sem prejudicar ataques (não funciona com armas à distância, usando habilidades de trapaceiro ou surpreso).",
            },
        ],
        "progressao": progressao,
    }


def _assassino() -> dict[str, Any]:
    ppes = [
        0, 1751, 3501, 7001, 14001, 25001, 50001, 90001, 150001, 200001, 350001, 500001,
        650001, 800001, 950001, 1100001, 1250001, 1400001, 1550001, 1700001, 1850001, 2000001, 2150001, 2300001,
    ]
    bpas = [0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8]
    eventos: dict[int, list[dict[str, Any]]] = {
        1: [
            _hab_prog("Armaduras (Especial)", "Usa couro, jaqueta de couro, gibão de peles/acolchoada, escudo pequeno e elmo de couro sem penalidade."),
            _hab_prog("Avaliar Alvo", "Observa por 1d3×10 min para descobrir nível (±10%), disposição, armas ocultas e hábitos.", "sabedoria"),
            _hab_prog("Escalar", "Escala superfícies difíceis a metade da velocidade.", "destreza"),
            _hab_prog("Ataque Mortal", "Após estudar alvo por 3 rodadas, ataque furtivo pode matar instantaneamente (JP CON)."),
            _hab_prog("Disfarce", "Personifica tipos gerais (1d3×10 min) ou indivíduos específicos (1 mês).", "carisma"),
            _hab_prog("Esconder-se", "Oculta-se com cobertura ou sombras (no N3 combina com Mover-se em Silêncio com -5).", "destreza"),
            _hab_prog("Ouvir", "Ouve sons suaves a até 9 m ou através de portas.", "sabedoria"),
            _hab_prog("Mover-se em Silêncio", "Move-se silenciosamente em ambientes abertos ou fechados.", "destreza"),
            _hab_prog("Venenos", "Identifica e fabrica venenos/antídotos (1/3 do preço) sem risco de autoenvenenamento; +1 JP venenos no N3.", "inteligencia"),
            _hab_prog("Ataque Furtivo", "+2 para acertar e +4 de dano contra alvo desavisado (distância até 9 m)."),
            _hab_prog("Armadilhas", "Encontra, desarma ou arma armadilhas mundanas e mágicas.", "inteligencia"),
        ],
        13: [
            _hab_prog("Surpresa", "Oponentes sofrem -1 em testes de Sabedoria contra surpresa."),
            _hab_prog("Ataque Furtivo", "Bônus aumenta para +3 ataque e +6 dano."),
        ],
        15: [
            _hab_prog("Bônus de Destreza", "Ganha +1 ponto permanente em Destreza."),
            _hab_prog("Marca do Carrasco", "Estilo de assinatura aumenta o ND do Ataque Mortal em +2."),
        ],
        18: [
            _hab_prog("Surpresa", "Oponentes sofrem -2 em testes de Sabedoria contra surpresa."),
            _hab_prog("Reação Rápida", "+1 em jogadas de iniciativa."),
        ],
        19: [
            _hab_prog("Ataque Furtivo", "Bônus aumenta para +4 ataque e +7 dano."),
        ],
        20: [
            _hab_prog("Morte Lenta", "Causa hemorragia de 1d6/rodada (cumulativo até 4 golpes) ao atacar antes do alvo."),
        ],
        23: [
            _hab_prog("Surpresa", "Oponentes sofrem -3 em testes de Sabedoria contra surpresa."),
            _hab_prog("Ataque Furtivo", "Bônus aumenta para +5 ataque e +9 dano."),
        ],
        24: [
            _hab_prog("Reação Rápida", "+2 iniciativa; resultado 11+ concede ação adicional."),
            _hab_prog("Morte Lenta", "Ferimentos curam metade do normal (mesmo magicamente) e podem incapacitar membro (JP CON)."),
        ],
    }
    progressao = [
        _linha_prog(n, "d6" if n <= 10 else "+2 PV", bpas[n - 1], ppes[n - 1], eventos.get(n))
        for n in range(1, 25)
    ]
    tabela_venenos = [
        {
            "tipo": "I",
            "categoria": "Venenos leves (irritação, sonolência, náuseas)",
            "custo_po": 5,
            "nd": 2,
            "sucesso_jp": "Sem efeito",
            "duracao_sucesso": "Não se aplica",
            "falha_jp": "-1 atributos físicos e -1 iniciativa",
            "duracao_falha": "1–3 dias",
        },
        {
            "tipo": "II",
            "categoria": "Poções que alteram a mente (alucinações, confusão, perda de memória)",
            "custo_po": 15,
            "nd": 2,
            "sucesso_jp": "Sem efeito",
            "duracao_sucesso": "Não se aplica",
            "falha_jp": "-1 atributos mentais e -1 iniciativa",
            "duracao_falha": "1–3 dias",
        },
        {
            "tipo": "III",
            "categoria": "Venenos que prejudicam habilidades e causam danos pequenos",
            "custo_po": 45,
            "nd": 4,
            "sucesso_jp": "1d4 de dano, -1 em todos os atributos secundários",
            "duracao_sucesso": "1–2 dias",
            "falha_jp": "1d8 de dano, -2 em todos os atributos primários",
            "duracao_falha": "2–6 dias",
        },
        {
            "tipo": "IV",
            "categoria": "Toxinas que incapacitam, aleijam ou causam danos maiores",
            "custo_po": 150,
            "nd": 8,
            "sucesso_jp": "1d8 de dano, -1 em todos os testes de atributo",
            "duracao_sucesso": "2–4 dias",
            "falha_jp": "2d8 de dano, estado comatoso",
            "duracao_falha": "3–9 dias",
        },
        {
            "tipo": "V",
            "categoria": "Venenos mortais que causam danos permanentes ou matam",
            "custo_po": 900,
            "nd": 12,
            "sucesso_jp": "1d10 de dano, perda permanente de 1 ponto do atributo secundário da classe",
            "duracao_sucesso": "1–6 dias",
            "falha_jp": "Morte (2ª JP CON) ou 2d12 de dano e perda permanente de 2 pontos do atributo primário da classe",
            "duracao_falha": "2 semanas",
        },
        {
            "tipo": "VI",
            "categoria": "Substâncias raras que causam danos permanentes massivos ou matam",
            "custo_po": 1800,
            "nd": 16,
            "sucesso_jp": "4d10 de dano, perda permanente de 1 ponto em todos os primários e 2 em todos os secundários",
            "duracao_sucesso": "Instantâneo",
            "falha_jp": "Morte",
            "duracao_falha": "Permanente",
        },
    ]
    return {
        "id": "assassino",
        "nome": "Assassino",
        "classe_expandida": True,
        "paginas_livro": "78–82",
        "atributo_principal": "destreza",
        "dado_vida": "d6",
        "pv_apos_nivel_10": 2,
        "disposicao": "qualquer uma não boa",
        "armas": {"qualquer": True, "lista": ["Qualquer"], "observacao": None},
        "armaduras": {
            "qualquer": False,
            "nenhuma": False,
            "lista": ["Couro", "Jaqueta de Couro", "Acolchoada", "Gibão de Peles"],
            "observacao": "Escudo pequeno e elmo de couro sem penalidade. Outras armaduras: -1 por ponto de CA acima de 12 (+ -1 escudo/elmo restrito).",
        },
        "conjurador": False,
        "tabela_venenos": tabela_venenos,
        "descricao": "Matadores especializados que caminham nas sombras usando furtividade, disfarce, venenos e ataques mortais precisos.",
        "habilidades": [
            {
                "id": "especial_armaduras_assassino",
                "nome": "Especial (Penalidade de Armadura)",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Usa couro, casaco de couro, acolchoada, escudo pequeno e elmo de couro sem penalidade. Outras armaduras: -1 por ponto acima de CA 12 (+ -1 escudo/elmo restrito).",
            },
            {
                "id": "avaliar_alvo",
                "nome": "Avaliar Alvo",
                "nivel_aquisicao": 1,
                "atributo_teste": "sabedoria",
                "descricao": "Observa alvo por 1d3×10 min para descobrir nível aproximado (±10%), disposição, armas ocultas, hábitos e maneirismos (afetado por elmos).",
            },
            {
                "id": "escalar_assassino",
                "nome": "Escalar",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Escala superfícies difíceis a 1/2 velocidade (mãos livres; falha por 5+ cai). Encostas naturais/degraus sem teste.",
            },
            {
                "id": "ataque_mortal",
                "nome": "Ataque Mortal",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Estuda vítima desavisada por 3 rodadas e ataca nas próximas 3 rodadas com Ataque Furtivo. Se causar dano, alvo faz JP CON ou morre instantaneamente (se passar, sofre dano normal de Ataque Furtivo).",
            },
            {
                "id": "disfarces_assassino",
                "nome": "Disfarces",
                "nivel_aquisicao": 1,
                "atributo_teste": "carisma",
                "descricao": "Geral: 1d3×10 min; indivíduo específico: 1 mês (altura/peso ±10%; teste secreto pelo GC; sexo -2, raça -2, idade -2/10 anos). Observador que conhece o alvo ganha +4/+8/+12 em INT.",
            },
            {
                "id": "esconder_se_assassino",
                "nome": "Esconder-se",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Oculta-se com cobertura/sombras. A partir do N3 combina com Mover-se em Silêncio com -5 (1/4 velocidade).",
            },
            {
                "id": "ouvir_assassino",
                "nome": "Ouvir",
                "nivel_aquisicao": 1,
                "atributo_teste": "sabedoria",
                "descricao": "Detecta sons suaves a 9 m ou adjacente a portas (parede de pedra -10; afetado por elmo grande/metal).",
            },
            {
                "id": "mover_se_em_silencio_assassino",
                "nome": "Mover-se em Silêncio",
                "nivel_aquisicao": 1,
                "atributo_teste": "destreza",
                "descricao": "Ambientes internos e externos: até 1/2 vel. sem penalidade, até máxima -5, correndo/atacando -20.",
            },
            {
                "id": "venenos",
                "nome": "Venenos",
                "nivel_aquisicao": 1,
                "atributo_teste": "inteligencia",
                "descricao": "Identifica e fabrica venenos/antídotos (matéria-prima custa 1/3 do preço de rua), sem risco ao aplicar em lâmina. Ganha +1 em JP contra venenos no N3.",
            },
            {
                "id": "ataque_furtivo_assassino",
                "nome": "Ataque Furtivo",
                "nivel_aquisicao": 1,
                "atributo_teste": None,
                "descricao": "Contra alvo desavisado (distância até 9 m; alvo só rola iniciativa na rodada seguinte): +2/+4 (N1), +3/+6 (N13), +4/+7 (N19), +5/+9 (N23).",
            },
            {
                "id": "armadilhas_assassino",
                "nome": "Armadilhas",
                "nivel_aquisicao": 1,
                "atributo_teste": "inteligencia",
                "descricao": "Encontra, desarma (1d4 rodadas, falha aciona) e arma/rearma (+5) armadilhas mundanas e mágicas.",
            },
            {
                "id": "surpresa",
                "nome": "Surpresa",
                "nivel_aquisicao": 13,
                "atributo_teste": None,
                "descricao": "Impõe penalidade no teste de Sabedoria de surpresa dos oponentes: -1 (N13), -2 (N18), -3 (N23).",
            },
            {
                "id": "marca_do_carrasco",
                "nome": "Marca do Carrasco",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Escolhe estilo de assinatura (arma, veneno ou tática); aumenta o ND da JP CON do Ataque Mortal em +2.",
            },
            {
                "id": "bonus_de_destreza",
                "nome": "Bônus de Destreza",
                "nivel_aquisicao": 15,
                "atributo_teste": None,
                "descricao": "Aumenta permanentemente a pontuação de Destreza em +1.",
            },
            {
                "id": "reacao_rapida_assassino",
                "nome": "Reação Rápida",
                "nivel_aquisicao": 18,
                "atributo_teste": None,
                "descricao": "+1 iniciativa (N18), +2 iniciativa (N24; resultado 11+ concede ação extra no final da rodada).",
            },
            {
                "id": "morte_lenta",
                "nome": "Morte Lenta",
                "nivel_aquisicao": 20,
                "atributo_teste": None,
                "descricao": "Atacando antes do alvo (acumula com Ataque Furtivo, até 4x por alvo; não afeta criaturas que não sangram): causa hemorragia de 1d6/rodada. No N24 reduz cura pela metade e pode incapacitar 1 membro (JP CON).",
            },
        ],
        "progressao": progressao,
    }


def _regras_multiclasse_e_classe_e_meia() -> dict[str, Any]:
    return {
        "paginas_livro": "83–85",
        "multiclasse": {
            "limites_classes": {"humano": 3, "nao_humano": 2},
            "decisao": "Deve ser escolhida na criação do personagem (sujeita à aprovação do Guardião do Castelo).",
            "atributos_principais": "Deve possuir como primários os atributos principais de todas as classes combinadas.",
            "disposicao": "Classes não podem ter disposições conflitantes (salvo liberação do GC).",
            "armas": "Usa qualquer arma permitida por qualquer uma das classes combinadas sem penalidade.",
            "armadura": "Pode usar armaduras de qualquer uma das classes, mantendo penalidades de habilidades específicas. Magos/Ilusionistas de armadura podem conjurar, mas alvos ganham bônus na JP igual ao bônus de CA base da armadura.",
            "ouro_inicial": "Rola para cada classe, soma e divide por 2 ou 3 (conforme número de classes).",
            "bpa": "Usa o BpA mais favorável entre as classes escolhidas.",
            "tabela_dado_vida": {
                "d4/1":  {"d4/1": "d4/1", "d6/2": "d6/2", "d8/3": "d6/2", "d10/4": "d6/2", "d12/5": "d8/3"},
                "d6/2":  {"d4/1": "d6/2", "d6/2": "d6/2", "d8/3": "d6/2", "d10/4": "d8/3", "d12/5": "d8/3"},
                "d8/3":  {"d4/1": "d6/2", "d6/2": "d6/2", "d8/3": "d8/3", "d10/4": "d8/3", "d12/5": "d10/4"},
                "d10/4": {"d4/1": "d6/2", "d6/2": "d8/3", "d8/3": "d8/3", "d10/4": "d10/4", "d12/5": "d10/4"},
                "d12/5": {"d4/1": "d8/3", "d6/2": "d8/3", "d8/3": "d10/4", "d10/4": "d10/4", "d12/5": "d12/5"},
            },
            "xp_adicional_por_nivel": [
                {"nivel": "2", "duas_classes": 200, "tres_classes": 300},
                {"nivel": "3", "duas_classes": 400, "tres_classes": 600},
                {"nivel": "4", "duas_classes": 600, "tres_classes": 900},
                {"nivel": "5", "duas_classes": 800, "tres_classes": 1200},
                {"nivel": "6", "duas_classes": 1000, "tres_classes": 1500},
                {"nivel": "7", "duas_classes": 1200, "tres_classes": 1800},
                {"nivel": "8", "duas_classes": 1400, "tres_classes": 2100},
                {"nivel": "9", "duas_classes": 1600, "tres_classes": 2400},
                {"nivel": "10", "duas_classes": 1800, "tres_classes": 2700},
                {"nivel": "11", "duas_classes": 2000, "tres_classes": 3000},
                {"nivel": "12", "duas_classes": 2200, "tres_classes": 3300},
                {"nivel": "13+", "duas_classes": 2400, "tres_classes": 3600},
            ],
        },
        "classe_e_meia": {
            "conceito": "Combina uma Classe Principal com uma Classe de Apoio (que evolui à metade da taxa da principal), tratada como uma única classe aprimorada.",
            "xp_regra": "XP da classe principal + metade do XP da classe de apoio.",
            "atributo_primario": "Exige apenas o atributo primário da classe principal.",
            "bpa_e_armas": "Usa o melhor BpA e a melhor lista de proficiências em armas.",
            "escudo": "Só pode usar escudo se permitido pela classe principal.",
            "habilidades_apoio_nivel_0": "Conjuradores conjuram 2 feitiços de nível 0; habilidades com teste de atributo usam bônus de nível +0; habilidades sem teste só são obtidas no nível 1 de apoio.",
            "tabela_progressao_niveis": [
                {"nivel": n, "classe_principal": n, "classe_apoio": n // 2}
                for n in range(1, 11)
            ],
            "tabela_dado_vida_principal_apoio": {
                "d4/1":  {"d4/1": "d4/1", "d6/2": "d4/1", "d8/3": "d6/2", "d10/4": "d6/2", "d12/5": "d8/3"},
                "d6/2":  {"d4/1": "d6/2", "d6/2": "d6/2", "d8/3": "d6/2", "d10/4": "d8/3", "d12/5": "d8/3"},
                "d8/3":  {"d4/1": "d6/2", "d6/2": "d8/3", "d8/3": "d8/3", "d10/4": "d8/3", "d12/5": "d10/4"},
                "d10/4": {"d4/1": "d8/3", "d6/2": "d8/3", "d8/3": "d10/4", "d10/4": "d10/4", "d12/5": "d10/4"},
                "d12/5": {"d4/1": "d8/3", "d6/2": "d10/4", "d8/3": "d10/4", "d10/4": "d12/5", "d12/5": "d12/5"},
            },
            "habilidades_como_apoio": {
                "todas": ["trapaceiro", "assassino", "clerigo", "mago", "ilusionista"],
                "combatente": "Ganha Especialização em Armas (em arma permitida pela classe principal); não ganha Domínio de Combate nem Ataque Extra.",
                "explorador": "Ganha todas as habilidades, exceto Combate Devastador e Inimigo Predileto.",
                "barbaro": "Ganha apenas Senso de Combate, Caçador de Cervos e Instinto Primitivo.",
                "lutador": "Ganha apenas Combate Corpo a Corpo (incluindo ataques secundários), Ataque Atordoante e Punhos de Ferro.",
                "druida": "Ganha todas, exceto Forma do Totem (salvo com Explorador ou Bárbaro) e não aprende Druídico.",
                "cavaleiro": "Ganha apenas Equitação (sem vínculo a virtudes/código).",
                "paladino": "Só pode ser escolhido como classe principal.",
                "bardo": "Não ganha Fascinar nem Inspirar Grandeza.",
            },
            "restricoes_combinacao": [
                "Combatente, Explorador, Clérigo, Bardo e Lutador podem se alinhar com qualquer outra classe.",
                "Trapaceiro e Assassino não podem apoiar Cavaleiro ou Paladino.",
                "Bárbaro não pode apoiar Cavaleiro nem se alinhar com Mago ou Ilusionista.",
                "Mago, Ilusionista ou Druida só podem apoiar Cavaleiro ou Paladino se o personagem for Elfo ou Meio-Elfo de linhagem élfica.",
            ],
        },
    }


def construir_classes_03() -> dict[str, Any]:
    """Monta o dicionário completo de `dados/dadosc&c/classes03.json` (Leva 03)."""
    return {
        "metadados": {
            "sistema": "Castles & Crusades",
            "edicao": "1ª Edição Brasileira (Livro do Jogador)",
            "arquivo_fonte": "ref/cc/C&C classes 03.pdf",
            "paginas_livro": "63–85",
            "total_paginas_pdf": 23,
            "leva": 3,
            "niveis_cobertos": "1–24",
            "versao_schema": 1,
            "idioma": "pt-BR",
        },
        "classes": [
            _mago(),
            _paladino(),
            _trapaceiro(),
            _assassino(),
        ],
        "multiclasse_e_classe_e_meia": _regras_multiclasse_e_classe_e_meia(),
    }


def validar_classes_03(dados: dict[str, Any]) -> None:
    """Valida completude da Leva 03 e integridade global das 13 classes somando classes01+02+03."""
    assert dados["metadados"]["sistema"] == "Castles & Crusades"
    classes = dados["classes"]
    assert len(classes) == 4
    assert [c["id"] for c in classes] == ["mago", "paladino", "trapaceiro", "assassino"]

    intro = json.loads((DIR_DADOS_CC / "introducao.json").read_text(encoding="utf-8"))
    c1 = json.loads((DIR_DADOS_CC / "classes01.json").read_text(encoding="utf-8"))
    c2 = json.loads((DIR_DADOS_CC / "classes02.json").read_text(encoding="utf-8"))

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

    # Cruzamento global: classes01 (5) + classes02 (4) + classes03 (4) == todas as 13 classes de introducao.json!
    todos_ids = {c["id"] for c in c1["classes"]} | {c["id"] for c in c2["classes"]} | {c["id"] for c in classes}
    assert len(todos_ids) == 13
    assert todos_ids == ids_intro, f"Diferença de classes: {todos_ids ^ ids_intro}"

    por_id = {c["id"]: c for c in classes}
    assert len(por_id["mago"]["conjuracao"]["feiticos_diarios"]) == 24
    assert por_id["mago"]["conjuracao"]["feiticos_diarios"]["1"] == {"0": 4, "1": 2}
    assert por_id["mago"]["conjuracao"]["feiticos_diarios"]["24"] == {
        "0": 8, "1": 8, "2": 7, "3": 7, "4": 6, "5": 6, "6": 5, "7": 5, "8": 4, "9": 4
    }
    assert len(por_id["assassino"]["tabela_venenos"]) == 6
    assert por_id["trapaceiro"]["progressao"][-1]["bpa"] == 8
    assert por_id["assassino"]["progressao"][-1]["bpa"] == 8
    assert len(dados["multiclasse_e_classe_e_meia"]["multiclasse"]["xp_adicional_por_nivel"]) == 12
    assert len(dados["multiclasse_e_classe_e_meia"]["classe_e_meia"]["tabela_progressao_niveis"]) == 10


def main() -> None:
    """Gera `dados/dadosc&c/classes03.json`, recarrega do disco e valida todas as 13 classes."""
    dados = construir_classes_03()
    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_SAIDA.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    recarregado = json.loads(CAMINHO_SAIDA.read_text(encoding="utf-8"))
    validar_classes_03(recarregado)
    total_habs = sum(len(c["habilidades"]) for c in recarregado["classes"])
    print(f"OK — {CAMINHO_SAIDA.relative_to(RAIZ_PROJETO)} gerado e validado com sucesso!")
    print(
        f"Classes Leva 03: {len(recarregado['classes'])} (Mago, Paladino, Trapaceiro, Assassino) | "
        f"Habilidades detalhadas: {total_habs} | Venenos: 6 níveis (I–VI) | "
        f"Cobertura total C&C: 13/13 classes validadas 1:1 com introducao.json!"
    )


if __name__ == "__main__":
    main()
