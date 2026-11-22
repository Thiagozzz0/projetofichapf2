"""Aplicação Flask e API REST do Gerador Procedural de Fichas Pathfinder 2E."""

from __future__ import annotations

import os
from typing import Any

from flask import Flask, Response, jsonify, render_template, request

from motor import (
    CLASSES_DIVINDADE_OBRIGATORIA,
    ErroValidacao,
    carregar_dados,
    divindades_compativeis_conceito,
    exportar_ficha_docx,
    exportar_ficha_txt,
    gerar_personagem,
    listar_opcoes_criacao,
    nome_arquivo_seguro,
)

app = Flask(__name__, static_folder="templates/static", static_url_path="/static")
app.json.ensure_ascii = False


def _extrair_payload() -> dict[str, Any] | None:
    payload = request.get_json(silent=True)
    if payload is None:
        payload = request.form.to_dict() if request.form else {}
    return payload if isinstance(payload, dict) else None


def _gerar_a_partir_payload(payload: dict[str, Any]) -> dict[str, Any]:
    campos_obrigatorios = ("ancestralidade_id", "heranca_id", "classe_id", "conceito_id")
    faltantes = [c for c in campos_obrigatorios if not str(payload.get(c, "")).strip()]
    if faltantes:
        raise ErroValidacao(f"Campos obrigatórios ausentes: {', '.join(faltantes)}.")

    nivel_raw = payload.get("nivel", 1)
    try:
        nivel = int(nivel_raw)
    except (TypeError, ValueError) as exc:
        raise ErroValidacao(f"Valor inválido para 'nivel': {nivel_raw!r}.") from exc

    return gerar_personagem(
        ancestralidade_id=str(payload["ancestralidade_id"]).strip(),
        heranca_id=str(payload["heranca_id"]).strip(),
        classe_id=str(payload["classe_id"]).strip(),
        conceito_id=str(payload["conceito_id"]).strip(),
        biografia_id=payload.get("biografia_id"),
        divindade_id=payload.get("divindade_id"),
        nome_personagem=payload.get("nome_personagem"),
        nome_jogador=str(payload.get("nome_jogador") or ""),
        nivel=nivel,
        seed=payload.get("seed"),
    )


def _resolver_resultado_para_exportacao(payload: dict[str, Any]) -> dict[str, Any]:
    candidato = payload.get("resultado") if isinstance(payload.get("resultado"), dict) else payload
    if isinstance(candidato, dict) and isinstance(candidato.get("ficha"), dict):
        ficha = candidato["ficha"]
        if isinstance(ficha.get("cabecalho"), dict) and isinstance(ficha.get("atributos"), dict):
            return candidato
        raise ErroValidacao("Estrutura de ficha inválida para exportação.")
    return _gerar_a_partir_payload(payload)


def _resposta_download(
    conteudo: str | bytes,
    mimetype: str,
    extensao: str,
    resultado: dict[str, Any],
) -> Response:
    cab = resultado["ficha"]["cabecalho"]
    nome_arq = nome_arquivo_seguro(
        cab.get("nome_personagem"),
        cab.get("classe"),
        int(cab.get("nivel") or 1),
        extensao,
    )
    resp = Response(conteudo, mimetype=mimetype)
    resp.headers["Content-Disposition"] = f'attachment; filename="{nome_arq}"'
    return resp


@app.get("/")
def index():
    """Interface principal da Etapa 4 (Criação e Ficha Oficial PF2E)."""
    return render_template("index.html")


@app.get("/api/saude")
def api_saude():
    """Verifica disponibilidade do serviço e integridade dos dados carregados."""
    dados = carregar_dados()
    return jsonify(
        {
            "status": "ok",
            "ancestralidades": len(dados.ancestralidades),
            "biografias": len(dados.biografias),
            "classes": len(dados.classes),
            "conceitos": len(dados.conceitos),
            "pericias": len(dados.pericias),
            "magias": len(dados.magias),
            "divindades": len(dados.divindades),
        }
    )


@app.get("/api/opcoes")
def api_opcoes():
    """Retorna todas as ancestralidades, biografias, classes e conceitos disponíveis."""
    return jsonify(listar_opcoes_criacao())


