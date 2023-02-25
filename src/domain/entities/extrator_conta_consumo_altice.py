from unidecode import unidecode
from .extrator_conta_base import ExtratorContaConsumoBase
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum

class ExtratorContaConsumoAltice(ExtratorContaConsumoBase):
    def get_info(self, text: str) -> ContaConsumo:
        text = unidecode(text)
        text = text.replace('|', ' ')
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.ALTICE, tipo_servico=TipoServicoEnum.INTERNET)

        conta_consumo.id_documento = self.get_data(text, 'No Referencia:', '\r\n')
        conta_consumo.id_contribuinte = self.get_data(text, 'No Contribuinte:', '\r\n')
        conta_consumo.id_cliente = self.get_data(text, 'No Cliente:', '\r\n')
        conta_consumo.id_contrato = self.get_data(text, 'No Conta:', '\r\n')
        conta_consumo.periodo_referencia = 'N/A'
        conta_consumo.data_emissao = self.get_data(text, 'Data de Emissao:', '\r\n')
        conta_consumo.data_vencimento = self.get_data(text, 'Debito bancario a partir de:', '\r\n')
        conta_consumo.valor = self.get_data(text, 'Valor a Pagar', '\r\n')

        return self.adjust_data(conta_consumo)


