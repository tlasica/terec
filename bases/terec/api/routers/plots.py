from fastapi import APIRouter
from loguru import logger

from terec.api.routers.results import TestSuiteRunInfo
from terec.api.routers.util import (
    get_org_or_raise,
    get_org_project_or_raise,
    get_test_suite_or_raise,
)
from terec.model.results import (
    TestSuiteRun,
)
from terec.model.util import model_to_dict

router = APIRouter()


@router.get("/orgs/{org_name}/projects/{project_name}/suites/{suite_name}/builds")
def get_suite_branch_run_history(
    org_name: str,
    project_name: str,
    suite_name: str,
    branch: str | None = None,
    limit: int = 32,
) -> list[TestSuiteRunInfo]:
    """
    Return builds (runs) history for given suite on given branch starting from the most recent ones.
    The collection is ordered by run_id descending and limit will cut the result to some N runs only.
    """
    # validate path
    get_org_or_raise(org_name)
    get_org_project_or_raise(org_name, project_name)
    get_test_suite_or_raise(org_name, project_name, suite_name)
    # collect results
    query_params = {
        "org": org_name,
        "project": project_name,
        "suite": suite_name,
    }
    if branch:
        query_params["branch"] = branch
    history = TestSuiteRun.objects(**query_params).limit(limit)
    # transform into run info
    res = [model_to_dict(r) for r in history]
    return res
