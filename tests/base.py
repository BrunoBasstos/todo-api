import jwt
import pytest
from flask_testing import TestCase
from app import app
from models import Base, engine, Session, Usuario
from utils.middleware import SECRET_KEY
from datetime import datetime, timedelta


class BaseTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def setup_mocker(self, mocker):
        self.mocker = mocker

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        Base.metadata.create_all(engine)
        self.session = Session()
        usuario = Usuario(nome="Usuário Base", email="email@base.com", senha="123456")
        self.session.add(usuario)
        self.session.commit()
        self.auth_token = self.create_auth_token(usuario.id)

    def tearDown(self):
        Base.metadata.drop_all(engine)
        self.session.close()

    def create_auth_token(self, user_id):
        token_payload = {
            'exp': datetime.utcnow() + timedelta(minutes=1),
            'sub': user_id,
            'usuario': 'Teste'
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')
        return token

    def get_default_test_header(self):
        return {'Authorization': f'Bearer {self.auth_token}'}
