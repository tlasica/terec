from fastapi import HTTPException

from terec.model.projects import Org, Project
from terec.model.results import TestSuite, TestSuiteRun


def is_valid_terec_name(name: str) -> bool:
    if not name:
        return False
    if not name[0].isalnum() or not name[-1].isalnum():
        return False
    for c in name[1:-1]:
        if not c.isalnum() and not c in [".", "_", "-"]:
            return False
    return True


def get_org_or_raise(org_name: str) -> Org:
    assert org_name
    org = Org.objects(name=org_name)
    if not org:
        raise HTTPException(status_code=404, detail=f"Org not found: {org_name}.")
    return org


def raise_if_org_exists(org_name: str):
    assert org_name
    org = Org.objects(name=org_name)
    if org:
        raise HTTPException(status_code=403, detail=f"Org {org_name} already exists.")


def get_org_project_or_raise(org_name: str, prj_name: str) -> Project:
    assert org_name
    assert prj_name
    prj = Project.objects(org=org_name, name=prj_name)
    if not prj:
        raise HTTPException(
            status_code=404, detail=f"Project not found: {org_name}/{prj_name}."
        )
    return prj


def get_test_suite_or_raise(org_name: str, prj_name: str, suite_name: str) -> TestSuite:
    assert org_name
    assert prj_name
    assert suite_name
    suite = TestSuite.objects(org=org_name, project=prj_name, suite=suite_name)
    if not suite:
        raise HTTPException(
            status_code=404,
            detail=f"Suite not found {org_name}/{prj_name}/{suite_name}.",
        )
    return suite


def get_test_suite_run_or_raise(
    org_name: str, prj_name: str, suite_name: str, branch: str, run_id: int
) -> TestSuiteRun:
    assert org_name
    assert prj_name
    assert suite_name
    assert branch
    assert run_id > 0
    suites = TestSuiteRun.objects(
        org=org_name, project=prj_name, suite=suite_name, branch=branch, run_id=run_id
    ).all()
    params_str = f"{org_name}/{prj_name}/{suite_name}/{branch}/{run_id}"
    if not suites:
        raise_not_found(f"Suite run not found {params_str}.")
    if len(suites) > 1:
        raise_server_error(
            f"Too many suite runs found for {params_str}. Exactly one is expected"
        )

    return suites[0]


def raise_not_found(detail: str):
    raise HTTPException(status_code=404, detail=detail)


def raise_bad_request(detail: str):
    raise HTTPException(status_code=400, detail=detail)


def raise_server_error(detail: str):
    raise HTTPException(status_code=500, detail=detail)
