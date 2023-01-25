from domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from domain.entities.extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoNOS(ExtratorContaConsumoBase):
    def get_info(self, texto: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.NOS, tipo_servico=TipoServicoEnum.INTERNET)

        conta_consumo.data_emissao = self.get_data(texto, 'Data da fatura','Período de faturação')
        conta_consumo.valor = self.get_data(texto, 'Valor desta fatura com IVA','Total a pagar até')
        conta_consumo.id_cliente = self.get_data(texto, 'N.º cliente','N.º contribuinte')
        conta_consumo.id_contribuinte = self.get_data(texto, 'N.º contribuinte','Página')
        conta_consumo.data_vencimento = self.get_data(texto, 'Débito direto a partir do dia:', 'IBAN da sua conta bancária')

        return conta_consumo


