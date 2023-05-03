# ToDo API

Este é um MVP para conclusão da primeira sprint do curso de pós graduação em engenharia de software pela PUC-Rio.

A ToDo API é uma aplicação Flask que permite o gerenciamento de tarefas a serem realizadas, incluindo a adição, edição e remoção de usuários, tarefas e prioridades. A API é protegida por autenticação de usuário e utiliza a biblioteca JWT para geração de tokens de acesso.

Além disso, este projeto é composto por uma aplicação React que consome a API para fornecer uma interface amigável ao usuário. O repositório da aplicação pode ser encontrado em [todo-front](https://github.com/BrunoBasstos/todo-front).

## Rotas implementadas

- `GET /`: Redireciona para a tela de escolha do estilo de documentação.
- `GET /auth`: Retorna os dados do usuário autenticado.
- `GET /usuario`: Retorna uma lista de todos os usuários cadastrados na base de dados.
- `GET /usuario/<int:id>`: Retorna um usuário específico da base de dados.
- `POST /usuario`: Adiciona um novo usuário à base de dados.
- `PUT /usuario/<int:id>`: Atualiza um usuário específico da base de dados.
- `DELETE /usuario/<int:id>`: Deleta um usuário específico da base de dados.
- `GET /tarefa`: Retorna uma lista de todas as tarefas cadastradas na base de dados.
- `GET /tarefa/<int:id>`: Retorna uma tarefa específica da base de dados.
- `POST /tarefa`: Adiciona uma nova tarefa à base de dados.
- `PUT /tarefa/<int:id>`: Atualiza uma tarefa específica da base de dados.
- `DELETE /tarefa/<int:id>`: Deleta uma tarefa específica da base de dados.
- `GET /prioridade`: Retorna uma lista de todas as prioridades cadastradas na base de dados.
- `GET /status`: Retorna uma lista de todos os status cadastrados na base de dados.
- `POST /login`: Realiza a autenticação do usuário.

## Tecnologias utilizadas

- Flask
- Flask OpenAPI3
- Flask CORS
- Pydantic
- SQLAlchemy
- JWT
- Bcrypt
- SQLite
- Docker

## Pré-requisitos

Antes de executar o projeto, certifique-se de ter instalado:

- Python 3.6 ou superior: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- pip (geralmente já incluído com Python): [https://pip.pypa.io/en/stable/installation/](https://pip.pypa.io/en/stable/installation/)
- Docker (caso deseje executar o projeto usando Docker): [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

## Como executar

1. Clone o repositório.
2. Crie e ative um ambiente virtual Python 3.
    1. No Windows, utilize o comando `python -m venv venv` para criar o ambiente virtual e `venv\Scripts\activate` para ativá-lo.
    2. No Linux, utilize o comando `python3 -m venv venv` para criar o ambiente virtual e `source venv/bin/activate` para ativá-lo.
3. Instale as dependências do projeto com o comando `pip install -r requirements.txt`.
4. Inicie a aplicação com o comando `python app.py`.
5. Acesse a documentação da API em `http://localhost:5000/openapi/swagger`.

## Como executar com Docker

1. Clone o repositório.
2. Abrir o terminal na pasta do projeto.
3. Executar o comando `docker build -t todo-api .`.
4. Executar o comando `docker run --name todo-api -p 5000:5000 todo-api`.
    1. Note que isto criará um container com o nome todo-api. Para reiniciar a aplicação nas próximas vezes, basta executar o comando `docker start todo-api`. Caso você queira remover o container, execute `docker rm -f todo-api`.

## Observações

Para facilitar o uso da API, foi criado um usuário administrador padrão com o email `admin@mail.com` e a senha `admin1234`.

## Contribuições

Contribuições são sempre bem-vindas! Se você deseja contribuir com este projeto, por favor, abra uma issue para discutir sua ideia antes de submeter um pull request.

## Licença

Este projeto está licenciado sob a licença MIT.
