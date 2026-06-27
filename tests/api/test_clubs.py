def register_and_login(client, email="clubs@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Club",
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


def test_create_club(client):
    headers = register_and_login(client)

    response = client.post(
        "/api/v1/clubs",
        headers=headers,
        json={
            "club_name": "7 Iron",
            "club_type": "iron",
            "manufacturer": "Tommy Armour",
            "model": "845 Silver Scot",
            "loft": 34,
            "carry_distance": 130,
            "total_distance": 140,
        },
    )

    assert response.status_code == 201
    assert response.json()["club_name"] == "7 Iron"
    assert response.json()["club_type"] == "iron"


def test_list_clubs(client):
    headers = register_and_login(client, email="listclubs@example.com")

    client.post(
        "/api/v1/clubs",
        headers=headers,
        json={
            "club_name": "Driver",
            "club_type": "wood",
        },
    )

    response = client.get("/api/v1/clubs", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["club_name"] == "Driver"


def test_get_single_club(client):
    headers = register_and_login(client, email="getclub@example.com")

    create_response = client.post(
        "/api/v1/clubs",
        headers=headers,
        json={
            "club_name": "Putter",
            "club_type": "putter",
        },
    )

    club_id = create_response.json()["id"]

    response = client.get(f"/api/v1/clubs/{club_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["club_name"] == "Putter"


def test_update_club(client):
    headers = register_and_login(client, email="updateclub@example.com")

    create_response = client.post(
        "/api/v1/clubs",
        headers=headers,
        json={
            "club_name": "Old 8 Iron",
            "club_type": "iron",
        },
    )

    club_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/clubs/{club_id}",
        headers=headers,
        json={
            "club_name": "8 Iron",
            "carry_distance": 125,
        },
    )

    assert response.status_code == 200
    assert response.json()["club_name"] == "8 Iron"
    assert response.json()["carry_distance"] == 125


def test_delete_club(client):
    headers = register_and_login(client, email="deleteclub@example.com")

    create_response = client.post(
        "/api/v1/clubs",
        headers=headers,
        json={
            "club_name": "Old Wedge",
            "club_type": "wedge",
        },
    )

    club_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/clubs/{club_id}", headers=headers)

    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/clubs/{club_id}", headers=headers)

    assert get_response.status_code == 404


def test_cannot_access_another_users_club(client):
    user_one_headers = register_and_login(client, email="userone@example.com")
    user_two_headers = register_and_login(client, email="usertwo@example.com")

    create_response = client.post(
        "/api/v1/clubs",
        headers=user_one_headers,
        json={
            "club_name": "Private Driver",
            "club_type": "wood",
        },
    )

    club_id = create_response.json()["id"]

    response = client.get(f"/api/v1/clubs/{club_id}", headers=user_two_headers)

    assert response.status_code == 404


def test_club_routes_require_auth(client):
    response = client.get("/api/v1/clubs")

    assert response.status_code == 401