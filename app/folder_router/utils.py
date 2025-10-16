from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Folder


class FolderDatabaseGetter:
    def __init__(self, session: Session):
        self._session = session

    def get_folder_instance_by_name(
        self, folder_name: str
    ) -> Folder | None:
        if folder_name:
            query = select(Folder).where(
                Folder.name == folder_name
            )
            folder_instance = (
                self._session.execute(query)
                .scalars()
                .first()
            )
            return folder_instance

        return None

    def get_folder_instance_by_id(
        self, folder_id: int
    ) -> Folder | None:
        if folder_id:
            query = select(Folder).where(
                Folder.id == folder_id
            )
            folder_instance = (
                self._session.execute(query)
                .scalars()
                .first()
            )
            return folder_instance

        return None

    def get_folder_instance_by_parent_id(
        self, parent_folder_id: int
    ) -> Folder | None:
        """
        if parent_folder_id added to request - response will be: child folder by parent folder id
        if  parent_folder_id does not added to request - response will beL all folders without parents
        """
        query = select(Folder).where(
            Folder.parent_id == parent_folder_id
        )
        folder_instance = (
            self._session.execute(query)
            .scalars()
            .all()
        )
        return folder_instance
