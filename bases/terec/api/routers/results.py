import datetime
import more_itertools

from codetiming import Timer
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel, field_validator

from terec.api.auth import req_read_perm, req_write_perm
from terec.api.routers.util import (
    get_org_or_raise,
    get_org_project_or_raise,
    get_test_suite_or_raise,
    get_test_suite_run_or_raise,
    raise_bad_request,
)
from terec.model.results import (
    TestSuite,
    TestSuiteRun,
    TestCaseRunStatus,
    TestSuiteRunStatus,
    TestCaseRun,
)
from terec.model.util import model_to_dict

router = APIRouter()


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
    branch: str
    run_id: int
    tstamp: datetime.datetime
    url: str | None = None
    commit: str | None = None
    pass_count: int | None = None
    fail_count: int | None = None
    skip_count: int | None = None
    total_count: int | None = None
    duration_sec: int | None = None
    status: TestSuiteRunStatus
    ignore: bool | None = False
    ignore_details: str | None = None

    @classmethod
    @field_validator("ignore", mode="plain")
    def set_ignore_to_false_on_none(cls, v: bool) -> bool:
        return False if v is None else v


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
    # TODO: possibly there should be run_id here as well

    def __str__(self):
        return f"{self.test_package}::{self.test_suite}::{self.test_case}::{self.test_config}"


@router.get("/orgs/{org_name}/suites")
def get_org_suites(
    org_name: str, authz: str = Depends(req_read_perm)
) -> list[TestSuiteInfo]:
    get_org_or_raise(org_name)
    return TestSuite.objects(org=org_name)


@router.get("/orgs/{org_name}/projects/{project_name}/suites")
def get_project_suites(
    org_name: str, project_name: str, authz: str = Depends(req_read_perm)
) -> list[TestSuiteInfo]:
    get_org_or_raise(org_name)
    return TestSuite.objects(org=org_name, project=project_name)


@router.get("/orgs/{org_name}/projects/{project_name}/suites/{suite_name}")
def get_project_suite(
    org_name: str,
    project_name: str,
    suite_name: str,
    authz: str = Depends(req_read_perm),
) -> TestSuiteInfo:
    get_org_or_raise(org_name)
    ret = TestSuite.objects(org=org_name, project=project_name, suite=suite_name)
    assert len(ret) <= 1
    return ret[0] if ret else None


@router.post("/orgs/{org_name}/suites")
def create_suite(
    org_name: str, body: TestSuiteInfo, authz: str = Depends(req_write_perm)
) -> TestSuiteInfo:
    org = get_org_or_raise(org_name)
    body.org = body.org or org.name
    assert body.org == org_name, "org name in body does not match the one in path"
    params = body.model_dump(exclude_none=True)
    return TestSuite.create(**params)


@router.post("/orgs/{org_name}/runs")
def create_suite_run(
    org_name: str, body: TestSuiteRunInfo, authz: str = Depends(req_write_perm)
) -> None:
    # validate org
    org = get_org_or_raise(org_name)
    body.org = body.org or org.name
    if body.org != org_name:
        raise_bad_request("org name in body does not match the one in path")
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
    if "branch" not in run_params:
        raise_bad_request("branch is mandatory")
    if "/" in run_params["branch"]:
        raise_bad_request(
            f"branch name {run_params['branch']} includes prohibited char: /"
        )
    TestSuiteRun.create(**run_params)


