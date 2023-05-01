# /enums/status.py
from enum import Enum


class Status(Enum):
    PENDENTE = 'pendente'
    EM_ANDAMENTO = 'em andamento'
    CONCLUIDA = 'concluída'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def is_valid(cls, status: str):
        return status in cls._value2member_map_

    @classmethod
    def get(cls, status: str):
        return cls._value2member_map_[status]
