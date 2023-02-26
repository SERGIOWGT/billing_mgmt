from dataclasses import dataclass
from typing import Optional

from src.domain.entities import *

@dataclass
class ExtratorContaConsumoFactory:
    @staticmethod
    def execute(texto :str)-> Optional[ExtratorContaConsumoBase]:
        if (texto.find('Esta é a sua fatura NOS') > 0):
            return ExtratorContaConsumoNOS()

        if (texto.find('NIPC 503504564') > 0):
            return ExtratorContaConsumoEDP()

        if (texto.find('My Vodafone') > 0):
            return ExtratorContaConsumoVodafone()

        if (texto.find('961 001 626') > 0):
            return ExtratorContaConsumoAltice()

        if (texto.find('www.aguasgaia.pt') > 0):
            return ExtratorContaConsumoAguasDeGaia()

        if (texto.find('meo.pt') > 0):
            return ExtratorContaConsumoMEO()

        if (texto.find('EM - NIPC 507 718 666') > 0):
            return ExtratorContaConsumoAguasDePorto()

        if (texto.find('www.epal.pt') > 0):
            return ExtratorContaConsumoEpal()

        if (texto.find('galp.pt') > 0):
            return ExtratorContaConsumoGalp()

        return None
