import json
import pytest

from faker import Faker
from terec.api.routers.projects import OrgInfo, is_valid_terec_name
from terec.model.projects import Org, Project, OrgToken


def not_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


@pytest.mark.usefixtures("api_client")
class TestGetOrgProjectsApi:
    fake = Faker()

    @pytest.fixture(autouse=True)
    def inject_client(self, api_client):
        self.api_client = api_client

    def test_should_raise_for_not_existing_org(self, cassandra_model):
        response = self.api_client.get("/admin/orgs/not-existing/projects")
        assert response.status_code == 404

    def test_get_all_org_projects(self, cassandra_model):
        org = Org.create(name=self.fake.domain_name())
        response = self.api_client.get(f"/admin/orgs/{org.name}/projects")
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
        response = self.api_client.get(f"/admin/orgs/{org.name}/projects")
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
        org_name = self.fake.domain_name()
        assert org_name not in orgs_before
        response = self._put_org(org_name)
        assert response.is_success, response.text
        assert response.status_code == 201
        assert len(response.json()["tokens"]) == 0
        # then it is listed in GET
        orgs_after = [o.name for o in self._get_orgs()]
        assert len(orgs_after) == len(orgs_before) + 1
        assert org_name in orgs_after
        org_tokens = OrgToken.objects(org=org_name)
        assert len(org_tokens) == 0

    def test_create_private_org(self, cassandra_model):
        # given some set of existing orgs
        orgs_before = [o.name for o in self._get_orgs()]
        # when a new org is created with PUT
        org_name = self.fake.domain_name()
        assert org_name not in orgs_before
        response = self._put_org(org_name, private=True)
        assert response.is_success, response.text
        assert response.status_code == 201
        assert len(response.json()["tokens"]) == 3
        # then it is listed in GET
        orgs_after = [o.name for o in self._get_orgs()]
        assert len(orgs_after) == len(orgs_before) + 1
        assert org_name in orgs_after
        # and it has tokens created
        org_tokens = OrgToken.objects(org=org_name)
        assert len(org_tokens) == 3

    def test_create_org_should_fail_if_org_exists(self, cassandra_model):
        org_name = self.fake.domain_word()
        response = self._put_org(org_name)
        assert response.is_success, response.text
        assert response.status_code == 201
        response = self._put_org(org_name)
        assert not response.is_success, response.text
        assert response.status_code == 403

    def test_create_project_in_public_org(self, cassandra_model):
        org_name = self.fake.domain_name()
        response = self._put_org(org_name, private=False)
        assert response.is_success, response.text
        response = self._put_project(org_name, "p")
        assert response.is_success, response.text

    def test_create_project_in_private_org(self, cassandra_model):
        # given private org
        org_name = self.fake.domain_name()
        response = self._put_org(org_name, private=True)
        assert response.is_success, response.text
        admin_token = response.json()["tokens"]["admin"]
        write_token = response.json()["tokens"]["write"]
        # when project request is sent without x-auth-token
        response = self._put_project(org_name, "p")
        assert response.status_code == 401
        # when project request is sent with invalid api key
        response = self._put_project(org_name, "p", headers={"X-API-KEY": "fake"})
        assert response.status_code == 401
        # when project request is sent with valid api key and admin permissions
        response = self._put_project(org_name, "p", headers={"X-API-KEY": admin_token})
        assert response.is_success, response.text
        # when project request is sent with valid api key without admin permissions
        response = self._put_project(org_name, "p", headers={"X-API-KEY": write_token})
        assert response.status_code == 401

    def test_get_projects_in_private_org(self, cassandra_model):
        # given private org
        org_name = self.fake.domain_name()
        response = self._put_org(org_name, private=True)
        assert response.is_success, response.text
        read_token = response.json()["tokens"]["read"]
        # when no token is provided it fails
        response = self._get_projects(org_name)
        assert response.status_code == 401
        # when read-only token is provided it works
        response = self._get_projects(org_name, headers={"X-API-KEY": read_token})
        assert response.is_success

    def _put_org(self, org_name: str, private: bool = False):
        org = {
            "name": org_name,
            "full_name": self.fake.word(),
            "url": "http://my.org",
            "private": private,
        }
        return self.api_client.put(f"/admin/orgs/", content=json.dumps(org))

    def _get_orgs(self) -> list[OrgInfo]:
        response = self.api_client.get(f"/admin/orgs/")
        assert response.is_success, response.text
        res = []
        for item in response.json():
            res.append(OrgInfo(**item))
        return res

    def _put_project(self, org_name: str, prj_name: str, headers: dict = None):
        data = {
            "org": org_name,
            "name": prj_name,
        }
        return self.api_client.put(
            f"/admin/orgs/{org_name}/projects",
            content=json.dumps(data),
            headers=headers,
        )

    def _get_projects(self, org_name: str, headers: dict = None):
        return self.api_client.get(f"/admin/orgs/{org_name}/projects", headers=headers)


def test_valid_org_and_project_names():
    assert is_valid_terec_name("cassandra")
    assert is_valid_terec_name("cassandra-3.11")
    assert is_valid_terec_name("Cassandra-3.11")
    assert is_valid_terec_name("Ala-ma-kota")
    assert is_valid_terec_name("Ala13-ma-kota_3_889_x")
    assert is_valid_terec_name("A")
    assert is_valid_terec_name("9livesdata")
    assert not is_valid_terec_name("Ala ma kota")
    assert not is_valid_terec_name("_Ala")
    assert not is_valid_terec_name("-Ala")
    assert not is_valid_terec_name(".Ala")
    assert not is_valid_terec_name("Ala_")
    assert not is_valid_terec_name("Ala-")
    assert not is_valid_terec_name("Ala.")
    assert not is_valid_terec_name("")
    assert not is_valid_terec_name("Ala!ma")
