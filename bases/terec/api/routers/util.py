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
    org_name: str, prj_name: str, suite_name: str, run_id: int
) -> TestSuiteRun:
    assert org_name
    assert prj_name
    assert suite_name
    assert run_id > 0
    suite = TestSuiteRun.objects(
        org=org_name, project=prj_name, suite=suite_name, run_id=run_id
    )
    if not suite:
        raise HTTPException(
            status_code=404,
            detail=f"Suite run not found {org_name}/{prj_name}/{suite_name}/{run_id}.",
        )
    return suite
