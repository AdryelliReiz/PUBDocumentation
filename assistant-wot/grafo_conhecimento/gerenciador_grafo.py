from dotenv import load_dotenv
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import SKOS, RDF, XSD, DCTERMS
from typing import List, Dict
import re
import os
import openai
import json
import requests

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
DCTERMS = Namespace("http://purl.org/dc/terms/")

EX = Namespace("http://example.org/")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
SCHEMA1 = Namespace("http://schema.org/")
SAREF = Namespace("https://w3id.org/saref#")
OM = Namespace("http://www.ontology-of-units-of-measure.org/resource/om-2/")

WOT_HYPERMEDIA = Namespace("https://www.w3.org/2019/wot/hypermedia#")
WOT_TD = Namespace("https://www.w3.org/2019/wot/td#")
WOT_JSON_SCHEMA = Namespace("https://www.w3.org/2019/wot/json-schema#")
HTTP_METHOD = Namespace("http://www.w3.org/2011/http#")

g = Graph()
try:
    g.parse("grafo_conhecimento/grafo.ttl", format="ttl")
except Exception:
    os.makedirs("grafo_conhecimento", exist_ok=True)

g.bind("skos", SKOS)
g.bind("rdf", RDF)
g.bind("xsd", XSD)
g.bind("dcterms", DCTERMS)
g.bind("ex", EX)
g.bind("sosa", SOSA)
g.bind("schema1", SCHEMA1)
g.bind("saref", SAREF)
g.bind("om", OM)
g.bind("wot-hyp", WOT_HYPERMEDIA)
g.bind("wot-td", WOT_TD)
g.bind("wot-js", WOT_JSON_SCHEMA)
g.bind("httpm", HTTP_METHOD)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def consultar_frase(frase_usuario, metadados):
    print("Iniciando consulta de frase no grafo de conhecimento...")
    if isinstance(metadados, str):
        metadados = {"localizacao": metadados}

    frase_usuario_lower = frase_usuario.lower().strip()
    localizacao_usuario_lower = metadados.get("localizacao", "").lower().strip()

    print(f"Buscando frase: '{frase_usuario_lower}' na localização desejada: '{localizacao_usuario_lower}'")

    print(f"Grafo contem {len(g)} triplas.")

    # Iterar sobre todas as Things no grafo
    for thing_uri in g.subjects(RDF.type, WOT_TD.Thing):
        thing_id = str(thing_uri)
        print(f"\n--- Verificando Thing: {thing_id} ---")
        
        # Obter a localização associada a esta Thing
        local_recurso = g.value(thing_uri, SCHEMA1.location) 
        local_nome_no_grafo = ""
        if local_recurso:
            nome_place = g.value(local_recurso, SCHEMA1.name) 
            if nome_place:
                local_nome_no_grafo = str(nome_place).lower().strip()
        
        print(f"Localização da Thing no grafo: '{local_nome_no_grafo}'")

        # Comparar a localização da Thing com a localização fornecida pelo usuário
        if localizacao_usuario_lower: # Se o usuário especificou uma localização
            if localizacao_usuario_lower != local_nome_no_grafo:
                print(f"Localização não corresponde. Pulando esta Thing.")
                continue # Pula esta Thing e vai para a próxima
            else:
                print(f"Localização corresponde: '{local_nome_no_grafo}'")
        else:
            print(f"Nenhuma localização especificada pelo usuário. Processando esta Thing.")

        # Iterar sobre as ações da Thing
        for action_affordance in g.objects(thing_uri, WOT_TD.hasActionAffordance):
            action_name_node = g.value(action_affordance, WOT_TD.name)
            
            labels_to_check = set()
            if action_name_node:
                labels_to_check.add(str(action_name_node).lower().strip())
            for alt_label_node in g.objects(action_affordance, SKOS.altLabel):
                labels_to_check.add(str(alt_label_node).lower().strip())
            
            current_action_name = str(action_name_node) if action_name_node else "N/A"
            print(f"  Verificando ação: '{current_action_name}' (Labels: {labels_to_check})")

            # Verificar se a frase do usuário corresponde a um nome ou altLabel da ação
            if frase_usuario_lower in labels_to_check:
                print(f"  Frase '{frase_usuario_lower}' corresponde a uma label da ação '{current_action_name}'.")
                # Se a frase bate, busca os detalhes do formulário (form) da ação
                for form in g.objects(action_affordance, WOT_TD.hasForm):
                    method_node = g.value(form, HTTP_METHOD.methodName)
                    target_node = g.value(form, WOT_HYPERMEDIA.hasTarget)
                    
                    base_uri_node = g.value(thing_uri, WOT_TD.baseURI)
                    full_target_url = str(target_node)
                    
                    # Constrói a URL completa se o target for relativo e baseURI existir
                    if base_uri_node and not full_target_url.startswith("http"):
                        base_uri_str = str(base_uri_node).rstrip('/')
                        target_str = str(target_node).lstrip('/')
                        full_target_url = f"{base_uri_str}/{target_str}"

                    if method_node and target_node:
                        print(f"  Ação completa encontrada! Retornando detalhes.")
                        return {
                            "thing_id": thing_id,
                            "action_name": current_action_name,
                            "http_method": str(method_node),
                            "target_url": full_target_url
                        }
                print(f"  Ação '{current_action_name}' corresponde, mas não foram encontrados form/method/target válidos.")
            else:
                print(f"  Frase '{frase_usuario_lower}' NÃO corresponde à ação '{current_action_name}'.")

    print("Nenhum conceito ou ação correspondente encontrado no grafo.")
    return None
    
