# Documentação

## O que é o `assistant-wot`?

O `assistant-wot` é um assistente inteligente que interpreta comandos em linguagem natural e executa ações em dispositivos da Internet das Coisas (IoT). Diferentemente de sistemas de automação que dependem de comandos rígidos e pré-programados, este assistente utiliza um **grafo de conhecimento semântico** como sua base operacional. Esse grafo é construído dinamicamente a partir da tradução de **Thing Descriptions (TDs)** para **triplas RDF**, permitindo que o assistente compreenda e interaja com os dispositivos com base em seu significado e contexto, e não apenas em sua sintaxe.

---

## Funcionalidades

O `assistant-wot` oferece um conjunto de funcionalidades essenciais para a interação com ambientes WoT:

* **Descoberta Automática de Dispositivos**: Utiliza o protocolo **mDNS** para localizar automaticamente um **Thing Directory** na rede local. Isso elimina a necessidade de configuração manual de endereços, tornando a solução escalável e aplicável a ambientes de domótica e laboratórios.
* **Construção Dinâmica do Grafo de Conhecimento**: Converte as **Thing Descriptions (TDs)** encontradas no diretório em um grafo de conhecimento RDF. As TDs, em formato JSON-LD, são transformadas em triplas `<sujeito, predicado, objeto>`, estabelecendo uma base semântica robusta para todas as interações.
* **Processamento Híbrido de Linguagem Natural**: Interpreta os comandos do usuário usando uma abordagem em duas etapas, orquestrada pelo módulo `processador_frases.py`. A primeira etapa realiza uma **busca determinística** no grafo. Se não houver correspondência exata, a segunda etapa utiliza um **modelo de linguagem avançado (GPT-4o)** para encontrar a melhor correspondência semântica.
* **Execução de Ações e Consulta de Propriedades**: Após a interpretação, o assistente é capaz de executar ações (como ligar ou desligar uma lâmpada) ou consultar propriedades de dispositivos (como a temperatura de um sensor) por meio de requisições HTTP diretas para as *Things*.
* **Mecanismo de Aprendizagem (Enriquecimento do Grafo)**: Quando um comando não é reconhecido, o assistente sugere ações semelhantes. Se o usuário confirmar uma sugestão, a frase original é adicionada ao grafo como um `altLabel` (usando a ontologia SKOS), ensinando o sistema a reconhecer o comando em interações futuras.

---

## Componentes Técnicos

O projeto é modular, com cada componente desempenhando um papel crucial na arquitetura.

### **1. Descoberta de Dispositivos**
O módulo `thing_directory.py` utiliza a biblioteca **`zeroconf`** para escutar anúncios de serviços do tipo `_wot._tcp.local` na rede. Ao encontrar um **Thing Directory**, ele obtém seu endereço IP e porta. Posteriormente, ele acessa a rota `/things` do diretório para recuperar todas as TDs, que servem como ponto de partida para a construção do grafo.

### **2. Grafo de Conhecimento**
O módulo `gerenciador_grafo.py` utiliza a biblioteca **`rdflib`** para construir e gerenciar o grafo RDF. O código carrega as TDs (em JSON-LD) e as converte em triplas RDF, que são salvas no arquivo `grafo.ttl`. Essa abordagem permite:

* Modelar as *Things* e suas capacidades (*Actions*, *Properties*, *Events*) como nós interconectados.
* Enriquecer o grafo dinamicamente, como na rota `/adicionar-informacao` (`app.py`), que adiciona novos `skos:altLabel` a um componente específico.

### **3. Processamento de Frases e Lógica Híbrida**
O `processador_frases.py` é o núcleo do assistente. Ele opera em duas fases:

1.  **Consulta Direta**: A função `consultar_frase()` normaliza o comando do usuário e realiza uma busca por correspondências exatas com os rótulos (`name` e `altLabel`) no grafo RDF. Se uma correspondência for encontrada, a ação é executada diretamente.
2.  **Consulta de Similaridade**: Se a busca direta falhar, a função `buscar_similaridade()` é ativada. O sistema envia um prompt detalhado, contendo as descrições das *Things* e os componentes disponíveis, para um modelo de linguagem (GPT-4o). O modelo é instruído a retornar uma lista JSON com os componentes mais relevantes, baseada em correspondência semântica e localização.

### **4. Interface Web (Flask)**
O módulo `app.py` é o responsável por centralizar a lógica da aplicação e servir a interface web para o usuário. Ele gerencia as seguintes rotas principais:

