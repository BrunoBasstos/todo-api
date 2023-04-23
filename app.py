from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
from flask import redirect
from sqlalchemy.exc import IntegrityError
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


@app.get('/usuario/{id}', tags=[usuario_tag])
def get_usuario(id: int):
    """Retorna um usuario específico da base de dados
    """
    session = Session()
    usuario = session.query(Usuario).filter_by(id=id).first()
    return usuario.to_dict(), 200


@app.post('/usuario', tags=[usuario_tag])
def add_usuario(form: UsuarioSchema):
    """Adiciona um novo Usuario à base de dados
    """
    usuario = Usuario(
        nome=form.nome,
        email=form.email,
        senha=form.senha)

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
        error_msg = "Usuario de mesmo nome já salvo na base :/"
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        return {"mesage": error_msg}, 409


@app.delete('/usuario/{id}', tags=[usuario_tag])
def delete_usuario(id: int):
    """Deleta um usuario específico da base de dados
    """
    session = Session()
    usuario = session.query(Usuario).filter_by(id=id).first()
    session.delete(usuario)
    session.commit()
    return usuario.to_dict(), 200


@app.get('/tarefa', tags=[tarefa_tag])
def get_tarefas():
    """Retorna uma lista de todas as tarefas cadastradas na base de dados
    """
    session = Session()
    tarefas = session.query(Tarefa).all()
    return [tarefa.to_dict() for tarefa in tarefas], 200


@app.get('/tarefa/{id}', tags=[tarefa_tag])
def get_tarefa(id: int):
    """Retorna uma tarefa específica da base de dados
    """
    session = Session()
    tarefa = session.query(Tarefa).filter_by(id=id).first()
    return tarefa.to_dict(), 200


@app.post('/tarefa', tags=[tarefa_tag])
def add_tarefa(form: TarefaSchema):
    """Adiciona uma nova Tarefa à base de dados
    """
    tarefa = Tarefa(
        titulo=form.titulo,
        descricao=form.descricao,
        prioridade=form.prioridade,
        status=form.status,
        usuario=form.usuario)

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
        error_msg = "Tarefa de mesmo nome já salvo na base :/"
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        return {"mesage": error_msg}, 409


@app.post('/tarefa/{id}/complete', tags=[tarefa_tag])
def complete_tarefa(id: int):
    """Marca uma tarefa específica como concluída na base de dados
    """
    session = Session()
    tarefa = session.query(Tarefa).filter_by(id=id).first()
    tarefa.status = "completa"
    session.commit()
    return tarefa.to_dict(), 200


@app.put('/tarefa/{id}', tags=[tarefa_tag])
def update_tarefa(id: int, form: TarefaSchema):
    """Atualiza uma tarefa específica da base de dados
    """
    session = Session()
    tarefa = session.query(Tarefa).filter_by(id=id).first()
    tarefa.titulo = form.titulo
    tarefa.descricao = form.descricao
    tarefa.status = form.status
    tarefa.prioridade = form.prioridade
    tarefa.usuario_id = form.usuario_id
    session.commit()
    return tarefa.to_dict(), 200


@app.delete('/tarefa/{id}', tags=[tarefa_tag])
def delete_tarefa(id: int):
    """Deleta uma tarefa específica da base de dados
    """
    session = Session()
    tarefa = session.query(Tarefa).filter_by(id=id).first()
    session.delete(tarefa)
    session.commit()
    return tarefa.to_dict(), 200


if __name__ == '__main__':
    app.run()
