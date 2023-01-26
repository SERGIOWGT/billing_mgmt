from domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from domain.entities.extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoEDP(ExtratorContaConsumoBase):
    def get_info(self, texto: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.EDP, tipo_servico=TipoServicoEnum.LUZ)

        conta_consumo.data_emissao = self.get_data(texto, 'Documento emitido a:','Período de faturação')
        conta_consumo.valor = self.get_data(texto, 'a pagar?','€ Débito na minha')
        conta_consumo.id_cliente = self.get_data(texto, '(Código Ponto Entrega)','PT')
        conta_consumo.id_contribuinte = self.get_data(texto, '310489482','Código de contrato')
        conta_consumo.data_vencimento = self.get_data(texto, 'Documento emitido a:', 'Período de faturação:')

        return conta_consumo


