from dataclasses import dataclass
import os
from typing import Any
from src.conta_consumo_factory import ExtratorContaConsumoFactory
from src.infra.pdf_extractor import PdfExtractor
from src.email_handler import EmailHandler

@dataclass
class App:
    base_folder: str
    downloads_folder = ''
    errors_folder = ''
    processed_folder = ''

    def __init__(self, base_folder: str):
        self.base_folder = base_folder
        self.downloaded_folder = base_folder
        self.processed_folder = self.downloaded_folder + '/processados'
        self.errors_folder = self.downloaded_folder + '/erros'
        self.ignored_folder=self.downloaded_folder + '/ignorados'


    def download_files(self, smtp_server: str, user_name: str, password: str, download_email_folder: str) -> int:
        num_emails = 0
        email = EmailHandler()

        email.login(smtp_server, user_name, password, use_ssl=True)
        messages_id = email.get_messages_id('INBOX')

        for message_uid in messages_id:
            (subject, sender, rec_date, has_attachments) = email.get_email_infos(message_uid)

            if (has_attachments):
                file_list = email.get_save_attachments(message_uid, download_email_folder)

                num_emails += 1
                email.move(message_uid, "PROCESSADOS")
               
                for file_name in file_list:
                    print(f'Downloaded "{file_name}" from "{sender}" titled "{subject}" on {rec_date}.')

        email.logout()
        return num_emails

    def _move_file(self, origin_file_name: str, destination_file_name: str):
        try:
            os.rename(origin_file_name, destination_file_name)
        except:
            pass
            

    def process_downloaded_files(self) -> Any:

        files = [f.upper() for f in os.listdir(self.downloaded_folder) ]
        for file_name in files:


            complete_file_name = os.path.join(self.downloaded_folder, file_name)
            if not file_name.endswith('.PDF'):
                destination = os.path.join(self.ignored_folder, file_name)
                self._move_file(complete_file_name, destination)
                continue


            print(file_name)
            
            all_text = PdfExtractor().get_text(complete_file_name)
            extrator = ExtratorContaConsumoFactory().execute(all_text)
            if (extrator):
                info_conta = extrator.get_info(all_text)

                print('*' * 100)
                print(f'Tipo Servico: {info_conta.tipo_servico.name} Concessionária:  {info_conta.concessionaria.name}')
                print(f'Id Documento: {info_conta.id_documento} Id Cliente: {info_conta.id_cliente} Id Contribuinte: {info_conta.id_contribuinte}')
                print(f'Mes / periodo referencia: {info_conta.periodo_referencia}')
                print(f'Emissao: {info_conta.data_emissao} Vencimento: {info_conta.data_vencimento} Valor: {info_conta.valor}')
                print('*' * 100)
                input('press <ENTER> to continue')
                destination = os.path.join(self.processed_folder, file_name)
                self._move_file(complete_file_name, destination)
            else:
                destination = os.path.join(self.errors_folder, file_name)
                self._move_file(complete_file_name, destination)

        return Any
