"""Suíte unitária dedicada de casos de borda matemáticos e regras PF2E (Etapa 5)."""

from __future__ import annotations

import io
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from motor import (
    ErroValidacao,
    carregar_acesso_mestre,
    carregar_dados,
    divindades_compativeis_conceito,
    gerar_personagem,
    listar_opcoes_regras_casa,
    validar_senha_regras_casa,
)
from motor.biografia_pericias import calcular_idiomas, calcular_pericias
from motor.combate_matematica import calcular_matematica_final
from motor.companheiros import gerar_companheiro_ou_familiar
from motor.equipamentos import calcular_proficiencias_combate, comprar_equipamentos, grau_arma
from motor.exportacao import exportar_ficha_docx, exportar_ficha_pdf, exportar_ficha_txt
from motor.magias import gerar_conjuracao
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


def test_divindade_obrigatoria_vs_opcional_e_compatibilidade() -> None:
    db = carregar_dados()
    # Clérigo e Campeão devem rejeitar "" e "nenhuma"
    for cls_id, con_id in (
        ("clerigo", "clerigo_hospitalario_sagrado"),
        ("campeao", "campeao_cruzado_vingador"),
    ):
        for val_inv in ("", "nenhuma"):
            try:
                gerar_personagem("humano", "heranca_versatil", cls_id, con_id, divindade_id=val_inv, seed=1, dados=db)
                raise AssertionError(f"{cls_id} deveria rejeitar divindade_id={val_inv!r}")
            except ErroValidacao:
                pass

    # Classes opcionais (Guerreiro e Mago) sem divindade com "nenhuma", "" ou None
    for cls_id, con_id in (
        ("guerreiro", "guerreiro_colosso_demolidor"),
        ("mago", "mago_evocador_artilharia"),
    ):
        for val_opt in ("nenhuma", "", None):
            r = gerar_personagem("humano", "heranca_versatil", cls_id, con_id, divindade_id=val_opt, seed=4, dados=db)
            assert r["ficha"]["cabecalho"]["divindade"] == ""
            assert r["meta_geracao"]["divindade_id"] is None
            assert r["meta_geracao"]["divindade_obrigatoria"] is False

    # Guerreiro com divindade "aleatoria" -> recebe uma das 20 sem poderes de Clérigo/Campeão
    g_rand = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor", divindade_id="aleatoria", seed=8, dados=db
    )
    assert g_rand["meta_geracao"]["divindade_id"] in db.divindades
    assert g_rand["meta_geracao"]["divindade_procedural"] is True
    assert g_rand["ficha"]["cabecalho"]["divindade"] != ""

    # Guerreiro com divindade manual Iomedae -> cabeçalho e detalhes preenchidos, procedural=False
    g_iom = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor", divindade_id="iomedae", seed=8, dados=db
    )
    assert "Iomedae" in g_iom["ficha"]["cabecalho"]["divindade"]
    assert g_iom["meta_geracao"]["divindade_detalhes"]["id"] == "iomedae"
    assert g_iom["meta_geracao"]["divindade_procedural"] is False

    # Campeão multi-causa com Desna -> nunca sorteia Paladino (OB), sempre Redentor (NB) ou Libertador (CB)
    for s in range(1, 21):
        camp_d = gerar_personagem(
            "humano", "heranca_versatil", "campeao", "campeao_cavaleiro_montado", divindade_id="desna", seed=s, dados=db
        )
        assert camp_d["meta_geracao"]["subclasse_oficial_id"] in {"redentor", "libertador"}

    # Campeão multi-causa com Urgathoa -> incompatível com Paladino/Redentor/Libertador
    try:
        gerar_personagem(
            "humano", "heranca_versatil", "campeao", "campeao_cavaleiro_montado", divindade_id="urgathoa", seed=1, dados=db
        )
        raise AssertionError("Campeão multi-causa deveria rejeitar Urgathoa")
    except ErroValidacao:
        pass

    # Arauto da Guerra com Urgathoa (só Ferir) -> funciona, equipa Segadeira, usa Fonte de Ferimento e não pega Mãos Curandeiras
    cl_urg = gerar_personagem(
        "humano", "heranca_perita", "clerigo", "clerigo_arauto_guerra", divindade_id="urgathoa", seed=5, dados=db
    )
    assert cl_urg["meta_geracao"]["divindade_detalhes"]["fonte_divina"] == "ferimento"
    assert any(g["arma"] == "Segadeira" for g in cl_urg["ficha"]["golpes_corpo_a_corpo"])
    assert any("Ferir (Fonte Divina" in (m["nome"] or "") for m in cl_urg["ficha"]["conjuracao"]["magias"])
    nomes_tal_cl = [x["nome"] for cat in cl_urg["ficha"]["habilidades_e_talentos"].values() for x in cat if x.get("nome")]
    assert "Mãos Curandeiras" not in nomes_tal_cl

    # Hospitalário Sagrado com Urgathoa -> rejeita com ErroValidacao
    try:
        gerar_personagem(
            "humano", "heranca_perita", "clerigo", "clerigo_hospitalario_sagrado", divindade_id="urgathoa", seed=5, dados=db
        )
        raise AssertionError("Hospitalário Sagrado deveria rejeitar Urgathoa")
    except ErroValidacao:
        pass


