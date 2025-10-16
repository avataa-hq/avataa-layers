import database  # noqa
from starlette.middleware.cors import (
    CORSMiddleware,
)
from config.app_config import DEBUG
from config.minio_config import MINIO_BUCKET
from folder_router import router as folder_router
from layers_router import router as layer_router
from init_app import create_app
from services.storage_service.utils import (
    MinioInitializer,
)

app_title = "Layers"
prefix = (
    f"/api/{app_title.replace(' ', '_').lower()}"
)

app = create_app(root_path=prefix)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_version = "1"
v1_options = {
    "root_path": f"{prefix}/v{app_version}",
    "title": app_title,
    "version": app_version,
}
if DEBUG:
    v1_options["debug"] = True

app_v1 = create_app(**v1_options)

app_v1.include_router(folder_router.router)
app_v1.include_router(layer_router.router)

app.mount(v1_options["root_path"], app_v1)


@app.on_event("startup")
def on_startup():
    minio_client = MinioInitializer()
    minio_client = minio_client.get_minio_client()

    if (
        minio_client
        and not minio_client.bucket_exists(
            MINIO_BUCKET
        )
    ):
        minio_client.make_bucket(MINIO_BUCKET)
