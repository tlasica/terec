import logging
import math
import os
import time

import pytest

from cassandra.cluster import Session

from terec.database import cassandra_session
from terec.model.projects import Org, Project
from terec.model.util import cqlengine_init

# This is to add --keepalive flag when running pytests so that we do not start docker again
# from https://github.com/avast/pytest-docker/issues/46#issuecomment-887408396


def pytest_addoption(parser):
    """Add custom options to pytest.
    Add the --keepalive option for pytest.
    """

    parser.addoption(
        "--keepalive",
        "-K",
        action="store_true",
        default=False,
        help="Keep Docker containers alive",
    )


@pytest.fixture(scope="session")
def keepalive(request):
    """Check if user asked to keep Docker running after the test."""

    return request.config.option.keepalive


@pytest.fixture(scope="session")
def docker_compose_project_name(keepalive, docker_compose_project_name):
    """
    Override `docker_compose_project_name` to make sure that we have a unique project name
    if user asked to keep containers alive. This way we won’t create Docker container every time we will start pytest.
    """

    if keepalive:
        return "pytest-terec"

    return docker_compose_project_name


@pytest.fixture(scope="session")
def docker_cleanup(keepalive, docker_cleanup):
    """
    If user asked to keep Docker alive, make `pytest-docker` execute the `docker-compose version` command.
    This way, Docker container won’t be shut down."""

    if keepalive:
        return "version"

    return docker_cleanup


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
    return cassandra_session(drop_keyspace=True)


@pytest.fixture(scope="session")
def cassandra_model(cassandra: Session) -> Session:
    cqlengine_init(cassandra)
    return cassandra


@pytest.fixture(scope="session")
def test_project(cassandra_model) -> Project:
    org_name = f"org-{math.floor(time.time())}"
    org = Org.create(name=org_name, full_name="My Organisation", url="http://my.org")
    prj = Project.create(org=org.name, name="TestProject")
    return prj
