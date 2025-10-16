import copy
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from layers_router.exceptions import (
    FileOrLinkNotUploaded,
    FileAndLinkUploaded,
)
from layers_router.schemas import LinkModel
from models import Layer


class LayerDatabaseGetter:
    def __init__(self, session: Session):
        self._session = session

    def get_layer_instance_by_name(
        self, layer_name: str
    ) -> Layer | None:
        if layer_name:
            query = select(Layer).where(
                Layer.name == layer_name
            )
            layer_instance = (
                self._session.execute(query)
                .scalars()
                .first()
            )
            return layer_instance

        return None

    def get_layer_instance_by_id(
        self, layer_id: int
    ) -> Layer | None:
        if layer_id:
            query = select(Layer).where(
                Layer.id == layer_id
            )
            layer_instance = (
                self._session.execute(query)
                .scalars()
                .first()
            )
            return layer_instance

        return None

    def get_layers_instance_by_folder_id(
        self, parent_folder_id: int
    ) -> List[Layer] | None:
        """
        if parent_folder_id added to request - response will be: child layers by parent folder id
        if  parent_folder_id does not added to request - response will beL all layers without folders
        """
        query = select(Layer).where(
            Layer.folder_id == parent_folder_id
        )
        layer_instance = (
            self._session.execute(query)
            .scalars()
            .all()
        )
        return layer_instance


class FileAndLinkValidator:
    def __init__(
        self,
        file: Optional[UploadFile],
        server_link: Optional[LinkModel],
    ):
        self.file = file
        self.server_link = server_link

    def validate(self):
        if not self.file and not self.server_link:
            raise FileOrLinkNotUploaded(
                status_code=422,
                detail="Both file and server_link cannot be None. Provide at least one.",
            )

        if self.file and self.server_link:
            raise FileAndLinkUploaded(
                status_code=422,
                detail="Both file and server_link cannot be provided simultaneously. Provide only one.",
            )


def save_layer_and_return(
    session: Session, layer: Layer
):
    session.add(layer)
    session.flush()
    new_layer = copy.deepcopy(layer)
    session.commit()

    return new_layer
