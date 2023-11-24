import logging

from fastapi import APIRouter
from pydantic.main import BaseModel

from terec.api.routers.results import TestSuiteRunInfo, TestCaseRunInfo
from terec.api.routers.util import (
    get_org_or_raise,
    get_org_project_or_raise,
    get_test_suite_or_raise,
)
from terec.model.failures import get_failed_tests_for_suite_runs
from terec.model.results import (
    TestSuiteRun,
)
from terec.model.util import model_to_dict

router = APIRouter()
logger = logging.getLogger(__name__)


class FailedTestCaseRunInfo(BaseModel):
    test_run: TestCaseRunInfo
    suite_run: TestSuiteRunInfo


@router.get("/orgs/{org_name}/projects/{project_name}/suites/{suite_name}/failed-tests")
def get_suite_branch_run_failed_tests(
    org_name: str,
    project_name: str,
    suite_name: str,
    branch: str | None = None,
    limit: int = 32,
) -> list[FailedTestCaseRunInfo]:
    """
    Return list of failed tests for given suite and branch.
    Each item on the list is ia pair of (test case run info, suite run info).
    Items are ordered by tests that were run (package.class.test.config).
    """
    # validate path
    get_org_or_raise(org_name)
    get_org_project_or_raise(org_name, project_name)
    get_test_suite_or_raise(org_name, project_name, suite_name)
    # collect runs results
    query_params = {
        "org": org_name,
        "project": project_name,
        "suite": suite_name,
    }
    if branch:
        query_params["branch"] = branch
    runs_history = TestSuiteRun.objects(**query_params).limit(limit)
    logger.info("Found {} interesting build runs for suite {}/{} on branch {}", len(runs_history), project_name, suite_name, branch)
    # collect failures for given runs history
    failed_tests = get_failed_tests_for_suite_runs(runs_history)
    logger.info("Found {} failed tests for suite {}/{} on branch {}", len(failed_tests), project_name, suite_name, branch)
    # transform into run info
    runs_by_id = {r.run_id: r for r in runs_history}
    res = []
    for test in failed_tests:
        test_info = TestCaseRunInfo(**model_to_dict(test))
        run_info = TestSuiteRunInfo(**model_to_dict(runs_by_id[test.run_id]))
        res.append(FailedTestCaseRunInfo(test_run=test_info, suite_run=run_info))
    return res
