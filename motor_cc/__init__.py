"""Motor de regras de Castles & Crusades (1ª Edição Brasileira)."""

from motor_cc.atributos import METODOS_GERACAO, rolar_atributos
from motor_cc.combate import REGRAS_PV
from motor_cc.gerador import gerar_ficha_cc, obter_opcoes_criacao

__all__ = [
    "METODOS_GERACAO",
    "REGRAS_PV",
    "gerar_ficha_cc",
    "obter_opcoes_criacao",
    "rolar_atributos",
]
