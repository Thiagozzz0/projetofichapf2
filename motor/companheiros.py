"""Geração de bloco pronto de Companheiro Animal ou Familiar (dados/companheiros_familiares.json)."""

from __future__ import annotations

import random
from typing import Any

from .dados import BaseDados
from .util import formatar_bonus, normalizar


_DADOS_FAMILIAR_TALENTOS = {"familiar", "familiar_alquimico", "familiar_leshy"}


def _mod_chave_familiar(classe_id: str, modificadores_mestre: dict[str, int]) -> int:
    mapa = {
        "alquimista": "int",
        "bardo": "car",
        "clerigo": "sab",
        "druida": "sab",
        "feiticeiro": "car",
        "mago": "int",
        "campeao": "car",
        "monge": "sab",
        "patrulheiro": "sab",
    }
    chave = mapa.get(classe_id, "car")
    return int(modificadores_mestre.get(chave, 0))


def _pontuar_companheiro(
    tipo: dict[str, Any],
    classe_id: str,
    conceito: dict[str, Any],
    ancestralidade: dict[str, Any] | None,
    biografia: dict[str, Any] | None,
) -> int:
    tid = tipo["id"]
    cid = conceito["id"]
    pts = 0

    if "montado" in cid or "cavaleiro" in cid:
        if tid == "cavalo":
            pts += 30
    elif classe_id == "patrulheiro" and tid in {"lobo", "passaro", "felino", "urso"}:
        pts += 4

    pericias_pri = list(conceito.get("pericias_prioritarias") or [])
    per_comp = normalizar(tipo.get("pericia", ""))
    if per_comp and per_comp in {normalizar(p) for p in pericias_pri[:4]}:
        pts += 10

    eq_rec = conceito.get("equipamento_recomendado") or {}
    estilo = eq_rec.get("estilo_empunhadura", "")
    if estilo == "distancia" and tid in {"passaro", "lobo", "felino"}:
        pts += 6
    if (estilo == "duas_armas" or "furtividade" in pericias_pri[:3]) and tid in {"felino", "serpente", "dromaeossauro"}:
        pts += 6
    if (eq_rec.get("usa_escudo") or "intimidacao" in pericias_pri[:3]) and tid in {"urso", "texugo", "lobo"}:
        pts += 6

    keywords = [
        normalizar(k)
        for k in (conceito.get("talentos_recomendados") or {}).get("tracos_ancestralidade_afinidade", [])
    ]
    texto_comp = normalizar(
        f"{tipo['nome']} {tipo.get('descricao', '')} {tipo.get('pericia', '')} {tipo.get('beneficio_de_suporte', '')}"
    )
    pts += sum(3 for kw in keywords if kw and kw in texto_comp)

    anc_id = ancestralidade["id"] if ancestralidade else ""
    afinidade_anc = {
        "anao": {"texugo": 4, "urso": 4},
        "elfo": {"passaro": 4, "felino": 4, "lobo": 4},
        "gnomo": {"texugo": 4, "passaro": 4, "serpente": 4},
        "goblin": {"lobo": 4, "serpente": 4, "dromaeossauro": 4},
        "halfling": {"lobo": 4, "felino": 4, "passaro": 4},
        "humano": {"cavalo": 2, "lobo": 2, "urso": 2},
    }
    pts += afinidade_anc.get(anc_id, {}).get(tid, 0)

    bio_id = biografia["id"] if biografia else ""
    afinidade_bio = {
        "encantador_de_animais": {"lobo": 4, "passaro": 4, "felino": 4},
        "cacador": {"lobo": 4, "passaro": 4, "felino": 4},
        "batedor": {"lobo": 4, "passaro": 4, "felino": 4},
        "nobre": {"cavalo": 4},
        "soldado": {"cavalo": 4},
        "mineiro": {"texugo": 4, "urso": 4},
        "eremita": {"texugo": 4, "urso": 4},
    }
    pts += afinidade_bio.get(bio_id, {}).get(tid, 0)
    return pts


