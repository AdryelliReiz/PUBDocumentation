from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Endpoint para fazer a consulta SPARQL
def execute_sparql(query):
    sparql_endpoint = "http://localhost:9999/blazegraph/sparql"  # Ajuste conforme seu endpoint SPARQL

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    params = {
        "query": query,
        "format": "json"  # Você pode ajustar o formato de resposta conforme necessário
    }

    try:
        response = requests.get(sparql_endpoint, headers=headers, params=params)
        response.raise_for_status()  # Verifica se houve erro na requisição HTTP
        return response.json()  # Retorna o JSON da resposta, ou um resultado adequado
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição SPARQL: {e}")
        return None

# Rota para inserir ou consultar dados (aqui exemplificado com PUT)
@app.route('/add_triple', methods=['PUT'])
def add_triple():
    data = request.json
    thing = data.get('thing')
    property = data.get('property')
    value = data.get('value')

    # Exemplo de consulta SPARQL para inserção de tripla
    query = f"""
    INSERT DATA {{
        <{thing}> <{property}> "{value}" .
    }}
    """

    # Executa a consulta SPARQL
    result = execute_sparql(query)
    
    if result:  # Se a consulta retornar algo (por exemplo, sucesso na inserção)
        return jsonify({'message': 'Tripla inserida com sucesso'}), 200
    else:
        return jsonify({'error': 'Erro ao inserir a tripla'}), 500

@app.route('/get_triple', methods=['GET'])
def get_triple():
    thing = request.args.get('thing')
    property = request.args.get('property')

    # Consulta SPARQL para recuperar a última tripla
    query = f"""
    SELECT ?value WHERE {{
        <{thing}> <{property}> ?value .
    }} ORDER BY DESC(?date) LIMIT 1
    """

    # Executa a consulta SPARQL
    result = execute_sparql(query)
    
    if result and 'results' in result:
        return jsonify(result['results']['bindings']), 200
    else:
        return jsonify({'error': 'Nenhum resultado encontrado'}), 404

if __name__ == "__main__":
    app.run(debug=True)
