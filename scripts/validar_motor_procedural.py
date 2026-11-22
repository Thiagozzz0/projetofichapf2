"""Suíte de validação completa do Motor Procedural PF2E, Backend Flask, Front-End e Exportadores."""

from __future__ import annotations

import io
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from app import app
from motor import carregar_dados, gerar_personagem, listar_opcoes_criacao
from motor.util import ATRIBUTOS, modificador, normalizar


def verificar_contrato_e_matematica(res: dict, dados) -> None:
    modelo = dados.estrutura_ficha["modelo_ficha_vazia"]
    meta = res["meta_geracao"]
    ficha = res["ficha"]

    # 1. Contrato idêntico ao modelo_ficha_vazia e nome válido
    nome_p = ficha["cabecalho"]["nome_personagem"]
    assert nome_p and len(nome_p) <= 40 and "variados" not in normalizar(nome_p), f"Nome inválido: {nome_p!r}"
    assert set(ficha.keys()) == set(modelo.keys()), "Chaves raiz da ficha divergem de estrutura_ficha.json"
    assert len(ficha["golpes_corpo_a_corpo"]) == 3
    assert len(ficha["golpes_a_distancia"]) == 3
    assert len(ficha["proficiencia_armas"]) == 4
    assert len(ficha["pericias"]) == 18

    rotulos_per = [p["rotulo_oficial"] for p in ficha["pericias"]]
    assert rotulos_per.index("SOCIEDADE") < rotulos_per.index("SOBREVIVÊNCIA")

    hab = ficha["habilidades_e_talentos"]
    assert len(hab["ancestralidade"]) == 7
    assert len(hab["pericia"]) == 11
    assert len(hab["gerais"]) == 5
    assert len(hab["classe"]) == 22
    assert len(hab["bonus"]) == 2
    assert len(ficha["acoes_e_atividades"]) == 6
    assert len(ficha["acoes_livres_e_reacoes"]) == 4
    assert len(ficha["conjuracao"]["truques_magicos"]) == 7
    assert len(ficha["conjuracao"]["magias_inatas"]) == 2
    assert len(ficha["conjuracao"]["magias_foco"]["slots"]) == 4
    assert len(ficha["conjuracao"]["magias"]) == 32

    # 2. Matemática de Atributos (1º nível: 8..18)
    for atr in ATRIBUTOS:
        val = ficha["atributos"][atr]["valor"]
        mod = ficha["atributos"][atr]["modificador"]
        assert 8 <= val <= 18, f"Atributo {atr} fora de 8..18: {val}"
        assert mod == modificador(val), f"Modificador incorreto em {atr}: {mod} != {modificador(val)}"

    # 3. PV, CA, Velocidade, Percepção, Salvamentos, Perícias
    assert ficha["pontos_vida"]["max"] > 0
    assert ficha["pontos_vida"]["atuais"] == ficha["pontos_vida"]["max"]
    ca = ficha["classe_armadura"]
    assert ca["total"] == 10 + ca["des_ou_limite"] + ca["proficiencia"] + ca["item"]
    assert ficha["velocidade"]["metros"] >= 1.5
    assert ficha["percepcao"]["total"] == ficha["percepcao"]["mod_sab"] + ficha["percepcao"]["proficiencia"]

    for sid in ("fortitude", "reflexos", "vontade"):
        s = ficha["jogadas_salvamento"][sid]
        assert s["total"] == s["mod_atributo"] + s["proficiencia"] + s["item"]

    for p in ficha["pericias"]:
        pen = p["penalidade_armadura"] or 0
        assert p["total"] == p["mod_atributo"] + p["proficiencia"] + p["item"] + pen
    assert ficha["pericias"][14]["grau_proficiencia"] == "treinado"  # saber_1 da biografia

    # 4. Orçamento (15 po = 1500 pc) e Riqueza
    assert meta["gasto_pc"] >= 0
    assert meta["saldo_pc"] >= 0
    assert meta["gasto_pc"] + meta["saldo_pc"] == 1500
    riq = ficha["inventario"]["riqueza"]
    assert riq["po"] * 100 + riq["pp"] * 10 + riq["pc"] == meta["saldo_pc"]

    # 5. Restrição de Druida sem metal
    if meta["classe_id"] == "druida":
        arm = dados.armaduras[next(
            k for k, v in dados.armaduras.items() if v["nome"] == meta["armadura_equipada"]
        )]
        assert normalizar(arm.get("material")) != "metal", f"Druida equipou metal: {arm['nome']}"
        esc_nome = ficha["classe_armadura"]["escudo"]["nome"]
        assert "aço" not in normalizar(esc_nome) and "aco" not in normalizar(esc_nome)


