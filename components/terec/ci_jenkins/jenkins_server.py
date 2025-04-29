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

    def suite_test_runs_for_build(
        self, job_name: str, build_num: int
    ) -> List[TestCaseRunInfo]:
        """
        Efficiently collect test suite runs by:
        1. First getting all suite names using tree parameter
        2. Then getting detailed results for each suite
        """
        try:
            # Try the new implementation with tree parameter
            # First get all suite names
            suite_names = self._get_jenkins_api(
                job_name, build_num, tree="suites[name]{0}"
            )

            # Then get detailed results for each suite
            for suite_name in [s["name"] for s in suite_names["suites"]]:
                test_report = self._get_jenkins_api(
                    job_name,
                    build_num,
                    tree=f"suites[name={suite_name}][name,duration,timestamp,id,cases[className,name,skipped,skippedMessage,status,stderr,stdout,duration,errorDetails,errorStackTrace,properties],properties]{0}",
                )
                for suite in test_report["suites"]:
                    yield parse_jenkins_report_suite(suite)
        except Exception as e:
            logger.warning(
                f"Failed to use tree parameter: {e}. Falling back to full API call."
            )
            # Fallback to the old implementation if tree parameter fails
            j = self.connect()
            test_report = j.get_build_test_report(name=job_name, number=build_num)
            for suite in test_report["suites"]:
                yield parse_jenkins_report_suite(suite)
