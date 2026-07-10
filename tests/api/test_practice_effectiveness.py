def register_and_login(client, email="effectiveness@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Practice",
            "last_name": "Effectiveness",
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
    session_date,
    practice_type="range",
):
    response = client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json={
            "session_date": session_date,
            "practice_type": practice_type,
            "duration_minutes": 45,
            "overall_rating": 8,
        },
    )

    assert response.status_code == 201


def create_round(
    client,
    headers,
    round_date,
    total_score,
    course_name="Effectiveness Course",
):
    response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": round_date,
            "course_name": course_name,
            "holes_played": 18,
            "total_score": total_score,
        },
    )

    assert response.status_code == 201


def test_practice_effectiveness_no_round_data(client):
    headers = register_and_login(client, email="effectiveness-empty@example.com")

    response = client.get(
        "/api/v1/analytics/practice-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_rounds_analyzed": 0,
        "rounds_after_practice": 0,
        "rounds_without_recent_practice": 0,
        "average_score_after_practice": None,
        "average_score_without_recent_practice": None,
        "score_difference": None,
        "practice_appears_helpful": False,
        "confidence_label": "insufficient_data",
        "observation": "Not enough comparison data yet.",
    }


def test_practice_effectiveness_rounds_but_no_practice_sessions(client):
    headers = register_and_login(client, email="effectiveness-rounds-only@example.com")
    create_round(client, headers, "2026-07-01", 88)
    create_round(client, headers, "2026-07-15", 84)

    response = client.get(
        "/api/v1/analytics/practice-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["total_rounds_analyzed"] == 2
    assert response.json()["rounds_after_practice"] == 0
    assert response.json()["rounds_without_recent_practice"] == 2
    assert response.json()["average_score_after_practice"] is None
    assert response.json()["average_score_without_recent_practice"] == 86.0
    assert response.json()["score_difference"] is None
    assert response.json()["practice_appears_helpful"] is False
    assert response.json()["confidence_label"] == "insufficient_data"


def test_practice_effectiveness_both_comparison_groups_present(client):
    headers = register_and_login(client, email="effectiveness-both-groups@example.com")
    create_practice_session(client, headers, "2026-06-20")
    create_round(client, headers, "2026-06-25", 81)
    create_round(client, headers, "2026-07-20", 89)

    response = client.get(
        "/api/v1/analytics/practice-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["total_rounds_analyzed"] == 2
    assert response.json()["rounds_after_practice"] == 1
    assert response.json()["rounds_without_recent_practice"] == 1
    assert response.json()["average_score_after_practice"] == 81.0
    assert response.json()["average_score_without_recent_practice"] == 89.0
    assert response.json()["score_difference"] == -8.0
    assert response.json()["confidence_label"] == "low"


def test_practice_effectiveness_practice_group_better_average_score(client):
    headers = register_and_login(client, email="effectiveness-better@example.com")
    create_practice_session(client, headers, "2026-06-01")
    create_round(client, headers, "2026-06-05", 80)
    create_round(client, headers, "2026-06-10", 82)
    create_round(client, headers, "2026-06-15", 83)
    create_round(client, headers, "2026-07-10", 86)
    create_round(client, headers, "2026-07-15", 88)
    create_round(client, headers, "2026-07-20", 89)

    response = client.get(
        "/api/v1/analytics/practice-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["rounds_after_practice"] == 3
    assert response.json()["rounds_without_recent_practice"] == 3
    assert response.json()["average_score_after_practice"] == 81.67
    assert response.json()["average_score_without_recent_practice"] == 87.67
    assert response.json()["score_difference"] == -6.0
    assert response.json()["practice_appears_helpful"] is True
    assert response.json()["confidence_label"] == "moderate"
    assert response.json()["observation"] == (
        "Rounds following recent practice averaged 6 fewer strokes, but this "
        "does not prove practice caused the improvement."
    )


def test_practice_effectiveness_practice_group_worse_average_score(client):
    headers = register_and_login(client, email="effectiveness-worse@example.com")
    create_practice_session(client, headers, "2026-06-01")
    create_round(client, headers, "2026-06-05", 91)
    create_round(client, headers, "2026-06-10", 92)
    create_round(client, headers, "2026-06-15", 93)
    create_round(client, headers, "2026-07-10", 84)
    create_round(client, headers, "2026-07-15", 85)
    create_round(client, headers, "2026-07-20", 86)

    response = client.get(
        "/api/v1/analytics/practice-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["average_score_after_practice"] == 92.0
    assert response.json()["average_score_without_recent_practice"] == 85.0
    assert response.json()["score_difference"] == 7.0
    assert response.json()["practice_appears_helpful"] is False
    assert response.json()["confidence_label"] == "moderate"
    assert response.json()["observation"] == (
        "No scoring improvement was observed after recent practice in the current data."
    )


def test_practice_effectiveness_custom_lookback_window(client):
    headers = register_and_login(client, email="effectiveness-lookback@example.com")
    create_practice_session(client, headers, "2026-07-01")
    create_round(client, headers, "2026-07-08", 80)
    create_round(client, headers, "2026-07-20", 90)

    default_response = client.get(
        "/api/v1/analytics/practice-effectiveness",
        headers=headers,
    )
    custom_response = client.get(
        "/api/v1/analytics/practice-effectiveness?lookback_days=20",
        headers=headers,
    )

    assert default_response.status_code == 200
    assert default_response.json()["rounds_after_practice"] == 1
    assert default_response.json()["rounds_without_recent_practice"] == 1
    assert custom_response.status_code == 200
    assert custom_response.json()["rounds_after_practice"] == 2
    assert custom_response.json()["rounds_without_recent_practice"] == 0


def test_practice_effectiveness_invalid_lookback_values(client):
    headers = register_and_login(client, email="effectiveness-invalid@example.com")

    low_response = client.get(
        "/api/v1/analytics/practice-effectiveness?lookback_days=0",
        headers=headers,
    )
    high_response = client.get(
        "/api/v1/analytics/practice-effectiveness?lookback_days=91",
        headers=headers,
    )

    assert low_response.status_code == 422
    assert high_response.status_code == 422


def test_practice_effectiveness_isolates_user_ownership(client):
    user_one_headers = register_and_login(client, email="effectiveness-one@example.com")
    user_two_headers = register_and_login(client, email="effectiveness-two@example.com")
    create_practice_session(client, user_one_headers, "2026-07-01")
    create_round(client, user_one_headers, "2026-07-05", 70)
    create_round(client, user_one_headers, "2026-07-20", 100)
    create_practice_session(client, user_two_headers, "2026-07-01")
    create_round(client, user_two_headers, "2026-07-05", 95)
    create_round(client, user_two_headers, "2026-07-20", 85)

    response = client.get(
        "/api/v1/analytics/practice-effectiveness",
        headers=user_two_headers,
    )

    assert response.status_code == 200
    assert response.json()["total_rounds_analyzed"] == 2
    assert response.json()["average_score_after_practice"] == 95.0
    assert response.json()["average_score_without_recent_practice"] == 85.0
    assert response.json()["score_difference"] == 10.0


def test_practice_effectiveness_requires_auth(client):
    response = client.get("/api/v1/analytics/practice-effectiveness")

    assert response.status_code == 401
