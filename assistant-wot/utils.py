import ipaddress
import socket
import requests

def is_same_subnet(ip1, ip2, subnet_mask='255.255.255.0'):
    """Verifica se dois IPs estão na mesma sub-rede."""
    net1 = ipaddress.IPv4Network(f"{ip1}/{subnet_mask}", strict=False)
    net2 = ipaddress.IPv4Network(f"{ip2}/{subnet_mask}", strict=False)
    return net1.network_address == net2.network_address

def obter_ip_local():
    """Obtém o IP real da máquina na rede local (não 127.0.0.1)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Erro ao obter IP local: {e}")
        return "127.0.0.1"

def executar_conceito(conceito):
    """Executa uma ação baseada no conceito identificado."""

    try:
        if conceito['http_method'] == 'GET':
            response = requests.get(conceito['target_url'])
        elif conceito['http_method'] == 'POST':
            response = requests.post(conceito['target_url'])
        else:
            raise ValueError("Método HTTP não suportado")

        if response.status_code == 200:
            print(f"Ação '{conceito['action_name']}' executada com sucesso!")
            return {"status": 200, "message": f"Ação '{conceito['action_name']}' executada com sucesso!"}
        else:
            print(f"Erro ao executar ação: {response.status_code}")
            return {"status": response.status_code, "message": "Erro ao executar ação"}
    except Exception as e:
        print(f"Erro ao executar ação: {e}")
        return {"status": 500, "message": str(e)}