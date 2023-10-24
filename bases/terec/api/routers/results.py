import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from terec.api.routers.util import get_org_or_raise
from terec.model.results import TestSuite, TestSuiteRun

router = APIRouter()

# TODO: shall we reflect modes or maybe instead keep only owned fields and then compose?


class TestSuiteInfo(BaseModel):
    __test__ = False
    org_name: str
    prj_name: str
    suite_name: str
    url: str | None = None


class TestSuiteRunInfo(BaseModel):
    __test__ = False
    org_name: str
    prj_name: str
    suite_name: str
    run_id: int
    tstamp: datetime.datetime
    url: str | None = None
    branch: str | None = None
    commit: str | None = None
    passed_tests: int | None = None
    failed_tests: int | None = None
    skipped_tests: int | None = None
    duration_sec: int | None = None


@router.get("/org/{org_name}/suites")
def get_org_suites(org_name: str) -> list[TestSuiteInfo]:
    get_org_or_raise(org_name)
    return TestSuite.objects(org_name=org_name)


@router.get("/org/{org_name}/projects/{prj_name}/suites")
def get_project_suites(org_name: str, prj_name: str) -> list[TestSuiteInfo]:
    get_org_or_raise(org_name)
    return TestSuite.objects(org_name=org_name, prj_name=prj_name)


@router.get("/org/{org_name}/projects/{prj_name}/suites/{suite_name}")
def get_project_suites(org_name: str, prj_name: str, suite_name: str) -> TestSuiteInfo:
    get_org_or_raise(org_name)
    ret = TestSuite.objects(org_name=org_name, prj_name=prj_name, suite_name=suite_name)
    assert len(ret) <= 1
    return ret[0] if ret else None


@router.post("/org/{org_name}/suites")
def create_suite(org_name: str, body: TestSuiteInfo) -> TestSuiteInfo:
    org = get_org_or_raise(org_name)
    body.org_name = body.org_name or org.name
    assert body.org_name == org_name, "org name in body does not match the one in path"
    params = body.model_dump(exclude_none=True)
    return TestSuite.create(**params)


@router.post("org/{org_name}/runs")
def create_suite_run(org_name: str, body: TestSuiteRunInfo) -> None:
    # validate
    org = get_org_or_raise(org_name)
    body.org_name = body.org_name or org.name
    assert body.org_name == org_name, "org name in body does not match the one in path"
    # create or update suite
    suite_columns = {"org_name", "prj_name", "suite_name"}
    suite_params = body.model_dump(include=suite_columns, exclude_none=True)
    TestSuite.create(**suite_params)
    # create run
    run_params = body.model_dump(exclude_none=True)
    TestSuiteRun.create(**run_params)
