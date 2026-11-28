"""Testes unitários do motor de regras de Castles & Crusades (motor_cc)."""

from __future__ import annotations

import unittest

from motor_cc import METODOS_GERACAO, gerar_ficha_cc, obter_opcoes_criacao, rolar_atributos
from motor_cc.atributos import calcular_modificador
from motor_cc.dados import (
    listar_classes,
    listar_disposicoes,
    listar_magias,
    listar_racas,
    mapa_todos_equipamentos,
)


class TestMotorCC(unittest.TestCase):
    def test_carregamento_completo_dados_cc(self) -> None:
        self.assertEqual(len(listar_racas()), 7)
        self.assertEqual(len(listar_classes()), 13)
        self.assertEqual(len(listar_disposicoes()), 9)
        self.assertEqual(len(mapa_todos_equipamentos()), 328)
        self.assertEqual(len(listar_magias()), 378)

        opcoes = obter_opcoes_criacao()
        self.assertEqual(len(opcoes["metodos_atributos"]), 4)
        self.assertEqual(len(opcoes["racas"]), 7)
        self.assertEqual(len(opcoes["classes"]), 13)

    def test_tabela_modificadores_oficial_cc(self) -> None:
        esperados = {
            1: -4,
            2: -3,
            3: -3,
            4: -2,
            5: -2,
            6: -1,
            8: -1,
            9: 0,
            12: 0,
            13: 1,
            15: 1,
            16: 2,
            17: 2,
            18: 3,
            19: 3,
        }
        for val, mod in esperados.items():
            self.assertEqual(calcular_modificador(val), mod, f"Valor {val}")

    def test_quatro_metodos_rolagem_atributos(self) -> None:
        for metodo in METODOS_GERACAO:
            res = rolar_atributos(metodo=metodo, seed=42)
            self.assertEqual(res["metodo"], metodo)
            self.assertEqual(len(res["valores"]), 6)
            for v in res["valores"].values():
                self.assertGreaterEqual(v, 3)
                self.assertLessEqual(v, 18)
            if metodo == "distribuido_62":
                self.assertEqual(sum(res["valores"].values()), 62)
            if metodo == "old_school_3d6_ordem":
                self.assertFalse(res["alocacao_livre"])
                self.assertEqual(len(res["sugestoes_classes"]), 13)

    def test_distribuido_62_rejeita_soma_invalida(self) -> None:
        with self.assertRaises(ValueError):
            gerar_ficha_cc(
                {
                    "raca_id": "humano",
                    "classe_id": "combatente",
                    "metodo_geracao": "distribuido_62",
                    "atributos_base": {
                        "forca": 18,
                        "destreza": 18,
                        "constituicao": 18,
                        "inteligencia": 10,
                        "sabedoria": 10,
                        "carisma": 10,
                    },
                }
            )

    def test_primarios_humano_vs_anao_e_meio_elfo(self) -> None:
        base_62 = {
            "forca": 15,
            "destreza": 12,
            "constituicao": 13,
            "inteligencia": 8,
            "sabedoria": 7,
            "carisma": 7,
        }
        ficha_hum = gerar_ficha_cc(
            {
                "nome": "Aldric",
                "raca_id": "humano",
                "classe_id": "combatente",
                "metodo_geracao": "distribuido_62",
                "atributos_base": base_62,
                "primarios_escolhidos": ["constituicao", "destreza"],
            }
        )
        self.assertEqual(ficha_hum["atributos"]["total_primarios"], 3)
        self.assertEqual(ficha_hum["atributos"]["atributos"]["forca"]["classe_base_siege"], 12)
        self.assertEqual(ficha_hum["atributos"]["atributos"]["inteligencia"]["classe_base_siege"], 18)
        self.assertEqual(ficha_hum["cabecalho"]["rotulo_metodo"], "Distribuído: 62 pontos")

        ficha_anao = gerar_ficha_cc(
            {
                "raca_id": "anao",
                "classe_id": "combatente",
                "metodo_geracao": "classico_3d6_livre",
                "atributos_base": base_62,
                "primarios_escolhidos": ["constituicao"],
            }
        )
        self.assertEqual(ficha_anao["atributos"]["total_primarios"], 2)
        # Anão: +1 CON, -1 DES
        self.assertEqual(ficha_anao["atributos"]["atributos"]["constituicao"]["valor"], 14)
        self.assertEqual(ficha_anao["atributos"]["atributos"]["destreza"]["valor"], 11)

        ficha_me = gerar_ficha_cc(
            {
                "raca_id": "meio_elfo",
                "linhagem_meio_elfo": "humana",
                "atributo_secundario_meio_elfo": "sabedoria",
                "classe_id": "bardo",
                "metodo_geracao": "classico_3d6_livre",
                "atributos_base": base_62,
            }
        )
        # Bardo tem CAR como primário; SAB é secundário e recebe +2 da linhagem humana
        self.assertEqual(ficha_me["atributos"]["atributo_secundario_meio_elfo"], "sabedoria")
        self.assertEqual(ficha_me["atributos"]["atributos"]["sabedoria"]["bonus_extra_teste"], 2)

    def test_pv_pos_nivel_10_e_ca_sobrecarga(self) -> None:
        base = {
            "forca": 10,
            "destreza": 16,  # +2
            "constituicao": 14,  # +1
            "inteligencia": 10,
            "sabedoria": 10,
            "carisma": 10,
        }
        ficha = gerar_ficha_cc(
            {
                "raca_id": "humano",
                "classe_id": "combatente",
                "nivel": 12,
                "regra_pv": "media_fixa",
                "atributos_base": base,
                "armadura_id": "camisa_de_cota_de_malha",
                "escudo_id": "escudo_medio_de_aco",
                "armas_ids": ["espada_longa", "arco_longo"],
            }
        )
        # N1 = 10+1=11, N2..10 = 9*(6+1)=63, N11..12 = 2*4=8 => total 82
        self.assertEqual(ficha["combate"]["pv"]["total"], 82)
        self.assertEqual(len(ficha["combate"]["pv"]["por_nivel"]), 12)
        self.assertEqual(len(ficha["combate"]["ataques"]), 2)
        self.assertEqual(ficha["combate"]["ca"]["total"], 10 + 4 + 1 + 2)  # 17

        # Testar perda de bônus de DES na CA quando Sobrecarregado (SB > 3 * CS)
        # FOR 3 (sem FOR/CON primários) => CS = 3, limite carregado = 9; itens de SB alto estouram 9
        base_fraco = {
            "forca": 3,
            "destreza": 16,  # +2
            "constituicao": 10,
            "inteligencia": 16,
            "sabedoria": 10,
            "carisma": 10,
        }
        ficha_sobre = gerar_ficha_cc(
            {
                "raca_id": "elfo",
                "classe_id": "mago",
                "primarios_escolhidos": ["destreza"],
                "atributos_base": base_fraco,
                "armadura_id": "armadura_completa",
                "escudo_id": "escudo_grande_de_aco",
                "armas_ids": ["alabarda", "bardiche"],
            }
        )
        self.assertEqual(ficha_sobre["equipamentos"]["sobrecarga"]["categoria_id"], "sobrecarregado")
        self.assertTrue(ficha_sobre["combate"]["ca"]["perdeu_des_por_sobrecarga"])
        self.assertEqual(ficha_sobre["combate"]["ca"]["mod_destreza"], 0)

    def test_conjuracao_com_feiticos_bonus_por_atributo(self) -> None:
        base = {
            "forca": 10,
            "destreza": 12,
            "constituicao": 12,
            "inteligencia": 18,  # +1 de 1º, +1 de 2º, +1 de 3º (cumulativo)
            "sabedoria": 10,
            "carisma": 10,
        }
        # Mago nível 1: tem acesso a 0º e 1º (não a 2º nem 3º) -> só ganha +1 de 1º!
        ficha_n1 = gerar_ficha_cc(
            {
                "raca_id": "elfo",
                "classe_id": "mago",
                "nivel": 1,
                "atributos_base": base,
                "auto_completar_feiticos": True,
            }
        )
        esp_n1 = ficha_n1["magias"]["espacos_por_circulo"]
        self.assertEqual(esp_n1["1"]["bonus_atributo"], 1)
        self.assertNotIn("2", esp_n1)

        # Mago nível 5: tem acesso a 0º, 1º, 2º e 3º -> ganha +1 em 1º, 2º e 3º!
        ficha_n5 = gerar_ficha_cc(
            {
                "raca_id": "elfo",
                "classe_id": "mago",
                "nivel": 5,
                "atributos_base": base,
                "auto_completar_feiticos": True,
            }
        )
        esp_n5 = ficha_n5["magias"]["espacos_por_circulo"]
        self.assertEqual(esp_n5["1"]["bonus_atributo"], 1)
        self.assertEqual(esp_n5["2"]["bonus_atributo"], 1)
        self.assertEqual(esp_n5["3"]["bonus_atributo"], 1)

    def test_todas_combinacoes_7_racas_x_13_classes(self) -> None:
        base = {
            "forca": 12,
            "destreza": 12,
            "constituicao": 12,
            "inteligencia": 12,
            "sabedoria": 12,
            "carisma": 12,
        }
        for raca in listar_racas():
            for classe in listar_classes():
                ficha = gerar_ficha_cc(
                    {
                        "raca_id": raca["id"],
                        "classe_id": classe["id"],
                        "nivel": 3,
                        "atributos_base": base,
                        "regra_pv": "media_fixa",
                        "auto_completar_feiticos": True,
                    }
                )
                self.assertGreater(ficha["combate"]["pv"]["total"], 0)
                self.assertGreaterEqual(ficha["combate"]["ca"]["total"], 9)


if __name__ == "__main__":
    unittest.main()
