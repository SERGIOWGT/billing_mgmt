from unidecode import unidecode
from src.domain.enums import ServiceProviderEnum, ServiceTypeEnum, DocumentTypeEnum
from .base.base_utility_bill import UtilityBillBase


class UtilityBillEpal(UtilityBillBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ServiceProviderEnum.EPAL
        self.tipo_servico = ServiceTypeEnum.AGUA

    def _convert_data(self, str_data: str, format: str) -> str:
        if (not str_data):
            return ''

        return str_data

    def _get_local_consumo(self, text) -> None:
        self.local_consumo = self._get_data(text, 'COD LOCAL', 'COD ENTIDADE ')

    def _get_id_contribuinte(self, text) -> None:
        self.id_contribuinte = ''

    def _get_id_cliente(self, text) -> None:
        self.id_cliente = self._get_data(text, 'COD CLIENTE', 'CONTA CLIENTE ')

    def _get_id_contrato(self, text) -> None:
        self.id_contrato = self._get_data(text, 'CONTA CLIENTE No', '\r\n')

    def _get_periodo_faturacao(self, text):
        self.periodo_referencia = self._get_data(text, 'Periodo de Faturacao de', '\r\n')
        self.periodo_referencia = self.periodo_referencia.replace(' a ', '~')
        self.periodo_referencia = self.periodo_referencia.replace('.', '-')

    def _get_id_documento(self, text: str) -> None:
        self.id_documento = self._get_data(text, 'FATURA no FT ', ', emitida em ')

    def _get_data_vencimento(self, text) -> None:
        self.str_vencimento = self._get_data(text, 'Debito a partir de ', num_chars=10)
        if (self.str_vencimento == ''):
            self.str_vencimento = self._get_data(text, 'Credito a partir de ', num_chars=10)
            if (self.str_vencimento):
                self.tipo_documento = DocumentTypeEnum.NOTA_CREDITO
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'YMD')

    def _get_valor(self, text) -> None:
        self.str_valor = self._get_data(text, 'Valor a Pagar', 'EUR')
        if self.str_valor == '':
            self.str_valor = self._get_data(text, 'Valor a Receber', 'EUR')
            if (self.str_valor):
                self.tipo_documento = DocumentTypeEnum.NOTA_CREDITO

    def _get_data_emissao(self, text) -> None:
        # WARN: data de emissao depende do id_documento
        str_emissao = f'{self.id_documento}, emitida em '
        self.str_emissao = self._get_data(text, str_emissao, num_chars=10)
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'YMD')

    def create(self, text: str) -> None:
        text = unidecode(text)
        self._get_periodo_faturacao(text)
        self._get_local_consumo(text)
        self._get_id_cliente(text)
        self._get_id_contrato(text)
        self._get_id_documento(text)
        self._get_data_emissao(text)
        self._get_data_vencimento(text)
        self._get_valor(text)
        self._check_account_of_qqd(text.upper())
        self._adjust_data()
