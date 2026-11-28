"""Cálculos de combate, Pontos de Vida, Classe de Armadura, BpA, ataques e habilidades de C&C."""

from __future__ import annotations

import random
import re
from typing import Any

REGRAS_PV: dict[str, dict[str, str]] = {
    "padrao": {
        "id": "padrao",
        "nome": "Padrão (rolar DV a cada nível)",
        "descricao": "Rola o Dado de Vida da classe + Modificador de Constituição em cada nível (mínimo 1 por nível).",
    },
    "opcional_1_maximo_n1": {
        "id": "opcional_1_maximo_n1",
        "nome": "Opcional #1 (Máximo no 1º Nível)",
        "descricao": "Recebe o valor máximo do Dado de Vida no 1º nível + Mod CON; rola nos níveis 2–10.",
    },
    "opcional_2_multiplas_rolagens_con": {
        "id": "opcional_2_multiplas_rolagens_con",
        "nome": "Opcional #2 (Múltiplas Rolagens por CON)",
        "descricao": "Rola o DV (1 + bônus de CON) vezes em cada nível e fica com o maior resultado + Mod CON.",
    },
    "media_fixa": {
        "id": "media_fixa",
        "nome": "Média Fixa (sem aleatoriedade)",
        "descricao": "Máximo no 1º nível e média arredondada para cima nos níveis 2–10 + Mod CON.",
    },
}


def _faces_dado(dado_vida: str) -> int:
    m = re.search(r"d(\d+)", str(dado_vida), re.IGNORECASE)
    if not m:
        raise ValueError(f"Dado de vida inválido: {dado_vida!r}")
    return int(m.group(1))


def obter_linha_progressao(classe: dict[str, Any], nivel: int) -> dict[str, Any]:
    """Retorna a linha de progressão (bpa, ppe, pv, habilidades) para o nível (1–24)."""
    if nivel < 1 or nivel > 24:
        raise ValueError(f"Nível fora da faixa suportada (1–24): {nivel}")
    prog = classe.get("progressao", [])
    for linha in prog:
        if int(linha["nivel"]) == nivel:
            return linha
    raise ValueError(f"Nível {nivel} não encontrado na progressão de {classe['id']}")


def obter_proximo_ppe(classe: dict[str, Any], nivel: int) -> int | None:
    """Retorna o PPE necessário para atingir o próximo nível (ou None no nível 24)."""
    if nivel >= 24:
        return None
    prox = obter_linha_progressao(classe, nivel + 1)
    return int(prox["ppe"])


