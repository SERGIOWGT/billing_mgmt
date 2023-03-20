from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, TipoServicoEnum
from .conta_consumo_base import ContaConsumoBase


class ContaConsumoMEO(ContaConsumoBase):
    def __init__(self, file_name: str):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.ALTICE_MEO
        self.tipo_servico = TipoServicoEnum.INTERNET

    def create(self, text: str) -> None:
        text = unidecode(text)
        text = text.replace('†', ' ').replace('∫', 'o.')

        self.id_documento = self._get_data(text, 'Fatura No: ', '\r\n')
        self.id_contrato = self._get_data(text, 'No Conta: ', '\r\n')
        self.id_cliente = self._get_data(text, 'No Cliente:', '\r\n')
        self.id_contribuinte = self._get_data(text, 'No Contribuinte:', '\r\n')
        self.nome_contribuinte = ''

        self.periodo_referencia = 'N/A'
        self.data_emissao = self._get_data(text, 'Data de Emissao:', '\r\n')
        self.data_vencimento = self._get_data(text, 'Debito bancario a partir de:', '\r\n')
        self.valor = self._get_data(text, 'TOTAL DA FATURA', '\r\n')

        # Ajusta as datas
        self.data_emissao = self._convert_2_default_date(self.data_emissao, 'DMY', full_month=True)
        self.data_vencimento = self._convert_2_default_date(self.data_vencimento, 'DMY', full_month=True)

        self._adjust_data()
