from dataclasses import dataclass
from typing import Optional

from src.domain.entities import *

@dataclass
class ExtratorContaConsumoFactory:
    @staticmethod
    def execute(texto :str)-> Optional[ExtratorContaConsumoBase]:
        if (texto.find('Esta é a sua fatura NOS') > 0):
           return ExtratorContaConsumoNOS()
        elif (texto.find('EDP Comercial') > 0):
            return ExtratorContaConsumoEDP()
        elif (texto.find('My Vodafone') > 0):
            return ExtratorContaConsumoVodafone()
        elif (texto.find('altice-empresas.pt') > 0):
            return ExtratorContaConsumoAltice()
        elif (texto.find('www.aguasgaia.pt') > 0):
            return ExtratorContaConsumoAguasDeGaia()
        elif (texto.find('meo.pt') > 0):
            return ExtratorContaConsumoMEO()

        return None
