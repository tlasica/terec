def test_openapi_doc(cassandra_model, api_client):
    response = api_client.get("docs")
    assert response.is_success, response.text
