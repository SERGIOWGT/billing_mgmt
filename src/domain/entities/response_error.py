from dataclasses import dataclass
from typing import Optional
from src.domain.entities.base.base_utility_bill import UtilityBillBase

@dataclass
class UtilityBillBaseResponse():
    email_file_id: str = ''
    google_file_id: str = ''
    file_name: str = ''
    
@dataclass
class UtilityBillErrorBaseResponse(UtilityBillBaseResponse):
    error_type: str = ''

@dataclass
class UtilityBillIgnoredResponse(UtilityBillErrorBaseResponse):
    ...

@dataclass
class UtilityBillErrorResponse(UtilityBillErrorBaseResponse):
    utility_bill: Optional[UtilityBillBase] = None

@dataclass
class UtilityBillDuplicatedResponse(UtilityBillErrorResponse):
    original_google_link: str = ''

@dataclass
class UtilityBillOkResponse(UtilityBillBaseResponse):
    utility_bill: Optional[UtilityBillBase] = None
