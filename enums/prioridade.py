# /enums/prioridade.py
from enum import Enum
from sqlalchemy import case


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

    @classmethod
    def get(cls, prioridade: str):
        return cls._value2member_map_[prioridade]

    @classmethod
    def case_order(cls, prioridade: str):
        prioridade_conditions = [
            (prioridade == "alta", 1),
            (prioridade == "média", 2),
            (prioridade == "baixa", 3),
        ]

        return case(*prioridade_conditions, else_=4)
