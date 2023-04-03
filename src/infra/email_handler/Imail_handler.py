from abc import ABC, abstractmethod
import imaplib
from mailbox import Message
from typing import List


class IEmailHandler (ABC):

    @abstractmethod
    def logout(self) -> None:
        ...

    @abstractmethod
    def login(self, host: str, user_name: str, password: str, use_ssl: True) -> None:
        ...

    @abstractmethod
    def get_messages_id(self, folder: str) -> List[int]:
        ...

    @abstractmethod
    def get_email_infos(self, message_uid: int) -> tuple:
        ...

    @abstractmethod
    def fetch_email(self, message_uid: int) -> Message:
        ...

    @abstractmethod
    def get_save_attachments(self, message_uid: int, download_folder: str):
        ...

    @abstractmethod
    def move(self, message_uid: int, destination_folder: str) -> None:
        ...