def test_revisao_geral_etapa_23() -> None:
    db = carregar_dados()

    # 1. Zero conflitos de Arma de 2 mãos + Escudo (Druida Senhor da Matilha, Campeão Montado e Capelão c/ 20 divindades)
    for anc_id, her_id, cls_id, con_id, div_id in (
        ("humano", "heranca_versatil", "druida", "druida_senhor_matilha", None),
        ("humano", "heranca_versatil", "campeao", "campeao_cavaleiro_montado", "iomedae"),
        ("humano", "heranca_versatil", "clerigo", "clerigo_arauto_guerra", "gorum"),
        ("humano", "heranca_versatil", "clerigo", "clerigo_arauto_guerra", "urgathoa"),
        ("humano", "heranca_versatil", "clerigo", "clerigo_arauto_guerra", "shelyn"),
    ):
        r = gerar_personagem(anc_id, her_id, cls_id, con_id, divindade_id=div_id, seed=7, dados=db)
        if r["ficha"]["classe_armadura"]["escudo"]["nome"]:
            for g in r["ficha"]["golpes_corpo_a_corpo"]:
                if g["arma"]:
                    w_obj = next((w for w in db.armas.values() if w["nome"] == g["arma"]), None)
                    assert not (w_obj and str(w_obj.get("maos")) == "2"), f"2M+Escudo em {con_id}/{div_id}: {g['arma']}"

    # Gorum / Urgathoa equipam Montante / Segadeira sem escudo
    r_gor = gerar_personagem("humano", "heranca_versatil", "clerigo", "clerigo_arauto_guerra", divindade_id="gorum", seed=7, dados=db)
    assert any(g["arma"] == "Montante" for g in r_gor["ficha"]["golpes_corpo_a_corpo"])
    assert r_gor["ficha"]["classe_armadura"]["escudo"]["nome"] == ""

    # 2. Campeão com Arma Deificada (Pharasma Adaga 1d4->1d6; Abadar Besta leve 1d8->1d10)
    camp_ph = gerar_personagem("humano", "heranca_versatil", "campeao", "campeao_bastiao_impenetravel", divindade_id="pharasma", seed=7, dados=db)
    adaga_c = next(g for g in camp_ph["ficha"]["golpes_corpo_a_corpo"] if g["arma"] == "Adaga")
    assert adaga_c["dano"]["dados"] == "1d6"
    camp_ab = gerar_personagem("humano", "heranca_versatil", "campeao", "campeao_cruzado_vingador", divindade_id="abadar", seed=7, dados=db)
    besta_c = next(g for g in camp_ab["ficha"]["golpes_a_distancia"] if g["arma"] == "Besta leve")
    assert besta_c["dano"]["dados"] == "1d10"

    # 3. Perspicácia Astuta eleva Percepção (ou salvamento) para especialista
    r_pa = gerar_personagem("humano", "heranca_versatil", "mago", "mago_arquimago_enciclopedico", seed=42, dados=db)
    assert r_pa["ficha"]["percepcao"]["grau_proficiencia"] == "especialista"

    # 4. Saber Ancestral concede 2 perícias + Saber 2 treinado
    per_res = calcular_pericias(
        db,
        db.ancestralidades["elfo"],
        db.heranca("elfo", "elfo_vidente"),
        db.biografias["estudioso"],
        db.classes["guerreiro"],
        None,
        db.conceitos["guerreiro_colosso_demolidor"],
        mod_int=0,
        pericias_ancestrais_fixas=["arcanismo", "natureza"],
        saber_ancestral=("Saber Élfico", "Talento Ancestral (Saber Élfico)"),
    )
    assert per_res["graus"]["arcanismo"] == "treinado" and per_res["graus"]["natureza"] == "treinado"
    assert per_res["saberes"]["saber_2"]["especializacao"] == "Saber Élfico"
    assert per_res["saberes"]["saber_2"]["grau"] == "treinado"

    # 5. Familiaridade com Armas Ancestrais e Armamento Não Convencional
    profs_elf_mago = calcular_proficiencias_combate(
        db.classes["mago"], db.subclasse("mago", "evocacao"), efeitos_talentos={"talento_ancestral_id": "familiaridade_com_armas_elficas"}
    )
    assert grau_arma(db.armas["arco_longo"], profs_elf_mago["armas"]) == "treinado"
    profs_elf_bardo = calcular_proficiencias_combate(
        db.classes["bardo"], None, efeitos_talentos={"talento_ancestral_id": "familiaridade_com_armas_elficas"}
    )
    assert grau_arma(db.armas["lamina_curva_elfica"], profs_elf_bardo["armas"]) == "treinado"
    profs_unc = calcular_proficiencias_combate(
        db.classes["guerreiro"], None, efeitos_talentos={"talento_ancestral_id": "armamento_nao_convencional"}
    )
    assert grau_arma(db.armas["katana"], profs_unc["armas"]) == "especialista"

    # 6. Magia Extraterrena, Truque Mágico Adaptado, Cúmplice Animal e Visão Órquica
    conj_ext = gerar_conjuracao(
        db, db.heranca("elfo", "elfo_das_florestas"), db.classes["guerreiro"], None,
        db.conceitos["guerreiro_colosso_demolidor"], {"for": 4, "des": 2, "con": 2, "int": 0, "sab": 1, "car": 0},
        [], talento_ancestral_id="magia_extraterrena",
    )
    assert len(conj_ext["magias_inatas"]) == 1 and conj_ext["tradicao"] == "arcana"

    conj_adap = gerar_conjuracao(
        db, db.heranca("humano", "heranca_versatil"), db.classes["mago"], db.subclasse("mago", "evocacao"),
        db.conceitos["mago_evocador_artilharia"], {"for": 0, "des": 2, "con": 1, "int": 4, "sab": 1, "car": 0},
        [], talento_ancestral_id="truque_magico_adaptado",
    )
    assert "arcana" not in conj_adap["truques"][-1].get("tradicoes", [])

    r_base = gerar_personagem(
        "gnomo", db.ancestralidades["gnomo"]["herancas"][0]["id"], "guerreiro", "guerreiro_colosso_demolidor", seed=1, dados=db
    )
    mods_base = {k: v["modificador"] for k, v in r_base["ficha"]["atributos"].items()}
    fam_cump = gerar_companheiro_ou_familiar(
        db, db.classes["guerreiro"], None, db.conceitos["guerreiro_colosso_demolidor"],
        [], r_base["ficha"], mods_base, talento_ancestral_id="cumplice_animal",
    )
    assert fam_cump is not None and fam_cump["categoria"] == "Familiar"

    # 7. Arquivo regras_especificas.json em ASCII + magias01/02 sem hífens quebrados nem tokens em inglês
    assert (RAIZ_PROJETO / "dados" / "regras_especificas.json").exists()
    assert not (RAIZ_PROJETO / "dados" / "regras_específicas.json").exists()
    for fn in ("magias01.json", "magias02.json"):
        dados_mg = json.loads((RAIZ_PROJETO / "dados" / fn).read_text(encoding="utf-8"))
        for grupo in (dados_mg["magias"], (dados_mg.get("magias_de_foco") or {}).get("lista", [])):
            txt_grp = json.dumps(grupo, ensure_ascii=False)
            assert "[one-action]" not in txt_grp and "[two-actions]" not in txt_grp and "[three-actions]" not in txt_grp and "[free-action]" not in txt_grp
        for m in dados_mg["magias"]:
            rl = m.get("resumo_lista") or ""
            for bad in ("divi-na", "ener-gia", "cir-cunstâncias", "efei-tos", "em-purra", "inde-tectável", "tempora-riamente", "de-sarmados"):
                assert bad not in rl, f"{bad!r} residual em {fn}:{m['id']}"

    # 8. Exportadores .txt e .docx: Subclasse no cabeçalho, pluralização e Preparada + anotações
    r_barb = gerar_personagem("humano", "heranca_versatil", "barbaro", "barbaro_guerreiro_draconico", seed=1, dados=db)
    txt_b = exportar_ficha_txt(r_barb)
    assert "Subclasse  :" in txt_b

    r_cl = gerar_personagem("humano", "heranca_versatil", "clerigo", "clerigo_arauto_guerra", divindade_id="iomedae", seed=2026, dados=db)
    docx_bytes = exportar_ficha_docx(r_cl)
    with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as zf:
        doc_txt = "".join(ET.fromstring(zf.read("word/document.xml")).itertext())
        assert "Subclasse PF2E" in doc_txt
        assert "Preparada •" in doc_txt


def test_aleatorio_7_campos_e_bonus_equipamentos() -> None:
    db = carregar_dados()

    # 1. Todos os 7 campos em aleatório e determinismo por seed
    r1 = gerar_personagem(
        "aleatorio", "aleatorio", "aleatorio", "aleatorio",
        biografia_id="aleatoria", divindade_id="aleatoria", nivel="aleatorio", seed=31415, dados=db,
    )
    r2 = gerar_personagem(
        "aleatorio", "aleatorio", "aleatorio", "aleatorio",
        biografia_id="aleatoria", divindade_id="aleatoria", nivel="aleatorio", seed=31415, dados=db,
    )
    assert r1 == r2
    assert r1["ficha"]["cabecalho"]["nivel"] == 1

    # Variando seeds com classe aleatória + divindade "nenhuma" nunca sorteia Clérigo/Campeão
    classes_vistas = set()
    for s in range(1, 25):
        r_no_div = gerar_personagem(
            "aleatorio", "aleatorio", "aleatorio", "aleatorio",
            biografia_id="aleatoria", divindade_id="nenhuma", nivel="aleatorio", seed=s, dados=db,
        )
        cls_id = r_no_div["meta_geracao"]["classe_id"]
        classes_vistas.add(cls_id)
        assert cls_id not in {"clerigo", "campeao"}
        assert r_no_div["ficha"]["cabecalho"]["divindade"] == ""
    assert len(classes_vistas) >= 3

    # Classe/Conceito aleatórios com divindade explícita incompatível para alguns conceitos (ex: Urgathoa) sempre geram válidos
    for s in range(1, 15):
        r_urg = gerar_personagem(
            "aleatorio", "aleatorio", "aleatorio", "aleatorio",
            biografia_id="aleatoria", divindade_id="urgathoa", nivel="aleatorio", seed=s, dados=db,
        )
        assert r_urg["meta_geracao"]["divindade_id"] == "urgathoa"

    # 2. Bônus de armadura na CA e nos itens de equipamentos, além de dano/bônus/quantidades
    r_guerr = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_muralha_aco", seed=9, dados=db)
    arm_res = r_guerr["meta_geracao"]["armadura_equipada_resumo"]
    assert "(+" in arm_res and "CA" in arm_res and "Lim DES +" in arm_res
    vestidos = [it["nome"] for it in r_guerr["ficha"]["inventario"]["itens_vestidos"]]
    outros = [it["nome"] for it in r_guerr["ficha"]["inventario"]["outros_itens"]]
    assert arm_res in vestidos
    assert any("Escudo" in n and "CA" in n and "Dureza" in n for n in vestidos)
    assert any("(1d" in n for n in vestidos)
    assert any("Kit de aventureiro" in n and "mochila" in n for n in outros)

    # Munições e Reagentes Alquímicos exibem quantidade clara sem duplicar "×"
    r_arq = gerar_personagem("elfo", "elfo_vidente", "guerreiro", "guerreiro_atirador_elite", seed=9, dados=db)
    vest_arq = [it["nome"] for it in r_arq["ficha"]["inventario"]["itens_vestidos"]]
    assert any("Flechas (Qtd: 20)" in n for n in vest_arq)
    txt_arq = exportar_ficha_txt(r_arq)
    assert r_arq["meta_geracao"]["armadura_equipada_resumo"] in txt_arq
    assert "Flechas (Qtd: 20) ×20" not in txt_arq

    r_alq = gerar_personagem("humano", "heranca_versatil", "alquimista", "alquimista_artilheiro_linha_frente", seed=9, dados=db)
    prep_alq = [it["nome"] for it in r_alq["ficha"]["inventario"]["itens_preparados"]]
    assert any("Reagentes Infundidos (Qtd:" in n for n in prep_alq)


