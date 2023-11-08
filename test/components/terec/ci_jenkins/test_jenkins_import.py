import json

from starlette.testclient import TestClient

from terec.ci_jenkins.build_info_parser import parse_jenkins_build_info
from terec.ci_jenkins.report_parser import parse_jenkins_report_suite
from terec.model.results import TestSuiteRun
from .sample_data.build_info import sample_build_info
from .sample_data.build_test_report import sample_build_test_report_suite
from terec.api.core import create_app


class TestJenkinsImport:
    """
    Test importing jenkins data (exposed via jenkins API) into the database
    by using parsers and api calls. This is kind of integration test.

    FIXME: I am not sure if this is valid place for this test
    """

    api_app = create_app()
    api_client = TestClient(api_app)

    def test_should_import_build(self, cassandra_model, test_project):
        # given some build info json from jenkins
        ci_build_info = sample_build_info()
        # when parsed and inserted via api call
        org = test_project.org
        suite = "cassandra-3.11-ci"
        runs_in_db = TestSuiteRun.objects(org=org, project=test_project.name, suite=suite)
        assert len(runs_in_db) == 0
        build_info = parse_jenkins_build_info(org=org, project=test_project.name, suite=suite, build=ci_build_info)
        build_info_d = build_info.model_dump(exclude_none=True)
        build_info_d["tstamp"] = str(build_info_d["tstamp"])
        response = self.api_client.post(
            f"/org/{org}/runs", content=json.dumps(build_info_d)
        )
        # then it should be persisted in the database
        assert response.is_success, response.text
        runs_in_db = TestSuiteRun.objects(org=org, project=test_project.name, suite=suite)
        assert len(runs_in_db) == 1

    def test_should_import_test_runs(self, cassandra_model, test_project):
        # given some build info json from jenkins
        ci_build_info = sample_build_info()
        ci_test_report = sample_build_test_report_suite()
        # when parsed and inserted via api call
        org = test_project.org
        suite = "cassandra-3.11-fastci"
        runs_in_db = TestSuiteRun.objects(org=org, project=test_project.name, suite=suite)
        assert len(runs_in_db) == 0
        build_info = parse_jenkins_build_info(org=org, project=test_project.name, suite=suite, build=ci_build_info)
        build_info_d = build_info.model_dump(exclude_none=True)
        build_info_d["tstamp"] = str(build_info_d["tstamp"])
        response = self.api_client.post(
            f"/org/{org}/runs", content=json.dumps(build_info_d)
        )
        test_cases = parse_jenkins_report_suite(ci_test_report)

        # then it should be persisted in the database
        assert response.is_success, response.text
        runs_in_db = TestSuiteRun.objects(org=org, project=test_project.name, suite=suite)
        assert len(runs_in_db) == 1
        pass