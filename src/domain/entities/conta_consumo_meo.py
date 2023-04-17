from unidecode import unidecode
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from .conta_consumo_base import ContaConsumoBase


class ContaConsumoMEO(ContaConsumoBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.ALTICE_MEO
        self.tipo_servico = TipoServicoEnum.TELECOM

    def create(self, text: str) -> None:
        text = unidecode(text)
        text = text.replace('†', ' ').replace('∫', 'o.')

        self.id_documento = self._get_data(text, 'Fatura No: ', '\r\n')
        self.id_contrato = self._get_data(text, 'No Conta: ', '\r\n')
        self.id_cliente = self._get_data(text, 'No Cliente:', '\r\n')
        self.id_contribuinte = self._get_data(text, 'No Contribuinte:', '\r\n')

        self.periodo_referencia = 'N/A'
        self.str_emissao = self._get_data(text, 'Data de Emissao:', '\r\n')
        self.str_vencimento = self._get_data(text, 'Debito bancario a partir de:', '\r\n')
        self.str_valor = self._get_data(text, 'TOTAL DA FATURA', '\r\n')

        # Ajusta as datas
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY', full_month=True)
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

        self._adjust_data()
