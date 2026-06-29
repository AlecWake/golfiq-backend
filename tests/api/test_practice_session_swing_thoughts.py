def register_and_login(client, email="links@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Link",
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


def create_practice_session(client, headers, practice_type="range"):
    response = client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json={
            "session_date": "2026-06-28",
            "practice_type": practice_type,
            "duration_minutes": 45,
        },
    )

    return response.json()["id"]


def create_swing_thought(client, headers, title="Smooth tempo"):
    response = client.post(
        "/api/v1/swing-thoughts",
        headers=headers,
        json={
            "title": title,
            "category": "tempo",
        },
    )

    return response.json()["id"]


def test_link_swing_thought_to_practice_session(client):
    headers = register_and_login(client)
    practice_session_id = create_practice_session(client, headers)
    swing_thought_id = create_swing_thought(client, headers)

    response = client.post(
        (
            f"/api/v1/practice-sessions/{practice_session_id}"
            f"/swing-thoughts/{swing_thought_id}"
        ),
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["id"] == swing_thought_id
    assert response.json()["title"] == "Smooth tempo"


def test_duplicate_swing_thought_link_is_prevented(client):
    headers = register_and_login(client, email="duplicatelink@example.com")
    practice_session_id = create_practice_session(client, headers)
    swing_thought_id = create_swing_thought(client, headers)

    first_response = client.post(
        (
            f"/api/v1/practice-sessions/{practice_session_id}"
            f"/swing-thoughts/{swing_thought_id}"
        ),
        headers=headers,
    )
    duplicate_response = client.post(
        (
            f"/api/v1/practice-sessions/{practice_session_id}"
            f"/swing-thoughts/{swing_thought_id}"
        ),
        headers=headers,
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


def test_list_practice_session_swing_thoughts(client):
    headers = register_and_login(client, email="listlinks@example.com")
    practice_session_id = create_practice_session(client, headers)
    first_swing_thought_id = create_swing_thought(client, headers, title="Quiet hands")
    second_swing_thought_id = create_swing_thought(client, headers, title="Full turn")

    for swing_thought_id in [first_swing_thought_id, second_swing_thought_id]:
        client.post(
            (
                f"/api/v1/practice-sessions/{practice_session_id}"
                f"/swing-thoughts/{swing_thought_id}"
            ),
            headers=headers,
        )

    response = client.get(
        f"/api/v1/practice-sessions/{practice_session_id}/swing-thoughts",
        headers=headers,
    )

    assert response.status_code == 200
    assert [thought["title"] for thought in response.json()] == [
        "Quiet hands",
        "Full turn",
    ]


def test_unlink_swing_thought_from_practice_session(client):
    headers = register_and_login(client, email="unlink@example.com")
    practice_session_id = create_practice_session(client, headers)
    swing_thought_id = create_swing_thought(client, headers)

    client.post(
        (
            f"/api/v1/practice-sessions/{practice_session_id}"
            f"/swing-thoughts/{swing_thought_id}"
        ),
        headers=headers,
    )

    delete_response = client.delete(
        (
            f"/api/v1/practice-sessions/{practice_session_id}"
            f"/swing-thoughts/{swing_thought_id}"
        ),
        headers=headers,
    )
    list_response = client.get(
        f"/api/v1/practice-sessions/{practice_session_id}/swing-thoughts",
        headers=headers,
    )

    assert delete_response.status_code == 204
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_cannot_link_another_users_swing_thought(client):
    user_one_headers = register_and_login(client, email="linkowner@example.com")
    user_two_headers = register_and_login(client, email="linkother@example.com")
    practice_session_id = create_practice_session(client, user_one_headers)
    swing_thought_id = create_swing_thought(client, user_two_headers)

    response = client.post(
        (
            f"/api/v1/practice-sessions/{practice_session_id}"
            f"/swing-thoughts/{swing_thought_id}"
        ),
        headers=user_one_headers,
    )

    assert response.status_code == 404


def test_cannot_access_another_users_practice_session_swing_thoughts(client):
    user_one_headers = register_and_login(client, email="sessionowner@example.com")
    user_two_headers = register_and_login(client, email="sessionother@example.com")
    practice_session_id = create_practice_session(client, user_one_headers)
    swing_thought_id = create_swing_thought(client, user_two_headers)

    link_response = client.post(
        (
            f"/api/v1/practice-sessions/{practice_session_id}"
            f"/swing-thoughts/{swing_thought_id}"
        ),
        headers=user_two_headers,
    )
    list_response = client.get(
        f"/api/v1/practice-sessions/{practice_session_id}/swing-thoughts",
        headers=user_two_headers,
    )

    assert link_response.status_code == 404
    assert list_response.status_code == 404


def test_practice_session_swing_thought_routes_require_auth(client):
    post_response = client.post("/api/v1/practice-sessions/1/swing-thoughts/1")
    get_response = client.get("/api/v1/practice-sessions/1/swing-thoughts")
    delete_response = client.delete("/api/v1/practice-sessions/1/swing-thoughts/1")

    assert post_response.status_code == 401
    assert get_response.status_code == 401
    assert delete_response.status_code == 401
