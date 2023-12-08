import datetime
import uuid

from functools import lru_cache

from codetiming import Timer
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic.main import BaseModel

from terec.api.routers.results import TestSuiteRunInfo, TestCaseRunInfo
from terec.api.routers.util import (
    get_org_or_raise,
    get_org_project_or_raise,
    get_test_suite_or_raise,
)
from terec.model.failures import (
    load_failed_tests_for_suite_runs,
    load_suite_branch_runs,
    load_test_case_runs,
)
from terec.model.results import (
    TestSuiteRun,
    TestCaseRun,
)
from terec.model.util import model_to_dict
from terec.regression.failure_analysis import TestCaseRunFailureAnalyser

router = APIRouter()


def request_error(msg):
    raise HTTPException(status_code=500, detail=msg)


class TestCaseSuiteRunInfo(BaseModel):
    """
    Full pair of test case run and test suite info (can be a little heavy).
    """

    test_run: TestCaseRunInfo
    suite_run: TestSuiteRunInfo


class TestCaseRunResultShortInfo(BaseModel):
    """
    Short information about test case run result: only run id, timestamp and result.
    It is assumed that this information is always in the context of some org/project/suite/branch already
    """

    run_id: int
    branch: str
    tstamp: datetime.datetime
    result: str


def validate_path(org_name: str, project_name: str, suite_name: str):
    get_org_or_raise(org_name)
    get_org_project_or_raise(org_name, project_name)
    get_test_suite_or_raise(org_name, project_name, suite_name)


@lru_cache(maxsize=1024)
def get_suite_branch_runs(
    org_name: str,
    project_name: str,
    suite_name: str,
    branch: str | None = None,
    limit: int = 32,
    user_req_id: str = str(
        uuid.uuid1()
    ),  # for memoizing if part of the same user request
) -> list[TestSuiteRun]:
    runs = load_suite_branch_runs(org_name, project_name, suite_name, branch, limit)
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


@Timer(name="api-history-get-failed-tests", logger=logger.info)
@router.get("/orgs/{org_name}/projects/{project_name}/suites/{suite_name}/failed-tests")
def get_suite_branch_run_failed_tests(
    org_name: str,
    project_name: str,
    suite_name: str,
    branch: str | None = None,
    limit: int = 32,
    threshold: int | None = None,
    user_req_id: str | None = None,
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
        org_name,
        project_name,
        suite_name,
        branch,
        limit,
        user_req_id=user_req_id or str(uuid.uuid1()),
    )
    # collect failures for given runs history
    failed_tests = load_failed_tests_for_suite_runs(runs_history)
    logger.info(
        "Found {} failed tests for suite {}/{} on branch {}",
        len(failed_tests),
        project_name,
        suite_name,
        branch,
    )
    # transform into run info
    return combine_test_runs_with_suite_runs(failed_tests, runs_history)


@Timer(name="api-history-get-test-runs", logger=logger.info)
@router.get("/orgs/{org_name}/projects/{project_name}/suites/{suite_name}/test-runs")
def get_suite_branch_test_runs_history(
    org_name: str,
    project_name: str,
    suite_name: str,
    test_package: str,
    test_class: str | None = None,
    test_case: str | None = None,
    test_config: str | None = None,
    branch: str | None = None,
    run_limit: int = 32,
    user_req_id: str | None = None,
) -> list[TestCaseSuiteRunInfo]:
    """
    Return history of tests - identified by {package, class, testname} in runs of given suite on given branch.
    Each item on the list is ia pair of (test case run info, suite run info).
    TODO: order info - maybe unordered?
    """
    # validate parameters
    if test_case and not test_class:
        request_error("When test_case is set then test_class is also required.")
    # collect relevant suite runs (on the branch)
    validate_path(org_name, project_name, suite_name)
    suite_runs = get_suite_branch_runs(
        org_name,
        project_name,
        suite_name,
        branch,
        run_limit,
        user_req_id=user_req_id or str(uuid.uuid1()),
    )
    # collect test run history
    suite_runs_ids = [x.run_id for x in suite_runs]
    test_runs = load_test_case_runs(
        org_name=org_name,
        project_name=project_name,
        suite_name=suite_name,
        runs=suite_runs_ids,
        test_package=test_package,
        test_class=test_class,
        test_case=test_case,
        test_config=test_config,
    )
    logger.info(
        "Found {} test {} runs for suite {}/{} on branch {} matching query",
        len(test_runs),
        f"{test_package}::{test_class}::{test_case}::{test_config}",
        project_name,
        suite_name,
        branch,
    )
    # convert into return format (test run + suite run)
    return combine_test_runs_with_suite_runs(test_runs, suite_runs)


