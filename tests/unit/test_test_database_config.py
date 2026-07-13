import pytest

from conftest import validate_test_database_url


@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql+psycopg://golfiq_user:local-password@localhost:5433/golfiq_test",
        "postgresql+psycopg://golfiq_user:ci-password@localhost:5432/golfiq_test",
    ],
)
def test_validate_test_database_url_accepts_dedicated_test_database(database_url):
    parsed_url = validate_test_database_url(database_url)

    assert parsed_url.database == "golfiq_test"


@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql+psycopg://golfiq_user:password@localhost:5433/golfiq_dev",
        "",
        "   ",
    ],
)
def test_validate_test_database_url_rejects_unsafe_database(database_url):
    with pytest.raises(RuntimeError, match="golfiq_test"):
        validate_test_database_url(database_url)


def test_validate_test_database_url_does_not_expose_password():
    password = "do-not-leak-this-password"
    database_url = (
        f"postgresql+psycopg://golfiq_user:{password}@localhost:5433/golfiq_dev"
    )

    with pytest.raises(RuntimeError) as exc_info:
        validate_test_database_url(database_url)

    assert password not in str(exc_info.value)
