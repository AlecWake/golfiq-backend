import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.dependencies.database import get_db
from app.main import app
from app.db import models


DEFAULT_TEST_DATABASE_URL = (
    "postgresql+psycopg://golfiq_user:golfiq_password@localhost:5433/golfiq_test"
)


def validate_test_database_url(database_url: str | URL) -> URL:
    """Return a parsed URL only when it targets the dedicated test database."""
    if not database_url or (
        isinstance(database_url, str) and not database_url.strip()
    ):
        raise RuntimeError(
            "TEST_DATABASE_URL must point to the dedicated 'golfiq_test' database."
        )

    try:
        parsed_url = make_url(database_url)
    except (ArgumentError, TypeError, ValueError) as exc:
        raise RuntimeError(
            "TEST_DATABASE_URL must be a valid URL for the dedicated "
            "'golfiq_test' database."
        ) from exc

    if parsed_url.database != "golfiq_test":
        raise RuntimeError(
            "TEST_DATABASE_URL must point to the dedicated 'golfiq_test' database."
        )

    return parsed_url


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    DEFAULT_TEST_DATABASE_URL,
)

engine = create_engine(validate_test_database_url(TEST_DATABASE_URL))

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture()
def db_session():
    validate_test_database_url(engine.url)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        validate_test_database_url(engine.url)
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
