from datetime import datetime

from fastapi import UploadFile
from pydantic import BaseModel, HttpUrl


class LayerUpdateRequest(BaseModel):
    folder_id: int | None


class LayerUpdateResponse(BaseModel):
    id: int
    name: str
    file_link: str
    folder_id: int | None
    created_by: str
    modified_by: str
    creation_date: datetime


class LayerCreateResponse(BaseModel):
    id: int
    name: str
    file_link: str
    folder_id: int | None
    created_by: str
    modified_by: str
    creation_date: datetime


class LayerResponse(BaseModel):
    id: int
    name: str
    file_link: str
    folder_id: int | None
    created_by: str
    modified_by: str
    creation_date: datetime


class LinkModel(BaseModel):
    server_link: HttpUrl | None = None


class CreateLayerRequest(BaseModel):
    server_link: HttpUrl | None = None
    file: UploadFile | None = None
