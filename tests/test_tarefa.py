# /tests/test_tarefa.py
import json
from enums import Prioridade, Status, Perfil
from tests.base import BaseTestCase
from models import Usuario, Tarefa


class TestTarefa(BaseTestCase):
    def test_get_tarefas(self):
        usuario = self.createUser(Perfil.ADMINISTRADOR.value)
        self.auth_token = self.create_auth_token(usuario.id)

        tarefa1 = Tarefa(titulo="Tarefa 1", descricao="Descrição da tarefa 1", status=Status.PENDENTE,
                         usuario_id=usuario.id, prioridade=Prioridade.ALTA)
        tarefa2 = Tarefa(titulo="Tarefa 2", descricao="Descrição da tarefa 2", status=Status.PENDENTE,
                         usuario_id=usuario.id, prioridade=Prioridade.BAIXA)
        self.session.add_all([tarefa1, tarefa2])
        self.session.commit()

        response = self.client.get('/tarefa', headers=self.get_default_test_header())
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)

        d = data[0]["usuario"]

        self.assertEqual(data[0]["titulo"], "Tarefa 1")
        self.assertEqual(data[1]["titulo"], "Tarefa 2")

    def test_user_dont_see_other_users_tarefas(self):
        usuario1 = self.createUser(Perfil.USUARIO.value)
        usuario2 = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario1.id)

        tarefa1 = Tarefa(titulo="Tarefa 1", descricao="Descrição da tarefa 1", status=Status.PENDENTE,
                         usuario_id=usuario1.id, prioridade=Prioridade.ALTA)
        tarefa2 = Tarefa(titulo="Tarefa 2", descricao="Descrição da tarefa 2", status=Status.PENDENTE,
                         usuario_id=usuario2.id, prioridade=Prioridade.BAIXA)
        self.session.add_all([tarefa1, tarefa2])
        self.session.commit()

        response = self.client.get('/tarefa', headers=self.get_default_test_header())
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]["titulo"], "Tarefa 1")

    def test_admin_can_see_other_users_tarefas(self):
        usuario1 = self.createUser(Perfil.ADMINISTRADOR.value)
        usuario2 = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario1.id)

        tarefa1 = Tarefa(titulo="Tarefa 1", descricao="Descrição da tarefa 1", status=Status.PENDENTE,
                         usuario_id=usuario1.id, prioridade=Prioridade.ALTA)
        tarefa2 = Tarefa(titulo="Tarefa 2", descricao="Descrição da tarefa 2", status=Status.PENDENTE,
                         usuario_id=usuario2.id, prioridade=Prioridade.BAIXA)
        self.session.add_all([tarefa1, tarefa2])
        self.session.commit()

        response = self.client.get('/tarefa', headers=self.get_default_test_header())
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]["titulo"], "Tarefa 1")
        self.assertEqual(data[1]["titulo"], "Tarefa 2")

    def test_get_tarefa_by_id(self):
        usuario = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario.id)

        tarefa1 = Tarefa(titulo="Tarefa 1", descricao="Descrição da tarefa 1", status=Status.PENDENTE,
                         usuario_id=usuario.id, prioridade=Prioridade.ALTA)
        tarefa2 = Tarefa(titulo="Tarefa 2", descricao="Descrição da tarefa 2", status=Status.PENDENTE,
                         usuario_id=usuario.id, prioridade=Prioridade.BAIXA)

        self.session.add_all([tarefa1, tarefa2])
        self.session.commit()

        response = self.client.get(f'/tarefa/{tarefa1.id}', headers=self.get_default_test_header())
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], tarefa1.id)
        self.assertEqual(data['titulo'], tarefa1.titulo)
        self.assertEqual(data['descricao'], tarefa1.descricao)

        id_invalido = max(tarefa1.id, tarefa2.id) + 1
        response = self.client.get(f'/tarefa/{id_invalido}', headers=self.get_default_test_header())
        self.assertEqual(response.status_code, 404)

    def test_add_tarefa(self):
        usuario = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario.id)

        payload = {
            'titulo': 'Tarefa de Teste',
            'descricao': 'Descrição da tarefa de teste',
            'status': 'pendente',
            'prioridade': 'alta',
            'usuario_id': 0
        }

        response = self.client.post('/tarefa', json=payload, headers=self.get_default_test_header())
        self.assertEqual(response.status_code, 422)
        response_data = response.get_data(as_text=True)
        self.assertIn('Usuario não encontrado', response_data)

        payload = {
            'titulo': 'Tarefa de Teste',
            'descricao': 'Descrição da tarefa de teste',
            'status': 'pendente',
            'prioridade': 'alta',
            'usuario_id': usuario.id
        }
        # send request again
        response = self.client.post('/tarefa', json=payload, headers=self.get_default_test_header())
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['titulo'], payload['titulo'])
        self.assertEqual(data['descricao'], payload['descricao'])
        self.assertEqual(data['status'], payload['status'])
        self.assertEqual(data['prioridade'], payload['prioridade'])
        self.assertEqual(data['usuario_id'], payload['usuario_id'])

    def test_update_tarefa(self):
        usuario = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario.id)
        outroUsuario = self.createUser(Perfil.USUARIO.value)

        tarefa = Tarefa(titulo="Tarefa 1", descricao="Descrição da tarefa 1", status=Status.PENDENTE,
                        usuario_id=usuario.id, prioridade=Prioridade.ALTA)
        self.session.add(tarefa)
        self.session.commit()

        payload = {
            'titulo': 'Tarefa de Teste',
            'descricao': 'Descrição da tarefa de teste',
            'status': 'pendente',
            'prioridade': 'alta',
            'usuario_id': outroUsuario.id
        }

        response = self.client.put(f'/tarefa/{tarefa.id}', json=payload, headers=self.get_default_test_header())
        self.assertEqual(response.status_code, 401)
        response_data = response.get_data(as_text=True)
        self.assertIn('restrito a administradores', response_data)

        payload['usuario_id'] = usuario.id

        # send request again
        response = self.client.put(f'/tarefa/{tarefa.id}', json=payload, headers=self.get_default_test_header())
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['titulo'], payload['titulo'])
        self.assertEqual(data['descricao'], payload['descricao'])
        self.assertEqual(data['status'], payload['status'])
        self.assertEqual(data['prioridade'], payload['prioridade'])
        self.assertEqual(data['usuario_id'], payload['usuario_id'])

    def test_delete_tarefa(self):
        usuario = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario.id)

        tarefa = Tarefa(titulo="Tarefa 1", descricao="Descrição da tarefa 1", status=Status.PENDENTE,
                        usuario_id=usuario.id, prioridade=Prioridade.ALTA)
        self.session.add(tarefa)
        self.session.commit()

        response = self.client.delete(f'/tarefa/{tarefa.id}', headers=self.get_default_test_header())
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f'/tarefa/{tarefa.id}', headers=self.get_default_test_header())
        self.assertEqual(response.status_code, 404)