def calcular_pv(
    classe: dict[str, Any],
    nivel: int,
    mod_con: int,
    regra_pv: str = "opcional_1_maximo_n1",
    pv_por_nivel_manual: list[int] | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    """Calcula PV total e por nível (1º ao 24º), seguindo dado_vida (N1–10) e pv_apos_nivel_10 (N11+)."""
    if regra_pv not in REGRAS_PV:
        raise ValueError(f"Regra de PV inválida: {regra_pv!r}. Use uma de {list(REGRAS_PV)}")

    faces = _faces_dado(classe["dado_vida"])
    pv_pos_10 = int(classe.get("pv_apos_nivel_10", 2))
    rng = random.Random(seed)

    por_nivel: list[dict[str, Any]] = []
    for nv in range(1, nivel + 1):
        if pv_por_nivel_manual and nv <= len(pv_por_nivel_manual) and pv_por_nivel_manual[nv - 1] is not None:
            ganho = max(1, int(pv_por_nivel_manual[nv - 1]))
            por_nivel.append({"nivel": nv, "rolagem": None, "mod_con": mod_con, "pv": ganho, "origem": "manual"})
            continue

        if nv > 10:
            # Em C&C após o 10º nível ganha-se PV fixo por nível sem aplicar Mod CON
            por_nivel.append({"nivel": nv, "rolagem": pv_pos_10, "mod_con": 0, "pv": pv_pos_10, "origem": "fixo_pos_10"})
            continue

        if regra_pv == "opcional_1_maximo_n1" and nv == 1:
            rol = faces
        elif regra_pv == "media_fixa":
            rol = faces if nv == 1 else (faces // 2) + 1
        elif regra_pv == "opcional_2_multiplas_rolagens_con":
            tentativas = max(1, 1 + max(0, mod_con))
            rol = max(rng.randint(1, faces) for _ in range(tentativas))
        else:
            rol = rng.randint(1, faces)

        ganho = max(1, rol + mod_con)
        por_nivel.append({"nivel": nv, "rolagem": rol, "mod_con": mod_con, "pv": ganho, "origem": regra_pv})

    total = sum(x["pv"] for x in por_nivel)
    return {
        "dado_vida": classe["dado_vida"],
        "pv_apos_nivel_10": pv_pos_10,
        "regra_pv": regra_pv,
        "total": total,
        "por_nivel": por_nivel,
    }


def calcular_ca(
    mod_des: int,
    armadura: dict[str, Any] | None = None,
    escudo: dict[str, Any] | None = None,
    elmo: dict[str, Any] | None = None,
    bonus_magia: int = 0,
    bonus_var: int = 0,
    sobrecarregado: bool = False,
) -> dict[str, Any]:
    """Calcula CA oficial de C&C: 10 + Armadura + Escudo + Mod DES + Magia + Var."""
    bonus_arm = int(armadura.get("ca", 0)) if armadura else 0
    bonus_esc = int(escudo.get("ca", 0)) if escudo else 0
    mod_des_efetivo = 0 if (sobrecarregado and mod_des > 0) else mod_des

    total = 10 + bonus_arm + bonus_esc + mod_des_efetivo + int(bonus_magia) + int(bonus_var)
    return {
        "total": total,
        "base": 10,
        "armadura": bonus_arm,
        "escudo": bonus_esc,
        "mod_destreza": mod_des_efetivo,
        "magia": int(bonus_magia),
        "var": int(bonus_var),
        "armadura_nome": armadura["nome"] if armadura else "Nenhuma",
        "escudo_nome": escudo["nome"] if escudo else "Nenhum",
        "elmo_nome": elmo["nome"] if elmo else "Nenhum",
        "perdeu_des_por_sobrecarga": bool(sobrecarregado and mod_des > 0),
    }


def calcular_ataques(
    armas: list[dict[str, Any]],
    bpa: int,
    mod_for: int,
    mod_des: int,
    bonus_magia: int = 0,
    bonus_var: int = 0,
) -> list[dict[str, Any]]:
    """Monta os blocos de ataque e dano para cada arma equipada."""
    resultado: list[dict[str, Any]] = []
    for arma in armas:
        cat = arma.get("categoria", "")
        is_projetil = cat == "armas_projeteis"
        mod_atq = mod_des if is_projetil else mod_for
        # Armas de arremesso / corpo a corpo somam FOR no dano; projéteis (arcos/bestas) não somam FOR
        mod_dano = 0 if is_projetil else mod_for
        total_atq = int(bpa) + mod_atq + int(bonus_var) + int(bonus_magia)

        dano_base = str(arma.get("dano", "1d4"))
        mod_dano_total = mod_dano + int(bonus_var) + int(bonus_magia)
        if mod_dano_total > 0:
            total_dano = f"{dano_base}+{mod_dano_total}"
        elif mod_dano_total < 0:
            total_dano = f"{dano_base}{mod_dano_total}"
        else:
            total_dano = dano_base

        resultado.append(
            {
                "id": arma["id"],
                "nome": arma["nome"],
                "tipo": "distancia" if is_projetil else "corpo_a_corpo",
                "bpa": int(bpa),
                "mod_ataque": mod_atq,
                "var_ataque": int(bonus_var),
                "magia_ataque": int(bonus_magia),
                "total_ataque": total_atq,
                "dano_base": dano_base,
                "mod_dano": mod_dano,
                "var_dano": int(bonus_var),
                "magia_dano": int(bonus_magia),
                "total_dano": total_dano,
                "alcance": arma.get("distancia") or arma.get("alcance") or "Corpo a corpo",
            }
        )
    return resultado


def coletar_habilidades(
    raca: dict[str, Any],
    classe: dict[str, Any],
    nivel: int,
    linhagem_meio_elfo: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Coleta todas as habilidades raciais e todas as habilidades de classe até o nível atual."""
    hab_raca: list[dict[str, Any]] = []
    for traco in raca.get("tracos", []):
        hab_raca.append(
            {
                "nome": traco["nome"],
                "atributo_teste": traco.get("atributo_teste"),
                "descricao": traco.get("descricao", ""),
                "origem": raca["nome"],
            }
        )

    if raca["id"] == "meio_elfo":
        lin_id = linhagem_meio_elfo or "elfica"
        lin = raca.get("linhagens", {}).get(lin_id)
        if lin:
            for traco in lin.get("tracos", []):
                hab_raca.append(
                    {
                        "nome": traco["nome"],
                        "atributo_teste": traco.get("atributo_teste"),
                        "descricao": traco.get("descricao", ""),
                        "origem": f"{raca['nome']} ({lin['nome']})",
                    }
                )

    # Habilidades de classe desbloqueadas na progressão (níveis 1..nivel)
    hab_classe: list[dict[str, Any]] = []
    vistas: set[str] = set()
    mapa_desc_detalhada = {
        h["nome"].lower(): h.get("descricao", "") for h in classe.get("habilidades", [])
    }

    for linha in classe.get("progressao", []):
        nv = int(linha["nivel"])
        if nv > nivel:
            break
        for h in linha.get("habilidades", []):
            chave = h["nome"].lower()
            if chave in vistas:
                # Atualiza entrada existente se habilidade escalar em nível superior
                hab_classe.append(
                    {
                        "nivel": nv,
                        "nome": h["nome"],
                        "teste": h.get("teste"),
                        "resumo": h.get("resumo", ""),
                        "descricao": mapa_desc_detalhada.get(chave, h.get("resumo", "")),
                    }
                )
            else:
                vistas.add(chave)
                hab_classe.append(
                    {
                        "nivel": nv,
                        "nome": h["nome"],
                        "teste": h.get("teste"),
                        "resumo": h.get("resumo", ""),
                        "descricao": mapa_desc_detalhada.get(chave, h.get("resumo", "")),
                    }
                )

    return {
        "raca": hab_raca,
        "classe": hab_classe,
    }
