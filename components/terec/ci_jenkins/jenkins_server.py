from jenkins import Jenkins
from loguru import logger
import requests
from typing import List, Optional

from terec.api.routers.results import TestSuiteRunInfo, TestCaseRunInfo
from terec.ci_jenkins.build_info_parser import parse_jenkins_build_info
from terec.ci_jenkins.report_parser import parse_jenkins_report_suite


class JenkinsServer:
    def __init__(self, url: str, username: str = None, password: str = None):
        self.url = url.rstrip("/")  # Remove trailing slash if present
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
        self, job_name: str, build_num: int, limit: int = 0
    ) -> List[TestCaseRunInfo]:
        """
        Efficiently collect test suite runs using optimized tree parameter and index-based collection
        """
        suite_count = self._get_suite_count(job_name, build_num)
        suite_count = suite_count if limit <= 0 else min(limit, suite_count)
        for suite_index in range(suite_count):
            yield self._get_suite_test_runs(job_name, build_num, suite_index)

    def _get_jenkins_api(
        self, job_name: str, build_num: int, tree: Optional[str] = None
    ) -> dict:
        """
        Helper method to make direct requests to Jenkins API
        """
        url = f"{self.url}/job/{job_name}/{build_num}/testReport/api/json"
        if tree:
            url += f"?tree={tree}"

        auth = (
            (self.username, self.password) if self.username and self.password else None
        )
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        return response.json()

    def _get_suite_count(self, job_name: str, build_num: int) -> int:
        """
        Get the total number of suites using optimized tree parameter
        """
        suite_info = self._get_jenkins_api(job_name, build_num, tree="suites[name]")
        logger.debug(f"Found {len(suite_info['suites'])} suites in build {build_num}")
        return len(suite_info["suites"])

    def _get_suite_test_runs(
        self, job_name: str, build_num: int, suite_index: int
    ) -> List[TestCaseRunInfo]:
        """
        Get test runs for a specific suite using optimized tree parameter
        """
        suite_fields = "name,duration,timestamp,id"
        case_fields = "className,name,skipped,skippedMessage,status,stderr,stdout,duration,errorDetails,errorStackTrace"
        suite = self._get_jenkins_api(
            job_name,
            build_num,
            tree=f"suites[{suite_fields},cases[{case_fields}]]{{{suite_index}}}",
        )["suites"][0]
        return parse_jenkins_report_suite(suite)
