from unidecode import unidecode
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from .conta_consumo_base import ContaConsumoBase


class ContaConsumoGalp(ContaConsumoBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.GALP
        self.tipo_servico = TipoServicoEnum.AGUA

    def create(self, text: str) -> None:
        text = unidecode(text)
        self.id_contribuinte = 'N/A'

        # OK
        self.id_documento = self._get_data(text, 'Fatura: ', '\r\n')
        self.id_cliente = self._get_data(text, 'N.o de contribuinte\r\n', '\r\n')
        self.id_contrato = self._get_data(text, 'N.o de contrato\r\n', '\r\n')
        self.nome_cliente = self._get_data(text, 'Nome do titular\r\n', '\r\n')

        self.str_valor = self._get_data(text, 'VALOR A DEBITAR:', 'EUR')
        self.periodo_referencia = self._get_data(text, 'Periodo de Faturacao:', '\r\n')
        self.str_vencimento = self._get_data(text, 'DEBITO ATE:', '\r\n')

        # WARN: data de emissao depende do id_documento
        str_emissao = f'{self.id_documento}\r\nData:'
        self.str_emissao = self._get_data(text, str_emissao, '\r\n')

        # Ajusta as datas
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

        self._adjust_data()
