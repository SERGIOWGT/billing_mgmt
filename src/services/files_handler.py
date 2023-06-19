import os
import shutil
from dataclasses import dataclass
from typing import List, Tuple
from src.domain.entities.response_error import UtilityBillIgnoredResponse, UtilityBillDuplicatedResponse, UtilityBillOkResponse, UtilityBillErrorResponse
from src.domain.entities.paid_utility_bill_list import PaidUtilityBillList
from src.domain.enums.document_type_enum import DocumentTypeEnum
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
            try:
                shutil.move(file_name, new_file_name)
                log.info(f'File moved: {file_name} --> {new_file_name}', instant_msg=True)
            except:
                log.info(f'File moved error: {file_name} --> {new_file_name}', instant_msg=True)

    @staticmethod
    def execute(log, download_folder: str, accommodation_list: AccommodationList, contas_pagas: PaidUtilityBillList) -> Tuple[List[UtilityBillOkResponse], List[UtilityBillErrorResponse], List[UtilityBillErrorResponse], List[UtilityBillDuplicatedResponse], List[UtilityBillIgnoredResponse]]:
        processed_list = []
        not_found_list: List[UtilityBillErrorResponse] = []
        error_list: List[UtilityBillErrorResponse] = []
        duplicated_list: List[UtilityBillDuplicatedResponse] = []
        ignored_list: List[UtilityBillIgnoredResponse] = []

        for file_name in [f.upper() for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f)) and f.upper().endswith('.PDF') == True]:
            complete_file_name = os.path.join(download_folder, file_name)
            log.info(f'Processing file: {file_name}', instant_msg=True)

            try:
                all_text = PdfExtractorHandler().get_text(complete_file_name)
            except Exception as erro:
                ignored_list.append(UtilityBillIgnoredResponse(error_type='10', google_file_id='', file_name=file_name, complete_file_name=complete_file_name))
                continue
            
            conta_consumo = UtilityBillFactory().execute(all_text)
            if (conta_consumo):
                try:
                    conta_consumo.create(all_text)
                    if conta_consumo.tipo_documento == DocumentTypeEnum.DETALHE_FATURA:
                        ignored_list.append(UtilityBillIgnoredResponse(error_type='1', google_file_id='', file_name=file_name, complete_file_name=complete_file_name))
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
                                duplicated_list.append(UtilityBillDuplicatedResponse(google_file_id='', file_name=file_name, original_google_link='',
                                                       complete_file_name=complete_file_name, utility_bill=conta_consumo))
                            else:
                                xxx = UtilityBillOkResponse(google_file_id='', file_name=file_name, complete_file_name=complete_file_name, utility_bill=conta_consumo)
                                processed_list.append(xxx)
                        else:
                            not_found_list.append(UtilityBillErrorResponse(error_type='7', google_file_id='', file_name=file_name, complete_file_name=complete_file_name, utility_bill=conta_consumo))
                    else:
                        error_list.append(UtilityBillErrorResponse(error_type='6', google_file_id='', file_name=file_name, complete_file_name=complete_file_name, utility_bill=conta_consumo))
                
                except Exception:
                    error_list.append(UtilityBillErrorResponse(error_type='5', google_file_id='', file_name=file_name, complete_file_name=complete_file_name, utility_bill=conta_consumo))
            else:
                ignored_list.append(UtilityBillIgnoredResponse(error_type='4', google_file_id='', file_name=file_name, complete_file_name=complete_file_name))

        return processed_list, not_found_list, error_list, duplicated_list, ignored_list
