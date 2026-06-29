def register_and_login(client, email="practicesessions@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Practice",
            "last_name": "Tester",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_create_practice_session(client):
    headers = register_and_login(client)

    response = client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json={
            "session_date": "2026-06-28",
            "practice_type": "putting",
            "duration_minutes": 45,
            "notes": "Worked on lag putting.",
            "overall_rating": 8,
        },
    )

    assert response.status_code == 201
    assert response.json()["practice_type"] == "putting"
    assert response.json()["overall_rating"] == 8


def test_list_practice_sessions(client):
    headers = register_and_login(client, email="listpractice@example.com")

    client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json={
            "session_date": "2026-06-28",
            "practice_type": "range",
            "duration_minutes": 60,
        },
    )

    response = client.get("/api/v1/practice-sessions", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["practice_type"] == "range"


def test_get_single_practice_session(client):
    headers = register_and_login(client, email="getpractice@example.com")

    create_response = client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json={
            "session_date": "2026-06-28",
            "practice_type": "chipping",
        },
    )

    practice_session_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/practice-sessions/{practice_session_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["practice_type"] == "chipping"


def test_update_practice_session(client):
    headers = register_and_login(client, email="updatepractice@example.com")

    create_response = client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json={
            "session_date": "2026-06-28",
            "practice_type": "old practice",
        },
    )

    practice_session_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/practice-sessions/{practice_session_id}",
        headers=headers,
        json={
            "practice_type": "approach shots",
            "duration_minutes": 75,
            "overall_rating": 9,
        },
    )

    assert response.status_code == 200
    assert response.json()["practice_type"] == "approach shots"
    assert response.json()["duration_minutes"] == 75
    assert response.json()["overall_rating"] == 9


def test_delete_practice_session(client):
    headers = register_and_login(client, email="deletepractice@example.com")

    create_response = client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json={
            "session_date": "2026-06-28",
            "practice_type": "delete practice",
        },
    )

    practice_session_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/practice-sessions/{practice_session_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/practice-sessions/{practice_session_id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_cannot_access_another_users_practice_session(client):
    user_one_headers = register_and_login(client, email="practiceone@example.com")
    user_two_headers = register_and_login(client, email="practicetwo@example.com")

    create_response = client.post(
        "/api/v1/practice-sessions",
        headers=user_one_headers,
        json={
            "session_date": "2026-06-28",
            "practice_type": "private practice",
        },
    )

    practice_session_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/practice-sessions/{practice_session_id}",
        headers=user_two_headers,
    )

    assert response.status_code == 404


def test_practice_session_routes_require_auth(client):
    response = client.get("/api/v1/practice-sessions")

    assert response.status_code == 401