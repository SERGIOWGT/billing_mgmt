from dataclasses import dataclass
from typing import Optional

from src.domain.entities import UtilityBillBase, UtilityBillGalp, UtilityBillAltice, UtilityBillAguasDeGaia, UtilityBillAguasDePorto, UtilityBillEDP, UtilityBillEpal, UtilityBillNOS, UtilityBillVodafone, UtilityBillMEO


@dataclass
class UtilityBillFactory:
    @staticmethod
    def execute(texto: str) -> Optional[UtilityBillBase]:
        if (texto.find('meo.pt') > 0):
            if (texto.find('ATCUD') > 0):
                return UtilityBillMEO()

        if (texto.find('My Vodafone') > 0):
            return UtilityBillVodafone()

        if (texto.find('Esta é a sua fatura NOS') > 0):
            return UtilityBillNOS()

        if (texto.find('www.epal.pt') > 0):
            return UtilityBillEpal()

        if (texto.find('NIPC 503504564') > 0):
            return UtilityBillEDP()

        if (texto.find('EM - NIPC 507 718 666') > 0):
            return UtilityBillAguasDePorto()

        if (texto.find('www.aguasgaia.pt') > 0):
            return UtilityBillAguasDeGaia()

        if (texto.find('961 001 626') > 0):
            return UtilityBillAltice()

        if (texto.find('galp.pt') > 0) and (texto.find('ATCUD') > 0):
            return UtilityBillGalp()

        return None
