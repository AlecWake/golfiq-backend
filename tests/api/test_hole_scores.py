def register_and_login(client, email="holescores@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "HoleScore",
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


def create_round(client, headers, course_name="Hole Score Course"):
    response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": "2026-07-06",
            "course_name": course_name,
            "holes_played": 18,
            "total_score": 82,
        },
    )

    return response.json()["id"]


def hole_score_payload(hole_number=1):
    return {
        "hole_number": hole_number,
        "strokes": 4,
        "putts": 2,
        "fairway_hit": True,
        "green_in_regulation": True,
        "penalty_strokes": 0,
        "notes": "Solid par.",
    }


def create_hole_score(client, headers, round_id, hole_number=1):
    response = client.post(
        f"/api/v1/rounds/{round_id}/hole-scores",
        headers=headers,
        json=hole_score_payload(hole_number),
    )

    return response.json()["id"]


def test_create_hole_score(client):
    headers = register_and_login(client)
    round_id = create_round(client, headers)

    response = client.post(
        f"/api/v1/rounds/{round_id}/hole-scores",
        headers=headers,
        json=hole_score_payload(),
    )

    assert response.status_code == 201
    assert response.json()["round_id"] == round_id
    assert response.json()["hole_number"] == 1
    assert response.json()["strokes"] == 4
    assert response.json()["fairway_hit"] is True


def test_list_hole_scores(client):
    headers = register_and_login(client, email="listholescores@example.com")
    round_id = create_round(client, headers)

    create_hole_score(client, headers, round_id, hole_number=2)
    create_hole_score(client, headers, round_id, hole_number=1)

    response = client.get(
        f"/api/v1/rounds/{round_id}/hole-scores",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["hole_number"] == 1
    assert response.json()[1]["hole_number"] == 2


def test_get_single_hole_score(client):
    headers = register_and_login(client, email="getholescore@example.com")
    round_id = create_round(client, headers)
    hole_score_id = create_hole_score(client, headers, round_id)

    response = client.get(
        f"/api/v1/rounds/{round_id}/hole-scores/{hole_score_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == hole_score_id
    assert response.json()["notes"] == "Solid par."


def test_update_hole_score(client):
    headers = register_and_login(client, email="updateholescore@example.com")
    round_id = create_round(client, headers)
    hole_score_id = create_hole_score(client, headers, round_id)

    response = client.put(
        f"/api/v1/rounds/{round_id}/hole-scores/{hole_score_id}",
        headers=headers,
        json={
            "strokes": 5,
            "putts": 1,
            "fairway_hit": False,
            "penalty_strokes": 1,
            "notes": "Penalty off the tee.",
        },
    )

    assert response.status_code == 200
    assert response.json()["strokes"] == 5
    assert response.json()["putts"] == 1
    assert response.json()["fairway_hit"] is False
    assert response.json()["penalty_strokes"] == 1
    assert response.json()["green_in_regulation"] is True


def test_delete_hole_score(client):
    headers = register_and_login(client, email="deleteholescore@example.com")
    round_id = create_round(client, headers)
    hole_score_id = create_hole_score(client, headers, round_id)

    delete_response = client.delete(
        f"/api/v1/rounds/{round_id}/hole-scores/{hole_score_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/rounds/{round_id}/hole-scores/{hole_score_id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_duplicate_hole_scores_are_prevented(client):
    headers = register_and_login(client, email="duplicateholescore@example.com")
    round_id = create_round(client, headers)

    first_response = client.post(
        f"/api/v1/rounds/{round_id}/hole-scores",
        headers=headers,
        json=hole_score_payload(),
    )
    duplicate_response = client.post(
        f"/api/v1/rounds/{round_id}/hole-scores",
        headers=headers,
        json=hole_score_payload(),
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


def test_duplicate_hole_scores_are_prevented_on_update(client):
    headers = register_and_login(client, email="updateconflictholescore@example.com")
    round_id = create_round(client, headers)
    first_hole_score_id = create_hole_score(client, headers, round_id, hole_number=1)
    create_hole_score(client, headers, round_id, hole_number=2)

    response = client.put(
        f"/api/v1/rounds/{round_id}/hole-scores/{first_hole_score_id}",
        headers=headers,
        json={"hole_number": 2},
    )

    assert response.status_code == 409


def test_cannot_access_another_users_hole_scores(client):
    user_one_headers = register_and_login(client, email="holeowner@example.com")
    user_two_headers = register_and_login(client, email="holeother@example.com")
    round_id = create_round(client, user_one_headers, course_name="Private Holes")
    hole_score_id = create_hole_score(client, user_one_headers, round_id)

    list_response = client.get(
        f"/api/v1/rounds/{round_id}/hole-scores",
        headers=user_two_headers,
    )
    get_response = client.get(
        f"/api/v1/rounds/{round_id}/hole-scores/{hole_score_id}",
        headers=user_two_headers,
    )
    update_response = client.put(
        f"/api/v1/rounds/{round_id}/hole-scores/{hole_score_id}",
        headers=user_two_headers,
        json={"strokes": 3},
    )
    delete_response = client.delete(
        f"/api/v1/rounds/{round_id}/hole-scores/{hole_score_id}",
        headers=user_two_headers,
    )
    create_response = client.post(
        f"/api/v1/rounds/{round_id}/hole-scores",
        headers=user_two_headers,
        json=hole_score_payload(hole_number=2),
    )

    assert list_response.status_code == 404
    assert get_response.status_code == 404
    assert update_response.status_code == 404
    assert delete_response.status_code == 404
    assert create_response.status_code == 404


def test_hole_score_routes_require_auth(client):
    response = client.get("/api/v1/rounds/1/hole-scores")

    assert response.status_code == 401


def test_hole_score_fields_are_validated(client):
    headers = register_and_login(client, email="validateholescore@example.com")
    round_id = create_round(client, headers)
    payload = hole_score_payload()
    payload["hole_number"] = 19

    response = client.post(
        f"/api/v1/rounds/{round_id}/hole-scores",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 422
