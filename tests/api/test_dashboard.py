def register_and_login(client, email="dashboard@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Dashboard",
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


def create_round(
    client,
    headers,
    course_name="Dashboard Course",
    round_date="2026-07-01",
    total_score=88,
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

    return response.json()["id"]


def create_round_stats(client, headers, round_id, putts=30):
    client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json={
            "fairways_hit": 10,
            "fairways_possible": 14,
            "greens_in_regulation": 10,
            "putts": putts,
            "penalties": 0,
            "up_and_downs": 2,
            "sand_saves": 1,
        },
    )


def create_practice_session(
    client,
    headers,
    session_date="2026-07-02",
    overall_rating=8,
):
    payload = {
        "session_date": session_date,
        "practice_type": "range",
    }

    if overall_rating is not None:
        payload["overall_rating"] = overall_rating

    client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json=payload,
    )


def create_club(client, headers, club_name="Driver"):
    client.post(
        "/api/v1/clubs",
        headers=headers,
        json={
            "club_name": club_name,
            "club_type": "wood",
        },
    )


def create_swing_thought(client, headers, title="Smooth tempo"):
    client.post(
        "/api/v1/swing-thoughts",
        headers=headers,
        json={
            "title": title,
            "category": "tempo",
        },
    )


def test_dashboard_summary_with_no_data(client):
    headers = register_and_login(client, email="dashboard-empty@example.com")

    response = client.get("/api/v1/dashboard/summary", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "total_rounds": 0,
        "total_practice_sessions": 0,
        "total_clubs": 0,
        "total_swing_thoughts": 0,
        "most_recent_round_date": None,
        "most_recent_practice_session_date": None,
        "best_score": None,
        "average_score": None,
        "average_putts": None,
        "average_practice_rating": None,
        "total_recommendations": 3,
        "highest_priority_recommendation": {
            "recommendation_id": "rec-1",
            "category": "Practice",
            "priority": "medium",
            "title": "Log your first practice session",
            "description": "You have not logged a practice session yet. Add one after your next range, short game, or putting session.",
        },
    }


def test_dashboard_summary_with_user_data(client):
    headers = register_and_login(client, email="dashboard-data@example.com")
    first_round_id = create_round(
        client,
        headers,
        round_date="2026-06-20",
        total_score=82,
    )
    second_round_id = create_round(
        client,
        headers,
        round_date="2026-07-04",
        total_score=90,
    )
    create_round_stats(client, headers, first_round_id, putts=38)
    create_round_stats(client, headers, second_round_id, putts=40)
    create_practice_session(
        client,
        headers,
        session_date="2026-06-21",
        overall_rating=7,
    )
    create_practice_session(
        client,
        headers,
        session_date="2026-07-05",
        overall_rating=8,
    )
    create_club(client, headers, club_name="Driver")
    create_club(client, headers, club_name="7 Iron")
    create_swing_thought(client, headers)

    response = client.get("/api/v1/dashboard/summary", headers=headers)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_rounds"] == 2
    assert summary["total_practice_sessions"] == 2
    assert summary["total_clubs"] == 2
    assert summary["total_swing_thoughts"] == 1
    assert summary["most_recent_round_date"] == "2026-07-04"
    assert summary["most_recent_practice_session_date"] == "2026-07-05"
    assert summary["best_score"] == 82
    assert summary["average_score"] == 86.0
    assert summary["average_putts"] == 39.0
    assert summary["average_practice_rating"] == 7.5
    assert summary["total_recommendations"] == 1
    assert summary["highest_priority_recommendation"]["priority"] == "high"
    assert (
        summary["highest_priority_recommendation"]["title"]
        == "Prioritize putting practice"
    )


def test_dashboard_summary_isolates_user_ownership(client):
    user_one_headers = register_and_login(
        client,
        email="dashboard-owner@example.com",
    )
    user_two_headers = register_and_login(
        client,
        email="dashboard-other@example.com",
    )
    round_id = create_round(
        client,
        user_one_headers,
        round_date="2026-07-06",
        total_score=72,
    )
    create_round_stats(client, user_one_headers, round_id, putts=25)
    create_practice_session(client, user_one_headers, session_date="2026-07-06")
    create_club(client, user_one_headers)
    create_swing_thought(client, user_one_headers)
    create_practice_session(
        client,
        user_two_headers,
        session_date="2026-07-01",
        overall_rating=6,
    )

    response = client.get("/api/v1/dashboard/summary", headers=user_two_headers)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_rounds"] == 0
    assert summary["total_practice_sessions"] == 1
    assert summary["total_clubs"] == 0
    assert summary["total_swing_thoughts"] == 0
    assert summary["most_recent_round_date"] is None
    assert summary["most_recent_practice_session_date"] == "2026-07-01"
    assert summary["best_score"] is None
    assert summary["average_score"] is None
    assert summary["average_putts"] is None
    assert summary["average_practice_rating"] == 6.0


def test_dashboard_summary_requires_auth(client):
    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 401


def test_dashboard_summary_handles_missing_optional_stats(client):
    headers = register_and_login(client, email="dashboard-missing@example.com")
    create_round(client, headers, total_score=91)
    create_practice_session(client, headers, overall_rating=None)

    response = client.get("/api/v1/dashboard/summary", headers=headers)

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_rounds"] == 1
    assert summary["total_practice_sessions"] == 1
    assert summary["best_score"] == 91
    assert summary["average_score"] == 91.0
    assert summary["average_putts"] is None
    assert summary["average_practice_rating"] is None
