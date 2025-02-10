import json
import logging
from datetime import datetime
from tornado.ioloop import IOLoop
from wotpy.protocols.http.server import HTTPServer
from wotpy.wot.servient import Servient
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
from rdflib.plugins.stores import berkeleydb
from tornado.web import RequestHandler, Application

# Configurações
HTTP_PORT = 9494  # Alterei para 9494 para evitar conflito com outro servidor
MY_ID = "datastore_server"

# Logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuração do Berkeley DB
graph_config = "berkeley_db"
store = berkeleydb.BerkeleyDB(configuration=graph_config)
graph = Graph(store=store, identifier=MY_ID)
graph.open(graph_config, create=True)

# Namespaces
ssn = Namespace("http://www.w3.org/ns/ssn/")
sosa = Namespace("http://www.w3.org/ns/sosa/")
ex = Namespace("http://wotpyrdfsetup.org/device/")

Observation = sosa.Observation
ResultTime = sosa.resultTime
HasResult = sosa.hasResult
Observes = sosa.observes

# Classe para manipulação de propriedades
class PropertyHandler(RequestHandler):
    def initialize(self, property_name):
        self.property_name = property_name

    def get(self):
        # Leitura da propriedade
        query = f"SELECT ?value WHERE {{ ?obs rdf:type sosa:Observation ; sosa:hasResult ?value . ?obs sosa:observes <{self.property_name}> . }}"
        result = graph.query(query)
        
        if not result:
            self.set_status(404)
            self.write({"error": "Propriedade não encontrada"})
            return

        # Assumindo que a consulta retorna apenas um resultado
        value = result.bindings[0]['value'].toPython()
        self.write({"value": value})

    def put(self):
        # Atualização de propriedade
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            value = data.get("value")
            if value is None:
                self.set_status(400)
                self.write({"error": "Campo 'value' é obrigatório"})
                return

            # Criação ou atualização da observação
            observation_id = f"Observation{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
            observation_uri = ex[observation_id]

            # Registra a nova observação
            graph.add((ex[self.property_name], Observes, Literal(self.property_name)))
            graph.add((observation_uri, RDF.type, Observation))
            graph.add((observation_uri, HasResult, Literal(value)))
            graph.add((observation_uri, ResultTime, Literal(datetime.utcnow().isoformat(), datatype=XSD.dateTime)))

            self.set_status(200)
            self.write({"message": "Propriedade atualizada com sucesso"})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

# Classe para manipulação de ações
class ActionHandler(RequestHandler):
    def initialize(self, action_name):
        self.action_name = action_name

    def post(self):
        try:
            data = json.loads(self.request.body.decode("utf-8"))
            value = data.get("value")
            if value is None:
                self.set_status(400)
                self.write({"error": "Campo 'value' é obrigatório"})
                return

            # Ação de execução baseada no nome
            # Aqui pode-se adicionar lógicas específicas para a ação.
            self.write({"message": f"Ação {self.action_name} executada com sucesso", "value": value})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

# Configuração do Servidor WoT
class CustomHTTPServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super(CustomHTTPServer, self).__init__(*args, **kwargs)

class SPARQLServer(Application):
    def __init__(self):
        handlers = [
            (r"/property/(.*)", PropertyHandler),  # Para manipulação das propriedades
            (r"/action/(.*)", ActionHandler),  # Para execução de ações
        ]
        super(SPARQLServer, self).__init__(handlers)

async def start_server():
    logger.info(f"Iniciando servidor HTTP na porta {HTTP_PORT}")
    
    # Criando e configurando o Servient WoT
    servient = Servient()
    http_server = CustomHTTPServer(port=HTTP_PORT)
    servient.add_server(http_server)  # Adiciona o servidor WoT

    # Iniciando o WoT e expondo o Thing
    wot = await servient.start()

    # Definição única da descrição do Thing
    thing_description = {
        "id": f"http://{MY_ID}.local",
        "properties": {
            "temperature": {
                "type": "Property",
                "forms": [{
                    "op": "readproperty",
                    "contentType": "application/json",
                    "href": f"http://{MY_ID}.local/property/temperature"
                }]
            }
        },
        "actions": {
            "reset": {
                "type": "Action",
                "forms": [{
                    "op": "writeproperty",
                    "contentType": "application/json",
                    "href": f"http://{MY_ID}.local/action/reset"
                }]
            }
        },
        "events": {},
    }

    # Expondo o Thing
    exposed_thing = wot.produce(thing_description)
    exposed_thing.expose()

    # Inicia o servidor HTTP
    http_server.listen(HTTP_PORT)
    logger.info(f"Servidor WoT exposto na porta {HTTP_PORT}")

if __name__ == "__main__":
    try:
        IOLoop.current().add_callback(start_server)
        logger.info("Servidor iniciado")
        IOLoop.current().start()
    finally:
        if store:
            store.close(commit_pending_transaction=True)
        if graph:
            graph.close()
