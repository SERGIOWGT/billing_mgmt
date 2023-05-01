import os
import shutil
from dataclasses import dataclass
from typing import List, Tuple
from src.domain.entities.paid_utility_bill_list import PaidUtilityBillList
from src.domain.enums.document_type_enum import DocumentTypeEnum

from src.domain.entities.base.base_utility_bill import UtilityBillBase
from src.domain.entities.accommodation_list import AccommodationList
from src.infra.pdf_extractor_handler.pdf_extractor_handler import \
    PdfExtractorHandler
from src.services.utility_bill_factory import UtilityBillFactory


@dataclass
class FilesHandler:
    @staticmethod
    def move_files(log, destination_folder: str, file_list: List[str]) -> None:
        for file_name in file_list:
            new_file_name = os.path.join(destination_folder, os.path.basename(file_name))
            shutil.move(file_name, new_file_name)

    @staticmethod
    def execute(log, download_folder: str, accommodation_list: AccommodationList, contas_pagas: PaidUtilityBillList) -> Tuple[List[UtilityBillBase], List[UtilityBillBase], List[UtilityBillBase], List[dict]]:
        processed_list = []
        not_found_list = []
        error_list = []
        ignored_list = []
        for file_name in [f.upper() for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f)) and f.upper().endswith('.PDF') == True]:
            complete_file_name = os.path.join(download_folder, file_name)
            log.info(f'Processing file: {complete_file_name}')

            all_text = PdfExtractorHandler().get_text(complete_file_name)
            conta_consumo = UtilityBillFactory().execute(all_text)
            if (conta_consumo):
                conta_consumo.file_name = complete_file_name
                try:
                    conta_consumo.create(all_text)
                    if conta_consumo.tipo_documento == DocumentTypeEnum.DETALHE_FATURA:
                        ignored_list.append({'file_name': complete_file_name, 'msg': conta_consumo.str_erro, 'Link Google': ''})
                    elif conta_consumo.is_ok():
                        accommodation = accommodation_list.get_accommodation(conta_consumo.concessionaria, conta_consumo.id_cliente.strip(),
                                                                         conta_consumo.id_contrato.strip(), conta_consumo.local_consumo.strip())
                        if (accommodation):
                            conta_consumo.id_alojamento = accommodation.nome
                            conta_consumo.diretorio_google = accommodation.diretorio

                            if (conta_consumo.tipo_documento == DocumentTypeEnum.NOTA_CREDITO) or (conta_consumo.tipo_documento == DocumentTypeEnum.FATURA_ZERADA):
                                if (conta_consumo.dt_emissao is None):
                                    error_list.append(conta_consumo)
                                    continue

                            ja_foi_paga = contas_pagas.exists(conta_consumo.concessionaria, conta_consumo.tipo_servico, accommodation.nome, conta_consumo.id_documento)
                            if (ja_foi_paga):
                                conta_consumo.str_erro = 'Conta já foi processada'
                                error_list.append(conta_consumo)
                            else:
                                processed_list.append(conta_consumo)
                        else:
                            not_found_list.append(conta_consumo)
                    else:
                        error_list.append(conta_consumo)

                except Exception:
                    error_list.append(conta_consumo)
            else:
                msg = f'Arquivo não reconhecido ou fora do formato {complete_file_name}'
                log.info(msg)
                ignored_list.append({'file_name': complete_file_name, 'msg': msg, 'Link Google': ''})

        return processed_list, not_found_list, error_list, ignored_list
