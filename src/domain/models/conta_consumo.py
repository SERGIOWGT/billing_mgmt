from dataclasses import dataclass
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum

@dataclass
class ContaConsumo:
    concessionaria: ConcessionariaEnum
    tipo_servico: TipoServicoEnum
    id_contribuinte = ''
    id_cliente = ''
    nome_contribuinte = ''
    periodo_referencia = ''
    data_emissao = ''
    data_vencimento = ''
    valor = ''
