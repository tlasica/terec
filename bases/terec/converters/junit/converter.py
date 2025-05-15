import xml.etree.ElementTree as ET
from typing import List, Dict
from datetime import datetime
from terec.api.routers.results import (
    TestSuiteRunInfo,
    TestCaseRunInfo,
    TestSuiteRunStatus,
    TestCaseRunStatus,
)


class JunitXmlConverter:
    """
    Converts a JUnit XML file into a list of TestSuiteRunInfo and TestCaseRunInfo objects.
    Handles multiple test suites in one file.
    """

    def __init__(self, xml_content: str):
        self.tree = ET.ElementTree(ET.fromstring(xml_content))
        self.suite_runs: List[TestSuiteRunInfo] = []
        self.test_cases_by_suite: Dict[str, List[TestCaseRunInfo]] = {}
        self._parse()

    def _parse(self):
        root = self.tree.getroot()
        suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
        for suite in suites:
            suite_name = suite.attrib.get("name", "suite")
            suite_run = TestSuiteRunInfo(
                org="imported",
                project="imported",
                suite=suite_name,
                branch="imported",
                run_id=1,
                tstamp=datetime.now(),
                url=None,
                commit=None,
                pass_count=int(suite.attrib.get("tests", 0))
                - int(suite.attrib.get("failures", 0))
                - int(suite.attrib.get("errors", 0))
                - int(suite.attrib.get("skipped", 0)),
                fail_count=int(suite.attrib.get("failures", 0))
                + int(suite.attrib.get("errors", 0)),
                skip_count=int(suite.attrib.get("skipped", 0)),
                total_count=int(suite.attrib.get("tests", 0)),
                duration_sec=int(float(suite.attrib.get("time", 0))),
                status=(
                    TestSuiteRunStatus.FAILURE
                    if int(suite.attrib.get("failures", 0))
                    + int(suite.attrib.get("errors", 0))
                    > 0
                    else TestSuiteRunStatus.SUCCESS
                ),
                ignore=False,
                ignore_details=None,
            )
            self.suite_runs.append(suite_run)
            cases: List[TestCaseRunInfo] = []
            for tc in suite.findall("testcase"):
                status = TestCaseRunStatus.PASS
                error_text = None
                skip_text = None
                # Robustly check for failure or error among children
                fail_node = None
                for child in tc:
                    if child.tag in ("failure", "error"):
                        fail_node = child
                        break
                if fail_node is not None:
                    status = TestCaseRunStatus.FAIL
                    error_details = fail_node.attrib.get("message", None)
                    error_stacktrace = fail_node.text or None
                else:
                    error_details = None
                    error_stacktrace = None
                # Check for skipped
                skip_node = None
                for child in tc:
                    if child.tag == "skipped":
                        skip_node = child
                        break
                if skip_node is not None:
                    status = TestCaseRunStatus.SKIP
                    skip_text = (
                        skip_node.attrib.get("message")
                        or (skip_node.text or None)
                        or "Test skipped (no details)"
                    )
                # Parse <system-out> and <system-err>
                stdout = None
                stderr = None
                for child in tc:
                    if child.tag == "system-out":
                        stdout = child.text or ""
                    elif child.tag == "system-err":
                        stderr = child.text or ""
                # Parse times (JUnit time is in seconds as string)
                duration_ms = int(float(tc.attrib.get("time", 0)) * 1000)
                case = TestCaseRunInfo(
                    test_package=tc.attrib.get("classname", ""),
                    test_suite=suite_name,
                    test_case=tc.attrib.get("name", ""),
                    test_config="#",
                    result=status,
                    test_group=None,
                    tstamp=None,
                    duration_ms=duration_ms,
                    stdout=stdout,
                    stderr=stderr,
                    error_stacktrace=(
                        error_stacktrace if status == TestCaseRunStatus.FAIL else None
                    ),
                    error_details=(
                        error_details if status == TestCaseRunStatus.FAIL else None
                    ),
                    skip_details=(
                        skip_text if status == TestCaseRunStatus.SKIP else None
                    ),
                )
                cases.append(case)
            self.test_cases_by_suite[suite_name] = cases

    def get_suite_runs(self) -> List[TestSuiteRunInfo]:
        return self.suite_runs

    def get_test_cases_for_suite(self, suite_name: str) -> List[TestCaseRunInfo]:
        return self.test_cases_by_suite.get(suite_name, [])
