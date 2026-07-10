def register_and_login(client, email="thoughtanalytics@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Thought",
            "last_name": "Analytics",
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


def create_swing_thought(client, headers, title="Smooth tempo", category="tempo"):
    response = client.post(
        "/api/v1/swing-thoughts",
        headers=headers,
        json={
            "title": title,
            "category": category,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_practice_session(client, headers, session_date):
    response = client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json={
            "session_date": session_date,
            "practice_type": "range",
            "duration_minutes": 45,
            "overall_rating": 8,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_round(client, headers, round_date, total_score, course_name="Analytics Course"):
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

    return response.json()["id"]


def link_swing_thought(client, headers, practice_session_id, swing_thought_id):
    response = client.post(
        (
            f"/api/v1/practice-sessions/{practice_session_id}"
            f"/swing-thoughts/{swing_thought_id}"
        ),
        headers=headers,
    )

    assert response.status_code == 201


def test_swing_thought_effectiveness_requires_auth(client):
    response = client.get("/api/v1/analytics/swing-thought-effectiveness")

    assert response.status_code == 401


def test_swing_thought_effectiveness_no_swing_thoughts(client):
    headers = register_and_login(client, email="thoughtanalytics-empty@example.com")

    response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_swing_thought_effectiveness_no_linked_practice_sessions(client):
    headers = register_and_login(client, email="thoughtanalytics-no-links@example.com")
    swing_thought_id = create_swing_thought(client, headers, title="Quiet hands")

    response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "swing_thought_id": swing_thought_id,
            "title": "Quiet hands",
            "category": "tempo",
            "linked_practice_sessions": 0,
            "associated_rounds": 0,
            "average_associated_round_score": None,
            "best_associated_round_score": None,
            "worst_associated_round_score": None,
            "effectiveness_label": "insufficient_data",
            "confidence_label": "insufficient_data",
            "observation": "Not enough associated round data yet.",
        }
    ]


def test_swing_thought_effectiveness_linked_session_no_associated_rounds(client):
    headers = register_and_login(client, email="thoughtanalytics-no-rounds@example.com")
    swing_thought_id = create_swing_thought(client, headers, title="Full turn")
    practice_session_id = create_practice_session(client, headers, "2026-07-01")
    link_swing_thought(client, headers, practice_session_id, swing_thought_id)
    create_round(client, headers, "2026-06-30", 88)
    create_round(client, headers, "2026-08-15", 84)

    response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    result = response.json()[0]
    assert result["linked_practice_sessions"] == 1
    assert result["associated_rounds"] == 0
    assert result["effectiveness_label"] == "insufficient_data"
    assert result["confidence_label"] == "insufficient_data"


def test_swing_thought_effectiveness_insufficient_data_result(client):
    headers = register_and_login(client, email="thoughtanalytics-insufficient@example.com")
    swing_thought_id = create_swing_thought(client, headers)
    practice_session_id = create_practice_session(client, headers, "2026-07-01")
    link_swing_thought(client, headers, practice_session_id, swing_thought_id)
    create_round(client, headers, "2026-07-05", 82)
    create_round(client, headers, "2026-08-10", 90)

    response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    result = response.json()[0]
    assert result["associated_rounds"] == 1
    assert result["average_associated_round_score"] == 82.0
    assert result["best_associated_round_score"] == 82
    assert result["worst_associated_round_score"] == 82
    assert result["effectiveness_label"] == "insufficient_data"
    assert result["confidence_label"] == "insufficient_data"


def test_swing_thought_effectiveness_promising_result(client):
    headers = register_and_login(client, email="thoughtanalytics-promising@example.com")
    swing_thought_id = create_swing_thought(client, headers, title="Balanced finish")
    practice_session_id = create_practice_session(client, headers, "2026-07-01")
    link_swing_thought(client, headers, practice_session_id, swing_thought_id)
    create_round(client, headers, "2026-07-05", 80)
    create_round(client, headers, "2026-07-12", 82)
    create_round(client, headers, "2026-08-10", 92)
    create_round(client, headers, "2026-08-20", 94)

    response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    result = response.json()[0]
    assert result["swing_thought_id"] == swing_thought_id
    assert result["associated_rounds"] == 2
    assert result["average_associated_round_score"] == 81.0
    assert result["best_associated_round_score"] == 80
    assert result["worst_associated_round_score"] == 82
    assert result["effectiveness_label"] == "promising"
    assert result["confidence_label"] == "low"
    assert result["observation"] == (
        "Rounds associated with this swing thought averaged 6 strokes lower "
        "than your overall average. This is an association and does not prove "
        "causation."
    )


def test_swing_thought_effectiveness_neutral_result(client):
    headers = register_and_login(client, email="thoughtanalytics-neutral@example.com")
    swing_thought_id = create_swing_thought(client, headers, title="Soft grip")
    practice_session_id = create_practice_session(client, headers, "2026-07-01")
    link_swing_thought(client, headers, practice_session_id, swing_thought_id)
    create_round(client, headers, "2026-07-05", 84)
    create_round(client, headers, "2026-07-12", 86)
    create_round(client, headers, "2026-08-10", 85)
    create_round(client, headers, "2026-08-20", 85)

    response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    result = response.json()[0]
    assert result["average_associated_round_score"] == 85.0
    assert result["effectiveness_label"] == "neutral"
    assert result["confidence_label"] == "low"
    assert result["observation"] == (
        "Rounds associated with this swing thought were similar to your "
        "overall scoring average."
    )


def test_swing_thought_effectiveness_struggling_result(client):
    headers = register_and_login(client, email="thoughtanalytics-struggling@example.com")
    swing_thought_id = create_swing_thought(client, headers, title="Fast hips")
    practice_session_id = create_practice_session(client, headers, "2026-07-01")
    link_swing_thought(client, headers, practice_session_id, swing_thought_id)
    create_round(client, headers, "2026-07-05", 92)
    create_round(client, headers, "2026-07-12", 94)
    create_round(client, headers, "2026-08-10", 80)
    create_round(client, headers, "2026-08-20", 82)

    response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    result = response.json()[0]
    assert result["average_associated_round_score"] == 93.0
    assert result["effectiveness_label"] == "struggling"
    assert result["confidence_label"] == "low"
    assert result["observation"] == (
        "Rounds associated with this swing thought averaged higher than your "
        "overall average. This is an association and does not prove causation."
    )


def test_swing_thought_effectiveness_custom_lookback_window(client):
    headers = register_and_login(client, email="thoughtanalytics-lookback@example.com")
    swing_thought_id = create_swing_thought(client, headers)
    practice_session_id = create_practice_session(client, headers, "2026-07-01")
    link_swing_thought(client, headers, practice_session_id, swing_thought_id)
    create_round(client, headers, "2026-07-12", 80)
    create_round(client, headers, "2026-07-20", 82)
    create_round(client, headers, "2026-08-15", 90)

    default_response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=headers,
    )
    custom_response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness?lookback_days=10",
        headers=headers,
    )

    assert default_response.status_code == 200
    assert default_response.json()[0]["associated_rounds"] == 2
    assert custom_response.status_code == 200
    assert custom_response.json()[0]["associated_rounds"] == 0


