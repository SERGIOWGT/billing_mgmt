from dataclasses import dataclass
from typing import Optional

from domain.entities.extrator_conta_base import ExtratorContaConsumoBase
from domain.entities.extrator_conta_consumo_nos import ExtratorContaConsumoNOS

@dataclass
class ExtratorContaConsumoFactory:
    @staticmethod
    def execute(texto :str)-> Optional[ExtratorContaConsumoBase]:
        if (texto.index('Esta é a sua fatura NOS') > 0):
            return ExtratorContaConsumoNOS()

        if (texto.index('Esta é a sua fatura NOS') > 0):
            return ExtratorContaConsumoNOS()

        return None
