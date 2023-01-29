from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoAguasDeGaia(ExtratorContaConsumoBase):
    def get_info(self, texto: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.AGUAS_DE_GAIA, tipo_servico=TipoServicoEnum.AGUA)

        data_emissao = self.get_data(texto, 'Emissão:','Cliente / Conta:').split()
        conta_consumo.data_emissao = data_emissao[0].strip()[0:10]

        valor = self.get_data(texto, 'Telefone: Referência Leitura: Dígitos a comunicar:','Valor a Pagar')
        conta_consumo.valor = valor[18:]
        
        conta_consumo.id_cliente = self.get_data(texto, 'Cliente / Conta:','NIF:')
        conta_consumo.id_contribuinte = self.get_data(texto, 'NIF:','Local Consumo:')
        conta_consumo.data_vencimento = self.get_data(texto, 'Débito direto a partir do dia:', 'IBAN da sua conta bancária')
        
        print(conta_consumo.data_emissao + ' - ' + conta_consumo.valor + ' - ' + conta_consumo.id_cliente + ' - ' + conta_consumo.id_contribuinte + ' - ' + conta_consumo.data_vencimento)
        
        return conta_consumo


