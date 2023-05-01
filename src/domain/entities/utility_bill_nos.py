import re
from unidecode import unidecode

from src.domain.entities.base.base_utility_bill import UtilityBillBase
from src.domain.enums import (ServiceProviderEnum, DocumentTypeEnum,
                              ServiceTypeEnum)


class UtilityBillNOS(UtilityBillBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ServiceProviderEnum.NOS
        self.tipo_servico = ServiceTypeEnum.TELECOM

    def _get_local_consumo(self, text) -> None:
        self.local_consumo = ''

    def _get_id_contribuinte(self, text) -> None:
        self.id_contribuinte = self._get_data(text, 'N.o contribuinte\r\n', '\r\n')

    def _get_id_cliente(self, text) -> None:
        self.id_cliente = self._get_data(text, 'N.o cliente\r\n', '\r\n')

    def _get_id_contrato(self, text) -> None:
        self.id_contrato = ''

    def _get_periodo_faturacao(self, text):
        self.periodo_referencia = self._get_data(text, 'Periodo de faturacao\r\n', '\r\n')
        self.periodo_referencia = self.periodo_referencia.replace(' de ', '/')

    def _get_id_documento(self, text: str) -> None:
        self.id_documento = self._get_data(text, 'Fatura n.o\r\n', '\r\n')

    def _get_data_vencimento(self, text) -> None:
        self.str_vencimento = self._get_data(text, 'Debito direto a partir do dia:\r\n', '\r\n')
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

    def _get_valor(self, text) -> None:
        self.str_valor = self._get_data(text, 'Valor desta fatura com IVA', '\r\n')

    def _get_data_emissao(self, text) -> None:
        self.str_emissao = self._get_data(text, 'Data da fatura\r\n', num_chars=10)
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY')

    def create(self, text: str) -> None:
        text = unidecode(text)

        self._check_account_of_qqd(text.upper())
        self._get_periodo_faturacao(text)
        self._get_local_consumo(text)
        self._get_id_cliente(text)
        self._get_id_contrato(text)
        self._get_id_documento(text)
        self._get_data_emissao(text)
        self._get_data_vencimento(text)
        self._get_valor(text)
        self._check_account_of_qqd(text.upper())

        if (self.str_vencimento == '') and (self.valor is None):
            self.str_valor = self._get_data(text, 'Total a pagar', 'Detalhe desta')
            self.str_valor = re.sub(r'[^0-9,]', '', self.str_valor) if self.str_valor else ''

            if (self.str_valor == '0,00'):
                self.tipo_documento = DocumentTypeEnum.FATURA_ZERADA

        self._adjust_data()
