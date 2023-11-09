import json

from fastapi.encoders import jsonable_encoder
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
        # when parsed
        org, project = test_project.org, test_project.name
        suite = "cassandra-3.11-ci"
        build_info = parse_jenkins_build_info(org, project, suite, ci_build_info)
        build_id = build_info.run_id
        # and inserted via api call
        self.check_suite_run_doesnt_exist(org, test_project.name, suite, build_id)
        self.add_test_suite_run(org, build_info)
        # then it should be persisted in the database
        self.check_suite_run_exists(org, test_project.name, suite, build_id)

    def test_should_import_test_runs(self, cassandra_model, test_project):
        # given some build info json from jenkins
        ci_build_info = sample_build_info()
        ci_test_report = sample_build_test_report_suite()
        # when parsed
        org, project = test_project.org, test_project.name
        suite = "cassandra-3.11-fastci"
        build_info = parse_jenkins_build_info(org, project, suite, ci_build_info)
        build_id = build_info.run_id
        test_cases = parse_jenkins_report_suite(ci_test_report)
        # then it should be inserted via api calls
        self.add_test_suite_run(org, build_info)
        self.add_test_results(org, project, suite, build_id, test_cases)

    def add_test_suite_run(self, org: str, build_info):
        build_info_d = build_info.model_dump(exclude_none=True)
        build_info_d["tstamp"] = str(build_info_d["tstamp"])
        url = f"/org/{org}/runs"
        response = self.api_client.post(url, content=json.dumps(build_info_d))
        assert response.is_success, response.text

    def add_test_results(
        self, org: str, project: str, suite: str, run_id: int, test_cases
    ):
        data = jsonable_encoder(test_cases, exclude_none=True)
        url = f"/org/{org}/project/{project}/suite/{suite}/run/{run_id}/tests"
        response = self.api_client.post(url, content=json.dumps(data))
        assert response.is_success, response.text

    def check_suite_run_exists(self, org, project, suite, run_id):
        runs_in_db = TestSuiteRun.objects(
            org=org, project=project, suite=suite, run_id=run_id
        )
        assert len(runs_in_db) == 1

    def check_suite_run_doesnt_exist(self, org, project, suite, run_id):
        runs_in_db = TestSuiteRun.objects(
            org=org, project=project, suite=suite, run_id=run_id
        )
        assert len(runs_in_db) == 0
