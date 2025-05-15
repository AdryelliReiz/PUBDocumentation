import socket
import netifaces
import time
import requests
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange
from utils import is_same_subnet

thing_directory_info = {
    "ip": 'localhost',
    "port": 8081
}  # Armazena o resultado da descoberta

def obter_ip_local():
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET)
        if addrs:
            return addrs[0]['addr']
    raise RuntimeError("Nenhum endereço IP encontrado nas interfaces de rede.")

def ao_mudar_servico(zeroconf, tipo_servico, nome, estado):
    global thing_directory_info
    if estado is ServiceStateChange.Added and "Thing Directory" in nome:
        info = zeroconf.get_service_info(tipo_servico, nome)
        if info:
            ips = [socket.inet_ntoa(addr) for addr in info.addresses]
            for ip in ips:
                if is_same_subnet(ip, obter_ip_local()):
                    thing_directory_info = {
                        "ip": ip,
                        "port": info.port,
                        "nome": nome
                    }
                    print(f"✅ Thing Directory encontrado: {thing_directory_info}")
                    zeroconf.close()
                    return

def descobrir_thing_directory(timeout=60):
    """
    Procura por um Thing Directory via mDNS com Zeroconf.
    Espera até 'timeout' segundos por um serviço válido.
    """
    global thing_directory_info

    print("Procurando Thing Directory via mDNS...")
    zeroconf = Zeroconf()
    ServiceBrowser(zeroconf, "_wot._tcp.local.", handlers=[ao_mudar_servico])

    # Espera pela descoberta ou timeout
    inicio = time.time()
    while thing_directory_info is None and (time.time() - inicio < timeout):
        print("Aguardando descoberta do Thing Directory...")
        time.sleep(0.5)

    if thing_directory_info is None:
        print("Nenhum Thing Directory encontrado.")
    return thing_directory_info

def buscar_things():
    """
    Busca as Things cadastradas no Thing Directory descoberto.
    Retorna a lista de Things ou None.
    """
    if thing_directory_info is None:
        print("Nenhum Thing Directory disponível para consulta.")
        return None

    url = f"http://{thing_directory_info['ip']}:{thing_directory_info['port']}/things"
    print(f"Buscando Things em {url}...")
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            print(f"Erro ao buscar Things: {resposta.status_code}")
            return None
    except Exception as e:
        print(f"Erro de conexão ao buscar Things: {e}")
        return None
