def register_and_login(client, email="roundstats@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "RoundStat",
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


def create_round(client, headers, course_name="Stats Course"):
    response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": "2026-06-28",
            "course_name": course_name,
            "holes_played": 18,
            "total_score": 82,
        },
    )

    return response.json()["id"]


def round_stat_payload():
    return {
        "fairways_hit": 8,
        "fairways_possible": 14,
        "greens_in_regulation": 9,
        "putts": 31,
        "penalties": 1,
        "up_and_downs": 3,
        "sand_saves": 1,
    }


def test_create_round_stats(client):
    headers = register_and_login(client)
    round_id = create_round(client, headers)

    response = client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json=round_stat_payload(),
    )

    assert response.status_code == 201
    assert response.json()["round_id"] == round_id
    assert response.json()["fairways_hit"] == 8
    assert response.json()["putts"] == 31


def test_get_round_stats(client):
    headers = register_and_login(client, email="getroundstats@example.com")
    round_id = create_round(client, headers)

    client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json=round_stat_payload(),
    )

    response = client.get(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["round_id"] == round_id
    assert response.json()["greens_in_regulation"] == 9


def test_update_round_stats(client):
    headers = register_and_login(client, email="updateroundstats@example.com")
    round_id = create_round(client, headers)

    client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json=round_stat_payload(),
    )

    response = client.put(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json={
            "fairways_hit": 10,
            "putts": 28,
            "penalties": 0,
        },
    )

    assert response.status_code == 200
    assert response.json()["fairways_hit"] == 10
    assert response.json()["putts"] == 28
    assert response.json()["penalties"] == 0
    assert response.json()["fairways_possible"] == 14


def test_delete_round_stats(client):
    headers = register_and_login(client, email="deleteroundstats@example.com")
    round_id = create_round(client, headers)

    client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json=round_stat_payload(),
    )

    delete_response = client.delete(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_cannot_access_another_users_round_stats(client):
    user_one_headers = register_and_login(client, email="statowner@example.com")
    user_two_headers = register_and_login(client, email="statother@example.com")
    round_id = create_round(client, user_one_headers, course_name="Private Stats")

    client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=user_one_headers,
        json=round_stat_payload(),
    )

    get_response = client.get(
        f"/api/v1/rounds/{round_id}/stats",
        headers=user_two_headers,
    )
    create_response = client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=user_two_headers,
        json=round_stat_payload(),
    )

    assert get_response.status_code == 404
    assert create_response.status_code == 404


def test_round_stats_routes_require_auth(client):
    response = client.get("/api/v1/rounds/1/stats")

    assert response.status_code == 401


def test_duplicate_round_stats_creation_is_prevented(client):
    headers = register_and_login(client, email="duplicateroundstats@example.com")
    round_id = create_round(client, headers)

    first_response = client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json=round_stat_payload(),
    )
    duplicate_response = client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json=round_stat_payload(),
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


def test_round_stats_fields_must_be_non_negative(client):
    headers = register_and_login(client, email="validateroundstats@example.com")
    round_id = create_round(client, headers)
    payload = round_stat_payload()
    payload["putts"] = -1

    response = client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 422
