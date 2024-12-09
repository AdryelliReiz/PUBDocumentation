import network
import uasyncio
import time
import json
import urequests
import machine
from microdot import Microdot, Response
from mdns_client import Client
from mdns_client.service_discovery import ServiceResponse
from mdns_client.service_discovery.txt_discovery import TXTServiceDiscovery
from mdns_client.responder import Responder

# Definindo variáveis globais
PORT=80
HOST="esp32"

# Definição da Thing Description (TD)
TD = {
    "@context": [
        "https://www.w3.org/2019/wot/td/v1",
        {"language": "en"}
    ],
    "title": "ESP32 Device",
    "id": "urn:dev:ops:ESP32-001",
    "base": "http://esp32.local",
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
        },
        "lightSensor": {
            "type": "number",
            "title": "Light Sensor",
            "description": "Get a value of light sensor",
            "readOnly": True,
            "forms": [
                {
                    "href": "/light-sensor",
                    "contentType": "application/json",
                    "op": "readproperty"
                }
            ]
        }
    },
    "actions": {
        "toggleLed": {
            "title": "Toggle Led",
            "description": "Turn on or turn off my led",
            "forms": [
                {
                    "href": "/toggle-led",
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
    "securityDefinitions": {"nosec_sc": {"scheme": "nosec"}}
}

# Setup items
light_sensor = machine.ADC(machine.Pin(34))
led = machine.Pin(2, machine.Pin.OUT)
led_state = 0
led.value(led_state)

# =============================== < wi-fi > ===============================
ssid = "Batcaverna-IoT"
password = "4pfXgcGh7y"
#ssid = "lab8"
#password = "lab8arduino"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    print("Conectando ao Wi-Fi...")
    time.sleep(1)

print("Wi-Fi conectado! Configurações de IP:", wlan.ifconfig())
own_ip_address = wlan.ifconfig()[0]

# =============================== < microdot > ===============================
app = Microdot()
Response.default_content_type = 'application/json'

@app.route('/')
async def handle_root(request):
    return {"message": "Hello from ESP32! This ESP acts as both a client and a server."}

@app.route('/properties/thing-description')
async def get_thing_description(request):
    return json.dumps(TD)

# Rota para ler o dado atual do sensor de luminosidade
@app.route('/properties/light_sensor')
async def get_light_sensor(request):
    sensor_value = light_sensor.read()
    return {"value": sensor_value}

# Rota para mudar o estado do LED (ligado ou desligado)
@app.route('/actions/toggle-led', methods=['PUT'])
async def toggle_led(request):
    global led_state

    try:
        # Obtém o valor do corpo da requisição
        data = request.json
        if "value" in data:
            # Verifica se o valor é 0 ou 1
            new_state = int(data["value"])
            if new_state not in (0, 1):
                return {"error": "'value' must be 0 or 1"}, 400
        
            led_state = new_state

        # Se não houver valor, apenas inverte o estado atual
        else:
            if led_state:
                led_state = 0
            else:
                led_state = 1
        
        # Atualiza o estado do LED
        led.value(led_state)
        
        return {"message": "LED updated", "led_state": led_state}
    except Exception as e:
        return {"error": str(e)}, 400

@app.route('<path:path>')
async def handle_not_found(request, path):
    return {"error": "Not found"}, 404

# =============================== < mDNS > ===============================
client = Client(own_ip_address)
responder = Responder(client, own_ip=own_ip_address, host=HOST)
responder.advertise("_wot", "_tcp", port=PORT)

print(f"Anunciado como {HOST}.local com serviço HTTP na porta {PORT}")
discovery = TXTServiceDiscovery(client)

class ServiceMonitor:
    def service_added(self, service: ServiceResponse):
        print("Service added:", service)

    def service_updated(self, service: ServiceResponse):
        print("Service updated:", service)

    def service_removed(self, service: ServiceResponse):
        print("Service removed:", service)

def is_same_subnet(ip1, ip2):
    return ip1.split('.')[:3] == ip2.split('.')[:3]

async def discover():
    print("Procurando Thing Directory...")
    discovery.add_service_monitor(ServiceMonitor())
    while True:
        await discovery.query("_wot", "_tcp")
        services = discovery.current("_wot", "_tcp")
        
        if services:
            print(f"Serviços encontrados: {services}")
            for service in services:
                for ip in service.ips:
                    if is_same_subnet(own_ip_address, ip):
                        print(f"Conectando ao serviço em {ip}:{service.port}")
                        url = f"http://{ip}:{service.port}/things/{TD['id']}"
                        try:
                            response = urequests.put(
                                url, data=json.dumps(TD), headers={"Content-Type": "application/json"}
                            )
                            print("Resposta do servidor:", response.status_code, response.text)
                            response.close()
                        except Exception as e:
                            print("Erro ao enviar requisição:", e)
                        return
        else:
            print("Nenhum serviço encontrado. Tentando novamente em 5 segundos...")
        await uasyncio.sleep(5)

async def start_server():
    print("Servidor iniciado na porta ", PORT)
    await app.start_server(host='0.0.0.0', port=PORT)

async def main():
    await uasyncio.gather(
        start_server(),
        discover()
    )

uasyncio.run(main())
