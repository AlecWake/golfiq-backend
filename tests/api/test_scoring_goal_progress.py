from app.db.models.golfer_profile import GolferProfile


ENDPOINT = "/api/v1/analytics/scoring-goal-progress"
PROFILE_ENDPOINT = "/api/v1/users/me/profile"


def register_and_login(client, email="goal-progress@example.com"):
    password = "secure-password-123"
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return (
        {"Authorization": f"Bearer {login.json()['access_token']}"},
        registration.json()["id"],
    )


def set_goal(client, headers, scoring_goal):
    response = client.put(
        PROFILE_ENDPOINT,
        headers=headers,
        json={"scoring_goal": scoring_goal},
    )
    assert response.status_code == 200


def create_round(client, headers, round_date, total_score, holes_played=18):
    response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": round_date,
            "course_name": "Goal Test Course",
            "holes_played": holes_played,
            "total_score": total_score,
        },
    )
    assert response.status_code == 201


def test_scoring_goal_progress_requires_authentication(client):
    assert client.get(ENDPOINT).status_code == 401


def test_missing_profile_and_blank_goal_are_safe(client, db_session):
    missing_headers, user_identifier = register_and_login(
        client, "missing-goal-profile@example.com"
    )
    profile = db_session.query(GolferProfile).filter(
        GolferProfile.user_id == user_identifier
    ).one()
    db_session.delete(profile)
    db_session.commit()

    missing_response = client.get(ENDPOINT, headers=missing_headers)
    assert missing_response.status_code == 200
    assert missing_response.json()["goal_status"] == "no_goal"

    blank_headers, _ = register_and_login(client, "blank-goal@example.com")
    blank_response = client.get(ENDPOINT, headers=blank_headers)
    assert blank_response.status_code == 200
    assert blank_response.json()["goal_status"] == "no_goal"
    assert blank_response.json()["observation"] == (
        "Add a scoring goal to your golfer profile to track progress."
    )


def test_unrecognized_goal_returns_valid_response(client):
    headers, _ = register_and_login(client, "unrecognized-goal@example.com")
    set_goal(client, headers, "Play more consistently")

    data = client.get(ENDPOINT, headers=headers).json()

    assert data["goal_status"] == "unrecognized_goal"
    assert data["target_score"] is None
    assert data["observation"] == (
        "Your scoring goal could not be converted into a numeric target."
    )


def test_supported_goal_parsing(client):
    goal_cases = (("Break 100", 99), ("Break 90", 89), ("85", 85))
    for case_number, (scoring_goal, expected_target) in enumerate(goal_cases):
        headers, _ = register_and_login(
            client, f"goal-parser-{case_number}@example.com"
        )
        set_goal(client, headers, scoring_goal)
        data = client.get(ENDPOINT, headers=headers).json()
        assert data["target_score"] == expected_target
        assert data["goal_status"] == "insufficient_data"


def test_no_rounds_has_no_division_by_zero(client):
    headers, _ = register_and_login(client, "no-goal-rounds@example.com")
    set_goal(client, headers, "Shoot under 100")

    data = client.get(ENDPOINT, headers=headers).json()

    assert data["goal_status"] == "insufficient_data"
    assert data["percentage_at_or_below_target"] == 0.0
    assert data["current_average_score"] is None
    assert data["observation"] == (
        "You need more round data before progress can be evaluated."
    )


def test_not_yet_reached_metrics_and_observation(client):
    headers, _ = register_and_login(client, "goal-not-reached@example.com")
    set_goal(client, headers, "Break 90")
    create_round(client, headers, "2026-07-01", 94)
    create_round(client, headers, "2026-07-02", 92)

    data = client.get(ENDPOINT, headers=headers).json()

    assert data["goal_status"] == "not_yet_reached"
    assert data["current_average_score"] == 93.0
    assert data["recent_average_score"] == 93.0
    assert data["best_score"] == 92
    assert data["rounds_at_or_below_target"] == 0
    assert data["strokes_from_goal"] == 4.0
    assert data["trend_label"] == "improving"
    assert data["observation"] == (
        "Your recent average is 4.0 strokes above your target."
    )


def test_occasionally_reached_and_percentage(client):
    headers, _ = register_and_login(client, "goal-occasional@example.com")
    set_goal(client, headers, "Average under 95")
    for day_number, score_value in enumerate((93, 96, 97, 98), start=1):
        create_round(
            client, headers, f"2026-06-{day_number:02d}", score_value
        )

    data = client.get(ENDPOINT, headers=headers).json()

    assert data["goal_status"] == "occasionally_reached"
    assert data["rounds_at_or_below_target"] == 1
    assert data["percentage_at_or_below_target"] == 25.0
    assert data["observation"] == "You have reached your target in 1 of 4 rounds."


def test_consistently_reached_uses_recent_window_deterministically(client):
    headers, _ = register_and_login(client, "goal-consistent@example.com")
    set_goal(client, headers, "Score below 90")
    dated_scores = (
        ("2026-06-01", 100),
        ("2026-06-02", 100),
        ("2026-06-03", 100),
        ("2026-06-04", 89),
        ("2026-06-05", 88),
        ("2026-06-06", 87),
        ("2026-06-07", 95),
        ("2026-06-08", 96),
    )
    for round_date, score_value in dated_scores:
        create_round(client, headers, round_date, score_value)

    data = client.get(ENDPOINT, headers=headers).json()

    assert data["goal_status"] == "consistently_reached"
    assert data["total_rounds"] == 8
    assert data["recent_rounds_considered"] == 5
    assert data["recent_average_score"] == 91.0
    assert data["observation"] == (
        "At least half of your recent rounds have met your target."
    )


def test_rounds_and_profile_are_isolated_by_authenticated_user(client):
    owner_headers, _ = register_and_login(client, "goal-owner@example.com")
    viewer_headers, _ = register_and_login(client, "goal-viewer@example.com")
    set_goal(client, owner_headers, "Break 80")
    set_goal(client, viewer_headers, "Break 100")
    create_round(client, owner_headers, "2026-05-01", 70)
    create_round(client, viewer_headers, "2026-05-01", 105)

    data = client.get(ENDPOINT, headers=viewer_headers).json()

    assert data["scoring_goal"] == "Break 100"
    assert data["total_rounds"] == 1
    assert data["best_score"] == 105
    assert data["rounds_at_or_below_target"] == 0


def test_dominant_hole_format_prevents_mixed_score_comparison(client):
    headers, _ = register_and_login(client, "goal-hole-format@example.com")
    set_goal(client, headers, "Break 90")
    create_round(client, headers, "2026-04-01", 40, holes_played=9)
    create_round(client, headers, "2026-04-02", 42, holes_played=9)
    create_round(client, headers, "2026-04-03", 100, holes_played=18)

    data = client.get(ENDPOINT, headers=headers).json()

    assert data["total_rounds"] == 2
    assert data["current_average_score"] == 41.0
    assert data["best_score"] == 40
    assert data["percentage_at_or_below_target"] == 100.0


def test_equal_format_counts_prefer_eighteen_hole_rounds(client):
    headers, _ = register_and_login(client, "goal-hole-tie@example.com")
    set_goal(client, headers, "Break 90")
    create_round(client, headers, "2026-03-01", 41, holes_played=9)
    create_round(client, headers, "2026-03-02", 95, holes_played=18)

    data = client.get(ENDPOINT, headers=headers).json()

    assert data["total_rounds"] == 1
    assert data["best_score"] == 95
    assert data["goal_status"] == "not_yet_reached"