def test_exportar_pdf_oficial_4_paginas() -> None:
    import pymupdf

    db = carregar_dados()
    # Clérigo com Arma Deificada, Armadura com bônus na CA, Ações e Magias em todas as 4 páginas
    cl = gerar_personagem(
        "humano", "heranca_versatil", "clerigo", "clerigo_arauto_guerra",
        divindade_id="iomedae", seed=17, nome_personagem="Valeros Teste PDF", dados=db,
    )
    pdf_bytes = exportar_ficha_pdf(cl)
    assert pdf_bytes.startswith(b"%PDF-")

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        assert len(doc) == 4
        txt_p1 = doc[0].get_text()
        txt_p2 = doc[1].get_text()
        txt_p3 = doc[2].get_text()
        txt_p4 = doc[3].get_text()

    assert "Valeros Teste PDF" in txt_p1
    assert "Iomedae" in txt_p1
    assert "CA)" in txt_p1 or cl["meta_geracao"]["armadura_equipada"] in txt_p1
    assert "Idiomas" in txt_p1
    assert cl["ficha"]["idiomas"][0] in txt_p1
    assert cl["ficha"]["habilidades_e_talentos"]["classe"][0]["nome"] in txt_p2
    assert "Divindade: Iomedae" in txt_p3
    assert cl["ficha"]["conjuracao"]["tradicoes_marcadas"]["divina"] is True
    assert cl["ficha"]["conjuracao"]["truques_magicos"][0]["nome"] in txt_p4
    assert cl["ficha"]["conjuracao"]["magias"][0]["nome"] in txt_p4


def test_escolhas_atributos_manual_procedural_aleatorio() -> None:
    db = carregar_dados()

    # 1. Trava da Etapa A (ancestralidade): proíbe repetir atributo já alterado (melhoria fixa ou penalidade)
    # Ex.: Anão (+2 CON, +2 SAB, -2 CAR) não pode aplicar livre da Etapa A em CON, SAB ou CAR;
    # a melhoria de CAR pode ser aplicada normalmente nas etapas seguintes (B, C ou D).
    for attr_bloqueado_a in ("con", "sab", "car"):
        try:
            gerar_personagem(
                "anao", "anao_da_forja", "guerreiro", "guerreiro_colosso_demolidor",
                escolhas_atributos={"ancestralidade_livres": [attr_bloqueado_a]}, seed=1, dados=db,
            )
            raise AssertionError(f"Anão não deveria aceitar '{attr_bloqueado_a}' no bônus livre da Etapa A")
        except ErroValidacao:
            pass

    anao_compensado_d = gerar_personagem(
        "anao", "anao_da_forja", "guerreiro", "guerreiro_colosso_demolidor",
        biografia_id="estudioso",
        escolhas_atributos={
            "ancestralidade_livres": ["for"],
            "biografia_restrito": "sab",
            "biografia_livre": "car",
            "livres_nivel_1": ["for", "con", "des", "car"],
        },
        seed=1,
        dados=db,
    )
    assert anao_compensado_d["meta_geracao"]["escolhas_atributos"]["ancestralidade_livres"] == ["for"]
    # CAR: 10 - 2 (Etapa A) + 2 (Etapa B) + 2 (Etapa D) = 12
    assert anao_compensado_d["ficha"]["atributos"]["car"]["valor"] == 12
    assert anao_compensado_d["meta_geracao"]["historico_abcd"][0]["deltas"].get("car", 0) == -2

    # E no modo procedural/aleatório da Etapa A, o defeito também nunca recebe o livre da Etapa A
    elfo_auto = gerar_personagem(
        "elfo", "elfo_artico", "mago", "mago_evocador_artilharia",
        escolhas_atributos={"ancestralidade_livres": ["aleatorio"]}, seed=3, dados=db,
    )
    assert elfo_auto["meta_geracao"]["escolhas_atributos"]["ancestralidade_livres"][0] not in {"des", "int", "con"}

    # 2. Biografia mista: livre manual em uma das 2 opções restritas + restrito procedural evita colisão automática
    est = db.biografias["estudioso"]  # opcoes: ["int", "sab"]
    r_bio_mix = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        biografia_id="estudioso",
        escolhas_atributos={"biografia_restrito": "procedural", "biografia_livre": "int"},
        seed=4,
        dados=db,
    )
    esc_m = r_bio_mix["meta_geracao"]["escolhas_atributos"]
    assert esc_m["biografia_livre"] == "int"
    assert esc_m["biografia_restrito"] == "sab"

    # 3. 4 bônus livres aleatórios preservam 4 atributos distintos e são determinísticos por seed
    r_rnd1 = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        escolhas_atributos={
            "ancestralidade_livres": ["aleatorio", "aleatorio"],
            "biografia_restrito": "aleatorio",
            "biografia_livre": "aleatorio",
            "livres_nivel_1": ["aleatorio", "aleatorio", "aleatorio", "aleatorio"],
        },
        seed=909,
        dados=db,
    )
    r_rnd2 = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        escolhas_atributos={
            "ancestralidade_livres": ["aleatorio", "aleatorio"],
            "biografia_restrito": "aleatorio",
            "biografia_livre": "aleatorio",
            "livres_nivel_1": ["aleatorio", "aleatorio", "aleatorio", "aleatorio"],
        },
        seed=909,
        dados=db,
    )
    assert r_rnd1 == r_rnd2
    esc_r = r_rnd1["meta_geracao"]["escolhas_atributos"]
    assert len(set(esc_r["ancestralidade_livres"])) == 2
    assert esc_r["biografia_restrito"] != esc_r["biografia_livre"]
    assert len(set(esc_r["livres_nivel_1"])) == 4

    # 4. Escolha manual de classe_chave e preservação estrita frente ao conceito divergente
    lad_car = gerar_personagem(
        "humano", "heranca_versatil", "ladino", "ladino_sabotador_venenoso",
        escolhas_atributos={"classe_chave": "car"}, seed=10, dados=db,
    )
    assert lad_car["meta_geracao"]["atributo_chave"] == "car"
    assert lad_car["meta_geracao"]["subclasse_oficial_id"] == "malandro"

    # Guerreiro Colosso Demolidor (conceito foca FOR/CON/DES) com todos atributos livres manuais em INT/SAB/CAR/DES
    guerr_div = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        biografia_id="estudioso",
        escolhas_atributos={
            "ancestralidade_livres": ["car", "int"],
            "biografia_restrito": "int",
            "biografia_livre": "sab",
            "classe_chave": "des",
            "livres_nivel_1": ["des", "int", "sab", "car"],
        },
        seed=42,
        dados=db,
    )
    atb_div = guerr_div["ficha"]["atributos"]
    assert atb_div["for"]["valor"] == 10
    assert atb_div["des"]["valor"] == 14
    assert atb_div["con"]["valor"] == 10
    assert atb_div["int"]["valor"] == 16
    assert atb_div["sab"]["valor"] == 14
    assert atb_div["car"]["valor"] == 14
    assert guerr_div["meta_geracao"]["atributo_chave"] == "des"
    assert guerr_div["meta_geracao"]["subclasse_oficial_id"] == "agressor"

    # Misto: 2 livres manuais divergentes + 2 livres procedurais guiados pelo conceito (sem sobrescrever os manuais)
    guerr_misto = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        biografia_id="estudioso",
        escolhas_atributos={
            "ancestralidade_livres": ["car", "procedural"],
            "biografia_restrito": "int",
            "biografia_livre": "procedural",
            "classe_chave": "procedural",
            "livres_nivel_1": ["car", "sab", "procedural", "procedural"],
        },
        seed=42,
        dados=db,
    )
    esc_mix = guerr_misto["meta_geracao"]["escolhas_atributos"]
    assert esc_mix["ancestralidade_livres"] == ["car", "for"]
    assert esc_mix["biografia_restrito"] == "int"
    assert esc_mix["biografia_livre"] == "for"
    assert esc_mix["classe_chave"] == "for"
    assert esc_mix["livres_nivel_1"] == ["car", "sab", "for", "con"]

    # Biografia procedural com biografia_restrito manual em atributo não-padrão seleciona biografia compatível
    mago_car_bio = gerar_personagem(
        "elfo", "elfo_vidente", "mago", "mago_evocador_artilharia",
        biografia_id="procedural",
        escolhas_atributos={"biografia_restrito": "car"},
        seed=15,
        dados=db,
    )
    assert mago_car_bio["meta_geracao"]["escolhas_atributos"]["biografia_restrito"] == "car"

    # 5. Validações de erro para combinações ilegais PF2E
    for esc_inv in (
        {"ancestralidade_livres": ["for", "for"]},  # Humano duplicado
        {"biografia_restrito": "for"},              # Fora das opções de Estudioso (int/sab)
        {"biografia_restrito": "int", "biografia_livre": "int"},
        {"classe_chave": "int"},                    # Guerreiro só aceita FOR ou DES
        {"livres_nivel_1": ["for", "des", "con", "for"]},
    ):
        try:
            gerar_personagem(
                "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
                biografia_id="estudioso", escolhas_atributos=esc_inv, seed=1, dados=db,
            )
            raise AssertionError(f"Deveria falhar com ErroValidacao para {esc_inv!r}")
        except ErroValidacao:
            pass