# TODO: maybe add something like "N test results added or updated" to the result?
@router.post(
    "/orgs/{org_name}/projects/{prj_name}/suites/{suite_name}/branches/{branch}/runs/{run_id}/tests"
)
def add_suite_run_test_results(
    org_name: str,
    prj_name: str,
    suite_name: str,
    branch: str,
    run_id: int,
    body: list[TestCaseRunInfo],
    authz: str = Depends(req_write_perm),
) -> dict:
    from cassandra.concurrent import execute_concurrent_with_args
    from cassandra.cqlengine.connection import get_session

    # empty list is not accepted
    if not body:
        raise HTTPException(
            status_code=400, detail="Empty list of test results to be imported."
        )
    # validate org/project/suite exists
    get_org_or_raise(org_name)
    get_org_project_or_raise(org_name, prj_name)
    get_test_suite_or_raise(org_name, prj_name, suite_name)
    suite_run = get_test_suite_run_or_raise(
        org_name, prj_name, suite_name, branch, run_id
    )
    # add test cases
    logger.info(
        "importing {} test case results for {}/{}/{}/{}/{}",
        len(body),
        org_name,
        prj_name,
        suite_name,
        branch,
        run_id,
    )
    now = datetime.datetime.now()

    cols = [
        "org",
        "project",
        "suite",
        "branch",
        "run_id",
        "test_package",
        "test_suite",
        "test_case",
        "test_config",
        "result",
        "test_group",
        "tstamp",
        "duration_ms",
        "stdout",
        "stderr",
        "error_stacktrace",
        "error_details",
        "skip_details",
    ]
    num_cols = len(cols)
    insert_cql = (
        f"INSERT INTO {TestCaseRun.column_family_name(include_keyspace=True)} "
        f"({', '.join(cols)})"
        f"VALUES({','.join('?' * num_cols)})"
        f"USING TIMESTAMP ?"
    )
    session = get_session()
    p_stmt = session.prepare(insert_cql)

    def limit_text_field(text: str) -> str:
        if text is None:
            return None
        return text[:16384] if len(text) > 16384 else text

    concurrency = 16
    for chunk in more_itertools.sliced(body, 2 * concurrency):
        params = []
        for test in chunk:
            timestamp = test.tstamp or suite_run.timestamp
            test_data = (
                org_name,
                prj_name,
                suite_name,
                branch,
                run_id,
                test.test_package,
                test.test_suite,
                test.test_case,
                test.test_config,
                test.result.value,
                test.test_group,
                timestamp,
                test.duration_ms,
                limit_text_field(test.stdout),
                limit_text_field(test.stderr),
                limit_text_field(test.error_stacktrace),
                limit_text_field(test.error_details),
                limit_text_field(test.skip_details),
            )
            assert len(test_data) == num_cols
            params.append(test_data)
        with Timer(
            logger=logger.info,
            initial_text=f"Inserting chunk of {len(params)} test case runs",
            text="Elapsed time for inserting chunk: {milliseconds:.0f} ms",
        ):
            execute_concurrent_with_args(
                session, p_stmt, params, concurrency=concurrency
            )

    # log information about import
    test_results_count = len(body)
    return {
        "test_count": test_results_count,
    }


@router.get(
    "/orgs/{org_name}/projects/{prj_name}/suites/{suite_name}/branches/{branch}/runs/{run_id}/tests"
)
def get_suite_run_tests(
    org_name: str,
    prj_name: str,
    suite_name: str,
    branch: str,
    run_id: int,
    result: TestCaseRunStatus | None = None,
    authz: str = Depends(req_read_perm),
) -> list[TestCaseRunInfo]:
    # validate parameters
    get_org_or_raise(org_name)
    get_org_project_or_raise(org_name, prj_name)
    get_test_suite_or_raise(org_name, prj_name, suite_name)
    get_test_suite_run_or_raise(org_name, prj_name, suite_name, branch, run_id)
    # collect results
    query_params = {
        "org": org_name,
        "project": prj_name,
        "suite": suite_name,
        "branch": branch,
        "run_id": run_id,
    }
    if result:
        query_params["result"] = result.upper()
    db_data = TestCaseRun.objects(**query_params).all()
    # build response
    resp = [TestCaseRunInfo(**model_to_dict(x)) for x in db_data]
    return resp


@router.get(
    "/orgs/{org_name}/projects/{prj_name}/suites/{suite_name}/branches/{branch}/runs/{run_id}/"
)
def get_suite_run_info(
    org_name: str,
    prj_name: str,
    suite_name: str,
    branch: str,
    run_id: int,
    authz: str = Depends(req_read_perm),
) -> TestSuiteRunInfo:
    # validate parameters
    get_org_or_raise(org_name)
    get_org_project_or_raise(org_name, prj_name)
    get_test_suite_or_raise(org_name, prj_name, suite_name)
    suite_run = get_test_suite_run_or_raise(
        org_name, prj_name, suite_name, branch, run_id
    )
    # build response
    return TestSuiteRunInfo(**model_to_dict(suite_run))
