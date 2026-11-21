"""Suíte unitária dedicada de casos de borda matemáticos e regras PF2E (Etapa 5)."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from motor import ErroValidacao, carregar_dados, gerar_personagem
from motor.biografia_pericias import calcular_idiomas
from motor.combate_matematica import calcular_matematica_final
from motor.equipamentos import calcular_proficiencias_combate, comprar_equipamentos
from motor.regras_atributos import calcular_atributos
from motor.talentos import selecionar_talentos
from motor.util import normalizar


def test_ca_limite_destreza_e_sem_armadura() -> None:
    db = carregar_dados()
    # DES 18 (+4) com Cota de Malha (Lim Des +1, CA +4): deve capar DES em +1
    ficha_base = gerar_personagem("elfo", "elfo_vidente", "guerreiro", "guerreiro_atirador_elite", seed=5, dados=db)
    # Montar cenário direto com Cota de Malha + DES 18 (+4)
    mods = {"for": 2, "des": 4, "con": 1, "int": 0, "sab": 1, "car": 0}
    vals = {"for": 14, "des": 18, "con": 12, "int": 10, "sab": 12, "car": 10}
    anc = db.ancestralidades["humano"]
    her = db.heranca("humano", "heranca_versatil")
    cls = db.classes["guerreiro"]
    sub = db.subclasse("guerreiro", "arqueiro")
    con = db.conceitos["guerreiro_atirador_elite"]
    bio = db.biografias["batedor"]
    profs = calcular_proficiencias_combate(cls, sub)

    cota_malha = db.armaduras["cota_de_malha"]  # bonus_ca=4, lim_des=1
    equip_malha = {
        "armadura": cota_malha,
        "escudo": None,
        "armas": [],
        "itens_vestidos": [],
        "itens_preparados": [],
        "outros_itens": [],
        "volume_total": 2.0,
        "volume_sobrecarregado": 7,
        "volume_maximo": 12,
        "esta_sobrecarregado": False,
        "gasto_pc": 600,
        "saldo_pc": 900,
        "riqueza": {"pc": 0, "pp": 0, "po": 9, "pl": 0},
    }
    from copy import deepcopy
    ficha_m = deepcopy(db.estrutura_ficha["modelo_ficha_vazia"])
    tal_res = selecionar_talentos(db, anc, her, bio, cls, sub, con, {"acrobatismo": "treinado"}, "acrobatismo")
    calcular_matematica_final(
        ficha_m, db, anc, her, cls, sub,
        {"valores": vals, "modificadores": mods, "atributo_chave": "des"},
        {"graus": {"acrobatismo": "treinado"}, "saberes": {"saber_1": {"especializacao": "Tática", "grau": "treinado"}, "saber_2": {"especializacao": "", "grau": "destreinado"}}},
        ["Comum", "Élfico"], tal_res, profs, equip_malha, nivel=1,
    )
    assert ficha_m["classe_armadura"]["des_ou_limite"] == 1
    assert ficha_m["classe_armadura"]["total"] == 10 + 1 + 3 + 4  # 18

    # Sem armadura com DES +4: sem limite -> total 17
    equip_sem = dict(equip_malha, armadura=db.armaduras["nenhuma_armadura"])
    ficha_s = deepcopy(db.estrutura_ficha["modelo_ficha_vazia"])
    calcular_matematica_final(
        ficha_s, db, anc, her, cls, sub,
        {"valores": vals, "modificadores": mods, "atributo_chave": "des"},
        {"graus": {"acrobatismo": "treinado"}, "saberes": {"saber_1": {"especializacao": "Tática", "grau": "treinado"}, "saber_2": {"especializacao": "", "grau": "destreinado"}}},
        ["Comum", "Élfico"], tal_res, profs, equip_sem, nivel=1,
    )
    assert ficha_s["classe_armadura"]["des_ou_limite"] == 4
    assert ficha_s["classe_armadura"]["total"] == 10 + 4 + 3 + 0  # 17


def test_penalidade_armadura_barulhenta_flexivel_e_ferro_desimpedido() -> None:
    db = carregar_dados()
    # Cota de malha: forca_minima=16, penalidade_testes=-2, tracos=['Barulhenta', 'Flexível'], pen_vel=-1.5
    cota = db.armaduras["cota_de_malha"]
    cls = db.classes["campeao"]
    sub = db.subclasse("campeao", "paladino")
    con = db.conceitos["campeao_cruzado_vingador"]
    bio = db.biografias["soldado"]
    profs = calcular_proficiencias_combate(cls, sub)
    equip = {
        "armadura": cota, "escudo": None, "armas": [],
        "itens_vestidos": [], "itens_preparados": [], "outros_itens": [],
        "volume_total": 2.0, "volume_sobrecarregado": 7, "volume_maximo": 12,
        "esta_sobrecarregado": False, "gasto_pc": 600, "saldo_pc": 900,
        "riqueza": {"pc": 0, "pp": 0, "po": 9, "pl": 0},
    }
    from copy import deepcopy

    # Caso 1: FOR 18 >= 16 -> Barulhenta ainda penaliza Furtividade (-2), mas Atletismo/Acrobatismo = 0
    anc_h = db.ancestralidades["humano"]
    her_h = db.heranca("humano", "heranca_versatil")
    tal_h = selecionar_talentos(db, anc_h, her_h, bio, cls, sub, con, {"atletismo": "treinado"}, "intimidacao")
    f1 = deepcopy(db.estrutura_ficha["modelo_ficha_vazia"])
    calcular_matematica_final(
        f1, db, anc_h, her_h, cls, sub,
        {"valores": {"for": 18, "des": 12, "con": 14, "int": 10, "sab": 10, "car": 14}, "modificadores": {"for": 4, "des": 1, "con": 2, "int": 0, "sab": 0, "car": 2}, "atributo_chave": "for"},
        {"graus": {"atletismo": "treinado"}, "saberes": {"saber_1": {"especializacao": "Guerra", "grau": "treinado"}, "saber_2": {"especializacao": "", "grau": "destreinado"}}},
        ["Comum", "Enânico"], tal_h, profs, equip, nivel=1,
    )
    furt1 = next(p for p in f1["pericias"] if p["id"] == "furtividade")
    atl1 = next(p for p in f1["pericias"] if p["id"] == "atletismo")
    assert furt1["penalidade_armadura"] == -2
    assert atl1["penalidade_armadura"] == 0
    assert f1["velocidade"]["metros"] == 7.5  # -1.5 + 1.5 = 0

    # Caso 2: FOR 12 < 16 com Cota de Malha (Flexível) -> Ladrão/Acrobatismo/Atletismo = 0, Furtividade/Ladroagem = -2, Vel -1.5m
    f2 = deepcopy(db.estrutura_ficha["modelo_ficha_vazia"])
    calcular_matematica_final(
        f2, db, anc_h, her_h, cls, sub,
        {"valores": {"for": 12, "des": 14, "con": 14, "int": 10, "sab": 10, "car": 16}, "modificadores": {"for": 1, "des": 2, "con": 2, "int": 0, "sab": 0, "car": 3}, "atributo_chave": "for"},
        {"graus": {"atletismo": "treinado"}, "saberes": {"saber_1": {"especializacao": "Guerra", "grau": "treinado"}, "saber_2": {"especializacao": "", "grau": "destreinado"}}},
        ["Comum", "Enânico"], tal_h, profs, equip, nivel=1,
    )
    assert next(p for p in f2["pericias"] if p["id"] == "atletismo")["penalidade_armadura"] == 0
    assert next(p for p in f2["pericias"] if p["id"] == "acrobatismo")["penalidade_armadura"] == 0
    assert next(p for p in f2["pericias"] if p["id"] == "ladroagem")["penalidade_armadura"] == -2
    assert f2["velocidade"]["metros"] == 6.0

    # Caso 3: Anão com Ferro Desimpedido ignora penalidade de velocidade mesmo com FOR < 16
    anc_a = db.ancestralidades["anao"]
    her_a = db.heranca("anao", "anao_da_forja")
    tal_a = dict(tal_h)
    tal_a["efeitos"] = dict(tal_h["efeitos"], ferro_desimpedido=True)
    f3 = deepcopy(db.estrutura_ficha["modelo_ficha_vazia"])
    calcular_matematica_final(
        f3, db, anc_a, her_a, cls, sub,
        {"valores": {"for": 12, "des": 14, "con": 16, "int": 10, "sab": 12, "car": 12}, "modificadores": {"for": 1, "des": 2, "con": 3, "int": 0, "sab": 1, "car": 1}, "atributo_chave": "for"},
        {"graus": {"atletismo": "treinado"}, "saberes": {"saber_1": {"especializacao": "Guerra", "grau": "treinado"}, "saber_2": {"especializacao": "", "grau": "destreinado"}}},
        ["Comum", "Enânico"], tal_a, profs, equip, nivel=1,
    )
    assert f3["velocidade"]["metros"] == 6.0  # base do anão intacta


def test_mochila_sobrecarga_e_carregador_robusto() -> None:
    db = carregar_dados()
    # Gnomo Bardo (FOR 8 = mod -1 => limite sem penalidade 4): com isenção da mochila (Kit 1 Vol), não sobrecarrega
    g = gerar_personagem("gnomo", "gnomo_tocado_pelas_fadas", "bardo", "bardo_comandante_inspirador", seed=42, dados=db)
    inv_g = g["ficha"]["inventario"]
    assert inv_g["volume_total"] <= inv_g["volume_sobrecarregado"]
    assert g["meta_geracao"]["observacoes_combate"]["esta_sobrecarregado"] is False

    # Operário concede Carregador Robusto -> +2 em sobrecarga e máximo
    op = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor", biografia_id="operario", seed=42, dados=db)
    mod_for = op["ficha"]["atributos"]["for"]["modificador"]
    assert op["ficha"]["inventario"]["volume_sobrecarregado"] == 5 + mod_for + 2
    assert op["ficha"]["inventario"]["volume_maximo"] == 10 + mod_for + 2

    # Sobrecarga real impõe -3m respeitando mínimo 1,5m
    from copy import deepcopy
    f_sob = deepcopy(db.estrutura_ficha["modelo_ficha_vazia"])
    anc = db.ancestralidades["anao"]  # vel 6.0
    her = db.heranca("anao", "anao_das_rochas")
    cls = db.classes["guerreiro"]
    sub = db.subclasse("guerreiro", "agressor")
    tal = selecionar_talentos(db, anc, her, db.biografias["soldado"], cls, sub, db.conceitos["guerreiro_colosso_demolidor"], {"atletismo": "treinado"})
    equip_sob = {
        "armadura": db.armaduras["nenhuma_armadura"], "escudo": None, "armas": [],
        "itens_vestidos": [], "itens_preparados": [], "outros_itens": [],
        "volume_total": 12.0, "volume_sobrecarregado": 9, "volume_maximo": 14,
        "esta_sobrecarregado": True, "gasto_pc": 0, "saldo_pc": 1500,
        "riqueza": {"pc": 0, "pp": 0, "po": 15, "pl": 0},
    }
    calcular_matematica_final(
        f_sob, db, anc, her, cls, sub,
        {"valores": {"for": 18, "des": 12, "con": 14, "int": 10, "sab": 12, "car": 10}, "modificadores": {"for": 4, "des": 1, "con": 2, "int": 0, "sab": 1, "car": 0}, "atributo_chave": "for"},
        {"graus": {}, "saberes": {"saber_1": {"especializacao": "Guerra", "grau": "treinado"}, "saber_2": {"especializacao": "", "grau": "destreinado"}}},
        ["Comum", "Enânico"], tal, calcular_proficiencias_combate(cls, sub), equip_sob, nivel=1,
    )
    assert f_sob["velocidade"]["metros"] == 3.0  # 6.0 - 3.0


def test_armas_acuidade_ladrao_propulsiva_posturas_e_anao_mago() -> None:
    db = carregar_dados()
    # Ladino Ladrão soma DES no dano com arma de acuidade
    lad = gerar_personagem("humano", "heranca_versatil", "ladino", "ladino_sombra_silenciosa", seed=10, dados=db)
    golpe_lad = lad["ficha"]["golpes_corpo_a_corpo"][0]
    assert golpe_lad["ataque"]["mod_atributo"] == lad["ficha"]["atributos"]["des"]["modificador"]
    assert golpe_lad["dano"]["for"] == lad["ficha"]["atributos"]["des"]["modificador"]

    # Propulsiva com FOR positiva (+3 -> +1) vs negativa (-1 -> -1)
    from motor.combate_matematica import _preencher_golpe
    arco_comp = db.armas["arco_longo_composto"]
    slot_pos = {"arma": "", "ataque": {}, "dano": {}}
    _preencher_golpe(slot_pos, arco_comp, True, "especialista", 1, {"for": 3, "des": 4}, "guerreiro", "arqueiro")
    assert slot_pos["dano"]["especial"] == 1
    slot_neg = {"arma": "", "ataque": {}, "dano": {}}
    _preencher_golpe(slot_neg, arco_comp, True, "especialista", 1, {"for": -1, "des": 4}, "guerreiro", "arqueiro")
    assert slot_neg["dano"]["especial"] == -1

    # Monge com Postura de 1º nível exibe golpe da postura e Punho 1d6
    monk = gerar_personagem("humano", "heranca_perita", "monge", "monge_artista_posturas", seed=11, dados=db)
    nomes_cc_m = [g["arma"] for g in monk["ficha"]["golpes_corpo_a_corpo"] if g["arma"]]
    assert any("Postura" in n for n in nomes_cc_m)
    assert any(g["arma"] == "Punho" and g["dano"]["dados"] == "1d6" for g in monk["ficha"]["golpes_corpo_a_corpo"])

    # Anão Mago recebe Adaga de Clã no inventário, mas NÃO nos golpes como Destreinado
    mago_anao = gerar_personagem("anao", "anao_das_rochas", "mago", "mago_evocador_artilharia", seed=7, dados=db)
    assert any("Adaga de clã" in it["nome"] for it in mago_anao["ficha"]["inventario"]["itens_vestidos"])
    for g in mago_anao["ficha"]["golpes_corpo_a_corpo"] + mago_anao["ficha"]["golpes_a_distancia"]:
        if g["arma"]:
            assert g["ataque"]["grau_proficiencia"] != "destreinado"


def test_idiomas_humano_mago_grimorio_e_regras_especificas() -> None:
    db = carregar_dados()
    # Humano Guerreiro (INT 10, mod 0): deve ter 2 idiomas reais (Comum + 1)
    h_g = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor", seed=15, dados=db)
    assert len(h_g["ficha"]["idiomas"]) == 2
    assert all("qualquer" not in normalizar(i) for i in h_g["ficha"]["idiomas"])

    # Humano Mago (INT 18, mod +4): deve ter 6 idiomas reais (Comum + 1 + 4) e zero texto descritivo
    h_m = gerar_personagem("humano", "heranca_versatil", "mago", "mago_evocador_artilharia", seed=15, dados=db)
    assert len(h_m["ficha"]["idiomas"]) == 6
    assert all("qualquer" not in normalizar(i) and len(i) <= 25 for i in h_m["ficha"]["idiomas"])

    # Mago Especialista tem 6 magias N1 no grimório inicial (5 comuns + 1 da escola)
    magias_n1 = [m["nome"] for m in h_m["ficha"]["conjuracao"]["magias"] if m["nome"]]
    assert len(magias_n1) == 6

    # Duro de Matar + Vitalidade (regras_específicas.json)
    for s in range(1, 30):
        r = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_muralha_aco", seed=s, dados=db)
        nomes_t = [x["nome"] for cat in r["ficha"]["habilidades_e_talentos"].values() for x in cat if x.get("nome")]
        if "Duro de Matar" in nomes_t:
            assert r["meta_geracao"]["limite_morrendo"] == 5
            break


def test_acoes_classe_pagina3_e_zero_descarte_talentos() -> None:
    db = carregar_dados()
    # Ações de classe na Pág. 3
    g = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_muralha_aco", seed=1, dados=db)
    reac_g = [a["nome"] for a in g["ficha"]["acoes_livres_e_reacoes"] if a["nome"]]
    assert "Ataque de Oportunidade" in reac_g

    b = gerar_personagem("humano", "heranca_versatil", "barbaro", "barbaro_guerreiro_draconico", seed=1, dados=db)
    ac_b = [a["nome"] for a in b["ficha"]["acoes_e_atividades"] if a["nome"]]
    assert "Fúria" in ac_b

    m = gerar_personagem("humano", "heranca_versatil", "monge", "monge_artista_posturas", seed=1, dados=db)
    ac_m = [a["nome"] for a in m["ficha"]["acoes_e_atividades"] if a["nome"]]
    assert "Rajada de Golpes" in ac_m

    p = gerar_personagem("humano", "heranca_versatil", "patrulheiro", "patrulheiro_metralhadora_flechas", seed=1, dados=db)
    ac_p = [a["nome"] for a in p["ficha"]["acoes_e_atividades"] if a["nome"]]
    assert "Caçar Presa" in ac_p

    alq = gerar_personagem("humano", "heranca_versatil", "alquimista", "alquimista_aberracao_mutante", seed=1, dados=db)
    ac_a = [a["nome"] for a in alq["ficha"]["acoes_e_atividades"] + alq["ficha"]["acoes_livres_e_reacoes"] if a["nome"]]
    assert "Alquimia Rápida" in ac_a and "Retroatividade Mutagênica" in ac_a

    # Zero descarte quando Humano Versátil + Ladino + Ambição Natural gera 3 talentos extras
    for s in range(1, 30):
        lad = gerar_personagem("humano", "heranca_versatil", "ladino", "ladino_sombra_silenciosa", seed=s, dados=db)
        hab = lad["ficha"]["habilidades_e_talentos"]
        if hab["ancestralidade"][2]["nome"] == "Ambição Natural":
            todos_preenchidos = [
                x["nome"]
                for k in ("pericia", "gerais", "classe", "bonus")
                for x in hab[k]
                if x.get("nome") and x["nome"] != "—"
            ]
            # Esquiva Ágil + Descobridor de Armadilha + 2 características + 1 perícia bio + 1 perícia ladino N1 + 1 geral versátil >= 7
            assert len(todos_preenchidos) >= 7, f"Talento descartado: {todos_preenchidos}"
            break


def test_divindades_reais_e_companheiros_familiares() -> None:
    db = carregar_dados()
    # Capelão da Guerra com Pharasma (Adaga, Arma Simples) -> ganha Simplicidade Mortal (Adaga 1d6!) e Perícia Medicina
    cl_ph = gerar_personagem("humano", "heranca_perita", "clerigo", "clerigo_arauto_guerra", divindade_id="pharasma", seed=3, dados=db)
    assert "Pharasma" in cl_ph["ficha"]["cabecalho"]["divindade"]
    assert next(p for p in cl_ph["ficha"]["pericias"] if p["id"] == "medicina")["grau_proficiencia"] == "treinado"
    adaga_g = next(g for g in cl_ph["ficha"]["golpes_corpo_a_corpo"] if g["arma"] == "Adaga")
    assert adaga_g["dano"]["dados"] == "1d6"  # Simplicidade Mortal elevou 1d4 -> 1d6

    # Capelão da Guerra com Iomedae (Espada Longa, Arma Marcial) -> equipa Espada Longa (1d8), sem Simplicidade Mortal
    cl_io = gerar_personagem("humano", "heranca_perita", "clerigo", "clerigo_arauto_guerra", divindade_id="iomedae", seed=3, dados=db)
    esp_g = next(g for g in cl_io["ficha"]["golpes_corpo_a_corpo"] if g["arma"] == "Espada longa")
    assert esp_g["ataque"]["grau_proficiencia"] == "treinado"
    assert esp_g["dano"]["dados"] == "1d8"

    # Divindade incompatível com Causa do Campeão deve falhar com ErroValidacao
    try:
        gerar_personagem("humano", "heranca_versatil", "campeao", "campeao_cruzado_vingador", divindade_id="urgathoa", seed=1, dados=db)
        raise AssertionError("Deveria rejeitar Urgathoa para Paladino OB")
    except ErroValidacao:
        pass

    # Companheiro Animal (Druida Senhor da Matilha e Patrulheiro Mestre das Feras)
    dr_comp = gerar_personagem("elfo", "elfo_das_florestas", "druida", "druida_senhor_matilha", seed=9, dados=db)
    comp = dr_comp["meta_geracao"]["companheiro_ou_familiar"]
    assert comp is not None and comp["categoria"] == "Companheiro Animal"
    assert comp["pv_max"] > 0 and comp["ca"] >= 15 and len(comp["ataques"]) >= 1

    # Familiar Aprimorado (Mago Ilusionista -> 3 habilidades diárias e reação Drenar Familiar)
    mg_fam = gerar_personagem("elfo", "elfo_vidente", "mago", "mago_ilusionista_enganador", seed=9, dados=db)
    fam = mg_fam["meta_geracao"]["companheiro_ou_familiar"]
    assert fam is not None and fam["categoria"] == "Familiar"
    assert fam["habilidades_diarias_max"] == 3
    assert len(fam["habilidades_selecionadas"]) == 3
    reac_m = [a["nome"] for a in mg_fam["ficha"]["acoes_livres_e_reacoes"] if a["nome"]]
    assert "Drenar Familiar" in reac_m


def main() -> None:
    test_ca_limite_destreza_e_sem_armadura()
    test_penalidade_armadura_barulhenta_flexivel_e_ferro_desimpedido()
    test_mochila_sobrecarga_e_carregador_robusto()
    test_armas_acuidade_ladrao_propulsiva_posturas_e_anao_mago()
    test_idiomas_humano_mago_grimorio_e_regras_especificas()
    test_acoes_classe_pagina3_e_zero_descarte_talentos()
    test_divindades_reais_e_companheiros_familiares()
    print("SUCESSO TOTAL — Todos os testes de casos de borda PF2E passaram!")


if __name__ == "__main__":
    main()
