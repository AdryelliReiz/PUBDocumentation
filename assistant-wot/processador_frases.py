from grafo_conhecimento.gerenciador_grafo import consultar_frase, buscar_similaridade
from utils import executar_conceito

def processar_frase(frase, localizacao):
    # Consultar o grafo de conhecimento
    print(f"Processando frase: {frase} com localização: {localizacao}")
    conceito = consultar_frase(frase, localizacao)

    print(f"Conceito encontrado: {conceito}")

    if conceito:
        print(f"Executando ação para o conceito: {conceito}")
        resultado = executar_conceito(conceito)
        return {
            "status": resultado['status'],
            "message": resultado['message'],
            "type": "CONCEITO",
            "data": conceito
        }
    else:
        similaridade = buscar_similaridade(frase, localizacao)
        print(similaridade)
        if len(similaridade) > 0:
            return {"status": 200, "type": "SIMILARIDADE", "data": similaridade}
        return {"status": 200, "type": "INDEFINIDO", "data": {}}
    
