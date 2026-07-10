def register_and_login(client, email="timeline@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Timeline",
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
    course_name="Timeline Course",
    total_score=82,
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
    fairways_hit=7,
    fairways_possible=14,
    greens_in_regulation=9,
    putts=30,
):
    client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json={
            "fairways_hit": fairways_hit,
            "fairways_possible": fairways_possible,
            "greens_in_regulation": greens_in_regulation,
            "putts": putts,
            "penalties": 0,
            "up_and_downs": 0,
            "sand_saves": 0,
        },
    )


def create_hole_score(
    client,
    headers,
    round_id,
    hole_number,
    putts=2,
    fairway_hit=True,
    green_in_regulation=True,
):
    client.post(
        f"/api/v1/rounds/{round_id}/hole-scores",
        headers=headers,
        json={
            "hole_number": hole_number,
            "strokes": 4,
            "putts": putts,
            "fairway_hit": fairway_hit,
            "green_in_regulation": green_in_regulation,
            "penalty_strokes": 0,
        },
    )


def create_practice_session(
    client,
    headers,
    session_date="2026-07-05",
    practice_type="range",
):
    client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json={
            "session_date": session_date,
            "practice_type": practice_type,
        },
    )


def test_improvement_timeline_no_rounds(client):
    headers = register_and_login(client, email="timelineempty@example.com")

    response = client.get(
        "/api/v1/analytics/improvement-timeline",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {"timeline": []}


def test_improvement_timeline_single_round(client):
    headers = register_and_login(client, email="timelinesingle@example.com")
    round_id = create_round(
        client,
        headers,
        course_name="Single Course",
        total_score=84,
        round_date="2026-07-01",
    )
    create_round_stats(
        client,
        headers,
        round_id,
        fairways_hit=7,
        fairways_possible=14,
        greens_in_regulation=8,
        putts=32,
    )

    response = client.get(
        "/api/v1/analytics/improvement-timeline",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "timeline": [
            {
                "round_id": round_id,
                "round_date": "2026-07-01",
                "course_name": "Single Course",
                "total_score": 84,
                "average_putts": 1.78,
                "fairway_percentage": 50.0,
                "gir_percentage": 44.44,
                "practice_sessions_since_previous_round": 0,
                "overall_trend_label": "insufficient_data",
            }
        ]
    }


def test_improvement_timeline_multiple_rounds(client):
    headers = register_and_login(client, email="timelinemultiple@example.com")
    first_round_id = create_round(
        client,
        headers,
        course_name="First Course",
        total_score=88,
        round_date="2026-06-01",
    )
    second_round_id = create_round(
        client,
        headers,
        course_name="Second Course",
        total_score=84,
        round_date="2026-06-15",
    )
    third_round_id = create_round(
        client,
        headers,
        course_name="Third Course",
        total_score=84,
        round_date="2026-07-01",
    )
    fourth_round_id = create_round(
        client,
        headers,
        course_name="Fourth Course",
        total_score=90,
        round_date="2026-07-10",
    )
    create_practice_session(client, headers, session_date="2026-05-30")
    create_practice_session(client, headers, session_date="2026-06-10")
    create_practice_session(client, headers, session_date="2026-06-15")
    create_practice_session(client, headers, session_date="2026-06-20")
    create_practice_session(client, headers, session_date="2026-07-10")

    response = client.get(
        "/api/v1/analytics/improvement-timeline",
        headers=headers,
    )

    assert response.status_code == 200
    timeline = response.json()["timeline"]
    assert [entry["round_id"] for entry in timeline] == [
        first_round_id,
        second_round_id,
        third_round_id,
        fourth_round_id,
    ]
    assert [entry["practice_sessions_since_previous_round"] for entry in timeline] == [
        0,
        2,
        1,
        1,
    ]
    assert [entry["overall_trend_label"] for entry in timeline] == [
        "insufficient_data",
        "improving",
        "stable",
        "declining",
    ]


def test_improvement_timeline_missing_statistics(client):
    headers = register_and_login(client, email="timelinemissing@example.com")
    first_round_id = create_round(
        client,
        headers,
        total_score=82,
        holes_played=9,
        round_date="2026-07-01",
    )
    second_round_id = create_round(
        client,
        headers,
        total_score=80,
        round_date="2026-07-08",
    )
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
    )

    response = client.get(
        "/api/v1/analytics/improvement-timeline",
        headers=headers,
    )

    assert response.status_code == 200
    timeline = response.json()["timeline"]
    assert timeline[0]["round_id"] == first_round_id
    assert timeline[0]["average_putts"] == 1.5
    assert timeline[0]["fairway_percentage"] == 50.0
    assert timeline[0]["gir_percentage"] == 50.0
    assert timeline[1]["round_id"] == second_round_id
    assert timeline[1]["average_putts"] is None
    assert timeline[1]["fairway_percentage"] is None
    assert timeline[1]["gir_percentage"] is None


def test_improvement_timeline_isolates_user_ownership(client):
    user_one_headers = register_and_login(client, email="timelineone@example.com")
    user_two_headers = register_and_login(client, email="timelinetwo@example.com")
    create_round(
        client,
        user_one_headers,
        course_name="Private Course",
        total_score=70,
    )
    user_two_round_id = create_round(
        client,
        user_two_headers,
        course_name="Other Course",
        total_score=100,
    )
    create_practice_session(client, user_one_headers)

    response = client.get(
        "/api/v1/analytics/improvement-timeline",
        headers=user_two_headers,
    )

    assert response.status_code == 200
    assert response.json()["timeline"] == [
        {
            "round_id": user_two_round_id,
            "round_date": "2026-07-06",
            "course_name": "Other Course",
            "total_score": 100,
            "average_putts": None,
            "fairway_percentage": None,
            "gir_percentage": None,
            "practice_sessions_since_previous_round": 0,
            "overall_trend_label": "insufficient_data",
        }
    ]


def test_improvement_timeline_requires_auth(client):
    response = client.get("/api/v1/analytics/improvement-timeline")

    assert response.status_code == 401
