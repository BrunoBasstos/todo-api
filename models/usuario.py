# /models/usuario.py
from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.orm import relationship

from enums import Perfil
from models import Base


class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    senha = Column(String(100), nullable=False)
    perfil = Column(Enum(Perfil), nullable=False, default=Perfil.USUARIO)

    tarefas = relationship("Tarefa", back_populates="usuario")

    def __init__(self, nome: str, email: str, senha: str, perfil: Perfil = Perfil.USUARIO):
        """
        Cria um Usuario

        Arguments:
            nome: o nome de um usuario.
            email: o email de um usuario.
            senha: a senha de um usuario.
        """
        self.nome = nome
        self.email = email
        self.perfil = perfil
        self.senha = senha

    def __repr__(self):
        return f"<Usuario {self.nome}>"

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "perfil": self.perfil.value
        }
