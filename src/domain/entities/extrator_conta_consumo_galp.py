from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoGalp(ExtratorContaConsumoBase):
    def get_info(self, text: str) -> ContaConsumo:
        text = unidecode(text)
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.GALP, tipo_servico=TipoServicoEnum.AGUA)

        conta_consumo.id_contribuinte = 'N/A'

        # OK
        conta_consumo.id_documento = self.get_data(text, 'Fatura: ', '\r\n')
        conta_consumo.id_cliente = self.get_data(text, 'N.o de contribuinte\r\n', '\r\n')
        conta_consumo.id_contrato = self.get_data(text, 'N.o de contrato\r\n', '\r\n')
        conta_consumo.nome_cliente = self.get_data(text, 'Nome do titular\r\n', '\r\n')

        conta_consumo.valor = self.get_data(text, 'VALOR A DEBITAR:', 'EUR')
        conta_consumo.periodo_referencia = self.get_data(text, 'Periodo de Faturacao:', '\r\n')
        conta_consumo.data_vencimento = self.get_data(text, 'DEBITO ATE:', '\r\n')

        # WARN: data de emissao depende do id_documento
        str_emissao = f'{conta_consumo.id_documento}\r\nData:'
        conta_consumo.data_emissao = self.get_data(text, str_emissao, '\r\n')

        # Ajusta as datas
        conta_consumo.data_emissao = self.convert_2_default_date(conta_consumo.data_emissao, 'DMY', full_month=True)
        conta_consumo.data_vencimento = self.convert_2_default_date(conta_consumo.data_vencimento, 'DMY', full_month=True)

        return self.adjust_data(conta_consumo)
