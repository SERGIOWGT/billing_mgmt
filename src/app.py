import io
import os
import time
from datetime import datetime, date
from typing import Any, List
from dataclasses import dataclass
import pandas as pd

from src.domain.enums.tipo_servico_enum import TipoServicoEnum
from src.domain.entities.conta_consumo_base import ContaConsumoBase

from src.infra.google_drive_handler.Igoogle_drive_handler import IGoogleDriveHandler
from src.domain.enums.concessionaria_enum import ConcessionariaEnum
from src.domain.entities.alojamentos import Alojamento, PoolAlojamentos
from src.services.process_files import ProcessFiles
from src.infra.email_handler.Imail_handler import IEmailHandler
from src.infra.email_handler.email_handler import EmailHandler
from src.services.download_attachment_handler import DownloadAttachmentHandler

from src.infra.app_configuration_reader.iapp_configuration_reader import IAppConfigurationReader
from src.infra.google_drive_handler.google_drive_handler import GoogleDriveHandler
from src.infra.exception_handler import ApplicationException

@dataclass
class App:

    def __init__(self, app_config: IAppConfigurationReader, drive: IGoogleDriveHandler, log):
        self.downloads_folder = app_config.get('directories.downloads')
        ApplicationException.when(not os.path.exists(self.downloads_folder), f'Path does not exist. [{self.downloads_folder}]', log)

        self.export_folder = app_config.get('directories.exports')
        ApplicationException.when(not os.path.exists(self.export_folder), f'Path does not exist. [{self.export_folder}]', log)

        ## aqui tem que locar
        self._drive = GoogleDriveHandler(app_config.get("directories.config"))
        ApplicationException.when(self._drive is None, 'Google Drive not connected.', log)

        self._log = log
        self._app_config = app_config
        self._drive = drive

    def _get_alojamentos(self) -> PoolAlojamentos:
        stream_file = self._drive.get_excel_file(self._app_config.get('google drive.file_accommodation_id'))
        df_ = pd.read_excel(io.BytesIO(stream_file))
        df = df_.where(pd.notnull(df_), None)

        alojamentos = []
        for index, row in df.iterrows():
            if (index < 1):
                continue

            nome = row[2]
            diretorio = row[3]
            for empresa in [x for x in list(ConcessionariaEnum) if x != ConcessionariaEnum.NADA]:
                cliente = row[1 + (3 * empresa)]
                conta = row[2 + (3 * empresa)]
                local = row[3 + (3 * empresa)]

                cliente = '' if (str(cliente) == 'None') else str(cliente).replace(' ', '')
                conta = '' if (str(conta) == 'None') else str(conta).replace(' ', '')
                local = '' if (str(local) == 'None') else str(local).replace(' ', '')

                if cliente or conta or local:
                    alojamentos.append(Alojamento(empresa, nome, diretorio, cliente, conta, local))

        return PoolAlojamentos(alojamentos)

    def _handle_ok_list(self, data: list[Any]) -> Any:
        alojamentos = self._get_alojamentos()

        not_found_list = []
        new_ok_list = []
        for conta in data:
            if (conta.concessionaria == ConcessionariaEnum.ALTICE_MEO):
                a = 0
                
            alojamento = alojamentos.get_alojamento(conta.concessionaria, conta.id_cliente.strip(), conta.id_contrato.strip(), conta.local_consumo.strip())
            if (alojamento):
                conta.id_alojamento = alojamento.nome
                conta.diretorio_google = alojamento.diretorio
                conta.nome_arquivo_google = self.mountFileName(conta.dt_vencimento, conta.concessionaria, conta.id_alojamento)
                new_ok_list.append(conta)
            else:
                not_found_list.append(conta)

        return (new_ok_list, not_found_list)

    def _create_df_ok(self, list: List[ContaConsumoBase]) -> Any:
        columns = ['Alojamento', 'Concessionaria', 'Tipo Servico', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local / Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia', 'Fim Referencia',  'Emissao', 'Vencimento', 'Valor', 'Diretorio Google', 'Arquivo Google', 'Arquivo Original']

        df = pd.DataFrame(columns=columns)
        for line in list:
            _dict = {}
            _dict['Alojamento'] = line.id_alojamento
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

    def _result_2_excel(self, new_ok_list, not_found_list, error_list, ignored_list):
        new_ok_list.sort(key=lambda x: x.concessionaria)
        not_found_list.sort(key=lambda x: x.concessionaria)
        error_list.sort(key=lambda x: x.concessionaria)

        df_ok = self._create_df_ok(new_ok_list)
        df_nf = self._create_df_sem_alojamento(not_found_list)
        df_error = self._create_df_error(error_list)
        df_ignored = self._create_df_ignored(ignored_list)

        now = datetime.now()
        output_file_name = f'output_{now.strftime("%Y-%m-%d.%H.%M.%S")}.xlsx'

        output_file_name = os.path.join(self.export_folder, output_file_name)

        with pd.ExcelWriter(output_file_name) as writer:
            df_ok.to_excel(writer, sheet_name='Processados', index=False)
            df_nf.to_excel(writer, sheet_name='Sem Alojamentos', index=False)
            df_error.to_excel(writer, sheet_name='Erros', index=False)
            df_ignored.to_excel(writer, sheet_name='Ignorados', index=False)

    def _process_downloaded_files(self) -> None:
        download_folder = self._app_config.get('directories.downloads')
        ok_list, error_list, ignored_list = ProcessFiles.execute(self._log, download_folder)

        (new_ok_list, not_found_list) = self._handle_ok_list(ok_list)
        self._result_2_excel(new_ok_list, not_found_list, error_list, ignored_list)

        parent_id = self._app_config.get('google drive.folder_client_id')
        for conta_ok in new_ok_list:
            new_parent_id = self._drive.find_file(conta_ok.diretorio_google, parent_id)
            if (new_parent_id is None):
                new_folder = self._drive.create_folder(conta_ok.diretorio_google, parent_id)
                self._log.info(f'Creating google drive directory {conta_ok.diretorio_google}')
                time.sleep(3)
                while (True):
                    new_parent_id = self._drive.find_file(conta_ok.diretorio_google, parent_id)
                    if (new_parent_id):
                        break
                    time.sleep(3)

                self._log.info('Created')
                new_folder = new_parent_id

            parents = [new_parent_id]
            self._log.info(f'Uploading file {conta_ok.nome_arquivo_google}')
            self._drive.upload_file(conta_ok.file_name, conta_ok.nome_arquivo_google, parents)

    def _get_and_connect_email(self)->IEmailHandler:
        email = EmailHandler()
        try:
            smtp_server = self._app_config.get('email.imap_server')
            user = self._app_config.get('email.user')
            password = self._app_config.get('email.password')
            email.login(smtp_server, user, password, use_ssl=True)
        except Exception:
            # tratar os eerros aqui
            raise
        return email

    def _download_emails(self, email) -> None:
        path_to_save = self._app_config.get('directories.downloads')
        ApplicationException.when(not os.path.exists(path_to_save), f'Path does not exist. [{path_to_save}]', self._log)
        input_email_folder = self._app_config.get('email.input_folder')
        output_email_folder = self._app_config.get('email.output_folder')
        DownloadAttachmentHandler.execute(path_to_save, input_email_folder, output_email_folder, self._log, email)

    def execute(self):
        email = self._get_and_connect_email()

        try:
            self._download_emails(email)
        except Exception:
            # tratar os eerros aqui
            raise

        self._process_downloaded_files()

        email.logout()

    def mountFileName(self, dt_vencimento: date, concessionaria: ConcessionariaEnum, alojamento: str) -> str:

        _name_list = ['', 'EDP', 'Galp', 'Aguas', 'Aguas', 'EPAL', 'Altice(MEO)', 'NOS', 'Vodafone']

        _dt_vencimento = dt_vencimento.strftime("%Y.%m.%d")
        _concessionaria = _name_list[concessionaria]
        _vet = alojamento.split('_')
        _alojamento = alojamento
        if (len(_vet) > 1):
            _alojamento = f'{_vet[0]}_{_vet[1]}'

        return f'{_dt_vencimento} {_concessionaria} - {_alojamento}.pdf'
