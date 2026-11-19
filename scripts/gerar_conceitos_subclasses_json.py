"""Gera e valida o catálogo de Conceitos/Subclasses procedurais (`dados/conceitos_subclasses.json`).

Etapa 2 do projeto: define a proposta temática e mecânica ("norte") de cada
conceito para todas as 12 classes básicas do Pathfinder 2E, conectando:
- Subclasse oficial da classe (quando aplicável);
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
from pathlib import Path
from typing import Any


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
DIR_DADOS = RAIZ_PROJETO / "dados"
CAMINHO_SAIDA = DIR_DADOS / "conceitos_subclasses.json"


def _conceito(
    id_conceito: str,
    classe_id: str,
    classe_nome: str,
    nome: str,
    subclasse_oficial_id: str,
    subclasse_oficial_nome: str,
    resumo_proposta: str,
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
) -> dict[str, Any]:
    """Constrói um objeto de conceito estruturado de forma uniforme."""
    return {
        "id": id_conceito,
        "classe_id": classe_id,
        "classe_nome": classe_nome,
        "nome": nome,
        "titulo_completo": f"{classe_nome} — {nome}",
        "subclasse_oficial_id": subclasse_oficial_id,
        "subclasse_oficial_nome": subclasse_oficial_nome,
        "resumo_proposta": resumo_proposta,
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
    """Define os 38 conceitos iniciais cobrindo todas as 12 classes básicas."""
    return [
        # =====================================================================
        # 1. ALQUIMISTA (3)
        # =====================================================================
        _conceito(
            id_conceito="alquimista_bombardeiro",
            classe_id="alquimista",
            classe_nome="Alquimista",
            nome="Bombardeiro Elemental",
            subclasse_oficial_id="bombardeiro",
            subclasse_oficial_nome="Bombardeiro",
            resumo_proposta=(
                "Especialista em arremesso de bombas alquímicas de fogo, ácido, frio e "
                "eletricidade à distância, controlando áreas e explorando fraquezas."
            ),
            prioridade_atributos=["int", "des", "con", "sab", "car", "for"],
            biografias_recomendadas=["funileiro", "estudioso", "artesao", "batedor"],
            pericias_prioritarias=["manufatura", "acrobatismo", "furtividade", "arcanismo", "sociedade"],
            saber_sugerido="Saber de Alquimia",
            talentos_classe_n1=["bombardeiro_rapido", "lancador_longinquo", "alquimico_sagaz"],
            talentos_classe_n2_mais=["bomba_de_fumaca"],
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
            id_conceito="alquimista_cirurgiao",
            classe_id="alquimista",
            classe_nome="Alquimista",
            nome="Cirurgião de Campo",
            subclasse_oficial_id="cirurgiao",
            subclasse_oficial_nome="Cirurgião",
            resumo_proposta=(
                "Suporte tático focado em elixires de vida, antídotos e medicina de combate "
                "para manter o grupo vivo sob pressão."
            ),
            prioridade_atributos=["int", "sab", "des", "con", "car", "for"],
            biografias_recomendadas=["medico_de_campo", "herbalista", "estudioso", "acolito"],
            pericias_prioritarias=["manufatura", "medicina", "natureza", "diplomacia", "sociedade"],
            saber_sugerido="Saber de Anatomia",
            talentos_classe_n1=["alquimico_sagaz", "familiar_alquimico", "bombardeiro_rapido"],
            talentos_classe_n2_mais=["resistencia_a_veneno"],
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
            id_conceito="alquimista_mutagenista",
            classe_id="alquimista",
            classe_nome="Alquimista",
            nome="Mutagenista Bestial",
            subclasse_oficial_id="mutagenista",
            subclasse_oficial_nome="Mutagenista",
            resumo_proposta=(
                "Combatente alquímico que consome mutagênicos para ampliar força e resistência "
                "física, entrando na linha de frente."
            ),
            prioridade_atributos=["int", "for", "con", "des", "sab", "car"],
            biografias_recomendadas=["mineiro", "prisioneiro", "operario", "funileiro"],
            pericias_prioritarias=["manufatura", "atletismo", "intimidacao", "medicina", "sobrevivencia"],
            saber_sugerido="Saber de Alquimia",
            talentos_classe_n1=["familiar_alquimico", "alquimico_sagaz"],
            talentos_classe_n2_mais=["mutagenico_revivificante", "resistencia_a_veneno"],
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

        # =====================================================================
        # 2. BÁRBARO (3)
        # =====================================================================
        _conceito(
            id_conceito="barbaro_draconico_duas_maos",
            classe_id="barbaro",
            classe_nome="Bárbaro",
            nome="Fúria Dracônica (Duas Mãos)",
            subclasse_oficial_id="instinto_de_dragao",
            subclasse_oficial_nome="Instinto de Dragão",
            resumo_proposta=(
                "Guerreiro furioso canalizando poder dracônico elementar em golpes devastadores "
                "com armas pesadas de duas mãos."
            ),
            prioridade_atributos=["for", "con", "des", "car", "sab", "int"],
            biografias_recomendadas=["soldado", "gladiador", "nomade", "mineiro"],
            pericias_prioritarias=["atletismo", "intimidacao", "sobrevivencia", "acrobatismo", "natureza"],
            saber_sugerido="Saber de Dragões",
            talentos_classe_n1=["investida_subita", "intimidacao_enfurecida"],
            talentos_classe_n2_mais=["finalizacao_furiosa", "sem_escapatoria"],
            talentos_pericia=["olhar_intimidante", "lutador_titanico", "salto_rapido"],
            talentos_gerais=["vitalidade", "iniciativa_incrivel", "veloz"],
            tracos_ancestralidade_afinidade=["fogo", "dragao", "forca", "intimidacao"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_escamas", "gibao_de_peles"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["machado_longo", "montante", "malho"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="duas_maos",
        ),
        _conceito(
            id_conceito="barbaro_animal_agarrador",
            classe_id="barbaro",
            classe_nome="Bárbaro",
            nome="Predador Selvagem",
            subclasse_oficial_id="instinto_animal",
            subclasse_oficial_nome="Instinto Animal",
            resumo_proposta=(
                "Combatente feroz que assume traços bestiais durante a fúria para agarrar, "
                "derrubar e dilacerar inimigos."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "car", "int"],
            biografias_recomendadas=["cacador", "eremita", "encantador_de_animais", "nomade"],
            pericias_prioritarias=["atletismo", "natureza", "sobrevivencia", "intimidacao", "acrobatismo"],
            saber_sugerido="Saber de Feras",
            talentos_classe_n1=["visao_agucada", "investida_subita"],
            talentos_classe_n2_mais=["faro_agucado", "retomar_o_folego"],
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
            id_conceito="barbaro_gigante_esmagador",
            classe_id="barbaro",
            classe_nome="Bárbaro",
            nome="Colosso Esmagador",
            subclasse_oficial_id="instinto_de_gigante",
            subclasse_oficial_nome="Instinto de Gigante",
            resumo_proposta=(
                "Brutamontes imparável que empunha armas massivas de impacto para quebrar "
                "linhas inimigas com dano bruto."
            ),
            prioridade_atributos=["for", "con", "sab", "des", "car", "int"],
            biografias_recomendadas=["operario", "gladiador", "prisioneiro", "guarda"],
            pericias_prioritarias=["atletismo", "intimidacao", "sobrevivencia", "medicina"],
            saber_sugerido="Saber de Guerra",
            talentos_classe_n1=["investida_subita", "arremessador_enfurecido"],
            talentos_classe_n2_mais=["finalizacao_furiosa", "restabelecer_se"],
            talentos_pericia=["carregador_robusto", "lutador_titanico", "coagir_grupo"],
            talentos_gerais=["vitalidade", "duro_de_matar", "recuperacao_rapida"],
            tracos_ancestralidade_afinidade=["forca", "resistencia", "tamanho"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_escamas", "gibao_de_peles"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["malho", "clava_pesada", "picareta_pesada"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="duas_maos",
        ),

        # =====================================================================
        # 3. BARDO (3)
        # =====================================================================
        _conceito(
            id_conceito="bardo_maestro_inspirador",
            classe_id="bardo",
            classe_nome="Bardo",
            nome="Maestro Inspirador",
            subclasse_oficial_id="maestro",
            subclasse_oficial_nome="Maestro",
            resumo_proposta=(
                "Líder inspirador e conjurador ocultista focado em composições musicais, "
                "bônus ao grupo e controle emocional."
            ),
            prioridade_atributos=["car", "des", "con", "sab", "int", "for"],
            biografias_recomendadas=["animador", "artista", "emissario", "nobre"],
            pericias_prioritarias=["performance", "ocultismo", "diplomacia", "dissimulacao", "sociedade"],
            saber_sugerido="Saber de Teatro",
            talentos_classe_n1=["composicao_prolongada", "magia_de_alcance"],
            talentos_classe_n2_mais=["inspirar_competencia", "expansao_de_truque_magico"],
            talentos_pericia=["performance_impressionante", "artista_virtuoso", "camarada"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["carisma", "som", "diplomacia", "magia"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["rapieira", "adaga"],
            armas_distancia_ids=["funda", "besta_leve"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="ocultista",
                tracos_prioritarios=["Mental", "Emoção", "Auditivo", "Cura"],
                escolas_prioritarias=["Encantamento", "Ilusão"],
                truques_prioritarios=["escudo_mistico", "projetil_telecinetico", "mensagem", "detectar_magia", "pasmar"],
                magias_nivel_1_prioritarias=["abrandar", "bencao", "medo", "objeto_ilusorio"],
            ),
        ),
        _conceito(
            id_conceito="bardo_enigma_erudito",
            classe_id="bardo",
            classe_nome="Bardo",
            nome="Erudito do Enigma",
            subclasse_oficial_id="enigma",
            subclasse_oficial_nome="Enigma",
            resumo_proposta=(
                "Investigador místico que desvenda segredos antigos com Saber Bárdico e "
                "magias ocultistas de adivinhação e ilusão."
            ),
            prioridade_atributos=["car", "int", "des", "con", "sab", "for"],
            biografias_recomendadas=["estudioso", "detetive", "advogado", "vidente"],
            pericias_prioritarias=["ocultismo", "performance", "sociedade", "arcanismo", "religiao"],
            saber_sugerido="Saber de Mistérios",
            talentos_classe_n1=["saber_bardico", "magia_de_alcance"],
            talentos_classe_n2_mais=["etude_do_mestre_do_saber", "expansao_de_truque_magico"],
            talentos_pericia=["identificar_estranhezas", "reconhecer_magia", "poliglota"],
            talentos_gerais=["perspicacia_astuta", "iniciativa_incrivel", "vitalidade"],
            tracos_ancestralidade_afinidade=["conhecimento", "sabedoria", "idiomas", "oculto"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro", "armadura_acolchoada"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "cajado"],
            armas_distancia_ids=["besta_leve", "funda"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="ocultista",
                tracos_prioritarios=["Detecção", "Mental", "Ilusão", "Adivinhação"],
                escolas_prioritarias=["Adivinhação", "Ilusão"],
                truques_prioritarios=["detectar_magia", "ler_aura", "som_fantasma", "escudo_mistico", "mensagem"],
                magias_nivel_1_prioritarias=["vinculo_mental", "objeto_ilusorio", "disfarce_ilusorio", "golpe_certo"],
            ),
        ),
        _conceito(
            id_conceito="bardo_polimata_esgrimista",
            classe_id="bardo",
            classe_nome="Bardo",
            nome="Polímata Versátil",
            subclasse_oficial_id="polimata",
            subclasse_oficial_nome="Polímata",
            resumo_proposta=(
                "Aventureiro multifacetado que combina esgrima ágil, versatilidade social "
                "e repertório ocultista adaptável."
            ),
            prioridade_atributos=["car", "des", "int", "con", "sab", "for"],
            biografias_recomendadas=["charlatao", "emissario", "acrobata", "marinheiro"],
            pericias_prioritarias=["performance", "dissimulacao", "acrobatismo", "diplomacia", "ocultismo"],
            saber_sugerido="Saber de Bardo",
            talentos_classe_n1=["performance_versatil", "composicao_prolongada"],
            talentos_classe_n2_mais=["polimata_esoterico", "musa_multifacetada"],
            talentos_pericia=["mentiroso_charmoso", "distracao_prolongada", "performance_fascinante"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "passo_aprumado"],
            tracos_ancestralidade_afinidade=["agilidade", "social", "versatilidade"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["rapieira", "espada_curta", "adaga"],
            armas_distancia_ids=["besta_de_mao", "funda"],
            estilo_empunhadura="uma_mao",
            conjuracao_recomendada=_conjuracao(
                tradicao="ocultista",
                tracos_prioritarios=["Ilusão", "Mental", "Força"],
                escolas_prioritarias=["Ilusão", "Encantamento"],
                truques_prioritarios=["projetil_telecinetico", "escudo_mistico", "som_fantasma", "prestidigitacao", "luz"],
                magias_nivel_1_prioritarias=["disfarce_ilusorio", "cativar", "misseis_magicos", "abrandar"],
            ),
        ),

        # =====================================================================
        # 4. CAMPEÃO (3)
        # =====================================================================
        _conceito(
            id_conceito="campeao_paladino_baluarte",
            classe_id="campeao",
            classe_nome="Campeão",
            nome="Paladino Baluarte de Escudo",
            subclasse_oficial_id="paladino",
            subclasse_oficial_nome="Paladino",
            resumo_proposta=(
                "Defensor sagrado da linha de frente que protege aliados com Retribuição "
                "Justa, Bloqueio com Escudo e armadura resistente."
            ),
            prioridade_atributos=["for", "con", "car", "sab", "des", "int"],
            biografias_recomendadas=["guarda", "soldado", "acolito", "nobre"],
            pericias_prioritarias=["religiao", "atletismo", "diplomacia", "intimidacao", "medicina"],
            saber_sugerido="Saber de Heráldica",
            talentos_classe_n1=["peso_da_culpa", "dominio_de_divindade"],
            talentos_classe_n2_mais=["graca_divina", "juramento_reluzente"],
            talentos_pericia=["carregador_robusto", "olhar_intimidante", "estudante_do_canone"],
            talentos_gerais=["vitalidade", "duro_de_matar", "recuperacao_rapida"],
            tracos_ancestralidade_afinidade=["protecao", "resistencia", "divino"],
            categoria_armadura_preferida="pesada",
            armaduras_ids=["cota_de_talas", "cota_de_malha", "cota_de_escamas"],
            usa_escudo=True,
            escudos_ids=["escudo_de_aco", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["espada_longa", "martelo_de_guerra", "maca"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao_e_escudo",
        ),
        _conceito(
            id_conceito="campeao_redentor_protetor",
            classe_id="campeao",
            classe_nome="Campeão",
            nome="Redentor Protetor",
            subclasse_oficial_id="redentor",
            subclasse_oficial_nome="Redentor",
            resumo_proposta=(
                "Guardião compassivo que enfraquece atacantes inimigos, cura feridos com "
                "Imposição de Mãos e resolve conflitos com diplomacia."
            ),
            prioridade_atributos=["for", "car", "con", "sab", "des", "int"],
            biografias_recomendadas=["acolito", "medico_de_campo", "emissario", "guarda"],
            pericias_prioritarias=["religiao", "diplomacia", "medicina", "atletismo", "sociedade"],
            saber_sugerido="Saber de Teologia",
            talentos_classe_n1=["peso_da_culpa", "dominio_de_divindade"],
            talentos_classe_n2_mais=["graca_divina", "juramento_reluzente"],
            talentos_pericia=["medicina_de_batalha", "camarada", "impressionar_grupo"],
            talentos_gerais=["vitalidade", "recuperacao_rapida", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["cura", "diplomacia", "luz"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_malha", "cota_de_escamas"],
            usa_escudo=True,
            escudos_ids=["escudo_de_aco", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["maca", "espada_longa"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="uma_mao_e_escudo",
        ),
        _conceito(
            id_conceito="campeao_libertador_duas_maos",
            classe_id="campeao",
            classe_nome="Campeão",
            nome="Libertador Vingador (Duas Mãos)",
            subclasse_oficial_id="libertador",
            subclasse_oficial_nome="Libertador",
            resumo_proposta=(
                "Campeão móvel que liberta aliados de amarras e pune opressores com "
                "golpes pesados de espada longa de duas mãos ou haste."
            ),
            prioridade_atributos=["for", "con", "car", "des", "sab", "int"],
            biografias_recomendadas=["prisioneiro", "nomade", "soldado", "cacador_de_recompensas"],
            pericias_prioritarias=["religiao", "atletismo", "intimidacao", "acrobatismo", "sobrevivencia"],
            saber_sugerido="Saber de Heráldica",
            talentos_classe_n1=["passo_desimpedido", "dominio_de_divindade"],
            talentos_classe_n2_mais=["juramento_vingativo", "graca_divina"],
            talentos_pericia=["salto_rapido", "lutador_titanico", "olhar_intimidante"],
            talentos_gerais=["veloz", "vitalidade", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["mobilidade", "liberdade", "forca"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_malha", "cota_de_escamas"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["montante", "alabarda", "glaive"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="duas_maos",
        ),

        # =====================================================================
        # 5. CLÉRIGO (3)
        # =====================================================================
        _conceito(
            id_conceito="clerigo_sacerdote_curandeiro",
            classe_id="clerigo",
            classe_nome="Clérigo",
            nome="Sacerdote Curandeiro e Protetor",
            subclasse_oficial_id="sacerdote_enclausurado",
            subclasse_oficial_nome="Sacerdote Enclausurado",
            resumo_proposta=(
                "Conjurador divino devotado à cura massiva, remoção de condições e "
                "proteção sagrada do grupo."
            ),
            prioridade_atributos=["sab", "car", "con", "des", "int", "for"],
            biografias_recomendadas=["acolito", "medico_de_campo", "eremita", "herbalista"],
            pericias_prioritarias=["religiao", "medicina", "diplomacia", "sociedade", "natureza"],
            saber_sugerido="Saber de Teologia",
            talentos_classe_n1=["maos_curandeiras", "iniciado_no_dominio", "magia_de_alcance"],
            talentos_classe_n2_mais=["cura_comunal", "fonte_versatil"],
            talentos_pericia=["medicina_de_batalha", "estudante_do_canone", "camarada"],
            talentos_gerais=["vitalidade", "iniciativa_incrivel", "recuperacao_rapida"],
            tracos_ancestralidade_afinidade=["cura", "positivo", "sabedoria"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=True,
            escudos_ids=["escudo_de_madeira", "broquel"],
            armas_corpo_a_corpo_ids=["cajado", "maca_leve"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["Cura", "Positivo", "Abjuração", "Luz"],
                escolas_prioritarias=["Necromancia", "Abjuração", "Encantamento"],
                truques_prioritarios=["estabilizar", "luz", "escudo_mistico", "orientacao", "detectar_magia"],
                magias_nivel_1_prioritarias=["curar", "bencao", "santuario", "protecao"],
            ),
        ),
        _conceito(
            id_conceito="clerigo_capelao_guerra",
            classe_id="clerigo",
            classe_nome="Clérigo",
            nome="Capelão da Guerra",
            subclasse_oficial_id="capelao_da_guerra",
            subclasse_oficial_nome="Capelão da Guerra",
            resumo_proposta=(
                "Clérigo combatente que marcha de armadura e escudo na linha de frente, "
                "canalizando poder divino em sua arma predileta."
            ),
            prioridade_atributos=["sab", "for", "con", "car", "des", "int"],
            biografias_recomendadas=["soldado", "guarda", "acolito", "medico_de_campo"],
            pericias_prioritarias=["religiao", "atletismo", "medicina", "intimidacao", "diplomacia"],
            saber_sugerido="Saber de Guerra",
            talentos_classe_n1=["castigo_sagrado", "simplicidade_mortal", "maos_agressoras"],
            talentos_classe_n2_mais=["ornar_armamento", "fonte_versatil"],
            talentos_pericia=["olhar_intimidante", "medicina_de_batalha", "carregador_robusto"],
            talentos_gerais=["vitalidade", "duro_de_matar", "bloqueio_com_escudo"],
            tracos_ancestralidade_afinidade=["forca", "guerra", "resistencia"],
            categoria_armadura_preferida="media",
            armaduras_ids=["cota_de_escamas", "gibao_de_peles", "couro_batido"],
            usa_escudo=True,
            escudos_ids=["escudo_de_aco", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["maca", "lanca", "maca_estrela"],
            armas_distancia_ids=["azagaia", "funda"],
            estilo_empunhadura="uma_mao_e_escudo",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["Cura", "Positivo", "Encantamento", "Abjuração"],
                escolas_prioritarias=["Transmutação", "Encantamento", "Necromancia"],
                truques_prioritarios=["lanca_divina", "escudo_mistico", "estabilizar", "orientacao", "luz"],
                magias_nivel_1_prioritarias=["arma_magica", "curar", "bencao", "medo"],
            ),
        ),
        _conceito(
            id_conceito="clerigo_exorcista_radiante",
            classe_id="clerigo",
            classe_nome="Clérigo",
            nome="Exorcista da Luz",
            subclasse_oficial_id="sacerdote_enclausurado",
            subclasse_oficial_nome="Sacerdote Enclausurado",
            resumo_proposta=(
                "Caçador sagrado de mortos-vivos e abominações, combinando energia positiva "
                "ofensiva e proteções contra trevas."
            ),
            prioridade_atributos=["sab", "car", "des", "con", "int", "for"],
            biografias_recomendadas=["acolito", "estudioso", "vidente", "detetive"],
            pericias_prioritarias=["religiao", "ocultismo", "medicina", "diplomacia", "sociedade"],
            saber_sugerido="Saber de Mortos-Vivos",
            talentos_classe_n1=["iniciado_no_dominio", "maos_agressoras", "maos_curandeiras"],
            talentos_classe_n2_mais=["afastar_mortos_vivos", "expansao_de_truque_magico"],
            talentos_pericia=["estudante_do_canone", "reconhecer_magia", "identificar_estranhezas"],
            talentos_gerais=["iniciativa_incrivel", "vitalidade", "perspicacia_astuta"],
            tracos_ancestralidade_afinidade=["luz", "positivo", "visao"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["Positivo", "Luz", "Cura", "Detecção"],
                escolas_prioritarias=["Necromancia", "Evocação", "Abjuração"],
                truques_prioritarios=["disrupcao_de_morto_vivo", "lanca_divina", "luz", "detectar_magia", "estabilizar"],
                magias_nivel_1_prioritarias=["curar", "armas_de_disrupcao", "protecao", "detectar_tendencia"],
            ),
        ),

        # =====================================================================
        # 6. DRUIDA (3)
        # =====================================================================
        _conceito(
            id_conceito="druida_tempestade_elemental",
            classe_id="druida",
            classe_nome="Druida",
            nome="Druida da Tempestade Elemental",
            subclasse_oficial_id="tempestade",
            subclasse_oficial_nome="Ordem da Tempestade",
            resumo_proposta=(
                "Conjurador primal ofensivo que invoca relâmpagos, ventos e fúria elemental "
                "contra os inimigos da natureza."
            ),
            prioridade_atributos=["sab", "des", "con", "int", "car", "for"],
            biografias_recomendadas=["eremita", "marinheiro", "nomade", "vidente"],
            pericias_prioritarias=["natureza", "sobrevivencia", "acrobatismo", "medicina", "atletismo"],
            saber_sugerido="Saber de Clima",
            talentos_classe_n1=["nascido_da_tempestade", "ampliar_magia", "magia_de_alcance"],
            talentos_classe_n2_mais=["explorador_de_ordem", "resistencia_a_veneno"],
            talentos_pericia=["especialidade_em_terreno", "forrageador", "medicina_natural"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["tempestade", "ar", "eletricidade", "elemental"],
            categoria_armadura_preferida="media",
            armaduras_ids=["gibao_de_peles", "couro_batido", "couro"],
            usa_escudo=True,
            escudos_ids=["escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["cajado", "lanca"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["Ar", "Eletricidade", "Água", "Fogo", "Frio", "Evocação"],
                escolas_prioritarias=["Evocação", "Conjuração"],
                truques_prioritarios=["arco_eletrico", "produzir_chama", "raio_de_gelo", "orientacao", "detectar_magia"],
                magias_nivel_1_prioritarias=["toque_chocante", "lufada_de_vento", "empurrao_hidraulico", "curar"],
            ),
        ),
        _conceito(
            id_conceito="druida_animais_companheiro",
            classe_id="druida",
            classe_nome="Druida",
            nome="Guardião das Feras",
            subclasse_oficial_id="animais",
            subclasse_oficial_nome="Ordem dos Animais",
            resumo_proposta=(
                "Protetor dos ermos acompanhado por um companheiro animal leal, combinando "
                "magia primal de suporte, plantas e cura."
            ),
            prioridade_atributos=["sab", "des", "con", "for", "car", "int"],
            biografias_recomendadas=["encantador_de_animais", "cacador", "herbalista", "lavrador"],
            pericias_prioritarias=["natureza", "sobrevivencia", "medicina", "atletismo", "diplomacia"],
            saber_sugerido="Saber de Animais",
            talentos_classe_n1=["companheiro_animal", "ampliar_magia"],
            talentos_classe_n2_mais=["chamado_dos_ermos", "explorador_de_ordem"],
            talentos_pericia=["treinar_animal", "medicina_natural", "rastreador_experiente"],
            talentos_gerais=["vitalidade", "cavalgar", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["animal", "planta", "natureza", "cura"],
            categoria_armadura_preferida="media",
            armaduras_ids=["gibao_de_peles", "couro"],
            usa_escudo=True,
            escudos_ids=["escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["lanca", "cajado"],
            armas_distancia_ids=["funda", "dardo"],
            estilo_empunhadura="uma_mao_e_escudo",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["Cura", "Planta", "Positivo", "Transmutação"],
                escolas_prioritarias=["Conjuração", "Transmutação", "Necromancia"],
                truques_prioritarios=["emaranhape", "estabilizar", "orientacao", "luz", "detectar_magia"],
                magias_nivel_1_prioritarias=["curar", "presa_magica", "convocar_animal", "passos_largos"],
            ),
        ),
        _conceito(
            id_conceito="druida_selvagem_metamorfo",
            classe_id="druida",
            classe_nome="Druida",
            nome="Metamorfo Selvagem",
            subclasse_oficial_id="selvagens",
            subclasse_oficial_nome="Ordem Selvagem",
            resumo_proposta=(
                "Druida de combate corpo a corpo que utiliza formas selvagens, garras "
                "mágicas e vigor físico no coração da batalha."
            ),
            prioridade_atributos=["sab", "for", "con", "des", "car", "int"],
            biografias_recomendadas=["nomade", "cacador", "eremita", "operario"],
            pericias_prioritarias=["natureza", "atletismo", "sobrevivencia", "acrobatismo", "intimidacao"],
            saber_sugerido="Saber de Feras",
            talentos_classe_n1=["aspecto_selvagem", "ampliar_magia"],
            talentos_classe_n2_mais=["explorador_de_ordem", "resistencia_a_veneno"],
            talentos_pericia=["lutador_titanico", "escalador_de_combate", "forrageador"],
            talentos_gerais=["vitalidade", "duro_de_matar", "veloz"],
            tracos_ancestralidade_afinidade=["polimorfia", "garras", "forca", "selvagem"],
            categoria_armadura_preferida="media",
            armaduras_ids=["gibao_de_peles", "couro_batido"],
            usa_escudo=True,
            escudos_ids=["escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["lanca", "clava", "foice"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao_e_escudo",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["Polimorfia", "Transmutação", "Cura"],
                escolas_prioritarias=["Transmutação", "Necromancia"],
                truques_prioritarios=["produzir_chama", "estabilizar", "orientacao", "emaranhape"],
                magias_nivel_1_prioritarias=["presa_magica", "passos_largos", "forma_de_peste", "curar"],
            ),
        ),

        # =====================================================================
        # 7. FEITICEIRO (3)
        # =====================================================================
        _conceito(
            id_conceito="feiticeiro_elemental_piromante",
            classe_id="feiticeiro",
            classe_nome="Feiticeiro",
            nome="Feiticeiro Elemental",
            subclasse_oficial_id="elemental",
            subclasse_oficial_nome="Linhagem Elemental",
            resumo_proposta=(
                "Conjurador espontâneo primal de alto impacto cujo sangue canaliza chamas, "
                "geadas, ventos e tempestades."
            ),
            prioridade_atributos=["car", "des", "con", "sab", "int", "for"],
            biografias_recomendadas=["nomade", "eremita", "marinheiro", "mineiro"],
            pericias_prioritarias=["natureza", "intimidacao", "acrobatismo", "sobrevivencia", "diplomacia"],
            saber_sugerido="Saber Elemental",
            talentos_classe_n1=["feiticaria_perigosa", "ampliar_magia", "magia_de_alcance"],
            talentos_classe_n2_mais=["expansao_de_truque_magico"],
            talentos_pericia=["olhar_intimidante", "reconhecer_magia", "forrageador"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["fogo", "elemental", "ar", "agua", "terra"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "cajado"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="primal",
                tracos_prioritarios=["Fogo", "Água", "Ar", "Frio", "Eletricidade", "Ácido", "Evocação"],
                escolas_prioritarias=["Evocação"],
                truques_prioritarios=["produzir_chama", "arco_eletrico", "raio_de_gelo", "jorro_acido", "detectar_magia"],
                magias_nivel_1_prioritarias=["maos_flamejantes", "empurrao_hidraulico", "toque_chocante", "curar"],
            ),
        ),
        _conceito(
            id_conceito="feiticeiro_draconico_arcano",
            classe_id="feiticeiro",
            classe_nome="Feiticeiro",
            nome="Feiticeiro Dracônico",
            subclasse_oficial_id="draconica",
            subclasse_oficial_nome="Linhagem Dracônica",
            resumo_proposta=(
                "Herdeiro de sangue dracônico focado em magia arcana explosiva, presença "
                "imponente e defesa mística."
            ),
            prioridade_atributos=["car", "des", "con", "int", "sab", "for"],
            biografias_recomendadas=["nobre", "emissario", "estudioso", "charlatao"],
            pericias_prioritarias=["arcanismo", "intimidacao", "diplomacia", "dissimulacao", "acrobatismo"],
            saber_sugerido="Saber de Dragões",
            talentos_classe_n1=["feiticaria_perigosa", "magia_de_alcance", "contramagica"],
            talentos_classe_n2_mais=["expansao_de_truque_magico"],
            talentos_pericia=["olhar_intimidante", "sentido_arcano", "reconhecer_magia"],
            talentos_gerais=["iniciativa_incrivel", "vitalidade", "perspicacia_astuta"],
            tracos_ancestralidade_afinidade=["dragao", "arcano", "fogo", "carisma"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "cajado"],
            armas_distancia_ids=["besta_leve", "funda"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["Evocação", "Abjuração", "Força", "Fogo"],
                escolas_prioritarias=["Evocação", "Abjuração"],
                truques_prioritarios=["escudo_mistico", "produzir_chama", "raio_de_gelo", "projetil_telecinetico", "detectar_magia"],
                magias_nivel_1_prioritarias=["misseis_magicos", "armadura_mistica", "maos_flamejantes", "medo"],
            ),
        ),
        _conceito(
            id_conceito="feiticeiro_angelical_suporte",
            classe_id="feiticeiro",
            classe_nome="Feiticeiro",
            nome="Feiticeiro Angelical",
            subclasse_oficial_id="angelical",
            subclasse_oficial_nome="Linhagem Angelical",
            resumo_proposta=(
                "Portador de centelha celestial voltado à tradição divina, combinando cura "
                "espontânea, bênçãos e diplomacia inspiradora."
            ),
            prioridade_atributos=["car", "con", "des", "sab", "int", "for"],
            biografias_recomendadas=["acolito", "emissario", "nobre", "medico_de_campo"],
            pericias_prioritarias=["religiao", "diplomacia", "medicina", "performance", "sociedade"],
            saber_sugerido="Saber Celestial",
            talentos_classe_n1=["familiar", "ampliar_magia", "magia_de_alcance"],
            talentos_classe_n2_mais=["familiar_melhorado", "expansao_de_truque_magico"],
            talentos_pericia=["camarada", "impressionar_grupo", "medicina_de_batalha"],
            talentos_gerais=["vitalidade", "recuperacao_rapida", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["celestial", "luz", "cura", "carisma"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "cajado"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="divina",
                tracos_prioritarios=["Cura", "Positivo", "Luz", "Abjuração"],
                escolas_prioritarias=["Necromancia", "Encantamento", "Abjuração"],
                truques_prioritarios=["estabilizar", "luz", "lanca_divina", "escudo_mistico", "orientacao"],
                magias_nivel_1_prioritarias=["curar", "bencao", "santuario", "comando"],
            ),
        ),

        # =====================================================================
        # 8. GUERREIRO (4) — incluindo exemplo citado pelo usuário!
        # =====================================================================
        _conceito(
            id_conceito="guerreiro_espada_duas_maos",
            classe_id="guerreiro",
            classe_nome="Guerreiro",
            nome="Mestre da Espada de Duas Mãos",
            subclasse_oficial_id="agressor",
            subclasse_oficial_nome="Agressor",
            resumo_proposta=(
                "Combatente de elite focado em espadas pesadas de duas mãos (como Montante), "
                "priorizando golpes devastadores, investidas e presença marcial."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "car", "int"],
            biografias_recomendadas=["soldado", "gladiador", "guarda", "discipulo_marcial"],
            pericias_prioritarias=["atletismo", "intimidacao", "acrobatismo", "sobrevivencia", "medicina"],
            saber_sugerido="Saber de Guerra",
            talentos_classe_n1=["ataque_poderoso", "investida_subita", "golpe_de_exatidao"],
            talentos_classe_n2_mais=["golpe_intimidante", "empurrao_brutal", "estocada"],
            talentos_pericia=["olhar_intimidante", "lutador_titanico", "salto_rapido"],
            talentos_gerais=["vitalidade", "iniciativa_incrivel", "veloz"],
            tracos_ancestralidade_afinidade=["forca", "espada", "marcial", "resistencia"],
            categoria_armadura_preferida="pesada",
            armaduras_ids=["cota_de_malha", "cota_de_escamas", "cota_de_talas"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["montante", "espada_bastarda", "bracamante"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="duas_maos",
        ),
        _conceito(
            id_conceito="guerreiro_baluarte_escudo",
            classe_id="guerreiro",
            classe_nome="Guerreiro",
            nome="Baluarte de Espada e Escudo",
            subclasse_oficial_id="agressor",
            subclasse_oficial_nome="Agressor",
            resumo_proposta=(
                "Linha de frente altamente defensiva que combina Espada Longa e Escudo de Aço "
                "para segurar inimigos e contra-atacar com precisão."
            ),
            prioridade_atributos=["for", "con", "des", "sab", "car", "int"],
            biografias_recomendadas=["guarda", "soldado", "nobre", "mineiro"],
            pericias_prioritarias=["atletismo", "intimidacao", "medicina", "sobrevivencia"],
            saber_sugerido="Saber de Tática",
            talentos_classe_n1=["escudo_reativo", "golpe_de_exatidao", "ataque_fisgador"],
            talentos_classe_n2_mais=["bloqueio_agressivo", "atracar_em_combate"],
            talentos_pericia=["carregador_robusto", "medicina_de_batalha", "olhar_intimidante"],
            talentos_gerais=["vitalidade", "duro_de_matar", "recuperacao_rapida"],
            tracos_ancestralidade_afinidade=["resistencia", "escudo", "forca"],
            categoria_armadura_preferida="pesada",
            armaduras_ids=["cota_de_malha", "cota_de_escamas"],
            usa_escudo=True,
            escudos_ids=["escudo_de_aco", "escudo_de_madeira"],
            armas_corpo_a_corpo_ids=["espada_longa", "martelo_de_guerra", "machado_de_batalha"],
            armas_distancia_ids=["azagaia"],
            estilo_empunhadura="uma_mao_e_escudo",
        ),
        _conceito(
            id_conceito="guerreiro_duelista_duas_armas",
            classe_id="guerreiro",
            classe_nome="Guerreiro",
            nome="Duelista de Duas Armas",
            subclasse_oficial_id="duelista",
            subclasse_oficial_nome="Duelista",
            resumo_proposta=(
                "Esgrimista veloz especializado em combater com duas lâminas simultâneas, "
                "desferindo cortes duplos de alta acurácia."
            ),
            prioridade_atributos=["des", "for", "con", "sab", "car", "int"],
            biografias_recomendadas=["gladiador", "acrobata", "marinheiro", "nobre"],
            pericias_prioritarias=["acrobatismo", "atletismo", "diplomacia", "dissimulacao", "intimidacao"],
            saber_sugerido="Saber de Esgrima",
            talentos_classe_n1=["corte_duplo", "golpe_de_exatidao"],
            talentos_classe_n2_mais=["aparada_de_duelo", "estocada"],
            talentos_pericia=["equilibrio_estavel", "queda_do_gato", "olhar_intimidante"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "passo_aprumado"],
            tracos_ancestralidade_afinidade=["agilidade", "espada", "velocidade"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "camisao_de_malha", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_longa", "espada_curta", "rapieira"],
            armas_distancia_ids=["adaga"],
            estilo_empunhadura="duas_armas",
        ),
        _conceito(
            id_conceito="guerreiro_arqueiro_precisao",
            classe_id="guerreiro",
            classe_nome="Guerreiro",
            nome="Arqueiro de Precisão",
            subclasse_oficial_id="arqueiro",
            subclasse_oficial_nome="Arqueiro",
            resumo_proposta=(
                "Atirador de elite com proficiência superior em arcos, focado em acertos "
                "críticos a longa distância e apoio tático."
            ),
            prioridade_atributos=["des", "for", "con", "sab", "int", "car"],
            biografias_recomendadas=["batedor", "cacador", "soldado", "guarda"],
            pericias_prioritarias=["acrobatismo", "furtividade", "sobrevivencia", "atletismo", "natureza"],
            saber_sugerido="Saber de Arquearia",
            talentos_classe_n1=["tiro_certeiro", "golpe_de_exatidao"],
            talentos_classe_n2_mais=["tiro_de_assistencia"],
            talentos_pericia=["esgueirador_de_terreno", "queda_do_gato", "rastreador_experiente"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "perspicacia_astuta"],
            tracos_ancestralidade_afinidade=["arco", "elfo", "agilidade", "visao"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "adaga"],
            armas_distancia_ids=["arco_longo", "arco_curto"],
            estilo_empunhadura="distancia",
        ),

        # =====================================================================
        # 9. LADINO (3)
        # =====================================================================
        _conceito(
            id_conceito="ladino_ladrao_acrobata",
            classe_id="ladino",
            classe_nome="Ladino",
            nome="Ladrão Acrobata Furtivo",
            subclasse_oficial_id="ladrao",
            subclasse_oficial_nome="Ladrão",
            resumo_proposta=(
                "Infiltrador ágil que usa Destreza no dano de acuidade, desarma armadilhas, "
                "flanqueia com acrobacia e ataca das sombras."
            ),
            prioridade_atributos=["des", "con", "car", "sab", "int", "for"],
            biografias_recomendadas=["criminoso", "crianca_de_rua", "acrobata", "batedor"],
            pericias_prioritarias=["furtividade", "ladroagem", "acrobatismo", "dissimulacao", "sociedade"],
            saber_sugerido="Saber do Submundo",
            talentos_classe_n1=["esquiva_agil", "descobridor_de_armadilha"],
            talentos_classe_n2_mais=["mobilidade", "saque_rapido"],
            talentos_pericia=["punga", "queda_do_gato", "contrabandista_experiente"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "passo_aprumado"],
            tracos_ancestralidade_afinidade=["furtividade", "agilidade", "visao_no_escuro"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro", "couro_batido"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["rapieira", "espada_curta", "adaga"],
            armas_distancia_ids=["arco_curto", "adaga", "dardo"],
            estilo_empunhadura="uma_mao",
        ),
        _conceito(
            id_conceito="ladino_malandro_social",
            classe_id="ladino",
            classe_nome="Ladino",
            nome="Malandro Social e Fintador",
            subclasse_oficial_id="malandro",
            subclasse_oficial_nome="Malandro",
            resumo_proposta=(
                "Manipulador carismático que deixa alvos desprevenidos com fintas e "
                "enganações antes de aplicar ataques furtivos."
            ),
            prioridade_atributos=["des", "car", "con", "int", "sab", "for"],
            biografias_recomendadas=["charlatao", "apostador", "detetive", "emissario"],
            pericias_prioritarias=["dissimulacao", "diplomacia", "intimidacao", "ladroagem", "furtividade"],
            saber_sugerido="Saber das Ruas",
            talentos_classe_n1=["finta_dupla", "voce_e_o_proximo", "esquiva_agil"],
            talentos_classe_n2_mais=["finta_de_distracao", "magica_menor"],
            talentos_pericia=["mentiroso_charmoso", "distracao_prolongada", "manha_das_ruas"],
            talentos_gerais=["iniciativa_incrivel", "perspicacia_astuta", "veloz"],
            tracos_ancestralidade_afinidade=["carisma", "engano", "social"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro", "armadura_acolchoada"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["rapieira", "adaga"],
            armas_distancia_ids=["besta_de_mao", "adaga"],
            estilo_empunhadura="uma_mao",
        ),
        _conceito(
            id_conceito="ladino_rufiao_brutal",
            classe_id="ladino",
            classe_nome="Ladino",
            nome="Rufião Intimidador",
            subclasse_oficial_id="rufiao",
            subclasse_oficial_nome="Rufião",
            resumo_proposta=(
                "Bandido vigoroso focado em Força e Intimidação, usando armadura média e "
                "golpes pesados para assustar e derrubar oponentes."
            ),
            prioridade_atributos=["for", "des", "con", "car", "sab", "int"],
            biografias_recomendadas=["prisioneiro", "criminoso", "guarda", "gladiador"],
            pericias_prioritarias=["intimidacao", "atletismo", "ladroagem", "furtividade", "sociedade"],
            saber_sugerido="Saber do Submundo",
            talentos_classe_n1=["voce_e_o_proximo", "esquiva_agil"],
            talentos_classe_n2_mais=["surra_brutal", "golpe_desequilibrante"],
            talentos_pericia=["olhar_intimidante", "coagir_grupo", "lutador_titanico"],
            talentos_gerais=["vitalidade", "duro_de_matar", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["forca", "intimidacao", "resistencia"],
            categoria_armadura_preferida="media",
            armaduras_ids=["gibao_de_peles", "couro_batido"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "maca", "porrete"],
            armas_distancia_ids=["azagaia", "dardo"],
            estilo_empunhadura="uma_mao",
        ),

        # =====================================================================
        # 10. MAGO (4) — incluindo exemplo exato citado pelo usuário!
        # =====================================================================
        _conceito(
            id_conceito="mago_elementalista",
            classe_id="mago",
            classe_nome="Mago",
            nome="Elementalista",
            subclasse_oficial_id="evocacao",
            subclasse_oficial_nome="Escola de Evocação",
            resumo_proposta=(
                "Mago especializado em canalizar fogo, frio, eletricidade, ácido e "
                "ventos arcanos por meio da Escola de Evocação para dano elemental e controle."
            ),
            prioridade_atributos=["int", "des", "con", "sab", "car", "for"],
            biografias_recomendadas=["estudioso", "eremita", "funileiro", "vidente"],
            pericias_prioritarias=["arcanismo", "natureza", "manufatura", "ocultismo", "sociedade"],
            saber_sugerido="Saber Elemental",
            talentos_classe_n1=["ampliar_magia", "magia_de_alcance", "familiar"],
            talentos_classe_n2_mais=["expansao_de_truque_magico", "ocultar_magia"],
            talentos_pericia=["sentido_arcano", "reconhecer_magia", "identificacao_rapida"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["fogo", "elemental", "arcano", "inteligencia"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga"],
            armas_distancia_ids=["besta_leve"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["Fogo", "Água", "Terra", "Ar", "Frio", "Eletricidade", "Ácido", "Evocação"],
                escolas_prioritarias=["Evocação"],
                truques_prioritarios=["produzir_chama", "raio_de_gelo", "arco_eletrico", "jorro_acido", "escudo_mistico"],
                magias_nivel_1_prioritarias=["maos_flamejantes", "toque_chocante", "empurrao_hidraulico", "lufada_de_vento", "misseis_magicos"],
            ),
        ),
        _conceito(
            id_conceito="mago_ilusionista_controlador",
            classe_id="mago",
            classe_nome="Mago",
            nome="Ilusionista e Controlador",
            subclasse_oficial_id="ilusao",
            subclasse_oficial_nome="Escola de Ilusão",
            resumo_proposta=(
                "Mestre da enganação arcana que confunde sentidos, cria miragens táticas "
                "e manipula o campo de batalha sem confronto direto."
            ),
            prioridade_atributos=["int", "des", "car", "con", "sab", "for"],
            biografias_recomendadas=["charlatao", "artista", "detetive", "estudioso"],
            pericias_prioritarias=["arcanismo", "dissimulacao", "ocultismo", "sociedade", "furtividade"],
            saber_sugerido="Saber de Ilusões",
            talentos_classe_n1=["familiar", "magia_de_alcance", "ampliar_magia"],
            talentos_classe_n2_mais=["ocultar_magia", "familiar_melhorado"],
            talentos_pericia=["sentido_arcano", "distracao_prolongada", "reconhecer_magia"],
            talentos_gerais=["iniciativa_incrivel", "perspicacia_astuta", "veloz"],
            tracos_ancestralidade_afinidade=["ilusao", "gnomo", "arcano", "mental"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["adaga", "cajado"],
            armas_distancia_ids=["besta_leve"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["Ilusão", "Visual", "Mental", "Auditivo"],
                escolas_prioritarias=["Ilusão", "Encantamento"],
                truques_prioritarios=["som_fantasma", "mensagem", "escudo_mistico", "detectar_magia", "luzes_dancantes"],
                magias_nivel_1_prioritarias=["objeto_ilusorio", "leque_de_cores", "disfarce_ilusorio", "sono"],
            ),
        ),
        _conceito(
            id_conceito="mago_abjurador_protetor",
            classe_id="mago",
            classe_nome="Mago",
            nome="Abjurador Protetor",
            subclasse_oficial_id="abjuracao",
            subclasse_oficial_nome="Escola de Abjuração",
            resumo_proposta=(
                "Arcanista defensivo focado em barreiras mágicas, anulação de feitiços "
                "inimigos e preservação da equipe."
            ),
            prioridade_atributos=["int", "con", "des", "sab", "car", "for"],
            biografias_recomendadas=["estudioso", "advogado", "guarda", "nobre"],
            pericias_prioritarias=["arcanismo", "sociedade", "ocultismo", "manufatura", "diplomacia"],
            saber_sugerido="Saber Arcano",
            talentos_classe_n1=["contramagica", "familiar", "ignorar_materiais"],
            talentos_classe_n2_mais=["familiar_melhorado", "expansao_de_truque_magico"],
            talentos_pericia=["reconhecer_magia", "sentido_arcano", "identificacao_rapida"],
            talentos_gerais=["vitalidade", "iniciativa_incrivel", "duro_de_matar"],
            tracos_ancestralidade_afinidade=["abjuracao", "protecao", "arcano"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga"],
            armas_distancia_ids=["besta_leve"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["Abjuração", "Força", "Detecção"],
                escolas_prioritarias=["Abjuração", "Adivinhação"],
                truques_prioritarios=["escudo_mistico", "detectar_magia", "ler_aura", "projetil_telecinetico", "luz"],
                magias_nivel_1_prioritarias=["armadura_mistica", "alarme", "queda_suave", "misseis_magicos"],
            ),
        ),
        _conceito(
            id_conceito="mago_necromante_sombrio",
            classe_id="mago",
            classe_nome="Mago",
            nome="Necromante Erudito",
            subclasse_oficial_id="necromancia",
            subclasse_oficial_nome="Escola de Necromancia",
            resumo_proposta=(
                "Estudioso das fronteiras entre vida e morte que drena vitalidade, "
                "enfraquece adversários e domina magia sombria."
            ),
            prioridade_atributos=["int", "con", "des", "sab", "car", "for"],
            biografias_recomendadas=["estudioso", "eremita", "medico_de_campo", "vidente"],
            pericias_prioritarias=["arcanismo", "ocultismo", "religiao", "medicina", "intimidacao"],
            saber_sugerido="Saber de Necromancia",
            talentos_classe_n1=["ignorar_materiais", "familiar", "magia_de_alcance"],
            talentos_classe_n2_mais=["familiar_melhorado", "ocultar_magia"],
            talentos_pericia=["sentido_arcano", "identificar_estranhezas", "reconhecer_magia"],
            talentos_gerais=["vitalidade", "duro_de_matar", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["sombra", "negativo", "necromancia"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["cajado", "adaga"],
            armas_distancia_ids=["besta_leve"],
            estilo_empunhadura="conjurador",
            conjuracao_recomendada=_conjuracao(
                tradicao="arcana",
                tracos_prioritarios=["Necromancia", "Negativo", "Medo", "Doença"],
                escolas_prioritarias=["Necromancia"],
                truques_prioritarios=["toque_gelido", "escudo_mistico", "detectar_magia", "projetil_telecinetico"],
                magias_nivel_1_prioritarias=["raio_de_enfraquecimento", "gavinhas_sombrias", "medo", "armadura_mistica"],
            ),
        ),

        # =====================================================================
        # 11. MONGE (3)
        # =====================================================================
        _conceito(
            id_conceito="monge_postura_montanha",
            classe_id="monge",
            classe_nome="Monge",
            nome="Muralha da Postura da Montanha",
            subclasse_oficial_id="monge_da_garca",
            subclasse_oficial_nome="Estilo de Combate / Postura Marcial",
            resumo_proposta=(
                "Artista marcial focado em Força e resistência que usa a Postura da Montanha "
                "para compensar Destreza baixa e desferir golpes pesados."
            ),
            prioridade_atributos=["for", "con", "sab", "des", "car", "int"],
            biografias_recomendadas=["discipulo_marcial", "mineiro", "guarda", "operario"],
            pericias_prioritarias=["atletismo", "intimidacao", "medicina", "religiao", "sobrevivencia"],
            saber_sugerido="Saber de Artes Marciais",
            talentos_classe_n1=["postura_da_montanha", "postura_do_dragao"],
            talentos_classe_n2_mais=["agarrao_esmagador", "punho_atordoante"],
            talentos_pericia=["lutador_titanico", "olhar_intimidante", "carregador_robusto"],
            talentos_gerais=["vitalidade", "duro_de_matar", "recuperacao_rapida"],
            tracos_ancestralidade_afinidade=["forca", "terra", "resistencia"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["manopla"],
            armas_distancia_ids=["funda"],
            estilo_empunhadura="desarmado",
        ),
        _conceito(
            id_conceito="monge_tigre_agil",
            classe_id="monge",
            classe_nome="Monge",
            nome="Garras da Postura do Tigre",
            subclasse_oficial_id="monge_da_garca",
            subclasse_oficial_nome="Estilo de Combate / Postura Marcial",
            resumo_proposta=(
                "Combatente veloz e acrobático que ataca com golpes cortantes ágeis, "
                "alta Classe de Armadura sem armadura e mobilidade extrema."
            ),
            prioridade_atributos=["des", "for", "con", "sab", "car", "int"],
            biografias_recomendadas=["discipulo_marcial", "acrobata", "batedor", "crianca_de_rua"],
            pericias_prioritarias=["acrobatismo", "furtividade", "atletismo", "sobrevivencia", "medicina"],
            saber_sugerido="Saber de Artes Marciais",
            talentos_classe_n1=["postura_do_tigre", "postura_da_garca", "postura_do_lobo"],
            talentos_classe_n2_mais=["folha_dancante", "punho_atordoante"],
            talentos_pericia=["queda_do_gato", "equilibrio_estavel", "esgueirador_de_terreno"],
            talentos_gerais=["veloz", "iniciativa_incrivel", "passo_aprumado"],
            tracos_ancestralidade_afinidade=["agilidade", "velocidade", "garras"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["manopla"],
            armas_distancia_ids=["dardo", "funda"],
            estilo_empunhadura="desarmado",
        ),
        _conceito(
            id_conceito="monge_mestre_ki",
            classe_id="monge",
            classe_nome="Monge",
            nome="Mestre do Ki Elemental",
            subclasse_oficial_id="monge_do_ki",
            subclasse_oficial_nome="Caminho do Ki",
            resumo_proposta=(
                "Monge místico que canaliza energia espiritual (ki) para curar, acelerar "
                "movimentos e infundir elementos nos próprios punhos."
            ),
            prioridade_atributos=["des", "sab", "for", "con", "car", "int"],
            biografias_recomendadas=["discipulo_marcial", "eremita", "acolito", "vidente"],
            pericias_prioritarias=["acrobatismo", "religiao", "medicina", "ocultismo", "atletismo"],
            saber_sugerido="Saber Monástico",
            talentos_classe_n1=["golpe_de_ki", "disparada_de_ki", "arsenal_monastico"],
            talentos_classe_n2_mais=["punho_elemental", "punho_atordoante"],
            talentos_pericia=["medicina_de_batalha", "queda_do_gato", "estudante_do_canone"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["sabedoria", "ki", "elemental"],
            categoria_armadura_preferida="sem_armadura",
            armaduras_ids=["roupa_de_explorador"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["manopla", "cajado"],
            armas_distancia_ids=["dardo", "funda"],
            estilo_empunhadura="desarmado",
        ),

        # =====================================================================
        # 12. PATRULHEIRO (3)
        # =====================================================================
        _conceito(
            id_conceito="patrulheiro_arqueiro_precisao",
            classe_id="patrulheiro",
            classe_nome="Patrulheiro",
            nome="Atirador de Precisão",
            subclasse_oficial_id="precisao",
            subclasse_oficial_nome="Precisão",
            resumo_proposta=(
                "Caçador especialista em Caçar Presa com arco longo ou besta, maximizando "
                "dano de precisão no primeiro disparo do turno."
            ),
            prioridade_atributos=["des", "sab", "con", "for", "int", "car"],
            biografias_recomendadas=["cacador", "batedor", "cacador_de_recompensas", "nomade"],
            pericias_prioritarias=["natureza", "sobrevivencia", "furtividade", "acrobatismo", "medicina"],
            saber_sugerido="Saber de Caça",
            talentos_classe_n1=["tiro_a_caca", "as_com_besta", "cacador_de_monstros"],
            talentos_classe_n2_mais=["mira_do_cacador", "terreno_predileto"],
            talentos_pericia=["rastreador_experiente", "esgueirador_de_terreno", "forrageador"],
            talentos_gerais=["iniciativa_incrivel", "veloz", "vitalidade"],
            tracos_ancestralidade_afinidade=["arco", "elfo", "sentidos", "agilidade"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro_batido", "couro"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_curta", "adaga"],
            armas_distancia_ids=["arco_longo", "arco_curto", "besta_pesada"],
            estilo_empunhadura="distancia",
        ),
        _conceito(
            id_conceito="patrulheiro_duas_armas_rajada",
            classe_id="patrulheiro",
            classe_nome="Patrulheiro",
            nome="Caçador de Rajada (Duas Armas)",
            subclasse_oficial_id="rajada",
            subclasse_oficial_nome="Rajada",
            resumo_proposta=(
                "Combatente agressivo dos ermos que reduz penalidades de ataques múltiplos "
                "para desferir sequências rápidas com duas armas."
            ),
            prioridade_atributos=["for", "des", "con", "sab", "int", "car"],
            biografias_recomendadas=["cacador", "soldado", "marinheiro", "mineiro"],
            pericias_prioritarias=["natureza", "sobrevivencia", "atletismo", "acrobatismo", "intimidacao"],
            saber_sugerido="Saber de Sobrevivência",
            talentos_classe_n1=["abate_duplo", "cacador_de_monstros"],
            talentos_classe_n2_mais=["saque_rapido", "guardiao_contra_monstros"],
            talentos_pericia=["escalador_de_combate", "rastreador_experiente", "salto_rapido"],
            talentos_gerais=["vitalidade", "veloz", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["forca", "agilidade", "selvagem"],
            categoria_armadura_preferida="media",
            armaduras_ids=["couro_batido", "gibao_de_peles", "cota_de_escamas"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["espada_longa", "espada_curta", "machadinha"],
            armas_distancia_ids=["azagaia", "arco_curto"],
            estilo_empunhadura="duas_armas",
        ),
        _conceito(
            id_conceito="patrulheiro_senhor_feras",
            classe_id="patrulheiro",
            classe_nome="Patrulheiro",
            nome="Batedor Senhor das Feras",
            subclasse_oficial_id="despiste",
            subclasse_oficial_nome="Despiste",
            resumo_proposta=(
                "Explorador tático que atua em dupla com um companheiro animal, dominando "
                "rastreamento, emboscadas e empatia selvagem."
            ),
            prioridade_atributos=["des", "sab", "con", "for", "car", "int"],
            biografias_recomendadas=["encantador_de_animais", "batedor", "herbalista", "cacador"],
            pericias_prioritarias=["natureza", "sobrevivencia", "furtividade", "medicina", "acrobatismo"],
            saber_sugerido="Saber de Fauna",
            talentos_classe_n1=["companheiro_animal", "cacador_de_monstros"],
            talentos_classe_n2_mais=["empatia_selvagem", "terreno_predileto"],
            talentos_pericia=["treinar_animal", "medicina_natural", "rastreador_experiente"],
            talentos_gerais=["cavalgar", "vitalidade", "iniciativa_incrivel"],
            tracos_ancestralidade_afinidade=["animal", "natureza", "furtividade"],
            categoria_armadura_preferida="leve",
            armaduras_ids=["couro", "couro_batido"],
            usa_escudo=False,
            escudos_ids=[],
            armas_corpo_a_corpo_ids=["lanca", "espada_curta", "adaga"],
            armas_distancia_ids=["arco_curto", "funda"],
            estilo_empunhadura="distancia",
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
            "versao": "1.0",
            "total_classes_cobertas": len(indice_por_classe),
            "total_conceitos": len(conceitos),
            "descricao": (
                "Cada conceito define o 'norte' temático e mecânico do personagem, conectando "
                "subclasse oficial, prioridade de atributos (ABCD), biografias, perícias, "
                "talentos, equipamentos iniciais (15 po) e conjuração."
            ),
        },
        "regras_uso_procedural": {
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
                "Quando `conjuracao_recomendada` não for nulo, preencher primeiro os espaços com "
                "`truques_prioritarios` e `magias_nivel_1_prioritarias`, completando eventuais vagas com "
                "magias da `tradicao` que possuam traços em `tracos_prioritarios` ou escolas em `escolas_prioritarias`."
            ),
        },
        "indice_por_classe": indice_por_classe,
        "conceitos": conceitos,
    }


def _carregar_json(nome_arquivo: str) -> dict[str, Any]:
    with (DIR_DADOS / nome_arquivo).open("r", encoding="utf-8") as f:
        return json.load(f)


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

    atributos_validos = {"for", "des", "con", "int", "sab", "car"}
    conceitos = dados["conceitos"]
    ids_vistos: set[str] = set()

    assert len(dados["indice_por_classe"]) == 12, "Todas as 12 classes devem possuir conceitos"
    for cid in classes_por_id:
        assert cid in dados["indice_por_classe"], f"Classe '{cid}' sem conceitos mapeados"

    for c in conceitos:
        cid = c["id"]
        assert cid not in ids_vistos, f"ID de conceito duplicado: {cid}"
        ids_vistos.add(cid)

        classe = classes_por_id[c["classe_id"]]
        assert c["classe_nome"] == classe["nome"]

        # Subclasse oficial
        sub_opcoes = {op["id"] for op in classe["subclasses"]["opcoes"]}
        assert c["subclasse_oficial_id"] in sub_opcoes, (
            f"Subclasse '{c['subclasse_oficial_id']}' não existe em {c['classe_id']}: {sub_opcoes}"
        )

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

        # Equipamentos e proficiência base (1º nível)
        eq_rec = c["equipamento_recomendado"]
        assert eq_rec["kit_classe_preferido"] in kits_classes
        assert len(eq_rec["armaduras_ids"]) >= 1

        prof_def = dict(classe["proficiencias_iniciais"]["defesas"])
        if c["classe_id"] == "clerigo" and c["subclasse_oficial_id"] == "capelao_da_guerra":
            prof_def["armaduras_leves"] = "treinado"
            prof_def["armaduras_medias"] = "treinado"
        elif c["classe_id"] == "ladino" and c["subclasse_oficial_id"] == "rufiao":
            prof_def["armaduras_medias"] = "treinado"

        mapa_cat_arm = {
            "Sem Armadura": "defesa_sem_armadura",
            "Armadura Leve": "armaduras_leves",
            "Armadura Média": "armaduras_medias",
            "Armadura Pesada": "armaduras_pesadas",
        }
        for aid in eq_rec["armaduras_ids"]:
            assert aid in armaduras_por_id, f"Armadura inválida '{aid}' em {cid}"
            arm = armaduras_por_id[aid]
            chave_def = mapa_cat_arm[arm["categoria"]]
            grau_def = str(prof_def.get(chave_def, "destreinado")).lower()
            assert not grau_def.startswith("destreinado"), (
                f"Armadura '{aid}' sem proficiência no 1º nível em {cid}"
            )
            if c["classe_id"] == "druida":
                assert (arm.get("material") or "").lower() != "metal", (
                    f"Druida não pode usar armadura de metal '{aid}' em {cid}"
                )

        for sid in eq_rec["escudos_ids"]:
            assert sid in escudos_por_id, f"Escudo inválido '{sid}' em {cid}"
            if c["classe_id"] == "druida":
                assert "aco" not in sid, f"Druida não pode usar escudo de metal '{sid}' em {cid}"

        prof_atk = classe["proficiencias_iniciais"]["ataques"]
        esp_raw = prof_atk.get("armas_especificas")
        esp_nomes = (
            {n.lower() for n in esp_raw.get("armas", [])}
            if isinstance(esp_raw, dict)
            else ({n.lower() for n in esp_raw} if isinstance(esp_raw, list) else set())
        )
        armas_todas = armas_cc_por_id | armas_dist_por_id
        for wid in eq_rec["armas_corpo_a_corpo_ids"]:
            assert wid in armas_cc_por_id, f"Arma CC inválida '{wid}' em {cid}"
        for wid in eq_rec["armas_distancia_ids"]:
            assert wid in armas_dist_por_id or wid in armas_cc_por_id, f"Arma distância inválida '{wid}' em {cid}"
        for wid in eq_rec["armas_corpo_a_corpo_ids"] + eq_rec["armas_distancia_ids"]:
            arma = armas_todas[wid]
            cat = arma["categoria"]
            if wid == "bomba_alquimica":
                ok = not str(prof_atk.get("bombas_alquimicas", "destreinado")).startswith("destreinado")
            elif arma["nome"].lower() in esp_nomes:
                ok = True
            elif cat == "Arma Simples":
                ok = not str(prof_atk.get("armas_simples", "destreinado")).startswith("destreinado")
            elif cat == "Arma Marcial":
                ok = not str(prof_atk.get("armas_marciais", "destreinado")).startswith("destreinado")
            elif cat == "Arma Avançada":
                ok = not str(prof_atk.get("armas_avancadas", "destreinado")).startswith("destreinado")
            else:
                ok = False
            assert ok, f"Arma '{wid}' ({cat}) sem proficiência no 1º nível em {cid}"

        # Conjuração (quando aplicável)
        conj = c["conjuracao_recomendada"]
        if conj is not None:
            trad = conj["tradicao"]
            assert trad in {"arcana", "divina", "ocultista", "primal"}
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
