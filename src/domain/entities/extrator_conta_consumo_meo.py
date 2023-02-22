from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoMEO(ExtratorContaConsumoBase):

    def get_info(self, text: str) -> ContaConsumo:
        #text = unidecode(text)

        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.MEO, tipo_servico=TipoServicoEnum.INTERNET)
        text = text.replace('†', ' ').replace('∫', 'o.')

        conta_consumo.id_cliente = self.get_data(text, 'No. Cliente:', '\r\n')
        conta_consumo.id_contribuinte = self.get_data(text, 'No. Contribuinte:', '\r\n')
        conta_consumo.nome_contribuinte = ''

        conta_consumo.periodo_referencia = ''
        conta_consumo.data_emissao = self.get_data(text, 'Data de Emiss„o:', '\r\n')
        conta_consumo.data_vencimento = self.get_data(text, 'DÈbito banc·rio a partir de:', '\r\n')
        conta_consumo.valor = self.get_data(text, 'TOTAL DA FATURA Ä', '\r\n')
        
        return self.adjust_date(conta_consumo)
