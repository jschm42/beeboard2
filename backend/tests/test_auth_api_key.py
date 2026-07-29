import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.api_key import ApiKey

def test_api_key_lifecycle(client: TestClient, db: Session):
    # 1. Register a test user and login
    reg_response = client.post("/api/auth/register", json={
        "username": "apikey_tester",
        "email": "keytester@example.com",
        "password": "strongpassword123",
        "first_name": "Key",
        "last_name": "Tester"
    })
    assert reg_response.status_code == 201
    
    login_response = client.post("/api/auth/login", data={
        "username": "apikey_tester",
        "password": "strongpassword123"
    })
    assert login_response.status_code == 200
    token_data = login_response.json()
    token = token_data["access_token"]
    
    # 2. Create an API Key via the API
    headers = {"Authorization": f"Bearer {token}"}
    create_response = client.post("/api/api-keys", json={
        "name": "Test Key",
        "expires_days": 30
    }, headers=headers)
    assert create_response.status_code == 201
    
    res_data = create_response.json()
    assert "raw_key" in res_data
    assert res_data["api_key_info"]["name"] == "Test Key"
    raw_key = res_data["raw_key"]
    key_id = res_data["api_key_info"]["id"]
    
    # 3. List API Keys to verify it's there
    list_response = client.get("/api/api-keys", headers=headers)
    assert list_response.status_code == 200
    keys = list_response.json()
    assert len(keys) >= 1
    assert any(k["id"] == key_id for k in keys)
    
    # 4. Authenticate using the new API Key on a protected route
    me_response = client.get("/api/auth/me", headers={"X-API-Key": raw_key})
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["username"] == "apikey_tester"
    
    # 5. Revoke the API Key
    delete_response = client.delete(f"/api/api-keys/{key_id}", headers=headers)
    assert delete_response.status_code == 204
    
    # 6. Verify the API Key is now invalid
    me_invalid_response = client.get("/api/auth/me", headers={"X-API-Key": raw_key})
    assert me_invalid_response.status_code == 401
