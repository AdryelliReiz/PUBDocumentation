from flask import Flask, jsonify, Response
import requests

app = Flask(__name__)

TD = {
    "@context": [
        "https://www.w3.org/2022/wot/td/v1.1",
        {
            "htv": "http://www.w3.org/2011/http#",
            "saref": "https://w3id.org/saref#",
            "om": "http://www.ontology-of-units-of-measure.org/resource/om-2/",
            "schema": "https://schema.org", 
            "skos": "http://www.w3.org/2004/02/skos/core#"
        }
    ],
    "id": "urn:uuid:014139c9-0000-4db5-9c61-cc2d2bfc217d",
    "title": "MyDeviceThing",
    "securityDefinitions": {
        "nosec_sc": {
            "scheme": "nosec"
        }
    },
    "security": ["nosec_sc"],
    "properties": {
        "position": {
            "type": "object",
            "@type": "schema:GeoCoordinates",
            "description" : "Work in progress. From example 47. It is not clear what is properties nested into properties and it is not clear the datatype (is is JSON?) notice that position in schema.org is the position of an item in a series so the name dont have to be bound to the ontology in fact, there is an @type which clarifies it in the response ... should properties be schema:geo??",
            "properties": {
                    "longitude": { "type": "number" },
                    "latitude":  { "type": "number" },
                    "elevation": { "type": "number" }
            },
            "forms": [{"href": "http://localhost:5000/position"}]
        },
        "lamp": {
            "type": "boolean",
            "readOnly": True,
            "observable": False,
            "skos:altLabel": "Lamp state",
            "description": "text in the response: True=On; False=Off, skos:altLabel is permitted see https://w3c.github.io/wot-thing-description/#saref-state-annotation-example for the same use with saref",
            "forms": [{
                "op": [
                    "readproperty"
                ],
                "href": "http://localhost:5000/lamp",
                "response": {
                    "contentType": "text/html"
                }
            }]},
        "temperature": {
            "type": "number",
            "readOnly": True,
            "observable": False,
            "skos:altLabel": "air temperature",
            "unit": "om:degreeCelsius",
            "description": "text in the response: air temperature in Celsius, TD recom example 44 is missing information: measurement unit is in the response(?) or in the request(?) saref:TemperatureSensor is deprecated.",
            "forms": [{
                "op": [
                    "readproperty"
                ],
                "href": "http://localhost:5000/temperature",
                "response": {
                    "contentType": "text/plain"
                }
            }]},
        "mute": {
            "type": "boolean",
            "readOnly": True,
            "observable": False,
            "skos:altLabel": "buzzer state",
            "description": "text in the response: True=On; False=Off",
            "forms": [{
                "op": [
                    "readproperty"
                ],
                "href": "http://localhost:5000/mute",
                "response": {
                    "contentType": "text/html"
                }
            }]

        },
        "ldr": {
            "type": "integer",
            "minimum": 0,
            "maximum": 4095,
            "readOnly": True,
            "observable": False,
            "skos:altLabel": "Ambient light",
            "description": "html form",
            "forms": [{
                "op": [
                    "readproperty"
                ],
                "href": "http://localhost:5000/ldr",
                "response": {
                    "contentType": "text/html"
                }
            }]
        }
    },
    "actions": {
        "lamp-on": {
            "safe": False,
            "idempotent": True,
            "skos:altLabel": "Acende a lâmpada",
            "forms": [{
                "op": "invokeaction",
                "href": "http://localhost:5000/lamp/on",
                "htv:methodName": "GET"
            }]
        },
        "lamp-off": {
            "safe": False,
            "idempotent": True,
            "skos:altLabel": "Apaga a lâmpada",
            "forms": [{
                "op": "invokeaction",
                "href": "http://localhost:5000/lamp/off",
                "htv:methodName": "GET"
            }]
        },
        "mute-on": {
            "safe": False,
            "idempotent": True,
            "skos:altLabel": "Desliga o buzzer",
            "forms": [{
                "op": "invokeaction",
                "href": "http://localhost:5000/mute/on",
                "htv:methodName": "GET"
            }]
        },
        "mute-off": {
            "safe": False,
            "idempotent": True,
            "skos:altLabel": "Liga o buzzer",
            "forms": [{
                "op": "invokeaction",
                "href": "http://localhost:5000/mute/off",
                "htv:methodName": "GET"
            }]
        }
    }
}


position_data = {
    "@context": "https://schema.org",
    "@type": "Place",
    "name": "Laboratório 8",
    "description": "Sala onde o dispositivo está localizado",
    "geo": {
        "@type": "GeoCoordinates",
        "latitude": 40.75,
        "longitude": -73.98,
        "elevation": 70.4
    }
}

@app.route("/lamp")
def get_lamp():
    print("[GET] Estado da lâmpada solicitado")
    return Response("True", mimetype='text/html')  # Simulando lâmpada ligada

@app.route("/temperature")
def get_temperature():
    print("[GET] Temperatura solicitada")
    return Response("25.2", mimetype='text/plain')  # Simulando 25.2 ºC

@app.route("/mute")
def get_mute():
    print("[GET] Estado do buzzer solicitado")
    return Response("False", mimetype='text/html')  # Simulando buzzer desligado

@app.route("/thing-description")
def thing_description():
    return jsonify(TD)

@app.route("/position")
def get_position():
    return jsonify(position_data)

@app.route("/ldr")
def get_ldr():
    # Valor simulado de luminosidade em lux
    return jsonify(ambientLight=238.5)

@app.route("/lamp/on", methods=["GET"])
def lamp_on():
    print("[ACTION] Acendendo lâmpada (simulado)")
    return jsonify({"status": "success", "message": "Lâmpada acesa (simulado)"}), 200

@app.route("/lamp/off", methods=["GET"])
def lamp_off():
    print("[ACTION] Apagando lâmpada (simulado)")
    return jsonify({"status": "success", "message": "Lâmpada apagada (simulado)"}), 200

@app.route("/mute/on", methods=["GET"])
def mute_on():
    print("[ACTION] Desligando buzzer (simulado)")
    return jsonify({"status": "success", "message": "Buzzer desligado (simulado)"}), 200

@app.route("/mute/off", methods=["GET"])
def mute_off():
    print("[ACTION] Ligando buzzer (simulado)")
    return jsonify({"status": "success", "message": "Buzzer ligado (simulado)"}), 200

if __name__ == "__main__":
    response = requests.put(f"http://localhost:8081/things/{TD['id']}", json=TD)
    app.run(debug=True)
