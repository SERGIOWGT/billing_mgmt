from dataclasses import dataclass
from datetime import datetime

@dataclass
class RecorringError:
    file_name: str = ''
    date: datetime = datetime.now()