def test_compra_manual_e_hibrida_equipamentos() -> None:
    db = carregar_dados()

    # 1. Compra manual completa: armadura + armas + escudo + variados com cálculo exato de PP/PO/PC e Volume
    pat_loja = gerar_personagem(
        "elfo", "elfo_vidente", "patrulheiro", "patrulheiro_atirador_precisao",
        escolhas_equipamentos={
            "armadura_id": "couro_batido",                # 300 pc (Vol 1)
            "escudo_id": "nenhum",                        # 0 pc
            "armas_corpo_a_corpo_ids": ["espada_curta"],  # 90 pc (Vol L)
            "armas_distancia_ids": ["arco_curto"],        # 300 pc (Vol 1)
            "equipamentos_variados": [
                {"id": "kit_de_aventureiro", "quantidade": 1},  # 70 pc (Vol 1 -> isento 2 Vol)
                {"id": "flechas", "quantidade": 2},             # 20 pc (20 flechas, Vol 2L)
            ],
        },
        seed=12,
        dados=db,
    )
    assert pat_loja["meta_geracao"]["gasto_pc"] == 780
    assert pat_loja["meta_geracao"]["saldo_pc"] == 720
    assert pat_loja["ficha"]["inventario"]["riqueza"] == {"pc": 0, "pp": 2, "po": 7, "pl": 0}
    assert any("Flechas (Qtd: 20)" in it["nome"] for it in pat_loja["ficha"]["inventario"]["itens_vestidos"])
    assert pat_loja["ficha"]["golpes_a_distancia"][0]["arma"] == "Arco curto"

    # 2. Compra híbrida: escolhe manualmente Armadura e Arma 2M, deixando Variados em Procedural
    guerr_hib = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        escolhas_equipamentos={
            "armadura_id": "cota_de_malha",          # 600 pc
            "armas_corpo_a_corpo_ids": ["montante"], # 200 pc
        },
        seed=8,
        dados=db,
    )
    # Montante manual é 2M -> escudo procedural não é comprado; distância/variados procedurais compram Azagaia + Kit de Aventureiro + itens de viagem dentro dos 90% (saldo >= 150 pc)
    assert 880 <= guerr_hib["meta_geracao"]["gasto_pc"] <= 1350
    assert guerr_hib["meta_geracao"]["saldo_pc"] >= 150
    assert guerr_hib["meta_geracao"]["observacoes_combate"]["esta_sobrecarregado"] is False
    assert guerr_hib["ficha"]["classe_armadura"]["escudo"]["nome"] == ""
    assert any("Kit de aventureiro" in it["nome"] for it in guerr_hib["ficha"]["inventario"]["outros_itens"])

    # 3. Orçamento excedido ou item alquímico bloqueado levantam ErroValidacao
    for esc_inv in (
        {"armadura_id": "armadura_completa"},
        {"equipamentos_variados": [{"id": "kit_de_aventureiro", "quantidade": 30}]},
        {"equipamentos_variados": ["elixir_da_vida_menor"]},
    ):
        try:
            gerar_personagem(
                "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
                escolhas_equipamentos=esc_inv, seed=1, dados=db,
            )
            raise AssertionError(f"Deveria falhar com ErroValidacao para {esc_inv!r}")
        except ErroValidacao:
            pass

    # 4. Anátema de Druida no back-end: bloqueia armadura/escudo de metal manual e aceita não-metal
    for esc_dru_inv in (
        {"armadura_id": "camisao_de_malha"},
        {"armadura_id": "cota_de_malha"},
        {"escudo_id": "escudo_de_aco"},
        {"escudo_id": "broquel"},
    ):
        try:
            gerar_personagem(
                "elfo", "elfo_das_florestas", "druida", "druida_furia_elementos",
                escolhas_equipamentos=esc_dru_inv, seed=2, dados=db,
            )
            raise AssertionError(f"Druida deveria rejeitar item de metal {esc_dru_inv!r}")
        except ErroValidacao:
            pass

    dru_ok = gerar_personagem(
        "elfo", "elfo_das_florestas", "druida", "druida_furia_elementos",
        escolhas_equipamentos={"armadura_id": "gibao_de_peles", "escudo_id": "escudo_de_madeira"},
        seed=2,
        dados=db,
    )
    assert dru_ok["meta_geracao"]["armadura_equipada"] == "Gibão de peles"
    assert dru_ok["ficha"]["classe_armadura"]["escudo"]["nome"] == "Escudo de madeira"


