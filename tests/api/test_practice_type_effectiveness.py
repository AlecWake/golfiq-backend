import pytest


ENDPOINT = "/api/v1/analytics/practice-types/effectiveness"


def register_and_login(client, email="practice-types@example.com"):
    password = "secure-password-123"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Practice Type",
            "last_name": "Tester",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_practice(client, headers, session_date, practice_type):
    response = client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json={"session_date": session_date, "practice_type": practice_type},
    )
    assert response.status_code == 201


def create_round(client, headers, round_date, total_score):
    response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": round_date,
            "course_name": "Practice Type Course",
            "holes_played": 18,
            "total_score": total_score,
        },
    )
    assert response.status_code == 201


def result_by_type(response_json, practice_type):
    return next(
        result
        for result in response_json["results"]
        if result["practice_type"] == practice_type
    )


def test_practice_type_effectiveness_requires_authentication(client):
    assert client.get(ENDPOINT).status_code == 401


def test_practice_type_effectiveness_empty_data(client):
    headers = register_and_login(client, "practice-types-empty@example.com")

    response = client.get(ENDPOINT, headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "total_practice_types": 0,
        "total_practice_sessions_analyzed": 0,
        "total_rounds_analyzed": 0,
        "overall_average_score": None,
        "lookback_days": 14,
        "minimum_rounds": 2,
        "results": [],
    }


def test_practice_without_rounds_is_insufficient(client):
    headers = register_and_login(client, "practice-types-no-rounds@example.com")
    create_practice(client, headers, "2026-06-01", "putting")

    response_json = client.get(ENDPOINT, headers=headers).json()
    result = response_json["results"][0]

    assert result["associated_round_count"] == 0
    assert result["average_associated_round_score"] is None
    assert result["effectiveness_label"] == "insufficient_data"
    assert result["confidence_label"] == "insufficient_data"


def test_one_associated_round_is_insufficient_by_default(client):
    headers = register_and_login(client, "practice-types-one-round@example.com")
    create_practice(client, headers, "2026-06-01", "range")
    create_round(client, headers, "2026-06-05", 82)

    result = client.get(ENDPOINT, headers=headers).json()["results"][0]

    assert result["associated_round_count"] == 1
    assert result["effectiveness_label"] == "insufficient_data"


@pytest.mark.parametrize(
    ("practice_type", "scores", "expected_label"),
    (
        ("putting", (80, 82), "promising"),
        ("range", (85, 86), "neutral"),
        ("driving", (90, 92), "struggling"),
    ),
)
def test_effectiveness_labels(client, practice_type, scores, expected_label):
    headers = register_and_login(
        client, f"practice-types-{practice_type}@example.com"
    )
    create_round(client, headers, "2026-05-01", 86)
    create_practice(client, headers, "2026-06-01", practice_type)
    create_round(client, headers, "2026-06-05", scores[0])
    create_round(client, headers, "2026-06-10", scores[1])

    result = client.get(ENDPOINT, headers=headers).json()["results"][0]

    assert result["effectiveness_label"] == expected_label


def test_types_are_grouped_case_insensitively_with_whitespace(client):
    headers = register_and_login(client, "practice-types-normalize@example.com")
    create_practice(client, headers, "2026-06-01", " Putting ")
    create_practice(client, headers, "2026-06-02", "PUTTING")
    create_practice(client, headers, "2026-06-03", "putting")
    create_round(client, headers, "2026-06-05", 82)

    response_json = client.get(ENDPOINT, headers=headers).json()

    assert response_json["total_practice_types"] == 1
    assert response_json["results"][0]["practice_type"] == "Putting"
    assert response_json["results"][0]["practice_session_count"] == 3
    assert response_json["results"][0]["associated_round_count"] == 1


def test_round_is_deduplicated_with_multiple_same_type_sessions(client):
    headers = register_and_login(client, "practice-types-deduplicate@example.com")
    create_practice(client, headers, "2026-06-01", "range")
    create_practice(client, headers, "2026-06-02", "range")
    create_round(client, headers, "2026-06-05", 80)

    result = client.get(
        f"{ENDPOINT}?minimum_rounds=1", headers=headers
    ).json()["results"][0]

    assert result["practice_session_count"] == 2
    assert result["associated_round_count"] == 1


def test_custom_lookback_and_minimum_rounds(client):
    headers = register_and_login(client, "practice-types-parameters@example.com")
    create_practice(client, headers, "2026-06-01", "short game")
    create_round(client, headers, "2026-06-05", 82)
    create_round(client, headers, "2026-06-20", 80)

    short_window = client.get(
        f"{ENDPOINT}?lookback_days=7&minimum_rounds=1", headers=headers
    ).json()
    long_window = client.get(
        f"{ENDPOINT}?lookback_days=30&minimum_rounds=3", headers=headers
    ).json()

    assert short_window["results"][0]["associated_round_count"] == 1
    assert short_window["results"][0]["confidence_label"] == "low"
    assert long_window["results"][0]["associated_round_count"] == 2
    assert long_window["results"][0]["effectiveness_label"] == "insufficient_data"


@pytest.mark.parametrize(
    "query_string",
    (
        "?lookback_days=0",
        "?lookback_days=91",
        "?minimum_rounds=0",
        "?minimum_rounds=21",
    ),
)
def test_invalid_query_parameters(client, query_string):
    headers = register_and_login(
        client, f"practice-types-invalid-{query_string[-1]}@example.com"
    )
    assert client.get(f"{ENDPOINT}{query_string}", headers=headers).status_code == 422


def test_ownership_isolation(client):
    owner_headers = register_and_login(client, "practice-types-owner@example.com")
    other_headers = register_and_login(client, "practice-types-other@example.com")
    create_practice(client, owner_headers, "2026-06-01", "putting")
    create_round(client, owner_headers, "2026-06-05", 70)
    create_practice(client, other_headers, "2026-06-01", "range")
    create_round(client, other_headers, "2026-06-05", 100)

    response_json = client.get(ENDPOINT, headers=other_headers).json()

    assert response_json["total_practice_types"] == 1
    assert response_json["total_rounds_analyzed"] == 1
    assert response_json["overall_average_score"] == 100.0
    assert response_json["results"][0]["practice_type"] == "Range"


def test_results_are_deterministic_and_promising_first(client):
    headers = register_and_login(client, "practice-types-order@example.com")
    create_round(client, headers, "2026-05-01", 90)
    for practice_type, session_date, score in (
        ("driving", "2026-06-01", 95),
        ("putting", "2026-07-01", 80),
        ("range", "2026-08-01", 90),
    ):
        create_practice(client, headers, session_date, practice_type)
        create_round(client, headers, session_date[:-2] + "05", score)

    first_json = client.get(
        f"{ENDPOINT}?minimum_rounds=1", headers=headers
    ).json()
    second_json = client.get(
        f"{ENDPOINT}?minimum_rounds=1", headers=headers
    ).json()

    assert first_json == second_json
    assert [result["practice_type"] for result in first_json["results"]] == [
        "Putting", "Range", "Driving"
    ]
    assert "does not prove" in first_json["results"][0]["observation"]
