def test_cassandra_connection_with_default_settings(cassandra):
    assert not cassandra.is_shutdown, "Connection is in shutdown state."
