"""Matemática final de combate, defesas, velocidade, golpes e ações da ficha PF2E."""

from __future__ import annotations

from typing import Any

from .equipamentos import grau_arma
from .util import (
    GRAUS,
    bonus_proficiencia,
    chave_categoria_armadura as _chave_categoria_armadura,
    formatar_bonus,
    grau_normalizado,
    normalizar,
    subir_grau as _subir_grau,
)


def _dano_arma_formatado(arma: dict[str, Any], bonus_dano: int) -> str:
    base = f"{arma['dano_quantidade']}{arma['dano_dado']}"
    if bonus_dano > 0:
        return f"{base}+{bonus_dano}"
    if bonus_dano < 0:
        return f"{base}{bonus_dano}"
    return base


def _preencher_golpe(
    slot: dict[str, Any],
    arma: dict[str, Any],
    eh_distancia: bool,
    grau_atk: str,
    nivel: int,
    modificadores: dict[str, int],
    classe_id: str,
    subclasse_id: str,
    dano_override: tuple[int, str] | None = None,
) -> None:
    tracos = list(arma.get("tracos", []))
    tracos_norm = " ".join(normalizar(t) for t in tracos)
    prof_bonus = bonus_proficiencia(grau_atk, nivel)

    if eh_distancia:
        mod_atk = modificadores["des"]
        if "propulsiv" in tracos_norm:
            terceiro_dano = modificadores["for"] // 2 if modificadores["for"] >= 0 else modificadores["for"]
        elif "arremesso" in tracos_norm:
            terceiro_dano = modificadores["for"]
        else:
            terceiro_dano = 0
        campo_terceiro = "especial"
    else:
        tem_acuidade = "acuidade" in tracos_norm
        mod_atk = max(modificadores["for"], modificadores["des"]) if tem_acuidade else modificadores["for"]
        if tem_acuidade and classe_id == "ladino" and subclasse_id == "ladrao":
            terceiro_dano = modificadores["des"]
        else:
            terceiro_dano = modificadores["for"]
        campo_terceiro = "for"

    qtd_dados, tipo_dado = dano_override or (
        arma.get("dano_quantidade") or 1,
        arma.get("dano_dado") or "d4",
    )

    slot["arma"] = arma["nome"]
    slot["ataque"] = {
        "total": mod_atk + prof_bonus,
        "mod_atributo": mod_atk,
        "proficiencia": prof_bonus,
        "grau_proficiencia": grau_atk,
        "item": 0,
    }
    slot["dano"] = {
        "dados": f"{qtd_dados}{tipo_dado}",
        campo_terceiro: terceiro_dano,
        "tipos_dano": [arma["dano_tipo"]] if arma.get("dano_tipo") and arma["dano_tipo"] != "Varia" else [],
        "especializacao": 0,
        "outro": 0,
        "tracos": tracos,
    }


def _sentidos_personagem(ancestralidade: dict[str, Any], heranca: dict[str, Any]) -> list[str]:
    sentidos: list[str] = []
    for hab in ancestralidade.get("habilidades_especiais", []):
        nome = hab.get("nome", "")
        if "visao" in normalizar(nome) or "olhos" in normalizar(nome):
            sentidos.append(nome)
    for s in heranca.get("sentidos_concedidos", []) or []:
        if s not in sentidos:
            # Herança com Visão no Escuro substitui Visão na Penumbra
            if normalizar(s) == "visao no escuro":
                sentidos = [x for x in sentidos if "penumbra" not in normalizar(x)]
            sentidos.append(s)
    return sentidos


