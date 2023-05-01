from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from flask import g, redirect, request
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import UnprocessableEntity
from models import Session, Usuario, Tarefa
from schemas import *
import jwt
import bcrypt
from datetime import datetime, timedelta
from utils.middleware import protect, SECRET_KEY

info = Info(title="ToDo API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

usuario_tag = Tag(name="Usuario", description="Incluir, alterar, visualizar e remover usuarios")
tarefa_tag = Tag(name="Tarefa", description="Incluir, alterar, visualizar e remover tarefas")
status_tag = Tag(name="Status", description="Listar os status disponíveis")
prioridade_tag = Tag(name="Prioridade", description="Listar as prioridades disponíveis")


@app.get('/')
@protect
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi/swagger')


@app.get('/usuario', tags=[usuario_tag])
@protect
def get_usuarios():
    """Retorna uma lista de todos os usuarios cadastrados na base de dados
    """
    if g.current_user.perfil != Perfil.ADMINISTRADOR:
        return [{
            "msg": "Acesso restrito a administradores.",
            "type": "authorization"
        }], 409
    session = Session()
    usuarios = session.query(Usuario).all()
    return [usuario.to_dict() for usuario in usuarios], 200


@app.get('/usuario/<id>', tags=[usuario_tag])
@protect
def get_usuario():
    """
    Retorna um usuario específico da base de dados
    """
    id = request.view_args['id']
    if g.current_user.perfil != Perfil.ADMINISTRADOR or g.current_user.id != id:
        return [{
            "msg": "Acesso ao perfil de terceiros é restrido a administradores.",
            "type": "authorization"
        }], 409

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
    if g.current_user.perfil != Perfil.ADMINISTRADOR:
        return [{
            "msg": "Acesso restrito a administradores.",
            "type": "authorization"
        }], 409
    senha_criptografada = bcrypt.hashpw(body.senha.encode('utf-8'), bcrypt.gensalt())
    senha_str = senha_criptografada.decode('utf-8')
    usuario = Usuario(
        nome=body.nome,
        email=body.email,
        senha=senha_str
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
        session.rollback()
        return [{
            "msg": "Já existe um usuário com este email.",
            "type": "integrity_error"
        }], 409

    except ValidationError as e:
        session.rollback()
        raise UnprocessableEntity(e.errors)

    except Exception as e:
        return {
            "msg": "Não foi possível salvar novo item.",
            "type": "unknown_error"
        }, 409


@app.put('/usuario/<id>', tags=[usuario_tag])
@protect
def update_usuario(body: UsuarioUpdateSchema):
    """
    Atualiza um usuario específico da base de dados
    """
    if g.current_user.perfil != Perfil.ADMINISTRADOR or g.current_user.id != id:
        return [{
            "msg": "Acesso ao perfil de terceiros é restrido a administradores.",
            "type": "authorization"
        }], 409

    id = request.view_args['id']
    session = Session()
    usuario = session.query(Usuario).filter(Usuario.id == id).first()
    usuario.nome = body.nome if body.nome is not None else usuario.nome
    usuario.email = body.email if body.email is not None else usuario.email
    usuario.senha = body.senha if body.senha is not None else usuario.senha
    session.commit()
    return usuario.to_dict(), 200


@app.delete('/usuario/<id>', tags=[usuario_tag])
@protect
def delete_usuario():
    """
    Deleta um usuario específico da base de dados
    """
    if g.current_user.perfil != Perfil.ADMINISTRADOR or g.current_user.id != id:
        return [{
            "msg": "Acesso ao perfil de terceiros é restrido a administradores.",
            "type": "authorization"
        }], 409
    id = request.view_args['id']
    session = Session()
    usuario = session.query(Usuario).filter_by(id=id).first()
    session.delete(usuario)
    session.commit()
    return usuario.to_dict(), 200


@app.get('/tarefa', tags=[tarefa_tag])
@protect
def get_tarefas():
    """
    Retorna uma lista de todas as tarefas cadastradas na base de dados
    """
    session = Session()

    if g.current_user.perfil == Perfil.ADMINISTRADOR:
        tarefas = session.query(Tarefa).order_by('usuario_id').all()
    else:
        usuario_id = g.current_user.id
        tarefas = session.query(Tarefa).fiilter_by(id=usuario_id).all()

    return [tarefa.to_dict() for tarefa in tarefas], 200


@app.get('/tarefa/<id>', tags=[tarefa_tag])
@protect
def get_tarefa():
    """
    Retorna uma tarefa específica da base de dados
    """
    id = request.view_args['id']
    session = Session()
    tarefa = session.query(Tarefa).filter(Tarefa.id == id).first()

    if g.current_user.perfil != Perfil.ADMINISTRADOR or g.current_user.id != tarefa.user_id:
        return [{
            "msg": "Acesso a tarefas de terceiros é restrido a administradores.",
            "type": "authorization"
        }], 409

    if tarefa is None:
        return [{
            "msg": "Tarefa não encontrada.",
            "type": "not_found"
        }], 404

    return tarefa.to_dict(), 200


@app.post('/tarefa', tags=[tarefa_tag])
@protect
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
    usuario = session.query(Usuario).filter_by(id=body.usuario_id).first()
    if usuario is None:
        error_msg = "Usuario não encontrado."
        raise UnprocessableEntity(error_msg)

    tarefa = Tarefa(
        titulo=body.titulo,
        descricao=body.descricao,
        prioridade=body.prioridade,
        status=Status(body.status),
        usuario_id=body.usuario_id)

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
@protect
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
@protect
def update_tarefa(body: TarefaSchema):
    """
    Atualiza uma tarefa específica da base de dados
    """
    session = Session()
    usuario = session.query(Usuario).filter_by(id=body.usuario_id).first()
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
    tarefa.usuario_id = body.usuario_id
    session.commit()
    return tarefa.to_dict(), 200


@app.delete('/tarefa/<id>', tags=[tarefa_tag])
@protect
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


@app.get('/prioridade', tags=[prioridade_tag])
@protect
def get_prioridades():
    """
    Retorna uma lista de todas as prioridades cadastradas na base de dados
    """
    return [prioridade.value for prioridade in Prioridade], 200


@app.get('/status', tags=[status_tag])
@protect
def get_status():
    """
    Retorna uma lista de todos os status cadastrados na base de dados
    """
    return [status.value for status in Status], 200


@app.post('/login')
def login():
    email = request.json.get('email')
    senha = request.json.get('senha')
    session = Session()
    usuario = session.query(Usuario).filter_by(email=email).first()

    if usuario is None or not bcrypt.checkpw(senha.encode('utf-8'), usuario.senha.encode('utf-8')):
        return [{"msg": "Credenciais inválidas"}], 401

    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'sub': usuario.id,
        'usuario': usuario.nome
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    # retornar o usuario e o token
    return [{
        **usuario.to_dict(),
        "access_token": token
    }], 200


if __name__ == '__main__':
    app.run()
