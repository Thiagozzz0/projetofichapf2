"""Cálculo de conjuração, seleção temática de magias, truques, foco e magias inatas."""

from __future__ import annotations

import math
import random
from typing import Any

from .dados import BaseDados
from .util import atributo_id, bonus_proficiencia, normalizar, slugify


_CLASSES_FOCO_CAR = {"campeao"}
_CLASSES_FOCO_SAB = {"monge"}
CLASSES_CONJURACAO_PLENA = frozenset({"bardo", "clerigo", "druida", "feiticeiro", "mago"})
TRADICOES_OFICIAIS = ("arcana", "divina", "ocultista", "primal")


def listar_catalogo_magias_n1(dados: BaseDados) -> dict[str, Any]:
    """Retorna catálogo de Truques Mágicos (N0) e Magias de 1º Círculo a partir de magias01/02.json."""
    por_id: dict[str, dict[str, Any]] = {}
    por_tradicao: dict[str, dict[str, list[str]]] = {
        t: {"truques": [], "nivel_1": []} for t in TRADICOES_OFICIAIS
    }

    for m in dados.magias.values():
        tracos = m.get("tracos") or []
        eh_truque = "Truque Mágico" in tracos
        nivel_m = m.get("nivel")
        if not eh_truque and nivel_m != 1:
            continue
        mid = m["id"]
        trads = [t for t in (m.get("tradicoes") or []) if t in TRADICOES_OFICIAIS]
        por_id[mid] = {
            "id": mid,
            "nome": m["nome"],
            "nivel": 0 if eh_truque else 1,
            "eh_truque": eh_truque,
            "tradicoes": trads,
            "escola": m.get("escola") or "",
            "acoes": _formatar_acoes(m.get("acoes")),
            "raridade": m.get("raridade") or "Comum",
            "resumo": m.get("resumo_lista") or (m.get("descricao") or "")[:160],
        }
        chave_lista = "truques" if eh_truque else "nivel_1"
        for t in trads:
            por_tradicao[t][chave_lista].append(mid)

    for t in TRADICOES_OFICIAIS:
        por_tradicao[t]["truques"].sort(key=lambda mid: normalizar(por_id[mid]["nome"]))
        por_tradicao[t]["nivel_1"].sort(key=lambda mid: normalizar(por_id[mid]["nome"]))

    return {"por_id": por_id, "por_tradicao": por_tradicao}


