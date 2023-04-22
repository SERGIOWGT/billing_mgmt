from unidecode import unidecode
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from .base.conta_consumo_base import ContaConsumoBase


class ContaConsumoGalp(ContaConsumoBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.GALP
        self.tipo_servico = TipoServicoEnum.AGUA

    def _conv_periodo_faturacao(self, value: str):
        ret = ''
        if (value):
            ret = value.strip()
            ret = ret.replace(' a ', '~')
            ret = ret.replace(' de ', '.')
            ret = ret.replace(' ', '.')
            vet = ret.split('~')
            if (len(vet) == 2):
                vet[0] = self._convert_2_default_date(vet[0], 'DMY', True)
                vet[1] = self._convert_2_default_date(vet[1], 'DMY', True)
                if vet[0] != '' and vet[1] != '' :
                    ret = f'{vet[0]} ~ {vet[1]}'

        return ret

    def _set_unavaible_data(self) -> None:
        self.local_consumo = ''
        self.id_contribuinte = ''

    def _search_id_data(self, text) -> bool:
        self.id_cliente = self._get_data(text, 'N.o de contribuinte\r\n', '\r\n')
        self.id_contrato = self._get_data(text, 'N.o de contrato\r\n', '\r\n')

    def create(self, text: str) -> None:
        text = unidecode(text)

        self._set_unavaible_data()
        self._search_id_data(text)

        self.id_documento = self._get_data(text, 'Fatura: ', '\r\n')
        self.str_valor = self._get_data(text, 'VALOR A DEBITAR:', 'EUR')
        self.str_vencimento = self._get_data(text, 'DEBITO ATE:', '\r\n')
        self.periodo_referencia = self._conv_periodo_faturacao(self._get_data(text, 'Periodo de Faturacao:', '\r\n'))

        # WARN: data de emissao depende do id_documento
        str_emissao = f'{self.id_documento}\r\nData:'
        self.str_emissao = self._get_data(text, str_emissao, '\r\n')

        # Ajusta as datas
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

        self._check_account_of_qqd(text.upper())
        self._adjust_data()