* **`/`**: Rota principal que renderiza a página `index.html`, onde o usuário pode inserir comandos.
* **`/processar`**: Recebe a frase e a localização do usuário via requisição `GET`. Chama `processar_frase()` e retorna uma resposta em JSON com o tipo de resultado (`CONCEITO`, `SIMILARIDADE` ou `INDEFINIDO`), que a interface web usa para exibir a resposta.
* **`/executar-acao`**: Recebe o `thing_uri`, `componente_name` e `componente_type` via `GET` e utiliza as funções `consulta_componente()` e `executar_conceito()` para realizar a ação na *Thing* física.
* **`/adicionar-informacao`**: Recebe uma frase via `POST` e chama `adicionar_frase()` para enriquecer o grafo com um novo `altLabel`.

---

## Bibliotecas Utilizadas

O projeto foi construído sobre uma pilha de bibliotecas Python, cada uma com uma função específica na arquitetura:

* **`flask`**: Microframework web utilizado para construir a interface de usuário e gerenciar as rotas da aplicação, servindo como ponto de entrada para a interação com o assistente.
* **`rdflib`** e **`rdflib-jsonld`**: Bibliotecas essenciais para a manipulação do grafo de conhecimento. O `rdflib` é o principal framework para trabalhar com RDF em Python, enquanto o `rdflib-jsonld` permite a conversão de `Thing Descriptions` (em JSON-LD) para o formato RDF.
* **`openai`**: Biblioteca oficial para interagir com a API da OpenAI, utilizada no módulo de processamento de frases para o modelo de linguagem GPT-4o na busca por similaridade.
* **`requests`**: Biblioteca para fazer requisições HTTP, usada tanto para consultar o `Thing Directory` quanto para interagir diretamente com os dispositivos (Things).
* **`zeroconf`**: Biblioteca que implementa o protocolo mDNS, fundamental para a descoberta automática do `Thing Directory` na rede local.
* **`dotenv`**: Utilizado para gerenciar variáveis de ambiente (como a chave da API da OpenAI), garantindo a segurança e portabilidade do projeto.
* **`netifaces`**: Ajuda a obter informações de rede, essenciais para a descoberta de serviços mDNS.

---

## Como Testar o Assistente

Para colocar o `assistant-wot` em funcionamento, você precisará de um ambiente de teste com um **Thing Directory** e, pelo menos, uma **Thing** disponível na rede.

### Setup de Teste

