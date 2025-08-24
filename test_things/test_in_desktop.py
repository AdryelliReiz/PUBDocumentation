import asyncio
import json
import requests
from zeroconf import Zeroconf, ServiceBrowser
from aiohttp import web
import socket
from zeroconf import Zeroconf, ServiceInfo

def registrar_servico_mdns():
    zeroconf = Zeroconf()
    desc = {
        "path": "/thing-description"
    }

    service_info = ServiceInfo(
        "_wot._tcp.local.",  # Tipo do serviço
        "desktopteste._wot._tcp.local.",  # Nome do serviço
        addresses=[socket.inet_aton(IP_LOCAL)],  # IP em bytes
        port=8080,
        properties=desc,
        server="esp32.local."  # Apelido mDNS desejado
    )

    try:
        zeroconf.register_service(service_info)
        print("✅ Serviço registrado via mDNS como:", service_info.name)
    except Exception as e:
        print("❌ Erro ao registrar serviço mDNS:", e)

    return zeroconf  # importante: mantenha para poder fechar depois se quiser


IP_LOCAL = '0.0.0.0'
# Cria um socket temporário para obter o IP local
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    try:
        s.connect(("8.8.8.8", 80))
        IP_LOCAL = s.getsockname()[0]
    except Exception as e:
        print("Não foi possível determinar o IP:", e)
        IP_LOCAL = "127.0.0.1"  # Usa localhost como fallback

TD = {
    "@context": [
        "https://www.w3.org/2019/wot/td/v1",
        {"language": "en"}
    ],
    "title": "ESP32 Device",
    "id": "urn:dev:ops:adry-desktop",
    "base": "http://desktopteste.local",
    "security": ["nosec_sc"],
    "properties": {
        "getThingDescription": {
            "type": "string",
            "title": "Get Thing Description",
            "description": "Provides the Thing Description of the device",
            "readOnly": True,
            "forms": [
                {
                    "href": "/getThingDescription",
                    "contentType": "application/json",
                    "op": "readproperty"
                }
            ]
        }
    },
    "actions": {
        "doSomething": {
            "title": "Do something",
            "description": "Does something",
            "forms": [
                {
                    "href": "/doSomething",
                    "contentType": "application/json",
                    "op": "invokeaction"
                }
            ]
        }
    },
    "events": {},
    "links": [
        {"rel": "properties", "href": "/properties"},
        {"rel": "actions", "href": "/actions"},
        {"rel": "events", "href": "/events"}
    ],
    "securityDefinitions": {
        "nosec_sc": {"scheme": "nosec"}
    }
}

def same_subrede(ip1, ip2):
    return ip1.split('.')[:3] == ip2.split('.')[:3]

async def handle_root(request):
    return web.json_response({"message": "Hello from desktop! This program acts as both a client and a server."})

async def get_thing_description(request):
    return web.json_response(TD)

async def do_something(request):
    print("Executing action: Buzz... (simulated)")
    return web.json_response({"message": "Action executed: buzz..."})

async def handle_not_found(request):
    return web.json_response({"error": "Not found"}, status=404)

async def discover_service():
    zeroconf = Zeroconf()
    services_discovered = False

    class ServiceListener:
        def __init__(self):
            self.services = []

        def add_service(self, zeroconf, type, name):
            info = zeroconf.get_service_info(type, name)
            if info:
                service_ips = [".".join(map(str, addr)) for addr in info.addresses]
                self.services.append((service_ips, info.port))
                print(f"Service found: IPs={service_ips}, Port={info.port}")

    listener = ServiceListener()
    ServiceBrowser(zeroconf, "_wot._tcp.local.", listener)

    await asyncio.sleep(10)  # Aguarda para descobrir os serviços

    for service_ips, port in listener.services:
        for ip in service_ips:
            if same_subrede(ip, IP_LOCAL):
                print(f"Attempting connection to IP: {ip}, Port: {port}")
                url = f"http://{ip}:{port}/things/{TD['id']}"
                headers = {"Content-Type": "application/json"}
                print(f"Requisição para: {url}")

                try:
                    response = requests.put(url, json=TD, headers=headers)
                    print("Response status:", response.status_code)
                    print("Response body:", response.text)
                except Exception as e:
                    print("Failed to send PUT request:", e)

                services_discovered = True  # Marca que o serviço foi encontrado e requisição enviada

    zeroconf.close()
    if not services_discovered:
        print("Nenhum serviço correspondente encontrado na subrede.")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle_root)
    app.router.add_get('/thing-description', get_thing_description)
    app.router.add_get('/do-something', do_something)
    app.router.add_get('/{tail:.*}', handle_not_found)

    runner = web.AppRunner(app)
    await runner.setup()
    api = web.TCPSite(runner, '0.0.0.0', 8080)
    print("Server started on http://0.0.0.0:8080")
    await api.start()

async def main():
    zeroconf = registrar_servico_mdns()
    # Inicia o servidor
    server_task = asyncio.create_task(start_server())
    # Executa a descoberta do serviço uma vez
    await discover_service()
    # Aguarda indefinidamente para manter o servidor ativo
    try:
        await asyncio.Event().wait()
    finally:
        zeroconf.close()


asyncio.run(main())