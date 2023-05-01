# /enums/perfil.py
from enum import Enum


class Perfil(Enum):
    ADMINISTRADOR = 'administrador'
    USUARIO = 'usuário'

    # Outros perfis, se necessário

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def is_valid(cls, perfil: str):
        return perfil in cls._value2member_map_
