from pydantic import BaseModel, Field
from enums.status import Status


class TarefaSchema(BaseModel):
    """
    Define como uma nova tarefa a ser inserida deve ser representada
    """
    titulo: str = Field(example="Comprar pão", description="O título da tarefa")
    descricao: str = Field(example="Ir na padaria da esquina", description="A descrição da tarefa")
    status: Status = Field(example=Status.PENDENTE, description="O status da tarefa")
    prioridade: str = Field(min_length=1, max_length=20, example="Alta", description="A prioridade da tarefa")
    usuario: int = Field(example=1, description="O id do usuário que criou a tarefa")
