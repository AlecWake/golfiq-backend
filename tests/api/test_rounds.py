def register_and_login(client, email="rounds@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Round",
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


def test_create_round(client):
    headers = register_and_login(client)

    response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": "2026-06-28",
            "course_name": "Pebble Beach Golf Links",
            "tee_box": "Blue",
            "holes_played": 18,
            "total_score": 82,
            "notes": "Strong front nine.",
        },
    )

    assert response.status_code == 201
    assert response.json()["course_name"] == "Pebble Beach Golf Links"
    assert response.json()["holes_played"] == 18
    assert response.json()["total_score"] == 82


def test_list_rounds(client):
    headers = register_and_login(client, email="listrounds@example.com")

    client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": "2026-06-28",
            "course_name": "Local Municipal",
            "holes_played": 9,
            "total_score": 41,
        },
    )

    response = client.get("/api/v1/rounds", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["course_name"] == "Local Municipal"


def test_get_single_round(client):
    headers = register_and_login(client, email="getround@example.com")

    create_response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": "2026-06-28",
            "course_name": "Pinehurst No. 2",
            "holes_played": 18,
            "total_score": 88,
        },
    )

    round_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/rounds/{round_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["course_name"] == "Pinehurst No. 2"


def test_update_round(client):
    headers = register_and_login(client, email="updateround@example.com")

    create_response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": "2026-06-28",
            "course_name": "Old Course",
            "holes_played": 18,
            "total_score": 90,
        },
    )

    round_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/rounds/{round_id}",
        headers=headers,
        json={
            "course_name": "Updated Course",
            "tee_box": "White",
            "total_score": 84,
            "notes": "Better putting.",
        },
    )

    assert response.status_code == 200
    assert response.json()["course_name"] == "Updated Course"
    assert response.json()["tee_box"] == "White"
    assert response.json()["total_score"] == 84


def test_delete_round(client):
    headers = register_and_login(client, email="deleteround@example.com")

    create_response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": "2026-06-28",
            "course_name": "Delete Course",
            "holes_played": 9,
            "total_score": 39,
        },
    )

    round_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/rounds/{round_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/rounds/{round_id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_cannot_access_another_users_round(client):
    user_one_headers = register_and_login(client, email="roundone@example.com")
    user_two_headers = register_and_login(client, email="roundtwo@example.com")

    create_response = client.post(
        "/api/v1/rounds",
        headers=user_one_headers,
        json={
            "round_date": "2026-06-28",
            "course_name": "Private Round",
            "holes_played": 18,
            "total_score": 78,
        },
    )

    round_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/rounds/{round_id}",
        headers=user_two_headers,
    )

    assert response.status_code == 404


def test_round_routes_require_auth(client):
    response = client.get("/api/v1/rounds")

    assert response.status_code == 401
