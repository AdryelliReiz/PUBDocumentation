from grafo_conhecimento.gerenciador_grafo import consultar_frase, buscar_similaridade, pesquisar_sugestoes
from thing_directory import buscar_things

def processar_frase(frase, metadados):
    # Consultar o grafo de conhecimento
    localizacao = metadados.get("localizacao", "")
    conceito = consultar_frase(frase, localizacao)

    if conceito:
        return {"status": 200, "type": "CONCEITO", "conceito": conceito}
    else:
        similaridade = buscar_similaridade(frase, metadados)
        print(similaridade)
        if len(similaridade) > 0:
            return {"status": 200, "type": "SIMILARIDADE", "data": similaridade}
        else:
            # Procurar things
            things_descriptions = buscar_things()
            print(things_descriptions)
            if things_descriptions:
                resposta = pesquisar_sugestoes(things_descriptions, frase, localizacao)
                return ({"status": 200, "type": "SUGESTOES", "data": resposta})
            else:
                # Nenhum conceito ou similaridade encontrada
                return {"status": 404, "data": {}}
