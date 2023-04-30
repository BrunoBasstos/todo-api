from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from flask import redirect, request
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import UnprocessableEntity

from enums import Prioridade
from enums.status import Status
from models import Session, Usuario, Tarefa
from schemas import *

info = Info(title="ToDo API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

usuario_tag = Tag(name="Usuario", description="Incluir, alterar, visualizar e remover usuarios")
tarefa_tag = Tag(name="Tarefa", description="Incluir, alterar, visualizar e remover tarefas")


@app.get('/')
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi/swagger')


@app.get('/usuario', tags=[usuario_tag])
def get_usuarios():
    """Retorna uma lista de todos os usuarios cadastrados na base de dados
    """
    session = Session()
    usuarios = session.query(Usuario).all()
    return [usuario.to_dict() for usuario in usuarios], 200


@app.get('/usuario/<id>', tags=[usuario_tag])
def get_usuario():
    """
    Retorna um usuario específico da base de dados
    """
    id = request.view_args['id']
    session = Session()
    usuario = session.query(Usuario).filter(Usuario.id == id).first()

    if usuario is None:
        return {"message": "Usuario não encontrado"}, 404

    return usuario.to_dict(), 200


@app.post('/usuario', tags=[usuario_tag])
def add_usuario(body: UsuarioSchema):
    """
    Adiciona um novo Usuario à base de dados
    """
    usuario = Usuario(
        nome=body.nome,
        email=body.email,
        senha=body.senha
    )

    try:
        # criando conexão com a base
        session = Session()
        # adicionando usuario
        session.add(usuario)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        return usuario.to_dict(), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Usuario de mesmo nome já salvo na base."
        return {"message": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item."
        return {"message": error_msg}, 409


@app.put('/usuario/<id>', tags=[usuario_tag])
def update_usuario(body: UsuarioUpdateSchema):
    """
    Atualiza um usuario específico da base de dados
    """
    id = request.view_args['id']
    session = Session()
    usuario = session.query(Usuario).filter(Usuario.id == id).first()
    usuario.nome = body.nome if body.nome is not None else usuario.nome
    usuario.email = body.email if body.email is not None else usuario.email
    usuario.senha = body.senha if body.senha is not None else usuario.senha
    session.commit()
    return usuario.to_dict(), 200


@app.delete('/usuario/<id>', tags=[usuario_tag])
def delete_usuario():
    """
    Deleta um usuario específico da base de dados
    """
    id = request.view_args['id']
    session = Session()
    usuario = session.query(Usuario).filter_by(id=id).first()
    session.delete(usuario)
    session.commit()
    return usuario.to_dict(), 200


@app.get('/tarefa', tags=[tarefa_tag])
def get_tarefas():
    """
    Retorna uma lista de todas as tarefas cadastradas na base de dados
    """
    session = Session()
    tarefas = session.query(Tarefa).all()
    return [tarefa.to_dict() for tarefa in tarefas], 200


@app.get('/tarefa/<id>', tags=[tarefa_tag])
def get_tarefa():
    """
    Retorna uma tarefa específica da base de dados
    """
    id = request.view_args['id']
    session = Session()
    tarefa = session.query(Tarefa).filter(Tarefa.id == id).first()

    if tarefa is None:
        return {"message": "Tarefa não encontrada"}, 404

    return tarefa.to_dict(), 200


@app.post('/tarefa', tags=[tarefa_tag])
def add_tarefa(body: TarefaSchema):
    """
    Adiciona uma nova Tarefa à base de dados
    """

    # validate body.status is a valid Status
    if not Status.is_valid(body.status.value):
        error_msg = "Status inválido."
        raise UnprocessableEntity(error_msg)

    # validate body.prioridade is a valid Prioridade
    if not Prioridade.is_valid(body.prioridade.value):
        error_msg = "Prioridade inválida."
        raise UnprocessableEntity(error_msg)

    # validate body.usuario is a valid Usuario
    session = Session()
    usuario = session.query(Usuario).filter_by(id=body.usuario).first()
    if usuario is None:
        error_msg = "Usuario não encontrado."
        raise UnprocessableEntity(error_msg)

    tarefa = Tarefa(
        titulo=body.titulo,
        descricao=body.descricao,
        prioridade=body.prioridade,
        status=Status(body.status),
        usuario=body.usuario)

    try:
        # criando conexão com a base
        session = Session()
        # adicionando tarefa
        session.add(tarefa)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        return tarefa.to_dict(), 200


    except IntegrityError as e:

        # como a duplicidade do nome é a provável razão do IntegrityError

        error_msg = "Tarefa de mesmo nome já salvo na base."

        raise UnprocessableEntity(error_msg)


    except Exception as e:

        # caso um erro fora do previsto

        error_msg = "Não foi possível salvar novo item."

        raise UnprocessableEntity(error_msg)


@app.post('/tarefa/{id}/complete', tags=[tarefa_tag])
def complete_tarefa(id: int):
    """
    Marca uma tarefa específica como concluída na base de dados
    """
    session = Session()
    tarefa = session.query(Tarefa).filter_by(id=id).first()
    tarefa.status = "completa"
    session.commit()
    return tarefa.to_dict(), 200


@app.put('/tarefa/<id>', tags=[tarefa_tag])
def update_tarefa(body: TarefaSchema):
    """
    Atualiza uma tarefa específica da base de dados
    """
    session = Session()
    usuario = session.query(Usuario).filter_by(id=body.usuario).first()
    if usuario is None:
        error_msg = "Usuario não encontrado."
        raise UnprocessableEntity(error_msg)

    id = request.view_args['id']
    session = Session()
    tarefa = session.query(Tarefa).filter_by(id=id).first()
    tarefa.titulo = body.titulo
    tarefa.descricao = body.descricao
    tarefa.status = body.status
    tarefa.prioridade = body.prioridade
    tarefa.usuario = body.usuario
    session.commit()
    return tarefa.to_dict(), 200


@app.delete('/tarefa/<id>', tags=[tarefa_tag])
def delete_tarefa():
    """
    Deleta uma tarefa específica da base de dados
    """
    id = request.view_args['id']
    session = Session()
    tarefa = session.query(Tarefa).filter_by(id=id).first()
    session.delete(tarefa)
    session.commit()
    return tarefa.to_dict(), 200


if __name__ == '__main__':
    app.run()
