# /tests/base.py
import jwt
import pytest
from flask_testing import TestCase
from app import app
from enums import Perfil
from models import Base, engine, Session, Usuario
from utils.middleware import SECRET_KEY
from datetime import datetime, timedelta
from faker import Faker


class BaseTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def setup_mocker(self, mocker):
        self.mocker = mocker

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        self.fake = Faker()
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

    def createUser(self, perfil):
        if not Perfil.is_valid(perfil):
            perfil = Perfil.USUARIO.value

        usuario = Usuario(
            nome=self.fake.name(),
            email=self.fake.email(),
            senha=self.fake.password(),
            perfil=Perfil.get(perfil)
        )
        self.session.add(usuario)
        self.session.commit()

        return usuario

    def getOrCreateUser(self, perfil):
        if not Perfil.is_valid(perfil):
            perfil = Perfil.USUARIO.value

        usuario = self.session.query(Usuario).filter_by(perfil=Perfil.get(perfil)).first()
        if not usuario:
            usuario = self.createUser(perfil)

        return usuario
