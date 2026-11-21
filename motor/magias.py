"""Cálculo de conjuração, seleção temática de magias, truques, foco e magias inatas."""

from __future__ import annotations

import math
import random
from typing import Any

from .dados import BaseDados
from .util import atributo_id, bonus_proficiencia, normalizar, slugify


_CLASSES_FOCO_CAR = {"campeao"}
_CLASSES_FOCO_SAB = {"monge"}


def _formatar_acoes(acoes: str | None) -> str:
    if not acoes:
        return "2"
    mapa = {"reacao": "Reação", "livre": "Livre"}
    return mapa.get(acoes, str(acoes))


def _formatar_componentes(componentes: list[str] | None) -> list[str]:
    mapa = {"material": "M", "somatico": "S", "somático": "S", "verbal": "V"}
    return [mapa.get(normalizar(c), c[:1].upper()) for c in (componentes or [])]


def _pontuar_magia(
    magia: dict[str, Any],
    tracos_pri: list[str],
    escolas_pri: list[str],
) -> int:
    score = 0
    tracos_m = {normalizar(t) for t in magia.get("tracos", [])}
    escola_m = normalizar(magia.get("escola"))
    if normalizar(magia.get("raridade")) == "incomum":
        score -= 5  # Prefere magias comuns quando houver empate
    for t in tracos_pri:
        if normalizar(t) in tracos_m:
            score += 4
    for e in escolas_pri:
        if normalizar(e) == escola_m:
            score += 3
    return score


def _selecionar_magias_por_nivel(
    dados: BaseDados,
    tradicao: str,
    nivel_magia: int | None,
    eh_truque: bool,
    quantidade: int,
    prioritarias_ids: list[str],
    tracos_pri: list[str],
    escolas_pri: list[str],
    ja_selecionadas: set[str],
    rng: random.Random | None,
) -> list[dict[str, Any]]:
    """Seleciona magias comuns da tradição priorizando a lista do conceito e depois os traços/escolas."""
    escolhidas: list[dict[str, Any]] = []

    def tentar_adicionar(magia: dict[str, Any] | None) -> None:
        if not magia or len(escolhidas) >= quantidade:
            return
        mid = magia["id"]
        if mid in ja_selecionadas:
            return
        if tradicao not in magia.get("tradicoes", []):
            return
        tracos = magia.get("tracos", [])
        if eh_truque and "Truque Mágico" not in tracos:
            return
        if not eh_truque and magia.get("nivel") != nivel_magia:
            return
        ja_selecionadas.add(mid)
        escolhidas.append(magia)

    # 1. Lista explícita do conceito
    for mid in prioritarias_ids:
        tentar_adicionar(dados.magias.get(mid))

    if len(escolhidas) >= quantidade:
        return escolhidas

    # 2. Busca dinâmica no catálogo de magias por tradição, traços e escola
    pool = []
    for m in dados.magias.values():
        if m["id"] in ja_selecionadas or tradicao not in m.get("tradicoes", []):
            continue
        eh_truque_m = "Truque Mágico" in m.get("tracos", [])
        if eh_truque != eh_truque_m:
            continue
        if not eh_truque and m.get("nivel") != nivel_magia:
            continue
        pool.append((_pontuar_magia(m, tracos_pri, escolas_pri), m))

    pool.sort(key=lambda x: x[0], reverse=True)
    if rng is not None and len(pool) > 1:
        # Embaralha levemente apenas itens fora do bloco de maior afinidade
        idx = 0
        while len(escolhidas) < quantidade and idx < len(pool):
            nota_atual = pool[idx][0]
            bloco = [m for n, m in pool[idx:] if n == nota_atual]
            rng.shuffle(bloco)
            for m in bloco:
                tentar_adicionar(m)
            idx += len(bloco)
    else:
        for _, m in pool:
            tentar_adicionar(m)

    return escolhidas


def _tabela_magias_classe(classe: dict[str, Any]) -> dict[str, Any] | None:
    te = classe.get("tabelas_especificas") or {}
    for chave, valor in te.items():
        if "magias_por_dia" in chave and isinstance(valor, list):
            return valor[0]
    return None


