# /models/__init__.py
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

from enums import Perfil
from models.base import Base
from models.usuario import Usuario
from models.tarefa import Tarefa


def create_default_admin_user(session):
    admin_email = "admin@email.com"
    admin_password = "admin1234"

    admin_exists = session.query(Usuario).filter(Usuario.email == admin_email).first()

    if not admin_exists:
        admin = Usuario(nome="Administrador Padrão", email=admin_email, senha=admin_password,
                        perfil=Perfil.ADMINISTRADOR)
        session.add(admin)
        session.commit()


db_path = "database/"

if not os.path.exists(db_path):
    os.makedirs(db_path)

db_url = 'sqlite:///%s/db.sqlite3' % db_path

engine = create_engine(db_url, echo=False)

Session = sessionmaker(bind=engine)

if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)
session = Session()
create_default_admin_user(session)
