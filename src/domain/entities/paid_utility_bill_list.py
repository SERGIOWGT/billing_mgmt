from dataclasses import dataclass
from typing import List
from src.domain.entities.paid_utility_bill import PaidUtilityBill
from src.domain.enums import (ServiceProviderEnum, ServiceTypeEnum)


@dataclass
class PaidUtilityBillList:
    def __init__(self, contas: List[PaidUtilityBill]):
        self.contas = contas

    def exists(self, concessionaria: ServiceProviderEnum, tipo_servico: ServiceTypeEnum, nome_Accommodation: str, id_documento: str) -> bool:
        def achou(conta):
            return conta.nome_Accommodation == nome_Accommodation and conta.id_documento == id_documento and conta.nome_concessionaria == ServiceProviderEnum(concessionaria).name and conta.nome_tipo_servico == ServiceTypeEnum(tipo_servico).name

        for conta in self.contas:
            if (achou(conta)):
                return True

        return False

    @property
    def count(self) -> int:
        return len(self.contas)
