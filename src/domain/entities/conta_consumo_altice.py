import re
from unidecode import unidecode
from src.domain.enums import (ConcessionariaEnum, TipoDocumentoEnum,
                              TipoServicoEnum)

from .base.conta_consumo_base import ContaConsumoBase

class ContaConsumoAltice(ContaConsumoBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.ALTICE_MEO
        self.tipo_servico = TipoServicoEnum.TELECOM

    def _set_unavaible_data(self) -> None:
        self.local_consumo = ''

    def _search_id_data(self, text) -> bool:
        self.id_cliente = self._get_data(text, 'No Cliente:', '\r\n')
        self.id_contrato = self._get_data(text, 'No Conta:', '\r\n')

    def _get_periodo_faturacao(self, text) -> None:
        x = re.search('Fatura\r\n\w+ [0-9]{4}', text)
        if x:
            pos_ini = x.regs[0][0] + 8
            pos_fim = x.regs[0][1]
            self.periodo_referencia = text[pos_ini:pos_fim]
            self.periodo_referencia = self.periodo_referencia.replace(' ', '/')

    def _get_data_vencimento(self, text) -> None:
        self.str_vencimento = self._get_data(text, 'Debito bancario a partir de:', '\r\n')
        if (self.str_vencimento == ''):
            self.str_vencimento = self._get_data(text, f'Fatura\r\n{self.periodo_referencia}', 'EUR')

    def create(self, text: str) -> None:
        text = unidecode(text)
        text = text.replace('|', ' ')

        self._set_unavaible_data()
        self._search_id_data(text)
        self._get_periodo_faturacao(text)
        self._get_data_vencimento(text)
        self._check_account_of_qqd(text.upper())
        
        self.id_documento = self._get_data(text, 'No Referencia:', '\r\n')
        self.str_emissao = self._get_data(text, 'Data de Emissao:', '\r\n')
        self.id_contribuinte = self._get_data(text, 'No Contribuinte:', '\r\n')
        self.str_valor = self._get_data(text, 'Valor a Pagar', '\r\n')

        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)
        self._adjust_data()
        
        if (self.str_vencimento == ''):
            if (self.valor == 0) and (self.str_emissao != ''):
                self.tipo_documento = TipoDocumentoEnum.FATURA_ZERADA
                self.str_erro = 'Fatura Zerada'



# Detalhe da Fatura No A785124244 fevereiro 2023\r\n
