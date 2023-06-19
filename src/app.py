from datetime import datetime
import copy
import io
import os
from dataclasses import dataclass
import re
import time
from typing import List
import pandas as pd

from src.domain.entities.response_error import UtilityBillIgnoredResponse, UtilityBillDuplicatedResponse, UtilityBillOkResponse, UtilityBillErrorResponse
from src.domain.entities.base.base_utility_bill import UtilityBillBase
from src.domain.entities.paid_utility_bill import PaidUtilityBill
from src.domain.entities.paid_utility_bill_list import PaidUtilityBillList
from src.services.results_saver import ResultsSaver

from src.infra.google_drive_handler.Igoogle_drive_handler import IGoogleDriveHandler
from src.domain.enums import AccommodationStatusEnum, ServiceProviderEnum, DocumentTypeEnum
from src.domain.entities.accommodation import Accommodation
from src.domain.entities.accommodation_list import AccommodationList
from src.services.files_handler import FilesHandler
from src.infra.email_handler.Imail_handler import IEmailHandler
from src.infra.email_handler.email_handler import EmailHandler
from src.services.attachment_downloader import AttachmentDownloader
from src.services.results_uploader import ResultsUploader

from src.infra.exception_handler import ApplicationException


@dataclass
class App:
    _folder_base_id = ''
    _folder_contabil_id = ''
    _others_folder_base_id = ''
    _results_folder_id = ''
    _folder_client_id = ''
    _export_folder = ''
    _base_folder = ''
    _database_folder = ''
    _download_folder = ''
    _smtp_server = ''
    _user = ''
    _password = ''
    _input_email_folder = ''
    _output_email_folder = ''
    _accommodations = ''
    _except_list = ''
    _processed_list = ''
    _not_found_list = ''
    _error_list = ''
    _duplicated_list = ''
    _ignored_list = ''

    def __init__(self, work_directory, accommodation_file_id: str, drive: IGoogleDriveHandler, log):
        self._base_folder = work_directory
        ApplicationException.when(log is None, 'Log não iniciado.')
        ApplicationException.when(drive is None, 'Google Drive não iniciado.', log)
        ApplicationException.when(accommodation_file_id == '', 'Chave "accommodation_file_id" não encontrada no arquivo de configuração.', log)
        self._accommodation_file_id = accommodation_file_id
        self._drive = drive
        self._log = log
        self._dict_config = {}

    @classmethod
    def _remove_space_and_dot(cls, value: str) -> str:
        pos = value.find('.0')
        if pos == len(value) - 2:
            value = value.replace('.0', '')

        return re.sub('[.\s]+', '', value)

    def _get_processed_utility_bills(self) -> PaidUtilityBillList:
        self._log.info('Downloading the paid bills from the historical worksheet', instant_msg=True)
        file_name = os.path.join(self._database_folder, 'database.xlsx')
        if os.path.exists(file_name) is False:
            return PaidUtilityBillList([])

        contas = []
        df_ = pd.read_excel(file_name, dtype={'N. Documento / N. Fatura': object})
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 22, 'History Sheet must have 22 columns. ', self._log)
        expected_columns = ['QQ Destino', 'Alojamento', 'Ano Emissao', 'Mes Emissao', 'Concessionaria', 'Tipo Servico',
                            'Tipo Documento', 'N. Contrato', 'N. Cliente', 'N. Contribuinte', 'Local / Instalacao',
                            'N. Documento / N. Fatura', 'Periodo Referencia', 'Inicio Referencia', 'Fim Referencia',
                            'Emissao', 'Vencimento', 'Valor', 'Diretorio Google', 'Arquivo Google', 'Arquivo Original', 'Data Processamento']
        actual_columns = df.columns.tolist()

        ApplicationException.when(expected_columns != actual_columns, f'The Historical Spreadsheet should have the columns {actual_columns}.', self._log)
        for _, row in df.iterrows():
            nome_concessionaria = row['Concessionaria']
            nome_concessionaria = nome_concessionaria.replace('\n', '')
            nome_tipo_servico = row['Tipo Servico']
            nome_tipo_servico = nome_tipo_servico.replace('\n', '')
            nome_Accommodation = row['Alojamento']
            id_documento = row['N. Documento / N. Fatura']
            dt_emissao = row['Emissao']
            contas.append(PaidUtilityBill(nome_concessionaria, nome_tipo_servico, nome_Accommodation, id_documento, dt_emissao))

        return PaidUtilityBillList(contas)

    def _get_accommodations(self) -> AccommodationList:
        sheet_name = 'Alojamentos'
        stream_file = self._drive.get_excel_file(self._accommodation_file_id)
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name=sheet_name)
        df = df_.where(pd.notnull(df_), None)
        df = df.astype(str)
        cols = df.shape[1]
        ApplicationException.when(cols != 20, f'A Sheet "{sheet_name}" da planilha de Alojamentos deve ter 20 colunas. ', self._log)

        accommodation_status_list = [str(x.value) for x in AccommodationStatusEnum]

        list_aux = []
        for _, row in df.iterrows():
            column_list = row.index.tolist()

            nome_alojamento = row['Alojamento']
            diretorio = row['Google Drive']
            nif = row['NIF Titular']
            status = row['Status']
            ApplicationException.when(status not in accommodation_status_list, f'O alojamento "{nome_alojamento}" da planilha de Alojamentos esta com status incompativel. [{status}]', self._log)

            for id_concessionaria in [x for x in list(ServiceProviderEnum) if x != ServiceProviderEnum.DESCONHECIDO]:
                nome_concessionaria = str(id_concessionaria.name).replace('ServiceProviderEnum.', '')
                nome_concessionaria = nome_concessionaria.replace(' ', '')

                conta = str(row[f'{nome_concessionaria} Contrato']) if f'{nome_concessionaria} Contrato' in column_list else ''
                cliente = row[f'{nome_concessionaria} Cliente'] if f'{nome_concessionaria} Cliente' in column_list else ''
                local = row[f'{nome_concessionaria} Local Consumo'] if f'{nome_concessionaria} Local Consumo' in column_list else ''

                cliente = '' if (str(cliente) == 'None') else self._remove_space_and_dot(cliente)
                conta = '' if (str(conta) == 'None') else self._remove_space_and_dot(conta)
                local = '' if (str(local) == 'None') else self._remove_space_and_dot(local)
                nome_alojamento = '' if (str(nome_alojamento) == 'None') else str(nome_alojamento).replace(' ', '')
                diretorio = '' if (str(diretorio) == 'None') else str(diretorio).replace(' ', '')

                if cliente or conta or local:
                    list_aux.append(Accommodation(id_concessionaria, status, nome_alojamento, diretorio, nif, cliente, conta, local))

        ApplicationException.when(len(list_aux) == 0, f'A planilha de Alojamentos esta vazia.', self._log)
        self._accommodations = AccommodationList(list_aux)

    def _get_except_list(self) -> None:
        sheet_name = 'Excecoes'
        stream_file = self._drive.get_excel_file(self._accommodation_file_id)
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name=sheet_name)
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 4, f'A Sheet "{sheet_name}" da planilha de Alojamentos deve ter 4 colunas. ', self._log)
        expected_columns = ['Alojamento Origem', 'Concessionaria', 'Tipo de Excecao', 'Alojamentos Destino']
        actual_columns = df.columns.tolist()
        ApplicationException.when(expected_columns != actual_columns, f'A sheet "{sheet_name}" da planilha de Alojamentoss deveria ter as seguintes colunas {actual_columns}.', self._log)

        result = {}
        for _, row in df.iterrows():
            accommodation_name_in = row['Alojamento Origem']
            except_type = row['Tipo de Excecao']
            nome_concessionaria = row['Concessionaria']
            accommodations_name_out = row['Alojamentos Destino']
            vet_accommodations = accommodations_name_out.split(';')
            ApplicationException.when(len(vet_accommodations) == 0, f'O alojamento "{accommodation_name_in}" esta com registro de exceção incompativel. [{accommodations_name_out}]', self._log)
            for index in range(len(vet_accommodations)):
                vet_accommodations[index] = vet_accommodations[index].strip()
                ApplicationException.when(
                    any(x for x in self._accommodations.Accommodations if x.nome == vet_accommodations[index]) is False,
                    f'O alojamento "{accommodation_name_in}" esta com registro de exceção incompativel. [{accommodations_name_out}]', self._log)

            result[(accommodation_name_in, nome_concessionaria)] = (except_type, vet_accommodations)

        self._except_list = result

    def _get_config_key(self, key: str) -> str:
        value = self._dict_config.get(key, '')
        ApplicationException.when(value == '', f'Chave não encontrada no arquivo de Accommodations. [key={key}]', self._log)
        return value

    def _get_email_handler(self) -> IEmailHandler:
        self._log.info('Connecting Email...', instant_msg=True)
        email = EmailHandler()

        try:
            self._user = 'robotqd23@gmail.com'
            self._password = 'hgtyrvabzwumkiwu'
            email.login(self._smtp_server, self._user, self._password, use_ssl=True)
        except Exception as error:
            msg = str(error)
            self._log.critical(msg)
            raise ApplicationException('Error connecting email') from error

        return email

    def _get_upload_email_files(self) -> None:
        self._log.info('Downloading PDF files from emails', instant_msg=True)
        email = self._get_email_handler()
        _, all_files = AttachmentDownloader.execute(self._download_folder, self._input_email_folder, self._output_email_folder, self._log, email)
        for file_name in all_files:
            complete_filename = os.path.join(self._download_folder, file_name)
            self._log.info(f'Uploading email file {file_name}', instant_msg=True)
            self._drive.upload_file(local_file_name=complete_filename, file_name=file_name, parents=[self._work_folder_id])
            self._log.info(f'Removing file {file_name}', instant_msg=True)
            os.remove(complete_filename)
        email.logout()
        
        num_files = len(all_files)
        if num_files == 0:
            self._log.info('No files downloaded', instant_msg=True, warn=True)
        elif num_files == 1:
            self._log.info('1 file downloaded', instant_msg=True, warn=True)
        else:
            self._log.info(f'{num_files} files downloaded', instant_msg=True, warn=True)

    def _clean_directories(self):
        self._log.info('Cleaning up directories', instant_msg=True)
        destination_folder = os.path.join(self._download_folder, 'processados')
        list_2_move = [conta.complete_file_name for conta in self._processed_list]
        FilesHandler.move_files(self._log, destination_folder, list_2_move)

        destination_folder = os.path.join(self._download_folder, 'ignorados')
        list_2_move = [conta.complete_file_name for conta in self._ignored_list]
        FilesHandler.move_files(self._log, destination_folder, list_2_move)

        destination_folder = os.path.join(self._download_folder, 'duplicados')
        list_2_move = [conta.complete_file_name for conta in self._duplicated_list]
        FilesHandler.move_files(self._log, destination_folder, list_2_move)

    def _handle_downloaded_files(self, processed_utility_bills) -> None:
        self._log.info('Processing downloaded files', instant_msg=True)
        self._processed_list, self._not_found_list, self._error_list,self._duplicated_list, self._ignored_list = FilesHandler.execute(self._log, self._download_folder, self._accommodations, processed_utility_bills)

    def _process_exceptions(self) -> None:
        self._log.info('Processing the exceptions', instant_msg=True)
        if len(self._processed_list) == 0:
            return

        if len(self._except_list) == 0:
            return

        added_records = []
        for line in self._processed_list:
            conta = line.utility_bill
            exception_data = self._except_list.get((conta.id_alojamento, ServiceProviderEnum(conta.concessionaria).name), '')
            if (exception_data):
                x = self._handle_exceptions(line, exception_data)
                added_records.extend(x)

        self._processed_list.extend(added_records)

    def _upload_files(self) -> None:
        uploader = ResultsUploader(self._log, self._drive)

        self._log.info('Uploading list of processed', instant_msg=True)
        uploader.upload_ok_list(self._folder_client_id, self._folder_contabil_id, self._processed_list)
        self._log.info(f'{len(self._processed_list)} file(s) processed', instant_msg=True)

        self._log.info('Uploading list of unprocessed ', instant_msg=True)
        uploader.upload_other_list(self._others_folder_base_id, self._not_found_list, self._error_list, self._duplicated_list, self._ignored_list)
        self._log.info(f'{len(self._not_found_list)} file(s) without accommodation', instant_msg=True)
        self._log.info(f'{len(self._error_list)} error file(s)', instant_msg=True)
        self._log.info(f'{len(self._duplicated_list)} duplicate file(s)', instant_msg=True)
        self._log.info(f'{len(self._ignored_list)} ignored file(s)', instant_msg=True)

    def _export_results(self, processed_utility_bills: PaidUtilityBillList):
        now = datetime.now()
        export_filename = f'output_{now.strftime("%Y-%m-%d.%H.%M.%S")}.xlsx'
        export_filename = os.path.join(self._export_folder, export_filename)
        database_filename = os.path.join(self._database_folder, 'database.xlsx')

        self._log.info('Saving the worksheets', instant_msg=True)
        saver = ResultsSaver(self._log, self._drive)
        saver.execute(export_filename, database_filename, self._processed_list, self._not_found_list, self._error_list, self._duplicated_list, self._ignored_list, processed_utility_bills.count+1)

        self._log.info('Upload results', instant_msg=True)
        uploader = ResultsUploader(self._log, self._drive)
        uploader.upload_results(self._results_folder_id, export_filename)

    def _handle_exceptions(self, line, exception_data) -> None:
        except_type = exception_data[0]
        accomm_destination_list = exception_data[1]
        parcela = round(line.utility_bill.valor / len(accomm_destination_list), 2)

        ret = []
        if except_type == 1:
            for index in range(len(accomm_destination_list)):
                new_line = copy.deepcopy(line)
                new_line.utility_bill.valor = parcela
                new_line.utility_bill.tipo_documento = DocumentTypeEnum.CONTA_CONSUMO_RATEIO
                new_line.utility_bill.id_alojamento = accomm_destination_list[index]
                ret.append(new_line)
        return ret

    def _get_config_infos_from_accommodation_file(self) -> dict:
        sheet_name = 'Config'
        stream_file = self._drive.get_excel_file(self._accommodation_file_id)
        df_ = pd.read_excel(io.BytesIO(stream_file), sheet_name=sheet_name)
        df = df_.where(pd.notnull(df_), None)
        cols = df.shape[1]
        ApplicationException.when(cols != 3, f'A Sheet "{sheet_name}" da planilha de Alojamentoss deve ter 3 colunas. ', self._log)
        expected_columns = ['Name', 'Value', 'Explanation']
        actual_columns = df.columns.tolist()
        ApplicationException.when(expected_columns != actual_columns, f'A sheet "{sheet_name}" da planilha de Alojamentos deveria ter as seguintes colunas {expected_columns}.', self._log)
        dict = {}
        for _, row in df.iterrows():
            dict[row['Name']] = row['Value']
        return dict

    def _get_and_validate_config(self) -> None:
        def get_and_validate_folder(base_folder, folder_name) -> str:
            ret = os.path.join(base_folder, folder_name)
            ApplicationException.when(not os.path.exists(ret), f'Path does not exist. [{ret}]', self._log)
            return ret

        def validate_folder(parent_id, sec_id, sec_name, name):
            config_folder_id = self._get_config_key(sec_id)
            config_folder_name = self._get_config_key(sec_name)
            folder_id = self._drive.find_file(config_folder_name, parent_id)
            ApplicationException.when(folder_id is None, f'{name} folder not found. [{config_folder_name}]', self._log)
            ApplicationException.when(config_folder_id != folder_id,
                                      f'{name} folder found but its id must be the same as the advisor in "{sec_id}". [{config_folder_id}]', self._log)

            return folder_id

        self._log.info('Getting the settings from the Accommodation worksheet', instant_msg=True)
        self._dict_config = self._get_config_infos_from_accommodation_file()
        self._log.info('Checking the settings', instant_msg=True)

        folder_base_id = self._get_config_key('googledrive.base.folderid')
        if folder_base_id.upper() in ['VAZIO', 'RAIZ']:
            folder_base_id = ''

        self._folder_client_id = validate_folder(folder_base_id, 'googledrive.client.folderid', 'googledrive.client.foldername', 'Client')
        self._folder_contabil_id = validate_folder(folder_base_id, 'googledrive.accounting.folderid', 'googledrive.accounting.foldername', 'Accounting')
        self._others_folder_base_id = validate_folder(folder_base_id, 'googledrive.otherfiles.folderid', 'googledrive.otherfiles.foldername', 'Other files')
        self._results_folder_id = validate_folder(folder_base_id, 'googledrive.results.folderid', 'googledrive.results.foldername', 'Results')
        self._work_folder_id = validate_folder(folder_base_id, 'googledrive.work.folderid', 'googledrive.work.foldername', 'Work')

        # self._base_folder = self._get_config_key('localbase.folder')
        ApplicationException.when(not os.path.exists(self._base_folder), f'Path does not exist. [{self._base_folder}]', self._log)

        self._download_folder = get_and_validate_folder(self._base_folder, 'downloads')
        self._export_folder = get_and_validate_folder(self._base_folder, 'exports')
        self._database_folder = get_and_validate_folder(self._base_folder, 'database')
        ApplicationException.when(not os.path.exists(self._database_folder), f'Path does not exist. [{self._database_folder}]', self._log)

        self._smtp_server = self._get_config_key('gmail.imap.server')
        self._user = self._get_config_key('gmail.user')
        self._password = self._get_config_key('gmail.password')
        self._input_email_folder = self._get_config_key('gmail.reading.folder')
        self._output_email_folder = self._get_config_key('gmail.output.folder')

        self._log.info('Downloading accommodations from the worksheet', instant_msg=True)
        self._get_accommodations()
        self._log.info('Downloading exceptions from the worksheet', instant_msg=True)
        self._get_except_list()

    def _handle_duplicates(self):

        if len(self._processed_list) > 0:
            new_list: List[UtilityBillOkResponse] = []
            for obj in self._processed_list:
                found = False
                for j, _ in enumerate(new_list):
                    if (obj.utility_bill == new_list[j].utility_bill):
                        found = True
                        break
                if (found):
                    obj.error_type = '8'
                    self._duplicated_list.append(obj)
                else:
                    new_list.append(obj)
            self._processed_list = new_list

        if len(self._not_found_list) > 0:
            new_list: List[UtilityBillOkResponse] = []
            for obj in self._not_found_list:
                found = False
                for j, _ in enumerate(new_list):
                    if (obj.utility_bill == new_list[j].utility_bill):
                        found = True
                        break
                if (found):
                    obj.error_type = '8'
                    self._duplicated_list.append(obj)
                else:
                    new_list.append(obj)
            self._not_found_list = new_list

    def _check_residence_change(self) -> None:
        ...

    def _check_missing_utility_bills(self) -> None:
        time.sleep(5)
        self._log.info('Downloading the paid bills from the historical worksheet', instant_msg=True)
        file_name = os.path.join(self._database_folder, 'database.xlsx')
        if os.path.exists(file_name) is False:
            return

        df_ = pd.read_excel(file_name, dtype={'N. Documento / N. Fatura': object})
        df = df_.where(pd.notnull(df_), None)
        maior_data = df.groupby(['Alojamento', 'Concessionaria'])['Data Processamento'].max()

        now = datetime.now()
        for index, value in maior_data.items():
            accomodation, service_provider = index
            if (len(value) > 10):
                value = str(value)[0:10]
            date_obj = datetime.strptime(value, '%Y/%m/%d')
            diferenca = now - date_obj
            if diferenca.days > 30:
                msg = f' o Alojamento {accomodation} recebeu a última conta da {service_provider} há mais de 30 dias (em {value})'
                self._log.info(msg, instant_msg=True, warn=True)

    def execute(self):
        self._log.info('Start of the App.execute routine', instant_msg=True)
        self._get_and_validate_config()

        processed_utility_bills = self._get_processed_utility_bills()
        self._get_upload_email_files()
        
        self._handle_downloaded_files(processed_utility_bills)
        num_files = len(self._processed_list) + len(self._not_found_list) + len(self._error_list) + len(self._duplicated_list) + len(self._ignored_list)
        if num_files == 0:
            self._log.info('No files processed', instant_msg=True, warn=True)
        elif num_files == 1:
            self._log.info('1 file processed', instant_msg=True, warn=True)
        else:
            self._log.info(f'{num_files} files processed', instant_msg=True, warn=True)

        self._handle_duplicates()
        self._process_exceptions()
        self._upload_files()
        self._export_results(processed_utility_bills)
        self._clean_directories()
        self._check_missing_utility_bills()