def test_swing_thought_effectiveness_invalid_lookback_values(client):
    headers = register_and_login(client, email="thoughtanalytics-invalid@example.com")

    low_response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness?lookback_days=0",
        headers=headers,
    )
    high_response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness?lookback_days=366",
        headers=headers,
    )

    assert low_response.status_code == 422
    assert high_response.status_code == 422


def test_swing_thought_effectiveness_prevents_duplicate_rounds(client):
    headers = register_and_login(client, email="thoughtanalytics-duplicates@example.com")
    swing_thought_id = create_swing_thought(client, headers)
    first_practice_session_id = create_practice_session(client, headers, "2026-07-01")
    second_practice_session_id = create_practice_session(client, headers, "2026-07-10")
    link_swing_thought(client, headers, first_practice_session_id, swing_thought_id)
    link_swing_thought(client, headers, second_practice_session_id, swing_thought_id)
    create_round(client, headers, "2026-07-15", 80)
    create_round(client, headers, "2026-07-20", 82)
    create_round(client, headers, "2026-08-20", 92)

    response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    result = response.json()[0]
    assert result["linked_practice_sessions"] == 2
    assert result["associated_rounds"] == 2
    assert result["average_associated_round_score"] == 81.0


def test_swing_thought_effectiveness_isolates_user_ownership(client):
    user_one_headers = register_and_login(client, email="thoughtanalytics-one@example.com")
    user_two_headers = register_and_login(client, email="thoughtanalytics-two@example.com")
    user_one_swing_thought_id = create_swing_thought(
        client,
        user_one_headers,
        title="Private one",
    )
    user_two_swing_thought_id = create_swing_thought(
        client,
        user_two_headers,
        title="Private two",
    )
    user_one_practice_session_id = create_practice_session(
        client,
        user_one_headers,
        "2026-07-01",
    )
    user_two_practice_session_id = create_practice_session(
        client,
        user_two_headers,
        "2026-07-01",
    )
    link_swing_thought(
        client,
        user_one_headers,
        user_one_practice_session_id,
        user_one_swing_thought_id,
    )
    link_swing_thought(
        client,
        user_two_headers,
        user_two_practice_session_id,
        user_two_swing_thought_id,
    )
    create_round(client, user_one_headers, "2026-07-05", 70)
    create_round(client, user_one_headers, "2026-08-10", 100)
    create_round(client, user_two_headers, "2026-07-05", 95)
    create_round(client, user_two_headers, "2026-08-10", 85)

    response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=user_two_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["swing_thought_id"] == user_two_swing_thought_id
    assert response.json()[0]["title"] == "Private two"
    assert response.json()[0]["average_associated_round_score"] == 95.0


def test_swing_thought_effectiveness_deterministic_result_ordering(client):
    headers = register_and_login(client, email="thoughtanalytics-ordering@example.com")
    zeta_swing_thought_id = create_swing_thought(client, headers, title="Zeta")
    alpha_swing_thought_id = create_swing_thought(client, headers, title="Alpha")
    beta_swing_thought_id = create_swing_thought(client, headers, title="Beta")
    zeta_practice_session_id = create_practice_session(client, headers, "2026-07-01")
    alpha_practice_session_id = create_practice_session(client, headers, "2026-07-02")
    link_swing_thought(client, headers, zeta_practice_session_id, zeta_swing_thought_id)
    link_swing_thought(client, headers, alpha_practice_session_id, alpha_swing_thought_id)
    create_round(client, headers, "2026-07-05", 80)
    create_round(client, headers, "2026-07-10", 82)
    create_round(client, headers, "2026-08-10", 94)
    create_round(client, headers, "2026-08-20", 96)

    response = client.get(
        "/api/v1/analytics/swing-thought-effectiveness",
        headers=headers,
    )

    assert response.status_code == 200
    results = response.json()
    assert [result["swing_thought_id"] for result in results] == [
        alpha_swing_thought_id,
        zeta_swing_thought_id,
        beta_swing_thought_id,
    ]
    assert [result["title"] for result in results] == ["Alpha", "Zeta", "Beta"]
