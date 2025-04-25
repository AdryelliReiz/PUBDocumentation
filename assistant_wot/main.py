import threading
import mdns
import serviente
from web import app

if __name__ == "__main__":

    # Inicia o monitoramento de serviços mDNS em uma thread separada
    threading.Thread(target=mdns.ServiceMonitor, daemon=True).start()
    
    # Inicia o servidor WoT em uma thread separada
    threading.Thread(target=serviente.run_wot_server, daemon=True).start()
    
    # Inicia o servidor web
    app.run(host="0.0.0.0", port=8080, debug=True)
