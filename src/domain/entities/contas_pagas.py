from dataclasses import dataclass
from typing import List


from src.domain.enums import (ConcessionariaEnum, TipoServicoEnum)

@dataclass
class ContaPaga():
    nome_concessionaria: str
    nome_tipo_servico: str
    nome_alojamento: str
    id_documento: str
    dt_emissao: str

class PoolContasPagas:
    def __init__(self, contas: List[ContaPaga]):
        self.contas = contas

    def exists(self, concessionaria: ConcessionariaEnum, tipo_servico: TipoServicoEnum, nome_alojamento: str, id_documento: str) -> bool:
        def achou(conta):
            return conta.nome_alojamento == nome_alojamento and conta.id_documento == id_documento and conta.nome_concessionaria == ConcessionariaEnum(concessionaria).name and conta.nome_tipo_servico == TipoServicoEnum(tipo_servico).name

        for conta in self.contas:
            if (achou(conta)):
                return True

        return False

    @property
    def count(self)->int:
        return len(self.contas)
