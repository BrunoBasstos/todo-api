import json
from tests.base import BaseTestCase
from models import Usuario


class TestUsuario(BaseTestCase):

    def test_get_usuarios(self):
        # Add some test data
        user1 = Usuario(nome="Test User 1", email="test1@email.com", senha="test123")
        user2 = Usuario(nome="Test User 2", email="test2@email.com", senha="test123")

        self.session.add(user1)
        self.session.add(user2)
        self.session.commit()

        # Make a request to the get_usuarios route
        response = self.client.get('/usuario')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)

        # Check if the data in the response is correct
        self.assertEqual(data[0]["nome"], "Test User 1")
        self.assertEqual(data[1]["nome"], "Test User 2")

    def test_get_usuario_by_id(self):
        # Add sample data to the test database
        user1 = Usuario(nome='User1', email='user1@example.com', senha='password1')
        user2 = Usuario(nome='User2', email='user2@example.com', senha='password2')

        self.session.add(user1)
        self.session.add(user2)
        self.session.commit()

        # Perform the test
        response = self.client.get(f'/usuario/{user1.id}')
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], user1.id)
        self.assertEqual(data['nome'], user1.nome)
        self.assertEqual(data['email'], user1.email)

        # Test non-existent user
        id_invalido = max(user1.id, user2.id) + 1
        response = self.client.get(f'/usuario/{id_invalido}')
        self.assertEqual(response.status_code, 404)

    def test_add_usuario(self):
        # Perform the test
        payload = {
            'nome': 'Usuário de Teste',
            'email': 'teste@email.com',
            'senha': 'teste123'
        }
        response = self.client.post('/usuario', json=payload)
        data = response.json
        print(data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['nome'], 'Usuário de Teste')
        self.assertEqual(data['email'], 'teste@email.com')

        user = self.session.query(Usuario).filter(Usuario.id == data['id']).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.nome, 'Usuário de Teste')
        self.assertEqual(user.email, data['email'])

    def test_update_usuario(self):
        # Add sample data to the test database
        user = Usuario(nome='Usuário Teste', email='usuarioteste@mail.com', senha='teste1234')
        self.session.add(user)
        self.session.commit()

        # Perform the test
        payload = {
            'nome': 'Usuário Teste Alterado',
            'email': 'emailalterado@mail.com'
        }
        response = self.client.put(f'/usuario/{user.id}', json=payload)
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['nome'], 'Usuário Teste Alterado')
        self.assertEqual(data['email'], 'emailalterado@mail.com')

    def test_delete_usuario(self):
        # Add sample data to the test database
        user = Usuario(nome='Usuário Teste', email='usuario@email.com', senha='teste1234')
        self.session.add(user)
        self.session.commit()

        # Perform the test
        response = self.client.delete(f'/usuario/{user.id}')
        self.assertEqual(response.status_code, 200)

        user = self.session.query(Usuario).filter(Usuario.id == user.id).first()
        self.assertIsNone(user)
