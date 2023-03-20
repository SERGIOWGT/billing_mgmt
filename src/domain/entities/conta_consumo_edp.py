from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, TipoServicoEnum
from .conta_consumo_base import ContaConsumoBase


class ContaConsumoEDP(ContaConsumoBase):
    def __init__(self, file_name: str):
        super().__init__(self)
        self.concessionaria = ConcessionariaEnum.EDP
        self.tipo_servico = TipoServicoEnum.INTERNET

    def create(self, text: str) -> None:
        text = unidecode(text)
        # Pedir mais samples desse pq aparentemente o preco/imposto mudou dia 10 de janeiro, no meio do periodo de faturacao entao o documento normal pode ser diferente

        self.id_documento = self._get_data(text, 'EDPC801-', '\r\n')
        self.id_contribuinte = 'N/A'  # self._get_data(text, 'Potência', '6,9 kVA (simples))
        self.id_cliente = 'N/A'  # self._get_data(text, '(Código Ponto Entrega)', 'PT')
        self.id_contrato = 'N/A'

        self.periodo_referencia = self._get_data(text, 'Periodo de faturacao:', '\r\n')
        self.data_emissao = self._get_data(text, 'Documento emitido a:', '\r\n')
        self.valor = self._get_data(text, 'a pagar?\r\n', '\r\n')
        self.data_vencimento = self._get_data(text, 'conta a partir de:\r\n', '\r\n')

        # Ajusta as datas
        self.data_emissao = self._convert_2_default_date(self.data_emissao, 'DMY', full_month=True)
        self.data_vencimento = self._convert_2_default_date(self.data_vencimento, 'DMY', full_month=True)

        self._adjust_data()
