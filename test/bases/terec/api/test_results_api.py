import pytest
import json
from unittest import SkipTest

from fastapi.encoders import jsonable_encoder

from conftest import random_name
from generator import generate_suite_with_test_runs
from .random_data import (
    random_test_suite_info,
    random_test_suite_run_info,
    random_test_case_run_info,
)
from terec.model.projects import Org, Project
from terec.model.results import TestSuite, TestSuiteRun, TestCaseRun, TestCaseRunStatus


def not_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def expect_error_404(api_client, url: str) -> None:
    response = api_client.get(url)
    assert response.status_code == 404


@pytest.mark.usefixtures("api_client")
class TestResultsSuitesAPI:
    @pytest.fixture(autouse=True)
    def inject_client(self, api_client):
        self.api_client = api_client

    def test_should_raise_for_not_existing_org(self, cassandra_model) -> None:
        expect_error_404(self.api_client, "/org/not-existing/suites")
        expect_error_404(self.api_client, "/org/not-existing/projects/a/suites")

    def test_create_suite_in_org(self, cassandra_model, org_name):
        # given an organization
        org = Org.create(name=org_name)
        # when 3 suites in project a and 2 in project b are created
        url = f"/tests/orgs/{org.name}/suites"
        for p in ["a", "b", "a", "a", "b"]:
            suite = random_test_suite_info(org.name, p)
            response = self.api_client.post(url, content=suite.model_dump_json())
            assert response.status_code == 200, response.text
        # then we can retrieve them
        self._expect_get_to_return_n(url=f"/tests/orgs/{org.name}/suites", n=5)
        self._expect_get_to_return_n(
            url=f"/tests/orgs/{org.name}/projects/a/suites", n=3
        )
        self._expect_get_to_return_n(
            url=f"/tests/orgs/{org.name}/projects/b/suites", n=2
        )

    def _expect_get_to_return_n(self, url: str, n: int) -> None:
        response = self.api_client.get(url=url)
        assert response.status_code == 200, response.text
        assert len(response.json()) == n, response.json()


@pytest.mark.usefixtures("api_client")
class TestSuiteRunsAPI:
    @pytest.fixture(autouse=True)
    def inject_client(self, api_client):
        self.api_client = api_client

    def post_suite_run(self, org_name, suite_run_info):
        url = f"/tests/orgs/{org_name}/runs"
        return self.api_client.post(url, content=suite_run_info.model_dump_json())

    def test_should_fail_create_on_non_existing_project(
        self, cassandra_model, org_name
    ):
        org = Org.create(name=org_name)
        project = random_name("non-existing-project")
        suite_run = random_test_suite_run_info(org.name, project, "ci", run_id=7)
        response = self.post_suite_run(org.name, suite_run)
        assert not response.is_success

    def test_should_create_run_and_suite_if_not_exists(self, cassandra_model, org_name):
        org = Org.create(name=org_name)
        prj = Project.create(org=org.name, name="a")
        suite_run = random_test_suite_run_info(org.name, prj.name, "ci", run_id=7)
        response = self.post_suite_run(org.name, suite_run)
        assert response.status_code == 200, response.text
        # then the suite is created
        suite = TestSuite.objects(org=org.name, project=prj.name, suite="ci")
        assert len(suite) == 1
        # and the run is created as well
        runs = TestSuiteRun.objects(org=org.name, project=prj.name, suite="ci")
        assert len(runs) == 1
        assert runs[0].run_id == 7, f"Expected run with id 7 but got: {runs[0]}"

    def test_should_create_runs_in_existing_suite(self, cassandra_model, org_name):
        # given an existing suite
        org = Org.create(name=org_name)
        prj = Project.create(org=org.name, name="a")
        TestSuite.create(org=org.name, project=prj.name, suite="ci")
        # when we add some test suite runs
        for run_id in range(1, 6):
            run = random_test_suite_run_info(org.name, prj.name, "ci", run_id=run_id)
            response = self.post_suite_run(org.name, run)
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


