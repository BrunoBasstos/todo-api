from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List

from schemas import TarefaSchema


class UsuarioViewSchema(BaseModel):
    """
    Define a representação visual de um usuario
    """
    id: Optional[int] = Field(None, example=1, description="ID do usuário")
    nome: str = Field(..., example="Joe Doe", description="Nome do usuário")
    email: str = Field(..., example="joedoe@email.com", description="Email do usuário")
    # tarefas: Optional[List[TarefaSchema]] = None


class UsuarioSchema(BaseModel):
    """
    Define como um novo usuario a ser inserido deve ser representado
    """
    nome: str = Field(example="Joe Doe", description="Nome do usuário")
    email: EmailStr = Field(example="joedoe@email.com", description="Email do usuário")
    senha: str = Field(example="123456", description="Senha do usuário")
    tarefas: Optional[List[TarefaSchema]] = None

    @validator('nome')
    def nome_must_be_str(cls, v):
        if not isinstance(v, str):
            raise ValueError('Nome deve ser uma string')
        return v

    @validator('senha')
    def senha_must_be_greater_than_5(cls, v):
        if len(v) < 6:
            raise ValueError('Senha deve ter no mínimo 5 caracteres')
        return v


class UsuarioUpdateSchema(UsuarioSchema):
    """
    Define como um usuario a ser atualizado deve ser representado
    """
    id: Optional[int] = Field(None, example=1, description="ID do usuário")
    nome: Optional[str] = Field(None, example="Joe Doe", description="Nome do usuário")
    email: Optional[EmailStr] = Field(None, example="joedoe@email.com", description="Email do usuário")
    senha: Optional[str] = Field(None, example="123456", description="Senha do usuário")
    tarefas: Optional[List[TarefaSchema]] = None


class UsuarioDeleteSchema(BaseModel):
    """
    Define como deve ser a estrutura retornada ao deletar um usuario
    """
    mesage: str
    nome: str


class UsuarioSearchSchema(BaseModel):
    """
    Define como um novo usuario a ser inserido deve ser representado
    """
    nome: Optional[str] = Field(None, example="Joe Doe", description="Nome do usuário")
    email: Optional[str] = Field(None, example="joedoe@email.com", description="Email do usuário")
