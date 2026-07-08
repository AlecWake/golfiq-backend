def register_and_login(client, email="recommendations@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Recommendation",
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


def create_round(
    client,
    headers,
    course_name="Recommendation Course",
    total_score=88,
    holes_played=18,
    round_date="2026-07-06",
):
    response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": round_date,
            "course_name": course_name,
            "holes_played": holes_played,
            "total_score": total_score,
        },
    )

    return response.json()["id"]


def create_round_stats(
    client,
    headers,
    round_id,
    fairways_hit=8,
    fairways_possible=14,
    greens_in_regulation=9,
    putts=30,
    penalties=1,
):
    client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json={
            "fairways_hit": fairways_hit,
            "fairways_possible": fairways_possible,
            "greens_in_regulation": greens_in_regulation,
            "putts": putts,
            "penalties": penalties,
            "up_and_downs": 0,
            "sand_saves": 0,
        },
    )


def create_swing_thought(client, headers, title="Smooth tempo"):
    response = client.post(
        "/api/v1/swing-thoughts",
        headers=headers,
        json={
            "title": title,
            "category": "tempo",
        },
    )

    return response.json()["id"]


def categories(response_json):
    return {recommendation["category"] for recommendation in response_json}


def titles(response_json):
    return {recommendation["title"] for recommendation in response_json}


def test_recommendations_for_user_with_no_data(client):
    headers = register_and_login(client, email="recommendations-empty@example.com")

    response = client.get("/api/v1/recommendations", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert categories(response.json()) == {"Practice", "General"}
    assert "Log your first practice session" in titles(response.json())
    assert "Create an active swing thought" in titles(response.json())
    assert "Log a round when you play" in titles(response.json())


def test_recommendations_for_user_with_practice_only(client):
    headers = register_and_login(client, email="recommendations-practice@example.com")
    create_practice_session(client, headers)
    create_swing_thought(client, headers)

    response = client.get("/api/v1/recommendations", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "General"
    assert response.json()[0]["title"] == "Log a round when you play"


def test_recommendations_for_user_with_rounds_only(client):
    headers = register_and_login(client, email="recommendations-rounds@example.com")
    create_round(client, headers)

    response = client.get("/api/v1/recommendations", headers=headers)

    assert response.status_code == 200
    assert "Log your first practice session" in titles(response.json())
    assert "Create an active swing thought" in titles(response.json())


def test_recommendations_use_round_analytics(client):
    headers = register_and_login(client, email="recommendations-analytics@example.com")
    first_round_id = create_round(
        client,
        headers,
        total_score=92,
        round_date="2026-06-01",
    )
    second_round_id = create_round(
        client,
        headers,
        total_score=78,
        round_date="2026-06-20",
    )
    third_round_id = create_round(
        client,
        headers,
        total_score=96,
        round_date="2026-07-06",
    )
    create_round_stats(
        client,
        headers,
        first_round_id,
        fairways_hit=5,
        fairways_possible=14,
        greens_in_regulation=4,
        putts=38,
        penalties=2,
    )
    create_round_stats(
        client,
        headers,
        second_round_id,
        fairways_hit=6,
        fairways_possible=14,
        greens_in_regulation=5,
        putts=37,
        penalties=2,
    )
    create_round_stats(
        client,
        headers,
        third_round_id,
        fairways_hit=4,
        fairways_possible=14,
        greens_in_regulation=3,
        putts=39,
        penalties=3,
    )

    response = client.get("/api/v1/recommendations", headers=headers)

    assert response.status_code == 200
    assert "Prioritize putting practice" in titles(response.json())
    assert "Practice approach shots" in titles(response.json())
    assert "Tighten tee shot accuracy" in titles(response.json())
    assert "Reduce penalty strokes" in titles(response.json())
    assert "Build more consistent scoring" in titles(response.json())


def test_recommendation_generation_includes_required_fields(client):
    headers = register_and_login(client, email="recommendations-fields@example.com")

    response = client.get("/api/v1/recommendations", headers=headers)

    assert response.status_code == 200
    first_recommendation = response.json()[0]
    assert set(first_recommendation) == {
        "recommendation_id",
        "category",
        "priority",
        "title",
        "description",
    }
    assert first_recommendation["recommendation_id"] == "rec-1"
    assert first_recommendation["priority"] in {"low", "medium", "high"}


def test_recommendations_isolate_user_ownership(client):
    user_one_headers = register_and_login(
        client,
        email="recommendations-owner@example.com",
    )
    user_two_headers = register_and_login(
        client,
        email="recommendations-other@example.com",
    )
    round_id = create_round(client, user_one_headers, total_score=99)
    create_round_stats(
        client,
        user_one_headers,
        round_id,
        fairways_hit=2,
        fairways_possible=14,
        greens_in_regulation=1,
        putts=42,
        penalties=5,
    )
    create_practice_session(client, user_two_headers)
    create_swing_thought(client, user_two_headers)

    response = client.get("/api/v1/recommendations", headers=user_two_headers)

    assert response.status_code == 200
    assert response.json() == [
        {
            "recommendation_id": "rec-1",
            "category": "General",
            "priority": "low",
            "title": "Log a round when you play",
            "description": "Rounds help GolfIQ connect your practice habits to on-course results.",
        }
    ]


def test_recommendations_requires_auth(client):
    response = client.get("/api/v1/recommendations")

    assert response.status_code == 401
