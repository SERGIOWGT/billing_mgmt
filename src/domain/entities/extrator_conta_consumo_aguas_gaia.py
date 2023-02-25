from unidecode import unidecode
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoAguasDeGaia(ExtratorContaConsumoBase):
    def get_info(self, text: str) -> ContaConsumo:
        text = unidecode(text)
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.AGUAS_DE_GAIA, tipo_servico=TipoServicoEnum.AGUA)
        
        # OK
        cliente_conta = self.get_data(text, 'Cliente / Conta:', '\r\n')
        vet = cliente_conta.strip().split('/')
        if (len(vet) == 2):
            conta_consumo.id_cliente = vet[0]
            conta_consumo.id_contrato = vet[1]

        conta_consumo.id_contribuinte = self.get_data(text, 'NIF:', '\r\n')
        conta_consumo.periodo_referencia = self.get_data(text, 'Periodo Faturacao:', '\r\n')
        conta_consumo.data_vencimento = self.get_data(text, 'Debito a partir de\r\n', '\r\n')
        conta_consumo.data_emissao = self.get_data(text, 'Data de Emissao\r\n', '\r\n')
        conta_consumo.data_vencimento = self.get_data(text, 'Debito a partir de\r\n', '\r\n')
        conta_consumo.id_cliente = self.get_data(text, 'Cliente / Conta:','NIF:')
        conta_consumo.id_contribuinte = self.get_data(text, 'NIF:','Local Consumo:')
        conta_consumo.data_emissao = self.get_data(text, 'Data de Emissao', 'Debito a partir de')

        # WARN: id_documento Tem mas esta colado no campo titular da conta
        conta_consumo.id_documento = self.get_data(text, 'Titular da conta:\r\n', '\r\n')

        # WARN: valor depende da data de vencimento
        conta_consumo.valor = self.get_data(text, f'Debito a partir de\r\n{conta_consumo.data_vencimento}\r\n', '\r\n')

        return self.adjust_data(conta_consumo)