def test_curadoria_e_selecao_manual_talentos() -> None:
    db = carregar_dados()

    # 1. Humano Versátil + Treinamento Geral libera exatamente 2 Talentos Gerais distintos no 1º nível
    guerr_2g = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        escolhas_talentos={
            "modo": "personalizado",
            "ancestralidade_id": "treinamento_geral",
            "classe_ids": ["ataque_poderoso"],
            "gerais_ids": ["iniciativa_incrivel", "veloz"],
        },
        seed=17,
        dados=db,
    )
    esc_t = guerr_2g["meta_geracao"]["escolhas_talentos"]
    assert esc_t["slots_disponiveis"] == {"ancestralidade": 1, "classe": 1, "pericia": 0, "gerais": 2}
    assert esc_t["gerais_ids"] == ["iniciativa_incrivel", "veloz"]
    assert guerr_2g["ficha"]["velocidade"]["metros"] == 9.0  # 7.5m + 1.5m (Veloz)
    nomes_hab_g = [
        x["nome"]
        for cat in guerr_2g["ficha"]["habilidades_e_talentos"].values()
        for x in cat
        if x.get("nome") and x["nome"] != "—"
    ]
    assert "Treinamento Geral" in nomes_hab_g and "Ataque Poderoso" in nomes_hab_g
    assert "Iniciativa Incrível" in nomes_hab_g and "Veloz" in nomes_hab_g

    # 2. Vínculo dinâmico: Ambição Natural em Clérigo (sem slot base N1) libera 1 talento de classe N1 manual
    cler_amb = gerar_personagem(
        "humano", "heranca_perita", "clerigo", "clerigo_hospitalario_sagrado",
        divindade_id="sarenrae",
        escolhas_talentos={
            "modo": "personalizado",
            "ancestralidade_id": "ambicao_natural",
            "classe_ids": ["maos_curandeiras"],
        },
        seed=22,
        dados=db,
    )
    assert cler_amb["meta_geracao"]["escolhas_talentos"]["slots_disponiveis"]["classe"] == 1
    assert cler_amb["meta_geracao"]["escolhas_talentos"]["classe_ids"] == ["maos_curandeiras"]
    hab_c = cler_amb["ficha"]["habilidades_e_talentos"]
    nomes_cls_c = [x["nome"] for x in hab_c["classe"] if x.get("nome")]
    nomes_bon_c = [x["nome"] for x in hab_c["bonus"] if x.get("nome")]
    assert "Iniciado no Domínio" in nomes_cls_c and "Mãos Curandeiras" in nomes_bon_c

    # 3. Bloqueios estritos de nível/classe/ancestralidade/duplicidade devem levantar ErroValidacao
    # Clérigo sem Ambição Natural tentando pegar talento de classe no 1º nível
    try:
        gerar_personagem(
            "elfo", "elfo_vidente", "clerigo", "clerigo_hospitalario_sagrado",
            divindade_id="desna",
            escolhas_talentos={"modo": "personalizado", "classe_ids": ["maos_curandeiras"]},
            seed=1,
            dados=db,
        )
        raise AssertionError("Clérigo sem Ambição Natural deveria bloquear talento de classe N1 manual")
    except ErroValidacao:
        pass

    # Combinações bloqueadas em Anão Guerreiro e Humano Versátil Guerreiro
    for esc_inv in (
        {"modo": "personalizado", "gerais_ids": ["bloqueio_com_escudo"]},  # Guerreiro já possui automático
        {"modo": "personalizado", "pericia_ids": ["certeza"]},             # Só Ladino libera perícia extra N1
        {"modo": "personalizado", "ancestralidade_id": "treinamento_geral", "gerais_ids": ["veloz", "veloz"]},
        {"modo": "personalizado", "ancestralidade_id": "elfo_ligeiro"},    # Talento de Elfo em Humano
        {"modo": "personalizado", "classe_ids": ["magia_de_alcance"]},     # Talento de outra classe
    ):
        try:
            gerar_personagem(
                "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
                escolhas_talentos=esc_inv, seed=1, dados=db,
            )
            raise AssertionError(f"Deveria falhar com ErroValidacao para {esc_inv!r}")
        except ErroValidacao:
            pass


def test_selecao_manual_e_regras_pericias() -> None:
    db = carregar_dados()

    # 1. Guerreiro Estudioso (INT 12 = +1) com escolha manual da perícia da Biografia, Classe e Livres
    # Vagas livres: Guerreiro (3) + INT (+1) = 4
    g_per = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        biografia_id="estudioso",
        escolhas_atributos={
            "ancestralidade_livres": ["for", "int"],
            "biografia_restrito": "sab",
            "biografia_livre": "con",
            "classe_chave": "for",
            "livres_nivel_1": ["for", "des", "con", "sab"],
        },
        escolhas_pericias={
            "modo": "personalizado",
            "pericia_biografia_id": "ocultismo",
            "pericia_classe_fixa_id": "acrobatismo",
            "pericias_livres": ["atletismo", "intimidacao", "medicina", "sobrevivencia"],
        },
        seed=31,
        dados=db,
    )
    esc_p = g_per["meta_geracao"]["escolhas_pericias"]
    assert esc_p["vagas_livres_total"] == 4
    assert esc_p["manuais_aplicadas"] == ["atletismo", "intimidacao", "medicina", "sobrevivencia"]
    treinadas_g = {p["id"] for p in g_per["ficha"]["pericias"] if p["grau_proficiencia"] == "treinado"}
    assert {"ocultismo", "acrobatismo", "atletismo", "intimidacao", "medicina", "sobrevivencia"}.issubset(treinadas_g)

    # 2. Sobreposição PF2E (Acólito dá Religião + Clérigo dá Religião => +1 vaga livre) + Shelyn (opção Performance)
    # Vagas livres: Clérigo (2) + INT (0) + Sobreposição (+1) = 3
    c_sob = gerar_personagem(
        "elfo", "elfo_vidente", "clerigo", "clerigo_hospitalario_sagrado",
        biografia_id="acolito",
        divindade_id="shelyn",
        escolhas_atributos={
            "ancestralidade_livres": ["sab"],
            "biografia_restrito": "sab",
            "biografia_livre": "car",
            "livres_nivel_1": ["des", "con", "sab", "car"],
        },
        escolhas_talentos={
            "modo": "personalizado",
            "ancestralidade_id": "elfo_ligeiro",
        },
        escolhas_pericias={
            "modo": "personalizado",
            "pericia_divindade_id": "performance",
            "pericias_livres": ["diplomacia", "medicina", "natureza", "sociedade"],
        },
        seed=5,
        dados=db,
    )
    # Elfo tem INT fixa +2 => mod_int = +1 => Clérigo (2) + INT (+1) + Sobreposição Religião (+1) = 4 vagas livres!
    assert "religiao" in c_sob["meta_geracao"]["escolhas_pericias"]["sobreposicoes"]
    assert c_sob["meta_geracao"]["escolhas_pericias"]["vagas_livres_total"] == 4

    # 3. Humano Herança Perita (+1) + Perícia Natural (+2) libera +3 vagas extras sem falso bloqueio
    # Bárbaro (3) + INT (0) + Herança Perita (+1) + Perícia Natural (+2) = 6 vagas livres
    b_ext = gerar_personagem(
        "humano", "heranca_perita", "barbaro", "barbaro_guerreiro_draconico",
        biografia_id="gladiador",
        escolhas_atributos={
            "ancestralidade_livres": ["for", "con"],
            "biografia_restrito": "for",
            "biografia_livre": "des",
            "livres_nivel_1": ["for", "des", "con", "sab"],
        },
        escolhas_talentos={"modo": "personalizado", "ancestralidade_id": "pericia_natural"},
        escolhas_pericias={
            "modo": "personalizado",
            "pericias_livres": ["acrobatismo", "diplomacia", "furtividade", "intimidacao", "medicina", "sobrevivencia"],
        },
        seed=9,
        dados=db,
    )
    assert b_ext["meta_geracao"]["escolhas_pericias"]["vagas_livres_total"] == 6
    assert len(b_ext["meta_geracao"]["escolhas_pericias"]["manuais_aplicadas"]) == 6

    # 4. Bloqueios estritos: exceder limite de vagas, duplicar perícia ou escolher opção inválida da classe/biografia
    for esc_inv in (
        {"modo": "personalizado", "pericias_livres": ["diplomacia", "intimidacao", "medicina", "sobrevivencia", "natureza"]},
        {"modo": "personalizado", "pericias_livres": ["diplomacia", "diplomacia"]},
        {"modo": "personalizado", "pericia_classe_fixa_id": "furtividade"},
        {"modo": "personalizado", "pericia_biografia_id": "atletismo"},
    ):
        try:
            gerar_personagem(
                "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
                biografia_id="estudioso",
                escolhas_atributos={
                    "ancestralidade_livres": ["for", "int"],
                    "biografia_restrito": "sab",
                    "biografia_livre": "con",
                    "classe_chave": "for",
                    "livres_nivel_1": ["for", "des", "con", "sab"],
                },
                escolhas_pericias=esc_inv,
                seed=1,
                dados=db,
            )
            raise AssertionError(f"Deveria falhar com ErroValidacao para {esc_inv!r}")
        except ErroValidacao:
            pass


