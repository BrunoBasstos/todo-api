from pydantic import BaseModel
from typing import Optional, List
from schemas import TarefaSchema


class UsuarioSchema(BaseModel):
    """
    Define como um novo usuario a ser inserido deve ser representado
    """
    nome: str = "Joe Doe"
    email: str = "joedoe@email.com"
    senha: str = "123456"
    tarefas: Optional[List[TarefaSchema]] = None
