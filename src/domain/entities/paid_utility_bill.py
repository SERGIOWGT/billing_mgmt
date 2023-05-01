from dataclasses import dataclass

@dataclass
class PaidUtilityBill():
    nome_concessionaria: str
    nome_tipo_servico: str
    nome_Accommodation: str
    id_documento: str
    dt_emissao: str
