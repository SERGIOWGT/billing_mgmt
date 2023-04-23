import re
from unidecode import unidecode

from src.domain.entities.base.conta_consumo_base import ContaConsumoBase
from src.domain.enums import (ConcessionariaEnum, TipoDocumentoEnum,
                              TipoServicoEnum)


class ContaConsumoNOS(ContaConsumoBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.NOS
        self.tipo_servico = TipoServicoEnum.TELECOM

    def _set_unavaible_data(self) -> None:
        self.local_consumo = ''
        self.id_contrato = ''

    def _search_id_data(self, text) -> bool:
        self.id_cliente = self._get_data(text, 'N.o cliente\r\n', '\r\n')

    def create(self, text: str) -> None:
        text = unidecode(text)

        self._set_unavaible_data()
        self._search_id_data(text)

        self.id_documento = self._get_data(text, 'Fatura n.o\r\n', '\r\n')
        self.id_contribuinte = self._get_data(text, 'N.o contribuinte\r\n', '\r\n')
        self.str_emissao = self._get_data(text, 'Data da fatura\r\n', num_chars=10)
        self.str_valor = self._get_data(text, 'Valor desta fatura com IVA', '\r\n')
        self.str_vencimento = self._get_data(text, 'Debito direto a partir do dia:\r\n', '\r\n')
        self.periodo_referencia = self._get_data(text, 'Periodo de faturacao\r\n', '\r\n')
        self.periodo_referencia = self.periodo_referencia.replace(' de ', '/')

        # Ajusta as datas
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY')
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

        if (self.str_vencimento == '') and (self.valor is None):
            self.str_valor = self._get_data(text, 'Total a pagar', 'Detalhe desta')
            self.str_valor = re.sub(r'[^0-9,]', '', self.str_valor) if self.str_valor else ''
            
            if (self.str_valor == '0,00'):
                self.tipo_documento = TipoDocumentoEnum.FATURA_ZERADA
                self.str_erro = 'Fatura Zerada'

        self._check_account_of_qqd(text.upper())
        self._adjust_data()
