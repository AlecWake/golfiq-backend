import logging
from uuid import UUID

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import create_app


def assert_generated_request_id(header_value: str) -> None:
    assert str(UUID(header_value)) == header_value


def test_request_id_is_generated_for_success(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert_generated_request_id(response.headers["X-Request-ID"])


def test_valid_client_request_id_is_echoed(client):
    response = client.get(
        "/api/v1/health", headers={"X-Request-ID": "client-request_42"}
    )
    assert response.headers["X-Request-ID"] == "client-request_42"


def test_invalid_request_ids_are_replaced(client):
    blank_response = client.get("/api/v1/health", headers={"X-Request-ID": " "})
    long_response = client.get(
        "/api/v1/health", headers={"X-Request-ID": "a" * 129}
    )
    assert_generated_request_id(blank_response.headers["X-Request-ID"])
    assert_generated_request_id(long_response.headers["X-Request-ID"])


def test_authentication_error_is_standardized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["error"]["code"] == "invalid_authentication_credentials"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_validation_error_is_sanitized_and_identifies_field(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "secret-value"},
    )
    body = response.json()
    assert response.status_code == 422
    assert body["error"]["code"] == "validation_error"
    assert any("email" in item["field"] for item in body["error"]["details"])
    assert "secret-value" not in response.text


def test_known_http_error_codes_and_request_ids():
    application = create_app()

    @application.get("/_test/not-found")
    def not_found():
        raise HTTPException(status_code=404, detail="Club not found.")

    @application.get("/_test/conflict")
    def conflict():
        raise HTTPException(status_code=409, detail="Duplicate resource.")

    with TestClient(application) as test_client:
        not_found_response = test_client.get("/_test/not-found")
        conflict_response = test_client.get("/_test/conflict")

    assert not_found_response.json()["error"]["code"] == "resource_not_found"
    assert conflict_response.json()["error"]["code"] == "resource_conflict"
    assert (
        not_found_response.json()["request_id"]
        == not_found_response.headers["X-Request-ID"]
    )


def test_unexpected_error_is_hidden_logged_and_has_request_id(caplog):
    application = create_app()

    @application.get("/_test/unexpected")
    def unexpected():
        raise RuntimeError("private database detail")

    with caplog.at_level(logging.INFO, logger="app"):
        with TestClient(application, raise_server_exceptions=False) as test_client:
            response = test_client.get(
                "/_test/unexpected",
                headers={"Authorization": "Bearer token-must-not-be-logged"},
            )

    body = response.json()
    assert response.status_code == 500
    assert body["error"] == {
        "code": "internal_server_error",
        "message": "An unexpected error occurred.",
        "details": None,
    }
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert "unexpected_request_error" in caplog.text
    assert "private database detail" in caplog.text
    assert "token-must-not-be-logged" not in caplog.text


def test_request_completion_log_contains_safe_required_fields(client, caplog):
    with caplog.at_level(logging.INFO, logger="app.requests"):
        response = client.get(
            "/api/v1/health",
            headers={"Authorization": "Bearer token-must-not-be-logged"},
        )

    log_text = caplog.text
    assert "request_complete" in log_text
    assert f"request_id={response.headers['X-Request-ID']}" in log_text
    assert "method=GET" in log_text
    assert "path=/api/v1/health" in log_text
    assert "status_code=200" in log_text
    assert "elapsed_ms=" in log_text
    assert "token-must-not-be-logged" not in log_text
