"""Gerador e validador de dados/equipamentos.json a partir de ref/Tools.pdf."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_SAIDA = RAIZ_PROJETO / "dados" / "dadospf2" / "equipamentos.json"

MULTIPLICADORES_MOEDA_PC = {
    "pc": 1,
    "pp": 10,
    "po": 100,
    "pl": 1000,
}

MATERIAIS_ARMADURA = {
    "Tecido": {"dureza": 1, "pv": 4, "limiar_quebra": 2},
    "Couro": {"dureza": 4, "pv": 16, "limiar_quebra": 8},
    "Metal": {"dureza": 9, "pv": 36, "limiar_quebra": 18},
}


def slugify(texto: str) -> str:
    """Converte um nome em identificador snake_case ASCII."""
    normalizado = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(c for c in normalizado if not unicodedata.combining(c))
    limpo = re.sub(r"[^a-zA-Z0-9]+", "_", sem_acentos.lower()).strip("_")
    return limpo


def parse_preco_pc(preco: str) -> int | None:
    """Converte string de preço (ex.: '3 po', '9 po, 6 pp', '5.000 po') para peças de cobre."""
    texto = preco.strip().lower()
    if texto in {"—", "-", "varia", ""}:
        return None
    if texto == "0":
        return 0

    total_pc = 0
    encontrou = False
    for parte in texto.split(","):
        m = re.search(r"([\d.]+)\s*(pc|pp|po|pl)\b", parte.strip())
        if m:
            valor = int(m.group(1).replace(".", ""))
            unidade = m.group(2)
            total_pc += valor * MULTIPLICADORES_MOEDA_PC[unidade]
            encontrou = True
    if not encontrou:
        raise ValueError(f"Não foi possível converter preço para pc: {preco!r}")
    return total_pc


def parse_volume_valor(volume: str) -> float:
    """Converte string de Volume ('—', 'L', '1', '16') para valor numérico."""
    v = volume.strip().upper()
    if v in {"—", "-", "0"}:
        return 0.0
    if v == "L":
        return 0.1
    return float(int(v))


def parse_dano(dano: str) -> dict[str, Any]:
    """Extrai estrutura numérica/tipo de uma string de dano (ex.: '1d8 Pf', '1 Pf', 'Varia')."""
    texto = dano.strip()
    if texto.lower() == "varia":
        return {"dano_quantidade": None, "dano_dado": None, "dano_fixo": None, "dano_tipo": "Varia"}
    m_dado = re.match(r"^(\d+)(d\d+)\s+(Cn|Ct|Pf)$", texto)
    if m_dado:
        return {
            "dano_quantidade": int(m_dado.group(1)),
            "dano_dado": m_dado.group(2),
            "dano_fixo": None,
            "dano_tipo": m_dado.group(3),
        }
    m_fixo = re.match(r"^(\d+)\s+(Cn|Ct|Pf)$", texto)
    if m_fixo:
        return {
            "dano_quantidade": None,
            "dano_dado": None,
            "dano_fixo": int(m_fixo.group(1)),
            "dano_tipo": m_fixo.group(2),
        }
    raise ValueError(f"Formato de dano não reconhecido: {dano!r}")


def construir_armadura(
    nome: str,
    categoria: str,
    preco: str,
    bonus_ca: int,
    limite_destreza: int | None,
    penalidade_testes: int,
    penalidade_velocidade_m: float,
    forca_minima: int | None,
    volume: str,
    grupo: str | None,
    tracos: list[str],
    material: str | None,
    descricao: str,
    nivel: int = 0,
    raridade: str = "Comum",
    inclui_subcamada_e_manoplas: bool = False,
) -> dict[str, Any]:
    """Monta entrada normalizada de armadura ou defesa sem armadura."""
    stats_mat = MATERIAIS_ARMADURA.get(material) if material else None
    return {
        "id": slugify(nome),
        "nome": nome,
        "categoria": categoria,
        "raridade": raridade,
        "nivel": nivel,
        "preco": preco,
        "preco_pc": parse_preco_pc(preco),
        "bonus_ca": bonus_ca,
        "limite_destreza": limite_destreza,
        "penalidade_testes": penalidade_testes,
        "penalidade_velocidade_m": penalidade_velocidade_m,
        "forca_minima": forca_minima,
        "volume": volume,
        "volume_valor": parse_volume_valor(volume),
        "grupo": grupo,
        "tracos": tracos,
        "material": material,
        "dureza": stats_mat["dureza"] if stats_mat else None,
        "pv": stats_mat["pv"] if stats_mat else None,
        "limiar_quebra": stats_mat["limiar_quebra"] if stats_mat else None,
        "inclui_subcamada_e_manoplas": inclui_subcamada_e_manoplas,
        "descricao": descricao,
    }


def construir_escudo(
    nome: str,
    preco: str,
    bonus_ca: int,
    bonus_ca_cobertura: int | None,
    penalidade_velocidade_m: float,
    volume: str,
    dureza: int,
    pv: int,
    limiar_quebra: int,
    permite_mao_livre: bool,
    descricao: str,
    nivel: int = 0,
) -> dict[str, Any]:
    """Monta entrada normalizada de escudo."""
    return {
        "id": slugify(nome),
        "nome": nome,
        "nivel": nivel,
        "preco": preco,
        "preco_pc": parse_preco_pc(preco),
        "bonus_ca": bonus_ca,
        "bonus_ca_cobertura": bonus_ca_cobertura,
        "penalidade_velocidade_m": penalidade_velocidade_m,
        "volume": volume,
        "volume_valor": parse_volume_valor(volume),
        "dureza": dureza,
        "pv": pv,
        "limiar_quebra": limiar_quebra,
        "permite_mao_livre": permite_mao_livre,
        "descricao": descricao,
    }


def construir_arma(
    nome: str,
    categoria: str,
    raridade: str,
    preco: str,
    dano: str,
    volume: str,
    maos: str,
    grupo: str,
    tracos: list[str],
    descricao: str,
    distancia_m: int | None = None,
    recarga: int | None = None,
    municao: str | None = None,
    nivel: int = 0,
) -> dict[str, Any]:
    """Monta entrada normalizada de arma corpo a corpo, à distância ou ataque desarmado."""
    dano_info = parse_dano(dano)
    return {
        "id": slugify(nome),
        "nome": nome,
        "categoria": categoria,
        "raridade": raridade,
        "nivel": nivel,
        "preco": preco,
        "preco_pc": parse_preco_pc(preco),
        "dano": dano,
        **dano_info,
        "distancia_m": distancia_m,
        "recarga": recarga,
        "volume": volume,
        "volume_valor": parse_volume_valor(volume),
        "maos": maos,
        "grupo": grupo,
        "tracos": tracos,
        "municao": municao,
        "descricao": descricao,
    }


def construir_equipamento_aventura(
    nome: str,
    preco: str,
    volume: str,
    maos: str,
    descricao: str,
    item_base: str | None = None,
    raridade: str = "Comum",
    nivel: int = 0,
    quantidade_pacote: int = 1,
    bonus_item: str | None = None,
    conteudo: list[str] | None = None,
    notas: str | None = None,
) -> dict[str, Any]:
    """Monta entrada normalizada de equipamento de aventura."""
    item: dict[str, Any] = {
        "id": slugify(nome),
        "nome": nome,
        "item_base": item_base,
        "raridade": raridade,
        "nivel": nivel,
        "quantidade_pacote": quantidade_pacote,
        "preco": preco,
        "preco_pc": parse_preco_pc(preco),
        "volume": volume,
        "volume_valor": parse_volume_valor(volume),
        "maos": maos,
        "bonus_item": bonus_item,
        "descricao": descricao,
    }
    if conteudo is not None:
        item["conteudo"] = conteudo
    if notas is not None:
        item["notas"] = notas
    return item


def construir_kit_classe(
    classe: str,
    preco: str,
    volume_texto: str,
    dinheiro_restante: str,
    armadura: str | None,
    armas: list[str],
    equipamentos: list[str],
    opcoes: list[str],
    nota: str | None = None,
) -> dict[str, Any]:
    """Monta entrada normalizada de kit inicial de classe."""
    kit: dict[str, Any] = {
        "id": slugify(classe),
        "classe": classe,
        "preco": preco,
        "preco_pc": parse_preco_pc(preco),
        "volume_texto": volume_texto,
        "dinheiro_restante": dinheiro_restante,
        "dinheiro_restante_pc": parse_preco_pc(dinheiro_restante),
        "armadura": armadura,
        "armas": armas,
        "equipamentos": equipamentos,
        "opcoes": opcoes,
    }
    if nota is not None:
        kit["nota"] = nota
    return kit


def obter_regras_gerais() -> dict[str, Any]:
    """Retorna regras gerais de dinheiro, volume, troca de equipamentos e dano em itens."""
    return {
        "dinheiro_inicial": {
            "po": 15,
            "pp": 150,
            "pc": 1500,
            "observacao": (
                "Seu personagem começa com 15 peças de ouro (150 peças de prata) para gastar "
                "em quaisquer itens comuns do Capítulo 6. Itens incomuns exigem acesso especial "
                "ou permissão do MJ."
            ),
        },
        "tabela_6_1_moedas": {
            "moedas": [
                {
                    "nome": "Peça de cobre",
                    "sigla": "pc",
                    "valor_em_pc": 1,
                    "taxas": {"pc": "1", "pp": "1/10", "po": "1/100", "pl": "1/1.000"},
                },
                {
                    "nome": "Peça de prata",
                    "sigla": "pp",
                    "valor_em_pc": 10,
                    "taxas": {"pc": "10", "pp": "1", "po": "1/10", "pl": "1/100"},
                },
                {
                    "nome": "Peça de ouro",
                    "sigla": "po",
                    "valor_em_pc": 100,
                    "taxas": {"pc": "100", "pp": "10", "po": "1", "pl": "1/10"},
                },
                {
                    "nome": "Peça de platina",
                    "sigla": "pl",
                    "valor_em_pc": 1000,
                    "taxas": {"pc": "1.000", "pp": "100", "po": "10", "pl": "1"},
                },
            ],
            "regras_preco_e_venda": {
                "venda_padrao_proporcao": 0.5,
                "venda_integral_itens": [
                    "moedas",
                    "gemas",
                    "objetos de arte",
                    "matérias-primas (como as usadas para Manufaturar)",
                ],
                "preco_traco": "Um item com Preço '—' não pode ser comprado.",
                "preco_zero": "Um item com Preço 0 normalmente é gratuito.",
            },
            "volume_moedas": {
                "moedas_por_volume_1": 1000,
                "regra": (
                    "Mil moedas de qualquer denominação ou combinação contam como Volume 1, "
                    "arredondando frações de 1.000 para baixo (100 moedas = 0; 1.999 moedas = Volume 1)."
                ),
            },
        },
        "regras_volume": {
            "limite_sem_penalidade_base": 5,
            "formula_limite_sem_penalidade": "5 + modificador de Força",
            "limite_maximo_base": 10,
            "formula_limite_maximo": "10 + modificador de Força",
            "condicao_sobrecarregado": {
                "condicoes": ["desajeitado 1"],
                "penalidade_velocidade_m": -3.0,
                "velocidade_minima_m": 1.5,
                "descricao": (
                    "Enquanto estiver sobrecarregado (acima de 5 + mod. Força), você fica "
                    "desajeitado 1 e sofre -3 metros de penalidade em todas as suas Velocidades "
                    "(não pode reduzir abaixo de 1,5 metros)."
                ),
            },
            "itens_leves_por_volume": 10,
            "regra_arredondamento_leves": (
                "Dez itens leves (L) contam como Volume 1, e frações são arredondadas para baixo "
                "(9 leves = Volume 0; 11 leves = Volume 1). Itens desprezíveis (—) não contam para "
                "o Volume a menos que carregados em quantidades consideráveis."
            ),
            "estimativa_por_peso": (
                "2,5 a 5 quilos = Volume 1; menos de meio quilo = desprezível (—); "
                "entre meio quilo e 2,5 quilos = leve (L)."
            ),
            "arrastando": {
                "multiplicador_volume": 0.5,
                "maos": 2,
                "velocidade_m_por_minuto": 15,
                "regra": (
                    "Arrastar um objeto ou criatura trata o Volume total como metade do normal, "
                    "exige duas mãos, uma coisa por vez, a cerca de 15 metros por minuto."
                ),
            },
            "volume_criaturas": [
                {"tamanho": "Minúsculo", "volume": 1},
                {"tamanho": "Pequeno", "volume": 3},
                {"tamanho": "Médio", "volume": 6},
                {"tamanho": "Grande", "volume": 12},
                {"tamanho": "Enorme", "volume": 24},
                {"tamanho": "Imenso", "volume": 48},
            ],
        },
        "tabela_6_2_mudando_equipamentos": {
            "acoes": [
                {
                    "mudanca": "Sacar, guardar ou pegar um item",
                    "nota_ref": 1,
                    "maos": "1 ou 2",
                    "acao": "Interagir",
                },
                {
                    "mudanca": "Passar um item para uma criatura voluntária ou pegá-lo com ela",
                    "nota_ref": 2,
                    "maos": "1 ou 2",
                    "acao": "Interagir",
                },
                {
                    "mudanca": "Soltar um item no chão",
                    "nota_ref": None,
                    "maos": "1 ou 2",
                    "acao": "Largar",
                },
                {
                    "mudanca": "Soltar um escudo preso em você",
                    "nota_ref": None,
                    "maos": "1",
                    "acao": "Interagir",
                },
                {
                    "mudanca": "Mudar sua empunhadura removendo uma mão de um item",
                    "nota_ref": None,
                    "maos": "2",
                    "acao": "Largar",
                },
                {
                    "mudanca": "Mudar sua empunhadura adicionando uma mão a um item",
                    "nota_ref": None,
                    "maos": "2",
                    "acao": "Interagir",
                },
                {
                    "mudanca": "Pegar um item de uma mochila ou bolsa",
                    "nota_ref": 3,
                    "maos": "2",
                    "acao": "Interagir",
                },
            ],
            "notas": {
                "1": (
                    "Se pegar um item de duas mãos com somente uma mão, você ainda precisa "
                    "mudar sua empunhadura antes de poder usá-lo."
                ),
                "2": (
                    "Uma criatura deve ter uma mão livre para que alguém passe um item para ela, "
                    "e pode precisar mudar a empunhadura dela para receber um item que requeira "
                    "duas mãos para ser empunhado ou usado."
                ),
                "3": (
                    "Pegar um item armazenado em sua própria mochila requer que primeiro você tire "
                    "a mochila das costas com uma ação de Interagir separada."
                ),
            },
        },
        "regras_dano_itens": {
            "dureza_e_pv": (
                "Cada vez que um item sofre dano, reduza o dano pela Dureza listada. O dano "
                "remanescente reduz os Pontos de Vida (PV) do item."
            ),
            "quebrado": {
                "gatilho": "PV <= Limiar de Quebra (LQ)",
                "efeito_geral": (
                    "Um objeto quebrado não pode ser usado para sua função normal nem concede "
                    "bônus, exceto armaduras, mantendo penalidades e limitações de uso/carga."
                ),
                "penalidade_estado_ca_armadura_quebrada": {
                    "Armadura Leve": -1,
                    "Armadura Média": -2,
                    "Armadura Pesada": -3,
                },
            },
            "destruido": "Um item é destruído quando seus PV chegam a 0 e não pode ser Reparado.",
            "imunidades_objeto": [
                "ataques não-letais",
                "cura",
                "doenças",
                "efeitos mentais (exceto se o item possuir uma mente)",
                "efeitos de morte",
                "necromancia",
                "sangramento",
                "venenos",
                "condenado",
                "drenado",
                "enjoado",
                "inconsciente",
                "fatigado",
                "paralisado",
            ],
            "itens_ma_qualidade": {
                "multiplicador_preco": 0.5,
                "vendavel": False,
                "penalidade_item": -2,
                "piora_penalidade_armadura": -2,
                "multiplicador_pv_lq": 0.5,
                "descricao": (
                    "Custa metade do Preço padrão, nunca pode ser vendido, impõe -2 de penalidade "
                    "de item em ataques, testes e CDs (como CA), piora penalidade em testes da "
                    "armadura em 2 pontos e possui metade dos PV e LQ normais."
                ),
            },
        },
    }


def obter_armaduras() -> dict[str, Any]:
    """Retorna regras, traços, especializações, materiais e todas as armaduras (Tabelas 6-3 e 6-4)."""
    itens = [
        # Tabela 6-3: Defesa Sem Armadura (2)
        construir_armadura(
            nome="Nenhuma armadura",
            categoria="Sem Armadura",
            preco="—",
            bonus_ca=0,
            limite_destreza=None,
            penalidade_testes=0,
            penalidade_velocidade_m=0.0,
            forca_minima=None,
            volume="—",
            grupo=None,
            tracos=[],
            material=None,
            descricao="Sem proteção de armadura; utiliza proficiência em defesa sem armadura.",
        ),
        construir_armadura(
            nome="Roupa de explorador",
            categoria="Sem Armadura",
            preco="1 pp",
            bonus_ca=0,
            limite_destreza=5,
            penalidade_testes=0,
            penalidade_velocidade_m=0.0,
            forca_minima=None,
            volume="L",
            grupo=None,
            tracos=["Confortável"],
            material="Tecido",
            descricao=(
                "Aventureiros que não usam armaduras viajam vestindo roupas duráveis. Embora não "
                "seja uma armadura e utilize sua proficiência em defesa sem armadura, ela ainda "
                "possui um Limite de Des e pode conceder um bônus de item na CA se estiver gravada "
                "com runas de potência (conforme descrito na página 590)."
            ),
        ),
        # Tabela 6-4: Armaduras Leves (4)
        construir_armadura(
            nome="Armadura acolchoada",
            categoria="Armadura Leve",
            preco="2 pp",
            bonus_ca=1,
            limite_destreza=3,
            penalidade_testes=0,
            penalidade_velocidade_m=0.0,
            forca_minima=10,
            volume="L",
            grupo=None,
            tracos=["Confortável"],
            material="Tecido",
            descricao=(
                "Esta armadura é simplesmente uma camada de tecido acolchoado pesado, às vezes "
                "usada por ser bastante barata. A armadura acolchoada é mais fácil de danificar e "
                "destruir do que outros tipos de armadura. Armaduras pesadas vêm com uma subcamada "
                "de armadura acolchoada inclusa em seu Preço, embora ela perca o traço confortável "
                "quando usada sob a armadura pesada."
            ),
        ),
        construir_armadura(
            nome="Couro",
            categoria="Armadura Leve",
            preco="2 po",
            bonus_ca=1,
            limite_destreza=4,
            penalidade_testes=-1,
            penalidade_velocidade_m=0.0,
            forca_minima=10,
            volume="1",
            grupo=None,
            tracos=[],
            material="Couro",
            descricao=(
                "Um misto de couro moldado por fervura e couro mais flexível, essa armadura "
                "fornece alguma proteção com o máximo de flexibilidade."
            ),
        ),
        construir_armadura(
            nome="Couro batido",
            categoria="Armadura Leve",
            preco="3 po",
            bonus_ca=2,
            limite_destreza=3,
            penalidade_testes=-1,
            penalidade_velocidade_m=0.0,
            forca_minima=12,
            volume="1",
            grupo=None,
            tracos=[],
            material="Couro",
            descricao=(
                "Esta armadura de couro é reforçada com tachas de metal e, às vezes, pequenas "
                "placas metálicas, fornecendo a maior parte da flexibilidade de uma armadura de "
                "couro, mas providenciando uma proteção mais robusta."
            ),
        ),
        construir_armadura(
            nome="Camisão de malha",
            categoria="Armadura Leve",
            preco="5 po",
            bonus_ca=2,
            limite_destreza=3,
            penalidade_testes=-1,
            penalidade_velocidade_m=0.0,
            forca_minima=12,
            volume="1",
            grupo=None,
            tracos=["Barulhenta", "Flexível"],
            material="Metal",
            descricao=(
                "Às vezes chamada de hauberk, esta é uma camisa longa construída dos mesmos anéis "
                "de metal que a cota de malha. Entretanto, ela é muito mais leve do que uma cota "
                "de malha e protege apenas o torso, braços e coxas de seu usuário."
            ),
        ),
        # Tabela 6-4: Armaduras Médias (4)
        construir_armadura(
            nome="Gibão de peles",
            categoria="Armadura Média",
            preco="2 po",
            bonus_ca=3,
            limite_destreza=2,
            penalidade_testes=-2,
            penalidade_velocidade_m=-1.5,
            forca_minima=14,
            volume="2",
            grupo="Couro",
            tracos=[],
            material="Couro",
            descricao=(
                "Um misto de peles, couro rígido e, às vezes, couro fervido moldado, esta "
                "armadura fornece proteção devido às suas camadas de couro — embora seu volume "
                "deixe seu usuário lento e com mobilidade reduzida."
            ),
        ),
        construir_armadura(
            nome="Cota de escamas",
            categoria="Armadura Média",
            preco="4 po",
            bonus_ca=3,
            limite_destreza=2,
            penalidade_testes=-2,
            penalidade_velocidade_m=-1.5,
            forca_minima=14,
            volume="2",
            grupo="Composta",
            tracos=[],
            material="Metal",
            descricao=(
                "Cotas de escamas consistem de muitas escamas de metal costuradas em um fundo de "
                "couro reforçado, frequentemente na forma de uma longa camisa que protege o torso, "
                "braços e pernas."
            ),
        ),
        construir_armadura(
            nome="Cota de malha",
            categoria="Armadura Média",
            preco="6 po",
            bonus_ca=4,
            limite_destreza=1,
            penalidade_testes=-2,
            penalidade_velocidade_m=-1.5,
            forca_minima=16,
            volume="2",
            grupo="Malha",
            tracos=["Barulhenta", "Flexível"],
            material="Metal",
            descricao=(
                "Uma cota de malha consiste de várias peças de armadura compostas de pequenos "
                "anéis de metal unidos formando uma malha protetora. Tipicamente ela inclui uma "
                "camisão de malha, calças, um par de proteção para os braços e uma coifa, "
                "coletivamente protegendo a maior parte do corpo."
            ),
        ),
        construir_armadura(
            nome="Placa peitoral",
            categoria="Armadura Média",
            preco="8 po",
            bonus_ca=4,
            limite_destreza=1,
            penalidade_testes=-2,
            penalidade_velocidade_m=-1.5,
            forca_minima=16,
            volume="2",
            grupo="Placas",
            tracos=[],
            material="Metal",
            descricao=(
                "Embora chamada de placa peitoral, este tipo de armadura consiste de várias placas "
                "de armadura completa ou meia armadura que protegem o torso, peito, pescoço e às "
                "vezes o quadril e as pernas. Ela estrategicamente concede parte da proteção da "
                "armadura completa enquanto permite maior flexibilidade e velocidade."
            ),
        ),
        # Tabela 6-4: Armaduras Pesadas (3)
        construir_armadura(
            nome="Cota de talas",
            categoria="Armadura Pesada",
            nivel=1,
            preco="13 po",
            bonus_ca=5,
            limite_destreza=1,
            penalidade_testes=-3,
            penalidade_velocidade_m=-3.0,
            forca_minima=16,
            volume="3",
            grupo="Composta",
            tracos=[],
            material="Metal",
            inclui_subcamada_e_manoplas=True,
            descricao=(
                "Este tipo de armadura é uma cota de malha reforçada com placas de metal flexível "
                "interligadas, tipicamente localizadas no torso, braços e pernas. Um conjunto "
                "desta armadura vem com uma subcamada de armadura acolchoada e um par de manoplas."
            ),
        ),
        construir_armadura(
            nome="Meia armadura",
            categoria="Armadura Pesada",
            nivel=1,
            preco="18 po",
            bonus_ca=5,
            limite_destreza=1,
            penalidade_testes=-3,
            penalidade_velocidade_m=-3.0,
            forca_minima=16,
            volume="3",
            grupo="Placas",
            tracos=[],
            material="Metal",
            inclui_subcamada_e_manoplas=True,
            descricao=(
                "Uma meia armadura consiste da parte superior das placas usadas em uma armadura "
                "completa, com placas de aço mais leves ou mais esparsas para os braços e pernas. "
                "Isto fornece parte da proteção de uma armadura completa, porém com maior "
                "flexibilidade e velocidade. Um conjunto desta armadura vem com uma subcamada de "
                "armadura acolchoada e um par de manoplas."
            ),
        ),
        construir_armadura(
            nome="Armadura completa",
            categoria="Armadura Pesada",
            nivel=2,
            preco="30 po",
            bonus_ca=6,
            limite_destreza=0,
            penalidade_testes=-3,
            penalidade_velocidade_m=-3.0,
            forca_minima=18,
            volume="4",
            grupo="Placas",
            tracos=["Baluarte"],
            material="Metal",
            inclui_subcamada_e_manoplas=True,
            descricao=(
                "Uma armadura completa consiste de placas interconectadas que cobrem o corpo quase "
                "inteiro em uma carapaça de aço. Ela é cara e pesada e o usuário frequentemente "
                "precisa de ajuda para vesti-la corretamente, mas fornece uma das melhores defesas "
                "que uma armadura pode fornecer. Esta armadura vem com uma subcamada de armadura "
                "acolchoada e um par de manoplas."
            ),
        ),
    ]

    return {
        "regras_ca": {
            "formula": (
                "Classe de Armadura = 10 + modificador de Destreza (até o Limite de Destreza de "
                "sua armadura) + bônus de proficiência + bônus de item da armadura na CA + "
                "outros bônus + penalidades"
            ),
            "tempo_colocar_remover": {
                "colocar_leve": "1 minuto",
                "colocar_media_ou_pesada": "5 minutos",
                "remover_qualquer": "1 minuto",
            },
            "regra_forca": (
                "Se o seu valor de Força for igual ou maior do que o valor de Força listado na "
                "armadura, você não sofre a penalidade em testes (exceto Furtividade se tiver o "
                "traço Barulhenta) e diminui a penalidade de Velocidade em 1,5 metros."
            ),
            "regra_volume_carregada": (
                "Uma armadura que seja carregada ou desgastada em vez de vestida normalmente "
                "possui 1 Volume a mais do que o listado (ou 1 de Volume total para Volume leve)."
            ),
        },
        "tracos_armadura": {
            "Baluarte": (
                "A armadura o cobre tão completamente que fornece benefícios contra alguns efeitos "
                "de dano. Em jogadas de Reflexos para evitar um efeito de dano, como contra uma "
                "bola de fogo, adicione +3 de modificador em vez de seu modificador de Destreza."
            ),
            "Barulhenta": (
                "Esta armadura é barulhenta e tende a alertar os outros sobre sua presença. A "
                "penalidade em testes da armadura se aplica a testes de Furtividade mesmo se você "
                "possuir o valor de Força exigido pela armadura."
            ),
            "Confortável": (
                "A armadura é tão confortável que você pode descansar normalmente enquanto a veste."
            ),
            "Flexível": (
                "A armadura é flexível o suficiente para que não atrapalhe a maioria de suas ações. "
                "Você não aplica sua penalidade em testes de Acrobatismo e Atletismo."
            ),
        },
        "efeitos_especializacao_armadura": {
            "Composta": (
                "As várias peças sobrepostas desta armadura lhe protegem de ataques perfurantes. "
                "Você ganha resistência a dano perfurante igual a 1 + o valor da runa de potência "
                "dela para armaduras médias ou 2 + o valor da runa de potência dela para armaduras "
                "pesadas."
            ),
            "Couro": (
                "A grossura da pele da armadura dispersa a força do impacto, reduzindo dano "
                "contundente. Você ganha resistência a dano contundente igual a 1 + o valor da "
                "runa de potência dela para armaduras médias ou 2 + o valor da runa de potência "
                "dela para armaduras pesadas."
            ),
            "Malha": (
                "A armadura é tão flexível que pode se dobrar com um acerto crítico, absorvendo "
                "parte do golpe. Reduza o dano de acertos críticos em 4 + o valor da runa de "
                "potência dela para armaduras médias ou 6 + o valor da runa de potência dela para "
                "armaduras pesadas. Isto não pode reduzir o dano abaixo do dano rolado antes dele "
                "ser dobrado pelo acerto crítico."
            ),
            "Placas": (
                "As placas resistentes não deixam falhas para lâminas cortantes. Você ganha "
                "resistência a dano cortante igual a 1 + o valor da runa de potência dela para "
                "armaduras médias ou 2 + o valor da runa de potência dela para armaduras pesadas."
            ),
        },
        "materiais_armadura": [
            {
                "material": "Tecido",
                "exemplos": ["armadura acolchoada", "roupa de explorador"],
                "dureza": 1,
                "pv": 4,
                "limiar_quebra": 2,
            },
            {
                "material": "Couro",
                "exemplos": ["couro", "couro batido", "gibão de peles"],
                "dureza": 4,
                "pv": 16,
                "limiar_quebra": 8,
            },
            {
                "material": "Metal",
                "exemplos": [
                    "armadura completa",
                    "camisão de malha",
                    "cota de escamas",
                    "cota de malha",
                    "cota de talas",
                    "meia armadura",
                    "placa peitoral",
                ],
                "dureza": 9,
                "pv": 36,
                "limiar_quebra": 18,
            },
        ],
        "itens": itens,
    }


def obter_escudos() -> dict[str, Any]:
    """Retorna regras de escudos e a Tabela 6-5."""
    return {
        "regras": {
            "erguer_um_escudo": (
                "Um escudo concede seu bônus na CA como um bônus de circunstância apenas enquanto "
                "estiver erguido usando a ação Erguer um Escudo (página 472), até o começo do seu "
                "próximo turno. A penalidade de Velocidade se aplica sempre que segurar o escudo."
            ),
            "bloqueio_com_escudo": (
                "Se tiver a reação Bloqueio com Escudo, enquanto estiver Erguendo um Escudo você "
                "pode reduzir o dano sofrido por uma quantidade igual à Dureza do escudo; tanto "
                "você quanto o escudo sofrem qualquer dano remanescente."
            ),
            "ataque_com_escudo": (
                "Um escudo pode ser usado para atacar como arma marcial utilizando as estatísticas "
                "de pancada com escudo na Tabela 6-7, ou com anexos (bossa de escudo / cravos de "
                "escudo). Escudos não podem ter runas gravadas diretamente, mas seus anexos podem."
            ),
        },
        "itens": [
            construir_escudo(
                nome="Broquel",
                preco="1 po",
                bonus_ca=1,
                bonus_ca_cobertura=None,
                penalidade_velocidade_m=0.0,
                volume="L",
                dureza=3,
                pv=6,
                limiar_quebra=3,
                permite_mao_livre=True,
                descricao=(
                    "Este escudo muito pequeno é um favorito entre duelistas e combatentes ágeis "
                    "que usam armaduras leves. Ele normalmente é feito de aço e preso no seu "
                    "antebraço. Você pode Erguer um Escudo com seu broquel desde que tenha a mão "
                    "livre — ou se estiver segurando um objeto leve (que não seja uma arma) nessa mão."
                ),
            ),
            construir_escudo(
                nome="Escudo de madeira",
                preco="1 po",
                bonus_ca=2,
                bonus_ca_cobertura=None,
                penalidade_velocidade_m=0.0,
                volume="1",
                dureza=3,
                pv=12,
                limiar_quebra=6,
                permite_mao_livre=False,
                descricao=(
                    "Como escudos de aço, escudos de madeira existem em vários tamanhos e "
                    "formatos. Embora sejam mais baratos que escudos de aço, quebram com maior "
                    "facilidade."
                ),
            ),
            construir_escudo(
                nome="Escudo de aço",
                preco="2 po",
                bonus_ca=2,
                bonus_ca_cobertura=None,
                penalidade_velocidade_m=0.0,
                volume="1",
                dureza=5,
                pv=20,
                limiar_quebra=10,
                permite_mao_livre=False,
                descricao=(
                    "Embora existam em vários tamanhos e formatos, a proteção oferecida por "
                    "escudos de aço vem da resistência de seu material. Embora sejam mais caros "
                    "que escudos de madeira, são muito mais duráveis."
                ),
            ),
            construir_escudo(
                nome="Escudo de corpo",
                preco="10 po",
                bonus_ca=2,
                bonus_ca_cobertura=4,
                penalidade_velocidade_m=-1.5,
                volume="4",
                dureza=5,
                pv=20,
                limiar_quebra=10,
                permite_mao_livre=False,
                descricao=(
                    "Estes escudos massivos podem ser usados para fornecer cobertura para o corpo "
                    "quase inteiro. Devido ao seu tamanho, eles normalmente são feitos de madeira "
                    "reforçada com metal. Quando erguido, você pode usar Obter Cobertura para "
                    "aumentar o bônus de circunstância na CA para +4."
                ),
            ),
        ],
    }


def obter_armas() -> dict[str, Any]:
    """Retorna regras, 32 traços, 15 especializações de crítico e Tabelas 6-6, 6-7 e 6-8."""
    tracos_arma = {
        "Acuidade": (
            "Você pode utilizar seu modificador de Destreza em vez de seu modificador de Força em "
            "rolagens de ataque usando esta arma corpo a corpo. Você ainda utiliza seu modificador "
            "de Força para calcular o dano."
        ),
        "Agarrar": (
            "Você pode usar esta arma para Agarrar com a perícia Atletismo mesmo se não tiver uma "
            "mão livre. Para isso, você utiliza o alcance da arma (se for diferente do seu) e "
            "aplica o bônus de item da arma em rolagens de ataque (se houver) como um bônus de item "
            "no teste de Atletismo. Se obtiver uma falha crítica no teste para Agarrar enquanto "
            "usar essa arma, você pode escolher soltá-la para sofrer os efeitos de uma falha em vez "
            "dos efeitos de uma falha crítica."
        ),
        "Ágil": (
            "A penalidade por ataques múltiplos que você sofre com esta arma é de -4 (em vez de -5) "
            "em seu segundo ataque no turno e de -8 (em vez de -10) em seu terceiro ataque (e "
            "ataques subsequentes) no turno."
        ),
        "Alcance": (
            "Esta arma é longa e pode ser usada para atacar criaturas a até 3 metros em vez de "
            "apenas criaturas adjacentes. Criaturas que já possuam alcance com o membro (ou "
            "membros) que empunha a arma, aumentam seu alcance com a arma em 1,5 metros."
        ),
        "Amplitude": (
            "Esta arma faz ataques amplos ou giratórios, tornando mais fácil atacar vários inimigos. "
            "Quando atacar com ela, você recebe +1 de bônus de circunstância em sua rolagem de "
            "ataque se já tiver tentado atacar um alvo diferente neste turno usando esta arma."
        ),
        "Anão": "Anões manufaturam e usam estas armas.",
        "Anexada": (
            "Uma arma anexada deve ser combinada com outro equipamento para ser usada. Este traço "
            "lista a qual tipo de item a arma deve ser anexada. Você deve estar empunhando ou usando "
            "o item ao qual a arma está anexada para poder atacar com ela. Normalmente um item pode "
            "ter apenas uma arma anexada a ele. Pode ser afixada com 10 minutos de trabalho e um "
            "teste bem-sucedido de Manufatura CD 10."
        ),
        "Aparar": (
            "Esta arma pode ser usada defensivamente para bloquear ataques. Enquanto empunhar esta "
            "arma e possuir proficiência treinado ou melhor com ela, você pode gastar uma ação de "
            "Interagir para posicionar sua arma defensivamente, recebendo +1 de bônus de "
            "circunstância na CA até o começo do seu próximo turno."
        ),
        "Apunhaladora": (
            "Quando você atinge uma criatura desprevenida, esta arma causa 1 ponto de dano de "
            "precisão em adição ao seu dano normal. O dano de precisão aumenta para 2 pontos se ela "
            "for uma arma +3."
        ),
        "Arremesso": (
            "Você pode arremessar esta arma como um ataque à distância; quando arremessada, ela é "
            "considerada uma arma à distância. Uma arma de arremesso adiciona seu modificador de "
            "Força ao dano da mesma forma que uma arma corpo a corpo. Quando este traço aparecer em "
            "uma arma corpo a corpo, ele também incluirá o incremento de distância. Armas à "
            "distância com este traço utilizam o incremento de distância especificado na entrada "
            "Distância da arma."
        ),
        "Derrubar": (
            "Você pode usar esta arma para Derrubar com a perícia Atletismo mesmo se não tiver uma "
            "mão livre. Para isso, você utiliza o alcance da arma (se for diferente do seu) e aplica "
            "o bônus de item da arma em rolagens de ataque (se houver) como um bônus de item no "
            "teste de Atletismo. Se obtiver uma falha crítica no teste para Derrubar enquanto usar "
            "essa arma, você pode escolher soltá-la para sofrer os efeitos de uma falha em vez dos "
            "efeitos de uma falha crítica."
        ),
        "Desarmado": (
            "Um ataque desarmado utiliza seu corpo em vez de uma arma manufaturada. Um ataque "
            "desarmado não é uma arma — embora seja categorizado com armas em grupos de armas e "
            "possa ter traços de armas. Como é parte de seu corpo, um ataque desarmado não pode "
            "sofrer Desarmar. Ele também não ocupa uma mão."
        ),
        "Desarmar": (
            "Você pode usar esta arma para Desarmar com a perícia Atletismo mesmo se não tiver uma "
            "mão livre. Para isso, você utiliza o alcance da arma (se for diferente do seu) e aplica "
            "o bônus de item da arma em rolagens de ataque (se houver) como um bônus de item no "
            "teste de Atletismo. Se obtiver uma falha crítica, pode soltá-la para sofrer falha "
            "normal. Em um sucesso crítico, ainda precisa de uma mão livre se quiser pegar o item."
        ),
        "Duas Mãos": (
            "Esta arma pode ser empunhada com duas mãos. Fazer isso altera o dado de dano da arma "
            "para o valor indicado. Esta mudança se aplica a todos os dados de dano da arma, assim "
            "como os dados de runas impactantes."
        ),
        "Elfo": "Elfos manufaturam e usam estas armas.",
        "Empurrar": (
            "Você pode usar esta arma para Empurrar com a perícia Atletismo mesmo se não tiver uma "
            "mão livre. Para isso, você utiliza o alcance da arma (se for diferente do seu) e aplica "
            "o bônus de item da arma em rolagens de ataque (se houver) como um bônus de item no "
            "teste de Atletismo. Se obtiver uma falha crítica, pode soltá-la para sofrer os efeitos "
            "de uma falha."
        ),
        "Enérgica": (
            "Esta arma se torna mais perigosa conforme acumula impulso. Quando atacar com ela mais "
            "de uma vez em seu turno, o segundo ataque recebe um bônus de circunstância de dano "
            "igual à quantidade de dados de dano da arma, e cada ataque subsequente recebe um bônus "
            "de circunstância igual ao dobro da quantidade de dados de dano da arma."
        ),
        "Fatal": (
            "O traço fatal inclui um tamanho de dado. Em um acerto crítico, o dado de dano da arma "
            "aumenta para esse tamanho listado (fazendo-o usar esse tamanho de dado em vez do "
            "tamanho de dano normal da arma para calcular o dano desse acerto crítico) e você "
            "adiciona um dado de dano extra do tamanho listado a esse dano."
        ),
        "Gêmea": (
            "Estas armas são usadas em pares, complementando uma à outra. Quando atacar com uma "
            "arma gêmea, você adiciona um bônus de circunstância à rolagem de dano igual à "
            "quantidade de dados de dano da arma se já tiver atacado com uma arma diferente desse "
            "mesmo tipo neste turno. As armas devem ser do mesmo tipo para se beneficiarem deste "
            "traço, mas não precisam possuir as mesmas runas."
        ),
        "Gnomo": "Gnomos manufaturam e usam estas armas.",
        "Goblin": "Goblins manufaturam e usam estas armas.",
        "Halfling": "Halflings manufaturam e usam estas armas.",
        "Justa": (
            "A arma é apropriada para combates montados sendo apoiada por suportes na armadura ou "
            "meios similares. Quando estiver montado, se tiver se movido pelo menos 3 metros na "
            "ação anterior ao seu ataque, adicione um bônus de circunstância ao dano desse ataque "
            "igual à quantidade de dados de dano dessa arma. Além disso, enquanto estiver montado, "
            "você pode empunhar a arma em uma mão, mudando o dado de dano para o valor listado."
        ),
        "Mão Livre": (
            "Esta arma não ocupa sua mão, normalmente por ser embutida em sua armadura. Uma arma "
            "de mão livre não pode ser alvo de Desarmar. Você pode usar a mão coberta por ela para "
            "empunhar outros itens e executar ações de manipular, mas não pode atacar com ela "
            "enquanto estiver usando a mão. Você só pode ter uma arma de mão livre em cada mão."
        ),
        "Monge": "Muitos monges aprendem a usar estas armas.",
        "Mortal": (
            "Em um acerto crítico, a arma adiciona um dado de dano de arma do tamanho listado. "
            "Role este dado depois de dobrar o dano da arma. Aumenta para dois dados com runa "
            "impactante maior e três dados com impactante superior."
        ),
        "Não-Letal": (
            "Ataques com esta arma são não-letais (página 453) e são usados para deixar criaturas "
            "inconscientes em vez de matá-las. Você pode usar uma arma não-letal para fazer ataques "
            "letais com -2 de penalidade de circunstância."
        ),
        "Orc": "Orcs manufaturam e usam estas armas.",
        "Oscilante": (
            "Você pode aproveitar o impulso de um ataque errado com esta arma para seu próximo "
            "ataque. Depois de errar com esta arma no seu turno, você recebe +1 de bônus de "
            "circunstância em seu próximo ataque realizado com esta arma antes do final de seu turno."
        ),
        "Propulsiva": (
            "Você adiciona metade de seu modificador de Força (se positivo) às rolagens de dano com "
            "uma arma à distância propulsiva. Se tiver um modificador de Força negativo, você "
            "adiciona seu modificador de Força inteiro."
        ),
        "Versátil": (
            "Uma arma versátil pode ser usada para causar um tipo diferente de dano do listado na "
            "seção de Dano. Este traço indica o tipo de dano alternativo (ex.: versátil Ct). Você "
            "escolhe o tipo de dano a cada ataque que fizer."
        ),
        "Voleio": (
            "Esta arma à distância é menos efetiva a curta distância. Seus ataques contra alvos "
            "dentro da distância listada sofrem -2 de penalidade."
        ),
    }

    especializacao_critico = {
        "Arco": (
            "Se o alvo de um acerto crítico estiver adjacente a uma superfície, ele fica preso "
            "nessa superfície pelo projétil. O alvo fica imobilizado e deve gastar uma ação de "
            "Interagir para fazer um teste de Atletismo CD 10 para soltar o projétil; ele não pode "
            "sair de seu espaço até que obtenha sucesso. A criatura não fica presa se for "
            "incorpórea, líquida ou puder escapar sem esforço."
        ),
        "Bomba": "Aumente o raio de respingo da bomba (se houver) para 3 metros.",
        "Clava": (
            "Você afasta o alvo em até 3 metros (você escolhe a distância). Este é um movimento "
            "forçado (página 475)."
        ),
        "Dardo": (
            "O alvo sofre 1d6 de dano persistente de sangramento. Você recebe um bônus de item "
            "neste dano de sangramento igual ao bônus de item da arma em rolagens de ataque."
        ),
        "Escudo": "Você afasta o alvo em 1,5 metros. Este é um movimento forçado (página 475).",
        "Espada": (
            "O alvo é desequilibrado pelo seu ataque, ficando desprevenido até o início do seu "
            "próximo turno."
        ),
        "Faca": (
            "O alvo sofre 1d6 de dano persistente de sangramento. Você recebe um bônus de item "
            "neste dano de sangramento igual ao bônus de item da arma em rolagens de ataque."
        ),
        "Funda": (
            "O alvo deve obter sucesso em uma jogada de Fortitude contra sua CD de classe ou fica "
            "atordoado 1."
        ),
        "Haste": (
            "O alvo é movido 1,5 metros em uma direção à sua escolha. Este é um movimento forçado "
            "(página 475)."
        ),
        "Lança": (
            "A lança perfura o alvo, enfraquecendo os ataques dele. O alvo fica desajeitado 1 até "
            "o início de seu próximo turno."
        ),
        "Machado": (
            "Escolha uma criatura adjacente ao alvo inicial e dentro do alcance. Se a CA dela for "
            "menor que o resultado da sua rolagem de ataque do acerto crítico, você causa dano a "
            "essa criatura igual ao resultado do dado de dano rolado da arma (incluindo dados "
            "extras por sua runa de potência, se houver). Esta quantia não é dobrada e nenhum "
            "bônus ou outros dados adicionais se aplicam a este dano."
        ),
        "Mangual": "O alvo é derrubado.",
        "Martelo": "O alvo é derrubado.",
        "Picareta": (
            "A arma perfura cruelmente o alvo, que sofre 2 pontos de dano adicional por dado de "
            "dano da arma."
        ),
        "Pugilato": (
            "O alvo deve obter sucesso em uma jogada de Fortitude contra sua CD de classe ou fica "
            "lento 1 até o final de seu próximo turno."
        ),
    }

    ataques_desarmados = [
        construir_arma(
            nome="Punho",
            categoria="Ataque Desarmado",
            raridade="Comum",
            preco="—",
            dano="1d4 Cn",
            volume="—",
            maos="1",
            grupo="Pugilato",
            tracos=["Acuidade", "ágil", "desarmado", "não-letal"],
            descricao=(
                "Ataque desarmado básico com punhos ou outras partes do corpo. Quase todos os "
                "personagens começam treinados em ataques desarmados."
            ),
        )
    ]

    corpo_a_corpo = [
        # Armas Simples (11)
        construir_arma(
            "Adaga",
            "Arma Simples",
            "Comum",
            "2 pp",
            "1d4 Pf",
            "L",
            "1",
            "Faca",
            ["Acuidade", "ágil", "arremesso 3 m", "versátil Ct"],
            "Esta pequena arma com lâmina é empunhada em uma mão e usada para apunhalar uma criatura em combate aproximado. Ela também pode ser arremessada.",
        ),
        construir_arma(
            "Cajado",
            "Arma Simples",
            "Comum",
            "0",
            "1d4 Cn",
            "1",
            "1",
            "Clava",
            ["Duas mãos d8"],
            "Esta longa peça de madeira pode auxiliar no caminhar e desferir golpes poderosos.",
        ),
        construir_arma(
            "Clava",
            "Arma Simples",
            "Comum",
            "0",
            "1d6 Cn",
            "1",
            "1",
            "Clava",
            ["Arremesso 3 m"],
            "Este é uma peça de madeira resistente moldada ou adaptada para esbordoar um inimigo. Clavas podem ser peças intrincadamente esculpidas de artes marciais ou algo tão simples quanto um galho de árvore ou pedaço de madeira.",
        ),
        construir_arma(
            "Foice",
            "Arma Simples",
            "Comum",
            "2 pp",
            "1d4 Ct",
            "L",
            "1",
            "Faca",
            ["Acuidade", "ágil", "derrubar"],
            "Originalmente uma ferramenta agrícola usada para colher grãos, esta arma de uma mão possui um cabo curto de madeira que termina em uma lâmina curva, às vezes afiada nos dois lados.",
        ),
        construir_arma(
            "Lança",
            "Arma Simples",
            "Comum",
            "1 pp",
            "1d6 Pf",
            "1",
            "1",
            "Lança",
            ["Arremesso 6 m"],
            "Composta por um longo cabo de metal e ponta com cravo do mesmo material, uma lança pode ser usada com uma mão como arma branca ou ser arremessada.",
        ),
        construir_arma(
            "Lança longa",
            "Arma Simples",
            "Comum",
            "5 pp",
            "1d8 Pf",
            "2",
            "2",
            "Lança",
            ["Alcance"],
            "Esta lança muito longa, às vezes chamada de pique, é feita apenas para perfurar e não para arremessar. Usada por muitos soldados e guardas de cidades para controle de multidão e defesa contra inimigos em investida, ela deve ser portada com as duas mãos.",
        ),
        construir_arma(
            "Maça",
            "Arma Simples",
            "Comum",
            "1 po",
            "1d6 Cn",
            "1",
            "1",
            "Clava",
            ["Empurrar"],
            "Com um cabo robusto e uma cabeça pesada de metal, uma maça é resistente e permite que seu usuário faça golpes poderosos e amasse armaduras.",
        ),
        construir_arma(
            "Maça leve",
            "Arma Simples",
            "Comum",
            "4 pp",
            "1d4 Cn",
            "L",
            "1",
            "Clava",
            ["Acuidade", "ágil", "empurrar"],
            "Uma maça leve possui um cabo de madeira ou metal que termina em uma densa cabeça de metal. Usada quase como uma clava, ela desfere golpes contundentes pesados, mas com poder extra vindo das tachas ou espinhos da cabeça de metal.",
        ),
        construir_arma(
            "Maça-estrela",
            "Arma Simples",
            "Comum",
            "1 po",
            "1d6 Cn",
            "1",
            "1",
            "Clava",
            ["Versátil Pf"],
            "Esta arma possui um cabo curto que termina em uma bola de metal cheia de espinhos.",
        ),
        construir_arma(
            "Manopla",
            "Arma Simples",
            "Comum",
            "2 pp",
            "1d4 Cn",
            "L",
            "1",
            "Pugilato",
            ["Ágil", "mão livre"],
            "Armaduras completas, meia armaduras e cotas de talas vêm com um par destas luvas de metal; mas elas também podem ser compradas separadamente e usadas com outros tipos de armadura. Elas não apenas protegem suas mãos como também transformam suas mãos em armas letais.",
        ),
        construir_arma(
            "Manopla com cravos",
            "Arma Simples",
            "Comum",
            "3 pp",
            "1d4 Pf",
            "L",
            "1",
            "Pugilato",
            ["Ágil", "mão livre"],
            "Fornecendo a mesma função defensiva que uma manopla comum, esta versão possui um agrupamento de cravos partindo dos nós dos dedos para causar dano perfurante com um soco.",
        ),
        # Armas Simples Incomuns (2)
        construir_arma(
            "Adaga de clã",
            "Arma Simples",
            "Incomum",
            "2 po",
            "1d4 Pf",
            "L",
            "1",
            "Faca",
            ["Ágil", "anão", "aparar", "versátil Cn"],
            "Esta adaga larga é carregada por anões como uma arma, ferramenta e designação de clã. Perder ou ter que entregar uma adaga de clã é considerado uma vergonha para a maioria dos anões.",
        ),
        construir_arma(
            "Katar (adaga de soco)",
            "Arma Simples",
            "Incomum",
            "3 pp",
            "1d4 Pf",
            "L",
            "1",
            "Faca",
            ["Ágil", "monge", "mortal d6"],
            "Também conhecidas como adagas de soco, katares são caracterizadas por seu punho em forma de 'H' que permite que a lâmina fique logo acima dos nós dos dedos.",
        ),
        # Armas Marciais (34)
        construir_arma(
            "Adaga de aparar",
            "Arma Marcial",
            "Comum",
            "5 pp",
            "1d4 Pf",
            "L",
            "1",
            "Faca",
            ["Acuidade", "ágil", "aparar", "desarmar", "versátil Ct"],
            "Esta adaga de bloqueio ostenta uma guarda robusta para proteger a mão do usuário.",
        ),
        construir_arma(
            "Alabarda",
            "Arma Marcial",
            "Comum",
            "2 po",
            "1d10 Pf",
            "2",
            "2",
            "Haste",
            ["Alcance", "versátil Ct"],
            "Esta arma de haste possui um cabo relativamente curto de 1,5 metros. Em sua ponta fica um cravo longo com uma lâmina de machado anexada.",
        ),
        construir_arma(
            "Bisarma",
            "Arma Marcial",
            "Comum",
            "2 po",
            "1d10 Ct",
            "2",
            "2",
            "Haste",
            ["Alcance", "derrubar"],
            "Esta arma de haste ostenta uma lâmina longa e curva, frequentemente de gume único, com um gancho despontando do lado oposto da lâmina, o que permite ao usuário derrubar oponentes à distância. Seu cabo normalmente mede 2,40 metros de comprimento.",
        ),
        construir_arma(
            "Bō",
            "Arma Marcial",
            "Comum",
            "2 pp",
            "1d8 Cn",
            "2",
            "2",
            "Clava",
            ["Alcance", "aparar", "derrubar", "monge"],
            "Este cajado forte, porém esguio, é estreitado nas pontas e bem balanceado. É feito para ser uma arma ofensiva e defensiva.",
        ),
        construir_arma(
            "Bossa de escudo",
            "Arma Marcial",
            "Comum",
            "5 pp",
            "1d6 Cn",
            "—",
            "1",
            "Escudo",
            ["Anexada ao escudo"],
            "Geralmente uma peça redonda, convexa ou cônica de metal denso anexada ao centro do escudo, uma bossa de escudo aumenta o dano contundente de uma pancada com escudo.",
        ),
        construir_arma(
            "Bracamante",
            "Arma Marcial",
            "Comum",
            "3 po",
            "1d10 Ct",
            "2",
            "2",
            "Espada",
            ["Amplitude", "enérgica"],
            "Esta arma é uma versão mais pesada e de duas mãos da cimitarra de lâmina curva. Seu peso em direção ao fim da lâmina a torna uma poderosa arma de corte.",
        ),
        construir_arma(
            "Chicote",
            "Arma Marcial",
            "Comum",
            "1 pp",
            "1d4 Ct",
            "1",
            "1",
            "Mangual",
            ["Acuidade", "alcance", "derrubar", "desarmar", "não-letal"],
            "Este longo cabo de couro grosso, frequentemente trançado, causa um corte doloroso, mas não-letal, à distância, normalmente acompanhado por um estalo bem distinto.",
        ),
        construir_arma(
            "Cimitarra",
            "Arma Marcial",
            "Comum",
            "1 po",
            "1d6 Ct",
            "1",
            "1",
            "Espada",
            ["Amplitude", "enérgica"],
            "Esta lâmina curva de uma mão é afiada em um dos lados.",
        ),
        construir_arma(
            "Clava pesada",
            "Arma Marcial",
            "Comum",
            "1 po",
            "1d10 Cn",
            "2",
            "2",
            "Clava",
            ["Empurrar", "oscilante"],
            "Enquanto muitas clavas pesadas são intrincadamente esculpidas, outras são pouco mais do que um grande galho de árvore. Estas clavas massivas são pesadas demais para serem usadas com apenas uma mão.",
        ),
        construir_arma(
            "Cravos de escudo",
            "Arma Marcial",
            "Comum",
            "5 pp",
            "1d6 Pf",
            "—",
            "1",
            "Escudo",
            ["Anexada ao escudo"],
            "Estes cravos de metal são estrategicamente colocados no lado defensivo do escudo para causar dano perfurante em uma pancada com escudo.",
        ),
        construir_arma(
            "Espada bastarda",
            "Arma Marcial",
            "Comum",
            "4 po",
            "1d8 Ct",
            "1",
            "1",
            "Espada",
            ["Duas mãos d12"],
            "Esta espada de lâmina larga, às vezes chamada de espada de uma mão e meia, possui um punho mais longo para que possa ser empunhada com uma mão ou usando as duas mãos para obter maior poder de corte ou perfuração.",
        ),
        construir_arma(
            "Espada curta",
            "Arma Marcial",
            "Comum",
            "9 pp",
            "1d6 Pf",
            "L",
            "1",
            "Espada",
            ["Acuidade", "ágil", "versátil Ct"],
            "Estas lâminas existem em uma variedade de formas e estilos, mas normalmente possuem 60 centímetros de comprimento.",
        ),
        construir_arma(
            "Espada longa",
            "Arma Marcial",
            "Comum",
            "1 po",
            "1d8 Ct",
            "1",
            "1",
            "Espada",
            ["Versátil Pf"],
            "Espadas longas podem ser espadas de um ou dois gumes. Suas lâminas são pesadas e elas possuem de 0,9 a 1,2 metros de comprimento.",
        ),
        construir_arma(
            "Faca-estrela",
            "Arma Marcial",
            "Comum",
            "2 po",
            "1d4 Pf",
            "L",
            "1",
            "Faca",
            ["Acuidade", "ágil", "arremesso 6 m", "mortal d6", "versátil Ct"],
            "Quatro lâminas de metal se estendem como as pontas de uma rosa dos ventos a partir de um anel central de metal. Quando empunhar uma faca-estrela pelo centro, o usuário pode usá-la como arma corpo a corpo. Ela também pode ser arremessada por curtas distâncias.",
        ),
        construir_arma(
            "Glaive",
            "Arma Marcial",
            "Comum",
            "1 po",
            "1d8 Ct",
            "2",
            "2",
            "Haste",
            ["Alcance", "enérgica", "mortal d8"],
            "Esta arma de haste consiste de uma longa lâmina de gume único no fim de uma haste de 2,10 metros. Ela é extremamente eficiente em fazer cortes letais à distância.",
        ),
        construir_arma(
            "Lança de cavalaria",
            "Arma Marcial",
            "Comum",
            "1 po",
            "1d8 Pf",
            "2",
            "2",
            "Lança",
            ["Alcance", "justa d6", "mortal d8"],
            "Esta arma similar a uma lança pesada é usada por uma criatura montada para causar muito dano.",
        ),
        construir_arma(
            "Machadinha",
            "Arma Marcial",
            "Comum",
            "4 pp",
            "1d6 Ct",
            "L",
            "1",
            "Machado",
            ["Ágil", "amplitude", "arremesso 3 m"],
            "Este pequeno machado pode ser usado em combate aproximado ou arremessado.",
        ),
        construir_arma(
            "Machado de batalha",
            "Arma Marcial",
            "Comum",
            "1 po",
            "1d8 Ct",
            "1",
            "1",
            "Machado",
            ["Amplitude"],
            "Estes machados são feitos explicitamente como armas em vez de ferramentas. Eles tipicamente possuem um peso menor, um cabo reforçado com tiras ou ferrolhos de metal e uma lâmina mais afiada, tornando-os ideais para cortar membros em vez de madeira.",
        ),
        construir_arma(
            "Machado longo",
            "Arma Marcial",
            "Comum",
            "2 po",
            "1d12 Ct",
            "2",
            "2",
            "Machado",
            ["Amplitude"],
            "Este grande machado de batalha é muito pesado para ser usado com apenas uma mão. Muitos machados longos incorporam duas lâminas frequentemente 'barbudas', com uma forma de gancho para aumentar a força do corte.",
        ),
        construir_arma(
            "Malho",
            "Arma Marcial",
            "Comum",
            "3 po",
            "1d12 Cn",
            "2",
            "2",
            "Martelo",
            ["Empurrar"],
            "Malhos são martelos de guerra massivos que devem ser usados com as duas mãos.",
        ),
        construir_arma(
            "Mangual",
            "Arma Marcial",
            "Comum",
            "8 pp",
            "1d6 Cn",
            "1",
            "1",
            "Mangual",
            ["Amplitude", "derrubar", "desarmar"],
            "Esta arma consiste de um cabo de madeira conectado por uma corrente, corda ou faixa de couro a uma bola ou cilindro com espinhos.",
        ),
        construir_arma(
            "Mangual de guerra",
            "Arma Marcial",
            "Comum",
            "2 po",
            "1d10 Cn",
            "2",
            "2",
            "Mangual",
            ["Amplitude", "derrubar", "desarmar"],
            "Este mangual grande possui um cabo longo conectado a um pedaço menor de madeira resistente ou metal que às vezes é crivado de espinhos.",
        ),
        construir_arma(
            "Martelo de guerra",
            "Arma Marcial",
            "Comum",
            "1 po",
            "1d8 Cn",
            "1",
            "1",
            "Martelo",
            ["Empurrar"],
            "Esta arma possui um cabo de madeira que termina em uma cabeça de metal grande e pesada. A cabeça do martelo pode possuir um ou dois lados, mas é sempre capaz de desferir poderosos golpes contundentes.",
        ),
        construir_arma(
            "Martelo leve",
            "Arma Marcial",
            "Comum",
            "3 pp",
            "1d6 Cn",
            "L",
            "1",
            "Martelo",
            ["Ágil", "arremesso 6 m"],
            "Esta versão menor do martelo de guerra possui um cabo de madeira ou metal que termina em uma cabeça de metal. Diferente do seu primo mais pesado, ele é leve o suficiente para ser arremessado.",
        ),
        construir_arma(
            "Montante",
            "Arma Marcial",
            "Comum",
            "2 po",
            "1d12 Ct",
            "2",
            "2",
            "Espada",
            ["Versátil Pf"],
            "Esta imensa espada de duas mãos é quase tão alta quanto seu usuário. A parte de baixo de sua lâmina frequentemente é cega para permitir que seja segurada para uso em combate próximo.",
        ),
        construir_arma(
            "Pancada com escudo",
            "Arma Marcial",
            "Comum",
            "—",
            "1d4 Cn",
            "—",
            "1",
            "Escudo",
            [],
            "Uma pancada com escudo não é uma arma de fato, e sim uma manobra na qual você empurra ou golpeia com seu escudo para acertar um inimigo com um ataque imprevisível.",
        ),
        construir_arma(
            "Picareta",
            "Arma Marcial",
            "Comum",
            "7 pp",
            "1d6 Pf",
            "1",
            "1",
            "Picareta",
            ["Fatal d10"],
            "Uma picareta projetada apenas para o combate possui um cabo de madeira e uma cabeça pesada e pontuda para desferir golpes devastadores.",
        ),
        construir_arma(
            "Picareta leve",
            "Arma Marcial",
            "Comum",
            "4 pp",
            "1d4 Pf",
            "L",
            "1",
            "Picareta",
            ["Ágil", "fatal d8"],
            "Uma picareta leve é um implemento de mineração modificado que possui um cabo de madeira terminando em uma cabeça de picareta feita mais para perfurar armadura e carne do que para lascar rochas.",
        ),
        construir_arma(
            "Picareta pesada",
            "Arma Marcial",
            "Comum",
            "1 po",
            "1d10 Pf",
            "2",
            "2",
            "Picareta",
            ["Fatal d12"],
            "Esta picareta possui cabo mais longo e cabeça mais ampla do que uma picareta convencional. Ela é pesada demais para ser usada com apenas uma mão.",
        ),
        construir_arma(
            "Porrete",
            "Arma Marcial",
            "Comum",
            "1 pp",
            "1d6 Cn",
            "L",
            "1",
            "Clava",
            ["Ágil", "não-letal"],
            "Um porrete tem um invólucro macio ao redor de um núcleo denso, geralmente uma cobertura de couro ao redor de um bastão de chumbo. A cabeça dele é mais ampla do que a empunhadura para dispersar a força do golpe, pois o propósito da arma é desacordar sua vítima em vez de tirar seu sangue.",
        ),
        construir_arma(
            "Ranseur",
            "Arma Marcial",
            "Comum",
            "2 po",
            "1d10 Pf",
            "2",
            "2",
            "Haste",
            ["Alcance", "desarmar"],
            "Esta arma de haste é um tridente longo com a ponta central mais longa do que as outras duas.",
        ),
        construir_arma(
            "Rapieira",
            "Arma Marcial",
            "Comum",
            "2 po",
            "1d6 Pf",
            "1",
            "1",
            "Espada",
            ["Acuidade", "desarmar", "mortal d8"],
            "A rapieira é uma lâmina perfurante longa e fina com um punho guarnecido. É valorizada por muitos como uma arma de duelo.",
        ),
        construir_arma(
            "Segadeira",
            "Arma Marcial",
            "Comum",
            "2 po",
            "1d10 Ct",
            "2",
            "2",
            "Haste",
            ["Derrubar", "mortal d10"],
            "Derivada de uma ferramenta agrícola usada para ceifar grãos e cereais longos, esta arma possui um cabo comprido de madeira com empunhaduras protuberantes, encimado por uma lâmina curva ajustada em um ângulo reto.",
        ),
        construir_arma(
            "Tridente",
            "Arma Marcial",
            "Comum",
            "1 po",
            "1d8 Pf",
            "1",
            "1",
            "Lança",
            ["Arremesso 6 m"],
            "Esta arma parecida com uma lança de três pontas tipicamente possui um cabo de 1,20 metros. Como uma lança, ele pode ser empunhado com uma mão ou ser arremessado.",
        ),
        # Armas Marciais Incomuns (13)
        construir_arma(
            "Adaga de soco órquica",
            "Arma Marcial",
            "Incomum",
            "7 pp",
            "1d6 Pf",
            "L",
            "1",
            "Faca",
            ["Ágil", "desarmar", "orc"],
            "Esta robusta lâmina de metal desenvolvida por orcs possui um punho horizontal com lâminas brotando em ambos os lados.",
        ),
        construir_arma(
            "Corrente com cravos",
            "Arma Marcial",
            "Incomum",
            "3 po",
            "1d8 Ct",
            "1",
            "2",
            "Mangual",
            ["Acuidade", "derrubar", "desarmar"],
            "Esta corrente de 1,20 metros de comprimento é coberta por farpas e possui cravos em uma ou ambas as pontas. Algumas ostentam argolas de metal para serem usadas como empunhaduras.",
        ),
        construir_arma(
            "Cortacão",
            "Arma Marcial",
            "Incomum",
            "1 pp",
            "1d6 Ct",
            "L",
            "1",
            "Espada",
            ["Acuidade", "ágil", "apunhaladora", "goblin"],
            "Esta lâmina curta, curvada e de manufatura bruta frequentemente possui furos em sua lâmina para reduzir seu peso. Ela é uma arma favorecida por goblins.",
        ),
        construir_arma(
            "Espada de templo",
            "Arma Marcial",
            "Incomum",
            "2 po",
            "1d8 Ct",
            "1",
            "1",
            "Espada",
            ["Derrubar", "monge"],
            "Esta lâmina pesada é favorecida por guardiões de locais religiosos. Ela possui uma lâmina distinta em formato de lua crescente que parece ser uma mistura de foice e espada.",
        ),
        construir_arma(
            "Fatia-cavalo",
            "Arma Marcial",
            "Incomum",
            "9 pp",
            "1d8 Ct",
            "2",
            "2",
            "Haste",
            ["Alcance", "derrubar", "goblin", "versátil Pf"],
            "Criada por goblins para lutar contra cavalos, esta arma é essencialmente um cabo longo que acaba em uma lâmina com um gancho grande.",
        ),
        construir_arma(
            "Forcado do furtador",
            "Arma Marcial",
            "Incomum",
            "1 po",
            "1d4 Pf",
            "L",
            "1",
            "Lança",
            ["Acuidade", "ágil", "arremesso 6 m", "apunhaladora", "halfling", "mortal d6"],
            "Esta arma de halflings parece um garfo longo com duas pontas e é usada tanto como arma quanto como implemento de cozinha.",
        ),
        construir_arma(
            "Kama",
            "Arma Marcial",
            "Incomum",
            "1 po",
            "1d6 Ct",
            "L",
            "1",
            "Faca",
            ["Ágil", "derrubar", "monge"],
            "Similar à foice e usada em algumas regiões para colher grãos, a kama é uma lâmina curta levemente curvada com um cabo de madeira.",
        ),
        construir_arma(
            "Katana",
            "Arma Marcial",
            "Incomum",
            "2 po",
            "1d6 Ct",
            "1",
            "1",
            "Espada",
            ["Duas mãos d10", "mortal d8", "versátil Pf"],
            "Uma katana é uma espada curva de gume único conhecida por sua lâmina imensamente afiada.",
        ),
        construir_arma(
            "Kukri",
            "Arma Marcial",
            "Incomum",
            "6 pp",
            "1d6 Ct",
            "L",
            "1",
            "Faca",
            ["Acuidade", "ágil", "derrubar"],
            "A lâmina desta faca de 30 centímetros se curva para dentro e não possui guarda com cruzeta no punho.",
        ),
        construir_arma(
            "Lâmina curva élfica",
            "Arma Marcial",
            "Incomum",
            "4 po",
            "1d8 Ct",
            "2",
            "2",
            "Espada",
            ["Acuidade", "elfo", "enérgica"],
            "Essencialmente uma versão mais longa da cimitarra, esta arma élfica tradicional possui uma lâmina mais fina do que a de sua prima.",
        ),
        construir_arma(
            "Martelo com gancho gnômico",
            "Arma Marcial",
            "Incomum",
            "2 po",
            "1d6 Cn",
            "1",
            "1",
            "Martelo",
            ["Derrubar", "duas mãos d10", "gnomo", "versátil Pf"],
            "Esta ferramenta e arma gnômica ostenta um martelo em uma ponta e uma picareta curva na outra. Ela é uma arma tão estranha e desengonçada que os outros acham que os gnomos são ligeiramente loucos por usá-la.",
        ),
        construir_arma(
            "Nunchaku",
            "Arma Marcial",
            "Incomum",
            "2 pp",
            "1d6 Cn",
            "L",
            "1",
            "Clava",
            ["Acuidade", "desarmar", "monge", "oscilante"],
            "O nunchaku é constituído por duas barras de madeira ou metal conectadas por uma corrente ou corda curta.",
        ),
        construir_arma(
            "Sai",
            "Arma Marcial",
            "Incomum",
            "6 pp",
            "1d4 Pf",
            "L",
            "1",
            "Faca",
            ["Acuidade", "ágil", "desarmar", "monge", "versátil Cn"],
            "Esta adaga perfurante é um espinho de metal flanqueado por um par de dentes forcados que podem ser usados para prender a arma de um inimigo.",
        ),
        # Armas Avançadas Incomuns (4)
        construir_arma(
            "Maça-chicote gnômica",
            "Arma Avançada",
            "Incomum",
            "3 po",
            "1d8 Cn",
            "2",
            "1",
            "Mangual",
            ["Alcance", "gnomo"],
            "Mais um mangual do que uma maça, esta arma possui um cabo curto conectado a uma corrente com uma bola em seu fim. A bola é propelida com um movimento do pulso, sendo que o próprio impulso traz a bola de volta para o usuário após o golpe.",
        ),
        construir_arma(
            "Machado de guerra enânico",
            "Arma Avançada",
            "Incomum",
            "3 po",
            "1d8 Ct",
            "2",
            "1",
            "Machado",
            ["Amplitude", "anão", "duas mãos d12"],
            "Esta arma favorecida por anões possui uma grande cabeça ornamentada montada em um cabo grosso. Este poderoso machado pode ser empunhado com uma ou duas mãos.",
        ),
        construir_arma(
            "Quebra-pescoço órquico",
            "Arma Avançada",
            "Incomum",
            "2 po",
            "1d8 Ct",
            "1",
            "1",
            "Machado",
            ["Amplitude", "enérgica", "orc"],
            "Este machado barbado possui uma lâmina única irregular que é perfeita para separar ossos de tendões e cartilagens.",
        ),
        construir_arma(
            "Sabre serrilhado",
            "Arma Avançada",
            "Incomum",
            "5 po",
            "1d6 Ct",
            "L",
            "1",
            "Espada",
            ["Acuidade", "ágil", "gêmea"],
            "A marca registrada dos assassinos do Louva-a-Deus Vermelho, esta lâmina curva é semelhante a uma serra — daí seu nome.",
        ),
    ]

    distancia = [
        # Armas Simples (7)
        construir_arma(
            "Azagaia",
            "Arma Simples",
            "Comum",
            "1 pp",
            "1d6 Pf",
            "L",
            "1",
            "Dardo",
            ["Arremesso"],
            "Esta lança fina é bem balanceada para arremesso, mas não é projetada para uso no combate corpo a corpo.",
            distancia_m=9,
            recarga=None,
        ),
        construir_arma(
            "Besta leve",
            "Arma Simples",
            "Comum",
            "3 po",
            "1d8 Pf",
            "1",
            "2",
            "Arco",
            [],
            "Esta arma de disparo possui uma parte parecida com um arco montada em cima de uma estrutura chamada coronha, com mecanismo para travar a corda e gatilho para lançar o virote.",
            distancia_m=36,
            recarga=1,
            municao="Virotes",
        ),
        construir_arma(
            "Besta de mão",
            "Arma Simples",
            "Comum",
            "3 po",
            "1d6 Pf",
            "L",
            "1",
            "Arco",
            [],
            "Às vezes chamada de arco dos becos por ladinos e rufiões, esta pequena besta dispara virotes pequenos. Ela é pequena o suficiente para ser disparada com uma mão, mas ainda requer as duas mãos para recarregar.",
            distancia_m=18,
            recarga=1,
            municao="Virotes",
        ),
        construir_arma(
            "Besta pesada",
            "Arma Simples",
            "Comum",
            "4 po",
            "1d10 Pf",
            "2",
            "2",
            "Arco",
            [],
            "Esta besta grande é mais difícil de recarregar e mais substancial do que uma besta convencional, mas dá golpes mais potentes.",
            distancia_m=36,
            recarga=2,
            municao="Virotes",
        ),
        construir_arma(
            "Dardo",
            "Arma Simples",
            "Comum",
            "1 pc",
            "1d4 Pf",
            "L",
            "1",
            "Dardo",
            ["Ágil", "arremesso"],
            "Esta arma de arremesso é maior do que uma flecha, mas menor do que uma azagaia. Ela tipicamente possui uma haste curta de madeira que acaba em uma ponta de metal.",
            distancia_m=6,
            recarga=None,
        ),
        construir_arma(
            "Funda",
            "Arma Simples",
            "Comum",
            "0",
            "1d6 Cn",
            "L",
            "1",
            "Funda",
            ["Propulsiva"],
            "Pouco mais que um recipiente de couro preso a um par de tiras, a funda pode ser usada para arremessar pedras lisas ou balas de funda à distância.",
            distancia_m=15,
            recarga=1,
            municao="Balas de funda",
        ),
        construir_arma(
            "Zarabatana",
            "Arma Simples",
            "Comum",
            "1 pp",
            "1 Pf",
            "L",
            "1",
            "Dardo",
            ["Ágil", "não-letal"],
            "Este tubo longo e estreito é usado para disparar dardos de zarabatana, exigindo apenas o poder de um sopro exalado com força.",
            distancia_m=6,
            recarga=1,
            municao="Dardos de zarabatana",
        ),
        # Armas Marciais (5)
        construir_arma(
            "Arco curto",
            "Arma Marcial",
            "Comum",
            "3 po",
            "1d6 Pf",
            "1",
            "1+",
            "Arco",
            ["Mortal d10"],
            "Este arco menor é feito de um único pedaço de madeira e é usado por escaramuçadores e cavalaria.",
            distancia_m=18,
            recarga=0,
            municao="Flechas",
        ),
        construir_arma(
            "Arco curto composto",
            "Arma Marcial",
            "Comum",
            "14 po",
            "1d6 Pf",
            "1",
            "1+",
            "Arco",
            ["Mortal d10", "propulsiva"],
            "Este arco curto é feito de chifre, madeira e tendões laminados juntos para aumentar o poder da puxada de sua corda e a força do projétil. O preferido entre arqueiros montados.",
            distancia_m=18,
            recarga=0,
            municao="Flechas",
        ),
        construir_arma(
            "Arco longo",
            "Arma Marcial",
            "Comum",
            "6 po",
            "1d8 Pf",
            "2",
            "1+",
            "Arco",
            ["Mortal d10", "voleio 9 m"],
            "Este arco de 1,5 metros de comprimento, normalmente feito de nogueira, olmo ou teixo, possui tração poderosa. Você deve usar as duas mãos para disparar um arco longo e ele não pode ser usado sobre uma montaria.",
            distancia_m=30,
            recarga=0,
            municao="Flechas",
        ),
        construir_arma(
            "Arco longo composto",
            "Arma Marcial",
            "Comum",
            "20 po",
            "1d8 Pf",
            "2",
            "1+",
            "Arco",
            ["Mortal d10", "propulsiva", "voleio 9 m"],
            "Esta arma de disparo é feita de chifre, madeira e tendões laminados juntos para aumentar o poder da puxada e a força do projétil. Você deve usar as duas mãos para dispará-lo e ele não pode ser usado sobre uma montaria.",
            distancia_m=30,
            recarga=0,
            municao="Flechas",
        ),
        construir_arma(
            "Bomba alquímica",
            "Arma Marcial",
            "Comum",
            "Varia",
            "Varia",
            "L",
            "1",
            "Bomba",
            ["Varia"],
            "Estas bombas existem em uma grande variedade de tipos e níveis de poder. Independentemente de sua variedade, você a arremessa no alvo e ela explode, liberando sua rajada alquímica. Estatísticas podem ser encontradas a partir da página 544.",
            distancia_m=6,
            recarga=None,
        ),
        # Armas Marciais Incomuns (2)
        construir_arma(
            "Cajado-funda halfling",
            "Arma Marcial",
            "Incomum",
            "5 po",
            "1d10 Cn",
            "1",
            "2",
            "Funda",
            ["Halfling", "propulsiva"],
            "Este cajado termina em uma ponta bifurcada que abriga uma funda. O comprimento do cajado fornece uma excelente alavanca quando usado com as duas mãos para arremessar rochas ou balas da funda.",
            distancia_m=24,
            recarga=1,
            municao="Balas de funda",
        ),
        construir_arma(
            "Shuriken",
            "Arma Marcial",
            "Incomum",
            "1 pc",
            "1d4 Pf",
            "—",
            "1",
            "Dardo",
            ["Ágil", "arremesso", "monge"],
            "Estas 'estrelas de arremesso' são pequenas peças planas de metal com as beiradas afiadas, feitas para serem arremessadas com um movimento do pulso.",
            distancia_m=6,
            recarga=0,
        ),
    ]

    municoes = [
        {
            "id": "virotes",
            "nome": "Virotes",
            "quantidade": 10,
            "preco": "1 pp",
            "preco_pc": 10,
            "volume": "L",
            "volume_valor": 0.1,
            "armas_compativeis": ["Besta leve", "Besta de mão", "Besta pesada"],
            "descricao": "Mais curtos do que as flechas tradicionais, mas tendo construção similar, virotes são a munição usada por bestas.",
        },
        {
            "id": "balas_de_funda",
            "nome": "Balas de funda",
            "quantidade": 10,
            "preco": "1 pc",
            "preco_pc": 1,
            "volume": "L",
            "volume_valor": 0.1,
            "armas_compativeis": ["Funda", "Cajado-funda halfling"],
            "descricao": "Estas pequenas bolas de metal, tipicamente de ferro ou chumbo, são projetadas para serem usadas como munição de fundas.",
        },
        {
            "id": "dardos_de_zarabatana",
            "nome": "Dardos de zarabatana",
            "quantidade": 10,
            "preco": "5 pc",
            "preco_pc": 5,
            "volume": "L",
            "volume_valor": 0.1,
            "armas_compativeis": ["Zarabatana"],
            "descricao": "Estes dardos leves e finos são tipicamente feitos de madeira de lei e estabilizados com penas ou pelos. Eles frequentemente são ocos para que possam ser usados para inocular venenos.",
        },
        {
            "id": "flechas",
            "nome": "Flechas",
            "quantidade": 10,
            "preco": "1 pp",
            "preco_pc": 10,
            "volume": "L",
            "volume_valor": 0.1,
            "armas_compativeis": [
                "Arco curto",
                "Arco curto composto",
                "Arco longo",
                "Arco longo composto",
            ],
            "descricao": "Estes projéteis são a munição para arcos. A haste de uma flecha é feita de madeira. Ela tem seu voo estabilizado por plumas em uma ponta e uma cabeça de metal na outra.",
        },
    ]

    return {
        "regras_ataque_dano": {
            "ataque_corpo_a_corpo": (
                "modificador de Força (ou opcionalmente Destreza para uma arma de acuidade) + "
                "bônus de proficiência + outros bônus + penalidades"
            ),
            "ataque_distancia": (
                "modificador de Destreza + bônus de proficiência + outros bônus + penalidades"
            ),
            "dano_corpo_a_corpo": (
                "dado de dano da arma ou ataque desarmado + modificador Força + bônus + penalidades"
            ),
            "dano_distancia": (
                "dado de dano da arma + modificador Força para armas de arremesso + bônus + penalidades"
            ),
            "penalidade_ataques_multiplos": {
                "padrao": {"segundo_ataque": -5, "terceiro_e_subsequentes": -10},
                "agil": {"segundo_ataque": -4, "terceiro_e_subsequentes": -8},
                "observacao": "Não se aplica a ataques fora do seu turno (ex.: reações).",
            },
            "acertos_criticos": (
                "20 natural ou resultado >= CA do alvo + 10 causa o dobro do dano em um Golpe."
            ),
            "armas_improvisadas": (
                "Sofre -2 de penalidade de item em rolagens de ataque; contam como armas simples; "
                "o MJ determina dano e traços."
            ),
            "progressao_tamanho_dado": ["1d4", "1d6", "1d8", "1d10", "1d12"],
            "incremento_distancia": (
                "Sem penalidade até o incremento; -2 de penalidade para cada múltiplo adicional; "
                "impossível atacar além do sexto incremento de distância."
            ),
            "maos_1_mais": (
                "Armas com '1+' podem ser seguradas em uma mão, mas exigem uma segunda mão livre "
                "para pegar, preparar e disparar."
            ),
        },
        "tracos_arma": tracos_arma,
        "efeitos_especializacao_critico": especializacao_critico,
        "ataques_desarmados": ataques_desarmados,
        "corpo_a_corpo": corpo_a_corpo,
        "distancia": distancia,
        "municoes": municoes,
    }


def obter_equipamentos_aventura() -> dict[str, Any]:
    """Retorna todos os itens das Tabelas 6-9 (Comuns) e 6-10 (Incomuns)."""
    comuns = [
        construir_equipamento_aventura(
            "Kit de aventureiro",
            "7 pp",
            "1",
            "—",
            "Este item representa o kit inicial de um aventureiro. O valor de Volume listado é para o conjunto inteiro.",
            conteudo=[
                "1 mochila (contendo os outros bens)",
                "2 algibeiras",
                "1 cantil",
                "15 metros de corda",
                "1 esteira de dormir",
                "10 peças de giz",
                "pederneira e isqueiro",
                "2 semanas de ração",
                "sabão",
                "5 tochas",
            ],
        ),
        construir_equipamento_aventura(
            "Alforje",
            "2 pp",
            "L",
            "2",
            "Alforjes vêm em pares. Cada um pode armazenar até 3 Volumes de itens. O valor de Volume apresentado é para quando estão sendo usados por uma montaria; se carregados por você, contam como Volume 1.",
        ),
        construir_equipamento_aventura(
            "Algemas ruins",
            "3 pp",
            "—",
            "2",
            "Prende alguém disposto ou rendido (10 a 30 segundos). Pernas presas: -4,5 m de penalidade de circunstância na Velocidade; pulsos presos: teste simples CD 5 para ações de Manuseio. Libertar requer 2 sucessos de Ladroagem CD 17.",
            item_base="Algemas",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Algemas simples",
            "3 po",
            "—",
            "2",
            "Como algemas ruins, mas libertar requer 3 sucessos de Ladroagem CD 22.",
            item_base="Algemas",
            nivel=1,
        ),
        construir_equipamento_aventura(
            "Algemas medianas",
            "20 po",
            "—",
            "2",
            "Como algemas ruins, mas libertar requer 4 sucessos de Ladroagem CD 27.",
            item_base="Algemas",
            nivel=3,
        ),
        construir_equipamento_aventura(
            "Algemas boas",
            "250 po",
            "—",
            "2",
            "Como algemas ruins, mas libertar requer 5 sucessos de Ladroagem CD 32.",
            item_base="Algemas",
            nivel=9,
        ),
        construir_equipamento_aventura(
            "Algemas superiores",
            "5.000 po",
            "—",
            "2",
            "Como algemas ruins, mas libertar requer 6 sucessos de Ladroagem CD 42.",
            item_base="Algemas",
            nivel=17,
        ),
        construir_equipamento_aventura(
            "Algibeira", "4 pc", "—", "—", "Uma algibeira comporta até quatro itens de Volume leve."
        ),
        construir_equipamento_aventura(
            "Ampulheta", "3 po", "L", "1", "Instrumento para medir passagens curtas de tempo."
        ),
        construir_equipamento_aventura(
            "Apito de advertência",
            "8 pc",
            "—",
            "1",
            "Também chamado de Apito de Aviso no texto descritivo. Quando soprado, pode ser ouvido claramente a até 750 metros em terreno aberto.",
        ),
        construir_equipamento_aventura(
            "Arpéu",
            "1 pp",
            "L",
            "1",
            "Você pode arremessar um arpéu com uma corda amarrada a ele para facilitar a escalada (rolagem de ataque com traço secreto contra CD, normalmente pelo menos CD 20).",
        ),
        construir_equipamento_aventura(
            "Azevinho e visco",
            "0",
            "—",
            "1",
            "Foco primal para conjuradores primais, como druidas; deve ser empunhado em uma mão para ser usado.",
        ),
        construir_equipamento_aventura(
            "Bainha",
            "1 pc",
            "—",
            "—",
            "Uma bainha ou estojo permite que você carregue facilmente uma arma consigo.",
        ),
        construir_equipamento_aventura(
            "Balança de mercador",
            "2 pp",
            "L",
            "2",
            "Balança portátil usada para pesar moedas, gemas e mercadorias.",
        ),
        construir_equipamento_aventura(
            "Bandoleira",
            "1 pp",
            "—",
            "—",
            "Comporta até oito itens de Volume leve com fácil acesso. Se carregada/arrumada em vez de usada cruzada no peito, o Volume é leve. Pode ser dedicada a um conjunto de ferramentas (como curandeiro) para sacá-las como parte da ação que necessita delas.",
        ),
        construir_equipamento_aventura(
            "Baú", "6 pp", "2", "2", "Um baú de madeira comporta até 8 Volumes de itens."
        ),
        construir_equipamento_aventura(
            "Bolsa de componentes materiais",
            "5 pp",
            "L",
            "1",
            "Contém componentes materiais para magias que os requerem; reabastecível durante suas preparações diárias.",
        ),
        construir_equipamento_aventura(
            "Bússola",
            "1 po",
            "—",
            "1",
            "Ajuda a Intuir Direção ou a se orientar em locais com campos magnéticos uniformes. Sem uma bússola, você sofre -2 de penalidade de item nestes testes.",
            item_base="Bússola",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Bússola com lente",
            "20 po",
            "—",
            "1",
            "Uma bússola com lente para leitura da escala concede +1 de bônus de item em testes para Intuir Direção ou se orientar.",
            item_base="Bússola",
            nivel=3,
            bonus_item="+1 em Intuir Direção / orientar-se",
        ),
        construir_equipamento_aventura(
            "Caneca", "1 pc", "—", "1", "Recipiente simples para bebidas."
        ),
        construir_equipamento_aventura(
            "Cantil",
            "5 pc",
            "L",
            "1",
            "Esteja cheio ou vazio, possui Volume leve e comporta até 1 dia de água para uma criatura Pequena ou Média.",
        ),
        construir_equipamento_aventura(
            "Conjunto de escrita",
            "1 po",
            "L",
            "2",
            "Inclui artigos de papelaria (papéis e pergaminhos), tinta, pena ou caneta tinteiro e cera para selar um selo simples.",
            item_base="Conjunto de escrita",
        ),
        construir_equipamento_aventura(
            "Papel e tinta extra",
            "1 pp",
            "—",
            "—",
            "Suprimentos de reposição para reabastecer um conjunto de escrita.",
            item_base="Conjunto de escrita",
        ),
        construir_equipamento_aventura(
            "Corda", "5 pp", "L", "2", "Corda resistente útil para escalada, amarrações e exploração."
        ),
        construir_equipamento_aventura(
            "Corrente (3 metros)", "4 po", "1", "2", "Corrente metálica de 3 metros de comprimento."
        ),
        construir_equipamento_aventura(
            "Escada (3 metros)", "3 pc", "3", "2", "Escada portátil de madeira com 3 metros."
        ),
        construir_equipamento_aventura(
            "Espelho", "1 po", "—", "1", "Espelho de mão polido."
        ),
        construir_equipamento_aventura(
            "Esteira de dormir", "1 pc", "L", "—", "Esteira enrolável para acampamento."
        ),
        construir_equipamento_aventura(
            "Estrepes",
            "3 pp",
            "L",
            "1",
            "Espalhados em um quadrado vazio adjacente com ação de Interagir. Primeira criatura que entrar deve passar em Acrobatismo CD 14 ou sofre 1d4 perfurante e 1 de dano persistente de sangramento (e -1,5 m de Velocidade enquanto sangrar). Podem ser recuperados se nenhuma criatura sofrer dano.",
        ),
        construir_equipamento_aventura(
            "Fechadura ruim",
            "2 pp",
            "—",
            "2",
            "Abrir requer dois testes bem-sucedidos de Ladroagem CD 15.",
            item_base="Fechadura",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Fechadura simples",
            "2 po",
            "—",
            "2",
            "Abrir requer três testes bem-sucedidos de Ladroagem CD 20.",
            item_base="Fechadura",
            nivel=1,
        ),
        construir_equipamento_aventura(
            "Fechadura mediana",
            "15 po",
            "—",
            "2",
            "Abrir requer quatro sucessos de Ladroagem contra CD 25.",
            item_base="Fechadura",
            nivel=3,
        ),
        construir_equipamento_aventura(
            "Fechadura boa",
            "200 po",
            "—",
            "2",
            "Abrir requer cinco sucessos de Ladroagem contra CD 30.",
            item_base="Fechadura",
            nivel=9,
        ),
        construir_equipamento_aventura(
            "Fechadura superior",
            "4.500 po",
            "—",
            "2",
            "Abrir requer seis sucessos de Ladroagem contra CD 40.",
            item_base="Fechadura",
            nivel=17,
        ),
        construir_equipamento_aventura(
            "Ferramenta longa",
            "1 po",
            "1",
            "2",
            "Ferramenta manual básica longa (como enxada, marreta ou pá). Pode ser usada como arma improvisada causando 1d6 de dano.",
            item_base="Ferramenta",
        ),
        construir_equipamento_aventura(
            "Ferramenta curta",
            "4 pp",
            "L",
            "1 ou 2",
            "Ferramenta manual básica curta (como broca, espátula ou gancho de gelo). Pode ser usada como arma improvisada causando 1d4 de dano.",
            item_base="Ferramenta",
        ),
        construir_equipamento_aventura(
            "Ferramentas de alquimista",
            "3 po",
            "1",
            "2",
            "Coleção móvel de frascos e químicos para tarefas alquímicas simples.",
        ),
        construir_equipamento_aventura(
            "Ferramentas de artesão",
            "4 po",
            "2",
            "2",
            "Necessárias para criar itens com a perícia Manufatura a partir de matéria-prima. Conjuntos diferentes são necessários para trabalhos diferentes.",
            item_base="Ferramentas de artesão",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Ferramentas de artesão autênticas",
            "50 po",
            "2",
            "2",
            "Ferramentas de artesão que fornecem +1 de bônus de item no teste de Manufatura.",
            item_base="Ferramentas de artesão",
            nivel=3,
            bonus_item="+1 em Manufatura",
        ),
        construir_equipamento_aventura(
            "Ferramentas de curandeiro",
            "5 po",
            "1",
            "2",
            "Necessárias para testes de Medicina para Administrar Primeiros Socorros, Tratar Doenças, Tratar Ferimentos ou Tratar Venenos.",
            item_base="Ferramentas de curandeiro",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Ferramentas de curandeiro expandidas",
            "50 po",
            "1",
            "2",
            "Concedem +1 de bônus de item para testes de Medicina com ferramentas de curandeiro.",
            item_base="Ferramentas de curandeiro",
            nivel=3,
            bonus_item="+1 em Medicina (com ferramentas de curandeiro)",
        ),
        construir_equipamento_aventura(
            "Ferramentas de ladrão",
            "3 po",
            "L",
            "2",
            "Necessárias para Abrir Fechaduras ou Desabilitar Dispositivos com Ladroagem.",
            item_base="Ferramentas de ladrão",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Gazuas de reposição",
            "3 pp",
            "—",
            "—",
            "Substituem ferramentas de ladrão quebradas sem exigir a ação Reparar.",
            item_base="Ferramentas de ladrão",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Ferramentas de ladrão infiltrador",
            "50 po",
            "L",
            "2",
            "Concedem +1 de bônus de item aos testes de Ladroagem para Abrir Fechaduras ou Desabilitar Dispositivos.",
            item_base="Ferramentas de ladrão",
            nivel=3,
            bonus_item="+1 em Ladroagem (Abrir Fechaduras / Desabilitar Dispositivos)",
        ),
        construir_equipamento_aventura(
            "Gazuas de ladrão infiltrador",
            "3 po",
            "—",
            "—",
            "Gazuas de reposição para ferramentas de ladrão infiltrador.",
            item_base="Ferramentas de ladrão",
            nivel=3,
        ),
        construir_equipamento_aventura(
            "Frasco", "5 pc", "—", "1", "Frasco de vidro simples que armazena até 30 ml de líquido."
        ),
        construir_equipamento_aventura(
            "Giz (10)",
            "1 pc",
            "—",
            "1",
            "Dez pedaços de giz para marcações.",
            quantidade_pacote=10,
        ),
        construir_equipamento_aventura(
            "Grimório (em branco)",
            "1 po",
            "L",
            "1",
            "Contém o conhecimento escrito necessário para aprender e preparar magias; cada grimório pode conter até 100 magias.",
        ),
        construir_equipamento_aventura(
            "Instrumento musical portátil",
            "8 pp",
            "1",
            "2",
            "Alaúde, flauta, gaita-de-foles, tambor pequeno, violino ou instrumento de mão similar.",
            item_base="Instrumento musical",
        ),
        construir_equipamento_aventura(
            "Instrumento musical portátil de virtuoso",
            "50 po",
            "1",
            "2",
            "Instrumento musical portátil de qualidade superior que concede +1 de bônus de item em testes de Performance usando este instrumento.",
            item_base="Instrumento musical",
            bonus_item="+1 em Performance",
        ),
        construir_equipamento_aventura(
            "Instrumento musical pesado",
            "2 po",
            "16",
            "2",
            "Instrumento pesado como conjunto inteiro de sinos, tambor grande ou instrumento com teclado, geralmente estacionário enquanto tocado.",
            item_base="Instrumento musical",
        ),
        construir_equipamento_aventura(
            "Instrumento musical pesado de virtuoso",
            "100 po",
            "16",
            "2",
            "Instrumento musical pesado de qualidade superior que concede +1 de bônus de item em testes de Performance usando este instrumento.",
            item_base="Instrumento musical",
            bonus_item="+1 em Performance",
        ),
        construir_equipamento_aventura(
            "Kit de arapuca",
            "5 po",
            "2",
            "2",
            "Contém ferramentas e materiais para Manufaturar arapucas usando a perícia Manufatura.",
            item_base="Kit de arapuca",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Kit de arapuca especialista",
            "55 po",
            "2",
            "2",
            "Concede +1 de bônus de item no teste de Manufatura para criar arapucas.",
            item_base="Kit de arapuca",
            nivel=3,
            bonus_item="+1 em Manufatura (arapucas)",
        ),
        construir_equipamento_aventura(
            "Kit de disfarce",
            "2 po",
            "L",
            "2",
            "Pequena caixa de madeira com cosméticos, pelos faciais falsos, cola cosmética e perucas simples, normalmente necessário para Personificar alguém com Dissimulação.",
            item_base="Kit de disfarce",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Cosméticos de reposição",
            "1 pp",
            "—",
            "—",
            "Reabastece o suprimento de um kit de disfarce comum.",
            item_base="Kit de disfarce",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Kit de disfarce de elite",
            "40 po",
            "L",
            "2",
            "Concede +1 de bônus de item nos testes de Dissimulação para Personificar alguém.",
            item_base="Kit de disfarce",
            nivel=3,
            bonus_item="+1 em Dissimulação (Personificar)",
        ),
        construir_equipamento_aventura(
            "Cosméticos elite",
            "5 pp",
            "—",
            "—",
            "Reabastece o suprimento de um kit de disfarce de elite.",
            item_base="Kit de disfarce",
            nivel=3,
        ),
        construir_equipamento_aventura(
            "Kit de escalada",
            "5 pp",
            "1",
            "2",
            "Inclui 15 metros de corda, roldanas, uma dúzia de pitões, um martelo, um gancho de escalada e grampos de ferro. Permite prender-se na parede (metade da Velocidade, mín. 1,5 m) e fazer teste simples CD 5 para evitar queda em falha crítica.",
            item_base="Kit de escalada",
        ),
        construir_equipamento_aventura(
            "Kit de escalada extrema",
            "40 po",
            "1",
            "2",
            "Como kit de escalada e concede +1 de bônus de item em testes de Atletismo para Escalar.",
            item_base="Kit de escalada",
            bonus_item="+1 em Atletismo (Escalar)",
        ),
        construir_equipamento_aventura(
            "Kit de montaria",
            "4 po",
            "1",
            "—",
            "Inclui arreio, estribo, rédea e sela para vestir um animal de montaria. O Volume é 1 quando vestido pela criatura; se carregado, aumenta para 2.",
        ),
        construir_equipamento_aventura(
            "Kit de pesca",
            "8 pp",
            "1",
            "2",
            "Inclui vara de pescar desmontável, anzóis, linha, iscas e rede de pesca.",
            item_base="Kit de pesca",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Kit de pesca profissional",
            "20 po",
            "1",
            "2",
            "Concede +1 de bônus de item em testes para pescar.",
            item_base="Kit de pesca",
            nivel=3,
            bonus_item="+1 em testes para pescar",
        ),
        construir_equipamento_aventura(
            "Kit de reparo",
            "2 po",
            "1",
            "2",
            "Contém amolador, bigorna portátil, ferramentas de carpintaria, tenazes e óleos; usado para Reparar itens com Manufatura.",
            item_base="Kit de reparo",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Kit de reparo soberbo",
            "25 po",
            "1",
            "2",
            "Concede +1 de bônus de item em testes de Manufatura para Reparar.",
            item_base="Kit de reparo",
            nivel=3,
            bonus_item="+1 em Manufatura (Reparar)",
        ),
        construir_equipamento_aventura(
            "Laboratório de alquimista",
            "5 po",
            "6",
            "2",
            "Necessário para Manufaturar itens alquímicos durante o recesso.",
            item_base="Laboratório de alquimista",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Laboratório de alquimista expandido",
            "55 po",
            "6",
            "2",
            "Fornece +1 de bônus de item em testes de Manufatura para criar itens alquímicos.",
            item_base="Laboratório de alquimista",
            nivel=3,
            bonus_item="+1 em Manufatura (itens alquímicos)",
        ),
        construir_equipamento_aventura(
            "Lanterna coberta",
            "7 pp",
            "L",
            "1",
            "Requer 500 ml de óleo para funcionar por 6 horas. Emana luz brilhante em raio de 9 metros (e luz fraca por mais 9 metros) com persianas que podem ser fechadas/abertas com uma ação de Interagir.",
            item_base="Lanterna",
        ),
        construir_equipamento_aventura(
            "Lanterna focada",
            "1 po",
            "1",
            "1",
            "Requer 500 ml de óleo para funcionar por 6 horas. Emite luz brilhante em um cone de 18 metros (e luz fraca por mais 18 metros).",
            item_base="Lanterna",
        ),
        construir_equipamento_aventura(
            "Livro básico de manufatura",
            "1 pp",
            "L",
            "2",
            "Contém as fórmulas (página 293) para Manufaturar todos os itens comuns de nível 0 do Capítulo 6.",
        ),
        construir_equipamento_aventura(
            "Livro de fórmulas (em branco)",
            "1 po",
            "L",
            "1",
            "Guarda até 100 fórmulas diferentes para criar itens com Manufaturar; alquimistas normalmente recebem um gratuitamente.",
        ),
        construir_equipamento_aventura(
            "Luneta",
            "20 po",
            "L",
            "2",
            "Permite que você veja oito vezes mais distante do que o normal.",
            item_base="Luneta",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Luneta excelente",
            "80 po",
            "L",
            "2",
            "Permite ver oito vezes mais distante e concede +1 de bônus de item em testes de Percepção para notar detalhes à distância.",
            item_base="Luneta",
            nivel=4,
            bonus_item="+1 em Percepção (detalhes à distância)",
        ),
        construir_equipamento_aventura(
            "Lupa",
            "40 po",
            "—",
            "1",
            "Lentes de mão de qualidade que concedem +1 de bônus de item em testes de Percepção para notar detalhes minuciosos em documentos, tecidos e afins.",
            nivel=3,
            bonus_item="+1 em Percepção (detalhes minuciosos)",
        ),
        construir_equipamento_aventura(
            "Martelo",
            "1 pp",
            "L",
            "1",
            "Martelo utilitário usado para fixar pitões ou trabalhos gerais.",
        ),
        construir_equipamento_aventura(
            "Mochila",
            "1 pp",
            "—",
            "—",
            "Comporta até 4 Volumes de itens; os primeiros 2 Volumes em sua mochila não contam contra seu limite de Volume. Se carregada em vez de usada nas costas, o Volume dela é leve.",
        ),
        construir_equipamento_aventura(
            "Óleo (meio litro)",
            "1 pc",
            "—",
            "2",
            "Abastece lanternas (500 ml duram 6 horas) ou pode ser incendiado (1 ação Interagir) e arremessado (1 ação ataque à distância): em acerto e teste simples CD 10, causa 1d6 de dano de fogo.",
        ),
        construir_equipamento_aventura(
            "Pé-de-cabra",
            "5 pp",
            "L",
            "2",
            "Permite alavancagem para Forçar um objeto com Atletismo; sem um pé-de-cabra, forçar algo a abrir sofre -2 de penalidade de item.",
            item_base="Pé-de-cabra",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Pé-de-cabra alavancado",
            "20 po",
            "L",
            "2",
            "Concede +1 de bônus de item em testes de Atletismo para Forçar qualquer coisa que possa ser forçada a abrir.",
            item_base="Pé-de-cabra",
            nivel=3,
            bonus_item="+1 em Atletismo (Forçar)",
        ),
        construir_equipamento_aventura(
            "Pederneira e isqueiro",
            "5 pc",
            "—",
            "2",
            "Usados para criar fogo fora de combate; acender uma chama requer pelo menos 3 ações.",
        ),
        construir_equipamento_aventura(
            "Pitão",
            "1 pc",
            "—",
            "1",
            "Pequeno cravo usado como âncora para cordas durante escaladas (requer martelo).",
        ),
        construir_equipamento_aventura(
            "Porta-pergaminho",
            "1 pp",
            "—",
            "2",
            "Armazena pergaminhos, mapas e outros documentos em rolos para transporte seguro.",
        ),
        construir_equipamento_aventura(
            "Rações (1 semana)",
            "4 pp",
            "L",
            "1",
            "Suprimento de comida de viagem para 1 semana.",
        ),
        construir_equipamento_aventura(
            "Roupas de explorador",
            "1 pp",
            "L",
            "—",
            "Roupas resistentes que podem ser reforçadas com runas para proteção usando proficiência em defesa sem armadura (Limite de Des +5, Confortável).",
            item_base="Roupas",
        ),
        construir_equipamento_aventura(
            "Roupas finas",
            "2 po",
            "L",
            "—",
            "Roupas apropriadas para um nobre ou rei, feitas de tecidos caros e padrões intricados.",
            item_base="Roupas",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Roupas finas de alta moda",
            "55 po",
            "L",
            "—",
            "Roupas finas de alta costura; concedem +1 de bônus de item em testes feitos para Impressionar nobres ou cidadãos de castas superiores.",
            item_base="Roupas",
            nivel=3,
            bonus_item="+1 para Impressionar nobres e castas superiores",
        ),
        construir_equipamento_aventura(
            "Roupas de inverno",
            "4 pp",
            "L",
            "—",
            "Permitem ignorar o dano ambiental de frio severo e reduzem o dano de frio extremo para frio severo.",
            item_base="Roupas",
        ),
        construir_equipamento_aventura(
            "Roupas ordinárias",
            "1 pp",
            "—",
            "—",
            "Roupas funcionais de costura básica (robes de monges, roupas de trabalho ou trajes de camponês).",
            item_base="Roupas",
        ),
        construir_equipamento_aventura(
            "Sabão", "2 pc", "—", "1", "Barra de sabão para higiene pessoal e limpeza."
        ),
        construir_equipamento_aventura(
            "Saco",
            "1 pp",
            "—",
            "2",
            "Comporta até 8 Volumes de itens. Contendo 2 Volumes ou menos pode ser usado no corpo preso em um cinto.",
        ),
        construir_equipamento_aventura(
            "Sacola (5)",
            "1 pc",
            "L",
            "1",
            "Cada sacola armazena até 2 Volumes de itens. O preço é para 5 sacolas; o Volume listado é por unidade (desprezível quando usada sobre o ombro, leve quando carregada/arrumada).",
            quantidade_pacote=5,
        ),
        construir_equipamento_aventura(
            "Símbolo religioso (madeira)",
            "1 pp",
            "L",
            "1",
            "Peça de madeira ornamentada com imagem de uma divindade; pode ser usada por conjuradores divinos (como clérigos) como foco divino quando empunhada em uma mão.",
            item_base="Símbolo religioso",
        ),
        construir_equipamento_aventura(
            "Símbolo religioso (prata)",
            "2 po",
            "L",
            "1",
            "Peça de prata ornamentada com imagem de uma divindade; foco divino quando empunhada em uma mão.",
            item_base="Símbolo religioso",
        ),
        construir_equipamento_aventura(
            "Tenda individual",
            "8 pp",
            "L",
            "2",
            "Abrigo portátil para 1 pessoa.",
            item_base="Tenda",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Tenda quatro pessoas",
            "5 po",
            "1",
            "2",
            "Abrigo portátil para até 4 pessoas.",
            item_base="Tenda",
            nivel=0,
        ),
        construir_equipamento_aventura(
            "Tenda pavilhão",
            "40 po",
            "12",
            "2",
            "Grande tenda estilo pavilhão.",
            item_base="Tenda",
            nivel=2,
        ),
        construir_equipamento_aventura(
            "Texto religioso",
            "1 po",
            "L",
            "1",
            "Manuscrito com escrituras de uma religião em particular; usado como foco divino quando empunhado em uma mão.",
        ),
        construir_equipamento_aventura(
            "Tocha",
            "1 pc",
            "L",
            "1",
            "Emana luz brilhante em raio de 6 metros (e luz fraca por mais 6 metros). Pode ser usada como arma improvisada causando 1d4 contundente mais 1 de dano de fogo.",
        ),
        construir_equipamento_aventura(
            "Utensílios de cozinha",
            "1 po",
            "2",
            "2",
            "Panelas, frigideiras e utensílios básicos para preparar refeições em viagem.",
        ),
        construir_equipamento_aventura(
            "Vara de 3 metros",
            "1 pc",
            "1",
            "2",
            "Permite usar a ação Buscar para procurar em um quadrado a até 3 metros de distância. Não é resistente o suficiente para ser usada como arma.",
        ),
        construir_equipamento_aventura(
            "Vela (10)",
            "1 pc",
            "—",
            "1",
            "Uma vela acesa emite luz fraca em um raio de 3 metros. Preço para pacote com 10 velas.",
            quantidade_pacote=10,
        ),
    ]

    incomuns = [
        construir_equipamento_aventura(
            "Diário acadêmico",
            "6 po",
            "L",
            "1",
            "Livreto sobre um tópico específico. Consultar por 1 minuto antes de um teste de perícia para Recordar Conhecimento sobre o assunto concede +1 de bônus de item no teste.",
            raridade="Incomum",
            nivel=3,
            bonus_item="+1 em Recordar Conhecimento (tópico específico)",
        ),
        construir_equipamento_aventura(
            "Compêndio acadêmico",
            "30 po",
            "L",
            "2",
            "Contém vários diários e concede +1 de bônus de item em testes para Recordar Conhecimento sobre um assunto mais amplo (como todos os mortos-vivos ou uma cidade inteira).",
            raridade="Incomum",
            nivel=3,
            bonus_item="+1 em Recordar Conhecimento (tópico amplo)",
        ),
        construir_equipamento_aventura(
            "Mapa de pesquisa",
            "10 po",
            "L",
            "1",
            "Detalha uma única localidade minuciosamente, concedendo +1 de bônus de item em testes de Sobrevivência e Recordar Conhecimento relacionados à localidade.",
            raridade="Incomum",
            nivel=3,
            bonus_item="+1 em Sobrevivência e Recordar Conhecimento (localidade)",
        ),
        construir_equipamento_aventura(
            "Atlas de pesquisa",
            "50 po",
            "L",
            "2",
            "Reúne vários mapas de pesquisa da mesma qualidade envolvendo tópicos ou regiões similares.",
            raridade="Incomum",
            nivel=3,
            bonus_item="+1 em Sobrevivência e Recordar Conhecimento (regiões do atlas)",
        ),
    ]

    return {"comuns": comuns, "incomuns": incomuns}


def obter_kits_de_classe() -> list[dict[str, Any]]:
    """Retorna os 12 kits iniciais de classe da página 289."""
    return [
        construir_kit_classe(
            classe="Alquimista",
            preco="9 po, 6 pp",
            volume_texto="4 mais 7 leves",
            dinheiro_restante="5 po, 4 pp",
            armadura="couro batido",
            armas=["adaga", "funda (com 20 balas de funda)"],
            equipamentos=[
                "kit de aventureiro",
                "bainha",
                "bandoleira",
                "2 conjuntos de estrepes",
                "ferramentas de alquimista",
                "livro básico de manufatura",
            ],
            opcoes=["kit de reparo (2 po)"],
        ),
        construir_kit_classe(
            classe="Bárbaro",
            preco="4 po, 1 pp",
            volume_texto="3 mais 5 leves",
            dinheiro_restante="10 po, 9 pp",
            armadura="gibão de peles",
            armas=["4 azagaias"],
            equipamentos=["kit de aventureiro", "arpéu", "2 bainhas"],
            opcoes=[
                "clava pesada (1 po)",
                "machado de batalha e escudo de aço (3 po)",
                "machado longo (2 po)",
                "montante (2 po)",
            ],
        ),
        construir_kit_classe(
            classe="Bardo",
            preco="6 po, 6 pp",
            volume_texto="4 mais 3 leves",
            dinheiro_restante="8 po, 4 pp",
            armadura="couro batido",
            armas=["adaga", "funda (com 20 balas de funda)", "rapieira"],
            equipamentos=[
                "kit de aventureiro",
                "bainha",
                "bandoleira",
                "instrumento musical portátil",
            ],
            opcoes=[],
        ),
        construir_kit_classe(
            classe="Campeão",
            preco="3 po, 9 pp",
            volume_texto="3 mais 7 leves",
            dinheiro_restante="11 po, 1 pp",
            armadura="gibão de peles",
            armas=["adaga", "4 azagaias"],
            equipamentos=["kit de aventureiro", "arpéu", "bainha", "pé-de-cabra"],
            opcoes=[
                "arma predileta de sua divindade (veja a seção divindades nas páginas 437 a 441; utilize o Preço listado neste capítulo)"
            ],
        ),
        construir_kit_classe(
            classe="Clérigo",
            preco="1 po, 5 pp",
            volume_texto="1 mais 3 leves",
            dinheiro_restante="13 po, 5 pp",
            armadura=None,
            armas=[],
            equipamentos=[
                "kit de aventureiro",
                "bandoleira",
                "2 conjuntos de estrepes",
                "símbolo religioso (madeira)",
            ],
            opcoes=[
                "arma predileta de sua divindade (veja a seção divindades nas páginas 437 a 441; utilize o Preço listado neste capítulo)",
                "gibão de peles (2 po)",
            ],
        ),
        construir_kit_classe(
            classe="Druida",
            preco="3 po, 7 pp",
            volume_texto="4 mais 4 leves",
            dinheiro_restante="11 po, 3 pp",
            armadura="couro",
            armas=["4 azagaias", "lança longa"],
            equipamentos=["kit de aventureiro", "azevinho e visco", "bandoleira"],
            opcoes=["ferramentas de curandeiro (5 po)"],
        ),
        construir_kit_classe(
            classe="Feiticeiro",
            preco="1 po, 6 pp",
            volume_texto="1 mais 6 leves",
            dinheiro_restante="12 po, 9 pp",
            armadura=None,
            armas=["adaga", "funda (com 20 balas de funda)"],
            equipamentos=[
                "kit de aventureiro",
                "bainha",
                "bandoleira",
                "2 conjuntos de estrepes",
            ],
            opcoes=[],
            nota=(
                "Valor 'Dinheiro Restante: 12 po, 9 pp' mantido exatamente conforme impresso na "
                "página 289 de ref/Tools.pdf (embora 15 po - 1 po 6 pp resulte em 13 po 4 pp)."
            ),
        ),
        construir_kit_classe(
            classe="Guerreiro",
            preco="3 po",
            volume_texto="3 mais 2 leves",
            dinheiro_restante="12 po",
            armadura="gibão de peles",
            armas=["adaga"],
            equipamentos=["kit de aventureiro", "arpéu", "bainha"],
            opcoes=[
                "arco longo (com 20 flechas) (6 po, 2 pp)",
                "espada longa e escudo de aço (3 po)",
                "montante (2 po)",
            ],
        ),
        construir_kit_classe(
            classe="Ladino",
            preco="5 po, 4 pp",
            volume_texto="4 mais 1 leves",
            dinheiro_restante="9 po, 6 pp",
            armadura="couro",
            armas=["adaga", "rapieira"],
            equipamentos=["kit de aventureiro", "bainha", "kit de escalada"],
            opcoes=["ferramentas de ladrão (3 po)"],
        ),
        construir_kit_classe(
            classe="Mago",
            preco="2 po, 2 pp",
            volume_texto="2 mais 2 leves",
            dinheiro_restante="12 po, 8 pp",
            armadura=None,
            armas=["cajado"],
            equipamentos=[
                "kit de aventureiro",
                "bolsa de componentes materiais",
                "conjunto de escrita",
            ],
            opcoes=["besta leve (com 20 virotes) (3 po, 2 pp)"],
        ),
        construir_kit_classe(
            classe="Monge",
            preco="4 po, 9 pp",
            volume_texto="5 mais 2 leves",
            dinheiro_restante="10 po, 1 pp",
            armadura=None,
            armas=["cajado", "lança longa"],
            equipamentos=[
                "kit de aventureiro",
                "arpéu",
                "bandoleira",
                "bastão de fumaça menor",
                "kit de escalada",
            ],
            opcoes=[],
        ),
        construir_kit_classe(
            classe="Patrulheiro",
            preco="9 po, 1 pp",
            volume_texto="4 mais 3 leves",
            dinheiro_restante="5 po, 9 pp",
            armadura="couro",
            armas=["adaga", "arco longo (com 20 flechas)"],
            equipamentos=["kit de aventureiro", "bainha"],
            opcoes=[],
        ),
    ]


def obter_equipamentos_alquimicos() -> dict[str, Any]:
    """Retorna os 12 itens da Tabela 6-11: Equipamentos Alquímicos."""
    bombas = [
        {
            "id": "bolsa_emaranhape_menor",
            "nome": "Bolsa emaranhapé menor",
            "categoria": "Bomba Alquímica",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 544,
            "dano_direto": None,
            "dano_persistente": None,
            "dano_respingo": None,
            "efeito_especial": "-3 metros de penalidade na Velocidade do alvo por 1 minuto; em sucesso crítico, alvo fica imobilizado até Escapar.",
            "descricao": "Esta bomba alquímica causa -3 metros de penalidade na Velocidade do alvo por 1 minuto. Além disso, no caso de um sucesso crítico em seu ataque, o alvo fica imobilizado até Escapar.",
        },
        {
            "id": "fogo_alquimico_menor",
            "nome": "Fogo alquímico menor",
            "categoria": "Bomba Alquímica",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 545,
            "dano_direto": "1d8 de fogo",
            "dano_persistente": "1 de fogo",
            "dano_respingo": "1 de fogo",
            "efeito_especial": None,
            "descricao": "Esta bomba alquímica causa 1d8 de dano de fogo, 1 de dano persistente de fogo e 1 de dano de fogo de respingo.",
        },
        {
            "id": "frasco_congelante_menor",
            "nome": "Frasco congelante menor",
            "categoria": "Bomba Alquímica",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 545,
            "dano_direto": "1d6 de frio",
            "dano_persistente": None,
            "dano_respingo": "1 de frio",
            "efeito_especial": "Impõe -1,5 metros de penalidade na Velocidade do alvo até o final do próximo turno dele.",
            "descricao": "Esta bomba alquímica causa 1d6 de dano de frio e 1 de dano de frio de respingo. Além disso, ela impõe -1,5 metros de penalidade na Velocidade do alvo até o final do próximo turno dele.",
        },
        {
            "id": "frasco_de_acido_menor",
            "nome": "Frasco de ácido menor",
            "categoria": "Bomba Alquímica",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 545,
            "dano_direto": "1 de ácido",
            "dano_persistente": "1d6 de ácido",
            "dano_respingo": "1 de ácido",
            "efeito_especial": None,
            "descricao": "Esta bomba alquímica causa 1 de dano de ácido, 1d6 de dano persistente de ácido e 1 de dano de ácido de respingo.",
        },
        {
            "id": "pedra_trovao_menor",
            "nome": "Pedra-trovão menor",
            "categoria": "Bomba Alquímica",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 545,
            "dano_direto": "1d4 sônico",
            "dano_persistente": None,
            "dano_respingo": "1 sônico",
            "efeito_especial": "Qualquer criatura a até 3 metros do alvo que falhar em salvamento de Fortitude CD 17 fica surda até o final do turno dela.",
            "descricao": "Esta bomba alquímica causa 1d4 de dano sônico e 1 de dano sônico de respingo. Além disso, qualquer criatura a até 3 metros do alvo que falhar em um salvamento de Fortitude CD 17 fica surda até o final do turno dela.",
        },
        {
            "id": "relampago_engarrafado_menor",
            "nome": "Relâmpago engarrafado menor",
            "categoria": "Bomba Alquímica",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 546,
            "dano_direto": "1d6 de eletricidade",
            "dano_persistente": None,
            "dano_respingo": "1 de eletricidade",
            "efeito_especial": "Deixa o alvo desprevenido até o início do seu próximo turno.",
            "descricao": "Esta bomba alquímica causa 1d6 de dano de eletricidade e 1 de dano de eletricidade de respingo. Além disso, ela deixa o alvo desprevenido até o início do seu próximo turno.",
        },
    ]

    elixires = [
        {
            "id": "antidoto_menor",
            "nome": "Antídoto menor",
            "categoria": "Elixir Alquímico",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 546,
            "descricao": "Ao beber um antídoto menor, você recebe +2 de bônus de item em salvamentos de Fortitude contra venenos durante 6 horas.",
        },
        {
            "id": "antipeste_menor",
            "nome": "Antipeste menor",
            "categoria": "Elixir Alquímico",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 546,
            "descricao": "Ao beber um antipeste menor, você recebe +2 de bônus de item em salvamentos de Fortitude contra doenças por 24 horas, incluindo salvamentos contra a progressão de doenças.",
        },
        {
            "id": "elixir_da_vida_minimo",
            "nome": "Elixir da vida mínimo",
            "categoria": "Elixir Alquímico",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 548,
            "descricao": "Restaura 1d6 Pontos de Vida e concede +1 de bônus de item em jogadas de salvamento contra doenças e venenos por 10 minutos.",
        },
    ]

    ferramentas = [
        {
            "id": "bastao_de_fumaca_menor",
            "nome": "Bastão de fumaça menor",
            "categoria": "Ferramenta Alquímica",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 550,
            "descricao": "Você cria uma cortina de fumaça com 1,5 metros de raio por 1 minuto.",
        },
        {
            "id": "bastao_solar",
            "nome": "Bastão solar",
            "categoria": "Ferramenta Alquímica",
            "preco": "3 po",
            "preco_pc": 300,
            "volume": "L",
            "volume_valor": 0.1,
            "pagina_referencia": 550,
            "descricao": "Você pode bater um bastão solar em uma superfície dura como uma ação de Interagir para fazê-lo emanar luz brilhante em 6 metros de raio (e luz fraca por mais 6 metros) durante 6 horas.",
        },
        {
            "id": "fosforo",
            "nome": "Fósforo",
            "categoria": "Ferramenta Alquímica",
            "preco": "2 pp",
            "preco_pc": 20,
            "volume": "—",
            "volume_valor": 0.0,
            "pagina_referencia": 550,
            "descricao": "Você pode usar um fósforo para acender algo inflamável com uma única ação de Interagir, mais rápido do que com pederneira e isqueiro.",
        },
    ]

    return {
        "observacao": "Descrições resumidas para itens comuns de 1º nível; descrições completas no Capítulo 11.",
        "bombas_alquimicas": bombas,
        "elixires_alquimicos": elixires,
        "ferramentas_alquimicas": ferramentas,
    }


def obter_equipamentos_magicos() -> dict[str, Any]:
    """Retorna os 5 itens da Tabela 6-12: Equipamentos Mágicos."""
    return {
        "observacao": "Descrições resumidas para itens comuns de 1º nível; descrições completas no Capítulo 11.",
        "consumiveis": [
            {
                "id": "agua_benta",
                "nome": "Água benta",
                "categoria": "Item Mágico Consumível",
                "preco": "3 po",
                "preco_pc": 300,
                "volume": "L",
                "volume_valor": 0.1,
                "pagina_referencia": 581,
                "descricao": "Você pode arremessar água benta como uma bomba, causando 1d6 de dano bondoso e 1 de dano bondoso de respingo a ínferos, mortos-vivos e outras criaturas vulneráveis a dano bondoso.",
            },
            {
                "id": "agua_profana",
                "nome": "Água profana",
                "categoria": "Item Mágico Consumível",
                "preco": "3 po",
                "preco_pc": 300,
                "volume": "L",
                "volume_valor": 0.1,
                "pagina_referencia": 581,
                "descricao": "Você pode arremessar água profana como uma bomba, causando 1d6 de dano maligno e 1 de dano maligno de respingo a celestiais e outras criaturas vulneráveis a dano maligno.",
            },
        ],
        "pocoes": [
            {
                "id": "pocao_de_cura_minima",
                "nome": "Poção de cura mínima",
                "categoria": "Poção",
                "preco": "4 po",
                "preco_pc": 400,
                "volume": "L",
                "volume_valor": 0.1,
                "pagina_referencia": 574,
                "descricao": "Você recupera 1d8 Pontos de Vida ao beber uma poção de cura mínima.",
            }
        ],
        "pergaminhos": [
            {
                "id": "pergaminho_magia_comum_1_nivel",
                "nome": "Pergaminho de uma magia comum de 1º nível",
                "categoria": "Pergaminho",
                "preco": "4 po",
                "preco_pc": 400,
                "volume": "L",
                "volume_valor": 0.1,
                "pagina_referencia": 573,
                "descricao": "Escritura mágica que contém a magia necessária para efetuar uma conjuração específica de 1º nível sem usar seus espaços de magia.",
            }
        ],
        "talismas": [
            {
                "id": "cristal_de_potencia",
                "nome": "Cristal de potência",
                "categoria": "Talismã",
                "preco": "4 po",
                "preco_pc": 400,
                "volume": "—",
                "volume_valor": 0.0,
                "pagina_referencia": 577,
                "descricao": "Quando afixar o cristal a uma arma e ativá-lo, o talismã empodera a arma pelo resto do turno, concedendo +1 de bônus de item em rolagens de ataque e um segundo dado de dano a ataques realizados com essa arma.",
            }
        ],
    }


def obter_formulas_servicos_animais_tamanhos() -> dict[str, Any]:
    """Retorna as Tabelas 6-13 a 6-20 (Fórmulas, Serviços, Conjuração, Custo de Vida, Animais e Tamanhos)."""
    formulas_raw = [
        (0, "5 pp"),
        (1, "1 po"),
        (2, "2 po"),
        (3, "3 po"),
        (4, "5 po"),
        (5, "8 po"),
        (6, "13 po"),
        (7, "18 po"),
        (8, "25 po"),
        (9, "35 po"),
        (10, "50 po"),
        (11, "70 po"),
        (12, "100 po"),
        (13, "150 po"),
        (14, "225 po"),
        (15, "325 po"),
        (16, "500 po"),
        (17, "750 po"),
        (18, "1.200 po"),
        (19, "2.000 po"),
        (20, "3.500 po"),
    ]

    tabela_6_13 = {
        "niveis": [
            {"nivel_item": nv, "preco": p, "preco_pc": parse_preco_pc(p)}
            for nv, p in formulas_raw
        ],
        "nota": (
            "Fórmulas para todos os itens comuns de nível 0 do Capítulo 6 podem ser compradas "
            "coletivamente por um livro básico de manufatura (1 pp). Copiar uma fórmula no livro "
            "de fórmulas leva 1 hora."
        ),
    }

    servicos_raw = [
        ("Bebidas", "Caneca de cerveja", "1 pc", "L", "1"),
        ("Bebidas", "Barril de cerveja", "2 pp", "2", "2"),
        ("Bebidas", "Pote de café ou chá", "2 pc", "L", "1"),
        ("Bebidas", "Garrafa de vinho", "1 pp", "L", "1"),
        ("Bebidas", "Garrafa de vinho fino", "1 po", "L", "1"),
        ("Trabalhador (1 dia)", "Desqualificado", "1 pp", "—", "—"),
        ("Trabalhador (1 dia)", "Qualificado", "5 pp", "—", "—"),
        ("Hospedagem (1 dia)", "Espaço no chão", "3 pc", "—", "—"),
        ("Hospedagem (1 dia)", "Cama (para 1)", "1 pp", "—", "—"),
        ("Hospedagem (1 dia)", "Quarto privado (para 2)", "8 pp", "—", "—"),
        ("Hospedagem (1 dia)", "Suíte extravagante (para 6)", "10 po", "—", "—"),
        ("Refeições", "Refeição ruim", "1 pc", "L", "2"),
        ("Refeições", "Refeição substancial", "3 pc", "L", "2"),
        ("Refeições", "Jantar chique", "1 po", "L", "2"),
        ("Estábulo (1 dia)", "Estábulo (1 dia)", "2 pc", "—", "—"),
        ("Pedágio", "Pedágio", "pelo menos 1 pc", "—", "—"),
        ("Transporte (a cada 7,5 km)", "Caravana", "3 pc", "—", "—"),
        ("Transporte (a cada 7,5 km)", "Carruagem", "2 pp", "—", "—"),
        ("Transporte (a cada 7,5 km)", "Balsa ou barco", "4 pc", "—", "—"),
        ("Transporte (a cada 7,5 km)", "Veleiro", "6 pc", "—", "—"),
    ]

    tabela_6_14 = [
        {
            "categoria": cat,
            "item": item,
            "preco": preco,
            "preco_pc": 1 if "pelo menos" in preco else parse_preco_pc(preco),
            "volume": vol,
            "volume_valor": parse_volume_valor(vol),
            "maos": maos,
        }
        for cat, item, preco, vol, maos in servicos_raw
    ]

    conjuracao_raw = [
        (1, "3 po"),
        (2, "7 po"),
        (3, "18 po"),
        (4, "40 po"),
        (5, "80 po"),
        (6, "160 po"),
        (7, "360 po"),
        (8, "720 po"),
        (9, "1.800 po"),
    ]

    tabela_6_15 = {
        "niveis": [
            {"nivel_magia": nv, "preco": p, "preco_pc": parse_preco_pc(p)}
            for nv, p in conjuracao_raw
        ],
        "observacoes": (
            "Mais qualquer custo requerido para conjurar a magia específica. Magias incomuns "
            "tipicamente custam pelo menos 100% a mais. Magias com execução maior que 1 minuto "
            "normalmente custam 25% a mais."
        ),
    }

    custo_vida_raw = [
        ("Subsistência", "4 pp", "2 po", "24 po"),
        ("Confortável", "1 po", "4 po", "52 po"),
        ("Bom", "30 po", "130 po", "1.600 po"),
        ("Extravagante", "100 po", "430 po", "5.200 po"),
    ]

    tabela_6_16 = {
        "padroes": [
            {
                "padrao": padrao,
                "semana": sem,
                "semana_pc": parse_preco_pc(sem),
                "mes": mes,
                "mes_pc": parse_preco_pc(mes),
                "ano": ano,
                "ano_pc": parse_preco_pc(ano),
            }
            for padrao, sem, mes, ano in custo_vida_raw
        ],
        "nota_subsistencia": "Você pode tentar Subsistir de graça utilizando Sobrevivência ou Sociedade (página 240).",
    }

    tabela_6_17 = {
        "itens": [
            {"categoria": "Cão", "animal": "Cão de guarda", "aluguel": "1 pc por dia", "aluguel_pc_dia": 1, "compra": "2 pp", "compra_pc": 20, "nivel": 0},
            {"categoria": "Cão", "animal": "Cão de montaria", "aluguel": "6 pc por dia", "aluguel_pc_dia": 6, "compra": "4 po", "compra_pc": 400, "nivel": 0},
            {"categoria": "Cavalo", "animal": "Cavalo de montaria", "aluguel": "1 pp por dia", "aluguel_pc_dia": 10, "compra": "8 po", "compra_pc": 800, "nivel": 0},
            {"categoria": "Cavalo", "animal": "Cavalo de guerra", "aluguel": "1 po por dia", "aluguel_pc_dia": 100, "compra": "30 po", "compra_pc": 3000, "nivel": 2},
            {"categoria": "Cavalo", "animal": "Animal de carga", "aluguel": "2 pc por dia", "aluguel_pc_dia": 2, "compra": "2 po", "compra_pc": 200, "nivel": 0},
            {"categoria": "Pônei", "animal": "Pônei de montaria", "aluguel": "8 pc por dia", "aluguel_pc_dia": 8, "compra": "7 po", "compra_pc": 700, "nivel": 0},
            {"categoria": "Pônei", "animal": "Pônei de guerra", "aluguel": "8 pp por dia", "aluguel_pc_dia": 80, "compra": "24 po", "compra_pc": 2400, "nivel": 2},
        ],
        "nota": "Aluguel pode exigir um depósito caução igual ao preço de compra. Animais não treinados para guerra ficam assustados 4 e fugindo em combate.",
    }

    tabela_6_18 = {
        "observacao": (
            "Todos os animais possuem proficiência treinado em armaduras de animal leves, e animais "
            "treinados para o combate são treinados em armaduras de animal pesadas. A coluna Força "
            "lista um modificador, e não um valor. Armaduras de animal não podem receber runas."
        ),
        "itens": [
            {
                "categoria": "Armadura Leve",
                "tamanho": "Pequena ou Média",
                "nivel": 0,
                "preco": "10 po",
                "preco_pc": 1000,
                "bonus_ca": 1,
                "limite_destreza": 5,
                "penalidade_testes": -1,
                "penalidade_velocidade_m": -1.5,
                "mod_forca_minimo": 3,
                "volume": "2",
                "volume_valor": 2.0,
            },
            {
                "categoria": "Armadura Leve",
                "tamanho": "Grande",
                "nivel": 0,
                "preco": "20 po",
                "preco_pc": 2000,
                "bonus_ca": 1,
                "limite_destreza": 5,
                "penalidade_testes": -1,
                "penalidade_velocidade_m": -1.5,
                "mod_forca_minimo": 3,
                "volume": "4",
                "volume_valor": 4.0,
            },
            {
                "categoria": "Armadura Pesada",
                "tamanho": "Pequena ou Média",
                "nivel": 2,
                "preco": "25 po",
                "preco_pc": 2500,
                "bonus_ca": 3,
                "limite_destreza": 3,
                "penalidade_testes": -3,
                "penalidade_velocidade_m": -3.0,
                "mod_forca_minimo": 5,
                "volume": "4",
                "volume_valor": 4.0,
            },
            {
                "categoria": "Armadura Pesada",
                "tamanho": "Grande",
                "nivel": 3,
                "preco": "50 po",
                "preco_pc": 5000,
                "bonus_ca": 3,
                "limite_destreza": 3,
                "penalidade_testes": -3,
                "penalidade_velocidade_m": -3.0,
                "mod_forca_minimo": 5,
                "volume": "8",
                "volume_valor": 8.0,
            },
        ],
    }

    tabela_6_19 = [
        {"tamanho": "Minúsculo", "limite_volume": "Metade", "trata_como_leve": "—", "trata_como_desprezivel": "Nenhum"},
        {"tamanho": "Pequeno ou Médio", "limite_volume": "Padrão", "trata_como_leve": "L", "trata_como_desprezivel": "—"},
        {"tamanho": "Grande", "limite_volume": "×2", "trata_como_leve": "1 Volume", "trata_como_desprezivel": "L"},
        {"tamanho": "Enorme", "limite_volume": "×4", "trata_como_leve": "2 Volumes", "trata_como_desprezivel": "1 Volume"},
        {"tamanho": "Imenso", "limite_volume": "×8", "trata_como_leve": "4 Volumes", "trata_como_desprezivel": "2 Volumes"},
    ]

    tabela_6_20 = {
        "linhas": [
            {"tamanho": "Minúsculo", "preco": "Padrão", "volume": "Metade*", "leve_se_torna": "—", "desprezivel_se_torna": "—"},
            {"tamanho": "Pequeno ou Médio", "preco": "Padrão", "volume": "Padrão", "leve_se_torna": "L", "desprezivel_se_torna": "—"},
            {"tamanho": "Grande", "preco": "×2", "volume": "×2", "leve_se_torna": "1 Volume", "desprezivel_se_torna": "L"},
            {"tamanho": "Enorme", "preco": "×4", "volume": "×4", "leve_se_torna": "2 Volumes", "desprezivel_se_torna": "1 Volume"},
            {"tamanho": "Imenso", "preco": "×8", "volume": "×8", "leve_se_torna": "4 Volumes", "desprezivel_se_torna": "2 Volumes"},
        ],
        "nota": "* Um item que teria seu Volume reduzido abaixo de 1 possui Volume leve.",
    }

    return {
        "tabela_6_13_formulas": tabela_6_13,
        "tabela_6_14_servicos_consumiveis": tabela_6_14,
        "tabela_6_15_servicos_conjuracao": tabela_6_15,
        "tabela_6_16_custo_de_vida": tabela_6_16,
        "tabela_6_17_animais": tabela_6_17,
        "tabela_6_18_armaduras_animal": tabela_6_18,
        "tabela_6_19_conversao_volumes": tabela_6_19,
        "tabela_6_20_itens_tamanhos_diferentes": tabela_6_20,
    }


def gerar_estrutura_completa() -> dict[str, Any]:
    """Constrói o dicionário completo de equipamentos para serialização JSON."""
    return {
        "fonte": {
            "arquivo": "ref/Tools.pdf",
            "titulo": "Capítulo 6: Equipamentos",
            "paginas": "271-295",
            "sistema": "Pathfinder 2ª Edição (Livro Básico)",
        },
        "regras_gerais": obter_regras_gerais(),
        "armaduras": obter_armaduras(),
        "escudos": obter_escudos(),
        "armas": obter_armas(),
        "equipamentos_aventura": obter_equipamentos_aventura(),
        "kits_de_classe": obter_kits_de_classe(),
        "equipamentos_alquimicos": obter_equipamentos_alquimicos(),
        "equipamentos_magicos": obter_equipamentos_magicos(),
        "formulas_servicos_animais_tamanhos": obter_formulas_servicos_animais_tamanhos(),
    }


def validar_dados(dados: dict[str, Any]) -> None:
    """Executa verificações de integridade e contagens exatas contra ref/Tools.pdf."""
    assert len(dados["armaduras"]["itens"]) == 13, "Esperado 13 entradas de armadura/sem armadura"
    assert len(dados["escudos"]["itens"]) == 4, "Esperado 4 escudos"
    assert len(dados["armas"]["tracos_arma"]) == 32, "Esperado 32 traços de arma"
    assert len(dados["armas"]["efeitos_especializacao_critico"]) == 15, "Esperado 15 grupos de crítico"
    assert len(dados["armas"]["ataques_desarmados"]) == 1, "Esperado 1 ataque desarmado"
    assert len(dados["armas"]["corpo_a_corpo"]) == 64, "Esperado 64 armas corpo a corpo"
    assert len(dados["armas"]["distancia"]) == 14, "Esperado 14 armas à distância"
    assert len(dados["armas"]["municoes"]) == 4, "Esperado 4 tipos de munição"
    assert len(dados["equipamentos_aventura"]["comuns"]) == 101, "Esperado 101 entradas comuns na Tabela 6-9"
    assert len(dados["equipamentos_aventura"]["incomuns"]) == 4, "Esperado 4 itens incomuns na Tabela 6-10"
    assert len(dados["kits_de_classe"]) == 12, "Esperado 12 kits de classe"

    alq = dados["equipamentos_alquimicos"]
    total_alq = (
        len(alq["bombas_alquimicas"])
        + len(alq["elixires_alquimicos"])
        + len(alq["ferramentas_alquimicas"])
    )
    assert total_alq == 12, "Esperado 12 itens alquímicos na Tabela 6-11"

    mag = dados["equipamentos_magicos"]
    total_mag = (
        len(mag["consumiveis"])
        + len(mag["pocoes"])
        + len(mag["pergaminhos"])
        + len(mag["talismas"])
    )
    assert total_mag == 5, "Esperado 5 itens mágicos na Tabela 6-12"

    fsat = dados["formulas_servicos_animais_tamanhos"]
    assert len(fsat["tabela_6_13_formulas"]["niveis"]) == 21
    assert len(fsat["tabela_6_14_servicos_consumiveis"]) == 20
    assert len(fsat["tabela_6_15_servicos_conjuracao"]["niveis"]) == 9
    assert len(fsat["tabela_6_16_custo_de_vida"]["padroes"]) == 4
    assert len(fsat["tabela_6_17_animais"]["itens"]) == 7
    assert len(fsat["tabela_6_18_armaduras_animal"]["itens"]) == 4
    assert len(fsat["tabela_6_19_conversao_volumes"]) == 5
    assert len(fsat["tabela_6_20_itens_tamanhos_diferentes"]["linhas"]) == 5

    # Valida que todos os itens tabulados têm volume_valor float e preco_pc int ou None
    colecoes_itens = [
        dados["armaduras"]["itens"],
        dados["escudos"]["itens"],
        dados["armas"]["ataques_desarmados"],
        dados["armas"]["corpo_a_corpo"],
        dados["armas"]["distancia"],
        dados["armas"]["municoes"],
        dados["equipamentos_aventura"]["comuns"],
        dados["equipamentos_aventura"]["incomuns"],
        alq["bombas_alquimicas"],
        alq["elixires_alquimicos"],
        alq["ferramentas_alquimicas"],
        mag["consumiveis"],
        mag["pocoes"],
        mag["pergaminhos"],
        mag["talismas"],
    ]
    for col in colecoes_itens:
        ids = [item["id"] for item in col]
        assert len(ids) == len(set(ids)), f"IDs duplicados encontrados: {ids}"
        for item in col:
            assert isinstance(item["volume_valor"], float), f"Volume inválido em {item['nome']}"
            assert item["preco_pc"] is None or isinstance(
                item["preco_pc"], int
            ), f"preco_pc inválido em {item['nome']}"


def main() -> None:
    """Gera dados/equipamentos.json, recarrega do disco e valida."""
    dados = gerar_estrutura_completa()
    validar_dados(dados)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    carregado = json.loads(CAMINHO_SAIDA.read_text(encoding="utf-8"))
    validar_dados(carregado)
    print(f"Arquivo gerado e validado com sucesso: {CAMINHO_SAIDA}")
    print(
        f"Resumo: {len(carregado['armaduras']['itens'])} armaduras, "
        f"{len(carregado['escudos']['itens'])} escudos, "
        f"{len(carregado['armas']['corpo_a_corpo'])} armas corpo a corpo, "
        f"{len(carregado['armas']['distancia'])} armas à distância, "
        f"{len(carregado['equipamentos_aventura']['comuns'])} equipamentos comuns, "
        f"{len(carregado['equipamentos_aventura']['incomuns'])} equipamentos incomuns, "
        f"{len(carregado['kits_de_classe'])} kits de classe."
    )


if __name__ == "__main__":
    main()
