from dataclasses import dataclass, field
from src.domain.entities.alojamentos import PoolAlojamentos

@dataclass
class ReportResult:

    def __init__ (self, ok_list, error_list, ignored_list):
        self._ok_list = ok_list
        self._error_list = error_list
        self._ignored_list = ignored_list
        self._not_found_list = []
        self._new_ok_list = ok_list
        
    def _handle_ok_list(self, alojamentos: PoolAlojamentos) -> None:
        _new_ok_list = []
        for conta in self._ok_list:
            alojamento = alojamentos.get_alojamento(conta.id_cliente.strip(), conta.id_contrato.strip(), conta.local_consumo.strip())
            if (alojamento):
                conta.id_alojamento = alojamento.nome
                conta.diretorio = alojamento.diretorio
                self._new_ok_list.append(conta)
            else:
                self._not_found_list.append(conta)
    
    def _handle_error_list() -> None:
        ...

    def _handle_ignored_list() -> None:
        ...    
    
        
    def execute(self):
        
