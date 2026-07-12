from datetime import datetime, timezone

import pytest

from app.db.models.golfer_profile import GolferProfile
from app.db.models.user import User
from app.schemas.recommendation import PracticePlanResponse


def register_and_login(client, email="recommendations@example.com"):
    password = "secure-password-123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Recommendation",
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


def create_practice_session(
    client,
    headers,
    practice_type="range",
    session_date="2026-07-06",
    duration_minutes=45,
    overall_rating=8,
):
    payload = {
        "session_date": session_date,
        "practice_type": practice_type,
    }

    if duration_minutes is not None:
        payload["duration_minutes"] = duration_minutes
    if overall_rating is not None:
        payload["overall_rating"] = overall_rating

    response = client.post(
        "/api/v1/practice-sessions",
        headers=headers,
        json=payload,
    )

    return response.json()["id"]


def create_round(
    client,
    headers,
    course_name="Recommendation Course",
    total_score=88,
    holes_played=18,
    round_date="2026-07-06",
):
    response = client.post(
        "/api/v1/rounds",
        headers=headers,
        json={
            "round_date": round_date,
            "course_name": course_name,
            "holes_played": holes_played,
            "total_score": total_score,
        },
    )

    return response.json()["id"]


def create_round_stats(
    client,
    headers,
    round_id,
    fairways_hit=8,
    fairways_possible=14,
    greens_in_regulation=9,
    putts=30,
    penalties=1,
):
    client.post(
        f"/api/v1/rounds/{round_id}/stats",
        headers=headers,
        json={
            "fairways_hit": fairways_hit,
            "fairways_possible": fairways_possible,
            "greens_in_regulation": greens_in_regulation,
            "putts": putts,
            "penalties": penalties,
            "up_and_downs": 0,
            "sand_saves": 0,
        },
    )


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


def categories(response_json):
    return {recommendation["category"] for recommendation in response_json}


def titles(response_json):
    return {recommendation["title"] for recommendation in response_json}


def update_profile(client, headers, **profile_fields):
    response = client.put(
        "/api/v1/users/me/profile",
        headers=headers,
        json=profile_fields,
    )
    assert response.status_code == 200
    return response.json()


def test_sparse_recommendations_use_profile_miss_and_goal(client):
    headers = register_and_login(client, email="recommendations-profile@example.com")
    update_profile(
        client,
        headers,
        experience_level="beginner",
        dominant_miss="slice",
        scoring_goal="Break 100",
    )

    first_json = client.get("/api/v1/recommendations", headers=headers).json()
    second_json = client.get("/api/v1/recommendations", headers=headers).json()

    assert first_json == second_json
    assert len([item for item in first_json if item["category"] == "Accuracy"]) == 1
    assert any("slice" in item["description"] for item in first_json)
    assert any("Break 100" in item["description"] for item in first_json)


def test_profile_personalizes_priorities_plan_and_schedule(client):
    headers = register_and_login(client, email="priorities-profile@example.com")
    update_profile(
        client,
        headers,
        experience_level="intermediate",
        dominant_miss="top",
        scoring_goal="Break 90",
        current_handicap_estimate=22,
    )

    priorities = client.get(
        "/api/v1/recommendations/practice-priorities", headers=headers
    ).json()
    plan = practice_plan(client, headers).json()
    schedule = weekly_schedule(
        client, headers, "?available_days=2&minutes_per_day=30"
    ).json()

    assert len({item["category"] for item in priorities}) == len(priorities)
    assert any("top" in item["explanation"] for item in priorities)
    assert any("Break 90" in item["explanation"] for item in priorities)
    assert any(item["category"] == "Ball Striking" for item in plan["practice_items"])
    assert all(day["total_minutes"] <= 30 for day in schedule["schedule"])
    assert sum(day["total_minutes"] for day in schedule["schedule"]) <= 60


def test_handicap_context_influences_fallback_without_optional_fields(client):
    headers = register_and_login(client, email="handicap-profile@example.com")
    update_profile(client, headers, current_handicap_estimate=32)

    priorities = client.get(
        "/api/v1/recommendations/practice-priorities", headers=headers
    ).json()

    ball_striking = next(item for item in priorities if item["category"] == "Ball Striking")
    assert ball_striking["supporting_metric"] == "Golfer profile context"


