# Projeto Assistant-WoT

Este projeto é uma aplicação Python cujo arquivo principal é `main.py`. Abaixo estão as instruções para executar o projeto, bem como uma explicação da estrutura do projeto e das funções implementadas.

## Antes de executar o projeto

É necessário que um thing-directory e pelo uma thing estajam rodando antes de executar o assistente para ter uma melhor experiência de uso.
O Exemplo de uma Thing que pode ser usada está na raiz do diretório PUBDOCUMENTATION, localizado em `/tests/thing/exemple_think_desktop.py`.

## Como executar o projeto

1. Certifique-se de ter o Python 3.8 ou superior instalado em sua máquina.
2. Instale as dependências necessárias executando:
    ```bash
    pip install -r requirements.txt
    ```
3. Execute o arquivo principal:
    ```bash
    python main.py
    ```

## Estrutura do Projeto

O projeto está organizado da seguinte forma:
```
assistant-wot/
├── main.py                  # Arquivo principal que inicia a aplicação
├── grafo_conhecimento/      # Diretório contendo o grafo de conhecimento e funções de manipulação
│   ├── __init__.py          # Inicializador do módulo
│   ├── gerenciador_grafo.py # Manipulador do grafo e consultas à OpenAI
│   └── grafo.ttl            # Arquivo do grafo de conhecimento
├── templates/               # Diretório contendo templates do frontend
│   └── index.html           # Arquivo principal HTML
├── app.py                   # Servidor Flask
├── thing_directory.py       # Arquivo responsável por chamadas ao Thing Directory
├── requirements.txt         # Arquivo com as dependências do projeto
├── utils.py                 # Funções utilitárias
├── processador_frases.txt   # Arquivo que processa frases e chama o módulo responsável
├── .env.example             # Exemplo de arquivo de variáveis de ambiente
└── README.md                # Documentação do projeto
```

## Documentação

Para fins de estudo e aprimoramento futuro do assistente, foi criada uma documentação explicando seu funcionamento, pontos que não foram abordados e exceções.
A documentação detalhada do projeto está disponível no arquivo [`docs/README.md`](./docs/README.md).

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).