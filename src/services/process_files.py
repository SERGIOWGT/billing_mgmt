import os
from dataclasses import dataclass
from typing import Union, List
from src.infra.pdf_extractor_handler.pdf_extractor_handler import PdfExtractorHandler
from src.services.conta_consumo_factory import ContaConsumoFactory

@dataclass
class ProcessFiles:
    @staticmethod
    def execute(log, download_folder: str) -> Union[List, List, List]:
        processed_list = []
        error_list = []
        ignored_list = []
        for file_name in [f.upper() for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f)) and f.upper().endswith('.PDF') == True]:
            complete_file_name = os.path.join(download_folder, file_name)
            log.info(f'Processing file: {complete_file_name}')

            all_text = PdfExtractorHandler().get_text(complete_file_name)
            conta_consumo = ContaConsumoFactory().execute(all_text)
            if (conta_consumo):
                conta_consumo.file_name = complete_file_name
                try:
                    conta_consumo.create(all_text)
                    if (conta_consumo.id_documento == '106007420385'):
                        a = 0
                    
                    if (conta_consumo.is_ok() is False):
                    
                        error_list.append(conta_consumo)
                    else:
                        processed_list.append(conta_consumo)

                except Exception:
                    error_list.append(conta_consumo)
            else:
                msg = f'Arquivo não reconhecido ou fora do formato {complete_file_name}'
                log.info(msg)
                ignored_list.append({'file_name': complete_file_name, 'msg': msg})

        return processed_list, error_list, ignored_list
