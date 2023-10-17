from terec.database import cassandra_session


def test_cassandra_connection_with_default_settings(cassandra):
    conn = cassandra_session()
    assert not conn.is_shutdown, "Connection is in shutdown state."
