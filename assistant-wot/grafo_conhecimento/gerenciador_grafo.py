from rdflib import Graph, Namespace
from rdflib.namespace import SKOS
from rdflib import URIRef, Literal
from typing import List, Dict
from dotenv import load_dotenv
import re
import os
import openai

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
EX = Namespace("http://example.org/")

# Criar e carregar o grafo de conhecimento
g = Graph()
g.parse("grafo_conhecimento/grafo.ttl", format="ttl")
g.bind("ex", EX)

# Load environment variables from a .env file
load_dotenv()

# Configurar sua chave da API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def consultar_frase(frase_usuario, metadados):
    """
    Consulta o grafo buscando uma frase levando em conta metadados (como localização).
    """
    if isinstance(metadados, str):
        metadados = {"localizacao": metadados}

    frase_usuario = frase_usuario.lower().strip()
    localizacao = metadados.get("localizacao", "").lower().strip()

    print(f"Buscando frase: '{frase_usuario}' com local: '{localizacao}'")

    for conceito in g.subjects(SKOS.prefLabel, None):
        label = g.value(conceito, SKOS.prefLabel)
        local = g.value(conceito, EX.temLocal)

        if label and local:
            label_str = str(label).lower().strip()
            local_str = str(g.value(local, SKOS.prefLabel)).lower().strip() if g.value(local, SKOS.prefLabel) else ""

            if frase_usuario == label_str and localizacao == local_str:
                return str(conceito)

    return None

def buscar_similaridade(frase, metadados):
    """
    Usa a API do ChatGPT para verificar quais conceitos no grafo têm relação com a frase e o metadado de localização.
    Retorna uma lista de URIs de conceitos relacionados.
    """
    localizacao = metadados.get("localizacao", "desconhecida")

    # Coletar todos os conceitos do grafo com seus metadados relevantes
    conceitos = []
    for conceito in g.subjects(predicate=SKOS.prefLabel):
        label = g.value(conceito, SKOS.prefLabel)
        local = g.value(conceito, EX.temLocal)
        processo = g.value(conceito, EX.temProcesso)

        conceitos.append({
            "uri": str(conceito),
            "label": str(label),
            "local": str(local) if local else "nenhum",
            "processo": str(processo) if processo else "nenhum"
        })

    if not conceitos:
        return []

    # Criar um prompt para o ChatGPT decidir quais conceitos são relevantes
    prompt = (
        f"Abaixo está uma lista de conceitos com suas URIs, frases e localizações.\n"
        f"Frase do usuário: '{frase}'\n"
        f"Localização: '{localizacao}'\n\n"
        f"Para cada conceito listado, avalie se ele tem relação com a frase e a localização fornecida.\n"
        f"Retorne **apenas uma lista com as URIs dos CONCEITOS mais relacionados**, não pode retornar frases e localizações.\n"
        f"Se não houver nenhum conceito relacionado, retorne uma lista vazia.\n"
        f"Não faça associações desnecessárias.\n\n"
    )

    for c in conceitos:
        prompt += f"- URI: {c['uri']}, Label: {c['label']}, Local: {c['local']}, Processo: {c['processo']}\n"

    # Chamada à API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente que ajuda a interpretar comandos de texto para controlar dispositivos."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=200
    )

    # Processar resposta
    content = response["choices"][0]["message"]["content"]
    print(content)
    
    # Extrair URIs (esperando que ele devolva uma lista tipo: [ "http://example.org/ApagarLuzQuarto", ... ])
    try:
    # Tenta extrair todas as URIs em formato de lista
        uris = re.findall(r'http[s]?://[^\s,\]]+', content)
        return uris
    except Exception as e:
        print(f"Erro ao extrair URIs: {e}")
        return []

def adicionar_frase(uri, frase):
    conceito_uri = URIRef(uri)

    # Verifica se a URI existe no grafo
    if (uri, None, None) not in g:
        Exception("URI não foi encontrado!")

    # Adiciona como altLabel (rótulo alternativo)
    g.add((conceito_uri, SKOS.altLabel, Literal(frase)))

    # Salvar o grafo de volta no arquivo TTL
    g.serialize(destination="grafo_conhecimento/grafo.ttl", format="turtle")

import openai

def pesquisar_sugestoes(things_descriptions: List[Dict], frase: str, localizacao: str) -> List[Dict]:
    # Aqui vamos gerar a consulta para o GPT
    prompt = f"""
    Considerando o seguinte contexto de Things (dispositivos inteligentes):

    {things_descriptions}

    O usuário fez a seguinte pergunta: "{frase}"

    Baseado nisso, por favor, sugira uma lista de ações possíveis que o usuário possa estar procurando. Para cada ação, forneça as seguintes informações:
    - prefLabel: Nome da ação.
    - altLabel: Sinônimos ou formas alternativas de descrever a ação.
    - description: Descrição da ação.
    - endpoint: URL base do Thing.
    - interaction: A rota para acionar a ação.
    - method: O método HTTP (POST, GET, PUT, DELETE).
    
    Exemplo de resposta:

    [
      {
        "prefLabel": "Ligar TV",
        "altLabel": ["ligar a televisão", "ativar TV"],
        "description": "Ligar a TV através da interface de controle.",
        "endpoint": "http://192.168.0.101:8080/things/tv",
        "interaction": "/actions/toggle",
        "method": "POST"
      },
      {
        "prefLabel": "Desligar TV",
        "altLabel": ["desligar a televisão", "desativar TV"],
        "description": "Desligar a TV através da interface de controle.",
        "endpoint": "http://192.168.0.101:8080/things/tv",
        "interaction": "/actions/toggle",
        "method": "POST"
      }
    ]
    """

    # Chamada para a API GPT-3 para obter as sugestões
    resposta = openai.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=500,
        temperature=0.5,
    )

    # Processando a resposta do GPT-3
    sugestoes = resposta.choices[0].text.strip()

    print(sugestoes)

    # Convertendo a resposta para um formato utilizável (lista de dicionários)
    try:
        sugestoes_lista = eval(sugestoes)  # Converte a string de resposta para uma lista de dicionários
    except Exception as e:
        print(f"Erro ao processar as sugestões: {e}")
        return []

    # Formatando as sugestões em uma lista de dicionários com as informações necessárias
    sugestoes_processadas = []
    for sugestao in sugestoes_lista:
        sugestao_formatada = {
            "prefLabel": sugestao.get("prefLabel"),
            "altLabel": sugestao.get("altLabel", []),
            "description": sugestao.get("description"),
            "endpoint": sugestao.get("endpoint"),
            "interaction": sugestao.get("interaction"),
            "method": sugestao.get("method")
        }
        sugestoes_processadas.append(sugestao_formatada)

    return sugestoes_processadas
