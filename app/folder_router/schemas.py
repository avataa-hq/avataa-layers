from datetime import datetime

from pydantic import BaseModel


class FolderCreateRequest(BaseModel):
    name: str
    parent_id: int | None


class FolderCreateResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_by: str
    modified_by: str
    creation_date: datetime
    modification_date: datetime


class FolderUpdateRequest(BaseModel):
    id: int
    name: str | None
    parent_id: int | None


class FolderUpdateResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_by: str
    modified_by: str
    creation_date: datetime
    modification_date: datetime


class FolderResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_by: str
    modified_by: str
    creation_date: datetime
    modification_date: datetime
