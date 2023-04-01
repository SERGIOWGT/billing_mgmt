import io
from typing import Any, Optional
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

class GoogleDriveHandler:
    SCOPE = 'https://www.googleapis.com/auth/drive'

    def __init__ (self, directory: str):
        credentials_file_path = f'{directory}/credentials.json'
        clientsecret_file_path = f'{directory}/credentials/client_secret.json'
        store = file.Storage(credentials_file_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(clientsecret_file_path, self.SCOPE)
            credentials = tools.run_flow(flow, store)

        http = credentials.authorize(Http())
        self.drive = discovery.build('drive', 'v3', http=http)

    def get_excel_file(self, file_id: str):
        request = self.drive.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

        return fh.getvalue() 

    def get_google_sheets_file(self, file_id: str):
        request = self.drive.files().export_media(fileId=file_id, 
                                        mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

        return fh.getvalue()

    def upload_file(self, local_file_name: str,  file_name: str, parent_id: str=''):
        file_metadata = {
            'name': file_name,
            'mimeType': '*/*',
        }
        if (parent_id):
            file_metadata["parents"] = [parent_id]

        media = MediaFileUpload(local_file_name,
                                mimetype='*/*',
                                resumable=True)
        return self.drive.files().create(body=file_metadata, media_body=media, fields='id').execute()

    def find_file(self, name: str, parent_id: str = '') -> Optional[Any]:
        q = f" name = '{name}' "
        if (parent_id):
            q += f" and '{parent_id}' in parents "

        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = self.drive.files().list(q=q,
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name, mimeType)',
                                            pageToken=page_token).execute()
            for file in response.get('files', []):
                return file.get("id")

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        return None

    def create_folder(self, name, parent_id: str = '') -> Any:
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if (parent_id):
            file_metadata["parents"] = [parent_id]

        file = self.drive.files().create(body=file_metadata, fields='id').execute()
        return file


#drive = GoogleDriveHandler('./credentials')
