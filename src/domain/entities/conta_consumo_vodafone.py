from unidecode import unidecode
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from .conta_consumo_base import ContaConsumoBase


class ContaConsumoVodafone(ContaConsumoBase):
    def __init__(self):
        super().__init__()
        self.concessionaria = ConcessionariaEnum.VODAFONE
        self.tipo_servico = TipoServicoEnum.INTERNET

    def create(self, text: str) -> None:
        text = unidecode(text)

        # OK
        self.id_cliente = ''

        informacoes_cliente = self._get_data(text, 'No Documento No Contribuinte No de Conta', 'Apoio a').split()
        if (len(informacoes_cliente) == 4):
            self.id_documento = informacoes_cliente[1]
            self.id_contrato = informacoes_cliente[3]
            self.id_contribuinte = informacoes_cliente[2]
        else:
            self.id_documento = 'N/A'
            self.id_contrato = 'N/A'
            self.id_contribuinte = 'N/A'

        self.str_emissao = self._get_data(text, 'Data de emissao: ', num_chars=10)
        valor = self._get_data(text, 'Total da fatura com IVA', 'Resumo do IVA').split('EUR')
        self.str_valor = valor[-1]
        self.periodo_referencia = self._get_data(text, 'Periodo de faturacao:', '\r\n')

        # WARN:
        self.str_vencimento = self._get_data(text, 'Data limite de pagamento:', 'Valor deste mes').strip()
        if not self.str_vencimento:
            self.str_vencimento = self._get_data(text, 'Debito a partir de', 'Valor deste mes').strip()

        # Ajusta as datas
        self.str_emissao = self._convert_2_default_date(self.str_emissao, 'DMY')
        self.str_vencimento = self._convert_2_default_date(self.str_vencimento, 'DMY', full_month=True)

        self._adjust_data()
