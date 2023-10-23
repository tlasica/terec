from terec.api.core import create_app


def test_sample(cassandra_model):
    assert create_app() is not None
