"""Testes de borda para dupla magia inata (Talento Ancestral + Ancestralidade Adotada)."""

from __future__ import annotations

import unittest

from app import ASSET_VERSION, app as flask_app
from motor import ErroValidacao, carregar_dados, gerar_personagem


class DuplaMagiaInataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dados = carregar_dados()
        self.conc_guerreiro = self.dados.conceitos_da_classe("guerreiro")[0]["id"]
        self.tal_dupla = {
            "modo": "personalizado",
            "ancestralidade_id": "magia_extraterrena",
            "gerais_ids": ["ancestralidade_adotada"],
            "ancestralidade_adotada_id": "gnomo",
            "talento_ancestral_adotado_id": "magia_do_primeiro_mundo",
        }

    def test_dupla_magia_inata_com_truque_exclusivo_arcano(self) -> None:
        res = gerar_personagem(
            ancestralidade_id="elfo",
            heranca_id="elfo_das_florestas",
            classe_id="guerreiro",
            conceito_id=self.conc_guerreiro,
            nivel=3,
            seed=99,
            escolhas_talentos=self.tal_dupla,
            escolhas_magias={"modo": "procedural", "truque_inato_ancestral_id": "escudo_mistico"},
        )
        inatas = [m["nome"] for m in res["ficha"]["conjuracao"]["magias_inatas"] if m.get("nome")]
        self.assertEqual(len(inatas), 2)
        self.assertIn("Escudo Místico", inatas)
        self.assertEqual(len(set(inatas)), 2)

    def test_dupla_magia_inata_com_truque_em_ambas_tradicoes_sem_duplicar(self) -> None:
        res = gerar_personagem(
            ancestralidade_id="elfo",
            heranca_id="elfo_das_florestas",
            classe_id="guerreiro",
            conceito_id=self.conc_guerreiro,
            nivel=3,
            seed=99,
            escolhas_talentos=self.tal_dupla,
            escolhas_magias={"modo": "procedural", "truque_inato_ancestral_id": "arco_eletrico"},
        )
        inatas = [m["nome"] for m in res["ficha"]["conjuracao"]["magias_inatas"] if m.get("nome")]
        self.assertEqual(len(inatas), 2)
        self.assertIn("Arco Elétrico", inatas)
        self.assertEqual(len(set(inatas)), 2)

    def test_dupla_magia_inata_com_truque_exclusivo_primal(self) -> None:
        res = gerar_personagem(
            ancestralidade_id="elfo",
            heranca_id="elfo_das_florestas",
            classe_id="guerreiro",
            conceito_id=self.conc_guerreiro,
            nivel=3,
            seed=99,
            escolhas_talentos=self.tal_dupla,
            escolhas_magias={"modo": "procedural", "truque_inato_ancestral_id": "estabilizar"},
        )
        inatas = [m["nome"] for m in res["ficha"]["conjuracao"]["magias_inatas"] if m.get("nome")]
        self.assertEqual(len(inatas), 2)
        self.assertIn("Estabilizar", inatas)
        self.assertEqual(len(set(inatas)), 2)

    def test_dupla_magia_inata_rejeita_truque_inexistente(self) -> None:
        with self.assertRaises(ErroValidacao):
            gerar_personagem(
                ancestralidade_id="elfo",
                heranca_id="elfo_das_florestas",
                classe_id="guerreiro",
                conceito_id=self.conc_guerreiro,
                nivel=3,
                seed=99,
                escolhas_talentos=self.tal_dupla,
                escolhas_magias={"modo": "procedural", "truque_inato_ancestral_id": "truque_que_nao_existe"},
            )

    def test_gnomo_tocado_pelas_fadas_truque_inato_heranca_manual_e_validacao(self) -> None:
        res = gerar_personagem(
            ancestralidade_id="gnomo",
            heranca_id="gnomo_tocado_pelas_fadas",
            classe_id="guerreiro",
            conceito_id=self.conc_guerreiro,
            nivel=1,
            seed=42,
            escolhas_magias={"modo": "procedural", "truque_inato_heranca_id": "estabilizar"},
        )
        inatas = [m["nome"] for m in res["ficha"]["conjuracao"]["magias_inatas"] if m.get("nome")]
        self.assertEqual(inatas, ["Estabilizar"])

        with self.assertRaises(ErroValidacao):
            gerar_personagem(
                ancestralidade_id="gnomo",
                heranca_id="gnomo_tocado_pelas_fadas",
                classe_id="guerreiro",
                conceito_id=self.conc_guerreiro,
                nivel=1,
                seed=42,
                escolhas_magias={"modo": "procedural", "truque_inato_heranca_id": "escudo_mistico"},
            )

    def test_gnomo_manancial_truque_inato_heranca_manual_e_validacao(self) -> None:
        res = gerar_personagem(
            ancestralidade_id="gnomo",
            heranca_id="gnomo_manancial",
            classe_id="guerreiro",
            conceito_id=self.conc_guerreiro,
            nivel=1,
            seed=42,
            escolhas_magias={"modo": "procedural", "truque_inato_heranca_id": "escudo_mistico"},
        )
        inatas = [m["nome"] for m in res["ficha"]["conjuracao"]["magias_inatas"] if m.get("nome")]
        self.assertEqual(inatas, ["Escudo Místico"])

        with self.assertRaises(ErroValidacao):
            gerar_personagem(
                ancestralidade_id="gnomo",
                heranca_id="gnomo_manancial",
                classe_id="guerreiro",
                conceito_id=self.conc_guerreiro,
                nivel=1,
                seed=42,
                escolhas_magias={
                    "modo": "procedural",
                    "truque_inato_heranca_id": "lanca_divina",
                    "tradicao_inata_heranca": "arcana",
                },
            )

    def test_gnomo_tocado_pelas_fadas_mais_adotada_magia_extraterrena_sem_conflito(self) -> None:
        res = gerar_personagem(
            ancestralidade_id="gnomo",
            heranca_id="gnomo_tocado_pelas_fadas",
            classe_id="guerreiro",
            conceito_id=self.conc_guerreiro,
            nivel=3,
            seed=42,
            escolhas_talentos={
                "modo": "personalizado",
                "gerais_ids": ["ancestralidade_adotada"],
                "ancestralidade_adotada_id": "elfo",
                "talento_ancestral_adotado_id": "magia_extraterrena",
            },
            escolhas_magias={
                "modo": "procedural",
                "truque_inato_heranca_id": "estabilizar",
                "truque_inato_ancestral_id": "escudo_mistico",
            },
        )
        inatas = [m["nome"] for m in res["ficha"]["conjuracao"]["magias_inatas"] if m.get("nome")]
        self.assertEqual(inatas, ["Estabilizar", "Escudo Místico"])

    def test_api_ancestralidade_n5_manual_e_elementos_ui_frente1(self) -> None:
        client = flask_app.test_client()
        with client.get("/") as resp_home:
            self.assertEqual(resp_home.status_code, 200)
            html = resp_home.get_data(as_text=True)
            self.assertIn('id="sel-truque-inato-heranca"', html)
            self.assertIn('id="tal-ancestralidade-n5"', html)
            self.assertIn(f"?v={ASSET_VERSION}", html)

        tal_n1_valido = self.dados.ancestralidades["humano"]["talentos_ancestralidade"][0]["id"]
        with client.post(
            "/api/gerar",
            json={
                "ancestralidade_id": "humano",
                "heranca_id": "heranca_versatil",
                "classe_id": "guerreiro",
                "conceito_id": self.conc_guerreiro,
                "nivel": 5,
                "seed": 77,
                "escolhas_talentos": {
                    "modo": "personalizado",
                    "ancestralidade_id": tal_n1_valido,
                    "ancestralidade_n5_id": "improvisador_astuto",
                },
            },
        ) as resp_gerar:
            self.assertEqual(resp_gerar.status_code, 200)
            anc_items = resp_gerar.get_json()["ficha"]["habilidades_e_talentos"]["ancestralidade"]
            nomes_anc = [x.get("nome") for x in anc_items]
            self.assertIn("Improvisador Astuto", nomes_anc)

        with client.post(
            "/api/gerar",
            json={
                "ancestralidade_id": "humano",
                "heranca_id": "heranca_versatil",
                "classe_id": "guerreiro",
                "conceito_id": self.conc_guerreiro,
                "nivel": 5,
                "seed": 77,
                "escolhas_talentos": {
                    "modo": "personalizado",
                    "ancestralidade_id": tal_n1_valido,
                    "ancestralidade_n5_id": tal_n1_valido,
                },
            },
        ) as resp_dup:
            self.assertEqual(resp_dup.status_code, 400)


if __name__ == "__main__":
    unittest.main()