def test_selecao_manual_e_aleatoria_magias() -> None:
    db = carregar_dados()

    # 1. Mago Especialista (Evocação): escolha manual de 5 truques + 6 magias N1 arcanas
    mg_man = gerar_personagem(
        "elfo", "elfo_vidente", "mago", "mago_evocador_artilharia",
        escolhas_magias={
            "modo": "personalizado",
            "truques_ids": ["detectar_magia", "escudo_mistico", "luz", "mao_mistica", "raio_de_gelo"],
            "magias_n1_ids": ["armadura_mistica", "misseis_magicos", "maos_flamejantes", "queda_suave", "salto", "alarme"],
        },
        seed=14,
        dados=db,
    )
    esc_m = mg_man["meta_geracao"]["escolhas_magias"]
    assert esc_m["modo"] == "personalizado"
    assert esc_m["tradicao"] == "arcana"
    assert len(esc_m["truques_manuais"]) == 5
    assert len(esc_m["magias_n1_manuais"]) == 6
    nomes_m1 = {m["nome"] for m in mg_man["ficha"]["conjuracao"]["magias"] if m.get("nome")}
    assert {"Armadura Mística", "Mísseis Mágicos", "Mãos Flamejantes", "Queda Suave", "Salto", "Alarme"}.issubset(nomes_m1)

    # 2. Feiticeiro Imperial: 1 truque fixo (Detectar Magia) + 4 livres, 1 N1 fixa (Mísseis Mágicos) + 2 livres
    ft_man = gerar_personagem(
        "humano", "heranca_versatil", "feiticeiro", "feiticeiro_arquimago_versatil",
        escolhas_magias={
            "modo": "personalizado",
            "truques_ids": ["escudo_mistico", "luz", "produzir_chama", "raio_de_gelo"],
            "magias_n1_ids": ["armadura_mistica", "maos_flamejantes"],
        },
        seed=7,
        dados=db,
    )
    nomes_ft_t = [t["nome"] for t in ft_man["ficha"]["conjuracao"]["truques_magicos"] if t.get("nome")]
    nomes_ft_1 = [m["nome"] for m in ft_man["ficha"]["conjuracao"]["magias"] if m.get("nome")]
    assert len(nomes_ft_t) == 5 and "Detectar Magia" in nomes_ft_t
    assert len(nomes_ft_1) == 3 and "Mísseis Mágicos" in nomes_ft_1

    # 3. Modo Aleatório respeita tradição e quantidade exata de truques/magias
    cl_rnd = gerar_personagem(
        "humano", "heranca_perita", "clerigo", "clerigo_hospitalario_sagrado",
        divindade_id="sarenrae",
        escolhas_magias={"modo": "aleatorio"},
        seed=33,
        dados=db,
    )
    assert cl_rnd["meta_geracao"]["escolhas_magias"]["modo"] == "aleatorio"
    assert len([t for t in cl_rnd["ficha"]["conjuracao"]["truques_magicos"] if t.get("nome")]) == 5

    # 4. Bloqueios estritos: tradição errada, nível errado, duplicata ou exceder vagas livres
    for esc_inv in (
        {"modo": "personalizado", "magias_n1_ids": ["curar"]},  # Curar não é arcana
        {"modo": "personalizado", "magias_n1_ids": ["bola_de_fogo"]},  # Bola de Fogo é 3º círculo
        {"modo": "personalizado", "truques_ids": ["luz", "luz"]},  # Duplicata
        {"modo": "personalizado", "truques_ids": ["detectar_magia", "escudo_mistico", "luz", "mao_mistica", "raio_de_gelo", "produzir_chama"]},  # 6 > 5
    ):
        try:
            gerar_personagem(
                "elfo", "elfo_vidente", "mago", "mago_evocador_artilharia",
                escolhas_magias=esc_inv, seed=1, dados=db,
            )
            raise AssertionError(f"Deveria falhar com ErroValidacao para {esc_inv!r}")
        except ErroValidacao:
            pass


def test_aderencia_procedural_nortes() -> None:
    db = carregar_dados()

    # 1. Magia inata de Herança (Gnomo Tocado pelas Fadas) e Truque Mágico Adaptado guiados pelo Conceito
    gn_fada = gerar_personagem(
        "gnomo", "gnomo_tocado_pelas_fadas", "druida", "druida_furia_elementos",
        seed=11,
        dados=db,
    )
    inatas_gn = gn_fada["ficha"]["conjuracao"]["magias_inatas"]
    assert inatas_gn and inatas_gn[0]["nome"] in {
        "Arco Elétrico", "Produzir Chama", "Raio de Gelo", "Emaranhapé", "Detectar Magia"
    }

    hum_adap = gerar_personagem(
        "humano", "heranca_versatil", "mago", "mago_evocador_artilharia",
        escolhas_talentos={"modo": "personalizado", "ancestralidade_id": "truque_magico_adaptado"},
        seed=11,
        dados=db,
    )
    truques_hum = [t["nome"] for t in hum_adap["ficha"]["conjuracao"]["truques_magicos"] if t.get("nome")]
    assert len(truques_hum) == 5

    # 2. Ferramentas temáticas da Biografia no modo procedural sem estourar 15 po
    p_med = gerar_personagem(
        "humano", "heranca_versatil", "monge", "monge_artista_posturas",
        biografia_id="medico_de_campo",
        seed=4,
        dados=db,
    )
    assert p_med["meta_geracao"]["saldo_pc"] >= 0
    assert any(
        "Ferramentas de curandeiro" in it["nome"]
        for it in p_med["ficha"]["inventario"]["itens_preparados"]
    )

    m_art = gerar_personagem(
        "humano", "heranca_versatil", "monge", "monge_artista_posturas",
        biografia_id="artesao",
        seed=4,
        dados=db,
    )
    assert 150 <= m_art["meta_geracao"]["saldo_pc"]
    assert any(
        "Ferramentas de artesão" in it["nome"]
        for it in m_art["ficha"]["inventario"]["itens_preparados"]
    )

    # 3. Arma de Familiaridade Ancestral priorizada quando compatível e proficiente
    an_arm = gerar_personagem(
        "anao", "anao_da_forja", "guerreiro", "guerreiro_colosso_demolidor",
        escolhas_talentos={"modo": "personalizado", "ancestralidade_id": "familiaridade_com_armas_enanicas"},
        seed=6,
        dados=db,
    )
    armas_an = [g["arma"] for g in an_arm["ficha"]["golpes_corpo_a_corpo"]]
    assert "Machado de guerra enânico" in armas_an
    assert an_arm["meta_geracao"]["saldo_pc"] >= 0

    el_arm = gerar_personagem(
        "elfo", "elfo_vidente", "guerreiro", "guerreiro_tempestade_laminas",
        escolhas_talentos={"modo": "personalizado", "ancestralidade_id": "familiaridade_com_armas_elficas"},
        seed=6,
        dados=db,
    )
    armas_el = [g["arma"] for g in el_arm["ficha"]["golpes_corpo_a_corpo"]]
    assert any(n in armas_el for n in ("Lâmina curva élfica", "Espada longa", "Rapieira"))

    # 4. Companheiro Animal e Familiar coerentes com Conceito, Ancestralidade e Biografia
    comp_an = gerar_personagem(
        "anao", "anao_das_rochas", "patrulheiro", "patrulheiro_mestre_feras",
        biografia_id="mineiro",
        escolhas_talentos={"modo": "personalizado", "classe_ids": ["companheiro_animal"]},
        seed=3,
        dados=db,
    )
    comp = comp_an["meta_geracao"]["companheiro_ou_familiar"]
    assert comp is not None and comp["id"] in {"texugo", "urso", "lobo"}

    fam_mar = gerar_personagem(
        "elfo", "elfo_vidente", "mago", "mago_ilusionista_enganador",
        biografia_id="marinheiro",
        seed=3,
        dados=db,
    )
    fam = fam_mar["meta_geracao"]["companheiro_ou_familiar"]
    assert fam is not None and fam["habilidades_diarias_max"] == 3
    fam_hids = {h["id"] for h in fam["habilidades_selecionadas"]}
    assert "fala" in fam_hids or "voador" in fam_hids or "anfibio" in fam_hids


