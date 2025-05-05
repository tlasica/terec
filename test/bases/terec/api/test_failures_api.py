import pytest
from faker import Faker
from fastapi.testclient import TestClient

from generator import ResultsGenerator, generate_suite_with_test_runs
from conftest import random_name
from terec.api.core import create_app
from terec.model.results import TestCaseRun


class TestFailuresGetFailedTestsAPI:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def get_failed_tests(self, org, project, suite, branch):
        url = f"/history/orgs/{org}/projects/{project}/suites/{suite}/failed-tests"
        params = {"branch": branch}
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

    def get_test_runs(
        self, org, project, suite, branch, t_package, t_class=None, t_case=None
    ):
        url = f"/history/orgs/{org}/projects/{project}/suites/{suite}/test-runs"
        q_params = {"branch": branch, "test_package": t_package}
        if t_class:
            q_params["test_class"] = t_class
        if t_case:
            q_params["test_case"] = t_case
        return self.api_client.get(url, params=q_params)

    def test_should_raise_for_not_existing_org(self, cassandra_model) -> None:
        resp = self.get_test_runs(
            "not-existing-org", "p", "s", "main", "org.example.test"
        )
        assert not resp.is_success
        assert "Org not found" in resp.text

    def test_should_fail_for_non_existing_project(self, cassandra_model, test_project):
        resp = self.get_test_runs(
            test_project.org,
            random_name("not-existing-project"),
            "s",
            "main",
            "org.example.test",
        )
        assert not resp.is_success
        assert "Project not found" in resp.text

    def test_should_fail_for_non_existing_suite(self, cassandra_model, test_project):
        resp = self.get_test_runs(
            test_project.org,
            test_project.name,
            random_name("suite"),
            "main",
            "org.example.test",
        )
        assert not resp.is_success
        assert "Suite not found" in resp.text

    def test_should_return_single_test_history(self, cassandra_model, test_project):
        # given some generated data with failed tests
        branch = "main"
        suite, suite_runs, test_runs = generate_suite_with_test_runs(
            test_project.org, test_project.name, branch=branch
        )
        assert len(test_runs) > 0
        # when we get single test history
        the_test: TestCaseRun = test_runs[0]
        resp = self.get_test_runs(
            suite.org,
            suite.project,
            suite.suite,
            "main",
            t_package=the_test.test_package,
            t_class=the_test.test_suite,
            t_case=the_test.test_case,
        )
        assert resp.is_success, resp.text
        # then it should have only one test case
        # then we get history for all generated runs
        test_case_runs = [x["test_run"] for x in resp.json()]
        expected_count = len([x for x in test_runs if x.is_same_test_case(the_test)])
        assert (
            len(resp.json()) == expected_count
        ), f"the_test: {str(the_test)} but got: {test_case_runs}"

    def test_should_return_class_history(self, cassandra_model, test_project):
        # given some generated data with failed tests
        suite, suite_runs, test_runs = generate_suite_with_test_runs(
            test_project.org, test_project.name, branch="main"
        )
        assert len(test_runs) > 0
        # when we get single test history
        the_test: TestCaseRun = test_runs[0]
        resp = self.get_test_runs(
            suite.org,
            suite.project,
            suite.suite,
            "main",
            t_package=the_test.test_package,
            t_class=the_test.test_suite,
        )
        assert resp.is_success, resp.text
        # then we get history for all generated runs
        expected_count = len([x for x in test_runs if x.is_same_test_suite(the_test)])
        assert len(resp.json()) == expected_count, resp.text

    def test_should_return_package_history(self, cassandra_model, test_project):
        # given some generated data with failed tests
        suite, suite_runs, test_runs = generate_suite_with_test_runs(
            test_project.org, test_project.name, branch="main"
        )
        assert len(test_runs) > 0
        # when we get single test history
        the_test: TestCaseRun = test_runs[0]
        resp = self.get_test_runs(
            suite.org,
            suite.project,
            suite.suite,
            "main",
            t_package=the_test.test_package,
        )
        assert resp.is_success, resp.text
        # then we get history for all generated runs
        expected_count = len(
            [x for x in test_runs if x.test_package == the_test.test_package]
        )
        assert len(resp.json()) == expected_count, resp.text


