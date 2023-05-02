# /tests/test_usuario.py
import json

from enums import Perfil
from tests.base import BaseTestCase
from models import Usuario


class TestUsuario(BaseTestCase):

    def test_admin_can_get_usuarios(self):
        admin = self.createUser(Perfil.ADMINISTRADOR.value)
        usuario = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(admin.id)

        response = self.client.get('/usuario', headers=self.get_default_test_header())
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(data[len(data) - 2]["nome"], admin.nome)
        self.assertEqual(data[len(data) - 1]["nome"], usuario.nome)

    def test_user_cannot_get_usuarios(self):
        usuario1 = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario1.id)

        response = self.client.get('/usuario', headers=self.get_default_test_header())
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data[0]['type'], 'authorization')

    def test_get_usuario_by_id(self):
        usuario1 = self.createUser(Perfil.USUARIO.value)
        usuario2 = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario1.id)

        response = self.client.get(f'/usuario/{usuario1.id}', headers=self.get_default_test_header())
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], usuario1.id)
        self.assertEqual(data['nome'], usuario1.nome)
        self.assertEqual(data['email'], usuario1.email)

    def test_user_cannot_see_other_user(self):
        usuario1 = self.createUser(Perfil.USUARIO.value)
        usuario2 = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario1.id)

        response = self.client.get(f'/usuario/{usuario2.id}', headers=self.get_default_test_header())
        data = response.json

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data[0]['type'], 'authorization')

    def test_admin_can_see_other_user(self):
        admin = self.createUser(Perfil.ADMINISTRADOR.value)
        usuario = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(admin.id)

        response = self.client.get(f'/usuario/{usuario.id}', headers=self.get_default_test_header())
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], usuario.id)
        self.assertEqual(data['nome'], usuario.nome)
        self.assertEqual(data['email'], usuario.email)

    def test_add_usuario(self):
        payload = {
            'nome': self.fake.name(),
            'email': self.fake.email(),
            'senha': self.fake.password()
        }
        response = self.client.post('/usuario', json=payload, headers=self.get_default_test_header())
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['nome'], payload['nome'])
        self.assertEqual(data['email'], payload['email'])

        user = self.session.query(Usuario).filter(Usuario.id == data['id']).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.nome, payload['nome'])
        self.assertEqual(user.nome, data['nome'])
        self.assertEqual(user.email, payload['email'])
        self.assertEqual(user.email, data['email'])

    def test_add_duplicated_usuario(self):
        usuario = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario.id)

        payload = {
            'nome': self.fake.name(),
            'email': usuario.email,
            'senha': self.fake.password()
        }

        response = self.client.post('/usuario', json=payload, headers=self.get_default_test_header())
        data = response.json
        self.assertEqual(response.status_code, 409)
        self.assertEqual(data[0]['msg'], 'Já existe um usuário com este email.')

    def test_update_usuario(self):
        usuario = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario.id)

        # Perform the test
        payload = {
            'nome': 'Usuário Teste Alterado',
            'email': 'emailalterado@mail.com'
        }
        response = self.client.put(f'/usuario/{usuario.id}', json=payload, headers=self.get_default_test_header())
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['nome'], 'Usuário Teste Alterado')
        self.assertEqual(data['email'], 'emailalterado@mail.com')

    def test_delete_usuario(self):
        usuario = self.createUser(Perfil.USUARIO.value)
        self.auth_token = self.create_auth_token(usuario.id)

        response = self.client.delete(f'/usuario/{usuario.id}', headers=self.get_default_test_header())
        self.assertEqual(response.status_code, 200)

        user = self.session.query(Usuario).filter(Usuario.id == usuario.id).first()
        self.assertIsNone(user)
