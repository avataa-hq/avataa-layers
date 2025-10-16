import copy
import io
import json

import requests
from sqlalchemy import select
from sqlmodel import Session

from common.initializers import Initializer
from config.minio_config import MINIO_URL
from layers_router.constants import GEO_FILE_TYPES
from layers_router.exceptions import (
    FolderNotExists,
    LayerAlreadyExists,
    LayerDoesNotExists,
    NotAvailableGeoFileType,
)
from layers_router.schemas import (
    CreateLayerRequest,
)
from layers_router.utils import (
    FileAndLinkValidator,
    save_layer_and_return,
)
from models import Layer


class GetLayers:
    def __init__(
        self,
        limit: int | None,
        offset: int | None,
        session: Session,
    ):
        self._limit = limit
        self._offset = offset
        self._session = session

    def execute(self):
        result_objects = self._session.execute(
            select(Layer)
            .limit(limit=self._limit)
            .offset(offset=self._offset)
        )
        return result_objects.scalars().all()


class GetLayersByFolderId(Initializer):
    def __init__(
        self,
        folder_id: int,
        limit: int | None,
        offset: int | None,
        session: Session,
    ):
        super().__init__(session=session)

        self._folder_id = folder_id
        self._limit = limit
        self._offset = offset

    def check(self):
        if self._folder_id:
            folder_instance = self._folder_db_getter.get_folder_instance_by_id(
                folder_id=self._folder_id
            )
            return folder_instance

        return None

    def execute(self):
        return self._layer_db_getter.get_layers_instance_by_folder_id(
            parent_folder_id=self._folder_id
        )


class CreateLayer(Initializer):
    def __init__(
        self,
        layer_name: str,
        folder_id: int | None,
        file_source: CreateLayerRequest,
        session: Session,
    ):
        super().__init__(session=session)

        self._layer_name = layer_name
        self._file_source = file_source
        self._folder_id = folder_id

    async def _create_file(self) -> str:
        file_bytes = (
            await self._file_source.file.read()
        )
        buf = io.BytesIO(file_bytes)

        self._minio_client.create_file(
            filename=self._file_source.file.filename,
            data_buf=buf,
            length=buf.getbuffer().nbytes,
        )

        file_link_in_minio = self._minio_client.get_file(
            filename=self._file_source.file.filename
        )

        return file_link_in_minio

    def _check_folder_exists(self):
        folder_instance = self._folder_db_getter.get_folder_instance_by_id(
            folder_id=self._folder_id
        )

        folder_not_exists_instance = (
            self._folder_id
            and not folder_instance
        )
        if folder_not_exists_instance:
            raise FolderNotExists(
                status_code=422,
                detail=f"Folder with id {self._folder_id} does not exists",
            )

    def _check_layer_already_exists(self):
        layer_instance = self._layer_db_getter.get_layer_instance_by_name(
            layer_name=self._layer_name
        )
        if layer_instance:
            raise LayerAlreadyExists(
                status_code=422,
                detail=f"Layer with name {self._layer_name} is already exists",
            )

    def _check_file_content_type(self):
        if self._file_source.file:
            file_content_type = self._file_source.file.filename.split(
                "."
            )[-1].lower()

            not_available_file_type = (
                file_content_type
                not in GEO_FILE_TYPES
            )
            if not_available_file_type:
                raise NotAvailableGeoFileType(
                    status_code=422,
                    detail=f"File content type .{file_content_type} is not available as geo file",
                )

    def _check_request_instances(self):
        """
        This method validate if file or link uploaded. Because it can't be uploaded link and file
        in one moment, and none of them too
        """
        validator = FileAndLinkValidator(
            file=self._file_source.file,
            server_link=self._file_source.server_link,
        )
        validator.validate()

    def check(self):
        self._check_request_instances()
        self._check_folder_exists()
        self._check_layer_already_exists()
        self._check_file_content_type()

    async def execute(self):
        new_layer = Layer(
            folder_id=self._folder_id,
            name=self._layer_name,
            file_link=await self._create_file()
            if self._file_source.file
            else self._file_source.server_link,
            created_by="test_client",
            modified_by="test_client",
        )

        return save_layer_and_return(
            session=self._session, layer=new_layer
        )


class UpdateLayer(Initializer):
    def __init__(
        self,
        layer_id: int,
        folder_id: int | None,
        session: Session,
    ):
        super().__init__(session=session)
        self._folder_id = folder_id
        self._layer_id = layer_id

    def check(self):
        if self._folder_id:
            folder_instance = self._folder_db_getter.get_folder_instance_by_id(
                folder_id=self._folder_id
            )
            if (
                self._folder_id
                and folder_instance
            ):
                return

            raise FolderNotExists(
                status_code=422,
                detail=f"Folder with id {self._folder_id} does not exists",
            )

    def execute(self):
        layer_instance = self._layer_db_getter.get_layer_instance_by_id(
            layer_id=self._layer_id
        )
        layer_instance.folder_id = self._folder_id

        self._session.add(layer_instance)
        self._session.flush()

        updated_layer = copy.deepcopy(
            layer_instance
        )
        self._session.commit()
        return updated_layer


class DeleteLayer(Initializer):
    def __init__(
        self, layer_id: int, session: Session
    ):
        super().__init__(session=session)
        self._layer_id = layer_id

        self._layer_instance = self._layer_db_getter.get_layer_instance_by_id(
            layer_id=self._layer_id
        )

    def check(self):
        if self._layer_instance:
            return

        raise LayerDoesNotExists(
            status_code=422,
            detail=f"Layer with id {self._layer_id} does not exists",
        )

    def execute(self):
        file_link = self._layer_instance.file_link

        filename = self._layer_instance.name

        file_link_domain = file_link.split("/")[2]

        if file_link_domain == MINIO_URL:
            self._minio_client.delete_file(
                filename=filename
            )

        self._session.delete(
            instance=self._layer_instance
        )
        self._session.commit()


class GetLayerContent(Initializer):
    def __init__(
        self, layer_id: int, session: Session
    ):
        super().__init__(session=session)
        self._layer_id = layer_id

        self._layer_instance = self._layer_db_getter.get_layer_instance_by_id(
            layer_id=self._layer_id
        )

    def check(self):
        if self._layer_instance:
            return

        raise LayerDoesNotExists(
            status_code=422,
            detail=f"Layer with id {self._layer_id} does not exists",
        )

    def execute(self) -> json:
        file_link = self._layer_instance.file_link
        file_link_domain = file_link.split("/")[2]

        if file_link_domain == MINIO_URL:
            response = requests.get(
                url=file_link, timeout=30
            )

            if response.status_code == 200:
                file_content = response.text
                return file_content

        return file_link
