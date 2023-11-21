import datetime
import logging

import more_itertools
from cassandra.cqlengine.query import BatchQuery, BatchType
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from terec.api.routers.util import (
    get_org_or_raise,
    get_org_project_or_raise,
    get_test_suite_or_raise,
    get_test_suite_run_or_raise,
)
from terec.model.results import (
    TestSuite,
    TestSuiteRun,
    TestCaseRunStatus,
    TestSuiteRunStatus,
    TestCaseRun,
)

router = APIRouter()
logger = logging.getLogger(__name__)

# TODO: shall we reflect modes or maybe instead keep only owned fields and then compose?


class TestSuiteInfo(BaseModel):
    __test__ = False
    org: str
    project: str
    suite: str
    url: str | None = None


class TestSuiteRunInfo(BaseModel):
    __test__ = False
    org: str
    project: str
    suite: str
    run_id: int
    tstamp: datetime.datetime
    url: str | None = None
    branch: str | None = None
    commit: str | None = None
    pass_count: int | None = None
    fail_count: int | None = None
    skip_count: int | None = None
    total_count: int | None = None
    duration_sec: int | None = None
    status: TestSuiteRunStatus
    ignore: bool = False
    ignore_details: str | None = None


class TestCaseRunInfo(BaseModel):
    __test__ = False
    test_package: str
    test_suite: str
    test_case: str
    test_config: str
    result: TestCaseRunStatus
    test_group: str | None = None
    tstamp: datetime.datetime | None = None
    duration_ms: int | None = None
    stdout: str | None = None
    stderr: str | None = None
    error_stacktrace: str | None = None
    error_details: str | None = None
    skip_details: str | None = None


@router.get("/org/{org_name}/suite")
def get_org_suites(org_name: str) -> list[TestSuiteInfo]:
    get_org_or_raise(org_name)
    return TestSuite.objects(org=org_name)


@router.get("/org/{org_name}/project/{project_name}/suite")
def get_project_suites(org_name: str, project_name: str) -> list[TestSuiteInfo]:
    get_org_or_raise(org_name)
    return TestSuite.objects(org=org_name, project=project_name)


@router.get("/org/{org_name}/project/{project_name}/suite/{suite_name}")
def get_project_suite(
    org_name: str, project_name: str, suite_name: str
) -> TestSuiteInfo:
    get_org_or_raise(org_name)
    ret = TestSuite.objects(org=org_name, project=project_name, suite=suite_name)
    assert len(ret) <= 1
    return ret[0] if ret else None


@router.post("/org/{org_name}/suite")
def create_suite(org_name: str, body: TestSuiteInfo) -> TestSuiteInfo:
    org = get_org_or_raise(org_name)
    body.org = body.org or org.name
    assert body.org == org_name, "org name in body does not match the one in path"
    params = body.model_dump(exclude_none=True)
    return TestSuite.create(**params)


@router.post("/org/{org_name}/run")
def create_suite_run(org_name: str, body: TestSuiteRunInfo) -> None:
    # validate org
    org = get_org_or_raise(org_name)
    body.org = body.org or org.name
    assert body.org == org_name, "org name in body does not match the one in path"
    # validate project
    get_org_project_or_raise(org_name, body.project)
    # create or update suite
    suite_columns = {"org", "project", "suite"}
    suite_params = body.model_dump(include=suite_columns, exclude_none=True)
    TestSuite.create(**suite_params)
    # create run
    run_params = body.model_dump(exclude_none=True)
    if "status" in run_params:
        run_params["status"] = run_params["status"].value
    TestSuiteRun.create(**run_params)


# TODO: maybe add something like "N test results added or updated"?
@router.post("/org/{org_name}/project/{prj_name}/suite/{suite_name}/run/{run_id}/tests")
def add_suite_run_tests(
    org_name: str,
    prj_name: str,
    suite_name: str,
    run_id: int,
    body: list[TestCaseRunInfo],
) -> dict:
    # empty list is not accepted
    if not body:
        raise HTTPException(
            status_code=400, detail="Empty list of test results to be imported."
        )
    # validate org/project/suite exists
    get_org_or_raise(org_name)
    get_org_project_or_raise(org_name, prj_name)
    get_test_suite_or_raise(org_name, prj_name, suite_name)
    # FIXME: we have a problem with branch/run order - we do not want to require branch
    get_test_suite_run_or_raise(org_name, prj_name, suite_name, run_id)
    # add test cases
    now = datetime.datetime.now()
    for chunk in more_itertools.sliced(body, 200):
        with BatchQuery(batch_type=BatchType.Unlogged) as batch:
            for test in chunk:
                attrs = test.model_dump()
                attrs["result"] = attrs["result"].value
                attrs["org"] = org_name
                attrs["project"] = prj_name
                attrs["suite"] = suite_name
                attrs["run_id"] = run_id
                TestCaseRun.batch(batch).create(**attrs, create_at=now)
    # log information about import
    test_results_count = len(body)
    logger.info(
        f"{test_results_count} test case results added to run {org_name}/{prj_name}/{suite_name}/{run_id}"
    )
    return {
        "test_count": test_results_count,
    }
