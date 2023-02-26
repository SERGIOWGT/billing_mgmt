from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoMEO(ExtratorContaConsumoBase):

    def get_info(self, text: str) -> ContaConsumo:
        text = unidecode(text)

        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.MEO, tipo_servico=TipoServicoEnum.INTERNET)
        text = text.replace('†', ' ').replace('∫', 'o.')

        conta_consumo.id_documento = self.get_data(text, 'Fatura No: ', '\r\n')
        conta_consumo.id_contrato = self.get_data(text, 'No Conta: ', '\r\n')
        conta_consumo.id_cliente = self.get_data(text, 'No Cliente:', '\r\n')
        conta_consumo.id_contribuinte = self.get_data(text, 'No Contribuinte:', '\r\n')
        conta_consumo.nome_contribuinte = ''

        conta_consumo.periodo_referencia = 'N/A'
        conta_consumo.data_emissao = self.get_data(text, 'Data de Emissao:', '\r\n')
        conta_consumo.data_vencimento = self.get_data(text, 'Debito bancario a partir de:', '\r\n')
        conta_consumo.valor = self.get_data(text, 'TOTAL DA FATURA', '\r\n')

        # Ajusta as datas
        conta_consumo.data_emissao = self.convert_2_default_date(conta_consumo.data_emissao, 'DMY', full_month=True)
        conta_consumo.data_vencimento = self.convert_2_default_date(conta_consumo.data_vencimento, 'DMY', full_month=True)

        return self.adjust_data(conta_consumo)
