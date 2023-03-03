from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoEpal(ExtratorContaConsumoBase):
    def convert_data(self, str_data: str, format: str) -> str:
        if (not str_data):
            return ''

        return str_data

    def get_info(self, text: str) -> ContaConsumo:
        text = unidecode(text)
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.EPAL, tipo_servico=TipoServicoEnum.AGUA)
        conta_consumo.id_contribuinte = 'N/A'

        # OK
        conta_consumo.id_documento = self.get_data(text, 'FATURA no FT ', ', emitida em ')
        conta_consumo.id_cliente = self.get_data(text, 'COD CLIENTE', 'CONTA CLIENTE ')
        conta_consumo.local_consumo = self.get_data(text, 'COD LOCAL', 'COD ENTIDADE ')
        conta_consumo.id_contrato = self.get_data(text, 'CONTA CLIENTE No', '\r\n')
        conta_consumo.nome_cliente = self.get_data(text, 'Titular do Contrato - ', 'NIF -')
        

        conta_consumo.valor = self.get_data(text, 'Valor a Pagar', 'EUR')
        conta_consumo.periodo_referencia = self.get_data(text, 'Periodo de Faturacao de', '\r\n')
        conta_consumo.data_vencimento = self.get_data(text, 'Debito a partir de ', num_chars=10)

        # WARN: data de emissao depende do id_documento
        str_emissao = f'{conta_consumo.id_documento}, emitida em '
        conta_consumo.data_emissao = self.get_data(text, str_emissao, num_chars=10)

        # Ajusta as datas
        conta_consumo.data_emissao = self.convert_2_default_date(conta_consumo.data_emissao, 'YMD')
        conta_consumo.data_vencimento = self.convert_2_default_date(conta_consumo.data_vencimento, 'YMD')

        return self.adjust_data(conta_consumo)
