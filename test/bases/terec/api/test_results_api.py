import json

from faker import Faker
from fastapi.testclient import TestClient
from terec.api.core import create_app
from terec.api.routers.results import TestSuiteInfo
from terec.model.projects import Org, Project


def not_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


class TestResultsSuitesApi:

    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def _expect_404(self, uri):
        response = self.api_client.get(uri)
        assert response.status_code == 404

    def test_should_raise_for_not_existing_org(self, cassandra_model) -> None:
        self._expect_404("/org/not-existing/suites")
        self._expect_404("/org/not-existing/projects/a/suites")

    def test_create_suite_in_org(self, cassandra_model):
        # given an organization
        org = Org.create(name=self.fake.company())
        # when 3 suites in project a and 2 in project b are created
        for p in ["a", "b", "a", "a", "b"]:
            suite = self._random_suite(org.name, p)
            response = self.api_client.post(url=f"/org/{org.name}/suites", content=json.dumps(suite))
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
            "org_name": org_name,
            "prj_name": prj_name,
            "suite_name": self.fake.word(),
            "url": self.fake.url()
        }
        TestSuiteInfo.model_validate(ret)
        TestSuiteInfo.model_validate_json(json.dumps(ret))
        return ret


    # def test_get_all_org_projects(self, cassandra_model) -> None:
    #     org = Org.create(name=self.fake.company())
    #     response = self.api_client.get(f"/org/{org.name}/projects")
    #     assert response.is_success
    #     assert response.json() == []
    #     prj_a = {
    #         "org_name": org.name,
    #         "prj_name": "a",
    #         "full_name": "Project A",
    #         "description":  "descr"
    #     }
    #     prj_b = {
    #         "org_name": org.name,
    #         "prj_name": "b",
    #         "full_name": "Project B",
    #         "url": "http://project.b.org"
    #     }
    #     Project.create(**prj_a)
    #     Project.create(**prj_b)
    #     response = self.api_client.get(f"/org/{org.name}/projects")
    #     assert response.is_success
    #     assert len(response.json()) == 2
    #     a = [x for x in response.json() if x["prj_name"] == "a"][0]
    #     b = [x for x in response.json() if x["prj_name"] == "b"][0]
    #     assert not_none(a) == not_none(prj_a)
    #     assert not_none(b) == not_none(prj_b)
    #
    #
    #
    #
    #
