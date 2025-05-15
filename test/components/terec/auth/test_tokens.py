from terec.auth.tokens import generate_token, hash_token, verify_token


def test_generate_token():
    token1 = generate_token()
    token2 = generate_token()

    # Assert that the tokens are strings
    assert isinstance(token1, str)
    assert isinstance(token2, str)

    # Assert that the tokens are 43 or more characters long (for a 32-byte token)
    assert len(token1) >= 43  # Based on the result of `secrets.token_urlsafe(32)`
    assert len(token2) >= 43

    # Assert that tokens are unique
    assert token1 != token2


def test_hash_token():
    token = "test_token_value"

    hashed_token1 = hash_token(token)
    hashed_token2 = hash_token(token)

    assert isinstance(hashed_token1, bytes)
    assert isinstance(hashed_token2, bytes)

    assert hashed_token1 != hashed_token2


def test_verify_token_success():
    """Test verifying a token successfully."""
    token = generate_token()
    hashed_token = hash_token(token)
    assert verify_token(token, hashed_token) is True


def test_verify_token_failure():
    """Test verifying a token with incorrect data."""
    token = "test_token_value"
    hashed_token = hash_token(token)
    wrong_token = "wrong_token_value"
    assert verify_token(wrong_token, hashed_token) is False
