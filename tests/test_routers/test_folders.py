import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from models import Folder

URL = "/api/layers/v1/folders"


@pytest.fixture(scope="function", autouse=True)
def session_fixture(session):
    folder_default_data = {
        "name": "first_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**folder_default_data)
    session.add(folder)
    session.commit()
    yield session


def test_get_folders(
    session: Session, client: TestClient
):
    """
    This test checks if created Folder is shows
    """
    response = client.get(f"{URL}/get_folders")
    assert response.status_code == 200

    expected_response = [
        {
            "id": 1,
            "name": "first_folder",
            "parent_id": None,
            "created_by": "test_client",
            "modified_by": "test_client",
            "creation_date": "2024-12-18T11:31:30.134493",
            "modification_date": "2024-12-18T11:31:30.134493",
        }
    ]
    assert response.json() == expected_response


def test_get_folders_without_any_folders(
    session: Session, client: TestClient
):
    """
    This test check response if there is no folder
    """
    folder_instance = session.get(Folder, ident=1)
    session.delete(folder_instance)
    session.commit()

    response = client.get(f"{URL}/get_folders")
    assert response.status_code == 200

    expected_response = []
    assert response.json() == expected_response


def test_get_folders_that_has_parents(
    session: Session, client: TestClient
):
    """
    This test check folders with parent and without parents
    """

    child_folder_default_data = {
        "name": "child_folder",
        "created_by": "test_client",
        "parent_id": 1,
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**child_folder_default_data)
    session.add(folder)
    session.commit()

    response = client.get(f"{URL}/get_folders")
    assert response.status_code == 200

    expected_response = [
        {
            "created_by": "test_client",
            "creation_date": "2024-12-18T11:31:30.134493",
            "id": 1,
            "modification_date": "2024-12-18T11:31:30.134493",
            "modified_by": "test_client",
            "name": "first_folder",
            "parent_id": None,
        },
        {
            "created_by": "test_client",
            "creation_date": "2024-12-18T11:31:30.134493",
            "id": 2,
            "modification_date": "2024-12-18T11:31:30.134493",
            "modified_by": "test_client",
            "name": "child_folder",
            "parent_id": 1,
        },
    ]
    assert response.json() == expected_response


def test_create_folder(
    session: Session, client: TestClient
):
    request = {"name": "unique_folder_name"}
    response = client.post(
        f"{URL}/create_folder", json=request
    )
    assert response.status_code == 200

    expected_response = {
        "id": 2,
        "name": "unique_folder_name",
        "parent_id": None,
        "created_by": "test_client",
        "modified_by": "test_client",
    }

    real_response = response.json()
    del real_response["creation_date"]
    del real_response["modification_date"]

    assert real_response == expected_response


def test_create_folder_with_parent(
    session: Session, client: TestClient
):
    request = {
        "name": "unique_folder_name",
        "parent_id": 1,
    }
    response = client.post(
        f"{URL}/create_folder", json=request
    )
    assert response.status_code == 200

    expected_response = {
        "created_by": "test_client",
        "id": 2,
        "modified_by": "test_client",
        "name": "unique_folder_name",
        "parent_id": 1,
    }
    real_response = response.json()
    del real_response["creation_date"]
    del real_response["modification_date"]

    assert real_response == expected_response


def test_create_folder_with_not_exists_parent(
    session: Session, client: TestClient
):
    request = {
        "name": "unique_folder_name",
        "parent_id": 1111,
    }
    response = client.post(
        f"{URL}/create_folder", json=request
    )
    assert response.status_code == 422

    assert response.json() == {
        "detail": "Parent folder with id 1111 does not exist."
    }


def test_create_folder_with_duplicated_name(
    session: Session, client: TestClient
):
    request = {"name": "unique_folder_name"}
    response = client.post(
        f"{URL}/create_folder", json=request
    )
    assert response.status_code == 200

    request = {"name": "unique_folder_name"}
    response = client.post(
        f"{URL}/create_folder", json=request
    )
    assert response.status_code == 422

    assert response.json() == {
        "detail": "Folder with name unique_folder_name already exists."
    }


def test_update_folder_with_duplicated_name(
    session: Session, client: TestClient
):
    request = {"name": "unique_folder_name"}
    response = client.post(
        f"{URL}/create_folder", json=request
    )
    assert response.status_code == 200

    request = {"name": "not_exists_folder_name"}
    not_exists_folder = client.post(
        f"{URL}/create_folder", json=request
    )
    assert not_exists_folder.status_code == 200

    request = {
        "id": not_exists_folder.json()["id"],
        "name": "unique_folder_name",
    }
    response = client.patch(
        f"{URL}/update_folder", json=request
    )
    assert response.status_code == 422

    assert response.json() == {
        "detail": "Folder with name unique_folder_name already exists."
    }


def test_update_folder_parent(
    session: Session, client: TestClient
):
    request = {"name": "unique_folder_name"}
    response = client.post(
        f"{URL}/create_folder", json=request
    )
    assert response.status_code == 200

    request = {
        "name": "not_exists_folder_name",
        "parent_id": response.json()["id"],
    }
    not_exists_folder = client.post(
        f"{URL}/create_folder", json=request
    )
    assert not_exists_folder.status_code == 200

    request = {
        "id": not_exists_folder.json()["id"],
        "parent_id": 1,
    }
    response = client.patch(
        f"{URL}/update_folder", json=request
    )
    assert response.status_code == 200

    expected_result = {
        "created_by": "test_client",
        "id": 3,
        "modified_by": "test_client",
        "name": "not_exists_folder_name",
        "parent_id": 1,
    }

    real_response = response.json()
    del real_response["creation_date"]
    del real_response["modification_date"]
    assert real_response == expected_result


def test_update_folder_name(
    session: Session, client: TestClient
):
    request = {"name": "unique_folder_name"}
    response = client.post(
        f"{URL}/create_folder", json=request
    )
    assert response.status_code == 200

    request = {
        "id": response.json()["id"],
        "name": "updated_folder_name",
    }
    response = client.patch(
        f"{URL}/update_folder", json=request
    )
    assert response.status_code == 200

    expected_result = {
        "created_by": "test_client",
        "id": 2,
        "modified_by": "test_client",
        "name": "updated_folder_name",
        "parent_id": None,
    }

    real_response = response.json()
    del real_response["creation_date"]
    del real_response["modification_date"]
    assert real_response == expected_result


def test_update_folder_not_exists_parent(
    session: Session, client: TestClient
):
    request = {
        "name": "not_exists_folder_name",
    }
    not_exists_folder = client.post(
        f"{URL}/create_folder", json=request
    )
    assert not_exists_folder.status_code == 200

    request = {
        "id": not_exists_folder.json()["id"],
        "parent_id": 1111,
    }
    response = client.patch(
        f"{URL}/update_folder", json=request
    )
    assert response.status_code == 422

    assert response.json() == {
        "detail": "Parent folder with id 1111 does not exist."
    }


def test_delete_folder(
    session: Session, client: TestClient
):
    response = client.delete(
        f"{URL}/delete_folder?folder_id=1"
    )
    assert response.status_code == 200

    assert response.json() == {
        "status": "Folder with id 1 was successfully deleted"
    }
    assert not session.get(Folder, ident=1)


def test_delete_not_exists_folder(
    session: Session, client: TestClient
):
    response = client.delete(
        f"{URL}/delete_folder?folder_id=1111"
    )
    assert response.status_code == 422

    assert response.json() == {
        "detail": "Folder with id 1111 does not exists"
    }


def test_delete_child_folders_while_deleting_parent(
    session: Session, client: TestClient
):
    request = {"name": "parent_folder_name"}
    response = client.post(
        f"{URL}/create_folder", json=request
    )
    assert response.status_code == 200

    request = {
        "name": "child_folder",
        "parent_id": response.json()["id"],
    }
    child_folder = client.post(
        f"{URL}/create_folder", json=request
    )
    assert child_folder.status_code == 200

    response = client.delete(
        f"{URL}/delete_folder?folder_id=2"
    )
    assert response.status_code == 200

    assert not session.get(Folder, 2)
    assert not session.get(Folder, 3)


def test_delete_child_folders_while_and_NOT_deleting_parent(
    session: Session, client: TestClient
):
    request = {"name": "parent_folder_name"}
    response = client.post(
        f"{URL}/create_folder", json=request
    )
    assert response.status_code == 200

    request = {
        "name": "child_folder",
        "parent_id": response.json()["id"],
    }
    child_folder = client.post(
        f"{URL}/create_folder", json=request
    )
    assert child_folder.status_code == 200

    response = client.delete(
        f"{URL}/delete_folder?folder_id=3"
    )
    assert response.status_code == 200

    assert session.get(Folder, 2)
    assert not session.get(Folder, 3)


def test_get_child_folders(
    session: Session, client: TestClient
):
    folder_default_data = {
        "name": "2nd_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
        "parent_id": 1,
    }
    folder_default_data_1 = {
        "name": "3rd_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
        "parent_id": 1,
    }
    folder_default_data_2 = {
        "name": "4th_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**folder_default_data)
    folder_1 = Folder(**folder_default_data_1)
    folder_2 = Folder(**folder_default_data_2)
    session.add(folder)
    session.add(folder_1)
    session.add(folder_2)
    session.commit()

    response = client.get(
        f"{URL}/get_folder_by_parent_folder_id?parent_folder_id=1"
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 2,
            "name": "2nd_folder",
            "parent_id": 1,
            "created_by": "test_client",
            "modified_by": "test_client",
            "creation_date": "2024-12-18T11:31:30.134493",
            "modification_date": "2024-12-18T11:31:30.134493",
        },
        {
            "id": 3,
            "name": "3rd_folder",
            "parent_id": 1,
            "created_by": "test_client",
            "modified_by": "test_client",
            "creation_date": "2024-12-18T11:31:30.134493",
            "modification_date": "2024-12-18T11:31:30.134493",
        },
    ]


def test_get_child_folders_without_parents(
    session: Session, client: TestClient
):
    folder_default_data = {
        "name": "2nd_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
        "parent_id": 1,
    }
    folder_default_data_1 = {
        "name": "3rd_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
        "parent_id": 1,
    }
    folder_default_data_2 = {
        "name": "4th_folder",
        "created_by": "test_client",
        "modified_by": "test_client",
        "creation_date": "2024-12-18 11:31:30.134493",
        "modification_date": "2024-12-18 11:31:30.134493",
    }

    folder = Folder(**folder_default_data)
    folder_1 = Folder(**folder_default_data_1)
    folder_2 = Folder(**folder_default_data_2)
    session.add(folder)
    session.add(folder_1)
    session.add(folder_2)
    session.commit()

    response = client.get(
        f"{URL}/get_folder_by_parent_folder_id"
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "created_by": "test_client",
            "creation_date": "2024-12-18T11:31:30.134493",
            "id": 1,
            "modification_date": "2024-12-18T11:31:30.134493",
            "modified_by": "test_client",
            "name": "first_folder",
            "parent_id": None,
        },
        {
            "created_by": "test_client",
            "creation_date": "2024-12-18T11:31:30.134493",
            "id": 4,
            "modification_date": "2024-12-18T11:31:30.134493",
            "modified_by": "test_client",
            "name": "4th_folder",
            "parent_id": None,
        },
    ]


def test_get_child_folders_with_not_exists_parent(
    session: Session, client: TestClient
):
    response = client.get(
        f"{URL}/get_folder_by_parent_folder_id?parent_folder_id=123123"
    )
    assert response.status_code == 200
    assert response.json() == []
