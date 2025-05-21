import math
import os
import pytest
import time


from cassandra.cluster import Session
from fastapi.testclient import TestClient
from loguru import logger

from terec.database import cassandra_session
from terec.model.projects import Org, Project, generate_org_tokens, OrgToken
from terec.model.results import TestSuiteRun, TestSuite
from terec.model.util import cqlengine_init, model_to_dict


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
    pytest_root = str(pytestconfig.rootpath)
    if pytest_root.endswith("/test"):
        return os.path.join(pytest_root, "docker-compose.yaml")
    else:
        return os.path.join(pytest_root, "test", "docker-compose.yaml")


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
            logger.warning(ex)
            return False

    docker_services.wait_until_responsive(
        timeout=120.0, pause=3.0, check=lambda: is_cassandra_responsive()
    )
    return cassandra_session(drop_keyspace=True)


@pytest.fixture(scope="session")
def cassandra_model(cassandra: Session) -> Session:
    cqlengine_init(cassandra)
    return cassandra


@pytest.fixture(scope="class")
def public_project(cassandra_model) -> Project:
    org_name = random_name("org")
    org = Org.create(name=org_name, full_name="My Organisation", url="http://my.org")
    prj = Project.create(org=org.name, name="TestProject")
    return prj


@pytest.fixture(scope="class")
def private_project(cassandra_model) -> tuple[Project, dict[str, str]]:
    org_name = random_name("org")
    org = Org.create(
        name=org_name, full_name="My Organisation", url="http://my.org", private=True
    )
    tokens = {}
    for token, token_data in generate_org_tokens(org.name):
        OrgToken.create(**model_to_dict(token_data))
        tokens[token_data.token_name] = token
    prj = Project.create(org=org.name, name="TestProject")
    return prj, tokens


@pytest.fixture
def public_project_suite(public_project) -> TestSuite:
    suite_name = random_name("suite")
    suite = TestSuite.create(
        org=public_project.org, project=public_project.name, suite=suite_name
    )
    return suite


@pytest.fixture
def public_project_suite_run(public_project_suite) -> TestSuiteRun:
    run_id = math.floor(time.time())
    run = TestSuiteRun.create(
        org=public_project_suite.org,
        project=public_project_suite.project,
        suite=public_project_suite.suite,
        branch="main",
        run_id=run_id,
    )
    return run


@pytest.fixture(scope="session")
def api_client() -> TestClient:
    from terec.api.core import create_app

    api_app = create_app()
    return TestClient(api_app)


def random_name(prefix: str) -> str:
    return f"{prefix}-{math.floor(1000 * time.time())}"
