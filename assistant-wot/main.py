import threading
from app import iniciar_app
from thing_directory import procurar_thing_directory, buscar_things
from grafo_conhecimento.gerenciador_grafo import adicionar_think_ao_grafo

def rodar_servidor():
    try:
        iniciar_app()
    except Exception as e:
        print(f"Erro ao iniciar o servidor Flask: {e}")

def rodar_descoberta():
    try:
        procurar_thing_directory()
        
        things = buscar_things()
        
        for thing in things:
            adicionar_think_ao_grafo(thing)
    except Exception as e:
        print(f"Erro ao rodar o Thing Directory: {e}")


if __name__ == "__main__":
    thread_app = threading.Thread(target=rodar_servidor)
    thread_td = threading.Thread(target=rodar_descoberta)

    thread_app.start()
    thread_td.start()

    thread_app.join()
    thread_td.join()
