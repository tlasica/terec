import secrets

from bcrypt import hashpw, gensalt, checkpw


def generate_token():
    return secrets.token_urlsafe(32)


def hash_token(token):
    return hashpw(token.encode("utf-8"), gensalt())


def verify_token(provided_token, hashed_token):
    assert provided_token is not None
    assert hashed_token is not None
    return checkpw(provided_token.encode("utf-8"), hashed_token)
