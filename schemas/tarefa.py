# /schemas/tarefa.py
from pydantic import BaseModel, Field, validator
from enums import Prioridade, Status
from datetime import datetime


class TarefaSchema(BaseModel):
    titulo: str = Field(example="Comprar pão", description="O título da tarefa")
    descricao: str = Field(example="Ir na padaria da esquina", description="A descrição da tarefa")
    status: Status = Field(example=Status.PENDENTE, description="O status da tarefa")
    prioridade: Prioridade = Field(example=Prioridade.ALTA, description="A prioridade da tarefa")
    usuario_id: int = Field(example=1, description="O id do usuário que criou a tarefa")
    data_insercao: datetime = Field(default=datetime.now(), description="A data de inserção da tarefa")
    data_conclusao: datetime = Field(default=None, description="A data de conclusão da tarefa", nullable=True)

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
