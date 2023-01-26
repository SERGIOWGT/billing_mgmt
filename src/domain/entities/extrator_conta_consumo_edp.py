from domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from domain.entities.extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoEDP(ExtratorContaConsumoBase):
    def get_info(self, texto: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.EDP, tipo_servico=TipoServicoEnum.LUZ)
        #Pedir mais samples desse pq aparentemente o preco/imposto mudou dia 10 de janeiro, no meio do periodo de faturacao entao o documento normal pode ser diferente

        conta_consumo.data_emissao = self.get_data(texto, 'Documento emitido a:','Período de faturação').strip()
        conta_consumo.valor = self.get_data(texto, 'a pagar?','Débito na minha')
        conta_consumo.id_cliente = self.get_data(texto, '(Código Ponto Entrega)','PT')
        conta_consumo.id_contribuinte = self.get_data(texto, 'Potência','6,9 kVA (simples)') #Mudar 6,9 kVA (simples), nem todos os clientes podem ter a mesma potencia (pode trocar por split)
        conta_consumo.data_vencimento = self.get_data(texto, 'Documento emitido a:', 'Período de faturação:')

        print(conta_consumo.data_emissao + ' - ' + conta_consumo.valor + ' - ' + conta_consumo.id_cliente + ' - ' + conta_consumo.id_contribuinte + ' - ' + conta_consumo.data_vencimento)
        
        return conta_consumo


