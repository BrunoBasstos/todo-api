# /enums/prioridade.py
from enum import Enum


class Prioridade(Enum):
    ALTA = 'alta'
    MEDIA = 'média'
    BAIXA = 'baixa'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def is_valid(cls, status: str):
        return status in cls._value2member_map_
