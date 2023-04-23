from pydantic import BaseModel
from enums.status import Status
from models.tarefa import Tarefa

class TarefaSchema(BaseModel):
    """
    Define como uma nova tarefa a ser inserida deve ser representada
    """
    titulo: str = "Comprar pão"
    descricao: str = "Comprar pão na padaria da esquina"
    status: str = Status.A_FAZER
    prioridade: str = "Alta"
    usuario: int = 1