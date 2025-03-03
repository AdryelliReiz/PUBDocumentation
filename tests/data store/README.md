
## Database

Neste projeto estamos utilizando Blazegraph como banco de dados para nossas consultas.

### Passos para criar o container que precisamos

No diretório onde o arquivo docker-compose.yml está localizado, execute o seguinte comando para criar e iniciar o container:
```bash
docker-compose up -d
```
O Docker Compose irá baixar a imagem obolibrary/blazegraph, criar o container blazegraph e iniciar o serviço.

### Desligar o Container

Para parar o container sem remover os volumes ou imagens, use:

```bash
docker-compose down
```

Este comando:
- Para os containers.
- Remove os containers e redes criadas pelo Docker Compose.
- Não remove os volumes (dados persistentes) nem as imagens.

Se você quiser parar o container, mas deixar os volumes e imagens intactos (sem removê-los), use:

```bash
docker-compose stop
```

### Ligar o Container

Para iniciar novamente o container (depois de ele ter sido desligado ou parado), use:

docker-compose up -d

Este comando:
- Cria e inicia os containers.
- O parâmetro -d (modo "detached") faz com que o container seja executado em segundo plano.

### Dica adicional
Se você fez alterações no docker-compose.yml e deseja que as mudanças sejam aplicadas, use:

```bash
docker-compose up -d --build
```

Isso irá garantir que as alterações no arquivo de configuração sejam aplicadas, reconstruindo as imagens se necessário.

### Acessar o Blazegraph
Após iniciar o container, o Blazegraph estará disponível em:

```
http://localhost:8081/blazegraph
```

### Verificar os Dados

Para verificar os dados carregados no Blazegraph, acesse o endpoint SPARQL em:

```bash
http://localhost:8081/blazegraph/#query
```
Execute uma consulta SPARQL para verificar as observações armazenadas:

```ttl
PREFIX ex: <http://example.org/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>

SELECT ?observation ?property ?value WHERE {
    ?observation a sosa:Observation ;
                 ?property ?value .
}
```

### Inserir Novos Arquivos RDF

Você pode adicionar novos arquivos RDF na pasta data/ do projeto e o container irá copiá-los para o diretório do Blazegraph ao iniciar.

### Detalhes Técnicos

O Docker Compose cria um container com a imagem do Blazegraph e configura a pasta data/ para armazenar os arquivos RDF. Durante a inicialização, o conteúdo da pasta `data/` é copiado para o container e o Blazegraph é iniciado.

Se precisar de mais detalhes sobre o funcionamento do Blazegraph ou consultas SPARQL, consulte a [documentação do Blazegraph](https://blazegraph.com/).