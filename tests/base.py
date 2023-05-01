from flask_testing import TestCase
from app import app
import pytest
from models import Base, engine, Session


class BaseTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def setup_mocker(self, mocker):
        self.mocker = mocker
        with app.test_request_context():
            self.mocker.patch('utils.middleware.request')

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        Base.metadata.create_all(engine)
        self.session = Session()

    def tearDown(self):
        Base.metadata.drop_all(engine)
        self.session.close()