def test_orcamento_90_peso_leve_e_viagem_procedural() -> None:
    db = carregar_dados()

    # 1. Procedural: reserva >= 10% em moedas (150 pc), gasta ~90% (<= 1350 pc), sem sobrecarga e com itens de viagem
    arquetipos = [
        ("gnomo", "gnomo_tocado_pelas_fadas", "mago", "mago_evocador_artilharia"),  # FOR baixa (mod -1 -> limite 4)
        ("humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor"),
        ("goblin", "goblin_inquebravel", "ladino", "ladino_sombra_silenciosa"),
        ("elfo", "elfo_vidente", "patrulheiro", "patrulheiro_atirador_precisao"),
        ("anao", "anao_da_forja", "clerigo", "clerigo_arauto_guerra"),
    ]
    for aid, hid, cid, conid in arquetipos:
        r = gerar_personagem(aid, hid, cid, conid, seed=77, dados=db)
        m = r["meta_geracao"]
        inv = r["ficha"]["inventario"]
        assert 1050 <= m["gasto_pc"] <= 1350, f"Gasto fora da faixa ~90% em {conid}: {m['gasto_pc']}"
        assert m["saldo_pc"] >= 150, f"Saldo abaixo de 10% em {conid}: {m['saldo_pc']}"
        assert m["observacoes_combate"]["esta_sobrecarregado"] is False
        assert inv["volume_total"] <= inv["volume_sobrecarregado"]

        nomes_inv = " | ".join(
            it["nome"] for it in (inv["itens_vestidos"] + inv["itens_preparados"] + inv["outros_itens"])
        )
        assert "Kit de aventureiro" in nomes_inv
        assert any(
            termo in nomes_inv
            for termo in ("Tenda individual", "Roupas de inverno", "Lanterna coberta", "Bússola", "Rações")
        )

    # 2. Manual: jogador pode gastar > 90% do orçamento e ficar sobrecarregado se desejar
    r_man = gerar_personagem(
        "gnomo", "gnomo_tocado_pelas_fadas", "mago", "mago_evocador_artilharia",
        escolhas_equipamentos={
            "modo": "personalizado",
            "armadura_id": "couro_batido",   # 300 pc (Vol 1)
            "escudo_id": "escudo_de_aco",    # 200 pc (Vol 1)
            "armas_corpo_a_corpo_ids": ["cajado"],  # 0 pc (Vol 1)
            "armas_distancia_ids": [],
            "equipamentos_variados": [
                {"id": "utensilios_de_cozinha", "quantidade": 3},   # 300 pc (Vol 6)
                {"id": "ferramentas_de_artesao", "quantidade": 1},  # 400 pc (Vol 2)
                {"id": "corda", "quantidade": 5},                   # 250 pc (Vol 5L)
            ],
        },
        seed=1,
        dados=db,
    )
    assert r_man["meta_geracao"]["gasto_pc"] == 1450
    assert r_man["meta_geracao"]["saldo_pc"] == 50
    assert r_man["meta_geracao"]["observacoes_combate"]["esta_sobrecarregado"] is True


def test_personalizacao_companheiro_familiar_e_perfil() -> None:
    db = carregar_dados()

    # 1. Companheiro Animal manual (tipo + nome) e Dados Biográficos (Pág. 3) em Druida Ordem dos Animais
    dru_comp = gerar_personagem(
        "humano", "heranca_versatil", "druida", "druida_senhor_matilha",
        escolhas_companheiro={"tipo_id": "urso", "nome": "Balgor"},
        escolhas_perfil={
            "tendencia": "ON",
            "idade": "28 anos",
            "genero_pronomes": "Ela/Dela",
            "aparencia": "Cicatriz no olho esquerdo e manto de peles.",
            "crencas": "Equilíbrio da floresta acima de tudo.",
            "aversoes": "Desmatamento e armaduras metálicas.",
        },
        seed=5,
        dados=db,
    )
    comp = dru_comp["meta_geracao"]["companheiro_ou_familiar"]
    assert comp is not None and comp["categoria"] == "Companheiro Animal"
    assert comp["id"] == "urso" and comp["nome"] == "Balgor (Urso)"
    assert dru_comp["ficha"]["cabecalho"]["tendencia"] == "ON"
    bio_f = dru_comp["ficha"]["perfil_e_campanha"]["dados_biograficos"]
    pers_f = dru_comp["ficha"]["perfil_e_campanha"]["personalidade"]
    assert bio_f["idade"] == "28 anos" and bio_f["genero_pronomes"] == "Ela/Dela"
    assert "Cicatriz" in bio_f["aparencia"]
    assert "Equilíbrio" in pers_f["crencas"] and "metálicas" in pers_f["aversoes"]

    # 2. Familiar manual em Mago Sintonização Aprimorada (3 habilidades válidas) + nome personalizado
    mg_fam = gerar_personagem(
        "elfo", "elfo_vidente", "mago", "mago_ilusionista_enganador",
        escolhas_companheiro={
            "nome": "Pip",
            "habilidades_ids": ["fala", "visao_no_escuro", "foco_de_familiar"],
        },
        escolhas_perfil={"tendencia": "CN"},
        seed=9,
        dados=db,
    )
    fam = mg_fam["meta_geracao"]["companheiro_ou_familiar"]
    assert fam is not None and fam["categoria"] == "Familiar"
    assert fam["nome"].startswith("Pip (")
    assert [h["id"] for h in fam["habilidades_selecionadas"]] == ["fala", "visao_no_escuro", "foco_de_familiar"]
    assert mg_fam["ficha"]["cabecalho"]["tendencia"] == "CN"

    # 3. Bloqueios estritos de tendência incompatível e pré-requisitos de habilidades de Familiar
    for kw_inv in (
        {"escolhas_perfil": {"tendencia": "CM"}},  # Druida exige neutro
    ):
        try:
            gerar_personagem("humano", "heranca_versatil", "druida", "druida_senhor_matilha", seed=1, dados=db, **kw_inv)
            raise AssertionError(f"Druida deveria rejeitar {kw_inv!r}")
        except ErroValidacao:
            pass

    for habs_inv in (
        ["bateria_de_magia"],  # Requer magias de 4º círculo (indisponível no N1)
        ["reagentes_extras"],  # Exclusiva de Alquimista
        ["assistente_de_laboratorio"],  # Sem Destreza Manual
    ):
        try:
            gerar_personagem(
                "elfo", "elfo_vidente", "mago", "mago_ilusionista_enganador",
                escolhas_companheiro={"habilidades_ids": habs_inv},
                seed=1,
                dados=db,
            )
            raise AssertionError(f"Mago deveria rejeitar habilidades {habs_inv!r}")
        except ErroValidacao:
            pass


    # 4. Catálogo completo de estatísticas N1 e Página 5 automática no PDF (5 pág. c/ companheiro ou familiar, 4 pág. sem)
    import pymupdf
    from motor.companheiros import listar_catalogo_companheiros_familiares

    cat_cf = listar_catalogo_companheiros_familiares(db)
    assert len(cat_cf["companheiros_animais"]) == 8
    for tipo_c in cat_cf["companheiros_animais"]:
        for chave in ("pv_n1", "ca_n1", "fortitude_n1", "reflexos_n1", "vontade_n1", "percepcao_n1", "modificadores_atributo", "pericias_n1", "ataques_n1", "manobra_avancada"):
            assert chave in tipo_c, f"Campo {chave!r} ausente no catálogo de {tipo_c['id']}"

    with pymupdf.open(stream=exportar_ficha_pdf(dru_comp), filetype="pdf") as doc_d:
        assert len(doc_d) == 5
        txt_p5_d = doc_d[4].get_text()
        assert "Balgor" in txt_p5_d and "Urso" in txt_p5_d and "PV" in txt_p5_d and "BENEFÍCIO DE SUPORTE" in txt_p5_d.upper()

    with pymupdf.open(stream=exportar_ficha_pdf(mg_fam), filetype="pdf") as doc_m:
        assert len(doc_m) == 5
        txt_p5_m = doc_m[4].get_text()
        assert "Pip" in txt_p5_m and "FAMILIAR" in txt_p5_m.upper() and "VISÃO NO ESCURO" in txt_p5_m.upper()

    guer_sem = gerar_personagem("humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor", seed=3, dados=db)
    with pymupdf.open(stream=exportar_ficha_pdf(guer_sem), filetype="pdf") as doc_g:
        assert len(doc_g) == 4


