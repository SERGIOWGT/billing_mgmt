import io
from typing import Any, Optional
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from .Igoogle_drive_handler import IGoogleDriveHandler


class GoogleDriveHandler (IGoogleDriveHandler):
    _SCOPE = 'https://www.googleapis.com/auth/drive'
    _drive = None

    def __init__(self, directory: str):
        credentials_file_path = f'{directory}/credentials.json'
        clientsecret_file_path = f'{directory}/client_secret.json'
        store = file.Storage(credentials_file_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(clientsecret_file_path, self._SCOPE)
            credentials = tools.run_flow(flow, store)

        http = credentials.authorize(Http())
        self._drive = discovery.build('drive', 'v3', http=http)

    def get_file(self, file_id: str):
        request = self.get_service().files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

        return fh.getvalue()

    def get_excel_file(self, file_id: str):
        request = self.get_service().files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

        return fh.getvalue()

    def get_google_sheets_file(self, file_id: str):
        request = self.get_service().files().export_media(fileId=file_id,
                                                          mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

        return fh.getvalue()

    def upload_file(self, local_file_name: str,  file_name: str, parents=[], mimeType='application/pdf'):
        file_metadata = {'name': file_name, 'mimeType': mimeType}
        if len(parents) > 0:
            file_metadata["parents"] = parents

        media = MediaFileUpload(local_file_name, mimetype='*/*', resumable=True)
        return self.get_service().files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

    def update_file(self, file_id, new_filename: str):
        file = self.get_service().files().get(fileId=file_id).execute()
        media_body = MediaFileUpload(new_filename, mimetype=file['mimeType'], resumable=False)
        return self.get_service().files().update(fileId=file_id, media_body=media_body, fields='id, webViewLink').execute()

    def find_file(self, name: str, parent_id: str = '') -> Optional[Any]:
        q = f" name = '{name}' and trashed = false "
        if (parent_id):
            q += f" and '{parent_id}' in parents "

        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = self.get_service().files().list(q=q,
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

        return self.get_service().files().create(body=file_metadata, fields='id, name, parents').execute()

    def get_service(self):
        return self._drive

    def get_files(self, folder_id):
        return self.get_service().files().list(q="'" + folder_id + "' in parents and trashed = false", fields="files(id, name)", orderBy="name", pageSize=1000).execute()

    def copy_file(self, file_id, folder_id, file_name):
        return self.get_service().files().copy(fileId=file_id, body={"parents": [folder_id], 'name': file_name}).execute()

    def delete_file(self, file_id):
        return self.get_service().files().delete(fileId=file_id).execute()


# drive = GoogleDriveHandler('./credentials')
