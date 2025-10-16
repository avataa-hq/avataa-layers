import io
import json

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from config.test_config import (
    TESTS_MINIO_URL,
    TESTS_MINIO_BUCKET,
)
from models import Folder, Layer

URL = "/api/layers/v1/layers"


def generate_geojson_in_memory(default_data=None):
    if default_data is None:
        default_data = {
            "type": "FeatureCollection",
            "features": [],
        }

    geojson_string = json.dumps(default_data)

    file = io.BytesIO()
    file.write(geojson_string.encode())
    file.seek(0)
    file.name = "data.geojson"
    return file


@pytest.fixture(scope="function", autouse=True)
def session_fixture(session):
    layer_default_data = {
        "name": "first_layer",
        "file_link": f"http://{TESTS_MINIO_URL}/{TESTS_MINIO_BUCKET}/data.geojson?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minio_admin_user%2F20241230%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20241230T101336Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=f206e6ac16a73bc87bcd1cc8b362f834a0aea31094f4c947651c59d226b8e607",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    layer = Layer(**layer_default_data)
    session.add(layer)
    session.commit()
    yield session


def test_get_layers(
    session: Session, client: TestClient
):
    response = client.post(
        f"{URL}/create_layer?layer_name=server_link",
        data={
            "server_link": "https://google.com",
            "type": "multipart/form-data",
        },
    )
    assert response.status_code == 200

    response = client.get(f"{URL}/get_layers")
    assert response.status_code == 200

    real_response = response.json()
    for layer in real_response:
        del layer["creation_date"]

    assert real_response == [
        {
            "created_by": "test_client",
            "file_link": f"http://{TESTS_MINIO_URL}/{TESTS_MINIO_BUCKET}/data.geojson?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minio_admin_user%2F20241230%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20241230T101336Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=f206e6ac16a73bc87bcd1cc8b362f834a0aea31094f4c947651c59d226b8e607",
            "folder_id": None,
            "id": 1,
            "modified_by": "test_client",
            "name": "first_layer",
        },
        {
            "created_by": "test_client",
            "file_link": "https://google.com",
            "folder_id": None,
            "id": 2,
            "modified_by": "test_client",
            "name": "server_link",
        },
    ]


def test_get_layers_by_folder_id(
    session: Session, client: TestClient
):
    folder_default_data = {
        "name": "first_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**folder_default_data)
    session.add(folder)
    session.flush()
    session.commit()

    updated_layer = session.get(Layer, ident=1)
    updated_layer.folder_id = folder.id
    session.commit()

    response = client.get(
        f"{URL}/get_layers_by_folder_id/?folder_id={folder.id}"
    )
    assert response.status_code == 200
    real_response = response.json()
    for layer in real_response:
        del layer["creation_date"]

    assert real_response == [
        {
            "created_by": "test_client",
            "file_link": f"http://{TESTS_MINIO_URL}/{TESTS_MINIO_BUCKET}/data.geojson?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minio_admin_user%2F20241230%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20241230T101336Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=f206e6ac16a73bc87bcd1cc8b362f834a0aea31094f4c947651c59d226b8e607",
            "folder_id": 1,
            "id": 1,
            "modified_by": "test_client",
            "name": "first_layer",
        }
    ]


def test_get_layers_by_empty_folder(
    session: Session, client: TestClient
):
    folder_default_data = {
        "name": "first_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**folder_default_data)
    session.add(folder)
    session.flush()
    session.commit()

    response = client.get(
        f"{URL}/get_layers_by_folder_id/?folder_id={folder.id}"
    )
    assert response.status_code == 200

    assert response.json() == []


def test_get_layers_by_not_exists_folder_id(
    session: Session, client: TestClient
):
    response = client.get(
        f"{URL}/get_layers_by_folder_id/?folder_id=1111"
    )
    assert response.status_code == 200
    real_response = response.json()

    assert real_response == []


def test_create_layer(
    session: Session, client: TestClient
):
    file = generate_geojson_in_memory()
    print(file.name)
    response = client.post(
        url=f"{URL}/create_layer?layer_name={file.name}",
        data={
            "filename": "data",
            "type": "multipart/form-data",
        },
        files={"file": file},
    )
    print(response.json())
    assert response.status_code == 200
    real_response = response.json()

    cut_file_link = f"http://{TESTS_MINIO_URL}/{TESTS_MINIO_BUCKET}/data.geojson"
    assert (
        real_response["file_link"].split("?")[0]
        == cut_file_link
    )
    del real_response["creation_date"]
    del real_response["file_link"]

    assert real_response == {
        "id": 2,
        "name": "data.geojson",
        "folder_id": None,
        "created_by": "test_client",
        "modified_by": "test_client",
    }


def test_create_layer_with_duplicated_name(
    session: Session, client: TestClient
):
    file = generate_geojson_in_memory()

    response = client.post(
        f"{URL}/create_layer?layer_name={file.name}",
        data={
            "filename": "data",
            "type": "multipart/form-data",
        },
        files={"file": file},
    )

    assert response.status_code == 200

    file = generate_geojson_in_memory()

    response = client.post(
        f"{URL}/create_layer?layer_name={file.name}",
        data={
            "filename": "data",
            "type": "multipart/form-data",
        },
        files={"file": file},
    )

    assert response.status_code == 422
    real_response = response.json()

    assert real_response == {
        "detail": "Layer with name data.geojson is already exists"
    }


def test_create_layer_in_folder(
    session: Session, client: TestClient
):
    folder_default_data = {
        "name": "first_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**folder_default_data)
    session.add(folder)
    session.flush()
    session.commit()

    file = generate_geojson_in_memory()

    response = client.post(
        url=f"{URL}/create_layer?layer_name={file.name}",
        data={
            "filename": "data",
            "type": "multipart/form-data",
            "folder_id": folder.id,
        },
        files={"file": file},
    )

    assert response.status_code == 200

    real_response = response.json()
    cut_file_link = f"http://{TESTS_MINIO_URL}/{TESTS_MINIO_BUCKET}/data.geojson"

    assert (
        real_response["file_link"].split("?")[0]
        == cut_file_link
    )
    del real_response["creation_date"]
    del real_response["file_link"]

    assert real_response == {
        "created_by": "test_client",
        "folder_id": 1,
        "id": 2,
        "modified_by": "test_client",
        "name": "data.geojson",
    }


def test_create_layer_with_server_url(
    session: Session, client: TestClient
):
    response = client.post(
        f"{URL}/create_layer?layer_name=server_link",
        data={
            "server_link": "https://google.com",
            "type": "multipart/form-data",
        },
    )
    assert response.status_code == 200
    real_response = response.json()
    del real_response["creation_date"]

    assert real_response == {
        "id": 2,
        "name": "server_link",
        "file_link": "https://google.com",
        "folder_id": None,
        "created_by": "test_client",
        "modified_by": "test_client",
    }


def test_create_layer_with_server_url_with_file(
    session: Session, client: TestClient
):
    file = generate_geojson_in_memory()

    response = client.post(
        f"{URL}/create_layer?layer_name=server_link",
        data={
            "server_link": "https://google.com",
            "type": "multipart/form-data",
        },
        files={"file": file},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Both file and server_link cannot be provided simultaneously. "
        "Provide only one."
    }


def test_create_layer_without_server_url_and_without_file(
    session: Session, client: TestClient
):
    response = client.post(
        f"{URL}/create_layer?layer_name=server_link",
        data={
            "type": "multipart/form-data",
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Both file and server_link cannot be None. Provide at least one."
    }


def test_update_layer_change_folder(
    session: Session, client: TestClient
):
    folder_default_data = {
        "name": "first_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**folder_default_data)
    session.add(folder)

    folder_default_data = {
        "name": "second_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**folder_default_data)
    session.add(folder)
    session.flush()
    session.commit()

    file = generate_geojson_in_memory()

    response = client.post(
        url=f"{URL}/create_layer?layer_name={file.name}",
        data={
            "filename": "data",
            "type": "multipart/form-data",
            "folder_id": folder.id,
        },
        files={"file": file},
    )

    assert response.status_code == 200

    response = client.patch(
        url=f"{URL}/update_layer/{1}",
        json={"folder_id": 2},
    )
    assert response.status_code == 200

    real_response = response.json()
    cut_file_link = f"http://{TESTS_MINIO_URL}/{TESTS_MINIO_BUCKET}/data.geojson"

    assert (
        real_response["file_link"].split("?")[0]
        == cut_file_link
    )
    del real_response["creation_date"]
    del real_response["file_link"]

    assert real_response == {
        "created_by": "test_client",
        "folder_id": 2,
        "id": 1,
        "modified_by": "test_client",
        "name": "first_layer",
    }


def test_update_layer_change_folder_to_none(
    session: Session, client: TestClient
):
    folder_default_data = {
        "name": "first_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**folder_default_data)
    session.add(folder)

    folder_default_data = {
        "name": "second_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**folder_default_data)
    session.add(folder)
    session.flush()
    session.commit()

    file = generate_geojson_in_memory()

    response = client.post(
        url=f"{URL}/create_layer?layer_name={file.name}",
        data={
            "filename": "data",
            "type": "multipart/form-data",
            "folder_id": folder.id,
        },
        files={"file": file},
    )

    assert response.status_code == 200

    response = client.patch(
        url=f"{URL}/update_layer/1",
        json={"folder_id": None},
    )
    assert response.status_code == 200

    real_response = response.json()
    cut_file_link = f"http://{TESTS_MINIO_URL}/{TESTS_MINIO_BUCKET}/data.geojson"

    assert (
        real_response["file_link"].split("?")[0]
        == cut_file_link
    )
    del real_response["creation_date"]
    del real_response["file_link"]

    assert real_response == {
        "created_by": "test_client",
        "folder_id": None,
        "id": 1,
        "modified_by": "test_client",
        "name": "first_layer",
    }


def test_update_layer_change_not_exists_folder(
    session: Session, client: TestClient
):
    response = client.patch(
        url=f"{URL}/update_layer/1",
        json={"folder_id": 2},
    )
    assert response.status_code == 422

    real_response = response.json()

    assert real_response == {
        "detail": "Folder with id 2 does not exists"
    }


def test_create_layer_with_not_available_type(
    session: Session, client: TestClient
):
    default_data = {
        "type": "FeatureCollection",
        "features": [],
    }

    geojson_string = json.dumps(default_data)

    file = io.BytesIO()
    file.write(geojson_string.encode())
    file.seek(0)
    file.name = "data.txt"

    response = client.post(
        f"{URL}/create_layer?layer_name={file.name}",
        data={
            "filename": "data",
            "type": "multipart/form-data",
        },
        files={"file": file},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "File content type .txt is not available as geo file"
    }


def test_get_layer_content(
    session: Session, client: TestClient
):
    file = generate_geojson_in_memory()

    response = client.post(
        f"{URL}/create_layer?layer_name={file.name}",
        data={
            "filename": "data",
            "type": "multipart/form-data",
        },
        files={"file": file},
    )
    assert response.status_code == 200

    response = client.get(
        f"{URL}/get_layer_content?layer_id=2"
    )

    assert response.status_code == 200
    real_response = response.json()
    assert real_response == {
        "features": [],
        "type": "FeatureCollection",
    }


def test_get_layer_content_from_server_url(
    session: Session, client: TestClient
):
    response = client.post(
        f"{URL}/create_layer?layer_name=server_link",
        data={
            "server_link": "https://google.com",
            "type": "multipart/form-data",
        },
    )
    assert response.status_code == 200

    response = client.get(
        f"{URL}/get_layer_content?layer_id=2"
    )

    assert response.status_code == 200
    real_response = response.text
    assert real_response == "https://google.com"


def test_get_layer_content_not_exists_layer(
    session: Session, client: TestClient
):
    response = client.get(
        f"{URL}/get_layer_content?layer_id=111"
    )

    assert response.status_code == 422
    real_response = response.json()
    assert real_response == {
        "detail": "Layer with id 111 does not exists"
    }


def test_delete_layer(
    session: Session, client: TestClient
):
    response = client.delete(
        f"{URL}/delete_layer?layer_id=1"
    )
    assert response.status_code == 200

    assert response.json() == {
        "status": "Layer with id 1 was successfully deleted"
    }
    assert not session.get(Folder, ident=1)


def test_delete_not_exists_layer(
    session: Session, client: TestClient
):
    response = client.delete(
        f"{URL}/delete_layer?layer_id=1111"
    )
    assert response.status_code == 422

    assert response.json() == {
        "detail": "Layer with id 1111 does not exists"
    }
