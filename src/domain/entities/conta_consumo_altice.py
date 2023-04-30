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

    def _get_local_consumo(self, text) -> None:
        self.local_consumo = ''

    def _get_id_contribuinte(self, text) -> None:
        self.id_contribuinte = self._get_data(text, 'No Contribuinte:', '\r\n')

    def _get_id_cliente(self, text) -> None:
        self.id_cliente = self._get_data(text, 'No Cliente:', '\r\n')

    def _get_id_contrato(self, text) -> None:
        self.id_contrato = self._get_data(text, 'No Conta:', '\r\n')

    def _get_periodo_faturacao(self, text) -> None:
        regex = 'Fatura\r\n({}) [0-9]{{4}}'.format(self.regex_months)
        x = re.search(regex, text)
        if x:
            pos_ini = x.regs[0][0] + 8
            pos_fim = x.regs[0][1]
            self.periodo_referencia = text[pos_ini:pos_fim]
            self.periodo_referencia = self.periodo_referencia.replace(' ', '/')

    def _get_id_documento(self, text: str) -> None:
        self.id_documento = self._get_data(text, 'No Referencia:', '\r\n')

    def _get_data_vencimento(self, text) -> None:
        self.str_vencimento = self._get_data(text, 'Debito bancario a partir de:', '\r\n')
        if (self.str_vencimento == ''):
            regex = 'Fatura\r\n({}) [0-9]{{4}} [0-9]{{1,2}} ({}) [0-9]{{4}}'.format(self.regex_months, self.regex_months)
            x = re.search(regex, text)
            if x:
                pos_ini = x.regs[0][0]
                pos_fim = x.regs[0][1]
                str_aux = text[pos_ini:pos_fim]
                vet = str_aux.split(' ')
                if (len(vet) == 5):
                    self.str_vencimento = f'{vet[2]} {vet[3]} {vet[4]}'

        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

    def _get_valor(self, text) -> None:
        self.str_valor = self._get_data(text, 'Valor a Pagar', '\r\n')

    def _get_data_emissao(self, text) -> None:
        self.str_emissao = self._get_data(text, 'Data de Emissao:', '\r\n')
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)

    def create(self, text: str) -> None:
        text = unidecode(text)
        text = text.replace('|', ' ')

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

        if (self.str_vencimento == ''):
            if (self.valor == 0) and (self.str_emissao != ''):
                self.tipo_documento = TipoDocumentoEnum.FATURA_ZERADA
                self.str_erro = 'Fatura Zerada'