def _resolver_magia_foco_dominio(
    dados: BaseDados,
    conceito: dict[str, Any],
    rng: random.Random | None,
) -> dict[str, Any] | None:
    candidatos = [
        m for m in dados.magias_foco.values()
        if m.get("classe_id") == "clerigo" and m.get("nivel") == 1
    ]
    if not candidatos:
        return None
    conj_rec = conceito.get("conjuracao_recomendada") or {}
    keywords = [normalizar(k) for k in conj_rec.get("tracos_prioritarios", [])]
    cid = conceito["id"]
    if any(k in cid for k in ("cura", "curandeiro", "hospitalario")):
        keywords.append("cura")
    elif any(k in cid for k in ("guerra", "arauto")):
        keywords.extend(["arma", "forca", "fervor"])
    elif any(k in cid for k in ("ceifador", "sombrio")):
        keywords.extend(["morte", "dor", "noite", "destruicao"])
    elif any(k in cid for k in ("teologo", "dominio", "exorcista")):
        keywords.extend(["sol", "luz", "fogo", "conhecimento"])

    avaliados = []
    for m in candidatos:
        texto = normalizar(f"{m['nome']} {m.get('dominio', '')} {m['descricao']} {' '.join(m['tracos'])}")
        pts = sum(3 for kw in keywords if kw in texto)
        avaliados.append((pts, m))
    avaliados.sort(key=lambda x: x[0], reverse=True)
    topo = avaliados[0][0]
    empates = [m for p, m in avaliados if p == topo]
    return rng.choice(empates) if (rng and len(empates) > 1) else empates[0]