def buscar_similaridade(frase_usuario, localicacao):
    """
    Busca Things no grafo que se relacionem com a frase do usuário,
    filtrando por localização e comparando informações de suas ações e propriedades.
    Retorna uma lista de URIs das Things mais relevantes.
    """

    localizacao_usuario_lower = localicacao.lower().strip()

    things_para_analisar = []

    # Iterar sobre todas as Things no grafo
    for thing_uri in g.subjects(RDF.type, WOT_TD.Thing):
        thing_data = {
            "uri": str(thing_uri),
            "title": str(g.value(thing_uri, WOT_TD.title) or "Sem Título"),
            "location": "",
            "actions": [],
            "properties": []
        }

        # Obter localização da Thing
        for loc_node in g.objects(thing_uri, SCHEMA1.location):
            place_name = g.value(loc_node, SCHEMA1.name)
            if place_name:
                thing_data["location"] = str(place_name).lower().strip()
                break

        # Filtrar por localização antes de coletar mais dados
        if localizacao_usuario_lower and thing_data["location"] != localizacao_usuario_lower:
            continue

        # Coletar informações sobre ações
        for action_affordance in g.objects(thing_uri, WOT_TD.hasActionAffordance):
            action_name = str(g.value(action_affordance, WOT_TD.name) or "Sem Nome")
            action_description = str(g.value(action_affordance, WOT_TD.description) or "")
            alt_labels = [str(l) for l in g.objects(action_affordance, SKOS.altLabel)]
            
            thing_data["actions"].append({
                "name": action_name,
                "description": action_description,
                "alt_labels": alt_labels
            })

        # Coletar informações sobre propriedades
        for prop_affordance in g.objects(thing_uri, WOT_TD.hasPropertyAffordance):
            prop_name = str(g.value(prop_affordance, WOT_TD.name) or "Sem Nome")
            prop_description = str(g.value(prop_affordance, WOT_TD.description) or "")
            alt_labels = [str(l) for l in g.objects(prop_affordance, SKOS.altLabel)]

            thing_data["properties"].append({
                "name": prop_name,
                "description": prop_description,
                "alt_labels": alt_labels
            })
        
        things_para_analisar.append(thing_data)

    if not things_para_analisar:
        print("Nenhuma Thing encontrada que corresponda à localização ou sem dados para análise.")
        return []
    
    print("Things para analisar:")
    print(things_para_analisar)

    # Montar o prompt para o GPT
    prompt = (
        f"Abaixo estão descrições de dispositivos (Things) com suas ações e propriedades.\n"
        f"**Frase do usuário:** '{frase_usuario}'\n"
        f"**Localização desejada:** '{localizacao_usuario_lower if localizacao_usuario_lower else 'qualquer'}'\n\n"
        f"Sua tarefa é encontrar as **ações e/ou propriedades mais relevantes** que correspondam à frase e localização do usuário.\n"
        f"**Critérios de relevância:**\n"
        f"- Nomes de ações/propriedades, rótulos alternativos (alt_labels) ou descrições que correspondam à frase do usuário.\n"
        f"- A localização da Thing deve corresponder à localização desejada, se especificada.\n"
        f"Retorne **APENAS uma lista JSON válida, com as chaves e valores de string entre aspas duplas**. A lista deve conter os componentes (ações ou propriedades) mais relevantes, no seguinte formato:\n"
        f"[`{{\"thing_uri\": \"<uri_da_thing>\", \"componente_name\": \"<nome>\", \"componente_type\": \"action\"|\"property\", \"alt_labels\": [\"<all_alt_labels>\", ...]}}`, ...]\n"
        f"Não inclua nenhuma outra informação na resposta, apenas a lista. Se não houver componentes relevantes, retorne uma lista vazia `[]`.\n\n"
    )

    for thing in things_para_analisar:
        prompt += f"--- Thing: {thing['uri']} ---\n"
        prompt += f"  Título: {thing['title']}\n"
        prompt += f"  Localização: {thing['location'] if thing['location'] else 'não especificada'}\n"
        
        if thing['actions']:
            prompt += "  Ações:\n"
            for action in thing['actions']:
                prompt += f"    - Nome: {action['name']}, Descrição: {action['description']}, Alt Labels: {', '.join(action['alt_labels'])}\n"
        
        if thing['properties']:
            prompt += "  Propriedades:\n"
            for prop in thing['properties']:
                prompt += f"    - Nome: {prop['name']}, Descrição: {prop['description']}, Alt Labels: {', '.join(prop['alt_labels'])}\n"
        prompt += "\n" # Espaço entre Things

    try:
        response = openai.chat.completions.create(
            model="gpt-4o", # ou gpt-4, gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "Você é um assistente que identifica as ações e propriedades mais relevantes a partir de um comando de usuário e descrições de Things. Responda APENAS com uma lista JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        content = response.choices[0].message.content
        print(f"Resposta bruta do GPT: {content}")

        # Tenta parsear a resposta como uma lista JSON
        match = re.search(r"\[\s*{.*?}\s*]", content, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            print("Nenhuma lista JSON encontrada.")
            return []
            
    except Exception as e:
        print(f"Erro ao chamar a API da OpenAI ou processar a resposta: {e}")
        return []

def adicionar_frase(uri: str, frase: str, componente_type: str, componente_name: str):
    """
    Adiciona uma nova frase como skos:altLabel a um componente (ação ou propriedade)
    de uma Thing no grafo, garantindo que o componente exista.

    Args:
        uri (str): A URI da Thing a ser modificada.
        frase (str): A nova frase para ser adicionada como altLabel.
        componente_type (str): O tipo do componente ('action' ou 'property').
        componente_name (str): O nome (wot-td:name) do componente.
    """
    thing_uri = URIRef(uri)

    if (thing_uri, None, None) not in g:
        print(f"Erro: URI da Thing '{uri}' não encontrada no grafo. Nenhuma frase adicionada.")
        return

    found_component = None
    if componente_type == "action":
        for action_affordance in g.objects(thing_uri, WOT_TD.hasActionAffordance):
            if g.value(action_affordance, WOT_TD.name) == Literal(componente_name):
                found_component = action_affordance
                break
    elif componente_type == "property":
        for prop_affordance in g.objects(thing_uri, WOT_TD.hasPropertyAffordance):
            if g.value(prop_affordance, WOT_TD.name) == Literal(componente_name):
                found_component = prop_affordance
                break

    if found_component:
        if (found_component, SKOS.altLabel, Literal(frase)) in g:
            print(f"A frase '{frase}' já existe para o componente '{componente_name}'.")
        else:
            g.add((found_component, SKOS.altLabel, Literal(frase)))
            g.serialize(destination="grafo_conhecimento/grafo.ttl", format="turtle")
            print(f"Frase '{frase}' adicionada com sucesso ao componente '{componente_name}'.")
    else:
        print(f"Erro: Componente '{componente_name}' do tipo '{componente_type}' não foi encontrado na Thing '{uri}'.")

def consulta_componente(thing_uri, componente_name, componente_type):
    """
    Busca os detalhes de um componente específico (ação ou propriedade) de uma Thing
    no grafo, retornando uma estrutura de dados pronta para execução.

    Args:
        thing_uri (str): A URI da Thing.
        componente_name (str): O nome (wot-td:name) da ação ou propriedade.
        componente_type (str): O tipo do componente ('action' ou 'property').
    """
    thing_uri = URIRef(thing_uri)
    
    # Validação inicial da URI da Thing
    if (thing_uri, None, None) not in g:
        print(f"Erro: URI da Thing '{thing_uri}' não encontrada no grafo.")
        return None

    found_component = None
    if componente_type == "action":
        for action_affordance in g.objects(thing_uri, WOT_TD.hasActionAffordance):
            if g.value(action_affordance, WOT_TD.name) == Literal(componente_name):
                found_component = action_affordance
                break
    elif componente_type == "property":
        for prop_affordance in g.objects(thing_uri, WOT_TD.hasPropertyAffordance):
            if g.value(prop_affordance, WOT_TD.name) == Literal(componente_name):
                found_component = prop_affordance
                break
    
    if not found_component:
        print(f"Componente '{componente_name}' do tipo '{componente_type}' não encontrado na Thing '{thing_uri}'.")
        return None

    # Se o componente foi encontrado, busca o formulário (form) para obter os detalhes de execução
    for form in g.objects(found_component, WOT_TD.hasForm):
        method_node = g.value(form, HTTP_METHOD.methodName)
        target_node = g.value(form, WOT_HYPERMEDIA.hasTarget)
        
        # Constrói a URL completa
        base_uri_node = g.value(thing_uri, WOT_TD.baseURI)
        full_target_url = str(target_node)
        
        if base_uri_node and not full_target_url.startswith("http"):
            base_uri_str = str(base_uri_node).rstrip('/')
            target_str = str(target_node).lstrip('/')
            full_target_url = f"{base_uri_str}/{target_str}"

        # Verifica se temos método e URL, e retorna a estrutura de dados
        if method_node and target_node:
            return {
                "thing_id": str(thing_uri),
                "action_name": componente_name,
                "http_method": str(method_node),
                "target_url": full_target_url
            }

    print(f"Componente '{componente_name}' encontrado, mas sem um formulário de execução (form) válido.")
    return None

def adicionar_think_ao_grafo(think: Dict):
    if not isinstance(think, dict):
        raise ValueError("A entrada 'think' deve ser um dicionário JSON-LD.")

    thing_uri_str = think.get("id")
    if not thing_uri_str:
        raise ValueError("O Thing Description não possui um 'id'. Não é possível adicionar ao grafo.")
    thing_uri = URIRef(thing_uri_str)

    # Lógica para limpar triplas existentes da Thing
    nodes_to_clear = {thing_uri}
    queue = [thing_uri]
    visited = {thing_uri}

    while queue:
        current_node = queue.pop(0)
        for s, p, o in g.triples((current_node, None, None)):
            if isinstance(o, URIRef) and (str(o).startswith(thing_uri_str) or p in [WOT_TD.hasPropertyAffordance, WOT_TD.hasActionAffordance, WOT_TD.definesSecurityScheme, SCHEMA1.location]):
                if o not in visited:
                    nodes_to_clear.add(o)
                    visited.add(o)
                    queue.append(o)
            elif isinstance(o, BNode):
                if o not in visited:
                    nodes_to_clear.add(o)
                    visited.add(o)
                    queue.append(o)
    
    triples_to_remove = set()
    for node in nodes_to_clear:
        for s, p, o in g.triples((node, None, None)):
            triples_to_remove.add((s, p, o))
        for s, p, o in g.triples((None, None, node)):
            triples_to_remove.add((s, p, o))
    
    for t in triples_to_remove:
        g.remove(t)
    
    # Parsing e adição do Thing Description
    jsonld_str = json.dumps(think)
    g_temp_td = Graph()
    g_temp_td.parse(data=jsonld_str, format="json-ld")

    # Garante que a Thing é do tipo wot-td:Thing
    if (thing_uri, RDF.type, WOT_TD.Thing) not in g_temp_td:
        g_temp_td.add((thing_uri, RDF.type, WOT_TD.Thing))

    for triple in g_temp_td:
        g.add(triple)

    # Processamento de localização (se houver)
    if "position" in think.get("properties", {}):
        position_property_td = think["properties"]["position"]
        if position_property_td.get("forms") and position_property_td["forms"][0].get("href"):
            url = position_property_td["forms"][0]["href"]
            try:
                response = requests.get(url)
                response.raise_for_status()
                position_data = response.json()

                location_node_from_data = None
                try:
                    jsonld_position = json.dumps(position_data)
                    g_pos_temp = Graph()
                    g_pos_temp.parse(data=jsonld_position, format="json-ld")
                    for triple in g_pos_temp:
                        g.add(triple)
                    
                    for s_pos in g_pos_temp.subjects(RDF.type, SCHEMA1.Place):
                        location_node_from_data = s_pos
                        break
                    if not location_node_from_data:
                        for s_pos in g_pos_temp.subjects(RDF.type, SCHEMA1.GeoCoordinates):
                            location_node_from_data = s_pos
                            break
                except json.JSONDecodeError:
                    geo_coord_uri = URIRef(f"{thing_uri_str}/location/geo")
                    
                    for s, p, o in list(g.triples((geo_coord_uri, None, None))): g.remove((s,p,o))
                    for s, p, o in list(g.triples((None, None, geo_coord_uri))): g.remove((s,p,o))

                    g.add((geo_coord_uri, RDF.type, SCHEMA1.GeoCoordinates))
                    if "latitude" in position_data:
                        g.add((geo_coord_uri, SCHEMA1.latitude, Literal(position_data["latitude"], datatype=XSD.float)))
                    if "longitude" in position_data:
                        g.add((geo_coord_uri, SCHEMA1.longitude, Literal(position_data["longitude"], datatype=XSD.float)))
                    if "elevation" in position_data:
                        g.add((geo_coord_uri, SCHEMA1.elevation, Literal(position_data["elevation"], datatype=XSD.float)))
                    
                    location_place_uri = URIRef(f"{thing_uri_str}/location")
                    
                    for s, p, o in list(g.triples((location_place_uri, None, None))): g.remove((s,p,o))
                    for s, p, o in list(g.triples((None, None, location_place_uri))): g.remove((s,p,o))

                    g.add((location_place_uri, RDF.type, SCHEMA1.Place))
                    g.add((location_place_uri, SCHEMA1.geo, geo_coord_uri))
                    location_node_from_data = location_place_uri
                
                for obj in list(g.objects(thing_uri, SCHEMA1.location)):
                    g.remove((thing_uri, SCHEMA1.location, obj))
                        
                if location_node_from_data:
                    g.add((thing_uri, SCHEMA1.location, location_node_from_data))

            except requests.exceptions.RequestException as req_e:
                print(f"Erro de requisição HTTP para a posição: {req_e}")
            except json.JSONDecodeError as json_e:
                print(f"Erro ao decodificar JSON da posição: {json_e}")
            except Exception as e:
                print(f"Erro inesperado no processamento da posição: {e}")

    g.serialize(destination="grafo_conhecimento/grafo.ttl", format="turtle")
