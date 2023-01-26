from dataclasses import dataclass
from typing import Optional

from domain.entities.extrator_conta_base import ExtratorContaConsumoBase
from domain.entities.extrator_conta_consumo_nos import ExtratorContaConsumoNOS
from domain.entities.extrator_conta_consumo_edp import ExtratorContaConsumoEDP
from domain.entities.extrator_conta_consumo_vodafone import ExtratorContaConsumoVodafone
from domain.entities.extrator_conta_consumo_altice import ExtratorContaConsumoAltice
from domain.entities.extrator_conta_consumo_aguas import ExtratorContaConsumoAguasDeGaia
from domain.entities.extrator_conta_consumo_meo import ExtratorContaConsumoMEO

@dataclass
class ExtratorContaConsumoFactory:
    @staticmethod
    def execute(texto :str)-> Optional[ExtratorContaConsumoBase]:
        if (texto.find('Esta é a sua fatura NOS') > 0):
           return ExtratorContaConsumoNOS()
        elif (texto.find('EDP Comercial') > 0):
            return ExtratorContaConsumoEDP()
        elif (texto.find('My Vodafone ') > 0):
            return ExtratorContaConsumoVodafone()
        elif (texto.find('altice-empresas.pt') > 0):
            return ExtratorContaConsumoAltice()
        elif (texto.find('www.aguasgaia.pt') > 0):
            return ExtratorContaConsumoAguasDeGaia()
        elif (texto.find('meo.pt') > 0):
            return ExtratorContaConsumoMEO()

        return None
