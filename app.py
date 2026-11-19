"""Aplicação Flask e API REST do Gerador Procedural de Fichas Pathfinder 2E."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from motor import ErroValidacao, carregar_dados, gerar_personagem, listar_opcoes_criacao

app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/")
def index():
    """Página simples de teste interativo da Etapa 3."""
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
            "resumo_proposta": c["resumo_proposta"],
        }
        for c in dados.conceitos_da_classe(classe_id)
    ]
    return jsonify({"classe_id": classe_id, "conceitos": conceitos})


@app.post("/api/gerar")
def api_gerar():
    """Gera uma ficha de personagem de 1º nível em JSON a partir das escolhas do usuário."""
    payload = request.get_json(silent=True)
    if payload is None:
        payload = request.form.to_dict() if request.form else {}
    if not isinstance(payload, dict):
        return jsonify({"erro": "Corpo da requisição inválido; esperado objeto JSON."}), 400

    campos_obrigatorios = ("ancestralidade_id", "heranca_id", "classe_id", "conceito_id")
    faltantes = [c for c in campos_obrigatorios if not str(payload.get(c, "")).strip()]
    if faltantes:
        return jsonify({"erro": f"Campos obrigatórios ausentes: {', '.join(faltantes)}."}), 400

    nivel_raw = payload.get("nivel", 1)
    try:
        nivel = int(nivel_raw)
    except (TypeError, ValueError):
        return jsonify({"erro": f"Valor inválido para 'nivel': {nivel_raw!r}."}), 400

    try:
        resultado = gerar_personagem(
            ancestralidade_id=str(payload["ancestralidade_id"]).strip(),
            heranca_id=str(payload["heranca_id"]).strip(),
            classe_id=str(payload["classe_id"]).strip(),
            conceito_id=str(payload["conceito_id"]).strip(),
            biografia_id=payload.get("biografia_id"),
            nome_personagem=payload.get("nome_personagem"),
            nome_jogador=str(payload.get("nome_jogador") or ""),
            nivel=nivel,
            seed=payload.get("seed"),
        )
    except ErroValidacao as exc:
        return jsonify({"erro": str(exc)}), 400

    return jsonify(resultado), 200


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
