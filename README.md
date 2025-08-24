# Desenvolvimento de uma Proposta de Integração da Arquitetura de Web of Things com a Ontologia SOSA/SSN

## Introdução
Este projeto visa explorar e desenvolver uma aplicação baseada na **Web of Things (WoT)**, alinhando-a com a **Ontologia SOSA/SSN** para criar um protótipo aplicado a **domótica** ou **casas inteligentes**. O objetivo é contribuir para a interoperabilidade de dispositivos de IoT, permitindo a troca de informações de maneira autônoma e confiável. A proposta envolve o uso de tecnologias semânticas que ajudam a integrar dados de IoT com contextos de aplicação mais amplos, especialmente através da anotação semântica de dispositivos e dados.

## Objetivos
### Objetivo Geral
Desenvolver uma aplicação protótipo que integre a arquitetura Web of Things com a Ontologia SOSA/SSN, aplicável ao contexto de domótica.

### Objetivos Específicos
1. Estudar a ferramenta WoTPy e as ontologias SOSA/SSN.
2. Criar um alinhamento das ontologias SOSA/SSN com a proposta da W3C.
3. Desenvolver ou reutilizar uma ontologia de domínio específica para domótica e integrá-la com as ontologias existentes.
4. Implementar e validar um protótipo de aplicação de domótica baseada em WoTPy, usando as ontologias estudadas.

## Ferramentas Utilizadas
- **WoTPy**: Ferramenta que implementa as recomendações da W3C para Web of Things.
- **Protégé**: Software para criação e manipulação de ontologias.
- **RDF (Resource Description Framework)** e **OWL (Ontology Web Language)**: Tecnologias para modelagem semântica.
- **SPARQL**: Linguagem de consulta para grafos RDF.
- **Python**: Linguagem de programação principal para o desenvolvimento da aplicação.

## Entregáveis
### 1. Repositório de Armazenamento de Dados
- **Descrição**: Repositório de dados aprimorado, utilizando grafos RDF para armazenamento de medições e dados semânticos.
- **Funcionalidade**: Compatível com WoTPy, permite consultas complexas com SPARQL, garantindo interoperabilidade entre Thing Description (TD) e SOSA/SSN.
- **Desafios**: Ajustar o formato de medições entre TD e SOSA para assegurar consistência semântica.

### 2. Dispositivo IoT Melhorado
- **Descrição**: Dispositivo atualizado para registrar affordances (TD:*Affordances) e possibilitar uma troca de dados padronizada com o repositório.
- **Desafios Técnicos**: Os dispositivos existentes utilizam C (com DNS-SD) e MicroPython. Para suportar descoberta de serviços em Python, adaptações como a biblioteca [micropython-mdns](https://github.com/cbrand/micropython-mdns) serão utilizadas.

### 3. GLAgent Melhorado
- **Descrição**: O GLAgent será aprimorado para realizar consultas semânticas ao diretório de coisas e ao repositório de dados, integrando consultas SPARQL com suporte a alinhamento TD-SOSA/SSN.
- **Funcionalidade**: O agente poderá buscar dispositivos e dados com base em affordances, possibilitando a composição automática de dispositivos.
- **Desafios**: Manter o alinhamento entre TD e SOSA no GLAgent, permitindo buscas e integrações semânticas.

## Alinhamento entre TD e SOSA/SSN
O alinhamento entre **Thing Description (TD)** e **SOSA/SSN** é essencial para garantir interoperabilidade entre dispositivos e serviços. Este processo transversal afetará todos os entregáveis, unificando o formato e a estrutura de dados, facilitando a interoperabilidade entre dispositivos, armazenamento e consultas.

## Estrutura do Projeto
- **/assistent-wot**: Projeto principal desenvolvido durante a pesquisa — assistente inteligente baseado em WoT.
- **/test_things**: Conjunto de dispositivos (Things) criados para testes e validação de funcionalidades de forma isolada.

## Discentes Responsáveis
- **José de Jesús Pérez Alcázar** (Proponente) - EACH/USP
- **Fabio Nakano** (Co-orientador) - EACH/USP
- **Adryelli Reis** (Bolsista) - USP, aluna de Sistemas de Informação

## Licença
Este projeto está licenciado sob a **Licença MIT**, permitindo a reprodução e modificação com os devidos créditos ao autor original. Consulte o arquivo `LICENSE` para mais detalhes.

---

Este README oferece uma visão geral do projeto e sua organização, facilitando a compreensão e o acompanhamento do progresso e resultados obtidos.
