from dataclasses import dataclass

@dataclass
class PaidUtilityBill():
    nome_concessionaria: str
    nome_tipo_servico: str
    nome_Accommodation: str
    id_documento: str
    dt_emissao: str
    original_file_id: str
    dt_begin_ref: str
    dt_end_ref: str
    nome_tipo_documento: str
