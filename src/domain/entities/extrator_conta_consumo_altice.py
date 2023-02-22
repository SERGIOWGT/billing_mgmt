from .extrator_conta_consumo_meo import ExtratorContaConsumoMEO
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum


class ExtratorContaConsumoAltice(ExtratorContaConsumoMEO):
    def get_info(self, text: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.ALTICE, tipo_servico=TipoServicoEnum.INTERNET)

        conta_consumo.id_cliente = self.get_data(text, 'Nº Cliente:', '\r\n')
        conta_consumo.id_cliente = self.clear_data(conta_consumo.id_cliente)
        conta_consumo.id_contribuinte = self.get_data(text, 'Nº Contribuinte:', '\r\n')
        conta_consumo.id_contribuinte = self.clear_data(conta_consumo.id_contribuinte)
        conta_consumo.nome_contribuinte = ''

        conta_consumo.periodo_referencia = ''
        conta_consumo.data_emissao = self.get_data(text, 'Data de Emissão:', '\r\n')
        conta_consumo.data_emissao = self.convert_date(conta_consumo.data_emissao)
        conta_consumo.data_vencimento = self.get_data(text, 'Débito bancário a partir de:', '\r\n')
        conta_consumo.data_vencimento = self.convert_date(conta_consumo.data_vencimento)
        conta_consumo.valor = self.get_data(text, 'TOTAL DA FATURA', '\r\n')
        conta_consumo.valor = self.clear_data(conta_consumo.valor)

        return conta_consumo


