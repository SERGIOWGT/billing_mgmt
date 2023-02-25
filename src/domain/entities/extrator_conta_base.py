from datetime import datetime
from abc import abstractmethod
from dataclasses import dataclass

from src.domain.models.conta_consumo import ContaConsumo

@dataclass
class ExtratorContaConsumoBase:
    mes_extenso = {'janeiro': 1, 'fevereiro': 2, 'marco': 3, 'abril': 4, 'maio': 5, 'junho': 6,
                   'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
                   'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
                   'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}
    
    @staticmethod
    def clear_data(text: str)->str:
        if (text):
            text = text.replace(' ', '')

        return text

    @abstractmethod
    def get_info(self, text: str) -> ContaConsumo:
        pass

    @staticmethod
    def get_data(text, start_str, end_str) -> str:
        start_pos = 0
        end_pos = 0
        start_pos = text.find(start_str)

        if start_pos > 0:
            if (len(text) > start_pos+len(start_str)+1):
                end_pos = text.find(end_str, start_pos+len(start_str)+1)

        if (start_pos >= end_pos):
            return ""

        start_pos += len(start_str)
        ret = text[start_pos:end_pos]
        ret = ret.replace('\r', '').replace('\n', '')

        return ret

    def is_date(self, str_date) -> bool:
        try:
            _date = datetime.strptime(str_date, '%d/%m/%Y')
        except ValueError:
            return False

        return True

    def convert_date(self, str_date: str) -> str:
        if (self.is_date(str_date)):
            return str_date

        if (not str_date):
            return ''

        str_date = str_date.strip()
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

    def adjust_data(self, _in: ContaConsumo) -> ContaConsumo:
        _in.id_documento = self.clear_data(_in.id_documento)
        _in.id_cliente = self.clear_data(_in.id_cliente)
        _in.id_contrato = self.clear_data(_in.id_contrato)
        _in.id_contribuinte = self.clear_data(_in.id_contribuinte)
        _in.data_emissao = self.convert_date(_in.data_emissao)
        _in.data_vencimento = self.convert_date(_in.data_vencimento)
        _in.valor = self.clear_data(_in.valor)
        return _in
        