def _gerar_companheiro_animal(
    cf: dict[str, Any],
    classe_id: str,
    conceito: dict[str, Any],
    nivel: int,
    rng: random.Random | None,
    ancestralidade: dict[str, Any] | None = None,
    biografia: dict[str, Any] | None = None,
) -> dict[str, Any]:
    comp_root = cf["companheiros_animais"]
    estagio_jovem = comp_root["estagios_evolucao"][0]
    tipos = comp_root["tipos_de_companheiro"]

    avaliados = [
        (_pontuar_companheiro(t, classe_id, conceito, ancestralidade, biografia), t)
        for t in tipos
    ]
    avaliados.sort(key=lambda par: par[0], reverse=True)
    topo = avaliados[0][0]
    candidatos = [t for pts, t in avaliados if pts >= topo - 3][:3] or tipos
    escolhido = rng.choice(candidatos) if (rng and len(candidatos) > 1) else candidatos[0]

    mods = escolhido["modificadores_atributo"]
    prof_treinado = 2 + nivel
    pv_max = int(escolhido["pontos_de_vida_ancestralidade"]) + (6 + int(mods["constituicao"])) * nivel
    ca = 10 + int(mods["destreza"]) + prof_treinado
    percepcao = int(mods["sabedoria"]) + prof_treinado
    fortitude = int(mods["constituicao"]) + prof_treinado
    reflexos = int(mods["destreza"]) + prof_treinado
    vontade = int(mods["sabedoria"]) + prof_treinado

    pericias = [
        {"nome": "Acrobatismo", "total": int(mods["destreza"]) + prof_treinado},
        {"nome": "Atletismo", "total": int(mods["forca"]) + prof_treinado},
    ]
    per_extra = escolhido.get("pericia", "")
    mapa_atr_per = {
        "furtividade": "destreza",
        "sobrevivencia": "sabedoria",
        "intimidacao": "carisma",
    }
    atr_p = mapa_atr_per.get(normalizar(per_extra), "sabedoria")
    if per_extra and normalizar(per_extra) not in {"acrobatismo", "atletismo"}:
        pericias.append({"nome": per_extra, "total": int(mods[atr_p]) + prof_treinado})

    ataques = []
    for atk in escolhido["ataques"]:
        tracos_l = [normalizar(t) for t in atk.get("tracos", [])]
        mod_atk = max(int(mods["forca"]), int(mods["destreza"])) if "acuidade" in tracos_l else int(mods["forca"])
        partes_dano = atk["dano"].split(" ", 1)
        dado_base = partes_dano[0]
        tipo_dano = partes_dano[1] if len(partes_dano) > 1 else ""
        mod_for = int(mods["forca"])
        dano_fmt = f"{dado_base}{formatar_bonus(mod_for) if mod_for else ''} {tipo_dano}".strip()
        ataques.append(
            {
                "nome": atk["nome"].title(),
                "acoes": atk.get("acoes", "1"),
                "ataque_total": mod_atk + prof_treinado,
                "dano": dano_fmt,
                "tracos": list(atk.get("tracos", [])),
            }
        )

    return {
        "categoria": "Companheiro Animal",
        "id": escolhido["id"],
        "nome": escolhido["nome"],
        "estagio": estagio_jovem["nome"],
        "tamanho": escolhido["tamanho"],
        "descricao": escolhido["descricao"],
        "pv_max": pv_max,
        "ca": ca,
        "percepcao": percepcao,
        "fortitude": fortitude,
        "reflexos": reflexos,
        "vontade": vontade,
        "velocidades": escolhido["velocidades_texto"],
        "sentidos": escolhido["sentidos"],
        "pericias": pericias,
        "ataques": ataques,
        "especial": escolhido.get("especial"),
        "beneficio_de_suporte": escolhido["beneficio_de_suporte"],
        "manobra_avancada": escolhido["manobra_avancada"]["nome"],
    }


