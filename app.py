# /app.py
from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from flask import g, redirect, request
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

docs_tag = Tag(name="Documentação", description="Documentação da API")
autenticacao_tag = Tag(name="Autenticação", description="Autenticação de usuários")
status_tag = Tag(name="Status", description="Listar os status disponíveis")
util_tag = Tag(name="Utils",
               description="Rotas para retornar informações úteis para a aplicação: lista de status, lista de prioridades e dados do usuário autenticado.")
usuario_tag = Tag(name="Usuario", description="Incluir, alterar, visualizar e remover usuarios", )
tarefa_tag = Tag(name="Tarefa", description="Incluir, alterar, visualizar e remover tarefas")


@app.get('/', tags=[docs_tag])
def home():
    """
    Redireciona para /openapi, tela que permite a escolha do estilo de documentação.

    Para efeitos didáticos e facilidade de uso, as requisições provenientes da documentação são autorizadas automaticamente.

    Para isso, foi criado um middleware que verifica se a requisição é originária da tela de documentação e, caso seja, o usuário administrador padrão criado na inicialização da aplicação é autorizado automaticamente.
    """
    return redirect('/openapi/swagger')


@app.post('/login', tags=[autenticacao_tag])
def login(body: LoginSchema):
    """
    Autentica um usuário e retorna uma instância do usuário autenticado com um token de acesso.

    Todas as rotas são protegidas por autenticação, exceto a rota de login e a rota de documentação.

    Para consumir as rotas protegidas, é necessário enviar o token de acesso obitido nesta rota no header Authorization, no formato Bearer <token>.
    """
    email = body.email
    senha = body.senha
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


@app.get('/auth', tags=[util_tag])
@protect
def auth():
    """
    Retorna o usuário autenticado com base no token de autenticação

    Usado para revalidação do Token em caso de refresh de página.
    """
    return g.current_user.to_dict(), 200


@app.get('/prioridade', tags=[util_tag])
@protect
def get_prioridades():
    """
    Retorna uma lista de todas as prioridades cadastradas na base de dados
    """
    return [prioridade.value for prioridade in Prioridade], 200


@app.get('/status', tags=[util_tag])
@protect
def get_status():
    """
    Retorna uma lista de todos os status cadastrados na base de dados
    """
    return [status.value for status in Status], 200


@app.get('/usuarios', tags=[usuario_tag])
@protect
def get_usuarios():
    """
    Retorna uma lista de todos os usuarios cadastrados na base de dados.

    Apenas administradores podem acessar essa rota.
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


@app.get('/usuario', tags=[usuario_tag])
@protect
def get_usuario(query: UsuarioIdSchema):
    """
    Retorna um usuario específico da base de dados.

    Apenas administradores podem acessar o perfil de terceiros.
    """
    id = query.id
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
    Adiciona um novo Usuario à base de dados.
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


@app.put('/usuario', tags=[usuario_tag])
@protect
def update_usuario(body: UsuarioUpdateSchema):
    """
    Atualiza um usuario específico da base de dados.
    """
    id = body.id
    session = Session()

    if g.current_user.perfil != Perfil.ADMINISTRADOR and g.current_user.id != id:
        return [{
            "msg": "Alteração de perfil de terceiros é restrito a administradores.",
            "type": "authorization"
        }], 401

    usuario = session.query(Usuario).filter(Usuario.id == id).first()

    usuario.nome = body.nome if body.nome is not None else usuario.nome
    if body.email is not None and body.email != usuario.email:
        usuario.email = body.email

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


@app.delete('/usuario', tags=[usuario_tag])
@protect
def delete_usuario(body: UsuarioIdSchema):
    """
    Deleta um usuario específico da base de dados.
    """
    id = body.id
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


@app.get('/tarefas', tags=[tarefa_tag])
@protect
def get_tarefas():
    """
    Retorna uma lista de todas as tarefas cadastradas na base de dados.
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


@app.get('/tarefa', tags=[tarefa_tag])
@protect
def get_tarefa(query: TarefaIdSchema):
    """
    Retorna uma tarefa específica da base de dados.
    """
    id = query.id
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
    Adiciona uma nova Tarefa à base de dados.
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


@app.put('/tarefa', tags=[tarefa_tag])
@protect
def update_tarefa(body: TarefaUpdateSchema):
    """
    Atualiza uma tarefa específica da base de dados.
    """
    session = Session()
    id = body.id

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


@app.delete('/tarefa', tags=[tarefa_tag])
@protect
def delete_tarefa(body: TarefaIdSchema):
    """
    Deleta uma tarefa específica da base de dados.
    """
    try:
        id = body.id
        session = Session()
        tarefa = session.query(Tarefa).filter_by(id=id).first()
        session.delete(tarefa)
        session.commit()
        session.close()
        return [{
            "msg": "Tarefa excluída com sucesso.",
            "type": "success"
        }], 200
    except Exception as e:
        error_msg = "Não foi possível deletar item."
        raise UnprocessableEntity(error_msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