def resumo_conjuracao_classe(dados: BaseDados, classe: dict[str, Any]) -> dict[str, Any] | None:
    """Extrai de dados/classes*.json as regras de conjuração de 1º nível da classe e subclasses."""
    cid = classe["id"]
    if cid not in CLASSES_CONJURACAO_PLENA:
        return None
    prof = classe["proficiencias_iniciais"].get("magias") or {}
    tabela = _tabela_magias_classe(classe) or {"truques_magicos": 5, "espacos_por_circulo": {"1": 2}}
    qtd_truques = int(tabela.get("truques_magicos", 5))
    espacos_base = int(tabela.get("espacos_por_circulo", {}).get("1", 2))
    trad_raw = prof.get("tradicao")
    trad_fixa = trad_raw if trad_raw in TRADICOES_OFICIAIS else None

    subclasses_info: dict[str, dict[str, Any]] = {}
    for sub in classe.get("subclasses", {}).get("opcoes", []):
        sid = sub["id"]
        trad_sub = sub.get("tradicao_magica") if sub.get("tradicao_magica") in TRADICOES_OFICIAIS else trad_fixa
        truque_fixo_id = None
        magia_n1_fixa_id = None

        if "magia_adicionada_repertorio" in sub:
            m_rep = dados.resolver_magia(sub["magia_adicionada_repertorio"])
            if m_rep:
                magia_n1_fixa_id = m_rep["id"]
        if "magias_concedidas" in sub:
            mc = sub["magias_concedidas"]
            m_t = dados.resolver_magia(mc.get("truque_magico"))
            m_1 = dados.resolver_magia(mc.get("1"))
            if m_t:
                truque_fixo_id = m_t["id"]
            if m_1:
                magia_n1_fixa_id = m_1["id"]

        esp_sub = espacos_base
        if cid == "mago":
            if sid != "universalista":
                esp_sub = espacos_base + 1
                qtd_n1_sub = 6
            else:
                qtd_n1_sub = 5
        elif cid == "bardo":
            qtd_n1_sub = 3 if magia_n1_fixa_id else 2
        elif cid == "feiticeiro":
            qtd_n1_sub = 3
        else:
            qtd_n1_sub = esp_sub

        subclasses_info[sid] = {
            "tradicao": trad_sub,
            "truque_fixo_id": truque_fixo_id,
            "magia_n1_fixa_id": magia_n1_fixa_id,
            "espacos_n1": esp_sub,
            "qtd_magias_n1": qtd_n1_sub,
            "eh_universalista": cid == "mago" and sid == "universalista",
        }

    return {
        "tradicao_fixa": trad_fixa,
        "estilo": prof.get("tipo_conjuracao", "preparada"),
        "atributo_conjuracao": atributo_id(prof.get("atributo_conjuracao")) or "int",
        "qtd_truques": qtd_truques,
        "espacos_n1_base": espacos_base,
        "subclasses": subclasses_info,
    }


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
    extras_permitidas_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Seleciona magias comuns da tradição priorizando a lista do conceito e depois os traços/escolas."""
    escolhidas: list[dict[str, Any]] = []
    extras = extras_permitidas_ids or set()

    def tentar_adicionar(magia: dict[str, Any] | None) -> None:
        if not magia or len(escolhidas) >= quantidade:
            return
        mid = magia["id"]
        if mid in ja_selecionadas:
            return
        if tradicao not in magia.get("tradicoes", []) and mid not in extras:
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
    divindade: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    candidatos = [
        m for m in dados.magias_foco.values()
        if m.get("classe_id") == "clerigo" and m.get("nivel") == 1
    ]
    if divindade and divindade.get("dominios"):
        doms_div = {normalizar(d) for d in divindade["dominios"]}
        filtrados = [m for m in candidatos if normalizar(m.get("dominio")) in doms_div]
        if filtrados:
            candidatos = filtrados
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
    divindade: dict[str, Any] | None = None,
    talento_ancestral_id: str | None = None,
    escolhas_magias: dict[str, Any] | None = None,
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

    inatas_ids = {m["id"] for m in inatas}
    if talento_ancestral_id == "magia_extraterrena":
        pool_ext = [
            m for m in dados.magias.values()
            if "arcana" in m.get("tradicoes", []) and "Truque Mágico" in m.get("tracos", []) and m["id"] not in inatas_ids
        ]
        escolhido_ext = rng.choice(pool_ext[:8]) if (rng and pool_ext) else (pool_ext[0] if pool_ext else None)
        if escolhido_ext:
            inatas.append(dict(escolhido_ext, frequencia="À vontade (Talento Ancestral)"))
            tradicao_inata = tradicao_inata or "arcana"
    elif talento_ancestral_id == "magia_do_primeiro_mundo":
        pool_pm = [
            m for m in dados.magias.values()
            if "primal" in m.get("tradicoes", []) and "Truque Mágico" in m.get("tracos", []) and m["id"] not in inatas_ids
        ]
        escolhido_pm = rng.choice(pool_pm[:8]) if (rng and pool_pm) else (pool_pm[0] if pool_pm else None)
        if escolhido_pm:
            inatas.append(dict(escolhido_pm, frequencia="À vontade (Talento Ancestral)"))
            tradicao_inata = tradicao_inata or "primal"

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
    esc_m = escolhas_magias or {}
    modo_mag_raw = normalizar(str(esc_m.get("modo") or "procedural"))
    modo_mag = (
        "aleatorio"
        if modo_mag_raw in ("aleatorio", "aleatoria", "random")
        else (
            "personalizado"
            if modo_mag_raw in ("personalizado", "manual")
            or any(
                esc_m.get(k) not in (None, "", "procedural", "aleatorio", [])
                for k in ("truques_ids", "magias_n1_ids")
            )
            else "procedural"
        )
    )
    truques_manuais_aplicados: list[str] = []
    magias_n1_manuais_aplicadas: list[str] = []
    qtd_truques_total = 0
    qtd_magias_n1_total = 0

    if conjuracao_plena and tradicao:
        conj_rec = conj_por_trad.get(tradicao) or conj_rec
        tabela = _tabela_magias_classe(classe) or {"truques_magicos": 5, "espacos_por_circulo": {"1": 2}}
        qtd_truques = int(tabela.get("truques_magicos", 5))
        qtd_truques_total = qtd_truques
        espacos_n1 = int(tabela.get("espacos_por_circulo", {}).get("1", 2))
        if classe_id == "mago" and sub_id != "universalista":
            espacos_n1 += 1  # +1 espaço de escola arcana por nível

        if classe_id == "clerigo":
            fonte_divina_info = {
                "tipo": "Ferimento (Ferir)" if fonte_divina == "ferimento" else "Cura (Curar)",
                "espacos": 1 + max(0, modificadores["car"]),
                "circulo": 1,
            }

        tracos_pri = [] if modo_mag == "aleatorio" else list(conj_rec.get("tracos_prioritarios", []))
        escolas_pri = [] if modo_mag == "aleatorio" else list(conj_rec.get("escolas_prioritarias", []))
        truques_pri = [] if modo_mag == "aleatorio" else list(conj_rec.get("truques_prioritarios", []))
        magias_n1_pri = [] if modo_mag == "aleatorio" else list(conj_rec.get("magias_nivel_1_prioritarias", []))

        # Magias fixas concedidas pela subclasse (Bardo Musa, Feiticeiro Linhagem)
        truques_fixos_sub: list[str] = []
        magias_n1_fixas_sub: list[str] = []
        extras_truques_sub: set[str] = set()
        extras_magias_sub: set[str] = set()

        if subclasse:
            if "magia_adicionada_repertorio" in subclasse:
                m_rep = dados.resolver_magia(subclasse["magia_adicionada_repertorio"])
                if m_rep:
                    magias_n1_fixas_sub.append(m_rep["id"])
                    extras_magias_sub.add(m_rep["id"])
            if "magias_concedidas" in subclasse:
                mc = subclasse["magias_concedidas"]
                m_t = dados.resolver_magia(mc.get("truque_magico"))
                m_1 = dados.resolver_magia(mc.get("1"))
                if m_t:
                    truques_fixos_sub.append(m_t["id"])
                    extras_truques_sub.add(m_t["id"])
                if m_1:
                    magias_n1_fixas_sub.append(m_1["id"])
                    extras_magias_sub.add(m_1["id"])
            if "magia_1_nivel_exemplo" in subclasse and modo_mag == "procedural":
                m_ex = dados.resolver_magia(subclasse["magia_1_nivel_exemplo"])
                if m_ex:
                    magias_n1_pri.insert(0, m_ex["id"])

        # Quantidade de magias conhecidas/no grimório N1
        if classe_id == "mago":
            qtd_magias_n1 = 6 if (subclasse and sub_id != "universalista") else 5
        elif classe_id == "bardo":
            qtd_magias_n1 = 3 if subclasse and subclasse.get("magia_adicionada_repertorio") else 2
        elif classe_id == "feiticeiro":
            qtd_magias_n1 = 3
        else:
            qtd_magias_n1 = espacos_n1
        qtd_magias_n1_total = qtd_magias_n1

        extras_divinas: set[str] = set()
        if classe_id == "clerigo" and divindade:
            mag_div_1 = (divindade.get("magias_clerigo") or {}).get("1")
            if mag_div_1 and mag_div_1 in dados.magias:
                extras_divinas.add(mag_div_1)
                if modo_mag == "procedural" and mag_div_1 not in magias_n1_pri:
                    magias_n1_pri.append(mag_div_1)

        def _validar_lista_manual_magia(
            raw_ids: Any,
            eh_truque_alvo: bool,
            limite_total: int,
            fixas_ids: list[str],
            extras_perm: set[str],
            rotulo: str,
        ) -> list[str]:
            if raw_ids is None or (isinstance(raw_ids, str) and normalizar(raw_ids) in ("", "procedural", "aleatorio", "auto")):
                return []
            if not isinstance(raw_ids, list):
                raise ValueError(f"Campo '{rotulo}' deve ser uma lista de IDs de magias.")
            vistos_m: set[str] = set()
            validas_novas: list[str] = []
            fixas_set = set(fixas_ids)
            for item in raw_ids:
                mid = str(item).strip()
                m_obj = dados.magias.get(mid)
                if not m_obj:
                    raise ValueError(f"Magia desconhecida em '{rotulo}': '{mid}'.")
                eh_t = "Truque Mágico" in (m_obj.get("tracos") or [])
                if eh_truque_alvo and not eh_t:
                    raise ValueError(f"'{m_obj['nome']}' não é um Truque Mágico.")
                if not eh_truque_alvo and (eh_t or m_obj.get("nivel") != 1):
                    raise ValueError(f"'{m_obj['nome']}' não é uma magia de 1º círculo.")
                if tradicao not in (m_obj.get("tradicoes") or []) and mid not in extras_perm:
                    raise ValueError(
                        f"'{m_obj['nome']}' não pertence à tradição '{tradicao}' de {classe['nome']}."
                    )
                if mid in vistos_m:
                    raise ValueError(f"Magia duplicada em '{rotulo}': '{m_obj['nome']}'.")
                vistos_m.add(mid)
                if mid not in fixas_set:
                    validas_novas.append(mid)
            vagas_livres = max(0, limite_total - len(fixas_set))
            if len(validas_novas) > vagas_livres:
                raise ValueError(
                    f"Você selecionou {len(validas_novas)} opções em '{rotulo}', mas há apenas "
                    f"{vagas_livres} vaga(s) livre(s) além das fixas da subclasse."
                )
            return validas_novas

        if modo_mag == "personalizado":
            truques_manuais_aplicados = _validar_lista_manual_magia(
                esc_m.get("truques_ids"), True, qtd_truques, truques_fixos_sub, extras_truques_sub, "truques_ids"
            )
            magias_n1_manuais_aplicadas = _validar_lista_manual_magia(
                esc_m.get("magias_n1_ids"),
                False,
                qtd_magias_n1,
                magias_n1_fixas_sub,
                extras_magias_sub | extras_divinas,
                "magias_n1_ids",
            )

        ids_truques_usados: set[str] = set()
        truques_ordem = [*truques_fixos_sub, *truques_manuais_aplicados, *truques_pri]
        truques_selecionados = _selecionar_magias_por_nivel(
            dados,
            tradicao,
            None,
            True,
            qtd_truques,
            truques_ordem,
            tracos_pri,
            escolas_pri,
            ids_truques_usados,
            rng,
            extras_permitidas_ids=extras_truques_sub,
        )
        if talento_ancestral_id == "truque_magico_adaptado" and truques_selecionados and modo_mag != "personalizado":
            pool_adapt = [
                m for m in dados.magias.values()
                if "Truque Mágico" in m.get("tracos", [])
                and tradicao not in m.get("tradicoes", [])
                and m["id"] not in ids_truques_usados
            ]
            if pool_adapt:
                adaptado = rng.choice(pool_adapt[:8]) if rng else pool_adapt[0]
                truques_selecionados[-1] = adaptado
                ids_truques_usados.add(adaptado["id"])

        ids_magias_usados: set[str] = set()
        magias_ordem = [*magias_n1_fixas_sub, *magias_n1_manuais_aplicadas, *magias_n1_pri]
        magias_selecionadas = _selecionar_magias_por_nivel(
            dados,
            tradicao,
            1,
            False,
            qtd_magias_n1,
            magias_ordem,
            tracos_pri,
            escolas_pri,
            ids_magias_usados,
            rng,
            extras_permitidas_ids=extras_magias_sub | extras_divinas,
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
        add_foco(_resolver_magia_foco_dominio(dados, conceito, rng, divindade=divindade))
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
        "escolhas_magias": {
            "modo": modo_mag,
            "tradicao": tradicao,
            "qtd_truques_total": qtd_truques_total,
            "qtd_magias_n1_total": qtd_magias_n1_total,
            "truques_manuais": truques_manuais_aplicados,
            "magias_n1_manuais": magias_n1_manuais_aplicadas,
        },
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
