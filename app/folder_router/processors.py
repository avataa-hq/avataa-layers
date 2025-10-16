import copy
import datetime

from sqlalchemy import select
from sqlmodel import Session

from common.initializers import Initializer
from folder_router.exceptions import (
    FolderAlreadyExists,
    ParentNotExists,
    FolderNotExists,
)
from folder_router.schemas import (
    FolderCreateRequest,
    FolderUpdateRequest,
)
from models import Folder


class GetFolders:
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
            select(Folder)
            .limit(limit=self._limit)
            .offset(offset=self._offset)
        )
        return result_objects.scalars().all()


class CreateFolder(Initializer):
    def __init__(
        self,
        request: FolderCreateRequest,
        session: Session,
    ):
        super().__init__(session=session)
        self._folder_to_create = request
        self._folder_instance = None

    def check(self):
        folder_exists = self._folder_db_getter.get_folder_instance_by_name(
            folder_name=self._folder_to_create.name
        )

        if folder_exists:
            raise FolderAlreadyExists(
                status_code=422,
                detail=f"Folder with name {self._folder_to_create.name} already exists.",
            )

        parent_folder_instance = self._folder_db_getter.get_folder_instance_by_id(
            folder_id=self._folder_to_create.parent_id
        )

        parent_not_exists = (
            self._folder_to_create.parent_id
            and not parent_folder_instance
        )

        if parent_not_exists:
            raise ParentNotExists(
                status_code=422,
                detail=f"Parent folder with id {self._folder_to_create.parent_id} does not exist.",
            )

    def execute(self):
        folder_with_user = (
            self._folder_to_create.dict(
                exclude_none=True
            )
        )
        folder_with_user["created_by"] = (
            "test_client"
        )
        folder_with_user["modified_by"] = (
            "test_client"
        )

        new_folder = Folder(**folder_with_user)

        self._session.add(new_folder)
        self._session.flush()
        new_folder = copy.deepcopy(new_folder)
        self._session.commit()

        return new_folder


class UpdateFolder(Initializer):
    def __init__(
        self,
        request: FolderUpdateRequest,
        session: Session,
    ):
        super().__init__(session=session)
        self._folder_to_update = request

    @staticmethod
    def _add_user(new_folder: dict) -> dict:
        folder_with_user = dict(new_folder)
        folder_with_user["created_by"] = (
            "test_client"
        )
        folder_with_user["modified_by"] = (
            "test_client"
        )
        return folder_with_user

    def check(self) -> None:
        if self._folder_db_getter.get_folder_instance_by_name(
            folder_name=self._folder_to_update.name
        ):
            raise FolderAlreadyExists(
                status_code=422,
                detail=f"Folder with name {self._folder_to_update.name} already exists.",
            )

        parent_folder_instance = self._folder_db_getter.get_folder_instance_by_id(
            folder_id=self._folder_to_update.parent_id
        )

        parent_not_exists = (
            self._folder_to_update.parent_id
            and not parent_folder_instance
        )

        if parent_not_exists:
            raise ParentNotExists(
                status_code=422,
                detail=f"Parent folder with id {self._folder_to_update.parent_id} does not exist.",
            )

        return

    def execute(self):
        folder_instance = self._folder_db_getter.get_folder_instance_by_id(
            self._folder_to_update.id
        )

        for (
            attribute,
            new_value,
        ) in self._folder_to_update.dict(
            exclude_unset=True
        ).items():
            setattr(
                folder_instance,
                attribute,
                new_value,
            )

        folder_instance.modification_date = (
            datetime.datetime.now()
        )

        self._session.add(folder_instance)
        self._session.flush()
        updated_folder = copy.deepcopy(
            folder_instance
        )
        self._session.commit()

        return updated_folder


class DeleteFolder(Initializer):
    def __init__(
        self, folder_id: int, session: Session
    ):
        super().__init__(session=session)
        self._folder_id = folder_id

        self._folder_instance = self._folder_db_getter.get_folder_instance_by_id(
            folder_id=self._folder_id
        )

    def check(self):
        if self._folder_instance:
            return

        raise FolderNotExists(
            status_code=422,
            detail=f"Folder with id {self._folder_id} does not exists",
        )

    def execute(self):
        self._session.delete(
            self._folder_instance
        )
        self._session.commit()


class GetFolderByParentFolderId(Initializer):
    def __init__(
        self,
        parent_folder_id: int | None,
        limit: int | None,
        offset: int | None,
        session: Session,
    ):
        super().__init__(session=session)

        self._parent_folder_id = parent_folder_id
        self._limit = limit
        self._offset = offset

    def check(self):
        if self._parent_folder_id:
            folder_instance = self._folder_db_getter.get_folder_instance_by_id(
                folder_id=self._parent_folder_id
            )

            folder_not_exists_instance = (
                self._parent_folder_id
                and not folder_instance
            )

            if folder_not_exists_instance:
                raise FolderNotExists(
                    status_code=422,
                    detail=f"Folder with id {self._parent_folder_id} does not exists",
                )
            return folder_instance

        return None

    def execute(self):
        return self._folder_db_getter.get_folder_instance_by_parent_id(
            parent_folder_id=self._parent_folder_id
        )
