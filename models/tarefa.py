# /models/tarefa.py
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from typing import Union
from enums import Prioridade, Status
from models import Base


class Tarefa(Base):
    __tablename__ = 'tarefa'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(4000))
    data_insercao = Column(DateTime, default=func.now(), nullable=False)
    data_conclusao = Column(DateTime, nullable=True)
    status = Column(Enum(Status), nullable=False)
    prioridade = Column(Enum(Prioridade), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id", ondelete='CASCADE'), nullable=False)

    usuario = relationship("Usuario", back_populates="tarefas", lazy='joined')

    def __init__(self, titulo: str, descricao: str, status: Status, prioridade: Prioridade, usuario_id: int,
                 data_insercao: Union[DateTime, None] = None, data_conclusao: Union[DateTime, None] = None):
        """
        Cria uma Tarefa

        Arguments:
            titulo: o titulo de uma tarefa.
            descricao: a descrição de uma tarefa.
            status: o status de uma tarefa.
            prioridade: a prioridade de uma tarefa.
            usuario_id: o id do usuário que criou a tarefa
            data_insercao: data de quando a tarefa foi feita ou inserida
                           à base
            data_conclusao: data de quando a tarefa foi concluída
        """
        self.titulo = titulo
        self.descricao = descricao
        self.status = status
        self.prioridade = prioridade
        self.usuario_id = usuario_id
        if data_insercao:
            self.data_insercao = data_insercao
        if data_conclusao:
            self.data_conclusao = data_conclusao

    def __repr__(self):
        return f"<Tarefa {self.titulo}>"

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "data_insercao": self.data_insercao,
            "data_conclusao": self.data_conclusao,
            "status": self.status.value,
            "prioridade": self.prioridade.value,
            "usuario_id": self.usuario_id,
            "usuario": self.usuario.to_dict() if self.usuario is not None else None
        }
