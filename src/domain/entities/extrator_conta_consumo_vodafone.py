from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoVodafone(ExtratorContaConsumoBase):
    def get_info(self, texto: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.VODAFONE, tipo_servico=TipoServicoEnum.INTERNET)
        conta_consumo.data_emissao = self.get_data(texto, 'Data de emissão:','Período de faturação:').strip()
        
        valor = self.get_data(texto, 'Total da fatura com IVA','Resumo do IVA').split('€')
        conta_consumo.valor = valor[3]
        
        informacoes_cliente = self.get_data(texto, 'Nº Documento Nº Contribuinte Nº de Conta','Apoio a Clientes').split()
        conta_consumo.id_cliente = informacoes_cliente[3]
        conta_consumo.id_contribuinte = informacoes_cliente[2]
       
        conta_consumo.data_vencimento = self.get_data(texto, 'Data limite de pagamento:','Valor deste mês').strip()

        print(conta_consumo.data_emissao + ' - ' + conta_consumo.valor + ' - ' + conta_consumo.id_cliente + ' - ' + conta_consumo.id_contribuinte + ' - ' + conta_consumo.data_vencimento)

        return conta_consumo