def main() -> None:
    dados = carregar_dados()
    opcoes = listar_opcoes_criacao(dados)
    assert len(opcoes["ancestralidades"]) == 6
    assert len(opcoes["biografias"]) == 35
    assert len(opcoes["classes"]) == 12
    assert opcoes["total_conceitos"] == 56

    # ------------------------------------------------------------------
    # 1. Determinismo com seed fixa e variação com seeds distintas
    # ------------------------------------------------------------------
    a1 = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor", seed=42)
    a2 = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor", seed=42)
    assert a1 == a2, "Mesma seed deve gerar ficha exatamente idêntica"

    b1 = gerar_personagem("elfo", "elfo_vidente", "mago", "mago_evocador_artilharia", seed=101)
    b2 = gerar_personagem("elfo", "elfo_vidente", "mago", "mago_evocador_artilharia", seed=202)
    assert b1["ficha"]["cabecalho"]["nome_personagem"] != b2["ficha"]["cabecalho"]["nome_personagem"] or (
        b1["meta_geracao"]["biografia_id"] != b2["meta_geracao"]["biografia_id"]
    )

    # ------------------------------------------------------------------
    # 2. Cobertura total de 56 conceitos + todas as 29 heranças
    # ------------------------------------------------------------------
    todas_herancas = [
        (anc["id"], her["id"])
        for anc in dados.ancestralidades.values()
        for her in anc["herancas"]
    ]
    assert len(todas_herancas) == 29

    todos_conceitos = list(dados.conceitos.values())
    assert len(todos_conceitos) == 56
    total_combinacoes = max(len(todas_herancas), len(todos_conceitos))
    for i in range(total_combinacoes):
        anc_id, her_id = todas_herancas[i % len(todas_herancas)]
        con = todos_conceitos[i % len(todos_conceitos)]
        res = gerar_personagem(
            ancestralidade_id=anc_id,
            heranca_id=her_id,
            classe_id=con["classe_id"],
            conceito_id=con["id"],
            seed=1000 + i,
            dados=dados,
        )
        verificar_contrato_e_matematica(res, dados)

    # ------------------------------------------------------------------
    # 3. Casos especiais de ancestralidade/herança e biografia manual
    # ------------------------------------------------------------------
    casos_especiais = [
        ("anao", "anao_da_forja", "campeao", "campeao_bastiao_impenetravel", "soldado"),
        ("elfo", "elfo_vidente", "guerreiro", "guerreiro_atirador_elite", "batedor"),
        ("gnomo", "gnomo_tocado_pelas_fadas", "bardo", "bardo_comandante_inspirador", "animador"),
        ("gnomo", "gnomo_manancial", "clerigo", "clerigo_hospitalario_sagrado", "acolito"),
        ("goblin", "goblin_inquebravel", "barbaro", "barbaro_guerreiro_draconico", None),
        ("goblin", "goblin_dentes_de_navalha", "ladino", "ladino_sombra_silenciosa", None),
        ("humano", "meio_elfo", "patrulheiro", "patrulheiro_metralhadora_flechas", None),
        ("humano", "meio_orc", "guerreiro", "guerreiro_colosso_demolidor", None),
        ("humano", "heranca_perita", "mago", "mago_evocador_artilharia", None),
        ("humano", "heranca_versatil", "ladino", "ladino_duelista_fanfarrao", None),
    ]
    for idx, (aid, hid, cid, conid, bid) in enumerate(casos_especiais):
        res = gerar_personagem(aid, hid, cid, conid, biografia_id=bid, seed=500 + idx, dados=dados)
        verificar_contrato_e_matematica(res, dados)
        if bid:
            assert not res["meta_geracao"]["biografia_procedural"]
            assert res["meta_geracao"]["biografia_id"] == bid
        if aid == "anao":
            assert any("adaga de cla" in normalizar(i["nome"]) for i in res["ficha"]["inventario"]["itens_vestidos"])
        if hid == "goblin_inquebravel":
            assert res["meta_geracao"]["ancestralidade_id"] == "goblin"
            # 10 (herança) + 12 (bárbaro) + mod_con >= 22
            assert res["ficha"]["pontos_vida"]["max"] >= 22
        if hid == "goblin_dentes_de_navalha":
            assert any("mandibulas" in normalizar(g["arma"]) for g in res["ficha"]["golpes_corpo_a_corpo"])
        if hid == "elfo_vidente":
            assert res["ficha"]["conjuracao"]["magias_inatas"][0]["nome"] == "Detectar Magia"

    # ------------------------------------------------------------------
    # 4. Sinergia temática e mapeamento procedural Conceito -> Subclasse
    # ------------------------------------------------------------------
    mago_elem = gerar_personagem("elfo", "elfo_das_florestas", "mago", "mago_evocador_artilharia", seed=77, dados=dados)
    nomes_magias_mago = {
        normalizar(m["nome"])
        for m in mago_elem["ficha"]["conjuracao"]["truques_magicos"] + mago_elem["ficha"]["conjuracao"]["magias"]
        if m["nome"]
    }
    assert mago_elem["meta_geracao"]["subclasse_oficial_id"] == "evocacao"
    assert mago_elem["meta_geracao"]["tese_arcana_id"] == "mescla_de_magia"
    assert mago_elem["ficha"]["conjuracao"]["tradicoes_marcadas"]["arcana"] is True
    assert "produzir chama" in nomes_magias_mago
    assert "maos flamejantes" in nomes_magias_mago

    guer_2m = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor", seed=88, dados=dados)
    assert guer_2m["meta_geracao"]["subclasse_oficial_id"] == "agressor"
    assert guer_2m["ficha"]["golpes_corpo_a_corpo"][0]["arma"] == "Montante"
    assert guer_2m["ficha"]["habilidades_e_talentos"]["classe"][2]["nome"] == "Ataque Poderoso"

    # Multi-subclasse procedural (Feiticeiro: Dracônica [arcana] ou Elemental [primal])
    linhagens_vistas: set[str] = set()
    for s in range(1, 31):
        feit = gerar_personagem(
            "humano", "heranca_versatil", "feiticeiro", "feiticeiro_artifice_elemental_draconico", seed=s, dados=dados
        )
        verificar_contrato_e_matematica(feit, dados)
        sub_f = feit["meta_geracao"]["subclasse_oficial_id"]
        linhagens_vistas.add(sub_f)
        if sub_f == "draconica":
            assert feit["ficha"]["conjuracao"]["tradicoes_marcadas"]["arcana"] is True
        else:
            assert sub_f == "elemental"
            assert feit["ficha"]["conjuracao"]["tradicoes_marcadas"]["primal"] is True
    assert linhagens_vistas == {"draconica", "elemental"}, f"Esperadas ambas linhagens, vistas: {linhagens_vistas}"

    # Bárbaro Instinto do Furor ganha 2 talentos de classe de 1º nível
    furor = gerar_personagem("anao", "anao_das_rochas", "barbaro", "barbaro_incursor_vanguarda", seed=12, dados=dados)
    assert furor["meta_geracao"]["subclasse_oficial_id"] == "instinto_do_furor"
    assert furor["ficha"]["habilidades_e_talentos"]["classe"][2]["nome"] == "Investida Súbita"
    assert any(
        b["nome"] == "Arremessador Enfurecido" for b in furor["ficha"]["habilidades_e_talentos"]["bonus"]
    )

    # Clérigo Ceifador Sombrio usa Fonte de Ferimento e tendência neutra
    ceifador = gerar_personagem("humano", "heranca_perita", "clerigo", "clerigo_ceifador_sombrio", seed=19, dados=dados)
    assert ceifador["ficha"]["cabecalho"]["tendencia"] == "N"
    assert any(
        "Ferir (Fonte Divina" in (m["nome"] or "") for m in ceifador["ficha"]["conjuracao"]["magias"]
    )

    # Monge Arsenal Monástico ganha proficiência treinado em armas com traço monge
    kensei = gerar_personagem("humano", "heranca_perita", "monge", "monge_guerreiro_armas_monasticas", seed=25, dados=dados)
    assert kensei["ficha"]["proficiencia_armas"][3]["rotulo"] == "ARMAS DE MONGE"
    assert kensei["ficha"]["proficiencia_armas"][3]["grau_proficiencia"] == "treinado"
    assert kensei["ficha"]["golpes_corpo_a_corpo"][0]["ataque"]["grau_proficiencia"] == "treinado"

    # Mago Ilusionista com Tese Sintonização com Familiar Aprimorada ganha Familiar
    ilus = gerar_personagem("elfo", "elfo_artico", "mago", "mago_ilusionista_enganador", seed=31, dados=dados)
    assert ilus["meta_geracao"]["tese_arcana_id"] == "sintonizacao_com_familiar_aprimorada"
    assert ilus["ficha"]["habilidades_e_talentos"]["classe"][2]["nome"] == "Familiar"

    # ------------------------------------------------------------------
    # 5. Rotas Flask via test_client()
    # ------------------------------------------------------------------
    client = app.test_client()

    r_idx = client.get("/")
    assert r_idx.status_code == 200
    html_idx = r_idx.get_data(as_text=True)
    assert "Pathfinder 2" in html_idx
    assert "ficha.css" in html_idx and "app.js" in html_idx

    assert client.get("/static/css/ficha.css").status_code == 200
    assert client.get("/static/js/app.js").status_code == 200

    req_txt = RAIZ_PROJETO / "requirements.txt"
    assert req_txt.exists(), "requirements.txt ausente na raiz do projeto"
    assert "Flask" in req_txt.read_text(encoding="utf-8")

    r_saude = client.get("/api/saude")
    assert r_saude.status_code == 200
    assert r_saude.get_json()["conceitos"] == 56
    assert r_saude.get_json()["divindades"] == 20

    r_opcoes = client.get("/api/opcoes")
    assert r_opcoes.status_code == 200
    opcoes_json = r_opcoes.get_json()
    assert len(opcoes_json["classes"]) == 12
    assert len(opcoes_json["divindades"]) == 20
    obrigatorias_ui = {c["id"] for c in opcoes_json["classes"] if c["divindade_obrigatoria"]}
    assert obrigatorias_ui == {"clerigo", "campeao"}
    mapa_conceitos_ui = {con["id"]: con for c in opcoes_json["classes"] for con in c["conceitos"]}
    esperado_div_compat = {
        "campeao_cruzado_vingador": 7,
        "campeao_bastiao_impenetravel": 9,
        "campeao_quebrador_correntes": 5,
        "campeao_cavaleiro_montado": 13,
        "clerigo_hospitalario_sagrado": 15,
        "clerigo_ceifador_sombrio": 11,
        "clerigo_arauto_guerra": 20,
        "guerreiro_colosso_demolidor": 20,
    }
    for cid_check, qtd_esp in esperado_div_compat.items():
        assert len(mapa_conceitos_ui[cid_check]["divindades_compativeis_ids"]) == qtd_esp

    r_her = client.get("/api/ancestralidades/elfo/herancas")
    assert r_her.status_code == 200 and len(r_her.get_json()["herancas"]) == 5
    assert client.get("/api/ancestralidades/inexistente/herancas").status_code == 404

    r_con = client.get("/api/classes/mago/conceitos")
    assert r_con.status_code == 200 and len(r_con.get_json()["conceitos"]) == 5
    assert r_con.get_json()["divindade_obrigatoria"] is False
    primeiro_con = r_con.get_json()["conceitos"][0]
    assert "subclasses_oficiais_candidatas" in primeiro_con and "sinergia_mecanica" in primeiro_con
    assert len(primeiro_con["divindades_compativeis_ids"]) == 20
    r_con_camp = client.get("/api/classes/campeao/conceitos")
    assert r_con_camp.status_code == 200 and r_con_camp.get_json()["divindade_obrigatoria"] is True
    assert client.get("/api/classes/inexistente/conceitos").status_code == 404

    r_ok = client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "mago",
            "conceito_id": "mago_evocador_artilharia",
            "seed": 12345,
        },
    )
    assert r_ok.status_code == 200
    payload_ok = r_ok.get_json()
    verificar_contrato_e_matematica(payload_ok, dados)

    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "clerigo",
            "conceito_id": "clerigo_hospitalario_sagrado",
            "divindade_id": "",
        },
    ).status_code == 400
    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "campeao",
            "conceito_id": "campeao_cruzado_vingador",
            "divindade_id": "nenhuma",
        },
    ).status_code == 400

    r_guerr_nenhuma = client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "divindade_id": "nenhuma",
            "seed": 42,
        },
    )
    assert r_guerr_nenhuma.status_code == 200
    assert r_guerr_nenhuma.get_json()["ficha"]["cabecalho"]["divindade"] == ""

    r_guerr_rand = client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "divindade_id": "aleatoria",
            "seed": 42,
        },
    )
    assert r_guerr_rand.status_code == 200
    assert r_guerr_rand.get_json()["ficha"]["cabecalho"]["divindade"] != ""

    r_all_rand = client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "aleatorio",
            "heranca_id": "aleatorio",
            "biografia_id": "aleatoria",
            "classe_id": "aleatorio",
            "conceito_id": "aleatorio",
            "divindade_id": "aleatorio",
            "nivel": "aleatorio",
            "seed": 2026,
        },
    )
    assert r_all_rand.status_code == 200
    payload_rand = r_all_rand.get_json()
    verificar_contrato_e_matematica(payload_rand, dados)
    assert "+0 CA" in payload_rand["meta_geracao"]["armadura_equipada_resumo"] or "CA" in payload_rand["meta_geracao"]["armadura_equipada_resumo"]

    # Erros controlados (400)
    assert client.post("/api/gerar", json={"ancestralidade_id": "humano"}).status_code == 400
    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "mago",
            "conceito_id": "guerreiro_colosso_demolidor",
        },
    ).status_code == 400
    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "mago",
            "conceito_id": "mago_evocador_artilharia",
            "nivel": 2,
        },
    ).status_code == 400

    # ------------------------------------------------------------------
    # 6. Exportação .TXT e .DOCX (com resultado pronto e por parâmetros)
    # ------------------------------------------------------------------
    # Exportação TXT via resultado já gerado
    r_txt_res = client.post("/api/exportar/txt", json={"resultado": mago_elem})
    assert r_txt_res.status_code == 200
    assert r_txt_res.mimetype == "text/plain"
    disp_txt = r_txt_res.headers.get("Content-Disposition", "")
    assert "attachment;" in disp_txt and disp_txt.endswith('.txt"')
    txt_body = r_txt_res.get_data(as_text=True)
    assert mago_elem["ficha"]["cabecalho"]["nome_personagem"] in txt_body
    assert "Evocador de Artilharia" in txt_body
    assert "PERÍCIAS (18 LINHAS OFICIAIS)" in txt_body
    assert "PÁGINA 4 (p. 583) — CONJURAÇÃO E MAGIAS" in txt_body
    assert "Mãos Flamejantes" in txt_body

    # Exportação TXT via parâmetros diretos
    r_txt_params = client.post(
        "/api/exportar/txt",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "seed": 88,
        },
    )
    assert r_txt_params.status_code == 200
    txt_guer = r_txt_params.get_data(as_text=True)
    assert "Montante" in txt_guer and "Ataque Poderoso" in txt_guer

    cl_iomedae = gerar_personagem(
        "humano", "heranca_perita", "clerigo", "clerigo_arauto_guerra", divindade_id="iomedae", seed=77, dados=dados
    )
    verificar_contrato_e_matematica(cl_iomedae, dados)
    dr_matilha = gerar_personagem("elfo", "elfo_das_florestas", "druida", "druida_senhor_matilha", seed=77, dados=dados)
    verificar_contrato_e_matematica(dr_matilha, dados)

    # Exportação TXT de Clérigo (Divindade) e Druida (Companheiro Animal)
    r_txt_cl = client.post("/api/exportar/txt", json={"resultado": cl_iomedae})
    assert r_txt_cl.status_code == 200
    txt_cl = r_txt_cl.get_data(as_text=True)
    assert "Iomedae" in txt_cl and "Arma Favorecida" in txt_cl

    r_txt_dr = client.post("/api/exportar/txt", json={"resultado": dr_matilha})
    assert r_txt_dr.status_code == 200
    txt_dr = r_txt_dr.get_data(as_text=True)
    assert "Companheiro Animal" in txt_dr

    # Exportação DOCX (Mago Evocador + Guerreiro Colosso + Clérigo Iomedae + Druida Matilha) com validação OOXML/XML completa
    arquivos_esperados_docx = {
        "[Content_Types].xml",
        "_rels/.rels",
        "word/_rels/document.xml.rels",
        "word/styles.xml",
        "word/document.xml",
    }
    for caso_res, trechos_esperados in (
        (mago_elem, [mago_elem["ficha"]["cabecalho"]["nome_personagem"], "Evocador de Artilharia", "Flamejantes"]),
        (guer_2m, [guer_2m["ficha"]["cabecalho"]["nome_personagem"], "Montante", "Ataque Poderoso"]),
        (cl_iomedae, [cl_iomedae["ficha"]["cabecalho"]["nome_personagem"], "Iomedae", "Arma Favorecida"]),
        (dr_matilha, [dr_matilha["ficha"]["cabecalho"]["nome_personagem"], "Companheiro Animal"]),
    ):
        r_docx = client.post("/api/exportar/docx", json={"resultado": caso_res})
        assert r_docx.status_code == 200
        assert r_docx.mimetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        disp_docx = r_docx.headers.get("Content-Disposition", "")
        assert "attachment;" in disp_docx and disp_docx.endswith('.docx"')

        raw_docx = r_docx.get_data()
        with zipfile.ZipFile(io.BytesIO(raw_docx), "r") as zf:
            assert zf.testzip() is None
            assert arquivos_esperados_docx.issubset(set(zf.namelist()))
            for nome_xml in arquivos_esperados_docx:
                ET.fromstring(zf.read(nome_xml))
            doc_txt = "".join(ET.fromstring(zf.read("word/document.xml")).itertext())
            for trecho in trechos_esperados:
                assert trecho in doc_txt, f"Trecho {trecho!r} ausente do word/document.xml"

    # Erros 400 nos endpoints de exportação
    assert client.post("/api/exportar/txt", json={}).status_code == 400
    assert client.post("/api/exportar/docx", json={"ficha": {}}).status_code == 400

    print("SUCESSO TOTAL — Validação da Etapa 3 + Etapa 4 concluída!")
    print(f"Conceitos validados: {len(todos_conceitos)}/56 | Heranças validadas: {len(todas_herancas)}/29")
    print(f"Casos especiais validados: {len(casos_especiais)} | Rotas Flask validadas: 8 endpoints + static (200/400/404)")
    print("Exportadores validados: .txt (UTF-8) e .docx (ZIP/OOXML/XML íntegros)")


if __name__ == "__main__":
    main()
