import os
import pytest

from terec.database import cassandra_session
from cassandra.cluster import Session


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "test", "docker-compose.yaml")


@pytest.fixture(scope="session")
def cassandra(docker_services) -> Session:
    """
    Ensure that Cassandra service is up and responsive.
    Returns session (Cassandra connection).
    """

    def is_cassandra_responsive() -> bool:
        try:
            cassandra_session()
            return True
        except Exception:
            return False

    docker_services.wait_until_responsive(
        timeout=120.0, pause=3.0, check=lambda: is_cassandra_responsive()
    )
    return cassandra_session()
