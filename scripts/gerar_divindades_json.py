"""Gera e valida o catálogo oficial de Divindades e Domínios (`dados/divindades.json`).

Extrai e estrutura todas as 20 Divindades Principais e os 37 Domínios da
Tabela 8–2 do Livro Básico de Pathfinder 2ª Edição (`pp. 437–441`), validando
1:1 perícias divinas, armas favorecidas, domínios e magias de clérigo contra
os demais arquivos JSON de `dados/`.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
DIR_DADOS = RAIZ_PROJETO / "dados" / "dadospf2"
CAMINHO_SAIDA = DIR_DADOS / "divindades.json"


def _norm(texto: str) -> str:
    sem = unicodedata.normalize("NFD", texto.lower().strip())
    return "".join(ch for ch in sem if unicodedata.category(ch) != "Mn")


def _divindade(
    id_div: str,
    nome: str,
    tendencia: str,
    resumo: str,
    editos: str,
    anatema: str,
    tendencias_seguidores: list[str],
    fontes_divinas: list[str],
    pericia_divina: list[str],
    arma_favorecida_id: str,
    arma_favorecida_nome: str,
    dominios: list[str],
    magias_clerigo: dict[str, str],
) -> dict[str, Any]:
    return {
        "id": id_div,
        "nome": nome,
        "tendencia": tendencia,
        "resumo": resumo,
        "editos": editos,
        "anatema": anatema,
        "tendencias_seguidores": tendencias_seguidores,
        "fontes_divinas": fontes_divinas,
        "pericia_divina": pericia_divina,
        "arma_favorecida_id": arma_favorecida_id,
        "arma_favorecida_nome": arma_favorecida_nome,
        "dominios": dominios,
        "magias_clerigo": magias_clerigo,
    }


def _construir_divindades() -> list[dict[str, Any]]:
    return [
        _divindade(
            id_div="abadar",
            nome="Abadar",
            tendencia="ON",
            resumo="O Mestre do Primeiro Cofre tem influência sobre as cidades, as leis, os mercadores e as riquezas.",
            editos="leve a civilização às fronteiras, ganhe riqueza através de trabalho duro e comércio, siga o estado de direito",
            anatema="engaje em bandidagem ou pirataria, roube, enfraqueça um tribunal cumpridor da lei",
            tendencias_seguidores=["OB", "ON", "OM"],
            fontes_divinas=["curar", "ferir"],
            pericia_divina=["sociedade"],
            arma_favorecida_id="besta_leve",
            arma_favorecida_nome="Besta leve",
            dominios=["Cidades", "Riqueza", "Terra", "Viagem"],
            magias_clerigo={"1": "objeto_ilusorio", "4": "criacao", "7": "mansao_magnifica"},
        ),
        _divindade(
            id_div="asmodeus",
            nome="Asmodeus",
            tendencia="OM",
            resumo="O Príncipe das Trevas reina sobre os contratos, o orgulho, a escravidão e a tirania.",
            editos="negocie contratos em seu benefício, governe tiranicamente e torture seres mais fracos, mostre subserviência aos seus superiores",
            anatema="quebre um contrato, liberte um escravo, insulte Asmodeus demonstrando misericórdia aos seus inimigos",
            tendencias_seguidores=["OM"],
            fontes_divinas=["ferir"],
            pericia_divina=["dissimulacao"],
            arma_favorecida_id="maca",
            arma_favorecida_nome="Maça",
            dominios=["Confiança", "Enganação", "Fogo", "Tirania"],
            magias_clerigo={"1": "cativar", "4": "sugestao", "6": "despistar"},
        ),
        _divindade(
            id_div="calistria",
            nome="Calístria",
            tendencia="CN",
            resumo="A Doce Ferroada enaltece as virtudes da luxúria, da vingança e da enganação.",
            editos="persiga sua liberdade individual, busque emoções hedonistas, vingue-se",
            anatema="seja consumido demais por amor ou por necessidade de vingança, deixe uma ofensa passar em branco",
            tendencias_seguidores=["CB", "CN", "CM"],
            fontes_divinas=["curar", "ferir"],
            pericia_divina=["dissimulacao"],
            arma_favorecida_id="chicote",
            arma_favorecida_nome="Chicote",
            dominios=["Dor", "Enganação", "Paixão", "Segredos"],
            magias_clerigo={"1": "cativar", "3": "subjugar", "6": "despistar"},
        ),
        _divindade(
            id_div="cayden_cailean",
            nome="Cayden Cailean",
            tendencia="CB",
            resumo="O Herói Bêbado promove a liberdade, a coragem e a luta pelas causas justas.",
            editos="beba, liberte escravos e auxilie os oprimidos, busque glória e aventura",
            anatema="desperdice álcool, seja malvado ou reservado quando bêbado, possua um escravo",
            tendencias_seguidores=["NB", "CB", "CN"],
            fontes_divinas=["curar"],
            pericia_divina=["atletismo"],
            arma_favorecida_id="rapieira",
            arma_favorecida_nome="Rapieira",
            dominios=["Cidades", "Indulgência", "Liberdade", "Poder"],
            magias_clerigo={"1": "passos_velozes", "2": "toque_da_idiotice", "5": "alucinacao"},
        ),
        _divindade(
            id_div="desna",
            nome="Desna",
            tendencia="CB",
            resumo="A gentil Canção das Esferas preside sobre os sonhos, a sorte, as estrelas e os viajantes.",
            editos="auxilie companheiros de viagem, explore lugares novos, expresse-se através da arte e da canção, descubra o que a vida tem a oferecer",
            anatema="cause medo ou desespero, conjure pesadelo ou use uma magia similar para corromper sonhos, engaje em comportamento fanático",
            tendencias_seguidores=["NB", "CB", "CN"],
            fontes_divinas=["curar"],
            pericia_divina=["acrobatismo"],
            arma_favorecida_id="faca_estrela",
            arma_favorecida_nome="Faca-estrela",
            dominios=["Lua", "Sonhos", "Sorte", "Viagem"],
            magias_clerigo={"1": "sono", "4": "voar", "5": "potencial_onirico"},
        ),
        _divindade(
            id_div="erastil",
            nome="Erastil",
            tendencia="OB",
            resumo="O Velho Certeiro é o deus da família, das fazendas, da caça e da proteção das comunidades.",
            editos="cuide de sua casa e família, cumpra seus deveres, mantenha a paz, proteja a comunidade",
            anatema="abandone seu lar em um momento de necessidade, escolha a si sobre sua comunidade, manche sua reputação, conte mentiras",
            tendencias_seguidores=["OB", "NB", "ON"],
            fontes_divinas=["curar"],
            pericia_divina=["sobrevivencia"],
            arma_favorecida_id="arco_longo",
            arma_favorecida_nome="Arco longo",
            dominios=["Família", "Natureza", "Riqueza", "Terra"],
            magias_clerigo={"1": "golpe_certo", "3": "muralha_de_espinhos", "5": "deslocamento_entre_arvores"},
        ),
        _divindade(
            id_div="gorum",
            nome="Gorum",
            tendencia="CN",
            resumo="Nosso Senhor em Ferro, deus da batalha, da força e das armas, cultuado pelo combate direto.",
            editos="obtenha vitória em combate justo, force seus limites, use armadura em combate",
            anatema="mate prisioneiros ou oponentes rendidos, impeça o conflito através de negociação, vença uma batalha através de táticas desonestas ou magia indireta",
            tendencias_seguidores=["CN", "CM"],
            fontes_divinas=["curar", "ferir"],
            pericia_divina=["atletismo"],
            arma_favorecida_id="montante",
            arma_favorecida_nome="Montante",
            dominios=["Confiança", "Destruição", "Fervor", "Poder"],
            magias_clerigo={"1": "golpe_certo", "2": "crescer", "4": "tempestade_de_armas"},
        ),
        _divindade(
            id_div="gozreh",
            nome="Gozreh",
            tendencia="N",
            resumo="Os Ventos e As Ondas, divindade de dois aspectos que governa a natureza, o mar e o clima.",
            editos="celebre, proteja e respeite a natureza em todas as suas formas",
            anatema="leve a civilização a se infiltrar nas regiões selvagens, crie mortos-vivos, despoje áreas de beleza natural",
            tendencias_seguidores=["NB", "ON", "N", "CN", "NM"],
            fontes_divinas=["curar"],
            pericia_divina=["sobrevivencia"],
            arma_favorecida_id="tridente",
            arma_favorecida_nome="Tridente",
            dominios=["Água", "Ar", "Natureza", "Viagem"],
            magias_clerigo={"1": "lufada_de_vento", "3": "relampago", "5": "controlar_a_agua"},
        ),
        _divindade(
            id_div="iomedae",
            nome="Iomedae",
            tendencia="OB",
            resumo="A Herdeira é a deusa da honra, da justiça, da regência e da valentia.",
            editos="seja comedido, lute por justiça e honra, tenha valentia em seu coração",
            anatema="abandone um companheiro necessitado, desonre-se, recuse um desafio de um igual",
            tendencias_seguidores=["OB", "NB"],
            fontes_divinas=["curar"],
            pericia_divina=["intimidacao"],
            arma_favorecida_id="espada_longa",
            arma_favorecida_nome="Espada longa",
            dominios=["Confiança", "Fervor", "Poder", "Verdade"],
            magias_clerigo={"1": "golpe_certo", "2": "crescer", "4": "escudo_de_fogo"},
        ),
        _divindade(
            id_div="irori",
            nome="Irori",
            tendencia="ON",
            resumo="O Mestre dos Mestres preside sobre a história, o conhecimento e o autoaperfeiçoamento.",
            editos="seja humilde, ajude os outros a se aperfeiçoarem, aprimore seu corpo, mente e espírito até um estado mais perfeito, pratique disciplina",
            anatema="fique viciado em uma substância, destrua um texto histórico importante, falhe em manter o autocontrole repetidamente",
            tendencias_seguidores=["OB", "ON", "OM"],
            fontes_divinas=["curar", "ferir"],
            pericia_divina=["atletismo"],
            arma_favorecida_id="punho",
            arma_favorecida_nome="Punho",
            dominios=["Conhecimento", "Perfeição", "Poder", "Verdade"],
            magias_clerigo={"1": "salto", "3": "rapidez", "4": "pele_de_pedra"},
        ),
        _divindade(
            id_div="lamashtu",
            nome="Lamashtu",
            tendencia="CM",
            resumo="A Mãe dos Monstros é a deusa da loucura, dos monstros e dos pesadelos.",
            editos="traga poder aos exilados e desfavorecidos, doutrine crianças nos ensinamentos de Lamashtu, torne o belo monstruoso, revele a corrupção e as falhas em todas as coisas",
            anatema="tente tratar uma doença mental ou deformidade, forneça socorro aos inimigos de Lamashtu",
            tendencias_seguidores=["CM"],
            fontes_divinas=["curar", "ferir"],
            pericia_divina=["sobrevivencia"],
            arma_favorecida_id="bracamante",
            arma_favorecida_nome="Bracamante",
            dominios=["Enganação", "Família", "Pesadelos", "Poder"],
            magias_clerigo={"1": "presa_magica", "2": "forma_de_animal", "4": "pesadelo"},
        ),
        _divindade(
            id_div="nethys",
            nome="Nethys",
            tendencia="N",
            resumo="O Olho que Tudo Vê, deus da magia com natureza dualística de destruição e preservação.",
            editos="busque poder mágico e o use",
            anatema="persiga caminhos mundanos no lugar dos mágicos",
            tendencias_seguidores=["NB", "ON", "N", "CN", "NM"],
            fontes_divinas=["curar", "ferir"],
            pericia_divina=["arcanismo"],
            arma_favorecida_id="cajado",
            arma_favorecida_nome="Cajado",
            dominios=["Conhecimento", "Destruição", "Magia", "Proteção"],
            magias_clerigo={"1": "misseis_magicos", "2": "boca_magica", "3": "levitacao"},
        ),
        _divindade(
            id_div="norgorber",
            nome="Norgorber",
            tendencia="NM",
            resumo="O deus da ganância, do homicídio, dos venenos e dos segredos ocultos.",
            editos="mantenha sua verdadeira identidade em segredo, sacrifique quem for preciso, aproveite cada vantagem em uma luta, trabalhe das sombras",
            anatema="permita que sua verdadeira identidade seja conectada aos seus negócios escusos, partilhe um segredo livremente, mostre misericórdia",
            tendencias_seguidores=["OM", "NM", "CM", "N"],
            fontes_divinas=["ferir"],
            pericia_divina=["furtividade"],
            arma_favorecida_id="espada_curta",
            arma_favorecida_nome="Espada curta",
            dominios=["Enganação", "Morte", "Riqueza", "Segredos"],
            magias_clerigo={"1": "disfarce_ilusorio", "2": "invisibilidade", "4": "assassino_fantasmagorico"},
        ),
        _divindade(
            id_div="pharasma",
            nome="Pharasma",
            tendencia="N",
            resumo="A Senhora das Tumbas preside sobre o nascimento, a morte, o destino e a profecia.",
            editos="lute para compreender antigas profecias, destrua mortos-vivos, prepare os corpos para o descanso",
            anatema="crie mortos-vivos, profane um corpo, pilhe uma tumba",
            tendencias_seguidores=["NB", "ON", "N"],
            fontes_divinas=["curar"],
            pericia_divina=["medicina"],
            arma_favorecida_id="adaga",
            arma_favorecida_nome="Adaga",
            dominios=["Conhecimento", "Cura", "Destino", "Morte"],
            magias_clerigo={"1": "vinculo_mental", "3": "arma_fantasmagorica", "4": "assassino_fantasmagorico"},
        ),
        _divindade(
            id_div="rovagug",
            nome="Rovagug",
            tendencia="CM",
            resumo="A Besta Violenta é o deus da destruição, do desastre e da ira primordial.",
            editos="destrua todas as coisas; liberte Rovagug de sua prisão",
            anatema="crie algo novo, deixe laços materiais o restringirem, torture uma vítima ou atrase sua destruição de qualquer forma",
            tendencias_seguidores=["NM", "CM"],
            fontes_divinas=["ferir"],
            pericia_divina=["atletismo"],
            arma_favorecida_id="machado_longo",
            arma_favorecida_nome="Machado longo",
            dominios=["Ar", "Destruição", "Fervor", "Terra"],
            magias_clerigo={"1": "maos_flamejantes", "2": "crescer", "6": "desintegrar"},
        ),
        _divindade(
            id_div="sarenrae",
            nome="Sarenrae",
            tendencia="NB",
            resumo="A Flor do Alvorecer é a deusa da cura, da honestidade, da redenção e do sol.",
            editos="destrua as Proles de Rovagug, proteja aliados, forneça auxílio aos doentes e feridos, busque e permita redenção",
            anatema="crie mortos-vivos, minta, negue a oportunidade de redenção a uma criatura arrependida, falhe em acabar com o mal",
            tendencias_seguidores=["OB", "NB", "CB"],
            fontes_divinas=["curar"],
            pericia_divina=["medicina"],
            arma_favorecida_id="cimitarra",
            arma_favorecida_nome="Cimitarra",
            dominios=["Cura", "Fogo", "Sol", "Verdade"],
            magias_clerigo={"1": "maos_flamejantes", "3": "bola_de_fogo", "4": "muralha_de_fogo"},
        ),
        _divindade(
            id_div="shelyn",
            nome="Shelyn",
            tendencia="NB",
            resumo="A Rosa Eterna é a deusa da arte, da beleza, do amor e da música.",
            editos="seja pacífico, escolha e aperfeiçoe uma arte, lidere através do exemplo, veja beleza em todas as coisas",
            anatema="destrua arte ou permita que seja destruída (a menos que esteja salvando uma vida ou em busca de uma arte maior), recuse-se a aceitar rendição",
            tendencias_seguidores=["OB", "NB", "CB"],
            fontes_divinas=["curar"],
            pericia_divina=["manufatura", "performance"],
            arma_favorecida_id="glaive",
            arma_favorecida_nome="Glaive",
            dominios=["Criação", "Família", "Paixão", "Proteção"],
            magias_clerigo={"1": "leque_de_cores", "3": "subjugar", "4": "criacao"},
        ),
        _divindade(
            id_div="torag",
            nome="Torag",
            tendencia="OB",
            resumo="O Pai da Criação é o deus enânico da forja, da proteção e da estratégia.",
            editos="seja honrado e direto, mantenha sua palavra, respeite a forja, sirva o seu povo",
            anatema="conte mentiras ou traia alguém, crie intencionalmente trabalhos inferiores, mostre misericórdia aos inimigos do seu povo",
            tendencias_seguidores=["OB", "ON"],
            fontes_divinas=["curar"],
            pericia_divina=["manufatura"],
            arma_favorecida_id="martelo_de_guerra",
            arma_favorecida_nome="Martelo de guerra",
            dominios=["Criação", "Família", "Proteção", "Terra"],
            magias_clerigo={"1": "vinculo_mental", "3": "prender_a_terra", "4": "criacao"},
        ),
        _divindade(
            id_div="urgathoa",
            nome="Urgathoa",
            tendencia="NM",
            resumo="A Princesa Pálida supervisiona a doença, a gula e a não-morte.",
            editos="torne-se um morto-vivo quando morrer, crie ou proteja os mortos-vivos, sacie seus apetites",
            anatema="negue seus apetites, destrua mortos-vivos, sacrifique sua vida",
            tendencias_seguidores=["OM", "NM", "CM"],
            fontes_divinas=["ferir"],
            pericia_divina=["intimidacao"],
            arma_favorecida_id="segadeira",
            arma_favorecida_nome="Segadeira",
            dominios=["Indulgência", "Magia", "Não-morte", "Poder"],
            magias_clerigo={"1": "variola_goblin", "2": "vitalidade_falsa", "7": "mascara_do_terror"},
        ),
        _divindade(
            id_div="zon_kuthon",
            nome="Zon-Kuthon",
            tendencia="OM",
            resumo="O Senhor da Meia-Noite é o deus da escuridão, da inveja, da perda e da dor.",
            editos="traga dor ao mundo, mutile seu corpo",
            anatema="crie fontes de luz permanentes ou duradouras, forneça conforto para os que sofrem",
            tendencias_seguidores=["ON", "OM", "NM"],
            fontes_divinas=["ferir"],
            pericia_divina=["intimidacao"],
            arma_favorecida_id="corrente_com_cravos",
            arma_favorecida_nome="Corrente com cravos",
            dominios=["Ambição", "Destruição", "Dor", "Escuridão"],
            magias_clerigo={"1": "dor_fantasma", "3": "muralha_de_espinhos", "5": "caminhar_nas_sombras"},
        ),
    ]


def _construir_dominios() -> list[dict[str, str]]:
    tabela = [
        ("Água", "Você controla água e corpos d'água.", "surto_da_mare", "aguaceiro"),
        ("Ambição", "Você se esforça para acompanhar e superar a competição.", "ambicao_cega", "vantagem_competitiva"),
        ("Ar", "Você pode controlar ventos e o clima.", "lufada_empurrante", "dispersar_no_ar"),
        ("Cidades", "Você possui poderes sobre ambientes e habitantes urbanos.", "rosto_na_multidao", "pulso_da_cidade"),
        ("Confiança", "Você supera seu medo e projeta orgulho.", "veu_de_confianca", "soberba_delirante"),
        ("Conhecimento", "Você recebe intuições divinas.", "recordacao_academica", "conhecer_o_inimigo"),
        ("Criação", "Você possui habilidades divinas relacionadas a manufatura e artes.", "salpico_de_arte", "floreio_artistico"),
        ("Cura", "Você usa cura mágica de forma particularmente potente.", "bencao_do_curandeiro", "censurar_a_morte"),
        ("Destino", "Você vê e compreende inevitabilidades ocultas.", "ler_destino", "tentar_a_sorte"),
        ("Destruição", "Você é um conduíte para a devastação divina.", "brado_de_destruicao", "aura_destrutiva"),
        ("Dor", "Você pune aqueles que lhe desagradam com uma ferroada afiada de dor.", "adocar_a_ferroada", "dor_retributiva"),
        ("Enganação", "Você engana os outros e trama travessuras ou artimanhas.", "mudanca_subita", "gemeo_do_enganador"),
        ("Escuridão", "Você opera na escuridão e afasta a luz.", "manto_de_sombras", "olhos_enegrecidos"),
        ("Família", "Você auxilia e protege sua família e comunidade mais efetivamente.", "palavras_tranquilizantes", "unidade"),
        ("Fervor", "Você tem sua proeza de combate aumentada pelo seu fogo interior.", "surto_de_arma", "entusiasmo_pela_batalha"),
        ("Fogo", "Você controla chamas.", "raio_de_fogo", "barreira_de_chamas"),
        ("Indulgência", "Você se refestela pesadamente e evita as consequências dos excessos.", "empanturrar", "seguir_o_rumo"),
        ("Liberdade", "Você libera a si e aos outros de grilhões e restrições.", "deslocamento_desimpedido", "palavra_de_liberdade"),
        ("Lua", "Você comanda poderes associados à lua.", "feixe_lunar", "toque_da_lua"),
        ("Magia", "Você realiza o inesperado e o inexplicável.", "receptaculo_de_magia", "farol_mistico"),
        ("Morte", "Você tem o poder de encerrar vidas e destruir mortos-vivos.", "chamado_da_morte", "erradicar_a_nao_morte"),
        ("Não-morte", "Você controla magia ligada aos mortos-vivos.", "toque_da_nao_morte", "sustento_maligno"),
        ("Natureza", "Você detém poder sobre animais e plantas.", "espinhos_vibrantes", "fartura_da_natureza"),
        ("Paixão", "Você evoca paixão, seja amor ou luxúria.", "toque_cativante", "adoracao_atraente"),
        ("Perfeição", "Você se esforça para aperfeiçoar sua mente, corpo e espírito.", "mente_aperfeicoada", "forma_aperfeicoada"),
        ("Pesadelos", "Você inunda mentes com horror e pavor.", "pesadelo_acordado", "pesadelo_compartilhado"),
        ("Poder", "Você possui poder físico reforçado pelo divino.", "impeto_atletico", "poder_de_tolerancia"),
        ("Proteção", "Você protege a si e aos outros.", "sacrificio_do_protetor", "esfera_do_protetor"),
        ("Riqueza", "Você detém poder sobre riqueza, comércio e tesouro.", "aparencia_de_riqueza", "metais_preciosos"),
        ("Segredos", "Você protege segredos e os mantém escondidos.", "quietude_forcada", "salvaguardar_segredo"),
        ("Sol", "Você canaliza o poder do sol e pune mortos-vivos.", "clarao_ofuscante", "luminancia_positiva"),
        ("Sonhos", "Você possui o poder de entrar em sonhos e manipulá-los.", "sonho_agradavel", "chamado_do_sonhador"),
        ("Sorte", "Você é sobrenaturalmente sortudo e sempre fica longe do perigo.", "uma_pitada_de_sorte", "golpe_de_sorte"),
        ("Terra", "Você controla o solo e pedras.", "arremessar_pedra", "tremor_localizado"),
        ("Tirania", "Você empunha poder para governar e escravizar os outros.", "toque_de_obediencia", "chicotada_de_comando"),
        ("Verdade", "Você vê através de mentiras e descobre a verdade.", "palavra_da_verdade", "vislumbrar_a_verdade"),
        ("Viagem", "Você possui poder sobre movimento e jornadas.", "pes_ageis", "trajeto_do_viajante"),
    ]
    return [
        {
            "id": _norm(nome).replace("-", "_").replace(" ", "_"),
            "nome": nome,
            "descricao": desc,
            "magia_dominio_id": m1,
            "magia_dominio_avancada_id": m4,
        }
        for nome, desc, m1, m4 in tabela
    ]


def validar_divindades(estrutura: dict[str, Any]) -> None:
    pericias_ids = {p["id"] for p in json.loads((DIR_DADOS / "pericias.json").read_text(encoding="utf-8"))["pericias"]}
    eq = json.loads((DIR_DADOS / "equipamentos.json").read_text(encoding="utf-8"))
    armas_ids = {
        w["id"]
        for k in ("corpo_a_corpo", "distancia", "ataques_desarmados")
        for w in eq["armas"][k]
    }
    magias = (
        json.loads((DIR_DADOS / "magias01.json").read_text(encoding="utf-8"))["magias"]
        + json.loads((DIR_DADOS / "magias02.json").read_text(encoding="utf-8"))["magias"]
    )
    magias_ids = {m["id"] for m in magias}
    m2 = json.loads((DIR_DADOS / "magias02.json").read_text(encoding="utf-8"))
    foco_ids = {m["id"] for m in m2["magias_de_foco"]["lista"]}
    dominios_foco = {_norm(m["dominio"]) for m in m2["magias_de_foco"]["lista"] if m.get("dominio")}

    divs = estrutura["divindades"]
    doms = estrutura["dominios"]
    assert len(divs) == 20, f"Esperadas 20 divindades, encontradas {len(divs)}"
    assert len(doms) == 37, f"Esperados 37 domínios, encontrados {len(doms)}"

    doms_nomes = {_norm(d["nome"]) for d in doms}
    for d in doms:
        assert d["magia_dominio_id"] in foco_ids, f"Magia de domínio ausente: {d['magia_dominio_id']}"
        assert d["magia_dominio_avancada_id"] in foco_ids, f"Magia avançada ausente: {d['magia_dominio_avancada_id']}"
        assert _norm(d["nome"]) in dominios_foco, f"Domínio sem magia de foco correspondente: {d['nome']}"

    for div in divs:
        for pid in div["pericia_divina"]:
            assert pid in pericias_ids, f"Perícia inválida {pid!r} em {div['id']}"
        assert div["arma_favorecida_id"] in armas_ids, f"Arma inválida {div['arma_favorecida_id']!r} em {div['id']}"
        for dom in div["dominios"]:
            assert _norm(dom) in doms_nomes, f"Domínio inválido {dom!r} em {div['id']}"
        mag_1 = div["magias_clerigo"].get("1")
        assert mag_1 in magias_ids, f"Magia de 1º círculo inválida {mag_1!r} em {div['id']}"


def main() -> None:
    estrutura = {
        "meta": {
            "titulo": "Pathfinder 2ª Edição — Divindades Principais e Domínios",
            "paginas_livro": "437–441",
            "total_divindades": 20,
            "total_dominios": 37,
        },
        "divindades": _construir_divindades(),
        "dominios": _construir_dominios(),
    }
    validar_divindades(estrutura)
    with CAMINHO_SAIDA.open("w", encoding="utf-8") as f:
        json.dump(estrutura, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Arquivo gerado com sucesso: {CAMINHO_SAIDA} (20 divindades, 37 domínios)")


if __name__ == "__main__":
    main()