class TestCaseRunCheckResponse(BaseModel):
    """
    Response for the test case check to find if this is a known failure or a new one.
    In addition to the result we got context (history of results for all builds),
    some summary like number of failures, similar and different failures etc.
    """

    # TODO: add search context like builds checked
    # TODO: add history per config
    class Summary(BaseModel):
        num_runs: int  # total number of runs that we found and are checking
        num_same_fail: int  # number of similar failures found
        num_diff_fail: int  # number of other failures found
        num_pass: int  # number of runs that passed
        num_skip: int  # number of runs that test was skipped

    test_case: TestCaseRunInfo
    summary: Summary
    similar_failures: list[TestCaseSuiteRunInfo]
    message: str | None
    is_known_failure: bool | None  # T (known failure), F (new failure), None (cannot say)

    @classmethod
    def from_analyser_result(cls, ar: TestCaseRunFailureAnalyser):
        params = {
            "test_case": TestCaseRunInfo(**model_to_dict(ar.failed_test)),
            "summary": cls.build_summary(ar),
            "similar_failures": combine_test_runs_with_suite_runs(
                ar.similar_failures, ar.suite_runs_to_check
            ),
            "message": ar.message(),
            "is_known_failure": ar.is_known_failure(),
        }
        return TestCaseRunCheckResponse(**params)

    @classmethod
    def build_summary(cls, ar: TestCaseRunFailureAnalyser):
        data = {
            "num_runs": ar.num_test_runs_checked(),
            "num_pass": ar.num_test_runs_pass(),
            "num_skip": ar.num_test_runs_pass(),
            "num_same_fail": ar.num_test_runs_fail_same_way(),
            "num_diff_fail": ar.num_test_runs_fail_different_way(),
        }
        return cls.Summary(**data)


@Timer(name="api-history-get-test-run-check", logger=logger.info)
@router.get(
    "/orgs/{org_name}/projects/{project_name}/suites/{suite_name}/test-run-check"
)
def get_test_run_check(
    org_name: str,
    project_name: str,
    suite_name: str,
    test_package: str,
    test_class: str,
    test_case: str,
    test_config: str,
    run_id: int,
    check_suite: str | None = None,
    check_branch: str | None = None,
    depth: int = 32,
    user_req_id: str | None = None,
) -> TestCaseRunCheckResponse:
    """
    Return information if given test run is similar to any known test failures on given branch.
    If it is then a list of matching similar failures is also returned.
    We can assume here that provided test run is FAIL.

    # TODO: at the moment it only works against same workflow, which... is not really good
    """
    validate_path(org_name, project_name, suite_name)
    if check_suite and not check_branch:
        request_error("check_branch q param is required with check_suite set.")
    if depth > 128 or depth < 1:
        request_error("maximum depth allowed is 128, minimum is 0")
    # collect requested test case run information
    test_runs = load_test_case_runs(
        org_name=org_name,
        project_name=project_name,
        suite_name=suite_name,
        runs=[run_id],
        test_package=test_package,
        test_class=test_class,
        test_case=test_case,
        test_config=test_config,
        limit=10,  # we expect 1! record but we can allow more to catch problems
    )
    logger.info(test_runs)
    if len(test_runs) != 1:
        request_error(f"Exactly one test case run was expected but got: {test_runs}")
    the_test = test_runs[0]
    # collect failure analysis results
    failure_analysis = TestCaseRunFailureAnalyser(the_test)
    if check_branch:
        check_suite = check_suite or the_test.suite
        failure_analysis.check_vs_upstream(check_suite, check_branch, depth=depth)
    else:
        failure_analysis.check_regression(depth=depth)
    # and prepare response
    response = TestCaseRunCheckResponse.from_analyser_result(failure_analysis)
    return response
