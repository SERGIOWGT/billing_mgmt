from dataclasses import dataclass
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum

@dataclass
class ContaConsumo:
    concessionaria: ConcessionariaEnum
    tipo_servico: TipoServicoEnum
    id_documento = ''
    id_contribuinte = ''
    id_cliente = ''
    id_contrato = ''
    nome_cliente = ''
    periodo_referencia = ''
    local_consumo = ''
    data_emissao = ''
    data_vencimento = ''
    valor = ''
    file_name = ''
