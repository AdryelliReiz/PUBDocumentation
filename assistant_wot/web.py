from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return '''
    <html>
        <body>
            <h2>Enviar Mensagem para o Servidor WoT</h2>
            <input type="text" id="msg_input" placeholder="Digite sua mensagem">
            <button onclick="sendMessage()">Enviar</button>
            <script>
                function sendMessage() {
                    let message = document.getElementById("msg_input").value;
                    fetch("http://localhost:8080/mensagem", {
                        method: "PUT",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ "mensagem": message })
                    }).then(response => console.log("Mensagem enviada!"));
                }
            </script>
        </body>
    </html>
    '''