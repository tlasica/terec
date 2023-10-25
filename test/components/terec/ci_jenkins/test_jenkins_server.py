from terec.ci_jenkins.jenkins_server import JenkinsServer


def test_jenkins_server_connection():
    cassandra_jenkins_url = "https://ci-cassandra.apache.org/"
    server = JenkinsServer(cassandra_jenkins_url).connect()
    version = server.get_version().split(".")
    assert len(version) >= 3
    assert all([v.isnumeric() for v in version])
