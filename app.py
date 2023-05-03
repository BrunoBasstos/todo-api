# /app.py
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
def home():
    """
    Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi/swagger')

@app.get('/auth')
@protect
def auth():
    return g.current_user.to_dict(), 200

@app.get('/usuario', tags=[usuario_tag])
@protect
def get_usuarios():
    """
    Retorna uma lista de todos os usuarios cadastrados na base de dados
    """
    if g.current_user.perfil != Perfil.ADMINISTRADOR:
        return [{
            "msg": "Acesso restrito a administradores.",
            "type": "authorization"
        }], 401

    session = Session()
    usuarios = session.query(Usuario).all()
    session.close()
    return [usuario.to_dict() for usuario in usuarios], 200


@app.get('/usuario/<int:id>', tags=[usuario_tag])
@protect
def get_usuario():
    """
    Retorna um usuario específico da base de dados
    """
    id = request.view_args['id']
    if g.current_user.perfil != Perfil.ADMINISTRADOR and g.current_user.id != id:
        return [{
            "msg": "Acesso ao perfil de terceiros é restrito a administradores.",
            "type": "authorization"
        }], 401

    session = Session()
    usuario = session.query(Usuario).filter(Usuario.id == id).first()
    session.close()
    if usuario is None:
        return [{
            "msg": "Usuário não encontrado.",
            "type": "not_found"
        }], 404

    return usuario.to_dict(), 200


@app.post('/usuario', tags=[usuario_tag])
def add_usuario(body: UsuarioSchema):
    """
    Adiciona um novo Usuario à base de dados
    """
    senha_criptografada = bcrypt.hashpw(body.senha.encode('utf-8'), bcrypt.gensalt())
    senha_str = senha_criptografada.decode('utf-8')
    usuario = Usuario(
        nome=body.nome,
        email=body.email,
        senha=senha_str
    )

    try:
        session = Session()
        session.add(usuario)
        session.commit()
        usuario_dict = usuario.to_dict()
        session.close()
        return usuario_dict, 200

    except IntegrityError as e:
        return [{
            "msg": "Já existe um usuário com este email.",
            "type": "integrity_error"
        }], 409

    except Exception as e:
        error_msg = "Não foi possível salvar novo item"
        raise UnprocessableEntity(error_msg)


@app.put('/usuario/<int:id>', tags=[usuario_tag])
@protect
def update_usuario(body: UsuarioUpdateSchema):
    """
    Atualiza um usuario específico da base de dados
    """
    id = request.view_args['id']
    session = Session()

    if g.current_user.perfil != Perfil.ADMINISTRADOR and g.current_user.id != id:
        return [{
            "msg": "Alteração de perfil de terceiros é restrito a administradores.",
            "type": "authorization"
        }], 401

    usuario = session.query(Usuario).filter(Usuario.id == id).first()
    usuario.nome = body.nome if body.nome is not None else usuario.nome
    usuario.email = body.email if body.email is not None else usuario.email
    usuario.perfil = body.perfil if body.perfil is not None else usuario.perfil
    if body.senha is not None:
        senha_criptografada = bcrypt.hashpw(body.senha.encode('utf-8'), bcrypt.gensalt())
        usuario.senha = senha_criptografada.decode('utf-8')

    try:
        session.commit()
        usuario_dict = usuario.to_dict()
        session.close()
        return usuario_dict, 200
    except IntegrityError as e:
        return [{
            "msg": "Já existe um usuário com este email.",
            "type": "integrity_error"
        }], 409


@app.delete('/usuario/<int:id>', tags=[usuario_tag])
@protect
def delete_usuario():
    """
    Deleta um usuario específico da base de dados
    """
    id = request.view_args['id']
    session = Session()

    if g.current_user.perfil != Perfil.ADMINISTRADOR and g.current_user.id != id:
        return [{
            "msg": "Exclusão de perfil de terceiros é restrito a administradores.",
            "type": "authorization"
        }], 401

    try:
        usuario = session.query(Usuario).filter_by(id=id).first()
        session.delete(usuario)
        session.commit()
        session.close()
        return [{
            "msg": "Usuário excluído com sucesso.",
            "type": "success"
        }], 200
    except Exception as e:
        error_msg = "Não foi possível excluir o usuário"
        raise UnprocessableEntity(error_msg)


@app.get('/tarefa', tags=[tarefa_tag])
@protect
def get_tarefas():
    """
    Retorna uma lista de todas as tarefas cadastradas na base de dados
    """
    session = Session()

    if g.current_user.perfil == Perfil.ADMINISTRADOR:
        tarefas = session.query(Tarefa).order_by(
            Tarefa.usuario_id,
            Prioridade.case_order(Tarefa.prioridade)
        ).all()
    else:
        usuario_id = g.current_user.id
        tarefas = session.query(Tarefa).filter_by(usuario_id=usuario_id).order_by(
            Prioridade.case_order(Tarefa.prioridade)
        ).all()

    session.close()
    return [tarefa.to_dict() for tarefa in tarefas], 200


@app.get('/tarefa/<int:id>', tags=[tarefa_tag])
@protect
def get_tarefa():
    """
    Retorna uma tarefa específica da base de dados
    """
    id = request.view_args['id']
    session = Session()
    tarefa = session.query(Tarefa).filter(Tarefa.id == id).first()
    session.close()
    if tarefa is None:
        return [{
            "msg": "Tarefa não encontrada.",
            "type": "not_found"
        }], 404

    if g.current_user.perfil != Perfil.ADMINISTRADOR and g.current_user.id != tarefa.usuario_id:
        return [{
            "msg": "Acesso a tarefas de terceiros é restrito a administradores.",
            "type": "authorization"
        }], 401

    return tarefa.to_dict(), 200


@app.post('/tarefa', tags=[tarefa_tag])
@protect
def add_tarefa(body: TarefaSchema):
    """
    Adiciona uma nova Tarefa à base de dados
    """
    session = Session()

    if not Status.is_valid(body.status.value):
        error_msg = "Status inválido."
        raise UnprocessableEntity(error_msg)

    if not Prioridade.is_valid(body.prioridade.value):
        error_msg = "Prioridade inválida."
        raise UnprocessableEntity(error_msg)

    usuario = g.current_user
    if usuario is None:
        error_msg = "Usuario não encontrado."
        raise UnprocessableEntity(error_msg)

    tarefa = Tarefa(
        titulo=body.titulo,
        descricao=body.descricao,
        prioridade=body.prioridade,
        status=Status(body.status),
        usuario_id=usuario.id
    )

    try:
        session.add(tarefa)
        session.commit()
        tarefa_dict = tarefa.to_dict()
        session.close()
        return tarefa_dict, 200

    except Exception as e:
        error_msg = "Não foi possível salvar novo item."
        raise UnprocessableEntity(error_msg)


@app.put('/tarefa/<int:id>', tags=[tarefa_tag])
@protect
def update_tarefa(body: TarefaSchema):
    """
    Atualiza uma tarefa específica da base de dados
    """
    session = Session()
    id = request.view_args['id']

    if not Status.is_valid(body.status.value):
        error_msg = "Status inválido."
        raise UnprocessableEntity(error_msg)

    if not Prioridade.is_valid(body.prioridade.value):
        error_msg = "Prioridade inválida."
        raise UnprocessableEntity(error_msg)

    tarefa = session.query(Tarefa).filter(Tarefa.id == id).first()
    if tarefa is None:
        error_msg = "Tarefa não encontrada."
        raise UnprocessableEntity(error_msg)

    usuario = session.query(Usuario).filter_by(id=body.usuario_id).first()
    if usuario is None:
        error_msg = "Usuario não encontrado."
        raise UnprocessableEntity(error_msg)

    if g.current_user.perfil != Perfil.ADMINISTRADOR and (
            g.current_user.id != tarefa.usuario_id or g.current_user.id != body.usuario_id):
        return [{
            "msg": "Alteração de tarefas de terceiros é restrito a administradores.",
            "type": "authorization"
        }], 401

    tarefa.titulo = body.titulo
    tarefa.descricao = body.descricao
    tarefa.status = body.status
    tarefa.prioridade = body.prioridade
    tarefa.usuario_id = body.usuario_id

    if body.status == Status.CONCLUIDA and tarefa.data_conclusao is None:
        tarefa.data_conclusao = datetime.now()

    if body.status != Status.CONCLUIDA:
        tarefa.data_conclusao = None

    session.commit()
    tarefa_dict = tarefa.to_dict()
    session.close()
    return tarefa_dict, 200


@app.delete('/tarefa/<int:id>', tags=[tarefa_tag])
@protect
def delete_tarefa():
    """
    Deleta uma tarefa específica da base de dados
    """
    try:
        id = request.view_args['id']
        session = Session()
        tarefa = session.query(Tarefa).filter_by(id=id).first()
        session.delete(tarefa)
        session.commit()
        session.close()
        return [{
            "msg": "Usuário excluído com sucesso.",
            "type": "success"
        }], 200
    except Exception as e:
        error_msg = "Não foi possível deletar item."
        raise UnprocessableEntity(error_msg)


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

    return [{
        **usuario.to_dict(),
        "access_token": token
    }], 200


if __name__ == '__main__':
    app.run()