1.  **Thing Directory**: Certifique-se de ter um `Thing Directory` em execução, como o disponível em [https://github.com/AdryelliReiz/thing-directory](https://github.com/AdryelliReiz/thing-directory).
2.  **Thing**: Inicie um dispositivo inteligente que se anuncie para o `Thing Directory`. Você pode usar o `test_things/think_desktop_version.py` do projeto, que possui uma **Thing Description** bem estruturada e alinhada com as ontologias SOSA/SSN.

**Importante**: Inicie o `Thing Directory` antes da `Thing` para que a `Thing` possa se registrar corretamente.

### Instalação e Execução do `assistant-wot`

1.  **Pré-requisitos**: Certifique-se de ter o Python 3.8 ou superior instalado.
2.  **Instalação de Dependências**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Execução**:
    ```bash
    python main.py
    ```

Quando você executar `main.py`, o assistente iniciará o servidor web e consultará o `Thing Directory` para construir o seu grafo de conhecimento. É importante notar que, a cada nova execução, o grafo de conhecimento é **sobrescrito** com as informações mais atualizadas do diretório, e não mantém o conhecimento adquirido em sessões anteriores.

### Interação com a Interface Web

Acesse `localhost:5000` em seu navegador para interagir com o assistente. A página possui um campo para o comando e um para a localização do dispositivo. Para fazer consultas eficazes, você pode:

* **Buscar no Grafo**: Verifique a estrutura do grafo de conhecimento (`grafo.ttl`) para encontrar os rótulos alternativos (`altLabels`) e a propriedade de localização (`position`).
* **Comandos Iguais**: Se o seu comando for exatamente igual a um `altLabel`, o assistente o executará diretamente.
* **Comandos Semelhantes**: Se o seu comando for semanticamente semelhante, mas não idêntico, a interface retornará uma lista de sugestões. Ao escolher uma, o assistente aprenderá a associar sua frase à ação desejada para futuras interações.

---

## Sugestões de Possíveis Melhorias

O `assistant-wot` é um **MVP (Produto Mínimo Viável)** e, como tal, possui algumas limitações que abrem espaço para futuras melhorias e pesquisas aprofundadas. As seguintes sugestões de evolução representam o próximo estágio na maturidade do sistema.

### **1. Persistência e Sincronização Dinâmica do Grafo**

A arquitetura atual, por sobrescrever o grafo de conhecimento a cada inicialização, não mantém as informações aprendidas em sessões anteriores. Embora essa abordagem garanta que o sistema sempre trabalhe com dados atualizados do **Thing Directory**, ela impede que o conhecimento seja cumulativo e representa uma limitação significativa.

Uma melhoria crucial seria implementar um **mecanismo de sincronização inteligente**. A solução ideal não seria apenas adicionar novas *Things* ou ignorar a sobrescrita, mas sim realizar um **mapeamento dinâmico**. Esse mapeamento deve ser capaz de:

* **Adicionar** novas *Things* descobertas no **Thing Directory** ao grafo existente.
* **Atualizar** as informações de *Things* já presentes no grafo, caso suas **Thing Descriptions** tenham sido modificadas (por exemplo, com novas propriedades, ações ou eventos).
* **Remover** conhecimento obsoleto, como rótulos alternativos (`altLabels`) de componentes que foram excluídos da descrição original.

Essa funcionalidade avançada, embora complexa, permitiria que o grafo de conhecimento se tornasse uma base de dados robusta e persistente, capaz de aprender continuamente com as interações do usuário sem a perda de informações valiosas.

### **2. Aprimoramento da Localização e Distribuição Espacial**

Atualmente, o assistente utiliza a propriedade `position` das **Thing Descriptions** como uma simples referência ao cômodo onde a *Thing* está instalada. Embora isso ajude a diferenciar dispositivos semelhantes em ambientes distintos, o potencial dessa informação pode ser drasticamente expandido.

Em um projeto maior, o uso de um contexto mais rico, como coordenadas geoespaciais (`schema.org/GeoCoordinates`), poderia servir como base para um **sistema de controle de acesso refinado**. Por exemplo, um sistema implantado em um prédio com múltiplos apartamentos poderia conceder a cada morador acesso e controle exclusivo sobre as *Things* localizadas em seu espaço, sem interferir nos dispositivos vizinhos. Aprimorar o uso da localização e da distribuição espacial das *Things* permitiria o desenvolvimento de aplicações mais complexas e seguras, alinhadas com as necessidades de ambientes multiusuários.

### **3. Expansão do Mecanismo de Execução de Ações**

A funcionalidade de execução de ações do assistente está limitada a requisições HTTP com o método **GET**. Isso se deve à simplicidade do método, que não exige o envio de um corpo de requisição. Contudo, muitas ações em dispositivos IoT, como definir o estado ou a cor de uma lâmpada, requerem o uso de métodos como **POST** ou **PUT**, que obrigam a passagem de parâmetros no corpo da requisição.

O desafio central para a evolução é a **interpretação semântica de parâmetros**. Se o assistente recebe um comando como `"Mudar a cor da lâmpada para vermelho"`, ele precisa ser capaz de:
1.  Identificar o comando principal (`Mudar a cor`).
2.  Extrair a informação do parâmetro (`vermelho`).
3.  Determinar o tipo de dado correto (por exemplo, uma `string` ou um código RGB como `#ff0000`).
4.  Formatar o dado bruto em um corpo de requisição JSON, XML ou outro formato, conforme especificado na **Thing Description**.

A melhor abordagem para lidar com essa complexidade é utilizar modelos de linguagem avançados, como o **GPT-4o**, para interpretar a intenção do usuário e extrair os parâmetros de forma inteligente. Isso transformaria a linguagem natural em dados estruturados, viabilizando o suporte completo a todos os métodos HTTP e até a outros protocolos (como CoAP, Socket e MQTT).

### **4. Reconhecimento de Voz**

A interface atual do assistente é baseada em texto. Embora funcional, a inclusão de um mecanismo de **reconhecimento de voz** facilitaria a interação, tornando-a mais conveniente e natural para o usuário. Essa melhoria elevaria a experiência de uso para um patamar mais alinhado com assistentes de voz comerciais, permitindo que os comandos sejam dados de forma mais fluida e intuitiva, especialmente em ambientes onde a digitação não é prática.