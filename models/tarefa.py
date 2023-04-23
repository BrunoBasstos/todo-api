from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from datetime import datetime
from typing import Union
from enums.status import Status

from models import Base


class Tarefa(Base):
    __tablename__ = 'tarefa'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(4000))
    data_insercao = Column(DateTime, default=datetime.now())
    data_conclusao = Column(DateTime, nullable=True)
    status = Column(Enum(Status), nullable=False)
    prioridade = Column(String(20), nullable=False)
    usuario = Column(Integer, ForeignKey("usuario.id"), nullable=False)

    def __init__(self, titulo: str, descricao: str, status: str, prioridade: str,
                 data_insercao: Union[DateTime, None] = None, data_conclusao: Union[DateTime, None] = None):
        """
        Cria uma Tarefa

        Arguments:
            titulo: o titulo de uma tarefa.
            descricao: a descrição de uma tarefa.
            status: o status de uma tarefa.
            prioridade: a prioridade de uma tarefa.
            data_insercao: data de quando a tarefa foi feita ou inserida
                           à base
            data_conclusao: data de quando a tarefa foi concluída
        """
        self.titulo = titulo
        self.descricao = descricao
        self.status = status
        self.prioridade = prioridade
        if data_insercao:
            self.data_insercao = data_insercao
        if data_conclusao:
            self.data_conclusao = data_conclusao