@app.get("/api/ancestralidades/<ancestralidade_id>/herancas")
def api_herancas_por_ancestralidade(ancestralidade_id: str):
    """Lista as heranças válidas para a ancestralidade informada."""
    dados = carregar_dados()
    anc = dados.ancestralidades.get(ancestralidade_id)
    if not anc:
        return jsonify({"erro": f"Ancestralidade não encontrada: '{ancestralidade_id}'."}), 404
    herancas = [{"id": h["id"], "nome": h["nome"], "descricao": h["descricao"]} for h in anc["herancas"]]
    return jsonify({"ancestralidade_id": ancestralidade_id, "herancas": herancas})


@app.get("/api/classes/<classe_id>/conceitos")
def api_conceitos_por_classe(classe_id: str):
    """Lista os conceitos/subclasses procedurais válidos para a classe informada."""
    dados = carregar_dados()
    classe = dados.classes.get(classe_id)
    if not classe:
        return jsonify({"erro": f"Classe não encontrada: '{classe_id}'."}), 404
    conceitos = [
        {
            "id": c["id"],
            "nome": c["nome"],
            "titulo_completo": c["titulo_completo"],
            "subclasse_oficial_id": c["subclasse_oficial_id"],
            "subclasse_oficial_nome": c["subclasse_oficial_nome"],
            "subclasses_oficiais_candidatas": c.get(
                "subclasses_oficiais_candidatas", [c["subclasse_oficial_id"]]
            ),
            "subclasses_oficiais_nomes": c.get(
                "subclasses_oficiais_nomes", [c["subclasse_oficial_nome"]]
            ),
            "resumo_proposta": c["resumo_proposta"],
            "sinergia_mecanica": c.get("sinergia_mecanica", ""),
            "divindades_compativeis_ids": divindades_compativeis_conceito(dados, classe_id, c),
        }
        for c in dados.conceitos_da_classe(classe_id)
    ]
    return jsonify(
        {
            "classe_id": classe_id,
            "divindade_obrigatoria": classe_id in CLASSES_DIVINDADE_OBRIGATORIA,
            "conceitos": conceitos,
        }
    )


@app.post("/api/gerar")
def api_gerar():
    """Gera uma ficha de personagem de 1º nível em JSON a partir das escolhas do usuário."""
    payload = _extrair_payload()
    if payload is None:
        return jsonify({"erro": "Corpo da requisição inválido; esperado objeto JSON."}), 400

    try:
        resultado = _gerar_a_partir_payload(payload)
    except ErroValidacao as exc:
        return jsonify({"erro": str(exc)}), 400

    return jsonify(resultado), 200


@app.post("/api/exportar/txt")
def api_exportar_txt():
    """Exporta a ficha (já gerada ou gerada sob demanda) em texto plano `.txt` UTF-8."""
    payload = _extrair_payload()
    if payload is None:
        return jsonify({"erro": "Corpo da requisição inválido; esperado objeto JSON."}), 400

    try:
        resultado = _resolver_resultado_para_exportacao(payload)
        conteudo_txt = exportar_ficha_txt(resultado)
    except (ErroValidacao, KeyError, TypeError) as exc:
        return jsonify({"erro": str(exc)}), 400

    return _resposta_download(conteudo_txt, "text/plain; charset=utf-8", "txt", resultado)


@app.post("/api/exportar/docx")
def api_exportar_docx():
    """Exporta a ficha (já gerada ou gerada sob demanda) em documento `.docx` (OOXML)."""
    payload = _extrair_payload()
    if payload is None:
        return jsonify({"erro": "Corpo da requisição inválido; esperado objeto JSON."}), 400

    try:
        resultado = _resolver_resultado_para_exportacao(payload)
        conteudo_docx = exportar_ficha_docx(resultado)
    except (ErroValidacao, KeyError, TypeError) as exc:
        return jsonify({"erro": str(exc)}), 400

    return _resposta_download(
        conteudo_docx,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "docx",
        resultado,
    )


if __name__ == "__main__":
    debug_ativo = os.environ.get("FLASK_DEBUG", "0").strip().lower() in {"1", "true", "yes"}
    app.run(debug=debug_ativo, host="127.0.0.1", port=5000)
