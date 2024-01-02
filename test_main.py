import pytest
from fastapi.testclient import TestClient
from main import app, get_db, ContactCreate

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    db = get_db()
    try:
        yield db
    finally:
        db.close()

def test_create_contact(test_db):
    contact_data = {"first_name": "John", "last_name": "Doe", "email": "john@example.com"}
    response = client.post("/contacts/", json=contact_data)
    assert response.status_code == 200
    created_contact = response.json()
    assert created_contact["first_name"] == "John"

def test_get_all_contacts(test_db):
    response = client.get("/contacts/")
    assert response.status_code == 200
    contacts = response.json()
    assert isinstance(contacts, list)


def test_update_contact(test_db):
    contact_data = {"first_name": "Jane", "last_name": "Doe", "email": "jane@example.com"}
    response_create = client.post("/contacts/", json=contact_data)
    created_contact = response_create.json()
    updated_data = {"first_name": "Jane_updated", "last_name": "Doe_updated", "email": "jane_updated@example.com"}
    response_update = client.put(f"/contacts/{created_contact['id']}", json=updated_data)
    assert response_update.status_code == 200
    updated_contact = response_update.json()
    assert updated_contact["first_name"] == "Jane_updated"
    assert updated_contact["last_name"] == "Doe_updated"


def test_delete_contact(test_db):
    contact_data = {"first_name": "Jim", "last_name": "Doe", "email": "jim@example.com"}
    response_create = client.post("/contacts/", json=contact_data)
    created_contact = response_create.json()
    response_delete = client.delete(f"/contacts/{created_contact['id']}")
    assert response_delete.status_code == 200
    assert response_delete.json() == {"message": "Contact deleted successfully"}
    response_get_deleted_contact = client.get(f"/contacts/{created_contact['id']}")
    assert response_get_deleted_contact.status_code == 404
