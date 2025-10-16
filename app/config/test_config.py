import os

TESTS_RUN_CONTAINER_POSTGRES_LOCAL = (
    os.environ.get(
        "TESTS_RUN_CONTAINER_POSTGRES_LOCAL",
        "True",
    ).upper()
    in ("TRUE", "Y", "YES", "1")
)

TESTS_DB_TYPE = os.environ.get(
    "TESTS_DB_TYPE", "postgresql"
)
TESTS_DB_USER = os.environ.get(
    "TESTS_DB_USER", "postgres"
)
TESTS_DB_PASS = os.environ.get(
    "TESTS_DB_PASS", "1234567890"
)
TESTS_DB_PORT = os.environ.get(
    "TESTS_DB_PORT", "5432"
)
TESTS_DB_NAME = os.environ.get(
    "TESTS_DB_NAME", "layers"
)
TESTS_DB_HOST = os.environ.get(
    "TESTS_DB_HOST", "localhost"
)

TEST_DATABASE_URL = f"{TESTS_DB_TYPE}://{TESTS_DB_USER}:{TESTS_DB_PASS}@{TESTS_DB_HOST}:{TESTS_DB_PORT}/{TESTS_DB_NAME}"

TESTS_MINIO_BUCKET = os.environ.get(
    "TESTS_MINIO_BUCKET", "layerbucket"
)
TESTS_MINIO_USER = os.environ.get(
    "TESTS_MINIO_USER", "minio_secret"
)
TESTS_MINIO_PASSWORD = os.environ.get(
    "TESTS_MINIO_PASSWORD", "minio_secret"
)

TESTS_MINIO_URL = os.environ.get(
    "TESTS_MINIO_URL", "localhost:9000"
)

TESTS_MINIO_SECURE = os.environ.get(
    "TESTS_MINIO_SECURE",
    "False",
).upper() in ("TRUE", "Y", "YES", "1")

TESTS_SECURITY_TYPE = os.environ.get(
    "TESTS_SECURITY_TYPE", "DISABLE"
)
