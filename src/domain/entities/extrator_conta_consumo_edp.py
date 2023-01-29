from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoEDP(ExtratorContaConsumoBase):
    def get_info(self, texto: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.EDP, tipo_servico=TipoServicoEnum.LUZ)
        #Pedir mais samples desse pq aparentemente o preco/imposto mudou dia 10 de janeiro, no meio do periodo de faturacao entao o documento normal pode ser diferente

        conta_consumo.id_cliente = self.get_data(texto, '(Código Ponto Entrega)', 'PT')
        conta_consumo.id_contribuinte = self.get_data(texto, 'Potência', '6,9 kVA (simples)')
        conta_consumo.nome_contribuinte = self.get_data(texto, 'Nome do titular IBAN\r\n', 'PT')

        conta_consumo.mes_referencia = self.get_data(texto, 'Período de faturação:', 'r\n').strip()
        conta_consumo.data_emissao = self.get_data(texto, 'Documento emitido a:','Período de faturação').strip()
        conta_consumo.valor = self.get_data(texto, 'a pagar?','Débito na minha')
        conta_consumo.data_vencimento = self.get_data(texto, 'Documento emitido a:', 'Período de faturação:')
        

        
        return conta_consumo


