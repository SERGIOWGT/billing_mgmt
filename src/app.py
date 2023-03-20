import os
import pandas as pd
from typing import Any, List
from dataclasses import dataclass
from src.domain.enums import ConcessionariaEnum, TipoServicoEnum
from src.domain.models.conta_consumo import ContaConsumo
from src.infra.exception_handler import ApplicationException
from src.conta_consumo_factory import ContaConsumoFactory
from src.infra.pdf_extractor import PdfExtractor
from src.email_handler import EmailHandler
from src.domain.entities.alojamentos import PoolAlojamentos

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
        self.ignored_folder = self.downloaded_folder + '/ignorados'

    def _create_df_default(self, list: List[ContaConsumo]) -> Any:
        columns = ['Concessionaria', 'Tipo Servico', 'N. Contrato', 'N. Cliente', 'N. Contribuinte',
                   'Local / Instalacao', 'N. Documento / N. Fatura', 'Periodo Referencia', 'Emissao', 
                   'Vencimento', 'Valor', 'Nome Cliente', 'Arquivo', 'Diretorio', 'Alojamento']

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
            _dict['Emissao'] = line.data_emissao
            _dict['Vencimento'] = line.data_vencimento
            _dict['Valor'] = line.valor
            _dict['Nome Cliente'] = line.nome_cliente
            _dict['Arquivo'] = line.file_name
            _dict['Diretorio'] = line.diretorio
            _dict['Alojamento'] = line.id_alojamento

            df = pd.concat([df, pd.DataFrame.from_records([_dict])])
        return df

    def _create_df_ignored(self, list) -> Any:
        columns = ['Erro', 'Arquivo']
        df = pd.DataFrame(columns=columns)
        for line in list:
            df = df.append({'Erro': line[0], 'Arquivo': line[1]}, ignore_index=True)

        return df

    def _result_2_excel(self, processed_list, error_list, ignored_list):
        df_ok = self._create_df_default(processed_list)
        df_error = self._create_df_default(error_list)
        df_ignored = self._create_df_ignored(ignored_list)

        with pd.ExcelWriter('output.xlsx') as writer:
            df_error.to_excel(writer, sheet_name='Erros', index=False)
            df_ignored.to_excel(writer, sheet_name='Ignorados', index=False)
            df_ok.to_excel(writer, sheet_name='Processados', index=False)

    def _move_file(self, file_name, destination, log):
        try:
            os.rename(file_name, destination)
        except Exception as error:
            ApplicationException.when(True, str(error), log)

    def _conta_consumo_2_log(self, info_conta, log):
        log.info(f'==> Concessionária/Tipo Servico: {info_conta.concessionaria.name} / {info_conta.tipo_servico.name} ')
        log.info(f'==> Id Documento: {info_conta.id_documento}')
        log.info(f'==> Id Cliente: {info_conta.id_cliente}')
        log.info(f'==> Id Contribuinte: {info_conta.id_contribuinte}')
        log.info(f'==> Id Contrato: {info_conta.id_contrato}')
        log.info(f'==> Mes / periodo referencia: {info_conta.periodo_referencia}')
        log.info(f'==> Emissao/Vencimento: {info_conta.data_emissao} / {info_conta.data_vencimento}')
        log.info(f'==> Valor: {info_conta.valor}')
        log.info(info_conta.__dict__)

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

    def _list_pdf(self):
        return [f.upper() for f in os.listdir(self.downloaded_folder) if os.path.isfile(os.path.join(self.downloaded_folder, f)) and f.endswith('.PDF') == True]

    def process_downloaded_files(self, log, alojamentos: PoolAlojamentos) -> Any:
        processed_list = []
        ignored_list = []
        error_list = []
        files = self._list_pdf()
        for file_name in files:
            complete_file_name = os.path.join(self.downloaded_folder, file_name)
            log.info(f'Processing file: {complete_file_name}')
            all_text = PdfExtractor().get_text(complete_file_name)
            conta_consumo = ContaConsumoFactory().execute(all_text, file_name)
            if (conta_consumo):
                try:
                    conta_consumo.create(all_text)
                    
                    alojamento = alojamentos.get_alojamento(conta_consumo.id_cliente, conta_consumo.id_contrato, conta_consumo.local_consumo)
                    if (alojamento):
                        conta_consumo.id_alojamento = alojamento.nome
                        conta_consumo.diretorio = alojamento.diretorio
                        
                    processed_list.append(conta_consumo)

                        
                    # self._conta_consumo_2_log(info_conta, log)

                except Exception:
                    error_list.append(conta_consumo)
                    # self._conta_consumo_2_log(info_conta, log)

                # destination = os.path.join(self.processed_folder, file_name)
            else:
                msg = f'Arquivo não reconhecido ou fora do formato {complete_file_name}'
                log.info(msg)
                ignored_list.append((file_name, msg))
                # destination = os.path.join(self.errors_folder, file_name)

            # self._move_file(complete_file_name, destination, log)

        if (len(files)):
            self._result_2_excel(processed_list, error_list, ignored_list)

        return Any
