import re
from unidecode import unidecode
from src.domain.enums import ServiceProviderEnum, ServiceTypeEnum, DocumentTypeEnum
from .base.base_utility_bill import UtilityBillBase


class UtilityBillGalp(UtilityBillBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ServiceProviderEnum.GALP
        self.tipo_servico = ServiceTypeEnum.AGUA

    def _adjust_periodo_faturacao(self):
        ret = ''
        if (self.periodo_referencia):
            ret = self.periodo_referencia.strip()
            ret = ret.replace(' a ', '~')
            ret = ret.replace(' de ', '.')
            ret = ret.replace(' ', '.')
            vet = ret.split('~')
            if (len(vet) == 2):
                vet[0] = self._convert_2_default_date(vet[0], 'DMY', True)
                vet[1] = self._convert_2_default_date(vet[1], 'DMY', True)
                if vet[0] != '' and vet[1] != '':
                    ret = f'{vet[0]} ~ {vet[1]}'

        self.periodo_referencia = ret

    def _get_local_consumo(self, text) -> None:
        self.local_consumo = ''

    def _get_id_contribuinte(self, text) -> None:
        self.id_contribuinte = ''

    def _get_id_cliente(self, text) -> None:
        self.id_cliente = self._get_data(text, 'N.o de contribuinte\r\n', '\r\n')

    def _get_id_contrato(self, text) -> None:
        self.id_contrato = self._get_data(text, 'N.o de contrato\r\n', '\r\n')

    def _get_periodo_faturacao(self, text):
        def get(text, str_search):
            resp = ''
            str1 = 'Periodo de Faturacao: '
            str_search = str1 + str_search
            x = re.search(str_search, text)
            if x:
                pos_ini = x.regs[0][0] + len(str1)
                pos_fim = x.regs[0][1]
                resp = text[pos_ini:pos_fim]
                return resp.replace('\r\n', '')
            return ''

        regex = r'\d{{2}} ({}) \d{{4}} a \d{{2}} ({}) \d{{4}}\r\n'.format(self.regex_months_reduced.upper(), self.regex_months_reduced.upper())
        self.periodo_referencia = get(text, regex)
        if (self.periodo_referencia.strip() == ''):
            regex = '\d{{2}} ({}) \d{{4}} a \d{{2}} ({}) \r\n\d{{4}}\r\n'.format(self.regex_months_reduced.upper(), self.regex_months_reduced.upper())
            self.periodo_referencia = get(text, regex)

        self._adjust_periodo_faturacao()

    def _get_id_documento(self, text: str) -> None:
        def __get(str_padrao, regex, text):
            x = re.search(regex, text)
            if x:
                pos_ini = x.regs[0][0] + len(str_padrao)
                pos_fim = x.regs[0][1]
                return text[pos_ini:pos_fim]
            return ''

        str_padrao = 'Nota de Credito: '
        regex = f'{str_padrao}NC \d+/\d+'
        self.id_documento = __get(str_padrao, regex, text)
        if (self.id_documento):
            self.tipo_documento = DocumentTypeEnum.NOTA_CREDITO
            self.id_documento = self.id_documento.strip()
            return

        str_padrao = 'Fatura: '
        regex = f'{str_padrao}FT \d+/\d+'
        self.id_documento = __get(str_padrao, regex, text)
        if (self.id_documento):
            self.tipo_documento = DocumentTypeEnum.CONTA_CONSUMO
            self.id_documento = self.id_documento.strip()
            return

    def _get_data_vencimento(self, text) -> None:
        if (self.tipo_documento == DocumentTypeEnum.NOTA_CREDITO):
            self.str_vencimento = ''
        else:
            self.str_vencimento = self._get_data(text, 'DEBITO ATE:', '\r\n')
            self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

    def _get_valor(self, text) -> None:
        if (self.tipo_documento == DocumentTypeEnum.NOTA_CREDITO):
            self.str_valor = self._get_data(text, 'Tem a receber\r\n', 'EUR')
        else:
            self.str_valor = self._get_data(text, 'VALOR A DEBITAR:', 'EUR')

    def _get_data_emissao(self, text) -> None:
        str_emissao = f'{self.id_documento}\r\nData:'
        self.str_emissao = self._get_data(text, str_emissao, '\r\n')
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)

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
