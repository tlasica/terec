from faker import Faker
from fastapi.testclient import TestClient
from terec.api.core import create_app
from terec.model.projects import Org, Project


def not_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


class TestGetOrgProjectsApi:
    fake = Faker()
    api_app = create_app()
    api_client = TestClient(api_app)

    def test_should_raise_for_not_existing_org(self, cassandra_model) -> None:
        response = self.api_client.get("/org/not-existing/projects")
        assert response.status_code == 404

    def test_get_all_org_projects(self, cassandra_model) -> None:
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
        assert response.is_success
        assert len(response.json()) == 2
        a = [x for x in response.json() if x["name"] == "a"][0]
        b = [x for x in response.json() if x["name"] == "b"][0]
        assert not_none(a) == not_none(prj_a)
        assert not_none(b) == not_none(prj_b)
