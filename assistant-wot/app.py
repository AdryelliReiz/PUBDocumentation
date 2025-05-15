from flask import Flask, request, render_template, jsonify
from processador_frases import processar_frase
from grafo_conhecimento.gerenciador_grafo import adicionar_frase, pesquisar_sugestoes
from thing_directory import buscar_things

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/processar", methods=["POST"])
def processar():
    dados = request.json
    frase = dados.get("frase")
    metadados = dados.get("metadados", {})  # localização, usuário, etc.
    resultado = processar_frase(frase, metadados)
    return jsonify(resultado)

@app.route("/adicionar-informacao", methods=["POST"])
def adicionar_informacao():
    dados = request.get_json()
    frase = dados.get("frase", "").strip().lower()
    sugestao_uri = dados.get("sugestao")

    if not frase or not sugestao_uri:
        return jsonify({"erro": "Dados incompletos"}), 400

    try:
        adicionar_frase(sugestao_uri, frase)

        return jsonify({"mensagem": f"A frase '{frase}' foi associada a {sugestao_uri} com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route("/pesquisa-avancada", methods=["POST"])
def pesquisa_avancado():
    dados = request.get_json()
    frase = dados.get("frase", "").strip().lower()
    metadados = dados.get("metadados", {})

    try:
        things_descriptions = buscar_things()
        print(things_descriptions)

        localizacao = metadados.get("localizacao", "")
        resposta = pesquisar_sugestoes(things_descriptions, frase, localizacao)
        return jsonify({"status": 200, "type": "SUGESTOES", "data": resposta})
        #if things_descriptions:
        #    localizacao = metadados.get("localizacao", "")
        #    resposta = pesquisar_sugestoes(things_descriptions, frase, localizacao)
        #    return jsonify({"status": 200, "type": "SUGESTOES", "data": resposta})
        #else:
        #    return jsonify({"status": 404, "data": {}})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route("/criar-informacao", methods=["POST"])
def criar():
    print("Criando informação...")

def iniciar_app():
    app.run(host="0.0.0.0", port=5000)