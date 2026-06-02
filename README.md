# 🎬 Sistema de Gestão de Filmes — API (Back-end)

Projeto de API REST desenvolvido como MVP para a disciplina de **Desenvolvimento Front-end Avançado** da PUC-Rio.

## 🎯 Objetivo
Apresentar o comportamento da arquitetura de uma API REST e demonstrar como o Back-end atua como o núcleo de processamento, garantindo a integridade dos dados e comunicando-se simultaneamente com:

* **Interface (Front-end):** Provendo os dados necessários para a experiência do usuário através de contratos de interface sólidos.
* **API Externa (TMDB):** Realizando a ponte para busca de dados dinâmicos e metadados de filmes em tempo real através do The Movie Database (TMDB).
* **Persistência Local (SQLite):** Garantindo o armazenamento seguro das regras de negócio e cadastros através do ORM SQLAlchemy.

## 🛠️ Tecnologias Utilizadas
* **Python 3.x & Flask:** Micro-framework para a construção da API, focado em performance e desacoplamento.
* **SQLAlchemy:** ORM para abstração e manipulação do banco de dados, garantindo a consistência das entidades.
* **SQLite:** Banco de dados relacional para persistência de regras de negócio e cadastros.
* **OpenAPI 3 / Swagger:** Documentação interativa da API, servindo como contrato de comunicação para o Front-end.
* **Docker:** Containerização para garantir portabilidade e consistência entre ambientes de desenvolvimento e execução.

## 🏗️ Comportamento da Arquitetura
A API foi desenhada para seguir os princípios REST, atuando como o *Gatekeeper* da aplicação e garantindo:

* **Validação de Payloads:** Toda requisição proveniente do Front-end é validada antes de qualquer interação com o banco, garantindo que apenas dados íntegros sejam processados.
* **Integração com TMDB:** O sistema realiza requisições HTTP para a API externa para alimentar o catálogo de filmes, garantindo dados sempre atualizados sem necessidade de armazenamento local massivo.
* **Padronização:** As respostas são entregues em formato JSON, facilitando o consumo pelo Front-end que roda de forma independente, assegurando um contrato de interface previsível e testável.

## 🚀 Como Executar
Para iniciar a API e acessar a documentação interativa via **Swagger**, siga os passos abaixo:

1. Certifique-se de estar com o ambiente virtual ativado e as dependências instaladas.
2. Execute o comando abaixo no terminal na raiz do projeto:

```bash
python app.py
