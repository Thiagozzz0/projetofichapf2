"""Orquestrador principal de geração de fichas de Castles & Crusades (1ª Ed. Brasileira)."""

from __future__ import annotations

from typing import Any

from motor_cc.atributos import (
    METODOS_GERACAO,
    ORDEM_ATRIBUTOS,
    resolver_atributos_personagem,
    rolar_atributos,
)
from motor_cc.combate import (
    REGRAS_PV,
    calcular_ataques,
    calcular_ca,
    calcular_pv,
    coletar_habilidades,
    obter_linha_progressao,
    obter_proximo_ppe,
)
from motor_cc.dados import (
    CATEGORIAS_EQUIPAMENTOS,
    carregar_equipamentos,
    carregar_listas_magias,
    listar_classes,
    listar_disposicoes,
    listar_racas,
    mapa_classes,
    mapa_disposicoes,
    mapa_racas,
)
from motor_cc.equipamentos import processar_equipamentos
from motor_cc.magias import calcular_conjuracao


def obter_opcoes_criacao() -> dict[str, Any]:
    """Retorna todas as opções estruturadas para popular o formulário /cc."""
    eq = carregar_equipamentos()
    equipamentos_por_categoria = {cat: eq.get(cat, []) for cat in CATEGORIAS_EQUIPAMENTOS}

    return {
        "sistema": "Castles & Crusades (1ª Edição Brasileira)",
        "metodos_atributos": list(METODOS_GERACAO.values()),
        "regras_pv": list(REGRAS_PV.values()),
        "ordem_atributos": list(ORDEM_ATRIBUTOS),
        "racas": [
            {
                "id": r["id"],
                "nome": r["nome"],
                "tamanho": r["tamanho"],
                "movimento_m": r["movimento_m"],
                "total_atributos_primarios": r["total_atributos_primarios"],
                "primarios_escolha_jogador": r["primarios_escolha_jogador"],
                "modificadores_atributos": r.get("modificadores_atributos", {}),
                "idiomas": r.get("idiomas", []),
                "linhagens": r.get("linhagens"),
                "tracos": r.get("tracos", []),
            }
            for r in listar_racas()
        ],
        "classes": [
            {
                "id": c["id"],
                "nome": c["nome"],
                "atributo_principal": c["atributo_principal"],
                "dado_vida": c["dado_vida"],
                "pv_apos_nivel_10": c.get("pv_apos_nivel_10"),
                "disposicao": c.get("disposicao"),
                "armas": c.get("armas"),
                "armaduras": c.get("armaduras"),
                "conjurador": bool(c.get("conjurador", False)),
                "tradicao": c.get("conjuracao", {}).get("tradicao") if c.get("conjurador") else None,
                "atributo_conjuracao": c.get("conjuracao", {}).get("atributo_conjuracao") if c.get("conjurador") else None,
                "conjuracao": c.get("conjuracao") if c.get("conjurador") else None,
                "ouro_inicial": eq.get("moedas", {}).get("ouro_inicial_por_classe", {}).get(c["id"]),
            }
            for c in listar_classes()
        ],
        "disposicoes": list(listar_disposicoes()),
        "equipamentos": equipamentos_por_categoria,
        "listas_magias": carregar_listas_magias(),
    }


def _resolver_idiomas(raca: dict[str, Any], classe: dict[str, Any], mod_int: int, idiomas_extras: list[str] | None) -> list[str]:
    idiomas: list[str] = []
    # Idiomas raciais iniciais (Comum + idioma próprio da raça)
    raca_idiomas = list(raca.get("idiomas", []))
    if raca_idiomas:
        for idi in raca_idiomas[:2]:
            if idi not in idiomas:
                idiomas.append(idi)
    else:
        idiomas.append("Comum")

    # Druídico para druidas
    if classe["id"] == "druida" and "Druídico" not in idiomas:
        idiomas.append("Druídico")

    # Idiomas extras escolhidos pelo jogador (ou por bônus de INT positivo)
    for extra in (idiomas_extras or []):
        limpo = str(extra).strip()
        if limpo and limpo not in idiomas:
            idiomas.append(limpo)

    return idiomas


