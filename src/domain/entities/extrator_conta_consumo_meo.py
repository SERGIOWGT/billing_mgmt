from domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from domain.entities.extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoMEO(ExtratorContaConsumoBase):
    def get_info(self, texto: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.MEO, tipo_servico=TipoServicoEnum.INTERNET)

        conta_consumo.data_emissao = self.get_data(texto, 'Data†de†Emiss„o:','N∫†Cliente:')
        conta_consumo.valor = self.get_data(texto, 'TOTAL†DA†FATURA Ä†','IVA')
        conta_consumo.id_cliente = self.get_data(texto, 'N∫†Cliente:','N∫†Contribuinte:')
        conta_consumo.id_contribuinte = self.get_data(texto, 'N∫†Contribuinte:','N∫†Conta:')
        conta_consumo.data_vencimento = self.get_data(texto, 'Débito direto a partir do dia:', 'IBAN da sua conta bancária')
        print(conta_consumo.data_emissao + ' - ' + conta_consumo.valor + ' - ' + conta_consumo.id_cliente + ' - ' + conta_consumo.id_contribuinte + ' - ' + conta_consumo.data_vencimento)
        return conta_consumo


