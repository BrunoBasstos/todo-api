# test cases para testar as rotas do app.py para o model de tarefas
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from app import app
from models import Session, create_engine, Tarefa, Usuario
from models.base import Base
from flask import json
from flask_testing import TestCase
from enums.status import Status


class TestTarefa(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=False)
        Base.metadata.create_all(engine)

        return app

    def setUp(self):
        session = Session()
        session.query(Tarefa).delete()
        session.query(Usuario).delete()
        session.commit()

        usuario1 = Usuario(nome='Usuario 1', email='usuario1@mail.com', senha='123456')
        usuario2 = Usuario(nome='Usuario 2', email='usuario2@mail.com', senha='123456')
        session.add_all([usuario1, usuario2])
        session.commit()

        tarefa1 = Tarefa(titulo='Tarefa 1', usuario=usuario1.id, descricao='Teste 1', status=Status.A_FAZER,
                         prioridade='Alta')
        tarefa2 = Tarefa(titulo='Tarefa 2', usuario=usuario1.id, descricao='Teste 2', status=Status.EM_ANDAMENTO,
                         prioridade='Baixa')
        tarefa3 = Tarefa(titulo='Tarefa 3', usuario=usuario1.id, descricao='Teste 3', status=Status.CONCLUIDA,
                         prioridade='Média')
        session.add_all([tarefa1, tarefa2, tarefa3])
        session.commit()

    def tearDown(self):
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=False)
        Base.metadata.drop_all(engine)

    def test_get_tarefas(self):
        response = self.client.get('/tarefa')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['titulo'], 'Tarefa 1')
        self.assertEqual(data[0]['usuario'], 1)
        self.assertEqual(data[1]['titulo'], 'Tarefa 2')
        self.assertEqual(data[1]['usuario'], 1)

    def test_create_tarefa(self):
        tarefa_data = {
            'titulo': 'Teste Criação Tarefa',
            'descricao': 'Tarefa criada via teste automatizado.',
            'status': 'a fazer',
            'prioridade': 'Alta',
            'usuario': 1
        }

        response = self.client.post('/tarefa', json=tarefa_data)
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['titulo'], 'Teste Criação Tarefa')
        self.assertEqual(data['descricao'], 'Tarefa criada via teste automatizado.')
        self.assertEqual(data['status'], 'a fazer')
        self.assertEqual(data['prioridade'], 'Alta')
        self.assertEqual(data['usuario'], 1)

    def test_get_tarefa(self):
        response = self.client.get('/tarefas/1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['titulo'], 'Tarefa 1')
        self.assertEqual(data['usuario'], 1)

    def test_get_tarefa_inexistente(self):
        response = self.client.get('/tarefas/3')
