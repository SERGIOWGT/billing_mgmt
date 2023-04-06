import io
import os
import time
from dataclasses import dataclass
import pandas as pd

from src.infra.google_drive_handler.Igoogle_drive_handler import IGoogleDriveHandler
from src.domain.enums.concessionaria_enum import ConcessionariaEnum
from src.domain.entities.alojamentos import Alojamento, PoolAlojamentos
from src.services.process_files import ProcessFiles
from src.infra.email_handler.Imail_handler import IEmailHandler
from src.infra.email_handler.email_handler import EmailHandler
from src.services.download_attachment_handler import DownloadAttachmentHandler
from src.services.upload_save_results import UploadSaveResults

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

    def _process_downloaded_files(self) -> None:
        download_folder = self._app_config.get('directories.downloads')
        ok_list, error_list, ignored_list = ProcessFiles.execute(self._log, download_folder)

        upload_save_results = UploadSaveResults(self._log, self._drive)
        folder_base_id = self._app_config.get('google drive.folder_client_id')
        export_folder = self._app_config.get('directories.exports')
        alojamentos = self._get_alojamentos()
        upload_save_results.execute(folder_base_id, export_folder, alojamentos, ok_list, error_list, ignored_list)

    def execute(self):
        email = self._get_and_connect_email()
        self._download_emails(email)
        self._process_downloaded_files()
        email.logout()
