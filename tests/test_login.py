import bcrypt

from tests.base import BaseTestCase
from models import Usuario


class TestLogin(BaseTestCase):

    def test_user_login(self):
        # Add sample data to the test database
        senha = 'teste123'
        senha_bcrypt = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        senha_bcrypt_string = senha_bcrypt.decode('utf-8')

        user = Usuario(nome='Usuário Teste', email="teste@mail.com", senha=senha_bcrypt_string)
        self.session.add(user)
        self.session.commit()

        # Perform the test
        payload = {
            'email': user.email,
            'senha': senha
        }

        response = self.client.post('/login', json=payload)
        data = response.json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data[0]['nome'], user.nome)
        self.assertEqual(data[0]['email'], user.email)
        self.assertIsNotNone(data[0]['access_token'])

    def test_user_login_invalid_email(self):
        # Add sample data to the test database
        senha = 'teste123'
        senha_bcrypt = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        senha_bcrypt_string = senha_bcrypt.decode('utf-8')

        user = Usuario(nome='Usuário Teste', email='teste@email.com', senha=senha_bcrypt_string)
        self.session.add(user)
        self.session.commit()

        # Perform the test
        payload = {
            'email': 'teste_errado@email.com',
            'senha': senha
        }

        response = self.client.post('/login', json=payload)
        data = response.json
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data[0]['msg'], 'Credenciais inválidas')

    def test_user_login_invalid_password(self):
        # Add sample data to the test database
        senha = 'teste123'
        senha_bcrypt = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        senha_bcrypt_string = senha_bcrypt.decode('utf-8')

        user = Usuario(nome='Usuário Teste', email='teste@mail.com', senha=senha_bcrypt_string)
        self.session.add(user)
        self.session.commit()

        # Perform the test
        payload = {
            'email': user.email,
            'senha': 'senha_errada'
        }

        response = self.client.post('/login', json=payload)
        data = response.json
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data[0]['msg'], 'Credenciais inválidas')
