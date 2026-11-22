"""Gerador e validador de dados/regras_especificas.json (exceções e regras transversais PF2E)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
DIR_DADOS = RAIZ_PROJETO / "dados"
CAMINHO_SAIDA = DIR_DADOS / "regras_especificas.json"


def construir_dados() -> dict[str, Any]:
    """Monta o catálogo central de regras específicas e exceções que alteram cálculos ou estrutura da ficha."""
    return {
        "fonte": {
            "titulo": "Regras Específicas, Exceções Estruturais e Acúmulo de Bônus (PF2E Níveis 1–20)",
            "proposito": (
                "Centralizar regras transversais e exceções mecânicas que alteram fórmulas padrão "
                "ou a estrutura normal da ficha sem quebrar o schema dos JSONs de capítulos."
            ),
            "sistema": "Pathfinder 2ª Edição (Livro Básico)",
            "referencias": [
                "Cap. 1 (Criação de Personagem e Subindo de Nível)",
                "Cap. 2 (Ancestralidades e Heranças)",
                "Cap. 5 (Talentos)",
                "Cap. 9 (Jogando o Jogo — Bônus, Penalidades e Condição Morrendo)",
            ],
        },
        "pontos_de_vida": {
            "regra_ancestralidade": {
                "aplicar_somente_nivel_1": True,
                "multiplica_por_nivel": False,
                "arquivo_origem": "ancestralidades_biografias.json",
                "campo_base_ancestralidade": "pontos_vida",
                "campo_substituto_heranca": "pv_ancestral_substituto",
                "observacao": (
                    "Os Pontos de Vida da ancestralidade (ou substituto de herança, como Goblin Inquebrável) "
                    "são somados uma única vez no 1º nível e nunca são multiplicados ao subir de nível."
                ),
            },
            "regra_classe_e_constituicao": {
                "multiplica_por_nivel": True,
                "campo_classe": "pontos_de_vida_por_nivel",
                "atributo_somado": "con",
                "retroativo_ao_aumentar_con": True,
                "minimo_ganho_por_nivel": 1,
                "formula_total": (
                    "max(1, pv_ancestralidade + (pv_classe + mod_con) * nivel "
                    "+ bonus_pv_por_nivel * nivel + bonus_pv_fixos)"
                ),
                "observacao": (
                    "Ao elevar Constituição nos níveis 5, 10, 15 ou 20 (ou por outros meios permanentes), "
                    "o novo modificador de CON aplica-se retroativamente a todos os níveis."
                ),
            },
            "modificadores_escalonados_por_nivel": [
                {
                    "id": "vitalidade",
                    "nome": "Vitalidade",
                    "origem_arquivo": "talentos.json",
                    "tipo_origem": "talento_geral",
                    "nivel_minimo": 1,
                    "tipo_bonus": "sem_tipo",
                    "pv_por_nivel": 1,
                    "acumula_com": ["firmeza_da_montanha"],
                    "efeito_secundario": "Reduz a CD base de testes de recuperação sob morrendo de 10 para 9.",
                },
                {
                    "id": "firmeza_da_montanha",
                    "nome": "Firmeza da Montanha",
                    "origem_arquivo": "ancestralidades_biografias.json",
                    "tipo_origem": "talento_ancestralidade",
                    "ancestralidade_id": "anao",
                    "nivel_minimo": 9,
                    "tipo_bonus": "sem_tipo",
                    "pv_por_nivel": 1,
                    "acumula_com": ["vitalidade"],
                    "efeito_secundario": (
                        "Reduz a CD base de testes de recuperação sob morrendo para 9 "
                        "(ou 6 se também possuir Vitalidade, cumulativo em PV)."
                    ),
                },
            ],
            "combinacoes_cumulativas": [
                {
                    "ids_requeridos": ["vitalidade", "firmeza_da_montanha"],
                    "pv_por_nivel_total": 2,
                    "cd_recuperacao_base": 6,
                    "observacao": (
                        "Vitalidade (+1 PV/nível) e Firmeza da Montanha (+1 PV/nível) não possuem tipo de bônus "
                        "e acumulam explicitamente (+2 PV/nível e CD de recuperação 6 + morrendo)."
                    ),
                }
            ],
            "pv_temporarios": {
                "somam_ao_maximo": False,
                "acumulam_entre_si": False,
                "regra": (
                    "Pontos de Vida temporários nunca aumentam os PV máximos nem se acumulam; "
                    "se uma segunda fonte conceder PV temporários, mantém-se apenas o maior valor restante."
                ),
            },
        },
        "morrendo_e_testes_de_recuperacao": {
            "limite_morrendo_padrao": 4,
            "modificadores_limite_morrendo": [
                {
                    "id": "duro_de_matar",
                    "nome": "Duro de Matar",
                    "origem_arquivo": "talentos.json",
                    "tipo_origem": "talento_geral",
                    "nivel_minimo": 1,
                    "novo_limite_morrendo": 5,
                }
            ],
            "formula_cd_recuperacao": "cd_base + valor_atual_morrendo",
            "cd_recuperacao_base_padrao": 10,
            "tabela_resolucao_cd_recuperacao": [
                {
                    "talentos_presentes": ["vitalidade", "firmeza_da_montanha"],
                    "cd_base": 6,
                    "descricao": "Possui Vitalidade e Firmeza da Montanha.",
                },
                {
                    "talentos_presentes": ["firmeza_da_montanha"],
                    "cd_base": 9,
                    "descricao": "Possui apenas Firmeza da Montanha.",
                },
                {
                    "talentos_presentes": ["vitalidade"],
                    "cd_base": 9,
                    "descricao": "Possui apenas Vitalidade.",
                },
                {
                    "talentos_presentes": [],
                    "cd_base": 10,
                    "descricao": "Padrão (sem Vitalidade nem Firmeza da Montanha).",
                },
            ],
        },
        "regras_acumulo_bonus_e_penalidades": {
            "principio_geral": (
                "No Pathfinder 2E, bônus do mesmo tipo não acumulam (aplica-se apenas o maior); "
                "penalidades do mesmo tipo também não acumulam (aplica-se apenas a pior/mais severa)."
            ),
            "tipos_bonus": [
                {
                    "id": "proficiencia",
                    "nome": "Bônus de Proficiência",
                    "acumula_mesmo_tipo": False,
                    "regra": "Determinado pelo grau (D/T/E/M/L) e nível; cada teste usa apenas uma proficiência.",
                },
                {
                    "id": "circunstancia",
                    "nome": "Bônus de Circunstância",
                    "acumula_mesmo_tipo": False,
                    "regra": "Usa apenas o maior bônus de circunstância aplicável ao teste ou estatística.",
                },
                {
                    "id": "estado",
                    "nome": "Bônus de Estado",
                    "acumula_mesmo_tipo": False,
                    "regra": "Usa apenas o maior bônus de estado aplicável (normalmente vindo de magias ou condições).",
                },
                {
                    "id": "item",
                    "nome": "Bônus de Item",
                    "acumula_mesmo_tipo": False,
                    "regra": "Usa apenas o maior bônus de item aplicável (ex.: armaduras, runas de potência).",
                },
                {
                    "id": "sem_tipo",
                    "nome": "Bônus / Incremento Sem Tipo",
                    "acumula_mesmo_tipo": True,
                    "regra": (
                        "Aumentos diretos sem categoria tipada acumulam entre si, salvo restrição explícita "
                        "(ex.: Vitalidade + Firmeza da Montanha em PV máximos)."
                    ),
                },
            ],
            "tipos_penalidade": [
                {
                    "id": "circunstancia",
                    "nome": "Penalidade de Circunstância",
                    "acumula_mesmo_tipo": False,
                    "regra": "Aplica-se apenas a pior penalidade de circunstância.",
                },
                {
                    "id": "estado",
                    "nome": "Penalidade de Estado",
                    "acumula_mesmo_tipo": False,
                    "regra": "Aplica-se apenas a pior penalidade de estado.",
                },
                {
                    "id": "item",
                    "nome": "Penalidade de Item",
                    "acumula_mesmo_tipo": False,
                    "regra": "Aplica-se apenas a pior penalidade de item.",
                },
                {
                    "id": "sem_tipo",
                    "nome": "Penalidade Sem Tipo",
                    "acumula_mesmo_tipo": True,
                    "regra": "Penalidades sem tipo (como penalidade de ataques múltiplos) acumulam entre si e com penalidades tipadas.",
                },
            ],
            "aplicacao_no_motor": (
                "Ao expandir o motor para níveis 2–20, agrupar modificadores por tipo usando max() para bônus "
                "e min() para penalidades tipadas, somando livremente apenas modificadores 'sem_tipo'."
            ),
        },
    }


def validar_dados(dados: dict[str, Any]) -> None:
    """Valida integridade interna e referências cruzadas com os JSONs existentes em dados/."""
    with (DIR_DADOS / "ancestralidades_biografias.json").open("r", encoding="utf-8") as f:
        anc_bio = json.load(f)
    with (DIR_DADOS / "talentos.json").open("r", encoding="utf-8") as f:
        talentos_json = json.load(f)

    ids_talentos_gerais = {t["id"]: t for t in talentos_json["talentos"]}
    ids_talentos_anc: dict[str, dict[str, Any]] = {}
    for anc in anc_bio["ancestralidades"]:
        for t in anc["talentos_ancestralidade"]:
            ids_talentos_anc[t["id"]] = t

    pv = dados["pontos_de_vida"]
    assert pv["regra_ancestralidade"]["aplicar_somente_nivel_1"] is True
    assert pv["regra_ancestralidade"]["multiplica_por_nivel"] is False
    assert pv["regra_classe_e_constituicao"]["multiplica_por_nivel"] is True

    assert "pv_ancestralidade + (pv_classe + mod_constituicao) * nivel" == (
        anc_bio["regras_criacao_personagem"]["formulas_ficha"]["pontos_vida"]
    )

    mods_esc = pv["modificadores_escalonados_por_nivel"]
    ids_mods = {m["id"] for m in mods_esc}
    for m in mods_esc:
        if m["origem_arquivo"] == "talentos.json":
            assert m["id"] in ids_talentos_gerais, f"Talento ausente em talentos.json: {m['id']}"
        elif m["origem_arquivo"] == "ancestralidades_biografias.json":
            assert m["id"] in ids_talentos_anc, f"Talento ausente em ancestralidades_biografias.json: {m['id']}"
        for alvo in m["acumula_com"]:
            assert alvo in ids_mods, f"Referência de acúmulo desconhecida: {alvo}"

    for comb in pv["combinacoes_cumulativas"]:
        for tid in comb["ids_requeridos"]:
            assert tid in ids_mods, f"ID requerido não encontrado: {tid}"

    morr = dados["morrendo_e_testes_de_recuperacao"]
    for mod_m in morr["modificadores_limite_morrendo"]:
        assert mod_m["id"] in ids_talentos_gerais, f"Talento ausente em talentos.json: {mod_m['id']}"

    cds = morr["tabela_resolucao_cd_recuperacao"]
    assert cds[0]["talentos_presentes"] == ["vitalidade", "firmeza_da_montanha"]
    assert cds[0]["cd_base"] == 6
    assert cds[-1]["talentos_presentes"] == []
    assert cds[-1]["cd_base"] == morr["cd_recuperacao_base_padrao"] == 10


def main() -> None:
    dados = construir_dados()
    validar_dados(dados)
    conteudo_novo = json.dumps(dados, ensure_ascii=False, indent=2)
    if CAMINHO_SAIDA.exists():
        atual = json.loads(CAMINHO_SAIDA.read_text(encoding="utf-8"))
        validar_dados(atual)
        if atual == dados:
            print(f"Arquivo já atualizado e validado com sucesso: {CAMINHO_SAIDA}")
            return
    with CAMINHO_SAIDA.open("w", encoding="utf-8") as f:
        f.write(conteudo_novo)
    print(f"Arquivo gerado e validado com sucesso: {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()
