import json
from unittest import SkipTest

from faker import Faker
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from conftest import random_name
from .random_data import (
    random_test_suite_info,
    random_test_suite_run_info,
    random_test_case_run_info,
)
from terec.api.core import create_app
from terec.model.projects import Org, Project
from terec.model.results import TestSuite, TestSuiteRun, TestCaseRun


def not_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def expect_error_404(api_client: TestClient, url: str) -> None:
    response = api_client.get(url)
    assert response.status_code == 404


class TestPlotsAPI:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def get_history(self, org, project, suite, branch):
        url = f"history/orgs/{org}/projects/{project}/suites/{suite}/builds?branch={branch}"
        return self.api_client.get(url)

    def test_should_raise_for_not_existing_org(self, cassandra_model) -> None:
        resp = self.get_history("not-existing-org", "p", "s", "main")
        assert not resp.is_success
        assert "Org not found" in resp.text

    def test_should_fail_for_non_existing_project(self, cassandra_model, test_project):
        resp = self.get_history(
            test_project.org, random_name("not-existing-project"), "s", "main"
        )
        assert not resp.is_success
        assert "Project not found" in resp.text

    def test_should_fail_for_non_existing_suite(self, cassandra_model, test_project):
        resp = self.get_history(
            test_project.org, test_project.name, random_name("suite"), "main"
        )
        assert not resp.is_success
        assert "Suite not found" in resp.text

    def add_suite_run(self, test_suite, branch, run_id):
        run = random_test_suite_run_info(
            test_suite.org, test_suite.project, test_suite.suite, run_id=run_id
        )
        run.branch = branch
        response = self.api_client.post(
            f"/tests/orgs/{test_suite.org}/runs", content=run.model_dump_json()
        )
        assert response.status_code == 200, response.text
        return run

    def test_should_return_build(self, cassandra_model, test_suite):
        # given some test suite runs in 3 branches
        branch_a, branch_b, branch_c = [
            random_name(f"branch-{p}") for p in ["a", "b", "c"]
        ]
        runs = [
            self.add_suite_run(test_suite, branch_a, 1),
            self.add_suite_run(test_suite, branch_a, 2),
            self.add_suite_run(test_suite, branch_b, 3),
            self.add_suite_run(test_suite, branch_a, 4),
            self.add_suite_run(test_suite, branch_b, 5),
            self.add_suite_run(test_suite, branch_a, 6),
        ]
        # when we ask for the history for each of the branches
        resp_a, resp_b, resp_c = [
            self.get_history(test_suite.org, test_suite.project, test_suite.suite, b)
            for b in [branch_a, branch_b, branch_c]
        ]
        for resp in [resp_a, resp_b, resp_c]:
            assert resp.is_success, resp.text
        # then history on branch c is empty
        history_a = resp_a.json()
        history_b = resp_b.json()
        history_c = resp_c.json()
        assert 4 == len(history_a)
        assert {branch_a} == {run["branch"] for run in history_a}
        assert 2 == len(history_b)
        assert {branch_b} == {run["branch"] for run in history_b}
        assert 0 == len(history_c)
