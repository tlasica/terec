from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from terec.model.projects import Project, Org
from terec.model.util import model_to_dict

router = APIRouter()

# TODO: can we validate if url is indeed an url?


# TODO: probably we should move it from router to model package
class ProjectInfo(BaseModel):
    org_name: str
    prj_name: str
    full_name: str | None = None
    description: str | None = None
    url: str | None = None


class TestSuiteInfo(BaseModel):
    org_name: str
    prj_name: str
    # TODO: finish


def get_org_or_raise(org_name) -> Org:
    org = Org.objects(name=org_name)
    if not org:
        raise HTTPException(
            status_code=404, detail=f"Org {org_name} not found in the database."
        )
    return org


@router.get("/org/{org_name}/projects")
def get_all_org_projects(org_name: str) -> list[ProjectInfo]:
    """
    Gets all projects defined for given organisation or empty list.
    If the organization does not exist it throws exception [TODO]
    """
    get_org_or_raise(org_name)
    projects = Project.objects(org_name=org_name)
    res = [ProjectInfo(**model_to_dict(p)) for p in projects]
    return res


@router.post("/org/{org_name}/projects")
def create_project(org_name: str, project_info: ProjectInfo) -> ProjectInfo:
    get_org_or_raise(org_name)
    if project_info.org_name and project_info.org_name != org_name:
        raise HTTPException(
            status_code=500,
            detail=f"Org name in request body ({project_info.org_name}) should match path ({org_name})",
        )
    params = project_info.model_dump(exclude_none=True)
    return Project.create(**params)


@router.post("/org/{org_name}/suites")
def create_suite(org_name: str) -> TestSuiteInfo:
    org = get_org_or_raise(org_name)
    return TestSuiteInfo()
    # TODO implement
