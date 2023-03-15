from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, TipoServicoEnum
from src.domain.entities.conta_consumo_base import ContaConsumoBase


class ContaConsumoNOS(ContaConsumoBase):
    def __init__(self, file_name: str):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.NOS
        self.tipo_servico = TipoServicoEnum.INTERNET

    def create(self, text: str) -> None:
        text = unidecode(text)

        self.id_contrato = 'N/A'
        self.id_documento = self._get_data(text, 'Fatura n.o\r\n', '\r\n')
        self.id_cliente = self._get_data(text, 'N.o cliente\r\n', '\r\n')
        self.id_contribuinte = self._get_data(text, 'N.o contribuinte\r\n', '\r\n')

        self.data_emissao = self._get_data(text, 'Data da fatura\r\n', num_chars=10)
        self.valor = self._get_data(text, 'Valor desta fatura com IVA', '\r\n')
        self.data_vencimento = self._get_data(text, 'Debito direto a partir do dia:', 'IBAN da sua conta bancaria')
        self.periodo_referencia = self._get_data(text, 'Periodo de faturacao\r\n', '\r\n')

        # Ajusta as datas
        self.data_emissao = self._convert_2_default_date(self.data_emissao, 'DMY')
        self.data_vencimento = self._convert_2_default_date(self.data_vencimento, 'YMD', full_month=True)

        self._adjust_data()