class TestFailuresCheckTestRunAPI:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def get_test_run_check(
        self,
        org,
        project,
        suite,
        branch,
        run_id,
        t_package,
        t_class,
        t_case,
        t_config,
        check_branch=None,
        check_suite=None,
    ):
        url = f"/history/orgs/{org}/projects/{project}/suites/{suite}/test-run-check"
        q_params = {
            "branch": branch,
            "run_id": run_id,
            "test_package": t_package,
            "test_class": t_class,
            "test_case": t_case,
            "test_config": t_config,
        }
        if check_suite:
            q_params["check_suite"] = check_suite
        if check_branch:
            q_params["check_branch"] = check_branch
        return self.api_client.get(url, params=q_params)

    TEST_FAIL = {
        "result": "FAIL",
        "error_details": "error happened",
        "error_stacktrace": "some stack trace",
    }

    TEST_PASS = {
        "result": "PASS",
    }

    @pytest.fixture()
    def gen_with_suite_runs(self, cassandra_model, test_project):
        suite_name = random_name("suite")
        gen = ResultsGenerator(num_tests=4)
        suite = gen.suite(test_project.org, test_project.name, suite_name)
        suite_runs = [gen.suite_run(suite, "main", n) for n in range(1, 5)]
        assert len(suite_runs) == 4
        assert suite_runs[0].run_id == 1 and suite_runs[-1].run_id == 4
        return gen

    def test_check_regression(self, gen_with_suite_runs):
        # given a history of test runs with some failure FPPF
        gen = gen_with_suite_runs
        case_template = gen.test_case_template()
        history = [
            gen.test_case_run(gen.get_suite_run(1), case_template, self.TEST_FAIL),
            gen.test_case_run(gen.get_suite_run(2), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(3), case_template, self.TEST_PASS),
            gen.test_case_run(gen.get_suite_run(4), case_template, self.TEST_FAIL),
        ]
        # when we make a test run check call
        failed_test = history[-1]
        resp = self.get_test_run_check(
            failed_test.org,
            failed_test.project,
            failed_test.suite,
            failed_test.branch,
            failed_test.run_id,
            failed_test.test_package,
            failed_test.test_suite,
            failed_test.test_case,
            failed_test.test_config,
        )
        # then it contains valid information in the reponse
        assert resp.is_success, resp.text
        data = resp.json()
        assert data["is_known_failure"]
        assert len(data["similar_failures"]) == 1
        assert data["summary"]["num_runs"] == 3
        assert data["summary"]["num_same_fail"] == 1
        assert data["summary"]["num_diff_fail"] == 0
        assert data["summary"]["num_skip"] == 0
        assert data["summary"]["num_pass"] == 2

    def test_get_test_run_check(self, cassandra_model, test_project):
        suite, suite_runs, test_runs = generate_suite_with_test_runs(
            test_project.org, test_project.name, branch="main"
        )
        the_test: TestCaseRun = next((x for x in test_runs if x.result == "FAIL"))
        assert the_test is not None

        resp = self.get_test_run_check(
            the_test.org,
            the_test.project,
            the_test.suite,
            the_test.branch,
            the_test.run_id,
            the_test.test_package,
            the_test.test_suite,
            the_test.test_case,
            the_test.test_config,
            check_branch="main",
        )

        assert resp.is_success, resp.text

    def test_check_known_fail_on_same_branch(self, cassandra_model, test_project):
        pass

    def test_check_new_fail_on_same_branch(self, cassandra_model, test_project):
        pass

    # def test_check_known_fail_on_other_branch(self, cassandra_model, test_project):
    #     pass
    #
    # def test_check_new_fail_on_other_branch(self, cassandra_model, test_project):
    #     pass
