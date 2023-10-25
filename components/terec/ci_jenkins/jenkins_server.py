from jenkins import Jenkins

from terec.api.routers.results import TestSuiteRunInfo, TestCaseRunInfo


class JenkinsServer:

    def __init__(self, url: str, username: str = None, password: str = None):
        self.url = url
        self.username = username
        self.password = password
        self.server = None

    def connect(self) -> Jenkins:
        self.server = Jenkins(self.url, self.username, self.password)
        return self.server

    def server(self) -> Jenkins:
        return self.server

    def suite_run_for_build(self, job_name:str, build_num: int) -> TestSuiteRunInfo:
        return None

    def suite_test_runs_for_build(self, job_name:str, build_num: int) -> list[TestCaseRunInfo]:
        return []

