from app.core.security import hash_password, verify_password


def test_hash_password_returns_different_value():
    plain_password = "secure-password-123"

    hashed_password = hash_password(plain_password)

    assert hashed_password != plain_password


def test_verify_password_returns_true_for_correct_password():
    plain_password = "secure-password-123"

    hashed_password = hash_password(plain_password)

    assert verify_password(plain_password, hashed_password) is True


def test_verify_password_returns_false_for_wrong_password():
    plain_password = "secure-password-123"
    wrong_password = "wrong-password"

    hashed_password = hash_password(plain_password)

    assert verify_password(wrong_password, hashed_password) is False