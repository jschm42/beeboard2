from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User

def test_auth_registration_and_login(client: TestClient, db: Session):
    # 1. Register a new user
    reg_response = client.post("/api/auth/register", json={
        "username": "tester",
        "email": "tester@example.com",
        "password": "strongpassword123",
        "first_name": "Test",
        "last_name": "User"
    })
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["username"] == "tester"
    assert reg_data["email"] == "tester@example.com"
    # First user registered in the system is promoted to SYSTEM_ADMIN in our router logic!
    assert reg_data["role"] == "SYSTEM_ADMIN"

    # 2. Login via standard form OAuth2
    login_response = client.post("/api/auth/login", data={
        "username": "tester",
        "password": "strongpassword123"
    })
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["user"]["username"] == "tester"

    # 3. Retrieve authenticated user details
    token = token_data["access_token"]
    me_response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["username"] == "tester"
    assert me_data["role"] == "SYSTEM_ADMIN"
