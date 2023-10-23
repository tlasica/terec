import logging
import os
import pytest

from cassandra.cluster import Session

from terec.database import cassandra_session
from terec.model.projects import Org, Project
from terec.model.util import cqlengine_init


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "test", "docker-compose.yaml")


@pytest.fixture(scope="session")
def cassandra(docker_services) -> Session:
    """
    Ensure that Cassandra service is up and responsive and initializes cqlengine (object mapper).
    Returns session (Cassandra connection).
    """

    def is_cassandra_responsive() -> bool:
        try:
            cassandra_session()
            return True
        except Exception as ex:
            logging.warning(ex)
            return False

    docker_services.wait_until_responsive(
        timeout=120.0, pause=3.0, check=lambda: is_cassandra_responsive()
    )
    return cassandra_session()


@pytest.fixture(scope="session")
def cassandra_model(cassandra: Session) -> Session:
    cqlengine_init(cassandra)
    return cassandra


@pytest.fixture(scope="session")
def test_project(cassandra_model) -> Project:
    org = Org.create(name="MyOrg", full_name="My Organisation", url="http://my.org")
    prj = Project.create(org_name=org.name, prj_name="TestProject")
    return prj
