from abc import abstractmethod
from dataclasses import dataclass

from domain.models.conta_consumo import ContaConsumo

@dataclass
class ExtratorContaConsumoBase:
    @abstractmethod
    def get_info(self, text: str) -> ContaConsumo:
        pass
    
    @staticmethod
    def get_data(text, start_str, end_str) -> str:
        start_pos = 0
        end_pos = 0
        start_pos = text.find(start_str)   
        
        if start_pos > 0:
            end_pos = text.find(end_str, start_pos+1)

        if (start_pos >= end_pos):
            return ""

        start_pos += len(start_str)
        ret = text[start_pos:end_pos]
        ret = ret.replace('\r', '').replace('\n', '')
            
        return ret