_MONGE_POSTURAS_GOLPES = {
    "postura_do_tigre": {
        "nome": "Garra do Tigre (Postura)",
        "dano_quantidade": 1,
        "dano_dado": "d8",
        "dano_tipo": "Ct",
        "tracos": ["Acuidade", "Ágil", "Desarmado", "Não-Letal"],
        "nota_ca": None,
    },
    "postura_do_lobo": {
        "nome": "Mandíbula do Lobo (Postura)",
        "dano_quantidade": 1,
        "dano_dado": "d8",
        "dano_tipo": "Pf",
        "tracos": ["Acuidade", "Ágil", "Apunhaladora", "Desarmado", "Não-Letal"],
        "nota_ca": None,
    },
    "postura_da_montanha": {
        "nome": "Pedra Cadente (Postura)",
        "dano_quantidade": 1,
        "dano_dado": "d8",
        "dano_tipo": "Cn",
        "tracos": ["Enérgico", "Desarmado", "Não-Letal"],
        "nota_ca": "Postura da Montanha (ativa): +4 bônus de estado na CA (Lim Des +0, -1,5m Vel.)",
    },
    "postura_da_garca": {
        "nome": "Asa da Garça (Postura)",
        "dano_quantidade": 1,
        "dano_dado": "d6",
        "dano_tipo": "Cn",
        "tracos": ["Acuidade", "Ágil", "Desarmado", "Não-Letal"],
        "nota_ca": "Postura da Garça (ativa): +1 bônus de circunstância na CA",
    },
    "postura_do_dragao": {
        "nome": "Cauda do Dragão (Postura)",
        "dano_quantidade": 1,
        "dano_dado": "d10",
        "dano_tipo": "Cn",
        "tracos": ["Desarmado", "Não-Letal", "Oscilante"],
        "nota_ca": None,
    },
}

_PASSO_DADO = {"d4": "d6", "d6": "d8", "d8": "d10", "d10": "d12", "d12": "d12"}


