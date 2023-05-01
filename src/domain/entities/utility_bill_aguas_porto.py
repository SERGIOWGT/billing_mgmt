from src.domain.enums import ServiceProviderEnum, ServiceTypeEnum
from .utility_bill_aguas_gaia import UtilityBillAguasDeGaia


class UtilityBillAguasDePorto(UtilityBillAguasDeGaia):
    def __init__(self):
        self.concessionaria = ServiceProviderEnum.AGUAS_DE_PORTO
        self.tipo_servico = ServiceTypeEnum.AGUA

    def create(self, text: str) -> None:
        super().create(text)
        self.tipo_servico = ServiceTypeEnum.AGUA
        self.concessionaria = ServiceProviderEnum.AGUAS_DE_PORTO

        vet = self.id_contrato.split('/')
        if (len(vet) == 2):
            self.id_contrato = vet[1]

        self._adjust_data()
