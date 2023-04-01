from dataclasses import dataclass
from typing import List

from src.domain.enums.concessionaria_enum import ConcessionariaEnum


@dataclass
class Alojamento:
    concessionaria: ConcessionariaEnum
    nome: str = ''
    diretorio: str = ''
    cliente: str = ''
    conta: str = ''
    local: str = ''

class PoolAlojamentos:
    alojamentos= []

    def __init__(self, alojamentos: List[Alojamento]):
        self.alojamentos = alojamentos

    def get_alojamento(self, cliente: str, conta: str, local: str):
        def filtro(el: Alojamento):            
            if el.cliente and (el.cliente != cliente):
                return False

            if el.conta and (el.conta != conta):
                return False

            if el.local and (el.local != local):
                return False

            return True

        result = [x for x in self.alojamentos if filtro(x)]

        if (len(result) != 1):
            return None
 
        return result[0]

