from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoVodafone(ExtratorContaConsumoBase):
    def get_info(self, text: str) -> ContaConsumo:
        text = unidecode(text)

        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.VODAFONE, tipo_servico=TipoServicoEnum.INTERNET)
        conta_consumo.data_emissao = self.get_data(text, 'Data de emissao:','Periodo de faturacao:').strip()
        conta_consumo.data_emissao = conta_consumo.data_emissao.replace('-', '/')

        valor = self.get_data(text, 'Total da fatura com IVA','Resumo do IVA').split('EUR')
        conta_consumo.valor = valor[-1]

        informacoes_cliente = self.get_data(text, 'No Documento No Contribuinte No de Conta','Apoio a').split()
        if (len(informacoes_cliente) == 3):
            conta_consumo.id_cliente = informacoes_cliente[3]
            conta_consumo.id_contribuinte = informacoes_cliente[2]

        conta_consumo.data_vencimento = self.get_data(text, 'Data limite de pagamento:','Valor deste mes').strip()
        if not conta_consumo.data_vencimento:
            conta_consumo.data_vencimento = self.get_data(text, 'Debito a partir de', 'Valor deste mes').strip()
            

        return self.adjust_data(conta_consumo)


