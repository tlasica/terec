from jenkins import Jenkins
from loguru import logger
from requests import Session
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
        self.session = requests.Session()

    def connect(self) -> Jenkins:
        if not self.server:
            logger.info(f"Connecting to Jenkins CI server at {self.url}")
            self.server = Jenkins(self.url, self.username, self.password)
        return self.server

    def server(self) -> Jenkins:
        return self.server

    def auth(self):
        has_auth = self.username and self.password
        return (self.username, self.password) if has_auth else None

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
        with Session() as session:
            session.auth = self.auth()
            batch_size = max(1, suite_count // 20)
            batches = [
                (i, min(i + batch_size, suite_count))
                for i in range(0, suite_count, batch_size)
            ]
            for start_idx, end_idx in batches:
                index = f"{{{start_idx},{end_idx}}}"
                logger.debug("Getting suites {}..{}", start_idx, end_idx)
                for suite_results in self._get_suites_test_runs(
                    session, job_name, build_num, index
                ):
                    yield suite_results

    def _get_jenkins_api(
        self,
        session: Session,
        job_name: str,
        build_num: int,
        tree: Optional[str] = None,
    ) -> dict:
        """
        Helper method to make direct requests to Jenkins API
        """
        url = f"{self.url}/job/{job_name}/{build_num}/testReport/api/json"
        if tree:
            url += f"?tree={tree}"
        response = session.get(url)
        response.raise_for_status()
        return response.json()

    def _get_suite_count(self, job_name: str, build_num: int) -> int:
        """
        Get the total number of suites using optimized tree parameter
        """
        with Session() as session:
            session.auth = self.auth()
            suite_info = self._get_jenkins_api(
                session, job_name, build_num, tree="suites[name]"
            )
            logger.debug(
                f"Found {len(suite_info['suites'])} suites in build {build_num}"
            )
            return len(suite_info["suites"])

    def _get_suites_test_runs(
        self, session, job_name: str, build_num: int, suites: str
    ) -> List[List[TestCaseRunInfo]]:
        """
        Get test runs for a specific suite using optimized tree parameter
        """
        suite_fields = "name,duration,timestamp,id"
        case_fields = "className,name,skipped,skippedMessage,status,stderr,stdout,duration,errorDetails,errorStackTrace"
        tree_param = f"suites[{suite_fields},cases[{case_fields}]]{suites}"
        resp = self._get_jenkins_api(session, job_name, build_num, tree=tree_param)
        suites = resp["suites"]
        return [parse_jenkins_report_suite(s) for s in suites]
