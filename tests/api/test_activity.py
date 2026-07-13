from datetime import datetime, timezone

from app.db.models.practice_session import PracticeSession
from app.db.models.round import Round


def register_and_login(client, email="activity@example.com"):
    password = "secure-password-123"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Activity",
            "last_name": "Tester",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


def create_round(client, headers, round_date="2026-06-28", course_name="Course"):
    return client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": round_date,
            "course_name": course_name,
            "holes_played": 18,
            "total_score": 92,
        },
    )


def create_practice(client, headers, session_date="2026-06-29", **values):
    payload = {"session_date": session_date, "practice_type": "putting"}
    payload.update(values)
    return client.post("/api/v1/practice-sessions", headers=headers, json=payload)


def test_activity_requires_authentication(client):
    assert client.get("/api/v1/activity").status_code == 401


def test_empty_activity_feed(client):
    headers = register_and_login(client)
    response = client.get("/api/v1/activity", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "total": 0, "limit": 20, "offset": 0, "has_more": False, "items": []
    }


def test_combined_feed_mapping_order_and_optional_fields(client):
    headers = register_and_login(client, "combined@example.com")
    create_round(client, headers)
    create_practice(client, headers, duration_minutes=45, overall_rating=8)
    body = client.get("/api/v1/activity", headers=headers).json()
    assert body["total"] == 2
    assert [item["activity_type"] for item in body["items"]] == ["practice", "round"]
    assert body["items"][0]["summary"] == "45-minute putting session rated 8/10"
    assert body["items"][0]["metadata"] == {
        "practice_type": "putting", "duration_minutes": 45, "overall_rating": 8
    }
    assert body["items"][1]["summary"] == "18-hole round: 92"
    assert body["items"][1]["metadata"]["tee_box"] is None


def test_activity_type_filters_and_validation(client):
    headers = register_and_login(client, "types@example.com")
    create_round(client, headers)
    create_practice(client, headers)
    rounds = client.get("/api/v1/activity?activity_type=round", headers=headers)
    practices = client.get("/api/v1/activity?activity_type=practice", headers=headers)
    assert rounds.json()["total"] == 1
    assert rounds.json()["items"][0]["activity_type"] == "round"
    assert practices.json()["total"] == 1
    assert practices.json()["items"][0]["activity_type"] == "practice"
    assert client.get("/api/v1/activity?activity_type=other", headers=headers).status_code == 422


def test_query_bounds_and_invalid_date_range(client):
    headers = register_and_login(client, "validation@example.com")
    for query in ("limit=0", "limit=101", "offset=-1"):
        assert client.get(f"/api/v1/activity?{query}", headers=headers).status_code == 422
    response = client.get(
        "/api/v1/activity?date_from=2026-07-02&date_to=2026-07-01",
        headers=headers,
    )
    assert response.status_code == 422


def test_inclusive_date_filters(client):
    headers = register_and_login(client, "dates@example.com")
    create_round(client, headers, "2026-06-27", "Early")
    create_round(client, headers, "2026-06-28", "Middle")
    create_practice(client, headers, "2026-06-29")
    response = client.get(
        "/api/v1/activity?date_from=2026-06-28&date_to=2026-06-29",
        headers=headers,
    )
    assert response.json()["total"] == 2
    assert {item["title"] for item in response.json()["items"]} == {"Middle", "putting"}


def test_pagination_total_has_more_and_offset_beyond_total(client):
    headers = register_and_login(client, "pages@example.com")
    for day in ("27", "28", "29"):
        create_round(client, headers, f"2026-06-{day}", f"Course {day}")
    first = client.get("/api/v1/activity?limit=2", headers=headers).json()
    later = client.get("/api/v1/activity?limit=2&offset=2", headers=headers).json()
    beyond = client.get("/api/v1/activity?offset=10", headers=headers).json()
    assert (first["total"], first["has_more"], len(first["items"])) == (3, True, 2)
    assert (later["total"], later["has_more"], len(later["items"])) == (3, False, 1)
    assert (beyond["total"], beyond["has_more"], beyond["items"]) == (3, False, [])


def test_deterministic_tie_breakers(client, db_session):
    headers = register_and_login(client, "ties@example.com")
    first = create_round(client, headers, "2026-06-28", "First").json()
    second = create_round(client, headers, "2026-06-28", "Second").json()
    fixed_time = datetime(2026, 6, 28, 12, tzinfo=timezone.utc)
    db_session.query(Round).filter(Round.id.in_([first["id"], second["id"]])).update(
        {Round.created_at: fixed_time}, synchronize_session=False
    )
    db_session.commit()
    items = client.get("/api/v1/activity", headers=headers).json()["items"]
    assert [item["title"] for item in items] == ["Second", "First"]


def test_ownership_isolation(client):
    owner_headers = register_and_login(client, "owner-activity@example.com")
    other_headers = register_and_login(client, "other-activity@example.com")
    create_round(client, owner_headers)
    create_practice(client, owner_headers)
    assert client.get("/api/v1/activity", headers=other_headers).json()["total"] == 0
