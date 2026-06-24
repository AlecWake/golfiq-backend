from app.db.models.golfer_profile import GolferProfile
from app.db.models.user import User


def test_register_user_creates_user_and_profile(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "register@example.com",
            "password": "secure-password-123",
            "first_name": "Register",
            "last_name": "User",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "register@example.com"
    assert data["first_name"] == "Register"
    assert data["last_name"] == "User"
    assert data["role"] == "golfer"
    assert "password" not in data
    assert "password_hash" not in data

    user = db_session.query(User).filter(User.email == "register@example.com").first()
    assert user is not None
    assert user.password_hash != "secure-password-123"

    profile = db_session.query(GolferProfile).filter(
        GolferProfile.user_id == user.id
    ).first()
    assert profile is not None


def test_register_user_rejects_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "secure-password-123",
        "first_name": "Duplicate",
        "last_name": "User",
    }

    first_response = client.post("/api/v1/auth/register", json=payload)
    second_response = client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409

def test_login_user_with_valid_credentials(client):
    payload = {
        "email": "login@example.com",
        "password": "secure-password-123",
        "first_name": "Login",
        "last_name": "User",
    }

    client.post("/api/v1/auth/register", json=payload)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "secure-password-123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Login successful."
    assert data["user"]["email"] == "login@example.com"
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_login_user_with_wrong_password_fails(client):
    payload = {
        "email": "wrongpassword@example.com",
        "password": "secure-password-123",
        "first_name": "Wrong",
        "last_name": "Password",
    }

    client.post("/api/v1/auth/register", json=payload)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpassword@example.com",
            "password": "bad-password",
        },
    )

    assert response.status_code == 401


def test_login_user_with_unknown_email_fails(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing@example.com",
            "password": "secure-password-123",
        },
    )

    assert response.status_code == 401