"""Testes unitários e de integração dos exportadores e rotas Flask /api/cc/*."""

from __future__ import annotations

import io
import unittest
import xml.etree.ElementTree as ET
import zipfile

import pymupdf

from app import app
from motor_cc import (
    exportar_ficha_cc_docx,
    exportar_ficha_cc_pdf,
    exportar_ficha_cc_txt,
    gerar_ficha_cc,
)


class TestCCApiExportacao(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()

    def _payload_marcial(self) -> dict:
        return {
            "nome": "Sir Roland",
            "titulos": "Campeão da Fronteira",
            "jogador": "Thiago",
            "raca_id": "humano",
            "classe_id": "combatente",
            "nivel": 3,
            "disposicao_id": "lei_bem",
            "metodo_geracao": "distribuido_62",
            "regra_pv": "media_fixa",
            "atributos_base": {
                "forca": 16,
                "destreza": 12,
                "constituicao": 14,
                "inteligencia": 7,
                "sabedoria": 6,
                "carisma": 7,
            },
            "primarios_escolhidos": ["constituicao", "destreza"],
            "armadura_id": "camisa_de_cota_de_malha",
            "escudo_id": "escudo_medio_de_aco",
            "elmo_id": "elmo_normal",
            "armas_ids": ["espada_longa", "arco_longo"],
            "itens_ids": ["mochila", "corda_de_canhamo_15_metros"],
            "anotacoes": "Juramento de proteger a cidade livre.",
        }

    def _payload_conjurador_alto(self) -> dict:
        return {
            "nome": "Alatar",
            "titulos": "Mestre das Runas",
            "raca_id": "elfo",
            "classe_id": "mago",
            "nivel": 9,
            "disposicao_id": "neutro_bem",
            "metodo_geracao": "old_school_3d6_ordem",
            "regra_pv": "media_fixa",
            "atributos_base": {
                "forca": 8,
                "destreza": 14,
                "constituicao": 12,
                "inteligencia": 18,
                "sabedoria": 11,
                "carisma": 10,
            },
            "primarios_escolhidos": ["destreza"],
            "armas_ids": ["adaga"],
            "auto_completar_feiticos": True,
        }

    def test_exportadores_marcial_txt_docx_pdf(self) -> None:
        ficha = gerar_ficha_cc(self._payload_marcial())

        # 1. TXT
        txt = exportar_ficha_cc_txt(ficha)
        self.assertIn("Método de Atributos: Distribuído: 62 pontos", txt)
        self.assertIn("Sir Roland", txt)
        self.assertIn("Espada, Longa", txt)

        # 2. DOCX (OOXML válido)
        docx_bytes = exportar_ficha_cc_docx(ficha)
        with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as zf:
            nomes = set(zf.namelist())
            self.assertIn("word/document.xml", nomes)
            doc_xml = zf.read("word/document.xml").decode("utf-8")
            ET.fromstring(doc_xml)
            self.assertIn("Distribuído: 62 pontos", doc_xml)
            self.assertIn("Sir Roland", doc_xml)

        # 3. PDF (1 página oficial preenchida)
        pdf_bytes = exportar_ficha_cc_pdf(ficha)
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        try:
            self.assertEqual(len(doc), 1)
            texto_p1 = doc[0].get_text()
            self.assertIn("Método: Distribuído: 62 pontos", texto_p1)
            self.assertIn("Sir Roland", texto_p1)
            self.assertIn("Espada, Longa", texto_p1)
            self.assertIn("Arco, Longo", texto_p1)
        finally:
            doc.close()

    def test_exportador_conjurador_alto_com_anexo_e_old_school(self) -> None:
        ficha = gerar_ficha_cc(self._payload_conjurador_alto())

        txt = exportar_ficha_cc_txt(ficha)
        self.assertIn("Método de Atributos: Old School: 3d6 em ordem", txt)
        self.assertIn("[ MAGIAS E FEITIÇOS ]", txt)

        docx_bytes = exportar_ficha_cc_docx(ficha)
        with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as zf:
            doc_xml = zf.read("word/document.xml").decode("utf-8")
            ET.fromstring(doc_xml)
            self.assertIn("Old School: 3d6 em ordem", doc_xml)

        pdf_bytes = exportar_ficha_cc_pdf(ficha)
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        try:
            # Mago Nv 9 possui feitiços de círculos 4 e 5 -> gera página 2 anexa
            self.assertEqual(len(doc), 2)
            texto_p1 = doc[0].get_text()
            texto_p2 = doc[1].get_text()
            self.assertIn("Método: Old School: 3d6 em ordem", texto_p1)
            self.assertIn("Alatar", texto_p1)
            self.assertIn("Nível 4", texto_p2)
            self.assertIn("Nível 5", texto_p2)
        finally:
            doc.close()

    def test_rotas_api_cc(self) -> None:
        # GET /api/cc/opcoes
        r_op = self.client.get("/api/cc/opcoes")
        self.assertEqual(r_op.status_code, 200)
        dados_op = r_op.get_json()
        self.assertEqual(len(dados_op["racas"]), 7)
        self.assertEqual(len(dados_op["classes"]), 13)
        self.assertEqual(len(dados_op["metodos_atributos"]), 4)

        # POST /api/cc/rolar-atributos
        r_rol = self.client.post("/api/cc/rolar-atributos", json={"metodo": "heroico_4d6", "seed": 7})
        self.assertEqual(r_rol.status_code, 200)
        self.assertEqual(r_rol.get_json()["rotulo_ficha"], "Heróico: 4d6")

        r_rol_err = self.client.post("/api/cc/rolar-atributos", json={"metodo": "invalido"})
        self.assertEqual(r_rol_err.status_code, 400)

        # POST /api/cc/gerar (válido e inválido)
        payload = self._payload_marcial()
        r_ger = self.client.post("/api/cc/gerar", json=payload)
        self.assertEqual(r_ger.status_code, 200)
        ficha = r_ger.get_json()
        self.assertEqual(ficha["cabecalho"]["nome"], "Sir Roland")

        r_ger_err = self.client.post("/api/cc/gerar", json={"raca_id": "inexistente", "classe_id": "combatente"})
        self.assertEqual(r_ger_err.status_code, 400)

        # POST /api/cc/exportar/txt (a partir da ficha pronta)
        r_txt = self.client.post("/api/cc/exportar/txt", json={"ficha": ficha})
        self.assertEqual(r_txt.status_code, 200)
        self.assertIn("text/plain", r_txt.content_type)
        self.assertIn("ficha_cc_sir_roland_combatente_nv3.txt", r_txt.headers["Content-Disposition"])
        self.assertIn("Distribuído: 62 pontos", r_txt.get_data(as_text=True))

        # POST /api/cc/exportar/docx (sob demanda direto do payload)
        r_docx = self.client.post("/api/cc/exportar/docx", json=payload)
        self.assertEqual(r_docx.status_code, 200)
        self.assertIn("officedocument.wordprocessingml", r_docx.content_type)
        self.assertIn(".docx", r_docx.headers["Content-Disposition"])
        with zipfile.ZipFile(io.BytesIO(r_docx.data), "r") as zf:
            self.assertIn("word/document.xml", zf.namelist())

        # POST /api/cc/exportar/pdf
        r_pdf = self.client.post("/api/cc/exportar/pdf", json={"ficha": ficha})
        self.assertEqual(r_pdf.status_code, 200)
        self.assertEqual(r_pdf.content_type, "application/pdf")
        self.assertIn("ficha_cc_sir_roland_combatente_nv3.pdf", r_pdf.headers["Content-Disposition"])
        self.assertTrue(r_pdf.data.startswith(b"%PDF"))

    def test_rotas_ui_cc_e_hub(self) -> None:
        r_hub = self.client.get("/")
        self.assertEqual(r_hub.status_code, 200)
        html_hub = r_hub.get_data(as_text=True)
        self.assertIn("card-sistema-cc", html_hub)
        self.assertIn("/castle-and-crusades", html_hub)

        r_pf2 = self.client.get("/pf2")
        self.assertEqual(r_pf2.status_code, 200)

        r_cc = self.client.get("/cc")
        self.assertEqual(r_cc.status_code, 200)
        html_cc = r_cc.get_data(as_text=True)
        self.assertIn('id="form-cc-gerador"', html_cc)
        self.assertIn('id="cc-ficha-pronta"', html_cc)
        self.assertIn("static/css/cc.css", html_cc)
        self.assertIn("static/js/cc/app.js", html_cc)

        for static_path in (
            "/static/css/cc.css",
            "/static/js/cc/estado.js",
            "/static/js/cc/atributos.js",
            "/static/js/cc/render_ficha.js",
            "/static/js/cc/app.js",
        ):
            r_st = self.client.get(static_path)
            self.assertEqual(r_st.status_code, 200, static_path)


if __name__ == "__main__":
    unittest.main()
