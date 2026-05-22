from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.ai_assistant import get_effective_model_and_key


def _register_and_login_admin(client: TestClient):
    reg_response = client.post(
        "/api/auth/register",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "strongpassword123",
            "first_name": "Admin",
            "last_name": "User",
        },
    )
    assert reg_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        data={"username": "adminuser", "password": "strongpassword123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_user_crud_and_password_encryption(client: TestClient, db: Session):
    headers = _register_and_login_admin(client)

    create_response = client.post(
        "/api/admin/users",
        json={
            "username": "managed",
            "email": "managed@example.com",
            "password": "managedpassword123",
            "role": "USER",
            "is_active": True,
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    user = db.query(User).filter(User.id == user_id).first()
    assert user is not None
    assert user.hashed_password.startswith("enc::")

    update_response = client.put(
        f"/api/admin/users/{user_id}",
        json={"first_name": "Managed", "role": "SYSTEM_ADMIN"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["role"] == "SYSTEM_ADMIN"

    delete_response = client.delete(f"/api/admin/users/{user_id}", headers=headers)
    assert delete_response.status_code == 204


def test_api_key_db_overrides_env_and_status_visible(client: TestClient, db: Session):
    headers = _register_and_login_admin(client)

    with patch("app.services.system_settings.settings.GEMINI_API_KEY", "env-gemini-key"):
        put_response = client.put(
            "/api/admin/secret-config/api-keys",
            json={"GEMINI_API_KEY": "db-gemini-key"},
            headers=headers,
        )
        assert put_response.status_code == 200

        get_response = client.get("/api/admin/secret-config/api-keys", headers=headers)
        assert get_response.status_code == 200
        gemini_status = get_response.json()["api_keys"]["GEMINI_API_KEY"]
        assert gemini_status["db_configured"] is True
        assert gemini_status["env_configured"] is True
        assert gemini_status["effective_source"] == "db"

        effective_model, key = get_effective_model_and_key("gemini/gemini-2.5-flash", db)
        assert effective_model == "gemini/gemini-2.5-flash"
        assert key == "db-gemini-key"


def test_registration_uses_email_sender_hook(client: TestClient):
    with patch("app.routers.auth.send_registration_email") as send_mail_mock:
        reg_response = client.post(
            "/api/auth/register",
            json={
                "username": "mailtester",
                "email": "mailtester@example.com",
                "password": "strongpassword123",
            },
        )
        assert reg_response.status_code == 201
        send_mail_mock.assert_called_once()


def test_smtp_db_overrides_env_and_clear_credentials(client: TestClient):
    headers = _register_and_login_admin(client)

    with patch("app.services.system_settings.settings.SMTP_HOST", "smtp.env.local"), patch(
        "app.services.system_settings.settings.SMTP_PORT", 2525
    ), patch("app.services.system_settings.settings.SMTP_FROM_EMAIL", "env@example.com"):
        put_response = client.put(
            "/api/admin/secret-config/smtp",
            json={
                "smtp_host": "smtp.db.local",
                "smtp_port": 587,
                "smtp_username": "db-user",
                "smtp_password": "db-pass",
                "smtp_from_email": "db@example.com",
                "smtp_use_tls": True,
                "smtp_use_ssl": False,
            },
            headers=headers,
        )
        assert put_response.status_code == 200
        assert put_response.json()["effective_source"] == "db"
        assert put_response.json()["host"] == "smtp.db.local"
        assert put_response.json()["username_configured"] is True
        assert put_response.json()["password_configured"] is True

        clear_response = client.put(
            "/api/admin/secret-config/smtp",
            json={
                "smtp_username": "",
                "smtp_password": "",
            },
            headers=headers,
        )
        assert clear_response.status_code == 200
        assert clear_response.json()["username_configured"] is False
        assert clear_response.json()["password_configured"] is False
