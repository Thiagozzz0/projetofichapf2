"""Pacote `motor` — Motor procedural de geração de fichas Pathfinder 2E."""

from .dados import BaseDados, carregar_dados
from .exportacao import exportar_ficha_docx, exportar_ficha_txt, nome_arquivo_seguro
from .gerador import (
    CLASSES_DIVINDADE_OBRIGATORIA,
    ErroValidacao,
    divindades_compativeis_conceito,
    gerar_personagem,
    listar_opcoes_criacao,
)

__all__ = [
    "BaseDados",
    "CLASSES_DIVINDADE_OBRIGATORIA",
    "ErroValidacao",
    "carregar_dados",
    "divindades_compativeis_conceito",
    "exportar_ficha_docx",
    "exportar_ficha_txt",
    "gerar_personagem",
    "listar_opcoes_criacao",
    "nome_arquivo_seguro",
]
