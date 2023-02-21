from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoVodafone(ExtratorContaConsumoBase):
    def get_info(self, texto: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.VODAFONE, tipo_servico=TipoServicoEnum.INTERNET)
        conta_consumo.data_emissao = self.get_data(texto, 'Data de emissao:','Periodo de faturacao:').strip()
        
        valor = self.get_data(texto, 'Total da fatura com IVA','Resumo do IVA').split('EUR')
        conta_consumo.valor = valor[-1]
        
        informacoes_cliente = self.get_data(texto, 'No Documento No Contribuinte No de Conta','Apoio a').split()
        conta_consumo.id_cliente = informacoes_cliente[3]
        conta_consumo.id_contribuinte = informacoes_cliente[2]
       
        conta_consumo.data_vencimento = self.get_data(texto, 'Data limite de pagamento:','Valor deste mes').strip()

        print(conta_consumo.data_emissao + ' - ' + conta_consumo.valor + ' - ' + conta_consumo.id_cliente + ' - ' + conta_consumo.id_contribuinte + ' - ' + conta_consumo.data_vencimento)

        return conta_consumo


