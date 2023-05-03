# /schemas/tarefa.py
from typing import Optional
from pydantic import BaseModel, Field, validator
from enums import Prioridade, Status
from datetime import datetime


class TarefaSchema(BaseModel):
    """
    Define como uma nova tarefa a ser inserida deve ser representado
    """
    titulo: str = Field(example="Comprar pão", description="O título da tarefa")
    descricao: str = Field(example="Ir na padaria da esquina", description="A descrição da tarefa")
    status: Status = Field(example=Status.PENDENTE, description="O status da tarefa")
    prioridade: Prioridade = Field(example=Prioridade.ALTA, description="A prioridade da tarefa")
    usuario_id: Optional[int] = Field(example=1, description="O id do usuário que criou a tarefa")
    data_insercao: Optional[datetime] = Field(default=datetime.now(), description="A data de inserção da tarefa")
    data_conclusao: Optional[datetime] = Field(default=None, description="A data de conclusão da tarefa", nullable=True)

    @validator('titulo')
    def titulo_must_be_str(cls, v):
        if not isinstance(v, str) or v == '':
            raise ValueError('Título deve ser uma string')
        return v

    @validator('descricao')
    def descricao_must_be_str(cls, v):
        if not isinstance(v, str) or v == '':
            raise ValueError('Descrição deve ser uma string')
        return v


class TarefaUpdateSchema(TarefaSchema):
    """
    Define como uma tarefa a ser atualizado deve ser representado
    """
    id: int = Field(None, example=1, description="ID do usuário")


class TarefaIdSchema(BaseModel):
    """
    Define como uma tarefa a ser deletada deve ser representado
    """
    id: int = Field(None, example=1, description="ID da Tarefa")
