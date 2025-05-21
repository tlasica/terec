import pytest
from pytest import fixture


@fixture
def cassandra_ci():
    from terec.ci_jenkins.jenkins_server import JenkinsServer

    cassandra_jenkins_url = "https://ci-cassandra.apache.org/"
    return JenkinsServer(cassandra_jenkins_url)


@fixture
def jenkins_server(docker_services):
    from terec.ci_jenkins.jenkins_server import JenkinsServer

    return JenkinsServer("http://localhost:8083/")


# @pytest.mark.skip(reason="This test uses external CI that is not reliable.")
def test_jenkins_server_connection(jenkins_server):
    version = jenkins_server.connect().get_version().split(".")
    assert len(version) >= 3
    assert all([v.isnumeric() for v in version])


# FIXME: start own jenkins in docker
# FIXME: mark as integration test
# FIXME: possibly use some kind of "last available" build
@pytest.mark.skip(reason="This test is long and sensitive as it uses hardcoded build.")
def test_get_suite_test_runs(cassandra_ci):
    job_name = "Cassandra-5.0"
    build_num = 451
    suites = list(
        cassandra_ci.suite_test_runs_for_build(
            job_name=job_name, build_num=build_num, limit=2
        )
    )
    assert len(suites) == 2
