from dataclasses import dataclass
import os
import time
from typing import Any, List
from datetime import datetime, date
import pandas as pd
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from src.domain.entities.conta_consumo_base import ContaConsumoBase
from src.infra.google_drive_handler.Igoogle_drive_handler import IGoogleDriveHandler
from src.domain.entities.alojamentos import PoolAlojamentos


@dataclass
class UploadSaveResults:
    _log: Any
    _drive: IGoogleDriveHandler

    def __init__(self, log, drive: IGoogleDriveHandler):
        self._log = log
        self._drive = drive

    def _create_df_ok(self, list: List[ContaConsumoBase]) -> Any:
        columns = ['Alojamento', 'Ano Emissao', 'Mes Emissao', 'Concessionaria', 'Tipo Servico', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local / Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia', 'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Diretorio Google', 'Arquivo Google', 'Arquivo Original']
        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['Alojamento'] = line.id_alojamento
            _dict['Ano Emissao'] = str(line.dt_emissao.year)
            _dict['Mes Emissao'] = format(line.dt_emissao.month, '02d')
            _dict['Concessionaria'] = ConcessionariaEnum(line.concessionaria).name
            _dict['Tipo Servico'] = TipoServicoEnum(line.tipo_servico).name
            _dict['N. Contrato'] = line.id_contrato
            _dict['N. Cliente'] = line.id_cliente
            _dict['N. Contribuinte'] = line.id_contribuinte
            _dict['Local / Instalacao'] = line.local_consumo
            _dict['N. Documento / N. Fatura'] = line.id_documento
            _dict['Periodo Referencia'] = line.periodo_referencia
            _dict['Inicio Referencia'] = line.str_inicio_referencia
            _dict['Fim Referencia'] = line.str_fim_referencia
            _dict['Emissao'] = line.str_emissao
            _dict['Vencimento'] = line.str_vencimento
            _dict['Valor'] = line.str_valor
            _dict['Diretorio Google'] = line.diretorio_google
            _dict['Arquivo Google'] = line.nome_arquivo_google
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_sem_alojamento(self, list: List[ContaConsumoBase]) -> Any:
        columns = ['Concessionaria', 'Tipo Servico', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                 'Local / Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia', 
                 'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Arquivo Original']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['Concessionaria'] = ConcessionariaEnum(line.concessionaria).name
            _dict['Tipo Servico'] = TipoServicoEnum(line.tipo_servico).name
            _dict['N. Contrato'] = line.id_contrato
            _dict['N. Cliente'] = line.id_cliente
            _dict['N. Contribuinte'] = line.id_contribuinte
            _dict['Local / Instalacao'] = line.local_consumo
            _dict['N. Documento / N. Fatura'] = line.id_documento
            _dict['Periodo Referencia'] = line.periodo_referencia
            _dict['Inicio Referencia'] = line.str_inicio_referencia
            _dict['Fim Referencia'] = line.str_fim_referencia
            _dict['Emissao'] = line.str_emissao
            _dict['Vencimento'] = line.str_vencimento
            _dict['Valor'] = line.str_valor
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_error(self, list: List[ContaConsumoBase]) -> Any:
        columns = ['Concessionaria', 'Tipo Servico', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local / Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia',
                   'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Erro', 'Arquivo Original']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['Concessionaria'] = ConcessionariaEnum(line.concessionaria).name
            _dict['Tipo Servico'] = TipoServicoEnum(line.tipo_servico).name
            _dict['N. Contrato'] = line.id_contrato
            _dict['N. Cliente'] = line.id_cliente
            _dict['N. Contribuinte'] = line.id_contribuinte
            _dict['Local / Instalacao'] = line.local_consumo
            _dict['N. Documento / N. Fatura'] = line.id_documento
            _dict['Periodo Referencia'] = line.periodo_referencia
            _dict['Inicio Referencia'] = line.str_inicio_referencia
            _dict['Fim Referencia'] = line.str_fim_referencia
            _dict['Emissao'] = line.str_emissao
            _dict['Vencimento'] = line.str_vencimento
            _dict['Valor'] = line.str_valor
            _dict['Erro'] = line.str_erro
            _dict['Arquivo Original'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_ignored(self, list) -> Any:
        columns = ['Erro', 'Arquivo']
        df = pd.DataFrame(columns=columns)
        for line in list:
            df = df.append({'Erro': line['msg'], 'Arquivo': line['file_name']}, ignore_index=True)

        return df

    def _result_2_excel(self, export_folder: str, new_ok_list: List[ContaConsumoBase], not_found_list: List[ContaConsumoBase], error_list: List[ContaConsumoBase], ignored_list: List[Any]):
        new_ok_list.sort(key=lambda x: x.concessionaria)
        not_found_list.sort(key=lambda x: x.concessionaria)
        error_list.sort(key=lambda x: x.concessionaria)

        df_ok = self._create_df_ok(new_ok_list)
        df_nf = self._create_df_sem_alojamento(not_found_list)
        df_error = self._create_df_error(error_list)
        df_ignored = self._create_df_ignored(ignored_list)

        now = datetime.now()
        output_file_name = f'output_{now.strftime("%Y-%m-%d.%H.%M.%S")}.xlsx'
        output_file_name = os.path.join(export_folder, output_file_name)
        with pd.ExcelWriter(output_file_name) as writer:
            df_ok.to_excel(writer, sheet_name='Processados', index=False)
            df_nf.to_excel(writer, sheet_name='Sem Alojamentos', index=False)
            df_error.to_excel(writer, sheet_name='Erros', index=False)
            df_ignored.to_excel(writer, sheet_name='Ignorados', index=False)

    def _handle_ok_list(self, alojamentos: PoolAlojamentos, data: list[Any]) -> Any:
        not_found_list = []
        new_ok_list = []
        for conta in data:
            alojamento = alojamentos.get_alojamento(conta.concessionaria, conta.id_cliente.strip(), conta.id_contrato.strip(), conta.local_consumo.strip())
            if (alojamento):
                conta.id_alojamento = alojamento.nome
                conta.diretorio_google = alojamento.diretorio
                conta.nome_arquivo_google = self._mountFileName(conta.dt_vencimento, conta.concessionaria, conta.id_alojamento)
                new_ok_list.append(conta)
            else:
                not_found_list.append(conta)

        return (new_ok_list, not_found_list)

    def _mountFileName(self, dt_vencimento: date, concessionaria: ConcessionariaEnum, alojamento: str) -> str:

        _name_list = ['', 'EDP', 'Galp', 'Aguas', 'Aguas', 'EPAL', 'Altice(MEO)', 'NOS', 'Vodafone']

        _dt_vencimento = dt_vencimento.strftime("%Y.%m.%d")
        _concessionaria = _name_list[concessionaria]
        _vet = alojamento.split('_')
        _alojamento = alojamento
        if (len(_vet) > 1):
            _alojamento = f'{_vet[0]}_{_vet[1]}'

        return f'{_dt_vencimento} {_concessionaria} - {_alojamento}.pdf'

    def execute(self, folder_base_id: str, export_folder: str, alojamentos: PoolAlojamentos, ok_list: List[ContaConsumoBase], error_list: List[ContaConsumoBase], ignored_list: List[Any])->None:
        (new_ok_list, not_found_list) = self._handle_ok_list(alojamentos, ok_list)
        self._result_2_excel(export_folder, new_ok_list, not_found_list, error_list, ignored_list)

        for conta_ok in new_ok_list:
            new_parent_id = self._drive.find_file(conta_ok.diretorio_google, folder_base_id)
            if (new_parent_id is None):
                new_folder = self._drive.create_folder(conta_ok.diretorio_google, folder_base_id)
                self._log.info(f'Creating google drive directory {conta_ok.diretorio_google}')
                time.sleep(3)
                while (True):
                    new_parent_id = self._drive.find_file(conta_ok.diretorio_google, folder_base_id)
                    if (new_parent_id):
                        break
                    time.sleep(3)

                self._log.info('Created')
                new_folder = new_parent_id

            parents: List[str] = [new_parent_id]
            self._log.info(f'Uploading file {conta_ok.nome_arquivo_google}')
            self._drive.upload_file(conta_ok.file_name, conta_ok.nome_arquivo_google, parents)
