import re
from unidecode import unidecode
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from .base.conta_consumo_base import ContaConsumoBase


class ContaConsumoGalp(ContaConsumoBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.GALP
        self.tipo_servico = TipoServicoEnum.AGUA

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
                if vet[0] != '' and vet[1] != '' :
                    ret = f'{vet[0]} ~ {vet[1]}'

        self.periodo_referencia = ret

    def _set_unavaible_data(self) -> None:
        self.local_consumo = ''
        self.id_contribuinte = ''

    def _search_id_data(self, text) -> bool:
        self.id_cliente = self._get_data(text, 'N.o de contribuinte\r\n', '\r\n')
        self.id_contrato = self._get_data(text, 'N.o de contrato\r\n', '\r\n')

    def _get_periodo_faturacao(self, text, str_search):
        str1 = 'Periodo de Faturacao: '
        str_search = str1 + str_search
        x = re.search(str_search, text)
        if x:
            pos_ini = x.regs[0][0] + len(str1)
            pos_fim = x.regs[0][1]
            self.periodo_referencia = text[pos_ini:pos_fim]
            self.periodo_referencia = self.periodo_referencia.replace('\r\n', '')
        
    def create(self, text: str) -> None:
        text = unidecode(text)

        self._set_unavaible_data()
        self._search_id_data(text)
        self._check_account_of_qqd(text.upper())

        self.id_documento = self._get_data(text, 'Fatura: ', '\r\n')

        regex = '[0-9]{{2}} ({}) [0-9]{{4}} a [0-9]{{2}} ({}) [0-9]{{4}}\r\n'.format(self.regex_months_reduced.upper(), self.regex_months_reduced.upper())
        self._get_periodo_faturacao(text, regex)
        if (self.periodo_referencia.strip() == ''):
            regex = '[0-9]{{2}} ({}) [0-9]{{4}} a [0-9]{{2}} ({}) \r\n[0-9]{{4}}\r\n'.format(self.regex_months_reduced.upper(), self.regex_months_reduced.upper())
            self._get_periodo_faturacao(text, regex)

        self.str_valor = self._get_data(text, 'VALOR A DEBITAR:', 'EUR')
        self.str_vencimento = self._get_data(text, 'DEBITO ATE:', '\r\n')

        # WARN: data de emissao depende do id_documento
        str_emissao = f'{self.id_documento}\r\nData:'
        self.str_emissao = self._get_data(text, str_emissao, '\r\n')

        # Ajusta as datas
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)
        self._adjust_periodo_faturacao()
        self._adjust_data()
