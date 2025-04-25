import json
import logging
import socket
import requests
import asyncio
import os
import netifaces
from datetime import datetime
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from wotpy.protocols.http.server import HTTPServer
from wotpy.wot.servient import Servient
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
from rdflib.plugins.stores import berkeleydb
from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange, ServiceInfo
from aiohttp import web

# Variáveis globais
HTTP_PORT = 9494

# Carrega o JSON do arquivo para a variável THING_DESCRIPTION
with open('thing_description.json', 'r') as file:
    THING_DESCRIPTION = json.load(file)

# Logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuração do Berkeley DB
graph_config = os.path.abspath("berkeley_db")
store = berkeleydb.BerkeleyDB()
graph = Graph(store=store, identifier="MY_ID")
graph.open(graph_config, create=True)

# Namespaces
ssn = Namespace("http://www.w3.org/ns/ssn/")
sosa = Namespace("http://www.w3.org/ns/sosa/")
ex = Namespace("http://wotpyrdfsetup.org/device/")

Observation = sosa.Observation
ResultTime = sosa.resultTime
HasResult = sosa.hasResult
Observes = sosa.observes

# Configuração do mDNS
print("Iniciando servidor mDNS...")

# Pega o endereço IP da máquina
def get_host_ip():
    iface = "eth0"  
    try:
        return netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
    except KeyError:
        raise RuntimeError(f"Não foi possível determinar o IP da interface {iface}. Verifique se está correto.")

own_ip_address = get_host_ip()

print(own_ip_address)

# Anuncia o serviço WoT
desc = {
    'name': 'datastore',
    'type': '_wot._tcp.local.',
    'port': HTTP_PORT,
    'server': own_ip_address,
    'properties': {
        'id': THING_DESCRIPTION['id'],
        'name': THING_DESCRIPTION['title']
    }
}

zeroconf = Zeroconf()
info = ServiceInfo(
    desc['type'],
    f"{desc['name']}.{desc['type']}",
    addresses=[socket.inet_aton(own_ip_address)],
    port=desc['port'],
    properties=desc['properties'],
    server=f"{desc['name']}.local."
)
print(info)

zeroconf.register_service(info)
print(f"Anunciado como {desc['name']}.local com serviço WoT na porta {HTTP_PORT}")

class ServiceMonitor:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, "_wot._tcp.local.", self)
        self.local_service_name = f"{desc['name']}.{desc['type']}"

    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        print(f"Serviço encontrado: {name}")
        
        # Verifica se o serviço encontrado não é o mesmo que está sendo executado
        if name != self.local_service_name and "Thing Directory" in name:
            info = zeroconf.get_service_info(type, name)
            if info:
                service = {
                    'host': info.server,
                    'port': info.port,
                    'ips': [socket.inet_ntoa(addr) for addr in info.addresses]
                }
                print(f"Service {name} added: {service}")
                self.connect_to_service(service)
        else:
            print(f"Ignorando o próprio serviço: {name}")

    def update_service(self, zeroconf, type, name):
        print(f"Service {name} updated")

    def connect_to_service(self, service):
        print(service)
        for ip in service['ips']:
            if is_same_subnet(ip, own_ip_address):
                service_name = service['host']  # Nome do serviço mDNS
                print(f"Conectando a {service_name}:{service['port']}")

                # Monta a URL usando o nome do serviço mDNS
                url = f"http://{ip}:{service['port']}/things/{THING_DESCRIPTION['id']}"

                try:
                    response = requests.put(
                        url, data=json.dumps(THING_DESCRIPTION), headers={"Content-Type": "application/json"}
                    )
                    print("Resposta do servidor:", response.status_code, response.text)
                except Exception as e:
                    print("Erro ao enviar requisição:", e)
        
def is_same_subnet(ip1, ip2):
    return ip1.split('.')[:3] == ip2.split('.')[:3]

def handle_root(request):
    return web.json_response(THING_DESCRIPTION)

async def start_server_http():
    app = web.Application()
    app.router.add_get('/', handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', HTTP_PORT)
    print("Servidor HTTP iniciado!")
    await site.start()

async def main():
    #monitor = ServiceMonitor()
    asyncio.create_task(start_server_http())
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
    #    monitor.zeroconf.close()
        print("Fechando servidor HTTP...")

asyncio.run(main())
