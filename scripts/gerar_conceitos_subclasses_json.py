"""Gera e valida o catálogo de Conceitos/Subclasses procedurais (`dados/conceitos_subclasses.json`).

Etapa 2 (v2.1) do projeto: define 72 conceitos temáticos e mecânicos (6 por classe)
cobrindo todas as 12 classes básicas do Pathfinder 2E. O jogador escolhe a Classe e o Conceito, e
o motor resolve proceduralmente a Subclasse Oficial mais adequada (exata ou
dentre `subclasses_oficiais_candidatas`), além de:
- Prioridade de atributos para distribuição ABCD;
- Biografias condizentes para geração procedural;
- Perícias e Saberes prioritários;
- Talentos recomendados (Classe N1, Classe N2+, Perícia, Gerais e traços ancestrais);
- Loadout de equipamentos compatível com 15 po iniciais;
- Diretriz de conjuração (tradição, traços/escolas e magias iniciais prioritárias).

Todas as referências são validadas 1:1 contra os JSONs reais de `dados/`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from motor.equipamentos import calcular_proficiencias_combate, grau_arma

DIR_DADOS = RAIZ_PROJETO / "dados" / "dadospf2"
CAMINHO_SAIDA = DIR_DADOS / "conceitos_subclasses.json"


def _conceito(
    id_conceito: str,
    classe_id: str,
    classe_nome: str,
    nome: str,
    subclasses_oficiais: list[tuple[str, str]],
    resumo_proposta: str,
    sinergia_mecanica: str,
    prioridade_atributos: list[str],
    biografias_recomendadas: list[str],
    pericias_prioritarias: list[str],
    saber_sugerido: str,
    talentos_classe_n1: list[str],
    talentos_classe_n2_mais: list[str],
    talentos_pericia: list[str],
    talentos_gerais: list[str],
    tracos_ancestralidade_afinidade: list[str],
    categoria_armadura_preferida: str,
    armaduras_ids: list[str],
    usa_escudo: bool,
    escudos_ids: list[str],
    armas_corpo_a_corpo_ids: list[str],
    armas_distancia_ids: list[str],
    estilo_empunhadura: str,
    conjuracao_recomendada: dict[str, Any] | None = None,
    conjuracao_por_tradicao: dict[str, dict[str, Any]] | None = None,
    fonte_divina_preferida: str | None = None,
    fontes_divinas_aceitas: list[str] | None = None,
    tendencia_preferida: str | None = None,
    tese_arcana_id: str | None = None,
    aliado_divino_sugerido: str | None = None,
) -> dict[str, Any]:
    """Constrói um objeto de conceito estruturado de forma uniforme."""
    sub_id_principal, sub_nome_principal = subclasses_oficiais[0]
    return {
        "id": id_conceito,
        "classe_id": classe_id,
        "classe_nome": classe_nome,
        "nome": nome,
        "titulo_completo": f"{classe_nome} — {nome}",
        "subclasse_oficial_id": sub_id_principal,
        "subclasse_oficial_nome": sub_nome_principal,
        "subclasses_oficiais_candidatas": [sid for sid, _ in subclasses_oficiais],
        "subclasses_oficiais_nomes": [snome for _, snome in subclasses_oficiais],
        "resumo_proposta": resumo_proposta,
        "sinergia_mecanica": sinergia_mecanica,
        "prioridade_atributos": prioridade_atributos,
        "biografias_recomendadas": biografias_recomendadas,
        "pericias_prioritarias": pericias_prioritarias,
        "saber_sugerido": saber_sugerido,
        "talentos_recomendados": {
            "classe_nivel_1": talentos_classe_n1,
            "classe_nivel_2_mais": talentos_classe_n2_mais,
            "pericia": talentos_pericia,
            "gerais": talentos_gerais,
            "tracos_ancestralidade_afinidade": tracos_ancestralidade_afinidade,
        },
        "equipamento_recomendado": {
            "categoria_armadura_preferida": categoria_armadura_preferida,
            "armaduras_ids": armaduras_ids,
            "usa_escudo": usa_escudo,
            "escudos_ids": escudos_ids,
            "armas_corpo_a_corpo_ids": armas_corpo_a_corpo_ids,
            "armas_distancia_ids": armas_distancia_ids,
            "estilo_empunhadura": estilo_empunhadura,
            "kit_classe_preferido": classe_nome,
        },
        "conjuracao_recomendada": conjuracao_recomendada,
        "conjuracao_por_tradicao": conjuracao_por_tradicao,
        "fonte_divina_preferida": fonte_divina_preferida,
        "fontes_divinas_aceitas": (
            fontes_divinas_aceitas
            if fontes_divinas_aceitas is not None
            else ([fonte_divina_preferida] if fonte_divina_preferida else None)
        ),
        "tendencia_preferida": tendencia_preferida,
        "tese_arcana_id": tese_arcana_id,
        "aliado_divino_sugerido": aliado_divino_sugerido,
    }


def _conjuracao(
    tradicao: str,
    tracos_prioritarios: list[str],
    escolas_prioritarias: list[str],
    truques_prioritarios: list[str],
    magias_nivel_1_prioritarias: list[str],
) -> dict[str, Any]:
    """Constrói a diretriz de conjuração temática de um conceito."""
    return {
        "tradicao": tradicao,
        "tracos_prioritarios": tracos_prioritarios,
        "escolas_prioritarias": escolas_prioritarias,
        "truques_prioritarios": truques_prioritarios,
        "magias_nivel_1_prioritarias": magias_nivel_1_prioritarias,
    }


def construir_conceitos() -> list[dict[str, Any]]:
    """Define os 72 conceitos (6 por classe) cobrindo todas as 12 classes básicas do Livro Básico."""
    return [
        # =====================================================================
        # 1. ALQUIMISTA (6)
        # =====================================================================
        _conceito(
            id_conceito="alquimista_artilheiro_linha_frente",
            classe_id="alquimista",
            classe_nome="Alquimista",
            nome="Artilheiro de Linha de Frente (Bombardeiro Puro)",
            subclasses_oficiais=[("bombardeiro", "Bombardeiro")],
            resumo_proposta=(
                "Artilheiro focado em bombas alquímicas infundidas de dano elemental "
                "à distância e controle de respingo sem atingir aliados."
            ),
            sinergia_mecanica=(
                "Usa Alquimia Rápida com Bombardeiro Rápido (1º) e Lançador Longínquo (1º) "
                "para sacar e arremessar bombas longe na mesma rodada; evolui com Respingo "
                "Calculado (4º), Bombas Direcionais (6º) e Respingo Expandido (10º)."
            ),
            prioridade_atributos=["int", "des", "con", "sab", "car", "for"],
            biografias_recomendadas=["funileiro", "estudioso", "artesao", "batedor"],
            pericias_prioritarias=["manufatura", "acrobatismo", "furtividade", "arcanismo", "sociedade"],
            saber_sugerido="Saber de Alquimia",
            talentos_classe_n1=["bombardeiro_rapido", "lancador_longinquo", "alquimico_sagaz"],
            talentos_classe_n2_mais=["respingo_calculado", "bombas_direcionais", "respingo_expandido"],
            talentos_pericia=["manufatura_alquimica", "especialidade_de_manufatura", "reparo_rapido"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["alquimia", "fogo", "engenho", "saber"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "clava"],
            armas_distancia_ids=["bomba_alquimica", "besta_leve", "funda"],
            estilo_empunhadura="distancia",
        ),
        _conceito(
            id_conceito="alquimista_sabotador_debilitante",
            classe_id="alquimista",
            classe_nome="Alquimista",
            nome="Sabotador Debilitante (Controle de Grupo)",
            subclasses_oficiais=[("bombardeiro", "Bombardeiro"), ("mutagenista", "Mutagenista")],
            resumo_proposta=(
                "Tático de campo que sacrifica dano bruto para cegar, enfraquecer, "
                "desacelerar e deixar chefes desprevenidos com aditivos alquímicos."
            ),
            sinergia_mecanica=(
                "Combina aditivos como Bomba de Fumaça (2º) para dar cobertura ao grupo "
                "com Bomba Debilitante (6º / 10º / 14º) e Bomba Grudenta (8º) para "
                "aplicar condições severas em inimigos prioritários."
            ),
            prioridade_atributos=["int", "des", "con", "sab", "car", "for"],
            biografias_recomendadas=["funileiro", "batedor", "criminoso", "estudioso"],
            pericias_prioritarias=["manufatura", "furtividade", "ladroagem", "acrobatismo", "sociedade"],
            saber_sugerido="Saber de Alquimia",
            talentos_classe_n1=["bombardeiro_rapido", "alquimico_sagaz", "lancador_longinquo"],
            talentos_classe_n2_mais=[
                "bomba_de_fumaca",
                "bomba_debilitante",
                "bomba_grudenta",
                "bomba_debilitante_maior",
                "bomba_debilitante_verdadeira",
            ],
            talentos_pericia=["manufatura_alquimica", "identificacao_rapida", "esgueirador_de_terreno"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["alquimia", "furtividade", "engenho"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "clava"],
            armas_distancia_ids=["bomba_alquimica", "funda", "dardo"],
            estilo_empunhadura="distancia",
        ),
        _conceito(
            id_conceito="alquimista_medico_combate",
            classe_id="alquimista",
            classe_nome="Alquimista",
            nome="Médico de Combate (Suporte e Cura)",
            subclasses_oficiais=[("cirurgiao", "Cirurgião")],
            resumo_proposta=(
                "Curandeiro científico que substitui Medicina por Manufatura e produz "
                "lotes extras de elixires restauradores para sustentar o grupo."
            ),
            sinergia_mecanica=(
                "Usa o Campo de Pesquisa Cirurgião com ferramentas de curandeiro, "
                "Alquímico Sagaz (1º) e Familiar Alquímico (1º); escala com Combinar "
                "Elixires (6º) e Elixir Misericordioso (10º) para curar e remover condições."
            ),
            prioridade_atributos=["int", "sab", "des", "con", "car", "for"],
            biografias_recomendadas=["medico_de_campo", "herbalista", "estudioso", "acolito"],
            pericias_prioritarias=["manufatura", "medicina", "natureza", "diplomacia", "sociedade"],
            saber_sugerido="Saber de Anatomia",
            talentos_classe_n1=["alquimico_sagaz", "familiar_alquimico", "bombardeiro_rapido"],
            talentos_classe_n2_mais=["combinar_elixires", "elixir_misericordioso", "resistencia_a_veneno"],
            talentos_pericia=["medicina_de_batalha", "manufatura_alquimica", "medicina_natural"],
            talentos_gerais=["vitalidade", "recuperacao_rapida", "duro_de_matar"],
            tracos_ancestralidade_afinidade=["cura", "sabedoria", "alquimia"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro", "armadura_acolchoada"],
            usa_escudo=True,
            escudos_ids=["broquel", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["maca_leve", "adaga"],
            armas_distancia_ids=["funda", "dardo"],
            estilo_empunhadura="uma_mao_e_escudo",
        ),
        _conceito(
            id_conceito="alquimista_aberracao_mutante",
            classe_id="alquimista",
            classe_nome="Alquimista",
            nome="Aberração Mutante (Combatente Corpo a Corpo)",
            subclasses_oficiais=[("mutagenista", "Mutagenista")],
            resumo_proposta=(
                "Combatente físico de linha de frente que consome mutagênicos bestiais "
                "ou irrefreáveis para ampliar força, garras e resistência a dano."
            ),
            sinergia_mecanica=(
                "Combina Força secundária e Campo Mutagenista com Mutagênico Revivificante "
                "(2º) para recuperar PV, Mutagênico Feral (8º) para ataques naturais letais "
                "e Mutagênico Invencível (12º) para resistência física."
            ),
            prioridade_atributos=["int", "for", "con", "des", "sab", "car"],
            biografias_recomendadas=["mineiro", "prisioneiro", "operario", "funileiro"],
            pericias_prioritarias=["manufatura", "atletismo", "intimidacao", "medicina", "sobrevivencia"],
            saber_sugerido="Saber de Alquimia",
            talentos_classe_n1=["familiar_alquimico", "alquimico_sagaz"],
            talentos_classe_n2_mais=["mutagenico_revivificante", "mutagenico_feral", "mutagenico_invencivel"],
            talentos_pericia=["carregador_robusto", "olhar_intimidante", "manufatura_alquimica"],
            talentos_gerais=["vitalidade", "duro_de_matar", "proficiencia_com_armas"],
            tracos_ancestralidade_afinidade=["resistencia", "forca", "garras", "mordida"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["lanca_longa", "maca", "adaga"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao",
        ),
        _conceito(
            id_conceito="alquimista_mestre_venenos",
            classe_id="alquimista",
            classe_nome="Alquimista",
            nome="Mestre dos Venenos e Infiltração",
            subclasses_oficiais=[
                ("mutagenista", "Mutagenista"),
                ("bombardeiro", "Bombardeiro"),
                ("cirurgiao", "Cirurgião"),
            ],
            resumo_proposta=(
                "Infiltrador furtivo que prepara venenos de contato e ferimento para "
                "revestir armas próprias e dos aliados antes dos combates."
            ),
            sinergia_mecanica=(
                "Prioriza Furtividade, Ladroagem e Manufatura para preparar toxinas; "
                "escala com Resistência a Veneno (2º), Alquimia Poderosa (8º) e "
                "Envenenador Potente (10º) para elevar a CD dos venenos."
            ),
            prioridade_atributos=["int", "des", "con", "sab", "car", "for"],
            biografias_recomendadas=["criminoso", "charlatao", "batedor", "herbalista"],
            pericias_prioritarias=["manufatura", "furtividade", "ladroagem", "dissimulacao", "natureza"],
            saber_sugerido="Saber de Venenos",
            talentos_classe_n1=["alquimico_sagaz", "familiar_alquimico", "bombardeiro_rapido"],
            talentos_classe_n2_mais=["resistencia_a_veneno", "alquimia_poderosa", "envenenador_potente"],
            talentos_pericia=["manufatura_alquimica", "contrabandista_experiente", "furto_subito"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "duro_de_matar"],
            tracos_ancestralidade_afinidade=["veneno", "furtividade", "alquimia"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "foice"],
            armas_distancia_ids=["zarabatana", "dardo", "besta_de_mao"],
            estilo_empunhadura="distancia",
        ),
        _conceito(
            id_conceito="alquimista_sabio_cognitivo",
            classe_id="alquimista",
            classe_nome="Alquimista",
            nome="Sábio Cognitivo e Estrategista (Elixires e Familiar)",
            subclasses_oficiais=[("cirurgiao", "Cirurgião"), ("mutagenista", "Mutagenista")],
            resumo_proposta=(
                "Pesquisador de retaguarda assistido por um familiar alquímico que "
                "potencializa perícias mentais e distribui elixires utilitários ao grupo."
            ),
            sinergia_mecanica=(
                "Prioriza Familiar Alquímico (1º) com assistente de laboratório e "
                "reagentes extras junto a Alquímico Sagaz (1º); escala com Alquimia "
                "Duradoura (4º), Alquimia Eficiente (4º) e Combinar Elixires (6º)."
            ),
            prioridade_atributos=["int", "des", "sab", "con", "car", "for"],
            biografias_recomendadas=["estudioso", "detetive", "eremita", "herbalista"],
            pericias_prioritarias=["manufatura", "arcanismo", "ocultismo", "natureza", "sociedade"],
            saber_sugerido="Saber Acadêmico",
            talentos_classe_n1=["familiar_alquimico", "alquimico_sagaz", "lancador_longinquo"],
            talentos_classe_n2_mais=["alquimia_duradoura", "alquimia_eficiente", "combinar_elixires"],
            talentos_pericia=["manufatura_alquimica", "identificacao_rapida", "conhecimento_duvidoso"],
            talentos_gerais=["perspicacia_astuta", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["inteligencia", "saber", "alquimia", "engenho"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "cajado"],
            armas_distancia_ids=["besta_leve", "bomba_alquimica"],
            estilo_empunhadura="distancia",
        ),

        # =====================================================================
        # 2. BÁRBARO (6)
        # =====================================================================
        _conceito(
            id_conceito="barbaro_fera_selvagem",
            classe_id="barbaro",
            classe_nome="Bárbaro",
            nome="Fera Selvagem (Combatente Desarmado)",
            subclasses_oficiais=[("instinto_animal", "Instinto Animal")],
            resumo_proposta=(
                "Lutador primal que entra em Fúria manifestando garras e mandíbulas "
                "animais que escalam de dano no combate corpo a corpo."
            ),
            sinergia_mecanica=(
                "Instinto Animal fornece ataques naturais ferozes; combina Visão "
                "Aguçada (1º) com Pele de Animal (6º) para compensar a perda de CA da "
                "Fúria e Atracar Furioso (12º) para imobilizar presas."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "car", "int"],
            biografias_recomendadas=["cacador", "eremita", "encantador_de_animais", "nomade"],
            pericias_prioritarias=["atletismo", "natureza", "sobrevivencia", "intimidacao", "acrobatismo"],
            saber_sugerido="Saber de Feras",
            talentos_classe_n1=["visao_agucada", "investida_subita"],
            talentos_classe_n2_mais=["pele_de_animal", "furia_animal", "atracar_furioso", "faro_agucado"],
            talentos_pericia=["lutador_titanico", "escalador_de_combate", "forrageador"],
            talentos_gerais=["duro_de_matar", "vitalidade", "veloz"],
            tracos_ancestralidade_afinidade=["garras", "mordida", "sentidos", "selvagem"],
            categoria_armadura_preferida="media",
            armaduras_ids=["gibao_de_peles", "couro_batido"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["manopla_com_cravos", "machado_de_batalha"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="desarmado",
        ),
        _conceito(
            id_conceito="barbaro_colosso_titanico",
            classe_id="barbaro",
            classe_nome="Bárbaro",
            nome="Colosso Titânico (Destruidor de Área)",
            subclasses_oficiais=[("instinto_de_gigante", "Instinto de Gigante")],
            resumo_proposta=(
                "Brutamontes colossal que empunha armas forjadas para criaturas Grandes "
                "para esmagar múltiplos inimigos com alcance ampliado."
            ),
            sinergia_mecanica=(
                "Empunhadura Titânica soma bônus massivo de Fúria com montantes ou "
                "machados grandes; escala com Investida Súbita (1º), Trespassar (6º), "
                "Estatura de Gigante (6º) e Estatura de Titã (12º)."
            ),
            prioridade_atributos=["for", "con", "sab", "des", "car", "int"],
            biografias_recomendadas=["operario", "gladiador", "prisioneiro", "guarda"],
            pericias_prioritarias=["atletismo", "intimidacao", "sobrevivencia", "medicina"],
            saber_sugerido="Saber de Guerra",
            talentos_classe_n1=["investida_subita", "intimidacao_enfurecida"],
            talentos_classe_n2_mais=["trespassar", "estatura_de_gigante", "estatura_de_tita", "finalizacao_furiosa"],
            talentos_pericia=["carregador_robusto", "lutador_titanico", "coagir_grupo"],
            talentos_gerais=["vitalidade", "duro_de_matar", "recuperacao_rapida"],
            tracos_ancestralidade_afinidade=["forca", "resistencia", "tamanho"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_escamas", "gibao_de_peles"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["montante", "machado_longo", "malho"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="duas_maos",
        ),
        _conceito(
            id_conceito="barbaro_guerreiro_draconico",
            classe_id="barbaro",
            classe_nome="Bárbaro",
            nome="Guerreiro Dracônico (Elemental e Intimidador)",
            subclasses_oficiais=[("instinto_de_dragao", "Instinto de Dragão")],
            resumo_proposta=(
                "Guerreiro feroz que canaliza o poder de um dragão para converter "
                "o dano adicional da Fúria em dano elemental e intimidar o campo."
            ),
            sinergia_mecanica=(
                "Une Intimidação Enfurecida (1º) para Desmoralizar em plena Fúria "
                "com Sopro de Fúria do Dragão (6º), Brado Aterrorizante (10º) e "
                "Asas da Fúria do Dragão (12º) para mobilidade aérea e área elemental."
            ),
            prioridade_atributos=["for", "con", "des", "car", "sab", "int"],
            biografias_recomendadas=["soldado", "gladiador", "nomade", "mineiro"],
            pericias_prioritarias=["atletismo", "intimidacao", "sobrevivencia", "acrobatismo", "natureza"],
            saber_sugerido="Saber de Dragões",
            talentos_classe_n1=["intimidacao_enfurecida", "investida_subita"],
            talentos_classe_n2_mais=[
                "sopro_de_furia_do_dragao",
                "asas_da_furia_do_dragao",
                "brado_aterrorizante",
                "finalizacao_furiosa",
            ],
            talentos_pericia=["olhar_intimidante", "lutador_titanico", "salto_rapido"],
            talentos_gerais=["vitalidade", "iniciativa_incrivel", "veloz"],
            tracos_ancestralidade_afinidade=["fogo", "dragao", "forca", "intimidacao"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_escamas", "gibao_de_peles"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["machado_longo", "montante", "espada_bastarda"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="duas_maos",
        ),
        _conceito(
            id_conceito="barbaro_cacador_assombracoes",
            classe_id="barbaro",
            classe_nome="Bárbaro",
            nome="Caçador de Assombrações (Guerreiro Ancestral)",
            subclasses_oficiais=[("instinto_espiritual", "Instinto Espiritual")],
            resumo_proposta=(
                "Combatente espiritual que canaliza ancestrais para causar dano "
                "positivo ou negativo e ferir criaturas incorpóreas sem penalidade."
            ),
            sinergia_mecanica=(
                "O Instinto Espiritual concede efeito automático de toque fantasma em "
                "Fúria; combina Visão Aguçada (1º) e Momento de Clareza (1º) com "
                "Interferência dos Espíritos (6º) e Ira do Espírito (12º)."
            ),
            prioridade_atributos=["for", "con", "sab", "des", "car", "int"],
            biografias_recomendadas=["eremita", "acolito", "vidente", "nomade"],
            pericias_prioritarias=["atletismo", "religiao", "ocultismo", "sobrevivencia", "intimidacao"],
            saber_sugerido="Saber de Espíritos",
            talentos_classe_n1=["visao_agucada", "investida_subita", "momento_de_clareza"],
            talentos_classe_n2_mais=["interferencia_dos_espiritos", "ira_do_espirito", "sem_escapatoria"],
            talentos_pericia=["estudante_do_canone", "identificar_estranhezas", "olhar_intimidante"],
            talentos_gerais=["duro_de_matar", "vitalidade", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["espirito", "visao", "religiao", "resistencia"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_escamas", "gibao_de_peles"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["machado_de_batalha", "espada_longa", "lanca_longa"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao",
        ),
        _conceito(
            id_conceito="barbaro_incursor_vanguarda",
            classe_id="barbaro",
            classe_nome="Bárbaro",
            nome="Incursor de Vanguarda (Mobilidade e Arremesso)",
            subclasses_oficiais=[("instinto_do_furor", "Instinto do Furor")],
            resumo_proposta=(
                "Escaramuçador agressivo sem anátema que ganha talento extra no 1º "
                "nível para combinar arremesso enfurecido e avanço imediato."
            ),
            sinergia_mecanica=(
                "O Instinto do Furor libera dois talentos no 1º nível (Investida Súbita "
                "+ Arremessador Enfurecido), abrindo combate com machadinhas/azagaias "
                "em Fúria antes de fechar distância com Movimento Veloz (4º)."
            ),
            prioridade_atributos=["for", "des", "con", "sab", "car", "int"],
            biografias_recomendadas=["batedor", "soldado", "cacador", "marinheiro"],
            pericias_prioritarias=["atletismo", "acrobatismo", "sobrevivencia", "intimidacao", "natureza"],
            saber_sugerido="Saber de Terreno",
            talentos_classe_n1=["investida_subita", "arremessador_enfurecido"],
            talentos_classe_n2_mais=["movimento_veloz", "sem_escapatoria", "salto_subito"],
            talentos_pericia=["salto_rapido", "escalador_de_combate", "olhar_intimidante"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["velocidade", "forca", "arremesso"],
            categoria_armadura_preferida="media",
            armaduras_ids=["gibao_de_peles", "couro_batido", "cota_de_escamas"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["machado_de_batalha", "machadinha"],
            armas_distancia_ids=["azagaia", "dardo"],
            estilo_empunhadura="uma_mao",
        ),
        _conceito(
            id_conceito="barbaro_quebra_feiticos",
            classe_id="barbaro",
            classe_nome="Bárbaro",
            nome="Quebra-Feitiços Implacável (Bastião de Escudo)",
            subclasses_oficiais=[
                ("instinto_do_furor", "Instinto do Furor"),
                ("instinto_espiritual", "Instinto Espiritual"),
            ],
            resumo_proposta=(
                "Bárbaro disciplinado de arma e escudo capaz de manter o controle "
                "mental em plena Fúria e pressionar conjuradores na linha de frente."
            ),
            sinergia_mecanica=(
                "Combina escudo erguido para mitigar a penalidade de CA da Fúria com "
                "Momento de Clareza (1º) e Intimidação Enfurecida (1º); evolui com "
                "Retomar o Fôlego (2º), Fúria Ferida (4º) e Ataque de Oportunidade (6º)."
            ),
            prioridade_atributos=["for", "con", "sab", "des", "car", "int"],
            biografias_recomendadas=["guarda", "soldado", "prisioneiro", "cacador_de_recompensas"],
            pericias_prioritarias=["atletismo", "intimidacao", "sobrevivencia", "acrobatismo", "religiao"],
            saber_sugerido="Saber de Guerra",
            talentos_classe_n1=["momento_de_clareza", "intimidacao_enfurecida", "investida_subita"],
            talentos_classe_n2_mais=["retomar_o_folego", "furia_ferida", "ataque_de_oportunidade"],
            talentos_pericia=["carregador_robusto", "olhar_intimidante", "lutador_titanico"],
            talentos_gerais=["duro_de_matar", "vitalidade", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["escudo", "resistencia", "forca", "coragem"],
            categoria_armadura_preferida="media",
            armaduras_ids=["placa_peitoral", "cota_de_escamas", "gibao_de_peles"],
            usa_escudo=True,
            escudos_ids=["escudo_de_aco", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["martelo_de_guerra", "machado_de_batalha", "espada_longa"],
            armas_distancia_ids=["azagaia", "machadinha"],
            estilo_empunhadura="uma_mao_e_escudo",
        ),

        # =====================================================================
        # 3. BARDO (6)
        # =====================================================================
        _conceito(
            id_conceito="bardo_comandante_inspirador",
            classe_id="bardo",
            classe_nome="Bardo",
            nome="Comandante Inspirador (Suporte de Grupo)",
            subclasses_oficiais=[("maestro", "Maestro")],
            resumo_proposta=(
                "Líder inspirador de suporte que mantém bônus de ataque e defesa "
                "ativos para todo o grupo durante praticamente todo o combate."
            ),
            sinergia_mecanica=(
                "A Musa Maestro concede Composição Prolongada (1º) para estender "
                "Inspirar Coragem ou Inspirar Defesa sem gastar ações toda rodada, "
                "culminando em Inspirar Heroísmo (8º) para picos de poder."
            ),
            prioridade_atributos=["car", "des", "con", "sab", "int", "for"],
            biografias_recomendadas=["animador", "artista", "emissario", "nobre"],
            pericias_prioritarias=["performance", "ocultismo", "diplomacia", "intimidacao", "sociedade"],
            saber_sugerido="Saber de Batalha",
            talentos_classe_n1=["composicao_prolongada", "magia_de_alcance"],
            talentos_classe_n2_mais=["inspirar_defesa", "inspirar_heroismo", "tempo_triplo"],
            talentos_pericia=["performance_impressionante", "impressionar_grupo", "artista_virtuoso"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["carisma", "som", "inspiracao", "diplomacia"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["rapieira", "espada_curta", "adaga"],
            armas_distancia_ids=["arco_curto", "funda"],
            estilo_empunhadura="uma_mao",
            conjuracao_recomendada=_conjuracao(
                tradicao="ocultista",
                tracos_prioritarios=["emocao", "mental", "sonico", "encantamento"],
                escolas_prioritarias=["encantamento", "ilusao", "abjuracao"],
                truques_prioritarios=["orientacao", "escudo_mistico", "pasmar", "detectar_magia", "mensagem"],
                magias_nivel_1_prioritarias=["bencao", "protecao", "abrandar", "medo"],
            ),
        ),
        _conceito(
            id_conceito="bardo_erudito_ocultista",
            classe_id="bardo",
            classe_nome="Bardo",
            nome="Erudito Ocultista (Enciclopédia Viva)",
            subclasses_oficiais=[("enigma", "Enigma")],
            resumo_proposta=(
                "Estudioso de mistérios capaz de identificar qualquer monstro, "
                "maldição ou enigma histórico com uma única perícia universal."
            ),
            sinergia_mecanica=(
                "A Musa Enigma garante Saber Bárdico (1º) como conhecimento "
                "universal, escalando com Étude do Mestre do Saber (2º), Sabe-Tudo (8º) "
                "e Hipercognição Verdadeira (14º) para dominar Recordar Conhecimento."
            ),
            prioridade_atributos=["car", "int", "des", "con", "sab", "for"],
            biografias_recomendadas=["estudioso", "detetive", "advogado", "acolito"],
            pericias_prioritarias=["ocultismo", "performance", "arcanismo", "sociedade", "religiao"],
            saber_sugerido="Saber Oculto",
            talentos_classe_n1=["saber_bardico", "magia_de_alcance"],
            talentos_classe_n2_mais=["etude_do_mestre_do_saber", "sabe_tudo", "hipercognicao_verdadeira"],
            talentos_pericia=["conhecimento_duvidoso", "identificar_estranhezas", "poliglota"],
            talentos_gerais=["perspicacia_astuta", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["saber", "adivinhacao", "ocultismo", "inteligencia"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro", "armadura_acolchoada"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "porrete"],
            armas_distancia_ids=["besta_leve", "funda"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="ocultista",
                tracos_prioritarios=["adivinhacao", "mental", "deteccao"],
                escolas_prioritarias=["adivinhacao", "encantamento", "abjuracao"],
                truques_prioritarios=["detectar_magia", "ler_aura", "orientacao", "mensagem", "escudo_mistico"],
                magias_nivel_1_prioritarias=["cativar", "bencao", "protecao", "misseis_magicos"],
            ),
        ),
        _conceito(
            id_conceito="bardo_duelista_gracioso",
            classe_id="bardo",
            classe_nome="Bardo",
            nome="Duelista Gracioso (Esgrimista Arcano)",
            subclasses_oficiais=[("polimata", "Polímata")],
            resumo_proposta=(
                "Esgrimista carismático que usa Performance no lugar das perícias "
                "sociais e combina esgrima ágil com ilusões e encantamentos."
            ),
            sinergia_mecanica=(
                "A Musa Polímata concede Performance Versátil (1º) para Fintar, "
                "Desmoralizar e Impressionar usando Performance, apoiado por Destreza "
                "alta, Polímata Esotérico (2º) e Inspirar Defesa (4º) em combate próximo."
            ),
            prioridade_atributos=["car", "des", "con", "sab", "int", "for"],
            biografias_recomendadas=["animador", "nobre", "charlatao", "gladiador"],
            pericias_prioritarias=["performance", "ocultismo", "acrobatismo", "diplomacia", "dissimulacao"],
            saber_sugerido="Saber de Teatro",
            talentos_classe_n1=["performance_versatil", "magia_de_alcance"],
            talentos_classe_n2_mais=["polimata_esoterico", "inspirar_defesa", "versatilidade_emblematica"],
            talentos_pericia=["performance_fascinante", "artista_virtuoso", "gracejos_da_corte"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["agilidade", "carisma", "ilusao", "arma"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["rapieira", "espada_curta", "chicote"],
            armas_distancia_ids=["adaga", "arco_curto"],
            estilo_empunhadura="uma_mao",
            conjuracao_recomendada=_conjuracao(
                tradicao="ocultista",
                tracos_prioritarios=["ilusao", "encantamento", "mental"],
                escolas_prioritarias=["ilusao", "encantamento", "abjuracao"],
                truques_prioritarios=["escudo_mistico", "projetil_telecinetico", "som_fantasma", "prestidigitacao", "orientacao"],
                magias_nivel_1_prioritarias=["disfarce_ilusorio", "cativar", "golpe_certo", "medo"],
            ),
        ),
        _conceito(
            id_conceito="bardo_controlador_mental",
            classe_id="bardo",
            classe_nome="Bardo",
            nome="Controlador Mental e Disruptor",
            subclasses_oficiais=[("maestro", "Maestro"), ("enigma", "Enigma")],
            resumo_proposta=(
                "Manipulador ocultista especializado em anular efeitos sonoros/visuais "
                "inimigos e impor condições de medo e controle mental."
            ),
            sinergia_mecanica=(
                "Usa Contraperformance como reação defensiva e alterna entre truques "
                "mentais/sônicos, Lamento da Condenação (6º), Harmonizar (6º) e "
                "Conjuração Consistente (6º) com magias ocultistas de controle."
            ),
            prioridade_atributos=["car", "des", "con", "sab", "int", "for"],
            biografias_recomendadas=["charlatao", "vidente", "artista", "emissario"],
            pericias_prioritarias=["ocultismo", "performance", "intimidacao", "dissimulacao", "diplomacia"],
            saber_sugerido="Saber Oculto",
            talentos_classe_n1=["composicao_prolongada", "saber_bardico", "magia_de_alcance"],
            talentos_classe_n2_mais=["lamento_da_condenacao", "harmonizar", "conjuracao_consistente"],
            talentos_pericia=["olhar_intimidante", "distracao_prolongada", "mente_na_minha_cara"],
            talentos_gerais=["iniciativa_incrivel", "perspicacia_astuta", "vitalidade"],
            tracos_ancestralidade_afinidade=["mental", "ilusao", "sonico", "carisma"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "chicote", "porrete"],
            armas_distancia_ids=["funda", "besta_leve"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="ocultista",
                tracos_prioritarios=["mental", "medo", "emocao", "ilusao"],
                escolas_prioritarias=["encantamento", "ilusao", "necromancia"],
                truques_prioritarios=["pasmar", "som_fantasma", "projetil_telecinetico", "escudo_mistico", "detectar_magia"],
                magias_nivel_1_prioritarias=["medo", "comando", "sono", "dor_fantasma"],
            ),
        ),
        _conceito(
            id_conceito="bardo_trovador_arqueiro",
            classe_id="bardo",
            classe_nome="Bardo",
            nome="Trovador de Vanguarda (Arqueiro Inspirador)",
            subclasses_oficiais=[("maestro", "Maestro"), ("polimata", "Polímata")],
            resumo_proposta=(
                "Arqueiro móvel que entoa composições de batalha enquanto dispara "
                "flechas guiadas por magias de precisão e encantamento."
            ),
            sinergia_mecanica=(
                "Aproveita a proficiência marcial em arco curto com Inspirar Coragem, "
                "Golpe Certo e Arma Mágica; escala com Composição Prolongada (1º), "
                "Inspirar Competência (2º) e Tempo Triplo (4º) para mobilidade do grupo."
            ),
            prioridade_atributos=["car", "des", "con", "sab", "int", "for"],
            biografias_recomendadas=["batedor", "nomade", "animador", "marinheiro"],
            pericias_prioritarias=["performance", "acrobatismo", "furtividade", "ocultismo", "diplomacia"],
            saber_sugerido="Saber de Guerra",
            talentos_classe_n1=["composicao_prolongada", "performance_versatil", "magia_de_alcance"],
            talentos_classe_n2_mais=["inspirar_competencia", "tempo_triplo", "inspirar_defesa"],
            talentos_pericia=["performance_impressionante", "esgueirador_de_terreno", "queda_do_gato"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["arco", "agilidade", "velocidade", "carisma"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "rapieira", "adaga"],
            armas_distancia_ids=["arco_curto", "funda"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="ocultista",
                tracos_prioritarios=["adivinhacao", "transmutacao", "emocao"],
                escolas_prioritarias=["adivinhacao", "transmutacao", "encantamento"],
                truques_prioritarios=["orientacao", "escudo_mistico", "projetil_telecinetico", "luz", "intuir_direcao"],
                magias_nivel_1_prioritarias=["golpe_certo", "arma_magica", "bencao", "abrandar"],
            ),
        ),
        _conceito(
            id_conceito="bardo_dramaturgo_sombras",
            classe_id="bardo",
            classe_nome="Bardo",
            nome="Dramaturgo das Sombras (Infiltrador e Ilusionista)",
            subclasses_oficiais=[("polimata", "Polímata"), ("enigma", "Enigma")],
            resumo_proposta=(
                "Artista furtivo de intriga e espionagem que oculta conjurações em "
                "atuações, manipula sombras e desorienta guardas e sentinelas."
            ),
            sinergia_mecanica=(
                "Combina Magia de Alcance (1º) e Performance Versátil (1º) com "
                "Magia Melodiosa (4º) para conjurar sem ser notado, apoiado por "
                "broquel, Furtividade e magias de ilusão e sombra."
            ),
            prioridade_atributos=["car", "des", "int", "con", "sab", "for"],
            biografias_recomendadas=["charlatao", "artista", "criminoso", "crianca_de_rua"],
            pericias_prioritarias=["performance", "furtividade", "dissimulacao", "ocultismo", "ladroagem"],
            saber_sugerido="Saber do Submundo",
            talentos_classe_n1=["magia_de_alcance", "performance_versatil", "saber_bardico"],
            talentos_classe_n2_mais=["magia_melodiosa", "expansao_de_truque_magico", "musa_multifacetada"],
            talentos_pericia=["distracao_prolongada", "mentiroso_charmoso", "furto_subito"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "perspicacia_astuta"],
            tracos_ancestralidade_afinidade=["sombra", "furtividade", "ilusao", "carisma"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=True,
            escudos_ids=["broquel"],
            armas_corpo_a_corpo_ids=["espada_curta", "adaga", "chicote"],
            armas_distancia_ids=["besta_de_mao", "dardo"],
            estilo_empunhadura="uma_mao_e_escudo",
            conjuracao_recomendada=_conjuracao(
                tradicao="ocultista",
                tracos_prioritarios=["ilusao", "sombra", "negativo", "mental"],
                escolas_prioritarias=["ilusao", "necromancia", "encantamento"],
                truques_prioritarios=["som_fantasma", "toque_gelido", "mao_mistica", "mensagem", "prestidigitacao"],
                magias_nivel_1_prioritarias=["gavinhas_sombrias", "disfarce_ilusorio", "servo_invisivel", "objeto_ilusorio"],
            ),
        ),

        # =====================================================================
        # 4. CAMPEÃO (6)
        # =====================================================================
        _conceito(
            id_conceito="campeao_bastiao_impenetravel",
            classe_id="campeao",
            classe_nome="Campeão",
            nome="Bastião Impenetrável (Tanque de Escudo)",
            subclasses_oficiais=[("redentor", "Redentor")],
            resumo_proposta=(
                "Guardião blindado que enfraquece atacantes inimigos e usa o escudo "
                "para absorver diretamente o dano direcionado aos aliados."
            ),
            sinergia_mecanica=(
                "Causa Redentor (Vislumbre de Redenção) somada a Bloqueio com Escudo, "
                "Peso da Culpa (1º), Guardião de Escudo (6º), Bloqueio Rápido (8º) e "
                "Escudo da Retribuição (10º) com futuro Aliado de Escudo (3º)."
            ),
            prioridade_atributos=["for", "con", "car", "sab", "des", "int"],
            biografias_recomendadas=["guarda", "acolito", "soldado", "medico_de_campo"],
            pericias_prioritarias=["religiao", "atletismo", "diplomacia", "medicina", "intimidacao"],
            saber_sugerido="Saber de Heráldica",
            talentos_classe_n1=["peso_da_culpa", "dominio_de_divindade"],
            talentos_classe_n2_mais=["guardiao_de_escudo", "bloqueio_rapido", "escudo_da_retribuicao"],
            talentos_pericia=["carregador_robusto", "medicina_de_batalha", "estudante_do_canone"],
            talentos_gerais=["vitalidade", "duro_de_matar", "recuperacao_rapida"],
            tracos_ancestralidade_afinidade=["resistencia", "escudo", "cura", "forca"],
            categoria_armadura_preferida="pesada",
            armaduras_ids=["placa_peitoral", "cota_de_malha", "cota_de_escamas"],
            usa_escudo=True,
            escudos_ids=["escudo_de_aco", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["espada_longa", "martelo_de_guerra", "maca"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao_e_escudo",
            aliado_divino_sugerido="escudo",
        ),
        _conceito(
            id_conceito="campeao_cruzado_vingador",
            classe_id="campeao",
            classe_nome="Campeão",
            nome="Cruzado Vingador (Linha de Frente Ofensiva)",
            subclasses_oficiais=[("paladino", "Paladino")],
            resumo_proposta=(
                "Guerreiro sagrado de linha de frente que pune qualquer adversário "
                "ousado o bastante para ferir seus companheiros próximos."
            ),
            sinergia_mecanica=(
                "Causa Paladino (Golpe Retributivo) combinada com Represália à "
                "Distância (1º), Punir o Mal (6º), Ataque de Oportunidade (6º) e "
                "Espírito da Lâmina Radiante (10º) com futuro Aliado de Lâmina (3º)."
            ),
            prioridade_atributos=["for", "car", "con", "sab", "des", "int"],
            biografias_recomendadas=["soldado", "acolito", "guarda", "nobre"],
            pericias_prioritarias=["religiao", "atletismo", "intimidacao", "diplomacia", "sociedade"],
            saber_sugerido="Saber de Guerra",
            talentos_classe_n1=["represalia_a_distancia", "dominio_de_divindade"],
            talentos_classe_n2_mais=["punir_o_mal", "ataque_de_oportunidade", "espirito_da_lamina_radiante"],
            talentos_pericia=["olhar_intimidante", "lutador_titanico", "estudante_do_canone"],
            talentos_gerais=["vitalidade", "iniciativa_incrivel", "veloz"],
            tracos_ancestralidade_afinidade=["arma", "forca", "sagrado", "coragem"],
            categoria_armadura_preferida="pesada",
            armaduras_ids=["placa_peitoral", "cota_de_malha", "cota_de_escamas"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["montante", "espada_bastarda", "machado_longo"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="duas_maos",
            aliado_divino_sugerido="lamina",
        ),
        _conceito(
            id_conceito="campeao_cavaleiro_montado",
            classe_id="campeao",
            classe_nome="Campeão",
            nome="Cavaleiro Montado (Mobilidade e Investida)",
            subclasses_oficiais=[
                ("paladino", "Paladino"),
                ("redentor", "Redentor"),
                ("libertador", "Libertador"),
            ],
            resumo_proposta=(
                "Cavaleiro blindado de alta mobilidade projetado para investir em "
                "campo aberto e comandar uma montaria fiel em combate."
            ),
            sinergia_mecanica=(
                "Prepara o personagem para Aliado Montaria (3º), Cavalo de Guerra "
                "Leal (6º), Curar Montaria (8º) e Corcel Imponente (10º), apoiado por "
                "Cavalgar, lança de cavalaria e Natureza/Atletismo elevados."
            ),
            prioridade_atributos=["for", "con", "car", "sab", "des", "int"],
            biografias_recomendadas=["nobre", "soldado", "encantador_de_animais", "guarda"],
            pericias_prioritarias=["religiao", "atletismo", "natureza", "diplomacia", "intimidacao"],
            saber_sugerido="Saber de Cavalaria",
            talentos_classe_n1=[
                "represalia_a_distancia",
                "peso_da_culpa",
                "passo_desimpedido",
                "dominio_de_divindade",
            ],
            talentos_classe_n2_mais=["cavalo_de_guerra_leal", "curar_montaria", "corcel_imponente"],
            talentos_pericia=["treinar_animal", "carregador_robusto", "estudante_do_canone"],
            talentos_gerais=["cavalgar", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["velocidade", "forca", "coragem"],
            categoria_armadura_preferida="pesada",
            armaduras_ids=["placa_peitoral", "cota_de_malha", "cota_de_escamas"],
            usa_escudo=True,
            escudos_ids=["escudo_de_aco", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["espada_longa", "martelo_de_guerra", "lanca"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao_e_escudo",
            aliado_divino_sugerido="montaria",
        ),
        _conceito(
            id_conceito="campeao_quebrador_correntes",
            classe_id="campeao",
            classe_nome="Campeão",
            nome="Quebrador de Correntes (Anticontrole e Mobilidade)",
            subclasses_oficiais=[("libertador", "Libertador")],
            resumo_proposta=(
                "Campeão ágil e incansável que liberta aliados de agarrões, paralisia "
                "e controle enquanto os reposiciona fora do perigo."
            ),
            sinergia_mecanica=(
                "Causa Libertador (Passo Libertador) unida a Passo Desimpedido (1º), "
                "Aura de Coragem (4º) e Andar Liberador (12º) para manter o grupo "
                "livre de restrições e medo."
            ),
            prioridade_atributos=["for", "des", "con", "car", "sab", "int"],
            biografias_recomendadas=["prisioneiro", "marinheiro", "nomade", "gladiador"],
            pericias_prioritarias=["religiao", "atletismo", "acrobatismo", "diplomacia", "sobrevivencia"],
            saber_sugerido="Saber de Navegação",
            talentos_classe_n1=["passo_desimpedido", "dominio_de_divindade"],
            talentos_classe_n2_mais=["aura_de_coragem", "guardiao_de_escudo", "andar_liberador"],
            talentos_pericia=["salto_rapido", "queda_do_gato", "escalador_de_combate"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["liberdade", "velocidade", "forca"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_malha", "cota_de_escamas", "gibao_de_peles"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_bastarda", "machado_longo", "espada_longa"],
            armas_distancia_ids=["azagaia", "machadinha"],
            estilo_empunhadura="duas_maos",
            aliado_divino_sugerido="lamina",
        ),
        _conceito(
            id_conceito="campeao_inquisidor_litanias",
            classe_id="campeao",
            classe_nome="Campeão",
            nome="Inquisidor de Litanias (Caçador de Ímpios)",
            subclasses_oficiais=[
                ("paladino", "Paladino"),
                ("redentor", "Redentor"),
                ("libertador", "Libertador"),
            ],
            resumo_proposta=(
                "Caçador devoto com Carisma e Religião elevados que utiliza magias de "
                "devoção, litanias e auras sagradas contra mortos-vivos e ímpios."
            ),
            sinergia_mecanica=(
                "Maximiza Imposição de Mãos ofensiva/curativa e CD divina via Carisma "
                "alto; escala com Domínio de Divindade (1º), Aura de Coragem (4º) e "
                "Litania Contra Ira (6º)."
            ),
            prioridade_atributos=["for", "car", "con", "sab", "des", "int"],
            biografias_recomendadas=["acolito", "detetive", "advogado", "guarda"],
            pericias_prioritarias=["religiao", "intimidacao", "diplomacia", "atletismo", "sociedade"],
            saber_sugerido="Saber de Teologia",
            talentos_classe_n1=[
                "dominio_de_divindade",
                "represalia_a_distancia",
                "peso_da_culpa",
                "passo_desimpedido",
            ],
            talentos_classe_n2_mais=["aura_de_coragem", "litania_contra_ira", "juramento_reluzente"],
            talentos_pericia=["estudante_do_canone", "olhar_intimidante", "identificacao_rapida"],
            talentos_gerais=["vitalidade", "duro_de_matar", "perspicacia_astuta"],
            tracos_ancestralidade_afinidade=["religiao", "luz", "carisma", "coragem"],
            categoria_armadura_preferida="pesada",
            armaduras_ids=["placa_peitoral", "cota_de_malha", "cota_de_escamas"],
            usa_escudo=True,
            escudos_ids=["escudo_de_aco", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["martelo_de_guerra", "espada_longa", "maca_estrela"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao_e_escudo",
            aliado_divino_sugerido="lamina",
        ),
        _conceito(
            id_conceito="campeao_sentinela_arqueiro",
            classe_id="campeao",
            classe_nome="Campeão",
            nome="Sentinela Celeste (Vigilante à Distância e Acuidade)",
            subclasses_oficiais=[
                ("paladino", "Paladino"),
                ("libertador", "Libertador"),
                ("redentor", "Redentor"),
            ],
            resumo_proposta=(
                "Campeão ágil focado em Destreza que vigia o campo com arco longo e "
                "lâminas leves, punindo inimigos à distância quando ferem aliados."
            ),
            sinergia_mecanica=(
                "Escolhe Destreza como atributo-chave e combina Represália à Distância "
                "(1º) para desferir Golpe Retributivo com arco; evolui com Graça "
                "Divina (2º), Aura de Coragem (4º) e futuro Aliado de Lâmina (3º)."
            ),
            prioridade_atributos=["des", "car", "con", "for", "sab", "int"],
            biografias_recomendadas=["cacador", "batedor", "acolito", "guarda"],
            pericias_prioritarias=["religiao", "acrobatismo", "furtividade", "diplomacia", "sobrevivencia"],
            saber_sugerido="Saber de Patrulha",
            talentos_classe_n1=["represalia_a_distancia", "passo_desimpedido", "dominio_de_divindade"],
            talentos_classe_n2_mais=["graca_divina", "aura_de_coragem", "ataque_de_oportunidade"],
            talentos_pericia=["esgueirador_de_terreno", "queda_do_gato", "estudante_do_canone"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["arco", "agilidade", "sagrado", "elfo"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "cota_de_escamas", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["rapieira", "espada_curta", "adaga"],
            armas_distancia_ids=["arco_longo", "arco_curto"],
            estilo_empunhadura="distancia",
            aliado_divino_sugerido="lamina",
        ),

        # =====================================================================
        # 5. CLÉRIGO (6)
        # =====================================================================
        _conceito(
            id_conceito="clerigo_hospitalario_sagrado",
            classe_id="clerigo",
            classe_nome="Clérigo",
            nome="Hospitalário Sagrado (Curandeiro Supremo)",
            subclasses_oficiais=[("sacerdote_enclausurado", "Sacerdote Enclausurado")],
            resumo_proposta=(
                "Sacerdote devotado à restauração que amplifica ao máximo sua Fonte "
                "de Cura com espaços extras de círculo máximo para salvar o grupo."
            ),
            sinergia_mecanica=(
                "Clérigo Claustro com Carisma alto para mais usos da Fonte de Cura, "
                "Mãos Curandeiras (1º) para dados d10 de cura, Cura Comunal (2º) e "
                "Socorro Canalizado (8º)."
            ),
            prioridade_atributos=["sab", "car", "con", "des", "int", "for"],
            biografias_recomendadas=["acolito", "medico_de_campo", "herbalista", "emissario"],
            pericias_prioritarias=["religiao", "medicina", "diplomacia", "natureza", "sociedade"],
            saber_sugerido="Saber de Teologia",
            talentos_classe_n1=["maos_curandeiras", "iniciado_no_dominio", "magia_de_alcance"],
            talentos_classe_n2_mais=["cura_comunal", "cura_comunal_aprimorada", "socorro_canalizado"],
            talentos_pericia=["medicina_de_batalha", "estudante_do_canone", "medicina_natural"],
            talentos_gerais=["vitalidade", "recuperacao_rapida", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["cura", "divino", "sabedoria", "vida"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["clava", "adaga"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="uma_mao",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["cura", "positivo", "luz", "abjuracao"],
                escolas_prioritarias=["necromancia", "abjuracao", "encantamento"],
                truques_prioritarios=["estabilizar", "orientacao", "luz", "escudo_mistico", "disrupcao_de_morto_vivo"],
                magias_nivel_1_prioritarias=["curar", "bencao", "protecao", "santuario"],
            ),
            fonte_divina_preferida="cura",
        ),
        _conceito(
            id_conceito="clerigo_arauto_guerra",
            classe_id="clerigo",
            classe_nome="Clérigo",
            nome="Arauto da Guerra (Sacerdote Blindado)",
            subclasses_oficiais=[("capelao_da_guerra", "Capelão da Guerra")],
            resumo_proposta=(
                "Sacerdote marcial blindado que luta na linha de frente e canaliza "
                "energia divina através da própria arma."
            ),
            sinergia_mecanica=(
                "A Doutrina Capelão da Guerra concede armaduras médias, escudo e arma "
                "favorita; combina Simplicidade Mortal (1º) com Ornar Armamento (2º), "
                "Canalizar Punição (4º) e Arma Divina (6º)."
            ),
            prioridade_atributos=["sab", "for", "con", "car", "des", "int"],
            biografias_recomendadas=["soldado", "acolito", "guarda", "gladiador"],
            pericias_prioritarias=["religiao", "atletismo", "intimidacao", "medicina", "diplomacia"],
            saber_sugerido="Saber de Guerra",
            talentos_classe_n1=["simplicidade_mortal", "maos_curandeiras", "castigo_sagrado"],
            talentos_classe_n2_mais=["ornar_armamento", "canalizar_punicao", "arma_divina"],
            talentos_pericia=["olhar_intimidante", "medicina_de_batalha", "carregador_robusto"],
            talentos_gerais=["vitalidade", "duro_de_matar", "proficiencia_com_armaduras"],
            tracos_ancestralidade_afinidade=["arma", "forca", "guerra", "resistencia"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_escamas", "gibao_de_peles", "couro_batido"],
            usa_escudo=True,
            escudos_ids=["escudo_de_aco", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["maca", "lanca", "adaga"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao_e_escudo",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["abjuracao", "encantamento", "positivo"],
                escolas_prioritarias=["abjuracao", "encantamento", "transmutacao"],
                truques_prioritarios=["escudo_mistico", "orientacao", "lanca_divina", "estabilizar", "luz"],
                magias_nivel_1_prioritarias=["arma_magica", "bencao", "curar", "protecao"],
            ),
            fonte_divina_preferida="cura",
            fontes_divinas_aceitas=["cura", "ferimento"],
        ),
        _conceito(
            id_conceito="clerigo_ceifador_sombrio",
            classe_id="clerigo",
            classe_nome="Clérigo",
            nome="Ceifador Sombrio (Canalizador Negativo)",
            subclasses_oficiais=[("sacerdote_enclausurado", "Sacerdote Enclausurado")],
            resumo_proposta=(
                "Clérigo de energia negativa que usa Fonte de Ferimento para devastar "
                "inimigos vivos em área e comandar mortos-vivos."
            ),
            sinergia_mecanica=(
                "Fonte de Ferimento com Mãos Agressoras (1º) ou Magia de Alcance (1º) "
                "e Carisma secundário; evolui com Canalização Direcionada (4º) para "
                "cones de dano negativo e Comandar Mortos-Vivos (4º)."
            ),
            prioridade_atributos=["sab", "car", "con", "des", "int", "for"],
            biografias_recomendadas=["eremita", "acolito", "vidente", "estudioso"],
            pericias_prioritarias=["religiao", "intimidacao", "ocultismo", "medicina", "sociedade"],
            saber_sugerido="Saber Necromântico",
            talentos_classe_n1=["maos_agressoras", "magia_de_alcance", "iniciado_no_dominio"],
            talentos_classe_n2_mais=["canalizacao_direcionada", "comandar_mortos_vivos", "infusao_necrotica"],
            talentos_pericia=["olhar_intimidante", "estudante_do_canone", "identificacao_rapida"],
            talentos_gerais=["iniciativa_incrivel", "vitalidade", "duro_de_matar"],
            tracos_ancestralidade_afinidade=["morte", "sombra", "negativo", "intimidacao"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["foice", "adaga"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="uma_mao",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["negativo", "morte", "medo", "necromancia"],
                escolas_prioritarias=["necromancia", "encantamento", "evocacao"],
                truques_prioritarios=["toque_gelido", "lanca_divina", "escudo_mistico", "pasmar", "ler_aura"],
                magias_nivel_1_prioritarias=["ferir", "ruina", "medo", "raio_de_enfraquecimento"],
            ),
            fonte_divina_preferida="ferimento",
            tendencia_preferida="N",
        ),
        _conceito(
            id_conceito="clerigo_teologo_dominios",
            classe_id="clerigo",
            classe_nome="Clérigo",
            nome="Teólogo dos Domínios (Conjurador Especialista)",
            subclasses_oficiais=[("sacerdote_enclausurado", "Sacerdote Enclausurado")],
            resumo_proposta=(
                "Erudito religioso que extrai o máximo das magias de foco dos domínios "
                "de sua divindade e de conjuração divina versátil."
            ),
            sinergia_mecanica=(
                "Clérigo Claustro recebe Iniciado no Domínio (1º) gratuitamente e "
                "escala para Domínio Avançado (8º) e Foco de Domínio (12º), "
                "combinado com Magia de Alcance (1º) e Expansão de Truque Mágico (2º)."
            ),
            prioridade_atributos=["sab", "con", "des", "car", "int", "for"],
            biografias_recomendadas=["acolito", "estudioso", "vidente", "emissario"],
            pericias_prioritarias=["religiao", "diplomacia", "ocultismo", "sociedade", "medicina"],
            saber_sugerido="Saber de Teologia",
            talentos_classe_n1=["iniciado_no_dominio", "magia_de_alcance", "castigo_sagrado"],
            talentos_classe_n2_mais=["expansao_de_truque_magico", "dominio_avancado", "foco_de_dominio"],
            talentos_pericia=["estudante_do_canone", "reconhecer_magia", "poliglota"],
            talentos_gerais=["iniciativa_incrivel", "perspicacia_astuta", "vitalidade"],
            tracos_ancestralidade_afinidade=["divino", "fogo", "luz", "saber"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "clava"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["fogo", "luz", "positivo", "divino"],
                escolas_prioritarias=["evocacao", "abjuracao", "adivinhacao"],
                truques_prioritarios=["lanca_divina", "disrupcao_de_morto_vivo", "luz", "orientacao", "detectar_magia"],
                magias_nivel_1_prioritarias=["bencao", "curar", "comando", "protecao"],
            ),
            fonte_divina_preferida="cura",
            fontes_divinas_aceitas=["cura", "ferimento"],
        ),
        _conceito(
            id_conceito="clerigo_inquisidor_expurgador",
            classe_id="clerigo",
            classe_nome="Clérigo",
            nome="Inquisidor Expurgador (Caçador de Mortos-Vivos e Ímpios)",
            subclasses_oficiais=[("capelao_da_guerra", "Capelão da Guerra")],
            resumo_proposta=(
                "Exorcista de campo equipado para caçar mortos-vivos e ínferos, "
                "convertendo energia positiva em dano sagrado purificador."
            ),
            sinergia_mecanica=(
                "Capelão da Guerra une Castigo Sagrado (1º) para ferir ínferos com "
                "Curar a Afastar Mortos-Vivos (2º), Canalizar Punição (4º) e Armas "
                "de Disrupção no 1º círculo."
            ),
            prioridade_atributos=["sab", "des", "car", "con", "for", "int"],
            biografias_recomendadas=["detetive", "cacador_de_recompensas", "acolito", "guarda"],
            pericias_prioritarias=["religiao", "medicina", "furtividade", "intimidacao", "sobrevivencia"],
            saber_sugerido="Saber de Mortos-Vivos",
            talentos_classe_n1=["castigo_sagrado", "simplicidade_mortal", "maos_curandeiras"],
            talentos_classe_n2_mais=["afastar_mortos_vivos", "canalizar_punicao", "arma_divina"],
            talentos_pericia=["estudante_do_canone", "identificacao_rapida", "medicina_de_batalha"],
            talentos_gerais=["iniciativa_incrivel", "vitalidade", "perspicacia_astuta"],
            tracos_ancestralidade_afinidade=["luz", "positivo", "sagrado", "visao"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "cota_de_escamas", "couro"],
            usa_escudo=True,
            escudos_ids=["escudo_de_madeira", "broquel"],
            armas_corpo_a_corpo_ids=["maca_estrela", "maca", "adaga"],
            armas_distancia_ids=["besta_leve", "funda"],
            estilo_empunhadura="uma_mao_e_escudo",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["positivo", "luz", "cura", "bem"],
                escolas_prioritarias=["necromancia", "evocacao", "abjuracao"],
                truques_prioritarios=["disrupcao_de_morto_vivo", "lanca_divina", "luz", "protecao_proibitiva", "orientacao"],
                magias_nivel_1_prioritarias=["armas_de_disrupcao", "curar", "protecao", "detectar_tendencia"],
            ),
            fonte_divina_preferida="cura",
        ),
        _conceito(
            id_conceito="clerigo_pregador_carismatico",
            classe_id="clerigo",
            classe_nome="Clérigo",
            nome="Orador Eclesiástico (Arauto Diplomata e Comandante)",
            subclasses_oficiais=[("sacerdote_enclausurado", "Sacerdote Enclausurado")],
            resumo_proposta=(
                "Emissário sagrado de Carisma elevado que lidera negociações, amplia "
                "o alcance de bênçãos e dita ordens divinas no campo de batalha."
            ),
            sinergia_mecanica=(
                "Prioriza Magia de Alcance (1º) para lançar Santuário, Bênção e Curar "
                "a 9 metros com estoque máximo de Fonte Divina via Carisma; escala "
                "com Fonte Versátil (2º) e Canalização Direcionada (4º)."
            ),
            prioridade_atributos=["sab", "car", "des", "con", "int", "for"],
            biografias_recomendadas=["emissario", "nobre", "advogado", "acolito"],
            pericias_prioritarias=["religiao", "diplomacia", "sociedade", "intimidacao", "ocultismo"],
            saber_sugerido="Saber de Heráldica",
            talentos_classe_n1=["magia_de_alcance", "iniciado_no_dominio", "maos_curandeiras"],
            talentos_classe_n2_mais=["fonte_versatil", "expansao_de_truque_magico", "canalizacao_direcionada"],
            talentos_pericia=["impressionar_grupo", "gracejos_da_corte", "estudante_do_canone"],
            talentos_gerais=["iniciativa_incrivel", "perspicacia_astuta", "vitalidade"],
            tracos_ancestralidade_afinidade=["carisma", "diplomacia", "divino", "inspiracao"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga"],
            armas_distancia_ids=["besta_leve", "funda"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["mental", "encantamento", "emocao", "cura"],
                escolas_prioritarias=["encantamento", "abjuracao", "adivinhacao"],
                truques_prioritarios=["orientacao", "mensagem", "protecao_proibitiva", "escudo_mistico", "detectar_magia"],
                magias_nivel_1_prioritarias=["comando", "santuario", "bencao", "vinculo_espiritual"],
            ),
            fonte_divina_preferida="cura",
            fontes_divinas_aceitas=["cura", "ferimento"],
        ),

        # =====================================================================
        # 6. DRUIDA (6) — Restrição obrigatória: sem armadura/escudo de metal
        # =====================================================================
        _conceito(
            id_conceito="druida_metamorfo_primal",
            classe_id="druida",
            classe_nome="Druida",
            nome="Metamorfo Primal (Combatente Bestial)",
            subclasses_oficiais=[("selvagens", "Selvagens")],
            resumo_proposta=(
                "Druida combatente que assume garras, mordidas e formas bestiais ou "
                "elementais para lutar diretamente na linha de frente."
            ),
            sinergia_mecanica=(
                "A Ordem dos Selvagens concede morfia selvagem e Aspecto Selvagem (1º), "
                "evoluindo para Aspecto de Inseto (6º), Aspecto de Elemental (10º) e "
                "Aspecto de Dragão (12º) para manter relevância marcial."
            ),
            prioridade_atributos=["sab", "for", "con", "des", "int", "car"],
            biografias_recomendadas=["eremita", "nomade", "cacador", "herbalista"],
            pericias_prioritarias=["natureza", "atletismo", "intimidacao", "sobrevivencia", "acrobatismo"],
            saber_sugerido="Saber de Feras",
            talentos_classe_n1=["aspecto_selvagem", "magia_de_alcance"],
            talentos_classe_n2_mais=["aspecto_de_inseto", "aspecto_de_elemental", "aspecto_de_dragao"],
            talentos_pericia=["lutador_titanico", "escalador_de_combate", "forrageador"],
            talentos_gerais=["vitalidade", "duro_de_matar", "veloz"],
            tracos_ancestralidade_afinidade=["garras", "mordida", "forca", "selvagem"],
            categoria_armadura_preferida="media",
            armaduras_ids=["gibao_de_peles", "couro_batido", "couro"],
            usa_escudo=True,
            escudos_ids=["escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["lanca", "clava", "adaga"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="uma_mao_e_escudo",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["metamorfose", "transmutacao", "cura"],
                escolas_prioritarias=["transmutacao", "evocacao", "necromancia"],
                truques_prioritarios=["produzir_chama", "emaranhape", "orientacao", "estabilizar", "detectar_magia"],
                magias_nivel_1_prioritarias=["presa_magica", "passos_velozes", "curar", "salto"],
            ),
        ),
        _conceito(
            id_conceito="druida_senhor_matilha",
            classe_id="druida",
            classe_nome="Druida",
            nome="Senhor da Matilha (Dupla Tática)",
            subclasses_oficiais=[("animais", "Animais")],
            resumo_proposta=(
                "Guardião selvagem que entra em combate acompanhado por uma fera "
                "leal para flanquear, derrubar e pressionar adversários juntos."
            ),
            sinergia_mecanica=(
                "A Ordem Animal concede Companheiro Animal (1º) gratuito, escalando "
                "com Companheiro Animal Maduro (4º), Companheiro Incrível (8º) e "
                "Companheiro Especializado (14º) mais magias de apoio."
            ),
            prioridade_atributos=["sab", "con", "des", "for", "car", "int"],
            biografias_recomendadas=["encantador_de_animais", "cacador", "herbalista", "batedor"],
            pericias_prioritarias=["natureza", "sobrevivencia", "atletismo", "medicina", "diplomacia"],
            saber_sugerido="Saber de Fauna",
            talentos_classe_n1=["companheiro_animal", "magia_de_alcance"],
            talentos_classe_n2_mais=["companheiro_animal_maduro", "companheiro_incrivel", "companheiro_especializado"],
            talentos_pericia=["treinar_animal", "medicina_natural", "forrageador"],
            talentos_gerais=["cavalgar", "vitalidade", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["animal", "natureza", "floresta"],
            categoria_armadura_preferida="media",
            armaduras_ids=["gibao_de_peles", "couro_batido", "couro"],
            usa_escudo=True,
            escudos_ids=["escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["lanca", "foice", "clava"],
            armas_distancia_ids=["funda", "dardo"],
            estilo_empunhadura="uma_mao_e_escudo",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["animal", "cura", "transmutacao"],
                escolas_prioritarias=["conjuracao", "transmutacao", "necromancia"],
                truques_prioritarios=["orientacao", "estabilizar", "emaranhape", "produzir_chama", "arco_eletrico"],
                magias_nivel_1_prioritarias=["presa_magica", "convocar_animal", "curar", "passos_largos"],
            ),
        ),
        _conceito(
            id_conceito="druida_furia_elementos",
            classe_id="druida",
            classe_nome="Druida",
            nome="Fúria dos Elementos (Artilheiro Primal)",
            subclasses_oficiais=[("tempestade", "Tempestade")],
            resumo_proposta=(
                "Conjurador primal ofensivo que invoca raios, ventos e tempestades "
                "para causar dano elemental em área sem sofrer penalidades climáticas."
            ),
            sinergia_mecanica=(
                "Ordem da Tempestade começa com 2 Pontos de Foco, surto da tempestade "
                "e Nascido da Tempestade (1º); escala com Ampliar Magia (1º), "
                "Retribuição da Tempestade (6º) e Invocador de Ventos (8º)."
            ),
            prioridade_atributos=["sab", "des", "con", "int", "car", "for"],
            biografias_recomendadas=["marinheiro", "nomade", "eremita", "estudioso"],
            pericias_prioritarias=["natureza", "acrobatismo", "sobrevivencia", "medicina", "atletismo"],
            saber_sugerido="Saber de Clima",
            talentos_classe_n1=["nascido_da_tempestade", "ampliar_magia", "magia_de_alcance"],
            talentos_classe_n2_mais=["retribuicao_da_tempestade", "invocador_de_ventos", "energia_avassaladora"],
            talentos_pericia=["esgueirador_de_terreno", "forrageador", "reconhecer_magia"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["eletricidade", "vento", "tempestade", "ar"],
            categoria_armadura_preferida="media",
            armaduras_ids=["gibao_de_peles", "couro_batido", "couro"],
            usa_escudo=True,
            escudos_ids=["escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["cajado", "lanca", "adaga"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="uma_mao_e_escudo",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["eletricidade", "ar", "fogo", "frio", "agua"],
                escolas_prioritarias=["evocacao", "conjuracao"],
                truques_prioritarios=["arco_eletrico", "produzir_chama", "raio_de_gelo", "emaranhape", "detectar_magia"],
                magias_nivel_1_prioritarias=["toque_chocante", "maos_flamejantes", "lufada_de_vento", "empurrao_hidraulico"],
            ),
        ),
        _conceito(
            id_conceito="druida_guardiao_botanico",
            classe_id="druida",
            classe_nome="Druida",
            nome="Guardião Botânico (Suporte e Familiar)",
            subclasses_oficiais=[("folha", "Folha")],
            resumo_proposta=(
                "Protetor das florestas focado em cura constante fora de combate, "
                "controle de terreno natural e apoio de um familiar planta."
            ),
            sinergia_mecanica=(
                "A Ordem da Folha concede Familiar Leshy (1º) e a magia boa baga; "
                "escala com Familiar Melhorado (2º), Empatia Verde (6º) e Aspecto de "
                "Planta (10º) com magias de controle vegetal e cura."
            ),
            prioridade_atributos=["sab", "con", "des", "car", "int", "for"],
            biografias_recomendadas=["herbalista", "eremita", "lavrador", "medico_de_campo"],
            pericias_prioritarias=["natureza", "diplomacia", "medicina", "sobrevivencia", "manufatura"],
            saber_sugerido="Saber de Botânica",
            talentos_classe_n1=["familiar_leshy", "magia_de_alcance", "ampliar_magia"],
            talentos_classe_n2_mais=["familiar_melhorado", "empatia_verde", "aspecto_de_planta"],
            talentos_pericia=["medicina_natural", "forrageador", "medicina_de_batalha"],
            talentos_gerais=["vitalidade", "recuperacao_rapida", "duro_de_matar"],
            tracos_ancestralidade_afinidade=["planta", "floresta", "cura", "fada"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro", "gibao_de_peles", "armadura_acolchoada"],
            usa_escudo=True,
            escudos_ids=["escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["cajado", "foice", "clava"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="uma_mao_e_escudo",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["planta", "cura", "terra", "agua"],
                escolas_prioritarias=["conjuracao", "transmutacao", "necromancia"],
                truques_prioritarios=["emaranhape", "estabilizar", "orientacao", "jorro_acido", "luz"],
                magias_nivel_1_prioritarias=["bastao_de_abrunheiro", "curar", "convocar_planta_ou_fungo", "passos_sem_pegadas"],
            ),
        ),
        _conceito(
            id_conceito="druida_piromante_cinzas",
            classe_id="druida",
            classe_nome="Druida",
            nome="Piromante das Cinzas (Incendiário Primal)",
            subclasses_oficiais=[("tempestade", "Tempestade"), ("folha", "Folha")],
            resumo_proposta=(
                "Conjurador primal de fogo, fumaça e ácido que amplia o raio de suas "
                "explosões para controlar grandes áreas de terreno."
            ),
            sinergia_mecanica=(
                "Prioriza Ampliar Magia (1º) para expandir áreas elementais e "
                "combina Produzir Chama, Jorro Ácido e Mãos Flamejantes com "
                "Explorador de Ordem (2º) e Conjuração Consistente (6º)."
            ),
            prioridade_atributos=["sab", "des", "con", "int", "car", "for"],
            biografias_recomendadas=["nomade", "eremita", "herbalista", "mineiro"],
            pericias_prioritarias=["natureza", "sobrevivencia", "acrobatismo", "arcanismo", "intimidacao"],
            saber_sugerido="Saber de Vulcões",
            talentos_classe_n1=["ampliar_magia", "nascido_da_tempestade", "magia_de_alcance"],
            talentos_classe_n2_mais=["explorador_de_ordem", "magia_de_ordem", "conjuracao_consistente"],
            talentos_pericia=["reconhecer_magia", "forrageador", "esgueirador_de_terreno"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["fogo", "terra", "deserto", "elemental"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro", "gibao_de_peles"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "foice", "adaga"],
            armas_distancia_ids=["funda", "dardo"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["fogo", "acido", "terra", "evocacao"],
                escolas_prioritarias=["evocacao", "conjuracao", "transmutacao"],
                truques_prioritarios=["produzir_chama", "jorro_acido", "arco_eletrico", "detectar_magia", "luz"],
                magias_nivel_1_prioritarias=["maos_flamejantes", "lubrificar", "passos_largos", "alarme"],
            ),
        ),
        _conceito(
            id_conceito="druida_errante_ermos",
            classe_id="druida",
            classe_nome="Druida",
            nome="Andarilho dos Ermos (Batedor e Sobrevivente)",
            subclasses_oficiais=[("selvagens", "Selvagens"), ("folha", "Folha")],
            resumo_proposta=(
                "Guia furtivo das fronteiras selvagens que combina lança longa, "
                "magias de mobilidade e camuflagem natural para emboscadas."
            ),
            sinergia_mecanica=(
                "Une Magia de Alcance (1º) e lança longa (alcance 3m) a Chamado dos "
                "Ermos (2º), Deslocamento da Floresta (4º) e Mil Faces (4º), "
                "cobrindo rastreamento, furtividade e cura de expedição."
            ),
            prioridade_atributos=["sab", "des", "con", "for", "int", "car"],
            biografias_recomendadas=["batedor", "cacador", "nomade", "herbalista"],
            pericias_prioritarias=["natureza", "sobrevivencia", "furtividade", "medicina", "atletismo"],
            saber_sugerido="Saber de Ermos",
            talentos_classe_n1=["magia_de_alcance", "aspecto_selvagem", "familiar_leshy"],
            talentos_classe_n2_mais=["chamado_dos_ermos", "deslocamento_da_floresta", "mil_faces"],
            talentos_pericia=["rastreador_experiente", "esgueirador_de_terreno", "medicina_natural"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["floresta", "velocidade", "furtividade", "natureza"],
            categoria_armadura_preferida="media",
            armaduras_ids=["couro_batido", "gibao_de_peles", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["lanca_longa", "lanca", "foice"],
            armas_distancia_ids=["azagaia", "funda"],
            estilo_empunhadura="duas_maos",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["planta", "animal", "transmutacao", "deteccao"],
                escolas_prioritarias=["transmutacao", "adivinhacao", "abjuracao"],
                truques_prioritarios=["intuir_direcao", "emaranhape", "orientacao", "estabilizar", "raio_de_gelo"],
                magias_nivel_1_prioritarias=["passos_sem_pegadas", "passos_largos", "anular_aroma", "curar"],
            ),
        ),

        # =====================================================================
        # 7. FEITICEIRO (6)
        # =====================================================================
        _conceito(
            id_conceito="feiticeiro_artifice_elemental_draconico",
            classe_id="feiticeiro",
            classe_nome="Feiticeiro",
            nome="Artífice Elemental / Dracônico (Explosão Bruta)",
            subclasses_oficiais=[("draconica", "Dracônica"), ("elemental", "Elemental")],
            resumo_proposta=(
                "Conjurador espontâneo destrutivo focado em bônus direto no dano "
                "elemental e explosões em área para limpar grupos inteiros."
            ),
            sinergia_mecanica=(
                "Linhagem Dracônica ou Elemental soma bônus de magia sanguínea no dano, "
                "potencializado por Feitiçaria Perigosa (1º), Ampliar Magia (1º), "
                "Linhagem Avançada (6º) e Energia Avassaladora (10º)."
            ),
            prioridade_atributos=["car", "des", "con", "sab", "int", "for"],
            biografias_recomendadas=["nobre", "vidente", "nomade", "charlatao"],
            pericias_prioritarias=["arcanismo", "natureza", "intimidacao", "acrobatismo", "diplomacia"],
            saber_sugerido="Saber Elemental",
            talentos_classe_n1=["feiticaria_perigosa", "ampliar_magia", "magia_de_alcance"],
            talentos_classe_n2_mais=["linhagem_avancada", "resistencia_de_linhagem", "energia_avassaladora"],
            talentos_pericia=["olhar_intimidante", "reconhecer_magia", "identificacao_rapida"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["fogo", "dragao", "elemental", "evocacao"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "clava"],
            armas_distancia_ids=["besta_leve", "funda"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["fogo", "eletricidade", "frio", "acido", "evocacao"],
                escolas_prioritarias=["evocacao", "abjuracao"],
                truques_prioritarios=["produzir_chama", "arco_eletrico", "raio_de_gelo", "escudo_mistico", "detectar_magia"],
                magias_nivel_1_prioritarias=["maos_flamejantes", "misseis_magicos", "toque_chocante", "armadura_mistica"],
            ),
            conjuracao_por_tradicao={
                "arcana": _conjuracao(
                    tradicao="arcana",
                    tracos_prioritarios=["fogo", "eletricidade", "frio", "acido", "evocacao"],
                    escolas_prioritarias=["evocacao", "abjuracao"],
                    truques_prioritarios=["produzir_chama", "arco_eletrico", "raio_de_gelo", "escudo_mistico", "detectar_magia"],
                    magias_nivel_1_prioritarias=["maos_flamejantes", "misseis_magicos", "toque_chocante", "armadura_mistica"],
                ),
                "primal": _conjuracao(
                    tradicao="primal",
                    tracos_prioritarios=["fogo", "eletricidade", "frio", "ar", "terra"],
                    escolas_prioritarias=["evocacao", "transmutacao"],
                    truques_prioritarios=["produzir_chama", "arco_eletrico", "raio_de_gelo", "jorro_acido", "detectar_magia"],
                    magias_nivel_1_prioritarias=["maos_flamejantes", "toque_chocante", "empurrao_hidraulico", "lufada_de_vento"],
                ),
            },
        ),
        _conceito(
            id_conceito="feiticeiro_manipulador_feerico_aberrante",
            classe_id="feiticeiro",
            classe_nome="Feiticeiro",
            nome="Manipulador Feérico / Aberrante (Controle Mental)",
            subclasses_oficiais=[("feerica", "Feérica"), ("aberrante", "Aberrante")],
            resumo_proposta=(
                "Conjurador sutil especializado em ilusões, encantamentos e "
                "debilitamentos mentais em cenas sociais ou emboscadas."
            ),
            sinergia_mecanica=(
                "Linhagem Feérica ou Aberrante combina Magia de Alcance (1º) e "
                "Familiar (1º) com Expansão de Truque Mágico (2º), Linhagem Avançada "
                "(6º) e Conjuração Consistente (6º) para controle tático."
            ),
            prioridade_atributos=["car", "des", "con", "sab", "int", "for"],
            biografias_recomendadas=["charlatao", "vidente", "emissario", "animador"],
            pericias_prioritarias=["dissimulacao", "diplomacia", "natureza", "ocultismo", "furtividade"],
            saber_sugerido="Saber de Fadas",
            talentos_classe_n1=["magia_de_alcance", "familiar", "ampliar_magia"],
            talentos_classe_n2_mais=["expansao_de_truque_magico", "linhagem_avancada", "conjuracao_consistente"],
            talentos_pericia=["mentiroso_charmoso", "distracao_prolongada", "identificar_estranhezas"],
            talentos_gerais=["iniciativa_incrivel", "perspicacia_astuta", "vitalidade"],
            tracos_ancestralidade_afinidade=["fada", "ilusao", "mental", "carisma"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "clava"],
            armas_distancia_ids=["funda", "besta_leve"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["mental", "ilusao", "encantamento", "emocao"],
                escolas_prioritarias=["encantamento", "ilusao", "adivinhacao"],
                truques_prioritarios=["emaranhape", "luzes_dancantes", "prestidigitacao", "orientacao", "detectar_magia"],
                magias_nivel_1_prioritarias=["cativar", "medo", "convocar_fada", "passos_sem_pegadas"],
            ),
            conjuracao_por_tradicao={
                "primal": _conjuracao(
                    tradicao="primal",
                    tracos_prioritarios=["mental", "ilusao", "encantamento", "emocao"],
                    escolas_prioritarias=["encantamento", "ilusao", "adivinhacao"],
                    truques_prioritarios=["emaranhape", "luzes_dancantes", "prestidigitacao", "orientacao", "detectar_magia"],
                    magias_nivel_1_prioritarias=["cativar", "medo", "convocar_fada", "passos_sem_pegadas"],
                ),
                "ocultista": _conjuracao(
                    tradicao="ocultista",
                    tracos_prioritarios=["mental", "ilusao", "encantamento", "emocao"],
                    escolas_prioritarias=["encantamento", "ilusao", "adivinhacao"],
                    truques_prioritarios=["pasmar", "som_fantasma", "projetil_telecinetico", "escudo_mistico", "detectar_magia"],
                    magias_nivel_1_prioritarias=["cativar", "medo", "sono", "disfarce_ilusorio"],
                ),
            },
        ),
        _conceito(
            id_conceito="feiticeiro_emissario_celestial_infernal",
            classe_id="feiticeiro",
            classe_nome="Feiticeiro",
            nome="Emissário Celestial ou Infernal (Suporte ou Maldição)",
            subclasses_oficiais=[
                ("angelical", "Angelical"),
                ("diabolica", "Diabólica"),
                ("demoniaca", "Demoníaca"),
            ],
            resumo_proposta=(
                "Canalizador espontâneo de magia divina que abençoa aliados com "
                "aura angelical ou amaldiçoa inimigos com fogo infernal."
            ),
            sinergia_mecanica=(
                "Linhagens Divinas combinam magias de linhagem (halo angelical / "
                "fogo infernal / gula demoníaca) com Magia de Alcance (1º), Feitiçaria "
                "Perigosa (1º) e Evolução Divina (4º) para espaços extras de curar/ferir."
            ),
            prioridade_atributos=["car", "con", "des", "sab", "int", "for"],
            biografias_recomendadas=["acolito", "emissario", "nobre", "advogado"],
            pericias_prioritarias=["religiao", "diplomacia", "intimidacao", "dissimulacao", "medicina"],
            saber_sugerido="Saber Planar",
            talentos_classe_n1=["magia_de_alcance", "feiticaria_perigosa", "ampliar_magia"],
            talentos_classe_n2_mais=["evolucao_divina", "linhagem_avancada", "resistencia_de_linhagem"],
            talentos_pericia=["estudante_do_canone", "olhar_intimidante", "gracejos_da_corte"],
            talentos_gerais=["vitalidade", "duro_de_matar", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["divino", "fogo", "cura", "carisma"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "clava"],
            armas_distancia_ids=["funda", "besta_leve"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["cura", "divino", "fogo", "medo"],
                escolas_prioritarias=["encantamento", "abjuracao", "necromancia"],
                truques_prioritarios=["lanca_divina", "escudo_mistico", "orientacao", "estabilizar", "luz"],
                magias_nivel_1_prioritarias=["curar", "bencao", "ferir", "comando"],
            ),
        ),
        _conceito(
            id_conceito="feiticeiro_arquimago_versatil",
            classe_id="feiticeiro",
            classe_nome="Feiticeiro",
            nome="Arquimago Versátil (Mestre do Repertório)",
            subclasses_oficiais=[("imperial", "Imperial")],
            resumo_proposta=(
                "Herdeiro de linhagem arcana antiga que amplia perícias com magia "
                "ancestral e ganha acesso a grimório auxiliar mesmo sendo espontâneo."
            ),
            sinergia_mecanica=(
                "Linhagem Imperial combina Contramágica (1º), Magia de Alcance (1º) "
                "e Familiar (1º) com Evolução Arcana (4º) e Expansão de Truque Mágico "
                "(2º) para máxima flexibilidade de magias conhecidas."
            ),
            prioridade_atributos=["car", "des", "con", "int", "sab", "for"],
            biografias_recomendadas=["estudioso", "nobre", "emissario", "advogado"],
            pericias_prioritarias=["arcanismo", "sociedade", "diplomacia", "ocultismo", "acrobatismo"],
            saber_sugerido="Saber Arcano",
            talentos_classe_n1=["contramagica", "magia_de_alcance", "familiar"],
            talentos_classe_n2_mais=["evolucao_arcana", "expansao_de_truque_magico", "linhagem_avancada"],
            talentos_pericia=["sentido_arcano", "reconhecer_magia", "identificacao_rapida"],
            talentos_gerais=["iniciativa_incrivel", "perspicacia_astuta", "vitalidade"],
            tracos_ancestralidade_afinidade=["arcano", "saber", "inteligencia"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "cajado"],
            armas_distancia_ids=["besta_leve", "funda"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["forca", "abjuracao", "evocacao", "adivinhacao"],
                escolas_prioritarias=["evocacao", "abjuracao", "transmutacao"],
                truques_prioritarios=["escudo_mistico", "projetil_telecinetico", "detectar_magia", "arco_eletrico", "prestidigitacao"],
                magias_nivel_1_prioritarias=["misseis_magicos", "armadura_mistica", "golpe_certo", "queda_suave"],
            ),
        ),
        _conceito(
            id_conceito="feiticeiro_herdeiro_morto_vivo",
            classe_id="feiticeiro",
            classe_nome="Feiticeiro",
            nome="Herdeiro dos Mortos-Vivos (Necromante de Sangue)",
            subclasses_oficiais=[("morta_viva", "Morta-Viva")],
            resumo_proposta=(
                "Conjurador marcado pelo toque da morte que drena vitalidade inimiga "
                "com energia negativa e resiste a efeitos letais."
            ),
            sinergia_mecanica=(
                "Linhagem Morta-Viva (tradição divina, Ferir no repertório e magia "
                "de foco Toque dos Mortos-Vivos) somada a Feitiçaria Perigosa (1º), "
                "Evolução Divina (4º) e Linhagem Avançada (6º)."
            ),
            prioridade_atributos=["car", "con", "des", "sab", "int", "for"],
            biografias_recomendadas=["eremita", "acolito", "vidente", "prisioneiro"],
            pericias_prioritarias=["religiao", "intimidacao", "medicina", "ocultismo", "furtividade"],
            saber_sugerido="Saber Necromântico",
            talentos_classe_n1=["feiticaria_perigosa", "magia_de_alcance", "familiar"],
            talentos_classe_n2_mais=["evolucao_divina", "linhagem_avancada", "resistencia_de_linhagem"],
            talentos_pericia=["olhar_intimidante", "estudante_do_canone", "medicina_de_batalha"],
            talentos_gerais=["duro_de_matar", "vitalidade", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["morte", "negativo", "sombra", "resistencia"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["foice", "adaga"],
            armas_distancia_ids=["besta_leve", "funda"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["negativo", "necromancia", "morte", "medo"],
                escolas_prioritarias=["necromancia", "abjuracao", "encantamento"],
                truques_prioritarios=["toque_gelido", "escudo_mistico", "lanca_divina", "pasmar", "detectar_magia"],
                magias_nivel_1_prioritarias=["ferir", "raio_de_enfraquecimento", "ruina", "medo"],
            ),
            conjuracao_por_tradicao={
                "divina": _conjuracao(
                    tradicao="divina",
                    tracos_prioritarios=["negativo", "necromancia", "morte", "medo"],
                    escolas_prioritarias=["necromancia", "abjuracao", "encantamento"],
                    truques_prioritarios=["toque_gelido", "escudo_mistico", "lanca_divina", "pasmar", "detectar_magia"],
                    magias_nivel_1_prioritarias=["ferir", "raio_de_enfraquecimento", "ruina", "medo"],
                ),
            },
        ),
        _conceito(
            id_conceito="feiticeiro_bruxo_estriga",
            classe_id="feiticeiro",
            classe_nome="Feiticeiro",
            nome="Bruxo da Estriga (Maldições e Familiar Ocultista)",
            subclasses_oficiais=[("estriga", "Estriga")],
            resumo_proposta=(
                "Místico ocultista ligado ao sangue de bruxas que lança maldições "
                "ciumentas, ilusões traiçoeiras e conta com um familiar espião."
            ),
            sinergia_mecanica=(
                "Linhagem Estriga (tradição ocultista e Maldição Ciumenta) combinada "
                "com Familiar (1º), Familiar Melhorado (2º), Evolução Ocultista (4º) "
                "e Linhagem Avançada (6º)."
            ),
            prioridade_atributos=["car", "des", "con", "int", "sab", "for"],
            biografias_recomendadas=["vidente", "herbalista", "eremita", "charlatao"],
            pericias_prioritarias=["ocultismo", "dissimulacao", "intimidacao", "natureza", "furtividade"],
            saber_sugerido="Saber de Maldições",
            talentos_classe_n1=["familiar", "magia_de_alcance", "contramagica"],
            talentos_classe_n2_mais=["familiar_melhorado", "evolucao_ocultista", "linhagem_avancada"],
            talentos_pericia=["identificar_estranhezas", "olhar_intimidante", "mentiroso_charmoso"],
            talentos_gerais=["perspicacia_astuta", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["maldicao", "ocultismo", "ilusao", "sombra"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga", "foice"],
            armas_distancia_ids=["funda", "dardo"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="ocultista",
                tracos_prioritarios=["maldicao", "mental", "ilusao", "necromancia"],
                escolas_prioritarias=["encantamento", "necromancia", "ilusao"],
                truques_prioritarios=["pasmar", "toque_gelido", "som_fantasma", "ler_aura", "escudo_mistico"],
                magias_nivel_1_prioritarias=["dor_fantasma", "ruina", "medo", "gavinhas_sombrias"],
            ),
            conjuracao_por_tradicao={
                "ocultista": _conjuracao(
                    tradicao="ocultista",
                    tracos_prioritarios=["maldicao", "mental", "ilusao", "necromancia"],
                    escolas_prioritarias=["encantamento", "necromancia", "ilusao"],
                    truques_prioritarios=["pasmar", "toque_gelido", "som_fantasma", "ler_aura", "escudo_mistico"],
                    magias_nivel_1_prioritarias=["dor_fantasma", "ruina", "medo", "gavinhas_sombrias"],
                ),
            },
        ),

        # =====================================================================
        # 8. GUERREIRO (6)
        # =====================================================================
        _conceito(
            id_conceito="guerreiro_muralha_aco",
            classe_id="guerreiro",
            classe_nome="Guerreiro",
            nome="Muralha de Aço (Arma e Escudo)",
            subclasses_oficiais=[("duelista", "Duelista (Arma de Uma Mão e Mão Livre)")],
            resumo_proposta=(
                "Defensor implacável de espada e escudo que controla o terreno com "
                "Ataque de Oportunidade, reações defensivas e proteção aos aliados."
            ),
            sinergia_mecanica=(
                "Une Bloqueio com Escudo gratuito a Escudo Reativo (1º), evoluindo "
                "para Bloqueio Agressivo (2º), Guardião de Escudo (6º), Escudo "
                "Reflexivo (6º) e Bloqueio Rápido com Escudo (8º)."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "car", "int"],
            biografias_recomendadas=["guarda", "soldado", "nobre", "operario"],
            pericias_prioritarias=["atletismo", "intimidacao", "medicina", "sobrevivencia", "acrobatismo"],
            saber_sugerido="Saber de Guerra",
            talentos_classe_n1=["escudo_reativo", "investida_subita", "ataque_fisgador"],
            talentos_classe_n2_mais=[
                "bloqueio_agressivo",
                "deslocamento_com_escudo",
                "guardiao_de_escudo",
                "bloqueio_rapido_com_escudo",
            ],
            talentos_pericia=["carregador_robusto", "olhar_intimidante", "medicina_de_batalha"],
            talentos_gerais=["vitalidade", "duro_de_matar", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["escudo", "forca", "resistencia"],
            categoria_armadura_preferida="pesada",
            armaduras_ids=["placa_peitoral", "cota_de_malha", "cota_de_escamas"],
            usa_escudo=True,
            escudos_ids=["escudo_de_aco", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["espada_longa", "martelo_de_guerra", "machado_de_batalha"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao_e_escudo",
        ),
        _conceito(
            id_conceito="guerreiro_tempestade_laminas",
            classe_id="guerreiro",
            classe_nome="Guerreiro",
            nome="Tempestade de Lâminas (Combate com Duas Armas)",
            subclasses_oficiais=[("duelista", "Duelista (Arma de Uma Mão e Mão Livre)")],
            resumo_proposta=(
                "Duelista ofensivo com duas lâminas que desfere dois golpes precisos "
                "sem penalidade de ataques múltiplos enquanto apara contra-ataques."
            ),
            sinergia_mecanica=(
                "Usa Corte Duplo (1º) com arma ágil na mão secundária, evoluindo com "
                "Aparada Dupla (4º), Agressão Vantajosa (6º) e Rajada com Duas Armas (14º)."
            ),
            prioridade_atributos=["for", "des", "con", "sab", "car", "int"],
            biografias_recomendadas=["gladiador", "marinheiro", "discipulo_marcial", "soldado"],
            pericias_prioritarias=["acrobatismo", "atletismo", "intimidacao", "diplomacia", "furtividade"],
            saber_sugerido="Saber de Esgrima",
            talentos_classe_n1=["corte_duplo", "golpe_de_exatidao", "investida_subita"],
            talentos_classe_n2_mais=["aparada_dupla", "reversao_rapida", "agressao_vantajosa"],
            talentos_pericia=["queda_do_gato", "salto_rapido", "olhar_intimidante"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["agilidade", "espada", "velocidade"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_malha", "cota_de_escamas", "couro_batido"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_longa", "espada_curta", "adaga"],
            armas_distancia_ids=["adaga", "azagaia"],
            estilo_empunhadura="duas_armas",
        ),
        _conceito(
            id_conceito="guerreiro_colosso_demolidor",
            classe_id="guerreiro",
            classe_nome="Guerreiro",
            nome="Colosso Demolidor (Arma de Duas Mãos)",
            subclasses_oficiais=[("agressor", "Agressor (Arma de Duas Mãos)")],
            resumo_proposta=(
                "Guerreiro de choque focado em golpes únicos devastadores com armas "
                "pesadas de duas mãos para quebrar armaduras e derrubar alvos."
            ),
            sinergia_mecanica=(
                "Combina Ataque Poderoso (1º) e Investida Súbita (1º) com Empurrão "
                "Brutal (2º), Assalto de Duas Mãos (4º) e Estilhaçar Defesas (6º)."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "car", "int"],
            biografias_recomendadas=["soldado", "operario", "gladiador", "mineiro"],
            pericias_prioritarias=["atletismo", "intimidacao", "sobrevivencia", "medicina"],
            saber_sugerido="Saber de Guerra",
            talentos_classe_n1=["ataque_poderoso", "investida_subita", "golpe_de_exatidao"],
            talentos_classe_n2_mais=["empurrao_brutal", "assalto_de_duas_maos", "estilhacar_defesas"],
            talentos_pericia=["lutador_titanico", "olhar_intimidante", "carregador_robusto"],
            talentos_gerais=["vitalidade", "iniciativa_incrivel", "duro_de_matar"],
            tracos_ancestralidade_afinidade=["forca", "arma", "resistencia"],
            categoria_armadura_preferida="pesada",
            armaduras_ids=["placa_peitoral", "cota_de_malha", "cota_de_escamas"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["montante", "machado_longo", "malho"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="duas_maos",
        ),
        _conceito(
            id_conceito="guerreiro_sentinela_haste",
            classe_id="guerreiro",
            classe_nome="Guerreiro",
            nome="Sentinela de Haste (Controle de Área e Alcance)",
            subclasses_oficiais=[("agressor", "Agressor (Arma de Duas Mãos)")],
            resumo_proposta=(
                "Controlador de corredores e vanguarda equipado com armas de haste "
                "para punir qualquer inimigo que tente se aproximar."
            ),
            sinergia_mecanica=(
                "Maximiza Ataque de Oportunidade a 3m com alabarda, glaive ou bisarma; "
                "escala com Investida Súbita (1º), Estocada (2º), Tombar (4º) e "
                "Postura de Estocada (12º)."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "car", "int"],
            biografias_recomendadas=["guarda", "soldado", "lavrador", "batedor"],
            pericias_prioritarias=["atletismo", "acrobatismo", "intimidacao", "sobrevivencia"],
            saber_sugerido="Saber de Tática",
            talentos_classe_n1=["investida_subita", "ataque_poderoso", "golpe_de_exatidao"],
            talentos_classe_n2_mais=["estocada", "tombar", "postura_de_estocada"],
            talentos_pericia=["lutador_titanico", "salto_rapido", "olhar_intimidante"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["alcance", "forca", "arma"],
            categoria_armadura_preferida="pesada",
            armaduras_ids=["placa_peitoral", "cota_de_malha", "cota_de_escamas"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["alabarda", "glaive", "bisarma", "ranseur"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="duas_maos",
        ),
        _conceito(
            id_conceito="guerreiro_atirador_elite",
            classe_id="guerreiro",
            classe_nome="Guerreiro",
            nome="Atirador de Elite (Arqueiro ou Besteiro)",
            subclasses_oficiais=[("arqueiro", "Arqueiro (Combate à Distância)")],
            resumo_proposta=(
                "Atirador de precisão extrema com proficiência Especialista já no 1º "
                "nível, letal tanto de longe quanto em combate à queima-roupa."
            ),
            sinergia_mecanica=(
                "Usa Tiro Certeiro (1º) para ignorar penalidade de voleio e somar +2 "
                "de dano próximo; evolui com Tiro Duplo (4º), Tiro Triplo (6º) e "
                "Tiro Debilitante (10º)."
            ),
            prioridade_atributos=["des", "for", "con", "sab", "int", "car"],
            biografias_recomendadas=["cacador", "batedor", "soldado", "cacador_de_recompensas"],
            pericias_prioritarias=["acrobatismo", "furtividade", "sobrevivencia", "atletismo", "medicina"],
            saber_sugerido="Saber de Balística",
            talentos_classe_n1=["tiro_certeiro", "golpe_de_exatidao"],
            talentos_classe_n2_mais=["tiro_de_assistencia", "tiro_duplo", "tiro_triplo", "tiro_debilitante"],
            talentos_pericia=["esgueirador_de_terreno", "rastreador_experiente", "salto_rapido"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["arco", "elfo", "agilidade", "sentidos"],
            categoria_armadura_preferida="media",
            armaduras_ids=["couro_batido", "gibao_de_peles", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "adaga"],
            armas_distancia_ids=["arco_longo", "arco_curto", "besta_pesada"],
            estilo_empunhadura="distancia",
        ),
        _conceito(
            id_conceito="guerreiro_lutador_arena",
            classe_id="guerreiro",
            classe_nome="Guerreiro",
            nome="Lutador de Arena (Mão Livre e Agarrador)",
            subclasses_oficiais=[("duelista", "Duelista (Arma de Uma Mão e Mão Livre)")],
            resumo_proposta=(
                "Combatente versátil que mantém uma mão livre para agarrar, "
                "derrubar, desarmar e aparar enquanto golpeia com espada ou machado."
            ),
            sinergia_mecanica=(
                "Combina Ataque Fisgador (1º) e Golpe de Exatidão (1º) com Atracar "
                "em Combate (2º), Aparada de Duelo (2º) e Arrebatar (4º) para "
                "neutralizar adversários no mano a mano."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "car", "int"],
            biografias_recomendadas=["gladiador", "discipulo_marcial", "cacador_de_recompensas", "soldado"],
            pericias_prioritarias=["atletismo", "acrobatismo", "intimidacao", "diplomacia"],
            saber_sugerido="Saber de Gladiador",
            talentos_classe_n1=["ataque_fisgador", "golpe_de_exatidao", "investida_subita"],
            talentos_classe_n2_mais=["atracar_em_combate", "aparada_de_duelo", "arrebatar"],
            talentos_pericia=["lutador_titanico", "escalador_de_combate", "olhar_intimidante"],
            talentos_gerais=["vitalidade", "iniciativa_incrivel", "duro_de_matar"],
            tracos_ancestralidade_afinidade=["forca", "agilidade", "combate"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_malha", "cota_de_escamas", "couro_batido"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_longa", "machado_de_batalha", "espada_bastarda"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao",
        ),

        # =====================================================================
        # 9. LADINO (6)
        # =====================================================================
        _conceito(
            id_conceito="ladino_valentao_brutal",
            classe_id="ladino",
            classe_nome="Ladino",
            nome="Valentão Brutal (Esquema Rufião)",
            subclasses_oficiais=[("rufiao", "Rufião")],
            resumo_proposta=(
                "Ladino robusto de armadura média e Força alta que aplica Ataque "
                "Furtivo com armas simples contundentes ou de haste e intimida inimigos."
            ),
            sinergia_mecanica=(
                "Esquema Rufião libera Força como atributo-chave e armadura média; "
                "combina Você É o Próximo (1º) com Surra Brutal (2º) e Golpeador "
                "Pavoroso (4º) para deixar alvos assustados e desprevenidos."
            ),
            prioridade_atributos=["for", "con", "des", "car", "sab", "int"],
            biografias_recomendadas=["prisioneiro", "criminoso", "guarda", "gladiador"],
            pericias_prioritarias=["intimidacao", "atletismo", "furtividade", "ladroagem", "acrobatismo"],
            saber_sugerido="Saber do Submundo",
            talentos_classe_n1=["voce_e_o_proximo", "esquiva_agil"],
            talentos_classe_n2_mais=["surra_brutal", "golpeador_pavoroso", "mobilidade"],
            talentos_pericia=["olhar_intimidante", "lutador_titanico", "coagir_grupo"],
            talentos_gerais=["vitalidade", "duro_de_matar", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["forca", "intimidacao", "resistencia"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_escamas", "gibao_de_peles", "couro_batido"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["maca", "lanca", "porrete"],
            armas_distancia_ids=["azagaia", "dardo"],
            estilo_empunhadura="uma_mao",
        ),
        _conceito(
            id_conceito="ladino_duelista_fanfarrao",
            classe_id="ladino",
            classe_nome="Ladino",
            nome="Duelista Fanfarrão (Esquema Malandro)",
            subclasses_oficiais=[("malandro", "Malandro")],
            resumo_proposta=(
                "Esgrimista audacioso focado em Dissimulação e Fintas rápidas para "
                "gerar Ataque Furtivo cara a cara mesmo sem precisar flanquear."
            ),
            sinergia_mecanica=(
                "Esquema Malandro com Carisma alto une Finta Dupla (1º) a Finta de "
                "Distração (2º) e Golpe Desequilibrante (2º), deixando o alvo "
                "desprevenido após uma finta bem-sucedida."
            ),
            prioridade_atributos=["des", "car", "con", "int", "sab", "for"],
            biografias_recomendadas=["charlatao", "apostador", "animador", "nobre"],
            pericias_prioritarias=["dissimulacao", "diplomacia", "acrobatismo", "intimidacao", "ladroagem"],
            saber_sugerido="Saber de Sociedade",
            talentos_classe_n1=["finta_dupla", "esquiva_agil", "voce_e_o_proximo"],
            talentos_classe_n2_mais=["finta_de_distracao", "golpe_desequilibrante", "mobilidade"],
            talentos_pericia=["mentiroso_charmoso", "distracao_prolongada", "gracejos_da_corte"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["carisma", "agilidade", "enganacao"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["rapieira", "espada_curta", "adaga"],
            armas_distancia_ids=["arco_curto", "dardo"],
            estilo_empunhadura="uma_mao",
        ),
        _conceito(
            id_conceito="ladino_sombra_silenciosa",
            classe_id="ladino",
            classe_nome="Ladino",
            nome="Sombra Silenciosa (Esquema Ladrão)",
            subclasses_oficiais=[("ladrao", "Ladrão")],
            resumo_proposta=(
                "Infiltrador clássico e letal que soma Destreza no dano corpo a corpo, "
                "desarma armadilhas e se move pelas sombras sem provocar reações."
            ),
            sinergia_mecanica=(
                "Esquema Ladrão combina Descobridor de Armadilha (1º) e Esquiva Ágil "
                "(1º) com Mobilidade (2º), Passo Leve (6º) e Infiltração Implausível "
                "(18º) com armas ágeis de acuidade."
            ),
            prioridade_atributos=["des", "con", "sab", "int", "car", "for"],
            biografias_recomendadas=["criminoso", "crianca_de_rua", "batedor", "detetive"],
            pericias_prioritarias=["furtividade", "ladroagem", "acrobatismo", "sobrevivencia", "sociedade"],
            saber_sugerido="Saber do Submundo",
            talentos_classe_n1=["esquiva_agil", "descobridor_de_armadilha"],
            talentos_classe_n2_mais=["mobilidade", "saque_rapido", "passo_leve"],
            talentos_pericia=["queda_do_gato", "furto_subito", "esgueirador_de_terreno"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "perspicacia_astuta"],
            tracos_ancestralidade_afinidade=["furtividade", "agilidade", "sombra", "noite"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "rapieira", "adaga"],
            armas_distancia_ids=["arco_curto", "dardo"],
            estilo_empunhadura="duas_armas",
        ),
        _conceito(
            id_conceito="ladino_sabotador_venenoso",
            classe_id="ladino",
            classe_nome="Ladino",
            nome="Sabotador Venenoso (Atirador Furtivo)",
            subclasses_oficiais=[("ladrao", "Ladrão"), ("malandro", "Malandro")],
            resumo_proposta=(
                "Emboscador à distância que dispara das sombras com arcos curtos ou "
                "adagas arremessadas, sabotando itens e envenenando alvos."
            ),
            sinergia_mecanica=(
                "Une Esquiva Ágil (1º) e Descobridor de Armadilha (1º) a Envenenar "
                "Arma (4º), Sabotagem (4º) e Envenenar Arma Aprimorado (8º) para "
                "drenar inimigos à distância."
            ),
            prioridade_atributos=["des", "int", "con", "sab", "car", "for"],
            biografias_recomendadas=["criminoso", "batedor", "cacador", "herbalista"],
            pericias_prioritarias=["furtividade", "ladroagem", "manufatura", "acrobatismo", "natureza"],
            saber_sugerido="Saber de Venenos",
            talentos_classe_n1=["esquiva_agil", "descobridor_de_armadilha", "finta_dupla"],
            talentos_classe_n2_mais=["envenenar_arma", "sabotagem", "envenenar_arma_aprimorado"],
            talentos_pericia=["esgueirador_de_terreno", "contrabandista_experiente", "manufatura_alquimica"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["veneno", "furtividade", "arco", "agilidade"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "adaga"],
            armas_distancia_ids=["arco_curto", "adaga", "zarabatana"],
            estilo_empunhadura="distancia",
        ),
        _conceito(
            id_conceito="ladino_acrobata_explorador",
            classe_id="ladino",
            classe_nome="Ladino",
            nome="Explorador de Ruínas (Caçador de Armadilhas)",
            subclasses_oficiais=[("ladrao", "Ladrão")],
            resumo_proposta=(
                "Especialista em masmorras e relíquias que detecta e desativa "
                "armadilhas complexas antes que o grupo caia em emboscadas."
            ),
            sinergia_mecanica=(
                "Prioriza Descobridor de Armadilha (1º) com Sabedoria e Inteligência "
                "altas para Percepção e Ladroagem; evolui com Mobilidade (2º), Aviso "
                "do Batedor (4º) e Perseguição Reativa (4º)."
            ),
            prioridade_atributos=["des", "sab", "int", "con", "car", "for"],
            biografias_recomendadas=["batedor", "detetive", "funileiro", "cacador_de_recompensas"],
            pericias_prioritarias=["ladroagem", "acrobatismo", "furtividade", "atletismo", "sobrevivencia"],
            saber_sugerido="Saber de Arquitetura",
            talentos_classe_n1=["descobridor_de_armadilha", "esquiva_agil"],
            talentos_classe_n2_mais=["mobilidade", "aviso_do_batedor", "perseguicao_reativa"],
            talentos_pericia=["queda_do_gato", "escalador_de_combate", "salto_rapido"],
            talentos_gerais=["perspicacia_astuta", "veloz", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["armadilha", "sentidos", "agilidade", "masmorra"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "rapieira", "adaga"],
            armas_distancia_ids=["besta_de_mao", "arco_curto", "dardo"],
            estilo_empunhadura="uma_mao",
        ),
        _conceito(
            id_conceito="ladino_infiltrador_arcano",
            classe_id="ladino",
            classe_nome="Ladino",
            nome="Infiltrador Místico (Espião e Impostor Social)",
            subclasses_oficiais=[("malandro", "Malandro")],
            resumo_proposta=(
                "Agente de intriga com Carisma como atributo principal que domina "
                "salões nobres, disfarces e truques místicos de infiltração."
            ),
            sinergia_mecanica=(
                "Assume Carisma como atributo-chave no Esquema Malandro, unindo "
                "Finta Dupla (1º) e broquel a Mágica Menor (2º) e Avaliação de "
                "Batalha (4º) para ler fraquezas inimigas."
            ),
            prioridade_atributos=["car", "des", "int", "sab", "con", "for"],
            biografias_recomendadas=["emissario", "nobre", "charlatao", "advogado"],
            pericias_prioritarias=["dissimulacao", "diplomacia", "sociedade", "ocultismo", "furtividade"],
            saber_sugerido="Saber de Espionagem",
            talentos_classe_n1=["finta_dupla", "voce_e_o_proximo", "esquiva_agil"],
            talentos_classe_n2_mais=["magica_menor", "finta_de_distracao", "avaliacao_de_batalha"],
            talentos_pericia=["gracejos_da_corte", "mentiroso_charmoso", "poliglota"],
            talentos_gerais=["iniciativa_incrivel", "perspicacia_astuta", "veloz"],
            tracos_ancestralidade_afinidade=["carisma", "ilusao", "diplomacia", "enganacao"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro", "couro_batido", "armadura_acolchoada"],
            usa_escudo=True,
            escudos_ids=["broquel"],
            armas_corpo_a_corpo_ids=["rapieira", "adaga", "espada_curta"],
            armas_distancia_ids=["besta_de_mao", "dardo"],
            estilo_empunhadura="uma_mao_e_escudo",
        ),

        # =====================================================================
        # 10. MAGO (6)
        # =====================================================================
        _conceito(
            id_conceito="mago_evocador_artilharia",
            classe_id="mago",
            classe_nome="Mago",
            nome="Evocador de Artilharia (Dano em Área)",
            subclasses_oficiais=[("evocacao", "Evocação")],
            resumo_proposta=(
                "Artilheiro arcano especialista em explosões elementais e conversão "
                "de espaços menores em conjurações de maior impacto."
            ),
            sinergia_mecanica=(
                "Escola de Evocação (raio de força) + Tese Mescla de Magia para "
                "fundir espaços em círculos altos; combina Ampliar Magia (1º) com "
                "Conjuração Consistente (6º) e Energia Avassaladora (10º)."
            ),
            prioridade_atributos=["int", "des", "con", "sab", "car", "for"],
            biografias_recomendadas=["estudioso", "funileiro", "vidente", "acolito"],
            pericias_prioritarias=["arcanismo", "ocultismo", "sociedade", "natureza", "manufatura"],
            saber_sugerido="Saber Arcano",
            talentos_classe_n1=["ampliar_magia", "magia_de_alcance"],
            talentos_classe_n2_mais=["conjuracao_consistente", "energia_avassaladora", "conjuracao_acelerada"],
            talentos_pericia=["sentido_arcano", "reconhecer_magia", "identificacao_rapida"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["arcano", "fogo", "inteligencia", "magia"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga"],
            armas_distancia_ids=["besta_leve"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["fogo", "eletricidade", "frio", "forca", "evocacao"],
                escolas_prioritarias=["evocacao"],
                truques_prioritarios=["produzir_chama", "arco_eletrico", "raio_de_gelo", "escudo_mistico", "detectar_magia"],
                magias_nivel_1_prioritarias=["maos_flamejantes", "misseis_magicos", "toque_chocante", "armadura_mistica", "golpe_certo"],
            ),
            tese_arcana_id="mescla_de_magia",
        ),
        _conceito(
            id_conceito="mago_duelista_contramagica",
            classe_id="mago",
            classe_nome="Mago",
            nome="Duelista de Contramágica (Especialista em Abjuração)",
            subclasses_oficiais=[("abjuracao", "Abjuração")],
            resumo_proposta=(
                "Protetor arcano que ergue barreiras defensivas para o grupo e "
                "neutraliza conjuradores inimigos com contramágicas precisas."
            ),
            sinergia_mecanica=(
                "Escola de Abjuração + Tese Substituição de Magia para adaptar a "
                "defesa certa em 10 minutos; une Contramágica (1º) a Penetração de "
                "Magia (6º), Trespassar Contramágica (12º) e Refletir Magia (14º)."
            ),
            prioridade_atributos=["int", "con", "des", "sab", "car", "for"],
            biografias_recomendadas=["estudioso", "advogado", "detetive", "guarda"],
            pericias_prioritarias=["arcanismo", "ocultismo", "religiao", "natureza", "sociedade"],
            saber_sugerido="Saber Arcano",
            talentos_classe_n1=["contramagica", "magia_de_alcance"],
            talentos_classe_n2_mais=["penetracao_de_magia", "trespassar_contramagica", "refletir_magia"],
            talentos_pericia=["reconhecer_magia", "identificacao_rapida", "sentido_arcano"],
            talentos_gerais=["iniciativa_incrivel", "vitalidade", "duro_de_matar"],
            tracos_ancestralidade_afinidade=["abjuracao", "protecao", "arcano", "inteligencia"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga"],
            armas_distancia_ids=["besta_leve"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["abjuracao", "forca", "protecao"],
                escolas_prioritarias=["abjuracao", "evocacao"],
                truques_prioritarios=["escudo_mistico", "detectar_magia", "ler_aura", "projetil_telecinetico", "luz"],
                magias_nivel_1_prioritarias=["armadura_mistica", "alarme", "trancar", "misseis_magicos", "queda_suave"],
            ),
            tese_arcana_id="substituicao_de_magia",
        ),
        _conceito(
            id_conceito="mago_ilusionista_enganador",
            classe_id="mago",
            classe_nome="Mago",
            nome="Ilusionista e Enganador (Controle Tático)",
            subclasses_oficiais=[("ilusao", "Ilusão")],
            resumo_proposta=(
                "Estrategista arcano que divide o campo de batalha com paredes "
                "falsas, duplicatas e sons enganosos sem depender de dano direto."
            ),
            sinergia_mecanica=(
                "Escola de Ilusão + Tese Sintonização com Familiar Aprimorada (ganha "
                "Familiar bônus); combina Ignorar Materiais (1º) com Ocultar Magia "
                "(2º) e Magia Silenciosa (4º) para conjurar escondido."
            ),
            prioridade_atributos=["int", "des", "con", "car", "sab", "for"],
            biografias_recomendadas=["charlatao", "artista", "detetive", "estudioso"],
            pericias_prioritarias=["arcanismo", "dissimulacao", "furtividade", "ocultismo", "sociedade"],
            saber_sugerido="Saber de Ilusões",
            talentos_classe_n1=["magia_de_alcance", "ignorar_materiais", "familiar"],
            talentos_classe_n2_mais=["ocultar_magia", "magia_silenciosa", "familiar_melhorado"],
            talentos_pericia=["sentido_arcano", "distracao_prolongada", "identificacao_rapida"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "perspicacia_astuta"],
            tracos_ancestralidade_afinidade=["ilusao", "fada", "sombra", "arcano"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "cajado"],
            armas_distancia_ids=["besta_leve"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["ilusao", "mental", "encantamento"],
                escolas_prioritarias=["ilusao", "encantamento"],
                truques_prioritarios=["som_fantasma", "luzes_dancantes", "prestidigitacao", "mao_mistica", "detectar_magia"],
                magias_nivel_1_prioritarias=["objeto_ilusorio", "disfarce_ilusorio", "leque_de_cores", "item_de_fachada", "ventriloquismo"],
            ),
            tese_arcana_id="sintonizacao_com_familiar_aprimorada",
        ),
        _conceito(
            id_conceito="mago_invocador_necromante",
            classe_id="mago",
            classe_nome="Mago",
            nome="Invocador / Necromante (Exército de Lacaios)",
            subclasses_oficiais=[("conjuracao", "Conjuração"), ("necromancia", "Necromancia")],
            resumo_proposta=(
                "Mestre da invocação que traz criaturas elementais, constructos ou "
                "forças necromânticas para controlar o ritmo do campo de batalha."
            ),
            sinergia_mecanica=(
                "Escola de Conjuração ou Necromancia + Tese Sintonização com Familiar "
                "Aprimorada; evolui com Familiar Melhorado (2º), Conjuração Consistente "
                "(6º) e Concentração Sem Esforço (16º) para sustentar invocações."
            ),
            prioridade_atributos=["int", "con", "des", "sab", "car", "for"],
            biografias_recomendadas=["eremita", "estudioso", "acolito", "vidente"],
            pericias_prioritarias=["arcanismo", "ocultismo", "natureza", "religiao", "sociedade"],
            saber_sugerido="Saber Planar",
            talentos_classe_n1=["magia_de_alcance", "ampliar_magia", "familiar"],
            talentos_classe_n2_mais=["familiar_melhorado", "conjuracao_consistente", "concentracao_sem_esforco"],
            talentos_pericia=["sentido_arcano", "identificar_estranhezas", "reconhecer_magia"],
            talentos_gerais=["vitalidade", "duro_de_matar", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["invocacao", "morte", "arcano", "inteligencia"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga"],
            armas_distancia_ids=["besta_leve"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["conjuracao", "necromancia", "negativo"],
                escolas_prioritarias=["conjuracao", "necromancia"],
                truques_prioritarios=["toque_gelido", "mao_mistica", "escudo_mistico", "detectar_magia", "projetil_telecinetico"],
                magias_nivel_1_prioritarias=["convocar_animal", "convocar_constructo", "servo_invisivel", "raio_de_enfraquecimento", "medo"],
            ),
            tese_arcana_id="sintonizacao_com_familiar_aprimorada",
        ),
        _conceito(
            id_conceito="mago_arquimago_enciclopedico",
            classe_id="mago",
            classe_nome="Mago",
            nome="Arquimago Enciclopédico (Versatilidade Total)",
            subclasses_oficiais=[("universalista", "Universalista")],
            resumo_proposta=(
                "Mago universalista sem restrição de escola que drena seu item "
                "vinculado por círculo e troca magias preparadas durante o dia."
            ),
            sinergia_mecanica=(
                "Escola Universalista (ganha Mão do Aprendiz gratuita) + Tese "
                "Substituição de Magia para trocar preparações em 10 minutos; escala "
                "com Expansão de Truque Mágico (2º), Versatilidade Universal (8º) e Rearranjar Magia (16º)."
            ),
            prioridade_atributos=["int", "des", "con", "sab", "car", "for"],
            biografias_recomendadas=["estudioso", "advogado", "detetive", "funileiro"],
            pericias_prioritarias=["arcanismo", "sociedade", "ocultismo", "natureza", "religiao"],
            saber_sugerido="Saber Acadêmico",
            talentos_classe_n1=["mao_do_aprendiz", "contramagica", "magia_de_alcance"],
            talentos_classe_n2_mais=["expansao_de_truque_magico", "versatilidade_universal", "rearranjar_magia"],
            talentos_pericia=["poliglota", "reconhecer_magia", "identificacao_rapida"],
            talentos_gerais=["perspicacia_astuta", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["saber", "inteligencia", "arcano"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga"],
            armas_distancia_ids=["besta_leve"],
            estilo_empunhadura="distancia",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["forca", "adivinhacao", "transmutacao", "abjuracao"],
                escolas_prioritarias=["evocacao", "abjuracao", "transmutacao", "adivinhacao"],
                truques_prioritarios=["detectar_magia", "escudo_mistico", "ler_aura", "prestidigitacao", "arco_eletrico"],
                magias_nivel_1_prioritarias=["misseis_magicos", "armadura_mistica", "passos_velozes", "queda_suave", "alarme"],
            ),
            tese_arcana_id="substituicao_de_magia",
        ),
        _conceito(
            id_conceito="mago_transmutador_batalha",
            classe_id="mago",
            classe_nome="Mago",
            nome="Transmutador de Batalha (Mestre de Metamagia e Forma)",
            subclasses_oficiais=[("transmutacao", "Transmutação"), ("adivinhacao", "Adivinhação")],
            resumo_proposta=(
                "Mago tático que altera propriedades físicas de armas e aliados, "
                "acelera movimentos e adapta metamagias diariamente em combate."
            ),
            sinergia_mecanica=(
                "Escola de Transmutação ou Adivinhação + Tese Experimentação "
                "Metamágica (ganha Magia de Alcance no 1º nível e flexibilidade "
                "metamágica no 4º); evolui com Magia Residual em Arma (4º) e Foco Vinculado (4º)."
            ),
            prioridade_atributos=["int", "des", "con", "for", "sab", "car"],
            biografias_recomendadas=["artesao", "funileiro", "estudioso", "soldado"],
            pericias_prioritarias=["arcanismo", "manufatura", "acrobatismo", "atletismo", "natureza"],
            saber_sugerido="Saber de Engenharia",
            talentos_classe_n1=["magia_de_alcance", "ampliar_magia", "ignorar_materiais"],
            talentos_classe_n2_mais=["magia_residual_em_arma", "foco_vinculado", "magia_de_escola_avancada"],
            talentos_pericia=["sentido_arcano", "reparo_rapido", "reconhecer_magia"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["transmutacao", "velocidade", "engenho", "arcano"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga", "clava"],
            armas_distancia_ids=["besta_leve"],
            estilo_empunhadura="duas_maos",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["transmutacao", "adivinhacao", "metamorfose"],
                escolas_prioritarias=["transmutacao", "adivinhacao"],
                truques_prioritarios=["escudo_mistico", "projetil_telecinetico", "mao_mistica", "arco_eletrico", "detectar_magia"],
                magias_nivel_1_prioritarias=["arma_magica", "passos_velozes", "golpe_certo", "salto", "carga_de_formiga"],
            ),
            tese_arcana_id="experimentacao_metamagica",
        ),

        # =====================================================================
        # 11. MONGE (6)
        # =====================================================================
        _conceito(
            id_conceito="monge_artista_posturas",
            classe_id="monge",
            classe_nome="Monge",
            nome="Artista das Posturas (Golpeador Ágil)",
            subclasses_oficiais=[("monge_da_garca", "Monge da Garça")],
            resumo_proposta=(
                "Lutador acrobático e veloz que combina Rajada de Golpes com "
                "posturas ágeis para entrar, golpear e flanquear com mobilidade máxima."
            ),
            sinergia_mecanica=(
                "Destreza alta com Postura do Tigre (1º), Postura do Lobo (1º) ou "
                "Postura da Garça (1º); evolui com Folha Dançante (2º), Chute "
                "Voador (4º) e Corte do Tigre / Arrasto do Lobo (6º)."
            ),
            prioridade_atributos=["des", "for", "con", "sab", "car", "int"],
            biografias_recomendadas=["acrobata", "discipulo_marcial", "batedor", "crianca_de_rua"],
            pericias_prioritarias=["acrobatismo", "atletismo", "furtividade", "diplomacia", "medicina"],
            saber_sugerido="Saber de Artes Marciais",
            talentos_classe_n1=["postura_do_tigre", "postura_do_lobo", "postura_da_garca"],
            talentos_classe_n2_mais=["folha_dancante", "chute_voador", "corte_do_tigre", "arrasto_do_lobo"],
            talentos_pericia=["queda_do_gato", "equilibrio_estavel", "salto_rapido"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["agilidade", "velocidade", "desarmado"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=[],
            armas_distancia_ids=["dardo"],
            estilo_empunhadura="desarmado",
        ),
        _conceito(
            id_conceito="monge_muralha_pedra",
            classe_id="monge",
            classe_nome="Monge",
            nome="Muralha de Pedra (Tanque Sem Armadura)",
            subclasses_oficiais=[("monge_da_garca", "Monge da Garça"), ("monge_do_ki", "Monge do Ki")],
            resumo_proposta=(
                "Vanguarda inabalável que atinge CA altíssima sem usar armadura "
                "e segura inimigos na linha de frente com golpes atordoantes."
            ),
            sinergia_mecanica=(
                "Postura da Montanha (1º) soma bônus de item à CA sem armadura; "
                "escala com Punho Atordoante (2º), Impedir Movimento (4º) e "
                "Fortaleza da Montanha (6º) para sustentar a linha de frente."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "car", "int"],
            biografias_recomendadas=["discipulo_marcial", "guarda", "operario", "gladiador"],
            pericias_prioritarias=["atletismo", "intimidacao", "medicina", "sobrevivencia", "acrobatismo"],
            saber_sugerido="Saber de Fortaleza",
            talentos_classe_n1=["postura_da_montanha", "postura_da_garca"],
            talentos_classe_n2_mais=["punho_atordoante", "impedir_movimento", "fortaleza_da_montanha"],
            talentos_pericia=["lutador_titanico", "carregador_robusto", "olhar_intimidante"],
            talentos_gerais=["vitalidade", "duro_de_matar", "recuperacao_rapida"],
            tracos_ancestralidade_afinidade=["terra", "pedra", "resistencia", "forca"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=[],
            armas_distancia_ids=["dardo"],
            estilo_empunhadura="desarmado",
        ),
        _conceito(
            id_conceito="monge_mestre_ki_mistico",
            classe_id="monge",
            classe_nome="Monge",
            nome="Mestre do Ki Místico (Poderes Espirituais)",
            subclasses_oficiais=[("monge_do_ki", "Monge do Ki")],
            resumo_proposta=(
                "Asceta disciplinado que desperta magia de foco ocultista para "
                "potencializar ataques desarmados, curar-se e disparar rajadas de ki."
            ),
            sinergia_mecanica=(
                "Sabedoria elevada com Golpe de Ki (1º) ou Disparada de Ki (1º), "
                "evoluindo com Punho Elemental (2º), Integridade Corporal (4º) e "
                "Rajada de Ki (6º) para dano energético e autossuficiência."
            ),
            prioridade_atributos=["des", "sab", "con", "for", "car", "int"],
            biografias_recomendadas=["eremita", "acolito", "discipulo_marcial", "vidente"],
            pericias_prioritarias=["acrobatismo", "religiao", "ocultismo", "medicina", "atletismo"],
            saber_sugerido="Saber Monástico",
            talentos_classe_n1=["golpe_de_ki", "disparada_de_ki"],
            talentos_classe_n2_mais=["punho_elemental", "integridade_corporal", "rajada_de_ki"],
            talentos_pericia=["medicina_de_batalha", "equilibrio_estavel", "queda_do_gato"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["sabedoria", "espirito", "ki", "agilidade"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=[],
            armas_distancia_ids=["dardo"],
            estilo_empunhadura="desarmado",
        ),
        _conceito(
            id_conceito="monge_guerreiro_armas_monasticas",
            classe_id="monge",
            classe_nome="Monge",
            nome="Guerreiro das Armas Monásticas (Kensei / Arqueiro Zen)",
            subclasses_oficiais=[("monge_do_ki", "Monge do Ki"), ("monge_da_garca", "Monge da Garça")],
            resumo_proposta=(
                "Mestre de armas tradicionais de monastério capaz de aplicar Rajada "
                "de Golpes e técnicas monásticas usando espadas de templo, bos e shurikens."
            ),
            sinergia_mecanica=(
                "Arsenal Monástico (1º) libera armas com traço monge (bo, espada de "
                "templo, kama, sai, shuriken) com escala automática de proficiência; "
                "combina com Defletir Projétil (4º) e Rajada de Manobras (4º)."
            ),
            prioridade_atributos=["des", "for", "con", "sab", "car", "int"],
            biografias_recomendadas=["discipulo_marcial", "soldado", "guarda", "artesao"],
            pericias_prioritarias=["acrobatismo", "atletismo", "religiao", "furtividade", "medicina"],
            saber_sugerido="Saber de Armas Marciais",
            talentos_classe_n1=["arsenal_monastico", "golpe_de_ki"],
            talentos_classe_n2_mais=["foco_em_pugilato", "defletir_projetil", "rajada_de_manobras"],
            talentos_pericia=["queda_do_gato", "equilibrio_estavel", "salto_rapido"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["arma", "agilidade", "disciplina"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["bo", "espada_de_templo", "kama", "sai", "katar_adaga_de_soco"],
            armas_distancia_ids=["shuriken", "dardo"],
            estilo_empunhadura="uma_mao",
        ),
        _conceito(
            id_conceito="monge_mestre_arremessos",
            classe_id="monge",
            classe_nome="Monge",
            nome="Mestre dos Arremessos (Agarrador e Controlador)",
            subclasses_oficiais=[("monge_do_ki", "Monge do Ki"), ("monge_da_garca", "Monge da Garça")],
            resumo_proposta=(
                "Especialista em combate físico próximo focado em agarrar, derrubar, "
                "arremessar oponentes contra outros alvos e controlar posicionamento."
            ),
            sinergia_mecanica=(
                "Força alta com Postura do Dragão (1º) ou Postura da Montanha (1º), "
                "escalando com Agarrão Esmagador (2º), Rajada de Manobras (4º) e "
                "Arremesso Giratório (6º)."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "car", "int"],
            biografias_recomendadas=["discipulo_marcial", "gladiador", "operario", "marinheiro"],
            pericias_prioritarias=["atletismo", "acrobatismo", "intimidacao", "medicina", "sobrevivencia"],
            saber_sugerido="Saber de Luta Livre",
            talentos_classe_n1=["postura_do_dragao", "postura_da_montanha"],
            talentos_classe_n2_mais=["agarrao_esmagador", "rajada_de_manobras", "arremesso_giratorio"],
            talentos_pericia=["lutador_titanico", "escalador_de_combate", "olhar_intimidante"],
            talentos_gerais=["vitalidade", "duro_de_matar", "veloz"],
            tracos_ancestralidade_afinidade=["forca", "combate", "resistencia"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=[],
            armas_distancia_ids=["dardo"],
            estilo_empunhadura="desarmado",
        ),
        _conceito(
            id_conceito="monge_dancarino_garca",
            classe_id="monge",
            classe_nome="Monge",
            nome="Dançarino da Garça (Esquiva Aérea e Contra-Ataque)",
            subclasses_oficiais=[("monge_da_garca", "Monge da Garça")],
            resumo_proposta=(
                "Acrobata marcial de defesa fluida que eleva sua CA na Postura da "
                "Garça, salta sobre obstáculos e contra-ataca com golpes de asa."
            ),
            sinergia_mecanica=(
                "Prioriza Postura da Garça (1º) para +1 de bônus de circunstância na "
                "CA e saltos aprimorados, escalando com Folha Dançante (2º), Chute "
                "Voador (4º) e Alvoroço da Garça (6º) como reação de contra-ataque."
            ),
            prioridade_atributos=["des", "sab", "con", "for", "car", "int"],
            biografias_recomendadas=["acrobata", "discipulo_marcial", "artista", "nomade"],
            pericias_prioritarias=["acrobatismo", "atletismo", "performance", "medicina", "furtividade"],
            saber_sugerido="Saber de Artes Marciais",
            talentos_classe_n1=["postura_da_garca", "disparada_de_ki"],
            talentos_classe_n2_mais=["folha_dancante", "chute_voador", "alvoroco_da_garca"],
            talentos_pericia=["queda_do_gato", "equilibrio_estavel", "salto_rapido"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["agilidade", "velocidade", "ar", "equilibrio"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador", "nenhuma_armadura"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=[],
            armas_distancia_ids=["dardo"],
            estilo_empunhadura="desarmado",
        ),

        # =====================================================================
        # 12. PATRULHEIRO (6)
        # =====================================================================
        _conceito(
            id_conceito="patrulheiro_metralhadora_flechas",
            classe_id="patrulheiro",
            classe_nome="Patrulheiro",
            nome="Metralhadora de Flechas (Arqueiro de Rajada)",
            subclasses_oficiais=[("rajada", "Rajada")],
            resumo_proposta=(
                "Arqueiro veloz que marca uma presa e reduz drasticamente a "
                "penalidade de ataques múltiplos para disparar saraivadas de flechas."
            ),
            sinergia_mecanica=(
                "Excelência Rajada somada a Tiro à Caça (1º) para dois disparos por "
                "uma ação; evolui com Mira do Caçador (2º), Tiro Longo (4º), Tiro "
                "Penetrante (10º) e Saraivada Impossível (18º)."
            ),
            prioridade_atributos=["des", "for", "con", "sab", "int", "car"],
            biografias_recomendadas=["cacador", "batedor", "soldado", "nomade"],
            pericias_prioritarias=["natureza", "sobrevivencia", "furtividade", "acrobatismo", "atletismo"],
            saber_sugerido="Saber de Caça",
            talentos_classe_n1=["tiro_a_caca", "cacador_de_monstros"],
            talentos_classe_n2_mais=["mira_do_cacador", "tiro_longo", "tiro_penetrante", "saraivada_impossivel"],
            talentos_pericia=["esgueirador_de_terreno", "rastreador_experiente", "forrageador"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["arco", "elfo", "agilidade", "velocidade"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "adaga"],
            armas_distancia_ids=["arco_longo", "arco_curto"],
            estilo_empunhadura="distancia",
        ),
        _conceito(
            id_conceito="patrulheiro_atirador_precisao",
            classe_id="patrulheiro",
            classe_nome="Patrulheiro",
            nome="Atirador de Precisão (Sniper de Um Tiro)",
            subclasses_oficiais=[("precisao", "Precisão")],
            resumo_proposta=(
                "Franco-atirador furtivo de besta pesada ou arco longo focado em "
                "maximizar o dano letal do primeiro disparo contra sua presa."
            ),
            sinergia_mecanica=(
                "Excelência Precisão (+1d8 de precisão) com Ás com Besta (1º) e "
                "Tiro à Caça (1º), evoluindo para Recarga em Movimento (4º) e "
                "Camuflagem (10º) para atirar sem sair das sombras."
            ),
            prioridade_atributos=["des", "sab", "con", "for", "int", "car"],
            biografias_recomendadas=["cacador", "cacador_de_recompensas", "batedor", "eremita"],
            pericias_prioritarias=["furtividade", "natureza", "sobrevivencia", "acrobatismo", "medicina"],
            saber_sugerido="Saber de Emboscada",
            talentos_classe_n1=["as_com_besta", "tiro_a_caca", "cacador_de_monstros"],
            talentos_classe_n2_mais=["mira_do_cacador", "recarga_em_movimento", "camuflagem"],
            talentos_pericia=["esgueirador_de_terreno", "rastreador_experiente", "forrageador"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "perspicacia_astuta"],
            tracos_ancestralidade_afinidade=["furtividade", "sentidos", "arco", "elfo"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "adaga"],
            armas_distancia_ids=["besta_pesada", "arco_longo", "besta_leve"],
            estilo_empunhadura="distancia",
        ),
        _conceito(
            id_conceito="patrulheiro_tormenta_duas_laminas",
            classe_id="patrulheiro",
            classe_nome="Patrulheiro",
            nome="Tormenta de Duas Lâminas (Combate Corpo a Corpo)",
            subclasses_oficiais=[("rajada", "Rajada"), ("precisao", "Precisão")],
            resumo_proposta=(
                "Combatente agressivo com duas armas que ataca e apara em ritmo "
                "acelerado contra a presa marcada no corpo a corpo."
            ),
            sinergia_mecanica=(
                "Combina Abate Duplo (1º) com Saque Rápido (2º), Aparada Dupla (4º) "
                "para ganhar bônus na CA e Golpe Escaramuçador (6º) para manter pressão."
            ),
            prioridade_atributos=["for", "des", "con", "sab", "int", "car"],
            biografias_recomendadas=["cacador", "soldado", "marinheiro", "mineiro"],
            pericias_prioritarias=["atletismo", "natureza", "sobrevivencia", "acrobatismo", "intimidacao"],
            saber_sugerido="Saber de Sobrevivência",
            talentos_classe_n1=["abate_duplo", "cacador_de_monstros"],
            talentos_classe_n2_mais=["saque_rapido", "aparada_dupla", "golpe_escaramucador"],
            talentos_pericia=["escalador_de_combate", "rastreador_experiente", "salto_rapido"],
            talentos_gerais=["vitalidade", "veloz", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["forca", "agilidade", "selvagem"],
            categoria_armadura_preferida="media",
            armaduras_ids=["gibao_de_peles", "cota_de_escamas", "couro_batido"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_longa", "espada_curta", "machadinha"],
            armas_distancia_ids=["azagaia", "arco_curto"],
            estilo_empunhadura="duas_armas",
        ),
        _conceito(
            id_conceito="patrulheiro_mestre_feras",
            classe_id="patrulheiro",
            classe_nome="Patrulheiro",
            nome="Mestre das Feras (Combate Sincronizado)",
            subclasses_oficiais=[("precisao", "Precisão"), ("rajada", "Rajada"), ("despiste", "Despiste")],
            resumo_proposta=(
                "Caçador em sintonia com um companheiro animal que compartilha os "
                "bônus de Caçar Presa e da Vantagem do Caçador em equipe."
            ),
            sinergia_mecanica=(
                "Companheiro Animal (1º) recebe sua Excelência de Caçador e escala "
                "com Empatia Selvagem (2º), Brado do Companheiro (4º), Companheiro "
                "Animal Maduro (6º), Companheiro Incrível (10º) e Lado a Lado (12º)."
            ),
            prioridade_atributos=["des", "sab", "con", "for", "car", "int"],
            biografias_recomendadas=["encantador_de_animais", "cacador", "herbalista", "batedor"],
            pericias_prioritarias=["natureza", "sobrevivencia", "medicina", "diplomacia", "acrobatismo"],
            saber_sugerido="Saber de Fauna",
            talentos_classe_n1=["companheiro_animal", "tiro_a_caca", "abate_duplo"],
            talentos_classe_n2_mais=[
                "empatia_selvagem",
                "brado_do_companheiro",
                "companheiro_animal_maduro",
                "companheiro_incrivel",
                "lado_a_lado",
            ],
            talentos_pericia=["treinar_animal", "medicina_natural", "rastreador_experiente"],
            talentos_gerais=["cavalgar", "vitalidade", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["animal", "natureza", "floresta"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["lanca", "espada_curta", "adaga"],
            armas_distancia_ids=["arco_curto", "funda"],
            estilo_empunhadura="distancia",
        ),
        _conceito(
            id_conceito="patrulheiro_mestre_arapucas",
            classe_id="patrulheiro",
            classe_nome="Patrulheiro",
            nome="Mestre das Arapucas e Caçador de Monstros (Tático)",
            subclasses_oficiais=[("despiste", "Despiste")],
            resumo_proposta=(
                "Caçador engenhoso que analisa monstros para conceder bônus ao grupo "
                "e arma arapucas táticas rapidamente no campo de batalha."
            ),
            sinergia_mecanica=(
                "Excelência Despiste (bônus em Manufatura, Natureza e Sobrevivência "
                "contra a presa) unida a Caçador de Monstros (1º), Guardião Contra "
                "Monstros (2º), Especialista em Arapuca (4º) e Arapucas Rápidas (6º)."
            ),
            prioridade_atributos=["des", "int", "sab", "con", "for", "car"],
            biografias_recomendadas=["cacador", "funileiro", "batedor", "estudioso"],
            pericias_prioritarias=["manufatura", "natureza", "sobrevivencia", "furtividade", "ladroagem"],
            saber_sugerido="Saber de Monstros",
            talentos_classe_n1=["cacador_de_monstros", "tiro_a_caca"],
            talentos_classe_n2_mais=["guardiao_contra_monstros", "especialista_em_arapuca", "arapucas_rapidas"],
            talentos_pericia=["manufatura_de_arapuca", "rastreador_experiente", "identificacao_rapida"],
            talentos_gerais=["perspicacia_astuta", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["engenho", "saber", "armadilha", "natureza"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "adaga"],
            armas_distancia_ids=["arco_curto", "besta_leve"],
            estilo_empunhadura="distancia",
        ),
        _conceito(
            id_conceito="patrulheiro_cacador_colossos",
            classe_id="patrulheiro",
            classe_nome="Patrulheiro",
            nome="Caçador de Colossos (Arma Pesada de Duas Mãos)",
            subclasses_oficiais=[("precisao", "Precisão")],
            resumo_proposta=(
                "Matador de feras gigantes que empunha armas pesadas de duas mãos "
                "para somar o dado extra de Precisão a golpes únicos devastadores."
            ),
            sinergia_mecanica=(
                "Foca em Força 18 com Excelência Precisão (+1d8 no primeiro acerto) "
                "e Caçador de Monstros (1º), evoluindo com Guardião Contra Monstros "
                "(2º), Inimigo Predileto (4º) e Interromper Presa (4º)."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "int", "car"],
            biografias_recomendadas=["cacador", "cacador_de_recompensas", "soldado", "operario"],
            pericias_prioritarias=["atletismo", "natureza", "sobrevivencia", "intimidacao", "medicina"],
            saber_sugerido="Saber de Gigantes",
            talentos_classe_n1=["cacador_de_monstros", "companheiro_animal"],
            talentos_classe_n2_mais=["guardiao_contra_monstros", "inimigo_predileto", "interromper_presa"],
            talentos_pericia=["lutador_titanico", "rastreador_experiente", "olhar_intimidante"],
            talentos_gerais=["vitalidade", "duro_de_matar", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["forca", "arma", "resistencia", "selvagem"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_escamas", "gibao_de_peles", "couro_batido"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["machado_longo", "montante", "alabarda"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="duas_maos",
        ),
    ]


def gerar_estrutura_conceitos() -> dict[str, Any]:
    """Monta o dicionário completo de `dados/conceitos_subclasses.json`."""
    conceitos = construir_conceitos()
    indice_por_classe: dict[str, list[str]] = {}
    for c in conceitos:
        indice_por_classe.setdefault(c["classe_id"], []).append(c["id"])

    return {
        "meta": {
            "titulo": "Pathfinder 2ª Edição — Catálogo de Conceitos e Subclasses Procedurais",
            "versao": "2.1",
            "total_classes_cobertas": len(indice_por_classe),
            "total_conceitos": len(conceitos),
            "descricao": (
                "Catálogo com 72 conceitos temáticos (6 por classe) cobrindo todas as 12 classes básicas. "
                "O jogador escolhe a Classe e o Conceito, e o motor seleciona proceduralmente "
                "a Subclasse Oficial do PF2E mais compatível (exata ou dentre candidatas), "
                "atributos ABCD, biografia, perícias, talentos, equipamentos (15 po) e magias."
            ),
        },
        "regras_uso_procedural": {
            "subclasse_procedural": (
                "A partir do conceito escolhido, o motor resolve a subclasse oficial consultando "
                "`subclasses_oficiais_candidatas` (usando a subclasse exata quando única ou "
                "selecionando deterministicamente via seed entre as candidatas compatíveis)."
            ),
            "atributos_abcd": (
                "Distribuir melhorias livres (Ancestralidade, Biografia e Etapa D) seguindo "
                "a ordem de `prioridade_atributos`, respeitando máximo +1 por etapa e teto 18 no 1º nível."
            ),
            "biografia": (
                "Se o usuário escolher modo procedural, selecionar prioritariamente um ID em "
                "`biografias_recomendadas` cujo atributo restrito ajude os 3 primeiros itens de `prioridade_atributos`."
            ),
            "pericias": (
                "Alocar escolhas livres de perícia seguindo a ordem de `pericias_prioritarias` e, "
                "quando houver Saber livre, utilizar `saber_sugerido`."
            ),
            "talentos": (
                "Selecionar talentos válidos (nível/pré-requisitos atendidos) priorizando as listas de "
                "`talentos_recomendados` e pontuando talentos ancestrais que combinem com `tracos_ancestralidade_afinidade`."
            ),
            "equipamentos": (
                "Adquirir primeiro a melhor combinação de armadura, arma(s) e escudo (se `usa_escudo`) "
                "em `equipamento_recomendado` dentro do orçamento inicial de 15 po (1.500 pc)."
            ),
            "conjuracao": (
                "Quando `conjuracao_recomendada` ou `conjuracao_por_tradicao` não for nulo, preencher "
                "primeiro os espaços com `truques_prioritarios` e `magias_nivel_1_prioritarias`, "
                "completando eventuais vagas com magias da `tradicao` que possuam traços em "
                "`tracos_prioritarios` ou escolas em `escolas_prioritarias`."
            ),
        },
        "indice_por_classe": indice_por_classe,
        "conceitos": conceitos,
    }


def _carregar_json(nome_arquivo: str) -> dict[str, Any]:
    with (DIR_DADOS / nome_arquivo).open("r", encoding="utf-8") as f:
        return json.load(f)


def _validar_bloco_conjuracao(
    conj: dict[str, Any],
    magias_por_id: dict[str, dict[str, Any]],
    cid: str,
) -> None:
    trad = conj["tradicao"]
    assert trad in {"arcana", "divina", "ocultista", "primal"}, f"Tradição inválida '{trad}' em {cid}"
    for mid in conj["truques_prioritarios"]:
        assert mid in magias_por_id, f"Truque inválido '{mid}' em {cid}"
        m = magias_por_id[mid]
        assert "Truque Mágico" in m.get("tracos", []), f"'{mid}' não é Truque Mágico"
        assert trad in m.get("tradicoes", []), f"Truque '{mid}' não pertence à tradição '{trad}'"
    for mid in conj["magias_nivel_1_prioritarias"]:
        assert mid in magias_por_id, f"Magia N1 inválida '{mid}' em {cid}"
        m = magias_por_id[mid]
        assert m.get("nivel") == 1, f"Magia '{mid}' não é nível 1"
        assert trad in m.get("tradicoes", []), f"Magia '{mid}' não pertence à tradição '{trad}'"


def validar_conceitos(dados: dict[str, Any]) -> None:
    """Valida 100% das referências cruzadas contra os JSONs reais de `dados/`."""
    classes_por_id: dict[str, dict[str, Any]] = {}
    for fn in ("classes01.json", "classes02.json", "classes03.json"):
        for c in _carregar_json(fn)["classes"]:
            classes_por_id[c["id"]] = c

    biografias_ids = {
        b["id"] for b in _carregar_json("ancestralidades_biografias.json")["biografias"]["lista"]
    }
    pericias_ids = {p["id"] for p in _carregar_json("pericias.json")["pericias"]}

    talentos_dados = _carregar_json("talentos.json")["talentos"]
    talentos_por_id = {t["id"]: t for t in talentos_dados}

    eq = _carregar_json("equipamentos.json")
    armaduras_por_id = {a["id"]: a for a in eq["armaduras"]["itens"]}
    escudos_por_id = {s["id"]: s for s in eq["escudos"]["itens"]}
    armas_cc_por_id = {w["id"]: w for w in eq["armas"]["corpo_a_corpo"]}
    armas_dist_por_id = {w["id"]: w for w in eq["armas"]["distancia"]}
    kits_classes = {k["classe"] for k in eq["kits_de_classe"]}

    magias_lista = _carregar_json("magias01.json")["magias"] + _carregar_json("magias02.json")["magias"]
    magias_por_id = {m["id"]: m for m in magias_lista}

    tese_arcana_ids = {
        op["id"]
        for car in classes_por_id["mago"]["caracteristicas_de_classe"]
        if car["id"] == "tese_arcana"
        for op in car["detalhes"]["opcoes"]
    }

    atributos_validos = {"for", "des", "con", "int", "sab", "car"}
    conceitos = dados["conceitos"]
    ids_vistos: set[str] = set()

    assert len(conceitos) == 72, f"Esperados 72 conceitos, encontrados {len(conceitos)}"
    assert len(dados["indice_por_classe"]) == 12, "Todas as 12 classes devem possuir conceitos"
    for cid in classes_por_id:
        assert cid in dados["indice_por_classe"], f"Classe '{cid}' sem conceitos mapeados"
        assert len(dados["indice_por_classe"][cid]) == 6, (
            f"Classe '{cid}' deveria ter 6 conceitos, possui {len(dados['indice_por_classe'][cid])}"
        )

    for c in conceitos:
        cid = c["id"]
        assert cid not in ids_vistos, f"ID de conceito duplicado: {cid}"
        ids_vistos.add(cid)

        classe = classes_por_id[c["classe_id"]]
        assert c["classe_nome"] == classe["nome"]
        assert c["resumo_proposta"].strip(), f"resumo_proposta vazio em {cid}"
        assert c["sinergia_mecanica"].strip(), f"sinergia_mecanica vazio em {cid}"

        # Subclasses oficiais candidatas
        sub_por_id = {op["id"]: op for op in classe["subclasses"]["opcoes"]}
        candidatas = c["subclasses_oficiais_candidatas"]
        assert len(candidatas) >= 1, f"Sem subclasses candidatas em {cid}"
        assert candidatas[0] == c["subclasse_oficial_id"]
        assert len(candidatas) == len(c["subclasses_oficiais_nomes"])
        for sub_id, sub_nome in zip(candidatas, c["subclasses_oficiais_nomes"]):
            assert sub_id in sub_por_id, (
                f"Subclasse '{sub_id}' não existe em {c['classe_id']}: {list(sub_por_id)}"
            )
            assert sub_por_id[sub_id]["nome"] == sub_nome, (
                f"Nome divergente de subclasse '{sub_id}': {sub_nome!r} != {sub_por_id[sub_id]['nome']!r}"
            )

        # Tese Arcana (Mago)
        if c.get("tese_arcana_id") is not None:
            assert c["classe_id"] == "mago"
            assert c["tese_arcana_id"] in tese_arcana_ids, f"Tese Arcana inválida '{c['tese_arcana_id']}'"

        # Prioridade de atributos
        assert len(c["prioridade_atributos"]) == 6
        assert set(c["prioridade_atributos"]) == atributos_validos

        # Biografias e Perícias
        assert len(c["biografias_recomendadas"]) >= 3
        for bid in c["biografias_recomendadas"]:
            assert bid in biografias_ids, f"Biografia inválida '{bid}' em {cid}"
        for pid in c["pericias_prioritarias"]:
            assert pid in pericias_ids, f"Perícia inválida '{pid}' em {cid}"

        # Talentos de classe
        tal_classe = {t["id"]: t for t in classe["talentos_de_classe"]}
        for tid in c["talentos_recomendados"]["classe_nivel_1"]:
            assert tid in tal_classe, f"Talento de classe '{tid}' não encontrado em {c['classe_id']}"
            assert tal_classe[tid]["nivel"] == 1, f"Talento '{tid}' não é de nível 1"
        for tid in c["talentos_recomendados"]["classe_nivel_2_mais"]:
            assert tid in tal_classe, f"Talento de classe '{tid}' não encontrado em {c['classe_id']}"
            assert tal_classe[tid]["nivel"] >= 2, f"Talento '{tid}' deveria ser nível >= 2"

        # Talentos de perícia e gerais
        for tid in c["talentos_recomendados"]["pericia"]:
            assert tid in talentos_por_id, f"Talento de perícia inválido '{tid}' em {cid}"
            assert talentos_por_id[tid]["categoria"] == "pericia", f"'{tid}' não é Talento de Perícia"
        for tid in c["talentos_recomendados"]["gerais"]:
            assert tid in talentos_por_id, f"Talento geral inválido '{tid}' em {cid}"
            assert talentos_por_id[tid]["categoria"] == "geral", f"'{tid}' não é Talento Geral"

        # Equipamentos e proficiência base (1º nível) unificada com o motor
        eq_rec = c["equipamento_recomendado"]
        assert eq_rec["kit_classe_preferido"] in kits_classes
        assert len(eq_rec["armaduras_ids"]) >= 1

        mapa_cat_arm = {
            "Sem Armadura": "sem_armadura",
            "Armadura Leve": "leve",
            "Armadura Média": "media",
            "Armadura Pesada": "pesada",
        }
        armas_todas = armas_cc_por_id | armas_dist_por_id
        for wid in eq_rec["armas_corpo_a_corpo_ids"]:
            assert wid in armas_cc_por_id, f"Arma CC inválida '{wid}' em {cid}"
        for wid in eq_rec["armas_distancia_ids"]:
            assert wid in armas_dist_por_id or wid in armas_cc_por_id, f"Arma distância inválida '{wid}' em {cid}"

        tal_n1 = c["talentos_recomendados"]["classe_nivel_1"]
        for sub_id in candidatas:
            profs = calcular_proficiencias_combate(
                classe, sub_por_id[sub_id], talentos_classe_ids=tal_n1
            )
            for aid in eq_rec["armaduras_ids"]:
                assert aid in armaduras_por_id, f"Armadura inválida '{aid}' em {cid}"
                arm = armaduras_por_id[aid]
                chave_def = mapa_cat_arm[arm["categoria"]]
                assert profs["defesas"].get(chave_def, "destreinado") != "destreinado", (
                    f"Armadura '{aid}' sem proficiência no 1º nível em {cid} (sub={sub_id})"
                )
                if profs["restricao_nao_metal"]:
                    assert (arm.get("material") or "").lower() != "metal", (
                        f"Druida não pode usar armadura de metal '{aid}' em {cid}"
                    )

            for sid in eq_rec["escudos_ids"]:
                assert sid in escudos_por_id, f"Escudo inválido '{sid}' em {cid}"
                if profs["restricao_nao_metal"]:
                    assert "aco" not in sid, f"Druida não pode usar escudo de metal '{sid}' em {cid}"

            for wid in eq_rec["armas_corpo_a_corpo_ids"] + eq_rec["armas_distancia_ids"]:
                arma = armas_todas[wid]
                assert grau_arma(arma, profs["armas"]) != "destreinado", (
                    f"Arma '{wid}' ({arma['categoria']}) sem proficiência no 1º nível em {cid}"
                )

        # Conjuração (quando aplicável)
        conj = c["conjuracao_recomendada"]
        if conj is not None:
            _validar_bloco_conjuracao(conj, magias_por_id, cid)

        conj_trad = c.get("conjuracao_por_tradicao")
        if conj_trad is not None:
            for trad_k, bloco in conj_trad.items():
                assert bloco["tradicao"] == trad_k
                _validar_bloco_conjuracao(bloco, magias_por_id, cid)
            if c["classe_id"] == "feiticeiro":
                trads_req = {sub_por_id[sid]["tradicao_magica"] for sid in candidatas}
                assert trads_req.issubset(set(conj_trad.keys())), (
                    f"conjuracao_por_tradicao incompleto em {cid}: {trads_req} vs {set(conj_trad)}"
                )


def main() -> None:
    """Gera `dados/conceitos_subclasses.json`, valida todas as referências e imprime resumo."""
    dados = gerar_estrutura_conceitos()
    validar_conceitos(dados)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with CAMINHO_SAIDA.open("w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")

    tamanho = CAMINHO_SAIDA.stat().st_size
    print(f"Arquivo gerado com sucesso: {CAMINHO_SAIDA} ({tamanho} bytes)")
    print(f"Classes cobertas: {dados['meta']['total_classes_cobertas']}")
    print(f"Total de conceitos validados: {dados['meta']['total_conceitos']}")
    for cid, lista in dados["indice_por_classe"].items():
        print(f"  - {cid}: {len(lista)} ({', '.join(lista)})")


if __name__ == "__main__":
    main()
