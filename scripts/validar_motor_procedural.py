"""Suíte de validação completa do Motor Procedural PF2E e rotas Flask (Etapa 3)."""

from __future__ import annotations

import json
import sys
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
    assert opcoes["total_conceitos"] == 38

    # ------------------------------------------------------------------
    # 1. Determinismo com seed fixa e variação com seeds distintas
    # ------------------------------------------------------------------
    a1 = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_espada_duas_maos", seed=42)
    a2 = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_espada_duas_maos", seed=42)
    assert a1 == a2, "Mesma seed deve gerar ficha exatamente idêntica"

    b1 = gerar_personagem("elfo", "elfo_vidente", "mago", "mago_elementalista", seed=101)
    b2 = gerar_personagem("elfo", "elfo_vidente", "mago", "mago_elementalista", seed=202)
    assert b1["ficha"]["cabecalho"]["nome_personagem"] != b2["ficha"]["cabecalho"]["nome_personagem"] or (
        b1["meta_geracao"]["biografia_id"] != b2["meta_geracao"]["biografia_id"]
    )

    # ------------------------------------------------------------------
    # 2. Cobertura total de 38 conceitos + todas as 29 heranças
    # ------------------------------------------------------------------
    todas_herancas = [
        (anc["id"], her["id"])
        for anc in dados.ancestralidades.values()
        for her in anc["herancas"]
    ]
    assert len(todas_herancas) == 29

    todos_conceitos = list(dados.conceitos.values())
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
        ("anao", "anao_da_forja", "campeao", "campeao_paladino_baluarte", "soldado"),
        ("elfo", "elfo_vidente", "guerreiro", "guerreiro_arqueiro_precisao", "batedor"),
        ("gnomo", "gnomo_tocado_pelas_fadas", "bardo", "bardo_maestro_inspirador", "animador"),
        ("gnomo", "gnomo_manancial", "clerigo", "clerigo_sacerdote_curandeiro", "acolito"),
        ("goblin", "goblin_inquebravel", "barbaro", "barbaro_draconico_duas_maos", None),
        ("goblin", "goblin_dentes_de_navalha", "ladino", "ladino_ladrao_acrobata", None),
        ("humano", "meio_elfo", "patrulheiro", "patrulheiro_arqueiro_precisao", None),
        ("humano", "meio_orc", "guerreiro", "guerreiro_espada_duas_maos", None),
        ("humano", "heranca_perita", "mago", "mago_elementalista", None),
        ("humano", "heranca_versatil", "ladino", "ladino_malandro_social", None),
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
    # 4. Sinergia temática dos conceitos solicitados pelo usuário
    # ------------------------------------------------------------------
    mago_elem = gerar_personagem("elfo", "elfo_das_florestas", "mago", "mago_elementalista", seed=77, dados=dados)
    nomes_magias_mago = {
        normalizar(m["nome"])
        for m in mago_elem["ficha"]["conjuracao"]["truques_magicos"] + mago_elem["ficha"]["conjuracao"]["magias"]
        if m["nome"]
    }
    assert mago_elem["ficha"]["conjuracao"]["tradicoes_marcadas"]["arcana"] is True
    assert "produzir chama" in nomes_magias_mago
    assert "maos flamejantes" in nomes_magias_mago

    guer_2m = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_espada_duas_maos", seed=88, dados=dados)
    assert guer_2m["ficha"]["golpes_corpo_a_corpo"][0]["arma"] == "Montante"
    assert guer_2m["ficha"]["habilidades_e_talentos"]["classe"][2]["nome"] == "Ataque Poderoso"

    # ------------------------------------------------------------------
    # 5. Rotas Flask via test_client()
    # ------------------------------------------------------------------
    client = app.test_client()

    r_idx = client.get("/")
    assert r_idx.status_code == 200
    assert "Pathfinder 2E" in r_idx.get_data(as_text=True)

    r_saude = client.get("/api/saude")
    assert r_saude.status_code == 200
    assert r_saude.get_json()["conceitos"] == 38

    r_opcoes = client.get("/api/opcoes")
    assert r_opcoes.status_code == 200
    assert len(r_opcoes.get_json()["classes"]) == 12

    r_her = client.get("/api/ancestralidades/elfo/herancas")
    assert r_her.status_code == 200 and len(r_her.get_json()["herancas"]) == 5
    assert client.get("/api/ancestralidades/inexistente/herancas").status_code == 404

    r_con = client.get("/api/classes/mago/conceitos")
    assert r_con.status_code == 200 and len(r_con.get_json()["conceitos"]) == 4
    assert client.get("/api/classes/inexistente/conceitos").status_code == 404

    r_ok = client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "mago",
            "conceito_id": "mago_elementalista",
            "seed": 12345,
        },
    )
    assert r_ok.status_code == 200
    payload_ok = r_ok.get_json()
    verificar_contrato_e_matematica(payload_ok, dados)

    # Erros controlados (400)
    assert client.post("/api/gerar", json={"ancestralidade_id": "humano"}).status_code == 400
    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "mago",
            "conceito_id": "guerreiro_espada_duas_maos",
        },
    ).status_code == 400
    assert client.post(
        "/api/gerar",
        json={
            "ancestralidade_id": "humano",
            "heranca_id": "heranca_versatil",
            "classe_id": "mago",
            "conceito_id": "mago_elementalista",
            "nivel": 2,
        },
    ).status_code == 400

    print("SUCESSO TOTAL — Validação da Etapa 3 concluída!")
    print(f"Conceitos validados: {len(todos_conceitos)}/38 | Heranças validadas: {len(todas_herancas)}/29")
    print(f"Casos especiais validados: {len(casos_especiais)} | Rotas Flask validadas: 6 endpoints (200/400/404)")


if __name__ == "__main__":
    main()
