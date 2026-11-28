"""Testes unitários do carregador modular de expansões em `motor/dados.py`."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from motor_pf2.dados import (
    DIR_DADOS_PADRAO,
    FONTE_BASE_ID,
    carregar_dados,
    limpar_cache_dados,
    listar_expansoes_disponiveis,
)


def _escrever_json(caminho: Path, conteudo: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")


class ExpansoesDadosTests(unittest.TestCase):
    def tearDown(self) -> None:
        limpar_cache_dados()

    def test_livro_basico_padrao_integro_e_arquetipos_indexados(self) -> None:
        dados = carregar_dados()
        self.assertEqual(len(dados.classes), 12)
        self.assertEqual(len(dados.ancestralidades), 6)
        self.assertEqual(len(dados.arquetipos), 12)
        self.assertEqual(dados.classes["guerreiro"]["fonte"], FONTE_BASE_ID)
        self.assertEqual(dados.ancestralidades["humano"]["fonte"], FONTE_BASE_ID)
        self.assertIn("tabela_2_1_idiomas_comuns", dados.idiomas)
        self.assertEqual(dados.herancas_versateis, {})

    def test_mesclagem_expansao_modular_isolamento_e_herancas_versateis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dir_tmp = Path(tmp) / "dados"
            dir_tmp.mkdir()
            for arq in DIR_DADOS_PADRAO.glob("*.json"):
                shutil.copy2(arq, dir_tmp / arq.name)

            # Expansão ativa simulando parte do Guia Avançado do Jogador
            dir_gaj = dir_tmp / "expansoes" / "gaj_teste"
            _escrever_json(
                dir_gaj / "manifest.json",
                {
                    "id": "gaj_teste",
                    "nome": "Guia Avançado (Teste)",
                    "sigla": "GAJ",
                    "ativa": True,
                    "ordem": 10,
                },
            )
            _escrever_json(
                dir_gaj / "classes.json",
                {
                    "classes": [
                        {
                            "id": "bruxo_teste",
                            "nome": "Bruxo",
                            "subclasses": {"opcoes": [{"id": "patrono_destino", "nome": "Destino"}]},
                            "talentos_de_classe": [{"id": "cackle_teste", "nome": "Gargalhada", "nivel": 1}],
                        }
                    ],
                    "extensoes_classes": {
                        "guerreiro": {
                            "talentos_de_classe": [
                                {"id": "golpe_gaj_teste", "nome": "Golpe GAJ Teste", "nivel": 1}
                            ]
                        }
                    },
                },
            )
            _escrever_json(
                dir_gaj / "ancestralidades_biografias.json",
                {
                    "ancestralidades": [
                        {
                            "id": "kobold_teste",
                            "nome": "Kobold",
                            "herancas": [{"id": "kobold_escamas_draconicas", "nome": "Escamas Dracônicas"}],
                            "talentos_ancestrais": [{"id": "recuo_kobold", "nome": "Recuo Kobold"}],
                        }
                    ],
                    "herancas_versateis": [
                        {
                            "id": "tiefling_teste",
                            "nome": "Tiefling",
                            "descricao": "Herança versátil planar.",
                            "talentos_ancestrais": [
                                {"id": "olhos_infernais_teste", "nome": "Olhos Infernais", "nivel": 1}
                            ],
                        }
                    ],
                    "extensoes_ancestralidades": {
                        "humano": {
                            "herancas": [{"id": "humano_invernal_teste", "nome": "Humano Invernal"}],
                            "talentos_ancestrais": [{"id": "talento_hum_gaj", "nome": "Talento Humano GAJ"}],
                        }
                    },
                    "biografias": {
                        "lista": [{"id": "cozinheiro_teste", "nome": "Cozinheiro"}]
                    },
                    "idiomas": {
                        "tabela_2_1_idiomas_comuns": [{"idioma": "Tengu", "regioes_falantes": "Tengus"}]
                    },
                },
            )
            _escrever_json(
                dir_gaj / "magias.json",
                {
                    "magias": [{"id": "fogo_fatuo_teste", "nome": "Fogo Fátuo", "nivel": 1}],
                    "magias_de_foco": {"lista": [{"id": "maldicao_teste", "nome": "Maldição Teste"}]},
                },
            )
            _escrever_json(
                dir_gaj / "talentos.json",
                {"talentos": [{"id": "talento_geral_gaj", "nome": "Talento Geral GAJ", "nivel": 1}]},
            )
            _escrever_json(
                dir_gaj / "equipamentos.json",
                {
                    "armas": {
                        "corpo_a_corpo": [{"id": "espada_gaj_teste", "nome": "Espada GAJ", "preco_pc": 100}]
                    }
                },
            )
            _escrever_json(
                dir_gaj / "arquetipos.json",
                {"arquetipos": [{"id": "bastiao_teste", "nome": "Bastião"}]},
            )

            # Expansão inativa por padrão
            dir_off = dir_tmp / "expansoes" / "exp_inativa"
            _escrever_json(
                dir_off / "manifest.json",
                {"id": "exp_inativa", "nome": "Expansão Inativa", "ativa": False, "ordem": 20},
            )
            _escrever_json(
                dir_off / "talentos.json",
                {"talentos": [{"id": "talento_inativo", "nome": "Talento Inativo", "nivel": 1}]},
            )

            disponiveis = listar_expansoes_disponiveis(dir_tmp)
            self.assertEqual([e["id"] for e in disponiveis], ["gaj_teste", "exp_inativa"])

            # 1) Modo padrão: carrega Livro Básico + gaj_teste (ignora exp_inativa)
            dados_padrao = carregar_dados(dir_tmp)
            self.assertEqual(dados_padrao.expansoes_ativas, ["gaj_teste"])
            self.assertIn("bruxo_teste", dados_padrao.classes)
            self.assertEqual(dados_padrao.classes["bruxo_teste"]["fonte"], "gaj_teste")
            self.assertTrue(
                any(
                    t["id"] == "golpe_gaj_teste"
                    for t in dados_padrao.classes["guerreiro"]["talentos_de_classe"]
                )
            )
            self.assertIn("kobold_teste", dados_padrao.ancestralidades)
            self.assertIn("tiefling_teste", dados_padrao.herancas_versateis)
            self.assertEqual(dados_padrao.heranca("anao", "tiefling_teste")["nome"], "Tiefling")
            self.assertTrue(
                any(h["id"] == "tiefling_teste" for h in dados_padrao.herancas_disponiveis("anao"))
            )
            self.assertTrue(
                any(t["id"] == "olhos_infernais_teste" for t in dados_padrao.talentos_mesticos["tiefling_teste"])
            )
            self.assertTrue(
                any(h["id"] == "humano_invernal_teste" for h in dados_padrao.ancestralidades["humano"]["herancas"])
            )
            self.assertIn("cozinheiro_teste", dados_padrao.biografias)
            self.assertIn("fogo_fatuo_teste", dados_padrao.magias)
            self.assertIn("maldicao_teste", dados_padrao.magias_foco)
            self.assertIn("talento_geral_gaj", dados_padrao.talentos_gerais_pericia)
            self.assertIn("espada_gaj_teste", dados_padrao.armas)
            self.assertIn("bastiao_teste", dados_padrao.arquetipos)
            self.assertNotIn("talento_inativo", dados_padrao.talentos_gerais_pericia)
            self.assertTrue(
                any(i["idioma"] == "Tengu" for i in dados_padrao.idiomas["tabela_2_1_idiomas_comuns"])
            )

            # 2) Modo somente Livro Básico (expansoes_ativas=()) permanece 100% isolado
            dados_base = carregar_dados(dir_tmp, expansoes_ativas=())
            self.assertEqual(dados_base.expansoes_ativas, [])
            self.assertNotIn("bruxo_teste", dados_base.classes)
            self.assertNotIn("tiefling_teste", dados_base.herancas_versateis)
            self.assertFalse(
                any(
                    t["id"] == "golpe_gaj_teste"
                    for t in dados_base.classes["guerreiro"]["talentos_de_classe"]
                )
            )
            self.assertFalse(
                any(h["id"] == "humano_invernal_teste" for h in dados_base.ancestralidades["humano"]["herancas"])
            )

            # 3) Ativação explícita da expansão inativa
            dados_custom = carregar_dados(dir_tmp, expansoes_ativas=("exp_inativa",))
            self.assertEqual(dados_custom.expansoes_ativas, ["exp_inativa"])
            self.assertIn("talento_inativo", dados_custom.talentos_gerais_pericia)
            self.assertNotIn("bruxo_teste", dados_custom.classes)


if __name__ == "__main__":
    unittest.main()
