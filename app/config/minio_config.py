import os

MINIO_URL = os.environ.get(
    "MINIO_URL", "minio:9000"
)
MINIO_USER = os.environ.get(
    "MINIO_USER", "layers"
)
MINIO_PASSWORD = os.environ.get(
    "MINIO_PASSWORD", ""
)
MINIO_BUCKET = os.environ.get(
    "MINIO_BUCKET", "layers"
)
MINIO_SECURE = os.environ.get(
    "MINIO_SECURE", "False"
).upper() in ("TRUE", "Y", "YES", "1")
