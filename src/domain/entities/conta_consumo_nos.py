from unidecode import unidecode
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from src.domain.entities.conta_consumo_base import ContaConsumoBase


class ContaConsumoNOS(ContaConsumoBase):
    def __init__(self):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.NOS
        self.tipo_servico = TipoServicoEnum.TELECOM

    def create(self, text: str) -> None:
        text = unidecode(text)

        self.id_contrato = ''
        self.id_documento = self._get_data(text, 'Fatura n.o\r\n', '\r\n')
        self.id_cliente = self._get_data(text, 'N.o cliente\r\n', '\r\n')
        self.id_contribuinte = self._get_data(text, 'N.o contribuinte\r\n', '\r\n')

        self.str_emissao = self._get_data(text, 'Data da fatura\r\n', num_chars=10)
        self.str_valor = self._get_data(text, 'Valor desta fatura com IVA', '\r\n')
        self.str_vencimento = self._get_data(text, 'Debito direto a partir do dia:\r\n', '\r\n')
        self.periodo_referencia = self._get_data(text, 'Periodo de faturacao\r\n', '\r\n')

        # Ajusta as datas
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY')
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

        self._adjust_data()
