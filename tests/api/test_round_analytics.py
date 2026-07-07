def register_and_login(client, email="roundanalytics@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "RoundAnalytics",
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


def create_round(client, headers, course_name="Analytics Course", total_score=73):
    response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": "2026-07-06",
            "course_name": course_name,
            "holes_played": 18,
            "total_score": total_score,
        },
    )

    return response.json()["id"]


def create_round_stats(client, headers, round_id):
    client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json={
            "fairways_hit": 8,
            "fairways_possible": 14,
            "greens_in_regulation": 10,
            "putts": 30,
            "penalties": 1,
            "up_and_downs": 4,
            "sand_saves": 1,
        },
    )


def create_hole_score(
    client,
    headers,
    round_id,
    hole_number,
    strokes,
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


def test_get_round_analytics_summary(client):
    headers = register_and_login(client)
    round_id = create_round(client, headers)
    create_round_stats(client, headers, round_id)
    create_hole_score(client, headers, round_id, hole_number=1, strokes=3)
    create_hole_score(client, headers, round_id, hole_number=2, strokes=4)
    create_hole_score(client, headers, round_id, hole_number=3, strokes=5)
    create_hole_score(client, headers, round_id, hole_number=4, strokes=6)

    response = client.get(
        f"/api/v1/rounds/{round_id}/analytics",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "round_id": round_id,
        "total_score": 73,
        "holes_played": 18,
        "fairways_hit": 8,
        "fairways_possible": 14,
        "fairway_percentage": 57.14,
        "greens_in_regulation": 10,
        "gir_percentage": 55.56,
        "total_putts": 30,
        "penalty_strokes": 1,
        "average_score_per_hole": 4.06,
        "birdies": 1,
        "pars": 1,
        "bogeys": 1,
        "double_bogeys_or_worse": 1,
    }


def test_cannot_access_another_users_round_analytics(client):
    user_one_headers = register_and_login(client, email="analyticsowner@example.com")
    user_two_headers = register_and_login(client, email="analyticsother@example.com")
    round_id = create_round(
        client,
        user_one_headers,
        course_name="Private Analytics",
    )

    response = client.get(
        f"/api/v1/rounds/{round_id}/analytics",
        headers=user_two_headers,
    )

    assert response.status_code == 404


def test_round_analytics_requires_auth(client):
    response = client.get("/api/v1/rounds/1/analytics")

    assert response.status_code == 401


def test_round_analytics_handles_missing_statistics(client):
    headers = register_and_login(client, email="missingstats@example.com")
    round_id = create_round(client, headers, total_score=80)
    create_hole_score(
        client,
        headers,
        round_id,
        hole_number=1,
        strokes=4,
        putts=1,
        fairway_hit=True,
        green_in_regulation=True,
        penalty_strokes=0,
    )
    create_hole_score(
        client,
        headers,
        round_id,
        hole_number=2,
        strokes=5,
        putts=2,
        fairway_hit=False,
        green_in_regulation=False,
        penalty_strokes=1,
    )

    response = client.get(
        f"/api/v1/rounds/{round_id}/analytics",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["fairways_hit"] == 1
    assert response.json()["fairways_possible"] == 2
    assert response.json()["fairway_percentage"] == 50.0
    assert response.json()["greens_in_regulation"] == 1
    assert response.json()["total_putts"] == 3
    assert response.json()["penalty_strokes"] == 1


def test_round_analytics_handles_missing_hole_scores(client):
    headers = register_and_login(client, email="missingholescores@example.com")
    round_id = create_round(client, headers, total_score=90)
    create_round_stats(client, headers, round_id)

    response = client.get(
        f"/api/v1/rounds/{round_id}/analytics",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["fairways_hit"] == 8
    assert response.json()["fairways_possible"] == 14
    assert response.json()["birdies"] == 0
    assert response.json()["pars"] == 0
    assert response.json()["bogeys"] == 0
    assert response.json()["double_bogeys_or_worse"] == 0
