from dataclasses import dataclass
from typing import Optional

from src.domain.entities import *

@dataclass
class ContaConsumoFactory:
    @staticmethod
    def execute(texto: str, file_name: str) -> Optional[ContaConsumoBase]:
        if (texto.find('Esta é a sua fatura NOS') > 0):
            return ContaConsumoNOS(file_name)

        if (texto.find('NIPC 503504564') > 0):
            return ContaConsumoEDP(file_name)

        if (texto.find('My Vodafone') > 0):
            return ContaConsumoVodafone(file_name)

        if (texto.find('961 001 626') > 0):
            return ContaConsumoAltice(file_name)

        if (texto.find('www.aguasgaia.pt') > 0):
            return ContaConsumoAguasDeGaia(file_name)

        if (texto.find('meo.pt') > 0):
            return ContaConsumoMEO(file_name)

        if (texto.find('EM - NIPC 507 718 666') > 0):
            return ContaConsumoAguasDePorto(file_name)

        if (texto.find('www.epal.pt') > 0):
            return ContaConsumoEpal(file_name)

        if (texto.find('galp.pt') > 0):
            return ContaConsumoGalp(file_name)

        return None
