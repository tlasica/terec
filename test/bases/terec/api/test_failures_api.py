from faker import Faker
from fastapi.testclient import TestClient

from generator import ResultsGenerator
from conftest import random_name
from terec.api.core import create_app


class TestFailuresAPI:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def get_failed_tests(self, org, project, suite, branch):
        url = f"/history/orgs/{org}/projects/{project}/suites/{suite}/failed-tests?branch={branch}"
        return self.api_client.get(url)

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