def gerar_ficha_cc(payload: dict[str, Any]) -> dict[str, Any]:
    """Gera a ficha completa e validada de um personagem de Castles & Crusades."""
    raca_id = str(payload.get("raca_id", "")).strip()
    classe_id = str(payload.get("classe_id", "")).strip()
    nivel = int(payload.get("nivel", 1))
    metodo_geracao = str(payload.get("metodo_geracao", "classico_3d6_livre")).strip()

    racas = mapa_racas()
    classes = mapa_classes()
    disposicoes = mapa_disposicoes()

    if raca_id not in racas:
        raise ValueError(f"Raça inválida ou não informada: {raca_id!r}")
    if classe_id not in classes:
        raise ValueError(f"Classe inválida ou não informada: {classe_id!r}")
    if nivel < 1 or nivel > 24:
        raise ValueError(f"Nível deve estar entre 1 e 24 (recebido: {nivel}).")

    raca = racas[raca_id]
    classe = classes[classe_id]

    # 1. Atributos, modificadores C&C e Sistema SIEGE
    valores_base = payload.get("atributos_base")
    if not valores_base:
        rol = rolar_atributos(metodo=metodo_geracao, seed=payload.get("seed"))
        valores_base = rol["valores"]

    bloco_attr = resolver_atributos_personagem(
        valores_base=valores_base,
        raca_id=raca_id,
        classe_id=classe_id,
        primarios_escolhidos=payload.get("primarios_escolhidos"),
        metodo_geracao=metodo_geracao,
        linhagem_meio_elfo=payload.get("linhagem_meio_elfo"),
        atributo_secundario_meio_elfo=payload.get("atributo_secundario_meio_elfo"),
    )
    attrs = bloco_attr["atributos"]

    # 2. Progressão da classe (BpA, PPE, Próximo PPE)
    linha_prog = obter_linha_progressao(classe, nivel)
    bpa = int(linha_prog["bpa"])
    ppe_atual = int(payload.get("exp") if payload.get("exp") is not None else linha_prog["ppe"])
    prox_ppe = obter_proximo_ppe(classe, nivel)

    # 3. Equipamentos, Moedas e Sobrecarga (SB)
    bloco_eq = processar_equipamentos(
        classe_id=classe_id,
        valor_forca=attrs["forca"]["valor"],
        forca_primario=attrs["forca"]["primario"],
        constituicao_primario=attrs["constituicao"]["primario"],
        movimento_base_m=float(raca["movimento_m"]),
        armadura_id=payload.get("armadura_id"),
        escudo_id=payload.get("escudo_id"),
        elmo_id=payload.get("elmo_id"),
        armas_ids=payload.get("armas_ids") or [],
        itens_ids=payload.get("itens_ids") or [],
        modo_ouro=str(payload.get("modo_ouro", "media")),
        ouro_manual_po=payload.get("ouro_manual_po"),
        seed=payload.get("seed"),
    )

    # 4. PV, CA e Ataques
    bloco_pv = calcular_pv(
        classe=classe,
        nivel=nivel,
        mod_con=attrs["constituicao"]["modificador"],
        regra_pv=str(payload.get("regra_pv", "opcional_1_maximo_n1")),
        pv_por_nivel_manual=payload.get("pv_por_nivel_manual"),
        seed=payload.get("seed"),
    )

    bloco_ca = calcular_ca(
        mod_des=attrs["destreza"]["modificador"],
        armadura=bloco_eq["armadura"],
        escudo=bloco_eq["escudo"],
        elmo=bloco_eq["elmo"],
        bonus_magia=int(payload.get("ca_bonus_magia", 0)),
        bonus_var=int(payload.get("ca_bonus_var", 0)),
        sobrecarregado=bloco_eq["sobrecarga"]["perde_bonus_des_ca"],
    )

    ataques = calcular_ataques(
        armas=bloco_eq["armas"],
        bpa=bpa,
        mod_for=attrs["forca"]["modificador"],
        mod_des=attrs["destreza"]["modificador"],
    )

    # 5. Habilidades (Raça e Classe)
    habilidades = coletar_habilidades(
        raca=raca,
        classe=classe,
        nivel=nivel,
        linhagem_meio_elfo=bloco_attr["linhagem_meio_elfo"],
    )

    # 6. Conjuração / Magias
    bloco_magias = calcular_conjuracao(
        classe=classe,
        nivel=nivel,
        atributos_detalhes=attrs,
        feiticos_escolhidos=payload.get("feiticos_escolhidos"),
        auto_completar=bool(payload.get("auto_completar_feiticos", False)),
    )

    # 7. Disposição e Idiomas
    disp_id = str(payload.get("disposicao_id", "neutro")).strip()
    disp_obj = disposicoes.get(disp_id)
    disp_nome = disp_obj["nome"] if disp_obj else disp_id

    idiomas = _resolver_idiomas(
        raca=raca,
        classe=classe,
        mod_int=attrs["inteligencia"]["modificador"],
        idiomas_extras=payload.get("idiomas_extras"),
    )

    avisos = list(bloco_eq.get("avisos", [])) + list(bloco_magias.get("avisos", []))

    return {
        "sistema": "Castles & Crusades (1ª Edição Brasileira)",
        "cabecalho": {
            "nome": str(payload.get("nome") or "Sem Nome").strip(),
            "titulos": str(payload.get("titulos") or "").strip(),
            "jogador": str(payload.get("jogador") or "").strip(),
            "raca_id": raca_id,
            "raca_nome": raca["nome"],
            "linhagem_meio_elfo": bloco_attr["linhagem_meio_elfo"],
            "classe_id": classe_id,
            "classe_nome": classe["nome"],
            "nivel": nivel,
            "disposicao_id": disp_id,
            "disposicao_nome": disp_nome,
            "idiomas": idiomas,
            "movimento_base_m": float(raca["movimento_m"]),
            "movimento_m": bloco_eq["sobrecarga"]["movimento_ajustado_m"],
            "exp": ppe_atual,
            "prox_exp": prox_ppe,
            "metodo_geracao": bloco_attr["metodo_geracao"],
            "rotulo_metodo": bloco_attr["rotulo_metodo"],
        },
        "atributos": bloco_attr,
        "combate": {
            "bpa": bpa,
            "pv": bloco_pv,
            "ca": bloco_ca,
            "ataques": ataques,
            "ferimentos_e_condicoes": str(payload.get("ferimentos_e_condicoes") or "").strip(),
        },
        "habilidades": habilidades,
        "equipamentos": bloco_eq,
        "magias": bloco_magias,
        "notas": {
            "itens_magicos": list(payload.get("itens_magicos") or []),
            "pocoes": list(payload.get("pocoes") or []),
            "anotacoes": str(payload.get("anotacoes") or "").strip(),
        },
        "avisos": avisos,
    }
