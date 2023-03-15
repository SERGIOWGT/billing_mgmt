from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .conta_consumo_base import ContaConsumoBase


class ContaConsumoEpal(ContaConsumoBase):
    def __init__(self, file_name: str):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.EPAL
        self.tipo_servico = TipoServicoEnum.AGUA

    def _convert_data(self, str_data: str, format: str) -> str:
        if (not str_data):
            return ''

        return str_data

    def create(self, text: str) -> None:
        text = unidecode(text)
        self.id_contribuinte = 'N/A'

        # OK
        self.id_documento = self._get_data(text, 'FATURA no FT ', ', emitida em ')
        self.id_cliente = self._get_data(text, 'COD CLIENTE', 'CONTA CLIENTE ')
        self.local_consumo = self._get_data(text, 'COD LOCAL', 'COD ENTIDADE ')
        self.id_contrato = self._get_data(text, 'CONTA CLIENTE No', '\r\n')
        self.nome_cliente = self._get_data(text, 'Titular do Contrato - ', 'NIF -')

        self.valor = self._get_data(text, 'Valor a Pagar', 'EUR')
        self.periodo_referencia = self._get_data(text, 'Periodo de Faturacao de', '\r\n')
        self.data_vencimento = self._get_data(text, 'Debito a partir de ', num_chars=10)

        # WARN: data de emissao depende do id_documento
        str_emissao = f'{self.id_documento}, emitida em '
        self.data_emissao = self._get_data(text, str_emissao, num_chars=10)

        # Ajusta as datas
        self.data_emissao = self._convert_2_default_date(self.data_emissao, 'YMD')
        self.data_vencimento = self._convert_2_default_date(self.data_vencimento, 'YMD')

        self._adjust_data()
