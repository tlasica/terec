from terec.lib.terec_api_client import TerecApiClient


class TerecAdminClient:
    def __init__(self, terec_api_client: TerecApiClient):
        self.terec_api_client = terec_api_client

    def create_org(self, org: str, private: bool, url: str = None):
        path = "/admin/orgs"
        body = {"name": org, "private": private, "url": url}
        return self.terec_api_client.put(path, body)

    def create_project(self, org: str, name: str, url: str = None):
        path = f"/admin/orgs/{org}/projects"
        body = {"org": org, "name": name, "url": url}
        return self.terec_api_client.put(path, body)

    def create_suite(self, org: str, project: str, name: str, url: str = None):
        path = f"/tests/orgs/{org}/suites"
        body = {"org": org, "project": project, "suite": name, "url": url}
        return self.terec_api_client.post(path, body)
