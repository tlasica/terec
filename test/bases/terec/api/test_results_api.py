import json

from faker import Faker
from fastapi.testclient import TestClient
from terec.api.core import create_app
from terec.api.routers.results import TestSuiteInfo
from terec.model.projects import Org, Project
from terec.model.results import TestSuite, TestSuiteRun


def not_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def expect_error_404(api_client: TestClient, url: str) -> None:
    response = api_client.get(url)
    assert response.status_code == 404


class TestResultsSuitesApi:
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
            suite = self._random_suite(org.name, p)
            response = self.api_client.post(
                url=f"/org/{org.name}/suites", content=json.dumps(suite)
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

    def _random_suite(self, org_name: str, prj_name: str) -> dict:
        ret = {
            "org": org_name,
            "project": prj_name,
            "suite": self.fake.word(),
            "url": self.fake.url(),
        }
        TestSuiteInfo.model_validate(ret)
        TestSuiteInfo.model_validate_json(json.dumps(ret))
        return ret


class TestSuiteRunsApi:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def test_should_create_run_and_suite_if_not_exists(self):
        org = Org.create(name=self.fake.company())
        new_prj = self.fake.user_name()
        suite_run = self._random_suite_run(org.name, new_prj, "ci", run_id=7)
        response = self.api_client.post(f"/org/{org.name}/runs", content=json.dumps(suite_run))
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
            suite_run = self._random_suite_run(org.name, prj.name, "ci", run_id=run_id)
            response = self.api_client.post(f"/org/{org.name}/runs", content=json.dumps(suite_run))
            assert response.status_code == 200, response.text
        # then they can be found in the db in run_id decreasing order
        runs = TestSuiteRun.objects(org=org.name, project=prj.name, suite="ci")
        assert len(runs) == 5
        assert [x.run_id for x in runs] == [5, 4, 3, 2, 1]

    # TODO: we need to add and test get methods

    def _random_suite_run(self, org_name: str, prj_name:str, suite_name: str, run_id: int) -> dict:
        run = {
            "org": org_name,
            "project": prj_name,
            "suite": suite_name,
            "run_id": run_id,
            "tstamp": str(self.fake.date_time_this_month()),
            "branch": "main",
            "commit": self.fake.md5(),
            "url": self.fake.url(),
            "passed_tests": self.fake.random.randint(10, 100),
            "failed_tests": self.fake.random.randint(1, 10),
            "skipped_tests": self.fake.random.randint(1, 10),
            "duration_sec": self.fake.random.randint(60, 120)
        }
        return run
