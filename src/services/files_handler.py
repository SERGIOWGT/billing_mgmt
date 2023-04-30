import os
import shutil
from dataclasses import dataclass
from typing import List, Tuple
from src.domain.entities.contas_pagas import PoolContasPagas
from src.domain.enums.tipo_documento_enum import TipoDocumentoEnum

from src.domain.entities.base.conta_consumo_base import ContaConsumoBase
from src.domain.entities.alojamentos import PoolAlojamentos
from src.infra.pdf_extractor_handler.pdf_extractor_handler import \
    PdfExtractorHandler
from src.services.conta_consumo_factory import ContaConsumoFactory


@dataclass
class FilesHandler:
    @staticmethod
    def move_files(log, destination_folder: str, file_list: List[str]) -> None:
        for file_name in file_list:
            new_file_name = os.path.join(destination_folder, os.path.basename(file_name))
            shutil.move(file_name, new_file_name)


    @staticmethod
    def execute(log, download_folder: str, alojamentos: PoolAlojamentos, contas_pagas: PoolContasPagas) -> Tuple[List[ContaConsumoBase], List[ContaConsumoBase], List[ContaConsumoBase], List[dict]]:
        processed_list = []
        not_found_list = []
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
                    if conta_consumo.tipo_documento == TipoDocumentoEnum.DETALHE_FATURA:
                        ignored_list.append({'file_name': complete_file_name, 'msg': conta_consumo.str_erro, 'Link Google': ''})
                    elif (conta_consumo.tipo_documento == TipoDocumentoEnum.NOTA_CREDITO) or (conta_consumo.tipo_documento == TipoDocumentoEnum.FATURA_ZERADA):
                        error_list.append(conta_consumo)
                    elif conta_consumo.is_ok():
                        alojamento = alojamentos.get_alojamento(conta_consumo.concessionaria, conta_consumo.id_cliente.strip(), conta_consumo.id_contrato.strip(), conta_consumo.local_consumo.strip())
                        if (alojamento):
                            conta_consumo.id_alojamento = alojamento.nome
                            conta_consumo.diretorio_google = alojamento.diretorio

                            ja_foi_paga = contas_pagas.exists(conta_consumo.concessionaria, conta_consumo.tipo_servico, alojamento.nome, conta_consumo.id_documento)
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
