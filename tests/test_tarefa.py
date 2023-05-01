import json
from enums import Prioridade, Status
from tests.base import BaseTestCase
from models import Usuario, Tarefa


class TestTarefa(BaseTestCase):
    def test_get_tarefas(self):
        tarefa1 = Tarefa(titulo="Tarefa 1", descricao="Descrição da tarefa 1", status=Status.PENDENTE, usuario=1,
                         prioridade=Prioridade.ALTA)
        tarefa2 = Tarefa(titulo="Tarefa 2", descricao="Descrição da tarefa 2", status=Status.PENDENTE, usuario=1,
                         prioridade=Prioridade.BAIXA)

        self.session.add_all([tarefa1, tarefa2])
        self.session.commit()

        response = self.client.get('/tarefa')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)

        d = data[0]["usuario"]

        self.assertEqual(data[0]["titulo"], "Tarefa 1")
        self.assertEqual(data[1]["titulo"], "Tarefa 2")

    def test_get_tarefa_by_id(self):
        tarefa1 = Tarefa(titulo="Tarefa 1", descricao="Descrição da tarefa 1", status=Status.PENDENTE, usuario=1,
                         prioridade=Prioridade.ALTA)
        tarefa2 = Tarefa(titulo="Tarefa 2", descricao="Descrição da tarefa 2", status=Status.PENDENTE, usuario=1,
                         prioridade=Prioridade.BAIXA)

        self.session.add_all([tarefa1, tarefa2])
        self.session.commit()

        response = self.client.get(f'/tarefa/{tarefa1.id}')
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], tarefa1.id)
        self.assertEqual(data['titulo'], tarefa1.titulo)
        self.assertEqual(data['descricao'], tarefa1.descricao)

        id_invalido = max(tarefa1.id, tarefa2.id) + 1
        response = self.client.get(f'/tarefa/{id_invalido}')
        self.assertEqual(response.status_code, 404)

    def test_add_tarefa(self):
        payload = {
            'titulo': 'Tarefa de Teste',
            'descricao': 'Descrição da tarefa de teste',
            'status': 'pendente',
            'prioridade': 'alta',
            'usuario': 1
        }
        response = self.client.post('/tarefa', json=payload)
        self.assertEqual(response.status_code, 422)
        response_data = response.get_data(as_text=True)
        self.assertIn('Usuario não encontrado', response_data)

        # add user
        usuario = Usuario(nome="Teste", email="teste@mail.com", senha="123456")
        self.session.add(usuario)
        self.session.commit()

        # send request again
        response = self.client.post('/tarefa', json=payload)
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['titulo'], payload['titulo'])
        self.assertEqual(data['descricao'], payload['descricao'])
        self.assertEqual(data['status'], payload['status'])
        self.assertEqual(data['prioridade'], payload['prioridade'])
        self.assertEqual(data['usuario'], payload['usuario'])

    def test_update_tarefa(self):
        tarefa = Tarefa(titulo="Tarefa 1", descricao="Descrição da tarefa 1", status=Status.PENDENTE, usuario=1,
                        prioridade=Prioridade.ALTA)
        self.session.add(tarefa)
        self.session.commit()

        payload = {
            'titulo': 'Tarefa de Teste',
            'descricao': 'Descrição da tarefa de teste',
            'status': 'pendente',
            'prioridade': 'alta',
            'usuario': 1
        }
        response = self.client.put(f'/tarefa/{tarefa.id}', json=payload)
        self.assertEqual(response.status_code, 422)
        response_data = response.get_data(as_text=True)
        self.assertIn('Usuario não encontrado', response_data)

        # add user
        usuario = Usuario(nome="Teste", email="teste@mail.com", senha="123456")
        self.session.add(usuario)
        self.session.commit()

        # send request again
        response = self.client.put(f'/tarefa/{tarefa.id}', json=payload)
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['titulo'], payload['titulo'])
        self.assertEqual(data['descricao'], payload['descricao'])
        self.assertEqual(data['status'], payload['status'])
        self.assertEqual(data['prioridade'], payload['prioridade'])
        self.assertEqual(data['usuario'], payload['usuario'])

    def test_delete_tarefa(self):
        tarefa = Tarefa(titulo="Tarefa 1", descricao="Descrição da tarefa 1", status=Status.PENDENTE, usuario=1,
                        prioridade=Prioridade.ALTA)
        self.session.add(tarefa)
        self.session.commit()

        response = self.client.delete(f'/tarefa/{tarefa.id}')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f'/tarefa/{tarefa.id}')
        self.assertEqual(response.status_code, 404)
