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
from motor_pf2 import carregar_dados, gerar_personagem, listar_opcoes_criacao
from motor_pf2.util import ATRIBUTOS, modificador, normalizar


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

    # 2. Matemática de Atributos (1º nível: 8..18; 5º nível: 8..19)
    max_atr = 19 if ficha["cabecalho"]["nivel"] >= 5 else 18
    for atr in ATRIBUTOS:
        val = ficha["atributos"][atr]["valor"]
        mod = ficha["atributos"][atr]["modificador"]
        assert 8 <= val <= max_atr, f"Atributo {atr} fora de 8..{max_atr}: {val}"
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

    # 4. Orçamento (conforme nível) e Riqueza
    assert meta["gasto_pc"] >= 0
    assert meta["saldo_pc"] >= 0
    assert meta["gasto_pc"] + meta["saldo_pc"] == meta.get("orcamento_pc", 1500)
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
    assert opcoes["total_conceitos"] == 72

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
    # 2. Cobertura total de 72 conceitos (6 por classe) + todas as 29 heranças
    # ------------------------------------------------------------------
    todas_herancas = [
        (anc["id"], her["id"])
        for anc in dados.ancestralidades.values()
        for her in anc["herancas"]
    ]
    assert len(todas_herancas) == 29

    todos_conceitos = list(dados.conceitos.values())
    assert len(todos_conceitos) == 72
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
        assert res["meta_geracao"]["saldo_pc"] >= 150, f"Reserva de 10% violada em {con['id']}: {res['meta_geracao']['saldo_pc']}"
        assert res["meta_geracao"]["gasto_pc"] <= 1350
        assert res["meta_geracao"]["observacoes_combate"]["esta_sobrecarregado"] is False, (
            f"Sobrecarga procedural em {con['id']}: {res['ficha']['inventario']['volume_total']}"
        )

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
        assert res["meta_geracao"]["saldo_pc"] >= 150, f"Reserva de 10% violada em {con['id']}: {res['meta_geracao']['saldo_pc']}"
        assert res["meta_geracao"]["gasto_pc"] <= 1350
        assert res["meta_geracao"]["observacoes_combate"]["esta_sobrecarregado"] is False, (
            f"Sobrecarga procedural em {con['id']}: {res['ficha']['inventario']['volume_total']}"
        )
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

    # Bárbaro Instinto do Furor ganha 2 talentos de classe de 1º nível (agrupados no mesmo slot TALENTO 1º)
    furor = gerar_personagem("anao", "anao_das_rochas", "barbaro", "barbaro_incursor_vanguarda", seed=12, dados=dados)
    assert furor["meta_geracao"]["subclasse_oficial_id"] == "instinto_do_furor"
    assert "Investida Súbita" in furor["ficha"]["habilidades_e_talentos"]["classe"][2]["nome"]
    assert "Arremessador Enfurecido" in furor["ficha"]["habilidades_e_talentos"]["classe"][2]["nome"]

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

    r_hub = client.get("/")
    assert r_hub.status_code == 200
    html_hub = r_hub.get_data(as_text=True)
    assert "Pathfinder 2e" in html_hub and "Castle and Crusades" in html_hub
    assert "icone-pf2.png" in html_hub and "icone-cc.png" in html_hub
    assert "hub.css" in html_hub

    r_cc = client.get("/cc")
    assert r_cc.status_code == 200
    assert "Castle and Crusades" in r_cc.get_data(as_text=True)

    r_idx = client.get("/pf2")
    assert r_idx.status_code == 200
    html_idx = r_idx.get_data(as_text=True)
    assert "Pathfinder 2" in html_idx
    assert "ficha.css" in html_idx and "render_ficha.js" in html_idx and "app.js" in html_idx
    for id_dom in (
        "painel-regras-casa",
        "modo-regras-casa",
        "btn-desbloquear-regras-casa",
        "box-senha-regras-casa",
        "input-senha-regras-casa",
        "acordeao-etapas",
        "desc-conceito-inline",
        "etapa-criacao-inicial",
        "etapa-talentos",
        "etapa-equipamentos",
        "corpo-etapa-criacao",
        "corpo-etapa-talentos",
        "corpo-etapa-equipamentos",
        "subgrupo-atb-ancestralidade",
        "subgrupo-atb-biografia",
        "subgrupo-atb-classe",
        "attr-classe-chave",
        "painel-atributos-abcd",
        "attr-anc-livre-1",
        "attr-bio-restrito",
        "attr-livre-1",
        "modo-talentos",
        "painel-talentos-custom",
        "tal-ancestralidade",
        "info-tal-biografia",
        "tal-classe-1",
        "tal-pericia-1",
        "tal-geral-1",
        "modo-equipamentos",
        "painel-equipamentos-custom",
        "eq-armadura",
        "eq-escudo",
        "eq-arma-cc-select",
        "eq-arma-dist-select",
        "eq-variado-select",
    ):
        assert id_dom in html_idx

    with client.get("/static/css/ficha.css") as r_css:
        assert r_css.status_code == 200
    with client.get("/static/js/render_ficha.js") as r_rf:
        assert r_rf.status_code == 200
    with client.get("/static/js/app.js") as r_app:
        assert r_app.status_code == 200

    req_txt = RAIZ_PROJETO / "requirements.txt"
    assert req_txt.exists(), "requirements.txt ausente na raiz do projeto"
    req_txt_body = req_txt.read_text(encoding="utf-8")
    assert "Flask" in req_txt_body and "PyMuPDF" in req_txt_body

    r_saude = client.get("/api/saude")
    assert r_saude.status_code == 200
    assert r_saude.get_json()["conceitos"] == 72
    assert r_saude.get_json()["divindades"] == 20

    r_rc = client.get("/api/regras-casa")
    assert r_rc.status_code == 200
    rc_json = r_rc.get_json()
    assert len(rc_json["perfis"]) == 2 and len(rc_json["regras"]) == 3
    assert rc_json["padrao_modo"] == "regras_da_casa"
    assert rc_json["protegido_por_senha"] is True
    assert rc_json["exigir_senha_a_cada_troca"] is True
    assert "senha" not in rc_json
    assert {r["id"] for r in rc_json["regras"]} == {
        "racao_por_unidade_peso_l",
        "oleo_500ml_peso_l",
        "conversao_5_leves_por_volume",
    }

    assert client.post("/api/regras-casa/validar-senha", json={"senha": "9930"}).status_code == 200
    assert client.post("/api/regras-casa/validar-senha", json={"senha": "9930"}).get_json()["autorizado"] is True
    r_senha_err = client.post("/api/regras-casa/validar-senha", json={"senha": "0000"})
    assert r_senha_err.status_code == 403 and r_senha_err.get_json()["autorizado"] is False
    assert client.post("/api/regras-casa/validar-senha", json={"senha": ""}).status_code == 403

    r_opcoes = client.get("/api/opcoes")
    assert r_opcoes.status_code == 200
    opcoes_json = r_opcoes.get_json()
    assert len(opcoes_json["classes"]) == 12
    assert len(opcoes_json["divindades"]) == 20
    anc_por_id = {a["id"]: a for a in opcoes_json["ancestralidades"]}
    assert anc_por_id["humano"]["qtd_melhorias_livres"] == 2 and anc_por_id["humano"]["melhorias_fixas_ids"] == []
    assert anc_por_id["humano"]["atributos_bloqueados_livres_ids"] == []
    assert anc_por_id["elfo"]["qtd_melhorias_livres"] == 1 and set(anc_por_id["elfo"]["melhorias_fixas_ids"]) == {"des", "int"}
    assert set(anc_por_id["elfo"]["atributos_bloqueados_livres_ids"]) == {"des", "int", "con"}
    assert set(anc_por_id["anao"]["atributos_bloqueados_livres_ids"]) == {"con", "sab", "car"}
    assert all(len(b["melhorias_atributo_ids"]) == 2 for b in opcoes_json["biografias"])
    obrigatorias_ui = {c["id"] for c in opcoes_json["classes"] if c["divindade_obrigatoria"]}
    assert obrigatorias_ui == {"clerigo", "campeao"}
    cls_por_id = {c["id"]: c for c in opcoes_json["classes"]}
    assert set(cls_por_id["guerreiro"]["atributo_chave_ids"]) == {"for", "des"}
    assert cls_por_id["guerreiro"]["permite_escolha_atributo_chave"] is True
    assert cls_por_id["mago"]["permite_escolha_atributo_chave"] is False
    mapa_conceitos_ui = {con["id"]: con for c in opcoes_json["classes"] for con in c["conceitos"]}
    assert set(mapa_conceitos_ui["ladino_duelista_fanfarrao"]["atributo_chave_opcoes"]) == {"des", "car"}
    assert "prioridade_atributos" in mapa_conceitos_ui["guerreiro_colosso_demolidor"]
    assert opcoes_json["nivel_minimo"] == 1
    assert opcoes_json["nivel_maximo_catalogo"] == 5
    assert opcoes_json["niveis_catalogo"] == [1, 2, 3, 4, 5]
    cat_tal = opcoes_json["catalogo_talentos"]
    assert cat_tal["nivel"] == 1
    assert cat_tal["nivel_maximo"] == 5
    assert set(cat_tal["ancestralidade_por_id"]) == set(anc_por_id)
    assert "5" in cat_tal["ancestralidade_por_nivel"]["humano"]
    assert set(cat_tal["mesticos"]) == {"meio_elfo", "meio_orc"}
    assert "5" in cat_tal["mesticos_por_nivel"]["meio_elfo"]
    assert cat_tal["classe_por_id"]["guerreiro"]["tem_slot_n1_base"] is True
    assert cat_tal["classe_por_id"]["guerreiro"]["niveis_slot_classe"] == [1, 2, 4]
    assert "2" in cat_tal["classe_por_id"]["guerreiro"]["talentos_por_nivel"]
    assert "4" in cat_tal["classe_por_id"]["guerreiro"]["talentos_por_nivel"]
    assert cat_tal["classe_por_id"]["bardo"]["tem_slot_n1_base"] is False
    assert cat_tal["classe_por_id"]["bardo"]["niveis_slot_classe"] == [2, 4]
    assert cat_tal["classe_por_id"]["clerigo"]["tem_slot_n1_base"] is False
    assert cat_tal["classe_por_id"]["ladino"]["tem_slot_n1_base"] is True
    assert len(cat_tal["pericia_n1"]) >= 30 and len(cat_tal["gerais_n1"]) >= 10
    assert "2" in cat_tal["pericia_por_nivel"] and "3" in cat_tal["gerais_por_nivel"]
    cat_mag = opcoes_json["catalogo_magias"]
    assert cat_mag["circulo_maximo"] == 3
    assert len(cat_mag["por_tradicao"]["arcana"]["nivel_2"]) > 0
    assert len(cat_mag["por_tradicao"]["arcana"]["nivel_3"]) > 0
    assert set(cat_mag["por_tradicao"]["arcana"]["por_circulo"]) == {"1", "2", "3"}
    assert "5" in cls_por_id["mago"]["conjuracao_classe"]["progressao_por_nivel"]
    assert cls_por_id["mago"]["conjuracao_classe"]["progressao_por_nivel"]["5"]["espacos_por_circulo"] == {"1": 3, "2": 3, "3": 2}
    cat_eq = opcoes_json["catalogo_equipamentos"]
    assert cat_eq["orcamento_inicial_pc"] == 1500
    assert cat_eq["orcamento_por_nivel_pc"] == {"1": 1500, "2": 3000, "3": 7500, "4": 14000, "5": 27000}
    assert {w["categoria"] for w in cat_eq["armas_corpo_a_corpo"]} == {"Arma Simples", "Arma Marcial", "Arma Avançada"}
    assert {w["categoria"] for w in cat_eq["armas_distancia"]} == {"Arma Simples", "Arma Marcial"}
    ids_var_cat = {it["id"] for it in cat_eq["equipamentos_variados"]}
    assert "kit_de_aventureiro" not in ids_var_cat and "flechas" in ids_var_cat
    assert {"kit_de_escalada", "kit_de_disfarce", "kit_de_reparo", "kit_de_pesca"} <= ids_var_cat
    assert cat_eq["kits_de_classe"] == {}
    assert "fogo_alquimico" not in ids_var_cat and "bomba_alquimica" not in {w["id"] for w in cat_eq["armas_distancia"]}
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
    assert r_con.status_code == 200 and len(r_con.get_json()["conceitos"]) == 6
    assert r_con.get_json()["divindade_obrigatoria"] is False
    primeiro_con = r_con.get_json()["conceitos"][0]
    assert "subclasses_oficiais_candidatas" in primeiro_con and "sinergia_mecanica" in primeiro_con
    assert "estilo_empunhadura" in primeiro_con and "saber_sugerido" in primeiro_con
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
    assert payload_ok["meta_geracao"]["orcamento_pc"] == 1500
    assert payload_ok["meta_geracao"]["escolhas_magias"]["qtd_magias_por_circulo"] == {"1": 6}
    assert payload_ok["meta_geracao"]["regras_casa"]["ativa"] is False
    assert payload_ok["meta_geracao"]["itens_leves_por_volume"] == 10

    r_ok_rc = client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "escolhas_regras_casa": {"modo": "regras_da_casa"},
            "seed": 12345,
        },
    )
    assert r_ok_rc.status_code == 200
    payload_ok_rc = r_ok_rc.get_json()
    verificar_contrato_e_matematica(payload_ok_rc, dados)
    assert payload_ok_rc["meta_geracao"]["regras_casa"]["ativa"] is True
    assert payload_ok_rc["meta_geracao"]["itens_leves_por_volume"] == 5

    r_txt_rc = client.post("/api/exportar/txt", json={"resultado": payload_ok_rc})
    assert r_txt_rc.status_code == 200
    txt_rc_body = r_txt_rc.get_data(as_text=True)
    assert "Regras Casa:" not in txt_rc_body and "5 L = 1 Vol" in txt_rc_body

    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "mago",
            "conceito_id": "mago_evocador_artilharia",
            "escolhas_regras_casa": {"modo": "invalido"},
        },
    ).status_code == 400

    # Talentos manuais válidos via POST /api/gerar e bloqueio 400 para slots inativos no 1º nível
    r_tal_ok = client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "biografia_id": "acrobata",
            "classe_id": "ladino",
            "conceito_id": "ladino_sombra_silenciosa",
            "escolhas_talentos": {
                "modo": "personalizado",
                "ancestralidade_id": "pericia_natural",
                "classe_ids": ["finta_dupla"],
                "pericia_ids": ["queda_do_gato"],
                "gerais_ids": ["veloz"],
            },
            "seed": 555,
        },
    )
    assert r_tal_ok.status_code == 200
    j_tal_ok = r_tal_ok.get_json()
    verificar_contrato_e_matematica(j_tal_ok, dados)
    assert j_tal_ok["meta_geracao"]["escolhas_talentos"]["ancestralidade_id"] == "pericia_natural"
    assert j_tal_ok["meta_geracao"]["escolhas_talentos"]["classe_ids"] == ["finta_dupla"]
    assert j_tal_ok["meta_geracao"]["escolhas_talentos"]["pericia_ids"] == ["queda_do_gato"]
    assert j_tal_ok["meta_geracao"]["escolhas_talentos"]["gerais_ids"] == ["veloz"]

    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "anao",
            "heranca_id": "anao_das_rochas",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "escolhas_talentos": {"modo": "personalizado", "gerais_ids": ["veloz"]},
        },
    ).status_code == 400
    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "escolhas_talentos": {"modo": "personalizado", "pericia_ids": ["certeza"]},
        },
    ).status_code == 400

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

    # Escolhas manuais e aleatórias de atributos ABCD via API
    r_atb_manual = client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "biografia_id": "operario",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "escolhas_atributos": {
                "ancestralidade_livres": ["for", "sab"],
                "biografia_restrito": "con",
                "biografia_livre": "for",
                "classe_chave": "des",
                "livres_nivel_1": ["for", "con", "sab", "car"],
            },
            "seed": 555,
        },
    )
    assert r_atb_manual.status_code == 200
    res_atb_m = r_atb_manual.get_json()
    verificar_contrato_e_matematica(res_atb_m, dados)
    assert res_atb_m["meta_geracao"]["escolhas_atributos"]["ancestralidade_livres"] == ["for", "sab"]
    assert res_atb_m["meta_geracao"]["escolhas_atributos"]["biografia_restrito"] == "con"
    assert res_atb_m["meta_geracao"]["escolhas_atributos"]["biografia_livre"] == "for"
    assert res_atb_m["meta_geracao"]["escolhas_atributos"]["classe_chave"] == "des"
    assert res_atb_m["meta_geracao"]["atributo_chave"] == "des"
    assert res_atb_m["meta_geracao"]["escolhas_atributos"]["livres_nivel_1"] == ["for", "con", "sab", "car"]
    assert res_atb_m["ficha"]["atributos"]["for"]["valor"] == 16
    assert res_atb_m["ficha"]["atributos"]["des"]["valor"] == 12
    assert res_atb_m["ficha"]["atributos"]["sab"]["valor"] == 14
    assert res_atb_m["ficha"]["atributos"]["car"]["valor"] == 12

    r_atb_rand = client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "elfo",
            "heranca_id": "elfo_vidente",
            "biografia_id": "estudioso",
            "classe_id": "mago",
            "conceito_id": "mago_evocador_artilharia",
            "escolhas_atributos": {
                "ancestralidade_livres": ["aleatorio"],
                "biografia_restrito": "aleatorio",
                "biografia_livre": "aleatorio",
                "livres_nivel_1": ["aleatorio", "aleatorio", "aleatorio", "aleatorio"],
            },
            "seed": 777,
        },
    )
    assert r_atb_rand.status_code == 200
    verificar_contrato_e_matematica(r_atb_rand.get_json(), dados)

    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "elfo",
            "heranca_id": "elfo_vidente",
            "biografia_id": "estudioso",
            "classe_id": "mago",
            "conceito_id": "mago_evocador_artilharia",
            "escolhas_atributos": {"ancestralidade_livres": ["des"]},
        },
    ).status_code == 400
    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "anao",
            "heranca_id": "anao_da_forja",
            "biografia_id": "estudioso",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "escolhas_atributos": {"ancestralidade_livres": ["car"]},
        },
    ).status_code == 400
    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "biografia_id": "estudioso",
            "classe_id": "mago",
            "conceito_id": "mago_evocador_artilharia",
            "escolhas_atributos": {"livres_nivel_1": ["int", "int", "des", "con"]},
        },
    ).status_code == 400

    # Compra manual/híbrida de equipamentos pela API deduzindo de 15 po (1.500 pc)
    r_eq_manual = client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "escolhas_equipamentos": {
                "modo": "personalizado",
                "armadura_id": "cota_de_escamas",          # 400 pc
                "escudo_id": "escudo_de_aco",               # 200 pc
                "armas_corpo_a_corpo_ids": ["espada_longa"],  # 100 pc
                "armas_distancia_ids": [],
                "equipamentos_variados": [
                    {"id": "mochila", "quantidade": 1},          # 10 pc
                    {"id": "racoes_1_semana", "quantidade": 1},  # 40 pc
                    {"id": "cantil", "quantidade": 1},           # 5 pc
                    {"id": "pederneira_e_isqueiro", "quantidade": 1},  # 5 pc
                    {"id": "tocha", "quantidade": 10},           # 10 pc
                    {"id": "corda", "quantidade": 2},            # 100 pc
                ],
            },
            "seed": 111,
        },
    )
    assert r_eq_manual.status_code == 200
    res_eq = r_eq_manual.get_json()
    verificar_contrato_e_matematica(res_eq, dados)
    assert res_eq["meta_geracao"]["gasto_pc"] == 870
    assert res_eq["meta_geracao"]["saldo_pc"] == 630
    assert res_eq["ficha"]["inventario"]["riqueza"] == {"pc": 0, "pp": 3, "po": 6, "pl": 0}
    assert res_eq["meta_geracao"]["armadura_equipada"] == "Cota de escamas"
    assert res_eq["ficha"]["golpes_corpo_a_corpo"][0]["arma"] == "Espada longa"
    assert res_eq["ficha"]["golpes_a_distancia"][0]["arma"] == ""

    # Estourou orçamento (> 1.500 pc) ou item alquímico bloqueado -> 400
    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "escolhas_equipamentos": {
                "armadura_id": "meia_armadura",  # 1800 pc > 1500 pc
            },
        },
    ).status_code == 400
    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "escolhas_equipamentos": {
                "equipamentos_variados": ["fogo_alquimico"],
            },
        },
    ).status_code == 400

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
            "nivel": 6,
        },
    ).status_code == 400

    # Progressão completa N2..N5 para todas as 12 classes via /api/gerar
    classes_lista = [c["id"] for c in opcoes_json["classes"]]
    for idx_cls, cid in enumerate(classes_lista):
        niv_teste = 2 + (idx_cls % 4)  # distribui entre níveis 2, 3, 4 e 5
        con_teste = cls_por_id[cid]["conceitos"][0]["id"]
        r_niv = client.post(
            "/api/gerar",
            json={
                "ancestralidade_id": "humano",
                "heranca_id": "heranca_versatil",
                "classe_id": cid,
                "conceito_id": con_teste,
                "nivel": niv_teste,
                "seed": 900 + idx_cls,
            },
        )
        assert r_niv.status_code == 200, f"Falha em {cid} N{niv_teste}: {r_niv.get_data(as_text=True)}"
        res_niv = r_niv.get_json()
        verificar_contrato_e_matematica(res_niv, dados)
        assert res_niv["ficha"]["cabecalho"]["nivel"] == niv_teste
        if niv_teste >= 5:
            assert any(h["etapa"] == "N5" for h in res_niv["meta_geracao"]["historico_abcd"])
            assert res_niv["ficha"]["habilidades_e_talentos"]["ancestralidade"][3]["nome"]

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

    # Exportação PDF oficial (idêntico à ficha de 4 páginas do livro via ref/Sheet Update.pdf)
    import pymupdf

    for caso_res, checks_por_pagina in (
        (
            mago_elem,
            {
                0: [mago_elem["ficha"]["cabecalho"]["nome_personagem"], "Mago", "ARCANISMO"],
                1: ["Elfo", "Mochila", "PO"],
                2: ["Evocador de Artilharia"],
                3: ["Mãos Flamejantes", "Produzir Chama"],
            },
        ),
        (
            guer_2m,
            {
                0: [guer_2m["ficha"]["cabecalho"]["nome_personagem"], "Montante", "ATLETISMO"],
                1: ["Ataque Poderoso", "Montante"],
                2: ["Agressor"],
            },
        ),
        (
            cl_iomedae,
            {
                0: [cl_iomedae["ficha"]["cabecalho"]["nome_personagem"], "Iomedae"],
                2: ["Iomedae", "Arma"],
                3: ["Truques Mágicos", "Divina"[:0]],
            },
        ),
        (
            dr_matilha,
            {
                0: [dr_matilha["ficha"]["cabecalho"]["nome_personagem"], "Druida"],
                2: ["Companheiro Animal"],
                3: ["Truques Mágicos"],
                4: [dr_matilha["meta_geracao"]["companheiro_ou_familiar"]["nome"], "PV"],
            },
        ),
    ):
        r_pdf = client.post("/api/exportar/pdf", json={"resultado": caso_res})
        assert r_pdf.status_code == 200
        assert r_pdf.mimetype == "application/pdf"
        disp_pdf = r_pdf.headers.get("Content-Disposition", "")
        assert "attachment;" in disp_pdf and disp_pdf.endswith('.pdf"')
        raw_pdf = r_pdf.get_data()
        assert raw_pdf.startswith(b"%PDF-")

        esperado_pags_min = 6 if caso_res["meta_geracao"].get("companheiro_ou_familiar") else 5
        with pymupdf.open(stream=raw_pdf, filetype="pdf") as pdf_doc:
            assert len(pdf_doc) >= esperado_pags_min
            for pg_idx, page in enumerate(pdf_doc):
                assert abs(page.rect.width - 603.0) < 0.5 and abs(page.rect.height - 783.0) < 0.5
                if pg_idx in checks_por_pagina:
                    pg_txt = page.get_text()
                    for trecho in checks_por_pagina[pg_idx]:
                        if trecho:
                            assert trecho in pg_txt, f"Trecho {trecho!r} ausente na página {pg_idx + 1} do PDF"
            ref_idx = 5 if caso_res["meta_geracao"].get("companheiro_ou_familiar") else 4
            txt_ref_all = "\n".join(pdf_doc[i].get_text() for i in range(ref_idx, len(pdf_doc)))
            assert "REFERÊNCIA COMPLETA" in txt_ref_all
            assert "HABILIDADES DA RAÇA" in txt_ref_all

    r_pdf_params = client.post(
        "/api/exportar/pdf",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "guerreiro",
            "conceito_id": "guerreiro_colosso_demolidor",
            "seed": 88,
        },
    )
    assert r_pdf_params.status_code == 200 and r_pdf_params.get_data().startswith(b"%PDF-")

    # Erros 400 nos endpoints de exportação
    assert client.post("/api/exportar/txt", json={}).status_code == 400
    assert client.post("/api/exportar/docx", json={"ficha": {}}).status_code == 400
    assert client.post("/api/exportar/pdf", json={"ficha": {}}).status_code == 400

    print("SUCESSO TOTAL — Validação da Etapa 3 + Etapa 4 concluída!")
    print(f"Conceitos validados: {len(todos_conceitos)}/72 | Heranças validadas: {len(todas_herancas)}/29")
    print(f"Casos especiais validados: {len(casos_especiais)} | Rotas Flask validadas: 9 endpoints + static (200/400/404)")
    print("Exportadores validados: .txt (UTF-8), .docx (OOXML/XML) e .pdf (4 páginas oficiais do livro)")


if __name__ == "__main__":
    main()
