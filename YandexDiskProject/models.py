from typing import List

from pydantic import BaseModel
from datetime import datetime
from DBConnection import FileType


class SystemItemImport(BaseModel):
    id: str
    url: str = None
    parent_id: str = None
    type: FileType
    size: int = None


class SystemItemImportRequest(BaseModel):
    items: List[SystemItemImport]
    updateDate: str


class Error:
    def __init__(self, code, message):
        self.code = code
        self.message = message


class SystemItem(BaseModel):
    id: str
    url: str
    date: datetime
    parent_id: str
    type: FileType
    size: int
    children: list
