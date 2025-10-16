from sqlmodel import Session

from folder_router.utils import (
    FolderDatabaseGetter,
)
from layers_router.utils import (
    LayerDatabaseGetter,
)
from services.storage_service.utils import (
    MinioInitializer,
)


class Initializer:
    def __init__(self, session: Session):
        self._session = session

        self._layer_db_getter = (
            LayerDatabaseGetter(session=session)
        )
        self._folder_db_getter = (
            FolderDatabaseGetter(session=session)
        )
        self._minio_client = MinioInitializer()
