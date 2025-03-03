import network
import machine
import uasyncio
import time
import json
import urequests
from microdot import Microdot, Response
from mdns_client import Client
from mdns_client.service_discovery import ServiceResponse
from mdns_client.service_discovery.txt_discovery import TXTServiceDiscovery
from mdns_client.responder import Responder

# =============================== < Configuração > ===============================
SSID = "Batcaverna-IoT"
PASSWORD = "4pfXgcGh7y"

DEVICE_ID = "urn:dev:ops:ESP32-001"
DEVICE_TITLE = "ESP32 Device"
BASE_URL = "http://esp32.local"

LIGHT_SENSOR = "light_sensor"
TD = {
    "@context": ["https://www.w3.org/2019/wot/td/v1"],
    "id": DEVICE_ID,
    "title": DEVICE_TITLE,
    "base": BASE_URL,
    "properties": {
        LIGHT_SENSOR: {
            "type": "number",
            "title": "Light Sensor",
            "description": "Current light sensor value",
            "readOnly": True,
            "forms": [
                {"href": f"/properties/{LIGHT_SENSOR}", "contentType": "application/json", "op": "readproperty"}
            ]
        }
    },
    "security": ["nosec_sc"],
    "securityDefinitions": {"nosec_sc": {"scheme": "nosec"}}
}

# Sensor setup
light_sensor = machine.ADC(machine.Pin(34))

# =============================== < Conexão Wi-Fi > ===============================
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    print("Conectando ao Wi-Fi...")
    time.sleep(1)

print("Wi-Fi conectado! Configurações de IP:", wlan.ifconfig())
own_ip_address = wlan.ifconfig()[0]

# =============================== < Microdot HTTP Server > ===============================
app = Microdot()
Response.default_content_type = 'application/json'

@app.route('/properties/light_sensor')
async def get_light_sensor(request):
    sensor_value = light_sensor.read()
    return {"value": sensor_value}

@app.route('/thing-description')
async def get_thing_description(request):
    return json.dumps(TD)

@app.route('<path:path>')
async def handle_not_found(request, path):
    return {"error": "Not found"}, 404

# =============================== < mDNS > ===============================
client = Client(own_ip_address)
responder = Responder(client, own_ip=own_ip_address, host="esp32")

# Anuncia o serviço HTTP na porta 80
responder.advertise("_http", "_tcp", port=80)
print("Anunciado como esp32.local com serviço HTTP na porta 80")
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

async def discover_and_register():
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
                        td_url = f"http://{ip}:{service.port}/things/{DEVICE_ID}"
                        prop_url = f"http://{ip}:{service.port}/things/{DEVICE_ID}/properties/{LIGHT_SENSOR}"

                        try:
                            # Registrar Thing Description
                            response = urequests.put(
                                td_url, data=json.dumps(TD), headers={"Content-Type": "application/json"}
                            )
                            print("TD registrada no servidor:", response.status_code, response.text)
                            response.close()

                            
                        except Exception as e:
                            print("Erro ao registrar Thing Description:", e)
                        return
        else:
            print("Nenhum serviço encontrado. Tentando novamente em 5 segundos...")
        await uasyncio.sleep(5)

# =============================== < Início da Aplicação > ===============================
async def start_server():
    print("Servidor HTTP iniciado na porta 80...")
    await app.start_server(host='0.0.0.0', port=80)

async def main():
    await uasyncio.gather(
        start_server(),
        discover_and_register()
    )

uasyncio.run(main())

