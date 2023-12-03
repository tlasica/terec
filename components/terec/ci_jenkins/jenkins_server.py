from jenkins import Jenkins
from loguru import logger

from terec.api.routers.results import TestSuiteRunInfo, TestCaseRunInfo
from terec.ci_jenkins.build_info_parser import parse_jenkins_build_info
from terec.ci_jenkins.report_parser import parse_jenkins_report_suite


class JenkinsServer:
    def __init__(self, url: str, username: str = None, password: str = None):
        self.url = url
        self.username = username
        self.password = password
        self.server = None

    def connect(self) -> Jenkins:
        if not self.server:
            logger.info(f"Connecting to Jenkins CI server at {self.url}")
            self.server = Jenkins(self.url, self.username, self.password)
        return self.server

    def server(self) -> Jenkins:
        return self.server

    def suite_run_for_build(self, job_name: str, build_num: int) -> TestSuiteRunInfo:
        j = self.connect()
        build_info = j.get_build_info(name=job_name, number=build_num)
        return parse_jenkins_build_info("org", "project", "suite", build_info)

    def suite_test_runs_for_build(
        self, job_name: str, build_num: int
    ) -> list[TestCaseRunInfo]:
        j = self.connect()
        test_report = j.get_build_test_report(name=job_name, number=build_num)
        for suite in test_report["suites"]:
            yield parse_jenkins_report_suite(suite)
