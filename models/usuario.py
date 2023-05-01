from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from models import Base


class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    senha = Column(String(100), nullable=False)

    tarefas = relationship("Tarefa")

    def __init__(self, nome: str, email: str, senha: str):
        """
        Cria um Usuario

        Arguments:
            nome: o nome de um usuario.
            email: o email de um usuario.
            senha: a senha de um usuario.
        """
        self.nome = nome
        self.email = email
        self.senha = senha

    def __repr__(self):
        return f"<Usuario {self.nome}>"

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email
        }
