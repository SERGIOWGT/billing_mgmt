from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_consumo_aguas_gaia import ExtratorContaConsumoAguasDeGaia

class ExtratorContaConsumoAguasDePorto(ExtratorContaConsumoAguasDeGaia):
    def get_info(self, text: str) -> ContaConsumo:
        conta_consumo = super().get_info(text)
        conta_consumo.tipo_servico = TipoServicoEnum.AGUA
        conta_consumo.concessionaria = ConcessionariaEnum.AGUAS_DE_PORTO

        vet = conta_consumo.id_contrato.split('/')
        if (len(vet) == 2):
            conta_consumo.id_contrato = vet[1]

        return self.adjust_data(conta_consumo)
