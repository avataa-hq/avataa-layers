from io import BytesIO

from minio import Minio

from config.minio_config import (
    MINIO_URL,
    MINIO_USER,
    MINIO_PASSWORD,
    MINIO_SECURE,
    MINIO_BUCKET,
)


class MinioInitializer:
    def __init__(
        self,
        minio_url: str = MINIO_URL,
        minio_user: str = MINIO_USER,
        minio_password: str = MINIO_PASSWORD,
        minio_secure: bool = MINIO_SECURE,
    ):
        self._minio_url = minio_url
        self._minio_user = minio_user
        self._minio_password = minio_password
        self._minio_secure = minio_secure

        self._minio_client = (
            self.get_minio_client()
        )

    def get_minio_client(self) -> Minio | None:
        if self._minio_url:
            self._minio_client = Minio(
                self._minio_url,
                self._minio_user,
                self._minio_password,
                secure=self._minio_secure,
            )
            return self._minio_client

        return

    def get_file(
        self,
        filename: str,
        minio_bucket: str = MINIO_BUCKET,
    ) -> str:
        minio_file_link = self._minio_client.presigned_get_object(
            bucket_name=minio_bucket,
            object_name=filename,
        )
        return minio_file_link

    def create_file(
        self,
        filename: str,
        data_buf: BytesIO,
        length: int,
        minio_bucket: str = MINIO_BUCKET,
    ) -> None:
        self._minio_client.put_object(
            bucket_name=minio_bucket,
            object_name=filename,
            data=data_buf,
            length=length,
        )

    def delete_file(
        self,
        filename: str,
        minio_bucket: str = MINIO_BUCKET,
    ) -> None:
        self._minio_client.remove_object(
            bucket_name=minio_bucket,
            object_name=filename,
        )