def _gerar_familiar(
    cf: dict[str, Any],
    classe_id: str,
    talentos_classe_ids: list[str],
    ficha_mestre: dict[str, Any],
    modificadores_mestre: dict[str, int],
    tese_arcana_id: str | None,
    nivel: int,
    conceito: dict[str, Any] | None = None,
    ancestralidade: dict[str, Any] | None = None,
    biografia: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fam_root = cf["familiares"]
    est = fam_root["estatisticas_base"]
    hab_fam = {h["id"]: h for h in fam_root["habilidades_de_familiar"]}
    hab_mestre = {h["id"]: h for h in fam_root["habilidades_de_mestre"]}

    qtd_habilidades = 3 if tese_arcana_id == "sintonizacao_com_familiar_aprimorada" else int(est["habilidades_diarias_base"])
    eh_leshy = "familiar_leshy" in talentos_classe_ids
    eh_alquimico = "familiar_alquimico" in talentos_classe_ids

    if eh_leshy:
        especie = "Familiar Leshy (Espírito Planta)"
        preferidas = ["fala", "vinculo_vital", "escalador"]
    elif eh_alquimico or classe_id == "alquimista":
        especie = "Familiar Alquímico (Homúnculo / Criatura Alquímica)"
        preferidas = ["destreza_manual", "assistente_de_laboratorio", "reagentes_extras", "fala"]
    elif classe_id in ("mago", "feiticeiro"):
        especie = "Familiar Arcano (Corvo / Coruja / Gato)"
        preferidas = ["foco_de_familiar", "conexao_de_truque_magico", "fala", "visao_no_escuro"]
    else:
        especie = "Familiar Místico"
        preferidas = ["fala", "vinculo_vital", "visao_no_escuro"]

    # Complementa prioridades de habilidades conforme Conceito, Ancestralidade e Biografia
    extras_afinidade: list[str] = []
    if conceito:
        per_pri = {normalizar(p) for p in (conceito.get("pericias_prioritarias") or [])[:4]}
        cid_con = conceito["id"]
        if "furtividade" in per_pri or "ladroagem" in per_pri or "batedor" in cid_con or "sabotador" in cid_con:
            extras_afinidade.extend(["visao_no_escuro", "faro", "voador", "escalador"])
        if any(p in per_pri for p in ("diplomacia", "enganacao", "performance", "intimidacao")) or "ilusionista" in cid_con:
            extras_afinidade.extend(["fala", "destreza_manual"])
        if any(k in cid_con for k in ("artilharia", "evocador", "duelista")):
            extras_afinidade.extend(["foco_de_familiar", "conexao_de_truque_magico", "voador"])
    if ancestralidade:
        anc_id = ancestralidade["id"]
        if anc_id in ("anao", "gnomo"):
            extras_afinidade.extend(["escavador", "visao_no_escuro"])
        elif anc_id == "elfo":
            extras_afinidade.extend(["voador", "movimento_rapido"])
    if biografia:
        bio_id = biografia["id"]
        if bio_id == "marinheiro":
            extras_afinidade.append("anfibio")
        elif bio_id == "mineiro":
            extras_afinidade.append("escavador")
        elif bio_id in ("batedor", "detetive"):
            extras_afinidade.append("faro")

    for hid_ext in extras_afinidade:
        if hid_ext not in preferidas:
            preferidas.append(hid_ext)

    # Valida pré-requisitos conhecidos de habilidades diárias
    possui_foco = int(ficha_mestre["conjuracao"]["magias_foco"]["pontos_foco"]["maximo"] or 0) > 0
    possui_conjuracao = any(ficha_mestre["conjuracao"]["tradicoes_marcadas"].values())

    escolhidas: list[dict[str, str]] = []
    usadas: set[str] = set()
    for hid in preferidas:
        if len(escolhidas) >= qtd_habilidades:
            break
        if hid == "foco_de_familiar" and not possui_foco:
            continue
        if hid in ("conexao_de_truque_magico", "transmitir_magia") and not possui_conjuracao:
            continue
        if hid == "assistente_de_laboratorio" and "destreza_manual" not in usadas:
            continue
        if hid == "reagentes_extras" and classe_id != "alquimista":
            continue
        item = hab_fam.get(hid) or hab_mestre.get(hid)
        if item:
            tipo_h = "Habilidade de Familiar" if hid in hab_fam else "Habilidade de Mestre"
            escolhidas.append(
                {
                    "id": item["id"],
                    "nome": item["nome"],
                    "tipo": tipo_h,
                    "descricao": item["descricao"],
                }
            )
            usadas.add(hid)

    # Completa se ainda faltar vaga
    for item in fam_root["habilidades_de_familiar"]:
        if len(escolhidas) >= qtd_habilidades:
            break
        if item["id"] not in usadas and item["id"] not in {"assistente_de_laboratorio", "falar_com_a_propria_especie"}:
            escolhidas.append(
                {
                    "id": item["id"],
                    "nome": item["nome"],
                    "tipo": "Habilidade de Familiar",
                    "descricao": item["descricao"],
                }
            )
            usadas.add(item["id"])

    mod_chave = _mod_chave_familiar(classe_id, modificadores_mestre)
    salv = ficha_mestre["jogadas_salvamento"]
    return {
        "categoria": "Familiar",
        "nome": especie,
        "tamanho": est["tamanho"],
        "pv_max": int(est["pontos_de_vida_por_nivel"]) * nivel,
        "ca": int(ficha_mestre["classe_armadura"]["total"]),
        "fortitude": int(salv["fortitude"]["total"]),
        "reflexos": int(salv["reflexos"]["total"]),
        "vontade": int(salv["vontade"]["total"]),
        "percepcao": nivel + mod_chave,
        "acrobatismo": nivel + mod_chave,
        "furtividade": nivel + mod_chave,
        "outros_testes": nivel,
        "velocidade": "7,5 metros",
        "sentidos": "Visão na Penumbra; empatia até 1,5 km",
        "habilidades_diarias_max": qtd_habilidades,
        "habilidades_selecionadas": escolhidas,
    }


def gerar_companheiro_ou_familiar(
    dados: BaseDados,
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    conceito: dict[str, Any],
    talentos_classe_ids: list[str],
    ficha_mestre: dict[str, Any],
    modificadores_mestre: dict[str, int],
    tese_arcana_id: str | None = None,
    talento_ancestral_id: str | None = None,
    ancestralidade: dict[str, Any] | None = None,
    biografia: dict[str, Any] | None = None,
    nivel: int = 1,
    rng: random.Random | None = None,
) -> dict[str, Any] | None:
    """Retorna o bloco pronto de Companheiro Animal ou Familiar quando aplicável."""
    cf = dados.companheiros_familiares
    classe_id = classe["id"]

    if "companheiro_animal" in talentos_classe_ids:
        return _gerar_companheiro_animal(
            cf,
            classe_id,
            conceito,
            nivel,
            rng,
            ancestralidade=ancestralidade,
            biografia=biografia,
        )

    if any(tid in _DADOS_FAMILIAR_TALENTOS for tid in talentos_classe_ids) or talento_ancestral_id == "cumplice_animal":
        return _gerar_familiar(
            cf,
            classe_id,
            talentos_classe_ids,
            ficha_mestre,
            modificadores_mestre,
            tese_arcana_id,
            nivel,
            conceito=conceito,
            ancestralidade=ancestralidade,
            biografia=biografia,
        )

    return None
