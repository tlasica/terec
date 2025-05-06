import json

from faker import Faker
from fastapi.encoders import jsonable_encoder
from pytest import fixture
from starlette.testclient import TestClient

from assertions import raise_for_status
from random_data import random_test_case_run_info
from terec.api.core import create_app


@fixture(scope="module")
def random_100_test_runs():
    return [random_test_case_run_info() for _ in range(100)]


class TestBenchmarkResultsAPI:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def post_test_results(
        self, org: str, prj: str, suite: str, branch: str, run: int, body: str
    ):
        url = f"/tests/orgs/{org}/projects/{prj}/suites/{suite}/branches/{branch}/runs/{run}/tests"
        return self.api_client.post(url, content=body)

    def test_benchmark_adding_100_test_results(
        self,
        cassandra_model,
        test_project,
        test_suite_run,
        benchmark,
        random_100_test_runs,
    ):
        # prepare random data encoded as json
        tests = random_100_test_runs
        body = jsonable_encoder(tests, exclude_none=True)
        json_body = json.dumps(body)
        # benchmark calling the api
        resp = benchmark(
            self.post_test_results,
            test_project.org,
            test_project.name,
            test_suite_run.suite,
            test_suite_run.branch,
            test_suite_run.run_id,
            json_body,
        )
        raise_for_status(resp)

    def test_benchmark_adding_1000_test_results(
        self, cassandra_model, test_project, test_suite_run, benchmark
    ):
        # prepare random data encoded as json
        tests = [random_test_case_run_info() for _ in range(1000)]
        body = jsonable_encoder(tests, exclude_none=True)
        json_body = json.dumps(body)
        # benchmark calling the api
        resp = benchmark(
            self.post_test_results,
            test_project.org,
            test_project.name,
            test_suite_run.suite,
            test_suite_run.branch,
            test_suite_run.run_id,
            json_body,
        )
        raise_for_status(resp)
