import logging

from codetiming import Timer
from fastapi import APIRouter, HTTPException
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
    TestCaseRun,
)
from terec.model.util import model_to_dict

router = APIRouter()
logger = logging.getLogger(__name__)


class TestCaseSuiteRunInfo(BaseModel):
    test_run: TestCaseRunInfo
    suite_run: TestSuiteRunInfo


def validate_path(org_name: str, project_name: str, suite_name: str):
    get_org_or_raise(org_name)
    get_org_project_or_raise(org_name, project_name)
    get_test_suite_or_raise(org_name, project_name, suite_name)


def get_suite_branch_runs(
    org_name: str,
    project_name: str,
    suite_name: str,
    branch: str | None = None,
    limit: int = 32,
) -> list[TestSuiteRun]:
    # collect runs results
    query_params = {
        "org": org_name,
        "project": project_name,
        "suite": suite_name,
    }
    if branch:
        query_params["branch"] = branch
    runs = TestSuiteRun.objects(**query_params).limit(limit)
    logger.info(
        "Found {} interesting build runs for suite {}/{} on branch {}",
        len(runs),
        project_name,
        suite_name,
        branch,
    )
    return runs


def combine_test_runs_with_suite_runs(
    test_runs: list[TestCaseRun], suite_runs: list[TestSuiteRun]
):
    runs_by_id = {r.run_id: r for r in suite_runs}
    res = []
    for test in test_runs:
        test_info = TestCaseRunInfo(**model_to_dict(test))
        run_info = TestSuiteRunInfo(**model_to_dict(runs_by_id[test.run_id]))
        res.append(TestCaseSuiteRunInfo(test_run=test_info, suite_run=run_info))
    return res


@Timer(name="api-history-get-failed-tests", logger=logging.info)
@router.get("/orgs/{org_name}/projects/{project_name}/suites/{suite_name}/failed-tests")
def get_suite_branch_run_failed_tests(
    org_name: str,
    project_name: str,
    suite_name: str,
    branch: str | None = None,
    limit: int = 32,
    threshold: int | None = None,
) -> list[TestCaseSuiteRunInfo]:
    """
    Return list of all failed tests for given suite and branch.
    Each item on the list is ia pair of (test case run info, suite run info).
    Items are ordered by tests that were run (package.class.test.config).
    Query parameters:
    1. limit - use N recent builds (ordered by run_id descending)
    2. threshold - return only tests that failed at least T times [TODO]
    """
    # collect relevant suite runs (on the branch)
    validate_path(org_name, project_name, suite_name)
    runs_history = get_suite_branch_runs(
        org_name, project_name, suite_name, branch, limit
    )
    # collect failures for given runs history
    failed_tests = get_failed_tests_for_suite_runs(runs_history)
    logger.info(
        "Found {} failed tests for suite {}/{} on branch {}",
        len(failed_tests),
        project_name,
        suite_name,
        branch,
    )
    # transform into run info
    return combine_test_runs_with_suite_runs(failed_tests, runs_history)


@Timer(name="api-history-get-test-runs", logger=logging.info)
@router.get("/orgs/{org_name}/projects/{project_name}/suites/{suite_name}/test-runs")
def get_suite_branch_test_runs_history(
    org_name: str,
    project_name: str,
    suite_name: str,
    test_package: str,
    test_class: str | None = None,
    test_case: str | None = None,
    branch: str | None = None,
    run_limit: int = 32,
) -> list[TestCaseSuiteRunInfo]:
    """
    Return history of tests - identified by {package, class, testname} in runs of given suite on given branch.
    Each item on the list is ia pair of (test case run info, suite run info).
    TODO: order info - maybe unordered?
    """
    # validate parameters
    if test_case and not test_class:
        raise HTTPException(
            status_code=400,
            detail="When test_case is set then test_class is also required.",
        )
    # collect relevant suite runs (on the branch)
    validate_path(org_name, project_name, suite_name)
    suite_runs = get_suite_branch_runs(
        org_name, project_name, suite_name, branch, run_limit
    )
    # collect test run history
    query_params = {
        "org": org_name,
        "project": project_name,
        "suite": suite_name,
        "run_id__in": [r.run_id for r in suite_runs],
        "test_package": test_package,
    }
    if test_class:
        query_params["test_suite"] = test_class
    if test_case:
        query_params["test_case"] = test_case
    # collect failures for given runs history
    test_runs = TestCaseRun.objects().filter(**query_params)
    logger.info(
        "Found {} test runs for suite {}/{} on branch {} matching query",
        len(test_runs),
        project_name,
        suite_name,
        branch,
    )
    # convert into return format (test run + suite run)
    return combine_test_runs_with_suite_runs(test_runs, suite_runs)
