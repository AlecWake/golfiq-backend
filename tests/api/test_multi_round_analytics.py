def register_and_login(client, email="multiroundanalytics@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "MultiRoundAnalytics",
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
    course_name="Summary Course",
    total_score=80,
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


def create_hole_score(
    client,
    headers,
    round_id,
    hole_number,
    strokes=4,
    putts=2,
    fairway_hit=True,
    green_in_regulation=True,
    penalty_strokes=0,
):
    client.post(
        f"/api/v1/rounds/{round_id}/hole-scores",
        headers=headers,
        json={
            "hole_number": hole_number,
            "strokes": strokes,
            "putts": putts,
            "fairway_hit": fairway_hit,
            "green_in_regulation": green_in_regulation,
            "penalty_strokes": penalty_strokes,
        },
    )


def test_get_multi_round_analytics_summary(client):
    headers = register_and_login(client)
    first_round_id = create_round(
        client,
        headers,
        course_name="First Summary Course",
        total_score=80,
        round_date="2026-06-01",
    )
    second_round_id = create_round(
        client,
        headers,
        course_name="Second Summary Course",
        total_score=76,
        round_date="2026-06-20",
    )
    third_round_id = create_round(
        client,
        headers,
        course_name="Third Summary Course",
        total_score=90,
        holes_played=9,
        round_date="2026-07-06",
    )
    create_round_stats(
        client,
        headers,
        first_round_id,
        fairways_hit=7,
        fairways_possible=14,
        greens_in_regulation=8,
        putts=30,
        penalties=2,
    )
    create_round_stats(
        client,
        headers,
        second_round_id,
        fairways_hit=10,
        fairways_possible=14,
        greens_in_regulation=11,
        putts=28,
        penalties=0,
    )
    create_hole_score(
        client,
        headers,
        third_round_id,
        hole_number=1,
        putts=1,
        fairway_hit=True,
        green_in_regulation=True,
        penalty_strokes=0,
    )
    create_hole_score(
        client,
        headers,
        third_round_id,
        hole_number=2,
        putts=2,
        fairway_hit=False,
        green_in_regulation=False,
        penalty_strokes=1,
    )

    response = client.get(
        "/api/v1/analytics/rounds/summary",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_rounds": 3,
        "average_score": 82.0,
        "best_score": 76,
        "worst_score": 90,
        "average_putts": 20.33,
        "average_penalties": 1.0,
        "average_fairway_percentage": 57.14,
        "average_gir_percentage": 51.85,
        "total_holes_played": 45,
        "recent_rounds_count": 2,
    }


def test_get_multi_round_analytics_summary_empty(client):
    headers = register_and_login(client, email="emptysummary@example.com")

    response = client.get(
        "/api/v1/analytics/rounds/summary",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_rounds": 0,
        "average_score": 0.0,
        "best_score": None,
        "worst_score": None,
        "average_putts": 0.0,
        "average_penalties": 0.0,
        "average_fairway_percentage": 0.0,
        "average_gir_percentage": 0.0,
        "total_holes_played": 0,
        "recent_rounds_count": 0,
    }


def test_multi_round_analytics_summary_isolates_user_ownership(client):
    user_one_headers = register_and_login(client, email="summaryowner@example.com")
    user_two_headers = register_and_login(client, email="summaryother@example.com")
    create_round(client, user_one_headers, total_score=70)
    create_round(client, user_two_headers, total_score=100)

    response = client.get(
        "/api/v1/analytics/rounds/summary",
        headers=user_two_headers,
    )

    assert response.status_code == 200
    assert response.json()["total_rounds"] == 1
    assert response.json()["average_score"] == 100.0
    assert response.json()["best_score"] == 100
    assert response.json()["worst_score"] == 100


def test_multi_round_analytics_summary_requires_auth(client):
    response = client.get("/api/v1/analytics/rounds/summary")

    assert response.status_code == 401


def test_multi_round_analytics_summary_handles_missing_stats(client):
    headers = register_and_login(client, email="summarymissingstats@example.com")
    first_round_id = create_round(client, headers, total_score=84, holes_played=9)
    create_round(client, headers, total_score=88, holes_played=18)
    create_hole_score(
        client,
        headers,
        first_round_id,
        hole_number=1,
        putts=1,
        fairway_hit=True,
        green_in_regulation=True,
    )
    create_hole_score(
        client,
        headers,
        first_round_id,
        hole_number=2,
        putts=2,
        fairway_hit=False,
        green_in_regulation=False,
        penalty_strokes=1,
    )

    response = client.get(
        "/api/v1/analytics/rounds/summary",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["total_rounds"] == 2
    assert response.json()["average_score"] == 86.0
    assert response.json()["average_putts"] == 3.0
    assert response.json()["average_penalties"] == 1.0
    assert response.json()["average_fairway_percentage"] == 50.0
    assert response.json()["average_gir_percentage"] == 50.0
    assert response.json()["total_holes_played"] == 27
