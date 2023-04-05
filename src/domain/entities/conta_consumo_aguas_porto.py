from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from .conta_consumo_aguas_gaia import ContaConsumoAguasDeGaia


class ContaConsumoAguasDePorto(ContaConsumoAguasDeGaia):
    def __init__(self):
        self.concessionaria = ConcessionariaEnum.AGUAS_DE_PORTO
        self.tipo_servico = TipoServicoEnum.AGUA

    def create(self, text: str) -> None:
        super().create(text)
        self.tipo_servico = TipoServicoEnum.AGUA
        self.concessionaria = ConcessionariaEnum.AGUAS_DE_PORTO

        vet = self.id_contrato.split('/')
        if (len(vet) == 2):
            self.id_contrato = vet[1]

        self._adjust_data()
