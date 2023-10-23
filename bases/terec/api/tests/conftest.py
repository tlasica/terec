import pytest
from starlette.testclient import TestClient
from terec.api.main import app


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    client = TestClient(app)
    return client
