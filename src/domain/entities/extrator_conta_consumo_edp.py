from datetime import datetime
from src.domain.models.conta_consumo import ConcessionariaEnum, ContaConsumo, TipoServicoEnum
from .extrator_conta_base import ExtratorContaConsumoBase

class ExtratorContaConsumoEDP(ExtratorContaConsumoBase):
    def convert_date(self, str_date: str) -> str:
        if (not str_date):
            return ''

        str_date = str_date.strip()
        str_date = str_date.replace(' de ', ' ')

        _vet = str_date.split()
        if (len(_vet) != 3):
            return ''

        _mes_extenso = _vet[1]
        _mes = self.mes_extenso.get(_mes_extenso.lower(), '')
        _str_date = f'{_vet[0]}/{_mes}/{_vet[2]}'
        try:
            _date = datetime.strptime(_str_date, '%d/%m/%Y')
        except ValueError:
            return ''

        return _str_date

    def get_info(self, text: str) -> ContaConsumo:
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.EDP, tipo_servico=TipoServicoEnum.LUZ)
        #Pedir mais samples desse pq aparentemente o preco/imposto mudou dia 10 de janeiro, no meio do periodo de faturacao entao o documento normal pode ser diferente

        conta_consumo.id_cliente = self.get_data(text, '(Código Ponto Entrega)', 'PT')
        conta_consumo.id_contribuinte = self.get_data(text, 'Potência', '6,9 kVA (simples)')
        conta_consumo.nome_contribuinte = '' #self.get_data(text, 'Nome do titular IBAN\r\n', 'PT')
        conta_consumo.mes_referencia = self.get_data(text, 'Período de faturação:', 'r\n').strip()
        conta_consumo.data_emissao = self.get_data(text, 'Documento emitido a:','Período de faturação').strip()
        conta_consumo.valor = self.get_data(text, 'a pagar?','Débito na minha')
        conta_consumo.data_vencimento = self.get_data(text, 'Documento emitido a:', 'Período de faturação:')

        return self.adjust_data(conta_consumo)
