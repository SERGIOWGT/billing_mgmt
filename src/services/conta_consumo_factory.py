from dataclasses import dataclass
from typing import Optional

from src.domain.entities import *

@dataclass
class ContaConsumoFactory:
    @staticmethod
    def execute(texto: str) -> Optional[ContaConsumoBase]:
        if (texto.find('Esta é a sua fatura NOS') > 0):
            return ContaConsumoNOS()

        if (texto.find('NIPC 503504564') > 0):
            return ContaConsumoEDP()

        if (texto.find('My Vodafone') > 0):
            return ContaConsumoVodafone()

        if (texto.find('961 001 626') > 0):
            return ContaConsumoAltice()

        if (texto.find('www.aguasgaia.pt') > 0):
            return ContaConsumoAguasDeGaia()

        if (texto.find('meo.pt') > 0):
            return ContaConsumoMEO()

        if (texto.find('EM - NIPC 507 718 666') > 0):
            return ContaConsumoAguasDePorto()

        if (texto.find('www.epal.pt') > 0):
            return ContaConsumoEpal()

        if (texto.find('galp.pt') > 0):
            return ContaConsumoGalp()

        return None
