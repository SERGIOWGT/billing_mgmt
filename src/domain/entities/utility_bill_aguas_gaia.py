import re
from unidecode import unidecode

from src.domain.enums import (ServiceProviderEnum, DocumentTypeEnum,
                              ServiceTypeEnum)

from .base.base_utility_bill import UtilityBillBase


class UtilityBillAguasDeGaia(UtilityBillBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ServiceProviderEnum.AGUAS_DE_GAIA
        self.tipo_servico = ServiceTypeEnum.AGUA

    def _get_local_consumo(self, text) -> None:
        self.local_consumo = ''

    def _get_instalacao(self, text) -> None:
        self.instalacao = self._get_data(text, 'Local Consumo:', '\r\n')

    def _get_id_contribuinte(self, text) -> None:
        self.id_contribuinte = self._get_data(text, 'NIF:', '\r\n')

    def _get_id_cliente(self, text) -> None:
        cliente_conta = self._get_data(text, 'Cliente / Conta:', '\r\n')
        vet = cliente_conta.strip().split('/')
        if (len(vet) != 2):
            return False

        self.id_cliente = vet[0]

    def _get_id_contrato(self, text) -> None:
        cliente_conta = self._get_data(text, 'Cliente / Conta:', '\r\n')
        vet = cliente_conta.strip().split('/')
        if (len(vet) != 2):
            return False

        self.id_contrato = cliente_conta

    def _get_periodo_faturacao(self, text):
        self.periodo_referencia = self._get_data(text, 'Periodo Faturacao:', '\r\n')

    def _get_id_documento(self, text: str) -> None:
        if self.tipo_documento == DocumentTypeEnum.NOTA_CREDITO:
            self.id_documento = self._get_data(text, 'Nota de Credito: ', 'Data Fatura')
            if not self.id_documento:
                self.id_documento = self._get_data(text, 'Titular da conta:\r\n', '\r\n')
        else:
            self.id_documento = self._get_data(text, 'Titular da conta:\r\n', '\r\n')
                
    def _get_data_vencimento(self, text) -> bool:
        self.str_vencimento = self._get_data(text, 'Debito a partir de\r\n', '\r\n')
        if (self.str_vencimento == ''):
            self.str_vencimento = self._get_data(text, 'Data limite pagamento\r\n', '\r\n')
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

    def _get_valor(self, text) -> None:
        if self.tipo_documento == DocumentTypeEnum.NOTA_CREDITO:
            #self.str_valor = self._get_data(text, 'Valor a Receber\r\n', '\r\n')
            regex = '[^0-9]*(-?\d+[.,]?\d*)EUR\r\nValor a Receber\r\n'
            x = re.search(regex, text)
            if x and len(x.regs) >= 2:
                pos_ini = x.regs[1][0]
                pos_fim = x.regs[1][1]
                self.str_valor = text[pos_ini:pos_fim]
        else:
            #vet = self._get_data(text, 'Saldo Atual', '\r\n')
            #vet = vet.strip()
            #vet = vet.split(' ')
            #if (len(vet) == 2):
                #self.str_valor = vet[1]
            regex = '[^0-9]*(-?\d+[.,]?\d*)EUR\r\nValor a Pagar\r\n'
            x = re.search(regex, text)
            if x and len(x.regs) >= 2:
                pos_ini = x.regs[1][0]
                pos_fim = x.regs[1][1]
                self.str_valor = text[pos_ini:pos_fim]

    def _get_data_emissao(self, text) -> None:
        self.str_emissao = self._get_data(text, 'Data de Emissao\r\n', '\r\n')
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)

    def create(self, text: str) -> None:
        text = unidecode(text)

        pos_nc = text.find('Nota de Credito\r\nDocumento:')
        #pos_vpag = text.find('r\nValor a Pagar\r\n')
        if pos_nc > 0:
            self.tipo_documento = DocumentTypeEnum.NOTA_CREDITO
        else:
            pos_vrec = text.find('\r\nValor a Receber\r\n')
            if pos_vrec > 0:
                self.tipo_documento = DocumentTypeEnum.NOTA_CREDITO

        self._get_periodo_faturacao(text)
        self._get_local_consumo(text)
        self._get_instalacao(text)
        self._get_id_cliente(text)
        self._get_id_contrato(text)
        self._get_id_documento(text)
        self._get_data_emissao(text)
        self._get_data_vencimento(text)
        self._get_valor(text)
        self._check_account_of_qqd(text.upper())

        #if (self.str_vencimento == '') and (self.valor is None) and self.id_documento == '':
        #    self.id_documento = self._get_data(text, 'Nota de Credito: ', 'Data Fatura')
        #    if (self.id_documento) and (self.str_valor):
        #        self.tipo_documento = DocumentTypeEnum.NOTA_CREDITO

        self._adjust_data()
        #if (self.tipo_documento != DocumentTypeEnum.NOTA_CREDITO):
        #    start_pos = text.find(f'-{self.str_valor}')
        #    if (start_pos > 0):
        #        if (self.id_documento) and (self.str_valor):
        #            self.tipo_documento = DocumentTypeEnum.NOTA_CREDITO
        #            self.valor = self.valor * (-1)
