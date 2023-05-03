# /schemas/usuario.py
from pydantic import BaseModel, Field, validator, EmailStr

class LoginSchema(BaseModel):
    """
    Define como uma solicitação de login deve ser representado
    """
    nome: str = Field(example="Joe Doe", description="Nome do usuário")
    email: str = Field(example="joedoe@email.com", description="Email do usuário")
    senha: str = Field(example="12345", description="Senha do usuário")

    @validator('nome')
    def nome_must_be_str(cls, v):
        if not isinstance(v, str) or v == '':
            raise ValueError('Nome deve ser uma string')
        return v

    @validator('senha')
    def senha_must_be_greater_than_5(cls, v):
        if len(v) < 5:
            raise ValueError('Senha deve ter no mínimo 5 caracteres')
        return v

    #     override EmailStr validator to translate its error message
    @validator('email')
    def email_must_be_valid(cls, v):
        try:
            return EmailStr.validate(v)
        except ValueError as e:
            raise ValueError('Formato de Email inválido') from e