def test_missing_profile_is_safe(client, db_session):
    headers = register_and_login(client, email="missing-profile@example.com")
    user = db_session.query(User).filter(User.email == "missing-profile@example.com").one()
    db_session.query(GolferProfile).filter(GolferProfile.user_id == user.id).delete()
    db_session.commit()

    assert client.get("/api/v1/recommendations", headers=headers).status_code == 200
    assert client.get(
        "/api/v1/recommendations/practice-priorities", headers=headers
    ).status_code == 200


def test_strong_analytics_remain_ahead_of_advanced_profile_hint(client):
    headers = register_and_login(client, email="advanced-profile@example.com")
    update_profile(
        client,
        headers,
        experience_level="advanced",
        dominant_miss="slice",
        current_handicap_estimate=6,
    )
    for index, total_score in enumerate((88, 89, 90), start=1):
        round_identifier = create_round(
            client,
            headers,
            total_score=total_score,
            round_date=f"2026-06-0{index}",
        )
        create_round_stats(
            client,
            headers,
            round_identifier,
            fairways_hit=10,
            greens_in_regulation=1,
            putts=31,
            penalties=0,
        )

    priorities = client.get(
        "/api/v1/recommendations/practice-priorities", headers=headers
    ).json()

    assert priorities[0]["category"] == "Iron Play"
    assert priorities[0]["priority_level"] == "High"
    assert not any(
        item["supporting_metric"] == "Profile dominant miss: slice"
        for item in priorities
    )


