from unittest.mock import MagicMock, patch
from terec.ci_jenkins.jenkins_server import JenkinsServer
from terec.api.routers.results import TestCaseRunInfo


def test_jenkins_server_connection():
    cassandra_jenkins_url = "https://ci-cassandra.apache.org/"
    server = JenkinsServer(cassandra_jenkins_url).connect()
    version = server.get_version().split(".")
    assert len(version) >= 3
    assert all([v.isnumeric() for v in version])


def test_suite_test_runs_for_build():
    """
    Test that suite_test_runs_for_build correctly fetches test results using tree parameter
    """
    # Mock responses
    suite_names_response = {"suites": [{"name": "suite1"}, {"name": "suite2"}]}

    test_report_response_1 = {
        "suites": [
            {
                "name": "suite1",
                "cases": [
                    {
                        "className": "org.example.TestClass",
                        "name": "test1",
                        "status": "PASSED",
                    }
                ],
            }
        ]
    }

    test_report_response_2 = {
        "suites": [
            {
                "name": "suite2",
                "cases": [
                    {
                        "className": "org.example.TestClass",
                        "name": "test2",
                        "status": "PASSED",
                    }
                ],
            }
        ]
    }

    # Mock requests
    with patch("requests.get") as mock_get, patch(
        "terec.ci_jenkins.jenkins_server.parse_jenkins_report_suite"
    ) as mock_parse:
        # Create mock responses in order
        mock_get.return_value.json.side_effect = [
            suite_names_response,
            test_report_response_1,
            test_report_response_2,
        ]

        # Create mock parsed results
        mock_parse.side_effect = [
            TestCaseRunInfo(
                test_package="org.example",
                test_suite="suite1",
                test_case="test1",
                test_config="",
                result="PASS",
                className="org.example.TestClass",
                name="test1",
                status="PASSED",
                duration=0,
                stderr="",
                stdout="",
                errorDetails=None,
                errorStackTrace=None,
                skipped=False,
                skippedMessage=None,
            ),
            TestCaseRunInfo(
                test_package="org.example",
                test_suite="suite2",
                test_case="test2",
                test_config="",
                result="PASS",
                className="org.example.TestClass",
                name="test2",
                status="PASSED",
                duration=0,
                stderr="",
                stdout="",
                errorDetails=None,
                errorStackTrace=None,
                skipped=False,
                skippedMessage=None,
            ),
        ]

        server = JenkinsServer("http://test")

        # Test that it fetches results correctly
        results = list(server.suite_test_runs_for_build("job1", 1))

        # Verify we made the correct API calls
        assert mock_get.call_count == 3  # 1 for suite names + 2 for test reports

        # Verify the results are parsed correctly
        assert len(results) == 2
        assert results[0].test_case == "test1"
        assert results[0].test_suite == "suite1"
        assert results[0].result == "PASS"
        assert results[1].test_case == "test2"
