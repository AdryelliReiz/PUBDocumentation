from flask import Flask, request, render_template, jsonify
from processador_frases import processar_frase
from grafo_conhecimento.gerenciador_grafo import adicionar_frase, consulta_componente
from utils import executar_conceito
import json

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html"), 200

@app.route("/processar", methods=["GET"])
def processar():
    frase = request.args.get("frase")
    localizacao = request.args.get("localizacao", {})
    resultado = processar_frase(frase, localizacao)
    return jsonify(resultado)

@app.route("/adicionar-informacao", methods=["POST"])
def adicionar_informacao():
    """
    Adiciona uma nova frase como rótulo alternativo a um componente específico
    de uma Thing no grafo de conhecimento.
    """
    dados = request.get_json()
    frase = dados.get("frase", "").strip().lower()
    thing_uri = dados.get("thing_uri")
    componente_name = dados.get("componente_name")
    componente_type = dados.get("componente_type")

    if not frase or not thing_uri or not componente_name or not componente_type:
        return jsonify({
            "status": 400,
            "type": "ERRO",
            "message": "Dados incompletos. São necessários: 'frase', 'thing_uri', 'componente_name' e 'componente_type'."
        }), 400

    try:
        adicionar_frase(thing_uri, frase, componente_type, componente_name)

        return jsonify({
            "status": 200,
            "type": "SUCESSO",
            "message": f"A frase '{frase}' foi associada com sucesso ao componente '{componente_name}' da Thing '{thing_uri}'."
        }), 200
    except Exception as e:
        print(f"Erro ao adicionar informação: {e}")
        return jsonify({
            "status": 500,
            "type": "ERRO",
            "message": f"Ocorreu um erro interno: {str(e)}."
        }), 500
    
@app.route("/executar-acao", methods=["GET"])
def executar():
    """
    Executa uma ação em uma Thing específica.
    """
    thing_uri = request.args.get("thing_uri")
    componente_name = request.args.get("componente_name")
    componente_type = request.args.get("componente_type")


    if not thing_uri or not componente_name:
        return jsonify({
            "status": 400,
            "type": "ERRO",
            "message": "Parâmetros 'thing_uri', 'componente_name' e 'componente_type' são necessários."
        }), 400

    conceito = consulta_componente(thing_uri, componente_name, componente_type)

    if not conceito:
        return jsonify({
            "status": 404,
            "type": "ERRO",
            "message": f"Nenhum componente encontrado com o nome '{componente_name}' na Thing '{thing_uri}'."
        }), 404
    
    resultado = executar_conceito(conceito)
    return {
        "status": resultado['status'],
        "message": resultado['message'],
        "type": "CONCEITO",
        "data": conceito
    }, 200

def iniciar_app():
    app.run(host="0.0.0.0", port=8000)