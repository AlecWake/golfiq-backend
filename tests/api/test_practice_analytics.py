def register_and_login(client, email="practiceanalytics@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "PracticeAnalytics",
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
    session_date="2026-07-06",
    duration_minutes=45,
    overall_rating=8,
):
    payload = {
        "session_date": session_date,
        "practice_type": practice_type,
    }

    if duration_minutes is not None:
        payload["duration_minutes"] = duration_minutes
    if overall_rating is not None:
        payload["overall_rating"] = overall_rating

    response = client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json=payload,
    )

    return response.json()["id"]


def create_swing_thought(client, headers, title="Smooth tempo", is_active=True):
    response = client.post(
        "/api/v1/swing-thoughts",
        headers=headers,
        json={
            "title": title,
            "category": "tempo",
        },
    )
    swing_thought_id = response.json()["id"]

    if not is_active:
        client.put(
            f"/api/v1/swing-thoughts/{swing_thought_id}",
            headers=headers,
            json={"is_active": False},
        )

    return swing_thought_id


def test_get_practice_analytics_summary(client):
    headers = register_and_login(client)
    first_session_id = create_practice_session(
        client,
        headers,
        practice_type="range",
        session_date="2026-06-01",
        duration_minutes=60,
        overall_rating=7,
    )
    create_practice_session(
        client,
        headers,
        practice_type="putting",
        session_date="2026-06-20",
        duration_minutes=30,
        overall_rating=9,
    )
    create_practice_session(
        client,
        headers,
        practice_type="range",
        session_date="2026-07-06",
        duration_minutes=45,
        overall_rating=8,
    )
    active_swing_thought_id = create_swing_thought(
        client,
        headers,
        title="Stay balanced",
    )
    create_swing_thought(
        client,
        headers,
        title="Archived thought",
        is_active=False,
    )
    client.post(
        (
            f"/api/v1/practice-sessions/{first_session_id}"
            f"/swing-thoughts/{active_swing_thought_id}"
        ),
        headers=headers,
    )

    response = client.get(
        "/api/v1/analytics/practice/summary",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_practice_sessions": 3,
        "total_practice_minutes": 135,
        "average_session_duration": 45.0,
        "average_rating": 8.0,
        "practice_type_counts": {
            "range": 2,
            "putting": 1,
        },
        "most_common_practice_type": "range",
        "recent_sessions_count": 2,
        "active_swing_thoughts_count": 1,
    }


def test_get_practice_analytics_summary_empty(client):
    headers = register_and_login(client, email="emptypracticeanalytics@example.com")
    create_swing_thought(client, headers)

    response = client.get(
        "/api/v1/analytics/practice/summary",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_practice_sessions": 0,
        "total_practice_minutes": 0,
        "average_session_duration": 0.0,
        "average_rating": 0.0,
        "practice_type_counts": {},
        "most_common_practice_type": None,
        "recent_sessions_count": 0,
        "active_swing_thoughts_count": 1,
    }


def test_practice_analytics_summary_isolates_user_ownership(client):
    user_one_headers = register_and_login(
        client,
        email="practiceanalyticsone@example.com",
    )
    user_two_headers = register_and_login(
        client,
        email="practiceanalyticstwo@example.com",
    )
    create_practice_session(
        client,
        user_one_headers,
        practice_type="range",
        duration_minutes=90,
        overall_rating=10,
    )
    create_swing_thought(client, user_one_headers, title="Private thought")
    create_practice_session(
        client,
        user_two_headers,
        practice_type="putting",
        duration_minutes=25,
        overall_rating=6,
    )

    response = client.get(
        "/api/v1/analytics/practice/summary",
        headers=user_two_headers,
    )

    assert response.status_code == 200
    assert response.json()["total_practice_sessions"] == 1
    assert response.json()["total_practice_minutes"] == 25
    assert response.json()["average_rating"] == 6.0
    assert response.json()["practice_type_counts"] == {"putting": 1}
    assert response.json()["active_swing_thoughts_count"] == 0


def test_practice_analytics_summary_requires_auth(client):
    response = client.get("/api/v1/analytics/practice/summary")

    assert response.status_code == 401


def test_practice_analytics_summary_handles_missing_duration_and_rating(client):
    headers = register_and_login(client, email="missingpracticeanalytics@example.com")
    create_practice_session(
        client,
        headers,
        practice_type="range",
        duration_minutes=None,
        overall_rating=None,
    )
    create_practice_session(
        client,
        headers,
        practice_type="putting",
        duration_minutes=30,
        overall_rating=8,
    )
    create_swing_thought(client, headers)

    response = client.get(
        "/api/v1/analytics/practice/summary",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["total_practice_sessions"] == 2
    assert response.json()["total_practice_minutes"] == 30
    assert response.json()["average_session_duration"] == 30.0
    assert response.json()["average_rating"] == 8.0
    assert response.json()["practice_type_counts"] == {
        "range": 1,
        "putting": 1,
    }
    assert response.json()["active_swing_thoughts_count"] == 1
