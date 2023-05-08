from dataclasses import dataclass
from typing import Optional
from src.domain.entities.base.base_utility_bill import UtilityBillBase

@dataclass
class UtilityBillBaseResponse():
    google_file_id: str = ''
    file_name: str = ''
    complete_file_name: str = ''

@dataclass
class UtilityBillErrorBaseResponse(UtilityBillBaseResponse):
    error_type: str = ''

@dataclass
class UtilityBillIgnoredResponse(UtilityBillErrorBaseResponse):
    error_type: str = ''
    
@dataclass
class UtilityBillOkResponse(UtilityBillBaseResponse):
    utility_bill: Optional[UtilityBillBase] = None

@dataclass
class UtilityBillErrorResponse(UtilityBillErrorBaseResponse):
    utility_bill: Optional[UtilityBillBase] = None

@dataclass
class UtilityBillDuplicatedResponse(UtilityBillErrorResponse):
    original_google_link: str = ''
