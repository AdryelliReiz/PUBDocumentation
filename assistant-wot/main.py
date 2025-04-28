import threading
from app import iniciar_app
from thing_directory import descobrir_thing_directory

def rodar_servidor():
    iniciar_app()

def rodar_descoberta():
    descobrir_thing_directory()

if __name__ == "__main__":
    thread_app = threading.Thread(target=rodar_servidor)
    thread_td = threading.Thread(target=rodar_descoberta)

    thread_app.start()
    thread_td.start()

    thread_app.join()
    thread_td.join()