def test_regras_da_casa_peso_racao_e_oleo() -> None:
    db = carregar_dados()

    eq_teste = {
        "modo": "personalizado",
        "armadura_id": "nenhuma",
        "escudo_id": "nenhum",
        "armas_corpo_a_corpo_ids": [],
        "armas_distancia_ids": [],
        "equipamentos_variados": [
            {"id": "racoes_1_semana", "quantidade": 1},
            {"id": "oleo_meio_litro", "quantidade": 5},
            {"id": "corda", "quantidade": 4},
        ],
    }

    # 1. Padrão Oficial: Ração semanal (L=1), Óleo desprezível (0), Corda 4L -> 5 L / (10 L = 1 V) = 0 Vol + 5 L
    r_of = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        escolhas_equipamentos=eq_teste, seed=10, dados=db,
    )
    out_of = r_of["ficha"]["inventario"]["outros_itens"]
    assert r_of["meta_geracao"]["regras_casa"]["ativa"] is False
    assert r_of["meta_geracao"]["itens_leves_por_volume"] == 10
    assert r_of["ficha"]["inventario"]["volume_total"] == 0.0
    assert r_of["meta_geracao"]["volume_leves_soltos"] == 5
    assert any(it["nome"] == "Rações (1 semana)" and it["volume"] == "L" for it in out_of)
    assert any(it["nome"].startswith("Óleo (meio litro)") and it["volume"] == "—" for it in out_of)

    # 2. Regras da Casa completas: Ração unidade (1L) + Óleo 500ml (5L) + Corda (4L) = 10 L / (5 L = 1 V) = 2 Vol + 0 L
    r_rc = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        escolhas_equipamentos=eq_teste,
        escolhas_regras_casa={"modo": "regras_da_casa"},
        seed=10,
        dados=db,
    )
    out_rc = r_rc["ficha"]["inventario"]["outros_itens"]
    assert r_rc["meta_geracao"]["regras_casa"]["ativa"] is True
    assert r_rc["meta_geracao"]["itens_leves_por_volume"] == 5
    assert r_rc["ficha"]["inventario"]["volume_total"] == 2.0
    assert r_rc["meta_geracao"]["volume_leves_soltos"] == 0
    assert any(it["nome"] == "Ração (1 unidade)" and it["volume"] == "L" for it in out_rc)
    assert any(it["nome"].startswith("Óleo (meio litro)") and it["volume"] == "5L" for it in out_rc)
    assert "Regras da Casa Ativas:" not in r_rc["ficha"]["perfil_e_campanha"]["anotacoes_campanha"]["anotacoes"]

    # 6 frascos de óleo sozinhos na regra da casa => 6 L => 1 Vol + 1 L solto
    r_oleo6 = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        escolhas_equipamentos={
            "modo": "personalizado",
            "armadura_id": "nenhuma",
            "escudo_id": "nenhum",
            "armas_corpo_a_corpo_ids": [],
            "armas_distancia_ids": [],
            "equipamentos_variados": [{"id": "oleo_meio_litro", "quantidade": 6}],
        },
        escolhas_regras_casa={"modo": "regras_da_casa"},
        seed=10,
        dados=db,
    )
    assert r_oleo6["ficha"]["inventario"]["volume_total"] == 1.0
    assert r_oleo6["meta_geracao"]["volume_leves_soltos"] == 1

    # Kit de aventureiro procedural com regras da casa substitui texto de conteúdo
    r_kit_rc = gerar_personagem(
        "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
        escolhas_regras_casa={"modo": "regras_da_casa"},
        seed=10,
        dados=db,
    )
    kit_item = next(
        it for it in r_kit_rc["ficha"]["inventario"]["outros_itens"]
        if it["nome"].startswith("Kit de aventureiro")
    )
    assert "2 unidades de ração (Volume L cada)" in kit_item["nome"]
    assert "2 semanas de ração" not in kit_item["nome"]

    # 3. Garante que BaseDados oficial em cache nunca foi mutada pelas regras da casa
    assert db.itens_gerais["racoes_1_semana"]["nome"] == "Rações (1 semana)"
    assert db.itens_gerais["oleo_meio_litro"]["volume"] == "—"
    assert "2 semanas de ração" in db.itens_gerais["kit_de_aventureiro"]["conteudo"]

    # 4. Modo personalizado removido / modo inexistente deve levantar ErroValidacao
    for modo_inv in ("personalizado", "regra_falsa"):
        try:
            gerar_personagem(
                "humano", "heranca_versatil", "guerreiro", "guerreiro_colosso_demolidor",
                escolhas_regras_casa={"modo": modo_inv},
                seed=1,
                dados=db,
            )
            raise AssertionError(f"Deveria falhar com ErroValidacao para modo '{modo_inv}'")
        except ErroValidacao:
            pass

    # 5. Arquivo de controle de senha e padrão "Regras da Casa"
    arq_acesso = RAIZ_PROJETO / "dados_houserules" / "acesso_mestre.json"
    assert arq_acesso.exists(), "Arquivo dados_houserules/acesso_mestre.json ausente"
    acesso = carregar_acesso_mestre()
    assert acesso["senha"] == "9930"
    assert acesso["padrao_modo"] == "regras_da_casa"
    assert acesso["exigir_senha_a_cada_troca"] is True

    assert validar_senha_regras_casa("9930") is True
    assert validar_senha_regras_casa(" 9930 ") is True
    assert validar_senha_regras_casa("9931") is False
    assert validar_senha_regras_casa("") is False
    assert validar_senha_regras_casa(None) is False

    opcoes_rc = listar_opcoes_regras_casa()
    assert opcoes_rc["padrao_modo"] == "regras_da_casa"
    assert opcoes_rc["protegido_por_senha"] is True
    assert opcoes_rc["exigir_senha_a_cada_troca"] is True
    assert "senha" not in opcoes_rc


def main() -> None:
    test_ca_limite_destreza_e_sem_armadura()
    test_penalidade_armadura_barulhenta_flexivel_e_ferro_desimpedido()
    test_mochila_sobrecarga_e_carregador_robusto()
    test_armas_acuidade_ladrao_propulsiva_posturas_e_anao_mago()
    test_idiomas_humano_mago_grimorio_e_regras_especificas()
    test_acoes_classe_pagina3_e_zero_descarte_talentos()
    test_divindades_reais_e_companheiros_familiares()
    test_divindade_obrigatoria_vs_opcional_e_compatibilidade()
    test_revisao_geral_etapa_23()
    test_aleatorio_7_campos_e_bonus_equipamentos()
    test_exportar_pdf_oficial_4_paginas()
    test_escolhas_atributos_manual_procedural_aleatorio()
    test_compra_manual_e_hibrida_equipamentos()
    test_curadoria_e_selecao_manual_talentos()
    test_selecao_manual_e_regras_pericias()
    test_selecao_manual_e_aleatoria_magias()
    test_aderencia_procedural_nortes()
    test_orcamento_90_peso_leve_e_viagem_procedural()
    test_personalizacao_companheiro_familiar_e_perfil()
    test_regras_da_casa_peso_racao_e_oleo()
    print("SUCESSO TOTAL — Todos os testes de casos de borda PF2E passaram!")


if __name__ == "__main__":
    main()
