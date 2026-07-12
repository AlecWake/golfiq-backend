from app.db.models.golfer_profile import GolferProfile
from app.db.models.user import User


PROFILE_PATH = "/api/v1/users/me/profile"


def register_and_login(client, email="profile@example.com"):
    password = "secure-password-123"
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return (
        {"Authorization": f"Bearer {login_response.json()['access_token']}"},
        register_response.json()["id"],
    )


def test_profile_routes_require_authentication(client):
    assert client.get(PROFILE_PATH).status_code == 401
    assert client.put(PROFILE_PATH, json={"scoring_goal": "Break 90"}).status_code == 401


def test_registration_created_profile_is_returned(client):
    headers, user_id = register_and_login(client)
    response = client.get(PROFILE_PATH, headers=headers)

    assert response.status_code == 200
    assert response.json()["user_id"] == user_id
    assert response.json()["current_handicap_estimate"] is None


def test_profile_response_contains_only_safe_fields_and_timestamps(client):
    headers, _ = register_and_login(client, "safe-profile@example.com")
    data = client.get(PROFILE_PATH, headers=headers).json()

    assert set(data) == {
        "id", "user_id", "current_handicap_estimate", "scoring_goal",
        "dominant_miss", "experience_level", "created_at", "updated_at",
    }
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_update_one_field_preserves_omitted_fields(client):
    headers, _ = register_and_login(client, "partial-profile@example.com")
    client.put(PROFILE_PATH, headers=headers, json={"scoring_goal": "Break 90"})
    response = client.put(
        PROFILE_PATH,
        headers=headers,
        json={"current_handicap_estimate": 18.2},
    )

    assert response.status_code == 200
    assert response.json()["current_handicap_estimate"] == 18.2
    assert response.json()["scoring_goal"] == "Break 90"


def test_update_all_editable_fields(client):
    headers, _ = register_and_login(client, "all-profile@example.com")
    response = client.put(
        PROFILE_PATH,
        headers=headers,
        json={
            "current_handicap_estimate": -10.0,
            "scoring_goal": "  Break 80  ",
            "dominant_miss": "  slice  ",
            "experience_level": "ADVANCED",
        },
    )

    assert response.status_code == 200
    assert response.json()["scoring_goal"] == "Break 80"
    assert response.json()["dominant_miss"] == "slice"
    assert response.json()["experience_level"] == "advanced"


def test_handicap_range_validation(client):
    headers, _ = register_and_login(client, "handicap-profile@example.com")

    assert client.put(PROFILE_PATH, headers=headers, json={"current_handicap_estimate": -10.1}).status_code == 422
    assert client.put(PROFILE_PATH, headers=headers, json={"current_handicap_estimate": 54.1}).status_code == 422
    assert client.put(PROFILE_PATH, headers=headers, json={"current_handicap_estimate": 54.0}).status_code == 200


def test_invalid_experience_level_is_rejected(client):
    headers, _ = register_and_login(client, "level-profile@example.com")
    response = client.put(
        PROFILE_PATH, headers=headers, json={"experience_level": "expert"}
    )
    assert response.status_code == 422


def test_user_id_cannot_be_reassigned(client):
    headers, user_id = register_and_login(client, "ownership-profile@example.com")
    response = client.put(PROFILE_PATH, headers=headers, json={"user_id": user_id + 1})

    assert response.status_code == 422
    assert client.get(PROFILE_PATH, headers=headers).json()["user_id"] == user_id


def test_users_only_access_their_own_profile(client):
    first_headers, first_user_id = register_and_login(client, "first-profile@example.com")
    second_headers, second_user_id = register_and_login(client, "second-profile@example.com")
    client.put(PROFILE_PATH, headers=first_headers, json={"scoring_goal": "First"})

    second_profile = client.get(PROFILE_PATH, headers=second_headers).json()
    assert second_profile["user_id"] == second_user_id
    assert second_profile["user_id"] != first_user_id
    assert second_profile["scoring_goal"] is None


def test_missing_profile_returns_not_found(client, db_session):
    headers, user_id = register_and_login(client, "missing-profile@example.com")
    golfer_profile = db_session.query(GolferProfile).filter(
        GolferProfile.user_id == user_id
    ).one()
    db_session.delete(golfer_profile)
    db_session.commit()

    assert client.get(PROFILE_PATH, headers=headers).status_code == 404
    assert client.put(PROFILE_PATH, headers=headers, json={}).status_code == 404
