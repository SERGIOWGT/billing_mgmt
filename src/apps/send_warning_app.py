
from dataclasses import dataclass
from typing import List
from src.domain.entities.response_error import UtilityBillErrorBaseResponse
from src.infra.repositorios import  PaidBillRepository
import datetime


@dataclass
class SendWarningApp:
    def __init__(self, log, drive, email_sender):
        self._log = log
        self._drive = drive
        self._email_sender = email_sender

    def _make_email(self, list, _to, subject, body, export_file_link: str):
        if len(list) == 0:
            subject += '- SEM REGISTROS'
            body = 'SEM REGISTROS'
        else:
            for indx_warn, reg in enumerate(list):
                body += '\n\n'
                title = reg[0]
                lines = reg[1]
                body += f'{indx_warn+1}) {title} \n'
                for indx, msg in enumerate(lines):
                    body += f'{indx_warn+1}.{indx+1}) {msg} \n'

            if export_file_link:
                body += f'\n\nLink do arquivo de exportação: {export_file_link}'

            body += '\n\nFIM DO RELATÓRIO'

        for email_address in _to.split(','):
            self._email_sender.send('robotqd23@gmail.com', email_address, subject, body)

        return subject, body

    def execute(self, not_found_list:  List[UtilityBillErrorBaseResponse], permission_error: List[str], active_accs: List[str], historic_folder_id: str, exports_file_link: str, email_list: str, days_to_warning: str):
        email_body = []
        if len(not_found_list) > 0:
            email_body.append(('LISTA DE FATURAS SEM ALOJAMENTOS', [f'{self._drive.make_google_link(x.google_file_id)}' for x in not_found_list]))

        self._log.save_message('Getting payments repository....', execution=True)
        paid_repo = PaidBillRepository()
        payments_file_id = self._drive.find_file('database.xlsx', historic_folder_id)
        stream_file = self._drive.get_excel_file(payments_file_id)
        paid_repo.from_excel(stream_file)
        total = paid_repo.number_of_payments()
        self._log.save_message(f'{total} payments(s)', execution=True)

        erro1 = paid_repo.get_last_discontinuous_period(active_accs)
        erro2 = paid_repo.get_possible_faults(days=days_to_warning, active_accommodations=active_accs)
        if (len(permission_error) > 0):
            email_body.append(('ALOJAMENTOS COM PROBLEMAS DE PERMISSIONAMENTO', permission_error))

        if len(erro1) > 0:
            email_body.append(('ALOJAMENTOS COM DESCONTINUIDADE NO RECEBIMENTO DAS CONTAS', erro1))

        if len(erro2) > 0:
            email_body.append((f'ALOJAMENTOS COM CONTAS PENDENTES (EMISSÃO DA CONTA >= {days_to_warning} QUE DIAS CORRIDOS)', erro2))

        data_atual = datetime.date.today()
        hora_atual = datetime.datetime.now().time()
        str_data_atual = data_atual.strftime("%d/%m/%Y")
        str_hora_atual = hora_atual.strftime("%H:%M")

        self._make_email(email_body, email_list, f"[ROBOT] AVISOS DE EXECUCÃO | {str_data_atual} | {str_hora_atual} ", '', exports_file_link)
