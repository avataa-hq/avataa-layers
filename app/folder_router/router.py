from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlmodel import Session

from database import get_session
from folder_router.exceptions import (
    FolderException,
)
from folder_router.processors import (
    CreateFolder,
    UpdateFolder,
    GetFolders,
    DeleteFolder,
    GetFolderByParentFolderId,
)
from folder_router.schemas import (
    FolderCreateRequest,
    FolderCreateResponse,
    FolderUpdateRequest,
    FolderUpdateResponse,
    FolderResponse,
)

router = APIRouter()


@router.get(
    path="/folders/get_folders",
    tags=["Folder"],
    response_model=List[FolderResponse],
)
def get_folders(
    limit: int = None,
    offset: int = None,
    session: Session = Depends(get_session),
):
    task = GetFolders(
        limit=limit,
        offset=offset,
        session=session,
    )
    folders = task.execute()
    return folders


@router.get(
    path="/folders/get_folder_by_parent_folder_id",
    tags=["Folder"],
    response_model=List[FolderResponse],
)
def get_folder_by_parent_folder_id(
    parent_folder_id: int = None,
    limit: int = None,
    offset: int = None,
    session: Session = Depends(get_session),
):
    task = GetFolderByParentFolderId(
        limit=limit,
        offset=offset,
        session=session,
        parent_folder_id=parent_folder_id,
    )
    folders = task.execute()
    return folders


@router.post(
    path="/folders/create_folder",
    tags=["Folder"],
    response_model=FolderCreateResponse,
)
def create_folder(
    folder_create_request: FolderCreateRequest,
    session: Session = Depends(get_session),
):
    try:
        task = CreateFolder(
            request=folder_create_request,
            session=session,
        )

        task.check()
        new_folder = task.execute()
        return new_folder

    except FolderException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )


@router.patch(
    path="/folders/update_folder",
    tags=["Folder"],
    response_model=FolderUpdateResponse,
)
def update_folder(
    folder_update_request: FolderUpdateRequest,
    session: Session = Depends(get_session),
):
    try:
        task = UpdateFolder(
            request=folder_update_request,
            session=session,
        )

        task.check()
        new_folder = task.execute()
        return new_folder

    except FolderException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )


@router.delete(
    path="/folders/delete_folder", tags=["Folder"]
)
def delete_folder(
    folder_id: int,
    session: Session = Depends(get_session),
):
    try:
        task = DeleteFolder(
            folder_id=folder_id, session=session
        )

        task.check()
        task.execute()
        return {
            "status": f"Folder with id {folder_id} was successfully deleted"
        }

    except FolderException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )
