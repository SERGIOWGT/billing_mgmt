from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoAguasDeGaia(ExtratorContaConsumoBase):
    def get_info(self, text: str) -> ContaConsumo:
        text = unidecode(text)
        conta_consumo = ContaConsumo(
            concessionaria=ConcessionariaEnum.AGUAS_DE_GAIA, tipo_servico=TipoServicoEnum.AGUA)
        conta_consumo.data_vencimento = self.get_data(
            text, 'Debito a partir de\r\n', '\r\n')


        valor = self.get_data(text, 'Telefone: Referencia Leitura: Digitos a comunicar:','Valor a Pagar')
        conta_consumo.valor = valor[18:]

        conta_consumo.id_cliente = self.get_data(text, 'Cliente / Conta:','NIF:')
        conta_consumo.id_contribuinte = self.get_data(text, 'NIF:','Local Consumo:')
        
        conta_consumo.data_emissao = self.get_data(text, 'Data de Emissao', 'Debito a partir de')

        return self.adjust_data(conta_consumo)


