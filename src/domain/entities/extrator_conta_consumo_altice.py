from domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from domain.entities.extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoAltice(ExtratorContaConsumoBase):
    def get_info(self, texto: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.ALTICE, tipo_servico=TipoServicoEnum.INTERNET)

        conta_consumo.data_emissao = self.get_data(texto, 'Data de Emissão:','Nº Cliente:').strip()
        conta_consumo.valor = self.get_data(texto, 'TOTAL DA FATURA','Informação Adicional').strip()
        conta_consumo.id_cliente = self.get_data(texto, 'Nº Cliente:','Nº Contribuinte:').strip()
        conta_consumo.id_contribuinte = self.get_data(texto, 'Nº Contribuinte: ','Nº Conta: ').strip()
        conta_consumo.data_vencimento = self.get_data(texto, 'Débito direto a partir do dia:', 'IBAN da sua conta bancária').strip()

        print(conta_consumo.data_emissao + ' - ' + conta_consumo.valor + ' - ' + conta_consumo.id_cliente + ' - ' + conta_consumo.id_contribuinte + ' - ' + conta_consumo.data_vencimento)

        return conta_consumo


