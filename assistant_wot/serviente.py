import json
from wotpy.wot.servient import Servient
from wotpy.protocols.http.server import HTTPServer
import asyncio

with open('thing_description.json', 'r') as file:
    THING_DESCRIPTION = json.load(file)

async def start_wot_server():
    servient = Servient()
    http_server = HTTPServer(port=8081)
    servient.add_server(http_server)
    wot = await servient.start()
    exposed_thing = await wot.produce(THING_DESCRIPTION)
    await exposed_thing.expose()
    print("Servidor WoT rodando na porta 8081.")
    await asyncio.Future()

def run_wot_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_wot_server())