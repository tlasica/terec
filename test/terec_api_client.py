import json

from httpx import Response
from starlette.testclient import TestClient


class TerecApiClient:
    def __init__(self, test_client: TestClient):
        self.client = test_client

    def put_org(
        self, name: str, full_name: str = "My Org", url: str = "http://my.org"
    ) -> Response:
        org = {"name": name, "full_name": full_name, "url": url}
        return self.client.put(f"/admin/orgs/", content=json.dumps(org))

    def put_project(
        self,
        org_name: str,
        name: str,
        full_name: str = "My Project",
        url: str = "http://my.org/project",
    ) -> Response:
        p = {"org": org_name, "name": name, "full_name": full_name, "url": url}
        return self.client.put(
            f"/admin/orgs/{org_name}/projects", content=json.dumps(p)
        )

    def post_suite(self, org_name: str, prj_name: str, name: str):
        s = {
            "org": org_name,
            "project": prj_name,
            "suite": name,
        }
        return self.client.post(f"/admin/orgs/{org_name}/suites", content=json.dumps(s))

    def post_suite_run(self, org_name, suite_run_info) -> Response:
        url = f"/tests/orgs/{org_name}/runs"
        return self.client.post(url, content=suite_run_info.model_dump_json())

    def post_test_results(
        self, org: str, prj: str, suite: str, branch: str, run: int, body: str
    ) -> Response:
        url = f"/tests/orgs/{org}/projects/{prj}/suites/{suite}/branches/{branch}/runs/{run}/tests"
        return self.client.post(url, content=body)

    def expect_get_error_404(self, url: str) -> None:
        response = self.client.get(url)
        assert response.status_code == 404
