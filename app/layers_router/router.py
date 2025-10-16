from typing import List

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    Form,
)
from pydantic import ValidationError
from sqlmodel import Session
from starlette.responses import PlainTextResponse

from database import get_session
from layers_router.exceptions import (
    LayerException,
)
from layers_router.processors import (
    CreateLayer,
    UpdateLayer,
    DeleteLayer,
    GetLayers,
    GetLayersByFolderId,
    GetLayerContent,
)
from layers_router.schemas import (
    LayerUpdateRequest,
    LayerResponse,
    LayerCreateResponse,
    LayerUpdateResponse,
    CreateLayerRequest,
)

router = APIRouter()


@router.get(
    path="/layers/get_layers",
    tags=["Layers"],
    response_model=List[LayerResponse],
)
def get_layers(
    limit: int = None,
    offset: int = None,
    session: Session = Depends(get_session),
):
    task = GetLayers(
        limit=limit,
        offset=offset,
        session=session,
    )
    layers = task.execute()
    return layers


@router.get(
    path="/layers/get_layers_by_folder_id",
    tags=["Layers"],
    response_model=List[LayerResponse],
)
def get_layers_by_folder_id(
    folder_id: int = None,
    limit: int = None,
    offset: int = None,
    session: Session = Depends(get_session),
):
    task = GetLayersByFolderId(
        folder_id=folder_id,
        limit=limit,
        offset=offset,
        session=session,
    )
    try:
        task.check()
        layers = task.execute()
        return layers

    except LayerException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )


@router.post(
    path="/layers/create_layer",
    tags=["Layers"],
    response_model=LayerCreateResponse,
)
async def create_layer(
    layer_name: str,
    server_link: str = Form(default=None),
    folder_id: int = Form(default=None),
    file: UploadFile | None = File(default=None),
    session: Session = Depends(get_session),
):
    try:
        task = CreateLayer(
            session=session,
            layer_name=layer_name,
            folder_id=folder_id,
            file_source=CreateLayerRequest(
                file=file, server_link=server_link
            ),
        )
        task.check()
        new_layer = await task.execute()
        return new_layer

    except LayerException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )
    except ValidationError:
        raise HTTPException(
            status_code=422,
            detail="Server link is not valid",
        )


@router.patch(
    path="/layers/update_layer/{layer_id}",
    tags=["Layers"],
    response_model=LayerUpdateResponse,
)
async def update_layer(
    layer_id: int,
    folder_for_update: LayerUpdateRequest,
    session: Session = Depends(get_session),
):
    task = UpdateLayer(
        folder_id=folder_for_update.folder_id,
        session=session,
        layer_id=layer_id,
    )

    try:
        task.check()
        updated_layer = task.execute()
        return updated_layer

    except LayerException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )


@router.delete(
    path="/layers/delete_layer", tags=["Layers"]
)
async def delete_layer(
    layer_id: int,
    session: Session = Depends(get_session),
):
    task = DeleteLayer(
        session=session, layer_id=layer_id
    )

    try:
        task.check()
        task.execute()
        return {
            "status": f"Layer with id {layer_id} was successfully deleted"
        }

    except LayerException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )


@router.get(
    path="/layers/get_layer_content",
    tags=["Layers"],
    response_class=PlainTextResponse,
)
async def get_layer_content(
    layer_id: int,
    session: Session = Depends(get_session),
):
    task = GetLayerContent(
        session=session, layer_id=layer_id
    )

    try:
        task.check()
        file_content = task.execute()
        return file_content

    except LayerException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )
