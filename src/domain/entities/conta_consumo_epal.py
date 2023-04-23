from unidecode import unidecode
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from .base.conta_consumo_base import ContaConsumoBase


class ContaConsumoEpal(ContaConsumoBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.EPAL
        self.tipo_servico = TipoServicoEnum.AGUA

    def _convert_data(self, str_data: str, format: str) -> str:
        if (not str_data):
            return ''

        return str_data

    def _set_unavaible_data(self) -> None:
        self.id_contribuinte = ''

    def _search_id_data(self, text) -> bool:
        self.id_cliente = self._get_data(text, 'COD CLIENTE', 'CONTA CLIENTE ')
        self.local_consumo = self._get_data(text, 'COD LOCAL', 'COD ENTIDADE ')
        self.id_contrato = self._get_data(text, 'CONTA CLIENTE No', '\r\n')

    def create(self, text: str) -> None:
        text = unidecode(text)

        self._set_unavaible_data()
        self._search_id_data(text)
        self._check_account_of_qqd(text.upper())

        self.id_documento = self._get_data(text, 'FATURA no FT ', ', emitida em ')
        self.periodo_referencia = self._get_data(text, 'Periodo de Faturacao de', '\r\n')
        self.periodo_referencia = self.periodo_referencia.replace(' a ', '~')
        self.periodo_referencia = self.periodo_referencia.replace('.', '-')

        self.str_valor = self._get_data(text, 'Valor a Pagar', 'EUR')
        self.str_vencimento = self._get_data(text, 'Debito a partir de ', num_chars=10)

        # WARN: data de emissao depende do id_documento
        str_emissao = f'{self.id_documento}, emitida em '
        self.str_emissao = self._get_data(text, str_emissao, num_chars=10)

        # Ajusta as datas
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'YMD')
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'YMD')
        self._adjust_data()
