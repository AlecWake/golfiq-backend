def register_and_login(client, email="correlation@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Correlation",
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


def create_practice_session(
    client,
    headers,
    practice_type="range",
    duration_minutes=45,
    overall_rating=8,
):
    payload = {
        "session_date": "2026-07-06",
        "practice_type": practice_type,
    }

    if duration_minutes is not None:
        payload["duration_minutes"] = duration_minutes
    if overall_rating is not None:
        payload["overall_rating"] = overall_rating

    client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json=payload,
    )


def create_round(
    client,
    headers,
    course_name="Correlation Course",
    total_score=82,
):
    client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": "2026-07-06",
            "course_name": course_name,
            "holes_played": 18,
            "total_score": total_score,
        },
    )


def test_get_practice_round_correlation(client):
    headers = register_and_login(client)
    create_practice_session(
        client,
        headers,
        practice_type="range",
        duration_minutes=60,
        overall_rating=8,
    )
    create_practice_session(
        client,
        headers,
        practice_type="putting",
        duration_minutes=30,
        overall_rating=6,
    )
    create_practice_session(
        client,
        headers,
        practice_type="range",
        duration_minutes=None,
        overall_rating=None,
    )
    create_round(client, headers, course_name="First Course", total_score=82)
    create_round(client, headers, course_name="Second Course", total_score=78)

    response = client.get(
        "/api/v1/analytics/practice-round-correlation",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_practice_sessions": 3,
        "total_rounds": 2,
        "average_practice_rating": 7.0,
        "average_round_score": 80.0,
        "total_practice_minutes": 90,
        "most_common_practice_type": "range",
        "best_round_score": 78,
        "worst_round_score": 82,
        "simple_observation": (
            "You have logged practice and round data. "
            "More advanced correlation will be added later."
        ),
    }


def test_practice_round_correlation_no_data(client):
    headers = register_and_login(client, email="correlationempty@example.com")

    response = client.get(
        "/api/v1/analytics/practice-round-correlation",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_practice_sessions": 0,
        "total_rounds": 0,
        "average_practice_rating": 0.0,
        "average_round_score": 0.0,
        "total_practice_minutes": 0,
        "most_common_practice_type": None,
        "best_round_score": None,
        "worst_round_score": None,
        "simple_observation": "Not enough data yet.",
    }


def test_practice_round_correlation_practice_only(client):
    headers = register_and_login(client, email="correlationpracticeonly@example.com")
    create_practice_session(client, headers, practice_type="short game")

    response = client.get(
        "/api/v1/analytics/practice-round-correlation",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["total_practice_sessions"] == 1
    assert response.json()["total_rounds"] == 0
    assert response.json()["average_round_score"] == 0.0
    assert response.json()["best_round_score"] is None
    assert response.json()["simple_observation"] == "Not enough data yet."


def test_practice_round_correlation_round_only(client):
    headers = register_and_login(client, email="correlationroundonly@example.com")
    create_round(client, headers, total_score=88)

    response = client.get(
        "/api/v1/analytics/practice-round-correlation",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["total_practice_sessions"] == 0
    assert response.json()["total_rounds"] == 1
    assert response.json()["average_round_score"] == 88.0
    assert response.json()["most_common_practice_type"] is None
    assert response.json()["simple_observation"] == "Not enough data yet."


def test_practice_round_correlation_isolates_user_ownership(client):
    user_one_headers = register_and_login(client, email="correlationone@example.com")
    user_two_headers = register_and_login(client, email="correlationtwo@example.com")
    create_practice_session(
        client,
        user_one_headers,
        practice_type="range",
        duration_minutes=90,
        overall_rating=10,
    )
    create_round(client, user_one_headers, total_score=70)
    create_practice_session(
        client,
        user_two_headers,
        practice_type="putting",
        duration_minutes=20,
        overall_rating=5,
    )
    create_round(client, user_two_headers, total_score=100)

    response = client.get(
        "/api/v1/analytics/practice-round-correlation",
        headers=user_two_headers,
    )

    assert response.status_code == 200
    assert response.json()["total_practice_sessions"] == 1
    assert response.json()["total_rounds"] == 1
    assert response.json()["average_practice_rating"] == 5.0
    assert response.json()["average_round_score"] == 100.0
    assert response.json()["total_practice_minutes"] == 20
    assert response.json()["most_common_practice_type"] == "putting"


def test_practice_round_correlation_requires_auth(client):
    response = client.get("/api/v1/analytics/practice-round-correlation")

    assert response.status_code == 401