def gerar_conjuracao(
    dados: BaseDados,
    heranca: dict[str, Any],
    classe: dict[str, Any],
    subclasse: dict[str, Any] | None,
    conceito: dict[str, Any],
    modificadores: dict[str, int],
    talentos_classe_ids: list[str],
    nivel: int = 1,
    fonte_divina: str = "cura",
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Calcula ataque/CD de magia, espaços por dia, truques, magias N1, foco e inatas."""
    prof_magia_info = classe["proficiencias_iniciais"].get("magias")
    sub_id = subclasse["id"] if subclasse else ""
    classe_id = classe["id"]
    conj_por_trad = conceito.get("conjuracao_por_tradicao") or {}
    conj_rec = conceito.get("conjuracao_recomendada") or {}

    # ------------------------------------------------------------------
    # 1. Magias Inatas de Herança (independente da classe)
    # ------------------------------------------------------------------
    inatas: list[dict[str, Any]] = []
    tradicao_inata: str | None = None
    if heranca["id"] == "elfo_vidente":
        m = dados.magias.get("detectar_magia")
        if m:
            inatas.append(dict(m, frequencia="À vontade (Herança)"))
            tradicao_inata = "arcana"
    elif heranca["id"] == "gnomo_tocado_pelas_fadas":
        pool = [m for m in dados.magias.values() if "primal" in m.get("tradicoes", []) and "Truque Mágico" in m.get("tracos", [])]
        escolhido = rng.choice(pool[:6]) if (rng and pool) else (pool[0] if pool else None)
        if escolhido:
            inatas.append(dict(escolhido, frequencia="À vontade (Fada)"))
            tradicao_inata = "primal"
    elif heranca["id"] == "gnomo_manancial":
        trad_pref = conj_rec.get("tradicao") if conj_rec.get("tradicao") in {"arcana", "divina", "ocultista"} else "arcana"
        pool = [m for m in dados.magias.values() if trad_pref in m.get("tradicoes", []) and "Truque Mágico" in m.get("tracos", [])]
        escolhido = rng.choice(pool[:6]) if (rng and pool) else (pool[0] if pool else None)
        if escolhido:
            inatas.append(dict(escolhido, frequencia="À vontade (Herança)"))
            tradicao_inata = trad_pref

    # ------------------------------------------------------------------
    # 2. Conjurador Pleno vs Foco Marcial vs Não-conjurador
    # ------------------------------------------------------------------
    conjuracao_plena = classe_id in {"bardo", "clerigo", "druida", "feiticeiro", "mago"}
    possui_foco_monge = classe_id == "monge" and any(t in talentos_classe_ids for t in ("golpe_de_ki", "disparada_de_ki"))
    possui_foco_campeao = classe_id in _CLASSES_FOCO_CAR

    if conjuracao_plena:
        if prof_magia_info["tradicao"] == "conforme_linhagem" and subclasse:
            tradicao = subclasse["tradicao_magica"]
        else:
            tradicao = prof_magia_info["tradicao"]
        estilo = prof_magia_info["tipo_conjuracao"]  # "preparada" ou "espontanea"
        atr_conj = atributo_id(prof_magia_info["atributo_conjuracao"]) or "int"
        grau_ataque = prof_magia_info.get("ataques_magia", "treinado")
        grau_cd = prof_magia_info.get("cds_magia", "treinado")
    elif possui_foco_campeao or possui_foco_monge:
        tradicao = "divina" if possui_foco_campeao else "ocultista"
        estilo = None
        atr_conj = "car" if possui_foco_campeao else "sab"
        grau_ataque = "treinado"
        grau_cd = "treinado"
    elif inatas:
        tradicao = tradicao_inata
        estilo = None
        atr_conj = "car"
        grau_ataque = "treinado"
        grau_cd = "treinado"
    else:
        return {
            "eh_conjurador": False,
            "conjuracao_plena": False,
            "tradicao": None,
            "estilo": None,
            "ataque_magia": {"total": 0, "mod_atributo_chave": 0, "proficiencia": 0, "grau_proficiencia": "destreinado"},
            "cd_magia": {"total": 10, "mod_atributo_chave": 0, "proficiencia": 0, "grau_proficiencia": "destreinado"},
            "nivel_truque": math.ceil(nivel / 2),
            "espacos_nivel_1": 0,
            "fonte_divina": None,
            "truques": [],
            "magias_n1": [],
            "pontos_foco": 0,
            "magias_foco": [],
            "magias_inatas": [],
        }

    mod_conj = modificadores[atr_conj]
    prof_atk = bonus_proficiencia(grau_ataque, nivel)
    prof_cd = bonus_proficiencia(grau_cd, nivel)

    # ------------------------------------------------------------------
    # 3. Truques e Magias de 1º Círculo (para Conjuradores Plenos)
    # ------------------------------------------------------------------
    truques_selecionados: list[dict[str, Any]] = []
    magias_selecionadas: list[dict[str, Any]] = []
    espacos_n1 = 0
    fonte_divina_info: dict[str, Any] | None = None

    if conjuracao_plena and tradicao:
        conj_rec = conj_por_trad.get(tradicao) or conj_rec
        tabela = _tabela_magias_classe(classe) or {"truques_magicos": 5, "espacos_por_circulo": {"1": 2}}
        qtd_truques = int(tabela.get("truques_magicos", 5))
        espacos_n1 = int(tabela.get("espacos_por_circulo", {}).get("1", 2))
        if classe_id == "mago" and sub_id != "universalista":
            espacos_n1 += 1  # +1 espaço de escola arcana por nível

        if classe_id == "clerigo":
            fonte_divina_info = {
                "tipo": "Ferimento (Ferir)" if fonte_divina == "ferimento" else "Cura (Curar)",
                "espacos": 1 + max(0, modificadores["car"]),
                "circulo": 1,
            }

        tracos_pri = list(conj_rec.get("tracos_prioritarios", []))
        escolas_pri = list(conj_rec.get("escolas_prioritarias", []))
        truques_pri = list(conj_rec.get("truques_prioritarios", []))
        magias_n1_pri = list(conj_rec.get("magias_nivel_1_prioritarias", []))

        # Concedidas pela subclasse (Bardo, Feiticeiro, Mago)
        if subclasse:
            if "magia_adicionada_repertorio" in subclasse:
                m_rep = dados.resolver_magia(subclasse["magia_adicionada_repertorio"])
                if m_rep:
                    magias_n1_pri.insert(0, m_rep["id"])
            if "magias_concedidas" in subclasse:
                mc = subclasse["magias_concedidas"]
                m_t = dados.resolver_magia(mc.get("truque_magico"))
                m_1 = dados.resolver_magia(mc.get("1"))
                if m_t:
                    truques_pri.insert(0, m_t["id"])
                if m_1:
                    magias_n1_pri.insert(0, m_1["id"])
            if "magia_1_nivel_exemplo" in subclasse:
                m_ex = dados.resolver_magia(subclasse["magia_1_nivel_exemplo"])
                if m_ex:
                    magias_n1_pri.insert(0, m_ex["id"])

        ids_truques_usados: set[str] = set()
        truques_selecionados = _selecionar_magias_por_nivel(
            dados, tradicao, None, True, qtd_truques, truques_pri, tracos_pri, escolas_pri, ids_truques_usados, rng
        )

        # Quantidade de magias conhecidas/no grimório N1
        if classe_id == "mago":
            qtd_magias_n1 = 5  # Grimório inicial (5 comuns N1 + 1 escola = exibimos até 5 nos slots)
        elif classe_id == "bardo":
            qtd_magias_n1 = 3 if subclasse and subclasse.get("magia_adicionada_repertorio") else 2
        elif classe_id == "feiticeiro":
            qtd_magias_n1 = 3
        else:
            # Clérigo e Druida conhecem toda a lista comum; preparam `espacos_n1`
            qtd_magias_n1 = espacos_n1

        ids_magias_usados: set[str] = set()
        magias_selecionadas = _selecionar_magias_por_nivel(
            dados, tradicao, 1, False, qtd_magias_n1, magias_n1_pri, tracos_pri, escolas_pri, ids_magias_usados, rng
        )

        # Marca quais ficam preparadas na ficha oficial
        for idx, m in enumerate(magias_selecionadas):
            m = dict(m)
            m["preparada"] = (estilo == "preparada" and idx < espacos_n1)
            magias_selecionadas[idx] = m

    # ------------------------------------------------------------------
    # 4. Magias de Foco & Pontos de Foco
    # ------------------------------------------------------------------
    pontos_foco = 0
    foco_selecionadas: list[dict[str, Any]] = []

    def add_foco(m: dict[str, Any] | None) -> None:
        if m and m["id"] not in {x["id"] for x in foco_selecionadas}:
            foco_selecionadas.append(m)

    if classe_id == "bardo":
        pontos_foco = 1
        add_foco(dados.magias_foco.get("inspirar_coragem"))
        add_foco(dados.magias_foco.get("contraperformance"))
        for tid in talentos_classe_ids:
            add_foco(dados.magias_foco.get(tid))
    elif classe_id == "campeao":
        pontos_foco = 1
        add_foco(dados.magias_foco.get("imposicao_de_maos"))
    elif classe_id == "clerigo" and "iniciado_no_dominio" in talentos_classe_ids:
        pontos_foco = 1
        add_foco(_resolver_magia_foco_dominio(dados, conceito, rng))
    elif classe_id == "druida" and subclasse:
        pontos_foco = 1 + int(subclasse.get("pontos_foco_adicionais") or 0)
        add_foco(dados.resolver_magia_foco(subclasse.get("magia_ordem")))
    elif classe_id == "feiticeiro" and subclasse:
        pontos_foco = 1
        nome_fi = subclasse.get("magias_de_linhagem", {}).get("inicial")
        add_foco(dados.resolver_magia_foco(nome_fi))
    elif classe_id == "mago" and subclasse and sub_id != "universalista":
        pontos_foco = 1
        add_foco(dados.resolver_magia_foco(subclasse.get("magia_de_escola")))
    elif possui_foco_monge:
        pontos_foco = 1
        for tid in talentos_classe_ids:
            if tid in ("golpe_de_ki", "disparada_de_ki"):
                add_foco(dados.magias_foco.get(tid))

    return {
        "eh_conjurador": True,
        "conjuracao_plena": conjuracao_plena,
        "tradicao": tradicao,
        "estilo": estilo,
        "ataque_magia": {
            "total": mod_conj + prof_atk,
            "mod_atributo_chave": mod_conj,
            "proficiencia": prof_atk,
            "grau_proficiencia": grau_ataque,
        },
        "cd_magia": {
            "total": 10 + mod_conj + prof_cd,
            "mod_atributo_chave": mod_conj,
            "proficiencia": prof_cd,
            "grau_proficiencia": grau_cd,
        },
        "nivel_truque": math.ceil(nivel / 2),
        "espacos_nivel_1": espacos_n1,
        "fonte_divina": fonte_divina_info,
        "truques": truques_selecionados,
        "magias_n1": magias_selecionadas,
        "pontos_foco": pontos_foco,
        "magias_foco": foco_selecionadas,
        "magias_inatas": inatas,
    }


def preencher_bloco_conjuracao_ficha(
    bloco_conjuracao: dict[str, Any],
    resumo_magias: dict[str, Any],
) -> None:
    """Popula `ficha['conjuracao']` respeitando exatamente os slots oficiais da Página 4."""
    bloco_conjuracao["ataque_magia"] = resumo_magias["ataque_magia"]
    bloco_conjuracao["cd_magia"] = resumo_magias["cd_magia"]
    bloco_conjuracao["nivel_truque"] = resumo_magias["nivel_truque"]

    trad = resumo_magias.get("tradicao")
    if trad and trad in bloco_conjuracao["tradicoes_marcadas"]:
        bloco_conjuracao["tradicoes_marcadas"][trad] = True

    estilo = resumo_magias.get("estilo")
    if estilo == "preparada":
        bloco_conjuracao["estilo_conjuracao"]["preparada"] = True
    elif estilo == "espontanea":
        bloco_conjuracao["estilo_conjuracao"]["espontanea"] = True

    esp_n1 = resumo_magias.get("espacos_nivel_1", 0)
    bloco_conjuracao["espacos_magia_por_dia"]["1"] = esp_n1
    if estilo == "espontanea":
        bloco_conjuracao["espacos_magia_espontanea_remanescentes"]["1"] = esp_n1

    # Truques (até 7 slots)
    for idx, m in enumerate(resumo_magias["truques"][: len(bloco_conjuracao["truques_magicos"])]):
        slot = bloco_conjuracao["truques_magicos"][idx]
        slot["nome"] = m["nome"]
        slot["nivel"] = 0
        slot["acoes"] = _formatar_acoes(m.get("acoes"))
        slot["componentes"] = _formatar_componentes(m.get("componentes"))
        slot["anotacoes"] = m.get("resumo_lista") or m.get("escola") or ""
        slot["preparada"] = True

    # Magias Inatas (até 2 slots)
    for idx, m in enumerate(resumo_magias["magias_inatas"][: len(bloco_conjuracao["magias_inatas"])]):
        slot = bloco_conjuracao["magias_inatas"][idx]
        slot["nome"] = m["nome"]
        slot["nivel"] = 0 if "Truque Mágico" in m.get("tracos", []) else m.get("nivel")
        slot["acoes"] = _formatar_acoes(m.get("acoes"))
        slot["componentes"] = _formatar_componentes(m.get("componentes"))
        slot["frequencia"] = m.get("frequencia", "À vontade")
        slot["anotacoes"] = m.get("resumo_lista") or ""

    # Pontos de Foco & Magias de Foco (até 4 slots)
    bloco_conjuracao["magias_foco"]["pontos_foco"] = {
        "atuais": resumo_magias["pontos_foco"],
        "maximo": resumo_magias["pontos_foco"],
    }
    for idx, m in enumerate(resumo_magias["magias_foco"][: len(bloco_conjuracao["magias_foco"]["slots"])]):
        slot = bloco_conjuracao["magias_foco"]["slots"][idx]
        slot["nome"] = m["nome"]
        slot["nivel"] = m.get("nivel")
        slot["acoes"] = _formatar_acoes(m.get("acoes"))
        slot["componentes"] = _formatar_componentes(m.get("componentes"))
        slot["anotacoes"] = m.get("escola") or ""

    # Magias N1 (até 32 slots) — inclui Fonte Divina extra do Clérigo quando aplicável
    magias_lista = list(resumo_magias["magias_n1"])
    fonte = resumo_magias.get("fonte_divina")
    if fonte and len(magias_lista) < len(bloco_conjuracao["magias"]):
        nome_magia_fonte = "Ferir" if "ferimento" in fonte["tipo"].lower() else "Curar"
        magias_lista.append(
            {
                "nome": f"{nome_magia_fonte} (Fonte Divina ×{fonte['espacos']})",
                "nivel": 1,
                "acoes": "1 a 3",
                "componentes": ["somático", "verbal"],
                "preparada": True,
                "resumo_lista": f"{fonte['espacos']} espaços extras de Fonte Divina ({fonte['tipo']})",
            }
        )

    for idx, m in enumerate(magias_lista[: len(bloco_conjuracao["magias"])]):
        slot = bloco_conjuracao["magias"][idx]
        slot["nome"] = m["nome"]
        slot["nivel"] = m.get("nivel", 1)
        slot["acoes"] = _formatar_acoes(m.get("acoes"))
        slot["componentes"] = _formatar_componentes(m.get("componentes"))
        slot["preparada"] = bool(m.get("preparada", False))
        slot["anotacoes"] = m.get("resumo_lista") or m.get("escola") or ""
