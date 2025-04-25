import os
import json
import socket
import requests
import netifaces
from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo
from utils import is_same_subnet

def get_host_ip():
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET)
        if addrs:
            return addrs[0]['addr']
    raise RuntimeError("Nenhuma interface de rede com IP encontrado.")


with open('thing_description.json', 'r') as file:
    THING_DESCRIPTION = json.load(file)
with open('configs.json', 'r') as file:
    CONFIGS = json.load(file)

own_ip_address = get_host_ip()

desc = {
    'name': f"wot-assistant-{os.getpid()}",
    'type': '_wot._tcp.local.',
    'port': CONFIGS["http_port"],
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
try:
    zeroconf.unregister_service(info)
except Exception:
    pass
zeroconf.register_service(info)

print(f"Anunciado como {desc['name']}.local com serviço WoT na porta {CONFIGS['http_port']}")

class ServiceMonitor:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, "_wot._tcp.local.", self)
        self.local_service_name = f"{desc['name']}.{desc['type']}"

    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        print(f"Serviço encontrado: {name}")
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
                service_name = service['host']  
                print(f"Conectando a {service_name}:{service['port']}")
                url = f"http://{ip}:{service['port']}/things/{THING_DESCRIPTION['id']}"
                try:
                    response = requests.put(
                        url, data=json.dumps(THING_DESCRIPTION), headers={"Content-Type": "application/json"}
                    )
                    print("Resposta do servidor:", response.status_code, response.text)
                except Exception as e:
                    print("Erro ao enviar requisição:", e)
