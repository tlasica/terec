import json
from unittest import SkipTest

from faker import Faker
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from terec.api.routers.results import TestCaseRunInfo
from .random_data import random_test_suite_info, random_test_suite_run_info, random_test_case_run_info
from terec.api.core import create_app
from terec.model.projects import Org, Project
from terec.model.results import TestSuite, TestSuiteRun, TestCaseRun


def not_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def expect_error_404(api_client: TestClient, url: str) -> None:
    response = api_client.get(url)
    assert response.status_code == 404


class TestResultsSuitesAPI:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def test_should_raise_for_not_existing_org(self, cassandra_model) -> None:
        expect_error_404(self.api_client, "/org/not-existing/suites")
        expect_error_404(self.api_client, "/org/not-existing/projects/a/suites")

    def test_create_suite_in_org(self, cassandra_model):
        # given an organization
        org = Org.create(name=self.fake.company())
        # when 3 suites in project a and 2 in project b are created
        for p in ["a", "b", "a", "a", "b"]:
            suite = random_test_suite_info(org.name, p)
            response = self.api_client.post(
                url=f"/org/{org.name}/suites", content=suite.model_dump_json()
            )
            assert response.status_code == 200, response.text
        # then we can retrieve them
        self._expect_get_to_return_n(url=f"/org/{org.name}/suites", n=5)
        self._expect_get_to_return_n(url=f"/org/{org.name}/projects/a/suites", n=3)
        self._expect_get_to_return_n(url=f"/org/{org.name}/projects/b/suites", n=2)

    def _expect_get_to_return_n(self, url: str, n: int) -> None:
        response = self.api_client.get(url=url)
        assert response.status_code == 200, response.text
        assert len(response.json()) == n, response.json()


class TestSuiteRunsAPI:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def test_should_create_run_and_suite_if_not_exists(self):
        org = Org.create(name=self.fake.company())
        new_prj = self.fake.user_name()
        suite_run = random_test_suite_run_info(org.name, new_prj, "ci", run_id=7)
        response = self.api_client.post(
            f"/org/{org.name}/runs", content=suite_run.model_dump_json()
        )
        assert response.status_code == 200, response.text
        # then the suit is created
        suite = TestSuite.objects(org=org.name, project=new_prj, suite="ci")
        assert len(suite) == 1
        # and the run is created as well
        runs = TestSuiteRun.objects(org=org.name, project=new_prj, suite="ci")
        assert len(runs) == 1
        assert runs[0].run_id == 7, f"Expected run with id 7 but got: {runs[0]}"

    def test_should_create_runs_in_existing_suite(self):
        # given an existing suite
        org = Org.create(name=self.fake.company())
        prj = Project.create(org=org.name, name=self.fake.user_name())
        TestSuite.create(org=org.name, project=self.fake.user_name(), suite="ci")
        # when we add some test suite runs
        for run_id in range(1, 6):
            run = random_test_suite_run_info(org.name, prj.name, "ci", run_id=run_id)
            response = self.api_client.post(
                f"/org/{org.name}/runs", content=run.model_dump_json()
            )
            assert response.status_code == 200, response.text
        # then they can be found in the db in run_id decreasing order
        runs = TestSuiteRun.objects(org=org.name, project=prj.name, suite="ci")
        assert len(runs) == 5
        assert [x.run_id for x in runs] == [5, 4, 3, 2, 1]
        # and have fields set
        suite_run: TestSuiteRun = runs[0]
        assert suite_run.pass_count is not None
        assert suite_run.fail_count is not None
        assert suite_run.skip_count is not None
        assert suite_run.total_count is not None


    # TODO: we need to add and test get methods


class TestCaseResultsAPI:

    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def post_test_results(self, org: str, prj: str, suite: str, run: int, body: str):
        url = f"/org/{org}/project/{prj}/suite/{suite}/run/{run}/tests"
        return self.api_client.post(url, content=body)

    def test_should_fail_for_empty_list_of_tests(self, cassandra_model, test_project, test_suite_run):
        resp = self.post_test_results(test_project.org, test_project.name, test_suite_run.suite, test_suite_run.run_id, "[]")
        assert 400 == resp.status_code, resp.text

    def test_should_fail_for_non_existing_org(self, cassandra_model):
        body = jsonable_encoder([random_test_case_run_info()], exclude_none=True)
        resp = self.post_test_results("non-existing-org", "p", "suite", 3, json.dumps(body))
        assert 404 == resp.status_code, resp.text
        assert "Org not found" in resp.text

    def test_should_fail_for_non_existing_project(self, cassandra_model, test_project):
        body = jsonable_encoder([random_test_case_run_info()], exclude_none=True)
        resp = self.post_test_results(test_project.org, "non-existing-project", "suite", 3, json.dumps(body))
        assert 404 == resp.status_code, resp.text
        assert "Project not found" in resp.text

    def test_should_fail_for_non_existing_suite(self, cassandra_model, test_project):
        body = jsonable_encoder([random_test_case_run_info()], exclude_none=True)
        resp = self.post_test_results(test_project.org, test_project.name, "non-existing-suite", 3, json.dumps(body))
        assert 404 == resp.status_code, resp.text
        assert "Suite not found" in resp.text

    def test_should_fail_for_non_existing_suite_run(self, cassandra_model, test_project, test_suite):
        body = jsonable_encoder([random_test_case_run_info()], exclude_none=True)
        resp = self.post_test_results(test_project.org, test_project.name, test_suite.suite, 1, json.dumps(body))
        assert 404 == resp.status_code, resp.text
        assert "Suite run not found" in resp.text

    def test_should_write_test_results(self, cassandra_model, test_project, test_suite_run):
        # given list of test results in some existing suite run
        tests = [random_test_case_run_info() for _ in range(7)]
        # when it is imported via api call
        body = jsonable_encoder(tests, exclude_none=True)
        resp = self.post_test_results(test_project.org, test_project.name, test_suite_run.suite, test_suite_run.run_id, json.dumps(body))
        assert resp.is_success, resp.text
        # then it is correctly stored in the database
        loaded = TestCaseRun.objects(org=test_project.org, project=test_project.name, suite=test_suite_run.suite, run_id=test_suite_run.run_id)
        assert len(loaded) == len(tests)


class TestIgnoreSuiteRunAPI:
    def test_ignore_suite_run(self, cassandra_model, test_project):
        # create suite run
        # should not be ignored by default
        # mark it ignored and check it is indeed
        # remove ignored status and check it is not ignored
        raise SkipTest("ignore api not implemented")