def calcular_matematica_final(
    ficha: dict[str, Any],
    dados: Any,
    ancestralidade: dict[str, Any],
    heranca: dict[str, Any],
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    atributos_res: dict[str, Any],
    pericias_res: dict[str, Any],
    idiomas: list[str],
    talentos_res: dict[str, Any],
    profs_combate: dict[str, Any],
    equip_res: dict[str, Any],
    nivel: int = 1,
    tese_arcana: dict[str, Any] | None = None,
    divindade: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Consolida PV, CA, Velocidade, Salvamentos, Percepção, Golpes, Perícias e Ações na ficha."""
    valores = atributos_res["valores"]
    mods = atributos_res["modificadores"]
    classe_id = classe["id"]
    sub_id = subclasse["id"] if subclasse else ""
    efeitos = talentos_res["efeitos"]

    # ------------------------------------------------------------------
    # 1. Pontos de Vida
    # ------------------------------------------------------------------
    pv_anc = int(heranca.get("pv_ancestral_substituto") or ancestralidade["pontos_vida"])
    pv_classe = int(classe["pontos_de_vida_por_nivel"])
    pv_vitalidade = nivel if efeitos.get("vitalidade") else 0
    pv_total = max(1, pv_anc + (pv_classe + mods["con"]) * nivel + pv_vitalidade)

    ficha["pontos_vida"]["max"] = pv_total
    ficha["pontos_vida"]["atuais"] = pv_total
    resistencias = list(heranca.get("resistencias", []) or [])
    ficha["pontos_vida"]["resistencias_e_imunidades"] = ", ".join(resistencias)

    # ------------------------------------------------------------------
    # 2. Classe de Armadura, Escudo e Penalidade de Armadura
    # ------------------------------------------------------------------
    armadura = equip_res["armadura"]
    cat_arm = _chave_categoria_armadura(armadura["categoria"])
    grau_def = profs_combate["defesas"][cat_arm]
    prof_ca = bonus_proficiencia(grau_def, nivel)
    limite_des = armadura.get("limite_destreza")
    des_efetiva = min(mods["des"], limite_des) if limite_des is not None else mods["des"]
    bonus_arm = int(armadura.get("bonus_ca") or 0)
    ca_total = 10 + des_efetiva + prof_ca + bonus_arm

    ficha["classe_armadura"] = {
        "total": ca_total,
        "des_ou_limite": des_efetiva,
        "limite_des_armadura": limite_des,
        "proficiencia": prof_ca,
        "grau_proficiencia": grau_def,
        "item": bonus_arm,
        "proficiencias_armadura": dict(profs_combate["defesas"]),
        "escudo": {
            "nome": equip_res["escudo"]["nome"] if equip_res["escudo"] else "",
            "bonus_ca": int(equip_res["escudo"]["bonus_ca"]) if equip_res["escudo"] else 0,
            "dureza": int(equip_res["escudo"]["dureza"]) if equip_res["escudo"] else 0,
            "pv_max": int(equip_res["escudo"]["pv"]) if equip_res["escudo"] else 0,
            "limiar_quebra": int(equip_res["escudo"]["limiar_quebra"]) if equip_res["escudo"] else 0,
            "pv_atuais": int(equip_res["escudo"]["pv"]) if equip_res["escudo"] else 0,
        },
    }

    forca_min = armadura.get("forca_minima")
    atende_for_armadura = (forca_min is None) or (valores["for"] >= int(forca_min))
    pen_testes_arm = 0 if atende_for_armadura else int(armadura.get("penalidade_testes") or 0)
    pen_vel_arm = float(armadura.get("penalidade_velocidade_m") or 0.0)
    if pen_vel_arm < 0 and atende_for_armadura:
        pen_vel_arm = min(0.0, pen_vel_arm + 1.5)
    if efeitos.get("ferro_desimpedido"):
        pen_vel_arm = 0.0

    # ------------------------------------------------------------------
    # 3. Velocidade
    # ------------------------------------------------------------------
    vel_base = float(ancestralidade["velocidade_m"])
    vel_bonus = (1.5 if efeitos.get("veloz") else 0.0) + (1.5 if efeitos.get("elfo_ligeiro") else 0.0)
    mov_incrivel = (classe_id == "monge" and nivel >= 3 and cat_arm == "sem_armadura")
    if mov_incrivel:
        vel_bonus += 3.0
    pen_sobrecarga = -3.0 if equip_res["esta_sobrecarregado"] else 0.0
    vel_final = max(1.5, vel_base + vel_bonus + pen_vel_arm + pen_sobrecarga)

    obs_vel = []
    if mov_incrivel:
        obs_vel.append("Movimento Incrível (+3m)")
    if pen_vel_arm < 0:
        obs_vel.append(f"Armadura {formatar_bonus(int(pen_vel_arm))}m" if pen_vel_arm.is_integer() else f"Armadura {pen_vel_arm}m")
    if equip_res["esta_sobrecarregado"]:
        obs_vel.append("Sobrecarregado (-3m)")
    ficha["velocidade"] = {
        "metros": vel_final,
        "tipos_movimento_anotacoes": "; ".join(obs_vel),
    }

    # ------------------------------------------------------------------
    # 4. CD de Classe, Salvamentos e Percepção
    # ------------------------------------------------------------------
    attr_chave = atributos_res["atributo_chave"]
    cd_classe_info = classe["proficiencias_iniciais"].get("cd_classe")
    grau_cd = grau_normalizado(cd_classe_info) if cd_classe_info else "treinado"
    prof_cd = bonus_proficiencia(grau_cd, nivel)
    ficha["cd_classe"] = {
        "total": 10 + mods[attr_chave] + prof_cd,
        "mod_atributo_chave": mods[attr_chave],
        "proficiencia": prof_cd,
        "grau_proficiencia": grau_cd,
        "item": 0,
    }

    salv_brutos = classe["proficiencias_iniciais"]["salvamentos"]
    graus_salv = {
        "fortitude": grau_normalizado(salv_brutos["fortitude"]),
        "reflexos": grau_normalizado(salv_brutos["reflexos"]),
        "vontade": grau_normalizado(salv_brutos["vontade"]),
    }
    if classe_id == "clerigo" and sub_id == "capelao_da_guerra":
        graus_salv["fortitude"] = "especialista"

    grau_perc = grau_normalizado(classe["proficiencias_iniciais"]["percepcao"])

    # Marcos de Salvamentos e Percepção dos níveis 2 a 5 (tabela_progressao)
    if nivel >= 3:
        if classe_id == "bardo":
            graus_salv["reflexos"] = _subir_grau(graus_salv["reflexos"], "especialista")
        elif classe_id == "clerigo" and sub_id == "sacerdote_enclausurado":
            graus_salv["fortitude"] = _subir_grau(graus_salv["fortitude"], "especialista")
        elif classe_id == "druida":
            graus_salv["fortitude"] = _subir_grau(graus_salv["fortitude"], "especialista")
            grau_perc = _subir_grau(grau_perc, "especialista")
        elif classe_id in ("guerreiro", "patrulheiro"):
            graus_salv["vontade"] = _subir_grau(graus_salv["vontade"], "especialista")

    if nivel >= 5:
        if classe_id in ("clerigo", "monge"):
            grau_perc = _subir_grau(grau_perc, "especialista")
        elif classe_id in ("druida", "mago"):
            graus_salv["reflexos"] = _subir_grau(graus_salv["reflexos"], "especialista")
        elif classe_id == "feiticeiro":
            graus_salv["fortitude"] = _subir_grau(graus_salv["fortitude"], "especialista")

    if efeitos.get("perspicacia_astuta"):
        if grau_perc == "treinado":
            grau_perc = "especialista"
        else:
            for sid_cand in ("vontade", "fortitude", "reflexos"):
                if graus_salv[sid_cand] == "treinado":
                    graus_salv[sid_cand] = "especialista"
                    break

    mapa_atr_salv = {"fortitude": "con", "reflexos": "des", "vontade": "sab"}
    for sid, atr in mapa_atr_salv.items():
        g = graus_salv[sid]
        p = bonus_proficiencia(g, nivel)
        ficha["jogadas_salvamento"][sid] = {
            "atributo_chave": atr,
            "total": mods[atr] + p,
            "mod_atributo": mods[atr],
            "proficiencia": p,
            "grau_proficiencia": g,
            "item": 0,
        }

    if heranca.get("habilidade_acao"):
        ficha["jogadas_salvamento"]["anotacoes"] = heranca["habilidade_acao"]["nome"]

    prof_perc = bonus_proficiencia(grau_perc, nivel)
    bonus_iniciativa = 2 if efeitos.get("iniciativa_incrivel") else 0
    sentidos = _sentidos_personagem(ancestralidade, heranca)
    if efeitos.get("visao_orquica") and "Visão no Escuro" not in sentidos:
        sentidos = [s for s in sentidos if "penumbra" not in normalizar(s)]
        sentidos.append("Visão no Escuro")
    ficha["percepcao"] = {
        "total": mods["sab"] + prof_perc,
        "mod_sab": mods["sab"],
        "proficiencia": prof_perc,
        "grau_proficiencia": grau_perc,
        "item": 0,
        "sentidos": sentidos,
    }
    if bonus_iniciativa:
        ficha["percepcao"]["sentidos"].append("Iniciativa Incrível (+2 circ. iniciativa)")

    # ------------------------------------------------------------------
    # 5. Perícias (18 linhas oficiais na ordem exata de estrutura_ficha.json)
    # ------------------------------------------------------------------
    tracos_arm = {normalizar(t) for t in armadura.get("tracos", [])}
    pen_bruta_arm = int(armadura.get("penalidade_testes") or 0)
    graus_per = pericias_res["graus"]
    saberes = pericias_res["saberes"]
    for linha in ficha["pericias"]:
        slot_id = linha["id"]
        atr = linha["atributo_chave"]
        if slot_id in ("saber_1", "saber_2"):
            info_saber = saberes[slot_id]
            grau = info_saber["grau"]
            linha["especializacao"] = info_saber["especializacao"]
        else:
            grau = graus_per.get(slot_id, "destreinado")
        prof = bonus_proficiencia(grau, nivel)
        if linha["penalidade_armadura"] is not None:
            if slot_id == "furtividade" and "barulhenta" in tracos_arm:
                pen_arm = pen_bruta_arm
            elif slot_id in ("acrobatismo", "atletismo") and "flexivel" in tracos_arm:
                pen_arm = 0
            else:
                pen_arm = pen_testes_arm
        else:
            pen_arm = 0
        linha["grau_proficiencia"] = grau
        linha["proficiencia"] = prof
        linha["mod_atributo"] = mods[atr]
        if linha["penalidade_armadura"] is not None:
            linha["penalidade_armadura"] = pen_arm
        linha["total"] = mods[atr] + prof + pen_arm

    ficha["idiomas"] = idiomas

    # ------------------------------------------------------------------
    # 6. Proficiência com Armas e Golpes (Corpo a Corpo e À Distância)
    # ------------------------------------------------------------------
    armas_prof = profs_combate["armas"]
    ficha["proficiencia_armas"][0]["grau_proficiencia"] = armas_prof["simples"]
    ficha["proficiencia_armas"][1]["grau_proficiencia"] = armas_prof["marcial"]
    ficha["proficiencia_armas"][2]["grau_proficiencia"] = armas_prof["desarmado"]
    ficha["proficiencia_armas"][2]["rotulo"] = "DESARMADO"
    if armas_prof["especificas_lista"]:
        ficha["proficiencia_armas"][3]["rotulo"] = f"ESPECÍFICAS ({classe['nome'].upper()})"
        ficha["proficiencia_armas"][3]["grau_proficiencia"] = armas_prof["especificas_grau"]
    elif armas_prof["bombas_alquimicas"] != "destreinado":
        ficha["proficiencia_armas"][3]["rotulo"] = "BOMBAS ALQUÍMICAS"
        ficha["proficiencia_armas"][3]["grau_proficiencia"] = armas_prof["bombas_alquimicas"]
    elif armas_prof.get("armas_traco_monge", "destreinado") != "destreinado":
        ficha["proficiencia_armas"][3]["rotulo"] = "ARMAS DE MONGE"
        ficha["proficiencia_armas"][3]["grau_proficiencia"] = armas_prof["armas_traco_monge"]
    elif armas_prof["avancada"] != "destreinado":
        ficha["proficiencia_armas"][3]["rotulo"] = "AVANÇADAS"
        ficha["proficiencia_armas"][3]["grau_proficiencia"] = armas_prof["avancada"]

    armas_cc = [w for w in equip_res["armas"] if w.get("tipo_ataque") == "corpo_a_corpo"]
    armas_dist = [w for w in equip_res["armas"] if w.get("tipo_ataque") == "distancia"]

    # Golpes Corpo a Corpo (3 slots)
    idx_cc = 0
    wid_div = divindade.get("arma_favorecida_id") if divindade else None

    def _override_simplicidade(arma_obj: dict[str, Any]) -> tuple[int, str] | None:
        if efeitos.get("simplicidade_mortal") and wid_div and arma_obj.get("id") == wid_div:
            dado_atual = arma_obj.get("dano_dado") or "d4"
            return (arma_obj.get("dano_quantidade") or 1, _PASSO_DADO.get(dado_atual, dado_atual))
        return None

    for w in armas_cc:
        if idx_cc >= 3:
            break
        _preencher_golpe(
            ficha["golpes_corpo_a_corpo"][idx_cc],
            w,
            False,
            grau_arma(w, armas_prof),
            nivel,
            mods,
            classe_id,
            sub_id,
            dano_override=_override_simplicidade(w),
        )
        idx_cc += 1

    # Golpe especial de Postura de Monge (1º nível) ou Instinto Animal (Bárbaro)
    nota_postura = ""
    if classe_id == "monge":
        for tid in talentos_res["talentos_classe_ids"]:
            post = _MONGE_POSTURAS_GOLPES.get(tid)
            if post and idx_cc < 3:
                _preencher_golpe(
                    ficha["golpes_corpo_a_corpo"][idx_cc],
                    post,
                    False,
                    armas_prof["desarmado"],
                    nivel,
                    mods,
                    classe_id,
                    sub_id,
                )
                idx_cc += 1
                if post["nota_ca"]:
                    nota_postura = post["nota_ca"]
                break
    elif classe_id == "barbaro" and sub_id == "instinto_animal" and idx_cc < 3:
        bestial = {
            "nome": "Ataque Bestial (Instinto Animal)",
            "dano_quantidade": 1,
            "dano_dado": "d10",
            "dano_tipo": "Pf",
            "tracos": ["Desarmado", "Morfia"],
        }
        _preencher_golpe(
            ficha["golpes_corpo_a_corpo"][idx_cc],
            bestial,
            False,
            armas_prof["desarmado"],
            nivel,
            mods,
            classe_id,
            sub_id,
        )
        idx_cc += 1

    # Punho (sempre para Monge no slot 0 se não houver arma, ou no próximo slot livre; Mandíbulas para Goblin Dentes de Navalha)
    if efeitos.get("dentes_de_navalha") and idx_cc < 3:
        mandibulas = {
            "nome": "Mandíbulas (Herança)",
            "dano_quantidade": 1,
            "dano_dado": "d6",
            "dano_tipo": "Pf",
            "tracos": ["Acuidade", "Desarmado"],
        }
        _preencher_golpe(
            ficha["golpes_corpo_a_corpo"][idx_cc],
            mandibulas,
            False,
            armas_prof["desarmado"],
            nivel,
            mods,
            classe_id,
            sub_id,
        )
        idx_cc += 1

    if idx_cc < 3:
        punho = dados.ataques_desarmados["punho"]
        override = (1, "d6") if classe_id == "monge" else _override_simplicidade(punho)
        _preencher_golpe(
            ficha["golpes_corpo_a_corpo"][idx_cc],
            punho,
            False,
            armas_prof["desarmado"],
            nivel,
            mods,
            classe_id,
            sub_id,
            dano_override=override,
        )

    # Golpes À Distância (3 slots)
    idx_dist = 0
    if classe_id == "alquimista":
        bomba = dados.armas["bomba_alquimica"]
        _preencher_golpe(
            ficha["golpes_a_distancia"][idx_dist],
            bomba,
            True,
            grau_arma(bomba, armas_prof),
            nivel,
            mods,
            classe_id,
            sub_id,
            dano_override=(1, "d8"),
        )
        idx_dist += 1

    for w in armas_dist:
        if idx_dist >= 3:
            break
        _preencher_golpe(
            ficha["golpes_a_distancia"][idx_dist],
            w,
            True,
            grau_arma(w, armas_prof),
            nivel,
            mods,
            classe_id,
            sub_id,
            dano_override=_override_simplicidade(w),
        )
        idx_dist += 1

    # Armas de arremesso compradas também entram nos slots à distância se houver vaga
    for w in armas_cc:
        if idx_dist >= 3:
            break
        if any("arremesso" in normalizar(t) for t in w.get("tracos", [])):
            _preencher_golpe(
                ficha["golpes_a_distancia"][idx_dist],
                w,
                True,
                grau_arma(w, armas_prof),
                nivel,
                mods,
                classe_id,
                sub_id,
                dano_override=_override_simplicidade(w),
            )
            idx_dist += 1

    # ------------------------------------------------------------------
    # 7. Inventário
    # ------------------------------------------------------------------
    ficha["inventario"] = {
        "itens_vestidos": equip_res["itens_vestidos"],
        "itens_preparados": equip_res["itens_preparados"],
        "outros_itens": equip_res["outros_itens"],
        "volume_total": equip_res["volume_total"],
        "volume_sobrecarregado": equip_res["volume_sobrecarregado"],
        "volume_maximo": equip_res["volume_maximo"],
        "itens_investidos_total": 0,
        "riqueza": equip_res["riqueza"],
    }

    # ------------------------------------------------------------------
    # 8. Página 3 — Ações e Atividades (6 slots) + Ações Livres e Reações (4 slots)
    # ------------------------------------------------------------------
    acoes_ativas: list[dict[str, Any]] = []
    acoes_reativas: list[dict[str, Any]] = []

    fontes_acoes: list[dict[str, Any] | None] = []
    # Ações concedidas por características de classe e subclasse
    for car in (talentos_res.get("caracteristicas_classe") or talentos_res["caracteristicas_classe_n1"]):
        if car.get("id") == "elo_arcano" and tese_arcana and tese_arcana.get("acao_substituta"):
            fontes_acoes.append(tese_arcana["acao_substituta"])
            continue
        for acao_c in car.get("acoes_concedidas") or []:
            if car.get("id") == "reacao_de_campeao" and subclasse and subclasse.get("reacao_campeao"):
                if normalizar(acao_c.get("nome")) != normalizar(subclasse["reacao_campeao"]):
                    continue
            fontes_acoes.append(acao_c)
    if subclasse:
        for acao_s in subclasse.get("acoes_concedidas") or []:
            fontes_acoes.append(acao_s)

    fontes_acoes.extend(list(talentos_res["talentos_classe"]))
    fontes_acoes.extend(list(talentos_res.get("talentos_ancestrais") or [talentos_res["talento_ancestral"]]))
    fontes_acoes.append(talentos_res["talento_biografia"].get("dados_completos"))
    for b in talentos_res["talentos_bonus"]:
        fontes_acoes.append(b.get("dados_completos"))
    if heranca.get("habilidade_acao"):
        ha = heranca["habilidade_acao"]
        fontes_acoes.append(
            {
                "nome": ha["nome"],
                "acoes": "reacao" if "rea" in normalizar(ha.get("acoes")) else ha.get("acoes"),
                "tracos": [heranca["nome"]],
                "acionamento": ha.get("acionamento", ""),
                "descricao": ha.get("efeito", ""),
            }
        )
    if efeitos.get("bloqueio_com_escudo"):
        be = dados.talentos_gerais_pericia["bloqueio_com_escudo"]
        fontes_acoes.append(be)

    nomes_vistos: set[str] = set()
    for item in fontes_acoes:
        if not isinstance(item, dict):
            continue
        ac = item.get("acoes")
        nome = item.get("nome", "")
        if not ac or nome in nomes_vistos:
            continue
        nomes_vistos.add(nome)
        registro = {
            "nome": nome,
            "acoes": ac,
            "tracos": list(item.get("tracos", [])),
            "pagina": None,
            "acionamento": item.get("acionamento") or "",
            "descricao": item.get("descricao") or "",
        }
        if ac in ("livre", "reacao"):
            acoes_reativas.append(registro)
        else:
            acoes_ativas.append(registro)

    for idx, item in enumerate(acoes_ativas[:6]):
        ficha["acoes_e_atividades"][idx].update(item)

    for idx, item in enumerate(acoes_reativas[:4]):
        slot = ficha["acoes_livres_e_reacoes"][idx]
        slot["nome"] = item["nome"]
        slot["tipo"] = "AÇÃO LIVRE" if item["acoes"] == "livre" else "REAÇÃO"
        slot["tracos"] = item["tracos"]
        slot["pagina"] = item["pagina"]
        slot["acionamento"] = item["acionamento"]
        slot["descricao"] = item["descricao"]

    escudo_bonus = int(equip_res["escudo"]["bonus_ca"]) if equip_res["escudo"] else 0
    return {
        "penalidade_armadura_testes": pen_testes_arm,
        "penalidade_armadura_velocidade": pen_vel_arm,
        "esta_sobrecarregado": equip_res["esta_sobrecarregado"],
        "limite_morrendo": efeitos.get("limite_morrendo", 4),
        "cd_recuperacao_base": efeitos.get("cd_recuperacao_base", 10),
        "ca_com_escudo": (ca_total + escudo_bonus) if escudo_bonus else None,
        "nota_postura": nota_postura,
        "maestria_guerreiro_grupo": armas_prof.get("maestria_guerreiro_grupo"),
    }
