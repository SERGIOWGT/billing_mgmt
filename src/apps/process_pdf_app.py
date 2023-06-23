from dataclasses import dataclass
from typing import List
from src.domain.entities.response_error import UtilityBillErrorResponse, UtilityBillIgnoredResponse, UtilityBillOkResponse
from src.domain.enums.document_type_enum import DocumentTypeEnum

from src.infra.exception_handler import ApplicationException
from src.infra.google_drive_handler.Igoogle_drive_handler import IGoogleDriveHandler
from src.infra.pdf_extractor_handler.pdf_extractor_handler import PdfExtractorHandler
from src.infra.repositorios.repositorio_alojamentos import AccommodationRepository
from src.services.utility_bill_factory import UtilityBillFactory


@dataclass
class ProcessPdfApp:
    _drive = None
    _log = None
    _in_analise_list = None
    _processed_list = None
    _error_list: List[UtilityBillErrorResponse] = None
    _ignored_list: List[UtilityBillIgnoredResponse] = None
    _accommodations_repo: AccommodationRepository = None
    
    def __init__(self, drive: IGoogleDriveHandler, log, accommodations_repo: AccommodationRepository):
        ApplicationException.when(log is None, 'Log não iniciado.')
        ApplicationException.when(drive is None, 'Google Drive não iniciado.', log)
        self._drive = drive
        self._log = log
        self._processed_list = []
        self._in_analise_list = []
        self._error_list = List[UtilityBillErrorResponse]
        self._ignored_list = List[UtilityBillIgnoredResponse]
        self._accommodations_repo = accommodations_repo

    def _read_files(self, work_folder_id: str)->None:
        files_in_drive = self._drive.get_files(work_folder_id)
        files = files_in_drive['files']
        for file in files:
            file_id = file['id']
            file_name = file['name']
            complete_file_name = file_name  # SO PARA MANTER A COMPATIBILIDADE
            self._log.info(f'Getting file: {file_name}', instant_msg=True)

            file_content = self._drive.get_file(file_id)
            all_text = PdfExtractorHandler().get_text(file_content)
            conta_consumo = UtilityBillFactory().execute(all_text)
            if (conta_consumo):
                try:
                    conta_consumo.create(all_text)
                    if conta_consumo.tipo_documento == DocumentTypeEnum.DETALHE_FATURA:
                        self._ignored_list.append(UtilityBillIgnoredResponse(error_type='1', email_file_id=file_id, google_file_id='', file_name=file_name, complete_file_name=complete_file_name))
                    elif conta_consumo.is_ok():
                        self._in_analise_list.append(UtilityBillOkResponse(email_file_id=file_id, google_file_id='', file_name=file_name,
                                                    complete_file_name=complete_file_name, utility_bill=conta_consumo))
                    else:
                        self._error_list.append(UtilityBillErrorResponse(error_type='6', email_file_id=file_id, google_file_id='',
                                          file_name=file_name, complete_file_name=complete_file_name, utility_bill=conta_consumo))
                except Exception:
                    self._error_list.append(UtilityBillErrorResponse(error_type='5', email_file_id=file_id, google_file_id='',
                                      file_name=file_name, complete_file_name=complete_file_name, utility_bill=conta_consumo))
            else:
                self._ignored_list.append(UtilityBillIgnoredResponse(error_type='4', email_file_id=file_id, google_file_id='', file_name=file_name, complete_file_name=complete_file_name))


    def _check_utilities_bill(self)->None:
        for conta_consumo in self._in_analise_list:
            print(conta_consumo)

    def execute(self, work_folder_id: str):
        # Aqui le os arquivos e os separa em com erro, ignorados e em analise
        self._read_files(work_folder_id)
        
        # Criar uma rotina que pega os arquivos em análise e joga nas listas corretas od já pagos, duplicados, com erro, e nos avisos do clovis
        self._check_utilities_bill()
        
        # Rotina para subir os arquivos das contas(igual do antigo)
        
        # Rotina para subir os arquivos de resultados (igual ao antigo)
        
        # Rotina para para excluir os emails
