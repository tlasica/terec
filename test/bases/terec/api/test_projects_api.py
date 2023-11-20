import json

from faker import Faker
from fastapi.testclient import TestClient
from terec.api.core import create_app
from terec.api.routers.projects import OrgInfo
from terec.model.projects import Org, Project


def not_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


class TestGetOrgProjectsApi:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def test_should_raise_for_not_existing_org(self, cassandra_model):
        response = self.api_client.get("/org/not-existing/projects")
        assert response.status_code == 404

    def test_get_all_org_projects(self, cassandra_model):
        org = Org.create(name=self.fake.company())
        response = self.api_client.get(f"/org/{org.name}/projects")
        assert response.is_success
        assert response.json() == []
        prj_a = {
            "org": org.name,
            "name": "a",
            "full_name": "Project A",
            "description": "descr",
        }
        prj_b = {
            "org": org.name,
            "name": "b",
            "full_name": "Project B",
            "url": "http://project.b.org",
        }
        Project.create(**prj_a)
        Project.create(**prj_b)
        response = self.api_client.get(f"/org/{org.name}/projects")
        assert response.is_success, response.text
        assert len(response.json()) == 2
        a = [x for x in response.json() if x["name"] == "a"][0]
        b = [x for x in response.json() if x["name"] == "b"][0]
        assert not_none(a) == not_none(prj_a)
        assert not_none(b) == not_none(prj_b)

    def test_create_org(self, cassandra_model):
        # given some set of existing orgs
        orgs_before = [o.name for o in self._get_orgs()]
        # when a new org is created with PUT
        org_name = self.fake.company()
        assert org_name not in orgs_before
        response = self._put_org(org_name)
        assert response.is_success, response.text
        assert response.status_code == 201
        # then it is listed in GET
        orgs_after = [o.name for o in self._get_orgs()]
        assert len(orgs_after) == len(orgs_before) + 1
        assert org_name in orgs_after

    def test_create_org_should_fail_if_org_exists(self, cassandra_model):
        org_name = self.fake.domain_word()
        response = self._put_org(org_name)
        assert response.is_success, response.text
        assert response.status_code == 201
        response = self._put_org(org_name)
        assert not response.is_success, response.text
        assert response.status_code == 403

    def _put_org(self, org_name: str):
        org = {
            "name": org_name,
            "full_name": self.fake.word(),
            "url": "http://my.org"
        }
        return self.api_client.put(f"/org/", content=json.dumps(org))

    def _get_orgs(self) -> list[OrgInfo]:
        response = self.api_client.get(f"/org/")
        assert response.is_success, response.text
        res = []
        for item in response.json():
            res.append(OrgInfo(**item))
        return res
