import io
import os
from typing import Any, List
from dataclasses import dataclass
import pandas as pd

from src.domain.enums.tipo_servico_enum import TipoServicoEnum

from src.domain.models.conta_consumo import ContaConsumo
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

    def _handle_ok_list(self, data: list[Any]) -> None:
        alojamentos = self._get_alojamentos()
        
        self._not_found_list = []
        self._new_ok_list = []
        for conta in data:
            alojamento = alojamentos.get_alojamento(conta.id_cliente.strip(), conta.id_contrato.strip(), conta.local_consumo.strip())
            if (alojamento):
                conta.id_alojamento = alojamento.nome
                conta.diretorio = alojamento.diretorio
                self._new_ok_list.append(conta)
            else:
                self._not_found_list.append(conta)

    def _create_df_default(self, list: List[ContaConsumo]) -> Any:
        columns = ['Alojamento', 'Concessionaria', 'Tipo Servico', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local / Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Emissao', 'Vencimento', 'Valor', 'Diretorio Google', 'Arquivo']

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
            _dict['Emissao'] = line.data_emissao
            _dict['Vencimento'] = line.data_vencimento
            _dict['Valor'] = line.valor
            _dict['Diretorio Google'] = line.gdrive_dir
            _dict['Arquivo'] = line.file_name

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_ignored(self, list) -> Any:
        columns = ['Erro', 'Arquivo']
        df = pd.DataFrame(columns=columns)
        for line in list:
            df = df.append({'Erro': line['msg'], 'Arquivo': line['file_name']}, ignore_index=True)

        return df

    def _result_2_excel(self, error_list, ignored_list):
        df_ok = self._create_df_default(self._new_ok_list)
        df_nf = self._create_df_default(self._not_found_list)
        df_error = self._create_df_default(error_list)
        df_ignored = self._create_df_ignored(ignored_list)
        output_file_name = os.path.join(self.export_folder, 'output.xlsx')

        with pd.ExcelWriter(output_file_name) as writer:
            df_ok.to_excel(writer, sheet_name='Processados', index=False)
            df_nf.to_excel(writer, sheet_name='Sem Alojamentos', index=False)
            df_error.to_excel(writer, sheet_name='Erros', index=False)
            df_ignored.to_excel(writer, sheet_name='Ignorados', index=False)

    def _process_downloaded_files(self) -> None:
        download_folder = self._app_config.get('directories.downloads')
        ok_list, error_list, ignored_list = ProcessFiles.execute(self._log, download_folder)
        
        self._handle_ok_list(ok_list)
        self._result_2_excel(error_list, ignored_list)
              
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
       
