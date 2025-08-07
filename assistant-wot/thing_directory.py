import socket
import time
import requests
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange
from utils import is_same_subnet, obter_ip_local

# Armazenará a informação do Thing Directory quando encontrado
thing_directory_info = None

def ao_mudar_servico(zeroconf, service_type, name, state_change):
    global thing_directory_info
    if state_change is ServiceStateChange.Added and "Thing Directory" in name:
        info = zeroconf.get_service_info(service_type, name)
        if info:
            ips = [socket.inet_ntoa(addr) for addr in info.addresses]
            for ip in ips:
                if is_same_subnet(ip, obter_ip_local()):
                    thing_directory_info = {
                        "ip": ip,
                        "port": info.port,
                        "nome": name
                    }
                    print(f"Thing Directory encontrado: {thing_directory_info}")
                    return

def procurar_thing_directory(timeout=60):
    """
    Procura um serviço mDNS do tipo _wot._tcp.local. (Thing Directory)
    """
    global thing_directory_info
    thing_directory_info = None

    print("Procurando Thing Directory via mDNS...")
    zeroconf = Zeroconf()
    ServiceBrowser(zeroconf, "_wot._tcp.local.", handlers=[ao_mudar_servico])

    start = time.time()
    while thing_directory_info is None and (time.time() - start < timeout):
        time.sleep(0.5)

    zeroconf.close()

    if thing_directory_info is None:
        print("Nenhum Thing Directory encontrado.")
    
    return thing_directory_info

def buscar_things():
    """
    Faz requisição HTTP ao Thing Directory para obter a lista de Things.
    """
    if thing_directory_info is None:
        print("Thing Directory não disponível.")
        return None

    url = f"http://{thing_directory_info['ip']}:{thing_directory_info['port']}/things"
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            print(f"Things encontrados: {resposta.json()}")
            return resposta.json()
        else:
            print(f"Erro ao buscar Things: {resposta.status_code}")
            return None
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None
