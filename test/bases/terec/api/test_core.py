from fastapi.testclient import TestClient

from terec.api.core import create_app


def test_openapi_doc(cassandra_model):
    api_app = create_app()
    assert api_app is not None
    api_client = TestClient(app=api_app)
    response = api_client.get("docs")
    assert response.is_success, response.text
