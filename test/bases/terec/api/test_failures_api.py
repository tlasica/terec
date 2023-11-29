from faker import Faker
from fastapi.testclient import TestClient

from generator import ResultsGenerator
from conftest import random_name
from terec.api.core import create_app
from terec.model.results import TestCaseRun


class TestFailuresGetFailedTestsAPI:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def get_failed_tests(self, org, project, suite, branch):
        url = f"/history/orgs/{org}/projects/{project}/suites/{suite}/failed-tests"
        params = {
            "branch": branch
        }
        return self.api_client.get(url, params=params)

    def test_should_raise_for_not_existing_org(self, cassandra_model) -> None:
        resp = self.get_failed_tests("not-existing-org", "p", "s", "main")
        assert not resp.is_success
        assert "Org not found" in resp.text

    def test_should_fail_for_non_existing_project(self, cassandra_model, test_project):
        resp = self.get_failed_tests(
            test_project.org, random_name("not-existing-project"), "s", "main"
        )
        assert not resp.is_success
        assert "Project not found" in resp.text

    def test_should_fail_for_non_existing_suite(self, cassandra_model, test_project):
        resp = self.get_failed_tests(
            test_project.org, test_project.name, random_name("suite"), "main"
        )
        assert not resp.is_success
        assert "Suite not found" in resp.text

    def test_should_return_failed_tests(self, cassandra_model, test_project):
        # given some generated data with failed tests
        gen = ResultsGenerator()
        suite_name = random_name("suite")
        suite = gen.suite(test_project.org, test_project.name, suite_name)
        runs = [gen.suite_run(suite, "main", n) for n in range(1, 10)]
        for r in runs:
            gen.test_case_runs(r)
        # when we get failed tests via api
        resp = self.get_failed_tests(suite.org, suite.project, suite.suite, "main")
        assert resp.is_success, resp.text
        # then we get same number as generated
        expected_count = sum(x.fail_count for x in runs)
        assert len(resp.json()) == expected_count


class TestFailuresGetTestRunsAPI:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def get_test_runs(self, org, project, suite, branch, t_package, t_class=None, t_case=None):
        url = f"/history/orgs/{org}/projects/{project}/suites/{suite}/test-runs"
        q_params = {
            "branch": branch,
            "test_package": t_package
        }
        if t_class:
            q_params["test_class"] = t_class
        if t_case:
            q_params["test_case"] = t_case
        return self.api_client.get(url, params=q_params)

    def test_should_raise_for_not_existing_org(self, cassandra_model) -> None:
        resp = self.get_test_runs("not-existing-org", "p", "s", "main", "org.example.test")
        assert not resp.is_success
        assert "Org not found" in resp.text

    def test_should_fail_for_non_existing_project(self, cassandra_model, test_project):
        resp = self.get_test_runs(
            test_project.org, random_name("not-existing-project"), "s", "main", "org.example.test"
        )
        assert not resp.is_success
        assert "Project not found" in resp.text

    def test_should_fail_for_non_existing_suite(self, cassandra_model, test_project):
        resp = self.get_test_runs(
            test_project.org, test_project.name, random_name("suite"), "main", "org.example.test"
        )
        assert not resp.is_success
        assert "Suite not found" in resp.text

    def test_should_return_single_test_history(self, cassandra_model, test_project):
        # given some generated data with failed tests
        gen = ResultsGenerator()
        suite_name = random_name("suite")
        suite = gen.suite(test_project.org, test_project.name, suite_name)
        suite_runs = [gen.suite_run(suite, "main", n) for n in range(1, 10)]
        test_runs: list[TestCaseRun] = []
        for r in suite_runs:
            test_runs += gen.test_case_runs(r)
        assert len(test_runs) > 0
        # when we get single test history
        the_test: TestCaseRun = test_runs[0]
        resp = self.get_test_runs(suite.org, suite.project, suite.suite, "main",
                                  t_package=the_test.test_package,
                                  t_class=the_test.test_suite,
                                  t_case=the_test.test_case)
        assert resp.is_success, resp.text
        # then it should have only one test case
        # then we get history for all generated runs
        test_case_runs = [x["test_run"] for x in resp.json()]
        expected_count = len([x for x in test_runs if x.is_same_test_case(the_test)])
        assert len(resp.json()) == expected_count, f"the_test: {str(the_test)} but got: {test_case_runs}"

    def test_should_return_class_history(self, cassandra_model, test_project):
        # given some generated data with failed tests
        gen = ResultsGenerator()
        suite_name = random_name("suite")
        suite = gen.suite(test_project.org, test_project.name, suite_name)
        suite_runs = [gen.suite_run(suite, "main", n) for n in range(1, 10)]
        test_runs: list[TestCaseRun] = []
        for r in suite_runs:
            test_runs += gen.test_case_runs(r)
        assert len(test_runs) > 0
        # when we get single test history
        the_test: TestCaseRun = test_runs[0]
        resp = self.get_test_runs(suite.org, suite.project, suite.suite, "main",
                                  t_package=the_test.test_package,
                                  t_class=the_test.test_suite)
        assert resp.is_success, resp.text
        # then we get history for all generated runs
        expected_count = len([x for x in test_runs if x.is_same_test_suite(the_test)])
        assert len(resp.json()) == expected_count, resp.text

    def test_should_return_package_history(self, cassandra_model, test_project):
        # given some generated data with failed tests
        gen = ResultsGenerator()
        suite_name = random_name("suite")
        suite = gen.suite(test_project.org, test_project.name, suite_name)
        suite_runs = [gen.suite_run(suite, "main", n) for n in range(1, 10)]
        test_runs: list[TestCaseRun] = []
        for r in suite_runs:
            test_runs += gen.test_case_runs(r)
        assert len(test_runs) > 0
        # when we get single test history
        the_test: TestCaseRun = test_runs[0]
        resp = self.get_test_runs(suite.org, suite.project, suite.suite, "main",
                                  t_package=the_test.test_package)
        assert resp.is_success, resp.text
        # then we get history for all generated runs
        expected_count = len([x for x in test_runs if x.test_package == the_test.test_package])
        assert len(resp.json()) == expected_count, resp.text