@pytest.mark.usefixtures("api_client")
class TestCaseResultsAPI:
    @pytest.fixture(autouse=True)
    def inject_client(self, api_client):
        self.api_client = api_client

    def post_test_results(
        self, org: str, prj: str, suite: str, branch: str, run: int, body: str
    ):
        url = f"/tests/orgs/{org}/projects/{prj}/suites/{suite}/branches/{branch}/runs/{run}/tests"
        return self.api_client.post(url, content=body)

    def get_test_results(
        self,
        org: str,
        prj: str,
        suite: str,
        branch: str,
        run: int,
        result: TestCaseRunStatus = None,
    ):
        url = f"/tests/orgs/{org}/projects/{prj}/suites/{suite}/branches/{branch}/runs/{run}/tests"
        params = {"result": result.upper()} if result else {}
        return self.api_client.get(url, params=params)

    def test_should_fail_for_empty_list_of_tests(
        self, cassandra_model, public_project, public_project_suite_run
    ):
        resp = self.post_test_results(
            public_project.org,
            public_project.name,
            public_project_suite_run.suite,
            public_project_suite_run.branch,
            public_project_suite_run.run_id,
            "[]",
        )
        assert 400 == resp.status_code, resp.text

    def test_should_fail_for_non_existing_org(self, cassandra_model):
        body = jsonable_encoder([random_test_case_run_info()], exclude_none=True)
        resp = self.post_test_results(
            "non-existing-org", "p", "branch", "suite", 3, json.dumps(body)
        )
        assert 404 == resp.status_code, resp.text
        assert "Org not found" in resp.text

    def test_should_fail_for_non_existing_project(
        self, cassandra_model, public_project
    ):
        body = jsonable_encoder([random_test_case_run_info()], exclude_none=True)
        resp = self.post_test_results(
            public_project.org,
            "non-existing-project",
            "branch",
            "suite",
            3,
            json.dumps(body),
        )
        assert 404 == resp.status_code, resp.text
        assert "Project not found" in resp.text

    def test_should_fail_for_non_existing_suite(self, cassandra_model, public_project):
        body = jsonable_encoder([random_test_case_run_info()], exclude_none=True)
        resp = self.post_test_results(
            public_project.org,
            public_project.name,
            random_name("non-existing-suite"),
            "some-branch",
            3,
            json.dumps(body),
        )
        assert 404 == resp.status_code, resp.text
        assert "Suite not found" in resp.text

    def test_should_fail_for_non_existing_suite_run(
        self, cassandra_model, public_project, public_project_suite
    ):
        body = jsonable_encoder([random_test_case_run_info()], exclude_none=True)
        resp = self.post_test_results(
            public_project.org,
            public_project.name,
            public_project_suite.suite,
            "some-branch",
            1,
            json.dumps(body),
        )
        assert 404 == resp.status_code, resp.text
        assert "Suite run not found" in resp.text

    def test_should_write_test_results(
        self, cassandra_model, public_project, public_project_suite_run
    ):
        # given list of test results in some existing suite run
        tests = [random_test_case_run_info() for _ in range(7)]
        # when it is imported via api call
        body = jsonable_encoder(tests, exclude_none=True)
        resp = self.post_test_results(
            public_project.org,
            public_project.name,
            public_project_suite_run.suite,
            public_project_suite_run.branch,
            public_project_suite_run.run_id,
            json.dumps(body),
        )
        assert resp.is_success, resp.text
        # then it is correctly stored in the database
        loaded = TestCaseRun.objects(
            org=public_project.org,
            project=public_project.name,
            suite=public_project_suite_run.suite,
            branch=public_project_suite_run.branch,
            run_id=public_project_suite_run.run_id,
        )
        assert len(loaded) == len(tests)

    def test_should_get_test_results(self, cassandra_model, public_project):
        org, project = public_project.org, public_project.name
        branch = "main"
        suite, suite_runs, test_runs = generate_suite_with_test_runs(
            org, project, branch=branch, num_runs=3
        )
        run_id = suite_runs[0].run_id
        resp = self.get_test_results(
            suite.org,
            suite.project,
            suite.suite,
            branch,
            run_id,
            result=None,
        )
        assert resp.is_success, resp.text
        run_tests = [x for x in test_runs if x.run_id == run_id]
        assert len(run_tests) == len(resp.json())

    def test_should_get_test_results_filtered_by_status(
        self, cassandra_model, public_project
    ):
        org, project = public_project.org, public_project.name
        branch = "main"
        suite, suite_runs, test_runs = generate_suite_with_test_runs(
            org, project, branch=branch
        )
        run_id = suite_runs[0].run_id
        resp = self.get_test_results(
            suite.org,
            suite.project,
            suite.suite,
            branch,
            suite_runs[0].run_id,
            result=TestCaseRunStatus.FAIL,
        )
        assert resp.is_success, resp.text
        run_tests = [
            x
            for x in test_runs
            if x.run_id == run_id and x.result == TestCaseRunStatus.FAIL
        ]
        assert len(run_tests) == len(resp.json())


@pytest.mark.usefixtures("api_client")
class TestIgnoreSuiteRunAPI:
    @pytest.fixture(autouse=True)
    def inject_client(self, api_client):
        self.api_client = api_client

    def test_ignore_suite_run(self, cassandra_model, public_project):
        # create suite run
        # should not be ignored by default
        # mark it ignored and check it is indeed
        # remove ignored status and check it is not ignored
        raise SkipTest("ignore api not implemented")
