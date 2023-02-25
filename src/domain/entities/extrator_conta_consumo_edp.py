from datetime import datetime
from unidecode import unidecode
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
        text = unidecode(text)
        conta_consumo = ContaConsumo(concessionaria=ConcessionariaEnum.EDP, tipo_servico=TipoServicoEnum.LUZ)
        #Pedir mais samples desse pq aparentemente o preco/imposto mudou dia 10 de janeiro, no meio do periodo de faturacao entao o documento normal pode ser diferente

        conta_consumo.id_documento = self.get_data(text, 'EDPC801-', '\r\n')
        conta_consumo.id_contribuinte = 'N/A' #Self.get_data(text, 'Potência', '6,9 kVA (simples))
        conta_consumo.id_cliente = 'N/A'  # self.get_data(text, '(Código Ponto Entrega)', 'PT')
        conta_consumo.id_contrato = 'N/A'  
        
        conta_consumo.periodo_referencia = self.get_data(text, 'Periodo de faturacao:', '\r\n')
        conta_consumo.data_emissao = self.get_data(text, 'Documento emitido a:', '\r\n')
        conta_consumo.valor = self.get_data(text, 'a pagar?\r\n', '\r\n')
        conta_consumo.data_vencimento = self.get_data(text, 'conta a partir de:\r\n', '\r\n')

        return self.adjust_data(conta_consumo)
