"""Testes unitários de casos de borda matemáticos e regras PF2E."""

from __future__ import annotations

import unittest

from scripts import validar_casos_borda_pf2e as suite


class CasosBordaPF2ETests(unittest.TestCase):
    """Executa cada caso de borda da suíte PF2E via unittest."""

    def test_ca_limite_destreza_e_sem_armadura(self) -> None:
        suite.test_ca_limite_destreza_e_sem_armadura()

    def test_penalidade_armadura_barulhenta_flexivel_e_ferro_desimpedido(self) -> None:
        suite.test_penalidade_armadura_barulhenta_flexivel_e_ferro_desimpedido()

    def test_mochila_sobrecarga_e_carregador_robusto(self) -> None:
        suite.test_mochila_sobrecarga_e_carregador_robusto()

    def test_armas_acuidade_ladrao_propulsiva_posturas_e_anao_mago(self) -> None:
        suite.test_armas_acuidade_ladrao_propulsiva_posturas_e_anao_mago()

    def test_idiomas_humano_mago_grimorio_e_regras_especificas(self) -> None:
        suite.test_idiomas_humano_mago_grimorio_e_regras_especificas()

    def test_acoes_classe_pagina3_e_zero_descarte_talentos(self) -> None:
        suite.test_acoes_classe_pagina3_e_zero_descarte_talentos()

    def test_divindades_reais_e_companheiros_familiares(self) -> None:
        suite.test_divindades_reais_e_companheiros_familiares()

    def test_divindade_obrigatoria_vs_opcional_e_compatibilidade(self) -> None:
        suite.test_divindade_obrigatoria_vs_opcional_e_compatibilidade()

    def test_revisao_geral_etapa_23(self) -> None:
        suite.test_revisao_geral_etapa_23()

    def test_aleatorio_7_campos_e_bonus_equipamentos(self) -> None:
        suite.test_aleatorio_7_campos_e_bonus_equipamentos()

    def test_exportar_pdf_oficial_4_paginas(self) -> None:
        suite.test_exportar_pdf_oficial_4_paginas()

    def test_escolhas_atributos_manual_procedural_aleatorio(self) -> None:
        suite.test_escolhas_atributos_manual_procedural_aleatorio()

    def test_compra_manual_e_hibrida_equipamentos(self) -> None:
        suite.test_compra_manual_e_hibrida_equipamentos()

    def test_curadoria_e_selecao_manual_talentos(self) -> None:
        suite.test_curadoria_e_selecao_manual_talentos()

    def test_selecao_manual_e_regras_pericias(self) -> None:
        suite.test_selecao_manual_e_regras_pericias()

    def test_selecao_manual_e_aleatoria_magias(self) -> None:
        suite.test_selecao_manual_e_aleatoria_magias()

    def test_aderencia_procedural_nortes(self) -> None:
        suite.test_aderencia_procedural_nortes()

    def test_orcamento_90_peso_leve_e_viagem_procedural(self) -> None:
        suite.test_orcamento_90_peso_leve_e_viagem_procedural()

    def test_personalizacao_companheiro_familiar_e_perfil(self) -> None:
        suite.test_personalizacao_companheiro_familiar_e_perfil()

    def test_regras_da_casa_peso_racao_e_oleo(self) -> None:
        suite.test_regras_da_casa_peso_racao_e_oleo()

    def test_pdf_secoes_referencia_completa(self) -> None:
        suite.test_pdf_secoes_referencia_completa()

    def test_progressao_niveis_2_a_5(self) -> None:
        suite.test_progressao_niveis_2_a_5()


if __name__ == "__main__":
    unittest.main()
