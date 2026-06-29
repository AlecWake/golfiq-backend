def register_and_login(client, email="swingthoughts@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Swing",
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


def test_create_swing_thought(client):
    headers = register_and_login(client)

    response = client.post(
        "/api/v1/swing-thoughts",
        headers=headers,
        json={
            "title": "Stay behind the ball",
            "description": "Keep head behind ball through impact.",
            "category": "downswing",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Stay behind the ball"
    assert response.json()["category"] == "downswing"


def test_list_swing_thoughts(client):
    headers = register_and_login(client, email="listswingthoughts@example.com")

    client.post(
        "/api/v1/swing-thoughts",
        headers=headers,
        json={
            "title": "Smooth tempo",
            "category": "tempo",
        },
    )

    response = client.get("/api/v1/swing-thoughts", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Smooth tempo"


def test_get_single_swing_thought(client):
    headers = register_and_login(client, email="getswingthought@example.com")

    create_response = client.post(
        "/api/v1/swing-thoughts",
        headers=headers,
        json={
            "title": "Left shoulder under chin",
            "category": "backswing",
        },
    )

    swing_thought_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/swing-thoughts/{swing_thought_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Left shoulder under chin"


def test_update_swing_thought(client):
    headers = register_and_login(client, email="updateswingthought@example.com")

    create_response = client.post(
        "/api/v1/swing-thoughts",
        headers=headers,
        json={
            "title": "Old thought",
            "category": "setup",
        },
    )

    swing_thought_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/swing-thoughts/{swing_thought_id}",
        headers=headers,
        json={
            "title": "New thought",
            "description": "Updated feel.",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New thought"
    assert response.json()["description"] == "Updated feel."


def test_delete_swing_thought(client):
    headers = register_and_login(client, email="deleteswingthought@example.com")

    create_response = client.post(
        "/api/v1/swing-thoughts",
        headers=headers,
        json={
            "title": "Delete me",
            "category": "temporary",
        },
    )

    swing_thought_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/swing-thoughts/{swing_thought_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/swing-thoughts/{swing_thought_id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_cannot_access_another_users_swing_thought(client):
    user_one_headers = register_and_login(client, email="swingone@example.com")
    user_two_headers = register_and_login(client, email="swingtwo@example.com")

    create_response = client.post(
        "/api/v1/swing-thoughts",
        headers=user_one_headers,
        json={
            "title": "Private thought",
            "category": "private",
        },
    )

    swing_thought_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/swing-thoughts/{swing_thought_id}",
        headers=user_two_headers,
    )

    assert response.status_code == 404


def test_swing_thought_routes_require_auth(client):
    response = client.get("/api/v1/swing-thoughts")

    assert response.status_code == 401