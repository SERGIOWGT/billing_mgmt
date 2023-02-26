from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from src.domain.entities.extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoNOS(ExtratorContaConsumoBase):
    def get_info(self, text: str) -> ContaConsumo:
        text = unidecode(text)
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.NOS, tipo_servico=TipoServicoEnum.INTERNET)

        conta_consumo.id_contrato = 'N/A'
        conta_consumo.id_documento = self.get_data(text, 'Fatura n.o\r\n', '\r\n')
        conta_consumo.id_cliente = self.get_data(text, 'N.o cliente\r\n', '\r\n')
        conta_consumo.id_contribuinte = self.get_data(text, 'N.o contribuinte\r\n', '\r\n')

        conta_consumo.data_emissao = self.get_data(text, 'Data da fatura\r\n', num_chars=10)
        conta_consumo.valor = self.get_data(text, 'Valor desta fatura com IVA', '\r\n')
        conta_consumo.data_vencimento = self.get_data(text, 'Debito direto a partir do dia:', 'IBAN da sua conta bancaria')
        conta_consumo.periodo_referencia = self.get_data(text, 'Periodo de faturacao\r\n', '\r\n')

        # Ajusta as datas
        conta_consumo.data_emissao = self.convert_2_default_date(conta_consumo.data_emissao, 'DMY')
        conta_consumo.data_vencimento = self.convert_2_default_date(conta_consumo.data_vencimento, 'YMD', full_month=True)

        return self.adjust_data(conta_consumo)


