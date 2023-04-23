from pydantic import BaseModel
from models.tarefa import Tarefa

class TarefaSchema(BaseModel):
    """
    Define como uma nova tarefa a ser inserida deve ser representada
    """
    titulo: str = "Comprar pão"
    descricao: str = "Comprar pão na padaria da esquina"
    status: str = "A fazer"
    prioridade: str = "Alta"
    usuario_id: int = 1