def test_recommendations_for_user_with_no_data(client):
    headers = register_and_login(client, email="recommendations-empty@example.com")

    response = client.get("/api/v1/recommendations", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert categories(response.json()) == {"Practice", "General"}
    assert "Log your first practice session" in titles(response.json())
    assert "Create an active swing thought" in titles(response.json())
    assert "Log a round when you play" in titles(response.json())


def test_recommendations_for_user_with_practice_only(client):
    headers = register_and_login(client, email="recommendations-practice@example.com")
    create_practice_session(client, headers)
    create_swing_thought(client, headers)

    response = client.get("/api/v1/recommendations", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "General"
    assert response.json()[0]["title"] == "Log a round when you play"


def test_recommendations_for_user_with_rounds_only(client):
    headers = register_and_login(client, email="recommendations-rounds@example.com")
    create_round(client, headers)

    response = client.get("/api/v1/recommendations", headers=headers)

    assert response.status_code == 200
    assert "Log your first practice session" in titles(response.json())
    assert "Create an active swing thought" in titles(response.json())


def test_recommendations_use_round_analytics(client):
    headers = register_and_login(client, email="recommendations-analytics@example.com")
    first_round_id = create_round(
        client,
        headers,
        total_score=92,
        round_date="2026-06-01",
    )
    second_round_id = create_round(
        client,
        headers,
        total_score=78,
        round_date="2026-06-20",
    )
    third_round_id = create_round(
        client,
        headers,
        total_score=96,
        round_date="2026-07-06",
    )
    create_round_stats(
        client,
        headers,
        first_round_id,
        fairways_hit=5,
        fairways_possible=14,
        greens_in_regulation=4,
        putts=38,
        penalties=2,
    )
    create_round_stats(
        client,
        headers,
        second_round_id,
        fairways_hit=6,
        fairways_possible=14,
        greens_in_regulation=5,
        putts=37,
        penalties=2,
    )
    create_round_stats(
        client,
        headers,
        third_round_id,
        fairways_hit=4,
        fairways_possible=14,
        greens_in_regulation=3,
        putts=39,
        penalties=3,
    )

    response = client.get("/api/v1/recommendations", headers=headers)

    assert response.status_code == 200
    assert "Prioritize putting practice" in titles(response.json())
    assert "Practice approach shots" in titles(response.json())
    assert "Tighten tee shot accuracy" in titles(response.json())
    assert "Reduce penalty strokes" in titles(response.json())
    assert "Build more consistent scoring" in titles(response.json())


def test_recommendation_generation_includes_required_fields(client):
    headers = register_and_login(client, email="recommendations-fields@example.com")

    response = client.get("/api/v1/recommendations", headers=headers)

    assert response.status_code == 200
    first_recommendation = response.json()[0]
    assert set(first_recommendation) == {
        "recommendation_id",
        "category",
        "priority",
        "title",
        "description",
    }
    assert first_recommendation["recommendation_id"] == "rec-1"
    assert first_recommendation["priority"] in {"low", "medium", "high"}


def test_recommendations_isolate_user_ownership(client):
    user_one_headers = register_and_login(
        client,
        email="recommendations-owner@example.com",
    )
    user_two_headers = register_and_login(
        client,
        email="recommendations-other@example.com",
    )
    round_id = create_round(client, user_one_headers, total_score=99)
    create_round_stats(
        client,
        user_one_headers,
        round_id,
        fairways_hit=2,
        fairways_possible=14,
        greens_in_regulation=1,
        putts=42,
        penalties=5,
    )
    create_practice_session(client, user_two_headers)
    create_swing_thought(client, user_two_headers)

    response = client.get("/api/v1/recommendations", headers=user_two_headers)

    assert response.status_code == 200
    assert response.json() == [
        {
            "recommendation_id": "rec-1",
            "category": "General",
            "priority": "low",
            "title": "Log a round when you play",
            "description": "Rounds help GolfIQ connect your practice habits to on-course results.",
        }
    ]


def test_recommendations_requires_auth(client):
    response = client.get("/api/v1/recommendations")

    assert response.status_code == 401


def priority_categories(response_json):
    return {priority["category"] for priority in response_json}


def priority_titles(response_json):
    return {priority["title"] for priority in response_json}


def priority_level_score(priority_level):
    return {"High": 3, "Medium": 2, "Low": 1}[priority_level]


def assert_ranked_order(response_json):
    assert [
        priority["priority_rank"] for priority in response_json
    ] == list(range(1, len(response_json) + 1))
    assert [
        priority_level_score(priority["priority_level"])
        for priority in response_json
    ] == sorted(
        [
            priority_level_score(priority["priority_level"])
            for priority in response_json
        ],
        reverse=True,
    )


def test_practice_priorities_for_user_with_no_data(client):
    headers = register_and_login(
        client,
        email="practice-priorities-empty@example.com",
    )

    response = client.get(
        "/api/v1/recommendations/practice-priorities",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert priority_categories(response.json()) == {
        "Practice Frequency",
        "Swing Thoughts",
        "Ball Striking",
    }
    assert response.json()[0]["priority_rank"] == 1
    assert response.json()[0]["priority_level"] == "High"
    assert response.json()[0]["category"] == "Practice Frequency"
    assert_ranked_order(response.json())


def test_practice_priorities_for_beginner_user(client):
    headers = register_and_login(
        client,
        email="practice-priorities-beginner@example.com",
    )
    create_practice_session(client, headers)

    response = client.get(
        "/api/v1/recommendations/practice-priorities",
        headers=headers,
    )

    assert response.status_code == 200
    assert priority_categories(response.json()) == {
        "Practice Frequency",
        "Swing Thoughts",
        "Ball Striking",
    }
    assert "Build more practice history" in priority_titles(response.json())
    assert "Create one active swing thought" in priority_titles(response.json())
    assert "Create a baseline with your next round" in priority_titles(response.json())
    assert_ranked_order(response.json())


def test_practice_priorities_for_experienced_user(client):
    headers = register_and_login(
        client,
        email="practice-priorities-experienced@example.com",
    )
    create_swing_thought(client, headers)
    create_practice_session(client, headers, session_date="2026-06-10")
    create_practice_session(client, headers, session_date="2026-06-20")
    create_practice_session(client, headers, session_date="2026-07-01")
    first_round_id = create_round(
        client,
        headers,
        total_score=98,
        round_date="2026-06-01",
    )
    second_round_id = create_round(
        client,
        headers,
        total_score=82,
        round_date="2026-06-15",
    )
    third_round_id = create_round(
        client,
        headers,
        total_score=105,
        round_date="2026-07-06",
    )
    create_round_stats(
        client,
        headers,
        first_round_id,
        fairways_hit=3,
        fairways_possible=14,
        greens_in_regulation=3,
        putts=39,
        penalties=3,
    )
    create_round_stats(
        client,
        headers,
        second_round_id,
        fairways_hit=4,
        fairways_possible=14,
        greens_in_regulation=4,
        putts=37,
        penalties=2,
    )
    create_round_stats(
        client,
        headers,
        third_round_id,
        fairways_hit=2,
        fairways_possible=14,
        greens_in_regulation=2,
        putts=40,
        penalties=4,
    )

    response = client.get(
        "/api/v1/recommendations/practice-priorities",
        headers=headers,
    )

    assert response.status_code == 200
    assert {
        "Putting",
        "Iron Play",
        "Accuracy",
        "Penalties",
        "Consistency",
    }.issubset(priority_categories(response.json()))
    assert "Practice Frequency" not in priority_categories(response.json())
    assert "Swing Thoughts" not in priority_categories(response.json())
    assert_ranked_order(response.json())


def test_practice_priorities_return_multiple_priorities_in_ranked_order(client):
    headers = register_and_login(
        client,
        email="practice-priorities-ranked@example.com",
    )

    response = client.get(
        "/api/v1/recommendations/practice-priorities",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) > 1
    assert_ranked_order(response.json())


def test_practice_priorities_isolate_user_ownership(client):
    user_one_headers = register_and_login(
        client,
        email="practice-priorities-owner@example.com",
    )
    user_two_headers = register_and_login(
        client,
        email="practice-priorities-other@example.com",
    )
    user_one_round_id = create_round(client, user_one_headers, total_score=104)
    create_round_stats(
        client,
        user_one_headers,
        user_one_round_id,
        fairways_hit=1,
        fairways_possible=14,
        greens_in_regulation=1,
        putts=43,
        penalties=6,
    )
    create_swing_thought(client, user_two_headers)
    create_practice_session(
        client,
        user_two_headers,
        session_date="2026-06-01",
    )
    create_practice_session(
        client,
        user_two_headers,
        session_date="2026-06-15",
    )
    create_practice_session(
        client,
        user_two_headers,
        session_date="2026-07-01",
    )
    user_two_round_id = create_round(client, user_two_headers, total_score=82)
    create_round_stats(
        client,
        user_two_headers,
        user_two_round_id,
        fairways_hit=10,
        fairways_possible=14,
        greens_in_regulation=10,
        putts=31,
        penalties=0,
    )

    response = client.get(
        "/api/v1/recommendations/practice-priorities",
        headers=user_two_headers,
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "priority_rank": 1,
            "category": "Consistency",
            "priority_level": "Low",
            "title": "Keep reinforcing what is working",
            "explanation": "Your logged data does not show an urgent weakness, so maintenance and steady tracking are the right priorities.",
            "supporting_metric": "No high-priority gaps detected",
            "suggested_focus": "Continue balanced practice and keep logging round and practice details.",
        }
    ]


def test_practice_priorities_requires_auth(client):
    response = client.get("/api/v1/recommendations/practice-priorities")

    assert response.status_code == 401


def test_practice_priorities_handle_missing_analytics(client):
    headers = register_and_login(
        client,
        email="practice-priorities-missing-analytics@example.com",
    )
    create_round(client, headers)

    response = client.get(
        "/api/v1/recommendations/practice-priorities",
        headers=headers,
    )

    assert response.status_code == 200
    assert "Add detail to future rounds" in priority_titles(response.json())
    assert "Rounds logged without analytics: 1" in {
        priority["supporting_metric"] for priority in response.json()
    }
    assert_ranked_order(response.json())


def practice_plan(client, headers):
    return client.get("/api/v1/recommendations/practice-plan", headers=headers)


def test_practice_plan_for_user_with_no_data(client):
    headers = register_and_login(client, email="practice-plan-empty@example.com")

    response = practice_plan(client, headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["confidence"] == "Low"
    assert 3 <= len(response_json["practice_items"]) <= 6
    assert response_json["estimated_session_length_minutes"] == sum(
        item["recommended_minutes"] for item in response_json["practice_items"]
    )


def test_practice_plan_for_beginner_user(client):
    headers = register_and_login(client, email="practice-plan-beginner@example.com")
    create_practice_session(client, headers)

    response = practice_plan(client, headers)

    assert response.status_code == 200
    assert response.json()["confidence"] == "Low"
    assert "Practice Frequency" in {
        item["category"] for item in response.json()["practice_items"]
    }


def test_practice_plan_for_experienced_user_combines_priorities(client):
    headers = register_and_login(client, email="practice-plan-experienced@example.com")
    create_swing_thought(client, headers)
    for session_date in ("2026-06-10", "2026-06-20", "2026-07-01"):
        create_practice_session(client, headers, session_date=session_date)
    for round_date, total_score in (
        ("2026-06-01", 98),
        ("2026-06-15", 82),
        ("2026-07-06", 105),
    ):
        round_identifier = create_round(
            client,
            headers,
            round_date=round_date,
            total_score=total_score,
        )
        create_round_stats(
            client,
            headers,
            round_identifier,
            fairways_hit=2,
            greens_in_regulation=2,
            putts=40,
            penalties=3,
        )

    response = practice_plan(client, headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["confidence"] == "High"
    assert response_json["overall_focus"] == "Iron Play"
    assert {"Penalties", "Putting", "Iron Play", "Accuracy"}.issubset(
        {item["category"] for item in response_json["practice_items"]}
    )


def test_practice_plan_order_is_deterministic(client):
    headers = register_and_login(client, email="practice-plan-order@example.com")

    first_response = practice_plan(client, headers)
    second_response = practice_plan(client, headers)

    first_items = first_response.json()["practice_items"]
    second_items = second_response.json()["practice_items"]
    assert first_items == second_items
    assert [item["order"] for item in first_items] == list(
        range(1, len(first_items) + 1)
    )


def test_practice_plan_isolates_user_ownership(client):
    owner_headers = register_and_login(client, email="practice-plan-owner@example.com")
    other_headers = register_and_login(client, email="practice-plan-other@example.com")
    owner_round_identifier = create_round(client, owner_headers, total_score=110)
    create_round_stats(
        client,
        owner_headers,
        owner_round_identifier,
        putts=45,
        penalties=6,
    )

    response = practice_plan(client, other_headers)

    assert response.status_code == 200
    assert response.json()["confidence"] == "Low"
    assert "Average putts: 45" not in {
        item["supporting_metric"] for item in response.json()["practice_items"]
    }


def test_practice_plan_requires_authentication(client):
    response = client.get("/api/v1/recommendations/practice-plan")

    assert response.status_code == 401


def weekly_schedule(client, headers, query_string=""):
    return client.get(
        f"/api/v1/recommendations/weekly-practice-schedule{query_string}",
        headers=headers,
    )


def scheduled_items(response_json):
    return [
        focus_item
        for schedule_day in response_json["schedule"]
        for focus_item in schedule_day["focus_items"]
    ]


def test_weekly_schedule_requires_authentication(client):
    response = client.get("/api/v1/recommendations/weekly-practice-schedule")

    assert response.status_code == 401


def test_weekly_schedule_for_user_with_no_data(client):
    headers = register_and_login(client, email="weekly-schedule-empty@example.com")

    response = weekly_schedule(client, headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["confidence"] == "Low"
    assert response_json["available_days"] == 3
    assert response_json["minutes_per_day"] == 60
    assert response_json["total_weekly_minutes"] == 180
    assert len(response_json["schedule"]) == 3
    assert all(item["recommended_minutes"] >= 5 for item in scheduled_items(response_json))


def test_weekly_schedule_for_experienced_user_uses_existing_priorities(client):
    headers = register_and_login(client, email="weekly-schedule-experienced@example.com")
    create_swing_thought(client, headers)
    for session_date in ("2026-06-10", "2026-06-20", "2026-07-01"):
        create_practice_session(client, headers, session_date=session_date)
    for round_date, total_score in (
        ("2026-06-01", 98),
        ("2026-06-15", 82),
        ("2026-07-06", 105),
    ):
        round_identifier = create_round(
            client,
            headers,
            round_date=round_date,
            total_score=total_score,
        )
        create_round_stats(
            client,
            headers,
            round_identifier,
            fairways_hit=2,
            greens_in_regulation=2,
            putts=40,
            penalties=3,
        )

    plan_response = practice_plan(client, headers)
    schedule_response = weekly_schedule(client, headers)

    assert schedule_response.status_code == 200
    assert schedule_response.json()["overall_focus"] == plan_response.json()["overall_focus"]
    plan_categories = {
        item["category"] for item in plan_response.json()["practice_items"]
    }
    assert {
        item["category"] for item in scheduled_items(schedule_response.json())
    }.issubset(plan_categories)


def test_weekly_schedule_accepts_custom_limits(client):
    headers = register_and_login(client, email="weekly-schedule-custom@example.com")

    response = weekly_schedule(
        client,
        headers,
        "?available_days=2&minutes_per_day=30",
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["available_days"] == 2
    assert response_json["minutes_per_day"] == 30
    assert response_json["total_weekly_minutes"] == 60
    assert len(response_json["schedule"]) <= 2


@pytest.mark.parametrize(
    "query_string",
    (
        "?available_days=0",
        "?available_days=8",
        "?minutes_per_day=14",
        "?minutes_per_day=181",
    ),
)
def test_weekly_schedule_rejects_invalid_limits(client, query_string):
    headers = register_and_login(
        client,
        email=f"weekly-schedule-invalid-{query_string[-1]}@example.com",
    )

    response = weekly_schedule(client, headers, query_string)

    assert response.status_code == 422


def test_weekly_schedule_never_exceeds_daily_or_weekly_limits(client):
    headers = register_and_login(client, email="weekly-schedule-limits@example.com")

    response = weekly_schedule(
        client,
        headers,
        "?available_days=2&minutes_per_day=15",
    )

    response_json = response.json()
    assert all(day["total_minutes"] <= 15 for day in response_json["schedule"])
    assert sum(day["total_minutes"] for day in response_json["schedule"]) <= 30


def test_weekly_schedule_allocates_plan_order_before_lower_priorities(client):
    headers = register_and_login(client, email="weekly-schedule-priority@example.com")

    response = weekly_schedule(
        client,
        headers,
        "?available_days=1&minutes_per_day=40",
    )

    items = scheduled_items(response.json())
    assert [item["order"] for item in items] == sorted(item["order"] for item in items)
    assert items[0]["priority"] == "High"


def test_weekly_schedule_is_deterministic(client):
    headers = register_and_login(client, email="weekly-schedule-order@example.com")

    first_json = weekly_schedule(client, headers).json()
    second_json = weekly_schedule(client, headers).json()

    assert first_json["schedule"] == second_json["schedule"]
    assert first_json["overall_focus"] == second_json["overall_focus"]


def test_weekly_schedule_isolates_user_ownership(client):
    owner_headers = register_and_login(client, email="weekly-owner@example.com")
    other_headers = register_and_login(client, email="weekly-other@example.com")
    owner_round_identifier = create_round(client, owner_headers, total_score=110)
    create_round_stats(
        client,
        owner_headers,
        owner_round_identifier,
        putts=45,
        penalties=6,
    )

    response = weekly_schedule(client, other_headers)

    assert response.status_code == 200
    assert response.json()["confidence"] == "Low"
    assert "Prioritize putting efficiency" not in {
        item["title"] for item in scheduled_items(response.json())
    }


def test_weekly_schedule_handles_empty_practice_plan(client, monkeypatch):
    headers = register_and_login(client, email="weekly-empty-plan@example.com")

    def empty_practice_plan(db, current_user):
        return PracticePlanResponse(
            generated_at=datetime.now(timezone.utc),
            overall_focus="",
            confidence="Low",
            estimated_session_length_minutes=0,
            practice_items=[],
        )

    monkeypatch.setattr(
        "app.services.weekly_practice_schedule_service.get_personalized_practice_plan",
        empty_practice_plan,
    )

    response = weekly_schedule(client, headers)

    assert response.status_code == 200
    assert response.json()["schedule"] == []
    assert response.json()["confidence"] == "Low"
    assert response.json()["overall_focus"] == "Build a balanced practice foundation"
